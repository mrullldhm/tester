# Supertrend + ATR trail + Kalman trend, M15 signals, CL1! 1m: feature association, ny

Generated 2026-10-31 12:57 UTC by `python -m tvtester.cli features supertrend_kalman --variant ny`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `hours=ny`, `trigger=both`, `vol=rvi`, `exit=flip`, `rr=3`, `swing=5`, `trail_mult=1`, `st_factor=2`, `kalman_q=0.0001`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## 0 ticks slippage: 2,628 trades, net 104,105.44 USD

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 3 .. 52 | 533 | 37.90% | 15.75 USD | -14.08 USD .. 44.82 USD | 8,397.34 USD |
| 52 .. 72 | 521 | 42.99% | 43.04 USD | 0.12 USD .. 86.08 USD | 22,425.58 USD |
| 72 .. 99 | 534 | 43.26% | -0.59 USD | -49.00 USD .. 48.01 USD | -316.68 USD |
| 99 .. 138 | 524 | 49.24% | 71.36 USD | 12.48 USD .. 134.95 USD | 37,393.52 USD |
| 138 .. 969 | 516 | 47.67% | 70.17 USD | -4.01 USD .. 145.02 USD | 36,205.68 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.09765 .. 2.519 | 526 | 44.11% | 93.49 USD | 45.08 USD .. 143.58 USD | 49,175.48 USD |
| 2.519 .. 3.166 | 525 | 41.90% | -2.15 USD | -46.78 USD .. 43.37 USD | -1,130.50 USD |
| 3.166 .. 3.843 | 526 | 43.73% | -20.50 USD | -66.83 USD .. 25.65 USD | -10,784.52 USD |
| 3.843 .. 4.892 | 525 | 45.52% | 63.07 USD | 13.09 USD .. 117.94 USD | 33,109.50 USD |
| 4.892 .. 13.75 | 526 | 45.63% | 64.14 USD | 8.26 USD .. 125.71 USD | 33,735.48 USD |

### `atr_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.592 .. 1.128 | 526 | 38.59% | 74.92 USD | 24.73 USD .. 128.14 USD | 39,405.48 USD |
| 1.128 .. 1.246 | 525 | 38.29% | -39.47 USD | -89.13 USD .. 12.18 USD | -20,720.50 USD |
| 1.246 .. 1.35 | 525 | 49.71% | 79.96 USD | 26.26 USD .. 136.23 USD | 41,979.50 USD |
| 1.35 .. 1.473 | 525 | 48.76% | 64.97 USD | 14.83 USD .. 115.27 USD | 34,109.50 USD |
| 1.473 .. 2.49 | 525 | 45.71% | 19.77 USD | -30.34 USD .. 67.92 USD | 10,379.50 USD |
| NaN | 2 | 0.00% | -524.02 USD | -524.02 USD .. -524.02 USD | -1,048.04 USD |

### `er`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.1332 | 526 | 46.20% | 108.91 USD | 55.26 USD .. 161.15 USD | 57,285.48 USD |
| 0.1332 .. 0.2075 | 525 | 46.67% | 11.31 USD | -35.23 USD .. 57.53 USD | 5,939.50 USD |
| 0.2075 .. 0.2788 | 526 | 42.02% | -28.03 USD | -75.81 USD .. 21.10 USD | -14,744.52 USD |
| 0.2788 .. 0.3693 | 525 | 42.86% | 89.79 USD | 34.32 USD .. 151.62 USD | 47,139.50 USD |
| 0.3693 .. 0.777 | 526 | 43.16% | 16.13 USD | -37.90 USD .. 75.91 USD | 8,485.48 USD |

### `hours_since_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 15 .. 16 | 1,539 | 40.55% | 26.67 USD | -3.71 USD .. 57.21 USD | 41,043.22 USD |
| 16 .. 17 | 446 | 51.57% | 109.86 USD | 50.63 USD .. 173.32 USD | 48,997.08 USD |
| 17 .. 18 | 269 | 43.49% | -0.45 USD | -52.56 USD .. 60.14 USD | -121.38 USD |
| 18 .. 20 | 374 | 50.80% | 37.93 USD | -1.27 USD .. 78.78 USD | 14,186.52 USD |

### `rvi_side`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 50.01 .. 55.96 | 526 | 42.40% | 47.06 USD | -7.97 USD .. 106.80 USD | 24,755.48 USD |
| 55.96 .. 59.91 | 525 | 44.57% | 52.11 USD | 0.02 USD .. 99.94 USD | 27,359.50 USD |
| 59.91 .. 64.15 | 526 | 44.49% | 31.44 USD | -22.08 USD .. 83.72 USD | 16,535.48 USD |
| 64.15 .. 68.83 | 525 | 44.76% | 24.40 USD | -21.72 USD .. 69.98 USD | 12,809.50 USD |
| 68.83 .. 86.46 | 526 | 44.68% | 43.05 USD | -8.02 USD .. 95.91 USD | 22,645.48 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 1,297 | 45.57% | 16.42 USD | -12.18 USD .. 46.04 USD | 21,296.06 USD |
| Short | 1,331 | 42.82% | 62.22 USD | 28.03 USD .. 98.66 USD | 82,809.38 USD |

### `weekday` (UTC clock: generated before the `report_tz` fix, see README audit note)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 500 | 44.80% | 38.34 USD | -9.42 USD .. 86.45 USD | 19,170.00 USD |
| Mon | 504 | 42.26% | 6.85 USD | -44.51 USD .. 53.46 USD | 3,453.92 USD |
| Thu | 521 | 45.11% | 36.36 USD | -15.11 USD .. 89.68 USD | 18,945.58 USD |
| Tue | 537 | 43.20% | 43.07 USD | -11.55 USD .. 95.98 USD | 23,131.26 USD |
| Wed | 566 | 45.41% | 69.62 USD | 12.64 USD .. 127.25 USD | 39,404.68 USD |

