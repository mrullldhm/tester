"""Feature-1 metric definitions and deterministic selection; no changes to feature-2 objectives.

Ruin is an infinite-horizon Brownian approximation of fixed-size, independent net trade P&L,
not a forecast or a prop-firm failure probability. See docs/ENGINE.md for its limitations.
"""

import math
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Objective:
    key: str
    label: str
    direction: str
    unit: str
    definition: str


OBJECTIVES = (
    Objective(
        "net_profit",
        "Net profit",
        "max",
        "usd",
        "Sum of closed-trade profit after commission; excludes open P&L.",
    ),
    Objective(
        "percent_profitable",
        "Win rate",
        "max",
        "percent",
        "Winning closed trades divided by all closed trades, including breakevens.",
    ),
    Objective(
        "expectancy",
        "Expectancy",
        "max",
        "usd",
        "Mean net profit per closed trade, including losses and breakevens.",
    ),
    Objective(
        "profit_factor",
        "Profit factor",
        "max",
        "ratio",
        "Gross winning profit divided by gross losing profit, both after commission. Undefined without losses.",
    ),
    Objective(
        "payoff_ratio",
        "Payoff ratio",
        "max",
        "ratio",
        "Average net winning trade divided by the absolute average net losing trade. Requires wins and losses.",
    ),
    Objective(
        "risk_of_ruin",
        "Risk of ruin (estimate)",
        "min",
        "percent",
        "Infinite-horizon diffusion estimate of losing the declared amount from starting capital. Assumes independent, stationary, fixed-size net trade P&L; ignores intratrade losses and margin.",
    ),
    Objective(
        "max_equity_drawdown",
        "Maximum drawdown",
        "min",
        "usd",
        "Largest equity drawdown under the tester's intrabar TradingView convention, including an open trade at the end.",
    ),
    Objective(
        "max_consecutive_losses",
        "Consecutive losses",
        "min",
        "count",
        "Longest streak of losing closed trades in execution order. A win or breakeven resets the streak.",
    ),
    Objective(
        "sharpe_ratio",
        "Sharpe ratio",
        "max",
        "ratio",
        "Monthly marked-to-market excess return divided by population standard deviation, using 2% annual risk-free rate; not annualized.",
    ),
    Objective(
        "sortino_ratio",
        "Sortino ratio",
        "max",
        "ratio",
        "Monthly marked-to-market excess return divided by downside deviation about the risk-free rate; not annualized.",
    ),
    Objective(
        "r_multiple",
        "R-multiple",
        "max",
        "r",
        "Mean net trade profit / initial stop risk in dollars. Risk is actual fill to initial stop, before costs. Requires positive initial risk for every closed trade; R standard deviation and mean / standard deviation describe consistency.",
    ),
    Objective(
        "mae",
        "Maximum adverse excursion (MAE)",
        "min",
        "usd",
        "Mean of each closed trade's maximum adverse price excursion in dollars, before commission; only the exposed intrabar path counts.",
    ),
    Objective(
        "mfe",
        "Maximum favorable excursion (MFE)",
        "max",
        "usd",
        "Mean of each closed trade's maximum favorable price excursion in dollars, before commission; only the exposed intrabar path counts. Unrealized opportunity, not realized profit.",
    ),
)
BY_KEY = {o.key: o for o in OBJECTIVES}
METRIC_VERSION = 1
DEFAULT_MIN_TRADES = 30
DEFAULT_RUIN_LOSS = 25_000.0


def validate_options(min_trades: int, ruin_loss: float) -> None:
    if min_trades < 1:
        raise ValueError("min_trades must be at least 1")
    if not math.isfinite(ruin_loss) or ruin_loss <= 0:
        raise ValueError("ruin_loss must be a finite positive dollar amount")


