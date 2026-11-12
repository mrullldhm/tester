import numpy as np
import pandas as pd

from cltester.data import add_session
from cltester.indicators import (
    atr_rma,
    atr_sma,
    ema,
    in_session,
    new_candle,
    on_1m,
    rma,
    rsi_sma,
    rsi_wilder,
    session_vwap,
    sma,
    supertrend,
    tf_candles,
    true_range,
    vortex,
    wma,
)


def frame(close, start="2024-03-05 08:00"):
    ts = pd.date_range(pd.Timestamp(start, tz="America/Chicago"), periods=len(close), freq="min").tz_convert("UTC")
    c = np.round(np.asarray(close, dtype=float), 2)
    return add_session(pd.DataFrame({"ts": ts, "raw_symbol": "CLJ4", "open": c, "high": c + 0.02, "low": c - 0.02,
                                     "close": c, "volume": 10, "vendor": "test"}))


def test_higher_timeframe_value_appears_only_after_candle_completes():
    df = frame(70 + np.arange(30) * 0.01)  # 08:00 .. 08:29 CT
    cd = tf_candles(df, "15m")
    v = on_1m(cd["close"], cd["avail"].to_numpy(), len(df))
    assert np.isnan(v[:14]).all()  # 08:00-08:14 candle complete at the 08:14 bar's close
    assert v[14] == df["close"].iat[14] and v[28] == v[14] and v[29] == df["close"].iat[29]
    assert new_candle(cd["avail"].to_numpy(), len(df)).sum() == 2


def test_ema_wma_rma_basics():
    x = pd.Series(np.arange(1.0, 11.0))
    assert np.isclose(ema(x, 3).iat[-1], x.ewm(span=3, adjust=False).mean().iat[-1])
    assert np.isclose(wma(x, 3).iat[-1], (8 * 1 + 9 * 2 + 10 * 3) / 6)
    r = rma(x, 4)
    assert np.isnan(r.iat[2]) and r.iat[3] == 2.5 and np.isclose(r.iat[4], 2.5 + (5 - 2.5) / 4)


def test_rsi_bounds_and_direction():
    up = rsi_wilder(pd.Series(np.arange(50.0)), 14)
    assert up.iat[-1] == 100.0
    mixed = rsi_wilder(pd.Series(np.sin(np.arange(200) / 5)), 14).dropna()
    assert mixed.between(0, 100).all()


def test_supertrend_follows_a_strong_trend():
    c = np.r_[np.linspace(70, 75, 60), np.linspace(75, 70, 60)]
    d, line = supertrend(c + 0.05, c - 0.05, c, 10, 1.8)
    assert d[55] == 1 and d[-1] == -1
    assert line[55] < c[55] and line[-1] > c[-1]


def test_vortex_in_trend():
    c = np.linspace(70, 75, 60)
    vp, vm = vortex(pd.Series(c + 0.05), pd.Series(c - 0.05), pd.Series(c), 14)
    assert vp.iat[-1] > 1 > vm.iat[-1]


def test_session_vwap_resets_each_trading_day():
    df = frame([70.0] * 3 + [80.0] * 3, start="2024-03-05 16:57")  # 17:00 CT starts the next trading day
    v = session_vwap(df)
    assert np.allclose(v[:3], 70.0) and np.allclose(v[3:], 80.0)


def test_true_range_and_atr_known_values():
    h, l, c = pd.Series([10.0, 12.0, 11.0]), pd.Series([9.0, 10.0, 8.0]), pd.Series([9.5, 11.0, 9.0])
    assert list(true_range(h, l, c)) == [1.0, 2.5, 3.0]  # bar 2: |12 - 9.5|; bar 3: |8 - 11|
    assert atr_sma(h, l, c, 2).iat[2] == 2.75
    assert np.isclose(atr_rma(h, l, c, 2).iat[2], 1.75 + (3.0 - 1.75) / 2)  # seed = mean(1, 2.5)


def test_rsi_sma_and_sma_known_values():
    c = pd.Series([1.0, 2.0, 1.0, 3.0])  # changes +1, -1, +2
    assert np.isclose(rsi_sma(c, 3).iat[3], 100 - 100 / (1 + (3 / 3) / (1 / 3)))
    assert sma(c, 2).iat[3] == 2.0


def test_indicators_keep_the_input_index():
    x = pd.Series(np.arange(1.0, 30.0), index=np.arange(100, 129))
    for out in (sma(x, 3), ema(x, 3), wma(x, 3), rma(x, 3), rsi_wilder(x, 3)):
        assert out.index.equals(x.index)


def test_supertrend_starts_down_like_tradingview():
    c = np.full(20, 70.0)
    d, _ = supertrend(c + 0.05, c - 0.05, c, 10, 1.8)
    assert np.isnan(d[8]) and d[9] == -1


def test_supertrend_flips_against_the_current_band():
    # Codex repro: flat candles, then a long lower wick pulls the current upper band below the close
    c = np.full(11, 70.0)
    h, l = np.full(11, 70.05), np.full(11, 69.95)
    l[-1] = 69.0
    d, line = supertrend(h, l, c, 10, 1.8)
    assert d[-2] == -1 and d[-1] == 1
    assert line[-1] < c[-1]


def test_supertrend_flips_down_against_the_current_band():
    c = np.full(13, 70.0)
    h, l = np.full(13, 70.05), np.full(13, 69.95)
    l[10] = 69.0  # flips up first
    h[-1] = 72.0  # a long upper wick lifts the current lower band above the close
    d, _ = supertrend(h, l, c, 10, 1.8)
    assert d[10] == 1 and d[-1] == -1


def test_candle_with_missing_last_minute_keeps_its_own_trading_day():
    # 15:45-15:59 CT candle with 15:59 missing completes on the next session's first bar (17:00)
    t = pd.to_datetime(["2024-03-05 15:45", "2024-03-05 15:58", "2024-03-05 17:00", "2024-03-05 17:01"]).tz_localize(
        "America/Chicago").tz_convert("UTC")
    c = np.array([70.0, 71.0, 72.0, 72.1])
    df = add_session(pd.DataFrame({"ts": t, "raw_symbol": "CLJ4", "open": c, "high": c + 0.02, "low": c - 0.02,
                                   "close": c, "volume": 1, "vendor": "test"}))
    cd = tf_candles(df, "15m")
    assert cd["avail"].iat[0] == 2  # usable only at 17:00
    assert cd["day"].iat[0] == pd.Timestamp("2024-03-05") and df["trading_day"].iat[2] == pd.Timestamp("2024-03-06")
    assert not in_session(df, cd)[0]
