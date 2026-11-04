"""Parameter grid: evaluate once, record thirteen objectives, retain net-profit order for compatibility."""

import itertools
import time

import pandas as pd

from . import metrics
from .config import DEFAULT, SLIPPAGE_SCENARIOS, Properties
from .data import Bars
from .engine import Result, run
from .objectives import DEFAULT_RUIN_LOSS, trade_metrics


def combos(grid: dict) -> list[dict]:
    keys = list(grid)
    return [dict(zip(keys, v)) for v in itertools.product(*(grid[k] for k in keys))]


def grid_rows(factory, grid: dict, bars: Bars, props: Properties = DEFAULT, label: str = "",
              orders: list[int] | None = None, ruin_loss: float = DEFAULT_RUIN_LOSS) -> list[dict]:
    """Headline numbers of the combinations numbered `orders` (1-based grid order; default all)."""
    cs = combos(grid)
    todo = orders if orders is not None else list(range(1, len(cs) + 1))
    rows = []
    t0 = time.time()
    for done, n in enumerate(todo, 1):
        p = cs[n - 1]
        res = run(factory(**p), bars, props)
        s = metrics.summary(res)
        a = s["all"]
        rows.append({**p, "order": n, "net_profit": a["net_profit"], "total_closed_trades": a["total_closed_trades"],
                     "percent_profitable": a["percent_profitable"], "profit_factor": a["profit_factor"],
                     "max_equity_drawdown": s["max_equity_drawdown"], "avg_trade": a["avg_trade"],
                     "sharpe_ratio": s["sharpe_ratio"], "sortino_ratio": s["sortino_ratio"],
                     **trade_metrics(metrics.trade_frame(res), ruin_loss)})
        if done % 16 == 0 or done == len(todo):
            print(f"  {label} {done}/{len(todo)} combos, {time.time() - t0:.0f}s", flush=True)
    return rows


def rank(rows: list[dict]) -> pd.DataFrame:
    """Highest net profit first. Ties: profit factor, then grid order."""
    df = pd.DataFrame(rows)
    df["_pf"] = df["profit_factor"].fillna(-1.0)
    df = df.sort_values(["net_profit", "_pf", "order"], ascending=[False, False, True]).drop(columns="_pf")
    return df.reset_index(drop=True)


def run_grid(factory, grid: dict, bars: Bars, props: Properties = DEFAULT, label: str = "") -> pd.DataFrame:
    """One row per combination with the TV headline numbers, ranked (see `rank`)."""
    return rank(grid_rows(factory, grid, bars, props, label))


def stress(factory, params: dict, bars: Bars, props: Properties = DEFAULT) -> dict[int, Result]:
    """The same combination at 0 ticks and every slippage scenario."""
    return {k: run(factory(**params), bars, props.with_slippage(k)) for k in (0, *SLIPPAGE_SCENARIOS)}
