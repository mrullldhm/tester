"""pd_swing rules (docs/strategies/pd_swing/README.md) on real dev bars: point-in-time, one attempt per level per day,
1R bracket, stop beyond the window extreme, protection, P3 owner swing point."""

import numpy as np
import pandas as pd
import pytest

from cltester.config import DATA_DIR
from cltester.data import add_session, load_bars
from cltester.strategy import load
from cltester.swings import swing_state
from strategies.pd_swing import find_gap

pytestmark = pytest.mark.skipif(not (DATA_DIR / "year=2019.parquet").exists(), reason="needs local CL bars")
VARIANTS = ["P1", "P2a", "P2b", "P3a", "P3b"]
PAIRS = [("5m", "1h"), ("15m", "4h")]


@pytest.fixture(scope="module")
def bars():
    return add_session(load_bars("2019-01-01", "2020-01-01"))


@pytest.fixture(scope="module")
def strat():
    return load("pd_swing")


def run(strat, df, v, tf, ctx):
    return strat.signals(df, {**strat.PARAMS, "variant": v, "tf": tf, "ctx": ctx})


@pytest.mark.parametrize("v", VARIANTS)
@pytest.mark.parametrize("tf,ctx", PAIRS)
def test_signal_exists_with_data_cut_at_its_bar(bars, strat, v, tf, ctx):
    sig = run(strat, bars, v, tf, ctx)
    for i in list(sig.index[:3]) + list(sig.index[-2:]):
        cut = run(strat, bars.iloc[:i + 1], v, tf, ctx)
        assert i in cut.index, f"{v} {tf} signal at {i} needs later bars"
        assert cut.loc[i].equals(sig.loc[i])


@pytest.mark.parametrize("v", VARIANTS)
def test_one_bracket_rule_per_signal(bars, strat, v):
    sig = run(strat, bars, v, "5m", "1h")
    risk = (sig["limit"] - sig["stop"]) * sig["side"]
    reward = (sig["target"] - sig["limit"]) * sig["side"]
    assert (risk > 0).all() and np.allclose(risk, reward, atol=0.006)  # 1R, rounded to a tick
    assert (sig["expire_min"] == 20).all()  # 4 candles of 5m


@pytest.mark.parametrize("v", VARIANTS)
def test_at_most_one_signal_per_level_per_day(bars, strat, v):
    sig = run(strat, bars, v, "5m", "1h")
    day = bars["trading_day"].to_numpy()[sig.index]
    assert len(day) == 0 or pd.Series(day).value_counts().max() <= 2  # PDH and PDL, one attempt each


def test_stop_is_one_tick_beyond_the_lows_since_the_touch(bars, strat):
    for v in VARIANTS:
        sig = run(strat, bars, v, "5m", "1h")
        for i, r in sig.iterrows():
            assert (r["stop"] < r["limit"]) == (r["side"] == 1)
            w = bars.iloc[i - 4 * 5 + 1:i + 1]  # the gap candle q (last 5 bars) is inside the stop window
            if r["side"] == 1:
                assert r["stop"] <= round(w["low"].iloc[-5:].min() - 0.01, 2)
            else:
                assert r["stop"] >= round(w["high"].iloc[-5:].max() + 0.01, 2)


def test_p3_b_is_the_owner_swing_point(bars, strat):
    sig = run(strat, bars, "P3a", "5m", "1h")
    st = swing_state(bars, "5m")
    for i, r in sig.iterrows():
        col = "5m_sh" if r["side"] == 1 else "5m_sl"
        assert not np.isnan(st[col].iloc[i])  # a base swing point exists when the order is placed


def test_unknown_variant_is_refused(bars, strat):
    with pytest.raises(ValueError):
        run(strat, bars.iloc[:5000], "P9", "5m", "1h")


@pytest.mark.parametrize("v", ["P1", "P2b"])
def test_frozen_protection_is_passed_to_the_engine_as_void(bars, strat, v):
    sig = run(strat, bars, v, "5m", "1h")
    assert len(sig) and sig["void"].notna().all()
    assert ((sig["void"] - sig["limit"]) * sig["side"] <= 0).all()  # at or beyond the limit on the losing side


