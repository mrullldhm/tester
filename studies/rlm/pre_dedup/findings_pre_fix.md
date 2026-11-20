# Superseded: findings from before the dedupe and exact-withdrawal fixes (2026-11-20). Current: ../findings.md

# RLM (Reaction Level Matrix, WillyAlgoTrader) on CL: findings

> **Current results (after the dedupe + exact-withdrawal fixes, 2026-11-20)** — the sections further below are the
> pre-fix run, kept for the record (`pre_dedup/`); use this box and `docs/strategies/rlm/README.md` Results.
> - Screen: 13,824 versions, median PF 0.98, 39.1% net > 0, **4 pass all gates** (1h/confirm/all/flat/tol 0.4/score 50/close).
> - Lead (band stop, 1R, all hours): 1,249 trades, PF 1.345 (strict 1.303), 11/12 years, pass 56%, $321/pass; top 10
>   days 23% of net; random-date null 0/300; **White RC p = 0.086** (was 0.25).
> - Window ct 02:00-10:00: 661 trades, PF 1.517 (strict 1.464), pass 73%, $380/pass, halves +43.4k / +15.1k.
> - Clock: exchange candle predicts better than Malaysia hour (score-0 set: −0.0018, 90% CI [−0.0034, −0.0001]);
>   summer/winter same-candle corr +0.55 vs same-Malaysia-hour −0.0x. Effect follows the candle number.
> - Trade features: close well away from the band (≥0.37 ATR) avgR ~0.13-0.19 vs just outside −0.04; heavily used
>   levels weaker; both sides positive. Descriptive only.
> - Owner decision: one 2022-2024 check-years run on the lead and/or the ct 02-10 window.

2026-11-20, Claude + Codex. Dev only (2010-06..2021), **in-sample, best of 13,824** unless noted. Validation and holdout
not loaded. Spec: `docs/strategies/rlm/README.md`. Codex briefs/replies: `codex/`. Grid: `grid_dev_9a2fa27f50.csv`
(+ `_screened`), summary `screen_dev.txt`, random-date null `null/lead.csv`, trade study `trades/lead_dev*.csv`,
family check `family_parts/` + `family.py`.

## What the original indicator really measures
Its "win rate" = share of trades that touched TP1 (1R), so a 1R touch followed by a break-even stop counts as a win.
Same-bar stop + target counts the target, entry is at market on the close, and it has no fees or P&L. The dashboard
number cannot show profitability. Here: real 1-CL brackets, fees, stop-first inside a bar, limit entries.

## Screen (declared before the grid)
| Gate | Versions passing (of 13,824) |
|---|---|
| trades ≥ 200 | 10,912 |
| PF ≥ 1.25 | 599 |
| years positive ≥ 70% | 751 |
| Combine pass ≥ 50% | 425 |
| cost/pass ≤ $500 | 1,731 |
| both halves > 0 | 2,325 |
| neighbours ≥ 60% positive | 3,422 |
| **all** | **1** |

Grid overall: 38.9% of versions net > 0, median PF 0.98 (no edge on average).

## What carries the result (median PF / share of versions net > 0)
| Dimension | Reading |
|---|---|
| sig_tf | **1h 1.01 / 51%**; 15m 0.99 / 42%; 5m 0.945 / 24% |
| entry | band retest 0.997 / 47%; close 0.962 / 31% |
| exit | r1 1.004 / 50%; r2 0.994; r3 0.977; **be3 (original's BE-after-TP1) 0.934 / 25%: worst** |
| session | rth 0.989 / 44%; all 0.974 / 34% |
| tol | 0.4 0.990 > 0.6 0.982 > 1.0 0.971 (tighter bands better) |
| weight (owner TF strength vs flat) | tf 0.982 / 40%; flat 0.977 / 38%: **no measurable difference**. The score threshold is not comparable across schemes (flat needs ~5 touches for score 50, TF weights 2-3), so this does not isolate the value of TF strength |
| reg (lock vs confirm), sources (all vs htf), stop (wick vs band), clv | small differences |

## Lead version (the only one through every gate)
`sig_tf=1h reg=confirm sources=all weight=flat tol=0.4 score=50 clv=0.6 entry=close stop=band exit=r1 session=all`
| Check | Result |
|---|---|
| Touch fills (ledger `0c7941f8774a`) | 1,281 trades, +$61,525, PF 1.309, win 54.5%, 11/12 years, pass 52.3%, $332/pass, max DD −$6,902 |
| Strict fills `--through 1` | 1,250 trades, +$53,020, PF 1.267, 10/12 years, pass 50.0%, $375/pass |
| Halves | +$34,855 (2010-15) / +$26,670 (2016-21) |
| Years | 2016 −$1,381, 2013 +$212; the other 10 positive |
| Sides | short PF 1.36, long PF 1.26 |
| Concentration | top 10 days = 25% of net (995 trading days with trades) |
| One-step neighbours | 81% net > 0; exits r2/r3/be3 PF 1.23-1.33, stop wick 1.24, clv 0.75 1.26, rth 1.46; breaks at tol 1.0 (PF 0.98) and score 0 (1.02) |
| Random-date null (300 runs, same CT minute/side/offset/risk/target) | median PF 0.974, max 1.17; 0/300 ≥ 1.309 (z 5.2, not selection-adjusted) |
| Same-day null (Codex, 300 runs: another completed hour on the same day, same side, CLV ≥ 0.6, same risk; no level test) | median PF 0.845, 95% 0.774-0.919, max 0.948; 0/300 reach 1.309 |
| Fill audit (Codex) | replayed exactly; trades without price improvement PF 1.35; one extra minute of order delay PF 1.32; no fill beyond the stop |
| Late entries | 91 entries ≥ 14:00 CT mostly flatten; without late signals PF 1.30 |
| Spot checks | 3 (Claude) + full replay (Codex) match raw bars |

## Trade study (wins vs losses; 14 predeclared features, 5 bins each; descriptive only)
No feature separates winners from losers strongly; most bins' day-clustered 90% CIs overlap. Weak, consistent-looking
patterns: heavily used levels are flat (10+ touches avgR −0.00, 6+ crosses 0.03 vs fresh 0-1 crosses 0.17); a
close 0.37+ ATR away from the band beats a close just outside it (0.15-0.19 vs −0.06); higher ATR better; both sides
positive; every CT-hour bin positive (07-10 CT best). Any of these used as a filter is a new trial and needs data it
was not found on. None is adopted.

## Combine sizing (Codex)
1 CL only. Planned loss per trade incl. fee: median $374, 95th pct $924, max $2,354. At 5 CL, 581/1,281 planned
losses exceed the $2,000 MLL.

## Family-wise check (declared step 2): does the lead beat what picking 1 of 13,824 produces?
Daily P&L of all 13,824 versions on dev (2,976 days), stationary day-block bootstrap (1,000 runs, mean block 5 days,
same days for every version so their correlation is kept), t-stat of mean daily P&L (`family_check.txt`).
| Test | Bootstrap max t (median / 95%) | Observed | p |
|---|---|---|---|
| White Reality Check (declared) | 3.76 / 4.67 | family best 4.19; lead 4.07 (rank 4) | 0.18 / **0.25** |
| Hansen SPA (post-hoc sensitivity) | 3.72 / 4.65 | same | 0.16 / 0.23 |

**The lead does not survive the family-wise check.** Against a single random-entry null it looks very strong (z 5.2,
0/300 same-day nulls), but with 13,824 correlated tries a t of ~4 is what the best version reaches even if no version
has an edge. The two nulls answer different questions: "is this version's P&L random?" (no) vs "is the best of
13,824 better than selection luck?" (not shown). The family's best four are all different versions (15m/5m band-retest
RTH r2 and the 1h lead), which is what noise at the top of a large family looks like.

