"""rlm: level book accounting (join, TF dedupe/upgrade, withdraw, cross penalty), order geometry for both sides,
break-even management that ignores the fill-bar high, and swing-event timing (docs/strategies/rlm/README.md)."""

import numpy as np
import pandas as pd
import pytest

from cltester.data import add_session
from cltester.engine import Ctx
from cltester.swings import HIGH, LOW
from strategies.rlm import COMBOS, CROSS_PENALTY, Book, Strategy, build_orders, swing_events

A = 10.0  # ATR34 in ticks


def _book(tol: float = 0.6) -> Book:
    return Book(len(COMBOS), tol)


def test_two_touches_join_one_level_weighted_mean():
    b = _book()
    b.touch((0, LOW, 1), LOW, 1000, 10, 14, 1.0, A, 1010.0, 5)
    b.touch((2, HIGH, 9), HIGH, 1004, 100, 159, 2.0, A, 990.0, 50)  # within 0.6 * 10 ticks
    al = np.flatnonzero(b.alive)
    assert len(al) == 1
    s = al[0]
    assert b.touches[s] == 2 and b.ht[s] == 1 and b.lt[s] == 1
    assert b.mid[s] == pytest.approx((1000 * 1 + 1004 * 2) / 3)
    assert b.strength[s] == pytest.approx(3.0) and b.maxw[s] == 2.0


def test_same_extreme_on_higher_tf_upgrades_weight_not_touches():
    b = _book()
    b.touch((0, LOW, 3), LOW, 1000, 15, 19, 1.0, A, 1010.0, 5)  # 5m candle bars 15..19
    b.touch((2, LOW, 0), LOW, 1000, 0, 59, 2.0, A, 1010.0, 9)  # 1h candle bars 0..59 holds the same low
    s = np.flatnonzero(b.alive)[0]
    assert b.touches[s] == 1 and b.strength[s] == pytest.approx(2.0) and b.maxw[s] == 2.0
    b.touch((1, LOW, 1), LOW, 1000, 15, 29, 1.5, A, 1010.0, 9)  # a weaker TF of it later adds nothing
    assert b.touches[s] == 1 and b.strength[s] == pytest.approx(2.0)


def test_withdraw_drops_to_next_tf_then_removes():
    b = _book()
    b.touch((0, LOW, 3), LOW, 1000, 15, 19, 1.0, A, 1010.0, 5)
    b.touch((2, LOW, 0), LOW, 1000, 0, 59, 2.0, A, 1010.0, 5)
    s = np.flatnonzero(b.alive)[0]
    b.withdraw((2, LOW, 0), A, 5)
    assert b.alive[s] and b.touches[s] == 1 and b.strength[s] == pytest.approx(1.0)
    b.withdraw((0, LOW, 3), A, 5)
    assert not b.alive.any()


def test_cross_flips_side_and_costs_strength_only_when_active():
    b = _book()
    b.touch((0, LOW, 1), LOW, 1000, 10, 14, 1.0, A, 1010.0, 5)
    s = np.flatnonzero(b.alive)[0]
    b.age_cross(980.0, 1.0, 6)  # one touch: side changes, no penalty
    assert b.side[s] == -1 and b.strength[s] == pytest.approx(1.0) and b.crosses[s] == 0
    b.touch((0, LOW, 7), LOW, 1001, 40, 44, 1.0, A, 980.0, 8)
    b.age_cross(1020.0, 1.0, 9)
    assert b.side[s] == 1 and b.crosses[s] == 1 and b.strength[s] == pytest.approx(2.0 * CROSS_PENALTY)


def _cand(side: int) -> pd.DataFrame:
    # support band 1000..1004 (long) / resistance band 1000..1004 (short); ATR14 10 ticks
    if side == 1:
        o, h, lo, c = 1003.0, 1012.0, 1001.0, 1010.0
    else:
        o, h, lo, c = 1001.0, 1003.0, 992.0, 994.0
    return pd.DataFrame([{"c": 40, "bar": 5, "side": side, "combo": 0, "mid": 1002.0, "lo": 1000.0, "hi": 1004.0,
                          "score": 60.0, "touches": 3, "polar": True, "maxw": 2.0, "strength": 5.0, "crosses": 0,
                          "age": 10, "atr34": 10.0, "atr14": 10.0, "o": o, "h": h, "l": lo, "cl": c}])


def _df() -> pd.DataFrame:
    ts = pd.date_range("2024-12-09 15:00", periods=10, freq="1min", tz="UTC")
    df = pd.DataFrame({"ts": ts, "raw_symbol": "CLF5", "open": 70.0, "high": 70.0, "low": 70.0, "close": 70.0})
    return add_session(df)


@pytest.mark.parametrize("side,entry,stop,target", [
    (1, 1010, 998, 1022),     # long: wick stop min(1001 - 2.5, 1010 - 5) = 998.5 -> floor 998; r1 target 1010 + 12
    (-1, -994, -1006, -982),  # short in side space: stop min(-992 - 2.5, -994 - 5) = -1005.5 -> floor -1006 (1006)
])
def test_order_geometry_close_entry_wick_stop(side, entry, stop, target):
    p = {**Strategy.PARAMS, "clv": 0.6, "score": 0, "entry": "close", "stop": "wick", "exit": "r1"}
    o = build_orders(_cand(side), _df(), p)
    assert (o["E"].iat[0], o["S"].iat[0], o["T"].iat[0]) == (entry, stop, target)


