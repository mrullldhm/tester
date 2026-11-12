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


def test_target_at_open_beats_later_stop_in_same_bar():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.50, 70.55, 69.70, 69.75), FLAT])
    t = backtest(b, sig(0))
    r = t.iloc[0]
    assert (r["reason"], r["exit"]) == ("target", 70.50)
    assert r["mae"] == pytest.approx(-20 - 4.04)  # fill bar low 69.98; the later 69.70 is after the exit


def test_path_records_open_and_worst_per_bar():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.05, 70.10, 69.90, 70.00), (67.00, 67.10, 66.90, 67.00)])
    t = backtest(b, sig(0, stop=60.0, target=80.0))
    opened, worst = t["path"].iat[0]
    assert list(np.round(opened + 4.04, 2)) == [0, 50, -3000]
    assert list(np.round(worst + 4.04, 2)) == [-20, -100, -3100]  # low 66.90 before the 67.00 close exit


# --- trade management hook and partial exit ---

def test_manage_moves_stop_from_next_bar():
    # fill bar 1 at 70.00; bar 2 high 70.30; manage moves the stop to 70.10 once best >= 70.30 (seen from bar 3)
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.05, 70.30, 70.05, 70.25), (70.20, 70.22, 70.05, 70.08),
                  FLAT])

    def manage(ctx):
        return (7010 if ctx.best >= 7030 else ctx.S), False

    t = backtest(b, sig(0, target=np.nan), manage=manage)
    assert (t["reason"].iat[0], t["exit"].iat[0], t["exit_bar"].iat[0]) == ("stop", 70.10, 3)


def test_manage_sees_only_previous_bars():
    seen = []
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.05, 70.30, 70.05, 70.25), (70.20, 70.35, 70.15, 70.30),
                  FLAT])

    def manage(ctx):
        seen.append((ctx.m, ctx.best))
        return ctx.S, False

    backtest(b, sig(0, target=np.nan), manage=manage)
    assert seen[:2] == [(2, 7002), (3, 7030)]  # best on bar m excludes bar m's own high


def test_manage_close_now_exits_at_open():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.05, 70.10, 70.01, 70.06), (70.04, 70.30, 70.00, 70.20)])
    t = backtest(b, sig(0, target=np.nan), manage=lambda ctx: (ctx.S, ctx.m == 3))
    assert (t["reason"].iat[0], t["exit"].iat[0]) == ("manage", 70.04)


def test_manage_stop_for_short_is_in_side_space():
    # short at 70.00, manage moves the stop down to 69.95 (side space: -6995)
    df, b = make([FLAT, (69.98, 70.02, 69.98, 70.00), (69.95, 69.96, 69.80, 69.85), (69.85, 69.97, 69.84, 69.90)])
    t = backtest(b, sig(0, side=-1, limit=70.00, stop=70.20, target=np.nan),
                 manage=lambda ctx: (ctx.to_side(6995) if ctx.m >= 3 else ctx.S, False))
    assert (t["reason"].iat[0], t["exit"].iat[0], t["net"].iat[0]) == ("stop", 69.95, pytest.approx(50 - 4.04))


def test_partial_exit_then_target():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.05, 70.21, 70.05, 70.15), (70.15, 70.40, 70.10, 70.35)])
    t = backtest(b, sig(0, qty=2, part_qty=1, part_target=70.20))
    r = t.iloc[0]
    assert (r["reason"], r["exit"], r["part_exit"]) == ("target", 70.40, 70.20)
    assert r["net"] == pytest.approx(200 + 400 - 2 * 4.04)


def test_partial_exit_then_stop():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.05, 70.21, 70.05, 70.15), (70.10, 70.12, 69.70, 69.75)])
    t = backtest(b, sig(0, qty=2, part_qty=1, part_target=70.20))
    r = t.iloc[0]
    assert (r["reason"], r["exit"], r["part_exit"]) == ("stop", 69.80, 70.20)
    assert r["net"] == pytest.approx(200 - 200 - 2 * 4.04)


def test_stop_beats_partial_in_same_bar():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.00, 70.25, 69.75, 70.00), FLAT])
    t = backtest(b, sig(0, qty=2, part_qty=1, part_target=70.20))
    r = t.iloc[0]
    assert (r["reason"], r["exit"]) == ("stop", 69.80) and np.isnan(r["part_exit"])
    assert r["net"] == pytest.approx(-400 - 2 * 4.04)


def test_partial_needs_valid_size_and_price():
    df, b = make([FLAT] * 3)
    with pytest.raises(ValueError):
        backtest(b, sig(0, qty=1, part_qty=1, part_target=70.2))
    with pytest.raises(ValueError):
        backtest(b, sig(0, qty=2, part_qty=1, part_target=70.6))  # beyond the target


def test_partial_at_the_open_and_its_path():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.25, 70.30, 70.01, 70.10), (70.15, 70.40, 70.10, 70.35)])
    t = backtest(b, sig(0, qty=2, part_qty=1, part_target=70.20))
    r = t.iloc[0]
    assert (r["part_exit"], r["reason"], r["exit"]) == (70.25, "target", 70.40)
    assert r["net"] == pytest.approx(250 + 400 - 2 * 4.04)
    worst = r["path"][1]
    assert worst[1] == pytest.approx(260 - 2 * 4.04)  # after the partial at the open, the low counts for 1 contract
    assert r["mae"] == pytest.approx(-40 - 2 * 4.04)  # the fill bar low, both contracts


