# FSP v2 — Feature 2 lab notebook

## Run 1: rule-interpretation grid (declared 2026-11-12, before any trial ran)

**Why.** The FSP v1 owner specification ([../../failed_swing_point/README.md](../../failed_swing_point/README.md)) leaves four cases open; v2 ([../README.md](../README.md)) makes them switches. The owner did not
choose, and asked for every combination to be tested. Picking a rule reading by its result is selection, the
same as a parameter search, so this is a Feature 2 run and is labelled that way.

| Rule | Off (`False`) | On (`True`) | Feature 1 default |
|---|---|---|---|
| A `burn_invalid_first` | first MSS with no stop anchor or risk ≤ 0 is skipped; the setup waits for a later MSS | that MSS uses up the setup | off |
| B `stop_search` | latest extreme fails the left-neighbour check → no signal | take the next most extreme price that passes (later wins ties) | off |
| C `breach_minute_hl` | HL/LH must form after the breach minute | HL/LH on the breach minute itself is allowed | on |
| D `offhours_setups` | only failures whose minute is inside the NY signal window (09:00–14:30 ET) create setups | failures at any hour create setups (still reset at 14:30) | on |

**Hypothesis.** None of the 16 readings turns the baseline (net −$11,926, PF 0.958, development interval)
into a positive-expectancy strategy. The spread between readings shows how much the result depends on these
unwritten choices.

**Fixed:** 1H setup, 15m confirmation, max risk 25 ticks, TP 50 ticks, NY entries, $2.01/order, 1 contract,
no added slippage, development interval (bars before 2024-01-01 UTC).

**Objective:** `net0` (net profit plus open P&L at the end). Ties: profit factor, then trial number.
**Minimum:** 300 closed trades. **Budget:** exactly 16 engine runs, a full 2×2×2×2 grid; trial 0 is the
Feature 1 default (A off, B off, C on, D on). There are no neighbour runs, because every neighbour is already in the grid.
**Wording:** any winner is in-sample, best of 16 evaluations, development interval. It is not a validated edge.

Runner: `.venv/bin/python tools/run_limited.py tools/fsp_v2_rule_grid.py`. (Run 1 itself ran as `tools/fsp_rule_grid.py` on the FSP module before the v2 rename, with the same logic; see the ledger lineage note.)

### Result (2026-11-12): hypothesis holds, no setting is profitable

Full table: [search_rules_grid_net0_n16.md](search_rules_grid_net0_n16.md). 16 engine runs, all 16 eligible (≥ 300 trades).
Trial 0 reproduced v1 exactly. Peak memory 1.35 GiB.

| Effect (other switches averaged) | net0 change | Reading |
|---|---|---|
| **D off** (NY-hour setups only) | +$5,650 to +$7,500 | the largest effect, but mainly fewer trades (about 1,700–1,900 vs 2,800–3,200), so less commission and fewer losers; PF only 0.958 → 0.974 |
| **A on** (invalid first MSS uses up the setup) | +$1,000 to +$2,600 | fewer trades again |
| **B on** (stop search) | about −$200 to −$1,000 | slightly worse |
| **C** | $0 | no effect; identical trades (see [../README.md](../README.md)) |

Best: trial 8 (A on, B off, C off, D off; trial 10 is identical), **net0 −$3,659.58, 1,679 trades, PF 0.974, win 19.1%,
max DD $19,006. In-sample, best of 16 evaluations, development interval.** Long −$4,397, short +$737. Every
setting loses, and the best gets closer to zero mostly by trading less. **Verdict: no candidate.** Nothing is frozen and
nothing goes to feature 3. The owner can still pick A/B/D on rule meaning; the result doesn't decide them.
