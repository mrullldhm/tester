# purple_pa

Status: dropped (2026-11-13: closest of six ports, still below the PF gate)
Code: `strategies/purple_pa.py`
Source: purple-trading.com "Trading oil intraday: price action strategy" (read 2026-11-13). Its evidence: one
hand-picked 10-day WTI example, 6 trades (5 wins), no costs, no backtest.

## Hypothesis
Previous-day highs and lows are levels other traders watch. The first test of such a level, confirmed by a
3-candle gap away from it, bounces at least 1R.

## Rules
- Levels: the previous CME trading day's high and low (article: previous days' highs/lows; "use fewer levels").
- A level is armed while candles stay fully on one side of it. A test = an armed level touched (high ≥ level from
  below, low ≤ level from above). Only the first test trades. If price later re-arms on the other side (the level
  broke), one retest is allowed with the role flipped. At most 2 tests per level per day.
- Test from above = support: long. Test from below = resistance: short.
- Confirmation: a bullish gap (high of candle q−2 < low of candle q) for a long, bearish gap (low of q−2 > high of
  q) for a short, completed 1–4 candles after the test candle, with q−2 no earlier than the candle before the test.
- Entry: limit at the gap's upper edge for a long (low of q) / lower edge for a short (high of q), the article's
  entry price; works 4 candles.
- Stop: 1 tick beyond the lowest low (long) / highest high (short) from the test candle to q.
- Target: 1R (the article's stated 1:1 for intraday trades). 1 contract, flatten 3:10 PM CT.
- Not ported: trend preference and news avoidance (no rule given), H1 levels other than the previous day.

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
| tf | 15m | 15m, 5m (article: 15m, possibly 5m) |
Total combinations on dev: 2. Validation only for a combination that passes the dev gates.

## Pass criteria
PROTOCOL.md dev gates and beating the ~$5/trade touch-fill bias.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-13 | dev | touch | 545 | +14,938 | 1.202 | 35.1% | — | 15m: +$27/trade, 9/12 years |
| 2026-11-13 | dev | touch | 593 | +12,714 | 1.238 | 55.0% | — | 5m: +$21/trade, 7/12 years |

All in-sample, 2 of 2 tried. Both fail PF ≥ 1.25; 5m also fails years positive (lost 2018–2021 in a row). Touch-only
fills: 36% (15m) and 43% (5m) of trades. Trades whose fill bar traded through the limit: 15m +$15.9/trade
(PF 1.10), 5m +$20.8 (PF 1.20), so the edge is not only the fill model, but it is thin and 15m leans on 2011
(+$6,606 of +$14,938). Spot check: 400 trades vs raw bars, 0 problems. Validation not run.
A follow-up (e.g. the article's trend preference) would be a new hypothesis with its own trial budget.

Re-run 2026-11-13 after the Codex review fixed order expiry (orders now expire on clock time, `expire_min`;
before, missing minutes stretched them). These rows replace the ones above; the verdict is unchanged.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 542 | +14,430 | 1.196 | 9/12 | 34.9% | 15m |
| dev | 592 | +12,858 | 1.241 | 7/12 | 55.0% | 5m |

Re-run 2026-11-13 after Codex review round 5: (a) a timed order now blocks new signals until its deadline even
across a data gap; (b) candles belong to their own trading day, signals from a candle that only completes in the next
session are dropped, and day levels come from raw bars. These rows replace all earlier ones.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 545 | +14,508 | 1.196 | 10/12 | 38.6% | 15m |
| dev | 591 | +12,732 | 1.239 | 7/12 | 55.0% | 5m |
