# purple_levels (purple_pa mechanics on more fixed levels)

Status: dropped (2026-11-16: `all` 5m and `nopd` 5m both fail validation 2022-2024; dev edge did not repeat. Holdout not run)
Code: `strategies/purple_levels.py`
Successor: `purple_levels_rth` (RTH-only, frozen 2026-11-17 for forward paper only; docs/strategies/purple_levels_rth/README.md)
Source: `purple_pa` (docs/strategies/purple_pa/README.md) + swing confluence study. Swing points: owner rule only.

## Hypothesis
`purple_pa` earns +$26-31 gross per trade but trades only ~47 times a year (15m): too slow for the Combine target.
Its edge plausibly comes from a level that is fixed before the session and watched by others, tested for the first
time. Other levels fixed at the day's open should behave the same: the previous trading week's high/low and the
owner's 4h and daily swing high/low (`swing_state` at the bar before the day's first candle; the owner's swing
points used as levels, not as triggers). If so, the families together give ~2.5x the trades at the same quality.

## Rules
`purple_pa`'s rules unchanged (arming from the day's first candle open, first test plus one role-flip retest, gap
confirmation within 4 candles, limit at the gap edge for 4 candles, stop 1 tick beyond the extreme since the test,
1R target, 1 contract, flatten 3:10 PM CT). Only the level set changes, fixed for the whole trading day:
- `pd`: previous CME trading day high/low (= `purple_pa`, control).
- `pw`: previous traded week (Monday-Friday trading days) high/low, from raw 1m bars. After a week with no bars,
  the last traded week before it; a holiday-short week is used as it is. The first loaded week is never used (it
  can be partial).
- `sw4h`: newest 4h swing high and swing low known at the day's open.
- `sw1d`: newest daily swing high and swing low known at the day's open.
- `all`: the union of the four (equal prices counted once); each level armed and tested on its own; two signals on
  one bar: the first in family order (pd, pw, sw4h, sw1d; high before low) is kept; the engine trades one position at a time.

## Parameters and trial budget
| Parameter | Grid |
|---|---|
| `levels` | pd, pw, sw4h, sw1d, all; round 2: sw, nopd (5m only) |
| `tf` | 5m, 15m |
Total combinations on dev: **10** (declared 2026-11-16 before any run). `pd` must reproduce `purple_pa` exactly.

## Round 2 (declared 2026-11-16, before the validation run of `all` 5m; owner option 3)
Question: does `pd` (the weakest family per trade on 5m) dilute `all`? Two new families, 5m only, same rules:
- `sw`: 4h + daily swing levels (union).
- `nopd`: previous week + 4h + daily swing levels (`all` without `pd`).
Budget: **2** more dev runs (total 12; tuned numbers report best of 12). These are dev-only; neither goes to validation
in this round, whatever the validation of `all` 5m shows. A winner would need its own later validation decision.

## Pass criteria
`docs/PROTOCOL.md` dev gates. A new family must match `pd` on gross $/trade (same `tf`) within noise, or it dilutes
the edge; `all` must keep ≥ 90% of `pd`'s gross $/trade while adding trades.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-16 | dev | touch, no exit slip | 591 | +$12,732 | 1.239 | 55.0% | $1,470 | pd 5m (= purple_pa, identical) |
| 2026-11-16 | dev | touch, no exit slip | 545 | +$14,508 | 1.196 | 38.6% | $1,064 | pd 15m (= purple_pa, identical) |
| 2026-11-16 | dev | touch, no exit slip | 281 | +$11,725 | 1.483 | 44.7% | $2,368 | pw 5m, gross $45.8/trade |
| 2026-11-16 | dev | touch, no exit slip | 236 | +$8,377 | 1.259 | 42.9% | $1,789 | pw 15m |
| 2026-11-16 | dev | touch, no exit slip | 490 | +$16,060 | 1.404 | 80.6% | $1,421 | sw4h 5m, 11/12 years |
| 2026-11-16 | dev | touch, no exit slip | 489 | +$8,974 | 1.142 | 39.5% | $1,862 | sw4h 15m |
| 2026-11-16 | dev | touch, no exit slip | 242 | +$14,372 | 1.715 | 76.8% | $1,776 | sw1d 5m, gross $63.4/trade, 11/12 years |
| 2026-11-16 | dev | touch, no exit slip | 219 | +$5,525 | 1.181 | 48.1% | $2,385 | sw1d 15m |
| 2026-11-16 | dev | touch, no exit slip | 1,161 | +$36,300 | 1.368 | 62.8% | $584 | **all 5m**: 100 trades/yr, 11/12 years, max DD −$4,796; best of 10 |
| 2026-11-16 | dev | touch, no exit slip | 1,009 | +$22,174 | 1.165 | 44.6% | $860 | all 15m |

