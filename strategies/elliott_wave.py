"""Elliott Wave 5 (wave-4 pullback limit) on CL1! 1-minute bars, one session per variant, no overnight holding.

Sources: "10 Seconds Elliott Wave" (iTradeAIMS, after Bill Williams: waves counted on the Awesome Oscillator)
and markokrivokapic.com (Fibonacci ratios for waves 4 and 5). The sources give no complete trade plan; every
rule below that is ours is marked (ours). Long side; the short side is the exact mirror.

1. AO = SMA5(hl2) - SMA34(hl2) on the 1m chart, every bar. Kept exact in integer ticks:
   ao = 34 * sum5(h + l) - 5 * sum34(h + l) = 340 x AO in ticks (same sign and order as AO).
2. Bull hump: the run of bars starting where AO turns >= 0 (from < 0). Through the bar it ends on, track the
   hump's highest high (equal: later), the lowest low after that high, and the hump's largest AO.
3. Wave 3 (PDF): the largest AO of the last `window` bars is positive, taller than the deepest negative AO of
   that window, and belongs to the current hump.
4. Wave 4 confirmed (PDF minimum): AO crosses below zero (ao[i] < 0 <= ao[i-1]). Decision at that bar's close.
5. Wave 3 top = the hump's highest high, and it must be the current owner 1m swing high
   (indicators/structure_swings.pine, tvtester/swings.py). Base = lowest low of the last `window` bars.
   Wave length L = top - base (ticks), at least `min_len`.
6. Levels (Krivokapic W4 0.382 / PDF W4 38-50 % and W4 > ~62 % = truncation; PDF TZ1 / TZ2 = 61.8 / 100 %):
   stop  = top - rnd(stop_r x L); skip when the pullback already touched it.
   limit = min(top - rnd(entry_r x L), signal close)   (ours: never above the close)
   tp    = limit + rnd(tp_x x L)                       (ours: projected from the limit, the planned wave-4 end)
   rnd = round half up (Pine math.round).
7. Orders (owner execution rules): buy limit from the next bar with its bracket (stop, tp) attached, only when
   flat with no working order. Unfilled limit cancelled when a 1m close finds the planned tp touched, at the
   session flat time, and on the contract's last bar. Open position closed at the first bar close outside the
   session (fills at the next open). Entries are limit orders only; the stop is an exit order.
"""

import numpy as np
import pandas as pd

from tvtester import swings as sw
from tvtester.data import Bars
from tvtester.engine import LONG, SHORT, Context
from tvtester.entries import PendingEntry
from tvtester.sessions import SESSIONS, local_clock
from tvtester.strategy import Strategy

AO_FAST, AO_SLOW = 5, 34


def _shared(bars: Bars, key, fn):
    k = ("elliott_wave", key)
    if k not in bars.cache:
        bars.cache[k] = fn()
    return bars.cache[k]


def rnd(x: float) -> int:
    """Pine math.round for x >= 0."""
    return int(np.floor(x + 0.5))


def awesome(bars: Bars) -> tuple[np.ndarray, np.ndarray]:
    """(ao as 340 x AO in ticks, valid mask). Exact integers, so zero crosses never depend on float error."""
    s = bars.h.astype(np.int64) + bars.l.astype(np.int64)
    cs = np.concatenate([[0], np.cumsum(s)])
    n = len(s)
    ao = np.zeros(n, dtype=np.int64)
    valid = np.arange(n) >= AO_SLOW - 1
    i = np.flatnonzero(valid)
    ao[i] = AO_SLOW * (cs[i + 1] - cs[i + 1 - AO_FAST]) - AO_FAST * (cs[i + 1] - cs[i + 1 - AO_SLOW])
    return ao, valid


def humps(bars: Bars, ao: np.ndarray, valid: np.ndarray) -> dict[str, np.ndarray]:
    """Per bar, after its close: the current bull hump (high, low after it, max AO) and bear hump (mirror)."""
    h, l = bars.h.tolist(), bars.l.tolist()
    a, v = ao.tolist(), valid.tolist()
    n = len(h)
    NA = sw.NONE
    b_hi, b_after, b_ao = [NA] * n, [NA] * n, [NA] * n
    s_lo, s_after, s_ao = [NA] * n, [NA] * n, [NA] * n
    bh = ba = bm = None
    sl = sa = sm = None
    for j in range(n):
        if v[j]:
            up = a[j] >= 0
            prev_up = None if j == 0 or not v[j - 1] else a[j - 1] >= 0
            if up and prev_up is False:
                bh, ba, bm = h[j], None, a[j]
            elif bh is not None:
                if h[j] >= bh:
                    bh, ba = h[j], None
                else:
                    ba = l[j] if ba is None else min(ba, l[j])
                bm = max(bm, a[j])
            if not up and prev_up is True:
                sl, sa, sm = l[j], None, a[j]
            elif sl is not None:
                if l[j] <= sl:
                    sl, sa = l[j], None
                else:
                    sa = h[j] if sa is None else max(sa, h[j])
                sm = min(sm, a[j])
        b_hi[j] = NA if bh is None else bh
        b_after[j] = NA if ba is None else ba
        b_ao[j] = NA if bm is None else bm
        s_lo[j] = NA if sl is None else sl
        s_after[j] = NA if sa is None else sa
        s_ao[j] = NA if sm is None else sm
    columns = {"b_hi": b_hi, "b_after": b_after, "b_ao": b_ao, "s_lo": s_lo, "s_after": s_after, "s_ao": s_ao}
    return {name: np.asarray(values, dtype=np.int64) for name, values in columns.items()}


