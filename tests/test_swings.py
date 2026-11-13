import numpy as np
import pandas as pd
import pytest

from cltester.data import add_session
from cltester.swings import build_candles, swing_points, swing_state


def bars(hl, start="2024-03-05 08:00"):
    """(high, low) per 1m bar; open/close in the middle."""
    ts = pd.date_range(pd.Timestamp(start, tz="America/Chicago"), periods=len(hl), freq="min").tz_convert("UTC")
    h = np.array([x[0] for x in hl])
    l = np.array([x[1] for x in hl])
    mid = np.round((h + l) / 2, 2)
    return add_session(pd.DataFrame({"ts": ts, "raw_symbol": "CLJ4", "open": mid, "high": h, "low": l,
                                     "close": mid, "volume": 1, "vendor": "test"}))


def points(df, tf="1m"):
    p = swing_points(df, tf)
    return list(zip(p["kind"], p["price"], strict=True))


ZIGZAG = [(70.10, 70.00), (70.20, 70.05), (70.50, 70.30), (70.40, 70.20), (70.25, 70.00),
          (70.30, 70.10), (70.60, 70.40), (70.45, 70.30), (70.50, 70.35)]


def test_alternating_swings():
    assert points(bars(ZIGZAG)) == [("SH", 70.50), ("SL", 70.00), ("SH", 70.60), ("SL", 70.30)]


def test_left_candle_may_equal_right_must_be_strict():
    # bar 2 low equals left (ok) -> swing low; bar 5 low equals right (not ok) -> bar 6 is the swing low instead
    df = bars([(71.0, 70.6), (71.2, 70.9), (70.9, 70.5), (70.8, 70.5), (71.1, 70.7), (71.3, 71.0), (71.2, 70.8),
               (71.0, 70.8), (71.1, 70.9)])
    p = swing_points(df)
    assert list(p["kind"]) == ["SH", "SL", "SH", "SL"]
    assert p["ts"].iloc[1] == df["ts"].iloc[3] and p["ts"].iloc[3] == df["ts"].iloc[7]


def _rule5(second_low):
    return bars([(71.0, 70.8), (71.2, 70.9), (71.1, 70.5), (70.8, 70.0), (70.75, 70.2), (70.7, second_low),
                 (70.6, 70.1 if second_low < 70.1 else second_low + 0.1), (70.65, 70.3)])


def test_rule5_lower_second_low_replaces_first():
    df = _rule5(69.90)
    p = swing_points(df)
    assert list(zip(p["kind"], p["price"], strict=True)) == [("SH", 71.2), ("SL", 69.90)]


def test_rule5_equal_second_low_later_wins():
    df = _rule5(70.00)
    p = swing_points(df)
    assert (p["kind"].iloc[1], p["price"].iloc[1], p["ts"].iloc[1]) == ("SL", 70.00, df["ts"].iloc[5])


def test_rule5_higher_second_low_is_dropped():
    df = _rule5(70.05)
    p = swing_points(df)
    assert (p["price"].iloc[1], p["ts"].iloc[1]) == (70.00, df["ts"].iloc[3])


def test_owner_example_lowest_candle_becomes_low_then_high():
    # bar 3 fails rule 2 (right candle has an equal low); bar 4 holds the lowest low and is also a swing high
    # candidate; bar 5 has a higher low and a lower high -> bar 4 is swing low, then swing high
    df = bars([(70.0, 69.8), (70.5, 70.0), (70.3, 69.5), (69.8, 69.0), (70.6, 69.0), (70.4, 69.3), (70.45, 69.4)])
    p = swing_points(df)
    assert list(zip(p["kind"], p["price"], strict=True)) == [("SH", 70.5), ("SL", 69.0), ("SH", 70.6)]
    assert p["ts"].iloc[1] == p["ts"].iloc[2] == df["ts"].iloc[4]


def test_rule4_lowest_candle_replaces_a_provisional_low():
    # SH 71.2 (bar 1), provisional SL 70.00 (bar 3). Bar 5 prints 69.80 but fails rule 2 (bar 6 has an equal low).
    # Bar 6 holds the lowest low 69.80 and is also a swing high candidate; bar 7 is inside it.
    # 70.00 is not the lowest of the transition, so bar 6 is the swing low, then the swing high.
    df = bars([(71.0, 70.8), (71.2, 70.9), (71.1, 70.5), (70.8, 70.0), (70.75, 70.2), (70.5, 69.8),
               (71.5, 69.8), (71.4, 70.0), (71.45, 70.1)])
    p = swing_points(df)
    assert list(zip(p["kind"], p["price"], strict=True)) == [("SH", 71.2), ("SL", 69.8), ("SH", 71.5)]
    assert p["ts"].iloc[1] == p["ts"].iloc[2] == df["ts"].iloc[6]


def test_rule4_non_candidate_lower_low_blocks_the_next_high():
    # SH 71.2, provisional SL 70.00. Bars 5 and 6 print 69.80 but fail rule 2 (equal right lows); bar 6 is a swing
    # high candidate (71.5). 70.00 is not the lowest, so there is no valid low between 71.2 and 71.5: they merge and
    # the higher one stays. Bar 7 (equal low, higher right low) is the swing low after it.
    df = bars([(71.0, 70.8), (71.2, 70.9), (71.1, 70.5), (70.8, 70.0), (70.75, 70.2), (70.5, 69.8),
               (71.5, 69.8), (71.4, 69.8), (71.45, 70.1)])
    p = swing_points(df)
    assert list(zip(p["kind"], p["price"], strict=True)) == [("SH", 71.5), ("SL", 69.8)]
    assert p["ts"].iloc[1] == df["ts"].iloc[7]


