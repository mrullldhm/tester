You are a quant co-researcher with Claude on repo /home/mrullldhm/personal/tradingview-tester (read CLAUDE.md, README.md,
docs/PROTOCOL.md, docs/SWINGS.md, docs/ENGINE.md, cltester/swings.py, strategies/juda_swing_point.py). READ ONLY: do not edit files.

Task: the owner gave a PDF strategy "Tomtrades 1hr/1m model (CBR simplified)" written for XAUUSD (gold). Text is in
/tmp/claude-1000/-home-mrullldhm-personal-tradingview-tester/a2d9ae2f-e6a8-4cf4-b90d-3a13a05c85b8/scratchpad/cbr.txt. Diagrams (PNG) in /tmp/claude-1000/-home-mrullldhm-personal-tradingview-tester/a2d9ae2f-e6a8-4cf4-b90d-3a13a05c85b8/scratchpad/cbrimg/*.png (p3_3/p3_4 = the 'type 3 shift' short/long diagram; p5_* = examples;
p1_4 = HTF wick concept; p1_5 = good/bad over-extension). Claude's reading of the diagrams:
 - Type 3 shift long: after a down leg, swing low L1, swing high H1, then a LOWER low L2 (takes local structure), then a 1m
   candle CLOSES above H1 (MSB = close past the wick high of the recent leg). Entry = limit at 50% of the MSB move (L2 to the
   high made by the MSB push), stop at L2, TP = 50% equilibrium of the over-extension leg (leg start to L2), or fixed 1.5R/2R.
 - Over-extension: >=20 minutes of price moving one way without substantial pullback before the reversal.
 - Context: in 2nd hour of Asia (Asia starts 00:00 UTC), sweep of the 1st-hour-of-Asia low (long) / high (short), or a
   'range rebalance' with a 30m candle sweep 30m+ into the 2nd hour. Bias from 1h gold + DXY (we have NO DXY data, CL 1m only).
 - Max 2 attempts per session, done after 1 win. Limit entries only (repo rule). Swing points MUST use cltester.swings owner rule.

Deliver (markdown, <= 900 words):
1. Your own independent CL translation of every rule, flagging where you disagree with Claude's reading above.
2. Which CL sessions/windows make sense as analogs to "2nd hour of Asia" for gold, and why (CL liquidity: 17:00 CT open,
   London, 08:00 CT NY open / 08:30-13:30 CT RTH, 09:30 CT Wed EIA). Give exact CT windows.
3. Bias proxies we can compute from CL 1m only (no DXY).
4. A full list of version dimensions (window x context/sweep x bias x extension filter x target x attempts) with
   concrete values, and a recommendation for how to keep the multiple-testing problem honest (stage design, trial budget).
5. Pitfalls in implementing it point-in-time with the owner swing rule on 1m (look-ahead, rolls, swing_state timing).
