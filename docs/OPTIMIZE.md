# Optimize (feature 2): feature engineering and parameter search

> **Execution update — 3 November 2026.** New runs use limit entries and commission only, with no
> added slippage and no 1- or 2-tick stress scenarios. Fair Price Reversal and Supertrend + Kalman place
> the limit at the signal/decision close, active from the next bar. A waiting entry is cancelled when
> the planned TP has been reached and it is still unfilled at the one-minute close. Existing session
> boundaries still cancel waiting orders; Tupa Trade retains its stop-limit trigger and swing invalidation.
> Limit fills can be at the limit or better. Stops and forced closes retain their existing order types.
> Historical reports, configurations and ledger entries are retained; they are not results of these new rules.


Feature 1 (`cli test`) answers "does this idea work?". Feature 2 answers "do filters or other parameters make it
better, and how many tries did it take to find that?". Every look at results costs credibility, so this feature
records each try in a ledger that the later validation feature (walk-forward / out-of-sample) will need.

Reviewed with Codex before and after it was built (`docs/REVIEWS.md`, R4 and R5).

## Rules
| Rule | Value |
|---|---|
| Development interval | bars with ts < **2024-01-01 00:00 UTC** (exclusive). `tvtester/experiment.py` holds it; `features`, `search` and `replay` all use it and cannot read later bars. `cli test` (feature 1) still reads every bar: it is never used to judge a feature-2 change |
| 2024-01-01 onward | **Previously exposed** (feature 1 picked its top combinations on data to October 2026), so it is not clean out-of-sample data. It is reserved from further development. Bars after the protocol freeze (2026-10-31) are the only data never looked at |
| Costs | Same Properties as feature 1: $2.01 per order, 1 contract; no added slippage; one baseline engine run |
| Objective | Declared before a search starts, never changed after looking. `net0` = net profit **plus open P&L of a position still open at the end** (so a losing open trade cannot hide) without added slippage. `net0` is the owner's feature-1 rule. Ties: profit factor (no losing trade ranks above any number), then trial number |
| Minimum trades | A trial with fewer than 300 closed trades in the objective scenario is not eligible and cannot win. If no trial is eligible the report says "no eligible trial" and nothing is frozen |
| Budget accounting | Trials = configurations tried, the baseline (trial 0) and TPE duplicates included. Engine runs = 1 per unique configuration plus 1 per neighbour; the ledger counts engine runs. A failed trial stops the search (a bug, never a result) |
| Wording | Every optimized number is "in-sample, best of N evaluations, development interval". Nothing here shows a tradable edge |
| Ledger | `results/<strategy>/ledger.jsonl`, append only: every association report, search, neighbour check and replay with its number of engine evaluations |

## Filters
A filter vetoes an entry; it never changes the signal logic or any feature value. Raw signal state is kept, so the
Pine twin needs no re-arming rule; what a vetoed signal does is the strategy's own signal rule, the same in both twins:
fair_price_reversal: it still uses up that session day's long (or short) signal, exactly as if it had been taken;
supertrend_kalman: the M15 event expires like any untaken event (events are never carried to a later bar).
The veto is checked at the entry decision in `on_bar` (the engine also calls `on_bar` while a position is open,
so a mask in `prepare` alone would not stop an entry on the bar a position closes). With no filters the strategy
is the feature-1 strategy, trade for trade (test).

A filter is `(feature, op, threshold)` with `op` `min` (value >= threshold) or `max` (value <= threshold). A NaN
feature value fails an enabled filter.

## Feature contracts (fair_price_reversal)
All values are known at the close of the signal bar, from that bar and earlier bars only. Tests: a literal
bar-by-bar Pine-style transcription, prefix invariance (values on a prefix equal the full-run values) and future
perturbation (changing later bars does not change earlier values), on 2024-02-20 .. 2024-04-15 (US / UK DST
changes). Note: those tests use bars after the development cutoff only to check code, never results.

