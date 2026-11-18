# ghost_box (Ghost Box, futures translation)

Status: dev (2026-11-18: 4 dev combinations, all fail the gates; premise study fails; not taken to validation)
Code: `strategies/ghost_box.py`. Premise study: `studies/ghost_box/` (run on dev only).
Source: "The Ghost Box Checklist" (Delta Ghost, 2-page PDF, `Ghost-Box-Checklist.pdf`), found online by the owner
2026-11-18. Written for a 0DTE iron condor on SPY/SPX. No other source material.

## What the source says (SPX)
Overnight high/low = box walls. Wait for the "Ghost Wick": the first push out of the box pokes through and closes
back inside. Box ≥ 0.4% of price. Overnight gap < 0.5%. Enter 10:00-10:30 ET. Sell a condor: short call above the top
wall, short put below the bottom wall, wings 5 SPX points out. Take 50% of credit or hold to expiry; exit the side in
trouble when a 5m candle closes beyond a wall. Skip CPI/FOMC/NFP days; VIX 13-25 gives +1 score.

## Why it cannot be tested as written
It is an options trade. Topstep Combine is futures only and the repo has no CL options prices. Two translations
(owner choice 2026-11-18: both):

1. **Premise study** (no P&L): after a ghost wick, does CL stay inside the box until 13:30 CT (CL settlement, the
   0DTE expiry analog)? Compared with the same days without a wick. If the wick carries no information, the
   strategy has nothing to trade on CL.
2. **Futures fade** (this strategy): the condor bets the box holds. The futures bet that the box holds is to fade the
   wick: sell after a failed push above the top wall, buy after a failed push below the bottom wall.

## Hypothesis
The overnight range on CL is set by thin Globex trade. When the first RTH push out of it fails and closes back
inside, the breakout traders who chased it are trapped and the range holds for the session; price rotates back
into the box. Who is on the other side: breakout buyers/sellers stopped out as price returns.

## CL mapping (owner choice 2026-11-18)
| PDF (SPX) | CL |
|---|---|
| overnight high/low | high/low of 17:00-07:59 CT bars (trading day's Globex session) |
| 10:00-10:30 ET (30-60 min after stock open) | 08:30-09:00 CT (30-60 min after 08:00 CT pit open) |
| wick search | 5m candles starting 08:00-08:55 CT |
| overnight gap | 08:00 CT open vs previous trading day's last bar close before 13:30 CT (settlement), same contract |
| 0DTE expiry | 13:30 CT |
| CPI/FOMC/NFP skip, VIX 13-25 | **not applied**: no news calendar or VIX/OVX data in the repo |

## Rules (side shown for a wick above the top wall = short; a wick below = long, mirror)
1. **Data.** ≥ 600 bars in 17:00-07:59 CT; one raw_symbol from 17:00 CT through the 08:00 open and again through the
   signal bar (a roll inside the box would fake the walls; later rolls are the engine's job, no lookahead); 08:00 CT
   bar present (≤ 08:05); previous day's settle bar on the same contract.
2. **Box.** top = max high, bottom = min low of 17:00-07:59 CT. Width (top − bottom) / 08:00 open ≥ 0.4%.
3. **Gap.** |08:00 open − previous settle| / previous settle < 0.5%.
4. **Ghost wick.** First 5m candle from 08:00 CT with high > top or low < bottom (strictly through). It must close
   back inside (bottom ≤ close ≤ top). Above-and-below in one candle: no trade. Closes outside: box broken, no trade.
   Must complete by 09:00 CT.
5. **Signal bar** = the later of the wick candle's completion bar and the last bar before 08:30 CT (that must be the
   08:29 bar, else no trade: the order would start before 08:30). Any 5m candle
   closing outside the box between the wick and the signal bar: no trade. The order must have at least 1 minute of
   window left (works until 09:00 CT, `expire_min`).
6. **Entry** (sell limit), param `entry`:
   - `wall`: limit at the top wall (sell where price already failed; fills only on a retest).
   - `close`: limit at the signal bar's 1m close.
7. **Stop** = wick high + 1 tick (the Ghost Stop analog: beyond where the fake move died).
8. **Target**, param `target`: `mid` = box middle (rounded to tick), `opposite` = bottom wall. Signal close already at
   or beyond the target: no trade.
9. **Management** (PDF exit rule): close at the next bar's open after a 5m candle closes above the top wall (beyond
   the wall on the losing side). Time exit at 13:30 CT (expiry analog). Engine flatten 15:10 CT never reached.
10. One trade a day, 1 contract. The PDF's 2%-of-account and score-based sizing are not used.

Box Score note: with the skip rules applied (wick +2, gap +2, width +2, window +1) every traded day scores ≥ 7, so
the score adds nothing beyond the rules above without news/VIX data.

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
| `entry` | wall | wall, close |
| `target` | mid | mid, opposite |
| `width_pct` | 0.4 | fixed (PDF) |
| `gap_pct` | 0.5 | fixed (PDF) |

Total combinations on dev: **4**, declared 2026-11-18 before the first run. Every tuned number reports best of 4.
Validation: the best one, frozen, only if it passes the dev gates.

## Pass criteria
Gates from docs/PROTOCOL.md (dev: ≥ 200 trades, PF ≥ 1.25, ≥ 70% years positive, Combine pass rate ≥ 50%, cost per
pass ≤ $500). Plus: the premise study must show the box holds more often after a wick than without one; if not, the
strategy result is luck, whatever it shows.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-18 | dev | touch, no exit slip | 123 | −$1,557 | 0.756 | 0.0% | — (0 passes) | entry wall, target mid; win 10.6%; 3/12 years positive |
| 2026-11-18 | dev | touch, no exit slip | 125 | −$3,065 | 0.548 | 0.0% | — (0 passes) | entry wall, target opposite; win 5.6%; 3/12 |
| 2026-11-18 | dev | touch, no exit slip | 191 | +$348 | 1.021 | 6.5% | $7,056 | entry close, target mid; best net and PF of 4; win 38.7%; 7/12 |
| 2026-11-18 | dev | touch, no exit slip | 211 | −$432 | 0.983 | 48.0% | $7,105 | entry close, target opposite; best pass rate of 4; win 28.4%; 7/12; median 802 trading days to pass |
All results in-sample unless the period is holdout or forward; tuned rows say best of N.

The 4 runs were repeated twice on new code hashes (a comment-only lint fix; then review fixes: roll check through the
signal bar only, 08:29 floor, one 5m candle build): identical numbers each time; 12 ledger rows, 4 distinct results.

Spot-checked 3 random trades (entry close / opposite: 2013-08-09 long target, 2013-01-16 short stop, 2014-01-16 long
stop) against raw 1m bars: box, wick candle, fill, exits all match.

## Verdict (2026-11-18)
Fails. Premise study (`studies/ghost_box/findings.md`): after a ghost wick the CL box breaks on a 5m close before
13:30 CT on 92% of days, more often than on days without a wick, so the wick is not a confirmation on CL. The futures
fade: best of 4 PF 1.02 (191 trades, below the 200 floor), every combination misses every dev gate. The 48% rolling pass
rate of `close/opposite` is an artefact of ~18 trades a year: the median pass takes 802 trading days, and the
sequential cost per pass is $7,105. Not run on validation (dev gates not met). The PDF's news and VIX filters could
not be applied (no data); they would only remove days, and nothing in the remaining days shows an edge to protect.

