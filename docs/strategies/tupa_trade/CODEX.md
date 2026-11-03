# Tupa Trade: steps for the owner and the Codex review request

Claude wrote the code in a cloud session that has no bar data and no Codex. These steps run on the owner's machine.

## 1. Owner: tests with data, then the feature-1 test

```bash
.venv/bin/python -m pytest -q 2>&1 | tee logs/pytest_tupa.log
```

```bash
sha256sum logs/pytest_tupa.log
```

`tests/test_tupa_trade.py::test_owner_trade_26_oct_2026` must pass: it checks that the code reproduces the 26 Oct
2026 short (sell stop-limit 100.76 / 100.77, fill 22:32 MYT, TP 100.52 at 22:33, +245.98 USD). If it fails, stop
and send the failure to Claude before running the grid.

```bash
.venv/bin/python -m tvtester.cli test tupa_trade --jobs 4
```

This writes `docs/strategies/tupa_trade/results.md` (README.md stays the spec), PNGs and `results/tupa_trade/`.

## 2. Codex: review request (paste into Codex)

Read `AGENTS.md`, `docs/ENGINE.md` (fills rule 8, stop-limit entries) and `docs/strategies/tupa_trade/README.md`
(sections 3b, 3c, 3d). Review, most severe first:

1. `tvtester/engine.py` stop-limit entries: trigger then limit along the bar path, gaps at the open, limit = stop,
   same-bar exits after the fill. Compare with TradingView's broker emulator.
2. `tvtester/swings.py` against `indicators/structure_swings.pine`: pivot rule, alternation, outside-candle order,
   higher-timeframe candle boundaries (4H from 18:00 New York, CME day, DST, missing last minute), closed-candle
   timing (no look-ahead), trend touches.
3. `strategies/tupa_trade.py` vs `strategies/tupa_trade.pine` (and `tests/tupa_literal.py`): same bias, setup, order
   amend / cancel, one trade per session, session end.
4. Replicate with your own code from `data/cl1/year=YYYY.parquet` (no `tvtester` / `strategies` imports): the 26 Oct
   2026 trade, then the top combination in `results.md` (trades, net profit at 0 / 1 / 2 ticks).

The pytest log and its SHA-256 are in `logs/pytest_tupa.log` (hash above). Do not run pytest unless asked.
