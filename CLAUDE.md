# tradingview-tester: rules for Claude

- Goal: an intraday CL strategy that passes the Topstep 50K Trading Combine consistently. Read `README.md` first.
- **CL only. MCL is banned** (non-syariah for the owner). `cltester.update.assert_cl` guards every download.
- Databento downloads cost money: show the quoted cost and get the owner's yes before downloading.
- Fill rules live in `docs/ENGINE.md`, Combine rules in `docs/TOPSTEP.md`; change the doc with the code and add a
  test per rule. Owner fill rules: limit entries, a touch fills, no exit slippage (gaps fill at the open).
- Topstep values marked VERIFY in `cltester/config.py` are unconfirmed; never present them as official.
- Follow `docs/PROTOCOL.md`: hypothesis doc before the first run; dev for tuning; validation once with frozen params;
  holdout once per strategy; every run lands in `results/ledger.csv`; every number says in-sample / best of N.
- **Swing points: owner rule only** (`docs/SWINGS.md`, `cltester/swings.py`). Mandatory for any strategy that uses
  swings; no other pivot method or swing settings. Signals use `swing_state` (point-in-time), never `swing_points`.
- Indicators are computed vectorised over every bar in `signals()`; a signal on bar i may only use data up to bar i.
- Spot-check trades against raw bars before calling any result real.
