# Supertrend + ATR trail + Kalman trend, M15 signals, CL1! 1m: feature association, asia

Generated 2026-10-31 12:57 UTC by `python -m tvtester.cli features supertrend_kalman --variant asia`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `hours=asia`, `trigger=trail`, `vol=none`, `exit=trail`, `rr=3`, `swing=3`, `trail_mult=2`, `st_factor=3`, `kalman_q=0.01`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## 0 ticks slippage: 979 trades, net 15,844.42 USD

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1 .. 20.6 | 196 | 41.84% | -2.03 USD | -15.70 USD .. 12.37 USD | -397.92 USD |
| 20.6 .. 28 | 205 | 47.80% | 9.20 USD | -10.04 USD .. 29.46 USD | 1,885.90 USD |
| 28 .. 38 | 204 | 43.14% | 13.38 USD | -11.31 USD .. 41.04 USD | 2,729.92 USD |
| 38 .. 52 | 183 | 48.09% | 40.57 USD | 8.26 USD .. 74.36 USD | 7,424.34 USD |
| 52 .. 400 | 191 | 46.60% | 22.00 USD | -49.43 USD .. 91.95 USD | 4,202.18 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.1077 .. 2.112 | 196 | 39.29% | -2.49 USD | -32.98 USD .. 28.26 USD | -487.92 USD |
| 2.112 .. 2.466 | 196 | 50.51% | 18.89 USD | -6.68 USD .. 47.79 USD | 3,702.08 USD |
| 2.466 .. 2.83 | 195 | 45.64% | 24.54 USD | -6.76 USD .. 58.62 USD | 4,786.10 USD |
| 2.83 .. 3.322 | 196 | 47.45% | 23.99 USD | -9.65 USD .. 58.67 USD | 4,702.08 USD |
| 3.322 .. 12.46 | 196 | 44.39% | 16.03 USD | -23.06 USD .. 56.58 USD | 3,142.08 USD |

### `atr_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.4021 .. 0.5723 | 196 | 42.35% | -7.39 USD | -25.14 USD .. 10.69 USD | -1,447.92 USD |
| 0.5723 .. 0.6384 | 195 | 47.69% | 17.36 USD | -3.22 USD .. 39.40 USD | 3,386.10 USD |
| 0.6384 .. 0.6993 | 196 | 42.35% | -8.56 USD | -33.93 USD .. 17.78 USD | -1,677.92 USD |
| 0.6993 .. 0.7848 | 195 | 46.67% | 40.24 USD | 4.58 USD .. 77.36 USD | 7,846.10 USD |
| 0.7848 .. 1.925 | 196 | 47.96% | 36.59 USD | -20.55 USD .. 91.84 USD | 7,172.08 USD |
| NaN | 1 | 100.00% | 565.98 USD | — .. — | 565.98 USD |

### `er`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.05263 | 199 | 45.73% | 11.61 USD | -15.33 USD .. 38.18 USD | 2,310.02 USD |
| 0.05263 .. 0.1014 | 194 | 46.39% | -4.69 USD | -42.31 USD .. 30.78 USD | -909.88 USD |
| 0.1014 .. 0.1801 | 194 | 50.52% | 40.57 USD | 8.62 USD .. 75.00 USD | 7,870.12 USD |
| 0.1801 .. 0.2879 | 196 | 39.80% | 1.49 USD | -35.40 USD .. 40.22 USD | 292.08 USD |
| 0.2879 .. 0.6634 | 196 | 44.90% | 32.05 USD | 2.10 USD .. 66.23 USD | 6,282.08 USD |

### `hours_since_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 2 .. 4 | 326 | 47.24% | 46.38 USD | 8.40 USD .. 86.26 USD | 15,119.48 USD |
| 4 .. 5 | 91 | 46.15% | 18.29 USD | -23.36 USD .. 61.87 USD | 1,664.18 USD |
| 5 .. 7 | 326 | 40.80% | -3.87 USD | -23.51 USD .. 15.71 USD | -1,260.52 USD |
| 7 .. 8 | 236 | 49.15% | 1.36 USD | -14.20 USD .. 17.33 USD | 321.28 USD |

### `rvi_side`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 31.4 .. 53.84 | 196 | 46.94% | 12.46 USD | -27.56 USD .. 52.29 USD | 2,442.08 USD |
| 53.84 .. 59.49 | 196 | 47.45% | 29.25 USD | -15.59 USD .. 72.28 USD | 5,732.08 USD |
| 59.49 .. 63.95 | 195 | 43.59% | 2.29 USD | -24.60 USD .. 29.82 USD | 446.10 USD |
| 63.95 .. 68.25 | 196 | 47.96% | 28.63 USD | -1.39 USD .. 58.17 USD | 5,612.08 USD |
| 68.25 .. 86.98 | 196 | 41.33% | 8.22 USD | -20.83 USD .. 39.42 USD | 1,612.08 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 505 | 44.95% | 22.87 USD | 3.94 USD .. 41.33 USD | 11,549.90 USD |
| Short | 474 | 45.99% | 9.06 USD | -17.27 USD .. 34.75 USD | 4,294.52 USD |

### `weekday` (UTC clock: generated before the `report_tz` fix, see README audit note)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 198 | 46.97% | 23.35 USD | -8.37 USD .. 56.84 USD | 4,624.04 USD |
| Mon | 135 | 48.15% | 44.50 USD | 3.41 USD .. 87.10 USD | 6,007.30 USD |
| Thu | 228 | 42.11% | -7.88 USD | -34.50 USD .. 20.42 USD | -1,796.56 USD |
| Tue | 226 | 45.58% | 21.42 USD | -11.18 USD .. 54.74 USD | 4,841.48 USD |
| Wed | 192 | 45.83% | 11.29 USD | -19.20 USD .. 44.19 USD | 2,168.16 USD |