def test_band_entry_and_band_stop_long():
    p = {**Strategy.PARAMS, "clv": 0.6, "score": 0, "entry": "band", "stop": "band", "exit": "r2"}
    o = build_orders(_cand(1), _df(), p)
    # limit at band top 1004; stop min(1000 - 2.5, 1004 - 5) = 997.5 -> 997; risk 7, target 1004 + 14
    assert (o["E"].iat[0], o["S"].iat[0], o["T"].iat[0]) == (1004, 997, 1018)


def test_break_even_ignores_fill_bar_high():
    s = Strategy()
    s._p = {"exit": "be3"}
    hi = np.array([0, 0, 1020, 1005, 1011, 1000], dtype=np.int64)  # fill bar j=2 high 1020 (may predate the fill)
    s._side_hi = {1: hi}
    s._tp1 = {1: 1010}
    ctx = Ctx(i=1, j=2, m=3, side=1, E=1000, S=990, T=1030, qty=1, best=1020)
    assert s.manage(ctx) == (990, False)  # only the fill bar seen so far: no BE
    ctx.m = 4
    assert s.manage(ctx) == (990, False)  # bar 3 high 1005 < 1000 + 10
    ctx.m = 5
    assert s.manage(ctx) == (1000, False)  # bar 4 high 1011 >= 1R: stop to entry from bar 5


def _swing_df() -> pd.DataFrame:
    """5m candles: down, swing low at candle 2, up to a swing high at candle 5, then down (locks the low)."""
    lows = [10.0, 9.8, 9.5, 9.7, 9.9, 10.1, 9.9, 9.7, 9.6]
    rows = []
    t0 = pd.Timestamp("2024-12-09 18:00", tz="America/Chicago")
    for k, lo in enumerate(lows):
        hi = lo + 0.3
        for i in range(5):
            rows.append((t0 + pd.Timedelta(minutes=5 * k + i), "CLF5", lo + 0.1, hi if i == 2 else lo + 0.2,
                         lo if i == 3 else lo + 0.1, lo + 0.15))
    df = pd.DataFrame(rows, columns=["ts", "raw_symbol", "open", "high", "low", "close"])
    df["ts"] = df["ts"].dt.tz_convert("UTC")
    return add_session(df)


def test_swing_event_timing_lock_after_confirm():
    df = _swing_df()
    conf = swing_events(df, "5m", "confirm")
    lock = swing_events(df, "5m", "lock")
    low_c = conf[(conf["kind"] == LOW) & (conf["op"] == 1)].iloc[0]
    assert low_c["candle"] == 2 and low_c["known"] == 3 * 5 + 4  # known at the close of candle 3 (its right candle)
    low_l = lock[lock["kind"] == LOW].iloc[0]
    assert low_l["candle"] == 2 and low_l["known"] == 6 * 5 + 4  # locked when the swing high (candle 5) confirms


def test_withdraw_takes_back_current_share_after_decay_and_cross():
    b = _book()
    b.touch((0, LOW, 1), LOW, 1000, 10, 14, 1.0, A, 1010.0, 0)
    b.touch((0, LOW, 2), LOW, 1001, 20, 24, 1.0, A, 1010.0, 0)
    b.age_cross(980.0, b.decay, 1)  # decay, then a cross of an active level: x 0.7
    b.withdraw((0, LOW, 1), A, 1)
    s = np.flatnonzero(b.alive)[0]
    assert b.strength[s] == pytest.approx(b.decay * CROSS_PENALTY)  # only the remaining touch's share


def test_two_lower_tf_points_of_one_extreme_keep_the_touch_alive():
    """Codex 2026-11-19: one 1h point and two nested 5m points of the same low; withdrawing one 5m point and the 1h
    point must leave the touch alive on the other 5m point."""
    b = _book()
    b.touch((0, LOW, 3), LOW, 1000, 15, 19, 1.0, A, 1010.0, 5)
    b.touch((2, LOW, 0), LOW, 1000, 0, 59, 2.0, A, 1010.0, 5)
    b.touch((0, LOW, 4), LOW, 1000, 15, 19, 1.0, A, 1010.0, 5)  # rare: same 5m extreme reported again
    s = np.flatnonzero(b.alive)[0]
    b.withdraw((0, LOW, 3), A, 5)
    b.withdraw((2, LOW, 0), A, 5)
    assert b.alive[s] and b.touches[s] == 1 and b.strength[s] == pytest.approx(1.0) and b.maxw[s] == 1.0


