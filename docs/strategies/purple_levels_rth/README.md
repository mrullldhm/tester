# purple_levels_rth (purple_levels, regular trading hours only)

Status: forward (frozen 2026-11-17; paper trading only, no paid Combine)
Code: `strategies/purple_levels_rth.py` (filters `strategies/purple_levels.py`, levels `all`, 5m)
Source: `studies/purple_levels_improve/` (Claude + Codex, dev only, 2026-11-17).

## Honesty first
This is **not an a-priori hypothesis**. Both researchers saw on dev that `purple_levels` all 5m earns its profit in
08:30-13:30 CT before choosing that window: a post-hoc, mechanism-informed selection on top of a family that was
already best of 12+ dev runs and failed validation 2022-2024 (`docs/strategies/purple_levels/README.md`).
Validation is spent for this family and is not re-run. The holdout (2025-2026-11-12) is kept unused: at ~23 trades a
year it is far too short to confirm the edge (Codex power estimate: 485-860 trades for 80% power at the dev strict
edge) and could only kill it. The only judge is **forward data after the freeze**.

## Hypothesis
Fixed levels (previous day, previous week, newest 4h and daily owner swing high/low) are reference points for the
participants who trade CL in the regular session (old pit hours 08:30-13:30 CT, most of the day's volume). A first
test of such a level followed by a fast departure (the purple gap) marks aggressive reversal flow plus trapped
breakout traders; the limit at the gap edge supplies liquidity into the pullback. Overnight, the same touches happen
in a thin book: on dev their expectancy is about 0R once an entry has to trade through the limit (adverse selection).

Dev evidence (in-sample, selected): all 5m strict fills, RTH entries +0.21R net per trade (270 trades, 11/12 years
positive) vs overnight ≈ 0R; RTH minus non-RTH controlling for stop size and year +0.15R (SE 0.077, BH q 0.06,
BY q 0.39: not robust after multiplicity correction).

## Rules
Everything is `purple_levels` with `levels=all`, `tf=5m` (purple_pa mechanics: first test plus one role-flip retest,
gap confirmation within 4 candles, limit at the gap edge, stop 1 tick beyond the extreme since the test, 1R target,
1 contract, flatten 3:10 PM CT). One addition:
- **Session**: a signal is kept only when its decision time (close of the signal 1m bar, CT) is at or after 08:30
  and before 13:30. Its limit works for 20 minutes or until 13:30 CT, whichever comes first. Open positions keep
  their normal exits (target, stop, 3:10 PM flatten). Setup history (arming, tests) still runs from the day's open:
  a level first tested overnight is not fresh at 08:30.
- **Fills for judging**: strict, `--through 1` (an entry counts only if price trades 1 tick beyond the limit).
  Touch-fill results are reported beside it, never instead of it.

## Parameters and trial budget
No grid. One frozen specification: levels all, tf 5m, confirm 4, expire 4 candles, rr 1.0, window 08:30-13:30 CT,
1 CL. Dev runs: 2 (touch, strict), only to record the frozen dev baseline for the forward comparison. Discarded
alternatives (counted, not run as strategies): first-test-only, mid-gap entry, fixed-dollar risk sizing
(Codex, `studies/purple_levels_improve/codex_report.md`, `codex_round2.md`).

## Forward plan (pre-registered)
- Freeze: 2026-11-17 (this doc + code hash in the ledger). No parameter changes during the forward year; a change
  is a new strategy with a new freeze.
- Data: CL bars after 2026-11-12 (`--period forward`), plus the owner's TopstepX paper account.
- Logging: every signal from `python -m cltester.cli test purple_levels_rth --period forward --through 1` and every
  paper order go into `docs/strategies/purple_levels_rth/forward_journal.csv` (versioned; `results/*/` is git-ignored): signal time, side, limit,
  stop, target, whether the paper order filled, fill price, exit, net, and a note on any difference from the
  backtest (missed fill, queue, slippage, rule error).
- Review date: **2027-11-17**, once. No interim performance peeking that changes anything. Safety stop: pause paper
  trading only for an execution/rule error, not for a losing streak.
- Primary metric: net $ per trade under strict fills vs the dev strict baseline below. Secondary: paper fill rate vs
  backtest fill rate, Combine feasibility. One year (~23 trades) cannot prove the edge; it can show whether execution
  matches the backtest and whether the result is in the dev range or clearly outside it.

## Pass criteria
Not a Combine candidate (dev cost per pass ≈ $1,180 vs the $500 gate; sizing does not fix it, Codex round 2).
Forward review asks only: (1) paper fills match backtest fills (≥ 80% of backtest strict entries also filled on
paper), (2) forward strict net per trade is not clearly negative. Both yes → continue forward collection; any no →
drop.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-17 | dev | touch, no exit slip | 273 | +$23,747 | 1.846 | 75.0% | $1,015 | 11/12 years, max DD −$2,659, $87.0/trade (390888dd9cf5; final code 1129ea203322, identical) |
| 2026-11-17 | dev | strict through 1 | 264 | +$20,243 | 1.714 | 74.9% | $1,176 | **frozen baseline**: 11/12 years, $76.7/trade, win 61.0% (5e96bb8fd259; final code 7955f919e3e9, identical: frozen hash) |

Dev, in-sample, post-hoc selection (see "Honesty first"); not evidence of an edge. The strict run reproduces Codex's
independent implementation exactly (264 trades, $76.68/trade, cost per pass $1,176). Spot-checked against raw bars
(strict): long 2012-04-10 limit 101.37, 11:39 CT bar low 101.34 (traded through), stop 100.74 hit 13:20 CT (low
100.72), target 102.00 not reached (high 101.40); long 2021-04-07 limit 58.98, 10:16 CT low 58.93, stop 58.51 hit
10:28 CT (low 58.38), target 59.45 not reached (high 59.05). Both match.
All results in-sample unless the period is holdout or forward; tuned rows say best of N.
