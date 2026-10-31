# Supertrend + Kalman M15: feature 2 (optimize) results

**Start here.** Verdict at the bottom (when the runs are done). The feature-1 result is [`../README.md`](../README.md).

Lab notebook (docs/OPTIMIZE.md, "Agent loop"). Hypotheses and budgets are written **before** the runs they
describe. Every run is in `results/supertrend_kalman/ledger.jsonl`. All numbers are in-sample, development
interval (bars before 2024-01-01 UTC).

## Protocol declared 2026-10-31, before any feature-2 run
- **Prior exposure.** Feature 1 picked each variant's top combination from 1,728 grid combinations per variant
  (6,912 in all) on 2010-06 .. 2026-10, so the baselines already saw the reserved interval (ledger lineage line).
  Feature 1 found no tradable edge: every top loses at 2 ticks; `all`, London and NY are above zero at 1 tick,
  Asia is not.
  Feature 2 asks one question: does a point-in-time entry filter make a baseline survive 1 tick on the
  development interval? A "no" is an acceptable answer.
- **Baselines** (`BASELINES` in the strategy) = the feature-1 top combination of each variant:

| Variant | trigger | vol | exit | rr | swing | trail_mult | st_factor | kalman_q |
|---|---|---|---|---|---|---|---|---|
| all | both | atr_ratio:1.3 | fixed | 3 | 3 | 1 | 3 | 0.0001 |
| asia | trail | none | trail | 3 | 3 | 2 | 3 | 0.01 |
| london | both | stop_atr:3 | trail | 2 | 5 | 2 | 3 | 0.0001 |
| ny | both | rvi | flip | 3 | 5 | 1 | 2 | 0.0001 |

- **Objective** `net1` (net profit + open P&L at 1 tick), at least 300 closed trades at 1 tick. Same reason as
  fair_price_reversal: a 0-tick objective rewards edges smaller than one tick per fill.
- **Budget** (trials per variant; each trial = 3 engine runs at 0 / 1 / 2 ticks; neighbours extra):

| Step | What | Sampler | Trials per variant | Seed |
|---|---|---|---|---|
| E1 | Association report, all / asia / london / ny | none | 2 engine runs | 0 |
| E2 | `filters` space: baseline parameters frozen, filters searched | random (reproducible) | 200 | 1 |
| E3 | `full` space: the feature-1 grid + filters | TPE, 4 jobs (same seed + jobs + versions = same trials) | 300 | 1 |

  Nothing beyond this budget is run without a new dated entry here first. **Amendment 2026-10-31, before any E3 run:** E3 uses
  `--jobs 2` for asia / london / ny and `--jobs 4` for `all` (RAM: two 4-worker searches do not fit in 14 GB).
  Only the TPE batch size changes; seed, trials and objective stay as declared. Filter ranges below are declared from
  the strategy's mechanics, before any feature value or trade was looked at. Total: 2,000 search trials (about
  6,000 engine runs) plus neighbours, on top of the 6,912 feature-1 configurations; every reported number is the
  best of all of them, not of one search.
- **Candidate rule (declared before E1).** A search winner is a candidate for feature-3 validation only if all
  hold on the development interval: eligible (300+ trades at 1 tick); net profit above zero at 1 **and** 2 ticks;
  at least two thirds of its neighbours above zero at 1 tick (plateau); no single calendar year above 50% of its
  1-tick net profit. E2 and E3 winners of a variant are judged separately by the same rule; if both pass, the
  one with fewer changes from the baseline goes forward (fewer degrees of freedom), the other is reported only.
  Neighbours and association intervals are diagnostics, never a reason to pick a different configuration.

## Features (all at the decision bar i, the first 1m bar of the bucket after the completed M15 bucket k)
| Feature | Units | Definition | Filter range (lo, hi, step) |
|---|---|---|---|
| `risk_ticks` | ticks | abs(close[i] - stop), stop = last confirmed M15 swing low (long) / high (short) at k | 10 .. 200, 5 |
| `risk_atr` | ATR | risk_ticks / ATR14(M15)[k] (ticks) | 0.5 .. 5.0, 0.25 |
| `atr_ratio` | ratio | ATR14 / ATR100 (M15)[k] | 0.6 .. 2.0, 0.1 |
| `er` | 0..1 | Kaufman efficiency ratio of M15 closes over 20 buckets at k: abs(c[k] - c[k-20]) / sum of abs(c[j] - c[j-1]), j = k-19..k. NaN until 21 buckets exist and when the sum is 0 (Pine: x / 0 = na) | 0.05 .. 0.8, 0.05 |
| `hours_since_open` | hours | `((NY minute of day of bar i's open - 1080) mod 1440) // 60`: whole hours since 18:00 New York (CME Globex day open), 0 .. 23, always the New York clock whatever the variant | 0 .. 23, 1 |
| `rvi_side` | 0..100 | RVI(10, 14)[k] for a long, 100 - RVI for a short (above 50 = volatility on the trade side) | 30 .. 80, 5 |

