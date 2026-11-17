# Independent CL strategy audit — dev / in-sample

**Verdict:** No tested change establishes a repeatable improvement. Keep `purple_levels_rth` frozen for its existing forward paper experiment; do not retune it or promote these dev results to a paid Combine. Other verdicts appear below. All performance and inference here are **dev / in-sample**, including the out-of-family check; planning estimates use selected dev effects.

Read-only inputs: required repository docs, the previous Purple study, ledger metadata and dev trades. No other researcher’s files in this study were read. Only `load_period("dev")` loaded bars: **3,983,238 bars / 2,976 CME days**, 2010-06-07–2021-12-31. No validation/holdout bars or trade lists, downloads, git, CLI tests, ledger changes, or production edits.

**Selection and units.** “Best” = highest total net; “median” = lower middle run by total net. Primary table keeps the latest ledger row per exact parameter dictionary (including fill mode), removing superseded code versions. Implicit/explicit defaults can remain duplicate dictionaries; they count conservatively. The table’s N is that dictionary count, **not independent trials**. It includes previously selected parameters and fill sensitivities. [Archive best/median](codex/archive_best_median.csv) separately retains literal historical hash selection; obsolete runs are not valid current candidates. Original risk was not recorded in those trade CSVs, so historical R is not identifiable without old signals. Current selected runs recover it from reproduced signals.

Net uses the repository’s $4.04 round-turn fee per contract and no exit slippage; strict fills change entry eligibility only. Gross ticks = gross dollars / ($10 × contracts), including partial legs. Gross R = gross dollars / (contracts × $10 × original **planned limit-to-stop ticks**); actual exit ticks never substitute for risk. Values below are mean ± **daily-cluster SE**, before fees. All dev days, including zero-trade days, enter clustering. One-sided positive-mean normal tests; 95% intervals are mean ± 1.96 SE. Days may still be serially dependent; selection and shared trades reduce the strength of this inference.

**1. Triage — dev / in-sample, best of N.**

| Strategy | N | Trades best / median | Best ticks ± SE | Best R ± SE | Median ticks ± SE | Median R ± SE | Best ticks BH / BY |
| --- | --- | --- | --- | --- | --- | --- | --- |
| xtley_gap | 6 | 6,341 / 1,931 | 0.421 ± 0.414 | 0.009 ± 0.024 | -0.259 ± 0.726 | -0.015 ± 0.022 | 0.367 / 1.000 |
| swapnil_momentum | 3 | 5,913 / 18,376 | -0.450 ± 0.704 | -0.009 ± 0.012 | -0.201 ± 0.269 | -0.002 ± 0.007 | 0.962 / 1.000 |
| swapnil_hm | 2 | 762 / 206 | 0.722 ± 3.402 | 0.013 ± 0.016 | -8.417 ± 6.889 | -0.013 ± 0.027 | 0.703 / 1.000 |
| ict_ea | 2 | 3,190 / 8,499 | -0.389 ± 0.151 | -0.034 ± 0.014 | -0.326 ± 0.093 | -0.024 ± 0.008 | 1.000 / 1.000 |
| scribd_supertrend | 2 | 15,418 / 14,955 | -0.088 ± 0.186 | -0.007 ± 0.008 | -0.836 ± 0.221 | -0.038 ± 0.008 | 0.920 / 1.000 |
| purple_pa | 2 | 542 / 589 | 3.061 ± 1.542 | 0.095 ± 0.040 | 2.706 ± 1.017 | 0.096 ± 0.040 | 0.084 / 0.586 |
| swing_point_failure | 15 | 2,399 / 7,352 | -0.738 ± 0.328 | -0.214 ± 0.051 | -0.357 ± 0.127 | -0.112 ± 0.023 | 1.000 / 1.000 |
| swing_point_failure_reversal | 8 | 6,410 / 6,520 | 0.139 ± 0.276 | -0.022 ± 0.033 | -0.273 ± 0.218 | -0.033 ± 0.032 | 0.601 / 1.000 |
| swing_point_manipulation | 21 | 1,437 / 1,174 | 0.779 ± 0.684 | 0.064 ± 0.065 | 0.018 ± 0.609 | -0.049 ± 0.065 | 0.322 / 1.000 |
| pd_swing | 10 | 72 / 4 | 1.778 ± 4.571 | 0.010 ± 0.109 | -9.500 ± 18.390 | 0.000 ± 0.500 | 0.641 / 1.000 |
| purple_levels | 16 | 1,157 / 542 | 3.668 ± 0.735 | 0.134 ± 0.029 | 3.061 ± 1.542 | 0.095 ± 0.040 | 3e-05 / 0.00021 |
| purple_levels_rth | 2 | 273 / 264 | 9.103 ± 1.924 | 0.256 ± 0.056 | 8.072 ± 1.978 | 0.220 ± 0.058 | 4.5e-05 / 0.00031 |