| Feature | Units | Definition at signal bar i | Available | Warm-up / missing | Pine |
|---|---|---|---|---|---|
| `minutes_from_open` | minutes | local minute of bar i's open - session open minute | bar i close | none | `minuteOfDay - openMinute` |
| `anchor_body_atr` | ATR | (body upper - body lower) / ATR(atr_len)[1] at the anchor bar that set the current body (the strategy's own ATR, 14) | anchor close | NaN if ATR na or 0 | stored at the anchor reset |
| `risk_ticks` | ticks | abs(close[i] - stop) where stop is the frozen excursion extreme (strategy stop) | bar i close | none | `math.abs(close - stop) / syminfo.mintick` |
| `risk_atr` | ATR | abs(close[i] - stop) / ATR(atr_len)[1] at bar i | bar i close | NaN if ATR na or 0 | `riskTicks * syminfo.mintick / moveAtr` |
| `range_ratio` | ratio | at the anchor bar a: R_a = highest(high, 1380)[1] - lowest(low, 1380)[1] (the 1,380 bars before the anchor, about one 23-hour CL trading day); value = R_a / mean of the previous 20 valid R values (compared first, then R_a is pushed) | anchor close | NaN while fewer than 1,380 bars precede the anchor (that reset is not stored) or fewer than 20 valid earlier R; NaN if the mean is not positive | `ta.highest` / `ta.lowest` with `[1]` at **global scope on every bar**, sampled inside the reset; `var` array of the last 20 |

The anchor values carry forward like Pine `var` (a day without its anchor bar keeps the previous body and its
features, as the signal logic does). Ratios use tick units in Python and price units in Pine (same ratio); a value
exactly on a threshold can differ by float rounding.

Descriptive only (association report, no filter): direction, local weekday.

Deferred (look-ahead or definition problems found in R4): higher-timeframe trend, settlement gap, EIA calendar,
roll week, session-open relative volume.

## Feature contracts (supertrend_kalman)
Values at the decision bar i = the first 1m bar of the bucket after the completed M15 bucket k (`prev[i]`; the
decision is at bar i's close, the fill at the next open). Every M15 value is from bucket k or earlier; the Pine twin
reads them through `request.security(.., "15", expr[1], lookahead_on)`. Defined only at **structurally eligible**
signals (signal on bucket k, inside the variant's hours, swing stop beyond the close, base `vol` filter passed),
whatever the position, filters or slippage; NaN elsewhere. Tests (`tests/test_supertrend_kalman_f2.py`): a literal
bar-by-bar transcription with its own ATR, swing pivots and ER, prefix invariance (prefix ending inside an M15
bucket), future perturbation, a window with the US and UK DST changes and a contract roll (2023-03 .. 2023-05,
code check only), and no filters = feature 1 trade for trade in all four variants.

| Feature | Units | Definition at decision bar i | Available | Warm-up / missing | Pine |
|---|---|---|---|---|---|
| `risk_ticks` | ticks | abs(close[i] - stop), stop = last confirmed strict M15 swing low (long) / high (short) at k, `swing` buckets each side | bar i close | NaN when no swing level exists or it is not beyond the close (no trade then) | `math.round(math.abs(close - lvl) / syminfo.mintick)` |
| `risk_atr` | ATR | risk_ticks / ATR14 of M15 bucket k, in ticks | bar i close | NaN while ATR14 is na (first 14 buckets) or 0 | `riskT / (a14B / syminfo.mintick)` |
| `atr_ratio` | ratio | ATR14 / ATR100 of M15 bucket k | bucket k close | NaN while ATR100 is na (first 100 buckets) or 0 | `a14B / a100B` |
| `er` | 0 .. 1 | abs(c[k] - c[k-20]) / sum of abs(c[j] - c[j-1]), j = k-19 .. k, M15 closes | bucket k close | NaN for k < 20 and when the sum is 0 (Pine x / 0 = na) | `math.abs(close - close[20]) / math.sum(math.abs(ta.change(close)), 20)` inside `m15()`, returned `[1]` |
| `hours_since_open` | hours | `((NY minute of day of bar i's open - 1080) mod 1440) // 60`, always the New York clock | bar i open | none | `math.floor(((nyMinute - 18 * 60 + 1440) % 1440) / 60)` |
| `rvi_side` | 0 .. 100 | TradingView RVI(10, 14) of bucket k for a long, 100 - RVI for a short | bucket k close | NaN while RVI is na | `sigB == 1 ? rviB : 100 - rviB` |

Python works in ticks, Pine in price; every feature is a ratio of the two or an integer tick count, so the values
are the same, but a value exactly on a threshold can differ by float rounding. The association report's weekday
uses the strategy's `report_tz` (New York here; each session's own zone for fair_price_reversal).


## Where the results are
One folder per strategy holds every readable feature-2 document: `docs/strategies/<strategy>/optimize/`.

| File | Written by |
|---|---|
| `README.md` | the lab notebook: hypotheses, budgets, results, verdict (hand-written) |
| `features_<variant>.md` | `features` |
| `search_<run_id>.md` | `search` (baseline vs winner, neighbours, top 20) |
| `winner_<config>.md` + `.png` | `replay` (full TradingView-style report of a frozen winner) |

`results/<strategy>/` holds only raw data (CSV, JSON, the ledger) for scripts and replication.

## Commands
```bash
.venv/bin/python -m tvtester.cli features fair_price_reversal --variant ny            # association report
.venv/bin/python -m tvtester.cli search fair_price_reversal --variant ny --space filters \
    --sampler random --trials 200 --objective net1 --seed 1 --jobs 4                   # search
.venv/bin/python -m tvtester.cli replay strategies/configs/<file>.json                 # frozen winner
```

### Association report (`features`)
Runs the baseline configuration (the feature-1 top combination of the variant) on the development interval at
0 and 1 tick (separate engine runs), joins each trade to its feature values at its **signal bar** (stored on the
trade), and buckets each feature: quintiles of the trades' own values for continuous features, groups for
categorical ones. Per bucket: trades, % profitable, average trade, net profit, and a 90% interval of the average
trade from a block bootstrap by ISO week (2,000 resamples). The intervals are not adjusted for picking the largest
spread: the report is exploratory, and a filter's real effect is only known from an engine run (removing a trade
can let in another trade the baseline never took).

### Search (`search`)
- The strategy module declares `SPACES` (`filters`: base parameters frozen at the baseline, filters searched;
  `full`: base parameters and filters). Per feature: mode `off` / `min` / `max`, and a threshold only when the mode
  is not `off` (canonical: a disabled filter has no threshold, so duplicates are found and evaluated once).
- `random`: all N configurations are drawn up front from the seed, then evaluated in parallel: same seed, same
  trials, whatever `--jobs` is. `tpe`: Optuna TPE (pinned `optuna==4.9.0`, multivariate, constant liar) driven by
  ask / tell in one process: it asks `--jobs` suggestions, evaluates the new ones in parallel, and tells the results
  back in order. The budget is exact, a configuration already evaluated (or repeated in the same batch) is reused
  and marked `duplicate`, and the same seed and `--jobs` give the same trials. The journal file is a record only.
- A search id (variant, space, sampler, objective, seed, trials) is used once. An interrupted search is not
  resumed. Ledger first, engine after: every batch of trials and the neighbour batch is logged (`search_batch`, its
  engine runs) **before** it runs, and `features` and `replay` log before running, so an interruption over-counts
  engine runs, never under-counts. `evaluations.jsonl` keeps the results as batches finish; the final `search`
  event carries the summary (`engine_runs`) and adds no count of its own.
- The no-filter baseline is always trial 0.
- `grid`: every combination of the declared parameter lists (parameters only, no filters), minus the space's
  declared `exclude` entries (configurations that behave identically to another). `--trials` must equal the
  grid size; the budget is never truncated or padded. Trial 0 is the baseline. Excluded configurations are also
  skipped as neighbours.
- Every trial runs the baseline only; all headline numbers are kept in `results/<strategy>/search/<run_id>/trials.csv`
  (one writer) with `run.json` (space, sampler, seed, objective, interval, code / data hashes, versions).
- Neighbours of the winner: each searched base parameter one step either way in its declared list (categorical:
  every other value), each enabled filter switched off and its threshold one step either way. They are diagnostics,
  never candidates, even when one beats the winner; same objective and trade minimum shown. Counted in the ledger.
- Resources: one worker peaks at about 1.6 GB (development bars + caches; caches are keyed by the few indicator
  settings, so they stay bounded). 4 workers on this 14 GB machine. One parallel layer (joblib processes).

### Replay (`replay`)
A frozen configuration (`strategies/configs/*.json`: strategy, variant, every parameter, filters, interval, source
run and trial) runs the baseline without any grid, and writes raw files to `results/<strategy>/replay/<name>/`
and its report to `docs/strategies/<strategy>/optimize/winner_<name>.md`. It never touches the feature-1 document.

## Agent loop
1. Hypothesis, written in the lab notebook `docs/strategies/<strategy>/optimize/README.md` before running anything.
2. Association report. 3. Feature code + tests (if a new feature is needed). 4. Search with a declared budget and
objective. 5. Winner, neighbours, slippage scenarios. 6. Verdict in the lab notebook. 7. Freeze the winner; Codex
reviews and replicates it before it is called real.

## Execution revision and historical configurations

New frozen configurations carry `execution_version: limit-close-tp-expiry-v1` and objective `net0`.
Replay and validation refuse older configurations before loading data or writing results. Historical `net1`
searches stay in the ledger and count as previous research; do not relabel them as new limit-entry searches.
A fresh search is required for selection under the new rules.
