"""Bar-by-bar backtest of limit-entry bracket orders on CL 1-minute bars. Rules: docs/ENGINE.md.

A strategy returns signals: one row per bar i where, after bar i closes, it places a limit entry order.
Columns: side (+1 long / -1 short), limit, stop (required), target (optional, NaN = none),
expire (bars the order stays working, default 30), hold (max bars in the trade, optional), qty (default 1).

Short trades run through the same code with prices negated, so every rule is written once, for longs.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import COMBINE_50K, FEE_ROUND_TURN, TICK, TICK_VALUE
from .data import Bars, session_minute, to_ticks


@dataclass(frozen=True)
class Fills:
    fee: float = FEE_ROUND_TURN  # $ per contract round turn
    flatten: int = session_minute(COMBINE_50K.flatten)  # session minute: no orders or positions from here


TRADE_COLUMNS = ["signal_bar", "entry_bar", "exit_bar", "entry_ts", "exit_ts", "trading_day", "side", "qty",
                 "entry", "exit", "reason", "ticks", "gross", "fee", "net", "mae", "mfe"]


def _prepare(signals: pd.DataFrame, n: int) -> pd.DataFrame:
    s = signals.copy()
    for col, default in (("target", np.nan), ("expire", 30), ("hold", np.nan), ("qty", 1)):
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
    if (s["qty"] < 1).any() or (s["expire"] < 1).any() or (s["hold"] < 0).any():
        raise ValueError("qty and expire must be >= 1, hold >= 0")
    return s.sort_index()


def backtest(bars: Bars, signals: pd.DataFrame, fills: Fills = Fills()) -> pd.DataFrame:
    n = len(bars)
    sig = _prepare(signals, n)
    flat = fills.flatten
    views = {1: (bars.o, bars.h, bars.l, bars.c), -1: (-bars.o, -bars.l, -bars.h, -bars.c)}
    lim, stp = to_ticks(sig["limit"]), to_ticks(sig["stop"])
    tgt = sig["target"].to_numpy(float)
    tgt_t = np.where(np.isnan(tgt), 0, np.round(np.nan_to_num(tgt) / TICK)).astype(np.int64)
    sides, qtys = sig["side"].to_numpy(np.int64), sig["qty"].to_numpy(np.int64)
    expires, holds = sig["expire"].to_numpy(np.int64), sig["hold"].to_numpy(float)
    rows = []
    next_free = -1
    for r, i in enumerate(sig.index.to_numpy()):
        if i < next_free or i + 1 >= n:
            continue
        side, qty = int(sides[r]), int(qtys[r])
        o, h, l, c = views[side]
        L, S = side * lim[r], side * stp[r]
        T = None if np.isnan(tgt[r]) else side * tgt_t[r]
        if S >= L or (T is not None and T <= L):
            raise ValueError(f"signal at bar {i}: stop must be on the losing side and target on the winning side")
        hold = None if np.isnan(holds[r]) else int(holds[r])
        day, sym = bars.day_id[i], bars.sym_id[i]
        # --- working entry order: bars i+1 .. i+expire ---
        entry_bar, last_active = -1, i
        for j in range(i + 1, min(n, i + 1 + int(expires[r]))):
            if bars.day_id[j] != day or bars.sym_id[j] != sym or bars.sess_minute[j] >= flat:
                break
            if l[j] <= L:  # a touch fills (owner rule)
                entry_bar, E = j, min(o[j], L)
                break
            last_active = j
        if entry_bar < 0:
            next_free = last_active
            continue
        # --- position ---
        j, worst, best = entry_bar, l[entry_bar], h[entry_bar]
        X, reason, exit_bar = None, "", -1
        if l[j] <= S:  # stop on the fill bar: assume it came after the fill
            X, reason = min(E, S), "stop"
            worst = X  # the bar low before the fill is not part of the trade
        m = j
        while X is None:
            if m > j:
                if bars.sess_minute[m] >= flat:
                    X, reason = o[m], "flatten"
                elif o[m] <= S:
                    X, reason = o[m], "stop"
                elif l[m] <= S:
                    X, reason = S, "stop"
                elif T is not None and h[m] >= T:
                    X, reason = max(o[m], T), "target"  # a gap beyond the target fills at the open
                if reason == "target":
                    worst, best = min(worst, l[m]), max(best, h[m])  # the low may have come before the target
                if X is not None:
                    break
                worst, best = min(worst, l[m]), max(best, h[m])
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
        worst, best = min(worst, X), max(best, X)
        ticks = int(X - E)
        fee = fills.fee * qty
        rows.append((i, entry_bar, exit_bar, bars.ts[entry_bar], bars.ts[exit_bar], bars.trading_day[entry_bar], side,
                     qty, side * E * TICK, side * X * TICK, reason, ticks, ticks * TICK_VALUE * qty, fee,
                     ticks * TICK_VALUE * qty - fee, (worst - E) * TICK_VALUE * qty - fee,
                     (best - E) * TICK_VALUE * qty - fee))
        next_free = exit_bar
    out = pd.DataFrame(rows, columns=TRADE_COLUMNS)
    out["entry"] = out["entry"].round(2)
    out["exit"] = out["exit"].round(2)
    return out
