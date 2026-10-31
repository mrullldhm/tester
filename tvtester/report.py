"""TradingView-style result documents (Markdown) plus CSV / JSON / PNG files.

Sections mirror the Strategy Tester tabs: Overview, Performance, Trades analysis, Risk/performance ratios,
List of trades. Extras that TV does not show (by year, exit reasons, slippage scenarios) are labelled.
"""

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from . import metrics  # noqa: E402
from .config import ROOT  # noqa: E402
from .engine import Result  # noqa: E402


def usd(x) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{'-' if x < 0 else ''}{abs(x):,.2f} USD"


def pct(x) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.2f}%"


def num(x, d: int = 3) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.{d}f}"


def rel(path: Path, base: Path) -> str:
    return Path(*([".."] * len(base.relative_to(ROOT).parts)), path.relative_to(ROOT)).as_posix()


def overview(s: dict) -> str:
    a = s["all"]
    rows = [
        ("Net profit", f"{usd(a['net_profit'])} ({pct(s['net_profit_pct'])})"),
        ("Total closed trades", f"{a['total_closed_trades']:,}"),
        ("Percent profitable", pct(a["percent_profitable"])),
        ("Profit factor", num(a["profit_factor"])),
        ("Max equity drawdown", f"{usd(s['max_equity_drawdown'])} ({pct(s['max_equity_drawdown_pct'])})"),
        ("Avg trade", usd(a["avg_trade"])),
        ("Avg # bars in trades", num(a["avg_bars_in_trades"], 0)),
    ]
    return "| Metric | Value |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in rows)


def _three(s: dict, rows: list[tuple[str, str, callable]]) -> str:
    out = ["| Metric | All | Long | Short |", "|---|---|---|---|"]
    for label, key, fmt in rows:
        out.append(f"| {label} | " + " | ".join(fmt(s[side].get(key)) for side in ("all", "long", "short")) + " |")
    return "\n".join(out)


def performance(s: dict) -> str:
    cap = s["initial_capital"]

    def money_pct(v):
        return "—" if v is None else f"{usd(v)} ({pct(v / cap * 100)})"

    table = _three(s, [("Net profit", "net_profit", money_pct), ("Gross profit", "gross_profit", money_pct),
                       ("Gross loss", "gross_loss", money_pct), ("Commission paid", "commission_paid", usd)])
    acct = [
        ("Initial capital", usd(cap)),
        ("Buy & hold return (TV-style, all capital at the first entry)",
         f"{usd(s['buy_hold_return'])} ({pct(s['buy_hold_return_pct'])})"),
        ("Max equity run-up (intrabar)", f"{usd(s['max_equity_runup'])} ({pct(s['max_equity_runup_pct'])})"),
        ("Max equity drawdown (intrabar)",
         f"{usd(s['max_equity_drawdown'])} ({pct(s['max_equity_drawdown_pct'])})"),
        ("Open P&L", usd(s["open_pnl"])),
        ("Max contracts held", str(s["max_contracts_held"])),
    ]
    return table + "\n\n| Account | Value |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in acct)


def trades_analysis(s: dict) -> str:
    def i(v):
        return "—" if v is None else f"{v:,}"

    return _three(s, [
        ("Total closed trades", "total_closed_trades", i), ("Winning trades", "winning_trades", i),
        ("Losing trades", "losing_trades", i), ("Even trades", "even_trades", i),
        ("Percent profitable", "percent_profitable", pct), ("Avg P&L", "avg_trade", usd),
        ("Avg P&L %", "avg_trade_pct", pct), ("Avg winning trade", "avg_winning_trade", usd),
        ("Avg losing trade", "avg_losing_trade", usd), ("Ratio avg win / avg loss", "ratio_avg_win_avg_loss", num),
        ("Largest winning trade", "largest_winning_trade", usd),
        ("Largest winning trade %", "largest_winning_trade_pct", pct),
        ("Largest losing trade", "largest_losing_trade", usd),
        ("Largest losing trade %", "largest_losing_trade_pct", pct),
        ("Avg # bars in trades", "avg_bars_in_trades", lambda v: num(v, 0)),
        ("Avg # bars in winning trades", "avg_bars_in_winning_trades", lambda v: num(v, 0)),
        ("Avg # bars in losing trades", "avg_bars_in_losing_trades", lambda v: num(v, 0)),
    ])


def ratios(s: dict) -> str:
    rows = [("Sharpe ratio", num(s["sharpe_ratio"])), ("Sortino ratio", num(s["sortino_ratio"])),
            ("Profit factor", num(s["all"]["profit_factor"])), ("Margin calls", str(s["margin_calls"]))]
    return "| Metric | Value |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in rows)


