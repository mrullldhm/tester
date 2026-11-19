# CBR (Tomtrades 1h/1m) on CL: findings

2026-11-19, Claude + Codex. Dev only (2010-06..2021), **in-sample, best of 1,728**. Validation and holdout not loaded.
Spec: `docs/strategies/cbr/README.md`. Codex briefs/replies: `codex/`. Grid: `grid_dev.csv` (+ `_screened`),
strict fills `grid_dev_through1_rth-ny.csv`, no-lower-low control `grid_dev_any_rth-ny.csv`, summary `screen_dev.txt`,
`claude/stress_dev.txt`, Codex bootstrap / null / sizing `codex/round3_*`.

## Screen (declared before the first run)
| Gate | Versions passing (of 1,728) |
|---|---|
| trades ≥ 200 | 192 |
| PF ≥ 1.25 | 495 |
| years positive ≥ 70% (all dev years) | 132 |
| Combine pass ≥ 50% | 212 |
| cost/pass ≤ $500 | **0** |
| both halves > 0 | 467 |
| neighbours ≥ 60% positive | 633 |
| **all** | **0** (24 pass all but cost: every one rth/ny, context `reb`) |

Grid overall: 49.9% of versions net > 0, median PF 1.04 (no edge on average).

## What carries the result
| Dimension | Reading (median PF / share of versions net > 0) |
|---|---|
| window | **rth 1.25 / 78.5%**; ny 1.07 / 59%; asia_utc 1.01 / 44%; london 0.99 / 46%; globex 0.94 / 35%; eia 0.86 / 37% |
| context | sweep of the reference-hour extreme (`fh`, the PDF's main trigger) is the worst: 0.95 / 38% |
| bias | `engulf` 0.70 / 26% (2 trades median: too rare); body 1.12, struct 1.09, none 1.04 |
| ext / target / attempts | small differences |

The PDF's literal clock (Asia 2nd hour) and its sweep trigger do not work on CL. What works is a CL-specific
reading: RTH 09:30-10:30 CT, no sweep needed.

## Lead version: rth / reb / none / e20 / r2 / attempts 1 (simplest of the 24)
| Check | Result |
|---|---|
| Touch fills (ledger `c1f04c050fbd`) | 547 trades, +$13,560, PF 1.33, win 38.8%, 10/12 years, pass 89.8%, $1,764/pass |
| Strict fills `--through 1` (ledger `19bb38706c42`) | 504 trades, +$5,394, PF 1.13, 6/12 years, pass 19.1%, $3,528/pass |
| Halves | +$8,987 (2010-15) / +$4,573 (2016-21): weakening |
| Sides | long PF 1.36, short PF 1.30 |
| Concentration | top 10 days = 55% of net |
| Random RTH null (Codex, 1,000 runs, same minutes/sides/brackets on random dates) | null median PF 1.03, 60.8% profitable; observed beaten by 3/1,000 (p ≈ 0.004 nominal, not selection-adjusted; Bonferroni over 1,728 would need 0.00003) |
| No-lower-low control (`shift=any`) | rth PF median 1.17 (vs 1.25 with type 3), 82% positive: most of the edge is RTH 1m MSB reversals after an extension; the type-3 lower low adds a little per trade |
| Sizing (Codex, touch) | 3 CL: pass 50%, $546/pass; 5 CL: 37%, $445/pass, worst trade $2,670 > $2,000 MLL. No size clears both gates |
| Spot checks | 5 trades (Codex) + 1 setup (Claude) match raw bars and the owner swing rule |

## Validation 2022-2024 (owner asked, 2026-11-19; frozen, one run, touch fills)
192 trades, +$494, PF 1.02, win 34.4%, 1/3 years positive (2022 −$780, 2023 +$2,515, 2024 −$1,240), Combine pass
0.5%, 0 sequential passes. Gates (PF ≥ 1.10, pass ≥ 40%) fail. Dev PF 1.33 shrank to about break-even: consistent
with best-of-1,728 selection plus the weakening already seen in 2016-21. **CBR dropped. Holdout not run.**

## Verdict
- **No version passes the declared screen; by protocol CBR stops on dev.** No validation run.
- Real but small lead: CL RTH 09:30-10:30 CT 1m reversal after a 20-min extension, limit at 50% of the MSB leg,
  2R. It beats random RTH brackets on dev, but under strict fills it is PF 1.13 and fails the Combine gates, it is
  too slow at 1 contract, and the edge halved in 2016-21.
- Same pattern as `purple_levels`: CL edges in this repo live in RTH and shrink under strict fills.
