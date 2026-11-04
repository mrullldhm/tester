# Search london_full_tpe_net0_s1_n300_recovery_20261104

Generated 2026-11-04 14:48 UTC. Strategy `fair_price_reversal`, variant `london`, space `full`, sampler `tpe`, seed 1, objective `net0` (net profit + open P&L without added slippage), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 300 trials (17 duplicates) and 9 neighbours: 292 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 11,237.30 USD | 1,635 | 35.84% | 1.086 | 7,901.56 USD | yes |
| 2 | 271 | risk_ticks <= 20 | 14,922.76 USD | 1,462 | 36.32% | 1.154 | 4,578.68 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_london_full_tpe_net0_s1_n300_recovery_20261104.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_london_full_tpe_net0_s1_n300_recovery_20261104.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 7 | risk_ticks <= 18 | 17,479.94 USD | 1,403 | 36.78% | 1.197 | 4,384.66 USD | yes |
| 2 | 8 | risk_ticks <= 22 | 14,808.14 USD | 1,493 | 36.24% | 1.146 | 4,578.68 USD | yes |
| 3 | 2 | atr_mult=2.0, risk_ticks <= 20 | 14,193.06 USD | 1,447 | 36.28% | 1.147 | 4,416.62 USD | yes |
| 4 | 1 | atr_mult=1.0, risk_ticks <= 20 | 13,775.32 USD | 1,434 | 35.98% | 1.144 | 4,554.66 USD | yes |
| 5 | 6 | baseline | 11,237.30 USD | 1,635 | 35.84% | 1.086 | 7,901.56 USD | yes |
| 6 | 0 | window=60, risk_ticks <= 20 | 10,894.48 USD | 2,576 | 34.70% | 1.061 | 8,487.92 USD | yes |
| 7 | 5 | target=rr1, risk_ticks <= 20 | 6,636.88 USD | 1,456 | 52.68% | 1.092 | 3,670.74 USD | yes |
| 8 | 4 | target=far, risk_ticks <= 20 | 6,570.90 USD | 1,455 | 54.78% | 1.099 | 3,245.24 USD | yes |
| 9 | 3 | target=near, risk_ticks <= 20 | 5,746.98 USD | 1,451 | 60.17% | 1.099 | 2,141.22 USD | yes |

Neighbour objective: median 11,237.30 USD, worst 5,746.98 USD, 9 of 9 above zero; winner 14,922.76 USD.

## Top 20 trials

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 271 | risk_ticks <= 20 | 14,922.76 USD | 1,462 | 36.32% | 1.154 | 4,578.68 USD | yes |
| 2 | 275 | risk_ticks <= 20 | 14,922.76 USD | 1,462 | 36.32% | 1.154 | 4,578.68 USD | yes |
| 3 | 128 | atr_mult=1.0, window=90, minutes_from_open <= 35, risk_atr <= 5, risk_ticks >= 6 | 14,374.50 USD | 1,775 | 36.11% | 1.096 | 9,200.18 USD | yes |
| 4 | 176 | range_ratio <= 1.6, risk_ticks >= 6 | 13,420.64 USD | 1,368 | 37.28% | 1.121 | 9,067.90 USD | yes |
| 5 | 180 | range_ratio <= 1.5, risk_ticks >= 6 | 13,403.50 USD | 1,325 | 37.51% | 1.126 | 8,014.74 USD | yes |
| 6 | 182 | range_ratio <= 1.5, risk_ticks >= 6 | 13,403.50 USD | 1,325 | 37.51% | 1.126 | 8,014.74 USD | yes |
| 7 | 106 | risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 8 | 109 | risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 9 | 207 | minutes_from_open <= 45, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 10 | 209 | minutes_from_open <= 45, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 11 | 211 | minutes_from_open <= 45, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 12 | 212 | minutes_from_open <= 40, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 13 | 213 | minutes_from_open <= 40, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 14 | 214 | minutes_from_open <= 40, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 15 | 215 | minutes_from_open <= 35, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 16 | 216 | minutes_from_open <= 40, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 17 | 259 | minutes_from_open <= 35, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 18 | 262 | minutes_from_open <= 30, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 19 | 269 | minutes_from_open <= 35, risk_ticks >= 6 | 12,917.84 USD | 1,508 | 36.80% | 1.102 | 6,940.66 USD | yes |
| 20 | 281 | anchor_body_atr <= 1.6, minutes_from_open <= 55 | 12,798.90 USD | 1,555 | 36.21% | 1.103 | 6,493.12 USD | yes |

Eligible trials: 210 of 300. Trials with objective above zero: 176.

Raw files in `results/fair_price_reversal/search/london_full_tpe_net0_s1_n300_recovery_20261104/`: `trials.csv` (every trial, baseline metrics), `neighbours.csv`, `run.json` (space, hashes, versions).
