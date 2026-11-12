"""Command line.

    python -m cltester.cli info                              data range and research periods
    python -m cltester.cli update [--source massive] [--yes] add new bars (Databento asks before paying)
    python -m cltester.cli test <name> [--period dev] [--set key=value ...]

`test` runs the backtest and the Topstep Combine simulator, prints both, saves the trades and appends one
row to results/ledger.csv. The holdout period runs once per strategy (docs/PROTOCOL.md).
"""

import argparse
import ast
import csv
import json
from datetime import UTC, datetime

import pandas as pd

from . import metrics, topstep
from .config import COMBINE_50K, LEDGER, MANIFEST, PERIODS, RESULTS
from .data import Bars, load_period
from .engine import Fills, backtest
from .strategy import load, params_hash

LEDGER_FIELDS = ["utc", "strategy", "hash", "period", "params", "trades", "net", "profit_factor",
                 "win_rate", "max_drawdown", "pass_rate", "seq_passes", "seq_fails", "seq_cost_per_pass_usd"]


def _parse_set(items: list[str]) -> dict:
    out = {}
    for it in items:
        k, _, v = it.partition("=")
        try:
            out[k] = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            out[k] = v
    return out


def _touches_holdout(period: str) -> bool:
    lo, hi = PERIODS[period]
    h_lo, h_hi = PERIODS["holdout"]
    return (lo is None or lo < str(h_hi)) and (hi is None or hi > str(h_lo))


def _ledger_rows() -> list[dict]:
    if not LEDGER.exists():
        return []
    with LEDGER.open() as f:
        return list(csv.DictReader(f))


def cmd_info(_: argparse.Namespace) -> None:
    man = json.loads(MANIFEST.read_text())
    print(f"bars {man['first_bar']} -> {man['last_bar']}  rows {man['rows']:,}  vendors {man.get('rows_by_vendor')}")
    for k, (a, b) in PERIODS.items():
        print(f"  {k:<11} {a or 'start'} -> {b or 'latest'}")


def cmd_update(a: argparse.Namespace) -> None:
    from .update import run

    run(a.source, a.end, a.yes)


def cmd_test(a: argparse.Namespace) -> None:
    strat = load(a.name)
    p = {**strat.PARAMS, **_parse_set(a.set)}
    unknown = set(p) - set(strat.PARAMS)
    if unknown:
        raise SystemExit(f"unknown params {sorted(unknown)}")
    h = params_hash(a.name, p)
    if _touches_holdout(a.period) and not a.unlock:
        if a.period != "holdout":
            raise SystemExit(f"period {a.period} includes holdout bars; use --period holdout (once) or --unlock")
        if any(r["strategy"] == a.name and r["period"] == "holdout" for r in _ledger_rows()):
            raise SystemExit("holdout already used for this strategy (docs/PROTOCOL.md); --unlock to override")
    df = load_period(a.period)
    bars = Bars.from_frame(df)
    fills = Fills()
    trades = backtest(bars, strat.signals(df, p), fills)
    days = topstep.trading_days(df)
    stats = metrics.summary(trades, days)
    combine = topstep.summary(topstep.rolling(trades, days), topstep.sequential(trades, days), days)

    print(f"{a.name} [{h}] period={a.period} params={p}")
    print(f"fills: limit touch, no exit slippage, fee=${fills.fee}/RT  (in-sample unless period is holdout/forward)")
    for k, v in stats.items():
        print(f"  {k:<18} {v}")
    print(f"{COMBINE_50K.name}:")
    for k, v in combine.items():
        print(f"  {k:<22} {v}")

    out = RESULTS / a.name
    out.mkdir(parents=True, exist_ok=True)
    trades.to_csv(out / f"{a.period}_{h}.csv", index=False)
    row = {"utc": datetime.now(UTC).isoformat(timespec="seconds"), "strategy": a.name, "hash": h,
           "period": a.period, "params": json.dumps(p, sort_keys=True),
           **{k: stats.get(k) for k in ("trades", "net", "profit_factor", "win_rate", "max_drawdown")},
           **{k: combine[k] for k in ("pass_rate", "seq_passes", "seq_fails", "seq_cost_per_pass_usd")}}
    new = not LEDGER.exists()
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def main() -> None:
    ap = argparse.ArgumentParser(prog="cltester")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info").set_defaults(fn=cmd_info)
    u = sub.add_parser("update")
    u.add_argument("--source", choices=["databento", "massive"], default="databento")
    u.add_argument("--end", help="UTC date or time, exclusive")
    u.add_argument("--yes", action="store_true", help="skip the Databento cost prompt (owner approved the quote)")
    u.set_defaults(fn=cmd_update)
    t = sub.add_parser("test")
    t.add_argument("name")
    t.add_argument("--period", choices=list(PERIODS), default="dev")
    t.add_argument("--set", nargs="*", default=[], help="param overrides key=value")
    t.add_argument("--unlock", action="store_true", help="allow a second holdout run")
    t.set_defaults(fn=cmd_test)
    a = ap.parse_args()
    pd.set_option("display.width", 160)
    a.fn(a)


if __name__ == "__main__":
    main()