def trade_metrics(tf: pd.DataFrame, ruin_loss: float = DEFAULT_RUIN_LOSS) -> dict:
    """Extra selection metrics from closed trades; zero activity is undefined, never an ideal score."""
    validate_options(1, ruin_loss)
    p = tf["profit"].to_numpy(dtype=float)
    n = len(p)
    wins, losses = p[p > 0], p[p < 0]
    streak = longest = 0
    for profit in p:
        streak = streak + 1 if profit < 0 else 0
        longest = max(longest, streak)
    mean = float(p.mean()) if n else None
    variance = float(p.var(ddof=0)) if n else None
    # Work in log space for selection: tiny probabilities must not tie after float underflow.
    log_ruin = None
    if n >= 2:
        if variance == 0:
            log_ruin = (
                0.0 if mean < 0 else -1e300
            )  # deterministic positive/zero increments never hit loss floor
        elif mean <= 0:
            log_ruin = 0.0
        else:
            log_ruin = max(-1e300, -2 * mean * ruin_loss / variance)
    r = tf["r_multiple"].to_numpy(dtype=float) if "r_multiple" in tf else np.array([])
    complete_r = n > 0 and len(r) == n and np.isfinite(r).all()
    r_mean = float(r.mean()) if complete_r else None
    r_sd = float(r.std(ddof=0)) if complete_r else None
    return {
        "expectancy": mean,
        "payoff_ratio": float(wins.mean() / -losses.mean())
        if len(wins) and len(losses)
        else None,
        "risk_of_ruin": 100 * math.exp(log_ruin) if log_ruin is not None else None,
        "risk_of_ruin_log": log_ruin,
        "max_consecutive_losses": longest if n else None,
        "r_multiple": r_mean,
        "r_stddev": r_sd,
        "r_consistency": r_mean / r_sd if r_sd is not None and r_sd > 0 else None,
        "r_valid_trades": int(np.isfinite(r).sum()),
        "mae": float(tf["drawdown"].mean()) if n else None,
        "mfe": float(tf["run_up"].mean()) if n else None,
    }


def rank_metric(
    grid: pd.DataFrame, key: str, min_trades: int = DEFAULT_MIN_TRADES
) -> pd.DataFrame:
    """Finite eligible scores first; ties: net profit, profit factor (undefined last), grid order."""
    if key not in BY_KEY:
        raise ValueError(f"unknown objective {key!r}")
    validate_options(min_trades, DEFAULT_RUIN_LOSS)
    if key not in grid:
        return grid.iloc[:0].copy()
    score_key = "risk_of_ruin_log" if key == "risk_of_ruin" else key
    if score_key not in grid:
        return grid.iloc[:0].copy()
    valid = np.isfinite(pd.to_numeric(grid[key], errors="coerce")) & np.isfinite(
        pd.to_numeric(grid[score_key], errors="coerce")
    )
    df = grid.loc[valid & (grid["total_closed_trades"] >= min_trades)].copy()
    cols = list(dict.fromkeys([score_key, "net_profit", "profit_factor", "order"]))
    ascending = [BY_KEY[key].direction == "min"] + [c == "order" for c in cols[1:]]
    return df.sort_values(
        cols, ascending=ascending, na_position="last", kind="stable"
    ).reset_index(drop=True)


def selection(
    grid: pd.DataFrame,
    param_keys,
    min_trades: int = DEFAULT_MIN_TRADES,
    ruin_loss: float = DEFAULT_RUIN_LOSS,
) -> dict:
    validate_options(min_trades, ruin_loss)

    def finite(value):
        return (
            float(value)
            if value is not None and pd.notna(value) and math.isfinite(float(value))
            else None
        )

    winners = {}
    for objective in OBJECTIVES:
        ranked = rank_metric(grid, objective.key, min_trades)
        if ranked.empty:
            winners[objective.key] = None
            continue
        row = ranked.iloc[0]
        scalar = lambda v: v.item() if hasattr(v, "item") else v
        values = {o.key: finite(row.get(o.key)) for o in OBJECTIVES}
        winners[objective.key] = {
            "order": int(row["order"]),
            "value": values[objective.key],
            "eligible": len(ranked),
            "params": {k: scalar(row[k]) for k in param_keys},
            "metrics": values,
            "total_closed_trades": int(row["total_closed_trades"]),
            "r_stddev": finite(row.get("r_stddev")),
            "r_consistency": finite(row.get("r_consistency")),
        }
    return {
        "metric_version": METRIC_VERSION,
        "min_trades": min_trades,
        "ruin_loss": ruin_loss,
        "grid_size": len(grid),
        "objectives": [asdict(o) for o in OBJECTIVES],
        "winners": winners,
    }
