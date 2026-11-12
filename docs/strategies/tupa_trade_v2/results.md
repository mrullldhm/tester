# Tupa Trade v2 (owner price action, MSS stop-limit, interpretation switches), CL1! New York session: results

Generated 2026-11-12 00:47 UTC by `python -m tvtester.cli test tupa_trade_v2`.

**Tupa Trade v2** = v1 plus five interpretation switches ([README.md](README.md)); this feature-1 run keeps every
switch at its v1 value, so it is v1 under the current owner swings. Owner spec:
[`../tupa_trade/README.md`](../tupa_trade/README.md) (sections 3b and 3c). Pure price action on the owner swing points
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
TradingView export. A runnable Pine v6 twin is in [`strategies/tupa_trade_v2.pine`](../../../strategies/tupa_trade_v2.pine).

## Test settings (TradingView Properties)

| Setting | Value |
|---|---|
| Symbol | CL1! (NYMEX Light Crude Oil, front month), 1-minute bars |
| Data | 2010-06-07 00:00:00+00:00 to 2026-11-10 08:27:00+00:00 UTC, 5,680,278 bars (manifest written 2026-11-04T02:31:15+00:00) |
| Initial capital | 50,000.00 USD |
| Order size | 1 contract |
| Commission | 2.01 USD per contract per order (4.02 USD round trip) |
| Execution | Limit entries; commission included; no added slippage |
| Pyramiding | 0 (one position) |
| Fills | TradingView broker emulator, Bar Magnifier off, limits fill on touch |
| Roll rule | position closed at the last bar of a contract (exit reason `roll`) |

## How the top combination was chosen

Every variant ran all combinations of its grid below with commission included. The combination with the highest **net profit** is the top combination (ties: higher profit factor, then grid order). This reference is retained for compatibility. Thirteen separate metric winners are also selected, with a declared minimum trade count; their values, settings and trade lists are linked below. No slippage stress runs are performed.

| Parameter | Values |
|---|---|
| `t_min` | 15m, 1h, 4h, 1d |

> **Read this first.** The top combination is the best of 4 tries (per variant) on the same data it is reported on (in-sample). Picking the best of many tries makes the result look better than what the same rules can be expected to earn on new data. Treat these numbers as an upper bound, not as a forecast.

## Summary: top combination per variant

| Variant | Parameters | Net profit | Trades | % profitable | Profit factor | Max DD |
|---|---|---|---|---|---|---|
| ny | t_min=1d | -11,212.56 USD | 528 | 29.36% | 0.770 | 11,913.72 USD |

## Variant: ny

**Top combination:** `session=ny`, `t_min=1d`

![Equity curve](equity_ny.png)

Files: [grid](../../../results/tupa_trade_v2/ny/grid.csv), [trades 0 ticks](../../../results/tupa_trade_v2/ny/trades_slippage0.csv), [summary](../../../results/tupa_trade_v2/ny/summary.json)

### Results after commission

#### Overview

| Metric | Value |
|---|---|
| Net profit | -11,212.56 USD (-22.43%) |
| Total closed trades | 528 |
| Percent profitable | 29.36% |
| Profit factor | 0.770 |
| Max equity drawdown | 11,913.72 USD (23.83%) |
| Avg trade | -21.24 USD |
| Avg # bars in trades | 14 |

#### Performance

| Metric | All | Long | Short |
|---|---|---|---|
| Net profit | -11,212.56 USD (-22.43%) | -6,497.26 USD (-12.99%) | -4,715.30 USD (-9.43%) |
| Gross profit | 37,596.90 USD (75.19%) | 18,906.44 USD (37.81%) | 18,690.46 USD (37.38%) |
| Gross loss | 48,809.46 USD (97.62%) | 25,403.70 USD (50.81%) | 23,405.76 USD (46.81%) |
| Commission paid | 2,122.56 USD | 1,057.26 USD | 1,065.30 USD |

| Account | Value |
|---|---|
| Initial capital | 50,000.00 USD |
| Buy & hold return (TV-style, all capital at the first entry) | 8,175.11 USD (16.35%) |
| Max equity run-up (intrabar) | 2,308.70 USD (4.62%) |
| Max equity drawdown (intrabar) | 11,913.72 USD (23.83%) |
| Open P&L | 0.00 USD |
| Max contracts held | 1 |

#### Trades analysis

