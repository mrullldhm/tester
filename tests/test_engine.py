import numpy as np
import pandas as pd
import pytest

from cltester.data import Bars, add_session
from cltester.engine import backtest


def make(rows, start="2024-03-05 08:00", sym=None):
    """rows of (open, high, low, close) in $; 1-minute bars from a CT start time."""
    ts = pd.date_range(pd.Timestamp(start, tz="America/Chicago"), periods=len(rows), freq="min").tz_convert("UTC")
    o, h, l, c = zip(*rows, strict=True)
    df = pd.DataFrame({"ts": ts, "raw_symbol": sym or ["CLJ4"] * len(rows), "open": o, "high": h, "low": l,
                       "close": c, "volume": 1, "vendor": "test"})
    df = add_session(df)
    return df, Bars.from_frame(df)


def sig(i, side=1, limit=70.0, stop=69.8, target=70.4, **kw):
    return pd.DataFrame({"side": side, "limit": limit, "stop": stop, "target": target, **kw}, index=[i])


FLAT = (70.10, 70.12, 70.08, 70.10)


def test_limit_fills_on_touch():
    df, b = make([FLAT, (70.05, 70.06, 70.01, 70.02), (70.05, 70.06, 70.00, 70.02), *[FLAT] * 3])
    t = backtest(b, sig(0))
    assert (t["entry_bar"].iat[0], t["entry"].iat[0]) == (2, 70.00)  # bar 1 stayed 1 tick above


def test_gap_below_limit_fills_at_open():
    df, b = make([FLAT, (69.95, 69.96, 69.90, 69.92), *[FLAT] * 3])
    t = backtest(b, sig(0, stop=69.5))
    assert t["entry"].iat[0] == 69.95


def test_target_and_fees():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.10, 70.41, 70.05, 70.40), FLAT])
    t = backtest(b, sig(0))
    r = t.iloc[0]
    assert (r["reason"], r["exit"], r["ticks"]) == ("target", 70.40, 40)
    assert r["net"] == pytest.approx(400 - 4.04)


def test_target_fills_on_touch():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.10, 70.39, 70.05, 70.30), (70.30, 70.40, 70.25, 70.30)])
    t = backtest(b, sig(0))
    assert (t["reason"].iat[0], t["exit_bar"].iat[0], t["exit"].iat[0]) == ("target", 3, 70.40)


def test_stop_beats_target_in_same_bar():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.00, 70.50, 69.70, 70.00), FLAT])
    t = backtest(b, sig(0))
    assert (t["reason"].iat[0], t["exit"].iat[0]) == ("stop", 69.80)


def test_stop_on_fill_bar():
    df, b = make([FLAT, (70.02, 70.02, 69.75, 69.76), FLAT])
    t = backtest(b, sig(0))
    assert (t["exit_bar"].iat[0], t["reason"].iat[0], t["exit"].iat[0]) == (1, "stop", 69.80)
    assert t["mae"].iat[0] == pytest.approx(-200 - 4.04)


def test_stop_gap_fills_at_open():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (69.50, 69.60, 69.40, 69.50), FLAT])
    t = backtest(b, sig(0))
    assert t["exit"].iat[0] == 69.50  # the market jumped over the stop: real traded price, not slippage


def test_short_mirror():
    df, b = make([FLAT, (70.18, 70.22, 70.17, 70.20), (70.10, 70.12, 69.79, 69.80), FLAT])
    t = backtest(b, sig(0, side=-1, limit=70.20, stop=70.40, target=69.80))
    r = t.iloc[0]
    assert (r["entry"], r["exit"], r["reason"], r["ticks"]) == (70.20, 69.80, "target", 40)
    assert r["mae"] == pytest.approx(-20 - 4.04)  # high 70.22 on the fill bar


def test_flatten_at_1510_ct():
    rows = [FLAT, (70.02, 70.02, 69.98, 70.00), FLAT, (70.05, 70.06, 70.04, 70.05)]
    df, b = make(rows, start="2024-03-05 15:07")
    t = backtest(b, sig(0))
    assert (t["reason"].iat[0], t["exit"].iat[0], t["exit_bar"].iat[0]) == ("flatten", 70.05, 3)


def test_no_entry_after_flatten_time():
    df, b = make([FLAT, (70.02, 70.02, 69.90, 70.00), FLAT], start="2024-03-05 15:09")
    assert backtest(b, sig(0)).empty


def test_roll_exit_on_contract_change():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.10, 70.15, 70.05, 70.12), (71.0, 71.1, 70.9, 71.0)],
                 sym=["CLJ4", "CLJ4", "CLJ4", "CLK4"])
    t = backtest(b, sig(0))
    assert (t["reason"].iat[0], t["exit"].iat[0]) == ("roll", 70.12)


def test_order_expires_and_signal_ignored_in_trade():
    df, b = make([FLAT, FLAT, FLAT, (70.02, 70.02, 69.98, 70.00), *[FLAT] * 3])
    assert backtest(b, sig(0, expire=2)).empty
    s = pd.concat([sig(0), sig(4)])
    t = backtest(b, s)
    assert len(t) == 1  # the second signal arrives while the first trade is open


def test_time_exit():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), FLAT, FLAT, FLAT])
    t = backtest(b, sig(0, hold=2))
    assert (t["reason"].iat[0], t["exit_bar"].iat[0]) == ("time", 3)


def test_bad_bracket_rejected():
    df, b = make([FLAT, FLAT])
    with pytest.raises(ValueError):
        backtest(b, sig(0, stop=70.1))


def test_trading_day_rolls_at_1700_ct():
    ts = pd.Series(pd.to_datetime(["2024-03-10 16:59", "2024-03-10 17:00", "2024-11-01 16:59"])
                   ).dt.tz_localize("America/Chicago").dt.tz_convert("UTC")
    df = add_session(pd.DataFrame({"ts": ts}))
    assert list(df["trading_day"].dt.strftime("%a %d")) == ["Sun 10", "Mon 11", "Fri 01"]
    assert list(df["sess_minute"]) == [1439, 0, 1439]
    assert np.all(df["ct_minute"].to_numpy() == [1019, 1020, 1019])


def test_nan_prices_rejected():
    df, b = make([FLAT, FLAT])
    with pytest.raises(ValueError):
        backtest(b, sig(0, stop=np.nan))


def test_mae_never_better_than_result():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.0, 70.05, 69.90, 69.90), FLAT])
    t = backtest(b, sig(0, hold=1))
    assert t["net"].iat[0] == pytest.approx(-100 - 4.04)
    assert t["mae"].iat[0] <= t["net"].iat[0]


def test_open_trade_at_end_of_data_is_data_end():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.05, 70.10, 70.01, 70.09)])
    t = backtest(b, sig(0))
    assert (t["reason"].iat[0], t["exit"].iat[0]) == ("data_end", 70.09)
