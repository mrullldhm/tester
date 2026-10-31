# Fair Price Reversal (LuxAlgo 9:29 ET), CL1! sessions: feature association, asia

Generated 2026-10-31 05:06 UTC by `python -m tvtester.cli features fair_price_reversal --variant asia`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `session=asia`, `window=30`, `atr_mult=2.0`, `swing=3`, `target=rr1`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## 0 ticks slippage: 342 trades, net 815.16 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 2 .. 16 | 70 | 42.86% | -15.02 USD | -57.93 USD .. 28.04 USD | -1,051.40 USD |
| 16 .. 21 | 77 | 46.75% | -30.77 USD | -64.42 USD .. 1.74 USD | -2,369.54 USD |
| 21 .. 24 | 72 | 56.94% | 38.48 USD | 5.85 USD .. 70.98 USD | 2,770.56 USD |
| 24 .. 27 | 68 | 50.00% | 20.83 USD | -20.59 USD .. 61.50 USD | 1,416.64 USD |
| 27 .. 29 | 55 | 56.36% | 0.89 USD | -42.91 USD .. 50.62 USD | 48.90 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.2996 | 137 | 51.82% | -0.08 USD | -29.60 USD .. 30.94 USD | -10.74 USD |
| 0.2996 .. 0.5477 | 68 | 50.00% | 10.83 USD | -29.54 USD .. 50.23 USD | 736.64 USD |
| 0.5477 .. 0.9889 | 68 | 51.47% | 2.16 USD | -31.73 USD .. 35.69 USD | 146.64 USD |
| 0.9889 .. 5.653 | 69 | 46.38% | -0.83 USD | -51.97 USD .. 53.36 USD | -57.38 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 3 .. 8 | 91 | 52.75% | 0.16 USD | -10.83 USD .. 10.12 USD | 14.18 USD |
| 8 .. 10 | 49 | 53.06% | 1.29 USD | -22.18 USD .. 25.17 USD | 63.02 USD |
| 10 .. 15 | 74 | 41.89% | -25.24 USD | -50.00 USD .. -0.87 USD | -1,867.48 USD |
| 15 .. 22 | 63 | 46.03% | -22.43 USD | -59.74 USD .. 14.35 USD | -1,413.26 USD |
| 22 .. 126 | 65 | 58.46% | 61.83 USD | -15.69 USD .. 138.71 USD | 4,018.70 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1.586 .. 2.882 | 69 | 52.17% | 21.63 USD | -21.15 USD .. 69.04 USD | 1,492.62 USD |
| 2.882 .. 3.335 | 68 | 54.41% | -4.31 USD | -41.06 USD .. 29.83 USD | -293.36 USD |
| 3.335 .. 3.798 | 68 | 35.29% | -47.70 USD | -88.72 USD .. -8.94 USD | -3,243.36 USD |
| 3.798 .. 4.546 | 68 | 51.47% | 4.07 USD | -47.11 USD .. 60.07 USD | 276.64 USD |
| 4.546 .. 108.2 | 69 | 57.97% | 37.43 USD | 0.47 USD .. 72.94 USD | 2,582.62 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.3717 .. 0.7102 | 68 | 44.12% | 0.69 USD | -34.77 USD .. 41.28 USD | 46.64 USD |
| 0.7102 .. 0.8776 | 68 | 61.76% | 37.89 USD | 5.69 USD .. 71.43 USD | 2,576.64 USD |
| 0.8776 .. 1.067 | 68 | 41.18% | -40.49 USD | -73.75 USD .. -6.41 USD | -2,753.36 USD |
| 1.067 .. 1.33 | 68 | 52.94% | 2.45 USD | -35.91 USD .. 42.55 USD | 166.64 USD |
| 1.33 .. 4.711 | 68 | 52.94% | 15.98 USD | -35.00 USD .. 65.51 USD | 1,086.64 USD |
| NaN | 2 | 0.00% | -154.02 USD | -224.02 USD .. -84.02 USD | -308.04 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 182 | 48.90% | -0.61 USD | -27.98 USD .. 26.26 USD | -111.64 USD |
| Short | 160 | 51.88% | 5.79 USD | -17.26 USD .. 27.47 USD | 926.80 USD |

### `weekday`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 63 | 46.03% | -5.77 USD | -44.03 USD .. 30.27 USD | -363.26 USD |
| Mon | 82 | 54.88% | 39.88 USD | -2.34 USD .. 83.05 USD | 3,270.36 USD |
| Thu | 60 | 41.67% | -15.19 USD | -54.02 USD .. 25.47 USD | -911.20 USD |
| Tue | 65 | 53.85% | 2.29 USD | -35.71 USD .. 40.91 USD | 148.70 USD |
| Wed | 72 | 52.78% | -18.46 USD | -64.99 USD .. 20.85 USD | -1,329.44 USD |

