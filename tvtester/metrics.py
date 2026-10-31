"""TradingView Strategy Tester numbers: Performance, Trades analysis, Risk/performance ratios, List of trades.

Definitions follow the TradingView help center ("Strategy Tester: Performance Summary"):
- Every trade's profit is net of commission. Net profit = gross profit - gross loss.
- Max drawdown (intrabar), per bar in a trade: max closed equity before the trade - equity on entry
  + contracts x adverse move to the bar's low (long) / high (short); the largest value wins. Run-up mirrors it
  with the min closed equity before the trade. Entry and exit bars count only the part of the path the trade
  was open (engine excursions). % = of initial capital (TV "as % of initial capital").
- Avg # bars in trades = exit bar index - entry bar index + 1.
- Sharpe / Sortino: monthly returns of month-end equity marked to market, risk-free 2%/12 a month, not annualized,
  population standard deviation. A zero denominator gives None, never infinity.
- Buy & hold: price change from the first trade's entry to the last close, as % of that entry, applied to
  the initial capital. The unadjusted front-month series has roll jumps inside it (labelled "TV-style").
"""

import math

import numpy as np
import pandas as pd

from .config import POINT_VALUE, TICK, TICK_VALUE
from .engine import Result, Trade


def _div(a: float, b: float) -> float | None:
    return None if b == 0 else a / b


def trade_frame(res: Result) -> pd.DataFrame:
    """One row per closed trade (TV "List of trades" plus extras)."""
    b, qty = res.bars, res.props.qty
    rows = []
    cum = 0.0
    for n, t in enumerate(res.trades, 1):
        cum += t.profit
        runup = max(0, t.direction * (t.best - t.entry_price)) * TICK_VALUE * t.qty
        dd = max(0, t.direction * (t.entry_price - t.worst)) * TICK_VALUE * t.qty
        value = abs(t.entry_price) * TICK * POINT_VALUE * t.qty
        rows.append({
            "trade": n,
            "type": "Long" if t.direction > 0 else "Short",
            "entry_signal": t.entry_id,
            "entry_time": b.ts[t.entry_bar],
            "entry_price": t.entry_price * TICK,
            "exit_signal": t.exit_id,
            "exit_time": b.ts[t.exit_bar],
            "exit_price": t.exit_price * TICK,
            "contracts": t.qty,
            "profit": t.profit,
            "profit_pct": _div(t.profit, value) and t.profit / value * 100,
            "cum_profit": cum,
            "cum_profit_pct": cum / res.props.initial_capital * 100,
            "run_up": runup,
            "run_up_pct": _div(runup, value) and runup / value * 100,
            "drawdown": dd,
            "drawdown_pct": _div(dd, value) and dd / value * 100,
            "bars": t.exit_bar - t.entry_bar + 1,
            "commission": t.commission,
            "exit_reason": t.exit_reason,
            "raw_symbol": b.raw_symbol[t.entry_bar],
            "signal_bar": t.signal_bar,
            "signal_time": b.ts[t.signal_bar] if t.signal_bar >= 0 else pd.NaT,
        })
    cols = ["trade", "type", "entry_signal", "entry_time", "entry_price", "exit_signal", "exit_time", "exit_price",
            "contracts", "profit", "profit_pct", "cum_profit", "cum_profit_pct", "run_up", "run_up_pct", "drawdown",
            "drawdown_pct", "bars", "commission", "exit_reason", "raw_symbol", "signal_bar", "signal_time"]
    return pd.DataFrame(rows, columns=cols)


def _open_pnl_at(t: Trade, price: int, entry_fee: float) -> float:
    return (price - t.entry_price) * t.direction * t.qty * TICK_VALUE - entry_fee


def _monthly_returns(res: Result) -> np.ndarray:
    """Month-end equity marked to market (closed profit + open P&L at the month's last close, entry commission
    included), every calendar month (UTC) of the test."""
    cap, b = res.props.initial_capital, res.bars
    naive = b.ts.tz_convert("UTC").tz_localize(None)
    months = pd.period_range(naive[0].to_period("M"), naive[-1].to_period("M"), freq="M")
    ends = pd.DatetimeIndex([m.end_time for m in months])
    last_idx = np.searchsorted(naive.as_unit("ns").asi8, ends.as_unit("ns").asi8, side="right") - 1
    exit_bars = np.array([t.exit_bar for t in res.trades], dtype=np.int64)
    profits = np.array([t.profit for t in res.trades], dtype=float)
    order = np.argsort(exit_bars, kind="stable")
    csum = np.concatenate([[0.0], np.cumsum(profits[order])])
    eq = cap + csum[np.searchsorted(exit_bars[order], last_idx, side="right")]
    spans = [(t, t.exit_bar) for t in res.trades] + ([(res.open_trade, len(b.c))] if res.open_trade else [])
    for t, end in spans:  # trades open at a month end: add their open P&L at that month's last close
        k = np.searchsorted(last_idx, t.entry_bar)
        if k == len(last_idx) or last_idx[k] >= end:
            continue
        for m in np.flatnonzero((last_idx >= t.entry_bar) & (last_idx < end)):
            eq[m] += _open_pnl_at(t, b.c[last_idx[m]], res.props.commission_per_order * t.qty)
    prev = np.concatenate([[cap], eq[:-1]])
    return eq / prev - 1