Only `purple_levels` and its frozen RTH successor retain positive gross-tick evidence at BY 5%; they are the same family, whose validation already failed. No unrelated family supplies a robust gross survivor. Normal SEs in very sparse bins are unreliable; zero empirical variance with two trades is not zero uncertainty.

Exploratory survivors were pre-declared as best gross-tick p<.05 before correction: `purple_pa`, `purple_levels`, `purple_levels_rth`. This is a screening rule, not proof. The correction table qualifies that screen. A positive estimate with an interval containing zero supplies no basis for optimizing a failed family; those receive only the mandatory out-of-family check.

**Multiplicity:** 665 evaluated statistic/portfolio/diagnostic/power cells; 603 finite inferential tests jointly corrected with BH and dependence-robust BY, including every unique historical hash’s gross ticks, both primary units, overlapping groups, contrasts and duplicate inputs. Undefined evaluated cells remain counted, with no p-value; empty decomposition bins are not tested. Details: [cell ledger](codex/cells.csv), [counts](codex/metadata.json), [pre-run declaration](codex/plan.md). This does **not** correct all earlier research (the prior Purple audit alone counted 276 cells; swing confluence examined thousands). Corrected dev significance does not establish an out-of-sample edge.

**2. Pre-declared out-of-family session check — dev / in-sample, best of each strategy’s N above.**

Exact declaration preceded calculations in [plan.md](codex/plan.md): one best canonical configuration per other family; independently replay **strict through1** entries; compare entry-time CT **08:30≤time<13:30** with all other times. Exclude `purple_levels`, its frozen successor and `purple_pa` because they share the originating mechanics. Primary: gross R mean difference. Secondary: net R difference and group means. Equal-strategy pooling uses day-aligned residual covariance, including shared-market exposure; it does not assume independent strategies. Each family keeps all original rules. Entry-time cohorts are descriptive, not executable session filters.

| Other strategy | Strict N RTH / other | Gross RTH R | Gross other R | Gross ΔR ± SE | BH / BY | Net ΔR ± SE |
| --- | --- | --- | --- | --- | --- | --- |
| xtley_gap | 1521 / 4581 | -0.063 | -0.074 | 0.011 ± 0.051 | 0.703 / 1.000 | 0.038 ± 0.051 |
| swapnil_momentum | 2355 / 3494 | -0.028 | -0.024 | -0.004 ± 0.022 | 0.843 / 1.000 | 0.004 ± 0.022 |
| swapnil_hm | 334 / 423 | 0.028 | -0.008 | 0.037 ± 0.032 | 0.317 / 1.000 | 0.037 ± 0.032 |
| ict_ea | 457 / 2546 | -0.106 | -0.124 | 0.018 ± 0.039 | 0.628 / 1.000 | 0.041 ± 0.040 |
| scribd_supertrend | 3822 / 10879 | 0.005 | -0.048 | 0.053 ± 0.017 | 0.005 / 0.036 | 0.059 ± 0.017 |
| swing_point_failure | 685 / 1683 | -0.204 | -0.403 | 0.199 ± 0.082 | 0.033 / 0.232 | 0.244 ± 0.082 |
| swing_point_failure_reversal | 1511 / 4810 | -0.084 | -0.141 | 0.056 ± 0.056 | 0.372 / 1.000 | 0.099 ± 0.057 |
| swing_point_manipulation | 250 / 1172 | 0.047 | 0.012 | 0.035 ± 0.145 | 0.701 / 1.000 | 0.052 ± 0.145 |
| pd_swing | 12 / 58 | 0.152 | -0.031 | 0.183 ± 0.269 | 0.514 / 1.000 | 0.190 ± 0.269 |

