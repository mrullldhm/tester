# Fair Price Reversal (LuxAlgo 9:29 ET), CL1! sessions: feature association, ny

Generated 2026-11-04 15:06 UTC by `python -m tvtester.cli features fair_price_reversal --variant ny`.

> **In-sample.** Development interval only (bars before 2024-01-01 UTC). Nothing here shows a tradable edge: out-of-sample validation is a later feature.

> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of many.

Baseline (feature-1 top combination): `session=ny`, `window=120`, `atr_mult=0.5`, `swing=1`, `target=rr2`. Bars: 2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00 (4,682,668).

## Baseline, commission included: 3,849 trades, net 69,157.02 USD

### `minutes_from_open`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 4 .. 18 | 827 | 34.70% | 20.27 USD | -1.60 USD .. 41.84 USD | 16,765.46 USD |
| 18 .. 30 | 771 | 33.72% | 10.57 USD | -11.40 USD .. 32.08 USD | 8,150.58 USD |
| 30 .. 48 | 716 | 35.06% | 32.14 USD | 6.63 USD .. 55.98 USD | 23,011.68 USD |
| 48 .. 72 | 769 | 35.76% | 5.25 USD | -17.91 USD .. 29.75 USD | 4,038.62 USD |
| 72 .. 119 | 766 | 37.21% | 22.44 USD | -1.11 USD .. 46.13 USD | 17,190.68 USD |

### `anchor_body_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0 .. 0.2041 | 770 | 35.84% | 17.53 USD | -5.38 USD .. 40.50 USD | 13,494.60 USD |
| 0.2041 .. 0.4132 | 770 | 35.58% | 18.93 USD | -3.26 USD .. 41.73 USD | 14,574.60 USD |
| 0.4132 .. 0.6774 | 769 | 35.24% | 11.51 USD | -9.35 USD .. 33.26 USD | 8,848.62 USD |
| 0.6774 .. 1.061 | 770 | 34.16% | 7.25 USD | -14.52 USD .. 29.70 USD | 5,584.60 USD |
| 1.061 .. 5.623 | 770 | 35.58% | 34.62 USD | 10.80 USD .. 58.26 USD | 26,654.60 USD |

### `risk_ticks`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 4 .. 13 | 895 | 32.85% | -4.03 USD | -11.63 USD .. 4.14 USD | -3,607.90 USD |
| 13 .. 17.2 | 645 | 31.16% | -12.25 USD | -26.17 USD .. 1.19 USD | -7,902.90 USD |
| 17.2 .. 23 | 811 | 33.91% | 0.84 USD | -15.67 USD .. 17.41 USD | 679.78 USD |
| 23 .. 32 | 756 | 35.19% | 6.61 USD | -16.78 USD .. 30.73 USD | 5,000.88 USD |
| 32 .. 203 | 742 | 43.40% | 101.06 USD | 60.00 USD .. 142.27 USD | 74,987.16 USD |

### `risk_atr`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.8503 .. 1.802 | 770 | 32.34% | 2.11 USD | -12.32 USD .. 16.11 USD | 1,624.60 USD |
| 1.802 .. 2.167 | 770 | 33.38% | -3.03 USD | -21.54 USD .. 16.13 USD | -2,335.40 USD |
| 2.167 .. 2.521 | 769 | 35.37% | 22.20 USD | 0.83 USD .. 44.89 USD | 17,068.62 USD |
| 2.521 .. 3.063 | 770 | 34.55% | 11.94 USD | -10.35 USD .. 34.32 USD | 9,194.60 USD |
| 3.063 .. 10.24 | 770 | 40.78% | 56.63 USD | 26.22 USD .. 87.55 USD | 43,604.60 USD |

### `range_ratio`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| 0.2698 .. 0.6899 | 767 | 36.38% | 27.65 USD | 5.54 USD .. 49.52 USD | 21,206.66 USD |
| 0.6899 .. 0.845 | 766 | 31.98% | -4.99 USD | -25.63 USD .. 16.82 USD | -3,819.32 USD |
| 0.845 .. 1.019 | 766 | 36.16% | 25.69 USD | 3.62 USD .. 48.52 USD | 19,680.68 USD |
| 1.019 .. 1.278 | 767 | 35.20% | 14.12 USD | -7.84 USD .. 36.70 USD | 10,826.66 USD |
| 1.278 .. 8.425 | 765 | 36.47% | 26.63 USD | -0.25 USD .. 53.15 USD | 20,374.70 USD |
| NaN | 18 | 44.44% | 49.31 USD | -102.59 USD .. 198.84 USD | 887.64 USD |

### `direction`

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Long | 1,964 | 35.03% | 19.74 USD | 4.53 USD .. 34.59 USD | 38,764.72 USD |
| Short | 1,885 | 35.54% | 16.12 USD | 1.84 USD .. 29.98 USD | 30,392.30 USD |

### `weekday` (America/New_York clock)

| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |
|---|---|---|---|---|---|
| Fri | 781 | 36.36% | 25.28 USD | 2.64 USD .. 48.18 USD | 19,740.38 USD |
| Mon | 749 | 35.91% | 17.60 USD | -4.01 USD .. 40.37 USD | 13,179.02 USD |
| Thu | 774 | 33.20% | 7.00 USD | -16.33 USD .. 30.18 USD | 5,418.52 USD |
| Tue | 760 | 36.18% | 26.35 USD | 3.95 USD .. 48.74 USD | 20,024.80 USD |
| Wed | 785 | 34.78% | 13.75 USD | -9.85 USD .. 36.24 USD | 10,794.30 USD |
