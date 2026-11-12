# Search h02_filters_random_net0_s1_n200

Generated 2026-11-11 20:24 UTC. Strategy `price_reversal_v2`, variant `h02`, space `filters`, sampler `random`, seed 1, objective `net0` (net profit + open P&L without added slippage), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 6 neighbours: 206 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 8,565.26 USD | 1,837 | 51.99% | 1.136 | 5,247.46 USD | yes |
| 2 | 70 | minutes_from_open <= 50, range_ratio <= 1.9 | 11,056.48 USD | 1,476 | 52.85% | 1.236 | 3,288.52 USD | yes |

Frozen configuration: `strategies/configs/price_reversal_v2_h02_filters_random_net0_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/price_reversal_v2_h02_filters_random_net0_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | minutes_from_open <= 50, range_ratio <= 2 | 11,234.22 USD | 1,489 | 52.92% | 1.238 | 3,766.56 USD | yes |
| 2 | 3 | minutes_from_open <= 50 | 10,896.74 USD | 1,563 | 52.85% | 1.208 | 4,724.80 USD | yes |
| 3 | 1 | minutes_from_open <= 45, range_ratio <= 1.9 | 10,483.20 USD | 1,340 | 53.73% | 1.249 | 2,968.22 USD | yes |
| 4 | 2 | minutes_from_open <= 55, range_ratio <= 1.9 | 10,023.58 USD | 1,621 | 52.13% | 1.191 | 3,916.86 USD | yes |
| 5 | 4 | minutes_from_open <= 50, range_ratio <= 1.8 | 9,506.88 USD | 1,456 | 52.47% | 1.204 | 3,548.62 USD | yes |
| 6 | 0 | range_ratio <= 1.9 | 9,145.20 USD | 1,740 | 52.01% | 1.161 | 3,779.12 USD | yes |

Neighbour objective: median 10,253.39 USD, worst 9,145.20 USD, 6 of 6 above zero; winner 11,056.48 USD.

## Top 20 trials

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 70 | minutes_from_open <= 50, range_ratio <= 1.9 | 11,056.48 USD | 1,476 | 52.85% | 1.236 | 3,288.52 USD | yes |
| 2 | 185 | anchor_body_atr <= 1.3, risk_atr <= 5.25, risk_ticks <= 36 | 10,381.82 USD | 1,609 | 52.14% | 1.206 | 2,680.48 USD | yes |
| 3 | 92 | risk_ticks <= 38 | 9,877.52 USD | 1,824 | 52.03% | 1.166 | 3,763.24 USD | yes |
| 4 | 73 | risk_atr <= 5.75, risk_ticks >= 8 | 9,867.40 USD | 630 | 58.25% | 1.300 | 3,379.84 USD | yes |
| 5 | 10 | risk_atr <= 5.5, risk_ticks <= 42 | 9,475.00 USD | 1,750 | 51.60% | 1.166 | 3,891.18 USD | yes |
| 6 | 47 | anchor_body_atr <= 1.2 | 9,324.24 USD | 1,688 | 53.02% | 1.166 | 4,390.98 USD | yes |
| 7 | 146 | anchor_body_atr <= 1.5 | 9,302.84 USD | 1,758 | 52.50% | 1.158 | 4,733.24 USD | yes |
| 8 | 115 | minutes_from_open <= 80, range_ratio <= 1.9 | 9,145.20 USD | 1,740 | 52.01% | 1.161 | 3,779.12 USD | yes |
| 9 | 59 | risk_atr <= 5.25, risk_ticks <= 32 | 9,081.58 USD | 1,721 | 51.31% | 1.165 | 3,360.78 USD | yes |
| 10 | 186 | risk_atr <= 5.5 | 9,072.84 USD | 1,758 | 51.59% | 1.153 | 5,045.20 USD | yes |
| 11 | 20 | anchor_body_atr <= 1.4 | 9,067.16 USD | 1,742 | 52.64% | 1.155 | 4,655.20 USD | yes |
| 12 | 191 | anchor_body_atr <= 1.6 | 9,032.54 USD | 1,773 | 52.40% | 1.151 | 5,025.30 USD | yes |
| 13 | 138 | minutes_from_open <= 60, range_ratio <= 1.9, risk_atr <= 6 | 8,866.10 USD | 1,695 | 51.62% | 1.161 | 3,886.96 USD | yes |
| 14 | 8 | risk_ticks <= 52 | 8,845.36 USD | 1,832 | 52.02% | 1.145 | 4,473.44 USD | yes |
| 15 | 18 | range_ratio >= 0.7 | 8,698.54 USD | 1,473 | 52.27% | 1.168 | 5,252.12 USD | yes |
| 16 | 168 | anchor_body_atr <= 1.9, risk_ticks <= 20 | 8,683.24 USD | 1,738 | 52.01% | 1.165 | 3,030.38 USD | yes |
| 17 | 129 | risk_atr <= 5.75 | 8,630.48 USD | 1,776 | 51.58% | 1.143 | 5,355.30 USD | yes |
| 18 | 161 | risk_atr >= 1 | 8,611.44 USD | 1,828 | 52.08% | 1.137 | 5,253.44 USD | yes |
| 19 | 0 | baseline | 8,565.26 USD | 1,837 | 51.99% | 1.136 | 5,247.46 USD | yes |
| 20 | 22 | minutes_from_open <= 115 | 8,565.26 USD | 1,837 | 51.99% | 1.136 | 5,247.46 USD | yes |

Eligible trials: 84 of 200. Trials with objective above zero: 80.

Raw files in `results/price_reversal_v2/search/h02_filters_random_net0_s1_n200/`: `trials.csv` (every trial, baseline metrics), `neighbours.csv`, `run.json` (space, hashes, versions).
