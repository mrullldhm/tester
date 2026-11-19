The RTH result is a credible research lead, but **no version qualifies for frozen validation under the declared screen**. The 78.5% positive share is correlated evidence, not 288 independent votes.

**All performance numbers below are dev, in-sample (2010-06–2021), selected after the best-of-1,728 screen.** I rebuilt `rth/reb/none/e20/r2/attempts=1`: **547 trades, $13,560 net, PF 1.330**, 38.76% wins, $24.79/trade. It exactly matches the screened row.

| Year | Trades | Net $ | PF |
|---|---:|---:|---:|
| 2010* | 21 | 2,125 | 2.32 |
| 2011 | 38 | 2,826 | 1.65 |
| 2012 | 43 | 806 | 1.22 |
| 2013 | 34 | 2,413 | 2.11 |
| 2014 | 40 | −62 | 0.98 |
| 2015 | 40 | 878 | 1.26 |
| 2016 | 52 | −640 | 0.82 |
| 2017 | 51 | 1,634 | 1.64 |
| 2018 | 49 | 1,832 | 1.53 |
| 2019 | 61 | 74 | 1.02 |
| 2020 | 54 | 1,312 | 1.40 |
| 2021 | 64 | 361 | 1.06 |

*2010 starts in June. Both halves are positive: $8,987 / $4,573. Longs: 259 trades, $7,204, PF 1.363; shorts: 288, $6,356, PF 1.299. Each side is positive in 9/12 years. Recent profitability is weaker than early profitability.

The top 10 days contribute **$7,460, or 55.0% of net**; excluding them leaves $6,101. Concentration matters, but they do not explain all profitability.

Using 10,000 resamples of complete trading days, including inactive days, the fixed-version 95% bootstrap net interval is **$3,903–$23,557**; 0.24% of resamples are nonpositive. With consecutive five-/20-day blocks, intervals are $4,313–$22,884 / $5,206–$22,410. These are conditional, unadjusted intervals—not proof after selecting among 1,728 versions.

The **1,000-run random-entry null** transplants all 1,043 orders’ daily schedules onto random dates within the same year, preserving exact CT signal minutes, sides, close-to-limit offsets, planned risk/2R brackets, expiry and one-attempt rules. Destination days are unique within each run; unfilled orders remain unfilled when the engine says so. No pattern features are required.

Null median: **497 fills, $1,240 net, PF 1.031**; 60.8% of portfolios profit. Its 95% net range is −$7,301 to $9,715. Only 3/1,000 reach the observed net; plus-one nominal p = **0.0040**. Thus arbitrary RTH brackets show mild profitability, while the pattern adds suggestive excess. This does **not** establish a selection-adjusted edge: p exceeds the conservative 0.05/1,728 threshold, and this control does not simulate the maximum across the grid. Matching year also leaves local volatility/regime differences uncontrolled.

Five raw-bar checks passed, including all intervening entry/exit bars. Prices below are entry → exit; stop/target shown separately.

| Date / side | CT entry → exit | Prices | Stop / target | Exit |
|---|---|---|---|---|
| 2010-06-15 short | 10:20 → 10:25 | 76.55 → 76.31 | 76.67 / 76.31 | Target |
| 2021-12-01 short | 09:39 → 10:46 | 68.40 → 67.46 | 68.87 / 67.46 | Target |
| 2010-06-11 long | 10:24 → 10:29 | 74.00 → 73.83 | 73.83 / 74.34 | Stop |
| 2021-12-31 short | 10:05 → 10:13 | 76.17 → 76.25 | 76.25 / 76.01 | Stop |
| 2011-02-22 long | 10:05 → 10:24 | 94.00 → 95.00 | 93.50 / 95.00 | Target |

These verify compatibility with raw OHLC and engine assumptions, not actual queue fills.

Fixed-size Combine sensitivity, retaining actual intratrade paths:

| Contracts | Rolling pass | Sequential $/pass |
|---:|---:|---:|
| 1 | 89.76% | 1,764 |
| 2 | 66.67% | 760 |
| 3 | 49.97% | 546 |
| 4 | 44.93% | 522 |
| 5 | 36.87% | 445 |

**No size clears both gates.** At one contract, median passing duration is 676 trading days. At five, the historical worst trade scales to $2,670, exceeding the $2,000 MLL. Sizing is additional exploratory testing, not a rescue of the frozen screen. No paid Combine deployment is justified; retain this exact simple version at one contract only as a research lead. No validation/holdout was accessed.
