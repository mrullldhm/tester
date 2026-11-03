# Tupa Trade (owner price action, MSS stop-limit), CL1! New York session: results

Generated 2026-11-03 05:24 UTC by `python -m tvtester.cli test tupa_trade`.

Owner strategy, spec in [README.md](README.md) (sections 3b and 3c). Pure price action on the owner swing points
([`indicators/structure_swings.pine`](../../../indicators/structure_swings.pine)), New York session only
(09:00-14:30 New York = 21:00-02:30 Malaysia time in US summer time, 22:00-03:30 in US winter time). Short side
below; the long side is the mirror.

- **Bias.** Tested timeframe T = the lowest timeframe from `t_min` up to daily whose newest swing is a swing low
  (a candidate: no swing high confirmed after it). Short bias when every timeframe below T, down to 5m, is in
  downtrend (its last uptrend HL touched by a closed candle). Timeframes 5m, 15m, 1H, 4H (anchored 18:00 New York),
  daily (CME trading day). Closed candles only.
- **Entry (1m market structure shift).** Newest confirmed 1m swing is a swing high and the swing low before it is
  a HL, not touched yet. Sell **stop-limit**: trigger = that HL (touch counts), limit = the HL, or stop loss - 25
  ticks when the stop loss is more than 25 ticks away.
- **Exits.** Stop loss exactly at the 1m swing high, take profit 25 ticks from the fill, or close at the New York
  session end (next open after the 14:29 bar). An unfilled triggered limit is cancelled when the next 1m swing high
  is confirmed. One trade per session.
- **Grid.** `t_min` (lowest timeframe allowed as T) is Claude's open point, not an owner rule. Everything else is
  fixed by the owner: TP 25 ticks, max risk 25 ticks.

Stop-limit fills follow the engine's stop-limit rule (`docs/ENGINE.md`, fills rule 8), not yet checked against a
TradingView export. A runnable Pine v6 twin is in [`strategies/tupa_trade.pine`](../../../strategies/tupa_trade.pine).

Review status (2026-11-03): Codex independently replicated the top combination ([R19](../../REVIEWS.md)),
in-sample, best of 4: 858 trades, a loss of 14,149.16 USD before slippage. This confirms internal consistency;
a TradingView export comparison is still needed for parity.
R19 also records a separate candle-grouping discrepancy on bars within the assumed daily halt.

## Test settings (TradingView Properties)

| Setting | Value |
|---|---|
| Symbol | CL1! (NYMEX Light Crude Oil, front month), 1-minute bars |
| Data | 2010-06-07 00:00:00+00:00 to 2026-11-02 16:30:00+00:00 UTC, 5,672,666 bars (manifest written 2026-10-29T06:25:08+00:00) |
| Initial capital | 50,000.00 USD |
| Order size | 1 contract |
| Commission | 2.01 USD per contract per order (4.02 USD round trip) |
| Slippage | 0 ticks baseline; 1 tick, 2 ticks shown separately (market and stop fills only, as TradingView) |
| Pyramiding | 0 (one position) |
| Fills | TradingView broker emulator, Bar Magnifier off, limits fill on touch |
| Roll rule | position closed at the last bar of a contract (exit reason `roll`) |

## How the top combination was chosen

Every variant ran all 4 combinations of the grid below at 0 ticks slippage. The combination with the highest **net profit** is the top combination (ties: higher profit factor, then grid order). Its slippage results use the same parameters, never a re-optimized set.

| Parameter | Values |
|---|---|
| `t_min` | 15m, 1h, 4h, 1d |

> **Read this first.** The top combination is the best of 4 tries on the same data it is reported on (in-sample). Picking the best of many tries makes the result look better than what the same rules can be expected to earn on new data. Treat these numbers as an upper bound, not as a forecast.

## Summary: top combination per variant

| Variant | Parameters | Net profit (0 / 1 / 2 ticks) | Trades | % profitable | Profit factor | Max DD |
|---|---|---|---|---|---|---|
| ny | t_min=1d | -14,149.16 USD / -20,179.16 USD / -26,209.16 USD | 858 | 31.12% | 0.819 | 16,076.00 USD |

