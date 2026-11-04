# Search ny_filters_random_net0_s1_n200

Generated 2026-11-04 14:00 UTC. Strategy `fair_price_reversal`, variant `ny`, space `filters`, sampler `random`, seed 1, objective `net0` (net profit + open P&L without added slippage), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 3 neighbours: 203 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 69,157.02 USD | 3,849 | 35.28% | 1.123 | 24,678.62 USD | yes |
| 2 | 4 | risk_ticks >= 22 | 84,729.22 USD | 1,739 | 38.93% | 1.237 | 10,250.84 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_ny_filters_random_net0_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_ny_filters_random_net0_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | risk_ticks >= 20 | 80,621.86 USD | 2,007 | 37.92% | 1.204 | 15,083.88 USD | yes |
| 2 | 2 | risk_ticks >= 24 | 79,490.00 USD | 1,500 | 39.20% | 1.246 | 9,720.98 USD | yes |
| 3 | 0 | baseline | 69,157.02 USD | 3,849 | 35.28% | 1.123 | 24,678.62 USD | yes |

Neighbour objective: median 79,490.00 USD, worst 69,157.02 USD, 3 of 3 above zero; winner 84,729.22 USD.

## Top 20 trials

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 | risk_ticks >= 22 | 84,729.22 USD | 1,739 | 38.93% | 1.237 | 10,250.84 USD | yes |
| 2 | 89 | risk_ticks >= 30 | 83,971.20 USD | 940 | 42.77% | 1.372 | 8,402.36 USD | yes |
| 3 | 82 | minutes_from_open <= 90, risk_ticks >= 28 | 73,480.30 USD | 985 | 40.51% | 1.318 | 8,440.70 USD | yes |
| 4 | 34 | minutes_from_open <= 95, risk_atr >= 1.75 | 72,920.04 USD | 2,898 | 36.30% | 1.162 | 19,085.82 USD | yes |
| 5 | 164 | risk_atr >= 2 | 71,902.28 USD | 2,686 | 36.49% | 1.165 | 17,206.30 USD | yes |
| 6 | 22 | minutes_from_open <= 115 | 71,289.98 USD | 3,801 | 35.39% | 1.128 | 24,177.10 USD | yes |
| 7 | 0 | baseline | 69,157.02 USD | 3,849 | 35.28% | 1.123 | 24,678.62 USD | yes |
| 8 | 161 | risk_atr >= 1 | 68,971.14 USD | 3,843 | 35.26% | 1.122 | 24,678.62 USD | yes |
| 9 | 61 | anchor_body_atr <= 2, risk_ticks >= 14 | 68,624.96 USD | 2,852 | 36.12% | 1.142 | 21,050.66 USD | yes |
| 10 | 11 | risk_atr <= 4.75, risk_ticks >= 20 | 64,567.38 USD | 1,931 | 37.18% | 1.170 | 19,107.20 USD | yes |
| 11 | 177 | minutes_from_open <= 110 | 60,573.44 USD | 3,728 | 35.09% | 1.110 | 27,653.26 USD | yes |
| 12 | 50 | anchor_body_atr <= 1.7, minutes_from_open <= 90, risk_ticks >= 14 | 58,243.36 USD | 2,432 | 35.73% | 1.140 | 25,913.44 USD | yes |
| 13 | 73 | risk_atr <= 5.75, risk_ticks >= 8 | 57,311.78 USD | 3,711 | 35.00% | 1.103 | 27,394.56 USD | yes |
| 14 | 129 | risk_atr <= 5.75 | 57,129.48 USD | 3,826 | 34.97% | 1.102 | 27,488.42 USD | yes |
| 15 | 85 | anchor_body_atr >= 0.3, risk_ticks >= 32 | 56,590.86 USD | 557 | 43.09% | 1.410 | 5,874.42 USD | yes |
| 16 | 186 | risk_atr <= 5.5 | 56,501.74 USD | 3,813 | 34.93% | 1.101 | 26,702.22 USD | yes |
| 17 | 20 | anchor_body_atr <= 1.4 | 56,151.10 USD | 3,445 | 35.15% | 1.111 | 29,294.52 USD | yes |
| 18 | 135 | risk_atr <= 5 | 55,868.12 USD | 3,794 | 34.90% | 1.101 | 27,368.10 USD | yes |
| 19 | 191 | anchor_body_atr <= 1.6 | 55,542.72 USD | 3,564 | 35.04% | 1.106 | 29,023.82 USD | yes |
| 20 | 98 | risk_atr <= 6 | 55,453.40 USD | 3,830 | 34.96% | 1.099 | 27,736.46 USD | yes |

Eligible trials: 107 of 200. Trials with objective above zero: 100.

Raw files in `results/fair_price_reversal/search/ny_filters_random_net0_s1_n200/`: `trials.csv` (every trial, baseline metrics), `neighbours.csv`, `run.json` (space, hashes, versions).
