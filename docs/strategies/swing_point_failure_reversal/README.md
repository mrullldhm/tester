# swing_point_failure_reversal (Swing Point Failure Reversal)

Status: dev (2026-11-15: all 5 dev combinations lose; fails every gate)
Code: `strategies/swing_point_failure_reversal.py`
Source: owner, 2026-11-15, after `swing_point_failure` lost on all 12 dev combinations with 84–90% of trades
stopped. Swing points: owner rule only (`cltester/swings.py`, docs/SWINGS.md).

## Hypothesis
Swing Point Failure (SPF) shorts are stopped 84–90% of the time on dev. If the short's stop is touched, the
pullback the short sold into was not over: buyers took the pullback high back. Trade with them: buy when the SPF
short's stop is touched, stop under the newest low, target 2R. Short is the mirror (SPF long's stop touched).

Selection-bias note: this idea was chosen after seeing the SPF dev results. A flipped copy of the SPF trades
(not this rule set) gave PF 1.02–1.12 on dev (in-sample, best of 12), below the 1.25 gate. Validation and holdout
are the real test.

## Rules (long, from an SPF short; short is the mirror, from an SPF long)
Source: every SPF signal (`strategies/swing_point_failure.py`, `swing_tf` 1h, `tie` 5m), both sides. Its
pullback timeframe `k` (1m or 5m) and its stop `H` (the short's stop price) are taken as is. A source is used
whether or not the SPF short limit filled and whatever it did after (owner: any stop touch).

1. **Watch window.** From the 1m bar after the SPF signal bar, same trading day and contract, until the bar before the next SPF
   signal (either side). Everything below (touch and trigger candle close) must happen inside it.
2. **Touch.** The first 1m bar in the window whose high ≥ `H` (a touch counts).
3. **Trigger candle** = the candle of timeframe `k` that holds the touch bar. Act at its close (1m: the touch bar
   itself). When its last minute has no bar, the signal comes at the close of the next bar (when the candle is
   known complete), but its close and lows are the trigger candle's own bars only.
4. **Stop** = the lowest low after the recent swing high: the newest confirmed swing high on timeframe `k`
   (`swing_state`, point-in-time at the trigger close) whose candle opens after `H`'s candle; when there is none,
   `H`'s candle. Lowest low from the clock-aligned open of the candle after that swing high through the trigger
   candle (the trigger candle's own low counts). `H`'s candle = the `k` candle holding the last 1m bar at or
   before the SPF signal bar with high = `H` (equal highs: the later one).
   `sl_tf` (default `pullback` = timeframe `k`): the timeframe whose newest confirmed swing high sets the stop. With
   5m or 15m, a swing high on that timeframe whose candle opens after `H`'s bar moves the window start to the
   candle after it (on that timeframe); otherwise the window starts after `H`'s `k` candle, as above. Allowed: 1m to 1h
   (clock-aligned candles); 4h and 1d are refused because their candles follow the 17:00 CT session.
5. **Entry** (buy limit, works from the next bar; no stop orders, so no entry slippage):
   `close` = trigger candle close. close − stop ≤ `risk` ticks: limit at `close`; otherwise limit at
   stop + `risk` ticks. No trade if stop ≥ close.
6. **Target** = limit + 2 × `risk` ticks (15→30, 20→40, 25→50). No breakeven, no trailing, 1 contract.
7. **Unfilled order** is cancelled at the close of the next SPF signal bar (either side), and by the engine at the
   trading-day change, contract change and 3:10 PM CT.
8. One entry per SPF signal. Overlap mode as in SPF (docs/ENGINE.md): a filled trade keeps running.

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
| `risk` (max entry-to-stop, ticks; target 2 × risk) | 25 | 15, 20, 25 |
| `swing_tf` (source SPF) | 1h | fixed |
| `tie` (source SPF) | 5m | fixed |
| `rr` | 2 | fixed |
| `sl_tf` (stop swing timeframe) | pullback | pullback; 5m and 15m at risk 25 only |

Total combinations on dev: **5**. 3 declared 2026-11-15 before the first run; 2 added the same day by the owner
after seeing them (`sl_tf` 5m, 15m at risk 25). Every tuned number reports best of 5. Validation: the best one, frozen, only
if it passes the dev gates.

## Pass criteria
Gates from docs/PROTOCOL.md (dev: ≥ 200 trades, PF ≥ 1.25, ≥ 70% years positive, Combine pass rate ≥ 50%, cost per
pass ≤ $500), plus: the neighbouring `risk` values also profitable.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-15 | dev | touch, no exit slip | 6,547 | −$56,300 | 0.883 | 10.6% | $1,707 | risk 25 (default) |
| 2026-11-15 | dev | touch, no exit slip | 6,520 | −$44,131 | 0.901 | 7.2% | $1,225 | risk 20 |
| 2026-11-15 | dev | touch, no exit slip | 6,468 | −$23,431 | 0.940 | 13.2% | $1,470 | risk 15; best net of the 1m/5m-stop rows (gross +$2,700 before $26,131 fees) |
| 2026-11-15 | dev | touch, no exit slip | 6,486 | −$21,143 | 0.960 | 20.1% | $712 | risk 25, `sl_tf` 5m (gross +$5,060) |
| 2026-11-15 | dev | touch, no exit slip | 6,410 | −$17,016 | 0.968 | 21.4% | $693 | risk 25, `sl_tf` 15m; best of 5 (gross +$8,880) |

Dev, in-sample, best of 5. Years positive 1–3/12 (stop from the setup's chart), 4/12 (5m and 15m stops).
A stop from 5m or 15m swings sits further away (15m: entry-to-stop median 10 ticks, quartiles 5 / 19) and lifts the
pass rate to about 21%, but PF stays under 1 and fees (~$26k) still decide the result. Spot-checked one 15m-stop
trade per side against raw bars (stop window start and extreme match). Figures from the run after three review fixes (swing high candle
open aligned to the clock; no trade when H sits in the trigger candle; a trigger candle missing its last minute
uses its own bars for close and stop, not the next bar's); both earlier runs gave identical figures and their 6
ledger rows stay. The same fix in `swing_point_failure.py` was then re-run here too (identical). From 2026-11-15
the run hash also covers `swing_point_failure.py` (`DEPENDS`); the last 3 rows (hashes 1423f54509c2, 11b627df8b5f,
94435be672b5) are the current code. Earlier rows reuse hashes across source changes; their trade files were
overwritten. Win rate 15–20%. Both sides lose about equally.

Why it loses (risk 25, spot-checked against raw bars, one trade per side): the stop is the lowest low since the
newest 1m/5m swing high, so it sits close: entry-to-stop median 7 ticks (quartiles 4 / 13), stopped trades median
−6 ticks, 13% stopped on the fill bar. The target stays 2 × risk (50 ticks) away. Same shape as SPF: a tiny stop
against a far fixed target, and ~6,500 trades × $4.04 fees (−$26k) on a gross near zero.

All results in-sample unless the period is holdout or forward; tuned rows say best of N.
