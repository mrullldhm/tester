> **Mandatory owner swings — 4 November 2026.** Every current and future strategy, feature, test,
> search and trailing exit must use only `indicators/structure_swings.pine` (`tvtester/swings.py`).
> Swing detection has no tunable settings: one neighbour per side, left equality/right strictness,
> next-candle-close confirmation, alternating swings, same-type extreme replacement (equal: later),
> and outside-candle ordering from 1-minute extremes with the indicator fallback. Equal highs are HH;
> equal lows are LL. No reset at contract rolls. Old pivot-based results are superseded.
> Active strategies: Fair Price Reversal and Tupa Trade. Supertrend Kalman is retired.

# TradingView Strategy Tester for CL1!

> **Execution update — 3 November 2026.** New runs use limit entries and commission only, with no
> added slippage and no 1- or 2-tick stress scenarios. Fair Price Reversal places
> the limit at the signal/decision close, active from the next bar. A waiting entry is cancelled when
> the planned TP has been reached and it is still unfilled at the one-minute close. Existing session
> boundaries still cancel waiting orders; Tupa Trade retains its stop-limit trigger and swing invalidation.
> Limit fills can be at the limit or better. Stops and forced closes retain their existing order types.
> Historical reports, configurations and ledger entries are retained; they are not results of these new rules.


A Python backtester that behaves like the **TradingView Strategy Tester** for one market only: **CL1!**, the
front-month NYMEX Light Sweet Crude Oil (WTI) future, on **1-minute bars**. For every strategy it tests,
it writes a results document laid out like TradingView's report: Overview, Performance, Trades analysis,
Risk/performance ratios and List of trades. New runs include commission and no added slippage.

> **In one sentence:** you write a strategy once in Python (plus a Pine twin for TradingView), run one command,
> and get a TradingView-style report for the best parameter combination with limit entries and commission included.

---

