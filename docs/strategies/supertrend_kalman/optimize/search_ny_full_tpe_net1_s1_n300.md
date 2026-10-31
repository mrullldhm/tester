# Search ny_full_tpe_net1_s1_n300

Generated 2026-10-31 14:02 UTC. Strategy `supertrend_kalman`, variant `ny`, space `full`, sampler `tpe`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 300 trials (33 duplicates) and 20 neighbours: 861 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 2 | 121 | hours_since_open >= 1, risk_atr >= 2 | 109,927.48 USD / 62,427.48 USD / 14,937.48 USD | 2,426 | 45.26% | 1.187 / 1.102 | 14,056.12 USD | yes |

Frozen configuration: `strategies/configs/supertrend_kalman_ny_full_tpe_net1_s1_n300.json`. Replay it with `python -m tvtester.cli replay strategies/configs/supertrend_kalman_ny_full_tpe_net1_s1_n300.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 14 | risk_atr >= 2 | 109,927.48 USD / 62,427.48 USD / 14,937.48 USD | 2,426 | 45.26% | 1.187 / 1.102 | 14,056.12 USD | yes |
| 2 | 15 | hours_since_open >= 0, risk_atr >= 2 | 109,927.48 USD / 62,427.48 USD / 14,937.48 USD | 2,426 | 45.26% | 1.187 / 1.102 | 14,056.12 USD | yes |
| 3 | 16 | hours_since_open >= 2, risk_atr >= 2 | 109,927.48 USD / 62,427.48 USD / 14,937.48 USD | 2,426 | 45.26% | 1.187 / 1.102 | 14,056.12 USD | yes |
| 4 | 9 | rr=2, hours_since_open >= 1, risk_atr >= 2 | 105,387.18 USD / 59,531.20 USD / 12,895.22 USD | 2,441 | 45.43% | 1.179 / 1.097 | 14,456.12 USD | yes |
| 5 | 18 | hours_since_open >= 1, risk_atr >= 1.75 | 103,449.70 USD / 54,329.70 USD / 5,219.70 USD | 2,515 | 44.77% | 1.170 / 1.085 | 13,216.32 USD | yes |
| 6 | 17 | hours_since_open >= 1 | 104,105.44 USD / 53,025.44 USD / 1,955.44 USD | 2,628 | 44.18% | 1.165 / 1.080 | 15,000.94 USD | yes |
| 7 | 2 | vol=none, hours_since_open >= 1, risk_atr >= 2 | 103,877.76 USD / 50,717.76 USD / -2,432.24 USD | 2,712 | 44.95% | 1.155 / 1.072 | 16,060.34 USD | yes |
| 8 | 7 | exit=fixed, hours_since_open >= 1, risk_atr >= 2 | 96,091.24 USD / 50,351.24 USD / 4,621.24 USD | 2,338 | 48.33% | 1.153 / 1.077 | 16,814.26 USD | yes |
| 9 | 19 | hours_since_open >= 1, risk_atr >= 2.25 | 95,169.78 USD / 49,729.78 USD / 4,299.78 USD | 2,311 | 45.05% | 1.168 / 1.084 | 14,661.08 USD | yes |
| 10 | 10 | swing=3, hours_since_open >= 1, risk_atr >= 2 | 81,489.22 USD / 38,319.22 USD / -5,300.78 USD | 2,239 | 44.93% | 1.146 / 1.066 | 14,755.52 USD | yes |
| 11 | 1 | trigger=trail, hours_since_open >= 1, risk_atr >= 2 | 64,004.94 USD / 31,464.94 USD / -1,065.06 USD | 1,653 | 44.16% | 1.157 / 1.074 | 14,560.84 USD | yes |
| 12 | 6 | vol=atr_ratio:1.3, hours_since_open >= 1, risk_atr >= 2 | 58,407.98 USD / 31,287.98 USD / 4,177.98 USD | 1,401 | 41.97% | 1.157 / 1.081 | 20,654.76 USD | yes |
| 13 | 11 | trail_mult=2, hours_since_open >= 1, risk_atr >= 2 | 51,321.44 USD / 25,521.44 USD / -278.56 USD | 1,328 | 45.93% | 1.155 / 1.074 | 14,425.92 USD | yes |
| 14 | 0 | trigger=st, hours_since_open >= 1, risk_atr >= 2 | 46,599.36 USD / 24,619.36 USD / 2,639.36 USD | 1,132 | 46.20% | 1.170 / 1.086 | 12,629.54 USD | yes |
| 15 | 13 | kalman_q=0.01, hours_since_open >= 1, risk_atr >= 2 | 87,445.96 USD / 22,465.96 USD / -42,554.04 USD | 3,302 | 44.25% | 1.105 / 1.026 | 24,075.84 USD | yes |
| 16 | 4 | vol=stop_atr:3, hours_since_open >= 1, risk_atr >= 2 | 27,965.92 USD / 10,265.92 USD / -7,034.08 USD | 904 | 45.35% | 1.130 / 1.045 | 14,404.82 USD | yes |
| 17 | 8 | exit=trail, hours_since_open >= 1, risk_atr >= 2 | 60,389.78 USD / 4,729.78 USD / -50,930.22 USD | 2,811 | 38.49% | 1.137 / 1.010 | 15,488.78 USD | yes |
| 18 | 12 | st_factor=3, hours_since_open >= 1, risk_atr >= 2 | 50,969.10 USD / 679.10 USD / -52,930.90 USD | 2,545 | 45.19% | 1.072 / 1.001 | 27,875.12 USD | yes |
| 19 | 3 | vol=stop_atr:1.5, hours_since_open >= 1, risk_atr >= 2 | 0.00 USD / 0.00 USD / 0.00 USD | 0 | — | — / — | 0.00 USD | no |
| 20 | 5 | vol=atr_ratio:1.0, hours_since_open >= 1, risk_atr >= 2 | 2,460.72 USD / -1,119.28 USD / -4,299.28 USD | 164 | 36.59% | 1.065 / 0.972 | 6,626.42 USD | no |

Neighbour objective: median 34,892.08 USD, worst -1,119.28 USD, 18 of 20 above zero; winner 62,427.48 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 121 | hours_since_open >= 1, risk_atr >= 2 | 109,927.48 USD / 62,427.48 USD / 14,937.48 USD | 2,426 | 45.26% | 1.187 / 1.102 | 14,056.12 USD | yes |
| 2 | 122 | hours_since_open >= 0, risk_atr >= 2 | 109,927.48 USD / 62,427.48 USD / 14,937.48 USD | 2,426 | 45.26% | 1.187 / 1.102 | 14,056.12 USD | yes |
| 3 | 299 | rr=2, atr_ratio >= 0.6, hours_since_open >= 10, risk_ticks >= 60 | 95,588.44 USD / 57,648.44 USD / 18,548.44 USD | 1,978 | 46.61% | 1.188 / 1.109 | 14,202.00 USD | yes |
| 4 | 295 | rr=2, atr_ratio >= 0.6, hours_since_open >= 10, risk_ticks >= 65 | 92,910.94 USD / 57,210.94 USD / 20,350.94 USD | 1,853 | 46.95% | 1.192 / 1.114 | 15,152.52 USD | yes |
| 5 | 150 | atr_ratio >= 0.9 | 104,212.32 USD / 54,392.32 USD / 4,182.32 USD | 2,584 | 44.50% | 1.167 / 1.083 | 14,796.72 USD | yes |
| 6 | 257 | atr_ratio >= 0.6, hours_since_open >= 0 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 7 | 261 | atr_ratio >= 0.6, hours_since_open >= 0 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 8 | 263 | atr_ratio >= 0.6, hours_since_open >= 0 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 9 | 264 | atr_ratio >= 0.6, hours_since_open >= 3 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 10 | 266 | atr_ratio >= 0.6, hours_since_open >= 3 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 11 | 269 | atr_ratio >= 0.6, hours_since_open >= 2 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 12 | 271 | atr_ratio >= 0.6, hours_since_open >= 4 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 13 | 272 | atr_ratio >= 0.6, hours_since_open >= 4 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 14 | 274 | atr_ratio >= 0.6, hours_since_open >= 5 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 15 | 276 | atr_ratio >= 0.6, hours_since_open >= 6 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 16 | 278 | atr_ratio >= 0.6, hours_since_open >= 6 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 17 | 281 | atr_ratio >= 0.6, hours_since_open >= 8 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 18 | 282 | atr_ratio >= 0.6, hours_since_open >= 8 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 19 | 284 | atr_ratio >= 0.6, hours_since_open >= 8 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |
| 20 | 286 | atr_ratio >= 0.6, hours_since_open >= 7 | 104,707.50 USD / 53,687.50 USD / 2,677.50 USD | 2,625 | 44.19% | 1.166 / 1.081 | 15,168.78 USD | yes |

Eligible trials: 195 of 300. Trials with objective above zero: 155.

Raw files in `results/supertrend_kalman/search/ny_full_tpe_net1_s1_n300/`: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
