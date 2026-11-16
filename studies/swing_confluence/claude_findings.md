# Claude findings: swing confluence study (dev, in-sample)

## 0. Round 2 (2026-11-16, after the Codex audit): repaired table, cross-check

Codex's audit (`codex_audit.md`) found 8 defects; all fixed in `build.py` / `cltester/swings.py` / `cltester/data.py`:
restored points counted as new events (21,527 rows, now removed: exact match), wrong rule-5 flag (now: no opposite
point after the previous same-side point), fair rate now strict-tick `(c-L+1)/(H-L+2)` and NaN when the
confirmation close is outside [L, H] (170,105 events), elapsed clock minutes, symmetric trend codes with 4 = equal
high/low, explicit missing levels (no price-sign tests), 1w/1mo completion from the scheduled calendar day (a live
prefix now matches full history; Codex's 2016-01-15 and 2016-07-29 examples checked), dev no longer reads 2022.

Repaired results (best of 724 single + 13,640 pair cells):
- Unconditional edge still ~0 on every base (−1.1 to +0.4 points). The 1m "findings" of round 1 vanish under the
  strict-tick fair rate: they were tick rounding, as Codex said.
- Only 1h swings confirmed at 17:00 CT pass alone (−5.2 points, n 1,170).
- 17 pair cells pass (20 before the Codex review of 2026-11-16 added the declared ≥ 9/12 same-sign years gate to
  `pairs.py`; it had been missing, 3 cells failed it). Survivor from round 1 (9/12 years): **15m swing in the top third of the 1h range with the 15m leg against:
  −6.8 points** (n 607, both halves, shorts −10.1). An avoid filter, not an entry.
- **Codex A replicates** on the repaired table (Codex code vs Claude code, same definition: a replication, not an
  independent discovery): 1h swing, slow transition (> 5 clock minutes per tick from the opposite point's candle),
  4h leg with: +3.7 points (n 1,796), shorts +4.8 points 12/12 years. Slow alone: +2.3.
- **Money check (A):** entering at the confirmation price, exit at the first break: +2.4 ticks gross, +2.0 after the
  $4.04 fee = about $20 per trade, 155 trades a year: about $3k/year on 1 contract, in-sample, best of ~29k cells.
  Codex's touch-limit diagnostic (limit a quarter leg back) kills it (+0.03 ticks gross): the limit fills mostly in
  the events that fail (adverse selection). Real, maybe; not a Combine passer.

Neither miner found the same cell independently. The two families agree on one theme: **how price arrives at a
swing (slow vs fast; deep in the higher-TF range or shallow) matters more than which timeframes point the same way.**

Event table: 1,936,238 swing events (bases 1m to 1d), dev 2010-06 to 2021-12, roll-crossing events excluded.

## 1. Baseline: a swing point alone is a random walk

Hold rate minus fair rate (geometry) per base and side: within ±1.5 points everywhere (1m −1.3, 5m 0, 15m 0,
1h +0.5, 4h 0, 1d ±2 on 1,000 events). Price confirming a swing point says nothing about the next break beyond
where price sits between the two levels. That matches the owner's three strategies: gross P&L ≈ 0 on dev.

## 2. Single features (705 cells, BH 5%)

9 cells pass (edge ≥ 3 points, ≥ 9/12 years). 8 are 1m microstructure (shallow retrace, quiet 18:00–23:00 CT
hours: 1–5 tick legs where tick rounding moves the fair rate). One weak real-looking: 1h swing confirmed at 17:00 CT
(session reopen) holds 4.3 points less than fair (n 1,291).

## 3. Pairs of timeframes (12,907 cells on 5m/15m/1h, BH 5%, both halves same sign ≥ 2 points)

31 pass, best of 12,907 (round 1 scan had no yearly gate; superseded by §0). Edges 3–8 points. Most involve 1w/1mo position or trend: those states change a few times
a year, so hundreds of events share one state and are not independent; z is overstated. Treat as regime, not setup.
Worth keeping:
- 15m swing low sitting in the upper third of the 1h range (shallow pullback inside the 1h leg) with the 15m leg
  already against: holds 5.9 points less than fair (n 691, both halves). Mirror for highs.
- 1h third consecutive swing low (two rule-5 sweeps in a row, no swing high between) with the 15m leg against: +7.7
  points (n 402). Alone, `fails = 2` on 1h is +4.2 (z 2.9), but 15m, 5m, 4h `fails = 2` show nothing: probably noise.

Conclusion so far: snapshot multi-timeframe swing state shifts the odds by a few points at most. It does not
contain the missing "something" by itself. Sequences (what happened, in which order) are the next thing to test.

## 4. Reverse-engineering the owner's three strategies

All three come from one idea: **the swing cycle (low, high, low, high) sets an expectation for the next point;
the trade is the reaction when price breaks that expectation.**

| Strategy | Expected | What happened instead | Bet |
|---|---|---|---|
| Swing Point Failure | after a swing low, the next swing high | price came back to the low | the failure continues |
| SPF Reversal | the failure continues | the failure trade's stop is taken | the failure itself failed |
| Manipulation | candle 2 builds the next swing high | candle 3 takes candle 2's low first, then its high | the dip was a stop run |

The words that generate them, which a pure geometry model lacks: **expectation, stop run (liquidity), trapped
side, who is in control.** With those words, any level gives three branches: reject, sweep then reclaim, accept.
Each branch is a new level with the same three branches. The owner's strategies are three nodes of that tree, and
they are fractal: Manipulation's 1h candle 3 is a 15m failure-of-failure.

Branches of the same tree the owner has not tested:
- **Accept then retest:** H broken, price comes back to H and holds (old high becomes support).
- **Exhaustion:** the 3rd failure in a row (measured above: weak).
- **Whose stops:** a sweep of a higher-timeframe point (or previous day high/low, equal highs) vs a sweep of a
  random candle low.
- **Speed of failure:** fast break (one candle) vs slow grind to the level.
- **Liquidity targets:** do equal highs/lows attract price before the opposite level?

## 5. Questions for the owner

1. On the 13 Nov 2026 example, what else was on screen: 4h/daily levels, previous day high/low, the time of day?
2. When you skip a setup that meets the rules on a chart, why? That reason is the hidden filter.
3. Where are the stops you mean by "liquidity": equal highs/lows, previous day, session high/low, swing points?
4. Do you treat the first test of a level differently from the second?

## 6. Round 3 (owner theory 2026-11-16; `round3.py`, 148 cells enumerated, 140 with n ≥ 300, none pass; H1 re-run with the ordered sequence)

- **Candle extremes are lower-TF swing points** (owner claim), 2015: 90% of 1h highs/lows are 1m swing points, 94-95%
  of 4h, 97-98% of daily; vs 5m: 77% / 87-88% / 95-97%. Mostly true; exceptions are extremes at a candle edge inside a
  move that continues into the next candle.
- **H1 nested manipulation: not supported.** Corrected 2026-11-16 after a Codex review: H1 first selected events by
  the snapshot `trend == 2` (HH+LL), which also took rule-5 replacements and events whose opposite point was not
  earlier. H1 now requires the ordered sequence from point-in-time state: previous high, then the HL, then the HH, then
  the event LL, strictly in time, HH above the earlier high, LL below the HL, no replacement (mirror for highs; the
  table stores the previous points' candle times). Ordered events: 1m 92,923 (was 143,461), 5m 29,428, 15m 10,889, 1h
  3,173. They hold 0.5-0.9 points *less* than fair, and the cells where the higher-TF low is intact and its trend is up
  are no better (1m with 5m intact + 5m up: −1.5, n 17,752); every H1 cell |edge| ≤ 2.5 points, none passes. An
  ordered LL is not more likely to become a higher-TF HL than geometry says. (Not checked: that the HL was higher than
  the low before it; the state keeps two points per side.)
  Why it looks true on a chart: an LL that later became an HTF HL is remembered as manipulation; one that did not is
  remembered as the start of a down move, a different pattern. The label is given after the outcome.
- **H2 forming higher-TF candle** (owner's 13 Nov 4h point): every cell |edge| ≤ 1.5 points.
- **H3 previous-day high/low:** an event that is today's first take of PDL (PDH for highs) holds +2.4 to +2.7
  points more than fair on 5m/15m (+2.0 1h), n ~1,500 each, same sign in both halves, not BH-significant. The
  only level family here that leans the right way on every intraday base.
- **purple_pa vs the swing strategies** (corrected by Codex round 3 from saved trades): both prediction and
  economics. Purple 15m is +$30.66 gross per trade (54.1% wins, stop exits median 28 ticks, fee ~1.4% of a loss);
  SPF default is −$5.92 gross per trade (stop exits median 4 ticks, fee ~10%): removing fees would not save SPF.
  Purple also trades ~50 times a year against ~600 for SPF. Which purple component (fixed level, first touch, gap
  departure, 1R bracket) carries the gross edge is not isolated yet.
- Fixes after the Codex round 3 audit: H2 now only counts still-forming higher-TF candles (12% of 15m cells were
  already complete); H3 uses explicit previous-day availability instead of a price-sign test. Re-run: still 0 pass.
- **Codex ordered test** (`codex_round3.md`): HL break → HTF low frozen → LTF reclaim of the lower high, 4 TF pairs,
  and the owner's breakout-candle-taken-out rule with the 4h right-candle state: no cell ≥ 3 points. Raw reclaim
  hold rates of 69-74% look strong but match the fair rate (69-73%): the reclaim moves price closer to the target.

## 7. Blind chart test (owner, 2026-11-16)

39 real 2021 moments (1m HL broken in a 1m uptrend, or the mirror), charts cut at the break, geometry 40-60% fair,
outcome hidden (artifact https://claude.ai/artifact/1eEnkWPWjXKFg47MoerWHX; `blind/make.py`, `blind/answers.csv`).
- **21/39 correct (53.8%)**; geometry alone expects 20.0. One-sided p vs 50% = 0.375: no detectable skill.
- Picked B "real break" 30 times, A "manipulation" 9 times; truth was 20 B / 19 A. Precision: A picks 5/9, B picks
  16/30. Longs 9/19, shorts 12/20. No notes given.
- Read: blind, at the moment of the break, the owner calls most breaks real; in hindsight on live charts the same
  moments are remembered as manipulations when they reversed. Consistent with outcome-based labelling (§6).
- Limit: 39 charts only detect a large skill (≈ 70%+ at this size). A modest 60% eye would need ~150 charts.