Every structurally eligible signal gets a value (signal, in hours, stop beyond the close, base `vol` filter
passed), **whatever the position**: position state depends on filters and slippage, so it never decides a feature
value. Other bars are NaN. Flatness and the filter are checked only at entry, inside the flat branch of `on_bar`
(a filter can never block an exit). A vetoed event expires (M15 events are never carried to a later bar, R6),
so no re-arming rule. NaN fails an enabled filter. Pine twin: the same values from `request.security` (ER inside
the M15 context, `er[1]`).

## Hypotheses (written before E1)
- **H1 risk size (cost).** At 1 tick a trade pays 10 USD slippage on the market entry and 10 USD more if it exits
  by stop or market close (a limit target never slips), plus 4.02 USD commission, whatever the stop size. So
  trades with a small `risk_ticks` lose most of their edge to costs. A `risk_ticks` minimum helps net1. Prior:
  strong (it held for fair_price_reversal).
- **H2 chop.** Trend entries in choppy markets (low `er`) do worse. A minimum `er` helps.
- **H3 regime.** `atr_ratio` matters, direction unknown (weak prior). `all` and `london` baselines already cap it
  or the stop width, so little room is expected there.
- **H4 time of day.** Entries in thin hours do worse in `all`. One bound per filter, so the two tails are
  separate tests: `hours_since_open >= X` drops the early Globex evening, `<= X` drops the hours before the halt
  (both together only if the search picks both).
- **H5 RVI side.** Weak prior; NY's baseline already uses RVI > 50 on the trade side.

## Results

### E1: association reports (2026-10-31)
[`features_all.md`](features_all.md), [`features_asia.md`](features_asia.md),
[`features_london.md`](features_london.md), [`features_ny.md`](features_ny.md). Development-interval baselines at
1 tick: `all` 3,716 trades +30,412; `asia` 979 trades -3,496; `london` 590 trades +6,258; `ny` 2,628 trades +53,025.
- **H1 partly supported.** Asia and London: the smallest-`risk_ticks` quintile loses (Asia 1-21 ticks -21.42 USD a
  trade, interval below zero; London 3-23 ticks -20.05). `all`: the widest quintile (76+ ticks) holds the whole
  profit (+102,237 of +30,412). NY: no clear order.
