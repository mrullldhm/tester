"""Owner swing point rule (mandatory for every strategy that uses swings). Spec: docs/SWINGS.md.

Each candle gives two price events, its high and its low, in the order they printed. Swing points are found on
that event stream:
  R2/R3  candidate low at candle k: low[k-1] >= low[k] and low[k+1] > low[k]  (high: mirror). Known when k+1 closes.
  R1     points alternate: low, high, low, high ...
  R4     a swing low is the lowest price between the swing highs around it (every candle counts, also the swing
         high candles' own lows when they printed inside the transition); high: mirror.
  R5     a second low with no high between replaces the first if lower or equal (equal: the later one wins),
         otherwise it is dropped; high: mirror.
Event order inside a candle: from its 1-minute bars (higher timeframes). When unknown (a 1m candle, or both
extremes in the same 1m bar), continue the order: after a swing high the low comes first, after a swing low the
high. Owner example: after a swing high, the candle holding the lowest low becomes swing low, then swing high,
when the candle after it has a higher low and a lower high.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import TICK
from .data import add_session, to_ticks

HIGH, LOW = 1, -1
UNKNOWN = -1
SESSION_LAST_MINUTE = 1379  # 15:59 CT, minutes since the 17:00 CT open: the last minute of a CME trading day
UNDO_DEPTH = 64  # points an outside-candle trial may rewrite; a deeper cascade raises
TIMEFRAMES = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "4h": 240, "1d": 1440}


@dataclass
class Candles:
    ts: pd.DatetimeIndex  # candle open (UTC)
    o: np.ndarray  # ticks
    h: np.ndarray
    l: np.ndarray  # noqa: E741
    c: np.ndarray
    high_first: np.ndarray  # 1 high printed first, 0 low first, -1 unknown
    avail: np.ndarray  # 1m bar index at whose close the candle is complete
    first: np.ndarray  # 1m bar index of the candle's first bar
    last: np.ndarray  # 1m bar index of the candle's last bar (avail can be later when its last minute is missing)

    def __len__(self) -> int:
        return len(self.o)


def build_candles(df: pd.DataFrame, tf: str) -> Candles:
    """Candles from 1m bars. 5m-1h: clock aligned. 4h: blocks from the 17:00 CT session open. 1d: trading day.
    A candle is complete at the close of its last minute (the 15:59 CT bar for the day's last 4h block and the daily
    candle); when that minute has no bar (early closes, quiet minutes), at the close of the next bar."""
    if tf not in TIMEFRAMES:
        raise ValueError(f"timeframe {tf} not in {list(TIMEFRAMES)}")
    if "sess_minute" not in df:
        df = add_session(df)
    n = len(df)
    o, h, l, c = (to_ticks(df[k]) for k in ("open", "high", "low", "close"))
    if n == 0:
        none = np.zeros(0, dtype=np.int64)
        return Candles(pd.DatetimeIndex([], tz="UTC"), none, none, none, none, none, none, none, none)
    if tf == "1m":
        idx = np.arange(n)
        return Candles(pd.DatetimeIndex(df["ts"]), o, h, l, c, np.full(n, UNKNOWN), idx, idx, idx)
    minutes = TIMEFRAMES[tf]
    sess = df["sess_minute"].to_numpy()
    day = pd.factorize(df["trading_day"])[0].astype(np.int64)
    day_close = sess == SESSION_LAST_MINUTE
    if tf == "1d":
        gid, last_minute = day, day_close
    elif tf == "4h":
        gid, last_minute = day * 10 + sess // 240, ((sess + 1) % 240 == 0) | day_close
    else:
        epoch_min = pd.DatetimeIndex(df["ts"]).as_unit("ns").asi8 // 60_000_000_000
        gid, last_minute = epoch_min // minutes, (epoch_min + 1) % minutes == 0
    start = np.flatnonzero(np.r_[True, gid[1:] != gid[:-1]])
    end = np.r_[start[1:], n] - 1
    hi = np.maximum.reduceat(h, start)
    lo = np.minimum.reduceat(l, start)
    first_hi = np.array([s + int(np.argmax(h[s:e + 1] == v)) for s, e, v in zip(start, end, hi, strict=True)])
    first_lo = np.array([s + int(np.argmax(l[s:e + 1] == v)) for s, e, v in zip(start, end, lo, strict=True)])
    order = np.where(first_hi < first_lo, 1, np.where(first_lo < first_hi, 0, UNKNOWN))
    avail = np.where(last_minute[end], end, end + 1)
    done = avail < n  # the last candle is left out until it is complete: it may still print new prices
    return Candles(pd.DatetimeIndex(df["ts"].to_numpy()[start[done]]), o[start[done]], hi[done], lo[done],
                   c[end[done]], order[done], avail[done], start[done], end[done])


@dataclass
class Point:
    kind: int  # HIGH or LOW
    price: int  # ticks
    candle: int
    event: int  # position in the event stream (2 per candle)


def _extreme_ok(kind: int, price: int, ev_hi: np.ndarray, ev_lo: np.ndarray, a: int, b: int) -> bool:
    """price is the highest high (kind HIGH) / lowest low in events a..b inclusive."""
    if b < a:
        return True
    return bool(price >= ev_hi[a:b + 1].max()) if kind == HIGH else bool(price <= ev_lo[a:b + 1].min())


def _offer(stack: list[Point], q: Point, ev_hi: np.ndarray, ev_lo: np.ndarray) -> None:
    while True:
        if not stack:
            if _extreme_ok(q.kind, q.price, ev_hi, ev_lo, 0, q.event):
                stack.append(q)
            return
        t = stack[-1]
        if t.kind == q.kind:  # R5: same type with no opposite point between
            more = q.price >= t.price if q.kind == HIGH else q.price <= t.price
            if not more:
                return
            stack.pop()
            continue
        if not _extreme_ok(q.kind, q.price, ev_hi, ev_lo, t.event + 1, q.event):
            return  # R4: a more extreme price already printed since t
        prev_event = stack[-2].event + 1 if len(stack) > 1 else 0
        if _extreme_ok(t.kind, t.price, ev_hi, ev_lo, prev_event, q.event - 1):
            stack.append(q)
            return
        stack.pop()  # R4: t is not the extreme of its own transition, so it is not a swing point


def _process(stack: list[Point], cd: Candles, k: int, high_first: int, is_low: bool, is_high: bool,
             ev_hi: np.ndarray, ev_lo: np.ndarray) -> None:
    """Offer candle k's two events in the given order."""
    first, second = (HIGH, LOW) if high_first == 1 else (LOW, HIGH)
    for slot, kind in enumerate((first, second)):
        e = 2 * k + slot
        ev_hi[e], ev_lo[e] = (cd.h[k], np.inf) if kind == HIGH else (-np.inf, cd.l[k])
        if kind == LOW and is_low:
            _offer(stack, Point(LOW, int(cd.l[k]), k, e), ev_hi, ev_lo)
        elif kind == HIGH and is_high:
            _offer(stack, Point(HIGH, int(cd.h[k]), k, e), ev_hi, ev_lo)


