# Fair Price Reversal (LuxAlgo 9:29 ET), CL1! sessions: feature 3 validation, `london` (london_filters_random_net1_s1_n200)

Generated 2026-10-31 16:18 UTC by `python -m tvtester.cli validate strategies/configs/fair_price_reversal_london_filters_random_net1_s1_n200.json`. Protocol: [`docs/VALIDATE.md`](../../../VALIDATE.md).

> **Development interval only** (bars before 2024-01-01 UTC). This is retrospective robustness, conditional on the frozen feature-2 search universe: the base parameters were picked on 2010-2026 and the filters on the whole development interval, so a fold is not out-of-sample evidence. Passing does not show a tradable edge.

**Candidate:** trial 89 of `results/fair_price_reversal/search/london_filters_random_net1_s1_n200`. Parameters `atr_mult=2.0`, `session=london`, `swing=3`, `target=rr2`, `window=120`; filters `risk_ticks >= 30`.

## Verdict

| Verdict | Result | Checks |
|---|---|---|
| Procedure (would the E2 search, run blind each year, have worked?) | **fail** | walk-forward 1 tick -4,335.34 USD (**fail**), 2 ticks -11,691.32 USD (**fail**); positive folds 4 of 10 (need 7, **fail**); PBO 0.190 (max 0.5, pass) |
| Candidate (is its Sharpe more than best-of-200 luck?) | **fail** | DSR 0.092 (need 0.95) |
| **Advance to feature 4** | **no** | both verdicts must pass |

Engine runs: 600 (matrix: 200 configurations x 0 / 1 / 2 ticks) + 60 fold runs. Every matrix row matched its `trials.csv` totals.

![Walk-forward and CSCV](london_filters_random_net1_s1_n200.png)

## Walk-forward re-selection (anchored, primary)

Each year Y: pick the best of the 200 E2 configurations on all development data before Y (1 tick, net profit + open P&L, scaled trade minimum), then run **that** configuration through year Y, starting flat. The last column is the frozen candidate in the same year (in-sample reference only).

| Test year | Picked trial | Configuration | Training result | Year result 0 / 1 / 2 ticks | Trades (1) | Frozen candidate (1 tick, in-sample) |
|---|---|---|---|---|---|---|
| 2014 | 89 | risk_ticks >= 30 | 11,725.94 USD | -598.24 USD / -818.24 USD / -1,038.24 USD | 12 | -818.24 USD |
| 2015 | 89 | risk_ticks >= 30 | 10,907.70 USD | -854.32 USD / -1,134.32 USD / -1,414.32 USD | 16 | -1,134.32 USD |
| 2016 | 89 | risk_ticks >= 30 | 9,773.38 USD | -292.16 USD / -432.16 USD / -572.16 USD | 8 | -432.16 USD |
| 2017 | 36 | range_ratio >= 1.3 | 9,062.54 USD | 1,387.14 USD / 827.14 USD / -282.86 USD | 43 | -328.04 USD |
| 2018 | 36 | range_ratio >= 1.3 | 9,889.68 USD | -1,903.06 USD / -2,783.06 USD / -3,663.06 USD | 53 | 3,057.84 USD |
| 2019 | 36 | range_ratio >= 1.3 | 7,106.62 USD | 2,333.32 USD / 1,933.32 USD / 987.34 USD | 34 | 73.92 USD |
| 2020 | 36 | range_ratio >= 1.3 | 9,039.94 USD | -1,126.98 USD / -1,992.96 USD / -2,692.96 USD | 48 | -3,782.56 USD |
| 2021 | 36 | range_ratio >= 1.3 | 7,046.98 USD | 259.00 USD / 57.04 USD / -642.96 USD | 48 | 2,605.48 USD |
| 2022 | 130 | anchor_body_atr >= 0.5, minutes_from_open >= 35, range_ratio >= 0.8 | 11,550.82 USD | -1,745.12 USD / -2,565.12 USD / -3,385.12 USD | 56 | 18,656.40 USD |
| 2023 | 89 | risk_ticks >= 30 | 29,624.26 USD | 3,233.02 USD / 2,573.02 USD / 1,013.02 USD | 49 | 2,573.02 USD |
| **Total** | | | | **692.60 USD / -4,335.34 USD / -11,691.32 USD** | 367 | 20,471.34 USD |

- Distinct configurations picked: 3 of 10 folds; the frozen candidate (trial 89) was picked in 4.
- Without its best year (2023, 2,573.02 USD): -6,908.36 USD at 1 tick.
- Walk-forward efficiency (mean year result / mean training result per training year, 1 tick): -0.27.
- Boundary check: a position left open at a fold end in 0 folds; fold run vs the same configuration's full-run slice differ by 0.00 USD in total at 1 tick.

