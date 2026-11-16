# pd_swing (previous-day level + owner swing structure)

Status: dropped (2026-11-16: all 10 variants fail every gate; 0-72 trades on dev)
Code: `strategies/pd_swing.py` (tests: `tests/test_pd_swing.py`)
Source: swing confluence study (`docs/studies/swing_confluence/`), Codex round 3 proposal §5, owner 2026-11-16
("try all" trigger points). Swing points: owner rule only (`cltester/swings.py`, `swing_state`).

## Hypothesis
The study found that swing points alone are a coin flip (hold rate = random-walk geometry) and that multi-timeframe
snapshots move it by 3-7 points at most. `purple_pa` (first touch of the previous day's high/low, 3-candle gap,
1R bracket) is the closest strategy so far: +$30.66 gross per trade on 15m, stop exits median 28 ticks. Its level is
fixed before the day starts and cannot be replaced, unlike a live swing point. Hypothesis: the owner's structure
(higher-timeframe swing intact, lower-timeframe failure then reclaim) adds selection on top of purple's fixed level
and purple's cost structure (wide stop, 1R, few trades). If the structure adds nothing, P1-P3 will match or trail the
controls.

## Shared rules (all variants except the controls)
- Levels: previous CME trading day's high (PDH) and low (PDL) from raw 1m bars.
- Base timeframe `tf` with context timeframe `ctx`: pairs 5m/1h and 15m/4h only.
- A level is **armed** after a completed base candle lies wholly above it (support, long) or wholly below it
  (resistance, short). The first touch (low ≤ PDL from above; high ≥ PDH from below) uses up the level for the day,
  traded or not. No role-flip retest. One attempt per level per day.
- **Protection**: at the touch, freeze the `ctx` swing low (long) / swing high (short) from `swing_state` at the bar
  before the touch. Cancel the setup (and any unfilled order) if it breaks before the fill.
- **Gap** (purple's proof of departure): bullish at candle q when high[q−2] < low[q]; bearish mirror. The first gap
  completed in the window the variant names.
- **Entry**: buy limit at low[q] (sell limit at high[q]), working from the next 1m bar for 4 base candles (clock time).
- **Stop**: 1 tick beyond the extreme from the variant's window start through q. **Target**: 1R (actual initial
  risk). No risk cap, no breakeven, 1 contract, one position at a time. Engine: touch fills, flatten 3:10 PM CT,
  day/contract change cancels. Same-1m-bar order ambiguity: no trade.

## Variants
| ID | Rules (long; short mirrors) | Trigger (owner Q1 "try all") |
|---|---|---|
| C | `purple_pa` unchanged (`tf` 5m, 15m). Reference only | its own |
| P1 | First armed touch of PDL; at the touch the `ctx` structure is HH+HL (`ctx_sh > ctx_sh2`, `ctx_sl > ctx_sl2`). Gap within 4 base candles after the touch | touch |
| P2-a | First touch of PDL; within 4 base candles after it, price strictly breaks a base swing low known at the touch (the HL break). Gap window starts at that break, ends 4 base candles after the touch | HL break |
| P2-b | As P2-a, then a new base swing high confirmed after the break (the LH), then a strict break of it (reclaim) before protection breaks. Gap window starts at the reclaim, ends 4 base candles after it | LH reclaim |
| P3-a | Owner manipulation at the level. Base candle B first breaks a base swing high known before B starts (no high above it since its candle); the next candle C touches B's low (low[C] ≤ low[B]) and B is the owner swing high at C's completion (`swing_state` price and candle). B or C is the day's first armed touch of PDL (support). Protection = `ctx` swing low frozen before B starts. Gap window: q from C+1 to C+4 | third candle close |
| P3-b | As P3-a, then B's high reclaimed (a candle r ≤ C+3 with high > high[B]) before any candle takes C's low. Gap window: q from r+1 to C+4 | B reclaim |

P3 is the owner's Swing Point Manipulation placed at the previous-day level: the dip that takes B's low into PDL is
the stop run, the trade is long (short mirror: B breaks a base swing low, C touches B's high, PDH first touch, B's
low reclaimed). Stop for P3: 1 tick beyond the extreme from B through q.

Windows (all variants): every candle in a window is in the same trading day and contract; protection must not break
(long: no 1m low below it) from the window start through q. P2-b: the LH and the reclaim must come in the same
trading day; a P2 gap needs q−2 ≥ the break (or reclaim) candle − 1, as purple.

## Parameters and trial budget
| Parameter | Grid |
|---|---|
| `variant` | C, P1, P2-a, P2-b, P3-a, P3-b |
| `tf`/`ctx` | 5m/1h, 15m/4h (C: 5m, 15m) |

Total combinations on dev: **12** (declared 2026-11-16 before any run). The two C rows reuse the existing
`purple_pa` code and count in the budget. Every tuned number reports best of 12. No stop, target, expiry or time
grids. Anything added later is a new declared budget.