## Variant: ny

**Top combination:** `session=ny`, `t_min=1d`

![Equity curve](equity_ny.png)

Files: [grid](../../../results/tupa_trade/ny/grid.csv), [trades 0 ticks](../../../results/tupa_trade/ny/trades_slippage0.csv), [trades 1 ticks](../../../results/tupa_trade/ny/trades_slippage1.csv), [trades 2 ticks](../../../results/tupa_trade/ny/trades_slippage2.csv), [summary](../../../results/tupa_trade/ny/summary.json)

### Baseline: 0 ticks slippage

#### Overview

| Metric | Value |
|---|---|
| Net profit | -14,149.16 USD (-28.30%) |
| Total closed trades | 858 |
| Percent profitable | 31.12% |
| Profit factor | 0.819 |
| Max equity drawdown | 16,076.00 USD (32.15%) |
| Avg trade | -16.49 USD |
| Avg # bars in trades | 13 |

#### Performance

| Metric | All | Long | Short |
|---|---|---|---|
| Net profit | -14,149.16 USD (-28.30%) | -6,566.34 USD (-13.13%) | -7,582.82 USD (-15.17%) |
| Gross profit | 63,846.66 USD (127.69%) | 31,207.40 USD (62.41%) | 32,639.26 USD (65.28%) |
| Gross loss | 77,995.82 USD (155.99%) | 37,773.74 USD (75.55%) | 40,222.08 USD (80.44%) |
| Commission paid | 3,449.16 USD | 1,676.34 USD | 1,772.82 USD |

| Account | Value |
|---|---|
| Initial capital | 50,000.00 USD |
| Buy & hold return (TV-style, all capital at the first entry) | 15,690.66 USD (31.38%) |
| Max equity run-up (intrabar) | 3,513.02 USD (7.03%) |
| Max equity drawdown (intrabar) | 16,076.00 USD (32.15%) |
| Open P&L | 0.00 USD |
| Max contracts held | 1 |

#### Trades analysis

| Metric | All | Long | Short |
|---|---|---|---|
| Total closed trades | 858 | 417 | 441 |
| Winning trades | 267 | 130 | 137 |
| Losing trades | 591 | 287 | 304 |
| Even trades | 0 | 0 | 0 |
| Percent profitable | 31.12% | 31.18% | 31.07% |
| Avg P&L | -16.49 USD | -15.75 USD | -17.19 USD |
| Avg P&L % | -0.02% | -0.01% | -0.02% |
| Avg winning trade | 239.13 USD | 240.06 USD | 238.24 USD |
| Avg losing trade | 131.97 USD | 131.62 USD | 132.31 USD |
| Ratio avg win / avg loss | 1.812 | 1.824 | 1.801 |
| Largest winning trade | 245.98 USD | 245.98 USD | 245.98 USD |
| Largest winning trade % | 1.98% | 1.98% | 1.05% |
| Largest losing trade | 254.02 USD | 254.02 USD | 254.02 USD |
| Largest losing trade % | 0.72% | 0.71% | 0.72% |
| Avg # bars in trades | 13 | 14 | 12 |
| Avg # bars in winning trades | 19 | 19 | 18 |
| Avg # bars in losing trades | 11 | 12 | 10 |

#### Risk/performance ratios

| Metric | Value |
|---|---|
| Sharpe ratio | -0.325 |
| Sortino ratio | -0.368 |
| Profit factor | 0.819 |
| Margin calls | 0 |

#### List of trades (last 10, newest first; full list in the trades CSV)

