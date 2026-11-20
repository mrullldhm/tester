# rlm (Reaction Level Matrix, WillyAlgoTrader, mapped to CL)

Status: dev (2026-11-20: after the fixes 4 versions pass the build-year checks; lead luck test p = 0.086; check years not run, owner to decide)
Code: `strategies/rlm.py`. Study: `studies/rlm/` (grid, screen, trade study, Codex briefs/replies in `codex/`).
Source: TradingView indicator "Reaction Level Matrix [WillyAlgoTrader]" v1.0.0 (Pine v6, an indicator, not a
strategy), pasted by the owner 2026-11-19. Logic excerpt: `studies/rlm/rlm_logic.pine`. Mapped by Claude, reviewed by
Codex (`studies/rlm/codex/reply1.md`). Swing points: owner rule only (`cltester/swings.py`).

## What the original claims, and what its numbers really are
The indicator clusters swing highs/lows into price bands ("levels"), scores them, and signals a rejection candle at
the nearest strong level. Its dashboard "win rate" is **the share of trades that touched TP1 (1R)**, not the share
that made money: a trade that touches 1R and then stops at break-even counts as a win (it loses the fee). Intrabar it
gives targets priority over stops (a bar that touches both counts the target), it enters at the signal close (market),
and it has no fees, slippage or P&L. Its displayed stats cannot show profitability. Here every trade is a real 1-CL
bracket with fees and the engine's worst-case intrabar order (stop first).

## Hypothesis
Prices where CL turned several times (and on bigger timeframes) hold orders: resting limit orders and stop clusters
of earlier participants. When price comes back to such a level and the candle closes strongly away from it, the
level held again; buying the retest/close with a stop beyond the wick should have positive expectancy.
Who is on the other side: breakout traders who sold into support (bought into resistance) and get trapped.

## Rules (long; short is the mirror)
| Original (Pine) | CL version | Note |
|---|---|---|
| Swings: `ta.pivothigh/low(6, 6)` on the chart TF | owner-rule swing points on several TFs (`sources`): `all` = S..1d of {5m, 15m, 1h, 4h, 1d}, `htf` = only TFs above S | owner rule mandatory; no swing length |
| Touch weight = 1 + reaction size (≤ 2.5 ATR) in the 6 confirmation bars | **weight = TF** (owner: the bigger the TF, the stronger the swing): 5m 1, 15m 1.5, 1h 2, 4h 3, 1d 3.5 (same 1..3.5 range as the original). Control `flat`: every TF weight 1 | ladder numbers are an assumption; only the order is the owner's |
| A pivot counts once | one turning point counts once: same kind, same price, one candle nested in the other = same extreme; a higher TF confirming it later upgrades the weight (strength + Δw from then on, no backdating), no extra touch | Codex: keep `touches` an event count |
| Swing known 6 bars after the extreme | `reg = lock`: touch when the point is locked (a newer opposite point exists above it, so rule 5 can no longer replace it). `reg = confirm`: touch when the point first appears (candle k+1 close); when it later leaves the structure (rule 5/4, while still in the top four points) its weight is withdrawn from the level from then on | lock is later but stable; confirm is earlier. Rule-4 removal of an already locked point is not withdrawn in lock mode (43 of 14,561 5m points in 2010) |
| Level engine per chart bar | per completed candle of the signal TF `sig_tf` S ∈ {5m, 15m, 1h}: age (half-life 500 S bars) and cross (close beyond the band: ×0.7 strength) with the candle close, register touches known by its completion, merge overlapping bands (5 passes), cap 60 levels, drop strength < 0.25, pick the 3 nearest active (≥ 2 touches) levels per side | constants as original |
| Band: weighted mean ± weighted std, clamped to [0.15, tol] × ATR34; join radius tol × ATR34 | same, ATR34 of S | `tol` ∈ {0.4, 0.6, 1.0} |
| Score = 100·(1 − e^(−strength·polar/6)), polar ×1.25 if touched by highs and lows | same | `score` ∈ {0, 50, 70} minimum |
| Buy rejection: price above the band before this bar, low into the band, close above the band, (close − low)/range ≥ clv, cooldown 10 bars per level, nearest level first, long wins a tie | same | `clv` ∈ {0.6, 0.75} |
| Entry at the signal close (market) | limit only (`entry`): `close` = limit at the signal candle close; `band` = limit at the band top (retest). Works one S interval (clock minutes) from the next 1m bar; killed by a target touch; engine cancels at day change / roll / 15:10 CT | owner rule: limit entries, touch fills |
| SL wick-anchored: min(low − 0.25·ATR14, entry − 0.5·ATR14) | `stop`: `wick` = same (ATR14 of S, vs the limit price); `band` = min(band low − 0.25·ATR14, entry − 0.5·ATR14) | risk < 5 ticks skipped |
| TP 1R/2R/3R, BE after TP1, close at TP3 or reversal | `exit`: `r1`, `r2`, `r3` fixed target; `be3` = 3R target, stop to entry once a bar after the fill bar reached 1R (effective next bar; the fill-bar high is ignored because it may predate the fill). Opposite-signal reversal not modelled (one position at a time) | 1 contract |
| any time | `session`: `all` (any signal 17:00..15:10 CT) or `rth` (signal candle completes 08:30..13:30 CT). Levels always evolve on all hours | RTH known from earlier studies (post-hoc prior) |