def daily_equity(res: Result) -> dict[str, np.ndarray]:
    """Equity marked to market at the last bar of every UTC date that has bars (feature 3, docs/VALIDATE.md).

    equity = initial capital + closed profit (exit bar <= day end) + open P&L of a position open at that bar's
    close, entry commission included (as `_monthly_returns` and TV's open P&L). closed = closed trades so far.
    The last value equals capital + net profit + open P&L of the run."""
    b = res.bars
    day = np.asarray(b.t_ms, dtype=np.int64) // 86_400_000
    ends = np.flatnonzero(np.r_[day[1:] != day[:-1], True])
    exit_bars = np.sort(np.array([t.exit_bar for t in res.trades], dtype=np.int64))
    profits = np.array([t.profit for t in sorted(res.trades, key=lambda t: t.exit_bar)], dtype=float)
    csum = np.concatenate([[0.0], np.cumsum(profits)])
    n_closed = np.searchsorted(exit_bars, ends, side="right")
    eq = res.props.initial_capital + csum[n_closed]
    spans = [(t, t.exit_bar) for t in res.trades] + ([(res.open_trade, len(b.c))] if res.open_trade else [])
    for t, end in spans:
        k0, k1 = np.searchsorted(ends, t.entry_bar), np.searchsorted(ends, end)  # day ends in [entry, exit)
        for m in range(k0, k1):
            eq[m] += _open_pnl_at(t, b.c[ends[m]], res.props.commission_per_order * t.qty)
    return {"day": day[ends], "end_bar": ends, "equity": eq, "closed": n_closed}


def _side_stats(tf: pd.DataFrame) -> dict:
    win, loss = tf[tf["profit"] > 0], tf[tf["profit"] < 0]
    gp, gl = win["profit"].sum(), -loss["profit"].sum()
    n = len(tf)
    avg_win = win["profit"].mean() if len(win) else None
    avg_loss = -loss["profit"].mean() if len(loss) else None
    return {
        "net_profit": gp - gl,
        "gross_profit": gp,
        "gross_loss": gl,
        "profit_factor": _div(gp, gl),
        "commission_paid": tf["commission"].sum(),
        "total_closed_trades": n,
        "winning_trades": len(win),
        "losing_trades": len(loss),
        "even_trades": n - len(win) - len(loss),
        "percent_profitable": _div(len(win), n) and len(win) / n * 100,
        "avg_trade": tf["profit"].mean() if n else None,
        "avg_trade_pct": tf["profit_pct"].mean() if n else None,
        "avg_winning_trade": avg_win,
        "avg_losing_trade": avg_loss,
        "ratio_avg_win_avg_loss": _div(avg_win or 0.0, avg_loss or 0.0) if avg_win and avg_loss else None,
        "largest_winning_trade": win["profit"].max() if len(win) else None,
        "largest_winning_trade_pct": win["profit_pct"].max() if len(win) else None,
        "largest_losing_trade": -loss["profit"].min() if len(loss) else None,
        "largest_losing_trade_pct": -loss["profit_pct"].min() if len(loss) else None,
        "avg_bars_in_trades": tf["bars"].mean() if n else None,
        "avg_bars_in_winning_trades": win["bars"].mean() if len(win) else None,
        "avg_bars_in_losing_trades": loss["bars"].mean() if len(loss) else None,
        "long_trades": int((tf["type"] == "Long").sum()),
        "short_trades": int((tf["type"] == "Short").sum()),
    }


