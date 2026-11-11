# FSP — Failed Swing Point: fixed default baseline

[Strategy specification](README.md). One fixed configuration; no parameter search or 30m comparison.

Data: **2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00**, 4,682,668 one-minute CL bars. End is exclusive 2024-01-01 UTC.

Settings: provisional 1H swings, 15m confirmation, both directions, New York entries 09:00–14:30 ET; one CL contract; maximum planned stop distance 25 ticks; TP 50 ticks from actual fill; $2.01/order; no added slippage.

MSS eligibility ends on a post-confirmation touch of the breach candle's fixed 15m high (short) or low (long), including a touch within the signal minute before its close. Already-placed limits are unaffected by that boundary or by later 1H points. Pending limits cancel at New York entry-session end; the scheduled CL daily close flattens all positions and clears all setups. No overnight carry. Roll exits apply.

## Results

#### Overview

| Metric | Value |
|---|---|
| Net profit | -32,452.00 USD (-64.90%) |
| Total closed trades | 12,600 |
| Percent profitable | 18.79% |
| Profit factor | 0.971 |
| Max equity drawdown | 84,570.74 USD (169.14%) |
| Avg trade | -2.58 USD |
| Avg # bars in trades | 26 |

#### Performance

| Metric | All | Long | Short |
|---|---|---|---|
| Net profit | -32,452.00 USD (-64.90%) | -32,852.54 USD (-65.71%) | 400.54 USD (0.80%) |
| Gross profit | 1,090,544.66 USD (2,181.09%) | 520,821.12 USD (1,041.64%) | 569,723.54 USD (1,139.45%) |
| Gross loss | 1,122,996.66 USD (2,245.99%) | 553,673.66 USD (1,107.35%) | 569,323.00 USD (1,138.65%) |
| Commission paid | 50,652.00 USD | 25,032.54 USD | 25,619.46 USD |

| Account | Value |
|---|---|
| Initial capital | 50,000.00 USD |
| Buy & hold return (TV-style, all capital at the first entry) | -2,861.49 USD (-5.72%) |
| Max equity run-up (intrabar) | 56,947.58 USD (113.90%) |
| Max equity drawdown (intrabar) | 84,570.74 USD (169.14%) |
| Open P&L | 0.00 USD |
| Max contracts held | 1 |

#### Trades analysis

| Metric | All | Long | Short |
|---|---|---|---|
| Total closed trades | 12,600 | 6,227 | 6,373 |
| Winning trades | 2,367 | 1,144 | 1,223 |
| Losing trades | 10,233 | 5,083 | 5,150 |
| Even trades | 0 | 0 | 0 |
| Percent profitable | 18.79% | 18.37% | 19.19% |
| Avg P&L | -2.58 USD | -5.28 USD | 0.06 USD |
| Avg P&L % | -0.00% | -0.00% | 0.00% |
| Avg winning trade | 460.73 USD | 455.26 USD | 465.84 USD |
| Avg losing trade | 109.74 USD | 108.93 USD | 110.55 USD |
| Ratio avg win / avg loss | 4.198 | 4.180 | 4.214 |
| Largest winning trade | 1,105.98 USD | 505.98 USD | 1,105.98 USD |
| Largest winning trade % | 3.91% | 3.66% | 3.91% |
| Largest losing trade | 314.02 USD | 254.02 USD | 314.02 USD |
| Largest losing trade % | 2.05% | 1.80% | 2.05% |
| Avg # bars in trades | 26 | 28 | 25 |
| Avg # bars in winning trades | 67 | 74 | 60 |
| Avg # bars in losing trades | 17 | 17 | 16 |

#### Risk/performance ratios

| Metric | Value |
|---|---|
| Sharpe ratio | -0.139 |
| Sortino ratio | -0.139 |
| Profit factor | 0.971 |
| Margin calls | 0 |


## By year

| Year | Trades | Net profit | % profitable | Profit factor |
|---|---|---|---|---|
| 2010 | 669 | -19,609.38 USD | 15.70% | 0.716 |
| 2011 | 1099 | 1,752.02 USD | 24.39% | 1.014 |
| 2012 | 1015 | -15,750.30 USD | 17.83% | 0.846 |
| 2013 | 988 | -32,911.76 USD | 13.06% | 0.646 |
| 2014 | 940 | -10,478.80 USD | 14.79% | 0.860 |
| 2015 | 988 | 3,158.24 USD | 20.24% | 1.035 |
| 2016 | 884 | 3,686.32 USD | 17.08% | 1.058 |
| 2017 | 842 | 6,735.16 USD | 15.44% | 1.150 |
| 2018 | 842 | 9,925.16 USD | 18.53% | 1.165 |
| 2019 | 768 | 3,522.64 USD | 17.32% | 1.065 |
| 2020 | 922 | -3,336.44 USD | 17.57% | 0.955 |
| 2021 | 901 | 11,357.98 USD | 21.31% | 1.151 |
| 2022 | 860 | 9,042.80 USD | 26.86% | 1.087 |
| 2023 | 882 | 454.36 USD | 21.54% | 1.005 |

