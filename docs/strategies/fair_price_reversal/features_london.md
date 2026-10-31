# Fair Price Reversal (LuxAlgo 9:29 ET), CL1! sessions: feature association, london

Generated 2026-10-31 05:06 UTC by `python -m tvtester.cli features fair_price_reversal --variant london`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `session=london`, `window=120`, `atr_mult=2.0`, `swing=3`, `target=rr2`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## 0 ticks slippage: 3,120 trades, net 40,277.60 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 9 .. 34 | 658 | 35.41% | 8.99 USD | -10.38 USD .. 28.53 USD | 5,914.84 USD |
| 34 .. 50 | 611 | 37.15% | 10.14 USD | -9.86 USD .. 30.93 USD | 6,193.78 USD |
| 50 .. 66 | 616 | 35.71% | 8.33 USD | -10.61 USD .. 27.21 USD | 5,133.68 USD |
| 66 .. 88 | 628 | 41.08% | 34.52 USD | 12.47 USD .. 56.75 USD | 21,675.44 USD |
| 88 .. 119 | 607 | 37.23% | 2.24 USD | -18.24 USD .. 23.64 USD | 1,359.86 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.3747 | 1,248 | 34.62% | -0.66 USD | -16.13 USD .. 15.15 USD | -826.96 USD |
| 0.3747 .. 0.5871 | 624 | 42.47% | 33.18 USD | 15.52 USD .. 51.94 USD | 20,701.52 USD |
| 0.5871 .. 0.9755 | 624 | 37.18% | 7.44 USD | -11.83 USD .. 27.88 USD | 4,641.52 USD |
| 0.9755 .. 13.61 | 624 | 37.66% | 25.26 USD | 4.79 USD .. 46.44 USD | 15,761.52 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 4 .. 11 | 629 | 33.86% | -1.70 USD | -10.61 USD .. 7.60 USD | -1,068.58 USD |
| 11 .. 15 | 780 | 38.08% | 10.36 USD | -0.51 USD .. 21.51 USD | 8,084.40 USD |
| 15 .. 19 | 557 | 35.73% | -1.26 USD | -16.21 USD .. 14.41 USD | -699.14 USD |
| 19 .. 25 | 531 | 35.40% | -7.09 USD | -27.25 USD .. 13.95 USD | -3,764.62 USD |
| 25 .. 129 | 623 | 42.86% | 60.55 USD | 24.55 USD .. 94.72 USD | 37,725.54 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1.546 .. 2.955 | 624 | 32.37% | -4.77 USD | -20.31 USD .. 11.83 USD | -2,978.48 USD |
| 2.955 .. 3.496 | 624 | 35.42% | 15.64 USD | -5.50 USD .. 37.12 USD | 9,761.52 USD |
| 3.496 .. 4.058 | 624 | 39.42% | 16.01 USD | -4.13 USD .. 36.99 USD | 9,991.52 USD |
| 4.058 .. 4.89 | 624 | 36.86% | 13.74 USD | -7.53 USD .. 35.19 USD | 8,571.52 USD |
| 4.89 .. 22.46 | 624 | 42.47% | 23.93 USD | 0.24 USD .. 47.83 USD | 14,931.52 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.2991 .. 0.6947 | 620 | 38.23% | 24.40 USD | 5.51 USD .. 44.00 USD | 15,127.60 USD |
| 0.6947 .. 0.8425 | 619 | 34.57% | -6.38 USD | -23.44 USD .. 11.74 USD | -3,948.38 USD |
| 0.8425 .. 1.017 | 620 | 38.06% | 10.01 USD | -8.27 USD .. 28.66 USD | 6,207.60 USD |
| 1.017 .. 1.279 | 619 | 37.96% | 10.39 USD | -10.04 USD .. 31.28 USD | 6,431.62 USD |
| 1.279 .. 4.791 | 620 | 38.55% | 29.77 USD | 6.66 USD .. 54.22 USD | 18,457.60 USD |
| NaN | 22 | 13.64% | -90.84 USD | -136.63 USD .. -41.22 USD | -1,998.44 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 1,624 | 37.68% | 14.05 USD | 0.81 USD .. 27.59 USD | 22,821.52 USD |
| Short | 1,496 | 36.90% | 11.67 USD | -1.24 USD .. 25.22 USD | 17,456.08 USD |

### `weekday`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 623 | 36.92% | 20.30 USD | -1.38 USD .. 43.55 USD | 12,645.54 USD |
| Mon | 636 | 34.12% | -6.10 USD | -24.57 USD .. 11.91 USD | -3,876.72 USD |
| Thu | 617 | 36.30% | 10.65 USD | -9.46 USD .. 31.10 USD | 6,569.66 USD |
| Tue | 620 | 40.48% | 27.88 USD | 7.79 USD .. 48.25 USD | 17,287.60 USD |
| Wed | 624 | 38.78% | 12.26 USD | -7.65 USD .. 32.62 USD | 7,651.52 USD |

