# Joint verdict, Claude + Codex (2026-11-18, dev 2010-06..2021, in-sample)

Sources: `claude_findings.md` (+ `claude/`; corrected after two Codex adversarial reviews: per-run, no pooling, defined-contrast rule, joint block bootstrap), `codex_report.md` (+ `codex/`, 665 cells, BH/BY).

| Strategy | Gross edge (dev) | Verdict |
|---|---|---|
| purple_levels_rth | +0.20R net strict (only BY-significant result; same family as failed purple_levels validation) | keep frozen, forward paper (2027-11-17 review) |
| purple_levels | failed validation 2022-24 | dropped; holdout preserved |
| purple_pa | +0.06R strict, not significant; RTH filter *lowers* its total net (Codex, paired test) | drop as separate candidate |
| xtley_gap, swapnil_hm, swapnil_momentum, swing_point_manipulation, swing_point_failure_reversal, pd_swing | indistinguishable from zero | drop; no edge to optimise |
| scribd_supertrend, swing_point_failure | negative in every run (point estimate), but significance depends on configuration | drop; no edge to optimise |
| ict_ea | reliably negative in every run, by 0.3 tick (< a fee) | drop; not invertible after fees and exits |

Agreed:
1. Only the purple family has a gross edge; no unrelated strategy replicates it.
2. RTH is better than other hours in 6/7 eligible strategies (Claude, median of defined runs, touch, ticks;
   joint block bootstrap mean +2.10 ticks, 95% [+0.12, +4.18], dominated by swapnil_hm; +0.57 without it) / 8/9
   (Codex, best run, strict, R) other strategies; size small (Codex pooled +0.065R gross, BH 0.13 / BY 0.87). A general session-quality
   effect about one fee in size; it does not create an edge where the setup has none.
3. Optimising strategies with zero gross edge would be fitting noise. No production change.

Codex correction to the earlier purple round: overnight is not universally ≈ 0 (purple_pa 15m Asia +0.19R strict).
This does not change the frozen purple_levels_rth spec, which is judged on forward data only.

Untested lead (not a result): strict net R is higher after a large prior-day range in all three purple portfolios
(overlapping trades, no contrast test). Only usable as a new pre-registered hypothesis, never as a filter on the
frozen strategy.
