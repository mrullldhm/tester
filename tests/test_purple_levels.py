"""purple_levels (docs/strategies/purple_levels/README.md): pd equals purple_pa, levels fixed at the day's open,
point-in-time signals, previous-week levels from raw bars."""

import numpy as np
import pandas as pd
import pytest

from cltester.config import DATA_DIR
from cltester.data import add_session, load_bars
from cltester.indicators import tf_candles
from cltester.strategy import load
from strategies.purple_levels import FAMILIES, UNIONS, previous_week_levels

pytestmark = pytest.mark.skipif(not (DATA_DIR / "year=2019.parquet").exists(), reason="needs local CL bars")


@pytest.fixture(scope="module")
def bars():
    return add_session(load_bars("2019-01-01", "2019-09-01"))


@pytest.fixture(scope="module")
def strat():
    return load("purple_levels")


def run(s, df, fam, tf="15m"):
    return s.signals(df, {**s.PARAMS, "levels": fam, "tf": tf})


@pytest.mark.parametrize("tf", ["15m", "5m"])
def test_pd_family_is_purple_pa(bars, strat, tf):
    pp = load("purple_pa")
    ref = pp.signals(bars, {**pp.PARAMS, "tf": tf})
    got = run(strat, bars, "pd", tf)
    pd.testing.assert_frame_equal(got.reset_index(), ref.reset_index(), check_dtype=False)


@pytest.mark.parametrize("fam", FAMILIES)
def test_signal_exists_with_data_cut_at_its_bar(bars, strat, fam):
    sig = run(strat, bars, fam)
    assert len(sig)
    for i in list(sig.index[:2]) + list(sig.index[-2:]):
        cut = run(strat, bars.iloc[:i + 1], fam)
        assert i in cut.index and cut.loc[i].equals(sig.loc[i])


def test_previous_week_levels_come_from_the_prior_trading_week(bars):
    days = np.array(["2019-03-11", "2019-03-15"], dtype="datetime64[ns]")  # Monday and Friday of one week
    ok, hi, lo = previous_week_levels(bars, days)
    prev = bars[(bars["trading_day"] >= "2019-03-04") & (bars["trading_day"] <= "2019-03-08")]
    assert ok.all() and (hi == round(prev["high"].max() * 100)).all() and (lo == round(prev["low"].min() * 100)).all()


def test_all_family_has_at_least_the_trades_of_each_family(bars, strat):
    every = set(run(strat, bars, "all").index)
    parts = set().union(*(run(strat, bars, f).index for f in UNIONS["all"]))
    assert every <= parts  # a union signal always comes from one family; one position at a time drops some


def test_unknown_family_is_refused(bars, strat):
    with pytest.raises(ValueError):
        run(strat, bars.iloc[:3000], "zz")


def test_families_and_unions_are_the_declared_set():
    assert FAMILIES == ("pd", "pw", "sw4h", "sw1d", "all", "sw", "nopd")
    assert UNIONS == {"all": ("pd", "pw", "sw4h", "sw1d"), "sw": ("sw4h", "sw1d"), "nopd": ("pw", "sw4h", "sw1d")}


def test_first_loaded_week_is_never_a_previous_week(bars):
    mid = bars[bars["trading_day"] >= "2019-03-06"].reset_index(drop=True)  # starts on a Wednesday
    days = np.array(["2019-03-06", "2019-03-11", "2019-03-18"], dtype="datetime64[ns]")
    ok, _, _ = previous_week_levels(mid, days)
    assert list(ok) == [False, False, True]


def test_union_counts_an_equal_price_once(bars, strat):
    cd = tf_candles(bars, "5m")
    cd = cd[cd["avail"] < len(bars)].reset_index(drop=True)
    days, day_id = np.unique(cd["day"].to_numpy(), return_inverse=True)
    starts = np.flatnonzero(np.r_[True, day_id[1:] != day_id[:-1]])
    for fam in UNIONS:
        for lv in strat.day_levels(bars, cd, days, day_id, starts, fam):
            assert len(lv) == len(set(lv))


@pytest.mark.parametrize("fam", ["sw4h", "sw1d", "pw"])
def test_day_levels_ignore_bars_after_the_open(bars, strat, fam):
    cd = tf_candles(bars, "5m")
    cd = cd[cd["avail"] < len(bars)].reset_index(drop=True)
    days, day_id = np.unique(cd["day"].to_numpy(), return_inverse=True)
    starts = np.flatnonzero(np.r_[True, day_id[1:] != day_id[:-1]])
    base = strat.day_levels(bars, cd, days, day_id, starts, fam)
    k = 40  # a day in the middle of the sample
    cut = bars.iloc[:cd["first"].iloc[starts[k]] + 1]  # only the day's first 1m bar
    cd2 = tf_candles(cut, "5m")
    cd2 = cd2[cd2["avail"] < len(cut)].reset_index(drop=True)
    days2, day_id2 = np.unique(cd2["day"].to_numpy(), return_inverse=True)
    starts2 = np.flatnonzero(np.r_[True, day_id2[1:] != day_id2[:-1]])
    early = strat.day_levels(cut, cd2, days2, day_id2, starts2, fam)
    assert early[k - 1] == base[k - 1]  # the previous day's levels, known by then, are unchanged
