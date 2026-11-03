"""Owner swing points (indicators/structure_swings.pine) on 1-minute bars and on higher-timeframe candles built from them.

Swing rule (owner, indicator): swing high at candle k when high[k-1] <= high[k] and high[k+1] < high[k] (low mirror),
known when candle k+1 closes. Alternation: a second swing high with no swing low between replaces the last one if it
is at least as high (equal: the later one), otherwise it is dropped. Outside candle (both): added in the order its
extremes printed (first 1m bar printing each; same 1m bar: high first when the high is nearer the open). Labels:
equal high = HH, equal low = LL.

Higher-timeframe candles (CL1! exchange sessions, America/New_York clock; the CME day runs 18:00 to 17:00 ET):
- 5m / 15m / 1h: clock aligned. 4h: anchored at 18:00 ET (18, 22, 02, 06, 10, 14; the last one runs to 18:00, so
  bars in the 17:00-18:00 halt, which 2010 data has, belong to it).
  1d: the trading day starting 18:00 ET (Sunday evening belongs to Monday).
- Closed candles only. A candle closes at the close of its last 1m bar when that bar is the candle's last minute;
  otherwise (missing last minute, early close, the day's last 4h / daily candle) when the next bar, the first of a
  later candle, closes. The day's last 4h and daily candles therefore close on the 18:00 ET reopen bar.

Trend per timeframe (owner, answers 21 and 28): down when the last uptrend HL (the current swing low, labelled HL)
is touched by a closed candle (low <= HL); up when the last downtrend LH is touched (high >= LH). A touched level is
used up until the swing it belongs to changes. Both in one candle: the later touch (1m bars) decides.

The Pine twin of all of this is inside strategies/tupa_trade.pine (same rules, bar by bar).
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .data import Bars

NY = "America/New_York"
SH, SL = 1, -1
TIMEFRAMES = ("5m", "15m", "1h", "4h", "1d")  # bias timeframes, low to high
_MS = {"5m": 300_000, "15m": 900_000, "1h": 3_600_000}
NONE = -(2 ** 62)  # "no swing yet" in tick arrays (CL traded below zero, so -1 is a price)


def open_rule_high_first(o, h, l):
    """Broker-emulator path: high first when the high is nearer the open (tie -> low first)."""
    return (h - o) < (o - l)


def candle_ids(ts: pd.DatetimeIndex, tf: str, next_minute: bool = False) -> np.ndarray:
    """Candle id of each bar open (or of the minute after it). No special case for the 17:00-18:00 ET halt: the day's
    last 4h candle and the daily candle run to 18:00, so they close when the next session's first bar closes (no
    trading decision falls in between). Bars inside the halt (2010 data: CME's break was shorter) stay in that
    candle (R19)."""
    t = ts + pd.Timedelta(minutes=1) if next_minute else ts
    lt = t.tz_convert(NY)
    m = (lt.hour * 60 + lt.minute).to_numpy()
    if tf in _MS:
        ids = t.as_unit("ms").asi8 // _MS[tf]
    else:
        d = (t + pd.Timedelta(hours=6)).tz_convert(NY)
        day = (d.year * 10000 + d.month * 100 + d.day).to_numpy().astype(np.int64)
        ids = day * 10 + ((m + 360) % 1440) // 240 if tf == "4h" else day
    return np.asarray(ids, dtype=np.int64)


@dataclass
class Candles:
    start: np.ndarray  # first 1m bar index
    end: np.ndarray  # last 1m bar index
    visible: np.ndarray  # 1m bar at whose close the candle is known closed (len(bars) = never)
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    hi_first: np.ndarray  # high printed before the low (1m order)


def candles(bars: Bars, tf: str) -> Candles:
    ids = candle_ids(bars.ts, tf)
    nxt = candle_ids(bars.ts, tf, next_minute=True)
    n = len(ids)
    start = np.concatenate([[0], np.flatnonzero(ids[1:] != ids[:-1]) + 1])
    end = np.concatenate([start[1:] - 1, [n - 1]])
    complete = nxt[end] != ids[end]
    visible = np.where(complete, end, end + 1)
    h = np.maximum.reduceat(bars.h, start)
    l = np.minimum.reduceat(bars.l, start)
    cn = np.repeat(np.arange(len(start)), end - start + 1)
    idx = np.arange(n)
    big = np.iinfo(np.int64).max
    hi_i = np.minimum.reduceat(np.where(bars.h == h[cn], idx, big), start)
    lo_i = np.minimum.reduceat(np.where(bars.l == l[cn], idx, big), start)
    same = open_rule_high_first(bars.o[hi_i], bars.h[hi_i], bars.l[hi_i])
    hi_first = np.where(hi_i == lo_i, same, hi_i < lo_i)
    return Candles(start, end, visible, bars.o[start], h, l, bars.c[end], hi_first)


class Zig:
    """Swing state of the indicator's `Zig` type (prices in ticks)."""

    __slots__ = ("last_type", "last_price", "cur_h", "prev_h", "cur_l", "prev_l", "idx_h", "idx_l", "n_h", "n_l")

    def __init__(self):
        self.last_type = 0
        self.last_price = 0
        self.cur_h = self.prev_h = self.cur_l = self.prev_l = None
        self.idx_h = self.idx_l = -1  # candle index of the current swing high / low
        self.n_h = self.n_l = 0  # swing highs / lows added or moved (dropped pivots do not count)

    def push(self, t: int, p: int, k: int) -> bool:
        if self.last_type == t:
            if not (p >= self.last_price if t == SH else p <= self.last_price):
                return False  # dropped: not a swing
        elif t == SH:
            self.prev_h = self.cur_h
        else:
            self.prev_l = self.cur_l
        if t == SH:
            self.cur_h, self.idx_h, self.n_h = p, k, self.n_h + 1
        else:
            self.cur_l, self.idx_l, self.n_l = p, k, self.n_l + 1
        self.last_type, self.last_price = t, p
        return True

    def pivots(self, hk1: int, hk: int, hk2: int, lk1: int, lk: int, lk2: int, hi_first: bool, k: int) -> tuple:
        """Candle k with neighbours k-1 (hk1, lk1) and k+1 (hk2, lk2). Returns (high added, low added)."""
        is_h = hk1 <= hk and hk2 < hk
        is_l = lk1 >= lk and lk2 > lk
        add_h = add_l = False
        if is_h and is_l:
            if hi_first:
                add_h = self.push(SH, hk, k)
                add_l = self.push(SL, lk, k)
            else:
                add_l = self.push(SL, lk, k)
                add_h = self.push(SH, hk, k)
        elif is_h:
            add_h = self.push(SH, hk, k)
        elif is_l:
            add_l = self.push(SL, lk, k)
        return add_h, add_l

    @property
    def low_is_hl(self) -> bool:
        return self.prev_l is not None and self.cur_l > self.prev_l

    @property
    def high_is_lh(self) -> bool:
        return self.prev_h is not None and self.cur_h < self.prev_h


@dataclass
class TfState:
    """Per-candle state after the candle closed, and the 1m bar it applies from."""

    visible: np.ndarray
    last_type: np.ndarray  # newest swing: SH / SL / 0
    trend: np.ndarray  # 1 up, -1 down, 0 none yet
    cur_h: np.ndarray  # ticks, NONE when none
    cur_l: np.ndarray

    def at_bars(self, n: int) -> np.ndarray:
        """Index of the state that applies at each 1m bar close (-1 = none yet)."""
        return np.searchsorted(self.visible, np.arange(n), side="right") - 1


def timeframe_state(bars: Bars, tf: str) -> TfState:
    cd = candles(bars, tf)
    m = len(cd.start)
    last_type = np.zeros(m, dtype=np.int8)
    trend_out = np.zeros(m, dtype=np.int8)
    cur_h = np.full(m, NONE, dtype=np.int64)
    cur_l = np.full(m, NONE, dtype=np.int64)
    z = Zig()
    trend, dn_used, up_used = 0, False, False
    H, L, hf = cd.h.tolist(), cd.l.tolist(), cd.hi_first.tolist()
    for j in range(m):
        dn = z.cur_l if (z.low_is_hl and not dn_used) else None
        up = z.cur_h if (z.high_is_lh and not up_used) else None
        td = dn is not None and L[j] <= dn
        tu = up is not None and H[j] >= up
        if td and tu:
            s, e = cd.start[j], cd.end[j] + 1
            fd = s + int(np.argmax(bars.l[s:e] <= dn))
            fu = s + int(np.argmax(bars.h[s:e] >= up))
            if fd == fu:
                up_last = not open_rule_high_first(bars.o[fd], bars.h[fd], bars.l[fd])
            else:
                up_last = fu > fd
            trend, dn_used, up_used = (1 if up_last else -1), True, True
        elif td:
            trend, dn_used = -1, True
        elif tu:
            trend, up_used = 1, True
        if j >= 2:
            k = j - 1
            add_h, add_l = z.pivots(H[k - 1], H[k], H[j], L[k - 1], L[k], L[j], hf[k], k)
            if add_h:
                up_used = False
            if add_l:
                dn_used = False
        last_type[j], trend_out[j] = z.last_type, trend
        cur_h[j] = NONE if z.cur_h is None else z.cur_h
        cur_l[j] = NONE if z.cur_l is None else z.cur_l
    return TfState(cd.visible, last_type, trend_out, cur_h, cur_l)


@dataclass
class MinuteSwings:
    """1m swing events (state after each event) and, per bar, the event that applies at its close."""

    bar: np.ndarray  # bar whose close confirmed the event
    last_type: np.ndarray
    cur_h: np.ndarray
    prev_h: np.ndarray  # NONE when none
    cur_l: np.ndarray
    prev_l: np.ndarray
    idx_h: np.ndarray  # bar index of the swing high / low candle
    idx_l: np.ndarray
    n_h: np.ndarray
    n_l: np.ndarray
    at: np.ndarray  # per bar: event index (-1 none)


def minute_swings(bars: Bars) -> MinuteSwings:
    o, h, l = bars.o, bars.h, bars.l
    n = len(bars)
    is_h = np.zeros(n, dtype=bool)
    is_l = np.zeros(n, dtype=bool)
    is_h[2:] = (h[:-2] <= h[1:-1]) & (h[2:] < h[1:-1])  # pivot at i-1, confirmed at the close of bar i
    is_l[2:] = (l[:-2] >= l[1:-1]) & (l[2:] > l[1:-1])
    hf = np.zeros(n, dtype=bool)
    hf[2:] = open_rule_high_first(o[1:-1], h[1:-1], l[1:-1])
    z = Zig()
    rows = []
    for i in np.flatnonzero(is_h | is_l).tolist():
        k = i - 1
        add_h, add_l = z.pivots(int(h[k - 1]), int(h[k]), int(h[i]), int(l[k - 1]), int(l[k]), int(l[i]),
                                bool(hf[i]), k)
        if add_h or add_l:
            rows.append((i, z.last_type, NONE if z.cur_h is None else z.cur_h, NONE if z.prev_h is None else z.prev_h,
                         NONE if z.cur_l is None else z.cur_l, NONE if z.prev_l is None else z.prev_l,
                         z.idx_h, z.idx_l, z.n_h, z.n_l))
    a = np.array(rows, dtype=np.int64).reshape(-1, 10)
    ev = a[:, 0]
    return MinuteSwings(ev, a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5], a[:, 6], a[:, 7], a[:, 8], a[:, 9],
                        np.searchsorted(ev, np.arange(n), side="right") - 1)