| Trade # | Type | Signal | Date/Time (UTC) | Price | Contracts | Profit | Cum. profit | Run-up | Drawdown |
|---|---|---|---|---|---|---|---|---|---|
| 858 | Exit short | Exit | 2026-10-16 15:36 | 98.04 | 1 | -254.02 USD (-0.26%) | -14,149.16 USD | 0.00 USD | 250.00 USD |
|  | Entry short | Short | 2026-10-16 15:33 | 97.79 | 1 |  |  |  |  |
| 857 | Exit long | Exit | 2026-10-13 14:32 | 93.56 | 1 | -194.02 USD (-0.21%) | -13,895.14 USD | 40.00 USD | 190.00 USD |
|  | Entry long | Long | 2026-10-13 14:24 | 93.75 | 1 |  |  |  |  |
| 856 | Exit long | Exit | 2026-10-12 15:01 | 93.71 | 1 | -204.02 USD (-0.22%) | -13,701.12 USD | 70.00 USD | 200.00 USD |
|  | Entry long | Long | 2026-10-12 14:48 | 93.91 | 1 |  |  |  |  |
| 855 | Exit short | Exit | 2026-10-08 14:15 | 92.28 | 1 | -184.02 USD (-0.20%) | -13,497.10 USD | 110.00 USD | 180.00 USD |
|  | Entry short | Short | 2026-10-08 14:10 | 92.10 | 1 |  |  |  |  |
| 854 | Exit long | Exit | 2026-09-28 15:04 | 95.48 | 1 | -194.02 USD (-0.20%) | -13,313.08 USD | 10.00 USD | 190.00 USD |
|  | Entry long | Long | 2026-09-28 15:04 | 95.67 | 1 |  |  |  |  |
| 853 | Exit short | Exit | 2026-09-15 13:11 | 101.91 | 1 | -254.02 USD (-0.25%) | -13,119.06 USD | 80.00 USD | 250.00 USD |
|  | Entry short | Short | 2026-09-15 13:07 | 101.66 | 1 |  |  |  |  |
| 852 | Exit long | Exit | 2026-09-02 16:44 | 91.16 | 1 | 245.98 USD (0.27%) | -12,865.04 USD | 250.00 USD | 70.00 USD |
|  | Entry long | Long | 2026-09-02 16:36 | 90.91 | 1 |  |  |  |  |
| 851 | Exit long | Exit | 2026-07-29 13:21 | 84.21 | 1 | -254.02 USD (-0.30%) | -13,111.02 USD | 0.00 USD | 250.00 USD |
|  | Entry long | Long | 2026-07-29 13:20 | 84.46 | 1 |  |  |  |  |
| 850 | Exit long | Exit | 2026-07-24 18:05 | 88.78 | 1 | -184.02 USD (-0.21%) | -12,857.00 USD | 240.00 USD | 180.00 USD |
|  | Entry long | Long | 2026-07-24 17:49 | 88.96 | 1 |  |  |  |  |
| 849 | Exit long | Exit | 2026-07-23 16:33 | 92.21 | 1 | 245.98 USD (0.27%) | -12,672.98 USD | 250.00 USD | 0.00 USD |
|  | Entry long | Long | 2026-07-23 16:31 | 91.96 | 1 |  |  |  |  |

#### By year (extra, not a TV tab)

| Year | Trades | Net profit | % profitable | Profit factor |
|---|---|---|---|---|
| 2010 | 36 | -2,934.72 USD | 25.00% | 0.430 |
| 2011 | 53 | -903.06 USD | 41.51% | 0.854 |
| 2012 | 48 | -4,162.96 USD | 18.75% | 0.347 |
| 2013 | 51 | -115.02 USD | 37.25% | 0.976 |
| 2014 | 45 | -670.90 USD | 28.89% | 0.827 |
| 2015 | 53 | 296.94 USD | 39.62% | 1.064 |
| 2016 | 52 | -499.04 USD | 25.00% | 0.865 |
| 2017 | 55 | 398.90 USD | 23.64% | 1.147 |
| 2018 | 68 | -2,573.36 USD | 22.06% | 0.570 |
| 2019 | 37 | -288.74 USD | 27.03% | 0.895 |
| 2020 | 42 | -618.84 USD | 28.57% | 0.818 |
| 2021 | 63 | 356.74 USD | 36.51% | 1.071 |
| 2022 | 42 | -1,798.84 USD | 35.71% | 0.672 |
| 2023 | 57 | 280.86 USD | 40.35% | 1.054 |
| 2024 | 56 | -605.12 USD | 28.57% | 0.862 |
| 2025 | 58 | -1,593.16 USD | 22.41% | 0.638 |
| 2026 | 42 | 1,281.16 USD | 50.00% | 1.330 |

