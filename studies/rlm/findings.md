# RLM (Reaction Level Matrix, WillyAlgoTrader) on CL: findings

2026-11-20, Claude + Codex. Dev only (2010-06..2021), **in-sample, best of 13,824** (13,882 with the session
windows) unless noted. Validation and holdout not loaded. Spec: `docs/strategies/rlm/README.md`.

Files: grid `grid_dev_475d0bd254.csv` (+ `_screened`), `screen_dev.txt`, family check `family_check.txt`
(`family_parts/` is gitignored), random-date null `null/lead.csv`, trade study `trades/lead_dev*.csv` +
`trades_lead_dev.txt`, sessions `sessions_dev.txt/.csv`, Codex briefs/replies `codex/`. Pipeline: `rerun.sh`
(grid, screen, family) then `followup.sh` (ledger, null, trades, sessions).

Code fixes before these results (all from Codex reviews, all tested in `tests/test_rlm.py`): one extreme seen on several
timeframes is one touch (smaller touches inside one bigger candle coalesce), confirm-mode removals come exactly from
the swing detector (`detect(observer=...)`), withdrawals take back the touch's current strength share, BE uses the
frozen TP1, roll-straddling candles are skipped, grid parts are fingerprinted by code and bar content. Every number
from before these fixes is void and kept in `pre_dedup/` (incl. `findings_pre_fix.md`).

## What the original indicator really measures
Its "win rate" = share of trades that touched TP1 (1R), so a 1R touch followed by a break-even stop counts as a win.
Same-bar stop + target counts the target, entry is at market on the close, no fees or P&L. The dashboard number
cannot show profitability. Here: real 1-CL brackets, fees, stop-first inside a bar, limit entries.

## Screen (declared before the grid)
| Gate | Versions passing (of 13,824) |
|---|---|
| trades ≥ 200 | 10,899 |
| PF ≥ 1.25 | 594 |
| years positive ≥ 70% | 746 |
| Combine pass ≥ 50% | 431 |
| cost/pass ≤ $500 | 1,711 |
| both halves > 0 | 2,283 |
| neighbours ≥ 60% positive | 3,413 |
| **all** | **4** |

Grid overall: 39.1% of versions net > 0, median PF 0.98 (no edge on average). The 4 that pass are one family:
1h, confirm, all sources, flat weight, tol 0.4, score 50, limit at the close; they differ in stop (band/wick), target
(1R/2R) and close strength (0.6/0.75).