## 1 tick slippage: 2,628 trades, net 53,025.44 USD

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 3 .. 52 | 533 | 36.96% | -2.63 USD | -32.47 USD .. 28.77 USD | -1,402.66 USD |
| 52 .. 72 | 521 | 41.07% | 23.89 USD | -18.75 USD .. 68.71 USD | 12,445.58 USD |
| 72 .. 99 | 534 | 41.95% | -20.52 USD | -68.50 USD .. 28.42 USD | -10,956.68 USD |
| 99 .. 138 | 524 | 47.90% | 51.63 USD | -9.44 USD .. 115.74 USD | 27,053.52 USD |
| 138 .. 969 | 516 | 45.93% | 50.17 USD | -21.51 USD .. 121.35 USD | 25,885.68 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.09765 .. 2.519 | 526 | 43.16% | 74.55 USD | 26.86 USD .. 125.14 USD | 39,215.48 USD |
| 2.519 .. 3.166 | 525 | 41.90% | -20.78 USD | -66.02 USD .. 23.47 USD | -10,910.50 USD |
| 3.166 .. 3.843 | 526 | 41.63% | -40.24 USD | -86.20 USD .. 6.62 USD | -21,164.52 USD |
| 3.843 .. 4.892 | 525 | 43.05% | 43.10 USD | -8.77 USD .. 95.49 USD | 22,629.50 USD |
| 4.892 .. 13.75 | 526 | 43.92% | 44.21 USD | -11.23 USD .. 103.77 USD | 23,255.48 USD |

### `atr_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.592 .. 1.128 | 526 | 36.69% | 55.56 USD | 3.51 USD .. 108.16 USD | 29,225.48 USD |
| 1.128 .. 1.246 | 525 | 37.90% | -58.02 USD | -108.12 USD .. -5.64 USD | -30,460.50 USD |
| 1.246 .. 1.35 | 525 | 47.62% | 60.27 USD | 7.13 USD .. 119.64 USD | 31,639.50 USD |
| 1.35 .. 1.473 | 525 | 47.05% | 45.20 USD | -4.95 USD .. 96.04 USD | 23,729.50 USD |
| 1.473 .. 2.49 | 525 | 44.57% | -0.04 USD | -48.27 USD .. 51.40 USD | -20.50 USD |
| NaN | 2 | 0.00% | -544.02 USD | -544.02 USD .. -544.02 USD | -1,088.04 USD |

### `er`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.1332 | 526 | 44.87% | 90.01 USD | 39.81 USD .. 141.43 USD | 47,345.48 USD |
| 0.1332 .. 0.2075 | 525 | 45.14% | -8.72 USD | -54.14 USD .. 37.26 USD | -4,580.50 USD |
| 0.2075 .. 0.2788 | 526 | 40.30% | -47.69 USD | -93.95 USD .. -1.57 USD | -25,084.52 USD |
| 0.2788 .. 0.3693 | 525 | 41.90% | 71.05 USD | 15.24 USD .. 131.73 USD | 37,299.50 USD |
| 0.3693 .. 0.777 | 526 | 41.44% | -3.72 USD | -56.88 USD .. 52.35 USD | -1,954.52 USD |

### `hours_since_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 15 .. 16 | 1,539 | 39.64% | 7.54 USD | -22.98 USD .. 39.31 USD | 11,603.22 USD |
| 16 .. 17 | 446 | 50.00% | 90.08 USD | 33.00 USD .. 151.11 USD | 40,177.08 USD |
| 17 .. 18 | 269 | 41.64% | -20.30 USD | -75.48 USD .. 36.84 USD | -5,461.38 USD |
| 18 .. 20 | 374 | 47.59% | 17.93 USD | -21.58 USD .. 59.56 USD | 6,706.52 USD |

### `rvi_side`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 50.01 .. 55.96 | 526 | 39.73% | 27.79 USD | -30.15 USD .. 87.86 USD | 14,615.48 USD |
| 55.96 .. 59.91 | 525 | 42.67% | 32.68 USD | -16.68 USD .. 81.38 USD | 17,159.50 USD |
| 59.91 .. 64.15 | 526 | 43.73% | 11.85 USD | -37.70 USD .. 62.12 USD | 6,235.48 USD |
| 64.15 .. 68.83 | 525 | 43.81% | 4.93 USD | -39.25 USD .. 53.90 USD | 2,589.50 USD |
| 68.83 .. 86.46 | 526 | 43.73% | 23.62 USD | -28.03 USD .. 78.28 USD | 12,425.48 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 1,297 | 43.79% | -3.44 USD | -33.82 USD .. 24.97 USD | -4,463.94 USD |
| Short | 1,331 | 41.70% | 43.19 USD | 8.70 USD .. 78.91 USD | 57,489.38 USD |

### `weekday` (UTC clock: generated before the `report_tz` fix, see README audit note)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 500 | 43.80% | 19.86 USD | -27.56 USD .. 67.06 USD | 9,930.00 USD |
| Mon | 504 | 39.88% | -13.50 USD | -60.48 USD .. 34.76 USD | -6,806.08 USD |
| Thu | 521 | 42.99% | 16.59 USD | -34.69 USD .. 66.63 USD | 8,645.58 USD |
| Tue | 537 | 42.46% | 23.63 USD | -32.07 USD .. 79.06 USD | 12,691.26 USD |
| Wed | 566 | 44.35% | 50.47 USD | -7.45 USD .. 109.36 USD | 28,564.68 USD |
