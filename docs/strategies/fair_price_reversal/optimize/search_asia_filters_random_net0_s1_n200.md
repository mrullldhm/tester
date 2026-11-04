# Search asia_filters_random_net0_s1_n200

Generated 2026-11-04 14:00 UTC. Strategy `fair_price_reversal`, variant `asia`, space `filters`, sampler `random`, seed 1, objective `net0` (net profit + open P&L without added slippage), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 6 neighbours: 206 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | -1,376.20 USD | 1,310 | 32.67% | 0.985 | 8,097.82 USD | yes |
| 2 | 67 | anchor_body_atr <= 0.7, range_ratio >= 0.8 | 5,038.40 USD | 580 | 34.31% | 1.123 | 3,631.80 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_asia_filters_random_net0_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_asia_filters_random_net0_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 | anchor_body_atr <= 0.7, range_ratio >= 0.7 | 6,870.02 USD | 699 | 34.76% | 1.144 | 3,100.90 USD | yes |
| 2 | 2 | anchor_body_atr <= 0.8, range_ratio >= 0.8 | 5,365.54 USD | 623 | 34.19% | 1.124 | 4,173.96 USD | yes |
| 3 | 1 | anchor_body_atr <= 0.6, range_ratio >= 0.8 | 4,891.46 USD | 527 | 34.91% | 1.130 | 3,727.48 USD | yes |
| 4 | 3 | anchor_body_atr <= 0.7 | 4,230.14 USD | 893 | 34.60% | 1.070 | 5,167.08 USD | yes |
| 5 | 5 | anchor_body_atr <= 0.7, range_ratio >= 0.9 | 3,976.48 USD | 476 | 34.45% | 1.115 | 3,007.38 USD | yes |
| 6 | 0 | range_ratio >= 0.8 | 1,180.74 USD | 863 | 32.79% | 1.018 | 6,084.36 USD | yes |

Neighbour objective: median 4,560.80 USD, worst 1,180.74 USD, 6 of 6 above zero; winner 5,038.40 USD.

## Top 20 trials

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 67 | anchor_body_atr <= 0.7, range_ratio >= 0.8 | 5,038.40 USD | 580 | 34.31% | 1.123 | 3,631.80 USD | yes |
| 2 | 192 | range_ratio >= 1.1 | 3,905.42 USD | 429 | 34.50% | 1.113 | 2,973.34 USD | yes |
| 3 | 155 | anchor_body_atr <= 0.8 | 3,708.84 USD | 958 | 34.24% | 1.057 | 5,517.02 USD | yes |
| 4 | 87 | anchor_body_atr <= 0.6, minutes_from_open <= 45 | 3,495.76 USD | 812 | 34.61% | 1.062 | 5,664.46 USD | yes |
| 5 | 47 | anchor_body_atr <= 1.2 | 3,167.10 USD | 1,145 | 33.71% | 1.041 | 5,823.50 USD | yes |
| 6 | 48 | minutes_from_open >= 15 | 3,010.44 USD | 878 | 32.57% | 1.050 | 6,678.24 USD | yes |
| 7 | 18 | range_ratio >= 0.7 | 2,037.54 USD | 1,023 | 33.04% | 1.028 | 6,094.86 USD | yes |
| 8 | 128 | anchor_body_atr <= 0.7, minutes_from_open >= 15, range_ratio >= 0.9, risk_ticks <= 48 | 1,671.74 USD | 313 | 34.82% | 1.079 | 2,427.72 USD | yes |
| 9 | 78 | range_ratio >= 0.6, risk_atr >= 2.5, risk_ticks >= 8 | 1,462.76 USD | 462 | 33.33% | 1.032 | 5,303.34 USD | yes |
| 10 | 157 | anchor_body_atr <= 0.4, risk_ticks <= 42 | 1,304.28 USD | 586 | 34.13% | 1.035 | 4,102.78 USD | yes |
| 11 | 71 | range_ratio >= 0.9 | 1,191.98 USD | 701 | 33.52% | 1.022 | 4,396.12 USD | yes |
| 12 | 79 | anchor_body_atr <= 0.3, range_ratio <= 2, risk_ticks <= 38 | 1,080.30 USD | 485 | 35.05% | 1.037 | 4,926.48 USD | yes |
| 13 | 64 | anchor_body_atr <= 0.1, risk_atr <= 4.25 | 770.44 USD | 378 | 33.60% | 1.037 | 2,012.64 USD | yes |
| 14 | 195 | range_ratio >= 0.7, risk_atr <= 4.25 | 707.18 USD | 941 | 32.31% | 1.011 | 6,698.78 USD | yes |
| 15 | 170 | range_ratio >= 0.9, risk_atr <= 5.75 | 634.24 USD | 688 | 33.28% | 1.012 | 4,872.10 USD | yes |
| 16 | 1 | anchor_body_atr <= 0.1, risk_ticks <= 14 | 556.52 USD | 374 | 33.69% | 1.033 | 2,554.60 USD | yes |
| 17 | 20 | anchor_body_atr <= 1.4 | 530.22 USD | 1,189 | 33.14% | 1.006 | 7,425.46 USD | yes |
| 18 | 146 | anchor_body_atr <= 1.5 | -474.40 USD | 1,220 | 32.87% | 0.994 | 7,347.52 USD | yes |
| 19 | 73 | risk_atr <= 5.75, risk_ticks >= 8 | -516.76 USD | 738 | 33.60% | 0.993 | 7,857.22 USD | yes |
| 20 | 70 | minutes_from_open <= 50, range_ratio <= 1.9 | -623.04 USD | 1,252 | 32.67% | 0.993 | 8,433.80 USD | yes |

Eligible trials: 74 of 200. Trials with objective above zero: 17.

Raw files in `results/fair_price_reversal/search/asia_filters_random_net0_s1_n200/`: `trials.csv` (every trial, baseline metrics), `neighbours.csv`, `run.json` (space, hashes, versions).
