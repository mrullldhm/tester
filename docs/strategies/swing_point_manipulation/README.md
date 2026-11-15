# swing_point_manipulation (Swing Point Manipulation)

Status: dev (2026-11-16: 14 dev combinations; best PF 1.044, fails every gate)
Code: `strategies/swing_point_manipulation.py`
Source: owner, 2026-11-15 (charts of CL 13 Nov 2026). Swing points: owner rule only (`cltester/swings.py`,
docs/SWINGS.md).

## Hypothesis
After a 1H swing high then a swing low, price tries to build the next 1H swing high: candle 2 makes a high equal to or
above candle 1. If candle 3 first takes candle 2's low (sweeps the sell stops under it) and then takes candle 2's
high in the same hour, the dip was a stop run, not a reversal: buyers are in control. Buy the 15m candle that broke
candle 2's high, stop under that 15m candle, target the latest 1H swing high (the top of the range the swing low
left). Short is the mirror.

## Rules (long; short is the mirror: swing low then swing high, candle 2 low ≤ candle 1 low, candle 3 takes candle
2's high first and then its low, sell limit, target the latest 1H swing low)
Times are candle opens; 1H candles follow the clock. All swing data is `swing_state(df, "1h", newest=True)`,
point-in-time.

1. **Structure.** At the close of candle 2 (c2; when its last minute is missing, the bar that completes it), the newest
   1H swing point is a swing low and a swing high exists before it (order swing high, then swing low).
   **TP** = that swing high's price.
   `outside` (owner 2026-11-15, both tested): one 1H candle can be both swing low and swing high (outside candle).
   When it printed the low first, the swing high on it is the newest point. `skip`: ignore that swing high; the
   long is armed and TP = the swing high before it. `strict`: no long setup. Owner example 13 Nov 2026 10:00 MYT:
   H 88.68, L 88.04 (low 10:00, high 10:35); TradingView shows only the swing low because 14:00's 89.18 later
   replaced that swing high; `skip` gives the owner's trade (TP 89.15), `strict` none. An outside candle that printed
   the high first leaves the swing low newest: armed in both modes, TP = its own high. Short is the mirror.
2. **Candles 1 and 2.** c1 and c2 are the two 1H candles before candle 3 (c3), consecutive in the candle list.
   They may span the daily halt, a weekend or a holiday (owner 2026-11-16: c1 to c3 need not be in one session).
   c1 opens at or after the swing low's candle (owner 2026-11-15: the swing low candle itself may be c1).
   high[c2] ≥ high[c1].
3. **Trigger inside c3.** First 1m bar of c3 with low ≤ low[c2] (a touch counts) comes in an earlier 1m bar than the
   first 1m bar of c3 with high ≥ high[c2]. Both must happen inside c3. Same 1m bar for both (order unknown): no
   trigger (owner 2026-11-15). A high touch before the first low touch: no trigger.
4. **Entry candle** = the 15m candle holding the 1m bar that reached high[c2]. Act at its close (when its last minute
   is missing, the signal comes when the candle is known complete; its prices are its own bars only).
   Stop = that 15m candle's low. `close` = its close.
5. **Entry** (buy limit, works from the next 1m bar): close − stop ≤ `risk` ticks: limit at `close`; otherwise limit at
   stop + `risk` ticks. Owner example 13 Nov 2026 13:30 MYT 15m: low 88.17, close 88.39 (22 ticks), risk 15: limit
   88.32. No trade if close = stop or if price touched TP between the break and the signal (so limit < TP).
   Code check: the owner example gives stop 88.17, limit 88.32 (risk 15), TP 89.15, signal at the 13:44 MYT 1m close.