## Audit counts

```json
{
  "bars": 4682668,
  "setups": 11153,
  "eligible_signal_bars": 25182,
  "orders_placed": 12722,
  "unfilled_orders_cancelled": 122,
  "pending_at_end": false,
  "nonpositive_initial_risk_closed_trades": 86
}
```

## Last trades

| Trade # | Type | Signal | Date/Time (UTC) | Price | Contracts | Profit | Cum. profit | Run-up | Drawdown |
|---|---|---|---|---|---|---|---|---|---|
| 12600 | Exit short | Daily close | 2023-12-28 21:59 | 72.04 | 1 | -134.02 USD (-0.19%) | -32,452.00 USD | 190.00 USD | 140.00 USD |
|  | Entry short | FSP | 2023-12-28 19:05 | 71.91 | 1 |  |  |  |  |
| 12599 | Exit short | FSP exit | 2023-12-28 18:57 | 72.00 | 1 | -14.02 USD (-0.02%) | -32,317.98 USD | 0.00 USD | 10.00 USD |
|  | Entry short | FSP | 2023-12-28 18:57 | 71.99 | 1 |  |  |  |  |
| 12598 | Exit short | FSP exit | 2023-12-28 18:47 | 72.07 | 1 | 495.98 USD (0.68%) | -32,303.96 USD | 500.00 USD | 50.00 USD |
|  | Entry short | FSP | 2023-12-28 18:02 | 72.57 | 1 |  |  |  |  |
| 12597 | Exit short | FSP exit | 2023-12-27 19:27 | 74.30 | 1 | -44.02 USD (-0.06%) | -32,799.94 USD | 340.00 USD | 40.00 USD |
|  | Entry short | FSP | 2023-12-27 19:14 | 74.26 | 1 |  |  |  |  |
| 12596 | Exit short | FSP exit | 2023-12-27 18:55 | 74.39 | 1 | -124.02 USD (-0.17%) | -32,755.92 USD | 10.00 USD | 120.00 USD |
|  | Entry short | FSP | 2023-12-27 18:53 | 74.27 | 1 |  |  |  |  |
| 12595 | Exit short | FSP exit | 2023-12-27 18:50 | 74.35 | 1 | -24.02 USD (-0.03%) | -32,631.90 USD | 40.00 USD | 20.00 USD |
|  | Entry short | FSP | 2023-12-27 18:49 | 74.33 | 1 |  |  |  |  |
| 12594 | Exit short | FSP exit | 2023-12-27 18:40 | 74.34 | 1 | -24.02 USD (-0.03%) | -32,607.88 USD | 80.00 USD | 20.00 USD |
|  | Entry short | FSP | 2023-12-27 18:36 | 74.32 | 1 |  |  |  |  |
| 12593 | Exit long | FSP exit | 2023-12-26 19:20 | 75.68 | 1 | -74.02 USD (-0.10%) | -32,583.86 USD | 390.00 USD | 70.00 USD |
|  | Entry long | FSP | 2023-12-26 18:31 | 75.75 | 1 |  |  |  |  |
| 12592 | Exit long | FSP exit | 2023-12-26 18:11 | 75.84 | 1 | -94.02 USD (-0.12%) | -32,509.84 USD | 30.00 USD | 90.00 USD |
|  | Entry long | FSP | 2023-12-26 18:07 | 75.93 | 1 |  |  |  |  |
| 12591 | Exit long | FSP exit | 2023-12-26 17:50 | 75.89 | 1 | -64.02 USD (-0.08%) | -32,415.82 USD | 230.00 USD | 60.00 USD |
|  | Entry long | FSP | 2023-12-26 16:58 | 75.95 | 1 |  |  |  |  |

## Artifacts

- [trades.csv](../../../results/failed_swing_point/first_default_mss15_2023_retry1/trades.csv)
- [summary.json](../../../results/failed_swing_point/first_default_mss15_2023_retry1/summary.json)
- [years.csv](../../../results/failed_swing_point/first_default_mss15_2023_retry1/years.csv)
- [setups.csv](../../../results/failed_swing_point/first_default_mss15_2023_retry1/setups.csv)
- [signals.csv](../../../results/failed_swing_point/first_default_mss15_2023_retry1/signals.csv)
- [orders.csv](../../../results/failed_swing_point/first_default_mss15_2023_retry1/orders.csv)
- [provenance.json](../../../results/failed_swing_point/first_default_mss15_2023_retry1/provenance.json)
- [counts.json](../../../results/failed_swing_point/first_default_mss15_2023_retry1/counts.json)
- [equity.png](../../../results/failed_swing_point/first_default_mss15_2023_retry1/equity.png)

This historical baseline is not out-of-sample validation. Tick-level fills and TradingView export parity are not established. An end-of-period open position is reported as open P&L, not force-closed.