## What carries the result (median PF / share of versions net > 0)
| Dimension | Reading |
|---|---|
| sig_tf | **1h 1.011 / 51%**; 15m 0.990 / 42%; 5m 0.946 / 25% |
| entry | band retest 0.999 / 48%; close 0.962 / 31% |
| exit | r1 1.004 / 51%; r2 0.994 / 46%; r3 0.976 / 35%; **be3 (original's BE after TP1) 0.934 / 25%: worst** |
| session | rth 0.989 / 44%; all 0.974 / 34% |
| tol | 0.4 0.990 > 0.6 0.982 > 1.0 0.970 (tighter bands better) |
| weight (owner TF strength vs flat) | tf 0.982 / 40%; flat 0.978 / 38%: **no measurable difference**. The score threshold is not comparable across schemes (flat needs ~5 touches for score 50, TF weights 2-3): the lead's TF sibling has 5,146 trades and PF 1.07 |
| reg, sources, stop, clv | small differences; score 0 0.990 > 50 0.975 > 70 0.968 |

## Lead version
`sig_tf=1h reg=confirm sources=all weight=flat tol=0.4 score=50 clv=0.6 entry=close stop=band exit=r1 session=all`
| Check | Result |
|---|---|
| Touch fills (ledger `2851bcbfb212`) | 1,249 trades, +$66,184, PF 1.345, win 55.3%, 11/12 years, pass 55.7%, $321/pass, max DD −$6,407 |
| Strict fills `--through 1` | 1,218 trades, +$57,849, PF 1.303, 11/12 years, pass 53.9%, $373/pass |
| Halves | +$39,465 (2010-15) / +$26,719 (2016-21) |
| Years | 2016 −$1,871; 2019 +$902; the other 10 +$2.0k to +$15.0k |
| Sides | short PF 1.37, long PF 1.32 |
| Concentration | top 10 days = 23% of net |
| One-step neighbours | 81% net > 0 |
| Random-date null (300 runs, same CT minute/side/offset/risk/target) | median PF 0.972; 0/300 ≥ 1.345 |
| **Family-wise White Reality Check (declared step 2)** | lead is rank 1 of 13,824 by t (4.47); bootstrap max t median 3.78, 95% 4.66; **p = 0.086** |

The single-version nulls say the lead's P&L is not random; the family check says a best-of-13,824 this good still
turns up about 1 time in 12 with no edge anywhere. Close, not proof.
Not re-run on the fixed code (same version, see `pre_dedup/`): Codex's same-day no-level null (0/300, median PF 0.85)
and fill audit (no fill beyond the stop; PF holds without price-improved fills).

## Sessions, hours and daylight saving (declared, 58 windows; `sessions.py`)
Lead frozen, only the window of the 1h signal candle's open time changes. Seen before the test: London + RTH carried
most of the lead's net (disclosed in the README), so this is partly a confirmation.
| Window | Trades | PF | Pass | $/pass | Halves | Within-58 RC p |
|---|---|---|---|---|---|---|
| all hours (lead) | 1,249 | 1.345 | 56% | $321 | +39.5k / +26.7k | — |
| **ct 02-10 (London + US open)** (ledger `d70b216ba51e`) | 661 | **1.517** (strict 1.464) | **73%** (strict 70%) | $380 (strict $441) | +43.4k / +15.1k | < 0.001 |
| ct 02-14 (all but Asia) | 834 | 1.479 | 66% | $361 | +42.6k / +19.0k | < 0.001 |
| ct 02-06 London / ldn 08-12 London clock | 358 / 361 | 1.531 / 1.554 | 61% / 71% | $817 / $664 | both + | 0.017 / 0.010 |
| ct 07-10 US open | 309 | 1.509 | 70% | $686 | both + | 0.058 |
| ct 17-01 Asia | 435 | 1.164 | 36% | $1,480 | +0.6k / +10.1k | 0.94 |

Single candles (35-95 trades each) are noise-level: best 13:00, 03:00, 21:00 CT (PF 1.9-2.3), worst 18:00, 14:00,
19:00, 11:00 CT (PF 0.71-0.93); none is better than best-of-58 luck.

**Exchange candle vs Malaysia clock (owner question).** Leave-one-year-out error of each trade's R from hour means:
the exchange candle predicts better than the Malaysia hour. Lead: −0.0086, 90% CI [−0.020, +0.003]; lead with
score 0 (7,622 trades): −0.0018, 90% CI [−0.0034, −0.0001], below zero. On the 7,622 trades the US summer and winter
profiles agree by exchange candle (corr +0.55) and not by Malaysia hour (corr −0.10). **The effect follows the candle
number after the 17:00 CT open, not the wall clock** (e.g. the 08:00 CT candle is 21:00 Malaysia in summer, 22:00 in
winter). London clock vs exchange clock for London: 1.55 vs 1.53, too few mismatch weeks to tell.

Caveat: the window is chosen on dev after the lead was chosen; the 58-window RC does not undo the 13,824-version
selection behind the lead.

## Trade study (lead, wins vs losses; 14 predeclared features, 5 bins each; descriptive only)
No feature splits winners from losers cleanly; most bins' day-clustered 90% CIs overlap. Weak patterns: a close
0.37+ ATR away from the band beats a close just outside it (avg R 0.13-0.19 vs −0.04); heavily used levels are
weaker (10+ touches 0.045 vs 0.16 at 6-8 touches; fresh 0-1 crosses 0.17); both sides positive. Any of these as a
filter is a new trial needing data it was not found on. None is adopted.

## Combine sizing
1 CL only. Planned loss per trade incl. fee: median $374; at 5 CL, 568 of 1,249 planned losses (46%) exceed the
$2,000 MLL.

## Status / verdict
- Screen: 4 pass. Strict fills: hold. Random-date null: pass. **Family-wise check: p = 0.086** (not below 0.05).
- Session test: ct 02-10 window PF 1.52, pass 73% (strict 1.46 / 70%); the effect follows the exchange candle.
- Owner decision pending: one 2022-2024 check-years run on the lead and/or the ct 02-10 window, declared before
  running. Holdout untouched.
