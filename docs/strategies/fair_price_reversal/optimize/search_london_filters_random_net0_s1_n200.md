# Search london_filters_random_net0_s1_n200

Generated 2026-11-04 14:00 UTC. Strategy `fair_price_reversal`, variant `london`, space `filters`, sampler `random`, seed 1, objective `net0` (net profit + open P&L without added slippage), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 6 neighbours: 206 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 11,237.30 USD | 1,635 | 35.84% | 1.086 | 7,901.56 USD | yes |
| 2 | 168 | anchor_body_atr <= 1.9, risk_ticks <= 20 | 15,599.54 USD | 1,423 | 36.54% | 1.166 | 4,338.58 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_london_filters_random_net0_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_london_filters_random_net0_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 | anchor_body_atr <= 1.9, risk_ticks <= 18 | 17,778.68 USD | 1,366 | 36.97% | 1.207 | 4,144.56 USD | yes |
| 2 | 2 | anchor_body_atr <= 2, risk_ticks <= 20 | 15,817.28 USD | 1,436 | 36.49% | 1.167 | 4,640.64 USD | yes |
| 3 | 1 | anchor_body_atr <= 1.8, risk_ticks <= 20 | 15,759.64 USD | 1,418 | 36.60% | 1.169 | 4,338.58 USD | yes |
| 4 | 5 | anchor_body_atr <= 1.9, risk_ticks <= 22 | 15,484.92 USD | 1,454 | 36.45% | 1.157 | 4,338.58 USD | yes |
| 5 | 0 | risk_ticks <= 20 | 14,922.76 USD | 1,462 | 36.32% | 1.154 | 4,578.68 USD | yes |
| 6 | 3 | anchor_body_atr <= 1.9 | 11,828.10 USD | 1,595 | 35.99% | 1.092 | 7,363.32 USD | yes |

Neighbour objective: median 15,622.28 USD, worst 11,828.10 USD, 6 of 6 above zero; winner 15,599.54 USD.

## Top 20 trials

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 168 | anchor_body_atr <= 1.9, risk_ticks <= 20 | 15,599.54 USD | 1,423 | 36.54% | 1.166 | 4,338.58 USD | yes |
| 2 | 158 | anchor_body_atr <= 2, range_ratio <= 1.6, risk_ticks <= 58 | 14,112.86 USD | 1,457 | 36.38% | 1.127 | 8,402.52 USD | yes |
| 3 | 18 | range_ratio >= 0.7 | 13,570.58 USD | 1,271 | 36.74% | 1.134 | 5,800.92 USD | yes |
| 4 | 144 | minutes_from_open <= 45, risk_ticks <= 16 | 13,037.92 USD | 1,304 | 36.35% | 1.166 | 4,220.64 USD | yes |
| 5 | 73 | risk_atr <= 5.75, risk_ticks >= 8 | 12,849.12 USD | 1,244 | 37.22% | 1.112 | 6,841.10 USD | yes |
| 6 | 191 | anchor_body_atr <= 1.6 | 12,798.90 USD | 1,555 | 36.21% | 1.103 | 6,493.12 USD | yes |
| 7 | 34 | minutes_from_open <= 95, risk_atr >= 1.75 | 12,792.46 USD | 1,477 | 36.49% | 1.105 | 6,918.50 USD | yes |
| 8 | 185 | anchor_body_atr <= 1.3, risk_atr <= 5.25, risk_ticks <= 36 | 12,683.46 USD | 1,427 | 35.81% | 1.117 | 4,348.38 USD | yes |
| 9 | 146 | anchor_body_atr <= 1.5 | 12,651.36 USD | 1,532 | 36.23% | 1.103 | 6,430.96 USD | yes |
| 10 | 25 | minutes_from_open >= 15, range_ratio <= 1.4 | 12,165.82 USD | 909 | 38.61% | 1.173 | 5,613.54 USD | yes |
| 11 | 179 | minutes_from_open <= 65, risk_atr >= 1.75, risk_ticks <= 44 | 12,164.72 USD | 1,464 | 36.41% | 1.103 | 6,543.86 USD | yes |
| 12 | 70 | minutes_from_open <= 50, range_ratio <= 1.9 | 11,812.92 USD | 1,554 | 36.10% | 1.098 | 9,351.06 USD | yes |
| 13 | 115 | minutes_from_open <= 80, range_ratio <= 1.9 | 11,812.92 USD | 1,554 | 36.10% | 1.098 | 9,351.06 USD | yes |
| 14 | 169 | range_ratio <= 1.5 | 11,755.32 USD | 1,434 | 36.40% | 1.106 | 8,680.26 USD | yes |
| 15 | 138 | minutes_from_open <= 60, range_ratio <= 1.9, risk_atr <= 6 | 11,749.10 USD | 1,545 | 35.92% | 1.098 | 9,277.04 USD | yes |
| 16 | 20 | anchor_body_atr <= 1.4 | 11,658.14 USD | 1,493 | 35.90% | 1.097 | 6,419.84 USD | yes |
| 17 | 164 | risk_atr >= 2 | 11,578.22 USD | 1,289 | 37.01% | 1.105 | 7,979.04 USD | yes |
| 18 | 10 | risk_atr <= 5.5, risk_ticks <= 42 | 11,413.78 USD | 1,611 | 35.69% | 1.091 | 5,366.02 USD | yes |
| 19 | 92 | risk_ticks <= 38 | 11,391.82 USD | 1,609 | 35.80% | 1.092 | 5,721.56 USD | yes |
| 20 | 0 | baseline | 11,237.30 USD | 1,635 | 35.84% | 1.086 | 7,901.56 USD | yes |

Eligible trials: 81 of 200. Trials with objective above zero: 78.

Raw files in `results/fair_price_reversal/search/london_filters_random_net0_s1_n200/`: `trials.csv` (every trial, baseline metrics), `neighbours.csv`, `run.json` (space, hashes, versions).
