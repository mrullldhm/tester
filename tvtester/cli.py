"""Test a strategy and write its result document.

    .venv/bin/python -m tvtester.cli test fair_price_reversal [--start 2010-06-07] [--end 2026-10-28]
        [--jobs 1] [--chunks 1]

A strategy module in strategies/ exposes:
    STRATEGY  Strategy subclass          TITLE, ABOUT  Markdown header text (CONCLUSION optional, shown after the summary)
    DOC       optional result file name in docs/strategies/<name>/ (default README.md)
    GRID      {param: [values]}          VARIANTS      {variant: {fixed params}} (one doc section each)
    notes(tf, params) -> list[str]       optional extra lines per variant
For each variant the grid runs once per setting without added slippage and selects thirteen metric winners.
The historical net-profit reference is retained. Output: docs/strategies/<name>/README.md (+ PNGs) and
results/<name>/<variant>/. --output-tag metrics keeps the old outputs and writes a separate metrics report.

Feature 2 (docs/OPTIMIZE.md; development interval only, every run logged to results/<name>/ledger.jsonl):
    features <name> --variant ny                      association report of the baseline trades
    search <name> --variant ny --space filters --sampler random --trials 200 --objective net0 --seed 1 --jobs 1
    replay strategies/configs/<file>.json             frozen configuration, baseline only

Exit study (docs/ENGINE.md "Exit management"; full feature-1 interval, logged to the ledger):
    exits <name> --jobs 1                             breakeven / trailing stop sweep on the frozen baselines

Feature 3 (docs/VALIDATE.md; development interval only, logged to the ledger):
    validate strategies/configs/<file>.json --jobs 1  walk-forward re-selection, CSCV / PBO, deflated Sharpe
"""

import sys

if __name__ == "__main__":
    from .resource_guard import entrypoint
    entrypoint(["-m", "tvtester.cli", *sys.argv[1:]])

import argparse
import importlib
import json
import re
import time
from datetime import datetime, timezone

from joblib import Parallel, delayed

from . import metrics, optimize, report
from .config import DEFAULT, ROOT, SLIPPAGE_SCENARIOS
from .data import MANIFEST, Bars, load_bars
from .objectives import DEFAULT_MIN_TRADES, DEFAULT_RUIN_LOSS, OBJECTIVES, selection, validate_options


def _factory(mod, variant: str):
    fixed = mod.VARIANTS[variant]

    def factory(**p):
        return mod.STRATEGY(**fixed, **p)
    return factory


def _grid_chunk(module_name: str, variant: str, start: str | None, end: str | None, orders: list[int],
                ruin_loss: float = DEFAULT_RUIN_LOSS) -> list[dict]:
    """Grid rows of the combinations numbered `orders`, in their own process (bars loaded there)."""
    mod = importlib.import_module(f"strategies.{module_name}")
    bars = Bars.from_frame(load_bars(start, end))
    return optimize.grid_rows(_factory(mod, variant), mod.GRID, bars, DEFAULT, label=variant, orders=orders,
                              ruin_loss=ruin_loss)


