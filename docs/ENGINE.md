# Engine rules (TradingView broker emulator)

> **Execution update — 3 November 2026.** New runs use limit entries and commission only, with no
> added slippage and no 1- or 2-tick stress scenarios. Fair Price Reversal places
> the limit at the signal/decision close, active from the next bar. A waiting entry is cancelled when
> the planned TP has been reached and it is still unfilled at the one-minute close. Existing session
> boundaries still cancel waiting orders; Tupa Trade retains its stop-limit trigger and swing invalidation.
> Limit fills can be at the limit or better. Stops and forced closes retain their existing order types.
> Historical reports, configurations and ledger entries are retained; they are not results of these new rules.


This page lists every rule the tester uses to turn orders into fills and fills into the Strategy Tester
numbers. Each rule follows TradingView's documented behaviour for a strategy with the properties below.
Where TradingView does not document a case, the rule is marked **convention**.

## Properties (fixed for every test)
| `strategy()` argument | Value |
|---|---|
| `initial_capital` | 50000 |
| `default_qty_type`, `default_qty_value` | `strategy.fixed`, 1 (CL: 1,000 barrels, $0.01 tick = $10) |
| `commission_type`, `commission_value` | `strategy.commission.cash_per_contract`, 2.01 (charged on every fill: $4.02 round trip) |
| `slippage` | 0; no stress scenarios |
| `pyramiding` | 0 |
| `calc_on_every_tick`, `calc_on_order_fills`, `process_orders_on_close` | false |
| `margin_long`, `margin_short` | 0 (no margin check; Pine v6 defaults to 100%, which would reject 1 CL on $50,000) |
| `backtest_fill_limits_assumption` | 0 (a limit fills when price touches it) |
| `use_bar_magnifier` | false |

## Mandatory swing definition (owner, 4 November 2026)

All current and future strategies, features, tests, searches, charts and swing trailing exits use
`indicators/structure_swings.pine`, implemented by `tvtester/swings.py`. No adjustable swing settings or
alternative pivot algorithms are allowed. A high uses left <= centre and right < centre (low mirror),
confirmed only when the right candle closes. Swings alternate; a same-type candidate replaces the newest
only when at least as extreme (equal: later). Outside candles process extremes in first-touch 1-minute
order, using the indicator open-distance fallback when needed (ties: low first). Equal highs label HH,
equal lows LL. Continue through contract rolls. The newest swing may move until the opposite type is added.

**Owner clarification, 10 November 2026:** the newest endpoint is provisional until an opposite swing
is accepted. An equal touch or breach before then removes it immediately, restoring surviving fixed
levels rather than an older provisional version of the removed endpoint. **11 November clarification:**
at a right-candle close, qualifying opposite-pivot confirmation takes priority over that candle's touch
removal. An endpoint removed during a forming HTF candle is secured/restored if that opposite pivot
qualifies when the candle closes. Historical decisions before that close are never backdated.
Historical replays expose removal at the first touching
1-minute close, including within forming higher-timeframe candles; live indicators check every update.
Confirmation of new pivots and higher-timeframe trend changes still require their existing candle closes.
Removal is a state event, not a new pivot signal. Previously emitted historical events are not erased.
Results predating this clarification must be rerun before being presented as current.

