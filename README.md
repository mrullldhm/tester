# TradingView Strategy Tester for CL1!

A Python backtester that behaves like the **TradingView Strategy Tester** for one market only: **CL1!**, the
front-month NYMEX Light Sweet Crude Oil (WTI) future, on **1-minute bars**. For every strategy it tests,
it writes a results document laid out like TradingView's report: Overview, Performance, Trades analysis,
Risk/performance ratios and List of trades. It also gives the same numbers again under slippage.

> **In one sentence:** you write a strategy once in Python (plus a Pine twin for TradingView), run one command,
> and get a TradingView-style report for the best parameter combination at 0, 1 and 2 ticks of slippage.

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
| Parameter grid | Runs every combination, ranks them by net profit, documents the top combination |
| Slippage scenarios | The top combination again at 1 tick and 2 ticks of slippage, in separate tables |
| Sessions | Asia, London and New York sessions for CL, verified against real CL volume, each in its own time zone (daylight saving handled) |
| Data updater | Adds new 1-minute bars from Databento (primary) or Massive (fallback) with one command |
| Pine twins | Every strategy has a Pine v6 version so you can check the trades on TradingView itself |

---

## Quick start

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

# big grids: split each variant's grid over 8 processes (same ranked grid as serial; about 1 GB RAM per process)
.venv/bin/python -m tvtester.cli test supertrend_kalman --jobs 8 --chunks 8
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
| Slippage | **0 ticks** in the main result. **1 tick and 2 ticks** shown separately |
| Pyramiding | 0 (one position at a time) |
| Margin | not checked |
| Limit orders | fill when price touches them |
| Bar Magnifier | off |
| Roll rule | a position open on the last bar of a contract is closed at that bar's close |

**What slippage means here.** As in TradingView, slippage makes every market order and stop order fill N ticks
worse than its price. Limit orders (for example a profit target) never slip. One tick of slippage on CL costs
$10 per affected fill, so a trade that enters at market and exits on its stop loses $20 more at 1 tick and
$40 more at 2 ticks.

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
 tvtester/optimize.py  ──► every grid combination → rank by net profit → re-run winner at 1 and 2 ticks
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
| `docs/strategies/<name>/README.md` | Results document per strategy |
| `docs/OPTIMIZE.md` | Feature 2 protocol and feature contracts |
| `docs/strategies/<name>/experiments.md`, `features_<variant>.md`, `optimized/` | Feature-2 lab notebook, association reports, replayed winners |
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
3. Picks the **top combination**: the highest net profit. Ties go to the higher profit factor, then grid order.
4. Runs that same combination again at **1 tick** and **2 ticks** of slippage. It never re-optimizes for slippage.
5. Writes the document, the equity chart, the CSV files and a JSON summary.

---

## Optimizing a strategy (feature 2)

Filters and parameter search, on the **development interval only** (bars before 2024-01-01 UTC). Full protocol
and feature definitions: [`docs/OPTIMIZE.md`](docs/OPTIMIZE.md).

```bash
.venv/bin/python -m tvtester.cli features fair_price_reversal --variant ny       # which features go with good / bad trades
.venv/bin/python -m tvtester.cli search fair_price_reversal --variant ny --space filters \
    --sampler random --trials 200 --objective net1 --seed 1 --jobs 4              # search filters (and parameters: --space full)
.venv/bin/python -m tvtester.cli replay strategies/configs/<file>.json            # re-run a frozen winner at 0 / 1 / 2 ticks
```

- A **filter** vetoes an entry at the signal bar (`risk_ticks >= 34`, ...). It never changes the signal logic.
- The **objective** is declared before the search (`net0` or `net1` = net profit at 0 or 1 tick) and a winner
  needs at least 300 trades.
- Every run is appended to `results/<name>/ledger.jsonl`, so later validation knows how many tries a result
  took. Every number is in-sample: feature 2 cannot show a tradable edge, only candidates for validation.
- 2024-01-01 onward was already used by feature 1, so it is "reserved", not clean out-of-sample data.

---

## Reading a results document

Each document follows the TradingView layout, top to bottom:

| Section | What it tells you |
|---|---|
| Test settings | The exact properties and data range used |
| How the top combination was chosen | The full grid and the ranking rule |
| Summary | One line per variant: parameters and net profit at 0 / 1 / 2 ticks |
| Overview | The headline numbers TradingView shows above its equity chart |
| Performance | Net profit, gross profit and loss, commission paid, buy & hold, max run-up and drawdown, open P&L |
| Trades analysis | Trade counts, win rate, average and largest trades, average bars in trades |
| Risk/performance ratios | Sharpe, Sortino, profit factor, margin calls |
| List of trades | The last 10 trades in TradingView's two-row format (full list in the CSV) |
| By year, exit reasons | Extras that TradingView does not show |
| Slippage scenarios | Side-by-side table, then a full report for each slippage level |
| Top 10 combinations | How the best combination compares with the next ones |

