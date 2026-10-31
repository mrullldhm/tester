# tradingview-tester: rules for Claude

- **CL only. MCL is banned** (non-syariah for the owner). `tvtester.update.assert_cl` guards every download.
- Goal: results identical to the TradingView Strategy Tester on CL1! 1m. Every engine rule is in `docs/ENGINE.md`;
  change the doc with the code. Owner rules that differ from TV (roll exit) stay labelled as such.
- Fixed properties: $50,000, 1 contract, $2.01 per order ($4.02 round trip), slippage 0 + separate 1 and 2 tick
  scenarios. Never call slippage "commission".
- Every strategy: Python class in `strategies/<name>.py` (with GRID / VARIANTS / TITLE / ABOUT), a runnable Pine v6
  twin `strategies/<name>.pine`, and a results doc from `python -m tvtester.cli test <name>`. Docs show the top
  combination only (highest net profit at 0 ticks) with its slippage scenarios, and say it is in-sample.
- Indicators are computed over every bar in `prepare`; `on_bar` may be skipped on idle bars.
- Codex reviews and replicates (`AGENTS.md`) before a result is called real. Give it a hashed pytest log.
- Databento downloads cost money: always show the quote and ask the owner first.
- Feature 2 (optimize, `docs/OPTIMIZE.md`): development interval only (before 2024-01-01; 2024+ is reserved, not
  clean OOS). Declare hypothesis, objective and trial budget in `experiments.md` before running; every run goes to the
  ledger; every optimized number says in-sample and best of N.
