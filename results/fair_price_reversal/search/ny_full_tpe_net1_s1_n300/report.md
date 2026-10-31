# Search ny_full_tpe_net1_s1_n300

Generated 2026-10-31 05:44 UTC. Strategy `fair_price_reversal`, variant `ny`, space `full`, sampler `tpe`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 300 trials (6 duplicates) and 13 neighbours: 921 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 55,002.92 USD / 2,423.02 USD / -49,304.92 USD | 3,054 | 37.10% | 1.091 / 1.004 | 19,966.92 USD | yes |
| 2 | 286 | atr_mult=1.0, anchor_body_atr >= 0.3, risk_ticks >= 34 | 48,318.88 USD / 35,686.92 USD / 22,470.94 USD | 856 | 41.94% | 1.206 / 1.146 | 10,203.16 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_ny_full_tpe_net1_s1_n300.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_ny_full_tpe_net1_s1_n300.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | anchor_body_atr >= 0.3, risk_ticks >= 34 | 60,339.58 USD / 47,763.60 USD / 35,147.62 USD | 821 | 43.00% | 1.273 / 1.208 | 7,789.04 USD | yes |
| 2 | 11 | atr_mult=1.0, anchor_body_atr >= 0.3, risk_ticks >= 32 | 52,208.64 USD / 38,096.68 USD / 22,730.70 USD | 968 | 41.63% | 1.203 / 1.142 | 10,203.16 USD | yes |
| 3 | 9 | atr_mult=1.0, anchor_body_atr >= 0.4, risk_ticks >= 34 | 45,189.02 USD / 33,997.06 USD / 22,421.08 USD | 749 | 42.19% | 1.223 / 1.162 | 8,620.60 USD | yes |
| 4 | 12 | atr_mult=1.0, anchor_body_atr >= 0.3, risk_ticks >= 36 | 43,177.06 USD / 31,661.08 USD / 20,105.10 USD | 747 | 42.03% | 1.202 / 1.143 | 10,203.16 USD | yes |
| 5 | 8 | atr_mult=1.0, anchor_body_atr >= 0.2, risk_ticks >= 34 | 48,316.38 USD / 31,538.44 USD / 16,542.46 USD | 981 | 41.18% | 1.176 / 1.110 | 10,946.78 USD | yes |
| 6 | 2 | atr_mult=1.5, anchor_body_atr >= 0.3, risk_ticks >= 34 | 44,084.66 USD / 31,252.70 USD / 17,836.72 USD | 867 | 41.41% | 1.184 / 1.126 | 10,203.16 USD | yes |
| 7 | 6 | atr_mult=1.0, target=rr1, anchor_body_atr >= 0.3, risk_ticks >= 34 | 36,216.32 USD / 24,486.32 USD / 13,370.34 USD | 884 | 54.52% | 1.188 / 1.121 | 6,627.08 USD | yes |
| 8 | 0 | atr_mult=1.0, window=90, anchor_body_atr >= 0.3, risk_ticks >= 34 | 33,774.64 USD / 23,982.68 USD / 13,572.68 USD | 668 | 41.02% | 1.179 / 1.122 | 14,221.00 USD | yes |
| 9 | 3 | atr_mult=1.0, swing=2, anchor_body_atr >= 0.3, risk_ticks >= 34 | 35,912.84 USD / 23,656.86 USD / 11,496.86 USD | 758 | 39.71% | 1.171 / 1.108 | 12,235.32 USD | yes |
| 10 | 7 | atr_mult=1.0, risk_ticks >= 34 | 42,349.12 USD / 20,631.18 USD / -644.80 USD | 1,244 | 40.35% | 1.118 / 1.055 | 16,995.02 USD | yes |
| 11 | 5 | atr_mult=1.0, target=far, anchor_body_atr >= 0.3, risk_ticks >= 34 | 31,128.28 USD / 18,578.28 USD / 6,028.28 USD | 886 | 61.74% | 1.194 / 1.111 | 7,861.70 USD | yes |
| 12 | 4 | atr_mult=1.0, target=near, anchor_body_atr >= 0.3, risk_ticks >= 34 | 27,158.28 USD / 15,238.28 USD / 3,318.28 USD | 886 | 67.16% | 1.201 / 1.108 | 11,105.72 USD | yes |
| 13 | 10 | atr_mult=1.0, anchor_body_atr >= 0.3 | 47,422.34 USD / 9,922.44 USD / -27,085.50 USD | 2,283 | 37.49% | 1.107 / 1.021 | 13,451.22 USD | yes |

