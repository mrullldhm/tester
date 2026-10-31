# Fair Price Reversal (LuxAlgo 9:29 ET), CL1! sessions: feature association, ny

Generated 2026-10-31 05:06 UTC by `python -m tvtester.cli features fair_price_reversal --variant ny`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `session=ny`, `window=120`, `atr_mult=0.5`, `swing=3`, `target=rr2`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## 0 ticks slippage: 3,054 trades, net 55,002.92 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 9 .. 32 | 656 | 37.80% | 22.29 USD | -8.25 USD .. 51.45 USD | 14,622.88 USD |
| 32 .. 47 | 595 | 33.28% | 4.89 USD | -32.19 USD .. 41.96 USD | 2,908.10 USD |
| 47 .. 64 | 600 | 37.83% | 4.23 USD | -28.28 USD .. 36.31 USD | 2,538.00 USD |
| 64 .. 88 | 602 | 39.87% | 43.09 USD | 6.64 USD .. 77.04 USD | 25,939.96 USD |
| 88 .. 119 | 601 | 36.61% | 14.97 USD | -20.58 USD .. 51.72 USD | 8,993.98 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.2041 | 611 | 36.33% | -6.61 USD | -40.23 USD .. 26.58 USD | -4,036.22 USD |
| 0.2041 .. 0.4165 | 611 | 34.70% | 0.73 USD | -30.49 USD .. 31.92 USD | 443.78 USD |
| 0.4165 .. 0.6865 | 610 | 40.16% | 52.55 USD | 17.13 USD .. 85.96 USD | 32,057.80 USD |
| 0.6865 .. 1.065 | 611 | 35.84% | 4.02 USD | -28.60 USD .. 36.79 USD | 2,453.78 USD |
| 1.065 .. 5.391 | 611 | 38.46% | 39.42 USD | 4.22 USD .. 76.62 USD | 24,083.78 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 6 .. 19 | 629 | 33.07% | -6.15 USD | -19.88 USD .. 7.78 USD | -3,868.58 USD |
| 19 .. 25 | 598 | 34.45% | -1.70 USD | -21.23 USD .. 18.43 USD | -1,013.96 USD |
| 25 .. 33 | 678 | 36.58% | 10.04 USD | -14.48 USD .. 36.89 USD | 6,804.44 USD |
| 33 .. 43 | 557 | 43.99% | 82.80 USD | 45.45 USD .. 117.26 USD | 46,120.86 USD |
| 43 .. 189 | 592 | 38.18% | 11.76 USD | -47.80 USD .. 68.26 USD | 6,960.16 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1.296 .. 2.599 | 611 | 33.06% | -15.95 USD | -40.01 USD .. 8.99 USD | -9,746.22 USD |
| 2.599 .. 3.066 | 611 | 37.64% | 29.89 USD | -0.85 USD .. 58.47 USD | 18,263.78 USD |
| 3.066 .. 3.556 | 610 | 34.43% | -8.17 USD | -39.57 USD .. 21.10 USD | -4,982.20 USD |
| 3.556 .. 4.231 | 611 | 38.63% | 38.52 USD | 1.85 USD .. 73.85 USD | 23,533.78 USD |
| 4.231 .. 12.9 | 611 | 41.73% | 45.72 USD | 3.69 USD .. 93.78 USD | 27,933.78 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.2698 .. 0.6964 | 608 | 37.66% | 14.20 USD | -17.92 USD .. 46.63 USD | 8,635.84 USD |
| 0.6964 .. 0.8487 | 607 | 36.57% | 18.60 USD | -13.45 USD .. 50.94 USD | 11,289.86 USD |
| 0.8487 .. 1.02 | 607 | 37.23% | 31.71 USD | -2.77 USD .. 67.67 USD | 19,249.86 USD |
| 1.02 .. 1.286 | 607 | 36.74% | 10.56 USD | -20.71 USD .. 41.37 USD | 6,409.86 USD |
| 1.286 .. 8.425 | 607 | 37.23% | 14.20 USD | -26.04 USD .. 54.32 USD | 8,619.86 USD |
| NaN | 18 | 38.89% | 44.31 USD | -201.35 USD .. 235.98 USD | 797.64 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 1,570 | 37.39% | 24.08 USD | 1.46 USD .. 44.48 USD | 37,808.60 USD |
| Short | 1,484 | 36.79% | 11.59 USD | -11.48 USD .. 33.37 USD | 17,194.32 USD |

### `weekday`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 620 | 39.19% | 25.45 USD | -6.65 USD .. 57.02 USD | 15,777.60 USD |
| Mon | 600 | 40.00% | 45.43 USD | 12.10 USD .. 78.95 USD | 27,258.00 USD |
| Thu | 608 | 34.70% | 2.03 USD | -33.68 USD .. 37.56 USD | 1,235.84 USD |
| Tue | 618 | 35.92% | 2.39 USD | -29.78 USD .. 34.45 USD | 1,475.64 USD |
| Wed | 608 | 35.69% | 15.22 USD | -17.62 USD .. 50.85 USD | 9,255.84 USD |

