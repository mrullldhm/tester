# Search ny_filters_random_net1_s1_n200

Generated 2026-10-31 13:14 UTC. Strategy `supertrend_kalman`, variant `ny`, space `filters`, sampler `random`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 3 neighbours: 609 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 2 | 33 | rvi_side >= 55 | 104,217.06 USD / 60,457.06 USD / 16,487.06 USD | 2,247 | 45.04% | 1.193 / 1.107 | 12,417.88 USD | yes |

Frozen configuration: `strategies/configs/supertrend_kalman_ny_filters_random_net1_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/supertrend_kalman_ny_filters_random_net1_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 2 | 1 | rvi_side >= 50 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 3 | 2 | rvi_side >= 60 | 53,634.94 USD / 21,374.94 USD / -11,095.06 USD | 1,653 | 44.95% | 1.132 / 1.050 | 14,259.76 USD | yes |

Neighbour objective: median 53,025.44 USD, worst 21,374.94 USD, 3 of 3 above zero; winner 60,457.06 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 33 | rvi_side >= 55 | 104,217.06 USD / 60,457.06 USD / 16,487.06 USD | 2,247 | 45.04% | 1.193 / 1.107 | 12,417.88 USD | yes |
| 2 | 59 | er <= 0.2, risk_atr <= 4.25, risk_ticks <= 115, rvi_side >= 45 | 74,398.48 USD / 57,518.48 USD / 41,098.48 USD | 876 | 47.15% | 1.444 / 1.325 | 12,460.54 USD | yes |
| 3 | 63 | atr_ratio <= 1.9 | 106,259.76 USD / 55,499.76 USD / 4,749.76 USD | 2,612 | 44.26% | 1.170 / 1.085 | 14,722.80 USD | yes |
| 4 | 2 | atr_ratio >= 1.2, rvi_side >= 35 | 92,939.54 USD / 55,479.54 USD / 17,569.54 USD | 1,923 | 47.63% | 1.213 / 1.122 | 24,981.68 USD | yes |
| 5 | 55 | er <= 0.4, hours_since_open <= 17 | 87,613.84 USD / 54,833.84 USD / 22,063.84 USD | 1,708 | 42.86% | 1.194 / 1.116 | 14,799.34 USD | yes |
| 6 | 64 | risk_atr >= 1.75 | 103,449.70 USD / 54,329.70 USD / 5,219.70 USD | 2,515 | 44.77% | 1.170 / 1.085 | 13,216.32 USD | yes |
| 7 | 14 | atr_ratio >= 0.8, hours_since_open >= 12 | 103,547.70 USD / 53,127.70 USD / 2,317.70 USD | 2,615 | 44.28% | 1.165 / 1.081 | 15,104.76 USD | yes |
| 8 | 30 | atr_ratio >= 0.8 | 103,547.70 USD / 53,127.70 USD / 2,317.70 USD | 2,615 | 44.28% | 1.165 / 1.081 | 15,104.76 USD | yes |
| 9 | 0 | baseline | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 10 | 3 | rvi_side >= 45 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 11 | 16 | hours_since_open >= 4 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 12 | 38 | hours_since_open >= 14, rvi_side >= 35 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 13 | 54 | hours_since_open <= 23, rvi_side >= 35 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 14 | 58 | hours_since_open >= 5 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 15 | 114 | rvi_side >= 35 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 16 | 127 | hours_since_open >= 2, rvi_side >= 45 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 17 | 142 | hours_since_open >= 0 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 18 | 184 | hours_since_open >= 1 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 19 | 85 | risk_ticks >= 100 | 75,023.58 USD / 52,743.58 USD / 30,463.58 USD | 1,121 | 48.44% | 1.236 / 1.160 | 12,245.52 USD | yes |
| 20 | 186 | er <= 0.75 | 102,209.46 USD / 51,149.46 USD / 99.46 USD | 2,627 | 44.16% | 1.162 / 1.077 | 15,000.94 USD | yes |

Eligible trials: 81 of 200. Trials with objective above zero: 74.

Raw files in `results/supertrend_kalman/search/ny_filters_random_net1_s1_n200/`: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
