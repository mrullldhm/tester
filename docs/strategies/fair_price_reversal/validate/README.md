# Fair Price Reversal: feature 3 (validation A) results

**Start here.** Verdict at the bottom. Protocol: [`docs/VALIDATE.md`](../../../VALIDATE.md).
Feature-2 notebook: [`../optimize/README.md`](../optimize/README.md).

Lab notebook. The protocol below was written **before** any feature-3 run. Every run is in
`results/fair_price_reversal/ledger.jsonl`. Development interval only (bars before 2024-01-01 UTC); no reserved bar is read.

## Protocol declared 2026-11-01, before any feature-3 run
- Candidates (all of them, frozen; none is added, swapped or re-tuned after looking):

| Candidate | Frozen configuration | Filters | E2 trial |
|---|---|---|---|
| ny E2 | `strategies/configs/fair_price_reversal_ny_filters_random_net1_s1_n200.json` | `anchor_body_atr >= 0.3`, `risk_ticks >= 32` | 85 |
| london E2 | `strategies/configs/fair_price_reversal_london_filters_random_net1_s1_n200.json` | `risk_ticks >= 30` | 89 |

- Method, folds (2014 .. 2023, anchored; rolling 4 years as sensitivity), S = 16 CSCV blocks, DSR population
  (the 200 E2 configurations), and the verdict rules are exactly those of `docs/VALIDATE.md` (hash in each
  run's `run.json`). Procedure verdict: walk-forward sum > 0 at 1 and 2 ticks, 7+ of 10 positive folds,
  PBO <= 0.5. Candidate verdict: DSR >= 0.95. Advance to feature 4 only if both pass.
- Budget: one `validate` run per candidate (600 matrix engine runs + up to 60 fold runs). A rerun needs a new
  dated entry here first and a stated reason (a bug, never a result).
- What it cannot show: the base parameters were picked on 2010-2026 data and the filters on the whole development
  interval, so passing is robustness conditional on the feature-2 search, not out-of-sample evidence.

## Results
One run per candidate (2026-11-01), as budgeted: 660 engine runs each (600 matrix + 60 fold runs), logged
before running. Every one of the 200 configurations matched its `trials.csv` totals at 0 / 1 / 2 ticks. Reports:
[`ny_filters_random_net1_s1_n200.md`](ny_filters_random_net1_s1_n200.md),
[`london_filters_random_net1_s1_n200.md`](london_filters_random_net1_s1_n200.md).

| Candidate | Walk-forward 0 / 1 / 2 ticks | Positive years (1 tick) | PBO | DSR (N = 200) | Procedure | Candidate |
|---|---|---|---|---|---|---|
| ny E2 | +35,026 / +22,840 / +9,740 | 6 of 10 | 0.184 | 0.432 | fail (years) | fail |
| london E2 | +693 / −4,335 / −11,691 | 4 of 10 | 0.190 | 0.092 | fail | fail |

- **NY.** The re-selection picked the frozen candidate in 8 of 10 years, so this mostly tests the candidate
  itself. Its walk-forward profit stays above zero at 2 ticks, but 2023 alone is +18,014 of +22,840 at 1 tick
  (without 2023: +4,826), and 2014, 2016, 2018 and 2019 lose. The rolling 4-year window loses at 1 tick (−731).
  The Sharpe is below the luck bar of 200 tries (SR 0.0356 per day vs 0.0382).
- **London.** The search switched between three configurations, and the years it picked lost money. The frozen
  candidate's in-sample profit (+20,471 over 2014-2023 at 1 tick) is mostly 2022 (+18,656), the year the
  procedure did not pick it.
- PBO is low for both (about 0.19): the best of the 200 usually stays above the median of the 200 in the other half
  of the data. That says the search ranks are stable, not that the best is profitable: in the London search 111
  of the 200 lose at 1 tick over the development interval.
- Codex replicated every pick, PBO and DSR exactly (R13).

## Verdict (feature 3, 2026-11-01)
- **Neither candidate advances to feature 4.** NY fails the positive-years rule (6 of 10, need 7) and the deflated
  Sharpe (0.43, need 0.95). London fails every walk-forward check and the deflated Sharpe (0.09).
- The minimum-stop filter (H2) is a real cost effect, but on this evidence it is a bet on volatile years (2022,
  2023), not a stable edge. No substitution: NY E3 and a `risk_atr` filter are not tried in its place; a new idea
  starts at feature 2 with its own budget.