Dev, in-sample, best of 10 (and `pd` itself was best of 2 before). Every new family beats `pd` on gross $/trade on
5m (pw $45.8, sw4h $36.8, sw1d $63.4 vs pd $25.6); on 15m only pw and sw1d do. 5m beats 15m in every family.
**all 5m** against the dev gates: trades 1,161 ≥ 200 ✓, PF 1.368 ≥ 1.25 ✓, years 11/12 ≥ 70% ✓, Combine pass rate
62.8% ≥ 50% ✓, cost per pass $584 > $500 ✗. Robustness: long 597 trades +$16,688, short 564 +$19,611; top 10 days
29% of net, +$18,591 without the top 20 days; only 2019 negative (−$3,045); 2011 is the best year (+$9,041).
Fills that traded through the limit +$33.0/trade (n 658) vs touch-only +$29.0 (n 503): not a touch-fill artefact.
Exits: 625 target, 489 stop (median 16 ticks, quartiles 10/25), 41 flatten, 6 roll.
Spot-checked against raw bars (all 5m): short 2016-07-15 (PDH 45.80 touched 06:55 CT high 45.90, bearish gap
low[q−2] 45.83 > high[q] 45.81, sell 45.81, stop 45.93, target 45.69 hit); long 2019-11-25 (PDL 57.50 touched 07:05
CT low 57.47, gap high[q−2] 57.66 < low[q] 57.72, buy 57.72, stop 57.46 hit). Both match.
Hashes: pd b29d51b075ee/219ca4c7af51, pw 3904aeffef2a/a84e4ebac2dd, sw4h ac626fc1aa31/afd7232773fe,
sw1d 45af30ea0d41/186fd2d2f373, all 9a9f533e54c4/f3d5cb329b4b (5m/15m).

Code review fixes (2026-11-16, production-eng gate PASS): `day_levels` takes the day index as an argument; the first
loaded week is never a previous week. `all` 5m dev re-run on the final code: identical (1,161 trades, +$36,300,
hash 0d7bec09b33d).

Round 2 (dev, 5m, best of 12): `sw` 705 trades +$26,012 PF 1.448 11/12 years pass 73.4% cost/pass $800
(bb31fdf99f48); `nopd` 849 trades +$32,980 PF 1.474 11/12 years pass 74.1% cost/pass $617 (83645049492b). Both
higher PF than `all`, fewer trades, cost per pass still above $500. Not validated (declared).

**Validation (2022-2024, `all` 5m, frozen, run once, 2026-11-16; it missed the dev cost-per-pass gate):**

| Period | Trades | Net | PF | Years + | Max DD | Pass rate | Cost/pass |
|---|---|---|---|---|---|---|---|
| validation | 353 | +$6,324 | 1.125 | 1/3 | −$7,452 | 47.4% | $719 |

Against the validation gates (trades ≥ 60, PF ≥ 1.10, pass ≥ 40%, cost/pass ≤ $750) it passes on paper. Robustness
says it does not hold: 2022 −$1,598, 2023 +$8,125, 2024 −$203; the top 10 days make $10,593, the other trades
−$4,270; longs +$9,189, shorts −$2,865; and the profit sits in touch-only fills (+$58.4/trade, n 113) while fills
that traded through the limit lose (−$1.2/trade, n 240). On dev that split was +$29 / +$33. A live limit order at
the touch price often does not fill, so the validation edge is most likely the fill model, not the market. Gross per
trade fell from $35.3 (dev) to $22.0. Spot-checked: short 2022-11-28 17:55 UTC sell 77.35, highest high 77.54 under
the 77.85 stop, target 76.85 touched at 20:34 UTC (low 76.85): match.
Verdict: not a holdout candidate as it stands. Holdout (once) is the owner's call.

**Strict-fill sensitivity (2026-11-16, `--through 1`: an entry fills only when price trades 1 tick through the
limit; docs/ENGINE.md).** Not the owner rule; a check on whether touch fills carry the result.

| Levels (5m) | Period | Trades | Gross/trade | Net | PF | Years + | Pass rate | Cost/pass |
|---|---|---|---|---|---|---|---|---|
| pd | dev | 537 | $16.3 | +$6,601 | 1.129 | 7/12 | 48.5% | $1,838 |
| all | dev | 1,055 | $26.7 | +$23,868 | 1.249 | 10/12 | 55.5% | $686 |
| nopd | dev | 770 | $35.2 | +$24,009 | 1.356 | 11/12 | 66.7% | $828 |
| sw | dev | 640 | $32.6 | +$18,264 | 1.322 | 10/12 | 52.6% | $1,225 |
| all | validation | 336 | $15.2 | +$3,743 | 1.075 | 1/3 | 36.0% | $719 |

Dev: the edge survives strict fills, most for the week and swing levels (`nopd` keeps PF 1.36 and 11/12 years);
the previous-day level loses most of its edge (PF 1.24 to 1.13). Validation: under strict fills `all` 5m fails the
validation gates (PF 1.075 < 1.10, pass rate 36% < 40%): 2022 −$1,744, 2023 +$5,870, 2024 −$383.
Verdict: `all` 5m failed validation. The dev result was real enough to survive strict fills, but 2022-2024 did not
repeat it. Hashes: dev pd f64db9e67861, all 246991053739, nopd 2d216a6286d7, sw c92b58abe495; validation all
246991053739.

