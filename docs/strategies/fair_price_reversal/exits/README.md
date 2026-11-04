# Fair Price Reversal (LuxAlgo 9:29 ET), CL1! sessions: exit study (breakeven, trailing stop, time exit)

Generated 2026-11-04 15:05 UTC by `python -m tvtester.cli exits fair_price_reversal`.

> **Read this first.** Exploratory **in-sample** exit sweep. Each variant's feature-1 top combination is frozen and only the exit rule changes. The best rule is the **best of 396** tries per variant (each family below says its own N), conditional on baselines that were themselves the best of the feature-1 grid, and after an earlier 330-rule version of this study (ledger). The interval is the full feature-1 interval, **including the reserved 2024+ bars**, so these exit winners cannot be validated on 2024+. Only the baseline is run, with commission and no added slippage.

## Settings

| Setting | Value |
|---|---|
| Data | 2010-06-07 00:00:00+00:00 to 2026-11-03 18:29:00+00:00 UTC, 5,674,164 bars (data hash `c4a4027e32165aa7`, code hash `02728c7b4adfd555`, grid hash `7d5efca0fc057cd2`) |
| Properties | as feature 1: $50,000, 1 contract, $2.01 per order ($4.02 round trip), no added slippage |
| Objective (declared first) | net0 (net profit + open P&L at the end, 0 ticks); ties: profit factor, then rule order |
| Baseline | the variant's feature-1 top combination, unchanged (entries, initial stop and target) |
| Run | `20261104T145109Z_7d5efc` (ledger `results/fair_price_reversal/ledger.jsonl`; files never overwritten) |

## Exit rules

Units: **T** = the trade's target distance in ticks (rr x signal risk). All rules run at every 1-minute bar close while in a position; a moved stop works from the next bar, a time exit fills at the next open. **best** = most favourable high (long) / low (short) since the entry bar. A stop never loosens. Trailing rules come with the target kept or removed, and most start either at once or after 0.5T. Full rules: `docs/ENGINE.md` (Exit management) and `tvtester/exits.py`.

| Family | Rule | Rules |
|---|---|---|
| `be_touch` | Breakeven when the high / low reaches be_x x T | 9 |
| `be_close` | Breakeven when a close reaches be_x x T | 6 |
| `be_time` | Breakeven after N bars if the close is in profit | 6 |
| `trail_frac` | Trail a fixed fraction of T behind the best price | 32 |
| `trail_atr` | Trail k x ATR(14) behind the best price (chandelier) | 16 |
| `trail_swing` | Trail at the last confirmed owner 1m swing low / high (fixed detection; TradingView export pending) | 4 |
| `trail_step` | Ratchet: lock one step behind every step of T reached | 4 |
| `trail_close` | Trail a fraction of T behind the best close | 16 |
| `trail_ema` | Trail at the 1m EMA while it is on the trade's side | 12 |
| `trail_sar` | Trail at the 1m Parabolic SAR while it is on the trade's side (UNVERIFIED SAR) | 8 |
| `both` | Every trailing rule with one of 3 declared breakevens: touch 0.5T +1t, close 0.5T +1t, time 30 bars +1t | 276 |
| `time_exit` | Close at market after N bars in the trade | 6 |
| | **Total (with the baseline)** | **396** |

Every rule that trails with `swing` or `sar` (their own families and the matching `both` rules, marked **(unverified)** below) uses the owner swing twin / Pine `ta.sar` that have **not been checked against a TradingView export** yet.

Breakeven is a stop price, not a guaranteed result: a gap can fill worse, and the round trip still costs $4.02 (1 tick offset = $10).

## Summary: best rule per variant

| Variant | Baseline net | Best rule (of 396) | Family | Best net | Rules beating the baseline |
|---|---|---|---|---|---|
| asia | -6,418.68 USD | BE after 60 bars +1t | be_time | -2,258.68 USD | 14 of 395 |
| london | 11,712.66 USD | none | baseline | 11,712.66 USD | 0 of 395 |
| ny | 60,180.72 USD | none | baseline | 60,180.72 USD | 0 of 395 |

## Variant: asia

**Frozen baseline:** `session=asia`, `window=30`, `atr_mult=2.0`, `swing=1`, `target=rr2`

![Closed-trade equity: baseline vs best rule](equity_asia.png)

Chart: closed trades only (an open position at the end is in the Open P&L column).