def _record(stack: list[Point], state: dict[str, np.ndarray], k: int) -> None:
    """State after candle k: the newest and the previous swing high and swing low in the structure
    (points alternate, so they are the top four of the stack)."""
    state["newest"][k] = stack[-1].kind if stack else 0
    seen = {HIGH: 0, LOW: 0}
    for p in stack[-1:-5:-1]:
        key = ("sh" if p.kind == HIGH else "sl") + ("" if seen[p.kind] == 0 else "2")
        seen[p.kind] += 1
        state[f"{key}_price"][k], state[f"{key}_candle"][k] = p.price, p.candle


def detect(cd: Candles) -> tuple[list[Point], dict[str, np.ndarray]]:
    """Run the rule over all candles. Returns the final swing points and the state as known after each candle's
    processing (candle k is processed when candle k+1 closes): last swing high / low price (ticks) and candle
    (sh, sl) and the ones before them (sh2, sl2), or -1 when none; newest: kind of the newest point (0 when none)."""
    n = len(cd)
    ev_hi = np.full(2 * n, -np.inf)  # high of a high event; -inf on low events
    ev_lo = np.full(2 * n, np.inf)
    stack: list[Point] = []
    state = {f"{key}_{f}": np.full(n, -1, dtype=np.int64) for key in ("sh", "sl", "sh2", "sl2")
             for f in ("price", "candle")}
    state["newest"] = np.zeros(n, dtype=np.int64)
    for k in range(n):
        is_low = 0 < k < n - 1 and cd.l[k - 1] >= cd.l[k] and cd.l[k + 1] > cd.l[k]
        is_high = 0 < k < n - 1 and cd.h[k - 1] <= cd.h[k] and cd.h[k + 1] < cd.h[k]
        high_first = int(cd.high_first[k])
        if high_first == UNKNOWN:
            high_first = 1 if stack and stack[-1].kind == LOW else 0  # continue the order
            if is_low and is_high and stack:
                cut = max(len(stack) - UNDO_DEPTH, 0)
                saved, last = stack[cut:], stack[-1]
                _process(stack, cd, k, high_first, is_low, is_high, ev_hi, ev_lo)
                if len(stack) < cut:
                    raise RuntimeError(f"swing cascade deeper than {UNDO_DEPTH} points at candle {k}")
                if all(p is not last for p in stack[cut:]):  # that order breaks rule 4 for the last point
                    del stack[cut:]
                    stack.extend(saved)
                    high_first = 1 - high_first
                else:
                    _record(stack, state, k)
                    continue
        _process(stack, cd, k, high_first, is_low, is_high, ev_hi, ev_lo)
        _record(stack, state, k)
    return stack, state


