# Search asia_filters_random_net1_s1_n200

Generated 2026-10-31 13:24 UTC. Strategy `supertrend_kalman`, variant `asia`, space `filters`, sampler `random`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 200 trials (0 duplicates) and 9 neighbours: 627 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 15,844.42 USD / -3,495.58 USD / -22,835.58 USD | 979 | 45.45% | 1.200 / 0.961 | 5,922.66 USD | yes |
| 2 | 93 | er >= 0.1, risk_atr <= 3, risk_ticks <= 90 | 8,558.88 USD / 1,538.88 USD / -5,481.12 USD | 356 | 42.98% | 1.333 / 1.051 | 3,578.68 USD | yes |

Frozen configuration: `strategies/configs/supertrend_kalman_asia_filters_random_net1_s1_n200.json`. Replay it with `python -m tvtester.cli replay strategies/configs/supertrend_kalman_asia_filters_random_net1_s1_n200.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | er >= 0.1, risk_atr <= 3.25, risk_ticks <= 90 | 11,913.66 USD / 3,673.66 USD / -4,566.34 USD | 417 | 45.56% | 1.416 / 1.110 | 2,792.26 USD | yes |
| 2 | 6 | er >= 0.1, risk_atr <= 3 | 10,742.70 USD / 3,542.70 USD / -3,657.30 USD | 365 | 43.84% | 1.395 / 1.113 | 3,578.68 USD | yes |
| 3 | 8 | er >= 0.1, risk_atr <= 3, risk_ticks <= 95 | 9,124.86 USD / 2,084.86 USD / -4,955.14 USD | 357 | 43.14% | 1.355 / 1.070 | 3,578.68 USD | yes |
| 4 | 7 | er >= 0.1, risk_atr <= 3, risk_ticks <= 85 | 8,222.90 USD / 1,222.90 USD / -5,777.10 USD | 355 | 42.82% | 1.320 / 1.041 | 3,578.68 USD | yes |
| 5 | 3 | er >= 0.1, risk_ticks <= 90 | 11,744.78 USD / 664.78 USD / -10,415.22 USD | 561 | 44.03% | 1.296 / 1.014 | 3,598.42 USD | yes |
| 6 | 1 | er >= 0.05, risk_atr <= 3, risk_ticks <= 90 | 8,357.94 USD / -1,582.06 USD / -11,522.06 USD | 503 | 44.33% | 1.224 / 0.963 | 4,046.48 USD | yes |
| 7 | 0 | risk_atr <= 3, risk_ticks <= 90 | 9,263.08 USD / -3,456.92 USD / -16,176.92 USD | 646 | 44.89% | 1.194 / 0.937 | 5,302.56 USD | yes |
| 8 | 2 | er >= 0.15, risk_atr <= 3, risk_ticks <= 90 | 6,132.94 USD / 1,152.94 USD / -3,827.06 USD | 253 | 41.90% | 1.329 / 1.053 | 4,020.84 USD | no |
| 9 | 4 | er >= 0.1, risk_atr <= 2.75, risk_ticks <= 90 | 5,100.08 USD / -719.92 USD / -6,539.92 USD | 296 | 41.55% | 1.230 / 0.972 | 3,880.74 USD | no |

Neighbour objective: median 1,152.94 USD, worst -3,456.92 USD, 6 of 9 above zero; winner 1,538.88 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 93 | er >= 0.1, risk_atr <= 3, risk_ticks <= 90 | 8,558.88 USD / 1,538.88 USD / -5,481.12 USD | 356 | 42.98% | 1.333 / 1.051 | 3,578.68 USD | yes |
| 2 | 140 | er <= 0.6, risk_atr <= 5, risk_ticks <= 200 | 19,111.10 USD / 451.10 USD / -18,208.90 USD | 945 | 45.61% | 1.267 / 1.005 | 4,418.44 USD | yes |
| 3 | 87 | er <= 0.75, risk_atr <= 5, rvi_side >= 65 | 6,073.30 USD / -546.70 USD / -7,166.70 USD | 335 | 43.58% | 1.240 / 0.981 | 2,595.72 USD | yes |
| 4 | 33 | rvi_side >= 55 | 14,150.88 USD / -789.12 USD / -15,729.12 USD | 756 | 44.84% | 1.236 / 0.988 | 5,246.38 USD | yes |
| 5 | 148 | atr_ratio <= 1, risk_atr <= 4.75 | 17,191.40 USD / -1,168.60 USD / -19,528.60 USD | 930 | 45.81% | 1.239 / 0.986 | 4,366.28 USD | yes |
| 6 | 43 | risk_atr <= 3.25, rvi_side >= 30 | 13,744.80 USD / -1,255.20 USD / -16,255.20 USD | 760 | 46.32% | 1.232 / 0.981 | 5,876.78 USD | yes |
| 7 | 136 | atr_ratio >= 0.6, risk_ticks <= 85, rvi_side <= 65 | 6,963.66 USD / -1,256.34 USD / -9,476.34 USD | 417 | 44.36% | 1.203 / 0.968 | 3,909.94 USD | yes |
| 8 | 55 | er <= 0.4, hours_since_open <= 17 | 16,935.52 USD / -1,304.48 USD / -19,544.48 USD | 924 | 45.78% | 1.230 / 0.985 | 5,576.08 USD | yes |
| 9 | 164 | atr_ratio <= 1.9, rvi_side >= 65 | 5,241.14 USD / -1,538.86 USD / -8,318.86 USD | 343 | 43.15% | 1.195 / 0.950 | 2,781.80 USD | yes |
| 10 | 163 | atr_ratio <= 1.4, er <= 0.7, risk_atr <= 3.25 | 13,178.82 USD / -1,801.18 USD / -16,781.18 USD | 759 | 46.25% | 1.223 / 0.973 | 5,876.78 USD | yes |
| 11 | 25 | hours_since_open <= 9, risk_atr >= 1.75, risk_ticks <= 160 | 15,356.62 USD / -1,923.38 USD / -19,203.38 USD | 869 | 45.68% | 1.230 / 0.975 | 3,704.16 USD | yes |
| 12 | 130 | hours_since_open <= 14, risk_ticks <= 145 | 17,036.68 USD / -2,043.32 USD / -21,123.32 USD | 966 | 45.24% | 1.234 / 0.976 | 4,418.44 USD | yes |
| 13 | 169 | risk_ticks <= 160 | 17,036.68 USD / -2,043.32 USD / -21,123.32 USD | 966 | 45.24% | 1.234 / 0.976 | 4,418.44 USD | yes |
| 14 | 19 | risk_atr <= 5 | 16,160.90 USD / -2,699.10 USD / -21,559.10 USD | 955 | 45.65% | 1.210 / 0.969 | 5,576.08 USD | yes |
| 15 | 21 | er <= 0.65, hours_since_open >= 2, risk_ticks <= 110 | 15,986.98 USD / -2,793.02 USD / -21,573.02 USD | 951 | 45.11% | 1.229 / 0.965 | 4,748.64 USD | yes |
| 16 | 117 | hours_since_open <= 21, risk_atr >= 1.5, rvi_side <= 75 | 14,318.68 USD / -2,861.32 USD / -20,041.32 USD | 866 | 46.65% | 1.199 / 0.965 | 5,922.66 USD | yes |
| 17 | 109 | er <= 0.7, rvi_side >= 60 | 8,254.68 USD / -2,985.32 USD / -14,225.32 USD | 566 | 44.17% | 1.189 / 0.941 | 3,458.24 USD | yes |
| 18 | 15 | risk_atr >= 0.75, risk_ticks <= 135, rvi_side <= 70 | 12,793.90 USD / -3,106.10 USD / -19,006.10 USD | 805 | 45.47% | 1.205 / 0.957 | 4,100.40 USD | yes |
| 19 | 181 | risk_ticks <= 110 | 15,688.94 USD / -3,131.06 USD / -21,951.06 USD | 953 | 45.02% | 1.223 / 0.961 | 4,748.64 USD | yes |
| 20 | 121 | risk_atr <= 4 | 14,612.00 USD / -3,148.00 USD / -20,908.00 USD | 900 | 45.56% | 1.199 / 0.962 | 5,576.08 USD | yes |

Eligible trials: 51 of 200. Trials with objective above zero: 2.

Raw files in `results/supertrend_kalman/search/asia_filters_random_net1_s1_n200/`: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
