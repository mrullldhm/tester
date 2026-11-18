# Ghost Box premise study: does the overnight box hold after a ghost wick?

2026-11-18. Code: `run.py` (definitions in its docstring; box and wick from `strategies/ghost_box.py`). Per-day
rows: `days.csv`. Dev only (2010-06..2021), in-sample, best of 1, no tuning, no P&L (no options prices).
CL mapping: box 17:00-07:59 CT, wick on 5m from 08:00 CT, window 08:30-09:00 CT, expiry analog 13:30 CT.

## Box survival from the start bar to 13:29 CT

| Group | Days | 5m close never outside | 13:29 close inside | never traded outside |
|---|---|---|---|---|
| ghost wick, PDF filters (the trade set) | 211 | 8.1% | 37.9% | 3.8% |
| ghost wick, width only (no gap filter) | 617 | 14.6% | 45.5% | 7.0% |
| ghost wick, gap >= 0.5% (filtered out) | 406 | 18.0% | 49.5% | 8.6% |
| intact box at 08:30, PDF filters, any wick | 696 | 14.2% | 45.3% | 8.6% |
| intact box at 08:30, PDF filters, no wick | 479 | 17.1% | 48.4% | 10.9% |
| intact box at 08:30, no filters, any wick | 1886 | 19.1% | 50.0% | 12.7% |
| no push 08:00-09:00, PDF filters | 384 | 21.4% | 51.0% | 13.5% |

## Reading

- **The premise fails on CL.** After a ghost wick, a 5m candle closes outside the box before 13:30 CT on 92% of
  trade-set days (the PDF's exit fires). Only 38% end inside the box.
- **The wick is a negative signal, not a confirmation.** Wick days hold less often than intact days without a wick
  (8.1% vs 17.1% on the 5m-close measure) and than days with no push at all (21.4%). A failed first push marks a
  wall price is already testing; it does not make the wall real.
- **The gap filter hurts.** Wick days with gap ≥ 0.5% hold more often (18.0%) than the ones the PDF keeps (8.1%).
  CL's 0.5% is SPX-calibrated; CL keeps only 36% of days.
- The width filter does nothing on CL: 99.9% of dev days have an overnight box ≥ 0.4% (median 1.55%).
- Every year 2010-2021: trade set below or equal to the intact-box baseline on the 5m-close measure except 2020-21
  (6 and 10 days). Wednesday (EIA 09:30 CT) is the worst weekday on end-inside (27%).
- Bias check: setup days start at their signal bar (up to 29 min after 08:29), baseline days at 08:29. The shorter
  window favours the setups, and they still hold less often.
- Days with a roll before 13:29 CT are skipped (unadjusted prices).
- Not checked: news calendar (CPI/FOMC/NFP) and VIX/OVX (no data in the repo).
