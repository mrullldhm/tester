"""Swing Point Manipulation rules (docs/strategies/swing_point_manipulation/README.md), one test per rule.

Side space (long). Synthetic: 1H candles of 4 bars (c1 = bars 4-7, c2 = 8-11, c3 = 12-15), 15m candles of 2 bars."""

import numpy as np
import pandas as pd
import pytest

from strategies.swing_point_manipulation import (
    NO_EXPIRY,
    SIGNAL_AFTER_SESSION,
    Frame,
    State,
    Strategy,
    _states,
    scan,
)

N = 16


def frame(hi, lo, size):
    first = np.arange(0, N, size)
    last = first + size - 1
    return Frame(np.maximum.reduceat(hi, first), np.minimum.reduceat(lo, first), first.astype(np.int64),
                 first, last, last.copy())


def c3():
    """Per 1H candle as candle 2: the next 4-bar hour."""
    first = np.r_[np.arange(4, N, 4), -1]
    return first, np.where(first < 0, -1, first + 3)


def base():
    """c1 high 110; c2 high 112 low 102; c3: bar 12 low 101 (takes c2 low), bar 13 high 113 (takes c2 high),
    closes 110. TP 200."""
    hi, lo, cl = np.full(N, 110.0), np.full(N, 100.0), np.full(N, 105.0)
    hi[8:12], lo[8:12] = 111, 102
    hi[9] = 112
    hi[12:], lo[12:] = 111, 104
    lo[12] = 101
    hi[13], cl[13] = 113, 110
    st = State(np.ones(N, bool), np.full(N, 200.0), np.zeros(N, np.int64))
    return hi, lo, cl, st


