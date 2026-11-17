# Independent review: 4H PDL swing count

## Frozen interpretation (before the count)

This is a descriptive frequency study, not a trade backtest. One fixed interpretation; no parameter search.
The draft README supplied the hypothesis before execution. User scope permits only this review, the independent
counter and its output; no ledger or other files are changed. The independent counter does not read/import
`studies/pdl_swing_4h/run.py` or its event output.

The main denominator follows the draft: a low accepted at candle c2 in `detect`'s snapshot after processing c2,
with `sl_candle == c2` and `newest == LOW`. That snapshot becomes known only at **c3 close**, not c2 close.
A replacement at a later candle is a separate event; no retroactive removal. Require completed c3 and c4 in the
same dev/validation partition as c2; censored lows are excluded, not labelled failures. Period/year belong to c2.
The swing detector runs continuously across the dev/validation boundary, using past dev state for validation.

PDL is the previous **observed CME trading day's** minimum 1m low, fixed using c2's trading day. Both SH0 and SL
are compared with that same level, even if SH0 belongs to an older day. C1: SH0 > PDL and SL <= PDL. C2:
SL > PDL with a known SH0 and PDL. Other: all remaining cases, including unavailable reference information.
Touches are inclusive and comparisons use integer ticks.

C3 requires c4.low <= c2.low and c4.high < c3.high, and the actual snapshot processing c3 (known at c4 close)
must have newest SH on c3 and retain SL on c2. Thus the mandatory swing engine, including rule 4, establishes
c3's identity. C4 requires c3.high >= c2.high and both c4 threshold hits, with first touch of c3.high before
first touch of c2.low. It is explicitly a **provisional high candle shape**, not a confirmed swing setup.
C4 unknown order means the first hits share a 1m bar whose open cannot resolve order. Both-hit low-first is
`none`. The four shape columns partition the low-event denominator; `all` is the sum of the other three groups.

## Critique of the draft

1. **The clarified PDL condition is correctly represented by C1.** It compares successive swing points;
   requiring c2 itself to straddle PDL would be wrong. A downward gap from SH0 above to SL below still qualifies.
   Equality belongs on SL's side; SH0 equal to PDL is not "above".
2. **C2 versus other needs an explicit convention.** Literal negation of the clarified crossing predicate
   includes structures already below PDL. The draft instead reserves C2 for SL > PDL and separates already-below
   as other. This is useful reporting, but it is narrower than interpreting "does NOT touch/break" as simply
   not C1. Its informal `other = SH0 <= PDL` row can also overlap C2 in unusual structures and omits unavailable
   PDL/SH0. Use the exhaustive decision order above; C2 + other is the complement of C1.
3. **A low event is not automatically the requested completed short setup.** "Recent swing low and swing high"
   does not specify a lookback, expiry, or denominator. The four consecutive observed candles define recency for
   shapes here; `all` also includes low events with no ensuing high/trigger. Report shape counts and denominators
   separately. A count of pairs of swings with arbitrary candle spacing would answer a different question.
4. **Timing and replacements must remain point-in-time.** A c2 low is known at c3 close, and a c3 high only at
   c4 close. Historical c4 action cannot be traded using c3's confirmed swing identity. Rule-5 replacements count
   separately here; an alternative is one event per low transition, but that is not this denominator. Later
   removals by rules 4/5 must not rewrite earlier observations. Do not use the final point stack.
5. **The C3 inequalities are only a local candidate test.** Rule 4 can reject a c3 candidate or remove c2.
   Check the actual c3 snapshot as well. Conversely, do not require c2 to survive processing c4: that processing
   needs c5 and would add an unrequested lookahead. c4's break is allowed to invalidate/replace the low later.
6. **C4 contradicts rule 3, including an exact touch.** c4.high >= c3.high prevents c3 being a confirmed swing
   high. No implementation can simultaneously satisfy all of that wording and the mandatory swing rule.
   The draft's separate candle-shape interpretation is reasonable, provided its counts are never presented as
   confirmed swing-high setups. Also, c4 does not automatically "take over" as a swing high: it needs c5 and
   the full structure rules. Whether c4 ultimately becomes SH/SL is a separate, longer-horizon question; it is
   not necessary to count this four-candle request and is not included here.
7. **Order means first threshold touches, not the final high/low order.** c4 can touch c3.high, then c2.low,
   then make its ultimate high. `cd.high_first[c4]` would misclassify that as low-first. Scan 1m highs/lows for
   first hits at the two setup prices. Same-minute hits usually remain unknown; if the minute opens at/above
   the upper threshold, high-first is known, or at/below the lower threshold, low-first is known. Do not infer
   order from candle colour. This threshold test differs intentionally from swing outside-candle ordering,
   where the owner has specified how unresolved extreme order continues the existing structure.
8. **Outside candles affect the denominator.** c2 can contain both accepted swing points. The draft's
   `newest=LOW` admits high-then-low c2 but excludes low-then-high c2, even when the low remains in state.
   That restriction is a choice, not explicit owner wording; it is retained for the main table and audited.
   c3 cannot also be a local swing-low candidate: confirmation of c2 requires c3.low > c2.low. c4 can
   be an outside candle, and its threshold-hit order remains separate from the swing detector's extreme-event
   order. Never impose a new pivot method or manually override the owner's unknown-order fallback.
