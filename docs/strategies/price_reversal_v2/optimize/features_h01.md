# Price Reversal v2 (hourly anchors, entry cap, fixed TP), CL1!: feature association, h01

Generated 2026-11-11 20:14 UTC by `python -m tvtester.cli features price_reversal_v2 --variant h01`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `anchor=h01`, `window=60`, `atr_mult=2.0`, `swing=1`, `target=rr2`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## Baseline, commission included: 2,279 trades, net 31,018.42 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 4 .. 14 | 479 | 37.16% | 14.69 USD | -7.65 USD .. 37.53 USD | 7,034.42 USD |
| 14 .. 22 | 469 | 35.39% | 19.20 USD | 1.10 USD .. 37.41 USD | 9,004.62 USD |
| 22 .. 30 | 422 | 40.52% | 19.49 USD | 1.53 USD .. 37.65 USD | 8,223.56 USD |
| 30 .. 42 | 468 | 35.04% | 8.97 USD | -3.24 USD .. 20.47 USD | 4,198.64 USD |
| 42 .. 59 | 441 | 33.79% | 5.80 USD | -7.95 USD .. 20.61 USD | 2,557.18 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.2052 | 456 | 36.40% | 13.85 USD | -3.19 USD .. 30.48 USD | 6,316.88 USD |
| 0.2052 .. 0.4393 | 456 | 33.77% | 8.85 USD | -8.99 USD .. 28.04 USD | 4,036.88 USD |
| 0.4393 .. 0.7102 | 455 | 35.60% | 4.88 USD | -11.18 USD .. 20.41 USD | 2,220.90 USD |
| 0.7102 .. 1.155 | 456 | 38.82% | 23.00 USD | 4.91 USD .. 42.79 USD | 10,486.88 USD |
| 1.155 .. 8.196 | 456 | 37.06% | 17.45 USD | 0.51 USD .. 35.03 USD | 7,956.88 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 2 .. 5 | 532 | 29.32% | -6.11 USD | -10.30 USD .. -1.88 USD | -3,248.64 USD |
| 5 .. 7 | 422 | 35.31% | 2.19 USD | -5.08 USD .. 9.97 USD | 923.56 USD |
| 7 .. 10 | 429 | 34.27% | 0.01 USD | -9.16 USD .. 9.60 USD | 5.42 USD |
| 10 .. 15 | 454 | 37.67% | 6.88 USD | -7.09 USD .. 20.26 USD | 3,124.92 USD |
| 15 .. 537 | 442 | 46.38% | 68.36 USD | 34.86 USD .. 104.48 USD | 30,213.16 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.8486 .. 2.116 | 456 | 35.53% | 5.63 USD | -3.63 USD .. 15.53 USD | 2,566.88 USD |
| 2.116 .. 2.649 | 456 | 32.46% | 8.96 USD | -4.11 USD .. 22.40 USD | 4,086.88 USD |
| 2.649 .. 3.253 | 455 | 32.09% | -0.66 USD | -18.78 USD .. 17.59 USD | -299.10 USD |
| 3.253 .. 4.077 | 456 | 39.47% | 23.74 USD | 6.31 USD .. 41.14 USD | 10,826.88 USD |
| 4.077 .. 18.28 | 456 | 42.11% | 30.34 USD | 5.82 USD .. 55.64 USD | 13,836.88 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.2981 .. 0.6906 | 453 | 37.31% | 23.82 USD | 5.58 USD .. 45.01 USD | 10,788.94 USD |
| 0.6906 .. 0.8533 | 452 | 35.40% | 2.90 USD | -8.94 USD .. 15.23 USD | 1,312.96 USD |
| 0.8533 .. 1.042 | 453 | 36.64% | 12.21 USD | -0.95 USD .. 27.16 USD | 5,528.94 USD |
| 1.042 .. 1.307 | 452 | 36.06% | 8.75 USD | -7.48 USD .. 24.46 USD | 3,952.96 USD |
| 1.307 .. 7.003 | 453 | 36.42% | 20.88 USD | -5.32 USD .. 46.59 USD | 9,458.94 USD |
| NaN | 16 | 31.25% | -1.52 USD | -44.02 USD .. 40.98 USD | -24.32 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 1,098 | 35.97% | 15.44 USD | 3.81 USD .. 27.43 USD | 16,956.04 USD |
| Short | 1,181 | 36.66% | 11.91 USD | 2.28 USD .. 21.85 USD | 14,062.38 USD |

### `weekday` (America/New_York clock)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Mon | 435 | 32.64% | -3.26 USD | -16.97 USD .. 11.04 USD | -1,418.70 USD |
| Sun | 531 | 42.37% | 37.26 USD | 15.11 USD .. 62.44 USD | 19,785.38 USD |
| Thu | 435 | 37.70% | 10.74 USD | -1.98 USD .. 23.01 USD | 4,671.30 USD |
| Tue | 435 | 35.40% | 3.43 USD | -9.46 USD .. 16.38 USD | 1,491.30 USD |
| Wed | 443 | 32.28% | 14.65 USD | -2.09 USD .. 32.19 USD | 6,489.14 USD |
