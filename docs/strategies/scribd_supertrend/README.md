# scribd_supertrend

Status: dropped (2026-11-13: loses in 11 of 12 years)
Code: `strategies/scribd_supertrend.py`
Source: Scribd document 376948099 "Setup for 10-15 Points Intraday Setup for Crude Oil" (2 pages, owner screenshot,
2026-11-12). Written for MCX crude (INR); no results given.

## Hypothesis
When Supertrend, the EMA 8/21 order and a strong Vortex reading all agree, the move continues 10–15 points.

## Rules
- 15m candles. Signal on the candle where all three conditions first agree within the trading day (the document:
  new opportunity every day, ignore previous day signals; entry at the next candle).
- Long: Supertrend(10, 1.8) up, EMA 8 > EMA 21, VI+ > 1.1 and VI− < 0.9 (Vortex 14, TradingView default).
  Short: Supertrend down, EMA 8 < EMA 21, VI− > 1.1 and VI+ < 0.9.
- Entry: limit at the signal close (document: market at the next open), working one candle.
- Stop: "Stop Loss ATR (Red Dots) – 4 points": entry ∓ (ATR 14 + 4 points). The document does not define the
  ATR stop further; this reading is mine.
- Exit, variant `trail`: once +10 points, the ATR stop is replaced by a trailing stop at the last 1m close ∓ ATR 14,
  forward only; no fixed target. Variant `fixed`: target +15 points, stop unchanged.
- Points: MCX crude was about ₹4,500 when the document was uploaded (2018). 1 point = CL price / 4,500
  (≈ 1.6 ticks at $70). 10 points ≈ 0.22%, 15 points ≈ 0.33%.
- Intraday only: flatten 3:10 PM CT. All session hours (the document gives none). 1 contract.

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
| exit | trail | trail, fixed |
Total combinations on dev: 2. Validation only for a combination that passes the dev gates.

## Pass criteria
PROTOCOL.md dev gates and beating the ~$5/trade touch-fill bias.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-13 | dev | touch | 14973 | -186,331 | 0.883 | 10.0% | — | trail after 10 pts |
| 2026-11-13 | dev | touch | 15436 | -75,661 | 0.955 | 15.9% | — | fixed 15-pt target |

All in-sample, 2 of 2 tried. Years positive 1/12 for both. The fixed target wins 51% for about 1:1 risk, so it
loses the fee and the trend filter adds nothing. Spot check: 400 trades vs raw bars, 0 problems. Validation not run.

Re-run 2026-11-13 after the review fixed the Supertrend warm-up (TradingView starts in a downtrend): trail
14,972 trades −$186,407 PF 0.883; fixed 15,435 trades −$75,897 PF 0.955. Same verdict.

Re-run 2026-11-13 after the Codex review: Supertrend now flips against the current bands, exactly like the Pine v5
reference (`ta.supertrend`). The old code compared against the previous bands; on dev 15m candles the direction
differed on 0 of 272,929 candles, so both runs are identical (trail −$186,407 PF 0.883; fixed −$75,897 PF 0.955).

Re-run 2026-11-13 after the Codex review fixed order expiry (orders now expire on clock time, `expire_min`;
before, missing minutes stretched them). These rows replace the ones above; the verdict is unchanged.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 14963 | -186,241 | 0.883 | 1/12 | 10.0% | trail |
| dev | 15425 | -76,147 | 0.955 | 1/12 | 15.9% | fixed 15 pts |

Re-run 2026-11-13 after Codex review round 5: (a) a timed order now blocks new signals until its deadline even
across a data gap; (b) candles belong to their own trading day, signals from a candle that only completes in the next
session are dropped, and day levels come from raw bars. These rows replace all earlier ones.

| Period | Trades | Net | PF | Years + | Pass rate | Note |
|---|---|---|---|---|---|---|
| dev | 14955 | -185,368 | 0.884 | 1/12 | 10.0% | trail |
| dev | 15418 | -75,819 | 0.955 | 1/12 | 15.6% | fixed 15 pts |
