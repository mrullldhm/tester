"""Test a strategy and write its result document.

    .venv/bin/python -m tvtester.cli test fair_price_reversal [--start 2010-06-07] [--end 2026-10-28]
        [--jobs 3] [--chunks 1]

A strategy module in strategies/ exposes:
    STRATEGY  Strategy subclass          TITLE, ABOUT  Markdown header text (CONCLUSION optional, shown after the summary)
    GRID      {param: [values]}          VARIANTS      {variant: {fixed params}} (one doc section each)
    notes(tf, params) -> list[str]       optional extra lines per variant
For each variant the grid runs at 0 ticks slippage, the highest net profit wins, and the winner is run again
at every slippage scenario. Output: docs/strategies/<name>/README.md (+ PNGs) and results/<name>/<variant>/.

Feature 2 (docs/OPTIMIZE.md; development interval only, every run logged to results/<name>/ledger.jsonl):
    features <name> --variant ny                      association report of the baseline trades
    search <name> --variant ny --space filters --sampler random --trials 200 --objective net1 --seed 1 --jobs 3
    replay strategies/configs/<file>.json             frozen configuration at 0 / 1 / 2 ticks

Exit study (docs/ENGINE.md "Exit management"; full feature-1 interval, logged to the ledger):
    exits <name> --jobs 6                             breakeven / trailing stop sweep on the frozen baselines

Feature 3 (docs/VALIDATE.md; development interval only, logged to the ledger):
    validate strategies/configs/<file>.json --jobs 4  walk-forward re-selection, CSCV / PBO, deflated Sharpe
"""

import argparse
import importlib
import json
import time
from datetime import datetime, timezone

from joblib import Parallel, delayed

from . import metrics, optimize, report
from .config import DEFAULT, ROOT, SLIPPAGE_SCENARIOS
from .data import MANIFEST, Bars, load_bars


def _factory(mod, variant: str):
    fixed = mod.VARIANTS[variant]

    def factory(**p):
        return mod.STRATEGY(**fixed, **p)
    return factory


def _grid_chunk(module_name: str, variant: str, start: str | None, end: str | None, orders: list[int]) -> list[dict]:
    """Grid rows of the combinations numbered `orders`, in their own process (bars loaded there)."""
    mod = importlib.import_module(f"strategies.{module_name}")
    bars = Bars.from_frame(load_bars(start, end))
    return optimize.grid_rows(_factory(mod, variant), mod.GRID, bars, DEFAULT, label=variant, orders=orders)


def _finish_variant(module_name: str, variant: str, start: str | None, end: str | None, rows: list[dict]):
    mod = importlib.import_module(f"strategies.{module_name}")
    bars = Bars.from_frame(load_bars(start, end))
    fixed = mod.VARIANTS[variant]
    factory = _factory(mod, variant)
    grid = optimize.rank(rows)
    best = {k: grid.iloc[0][k] for k in mod.GRID}
    best = {k: (v.item() if hasattr(v, "item") else v) for k, v in best.items()}
    results = optimize.stress(factory, best, bars)
    out = ROOT / "results" / module_name / variant
    sums = report.save_variant(results, grid, out)
    doc_dir = ROOT / "docs" / "strategies" / module_name
    png = doc_dir / f"equity_{variant}.png"
    report.equity_png(results, png, f"{mod.TITLE}: {variant} (top combination)")
    tfs = {k: metrics.trade_frame(r) for k, r in results.items()}
    extra = mod.notes(tfs[0], {**fixed, **best}) if hasattr(mod, "notes") else []
    return variant, best, grid, sums, tfs, extra, len(bars), str(bars.ts[0]), str(bars.ts[-1])


