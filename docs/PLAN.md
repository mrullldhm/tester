# Plan: TradingView Strategy Tester for CL1! (rev 1, 2026-10-29)

Owner: mrullldhm. Builder: Claude. Reviewer and independent replicator: Codex.

## Goal
A Python backtester that gives the same results the TradingView Strategy Tester would give on `NYMEX:CL1!`
1-minute bars, and writes a TradingView-style result document for every strategy tested.

## Fixed settings (TradingView "Properties" tab)
| Setting | Value |
|---|---|
| Initial capital | 50,000 USD |
| Order size | 1 contract (CL: 1,000 bbl, tick 0.01 = $10) |
| Commission | cash per contract, $2.01 per order = $4.02 round trip |
| Slippage | 0 ticks baseline; stress scenarios 1 tick and 2 ticks (separate tables) |
| Pyramiding | 0 (one position at a time) |
| Recalculate | not on every tick, not after order fills; `process_orders_on_close` off |
| Margin | none checked |
| Limit fill assumption | 0 ticks (limit fills on touch) |
| Bar Magnifier | off |

## Data
- `data/cl1/year=YYYY.parquet`: front-month CL (Databento `CL.v.0`, roll by volume, switch 00:00 UTC) for
  2010-06-06 .. 2026-10-13 plus Massive extension bars to 2026-10-27. Columns: ts (UTC bar open), raw_symbol,
  open, high, low, close, volume, vendor. Copied once from `market-tester` (`tools/import_market_tester.py`).
- `python -m tvtester.update` adds new bars: Databento `CL.v.0` ohlcv-1m by default (prints the cost quote and
  asks first), Massive REST as a fallback (front picked by previous UTC day volume, same rule).
- Known gap to TV: TradingView's own CL1! roll dates and a few bars can differ. Results are "TV semantics on
  Databento CL front month", documented in the README.

## Engine (TradingView broker emulator)
- Script runs at each bar close; orders work from the next bar. Market orders fill at the next bar open.
- Intrabar path: O-H-L-C if the high is nearer the open, else O-L-H-C (tie: O-L-H-C, unverified).
- Stops/limits: fill at the open if the open gaps through; else at the order price when the path reaches it.
  Exit orders (`strategy.exit` with stop + limit, one bracket per entry) can fill on the entry bar after the fill.
- Slippage (TV): market and stop fills move N ticks against the trader; limit fills do not.
- Commission per filled order.
- **Roll rule (owner choice):** a position never crosses a contract roll. If a position is open on the last bar
  of a contract, it is closed at that bar's close (exit reason `roll`).
- Bars are 1-minute; the engine only calls the strategy on bars it asks for (active mask) plus any bar with a
  position or working order, so a 16-year run stays fast.

## Report (TradingView Strategy Tester tabs)
- **Overview**: net profit, total closed trades, % profitable, profit factor, max drawdown, avg trade,
  avg bars in trade, equity curve PNG.
- **Performance Summary** (All / Long / Short): net profit, gross profit, gross loss, max run-up, max drawdown,
  buy & hold return, Sharpe, Sortino, profit factor, max contracts held, open P&L, commission paid, total
  closed trades, total open trades, winners, losers, % profitable, avg trade, avg win, avg loss, ratio avg
  win/avg loss, largest win/loss, avg bars in all/winning/losing trades. Definitions follow TV help pages
  (Sharpe/Sortino on monthly returns, rf 2%/yr, not annualized; drawdown intrabar from trade excursions).
- **List of Trades**: Trade #, Type, Signal, Date/Time, Price, Contracts, Profit, Cum. Profit, Run-up, Drawdown.
- Extra (not in TV): results by year, by session, exit reasons.

## Docs per strategy
`docs/strategies/<strategy>/README.md` (one per strategy; sub-section per session variant):
1. Strategy rules and source; 2. Parameter grid and how the top combination was chosen (highest net profit,
   baseline costs); 3. Top combination: full TV report at 0 slippage; 4. Same combination at 1-tick and 2-tick
   slippage (separate tables); 5. Top 10 combinations table; 6. Caveat: picking the best of N combinations on
   the same data overstates future results.
Trades CSV and summary JSON in `results/<strategy>/`.

## First strategy: 9:29 ET Fair Price Reversal (LuxAlgo, MPL-2.0), 3 session variants for CL
Signal logic ported line for line from the 1-minute path (`strategies/reference/*.pine`): 9:29 body,
ATR(14)[1] excursion, 21-bar pivot buffer, lower-high / higher-low structure, MSS break inside the window.
For CL the anchor minute is the minute before each session open (verified against CL volume, median per
minute 2024-2025):

| Session | Open (local) | Anchor candle | Malaysia time (UTC+8) | Volume spike |
|---|---|---|---|---|
| Asia | 09:00 Asia/Shanghai (= Singapore / Kuala Lumpur, no DST) | 08:59 | 09:00 all year | 204 vs 16 before |
| London | 08:00 Europe/London | 07:59 | 15:00 (BST) / 16:00 (GMT) | 168 vs 45 |
| New York | 09:00 America/New_York (NYMEX crude open) | 08:59 | 21:00 (EDT) / 22:00 (EST) | 1001 vs 170 |

US and UK change clocks on different dates, so each session uses its own time zone, never a fixed UTC offset.

The indicator has no exits, so the strategy adds (documented as our addition):
- Entry: market order at the next bar open after the signal bar (TV default).
- Stop: the excursion extreme (highest high for shorts / lowest low for longs from the excursion bar to the
  signal bar).
- Target modes (grid): `near` (9:29 body edge nearest), `far` (far body edge), `rr1`, `rr2` (1R / 2R from fill).
- Flat at session end: Asia 15:00 Shanghai, London 13:00 London, New York 14:30 New York (CL settlement).
- Grid per session: window [30, 60, 90, 120] x ATR mult [0.5, 1.0, 1.5, 2.0] x pivot strength [1, 2, 3]
  x target [near, far, rr1, rr2] = 192 combinations; ATR length 14 fixed.

## Codex
1. Review this plan (now). 2. Review engine + strategy code with a hashed pytest log. 3. Replicate the top NY
   combination's net profit and trade count independently from the parquet files.
