# Independent audit of purple_levels

**Verdict: stop optimising this family. Freeze one version and paper-test it forward.** There is a plausible liquidity/reversal mechanism and a positive dev result under traded-through entries, but neither tested revision establishes an improvement. The spent validation described in the brief lowers confidence; more dev selection cannot restore independent evidence.

**Scope and multiplicity.** Every performance number below is **dev / in-sample**, 2010-06-07–2021-12-31. Only `load_period("dev")` was called: 3,983,238 bars and 2,976 trading days. No validation/holdout bars, other researcher’s files, git, downloads, CLI tests or ledger writes. Changes are confined to this report and `codex/`. Production source was instrumented in memory to recover setup metadata; all four baseline trade lists reproduced exactly on count, signal/entry/exit bars, side, prices and net. Instrumented order columns equal the original strategy’s signals. Twelve deterministic first/middle/last raw-bar checks passed for setup, contract continuity, entry and exit; this is a spot check, not a full execution audit.

The pre-run [plan](codex/plan.md) declares **8 portfolio cells**: 4 baseline reproductions and 4 fresh revision runs (2 changes × 2 level universes), all 5m. There are **132 nonempty decomposition cells + 4 paired daily comparisons = 144 expectancy tests including portfolios**. Empty bins are not tested. Additional accounting: 8 execution cohorts, 4 top-ten-day removal summaries and 8 power scenarios: **164 evaluated strategy/diagnostic/scenario cells in total**; multiple statistics within a cell are not separate variants. Full results, including years and both fill models, are in [dev_cells.csv](codex/dev_cells.csv). No hidden parameter search or combined revision. Historical selection was already at least 12 candidates plus earlier purple_pa trials and fill sensitivities; this audit is additional research, not a new clean discovery.

Tests use one-sided positive net expectancy, a daily-cluster ratio standard error, and a normal reference. For trade mean μ, SE = √[D/(D−1) Σday(Pday−μNday)²]/N, including zero-trade days. BH covers all 144 tests, retaining overlapping/duplicate cells. Because those tests overlap, the CSV also gives dependence-robust Benjamini–Yekutieli (BY) q-values. BH flags 69 cells; BY flags 36, many describing the same trades. Neither correction accounts for the earlier research history, serial dependence between days, or turns selected dev performance into an out-of-sample claim. Paired revision tests compare total daily P&L, not just a changed mix of trades.

**Baseline and revision results — dev / in-sample; $4.04 round-turn fee, one CL contract, no exit slippage.** “Strict” requires a one-tick trade-through at entry, still executing at the stated limit or better open.

| Portfolio | Trades | Net | Net/trade | PF | Years + | BH q | BY q |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all_touch | 1157 | $37,766 | $32.64 | 1.388 | 11/12 | 0.0002 | 0.0009 |
| all_strict | 1051 | $25,334 | $24.10 | 1.269 | 10/12 | 0.0053 | 0.0295 |
| nopd_touch | 847 | $33,618 | $39.69 | 1.488 | 11/12 | 0.0002 | 0.0009 |
| nopd_strict | 768 | $24,647 | $32.09 | 1.369 | 11/12 | 0.0023 | 0.0129 |
| all_first_only_strict | 565 | $20,777 | $36.77 | 1.410 | 10/12 | 0.0025 | 0.0138 |
| nopd_first_only_strict | 418 | $18,201 | $43.54 | 1.498 | 11/12 | 0.0025 | 0.0138 |
| all_midpoint_strict | 908 | $18,382 | $20.24 | 1.248 | 10/12 | 0.0149 | 0.0829 |
| nopd_midpoint_strict | 660 | $19,844 | $30.07 | 1.385 | 9/12 | 0.0025 | 0.0138 |

The original strict all/nopd portfolios remain positive after removing their ten best days: **$15,586 / $15,540 dev / in-sample**. Their worst dev year is 2019; positive aggregate expectancy does not ensure a viable Combine path. No new Combine pass-rate or cost-per-pass simulation was performed, so none of these revisions is shown to meet the owner’s actual objective.

**Mechanism and decomposition.** A watched high/low can concentrate resting liquidity and breakout stops. A failed break followed by a fast departure could reflect aggressive reversal flow and forced liquidation by trapped breakout traders. The limit buyer/seller then supplies liquidity to a pullback, with the structural extreme defining failure. This could repeat when those participants and order-placement habits persist. Bars do not identify participants or orders: this is an economic hypothesis, not an observed explanation. The supplied level-regime findings give no standalone first-touch edge; a gap partly records a reversal already underway. A bounce conditional on that gap is not an executable profit probability.

The following table attributes accepted original trades, **dev / in-sample**, to the first family in production order at duplicate prices. It is not a family ablation: competing levels, first-family tie-breaking and one-position blocking affect attribution. Clock bins use the signal bar in Chicago time; overnight includes 17:00–07:59. Gap and signed entry distance use the original planned stop distance R. Stop bins are planned entry-to-stop ticks; gap size is the three-candle gap width.