Equal-strategy pooled **gross_R** contrast: **0.065 ± 0.037**, 95% interval [-0.008, 0.138], BH 0.125, BY 0.872 (dev / in-sample).

Equal-strategy pooled **net_R** contrast: **0.085 ± 0.037**, 95% interval [0.012, 0.157], BH 0.045, BY 0.315 (dev / in-sample).

RTH is better in 8 of 9 gross contrasts, but the primary pooled gross test fails BH and BY. Only Supertrend’s individual gross contrast survives BY: its RTH gross mean is near zero and its RTH net mean remains negative. SPF’s positive contrast is less-negative trading, not positive expectancy. The pooled secondary net contrast passes BH but fails BY; smaller fee/R during busier hours can contribute. Thus the evidence suggests a general session cost/quality effect, **not** transferable profitable edge. Purple’s relatives cannot serve as independent replication; different strategies still share CL bars.

**3. Survivor decomposition — dev / in-sample, selected as above.** Fixed bins and all cells, including side, prior-day volatility and touch-only/traded-through fill-bar cohorts, are in [cells.csv](codex/cells.csv). The compact comparison below uses strict portfolios. Mean R includes every exit. The prior-day regime uses only completed day ranges and a trailing 60-day median (minimum 20); no future-day range or alternate swing definition.

| Survivor | Strict cohort | N | Net R ± SE | Net dollars |
| --- | --- | --- | --- | --- |
| purple_pa | session/RTH | 182 | 0.104 ± 0.065 | $7,985 |
| purple_pa | session/Asia | 144 | 0.193 ± 0.080 | $6,018 |
| purple_pa | session/London | 124 | -0.065 ± 0.089 | $-491 |
| purple_pa | session/Pre | 47 | -0.163 ± 0.144 | $-2,540 |
| purple_pa | session/Late | 19 | 0.066 ± 0.120 | $473 |
| purple_pa | stop_bin/<=8 | 9 | 0.529 ± 0.272 | $294 |
| purple_pa | stop_bin/9-16 | 76 | 0.113 ± 0.113 | $863 |
| purple_pa | stop_bin/>16 | 431 | 0.043 ± 0.045 | $10,289 |
| purple_pa | side/-1 | 276 | 0.100 ± 0.056 | $10,295 |
| purple_pa | side/1 | 240 | 0.019 ± 0.060 | $1,150 |
| purple_levels | session/RTH | 270 | 0.206 ± 0.057 | $21,259 |
| purple_levels | session/Asia | 420 | 0.001 ± 0.048 | $2,053 |
| purple_levels | session/London | 257 | -0.037 ± 0.062 | $582 |
| purple_levels | session/Pre | 77 | -0.030 ± 0.113 | $-211 |
| purple_levels | session/Late | 27 | 0.299 ± 0.096 | $1,651 |
| purple_levels | stop_bin/<=8 | 124 | -0.041 ± 0.091 | $-231 |
| purple_levels | stop_bin/9-16 | 380 | -0.004 ± 0.051 | $-195 |
| purple_levels | stop_bin/>16 | 547 | 0.108 ± 0.041 | $25,760 |
| purple_levels | side/-1 | 514 | 0.054 ± 0.044 | $12,363 |
| purple_levels | side/1 | 537 | 0.046 ± 0.042 | $12,971 |
| purple_levels_rth | session/RTH | 264 | 0.204 ± 0.058 | $20,243 |
| purple_levels_rth | stop_bin/<=8 | 2 | 0.949 ± 0.000 | $152 |
| purple_levels_rth | stop_bin/9-16 | 37 | -0.054 ± 0.164 | $-209 |
| purple_levels_rth | stop_bin/>16 | 225 | 0.240 ± 0.062 | $20,301 |
| purple_levels_rth | side/-1 | 134 | 0.136 ± 0.085 | $6,369 |
| purple_levels_rth | side/1 | 130 | 0.273 ± 0.079 | $13,875 |

