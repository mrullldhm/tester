# Search entry_london_filters_random_net0_s1_n200_fix_session_reentry

Generated 2026-11-11 20:26 UTC. Strategy `price_reversal_v2`, variant `entry_london`, space `filters`, sampler `random`, seed 1, objective `net0` (net profit + open P&L without added slippage), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 6 neighbours: 206 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 11,174.58 USD | 1,571 | 35.77% | 1.086 | 7,849.10 USD | yes |
| 2 | 168 | anchor_body_atr <= 1.9, risk_ticks <= 20 | 13,867.02 USD | 1,349 | 36.55% | 1.153 | 3,727.42 USD | yes |

Frozen configuration: `strategies/configs/price_reversal_v2_entry_london_filters_random_net0_s1_n200_fix_session_reentry.json`. Replay it with `python -m tvtester.cli replay strategies/configs/price_reversal_v2_entry_london_filters_random_net0_s1_n200_fix_session_reentry.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 | anchor_body_atr <= 1.9, risk_ticks <= 18 | 16,604.10 USD | 1,295 | 37.07% | 1.200 | 3,404.54 USD | yes |
| 2 | 2 | anchor_body_atr <= 2, risk_ticks <= 20 | 14,084.76 USD | 1,362 | 36.49% | 1.154 | 3,782.40 USD | yes |
| 3 | 1 | anchor_body_atr <= 1.8, risk_ticks <= 20 | 14,027.12 USD | 1,344 | 36.61% | 1.155 | 3,519.38 USD | yes |
| 4 | 5 | anchor_body_atr <= 1.9, risk_ticks <= 22 | 13,742.40 USD | 1,380 | 36.45% | 1.144 | 4,401.54 USD | yes |
| 5 | 0 | risk_ticks <= 20 | 13,346.22 USD | 1,389 | 36.29% | 1.142 | 4,280.56 USD | yes |
| 6 | 3 | anchor_body_atr <= 1.9 | 12,403.42 USD | 1,529 | 36.04% | 1.099 | 7,295.96 USD | yes |

Neighbour objective: median 13,884.76 USD, worst 12,403.42 USD, 6 of 6 above zero; winner 13,867.02 USD.

## Top 20 trials

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 168 | anchor_body_atr <= 1.9, risk_ticks <= 20 | 13,867.02 USD | 1,349 | 36.55% | 1.153 | 3,727.42 USD | yes |
| 2 | 146 | anchor_body_atr <= 1.5 | 13,244.62 USD | 1,469 | 36.28% | 1.110 | 6,395.76 USD | yes |
| 3 | 191 | anchor_body_atr <= 1.6 | 13,200.20 USD | 1,490 | 36.24% | 1.108 | 6,598.02 USD | yes |
| 4 | 158 | anchor_body_atr <= 2, range_ratio <= 1.6, risk_ticks <= 58 | 13,178.08 USD | 1,396 | 36.39% | 1.120 | 8,252.02 USD | yes |
| 5 | 18 | range_ratio >= 0.7 | 13,037.56 USD | 1,222 | 36.50% | 1.129 | 6,020.92 USD | yes |
| 6 | 20 | anchor_body_atr <= 1.4 | 12,911.40 USD | 1,430 | 36.01% | 1.110 | 6,675.82 USD | yes |
| 7 | 144 | minutes_from_open <= 45, risk_ticks <= 16 | 12,711.28 USD | 1,236 | 36.49% | 1.168 | 3,492.30 USD | yes |
| 8 | 185 | anchor_body_atr <= 1.3, risk_atr <= 5.25, risk_ticks <= 36 | 12,240.74 USD | 1,363 | 35.80% | 1.116 | 4,445.62 USD | yes |
| 9 | 34 | minutes_from_open <= 95, risk_atr >= 1.75 | 11,787.28 USD | 1,436 | 36.14% | 1.097 | 7,260.26 USD | yes |
| 10 | 70 | minutes_from_open <= 50, range_ratio <= 1.9 | 11,422.16 USD | 1,492 | 35.92% | 1.095 | 9,194.58 USD | yes |
| 11 | 115 | minutes_from_open <= 80, range_ratio <= 1.9 | 11,422.16 USD | 1,492 | 35.92% | 1.095 | 9,194.58 USD | yes |
| 12 | 8 | risk_ticks <= 52 | 11,312.72 USD | 1,564 | 35.81% | 1.089 | 6,337.04 USD | yes |
| 13 | 164 | risk_atr >= 2 | 11,242.64 USD | 1,268 | 36.67% | 1.102 | 7,573.06 USD | yes |
| 14 | 92 | risk_ticks <= 38 | 11,203.12 USD | 1,544 | 35.82% | 1.092 | 5,381.36 USD | yes |
| 15 | 0 | baseline | 11,174.58 USD | 1,571 | 35.77% | 1.086 | 7,849.10 USD | yes |
| 16 | 22 | minutes_from_open <= 115 | 11,174.58 USD | 1,571 | 35.77% | 1.086 | 7,849.10 USD | yes |
| 17 | 95 | minutes_from_open <= 30 | 11,174.58 USD | 1,571 | 35.77% | 1.086 | 7,849.10 USD | yes |
| 18 | 161 | risk_atr >= 1 | 11,174.58 USD | 1,571 | 35.77% | 1.086 | 7,849.10 USD | yes |
| 19 | 177 | minutes_from_open <= 110 | 11,174.58 USD | 1,571 | 35.77% | 1.086 | 7,849.10 USD | yes |
| 20 | 73 | risk_atr <= 5.75, risk_ticks >= 8 | 11,173.54 USD | 1,223 | 36.71% | 1.098 | 7,450.82 USD | yes |

Eligible trials: 80 of 200. Trials with objective above zero: 77.

Raw files in `results/price_reversal_v2/search/entry_london_filters_random_net0_s1_n200_fix_session_reentry/`: `trials.csv` (every trial, baseline metrics), `neighbours.csv`, `run.json` (space, hashes, versions).
