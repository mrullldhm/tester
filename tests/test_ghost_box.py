"""ghost_box (docs/strategies/ghost_box/README.md): overnight box, ghost wick, 08:30-09:00 CT fade, exits."""

import numpy as np
import pandas as pd
import pytest

from cltester.data import Bars, add_session
from cltester.engine import backtest
from cltester.strategy import load
from strategies.ghost_box import ghost_days, mid_target

DAY = "2024-03-05"


def frame() -> pd.DataFrame:
    """2024-03-04 13:00 CT to 2024-03-05 14:00 CT, flat 70.00 with a 70.10 / 69.70 overnight box (0.57% wide), settle
    70.00, and a 5m candle 08:10-08:14 CT that pokes to 70.15 and closes 70.00 (ghost wick above)."""
    ts = pd.date_range(pd.Timestamp("2024-03-04 13:00", tz="America/Chicago"),
                       pd.Timestamp(f"{DAY} 13:59", tz="America/Chicago"), freq="min")
    c = np.full(len(ts), 70.0)
    df = add_session(pd.DataFrame({"ts": ts.tz_convert("UTC"), "raw_symbol": "CLJ4", "open": c, "high": c + 0.01,
                                   "low": c - 0.01, "close": c, "volume": 1, "vendor": "test"}))
    set_bar(df, f"{DAY} 01:00", high=70.10)
    set_bar(df, f"{DAY} 03:00", low=69.70)
    set_bar(df, f"{DAY} 08:12", high=70.15)
    return df


def at(df: pd.DataFrame, ct: str) -> int:
    return int(np.flatnonzero(df["ct"] == pd.Timestamp(ct, tz="America/Chicago"))[0])


def set_bar(df: pd.DataFrame, ct: str, **kw) -> None:
    i = at(df, ct)
    for k, v in kw.items():
        df.loc[i, k] = v


def run(df: pd.DataFrame, **p) -> tuple[pd.DataFrame, pd.DataFrame]:
    s = load("ghost_box")
    params = {**s.PARAMS, **p}
    sig = s.signals(df, params)
    return sig, backtest(Bars.from_frame(df), sig, manage=s.manage)


def test_wick_above_gives_short_at_top_wall_from_0830():
    df = frame()
    sig, _ = run(df)
    assert list(sig.index) == [at(df, f"{DAY} 08:29")]  # works from 08:30
    r = sig.iloc[0]
    assert (r.side, r.limit, r.stop, r.target, r.expire_min) == (-1, 70.10, 70.16, 69.90, 30.0)


def test_entry_close_uses_signal_close():
    sig, _ = run(frame(), entry="close")
    assert sig.iloc[0].limit == 70.00


def test_target_opposite_is_bottom_wall():
    sig, _ = run(frame(), target="opposite")
    assert sig.iloc[0].target == 69.70


def test_poke_must_go_strictly_through():
    df = frame()
    set_bar(df, f"{DAY} 08:12", high=70.10)
    assert ghost_days(df).set_index("day").loc[pd.Timestamp(DAY), "status"] == "no_push"


def test_push_closing_outside_breaks_the_box():
    df = frame()
    set_bar(df, f"{DAY} 08:14", close=70.12, high=70.12)
    assert ghost_days(df).set_index("day").loc[pd.Timestamp(DAY), "status"] == "broken"
    assert run(df)[0].empty


def test_close_outside_after_wick_before_signal_kills_setup():
    df = frame()
    set_bar(df, f"{DAY} 08:24", close=69.60, low=69.60)  # 08:20 candle closes below the bottom wall
    assert ghost_days(df).set_index("day").loc[pd.Timestamp(DAY), "status"] == "broken_after"


@pytest.mark.parametrize(("settle", "trades"), [(70.00, 1), (69.60, 0)])  # gap 0% vs 0.57%
def test_gap_filter(settle, trades):
    df = frame()
    set_bar(df, "2024-03-04 13:29", close=settle)
    assert len(run(df)[0]) == trades


def test_narrow_box_is_skipped():
    df = frame()
    set_bar(df, f"{DAY} 03:00", low=69.90)  # width 0.20 / 70 = 0.29%
    assert run(df)[0].empty


def test_wick_after_window_is_no_trade():
    df = frame()
    set_bar(df, f"{DAY} 08:12", high=70.01)
    set_bar(df, f"{DAY} 08:57", high=70.15)  # 08:55 candle completes at 09:00: no window left
    assert ghost_days(df).set_index("day").loc[pd.Timestamp(DAY), "status"] == "late"


def test_roll_inside_box_is_unusable():
    df = frame()
    df.loc[: at(df, f"{DAY} 02:00"), "raw_symbol"] = "CLH4"
    assert ghost_days(df).set_index("day").loc[pd.Timestamp(DAY), "status"] == "roll"


def test_5m_close_above_wall_exits_at_next_open():
    df = frame()
    set_bar(df, f"{DAY} 08:40", high=70.10)  # retest fills the 70.10 sell limit
    set_bar(df, f"{DAY} 08:49", close=70.11, high=70.12)  # 08:45 candle closes above the wall, below the stop
    _, t = run(df)
    assert len(t) == 1
    tr = t.iloc[0]
    assert tr.entry == 70.10 and tr.reason == "manage"
    assert tr.exit_ts == pd.Timestamp(f"{DAY} 08:50", tz="America/Chicago")


def test_time_exit_at_1330():
    df = frame()
    set_bar(df, f"{DAY} 08:40", high=70.10)
    _, t = run(df)
    tr = t.iloc[0]
    assert tr.reason == "manage" and tr.exit_ts == pd.Timestamp(f"{DAY} 13:30", tz="America/Chicago")


def test_stop_beyond_wick():
    df = frame()
    set_bar(df, f"{DAY} 08:40", high=70.10)
    set_bar(df, f"{DAY} 08:42", high=70.16)
    _, t = run(df)
    assert t.iloc[0].reason == "stop" and t.iloc[0].exit == 70.16


def test_fixed_params_refused():
    s = load("ghost_box")
    with pytest.raises(ValueError):
        s.signals(frame(), {**s.PARAMS, "gap_pct": 1.0})


def test_roll_after_signal_does_not_change_the_signal():
    df = frame()
    before = run(df)[0]
    df.loc[at(df, f"{DAY} 10:00"):, "raw_symbol"] = "CLK4"
    assert run(df)[0].equals(before)


def test_bars_after_signal_do_not_change_the_signal():
    df = frame()
    before = run(df)[0]
    set_bar(df, f"{DAY} 08:31", high=72.0, low=68.0, close=68.0)
    assert run(df)[0].equals(before)


def test_missing_0829_bar_gives_no_order_before_0830():
    df = frame().drop(index=[at(frame(), f"{DAY} 08:29")]).reset_index(drop=True)
    assert run(df)[0].empty


@pytest.mark.parametrize(("top", "bot", "side", "mid"), [(10, 4, 1, 7), (11, 4, 1, 7), (11, 4, -1, 8), (10, 4, -1, 7)])
def test_mid_target_half_tick_rounds_toward_entry(top, bot, side, mid):
    assert mid_target(top, bot, side) == mid
