# Supertrend + Kalman M15: feature 3 (validation A) results

**Start here.** Verdict at the bottom. Protocol: [`docs/VALIDATE.md`](../../../VALIDATE.md).
Feature-2 notebook: [`../optimize/README.md`](../optimize/README.md).

Lab notebook. The protocol below was written **before** any feature-3 run. Every run is in
`results/supertrend_kalman/ledger.jsonl`. Development interval only (bars before 2024-01-01 UTC); no reserved bar is read.

## Protocol declared 2026-11-01, before any feature-3 run
- Candidates (all of them, frozen; none is added, swapped or re-tuned after looking):

| Candidate | Frozen configuration | Filters | E2 trial |
|---|---|---|---|
| ny E2 | `strategies/configs/supertrend_kalman_ny_filters_random_net1_s1_n200.json` | `rvi_side >= 55` | 33 |

- Method, folds (2014 .. 2023, anchored; rolling 4 years as sensitivity), S = 16 CSCV blocks, DSR population
  (the 200 E2 configurations), and the verdict rules are exactly those of `docs/VALIDATE.md` (hash in each
  run's `run.json`). Procedure verdict: walk-forward sum > 0 at 1 and 2 ticks, 7+ of 10 positive folds,
  PBO <= 0.5. Candidate verdict: DSR >= 0.95. Advance to feature 4 only if both pass.
- Budget: one `validate` run per candidate (600 matrix engine runs + up to 60 fold runs). A rerun needs a new
  dated entry here first and a stated reason (a bug, never a result).
- What it cannot show: the base parameters were picked on 2010-2026 data and the filters on the whole development
  interval, so passing is robustness conditional on the feature-2 search, not out-of-sample evidence.

## Results
One run (2026-11-01), as budgeted: 660 engine runs (600 matrix + 60 fold runs), logged before running. Every one
of the 200 configurations matched its `trials.csv` totals at 0 / 1 / 2 ticks. Report:
[`ny_filters_random_net1_s1_n200.md`](ny_filters_random_net1_s1_n200.md).

| Candidate | Walk-forward 0 / 1 / 2 ticks | Positive years (1 tick) | PBO | DSR (N = 200) | Procedure | Candidate |
|---|---|---|---|---|---|---|
| ny E2 | +58,245 / +32,245 / +6,035 | 7 of 10 | 0.175 | 0.180 | **pass** | fail |

- **Procedure passes, just.** Re-selected each year, the E2 search picked the frozen candidate (`rvi_side >= 55`)
  in 7 of 10 years and made money at 1 and 2 ticks, with exactly the 7 positive years the rule needs. At 2 ticks
  5 of 10 years lose; the 2-tick total (+6,035) rests on 2021 and 2022, when a different configuration was picked.
- **Candidate fails.** Its daily Sharpe (0.0269) is below the luck bar of the 200 E2 tries (0.0408): DSR 0.180.
  Without deflation it is 0.963 likely above zero, so the edge is too small to stand out from the search that found
  it. With the broader trial counts (2,202 for NY, 8,928 for the strategy) DSR falls to 0.05 and 0.03.
- PBO sensitivities are much weaker than the primary 0.175: 0.425 among eligible configurations only, 0.453 at
  2 ticks (diagnostic, cannot change the verdict).
- Codex replicated every pick, the PBO and the DSR exactly, and re-ran the 2015 fold with its own engine (R13).

## Verdict (feature 3, 2026-11-01)
- **Does not advance to feature 4.** The procedure passes, the candidate fails the deflated Sharpe (0.18, need
  0.95). Both must pass.
- Reading: the New York baseline (picked by feature 1 on 2010-2026) carries the result; the E2 filter adds little,
  and the whole is not distinguishable from the best of 200 tries. No substitution (NY E3 is not tried in its
  place).