Files: [grid](../../../../results/fair_price_reversal/exits/20261104T145109Z_7d5efc/asia/grid.csv), [summary](../../../../results/fair_price_reversal/exits/20261104T145109Z_7d5efc/asia/summary.json), best rule trades [0 ticks](../../../../results/fair_price_reversal/exits/20261104T145109Z_7d5efc/asia/best_trades_slippage0.csv)

### Best rule of each family

| Family | Best rule | Best of | Net profit | Open P&L at the end | Trades | % profitable | PF | Avg trade | Max DD | Trades with stop moved / closed by time exit | Family rules beating the baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | none | 1 | -6,418.68 USD | 0.00 USD | 1,634 | 32.50% | 0.948 | -3.93 USD | 11,406.78 USD | 0 / 0 |  |
| be_touch | BE touch 0.75T +1t | 9 | -5,458.68 USD | 0.00 USD | 1,634 | 37.76% | 0.953 | -3.34 USD | 10,886.78 USD | 515 / 0 | 3 of 9 |
| be_close | BE close 0.75T +1t | 6 | -6,288.68 USD | 0.00 USD | 1,634 | 35.62% | 0.947 | -3.85 USD | 11,076.78 USD | 425 / 0 | 1 of 6 |
| be_time | BE after 60 bars +1t | 6 | -2,258.68 USD | 0.00 USD | 1,634 | 39.78% | 0.979 | -1.38 USD | 7,790.80 USD | 275 / 0 | 2 of 6 |
| trail_frac | trail 1T | 32 | -4,428.68 USD | 0.00 USD | 1,634 | 30.60% | 0.962 | -2.71 USD | 10,236.78 USD | 668 / 0 | 5 of 32 |
| trail_atr | trail 3 ATR from 0.5T | 16 | -8,602.70 USD | 0.00 USD | 1,635 | 40.06% | 0.914 | -5.26 USD | 10,940.80 USD | 742 / 0 | 0 of 16 |
| trail_swing | trail owner swings (fixed) (unverified) | 4 | -10,184.76 USD | 0.00 USD | 1,638 | 31.26% | 0.821 | -6.22 USD | 11,083.22 USD | 1,447 / 0 | 0 of 4 |
| trail_step | trail step 0.5T | 4 | -8,008.68 USD | 0.00 USD | 1,634 | 24.05% | 0.919 | -4.90 USD | 11,174.82 USD | 750 / 0 | 0 of 4 |
| trail_close | trail close 1T | 16 | -4,698.68 USD | 0.00 USD | 1,634 | 31.33% | 0.961 | -2.88 USD | 9,626.78 USD | 602 / 0 | 2 of 16 |
| trail_ema | trail EMA 50 from 0.5T | 12 | -8,822.70 USD | 0.00 USD | 1,635 | 44.22% | 0.912 | -5.40 USD | 10,239.84 USD | 707 / 0 | 0 of 12 |
| trail_sar | trail SAR 0.01/0.01/0.1 from 0.5T (unverified) | 8 | -8,748.68 USD | 0.00 USD | 1,634 | 36.54% | 0.916 | -5.35 USD | 10,470.80 USD | 645 / 0 | 0 of 8 |
| both | BE close 0.5T +1t; trail 0.75T from 0.5T | 276 | -7,308.68 USD | 0.00 USD | 1,634 | 43.39% | 0.927 | -4.47 USD | 10,422.46 USD | 750 / 0 | 0 of 276 |
| time_exit | time exit 60 bars | 6 | -4,898.68 USD | 0.00 USD | 1,634 | 37.39% | 0.954 | -3.00 USD | 8,030.80 USD | 0 / 308 | 1 of 6 |
| **overall** | BE after 60 bars +1t | 396 | -2,258.68 USD | 0.00 USD | 1,634 | 39.78% | 0.979 | -1.38 USD | 7,790.80 USD | 275 / 0 |  |

### Top 10 of 396 (0 ticks)

