# Study: what changed for fixed levels after 2021

A study, not a strategy. `purple_levels` (fixed levels: previous day, previous week, 4h and daily swing points) had a
real edge on 2010-2021 that survives strict fills, then made money in only 1 of 3 years on 2022-2024. Question:
**is the level edge gone, or paused by a market regime, and what in the price action changed?**

## Data
CL 1m bars, trading days 2010-06 to 2024-12 (dev + validation). Validation is already spent for the level
strategies (two validation runs); this study reads it descriptively. **Holdout (2025+) is not loaded.**

## Events
On 5m candles, per trading day, the four level sets of `purple_levels` fixed at the 17:00 CT open (`pd`, `pw`,
`sw4h`, `sw1d`). A level is armed as in `purple_pa` (price on one side at the day's open, or a later candle wholly
on one side). Event = the **first touch** of each armed level per day (support from above, resistance from below),
at the first 1m bar that reaches it. Highs and lows only.

## Outcome (symmetric, so the random-walk rate is 50%)
Scale X = 10% of the previous trading day's range (high − low, ticks; at least 3 ticks). From the 1m bar after the
touch: **bounce** = price trades X beyond the level on the side it came from, before trading X through it (strict).
Ties in one 1m bar and resolutions after the day ends or across a roll are left out.

## Measured per calendar year (2010-2024), all level sets and per set
- n, bounce rate, edge vs 50%, z.
- Market context from highs/lows only: median daily range (ticks), share of days that take out the previous day's
  high or low.
- Touch character: how far the touch 1m bar went through the level (in X units), and whether `purple_pa`'s gap
  (3-candle gap away from the level within 4 candles) followed; bounce rate given a gap.

## What would answer the question
- Bounce edge positive every year 2010-2021 and ~0 in 2022-2024, unrelated to daily range: the edge is gone.
- Bounce edge tracks the range regime (e.g. weak in high-range years such as 2022, back when range normalises):
  paused by regime; a range filter becomes a declared hypothesis for a new strategy (dev only).
- Bounce edge still there in 2022-2024 but the gap entry no longer captures it: the entry is the problem, not the
  level.

No trading, no ledger rows. Results: `studies/level_regime/findings.md`.
