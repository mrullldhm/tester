"""Owner swing point rule (mandatory for every strategy that uses swings). Spec: docs/SWINGS.md.

Each candle gives two price events, its high and its low, in the order they printed. Swing points are found on
that event stream:
  R2/R3  candidate low at candle k: low[k-1] >= low[k] and low[k+1] > low[k]  (high: mirror). Known when k+1 closes.
  R1     points alternate: low, high, low, high ...
  R4     a swing low is the lowest price between the swing highs around it (every candle counts, also the swing
         high candles' own lows when they printed inside the transition); high: mirror.
  R5     a second low with no high between replaces the first if lower or equal (equal: the later one wins),
         otherwise it is dropped; high: mirror.
  Touch  a later touch removes the newest point when it follows an opposite point on the same candle.
Event order inside a candle: from its 1-minute bars (higher timeframes). When unknown (a 1m candle, or both
extremes in the same 1m bar), continue the order: after a swing high the low comes first, after a swing low the
high. Owner example: after a swing high, the candle holding the lowest low becomes swing low, then swing high,
when the candle after it has a higher low and a lower high.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import TICK
from .data import add_session, to_ticks

HIGH, LOW = 1, -1
UNKNOWN = -1
SESSION_LAST_MINUTE = 1379  # 15:59 CT, minutes since the 17:00 CT open: the last minute of a CME trading day
# 1w, 1mo: trading-day groups (minutes are nominal); "1mo", never "1M", so it cannot be misread as 1m
TIMEFRAMES = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "4h": 240, "1d": 1440, "1w": 7200, "1mo": 30000}


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
    minute_highs: np.ndarray | None = None  # includes any unfinished higher-timeframe candle
    minute_lows: np.ndarray | None = None

    def __len__(self) -> int:
        return len(self.o)

    def mirrored(self) -> "Candles":
        """Negate prices, exchanging highs and lows and their order."""
        high_first = np.where(self.high_first == UNKNOWN, UNKNOWN, 1 - self.high_first)
        minute_highs = None if self.minute_lows is None else -self.minute_lows
        minute_lows = None if self.minute_highs is None else -self.minute_highs
        return Candles(self.ts, -self.o, -self.l, -self.h, -self.c, high_first, self.avail, self.first, self.last,
                       minute_highs, minute_lows)


def build_candles(df: pd.DataFrame, tf: str) -> Candles:
    """Candles from 1m bars. 5m-1h: clock aligned. 4h: blocks from the 17:00 CT session open. 1d: trading day.
    1w: trading days Monday-Friday. 1mo: trading days of one calendar month.
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
        return Candles(pd.DatetimeIndex(df["ts"]), o, h, l, c, np.full(n, UNKNOWN), idx, idx, idx, h, l)
    minutes = TIMEFRAMES[tf]
    sess = df["sess_minute"].to_numpy()
    day = pd.factorize(df["trading_day"])[0].astype(np.int64)
    day_close = sess == SESSION_LAST_MINUTE
    if tf == "1d":
        gid, last_minute = day, day_close
    elif tf in ("1w", "1mo"):
        tday = pd.DatetimeIndex(df["trading_day"])
        if tf == "1w":  # Monday-to-Friday trading days (Sunday evening belongs to Monday)
            gid = ((tday.as_unit("ns").asi8 // 86_400_000_000_000) + 3) // 7  # 1970-01-01 was a Thursday
        else:
            gid = (tday.year * 12 + tday.month).to_numpy()
        gid = np.asarray(gid, dtype=np.int64)
        # complete at 15:59 CT of the scheduled last day (Friday / last weekday of the month), from the bar's own
        # date only, so a live prefix agrees with full history. A holiday on that day: complete at the next bar.
        if tf == "1w":
            sched = tday.day_of_week == 4
        else:
            sched = tday == tday + pd.offsets.BMonthEnd(0)
        last_minute = day_close & np.asarray(sched)
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
                   c[end[done]], order[done], avail[done], start[done], end[done], h, l)


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


def _offer(stack: list[Point], q: Point, ev_hi: np.ndarray, ev_lo: np.ndarray,
           prior_removals: list[tuple[Point, bool]] | None) -> None:
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
            if prior_removals is not None and t.candle < q.candle:
                prior_removals.append((t, False))
            continue
        if not _extreme_ok(q.kind, q.price, ev_hi, ev_lo, t.event + 1, q.event):
            return  # R4: a more extreme price already printed since t
        prev_event = stack[-2].event + 1 if len(stack) > 1 else 0
        if _extreme_ok(t.kind, t.price, ev_hi, ev_lo, prev_event, q.event - 1):
            stack.append(q)
            return
        stack.pop()  # R4: t is not the extreme of its own transition, so it is not a swing point
        if prior_removals is not None and t.candle < q.candle:
            prior_removals.append((t, True))


def _process(stack: list[Point], cd: Candles, k: int, high_first: int, is_low: bool, is_high: bool,
             ev_hi: np.ndarray, ev_lo: np.ndarray, prior_removals: list[tuple[Point, bool]] | None = None) -> None:
    """Offer candle k's two events in the given order."""
    first, second = (HIGH, LOW) if high_first == 1 else (LOW, HIGH)
    for slot, kind in enumerate((first, second)):
        e = 2 * k + slot
        ev_hi[e], ev_lo[e] = (cd.h[k], np.inf) if kind == HIGH else (-np.inf, cd.l[k])
        if kind == LOW and is_low:
            _offer(stack, Point(LOW, int(cd.l[k]), k, e), ev_hi, ev_lo, prior_removals)
        elif kind == HIGH and is_high:
            _offer(stack, Point(HIGH, int(cd.h[k]), k, e), ev_hi, ev_lo, prior_removals)


def _record(stack: list[Point], state: dict[str, np.ndarray], k: int) -> None:
    """State after candle k: the newest and the previous swing high and swing low in the structure
    (points alternate, so they are the top four of the stack)."""
    state["newest"][k] = stack[-1].kind if stack else 0
    seen = {HIGH: 0, LOW: 0}
    for p in stack[-1:-5:-1]:
        key = ("sh" if p.kind == HIGH else "sl") + ("" if seen[p.kind] == 0 else "2")
        seen[p.kind] += 1
        state[f"{key}_price"][k], state[f"{key}_candle"][k] = p.price, p.candle


def _empty_state(n: int) -> dict[str, np.ndarray]:
    state = {f"{key}_{f}": np.full(n, -1, dtype=np.int64) for key in ("sh", "sl", "sh2", "sl2")
             for f in ("price", "candle")}
    state["newest"] = np.zeros(n, dtype=np.int64)
    return state


def _touch_bar(cd: Candles, k: int, point: Point) -> int | None:
    """First touch after the last confirmation and up to the next one, if available."""
    start = int(cd.avail[k]) + 1
    highs = point.kind == HIGH
    minutes = cd.minute_highs if highs else cd.minute_lows
    reaches = np.greater_equal if highs else np.less_equal
    if minutes is None:
        extremes = cd.h if highs else cd.l
        if k + 1 < len(cd) and cd.avail[k + 1] >= start and reaches(extremes[k + 1], point.price):
            return int(cd.avail[k + 1])
        return None
    stop = int(cd.avail[k + 1]) + 1 if k + 1 < len(cd) else len(minutes)
    touched = reaches(minutes[start:stop], point.price)
    if touched.any():
        return start + int(touched.argmax())
    return None


def _paired_swing(stack: list[Point]) -> bool:
    return len(stack) >= 2 and stack[-1].candle == stack[-2].candle


def _touch_on_delayed_confirmation(cd: Candles, right: int, point: Point) -> bool:
    """The minute that closes a gap-delayed right candle can already belong to the next candle."""
    if right >= len(cd) or cd.avail[right] == cd.last[right]:
        return False
    minute = cd.avail[right]
    if point.kind == HIGH:
        return cd.minute_highs is not None and bool(cd.minute_highs[minute] >= point.price)
    return cd.minute_lows is not None and bool(cd.minute_lows[minute] <= point.price)


def detect(cd: Candles, observer: Callable[[int, list[Point]], None] | None = None, *,
           on_touch: Callable[[int, int, list[Point]], None] | None = None,
           ) -> tuple[list[Point], dict[str, np.ndarray]]:
    """Run the rule over all candles. Returns the final swing points and the state as known after each candle's
    processing (candle k is processed when candle k+1 closes): last swing high / low price (ticks) and candle
    (sh, sl) and the ones before them (sh2, sl2), or -1 when none; newest: kind of the newest point (0 when none).
    observer(k, stack), optional, is called after candle k is processed with the live structure (read only): it
    sees the resulting points, including changes from deep rule-4 cascades. on_touch(k, minute, stack) receives
    the read-only structure immediately after a touch removal before processing candle k."""
    n = len(cd)
    ev_hi = np.full(2 * n, -np.inf)  # high of a high event; -inf on low events
    ev_lo = np.full(2 * n, np.inf)
    stack: list[Point] = []
    state = _empty_state(n)
    for k in range(n):
        if _paired_swing(stack):
            touched_at = _touch_bar(cd, k, stack[-1])
            if touched_at is not None:
                stack.pop()
                if on_touch is not None:
                    on_touch(k, touched_at, stack)
        is_low = 0 < k < n - 1 and cd.l[k - 1] >= cd.l[k] and cd.l[k + 1] > cd.l[k]
        is_high = 0 < k < n - 1 and cd.h[k - 1] <= cd.h[k] and cd.h[k + 1] < cd.h[k]
        order_known = cd.high_first[k] != UNKNOWN
        high_first = int(cd.high_first[k]) if order_known else int(bool(stack and stack[-1].kind == LOW))
        if not order_known and is_low and is_high and stack:
            prior_removals: list[tuple[Point, bool]] = []  # prior point and whether rule 4 removed it
            _process(stack, cd, k, high_first, is_low, is_high, ev_hi, ev_lo, prior_removals)
            if prior_removals and prior_removals[0][1]:
                while stack and stack[-1].candle == k:
                    stack.pop()
                stack.extend(point for point, _ in reversed(prior_removals))
                _process(stack, cd, k, 1 - high_first, is_low, is_high, ev_hi, ev_lo)
        else:
            _process(stack, cd, k, high_first, is_low, is_high, ev_hi, ev_lo)
        if _paired_swing(stack) and _touch_on_delayed_confirmation(cd, k + 1, stack[-1]):
            stack.pop()
        _record(stack, state, k)
        if observer is not None:
            observer(k, stack)
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
    that bar's close. Missing swings are NaN. A touch can remove the newest paired swing before its timeframe candle
    closes. prev=True adds the swing high and low before the latest ones ({tf}_sh2, {tf}_sl2).
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
    touches: list[tuple[int, int, list[Point]]] = []

    def remember_touch(k: int, minute: int, stack: list[Point]) -> None:
        touches.append((k, minute, stack[-4:]))

    _, st = detect(cd, on_touch=remember_touch)
    when = np.full(len(cd), n, dtype=np.int64)  # candle k is processed when candle k+1 is complete
    when[:-1] = cd.avail[1:]
    updated = np.flatnonzero(when < n)
    src = np.full(n, -1, dtype=np.int64)
    src[when[updated]] = updated  # several candles on one bar: the last one wins
    src = np.maximum.accumulate(src)  # each bar shows the newest full snapshot, never a mix of old and new
    if touches:
        touched_state = _empty_state(len(touches))
        for i, (k, minute, stack) in enumerate(touches):
            _record(stack, touched_state, i)
            src[minute:when[k]] = len(cd) + i
        st = {key: np.concatenate((values, touched_state[key])) for key, values in st.items()}
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
