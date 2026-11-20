Round 3: independent read of the RLM dev result. Repo /home/mrullldhm/personal/tradingview-tester.
MEMORY RULES (machine has 11 GB; it crashed twice): wrap every python run as
`bash -c 'ulimit -v 3000000; PYTHONPATH=. .venv/bin/python ...'`; ONE python process at a time; load_period('dev')
is allowed (~1.1 GB) but nothing else heavy beside it; never store full swing stacks. Write only under
studies/rlm/codex/. Do not edit other files.
Context: docs/strategies/rlm/README.md (spec + declared screen), your audit fixes applied (reply2.md),
studies/rlm/screen_dev.txt (13,824-version dev screen), studies/rlm/grid_dev_9a2fa27f50_screened.csv.
Result: exactly 1 version passes all gates: sig_tf=1h reg=confirm sources=all weight=flat tol=0.4 score=50 clv=0.6
entry=close stop=band exit=r1 session=all. Dev (in-sample, best of 13,824): 1,281 trades, PF 1.309, 11/12 years,
pass 52%, $332/pass (ledger 0c7941f8774a); --through 1: PF 1.267, pass 50%. Random-date null
(studies/rlm/null.py, 300 runs, same CT minute/side/offset/risk/target): median PF 0.974, max 1.17, z = 5.2.
Trade features: studies/rlm/trades/lead_dev_features.csv (no strong monotone filter). Grid medians: PF 0.98, 39% net>0.
Observation: weight=tf sibling (same params) gives 5,190 trades and PF 1.07: with flat weights, score>=50 needs ~5
touches, so the score threshold is a different filter per weight scheme.
Tasks:
1. Try to break it: look-ahead or engine artefacts specific to entry=close (limit at the 1h close, next 1m bar),
   e.g. fills where the next bar opens through the limit, trades after 14:00 CT that only flatten, 1h candle
   completion vs signal bar, session/holiday candles, roll weeks. Quantify each.
2. Is the null fair? Does a random-date null miss structure (e.g. 1h-close momentum/reversal at the same minute
   on the same day, volatility regime)? Build one stronger null you think is fairer (e.g. same day, random other
   1h close in the session; or the version's signals with the level test removed: every 1h candle with clv>=0.6
   rejection shape) and report PF distribution vs 1.309.
3. Verdict: does this version deserve ONE frozen validation run (2022-2024)? Any pre-registered change you
   would make BEFORE validation (none is fine)? Sizing for the Combine (max 5 CL, $2,000 trailing MLL)?
Reply <= 800 words, numbers labelled in-sample. Save scripts/outputs under studies/rlm/codex/.
