# cbr (Tomtrades CBR simplified, 1h/1m model)

Status: dropped (2026-11-19: best dev version fails validation 2022-2024, PF 1.02, 1/3 years, pass rate 0.5%; holdout not run)
Findings: `studies/cbr/findings.md`. The spec below was written before any P&L run.
Code: `strategies/cbr.py`. Study: `studies/cbr/`.
Source: owner PDF `cbr.pdf` ("Backtesting Reimagined, Tomtrades 1hr/1m model (CBR simplified)", Tom Gratwicke /
itstomtrades), written for XAUUSD with DXY. Mapped to CL by Claude and Codex 2026-11-19 (Codex brief + reply in
`studies/cbr/codex/`). Swing points: owner rule only (`cltester/swings.py`).

## Hypothesis
When price trends on the 1h chart, the next 1h candle often opens against the trend and prints a wick before the
trend resumes. On 1m, the end of that wick shows as an over-extension (20+ minutes one way, no big bounce) that
sweeps a nearby high/low, then a "type 3 shift": a lower low followed by a close above the last swing high (MSB).
Late sellers are trapped below the swept level; price rebalances to the middle of the extension leg.
Who is on the other side: stop-out / breakout sellers at the sweep. Gold claim; CL untested.

## PDF rules and CL mapping (long; short is the mirror)
| PDF (gold) | CL version | Note |
|---|---|---|
| 1m entries, best window 2nd hour of Asia (Asia 00:00 UTC) | `window`: entry hour after a reference hour (below) | CL liquidity differs; six analogs |
| Bias from 1h gold + DXY | `bias`: none / ref-hour body direction / ref-hour bullish engulfing of the previous 60 bars / 1h owner-rule structure (HH+HL) at window start | No DXY data. Frozen at window start |
| 20m+ expansion against bias, no substantial pullback | `ext`: origin = earliest bar 20..60 bars before L2 whose high is the highest high to L2 and that passes the filter (the whole one-way move) (`e20`: ≥20 bars, largest bounce ≤ 50% of leg, close efficiency ≥ 0.30; `e30`: ≥30, ≤50%, ≥0.25; `e20loose`: ≥20, ≤60%, ≥0.20; `dur`: ≥20 bars only) | Thresholds fixed by setup frequency, before P&L (Codex's 25%/0.65 kept 0.5% of setups: gold-scale numbers) |
| Sweep of 1st-hour low, or range rebalance (+ 30m low sweep 30m+ into 2nd hour) | `context`: `fh` L2 below the reference-hour low, L2 inside the window, MSB close back above it; `reb` extension only; `reb30` L2 below the last completed 30m candle low (from the ref hour on), L2 in the window's last 30 min | "Rebalance" = extension proxy, not Trader Kane's model |
| Type 3 shift on 1m | owner 1m swings: newest point swing low L2 < previous swing low L1, swing high H1 between; MSB = first 1m close above H1 (state as known at that close) | Inside the window, one contract and one session from the bar before L1 |
| Entry ~50% of MSB move | buy limit at L2 + floor((U − L2)/2), U = highest high L2..MSB bar, frozen at the MSB close | Works 15 bars (the window limits signals, not fills); cancelled by a target touch (engine `kill`) or a newer setup |
| Stop at the shift low | stop = L2 | Risk < 5 ticks: skipped (fee $4.04 = 8% of 5 ticks) |
| TP: 50% of the over-extension, fixed 1.5R, or broader | `target`: `mid` = floor((origin high + L2)/2) (skip if ≤ entry), `r1.5` / `r2` = entry + ceil(k·risk) | 2R from the PDF example |
| Max 2 attempts per session, done after one win | `attempts`: 1 or 2 fills per day, stop after the first winning exit | Unfilled orders are not attempts |

Windows (`window`, reference hour then entry hour):
| Key | Reference hour | Entry hour | Why |
|---|---|---|---|
| `asia_utc` | 00:00-01:00 UTC | 01:00-02:00 UTC | literal PDF clock |
| `globex` | 17:00-18:00 CT | 18:00-19:00 CT | 2nd hour after CL reopens |
| `london` | 08:00-09:00 London | 09:00-10:00 London | London participation |
| `ny` | 08:00-09:00 CT | 09:00-10:00 CT | NY open anchor |
| `rth` | 08:30-09:30 CT | 09:30-10:30 CT | old pit / RTH (repo's purple_levels edge sat in RTH) |
| `eia` | Wed 09:30-10:30 CT | Wed 10:30-11:30 CT | EIA release (holiday shifts ignored: no calendar data) |

Roll/session guard (Codex audit 2026-11-19): structure from the bar before L1, the reference hour, the extension search and the 1h structure points must sit in the signal's contract (structure, ref hour and extension also in its trading day); the engulf's previous 60 bars may cross the 16:00-17:00 halt but not a roll. `struct` abstains (0) when its 1h points cross a roll.

1 contract, engine fills (touch fills, no exit slippage, flat 15:10 CT), all signals from data up to the signal bar.

## Parameters and trial budget
| Parameter | Values |
|---|---|
| `window` | 6 above |
| `context` | fh, reb, reb30 |
| `bias` | none, body, engulf, struct |
| `ext` | e20, e30, e20loose, dur |
| `target` | mid, r1.5, r2 |
| `attempts` | 1, 2 |

Owner asked for every version: **1,728 combinations**, all run on dev once as a screen (`studies/cbr/grid.py`,
every row kept in `studies/cbr/grid_dev.csv`). Every dev number from this strategy is **best of 1,728**.
Multiple-testing guard, declared now (years positive counts every dev year; a year with no trades is not positive):
1. Screen: dev gates (PROTOCOL.md) on the full dev period, plus both halves (2010-06..2015, 2016..2021) net
   positive, plus neighbours: of the versions one parameter step away, ≥ 60% net positive.
2. Survivors (max 3, ranked by Combine pass rate) go through `cli test --period dev` (ledger) and `--through 1`
   (strict fill sensitivity must stay PF ≥ 1.10). Spot-check trades against raw bars.
3. Validation 2022-2024: each survivor once, frozen. Holdout only with the owner's yes.
If nothing survives step 1, the strategy is dropped on dev; no re-mapping after looking.

## Pass criteria
PROTOCOL.md dev gates: ≥ 200 trades, PF ≥ 1.25, ≥ 70% years positive, Combine pass rate ≥ 50%, cost per pass
≤ $500. Note: a fixed-time random-ish order (template) scores 19% pass rate on dev, so pass rate alone is noisy.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-11-19 | dev | touch | — | — | median 1.04 | — | — | 1,728-version screen: 0 pass all gates, 24 pass all but cost/pass (all rth/ny, `reb`) |
| 2026-11-19 | dev | touch, no exit slip | 547 | $13,560 | 1.330 | 89.8% | $1,764 | rth/reb/none/e20/r2/attempts 1, best of 1,728; 10/12 years; ledger c1f04c050fbd |
| 2026-11-19 | dev | through 1 | 504 | $5,394 | 1.133 | 19.1% | $3,528 | same version, strict fills; 6/12 years; ledger 19bb38706c42 |

| 2026-11-19 | validation | touch, no exit slip | 192 | $494 | 1.024 | 0.5% | — (0 passes) | same version frozen, run once (owner's yes, outside the screen rule); 2022 −$780, 2023 +$2,515, 2024 −$1,240; longs +$2,923, shorts −$2,428. Fails PF ≥ 1.10 and pass ≥ 40% |

`shift` = `any` (no lower low) is a control added after the screen, not part of the budget.
All results in-sample unless the period is holdout or forward; tuned rows say best of N.