- **H2 (chop) not supported.** `er` buckets are not monotonic in any variant (NY's lowest-ER bucket is its best).
- **H3, H5: no pattern** beyond noise; the buckets jump up and down.
- **H4:** no consistent time-of-day shape in `all`; London 10-11 h (about 04:00-05:00 New York) and NY 16-17 h
  look good, but these are single buckets out of many, not adjusted for picking.
- `all` shorts made money and longs lost (+58,427 / -28,016), also in NY. Descriptive only, not a filter.
- **Audit note (2026-10-31, after E1-E3 had run):** the E1 reports' `weekday` buckets are on the **UTC** clock
  (the association code took the time zone from fair_price_reversal's session object; now each strategy declares
  `report_tz`, New York here). Weekday is descriptive only: no filter or search used it, so no result changes.
  The reports were not regenerated (that would be 8 more engine runs for a label).

### E2: filters only, random, 200 trials per variant, objective `net1` (2026-10-31)
| Variant | Winner | Net 0 / 1 / 2 ticks | Trades (1) | Baseline 0 / 1 / 2 ticks | Neighbours above 0 (1 tick) | Largest year (1 tick) | Rule |
|---|---|---|---|---|---|---|---|
| all | `risk_ticks >= 100` | +137,285 / +122,375 / +109,195 | 546 | +91,453 / +30,412 / -34,756 | 3 of 3 | 2022: 53.5% | **fails** (year) |
| ny | `rvi_side >= 55` | +104,217 / +60,457 / +16,487 | 2,247 | +104,105 / +53,025 / +1,955 | 3 of 3 | 2022: 32.4% | **passes** |
| london | `risk_atr >= 1.5`, `rvi_side <= 75` (+ `hours_since_open <= 21`, no effect in London) | +20,149 / +9,689 / -951 | 535 | +17,638 / +6,258 / -5,302 | 9 of 9 | not needed | fails (2 ticks) |
| asia | `er >= 0.1`, `risk_atr <= 3`, `risk_ticks <= 90` | +8,559 / +1,539 / -5,481 | 356 | +15,844 / -3,496 / -22,836 | 6 of 9 | not needed | fails (2 ticks, neighbours) |

Reports: `search_<variant>_filters_random_net1_s1_n200.md`; replays of the rule checks: `winner_*.md`.

**Reading.**
- **`all`: H1 in its strongest form, and still rejected.** A 100-tick (1.00 USD) minimum stop keeps 546 of 3,716
  trades and turns -34,756 at 2 ticks into +109,195. The cost mechanism is the declared one. But 134 of the 546
  trades and 53.5% of the 1-tick profit are 2022, 2017 has 5 trades: a fixed tick threshold is a volatility-regime
  switch (as for fair_price_reversal). The declared year rule rejects it. Not a candidate.
- **`ny`: a small step.** The baseline already makes money at 1 and (barely) 2 ticks on the development interval
  (the feature-1 top was picked on 2010-2026, so this is not news). The winner only raises the baseline's own RVI
  threshold from 50 to 55; neighbours 50 / 60 give +53,025 / +21,375 at 1 tick. It passes every declared rule.
- London and Asia: still no edge at 2 ticks.

### E3: feature-1 grid + filters, TPE, 300 trials per variant, objective `net1` (2026-10-31)
| Variant | Winner | Net 0 / 1 / 2 ticks | Trades (1) | Neighbours above 0 (1 tick) | Largest year (1 tick) | Rule |
|---|---|---|---|---|---|---|
| ny | `risk_atr >= 2` (+ `hours_since_open >= 1`, no effect in NY) | +109,927 / +62,427 / +14,937 | 2,426 | 18 of 20 | 2022: 45.1% | passes; not taken forward (tie rule) |
| london | `st_factor=2`, `trigger=trail`, 4 filters | +17,530 / +9,020 / +470 | 485 | 16 of 24 (exactly 2/3) | 2022: 65.0% | **fails** (year) |
| asia | `kalman_q=0.0001`, `rr=2`, `swing=5`, 4 filters | +12,565 / +5,865 / -835 | 342 | 20 of 26 | not needed | fails (2 ticks) |
| all | `swing=5`, `trigger=trail`, `atr_ratio >= 1.1`, `hours_since_open >= 8`, `risk_atr >= 1`, `risk_ticks >= 25` | +118,333 / +104,967 / +90,347 | 942 | 21 of 26 | 2022: 92.7% | **fails** (year) |

**Reading.** `all` E3 looks like the best result of the whole study (+90,347 at 2 ticks) and is the clearest
failure: 2022 alone is +97,256 of +104,967 (92.7%), 7 of 14 years lose. Two changed settings and four filters fitted
the 2022 crude spike. NY E3 passes too, but the declared tie rule sends the configuration with fewer changes forward:
E2 (one filter) over E3 (two filters, one of them inert). It is reported, not validated. The NY E2 and E3 winners
filter different things (RVI side vs stop width in ATR) and land within 2,000 USD of each other at 1 tick: the
NY baseline itself carries the result; neither filter adds much.

### Independent replication (Codex R10, 2026-10-31)
Codex rebuilt the NY E2 candidate from the 2010-2023 parquet files with its own code, before opening the trade
lists: 2,247 trades, +104,217.06 USD at 0 ticks and +60,457.06 USD at 1 tick, every trade matched (signal bar,
times, prices, profit, exit reason). It flagged that NY has 10 owner-rule roll exits the Pine twin does not do
(now documented in the twin).

## Verdict (feature 2, 2026-10-31)
- **One candidate for validation: NY E2** (baseline + `rvi_side >= 55`). On the development interval: +104,217 /
  +60,457 / +16,487 USD at 0 / 1 / 2 ticks, 2,247 trades, 3 of 3 neighbours above zero, largest year 32%.
  Codex replicated it trade for trade (R10). It is a small step from a baseline that already made money at 1 tick
  before 2024, and that baseline was itself picked on 2010-2026 data.
- **Rejected by the rules declared before E1:** both `all` winners (2022 = 53.5% and 92.7% of profit), London
  (loses at 2 ticks, or 2022 = 65%), Asia (loses at 2 ticks in both searches), NY E3 (passes, but the tie rule
  sends the simpler E2 forward).
- **H1 (stop size) is real and is a volatility-regime effect**, as for fair_price_reversal: wide stops in ticks
  come with volatile years. A tick threshold should not be trusted without out-of-sample data.
- **Count against the candidate:** 6,912 feature-1 configurations, then 2,000 feature-2 trials and their
  neighbours (ledger: every engine run, including 53 code-check runs). Everything above is in-sample, best of N.
- **Next:** feature 3 (validation A, development interval only) on NY E2 only,
  [`../validate/README.md`](../validate/README.md). The reserved 2024+ data is feature 5 (roadmap renumbered
  2026-11-01). Not checked on TradingView yet:
  the Pine twin has the filters, but compiling and matching it on NYMEX:CL1! 1m is the owner's step.
