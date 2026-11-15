"""Swing Point Failure Reversal rules (docs/strategies/swing_point_failure_reversal/README.md), one test per rule.

Side space of an SPF short (prices in ticks, bar t opens at minute t): the reversal is a long."""

import numpy as np
import pandas as pd
import pytest

from cltester.data import add_session
from strategies.swing_point_failure import MIN_NS, NO_EXPIRY
from strategies.swing_point_failure import Strategy as Spf
from strategies.swing_point_failure_reversal import NEVER, Source, Strategy, Swing, Tf, _candle_bars, scan

N = 20
NAT = np.iinfo(np.int64).min
TS = np.arange(N, dtype=np.int64) * MIN_NS


def base():
    """SPF short signal at bar 5, stop H = 120 (bar 3). Low 100 at bar 7. Bar 12 touches H (high 121), closes 118."""
    hi, lo, cl = np.full(N, 115.0), np.full(N, 110.0), np.full(N, 112.0)
    hi[3] = 120
    lo[7] = 100
    hi[12], cl[12] = 121, 118
    m5 = np.arange(N) // 5 * 5 + 4
    tfs = {"1m": Tf(np.arange(N), np.arange(N), Swing(MIN_NS, np.full(N, NAT))),
           "5m": Tf(m5, m5.copy(), Swing(5 * MIN_NS, np.full(N, NAT)))}
    return hi, lo, cl, tfs


def run(hi, lo, cl, tfs, tf="1m", nxt=N, last=N - 1, risk=25, sl=None):
    return scan(hi, lo, cl, TS, Source(5, 120.0, tf, nxt, last), tfs, risk, 2, sl)


def test_touch_buys_at_the_trigger_close_with_stop_at_the_low_since_h():
    r = run(*base())
    assert (r["touch"], r["end"], r["why"]) == (12, 12, "trigger")
    assert (r["limit"], r["stop"], r["target"], r["expire"]) == (118, 100, 168, NO_EXPIRY)


def test_a_touch_counts():
    hi, lo, cl, tfs = base()
    hi[12] = 120
    assert run(hi, lo, cl, tfs)["why"] == "trigger"


def test_wide_stop_puts_the_limit_risk_ticks_above_the_stop():
    r = run(*base(), risk=15)
    assert (r["limit"], r["stop"], r["target"]) == (115, 100, 145)  # target = limit + 2 x 15


def test_newer_swing_high_moves_the_stop_to_the_low_after_it():
    hi, lo, cl, tfs = base()
    lo[10] = 108
    tfs["1m"].swing.sh_ts[12] = TS[9]  # lower high LH at bar 9, confirmed by the trigger close
    r = run(hi, lo, cl, tfs)
    assert (r["stop"], r["limit"], r["ref_ts"]) == (108, 118, TS[9])


def test_swing_high_before_h_is_ignored():
    hi, lo, cl, tfs = base()
    lo[2] = 90
    tfs["1m"].swing.sh_ts[12] = TS[1]
    assert run(hi, lo, cl, tfs)["stop"] == 100


def test_equal_highs_take_the_later_one_as_h():
    hi, lo, cl, tfs = base()
    hi[1], lo[2] = 120, 90  # lowest low sits between the two equal highs: outside the window
    assert run(hi, lo, cl, tfs)["stop"] == 100


def test_trigger_candle_low_counts_for_the_stop():
    hi, lo, cl, tfs = base()
    lo[12] = 95
    r = run(hi, lo, cl, tfs)
    assert (r["stop"], r["limit"]) == (95, 118)


def test_5m_trigger_acts_at_the_candle_close():
    hi, lo, cl, tfs = base()
    cl[14] = 117
    r = run(hi, lo, cl, tfs, tf="5m")
    assert (r["touch"], r["end"], r["limit"]) == (12, 14, 117)
    assert r["ref_ts"] == 0  # H's 5m candle opens at minute 0: the stop window starts at minute 5
    lo[4] = 80  # before the window
    assert run(hi, lo, cl, tfs, tf="5m")["stop"] == 100


def test_window_ends_before_the_next_spf_signal():
    assert run(*base(), nxt=12)["why"] == "no touch"
    r = run(*base(), tf="5m", nxt=14)  # touch inside, 5m candle closes on the next SPF bar
    assert (r["touch"], r["why"]) == (12, "trigger candle closes after the window")


def test_window_ends_at_the_day_or_contract_end():
    assert run(*base(), last=11)["why"] == "no touch"


def test_unfilled_order_is_cancelled_at_the_next_spf_signal_close():
    assert run(*base(), nxt=16)["expire"] == 4  # works bars 13-16


def test_no_trade_when_the_stop_is_at_or_above_the_close():
    hi, lo, cl, tfs = base()
    cl[12] = 100
    assert run(hi, lo, cl, tfs)["why"] == "no risk (stop at the close)"