def run(hi, lo, cl, st, risk=15):
    rows = scan(hi, lo, cl, frame(hi, lo, 4), c3(), frame(hi, lo, 2), np.arange(N) // 2, st, np.full(N, N - 1), risk)
    return next((r for r in rows if r["c3"] == 3), None)


def test_low_then_high_in_candle_3_buys_the_15m_close_with_stop_at_its_low():
    r = run(*base())
    assert (r["why"], r["lo_touch"], r["hi_touch"], r["end"]) == ("trigger", 12, 13, 13)
    assert (r["limit"], r["stop"], r["target"], r["expire"]) == (110, 101, 200, NO_EXPIRY)


def test_touches_count():
    hi, lo, cl, st = base()
    lo[12], hi[13] = 102, 112
    assert run(hi, lo, cl, st)["why"] == "trigger"


def test_wide_15m_candle_puts_the_limit_risk_ticks_above_its_low():
    hi, lo, cl, st = base()
    hi[13], cl[13] = 130, 125
    assert (run(hi, lo, cl, st)["limit"], run(hi, lo, cl, st, risk=20)["limit"]) == (116, 121)


def test_high_first_gives_no_trigger():
    hi, lo, cl, st = base()
    lo[12], hi[12] = 104, 113
    lo[13] = 101
    assert run(hi, lo, cl, st)["why"] == "high first or same 1m bar"


def test_both_sides_in_one_1m_bar_gives_no_trigger():
    hi, lo, cl, st = base()
    lo[12], hi[12] = 101, 113
    lo[13] = 104
    assert run(hi, lo, cl, st)["why"] == "high first or same 1m bar"


def test_only_one_side_taken_gives_no_trigger():
    hi, lo, cl, st = base()
    hi[13] = 111
    assert run(hi, lo, cl, st)["why"] == "no touch of both sides"


def test_candle_2_high_below_candle_1_is_not_a_setup():
    hi, lo, cl, st = base()
    hi[5] = 113
    assert run(hi, lo, cl, st) is None


def test_equal_candle_2_high_is_a_setup():
    hi, lo, cl, st = base()
    hi[5] = 112
    assert run(hi, lo, cl, st)["why"] == "trigger"


def test_structure_must_be_armed_at_candle_2_close():
    hi, lo, cl, st = base()
    st.armed[11] = False
    assert run(hi, lo, cl, st) is None


def test_candle_1_may_be_the_swing_low_candle_but_not_before_it():
    hi, lo, cl, st = base()
    st.base_ts[:] = 4  # swing low on c1's candle
    assert run(hi, lo, cl, st)["why"] == "trigger"
    st.base_ts[:] = 8  # swing low on c2: c1 opens before it
    assert run(hi, lo, cl, st) is None


def test_tp_touched_before_the_order_works_gives_no_trade():
    hi, lo, cl, st = base()
    st.tp[:] = 113
    assert run(hi, lo, cl, st)["why"] == "TP touched before the order"


def test_order_works_through_the_first_tp_touch_bar_where_the_engine_kill_decides():
    hi, lo, cl, st = base()
    hi[15] = 200
    assert run(hi, lo, cl, st)["expire"] == 2  # bars 14-15; bar 15 is decided by the engine's kill (= target)
    hi[14] = 200
    assert (run(hi, lo, cl, st)["why"], run(hi, lo, cl, st)["expire"]) == ("trigger", 1)


def states_frame(newest, sh_ts, sl_ts):
    ts = lambda h: pd.Series([pd.Timestamp("2026-01-01", tz="UTC") + pd.Timedelta(hours=h)])  # noqa: E731
    return pd.DataFrame({"1h_sh": [90.0], "1h_sl": [88.0], "1h_sh2": [91.0], "1h_sl2": [87.0],
                         "1h_sh_ts": ts(sh_ts), "1h_sl_ts": ts(sl_ts), "1h_sh2_ts": ts(0), "1h_sl2_ts": ts(0),
                         "1h_newest": [newest]})


def test_outside_candle_swing_high_on_the_swing_low_candle():
    s = states_frame(1, 5, 5)  # one candle is SL then SH: newest is the SH
    skip, strict = _states(s, "skip"), _states(s, "strict")
    assert (bool(skip[1].armed[0]), skip[1].tp[0]) == (True, 9100)  # TP = the swing high before it
    assert not strict[1].armed[0]
    # short side: SL then SH is its own valid structure, TP = that candle's low
    assert all(bool(m[-1].armed[0]) and m[-1].tp[0] == -8800 for m in (skip, strict))
    s = states_frame(1, 6, 5)  # SH on a later candle: a real swing high, no long setup
    assert not _states(s, "skip")[1].armed[0]


def test_short_is_the_mirror():
    s = states_frame(1, 6, 5)  # newest swing high: short armed, TP = swing low (side space negated)
    st = _states(s, "strict")[-1]
    assert (bool(st.armed[0]), st.tp[0]) == (True, -8800)


def test_a_new_setup_cancels_an_unfilled_order(monkeypatch):
    s = Strategy()
    rows = pd.DataFrame({"side": [1, -1], "limit": [10.0, 9.0], "stop": [9.0, 10.0], "target": [12.0, 7.0],
                         "end": [100, 130], "expire": [NO_EXPIRY, 40], "why": "trigger"})
    monkeypatch.setattr(s, "setups", lambda df, p: rows)
    sig = s.signals(None, s.PARAMS)
    assert list(sig["expire"]) == [30, 40]  # the first works through bar 130


def test_unknown_outside_mode_is_refused():
    with pytest.raises(ValueError):
        Strategy().setups(pd.DataFrame(), {**Strategy.PARAMS, "outside": "x"})


def run_confirm(hi, lo, cl, st, risk=15):
    rows = scan(hi, lo, cl, frame(hi, lo, 4), c3(), frame(hi, lo, 2), np.arange(N) // 2, st, np.full(N, N - 1), risk,
                confirm=True)
    return next(r for r in rows if r["c3"] == 3)


def test_confirm_places_the_same_limit_after_the_next_15m_candle_holds_the_low():
    r = run_confirm(*base())  # break candle bars 12-13 (low 101), next 15m bars 14-15 (low 104)
    assert (r["why"], r["end"], r["limit"], r["stop"]) == ("trigger", 15, 110, 101)


def test_confirm_skips_when_the_next_15m_candle_touches_the_low():
    hi, lo, cl, st = base()
    lo[15] = 101
    assert run_confirm(hi, lo, cl, st)["why"] == "next 15m candle took the low"


def test_confirm_skips_when_tp_is_touched_in_the_next_15m_candle():
    hi, lo, cl, st = base()
    hi[14] = 200
    assert run_confirm(hi, lo, cl, st)["why"] == "TP touched before the order"


def test_confirm_needs_a_next_15m_candle_in_the_session():
    hi, lo, cl, st = base()
    rows = scan(hi, lo, cl, frame(hi, lo, 4), c3(), frame(hi, lo, 2), np.arange(N) // 2, st, np.full(N, 13), 15,
                confirm=True)
    assert next(r for r in rows if r["c3"] == 3)["why"] == "no next 15m candle in the session"


@pytest.mark.parametrize("confirm", [0, 1])
def test_signals_exist_at_their_bar_without_later_data(confirm):
    """Point in time: cut the data right after each signal bar; the same signal must already be there."""
    from cltester import data
    try:
        df = data.add_session(data.load_bars("2026-11-03", "2026-11-14")).reset_index(drop=True)
    except FileNotFoundError:
        pytest.skip("no local bars")
    s, p = Strategy(), {**Strategy.PARAMS, "confirm": confirm}
    full = s.signals(df, p)
    assert len(full)
    for bar in full.index:
        cut = s.signals(df.iloc[:bar + 1].copy(), p)
        assert bar in cut.index, f"signal at bar {bar} needs later bars"
        cols = ["side", "limit", "stop", "target"]
        assert cut.loc[bar, cols].equals(full.loc[bar, cols])


def test_a_newer_order_cancels_the_older_one_and_every_order_carries_the_tp_kill(monkeypatch):
    s = Strategy()
    rows = pd.DataFrame({"side": [1, -1, 1], "limit": [10.0, 8.0, 11.0], "stop": [9.0, 9.0, 10.0],
                         "target": [12.0, 7.0, 13.0], "end": [100, 120, 150], "expire": [NO_EXPIRY, 1, 5],
                         "why": ["trigger", "trigger", "trigger"]})
    monkeypatch.setattr(s, "setups", lambda df, p: rows)
    sig = s.signals(None, s.PARAMS)
    assert list(sig.index) == [100, 120, 150] and list(sig["expire"]) == [20, 1, 5]  # first works through bar 120
    assert list(sig["kill"]) == [12.0, 7.0, 13.0]


@pytest.mark.parametrize("confirm", [False, True])
def test_a_candle_completed_by_the_next_session_gives_no_order(confirm):
    """The deciding 15m candle (break, or the next one with confirm) misses its last minute, so it completes at the
    first bar of the next session or contract: no order."""
    hi, lo, cl, st = base()
    m15 = frame(hi, lo, 2)
    deciding = 7 if confirm else 6  # break candle bars 12-13; next candle bars 14-15
    end = int(m15.last[deciding])
    m15.avail[deciding] = end + 1
    hi, lo, cl = (np.r_[x, x[-1]] for x in (hi, lo, cl))  # one bar of the next session
    st = State(np.r_[st.armed, True], np.r_[st.tp, st.tp[-1]], np.r_[st.base_ts, 0])
    last = np.r_[np.full(end + 1, end), np.full(len(hi) - end - 1, len(hi) - 1)]
    rows = scan(hi, lo, cl, frame(hi[:N], lo[:N], 4), c3(), m15, np.r_[np.arange(N) // 2, -1], st, last, 15,
                confirm=confirm)
    assert next(r for r in rows if r["c3"] == 3)["why"] == SIGNAL_AFTER_SESSION


def run_tp(hi, lo, cl, st, tp_ticks):
    rows = scan(hi, lo, cl, frame(hi, lo, 4), c3(), frame(hi, lo, 2), np.arange(N) // 2, st, np.full(N, N - 1), 15,
                tp_ticks=tp_ticks)
    return next(r for r in rows if r["c3"] == 3)


def test_fixed_tp_targets_ticks_above_the_limit():
    r = run_tp(*base(), tp_ticks=30)
    assert (r["why"], r["limit"], r["target"]) == ("trigger", 110, 140)


def test_fixed_tp_ignores_the_swing_target_before_the_order():
    hi, lo, cl, st = base()
    st.tp[:] = 113  # the break reaches the swing high: no trade with the swing target, a trade with a fixed one
    assert run(hi, lo, cl, st)["why"] == "TP touched before the order"
    assert run_tp(hi, lo, cl, st, tp_ticks=15)["target"] == 125


def test_fixed_tp_touch_cancels_the_unfilled_order():
    hi, lo, cl, st = base()
    hi[15] = 125
    assert run_tp(hi, lo, cl, st, tp_ticks=15)["expire"] == 2  # through the TP-touch bar 15; the engine kill decides it


def test_tp_must_be_swing_or_positive_ticks():
    with pytest.raises(ValueError):
        Strategy().setups(pd.DataFrame(), {**Strategy.PARAMS, "tp": 0})
