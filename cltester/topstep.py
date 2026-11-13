"""Topstep Trading Combine pass/fail simulator over a backtest's trades. Rules: docs/TOPSTEP.md.

Per trade the engine gives net P&L and its path: open and worst P&L of every held bar (fees included).
Within a day, walking each trade bar by bar (trades open at the same time are merged into one, P&L summed per bar):
  - a bar that opens at or through a limit executes at the open (a gap does not stop at the limit);
  - inside a bar, price moves continuously, so the higher of the two limits is hit first;
  - MLL hit (balance + day realized + open P&L <= MLL) -> account fails;
  - DLL hit (when enabled; day realized + open P&L <= -DLL) -> trade liquidated there, no more trades that day.
End of day: balance += day P&L; MLL = min(max(MLL, highest EOD balance - max_loss), mll_lock).
Pass at end of day: profit >= max(target, best_day / consistency).
"""

from collections import defaultdict
from dataclasses import dataclass, fields

import numpy as np
import pandas as pd

from .config import COMBINE_50K, Combine


@dataclass
class Attempt:
    start: pd.Timestamp
    end: pd.Timestamp | None
    outcome: str  # pass | fail | open (data ended first)
    days: int  # trading days from start to end, inclusive
    active_days: int  # days with at least one trade
    profit: float
    best_day: float


ATTEMPT_COLUMNS = [f.name for f in fields(Attempt)]


def _by_day(trades: pd.DataFrame, rules: Combine) -> dict:
    if trades.empty:
        return {}
    if trades["qty"].max() > rules.max_contracts:
        raise ValueError(f"trade size above {rules.max_contracts} contracts")
    out = defaultdict(list)
    spans = defaultdict(list)
    paths = trades["path"] if "path" in trades else [(np.array([0.0]), np.array([m])) for m in trades["mae"]]
    # Without bar spans (hand-made trade lists) trades are walked one after another, never merged.
    has_bars = {"entry_bar", "exit_bar", "path"} <= set(trades.columns)
    entries = trades["entry_bar"] if has_bars else [0] * len(trades)
    exits = trades["exit_bar"] if has_bars else [0] * len(trades)
    for d, net, path, e, x in zip(trades["trading_day"], trades["net"], paths, entries, exits, strict=True):
        out[pd.Timestamp(d)].append((float(net), path))
        spans[pd.Timestamp(d)].append((int(e), int(x)))
    if has_bars:
        if _peak_open_qty(trades) > rules.max_contracts:
            raise ValueError(f"more than {rules.max_contracts} contracts open at once")
        for d in out:
            out[d] = _merge_overlaps(out[d], spans[d])
    return out


def _peak_open_qty(trades: pd.DataFrame) -> int:
    """Most contracts held in any one bar (a trade holds from its entry bar through its exit bar; a partial exit
    releases its contracts after its bar)."""
    qty = trades["qty"].to_numpy()
    part_bar = trades["part_bar"].to_numpy() if "part_bar" in trades else np.full(len(trades), -1)
    part_qty = trades["part_qty"].to_numpy() if "part_qty" in trades else np.zeros(len(trades), dtype=int)
    has_part = part_bar >= 0
    bar = np.r_[trades["entry_bar"].to_numpy(), trades["exit_bar"].to_numpy() + 1, part_bar[has_part] + 1]
    change = np.r_[qty, -(qty - np.where(has_part, part_qty, 0)), -part_qty[has_part]]
    order = np.lexsort((change, bar))  # same bar: exits (negative) before entries
    return int(np.cumsum(change[order]).max())


def _merge_overlaps(day: list, spans: list[tuple[int, int]]) -> list:
    """Trades open at the same time become one combined trade, so the loss limits see their summed P&L per bar.
    A trade that closed earlier in the group counts with its net from the bar after its exit."""
    order = sorted(range(len(day)), key=lambda k: spans[k][0])
    groups: list[list[int]] = []
    group_end = -1
    for k in order:
        if groups and spans[k][0] <= group_end:
            groups[-1].append(k)
            group_end = max(group_end, spans[k][1])
        else:
            groups.append([k])
            group_end = spans[k][1]
    out = []
    for g in groups:
        if len(g) == 1:
            out.append(day[g[0]])
            continue
        start = min(spans[k][0] for k in g)
        size = max(spans[k][1] for k in g) - start + 1
        opened, worst = np.zeros(size), np.zeros(size)
        for k in g:
            net, (po, pw) = day[k]
            a, b = spans[k][0] - start, spans[k][1] - start
            if len(po) != b - a + 1:
                raise ValueError("trade path length does not match its entry and exit bars")
            opened[a:b + 1] += po
            worst[a:b + 1] += pw
            opened[b + 1:] += net
            worst[b + 1:] += net
        out.append((sum(day[k][0] for k in g), (opened, worst)))
    return out