def write_doc(mod, module_name: str, outputs: list, n_combos: int) -> str:
    doc_dir = ROOT / "docs" / "strategies" / module_name
    _, _, _, _, _, _, nbars, first, last = outputs[0]
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    lines = [
        f"# {mod.TITLE}: results", "",
        f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC by `python -m tvtester.cli test {module_name}`.",
        "", mod.ABOUT.strip(), "",
        "## Test settings (TradingView Properties)", "",
        "| Setting | Value |", "|---|---|",
        f"| Symbol | CL1! (NYMEX Light Crude Oil, front month), 1-minute bars |",
        f"| Data | {first} to {last} UTC, {nbars:,} bars (manifest written {manifest.get('written_utc', '?')}) |",
        f"| Initial capital | {report.usd(DEFAULT.initial_capital)} |",
        f"| Order size | {DEFAULT.qty} contract |",
        f"| Commission | {report.usd(DEFAULT.commission_per_order)} per contract per order "
        f"({report.usd(2 * DEFAULT.commission_per_order)} round trip) |",
        "| Slippage | 0 ticks baseline; " + ", ".join(f"{k} tick" + ("s" if k > 1 else "") for k in SLIPPAGE_SCENARIOS)
        + " shown separately (market and stop fills only, as TradingView) |",
        "| Pyramiding | 0 (one position) |",
        "| Fills | TradingView broker emulator, Bar Magnifier off, limits fill on touch |",
        "| Roll rule | position closed at the last bar of a contract (exit reason `roll`) |",
        "",
        "## How the top combination was chosen", "",
        f"Every variant ran all {n_combos} combinations of the grid below at 0 ticks slippage. The combination "
        "with the highest **net profit** is the top combination (ties: higher profit factor, then grid order). "
        "Its slippage results use the same parameters, never a re-optimized set.", "",
        "| Parameter | Values |", "|---|---|",
        *[f"| `{k}` | {', '.join(map(str, v))} |" for k, v in mod.GRID.items()], "",
        "> **Read this first.** The top combination is the best of "
        f"{n_combos} tries on the same data it is reported on (in-sample). Picking the best of many tries makes "
        "the result look better than what the same rules can be expected to earn on new data. Treat these numbers "
        "as an upper bound, not as a forecast.", "",
        "## Summary: top combination per variant", "",
        "| Variant | Parameters | Net profit (0 / " + " / ".join(f"{k}" for k in SLIPPAGE_SCENARIOS)
        + " ticks) | Trades | % profitable | Profit factor | Max DD |",
        "|---|---|---|---|---|---|---|",
    ]
    for variant, best, grid, sums, *_ in outputs:
        s0 = sums[0]
        nets = " / ".join(report.usd(sums[k]["all"]["net_profit"]) for k in sums)
        lines.append(f"| {variant} | {', '.join(f'{k}={v}' for k, v in best.items())} | {nets} | "
                     f"{s0['all']['total_closed_trades']:,} | {report.pct(s0['all']['percent_profitable'])} | "
                     f"{report.num(s0['all']['profit_factor'])} | {report.usd(s0['max_equity_drawdown'])} |")
    lines.append("")
    if getattr(mod, "CONCLUSION", ""):
        lines += ["## Conclusion", "", mod.CONCLUSION.strip(), ""]
    for variant, best, grid, sums, tfs, extra, *_ in outputs:
        res_dir = ROOT / "results" / module_name / variant
        lines += [
            f"## Variant: {variant}", "",
            f"**Top combination:** {', '.join(f'`{k}={v}`' for k, v in {**mod.VARIANTS[variant], **best}.items())}",
            "", f"![Equity curve]({f'equity_{variant}.png'})", "",
            f"Files: [grid]({report.rel(res_dir / 'grid.csv', doc_dir)}), "
            + ", ".join(f"[trades {k} ticks]({report.rel(res_dir / f'trades_slippage{k}.csv', doc_dir)})"
                        for k in sums)
            + f", [summary]({report.rel(res_dir / 'summary.json', doc_dir)})", "",
            "### Baseline: 0 ticks slippage", "", report.full_report(sums[0], tfs[0]),
            "#### List of trades (last 10, newest first; full list in the trades CSV)", "",
            report.trade_list(tfs[0]), "",
            "#### By year (extra, not a TV tab)", "", report.by_year(tfs[0]), "",
            "#### Exit reasons (extra)", "",
            "| Reason | Trades |", "|---|---|",
            *[f"| {k} | {v} |" for k, v in sums[0]["exit_reasons"].items()], "",
            *[f"- {x}" for x in extra], "",
            "### Slippage scenarios (same parameters)", "", report.scenario_table(sums), "",
        ]
        for k in SLIPPAGE_SCENARIOS:
            lines += [f"#### {k} tick{'s' if k > 1 else ''} slippage: full report", "",
                      report.full_report(sums[k], tfs[k], level=5)]
        top = grid.head(10)
        cols = list(mod.GRID)
        lines += [
            "### Top 10 combinations (0 ticks)", "",
            "| # | " + " | ".join(cols) + " | Net profit | Trades | % profitable | Profit factor | Max DD |",
            "|---" * (len(cols) + 6) + "|",
            *[f"| {n} | " + " | ".join(str(r[c]) for c in cols) + f" | {report.usd(r['net_profit'])} | "
              f"{int(r['total_closed_trades']):,} | {report.pct(r['percent_profitable'])} | "
              f"{report.num(r['profit_factor'])} | {report.usd(r['max_equity_drawdown'])} |"
              for n, (_, r) in enumerate(top.iterrows(), 1)],
            f"", f"Profitable combinations: {(grid['net_profit'] > 0).sum()} of {len(grid)}.", "",
        ]
    path = doc_dir / "README.md"
    path.write_text("\n".join(lines))
    return str(path)


