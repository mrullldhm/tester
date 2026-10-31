# Plan: Supertrend + ATR trail + Kalman trend + volatility filter, M15 signals on CL1! 1m (r1, 2026-10-31)

> **Status:** built and tested. Codex review changed several points (docs/REVIEWS.md R6, R7); the code and
> `strategies/supertrend_kalman.py` ABOUT are the final spec. Final grid: 1,728 per variant (`st_factor` {2, 3},
> `vol` 6 values, `kalman_q` {0.01, 0.0001}). Results: docs/strategies/supertrend_kalman/README.md.

Owner request: Supertrend plus ATR trailing on M15, Kalman trend filter, a volatility filter so it does not trade
with a wide stop, stop at swing high / low, target RR 1:2 to 1:3. Feature 1 only (`cli test`), no feature 2.
Owner was unsure about every design fork and asked to **test all of them**, so each fork is a grid parameter or a
variant. Builder: Claude. Reviewer / replicator: Codex.

## Timeframe mapping (the main parity risk)
- Engine stays on 1m bars (fills, costs, intrabar path unchanged).
- M15 bars are built from 1m bars by flooring the UTC bar-open time to 15 minutes (CL Globex day starts 18:00 NY,
  a 15-minute boundary; TradingView HTF intraday bars align the same way for CL). Missing 1m bars: the bucket is
  built from the bars that exist. O = first open, H = max, L = min, C = last close.
- Non-repainting access, the Pine twin uses `request.security(syminfo.tickerid, "15", expr[1],
  lookahead = barmerge.lookahead_on)`: the value of the last **completed** M15 bucket. In Python: an M15 value of
  bucket k is visible from the first 1m bar of any later bucket. A signal on bucket k is acted on at the close of
  the first 1m bar of the next bucket, so the market entry fills at the open of the following 1m bar
  (normally hh:01 / :16 / :31 / :46). One minute later than a native 15m chart; accepted for twin parity.
- All M15 indicators computed over every M15 bucket (Pine runs every bar).

## Indicators (M15, Pine-exact)
| Name | Definition | Params |
|---|---|---|
| Supertrend | `ta.supertrend(factor, atr_len)` (hl2 bands, ATR = RMA of TR, band ratchet, Pine direction rule) | `st_factor`, `atr_len` = 10 |
| ATR trailing stop (UT Bot) | `nLoss = trail_mult * ta.atr(atr_len)`; classic recursion on close: rising above prev stop keeps `max(prev, c - nLoss)`, falling `min(prev, c + nLoss)`, cross resets | `trail_mult` |
| Kalman trend | 2-state constant-velocity Kalman filter on close (state = level, slope). Trend = sign of slope estimate. Q = q * [[1/4,1/2],[1/2,1]] style (discrete white-noise acceleration), R = 1, init from first close, P0 large | `kalman_q` (one value, maybe 2) |
| ATR | `ta.atr(14)` on M15 (for volatility filters) | |
| Swings | M15 pivot high / low, `strength` bars each side (Pine `ta.pivothigh/low`, strict as `buffer_pivots`), last confirmed value carried forward | `swing` |
| RVI | TradingView Relative Volatility Index: stdev(close, 10), EMA 14 of up / down stdev, `100 * up / (up + down)` | |

## Entry trigger (`trigger`, grid)
All need Kalman slope in the trade direction at the signal bucket.
- `st_flip`: Supertrend direction flips (to up for long, down for short).
- `trail_flip`: ATR trail flips into the side of the current Supertrend direction (Supertrend = trend, ATR trail = timing).
- `both`: Supertrend and ATR trail both point the same way; signal on the bucket where the second of them flips.

## Stop and target
- Stop: last confirmed M15 swing low (long) / swing high (short) at the signal bucket. No trade if that level is
  on the wrong side of the signal close or missing.
- Risk R = |signal close - stop| in ticks. Target = `rr` x R in ticks from the actual fill (Pine `profit=`), `rr` in {2, 3}.
  Stop is an absolute price (`stop=`), as fair_price_reversal.

## Volatility filter (`vol`, grid; "so it does not trade with a wide stop")
| Value | Rule at the signal bucket |
|---|---|
| `none` | no filter (control) |
| `stop_atr:X` | skip if R > X x ATR14(M15). X in {1.5, 3.0} |
| `atr_ratio:X` | skip if ATR14 / ATR100 (M15) > X. X in {1.0, 1.3} |
| `rvi` | long only if RVI > 50, short only if RVI < 50 (directional volatility, not a width filter; tested because the owner named "volatility index") |
CBOE OVX (crude oil VIX) is **not** tested: not in the repo, would need new data (cost quote first).

## Exit (`exit`, grid)
One `strategy.exit` id per entry (engine limit), amended in place.
- `fixed`: swing stop + RR target, nothing else.
- `trail`: same bracket, stop amended each new M15 bucket to the ATR trail level when it is tighter than the
  current stop (never loosens). Target unchanged.
- `flip`: fixed bracket, plus `close_all` when Supertrend flips against the position (market at next 1m open).

## Hours (`VARIANTS`)
| Variant | Entries | Forced flat |
|---|---|---|
| `all` | any time | none (only the owner roll exit). Holds through the daily 17:00-18:00 NY halt and weekends |
| `asia` / `london` / `ny` | signal inside the `sessions.py` session [open, flat - 1 min) | close_all after flat time, as fair_price_reversal |

## Grid (draft; sized after an engine-speed benchmark)
`trigger` 3 x `vol` 6 x `exit` 3 x `rr` 2 x `swing` {3, 5} x `st_factor` {2, 3} x `trail_mult` {1, 2} = 864 per variant,
4 variants. Indicator arrays cached on `Bars` per parameter so combinations share them. Report says best of 864.

## Deliverables
`strategies/supertrend_kalman.py` (GRID / VARIANTS / TITLE / ABOUT / CONCLUSION), `strategies/supertrend_kalman.pine`
twin, `tests/test_supertrend_kalman.py` (indicator vs literal bar-by-bar Pine transcription, M15 no-look-ahead test,
trail never loosens, vol filter vetoes), results doc from `python -m tvtester.cli test supertrend_kalman`.
Codex: review this plan, then the code (hashed pytest log), then replicate the top combination independently.

## Open questions for Codex
1. Is `expr[1]` + `lookahead_on` on a 1m chart exactly "last completed 15m bucket" on historical bars, including
   missing 1m bars and the daily halt? Better alternative?
2. Does TradingView align 15m buckets for NYMEX:CL1! to UTC 15-minute boundaries (session 18:00 NY)?
3. Kalman definition: anything more standard on TradingView for "Kalman trend"?
4. Look-ahead or Pine/Python mismatch risks in the trail-amend and flip exits.
5. Grid size vs in-sample bias: cut anything?