## 1 tick slippage: 979 trades, net -3,495.58 USD

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1 .. 20.6 | 196 | 34.18% | -21.42 USD | -35.83 USD .. -6.60 USD | -4,197.92 USD |
| 20.6 .. 28 | 205 | 39.51% | -10.70 USD | -30.09 USD .. 8.40 USD | -2,194.10 USD |
| 28 .. 38 | 204 | 38.24% | -6.42 USD | -31.65 USD .. 20.65 USD | -1,310.08 USD |
| 38 .. 52 | 183 | 44.81% | 20.68 USD | -12.01 USD .. 53.25 USD | 3,784.34 USD |
| 52 .. 400 | 191 | 45.55% | 2.21 USD | -66.35 USD .. 69.72 USD | 422.18 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.1077 .. 2.112 | 196 | 35.20% | -21.67 USD | -52.10 USD .. 10.52 USD | -4,247.92 USD |
| 2.112 .. 2.466 | 196 | 43.88% | -0.91 USD | -28.09 USD .. 27.65 USD | -177.92 USD |
| 2.466 .. 2.83 | 195 | 40.00% | 4.54 USD | -27.63 USD .. 37.12 USD | 886.10 USD |
| 2.83 .. 3.322 | 196 | 42.86% | 3.99 USD | -29.61 USD .. 39.58 USD | 782.08 USD |
| 3.322 .. 12.46 | 196 | 39.80% | -3.76 USD | -44.60 USD .. 34.96 USD | -737.92 USD |

### `atr_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.4021 .. 0.5723 | 196 | 35.71% | -27.29 USD | -44.33 USD .. -9.24 USD | -5,347.92 USD |
| 0.5723 .. 0.6384 | 195 | 42.05% | -2.33 USD | -23.14 USD .. 19.27 USD | -453.90 USD |
| 0.6384 .. 0.6993 | 196 | 38.27% | -28.36 USD | -54.60 USD .. -1.58 USD | -5,557.92 USD |
| 0.6993 .. 0.7848 | 195 | 42.56% | 20.54 USD | -13.77 USD .. 56.19 USD | 4,006.10 USD |
| 0.7848 .. 1.925 | 196 | 42.86% | 16.90 USD | -39.22 USD .. 72.07 USD | 3,312.08 USD |
| NaN | 1 | 100.00% | 545.98 USD | — .. — | 545.98 USD |

### `er`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.05263 | 199 | 39.70% | -7.99 USD | -34.02 USD .. 18.47 USD | -1,589.98 USD |
| 0.05263 .. 0.1014 | 194 | 43.30% | -24.48 USD | -63.22 USD .. 11.36 USD | -4,749.88 USD |
| 0.1014 .. 0.1801 | 194 | 41.24% | 20.77 USD | -11.83 USD .. 55.72 USD | 4,030.12 USD |
| 0.1801 .. 0.2879 | 196 | 35.71% | -18.20 USD | -55.86 USD .. 17.05 USD | -3,567.92 USD |
| 0.2879 .. 0.6634 | 196 | 41.84% | 12.15 USD | -19.86 USD .. 45.36 USD | 2,382.08 USD |

### `hours_since_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 2 .. 4 | 326 | 42.33% | 26.87 USD | -11.85 USD .. 66.75 USD | 8,759.48 USD |
| 4 .. 5 | 91 | 41.76% | -1.71 USD | -44.68 USD .. 41.11 USD | -155.82 USD |
| 5 .. 7 | 326 | 37.12% | -23.68 USD | -43.87 USD .. -2.86 USD | -7,720.52 USD |
| 7 .. 8 | 236 | 41.53% | -18.55 USD | -34.24 USD .. -3.19 USD | -4,378.72 USD |

### `rvi_side`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 31.4 .. 53.84 | 196 | 40.31% | -7.23 USD | -46.83 USD .. 35.03 USD | -1,417.92 USD |
| 53.84 .. 59.49 | 196 | 42.86% | 9.76 USD | -32.06 USD .. 50.30 USD | 1,912.08 USD |
| 59.49 .. 63.95 | 195 | 38.46% | -17.71 USD | -44.63 USD .. 11.11 USD | -3,453.90 USD |
| 63.95 .. 68.25 | 196 | 42.35% | 8.94 USD | -20.92 USD .. 39.32 USD | 1,752.08 USD |
| 68.25 .. 86.98 | 196 | 37.76% | -11.67 USD | -41.14 USD .. 18.66 USD | -2,287.92 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 505 | 40.40% | 3.19 USD | -15.67 USD .. 21.71 USD | 1,609.90 USD |
| Short | 474 | 40.30% | -10.77 USD | -38.82 USD .. 13.26 USD | -5,105.48 USD |

### `weekday` (UTC clock: generated before the `report_tz` fix, see README audit note)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 198 | 40.40% | 3.76 USD | -28.92 USD .. 36.03 USD | 744.04 USD |
| Mon | 135 | 44.44% | 24.65 USD | -14.47 USD .. 67.96 USD | 3,327.30 USD |
| Thu | 228 | 38.16% | -27.70 USD | -56.35 USD .. 0.08 USD | -6,316.56 USD |
| Tue | 226 | 39.38% | 1.69 USD | -31.94 USD .. 35.07 USD | 381.48 USD |
| Wed | 192 | 41.15% | -8.50 USD | -38.55 USD .. 22.82 USD | -1,631.84 USD |
