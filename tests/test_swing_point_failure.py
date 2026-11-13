"""Swing Point Failure rules (docs/strategies/swing_point_failure/README.md), one test per rule.

Scan tests build side-space inputs by hand (short side, prices in ticks, bar t opens at minute t)."""

import numpy as np
import pandas as pd
import pytest

from cltester.data import add_session
from cltester.strategy import load
from strategies.swing_point_failure import MIN_NS, NO_EXPIRY, Ltf, Side, scan

N = 14
NAT = np.iinfo(np.int64).min
TS = np.arange(N, dtype=np.int64) * MIN_NS
LOW_ID = -10 * MIN_NS  # the failed swing low's candle, before the data


def ltf(name, minutes):
    step = minutes * MIN_NS
    return Ltf(name, np.full(N, np.nan), np.full(N, np.nan), np.full(N, NAT), TS // step * step, np.full(N, np.nan))


def base():
    """Swing low 100 armed. Touch at bar 2. 1m HL 105 (candle 4) confirmed at bar 5. Bar 8 breaks it, closes 106."""
    lo, hi, cl = np.full(N, 110.0), np.full(N, 115.0), np.full(N, 112.0)
    lo[2] = 99
    lo[8], cl[8] = 104, 106
    m1, m5 = ltf("1m", 1), ltf("5m", 5)
    m1.done_lo = lo
    m1.sl[5:], m1.sl2[5:], m1.sl_ts[5:] = 105, 98, TS[4]
    sd = Side(lo, hi, cl, np.full(N, 100.0), np.full(N, LOW_ID), np.full(N, True), np.full(N, NAT),
              np.full(N, 150.0), [m1, m5])
    return sd


def run(sd, tie="5m", day=None):
    out = scan(sd, TS, np.zeros(N, dtype=np.int64) if day is None else day, 25, 2, tie)
    assert len(out) == 1  # one setup per swing low
    return out[0]


def test_trigger_at_the_close_when_risk_fits():
    r = run(base())
    assert (r["touch"], r["tf"], r["why"], r["end"]) == (2, "1m", "trigger", 8)
    assert (r["limit"], r["stop"], r["target"], r["expire"]) == (106, 115, 56, NO_EXPIRY)


def test_wide_stop_puts_the_limit_risk_ticks_below_the_stop():
    sd = base()
    sd.hi[6] = 140
    r = run(sd)
    assert (r["stop"], r["limit"], r["target"]) == (140, 115, 65)


def test_pullback_reaching_the_previous_candle_high_ends_the_setup():
    sd = base()
    sd.hi[7] = 150  # a touch counts
    r = run(sd)
    assert (r["why"], r["end"]) == ("invalidation level", 7)
    assert np.isnan(r["limit"])


def test_the_touch_bar_itself_does_not_invalidate():
    sd = base()
    sd.hi[2] = 150
    assert run(sd)["why"] == "trigger"


@pytest.mark.parametrize("change", ["replaced", "swing high"])
def test_setup_ends_when_the_low_is_no_longer_the_newest_point(change):
    sd = base()
    if change == "replaced":
        sd.lvl_id[6:] = LOW_ID + 5 * MIN_NS  # rule 5: a lower low took its place
    else:
        sd.armed[6:] = False  # a swing high confirmed after it
    r = run(sd)
    assert (r["why"], r["end"]) == ("swing low replaced or swing high", 6)


def test_higher_low_before_the_touch_does_not_count():
    sd = base()
    sd.ltfs[0].sl_ts[5:] = TS[1]
    r = run(sd)
    assert r["tf"] is None and r["why"] == "data end"


def test_trigger_level_trails_to_the_newest_higher_low_and_the_stop_starts_after_it():
    sd = base()
    m1 = sd.ltfs[0]
    m1.sl[7:], m1.sl2[7:], m1.sl_ts[7:] = 107, 105, TS[6]
    sd.lo[8] = 106  # breaks 107, not 105
    sd.hi[5] = 130  # before the newest higher low: not part of the stop
    r = run(sd)
    assert (r["why"], r["hl"], r["stop"], r["limit"]) == ("trigger", 107, 115, 106)


@pytest.mark.parametrize("tie", ["5m", "1m"])
def test_tie_between_timeframes_follows_the_parameter(tie):
    sd = base()
    m5 = sd.ltfs[1]
    m5.sl[5:], m5.sl2[5:], m5.sl_ts[5:] = 104, 98, 0
    assert run(sd, tie=tie)["tf"] == tie


def test_first_timeframe_with_a_higher_low_is_locked():
    sd = base()
    m5 = sd.ltfs[1]
    m5.sl[6:], m5.sl2[6:], m5.sl_ts[6:] = 104, 98, 0  # 5m confirms one bar after 1m
    assert run(sd, tie="5m")["tf"] == "1m"


def test_unfilled_order_is_cancelled_when_a_later_swing_high_is_confirmed():
    sd = base()
    sd.opp_id[3:] = LOW_ID - MIN_NS  # an older swing high: no cancel
    sd.opp_id[11:] = LOW_ID + MIN_NS
    assert run(sd)["expire"] == 3
    day = np.zeros(N, dtype=np.int64)
    day[10:] = 1  # the engine cancels at the day change first
    assert run(sd, day=day)["expire"] == NO_EXPIRY


def test_no_trade_when_the_stop_is_not_above_the_close():
    sd = base()
    sd.cl[8] = 115
    r = run(sd)
    assert r["why"] == "no risk (stop at the close)" and np.isnan(r["limit"])


def test_long_side_is_the_mirror_of_the_short_side():
    rng = np.random.default_rng(11)
    n = 60 * 24 * 8
    ts = (pd.Timestamp("2024-03-04 17:00", tz="America/Chicago") + pd.to_timedelta(np.arange(n), unit="min"))
    walk = np.round(70 + np.cumsum(rng.normal(0, 0.03, n)), 2)
    o = np.r_[70.0, walk[:-1]]
    hi = np.maximum(o, walk) + np.round(rng.uniform(0, 0.03, n), 2)
    lo = np.minimum(o, walk) - np.round(rng.uniform(0, 0.03, n), 2)

    def frame(op, h, low, c):
        return add_session(pd.DataFrame({"ts": ts.tz_convert("UTC"), "raw_symbol": "CLJ4", "open": op, "high": h,
                                         "low": low, "close": c, "volume": 1, "vendor": "test"}))

    s = load("swing_point_failure")
    a = s.setups(frame(o, hi, lo, walk), s.PARAMS)
    b = s.setups(frame(np.round(140 - o, 2), np.round(140 - lo, 2), np.round(140 - hi, 2), np.round(140 - walk, 2)),
                 s.PARAMS)
    assert (a["why"] == "trigger").any()
    assert len(a) == len(b)
    a = a.sort_values(["touch", "side"]).reset_index(drop=True)
    b = b.sort_values(["touch", "side"], ascending=[True, False]).reset_index(drop=True)
    assert (a["side"] == -b["side"]).all()
    assert a[["touch", "end", "why", "tf"]].equals(b[["touch", "end", "why", "tf"]])
    for col in ("level", "inval", "hl", "limit", "stop", "target"):
        assert np.allclose(a[col], np.round(140 - b[col], 2), equal_nan=True), col


def test_two_candles_completing_on_one_bar_keep_the_lowest_low():
    from cltester.swings import Candles
    from strategies.swing_point_failure import _completed_extremes

    idx = pd.DatetimeIndex([], tz="UTC")
    cd = Candles(idx, *(np.array(v) for v in ([1, 1], [9, 8], [3, 5], [1, 1], [0, 0], [2, 2], [0, 1], [1, 2])))
    lows, highs = _completed_extremes(cd, 4)
    assert lows[2] == 3 and highs[2] == 9
    assert np.isnan(lows[[0, 1, 3]]).all()


def test_stop_window_starts_at_the_next_candle_when_the_hl_candle_misses_its_first_minute():
    # minute 5 has no bar: the 5m HL candle (05-09) starts trading at 06. The candle after it opens at 10, and its
    # 10:00 high (140) belongs to the stop
    minutes = np.r_[np.arange(5), np.arange(6, 25)]
    ts = minutes.astype(np.int64) * MIN_NS
    n = len(ts)
    at = {int(m): k for k, m in enumerate(minutes)}
    lo, hi, cl = np.full(n, 110.0), np.full(n, 115.0), np.full(n, 112.0)
    lo[at[2]] = 99
    hi[at[10]] = 140
    step = 5 * MIN_NS
    m1 = Ltf("1m", np.full(n, np.nan), np.full(n, np.nan), np.full(n, NAT), ts, lo)
    m5 = Ltf("5m", np.full(n, np.nan), np.full(n, np.nan), np.full(n, NAT), ts // step * step, np.full(n, np.nan))
    m5.sl[at[14]:], m5.sl2[at[14]:], m5.sl_ts[at[14]:] = 105, 98, 6 * MIN_NS  # confirmed when 10-14 completes
    m5.done_lo[at[19]], cl[at[19]] = 104, 106  # candle 15-19 breaks the HL
    sd = Side(lo, hi, cl, np.full(n, 100.0), np.full(n, LOW_ID), np.full(n, True), np.full(n, NAT),
              np.full(n, 150.0), [m1, m5])
    (r,) = scan(sd, ts, np.zeros(n, dtype=np.int64), 25, 2, "5m")
    assert (r["tf"], r["why"], r["stop"], r["limit"]) == ("5m", "trigger", 140, 115)
