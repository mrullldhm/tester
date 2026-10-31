# Supertrend + ATR trail + Kalman trend, M15 signals, CL1! 1m: feature association, all

Generated 2026-10-31 12:57 UTC by `python -m tvtester.cli features supertrend_kalman --variant all`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `hours=all`, `trigger=both`, `vol=atr_ratio:1.3`, `exit=fixed`, `rr=3`, `swing=3`, `trail_mult=1`, `st_factor=3`, `kalman_q=0.0001`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## 0 ticks slippage: 3,728 trades, net 91,453.44 USD

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1 .. 22 | 775 | 25.29% | -2.95 USD | -19.14 USD .. 13.38 USD | -2,285.50 USD |
| 22 .. 34 | 730 | 21.37% | -43.95 USD | -70.61 USD .. -15.47 USD | -32,084.60 USD |
| 34 .. 50 | 777 | 26.00% | 4.59 USD | -37.67 USD .. 48.58 USD | 3,566.46 USD |
| 50 .. 76 | 715 | 26.43% | 13.06 USD | -50.67 USD .. 80.47 USD | 9,335.70 USD |
| 76 .. 434 | 731 | 31.74% | 154.48 USD | 24.07 USD .. 288.01 USD | 112,921.38 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.04398 .. 1.617 | 746 | 26.68% | 26.18 USD | -3.97 USD .. 57.18 USD | 19,531.08 USD |
| 1.617 .. 2.28 | 745 | 20.13% | -73.16 USD | -117.32 USD .. -28.84 USD | -54,504.90 USD |
| 2.28 .. 3.185 | 746 | 28.02% | 55.06 USD | -6.47 USD .. 115.22 USD | 41,071.08 USD |
| 3.185 .. 4.132 | 745 | 26.17% | 16.57 USD | -61.28 USD .. 98.08 USD | 12,345.10 USD |
| 4.132 .. 26.08 | 746 | 29.76% | 97.87 USD | -20.29 USD .. 214.89 USD | 73,011.08 USD |

### `atr_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.4317 .. 0.6901 | 746 | 25.34% | -0.29 USD | -39.97 USD .. 41.19 USD | -218.92 USD |
| 0.6901 .. 0.8061 | 745 | 24.83% | 16.19 USD | -30.07 USD .. 66.16 USD | 12,065.10 USD |
| 0.8061 .. 0.9406 | 746 | 27.21% | 21.33 USD | -46.71 USD .. 93.92 USD | 15,911.08 USD |
| 0.9406 .. 1.107 | 745 | 24.83% | -6.36 USD | -82.29 USD .. 76.13 USD | -4,734.90 USD |
| 1.107 .. 1.3 | 746 | 28.55% | 91.73 USD | -10.36 USD .. 199.77 USD | 68,431.08 USD |

### `er`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.1184 | 746 | 24.66% | -72.60 USD | -120.27 USD .. -24.98 USD | -54,158.92 USD |
| 0.1184 .. 0.2078 | 745 | 28.19% | 120.57 USD | 52.94 USD .. 192.14 USD | 89,825.10 USD |
| 0.2078 .. 0.2857 | 752 | 25.27% | -20.03 USD | -79.80 USD .. 40.83 USD | -15,063.04 USD |
| 0.2857 .. 0.3886 | 739 | 25.71% | 44.90 USD | -32.36 USD .. 124.95 USD | 33,179.22 USD |
| 0.3886 .. 0.8409 | 746 | 26.94% | 50.50 USD | -47.67 USD .. 152.02 USD | 37,671.08 USD |

### `hours_since_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 4 | 860 | 27.44% | 18.51 USD | -39.18 USD .. 82.57 USD | 15,922.80 USD |
| 4 .. 8 | 688 | 23.98% | -28.54 USD | -89.94 USD .. 31.90 USD | -19,635.76 USD |
| 8 .. 11 | 821 | 26.07% | 38.59 USD | -23.78 USD .. 101.98 USD | 31,679.58 USD |
| 11 .. 14 | 628 | 26.91% | 56.12 USD | -28.20 USD .. 142.34 USD | 35,245.44 USD |
| 14 .. 23 | 731 | 26.13% | 38.63 USD | -56.97 USD .. 132.86 USD | 28,241.38 USD |

