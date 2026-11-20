# Swing point rule (owner, mandatory)

Every strategy, study or chart that uses swing points uses `cltester/swings.py`. No other pivot method, no
adjustable swing settings. Tests: `tests/test_swings.py`.

## Owner rules (2026-11-12)

| # | Rule |
|---|---|
| 1 | Swing points alternate: low, high, low, high … |
| 2 | Swing low at candle k: left candle low ≥ low[k] (equal allowed) and right candle low > low[k] (strict). |
| 3 | Swing high at candle k: left candle high ≤ high[k] (equal allowed) and right candle high < high[k] (strict). |
| 4 | A swing low is the lowest price of the whole transition between the swing highs around it (every candle counts, not only candidates). Swing high: mirror. Example: SH 70, SL 68, SH 71 or 69: 68 is the lowest price between the two highs. |
| 5 | A second low with no swing high between: lower replaces the first; higher is not a swing low. Swing high: mirror. |
| 6 | A point must meet 1, 2/3, 4 and 5 together. |

## Owner answers to edge cases (2026-11-12)

- **Equal lows** (or equal highs) with no opposite point between: the **later** one is the swing point.
- **A candle can be both** swing low and swing high (outside candle) when both rule 2 and rule 3 hold. Its two
  prices count in the order they printed:
  - higher timeframes: the order of the 1-minute bars inside it (first 1m bar that printed the high vs the low);
  - unknown order (a 1-minute candle, or both prices in the same 1m bar): **continue the order**: after a swing
    high its low comes first, after a swing low its high. Use the other order if rule 4 removes the existing last
    point in the default order. The usual rules still apply to both points in the other order.
- **Rule 4 vs rule 2**: when the lowest candle fails rule 2 because its right candle has an equal or lower low,
  the right candle is the lowest price. When the candle after it has a higher low and a lower high, that right candle
  is the swing low and the swing high (owner example, tested).
- When no candle meets rules 2 and 4 together between two swing highs, there is no swing low between them: the two
  highs merge and rule 5 keeps the higher one.

## Outside-candle touch invalidation

When an outside candle gives a swing low followed by a swing high, a later touch or break of that high removes it
while it is still the newest swing point. The swing low stays in place at the touch. A new high still needs its own
right candle and must pass the swing rules. The rule mirrors for a swing high followed by a swing low.

## Timing (no look-ahead)

- A candidate at candle k is known when candle k+1 **closes**.
- The newest point can still be replaced (rule 5) or removed (rule 4 or the outside-candle touch rule) by later
  candles. Earlier points can be removed only through rule 4 (rare).
- `swing_state(df, tf)`: per 1m bar, the last swing high and swing low **as known at that bar's close**. Use it for
  signals; `prev=True` adds the swing high and low before them (`{tf}_sh2`, `{tf}_sl2`); `newest=True` adds `{tf}_newest`
  (1 swing high, −1 swing low, 0 none): which point came last, also when one candle is both. `swing_points(df, tf)` is the final structure after all data: charts and studies only.
- An unfinished candle cannot confirm a swing. Its price can invalidate the newest outside-candle swing point at
  the close of the first 1m bar that reaches its level. If that bar also makes the prior candle available after a
  gap, the touched point is omitted from that close's published state.
- Every update publishes the latest swing high and low still in the structure. If a removal exposes an older
  point, that point becomes current again. A side with no remaining point shows as empty (NaN).

## Timeframes

`1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mo`, built from the 1m bars. 5m to 1h follow the clock. 4h blocks start at the
17:00 CT session open. 1d is the CME trading day. 1w is the Monday-to-Friday trading days (Sunday evening belongs to
Monday). 1mo is the trading days of one calendar month (named `1mo`, never `1M`, so it cannot be misread as 1m).
1w and 1mo are complete at the 15:59 CT close of their last trading day (the exchange calendar is known ahead). A candle is complete at the close of its last minute (4h: 20:59, 00:59,
04:59, 08:59, 12:59 CT; the day's last 4h block and the daily candle: 15:59 CT, the last minute before the halt).
If that minute has no bar (early-close holidays, quiet minutes), it is complete at the close of the next bar. Swings
continue across contract changes (prices are not back-adjusted).

## Audit on 2024 CL data

The audit checked 148,873 swing points across all nine timeframes for alternation, candidate inequalities,
recorded order when both points came from one candle, and the highest high or lowest low in each completed
transition. It also checked that all 72 truncated-data snapshots matched the same minutes in the longer run.
