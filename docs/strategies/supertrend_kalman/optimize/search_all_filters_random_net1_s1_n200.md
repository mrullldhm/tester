# Search all_filters_random_net1_s1_n200

Generated 2026-10-31 14:02 UTC. Strategy `supertrend_kalman`, variant `all`, space `filters`, sampler `random`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 3 neighbours: 609 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 91,453.44 USD / 30,411.68 USD / -34,755.96 USD | 3,728 | 26.15% | 1.063 / 1.020 | 47,383.68 USD | yes |
| 2 | 85 | risk_ticks >= 100 | 137,285.08 USD / 122,375.08 USD / 109,195.08 USD | 546 | 35.16% | 1.266 / 1.233 | 27,642.46 USD | yes |

Frozen configuration: `strategies/configs/supertrend_kalman_all_filters_random_net1_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/supertrend_kalman_all_filters_random_net1_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | risk_ticks >= 105 | 144,908.24 USD / 137,598.24 USD / 125,398.24 USD | 488 | 35.66% | 1.304 / 1.285 | 26,628.44 USD | yes |
| 2 | 1 | risk_ticks >= 95 | 129,979.96 USD / 114,199.96 USD / 100,149.96 USD | 602 | 34.55% | 1.235 / 1.203 | 33,665.22 USD | yes |
| 3 | 0 | baseline | 91,453.44 USD / 30,411.68 USD / -34,755.96 USD | 3,728 | 26.15% | 1.063 / 1.020 | 47,383.68 USD | yes |

Neighbour objective: median 114,199.96 USD, worst 30,411.68 USD, 3 of 3 above zero; winner 122,375.08 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 85 | risk_ticks >= 100 | 137,285.08 USD / 122,375.08 USD / 109,195.08 USD | 546 | 35.16% | 1.266 / 1.233 | 27,642.46 USD | yes |
| 2 | 89 | atr_ratio >= 1.1 | 126,693.90 USD / 103,779.98 USD / 78,668.02 USD | 1,305 | 29.04% | 1.183 / 1.146 | 41,668.40 USD | yes |
| 3 | 49 | risk_atr >= 4.75 | 94,999.62 USD / 81,727.66 USD / 70,617.66 USD | 719 | 31.43% | 1.188 / 1.159 | 23,012.14 USD | yes |
| 4 | 76 | risk_atr >= 2.75, risk_ticks >= 35, rvi_side <= 75 | 102,765.46 USD / 70,609.58 USD / 32,761.64 USD | 1,827 | 28.41% | 1.100 / 1.067 | 45,880.54 USD | yes |
| 5 | 29 | atr_ratio >= 0.6, risk_ticks >= 115, rvi_side <= 70 | 73,592.80 USD / 68,022.80 USD / 57,562.80 USD | 360 | 33.33% | 1.189 / 1.172 | 34,758.34 USD | yes |
| 6 | 68 | atr_ratio >= 1, er <= 0.45, hours_since_open >= 14, risk_ticks >= 80 | 65,426.78 USD / 58,456.78 USD / 46,596.78 USD | 461 | 31.89% | 1.173 / 1.152 | 27,625.22 USD | yes |
| 7 | 46 | atr_ratio <= 1, risk_atr >= 4.75 | 68,150.56 USD / 55,964.58 USD / 47,124.58 USD | 572 | 30.42% | 1.192 / 1.155 | 32,145.22 USD | yes |
| 8 | 2 | atr_ratio >= 1.2, rvi_side >= 35 | 60,941.94 USD / 49,201.94 USD / 37,204.00 USD | 803 | 28.27% | 1.135 / 1.106 | 34,484.10 USD | yes |
| 9 | 176 | er >= 0.45, risk_atr >= 3.5 | 58,382.56 USD / 51,452.56 USD / 44,522.56 USD | 472 | 32.63% | 1.190 / 1.164 | 39,095.22 USD | yes |
| 10 | 11 | er >= 0.35, hours_since_open <= 22, risk_ticks <= 165, rvi_side <= 75 | 77,581.36 USD / 44,819.40 USD / 18,853.42 USD | 1,532 | 27.48% | 1.124 / 1.069 | 40,410.90 USD | yes |
| 11 | 168 | er <= 0.7 | 106,281.58 USD / 46,117.86 USD / -18,809.78 USD | 3,721 | 26.28% | 1.074 / 1.031 | 47,383.68 USD | yes |
| 12 | 30 | atr_ratio >= 0.8 | 85,284.80 USD / 41,329.02 USD / -12,462.84 USD | 2,760 | 26.49% | 1.069 / 1.032 | 53,469.08 USD | yes |
| 13 | 38 | hours_since_open >= 14, rvi_side >= 35 | 74,343.20 USD / 40,571.04 USD / 4,767.12 USD | 1,840 | 27.01% | 1.088 / 1.046 | 62,191.70 USD | yes |
| 14 | 174 | er >= 0.4, hours_since_open <= 15, rvi_side <= 65 | 48,007.06 USD / 35,577.06 USD / 22,171.08 USD | 747 | 27.31% | 1.140 / 1.101 | 29,976.98 USD | yes |
| 15 | 162 | risk_atr >= 4 | 57,487.10 USD / 36,001.12 USD / 17,259.16 USD | 1,145 | 28.65% | 1.078 / 1.048 | 39,083.86 USD | yes |
| 16 | 186 | er <= 0.75 | 94,143.44 USD / 33,121.68 USD / -32,025.96 USD | 3,728 | 26.18% | 1.065 / 1.022 | 47,383.68 USD | yes |
| 17 | 161 | hours_since_open <= 14, risk_ticks >= 55 | 62,367.32 USD / 28,281.34 USD / 5,823.30 USD | 1,334 | 28.41% | 1.072 / 1.032 | 38,274.70 USD | yes |
| 18 | 0 | baseline | 91,453.44 USD / 30,411.68 USD / -34,755.96 USD | 3,728 | 26.15% | 1.063 / 1.020 | 47,383.68 USD | yes |
| 19 | 63 | atr_ratio <= 1.9 | 91,453.44 USD / 30,411.68 USD / -34,755.96 USD | 3,728 | 26.15% | 1.063 / 1.020 | 47,383.68 USD | yes |
| 20 | 142 | hours_since_open >= 0 | 91,453.44 USD / 30,411.68 USD / -34,755.96 USD | 3,728 | 26.15% | 1.063 / 1.020 | 47,383.68 USD | yes |

Eligible trials: 116 of 200. Trials with objective above zero: 43.

Raw files in `results/supertrend_kalman/search/all_filters_random_net1_s1_n200/`: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
