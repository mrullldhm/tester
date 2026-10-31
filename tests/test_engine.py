"""Broker emulator rules on hand-made bars (prices in ticks)."""

import numpy as np
import pandas as pd
import pytest

from tvtester.config import DEFAULT
from tvtester.data import Bars
from tvtester.engine import LONG, SHORT, run
from tvtester.strategy import Strategy


def make_bars(ohlc, symbols=None):
    n = len(ohlc)
    ts = pd.date_range("2024-03-04 14:00", periods=n, freq="1min", tz="UTC")
    a = np.asarray(ohlc, dtype=np.int64)
    sym = np.asarray(symbols or ["CLJ4"] * n, dtype=object)
    last = np.zeros(n, dtype=bool)
    last[:-1] = sym[:-1] != sym[1:]
    return Bars(ts, ts.as_unit("ms").asi8, a[:, 0], a[:, 1], a[:, 2], a[:, 3], np.ones(n), sym, last)


class Script(Strategy):
    """Runs a dict {bar index: callable(ctx)} at bar closes."""

    def __init__(self, actions):
        super().__init__()
        self.actions = actions

    def prepare(self, bars):
        m = np.zeros(len(bars), dtype=bool)
        m[list(self.actions)] = True
        return m

    def on_bar(self, ctx, i):
        if i in self.actions:
            self.actions[i](ctx)


def one(res):
    assert len(res.trades) == 1
    return res.trades[0]


def test_market_entry_fills_next_open_and_commission():
    bars = make_bars([(100, 101, 99, 100), (105, 106, 104, 105), (110, 111, 109, 110), (120, 121, 119, 120)])
    res = run(Script({0: lambda c: c.entry("L", LONG), 1: lambda c: c.close_all()}), bars)
    t = one(res)
    assert (t.entry_bar, t.entry_price, t.exit_bar, t.exit_price) == (1, 105, 2, 110)
    assert t.profit == pytest.approx(5 * 10 - 4.02)


def test_path_high_first_when_high_is_nearer_open():
    # entry bar 1: open 100, high 103 (3 away), low 95 (5 away) -> O-H-L-C: target 103 hits before stop 96
    bars = make_bars([(100, 100, 100, 100), (100, 103, 95, 99)])
    s = Script({0: lambda c: (c.entry("L", LONG), c.exit("X", "L", stop=96, limit=103))})
    t = one(run(s, bars))
    assert (t.exit_price, t.exit_reason) == (103, "limit")


def test_path_low_first_and_tie_goes_low_first():
    for bar in [(100, 105, 97, 101), (100, 104, 96, 101)]:  # low nearer / equal distance
        bars = make_bars([(100, 100, 100, 100), bar])
        s = Script({0: lambda c: (c.entry("L", LONG), c.exit("X", "L", stop=97 if bar[2] == 97 else 96,
                                                                 limit=bar[1]))})
        assert one(run(s, bars)).exit_reason == "stop"


def test_gap_through_stop_fills_at_open_and_limit_gap_gets_better_price():
    bars = make_bars([(100, 100, 100, 100), (100, 101, 99, 100), (90, 92, 89, 91)])
    s = Script({0: lambda c: (c.entry("L", LONG), c.exit("X", "L", stop=95, limit=110))})
    assert one(run(s, bars)).exit_price == 90
    bars = make_bars([(100, 100, 100, 100), (100, 101, 99, 100), (115, 116, 114, 115)])
    assert one(run(s.__class__(s.actions), bars)).exit_price == 115


def test_profit_loss_ticks_measured_from_fill():
    bars = make_bars([(100, 100, 100, 100), (102, 104, 102, 104), (104, 112, 104, 111)])
    s = Script({0: lambda c: (c.entry("L", LONG), c.exit("X", "L", profit=8, loss=5))})
    t = one(run(s, bars))
    assert (t.entry_price, t.exit_price) == (102, 110)


def test_exit_can_fill_on_entry_bar_after_the_fill():
    bars = make_bars([(100, 100, 100, 100), (100, 100, 94, 96)])
    s = Script({0: lambda c: (c.entry("L", LONG), c.exit("X", "L", stop=95))})
    t = one(run(s, bars))
    assert (t.entry_bar, t.exit_bar, t.exit_price) == (1, 1, 95)


def test_slippage_hits_market_and_stop_not_limit():
    props = DEFAULT.with_slippage(2)
    bars = make_bars([(100, 100, 100, 100), (100, 101, 99, 100), (100, 100, 90, 91)])
    s = Script({0: lambda c: (c.entry("S", SHORT), c.exit("X", "S", stop=110, limit=95))})
    t = one(run(s, bars, props))
    assert (t.entry_price, t.exit_price) == (98, 95)  # sell 2 ticks lower; limit unslipped
    bars = make_bars([(100, 100, 100, 100), (100, 101, 99, 100), (100, 112, 100, 111)])
    t = one(run(Script(s.actions), bars, props))
    assert t.exit_price == 112  # buy stop 110 + 2 ticks


def test_stop_entry_and_activated_stop():
    bars = make_bars([(100, 100, 100, 100), (100, 103, 99, 102), (102, 102, 102, 102)])
    t = one(run(Script({0: lambda c: c.entry("L", LONG, stop=102), 1: lambda c: c.close_all()}), bars))
    assert (t.entry_bar, t.entry_price) == (1, 102)
    # buy stop below the close when placed is triggered: fills at the next open even if that open is lower
    bars = make_bars([(100, 100, 100, 100), (95, 96, 94, 95), (95, 95, 95, 95)])
    t = one(run(Script({0: lambda c: c.entry("L", LONG, stop=98), 1: lambda c: c.close_all()}), bars))
    assert (t.entry_bar, t.entry_price) == (1, 95)