| Metric | All | Long | Short |
|---|---|---|---|
| Total closed trades | 528 | 263 | 265 |
| Winning trades | 155 | 78 | 77 |
| Losing trades | 373 | 185 | 188 |
| Even trades | 0 | 0 | 0 |
| Percent profitable | 29.36% | 29.66% | 29.06% |
| Avg P&L | -21.24 USD | -24.70 USD | -17.79 USD |
| Avg P&L % | -0.02% | -0.02% | -0.03% |
| Avg winning trade | 242.56 USD | 242.39 USD | 242.73 USD |
| Avg losing trade | 130.86 USD | 137.32 USD | 124.50 USD |
| Ratio avg win / avg loss | 1.854 | 1.765 | 1.950 |
| Largest winning trade | 245.98 USD | 245.98 USD | 245.98 USD |
| Largest winning trade % | 1.98% | 1.98% | 1.05% |
| Largest losing trade | 264.02 USD | 264.02 USD | 254.02 USD |
| Largest losing trade % | 0.72% | 0.61% | 0.72% |
| Avg # bars in trades | 14 | 15 | 13 |
| Avg # bars in winning trades | 21 | 24 | 19 |
| Avg # bars in losing trades | 11 | 11 | 10 |

#### Risk/performance ratios

| Metric | Value |
|---|---|
| Sharpe ratio | -0.466 |
| Sortino ratio | -0.463 |
| Profit factor | 0.770 |
| Margin calls | 0 |

#### List of trades (last 10, newest first; full list in the trades CSV)

| Trade # | Type | Signal | Date/Time (UTC) | Price | Contracts | Profit | Cum. profit | Run-up | Drawdown |
|---|---|---|---|---|---|---|---|---|---|
| 528 | Exit short | Exit | 2026-10-08 17:11 | 91.00 | 1 | -124.02 USD (-0.14%) | -11,212.56 USD | 100.00 USD | 120.00 USD |
|  | Entry short | Short | 2026-10-08 17:05 | 90.88 | 1 |  |  |  |  |
| 527 | Exit long | Exit | 2026-09-28 15:04 | 95.48 | 1 | -194.02 USD (-0.20%) | -11,088.54 USD | 10.00 USD | 190.00 USD |
|  | Entry long | Long | 2026-09-28 15:04 | 95.67 | 1 |  |  |  |  |
| 526 | Exit short | Exit | 2026-07-30 16:51 | 83.97 | 1 | -174.02 USD (-0.21%) | -10,894.52 USD | 30.00 USD | 170.00 USD |
|  | Entry short | Short | 2026-07-30 16:46 | 83.80 | 1 |  |  |  |  |
| 525 | Exit long | Exit | 2026-07-29 14:26 | 84.77 | 1 | 245.98 USD (0.29%) | -10,720.50 USD | 250.00 USD | 160.00 USD |
|  | Entry long | Long | 2026-07-29 14:13 | 84.52 | 1 |  |  |  |  |
| 524 | Exit long | Exit | 2026-07-13 16:00 | 74.93 | 1 | 245.98 USD (0.33%) | -10,966.48 USD | 250.00 USD | 170.00 USD |
|  | Entry long | Long | 2026-07-13 15:35 | 74.68 | 1 |  |  |  |  |
| 523 | Exit short | Exit | 2026-07-09 14:38 | 72.73 | 1 | -174.02 USD (-0.24%) | -11,212.46 USD | 170.00 USD | 170.00 USD |
|  | Entry short | Short | 2026-07-09 14:32 | 72.56 | 1 |  |  |  |  |
| 522 | Exit long | Exit | 2026-06-10 14:03 | 89.76 | 1 | -84.02 USD (-0.09%) | -11,038.44 USD | 90.00 USD | 80.00 USD |
|  | Entry long | Long | 2026-06-10 14:00 | 89.84 | 1 |  |  |  |  |
| 521 | Exit long | Exit | 2026-06-01 14:57 | 94.71 | 1 | 245.98 USD (0.26%) | -10,954.42 USD | 250.00 USD | 40.00 USD |
|  | Entry long | Long | 2026-06-01 14:55 | 94.46 | 1 |  |  |  |  |
| 520 | Exit long | Exit | 2026-05-07 18:28 | 94.76 | 1 | -244.02 USD (-0.26%) | -11,200.40 USD | 70.00 USD | 240.00 USD |
|  | Entry long | Long | 2026-05-07 18:27 | 95.00 | 1 |  |  |  |  |
| 519 | Exit long | Exit | 2026-05-05 17:11 | 102.16 | 1 | -154.02 USD (-0.15%) | -10,956.38 USD | 30.00 USD | 150.00 USD |
|  | Entry long | Long | 2026-05-05 17:10 | 102.31 | 1 |  |  |  |  |

#### By year (extra, not a TV tab)

