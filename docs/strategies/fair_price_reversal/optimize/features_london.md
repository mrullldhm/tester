# Fair Price Reversal (LuxAlgo 9:29 ET), CL1! sessions: feature association, london

Generated 2026-11-04 15:06 UTC by `python -m tvtester.cli features fair_price_reversal --variant london`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `session=london`, `window=30`, `atr_mult=1.5`, `swing=1`, `target=rr2`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## Baseline, commission included: 1,635 trades, net 11,237.30 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 4 .. 11 | 347 | 32.28% | 2.49 USD | -17.42 USD .. 22.07 USD | 865.06 USD |
| 11 .. 15 | 309 | 32.36% | -9.68 USD | -25.76 USD .. 7.92 USD | -2,992.18 USD |
| 15 .. 20 | 379 | 41.69% | 21.73 USD | 3.94 USD .. 39.48 USD | 8,236.42 USD |
| 20 .. 24 | 291 | 37.11% | 12.06 USD | -8.11 USD .. 31.73 USD | 3,510.18 USD |
| 24 .. 29 | 309 | 34.95% | 5.24 USD | -15.51 USD .. 24.82 USD | 1,617.82 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.3554 | 654 | 37.00% | 7.89 USD | -7.21 USD .. 21.34 USD | 5,160.92 USD |
| 0.3554 .. 0.5556 | 327 | 36.09% | 4.91 USD | -12.58 USD .. 21.94 USD | 1,605.46 USD |
| 0.5556 .. 0.9491 | 327 | 35.17% | 9.04 USD | -10.78 USD .. 28.65 USD | 2,955.46 USD |
| 0.9491 .. 4.345 | 327 | 33.94% | 4.63 USD | -12.52 USD .. 21.00 USD | 1,515.46 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 3 .. 7 | 382 | 30.63% | -4.39 USD | -11.21 USD .. 2.83 USD | -1,675.64 USD |
| 7 .. 9 | 314 | 40.76% | 17.22 USD | 5.54 USD .. 28.68 USD | 5,407.72 USD |
| 9 .. 12 | 331 | 37.16% | 12.05 USD | -3.12 USD .. 26.02 USD | 3,989.38 USD |
| 12 .. 17 | 321 | 38.63% | 21.74 USD | 1.39 USD .. 40.79 USD | 6,979.58 USD |
| 17 .. 94 | 287 | 32.75% | -12.07 USD | -49.71 USD .. 28.83 USD | -3,463.74 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1.036 .. 1.982 | 327 | 31.19% | -5.00 USD | -19.62 USD .. 9.82 USD | -1,634.54 USD |
| 1.982 .. 2.353 | 327 | 37.31% | 15.77 USD | -1.12 USD .. 32.88 USD | 5,155.46 USD |
| 2.353 .. 2.685 | 327 | 36.09% | 5.77 USD | -11.89 USD .. 23.40 USD | 1,885.46 USD |
| 2.685 .. 3.184 | 327 | 35.78% | 3.29 USD | -16.32 USD .. 22.79 USD | 1,075.46 USD |
| 3.184 .. 66.2 | 327 | 38.84% | 14.54 USD | -9.88 USD .. 38.98 USD | 4,755.46 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.3119 .. 0.6849 | 325 | 30.77% | -15.19 USD | -32.37 USD .. 1.37 USD | -4,936.50 USD |
| 0.6849 .. 0.8324 | 324 | 41.36% | 26.94 USD | 10.84 USD .. 43.69 USD | 8,727.52 USD |
| 0.8324 .. 1.013 | 324 | 37.35% | 9.78 USD | -9.28 USD .. 28.89 USD | 3,167.52 USD |
| 1.013 .. 1.297 | 324 | 32.72% | -0.41 USD | -17.57 USD .. 17.23 USD | -132.48 USD |
| 1.297 .. 4.616 | 325 | 37.23% | 13.80 USD | -7.30 USD .. 34.55 USD | 4,483.50 USD |
| NaN | 13 | 30.77% | -5.56 USD | -77.35 USD .. 55.98 USD | -72.26 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 849 | 35.10% | 6.96 USD | -4.82 USD .. 19.15 USD | 5,907.02 USD |
| Short | 786 | 36.64% | 6.78 USD | -5.04 USD .. 19.10 USD | 5,330.28 USD |

### `weekday` (Europe/London clock)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 325 | 32.31% | -3.28 USD | -21.76 USD .. 14.91 USD | -1,066.50 USD |
| Mon | 328 | 42.07% | 28.91 USD | 10.84 USD .. 46.75 USD | 9,481.44 USD |
| Thu | 324 | 35.49% | 3.91 USD | -14.55 USD .. 21.37 USD | 1,267.52 USD |
| Tue | 318 | 37.42% | 19.16 USD | -0.86 USD .. 39.76 USD | 6,091.64 USD |
| Wed | 340 | 32.06% | -13.34 USD | -30.04 USD .. 3.32 USD | -4,536.80 USD |
