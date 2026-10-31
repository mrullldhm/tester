# Search london_full_tpe_net1_s1_n300

Generated 2026-10-31 14:07 UTC. Strategy `supertrend_kalman`, variant `london`, space `full`, sampler `tpe`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 300 trials (22 duplicates) and 24 neighbours: 906 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 17,638.20 USD / 6,258.20 USD / -5,301.80 USD | 590 | 42.71% | 1.272 / 1.087 | 4,419.24 USD | yes |
| 2 | 222 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 17,530.30 USD / 9,020.30 USD / 470.30 USD | 485 | 42.06% | 1.315 / 1.147 | 4,980.80 USD | yes |

Frozen configuration: `strategies/configs/supertrend_kalman_london_full_tpe_net1_s1_n300.json`. Replay it with `python -m tvtester.cli replay strategies/configs/supertrend_kalman_london_full_tpe_net1_s1_n300.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 23 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 75 | 17,864.62 USD / 9,634.62 USD / 1,364.62 USD | 469 | 42.00% | 1.332 / 1.163 | 4,980.80 USD | yes |
| 2 | 21 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.5, rvi_side <= 80 | 17,356.58 USD / 9,066.58 USD / 736.58 USD | 471 | 42.25% | 1.318 / 1.151 | 4,926.78 USD | yes |
| 3 | 14 | st_factor=2, trigger=trail, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 17,530.30 USD / 9,020.30 USD / 470.30 USD | 485 | 42.06% | 1.315 / 1.147 | 4,980.80 USD | yes |
| 4 | 15 | st_factor=2, trigger=trail, er <= 0.75, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 17,530.30 USD / 9,020.30 USD / 470.30 USD | 485 | 42.06% | 1.315 / 1.147 | 4,980.80 USD | yes |
| 5 | 16 | st_factor=2, trigger=trail, er <= 0.8, risk_atr >= 1.25, rvi_side <= 80 | 17,530.30 USD / 9,020.30 USD / 470.30 USD | 485 | 42.06% | 1.315 / 1.147 | 4,980.80 USD | yes |
| 6 | 17 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 7, risk_atr >= 1.25, rvi_side <= 80 | 17,530.30 USD / 9,020.30 USD / 470.30 USD | 485 | 42.06% | 1.315 / 1.147 | 4,980.80 USD | yes |
| 7 | 18 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 9, risk_atr >= 1.25, rvi_side <= 80 | 17,530.30 USD / 9,020.30 USD / 470.30 USD | 485 | 42.06% | 1.315 / 1.147 | 4,980.80 USD | yes |
| 8 | 20 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1, rvi_side <= 80 | 17,322.16 USD / 8,712.16 USD / 62.16 USD | 492 | 41.87% | 1.307 / 1.140 | 4,980.80 USD | yes |
| 9 | 22 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25 | 16,830.20 USD / 8,220.20 USD / -429.80 USD | 490 | 41.84% | 1.298 / 1.132 | 5,014.82 USD | yes |
| 10 | 19 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, rvi_side <= 80 | 16,595.98 USD / 7,845.98 USD / -1,064.02 USD | 501 | 41.52% | 1.290 / 1.124 | 4,980.80 USD | yes |
| 11 | 7 | exit=fixed, st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 15,592.36 USD / 7,272.36 USD / -1,077.64 USD | 482 | 45.23% | 1.244 / 1.105 | 7,146.78 USD | yes |
| 12 | 9 | rr=3, st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 16,320.30 USD / 6,750.30 USD / -2,829.70 USD | 485 | 41.86% | 1.293 / 1.110 | 5,060.80 USD | yes |
| 13 | 0 | st_factor=2, trigger=st, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 16,376.84 USD / 6,316.84 USD / -3,973.16 USD | 558 | 43.55% | 1.254 / 1.089 | 5,581.40 USD | yes |
| 14 | 1 | st_factor=2, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 17,597.40 USD / 6,257.40 USD / -5,312.60 USD | 630 | 43.02% | 1.242 / 1.078 | 4,385.02 USD | yes |
| 15 | 12 | trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 13,134.66 USD / 6,064.66 USD / -435.34 USD | 367 | 42.51% | 1.311 / 1.130 | 4,166.28 USD | yes |
| 16 | 8 | exit=flip, st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 13,882.36 USD / 5,522.36 USD / -2,867.64 USD | 482 | 43.15% | 1.223 / 1.081 | 6,066.78 USD | yes |
| 17 | 10 | st_factor=2, swing=3, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 8,347.20 USD / -3,032.80 USD / -14,452.80 USD | 640 | 39.06% | 1.107 / 0.965 | 7,689.14 USD | yes |
| 18 | 13 | kalman_q=0.01, st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 21,602.66 USD / -5,437.34 USD / -33,537.34 USD | 1,467 | 39.67% | 1.119 / 0.973 | 8,690.50 USD | yes |
| 19 | 4 | st_factor=2, trigger=trail, vol=atr_ratio:1.0, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 636.28 USD / -17,643.72 USD / -35,953.72 USD | 986 | 38.34% | 1.005 / 0.870 | 7,658.02 USD | yes |
| 20 | 5 | st_factor=2, trigger=trail, vol=atr_ratio:1.3, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 188.96 USD / -21,371.04 USD / -42,961.04 USD | 1,152 | 39.67% | 1.001 / 0.866 | 7,574.82 USD | yes |
| 21 | 2 | st_factor=2, trigger=trail, vol=none, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | -921.24 USD / -22,681.24 USD / -44,471.24 USD | 1,162 | 39.59% | 0.994 / 0.860 | 7,912.96 USD | yes |
| 22 | 6 | st_factor=2, trigger=trail, vol=rvi, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | -5,510.60 USD / -24,850.60 USD / -44,220.60 USD | 1,030 | 40.19% | 0.958 / 0.827 | 14,359.70 USD | yes |
| 23 | 11 | st_factor=2, trail_mult=1, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | -8,404.88 USD / -26,844.88 USD / -44,924.88 USD | 944 | 37.82% | 0.905 / 0.734 | 10,645.94 USD | yes |
| 24 | 3 | st_factor=2, trigger=trail, vol=stop_atr:1.5, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 173.72 USD / -46.28 USD / -266.28 USD | 14 | 35.71% | 1.169 / 0.962 | 968.14 USD | no |

Neighbour objective: median 6,533.57 USD, worst -26,844.88 USD, 16 of 24 above zero; winner 9,020.30 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 222 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 1.25, rvi_side <= 80 | 17,530.30 USD / 9,020.30 USD / 470.30 USD | 485 | 42.06% | 1.315 / 1.147 | 4,980.80 USD | yes |
| 2 | 206 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 10, risk_atr >= 1.75 | 14,545.76 USD / 8,805.76 USD / 3,065.76 USD | 312 | 45.51% | 1.415 / 1.228 | 2,882.56 USD | yes |
| 3 | 208 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 10, risk_atr >= 1.75 | 14,545.76 USD / 8,805.76 USD / 3,065.76 USD | 312 | 45.51% | 1.415 / 1.228 | 2,882.56 USD | yes |
| 4 | 211 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 10, risk_atr >= 1.75 | 14,545.76 USD / 8,805.76 USD / 3,065.76 USD | 312 | 45.51% | 1.415 / 1.228 | 2,882.56 USD | yes |
| 5 | 144 | st_factor=2, trigger=trail, risk_atr >= 1.75 | 16,599.14 USD / 8,709.14 USD / 779.14 USD | 443 | 41.99% | 1.320 / 1.153 | 4,836.78 USD | yes |
| 6 | 265 | st_factor=2, trigger=trail, atr_ratio <= 2, er <= 0.7, risk_atr >= 1.75 | 16,599.14 USD / 8,709.14 USD / 779.14 USD | 443 | 41.99% | 1.320 / 1.153 | 4,836.78 USD | yes |
| 7 | 266 | st_factor=2, trigger=trail, atr_ratio <= 2, er <= 0.7, risk_atr >= 1.75 | 16,599.14 USD / 8,709.14 USD / 779.14 USD | 443 | 41.99% | 1.320 / 1.153 | 4,836.78 USD | yes |
| 8 | 204 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 10, risk_atr >= 1.5 | 14,647.32 USD / 8,567.32 USD / 2,487.32 USD | 334 | 45.51% | 1.391 / 1.208 | 3,360.20 USD | yes |
| 9 | 259 | st_factor=2, trigger=st, er <= 0.7, hours_since_open >= 10, risk_atr >= 1 | 16,185.72 USD / 8,495.72 USD / 685.72 USD | 414 | 46.38% | 1.355 / 1.169 | 4,230.20 USD | yes |
| 10 | 103 | st_factor=2, trigger=st, er <= 0.65, risk_atr >= 1.75 | 17,743.82 USD / 8,443.82 USD / -1,086.18 USD | 509 | 44.40% | 1.302 / 1.131 | 4,381.00 USD | yes |
| 11 | 110 | st_factor=2, trigger=st, er <= 0.65, risk_atr >= 1.75 | 17,743.82 USD / 8,443.82 USD / -1,086.18 USD | 509 | 44.40% | 1.302 / 1.131 | 4,381.00 USD | yes |
| 12 | 227 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 2, rvi_side <= 75 | 15,380.24 USD / 8,400.24 USD / 1,420.24 USD | 388 | 42.53% | 1.335 / 1.166 | 4,480.70 USD | yes |
| 13 | 229 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 2, rvi_side <= 75 | 15,380.24 USD / 8,400.24 USD / 1,420.24 USD | 388 | 42.53% | 1.335 / 1.166 | 4,480.70 USD | yes |
| 14 | 230 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 8, risk_atr >= 2, rvi_side <= 75 | 15,380.24 USD / 8,400.24 USD / 1,420.24 USD | 388 | 42.53% | 1.335 / 1.166 | 4,480.70 USD | yes |
| 15 | 68 | st_factor=2, trigger=trail, risk_atr >= 1.25 | 16,830.20 USD / 8,220.20 USD / -429.80 USD | 490 | 41.84% | 1.298 / 1.132 | 5,014.82 USD | yes |
| 16 | 89 | st_factor=2, trigger=trail, er <= 0.8, risk_atr >= 1.25 | 16,830.20 USD / 8,220.20 USD / -429.80 USD | 490 | 41.84% | 1.298 / 1.132 | 5,014.82 USD | yes |
| 17 | 90 | st_factor=2, trigger=trail, er <= 0.8, risk_atr >= 1.25 | 16,830.20 USD / 8,220.20 USD / -429.80 USD | 490 | 41.84% | 1.298 / 1.132 | 5,014.82 USD | yes |
| 18 | 198 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 10, risk_atr >= 1.25 | 14,419.18 USD / 8,199.18 USD / 1,979.18 USD | 341 | 45.16% | 1.380 / 1.196 | 3,360.20 USD | yes |
| 19 | 202 | st_factor=2, trigger=trail, er <= 0.8, hours_since_open >= 10, risk_atr >= 1.25 | 14,419.18 USD / 8,199.18 USD / 1,979.18 USD | 341 | 45.16% | 1.380 / 1.196 | 3,360.20 USD | yes |
| 20 | 154 | st_factor=2, trigger=trail, risk_atr >= 1 | 16,622.06 USD / 7,912.06 USD / -837.94 USD | 497 | 41.65% | 1.291 / 1.126 | 5,014.82 USD | yes |

Eligible trials: 156 of 300. Trials with objective above zero: 78.

Raw files in `results/supertrend_kalman/search/london_full_tpe_net1_s1_n300/`: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
