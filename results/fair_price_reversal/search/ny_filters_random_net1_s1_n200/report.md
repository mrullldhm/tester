# Search ny_filters_random_net1_s1_n200

Generated 2026-10-31 05:44 UTC. Strategy `fair_price_reversal`, variant `ny`, space `filters`, sampler `random`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 6 neighbours: 618 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 55,002.92 USD / 2,423.02 USD / -49,304.92 USD | 3,054 | 37.10% | 1.091 / 1.004 | 19,966.92 USD | yes |
| 2 | 85 | anchor_body_atr >= 0.3, risk_ticks >= 32 | 63,293.46 USD / 49,297.48 USD / 34,591.50 USD | 927 | 42.50% | 1.261 / 1.195 | 9,717.98 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_ny_filters_random_net1_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_ny_filters_random_net1_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | anchor_body_atr >= 0.2, risk_ticks >= 32 | 68,507.04 USD / 50,505.08 USD / 34,523.12 USD | 1,048 | 42.08% | 1.248 / 1.175 | 11,163.46 USD | yes |
| 2 | 4 | anchor_body_atr >= 0.3, risk_ticks >= 30 | 66,703.22 USD / 49,681.26 USD / 32,485.28 USD | 1,039 | 42.06% | 1.254 / 1.181 | 9,640.34 USD | yes |
| 3 | 2 | anchor_body_atr >= 0.4, risk_ticks >= 32 | 60,769.78 USD / 48,373.80 USD / 35,467.82 USD | 811 | 43.16% | 1.291 / 1.222 | 8,669.84 USD | yes |
| 4 | 5 | anchor_body_atr >= 0.3, risk_ticks >= 34 | 60,339.58 USD / 47,763.60 USD / 35,147.62 USD | 821 | 43.00% | 1.273 / 1.208 | 7,789.04 USD | yes |
| 5 | 0 | risk_ticks >= 32 | 63,905.86 USD / 40,873.90 USD / 18,731.94 USD | 1,307 | 41.16% | 1.179 / 1.110 | 12,618.84 USD | yes |
| 6 | 3 | anchor_body_atr >= 0.3 | 62,906.80 USD / 27,132.88 USD / -8,139.08 USD | 2,160 | 37.92% | 1.151 / 1.061 | 11,843.22 USD | yes |

Neighbour objective: median 48,068.70 USD, worst 27,132.88 USD, 6 of 6 above zero; winner 49,297.48 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 85 | anchor_body_atr >= 0.3, risk_ticks >= 32 | 63,293.46 USD / 49,297.48 USD / 34,591.50 USD | 927 | 42.50% | 1.261 / 1.195 | 9,717.98 USD | yes |
| 2 | 89 | risk_ticks >= 30 | 62,760.60 USD / 35,862.66 USD / 10,390.70 USD | 1,470 | 40.54% | 1.162 / 1.088 | 13,723.00 USD | yes |
| 3 | 16 | minutes_from_open >= 25, range_ratio <= 1.5, risk_ticks >= 34 | 50,697.48 USD / 33,451.50 USD / 17,705.52 USD | 926 | 42.12% | 1.200 / 1.126 | 11,043.06 USD | yes |
| 4 | 3 | anchor_body_atr >= 0.3 | 62,906.80 USD / 27,132.88 USD / -8,139.08 USD | 2,160 | 37.92% | 1.151 / 1.061 | 11,843.22 USD | yes |
| 5 | 130 | anchor_body_atr >= 0.5, minutes_from_open >= 35, range_ratio >= 0.8 | 39,943.40 USD / 26,353.40 USD / 13,413.40 USD | 830 | 39.40% | 1.248 / 1.153 | 7,404.72 USD | yes |
| 6 | 180 | anchor_body_atr >= 0.4, range_ratio <= 1.3, risk_atr >= 3.25 | 35,314.40 USD / 22,788.42 USD / 9,682.44 USD | 780 | 39.87% | 1.220 / 1.134 | 14,551.62 USD | yes |
| 7 | 131 | range_ratio <= 0.9, risk_atr <= 5.25, risk_ticks <= 54 | 42,835.00 USD / 21,927.06 USD / 935.10 USD | 1,250 | 37.92% | 1.214 / 1.101 | 7,565.26 USD | yes |
| 8 | 53 | anchor_body_atr <= 0.7, risk_atr >= 3.25, risk_ticks <= 50 | 31,678.82 USD / 18,828.82 USD / 6,446.86 USD | 759 | 39.39% | 1.235 / 1.130 | 8,676.96 USD | yes |
| 9 | 75 | risk_atr >= 4.25 | 26,886.04 USD / 17,946.04 USD / 8,226.04 USD | 598 | 41.81% | 1.188 / 1.120 | 10,436.58 USD | yes |
| 10 | 4 | risk_ticks >= 22 | 57,396.96 USD / 17,783.04 USD / -20,608.92 USD | 2,252 | 38.32% | 1.111 / 1.032 | 18,022.18 USD | yes |
| 11 | 41 | range_ratio >= 0.7, risk_atr >= 4.25 | 24,982.46 USD / 17,782.46 USD / 10,402.46 USD | 477 | 41.09% | 1.216 / 1.147 | 9,167.12 USD | yes |
| 12 | 78 | range_ratio >= 0.6, risk_atr >= 2.5, risk_ticks >= 8 | 56,095.86 USD / 17,191.94 USD / -22,796.00 USD | 2,307 | 37.84% | 1.117 / 1.034 | 19,030.20 USD | yes |
| 13 | 198 | minutes_from_open >= 75, risk_ticks >= 34 | 23,695.32 USD / 16,875.32 USD / 9,325.32 USD | 434 | 42.40% | 1.206 / 1.140 | 14,109.24 USD | yes |
| 14 | 33 | minutes_from_open >= 65, risk_ticks >= 6 | 37,080.18 USD / 16,620.18 USD / -7,149.82 USD | 1,291 | 38.03% | 1.146 / 1.062 | 14,061.64 USD | yes |
| 15 | 82 | minutes_from_open <= 90, risk_ticks >= 28 | 40,929.38 USD / 16,377.42 USD / -7,312.58 USD | 1,331 | 39.29% | 1.118 / 1.045 | 17,028.18 USD | yes |
| 16 | 106 | anchor_body_atr >= 0.2 | 58,778.84 USD / 15,768.94 USD / -23,439.00 USD | 2,458 | 37.31% | 1.123 / 1.031 | 16,778.94 USD | yes |
| 17 | 121 | risk_atr >= 3.5, risk_ticks <= 58 | 30,868.20 USD / 14,392.22 USD / -4,417.78 USD | 1,090 | 39.17% | 1.148 / 1.065 | 13,487.52 USD | yes |
| 18 | 45 | risk_atr >= 3 | 46,353.56 USD / 14,275.62 USD / -17,906.34 USD | 1,922 | 38.03% | 1.111 / 1.032 | 21,767.50 USD | yes |
| 19 | 154 | range_ratio <= 1, risk_ticks <= 44 | 39,188.14 USD / 13,970.20 USD / -10,191.76 USD | 1,493 | 37.24% | 1.169 / 1.055 | 7,964.86 USD | yes |
| 20 | 199 | risk_atr >= 2.75 | 52,058.82 USD / 13,914.90 USD / -24,447.06 USD | 2,259 | 37.76% | 1.109 / 1.028 | 21,636.38 USD | yes |

Eligible trials: 117 of 200. Trials with objective above zero: 62.

Files: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
