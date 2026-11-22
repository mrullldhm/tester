"""Historical Tupa 1 occurrences, using the owner's point-in-time swing state."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from cltester.data import to_ticks
from cltester.swings import HIGH, LOW, Candles, ProvisionalSwings


@dataclass(frozen=True)
class Setup:
    side: int
    c1: int
    c2: int
    c3: int
    reference: int
    reference_level: int
    catalyst: int
    catalyst_swing: pd.Timestamp
    catalyst_swing_price: int
    first_touch: int
    second_touch: int
    retest: int
    confirmation: int
    early_sweep: int | None
    inside: bool
    crosses_roll: bool


def ordered_sweep(candles: Candles, opens: np.ndarray, k: int, *, high_first: bool = False):
    prior_low, prior_high = candles.l[k - 1], candles.h[k - 1]
    if candles.l[k] > prior_low or candles.h[k] < prior_high:
        return None
    start, end = candles.first[k], candles.last[k] + 1
    lo = start + np.argmax(candles.minute_lows[start:end] <= prior_low)
    hi = start + np.argmax(candles.minute_highs[start:end] >= prior_high)
    if hi == lo:
        at_open = (prior_low < prior_high <= opens[hi] if high_first else opens[lo] <= prior_low < prior_high)
        return (hi, lo) if at_open else None
    if high_first:
        return (hi, lo) if hi < lo else None
    return (lo, hi) if lo < hi else None


def scan(df, small: Candles, large: Candles, reference: Candles, small_state, large_state,
         provisional: ProvisionalSwings, swing_kind: int):
    """Yield the first retest per catalyst. A swing low sets up a long, and a swing high sets up a short."""
    symbol = df.raw_symbol.to_numpy()
    rolls = np.cumsum(np.r_[False, symbol[1:] != symbol[:-1]])
    minute_open = swing_kind * to_ticks(df.open)
    if swing_kind == LOW:
        small, large = small.mirrored(), large.mirrored()
    minor_swing = "sl" if swing_kind == HIGH else "sh"
    major_swing = "sh" if swing_kind == HIGH else "sl"
    minor_points = pd.DatetimeIndex(small_state[minor_swing])
    minor_opposite = pd.DatetimeIndex(small_state[major_swing])
    latest = large.ts.get_indexer(pd.DatetimeIndex(large_state[major_swing]))
    opposite_points = pd.DatetimeIndex(large_state[minor_swing])
    active = np.where(large_state["newest"] == swing_kind, latest, -1)
    changes = np.flatnonzero(np.r_[False, active[:-1] != active[1:]])
    reference_levels = reference.h if swing_kind == HIGH else -reference.l

    for c2 in range(1, len(large) - 1):
        c1, c3 = c2 - 1, c2 + 1
        if large.h[c1] > large.h[c2]:
            continue
        closed = large.avail[c3]
        closes_as_swing = closed < len(df) and active[closed] == c2
        ref = np.searchsorted(reference.last, large.first[c1], side="left") - 1
        if ref < 0 or large.c[c1] < reference_levels[ref]:
            continue
        first = large.avail[c2] + 1
        right_start, right_end = large.first[c3], large.last[c3] + 1
        early = []
        for k in range(max(1, np.searchsorted(small.first, right_start)), np.searchsorted(small.first, right_end)):
            sweep = ordered_sweep(small, minute_open, k, high_first=True)
            if sweep is not None and sweep[1] < min(closed, right_end):
                early.append(sweep[1])
        if not closes_as_swing and not early:
            continue
        end, end_is_close = right_end, False
        end_touches_swing = False
        if closes_as_swing:
            change = np.searchsorted(changes, closed, side="right")
            end = changes[change] if change < len(changes) else len(df)
            ending_candle = np.searchsorted(large.avail, end)
            end_is_close = ending_candle < len(large.avail) and end == large.avail[ending_candle]
            if end < len(df):
                end_touches_swing = (
                    opposite_points[end - 1] == large.ts[c2] and large.minute_highs[end] >= large.h[c2]
                )
        lo = np.searchsorted(small.first, large.first[c1])
        hi = np.searchsorted(small.first, large.last[c1], side="right")
        for k in range(max(1, lo), hi):
            sweep = ordered_sweep(small, minute_open, k)
            if sweep is None:
                continue
            first_touch, second_touch = sweep
            if small_state["newest"][second_touch - 1] != -swing_kind:
                continue
            catalyst_swing = minor_points[second_touch - 1]
            catalyst_swing_level = small.l[small.ts.get_loc(catalyst_swing)]
            # In short-normalized prices the opposing swing low must be below the reference high.
            if catalyst_swing_level >= reference_levels[ref]:
                continue
            if (minor_opposite[second_touch - 1] == catalyst_swing
                    and small.minute_lows[second_touch] <= catalyst_swing_level):
                # If this minute also invalidates the swing, the second touch needs known priority.
                open_at_second = minute_open[second_touch]
                if open_at_second < small.h[k - 1] or open_at_second <= catalyst_swing_level:
                    continue
            stop = end
            # A close-only change leaves candle 2 active during the minute. If the minute also
            # touches a paired swing, only a retest already reached at the open has known priority.
            if closes_as_swing and end < len(df) and (
                (end_is_close and not end_touches_swing)
                or (minute_open[end] <= small.l[k] and minute_open[end] < large.h[c2])
            ):
                stop += 1
            hits = np.flatnonzero(small.minute_lows[first:stop] <= small.l[k])
            if not hits.size:
                continue
            retest = first + hits[0]
            confirmation, early_sweep = max(closed, retest), None
            for swept in early:
                ready = max(retest, swept)
                if ready >= min(closed, right_end):
                    break
                right = slice(right_start, ready + 1)
                if large.minute_highs[right].max() >= large.h[c2]:
                    break
                other = int(large.l[c1] >= large.l[c2] and large.minute_lows[right].min() > large.l[c2])
                low, high = (other, 1) if swing_kind == HIGH else (1, other)
                touched = int(provisional.touches[c2] <= ready)
                if provisional.kinds[c2, touched, low, high] == swing_kind:
                    confirmation, early_sweep = ready, swept
                    break
            if early_sweep is None and not closes_as_swing:
                continue
            reference_price = int(swing_kind * reference_levels[ref])
            roll_start = min(large.first[c1], small.first[k - 1])
            yield Setup(-swing_kind, c1, c2, c3, ref, reference_price, k, catalyst_swing,
                        int(swing_kind * catalyst_swing_level), first_touch, second_touch, retest, confirmation,
                        early_sweep, retest <= closed,
                        rolls[confirmation] != rolls[roll_start])