## Sessions, hours and daylight saving (declared test, 58 windows; `sessions.py`, `sessions_dev.txt`)
Lead frozen, only the window of the 1h signal candle's open time changes. Seen before the test: the lead's
London + RTH hours carried ~80% of net (disclosed in the README), so this is partly a confirmation.
| Window | Trades | PF | Pass | $/pass | Halves | Within-58 RC p |
|---|---|---|---|---|---|---|
| all hours (lead) | 1,281 | 1.31 | 52% | $332 | +34.9k / +26.7k | — |
| **ct 02-10 (London + US open, exchange candles)** | 675 | **1.47** (strict 1.41) | **64%** (strict 58%) | $394 (strict $441) | +39.4k / +15.5k | < 0.001 |
| ct 02-14 (all but Asia) | 853 | 1.44 | 60% | $383 | +39.1k / +19.4k | < 0.001 |
| ct 02-06 London / ldn 08-12 London clock | 363 / 365 | 1.48 / 1.51 | 54% / 67% | $822 / $735 | both + | 0.04 / 0.02 |
| ct 07-10 US open | 319 | 1.47 | 68% | $745 | both + | 0.08 |
| ct 17-01 Asia | 448 | 1.13 | 27% | $1,850 | −0.5k / +9.7k | 0.98 |
Single candles (40-95 trades each) are noise-level: best CT 03:00, 08:00, 21:00 (PF 1.8-1.9), worst 18:00, 00:00,
01:00, 14:00 (PF 0.73-0.89); none is better than best-of-58 luck (p ≥ 0.23).

**Exchange candle vs Malaysia clock (owner question).** Leave-one-year-out error of each trade's R from hour means:
the exchange candle predicts better than the Malaysia hour. Lead (1,281 trades): −0.0071, 90% CI [−0.018, +0.004];
lead with score 0 (7,653 trades): −0.0021, 90% CI [−0.0037, −0.0003], below zero. Per exchange candle, the US summer
and winter profiles agree (corr +0.49 on 7,653 trades); matched by Malaysia hour instead (candle shifted one) they do
not (corr −0.06). **The effect follows the candle number after the 17:00 CT open, not the wall clock**: e.g. the
08:00 CT candle is 21:00 Malaysia in summer and 22:00 in winter, and it is that candle that matters.
London clock vs exchange clock for the London session: 1.51 vs 1.48, too few mismatch weeks (~4 a year) to tell.

Caveat: the window is chosen on dev after the lead was chosen; the 58-window RC does not undo the 13,824-version
selection behind the lead. Total trials 13,882.

## Status / verdict
- Step 1 (screen): 1 pass. Step 3 (strict fills, spot checks): pass. **Step 2 (family-wise): fail, p = 0.25.**
- Session test: the 02:00-10:00 CT window (exchange candles) improves PF to 1.47 and pass rate to 64% (strict 1.41 /
  58%); the effect follows the exchange candle, not the Malaysia clock.
- Owner decision needed: spend the single validation run (2022-2024) on the frozen lead and/or the ct 02-10 window
  (declare which before running), or stop on dev. Holdout untouched.
- Same lesson as purple_levels / CBR: thin CL edges at 1h/RTH, strong vs naive nulls, not strong vs multiple testing.
