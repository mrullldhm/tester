# swapnil_hm

Status: dropped (2026-11-13: fails dev gates)
Code: `strategies/swapnil_hm.py`
Source: github.com/Swapnil227-arch/algo-trading-framework, `strategies/HM/buying.py` and `selling.py` (4h OANDA
USDJPY CSV exported from TradingView; settings in the files).

## Hypothesis
Hilega Milega (RSI-based "price strength" above "volume strength") plus price above the Bollinger basis and VWAP
with an extreme RSI marks a strong push that runs a fixed distance further. No evidence in the source beyond a
certificate and in-sample tuned values.

## Rules
- Timeframe: 4h candles (source). Signal when a candle completes.
- Indicators (TradingView standard, the CSV columns): RSI 14; HM on RSI 9: price strength = EMA 3 of RSI 9,
  volume strength = WMA 21 of RSI 9; Bollinger basis = SMA 20 of close; VWAP of the CME trading day.
- Long: volume strength < price strength, close > basis, close > VWAP, RSI 14 > 75.
  Short: volume strength > price strength, close < basis, close < VWAP, RSI 14 < 20.
- Entry: source at the next candle's open; here a limit at the signal close for one candle (owner rule).
- Stop (long): newest candle at or before the signal with close − open ≥ `five` and entry − its open > `five`:
  its open − `trail`; none found: entry − `start`. Short: mirror with the sell values.
- Target: entry + `tgt` (long) / entry − `tgt_s` (short). Fixed.
- Candle stop update after each completed candle in the trade (source `trade()`): long: green candle ≥ `five` →
  stop = its open − `trail`; red candle ≥ `five` → stop = its close − `trail`. Short mirror with `trail_s`.
  The stop can move both ways (as coded).
- Source units are USDJPY price units (~145). Scaled to CL by percent of price: five 0.1 → 0.069%, trail 4.5 →
  3.10%, start 0.5 → 0.345%, tgt 3 → 2.07%; short: tgt 2.8 → 1.93%, trail 2.1 → 1.45%.
- 1 contract, flatten 3:10 PM CT. With 2–3% stops and targets, most trades end at the flatten.

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
| tf | 4h | 4h, 1h |
Total combinations on dev: 2. Validation only for a combination that passes the dev gates.

## Pass criteria
PROTOCOL.md dev gates and beating the ~$5/trade touch-fill bias.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-13 | dev | touch | 220 | -12,569 | 0.860 | 16.9% | — | 4h (source timeframe) |
| 2026-11-13 | dev | touch | 791 | +21,464 | 1.087 | 34.1% | — | 1h: +$27/trade, 7/12 years |

All in-sample, 2 of 2 tried. 1h is the best: +$27/trade is above the touch-fill bias, but PF 1.09 < 1.25 and 7/12
years positive < 70%. 74% of its trades exit at the 3:10 PM flatten (targets/stops of 2–3% rarely hit intraday),
so it acts as "enter an extreme-RSI push, hold to the close". Spot check: 400 trades vs raw bars, 0 problems.
Validation not run.

Re-run 2026-11-13 after indicator fixes (WMA rewrite, index handling): identical results.

Re-run 2026-11-13 after the Codex review fixed order expiry (orders now expire on clock time, `expire_min`;
before, missing minutes stretched them). These rows replace the ones above; the verdict is unchanged.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 220 | -12,569 | 0.860 | 5/12 | 16.9% | 4h |
| dev | 791 | +21,514 | 1.087 | 7/12 | 34.1% | 1h |

Re-run 2026-11-13 after Codex review round 5: (a) a timed order now blocks new signals until its deadline even
across a data gap; (b) candles belong to their own trading day, signals from a candle that only completes in the next
session are dropped, and day levels come from raw bars. These rows replace all earlier ones.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 206 | -18,172 | 0.786 | 4/12 | 15.8% | 4h |
| dev | 762 | +2,422 | 1.010 | 5/12 | 32.6% | 1h: the earlier +$21.5K was mostly stale previous-session candles / wrong-session VWAP |