> **Important.** The top combination is the best of many tries on the same data. That makes it look better
> than what the rules can be expected to earn in the future. Read it as an upper bound. A strategy whose top
> combination loses money, or whose profit disappears at 1 tick of slippage, has no edge worth trading.

---

## Adding a new strategy

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

### Fair Price Reversal (LuxAlgo 9:29 ET), three CL sessions

Full report: [`docs/strategies/fair_price_reversal/README.md`](docs/strategies/fair_price_reversal/README.md).
Period: 2010-06-07 to 2026-10-27. Top combination of 192 per session, ranked by net profit at 0 ticks.

| Session | Top combination | Net profit, 0 ticks | 1 tick | 2 ticks | Trades | Profit factor | Max drawdown |
|---|---|---|---|---|---|---|---|
| Asia (09:00 UTC+8) | window 30, ATR x2.0, swing 3, target 1R | +1,182.96 USD | −5,657.04 USD | −14,087.04 USD | 452 | 1.031 | 5,704.86 USD |
| London (08:00 London) | window 120, ATR x2.0, swing 3, target 2R | +34,591.64 USD | −33,338.16 USD | −101,643.94 USD | 3,818 | 1.072 | 13,213.46 USD |
| New York (09:00 NY) | window 120, ATR x0.5, swing 3, target 2R | +42,475.80 USD | −20,100.08 USD | −81,394.00 USD | 3,710 | 1.056 | 20,110.90 USD |

**Verdict: no tradable edge.** Even the best combination of each session makes only a few dollars per trade
before slippage (New York: $11.45 per trade). One tick of slippage costs up to $20 per trade, so every session
loses money at 1 tick. Only 3 (Asia), 91 (London) and 19 (New York) of the 192 combinations were profitable
even at 0 ticks, and those are in-sample.

**Independent check:** Codex rebuilt the New York result with its own code (no shared code) from the raw
parquet files: 3,710 trades and +42,475.80 USD at 0 ticks, 3,704 trades and −20,100.08 USD at 1 tick. Every
trade matched on side, times, prices, profit and exit reason ([`docs/REVIEWS.md`](docs/REVIEWS.md)).

**Feature 2 (optimize), development interval 2010-06 to 2023-12, in-sample:** lab notebook
[`docs/strategies/fair_price_reversal/experiments.md`](docs/strategies/fair_price_reversal/experiments.md).

| Session | Candidate | Net 0 / 1 / 2 ticks | Trades | Baseline at 1 tick |
|---|---|---|---|---|
| New York | baseline + `anchor_body_atr >= 0.3`, `risk_ticks >= 32` | +63,293 / +49,297 / +34,592 USD | 927 | +2,423 USD |
| London | baseline + `risk_ticks >= 30` | +39,017 / +32,197 / +23,121 USD | 436 | -13,754 USD |
| Asia | none (no eligible trial made money at 1 tick) | | | -4,085 USD |

A minimum stop size (a hypothesis declared before the search: costs are a large share of a small R) is what the
searches found, with stable neighbours. Picked from 1,500 trials; profits lean on volatile years (London 2022 is
58% of its total). Codex replicated the New York candidate trade for trade. Not a tradable edge until it passes
out-of-sample validation (feature 3).

### Supertrend + ATR trail + Kalman trend + volatility filter, M15 signals

Full report: [`docs/strategies/supertrend_kalman/README.md`](docs/strategies/supertrend_kalman/README.md).
Period: 2010-06-07 to 2026-10-27. Every design fork the owner left open (entry trigger, volatility filter, exit,
trading hours) was tested: top combination of 1,728 per variant, ranked by net profit at 0 ticks.

| Variant | Top combination | Net profit, 0 ticks | 1 tick | 2 ticks | Trades | Max drawdown |
|---|---|---|---|---|---|---|
| all (24 h) | both, atr_ratio 1.3, fixed, 3R, swing 3, ST 3, Kalman q 0.0001 | +128,886.58 USD | +42,086.78 USD | −37,224.68 USD | 4,471 | 51,168.74 USD |
| Asia | trail, no filter, trail exit, 3R, swing 3, ST 3, q 0.01 | +18,111.68 USD | −5,888.32 USD | −29,888.32 USD | 1,216 | 7,818.28 USD |
| London | both, stop_atr 3, trail exit, 2R, swing 5, ST 3, q 0.0001 | +16,241.58 USD | +2,481.58 USD | −11,618.42 USD | 721 | 8,685.46 USD |
| New York | both, rvi, flip exit, 3R, swing 5, ST 2, q 0.0001 | +84,714.24 USD | +22,574.24 USD | −39,555.76 USD | 3,188 | 24,275.52 USD |

**Verdict: no tradable edge.** Every top combination loses at 2 ticks; best of 1,728 in-sample. The 24-hour top
has a drawdown larger than the account (102%) and its ten best trades make 79% of its profit. Codex replicated
the 24-hour top trade for trade (0.00 USD difference at 0 and 1 tick).

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
