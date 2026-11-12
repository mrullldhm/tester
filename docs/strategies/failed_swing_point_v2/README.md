# FSP v2 — Failed Swing Point v2

FSP v2 is **FSP v1** ([../failed_swing_point/README.md](../failed_swing_point/README.md)) with four switches
for the cases the v1 owner specification leaves open. Every other rule is the v1 rule: CL1! only, one contract,
1H provisional-swing failure, 15m confirmation, first valid 1m MSS, 25-tick maximum planned risk, 50-tick TP from fill,
New York entries 09:00–14:30 ET, $2.01 per order. With every switch at its default, v2 is v1 trade for trade
(grid trial 0: 3,198 trades, −$11,925.96, identical to `first_default_first_mss_halt_2023`).

Code: `strategies/failed_swing_point_v2.py`. Tests: `tests/test_fsp_v2.py` (unittest). Runner:
`tools/fsp_v2_rule_grid.py`. v1 (`strategies/failed_swing_point.py`) is unchanged.

| Switch | Default (= v1) | Other setting |
|---|---|---|
| **A** `burn_invalid_first` | `False`: the first MSS with no valid stop anchor, or with risk ≤ 0, is skipped, and the setup waits for a later MSS | `True`: that MSS uses up the setup; no order, no later MSS |
| **B** `stop_search` | `False`: if the most extreme post-structure price fails the left-neighbour check, there is no signal | `True`: try the next most extreme price that passes (the later bar wins ties) |
| **C** `breach_minute_hl` | `True`: an HL/LH on the breach minute itself is eligible | `False`: the HL/LH must form after the breach minute |
| **D** `offhours_setups` | `True`: failures at any hour create setups (they still reset at 14:30 ET) | `False`: only failures whose minute is inside the NY signal window create setups |

**C has no effect.** All 8 C pairs in the grid gave byte-identical trade lists. For a short, the breach minute
has just broken the 1H swing low, so its low is a lower low and cannot be an HL (the long case mirrors this).
The switch is kept only so the grid stays complete.

## Status

The feature 2 grid of all 16 settings ([optimize/README.md](optimize/README.md)) found no profitable setting. The best
is −$3,659.58 (A on, B off, D off), **in-sample, best of 16, development interval**. No Pine twin exists yet,
and Codex has not replicated v2.
