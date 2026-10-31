# Supertrend + ATR trail + Kalman trend, M15 signals, CL1! 1m: feature 3 validation, `ny` (ny_filters_random_net1_s1_n200)

Generated 2026-10-31 16:21 UTC by `python -m tvtester.cli validate strategies/configs/supertrend_kalman_ny_filters_random_net1_s1_n200.json`. Protocol: [`docs/VALIDATE.md`](../../../VALIDATE.md).

> **Development interval only** (bars before 2024-01-01 UTC). This is retrospective robustness, conditional on the frozen feature-2 search universe: the base parameters were picked on 2010-2026 and the filters on the whole development interval, so a fold is not out-of-sample evidence. Passing does not show a tradable edge.

**Candidate:** trial 33 of `results/supertrend_kalman/search/ny_filters_random_net1_s1_n200`. Parameters `exit=flip`, `hours=ny`, `kalman_q=0.0001`, `rr=3`, `st_factor=2`, `swing=5`, `trail_mult=1`, `trigger=both`, `vol=rvi`; filters `rvi_side >= 55`.

## Verdict

| Verdict | Result | Checks |
|---|---|---|
| Procedure (would the E2 search, run blind each year, have worked?) | pass | walk-forward 1 tick 32,245.16 USD (pass), 2 ticks 6,035.16 USD (pass); positive folds 7 of 10 (need 7, pass); PBO 0.175 (max 0.5, pass) |
| Candidate (is its Sharpe more than best-of-200 luck?) | **fail** | DSR 0.180 (need 0.95) |
| **Advance to feature 4** | **no** | both verdicts must pass |

Engine runs: 600 (matrix: 200 configurations x 0 / 1 / 2 ticks) + 60 fold runs. Every matrix row matched its `trials.csv` totals.

![Walk-forward and CSCV](ny_filters_random_net1_s1_n200.png)

## Walk-forward re-selection (anchored, primary)

Each year Y: pick the best of the 200 E2 configurations on all development data before Y (1 tick, net profit + open P&L, scaled trade minimum), then run **that** configuration through year Y, starting flat. The last column is the frozen candidate in the same year (in-sample reference only).

| Test year | Picked trial | Configuration | Training result | Year result 0 / 1 / 2 ticks | Trades (1) | Frozen candidate (1 tick, in-sample) |
|---|---|---|---|---|---|---|
| 2014 | 53 | atr_ratio <= 1.8, hours_since_open >= 15, risk_atr <= 2.5 | 5,660.62 USD | 669.20 USD / -70.80 USD / -810.80 USD | 40 | 13,568.86 USD |
| 2015 | 33 | rvi_side >= 55 | 18,027.56 USD | 10,878.66 USD / 7,658.66 USD / 4,438.66 USD | 167 | 7,658.66 USD |
| 2016 | 33 | rvi_side >= 55 | 25,686.22 USD | 6,832.68 USD / 3,612.68 USD / 392.68 USD | 166 | 3,612.68 USD |
| 2017 | 33 | rvi_side >= 55 | 29,298.90 USD | 4,845.04 USD / 2,025.04 USD / -1,064.96 USD | 148 | 2,025.04 USD |
| 2018 | 33 | rvi_side >= 55 | 31,323.94 USD | -533.50 USD / -3,933.50 USD / -7,333.50 USD | 175 | -3,933.50 USD |
| 2019 | 33 | rvi_side >= 55 | 27,390.44 USD | 2,246.60 USD / -1,173.40 USD / -4,533.40 USD | 170 | -1,173.40 USD |
| 2020 | 33 | rvi_side >= 55 | 26,217.04 USD | 4,158.46 USD / 678.46 USD / -2,801.54 USD | 177 | 678.46 USD |
| 2021 | 59 | er <= 0.2, risk_atr <= 4.25, risk_ticks <= 115, rvi_side >= 45 | 29,580.22 USD | 11,636.44 USD / 10,176.44 USD / 8,716.44 USD | 78 | 7,118.76 USD |
| 2022 | 59 | er <= 0.2, risk_atr <= 4.25, risk_ticks <= 115, rvi_side >= 45 | 39,756.66 USD | 6,991.36 USD / 6,431.36 USD / 5,871.36 USD | 32 | 19,602.58 USD |
| 2023 | 33 | rvi_side >= 55 | 53,616.84 USD | 10,520.22 USD / 6,840.22 USD / 3,160.22 USD | 189 | 6,840.22 USD |
| **Total** | | | | **58,245.16 USD / 32,245.16 USD / 6,035.16 USD** | 1342 | 55,998.36 USD |

- Distinct configurations picked: 3 of 10 folds; the frozen candidate (trial 33) was picked in 7.
- Without its best year (2021, 10,176.44 USD): 22,068.72 USD at 1 tick.
- Walk-forward efficiency (mean year result / mean training result per training year, 1 tick): 0.92.
- Boundary check: a position left open at a fold end in 0 folds; fold run vs the same configuration's full-run slice differ by 0.00 USD in total at 1 tick.

