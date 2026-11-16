# Study: swing confluence across timeframes

A study, not a strategy: no orders, no Combine. It measures what price does after a swing point under each
multi-timeframe context, so later strategies start from measured behaviour instead of chart memory.

## Question

When a new swing point is confirmed on one timeframe, does the swing structure of the other timeframes
(1m, 5m, 15m, 1h, 4h, 1d, 1w, 1mo) change whether that point **holds** or **fails**?

Owner's belief (2026-11-16): market structure + swing points are the key; the three swing strategies
(manipulation, failure reversal, failure) may lack confluence from other timeframes. Pure price action only:
highs and lows that define swing points. No indicators; candle open/close is not used as a feature.

## Event and outcome

- **Event**: a new swing low (or high) on a base timeframe B in {1m, 5m, 15m, 1h, 4h, 1d}, at the 1m bar where it
  becomes known (`swing_state`, point-in-time). Rule-5 replacements are new events (flagged).
- **Hold / fail**: for a swing low L with the swing high H above it on B: **hold** = a later high > H prints before a
  low < L; **fail** = the reverse. Swing high: mirror. Same-bar tie = unknown, left out.
- **Fair rate**: under a random walk the hold rate is pure geometry: `(c - L) / (H - L)` with c the price where the
  event becomes known (the close of that 1m bar; used only for this baseline, never as a feature). A context only
  matters if its hold rate beats its **own** fair rate. Without this, "price near the low holds less" would look like
  a pattern when it is just distance.
- Also stored: time to resolution, deepest retest before a hold, furthest run before a fail, roll / day crossed.

## Context features (point-in-time at the event bar, every timeframe T)

All aligned to the event's direction (a swing low expects up; a swing high is mirrored):

| Feature | Meaning |
|---|---|
| `T_trend` | with (HH+HL for a low event), against, expand (HH+LL), contract (LH+HL) from T's last two highs/lows |
| `T_leg` | T's current leg: with (newest T point is a low, for a low event) or against |
| `T_pos` | where the event price sits in T's range [sl, sh]: 0 = at T's own extreme, 1 = at the opposite one; < 0 beyond |
| `T_sweep` | the event took out T's last same-side point known before the event candle began (liquidity grab) |
| `retrace` | event leg / previous leg on B (> 1 = lower low for a low event) |
| `ct_hour`, `weekday` | when the event became known (CT) |

Raw levels per timeframe are stored too, so a miner can build its own features.

## Rules

- **dev only** (2010-06 to 2021-12). Validation and holdout are not touched by this study.
- Events whose resolution crosses a contract roll are excluded (prices are not back-adjusted).
- A finding needs: n >= 300, edge (hold rate - fair rate) >= 3 points, same sign in >= 9 of 12 dev years,
  and survives Benjamini-Hochberg at 5% across **every** cell tested (the count is the trial budget, reported).
- Two independent miners (Claude, Codex) work from the same event table. Codex also audits the table for look-ahead.
  A finding both find independently ranks above a finding only one finds.
- A finding becomes a strategy only through a new `docs/strategies/<name>/README.md` and the normal protocol.

## Files

- `studies/swing_confluence/build.py`: builds `data/studies/swing_confluence_dev.parquet`
- `studies/swing_confluence/claude_findings.md`, `codex_findings.md`, `codex_audit.md`: results

## Log

- 2026-11-16 round 1: table built, Claude scan (705 + 12,907 cells), Codex audit + mining (15,643 cells).
- 2026-11-16 round 2: 8 audit defects fixed (see `studies/swing_confluence/claude_findings.md` §0), table rebuilt
  (1,914,711 events), scans re-run (724 + 13,640 cells). Edges found: 3–7 points of hold rate; best (Codex A) is
  about +2 ticks per trade after fees at the confirmation price, ~0 with a pullback limit entry. In-sample, dev only.

## Round 3 hypotheses (owner 2026-11-16, declared before the run)

H1 **Nested manipulation** (owner): an LL that breaks the base timeframe's HL after an HH (base structure
HH-HL-HH-LL, trend code 2 "expand"; highs mirrored) is a manipulation when the higher timeframe T's own swing low is
not taken (`T_sweep` 0) and T is still up (`T_trend` with, or `T_leg` with). Prediction: such events hold (break the
base HH first) more than fair; the same LL that also takes T's low holds less. Bases 1m/5m/15m/1h, T every higher
timeframe up to 1d. Cells: base × T × {T_sweep 0/1} × {T_trend with / other}.

H2 **Forming higher-timeframe candle** (owner, 13 Nov 2026 example: the 1h candle 3 had closed, the 4h candle 3
had not): at the event bar, the higher timeframe candle that holds it is still open. Feature: has the forming T
candle already taken the previous complete T candle's low (for a low event; high mirrored)? and is the event its
own extreme so far. T in 15m/1h/4h/1d for bases below T.

H3 **Previous-day high/low** (why `purple_pa` comes closest): an event whose extreme is the first take of the
previous CME day's low (low event; high mirrored), and an event that stops short of it, against all other events.
`purple_pa` itself: first test of PDH/PDL, then a 3-candle gap away (fast departure) as proof.

Trial budget: all cells of H1-H3 count together (reported); same gates as above (BH 5%, edge ≥ 3 points, both
halves same sign).