def _equity_extremes(tf: pd.DataFrame, cap: float, open_trade: Trade | None) -> dict:
    max_dd = max_ru = 0.0
    closed = cap
    hi = lo = cap
    rows = list(zip(tf["profit"], tf["drawdown"], tf["run_up"]))
    if open_trade is not None:
        t = open_trade
        rows.append((0.0, max(0, t.direction * (t.entry_price - t.worst)) * TICK_VALUE * t.qty,
                     max(0, t.direction * (t.best - t.entry_price)) * TICK_VALUE * t.qty))
    for profit, dd, ru in rows:
        max_dd = max(max_dd, hi - closed + dd)
        max_ru = max(max_ru, closed - lo + ru)
        closed += profit
        hi, lo = max(hi, closed), min(lo, closed)
    return {"max_equity_drawdown": max_dd, "max_equity_drawdown_pct": max_dd / cap * 100,
            "max_equity_runup": max_ru, "max_equity_runup_pct": max_ru / cap * 100}


def open_pnl(res: Result) -> float:
    t: Trade | None = res.open_trade
    if t is None:
        return 0.0
    return _open_pnl_at(t, res.bars.c[res.last_bar], t.commission)


def summary(res: Result) -> dict:
    """TV Performance Summary. Keys "all", "long", "short" hold trade stats; top level holds account stats."""
    tf = trade_frame(res)
    cap, rf = res.props.initial_capital, res.props.risk_free_rate / 12
    r = _monthly_returns(res)
    sd = r.std(ddof=0) if len(r) else 0.0
    down = math.sqrt(np.mean(np.minimum(0.0, r - rf) ** 2)) if len(r) else 0.0
    out = {
        "initial_capital": cap,
        "period_start": str(res.bars.ts[0]),
        "period_end": str(res.bars.ts[-1]),
        **_equity_extremes(tf, cap, res.open_trade),
        "sharpe_ratio": _div(r.mean() - rf, sd) if sd > 0 else None,
        "sortino_ratio": _div(r.mean() - rf, down) if down > 0 else None,
        "open_pnl": open_pnl(res),
        "total_open_trades": int(res.open_trade is not None),
        "max_contracts_held": res.props.qty if res.trades or res.open_trade else 0,
        "margin_calls": 0,
        "commission_per_order": res.props.commission_per_order,
        "slippage_ticks": res.props.slippage_ticks,
    }
    first = res.trades[0] if res.trades else res.open_trade
    if first is not None:
        bh = (res.bars.c[res.last_bar] - first.entry_price) / abs(first.entry_price)
        out["buy_hold_return"], out["buy_hold_return_pct"] = bh * cap, bh * 100
    else:
        out["buy_hold_return"] = out["buy_hold_return_pct"] = None
    out["all"] = _side_stats(tf)
    out["long"] = _side_stats(tf[tf["type"] == "Long"])
    out["short"] = _side_stats(tf[tf["type"] == "Short"])
    out["net_profit_pct"] = out["all"]["net_profit"] / cap * 100
    out["exit_reasons"] = tf["exit_reason"].value_counts().to_dict()
    return out


PERIOD_GRAINS = ("year", "month", "week", "day")


def _period_key(exit_time: pd.Series, grain: str) -> pd.Series:
    """Bucket by UTC exit date. Weeks start on Monday and are named by that Monday (YYYY-MM-DD)."""
    t = pd.to_datetime(exit_time, utc=True)
    if grain == "year":
        return t.dt.year
    if grain == "month":
        return t.dt.strftime("%Y-%m")
    if grain == "week":
        return (t.dt.normalize() - pd.to_timedelta(t.dt.day_of_week, unit="D")).dt.strftime("%Y-%m-%d")
    if grain == "day":
        return t.dt.strftime("%Y-%m-%d")
    raise ValueError(f"unknown period grain {grain!r}; expected one of {PERIOD_GRAINS}")


def by_period(tf: pd.DataFrame, grain: str) -> pd.DataFrame:
    """Closed trades grouped by exit period: trades, net profit, % profitable, profit factor (NaN with no loss).

    Extra, not a TradingView tab. Periods without exits are absent."""
    cols = ["period", "trades", "net_profit", "percent_profitable", "profit_factor"]
    if tf.empty:
        _period_key(pd.Series([], dtype="datetime64[ns, UTC]"), grain)
        return pd.DataFrame(columns=cols)
    g = tf.groupby(_period_key(tf["exit_time"], grain))
    out = g.agg(trades=("profit", "size"), net_profit=("profit", "sum"),
                wins=("profit", lambda s: (s > 0).sum()),
                gp=("profit", lambda s: s[s > 0].sum()), gl=("profit", lambda s: -s[s < 0].sum()))
    out["percent_profitable"] = out["wins"] / out["trades"] * 100
    out["profit_factor"] = out["gp"] / out["gl"].replace(0, np.nan)
    return out.drop(columns=["wins", "gp", "gl"]).reset_index(names="period")


def by_year(tf: pd.DataFrame) -> pd.DataFrame:
    return by_period(tf, "year").rename(columns={"period": "year"})
