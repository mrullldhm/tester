import numpy as np
import pandas as pd
import pytest

from cltester.swings import HIGH, LOW, Candles, ProvisionalSwings
from studies.tupa_1.scan import scan


def scan_case(*, kind=HIGH, swing_price=95, retest=18, retest_open=105, retest_high=109,
              paired=False, c2_gap=False, c3_gap=False, early=False, catalyst_paired=False,
              second_open=105, second_low=104, c1_start=4, roll_at=None):
    """Use a short-shaped sequence and mirror prices to exercise the long rules."""
    n = 28
    minutes = np.arange(n)
    minutes[16:] += c2_gap
    minutes[22:] += c3_gap
    ts = pd.Timestamp("2024-03-05", tz="UTC") + pd.to_timedelta(minutes, unit="min")
    opens = np.full(n, 105)
    highs, lows = np.full(n, 108), np.full(n, 104)
    highs[:2], lows[:2], opens[:2] = 100, 90, 95
    lows[2:4] = swing_price
    highs[4], lows[4] = 110, 101
    lows[6], highs[7] = 100, 111
    opens[7], lows[7] = second_open, second_low
    highs[12], highs[14] = 120, 110
    opens[retest], highs[retest], lows[retest] = retest_open, retest_high, min(99, second_low, retest_open)
    if early:
        highs[16], lows[17] = 111, 103
        lows[16] = 105

    symbols = np.full(n, "CLQ5")
    if roll_at is not None:
        symbols[roll_at:] = "CLU5"
    df = pd.DataFrame({"ts": ts, "open": kind * opens / 100, "close": kind * opens / 100, "raw_symbol": symbols})

    def candles(starts, ends):
        first, last = np.array(starts), np.array(ends)
        cd = Candles(ts[first], opens[first], np.maximum.reduceat(highs, first),
                     np.minimum.reduceat(lows, first), opens[last], np.full(len(first), -1),
                     last.copy(), first, last, highs, lows)
        return cd if kind == HIGH else cd.mirrored()

    small = candles(range(0, n, 2), range(1, n, 2))
    large = candles([0, c1_start, 10, 16, 22], [c1_start - 1, 9, 15, 21, 27])
    reference = candles([0, 2], [1, 27])
    if c2_gap:
        large.avail[2] = 16
    if c3_gap:
        large.avail[3] = 22

    def state():
        return {"sh": pd.Series(pd.NaT, index=range(n), dtype=ts.dtype),
                "sl": pd.Series(pd.NaT, index=range(n), dtype=ts.dtype), "newest": np.zeros(n, dtype=int)}

    small_state, large_state = state(), state()
    major, minor = ("sh", "sl") if kind == HIGH else ("sl", "sh")
    small_state[minor].iloc[6] = small.ts[1]
    small_state["newest"][6] = -kind
    if catalyst_paired:
        small_state[major].iloc[6] = small.ts[1]
    start = large.avail[3]
    stop = 27 if retest == 27 else n
    large_state[major].iloc[start:stop] = large.ts[2]
    large_state["newest"][start:stop] = kind
    if paired:
        large_state[minor].iloc[start:] = large.ts[2]
        large_state["newest"][stop:] = -kind
    preview = ProvisionalSwings(np.zeros((len(large), 2, 2, 2), dtype=np.int8), np.full(len(large), n))
    if early:
        preview.kinds[2, 0, int(kind == LOW), int(kind == HIGH)] = kind
    return list(scan(df, small, large, reference, small_state, large_state, preview, kind))


@pytest.mark.parametrize("kind", [HIGH, LOW])
@pytest.mark.parametrize("swing_price, accepted", [(99, True), (100, False), (101, False)])
def test_catalyst_swing_strictly_clears_reference(kind, swing_price, accepted):
    setups = scan_case(kind=kind, swing_price=swing_price)
    assert bool(setups) is accepted
    if accepted:
        assert setups[0].catalyst_swing_price == kind * swing_price


@pytest.mark.parametrize("kind", [HIGH, LOW])
@pytest.mark.parametrize(
    "paired, open_, low, accepted",
    [(True, 94, 94, False), (True, 95, 95, False), (True, 105, 95, False),
     (True, 110, 95, True), (True, 105, 104, True), (False, 94, 94, True)],
)
def test_catalyst_second_touch_requires_an_active_swing(kind, paired, open_, low, accepted):
    setups = scan_case(kind=kind, catalyst_paired=paired, second_open=open_, second_low=low)
    assert bool(setups) is accepted
    if accepted:
        assert setups[0].second_touch == 7


@pytest.mark.parametrize(
    "kind, paired, retest_open, retest_high, accepted",
    [(HIGH, True, 121, 121, False), (LOW, True, 120, 120, False), (HIGH, True, 105, 120, False),
     (HIGH, True, 99, 120, True), (HIGH, False, 105, 120, True), (HIGH, True, 105, 119, True)],
)
def test_retest_on_minute_that_closes_swing_candle(kind, paired, retest_open, retest_high, accepted):
    setups = scan_case(kind=kind, paired=paired, retest=27, retest_open=retest_open, retest_high=retest_high)
    assert bool(setups) is accepted


@pytest.mark.parametrize("retest", [22, 23])
def test_retest_on_gap_delayed_candle_3_close(retest):
    [setup] = scan_case(c3_gap=True, retest=retest)
    assert setup.retest == retest
    assert setup.confirmation == retest
    assert setup.inside == (retest == 22)


def test_gap_delayed_candle_2_close_allows_sweep_from_candle_3_open():
    [setup] = scan_case(c2_gap=True, early=True)
    assert setup.early_sweep == 17
    assert setup.retest == setup.confirmation == 18


@pytest.mark.parametrize(
    "c1_start, roll_at, crosses_roll",
    [(2, 3, True), (2, 2, False), (6, 5, True), (2, 21, True), (2, 22, False)],
)
def test_contract_roll_check_covers_candle_1_and_catalyst_context(c1_start, roll_at, crosses_roll):
    [setup] = scan_case(c1_start=c1_start, roll_at=roll_at)
    assert setup.crosses_roll == crosses_roll