### `rvi_side`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 17.82 .. 51.22 | 746 | 26.81% | 46.72 USD | -19.34 USD .. 112.94 USD | 34,851.08 USD |
| 51.22 .. 57.4 | 745 | 23.89% | -17.21 USD | -85.52 USD .. 55.03 USD | -12,824.90 USD |
| 57.4 .. 62.45 | 746 | 28.28% | 82.79 USD | 8.88 USD .. 158.98 USD | 61,761.08 USD |
| 62.45 .. 68.49 | 745 | 25.10% | -34.07 USD | -107.12 USD .. 44.14 USD | -25,384.90 USD |
| 68.49 .. 89.87 | 746 | 26.68% | 44.30 USD | -38.00 USD .. 122.50 USD | 33,051.08 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 1,885 | 25.36% | 2.13 USD | -42.83 USD .. 46.47 USD | 4,022.30 USD |
| Short | 1,843 | 26.97% | 47.44 USD | 4.43 USD .. 92.31 USD | 87,431.14 USD |

### `weekday` (UTC clock: generated before the `report_tz` fix, see README audit note)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 702 | 24.79% | -41.54 USD | -105.20 USD .. 22.93 USD | -29,162.04 USD |
| Mon | 784 | 27.17% | 96.68 USD | 20.41 USD .. 179.21 USD | 75,798.32 USD |
| Sun | 67 | 25.37% | -121.48 USD | -366.56 USD .. 144.34 USD | -8,139.34 USD |
| Thu | 754 | 26.26% | 18.42 USD | -48.02 USD .. 89.39 USD | 13,888.92 USD |
| Tue | 725 | 25.93% | 27.70 USD | -42.55 USD .. 102.57 USD | 20,085.50 USD |
| Wed | 696 | 26.58% | 27.27 USD | -52.02 USD .. 118.00 USD | 18,982.08 USD |

## 1 tick slippage: 3,716 trades, net 30,411.68 USD

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1 .. 22 | 767 | 24.90% | -17.48 USD | -35.24 USD .. 0.95 USD | -13,403.34 USD |
| 22 .. 34 | 732 | 21.31% | -60.30 USD | -88.43 USD .. -30.12 USD | -44,142.64 USD |
| 34 .. 49 | 731 | 26.13% | -8.18 USD | -49.67 USD .. 37.41 USD | -5,978.62 USD |
| 49 .. 76 | 759 | 25.96% | -10.94 USD | -77.56 USD .. 51.94 USD | -8,301.18 USD |
| 76 .. 434 | 727 | 31.64% | 140.63 USD | 6.42 USD .. 273.48 USD | 102,237.46 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.04398 .. 1.617 | 744 | 26.21% | 10.43 USD | -19.50 USD .. 41.20 USD | 7,759.12 USD |
| 1.617 .. 2.279 | 743 | 20.05% | -90.59 USD | -134.74 USD .. -46.87 USD | -67,306.86 USD |
| 2.279 .. 3.18 | 743 | 27.73% | 33.88 USD | -25.05 USD .. 96.23 USD | 25,173.14 USD |
| 3.18 .. 4.117 | 743 | 26.24% | 3.33 USD | -77.14 USD .. 85.34 USD | 2,473.14 USD |
| 4.117 .. 26.08 | 743 | 29.61% | 83.87 USD | -30.07 USD .. 201.41 USD | 62,313.14 USD |

