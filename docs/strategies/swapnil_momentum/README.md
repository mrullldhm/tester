# swapnil_momentum

Status: dropped (2026-11-13: loses on every timeframe)
Code: `strategies/swapnil_momentum.py`
Source: github.com/Swapnil227-arch/algo-trading-framework, `strategies/momentum/strategy_1_momentum.py`
(4h OANDA CSVs, XAUUSD settings in the file).

## Hypothesis
Two candles of the same colour in a row mean momentum that continues for at least one more risk unit. The source
claims "consistent monthly returns" and a prop-challenge certificate; its backtest checks exits on the signal candle
itself (look-ahead) and fits the R multipliers in-sample (`maxprofitcalc.py`).

## Rules
- Timeframe: 4h candles (source). Signal when a candle completes.
- Long: the last two completed candles closed green (close > open). Short: two red.
- One position at a time; no reversal while in a trade (engine: one at a time).
- Entry: source buys at the next candle's open; here a limit at the signal candle's close (owner rule: limit
  entries), working for one candle.
- Stop: signal candle low − x (short: high + x). x = 1 gold unit in the source = 0.05% of price here.
- Target by stop size (source: ybuying = [1, 3, 1] with buckets at 40 and 50 of a 100-unit max stop on gold ≈ 2%
  and 2.5% of price): stop < 2% of price → 1R; 2–2.5% → 3R; > 2.5% → 1R.
- 1 contract, flatten 3:10 PM CT (intraday only).

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
| tf | 4h | 4h, 1h, 15m |
Total combinations on dev: 3. Validation only for a combination that passes the dev gates.

## Pass criteria
PROTOCOL.md dev gates (≥ 200 trades, PF ≥ 1.25, ≥ 70% years positive) and beating the ~$5/trade touch-fill bias.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-13 | dev | touch | 6107 | -42,882 | 0.969 | 17.7% | — | 4h (source timeframe) |
| 2026-11-13 | dev | touch | 18805 | -124,472 | 0.954 | 13.7% | — | 1h |
| 2026-11-13 | dev | touch | 51595 | -323,254 | 0.938 | 9.6% | — | 15m |

All in-sample, 3 of 3 tried. Win rate 48% at mostly 1R targets: about a coin flip, so each trade loses the fee
and a bit. Years positive 4, 1, 0 of 12. Spot check: 400 trades against raw bars, 0 problems. Validation not run.

Re-run 2026-11-13 after the Codex review fixed order expiry (orders now expire on clock time, `expire_min`;
before, missing minutes stretched them). These rows replace the ones above; the verdict is unchanged.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 6115 | -41,815 | 0.970 | 4/12 | 17.7% | 4h |
| dev | 18844 | -123,760 | 0.955 | 1/12 | 13.8% | 1h |
| dev | 51621 | -324,819 | 0.937 | 0/12 | 9.5% | 15m |

Re-run 2026-11-13 after Codex review round 5: (a) a timed order now blocks new signals until its deadline even
across a data gap; (b) candles belong to their own trading day, signals from a candle that only completes in the next
session are dropped, and day levels come from raw bars. These rows replace all earlier ones.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 5913 | -50,499 | 0.960 | 3/12 | 19.6% | 4h |
| dev | 18376 | -111,169 | 0.959 | 2/12 | 13.4% | 1h |
| dev | 51612 | -326,022 | 0.937 | 0/12 | 9.5% | 15m |