### Sensitivity: rolling 4-year training window (cannot rescue a failure)

| Test year | Picked trial | Configuration | Year result 0 / 1 / 2 ticks |
|---|---|---|---|
| 2014 | 89 | risk_ticks >= 30 | -598.24 USD / -818.24 USD / -1,038.24 USD |
| 2015 | 89 | risk_ticks >= 30 | -854.32 USD / -1,134.32 USD / -1,414.32 USD |
| 2016 | 172 | anchor_body_atr >= 1.4 | 803.52 USD / 503.52 USD / -36.48 USD |
| 2017 | 172 | anchor_body_atr >= 1.4 | 73.62 USD / -206.38 USD / -816.38 USD |
| 2018 | 176 | range_ratio >= 1.5 | -2,070.60 USD / -2,610.60 USD / -3,150.60 USD |
| 2019 | 110 | minutes_from_open >= 40, risk_atr >= 5.5 | -406.38 USD / -706.38 USD / -1,006.38 USD |
| 2020 | 66 | anchor_body_atr <= 0.5, risk_atr >= 2.75 | 231.62 USD / -1,114.36 USD / -3,114.36 USD |
| 2021 | 50 | anchor_body_atr <= 1.7, minutes_from_open <= 90, risk_ticks >= 14 | -2,204.86 USD / -3,686.82 USD / -5,666.82 USD |
| 2022 | 130 | anchor_body_atr >= 0.5, minutes_from_open >= 35, range_ratio >= 0.8 | -1,745.12 USD / -2,565.12 USD / -3,385.12 USD |
| 2023 | 115 | minutes_from_open <= 80, range_ratio <= 1.9 | 3,250.22 USD / 140.22 USD / -5,139.78 USD |
| **Total** | | | **-3,520.54 USD / -12,198.48 USD / -24,768.48 USD** |

## CSCV: probability of backtest overfitting

Daily P&L at 1 tick in 16 blocks, all 12,870 ways to split them into two halves. In each split the best configuration of one half is ranked in the other half. PBO = share of splits where it lands at or below the median. A diagnostic of the search, not a time-ordered test.

| Version | PBO | P(OOS loss) | Median logit | Median IS / OOS net of the pick | Slope (OOS on IS) | Skipped splits |
|---|---|---|---|---|---|---|
| primary (1 tick, all 200) | 0.190 | 0.198 | 3.32 | 16,189.87 USD / 7,064.69 USD | -0.083 | 0 |
| eligible configurations only | 0.202 | 0.198 | 3.33 | 16,189.87 USD / 7,064.69 USD | -0.083 | 0 |
| 2 ticks | 0.191 | 0.351 | 2.59 | 11,820.47 USD / 3,105.11 USD | -0.008 | 0 |

Identical trade paths among the 200 (inert filters): 14.

## Deflated Sharpe ratio of the frozen candidate

Daily marked-to-market P&L / 50,000 (fixed capital, idle days included as zeros), Sharpe per day, not annualized. The trial population that sets the luck bar is the 200 E2 configurations (their own Sharpe spread). The broader N rows reuse that spread for configurations whose spread was not measured here: an assumption, shown for scale.

| Version | SR (daily) | Skew | Kurtosis | N | SR luck bar (SR0) | DSR |
|---|---|---|---|---|---|---|
| primary: 1 tick, N = 200 | 0.0392 | 4.06 | 41.3 | 200 | 0.0581 | 0.092 |
| 1 tick, N = variant distinct | 0.0392 | 4.06 | 41.3 | 698 | 0.0662 | 0.029 |
| 1 tick, N = strategy distinct | 0.0392 | 4.06 | 41.3 | 2,011 | 0.0725 | 0.010 |
| 2 ticks, N = 200 | 0.0281 | 3.86 | 40.7 | 200 | 0.0930 | 0.000 |
| 1 tick, monthly returns, N = 200 | 0.1544 | 4.54 | 34.3 | 200 | 0.2800 | 0.012 |

- Distinct configurations: variant 698, strategy 2,011 (feature-1 grid + every search trial and neighbour). Configurations with zero variance left out of the spread: 13.
- Probabilistic Sharpe (SR > 0, no deflation), 1 tick: 0.997. 90% block bootstrap interval of the daily SR (mean block 20 days): 0.0095 .. 0.0661.
- The formula assumes independent, identically distributed returns; the bootstrap interval is the dependence check.

Raw files in `results/fair_price_reversal/validate/london_filters_random_net1_s1_n200/`: `matrix.npz`, `folds.csv`, `folds_rolling.csv`, `pbo.json`, `dsr.json`, `verdict.json`, `run.json` (hashes).
