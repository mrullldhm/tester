# Claude findings (dev 2010-06..2021, in-sample). Plan: `claude/PLAN.md` (incl. amendment); code `claude/rth_cross.py`.

Corrected 2026-11-18 after the Codex adversarial review: the first version pooled runs and de-duplicated entries in
arbitrary set order, so conflicting outcomes were picked at random (superseded numbers kept in
`claude/rth_cross_pooled_superseded.csv`). Now every dev touch-fill run is analysed separately, in sorted order;
output is identical across Python hash seeds. Per-run rows: `claude/rth_cross_runs.csv`.
Second correction (same day, second Codex review): undefined session contrasts no longer cast a vote, and the
binomial sign test is replaced by a joint day-block bootstrap (PLAN.md amendment 2).

Gross = before fees, ticks per contract (fee ≈ 0.40 tick). SE = daily-cluster. purple_* excluded (source of the RTH
hypothesis); pd_swing excluded (every run < 100 trades).

| Strategy | Runs (defined contrast) | Gross ticks/trade: median run (min..max) | Every run's 95% CI below 0? | RTH − other ticks: median of defined runs (min..max) | Defined runs with RTH better |
|---|---|---|---|---|---|
| ict_ea | 6 (1) | −0.32 (−0.39..−0.31) | **yes** | undefined (5 of 6 runs have < 30 RTH trades) | — |
| scribd_supertrend | 8 (8) | −0.46 (−0.84..−0.09) | no | +1.20 (+0.93..+1.48) | 100% |
| swapnil_hm | 8 (8) | −2.29 (−8.42..+3.12) | no | +11.24 (+5.92..+19.12) | 100% |
| swapnil_momentum | 9 (9) | −0.25 (−0.45..−0.20) | no | +0.72 (−0.22..+1.24) | 78% |
| swing_point_failure | 27 (27) | −0.59 (−1.01..−0.20) | no | +0.24 (−0.44..+0.95) | 85% |
| swing_point_failure_reversal | 17 (17) | −0.27 (−0.46..+0.14) | no | −0.23 (−0.44..+0.66) | 41% |
| swing_point_manipulation | 42 (42) | +0.03 (−0.27..+0.78) | no | +1.30 (−0.06..+3.30) | 98% |
| xtley_gap | 18 (18) | +0.14 (−1.65..+0.44) | no | +0.21 (−1.03..+11.79) | 50% |

1. **No strategy has a gross edge.** No strategy has every run's interval above zero; the median run is within about
   ±0.6 tick of zero everywhere except swapnil_hm (−2.3, very noisy). Only **ict_ea** is reliably negative (all 6
   runs), by 0.3 tick: smaller than a fee, so not invertible. scribd_supertrend and swing_point_failure are negative
   in every run too, but whether that is significant depends on the configuration: the earlier "reliably negative"
   claim for them is **withdrawn**.
2. **Out-of-family RTH test (pre-declared, amended twice):** 7 strategies eligible (ict_ea undefined). RTH better
   in 6 of 7 votes (descriptive; strategies share CL history and swing_point_failure_reversal is built on
   swing_point_failure, so no binomial test). Joint 20-day block bootstrap, dependence kept: mean of median-run
   RTH − other = **+2.10 ticks, 95% [+0.12, +4.18]**, bootstrap share ≤ 0 = 1.5%.
   Caveats: the mean is dominated by swapnil_hm (+11.2 ticks); without it the other six average +0.57 ticks
   (descriptive, not declared, no interval). Differences are in ticks and RTH moves are larger, so part is scale
   (Codex's R-unit test: +0.065R gross, BH 0.13 / BY 0.87). Read as a consistent direction, small in size apart
   from one noisy strategy.
3. RTH filtering does not lift any strategy's median run clear of fees with an edge behind it; optimising
   strategies with zero gross edge would be fitting noise. No production change.
