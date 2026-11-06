# Fair Price Reversal (LuxAlgo 9:29 ET), CL1! sessions: results

> **Historical; superseded pending rerun (5 November 2026).** The shared owner swing detector and
> this strategy's Pine twin now enforce the clarified leg-extreme validity condition. The results
> below predate the correction and have not been rerun under it.

Generated 2026-11-04 13:56 UTC by `python -m tvtester.cli test fair_price_reversal`.

Source: LuxAlgo, [9:29 ET Fair Price Reversal](https://www.luxalgo.com/library/indicator/9-29-et-fair-price-reversal/)
(Pine v6, MPL-2.0). The original reads NQ around the 9:30 ET stock open. Here it runs on CL1! with the anchor
moved to the candle before each CL session open:

| Variant | Session open | Anchor candle | Malaysia time (UTC+8) | Flat at |
|---|---|---|---|---|
| asia | 09:00 Asia/Shanghai (same clock as Singapore / Kuala Lumpur, no DST) | 08:59 | 09:00 all year | 15:00 Asia/Shanghai |
| london | 08:00 Europe/London | 07:59 | 15:00 (UK summer) / 16:00 (UK winter) | 13:00 London |
| ny | 09:00 America/New_York (NYMEX crude open) | 08:59 | 21:00 (US summer) / 22:00 (US winter) | 14:30 New York |

**Signal (owner swing adaptation):** the anchor candle's body (open/close) is the fair price. Inside the
setup window that starts at the session open, price must move at least `atr_mult` x ATR(14) of the previous
bar beyond the body. A long needs a lower swing high to form after a move down, then a close above that swing
high while still below the body ("MSS LONG"); a short is the mirror ("MSS SHORT"). At most one long and one
short signal per session day. Swing highs / lows follow only `indicators/structure_swings.pine`: one neighbour per side, left equality, right strictness, alternation and ordered outside candles. No swing setting is searched.

**Trade rules (ours, the indicator has none):**
- Entry: limit at the signal close, active from the next bar, only when flat.
- Stop: the excursion extreme, fixed at the signal bar (lowest low since the move down began for a long,
  highest high since the move up began for a short).
- Target (`target`): `near` = nearest body edge, `far` = far body edge (limit orders), `rr1` / `rr2` = 1R / 2R
  measured in ticks from the actual fill, where R = signal close to stop.
- Session end: any open position is closed at the next bar open after the flat time.

A runnable Pine v6 twin for checking trades in TradingView is in
[`strategies/fair_price_reversal.pine`](../../../strategies/fair_price_reversal.pine).

## Test settings (TradingView Properties)

| Setting | Value |
|---|---|
| Symbol | CL1! (NYMEX Light Crude Oil, front month), 1-minute bars |
| Data | 2010-06-07 00:00:00+00:00 to 2026-11-03 18:29:00+00:00 UTC, 5,674,164 bars (manifest written 2026-11-04T02:31:15+00:00) |
| Initial capital | 50,000.00 USD |
| Order size | 1 contract |
| Commission | 2.01 USD per contract per order (4.02 USD round trip) |
| Execution | Limit entries; commission included; no added slippage |
| Pyramiding | 0 (one position) |
| Fills | TradingView broker emulator, Bar Magnifier off, limits fill on touch |
| Roll rule | position closed at the last bar of a contract (exit reason `roll`) |

## How the top combination was chosen

Every variant ran all 64 combinations of the grid below with commission included. The combination with the highest **net profit** is the top combination (ties: higher profit factor, then grid order). This reference is retained for compatibility. Thirteen separate metric winners are also selected, with a declared minimum trade count; their values, settings and trade lists are linked below. No slippage stress runs are performed.

| Parameter | Values |
|---|---|
| `window` | 30, 60, 90, 120 |
| `atr_mult` | 0.5, 1.0, 1.5, 2.0 |
| `swing` | 1 |
| `target` | near, far, rr1, rr2 |

> **Read this first.** The top combination is the best of 64 tries on the same data it is reported on (in-sample). Picking the best of many tries makes the result look better than what the same rules can be expected to earn on new data. Treat these numbers as an upper bound, not as a forecast.

## Summary: top combination per variant

| Variant | Parameters | Net profit | Trades | % profitable | Profit factor | Max DD |
|---|---|---|---|---|---|---|
| asia | window=30, atr_mult=2.0, swing=1, target=rr2 | -6,418.68 USD | 1,634 | 32.50% | 0.948 | 11,406.78 USD |
| london | window=30, atr_mult=1.5, swing=1, target=rr2 | 11,712.66 USD | 1,967 | 35.18% | 1.071 | 7,901.56 USD |
| ny | window=120, atr_mult=0.5, swing=1, target=rr2 | 60,180.72 USD | 4,664 | 34.69% | 1.086 | 24,678.62 USD |

## Conclusion

Execution rules changed to limit entries at the decision close, with unfilled entries cancelled after the
planned target is reached at a one-minute close. Historical market-entry conclusions do not apply. Read
the newly generated tables as in-sample research; independent replication and TradingView comparison are
pending.

## Variant: asia

**Top combination:** `session=asia`, `window=30`, `atr_mult=2.0`, `swing=1`, `target=rr2`

![Equity curve](equity_asia.png)

Files: [grid](../../../results/fair_price_reversal/asia/grid.csv), [trades 0 ticks](../../../results/fair_price_reversal/asia/trades_slippage0.csv), [summary](../../../results/fair_price_reversal/asia/summary.json)

### Results after commission

#### Overview

| Metric | Value |
|---|---|
| Net profit | -6,418.68 USD (-12.84%) |
| Total closed trades | 1,634 |
| Percent profitable | 32.50% |
| Profit factor | 0.948 |
| Max equity drawdown | 11,406.78 USD (22.81%) |
| Avg trade | -3.93 USD |
| Avg # bars in trades | 47 |

#### Performance

| Metric | All | Long | Short |
|---|---|---|---|
| Net profit | -6,418.68 USD (-12.84%) | -236.50 USD (-0.47%) | -6,182.18 USD (-12.36%) |
| Gross profit | 117,845.38 USD (235.69%) | 64,230.58 USD (128.46%) | 53,614.80 USD (107.23%) |
| Gross loss | 124,264.06 USD (248.53%) | 64,467.08 USD (128.93%) | 59,796.98 USD (119.59%) |
| Commission paid | 6,568.68 USD | 3,316.50 USD | 3,252.18 USD |

| Account | Value |
|---|---|
| Initial capital | 50,000.00 USD |
| Buy & hold return (TV-style, all capital at the first entry) | 18,904.01 USD (37.81%) |
| Max equity run-up (intrabar) | 11,316.06 USD (22.63%) |
| Max equity drawdown (intrabar) | 11,406.78 USD (22.81%) |
| Open P&L | 0.00 USD |
| Max contracts held | 1 |

#### Trades analysis

| Metric | All | Long | Short |
|---|---|---|---|
| Total closed trades | 1,634 | 825 | 809 |
| Winning trades | 531 | 271 | 260 |
| Losing trades | 1,103 | 554 | 549 |
| Even trades | 0 | 0 | 0 |
| Percent profitable | 32.50% | 32.85% | 32.14% |
| Avg P&L | -3.93 USD | -0.29 USD | -7.64 USD |
| Avg P&L % | -0.00% | 0.00% | -0.01% |
| Avg winning trade | 221.93 USD | 237.01 USD | 206.21 USD |
| Avg losing trade | 112.66 USD | 116.37 USD | 108.92 USD |
| Ratio avg win / avg loss | 1.970 | 2.037 | 1.893 |
| Largest winning trade | 2,655.98 USD | 2,655.98 USD | 955.98 USD |
| Largest winning trade % | 3.02% | 3.02% | 2.14% |
| Largest losing trade | 1,794.02 USD | 1,794.02 USD | 694.02 USD |
| Largest losing trade % | 2.08% | 2.08% | 1.80% |
| Avg # bars in trades | 47 | 47 | 47 |
| Avg # bars in winning trades | 68 | 72 | 64 |
| Avg # bars in losing trades | 37 | 34 | 39 |

#### Risk/performance ratios

| Metric | Value |
|---|---|
| Sharpe ratio | -0.204 |
| Sortino ratio | -0.265 |
| Profit factor | 0.948 |
| Margin calls | 0 |

#### List of trades (last 10, newest first; full list in the trades CSV)

| Trade # | Type | Signal | Date/Time (UTC) | Price | Contracts | Profit | Cum. profit | Run-up | Drawdown |
|---|---|---|---|---|---|---|---|---|---|
| 1634 | Exit short | Exit | 2026-11-03 05:35 | 97.15 | 1 | -494.02 USD (-0.51%) | -6,418.68 USD | 540.00 USD | 490.00 USD |
|  | Entry short | Short | 2026-11-03 01:24 | 96.66 | 1 |  |  |  |  |
| 1633 | Exit short | Exit | 2026-10-28 01:55 | 101.32 | 1 | -424.02 USD (-0.42%) | -5,924.66 USD | 100.00 USD | 420.00 USD |
|  | Entry short | Short | 2026-10-28 01:19 | 100.90 | 1 |  |  |  |  |
| 1632 | Exit long | Exit | 2026-10-27 01:33 | 100.87 | 1 | -144.02 USD (-0.14%) | -5,500.64 USD | 150.00 USD | 140.00 USD |
|  | Entry long | Long | 2026-10-27 01:19 | 101.01 | 1 |  |  |  |  |
| 1631 | Exit short | Exit | 2026-10-23 01:52 | 100.24 | 1 | -444.02 USD (-0.44%) | -5,356.62 USD | 180.00 USD | 440.00 USD |
|  | Entry short | Short | 2026-10-23 01:12 | 99.80 | 1 |  |  |  |  |
| 1630 | Exit short | Exit | 2026-10-21 02:00 | 99.09 | 1 | -244.02 USD (-0.25%) | -4,912.60 USD | 120.00 USD | 240.00 USD |
|  | Entry short | Short | 2026-10-21 01:11 | 98.85 | 1 |  |  |  |  |
| 1629 | Exit long | Exit | 2026-10-16 01:34 | 97.59 | 1 | 255.98 USD (0.26%) | -4,668.58 USD | 260.00 USD | 80.00 USD |
|  | Entry long | Long | 2026-10-16 01:11 | 97.33 | 1 |  |  |  |  |
| 1628 | Exit long | Exit | 2026-10-15 01:51 | 93.90 | 1 | -184.02 USD (-0.20%) | -4,924.56 USD | 260.00 USD | 180.00 USD |
|  | Entry long | Long | 2026-10-15 01:26 | 94.08 | 1 |  |  |  |  |
| 1627 | Exit short | Exit | 2026-10-14 01:42 | 95.40 | 1 | -114.02 USD (-0.12%) | -4,740.54 USD | 120.00 USD | 110.00 USD |
|  | Entry short | Short | 2026-10-14 01:24 | 95.29 | 1 |  |  |  |  |
| 1626 | Exit long | Exit | 2026-10-13 01:54 | 92.65 | 1 | -234.02 USD (-0.25%) | -4,626.52 USD | 70.00 USD | 230.00 USD |
|  | Entry long | Long | 2026-10-13 01:24 | 92.88 | 1 |  |  |  |  |
| 1625 | Exit long | Exit | 2026-10-12 05:31 | 90.78 | 1 | 775.98 USD (0.86%) | -4,392.50 USD | 780.00 USD | 170.00 USD |
|  | Entry long | Long | 2026-10-12 01:10 | 90.00 | 1 |  |  |  |  |

#### By year (extra, not a TV tab)

| Year | Trades | Net profit | % profitable | Profit factor |
|---|---|---|---|---|
| 2010 | 49 | 53.02 USD | 36.73% | 1.022 |
| 2011 | 119 | -2,528.38 USD | 31.93% | 0.746 |
| 2012 | 95 | -501.90 USD | 29.47% | 0.912 |
| 2013 | 81 | -1,255.62 USD | 32.10% | 0.705 |
| 2014 | 63 | 826.74 USD | 38.10% | 1.335 |
| 2015 | 78 | -493.56 USD | 28.21% | 0.866 |
| 2016 | 67 | 850.66 USD | 40.30% | 1.333 |
| 2017 | 53 | -1,863.06 USD | 11.32% | 0.214 |
| 2018 | 88 | -83.76 USD | 32.95% | 0.981 |
| 2019 | 96 | -975.92 USD | 29.17% | 0.821 |
| 2020 | 119 | 2,891.62 USD | 40.34% | 1.354 |
| 2021 | 120 | 597.60 USD | 33.33% | 1.065 |
| 2022 | 152 | 1,578.96 USD | 34.87% | 1.071 |
| 2023 | 130 | -472.60 USD | 31.54% | 0.951 |
| 2024 | 109 | -98.18 USD | 33.94% | 0.986 |
| 2025 | 102 | -320.04 USD | 31.37% | 0.951 |
| 2026 | 113 | -4,624.26 USD | 30.09% | 0.751 |

#### Exit reasons (extra)

| Reason | Trades |
|---|---|
| stop | 1090 |
| limit | 496 |
| close | 48 |

- Session-end exits more than 5 minutes after the flat time (missing bars / early closes): 1.
- Roll exits: 0.

### Best settings by metric

Each winner needs at least 30 closed trades. Undefined values are excluded. Ties: higher net profit, higher profit factor, then grid order. Ruin loss threshold: 25,000.00 USD from starting capital. All selections are in-sample. MAE/MFE objectives use the mean of the per-trade maxima.

| Metric | Goal | Best value | Grid order | Trades | Eligible settings | Parameters |
|---|---|---|---|---|---|---|
| Net profit | max | -6,418.68 USD | [16](../../../results/fair_price_reversal/asia/metric_winners/order_16/trades_slippage0.csv) | 1634 | 64 | window=30, atr_mult=2.0, swing=1, target=rr2 |
| Win rate | max | 54.45% | [1](../../../results/fair_price_reversal/asia/metric_winners/order_1/trades_slippage0.csv) | 1315 | 64 | window=30, atr_mult=0.5, swing=1, target=near |
| Expectancy | max | -3.93 USD | [16](../../../results/fair_price_reversal/asia/metric_winners/order_16/trades_slippage0.csv) | 1634 | 64 | window=30, atr_mult=2.0, swing=1, target=rr2 |
| Profit factor | max | 0.948 | [16](../../../results/fair_price_reversal/asia/metric_winners/order_16/trades_slippage0.csv) | 1634 | 64 | window=30, atr_mult=2.0, swing=1, target=rr2 |
| Payoff ratio | max | 1.970 | [16](../../../results/fair_price_reversal/asia/metric_winners/order_16/trades_slippage0.csv) | 1634 | 64 | window=30, atr_mult=2.0, swing=1, target=rr2 |
| Risk of ruin (estimate) | min | 100.00% | [16](../../../results/fair_price_reversal/asia/metric_winners/order_16/trades_slippage0.csv) | 1634 | 64 | window=30, atr_mult=2.0, swing=1, target=rr2 |
| Maximum drawdown | min | 9,012.36 USD | [14](../../../results/fair_price_reversal/asia/metric_winners/order_14/trades_slippage0.csv) | 1597 | 64 | window=30, atr_mult=2.0, swing=1, target=far |
| Consecutive losses | min | 7.000 | [1](../../../results/fair_price_reversal/asia/metric_winners/order_1/trades_slippage0.csv) | 1315 | 64 | window=30, atr_mult=0.5, swing=1, target=near |
| Sharpe ratio | max | -0.150 | [56](../../../results/fair_price_reversal/asia/metric_winners/order_56/trades_slippage0.csv) | 4156 | 64 | window=120, atr_mult=1.0, swing=1, target=rr2 |
| Sortino ratio | max | -0.203 | [52](../../../results/fair_price_reversal/asia/metric_winners/order_52/trades_slippage0.csv) | 3771 | 64 | window=120, atr_mult=0.5, swing=1, target=rr2 |
| R-multiple | max | No eligible value | — | — | 0 | — |
| Maximum adverse excursion (MAE) | min | 64.49 USD | [53](../../../results/fair_price_reversal/asia/metric_winners/order_53/trades_slippage0.csv) | 4213 | 64 | window=120, atr_mult=1.0, swing=1, target=near |
| Maximum favorable excursion (MFE) | max | 119.70 USD | [16](../../../results/fair_price_reversal/asia/metric_winners/order_16/trades_slippage0.csv) | 1634 | 64 | window=30, atr_mult=2.0, swing=1, target=rr2 |

- **Net profit:** Sum of closed-trade profit after commission; excludes open P&L.
- **Win rate:** Winning closed trades divided by all closed trades, including breakevens.
- **Expectancy:** Mean net profit per closed trade, including losses and breakevens.
- **Profit factor:** Gross winning profit divided by gross losing profit, both after commission. Undefined without losses.
- **Payoff ratio:** Average net winning trade divided by the absolute average net losing trade. Requires wins and losses.
- **Risk of ruin (estimate):** Infinite-horizon diffusion estimate of losing the declared amount from starting capital. Assumes independent, stationary, fixed-size net trade P&L; ignores intratrade losses and margin.
- **Maximum drawdown:** Largest equity drawdown under the tester's intrabar TradingView convention, including an open trade at the end.
- **Consecutive losses:** Longest streak of losing closed trades in execution order. A win or breakeven resets the streak.
- **Sharpe ratio:** Monthly marked-to-market excess return divided by population standard deviation, using 2% annual risk-free rate; not annualized.
- **Sortino ratio:** Monthly marked-to-market excess return divided by downside deviation about the risk-free rate; not annualized.
- **R-multiple:** Mean net trade profit / initial stop risk in dollars. Risk is actual fill to initial stop, before costs. Requires positive initial risk for every closed trade; R standard deviation and mean / standard deviation describe consistency.
- **Maximum adverse excursion (MAE):** Mean of each closed trade's maximum adverse price excursion in dollars, before commission; only the exposed intrabar path counts.
- **Maximum favorable excursion (MFE):** Mean of each closed trade's maximum favorable price excursion in dollars, before commission; only the exposed intrabar path counts. Unrealized opportunity, not realized profit.

Full selection metadata: [metric_winners.json](../../../results/fair_price_reversal/asia/metric_winners.json).

### Top 10 combinations

| # | window | atr_mult | swing | target | Net profit | Trades | % profitable | Profit factor | Max DD |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 30 | 2.0 | 1 | rr2 | -6,418.68 USD | 1,634 | 32.50% | 0.948 | 11,406.78 USD |
| 2 | 30 | 2.0 | 1 | far | -8,139.94 USD | 1,597 | 49.59% | 0.908 | 9,012.36 USD |
| 3 | 30 | 2.0 | 1 | rr1 | -8,262.30 USD | 1,615 | 47.80% | 0.914 | 9,739.44 USD |
| 4 | 30 | 2.0 | 1 | near | -8,945.82 USD | 1,591 | 53.61% | 0.889 | 9,431.30 USD |
| 5 | 30 | 1.0 | 1 | rr2 | -8,983.56 USD | 1,578 | 32.00% | 0.924 | 13,697.94 USD |
| 6 | 30 | 0.5 | 1 | far | -10,298.46 USD | 1,323 | 49.43% | 0.862 | 11,194.90 USD |
| 7 | 30 | 0.5 | 1 | rr1 | -10,444.74 USD | 1,337 | 47.79% | 0.872 | 11,705.90 USD |
| 8 | 30 | 0.5 | 1 | near | -10,746.30 USD | 1,315 | 54.45% | 0.839 | 11,258.12 USD |
| 9 | 30 | 1.0 | 1 | far | -10,908.84 USD | 1,542 | 49.74% | 0.871 | 11,919.20 USD |
| 10 | 30 | 0.5 | 1 | rr2 | -10,947.00 USD | 1,350 | 31.93% | 0.895 | 13,056.44 USD |

Profitable combinations: 0 of 64.

## Variant: london

**Top combination:** `session=london`, `window=30`, `atr_mult=1.5`, `swing=1`, `target=rr2`

![Equity curve](equity_london.png)

Files: [grid](../../../results/fair_price_reversal/london/grid.csv), [trades 0 ticks](../../../results/fair_price_reversal/london/trades_slippage0.csv), [summary](../../../results/fair_price_reversal/london/summary.json)

### Results after commission

#### Overview

| Metric | Value |
|---|---|
| Net profit | 11,712.66 USD (23.43%) |
| Total closed trades | 1,967 |
| Percent profitable | 35.18% |
| Profit factor | 1.071 |
| Max equity drawdown | 7,901.56 USD (15.80%) |
| Avg trade | 5.95 USD |
| Avg # bars in trades | 28 |

#### Performance

| Metric | All | Long | Short |
|---|---|---|---|
| Net profit | 11,712.66 USD (23.43%) | 7,209.30 USD (14.42%) | 4,503.36 USD (9.01%) |
| Gross profit | 176,408.16 USD (352.82%) | 92,664.86 USD (185.33%) | 83,743.30 USD (167.49%) |
| Gross loss | 164,695.50 USD (329.39%) | 85,455.56 USD (170.91%) | 79,239.94 USD (158.48%) |
| Commission paid | 7,907.34 USD | 4,160.70 USD | 3,746.64 USD |

| Account | Value |
|---|---|
| Initial capital | 50,000.00 USD |
| Buy & hold return (TV-style, all capital at the first entry) | 18,094.29 USD (36.19%) |
| Max equity run-up (intrabar) | 15,824.06 USD (31.65%) |
| Max equity drawdown (intrabar) | 7,901.56 USD (15.80%) |
| Open P&L | 0.00 USD |
| Max contracts held | 1 |

#### Trades analysis

| Metric | All | Long | Short |
|---|---|---|---|
| Total closed trades | 1,967 | 1,035 | 932 |
| Winning trades | 692 | 357 | 335 |
| Losing trades | 1,275 | 678 | 597 |
| Even trades | 0 | 0 | 0 |
| Percent profitable | 35.18% | 34.49% | 35.94% |
| Avg P&L | 5.95 USD | 6.97 USD | 4.83 USD |
| Avg P&L % | 0.01% | 0.01% | 0.00% |
| Avg winning trade | 254.93 USD | 259.57 USD | 249.98 USD |
| Avg losing trade | 129.17 USD | 126.04 USD | 132.73 USD |
| Ratio avg win / avg loss | 1.974 | 2.059 | 1.883 |
| Largest winning trade | 1,935.98 USD | 1,935.98 USD | 1,135.98 USD |
| Largest winning trade % | 4.48% | 4.48% | 1.53% |
| Largest losing trade | 1,264.02 USD | 1,264.02 USD | 574.02 USD |
| Largest losing trade % | 2.19% | 1.23% | 2.19% |
| Avg # bars in trades | 28 | 29 | 27 |
| Avg # bars in winning trades | 40 | 43 | 36 |
| Avg # bars in losing trades | 21 | 21 | 22 |

#### Risk/performance ratios

| Metric | Value |
|---|---|
| Sharpe ratio | -0.037 |
| Sortino ratio | -0.053 |
| Profit factor | 1.071 |
| Margin calls | 0 |

#### List of trades (last 10, newest first; full list in the trades CSV)

| Trade # | Type | Signal | Date/Time (UTC) | Price | Contracts | Profit | Cum. profit | Run-up | Drawdown |
|---|---|---|---|---|---|---|---|---|---|
| 1967 | Exit long | Exit | 2026-10-30 09:06 | 103.42 | 1 | -304.02 USD (-0.29%) | 11,712.66 USD | 250.00 USD | 300.00 USD |
|  | Entry long | Long | 2026-10-30 08:30 | 103.72 | 1 |  |  |  |  |
| 1966 | Exit long | Exit | 2026-10-28 08:28 | 101.20 | 1 | -244.02 USD (-0.24%) | 12,016.68 USD | 30.00 USD | 240.00 USD |
|  | Entry long | Long | 2026-10-28 08:22 | 101.44 | 1 |  |  |  |  |
| 1965 | Exit long | Exit | 2026-10-26 08:15 | 101.10 | 1 | -154.02 USD (-0.15%) | 12,260.70 USD | 0.00 USD | 150.00 USD |
|  | Entry long | Long | 2026-10-26 08:14 | 101.25 | 1 |  |  |  |  |
| 1964 | Exit short | Exit | 2026-10-22 07:17 | 99.60 | 1 | -214.02 USD (-0.22%) | 12,414.72 USD | 120.00 USD | 210.00 USD |
|  | Entry short | Short | 2026-10-22 07:09 | 99.39 | 1 |  |  |  |  |
| 1963 | Exit short | Exit | 2026-10-19 08:30 | 97.12 | 1 | -154.02 USD (-0.16%) | 12,628.74 USD | 250.00 USD | 150.00 USD |
|  | Entry short | Short | 2026-10-19 07:27 | 96.97 | 1 |  |  |  |  |
| 1962 | Exit long | Exit | 2026-10-12 07:38 | 90.84 | 1 | -234.02 USD (-0.26%) | 12,782.76 USD | 440.00 USD | 230.00 USD |
|  | Entry long | Long | 2026-10-12 07:08 | 91.07 | 1 |  |  |  |  |
| 1961 | Exit short | Exit | 2026-10-08 07:30 | 91.47 | 1 | -254.02 USD (-0.28%) | 13,016.78 USD | 20.00 USD | 250.00 USD |
|  | Entry short | Short | 2026-10-08 07:17 | 91.22 | 1 |  |  |  |  |
| 1960 | Exit long | Exit | 2026-10-07 07:33 | 89.74 | 1 | -184.02 USD (-0.20%) | 13,270.80 USD | 100.00 USD | 180.00 USD |
|  | Entry long | Long | 2026-10-07 07:16 | 89.92 | 1 |  |  |  |  |
| 1959 | Exit long | Exit | 2026-10-05 07:26 | 89.83 | 1 | -154.02 USD (-0.17%) | 13,454.82 USD | 20.00 USD | 150.00 USD |
|  | Entry long | Long | 2026-10-05 07:25 | 89.98 | 1 |  |  |  |  |
| 1958 | Exit long | Exit | 2026-09-23 07:24 | 90.01 | 1 | 535.98 USD (0.60%) | 13,608.84 USD | 540.00 USD | 50.00 USD |
|  | Entry long | Long | 2026-09-23 07:10 | 89.47 | 1 |  |  |  |  |

#### By year (extra, not a TV tab)

| Year | Trades | Net profit | % profitable | Profit factor |
|---|---|---|---|---|
| 2010 | 70 | 1,348.60 USD | 37.14% | 1.274 |
| 2011 | 152 | 878.96 USD | 35.53% | 1.054 |
| 2012 | 137 | 3,029.26 USD | 39.42% | 1.286 |
| 2013 | 117 | 4,289.66 USD | 47.01% | 1.711 |
| 2014 | 102 | 1,819.96 USD | 36.27% | 1.315 |
| 2015 | 136 | 733.28 USD | 33.82% | 1.082 |
| 2016 | 121 | 823.58 USD | 36.36% | 1.113 |
| 2017 | 108 | 745.84 USD | 34.26% | 1.146 |
| 2018 | 101 | -3,056.02 USD | 23.76% | 0.570 |
| 2019 | 80 | 1,228.40 USD | 38.75% | 1.307 |
| 2020 | 108 | 975.84 USD | 35.19% | 1.123 |
| 2021 | 120 | -1,202.40 USD | 33.33% | 0.882 |
| 2022 | 144 | -2,108.88 USD | 32.64% | 0.914 |
| 2023 | 139 | 1,731.22 USD | 38.13% | 1.140 |
| 2024 | 114 | 181.72 USD | 34.21% | 1.024 |
| 2025 | 115 | -572.30 USD | 29.57% | 0.938 |
| 2026 | 103 | 865.94 USD | 32.04% | 1.051 |

#### Exit reasons (extra)

| Reason | Trades |
|---|---|
| stop | 1272 |
| limit | 683 |
| close | 12 |

- Session-end exits more than 5 minutes after the flat time (missing bars / early closes): 0.
- Roll exits: 0.

### Best settings by metric

Each winner needs at least 30 closed trades. Undefined values are excluded. Ties: higher net profit, higher profit factor, then grid order. Ruin loss threshold: 25,000.00 USD from starting capital. All selections are in-sample. MAE/MFE objectives use the mean of the per-trade maxima.

| Metric | Goal | Best value | Grid order | Trades | Eligible settings | Parameters |
|---|---|---|---|---|---|---|
| Net profit | max | 11,712.66 USD | [12](../../../results/fair_price_reversal/london/metric_winners/order_12/trades_slippage0.csv) | 1967 | 64 | window=30, atr_mult=1.5, swing=1, target=rr2 |
| Win rate | max | 59.66% | [9](../../../results/fair_price_reversal/london/metric_winners/order_9/trades_slippage0.csv) | 1956 | 64 | window=30, atr_mult=1.5, swing=1, target=near |
| Expectancy | max | 5.95 USD | [12](../../../results/fair_price_reversal/london/metric_winners/order_12/trades_slippage0.csv) | 1967 | 64 | window=30, atr_mult=1.5, swing=1, target=rr2 |
| Profit factor | max | 1.071 | [12](../../../results/fair_price_reversal/london/metric_winners/order_12/trades_slippage0.csv) | 1967 | 64 | window=30, atr_mult=1.5, swing=1, target=rr2 |
| Payoff ratio | max | 2.003 | [4](../../../results/fair_price_reversal/london/metric_winners/order_4/trades_slippage0.csv) | 1754 | 64 | window=30, atr_mult=0.5, swing=1, target=rr2 |
| Risk of ruin (estimate) | min | 0.19% | [11](../../../results/fair_price_reversal/london/metric_winners/order_11/trades_slippage0.csv) | 1965 | 64 | window=30, atr_mult=1.5, swing=1, target=rr1 |
| Maximum drawdown | min | 3,631.72 USD | [1](../../../results/fair_price_reversal/london/metric_winners/order_1/trades_slippage0.csv) | 1743 | 64 | window=30, atr_mult=0.5, swing=1, target=near |
| Consecutive losses | min | 6.000 | [1](../../../results/fair_price_reversal/london/metric_winners/order_1/trades_slippage0.csv) | 1743 | 64 | window=30, atr_mult=0.5, swing=1, target=near |
| Sharpe ratio | max | -0.037 | [12](../../../results/fair_price_reversal/london/metric_winners/order_12/trades_slippage0.csv) | 1967 | 64 | window=30, atr_mult=1.5, swing=1, target=rr2 |
| Sortino ratio | max | -0.053 | [12](../../../results/fair_price_reversal/london/metric_winners/order_12/trades_slippage0.csv) | 1967 | 64 | window=30, atr_mult=1.5, swing=1, target=rr2 |
| R-multiple | max | No eligible value | — | — | 0 | — |
| Maximum adverse excursion (MAE) | min | 70.44 USD | [9](../../../results/fair_price_reversal/london/metric_winners/order_9/trades_slippage0.csv) | 1956 | 64 | window=30, atr_mult=1.5, swing=1, target=near |
| Maximum favorable excursion (MFE) | max | 152.47 USD | [64](../../../results/fair_price_reversal/london/metric_winners/order_64/trades_slippage0.csv) | 4928 | 64 | window=120, atr_mult=2.0, swing=1, target=rr2 |

- **Net profit:** Sum of closed-trade profit after commission; excludes open P&L.
- **Win rate:** Winning closed trades divided by all closed trades, including breakevens.
- **Expectancy:** Mean net profit per closed trade, including losses and breakevens.
- **Profit factor:** Gross winning profit divided by gross losing profit, both after commission. Undefined without losses.
- **Payoff ratio:** Average net winning trade divided by the absolute average net losing trade. Requires wins and losses.
- **Risk of ruin (estimate):** Infinite-horizon diffusion estimate of losing the declared amount from starting capital. Assumes independent, stationary, fixed-size net trade P&L; ignores intratrade losses and margin.
- **Maximum drawdown:** Largest equity drawdown under the tester's intrabar TradingView convention, including an open trade at the end.
- **Consecutive losses:** Longest streak of losing closed trades in execution order. A win or breakeven resets the streak.
- **Sharpe ratio:** Monthly marked-to-market excess return divided by population standard deviation, using 2% annual risk-free rate; not annualized.
- **Sortino ratio:** Monthly marked-to-market excess return divided by downside deviation about the risk-free rate; not annualized.
- **R-multiple:** Mean net trade profit / initial stop risk in dollars. Risk is actual fill to initial stop, before costs. Requires positive initial risk for every closed trade; R standard deviation and mean / standard deviation describe consistency.
- **Maximum adverse excursion (MAE):** Mean of each closed trade's maximum adverse price excursion in dollars, before commission; only the exposed intrabar path counts.
- **Maximum favorable excursion (MFE):** Mean of each closed trade's maximum favorable price excursion in dollars, before commission; only the exposed intrabar path counts. Unrealized opportunity, not realized profit.

Full selection metadata: [metric_winners.json](../../../results/fair_price_reversal/london/metric_winners.json).

### Top 10 combinations

| # | window | atr_mult | swing | target | Net profit | Trades | % profitable | Profit factor | Max DD |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 30 | 1.5 | 1 | rr2 | 11,712.66 USD | 1,967 | 35.18% | 1.071 | 7,901.56 USD |
| 2 | 30 | 2.0 | 1 | rr2 | 10,439.04 USD | 1,948 | 35.01% | 1.064 | 8,457.44 USD |
| 3 | 30 | 0.5 | 1 | rr2 | 10,418.92 USD | 1,754 | 34.83% | 1.071 | 8,204.58 USD |
| 4 | 30 | 1.0 | 1 | rr2 | 10,285.32 USD | 1,934 | 34.90% | 1.063 | 8,485.38 USD |
| 5 | 30 | 1.5 | 1 | rr1 | 5,970.70 USD | 1,965 | 51.81% | 1.049 | 7,193.66 USD |
| 6 | 30 | 2.0 | 1 | rr1 | 5,519.14 USD | 1,943 | 51.57% | 1.045 | 7,431.50 USD |
| 7 | 30 | 1.0 | 1 | rr1 | 4,985.32 USD | 1,934 | 51.50% | 1.041 | 8,065.42 USD |
| 8 | 30 | 0.5 | 1 | near | 3,913.14 USD | 1,743 | 59.38% | 1.046 | 3,631.72 USD |
| 9 | 30 | 1.5 | 1 | near | 3,236.88 USD | 1,956 | 59.66% | 1.034 | 4,634.68 USD |
| 10 | 30 | 2.0 | 1 | near | 3,011.30 USD | 1,935 | 59.22% | 1.032 | 4,828.60 USD |

Profitable combinations: 19 of 64.

## Variant: ny

**Top combination:** `session=ny`, `window=120`, `atr_mult=0.5`, `swing=1`, `target=rr2`

![Equity curve](equity_ny.png)

Files: [grid](../../../results/fair_price_reversal/ny/grid.csv), [trades 0 ticks](../../../results/fair_price_reversal/ny/trades_slippage0.csv), [summary](../../../results/fair_price_reversal/ny/summary.json)

### Results after commission

#### Overview

| Metric | Value |
|---|---|
| Net profit | 60,180.72 USD (120.36%) |
| Total closed trades | 4,664 |
| Percent profitable | 34.69% |
| Profit factor | 1.086 |
| Max equity drawdown | 24,678.62 USD (49.36%) |
| Avg trade | 12.90 USD |
| Avg # bars in trades | 37 |

#### Performance

| Metric | All | Long | Short |
|---|---|---|---|
| Net profit | 60,180.72 USD (120.36%) | 33,128.38 USD (66.26%) | 27,052.34 USD (54.10%) |
| Gross profit | 761,075.64 USD (1,522.15%) | 402,165.46 USD (804.33%) | 358,910.18 USD (717.82%) |
| Gross loss | 700,894.92 USD (1,401.79%) | 369,037.08 USD (738.07%) | 331,857.84 USD (663.72%) |
| Commission paid | 18,749.28 USD | 9,571.62 USD | 9,177.66 USD |

| Account | Value |
|---|---|
| Initial capital | 50,000.00 USD |
| Buy & hold return (TV-style, all capital at the first entry) | 17,190.56 USD (34.38%) |
| Max equity run-up (intrabar) | 72,239.48 USD (144.48%) |
| Max equity drawdown (intrabar) | 24,678.62 USD (49.36%) |
| Open P&L | 0.00 USD |
| Max contracts held | 1 |

#### Trades analysis

| Metric | All | Long | Short |
|---|---|---|---|
| Total closed trades | 4,664 | 2,381 | 2,283 |
| Winning trades | 1,618 | 827 | 791 |
| Losing trades | 3,046 | 1,554 | 1,492 |
| Even trades | 0 | 0 | 0 |
| Percent profitable | 34.69% | 34.73% | 34.65% |
| Avg P&L | 12.90 USD | 13.91 USD | 11.85 USD |
| Avg P&L % | 0.02% | 0.03% | 0.01% |
| Avg winning trade | 470.38 USD | 486.29 USD | 453.74 USD |
| Avg losing trade | 230.10 USD | 237.48 USD | 222.42 USD |
| Ratio avg win / avg loss | 2.044 | 2.048 | 2.040 |
| Largest winning trade | 4,195.98 USD | 3,135.98 USD | 4,195.98 USD |
| Largest winning trade % | 8.62% | 8.62% | 7.23% |
| Largest losing trade | 1,854.02 USD | 1,854.02 USD | 1,264.02 USD |
| Largest losing trade % | 4.38% | 2.54% | 4.38% |
| Avg # bars in trades | 37 | 38 | 36 |
| Avg # bars in winning trades | 57 | 61 | 52 |
| Avg # bars in losing trades | 27 | 26 | 28 |

#### Risk/performance ratios

| Metric | Value |
|---|---|
| Sharpe ratio | 0.098 |
| Sortino ratio | 0.173 |
| Profit factor | 1.086 |
| Margin calls | 0 |

#### List of trades (last 10, newest first; full list in the trades CSV)

| Trade # | Type | Signal | Date/Time (UTC) | Price | Contracts | Profit | Cum. profit | Run-up | Drawdown |
|---|---|---|---|---|---|---|---|---|---|
| 4664 | Exit short | Exit | 2026-11-03 14:24 | 95.85 | 1 | -374.02 USD (-0.39%) | 60,180.72 USD | 220.00 USD | 370.00 USD |
|  | Entry short | Short | 2026-11-03 14:14 | 95.48 | 1 |  |  |  |  |
| 4663 | Exit long | Exit | 2026-11-02 14:30 | 97.30 | 1 | -234.02 USD (-0.24%) | 60,554.74 USD | 350.00 USD | 230.00 USD |
|  | Entry long | Long | 2026-11-02 14:21 | 97.53 | 1 |  |  |  |  |
| 4662 | Exit short | Exit | 2026-10-30 15:05 | 103.99 | 1 | 435.98 USD (0.42%) | 60,788.76 USD | 440.00 USD | 120.00 USD |
|  | Entry short | Short | 2026-10-30 14:26 | 104.43 | 1 |  |  |  |  |
| 4661 | Exit long | Exit | 2026-10-29 14:04 | 100.93 | 1 | 755.98 USD (0.75%) | 60,352.78 USD | 760.00 USD | 10.00 USD |
|  | Entry long | Long | 2026-10-29 13:53 | 100.17 | 1 |  |  |  |  |
| 4660 | Exit short | Exit | 2026-10-28 14:40 | 102.46 | 1 | -204.02 USD (-0.20%) | 59,596.80 USD | 100.00 USD | 200.00 USD |
|  | Entry short | Short | 2026-10-28 14:31 | 102.26 | 1 |  |  |  |  |
| 4659 | Exit long | Exit | 2026-10-27 14:50 | 100.08 | 1 | -444.02 USD (-0.44%) | 59,800.82 USD | 190.00 USD | 440.00 USD |
|  | Entry long | Long | 2026-10-27 14:46 | 100.52 | 1 |  |  |  |  |
| 4658 | Exit short | Exit | 2026-10-27 14:25 | 100.87 | 1 | 695.98 USD (0.69%) | 60,244.84 USD | 700.00 USD | 0.00 USD |
|  | Entry short | Short | 2026-10-27 14:10 | 101.57 | 1 |  |  |  |  |
| 4657 | Exit long | Exit | 2026-10-26 15:20 | 101.65 | 1 | 875.98 USD (0.87%) | 59,548.86 USD | 880.00 USD | 0.00 USD |
|  | Entry long | Long | 2026-10-26 14:44 | 100.77 | 1 |  |  |  |  |
| 4656 | Exit short | Exit | 2026-10-26 14:15 | 100.75 | 1 | 955.98 USD (0.94%) | 58,672.88 USD | 960.00 USD | 210.00 USD |
|  | Entry short | Short | 2026-10-26 13:21 | 101.71 | 1 |  |  |  |  |
| 4655 | Exit long | Exit | 2026-10-22 14:40 | 98.26 | 1 | -334.02 USD (-0.34%) | 57,716.90 USD | 70.00 USD | 330.00 USD |
|  | Entry long | Long | 2026-10-22 14:37 | 98.59 | 1 |  |  |  |  |

#### By year (extra, not a TV tab)

| Year | Trades | Net profit | % profitable | Profit factor |
|---|---|---|---|---|
| 2010 | 155 | 6,576.90 USD | 40.00% | 1.254 |
| 2011 | 278 | 7,222.44 USD | 34.89% | 1.119 |
| 2012 | 290 | 8,214.20 USD | 36.55% | 1.176 |
| 2013 | 261 | 8,640.78 USD | 36.78% | 1.238 |
| 2014 | 252 | -5,223.04 USD | 29.76% | 0.847 |
| 2015 | 293 | -8,267.86 USD | 29.69% | 0.818 |
| 2016 | 294 | -1,811.88 USD | 32.31% | 0.941 |
| 2017 | 278 | 12.44 USD | 33.09% | 1.001 |
| 2018 | 301 | -5,680.02 USD | 30.23% | 0.840 |
| 2019 | 285 | 2,264.30 USD | 37.54% | 1.072 |
| 2020 | 279 | 7,558.42 USD | 37.28% | 1.232 |
| 2021 | 296 | 18,730.08 USD | 40.20% | 1.506 |
| 2022 | 287 | 13,246.26 USD | 36.93% | 1.171 |
| 2023 | 300 | 17,674.00 USD | 40.33% | 1.369 |
| 2024 | 290 | -7,655.80 USD | 30.69% | 0.827 |
| 2025 | 284 | 4,948.32 USD | 34.51% | 1.148 |
| 2026 | 241 | -6,268.82 USD | 30.29% | 0.895 |

#### Exit reasons (extra)

| Reason | Trades |
|---|---|
| stop | 3029 |
| limit | 1522 |
| close | 113 |

- Session-end exits more than 5 minutes after the flat time (missing bars / early closes): 3.
- Roll exits: 0.

### Best settings by metric

Each winner needs at least 30 closed trades. Undefined values are excluded. Ties: higher net profit, higher profit factor, then grid order. Ruin loss threshold: 25,000.00 USD from starting capital. All selections are in-sample. MAE/MFE objectives use the mean of the per-trade maxima.

| Metric | Goal | Best value | Grid order | Trades | Eligible settings | Parameters |
|---|---|---|---|---|---|---|
| Net profit | max | 60,180.72 USD | [52](../../../results/fair_price_reversal/ny/metric_winners/order_52/trades_slippage0.csv) | 4664 | 64 | window=120, atr_mult=0.5, swing=1, target=rr2 |
| Win rate | max | 58.66% | [1](../../../results/fair_price_reversal/ny/metric_winners/order_1/trades_slippage0.csv) | 1841 | 64 | window=30, atr_mult=0.5, swing=1, target=near |
| Expectancy | max | 13.65 USD | [36](../../../results/fair_price_reversal/ny/metric_winners/order_36/trades_slippage0.csv) | 4127 | 64 | window=90, atr_mult=0.5, swing=1, target=rr2 |
| Profit factor | max | 1.091 | [36](../../../results/fair_price_reversal/ny/metric_winners/order_36/trades_slippage0.csv) | 4127 | 64 | window=90, atr_mult=0.5, swing=1, target=rr2 |
| Payoff ratio | max | 2.079 | [16](../../../results/fair_price_reversal/ny/metric_winners/order_16/trades_slippage0.csv) | 2001 | 64 | window=30, atr_mult=2.0, swing=1, target=rr2 |
| Risk of ruin (estimate) | min | 1.37% | [36](../../../results/fair_price_reversal/ny/metric_winners/order_36/trades_slippage0.csv) | 4127 | 64 | window=90, atr_mult=0.5, swing=1, target=rr2 |
| Maximum drawdown | min | 13,264.84 USD | [2](../../../results/fair_price_reversal/ny/metric_winners/order_2/trades_slippage0.csv) | 1848 | 64 | window=30, atr_mult=0.5, swing=1, target=far |
| Consecutive losses | min | 6.000 | [1](../../../results/fair_price_reversal/ny/metric_winners/order_1/trades_slippage0.csv) | 1841 | 64 | window=30, atr_mult=0.5, swing=1, target=near |
| Sharpe ratio | max | 0.098 | [52](../../../results/fair_price_reversal/ny/metric_winners/order_52/trades_slippage0.csv) | 4664 | 64 | window=120, atr_mult=0.5, swing=1, target=rr2 |
| Sortino ratio | max | 0.173 | [52](../../../results/fair_price_reversal/ny/metric_winners/order_52/trades_slippage0.csv) | 4664 | 64 | window=120, atr_mult=0.5, swing=1, target=rr2 |
| R-multiple | max | No eligible value | — | — | 0 | — |
| Maximum adverse excursion (MAE) | min | 120.71 USD | [1](../../../results/fair_price_reversal/ny/metric_winners/order_1/trades_slippage0.csv) | 1841 | 64 | window=30, atr_mult=0.5, swing=1, target=near |
| Maximum favorable excursion (MFE) | max | 263.82 USD | [64](../../../results/fair_price_reversal/ny/metric_winners/order_64/trades_slippage0.csv) | 4939 | 64 | window=120, atr_mult=2.0, swing=1, target=rr2 |

- **Net profit:** Sum of closed-trade profit after commission; excludes open P&L.
- **Win rate:** Winning closed trades divided by all closed trades, including breakevens.
- **Expectancy:** Mean net profit per closed trade, including losses and breakevens.
- **Profit factor:** Gross winning profit divided by gross losing profit, both after commission. Undefined without losses.
- **Payoff ratio:** Average net winning trade divided by the absolute average net losing trade. Requires wins and losses.
- **Risk of ruin (estimate):** Infinite-horizon diffusion estimate of losing the declared amount from starting capital. Assumes independent, stationary, fixed-size net trade P&L; ignores intratrade losses and margin.
- **Maximum drawdown:** Largest equity drawdown under the tester's intrabar TradingView convention, including an open trade at the end.
- **Consecutive losses:** Longest streak of losing closed trades in execution order. A win or breakeven resets the streak.
- **Sharpe ratio:** Monthly marked-to-market excess return divided by population standard deviation, using 2% annual risk-free rate; not annualized.
- **Sortino ratio:** Monthly marked-to-market excess return divided by downside deviation about the risk-free rate; not annualized.
- **R-multiple:** Mean net trade profit / initial stop risk in dollars. Risk is actual fill to initial stop, before costs. Requires positive initial risk for every closed trade; R standard deviation and mean / standard deviation describe consistency.
- **Maximum adverse excursion (MAE):** Mean of each closed trade's maximum adverse price excursion in dollars, before commission; only the exposed intrabar path counts.
- **Maximum favorable excursion (MFE):** Mean of each closed trade's maximum favorable price excursion in dollars, before commission; only the exposed intrabar path counts. Unrealized opportunity, not realized profit.

Full selection metadata: [metric_winners.json](../../../results/fair_price_reversal/ny/metric_winners.json).

### Top 10 combinations

| # | window | atr_mult | swing | target | Net profit | Trades | % profitable | Profit factor | Max DD |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 120 | 0.5 | 1 | rr2 | 60,180.72 USD | 4,664 | 34.69% | 1.086 | 24,678.62 USD |
| 2 | 90 | 0.5 | 1 | rr2 | 56,339.46 USD | 4,127 | 34.58% | 1.091 | 27,146.34 USD |
| 3 | 120 | 1.0 | 1 | rr2 | 43,676.68 USD | 4,966 | 34.35% | 1.058 | 32,478.54 USD |
| 4 | 120 | 2.0 | 1 | rr2 | 43,345.22 USD | 4,939 | 34.40% | 1.057 | 29,582.36 USD |
| 5 | 120 | 1.5 | 1 | rr2 | 42,682.16 USD | 4,992 | 34.29% | 1.056 | 29,608.74 USD |
| 6 | 90 | 1.0 | 1 | rr2 | 40,178.94 USD | 4,453 | 34.22% | 1.060 | 31,747.86 USD |
| 7 | 90 | 2.0 | 1 | rr2 | 37,547.58 USD | 4,421 | 34.18% | 1.055 | 29,381.58 USD |
| 8 | 90 | 1.5 | 1 | rr2 | 36,720.40 USD | 4,480 | 34.08% | 1.054 | 30,708.06 USD |
| 9 | 60 | 0.5 | 1 | rr2 | 29,234.70 USD | 3,265 | 33.91% | 1.060 | 23,405.02 USD |
| 10 | 60 | 2.0 | 1 | rr2 | 24,293.32 USD | 3,534 | 33.70% | 1.045 | 29,018.18 USD |

Profitable combinations: 16 of 64.
