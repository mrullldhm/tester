# juda_swing_point (Juda Swing Point)

Status: dev (2026-11-18: 6 dev combinations, all fail every gate; best PF 0.969)
Code: `strategies/juda_swing_point.py`
Source: owner, 2026-11-18 (chart CL 17 Nov 2026, 15m). Swing points: owner rule only (`cltester/swings.py`,
docs/SWINGS.md). Setup count study: `studies/juda_swing_point/findings.md` (run before this file; it counted setups
and a descriptive 1R/2R race on dev, so dev is not unseen for this idea).

## Hypothesis
In a 15m uptrend (EMA 10 > 20 > 50), a swing high that price takes out before any pullback low forms shows buyers in
control. The candle that then takes the previous candle's high and flips down through its low is a stop run under
the trend (manipulation). If the next candle does not go back to that low, the sweep held: buy. Short is the mirror.

## Rules (long; short is the mirror: swing low, takes low then high, sell limit, stop at the confirmation high)
All on 15m candles; swing data from `cltester.swings.detect`, point-in-time (candle k's state is known when k+1
closes).

1. **Invalidation.** The newest swing point is a swing high P. Candle j has high ≥ P (touch counts) while P is still
   the newest point (no swing low formed after it).
2. **Manipulation candle m** (m ≥ j, m = j allowed; owner chart: the break candle itself). While the newest point is
   still P (no swing low, no new swing high confirmed), m has high ≥ high[m−1] and low < low[m−1], and the first
   1m bar reaching high[m−1] comes before the first 1m bar breaking low[m−1]. Same 1m bar: an open already beyond a
   level counts as first; otherwise unknown and the invalidation ends with no trade. Low first: not a manipulation
   candle, keep waiting.
3. **Confirmation candle** m+1: low > low[m] (no touch). If it touches, keep waiting (rule 2) while the structure
   holds.
4. **Trend.** EMA 10 > EMA 20 > EMA 50 on 15m closes at the confirmation close.
5. **Entry** (owner 2026-11-18): buy limit placed at the confirmation candle close, works from the next 1m bar.
   Stop = confirmation candle low (`stop` = `confirm`); `stop` = `manip` (owner 2026-11-18, after runs 1-4): the
   manipulation candle low. close − stop ≤ `risk` (15) ticks: limit at close; otherwise limit at stop + 15
   ticks (Claude's reading, same as `swing_point_manipulation` rule 5; owner to confirm). close = stop: no trade.
   The confirmation candle must complete inside its own trading day and contract.
   The candle left of the swing high P (its rule-3 reference) through the signal bar must be one contract (Codex
   reviews 2026-11-18: prices are not back-adjusted, so a roll could fake the swing, the break, the sweep, the
   confirmation and the stop).
6. **Target** = limit + `tp` ticks (15 or 30). No breakeven, no trailing, 1 contract.
7. **Unfilled order.** `cancel` = `lhll` (owner 2026-11-18, after the first 2 dev runs; default): cancelled at the
   close of the 15m candle whose close confirms a lower high (a new 15m swing high, owner rule, priced below the
   swing high before it) or a lower low (a new swing low below the swing low before it); the order works through
   that bar. No TP-touch cancel. `tp` (first 2 runs, Claude's default then): cancelled at the first 1m bar that
   touches the target; when that bar opens at or
   through the fill level, the order filled at the open first (engine `kill` = target, docs/ENGINE.md, so
   `--through N` is respected; Codex reviews 2026-11-18).
   Both: also cancelled at the next setup signal (either side) and by the engine at the
   trading-day change, contract change and 3:10 PM CT. One order or position at a time.
8. Session: all hours (no filter).

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
| `risk` | 15 | fixed (owner) |
| `tp` (ticks) | 15 | 15, 30 (owner) |
| `tf` | 15m | fixed |
| `cancel` (unfilled order) | lhll | tp (runs 1-2), lhll (runs 3-6) |
| `stop` | confirm | confirm (runs 1-4), manip (runs 5-6) |

Total combinations on dev: **4**. 2 (`tp` 15/30, `cancel` tp) declared 2026-11-18 before the first run; 2 (`tp`
15/30, `cancel` lhll) added the same day by the owner after seeing them; 2 (`tp` 15/30, `cancel` lhll, `stop`
manip) added the same day after seeing those. Every tuned number reports best of 6.
Validation: the better one, frozen, only if it passes the dev gates.

## Pass criteria
Gates from docs/PROTOCOL.md (dev: ≥ 200 trades, PF ≥ 1.25, ≥ 70% years positive, Combine pass rate ≥ 50%, cost per
pass ≤ $500).

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-18 | dev | touch, no exit slip | 633 | −$7,907 | 0.752 | 0.0% | — (0 passes) | tp 15, cancel tp, stop confirm; win 26.1%; 1/12 years positive |
| 2026-11-18 | dev | touch, no exit slip | 666 | −$7,711 | 0.809 | 0.2% | — (0 passes) | tp 30, cancel tp, stop confirm; win 17.9%; 4/12 |
| 2026-11-18 | dev | touch, no exit slip | 696 | −$6,932 | 0.807 | 0.0% | — (0 passes) | tp 15, lhll, stop confirm; win 28.6%; 3/12 |
| 2026-11-18 | dev | touch, no exit slip | 696 | −$8,102 | 0.814 | 4.8% | — (0 passes) | tp 30, lhll, stop confirm; win 18.4%; 4/12 |
| 2026-11-18 | dev | touch, no exit slip | 655 | −$1,186 | 0.969 | 0.0% | — (0 passes) | tp 15, lhll, stop manip; best net of 6; win 40.0%; 7/12 |
| 2026-11-18 | dev | touch, no exit slip | 653 | −$4,798 | 0.904 | 6.9% | $7,301 | tp 30, lhll, stop manip; best pass rate of 6; win 25.7%; 4/12 |

Rows above: after the full contract-roll guard (swing reference through signal; 2nd Codex review 2026-11-18). The 12
earlier ledger rows (no guard; guard from candle m−1 only) are superseded, not deleted. Then (3rd Codex review)
the TP cancel keeps orders that open at the limit on the TP-touch bar: only the tp 15 / cancel tp row changed (630 to 633
trades); all 6 rerun on that code. Then (4th review) the TP-touch decision moved into the engine (`kill`), so `--through N`
uses the strict fill level; all 6 re-run with touch fills: identical.
All results in-sample unless the period is holdout or forward; tuned rows say best of N.
