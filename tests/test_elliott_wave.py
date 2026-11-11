"""Elliott Wave 5: vectorised setups against a literal bar-by-bar (Pine-style) transcription, causality,
limit-only entries, TP expiry and same-session exits.

The literal shares the spec reading and sw.Zig: it checks the vectorisation, not the spec."""

import math

import numpy as np
import pytest

from strategies.elliott_wave import ElliottWave, setups
from tvtester import swings as sw
from tvtester.data import DATA_DIR, Bars, load_bars
from tvtester.engine import LONG, SHORT, run
from tvtester.sessions import SESSIONS, local_clock

pytestmark = pytest.mark.skipif(not any(DATA_DIR.glob("*.parquet")), reason="no data")

PARAMS = [
    ("ny", 100, 0.382, 0.618, 0.618, 20),
    ("london", 140, 0.5, 0.786, 1.0, 40),
    ("asia", 120, 0.382, 0.786, 1.0, 20),
]


@pytest.fixture(scope="module")
def frame():
    return load_bars("2023-03-01", "2023-05-31")


@pytest.fixture(scope="module")
def bars(frame):
    return Bars.from_frame(frame)


def literal(bars, session, window, entry_r, stop_r, tp_x, min_len):
    """Pine-style state machine, one bar at a time: [(bar, direction, limit, stop, tp)]."""
    s = SESSIONS[session]
    mod, _ = local_clock(bars.ts, s.tz)
    o, h, l, c = (x.tolist() for x in (bars.o, bars.h, bars.l, bars.c))
    hl = [h[i] + l[i] for i in range(len(h))]
    z = sw.Zig()
    aos = []
    bull = bear = None  # [extreme, after, ao extreme]
    out = []
    for i in range(len(h)):
        if i >= 2:
            k = i - 1
            hf = sw.open_rule_high_first(o[k], h[k], l[k])
            z.pivots(h[k - 1], h[k], h[i], l[k - 1], l[k], l[i], bool(hf), k)
        z.invalidate(h[i], l[i])
        ao = None
        if i >= 33:
            ao = 34 * sum(hl[i - 4: i + 1]) - 5 * sum(hl[i - 33: i + 1])
        aos.append(ao)
        prev = aos[i - 1] if i >= 1 else None
        if ao is not None:
            if ao >= 0 and prev is not None and prev < 0:
                bull = [h[i], None, ao]
            elif bull is not None:
                if h[i] >= bull[0]:
                    bull[0], bull[1] = h[i], None
                else:
                    bull[1] = l[i] if bull[1] is None else min(bull[1], l[i])
                bull[2] = max(bull[2], ao)
            if ao < 0 and prev is not None and prev >= 0:
                bear = [l[i], None, ao]
            elif bear is not None:
                if l[i] <= bear[0]:
                    bear[0], bear[1] = l[i], None
                else:
                    bear[1] = h[i] if bear[1] is None else max(bear[1], h[i])
                bear[2] = min(bear[2], ao)
        if not (s.open_minute <= mod[i] < s.flat_minute - 1) or i < window + 32 or prev is None:
            continue
        w = aos[i - window + 1: i + 1]
        wmax, wmin = max(w), min(w)
        if ao < 0 <= prev and bull is not None and bull[1] is not None:
            top = bull[0]
            if wmax > 0 and bull[2] == wmax and wmax > -wmin and z.cur_h == top:
                L = top - min(l[i - window + 1: i + 1])
                st = top - math.floor(stop_r * L + 0.5)
                if L >= min_len and bull[1] > st:
                    lim = min(top - math.floor(entry_r * L + 0.5), c[i])
                    out.append((i, LONG, lim, st, lim + math.floor(tp_x * L + 0.5)))
        if ao >= 0 > prev and bear is not None and bear[1] is not None:
            bot = bear[0]
            if wmin < 0 and bear[2] == wmin and -wmin > wmax and z.cur_l == bot:
                L = max(h[i - window + 1: i + 1]) - bot
                st = bot + math.floor(stop_r * L + 0.5)
                if L >= min_len and bear[1] < st:
                    lim = max(bot + math.floor(entry_r * L + 0.5), c[i])
                    out.append((i, SHORT, lim, st, lim - math.floor(tp_x * L + 0.5)))
    return out


def vectorised(bars, *p):
    sg = setups(bars, *p)
    at = np.flatnonzero(sg["sig"])
    return [(int(i), int(sg["sig"][i]), int(sg["limit"][i]), int(sg["stop"][i]), int(sg["tp"][i])) for i in at]


@pytest.mark.parametrize("p", PARAMS)
def test_setups_match_literal(bars, p):
    got = vectorised(bars, *p)
    assert got, "expected setups in three months of 1m data"
    assert got == literal(bars, *p)


@pytest.mark.parametrize("p", PARAMS)
def test_levels_are_ordered(bars, p):
    for _, d, lim, st, tp in vectorised(bars, *p):
        assert (st < lim < tp) if d == LONG else (tp < lim < st)


def test_no_lookahead(frame, bars):
    full = vectorised(bars, *PARAMS[0])
    cut = len(bars) // 2
    part = vectorised(Bars.from_frame(frame.iloc[:cut].reset_index(drop=True)), *PARAMS[0])
    assert part == [x for x in full if x[0] < cut]


def test_both_directions_present(bars):
    found = {d for p in PARAMS for _, d, *_ in vectorised(bars, *p)}
    assert found == {LONG, SHORT}


@pytest.mark.parametrize("bad", [
    ("ny", 100, 0.618, 0.5, 0.618, 20),
    ("ny", 100, 0.382, 0.618, 0.0, 20),
    ("ny", 100, 0.382, 0.618, 0.618, 0),
    ("ny", 0, 0.382, 0.618, 0.618, 20),
])
def test_bad_parameters_rejected(bars, bad):
    with pytest.raises(ValueError):
        setups(bars, *bad)


@pytest.mark.parametrize("session", ["asia", "london", "ny"])
def test_limit_entries_and_same_session_exits(bars, session):
    st = ElliottWave(session=session)
    r = run(st, bars)
    sg = st.sig
    s = SESSIONS[session]
    mod, day = local_clock(bars.ts, s.tz)
    assert r.trades
    for t in r.trades:
        lim = int(sg["limit"][t.signal_bar])
        assert sg["sig"][t.signal_bar] == t.direction
        assert t.entry_bar > t.signal_bar
        # limit only: filled at the limit or better, never worse
        assert (t.entry_price <= lim) if t.direction == LONG else (t.entry_price >= lim)
        assert t.exit_reason in ("stop", "limit", "close", "roll")
        assert day[t.exit_bar] == day[t.signal_bar]  # never held overnight
        # TP expiry: no 1m close between placement and fill found the planned target touched
        tp = int(sg["tp"][t.signal_bar])
        waited = slice(t.signal_bar + 1, t.entry_bar)
        touched = bars.h[waited] >= tp if t.direction == LONG else bars.l[waited] <= tp
        assert not touched.any()
        assert all(s.open_minute <= m < s.flat_minute - 1 for m in mod[t.signal_bar: t.entry_bar])
        assert t.initial_risk_ticks is None or t.initial_risk_ticks > 0  # None: open gapped past the stop
