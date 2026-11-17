# Codex brief: can purple_levels be improved on a genuine edge, without overfitting?

You are an independent researcher. Claude is analysing the same question in parallel; do not look for or read
Claude's notes in this folder (anything except this brief). Write your own answer.

## Read first
CLAUDE.md, docs/PROTOCOL.md, docs/ENGINE.md, docs/SWINGS.md, docs/strategies/purple_pa/README.md,
docs/strategies/purple_levels/README.md, studies/level_regime/findings.md, strategies/purple_levels.py,
strategies/purple_pa.py, cltester/engine.py.

## State of play
- purple_levels: dev 2010-06..2021 looked good (all 5m PF 1.39, best of 12+), validation 2022-2024 failed / was
  carried by touch-only fills and 10 days. Validation has now been looked at for `all` and `nopd` (touch + strict).
- Holdout 2025..2026-11-12 is unused for this family. Forward (after 2026-11-12) is the only truly clean data.
- Level regime study: bare first touch of a fixed level = coin flip vs random-walk fair; edge appears only in the
  fast departure (gap), which is partly circular.

## Rules for you (hard)
- READ-ONLY on everything except `studies/purple_levels_improve/codex/` (create it) and
  `studies/purple_levels_improve/codex_report.md`.
- Use only dev data: `cltester.data.load_period("dev")`. Do NOT load validation, holdout or "all".
  Do NOT run `python -m cltester.cli test` (it writes the ledger). No git, no downloads.
- Python: `.venv/bin/python`. Dev trade lists already exist: `results/purple_levels/dev_018fdfd1eb22.csv`
  (all 5m, touch fills), `dev_e0799b1e4110.csv` (all 5m strict through-1), `dev_b777ef9ec188.csv` (nopd 5m),
  `dev_17242b70a399.csv` (nopd strict). The `levels` family per trade is not in the CSV; recompute if needed by
  calling the strategy's `signals()` on dev bars yourself (do not write the ledger).
- Count every cell / variant you evaluate. Report multiplicity honestly (BH or similar), and label all numbers
  dev, in-sample.

## Questions
1. Mechanism: what is the most plausible *economic* reason this setup ever made money (who is on the other side,
   why would it repeat)? Which parts of the rule set carry the edge and which are decoration? Decompose dev P&L by
   component (level family, time of day, gap size vs stop, touch-only vs traded-through fill, first test vs retest,
   long/short, distance of entry from level, stop size in ticks vs fees).
2. Fill realism: touch fills vs traded-through fills. Is the dev edge concentrated in the fills a live limit order
   would most likely miss (adverse selection)? Quantify on dev. Propose an entry that does not depend on touch
   fills (e.g. stop/market entry on gap confirmation, entry inside the gap, etc.) and say what it costs.
3. Propose at most 3 changes, each with an a-priori reason that does NOT come from looking at 2022-2024 results.
   For each: the exact rule, why it should be robust, how many parameter values (keep it to 1-2), and a dev
   check (descriptive; you may simulate it yourself in your folder with the engine, without the ledger).
   Prefer changes that remove degrees of freedom over ones that add filters.
4. Test plan: given validation is spent for `all`/`nopd`, what data can still honestly judge a revised version
   (holdout once? forward/paper only?), what sample size is needed to detect the dev edge vs zero at reasonable
   power, and how long forward would take at the trade rate.
5. Straight verdict: is there a credible path, or should the owner stop optimising this family and only
   forward-test the frozen version?

Keep the report concise (tables > prose), plain English, every number labelled dev / in-sample.
