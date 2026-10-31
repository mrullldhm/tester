"""The vectorized port must give the same signals as a literal bar-by-bar transcription of the Pine script
(real 21-bar buffers, Pine ATR, state updated on every bar)."""

import math

import numpy as np
import pytest

from strategies.fair_price_reversal import signals
from tvtester import ta
from tvtester.data import DATA_DIR, Bars, load_bars
from tvtester.sessions import SESSIONS, local_clock

pytestmark = pytest.mark.skipif(not any(DATA_DIR.glob("*.parquet")), reason="no data")


def pivot(values, strength, high):
    n = len(values)
    if n < strength * 2 + 1:
        return math.nan
    ci = n - strength - 1
    cand = values[ci]
    for k in range(ci - strength, ci + strength + 1):
        if k != ci and ((values[k] >= cand) if high else (values[k] <= cand)):
            return math.nan
    return cand


def literal(bars, session, window, mult, swing, atr_len=14, with_stop=False):
    """Signals as [(bar, direction)], or [(bar, direction, stop)] with the Pine twin's tracked excursion extreme."""
    s = SESSIONS[session]
    mod, day = local_clock(bars.ts, s.tz)
    atr1 = ta.shift(ta.atr(bars.h, bars.l, bars.c, atr_len), 1)
    hs, ls, ts = [], [], []
    last_day = bu = bl = last_sh = last_sl = None
    up_seen = lo_seen = long_sent = short_sent = False
    up_t = lo_t = None
    lr = sr = False
    lt = st = None
    d = 0
    los = his = None  # Pine lowSinceLowerExcursion / highSinceUpperExcursion
    out = []
    for i in range(len(bars)):
        o, h, l, c = bars.o[i], bars.h[i], bars.l[i], bars.c[i]
        hs.append(h); ls.append(l); ts.append(i)
        if len(hs) > 21:
            hs.pop(0); ls.pop(0); ts.pop(0)
        ph, pl = pivot(hs, swing, True), pivot(ls, swing, False)
        pt = ts[len(ts) - swing - 1] if len(ts) >= swing * 2 + 1 else None
        los = None if los is None else min(los, l)
        his = None if his is None else max(his, h)
        if mod[i] == s.anchor_minute and (last_day is None or day[i] != last_day):
            bu, bl = max(o, c), min(o, c)
            up_seen = lo_seen = long_sent = short_sent = False
            d, up_t, lo_t, lr, sr, lt, st = 0, None, None, False, False, None, None
            los = his = None
            last_day = day[i]
        win = s.open_minute <= mod[i] < s.open_minute + window
        a = atr1[i]
        if win and not math.isnan(a) and a > 0 and bu is not None:
            md = a * mult
            if up_seen and d != -1 and not short_sent and c < bu + md:
                up_seen = False
            if lo_seen and d != 1 and not long_sent and c > bl - md:
                lo_seen = False
            uh = not up_seen and not short_sent and h >= bu + md
            lh = not lo_seen and not long_sent and l <= bl - md
            if uh and lh:
                up_seen = lo_seen = True; up_t = lo_t = i; d = 0; lr = sr = False; lt = st = None; his, los = h, l
            elif uh:
                up_seen, up_t, d = True, i, -1; lr = sr = False; lt = st = None; his = h
            elif lh:
                lo_seen, lo_t, d = True, i, 1; lr = sr = False; lt = st = None; los = l
        if not math.isnan(ph):
            if win and d == 1 and lo_seen and not long_sent and last_sh is not None and pt is not None \
                    and pt > lo_t and ph < last_sh:
                lr, lt = True, ph
            last_sh = ph
        if not math.isnan(pl):
            if win and d == -1 and up_seen and not short_sent and last_sl is not None and pt is not None \
                    and pt > up_t and pl > last_sl:
                sr, st = True, pl
            last_sl = pl
        if win and d == 1 and lr and not long_sent and c > lt and c < bl:
            out.append((i, 1, los) if with_stop else (i, 1)); long_sent, lr, d = True, False, 0
        if win and d == -1 and sr and not short_sent and c < st and c > bu:
            out.append((i, -1, his) if with_stop else (i, -1)); short_sent, sr, d = True, False, 0
        if mod[i] >= s.open_minute + window:
            lr = sr = False
    return out


@pytest.mark.parametrize("session", ["asia", "london", "ny"])
@pytest.mark.parametrize("window,mult,swing", [(60, 1.0, 2), (30, 0.5, 1), (120, 2.0, 3)])
def test_port_matches_literal_pine(session, window, mult, swing):
    bars = Bars.from_frame(load_bars("2024-02-20", "2024-04-15"))  # spans the US / UK DST changes
    got = signals(bars, session, window, mult, swing)["sig"]
    want = literal(bars, session, window, mult, swing)
    assert [(int(i), int(got[i])) for i in np.flatnonzero(got)] == want
    assert len(want) > 5
