# Elliott Wave 5: spec and sources

Intraday CL1! 1-minute strategy that trades wave 5 after a confirmed wave 4. No position is held overnight:
each variant is one session and is flat by its flat time. Results: [results.md](results.md) (in-sample).

## Sources

| Source | What it gives | What it does not give |
|---|---|---|
| "10 Seconds Elliott Wave", 2nd ed. (Immy Yousafzai, iTradeAIMS, 2023; after Bill Williams, *Trading Chaos*) | Wave count on the Awesome Oscillator: 100-140 bar window, tallest AO peak = wave 3, AO zero cross against it = wave 4 minimum, divergence = wave 5. Wave 4 retraces 38-50 %; deeper than about 62 % truncates wave 5. Wave 5 ends at Target Zone 1 / 2 (61.8 % / 100 % expansion) "8 out of 10 times". | A complete entry: "The Setup One", AIMS Box, AIMS Gator and its Purple Line are paid products the book does not define. No backtest; the 80 % and 466 % claims have no source. |
| markokrivokapic.com, 31 articles (impulse, corrective patterns, Fibonacci, fractals, truncation) | Hard rules (W2 never past the W1 origin, W3 never the shortest, W4 never into W1 territory except diagonals) and Fibonacci zones: W4 0.382 of W3 (0.236 / 0.5), W5 = W1 or 0.618 of W1-W3, C = A, and so on. | Entry, stop, sizing and exit rules: none on any page. Swing / degree selection is discretionary. Corrective patterns confirm only after they complete. No backtest; every percentage is unsourced. |

The book is not by the same author as the website.

## Rules (long; short is the mirror)

| # | Rule | Origin |
|---|---|---|
| 1 | AO = SMA5(hl2) - SMA34(hl2), 1m, every bar; exact in ticks (340 x AO) | Book (Bill Williams AO) |
| 2 | Wave 3: tallest AO peak of the last `window` bars is green, taller than the deepest red one, and in the current AO hump | Book, steps 2-3 (`window` 100 / 140) |
| 3 | Wave 4 confirmed: AO crosses below zero; decision at that 1m close, inside the session | Book, step 4 |
| 4 | Top = the hump's highest high, and it must be the current owner 1m swing high | Ours (mandatory owner swings, docs/ENGINE.md) |
| 5 | Base = lowest low of the window; L = top - base >= `min_len` ticks | Ours (the book's "start of wave 1" anchor; its two anchor descriptions conflict, p124 vs p126) |
| 6 | Entry: buy **limit** at top - `entry_r` x L, or the signal close if lower; from the next bar | Ratio: book 38-50 % / Krivokapic 0.382. Limit only: owner |
| 7 | Skip when the pullback has already touched the stop level | Ours |
| 8 | Stop: top - `stop_r` x L (0.618 / 0.786) | Book: wave 4 beyond about 62 % truncates wave 5; 0.786 is Krivokapic's deep level |
| 9 | Target: limit + `tp_x` x L (0.618 = TZ1, 1.0 = TZ2) | Book target zones, projected from the planned wave-4 end (ours) |
| 10 | Unfilled limit cancelled when a 1m close finds the target touched, at the session end and on the contract's last bar | Owner limit-entry lifecycle (docs/ENGINE.md) |
| 11 | Flat at the session end (close at the next open); one position or order at a time | Owner: no overnight |

Not used: the book's divergence exit and Purple Line filter (undefined), every corrective-pattern and
Fibonacci-time rule from the website (hindsight-only or no trade rule), slippage scenarios (owner: limit
entries, no slippage tests).

## Properties

$50,000, 1 contract, $2.01 per order ($4.02 round trip), no slippage, sessions as in docs/SESSIONS.md.
Pine v6 twin: [`strategies/elliott_wave.pine`](../../../strategies/elliott_wave.pine), not yet compiled or
compared against a TradingView export.
