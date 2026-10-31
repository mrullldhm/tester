# Search asia_full_tpe_net1_s1_n300

Generated 2026-10-31 14:14 UTC. Strategy `supertrend_kalman`, variant `asia`, space `full`, sampler `tpe`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 300 trials (15 duplicates) and 26 neighbours: 933 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 15,844.42 USD / -3,495.58 USD / -22,835.58 USD | 979 | 45.45% | 1.200 / 0.961 | 5,922.66 USD | yes |
| 2 | 230 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 12,565.16 USD / 5,865.16 USD / -834.84 USD | 342 | 47.66% | 1.500 / 1.203 | 2,202.36 USD | yes |

Frozen configuration: `strategies/configs/supertrend_kalman_asia_full_tpe_net1_s1_n300.json`. Replay it with `python -m tvtester.cli replay strategies/configs/supertrend_kalman_asia_full_tpe_net1_s1_n300.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 9 | kalman_q=0.0001, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 12,885.16 USD / 6,085.16 USD / -714.84 USD | 342 | 47.66% | 1.513 / 1.210 | 2,202.36 USD | yes |
| 2 | 14 | kalman_q=0.0001, rr=2, swing=5, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 12,565.16 USD / 5,865.16 USD / -834.84 USD | 342 | 47.66% | 1.500 / 1.203 | 2,202.36 USD | yes |
| 3 | 15 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 11, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 12,565.16 USD / 5,865.16 USD / -834.84 USD | 342 | 47.66% | 1.500 / 1.203 | 2,202.36 USD | yes |
| 4 | 16 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 13, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 12,565.16 USD / 5,865.16 USD / -834.84 USD | 342 | 47.66% | 1.500 / 1.203 | 2,202.36 USD | yes |
| 5 | 22 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 175, rvi_side <= 70 | 12,565.16 USD / 5,865.16 USD / -834.84 USD | 342 | 47.66% | 1.500 / 1.203 | 2,202.36 USD | yes |
| 6 | 17 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_ticks <= 170, rvi_side <= 70 | 13,130.44 USD / 5,790.44 USD / -1,889.56 USD | 378 | 48.15% | 1.477 / 1.182 | 2,502.36 USD | yes |
| 7 | 21 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 165, rvi_side <= 70 | 12,399.18 USD / 5,719.18 USD / -960.82 USD | 341 | 47.51% | 1.494 / 1.197 | 2,202.36 USD | yes |
| 8 | 5 | kalman_q=0.0001, rr=2, swing=5, vol=atr_ratio:1.3, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 12,209.18 USD / 5,529.18 USD / -1,150.82 USD | 341 | 47.51% | 1.486 / 1.191 | 2,202.36 USD | yes |
| 9 | 23 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170 | 13,665.72 USD / 5,525.72 USD / -2,614.28 USD | 414 | 46.86% | 1.441 / 1.155 | 2,645.12 USD | yes |
| 10 | 18 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 1.75, risk_ticks <= 170, rvi_side <= 70 | 12,316.92 USD / 5,376.92 USD / -1,563.08 USD | 354 | 47.46% | 1.476 / 1.180 | 2,202.36 USD | yes |
| 11 | 7 | exit=fixed, kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 11,301.24 USD / 4,681.24 USD / -1,938.76 USD | 338 | 49.70% | 1.405 / 1.149 | 2,736.48 USD | yes |
| 12 | 8 | exit=flip, kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 11,261.24 USD / 4,641.24 USD / -1,978.76 USD | 338 | 49.41% | 1.406 / 1.148 | 2,628.14 USD | yes |
| 13 | 4 | kalman_q=0.0001, rr=2, swing=5, vol=atr_ratio:1.0, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 10,881.34 USD / 4,361.34 USD / -2,158.66 USD | 333 | 47.45% | 1.443 / 1.154 | 2,202.36 USD | yes |
| 14 | 20 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, rvi_side <= 70 | 10,918.98 USD / 4,038.98 USD / -2,841.02 USD | 351 | 47.01% | 1.391 / 1.127 | 2,480.50 USD | yes |
| 15 | 25 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 75 | 11,568.28 USD / 3,988.28 USD / -3,591.72 USD | 386 | 46.89% | 1.397 / 1.119 | 2,532.36 USD | yes |
| 16 | 6 | kalman_q=0.0001, rr=2, swing=5, vol=rvi, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 10,027.82 USD / 3,967.82 USD / -2,092.18 USD | 309 | 46.93% | 1.419 / 1.145 | 2,202.26 USD | yes |
| 17 | 19 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2.25, risk_ticks <= 170, rvi_side <= 70 | 9,271.64 USD / 2,991.64 USD / -3,288.36 USD | 318 | 47.17% | 1.400 / 1.112 | 1,590.50 USD | yes |
| 18 | 10 | kalman_q=0.0001, rr=2, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 8,375.56 USD / 2,075.56 USD / -4,224.44 USD | 322 | 47.83% | 1.327 / 1.071 | 2,466.38 USD | yes |
| 19 | 13 | rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 10,940.22 USD / -2,619.78 USD / -16,179.78 USD | 689 | 45.57% | 1.206 / 0.957 | 3,104.72 USD | yes |
| 20 | 1 | kalman_q=0.0001, rr=2, swing=5, trigger=both, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 10,135.30 USD / -4,404.70 USD / -18,944.70 USD | 735 | 44.35% | 1.174 / 0.934 | 3,402.30 USD | yes |
| 21 | 12 | kalman_q=0.0001, rr=2, st_factor=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 2,468.50 USD / -8,931.50 USD / -20,331.50 USD | 575 | 42.96% | 1.053 / 0.833 | 4,710.98 USD | yes |
| 22 | 0 | kalman_q=0.0001, rr=2, swing=5, trigger=st, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | -1,570.76 USD / -10,310.76 USD / -19,050.76 USD | 438 | 41.55% | 0.956 / 0.750 | 9,100.32 USD | yes |
| 23 | 11 | kalman_q=0.0001, rr=2, swing=5, trail_mult=1, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | -15,144.88 USD / -43,844.88 USD / -72,544.88 USD | 1,444 | 35.53% | 0.831 / 0.598 | 20,994.04 USD | yes |
| 24 | 24 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 65 | 10,913.04 USD / 6,053.04 USD / 1,193.04 USD | 248 | 50.40% | 1.659 / 1.315 | 2,026.18 USD | no |
| 25 | 3 | kalman_q=0.0001, rr=2, swing=5, vol=stop_atr:3, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 6,537.40 USD / 4,057.40 USD / 1,577.40 USD | 130 | 48.46% | 1.651 / 1.354 | 1,936.18 USD | no |
| 26 | 2 | kalman_q=0.0001, rr=2, swing=5, vol=stop_atr:1.5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 0.00 USD / 0.00 USD / 0.00 USD | 0 | — | — / — | 0.00 USD | no |

Neighbour objective: median 4,501.29 USD, worst -43,844.88 USD, 20 of 26 above zero; winner 5,865.16 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 230 | kalman_q=0.0001, rr=2, swing=5, hours_since_open <= 12, risk_atr >= 2, risk_ticks <= 170, rvi_side <= 70 | 12,565.16 USD / 5,865.16 USD / -834.84 USD | 342 | 47.66% | 1.500 / 1.203 | 2,202.36 USD | yes |
| 2 | 217 | kalman_q=0.0001, swing=5, hours_since_open <= 14, risk_atr >= 2, risk_ticks <= 175 | 13,985.72 USD / 5,745.72 USD / -2,494.28 USD | 414 | 46.86% | 1.451 / 1.161 | 2,645.12 USD | yes |
| 3 | 86 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.6, hours_since_open <= 18, risk_ticks <= 170 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 4 | 195 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.7, risk_ticks <= 180 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 5 | 197 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.7, risk_ticks <= 180 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 6 | 198 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.7, risk_ticks <= 180 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 7 | 200 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.7, risk_ticks <= 175 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 8 | 202 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.7, risk_ticks <= 175 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 9 | 204 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.7, risk_ticks <= 175 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 10 | 208 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.8, risk_ticks <= 175 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 11 | 210 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.8, risk_ticks <= 175 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 12 | 227 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.8, risk_ticks <= 170 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 13 | 231 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.7, risk_ticks <= 170 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 14 | 235 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.8, risk_ticks <= 170 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 15 | 277 | kalman_q=0.0001, rr=2, swing=5, risk_ticks <= 175 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 16 | 284 | kalman_q=0.0001, rr=2, swing=5, risk_ticks <= 180 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 17 | 286 | kalman_q=0.0001, rr=2, swing=5, risk_ticks <= 180 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 18 | 288 | kalman_q=0.0001, rr=2, swing=5, risk_ticks <= 180 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 19 | 290 | kalman_q=0.0001, rr=2, swing=5, risk_ticks <= 180 | 14,532.96 USD / 5,712.96 USD / -3,447.04 USD | 452 | 47.35% | 1.433 / 1.148 | 2,980.40 USD | yes |
| 20 | 232 | kalman_q=0.0001, rr=2, swing=5, atr_ratio <= 1.7, risk_ticks <= 165 | 14,366.98 USD / 5,566.98 USD / -3,573.02 USD | 451 | 47.23% | 1.428 / 1.144 | 2,980.40 USD | yes |

Eligible trials: 176 of 300. Trials with objective above zero: 102.

Raw files in `results/supertrend_kalman/search/asia_full_tpe_net1_s1_n300/`: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
