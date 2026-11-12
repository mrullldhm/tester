# Price Reversal v2 (hourly anchors, entry cap, fixed TP), CL1!: feature association, entry_london

Generated 2026-11-11 20:24 UTC by `python -m tvtester.cli features price_reversal_v2 --variant entry_london`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `anchor=london`, `swing=1`, `window=30`, `atr_mult=1.5`, `target=rr2`, `entry_cap=50`, `tp_mode=default`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## Baseline, commission included: 1,571 trades, net 11,174.58 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 4 .. 12 | 386 | 33.68% | 5.77 USD | -14.02 USD .. 24.57 USD | 2,228.28 USD |
| 12 .. 16 | 297 | 31.99% | -11.80 USD | -28.41 USD .. 5.85 USD | -3,503.94 USD |
| 16 .. 20 | 286 | 40.91% | 19.23 USD | -2.07 USD .. 39.45 USD | 5,500.28 USD |
| 20 .. 25 | 355 | 34.37% | 0.09 USD | -16.34 USD .. 17.94 USD | 32.90 USD |
| 25 .. 29 | 247 | 39.68% | 28.00 USD | 2.82 USD .. 51.62 USD | 6,917.06 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.3514 | 629 | 37.52% | 11.89 USD | -3.42 USD .. 26.78 USD | 7,481.42 USD |
| 0.3514 .. 0.5593 | 314 | 36.62% | 8.88 USD | -9.62 USD .. 27.18 USD | 2,787.72 USD |
| 0.5593 .. 0.9644 | 314 | 33.76% | 1.08 USD | -18.74 USD .. 21.49 USD | 337.72 USD |
| 0.9644 .. 4.823 | 314 | 33.44% | 1.81 USD | -15.69 USD .. 19.55 USD | 567.72 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 3 .. 7 | 339 | 31.56% | -3.61 USD | -11.26 USD .. 4.08 USD | -1,222.78 USD |
| 7 .. 9 | 295 | 38.64% | 12.12 USD | 0.19 USD .. 24.15 USD | 3,574.10 USD |
| 9 .. 12 | 325 | 38.15% | 15.61 USD | 1.37 USD .. 30.08 USD | 5,073.50 USD |
| 12 .. 17 | 319 | 38.56% | 21.28 USD | 1.50 USD .. 41.78 USD | 6,787.62 USD |
| 17 .. 81 | 293 | 32.08% | -10.37 USD | -48.13 USD .. 30.21 USD | -3,037.86 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1.036 .. 2.016 | 315 | 32.70% | 1.88 USD | -13.74 USD .. 18.25 USD | 593.70 USD |
| 2.016 .. 2.392 | 314 | 37.90% | 12.06 USD | -5.38 USD .. 28.71 USD | 3,787.72 USD |
| 2.392 .. 2.748 | 314 | 34.39% | -0.07 USD | -17.39 USD .. 17.63 USD | -22.28 USD |
| 2.748 .. 3.28 | 314 | 35.67% | 5.53 USD | -14.98 USD .. 25.37 USD | 1,737.72 USD |
| 3.28 .. 21.96 | 314 | 38.22% | 16.17 USD | -9.41 USD .. 41.77 USD | 5,077.72 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.3119 .. 0.6847 | 312 | 31.41% | -14.15 USD | -31.54 USD .. 2.38 USD | -4,414.24 USD |
| 0.6847 .. 0.8303 | 312 | 38.78% | 19.60 USD | 2.18 USD .. 36.77 USD | 6,115.76 USD |
| 0.8303 .. 1.015 | 311 | 38.26% | 14.05 USD | -5.91 USD .. 33.60 USD | 4,369.78 USD |
| 1.015 .. 1.298 | 312 | 32.69% | -2.58 USD | -20.82 USD .. 16.59 USD | -804.24 USD |
| 1.298 .. 4.616 | 312 | 37.82% | 18.42 USD | -5.74 USD .. 42.11 USD | 5,745.76 USD |
| NaN | 12 | 33.33% | 13.48 USD | -77.35 USD .. 104.31 USD | 161.76 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 813 | 34.93% | 7.09 USD | -4.39 USD .. 19.28 USD | 5,761.74 USD |
| Short | 758 | 36.68% | 7.14 USD | -5.38 USD .. 20.73 USD | 5,412.84 USD |

### `weekday` (Europe/London clock)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 313 | 34.19% | 7.39 USD | -12.04 USD .. 27.98 USD | 2,311.74 USD |
| Mon | 312 | 41.99% | 28.00 USD | 10.03 USD .. 47.43 USD | 8,735.76 USD |
| Thu | 309 | 34.95% | -0.46 USD | -19.95 USD .. 18.77 USD | -142.18 USD |
| Tue | 313 | 36.42% | 15.25 USD | -5.50 USD .. 36.56 USD | 4,771.74 USD |
| Wed | 324 | 31.48% | -13.90 USD | -31.09 USD .. 2.99 USD | -4,502.48 USD |
