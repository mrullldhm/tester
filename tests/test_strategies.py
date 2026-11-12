import numpy as np
import pandas as pd
import pytest

from cltester.data import Bars, add_session
from cltester.engine import backtest
from cltester.strategy import load


def trades(rows, part_exit=None):
    """rows of (trading_day, net, final-leg ticks) in entry order; part_exit per row (NaN = no partial)."""
    d, net, ticks = zip(*rows, strict=True)
    return pd.DataFrame({"trading_day": pd.to_datetime(d), "net": net, "ticks": ticks,
                         "part_exit": np.nan if part_exit is None else part_exit})


def test_ict_day_rules_cut_off_the_rest_of_the_day():
    s = load("ict_ea")
    p = s.PARAMS
    day = "2024-03-05"
    # max 3 trades a day
    assert len(s.day_rules(trades([(day, 10, 1)] * 5), p)) == 3
    # 2 losses in a row end the day; a win in between resets the count
    many = {**p, "max_trades": 10}
    out = s.day_rules(trades([(day, -10, -1), (day, 10, 1), (day, -10, -1), (day, -10, -1), (day, 10, 1)]), many)
    assert len(out) == 4
    out = s.day_rules(trades([(day, -10, -1), (day, -10, -1), (day, 50, 5)]), p)
    assert len(out) == 2
    # day loss and day gain limits stop new trades
    assert len(s.day_rules(trades([(day, -1000, -100), (day, 10, 1)]), p)) == 1
    assert len(s.day_rules(trades([(day, 800, 80), (day, 10, 1)]), p)) == 1
    # a new day starts fresh
    out = s.day_rules(trades([(day, -10, -1), (day, -10, -1), (day, 5, 1), ("2024-03-06", 5, 1)]), p)
    assert list(out.index) == [0, 1, 3]


def test_day_rules_default_keeps_every_trade():
    s = load("purple_pa")
    t = trades([("2024-03-05", -10, -1)] * 4)
    assert s.day_rules(t, s.PARAMS).equals(t)


NEW = ["xtley_gap", "swapnil_momentum", "swapnil_hm", "ict_ea", "scribd_supertrend", "purple_pa"]


@pytest.mark.parametrize("name", NEW)
@pytest.mark.parametrize("n_bars", [0, 3, 20])
def test_warm_up_without_a_complete_candle_gives_no_trades(name, n_bars):
    ts = pd.date_range(pd.Timestamp("2024-03-05 08:00", tz="America/Chicago"), periods=n_bars,
                       freq="min").tz_convert("UTC")
    c = 70 + np.arange(n_bars) * 0.01
    df = add_session(pd.DataFrame({"ts": ts, "raw_symbol": "CLJ4", "open": c, "high": c + 0.02, "low": c - 0.02,
                                   "close": c, "volume": 1, "vendor": "test"}))
    s = load(name)
    sig = s.signals(df, s.PARAMS)
    assert len(sig) == 0
    assert len(s.day_rules(backtest(Bars.from_frame(df), sig, manage=s.manage), s.PARAMS)) == 0


def sparse_frame(minutes, closes, opens, day="2024-03-05"):
    """1m bars only at the given CT minutes after 08:00 (missing minutes are real in quiet markets)."""
    ts = (pd.Timestamp(f"{day} 08:00", tz="America/Chicago") + pd.to_timedelta(minutes, unit="min")).tz_convert("UTC")
    o, c = np.asarray(opens, float), np.asarray(closes, float)
    return add_session(pd.DataFrame({"ts": ts, "raw_symbol": "CLJ4", "open": o, "high": np.maximum(o, c) + 0.01,
                                     "low": np.minimum(o, c) - 0.01, "close": c, "volume": 1, "vendor": "test"}))


def test_candles_completing_on_one_bar_give_one_signal():
    # Codex repro: with 08:29 and 08:30-08:43 missing, two 15m candles complete on the same 1m bar
    df = sparse_frame([0, 14, 15, 28, 44, 45], closes=[70.01, 70.05, 70.06, 70.10, 70.15, 70.16],
                      opens=[70.00, 70.02, 70.05, 70.07, 70.11, 70.15])
    s = load("swapnil_momentum")
    p = {**s.PARAMS, "tf": "15m"}
    sig = s.signals(df, p)
    assert sig.index.is_unique and len(sig) >= 1
    backtest(Bars.from_frame(df), sig)


@pytest.mark.parametrize("name", NEW)
def test_sparse_random_data_runs_end_to_end(name):
    rng = np.random.default_rng(7)
    minutes = np.sort(rng.choice(np.arange(60 * 24 * 12), 60 * 24 * 12 * 6 // 10, replace=False))
    walk = 70 + np.cumsum(rng.normal(0, 0.03, len(minutes)))
    df = sparse_frame(minutes, closes=np.round(walk, 2), opens=np.round(np.r_[70, walk[:-1]], 2))
    s = load(name)
    for tf_value in s.GRID.get("tf", [None]):
        p = s.PARAMS if tf_value is None else {**s.PARAMS, "tf": tf_value}
        sig = s.signals(df, p)
        assert sig.index.is_unique
        s.day_rules(backtest(Bars.from_frame(df), sig, manage=s.manage), p)


def test_momentum_order_expires_after_one_candle_of_clock_time():
    # Codex repro: 15m signal at 08:29, next bar 09:00 touches the limit, the one-candle order expired at 08:45
    df = sparse_frame([0, 14, 15, 29, 60, 61], closes=[70.01, 70.05, 70.06, 70.10, 70.00, 70.05],
                      opens=[70.00, 70.02, 70.05, 70.07, 70.10, 70.00])
    s = load("swapnil_momentum")
    p = {**s.PARAMS, "tf": "15m"}
    sig = s.signals(df, p)
    assert 3 in sig.index  # the 08:15-08:29 candle completes at bar 3
    assert backtest(Bars.from_frame(df), sig.loc[[3]]).empty


def test_purple_levels_come_from_raw_bars_of_the_previous_day():
    from strategies.purple_pa import previous_day_levels

    t = pd.to_datetime(["2024-03-05 15:45", "2024-03-05 15:58", "2024-03-05 17:00", "2024-03-05 17:01"]).tz_localize(
        "America/Chicago").tz_convert("UTC")
    c = np.array([70.0, 71.0, 72.0, 72.1])
    df = add_session(pd.DataFrame({"ts": t, "raw_symbol": "CLJ4", "open": c, "high": c + 0.02, "low": c - 0.02,
                                   "close": c, "volume": 1, "vendor": "test"}))
    ok, hi, lo = previous_day_levels(df, np.array(pd.to_datetime(["2024-03-05", "2024-03-06"]), dtype="datetime64[ns]"))
    assert list(ok) == [False, True]
    assert (hi[1], lo[1]) == (7102, 6998)  # 2024-03-05 extremes, including its late candle


def test_ict_profitable_partial_resets_the_loss_streak():
    # Codex repro: loss, then a trade whose partial wins but final leg loses, then an eligible trade
    s = load("ict_ea")
    day = "2024-03-05"
    rows = [(day, -100, -10), (day, 50, -2), (day, 30, 3)]
    out = s.day_rules(trades(rows, part_exit=[np.nan, 70.2, np.nan]), s.PARAMS)
    assert len(out) == 3  # the streak is 1 after trade 2, not 2
    out = s.day_rules(trades(rows), s.PARAMS)
    assert len(out) == 2  # without the partial, two losing legs in a row end the day
