"""purple_levels_rth (docs/strategies/purple_levels_rth/README.md): 08:30-13:30 CT decision window, orders cancelled
at 13:30, otherwise identical to purple_levels all 5m."""

import numpy as np
import pandas as pd
import pytest

from cltester.config import DATA_DIR
from cltester.data import Bars, add_session, load_bars
from cltester.engine import backtest
from cltester.strategy import load
from strategies.purple_levels_rth import rth_filter


def frame(start_ct: str, minutes: int, price: float = 70.0) -> pd.DataFrame:
    ts = pd.date_range(pd.Timestamp(start_ct, tz="America/Chicago"), periods=minutes, freq="min").tz_convert("UTC")
    c = np.full(minutes, price)
    return add_session(pd.DataFrame({"ts": ts, "raw_symbol": "CLJ4", "open": c, "high": c + 0.02, "low": c - 0.02,
                                     "close": c, "volume": 1, "vendor": "test"}))


def sig_at(bars: list[int], expire: float = 20.0) -> pd.DataFrame:
    n = len(bars)
    return pd.DataFrame({"side": [1] * n, "limit": [69.90] * n, "stop": [69.80] * n, "target": [70.00] * n,
                         "expire_min": [expire] * n}, index=pd.Index(bars, dtype=int))


def test_window_edges_use_the_signal_bar_close():
    df = frame("2024-03-05 08:28", 330)  # bar k opens 08:28 + k min; its decision is at its close
    # decisions: 08:29 (out), 08:30 (in), 13:29 (in), 13:30 (out)
    k = {"0829": 0, "0830": 1, "1329": 300, "1330": 301}
    out = rth_filter(df, sig_at(list(k.values())))
    assert list(out.index) == [k["0830"], k["1329"]]


def test_order_works_until_1330_at_most():
    df = frame("2024-03-05 08:28", 330)
    out = rth_filter(df, sig_at([1, 291, 300]))  # decisions 08:30, 13:20, 13:29
    assert out["expire_min"].tolist() == [20.0, 10.0, 1.0]


def test_dst_uses_chicago_clock():
    summer = frame("2024-07-09 08:27", 2)  # CDT: bar 0 decides 08:28 (out), bar 1 decides 08:29 (out)
    assert rth_filter(summer, sig_at([0, 1])).empty
    summer = frame("2024-07-09 08:29", 2)  # bar 0 decides 08:30 CT = 13:30 UTC (in)
    assert list(rth_filter(summer, sig_at([0])).index) == [0]


@pytest.mark.parametrize(("through_bar_ct", "fills"), [("13:29", 1), ("13:30", 0)])
def test_engine_order_works_through_1329_and_dies_at_1330(through_bar_ct, fills):
    df = frame("2024-03-05 13:20", 20)
    k = int((pd.Timestamp(f"2024-03-05 {through_bar_ct}") - pd.Timestamp("2024-03-05 13:20")).total_seconds() // 60)
    df.loc[df.index[k], "low"] = 69.80  # trades through the 69.90 limit
    sig = rth_filter(df, sig_at([4]))  # decided 13:25
    assert sig["expire_min"].tolist() == [5.0]
    assert len(backtest(Bars.from_frame(df), sig)) == fills


def test_frozen_params_cannot_be_overridden():
    s = load("purple_levels_rth")
    with pytest.raises(ValueError, match="frozen"):
        s.signals(frame("2024-03-05 08:28", 5), {**s.PARAMS, "levels": "pd"})


def test_empty_signals_pass_through():
    df = frame("2024-03-05 08:28", 5)
    assert rth_filter(df, sig_at([])).empty


@pytest.mark.skipif(not (DATA_DIR / "year=2019.parquet").exists(), reason="needs local CL bars")
def test_rth_signals_are_purple_levels_all_5m_inside_the_window():
    df = add_session(load_bars("2019-01-01", "2019-07-01"))
    rth, base = load("purple_levels_rth"), load("purple_levels")
    got = rth.signals(df, rth.PARAMS)
    ref = base.signals(df, {**base.PARAMS, "levels": "all", "tf": "5m"})
    assert len(got) and set(got.index) <= set(ref.index) and len(got) < len(ref)
    cols = ["side", "limit", "stop", "target"]
    pd.testing.assert_frame_equal(got[cols], ref.loc[got.index, cols])
    assert (got["expire_min"] <= ref.loc[got.index, "expire_min"]).all()
    mins = df["ct_minute"].to_numpy()[got.index.to_numpy()] + 1
    assert ((mins >= 510) & (mins < 810)).all()
    i = got.index[-1]  # point-in-time: same signal with data cut at its bar
    cut = rth.signals(df.iloc[:i + 1], rth.PARAMS)
    assert i in cut.index and cut.loc[i].equals(got.loc[i])
