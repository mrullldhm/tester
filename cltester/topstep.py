"""Topstep Trading Combine pass/fail simulator over a backtest's trades. Rules: docs/TOPSTEP.md.

Per trade the engine gives net P&L and MAE (worst open P&L incl. fees). Within a day:
  - DLL (when enabled): day's realized + trade MAE <= -DLL -> trade closed at the DLL, no more trades that day.
  - MLL: balance + day's realized + trade MAE <= MLL at any moment -> account fails.
  When both are reached in one trade, the higher level is hit first.
End of day: balance += day P&L; MLL = min(max(MLL, highest EOD balance - max_loss), mll_lock).
Pass at end of day: profit >= max(target, best_day / consistency).
"""

from collections import defaultdict
from dataclasses import dataclass

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


def _by_day(trades: pd.DataFrame, rules: Combine) -> dict:
    if len(trades) and trades["qty"].max() > rules.max_contracts:
        raise ValueError(f"trade size above {rules.max_contracts} contracts")
    out = defaultdict(list)
    for d, net, mae in zip(trades["trading_day"], trades["net"], trades["mae"], strict=True):
        out[pd.Timestamp(d)].append((float(net), float(mae)))
    return out


def run_attempt(per_day: dict, days: list[pd.Timestamp], k0: int, rules: Combine = COMBINE_50K) -> Attempt:
    bal = hi = rules.start_balance
    dll = rules.daily_loss
    mll = bal - rules.max_loss
    best, active = -np.inf, 0
    for k in range(k0, len(days)):
        trades = per_day.get(days[k], ())
        day = 0.0
        active += bool(trades)
        for net, mae in trades:
            # equity falls to bal + day + mae; whichever limit sits higher is hit first
            if dll is not None and day + mae <= -dll and bal - dll > mll:
                day = -dll
                break
            if bal + day + mae <= mll:
                return Attempt(days[k0], days[k], "fail", k - k0 + 1, active, bal + day + mae - rules.start_balance,
                               max(best, 0.0))
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
    return pd.DataFrame([run_attempt(per_day, days, k, rules).__dict__ for k in range(len(days))])


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
    return pd.DataFrame(out)


def summary(roll: pd.DataFrame, seq: pd.DataFrame, days: list[pd.Timestamp], rules: Combine = COMBINE_50K) -> dict:
    done = roll[roll["outcome"] != "open"]
    passed = done[done["outcome"] == "pass"]
    s_pass = int((seq["outcome"] == "pass").sum()) if len(seq) else 0
    s_fail = int((seq["outcome"] == "fail").sum()) if len(seq) else 0
    months = (days[-1] - days[0]).days / 30.44 if days else 0.0  # subscription runs the whole period
    cost = rules.monthly_fee * months + rules.reset_fee * s_fail
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
