"""Tupa Trade v2: v1 plus five interpretation switches (docs/strategies/tupa_trade_v2/optimize/README.md).

- All switches at v1 = Tupa Trade v1 trade for trade (and the same bias).
- Every switch combination tested here: the vectorized strategy equals the literal bar-by-bar transcription of the
  Pine twin (tests/tupa_v2_literal.py) on synthetic CL-like bars; each switch changes at least one trade.
"""

import numpy as np
import pytest

from strategies.tupa_trade import TupaTrade
from strategies.tupa_trade import bias as bias_v1
from strategies.tupa_trade_v2 import SWITCHES, T_CHOICES, TupaTradeV2, bias
from tests.test_tupa_trade import synthetic, trade_rows
from tests.tupa_v2_literal import LiteralTupaV2
from tvtester import swings as sw
from tvtester.data import Bars
from tvtester.engine import run


@pytest.mark.parametrize("seed", [0, 1, 2])
@pytest.mark.parametrize("t_min", T_CHOICES)
def test_v2_defaults_equal_v1(seed, t_min):
    bars = synthetic(seed=seed)
    np.testing.assert_array_equal(bias(bars, t_min), bias_v1(bars, t_min))
    assert run(TupaTradeV2(t_min=t_min), bars).trades == run(TupaTrade(t_min=t_min), bars).trades


@pytest.mark.parametrize("seed", [0, 1])
@pytest.mark.parametrize("t_min", T_CHOICES)
def test_v2_defaults_match_literal(seed, t_min):
    bars = synthetic(seed=seed, halt_bars=seed == 1)
    lit = LiteralTupaV2(t_min=t_min)
    a = run(TupaTradeV2(t_min=t_min), bars)
    b = run(lit, Bars(bars.ts, bars.t_ms, bars.o, bars.h, bars.l, bars.c, bars.volume, bars.raw_symbol,
                      bars.last_of_contract))
    np.testing.assert_array_equal(bias(bars, t_min), lit.bias_log)
    assert trade_rows(a) == trade_rows(b)


# --- feature-2 interpretation switches (docs/strategies/tupa_trade/optimize/README.md) ----------------------

V1 = {k: v[0] for k, v in SWITCHES.items()}
ALT = {k: v[1] for k, v in SWITCHES.items()}
SWITCH_CASES = [{k: ALT[k]} for k in SWITCHES] + [ALT]


def _plain(bars):
    return Bars(bars.ts, bars.t_ms, bars.o, bars.h, bars.l, bars.c, bars.volume, bars.raw_symbol, bars.last_of_contract)


@pytest.mark.parametrize("seed", [0, 1])
@pytest.mark.parametrize("t_min", ["15m", "1h", "4h"])
@pytest.mark.parametrize("sel", SWITCH_CASES, ids=lambda d: ",".join(f"{k}={v}" for k, v in d.items()))
def test_switches_match_literal_transcription(seed, t_min, sel):
    bars = synthetic(seed=seed)
    lit = LiteralTupaV2(t_min=t_min, **sel)
    a = run(TupaTradeV2(t_min=t_min, **sel), bars)
    b = run(lit, _plain(bars))
    p = {**V1, **sel}
    np.testing.assert_array_equal(bias(bars, t_min, p["t_rule"], p["trend"]), lit.bias_log)
    assert trade_rows(a) == trade_rows(b)
    assert (a.open_trade is None) == (b.open_trade is None)


@pytest.mark.parametrize("sel", SWITCH_CASES, ids=lambda d: ",".join(f"{k}={v}" for k, v in d.items()))
def test_each_switch_changes_something(sel):
    """A switch that never changes a trade on synthetic bars would make the parity test above meaningless."""
    rows_v1, rows_alt = [], []
    # TP expiry only bites when the limit sits away from the trigger (risk > max_risk): make that common here
    tp, mr = (5, 3) if "tp_expiry" in sel else (25, 25)
    for seed in range(3):
        bars = synthetic(seed=seed)
        rows_v1 += trade_rows(run(TupaTradeV2(t_min="15m", tp=tp, max_risk=mr), bars))
        rows_alt += trade_rows(run(TupaTradeV2(t_min="15m", tp=tp, max_risk=mr, **sel), bars))
    assert rows_v1 != rows_alt


