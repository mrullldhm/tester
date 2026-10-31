# Search london_filters_random_net1_s1_n200

Generated 2026-10-31 13:18 UTC. Strategy `supertrend_kalman`, variant `london`, space `filters`, sampler `random`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 9 neighbours: 627 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 17,638.20 USD / 6,258.20 USD / -5,301.80 USD | 590 | 42.71% | 1.272 / 1.087 | 4,419.24 USD | yes |
| 2 | 117 | hours_since_open <= 21, risk_atr >= 1.5, rvi_side <= 75 | 20,149.30 USD / 9,689.30 USD / -950.70 USD | 535 | 43.74% | 1.347 / 1.151 | 4,103.16 USD | yes |

Frozen configuration: `strategies/configs/supertrend_kalman_london_filters_random_net1_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/supertrend_kalman_london_filters_random_net1_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | hours_since_open <= 21, risk_atr >= 1.75, rvi_side <= 75 | 20,181.76 USD / 10,061.76 USD / -238.24 USD | 512 | 44.14% | 1.366 / 1.165 | 4,619.14 USD | yes |
| 2 | 0 | risk_atr >= 1.5, rvi_side <= 75 | 20,149.30 USD / 9,689.30 USD / -950.70 USD | 535 | 43.74% | 1.347 / 1.151 | 4,103.16 USD | yes |
| 3 | 1 | hours_since_open <= 20, risk_atr >= 1.5, rvi_side <= 75 | 20,149.30 USD / 9,689.30 USD / -950.70 USD | 535 | 43.74% | 1.347 / 1.151 | 4,103.16 USD | yes |
| 4 | 2 | hours_since_open <= 22, risk_atr >= 1.5, rvi_side <= 75 | 20,149.30 USD / 9,689.30 USD / -950.70 USD | 535 | 43.74% | 1.347 / 1.151 | 4,103.16 USD | yes |
| 5 | 4 | hours_since_open <= 21, risk_atr >= 1.25, rvi_side <= 75 | 19,875.08 USD / 9,255.08 USD / -1,544.92 USD | 546 | 43.41% | 1.336 / 1.141 | 3,911.20 USD | yes |
| 6 | 3 | hours_since_open <= 21, rvi_side <= 75 | 19,478.90 USD / 8,738.90 USD / -2,181.10 USD | 555 | 43.24% | 1.325 / 1.132 | 3,974.42 USD | yes |
| 7 | 8 | hours_since_open <= 21, risk_atr >= 1.5, rvi_side <= 80 | 19,356.84 USD / 8,476.84 USD / -2,583.16 USD | 558 | 43.37% | 1.318 / 1.126 | 4,103.16 USD | yes |
| 8 | 7 | hours_since_open <= 21, risk_atr >= 1.5, rvi_side <= 70 | 16,611.00 USD / 7,671.00 USD / -1,099.00 USD | 450 | 44.44% | 1.336 / 1.140 | 3,532.46 USD | yes |
| 9 | 6 | hours_since_open <= 21, risk_atr >= 1.5 | 18,308.60 USD / 7,208.60 USD / -4,071.40 USD | 570 | 43.16% | 1.291 / 1.103 | 4,557.18 USD | yes |

Neighbour objective: median 9,255.08 USD, worst 7,208.60 USD, 9 of 9 above zero; winner 9,689.30 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 117 | hours_since_open <= 21, risk_atr >= 1.5, rvi_side <= 75 | 20,149.30 USD / 9,689.30 USD / -950.70 USD | 535 | 43.74% | 1.347 / 1.151 | 4,103.16 USD | yes |
| 2 | 15 | risk_atr >= 0.75, risk_ticks <= 135, rvi_side <= 70 | 17,784.72 USD / 8,664.72 USD / -285.28 USD | 464 | 44.18% | 1.360 / 1.158 | 3,200.30 USD | yes |
| 3 | 130 | hours_since_open <= 14, risk_ticks <= 145 | 19,356.24 USD / 8,016.24 USD / -3,503.76 USD | 588 | 42.86% | 1.306 / 1.114 | 4,419.24 USD | yes |
| 4 | 21 | er <= 0.65, hours_since_open >= 2, risk_ticks <= 110 | 18,954.28 USD / 7,654.28 USD / -3,825.72 USD | 586 | 42.66% | 1.300 / 1.109 | 4,419.24 USD | yes |
| 5 | 181 | risk_ticks <= 110 | 18,954.28 USD / 7,654.28 USD / -3,825.72 USD | 586 | 42.66% | 1.300 / 1.109 | 4,419.24 USD | yes |
| 6 | 64 | risk_atr >= 1.75 | 18,341.06 USD / 7,581.06 USD / -3,358.94 USD | 547 | 43.51% | 1.305 / 1.114 | 5,073.16 USD | yes |
| 7 | 140 | er <= 0.6, risk_atr <= 5, risk_ticks <= 200 | 18,902.22 USD / 7,542.22 USD / -3,997.78 USD | 589 | 42.78% | 1.297 / 1.107 | 4,419.24 USD | yes |
| 8 | 169 | risk_ticks <= 160 | 18,902.22 USD / 7,542.22 USD / -3,997.78 USD | 589 | 42.78% | 1.297 / 1.107 | 4,419.24 USD | yes |
| 9 | 9 | hours_since_open >= 6, risk_ticks <= 175, rvi_side <= 65 | 14,388.58 USD / 6,968.58 USD / -281.42 USD | 371 | 43.94% | 1.358 / 1.156 | 3,334.32 USD | yes |
| 10 | 55 | er <= 0.4, hours_since_open <= 17 | 17,846.44 USD / 6,666.44 USD / -4,693.56 USD | 578 | 42.73% | 1.281 / 1.095 | 4,057.18 USD | yes |
| 11 | 54 | hours_since_open <= 23, rvi_side >= 35 | 17,952.22 USD / 6,592.22 USD / -4,947.78 USD | 589 | 42.78% | 1.278 / 1.092 | 4,419.24 USD | yes |
| 12 | 114 | rvi_side >= 35 | 17,952.22 USD / 6,592.22 USD / -4,947.78 USD | 589 | 42.78% | 1.278 / 1.092 | 4,419.24 USD | yes |
| 13 | 182 | risk_atr <= 3.75, rvi_side >= 35 | 17,952.22 USD / 6,592.22 USD / -4,947.78 USD | 589 | 42.78% | 1.278 / 1.092 | 4,419.24 USD | yes |
| 14 | 0 | baseline | 17,638.20 USD / 6,258.20 USD / -5,301.80 USD | 590 | 42.71% | 1.272 / 1.087 | 4,419.24 USD | yes |
| 15 | 16 | hours_since_open >= 4 | 17,638.20 USD / 6,258.20 USD / -5,301.80 USD | 590 | 42.71% | 1.272 / 1.087 | 4,419.24 USD | yes |
| 16 | 19 | risk_atr <= 5 | 17,638.20 USD / 6,258.20 USD / -5,301.80 USD | 590 | 42.71% | 1.272 / 1.087 | 4,419.24 USD | yes |
| 17 | 23 | atr_ratio <= 1.6, hours_since_open <= 16 | 17,638.20 USD / 6,258.20 USD / -5,301.80 USD | 590 | 42.71% | 1.272 / 1.087 | 4,419.24 USD | yes |
| 18 | 43 | risk_atr <= 3.25, rvi_side >= 30 | 17,638.20 USD / 6,258.20 USD / -5,301.80 USD | 590 | 42.71% | 1.272 / 1.087 | 4,419.24 USD | yes |
| 19 | 58 | hours_since_open >= 5 | 17,638.20 USD / 6,258.20 USD / -5,301.80 USD | 590 | 42.71% | 1.272 / 1.087 | 4,419.24 USD | yes |
| 20 | 63 | atr_ratio <= 1.9 | 17,638.20 USD / 6,258.20 USD / -5,301.80 USD | 590 | 42.71% | 1.272 / 1.087 | 4,419.24 USD | yes |

Eligible trials: 47 of 200. Trials with objective above zero: 45.

Raw files in `results/supertrend_kalman/search/london_filters_random_net1_s1_n200/`: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
