# Round 3 independent dev audit

All results are dev (2010-06..2021-12), in-sample, selected after a best-of-1,728 screen. No validation/holdout reads. No strategy, engine, screen, ledger or specification changes.

Reproduce from repo root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python studies/cbr/codex/round3.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python studies/cbr/codex/round3_null.py
```

The first script always rebuilds strategy signals, asserts trades/net equal the screened row, saves trade paths and a plain CSV, checks five trades against raw minute bars, bootstraps daily returns (including all inactive trading days), and evaluates fixed sizes 1..5 using actual engine paths. Seeds are fixed. Source file SHA256 values are recorded in the summary. The large RTH bars pickle is a removable temporary cache; the null script recreates bars from dev if absent.

The null moves each original signal day's entire order schedule to a randomly chosen dev date **in the same calendar year**, without replacement within each year. It preserves exact CT signal minutes, sides, integer tick offsets of entry/stop/target/kill from the known signal close, and expiry (including original newer-order cancellation). There are 1,043 orders across 927 original signal days. Candidate destination days must contain all 60 possible signal minutes; 2,934 qualify. Trades remain conditional on engine fills and one attempt per day; no pattern features are recomputed on destination dates. Preserve all original orders rather than condition on observed successful fills. Planned brackets are 2R; realized R can change with gaps/flattening. The compact bar replay is asserted identical to the full-bar original trade list before any randomization.

This is a conditional, descriptive randomization control. It matches year but not local volatility or within-year trend regime; it tests this schedule's excess over arbitrary RTH dates, not a pure causal contribution of type-3 structure. It does not estimate the null distribution of the maximum of all 1,728 strategies. The nominal Monte Carlo p-value and bootstrap intervals are not selection-adjusted. Rolling Combine starts overlap and are not independent experiments. Sizing sensitivity adds five exploratory variants and does not amend the original one-contract screen.

Bootstrap: 10,000 circular moving-block resamples each at 1, 5 and 20 consecutive trading days, resampled to the original number of days. These percentile intervals describe fixed-version sampling stability, conditional on the selection and on historical dev regimes. Resampling does not simulate future slippage, structural change, or the full research search.

Spot checks: deterministic first and last target, first and last stop, and largest absolute gross result. Assert no earlier fill/kill, entry price consistency, no earlier bracket exit, and recorded terminal stop/target price. Raw entry/exit OHLC, signal OHLC, raw contract and timestamps are retained in round3_spotchecks.json. OHLC verifies compatibility with the engine's stated intrabar assumptions; it cannot establish actual queue fills or tick ordering.
