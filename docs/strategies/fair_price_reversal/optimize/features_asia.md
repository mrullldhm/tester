# Fair Price Reversal (LuxAlgo 9:29 ET), CL1! sessions: feature association, asia

Generated 2026-11-04 15:06 UTC by `python -m tvtester.cli features fair_price_reversal --variant asia`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `session=asia`, `window=30`, `atr_mult=2.0`, `swing=1`, `target=rr2`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## Baseline, commission included: 1,310 trades, net -1,376.20 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 4 .. 11 | 285 | 32.63% | -15.74 USD | -34.05 USD .. 0.88 USD | -4,485.70 USD |
| 11 .. 16 | 292 | 30.14% | -12.03 USD | -30.98 USD .. 5.50 USD | -3,513.84 USD |
| 16 .. 20 | 234 | 34.62% | -0.13 USD | -21.43 USD .. 22.68 USD | -30.68 USD |
| 20 .. 25 | 271 | 30.26% | 4.06 USD | -13.26 USD .. 20.80 USD | 1,100.58 USD |
| 25 .. 29 | 228 | 36.84% | 24.36 USD | 0.65 USD .. 49.20 USD | 5,553.44 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.3141 | 524 | 35.88% | 14.61 USD | -4.94 USD .. 37.63 USD | 7,653.52 USD |
| 0.3141 .. 0.5761 | 262 | 31.30% | -15.89 USD | -34.46 USD .. 2.35 USD | -4,163.24 USD |
| 0.5761 .. 0.9474 | 262 | 32.06% | 0.06 USD | -16.14 USD .. 15.87 USD | 16.76 USD |
| 0.9474 .. 5.901 | 262 | 28.24% | -18.64 USD | -41.32 USD .. 5.98 USD | -4,883.24 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 2 .. 5 | 283 | 27.92% | -6.39 USD | -12.19 USD .. -0.72 USD | -1,807.66 USD |
| 5 .. 7 | 263 | 33.46% | -1.24 USD | -10.38 USD .. 8.13 USD | -327.26 USD |
| 7 .. 10 | 305 | 31.80% | -7.20 USD | -17.94 USD .. 4.08 USD | -2,196.10 USD |
| 10 .. 14 | 205 | 36.10% | 5.44 USD | -15.25 USD .. 25.05 USD | 1,115.90 USD |
| 14 .. 133 | 254 | 35.43% | 7.24 USD | -36.45 USD .. 52.20 USD | 1,838.92 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.9478 .. 2.094 | 262 | 32.44% | 2.70 USD | -11.76 USD .. 17.49 USD | 706.76 USD |
| 2.094 .. 2.468 | 262 | 34.73% | -0.32 USD | -15.33 USD .. 14.75 USD | -83.24 USD |
| 2.468 .. 2.918 | 262 | 33.21% | 8.84 USD | -15.76 USD .. 37.10 USD | 2,316.76 USD |
| 2.918 .. 3.523 | 262 | 28.63% | -7.99 USD | -31.03 USD .. 17.31 USD | -2,093.24 USD |
| 3.523 .. 106.8 | 262 | 34.35% | -8.49 USD | -31.49 USD .. 14.75 USD | -2,223.24 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.2898 .. 0.6928 | 260 | 31.54% | -15.94 USD | -29.92 USD .. -1.12 USD | -4,145.20 USD |
| 0.6928 .. 0.8502 | 259 | 30.89% | 4.44 USD | -11.78 USD .. 21.42 USD | 1,148.82 USD |
| 0.8502 .. 1.029 | 260 | 33.08% | -2.33 USD | -18.08 USD .. 12.47 USD | -605.20 USD |
| 1.029 .. 1.28 | 259 | 29.34% | -11.86 USD | -30.30 USD .. 7.98 USD | -3,071.18 USD |
| 1.28 .. 8.218 | 260 | 37.69% | 19.63 USD | -15.83 USD .. 60.03 USD | 5,104.80 USD |
| NaN | 12 | 50.00% | 15.98 USD | -8.19 USD .. 40.53 USD | 191.76 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 654 | 32.26% | -0.27 USD | -14.70 USD .. 16.00 USD | -179.08 USD |
| Short | 656 | 33.08% | -1.82 USD | -14.80 USD .. 10.01 USD | -1,197.12 USD |

### `weekday` (Asia/Shanghai clock)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 258 | 33.72% | 6.29 USD | -11.45 USD .. 27.02 USD | 1,622.84 USD |
| Mon | 268 | 32.84% | -6.07 USD | -28.79 USD .. 17.10 USD | -1,627.36 USD |
| Thu | 265 | 28.30% | -13.49 USD | -30.07 USD .. 2.57 USD | -3,575.30 USD |
| Tue | 258 | 34.88% | 10.09 USD | -12.74 USD .. 35.83 USD | 2,602.84 USD |
| Wed | 261 | 33.72% | -1.53 USD | -18.66 USD .. 15.75 USD | -399.22 USD |
