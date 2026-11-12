# tradingview-tester

Research repo for one question: **is there an intraday CL (crude oil) strategy that passes the Topstep 50K Trading
Combine consistently?** CL only: MCL is banned (non-syariah for the owner).

Like a flight simulator for the Combine: replay 16 years of 1-minute CL bars, place the strategy's limit orders under
strict fill rules, then run every possible Combine attempt through Topstep's loss limits and consistency rule.

## Pipeline

```
data/cl1 (Databento CL.v.0 1m)
   │  cltester.data      load bars, add Chicago session fields (trading day, minutes since 17:00 CT)
   ▼
strategies/<name>.py     signals(): one limit bracket order per signal bar
   │  cltester.engine    limit fills on touch, stop/target/flatten 3:10 PM CT/roll exits, fees, MAE
   ▼
trades
   │  cltester.metrics   net, PF, drawdown, years positive
   │  cltester.topstep   50K Combine: EOD-trailing MLL on intraday equity, optional DLL, 55% consistency
   ▼
results/ledger.csv       one row per run, never deleted
```

## Layout

| Path | What |
|---|---|
| `cltester/` | the toolkit: `config` (contract, costs, Topstep rules, periods), `data`, `update`, `engine`, `topstep`, `metrics`, `strategy`, `cli` |
| `strategies/` | one file per strategy; `template.py` is a plumbing check only |
| `docs/` | `PROTOCOL.md` (how research is done), `TOPSTEP.md` (rules + what to verify), `ENGINE.md` (fill rules), `DATA.md` |
| `docs/strategies/<name>/` | hypothesis and results per strategy (`TEMPLATE.md`) |
| `tests/` | one test per fill rule and Combine rule |
| `data/` | paid bars, local only |
| `web/` | front end (own repo) |

## Use

```bash
.venv/bin/python -m cltester.cli info                       # data range, periods
.venv/bin/python -m cltester.cli update                     # Databento: shows cost, asks first
.venv/bin/python -m cltester.cli test <name> --period dev   # backtest + Combine simulation, logs to ledger
.venv/bin/python -m pytest -q && .venv/bin/ruff check .
```

New strategy: write `docs/strategies/<name>/README.md` from the template first (hypothesis, rules, trial budget),
then `strategies/<name>.py` (see `cltester/strategy.py` for the contract).

## Fixed assumptions

- 1 CL contract unless the strategy sizes up (max 5). Tick $0.01 = $10.
- Fee $4.04 per contract round turn. Entries are limit orders; a touch fills; exits have no slippage.
- Topstep numbers are from 2026 third-party guides; see the VERIFY list in `docs/TOPSTEP.md`.
