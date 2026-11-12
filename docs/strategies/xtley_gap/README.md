# xtley_gap

Status: dropped (2026-11-13: no dev combination near the gates)
Code: `strategies/xtley_gap.py`
Source: github.com/Xtley001/Mean-Reversion-Gap-Strategy-Trading-Bot (`engine.py`, `config.py`, `indicators.py`), MT5
EA for forex/CFDs. Ported with the USOIL settings from its `SYMBOL_SETTINGS`.

## Hypothesis
In a quiet market (short ATR below long ATR), price stretched more than 0.6% from the EMA 360 but already back
above (below) the EMA 20 with RSI turning, reverts toward the EMA 360. Who pays: late trend followers. The source
gives no evidence; it claims prop-firm suitability only.

## Rules (source logic, completed candles only)
- Timeframe: 5m, 15m or 30m candles (source runs all three). Signal when a candle completes. All session hours.
- Long: ATR10 < ATR20 (SMA of true range), close < EMA360 − 0.6%·EMA360, close > EMA20, RSI20 (SMA) falling
  (previous > current) and RSI < 70. Short: mirror (close > EMA360 + gap, close < EMA20, RSI rising, RSI > 30).
  The RSI condition is as coded in the source (falling RSI for a long).
- Entry: limit 2 ticks better than the close (source: 2 pips from ask/bid), works 5 candles.
- At least 5 candles between signals (source MIN_BARS_BETWEEN_TRADES).
- Stop 1.5 × ATR10; target 5R.
- Trailing (source `manage_existing_positions`): once open profit ≥ 1R, stop = entry + whole R units of profit,
  or close − 2.0 × ATR10 if higher (USOIL trailingFactor 2.0); only moves forward. Checked on 1m closes.
  Source bug: its modify call also sets TP = entry − |SL distance| × 5, below price for a long, which MT5 rejects,
  so live the trailing likely never applied. Hence variant `trail=False`.
- 1 contract. Topstep flatten 3:10 PM CT.

## Port differences
- Source uses the live, unfinished candle; here only completed candles (no look-ahead).
- Prop-firm % limits, spread filter, and $50 fixed risk sizing dropped (1 CL contract).
- Continuous CL1! is not back-adjusted: EMA 360 crosses roll jumps.

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
| tf | 15m | 5m, 15m, 30m |
| trail | True | True, False |
Total combinations on dev: 6. Validation: only if a combination passes the dev gates; one run, frozen.

## Pass criteria
PROTOCOL.md dev gates: ≥ 200 trades, PF ≥ 1.25, ≥ 70% years positive. Also must beat the random-entry baseline
(touch fills inflate limit-entry results by ~$5/trade, see 2026-11-12 article test).

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-13 | dev | touch | 8063 | -27,965 | 0.956 | 10.8% | — | 5m trail, best of 6 = none |
| 2026-11-13 | dev | touch | 6331 | +2,003 | 1.003 | 20.0% | — | 5m no trail |
| 2026-11-13 | dev | touch | 4179 | +1,537 | 1.003 | 28.8% | — | 15m trail (best PF, tie) |
| 2026-11-13 | dev | touch | 3451 | -3,292 | 0.994 | 20.4% | — | 15m no trail |
| 2026-11-13 | dev | touch | 1930 | -15,247 | 0.943 | 24.0% | — | 30m trail |
| 2026-11-13 | dev | touch | 1731 | -33,213 | 0.906 | 16.5% | — | 30m no trail |

All in-sample, best of 6. Every combination is around breakeven or worse before the ~$5/trade touch-fill bias is
removed, so after it all lose. Years positive 2–7 of 12. Spot check: 400 trades against raw bars, 0 problems.
Validation not run (no candidate). Holdout untouched.

Re-run 2026-11-13 after the Codex review fixed order expiry (orders now expire on clock time, `expire_min`;
before, missing minutes stretched them). These rows replace the ones above; the verdict is unchanged.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 8088 | -28,046 | 0.956 | 2/12 | 11.6% | 5m trail |
| dev | 6342 | +928 | 1.001 | 5/12 | 20.3% | 5m no trail |
| dev | 4191 | +288 | 1.001 | 5/12 | 27.2% | 15m trail |
| dev | 3466 | -6,053 | 0.988 | 5/12 | 19.7% | 15m no trail |
| dev | 1935 | -15,797 | 0.941 | 7/12 | 24.9% | 30m trail |
| dev | 1737 | -33,667 | 0.905 | 5/12 | 16.6% | 30m no trail |

Re-run 2026-11-13 after Codex review round 5: (a) a timed order now blocks new signals until its deadline even
across a data gap; (b) candles belong to their own trading day, signals from a candle that only completes in the next
session are dropped, and day levels come from raw bars. These rows replace all earlier ones.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 8086 | -28,017 | 0.956 | 2/12 | 11.5% | 5m trail |
| dev | 6341 | +1,082 | 1.002 | 5/12 | 20.3% | 5m no trail |
| dev | 4191 | +288 | 1.001 | 5/12 | 27.2% | 15m trail |
| dev | 3466 | -6,053 | 0.988 | 5/12 | 19.7% | 15m no trail |
| dev | 1931 | -12,801 | 0.951 | 7/12 | 25.1% | 30m trail |
| dev | 1729 | -35,535 | 0.898 | 4/12 | 14.7% | 30m no trail |