| Survivor | Touch-only N / net R ± SE | Through fill-bar N / net R ± SE | Strict prior quiet N / net R ± SE | Strict prior large N / net R ± SE |
| --- | --- | --- | --- | --- |
| purple_pa | 186 / 0.157 ± 0.067 | 356 / 0.037 ± 0.050 | 268 / -0.00045 ± 0.057 | 243 / 0.137 ± 0.060 |
| purple_levels | 467 / 0.120 ± 0.045 | 690 / 0.094 ± 0.037 | 550 / 0.023 ± 0.041 | 494 / 0.078 ± 0.045 |
| purple_levels_rth | 74 / 0.124 ± 0.113 | 199 / 0.283 ± 0.064 | 134 / 0.157 ± 0.082 | 128 / 0.256 ± 0.082 |

The larger-prior-range cohort has higher strict net R in all three related portfolios, plausibly because enough range helps a 1R target finish before flattening. These are overlapping Purple trades, no between-regime contrast was tested, and there is no unrelated survivor: this is not independent replication. Side strength switches across these portfolios, and the small-stop cells are sparse, so neither supports a universal side/stop filter. `purple_pa` 15m also has positive Asia net R, contradicting a universal overnight≈0 claim. Its RTH filter removes profitable overnight trades.

A touch-run fill bar that trades through is not the strict strategy: waiting for a deeper print can delay fills, change exits and block later orders. Strict portfolios above were replayed in the engine, not made by dropping touch-only trades. Neither those cohorts nor the stop bins justify new thresholds. Prior studies show bare fixed-level touches are near their geometric fair rate; the gap already records departure, so its bounce association is partly circular.

**4. One proposed change, one parameter value — dev check rejected.** `purple_pa` only, keeping its pre-selected best timeframe and all other parameters: signals decided at CT 08:30≤close<13:30, cap order expiry at 13:30, retain original position exits and overnight setup history. Reason fixed before this check: watched levels and greater regular-session participation may improve the liquidity supplied on pullbacks. This window came from earlier Purple dev research, so this is mechanism-informed family selection, **not** an independent discovery. No window grid, combined filters, or new `purple_levels`/`purple_levels_rth` variant.

| Change fill model | New trades | Original net | Changed net | Paired total Δ | Daily Δ$ ± SE | 95% interval | BH / BY | New PF |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RTH_through0 | 183 | $14,400 | $9,401 | $-5,000 | -1.68 ± 1.89 | [-5.38, 2.02] | 1.000 / 1.000 | 1.309 |
| RTH_through1 | 178 | $11,445 | $8,041 | $-3,404 | -1.14 ± 1.81 | [-4.69, 2.40] | 0.962 / 1.000 | 1.265 |

The revision lowers total net by $5,000 touch / $3,404 strict (dev / in-sample), with no paired improvement. Paired daily differences include every dev trading day, not only days the revision trades. A higher conditional mean/PF with fewer trades does not itself improve earning rate. No production change is recommended on these selected dev comparisons; artifacts preserve the tested specification and its paired daily series.

**5. What can judge this, power, and verdicts.** The ledger records validation only for `purple_levels` (12 rows, including execution sensitivities and bug-fix replays), with failed all/nopd strict validation documented in its README. Every listed strategy has zero holdout ledger rows. This is repository usage, not virgin data: protocol says the owner researched every year through 2026 before reset. Related Purple strategies inherit shared validation exposure; a new name or filter does not restore it. The level-regime study also used dev+validation; its findings were read as required, without loading those data. Only observations after a genuine freeze, not already inspected, plus paper execution logs can provide clean evidence.