#### Exit reasons (extra)

| Reason | Trades |
|---|---|
| stop | 584 |
| limit | 255 |
| close | 19 |

- Session-end exits more than 5 minutes after the flat time (missing bars / early closes): 2.
- Roll exits: 0.

### Slippage scenarios (same parameters)

| Metric | Baseline (0 ticks) | 1 tick | 2 ticks |
|---|---|---|---|
| Net profit | -14,149.16 USD | -20,179.16 USD | -26,209.16 USD |
| Total closed trades | 858 | 858 | 858 |
| Percent profitable | 31.12% | 31.00% | 31.00% |
| Profit factor | 0.819 | 0.760 | 0.708 |
| Avg trade | -16.49 USD | -23.52 USD | -30.55 USD |
| Max equity drawdown | 16,076.00 USD | 21,786.00 USD | 27,496.00 USD |
| Sharpe ratio | -0.325 | -0.366 | -0.399 |
| Sortino ratio | -0.368 | -0.404 | -0.430 |

#### 1 tick slippage: full report

##### Overview

| Metric | Value |
|---|---|
| Net profit | -20,179.16 USD (-40.36%) |
| Total closed trades | 858 |
| Percent profitable | 31.00% |
| Profit factor | 0.760 |
| Max equity drawdown | 21,786.00 USD (43.57%) |
| Avg trade | -23.52 USD |
| Avg # bars in trades | 13 |

##### Performance

| Metric | All | Long | Short |
|---|---|---|---|
| Net profit | -20,179.16 USD (-40.36%) | -9,486.34 USD (-18.97%) | -10,692.82 USD (-21.39%) |
| Gross profit | 63,730.68 USD (127.46%) | 31,161.42 USD (62.32%) | 32,569.26 USD (65.14%) |
| Gross loss | 83,909.84 USD (167.82%) | 40,647.76 USD (81.30%) | 43,262.08 USD (86.52%) |
| Commission paid | 3,449.16 USD | 1,676.34 USD | 1,772.82 USD |

| Account | Value |
|---|---|
| Initial capital | 50,000.00 USD |
| Buy & hold return (TV-style, all capital at the first entry) | 15,690.66 USD (31.38%) |
| Max equity run-up (intrabar) | 3,273.02 USD (6.55%) |
| Max equity drawdown (intrabar) | 21,786.00 USD (43.57%) |
| Open P&L | 0.00 USD |
| Max contracts held | 1 |

##### Trades analysis

| Metric | All | Long | Short |
|---|---|---|---|
| Total closed trades | 858 | 417 | 441 |
| Winning trades | 266 | 129 | 137 |
| Losing trades | 592 | 288 | 304 |
| Even trades | 0 | 0 | 0 |
| Percent profitable | 31.00% | 30.94% | 31.07% |
| Avg P&L | -23.52 USD | -22.75 USD | -24.25 USD |
| Avg P&L % | -0.03% | -0.02% | -0.03% |
| Avg winning trade | 239.59 USD | 241.56 USD | 237.73 USD |
| Avg losing trade | 141.74 USD | 141.14 USD | 142.31 USD |
| Ratio avg win / avg loss | 1.690 | 1.712 | 1.671 |
| Largest winning trade | 245.98 USD | 245.98 USD | 245.98 USD |
| Largest winning trade % | 1.98% | 1.98% | 1.05% |
| Largest losing trade | 264.02 USD | 264.02 USD | 264.02 USD |
| Largest losing trade % | 0.76% | 0.74% | 0.76% |
| Avg # bars in trades | 13 | 14 | 12 |
| Avg # bars in winning trades | 19 | 19 | 18 |
| Avg # bars in losing trades | 11 | 12 | 10 |

