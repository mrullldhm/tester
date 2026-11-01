"""Exit management shared by the strategies: breakeven, trailing stop and time exit, at each 1m bar close.

Every rule here is a custom stop moved (or a market close sent) at the bar close, so it works from the next bar.
It is not Pine's native intrabar `trail_points`. docs/ENGINE.md "Exit management" has the rules; the Pine twins
compute the same. Units, all integer ticks:
- T = the trade's target distance (the `profit=` ticks, or |limit - fill| for a price target), frozen at entry.
- entry = the actual fill (slippage included, Pine strategy.position_avg_price).
- best = most favourable bar extreme since the entry bar, entry bar included (entries are market orders at an
  open, so the whole entry bar follows the fill); fav = (best - entry) x direction.
- rnd = round half up (Pine math.round for x >= 0). Indicator levels (ATR / EMA / SAR, float ticks) are rounded
  toward the trade's side: floor for a long stop, ceil for a short stop (1e-6 guard, as the twin divides dollars).

Breakeven `be` (stop to entry + direction x `be_offset` ticks):
- "touch": fav >= rnd(be_x x T)           "close": (close - entry) x direction >= rnd(be_x x T)
- "time":  age >= be_x bars (age = i - entry bar + 1) and (close - entry) x direction > be_offset
Trailing `trail` (active once fav >= rnd(trail_at x T); best only grows, so activation latches):
- "frac":  best - direction x max(1, rnd(trail_x x T))
- "atr":   best - direction x trail_x x ATR(14) of the 1m chart at bar i (chandelier)
- "swing": the last pivot low (long) / high (short) confirmed at or before bar i, strength trail_x
           (Pine ta.pivotlow(low, n, n); value known n bars after the pivot bar)
- "step":  s = max(1, rnd(trail_x x T)), m = floor(fav / s); m >= 1: entry + direction x (m - 1) x s
- "close": best close since the entry bar (its close included) - direction x max(1, rnd(trail_x x T))
- "ema":   EMA(trail_x) of the 1m close, only while on the trade's side of the close
- "sar":   ta.sar(SAR_SETS[trail_x]) of the 1m chart, only while on the trade's side of the close
The stop becomes the tightest of the current stop and the active levels; never looser (strategy policy). A level
already through the close is a triggered stop and fills at the next open.
`time_exit` N > 0: at the close of the bar where age >= N, cancel the bracket and close at market (next open).
`keep_target=False` (needs a trailing stop or a time exit): no profit leg, from the entry on.
Indicators (ATR, EMA, pivots, SAR) are computed over every bar, flat or not, as Pine does.
Defaults (be="none", trail="none", time_exit=0, keep_target=True) leave the strategy exactly as it was.
"""

import math
from dataclasses import dataclass

import numpy as np

from . import ta

LONG = 1
BE_STYLES = ("none", "touch", "close", "time")
TRAIL_STYLES = ("none", "frac", "atr", "swing", "step", "close", "ema", "sar")
SAR_SETS = ((0.02, 0.02, 0.2), (0.01, 0.01, 0.1))  # (start, increment, maximum)
ATR_LEN = 14
UNVERIFIED = ("swing", "sar")  # Python transcriptions of ta.pivotlow / ta.sar, not yet checked against a TV export


def rnd(x: float) -> int:
    """Round half up, as Pine math.round for x >= 0."""
    return math.floor(x + 0.5 + 1e-9)


def _toward(x: float, direction: int) -> int:
    """An indicator stop level in ticks, rounded to the trade's side (long: down, short: up)."""
    return math.floor(x + 1e-6) if direction == LONG else math.ceil(x - 1e-6)


