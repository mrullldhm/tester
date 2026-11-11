"""One fixed FSP baseline with audit artifacts. Invoke through tools/run_limited.py, --jobs 1."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    from tvtester.resource_guard import entrypoint
    entrypoint([str(Path(__file__).resolve()), *sys.argv[1:]])


def main():
    import pandas as pd
    from strategies.failed_swing_point import FailedSwingPoint
    from tvtester.config import ROOT
    from tvtester.data import Bars, load_bars
    from tvtester.engine import run
    from tvtester import metrics, report, swings

    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, choices=[1], default=1)
    ap.add_argument("--run-tag", required=True)
    ap.add_argument("--start")
    ap.add_argument("--end", default="2024-01-01")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", a.run_tag):
        ap.error("run-tag must start with a lowercase letter and contain lowercase letters, digits or underscores")
    if pd.Timestamp(a.end, tz="UTC") > pd.Timestamp("2024-01-01", tz="UTC"):
        ap.error("FSP performance must end before 2024-01-01 UTC")
    # Running the standard guard is mandatory; a direct accidental invocation cannot bypass it.
    out = ROOT / "results" / "failed_swing_point" / a.run_tag
    out.mkdir(parents=True, exist_ok=False)
    doc = ROOT / "docs" / "strategies" / "failed_swing_point" / f"{a.run_tag}.md"
    if doc.exists():
        raise FileExistsError(doc)
    status = {"status": "started", "started_utc": datetime.now(timezone.utc).isoformat(),
              "start": a.start, "end_exclusive": a.end, "swing_rule": swings.SWING_RULE,
              "lifecycle": "ny_session_first_mss_halt_v5",
              "variant": "original"}
    (out / "status.json").write_text(json.dumps(status, indent=2))
    print("Loading CL bars before", a.end, flush=True)
    bars = Bars.from_frame(load_bars(a.start, a.end))
    strategy = FailedSwingPoint()
    title = "FSP"
    print("Running fixed", title, "baseline:", len(bars), "bars", flush=True)
    result = run(strategy, bars)
    summary = metrics.summary(result)
    trades = metrics.trade_frame(result)
    trades.to_csv(out / "trades.csv", index=False)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False))
    signal_rows = []
    for entries in strategy.signals.values():
        for signal in entries:
            row = asdict(signal)
            row["time"] = str(bars.ts[signal.bar])
            row["structure_time"] = str(bars.ts[signal.structure_bar])
            row["stop_time"] = str(bars.ts[signal.stop_bar])
            signal_rows.append(row)
    pd.DataFrame(signal_rows).to_csv(out / "signals.csv", index=False)
    setup_rows = []
    for setup in strategy.setups:
        row = asdict(setup)
        for field in ("origin", "touch", "ready", "end", "first_signal"):
            i = row[field]
            row[f"{field}_time"] = str(bars.ts[i]) if i is not None and i < len(bars) else None
        setup_rows.append(row)
    pd.DataFrame(setup_rows).to_csv(out / "setups.csv", index=False)
    actions = pd.DataFrame(strategy.actions, columns=["bar", "action", "signal_bar", "reason"])
    actions.to_csv(out / "orders.csv", index=False)
    metrics.by_year(trades).to_csv(out / "years.csv", index=False)
    report.equity_png({0: result}, out / "equity.png", title + " — fixed 1H / 15m baseline, through 2023")
    files = ["strategies/failed_swing_point.py", "tvtester/swings.py", "indicators/structure_swings.pine",
             "tvtester/engine.py", "tvtester/metrics.py", "tvtester/config.py", "tvtester/fsp_clock.py", "tools/run_fsp.py"]
    provenance = {"parameters": strategy.params, "source_sha256": {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}, "data_sha256": {}}
    for year in sorted(set(bars.ts.year)):
        path = ROOT / "data" / "cl1" / f"year={year}.parquet"
        digest = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        provenance["data_sha256"][path.name] = digest.hexdigest()
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2))
    placed = actions[actions.action == "place"]
    counts = {"bars": len(bars), "setups": len(strategy.setups), "eligible_signal_bars": len(strategy.signals),
              "orders_placed": len(placed), "unfilled_orders_cancelled": int((actions.action == "cancel").sum()),
              "pending_at_end": strategy.pending is not None,
              "halt_reopen_exits": sum(t.exit_id == "New York halt reopen" for t in result.trades),
              "nonpositive_initial_risk_closed_trades": sum(t.initial_risk_ticks is None for t in result.trades)}
    (out / "counts.json").write_text(json.dumps(counts, indent=2))
    text = [f"# {title} — Failed Swing Point: fixed default baseline", "",
            "[Strategy specification](README.md). One fixed configuration; no parameter search or 30m comparison.", "",
            f"Data: **{bars.ts[0]} to {bars.ts[-1]}**, {len(bars):,} one-minute CL bars. End is exclusive {a.end} UTC.",
            "", "Settings: provisional 1H swings, 15m confirmation, both directions, New York entries 09:00–14:30 ET; one CL contract; "
            "maximum planned stop distance 25 ticks; TP 50 ticks from actual fill; $2.01/order; no added slippage.",
            "", "Each failed 1H setup is eligible only at its first valid 1m MSS. At most one limit order "
            "per setup; no replacement attempt after cancellation, TP or SL. Busy-account signals are not deferred.",
            "", "MSS eligibility ends on a post-confirmation touch of the breach candle's fixed 15m high (short) "
            "or low (long), including a touch within the signal minute before its close. Already-placed limits "
            "are unaffected by that boundary or by later 1H points. Pending limits cancel at New York entry-session end; "
            "New York close at 14:30 ET (or the earlier scheduled exchange close) cancels limits, "
            "flattens all positions and clears all setups. A new failed setup is required after reset. Roll exits apply.",
            "", "Halt exception: if the scheduled cutoff has no tradable closing minute, cancel old orders "
            "and close the position at the OPEN of the first available reopening bar. Normal SL/TP fills "
            "before the cutoff remain valid. No price is backdated or fabricated.",
            "", "## Results", "", report.full_report(summary, trades), "", "## By year", "", report.by_year(trades),
            "", "## Audit counts", "", "```json", json.dumps(counts, indent=2), "```", "",
            "## Last trades", "", report.trade_list(trades), "", "## Artifacts", ""]
    for name in ("trades.csv", "summary.json", "years.csv", "setups.csv", "signals.csv", "orders.csv",
                 "provenance.json", "counts.json", "equity.png"):
        text.append(f"- [{name}]({report.rel(out / name, doc.parent)})")
    text += ["", "This historical baseline is not out-of-sample validation. Tick-level fills and TradingView export "
             "parity are not established. An end-of-period open position is reported as open P&L, not force-closed.", ""]
    doc.write_text("\n".join(text))
    status.update(status="complete", finished_utc=datetime.now(timezone.utc).isoformat(), report=str(doc))
    (out / "status.json").write_text(json.dumps(status, indent=2))
    print(json.dumps({"report": str(doc), "all": summary["all"],
                      "max_drawdown": summary["max_equity_drawdown"], "counts": counts}, indent=2), flush=True)


if __name__ == "__main__":
    main()