Point-in-time: a swing candle k's state is known when candle k+1 completes (`avail`); orders work from the next 1m
bar. A signal candle that straddles a roll or completes in the next session is skipped.
Rolls (prices not back-adjusted): levels, ATR and touches reset at every contract change; a touch needs its extreme
candle and its left reference candle inside the current contract. Owner swing structure itself runs on unchanged.

Code audit before the grid (Codex round 2, `studies/rlm/codex/reply2.md`; all fixed, tests in `tests/test_rlm.py`):
a touch keeps the weight of every swing point (pid) that confirmed its extreme, not one per TF; a level's death
purges its touches (no stale strength shares); a withdrawal takes back the touch's current share (decays and cross
penalties included); BE triggers at the frozen TP1 (intended limit + intended 1R) and moves the stop to the actual
fill; candles that straddle a roll are skipped and left out of ATR; grid parts carry a code fingerprint and the merge
refuses an incomplete family. Confirm-mode withdrawals: first inferred from the top-4 state; Codex's adversarial review found it missed points
removed by rule-4 cascades (92 on 2010 5m). Now exact: the detector reports every point that enters or leaves the
structure (`cltester.swings.detect(observer=...)`, read-only hook); replaying the events rebuilds the structure
exactly (2010 5m/15m/1h; random-walk test). Multi-timeframe dedupe also fixed (several smaller touches inside one
bigger candle coalesce). All results before these fixes are void (`studies/rlm/pre_dedup/`).

## Parameters and trial budget
| Parameter | Values |
|---|---|
| `sig_tf` | 5m, 15m, 1h |
| `reg` | lock, confirm |
| `sources` | all, htf |
| `weight` | tf, flat |
| `tol` | 0.4, 0.6, 1.0 |
| `score` | 0, 50, 70 |
| `clv` | 0.6, 0.75 |
| `entry` | close, band |
| `stop` | wick, band |
| `exit` | r1, r2, r3, be3 |
| `session` | all, rth |

Owner asked for every version: **13,824 combinations**, all run once on dev as a screen (`studies/rlm/grid.py`, every
row kept). Codex recommended 48 (`codex/reply1.md`); the full grid is run because the owner asked, so the guard
below must carry the multiple-testing load. Every dev number is **best of 13,824**.

Disclosure: before this file was written, one smoke run of the default version on dev 2010-06..2011 (15m, lock,
be3) was looked at: 2,418 trades, PF 0.91. The spec above was not changed because of it.

## Screen and guard (declared before the grid)
1. Dev gates (PROTOCOL.md): trades ≥ 200, PF ≥ 1.25, years positive ≥ 70% (all dev years; no-trade year = not
   positive), Combine pass ≥ 50%, cost/pass ≤ $500; plus both halves (2010-06..2015, 2016..2021) net > 0, plus ≥ 60% of
   one-step neighbours net > 0.
2. Family check (Codex): day-block bootstrap of the max PF across the screened family vs a random-entry null
   (same times, sides, brackets on random dates) to see if the best version beats what selection alone produces.
3. Survivors (max 3, ranked by pass rate): `cli test --period dev` (ledger) and `--through 1` (PF must stay ≥ 1.10),
   trade spot-checks against raw bars.
4. Trade study (wins vs losses): predeclared features (TF of the strongest touch, touches, score, polarity, age,
   crosses, band width/ATR, CLV, risk ticks, CT hour, side, ATR); any filter found there is a new trial and needs data
   it was not found on.
5. Validation 2022-2024 once per survivor, frozen. Holdout only with the owner's yes.
If nothing survives step 1, the strategy is dropped on dev.

## Session / hour / daylight-saving test (owner request 2026-11-20, declared before the run)
Question 1: which session or hour does the lead trade best in? Question 2 (owner): does performance belong to the
**exchange candle** (the n-th 1h candle after the 17:00 CT open; the first candle is 06:00 Malaysia time in US summer,
07:00 in US winter) or to the **wall clock** (a fixed Malaysia / UTC hour)? Malaysia has no daylight saving, so a
fixed Malaysia hour is a fixed UTC hour; the exchange candle moves by 1 hour against it twice a year. London has
its own daylight saving dates (about 3 weeks apart from the US in March and 1 week in Oct/Nov), so the London clock
is a third candidate for the London session.

Disclosure: before this section was written, the lead's trades were looked at by Chicago hour and five Chicago
sessions (all-hours version; London 02:00-07:00 and RTH 08:30-13:30 carried ~80% of net). Every window below is
therefore at best a confirmation of something already seen, and is counted as a new trial.

