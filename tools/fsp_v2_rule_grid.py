"""F2 run 1 for FSP v2: all 16 readings of the four owner-unresolved rules (docs/strategies/failed_swing_point_v2/optimize/README.md).

Invoke through tools/run_limited.py. Development interval only; ledger first, engine after.
"""
from datetime import datetime, timezone
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    from tvtester.resource_guard import entrypoint
    entrypoint([str(Path(__file__).resolve()), *sys.argv[1:]])

RUN_ID = "rules_grid_net0_n16"
BASELINE = {"net0": -11925.96, "trades": 3198}  # FSP v1 fixed default, first_default_first_mss_halt_2023
MIN_TRADES = 300
LETTERS = {"burn_invalid_first": "A", "stop_search": "B", "breach_minute_hl": "C", "offhours_setups": "D"}


def configs():
    from strategies.failed_swing_point_v2 import RULE_DEFAULTS
    keys = list(RULE_DEFAULTS)
    grid = [dict(zip(keys, v)) for v in itertools.product((False, True), repeat=len(keys))]
    grid.remove(RULE_DEFAULTS)
    return [dict(RULE_DEFAULTS)] + grid  # trial 0 = feature 1 default


def label(rules):
    return " ".join(f"{LETTERS[k]}{'+' if v else '-'}" for k, v in rules.items())


def main():
    import pandas as pd
    from strategies.failed_swing_point_v2 import FailedSwingPointV2
    from tvtester import experiment, metrics, report
    from tvtester.config import ROOT
    from tvtester.engine import run

    out = ROOT / "results" / "failed_swing_point_v2" / "search" / RUN_ID
    out.mkdir(parents=True, exist_ok=False)  # a run id is used once
    doc = ROOT / "docs" / "strategies" / "failed_swing_point_v2" / "optimize" / f"search_{RUN_ID}.md"
    grid = configs()
    bars = experiment.dev_bars()
    prov = experiment.provenance("failed_swing_point_v2", bars)
    (out / "run.json").write_text(json.dumps({"run_id": RUN_ID, "objective": "net0", "min_trades": MIN_TRADES,
                                              "trials": grid, "provenance": prov}, indent=2, default=str))
    experiment.log("failed_swing_point_v2", "search_batch", len(grid), run_id=RUN_ID, trials=len(grid))
    rows, results = [], {}
    for n, rules in enumerate(grid):
        strategy = FailedSwingPointV2(**rules)
        res = run(strategy, bars)
        s = metrics.summary(res)
        a = s["all"]
        row = {"trial": n, "label": label(rules), **rules, "net0": a["net_profit"] + s["open_pnl"],
               "trades0": a["total_closed_trades"], "pf": a["profit_factor"], "win_pct": a["percent_profitable"],
               "avg_trade": a["avg_trade"], "max_dd": s["max_equity_drawdown"],
               "long_net": s.get("long", {}).get("net_profit"), "short_net": s.get("short", {}).get("net_profit"),
               "setups": len(strategy.setups), "orders": sum(x[1] == "place" for x in strategy.actions)}
        rows.append(row)
        results[n] = (res, s, metrics.trade_frame(res))
        results[n][2].to_csv(out / f"trades_t{n:02d}.csv", index=False)
        print(json.dumps({k: row[k] for k in ("trial", "label", "net0", "trades0", "pf")}), flush=True)
        if n == 0 and (round(row["net0"], 2) != BASELINE["net0"] or row["trades0"] != BASELINE["trades"]):
            raise SystemExit(f"Trial 0 does not reproduce the FSP v1 baseline: {row}")
    df = pd.DataFrame(rows)
    df.to_csv(out / "trials.csv", index=False)
    ok = df[df.trades0 >= MIN_TRADES].copy()
    ok["pf_rank"] = ok.pf.fillna(float("inf"))
    ranked = ok.sort_values(["net0", "pf_rank", "trial"], ascending=[False, False, True])
    win = int(ranked.iloc[0].trial) if len(ranked) else None
    experiment.log("failed_swing_point_v2", "search", 0, run_id=RUN_ID, winner_trial=win, engine_runs=len(grid),
                   winner_net0=float(ranked.iloc[0].net0) if win is not None else None)

    usd = lambda v: "n/a" if v is None or pd.isna(v) else f"{v:,.2f}"
    L = [f"# FSP v2 — rule-interpretation grid ({RUN_ID})", "",
         "Pre-registered in [README.md](README.md). **In-sample, best of 16 evaluations, development interval "
         f"({bars.ts[0]} to {bars.ts[-1]}).** Not a validated edge.", "",
         "A = an invalid first MSS uses up the setup · B = search for the next stop extreme · "
         "C = an HL/LH on the breach minute is allowed · D = setups from any hour (not just 09:00–14:30 ET). "
         "`+` on, `-` off. Trial 0 is the FSP v1 default.", "",
         "| Rank | Trial | Rules | net0 USD | Trades | PF | Win % | Avg trade | Max DD | Long | Short |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for rank, r in enumerate(ranked.itertuples(), 1):
        L.append(f"| {rank} | {r.trial} | {r.label} | {usd(r.net0)} | {r.trades0:,} | {r.pf:.3f} | {r.win_pct:.2f} | "
                 f"{usd(r.avg_trade)} | {usd(r.max_dd)} | {usd(r.long_net)} | {usd(r.short_net)} |")
    if win is None:
        L += ["", "No eligible trial (fewer than 300 trades everywhere). Nothing is frozen."]
    else:
        _, s, trades = results[win]
        L += ["", f"## Best of 16: trial {win} ({label(grid[win])})", "",
              "In-sample, best of 16 evaluations. Slippage scenarios are not run (execution update, 3 November 2026).",
              "", report.full_report(s, trades), "", "## By year", "", report.by_year(trades)]
    L += ["", f"Raw files: `results/failed_swing_point_v2/search/{RUN_ID}/`. "
          f"Written {datetime.now(timezone.utc).isoformat(timespec='seconds')}.", ""]
    doc.write_text("\n".join(L))
    print(json.dumps({"report": str(doc), "winner": win}), flush=True)


if __name__ == "__main__":
    main()
