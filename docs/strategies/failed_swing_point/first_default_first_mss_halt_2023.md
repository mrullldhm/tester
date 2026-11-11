# FSP — Failed Swing Point: fixed default baseline

[Strategy specification](README.md). One fixed configuration; no parameter search or 30m comparison.

Data: **2010-06-07 00:00:00+00:00 to 2023-12-29 21:59:00+00:00**, 4,682,668 one-minute CL bars. End is exclusive 2024-01-01 UTC.

Settings: provisional 1H swings, 15m confirmation, both directions, New York entries 09:00–14:30 ET; one CL contract; maximum planned stop distance 25 ticks; TP 50 ticks from actual fill; $2.01/order; no added slippage.

Each failed 1H setup is eligible only at its first valid 1m MSS. At most one limit order per setup; no replacement attempt after cancellation, TP or SL. Busy-account signals are not deferred.

MSS eligibility ends on a post-confirmation touch of the breach candle's fixed 15m high (short) or low (long), including a touch within the signal minute before its close. Already-placed limits are unaffected by that boundary or by later 1H points. Pending limits cancel at New York entry-session end; New York close at 14:30 ET (or the earlier scheduled exchange close) cancels limits, flattens all positions and clears all setups. A new failed setup is required after reset. Roll exits apply.

Halt exception: if the scheduled cutoff has no tradable closing minute, cancel old orders and close the position at the OPEN of the first available reopening bar. Normal SL/TP fills before the cutoff remain valid. No price is backdated or fabricated.

## Results

#### Overview

| Metric | Value |
|---|---|
| Net profit | -11,925.96 USD (-23.85%) |
| Total closed trades | 3,198 |
| Percent profitable | 18.86% |
| Profit factor | 0.958 |
| Max equity drawdown | 30,453.76 USD (60.91%) |
| Avg trade | -3.73 USD |
| Avg # bars in trades | 21 |

#### Performance

| Metric | All | Long | Short |
|---|---|---|---|
| Net profit | -11,925.96 USD (-23.85%) | -17,695.72 USD (-35.39%) | 5,769.76 USD (11.54%) |
| Gross profit | 273,515.94 USD (547.03%) | 124,094.40 USD (248.19%) | 149,421.54 USD (298.84%) |
| Gross loss | 285,441.90 USD (570.88%) | 141,790.12 USD (283.58%) | 143,651.78 USD (287.30%) |
| Commission paid | 12,855.96 USD | 6,375.72 USD | 6,480.24 USD |

| Account | Value |
|---|---|
| Initial capital | 50,000.00 USD |
| Buy & hold return (TV-style, all capital at the first entry) | -2,861.49 USD (-5.72%) |
| Max equity run-up (intrabar) | 21,922.84 USD (43.85%) |
| Max equity drawdown (intrabar) | 30,453.76 USD (60.91%) |
| Open P&L | 0.00 USD |
| Max contracts held | 1 |

#### Trades analysis

| Metric | All | Long | Short |
|---|---|---|---|
| Total closed trades | 3,198 | 1,586 | 1,612 |
| Winning trades | 603 | 280 | 323 |
| Losing trades | 2,595 | 1,306 | 1,289 |
| Even trades | 0 | 0 | 0 |
| Percent profitable | 18.86% | 17.65% | 20.04% |
| Avg P&L | -3.73 USD | -11.16 USD | 3.58 USD |
| Avg P&L % | -0.00% | -0.01% | 0.01% |
| Avg winning trade | 453.59 USD | 443.19 USD | 462.61 USD |
| Avg losing trade | 110.00 USD | 108.57 USD | 111.44 USD |
| Ratio avg win / avg loss | 4.124 | 4.082 | 4.151 |
| Largest winning trade | 495.98 USD | 495.98 USD | 495.98 USD |
| Largest winning trade % | 3.91% | 3.66% | 3.91% |
| Largest losing trade | 314.02 USD | 254.02 USD | 314.02 USD |
| Largest losing trade % | 1.63% | 1.63% | 0.97% |
| Avg # bars in trades | 21 | 21 | 20 |
| Avg # bars in winning trades | 47 | 48 | 46 |
| Avg # bars in losing trades | 15 | 16 | 14 |

#### Risk/performance ratios

| Metric | Value |
|---|---|
| Sharpe ratio | -0.072 |
| Sortino ratio | -0.104 |
| Profit factor | 0.958 |
| Margin calls | 0 |


## By year

| Year | Trades | Net profit | % profitable | Profit factor |
|---|---|---|---|---|
| 2010 | 136 | -5,166.72 USD | 15.44% | 0.650 |
| 2011 | 254 | -2,231.08 USD | 23.62% | 0.925 |
| 2012 | 237 | -5,252.74 USD | 18.14% | 0.795 |
| 2013 | 248 | -13,256.96 USD | 11.29% | 0.474 |
| 2014 | 236 | -28.72 USD | 17.37% | 0.998 |
| 2015 | 239 | 1,769.22 USD | 21.34% | 1.080 |
| 2016 | 249 | 1,749.02 USD | 20.48% | 1.092 |
| 2017 | 259 | 138.82 USD | 14.29% | 1.009 |
| 2018 | 253 | 4,322.94 USD | 18.18% | 1.263 |
| 2019 | 225 | 3,575.50 USD | 19.56% | 1.227 |
| 2020 | 235 | -3,184.70 USD | 15.32% | 0.837 |
| 2021 | 222 | 1,137.56 USD | 20.27% | 1.060 |
| 2022 | 193 | 3,754.14 USD | 29.02% | 1.160 |
| 2023 | 212 | 747.76 USD | 20.75% | 1.036 |

