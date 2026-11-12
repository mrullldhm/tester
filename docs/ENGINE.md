# Engine fill rules

Code: `cltester/engine.py`. Tests: `tests/test_engine.py` (one test per rule). Change this file with the code.

Owner rules: **entries are limit orders only**, a **touch fills** a limit, and **exits have no slippage**: every
exit fills at the stated price. A gap is not slippage: when the bar opens beyond a stop, the open is the first
traded price, so the stop fills there.

## Order life

| Step | Rule |
|---|---|
| Signal | Computed on bar *i* using data up to bar *i* close. The order works from bar *i+1*. Rows with a missing or non-finite limit/stop are refused. |
| Working | Up to `expire` bars (default 30). Cancelled at the trading-day change, contract change or 3:10 PM CT. |
| One at a time | A signal is ignored while an order works or a position is open. A signal on the exit bar is accepted. |
| Size | `qty` contracts (default 1); the Combine simulator refuses more than 5. |

## Fills (long side; shorts are the mirror image)

| Event | Condition on bar *j* | Fill price |
|---|---|---|
| Limit entry | low ≤ limit (a touch fills) | min(open, limit) |
| Stop on the fill bar | low of the fill bar ≤ stop (assume the low came after the fill) | min(entry, stop) |
| Flatten | first bar at or after 3:10 PM CT | open |
| Stop at the open | open ≤ stop | open (gap) |
| Target at the open | open ≥ target | open (gap in our favour) |
| Stop | low ≤ stop | stop |
| Target (limit) | high ≥ target (a touch fills) | target |
| Stop and target both inside one bar | stop first (worst case) | stop |
| Target on the fill bar | not allowed (unknown order inside the bar) | — |
| Time exit (`hold`) | `hold` bars after the fill bar | close |
| Contract change | last bar before `raw_symbol` changes | close |
| Day end | last bar of the trading day (early-close holidays end before 3:10 PM) | close |
| End of data | last bar loaded, position still open | close |

Check order per bar after the fill bar: flatten, stop at open, target at open, stop inside the bar, target inside
the bar, then end of data / time / roll / day end at the close. The open is the first price of the bar, so an exit
there happens before anything else in that bar.

## Money

- CL: tick $0.01 = $10 per contract. Prices are compared as integer ticks.
- Fee $4.04 per contract round turn, charged in `net`, `mae` and `mfe`.
- `mae`: worst open P&L during the trade from bar lows (longs) incl. fee, used by the Combine MLL check.
  An exit at the open counts only the open; a stop inside the bar counts the stop; other exit bars count the whole bar.
- `path`: per held bar, (open P&L, worst P&L) incl. fee. The Combine simulator walks it so a gap through a loss
  limit executes at the open price. Not written to the trade CSV.
  The exit price always counts, so MAE is never better than the realized result.

## Why these rules

- Touch fills and no exit slippage are owner rules. Both are optimistic: in live trading a limit at the touch can
  sit in the queue unfilled, and a stop can fill a tick or more worse. Keep that in mind when a result depends on
  many small wins at exact limit prices.
- Worst-case intrabar order: 1-minute bars do not show the order of high and low. Assuming stop first can only make
  results worse, never better.
- Flat by 3:10 PM CT and at each contract change: Topstep closes positions at 3:10 PM CT, and the continuous series
  is not back-adjusted, so holding through a contract change would book a fake price jump.
