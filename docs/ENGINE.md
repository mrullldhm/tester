# Engine rules (TradingView broker emulator)

This page lists every rule the tester uses to turn orders into fills and fills into the Strategy Tester
numbers. Each rule follows TradingView's documented behaviour for a strategy with the properties below.
Where TradingView does not document a case, the rule is marked **convention**.

## Properties (fixed for every test)
| `strategy()` argument | Value |
|---|---|
| `initial_capital` | 50000 |
| `default_qty_type`, `default_qty_value` | `strategy.fixed`, 1 (CL: 1,000 barrels, $0.01 tick = $10) |
| `commission_type`, `commission_value` | `strategy.commission.cash_per_contract`, 2.01 (charged on every fill: $4.02 round trip) |
| `slippage` | 0 baseline; scenarios 1 and 2 ticks |
| `pyramiding` | 0 |
| `calc_on_every_tick`, `calc_on_order_fills`, `process_orders_on_close` | false |
| `margin_long`, `margin_short` | 0 (no margin check; Pine v6 defaults to 100%, which would reject 1 CL on $50,000) |
| `backtest_fill_limits_assumption` | 0 (a limit fills when price touches it) |
| `use_bar_magnifier` | false |

## Script cycle
1. The strategy runs at the **close** of each bar. It sees that bar and every earlier bar, never a later one.
2. Orders it places start to work on the **next** bar.

## Fills on a bar
1. **Intrabar path.** The emulator assumes price went open, then the nearer extreme, then the other extreme,
   then close: O-H-L-C if the high is nearer the open, else O-L-H-C. Equal distance: O-L-H-C (**convention**).
2. **At the open.** Market orders fill at the open. A stop or limit the open has gapped through fills at the
   open (a limit gets the better open price).
3. **Triggered stops.** A stop (entry, or exit placed while in a position) that is already through the close when
   placed is triggered: it fills at the next open even if that open gaps back.
4. **Along the path.** A stop fills at its price when the path reaches it; a limit fills at its price when the
   path touches it. Orders fill in the order the path meets them.
5. **Exits on the entry bar.** A `strategy.exit` placed with its entry starts working from the entry fill
   point, on the same bar. `profit` / `loss` distances are measured from the actual fill price.
6. **Brackets.** Each `strategy.exit` id is one bracket (stop and limit legs). The first leg to fill cancels
   the other. Placing the same id again amends it. All exits are removed when the position closes. When a level
   is given both as a price (`stop` / `limit`) and as a distance (`loss` / `profit`), the one price reaches
   first is used (Pine v6).
7. **Entries.** With `pyramiding = 0`, an entry in the same direction as the open position is ignored. An entry
   in the opposite direction reverses the position (TradingView behaviour) and keeps the new entry's exits.
   Strategies here only enter when flat.
8. **Not supported (raises an error instead of guessing):** stop-limit entries, and more than one
   `strategy.exit` id per entry (Pine's quantity reservation across partial exits).
9. **Slippage.** Market and stop fills move N ticks against the trader. Limit fills never slip.
10. **Commission.** $2.01 x contracts on every fill. Cancelled orders cost nothing.

## Filters (feature 2)
- An entry filter vetoes an order at the signal bar's close; the signal logic and its state are unchanged (a vetoed
  signal still uses up that day's signal). The veto is checked where the entry is decided (`on_bar`), because the
  engine also calls `on_bar` on bars where a position is open or closes. Full rules: `docs/OPTIMIZE.md`.
- Every trade records its **signal bar** (the bar whose close placed the entry order): `signal_bar` and
  `signal_time` in the trades CSV. Feature values are read at that bar, never at the fill bar.

## Owner rules (not TradingView behaviour)
- **Roll exit.** A position open on the last bar of a contract is closed at that bar's close (reason `roll`).
  TradingView's CL1! would hold through the roll and book the price gap as profit or loss.

## Strategy Tester numbers
| Number | Definition |
|---|---|
| Trade profit | (exit - entry) x direction x contracts x $10 per tick - commission (entry + exit) |
| Net profit | gross profit - gross loss |
| Gross profit / loss | sum of winning / losing trade profits (after commission) |
| Profit factor | gross profit / gross loss (— when there are no losers) |
| Percent profitable | winning trades / all closed trades (even trades count in the total) |
| Avg # bars in trades | exit bar index - entry bar index + 1, bars as they exist in the data |
| Max equity drawdown (intrabar) | for each bar in a trade (the open trade at the end included): highest closed equity before the trade - equity at entry + contracts x adverse move to the bar's low (long) / high (short). Largest value. Entry and exit bars count only the part of the path while the trade was open. % = of initial capital |
| Max equity run-up (intrabar) | mirror: equity at entry - lowest closed equity before the trade + favourable move to the bar's high (long) / low (short) |
| Sharpe ratio | (mean monthly return - 2%/12) / standard deviation of monthly returns (population). Monthly return = month-end equity / previous month-end equity - 1, every calendar month (UTC) of the test. Month-end equity = closed profit + open P&L at the month's last close (entry commission included). Not annualized |
| Sortino ratio | (mean monthly return - 2%/12) / sqrt(mean(min(0, r - 2%/12)^2)) over all months |
| Buy & hold return | (last close - first trade's entry price) / first trade's entry price, applied to the initial capital (all capital at the first entry, as TradingView). The unadjusted front-month series includes roll gaps |
| Open P&L | the open position at the end, marked at the last close, after entry commission |

## Data and parity limits
- Bars: Databento `CL.v.0` (front month by previous-day volume, switching at 00:00 UTC) plus Massive bars
  for the latest days. TradingView's CL1! also switches by volume, with its own per-symbol rule, so a few roll
  days can differ by a day or so. Bars can differ slightly between vendors.
- 2020-04-20: Databento's front month had already rolled to the June contract (CLM0), while TradingView's CL1!
  still showed May (CLK0), which settled at -$37.63.
- The only real proof of parity is a TradingView export of the same strategy. Use the Pine twin of each strategy
  (`strategies/*.pine`) on `NYMEX:CL1!` 1-minute with Deep Backtesting and compare trades.