**Validation of `nopd` 5m (owner "proceed", 2026-11-16; run once, frozen; it also missed the dev cost-per-pass gate).**
Not independent of the `all` validation above: `nopd` shares most of its trades with `all`, already run on 2022-2024.

| Fills | Trades | Gross/trade | Net | PF | Years | Pass rate | Cost/pass | Max DD |
|---|---|---|---|---|---|---|---|---|
| touch (owner rule) | 280 | $17.6 | +$3,789 | 1.092 | 2022 −$330, 2023 +$3,776, 2024 +$342 | 32.4% | $539 | −$4,281 |
| strict (through 1) | 272 | $13.5 | +$2,561 | 1.062 | 2022 −$330, 2023 +$2,971, 2024 −$80 | 18.9% | $1,078 | −$4,281 |

Fails the validation gates under both fill rules (PF < 1.10, pass rate < 40%). Same shape as `all`: without the top
10 days −$5,621; longs +$4,503, shorts −$714; touch-only fills +$63.2/trade vs traded-through −$5.0. 2023 carries
both validations. Hashes 83645049492b (touch), 2d216a6286d7 (strict).
Verdict: dropped. The fixed-level edge is real on 2010-2021 (it survives strict fills) but did not repeat on
2022-2024. Holdout is unused and stays unused for this family.

**Roll-fix re-run (2026-11-16, Codex adversarial review).** The gap could read candles from before a mid-session
contract roll, so the new contract's price jump could fake a gap. Setups whose stop window, gap candles or signal
bar span a roll are now cancelled (shared fix with `purple_pa`; `tests/test_purple_roll.py`). Every run was re-run;
these figures replace the dev rows above (validation runs are bug-fix re-runs, not new looks, and came out
identical: no roll setups in 2022-2024).

| Levels | tf | Fills | Trades | Net | PF | Years + | Pass rate | Cost/pass |
|---|---|---|---|---|---|---|---|---|
| pd | 5m / 15m | touch | 587 / 541 | +$13,599 / +$14,314 | 1.259 / 1.195 | 7 / 9 of 12 | 55.5% / 33.9% | $1,450 / $1,057 |
| pw | 5m / 15m | touch | 279 / 233 | +$12,133 / +$7,819 | 1.508 / 1.242 | | 47.2% / 40.2% | $1,776 / $1,801 |
| sw4h | 5m / 15m | touch | 485 / 485 | +$16,991 / +$9,251 | 1.438 / 1.148 | | 84.3% / 40.9% | $1,421 / $1,862 |
| sw1d | 5m / 15m | touch | 242 / 217 | +$14,372 / +$5,473 | 1.715 / 1.180 | | 76.8% / 48.0% | $1,776 / $2,385 |
| all | 5m / 15m | touch | 1,153 / 1,000 | +$38,132 / +$22,600 | 1.394 / 1.170 | 11/12 (5m) | 62.8% / 42.4% | $543 / $838 |
| sw | 5m | touch | 700 | +$26,942 | 1.472 | | 73.3% | $806 |
| nopd | 5m | touch | 843 | +$33,984 | 1.496 | 11/12 | 74.2% | $617 |
| pd / all / nopd / sw | 5m | strict | 535 / 1,049 / 766 / 637 | +$7,429 / +$25,662 / +$24,975 / +$19,157 | 1.147 / 1.273 / 1.376 / 1.343 | | 49.5% / 57.9% / 67.0% / 52.6% | $1,838 / $833 / $822 / $1,217 |

Removed trades were mostly losers, so every dev run improves slightly; no verdict changes (`all` 5m still misses the
$500 cost-per-pass gate at $543; validation unchanged, still failed).

Roll-guard refinement (2026-11-16, Codex review): the roll fix above ended a setup when an early gap candidate only
read a candle from before the roll, losing a later gap wholly on the new contract. Now a setup ends only if the touch
through the signal bar crosses a roll; such a candidate is skipped. Re-run: 1-4 trades recovered per run; dev now
pd 5m 589 / +$13,560 / PF 1.258, pd 15m 542 / +$14,400 / 1.196, sw4h 5m 489 / +$16,624 / 1.424, sw4h 15m 487 /
+$9,223 / 1.147, all 5m 1,157 / +$37,766 / 1.388 (pass 62.8%, cost per pass $580), all 15m 1,002 / +$22,572 / 1.170,
sw 5m 704 / +$26,576 / 1.462, nopd 5m 847 / +$33,618 / 1.488; strict all / nopd / sw 1.269 / 1.369 / 1.335; other
runs and both validations identical. No verdict changes.

All results in-sample unless the period is holdout or forward; tuned rows say best of N.