def test_defaults_are_v1():
    assert TupaTradeV2().params | V1 == TupaTradeV2().params
    for k, v in ALT.items():
        with pytest.raises(ValueError):
            TupaTradeV2(**{k: v + "x"})


@pytest.mark.parametrize("tf", sw.TIMEFRAMES[:3])
def test_fresh_trend_is_trend_until_cleared(tf):
    st = sw.timeframe_state(synthetic(seed=0), tf)
    assert ((st.fresh == 0) | (st.fresh == st.trend)).all()
    assert ((st.fresh == 0) & (st.trend != 0)).any()  # the clearing rule fires
    assert (st.fresh != 0).any()


def test_retest_places_already_triggered_limits():
    for seed in range(3):
        bars = synthetic(seed=seed)
        s = TupaTradeV2(t_min="15m", touched="retest")
        run(s, bars)
    # Strategy-level: an MSS whose break point was touched is skipped by v1 and armed by retest.
    bars = synthetic(seed=0)
    a, b = TupaTradeV2(t_min="15m"), TupaTradeV2(t_min="15m", touched="retest")
    run(a, bars), run(b, bars)
    touched = [i for i in np.flatnonzero(a.win) if a.setup(i) is None and b.setup(i) is not None]
    assert touched
    for i in touched[:50]:
        d, bp, *_ = b.setup(i)
        lo = bars.l[b.m1.idx_l[b.m1.at[i]] + 1: i + 1].min() if d == -1 else bars.h[b.m1.idx_h[b.m1.at[i]] + 1: i + 1].max()
        assert (lo <= bp) if d == -1 else (lo >= bp)


def test_grid_sampler_enumerates_the_declared_tupa_space():
    import strategies.tupa_trade_v2 as mod
    from tvtester import search

    space = search.space_of(mod, "ny", "interpretation")
    cfgs = search.draw_grid(space, 112)
    keys = {search.key(c) for c in cfgs}
    assert len(keys) == 112 and cfgs[0] == search.canonical(space["base"], [])
    assert not any(c["params"]["t_min"] == "1d" and c["params"]["t_rule"] == "highest" for c in cfgs)
    with pytest.raises(SystemExit):
        search.draw_grid(space, 111)
    nb = search.neighbours(search.canonical({**space["base"], "t_min": "1d"}, []), space)
    assert all(not search.excluded(c["params"], space) for c in nb)
    assert {c["params"]["t_min"] for c in nb} == {"15m", "1h", "4h", "1d"}


@pytest.mark.parametrize("seed", [0, 1, 2])
@pytest.mark.parametrize("sel", [{"tp_expiry": "off"}, {"tp_expiry": "off", "order": "freeze", "touched": "retest"}, {}],
                         ids=["off", "off+freeze+retest", "v1"])
def test_tp_expiry_branch_matches_literal(seed, sel):
    """Small max risk puts the limit away from the trigger, so the TP-expiry branch actually runs."""
    bars = synthetic(seed=seed)
    a = run(TupaTradeV2(t_min="15m", tp=5, max_risk=3, **sel), bars)
    b = run(LiteralTupaV2(t_min="15m", tp=5, max_risk=3, **sel), _plain(bars))
    assert trade_rows(a) == trade_rows(b)


def test_random_and_tpe_refuse_a_space_with_exclusions():
    import strategies.tupa_trade_v2 as mod
    from tvtester import search

    space = search.space_of(mod, "ny", "interpretation")
    with pytest.raises(SystemExit):
        search.draw_random(space, 10, 1)
    assert not search.excluded(space["base"], space)
    assert search.excluded({**space["base"], "t_min": "1d", "t_rule": "highest"}, space)