def _finish_variant(module_name: str, variant: str, start: str | None, end: str | None, rows: list[dict],
                    min_trades: int = DEFAULT_MIN_TRADES, ruin_loss: float = DEFAULT_RUIN_LOSS, output_tag: str = ""):
    mod = importlib.import_module(f"strategies.{module_name}")
    bars = Bars.from_frame(load_bars(start, end))
    fixed = mod.VARIANTS[variant]
    factory = _factory(mod, variant)
    grid = optimize.rank(rows)
    best = {k: grid.iloc[0][k] for k in mod.GRID}
    best = {k: (v.item() if hasattr(v, "item") else v) for k, v in best.items()}
    results = optimize.stress(factory, best, bars)
    out = ROOT / "results" / module_name
    if output_tag:
        out /= output_tag
    out /= variant
    sums = report.save_variant(results, grid, out)
    selected = selection(grid, mod.GRID, min_trades, ruin_loss)
    from .experiment import EXECUTION_VERSION

    selected["execution_version"] = EXECUTION_VERSION
    selected["period_start"], selected["period_end"] = str(bars.ts[0]), str(bars.ts[-1])
    # Rerun each distinct winner once; several objectives can choose the same settings.
    saved = set()
    for winner in selected["winners"].values():
        if winner is None or winner["order"] in saved:
            continue
        order = winner["order"]
        chosen = results if order == int(grid.iloc[0]["order"]) else optimize.stress(factory, winner["params"], bars)
        report.save_variant(chosen, grid[grid["order"] == order], out / "metric_winners" / f"order_{order}")
        saved.add(order)
    (out / "metric_winners.json").write_text(json.dumps(selected, indent=2, allow_nan=False))
    doc_dir = ROOT / "docs" / "strategies" / module_name
    png = doc_dir / f"{output_tag + '_' if output_tag else ''}equity_{variant}.png"
    report.equity_png(results, png, f"{mod.TITLE}: {variant} (top combination)")
    tfs = {k: metrics.trade_frame(r) for k, r in results.items()}
    extra = mod.notes(tfs[0], {**fixed, **best}) if hasattr(mod, "notes") else []
    return variant, best, grid, sums, tfs, extra, len(bars), str(bars.ts[0]), str(bars.ts[-1])


