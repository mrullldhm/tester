# Search all_full_tpe_net1_s1_n300

Generated 2026-10-31 14:51 UTC. Strategy `supertrend_kalman`, variant `all`, space `full`, sampler `tpe`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 300 trials (0 duplicates) and 26 neighbours: 978 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 91,453.44 USD / 30,411.68 USD / -34,755.96 USD | 3,728 | 26.15% | 1.063 / 1.020 | 47,383.68 USD | yes |
| 2 | 221 | swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 118,333.16 USD / 104,967.18 USD / 90,347.18 USD | 942 | 29.19% | 1.194 / 1.169 | 39,913.60 USD | yes |

Frozen configuration: `strategies/configs/supertrend_kalman_all_full_tpe_net1_s1_n300.json`. Replay it with `python -m tvtester.cli replay strategies/configs/supertrend_kalman_all_full_tpe_net1_s1_n300.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 13 | kalman_q=0.01, swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 149,244.66 USD / 136,654.66 USD / 123,614.66 USD | 867 | 31.26% | 1.280 / 1.251 | 30,966.58 USD | yes |
| 2 | 17 | swing=5, trigger=trail, atr_ratio >= 1.1, risk_atr >= 1, risk_ticks >= 25 | 123,002.66 USD / 109,216.68 USD / 94,176.68 USD | 967 | 29.27% | 1.195 / 1.169 | 48,511.04 USD | yes |
| 3 | 24 | swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 20 | 121,738.84 USD / 107,526.88 USD / 92,686.88 USD | 958 | 29.23% | 1.199 / 1.172 | 40,127.62 USD | yes |
| 4 | 25 | swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 30 | 119,867.58 USD / 106,841.60 USD / 92,561.60 USD | 921 | 29.42% | 1.198 / 1.173 | 40,659.58 USD | yes |
| 5 | 23 | swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1 | 121,150.70 USD / 106,818.74 USD / 91,858.74 USD | 965 | 29.12% | 1.198 / 1.171 | 40,127.62 USD | yes |
| 6 | 19 | swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 9, risk_atr >= 1, risk_ticks >= 25 | 119,477.18 USD / 106,131.20 USD / 91,531.20 USD | 941 | 29.22% | 1.196 / 1.171 | 39,913.60 USD | yes |
| 7 | 22 | swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1.25, risk_ticks >= 25 | 118,729.24 USD / 105,423.26 USD / 90,863.26 USD | 938 | 29.21% | 1.195 / 1.170 | 40,335.56 USD | yes |
| 8 | 18 | swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 7, risk_atr >= 1, risk_ticks >= 25 | 118,187.18 USD / 104,841.20 USD / 90,241.20 USD | 941 | 29.22% | 1.194 / 1.169 | 39,913.60 USD | yes |
| 9 | 20 | swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_ticks >= 25 | 118,089.14 USD / 104,703.16 USD / 90,063.16 USD | 943 | 29.16% | 1.194 / 1.168 | 39,913.60 USD | yes |
| 10 | 21 | swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 0.75, risk_ticks >= 25 | 118,089.14 USD / 104,703.16 USD / 90,063.16 USD | 943 | 29.16% | 1.194 / 1.168 | 39,913.60 USD | yes |
| 11 | 1 | swing=5, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 108,066.44 USD / 92,764.48 USD / 71,698.50 USD | 1,078 | 29.41% | 1.152 / 1.128 | 30,054.20 USD | yes |
| 12 | 12 | st_factor=2, swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 83,997.72 USD / 71,897.72 USD / 59,347.72 USD | 814 | 29.98% | 1.155 / 1.130 | 38,100.30 USD | yes |
| 13 | 16 | swing=5, trigger=trail, atr_ratio >= 1.2, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 79,244.28 USD / 70,814.28 USD / 61,884.28 USD | 586 | 30.55% | 1.200 / 1.175 | 26,799.14 USD | yes |
| 14 | 15 | swing=5, trigger=trail, atr_ratio >= 1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 66,347.56 USD / 47,871.58 USD / 29,395.60 USD | 1,222 | 28.07% | 1.086 / 1.061 | 76,443.44 USD | yes |
| 15 | 6 | swing=5, trigger=trail, vol=rvi, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 72,623.02 USD / 45,404.98 USD / 26,889.00 USD | 1,049 | 31.17% | 1.088 / 1.054 | 62,780.44 USD | yes |
| 16 | 10 | trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 63,467.14 USD / 41,451.16 USD / 22,491.16 USD | 1,043 | 28.00% | 1.113 / 1.072 | 39,929.88 USD | yes |
| 17 | 4 | swing=5, trigger=trail, vol=stop_atr:3, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 47,313.32 USD / 31,893.32 USD / 13,097.34 USD | 1,034 | 28.72% | 1.100 / 1.065 | 41,288.62 USD | yes |
| 18 | 2 | swing=5, trigger=trail, vol=none, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 54,803.08 USD / 26,409.06 USD / 6,413.08 USD | 1,146 | 30.54% | 1.060 / 1.028 | 79,350.94 USD | yes |
| 19 | 8 | exit=flip, swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 46,098.78 USD / 21,008.78 USD / -4,721.22 USD | 1,361 | 37.40% | 1.102 / 1.045 | 21,755.14 USD | yes |
| 20 | 0 | swing=5, trigger=st, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 24,194.06 USD / 18,748.08 USD / 7,868.08 USD | 397 | 29.47% | 1.092 / 1.070 | 18,928.64 USD | yes |
| 21 | 11 | swing=5, trail_mult=2, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 551.40 USD / -6,088.60 USD / -14,068.60 USD | 430 | 30.47% | 1.002 / 0.978 | 32,357.02 USD | yes |
| 22 | 9 | rr=2, swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 5,230.76 USD / -8,355.22 USD / -21,589.14 USD | 1,062 | 34.56% | 1.008 / 0.988 | 47,282.14 USD | yes |
| 23 | 7 | exit=trail, swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 778.30 USD / -30,641.70 USD / -62,431.70 USD | 1,585 | 34.57% | 1.003 / 0.885 | 25,467.14 USD | yes |
| 24 | 14 | swing=5, trigger=trail, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | -20,638.84 USD / -51,360.80 USD / -81,980.80 USD | 2,042 | 26.74% | 0.982 / 0.955 | 70,704.46 USD | yes |
| 25 | 3 | swing=5, trigger=trail, vol=stop_atr:1.5, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 6,707.90 USD / 5,227.90 USD / 1,347.90 USD | 105 | 30.48% | 1.200 / 1.150 | 5,608.84 USD | no |
| 26 | 5 | swing=5, trigger=trail, vol=atr_ratio:1.0, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 0.00 USD / 0.00 USD / 0.00 USD | 0 | — | — / — | 0.00 USD | no |

Neighbour objective: median 61,710.92 USD, worst -49,602.81 USD, 21 of 26 above zero; winner 107,945.17 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 221 | swing=5, trigger=trail, atr_ratio >= 1.1, hours_since_open >= 8, risk_atr >= 1, risk_ticks >= 25 | 118,333.16 USD / 104,967.18 USD / 90,347.18 USD | 942 | 29.19% | 1.194 / 1.169 | 39,913.60 USD | yes |
| 2 | 190 | exit=flip, hours_since_open >= 10, risk_ticks >= 90 | 114,441.84 USD / 97,011.84 USD / 77,841.84 USD | 808 | 38.86% | 1.315 / 1.260 | 20,851.90 USD | yes |
| 3 | 177 | exit=flip, vol=none, atr_ratio <= 1.4, hours_since_open >= 8, risk_atr >= 1.75, risk_ticks >= 95 | 111,710.20 USD / 90,560.20 USD / 68,130.20 USD | 990 | 40.00% | 1.258 / 1.204 | 16,146.48 USD | yes |
| 4 | 194 | rr=2, vol=rvi, atr_ratio <= 1.3, hours_since_open >= 11, risk_atr >= 0.5, risk_ticks >= 55 | 112,091.34 USD / 85,461.44 USD / 65,601.44 USD | 1,333 | 36.08% | 1.144 / 1.107 | 59,641.46 USD | yes |
| 5 | 213 | exit=flip, vol=rvi, hours_since_open >= 11, risk_ticks >= 45 | 145,968.56 USD / 81,992.58 USD / 16,076.60 USD | 3,172 | 38.90% | 1.134 / 1.073 | 39,421.54 USD | yes |
| 6 | 209 | exit=flip, vol=rvi, hours_since_open >= 11, risk_ticks >= 40 | 147,287.98 USD / 79,882.00 USD / 9,110.04 USD | 3,401 | 38.49% | 1.128 / 1.067 | 42,038.32 USD | yes |
| 7 | 188 | exit=flip, vol=none, atr_ratio <= 1.3, hours_since_open >= 10, risk_atr >= 0.5, risk_ticks >= 50 | 121,950.88 USD / 77,330.88 USD / 29,330.88 USD | 2,256 | 35.59% | 1.150 / 1.092 | 26,289.20 USD | yes |
| 8 | 186 | exit=flip, vol=none, atr_ratio <= 1.3, hours_since_open >= 10, risk_atr >= 1, risk_ticks >= 75 | 102,438.06 USD / 77,128.06 USD / 50,758.06 USD | 1,197 | 37.93% | 1.205 / 1.150 | 20,621.40 USD | yes |
| 9 | 156 | exit=flip, vol=rvi, atr_ratio <= 1.1, hours_since_open >= 0, risk_ticks >= 65 | 101,993.74 USD / 76,093.74 USD / 54,213.74 USD | 1,213 | 34.05% | 1.224 / 1.161 | 33,986.26 USD | yes |
| 10 | 59 | exit=flip, vol=none, atr_ratio <= 1.4, hours_since_open >= 4, risk_ticks >= 90 | 99,060.52 USD / 74,530.52 USD / 48,260.52 USD | 1,174 | 38.42% | 1.195 / 1.143 | 20,837.58 USD | yes |
| 11 | 183 | exit=flip, vol=none, atr_ratio <= 1.4, hours_since_open >= 6, risk_atr >= 1, risk_ticks >= 70 | 108,957.22 USD / 71,707.22 USD / 33,397.22 USD | 1,839 | 37.63% | 1.148 / 1.095 | 27,552.28 USD | yes |
| 12 | 200 | exit=flip, vol=rvi, hours_since_open >= 10, risk_ticks >= 35 | 144,777.22 USD / 71,055.26 USD / -5,308.66 USD | 3,839 | 37.22% | 1.115 / 1.054 | 48,394.04 USD | yes |
| 13 | 39 | exit=flip, trigger=st, vol=none, atr_ratio <= 1.4, risk_ticks >= 70, rvi_side <= 80 | 85,807.72 USD / 70,147.72 USD / 51,457.72 USD | 814 | 37.84% | 1.263 / 1.208 | 16,295.42 USD | yes |
| 14 | 176 | swing=5, atr_ratio <= 1.5, hours_since_open >= 13, risk_atr >= 1.25, risk_ticks >= 75 | 89,885.86 USD / 68,181.84 USD / 50,711.84 USD | 807 | 31.60% | 1.132 / 1.098 | 40,994.52 USD | yes |
| 15 | 296 | kalman_q=0.01, rr=2, atr_ratio <= 1.5, hours_since_open >= 9, risk_atr >= 1.75, risk_ticks >= 60 | 99,768.72 USD / 67,596.76 USD / 48,144.90 USD | 1,764 | 35.71% | 1.093 / 1.061 | 42,459.34 USD | yes |
| 16 | 203 | exit=flip, kalman_q=0.01, trigger=trail, vol=none, atr_ratio <= 1.3, hours_since_open >= 9, risk_atr >= 1, risk_ticks >= 50 | 102,570.28 USD / 67,190.28 USD / 33,740.28 USD | 1,786 | 35.55% | 1.158 / 1.100 | 17,238.12 USD | yes |
| 17 | 71 | exit=flip, kalman_q=0.01, vol=none, atr_ratio <= 1.4, hours_since_open >= 4, risk_ticks >= 100 | 90,305.34 USD / 66,525.34 USD / 40,435.34 USD | 1,133 | 38.48% | 1.167 / 1.120 | 28,699.28 USD | yes |
| 18 | 104 | exit=flip, vol=rvi, atr_ratio <= 1.2, hours_since_open >= 2, risk_atr >= 2.5, risk_ticks >= 60 | 98,127.54 USD / 66,357.54 USD / 34,127.54 USD | 1,523 | 34.21% | 1.177 / 1.115 | 23,216.98 USD | yes |
| 19 | 55 | exit=flip, vol=rvi, atr_ratio <= 1.4, hours_since_open >= 0, risk_ticks >= 70 | 102,784.86 USD / 65,074.86 USD / 26,764.86 USD | 1,857 | 37.37% | 1.141 / 1.087 | 28,902.00 USD | yes |
| 20 | 192 | exit=flip, vol=none, atr_ratio <= 1.1, hours_since_open >= 10, risk_atr >= 0.5, risk_ticks >= 40 | 101,129.94 USD / 63,789.94 USD / 27,383.96 USD | 1,903 | 32.32% | 1.160 / 1.097 | 31,488.72 USD | yes |

Eligible trials: 195 of 300. Trials with objective above zero: 121.

Raw files in `results/supertrend_kalman/search/all_full_tpe_net1_s1_n300/`: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
