# swing_point_failure (Swing Point Failure)

Status: dev (2026-11-14: all 12 dev combinations lose; fails every gate)
Code: `strategies/swing_point_failure.py`
Source: owner model, 2026-11-13. Swing points: owner rule only (`cltester/swings.py`, docs/SWINGS.md).

## Hypothesis
Swing points alternate: low, high, low, high. When a swing low prints and the market fails to make the next swing
high, then comes back to the low, the low has failed as a swing point. That failure marks sellers in control. The
entry waits for the first small-timeframe pullback (an uptrend with a confirmed higher low) to break, so the short
joins the failure after counter-traders have shown themselves and been beaten. Long is the mirror.

## Rules (short; long is the mirror: swing high, lower high, low ↔ high)
Swing timeframe `swing_tf` (default 1h). Execution timeframes 1m and 5m. Times are 1m bar closes, CT.

1. **Armed.** The newest point of the swing-timeframe structure (`swing_state(..., newest=True)`, point-in-time) is
   a swing low: no confirmed swing high after it. A candle that is both points uses the owner order rule
   (docs/SWINGS.md). Each swing low (identified by its candle) gives at most one setup.
2. **Failure (touch).** The first 1m bar after the low is known whose low ≤ the swing low. The touch fixes the
   **invalidation level**: the high of the swing-timeframe candle before the one that holds the touch bar.
3. **Setup ends without a trade** when, before a trigger:
   - any 1m bar after the touch bar reaches the invalidation level (high ≥ level), or
   - the newest swing-timeframe point is no longer that swing low: a swing high is confirmed, or rule 5 replaced the
     low with a lower one (that new low is a new setup when price comes back to it).
   On the same bar close, these end checks come before the trigger.
4. **Pullback timeframe.** The first of 1m / 5m to confirm a **higher low** (HL): its newest swing low is above the
   swing low before it, and the HL candle starts at or after the start of that timeframe's candle holding the touch.
   The swing low before it may be from before the touch. Both on the same bar close: `tie` decides (default 5m;
   version 2: 1m). The timeframe is then locked for the setup.
5. **Trigger.** The trigger level trails to the newest HL on the locked timeframe. The trigger candle is the first
   candle of that timeframe whose low ≤ the trigger level (a touch counts). Act at its close.
6. **Stop** = the swing high after the HL: the highest high from the candle after the HL candle (its clock-aligned
   open, also when the HL candle's first minute has no bar) through the trigger candle. When the trigger candle holds that high, it is assumed to become the swing high (owner); a later higher
   high stops the trade out.
7. **Entry** (short limit, works from the next bar): `close` = trigger candle close.
   stop − close ≤ `risk` ticks: limit at `close`; otherwise limit at stop − `risk` ticks. No trade if stop ≤ close.
8. **Target** = entry − `rr` × `risk` ticks (25 → 50). No breakeven, no trailing, 1 contract.
9. **Unfilled order** is cancelled at the close of the 1m bar where a swing-timeframe swing high whose candle comes
   after the touched low is confirmed (and by the engine at the trading-day change, contract change, 3:10 PM CT).
10. One entry per setup (the first pullback). No session window, no daily trade limit. The engine flattens at
    3:10 PM CT.
11. **Overlap** (owner, 2026-11-14; engine overlap mode, docs/ENGINE.md): a new trigger cancels an order that has
    not filled; a filled trade keeps running and the new order is placed too. Max 5 contracts open (Combine).
    The Combine simulator sums trades that are open together (docs/TOPSTEP.md).

Interpretations to confirm with the owner:
- Execution candidates are 1m and 5m only.
- Same bar close: setup end (rule 3) wins over the trigger.
- If the newest pullback swing low stops being a higher low (rule 4/5 change), the trigger level stays at the last
  higher low.

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
| `swing_tf` | 1h | 1h, 4h |
| `risk` (max entry-to-stop, ticks) | 25 | 25, 20, 15 |
| `rr` (target = rr × risk) | 2 | fixed |
| `tie` (1m and 5m HL on the same bar) | 5m | 5m, 1m |

Total combinations on dev: **12**, declared 2026-11-14 before the first run. Every tuned number reports best of 12.
Validation: the best combination only, frozen, if it passes the dev gates.

## Pass criteria
Gates from docs/PROTOCOL.md (dev: ≥ 200 trades, PF ≥ 1.25, ≥ 70% years positive, Combine pass rate ≥ 50%, cost per
pass ≤ $500), plus: the neighbours of the chosen combination (other `risk` values, same `swing_tf`) also profitable.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-14 | dev | touch, no exit slip | 7,364 | −$73,371 | 0.821 | 4.6% | $3,365 | 1h, risk 25, tie 5m (default); tie 1m identical |
| 2026-11-14 | dev | touch, no exit slip | 7,352 | −$69,522 | 0.822 | 6.3% | $3,250 | 1h, risk 20; best PF and pass rate of 12; tie 1m identical |
| 2026-11-14 | dev | touch, no exit slip | 7,310 | −$64,792 | 0.819 | 0.5% | — | 1h, risk 15; tie 1m identical |
| 2026-11-14 | dev | touch, no exit slip | 2,404 | −$34,092 | 0.784 | 1.3% | — | 4h, risk 25 (tie 1m: −$33,992) |
| 2026-11-14 | dev | touch, no exit slip | 2,399 | −$27,502 | 0.814 | 0.5% | — | 4h, risk 20; best net of 12 (tie 1m: −$27,402) |
| 2026-11-14 | dev | touch, no exit slip | 2,383 | −$28,217 | 0.790 | 2.2% | $7,987 | 4h, risk 15 (tie 1m: −$28,117) |

Dev, in-sample, best of 12. Years positive: 0/12 (1h), 1–3/12 (4h). Win rate 10–15%.
Figures from the run after two bug fixes (stop window on a 5m HL candle missing its first minute; partial-exit
contract count); the pre-fix run gave identical figures and was removed from the ledger (owner).

Why it loses (default run, spot-checked against raw bars): the stop is the 1m pullback swing high, so it is
usually tiny (stopped trades: median −4 ticks, 19% stopped on the fill bar) while the target stays 50 ticks away.
Gross P&L is negative before fees; fees ($4.04 per trade, ~7,400 trades) add about −$30k. The owner examples had
17–38 tick stops, which are the minority. The tie setting decided almost nothing (1m confirms first).
All results in-sample unless the period is holdout or forward; tuned rows say best of N.
