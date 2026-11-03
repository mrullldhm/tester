"""Tupa Trade: swings, timeframe candles, bias and orders.

- The vectorized strategy (strategies/tupa_trade.py) must trade exactly like a literal bar-by-bar transcription of
  the Pine twin (tests/tupa_literal.py) on synthetic CL-like bars with weekends, the daily halt, missing minutes and
  a DST change.
- Hand-made cases for the swing rule (indicator) and the trend rule.
- With data: the owner's 26 Oct 2026 trade (docs/strategies/tupa_trade/README.md, 1m section) is reproduced.
"""

from pathlib import Path
import re

import numpy as np
import pandas as pd
import pytest

from strategies.tupa_trade import T_CHOICES, TupaTrade, bias
from tests.tupa_literal import LiteralTupa, pine_eq, pine_ne
from tvtester import swings as sw
from tvtester.data import DATA_DIR, Bars, load_bars
from tvtester.engine import run

NY = "America/New_York"


@pytest.mark.parametrize("a,b,eq,ne", [(None, None, False, False), (1, None, False, False),
                                    (None, 1, False, False), (1, 1, True, False), (1, 2, False, True)])
def test_pine_na_equality(a, b, eq, ne):
    assert pine_eq(a, b) is eq
    assert pine_ne(a, b) is ne


def unguarded_na_comparisons(source):
    """Check direct ==/!= uses of na-initialized var scalars, including reversed operands.

    Accept an explicit na() check before the comparison, on its line or an enclosing if.
    This deliberately conservative source check requires guards to remain visible.
    """
    source = re.sub(r"//[^\n]*", "", source)
    names = re.findall(r"\bvar\s+\w+\s+(\w+)\s*=\s*na\b", source)
    enclosing = []
    failures = []
    for lineno, line in enumerate(source.splitlines(), 1):
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        while enclosing and enclosing[-1][0] >= indent:
            enclosing.pop()
        for name in names:
            comparison = rf"\b{re.escape(name)}\b\s*(?:==|!=)|(?:==|!=)\s*\b{re.escape(name)}\b"
            for match in re.finditer(comparison, line):
                guards = " ".join(text for _, text in enclosing) + " " + line[:match.start()]
                if not re.search(rf"\bna\s*\(\s*{re.escape(name)}\s*\)", guards):
                    failures.append((lineno, name))
        if line.lstrip().startswith("if "):
            enclosing.append((indent, line.strip()))
    return failures


def test_pine_na_initialized_vars_have_guarded_comparisons():
    root = Path(__file__).resolve().parents[1]
    for path in ("strategies/tupa_trade.pine", "indicators/structure_swings.pine"):
        source = (root / path).read_text()
        assert not unguarded_na_comparisons(source), path
    # Prove that removing the fix fails the static check.
    source = (root / "strategies/tupa_trade.pine").read_text()
    old = source.replace("if na(curDay) or dayKey != curDay", "if dayKey != curDay")
    assert old != source
    line = old.splitlines().index("if dayKey != curDay") + 1
    assert unguarded_na_comparisons(old) == [(line, "curDay")]
    assert unguarded_na_comparisons("var int x = na\nif x == 1\n    x := 2") == [(2, "x")]


@pytest.mark.parametrize("data_window", ["synthetic", pytest.param(
    "2026-10", marks=pytest.mark.skipif(not (DATA_DIR / "year=2026.parquet").exists(), reason="no 2026 CL data"))])
def test_na_session_reset_old_pine_stops_after_first_trade(data_window):
    class OldPineTupa(LiteralTupa):
        def _new_session(self, day):
            return pine_ne(day, self.cur_day)  # OLD Pine: if dayKey != curDay

    # Exercise both the existing CL session / DST fixture and an unfiltered real-data window.
    bars = synthetic() if data_window == "synthetic" else Bars.from_frame(load_bars("2026-10-01", "2026-11-03"))
    old = OldPineTupa(t_min="1d")
    broken = run(old, bars)
    fixed = run(LiteralTupa(t_min="1d"), bars)
    python = run(TupaTrade(t_min="1d"), bars)
    assert len(broken.trades) == 1
    assert old.cur_day is None and old.traded
    assert trade_rows(broken) == trade_rows(fixed)[:1]
    dates = [bars.ts[t.entry_bar].tz_convert(NY).strftime("%Y-%m-%d") for t in fixed.trades]
    assert len(dates) == len(set(dates)) == 4
    assert fixed.trades == python.trades  # all trade fields, including costs and profit
    assert fixed.open_trade is None and python.open_trade is None


