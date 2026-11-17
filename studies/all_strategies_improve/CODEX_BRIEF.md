# Codex brief: can any strategy in this repo be improved on a genuine, repeatable edge without overfitting?

Independent researcher. Claude works on the same question in parallel; do not read Claude's files in this folder
(anything other than this brief) until told to in a later round.

## Read first
CLAUDE.md, docs/PROTOCOL.md, docs/ENGINE.md, docs/SWINGS.md, every `docs/strategies/*/README.md`,
`studies/purple_levels_improve/` (the previous round: Claude + you; result = `purple_levels_rth`, frozen for forward
paper), `studies/level_regime/findings.md`, the swing confluence study summary in
`docs/studies/swing_confluence/README.md`, `results/ledger.csv`.

## Strategies
ict_ea, pd_swing, purple_pa, purple_levels (-> purple_levels_rth, frozen: do NOT retune), scribd_supertrend,
swapnil_hm, swapnil_momentum, swing_point_failure, swing_point_failure_reversal, swing_point_manipulation,
xtley_gap. Dev trade lists for every ledger run: `results/<strategy>/dev_<hash>.csv` (hash from the ledger).

## Hard rules
- Write only under `studies/all_strategies_improve/codex/` and `studies/all_strategies_improve/codex_report.md`.
- Dev data only: `cltester.data.load_period("dev")`. Never load validation, holdout or all. No
  `python -m cltester.cli test` (writes the ledger), no git, no downloads. Python: `.venv/bin/python`, `PYTHONPATH=.`.
- Swing points only via the owner rule (`cltester.swings.swing_state`), point-in-time.
- CL only. Count every cell you evaluate; BH/BY across them; label every number dev / in-sample, best of N where
  the run was selected.

## Questions
1. Triage: for each strategy's best and median dev run, gross expectancy per trade in ticks and in R (before fees),
   with daily-cluster SE. Which strategies have a gross edge distinguishable from zero at all? A strategy with no
   gross edge cannot be "optimised" without overfitting: say so and stop on it.
2. For the survivors: decompose dev P&L (session/time of day, side, stop size, fill type touch-only vs traded
   through, trend/volatility regime if cheap). Look for effects that are (a) present across several strategies, not
   one, and (b) have an a-priori market reason. A cross-strategy effect is much stronger evidence than a
   within-strategy one.
3. Specifically test, as an out-of-family check: does the session effect found in purple_levels (08:30-13:30 CT
   good, overnight ≈ 0 under strict fills) also appear in the OTHER strategies' dev trades? Pre-declare the exact
   test before running it.
4. Propose at most 3 changes in total across the repo, each with an a-priori reason, 1-2 parameter values, a dev
   check you run yourself (engine in memory, no ledger), and paired daily-P&L inference vs the unchanged strategy.
5. Data: what can honestly judge a change (validation used? holdout used? per strategy: check the ledger),
   power, and a straight verdict per strategy: drop / freeze for forward / one more pre-registered test.

Concise, tables over prose, plain English.