def _walk(path: tuple, fail_at: float, dll_at: float | None) -> tuple[str, float]:
    """Walk one trade's bars. fail_at / dll_at: trade P&L at which MLL / DLL is hit.
    Returns ("fail", pnl) | ("dll", pnl at liquidation) | ("ok", 0.0)."""
    for opened, worst in zip(path[0], path[1], strict=True):
        if opened <= fail_at:
            return "fail", float(opened)
        if dll_at is not None and opened <= dll_at:
            return "dll", float(opened)
        if dll_at is not None and dll_at >= fail_at and worst <= dll_at:
            return "dll", dll_at
        if worst <= fail_at:
            return "fail", fail_at
    return "ok", 0.0


def run_attempt(per_day: dict, days: list[pd.Timestamp], k0: int, rules: Combine = COMBINE_50K) -> Attempt:
    bal = hi = rules.start_balance
    dll = rules.daily_loss
    mll = bal - rules.max_loss
    best, active = -np.inf, 0
    for k in range(k0, len(days)):
        trades = per_day.get(days[k], ())
        day = 0.0
        active += bool(trades)
        for net, path in trades:
            hit, pnl = _walk(path, mll - bal - day, None if dll is None else -dll - day)
            if hit == "fail":
                return Attempt(days[k0], days[k], "fail", k - k0 + 1, active, bal + day + pnl - rules.start_balance,
                               max(best, 0.0))
            if hit == "dll":
                day += pnl
                break
            day += net
        bal += day
        if trades:
            best = max(best, day)
        hi = max(hi, bal)
        mll = min(max(mll, hi - rules.max_loss), rules.mll_lock)
        profit = bal - rules.start_balance
        if profit >= max(rules.profit_target, best / rules.consistency):
            return Attempt(days[k0], days[k], "pass", k - k0 + 1, active, profit, best)
    return Attempt(days[k0], None, "open", len(days) - k0, active, bal - rules.start_balance, max(best, 0.0))


def trading_days(bars: pd.DataFrame) -> list[pd.Timestamp]:
    return [pd.Timestamp(d) for d in np.unique(bars["trading_day"].to_numpy())]


def rolling(trades: pd.DataFrame, days: list[pd.Timestamp], rules: Combine = COMBINE_50K) -> pd.DataFrame:
    """One attempt starting on every trading day. Attempts overlap, so they are not independent."""
    per_day = _by_day(trades, rules)
    return pd.DataFrame([run_attempt(per_day, days, k, rules).__dict__ for k in range(len(days))],
                        columns=ATTEMPT_COLUMNS)


def sequential(trades: pd.DataFrame, days: list[pd.Timestamp], rules: Combine = COMBINE_50K) -> pd.DataFrame:
    """Back-to-back attempts as a trader would live them: after a pass or fail, restart the next day."""
    per_day = _by_day(trades, rules)
    out, k = [], 0
    while k < len(days):
        a = run_attempt(per_day, days, k, rules)
        out.append(a.__dict__)
        if a.outcome == "open":
            break
        k += a.days
    return pd.DataFrame(out, columns=ATTEMPT_COLUMNS)


def subscription_cost(seq: pd.DataFrame, last_day: pd.Timestamp, rules: Combine = COMBINE_50K) -> float:
    """Billing as lived: a subscription starts with the first attempt and again after every pass. It is paid at
    the start and every 30 days until the pass (or the end of data). Each fail inside it costs one reset."""
    cost, sub_start = 0.0, None
    for start, end, outcome in zip(seq["start"], seq["end"], seq["outcome"], strict=True):
        if sub_start is None:
            sub_start = start
        if outcome == "fail":
            cost += rules.reset_fee
            continue
        stop = end if outcome == "pass" else last_day
        cost += rules.monthly_fee * ((stop - sub_start).days // 30 + 1)
        sub_start = None
    if sub_start is not None:  # the data ended right after a fail: that subscription ran to the last day
        cost += rules.monthly_fee * ((last_day - sub_start).days // 30 + 1)
    return cost


def summary(roll: pd.DataFrame, seq: pd.DataFrame, days: list[pd.Timestamp], rules: Combine = COMBINE_50K) -> dict:
    done = roll[roll["outcome"] != "open"]
    passed = done[done["outcome"] == "pass"]
    s_pass = int((seq["outcome"] == "pass").sum()) if len(seq) else 0
    s_fail = int((seq["outcome"] == "fail").sum()) if len(seq) else 0
    cost = subscription_cost(seq, days[-1], rules) if days else 0.0
    return {
        "rolling_attempts": len(done),
        "pass_rate": round(len(passed) / len(done), 4) if len(done) else float("nan"),
        "median_days_to_pass": float(passed["days"].median()) if len(passed) else float("nan"),
        "median_days_to_fail": float(done.loc[done["outcome"] == "fail", "days"].median())
        if (done["outcome"] == "fail").any() else float("nan"),
        "seq_passes": s_pass,
        "seq_fails": s_fail,
        "seq_cost_usd": round(cost, 2),
        "seq_cost_per_pass_usd": round(cost / s_pass, 2) if s_pass else float("nan"),
    }
