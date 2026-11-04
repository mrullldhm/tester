# Search ny_full_tpe_net0_s1_n300

Generated 2026-11-04 14:06 UTC. Strategy `fair_price_reversal`, variant `ny`, space `full`, sampler `tpe`, seed 1, objective `net0` (net profit + open P&L without added slippage), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 300 trials (39 duplicates) and 11 neighbours: 272 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 69,157.02 USD | 3,849 | 35.28% | 1.123 | 24,678.62 USD | yes |
| 2 | 102 | risk_atr >= 1.75, risk_ticks >= 22 | 85,071.32 USD | 1,634 | 39.41% | 1.253 | 10,074.76 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_ny_full_tpe_net0_s1_n300.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_ny_full_tpe_net0_s1_n300.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 6 | risk_atr >= 1.5, risk_ticks >= 22 | 86,047.76 USD | 1,712 | 39.14% | 1.245 | 10,250.84 USD | yes |
| 2 | 5 | risk_ticks >= 22 | 84,729.22 USD | 1,739 | 38.93% | 1.237 | 10,250.84 USD | yes |
| 3 | 9 | risk_atr >= 1.75, risk_ticks >= 20 | 82,004.66 USD | 1,867 | 38.46% | 1.222 | 14,499.76 USD | yes |
| 4 | 7 | risk_atr >= 2, risk_ticks >= 22 | 80,428.34 USD | 1,483 | 39.65% | 1.260 | 9,506.72 USD | yes |
| 5 | 0 | window=90, risk_atr >= 1.75, risk_ticks >= 22 | 78,941.70 USD | 1,415 | 39.15% | 1.269 | 12,882.94 USD | yes |
| 6 | 10 | risk_atr >= 1.75, risk_ticks >= 24 | 78,719.64 USD | 1,418 | 39.56% | 1.256 | 9,778.92 USD | yes |
| 7 | 1 | atr_mult=1.0, risk_atr >= 1.75, risk_ticks >= 22 | 78,263.04 USD | 1,748 | 38.90% | 1.214 | 12,035.04 USD | yes |
| 8 | 8 | risk_atr >= 1.75 | 75,614.14 USD | 3,193 | 36.20% | 1.152 | 17,870.08 USD | yes |
| 9 | 3 | target=far, risk_atr >= 1.75, risk_ticks >= 22 | 31,478.36 USD | 1,682 | 56.42% | 1.128 | 6,694.92 USD | yes |
| 10 | 4 | target=rr1, risk_atr >= 1.75, risk_ticks >= 22 | 26,678.46 USD | 1,677 | 51.82% | 1.096 | 10,931.58 USD | yes |
| 11 | 2 | target=near, risk_atr >= 1.75, risk_ticks >= 22 | 16,520.42 USD | 1,679 | 61.05% | 1.074 | 7,149.64 USD | yes |

Neighbour objective: median 78,719.64 USD, worst 16,520.42 USD, 11 of 11 above zero; winner 85,071.32 USD.

## Top 20 trials

| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 102 | risk_atr >= 1.75, risk_ticks >= 22 | 85,071.32 USD | 1,634 | 39.41% | 1.253 | 10,074.76 USD | yes |
| 2 | 178 | risk_ticks >= 22 | 84,729.22 USD | 1,739 | 38.93% | 1.237 | 10,250.84 USD | yes |
| 3 | 188 | risk_ticks >= 30 | 83,971.20 USD | 940 | 42.77% | 1.372 | 8,402.36 USD | yes |
| 4 | 192 | risk_ticks >= 30 | 83,971.20 USD | 940 | 42.77% | 1.372 | 8,402.36 USD | yes |
| 5 | 205 | risk_ticks >= 30 | 83,971.20 USD | 940 | 42.77% | 1.372 | 8,402.36 USD | yes |
| 6 | 226 | risk_ticks >= 30 | 83,971.20 USD | 940 | 42.77% | 1.372 | 8,402.36 USD | yes |
| 7 | 238 | risk_ticks >= 30 | 83,971.20 USD | 940 | 42.77% | 1.372 | 8,402.36 USD | yes |
| 8 | 249 | risk_ticks >= 30 | 83,971.20 USD | 940 | 42.77% | 1.372 | 8,402.36 USD | yes |
| 9 | 111 | risk_atr >= 1.5, risk_ticks >= 26 | 83,306.36 USD | 1,282 | 40.48% | 1.290 | 8,831.84 USD | yes |
| 10 | 180 | risk_ticks >= 26 | 82,492.04 USD | 1,298 | 40.29% | 1.284 | 8,831.84 USD | yes |
| 11 | 265 | risk_ticks >= 26 | 82,492.04 USD | 1,298 | 40.29% | 1.284 | 8,831.84 USD | yes |
| 12 | 270 | risk_ticks >= 26 | 82,492.04 USD | 1,298 | 40.29% | 1.284 | 8,831.84 USD | yes |
| 13 | 154 | risk_atr >= 1.75, risk_ticks >= 30 | 81,145.72 USD | 914 | 42.78% | 1.369 | 8,026.28 USD | yes |
| 14 | 193 | risk_ticks >= 28 | 81,073.38 USD | 1,131 | 41.03% | 1.309 | 8,440.70 USD | yes |
| 15 | 196 | risk_ticks >= 28 | 81,073.38 USD | 1,131 | 41.03% | 1.309 | 8,440.70 USD | yes |
| 16 | 199 | risk_ticks >= 28 | 81,073.38 USD | 1,131 | 41.03% | 1.309 | 8,440.70 USD | yes |
| 17 | 201 | risk_ticks >= 28 | 81,073.38 USD | 1,131 | 41.03% | 1.309 | 8,440.70 USD | yes |
| 18 | 202 | risk_ticks >= 28 | 81,073.38 USD | 1,131 | 41.03% | 1.309 | 8,440.70 USD | yes |
| 19 | 206 | risk_ticks >= 28 | 81,073.38 USD | 1,131 | 41.03% | 1.309 | 8,440.70 USD | yes |
| 20 | 216 | risk_ticks >= 28 | 81,073.38 USD | 1,131 | 41.03% | 1.309 | 8,440.70 USD | yes |

Eligible trials: 217 of 300. Trials with objective above zero: 188.

Raw files in `results/fair_price_reversal/search/ny_full_tpe_net0_s1_n300/`: `trials.csv` (every trial, baseline metrics), `neighbours.csv`, `run.json` (space, hashes, versions).