| Component/bin | all strict: N / net / mean | nopd strict: N / net / mean |
| --- | --- | --- |
| family: pd | 534 / $7,573 / $14.2 | — |
| family: pw | 184 / $7,247 / $39.4 | 250 / $8,830 / $35.3 |
| family: sw1d | 118 / $5,263 / $44.6 | 123 / $3,953 / $32.1 |
| family: sw4h | 215 / $5,251 / $24.4 | 395 / $11,864 / $30.0 |
| clock: 08-10 | 164 / $12,037 / $73.4 | 134 / $8,709 / $65.0 |
| clock: 10-12 | 83 / $5,225 / $62.9 | 70 / $5,997 / $85.7 |
| clock: 12-15:10 | 76 / $3,613 / $47.5 | 63 / $3,175 / $50.4 |
| clock: 17-08 | 728 / $4,459 / $6.1 | 501 / $6,766 / $13.5 |
| gap_bin: <=.10 | 232 / $6,623 / $28.5 | 167 / $7,325 / $43.9 |
| gap_bin: .10-.25 | 460 / $11,432 / $24.9 | 344 / $9,080 / $26.4 |
| gap_bin: >.25 | 359 / $7,280 / $20.3 | 257 / $8,242 / $32.1 |
| test_number: 1 | 565 / $20,777 / $36.8 | 418 / $18,201 / $43.5 |
| test_number: 2 | 486 / $4,557 / $9.4 | 350 / $6,446 / $18.4 |
| side: -1 | 514 / $12,363 / $24.1 | 361 / $9,822 / $27.2 |
| side: 1 | 537 / $12,971 / $24.2 | 407 / $14,826 / $36.4 |
| distance_bin: <=.5 | 410 / $4,564 / $11.1 | 303 / $4,716 / $15.6 |
| distance_bin: .5-1 | 641 / $20,770 / $32.4 | 465 / $19,931 / $42.9 |
| stop_bin: <=8 | 124 / −$231 / $-1.9 | 96 / −$248 / $-2.6 |
| stop_bin: 9-16 | 380 / −$195 / $-0.5 | 264 / $1,123 / $4.3 |
| stop_bin: >16 | 547 / $25,760 / $47.1 | 408 / $23,772 / $58.3 |

The empty distance >1R bin was declared but has no trades. Conclusions are descriptive: both sides contribute; first tests look stronger than retests; the higher average return at larger stop sizes and during daytime may reflect volatility and dollar exposure rather than predictive skill. All-strict gap/R bins have no monotonic improvement with larger gaps. Its individual family positive-mean tests all have BH q > .05. These observations do not justify choosing a family, time window, minimum stop or gap threshold after this look. No no-gap, random-level or alternative-stop counterfactual was run, so the gap, level identity and structural stop cannot be causally separated. The exact four-candle confirmation/expiry, 1R target, 5m aggregation and family priority remain unproven choices. First-only removes one exception without inventing a threshold.

**Fill realism — dev / in-sample.** Classifying the original touch run by its first fill bar:

| Universe | First fill bar | N | Net | Mean | PF |
| --- | --- | --- | --- | --- | --- |
| all | touch_only | 467 | $13,563 | $29.04 | 1.412 |
| all | through | 690 | $24,202 | $35.08 | 1.376 |
| nopd | touch_only | 337 | $10,939 | $32.46 | 1.465 |
| nopd | through | 510 | $22,680 | $44.47 | 1.499 |

Dev profit is **not confined to exact-touch fills**: traded-through fills have the higher mean in both universes. But that partition understates the economic cost of waiting for a fill. The complete strict rerun loses $12,432 (32.9%) of all net and $8,971 (26.7%) of nopd net. Matching by original signal explains it:

| Universe / execution cohort | N | Touch net | Strict net | Difference |
| --- | --- | --- | --- | --- |
| all / same_signal_same_bar | 690 | $24,202 | $24,202 | $0 |
| all / same_signal_delayed | 361 | $1,402 | $1,132 | −$270 |
| all / touch_run_only | 106 | $12,162 | $0 | −$12,162 |
| all / strict_run_only | 0 | $0 | $0 | $0 |
| nopd / same_signal_same_bar | 510 | $22,680 | $22,680 | $0 |
| nopd / same_signal_delayed | 258 | $2,128 | $1,968 | −$160 |
| nopd / touch_run_only | 79 | $8,811 | $0 | −$8,811 |
| nopd / strict_run_only | 0 | $0 | $0 | $0 |

Most lost profit comes from signals absent from the strict portfolio. Matching alone cannot separate missing trade-throughs from signals blocked by another working order or position. Waiting also delays many fills; those delayed setups are much weaker than the immediately traded-through cohort. That is consistent with a fill-selection problem: profitable departures can run away, while continued selling into a bid / buying into an offer selects worse opportunities. It is not proof of live queue behaviour or universal adverse selection. One-minute OHLC cannot establish queue position, volume ahead or stop slippage. Strict fills are a sensitivity, not a guarantee of execution; unchanged touch-based targets remain optimistic.