def write_doc(mod, module_name: str, outputs: list, n_combos: int, output_tag: str = "") -> str:
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
        "| Execution | Limit entries; commission included; no added slippage |",
        "| Pyramiding | 0 (one position) |",
        "| Fills | TradingView broker emulator, Bar Magnifier off, limits fill on touch |",
        "| Roll rule | position closed at the last bar of a contract (exit reason `roll`) |",
        "",
        "## How the top combination was chosen", "",
        f"Every variant ran all {n_combos} combinations of the grid below with commission included. The combination "
        "with the highest **net profit** is the top combination (ties: higher profit factor, then grid order). "
        "This reference is retained for compatibility. Thirteen separate metric winners are also selected, "
        "with a declared minimum trade count; their values, settings and trade lists are linked below. "
        "No slippage stress runs are performed.", "",
        "| Parameter | Values |", "|---|---|",
        *[f"| `{k}` | {', '.join(map(str, v))} |" for k, v in mod.GRID.items()], "",
        "> **Read this first.** The top combination is the best of "
        f"{n_combos} tries on the same data it is reported on (in-sample). Picking the best of many tries makes "
        "the result look better than what the same rules can be expected to earn on new data. Treat these numbers "
        "as an upper bound, not as a forecast.", "",
        "## Summary: top combination per variant", "",
        "| Variant | Parameters | Net profit | Trades | % profitable | Profit factor | Max DD |",
        "|---|---|---|---|---|---|---|",
    ]
    for variant, best, grid, sums, *_ in outputs:
        s0 = sums[0]
        nets = " / ".join(report.usd(sums[k]["all"]["net_profit"]) for k in sums)
        lines.append(f"| {variant} | {', '.join(f'{k}={v}' for k, v in best.items())} | {nets} | "
                     f"{s0['all']['total_closed_trades']:,} | {report.pct(s0['all']['percent_profitable'])} | "
                     f"{report.num(s0['all']['profit_factor'])} | {report.usd(s0['max_equity_drawdown'])} |")
    lines.append("")
    if getattr(mod, "CONCLUSION", "") and not output_tag:
        lines += ["## Conclusion", "", mod.CONCLUSION.strip(), ""]
    for variant, best, grid, sums, tfs, extra, *_ in outputs:
        res_dir = ROOT / "results" / module_name
        if output_tag:
            res_dir /= output_tag
        res_dir /= variant
        png_name = f"{output_tag + '_' if output_tag else ''}equity_{variant}.png"
        lines += [
            f"## Variant: {variant}", "",
            f"**Top combination:** {', '.join(f'`{k}={v}`' for k, v in {**mod.VARIANTS[variant], **best}.items())}",
            "", f"![Equity curve]({png_name})", "",
            f"Files: [grid]({report.rel(res_dir / 'grid.csv', doc_dir)}), "
            + ", ".join(f"[trades {k} ticks]({report.rel(res_dir / f'trades_slippage{k}.csv', doc_dir)})"
                        for k in sums)
            + f", [summary]({report.rel(res_dir / 'summary.json', doc_dir)})", "",
            "### Results after commission", "", report.full_report(sums[0], tfs[0]),
            "#### List of trades (last 10, newest first; full list in the trades CSV)", "",
            report.trade_list(tfs[0]), "",
            "#### By year (extra, not a TV tab)", "", report.by_year(tfs[0]), "",
            "#### Exit reasons (extra)", "",
            "| Reason | Trades |", "|---|---|",
            *[f"| {k} | {v} |" for k, v in sums[0]["exit_reasons"].items()], "",
            *[f"- {x}" for x in extra], "",
        ]
        if (res_dir / "metric_winners.json").exists():
            selected = json.loads((res_dir / "metric_winners.json").read_text())
            lines += ["### Best settings by metric", "",
                      f"Each winner needs at least {selected['min_trades']} closed trades. Undefined values are excluded. "
                      "Ties: higher net profit, higher profit factor, then grid order. "
                      f"Ruin loss threshold: {report.usd(selected['ruin_loss'])} from starting capital. "
                      "All selections are in-sample. MAE/MFE objectives use the mean of the per-trade maxima.", "",
                      "| Metric | Goal | Best value | Grid order | Trades | Eligible settings | Parameters |", "|---|---|---|---|---|---|---|"]
            for objective in OBJECTIVES:
                w = selected["winners"][objective.key]
                if w is None:
                    lines.append(f"| {objective.label} | {objective.direction} | No eligible value | — | — | 0 | — |")
                else:
                    fmt = report.usd if objective.unit == "usd" else report.pct if objective.unit == "percent" else report.num
                    path = res_dir / "metric_winners" / f"order_{w['order']}" / "trades_slippage0.csv"
                    lines.append(f"| {objective.label} | {objective.direction} | {fmt(w['value'])} | "
                                 f"[{w['order']}]({report.rel(path, doc_dir)}) | {w['total_closed_trades']} | "
                                 f"{w['eligible']} | {', '.join(f'{k}={v}' for k, v in w['params'].items())} |")
            lines += ["", *[f"- **{o.label}:** {o.definition}" for o in OBJECTIVES], "",
                      f"Full selection metadata: [metric_winners.json]({report.rel(res_dir / 'metric_winners.json', doc_dir)}).", ""]
        for k in SLIPPAGE_SCENARIOS:
            lines += [f"#### {k} tick{'s' if k > 1 else ''} slippage: full report", "",
                      report.full_report(sums[k], tfs[k], level=5)]
        top = grid.head(10)
        cols = list(mod.GRID)
        lines += [
            "### Top 10 combinations", "",
            "| # | " + " | ".join(cols) + " | Net profit | Trades | % profitable | Profit factor | Max DD |",
            "|---" * (len(cols) + 6) + "|",
            *[f"| {n} | " + " | ".join(str(r[c]) for c in cols) + f" | {report.usd(r['net_profit'])} | "
              f"{int(r['total_closed_trades']):,} | {report.pct(r['percent_profitable'])} | "
              f"{report.num(r['profit_factor'])} | {report.usd(r['max_equity_drawdown'])} |"
              for n, (_, r) in enumerate(top.iterrows(), 1)],
            f"", f"Profitable combinations: {(grid['net_profit'] > 0).sum()} of {len(grid)}.", "",
        ]
    path = doc_dir / (f"{output_tag}.md" if output_tag else getattr(mod, "DOC", "README.md"))
    path.write_text("\n".join(lines))
    return str(path)