def trade_list(tf: pd.DataFrame, last: int = 10) -> str:
    """TV List of trades layout (exit row above entry row), newest first, last N trades."""
    out = ["| Trade # | Type | Signal | Date/Time (UTC) | Price | Contracts | Profit | Cum. profit | Run-up | Drawdown |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in tf.tail(last).iloc[::-1].iterrows():
        side = r["type"]
        money = f"{usd(r['profit'])} ({pct(r['profit_pct'])})"
        out.append(f"| {r['trade']} | Exit {side.lower()} | {r['exit_signal']} | {r['exit_time']:%Y-%m-%d %H:%M} | "
                   f"{r['exit_price']:.2f} | {r['contracts']} | {money} | {usd(r['cum_profit'])} | "
                   f"{usd(r['run_up'])} | {usd(r['drawdown'])} |")
        out.append(f"|  | Entry {side.lower()} | {r['entry_signal']} | {r['entry_time']:%Y-%m-%d %H:%M} | "
                   f"{r['entry_price']:.2f} | {r['contracts']} |  |  |  |  |")
    return "\n".join(out)


def by_year(tf: pd.DataFrame) -> str:
    y = metrics.by_year(tf)
    out = ["| Year | Trades | Net profit | % profitable | Profit factor |", "|---|---|---|---|---|"]
    for _, r in y.iterrows():
        out.append(f"| {int(r['year'])} | {int(r['trades'])} | {usd(r['net_profit'])} | "
                   f"{pct(r['percent_profitable'])} | {num(r['profit_factor'])} |")
    return "\n".join(out)


def scenario_table(sums: dict[int, dict]) -> str:
    cols = list(sums)
    head = "| Metric | " + " | ".join("Baseline (0 ticks)" if k == 0 else f"{k} tick{'s' if k > 1 else ''}"
                                       for k in cols) + " |"
    rows = [
        ("Net profit", lambda s: usd(s["all"]["net_profit"])),
        ("Total closed trades", lambda s: f"{s['all']['total_closed_trades']:,}"),
        ("Percent profitable", lambda s: pct(s["all"]["percent_profitable"])),
        ("Profit factor", lambda s: num(s["all"]["profit_factor"])),
        ("Avg trade", lambda s: usd(s["all"]["avg_trade"])),
        ("Max equity drawdown", lambda s: usd(s["max_equity_drawdown"])),
        ("Sharpe ratio", lambda s: num(s["sharpe_ratio"])),
        ("Sortino ratio", lambda s: num(s["sortino_ratio"])),
    ]
    return "\n".join([head, "|---" * (len(cols) + 1) + "|"] +
                     [f"| {lab} | " + " | ".join(f(sums[k]) for k in cols) + " |" for lab, f in rows])


def equity_png(results: dict[int, Result], path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 4), dpi=110)
    for k, res in results.items():
        tf = metrics.trade_frame(res)
        if tf.empty:
            continue
        eq = res.props.initial_capital + tf["cum_profit"]
        ax.plot(tf["exit_time"], eq, lw=1.2 if k == 0 else 0.9,
                label="Baseline (0 ticks)" if k == 0 else f"{k} tick slippage")
    ax.axhline(results[0].props.initial_capital, color="#888", lw=0.6, ls="--")
    ax.set_title(title)
    ax.set_ylabel("Equity (USD)")
    ax.grid(alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def full_report(s: dict, tf: pd.DataFrame, level: int = 4) -> str:
    h = "#" * level
    return (f"{h} Overview\n\n{overview(s)}\n\n{h} Performance\n\n{performance(s)}\n\n"
            f"{h} Trades analysis\n\n{trades_analysis(s)}\n\n{h} Risk/performance ratios\n\n{ratios(s)}\n")


def save_variant(results: dict[int, Result], grid: pd.DataFrame, out_dir: Path) -> dict:
    """Write CSV / JSON for one tested variant; return the summaries by slippage."""
    out_dir.mkdir(parents=True, exist_ok=True)
    grid.to_csv(out_dir / "grid.csv", index=False)
    sums = {}
    for k, res in results.items():
        s = metrics.summary(res)
        sums[k] = s
        metrics.trade_frame(res).to_csv(out_dir / f"trades_slippage{k}.csv", index=False)
    (out_dir / "summary.json").write_text(json.dumps({f"slippage_{k}": v for k, v in sums.items()}, indent=2,
                                                     default=str))
    return sums