def test_higher_timeframe_uses_1m_order_inside_candle():
    # one 5m candle (08:05-08:09) prints its high at 08:06 and its low at 08:08: high first
    flat = [(70.0, 69.9)] * 5
    hl = flat + [(70.1, 70.0), (70.9, 70.2), (70.5, 70.1), (70.3, 69.0), (70.2, 69.5)] + flat
    cd = build_candles(bars(hl), "5m")
    assert list(cd.high_first) == [-1, 1, -1]  # flat candles: both extremes in the first bar


@pytest.mark.parametrize("tf", ["1m", "5m", "15m", "1h"])
def test_state_never_uses_future_bars(tf):
    rng = np.random.default_rng(7)
    mid = 70 + np.cumsum(rng.integers(-3, 4, 900)) * 0.01
    hl = [(round(m + 0.03, 2), round(m - 0.03, 2)) for m in mid]
    full = swing_state(bars(hl), tf, prev=True, newest=True)
    for cut in (100, 252, 431, 777, 899):  # cuts inside higher-timeframe candles; the last row is compared too
        part = swing_state(bars(hl[:cut]), tf, prev=True, newest=True)
        pd.testing.assert_frame_equal(full.iloc[:cut], part)


def test_unfinished_candle_cannot_confirm_a_swing():
    # 5m candles: 08:00-08:04 high 70, 08:05-08:09 high 72, then 08:10 high 71 (candle not finished)
    hl = [(70.0, 69.0)] * 5 + [(72.0, 71.0)] * 5 + [(71.0, 70.5)]
    assert swing_state(bars(hl), "5m")["5m_sh"].isna().all()
    st = swing_state(bars(hl + [(71.0, 70.5)] * 4), "5m")  # 08:14 completes the candle
    assert st["5m_sh"].iloc[-1] == 72.0 and st["5m_sh"].iloc[:-1].isna().all()


def test_removed_swing_is_not_carried_forward():
    # rule 4 removes SL 70.00 while candle 6 is processed (at bar 7's close)
    df = bars([(71.0, 70.8), (71.2, 70.9), (71.1, 70.5), (70.8, 70.0), (70.75, 70.2), (70.5, 69.8),
               (71.5, 69.8), (71.4, 69.8), (71.45, 70.1)])
    st = swing_state(df)
    assert st["1m_sl"].iloc[6] == 70.0  # still provisional at bar 6's close
    assert np.isnan(st["1m_sl"].iloc[7]) and pd.isna(st["1m_sl_ts"].iloc[7])
    assert st["1m_sh"].iloc[7] == 71.5


@pytest.mark.parametrize("tf", ["5m", "15m", "1h", "4h", "1d"])
def test_warm_up_with_no_complete_candle_returns_empty_state(tf):
    st = swing_state(bars([(70.1, 70.0)]), tf)
    assert len(st) == 1 and st.isna().all().all()


def test_4h_block_is_complete_at_its_last_minute():
    df = bars([(70.1, 70.0)] * 241, start="2024-03-04 17:00")  # 17:00-20:59 CT block + the 21:00 bar
    assert list(build_candles(df.iloc[:240], "4h").avail) == [239]  # complete at the 20:59 close, not at 21:00
    assert list(build_candles(df, "4h").avail) == [239]  # the 21:00 block is still open


def test_day_is_complete_at_1559_ct():
    df = bars([(70.1, 70.0)] * 60, start="2024-03-05 15:00")  # 15:00-15:59 CT, last hour of the trading day
    cd = build_candles(df, "1d")
    assert list(cd.avail) == [59]
    assert list(build_candles(df, "4h").avail) == [59]


@pytest.mark.parametrize("tf", ["1m", "5m", "15m", "30m", "1h", "4h", "1d"])
def test_empty_frame_gives_empty_results(tf):
    df = bars([]).iloc[:0]
    assert swing_points(df, tf).empty
    st = swing_state(df, tf)
    assert st.empty and list(st.columns) == [f"{tf}_sh", f"{tf}_sh_ts", f"{tf}_sl", f"{tf}_sl_ts"]


def test_state_prev_gives_the_points_before_the_last():
    df = bars(ZIGZAG + [(70.40, 70.20), (70.70, 70.50), (70.60, 70.45)])
    st = swing_state(df, "1m", prev=True)
    pts = points(df)
    last = st.iloc[-1]
    highs = [p for k, p in pts if k == "SH"]
    lows = [p for k, p in pts if k == "SL"]
    assert (last["1m_sh"], last["1m_sh2"]) == (highs[-1], highs[-2])
    assert (last["1m_sl"], last["1m_sl2"]) == (lows[-1], lows[-2])
    plain = swing_state(df, "1m")
    assert list(plain.columns) == ["1m_sh", "1m_sh_ts", "1m_sl", "1m_sl_ts"]
    assert plain["1m_sh"].equals(st["1m_sh"]) and plain["1m_sl"].equals(st["1m_sl"])


def test_newest_settles_order_when_one_candle_is_both_points():
    # owner example: bar 4 is swing low, then swing high (confirmed at bar 5's close)
    df = bars([(70.0, 69.8), (70.5, 70.0), (70.3, 69.5), (69.8, 69.0), (70.6, 69.0), (70.4, 69.3), (70.45, 69.4)])
    st = swing_state(df, "1m", newest=True)
    assert st["1m_sh_ts"].iloc[5] == st["1m_sl_ts"].iloc[5] == df["ts"].iloc[4]
    assert st["1m_newest"].iloc[5] == 1
    assert list(swing_state(bars(ZIGZAG), "1m", newest=True)["1m_newest"]) == [0, 0, 0, 1, 1, -1, -1, 1, -1]
