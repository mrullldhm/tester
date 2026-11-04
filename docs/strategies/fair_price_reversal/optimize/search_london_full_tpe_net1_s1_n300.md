> **Superseded — 4 November 2026.** This is a historical record under previous rules.
> Current runs must use only `indicators/structure_swings.pine`; see the regenerated strategy results
> and current `net0` search/validation reports. These numbers do not establish current-rule performance.

# Search london_full_tpe_net1_s1_n300

Generated 2026-10-31 12:37 UTC. Strategy `fair_price_reversal`, variant `london`, space `full`, sampler `tpe`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 300 trials (7 duplicates) and 17 neighbours: 930 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 40,277.60 USD / -13,754.26 USD / -70,832.10 USD | 3,120 | 37.31% | 1.111 / 0.966 | 13,213.46 USD | yes |
| 2 | 213 | atr_mult=1.5, window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.75 | 12,869.44 USD / 5,929.44 USD / -950.56 USD | 428 | 39.02% | 1.295 / 1.120 | 3,030.64 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_london_full_tpe_net1_s1_n300.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_london_full_tpe_net1_s1_n300.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | atr_mult=1.0, window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.75 | 13,365.52 USD / 6,485.52 USD / -334.48 USD | 424 | 39.15% | 1.311 / 1.133 | 3,030.64 USD | yes |
| 2 | 3 | window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.75 | 12,893.46 USD / 5,953.46 USD / -926.54 USD | 427 | 38.88% | 1.295 / 1.120 | 3,030.64 USD | yes |
| 3 | 1 | atr_mult=1.5, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.75 | 12,869.44 USD / 5,929.44 USD / -950.56 USD | 428 | 39.02% | 1.295 / 1.120 | 3,030.64 USD | yes |
| 4 | 14 | atr_mult=1.5, window=90, minutes_from_open <= 75, range_ratio <= 0.7 | 12,725.42 USD / 5,765.42 USD / -1,134.58 USD | 429 | 38.93% | 1.291 / 1.116 | 3,174.66 USD | yes |
| 5 | 15 | atr_mult=1.5, window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.5 | 12,725.42 USD / 5,765.42 USD / -1,134.58 USD | 429 | 38.93% | 1.291 / 1.116 | 3,174.66 USD | yes |
| 6 | 9 | atr_mult=1.5, window=90, minutes_from_open <= 70, range_ratio <= 0.7, risk_atr >= 1.75 | 12,046.02 USD / 5,486.02 USD / -1,013.98 USD | 399 | 38.85% | 1.297 / 1.119 | 4,280.22 USD | yes |
| 7 | 16 | atr_mult=1.5, window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 2 | 12,253.56 USD / 5,373.56 USD / -1,446.44 USD | 422 | 38.86% | 1.283 / 1.110 | 2,926.62 USD | yes |
| 8 | 10 | atr_mult=1.5, window=90, minutes_from_open <= 80, range_ratio <= 0.7, risk_atr >= 1.75 | 12,780.80 USD / 5,360.80 USD / -1,999.20 USD | 460 | 39.13% | 1.275 / 1.102 | 3,941.22 USD | yes |
| 9 | 8 | atr_mult=1.5, window=90, range_ratio <= 0.7, risk_atr >= 1.75 | 13,867.64 USD / 5,247.64 USD / -3,072.36 USD | 518 | 38.42% | 1.262 / 1.087 | 3,531.20 USD | yes |
| 10 | 0 | atr_mult=1.5, window=60, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.75 | 6,415.76 USD / 1,365.76 USD / -4,014.24 USD | 312 | 36.54% | 1.195 / 1.037 | 5,476.86 USD | yes |
| 11 | 4 | atr_mult=1.5, swing=2, window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.75 | 9,074.38 USD / 138.40 USD / -8,403.56 USD | 581 | 36.83% | 1.164 / 1.002 | 5,741.26 USD | yes |
| 12 | 13 | atr_mult=1.5, window=90, minutes_from_open <= 75, range_ratio <= 0.8, risk_atr >= 1.75 | 10,925.90 USD / -1,374.10 USD / -13,254.10 USD | 705 | 37.59% | 1.148 / 0.984 | 8,438.44 USD | yes |
| 13 | 7 | atr_mult=1.5, target=rr1, window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.75 | 5,715.32 USD / -1,474.68 USD / -7,544.68 USD | 434 | 53.23% | 1.163 / 0.964 | 2,546.68 USD | yes |
| 14 | 6 | atr_mult=1.5, target=far, window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.75 | 3,711.30 USD / -2,328.70 USD / -8,368.70 USD | 435 | 62.30% | 1.138 / 0.923 | 3,422.88 USD | yes |
| 15 | 5 | atr_mult=1.5, target=near, window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.75 | 2,661.30 USD / -3,178.70 USD / -9,018.70 USD | 435 | 64.60% | 1.111 / 0.882 | 3,094.16 USD | yes |
| 16 | 11 | atr_mult=1.5, window=90, minutes_from_open <= 75, risk_atr >= 1.75 | 29,239.16 USD / -6,142.80 USD / -47,212.80 USD | 2,142 | 37.02% | 1.118 / 0.978 | 7,955.60 USD | yes |
| 17 | 12 | atr_mult=1.5, window=90, minutes_from_open <= 75, range_ratio <= 0.6, risk_atr >= 1.75 | 2,260.12 USD / -1,309.88 USD / -4,839.88 USD | 194 | 36.60% | 1.110 / 0.944 | 2,708.58 USD | no |

