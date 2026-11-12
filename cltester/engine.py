"""Bar-by-bar backtest of limit-entry bracket orders on CL 1-minute bars. Rules: docs/ENGINE.md.

A strategy returns signals: one row per bar i where, after bar i closes, it places a limit entry order.
Columns: side (+1 long / -1 short), limit, stop (required), target (optional, NaN = none),
expire (bars the order stays working, default 30) or expire_min (minutes of clock time after the signal bar's
close; replaces expire, so missing minutes cannot stretch the order), hold (max bars in the trade, optional),
qty (default 1),
part_qty / part_target (optional partial exit: part_qty contracts leave at part_target, the rest runs on).

Optional trade management: `manage(ctx)` is called on every held bar m after the fill bar, before that bar's
exits are checked, with data up to bar m-1 only. It returns (stop, close_now): the stop for bar m (any price, in
the trade's own side space, see below) and whether to close the whole position at bar m's open.

Short trades run through the same code with prices negated, so every rule is written once, for longs.
`manage` sees those side-space prices too: for a short, ctx.E, ctx.S, ctx.best are negated ticks, and the stop it
returns must be negated ticks as well (helpers: ctx.side, ctx.to_side(price_ticks)).
"""

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .config import COMBINE_50K, FEE_ROUND_TURN, TICK, TICK_VALUE
from .data import Bars, session_minute, to_ticks


@dataclass(frozen=True)
class Fills:
    fee: float = FEE_ROUND_TURN  # $ per contract round turn
    flatten: int = session_minute(COMBINE_50K.flatten)  # session minute: no orders or positions from here


@dataclass
class Ctx:
    """What `manage` may look at on held bar m. Prices are integer ticks in side space (negated for shorts)."""

    i: int  # signal bar
    j: int  # fill bar
    m: int  # bar about to be checked (data up to m-1 may be used)
    side: int
    E: int  # entry
    S: int  # current stop
    T: int | None  # target
    qty: int  # contracts still open
    best: int  # highest side-space high from the fill bar through bar m-1 (the fill bar's high may predate the fill)
    state: dict = field(default_factory=dict)  # free per-trade memory for the strategy

    def to_side(self, ticks: int) -> int:
        return self.side * ticks


TRADE_COLUMNS = ["signal_bar", "entry_bar", "exit_bar", "entry_ts", "exit_ts", "trading_day", "side", "qty",
                 "entry", "exit", "reason", "ticks", "part_exit", "gross", "fee", "net", "mae", "mfe", "path"]
# ticks: exit - entry of the final leg per contract (side-adjusted). part_exit: price of the partial exit or NaN.
# path: (open P&L per held bar, worst P&L per held bar) in $ incl. fee; first entry = the fill bar.
# The Combine simulator walks it so a gap through a loss limit executes at the open, not at the limit.


def _prepare(signals: pd.DataFrame, n: int) -> pd.DataFrame:
    s = signals.copy()
    for col, default in (("target", np.nan), ("expire", 30), ("expire_min", np.nan), ("hold", np.nan), ("qty", 1),
                         ("part_qty", 0), ("part_target", np.nan)):
        if col not in s:
            s[col] = default
    missing = {"side", "limit", "stop"} - set(s.columns)
    if missing:
        raise ValueError(f"signals miss columns {sorted(missing)}")
    if not s.index.is_unique or s.index.min() < 0 or s.index.max() >= n:
        raise ValueError("signal index must be unique bar positions inside the bars")
    if not s["side"].isin([1, -1]).all():
        raise ValueError("side must be +1 or -1")
    if not np.isfinite(s[["limit", "stop"]].to_numpy(float)).all():
        raise ValueError("limit and stop must be finite prices")
    if (s["qty"] < 1).any() or (s["expire"] < 1).any() or (s["hold"] < 0).any() or (s["expire_min"] < 1).any():
        raise ValueError("qty, expire and expire_min must be >= 1, hold >= 0")
    pq, q = s["part_qty"].to_numpy(np.int64), s["qty"].to_numpy(np.int64)
    if (pq < 0).any() or ((pq > 0) & (pq >= q)).any():
        raise ValueError("part_qty must be 0 or below qty")
    if ((pq > 0) & ~np.isfinite(s["part_target"].to_numpy(float))).any():
        raise ValueError("part_qty needs a finite part_target")
    return s.sort_index()