| # | Rule | Family | Objective | Trades | % profitable | PF | Max DD |
|---|---|---|---|---|---|---|---|
| 1 | BE after 60 bars +1t | be_time | -2,258.68 USD | 1,634 | 39.78% | 0.979 | 7,790.80 USD |
| 2 | BE after 60 bars +0t | be_time | -3,868.68 USD | 1,634 | 28.27% | 0.964 | 8,395.12 USD |
| 3 | trail 1T | trail_frac | -4,428.68 USD | 1,634 | 30.60% | 0.962 | 10,236.78 USD |
| 4 | trail 1T from 0.25T | trail_frac | -4,428.68 USD | 1,634 | 30.60% | 0.962 | 10,236.78 USD |
| 5 | trail 1T from 0.5T | trail_frac | -4,428.68 USD | 1,634 | 30.60% | 0.962 | 10,236.78 USD |
| 6 | trail close 1T | trail_close | -4,698.68 USD | 1,634 | 31.33% | 0.961 | 9,626.78 USD |
| 7 | trail close 1T from 0.5T | trail_close | -4,698.68 USD | 1,634 | 31.33% | 0.961 | 9,626.78 USD |
| 8 | time exit 60 bars | time_exit | -4,898.68 USD | 1,634 | 37.39% | 0.954 | 8,030.80 USD |
| 9 | trail 1T from 0.75T | trail_frac | -4,998.68 USD | 1,634 | 31.09% | 0.958 | 10,456.78 USD |
| 10 | trail 0.75T from 0.75T | trail_frac | -5,258.68 USD | 1,634 | 35.31% | 0.954 | 10,224.82 USD |

Rules with a positive objective: 0 of 396. Rules beating the baseline: 14 of 395.

## Variant: london

**Frozen baseline:** `session=london`, `window=30`, `atr_mult=1.5`, `swing=1`, `target=rr2`

![Closed-trade equity: baseline vs best rule](equity_london.png)

Chart: closed trades only (an open position at the end is in the Open P&L column).

Files: [grid](../../../../results/fair_price_reversal/exits/20261104T145109Z_7d5efc/london/grid.csv), [summary](../../../../results/fair_price_reversal/exits/20261104T145109Z_7d5efc/london/summary.json), best rule trades [0 ticks](../../../../results/fair_price_reversal/exits/20261104T145109Z_7d5efc/london/best_trades_slippage0.csv)

### Best rule of each family

| Family | Best rule | Best of | Net profit | Open P&L at the end | Trades | % profitable | PF | Avg trade | Max DD | Trades with stop moved / closed by time exit | Family rules beating the baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | none | 1 | 11,712.66 USD | 0.00 USD | 1,967 | 35.18% | 1.071 | 5.95 USD | 7,901.56 USD | 0 / 0 |  |
| be_touch | BE touch 0.75T +1t | 9 | 3,032.66 USD | 0.00 USD | 1,967 | 40.52% | 1.020 | 1.54 USD | 12,371.92 USD | 667 / 0 | 0 of 9 |
| be_close | BE close 0.75T +1t | 6 | 4,442.66 USD | 0.00 USD | 1,967 | 37.72% | 1.028 | 2.26 USD | 11,051.92 USD | 519 / 0 | 0 of 6 |
| be_time | BE after 60 bars +0t | 6 | 6,472.66 USD | 0.00 USD | 1,967 | 32.23% | 1.043 | 3.29 USD | 8,591.56 USD | 192 / 0 | 0 of 6 |
| trail_frac | trail 1T | 32 | 6,282.66 USD | 0.00 USD | 1,967 | 32.03% | 1.041 | 3.19 USD | 11,131.92 USD | 919 / 0 | 0 of 32 |
| trail_atr | trail 4 ATR from 0.5T | 16 | 2,948.64 USD | 0.00 USD | 1,968 | 36.33% | 1.021 | 1.50 USD | 8,319.16 USD | 879 / 0 | 0 of 16 |
| trail_swing | trail owner swings (fixed) from 0.5T (unverified) | 4 | -1,231.56 USD | 0.00 USD | 1,978 | 44.79% | 0.990 | -0.62 USD | 11,045.06 USD | 978 / 0 | 0 of 4 |
| trail_step | trail step 0.5T | 4 | -1,327.34 USD | 0.00 USD | 1,967 | 25.06% | 0.989 | -0.67 USD | 9,821.92 USD | 991 / 0 | 0 of 4 |
| trail_close | trail close 1T | 16 | 6,242.66 USD | 0.00 USD | 1,967 | 33.20% | 1.040 | 3.17 USD | 10,121.92 USD | 790 / 0 | 0 of 16 |
| trail_ema | trail EMA 50 from 0.5T | 12 | 1,698.64 USD | 0.00 USD | 1,968 | 47.26% | 1.013 | 0.86 USD | 7,053.34 USD | 930 / 0 | 0 of 12 |
| trail_sar | trail SAR 0.01/0.01/0.1 from 0.5T (unverified) | 8 | 2,038.64 USD | 0.00 USD | 1,968 | 38.31% | 1.015 | 1.04 USD | 10,249.16 USD | 864 / 0 | 0 of 8 |
| both | BE close 0.5T +1t; trail EMA 50 from 0.5T | 276 | 2,318.64 USD | 0.00 USD | 1,968 | 49.14% | 1.019 | 1.18 USD | 6,978.76 USD | 962 / 0 | 0 of 276 |
| time_exit | time exit 60 bars | 6 | 8,652.66 USD | 0.00 USD | 1,967 | 36.71% | 1.057 | 4.40 USD | 7,061.56 USD | 0 / 212 | 0 of 6 |
| **overall** | none | 396 | 11,712.66 USD | 0.00 USD | 1,967 | 35.18% | 1.071 | 5.95 USD | 7,901.56 USD | 0 / 0 |  |

