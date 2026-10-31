# Supertrend + ATR trail + Kalman trend, M15 signals, CL1! 1m: feature association, london

Generated 2026-10-31 12:57 UTC by `python -m tvtester.cli features supertrend_kalman --variant london`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `hours=london`, `trigger=both`, `vol=stop_atr:3`, `exit=trail`, `rr=2`, `swing=5`, `trail_mult=2`, `st_factor=3`, `kalman_q=0.0001`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## 0 ticks slippage: 590 trades, net 17,638.20 USD

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 3 .. 23 | 126 | 33.33% | -1.24 USD | -28.67 USD .. 29.26 USD | -156.52 USD |
| 23 .. 30 | 124 | 38.71% | -0.79 USD | -33.47 USD .. 36.32 USD | -98.48 USD |
| 30 .. 37 | 111 | 47.75% | 40.21 USD | -6.50 USD .. 88.98 USD | 4,463.78 USD |
| 37 .. 48 | 113 | 43.36% | 8.55 USD | -44.87 USD .. 62.63 USD | 965.74 USD |
| 48 .. 292 | 116 | 51.72% | 107.45 USD | 26.94 USD .. 190.13 USD | 12,463.68 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.08984 .. 2.189 | 118 | 36.44% | -4.78 USD | -49.35 USD .. 42.86 USD | -564.36 USD |
| 2.189 .. 2.486 | 118 | 42.37% | 57.17 USD | 5.87 USD .. 113.18 USD | 6,745.64 USD |
| 2.486 .. 2.676 | 118 | 39.83% | -2.58 USD | -52.21 USD .. 49.78 USD | -304.36 USD |
| 2.676 .. 2.838 | 118 | 50.00% | 77.51 USD | 21.44 USD .. 137.85 USD | 9,145.64 USD |
| 2.838 .. 3 | 118 | 44.92% | 22.17 USD | -29.03 USD .. 71.47 USD | 2,615.64 USD |

### `atr_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.4275 .. 0.6979 | 118 | 33.90% | 12.00 USD | -25.72 USD .. 49.12 USD | 1,415.64 USD |
| 0.6979 .. 0.7742 | 118 | 37.29% | 37.67 USD | -12.61 USD .. 90.11 USD | 4,445.64 USD |
| 0.7742 .. 0.8543 | 118 | 40.68% | 14.71 USD | -32.26 USD .. 65.42 USD | 1,735.64 USD |
| 0.8543 .. 0.9336 | 118 | 52.54% | 42.25 USD | -15.07 USD .. 107.01 USD | 4,985.64 USD |
| 0.9336 .. 1.326 | 118 | 49.15% | 42.84 USD | -18.14 USD .. 107.75 USD | 5,055.64 USD |

### `er`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.1111 | 119 | 47.06% | 46.74 USD | -12.53 USD .. 113.63 USD | 5,561.62 USD |
| 0.1111 .. 0.1599 | 117 | 40.17% | 12.39 USD | -34.11 USD .. 60.82 USD | 1,449.66 USD |
| 0.1599 .. 0.2125 | 118 | 44.92% | 41.91 USD | -8.65 USD .. 100.52 USD | 4,945.64 USD |
| 0.2125 .. 0.2653 | 120 | 35.83% | -16.69 USD | -60.26 USD .. 29.03 USD | -2,002.40 USD |
| 0.2653 .. 0.4586 | 116 | 45.69% | 66.24 USD | 10.59 USD .. 123.02 USD | 7,683.68 USD |

### `hours_since_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 9 .. 10 | 323 | 36.22% | 8.86 USD | -20.80 USD .. 38.52 USD | 2,861.54 USD |
| 10 .. 11 | 106 | 52.83% | 130.23 USD | 64.46 USD .. 200.61 USD | 13,803.88 USD |
| 11 .. 12 | 78 | 46.15% | 27.77 USD | -42.08 USD .. 100.54 USD | 2,166.44 USD |
| 12 .. 14 | 83 | 51.81% | -14.38 USD | -44.15 USD .. 16.35 USD | -1,193.66 USD |

### `rvi_side`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 33.92 .. 54.75 | 118 | 45.76% | 54.12 USD | -0.17 USD .. 112.91 USD | 6,385.64 USD |
| 54.75 .. 59.34 | 118 | 41.53% | 35.56 USD | -16.23 USD .. 88.93 USD | 4,195.64 USD |
| 59.34 .. 64.42 | 118 | 44.07% | 7.93 USD | -47.03 USD .. 62.07 USD | 935.64 USD |
| 64.42 .. 70.18 | 118 | 44.07% | 37.76 USD | -4.87 USD .. 82.59 USD | 4,455.64 USD |
| 70.18 .. 88.66 | 118 | 38.14% | 14.12 USD | -37.44 USD .. 68.51 USD | 1,665.64 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 282 | 42.91% | 29.46 USD | 0.59 USD .. 59.99 USD | 8,306.36 USD |
| Short | 308 | 42.53% | 30.30 USD | -4.32 USD .. 65.92 USD | 9,331.84 USD |

### `weekday` (UTC clock: generated before the `report_tz` fix, see README audit note)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 118 | 39.83% | 11.83 USD | -40.22 USD .. 69.26 USD | 1,395.64 USD |
| Mon | 105 | 40.00% | 16.84 USD | -40.67 USD .. 72.57 USD | 1,767.90 USD |
| Thu | 127 | 42.52% | 8.34 USD | -34.42 USD .. 52.08 USD | 1,059.46 USD |
| Tue | 127 | 42.52% | 58.74 USD | 6.92 USD .. 118.89 USD | 7,459.46 USD |
| Wed | 113 | 48.67% | 52.71 USD | 8.94 USD .. 100.31 USD | 5,955.74 USD |

