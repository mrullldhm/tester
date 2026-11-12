# Data: CL1! 1-minute bars

| Item | Value |
|---|---|
| Market | CL, NYMEX Light Sweet Crude, front month. **MCL banned**; `assert_cl` refuses any other root |
| Source | Databento GLBX.MDP3 `ohlcv-1m`, continuous `CL.v.0` (primary); Massive REST outrights (fallback) |
| Range | 2010-06-07 to latest (`python -m cltester.cli info`) |
| Storage | `data/cl1/year=YYYY.parquet`; `data/manifest.json` holds range, row counts, hashes, update log |
| Columns | `ts` (bar open, UTC), `raw_symbol`, `open`, `high`, `low`, `close` ($), `volume`, `vendor` |
| Front month | contract with the highest previous-UTC-day volume, switching at 00:00 UTC (Databento rule; Massive rebuilt the same way) |
| Adjustment | none: prices are the traded contract's. A `raw_symbol` change is a price jump; the engine exits before it |
| Licence | paid Databento data: not committed (`.gitignore`), not shared |

## Session fields (`cltester.data.add_session`)

- `ct`: bar open in America/Chicago.
- `trading_day`: CME/Topstep day. Bars from 17:00 CT belong to the next day (Sunday evening = Monday).
- `sess_minute`: minutes since the 17:00 CT open (0..1379); 3:10 PM CT = 1330.
- Minutes with no trades have no bar. Holidays close early, so a day can end before 3:10 PM CT.

## Updating

```bash
.venv/bin/python -m cltester.cli update            # Databento: prints the quoted cost, asks before download
.venv/bin/python -m cltester.cli update --source massive
```

Databento costs money: show the owner the quote and get a yes before `--yes`. Only one update runs at a time
(`data/.update.lock`), and files are written to a temp name then renamed, so a crash never leaves half a file.
A Databento update replaces any Massive bars it now covers. Every update is checked: on the $0.01 tick, low ≤ open/close ≤ high, unique times, CL only.

## Known facts

- Front-month-by-volume avoided the 2020-04-20 negative CLK0 print (lowest stored low in 2020: $6.50).
- Databento flagged 2026-11-01 and 2026-11-08 as degraded days (Sundays, little or no trading).
