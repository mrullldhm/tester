# Elliott Wave: pre-registered chance checks (declared 12 November 2026, before any run)

Background and rationale: [`docs/research/elliott_wave/README.md`](../../../research/elliott_wave/README.md)
section 5. This is a **gate before optimisation**: no P&L tuning, no parameter search. Each hypothesis has
fixed rules, written here before the first run. Script: `tools/elliott_chance.py`.

## Question

Does the hypothesis's wave count predict the next move better than a random walk, after a limit fill?

## Metric (objective)

For every setup, simulate the limit order on 1-minute bars and measure the gross outcome in ticks:
`(exit - fill) x direction`, exits at the stop S, the target T, or the session end. Under a driftless random
walk this has expectation **exactly 0** for any stop / target / time cut (optional stopping), so 0 is the
null. Costs are not subtracted; the pass bar includes them.

- **Pass:** mean >= **0.4 tick** (the $4.02 round trip) **and** day-clustered t >= **3.0**, pooled over the
  three sessions. Both required. t >= 3 because 15 tests are run (about a 0.002 one-sided level each).
- Day-clustered t: sum outcomes per (session, local day), t = mean of those sums / (sd / sqrt(days)) scaled
  to the per-trade mean sign. Overlapping setups are allowed; clustering keeps them from inflating t.
- Also reported (descriptive, not pass criteria): setups, fill rate, top-first rate vs its random-walk
  expectation (lim - S) / (T - S), unresolved share, per session.
- H4 stop: the wave-4 low itself (a touch exits).

## Budget

**15 tests**: 5 hypotheses x 3 degrees (1m, 5m, 15m). No other variants, no reruns with changed numbers.
A failed hypothesis is not re-tuned; a passed one goes to a strategy run that is declared separately.

## Common rules

- Data: development interval only (bars before 2024-01-01 UTC). 2024+ reserved.
- Sessions asia / london / ny (docs/SESSIONS.md). Decision bar inside [open, flat - 1 min) local time.
- Degree: series = 1m bars, or closed 5m / 15m candles (`tvtester.swings.candles`); a decision is made at the
  1m bar where that candle is known closed.