## Audit counts

Independent raw CL execution replay checked all 3,198 trades: every entry/exit price and time matched,
net P&L matched to the cent, and no failed setup produced a repeated trade. The single halt exception
closed at 100.67 on 13 February 2012 at 15:15 New York time, the first reopening bar's open.
The audit uses supplied signals; it does not independently detect owner swings or establish TradingView parity.
[Independent audit](../../../results/failed_swing_point/first_default_first_mss_halt_2023/independent_audit.json).

```json
{
  "bars": 4682668,
  "setups": 11158,
  "eligible_signal_bars": 3296,
  "orders_placed": 3229,
  "unfilled_orders_cancelled": 31,
  "pending_at_end": false,
  "halt_reopen_exits": 1,
  "nonpositive_initial_risk_closed_trades": 24
}
```

## Last trades

| Trade # | Type | Signal | Date/Time (UTC) | Price | Contracts | Profit | Cum. profit | Run-up | Drawdown |
|---|---|---|---|---|---|---|---|---|---|
| 3198 | Exit short | FSP exit | 2023-12-28 18:47 | 72.07 | 1 | 495.98 USD (0.68%) | -11,925.96 USD | 500.00 USD | 50.00 USD |
|  | Entry short | FSP | 2023-12-28 18:02 | 72.57 | 1 |  |  |  |  |
| 3197 | Exit short | FSP exit | 2023-12-27 18:40 | 74.34 | 1 | -24.02 USD (-0.03%) | -12,421.94 USD | 80.00 USD | 20.00 USD |
|  | Entry short | FSP | 2023-12-27 18:36 | 74.32 | 1 |  |  |  |  |
| 3196 | Exit long | FSP exit | 2023-12-26 17:50 | 75.89 | 1 | -64.02 USD (-0.08%) | -12,397.92 USD | 230.00 USD | 60.00 USD |
|  | Entry long | FSP | 2023-12-26 16:58 | 75.95 | 1 |  |  |  |  |
| 3195 | Exit short | New York close | 2023-12-22 19:29 | 73.58 | 1 | 355.98 USD (0.48%) | -12,333.90 USD | 450.00 USD | 120.00 USD |
|  | Entry short | FSP | 2023-12-22 16:58 | 73.94 | 1 |  |  |  |  |
| 3194 | Exit long | FSP exit | 2023-12-21 16:22 | 73.82 | 1 | -84.02 USD (-0.11%) | -12,689.88 USD | 30.00 USD | 80.00 USD |
|  | Entry long | FSP | 2023-12-21 16:21 | 73.90 | 1 |  |  |  |  |
| 3193 | Exit short | FSP exit | 2023-12-20 17:55 | 74.14 | 1 | -14.02 USD (-0.02%) | -12,605.86 USD | 100.00 USD | 10.00 USD |
|  | Entry short | FSP | 2023-12-20 17:53 | 74.13 | 1 |  |  |  |  |
| 3192 | Exit long | FSP exit | 2023-12-20 14:17 | 74.94 | 1 | -54.02 USD (-0.07%) | -12,591.84 USD | 10.00 USD | 50.00 USD |
|  | Entry long | FSP | 2023-12-20 14:16 | 74.99 | 1 |  |  |  |  |
| 3191 | Exit long | FSP exit | 2023-12-19 14:02 | 72.82 | 1 | -134.02 USD (-0.18%) | -12,537.82 USD | 70.00 USD | 130.00 USD |
|  | Entry long | FSP | 2023-12-19 14:01 | 72.95 | 1 |  |  |  |  |
| 3190 | Exit short | FSP exit | 2023-12-18 18:58 | 73.03 | 1 | 495.98 USD (0.67%) | -12,403.80 USD | 500.00 USD | 20.00 USD |
|  | Entry short | FSP | 2023-12-18 18:33 | 73.53 | 1 |  |  |  |  |
| 3189 | Exit short | FSP exit | 2023-12-15 14:31 | 71.48 | 1 | 495.98 USD (0.69%) | -12,899.78 USD | 500.00 USD | 20.00 USD |
|  | Entry short | FSP | 2023-12-15 14:01 | 71.98 | 1 |  |  |  |  |

## Artifacts

- [trades.csv](../../../results/failed_swing_point/first_default_first_mss_halt_2023/trades.csv)
- [summary.json](../../../results/failed_swing_point/first_default_first_mss_halt_2023/summary.json)
- [years.csv](../../../results/failed_swing_point/first_default_first_mss_halt_2023/years.csv)
- [setups.csv](../../../results/failed_swing_point/first_default_first_mss_halt_2023/setups.csv)
- [signals.csv](../../../results/failed_swing_point/first_default_first_mss_halt_2023/signals.csv)
- [orders.csv](../../../results/failed_swing_point/first_default_first_mss_halt_2023/orders.csv)
- [provenance.json](../../../results/failed_swing_point/first_default_first_mss_halt_2023/provenance.json)
- [counts.json](../../../results/failed_swing_point/first_default_first_mss_halt_2023/counts.json)
- [equity.png](../../../results/failed_swing_point/first_default_first_mss_halt_2023/equity.png)

This historical baseline is not out-of-sample validation. Tick-level fills and TradingView export parity are not established. An end-of-period open position is reported as open P&L, not force-closed.