def owner_levels(bars: Bars) -> tuple[np.ndarray, np.ndarray]:
    """Current owner 1m swing high / low at each bar close (NONE before the first)."""
    def build():
        m = sw.minute_swings(bars)
        ok = m.at >= 0
        j = np.maximum(m.at, 0)
        return np.where(ok, m.cur_h[j], sw.NONE), np.where(ok, m.cur_l[j], sw.NONE)
    return _shared(bars, "owner", build)


def setups(bars: Bars, session: str, window: int, entry_r: float, stop_r: float, tp_x: float,
           min_len: int) -> dict[str, np.ndarray]:
    """Per bar: sig (+1 / -1 / 0) and the planned limit, stop and tp (ticks) of the entry placed at its close."""
    if not 0 < entry_r < stop_r < 1:
        raise ValueError("need 0 < entry_r < stop_r < 1")
    if tp_x <= 0 or min_len < 1 or window < 1:
        raise ValueError("need tp_x > 0, min_len >= 1 and window >= 1")
    s = SESSIONS[session]
    ao, valid = _shared(bars, "ao", lambda: awesome(bars))
    hp = _shared(bars, "humps", lambda: humps(bars, ao, valid))
    own_h, own_l = owner_levels(bars)
    mod, _ = _shared(bars, ("clock", s.tz), lambda: local_clock(bars.ts, s.tz))

    def rolling():
        ser = pd.Series(ao)
        return (ser.rolling(window).max().to_numpy(), ser.rolling(window).min().to_numpy(),
                pd.Series(bars.l).rolling(window).min().to_numpy(), pd.Series(bars.h).rolling(window).max().to_numpy())
    wmax, wmin, lo_n, hi_n = _shared(bars, ("rolling", window), rolling)

    n = len(bars)
    sig = np.zeros(n, dtype=np.int8)
    limit = np.zeros(n, dtype=np.int64)
    stop = np.zeros(n, dtype=np.int64)
    tp = np.zeros(n, dtype=np.int64)
    first = window - 1 + AO_SLOW - 1  # every AO in the window valid
    in_sess = (mod >= s.open_minute) & (mod < s.flat_minute - 1)
    prev = np.concatenate([[0], ao[:-1]])
    ok = in_sess & (np.arange(n) >= max(first, 1))
    down = np.flatnonzero(ok & (ao < 0) & (prev >= 0))
    up = np.flatnonzero(ok & (ao >= 0) & (prev < 0))
    c = bars.c
    for i in down.tolist():
        top, after = int(hp["b_hi"][i]), int(hp["b_after"][i])
        if not (wmax[i] > 0 and hp["b_ao"][i] == wmax[i] and wmax[i] > -wmin[i]):
            continue
        if top == sw.NONE or after == sw.NONE or own_h[i] != top:
            continue
        L = top - int(lo_n[i])
        if L < min_len:
            continue
        st = top - rnd(stop_r * L)
        if after <= st:
            continue
        lim = min(top - rnd(entry_r * L), int(c[i]))
        sig[i], limit[i], stop[i], tp[i] = LONG, lim, st, lim + rnd(tp_x * L)
    for i in up.tolist():
        bot, after = int(hp["s_lo"][i]), int(hp["s_after"][i])
        if not (wmin[i] < 0 and hp["s_ao"][i] == wmin[i] and -wmin[i] > wmax[i]):
            continue
        if bot == sw.NONE or after == sw.NONE or own_l[i] != bot:
            continue
        L = int(hi_n[i]) - bot
        if L < min_len:
            continue
        st = bot + rnd(stop_r * L)
        if after >= st:
            continue
        lim = max(bot + rnd(entry_r * L), int(c[i]))
        sig[i], limit[i], stop[i], tp[i] = SHORT, lim, st, lim - rnd(tp_x * L)
    return {"sig": sig, "limit": limit, "stop": stop, "tp": tp}