def test_mfe_counts_the_partial_leg_at_its_exit_price():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.05, 70.21, 70.05, 70.15), (70.15, 70.40, 70.10, 70.35)])
    r = backtest(b, sig(0, qty=2, part_qty=1, part_target=70.20)).iloc[0]
    assert r["mfe"] == pytest.approx(r["net"])  # the target was the best the trade could show


def test_manage_sees_fewer_contracts_after_the_partial():
    seen = []
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.05, 70.21, 70.05, 70.15), (70.15, 70.18, 70.10, 70.12),
                  (70.12, 70.40, 70.10, 70.35)])

    def manage(ctx):
        seen.append(ctx.qty)
        return ctx.S, False

    backtest(b, sig(0, qty=2, part_qty=1, part_target=70.20), manage=manage)
    assert seen == [2, 1, 1]


def test_stop_moved_beyond_the_open_exits_at_the_open():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), (70.10, 70.20, 70.08, 70.15), (70.05, 70.30, 70.04, 70.25)])
    t = backtest(b, sig(0, target=np.nan), manage=lambda ctx: (7006 if ctx.m == 3 else ctx.S, False))
    assert (t["reason"].iat[0], t["exit"].iat[0], t["exit_bar"].iat[0]) == ("stop", 70.05, 3)


def test_flatten_beats_manage_close():
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), FLAT, FLAT], start="2024-03-05 15:07")
    t = backtest(b, sig(0, target=np.nan), manage=lambda ctx: (ctx.S, True if ctx.m == 3 else False))
    assert (t["reason"].iat[0], t["exit_bar"].iat[0]) == ("flatten", 3)


@pytest.mark.parametrize("bad", [7010.5, float("nan")])
def test_manage_must_return_whole_ticks(bad):
    df, b = make([FLAT, (70.02, 70.02, 69.98, 70.00), FLAT, FLAT])
    with pytest.raises(ValueError):
        backtest(b, sig(0, target=np.nan), manage=lambda ctx: (bad, False))


@pytest.mark.parametrize("side", [1, -1])
def test_manage_accepts_stops_across_zero(side):
    # entry at $0.10 with the stop on the other side of zero: valid, a no-op manager must not reject it
    rows = [(0.12, 0.12, 0.08, 0.10), (0.10, 0.12, 0.08, 0.10), (0.10, 0.12, 0.08, 0.10), (0.10, 0.12, 0.08, 0.10)]
    df, b = make(rows)
    s = sig(0, side=side, limit=0.10, stop=0.10 - side * 0.20, target=np.nan)
    plain = backtest(b, s)
    managed = backtest(b, s, manage=lambda ctx: (ctx.S, False))
    cols = ["entry", "exit", "reason", "net"]
    assert managed[cols].equals(plain[cols])


def test_manage_stop_at_zero_ticks_is_valid():
    df, b = make([(0.12, 0.12, 0.08, 0.10), (0.10, 0.12, 0.08, 0.10), (0.05, 0.06, -0.02, 0.00), FLAT])
    t = backtest(b, sig(0, limit=0.10, stop=-0.10, target=np.nan), manage=lambda ctx: (0, False))
    assert (t["reason"].iat[0], t["exit"].iat[0]) == ("stop", 0.00)


def make_at(minutes, rows, start="2024-03-05 08:00"):
    """1m bars only at the given minutes after start (missing minutes)."""
    ts = (pd.Timestamp(start, tz="America/Chicago") + pd.to_timedelta(minutes, unit="min")).tz_convert("UTC")
    o, h, l, c = zip(*rows, strict=True)
    df = add_session(pd.DataFrame({"ts": ts, "raw_symbol": "CLJ4", "open": o, "high": h, "low": l, "close": c,
                                   "volume": 1, "vendor": "test"}))
    return df, Bars.from_frame(df)


def test_expire_min_counts_clock_time_not_bars():
    # signal at 08:29, 15 minutes to work (until 08:44); the next bar is 09:00 and touches the limit: no fill
    df, b = make_at([29, 60, 61], [FLAT, (70.02, 70.02, 69.98, 70.00), FLAT])
    assert backtest(b, sig(0, expire_min=15)).empty
    assert len(backtest(b, sig(0, expire=15))) == 1  # bar-count expiry would have filled it


def test_expire_min_fills_inside_the_window_and_ignores_the_bar_limit():
    df, b = make_at(list(range(40)), [FLAT] * 39 + [(70.02, 70.02, 69.98, 70.00)])
    t = backtest(b, sig(0, expire_min=39))  # last working minute 08:39 = bar 39, past the 30-bar default
    assert t["entry_bar"].iat[0] == 39
    assert backtest(b, sig(0, expire_min=38)).empty


def test_timed_order_blocks_signals_until_its_deadline_across_a_gap():
    # Codex repro: order from 08:00 works until 08:15; bars 08:00-08:02 then 08:17. A signal at 08:02 is placed while
    # the first order still works, so it is ignored even though the first order never fills.
    above = (70.10, 70.12, 70.08, 70.10)
    df, b = make_at([0, 1, 2, 17, 18], [above, above, above, (70.02, 70.02, 69.98, 70.00), FLAT])
    first = sig(0, limit=70.00, stop=69.80, expire_min=15)
    second = sig(2, limit=70.00, stop=69.80, expire_min=15)
    assert backtest(b, pd.concat([first, second])).empty
    third = sig(3, limit=70.10, stop=69.80, target=70.40, expire_min=15)  # 08:17: after the deadline, accepted
    assert list(backtest(b, pd.concat([first, third]))["signal_bar"]) == [3]
