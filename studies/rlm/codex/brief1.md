You are a quant co-researcher with Claude on repo /home/mrullldhm/personal/tradingview-tester. Read CLAUDE.md, README.md,
docs/PROTOCOL.md, docs/SWINGS.md, docs/ENGINE.md, cltester/swings.py (swing_state), cltester/engine.py header, and memory
of past studies in docs/strategies/*/README.md (esp. cbr, purple_levels, juda_swing_point: edges lived in RTH and died
under strict fills / validation). READ ONLY: do not edit any file. Write nothing.

Task: owner wants the TradingView indicator "Reaction Level Matrix [WillyAlgoTrader]" tested on CL 1m data (2010-2021 dev).
Its trading logic is in studies/rlm/rlm_logic.pine. Owner constraint: swing points MUST be the owner rule
(cltester/swings.py). Owner quote: "Industry swing point uses Swing Length to define strength. My swing point strength
is defined by TF. The bigger the TF, the stronger the swing point. It doesn't use swing length." Limit entries only,
touch fills, no exit slippage, flat 15:10 CT, Topstep 50K Combine target.

Claude's draft mapping (critique it, propose your own where you disagree):
- Signal TF S in {5m,15m,1h}: level engine and rejection candle run on completed S candles (ATR34 of S for tolerance/band,
  ATR14 of S for stop). Half-life 500 S-bars, cross penalty, 60-level cap, merge, 3 nearest per side, cooldown 10 S-bars.
- Touches come from owner swing points on several TFs: sources = S..1d ("all") or >S..1d ("htf"). A point is registered
  when it is LOCKED: the opposite swing after it is confirmed (newest flips), so rule-5 replacement cannot fake a touch.
  Weight = TF weight (owner): 5m 1, 15m 1.5, 30m 2, 1h 2.5, 4h 3, 1d 3.5 (same 1..3.5 range as the original reaction
  weight), control "flat" = 1. One turning point counted once: when a higher TF locks the same extreme (same kind, same
  price, lower-TF candle inside the higher-TF candle) the touch is upgraded to the higher weight, touches not incremented.
- Rolls: levels reset at each raw_symbol change (prices not back-adjusted); only extremes printed in the current contract.
- Rejection rule as original (approached / touched / held / CLV / score / cooldown).
- Entry (limit only): `close` = limit at signal close; `band` = limit at the level band edge (retest). Expiry ~ a few S bars.
- Stop: `wick` = original wick-anchored (low - 0.25 ATR14, min 0.5 ATR14 from entry); `band` = level lo - 0.25 ATR14 (min 0.5).
- Exit: fixed 1R / 2R / 3R, or 3R with BE after 1R (original-like 1 contract), opposite signal closes? (engine: manage()).
- Session: all (17:00-15:10) vs rth (08:30-13:30 CT entries).
- Grid of every dimension, dev screen with gates like studies/cbr (PF>=1.25, >=200 trades, 70% years, pass>=50%,
  cost/pass<=$500, halves, neighbours), then strict fills --through 1, spot checks, trade-feature correlation study, one
  validation run only for survivors.

Deliver (markdown <= 900 words):
1. Flaws/optimism in the ORIGINAL indicator's own stats (what its displayed win rate really measures).
2. Your independent CL translation of each rule; flag disagreements with the draft (esp. how TF strength should enter
   the score, locking vs registering at confirmation, multi-TF double counting, ATR choice for tolerance, rolls).
3. Version dimensions you would add or drop, and a trial budget + multiple-testing guard you consider honest.
4. Point-in-time pitfalls (swing_state timing, candle avail, rolls, session breaks) specific to this design.
5. What trade features to log for the win/loss correlation study, and how to keep that study from becoming curve-fitting.