Neighbour objective: median 24,486.32 USD, worst 9,922.44 USD, 13 of 13 above zero; winner 35,686.92 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 286 | atr_mult=1.0, anchor_body_atr >= 0.3, risk_ticks >= 34 | 48,318.88 USD / 35,686.92 USD / 22,470.94 USD | 856 | 41.94% | 1.206 / 1.146 | 10,203.16 USD | yes |
| 2 | 107 | window=90, anchor_body_atr >= 0.3, range_ratio <= 1.1, risk_atr >= 2, risk_ticks >= 26 | 45,153.38 USD / 33,737.40 USD / 22,517.40 USD | 631 | 42.79% | 1.314 / 1.223 | 8,805.22 USD | yes |
| 3 | 289 | atr_mult=1.0, anchor_body_atr >= 0.3, risk_ticks >= 36 | 43,177.06 USD / 31,661.08 USD / 20,105.10 USD | 747 | 42.03% | 1.202 / 1.143 | 10,203.16 USD | yes |
| 4 | 283 | atr_mult=1.0, anchor_body_atr >= 0.4, risk_ticks >= 36 | 41,744.94 USD / 31,528.96 USD / 21,272.98 USD | 653 | 42.42% | 1.228 / 1.166 | 8,620.60 USD | yes |
| 5 | 275 | atr_mult=1.5, anchor_body_atr >= 0.3, risk_ticks >= 30 | 48,756.04 USD / 31,278.10 USD / 13,082.12 USD | 1,098 | 40.53% | 1.171 / 1.105 | 10,203.16 USD | yes |
| 6 | 276 | atr_mult=1.5, anchor_body_atr >= 0.3, risk_ticks >= 36 | 39,946.96 USD / 28,330.98 USD / 16,675.00 USD | 752 | 41.62% | 1.184 / 1.126 | 10,203.16 USD | yes |
| 7 | 295 | atr_mult=1.0, anchor_body_atr >= 0.4, risk_ticks >= 38 | 35,210.66 USD / 26,634.68 USD / 17,878.70 USD | 567 | 42.15% | 1.212 / 1.155 | 8,246.58 USD | yes |
| 8 | 296 | atr_mult=1.0, anchor_body_atr >= 0.4, risk_ticks >= 38 | 35,210.66 USD / 26,634.68 USD / 17,878.70 USD | 567 | 42.15% | 1.212 / 1.155 | 8,246.58 USD | yes |
| 9 | 84 | anchor_body_atr >= 0.2, range_ratio <= 0.9, risk_ticks >= 26 | 37,659.36 USD / 26,217.40 USD / 14,991.42 USD | 632 | 41.77% | 1.259 / 1.172 | 12,987.48 USD | yes |
| 10 | 288 | atr_mult=1.0, target=rr1, anchor_body_atr >= 0.3, risk_ticks >= 38 | 33,660.62 USD / 24,710.62 USD / 15,310.62 USD | 669 | 55.31% | 1.215 / 1.151 | 6,344.62 USD | yes |
| 11 | 113 | anchor_body_atr >= 0.3, range_ratio <= 1.1, risk_ticks >= 16 | 46,350.18 USD / 23,352.24 USD / 2,726.26 USD | 1,291 | 38.88% | 1.183 / 1.086 | 11,176.52 USD | yes |
| 12 | 299 | atr_mult=1.0, target=rr1, anchor_body_atr >= 0.4, risk_ticks >= 36 | 32,034.64 USD / 23,004.64 USD / 13,524.64 USD | 668 | 54.79% | 1.214 / 1.147 | 6,198.74 USD | yes |
| 13 | 261 | atr_mult=1.0, window=90, anchor_body_atr >= 0.5, minutes_from_open >= 55, risk_ticks >= 22 | 28,177.68 USD / 22,507.68 USD / 15,907.68 USD | 416 | 41.59% | 1.320 / 1.242 | 7,676.22 USD | yes |
| 14 | 110 | anchor_body_atr >= 0.3, range_ratio <= 1.1, risk_ticks >= 14 | 45,887.02 USD / 22,099.08 USD / 663.10 USD | 1,349 | 38.62% | 1.177 / 1.080 | 11,466.62 USD | yes |
| 15 | 167 | anchor_body_atr >= 0.4, minutes_from_open >= 45, range_ratio <= 0.9, risk_ticks >= 26 | 27,401.04 USD / 21,871.04 USD / 14,781.04 USD | 348 | 44.54% | 1.365 / 1.276 | 7,902.46 USD | yes |
| 16 | 291 | anchor_body_atr >= 0.3, range_ratio >= 1, risk_ticks >= 36 | 24,765.26 USD / 19,355.26 USD / 14,195.26 USD | 337 | 43.03% | 1.262 / 1.197 | 9,754.82 USD | yes |
| 17 | 219 | atr_mult=1.5, anchor_body_atr >= 0.3, range_ratio <= 1.1, risk_ticks >= 22 | 35,634.18 USD / 17,326.24 USD / -679.74 USD | 1,091 | 39.14% | 1.148 / 1.068 | 10,815.74 USD | yes |
| 18 | 98 | anchor_body_atr >= 0.3, range_ratio <= 0.8, risk_ticks >= 22 | 24,306.18 USD / 16,736.18 USD / 6,896.18 USD | 491 | 41.14% | 1.230 / 1.150 | 8,229.74 USD | yes |
| 19 | 117 | swing=2, window=60, anchor_body_atr >= 0.4, range_ratio <= 1, risk_ticks >= 20 | 26,010.20 USD / 16,634.22 USD / 10,134.22 USD | 490 | 39.59% | 1.265 / 1.159 | 5,430.50 USD | yes |
| 20 | 121 | swing=2, window=60, anchor_body_atr >= 0.4, range_ratio <= 1, risk_ticks >= 22 | 24,773.16 USD / 16,607.18 USD / 10,727.18 USD | 442 | 39.82% | 1.269 / 1.170 | 5,430.50 USD | yes |

Eligible trials: 187 of 300. Trials with objective above zero: 89.

Files: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