## 1 tick slippage: 342 trades, net -4,084.84 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 2 .. 16 | 70 | 40.00% | -31.31 USD | -78.00 USD .. 15.00 USD | -2,191.40 USD |
| 16 .. 21 | 77 | 45.45% | -44.80 USD | -79.03 USD .. -10.40 USD | -3,449.54 USD |
| 21 .. 24 | 72 | 50.00% | 18.20 USD | -15.27 USD .. 53.47 USD | 1,310.56 USD |
| 24 .. 27 | 68 | 50.00% | 10.24 USD | -31.37 USD .. 55.83 USD | 696.64 USD |
| 27 .. 29 | 55 | 56.36% | -8.20 USD | -58.86 USD .. 41.00 USD | -451.10 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.2996 | 137 | 46.72% | -17.52 USD | -48.40 USD .. 14.93 USD | -2,400.74 USD |
| 0.2996 .. 0.5477 | 68 | 50.00% | 0.83 USD | -40.05 USD .. 44.95 USD | 56.64 USD |
| 0.5477 .. 0.9889 | 68 | 50.00% | -12.70 USD | -47.31 USD .. 24.37 USD | -863.36 USD |
| 0.9889 .. 5.653 | 69 | 46.38% | -12.72 USD | -66.16 USD .. 41.43 USD | -877.38 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 3 .. 8 | 91 | 49.45% | -13.36 USD | -25.95 USD .. -1.05 USD | -1,215.82 USD |
| 8 .. 10 | 49 | 51.02% | -11.57 USD | -36.06 USD .. 12.32 USD | -566.98 USD |
| 10 .. 15 | 74 | 36.49% | -47.80 USD | -72.74 USD .. -22.07 USD | -3,537.48 USD |
| 15 .. 22 | 63 | 46.03% | -34.34 USD | -71.78 USD .. 4.67 USD | -2,163.26 USD |
| 22 .. 126 | 65 | 58.46% | 52.29 USD | -26.75 USD .. 128.00 USD | 3,398.70 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1.586 .. 2.882 | 69 | 50.72% | 10.62 USD | -34.62 USD .. 60.01 USD | 732.62 USD |
| 2.882 .. 3.335 | 68 | 50.00% | -21.08 USD | -59.69 USD .. 14.79 USD | -1,433.36 USD |
| 3.335 .. 3.798 | 68 | 35.29% | -60.78 USD | -102.18 USD .. -22.52 USD | -4,133.36 USD |
| 3.798 .. 4.546 | 68 | 47.06% | -16.37 USD | -70.46 USD .. 40.40 USD | -1,113.36 USD |
| 4.546 .. 108.2 | 69 | 56.52% | 26.99 USD | -11.27 USD .. 63.96 USD | 1,862.62 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.3717 .. 0.7102 | 68 | 41.18% | -16.37 USD | -54.32 USD .. 25.53 USD | -1,113.36 USD |
| 0.7102 .. 0.8776 | 68 | 60.29% | 26.72 USD | -8.08 USD .. 61.65 USD | 1,816.64 USD |
| 0.8776 .. 1.067 | 68 | 39.71% | -54.31 USD | -89.40 USD .. -19.02 USD | -3,693.36 USD |
| 1.067 .. 1.33 | 68 | 50.00% | -10.34 USD | -50.49 USD .. 27.53 USD | -703.36 USD |
| 1.33 .. 4.711 | 68 | 50.00% | -0.64 USD | -49.45 USD .. 51.29 USD | -43.36 USD |
| NaN | 2 | 0.00% | -174.02 USD | -244.02 USD .. -104.02 USD | -348.04 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 182 | 46.70% | -14.95 USD | -42.20 USD .. 12.77 USD | -2,721.64 USD |
| Short | 160 | 49.38% | -8.52 USD | -30.36 USD .. 14.41 USD | -1,363.20 USD |

### `weekday`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 63 | 44.44% | -17.19 USD | -54.66 USD .. 20.42 USD | -1,083.26 USD |
| Mon | 82 | 53.66% | 28.05 USD | -15.37 USD .. 74.77 USD | 2,300.36 USD |
| Thu | 60 | 36.67% | -38.19 USD | -78.52 USD .. 1.98 USD | -2,291.20 USD |
| Tue | 65 | 49.23% | -14.79 USD | -53.72 USD .. 27.36 USD | -961.30 USD |
| Wed | 72 | 52.78% | -28.46 USD | -72.21 USD .. 13.62 USD | -2,049.44 USD |
