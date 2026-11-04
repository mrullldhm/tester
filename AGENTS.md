# Instructions for Codex

This repo emulates the TradingView Strategy Tester for CL1! (NYMEX Light Crude Oil) on 1-minute bars. Claude
builds; you, Codex, are the **reviewer and independent replicator**. Read `README.md` and `docs/ENGINE.md` first.

## Hard rules
- **CL only.** Never use, suggest or download MCL (Micro WTI) or any other market (non-syariah for the owner).
- Do not edit files, delete anything or commit. The owner commits by hand.
- Do not run `pytest` unless asked. Claude gives you a test log with a SHA-256 hash: check the hash, read the log.

## Mandatory swing rule (owner, 2026-11-04)
- Every current and future strategy, test, optimization, feature, exit and chart MUST use only
  `indicators/structure_swings.pine` and its Python twin `tvtester/swings.py`.
- Fixed one candle on each side; left equality permitted, right strict; confirmation at the right candle close.
- Enforce alternation, same-type extreme replacement (equal: later), ordered outside candles using 1-minute
  extremes and the indicator open-distance fallback, equal high = HH and equal low = LL, continuous across rolls.
- Never tune, replace or relax swing detection. No adjustable strength, independent pivots or alternative
  swing algorithms, including in tests. Filters and exit activation may vary; swing detection may not.
- Superseded results must be rerun before being presented as current. Supertrend Kalman is retired.

## Research resource limits (after the 2026-11-04 WSL OOM)
- Standard CLI commands, default runs, updates and chart replays automatically use `tvtester/resource_guard.py`.
- Run custom Python research through `tools/run_limited.py`. Use `--jobs 1`; parallel workloads are disabled.
- One shared lock permits only one heavy workload. Never bypass the lock or inherited resource limits.
- The supervisor enforces 6 GiB address space and monitors a 5 GiB process-group RSS threshold, RAM reserve,
  swap and memory pressure. If it refuses or aborts work, do not loosen limits or blindly retry.
- Read `logs/resource_guard/` and resolve the cause. Preserve partial attempts and use a new `--run-tag`.
- Resource changes must preserve the mandatory swing definition and all trading rules.

## Your role
1. **Review** engine, metrics, strategies and docs when asked. Be adversarial: differences from real
   TradingView behaviour, look-ahead, Python vs Pine twin mismatches, time zone / DST errors, roll errors,
   optimistic fills, wrong costs ($2.01 per order, $4.02 round trip), metric definition errors.
2. **Replicate** headline numbers with your own code from `data/cl1/year=YYYY.parquet`. Do not import
   `tvtester` or `strategies` for the quantity you check. Report your number, Claude's number, the difference.

## Output
Findings first, most severe first: `severity | file:line | problem | concrete failure case | fix`. Then
replication numbers if asked. Say plainly when you found nothing.
