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
    high its low comes first, after a swing low its high. If that order would break rule 4 for the existing last
    point, the other order is used (that order is the only one where the structure holds).
- **Rule 4 vs rule 2**: when the lowest candle fails rule 2 because its right candle has an equal or lower low,
  the right candle is the lowest price. When the candle after it has a higher low and a lower high, that right candle
  is the swing low and the swing high (owner example, tested).
- When no candle meets rules 2 and 4 together between two swing highs, there is no swing low between them: the two
  highs merge and rule 5 keeps the higher one.

## Timing (no look-ahead)

- A candidate at candle k is known when candle k+1 **closes**.
- The newest point can still be replaced (rule 5) or removed (rule 4) by later candles. Earlier points can be
  removed only through rule 4 (rare).
- `swing_state(df, tf)`: per 1m bar, the last swing high and swing low **as known at that bar's close**. Use it for
  signals; `prev=True` adds the swing high and low before them (`{tf}_sh2`, `{tf}_sl2`). `swing_points(df, tf)` is the final structure after all data: charts and studies only.
- An unfinished candle is ignored until it is complete, so it can never act as a right candle.
- Every update publishes the full state. A point removed by rule 4 shows as empty (NaN) from that bar on. An old
  level is never carried forward after it was removed.

## Timeframes

`1m, 5m, 15m, 30m, 1h, 4h, 1d`, built from the 1m bars. 5m to 1h follow the clock. 4h blocks start at the 17:00 CT
session open. 1d is the CME trading day. A candle is complete at the close of its last minute (4h: 20:59, 00:59,
04:59, 08:59, 12:59 CT; the day's last 4h block and the daily candle: 15:59 CT, the last minute before the halt).
If that minute has no bar (early-close holidays, quiet minutes), it is complete at the close of the next bar. Swings
continue across contract changes (prices are not back-adjusted).

## Checked on 2025 data

1m 113,345 points, 5m 24,459, 1h 1,876, 4h 470, 1d 94: zero order breaks, zero rule 2/3 breaks, and no lower low
(higher high) inside any transition. 1m detection takes about 1 s per year.
