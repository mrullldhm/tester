# Search london_filters_random_net1_s1_n200

Generated 2026-10-31 05:44 UTC. Strategy `fair_price_reversal`, variant `london`, space `filters`, sampler `random`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 3 neighbours: 609 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 40,277.60 USD / -13,754.26 USD / -70,832.10 USD | 3,120 | 37.31% | 1.111 / 0.966 | 13,213.46 USD | yes |
| 2 | 89 | risk_ticks >= 30 | 39,017.28 USD / 32,197.28 USD / 23,121.30 USD | 436 | 45.64% | 1.422 / 1.331 | 7,567.38 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_london_filters_random_net1_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_london_filters_random_net1_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | risk_ticks >= 32 | 38,284.66 USD / 32,864.66 USD / 24,868.68 USD | 367 | 46.87% | 1.474 / 1.388 | 7,649.84 USD | yes |
| 2 | 1 | risk_ticks >= 28 | 38,181.96 USD / 29,711.96 USD / 19,595.98 USD | 502 | 44.62% | 1.369 / 1.272 | 8,155.52 USD | yes |
| 3 | 0 | baseline | 40,277.60 USD / -13,754.26 USD / -70,832.10 USD | 3,120 | 37.31% | 1.111 / 0.966 | 13,213.46 USD | yes |

Neighbour objective: median 29,711.96 USD, worst -13,754.26 USD, 2 of 3 above zero; winner 32,197.28 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 89 | risk_ticks >= 30 | 39,017.28 USD / 32,197.28 USD / 23,121.30 USD | 436 | 45.64% | 1.422 / 1.331 | 7,567.38 USD | yes |
| 2 | 82 | minutes_from_open <= 90, risk_ticks >= 28 | 29,428.18 USD / 22,948.18 USD / 15,128.18 USD | 391 | 43.73% | 1.361 / 1.267 | 7,369.08 USD | yes |
| 3 | 4 | risk_ticks >= 22 | 31,102.76 USD / 15,000.80 USD / -4,881.16 USD | 962 | 39.29% | 1.177 / 1.080 | 12,048.88 USD | yes |
| 4 | 76 | range_ratio >= 0.9, risk_ticks >= 26 | 18,632.40 USD / 12,202.40 USD / 3,976.42 USD | 380 | 42.89% | 1.235 / 1.146 | 6,789.24 USD | yes |
| 5 | 130 | anchor_body_atr >= 0.5, minutes_from_open >= 35, range_ratio >= 0.8 | 24,246.26 USD / 8,428.32 USD / -5,363.64 USD | 787 | 40.79% | 1.264 / 1.082 | 5,488.84 USD | yes |
| 6 | 36 | range_ratio >= 1.3 | 16,686.24 USD / 8,118.30 USD / -3,007.68 USD | 588 | 38.44% | 1.216 / 1.096 | 5,363.96 USD | yes |
| 7 | 11 | risk_atr <= 4.75, risk_ticks >= 20 | 18,967.66 USD / 7,775.70 USD / -5,330.28 USD | 717 | 37.38% | 1.144 / 1.055 | 11,359.34 USD | yes |
| 8 | 13 | minutes_from_open <= 95, range_ratio <= 2, risk_atr >= 3 | 40,526.08 USD / 7,632.16 USD / -28,489.80 USD | 1,996 | 38.73% | 1.169 / 1.029 | 8,190.44 USD | yes |
| 9 | 75 | risk_atr >= 4.25 | 26,174.28 USD / 6,558.30 USD / -12,731.70 USD | 1,086 | 39.96% | 1.189 / 1.043 | 6,835.60 USD | yes |
| 10 | 176 | range_ratio >= 1.5 | 11,683.00 USD / 6,537.02 USD / -32.98 USD | 350 | 38.00% | 1.236 / 1.122 | 3,896.42 USD | yes |
| 11 | 110 | minutes_from_open >= 40, risk_atr >= 5.5 | 12,815.06 USD / 6,035.06 USD / 415.06 USD | 347 | 46.11% | 1.292 / 1.126 | 3,859.24 USD | yes |
| 12 | 117 | minutes_from_open <= 80, risk_atr <= 5 | 37,345.42 USD / 5,993.46 USD / -28,746.54 USD | 1,929 | 36.81% | 1.177 / 1.025 | 6,735.72 USD | yes |
| 13 | 115 | minutes_from_open <= 80, range_ratio <= 1.9 | 42,206.50 USD / 5,884.54 USD / -34,455.46 USD | 2,175 | 37.84% | 1.173 / 1.022 | 6,988.58 USD | yes |
| 14 | 152 | range_ratio >= 1.4, risk_atr >= 2 | 12,219.24 USD / 5,737.28 USD / -2,052.72 USD | 438 | 37.90% | 1.199 / 1.086 | 3,752.90 USD | yes |
| 15 | 88 | anchor_body_atr >= 0.7, minutes_from_open <= 85 | 17,930.58 USD / 5,254.60 USD / -10,311.38 USD | 771 | 38.00% | 1.218 / 1.057 | 4,338.74 USD | yes |
| 16 | 159 | risk_atr >= 4.75 | 17,771.68 USD / 3,791.68 USD / -10,008.32 USD | 716 | 42.18% | 1.193 / 1.037 | 6,159.84 USD | yes |
| 17 | 21 | anchor_body_atr <= 1.5, risk_atr >= 5, risk_ticks >= 14 | 13,676.28 USD / 3,146.28 USD / -7,063.72 USD | 486 | 44.03% | 1.207 / 1.043 | 6,077.78 USD | yes |
| 18 | 19 | risk_atr >= 4.5 | 19,604.46 USD / 3,118.48 USD / -13,311.52 USD | 877 | 40.71% | 1.174 / 1.025 | 6,452.70 USD | yes |
| 19 | 151 | minutes_from_open >= 65, range_ratio <= 1.1, risk_atr >= 3.5, risk_ticks >= 16 | 10,720.04 USD / 2,920.04 USD / -3,609.96 USD | 398 | 41.71% | 1.205 / 1.051 | 4,830.04 USD | yes |
| 20 | 45 | risk_atr >= 3 | 44,831.20 USD / 2,899.34 USD / -40,520.56 USD | 2,440 | 38.77% | 1.151 / 1.009 | 10,282.10 USD | yes |

Eligible trials: 112 of 200. Trials with objective above zero: 28.

Files: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
