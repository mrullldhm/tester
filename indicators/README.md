# Tupa chart indicator

Paste [`tupa.pine`](tupa.pine) into TradingView's Pine Editor, save, and add it to a CL chart.
It combines the owner swing indicator with two possible next-swing levels. The existing
[`structure_swings.pine`](structure_swings.pine) remains available separately; only add Tupa
if you want to avoid drawing the swing labels twice.

## Default behaviour

The latest **confirmed reference-timeframe swing high** selects possible swing-low levels.
The reference timeframe defaults to **Daily** and stays fixed when you switch chart timeframes:

- **White:** the previous closed reference candle's low.
- **Blue:** the latest confirmed swing low on the next lower timeframe.

A confirmed reference swing low selects the mirror: previous candle high and lower-timeframe swing high.
With Daily selected, the automatic lower timeframe is **4H**. The other automatic steps are
monthly → weekly → daily → 4H → 1H → 15m → 5m → 1m. Intermediate chart periods select the
nearest smaller timeframe in that list. A 1m reference has no lower-timeframe line.

Each marker is visible on its source timeframe and every smaller chart, and hidden on larger charts:

| Settings: Daily reference, Auto lower | Daily chart | 4H chart | 1H / 15m / 5m / 1m chart |
|---|---|---|---|
| Daily previous-candle level (white) | visible | visible | visible |
| 4H confirmed-swing level (blue) | hidden | visible | visible |

Select **4H** as the reference to use 4H previous-candle levels and confirmed 1H swings instead.
Changing the viewing chart does not replace these sources with that chart's own candles.

The lines are **solid, width 1** by default, and extend right **from the source candle**: the first
previous candle supplying the low/high, or the candle containing the confirmed lower swing. The
historical anchor is visual only; the line appears only after its source data becomes available.
The indicator shows only the latest level from each source, rather than every historical candidate.
**Remove failed swing candidates** is enabled by default. A touch is a possible formation event,
not proof of a swing. The candle that touches a marked level is tracked as the candidate:

- For a swing low, the next reference candle must keep its low strictly above the candidate candle's low.
  A touch or break removes the old candidate level. The previous-candle line then marks the failed
  candidate candle's low, ready for a new attempt.
- Swing highs mirror this: the next candle must remain strictly below the candidate high.
- An invalidated lower-timeframe swing level stays hidden until a newer confirmed lower swing
  becomes available. It is not restored from the same stale source on the next reference candle.

For example, candle A has low 100.00 and candle B raids it with low 99.00. The old 100.00 line
is kept while B's swing-low possibility is being tested. If candle C touches 99.00, the 100.00
candidate is removed, the previous-candle line moves to B's 99.00 low, and a failed lower-source
line is hidden. This display update can occur during C; it does not wait for C to close to acknowledge
a touch that has already invalidated the strict-right condition. B's final low is known because B
has closed. The current forming candle's low is never substituted as the replacement source.

Turn the setting off to show the latest source levels without this invalidation lifecycle.
Swing confirmation follows the owner detector, including later extreme replacement; it does not
mean that the swing is final or guaranteed to hold.

## Settings

Under **Possible next swing levels**, configure the reference timeframe, each source's visibility and color,
line width, price labels, status panel, lower timeframe and failed-candidate removal. **Next swing** can use Auto or manually display
Swing low / Swing high possibilities. Manual direction affects the markers, never swing detection.
The lower timeframe must be smaller than the reference timeframe.

The original swing zigzag, labels and display colors remain configurable separately. Swing strength,
neighbour equality, confirmation timing, alternation and leg-extreme validity are fixed.

## Timing and verification

The current reference candle's forming high/low is excluded from the previous-candle level. Lower swings use
only closed lower candles, with the confirmation at their right neighbour's close. Neither source
requires waiting for a lower swing to become final. Requests use TradingView's native session-aligned
candles; use standard CL time-based candles and the intended chart session settings.
Forming candle ranges are used only to track level touches and invalidate display candidates;
they do not change swing detection. The three-candle validity rule uses reference candles even on
smaller charts. Closed reference snapshots are requested with a one-source-candle offset; displayed
lower swings refresh at their own closes. A smaller chart can detect a touch of the last closed
reference candle's extreme without reading the reference candle's eventual future high/low.
Pre-confirmation prices are excluded from a new lower level's touch tracking.

Lower-timeframe history and 1m ordering data depend on the data available to the account. Missing
1m ordering uses the same owner open-distance fallback; an affected outside swing is marked `?`.
The status panel reports when no suitable lower swing is available. The lower snapshot uses Pine v6
[nested requests and intrabar arrays](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/).

The chart swing core is copied verbatim from `structure_swings.pine`. The request-safe lower state
uses the same pivot, alternation, replacement, leg-extreme and ordering rules without creating drawings.
This file has not yet been compiled or visually checked in TradingView. Local verification does not
establish TradingView execution parity. No backtest or trade recommendation is provided by the levels.
The scripted source checks were refused before execution by the research guard (5 November): available
RAM 5.15 GiB, startup requirement 8.34 GiB. Limits were not changed and the workload was not retried.
