# FSP v2 — rule-interpretation grid (rules_grid_net0_n16)

Pre-registered in [README.md](README.md). **In-sample, best of 16 evaluations, development interval (2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00).** Not a validated edge.

A = an invalid first MSS uses up the setup · B = search for the next stop extreme · C = an HL/LH on the breach minute is allowed · D = setups from any hour (not just 09:00–14:30 ET). `+` on, `-` off. Trial 0 is the FSP v1 default.

| Rank | Trial | Rules | net0 USD | Trades | PF | Win % | Avg trade | Max DD | Long | Short |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 8 | A+ B- C- D- | -3,659.58 | 1,679 | 0.974 | 19.12 | -2.18 | 19,005.52 | -4,396.60 | 737.02 |
| 2 | 10 | A+ B- C+ D- | -3,659.58 | 1,679 | 0.974 | 19.12 | -2.18 | 19,005.52 | -4,396.60 | 737.02 |
| 3 | 12 | A+ B+ C- D- | -3,854.30 | 1,715 | 0.973 | 19.07 | -2.25 | 19,221.80 | -4,080.92 | 226.62 |
| 4 | 14 | A+ B+ C+ D- | -3,854.30 | 1,715 | 0.973 | 19.07 | -2.25 | 19,221.80 | -4,080.92 | 226.62 |
| 5 | 1 | A- B- C- D- | -4,674.48 | 1,924 | 0.971 | 19.18 | -2.43 | 20,467.22 | -6,859.00 | 2,184.52 |
| 6 | 3 | A- B- C+ D- | -4,674.48 | 1,924 | 0.971 | 19.18 | -2.43 | 20,467.22 | -6,859.00 | 2,184.52 |
| 7 | 4 | A- B+ C- D- | -5,008.50 | 1,925 | 0.969 | 19.12 | -2.60 | 21,297.22 | -7,219.00 | 2,210.50 |
| 8 | 6 | A- B+ C+ D- | -5,008.50 | 1,925 | 0.969 | 19.12 | -2.60 | 21,297.22 | -7,219.00 | 2,210.50 |
| 9 | 9 | A+ B- C- D+ | -9,312.48 | 2,824 | 0.963 | 18.80 | -3.30 | 28,781.26 | -14,233.98 | 4,921.50 |
| 10 | 11 | A+ B- C+ D+ | -9,312.48 | 2,824 | 0.963 | 18.80 | -3.30 | 28,781.26 | -14,233.98 | 4,921.50 |
| 11 | 13 | A+ B+ C- D+ | -10,317.50 | 2,875 | 0.959 | 18.71 | -3.59 | 29,977.74 | -15,434.48 | 5,116.98 |
| 12 | 15 | A+ B+ C+ D+ | -10,317.50 | 2,875 | 0.959 | 18.71 | -3.59 | 29,977.74 | -15,434.48 | 5,116.98 |
| 13 | 0 | A- B- C+ D+ | -11,925.96 | 3,198 | 0.958 | 18.86 | -3.73 | 30,453.76 | -17,695.72 | 5,769.76 |
| 14 | 2 | A- B- C- D+ | -11,925.96 | 3,198 | 0.958 | 18.86 | -3.73 | 30,453.76 | -17,695.72 | 5,769.76 |
| 15 | 5 | A- B+ C- D+ | -12,512.04 | 3,202 | 0.956 | 18.77 | -3.91 | 31,997.78 | -18,623.76 | 6,111.72 |
| 16 | 7 | A- B+ C+ D+ | -12,512.04 | 3,202 | 0.956 | 18.77 | -3.91 | 31,997.78 | -18,623.76 | 6,111.72 |

## Best of 16: trial 8 (A+ B- C- D-)

In-sample, best of 16 evaluations. Slippage scenarios are not run (execution update, 3 November 2026).

#### Overview

| Metric | Value |
|---|---|
| Net profit | -3,659.58 USD (-7.32%) |
| Total closed trades | 1,679 |
| Percent profitable | 19.12% |
| Profit factor | 0.974 |
| Max equity drawdown | 19,005.52 USD (38.01%) |
| Avg trade | -2.18 USD |
| Avg # bars in trades | 20 |