def test_dead_level_purges_its_touches():
    b = _book()
    b.touch((0, LOW, 3), LOW, 1000, 15, 19, 1.0, A, 1010.0, 5)
    s = np.flatnonzero(b.alive)[0]
    b._kill(s)
    assert not b.entries and not b.pid2key and not b.base and not any(b.registry.values())
    b.touch((2, LOW, 0), LOW, 1000, 0, 59, 2.0, A, 1010.0, 9)  # the extreme comes back as a fresh touch
    s = np.flatnonzero(b.alive)[0]
    assert b.touches[s] == 1 and b.strength[s] == pytest.approx(2.0)


def test_window_clocks_follow_daylight_saving():
    from strategies.rlm import in_window
    # first 1h candle of the session (17:00 CT): 06:00 Malaysia in US summer, 07:00 in US winter
    summer = pd.DatetimeIndex(["2024-07-08 22:00"], tz="UTC")  # 17:00 CDT
    winter = pd.DatetimeIndex(["2024-01-08 23:00"], tz="UTC")  # 17:00 CST
    for ts in (summer, winter):
        assert in_window(ts, "ct:17-17")[0]
        assert in_window(ts, "ct:17-01")[0] and not in_window(ts, "ct:02-06")[0]
    assert in_window(summer, "myt:06-06")[0] and not in_window(winter, "myt:06-06")[0]
    assert in_window(winter, "myt:07-07")[0]
    # 02:00 CT = 08:00 London in both seasons, except when US and UK daylight saving differ (2024-03-12: US on, UK off)
    assert in_window(pd.DatetimeIndex(["2024-07-09 07:00"], tz="UTC"), "ldn:08-08")[0]
    assert in_window(pd.DatetimeIndex(["2024-03-12 07:00"], tz="UTC"), "ldn:07-07")[0]
    with pytest.raises(ValueError):
        in_window(summer, "est:1-2")


def test_enclosing_candle_coalesces_two_lower_tf_touches():
    """Codex 2026-11-20: two 5m swing lows at the same price in different 5m candles, then one 1h candle holding
    both: one extreme on 1h, so one touch of weight 2, and a later 5m point inside that 1h candle adds nothing."""
    b = _book()
    b.touch((0, LOW, 3), LOW, 1000, 15, 19, 1.0, A, 1010.0, 5)
    b.touch((0, LOW, 9), LOW, 1000, 45, 49, 1.0, A, 1010.0, 6)
    s = np.flatnonzero(b.alive)[0]
    assert b.touches[s] == 2 and b.strength[s] == pytest.approx(2.0)
    b.touch((2, LOW, 0), LOW, 1000, 0, 59, 2.0, A, 1010.0, 7)
    assert np.flatnonzero(b.alive).tolist() == [s]
    assert b.touches[s] == 1 and b.strength[s] == pytest.approx(2.0) and b.maxw[s] == 2.0
    assert len(b.registry[(LOW, 1000)]) == 1
    b.touch((0, LOW, 11), LOW, 1000, 55, 59, 1.0, A, 1010.0, 8)  # inside the 1h candle: same extreme
    assert b.touches[s] == 1 and b.strength[s] == pytest.approx(2.0)
    b.withdraw((2, LOW, 0), A, 9)  # 1h point leaves: the touch drops to its 5m points (weight 1), still one touch
    assert b.touches[s] == 1 and b.strength[s] == pytest.approx(1.0) and b.maxw[s] == 1.0
    for pid in ((0, LOW, 3), (0, LOW, 9), (0, LOW, 11)):
        b.withdraw(pid, A, 9)
    assert not b.alive.any() and not b.pid2key


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_confirm_events_replay_the_exact_structure(seed):
    """Codex adversarial review 2026-11-20: withdrawals inferred from the top-4 state missed points removed by
    rule-4 cascades (older points resurfacing). Confirm-mode events now come from the detector itself: replaying
    them must give exactly the live structure, and no point leaves before it entered."""
    from cltester.swings import build_candles, detect
    rng = np.random.default_rng(seed)
    n = 3000
    steps = rng.integers(-3, 4, n).cumsum()
    close = 70.0 + 0.01 * steps
    hi = close + 0.01 * rng.integers(0, 4, n)
    lo = close - 0.01 * rng.integers(0, 4, n)
    op = np.r_[close[0], close[:-1]]
    ts = pd.date_range("2024-03-04 23:00", periods=n, freq="1min", tz="UTC")
    df = add_session(pd.DataFrame({"ts": ts, "raw_symbol": "CLJ4", "open": op, "high": np.maximum(hi, op),
                                   "low": np.minimum(lo, op), "close": close}))
    ev = swing_events(df, "5m", "confirm")
    cd = build_candles(df, "5m")
    live: set = set()
    for r in ev.itertuples():
        pt = (r.kind, r.candle)
        if r.op > 0:
            assert pt not in live
            live.add(pt)
        else:
            assert pt in live
            live.remove(pt)
    snap: dict = {}
    last_known = len(cd) - 2  # events of candle k are known at avail[k+1]

    def grab(k, stack):
        if k == last_known:
            snap["s"] = {(p.kind, p.candle) for p in stack}

    detect(cd, observer=grab)
    assert live == snap["s"]
    assert (ev["op"] < 0).any()
