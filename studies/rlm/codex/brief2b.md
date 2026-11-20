Round 2 (retry): code audit of strategies/rlm.py while the dev grid runs. Repo /home/mrullldhm/personal/tradingview-tester.
MEMORY RULES (your last attempt crashed the machine, 11 GB RAM, ~6 GB used by the running grid):
- Every python run: `bash -c 'ulimit -v 2500000; PYTHONPATH=. .venv/bin/python ...'`, at most ONE year of bars
  (cltester.data.load_bars('2010-06-01','2011-01-01') + add_session), never load_period('dev').
- Never store the full swing stack per candle (that was the crash: quadratic memory); top 4 points only.
- Do not touch studies/rlm/grid_parts/ or kill python processes (the grid is running).
You may write scratch scripts only under studies/rlm/codex/. Do not edit other files.
Already done since your round 2 probe (studies/rlm/codex/audit_round2.py): withdrawals checked against the true
top-4 stack on 2010 5m: 0 missed, 3 spurious of 2,107; withdraw now takes back the touch's CURRENT strength share
(Book.ls log-scale of decays and cross penalties, Book.base per touch; test in tests/test_rlm.py).
Audit strategies/rlm.py against docs/strategies/rlm/README.md and studies/rlm/rlm_logic.pine:
1. Look-ahead (swing_events known = avail[k+1]; candidates loop order; build_orders; manage uses data <= m-1).
2. Bugs: Book touch/withdraw/_merge/_shift/age_cross/nearest/score, cooldown per combo, side-space rounding for
   shorts, kill/expiry, roll guards (c_start, ref_first, ATR reset per contract), RTH filter.
3. Anything that makes the 13,824-version screen misleading.
Reply: numbered findings, severity (bug / look-ahead / minor), file:line, concrete fix. <= 600 words.
