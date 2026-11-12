# Price Reversal v2: feature-2 / feature-3 lab notebook

## Protocol (declared 2026-11-12, before any v2 feature-1 result was read)

Written while the first `cli test price_reversal_v2` run was still in progress; no v2 grid, trade or summary file
had been opened. The owner asked to run features 2-5 "if it passes the requirement".

### Gate from feature 1 to feature 2 (hour anchors h01..h23)
An hour advances only if **both** hold on its feature-1 grid (all bars, 0 ticks, commission included):
1. the **median net profit of its 64 grid settings is > 0** (the whole grid, not the best setting), and
2. its top setting has **at least 300 closed trades before 2024-01-01** (the feature-2 minimum).

At most **3 hours** advance: the qualifying hours with the highest grid median. Hours are not re-ranked after any
feature-2 run. The hour selection itself is a look at 23 x 64 = 1,472 settings on all bars (2024+ included) and is
disclosed with every later number.

### Gate for the entry cap / fixed TP (entry_asia, entry_london, entry_ny)
A cap / TP setting advances for a session only if, against `entry_cap = 0, tp_mode = default` on the same
baseline, it has **higher net at 2 ticks slippage and a higher net / max drawdown ratio** (all bars). At most one
setting per session advances (highest net / max DD among qualifiers). These sessions' earlier FPR filter
candidates failed feature 3; a capped variant is a new idea with its own budget, not a rescue of those candidates.

### Feature 2 for each advancing variant (development interval < 2024-01-01 only)
- Baseline = the variant's feature-1 top combination (with the advancing cap / TP for entry variants).
- Hypothesis: a single entry filter from the declared feature set raises net0 without dropping below 300 trades.
- Objective `net0`; space `filters`; sampler `random`; seed 1; **200 trials**; minimum 300 trades. Budget per
  variant: 2 association runs + 200 trials + neighbours + 1 replay, all in `results/price_reversal_v2/ledger.jsonl`.
- No `full` (TPE) search, no second seed, no re-run after looking.

### Feature 3
Every frozen feature-2 winner runs `cli validate` unchanged (docs/VALIDATE.md): anchored walk-forward sum > 0,
>= 7/10 positive folds, PBO <= 0.5, DSR >= 0.95 (N = 200). Fail = stop; no substitution.

### Features 4 and 5
Not built in this repository (2026-11-12): the Topstep 50K layer has open owner decisions (quantity exception,
daily loss limit on/off, horizon, Standard vs Static) and feature 5 needs a frozen strategy + prop policy. A
candidate that passes feature 3 waits for them; nothing is run on the reserved interval.

## Results
(Filled in after the runs, below this line.)

### Gate outcome (2026-11-12, after feature 1; numbers in [../study.md](../study.md))

| Variant | Gate | Result |
|---|---|---|
| h01 (18:00 ET) | median of 64 = +$23,729; 64 / 64 positive; top setting 2,279 dev trades | **advances** |
| h02 (19:00 ET) | median of 64 = +$850; 35 / 64 positive; top setting 1,837 dev trades | **advances** |
| h03 .. h23 | median of 64 <= 0 | stop |
| entry_london | cap 50 / default: net at 2 ticks -$10,756 vs -$12,474, net / max DD 1.76 vs 1.51 (cap 45 also qualified, 1.64) | **advances (cap 50)** |
| entry_ny | best net / DD (cap 0 / fixed, 1.14) has lower 2-tick net (-$28,980 vs -$28,680) | stop |
| entry_asia | every setting loses; nothing beats cap 0 on both | stop |

Observed after the gate, recorded here, **not acted on** (no protocol change): $28,953 of h01's $34,150 top-setting
net comes from Sunday-evening signals (the weekend reopen); Monday-Thursday signals net about $5,200. At the
reopen the market is thin, and touch fills of limit orders there are optimistic.

### Feature 2 (development interval, 200-trial random filter searches, objective net0)

| Variant | Baseline dev net / trades | Winner | Winner dev net / trades / max DD | Neighbours |
|---|---|---|---|---|
| h01 | $31,018 / 2,279 | **baseline** (no filter beat it) | $31,018 / 2,279 / $6,151 | none (nothing to move) |
| h02 | $8,565 / 1,837 | `minutes_from_open <= 50, range_ratio <= 1.9` | $11,056 / 1,476 / $3,289 | 6 / 6 > 0 |
| entry_london | $11,175 / 1,571 | `anchor_body_atr <= 1.9, risk_ticks <= 20` | $13,867 / 1,349 / $3,727 | 6 / 6 > 0 |

In-sample, best of 200 trials each. The London winner's `risk_ticks <= 20` makes the 50-tick entry cap inactive:
its trades are identical to Fair Price Reversal's London filter candidate on current code ($13,867.02, 1,349).
The cap itself adds nothing there.

Incidents (bugs, never results; attempts preserved, counted in the ledger):
- `entry_london_filters_random_net0_s1_n200`: stopped at its first filtered trial, `KeyError('session')` in
  v2's session-anchor filter path. Fixed (re-entrant session alias + regression test); rerun as
  `..._fix_session_reentry`. Hourly variants never used that code path.
- `validate h01_filters_random_net0_s1_n200`: `tvtester/validate.py` crashed reading the header-only
  `neighbours.csv` of a baseline winner; also counted distinct configurations from the module GRID instead of a
  variant's own grid. Fixed; rerun as `..._fix_empty_neighbours`. The partial attempt was not read.

### Feature 3

| Candidate | Walk-forward net | Positive years | PBO | DSR (N = 200) | Procedure | Candidate | Advance |
|---|---|---|---|---|---|---|---|
| h01 | +$16,054 | 7 / 10 | 0.028 | 0.584 | pass | **fail** | no |
| h02 | +$5,648 | 6 / 10 | 0.137 | 0.414 | **fail** | **fail** | no |
| entry_london | -$3,000 | 5 / 10 | 0.255 | 0.388 | **fail** | **fail** | no |

Reports: [h01](../validate/h01_filters_random_net0_s1_n200_fix_empty_neighbours.md),
[h02](../validate/h02_filters_random_net0_s1_n200.md),
[entry_london](../validate/entry_london_filters_random_net0_s1_n200_fix_session_reentry.md).

**Verdict: no Price Reversal v2 candidate advances to feature 4.** Features 4 and 5 were not run (not built,
and nothing passed). Per docs/VALIDATE.md there is no substitution or re-tuning of these candidates. Codex
review and replication of these numbers are pending.