#### Performance

| Metric | All | Long | Short |
|---|---|---|---|
| Net profit | -3,659.58 USD (-7.32%) | -4,396.60 USD (-8.79%) | 737.02 USD (1.47%) |
| Gross profit | 137,659.58 USD (275.32%) | 63,600.92 USD (127.20%) | 74,058.66 USD (148.12%) |
| Gross loss | 141,319.16 USD (282.64%) | 67,997.52 USD (136.00%) | 73,321.64 USD (146.64%) |
| Commission paid | 6,749.58 USD | 3,336.60 USD | 3,412.98 USD |

| Account | Value |
|---|---|
| Initial capital | 50,000.00 USD |
| Buy & hold return (TV-style, all capital at the first entry) | -2,535.27 USD (-5.07%) |
| Max equity run-up (intrabar) | 20,331.40 USD (40.66%) |
| Max equity drawdown (intrabar) | 19,005.52 USD (38.01%) |
| Open P&L | 0.00 USD |
| Max contracts held | 1 |

#### Trades analysis

| Metric | All | Long | Short |
|---|---|---|---|
| Total closed trades | 1,679 | 830 | 849 |
| Winning trades | 321 | 154 | 167 |
| Losing trades | 1,358 | 676 | 682 |
| Even trades | 0 | 0 | 0 |
| Percent profitable | 19.12% | 18.55% | 19.67% |
| Avg P&L | -2.18 USD | -5.30 USD | 0.87 USD |
| Avg P&L % | 0.00% | -0.00% | 0.01% |
| Avg winning trade | 428.85 USD | 412.99 USD | 443.47 USD |
| Avg losing trade | 104.06 USD | 100.59 USD | 107.51 USD |
| Ratio avg win / avg loss | 4.121 | 4.106 | 4.125 |
| Largest winning trade | 495.98 USD | 495.98 USD | 495.98 USD |
| Largest winning trade % | 2.41% | 1.49% | 2.41% |
| Largest losing trade | 314.02 USD | 254.02 USD | 314.02 USD |
| Largest losing trade % | 0.94% | 0.88% | 0.94% |
| Avg # bars in trades | 20 | 21 | 20 |
| Avg # bars in winning trades | 45 | 49 | 42 |
| Avg # bars in losing trades | 15 | 14 | 15 |

#### Risk/performance ratios

| Metric | Value |
|---|---|
| Sharpe ratio | -0.096 |
| Sortino ratio | -0.127 |
| Profit factor | 0.974 |
| Margin calls | 0 |


## By year

| Year | Trades | Net profit | % profitable | Profit factor |
|---|---|---|---|---|
| 2010 | 69 | -4,107.38 USD | 11.59% | 0.467 |
| 2011 | 141 | -676.82 USD | 24.11% | 0.957 |
| 2012 | 116 | -1,936.32 USD | 18.10% | 0.835 |
| 2013 | 146 | -9,126.92 USD | 10.27% | 0.395 |
| 2014 | 133 | 25.34 USD | 17.29% | 1.002 |
| 2015 | 118 | 3,375.64 USD | 24.58% | 1.352 |
| 2016 | 130 | 3,327.40 USD | 25.38% | 1.362 |
| 2017 | 144 | 311.12 USD | 14.58% | 1.040 |
| 2018 | 133 | 3,425.34 USD | 21.05% | 1.407 |
| 2019 | 130 | 847.40 USD | 18.46% | 1.099 |
| 2020 | 116 | -2,136.32 USD | 14.66% | 0.758 |
| 2021 | 100 | 4,308.00 USD | 25.00% | 1.676 |
| 2022 | 92 | 250.16 USD | 27.17% | 1.021 |
| 2023 | 111 | -1,546.22 USD | 16.22% | 0.847 |

Raw files: `results/failed_swing_point_v2/search/rules_grid_net0_n16/`. Written 2026-11-12T00:41:56+00:00.
