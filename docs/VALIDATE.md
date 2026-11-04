# Validate (feature 3): does the feature-2 result survive its own selection?

> **Execution update — 3 November 2026.** New runs use limit entries and commission only, with no
> added slippage and no 1- or 2-tick stress scenarios. Fair Price Reversal and Supertrend + Kalman place
> the limit at the signal/decision close, active from the next bar. A waiting entry is cancelled when
> the planned TP has been reached and it is still unfilled at the one-minute close. Existing session
> boundaries still cancel waiting orders; Tupa Trade retains its stop-limit trigger and swing invalidation.
> Limit fills can be at the limit or better. Stops and forced closes retain their existing order types.
> Historical reports, configurations and ledger entries are retained; they are not results of these new rules.


Roadmap (owner, 2026-10-31): feature 1 = test, feature 2 = optimize, **feature 3 = validation A** (this file,
development interval only), feature 4 = Topstep 50K prop-challenge layer, feature 5 = one final check of the frozen
package (strategy + prop policy) on the reserved 2024+ interval.

Feature 3 never reads a bar at or after **2024-01-01 00:00 UTC** (`experiment.dev_bars()`, tested). It asks two
questions about each feature-2 candidate, with a separate verdict for each:

1. **Procedure.** Would the feature-2 search, run blind year after year, have picked configurations that made
   money in the following year? (walk-forward re-selection, CSCV / probability of backtest overfitting)
2. **Candidate.** Is the frozen candidate's Sharpe ratio larger than the best of its search would show by luck?
   (deflated Sharpe ratio)

Reviewed with Codex before it was built (`docs/REVIEWS.md`, R12, two rounds).

> **What feature 3 cannot show.** Every candidate's base parameters were picked by feature 1 on 2010-2026, and its
> filters, features and the decision to take it forward used the whole development interval. A 2014 fold
> therefore tests configurations built with later information. Feature 3 is **retrospective robustness,
> conditional on the frozen feature-2 search universe**, not out-of-sample evidence. "Out-of-sample" below only
> means "after the fold's own training cutoff".

## The search universe
Each candidate came from an E2 search: `filters` space, random sampler, seed 1, 200 trials, objective `net0`,
300+ closed trades in the baseline. The random sampler draws its 200 configurations from the seed alone, before any
data is read. So "run the E2 search on a training window" = "pick the best of the same 200 configurations on that
window", without drawing again. The 200 configurations are read from the search's `trials.csv` (sorted by its
`trial` column, not its ranked row order).

## Step 1: the matrix (200 engine runs per candidate)
Each of the 200 configurations runs on the development bars once without added slippage. From each run:
- **Daily marked-to-market equity**: at the last bar of every UTC date that has bars, initial capital + closed
  profit + open P&L of a position still open, at that bar's close, entry commission included (the same marking as
  TradingView's open P&L and as `metrics._monthly_returns`). Days without trades keep their value (true zeros in
  the daily P&L, never dropped).
- Closed trades per day (exit date), for the trade minimum.

Check before any statistic: every configuration's last equity - capital = its `trials.csv` net + open P&L, and its
closed trades = its trade count, in all three scenarios (tolerance 1e-6 USD). A mismatch stops the run.

Prefix invariance makes the matrix a valid record of every earlier cutoff: indicators use only past bars (tested
in feature 2) and each strategy keeps state only from its own entries, so equity at the end of day d of the full
run = equity of a run on the bars up to day d **with the development set's roll flags** (a rebuilt prefix would
mark its last bar as no roll and skip a real roll exit there; fold runs therefore keep the full flags).

## Step 2: walk-forward re-selection (primary: anchored)
- Folds: test years 2014 .. 2023 (UTC). Training window for fold Y: first development bar .. Y-01-01.
- **Selection = the E2 rule at the cutoff**: objective = equity at the last day-end before Y-01-01 - capital, at
  baseline costs (closed profit + open P&L, as `net0`). Eligible: closed trades before the cutoff >=
  ceil(300 x training days / development days) (days = UTC dates with bars). Highest objective wins; ties: higher
  profit factor of the window's closed trades (no losing trade ranks above any number, no trade = -1), then lower
  trial number, as E2. **No eligible configuration: the fold is in cash (0 USD) and counted.**
- **Fold result = an executable run**, not stitched trades: the chosen configuration runs on the development bars
  up to Y+1-01-01 (indicators computed over all of them, so no warm-up reset), starting **flat** at the first bar
  of year Y (`engine.run(..., start=i)`), with the development set's roll flags. Starting flat is the fold policy
  (a fresh account), not a claim that it equals continuous trading: a position of the full run can cross
  1 January (missing bars can delay a session exit), so each fold also shows the same configuration's full-run
  slice and the report gives the total difference. A position still open at the fold end is
  valued as a market close at the last bar's close: open P&L minus exit commission and the scenario's slippage.
  Run the baseline only (selection uses net0).