@dataclass(frozen=True)
class ExitRule:
    be: str = "none"
    be_x: float = 0.0  # touch / close: fraction of T; time: bars
    be_offset: int = 0
    trail: str = "none"
    trail_at: float = 0.0  # fraction of T where trailing starts
    trail_x: float = 0.0  # the style's own setting (see module doc)
    keep_target: bool = True
    time_exit: int = 0  # bars; 0 = off

    def __post_init__(self):
        if self.be not in BE_STYLES or self.trail not in TRAIL_STYLES:
            raise ValueError(f"be in {BE_STYLES}, trail in {TRAIL_STYLES}")
        if min(self.be_x, self.be_offset, self.trail_at, self.trail_x, self.time_exit) < 0:
            raise ValueError("exit rule values must be >= 0")
        if (self.be != "none") != (self.be_x > 0):
            raise ValueError("breakeven needs be_x > 0, and be_x needs a breakeven style")
        if self.trail not in ("none", "sar") and self.trail_x <= 0:
            raise ValueError("this trailing style needs trail_x > 0")
        if self.trail == "sar" and int(self.trail_x) not in range(len(SAR_SETS)):
            raise ValueError("sar: trail_x is an index into SAR_SETS")
        if self.trail in ("swing", "ema") and self.trail_x != int(self.trail_x):
            raise ValueError("swing / ema: trail_x is a whole number of bars")
        if self.trail == "step" and self.trail_at != 0:
            raise ValueError("step trailing has no start setting")
        if not self.keep_target and self.trail == "none" and self.time_exit == 0:
            raise ValueError("keep_target=False needs a trailing stop or a time exit")

    @property
    def active(self) -> bool:
        return self.be != "none" or self.trail != "none" or self.time_exit > 0

    def params(self) -> dict:
        """Strategy keyword arguments that differ from the defaults (so plain strategies keep their labels)."""
        d = ExitRule()
        return {k: getattr(self, k) for k in d.__dataclass_fields__ if getattr(self, k) != getattr(d, k)}

    def family(self) -> str:
        """Report family: baseline, be_<style>, trail_<style>, both, time_exit."""
        if self.time_exit:
            return "time_exit"
        if self.be != "none" and self.trail != "none":
            return "both"
        if self.be != "none":
            return f"be_{self.be}"
        if self.trail != "none":
            return f"trail_{self.trail}"
        return "baseline"

    def label(self) -> str:
        parts = []
        if self.be == "time":
            parts.append(f"BE after {self.be_x:g} bars +{self.be_offset}t")
        elif self.be != "none":
            parts.append(f"BE {self.be} {self.be_x:g}T +{self.be_offset}t")
        if self.trail != "none":
            v = self.trail_x
            x = ("SAR " + "/".join(map(str, SAR_SETS[int(v)])) if self.trail == "sar" else
                 {"frac": f"{v:g}T", "atr": f"{v:g} ATR", "swing": f"pivot {v:g}", "step": f"step {v:g}T",
                  "close": f"close {v:g}T", "ema": f"EMA {v:g}"}[self.trail])
            parts.append(f"trail {x}" + (f" from {self.trail_at:g}T" if self.trail_at else ""))
        if self.time_exit:
            parts.append(f"time exit {self.time_exit} bars")
        if not self.keep_target:
            parts.append("no target")
        return "; ".join(parts) or "none"


# --- indicators (whole bar arrays, cached on the Bars object) ---------------------------------------------
def pivots(x: np.ndarray, n: int, high: bool) -> np.ndarray:
    """Pine ta.pivothigh / ta.pivotlow(x, n, n) as a series: the pivot value at the confirmation bar j + n,
    NaN elsewhere. Tie rule (UNVERIFIED vs TradingView): a low pivot is <= each of the n older bars and < each of
    the n newer bars; a high pivot mirrors (>= older, > newer)."""
    out = np.full(len(x), np.nan)
    if len(x) < 2 * n + 1:
        return out
    xf = x.astype(float)
    m = len(x) - 2 * n
    center = xf[n: n + m]
    ok = np.ones(m, dtype=bool)
    for k in range(1, n + 1):
        older, newer = xf[n - k: n - k + m], xf[n + k: n + k + m]
        ok &= ((center >= older) & (center > newer)) if high else ((center <= older) & (center < newer))
    out[2 * n:] = np.where(ok, center, np.nan)
    return out


def carry(x: np.ndarray) -> np.ndarray:
    """Last non-NaN value at or before each bar (Pine `var` set when the series is not na)."""
    idx = np.where(~np.isnan(x), np.arange(len(x)), -1)
    idx = np.maximum.accumulate(idx)
    out = np.full(len(x), np.nan)
    ok = idx >= 0
    out[ok] = x[idx[ok]]
    return out