## 1 tick slippage: 3,113 trades, net -13,754.26 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 9 .. 34 | 658 | 34.95% | -5.51 USD | -25.57 USD .. 15.02 USD | -3,625.16 USD |
| 34 .. 50 | 611 | 35.68% | -9.76 USD | -31.32 USD .. 11.92 USD | -5,966.22 USD |
| 50 .. 66 | 614 | 34.69% | -8.81 USD | -28.61 USD .. 9.90 USD | -5,408.28 USD |
| 66 .. 88 | 626 | 39.78% | 19.35 USD | -3.35 USD .. 42.50 USD | 12,113.48 USD |
| 88 .. 119 | 604 | 35.43% | -17.99 USD | -37.87 USD .. 4.91 USD | -10,868.08 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.3753 | 1,245 | 33.57% | -17.59 USD | -32.87 USD .. -2.05 USD | -21,894.90 USD |
| 0.3753 .. 0.5874 | 623 | 41.25% | 16.45 USD | -1.38 USD .. 34.24 USD | 10,245.54 USD |
| 0.5874 .. 0.976 | 622 | 35.69% | -12.03 USD | -33.39 USD .. 7.37 USD | -7,480.44 USD |
| 0.976 .. 13.61 | 623 | 36.44% | 8.63 USD | -11.09 USD .. 30.26 USD | 5,375.54 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 4 .. 11 | 629 | 32.11% | -19.00 USD | -28.26 USD .. -9.61 USD | -11,948.58 USD |
| 11 .. 15 | 780 | 37.18% | -5.92 USD | -18.35 USD .. 6.22 USD | -4,615.60 USD |
| 15 .. 19 | 555 | 34.05% | -20.29 USD | -37.81 USD .. -4.18 USD | -11,261.10 USD |
| 19 .. 25 | 527 | 33.97% | -25.90 USD | -47.69 USD .. -4.15 USD | -13,648.54 USD |
| 25 .. 129 | 622 | 42.44% | 44.57 USD | 10.01 USD .. 80.62 USD | 27,719.56 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1.546 .. 2.951 | 623 | 31.14% | -22.62 USD | -38.94 USD .. -5.99 USD | -14,094.46 USD |
| 2.951 .. 3.496 | 622 | 34.57% | -0.93 USD | -22.33 USD .. 20.31 USD | -580.44 USD |
| 3.496 .. 4.057 | 623 | 37.88% | -1.89 USD | -23.02 USD .. 19.51 USD | -1,174.46 USD |
| 4.057 .. 4.89 | 622 | 36.17% | -0.72 USD | -22.04 USD .. 21.20 USD | -450.44 USD |
| 4.89 .. 22.46 | 623 | 40.77% | 4.09 USD | -19.11 USD .. 28.35 USD | 2,545.54 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.2991 .. 0.6945 | 619 | 36.19% | 7.74 USD | -12.04 USD .. 28.50 USD | 4,791.62 USD |
| 0.6945 .. 0.8423 | 618 | 33.66% | -24.67 USD | -42.80 USD .. -5.43 USD | -15,244.36 USD |
| 0.8423 .. 1.016 | 618 | 37.06% | -6.53 USD | -25.12 USD .. 13.27 USD | -4,034.36 USD |
| 1.016 .. 1.279 | 618 | 36.25% | -10.07 USD | -31.60 USD .. 10.81 USD | -6,224.36 USD |
| 1.279 .. 4.791 | 618 | 38.19% | 15.11 USD | -9.18 USD .. 40.12 USD | 9,335.64 USD |
| NaN | 22 | 13.64% | -108.11 USD | -156.75 USD .. -57.48 USD | -2,378.44 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 1,617 | 36.55% | -2.47 USD | -15.24 USD .. 11.76 USD | -4,000.34 USD |
| Short | 1,496 | 35.63% | -6.52 USD | -19.42 USD .. 6.94 USD | -9,753.92 USD |

### `weekday`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 622 | 35.53% | 2.70 USD | -19.40 USD .. 26.49 USD | 1,679.56 USD |
| Mon | 634 | 33.12% | -23.63 USD | -43.24 USD .. -4.50 USD | -14,978.68 USD |
| Thu | 615 | 35.77% | -3.63 USD | -25.11 USD .. 15.92 USD | -2,232.30 USD |
| Tue | 619 | 38.93% | 10.03 USD | -10.70 USD .. 32.15 USD | 6,211.62 USD |
| Wed | 623 | 37.24% | -7.12 USD | -27.05 USD .. 13.21 USD | -4,434.46 USD |