9. **Choose one day's PDL for the whole comparison.** Use c2's day, not c4/confirmation day, UTC day, or
   Malaysia calendar day. If SH0 is on an earlier day, compare its price with c2's PDL, rather than comparing
   each point to a different moving level. This is a fixed-level crossing condition; it does not assert that
   the entire SH0-to-SL transition occurred while that level was the live PDL. Restricting SH0 to c2's day or
   freezing PDL on SH0's day would be separate studies.
10. **Sessions, weekends and missing bars need rules.** Previous means previous observed trading session,
    e.g. Monday normally uses Friday. Holidays are not zero-price days. Entire missing sessions in the source
    would silently make this an older reference; no exchange-calendar completeness guarantee is claimed.
    c1..c4 are adjacent observed 4H candles across session/weekend gaps, not four equal elapsed-time blocks.
    The final daily block is only three scheduled hours. Preserve the repo's 17:00 CT alignment and DST.
    A block with a missing final minute completes at the next observed bar; it remains assigned to its own
    bars' trading day, not `avail`'s day. Include such blocks and audit delayed completions rather than quietly
    imposing a new session filter. Gaps count as observed threshold reaches; absent minutes have no invented path.
11. **Boundary limits matter.** A UTC-date load can begin after the opening of its first CME session, leaving
    its first daily low partial and affecting the next day's PDL. Here the actual first available bar is
    2010-06-07 00:00 UTC, already inside that CME session. No padding is added because the user prescribed
    the load. The first observed day has no PDL and goes to other.
    Swing history also has no pre-window warmup. The end omits unfinished candles; exclude insufficient future
    horizon at each partition boundary. These counts are conditional on available data, not exact calendar-wide
    opportunity rates. Unadjusted contract changes are included as required by the swing library, so roll gaps
    can contribute threshold crossings.

## Results

The single frozen run loaded **5,031,811 1m bars**, forming **22,401 completed 4H candles**. Actual UTC
coverage is 2010-06-07 00:00 through 2024-12-31 21:59. All research rows have trading_day < 2025-01-01.
These are **in-sample descriptive counts**, including the period named validation; there are no performance
claims or tuned variants. Validation was evaluated once under the frozen conventions above.

| Period | Group | C3 | C4 | C4 unknown order | none | Total |
|---|---|---:|---:|---:|---:|---:|
| dev (2010-06..2021) | all | 209 | 84 | 0 | 2,932 | 3,225 |
| dev | C1 PDL cross | 68 | 19 | 0 | 1,418 | 1,505 |
| dev | C2 no PDL | 141 | 65 | 0 | 1,499 | 1,705 |
| dev | other | 0 | 0 | 0 | 15 | 15 |
| validation (2022..2024) | all | 55 | 38 | 0 | 738 | 831 |
| validation | C1 PDL cross | 21 | 7 | 0 | 364 | 392 |
| validation | C2 no PDL | 33 | 31 | 0 | 372 | 436 |
| validation | other | 1 | 0 | 0 | 2 | 3 |

For the PDL-cross setup specifically, dev has **68 confirmed C3** and **19 provisional C4** shapes;
validation has **21 confirmed C3** and **7 provisional C4** shapes. C4 cannot be called a confirmed
swing-high setup under the current owner rule. Zero unknown-order observations is an empirical result;
the implementation retains that category.

Audit across both periods:

- 150 accepted low events were excluded because the same candle ended newest=HIGH (the draft's outside-candle restriction).
- 1 newest-low event was censored for insufficient horizon or crossing the dev/validation boundary.
- 0 local C3 shapes were rejected by the stronger actual-structure check, so that tightening did not change this sample's C3 count.
- 40 both-threshold candle shapes were low-first and therefore `none`.
- 2,364 counted low-event windows spanned multiple trading days; 767 had c3 or c4 completion delayed into a later session.

The saved output includes all per-year tables and raw-bar checks. For example:

- C1/C3, c2 open 2010-08-23 22:00 UTC: SH0 74.48, PDL 72.67, c2 low 72.54;
  c3 high 73.05, c4 high 72.81 and low 72.02.
- C1/C4, c2 open 2010-08-31 06:00 UTC: SH0 75.59, PDL 74.01, c2 low 73.38;
  c3 high 74.57; c4 first touches the high threshold at 14:00 UTC, then the low threshold at 15:32 UTC.
  c4's full range is 74.75 / 72.30.

Verification: the counter asserts group partitioning and checks spot-sampled candle extremes against their
underlying 1m bars. Six separate synthetic checks cover high-first, low-first, unresolved same-minute hits,
same-minute hits resolved by the opening price in either direction, and missing hits. Ruff passes;
all **51 swing/indicator regression tests pass**.

## Owner's 16 November 2026 example

The separate call `load_bars("2026-11-01", "2026-11-18")` was made solely for this check; these bars never
enter the historical tables. The requested Malaysia opens are 07:00, 11:00, 15:00 and 19:00 on November 16
(UTC: November 15 23:00; November 16 03:00, 07:00, 11:00). Those align with the repository's 4H blocks
in November (CT standard time).

**Classification is unverifiable from the local dataset.** Its last available bar is 2026-11-13 11:22 UTC
(19:22 Malaysia), before all four candles. The counter explicitly reports the missing example rather than
inventing a classification. No paid download was attempted. The example check is implemented and will print
its candles, group, shape, and first threshold-hit timestamps when those bars become available.

Artifacts: [independent counter](../../../studies/pdl_swing_4h/codex_count.py),
[complete saved output](../../../studies/pdl_swing_4h/codex_counts.txt).
Reproduce with `.venv/bin/python -m studies.pdl_swing_4h.codex_count > studies/pdl_swing_4h/codex_counts.txt`.

