"""studies/juda_swing_point: outcome race stops at contract changes, late and validation setups get no race."""

import numpy as np

from studies.juda_swing_point.run import FLAT, race, race_status


def bars(n: int, start_sess: int = 600):
    h = np.full(n, 105)
    lo = np.full(n, 95)
    c = np.full(n, 100)
    sess = np.arange(start_sess, start_sess + n)
    day = np.array(["2015-03-04"] * n, dtype="datetime64[D]")
    sym = np.zeros(n, dtype=int)
    return h, lo, c, sess, day, sym


def test_contract_change_ends_the_race_as_roll():
    h, lo, c, sess, day, sym = bars(10)
    sym[5:] = 1
    lo[6] = 50  # new contract's price gap would hit the stop
    h[7] = 200  # and the target
    out = race(h, lo, c, sess, day, sym, 0, 100, 90)
    assert out["r1"] == "roll" and out["r2"] == "roll" and np.isnan(out["flat_r"])


def test_stop_before_the_roll_still_counts():
    h, lo, c, sess, day, sym = bars(10)
    sym[5:] = 1
    lo[3] = 89
    out = race(h, lo, c, sess, day, sym, 0, 100, 90)
    assert out["r1"] == "stop" and out["r2"] == "stop"


def test_no_roll_flat_at_1510_keeps_flat_return():
    h, lo, c, sess, day, sym = bars(10, start_sess=FLAT - 5)
    out = race(h, lo, c, sess, day, sym, 0, 100, 90)
    assert out["r1"] == "flat" and out["flat_r"] == 0.0


def test_race_status_rules():
    _, _, _, sess, day, sym = bars(10)
    assert race_status(sess, sym, day, 0, 4, 10) == "ok"
    assert race_status(sess, sym, day, 0, 4, 0) == "no_risk"
    late = sess.copy()
    late[4] = FLAT  # confirmation closes at 15:10 CT
    assert race_status(late, sym, day, 0, 4, 10) == "late"
    rolled = sym.copy()
    rolled[2:] = 1  # manipulation candle on the old contract, entry on the new one
    assert race_status(sess, rolled, day, 0, 4, 10) == "roll_setup"
    val = np.array(["2022-01-03"] * 10, dtype="datetime64[D]")
    assert race_status(sess, sym, val, 0, 4, 10) == "validation"
    next_day = day.copy()
    next_day[4:] = np.datetime64("2015-03-05")
    assert race_status(sess, sym, next_day, 0, 4, 10) == "late"


def test_missing_closing_minute_enters_at_the_availability_bar_close():
    import pandas as pd

    from cltester.data import add_session, to_ticks
    from cltester.swings import build_candles
    from studies.juda_swing_point.run import confirmation_entry

    minutes = [m for m in range(30) if m != 14]  # 08:14 missing: the 08:00 15m candle completes on the 08:15 bar
    start_ct = pd.Timestamp("2024-03-05 08:00", tz="America/Chicago")
    ts = (start_ct + pd.to_timedelta(minutes, unit="min")).tz_convert("UTC")
    close = 70 + np.arange(len(minutes)) * 0.01
    df = add_session(pd.DataFrame({"ts": ts, "raw_symbol": "CLJ4", "open": close, "high": close + 0.01,
                                   "low": close - 0.01, "close": close, "volume": 1, "vendor": "test"}))
    cd = build_candles(df, "15m")
    c1 = to_ticks(df["close"])
    k = int(np.flatnonzero(cd.avail != cd.last)[0])
    start, entry, delayed = confirmation_entry(cd, c1, k)
    assert delayed and start == cd.avail[k] != cd.last[k]
    assert entry == c1[start] != cd.c[k]  # not the stale candle close
    ok = int(np.flatnonzero(cd.avail == cd.last)[0])
    assert confirmation_entry(cd, c1, ok) == (int(cd.last[ok]), int(cd.c[ok]), False)
