# Claude plan (declared 2026-11-18 before computing anything below)

Dev only, existing trade lists (no new strategy runs, no ledger writes).

Run selection per strategy (fixed rule, no picking): the dev run with the most trades among runs with the highest
profit factor is NOT used (selection bias); instead use **every** dev touch-fill run of the strategy and pool
trades per strategy de-duplicated by (entry_ts, side, entry) so overlapping variants count once. Excluded:
purple_levels and purple_levels_rth (the source of the hypothesis) and purple_pa (its trades are the `pd` family
of purple_levels). pd_swing excluded if fewer than 100 pooled trades.

1. Gross edge: per strategy, gross $/trade and gross ticks/trade, daily-cluster SE.
2. Out-of-family RTH test. H1: gross ticks/trade for entries 08:30-13:30 CT > entries outside it. Per strategy:
   difference and daily-cluster SE. Primary statistic: number of strategies with a positive difference
   (one-sided sign test across k strategies). Secondary: pooled difference with strategy fixed effects.
   Entry time = entry_ts in CT.
3. Only if H1 is supported: describe which strategies have RTH-only gross > fees.

## Amendment (2026-11-18, after Codex adversarial review; declared before re-running)
Bug: pooling runs and dropping duplicate (entry_ts, side, entry) kept the first run's outcome in set order, so
conflicting exits/P&L were picked arbitrarily (scribd_supertrend: 7,527 conflicting keys; result order-dependent).
Fix: no pooling. Every dev touch-fill run is analysed separately (runs sorted by hash, deterministic). Per strategy
report: number of runs, the **median run** of gross ticks/trade and of RTH − other, the min..max across runs, and the
share of runs with RTH > other. A strategy is "reliably negative/positive" only if every run's 95% interval excludes
zero on that side. Cross-strategy sign test uses each strategy's median-run RTH − other. pd_swing runs with < 100
trades are skipped. The first (pooled) results are kept in `rth_cross_pooled_superseded.csv`, not used.

## Amendment 2 (2026-11-18, after the second Codex adversarial review; declared before re-running)
1. Missing comparisons: a run's RTH − other contrast is **defined** only if it has ≥ 30 RTH and ≥ 30 other trades.
   A strategy gets a vote only if ≥ 50% of its runs are defined; its vote is the median over defined runs only.
   Report defined/total runs; the share of runs with RTH better is over defined runs. Ineligible strategies are
   reported as "undefined", never as a vote.
2. Inference: the binomial sign test is dropped (strategies share CL history; swing_point_failure_reversal is built
   on swing_point_failure). The count of positive votes is descriptive only. Inference uses a joint circular block
   bootstrap over trading days (block 20 days, 2,000 resamples, seed 20261118): every run is resampled with the
   same days, so cross-strategy dependence is kept. Statistic: the mean over eligible strategies of their
   median-run RTH − other (ticks). Report its 95% percentile interval and the bootstrap share ≤ 0 (one-sided).
   Day calendar = union of trading days with any trade in any analysed run.
