# Price Reversal v2 (hourly anchors, entry cap, fixed TP), CL1!: feature association, h02

Generated 2026-11-11 20:20 UTC by `python -m tvtester.cli features price_reversal_v2 --variant h02`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `anchor=h02`, `window=60`, `atr_mult=0.5`, `swing=1`, `target=far`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## Baseline, commission included: 1,837 trades, net 8,565.26 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 4 .. 18 | 399 | 58.65% | 4.25 USD | -3.51 USD .. 12.46 USD | 1,696.02 USD |
| 18 .. 27 | 338 | 50.00% | 0.06 USD | -8.78 USD .. 10.08 USD | 21.24 USD |
| 27 .. 36 | 369 | 58.27% | 18.66 USD | 9.19 USD .. 28.27 USD | 6,886.62 USD |
| 36 .. 47 | 373 | 45.31% | 3.30 USD | -5.41 USD .. 12.35 USD | 1,230.54 USD |
| 47 .. 59 | 358 | 46.93% | -3.55 USD | -12.00 USD .. 5.30 USD | -1,269.16 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.1501 | 735 | 54.69% | 3.72 USD | -1.99 USD .. 10.03 USD | 2,735.30 USD |
| 0.1501 .. 0.5072 | 367 | 52.04% | 13.75 USD | 3.05 USD .. 24.32 USD | 5,044.66 USD |
| 0.5072 .. 0.8102 | 367 | 51.23% | 2.82 USD | -6.13 USD .. 11.48 USD | 1,034.66 USD |
| 0.8102 .. 5.08 | 368 | 47.28% | -0.68 USD | -9.89 USD .. 8.44 USD | -249.36 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 2 .. 4 | 487 | 45.79% | -1.21 USD | -4.49 USD .. 1.86 USD | -587.74 USD |
| 4 .. 5 | 280 | 47.14% | -2.02 USD | -7.51 USD .. 3.69 USD | -565.60 USD |
| 5 .. 7 | 397 | 51.64% | -0.32 USD | -5.77 USD .. 5.52 USD | -125.94 USD |
| 7 .. 10 | 329 | 55.62% | 5.95 USD | -3.08 USD .. 15.67 USD | 1,957.42 USD |
| 10 .. 81 | 344 | 61.63% | 22.93 USD | 7.35 USD .. 39.74 USD | 7,887.12 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.5823 .. 2.163 | 368 | 41.58% | 8.13 USD | 0.08 USD .. 16.33 USD | 2,990.64 USD |
| 2.163 .. 2.676 | 367 | 48.50% | -3.58 USD | -11.61 USD .. 3.90 USD | -1,315.34 USD |
| 2.676 .. 3.194 | 367 | 50.14% | 6.23 USD | -3.33 USD .. 16.32 USD | 2,284.66 USD |
| 3.194 .. 3.952 | 367 | 56.13% | 5.95 USD | -1.42 USD .. 13.76 USD | 2,184.66 USD |
| 3.952 .. 14.9 | 368 | 63.59% | 6.58 USD | -4.25 USD .. 17.28 USD | 2,420.64 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.2809 .. 0.7082 | 365 | 50.96% | -1.20 USD | -9.12 USD .. 7.08 USD | -437.30 USD |
| 0.7082 .. 0.8654 | 365 | 54.79% | 10.53 USD | 2.37 USD .. 18.85 USD | 3,842.70 USD |
| 0.8654 .. 1.043 | 364 | 48.63% | -1.47 USD | -9.02 USD .. 6.09 USD | -533.28 USD |
| 1.043 .. 1.316 | 365 | 53.15% | 4.39 USD | -3.06 USD .. 12.11 USD | 1,602.70 USD |
| 1.316 .. 5.238 | 365 | 52.88% | 11.02 USD | -0.15 USD .. 23.18 USD | 4,022.70 USD |
| NaN | 13 | 38.46% | 5.21 USD | -14.69 USD .. 21.36 USD | 67.74 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 930 | 53.87% | 6.26 USD | 0.04 USD .. 12.55 USD | 5,821.40 USD |
| Short | 907 | 50.06% | 3.03 USD | -3.35 USD .. 9.12 USD | 2,743.86 USD |

### `weekday` (America/New_York clock)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Mon | 349 | 57.02% | 15.49 USD | 6.52 USD .. 23.92 USD | 5,407.02 USD |
| Sun | 427 | 52.46% | 3.12 USD | -7.63 USD .. 13.59 USD | 1,333.46 USD |
| Thu | 337 | 49.55% | 1.44 USD | -7.09 USD .. 10.49 USD | 485.26 USD |
| Tue | 359 | 49.30% | 0.69 USD | -9.41 USD .. 11.80 USD | 246.82 USD |
| Wed | 365 | 51.51% | 2.99 USD | -5.02 USD .. 10.86 USD | 1,092.70 USD |