## Pass criteria
`docs/PROTOCOL.md` dev gates (≥ 200 trades, PF ≥ 1.25, ≥ 70% years positive, Combine pass rate ≥ 50%, cost per pass
≤ $500). In addition, a P variant must beat its control on gross $/trade on the same `tf`; otherwise the structure
adds nothing and the variant is dropped even if it passes. Trade list spot-checked against raw bars before any
result is called real.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-16 | dev | touch, no exit slip | 11 | +$626 | 1.98 | — | — | P1 5m/1h, gross +$60.9/trade (n too small) |
| 2026-11-16 | dev | touch, no exit slip | 15 | −$1,681 | 0.41 | 0% | — | P1 15m/4h |
| 2026-11-16 | dev | touch, no exit slip | 21 | −$885 | 0.47 | — | — | P2-a 5m/1h |
| 2026-11-16 | dev | touch, no exit slip | 38 | −$2,704 | 0.62 | 0% | — | P2-a 15m/4h |
| 2026-11-16 | dev | touch, no exit slip | 27 | −$579 | 0.81 | 0% | — | P2-b 5m/1h |
| 2026-11-16 | dev | touch, no exit slip | 72 | +$989 | 1.09 | 68.8% | $7,056 | P2-b 15m/4h; best net of 12; gross +$17.8/trade < control $30.7 |
| 2026-11-16 | dev | touch, no exit slip | 1 / 4 | −$164 / −$396 | — | — | — | P3-a 5m / 15m |
| 2026-11-16 | dev | touch, no exit slip | 1 / 0 | −$164 / $0 | — | — | — | P3-b 5m / 15m |
| 2026-11-16 | dev | touch, no exit slip | 591 | +$12,732 | 1.24 | 55.0% | $1,470 | control: purple_pa 5m (hash unchanged) |
| 2026-11-16 | dev | touch, no exit slip | 545 | +$14,508 | 1.20 | 38.6% | $1,064 | control: purple_pa 15m (hash unchanged) |

Dev, in-sample, best of 12. Every P variant fails the trade-count gate (≥ 200) by a wide margin and none beats its
control on gross $/trade except P1 5m (11 trades: noise). Why so few: on dev 5m, 2,813 first touches; about one in
six has a gap within 4 candles; the structure filters keep ~15% of those. P3: the owner's manipulation candle lines
up with the day's first PDL/PDH touch 61 times (5m) / 76 (15m) in 11.5 years, and the context swing low (high)
survives in only 5 / 19 of them, because a sweep into the previous-day level usually also takes the 1h/4h swing.
Verdict: adding the owner's structure to purple's mechanics removes ~90% of its trades without raising gross per
trade. The structure filters do not select better bounces.
Spot-checked against raw bars (P2-b 15m/4h): long 2010-09-07 (PDL 73.80 touched 18:30 CT low 73.69, gap 20:30 CT
high[q−2] 73.93 < low[q] 74.06, entry 74.06, stop 73.68: match); long 2010-11-25 (PDH 84.21 touched from above at
18:00 CT, reclaim and gap at 22:00 CT, stop 83.69 one tick under the 83.70 low since the touch: match, and it shows
P2-b's weakness: no deadline, so a touch can become a slow breakdown hours before the "reclaim").

Review fix (2026-11-16, Codex adversarial review): the frozen protection was checked only through the gap candle q,
so an order could still fill after protection broke (a gap through it). Signals now carry it as `void`; the engine
cancels a working order when price breaks it first, and a bar that breaks it and reaches the limit is cancelled
(order unknown; docs/ENGINE.md). All 10 dev runs re-run: identical (protection sits at or beyond the stop, so only a
gap through both could trigger it, and dev had none). Current hashes: P1 835d76f0a8d4/30bf474e74d1, P2a
cb68a49d3f2f/bf6d9b80fb85, P2b f4e089e13af8/ab4926dead63, P3a c11937a69f34/733aca0d6507, P3b e8d57e5111e5/6ea0baeb8b94
(5m/15m). Same review: negative `--through` values are now refused (they let orders fill before price reached them).
Second review fix (2026-11-16, Codex adversarial review): the void check looked at the whole bar's low before the
fill, so a bar that opened between the limit and the void (or touched the limit on the way down) and then broke the
void lost a real fill and its stop-out. Now: open beyond the void cancels; otherwise the fill comes first (price
reaches the limit before the void) and the void no longer matters. All 10 dev runs re-run: identical again (same
hashes: the hash covers strategy code, not the engine). Third review fix (same day): a void-cancelled order was treated as ending one bar early, so a
signal on the bar before the cancellation could be accepted while the order still worked; now the engine frees the
slot from the cancelling bar's close. Re-run: identical. Fourth review fix (same day): `--set tf=15m` alone kept the 5m default
context (1h); `ctx` now defaults to `auto` (5m→1h, 15m→4h) and any other pair is refused. All runs on record used
the declared pairs explicitly; re-run identical. Fifth review fix (same day): the gap check read candle q−2 without checking its contract (a roll
just before the touch could fake a gap), and protection was checked only through candle q, not through the later bar
where q is known when its last minute is missing. Now every candle the gap reads shares the setup's contract, and
protection is checked on raw 1m bars through that availability bar (`find_gap`, tested). Re-run: identical. Sixth review fix (same day): when q's last minute is missing, the bar where q becomes known can be the
first bar of the next contract (midnight UTC roll), so an old-contract setup could trade on the new contract; now
every raw 1m bar from the setup window through that availability bar must be one contract. Re-run: identical
(hashes P1 876fd9d58cb3/736424cb9cc6, P2a e31887126912/73c34c089f92, P2b 6cd6f30ec376/b49d4be51b86, P3a
1106c0c5fe06/2ad1eb1f1294, P3b 3a9a3c420981/7fd21daa2669).

All results in-sample unless the period is holdout or forward; tuned rows say best of N.