All-strict planned stop median is **17 ticks** (quartiles 11/27), versus a fee of **0.404 tick**: 2.38% of median planned risk. Both <=8 and 9–16 tick stop bins lose after fees in all-strict, while >16 ticks supplies all its net. This is not explained by fees alone: larger dollar risk also changes payoff scale and trade composition. Net/trade before additional execution costs is only **2.41 ticks all-strict / 3.21 ticks nopd-strict**; that is the entire budget for any unmodelled round-trip cost before estimated expectancy reaches zero. Do not turn the observed 16-tick boundary into another filter.

**Two changes only; one parameter value each, no combined version.** The dev reason and rules were written before simulations in the plan. Neither was derived from validation behaviour.

| Change | Exact rule and a-priori reason | Dev / in-sample cost versus original strict |
| --- | --- | --- |
| First tests only | After production signal construction and duplicate tie-breaking, discard test_number=2. Keep all other rules. Removes role-flip retests and their exception; fresh resting liquidity should be less depleted on first encounter. No threshold to tune. Robustness is plausible, not established. | all: −486 trades, −$4,557 net; nopd: −350 trades, −$6,446 net. PF/mean rise but total earning rate falls. |
| Inside-gap entry | Move limit toward stop by floor(gap_ticks/2) ticks (half-gap, one value). Keep structural stop, reset target to 1R from new limit; retain 20-minute expiry. Require through1. Better price compensates for supplying pullback liquidity; normalises placement to the gap rather than an optimised tick offset. One-tick gaps leave limit unchanged. | all: −143 trades, −$6,952 net; nopd: −108 trades, −$4,804 net. Lower risk/closer target and missed fills consume the entry improvement. |

The midpoint test is an entry inside the gap that does not book exact-touch entry fills. It still needs an actual traded-through passive fill in paper trading. It retains the original deduplicated signals; it does not revive discarded same-bar candidates. All four paired positive-improvement tests have **BH q ≥ .848 dev / in-sample**: there is no demonstrated gain in total daily profit. Neither revision is a recommended replacement. First-only is the more defensible simplification if the owner insists on freezing a new hypothesis; any such choice now inherits this dev look and must be judged on new data.

**Honest test plan and power.** The brief says all/nopd touch/strict validation is spent. Renaming or filtering them does not create an independent 2022–2024 test. The family-unused 2025–2026-11-12 holdout could be used once as a locked family-level audit after choosing exactly one specification, execution model, primary metric and stopping rule. It is not truly unseen: the protocol says the owner researched those years before the reset. A failure ends the candidate; no subgroup rescue or second holdout pass. Prefer to preserve it and use forward/paper data strictly after 2026-11-12, excluding any bars inspected before the specification is frozen. Log every signal, cancellation, unfilled order, queue-dependent fill, fees and actual execution; compare daily net profit with the frozen strict prediction. Do not inspect rolling results and stop at the first significant win.

The estimates below are **dev / in-sample inputs and planning projections, not forward observations**. Two-sided α=.05, 80% power against zero: N ≈ [(1.960+0.842) σeffective/μ]², with σeffective = daily-cluster SE × √Ndev. Keep the current dev annual trade rate and variance; half-effect scenarios require four times as many trades. This assumes independent days, a stable distribution and a fixed single primary candidate. Positive serial correlation, multiple future candidates, missing fills and a smaller true edge require more data. It tests average net expectancy, not Combine pass probability.

| Dev inputs | Trades/year | Observed mean | N at mean | Years | N at half mean | Years |
| --- | --- | --- | --- | --- | --- | --- |
| all_touch | 100.0 | $32.64 | 461 | 4.6 | 1,842 | 18.4 |
| all_strict | 90.9 | $24.10 | 857 | 9.4 | 3,428 | 37.7 |
| nopd_touch | 73.2 | $39.69 | 310 | 4.2 | 1,238 | 16.9 |
| nopd_strict | 66.4 | $32.09 | 485 | 7.3 | 1,938 | 29.2 |

A holdout of roughly the stated two-year span is therefore too short for 80% power at the dev strict-fill edge. A practical fixed one-year paper review can reject bad execution assumptions and assess operational feasibility, but cannot certify this small edge. Calendar review dates should be fixed in advance; any interim safety stops must also be specified. Keep maximum drawdown, daily concentration and Combine feasibility as separate operational criteria. A positive dev t-statistic is no substitute for that evidence.

There is a credible path to **measuring** the frozen idea, with strict execution accounting and realistic costs. There is no demonstrated path from these dev edits to a robust improved strategy. Freeze the original all-5m specification as one primary forward experiment if continuing, retain nopd and these revisions as documented research rather than competing live selections, and spend effort on execution records instead of further optimisation.

Reproducibility: [audit.py](codex/audit.py), [run log](codex/run.log), [setup verification](codex/verify_setups.py), [setup checks](codex/dev_setup_checks.csv), [entry/exit checks](codex/dev_spot_checks.csv), [power inputs](codex/dev_power.csv), [execution accounting](codex/dev_execution_accounting.csv). Run from the repository root with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. .venv/bin/python studies/purple_levels_improve/codex/audit.py`, then `verify_setups.py` and `finish.py`; `write_report.py` renders this report. All generated trade and signal files are dev / in-sample and remain under `codex/`.
