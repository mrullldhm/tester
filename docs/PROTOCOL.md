# Research protocol

Goal: find an intraday CL strategy that passes the Topstep 50K Combine consistently and keeps passing on data it
was not built on. The protocol exists to stop curve-fitting: with enough tries, something always looks good
in-sample.

## Periods (`cltester/config.py`, by CME trading day, end exclusive)

Periods are cut on `trading_day`, never mid-session. Any `test` period that overlaps holdout (`holdout`, `all`)
needs the holdout guard.

| Period | Range | Use |
|---|---|---|
| dev | 2010-06 to 2021-12 | build and tune. Unlimited looks, but every run is logged |
| validation | 2022 to 2024 | frozen parameters, one run per candidate. No tuning after looking |
| holdout | 2025 to 2026-11-12 | once per strategy (the CLI refuses a second run without `--unlock`) |
| forward | after 2026-11-12 | new bars only, then paper/live on TopstepX |

Honesty note: before the 2026-11-12 reset the owner had already researched every year up to 2026. Validation and
holdout are therefore "not used in this repo", not truly unseen. Only **forward** is clean.

## Stages

1. **Hypothesis first.** Before any run, write `docs/strategies/<name>/README.md`: the idea, why CL should behave
   that way, exact entry/exit rules, parameters, the trial budget (how many combinations will be tried) and the pass
   criteria. Template: `docs/strategies/TEMPLATE.md`.
2. **Dev.** `python -m cltester.cli test <name> --period dev`. Tune within the declared budget.
3. **Robustness on dev.** Neighbouring parameters must also be profitable;
   positive in most years; not carried by a few days.
4. **Validation.** Frozen parameters, one run. Record the result whatever it is.
5. **Holdout.** Once. A fail ends the candidate (a new idea is a new strategy, not a retune).
6. **Forward.** New bars and paper trading on TopstepX before real money.

## Proposed gates (owner may change)

| Gate | dev | validation |
|---|---|---|
| Trades | ≥ 200 | ≥ 60 |
| Profit factor (net) | ≥ 1.25 | ≥ 1.10 |
| Years positive | ≥ 70% | — |
| Combine rolling pass rate | ≥ 50% of finished attempts | ≥ 40% |
| Sequential cost per pass | ≤ $500 | ≤ $750 |

## Reporting rules

- Every `test` run appends to `results/ledger.csv` (strategy, code+params hash, period, fills, key stats).
  Never delete ledger rows.
- Every reported number says its period and **in-sample**, and for tuned results **best of N** (N from the ledger).
- Fills follow docs/ENGINE.md (touch fills, no exit slippage). Never call fees "slippage" or slippage "commission".
- A result is not real until the trade list has been spot-checked against raw bars.