def synthetic(days=24, seed=0, start="2026-03-01 18:00", drop=0.03, halt_bars=False):
    """CL-like 1m bars in ticks: CME hours (Sun 18:00 - Fri 17:00 New York, daily halt 17:00-18:00), random gaps,
    trending random walk. Spans the 8 March 2026 US DST change. `halt_bars`: also trade 17:00-17:14 (2010 data
    has bars there: CME's daily break was shorter)."""
    rng = np.random.default_rng(seed)
    t = pd.date_range(pd.Timestamp(start, tz=NY), periods=days * 1440, freq="1min")
    m = t.hour * 60 + t.minute
    wd = t.day_of_week
    keep = ~((m >= (17 * 60 + 15 if halt_bars else 17 * 60)) & (m < 18 * 60))
    keep &= ~(wd == 5) & ~((wd == 4) & (m >= 17 * 60)) & ~((wd == 6) & (m < 18 * 60))
    keep &= rng.random(len(t)) > drop
    t = t[keep].tz_convert("UTC")
    n = len(t)
    drift = np.repeat(rng.normal(0, 0.6, n // 90 + 1), 90)[:n]
    c = 7000 + np.cumsum(np.round(rng.normal(drift, 2.5)).astype(np.int64))
    o = np.concatenate([[c[0]], c[:-1]]) + rng.integers(-1, 2, n)
    h = np.maximum(o, c) + rng.integers(0, 4, n)
    l = np.minimum(o, c) - rng.integers(0, 4, n)
    sym = np.array(["CLK6"] * n, dtype=object)
    return Bars(t, t.as_unit("ms").asi8, o, h, l, c, np.ones(n), sym, np.zeros(n, dtype=bool))


def trade_rows(res):
    return [(t.direction, t.entry_bar, t.entry_price, t.exit_bar, t.exit_price, t.exit_reason) for t in res.trades]


@pytest.mark.parametrize("seed", [0, 1, 2])
@pytest.mark.parametrize("t_min", T_CHOICES)
def test_vectorized_matches_literal_transcription(seed, t_min):
    bars = synthetic(seed=seed)
    lit = LiteralTupa(t_min=t_min)
    a = run(TupaTrade(t_min=t_min), bars)
    b = run(lit, Bars(bars.ts, bars.t_ms, bars.o, bars.h, bars.l, bars.c, bars.volume, bars.raw_symbol,
                      bars.last_of_contract))
    np.testing.assert_array_equal(bias(bars, t_min), lit.bias_log)
    assert trade_rows(a) == trade_rows(b)
    assert (a.open_trade is None) == (b.open_trade is None)


def test_synthetic_bars_trade_both_sides():
    """The comparison above is only meaningful if the strategy trades: both sides, every exit kind."""
    rows = []
    for seed in range(3):
        rows += trade_rows(run(TupaTrade(t_min="15m"), synthetic(seed=seed)))
    assert {r[0] for r in rows} == {1, -1}
    assert {"limit", "stop"} <= {r[5] for r in rows}


def test_stop_limit_levels_and_one_trade_per_session():
    for seed in range(3):
        bars = synthetic(seed=seed)
        res = run(TupaTrade(t_min="15m"), bars)
        days = [bars.ts[t.entry_bar].tz_convert(NY).date() for t in res.trades]
        assert len(days) == len(set(days))
        for t in res.trades:
            lt = bars.ts[t.entry_bar].tz_convert(NY)
            assert 9 * 60 <= lt.hour * 60 + lt.minute < 14 * 60 + 30
            risk = (t.exit_price - t.entry_price) * t.direction
            if t.exit_reason == "limit":
                assert risk == 25
            if t.exit_reason == "stop":
                assert -25 <= risk < 0


def make(ohlc, start="2026-03-04 15:00"):
    a = np.asarray(ohlc, dtype=np.int64)
    n = len(a)
    ts = pd.date_range(start, periods=n, freq="1min", tz="UTC")
    return Bars(ts, ts.as_unit("ms").asi8, a[:, 0], a[:, 1], a[:, 2], a[:, 3], np.ones(n),
                np.array(["CLK6"] * n, dtype=object), np.zeros(n, dtype=bool))


def test_swing_rule_left_equal_right_strict_and_alternation():
    # highs: 10, 12, 12, 11 -> bar 2 is a swing high (left equal), bar 1 is not (right equal)
    bars = make([(9, 10, 8, 9), (11, 12, 10, 11), (11, 12, 10, 11), (10, 11, 9, 10), (9, 10, 7, 8),
                 (8, 9, 8, 9), (9, 13, 9, 12), (12, 12, 10, 11)])
    m = sw.minute_swings(bars)
    first = int(np.flatnonzero(m.last_type == sw.SH)[0])
    assert (m.bar[first], m.idx_h[first], m.cur_h[first]) == (3, 2, 12)
    # low 7 at bar 4 confirmed at bar 5; high 13 at bar 6 confirmed at bar 7 -> HH (13 >= 12)
    assert m.cur_l[m.at[5]] == 7 and m.last_type[m.at[5]] == sw.SL
    e = m.at[7]
    assert (m.last_type[e], m.cur_h[e], m.prev_h[e]) == (sw.SH, 13, 12)


def test_lower_pivot_high_is_dropped_higher_replaces():
    z = sw.Zig()
    z.push(sw.SL, 5, 0)
    z.push(sw.SH, 20, 1)
    assert not z.push(sw.SH, 19, 2) and z.cur_h == 20 and z.n_h == 1  # dropped
    assert z.push(sw.SH, 20, 3) and z.idx_h == 3 and z.n_h == 2  # equal: the later one
    assert z.prev_h is None


def test_four_hour_and_daily_candles_follow_the_cme_day():
    ts = pd.DatetimeIndex(pd.to_datetime(["2026-10-25 22:00", "2026-10-26 01:59", "2026-10-26 02:00",
                                          "2026-10-26 17:59", "2026-10-26 18:00", "2026-10-26 20:59",
                                          "2026-10-26 22:00"]).tz_localize(NY).tz_convert("UTC"))
    h4 = sw.candle_ids(ts, "4h")
    assert h4[0] == h4[1] != h4[2]  # 22:00-02:00 ET, then 02:00
    d = sw.candle_ids(ts, "1d")
    assert d[0] == d[3] != d[4] == d[6]  # 18:00 ET starts the next trading day
    halt = pd.DatetimeIndex(pd.to_datetime(["2026-10-26 14:00", "2026-10-26 16:59", "2026-10-26 17:10"])
                            .tz_localize(NY).tz_convert("UTC"))
    for tf in ("4h", "1d"):  # no halt special case: halt bars stay in the day's last candle (R19)
        ids = sw.candle_ids(halt, tf)
        assert ids[0] == ids[1] == ids[2] == sw.candle_ids(halt[1:2], tf, next_minute=True)[0]


@pytest.mark.parametrize("seed", [0, 1])
@pytest.mark.parametrize("t_min", T_CHOICES)
def test_bars_inside_the_daily_halt_match_literal(seed, t_min):
    """R19: 2010 data has bars in 17:00-18:00 New York. Python and the Pine transcription must group them the same way."""
    bars = synthetic(seed=seed, halt_bars=True)
    lit = LiteralTupa(t_min=t_min)
    a = run(TupaTrade(t_min=t_min), bars)
    b = run(lit, Bars(bars.ts, bars.t_ms, bars.o, bars.h, bars.l, bars.c, bars.volume, bars.raw_symbol,
                      bars.last_of_contract))
    np.testing.assert_array_equal(bias(bars, t_min), lit.bias_log)
    assert trade_rows(a) == trade_rows(b)


def test_trend_down_when_hl_touched_by_closed_candle():
    # 5m candles (high, low): L 100 (candle 1), H 115 (2), HL 104 (3), HH 120 (4); candle 5 touches 104 -> down
    five = [(110, 105), (108, 100), (115, 106), (112, 104), (120, 107), (118, 103), (110, 101)]
    one = []
    for h, l in five:  # five 1m bars per 5m candle
        mid = (h + l) // 2
        one += [(mid, h, l, mid)] + [(mid,) * 4] * 4
    st = sw.timeframe_state(make(one, start="2026-03-04 15:00"), "5m")
    assert list(st.trend) == [0, 0, 0, 0, 0, -1, -1]
    assert list(st.last_type[4:6]) == [sw.SL, sw.SH]  # HL 104 confirmed by candle 4, HH 120 by candle 5
    assert st.cur_l[5] == 104 and st.cur_h[5] == 120


@pytest.mark.skipif(not any(DATA_DIR.glob("*.parquet")), reason="no data")
def test_owner_trade_26_oct_2026():
    """README section 4, 1m: short, sell stop-limit 100.76 / 100.77, filled 22:32 MYT, TP 100.52 at 22:33,
    +245.98 USD. This is the owner's worked example: the code must reproduce it before any result is called real."""
    bars = Bars.from_frame(load_bars("2026-06-01", "2026-10-27"))
    res = run(TupaTrade(t_min="1h"), bars)
    myt = "Asia/Kuala_Lumpur"
    day = [t for t in res.trades if bars.ts[t.entry_bar].tz_convert(myt).strftime("%Y-%m-%d") == "2026-10-26"]
    assert len(day) == 1
    t = day[0]
    assert t.direction == -1 and t.entry_price == 10077 and t.exit_price == 10052 and t.exit_reason == "limit"
    assert bars.ts[t.entry_bar].tz_convert(myt).strftime("%H:%M") == "22:32"
    assert bars.ts[t.exit_bar].tz_convert(myt).strftime("%H:%M") == "22:33"
    assert t.profit == pytest.approx(245.98)