5a. **`confirm`** (owner 2026-11-15, added after the first 6 dev runs): `0` places the order at the break candle's
   close (rule 5). `1` waits for the next 15m candle: if its low touches or breaks the break candle's low, no trade;
   otherwise the same limit (from the break candle's close, rule 5) and stop are placed at that next candle's close.
   The next candle must start in the same trading day and contract. TP touched through that close: no trade.
   Rules 4 and 5a: the signal bar must be in the trading day and contract of the bar that took candle 2's high (a
   candle missing its last minute can complete at the next session's first bar); otherwise no trade.
   Owner example with `confirm` 1: the 13:45 MYT 15m candle stays above 88.17, order 88.32 placed at the 13:59 close.
6. **Target** = TP (latest 1H swing high). No breakeven, no trailing, 1 contract.
   `tp` (owner 2026-11-16, added after the first 9 dev runs): `swing` (default) as above; a number N = fixed target
   N ticks from the limit (15, 30, 45, 60, 75 tested). With a fixed target the swing high plays no part after the setup:
   rule 5's "TP touched between the break and the signal" check is skipped (the order does not exist yet), and rule 7
   cancels the unfilled order at the first touch of the fixed target.
7. **Unfilled order** is cancelled (owner 2026-11-15) at the first 1m bar that touches TP (the order does not work in
   that bar) or at the next setup signal (either side; the order works through that bar), and by the engine at the
   trading-day change, contract change and 3:10 PM CT.
8. One order or position at a time (engine default, no overlap). A setup signal while a position is open is ignored.

Open (owner): a second entry version with a 5m stop is not final and is not tested.

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
| `risk` (max entry-to-stop, ticks) | 15 | 15, 20, 25 |
| `outside` | skip | skip, strict |
| `confirm` (wait for the next 15m candle) | 0 | 0; 1 with `outside` strict only |
| `tp` (target) | swing | swing; 15, 30, 45, 60, 75 ticks with risk 15, strict, confirm 1 only |
| `swing_tf` | 1h | fixed |
| `entry_tf` | 15m | fixed |

Total combinations on dev: **13**. 6 (3 `risk` × 2 `outside`, `confirm` 0) declared 2026-11-15 before the first run;
3 (`confirm` 1, `outside` strict, `risk` 15/20/25) added the same day by the owner after seeing them; 4 (`tp` 15, 30,
45, 60 on risk 15, strict, confirm 1) added 2026-11-16 after seeing those; 1 (`tp` 75) added the same day after
seeing them. Every tuned number reports best of 14.
Validation: the best one, frozen, only if it passes the dev gates.

## Pass criteria
Gates from docs/PROTOCOL.md (dev: ≥ 200 trades, PF ≥ 1.25, ≥ 70% years positive, Combine pass rate ≥ 50%, cost per
pass ≤ $500), plus: the neighbouring `risk` values also profitable.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-15 | dev | touch, no exit slip | 1,207 | −$4,486 | 0.947 | 5.0% | $7,350 | risk 15, skip (default); best net of 6 (gross +$390) |
| 2026-11-15 | dev | touch, no exit slip | 1,249 | −$5,396 | 0.943 | 9.5% | $3,822 | risk 20, skip |
| 2026-11-15 | dev | touch, no exit slip | 1,274 | −$8,607 | 0.915 | 9.2% | $2,564 | risk 25, skip |
| 2026-11-15 | dev | touch, no exit slip | 1,174 | −$4,533 | 0.945 | 9.2% | $3,700 | risk 15, strict (gross +$210) |
| 2026-11-15 | dev | touch, no exit slip | 1,216 | −$5,233 | 0.943 | 14.2% | $7,497 | risk 20, strict; best pass rate of 6 |
| 2026-11-15 | dev | touch, no exit slip | 1,240 | −$8,410 | 0.915 | 13.2% | $3,822 | risk 25, strict |
| 2026-11-15 | dev | touch, no exit slip | 715 | +$2,301 | 1.044 | 24.1% | $7,105 | risk 15, strict, confirm; best of 9 (gross +$5,190) |
| 2026-11-15 | dev | touch, no exit slip | 735 | −$279 | 0.995 | 20.1% | $7,252 | risk 20, strict, confirm |
| 2026-11-15 | dev | touch, no exit slip | 750 | −$1,870 | 0.970 | 10.0% | $7,350 | risk 25, strict, confirm |
| 2026-11-16 | dev | touch, no exit slip | 983 | −$1,551 | 0.973 | 1.3% | no pass | risk 15, strict, confirm, TP 15 ticks |
| 2026-11-16 | dev | touch, no exit slip | 1,235 | −$6,049 | 0.936 | 0.0% | no pass | risk 15, strict, confirm, TP 30 ticks |
| 2026-11-16 | dev | touch, no exit slip | 1,362 | −$992 | 0.991 | 17.6% | $1,923 | risk 15, strict, confirm, TP 45 ticks |
| 2026-11-16 | dev | touch, no exit slip | 1,437 | +$5,385 | 1.042 | 32.4% | $1,127 | risk 15, strict, confirm, TP 60 ticks; best net and pass rate of 14 (gross +$11,190) |
| 2026-11-16 | dev | touch, no exit slip | 1,477 | +$4,663 | 1.034 | 21.7% | $1,323 | risk 15, strict, confirm, TP 75 ticks (gross +$10,630) |

Dev, in-sample, best of 6. Years positive 4–6/12. Win rate 24–27%; avg win ~$270, avg loss ~$93–110. Gross is
about zero (−$3,460 to +$390); fees (~$4,900) decide the sign. `outside` barely matters (skip adds ~35 trades).
Risk 15, skip by side: long 571 trades −$4,037, short 636 trades −$449. Exits: ~75% stop, ~21% target, rest
flatten 3:10 PM CT. Ledger hashes: bf04e5c78de2, c787d55ba166, b6eb6f31e0ae (skip 15/20/25), 86338ebb1a27,
c27be5da83a1, b90f8c66676e (strict 15/20/25).

Spot-checked against raw bars (risk 15, skip): long 2014-12-28 17:15 CT 15m (c1 Fri 15:00, c2 Fri 16:00, c3 Sun
17:00; limit 55.23 = low 55.08 + 15, stopped at 55.08); short 2017-01-27 02:15 CT 15m (c2 low 53.74 equal to c1,
c3 took 54.01 then 53.74; limit 53.73 = close, stop 53.85 not touched, target 52.79 hit 10:35 CT). Both match.
`confirm` 1 (strict; added after seeing the first 6; hashes 3ae268f690e7, 4c4e99c1a219, 24c012b54e85 for risk
15/20/25): ~40% fewer trades, gross positive in all three, best PF 1.044 (risk 15, best of 9), years positive 6–7/12,
still far below every gate (PF 1.25, pass rate 50%, cost/pass $500). Risk 15 by side: long 340 trades −$1,484, short
375 trades +$3,785. Spot-checked long 2017-12-15 (c3 22:00 CT took 57.13 then 57.20; break candle 22:15 low 57.16;
22:30 candle held at 57.17; order placed at the 22:44 close, filled at the 22:45 open 57.19 below the 57.20 limit;
TP 57.22, a 3-tick target). TP can sit a few ticks from entry: the rules set no minimum.
Point-in-time fix (2026-11-15, Codex review): candle 3 was only scanned once its hour was complete, so in live or
forward data a signal inside the newest hour appeared only after that hour closed. Candle 3 now uses the 1m bars of
the clock hour after candle 2, finished or not; a test cuts the data at each signal bar and checks the signal is
already there. All 9 dev runs re-run: identical figures (the bug only touches the last hour of the data). Current
hashes: skip 15/20/25 4bd0f5036955, 0bf737182a4b, 9aa0608226ce; strict 34c242e01f32, ba5cbcdcb832, 79bed0772a77;
strict confirm 4bf74edcb012, 4633bd19b28e, 20c3bafdee22. The earlier 9 rows stay in the ledger.
Cancel fix (2026-11-15, Codex review): a setup whose order is cancelled by a TP touch on its first working bar
was dropped before the cancel times were set, so it did not cancel an older unfilled order (rule 7). Now every
placed order counts. Such setups are rare on dev (20 of 1,412 triggers with `confirm` 0, 13 of 892 with `confirm` 1)
and none met a still-working older order: all 9 re-runs identical. Current hashes: skip 15/20/25 df864b047e46,
290a98ffcadc, 47c4d5ed30ee; strict ffc8f978a65d, 74654aa79407, 2a820a55946e; strict confirm 27408642fa7a,
f3732a3e8c78, e16633405778.
Session fix (2026-11-15, Codex review): a 15m candle missing its last minute completes at the next bar, which can
be the first bar of the next session or contract; the old setup then placed its order there. Now the signal bar
(break candle, or the next candle with `confirm` 1) must be in the trading day and contract of the 1m bar that took
candle 2's high; otherwise no order. Dev: 0 such setups with `confirm` 0, 3 with `confirm` 1; all 9 re-runs
identical. Current hashes: skip 15/20/25 94a11d96ebce, 90a9f802eb54, f2d0d64ca5a8; strict 8e0b071e38ac,
444aefd3c17b, ae99557b7ae3; strict confirm 758b83b5d21c, d220f4edc7aa, e0dbb5b0e436.
Fixed TP (2026-11-16, best of 13, in-sample): TP 15 / 30 / 45 / 60 ticks give PF 0.973 / 0.936 / 0.991 / 1.042,
years positive 5 / 4 / 6 / 7 of 12, win rate 36% / 24% / 20% / 18%. More trades than the swing target (983–1,437 vs
715): shorter trades free the one-position slot, the pre-order swing check is gone, and fewer orders are cancelled
by an early target touch. Results are not monotonic in TP (30 is the worst), so the TP 60 edge looks like noise,
not a trend. TP 60 is the best pass rate of all 13 (32.4%) and PF matches the swing target (1.042 vs 1.044); both
stay far under the gates. Swing-target re-run with the `tp` code: identical (715 trades, +$2,301). Spot-checked
TP 60: every target exit is 60 ticks from the entry or more (up to 68 when price opened through the limit); short
2013-08-02 entry 107.93, target 107.33 hit at 12:31 UTC, highest high 107.99 stays under the stop. Hashes: TP 15
411dff8ab2ff, 30 5bbe555edea7, 45 08607e3721f8, 60 8cf495b86d35; swing re-run 31949a423a66.
TP 75 (2026-11-16, best of 14, in-sample): PF 1.034, win rate 16%, years positive 8/12 (the most of any version),
pass rate 21.7%, drawdown −$7,655. Slightly below TP 60 on net, PF and pass rate, so the curve flattens past 60.
Target exits are 75–83 ticks from entry; spot-checked long 2016-10-19 (entry 50.78, target 51.53; high 51.52 before
the exit bar, low 50.77 stays above the stop). Hash 74f373c054d0.
Note from the first check: c1 to c3 may span the weekend or the daily halt (candles are consecutive in the
candle list, as in the swing rule); the owner confirmed this is intended (2026-11-16).

All results in-sample unless the period is holdout or forward; tuned rows say best of N.