| Year | Trades | Net profit | % profitable | Profit factor |
|---|---|---|---|---|
| 2010 | 18 | -1,292.36 USD | 27.78% | 0.488 |
| 2011 | 36 | -1,684.72 USD | 36.11% | 0.655 |
| 2012 | 32 | -1,598.64 USD | 25.00% | 0.552 |
| 2013 | 28 | -2,012.56 USD | 21.43% | 0.423 |
| 2014 | 22 | 101.56 USD | 31.82% | 1.063 |
| 2015 | 32 | 361.36 USD | 40.62% | 1.127 |
| 2016 | 40 | -30.80 USD | 27.50% | 0.989 |
| 2017 | 32 | -658.64 USD | 15.62% | 0.651 |
| 2018 | 28 | -892.56 USD | 25.00% | 0.618 |
| 2019 | 30 | 1,069.40 USD | 40.00% | 1.568 |
| 2020 | 28 | 647.44 USD | 35.71% | 1.357 |
| 2021 | 35 | -1,140.70 USD | 25.71% | 0.633 |
| 2022 | 31 | -2,244.62 USD | 25.81% | 0.467 |
| 2023 | 39 | 113.22 USD | 38.46% | 1.032 |
| 2024 | 37 | -428.74 USD | 29.73% | 0.863 |
| 2025 | 41 | -1,464.82 USD | 19.51% | 0.573 |
| 2026 | 19 | -56.38 USD | 36.84% | 0.968 |

#### Exit reasons (extra)

| Reason | Trades |
|---|---|
| stop | 369 |
| limit | 151 |
| close | 8 |

- Session-end exits more than 5 minutes after the flat time (missing bars / early closes): 2.
- Roll exits: 0.

### Best settings by metric

Each winner needs at least 30 closed trades. Undefined values are excluded. Ties: higher net profit, higher profit factor, then grid order. Ruin loss threshold: 25,000.00 USD from starting capital. All selections are in-sample. MAE/MFE objectives use the mean of the per-trade maxima.

| Metric | Goal | Best value | Grid order | Trades | Eligible settings | Parameters |
|---|---|---|---|---|---|---|
| Net profit | max | -11,212.56 USD | [4](../../../results/tupa_trade_v2/ny/metric_winners/order_4/trades_slippage0.csv) | 528 | 4 | t_min=1d |
| Win rate | max | 32.82% | [1](../../../results/tupa_trade_v2/ny/metric_winners/order_1/trades_slippage0.csv) | 3726 | 4 | t_min=15m |
| Expectancy | max | -10.09 USD | [1](../../../results/tupa_trade_v2/ny/metric_winners/order_1/trades_slippage0.csv) | 3726 | 4 | t_min=15m |
| Profit factor | max | 0.888 | [1](../../../results/tupa_trade_v2/ny/metric_winners/order_1/trades_slippage0.csv) | 3726 | 4 | t_min=15m |
| Payoff ratio | max | 1.859 | [2](../../../results/tupa_trade_v2/ny/metric_winners/order_2/trades_slippage0.csv) | 2450 | 4 | t_min=1h |
| Risk of ruin (estimate) | min | 100.00% | [4](../../../results/tupa_trade_v2/ny/metric_winners/order_4/trades_slippage0.csv) | 528 | 4 | t_min=1d |
| Maximum drawdown | min | 11,913.72 USD | [4](../../../results/tupa_trade_v2/ny/metric_winners/order_4/trades_slippage0.csv) | 528 | 4 | t_min=1d |
| Consecutive losses | min | 13.000 | [4](../../../results/tupa_trade_v2/ny/metric_winners/order_4/trades_slippage0.csv) | 528 | 4 | t_min=1d |
| Sharpe ratio | max | -0.197 | [1](../../../results/tupa_trade_v2/ny/metric_winners/order_1/trades_slippage0.csv) | 3726 | 4 | t_min=15m |
| Sortino ratio | max | -0.247 | [1](../../../results/tupa_trade_v2/ny/metric_winners/order_1/trades_slippage0.csv) | 3726 | 4 | t_min=15m |
| R-multiple | max | -0.095 | [1](../../../results/tupa_trade_v2/ny/metric_winners/order_1/trades_slippage0.csv) | 3726 | 4 | t_min=15m |
| Maximum adverse excursion (MAE) | min | 105.15 USD | [2](../../../results/tupa_trade_v2/ny/metric_winners/order_2/trades_slippage0.csv) | 2450 | 4 | t_min=1h |
| Maximum favorable excursion (MFE) | max | 130.50 USD | [1](../../../results/tupa_trade_v2/ny/metric_winners/order_1/trades_slippage0.csv) | 3726 | 4 | t_min=15m |

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

Full selection metadata: [metric_winners.json](../../../results/tupa_trade_v2/ny/metric_winners.json).

### Top 10 combinations

| # | t_min | Net profit | Trades | % profitable | Profit factor | Max DD |
|---|---|---|---|---|---|---|
| 1 | 1d | -11,212.56 USD | 528 | 29.36% | 0.770 | 11,913.72 USD |
| 2 | 4h | -24,553.76 USD | 1,088 | 29.04% | 0.754 | 25,424.52 USD |
| 3 | 1h | -32,119.00 USD | 2,450 | 31.43% | 0.852 | 34,155.60 USD |
| 4 | 15m | -37,608.52 USD | 3,726 | 32.82% | 0.888 | 40,436.24 USD |

Profitable combinations: 0 of 4.