## Contents
1. [What you get](#what-you-get)
2. [Quick start](#quick-start)
3. [Test settings](#test-settings)
4. [How it works](#how-it-works)
5. [Project layout](#project-layout)
6. [Price data](#price-data)
7. [Testing a strategy](#testing-a-strategy)
8. [Optimizing a strategy (feature 2)](#optimizing-a-strategy-feature-2)
9. [Reading a results document](#reading-a-results-document)
10. [Adding a new strategy](#adding-a-new-strategy)
11. [Strategies tested so far](#strategies-tested-so-far)
12. [How close is it to TradingView?](#how-close-is-it-to-tradingview)
13. [Quality checks](#quality-checks)
14. [FAQ](#faq)

---

## What you get

| Feature | Details |
|---|---|
| TradingView broker emulator | Same fill rules as TradingView: orders placed at a bar's close fill from the next bar, the intrabar path (open, nearer extreme, other extreme, close), gaps, stop and limit orders, brackets, slippage on market and stop fills only |
| TradingView report | Net profit, gross profit and loss, profit factor, max equity drawdown and run-up (intrabar), Sharpe, Sortino, percent profitable, average trade, largest win and loss, average bars in trade, list of trades, for all trades and for longs and shorts separately |
| Parameter grid | Runs every combination, finds separate winners for 13 metrics, and documents each winner's settings and results |
| Sessions | Asia, London and New York sessions for CL, verified against real CL volume, each in its own time zone (daylight saving handled) |
| Data updater | Adds new 1-minute bars from Databento (primary) or Massive (fallback) with one command |
| Pine twins | Every strategy has a Pine v6 version so you can check the trades on TradingView itself |

---

## Quick start

Research commands now start the memory supervisor automatically, including direct CLI commands, default
runs, data updates and local trade replays. Only one heavy workload may run at a time.

- Hard address-space limit: **6 GiB per workload process**, one BLAS thread, `--jobs 1`.
- The supervisor stops the process group above **5 GiB observed resident memory**, below the system RAM
  reserve (20% of WSL RAM, at least 2 GiB), below 20% free swap, or during sustained memory pressure.
- An idle chart worker exits after 30 seconds to release its cached data and the research lock.
- Structured start/sample/stop records are written to `logs/resource_guard/`.

For custom Python scripts, use `.venv/bin/python tools/run_limited.py <script.py>`.
See [WSL prevention and activation](docs/WSL_PREVENTION.md) for the Windows-side settings and restart step.
These protections leave swing detection and trading rules unchanged.

```bash
cd tradingview-tester
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python -m pytest -q                                   # check the install (all tests should pass)
.venv/bin/python -m tvtester.cli test fair_price_reversal       # run a strategy, write its document
```

The document appears in `docs/strategies/fair_price_reversal/README.md`. The raw files (all combinations,
full trade lists, summaries) go to `results/fair_price_reversal/`.

Useful options:

```bash
# test a shorter period (UTC dates, end is exclusive)
.venv/bin/python -m tvtester.cli test fair_price_reversal --start 2024-01-01 --end 2025-01-01

# test one variant only, using 1 CPU process
.venv/bin/python -m tvtester.cli test fair_price_reversal --variants ny --jobs 1

# heavy grids: one process, through tools/run_limited.py
.venv/bin/python -m tvtester.cli test fair_price_reversal --jobs 1
```

---

## Test settings

These match the **Properties** tab of a TradingView strategy and are the same for every test
(`tvtester/config.py`).

| Setting | Value |
|---|---|
| Initial capital | **50,000 USD** |
| Order size | **1 contract** (CL = 1,000 barrels; 1 tick = $0.01 = **$10**) |
| Commission | **$2.01 per contract per order**, so **$4.02 per round trip** (entry + exit) |
| Added slippage | **0 ticks**; no stress scenarios |
| Pyramiding | 0 (one position at a time) |
| Margin | not checked |
| Limit orders | fill when price touches them |
| Bar Magnifier | off |
| Roll rule | a position open on the last bar of a contract is closed at that bar's close |

**Limit fills.** A limit prevents a worse entry price, but can remain unfilled or receive a better gap price.
The default broker settings add no slippage to any fills. Stops and forced closes are still modeled under
TradingView's existing order rules; the fee remains $2.01 per fill.

---

## How it works

Think of the tester as a flight simulator for a TradingView strategy. The price data is the weather recording,
the strategy is the pilot, and the broker emulator is the physics engine that decides exactly where each order
fills.

```
 data/cl1/*.parquet ──► Bars (prices in whole ticks)
                              │
                              ▼
 strategies/<name>.py  ──► prepare(): indicators over every bar
                              │
                              ▼
 tvtester/engine.py    ──► for each bar: fill working orders along the intrabar path,
                           then call on_bar() at the bar's close (new orders start next bar)
                              │
                              ▼
 tvtester/metrics.py   ──► TradingView numbers (Performance Summary, List of trades)
                              │
                              ▼
 tvtester/optimize.py  ──► every grid combination → 13 metric winners → reports, commission included
                              │
                              ▼
 tvtester/report.py    ──► docs/strategies/<name>/README.md + charts, results/<name>/*.csv
```

Key design choices, and why:

| Choice | Why |
|---|---|
| Prices are stored as whole **ticks** (integers) inside the engine | Exact comparisons. A float like 71.9999999 can never miss a stop at 72.00. Negative prices (CL on 2020-04-20) work too |
| Indicators are computed over **every** bar | Pine runs a script on every bar. Skipping bars would change ATR and swing points |
| The engine only calls the strategy on bars it needs (signals, open position, working orders) | A 16-year 1-minute test (5.6 million bars) runs in seconds, with the same results as calling it on every bar |
| Each session uses its **own time zone** | The US and UK change clocks on different dates; a fixed UTC offset would be wrong for weeks each year |
| Every strategy has a **Pine twin** | Python-to-Python checks cannot prove TradingView parity. Running the twin on TradingView can |

All fill and metric rules are listed one by one in [`docs/ENGINE.md`](docs/ENGINE.md).

---

## Project layout

| Path | What it holds |
|---|---|
| `tvtester/config.py` | Test settings (capital, commission, slippage scenarios, CL tick size) |
| `tvtester/data.py` | Loading the 1-minute bars; storage layout |
| `tvtester/engine.py` | TradingView broker emulator and the bar loop |
| `tvtester/metrics.py` | TradingView Strategy Tester numbers |
| `tvtester/ta.py` | Pine `ta.*` equivalents (`ta.atr`, `ta.rma`, `ta.tr`, swing pivots) |
| `tvtester/sessions.py` | Asia / London / New York session definitions |
| `tvtester/optimize.py` | Parameter grid, ranking, slippage re-runs |
| `tvtester/features.py` | Entry filters (vetoes) and point-in-time feature helpers |
| `tvtester/experiment.py` | Feature-2 protocol: development interval, provenance hashes, ledger |
| `tvtester/search.py`, `tvtester/associate.py`, `tvtester/tune.py` | Random / TPE search, feature association report, the `features` / `search` / `replay` commands |
| `tvtester/report.py`, `tvtester/cli.py` | Results documents and the command line |
| `tvtester/update.py` | Data updater (Databento, Massive) |
| `strategies/` | One Python file and one Pine twin per strategy; `reference/` keeps original source scripts |
| `docs/ENGINE.md` | Every engine and metric rule |
| `docs/SESSIONS.md` | How the CL session times were verified |
| `docs/PLAN.md` | The build plan, reviewed by Codex |
| `docs/OPTIMIZE.md` | Feature 2 protocol and feature contracts |
| `docs/strategies/<name>/README.md` | Feature 1 result (TradingView-style report) |
| `docs/strategies/<name>/optimize/` | Feature 2 result: `README.md` (summary and verdict), `features_*`, `search_*`, `winner_*` reports |
| `results/<name>/search/<run>/`, `results/<name>/ledger.jsonl` | Every search trial, neighbours, run provenance; the append-only record of every feature-2 run |
| `strategies/configs/*.json` | Frozen winning configurations (replayable) |
| `results/<name>/<variant>/` | `grid.csv` (all combinations), `trades_slippage{0,1,2}.csv`, `summary.json` |
| `data/cl1/year=YYYY.parquet`, `data/manifest.json` | Price data and its record (source, row counts, hashes, updates) |
| `tools/import_market_tester.py` | One-time import of the price data from the `market-tester` repo |
| `tests/` | Engine rule tests and the Pine port check |

---

## Price data

| Item | Value |
|---|---|
| Market | CL front month (the contract TradingView shows as CL1!) |
| Bar size | 1 minute, bar time = bar open, stored in UTC |
| History | 2010-06-07 to 2026-10-27 (5,667,487 bars at import) |
| Sources | Databento `GLBX.MDP3` `CL.v.0` (to 2026-10-13), Massive REST (after that) |
| Front-month rule | the contract with the highest volume on the previous UTC day, switching at 00:00 UTC |
| Columns | `ts`, `raw_symbol` (e.g. `CLZ6`), `open`, `high`, `low`, `close`, `volume`, `vendor` |

### Updating the data

API keys live in `.env` (copy `.env.example` and fill it in; `.env` is never committed).

```bash
.venv/bin/python -m tvtester.update                  # Databento: prints the cost quote and asks before downloading
.venv/bin/python -m tvtester.update --yes            # Databento without the question
.venv/bin/python -m tvtester.update --source massive # Massive: fills the most recent days
```

- **Databento** is the main source. It costs a small amount per download, so the updater always shows the
  price first. When Databento covers days that were filled from Massive, it replaces those bars.
- **Massive** has the most recent minutes. It has no continuous contract, so the updater rebuilds the front
  month with the same volume rule.
- Every update checks that prices sit on the $0.01 tick, that low ≤ open/close ≤ high, and that no bar time
  repeats, then records itself in `data/manifest.json`.
- Only CL contracts can be downloaded. Any other symbol (including MCL) is refused.

---

## Testing a strategy

```bash
.venv/bin/python -m tvtester.cli test <strategy> [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--variants a b] [--jobs N]
```

What the command does, step by step:

1. Loads the bars for the period.
2. For each **variant** (for example each session), runs **every combination** in the strategy's grid with
   0 ticks of slippage.
3. Selects **13 separate metric winners**: net profit, win rate, expectancy, profit factor, payoff ratio,
   estimated risk of ruin, maximum drawdown, consecutive losses, Sharpe, Sortino, R-multiple, MAE and MFE.
   Each needs at least 30 closed trades by default. Undefined values are excluded. Drawdown, loss streak,
   estimated ruin and MAE are minimized; other objectives are maximized. Ties: net profit, profit factor, grid order.
4. Writes the winning baseline run. No additional slippage scenarios are run.
5. Writes the document, the equity chart, the CSV files and a JSON summary.

To preserve the historical reports while generating the new multi-metric results for the web:

```bash
.venv/bin/python -m tvtester.cli test tupa_trade --output-tag metrics --jobs 1
# Also supported: --min-trades 30 --ruin-loss 25000
cd web
npm run export
```

The new selections go to `results/<strategy>/metrics/<variant>/metric_winners.json`; distinct winners have
their own saved trade lists and summaries. The web shows a metric selector and all-winners comparison.
Risk of ruin is a labelled model estimate with a declared loss threshold, not a forecast. R-multiple uses
initial stop risk at the actual fill; R spread and consistency are included. MAE/MFE rank the average of the
per-trade maxima. Full definitions and limitations: [engine rules](docs/ENGINE.md#feature-1-thirteen-separate-metric-winners).

---

## Optimizing a strategy (feature 2)

Filters and parameter search, on the **development interval only** (bars before 2024-01-01 UTC). Full protocol
and feature definitions: [`docs/OPTIMIZE.md`](docs/OPTIMIZE.md).

```bash
.venv/bin/python -m tvtester.cli features fair_price_reversal --variant ny       # which features go with good / bad trades
.venv/bin/python -m tvtester.cli search fair_price_reversal --variant ny --space filters \
    --sampler random --trials 200 --objective net0 --seed 1 --jobs 1              # search filters (and parameters: --space full)
.venv/bin/python -m tvtester.cli replay strategies/configs/<file>.json            # replay a new limit-entry winner, baseline only
```

- A **filter** vetoes an entry at the signal bar (`risk_ticks >= 34`, ...). It never changes the signal logic.
- The **objective** is declared before the search (`net0` = baseline net profit plus open P&L) and a winner
  needs at least 300 trades.
- Every run is appended to `results/<name>/ledger.jsonl`, so later validation knows how many tries a result
  took. Every number is in-sample: feature 2 cannot show a tradable edge, only candidates for validation.
- 2024-01-01 onward was already used by feature 1, so it is "reserved", not clean out-of-sample data.

---

## Validating a candidate (feature 3)

Feature 3 asks whether a feature-2 result survives its own selection, on the development interval only (bars
before 2024-01-01; nothing reserved is read). Protocol and verdict rules: [`docs/VALIDATE.md`](docs/VALIDATE.md).

```bash
.venv/bin/python -m tvtester.cli validate strategies/configs/<candidate>.json --jobs 1
```

| Check | Question | Pass |
|---|---|---|
| Walk-forward re-selection | Each year, pick the best of the same 200 E2 configurations on the years before, then trade it for that year. Would that have made money? | baseline sum > 0, 7+ of 10 years positive |
| CSCV / PBO | How often does the best configuration of one half of the data land in the bottom half of the other? | PBO <= 0.5 |
| Deflated Sharpe | Is the candidate's Sharpe higher than the best of 200 tries would show by luck? | DSR >= 0.95 |

A candidate goes on to feature 4 (Topstep 50K prop layer) only if both the procedure and the candidate pass. Feature
5 is the one check on the reserved 2024+ data. Roadmap renumbered by the owner on 2026-11-01.

**Current result (4 November 2026): none of the three random-filter candidates advances.**
All use fixed owner swings, limit entries, commission and no added slippage.

| Candidate | Walk-forward net | Positive years | PBO | DSR | Advance |
|---|---|---|---|---|---|
| Fair Price Reversal NY | +39,463.24 USD | 7 of 10 | 0.0107 | 0.7591 | no |
| Fair Price Reversal London | −1,045.58 USD | 6 of 10 | 0.1663 | 0.4732 | no |
| Fair Price Reversal Asia | −2,967.60 USD | 5 of 10 | 0.7724 | 0.0848 | no |

## Reading a results document

Each document follows the TradingView layout, top to bottom:

| Section | What it tells you |
|---|---|
| Test settings | The exact properties and data range used |
| How the top combination was chosen | The full grid and the ranking rule |
| Summary | One line per variant: parameters and net profit after commission |
| Overview | The headline numbers TradingView shows above its equity chart |
| Performance | Net profit, gross profit and loss, commission paid, buy & hold, max run-up and drawdown, open P&L |
| Trades analysis | Trade counts, win rate, average and largest trades, average bars in trades |
| Risk/performance ratios | Sharpe, Sortino, profit factor, margin calls |
| List of trades | The last 10 trades in TradingView's two-row format (full list in the CSV) |
| By year, exit reasons | Extras that TradingView does not show |
| Top 10 combinations | How the best combination compares with the next ones |

> **Important.** The top combination is the best of many tries on the same data. That makes it look better
> than what the rules can be expected to earn in the future. Read it as an upper bound. A strategy whose top
> combination loses money, or whose profit disappears at 1 tick of slippage, has no edge worth trading.

---

## Adding a new strategy

Every new strategy must use `tvtester.swings` for swing points and preserve the exact rules of
`indicators/structure_swings.pine`. Swing strength, tie rules, confirmation, alternation, replacement and
outside-candle ordering are fixed. Do not add a swing search axis or an alternative pivot helper.

1. Create `strategies/my_strategy.py`:

```python
import numpy as np
from tvtester.engine import LONG, SHORT
from tvtester.strategy import Strategy

class MyStrategy(Strategy):
    name = "my_strategy"

    def __init__(self, length=20, session="ny"):
        super().__init__(length=length, session=session)

    def prepare(self, bars):
        # compute every indicator over ALL bars here (prices are in ticks: bars.o, bars.h, bars.l, bars.c)
        self.signal = ...                    # e.g. +1 / -1 / 0 per bar
        return self.signal != 0              # bars where on_bar must run while flat

    def on_bar(self, ctx, i):                # runs at the close of bar i
        if ctx.position_size == 0 and self.signal[i] == 1:
            ctx.entry("Long", LONG)                          # market: fills at the next open
            ctx.exit("Exit", "Long", stop=..., limit=...)    # or profit=/loss= in ticks from the fill

STRATEGY = MyStrategy
TITLE = "My strategy"
ABOUT = "What the strategy does, in plain words."
GRID = {"length": [10, 20, 50]}
VARIANTS = {"ny": {"session": "ny"}}
```

2. Write the Pine twin `strategies/my_strategy.pine` with the same `strategy()` properties
   (copy the header of `strategies/fair_price_reversal.pine`).
3. Add a test, then run `.venv/bin/python -m tvtester.cli test my_strategy`.

Orders available inside `on_bar` (same meaning as in Pine):

| Call | Pine equivalent |
|---|---|
| `ctx.entry(id, LONG or SHORT, stop=None, limit=None, oca=None)` | `strategy.entry` |
| `ctx.exit(id, from_entry, stop=, limit=, profit=, loss=)` | `strategy.exit` (`profit` / `loss` in ticks) |
| `ctx.close_all(comment, immediately=False)` | `strategy.close_all` |
| `ctx.cancel(id)`, `ctx.cancel_all()` | `strategy.cancel`, `strategy.cancel_all` |
| `ctx.position_size`, `ctx.position_avg_price` | `strategy.position_size`, `strategy.position_avg_price` |

---

## Strategies tested so far

Current runs use only `indicators/structure_swings.pine`, limit entries, $2.01 commission per order,
and no added slippage. History: 2010-06-07 through 2026-11-03, 5,674,164 CL one-minute bars.
F1 selects a separate winner for each of 13 metrics; the net-profit references are below.

| Strategy / session | Grid settings | Best net profit | Trades | Profit factor |
|---|---|---|---|---|
| Fair Price Reversal / Asia | 64 | −6,418.68 USD | 1,634 | 0.9483 |
| Fair Price Reversal / London | 64 | +11,712.66 USD | 1,967 | 1.0711 |
| Fair Price Reversal / New York | 64 | +60,180.72 USD | 4,664 | 1.0859 |
| Tupa Trade / New York | 4 | −13,547.10 USD | 855 | 0.8244 |

These are in-sample selections on the same data. Swing detection was fixed and never searched.

Reports: [Fair Price Reversal](docs/strategies/fair_price_reversal/README.md),
[Tupa Trade](docs/strategies/tupa_trade/results.md). Current search, validation and exit-study summaries
are indexed in [the owner-swing results summary](docs/OWNER_SWING_RESULTS.md).
Older reports remain historical records and do not establish performance under the current rules.

---

## How close is it to TradingView?

The fill rules and the report numbers follow TradingView's documentation (details in
[`docs/ENGINE.md`](docs/ENGINE.md)). Three things can still make a TradingView run differ slightly:

| Difference | Effect |
|---|---|
| **Price data.** TradingView uses its own CL1! feed. This repo uses Databento and Massive bars | A handful of bars can differ by a tick, which can change a few signals |
| **Roll dates.** TradingView switches CL1! by volume with its own rule. This repo uses the previous day's volume | Around some rolls, the two can be on different contracts for about a day. On 2020-04-20 (the day CL went negative), the data here is on the June contract, while TradingView showed May |
| **Roll exit.** This repo closes positions at a contract's last bar, as the owner chose. TradingView would hold through the roll | None for intraday session strategies, which are always flat at 00:00 UTC when the switch happens |

**How to check parity yourself:** open `NYMEX:CL1!` on a 1-minute chart in TradingView, add the Pine twin from
`strategies/`, set its inputs to the top combination from the results document, turn on Deep Backtesting for
the same date range, and compare the List of trades with `results/<name>/<variant>/trades_slippage0.csv`.

---

## Quality checks

| Check | Where |
|---|---|
| Engine rules: next-open fills, intrabar path, gaps, triggered stops, brackets from the fill, same-bar exits, slippage, negative prices, roll exit, reversals | `tests/test_engine.py` |
| Pine port: the fast Python port gives the same signals as a literal bar-by-bar translation of the Pine script, for all three sessions, across daylight-saving change weeks | `tests/test_fair_price_reversal.py` |
| Feature 2: features match a literal Pine-style transcription; features and signals are causal (prefix and future-change tests); no filters = feature 1 trade for trade; vetoed signals never trade; search draws, neighbours and ranking | `tests/test_features.py` |
| Independent review | Codex reviewed the plan and the code, and recomputed the headline numbers with its own code (see the strategy documents) |

---

## FAQ

**Why 1 contract and not a % of equity?** It matches a fixed-size futures account and keeps every trade's
dollar result comparable over 16 years.

**Why is commission $2.01 and not $4.02?** TradingView charges commission on every order. $2.01 on the entry
plus $2.01 on the exit is $4.02 per round trip.

**Can I change the settings?** Yes, in `tvtester/config.py`. Every document records the settings it used.

**Does it support other markets?** No, by design. The repo is for CL only. MCL and other markets are refused.
