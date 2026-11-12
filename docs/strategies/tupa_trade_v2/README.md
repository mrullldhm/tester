# Tupa Trade v2

Created 2026-11-12 at the owner's request. **v2 = Tupa Trade v1 plus five switches** for the choices Claude
made where the owner has no rule yet (v1 README section 3d). The owner's spec is unchanged and stays in
[`../tupa_trade/README.md`](../tupa_trade/README.md). v1 (`strategies/tupa_trade.py`) is untouched.

| Switch | v1 value (default) | Alternative | Open choice |
|---|---|---|---|
| `t_rule` | lowest | highest | which timeframe with a candidate swing is T |
| `trend` | sticky | fresh | how long a timeframe's down (up) trend counts |
| `touched` | skip | retest | MSS whose break point was already touched |
| `order` | follow | freeze | the order before its trigger |
| `tp_expiry` | on | off | unfilled order once the planned TP is reached |

Exact definitions: [optimize/README.md](optimize/README.md) (study 1) and the docstring of
`strategies/tupa_trade_v2.py`. None of the alternatives is an owner rule.

Files: `strategies/tupa_trade_v2.py`, Pine twin `strategies/tupa_trade_v2.pine` (five extra inputs),
literal transcription `tests/tupa_v2_literal.py`, tests `tests/test_tupa_trade_v2.py`.

Checks (2026-11-12, pytest): with every switch at v1, v2 equals v1 trade for trade and bias for bias on
synthetic bars (all four `t_min`); every switch case equals the literal Pine transcription; each switch changes
at least one trade. Not checked: TradingView compilation or a TradingView export of either twin.

The `fresh` trend lives in the shared `tvtester/swings.py` (`TfState.fresh`); v1 does not read it.

Results: feature 1 with switches at v1 in [results.md](results.md) (= v1 under the current owner swings);
feature 2 study in [optimize/](optimize/README.md): 112 interpretations, **none profitable** in-sample
(best -$1,956.10, 305 trades, development interval).

**Known issue (pre-existing, not from v2):** since the 10-11 November owner swing rules (provisional swing
removed when touched), v1 and v2 no longer take the owner's 26 Oct 2026 short. The 1m swing high 100.91
(22:20 MYT) is removed by the 22:22 high 100.93, so the HL becomes 100.75 (22:18) instead of the owner's
100.76 (22:22). Price reaches 100.76 at 22:32 but 100.75 only at 22:33, falling to 100.50 without returning to
the 100.77 limit: no fill. `tests/test_tupa_trade.py::test_owner_trade_26_oct_2026` fails on HEAD. Owner to
decide which reading is right.
