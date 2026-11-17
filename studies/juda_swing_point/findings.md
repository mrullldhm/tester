# Juda Swing Point (15m swing break + manipulation candle): setup count

Owner idea 2026-11-18. Code: `run.py` (rules in its docstring). Events: `events.csv`. Holdout (2025+) not loaded.

## Definition used

Long: newest 15m swing point (owner rule) is swing high P. Candle j touches/breaks P before any swing low forms.
From j on (j included), while the structure is unchanged, manipulation candle m: high >= high[m-1] first, then
low < low[m-1] (1m order). Confirmation m+1: low > low[m]. EMA 10 > 20 > 50 (15m closes) at confirmation close.
Short: mirror (same code on negated prices).

## Counts (best of 1, no tuning)

| Period | Side | SH/SL invalidations | Setups (no EMA) | Setups + EMA at confirm | + EMA at manip too |
|---|---|---|---|---|---|
| dev 2010-06..2021 | long | 9,568 | 892 | 450 | 423 |
| dev | short | 9,176 | 848 | 377 | 358 |
| validation 2022-24 | long | 2,466 | 259 | 149 | 143 |
| validation | short | 2,391 | 249 | 113 | 106 |

About 60-75 setups a year with EMA (both sides), 22-65 per side per year. Not filtered by session.

- 68% long / 72% short: the manipulation candle is the break candle itself (owner chart example shape).
- Most invalidations end without a setup: a new swing high confirms first (~69%), or a swing low forms (~19%).
- ~2.5% end with an unknown in-candle order (high and low break in the same 1m bar): excluded.
- Risk (confirmation close to manipulation low): median 14 ticks long, 16 short; 95th pct 55 / 69.

## Descriptive race, dev only, in-sample (not a backtest: market at confirmation close, no fees)

| Side | n | 1R hit before stop | 2R hit before stop |
|---|---|---|---|
| long | 450 | 174 vs 210 stop (66 flat) | 114 vs 259 |
| short | 377 | 166 vs 169 stop (42 flat) | 104 vs 214 |

No edge visible at 1R/2R: about coin-flip at 1R, below breakeven at 2R before fees.

## Spot-check

Three 2019 setups (2 long, 1 short) checked against raw 1m bars: break, high-first-then-low order, confirmation
hold all correct. Owner's 2026-11-17 chart example not in data yet (data ended 2026-11-16 15:56 UTC).
