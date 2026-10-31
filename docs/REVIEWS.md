# Codex reviews

Claude built the repo; Codex (OpenAI Codex CLI 0.163.0) reviewed and replicated, as set out in `AGENTS.md`.

## R1: plan review (docs/PLAN.md), 2026-10-29
2 critical, 11 high, several medium findings. Main changes made:

| Finding | Change |
|---|---|
| Exact CL1! parity needs TradingView's own bars and roll dates | Stated as a limit in README and `docs/ENGINE.md`; Pine twin added so parity can be checked on TradingView |
| R-multiple target from the fill is not computable at the signal close | Targets use Pine `profit=` in ticks from the actual fill, R from the signal close |
| Skipping bars would change indicator state | Indicators over every bar in `prepare`; a literal bar-by-bar Pine transcription test proves the port |
| Roll exit is not TradingView behaviour | Kept (owner's explicit choice), labelled as an owner rule; 0-1 roll exits per session in practice |
| Pivot / ATR / window / anchor semantics underspecified | Ported line for line; strict pivots, Wilder ATR `[1]`, half-open window, anchor-only resets |
| Drawdown must use TV's pre-entry closed-equity formula | Implemented from the TradingView help page; % of initial capital |
| Margin default in Pine v6 is 100% | `margin_long = margin_short = 0` in the Pine twin |
| Reversal policy, commission per contract, avg bars + 1, Sharpe / Sortino conventions | Defined in `docs/ENGINE.md` |

## R2: code review, 2026-10-29 (pytest log hash checked by Codex)
1 high, 8 medium. All fixed, each with a regression test (`tests/test_engine.py`):

| Sev | Finding | Fix |
|---|---|---|
| High | Updater accepted NaN prices | Non-finite values rejected |
| Medium | Reversal deleted the incoming entry's bracket | Only the outgoing entry's exits are cancelled |
| Medium | Exit stop already through the close when placed lost its trigger on a gap back | Triggered exit stops fill at the next open |
| Medium | Stop-limit entries filled as two independent legs | Refused (NotImplementedError) |
| Medium | Several exits per entry ignored quantity reservation | Refused: one `strategy.exit` id per entry |
| Medium | `profit` overwrote `limit` (and `loss` overwrote `stop`) | The level price reaches first wins (Pine v6) |
| Medium | Open trade at the end left out of drawdown / run-up / buy & hold | Included |
| Medium | Monthly returns used realized profit only | Month-end equity marked to market |
| Medium | Massive updater fetched a fixed 3 contracts | Fetches every contract through the end date; refuses if the last one becomes front |

No issues found in pivot timing, ATR[1], stop ranges, session / DST handling, look-ahead, Python / Pine
signal parity, report rendering or the CLI.

## R3: independent replication of the New York top combination, 2026-10-29
Codex wrote its own engine and signal code (no import from `tvtester` or `strategies`) and ran it on all
5,667,487 bars.

| Slippage | Trades | Codex net | Claude net | Difference |
|---|---|---|---|---|
| 0 ticks | 3,710 | 42,475.80 USD | 42,475.80 USD | 0.00 |
| 1 tick | 3,704 | -20,100.08 USD | -20,100.08 USD | 0.00 |

Every trade matched on side, entry and exit time, prices, profit and exit reason.

## R4: feature-2 plan and design review (docs/OPTIMIZE.md), 2026-10-31
Two passes: the plan draft (14 high, 5 medium) and the revised design (4 high, 4 medium). Main changes:

| Finding | Change |
|---|---|
| A `prepare` mask is a scheduling hint, not a gate: `on_bar` also runs while a position is open | Veto checked at the entry decision in `on_bar`; test: vetoed signal bars never trade |
| 2024 onward already exposed by feature 1 | Development interval ends 2024-01-01 (exclusive); 2024+ labelled "previously exposed, reserved", not clean OOS |
| Baseline trade subsets are not filtered-strategy results; 0-tick trades cannot give 1-tick results | Association report labelled descriptive; separate engine runs per scenario |
| Trades lacked their signal bar | `signal_bar` / `signal_time` on every trade |
| Look-ahead risks: HTF `request.security` timing, settlement is a VWAP window, EIA exceptions, roll week | Deferred; first features limited to five with written contracts and causality tests |
| `ta.highest(...)[1]` inside the reset block has conditional history in Pine | Computed at global scope every bar, sampled at the reset |
| Cache keyed by `id(bars)` | Cache lives on the `Bars` object |
| Objective / ties / terminal position / no winner / neighbours undefined | Objective = net + open P&L, 300-trade minimum, PF ties, "no eligible trial", neighbours diagnostic only |

## R5: feature-2 code review, 2026-10-31 (pytest log hash checked by Codex)
5 high, 6 medium. All fixed, each with a test in `tests/test_features.py`:

| Sev | Finding | Fix |
|---|---|---|
| High | Feature test read reserved-period outcomes | Parity test now on the development interval against the feature-1 trade list cut at 2024-01-01 |
| High | A winner with no neighbours crashed the report | Empty neighbour tables handled |
| High | `MaxTrialsCallback` let parallel workers overrun the budget | TPE driven by ask / tell in one process; exact budget |
| High | Evaluations lost from the ledger when a run failed late | `search_start` event, `evaluations.jsonl` written as it goes; `features` / `replay` log before running |
| High | Reopening an unfinished journal mixed experiments | A search id is used once; existing run directories are refused |
| Medium | Duplicate detection raced across workers | Duplicates claimed in-process before evaluation |
| Medium | Loader opened `year=2024.parquet` for an end of 2024-01-01 | An exclusive 1 January end never opens that year (test with a spy) |
| Medium | Replay ignored the interval start; matched without open P&L / objective | Whole interval validated; open P&L and objective compared |
| Medium | Data hash ignored contract symbols (roll exits) | Hash covers times, prices, volume and contracts |
| Medium | Constant feature values crashed bucketing | One bucket per value when there are fewer than five distinct values |

`cli test` (feature 1) still reads every bar by the owner's design; the rule is that it is never used to judge a
feature-2 change (docs/OPTIMIZE.md).

## R6: independent replication of the NY feature-2 candidate and final review, 2026-10-31
Codex wrote its own engine, signal and feature code (no import from `tvtester` or `strategies`), opening only the
2010-2023 parquet files (4,682,668 bars). Configuration `strategies/configs/fair_price_reversal_ny_filters_random_net1_s1_n200.json`.

| Slippage | Codex trades | Claude trades | Codex net | Claude net | Difference |
|---|---|---|---|---|---|
| 0 ticks | 927 | 927 | +63,293.46 USD | +63,293.46 USD | 0.00 |
| 1 tick | 926 | 926 | +49,297.48 USD | +49,297.48 USD | 0.00 |

Every trade matched on side, signal / entry / exit times, prices, profit, exit reason, contract, signal bar, bars,
quantity and commission. Findings (2 high, 4 medium), all fixed:

| Sev | Finding | Fix |
|---|---|---|
| High | Engine runs only reached the ledger after a whole search finished | Each batch (and the neighbour batch) is logged before it runs; test with an engine failure in the second batch |
| High | Notebook claimed a strict advance budget and development-only selection while the ledger shows three after-the-fact looks, one on reserved data | Exceptions disclosed in the lab notebook (`docs/strategies/fair_price_reversal/optimize/README.md`) |
| Medium | "Both candidates turn a loss into a profit": NY's development baseline already made +2,423 at 1 tick | Reworded per variant |
| Medium | A flat $24.02 round-trip cost ignored unslipped limit exits ($14.02) | Cost stated by exit type |
| Medium | "Asia has no configuration that makes money" ignored trials under the trade minimum | "No eligible trial" |
| Medium | E3 conclusions overstated (cause, "curve-fit", four filters) | Narrowed to what these runs show; three filters |


## R6: Supertrend + Kalman plan review (docs/research/supertrend_kalman_plan.md), 2026-10-31
7 high, 11 medium (full text: logs/codex/r6_plan_review.md). Main changes:

| Finding | Change |
|---|---|
| `ta.pivothigh` and the strict buffer pivot differ | Strict custom pivot in both twins |
| Carried-forward HTF signal could re-enter | One decision per completed M15 bucket, at the first 1m bar of the next bucket; vetoed / occupied events expire |
| Market close racing an open bracket | `flip` exit cancels the bracket before `close_all` |
| Trail amend timing, opposite-side UT levels, target recomputed | Amend at the receiving bar's close; opposite-side levels rejected; entry `profit` ticks frozen |
| Kalman, UT events, Supertrend sign underspecified | Kalman frozen to Codex's spec (P0 = 100 I, Joseph update); UT buy = close > T and close[1] <= T[1]; side = -direction |
| `all` variant roll exit not in TradingView | Labelled; roll exits counted in the doc |
| Selection count | Full count disclosed (6,912) |

Deviation: `kalman_q` became a grid value {0.01, 0.0001} after 0.01 agreed with 97.5% of Supertrend flips on 2023
(signal counts only, no profit numbers).

## R7: Supertrend + Kalman code review, 2026-10-31 (pytest log hash checked by Codex)
2 high, 3 medium, all fixed (logs/codex/r7_code_review.md, re-check r7b_fix_check.md: all correct):

| Sev | Finding | Fix |
|---|---|---|
| High | Pine `nz()` on a bool does not compile in v6 | `not aUp[1]` |
| High | Undisclosed grid cuts (`st_factor` 2, `atr_ratio` 1.0 / 1.3) | Restored: 1,728 per variant |
| Medium | Session close kept the bracket (same race as `flip`) | Bracket cancelled first, regression test |
| Medium | SMA-seeded `ema` called Pine `ta.ema` | Pine seeding (first valid value); twin uses built-in `ta.ema` |
| Medium | Partial first M15 bucket accepted | Bars must start on a 15-minute boundary |

No defect in the HTF tuple offsets or the grid chunking (`cli test --chunks`).

## R8: independent replication of the Supertrend + Kalman `all` top combination, 2026-10-31
Codex's own code, all 5,667,487 bars, computed before opening Claude's trade lists.

| Slippage | Trades | Codex net | Claude net | Difference |
|---|---|---|---|---|
| 0 ticks | 4,471 | 128,886.58 USD | 128,886.58 USD | 0.00 |
| 1 tick | 4,461 | 42,086.78 USD | 42,086.78 USD | 0.00 |

Every trade matched on signal bar, side, times, prices, profit and exit reason (121 roll exits in both).

## R9: Supertrend + Kalman feature-2 plan and code review, 2026-10-31 (pytest log hash checked by Codex)
Plan (logs/codex/r9_f2_plan_review.md): 1 high, 3 medium, 3 low, no look-ahead in the feature formulas.

| Finding | Change |
|---|---|
| Feature eligibility must not depend on the position (filters and slippage change it) | Features defined at every structurally eligible signal; flatness and veto checked only at entry; test |
| ER warm-up / zero denominator unspecified | NaN until 21 buckets and on a zero sum, in both twins; test |
| Candidate acceptance not predeclared | Candidate rule written before E1 (1 and 2 ticks, 2/3 neighbours, no year above 50%, tie rule) |
| H4 needs two bounds; cost wording; `all` 1-tick result misquoted | H4 split into two tails; cost per exit type; feature-1 conclusion corrected |

Code (logs/codex/r9b_f2_code_review.md): no implementation defect; the exit-veto test was vacuous (filter incompatible
with the NY base RVI rule). Rewritten: a veto on every bar after entry leaves the exit unchanged for flip / trail / fixed.

## R10: independent replication of the NY feature-2 candidate (supertrend_kalman), 2026-10-31
Codex's own code, 4,682,668 development bars, computed before opening Claude's trade lists.

| Slippage | Trades | Codex net | Claude net | Difference |
|---|---|---|---|---|
| 0 ticks | 2,247 | 104,217.06 USD | 104,217.06 USD | 0.00 |
| 1 tick | 2,247 | 60,457.06 USD | 60,457.06 USD | 0.00 |

Every trade matched. Found: NY has 10 owner-rule roll exits the Pine twin does not do (twin and docs corrected).

## R11: is feature 2 strategy-generic? 2026-10-31 (pytest log hash checked by Codex)
Owner-requested audit of the feature-2 modules for fair_price_reversal assumptions. Fixed: association weekday clock
came from the FPR session object (supertrend weekdays were UTC; now `Strategy.report_tz`), ledger lineage note
per strategy with exclusive create, OPTIMIZE.md veto wording, supertrend feature-contract table, stronger tests,
ledger corrections for 53 code-check engine runs. Codex (logs/codex/r11_f2_generic_audit.md): no remaining FPR
assumption in features / search / tune / associate / experiment / cli / report / metrics; contracts, veto and
ledger counts verified; low: label the old UTC weekday tables (done).

## R12: feature-3 plan, spec and code review, 2026-11-01 (pytest log hash checked by Codex)
Four rounds. (1) Topstep prop plan (now feature 4): CL limit 3 minis not 5, per-attempt account state, bar-path
MLL/DLL, null baseline for variance seeking. (2) Feature-3 spec draft: frozen candidate vs re-selection need
separate verdicts; closed-trade slicing did not reproduce the E2 objective (now daily marked-to-market equity);
switched configurations need executable fold runs (now `engine.run(start=...)`); DSR N and variance must come from
the same population; CSCV ties, ranks and no-eligible rules frozen; stale "feature 3 = reserved data" notes fixed.
(3) Revised spec: a rebuilt prefix lost the last bar's roll flag (fold runs keep the development set's flags); E2's
profit-factor tie-break restored; "always flat at midnight" claim removed. (4) Code (logs/pytest_review12.log,
121 passed, hash verified): the command now rejects any source search that is not the declared E2 random draw;
the walk-forward chart includes the fold-end market close. No other finding.

## R13: independent replication of the feature-3 results, 2026-11-01
Codex recomputed from `matrix.npz` with its own code: every anchored pick 2014-2023 of all three candidates, PBO
(12,870 splits) and primary DSR (N = 200): differences 0. It re-ran one executable fold with its own engine from the
parquet files (bars before 2016): supertrend_kalman NY trial 33, flat from the first 2015 bar, 1 tick: +7,658.66 USD,
167 trades, difference 0. Verdicts agree: none advances.