def _ticks_or_zero(prices: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Prices as float and as integer ticks; NaN (no order) becomes 0 ticks."""
    v = prices.to_numpy(float)
    return v, np.where(np.isnan(v), 0, np.round(np.nan_to_num(v) / TICK)).astype(np.int64)


def _check_stop(stop, signal_bar: int) -> int:
    """manage() must return a finite whole number of ticks (side space: use ctx.to_side for shorts)."""
    if not np.isfinite(stop) or stop != int(stop):
        raise ValueError(f"signal at bar {signal_bar}: manage returned stop {stop}; need whole side-space ticks")
    return int(stop)


def backtest(bars: Bars, signals: pd.DataFrame, fills: Fills = Fills(),
             manage: Callable[[Ctx], tuple[int, bool]] | None = None) -> pd.DataFrame:
    n = len(bars)
    sig = _prepare(signals, n)
    flat = fills.flatten
    views = {1: (bars.o, bars.h, bars.l, bars.c), -1: (-bars.o, -bars.l, -bars.h, -bars.c)}
    lim, stp = to_ticks(sig["limit"]), to_ticks(sig["stop"])
    tgt, tgt_t = _ticks_or_zero(sig["target"])
    _, ptg_t = _ticks_or_zero(sig["part_target"])
    sides, qtys = sig["side"].to_numpy(np.int64), sig["qty"].to_numpy(np.int64)
    pqtys = sig["part_qty"].to_numpy(np.int64)
    expires, holds = sig["expire"].to_numpy(np.int64), sig["hold"].to_numpy(float)
    expire_min = sig["expire_min"].to_numpy(float)
    minute = bars.ts.as_unit("ns").asi8 // 60_000_000_000  # bar open, minutes since epoch
    rows = []
    next_free = -1
    for r, i in enumerate(sig.index.to_numpy()):
        if i < next_free or i + 1 >= n:
            continue
        side, qty, pq = int(sides[r]), int(qtys[r]), int(pqtys[r])
        o, h, l, c = views[side]
        L, S = side * lim[r], side * stp[r]
        T = None if np.isnan(tgt[r]) else side * tgt_t[r]
        P = side * ptg_t[r] if pq > 0 else None
        if S >= L or (T is not None and T <= L) or (P is not None and (P <= L or (T is not None and P > T))):
            raise ValueError(f"signal at bar {i}: stop must be on the losing side and targets on the winning side")
        hold = None if np.isnan(holds[r]) else int(holds[r])
        day, sym = bars.day_id[i], bars.sym_id[i]
        # --- working entry order: bars i+1 .. i+expire ---
        entry_bar, last_active = -1, i
        timed = not np.isnan(expire_min[r])
        deadline = minute[i] + 1 + int(expire_min[r]) if timed else 0  # first minute the order no longer works
        for j in range(i + 1, n if timed else min(n, i + 1 + int(expires[r]))):
            if bars.day_id[j] != day or bars.sym_id[j] != sym or bars.sess_minute[j] >= flat:
                break
            if timed and minute[j] >= deadline:
                break
            if l[j] <= L:  # a touch fills (owner rule)
                entry_bar, E = j, min(o[j], L)
                break
            last_active = j
        if entry_bar < 0:
            next_free = last_active
            if timed and last_active + 1 < n and minute[last_active + 1] >= deadline \
                    and minute[last_active] + 1 < deadline:
                next_free = last_active + 1  # a gap spans the deadline: the order still worked at last_active's close
            continue
        # --- position: per held bar, the open and worst price feed the Combine path check ---
        j = entry_bar
        X, reason = None, ""
        rem, realized, PX = qty, 0, None  # contracts open, side-space ticks*contracts booked by the partial
        p_open, p_worst = [0], [(l[j] - E) * qty]
        best = h[j]
        best_pnl = (h[j] - E) * qty  # best open P&L (ticks x contracts) for mfe
        ctx = Ctx(i=int(i), j=j, m=j, side=side, E=int(E), S=int(S), T=None if T is None else int(T),
                  qty=rem, best=int(best)) if manage is not None else None
        if l[j] <= S:  # stop on the fill bar: assume it came after the fill
            X, reason = min(E, S), "stop"
            p_worst[0] = (X - E) * qty  # the bar low before the fill is not part of the trade
        m = j
        while X is None:
            if m > j:
                close_now = False
                if manage is not None and ctx is not None:
                    ctx.m, ctx.S, ctx.qty, ctx.best = m, int(S), rem, int(best)
                    new_s, close_now = manage(ctx)
                    S = _check_stop(new_s, i)
                real0, rem0 = realized, rem  # booked P&L and contracts at the bar's open
                part_at_open = False
                if bars.sess_minute[m] >= flat:
                    X, reason = o[m], "flatten"
                elif close_now:
                    X, reason = o[m], "manage"
                elif o[m] <= S:
                    X, reason = o[m], "stop"
                elif T is not None and o[m] >= T:
                    X, reason = o[m], "target"
                else:
                    if P is not None and PX is None and o[m] >= P:  # partial at the open (gap in our favour)
                        PX, realized, rem = o[m], realized + (o[m] - E) * pq, rem - pq
                        part_at_open = True
                    if l[m] <= S:
                        X, reason = S, "stop"  # stop and any target in one bar: stop first
                    else:
                        if P is not None and PX is None and h[m] >= P:
                            PX, realized, rem = P, realized + (P - E) * pq, rem - pq
                            best_pnl = max(best_pnl, realized + (P - E) * rem)
                        if T is not None and h[m] >= T:
                            X, reason = T, "target"
                p_open.append(real0 + (o[m] - E) * rem0)
                if X is not None and X == o[m]:
                    p_worst.append(real0 + (X - E) * rem0)  # exit at the open: nothing after it counts
                    best = max(best, X)
                    best_pnl = max(best_pnl, real0 + (X - E) * rem0)
                    break
                if reason == "stop":
                    p_worst.append(realized + (S - E) * rem)
                elif part_at_open:  # the open comes first, so the low counts only for what is left
                    p_worst.append(realized + (l[m] - E) * rem)
                else:  # order inside the bar unknown: the low counts with the contracts held at the bar's open
                    p_worst.append(real0 + (l[m] - E) * rem0)
                if X is None or reason == "target":
                    best = max(best, h[m])
                    best_pnl = max(best_pnl, realized + (h[m] - E) * rem)
                if X is not None:
                    break
            if m == n - 1:
                X, reason = c[m], "data_end"
            elif hold is not None and m - j >= hold:
                X, reason = c[m], "time"
            elif bars.last_of_sym[m]:
                X, reason = c[m], "roll"
            elif bars.last_of_day[m]:
                X, reason = c[m], "day_end"
            else:
                m += 1
        exit_bar = m
        p_worst[-1] = min(p_worst[-1], realized + (X - E) * rem)
        best_pnl = max(best_pnl, realized + (X - E) * rem)
        fee = fills.fee * qty
        total = realized + (X - E) * rem  # side-space ticks x contracts
        path = (np.array(p_open, dtype=float) * TICK_VALUE - fee, np.array(p_worst, dtype=float) * TICK_VALUE - fee)
        rows.append((i, entry_bar, exit_bar, bars.ts[entry_bar], bars.ts[exit_bar], bars.trading_day[entry_bar], side,
                     qty, side * E * TICK, side * X * TICK, reason, int(X - E),
                     np.nan if PX is None else side * PX * TICK, total * TICK_VALUE, fee, total * TICK_VALUE - fee,
                     float(path[1].min()), best_pnl * TICK_VALUE - fee, path))
        next_free = exit_bar
    out = pd.DataFrame(rows, columns=TRADE_COLUMNS)
    for col in ("entry", "exit", "part_exit"):
        out[col] = out[col].astype(float).round(2)
    return out
