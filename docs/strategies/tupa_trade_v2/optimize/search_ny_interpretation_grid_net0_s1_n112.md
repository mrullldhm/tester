# Search ny_interpretation_grid_net0_s1_n112

Generated 2026-11-12 00:56 UTC. Strategy `tupa_trade_v2`, variant `ny`, space `interpretation`, sampler `grid`, seed 1, objective `net0` (net profit + open P&L without added slippage), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 112 trials (0 duplicates) and 7 neighbours: 119 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | -9,262.62 USD | 431 | 29.93% | 0.771 | 10,126.24 USD | yes |
| 2 | 94 | t_min=4h, t_rule=highest, touched=retest, tp_expiry=off, trend=fresh | -1,956.10 USD | 305 | 31.80% | 0.923 | 4,812.30 USD | yes |

Frozen configuration: `strategies/configs/tupa_trade_v2_ny_interpretation_grid_net0_s1_n112.json`. Replay it with `python -m tvtester.cli replay strategies/configs/tupa_trade_v2_ny_interpretation_grid_net0_s1_n112.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | order=freeze, t_min=4h, t_rule=highest, touched=retest, tp_expiry=off, trend=fresh | -2,330.62 USD | 331 | 31.72% | 0.916 | 5,807.16 USD | yes |
| 2 | 2 | t_min=4h, touched=retest, tp_expiry=off, trend=fresh | -2,569.56 USD | 378 | 31.48% | 0.918 | 6,112.80 USD | yes |
| 3 | 6 | t_min=4h, t_rule=highest, touched=retest, trend=fresh | -2,798.06 USD | 303 | 31.02% | 0.890 | 4,812.30 USD | yes |
| 4 | 1 | t_min=1h, t_rule=highest, touched=retest, tp_expiry=off, trend=fresh | -3,593.34 USD | 767 | 30.25% | 0.939 | 10,048.88 USD | yes |
| 5 | 0 | t_min=15m, t_rule=highest, touched=retest, tp_expiry=off, trend=fresh | -10,208.70 USD | 1,435 | 30.38% | 0.910 | 12,137.62 USD | yes |
| 6 | 3 | t_min=4h, t_rule=highest, touched=retest, tp_expiry=off | -15,641.00 USD | 1,050 | 29.14% | 0.823 | 15,980.90 USD | yes |
| 7 | 4 | t_min=4h, t_rule=highest, tp_expiry=off, trend=fresh | -2,389.58 USD | 179 | 32.40% | 0.853 | 4,131.30 USD | no |

Neighbour objective: median -2,798.06 USD, worst -15,641.00 USD, 0 of 7 above zero; winner -1,956.10 USD.

## Top 20 trials

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 94 | t_min=4h, t_rule=highest, touched=retest, tp_expiry=off, trend=fresh | -1,956.10 USD | 305 | 31.80% | 0.923 | 4,812.30 USD | yes |
| 2 | 96 | order=freeze, t_min=4h, t_rule=highest, touched=retest, tp_expiry=off, trend=fresh | -2,330.62 USD | 331 | 31.72% | 0.916 | 5,807.16 USD | yes |
| 3 | 78 | t_min=4h, touched=retest, tp_expiry=off, trend=fresh | -2,569.56 USD | 378 | 31.48% | 0.918 | 6,112.80 USD | yes |
| 4 | 93 | t_min=4h, t_rule=highest, touched=retest, trend=fresh | -2,798.06 USD | 303 | 31.02% | 0.890 | 4,812.30 USD | yes |
| 5 | 95 | order=freeze, t_min=4h, t_rule=highest, touched=retest, trend=fresh | -3,172.58 USD | 329 | 31.00% | 0.887 | 6,157.16 USD | yes |
| 6 | 80 | order=freeze, t_min=4h, touched=retest, tp_expiry=off, trend=fresh | -3,516.24 USD | 412 | 31.31% | 0.899 | 7,860.52 USD | yes |
| 7 | 62 | t_min=1h, t_rule=highest, touched=retest, tp_expiry=off, trend=fresh | -3,593.34 USD | 767 | 30.25% | 0.939 | 10,048.88 USD | yes |
| 8 | 77 | t_min=4h, touched=retest, trend=fresh | -3,623.48 USD | 374 | 30.75% | 0.885 | 6,444.44 USD | yes |
| 9 | 61 | t_min=1h, t_rule=highest, touched=retest, trend=fresh | -4,109.22 USD | 761 | 29.96% | 0.929 | 10,080.84 USD | yes |
| 10 | 79 | order=freeze, t_min=4h, touched=retest, trend=fresh | -4,570.16 USD | 408 | 30.64% | 0.870 | 8,422.48 USD | yes |
| 11 | 59 | order=freeze, t_min=1h, t_rule=highest, trend=fresh | -4,969.04 USD | 552 | 32.25% | 0.893 | 8,400.08 USD | yes |
| 12 | 26 | t_min=15m, t_rule=highest, tp_expiry=off, trend=fresh | -5,088.46 USD | 823 | 33.17% | 0.926 | 7,903.44 USD | yes |
| 13 | 64 | order=freeze, t_min=1h, t_rule=highest, touched=retest, tp_expiry=off, trend=fresh | -5,171.12 USD | 856 | 30.84% | 0.923 | 12,174.30 USD | yes |
| 14 | 63 | order=freeze, t_min=1h, t_rule=highest, touched=retest, trend=fresh | -5,178.96 USD | 848 | 30.66% | 0.922 | 12,206.26 USD | yes |
| 15 | 60 | order=freeze, t_min=1h, t_rule=highest, tp_expiry=off, trend=fresh | -5,231.10 USD | 555 | 32.25% | 0.889 | 8,654.10 USD | yes |
| 16 | 100 | touched=retest | -5,423.36 USD | 568 | 29.75% | 0.883 | 6,306.28 USD | yes |
| 17 | 25 | t_min=15m, t_rule=highest, trend=fresh | -5,548.26 USD | 813 | 32.84% | 0.918 | 8,141.38 USD | yes |
| 18 | 5 | t_min=15m, touched=retest | -6,228.70 USD | 3,435 | 32.55% | 0.978 | 23,183.02 USD | yes |
| 19 | 101 | touched=retest, tp_expiry=off | -6,281.40 USD | 570 | 29.47% | 0.866 | 6,736.88 USD | yes |
| 20 | 6 | t_min=15m, touched=retest, tp_expiry=off | -6,302.82 USD | 3,441 | 32.64% | 0.978 | 23,233.02 USD | yes |

Eligible trials: 96 of 112. Trials with objective above zero: 0.

Raw files in `results/tupa_trade_v2/search/ny_interpretation_grid_net0_s1_n112/`: `trials.csv` (every trial, baseline metrics), `neighbours.csv`, `run.json` (space, hashes, versions).