Historical pivot-based results do not establish results under these rules; rerun them before publication.

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
8. **Stop-limit entries** (`strategy.entry(stop=, limit=)`). The stop is only a trigger: when the path reaches it,
   or the open gaps through it, the order becomes a limit order at its limit price and fills when the rest of the
   path touches that limit, on the same bar or later (at the open if a later open is already through the limit).
   A limit already marketable at the trigger point fills there (limit = stop: at the stop). Touching the limit before
   the trigger does nothing. Limit fills never slip. **Convention**, not yet checked against a TradingView export
   (the first check is the 26 Oct 2026 tupa_trade trade). A stop-limit placed with its stop already through the
   close raises an error (TradingView's behaviour there is not verified).
9. **Not supported (raises an error instead of guessing):** more than one `strategy.exit` id per entry (Pine's
   quantity reservation across partial exits).
10. **Slippage.** Market and stop fills move N ticks against the trader. Limit fills never slip.
11. **Commission.** $2.01 x contracts on every fill. Cancelled orders cost nothing.

**Optional broker cancellation.** Generic entries can carry `cancel_touch` and `cancel_side` boundaries;
touches cancel an unfilled entry along the broker path, with cancellation first at a gap through both
prices. FSP does not use that optional pending-order feature.

**FSP MSS eligibility.** After the breach confirmation candle closes, touching its fixed 15m high
invalidates subsequent short MSS signals; touching its fixed 15m low invalidates subsequent long MSS
signals. The MSS minute must not reach that boundary before its own close, when the entry decision is
made. Later 1H candidates and previous-1H extremes have no cancellation role. Already-placed limits are
unaffected by that eligibility cutoff and keep their price/bracket until fill or the entry/day cutoff.

**FSP New York reset and entry window (owner default update, 11 November 2026).** FSP entries/fills use
09:00–14:30 America/New_York. At 14:30 ET, or the earlier scheduled exchange close, cancel limits,
close remaining positions with `close_all(immediately=True)` and discard failed setups. Only new
failed setups can arm trades after reset. TP is 50 ticks from actual fill, max planned risk remains 25. The daily source's
later swing-confirmation timestamp is not used as an execution deadline. The bounded calendar supplies
regular/holiday close times without observing a later price gap. If a halt spans the cutoff, cancel the
old orders and queue the overdue market close before processing the first available reopening bar;
the position exits at that bar's open, labeled `New York halt reopen`, before its intrabar bracket path.
No price is fabricated or backdated. These lifecycle
changes do not reset or modify owner swing detection. Fresh failures after the cutoff belong to the next
New York cycle, without a second reset at the CL evening reopen. Each failed 1H setup can supply only
its first valid 1m entry signal. No later attempt is allowed after TP, SL, cancellation or a first signal
skipped while another trade/order is active. All 43 focused checks pass. The full baseline through 2023
is complete with the owner-approved halt exception. Independent raw CL replay matches all 3,198
entry/exit prices and times and net P&L to the cent, with no repeated trade from one failed setup.
This audit uses supplied signals and does not independently detect swings.

## Limit-entry lifecycle (owner rule, revised 3 November 2026)

- Fair Price Reversal: limit at the signal candle close.
- Elliott Wave 5 (12 November 2026): limit at the wave-4 Fibonacci level, or the signal close when that is
  nearer the stop. Stop and target are absolute prices fixed at placement. Same TP expiry and session
  cancellation. Limit entries only (owner); the stop is an exit order. Spec: `docs/strategies/elliott_wave/`.
- The limit starts working on the next bar, with its bracket already attached. No re-pricing while waiting.
- Planned TP is fixed at placement: the anchor target for near/far, otherwise the planned limit plus/minus
  the declared profit distance. Actual relative-profit exits still measure that distance from the fill.
- Cancellation runs at each one-minute close, after the engine has processed that candle. If the entry is
  still waiting and that candle touched the planned TP, cancel the entry and its bracket. This is a
  bar-close rule, **not intrabar cancellation**: a fill earlier in the same candle remains a trade.
- Waiting orders are also cancelled at the existing session boundary and on the old contract's last bar.
  The Pine twins do not emulate the owner's contract-roll rule.
- Tupa Trade keeps its MSS stop-limit, swing invalidation and one-filled-trade-per-session rule, adding TP
  expiry. A TP-expired Tupa setup cannot re-arm unchanged.
- Default runs, searches, replay and validation add no slippage. The generic broker can still emulate
  nonzero slippage for old research and regression checks; no scheduled scenario jobs use it.

## Filters (feature 2)
- An entry filter vetoes an order at the signal bar's close; the signal logic and its state are unchanged (a vetoed
  signal still uses up that day's signal). The veto is checked where the entry is decided (`on_bar`), because the
  engine also calls `on_bar` on bars where a position is open or closes. Full rules: `docs/OPTIMIZE.md`.
- Every trade records its **signal bar** (the bar whose close placed the entry order): `signal_bar` and
  `signal_time` in the trades CSV. Feature values are read at that bar, never at the fill bar.

## Exit management (exit study; `tvtester/exits.py`, both Pine twins)
Custom stops moved at the bar close, plus an optional time exit. Not Pine's native `trail_points` / `trail_offset`
(which trail intrabar), so the twins compute every level themselves and amend the bracket with `strategy.exit`
(same id). `tvtester/exits.py` has the exact formulas; summary:
- **When.** At every 1-minute bar close while in a position, after the session-end / ST-flip checks. A moved stop
  works from the next bar; a level hit and given back inside one bar cannot exit on that bar. A time exit cancels
  the bracket and closes at market (next open), like the ST flip.
- **Units.** T = the trade's target distance in ticks, frozen at entry (`profit=` ticks, or |limit - fill|).
  Entry = the actual fill, slippage included (`strategy.position_avg_price`). best = most favourable high / low
  since the entry bar, with the full entry candle included to match the Pine exit-management scripts.
  For an intrabar limit fill this convention can include movement before the fill; it is not a measure of
  post-fill excursion. Engine drawdown and run-up still use only the exposed part of the path. rnd = round half up (Pine `math.round`); indicator levels round toward the trade's side.
- **Breakeven** (stop to entry + `be_offset` ticks): `touch` (best reaches `be_x` x T), `close` (a close reaches
  it), `time` (after `be_x` bars if the close is more than `be_offset` ticks in profit).
- **Trailing** (active once best reaches `trail_at` x T): `frac` (best - x T), `atr` (best - k x ATR(14) of the 1m
  chart), `swing` (last confirmed owner 1m swing low / high, fixed detection), `step` (lock one step behind each step
  of T reached), `close` (best close - x T), `ema` (EMA(n) of the 1m close), `sar` (`ta.sar` of the 1m chart).
  EMA and SAR count only while on the trade's side of the close. Indicators are computed on every bar, flat or not.
- The stop becomes the tightest of the current stop and the active levels. Never looser: a strategy policy, not an
  engine rule.
- A level already through the close is a triggered stop: it fills at the next open, with stop slippage. Breakeven
  is a stop price, not a guaranteed result. If that next open is also past the kept target, the stop leg fills
  (stop checked first at the open, **convention**: not checked against a TradingView export).
- `keep_target=False` (with a trailing stop or a time exit): no profit leg from the entry on (`profit = na`).
- **Unverified:** `swing` and `sar` use the owner swing twin and the Pine reference `pine_sar`. Not yet checked against a TradingView export.
- Defaults (`be="none"`, `trail="none"`, `time_exit=0`) are the plain strategy, trade for trade (test).
- `python -m tvtester.cli exits <name>` sweeps 396 rules on each variant's frozen feature-1 baseline over the full
  feature-1 interval (`tvtester/exitstudy.py`). In-sample, best of N, uses the reserved 2024+ bars.

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

Period tables (extra, not a TradingView tab; `metrics.by_period`, `metrics.by_year` is its year case): closed trades
grouped by the **UTC calendar date of the exit**, by year, month, ISO week (Monday start, named by that Monday) or
day. Per period: trades, net profit (sum of trade profits), % profitable (profit > 0), profit factor (gross profit /
gross loss, undefined with no losing trade). Periods without exits are left out. UTC dates are not CL trading days:
a Sunday 18:00 New York open is still the previous UTC week.

## Data and parity limits
- Bars: Databento `CL.v.0` (front month by previous-day volume, switching at 00:00 UTC) plus Massive bars
  for the latest days. TradingView's CL1! also switches by volume, with its own per-symbol rule, so a few roll
  days can differ by a day or so. Bars can differ slightly between vendors.
- 2020-04-20: Databento's front month had already rolled to the June contract (CLM0), while TradingView's CL1!
  still showed May (CLK0), which settled at -$37.63.
- The only real proof of parity is a TradingView export of the same strategy. Use the Pine twin of each strategy
  (`strategies/*.pine`) on `NYMEX:CL1!` 1-minute with Deep Backtesting and compare trades.

## Feature 1: thirteen separate metric winners

The `test` command evaluates the same grid once and selects a separate winner for each of these objectives:

| Objective | Direction | Definition |
|---|---|---|
| Net profit | Highest | Sum of closed-trade net P&L, after commission; excludes final open P&L |
| Win rate | Highest | Winning closed trades / all closed trades, including breakevens |
| Expectancy | Highest | Mean net P&L per closed trade, in USD; the existing average-trade metric |
| Profit factor | Highest | Sum of winning net P&L / absolute sum of losing net P&L; undefined without losses |
| Payoff ratio | Highest | Average winning net P&L / absolute average losing net P&L; requires both |
| Risk of ruin estimate | Lowest | Infinite-horizon diffusion approximation of reaching a fixed loss floor below initial capital |
| Maximum drawdown | Lowest | Existing intrabar account drawdown convention above; includes the final open position |
| Maximum consecutive losses | Lowest | Longest sequence of negative closed-trade results in execution order; zero or positive P&L resets it |
| Sharpe ratio | Highest | Existing monthly, marked-to-market, nonannualized definition above |
| Sortino ratio | Highest | Existing monthly, marked-to-market, nonannualized definition above |
| R-multiple | Highest | Mean of net trade P&L / initial dollar stop risk, with one R fixed at the actual entry fill |
| MAE | Lowest | Average of each closed trade's maximum adverse excursion in USD, before fees |
| MFE | Highest | Average of each closed trade's maximum favorable excursion in USD, before fees |

**Selection contract.** Default eligibility is at least 30 closed trades (`--min-trades` changes it). Each
metric excludes undefined and nonfinite values; a configuration with no trades cannot win a risk metric.
Ties use higher net profit, then higher profit factor (undefined last), then original grid order. Risk of ruin
uses its unrounded log probability for ranking so floating-point underflow does not turn different tiny risks
into false ties. If no configuration is eligible, that objective has no winner. Negative-profit configurations
remain eligible: winning a risk ranking does not imply making money. The unconstrained net-profit reference
and old CSV layout remain available for compatibility; eligible net-profit selection is explicitly separate.

**Initial risk and R consistency.** The engine freezes the initial attached bracket's stop distance at the
actual entry fill, before stop amendments. With both an absolute and relative stop, it uses the same resolved
stop as the engine. One R = positive signed distance from fill to stop × $10/tick × contracts, before fees;
trade R = net realized P&L / one R. A favorable gap changes actual risk. A missing stop, or a gap through the
stop resulting in zero/negative risk, leaves R undefined. The whole configuration's R objective is undefined
unless every closed trade has valid initial risk. Later stop moves never change R. Standard deviation of R
(population) and mean R / standard deviation are also saved to describe consistency; zero standard deviation
makes the consistency ratio undefined. This ratio is supplementary, not a fourteenth ranking.

**Excursions.** MAE/MFE reuse the engine's `worst`/`best` while exposed, via trade-frame `drawdown`/`run_up`.
Pre-entry and post-exit portions of a candle are excluded. Each trade has a maximum excursion; the grid
objective averages those maxima. These are gross price excursions, not equity drawdown or realized returns.
MFE can select wide-risk trades or trades that gave profits back, so its winner's MAE and realized net P&L
are shown beside it. Open trades do not enter trade-average objectives.

**Risk-of-ruin model.** The default loss budget is $25,000 from the $50,000 starting capital
(`--ruin-loss`, a positive dollar amount no larger than starting capital). Let μ and σ² be the population
mean and variance of closed-trade net dollar P&L. For at least two trades, the Brownian approximation is
`P(ever hitting -loss_budget) = exp(-2 * μ * loss_budget / σ²)` for μ > 0 and σ² > 0; it is 1 for μ ≤ 0
with positive variance. Zero-variance deterministic increments have probability 1 when negative and 0
otherwise. Published probabilities are percentages. This model assumes independent, stationary trade P&L
and unchanged fixed contract size forever. It ignores within-trade equity losses, serial dependence,
parameter uncertainty, margin, withdrawals and changes in market conditions. It is neither a validated
future probability nor a Topstep failure probability. Historical drawdown is a different quantity.

**Artifacts.** `grid.csv` gains all selection metrics, plus R spread/consistency and log ruin probability.
`metric_winners.json` records all definitions, eligibility, threshold, execution version, interval, winning
orders/parameters and all thirteen values for each winner. Each distinct selected order is rerun once into
`metric_winners/order_N/`, with summary and trades; several objectives can share that report.
`--output-tag metrics` writes separate `results/<strategy>/metrics/<variant>/` artifacts and
`docs/strategies/<strategy>/metrics.md`, keeping historical reports intact. The web exporter verifies winners
against the tester's selection rules, grid, rerun summaries and trade totals; it publishes only aggregate
values. The browser never computes trading metrics. Historical grids missing the new fields are marked
pending until rerun rather than populated with inferred results.

Definitions: [TradingView payoff ratio](https://my.tradingview.com/support/solutions/43000681719/),
[TradingView trade excursions](https://www.tradingview.com/blog/en/changes-in-the-backtesting-report-16416/),
[Van Tharp's initial-risk/R-multiple explanation](https://vantharp.com/wp-content/uploads/2018/06/A_Short_Lesson_on_R_and_R-multiple.pdf).
