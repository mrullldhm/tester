Round 2: code audit (READ ONLY, do not edit). Repo /home/mrullldhm/personal/tradingview-tester.
Read docs/strategies/cbr/README.md (the merged spec; your round-1 reply is studies/cbr/codex/reply1.md; note the
extension thresholds were recalibrated by setup frequency because 25%/0.65 kept 0.5% of setups) and strategies/cbr.py.
No P&L has been run yet. Audit strategies/cbr.py for:
1. Look-ahead: every feature used at signal bar i must be known at bar i's close (swing state offset st[i-1],
   ref-hour stats, 30m candle choice via avail, 1h swing_state at ws-1, extension origin, U).
2. Bugs vs the README spec (MSB = first close above each swing high; structure check; windows/DST via clocks;
   reb30 / fh sweep definitions; engulf; target rounding; side-space mirroring; day_rules semantics; expiry/kill).
3. Roll/session guards (unadjusted prices) — anything missing.
4. Anything that would make the 1,728-version screen misleading.
You may run small read-only python checks with .venv/bin/python (load_period('dev') is ~2s; candidates() ~60s).
Reply: numbered findings, each with severity (bug/look-ahead/minor), file:line, and a concrete fix. <= 700 words.