Base: the lead, every parameter frozen, only the signal window changes. A window keeps a signal when the **open
time of its 1h signal candle** is inside it, on the stated clock. Levels still evolve on every hour.
| Clock | Windows (candle open hours, inclusive) | Count |
|---|---|---|
| ct (exchange, = candle number: 17:00 is candle 1) | asia 17-01, london 02-06, us_open 07-10, us_mid 11-14, london+us_open 02-10, all-but-asia 02-14 | 6 |
| ct single candles | each of the 23 candles 17:00 .. 15:00 | 23 |
| myt (Malaysia, fixed UTC+8) | the four sessions at their US-winter Malaysia hours: asia 07-15, london 16-20, us_open 21-00, us_mid 01-04 | 4 |
| myt single hours | each of the 24 Malaysia hours | 24 |
| ldn (London clock) | london 08-12 London time (= ct 02-06 except in the weeks the US and UK daylight saving dates differ) | 1 |
**58 versions.** Running total for this strategy: 13,824 + 58 = **13,882**.

Analysis (declared):
1. Screen every window with the dev gates. Single candles have ~40-90 trades and cannot pass trades ≥ 200; they
   are reported, not selected.
2. Family-wise White Reality Check over the 58 windows (same method as step 2). A window that is not better than
   best-of-58 luck is not adopted.
3. Clock attribution: on the all-hours trades of the lead **and** of the lead with score 0 (more trades, ~7,650),
   leave-one-year-out prediction of each trade's R from the hour means of the other years, once with the exchange
   candle and once with the Malaysia hour as the hour key. Lower error = the clock the effect lives on. Day-block
   bootstrap CI of the error difference. Plus a direct view: per exchange candle, mean R in US summer vs US winter
   (a candle effect stays put; a wall-clock effect shifts by one candle between seasons).
4. Halves: any window kept must be positive in 2010-15 and 2016-21.
Nothing found here changes the frozen lead unless it survives 1, 2 and 4; even then it is a new candidate for the
check years, not a dev result.

## Pass criteria
PROTOCOL.md dev gates (above), validation PF ≥ 1.10 and pass ≥ 40%.

## Results
Rows dated 2026-11-20 above the dedupe-fix line come from code that could count one extreme as several touches
(Codex adversarial review); they are void and kept for the record (`studies/rlm/pre_dedup/`).

| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-20 | dev | touch | — | — | median 0.98 | — | — | 13,824-version screen (`studies/rlm/screen_dev.txt`): 38.9% net > 0; **1 passes all gates** |
| 2026-11-20 | dev | touch, no exit slip | 1,281 | $61,525 | 1.309 | 52.3% | $332 | lead: 1h/confirm/all/flat/tol 0.4/score 50/clv 0.6/close/band/r1/all; best of 13,824; 11/12 years; ledger 0c7941f8774a |
| 2026-11-20 | dev | through 1 | 1,250 | $53,020 | 1.267 | 50.0% | $375 | same version, strict fills; 10/12 years |
| 2026-11-20 | dev | touch | — | — | — | — | — | nulls: random-date 0/300 ≥ PF 1.309 (median 0.97); same-day no-level (Codex) 0/300 (median 0.85) |
| 2026-11-20 | dev | touch | — | — | — | — | — | family-wise (step 2): White RC p = 0.25 for the lead (SPA post-hoc 0.23): **not better than best-of-13,824 luck** |
| 2026-11-20 | dev | touch | 675 | $54,873 | 1.466 | 64.4% | $394 | session test: lead with window ct:02-10 (exchange candles opening 02:00-10:00 CT); passes all gates; RC within the 58 windows p < 0.001; best of 13,882; 10/12 years; halves +$39.4k / +$15.5k; ledger 7ba58d609451 |
| 2026-11-20 | dev | through 1 | 659 | $48,718 | 1.414 | 58.2% | $441 | same window, strict fills; 10/12 years |
| 2026-11-20 | dev | — | — | — | median 0.98 | — | — | **after the dedupe + exact-withdrawal fixes**: 13,824 versions, 39.1% net > 0, 4 pass all gates (all 1h/confirm/all/flat/tol 0.4/score 50/close) |
| 2026-11-20 | dev | touch | 1,249 | $66,184 | 1.345 | 55.7% | $321 | lead (band stop, r1, all hours); best of 13,824; 11/12 years; ledger 2851bcbfb212; White RC p = 0.086 (rank 1, t 4.47) |
| 2026-11-20 | dev | through 1 | 1,218 | $57,849 | 1.303 | 53.9% | $373 | same, strict fills; 11/12 years |
| 2026-11-20 | dev | touch | — | — | — | — | — | random-date null 0/300 ≥ PF 1.345 (median 0.97) |
| 2026-11-20 | dev | touch | 661 | $58,420 | 1.517 | 72.5% | $380 | lead, window ct:02-10; best of 13,882; 10/12 years; 58-window RC p < 0.001; ledger d70b216ba51e |
| 2026-11-20 | dev | through 1 | 645 | $52,314 | 1.464 | 70.2% | $441 | same window, strict fills |
All results in-sample unless the period is holdout or forward; tuned rows say best of N.
