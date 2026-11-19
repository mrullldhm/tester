Round 3: independent read of the dev screen. Repo /home/mrullldhm/personal/tradingview-tester. You may WRITE only
inside studies/cbr/codex/ (scripts + outputs); do not edit anything else. Run python with .venv/bin/python.
Context: docs/strategies/cbr/README.md (spec + declared screen), strategies/cbr.py (your round-2 fixes applied),
studies/cbr/grid_dev_screened.csv (all 1,728 dev versions, touch fills), studies/cbr/screen_dev.txt (summary).
Result: 0 versions pass all gates; cost/pass <= $500 kills all (~20-45 trades/yr at 1 contract). 24 pass every other
gate, all window rth/ny, context reb. rth: 78.5% of 288 versions net > 0, median PF 1.25; other windows ~35-46%.
Claude is running now (do NOT duplicate): strict-fill (--through 1) grid for rth+ny, and a "type-3 vs any MSB" control.
Your tasks (Codex-only, independent):
1. Is the RTH effect real or a multiple-testing / dependence artefact? The 288 rth versions share trades, so 78.5%
   is not 288 independent votes. Quantify: e.g. day-block bootstrap of the simplest version (rth, reb, none, e20, r2,
   attempts 1: rebuild its trades with strategies.cbr + cltester.engine as in studies/cbr/grid.py), per-year table,
   concentration (top 10 days share of net), long vs short, and a random-entry RTH null matched on time-of-day,
   side and bracket (R distribution) to see whether CL RTH 1m limit brackets are profitable without the pattern.
2. Spot-check 5 trades of that version against raw bars (entry fill, stop/target exit) and report.
3. Verdict: which (if any) version deserves a single frozen validation run, and with what sizing for the Combine
   (max 5 contracts, $2,000 trailing MLL)? Be explicit about best-of-1,728.
Reply <= 800 words, numbers with in-sample labels. Save scripts/outputs under studies/cbr/codex/.
