# Tupa Trade v2: feature 2 lab notebook

Protocol: [`docs/OPTIMIZE.md`](../../../OPTIMIZE.md). Development interval only (bars before 2024-01-01 UTC).
2024 onward is reserved (previously exposed, not clean out-of-sample).

## Study 1: interpretation grid (declared 2026-11-12, before any run)

**Why.** v1 ([owner spec README](../../tupa_trade/README.md) sections 3c/3d) contains six choices Claude made where the owner has no rule yet. The owner
was asked and is not sure of the answers (2026-11-12), and asked to test every combination, named Tupa Trade v2. This study measures
how much each open choice changes the in-sample result. It cannot tell which choice is the owner's discretion;
only more owner walkthroughs can.

**Hypothesis.** At least one interpretation turns v1's loss into a positive `net0` on the development interval.
If true, it must also show up as a *consistent* effect of that switch across the other combinations (main-effect
table), not only in the single best configuration. Prior expectation: unlikely; every v1 combination lost.

**Space** (`SPACES["interpretation"]` in `strategies/tupa_trade_v2.py`; first value = v1):

| Open choice | Values | Meaning of the alternative |
|---|---|---|
| #1 lowest timeframe allowed as T | `t_min` 15m / 1h / 4h / 1d | unchanged from feature 1 |
| #1 which candidate timeframe is T | `t_rule` lowest / **highest** | the highest timeframe (from `t_min` to daily) whose newest swing is a candidate |
| #2 trend persistence | `trend` sticky / **fresh** | a timeframe's down trend is cleared when it accepts its next swing high after the break (long mirror); set again only by a new touch |
| #3 break point already touched | `touched` skip / **retest** | arm the order anyway; with the close through the break point it is a plain limit waiting for a return |
| #4 order before the trigger | `order` follow / **freeze** | kept from placement until the next 1m swing high (long: low), the planned TP, the session end or a fill; bias loss does not cancel it |
| #5 unfilled order at planned TP | `tp_expiry` on / **off** | keep the order after the planned TP is reached |
| #6 session timing | not searched | owner rule (NY 09:00-14:30) |

`t_min = 1d` with `t_rule = highest` is excluded: only the daily can be T, so it equals `lowest`.
**Budget: 112 configurations** (7 x 16), exhaustive `grid` sampler, one engine run each, plus the winner's
neighbours. Fixed: TP 25 ticks, max risk 25 ticks, $2.01 per order, no added slippage.

**Objective:** `net0` (net profit plus open P&L, no added slippage). Minimum 300 closed trades.
**Baseline (trial 0):** the feature-1 top combination under the current owner swings, all switches at v1.

**Decision rule, declared now.** Report the winner as "in-sample, best of 112 (+ neighbours), development
interval". It is a feature-3 candidate only if (a) `net0` > 0 with >= 300 trades, and (b) its neighbours are
not a collapse (median neighbour above zero). A switch is reported as a consistent effect only if its
alternative improves `net0` in at least 75% of the paired configurations (all other switches equal).
No rule enters the owner's spec from this study without the owner's confirmation.

## Results (run 2026-11-12, `search_ny_interpretation_grid_net0_s1_n112`)

> **In-sample, development interval, best of 112 + 7 neighbours (119 engine runs).** No tradable edge shown.

[Search report](search_ny_interpretation_grid_net0_s1_n112.md). Feature 1 baseline first ([results.md](../results.md),
all bars, switches at v1): top `t_min=1d`, -$11,212.56, 528 trades, best of 4.

| | Configuration | net0 | Trades | Avg trade | PF |
|---|---|---|---|---|---|
| Baseline (trial 0) | v1, `t_min=1d` | -$9,262.62 | 431 | -$21.49 | 0.771 |
| Winner (trial 94) | `t_min=4h`, highest, fresh, retest, TP expiry off | -$1,956.10 | 305 | -$6.41 | 0.923 |

- **Eligible trials: 96 of 112. Above zero: 0.** Two trials are positive (+$231.72 with 114 trades, +$22.68
  with 166 trades), both below the 300-trade minimum: noise, not eligible.
- Neighbours: 0 of 7 above zero, median -$2,798.06.
- **Decision rule: no feature-3 candidate.** Condition (a), `net0` > 0, fails.

Paired effect of each switch (all other switches equal; `tools/tupa_v2_effects.py`):

| Alternative | Pairs | net0 better | Median net0 change | Avg trade better | Median avg-trade change | Reading |
|---|---|---|---|---|---|---|
| `t_rule=highest` | 48 | 42 (88%) | +$2,854 | 23 (48%) | -$0.08 | fewer trades only (median -627); no per-trade effect |
| `trend=fresh` | 56 | 52 (93%) | +$15,399 | 45 (80%) | +$5.64 | consistent: fewer trades **and** better per trade |
| `touched=retest` | 56 | 35 (63%) | +$911 | 49 (88%) | +$5.69 | better per trade, more trades; below the 75% net0 bar |
| `order=freeze` | 56 | 14 (25%) | -$1,717 | 23 (41%) | -$0.70 | worse: v1 "follow" kept |
| `tp_expiry=off` | 56 | 27 (48%) | -$41 | 28 (50%) | +$0.01 | no effect |

Across the eligible trials the average trade ranges from -$25.43 to -$1.81. **Every eligible interpretation
loses per trade.** By the declared 75% rule, `trend=fresh` (93%) and `t_rule=highest` (88%) are consistent
net0 effects, but `highest` only removes trades from a losing strategy. `fresh` and `retest` cut the per-trade
loss by about $5.6 each; neither brings it above zero. These are in-sample patterns, not owner rules.

**Verdict.** The open interpretation choices do not explain the lack of edge. The gap between v1 and the
owner's discretion is more likely in the uncoded parts (README 4c: anticipated swing locations; answer 9:
daily decides; weekly context). Codex review and replication of this search: pending.