## 1 tick slippage: 590 trades, net 6,258.20 USD

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 3 .. 23 | 126 | 28.57% | -20.05 USD | -48.34 USD .. 11.27 USD | -2,526.52 USD |
| 23 .. 30 | 124 | 35.48% | -19.02 USD | -50.84 USD .. 15.52 USD | -2,358.48 USD |
| 30 .. 37 | 111 | 41.44% | 17.24 USD | -31.09 USD .. 64.79 USD | 1,913.78 USD |
| 37 .. 48 | 113 | 41.59% | -10.04 USD | -61.77 USD .. 44.11 USD | -1,134.26 USD |
| 48 .. 292 | 116 | 49.14% | 89.34 USD | 9.24 USD .. 169.21 USD | 10,363.68 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.08984 .. 2.189 | 118 | 33.05% | -28.51 USD | -72.07 USD .. 21.56 USD | -3,364.36 USD |
| 2.189 .. 2.486 | 118 | 38.98% | 39.54 USD | -13.41 USD .. 95.81 USD | 4,665.64 USD |
| 2.486 .. 2.676 | 118 | 35.59% | -20.71 USD | -70.11 USD .. 28.62 USD | -2,444.36 USD |
| 2.676 .. 2.838 | 118 | 44.07% | 58.86 USD | 2.87 USD .. 115.65 USD | 6,945.64 USD |
| 2.838 .. 3 | 118 | 43.22% | 3.86 USD | -46.70 USD .. 56.49 USD | 455.64 USD |

### `atr_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.4275 .. 0.6979 | 118 | 33.05% | -4.10 USD | -42.65 USD .. 34.41 USD | -484.36 USD |
| 0.6979 .. 0.7742 | 118 | 35.59% | 17.42 USD | -35.59 USD .. 70.33 USD | 2,055.64 USD |
| 0.7742 .. 0.8543 | 118 | 35.59% | -8.26 USD | -60.50 USD .. 41.67 USD | -974.36 USD |
| 0.8543 .. 0.9336 | 118 | 46.61% | 24.29 USD | -35.62 USD .. 88.14 USD | 2,865.64 USD |
| 0.9336 .. 1.326 | 118 | 44.07% | 23.69 USD | -36.96 USD .. 87.66 USD | 2,795.64 USD |

### `er`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.1111 | 119 | 41.18% | 22.37 USD | -41.52 USD .. 85.33 USD | 2,661.62 USD |
| 0.1111 .. 0.1599 | 117 | 38.46% | -6.24 USD | -48.94 USD .. 38.80 USD | -730.34 USD |
| 0.1599 .. 0.2125 | 118 | 41.53% | 23.78 USD | -27.33 USD .. 83.75 USD | 2,805.64 USD |
| 0.2125 .. 0.2653 | 120 | 32.50% | -35.02 USD | -81.39 USD .. 11.81 USD | -4,202.40 USD |
| 0.2653 .. 0.4586 | 116 | 41.38% | 49.34 USD | -5.34 USD .. 105.82 USD | 5,723.68 USD |

### `hours_since_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 9 .. 10 | 323 | 33.44% | -10.89 USD | -40.62 USD .. 17.83 USD | -3,518.46 USD |
| 10 .. 11 | 106 | 51.89% | 112.49 USD | 39.12 USD .. 188.25 USD | 11,923.88 USD |
| 11 .. 12 | 78 | 42.31% | 9.06 USD | -61.75 USD .. 84.95 USD | 706.44 USD |
| 12 .. 14 | 83 | 40.96% | -34.38 USD | -63.69 USD .. -4.38 USD | -2,853.66 USD |

### `rvi_side`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 33.92 .. 54.75 | 118 | 43.22% | 36.49 USD | -18.66 USD .. 95.38 USD | 4,305.64 USD |
| 54.75 .. 59.34 | 118 | 38.14% | 18.10 USD | -33.42 USD .. 70.39 USD | 2,135.64 USD |
| 59.34 .. 64.42 | 118 | 38.98% | -17.66 USD | -69.93 USD .. 36.60 USD | -2,084.36 USD |
| 64.42 .. 70.18 | 118 | 40.68% | 19.96 USD | -21.68 USD .. 61.77 USD | 2,355.64 USD |
| 70.18 .. 88.66 | 118 | 33.90% | -3.85 USD | -56.25 USD .. 51.21 USD | -454.36 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 282 | 40.07% | 11.51 USD | -18.38 USD .. 42.27 USD | 3,246.36 USD |
| Short | 308 | 37.99% | 9.78 USD | -25.03 USD .. 45.21 USD | 3,011.84 USD |

### `weekday` (UTC clock: generated before the `report_tz` fix, see README audit note)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 118 | 33.90% | -8.94 USD | -62.25 USD .. 48.92 USD | -1,054.36 USD |
| Mon | 105 | 39.05% | -6.31 USD | -62.11 USD .. 53.68 USD | -662.10 USD |
| Thu | 127 | 38.58% | -10.24 USD | -54.83 USD .. 35.44 USD | -1,300.54 USD |
| Tue | 127 | 39.37% | 41.73 USD | -15.64 USD .. 102.61 USD | 5,299.46 USD |
| Wed | 113 | 44.25% | 35.18 USD | -11.24 USD .. 79.61 USD | 3,975.74 USD |
