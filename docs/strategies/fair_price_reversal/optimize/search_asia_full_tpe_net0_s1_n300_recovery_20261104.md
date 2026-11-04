# Search asia_full_tpe_net0_s1_n300_recovery_20261104

Generated 2026-11-04 14:51 UTC. Strategy `fair_price_reversal`, variant `asia`, space `full`, sampler `tpe`, seed 1, objective `net0` (net profit + open P&L without added slippage), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 300 trials (30 duplicates) and 15 neighbours: 285 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | -1,376.20 USD | 1,310 | 32.67% | 0.985 | 8,097.82 USD | yes |
| 2 | 273 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.8 | 7,838.14 USD | 493 | 35.70% | 1.238 | 3,795.22 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_asia_full_tpe_net0_s1_n300_recovery_20261104.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_asia_full_tpe_net0_s1_n300_recovery_20261104.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 13 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.7 | 8,949.96 USD | 602 | 35.71% | 1.227 | 4,584.72 USD | yes |
| 2 | 10 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 40, range_ratio >= 0.8 | 8,346.98 USD | 451 | 35.25% | 1.280 | 3,374.62 USD | yes |
| 3 | 11 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 50, range_ratio >= 0.8 | 7,931.46 USD | 527 | 36.24% | 1.227 | 3,921.30 USD | yes |
| 4 | 14 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.9 | 7,232.00 USD | 400 | 36.25% | 1.264 | 2,908.64 USD | yes |
| 5 | 1 | window=90, anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.8 | 6,970.20 USD | 490 | 35.51% | 1.208 | 3,795.22 USD | yes |
| 6 | 3 | target=near, window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.8 | 6,322.16 USD | 492 | 54.67% | 1.291 | 2,280.50 USD | yes |
| 7 | 4 | target=far, window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.8 | 6,152.16 USD | 492 | 54.07% | 1.276 | 2,870.50 USD | yes |
| 8 | 9 | window=60, anchor_body_atr <= 0.3, range_ratio >= 0.8 | 6,142.02 USD | 599 | 35.39% | 1.153 | 3,782.66 USD | yes |
| 9 | 0 | anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.8 | 5,897.52 USD | 324 | 34.88% | 1.271 | 2,808.84 USD | yes |
| 10 | 8 | window=60, anchor_body_atr <= 0.4, minutes_from_open <= 45, range_ratio >= 0.8 | 5,676.14 USD | 593 | 34.23% | 1.137 | 4,443.56 USD | yes |
| 11 | 7 | window=60, anchor_body_atr <= 0.2, minutes_from_open <= 45, range_ratio >= 0.8 | 5,447.58 USD | 421 | 35.39% | 1.215 | 2,417.06 USD | yes |
| 12 | 12 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45 | 4,480.18 USD | 791 | 34.39% | 1.084 | 7,525.02 USD | yes |
| 13 | 5 | target=rr1, window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.8 | 3,834.02 USD | 499 | 50.70% | 1.147 | 2,780.50 USD | yes |
| 14 | 6 | window=60, minutes_from_open <= 45, range_ratio >= 0.8 | 2,859.48 USD | 1,326 | 33.56% | 1.030 | 6,767.72 USD | yes |
| 15 | 2 | atr_mult=1.5, window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.8 | 1,920.20 USD | 490 | 34.08% | 1.057 | 5,069.24 USD | yes |

Neighbour objective: median 6,142.02 USD, worst 1,920.20 USD, 15 of 15 above zero; winner 7,838.14 USD.

## Top 20 trials

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 273 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.8 | 7,838.14 USD | 493 | 35.70% | 1.238 | 3,795.22 USD | yes |
| 2 | 275 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45, range_ratio >= 0.8 | 7,838.14 USD | 493 | 35.70% | 1.238 | 3,795.22 USD | yes |
| 3 | 234 | anchor_body_atr <= 0.3, minutes_from_open <= 40 | 6,813.72 USD | 514 | 35.99% | 1.208 | 3,960.60 USD | yes |
| 4 | 254 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 40 | 6,651.48 USD | 726 | 34.85% | 1.138 | 6,962.96 USD | yes |
| 5 | 255 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 40 | 6,651.48 USD | 726 | 34.85% | 1.138 | 6,962.96 USD | yes |
| 6 | 256 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 40 | 6,651.48 USD | 726 | 34.85% | 1.138 | 6,962.96 USD | yes |
| 7 | 295 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 35 | 5,953.18 USD | 641 | 34.79% | 1.141 | 5,052.86 USD | yes |
| 8 | 245 | window=90, anchor_body_atr <= 0.3, minutes_from_open <= 40 | 5,531.58 USD | 721 | 34.54% | 1.115 | 6,962.96 USD | yes |
| 9 | 247 | window=90, anchor_body_atr <= 0.3, minutes_from_open <= 40 | 5,531.58 USD | 721 | 34.54% | 1.115 | 6,962.96 USD | yes |
| 10 | 248 | window=90, anchor_body_atr <= 0.3, minutes_from_open <= 40 | 5,531.58 USD | 721 | 34.54% | 1.115 | 6,962.96 USD | yes |
| 11 | 253 | window=90, anchor_body_atr <= 0.3, minutes_from_open <= 40 | 5,531.58 USD | 721 | 34.54% | 1.115 | 6,962.96 USD | yes |
| 12 | 264 | window=90, anchor_body_atr <= 0.3, minutes_from_open <= 40 | 5,531.58 USD | 721 | 34.54% | 1.115 | 6,962.96 USD | yes |
| 13 | 243 | window=90, anchor_body_atr <= 0.2, minutes_from_open <= 40, range_ratio >= 0.7 | 5,162.46 USD | 477 | 34.59% | 1.176 | 4,185.06 USD | yes |
| 14 | 229 | anchor_body_atr <= 0.4, minutes_from_open <= 40 | 4,822.02 USD | 599 | 34.56% | 1.121 | 4,271.22 USD | yes |
| 15 | 230 | anchor_body_atr <= 0.4, minutes_from_open <= 40 | 4,822.02 USD | 599 | 34.56% | 1.121 | 4,271.22 USD | yes |
| 16 | 250 | window=60, anchor_body_atr <= 0.2, minutes_from_open <= 40 | 4,765.24 USD | 638 | 34.64% | 1.123 | 3,740.60 USD | yes |
| 17 | 251 | window=60, anchor_body_atr <= 0.2, minutes_from_open <= 40 | 4,765.24 USD | 638 | 34.64% | 1.123 | 3,740.60 USD | yes |
| 18 | 143 | anchor_body_atr <= 1.2, minutes_from_open >= 20, risk_ticks <= 34 | 4,522.16 USD | 492 | 34.35% | 1.157 | 2,393.10 USD | yes |
| 19 | 257 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45 | 4,480.18 USD | 791 | 34.39% | 1.084 | 7,525.02 USD | yes |
| 20 | 258 | window=60, anchor_body_atr <= 0.3, minutes_from_open <= 45 | 4,480.18 USD | 791 | 34.39% | 1.084 | 7,525.02 USD | yes |

Eligible trials: 188 of 300. Trials with objective above zero: 84.

Raw files in `results/fair_price_reversal/search/asia_full_tpe_net0_s1_n300_recovery_20261104/`: `trials.csv` (every trial, baseline metrics), `neighbours.csv`, `run.json` (space, hashes, versions).
