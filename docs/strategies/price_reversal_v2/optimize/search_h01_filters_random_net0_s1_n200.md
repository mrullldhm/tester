# Search h01_filters_random_net0_s1_n200

Generated 2026-11-11 20:19 UTC. Strategy `price_reversal_v2`, variant `h01`, space `filters`, sampler `random`, seed 1, objective `net0` (net profit + open P&L without added slippage), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 0 neighbours: 200 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 31,018.42 USD | 2,279 | 36.33% | 1.204 | 6,151.28 USD | yes |

Frozen configuration: `strategies/configs/price_reversal_v2_h01_filters_random_net0_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/price_reversal_v2_h01_filters_random_net0_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|

No neighbours (the winner has no searched parameter or filter to move).

## Top 20 trials

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 31,018.42 USD | 2,279 | 36.33% | 1.204 | 6,151.28 USD | yes |
| 2 | 22 | minutes_from_open <= 115 | 31,018.42 USD | 2,279 | 36.33% | 1.204 | 6,151.28 USD | yes |
| 3 | 177 | minutes_from_open <= 110 | 31,018.42 USD | 2,279 | 36.33% | 1.204 | 6,151.28 USD | yes |
| 4 | 161 | risk_atr >= 1 | 30,618.52 USD | 2,274 | 36.19% | 1.201 | 6,379.22 USD | yes |
| 5 | 73 | risk_atr <= 5.75, risk_ticks >= 8 | 29,726.10 USD | 1,195 | 39.50% | 1.286 | 4,997.78 USD | yes |
| 6 | 34 | minutes_from_open <= 95, risk_atr >= 1.75 | 29,620.46 USD | 2,077 | 36.30% | 1.205 | 7,023.90 USD | yes |
| 7 | 164 | risk_atr >= 2 | 29,193.56 USD | 1,922 | 36.58% | 1.212 | 7,384.96 USD | yes |
| 8 | 129 | risk_atr <= 5.75 | 27,903.18 USD | 2,141 | 36.29% | 1.204 | 4,706.12 USD | yes |
| 9 | 98 | risk_atr <= 6 | 27,570.82 USD | 2,159 | 36.36% | 1.199 | 4,706.12 USD | yes |
| 10 | 61 | anchor_body_atr <= 2, risk_ticks >= 14 | 27,555.38 USD | 531 | 43.88% | 1.412 | 5,330.44 USD | yes |
| 11 | 115 | minutes_from_open <= 80, range_ratio <= 1.9 | 26,316.40 USD | 2,180 | 36.10% | 1.189 | 6,427.38 USD | yes |
| 12 | 50 | anchor_body_atr <= 1.7, minutes_from_open <= 90, risk_ticks >= 14 | 26,093.92 USD | 504 | 44.05% | 1.415 | 6,223.36 USD | yes |
| 13 | 118 | range_ratio <= 1.7, risk_ticks >= 14 | 25,835.78 USD | 511 | 44.42% | 1.440 | 4,878.38 USD | yes |
| 14 | 186 | risk_atr <= 5.5 | 25,393.68 USD | 2,116 | 36.01% | 1.188 | 5,434.06 USD | yes |
| 15 | 70 | minutes_from_open <= 50, range_ratio <= 1.9 | 25,190.50 USD | 1,975 | 36.35% | 1.197 | 6,429.58 USD | yes |
| 16 | 138 | minutes_from_open <= 60, range_ratio <= 1.9, risk_atr <= 6 | 24,878.70 USD | 2,065 | 36.17% | 1.196 | 4,272.94 USD | yes |
| 17 | 20 | anchor_body_atr <= 1.4 | 24,792.66 USD | 1,967 | 35.99% | 1.190 | 6,075.66 USD | yes |
| 18 | 48 | minutes_from_open >= 15 | 24,307.72 USD | 1,814 | 36.16% | 1.215 | 8,079.00 USD | yes |
| 19 | 95 | minutes_from_open <= 30 | 24,262.60 USD | 1,370 | 37.59% | 1.243 | 6,203.22 USD | yes |
| 20 | 191 | anchor_body_atr <= 1.6 | 24,191.16 USD | 2,042 | 35.99% | 1.178 | 6,833.80 USD | yes |

Eligible trials: 95 of 200. Trials with objective above zero: 92.

Raw files in `results/price_reversal_v2/search/h01_filters_random_net0_s1_n200/`: `trials.csv` (every trial, baseline metrics), `neighbours.csv`, `run.json` (space, hashes, versions).