| Strategy | Dev rows / hashes | Validation / holdout rows | Best strict net R ± SE | N / years at dev effect | Verdict |
| --- | --- | --- | --- | --- | --- |
| xtley_gap | 18 / 18 | 0 / 0 | -0.110 ± 0.024 | — (μ≤0) | drop; no established gross edge |
| swapnil_momentum | 9 / 9 | 0 / 0 | -0.037 ± 0.012 | — (μ≤0) | drop; no established gross edge |
| swapnil_hm | 8 / 8 | 0 / 0 | 0.006 ± 0.016 | 45,792 / 699.7y | drop; no established gross edge |
| ict_ea | 6 / 6 | 0 / 0 | -0.176 ± 0.014 | — (μ≤0) | drop; no established gross edge |
| scribd_supertrend | 10 / 8 | 0 / 0 | -0.053 ± 0.008 | — (μ≤0) | drop; no established gross edge |
| purple_pa | 12 / 10 | 0 / 0 | 0.062 ± 0.041 | 1,785 / 40.0y | drop as separate candidate; no extra Purple selection |
| swing_point_failure | 27 / 27 | 0 / 0 | -0.444 ± 0.039 | — (μ≤0) | drop; no established gross edge |
| swing_point_failure_reversal | 20 / 17 | 0 / 0 | -0.203 ± 0.027 | — (μ≤0) | drop; no established gross edge |
| swing_point_manipulation | 42 / 42 | 0 / 0 | -0.025 ± 0.064 | — (μ≤0) | drop; no established gross edge |
| pd_swing | 80 / 60 | 0 / 0 | -0.014 ± 0.112 | — (μ≤0) | drop; sparse, no established gross edge |
| purple_levels | 49 / 49 | 12 / 0 | 0.050 ± 0.031 | 3,087 / 34.0y | drop; failed validation; preserve holdout |
| purple_levels_rth | 4 / 4 | 0 / 0 | 0.204 ± 0.058 | 167 / 7.3y | freeze for forward; existing paper plan only |

Power is a planning calculation, not a forecast: two-sided 5%, 80% power, N≈(2.802×daily-cluster SE/selected mean)²×dev N. Calendar years use the observed dev trade rate. No positive selected net mean means no finite sample target to establish that same effect as positive. At half the selected effect, required N/years quadruple; parameter selection, regime change, serial dependence and execution uncertainty can increase them further. Sparse positive `pd_swing` estimates are especially unreliable. A year of frozen RTH paper trading is primarily an execution check; it cannot certify a repeatable edge or Combine feasibility. Existing frozen RTH cost/pass already misses the repository gate; this audit makes no new Combine probability claim.

**Verification and reproduction.** All 72 deterministic first/middle/last touch/strict raw-bar checks passed; BH/BY and paired daily SEs were independently recomputed ([verification log](codex/verify.log)). 24/24 selected best/median replays match ledger trade count, signal/entry/exit bars, side, size, prices, gross and net. [Replay checks](codex/replay_checks.csv), [raw-bar entry/exit spot checks](codex/verification_spot_checks.csv), [selection hashes/parameters](codex/selections.json), best dev trade/signal files and strict trade files are under `codex/`. Spot checks verify selected entries against limit/strict reach and raw exits; they are not a full independent signal audit or proof of queue fills. Swing strategies use production `swing_state` only, point-in-time. No new swing logic was introduced.

Reproduce from repo root: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. .venv/bin/python studies/all_strategies_improve/codex/run.py`, then `.../codex/verify.py` and `.../codex/report.py` with the same interpreter/environment. The first invocation stopped at strict replay because a fresh managed strategy lacked signal-initialized state; `run.py` is corrected, and [resume.py](codex/resume.py) continued saved triage without new parameter choices. Both logs are retained; repeated calculations are not additional selected cells.
