# Search asia_filters_random_net1_s1_n200

Generated 2026-10-31 05:44 UTC. Strategy `fair_price_reversal`, variant `asia`, space `filters`, sampler `random`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 3 neighbours: 609 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 815.16 USD / -4,084.84 USD / -10,584.84 USD | 342 | 50.29% | 1.030 / 0.869 | 3,940.30 USD | yes |
| 2 | 48 | minutes_from_open >= 15 | 1,215.96 USD / -2,924.04 USD / -8,744.04 USD | 302 | 50.99% | 1.053 / 0.889 | 2,464.22 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_asia_filters_random_net1_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_asia_filters_random_net1_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 815.16 USD / -4,084.84 USD / -10,584.84 USD | 342 | 50.29% | 1.030 / 0.869 | 3,940.30 USD | yes |
| 2 | 1 | minutes_from_open >= 10 | 301.24 USD / -4,388.76 USD / -10,828.76 USD | 338 | 50.00% | 1.011 / 0.858 | 3,940.30 USD | yes |
| 3 | 2 | minutes_from_open >= 20 | 3,847.46 USD / 867.46 USD / -3,442.54 USD | 227 | 54.19% | 1.247 / 1.048 | 2,182.36 USD | no |

Neighbour objective: median -4,084.84 USD, worst -4,388.76 USD, 1 of 3 above zero; winner -2,924.04 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 48 | minutes_from_open >= 15 | 1,215.96 USD / -2,924.04 USD / -8,744.04 USD | 302 | 50.99% | 1.053 / 0.889 | 2,464.22 USD | yes |
| 2 | 47 | anchor_body_atr <= 1.2 | 1,429.98 USD / -2,970.02 USD / -8,970.02 USD | 301 | 51.16% | 1.064 / 0.885 | 3,506.28 USD | yes |
| 3 | 20 | anchor_body_atr <= 1.4 | 1,345.76 USD / -3,194.24 USD / -9,334.24 USD | 312 | 50.64% | 1.057 / 0.883 | 3,506.28 USD | yes |
| 4 | 146 | anchor_body_atr <= 1.5 | 1,337.52 USD / -3,322.48 USD / -9,582.48 USD | 324 | 50.93% | 1.053 / 0.885 | 3,506.28 USD | yes |
| 5 | 179 | minutes_from_open <= 65, risk_atr >= 1.75, risk_ticks <= 44 | 921.54 USD / -3,718.46 USD / -9,958.46 USD | 323 | 50.46% | 1.042 / 0.857 | 1,980.20 USD | yes |
| 6 | 191 | anchor_body_atr <= 1.6 | 781.44 USD / -3,958.56 USD / -10,298.56 USD | 328 | 50.30% | 1.031 / 0.866 | 3,506.28 USD | yes |
| 7 | 0 | baseline | 815.16 USD / -4,084.84 USD / -10,584.84 USD | 342 | 50.29% | 1.030 / 0.869 | 3,940.30 USD | yes |
| 8 | 22 | minutes_from_open <= 115 | 815.16 USD / -4,084.84 USD / -10,584.84 USD | 342 | 50.29% | 1.030 / 0.869 | 3,940.30 USD | yes |
| 9 | 95 | minutes_from_open <= 30 | 815.16 USD / -4,084.84 USD / -10,584.84 USD | 342 | 50.29% | 1.030 / 0.869 | 3,940.30 USD | yes |
| 10 | 161 | risk_atr >= 1 | 815.16 USD / -4,084.84 USD / -10,584.84 USD | 342 | 50.29% | 1.030 / 0.869 | 3,940.30 USD | yes |
| 11 | 177 | minutes_from_open <= 110 | 815.16 USD / -4,084.84 USD / -10,584.84 USD | 342 | 50.29% | 1.030 / 0.869 | 3,940.30 USD | yes |
| 12 | 34 | minutes_from_open <= 95, risk_atr >= 1.75 | 779.18 USD / -4,120.82 USD / -10,620.82 USD | 341 | 50.15% | 1.029 / 0.868 | 3,940.30 USD | yes |
| 13 | 8 | risk_ticks <= 52 | 593.40 USD / -4,126.60 USD / -10,446.60 USD | 330 | 50.61% | 1.025 / 0.850 | 2,802.26 USD | yes |
| 14 | 164 | risk_atr >= 2 | 695.26 USD / -4,184.74 USD / -10,664.74 USD | 337 | 49.85% | 1.026 / 0.866 | 3,940.30 USD | yes |
| 15 | 17 | minutes_from_open >= 10, range_ratio <= 1.7 | -368.16 USD / -4,758.16 USD / -10,538.16 USD | 308 | 50.00% | 0.984 / 0.820 | 3,346.28 USD | yes |
| 16 | 70 | minutes_from_open <= 50, range_ratio <= 1.9 | -188.46 USD / -4,908.46 USD / -10,868.46 USD | 323 | 50.15% | 0.992 / 0.826 | 3,940.30 USD | yes |
| 17 | 115 | minutes_from_open <= 80, range_ratio <= 1.9 | -188.46 USD / -4,908.46 USD / -10,868.46 USD | 323 | 50.15% | 0.992 / 0.826 | 3,940.30 USD | yes |
| 18 | 92 | risk_ticks <= 38 | -722.28 USD / -5,282.28 USD / -11,442.28 USD | 314 | 50.00% | 0.966 / 0.788 | 2,345.22 USD | yes |
| 19 | 98 | risk_atr <= 6 | -622.48 USD / -5,322.48 USD / -11,382.48 USD | 324 | 49.07% | 0.976 / 0.824 | 3,940.30 USD | yes |
| 20 | 129 | risk_atr <= 5.75 | -816.40 USD / -5,496.40 USD / -11,536.40 USD | 320 | 48.75% | 0.969 / 0.817 | 3,940.30 USD | yes |

Eligible trials: 24 of 200. Trials with objective above zero: 0.

Files: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