##### Risk/performance ratios

| Metric | Value |
|---|---|
| Sharpe ratio | -0.366 |
| Sortino ratio | -0.404 |
| Profit factor | 0.760 |
| Margin calls | 0 |

#### 2 ticks slippage: full report

##### Overview

| Metric | Value |
|---|---|
| Net profit | -26,209.16 USD (-52.42%) |
| Total closed trades | 858 |
| Percent profitable | 31.00% |
| Profit factor | 0.708 |
| Max equity drawdown | 27,496.00 USD (54.99%) |
| Avg trade | -30.55 USD |
| Avg # bars in trades | 13 |

##### Performance

| Metric | All | Long | Short |
|---|---|---|---|
| Net profit | -26,209.16 USD (-52.42%) | -12,406.34 USD (-24.81%) | -13,802.82 USD (-27.61%) |
| Gross profit | 63,620.68 USD (127.24%) | 31,121.42 USD (62.24%) | 32,499.26 USD (65.00%) |
| Gross loss | 89,829.84 USD (179.66%) | 43,527.76 USD (87.06%) | 46,302.08 USD (92.60%) |
| Commission paid | 3,449.16 USD | 1,676.34 USD | 1,772.82 USD |

| Account | Value |
|---|---|
| Initial capital | 50,000.00 USD |
| Buy & hold return (TV-style, all capital at the first entry) | 15,690.66 USD (31.38%) |
| Max equity run-up (intrabar) | 3,033.02 USD (6.07%) |
| Max equity drawdown (intrabar) | 27,496.00 USD (54.99%) |
| Open P&L | 0.00 USD |
| Max contracts held | 1 |

##### Trades analysis

| Metric | All | Long | Short |
|---|---|---|---|
| Total closed trades | 858 | 417 | 441 |
| Winning trades | 266 | 129 | 137 |
| Losing trades | 592 | 288 | 304 |
| Even trades | 0 | 0 | 0 |
| Percent profitable | 31.00% | 30.94% | 31.07% |
| Avg P&L | -30.55 USD | -29.75 USD | -31.30 USD |
| Avg P&L % | -0.04% | -0.03% | -0.05% |
| Avg winning trade | 239.18 USD | 241.25 USD | 237.22 USD |
| Avg losing trade | 151.74 USD | 151.14 USD | 152.31 USD |
| Ratio avg win / avg loss | 1.576 | 1.596 | 1.557 |
| Largest winning trade | 245.98 USD | 245.98 USD | 245.98 USD |
| Largest winning trade % | 1.98% | 1.98% | 1.05% |
| Largest losing trade | 274.02 USD | 274.02 USD | 274.02 USD |
| Largest losing trade % | 0.80% | 0.76% | 0.80% |
| Avg # bars in trades | 13 | 14 | 12 |
| Avg # bars in winning trades | 19 | 19 | 18 |
| Avg # bars in losing trades | 11 | 12 | 10 |

##### Risk/performance ratios

| Metric | Value |
|---|---|
| Sharpe ratio | -0.399 |
| Sortino ratio | -0.430 |
| Profit factor | 0.708 |
| Margin calls | 0 |

### Top 10 combinations (0 ticks)

| # | t_min | Net profit | Trades | % profitable | Profit factor | Max DD |
|---|---|---|---|---|---|---|
| 1 | 1d | -14,149.16 USD | 858 | 31.12% | 0.819 | 16,076.00 USD |
| 2 | 1h | -32,852.42 USD | 3,421 | 32.83% | 0.892 | 36,035.26 USD |
| 3 | 4h | -33,554.12 USD | 2,006 | 30.76% | 0.815 | 34,763.68 USD |
| 4 | 15m | -34,157.98 USD | 4,099 | 33.40% | 0.907 | 38,751.04 USD |

Profitable combinations: 0 of 4.