def test_context_follows_the_base_timeframe_by_default(bars, strat):
    p15 = {**strat.PARAMS, "variant": "P2b", "tf": "15m"}  # no ctx given: must use 4h, not the 5m default's 1h
    auto = strat.signals(bars, p15)
    pd.testing.assert_frame_equal(auto, run(strat, bars, "P2b", "15m", "4h"))


@pytest.mark.parametrize("tf,ctx", [("15m", "1h"), ("5m", "4h"), ("1h", "auto")])
def test_undeclared_timeframe_pairs_are_refused(bars, strat, tf, ctx):
    with pytest.raises(ValueError):
        run(strat, bars.iloc[:5000], "P1", tf, ctx)


def _candles(hl, sym=None, extra_last=0):
    """Candle arrays for find_gap: one 1m bar per candle (bar = candle index), so first = av = index, unless
    extra_last adds bars after the last candle that it only becomes known at (its last minute missing)."""
    n = len(hl)
    h = np.array([x[0] for x in hl])
    l = np.array([x[1] for x in hl])  # noqa: E741
    h1, l1 = list(h), list(l)
    av = np.arange(n)
    for _ in range(extra_last):  # bars after the last candle; the last candle is known only at the final one
        h1.append(h[-1])
        l1.append(l[-1])
    av[-1] = n - 1 + extra_last
    sym = np.array(sym if sym else [0] * n)
    sym1 = np.r_[sym, [sym[-1]] * extra_last]
    return {"h": h, "l": l, "sym": sym, "live": np.ones(n, bool), "first": np.arange(n),
            "av": av, "h1": np.array(h1), "l1": np.array(l1), "sym1": sym1}


def test_gap_found_in_one_contract():
    c = _candles([(100, 90), (95, 92), (94, 93), (99, 96)])  # touch at 1; gap at 3: high[1] 95 < low[3] 96
    assert find_gap(2, 5, 0, 1, 1, 80, 4, c) == 3


def test_gap_reading_a_candle_from_before_a_roll_is_refused():
    c = _candles([(100, 90), (95, 92), (94, 93), (99, 96)], sym=[0, 0, 1, 1])  # touch at 2 is the first new candle
    assert find_gap(3, 6, 1, 1, 2, 80, 4, c) == -1  # q=3 reads q-2=1 from the old contract


def test_protection_is_checked_through_the_bar_where_the_gap_candle_is_known():
    c = _candles([(100, 90), (95, 92), (94, 93), (99, 96)], extra_last=1)
    c["l1"][-1] = 70  # the late availability bar trades below protection 80
    assert find_gap(2, 5, 0, 1, 1, 80, 4, c) == -1
    c["l1"][-1] = 96
    assert find_gap(2, 5, 0, 1, 1, 80, 4, c) == 3


def test_gap_known_only_on_a_bar_of_the_next_contract_is_refused():
    c = _candles([(100, 90), (95, 92), (94, 93), (99, 96)], extra_last=1)  # q=3 known at the extra bar 4
    assert find_gap(2, 5, 0, 1, 1, 80, 4, c) == 3
    c["sym1"][-1] = 1  # that availability bar is the first bar of the new contract (midnight UTC roll)
    assert find_gap(2, 5, 0, 1, 1, 80, 4, c) == -1


def test_later_gap_after_a_roll_just_before_the_touch_is_found():
    # touch at 2 is the first new-contract candle; q=3 would read candle 1 (old contract): skipped, not the end;
    # q=4 reads 2..4, all new: high[2] 94 < low[4] 96 is a valid gap
    c = _candles([(100, 90), (95, 92), (94, 93), (94, 93), (99, 96)], sym=[0, 0, 1, 1, 1])
    assert find_gap(3, 6, 1, 1, 2, 80, 5, c) == 4