- Swings: owner rule only. 1m: the `Zig` replay of `tvtester/swings.py` (exact). 5m / 15m: the same `Zig`
  replayed per closed candle (pivots, then removal by the candle's range). This is a research
  approximation of `timeframe_state` (removal is not shown at the first touching 1m close inside the
  candle); its agreement with `timeframe_state` at candle closes is measured and reported.
- AO on the series: 34 x sum5(h + l) - 5 x sum34(h + l) (ticks, exact). AO window = 120 series bars.
- Minimum defining leg (wave 3 or wave 1): 20 ticks. rnd = round half up.
- Order: limit at the decision close or better level, working from the next 1m bar. Long fill when low <=
  limit, at min(open, limit). Before the fill it is cancelled at a 1m close that finds T touched, at the
  session end, or by a hypothesis cancel rule.
- After the fill: on the fill bar only S counts (conservative). Later bars: S and T in one bar = S
  (conservative); gaps fill at the open. Unresolved at the session end: the close of the first bar
  outside the session window.
- Long described; short is the mirror. T = one tick beyond the reference extreme.

## Hypotheses

| # | Name | Setup (long) | Limit | Stop S | Target T |
|---|---|---|---|---|---|
| H1 | AO count by degree | Current strategy rules on the series: tallest AO peak of the window, green, taller than the deepest red, in the current hump; AO crosses below zero; top = hump high = current owner swing high; base = window low; L = top - base >= 20 | min(top - rnd(0.382 L), close) | top - rnd(0.618 L); skip if already touched | top + 1 |
| H2 | GET Type 1 filters | H1, plus cancel the unfilled order at a series close when AO < -0.40 x the wave-3 AO peak (1.40 rule), or when the wave-4 speed (top - low since top) / series bars since top exceeds the wave-3 speed L / series bars from base to top (PTI proxy; the real PTI is proprietary). Reward/risk >= 1.5 is implied by the levels | as H1 | as H1 | as H1 |
| H3 | Orthodox hard rules, no AO | Owner pivots L0 < H1, L2 > L0 (W2 < 100 %), H3 > H1, W3 = H3 - L2 >= 1.618 x W1 (Neely extension; W3 not shortest), W3 >= 20, decision when L4 (wave 4 low) is first accepted, low since H3 > H1 (no overlap) | min(H3 - rnd(0.382 W3), close); skip unless > H1 | H1 (wave-1 territory) | H3 + 1 |
| H4 | Confirm wave-4 end, then limit | H1 setup without placing the order; then the first series close where AO recrosses >= 0, inside the session, with the low since top above top - rnd(0.618 L) and no new high since top | the recross close | lowest low since top (wave-4 low) | top + 1 |
| H5 | Wave 3 from wave 2 (1-2) | Owner pivots Hp, L0, H1, L2: H1 > Hp (wave 1 breaks the prior swing high), W1 = H1 - L0 >= 20, decision when L2 is first accepted, L2 > L0 | min(H1 - rnd(0.618 W1), close); skip unless > L0 | L0 (wave-1 origin) | H1 + 1 |

## Ledger

Every check run appends one line per test to `results/elliott_wave/ledger.jsonl` (`kind: chance_check`),
with the hypothesis, degree, metric values, data hash and script hash.

## Results (run 12 November 2026, definitions unchanged)

**0 of 15 pass.** Development interval, gross ticks per filled setup (cost = 0.4 tick).

| Hyp | Degree | Setups | Filled | Mean ticks | t (day-clustered) | Top-first | RW expected | Unresolved | Pass |
|---|---|---|---|---|---|---|---|---|---|
| H1 | 1m | 4005 | 3071 | -0.685 | -1.70 | 0.264 | 0.326 | 0.103 | no |
| H2 | 1m | 4005 | 1629 | -0.562 | -1.12 | 0.239 | 0.293 | 0.070 | no |
| H3 | 1m | 22135 | 13143 | 0.036 | 0.20 | 0.406 | 0.422 | 0.036 | no |
| H4 | 1m | 2419 | 2357 | -1.263 | **-3.60** | 0.455 | 0.505 | 0.051 | no |
| H5 | 1m | 125405 | 62810 | 0.331 | **3.83** | 0.349 | 0.354 | 0.030 | no (mean < 0.4) |
| H1 | 5m | 667 | 510 | -1.061 | -0.67 | 0.155 | 0.316 | 0.310 | no |
| H2 | 5m | 667 | 372 | -1.554 | -0.85 | 0.151 | 0.296 | 0.255 | no |
| H3 | 5m | 7899 | 4509 | -0.364 | -0.79 | 0.343 | 0.415 | 0.132 | no |
| H4 | 5m | 331 | 326 | -1.420 | -0.83 | 0.402 | 0.548 | 0.279 | no |
| H5 | 5m | 54337 | 26332 | 0.126 | 0.69 | 0.302 | 0.355 | 0.125 | no |
| H1 | 15m | 198 | 90 | -3.711 | -0.83 | 0.044 | 0.324 | 0.633 | no |
| H2 | 15m | 198 | 57 | -7.877 | -1.40 | 0.053 | 0.292 | 0.509 | no |
| H3 | 15m | 3108 | 1683 | -0.685 | -0.70 | 0.263 | 0.420 | 0.295 | no |
| H4 | 15m | 108 | 107 | 3.813 | 1.10 | 0.299 | 0.515 | 0.561 | no |
| H5 | 15m | 22277 | 10071 | 0.239 | 0.68 | 0.219 | 0.357 | 0.312 | no |

Tool checks: H1 on 1m reproduces the strategy's 4,005 setups exactly; 0 pivot-list mismatches; candle-level
swing replay agrees with `timeframe_state` at 99.81 % (5m) / 99.91 % (15m) of candle closes.

Reading:
- In 14 of 15 tests the target is reached first **less** often than a random walk would reach it. No count
  predicts the wave it names. The one exception, H4 15m, rests on 107 trades with t = 1.1.
- H4 1m (confirmation entry) is significantly **negative**: after AO recrosses zero, short-term moves revert.
  This matches the < 30-minute mean reversion in the literature.
- H5 1m is the only significant positive result, but below the cost bar (0.33 < 0.4 tick). Its top-first rate
  equals the random walk (0.349 vs 0.354), so the gain does not come from the wave count reaching its target.
  Most likely it comes from the outcome mix (gap fills better than the limit, session-end exits); this split
  was not measured separately. Not a wave edge.
- Per the declaration, no hypothesis is re-tuned. Ledger: 15 `chance_check` lines.