def swing_points(df: pd.DataFrame, tf: str = "1m") -> pd.DataFrame:
    """Final swing points over the whole frame (for charts and studies, NOT for signals: later candles can
    replace a point). Columns: kind (SH/SL), price, ts (candle open), known_at (1m bar index)."""
    cd = build_candles(df, tf)
    pts, _ = detect(cd)
    return pd.DataFrame({
        "kind": ["SH" if p.kind == HIGH else "SL" for p in pts],
        "price": [round(p.price * TICK, 2) for p in pts],
        "ts": [cd.ts[p.candle] for p in pts],
        "known_at": [int(cd.avail[p.candle + 1]) for p in pts],
    })


def swing_state(df: pd.DataFrame, tf: str = "1m", prev: bool = False, newest: bool = False) -> pd.DataFrame:
    """Point-in-time swing state for every 1m bar of df: the last swing high and swing low as they were known at
    that bar's close. Safe for signals. NaN until a swing exists, and NaN again when rule 4 removes it. The newest
    point can still be replaced (rule 5). prev=True adds the swing high and low before them ({tf}_sh2, {tf}_sl2).
    newest=True adds {tf}_newest: 1 when the newest point is the swing high, -1 the swing low, 0 none. It settles
    which came last when one candle is both (same _ts)."""
    cols = ("sh", "sl", "sh2", "sl2") if prev else ("sh", "sl")
    cd = build_candles(df, tf)
    n = len(df)
    out = pd.DataFrame(index=df.index)
    if len(cd) == 0:  # warm-up: no candle is complete yet
        for col in cols:
            out[f"{tf}_{col}"] = np.nan
            out[f"{tf}_{col}_ts"] = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")
        if newest:
            out[f"{tf}_newest"] = 0
        return out
    _, st = detect(cd)
    when = np.full(len(cd), n, dtype=np.int64)  # candle k is processed when candle k+1 is complete
    when[:-1] = cd.avail[1:]
    updated = np.flatnonzero(when < n)
    src = np.full(n, -1, dtype=np.int64)
    src[when[updated]] = updated  # several candles on one bar: the last one wins
    src = np.maximum.accumulate(src)  # each bar shows the newest full snapshot, never a mix of old and new
    known = src >= 0
    for col in cols:
        candle = np.where(known, st[f"{col}_candle"][np.maximum(src, 0)], -1)
        ok = candle >= 0
        price = np.where(ok, st[f"{col}_price"][np.maximum(src, 0)] * TICK, np.nan)
        out[f"{tf}_{col}"] = np.round(price, 2)
        ts = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")
        ts.iloc[np.flatnonzero(ok)] = cd.ts[candle[ok]]
        out[f"{tf}_{col}_ts"] = ts
    if newest:
        out[f"{tf}_newest"] = np.where(known, st["newest"][np.maximum(src, 0)], 0)
    return out
