Round 2: code audit BEFORE the 13,824-version dev grid runs. Repo /home/mrullldhm/personal/tradingview-tester.
READ ONLY for repo files; you may write scratch scripts only under studies/rlm/codex/. Python: .venv/bin/python
(PYTHONPATH=.). Your round-1 reply: studies/rlm/codex/reply1.md (adopted: confirm mode with withdrawal, roll guard on
the left reference candle, ATR reset per contract, expiry 1 S interval, BE ignores fill-bar high; NOT adopted: the
48-config budget -- owner asked for every version, so full grid + your bootstrap family check, see the README).
Read docs/strategies/rlm/README.md (spec, frozen) and audit strategies/rlm.py and studies/rlm/grid.py for:
1. Look-ahead: swing_events known times (detect state[k] known at avail[k+1]), lock/confirm/withdraw logic, candle
   avail vs signal bar, ATR, levels, manage() (data up to m-1 only), anything using future bars.
2. Bugs vs the Pine logic (studies/rlm/rlm_logic.pine) and the README: aging/cross order, merge, eviction, nearest
   selection, rejection tests, cooldown per combo, score, band refit, TF dedupe/upgrade/withdraw accounting
   (Book.touch / withdraw / _shift / _merge), side-space mirroring in build_orders (entry/stop/target rounding for
   shorts), kill/expiry, risk floor.
3. Roll/session guards; anything that makes the screen misleading.
Small read-only checks are fine (load_period('dev') ~1 s; trim to one year for speed; candidates() 5m on dev ~60 s).
Reply: numbered findings, severity (bug / look-ahead / minor), file:line, concrete fix. <= 700 words.