def sar(h: np.ndarray, l: np.ndarray, c: np.ndarray, start: float, inc: float, mx: float) -> np.ndarray:
    """Literal transcription of the Pine reference `pine_sar` (ta.sar). na on bar 0, initialised on bar 1.
    UNVERIFIED against a TradingView export."""
    n = len(c)
    out = np.full(n, np.nan)
    if n < 2:
        return out
    H, L, C = h.astype(float).tolist(), l.astype(float).tolist(), c.astype(float).tolist()
    vals = out.tolist()
    result = max_min = acc = 0.0
    is_below = False
    for i in range(1, n):
        first = False
        if i == 1:
            if C[1] > C[0]:
                is_below, max_min, result = True, H[1], L[0]
            else:
                is_below, max_min, result = False, L[1], H[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if is_below:
            if result > L[i]:
                first, is_below = True, False
                result = max(H[i], max_min)
                max_min, acc = L[i], start
        elif result < H[i]:
            first, is_below = True, True
            result = min(L[i], max_min)
            max_min, acc = H[i], start
        if not first:
            if is_below:
                if H[i] > max_min:
                    max_min, acc = H[i], min(acc + inc, mx)
            elif L[i] < max_min:
                max_min, acc = L[i], min(acc + inc, mx)
        if is_below:
            result = min(result, L[i - 1])
            if i > 1:
                result = min(result, L[i - 2])
        else:
            result = max(result, H[i - 1])
            if i > 1:
                result = max(result, H[i - 2])
        vals[i] = result
    return np.asarray(vals)


def _cached(bars, key, fn):
    k = ("exits", *key)
    if k not in bars.cache:
        bars.cache[k] = fn()
    return bars.cache[k]


def levels(bars, rule: ExitRule) -> dict:
    """Per-bar indicator arrays the rule needs (float ticks)."""
    h, l, c = bars.h, bars.l, bars.c
    t = rule.trail
    if t == "atr":
        return {"atr": _cached(bars, ("atr", ATR_LEN), lambda: ta.atr(h, l, c, ATR_LEN))}
    if t == "ema":
        n = int(rule.trail_x)
        return {"ema": _cached(bars, ("ema", n), lambda: ta.ema(c.astype(float), n))}
    if t == "swing":
        n = int(rule.trail_x)
        return {"pl": _cached(bars, ("pl", n), lambda: carry(pivots(l, n, False))),
                "ph": _cached(bars, ("ph", n), lambda: carry(pivots(h, n, True)))}
    if t == "sar":
        s = SAR_SETS[int(rule.trail_x)]
        return {"sar": _cached(bars, ("sar", s), lambda: sar(h, l, c, *s))}
    return {}


# --- per-trade manager ------------------------------------------------------------------------------------
class Manager:
    """What a strategy calls at each bar close while in a position. Holds the per-trade state (Pine `var`s reset
    on the entry bar)."""

    def __init__(self, rule: ExitRule):
        self.rule = rule
        self.bars = None
        self.ind: dict = {}
        self.entry_bar = -1
        self.best = self.best_close = 0
        self.moved: set[int] = set()  # entry bars of trades whose stop these rules moved (diagnostic)
        self.timed: set[int] = set()  # entry bars of trades closed by the time exit

    def prepare(self, bars) -> None:
        self.__init__(self.rule)
        self.bars = bars
        self.ind = levels(bars, self.rule)

    def time_up(self, entry_bar: int, i: int) -> bool:
        if self.rule.time_exit and i - entry_bar + 1 >= self.rule.time_exit:
            self.timed.add(entry_bar)
            return True
        return False

    def new_stop(self, i: int, direction: int, entry_bar: int, entry: int, target_ticks: int, stop: int):
        """The tightened stop (ticks) at bar i's close, or None."""
        r, b, d = self.rule, self.bars, direction
        hi, lo, c = int(b.h[i]), int(b.l[i]), int(b.c[i])
        px = hi if d == LONG else lo
        if entry_bar != self.entry_bar:
            self.entry_bar, self.best, self.best_close = entry_bar, px, c
        else:
            self.best = max(self.best, px) if d == LONG else min(self.best, px)
            self.best_close = max(self.best_close, c) if d == LONG else min(self.best_close, c)
        if r.be == "none" and r.trail == "none":
            return None
        fav = (self.best - entry) * d
        cfav = (c - entry) * d
        T = target_ticks
        lv = []
        be_lvl = entry + d * r.be_offset
        if ((r.be == "touch" and fav >= rnd(r.be_x * T)) or (r.be == "close" and cfav >= rnd(r.be_x * T))
                or (r.be == "time" and i - entry_bar + 1 >= r.be_x and cfav > r.be_offset)):
            lv.append(be_lvl)
        if r.trail != "none" and fav >= rnd(r.trail_at * T):
            x = self._trail(i, d, entry, T, fav, c)
            if x is not None:
                lv.append(x)
        if not lv:
            return None
        lvl = max(lv) if d == LONG else min(lv)
        if (lvl - stop) * d > 0:
            self.moved.add(entry_bar)
            return lvl
        return None

    def _trail(self, i, d, entry, T, fav, c):
        r, t = self.rule, self.rule.trail
        if t == "frac":
            return self.best - d * max(1, rnd(r.trail_x * T))
        if t == "close":
            return self.best_close - d * max(1, rnd(r.trail_x * T))
        if t == "step":
            s = max(1, rnd(r.trail_x * T))
            m = fav // s
            return entry + d * (m - 1) * s if m >= 1 else None
        if t == "atr":
            a = self.ind["atr"][i]
            return _toward(self.best - d * r.trail_x * a, d) if a == a else None
        if t == "swing":
            p = self.ind["pl" if d == LONG else "ph"][i]
            return int(p) if p == p else None
        x = self.ind[t][i]  # ema / sar: only while on the trade's side of the close
        if x != x or (x - c) * d >= 0:
            return None
        return _toward(x, d)


# --- exit study grid (python -m tvtester.cli exits <name>), declared 2026-11-01 before the v2 runs --------
COMBINED_BE = (("touch", 0.5, 1), ("close", 0.5, 1), ("time", 30, 1))


def _be_rules() -> list[ExitRule]:
    out = [ExitRule(be="touch", be_x=a, be_offset=o) for a in (0.25, 0.5, 0.75) for o in (0, 1, 2)]
    out += [ExitRule(be="close", be_x=a, be_offset=o) for a in (0.25, 0.5, 0.75) for o in (0, 1)]
    out += [ExitRule(be="time", be_x=n, be_offset=o) for n in (15, 30, 60) for o in (0, 1)]
    return out


def _trail_specs() -> list[dict]:
    keep = (True, False)
    out = [dict(trail="frac", trail_at=a, trail_x=x, keep_target=k)
           for a in (0.0, 0.25, 0.5, 0.75) for x in (0.25, 0.5, 0.75, 1.0) for k in keep]
    out += [dict(trail="atr", trail_at=a, trail_x=x, keep_target=k) for x in (1, 2, 3, 4) for a in (0.0, 0.5)
            for k in keep]
    out += [dict(trail="swing", trail_at=a, trail_x=x, keep_target=k) for x in (2, 3, 5) for a in (0.0, 0.5)
            for k in keep]
    out += [dict(trail="step", trail_x=x, keep_target=k) for x in (0.25, 0.5) for k in keep]
    out += [dict(trail="close", trail_at=a, trail_x=x, keep_target=k) for x in (0.25, 0.5, 0.75, 1.0)
            for a in (0.0, 0.5) for k in keep]
    out += [dict(trail="ema", trail_at=a, trail_x=x, keep_target=k) for x in (9, 20, 50) for a in (0.0, 0.5)
            for k in keep]
    out += [dict(trail="sar", trail_at=a, trail_x=x, keep_target=k) for x in (0, 1) for a in (0.0, 0.5)
            for k in keep]
    return out


def study_rules() -> list[ExitRule]:
    """Fixed order: baseline, breakeven (21), trailing (100), both (300 = 100 trails x 3 declared breakevens),
    time exit (6) = 428 rules."""
    trails = _trail_specs()
    out = [ExitRule()]
    out += _be_rules()
    out += [ExitRule(**t) for t in trails]
    out += [ExitRule(be=s, be_x=x, be_offset=o, **t) for s, x, o in COMBINED_BE for t in trails]
    out += [ExitRule(time_exit=n, keep_target=k) for n in (15, 30, 60) for k in (True, False)]
    return out
