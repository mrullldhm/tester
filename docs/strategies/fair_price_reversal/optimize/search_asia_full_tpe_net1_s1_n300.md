> **Superseded — 4 November 2026.** This is a historical record under previous rules.
> Current runs must use only `indicators/structure_swings.pine`; see the regenerated strategy results
> and current `net0` search/validation reports. These numbers do not establish current-rule performance.

# Search asia_full_tpe_net1_s1_n300

Generated 2026-10-31 12:37 UTC. Strategy `fair_price_reversal`, variant `asia`, space `full`, sampler `tpe`, seed 1, objective `net1` (net profit + open P&L at 1 tick), at least 300 closed trades.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). The winner is the best of 300 trials (57 duplicates) and 10 neighbours: 759 engine runs. Nothing here shows a tradable edge: out-of-sample validation is a later feature.

## Baseline vs winner

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | baseline | 815.16 USD / -4,084.84 USD / -10,584.84 USD | 342 | 50.29% | 1.030 / 0.869 | 3,940.30 USD | yes |
| 2 | 252 | atr_mult=0.5, swing=2, target=far, range_ratio <= 1.2 | 3,604.86 USD / -1,345.14 USD / -6,295.14 USD | 357 | 61.90% | 1.229 / 0.927 | 1,677.18 USD | yes |

Frozen configuration: `strategies/configs/fair_price_reversal_asia_full_tpe_net1_s1_n300.json`. Replay it with `python -m tvtester.cli replay strategies/configs/fair_price_reversal_asia_full_tpe_net1_s1_n300.json`.

## Neighbours of the winner (diagnostic, never candidates)

Each searched parameter one step either way, each filter switched off, each threshold one step either way. A winner whose neighbours collapse is a spike, not a plateau.

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | atr_mult=1.0, swing=2, target=far, range_ratio <= 1.2 | 4,177.48 USD / -1,692.52 USD / -7,562.52 USD | 426 | 62.21% | 1.220 / 0.924 | 1,945.22 USD | yes |
| 2 | 9 | atr_mult=0.5, swing=2, target=far, range_ratio <= 1.3 | 3,220.24 USD / -2,189.76 USD / -7,599.76 USD | 388 | 61.08% | 1.186 / 0.892 | 1,807.18 USD | yes |
| 3 | 4 | atr_mult=0.5, swing=2, target=near, range_ratio <= 1.2 | 2,184.86 USD / -2,585.14 USD / -7,355.14 USD | 357 | 64.43% | 1.155 / 0.845 | 1,851.00 USD | yes |
| 4 | 8 | atr_mult=0.5, swing=2, target=far, range_ratio <= 1.1 | 1,149.88 USD / -3,120.12 USD / -7,390.12 USD | 306 | 60.46% | 1.081 / 0.812 | 1,974.82 USD | yes |
| 5 | 5 | atr_mult=0.5, swing=2, range_ratio <= 1.2 | 1,184.86 USD / -3,845.14 USD / -10,745.14 USD | 357 | 47.90% | 1.050 / 0.863 | 2,246.36 USD | yes |
| 6 | 7 | atr_mult=0.5, swing=2, target=far | 1,016.08 USD / -5,993.92 USD / -13,003.92 USD | 496 | 59.07% | 1.037 / 0.811 | 5,099.92 USD | yes |
| 7 | 6 | atr_mult=0.5, swing=2, target=rr2, range_ratio <= 1.2 | -2,877.10 USD / -8,767.10 USD / -15,317.10 USD | 355 | 30.70% | 0.908 / 0.759 | 6,641.58 USD | yes |
| 8 | 2 | atr_mult=0.5, swing=1, target=far, range_ratio <= 1.2 | -467.46 USD / -11,737.46 USD / -23,007.46 USD | 773 | 54.59% | 0.987 / 0.719 | 2,643.86 USD | yes |
| 9 | 0 | atr_mult=0.5, swing=2, target=far, window=60, range_ratio <= 1.2 | -9,167.78 USD / -24,977.78 USD / -40,787.78 USD | 1,089 | 55.10% | 0.846 / 0.640 | 10,563.82 USD | yes |
| 10 | 3 | atr_mult=0.5, target=far, range_ratio <= 1.2 | 1,246.30 USD / -1,303.70 USD / -3,853.70 USD | 185 | 63.78% | 1.146 / 0.868 | 1,772.46 USD | no |

Neighbour objective: median -3,482.63 USD, worst -24,977.78 USD, 0 of 10 above zero; winner -1,345.14 USD.

## Top 20 trials

| # | Trial | Configuration | Net 0 / 1 / 2 ticks | Trades (0) | % prof. (0) | PF (0 / 1) | Max DD (0) | Eligible |
|---|---|---|---|---|---|---|---|---|
| 1 | 252 | atr_mult=0.5, swing=2, target=far, range_ratio <= 1.2 | 3,604.86 USD / -1,345.14 USD / -6,295.14 USD | 357 | 61.90% | 1.229 / 0.927 | 1,677.18 USD | yes |
| 2 | 256 | atr_mult=0.5, swing=2, target=far, range_ratio <= 1.2 | 3,604.86 USD / -1,345.14 USD / -6,295.14 USD | 357 | 61.90% | 1.229 / 0.927 | 1,677.18 USD | yes |
| 3 | 260 | atr_mult=0.5, swing=2, target=far, range_ratio <= 1.2 | 3,604.86 USD / -1,345.14 USD / -6,295.14 USD | 357 | 61.90% | 1.229 / 0.927 | 1,677.18 USD | yes |
| 4 | 264 | atr_mult=0.5, swing=2, target=far, range_ratio <= 1.2 | 3,604.86 USD / -1,345.14 USD / -6,295.14 USD | 357 | 61.90% | 1.229 / 0.927 | 1,677.18 USD | yes |
| 5 | 268 | atr_mult=0.5, swing=2, target=far, range_ratio <= 1.2 | 3,604.86 USD / -1,345.14 USD / -6,295.14 USD | 357 | 61.90% | 1.229 / 0.927 | 1,677.18 USD | yes |
| 6 | 272 | atr_mult=0.5, swing=2, target=far, range_ratio <= 1.2 | 3,604.86 USD / -1,345.14 USD / -6,295.14 USD | 357 | 61.90% | 1.229 / 0.927 | 1,677.18 USD | yes |
| 7 | 230 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 8 | 233 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 9 | 237 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 10 | 241 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 11 | 244 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 12 | 250 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 13 | 251 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 14 | 253 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 15 | 257 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 16 | 261 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 17 | 265 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 18 | 269 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 19 | 273 | swing=2, target=far, range_ratio <= 1.2 | 4,672.76 USD / -1,667.24 USD / -8,007.24 USD | 462 | 62.55% | 1.230 / 0.930 | 1,953.36 USD | yes |
| 20 | 267 | atr_mult=1.5, swing=2, target=far, range_ratio <= 1.2 | 4,359.04 USD / -1,810.96 USD / -7,980.96 USD | 448 | 62.28% | 1.219 / 0.922 | 1,953.46 USD | yes |

Eligible trials: 162 of 300. Trials with objective above zero: 0.

Raw files in `results/fair_price_reversal/search/asia_full_tpe_net1_s1_n300/`: `trials.csv` (every trial, all scenarios), `neighbours.csv`, `run.json` (space, hashes, versions).