def test_swing_high_whose_candle_misses_its_first_minute_still_starts_the_window_at_the_next_candle():
    hi, lo, cl, tfs = base()
    lo[10] = 108
    tfs["5m"].swing.sh_ts[14] = TS[6]  # swing high in the 5-9 candle, first traded minute 6
    r = run(hi, lo, cl, tfs, tf="5m")
    assert (r["ref_ts"], r["stop"]) == (TS[5], 108)  # bars 5-9 (low 100 at bar 7) are not in the window


def test_h_inside_the_trigger_candle_gives_no_trade():
    hi, lo, cl, tfs = base()
    hi[3], hi[5], hi[7] = 115, 120, 121  # H printed on the signal bar, touched again in the same 5m candle
    r = run(hi, lo, cl, tfs, tf="5m")
    assert (r["touch"], r["why"]) == (7, "empty stop window")


def frame(minutes, low, high, close):
    ts = (pd.Timestamp("2024-03-05 08:00", tz="America/Chicago") + pd.to_timedelta(minutes, unit="min"))
    return add_session(pd.DataFrame({"ts": ts.tz_convert("UTC"), "raw_symbol": "CLJ4", "open": close, "high": high,
                                     "low": low, "close": close, "volume": 1, "vendor": "test"}))


def test_candle_bars_map_each_bar_to_its_candle_completion_and_last_bar():
    minutes = [0, 1, 2, 3, 5, 6, 9, 10]  # 08:04 missing; the 08:10 candle is unfinished
    df = frame(minutes, [70.0] * 8, [70.1] * 8, [70.05] * 8)
    done, end = _candle_bars(df, "5m", 8)
    assert list(done) == [4, 4, 4, 4, 6, 6, 6, NEVER]
    assert list(end) == [3, 3, 3, 3, 6, 6, 6, NEVER]
    assert [list(x) for x in _candle_bars(df, "1m", 8)] == [list(range(8))] * 2


def test_trigger_candle_missing_its_last_minute_uses_its_own_prices_not_the_next_bar():
    hi, lo, cl, tfs = base()
    tfs["5m"].done[10:14], tfs["5m"].end[10:14] = 14, 13  # bar 14 = first bar of the next candle (minute 14 gone)
    cl[13], cl[14], lo[14] = 117, 90, 80
    r = run(hi, lo, cl, tfs, tf="5m")
    assert (r["end"], r["limit"], r["stop"]) == (14, 117, 100)  # signal at bar 14's close, prices through bar 13


def test_spf_long_source_gives_a_short_in_real_prices(monkeypatch):
    low, high, close = np.full(N, 70.05), np.full(N, 70.15), np.full(N, 70.10)
    low[3], high[7] = 70.00, 70.30
    low[12], close[12] = 69.99, 70.05
    df = frame(np.arange(N), low, high, close)
    spf = pd.DataFrame({"side": [1], "end": [5], "stop": [70.00], "tf": ["1m"], "limit": [70.10]})
    monkeypatch.setattr(Spf, "setups", lambda self, df, p: spf)
    s = Strategy()
    sig = s.signals(df, s.PARAMS)
    assert list(sig.index) == [12]
    assert sig.iloc[0].to_dict() == {"side": -1, "limit": 70.05, "stop": 70.30, "target": 69.55, "expire": NO_EXPIRY}


def test_sl_tf_swing_high_after_h_sets_the_stop_window():
    hi, lo, cl, tfs = base()
    lo[10] = 108
    m15 = Swing(15 * MIN_NS, np.full(N, NAT))
    m15.sh_ts[12] = TS[0] + 5 * MIN_NS  # a "15m" swing high candle opening after H (bar 3); window from minute 20
    r = run(hi, lo, cl, tfs, sl=m15)
    assert r["why"] == "empty stop window"  # minute 20 is after the trigger: no bars left
    m5 = Swing(5 * MIN_NS, np.full(N, NAT))
    m5.sh_ts[12] = TS[6]  # 5m swing high in the 5-9 candle: window from bar 10
    r = run(hi, lo, cl, tfs, sl=m5)
    assert (r["ref_ts"], r["stop"]) == (TS[5], 108)


def test_sl_tf_swing_high_not_after_h_keeps_the_window_after_h():
    hi, lo, cl, tfs = base()
    m15 = Swing(15 * MIN_NS, np.full(N, NAT))
    m15.sh_ts[12] = TS[0]  # the 15m candle holding H: not after H
    r = run(hi, lo, cl, tfs, sl=m15)
    assert (r["ref_ts"], r["stop"]) == (TS[3], 100)  # after H's 1m candle, as without sl_tf


def test_sl_tf_other_than_clock_aligned_timeframes_is_refused():
    s = Strategy()
    low, high, close = np.full(N, 70.05), np.full(N, 70.15), np.full(N, 70.10)
    df = frame(np.arange(N), low, high, close)
    for bad in ("7m", "4h", "1d"):  # 4h and 1d candles follow the session, not the clock
        with pytest.raises(ValueError, match="sl_tf"):
            s.setups(df, {**s.PARAMS, "sl_tf": bad})