- Report per fold: chosen configuration, its training objective, baseline fold result, trades. Totals: sum of
  fold results per scenario, positive folds, and walk-forward efficiency = (mean fold result in the baseline) / (mean of
  the chosen configurations' training objective per training year); "n/a" when the denominator is not positive.
- Sensitivity (declared, cannot rescue a failure): rolling 4-year training window (Y-4-01-01 .. Y-01-01; the
  window's equity change, trades closed inside it, same minimum scaled to its days).
- Reference only (in-sample): the frozen candidate's own result in each test year.

## Step 3: CSCV / probability of backtest overfitting (Bailey, Borwein, Lopez de Prado, Zhu 2015)
A search-overfitting diagnostic, **not** chronological validation (an in-sample half can hold 2023 and its other
half 2014; the 12,870 splits overlap heavily and are not independent).
- Daily P&L matrix in the baseline (day-to-day change of marked equity), 200 configurations x development days.
- S = 16 contiguous blocks of equal day count (the first `days mod 16` blocks get one more day). All C(16, 8) =
  12,870 splits into in-sample (IS) / out-of-sample (OOS) halves. No purge (trades are intraday; a trade crossing a
  block join is marked to market at day ends, so each block holds its own P&L).
- Per split: IS winner = highest IS net among configurations with IS closed trades >= ceil(300 x IS days /
  development days); ties: higher IS profit factor, then lower trial number. No eligible configuration: the split is skipped and counted.
  OOS rank of the winner among **all 200** by OOS net: ascending, 1 = worst, ties get the average rank; relative
  rank w = rank / (N + 1), logit = ln(w / (1 - w)). **PBO = share of splits with logit <= 0.**
- Also reported: P(winner's OOS net < 0), the median logit, the degradation slope (least squares of OOS net on IS
  net of the winners, intercept shown), the number of identical-path configurations (same daily P&L vector), and a
  sensitivity ranking only among eligible configurations, and under the historical 2-tick rules.

## Step 4: deflated Sharpe ratio of the frozen candidate (Bailey & Lopez de Prado 2014)
- Returns: daily marked-to-market P&L / 50,000 (fixed-capital returns, no compounding, no risk-free rate: the
  margin is not an invested cash balance). Every development day counts, idle days are zeros.
- SR = mean / sample standard deviation (ddof 1), per day, not annualized. Skewness g3 (biased moment estimator)
  and Pearson kurtosis g4 (not excess; normal = 3) of the candidate's daily returns; T = days.
- Trial population (paired, primary): the 200 E2 configurations. V = variance (ddof 1) of their daily SRs at the
  same scenario (configurations with zero variance excluded and counted), N = 200.
  SR0 = sqrt(V) x ((1 - gamma) x Z^-1(1 - 1/N) + gamma x Z^-1(1 - 1/(N e))), gamma = Euler-Mascheroni.
  DSR = Phi((SR - SR0) x sqrt(T - 1) / sqrt(1 - g3 SR + (g4 - 1) / 4 x SR^2)).
- Sensitivity, labelled as an assumption (the variance of those configurations was not measured here): the same
  V with N = every distinct configuration the variant saw (feature-1 grid + E2 + E3 non-duplicates + neighbours),
  and with N = every distinct configuration of the strategy (all variants). Also: monthly returns and a
  90% stationary block bootstrap interval of the daily SR (mean block 20 days, 2,000 resamples, seed 0), because
  serial dependence is not handled by the formula.
- The formula is an approximation (independent, identically distributed returns). Undefined (zero variance, a
  negative value under the square root): the candidate fails.

## Trial and work accounting
The ledger keeps counting **engine runs** (`evaluations`). Feature 3 logs before running: `validate_matrix`
(200 runs), `validate_folds` (fold runs). Distinct configurations, search trials and the paired trial population
are separate numbers in each report; engine runs are never used as N.

## Verdict rules (fixed before any feature-3 run, the same for every candidate)
| Verdict | Passes only if all hold (baseline, commission included) |
|---|---|
| **Procedure** | anchored walk-forward: sum of baseline fold results > 0; at least 7 of 10 folds > 0; PBO <= 0.5 |
| **Candidate** | DSR >= 0.95, paired population (N = 200) |
| **Advance to feature 4** | both verdicts pass |

- A sensitivity never turns a fail into a pass. An undefined primary number is a fail.
- No substitution after looking: a failed candidate is not replaced by another search winner (NY E3, `risk_atr`)
  or re-tuned. A new idea needs its own dated budget in a lab notebook and starts at feature 2.
- 7 of 10 positive folds would happen about 17% of the time by coin flips; the rule is an advancement gate, not
  proof. Passing feature 3 does not show a tradable edge.

## Files
| Path | What |
|---|---|
| `docs/strategies/<strategy>/validate/README.md` | lab notebook: protocol (before runs), results, verdict |
| `docs/strategies/<strategy>/validate/<tag>.md` + `.png` | report of one candidate (generated) |
| `results/<strategy>/validate/<tag>/` | `matrix.npz` (daily equity + trades), `folds.csv`, `folds_rolling.csv`, `pbo.json`, `dsr.json`, `run.json` (hashes of code, data, trials.csv, config, this file) |

## Command
```bash
.venv/bin/python -m tvtester.cli validate strategies/configs/<candidate>.json --jobs 4
```
A tag is run once; an existing output folder stops the command.

## Revised execution basis

The 3 November 2026 limit-entry revision replaces the previous cost-scenario gate. New validation uses only
net0, with one baseline walk-forward profit check, 7 positive folds, PBO <= 0.5 and DSR >= 0.95. No 1- or
2-tick sensitivities are run. Rolling training-window, eligible-only PBO, broader trial-population and monthly
DSR sensitivities remain. The original published verdicts belong to the previous execution rules.