def test_negative_prices():
    bars = make_bars([(-100, -100, -100, -100), (-200, -150, -300, -250), (-250, -250, -250, -250)])
    t = one(run(Script({0: lambda c: c.entry("S", SHORT), 1: lambda c: c.close_all()}), bars))
    assert t.profit == pytest.approx(-(-250 - -200) * 10 - 4.02)


def test_roll_forces_exit_at_last_bar_close():
    bars = make_bars([(100, 100, 100, 100), (100, 101, 99, 101), (130, 131, 129, 130)],
                     symbols=["CLJ4", "CLJ4", "CLK4"])
    t = one(run(Script({0: lambda c: c.entry("L", LONG)}), bars))
    assert (t.exit_bar, t.exit_price, t.exit_reason) == (1, 101, "roll")


def test_opposite_entry_reverses_and_same_direction_is_ignored():
    bars = make_bars([(100,) * 4, (101,) * 4, (102,) * 4, (103,) * 4, (104,) * 4])
    res = run(Script({0: lambda c: c.entry("L", LONG), 1: lambda c: c.entry("L2", LONG),
                      2: lambda c: c.entry("S", SHORT)}), bars)
    assert len(res.trades) == 1 and res.trades[0].exit_price == 103
    assert res.open_trade.direction == SHORT and res.open_trade.entry_price == 103


def test_reversal_keeps_the_incoming_bracket():
    bars = make_bars([(100,) * 4, (100,) * 4, (100, 101, 99, 100), (100, 106, 100, 105)])
    res = run(Script({0: lambda c: c.entry("L", LONG),
                      1: lambda c: (c.entry("S", SHORT), c.exit("XS", "S", stop=105, limit=95))}), bars)
    assert [t.exit_reason for t in res.trades] == ["reverse", "stop"]


def test_exit_stop_through_the_close_when_placed_fills_at_next_open():
    bars = make_bars([(100,) * 4, (100,) * 4, (110, 112, 109, 111)])
    res = run(Script({0: lambda c: c.entry("L", LONG), 1: lambda c: c.exit("X", "L", stop=105)}), bars)
    assert (res.trades[0].exit_bar, res.trades[0].exit_price) == (2, 110)


def test_absolute_and_relative_levels_nearest_wins():
    bars = make_bars([(100,) * 4, (100,) * 4, (100, 112, 100, 111)])
    t = one(run(Script({0: lambda c: (c.entry("L", LONG), c.exit("X", "L", limit=105, profit=10))}), bars))
    assert t.exit_price == 105


def test_unsupported_orders_raise():
    bars = make_bars([(100,) * 4, (100,) * 4])
    with pytest.raises(NotImplementedError):
        run(Script({0: lambda c: c.entry("L", LONG, stop=110, limit=95)}), bars)
    with pytest.raises(NotImplementedError):
        run(Script({0: lambda c: (c.entry("L", LONG), c.exit("A", "L", limit=110), c.exit("B", "L", stop=95))}), bars)


def test_open_trade_counts_in_drawdown_runup_and_buy_hold():
    from tvtester import metrics
    bars = make_bars([(100,) * 4, (100, 120, 50, 60)])
    s = metrics.summary(run(Script({0: lambda c: c.entry("L", LONG)}), bars))
    assert s["max_equity_drawdown"] == 500 and s["max_equity_runup"] == 200
    assert s["buy_hold_return_pct"] == pytest.approx(-40.0)


def test_update_rejects_nan_and_non_cl():
    from tvtester.update import check_bars
    df = pd.DataFrame({"ts": pd.to_datetime(["2026-01-02 14:00"], utc=True), "raw_symbol": ["CLG6"],
                       "open": [float("nan")], "high": [71.0], "low": [69.0], "close": [70.0], "volume": [5]})
    with pytest.raises(ValueError):
        check_bars(df.copy())
    with pytest.raises(ValueError):
        check_bars(df.assign(open=70.0, raw_symbol="MCLG6"))


def test_monthly_returns_mark_open_positions_at_month_end():
    from tvtester import metrics
    ts = pd.DatetimeIndex(["2024-01-31 20:00", "2024-01-31 20:01", "2024-02-01 14:00", "2024-02-01 14:01"], tz="UTC")
    a = np.array([(100,) * 4, (100,) * 4, (150,) * 4, (120,) * 4], dtype=np.int64)
    sym = np.array(["CLH4"] * 4, dtype=object)
    bars = Bars(ts, ts.as_unit("ms").asi8, a[:, 0], a[:, 1], a[:, 2], a[:, 3], np.ones(4), sym, np.zeros(4, bool))
    res = run(Script({0: lambda c: c.entry("L", LONG), 2: lambda c: c.close_all()}), bars)
    r = metrics._monthly_returns(res)
    assert r[0] == pytest.approx(-2.01 / 50_000)  # long filled at 100 on Jan 31, marked at 100 minus entry fee
    assert r[1] == pytest.approx((50_000 + 20 * 10 - 4.02) / (50_000 - 2.01) - 1)  # exit at the next open, 120