### Top 10 of 396 (0 ticks)

| # | Rule | Family | Objective | Trades | % profitable | PF | Max DD |
|---|---|---|---|---|---|---|---|
| 1 | none | baseline | 11,712.66 USD | 1,967 | 35.18% | 1.071 | 7,901.56 USD |
| 2 | time exit 60 bars | time_exit | 8,652.66 USD | 1,967 | 36.71% | 1.057 | 7,061.56 USD |
| 3 | BE after 60 bars +0t | be_time | 6,472.66 USD | 1,967 | 32.23% | 1.043 | 8,591.56 USD |
| 4 | trail 1T | trail_frac | 6,282.66 USD | 1,967 | 32.03% | 1.041 | 11,131.92 USD |
| 5 | trail 1T from 0.25T | trail_frac | 6,282.66 USD | 1,967 | 32.03% | 1.041 | 11,131.92 USD |
| 6 | trail 1T from 0.5T | trail_frac | 6,282.66 USD | 1,967 | 32.03% | 1.041 | 11,131.92 USD |
| 7 | trail close 1T | trail_close | 6,242.66 USD | 1,967 | 33.20% | 1.040 | 10,121.92 USD |
| 8 | trail close 1T from 0.5T | trail_close | 6,242.66 USD | 1,967 | 33.20% | 1.040 | 10,121.92 USD |
| 9 | BE after 60 bars +1t | be_time | 6,052.66 USD | 1,967 | 38.54% | 1.040 | 8,341.56 USD |
| 10 | trail 1T from 0.75T | trail_frac | 5,092.66 USD | 1,967 | 32.64% | 1.033 | 11,521.92 USD |

Rules with a positive objective: 45 of 396. Rules beating the baseline: 0 of 395.

## Variant: ny

**Frozen baseline:** `session=ny`, `window=120`, `atr_mult=0.5`, `swing=1`, `target=rr2`

![Closed-trade equity: baseline vs best rule](equity_ny.png)

Chart: closed trades only (an open position at the end is in the Open P&L column).

Files: [grid](../../../../results/fair_price_reversal/exits/20261104T145109Z_7d5efc/ny/grid.csv), [summary](../../../../results/fair_price_reversal/exits/20261104T145109Z_7d5efc/ny/summary.json), best rule trades [0 ticks](../../../../results/fair_price_reversal/exits/20261104T145109Z_7d5efc/ny/best_trades_slippage0.csv)

### Best rule of each family