class ElliottWave(Strategy):
    name = "elliott_wave"

    def __init__(self, session: str = "ny", window: int = 120, entry_r: float = 0.382, stop_r: float = 0.618,
                 tp_x: float = 0.618, min_len: int = 20, filters=()):
        if filters:
            raise NotImplementedError("elliott_wave has no feature-2 filters yet")
        # grid winners come back from a DataFrame as numpy floats
        super().__init__((), session=session, window=int(window), entry_r=float(entry_r), stop_r=float(stop_r),
                         tp_x=float(tp_x), min_len=int(min_len))
        self.s = SESSIONS[session]
        self.report_tz = self.s.tz
        self.pending = PendingEntry()

    def prepare(self, bars: Bars) -> np.ndarray:
        p = self.params
        self.bars = bars
        self.pending = PendingEntry()
        self.sig = setups(bars, p["session"], p["window"], p["entry_r"], p["stop_r"], p["tp_x"], p["min_len"])
        self.mod, _ = _shared(bars, ("clock", self.s.tz), lambda: local_clock(bars.ts, self.s.tz))
        return self.sig["sig"] != 0

    def _in_session(self, i: int) -> bool:
        return self.s.open_minute <= self.mod[i] < self.s.flat_minute - 1

    def on_bar(self, ctx: Context, i: int) -> None:
        waiting = self.pending.waiting(ctx, self.bars, i, self._in_session(i))
        if ctx.position_size != 0:
            if not self._in_session(i):
                ctx.close_all("Session end")
            return
        if waiting or self.bars.last_of_contract[i]:
            return
        d = int(self.sig["sig"][i])
        if d == 0 or not self._in_session(i):
            return
        eid = "Long" if d == LONG else "Short"
        tp = int(self.sig["tp"][i])
        ctx.entry(eid, d, limit=int(self.sig["limit"][i]))
        ctx.exit("Exit", eid, stop=int(self.sig["stop"][i]), limit=tp)
        self.pending.place(eid, d, tp)


# --- test definition (python -m tvtester.cli test elliott_wave) -------------------------------------------
STRATEGY = ElliottWave
DOC = "results.md"
TITLE = "Elliott Wave 5 (AO wave count, wave-4 pullback limit), CL1! sessions"
GRID = {"window": [100, 140], "entry_r": [0.382, 0.5], "stop_r": [0.618, 0.786], "tp_x": [0.618, 1.0],
        "min_len": [20, 40]}
VARIANTS = {"asia": {"session": "asia"}, "london": {"session": "london"}, "ny": {"session": "ny"}}
ABOUT = """
Spec and sources: [README.md](README.md). Waves are counted on the Awesome Oscillator (AO = SMA5(hl2) -
SMA34(hl2), 1m) as in "10 Seconds Elliott Wave" (iTradeAIMS, after Bill Williams); the Fibonacci levels come
from that book and markokrivokapic.com. Long side below; the short side is the mirror.

- **Wave 3.** The tallest AO peak of the last `window` bars (the book's 100-140 bar rule) is green, taller than
  the deepest red AO in that window, and belongs to the current AO hump.
- **Wave 4 confirmed.** AO crosses below zero. Decision at that 1m close, inside the session only.
- **Anchors.** Top = the hump's highest high, which must be the current owner 1m swing high
  ([`indicators/structure_swings.pine`](../../../indicators/structure_swings.pine)). Base = lowest low of the
  window. L = top - base, at least `min_len` ticks.
- **Entry: limit only.** Buy limit at top - `entry_r` x L (or the signal close if lower), working from the next
  bar. Skipped when the pullback has already touched the stop level.
- **Exits.** Stop at top - `stop_r` x L (the book: a wave 4 deeper than about 62 % truncates wave 5). Target
  = limit + `tp_x` x L (the book's Target Zones 1 / 2: 61.8 % / 100 %). Flat at the session end.
- An unfilled limit is cancelled when a 1m close finds the target touched, at the session end, and on the
  contract's last bar. One position or working order at a time.

| Variant | Session (own time zone) | Malaysia time (UTC+8) | Flat at |
|---|---|---|---|
| asia | 09:00 Asia/Shanghai | 09:00 | 15:00 Asia/Shanghai |
| london | 08:00 Europe/London | 15:00 / 16:00 (UK summer / winter) | 13:00 London |
| ny | 09:00 America/New_York | 21:00 / 22:00 (US summer / winter) | 14:30 New York |

Commission $2.01 per order, no slippage (limit entries). In-sample: the grid's best of 32 per session on all
available bars, including the reserved 2024+ interval. A runnable Pine v6 twin is in
[`strategies/elliott_wave.pine`](../../../strategies/elliott_wave.pine).
"""


def notes(tf, params) -> list[str]:
    s = SESSIONS[params["session"]]
    out = []
    if not tf.empty:
        lt = tf["exit_time"].dt.tz_convert(s.tz)
        mod = lt.dt.hour * 60 + lt.dt.minute
        late = ((tf["exit_reason"] == "close") & ((mod > s.flat_minute + 5) | (mod < s.open_minute))).sum()
        out.append(f"Session-end exits more than 5 minutes after the flat time (missing bars / early closes): {late}.")
        out.append(f"Roll exits: {(tf['exit_reason'] == 'roll').sum()}.")
    return out
