"""Trade-list statistics. All $ figures are net of fees unless named gross."""

import numpy as np
import pandas as pd


def daily_pnl(trades: pd.DataFrame, days: list[pd.Timestamp]) -> pd.Series:
    """Net P&L per trading day, zero on days without trades."""
    s = trades.groupby(pd.to_datetime(trades["trading_day"]))["net"].sum() if len(trades) else pd.Series(dtype=float)
    return s.reindex(pd.DatetimeIndex(days), fill_value=0.0)


def realized_equity(trades: pd.DataFrame) -> pd.Series:
    """Cumulative net P&L in exit order. Overlapping trades can exit out of signal order; trades that exit on the
    same bar are booked together."""
    if "exit_bar" not in trades:
        return trades["net"].cumsum()
    return trades.groupby("exit_bar", sort=True)["net"].sum().cumsum()


def summary(trades: pd.DataFrame, days: list[pd.Timestamp]) -> dict:
    n = len(trades)
    if n == 0:
        return {"trades": 0, "net": 0.0}
    net = trades["net"]
    wins, losses = net[net > 0], net[net <= 0]
    eq = realized_equity(trades)
    day = daily_pnl(trades, days)
    sd = day.std()
    by_year = trades.groupby(pd.to_datetime(trades["trading_day"]).dt.year)["net"].sum()
    return {
        "trades": n,
        "net": round(float(net.sum()), 2),
        "gross": round(float(trades["gross"].sum()), 2),
        "fees": round(float(trades["fee"].sum()), 2),
        "win_rate": round(len(wins) / n, 4),
        "profit_factor": round(float(wins.sum() / -losses.sum()), 3) if losses.sum() < 0 else float("inf"),
        "avg_trade": round(float(net.mean()), 2),
        "avg_win": round(float(wins.mean()), 2) if len(wins) else 0.0,
        "avg_loss": round(float(losses.mean()), 2) if len(losses) else 0.0,
        "max_drawdown": round(float((eq - eq.cummax().clip(lower=0)).min()), 2),
        "worst_day": round(float(day.min()), 2),
        "best_day": round(float(day.max()), 2),
        "sharpe_daily_ann": round(float(day.mean() / sd * np.sqrt(252)), 3) if sd > 0 else float("nan"),
        "years_positive": f"{int((by_year > 0).sum())}/{len(by_year)}",
        "exit_reasons": trades["reason"].value_counts().to_dict(),
    }