def main() -> None:
    ap = argparse.ArgumentParser(prog="tvtester")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("test", help="run a strategy grid and write its document")
    t.add_argument("strategy")
    t.add_argument("--start")
    t.add_argument("--end")
    t.add_argument("--jobs", type=int, default=3)
    t.add_argument("--variants", nargs="*")
    t.add_argument("--chunks", type=int, default=1, help="split each variant's grid over this many processes")
    f = sub.add_parser("features", help="feature association report (development interval)")
    f.add_argument("strategy")
    f.add_argument("--variant", required=True)
    se = sub.add_parser("search", help="random / TPE search (development interval)")
    se.add_argument("strategy")
    se.add_argument("--variant", required=True)
    se.add_argument("--space", required=True)
    se.add_argument("--sampler", choices=["random", "tpe"], required=True)
    se.add_argument("--trials", type=int, required=True)
    se.add_argument("--objective", choices=["net0", "net1"], required=True)
    se.add_argument("--seed", type=int, default=1)
    se.add_argument("--jobs", type=int, default=1)
    r = sub.add_parser("replay", help="run a frozen configuration (development interval)")
    r.add_argument("config")
    v = sub.add_parser("validate", help="feature 3: validate a frozen feature-2 candidate (development interval)")
    v.add_argument("config")
    v.add_argument("--jobs", type=int, default=1)
    x = sub.add_parser("exits", help="exit study: breakeven / trailing stop on the frozen feature-1 baselines")
    x.add_argument("strategy")
    x.add_argument("--jobs", type=int, default=6)
    x.add_argument("--variants", nargs="*")
    a = ap.parse_args()
    if a.cmd == "exits":
        from . import exitstudy

        t0 = time.time()
        print(f"wrote {exitstudy.cmd_exits(a.strategy, a.jobs, a.variants)} in {time.time() - t0:.0f}s")
        return
    if a.cmd == "validate":
        from . import validate

        t0 = time.time()
        print(f"wrote {validate.cmd_validate(a.config, a.jobs)} in {time.time() - t0:.0f}s")
        return
    if a.cmd != "test":
        from . import tune

        t0 = time.time()
        if a.cmd == "features":
            path = tune.cmd_features(a.strategy, a.variant)
        elif a.cmd == "search":
            path = tune.cmd_search(a.strategy, a.variant, a.space, a.sampler, a.trials, a.objective, a.seed, a.jobs)
        else:
            path = tune.cmd_replay(a.config)
        print(f"wrote {path} in {time.time() - t0:.0f}s")
        return
    mod = importlib.import_module(f"strategies.{a.strategy}")
    variants = a.variants or list(mod.VARIANTS)
    t0 = time.time()
    n = len(optimize.combos(mod.GRID))
    k = max(1, min(a.chunks, n))
    tasks = [(v, list(range(j + 1, n + 1, k))) for v in variants for j in range(k)]  # interleaved: even chunk cost
    parts = Parallel(n_jobs=a.jobs)(delayed(_grid_chunk)(a.strategy, v, a.start, a.end, o) for v, o in tasks)
    rows = {v: [] for v in variants}
    for (v, _), r in zip(tasks, parts):
        rows[v] += r
    outputs = Parallel(n_jobs=a.jobs)(delayed(_finish_variant)(a.strategy, v, a.start, a.end, rows[v])
                                      for v in variants)
    path = write_doc(mod, a.strategy, outputs, n)
    print(f"wrote {path} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