Neighbour objective: median 5,247.64 USD, worst -6,142.80 USD, 11 of 17 above zero; winner 5,929.44 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 213 | atr_mult=1.5, window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1.75 | 12,869.44 USD / 5,929.44 USD / -950.56 USD | 428 | 39.02% | 1.295 / 1.120 | 3,030.64 USD | yes |
| 2 | 224 | atr_mult=1.5, window=90, minutes_from_open <= 75, range_ratio <= 0.7, risk_atr >= 1 | 12,725.42 USD / 5,765.42 USD / -1,134.58 USD | 429 | 38.93% | 1.291 / 1.116 | 3,174.66 USD | yes |
| 3 | 220 | atr_mult=1.5, window=90, minutes_from_open <= 80, range_ratio <= 0.7, risk_atr >= 1 | 12,636.78 USD / 5,196.78 USD / -2,183.22 USD | 461 | 39.05% | 1.271 / 1.098 | 4,085.24 USD | yes |
| 4 | 245 | atr_mult=1.5, window=90, minutes_from_open <= 80, range_ratio >= 0.8 | 28,865.88 USD / 4,433.92 USD / -25,516.08 USD | 1,506 | 37.72% | 1.161 / 1.022 | 6,864.26 USD | yes |
| 5 | 182 | swing=2, window=90, anchor_body_atr <= 0.6, minutes_from_open <= 85, range_ratio <= 0.7, risk_atr >= 1.75 | 9,210.54 USD / 3,424.56 USD / -2,167.40 USD | 373 | 37.80% | 1.259 / 1.085 | 2,994.42 USD | yes |
| 6 | 178 | swing=2, window=90, anchor_body_atr <= 0.8, minutes_from_open <= 100, range_ratio <= 0.7, risk_atr >= 1.75 | 10,682.46 USD / 3,164.52 USD / -3,987.44 USD | 477 | 37.53% | 1.237 / 1.062 | 3,239.84 USD | yes |
| 7 | 184 | swing=2, window=90, anchor_body_atr <= 0.6, minutes_from_open <= 85, range_ratio <= 0.7, risk_atr >= 2 | 8,694.76 USD / 3,068.78 USD / -2,363.18 USD | 362 | 38.12% | 1.251 / 1.078 | 2,880.40 USD | yes |
| 8 | 275 | swing=2, window=90, anchor_body_atr <= 0.8, minutes_from_open <= 90, range_ratio <= 0.7 | 10,362.36 USD / 2,764.42 USD / -4,467.54 USD | 482 | 37.34% | 1.227 / 1.053 | 3,351.90 USD | yes |
| 9 | 142 | atr_mult=0.5, window=90, anchor_body_atr <= 0.5, range_ratio <= 0.9, risk_atr >= 1.5 | 10,987.44 USD / 1,887.44 USD / -7,588.54 USD | 528 | 38.07% | 1.186 / 1.028 | 6,972.24 USD | yes |
| 10 | 282 | atr_mult=1.5, target=far, window=90, anchor_body_atr >= 0.6, minutes_from_open <= 75, range_ratio >= 0.7 | 10,920.92 USD / 1,560.92 USD / -7,799.08 USD | 654 | 57.95% | 1.238 / 1.030 | 4,149.58 USD | yes |
| 11 | 286 | atr_mult=1.5, target=far, window=90, anchor_body_atr >= 0.6, minutes_from_open <= 75, range_ratio >= 0.7 | 10,920.92 USD / 1,560.92 USD / -7,799.08 USD | 654 | 57.95% | 1.238 / 1.030 | 4,149.58 USD | yes |
| 12 | 298 | atr_mult=1.5, target=far, window=90, anchor_body_atr >= 0.7, minutes_from_open <= 70, range_ratio >= 0.5 | 10,107.70 USD / 1,347.70 USD / -7,412.30 USD | 615 | 58.54% | 1.243 / 1.029 | 3,118.58 USD | yes |
| 13 | 279 | atr_mult=1.5, target=far, window=90, anchor_body_atr >= 0.6, minutes_from_open <= 70, range_ratio >= 0.7 | 10,175.64 USD / 1,335.64 USD / -7,504.36 USD | 618 | 57.93% | 1.235 / 1.028 | 3,723.40 USD | yes |
| 14 | 292 | atr_mult=1.5, target=far, window=90, anchor_body_atr >= 0.8, minutes_from_open <= 70, range_ratio >= 0.5 | 8,527.54 USD / 1,037.54 USD / -6,452.46 USD | 523 | 57.93% | 1.234 / 1.025 | 3,311.04 USD | yes |
| 15 | 40 | window=60, minutes_from_open >= 30, range_ratio <= 1 | 12,778.86 USD / 988.86 USD / -12,011.14 USD | 657 | 38.81% | 1.182 / 1.012 | 7,229.82 USD | yes |
| 16 | 156 | atr_mult=0.5, swing=2, window=90, anchor_body_atr <= 0.6, minutes_from_open <= 100, range_ratio <= 0.9, risk_atr >= 1 | 13,288.12 USD / 986.16 USD / -11,441.78 USD | 794 | 37.78% | 1.168 / 1.011 | 4,561.50 USD | yes |
| 17 | 284 | atr_mult=0.5, target=far, window=90, anchor_body_atr >= 0.7, minutes_from_open <= 70, range_ratio >= 0.6 | 8,730.96 USD / 840.96 USD / -7,049.04 USD | 552 | 57.97% | 1.226 / 1.019 | 3,440.94 USD | yes |
| 18 | 135 | window=60, range_ratio <= 0.7, risk_atr >= 1.5 | 5,905.76 USD / 835.76 USD / -4,564.24 USD | 312 | 36.22% | 1.179 / 1.022 | 5,590.88 USD | yes |
| 19 | 144 | atr_mult=0.5, window=90, anchor_body_atr <= 0.4, range_ratio <= 0.9, risk_atr >= 1 | 7,831.30 USD / 681.30 USD / -7,244.68 USD | 435 | 37.01% | 1.154 / 1.012 | 6,956.50 USD | yes |
| 20 | 216 | atr_mult=1.5, window=90, minutes_from_open <= 85, range_ratio <= 0.8, risk_atr >= 1.5 | 14,807.82 USD / 667.82 USD / -12,932.18 USD | 809 | 37.95% | 1.175 / 1.007 | 7,480.04 USD | yes |

Eligible trials: 160 of 300. Trials with objective above zero: 25.

Raw files in `results/fair_price_reversal/search/london_full_tpe_net1_s1_n300/`: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