### `atr_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.4317 .. 0.6908 | 744 | 25.40% | -12.03 USD | -53.21 USD .. 29.25 USD | -8,950.88 USD |
| 0.6908 .. 0.8064 | 743 | 24.23% | -6.44 USD | -55.54 USD .. 44.76 USD | -4,786.86 USD |
| 0.8064 .. 0.9411 | 743 | 26.92% | -3.21 USD | -75.43 USD .. 73.07 USD | -2,386.86 USD |
| 0.9411 .. 1.109 | 743 | 24.63% | -20.39 USD | -101.05 USD .. 62.46 USD | -15,146.86 USD |
| 1.109 .. 1.3 | 743 | 28.67% | 83.02 USD | -17.49 USD .. 183.64 USD | 61,683.14 USD |

### `er`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.1181 | 744 | 24.33% | -86.12 USD | -132.24 USD .. -36.88 USD | -64,070.88 USD |
| 0.1181 .. 0.2073 | 743 | 28.13% | 105.35 USD | 38.09 USD .. 175.90 USD | 78,273.14 USD |
| 0.2073 .. 0.2857 | 752 | 25.00% | -42.68 USD | -100.78 USD .. 16.96 USD | -32,093.04 USD |
| 0.2857 .. 0.3881 | 734 | 25.48% | 26.51 USD | -49.05 USD .. 109.98 USD | 19,459.32 USD |
| 0.3881 .. 0.8409 | 743 | 26.92% | 38.82 USD | -57.89 USD .. 136.37 USD | 28,843.14 USD |

### `hours_since_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 4 | 859 | 27.12% | 1.11 USD | -56.38 USD .. 59.16 USD | 956.82 USD |
| 4 .. 8 | 682 | 24.05% | -38.36 USD | -95.00 USD .. 24.16 USD | -26,161.64 USD |
| 8 .. 11 | 817 | 25.83% | 18.20 USD | -46.17 USD .. 82.71 USD | 14,865.66 USD |
| 11 .. 14 | 623 | 26.48% | 34.90 USD | -48.50 USD .. 122.26 USD | 21,745.54 USD |
| 14 .. 23 | 735 | 26.12% | 25.86 USD | -65.21 USD .. 122.31 USD | 19,005.30 USD |

### `rvi_side`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 17.82 .. 51.18 | 744 | 26.61% | 32.43 USD | -31.12 USD .. 99.64 USD | 24,129.12 USD |
| 51.18 .. 57.32 | 743 | 23.69% | -34.30 USD | -103.39 USD .. 37.53 USD | -25,486.86 USD |
| 57.32 .. 62.37 | 743 | 27.86% | 63.68 USD | -9.20 USD .. 138.27 USD | 47,313.14 USD |
| 62.37 .. 68.41 | 743 | 25.03% | -47.02 USD | -120.72 USD .. 27.17 USD | -34,936.86 USD |
| 68.41 .. 89.87 | 743 | 26.65% | 26.10 USD | -53.41 USD .. 106.71 USD | 19,393.14 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 1,882 | 25.19% | -14.89 USD | -57.69 USD .. 30.07 USD | -28,015.64 USD |
| Short | 1,834 | 26.77% | 31.86 USD | -11.46 USD .. 74.76 USD | 58,427.32 USD |

### `weekday` (UTC clock: generated before the `report_tz` fix, see README audit note)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 699 | 24.46% | -62.63 USD | -128.79 USD .. 2.74 USD | -43,779.98 USD |
| Mon | 783 | 27.08% | 82.74 USD | 8.48 USD .. 164.07 USD | 64,782.34 USD |
| Sun | 67 | 25.37% | -137.90 USD | -380.98 USD .. 126.44 USD | -9,239.34 USD |
| Thu | 750 | 26.27% | 0.91 USD | -67.61 USD .. 72.97 USD | 685.00 USD |
| Tue | 723 | 25.73% | 11.68 USD | -60.55 USD .. 82.65 USD | 8,443.54 USD |
| Wed | 694 | 26.22% | 13.72 USD | -72.26 USD .. 100.95 USD | 9,520.12 USD |