| Family | Best rule | Best of | Net profit | Open P&L at the end | Trades | % profitable | PF | Avg trade | Max DD | Trades with stop moved / closed by time exit | Family rules beating the baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | none | 1 | 60,180.72 USD | 0.00 USD | 4,664 | 34.69% | 1.086 | 12.90 USD | 24,678.62 USD | 0 / 0 |  |
| be_touch | BE touch 0.75T +0t | 9 | 33,650.62 USD | 0.00 USD | 4,669 | 30.65% | 1.052 | 7.21 USD | 32,486.66 USD | 1,575 / 0 | 0 of 9 |
| be_close | BE close 0.75T +0t | 6 | 46,592.68 USD | 0.00 USD | 4,666 | 32.90% | 1.069 | 9.99 USD | 26,712.64 USD | 1,205 / 0 | 0 of 6 |
| be_time | BE after 60 bars +0t | 6 | 22,518.66 USD | 0.00 USD | 4,667 | 30.30% | 1.036 | 4.83 USD | 28,666.54 USD | 649 / 0 | 0 of 6 |
| trail_frac | trail 1T from 0.75T | 32 | 43,352.68 USD | 0.00 USD | 4,666 | 32.21% | 1.064 | 9.29 USD | 28,148.62 USD | 1,575 / 0 | 0 of 32 |
| trail_atr | trail 4 ATR from 0.5T; no target | 16 | 0.28 USD | 0.00 USD | 4,286 | 34.41% | 1.000 | 0.00 USD | 31,512.84 USD | 1,999 / 0 | 0 of 16 |
| trail_swing | trail owner swings (fixed) from 0.5T (unverified) | 4 | -28,520.52 USD | 0.00 USD | 4,826 | 43.76% | 0.951 | -5.91 USD | 41,702.86 USD | 2,254 / 0 | 0 of 4 |
| trail_step | trail step 0.5T; no target | 4 | 1,514.22 USD | 0.00 USD | 4,489 | 24.62% | 1.003 | 0.34 USD | 30,693.60 USD | 2,205 / 0 | 0 of 4 |
| trail_close | trail close 1T | 16 | 46,436.70 USD | 0.00 USD | 4,665 | 33.10% | 1.068 | 9.95 USD | 23,711.48 USD | 1,878 / 0 | 0 of 16 |
| trail_ema | trail EMA 50 from 0.5T; no target | 12 | 4,730.90 USD | 0.00 USD | 4,455 | 46.96% | 1.009 | 1.06 USD | 27,534.28 USD | 2,132 / 0 | 0 of 12 |
| trail_sar | trail SAR 0.01/0.01/0.1 from 0.5T; no target (unverified) | 8 | -6,904.12 USD | 0.00 USD | 4,506 | 37.26% | 0.988 | -1.53 USD | 36,832.82 USD | 2,162 / 0 | 0 of 8 |
| both | BE close 0.5T +1t; trail close 0.75T from 0.5T; no target | 276 | 14,784.76 USD | 0.00 USD | 4,362 | 44.20% | 1.027 | 3.39 USD | 30,014.44 USD | 2,115 / 0 | 0 of 276 |
| time_exit | time exit 60 bars | 6 | 16,480.22 USD | 0.00 USD | 4,689 | 37.32% | 1.026 | 3.51 USD | 32,228.34 USD | 0 / 733 | 0 of 6 |
| **overall** | none | 396 | 60,180.72 USD | 0.00 USD | 4,664 | 34.69% | 1.086 | 12.90 USD | 24,678.62 USD | 0 / 0 |  |

### Top 10 of 396 (0 ticks)

| # | Rule | Family | Objective | Trades | % profitable | PF | Max DD |
|---|---|---|---|---|---|---|---|
| 1 | none | baseline | 60,180.72 USD | 4,664 | 34.69% | 1.086 | 24,678.62 USD |
| 2 | BE close 0.75T +0t | be_close | 46,592.68 USD | 4,666 | 32.90% | 1.069 | 26,712.64 USD |
| 3 | trail close 1T | trail_close | 46,436.70 USD | 4,665 | 33.10% | 1.068 | 23,711.48 USD |
| 4 | trail close 1T from 0.5T | trail_close | 46,436.70 USD | 4,665 | 33.10% | 1.068 | 23,711.48 USD |
| 5 | BE close 0.75T +1t | be_close | 45,882.68 USD | 4,666 | 37.14% | 1.068 | 27,012.64 USD |
| 6 | trail 1T from 0.75T | trail_frac | 43,352.68 USD | 4,666 | 32.21% | 1.064 | 28,148.62 USD |
| 7 | BE touch 0.75T +0t | be_touch | 33,650.62 USD | 4,669 | 30.65% | 1.052 | 32,486.66 USD |
| 8 | BE touch 0.75T +1t | be_touch | 32,850.62 USD | 4,669 | 40.01% | 1.051 | 33,186.66 USD |
| 9 | trail 1T | trail_frac | 32,252.68 USD | 4,666 | 31.23% | 1.049 | 29,246.58 USD |
| 10 | trail 1T from 0.25T | trail_frac | 32,252.68 USD | 4,666 | 31.23% | 1.049 | 29,246.58 USD |

Rules with a positive objective: 58 of 396. Rules beating the baseline: 0 of 395.