## 1 tick slippage: 3,049 trades, net 2,423.02 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 9 .. 32 | 656 | 37.35% | 4.59 USD | -25.68 USD .. 36.21 USD | 3,012.88 USD |
| 32 .. 46.2 | 564 | 32.98% | -14.18 USD | -50.43 USD .. 26.60 USD | -7,997.28 USD |
| 46.2 .. 64 | 631 | 37.08% | -10.93 USD | -44.28 USD .. 23.08 USD | -6,896.62 USD |
| 64 .. 88 | 599 | 39.57% | 26.88 USD | -9.43 USD .. 61.92 USD | 16,102.02 USD |
| 88 .. 119 | 599 | 35.56% | -3.00 USD | -38.20 USD .. 34.43 USD | -1,797.98 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.2039 | 610 | 35.90% | -23.45 USD | -55.59 USD .. 10.53 USD | -14,302.20 USD |
| 0.2039 .. 0.4164 | 610 | 34.10% | -18.54 USD | -49.58 USD .. 12.95 USD | -11,312.20 USD |
| 0.4164 .. 0.6855 | 609 | 40.07% | 39.86 USD | 7.16 USD .. 73.08 USD | 24,271.82 USD |
| 0.6855 .. 1.064 | 610 | 34.92% | -17.99 USD | -48.94 USD .. 13.70 USD | -10,972.20 USD |
| 1.064 .. 5.391 | 610 | 37.87% | 24.16 USD | -12.06 USD .. 62.67 USD | 14,737.80 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 6 .. 19 | 628 | 32.64% | -22.00 USD | -36.37 USD .. -8.01 USD | -13,814.56 USD |
| 19 .. 25 | 598 | 34.28% | -16.51 USD | -37.33 USD .. 5.76 USD | -9,873.96 USD |
| 25 .. 33 | 676 | 35.36% | -10.25 USD | -36.29 USD .. 16.04 USD | -6,927.52 USD |
| 33 .. 43 | 556 | 43.71% | 67.45 USD | 29.83 USD .. 104.54 USD | 37,504.88 USD |
| 43 .. 189 | 591 | 37.73% | -7.56 USD | -69.54 USD .. 53.04 USD | -4,465.82 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 1.296 .. 2.599 | 610 | 32.79% | -32.92 USD | -55.70 USD .. -8.56 USD | -20,082.20 USD |
| 2.599 .. 3.065 | 610 | 37.38% | 13.80 USD | -15.95 USD .. 43.31 USD | 8,417.80 USD |
| 3.065 .. 3.557 | 609 | 33.33% | -29.57 USD | -59.17 USD .. 2.64 USD | -18,008.18 USD |
| 3.557 .. 4.233 | 610 | 38.20% | 21.37 USD | -15.12 USD .. 58.96 USD | 13,037.80 USD |
| 4.233 .. 12.9 | 610 | 41.15% | 31.24 USD | -14.18 USD .. 75.93 USD | 19,057.80 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.2698 .. 0.6963 | 607 | 37.07% | -1.55 USD | -33.95 USD .. 32.31 USD | -940.14 USD |
| 0.6963 .. 0.8477 | 606 | 36.47% | 3.50 USD | -30.07 USD .. 36.13 USD | 2,123.88 USD |
| 0.8477 .. 1.02 | 606 | 36.14% | 9.12 USD | -23.87 USD .. 43.86 USD | 5,523.88 USD |
| 1.02 .. 1.286 | 606 | 36.30% | -6.38 USD | -38.80 USD .. 28.17 USD | -3,866.12 USD |
| 1.286 .. 8.425 | 606 | 36.80% | -1.61 USD | -40.91 USD .. 37.35 USD | -976.12 USD |
| NaN | 18 | 38.89% | 30.98 USD | -219.00 USD .. 225.65 USD | 557.64 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 1,566 | 36.91% | 6.19 USD | -16.28 USD .. 27.83 USD | 9,694.68 USD |
| Short | 1,483 | 36.21% | -4.90 USD | -28.03 USD .. 17.20 USD | -7,271.66 USD |

### `weekday`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 618 | 38.03% | 5.19 USD | -28.06 USD .. 38.12 USD | 3,205.64 USD |
| Mon | 599 | 39.90% | 30.92 USD | -4.26 USD .. 65.74 USD | 18,522.02 USD |
| Thu | 608 | 34.38% | -14.86 USD | -51.40 USD .. 21.26 USD | -9,034.16 USD |
| Tue | 616 | 35.55% | -15.53 USD | -48.48 USD .. 17.67 USD | -9,566.32 USD |
| Wed | 608 | 35.03% | -1.16 USD | -35.42 USD .. 34.59 USD | -704.16 USD |
