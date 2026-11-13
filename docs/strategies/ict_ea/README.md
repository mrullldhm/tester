# ict_ea

Status: dropped (2026-11-13: loses before fees)
Code: `strategies/ict_ea.py`
Source: github.com/hungpixi/ict-system-ea, `ICT_SystemEA_v2.mq5` (MT5 EA, gold, The5%ers rules). Swing points
replaced by the owner rule (`cltester/swings.py`, docs/SWINGS.md) as instructed by the owner.

## Hypothesis
ICT confluence (structure trend, BOS/CISD, discount/premium, fair value gap, order block, daily OLHC/OHLC bias)
predicts the next 2R move. The source shows only screenshots of its own backtest; no out-of-sample data.

## Rules (source logic, evaluated when each 5m candle completes)
- Structure on 1h with the owner swing rule (`swing_state(df, "1h", prev=True)`): last two swing highs sh1, sh2 and
  lows sl1, sl2. Trend bullish if sh1 > sh2 and sl1 > sl2, bearish if both lower, else unchanged. Last 1h close above
  sh1 in a bull trend = BOS; below sl1 = BOS (bear). Bull trend and close < sl1 = CHOCH, trend turns bearish (mirror);
  CHOCH with body/range > 0.6 = CISD. Trend and last signal persist between updates (as coded, updated every 5m).
- PDA on 5m: equilibrium = (sh1 + sl1)/2 (fallback: 50-candle range); close below = discount, above = premium.
  FVG: newest 3-candle gap in the last 19 candles. Order block: newest opposite candle followed by a big candle
  (body/range > 0.6, larger range) in the last 29 candles (the source's i=1 uses the unfinished bar: skipped).
- Liquidity sweeps: the source's sweep test can never be true (its 50-bar high includes the bar it tests), so 0.
- SMT divergence needs DXY: not available here, skipped (the source also skips when the broker has no DXY).
- Daily bias (+2 points): source `DetermineFirstExtreme` on 5m candles of the CME trading day so far.
- Score: bull = trend↑ + (BOS/CISD in trend↑) + discount + bullish FVG + bullish OB + 2×OLHC; bear mirror. Signal
  when score ≥ 3 and above the other side.
- Entry: source market at the ask; here a limit at the 5m close, working 5 minutes.
- Stop: bullish OB low − 20 pts if a bullish OB exists, else last swing low − 20 pts; capped at 400 pts; skip if the
  stop distance < 30 pts. Target 2R.
- Size: 0.5% of $50K risk ($250) / stop $, floored, 1 to 5 contracts.
- Management (source `ManagePositions`, checked on 1m closes): after 2h in the trade and losing: close. At 1R:
  partial exit down to 1 contract (the source halves on every tick above 1R). At 0.5R: stop to entry + 5 pts.
  At 100 pts profit: stop = price − 30 pts, forward only.
- Daily rules: max 3 trades, stop after 2 losses in a row, stop at −2% ($1,000) or +1.5% ($750) day P&L.
- No session filter: the source defines `IsAllowedSession` but never calls it.
- Points: source is gold (point $0.01 at ~$3,000; gold moves about half as much as CL in %). 1 point is mapped to
  6.7e-6 × CL price (≈ 0.05 tick at $70): 20 pts ≈ 1 tick, 400 pts ≈ 19 ticks, 100 pts ≈ 5 ticks. Assumption.

## Parameters and trial budget
Source defaults, 1 combination on dev, plus 1 owner variant: every score component must agree (`min_conf` 7 =
trend + BOS/CISD + discount/premium + FVG + order block + 2× daily bias; the maximum score, so the other side is 0).
Total 2. Validation only if it passes the dev gates.

## Pass criteria
PROTOCOL.md dev gates and beating the ~$5/trade touch-fill bias.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-13 | dev | touch | 8507 | -115,902 | 0.783 | 0.2% | — | source defaults, pt_frac 6.7e-6 |

All in-sample. Loses even before fees (gross −$3.15 per contract per trade); win rate 57% comes from
tiny trailed wins, the losses are full stops. Years positive 0/12. Spot check: 400 trades vs raw bars,
0 problems. Validation not run.

Re-run 2026-11-13 after the review removed a look-ahead (the daily-bias tolerance used the median price of the
whole period; now the day's open): identical result, 8,507 trades −$115,902 PF 0.783.

Re-run 2026-11-13 after the Codex review fixed order expiry (orders now expire on clock time, `expire_min`;
before, missing minutes stretched them). These rows replace the ones above; the verdict is unchanged.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 8502 | -115,133 | 0.783 | 0/12 | 0.4% | source defaults |

Re-run 2026-11-13 after Codex review round 5: (a) a timed order now blocks new signals until its deadline even
across a data gap; (b) candles belong to their own trading day, signals from a candle that only completes in the next
session are dropped, and day levels come from raw bars. These rows replace all earlier ones.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 8496 | -117,656 | 0.779 | 0/12 | 0.4% | source defaults |

Re-run 2026-11-13 after Codex review round 6: a profitable partial exit now resets the 2-losses-in-a-row count
(as the source counts closing deals). Replaces the rows above.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 8499 | -117,599 | 0.779 | 0/12 | 0.4% | source defaults |

Owner variant 2026-11-13: trade only when every score component agrees (`min_conf` 7, the maximum score). Run after
the rows above, same code. Spot check: 400 trades vs raw bars, 0 problems; all 12,746 signals score 7 against 0.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 3190 | -54,915 | 0.771 | 0/12 | 0.0% | all components (score 7) |

Fewer trades, so it loses less in total, but per trade it is worse (PF 0.771 against 0.779; −$17.21 per trade, gross
−$6.60 per trade before fees). Requiring full confluence does not add edge. Status stays dropped.