### Sensitivity: rolling 4-year training window (cannot rescue a failure)

| Test year | Picked trial | Configuration | Year result 0 / 1 / 2 ticks |
|---|---|---|---|
| 2014 | 53 | atr_ratio <= 1.8, hours_since_open >= 15, risk_atr <= 2.5 | 669.20 USD / -70.80 USD / -810.80 USD |
| 2015 | 33 | rvi_side >= 55 | 10,878.66 USD / 7,658.66 USD / 4,438.66 USD |
| 2016 | 33 | rvi_side >= 55 | 6,832.68 USD / 3,612.68 USD / 392.68 USD |
| 2017 | 59 | er <= 0.2, risk_atr <= 4.25, risk_ticks <= 115, rvi_side >= 45 | 678.70 USD / -561.30 USD / -1,801.30 USD |
| 2018 | 33 | rvi_side >= 55 | -533.50 USD / -3,933.50 USD / -7,333.50 USD |
| 2019 | 59 | er <= 0.2, risk_atr <= 4.25, risk_ticks <= 115, rvi_side >= 45 | 5,962.72 USD / 4,662.72 USD / 3,422.72 USD |
| 2020 | 55 | er <= 0.4, hours_since_open <= 17 | 12,733.58 USD / 10,453.58 USD / 8,173.58 USD |
| 2021 | 55 | er <= 0.4, hours_since_open <= 17 | 15,623.38 USD / 13,083.38 USD / 10,543.38 USD |
| 2022 | 55 | er <= 0.4, hours_since_open <= 17 | 19,391.42 USD / 16,911.42 USD / 14,431.42 USD |
| 2023 | 0 | baseline | 8,737.66 USD / 4,497.66 USD / 257.66 USD |
| **Total** | | | **80,974.50 USD / 56,314.50 USD / 31,714.50 USD** |

## CSCV: probability of backtest overfitting

Daily P&L at 1 tick in 16 blocks, all 12,870 ways to split them into two halves. In each split the best configuration of one half is ranked in the other half. PBO = share of splits where it lands at or below the median. A diagnostic of the search, not a time-ordered test.

| Version | PBO | P(OOS loss) | Median logit | Median IS / OOS net of the pick | Slope (OOS on IS) | Skipped splits |
|---|---|---|---|---|---|---|
| primary (1 tick, all 200) | 0.175 | 0.172 | 1.42 | 39,235.41 USD / 15,214.61 USD | -0.892 | 0 |
| eligible configurations only | 0.425 | 0.172 | 0.17 | 39,235.41 USD / 15,214.61 USD | -0.892 | 0 |
| 2 ticks | 0.453 | 0.454 | 0.74 | 26,148.10 USD / 1,876.16 USD | -0.935 | 0 |

Identical trade paths among the 200 (inert filters): 77.

## Deflated Sharpe ratio of the frozen candidate

Daily marked-to-market P&L / 50,000 (fixed capital, idle days included as zeros), Sharpe per day, not annualized. The trial population that sets the luck bar is the 200 E2 configurations (their own Sharpe spread). The broader N rows reuse that spread for configurations whose spread was not measured here: an assumption, shown for scale.

| Version | SR (daily) | Skew | Kurtosis | N | SR luck bar (SR0) | DSR |
|---|---|---|---|---|---|---|
| primary: 1 tick, N = 200 | 0.0269 | 1.61 | 13.2 | 200 | 0.0408 | 0.180 |
| 1 tick, N = variant distinct | 0.0269 | 1.61 | 13.2 | 2,202 | 0.0512 | 0.054 |
| 1 tick, N = strategy distinct | 0.0269 | 1.61 | 13.2 | 8,928 | 0.0565 | 0.025 |
| 2 ticks, N = 200 | 0.0073 | 1.54 | 13.1 | 200 | 0.0363 | 0.029 |
| 1 tick, monthly returns, N = 200 | 0.1619 | 1.01 | 6.1 | 200 | 0.2120 | 0.247 |

- Distinct configurations: variant 2,202, strategy 8,928 (feature-1 grid + every search trial and neighbour). Configurations with zero variance left out of the spread: 59.
- Probabilistic Sharpe (SR > 0, no deflation), 1 tick: 0.963. 90% block bootstrap interval of the daily SR (mean block 20 days): 0.0041 .. 0.0489.
- The formula assumes independent, identically distributed returns; the bootstrap interval is the dependence check.

Raw files in `results/supertrend_kalman/validate/ny_filters_random_net1_s1_n200/`: `matrix.npz`, `folds.csv`, `folds_rolling.csv`, `pbo.json`, `dsr.json`, `verdict.json`, `run.json` (hashes).
