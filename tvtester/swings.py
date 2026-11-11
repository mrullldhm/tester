"""Owner swing points (indicators/structure_swings.pine) on 1-minute bars and on higher-timeframe candles built from them.

Swing rule (owner, indicator): swing high at candle k when high[k-1] <= high[k] and high[k+1] < high[k] (low mirror),
known when candle k+1 closes. Alternation: a second swing high with no swing low between replaces the last one if it
is at least as high (equal: the later one), otherwise it is dropped. Outside candle (both): added in the order its
extremes printed (first 1m bar printing each; same 1m bar: high first when the high is nearer the open). Labels:
equal high = HH, equal low = LL. An accepted high must also be the highest high since the accepted low
(low mirror); all intervening candles count, including those that are not pivots. Same-candle extremes
are observed in their 1m order. Owner clarification, 2026-11-05.
Owner clarification, 2026-11-10: the newest endpoint is provisional until an opposite swing is accepted.
An equal touch/breach before then removes it immediately, restoring the surviving fixed structure.
On historical data removal is visible at the first touching 1m close, including inside forming HTF candles.
At a right-candle close, accept a qualifying opposite pivot before applying that candle's touch removal.
An endpoint removed during a forming HTF candle can therefore be secured/restored by the opposite pivot
confirmed at its close. Previously emitted decisions are never backdated or erased.

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
_MS = {"5m": 300_000, "15m": 900_000, "30m": 1_800_000, "1h": 3_600_000}
NONE = -(2 ** 62)  # "no swing yet" in tick arrays (CL traded below zero, so -1 is a price)
SWING_RULE = "structure-swings-v4-opposite-confirmation-first"


def require_owner_swing(strength=1):
    """Compatibility guard: swing detection is fixed, never a research parameter."""
    if strength != 1:
        raise ValueError("Swing rules are fixed by indicators/structure_swings.pine; swing must be 1")


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

    __slots__ = ("last_type", "last_price", "cur_h", "prev_h", "cur_l", "prev_l", "idx_h", "idx_l", "n_h", "n_l",
                 "hi_since_l", "lo_since_h", "pending", "_before", "recovered_type")

    _RESTORE = ("last_type", "last_price", "cur_h", "prev_h", "cur_l", "prev_l", "idx_h", "idx_l",
                "hi_since_l", "lo_since_h")

    def __init__(self):
        self.last_type = 0
        self.last_price = 0
        self.cur_h = self.prev_h = self.cur_l = self.prev_l = None
        self.idx_h = self.idx_l = -1  # candle index of the current swing high / low
        self.n_h = self.n_l = 0  # high/low revisions: added, moved or removed; dropped pivots do not count
        self.hi_since_l = self.lo_since_h = None
        self.pending = False
        self._before = None
        self.recovered_type = 0

    def copy(self):
        """A source-candle opening checkpoint; no shared mutable leg-boundary backup."""
        other = Zig()
        for name in self.__slots__:
            value = getattr(self, name)
            setattr(other, name, value.copy() if name == "_before" and value is not None else value)
        return other

    @property
    def candidate_type(self):
        return self.last_type if self.pending else 0

    def invalidate(self, h: int, l: int) -> bool:
        """An equal touch removes only the provisional endpoint.

        Restore the surviving structure, never an earlier provisional version of a replaced endpoint.
        Counts remain monotonic event ids. Historical states emitted before this touch are unchanged.
        """
        if not self.pending or not (h >= self.last_price if self.last_type == SH else l <= self.last_price):
            return False
        if self.last_type == SH:
            self.n_h += 1
        else:
            self.n_l += 1
        observed_h, observed_l = self.hi_since_l, self.lo_since_h
        for name, value in zip(self._RESTORE, self._before):
            setattr(self, name, value)
        self.pending = False
        self._before = None
        if observed_h is not None:
            self.hi_since_l = observed_h if self.hi_since_l is None else max(self.hi_since_l, observed_h)
        if observed_l is not None:
            self.lo_since_h = observed_l if self.lo_since_h is None else min(self.lo_since_h, observed_l)
        if self.hi_since_l is not None:
            self.hi_since_l = max(self.hi_since_l, h)
        if self.lo_since_h is not None:
            self.lo_since_h = min(self.lo_since_h, l)
        return True

    def push(self, t: int, p: int, k: int) -> bool:
        if t == SH and self.hi_since_l is not None and p < self.hi_since_l:
            return False
        if t == SL and self.lo_since_h is not None and p > self.lo_since_h:
            return False
        if self.last_type == t:
            if not (p >= self.last_price if t == SH else p <= self.last_price):
                return False  # dropped: not a swing
        if self.last_type != t or not self.pending:
            self._before = [getattr(self, name) for name in self._RESTORE]
        if self.last_type != t and t == SH:
            self.prev_h = self.cur_h
        elif self.last_type != t:
            self.prev_l = self.cur_l
        if t == SH:
            self.cur_h, self.idx_h, self.n_h = p, k, self.n_h + 1
            self.lo_since_h = p
        else:
            self.cur_l, self.idx_l, self.n_l = p, k, self.n_l + 1
            self.hi_since_l = p
        self.last_type, self.last_price = t, p
        self.pending = True
        return True

    def visit(self, t: int, p: int, k: int, is_pivot: bool) -> bool:
        """Observe every extreme in time order; only fixed-rule pivots can become swings."""
        added = self.push(t, p, k) if is_pivot else False
        if self._before is not None:
            j = 8 if t == SH else 9
            old = self._before[j]
            if old is not None:
                self._before[j] = max(old, p) if t == SH else min(old, p)
        if t == SH and self.hi_since_l is not None:
            self.hi_since_l = max(self.hi_since_l, p)
        elif t == SL and self.lo_since_h is not None:
            self.lo_since_h = min(self.lo_since_h, p)
        return added

    def pivots(self, hk1: int, hk: int, hk2: int, lk1: int, lk: int, lk2: int, hi_first: bool, k: int,
               opening=None) -> tuple:
        """Candle k with neighbours k-1 (hk1, lk1) and k+1 (hk2, lk2). Returns (high added, low added)."""
        self.recovered_type = 0
        if opening is not None and opening.pending and not self.pending:
            # A live removal was known earlier, but a pivot on the intervening source candle
            # may now secure that endpoint. Evaluate only NOW, when the right candle closed.
            probe = opening.copy()
            accepted = probe.pivots(hk1, hk, hk2, lk1, lk, lk2, hi_first, k)
            if any(accepted):
                for name in self._RESTORE:
                    setattr(self, name, getattr(opening, name))
                self._before = None if opening._before is None else opening._before.copy()
                self.pending = True
                self.recovered_type = opening.last_type
        is_h = hk1 <= hk and hk2 < hk
        is_l = lk1 >= lk and lk2 > lk
        if hi_first:
            add_h = self.visit(SH, hk, k, is_h)
            add_l = self.visit(SL, lk, k, is_l)
        else:
            add_l = self.visit(SL, lk, k, is_l)
            add_h = self.visit(SH, hk, k, is_h)
        return add_h, add_l

    @property
    def low_is_hl(self) -> bool:
        return self.cur_l is not None and self.prev_l is not None and self.cur_l > self.prev_l

    @property
    def high_is_lh(self) -> bool:
        return self.cur_h is not None and self.prev_h is not None and self.cur_h < self.prev_h


@dataclass
class TfState:
    """Sparse states at candle closes and at the first 1m close removing a provisional swing."""

    visible: np.ndarray
    last_type: np.ndarray  # provisional swing: SH / SL / 0 (none, including after removal)
    trend: np.ndarray  # 1 up, -1 down, 0 none yet
    cur_h: np.ndarray  # ticks, NONE when none
    cur_l: np.ndarray

    def at_bars(self, n: int) -> np.ndarray:
        """Index of the state that applies at each 1m bar close (-1 = none yet)."""
        return np.searchsorted(self.visible, np.arange(n), side="right") - 1


def timeframe_state(bars: Bars, tf: str) -> TfState:
    cd = candles(bars, tf)
    z = Zig()
    trend, dn_used, up_used = 0, False, False
    H, L, hf = cd.h.tolist(), cd.l.tolist(), cd.hi_first.tolist()
    highs, lows = bars.h.tolist(), bars.l.tolist()
    paths = open_rule_high_first(bars.o, bars.h, bars.l)
    fd = np.full(len(cd.start), -1, dtype=np.int64)
    fu = np.full(len(cd.start), -1, dtype=np.int64)
    rows = []

    def emit(i):
        rows.append((i, z.candidate_type, trend, NONE if z.cur_h is None else z.cur_h,
                     NONE if z.cur_l is None else z.cur_l))

    def finish(j, i):
        nonlocal trend, dn_used, up_used
        if fd[j] >= 0 and fu[j] >= 0:
            up_last = not paths[fd[j]] if fd[j] == fu[j] else fu[j] > fd[j]
            trend, dn_used, up_used = (1 if up_last else -1), True, True
        elif fd[j] >= 0:
            trend, dn_used = -1, True
        elif fu[j] >= 0:
            trend, up_used = 1, True
        if j >= 2:
            k = j - 1
            add_h, add_l = z.pivots(H[k - 1], H[k], H[j], L[k - 1], L[k], L[j], hf[k], k, opening=opening)
            if add_h:
                up_used = False
            if add_l:
                dn_used = False
        emit(i)

    j = 0
    opening = z.copy()
    for i, (h, l) in enumerate(zip(highs, lows)):
        # A candle missing its last minute closes before feeding the next candle's first bar,
        # exactly as the Pine accumulator. Never expose its pivots on an earlier minute.
        if i > cd.end[j]:
            if cd.visible[j] == i:
                finish(j, i)
            j += 1
            opening = z.copy()
        if z.low_is_hl and not dn_used and fd[j] < 0 and l <= z.cur_l:
            fd[j] = i
        if z.high_is_lh and not up_used and fu[j] < 0 and h >= z.cur_h:
            fu[j] = i
        if cd.visible[j] == i and cd.end[j] == i:
            finish(j, i)
        if z.invalidate(h, l):
            emit(i)
    if not rows:
        rows.append((len(bars), 0, 0, NONE, NONE))
    a = np.asarray(rows, dtype=np.int64).reshape(-1, 5)
    return TfState(a[:, 0], a[:, 1].astype(np.int8), a[:, 2].astype(np.int8), a[:, 3], a[:, 4])


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
    added_h: np.ndarray  # actual accepted pivots; removals are state events, never new pivot signals
    added_l: np.ndarray


def minute_swings(bars: Bars) -> MinuteSwings:
    o, h, l = bars.o, bars.h, bars.l
    n = len(bars)
    hf = np.zeros(n, dtype=bool)
    hf[2:] = open_rule_high_first(o[1:-1], h[1:-1], l[1:-1])
    z = Zig()
    rows = []
    # Non-pivot candles can contain the leg extreme and must also be observed.
    for i in range(2, n):
        k = i - 1
        add_h, add_l = z.pivots(int(h[k - 1]), int(h[k]), int(h[i]), int(l[k - 1]), int(l[k]), int(l[i]),
                                bool(hf[i]), k)
        removed = z.invalidate(int(h[i]), int(l[i]))
        if removed or add_h or add_l:
            rows.append((i, z.candidate_type, NONE if z.cur_h is None else z.cur_h, NONE if z.prev_h is None else z.prev_h,
                         NONE if z.cur_l is None else z.cur_l, NONE if z.prev_l is None else z.prev_l,
                         z.idx_h, z.idx_l, z.n_h, z.n_l, add_h, add_l))
    a = np.array(rows, dtype=np.int64).reshape(-1, 12)
    ev = a[:, 0]
    return MinuteSwings(ev, a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5], a[:, 6], a[:, 7], a[:, 8], a[:, 9],
                        np.searchsorted(ev, np.arange(n), side="right") - 1, a[:, 10].astype(bool), a[:, 11].astype(bool))


def minute_swing_series(bars: Bars) -> dict[str, np.ndarray]:
    """Fixed owner swings: accepted events and carried levels, visible only at confirmation.

    Previous levels are the preceding alternating swings of the same type, so moving
    the newest swing never turns a replacement into a new structural comparison.
    """
    key = (SWING_RULE, "minute-series")
    if key in bars.cache:
        return bars.cache[key]
    m = minute_swings(bars)
    out = {}
    for name, current, previous, added in (
        ("high", m.cur_h, m.prev_h, m.added_h), ("low", m.cur_l, m.prev_l, m.added_l)
    ):
        event = np.full(len(bars), np.nan)
        prev = np.full(len(bars), np.nan)
        event[m.bar[added]] = current[added]
        valid_prev = added & (previous != NONE)
        prev[m.bar[valid_prev]] = previous[valid_prev]
        level = np.full(len(bars), np.nan)
        valid = m.at >= 0
        level[valid] = current[m.at[valid]]
        level[level == NONE] = np.nan
        out[name], out[f"prev_{name}"], out[f"last_{name}"] = event, prev, level
    bars.cache[key] = out
    return out