def main() -> None:
    ap = argparse.ArgumentParser(prog="tvtester")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("test", help="run a strategy grid and write its document")
    t.add_argument("strategy")
    t.add_argument("--start")
    t.add_argument("--end")
    t.add_argument("--jobs", type=int, default=1)
    t.add_argument("--variants", nargs="*")
    t.add_argument("--chunks", type=int, default=1, help="split each variant's grid over this many processes")
    t.add_argument("--min-trades", type=int, default=DEFAULT_MIN_TRADES,
                   help="minimum closed trades for each of the 13 metric winners (default: 30)")
    t.add_argument("--ruin-loss", type=float, default=DEFAULT_RUIN_LOSS,
                   help="loss in USD from starting capital for the estimated risk of ruin (default: 25000)")
    t.add_argument("--output-tag", default="", help="separate named results/report; use metrics to preserve historical reports")
    f = sub.add_parser("features", help="feature association report (development interval)")
    f.add_argument("strategy")
    f.add_argument("--variant", required=True)
    se = sub.add_parser("search", help="random / TPE search (development interval)")
    se.add_argument("strategy")
    se.add_argument("--variant", required=True)
    se.add_argument("--space", required=True)
    se.add_argument("--sampler", choices=["random", "tpe"], required=True)
    se.add_argument("--trials", type=int, required=True)
    se.add_argument("--objective", choices=["net0"], required=True)
    se.add_argument("--seed", type=int, default=1)
    se.add_argument("--jobs", type=int, default=1)
    se.add_argument("--run-tag", default="", help="unique suffix for a new attempt; preserves interrupted runs")
    r = sub.add_parser("replay", help="run a frozen configuration (development interval)")
    r.add_argument("config")
    v = sub.add_parser("validate", help="feature 3: validate a frozen feature-2 candidate (development interval)")
    v.add_argument("config")
    v.add_argument("--jobs", type=int, default=1)
    v.add_argument("--run-tag", default="", help="unique suffix for a new validation attempt")
    x = sub.add_parser("exits", help="exit study: breakeven / trailing stop on the frozen feature-1 baselines")
    x.add_argument("strategy")
    x.add_argument("--jobs", type=int, default=1)
    x.add_argument("--variants", nargs="*")
    a = ap.parse_args()
    if getattr(a, "jobs", 1) != 1:
        ap.error("Research safety requires --jobs 1; parallel workloads are disabled")
    if a.cmd == "exits":
        from . import exitstudy

        t0 = time.time()
        print(f"wrote {exitstudy.cmd_exits(a.strategy, a.jobs, a.variants)} in {time.time() - t0:.0f}s")
        return
    if a.cmd == "validate":
        from . import validate

        t0 = time.time()
        print(f"wrote {validate.cmd_validate(a.config, a.jobs, a.run_tag)} in {time.time() - t0:.0f}s")
        return
    if a.cmd != "test":
        from . import tune

        t0 = time.time()
        if a.cmd == "features":
            path = tune.cmd_features(a.strategy, a.variant)
        elif a.cmd == "search":
            path = tune.cmd_search(a.strategy, a.variant, a.space, a.sampler, a.trials, a.objective, a.seed, a.jobs, a.run_tag)
        else:
            path = tune.cmd_replay(a.config)
        print(f"wrote {path} in {time.time() - t0:.0f}s")
        return
    mod = importlib.import_module(f"strategies.{a.strategy}")
    validate_options(a.min_trades, a.ruin_loss)
    if a.output_tag and not re.fullmatch(r"[a-z][a-z0-9_]*", a.output_tag):
        raise ValueError("output-tag must contain only lowercase letters, digits and underscores, starting with a letter")
    if a.ruin_loss > DEFAULT.initial_capital:
        raise ValueError("ruin-loss cannot exceed starting capital")
    variants = a.variants or list(mod.VARIANTS)
    t0 = time.time()
    n = len(optimize.combos(mod.GRID))
    k = max(1, min(a.chunks, n))
    tasks = [(v, list(range(j + 1, n + 1, k))) for v in variants for j in range(k)]  # interleaved: even chunk cost
    parts = Parallel(n_jobs=a.jobs)(delayed(_grid_chunk)(a.strategy, v, a.start, a.end, o, a.ruin_loss) for v, o in tasks)
    rows = {v: [] for v in variants}
    for (v, _), r in zip(tasks, parts):
        rows[v] += r
    outputs = Parallel(n_jobs=a.jobs)(delayed(_finish_variant)(a.strategy, v, a.start, a.end, rows[v], a.min_trades, a.ruin_loss, a.output_tag)
                                      for v in variants)
    path = write_doc(mod, a.strategy, outputs, n, a.output_tag)
    print(f"wrote {path} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
