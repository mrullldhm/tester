"""Purple Trading oil price-action strategy. Hypothesis: docs/strategies/purple_pa/README.md."""

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.indicators import in_session, tf_candles, tf_minutes
from cltester.strategy import Base


class Strategy(Base):
    NAME = "purple_pa"
    ABOUT = "First test of previous-day high/low confirmed by a 3-candle gap; limit at the gap edge, 1R target."
    PARAMS = {"tf": "15m", "confirm": 4, "rr": 1.0, "expire_candles": 4}
    GRID = {"tf": ["15m", "5m"]}

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        n = len(df)
        cd = tf_candles(df, p["tf"])
        av = cd["avail"].to_numpy()
        ok = av < n
        cd, av = cd[ok].reset_index(drop=True), av[ok]
        if len(cd) == 0:  # warm-up: no candle complete yet
            return pd.DataFrame(columns=["side", "limit", "stop", "target", "expire_min"],
                                index=pd.Index([], dtype=int))
        h, l, c = (np.round(cd[k].to_numpy() / TICK).astype(np.int64) for k in ("high", "low", "close"))
        o = np.round(cd["open"].to_numpy() / TICK).astype(np.int64)
        live = in_session(df, cd)
        days, day_id = np.unique(cd["day"].to_numpy(), return_inverse=True)
        prev_ok, dh, dl = previous_day_levels(df, days)
        rows, idx = [], []
        starts = np.flatnonzero(np.r_[True, day_id[1:] != day_id[:-1]])
        ends = np.r_[starts[1:], len(cd)]
        for a, b in zip(starts, ends, strict=True):
            d = day_id[a]
            if not prev_ok[d]:
                continue
            for lev in (dh[d], dl[d]):
                side = 1 if o[a] > lev else -1 if o[a] < lev else 0  # +1 price above the level
                armed, tests, first_side = side != 0, 0, 0
                t = a
                while t < b:
                    if not armed:
                        if l[t] > lev:
                            side, armed = 1, tests == 0 or side_changed(first_side, 1)
                        elif h[t] < lev:
                            side, armed = -1, tests == 0 or side_changed(first_side, -1)
                        t += 1
                        continue
                    touched = (side == 1 and l[t] <= lev) or (side == -1 and h[t] >= lev)
                    if not touched:
                        t += 1
                        continue
                    tests += 1
                    armed = False
                    if tests == 1:
                        first_side = side
                    sd = side  # from above: support, long; from below: resistance, short
                    for q in range(t + 1, min(t + 1 + p["confirm"], b)):
                        if q - 2 < max(t - 1, a):
                            continue
                        gap = (h[q - 2] < l[q]) if sd == 1 else (l[q - 2] > h[q])
                        if not gap:
                            continue
                        entry = l[q] if sd == 1 else h[q]
                        stop = (l[t:q + 1].min() - 1) if sd == 1 else (h[t:q + 1].max() + 1)
                        risk = (entry - stop) * sd
                        if risk >= 1 and live[q]:
                            rows.append((sd, entry * TICK, stop * TICK,
                                         (entry + sd * max(int(round(risk * p["rr"])), 1)) * TICK,
                                         p["expire_candles"] * tf_minutes(p["tf"])))
                            idx.append(av[q])
                        break
                    if tests >= 2:
                        break
                    t += 1
        out = pd.DataFrame(rows, columns=["side", "limit", "stop", "target", "expire_min"], index=idx)
        out = out[~out.index.duplicated(keep="first")]  # both levels on one candle: keep the first found
        return out.sort_index()


def side_changed(first: int, now: int) -> bool:
    """A retest is allowed only after the level broke: price re-armed on the other side of it."""
    return first != 0 and now != first


def previous_day_levels(df: pd.DataFrame, days: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per trading day: (has a previous day, its high, its low) in ticks, from the raw 1m bars. Not from candles:
    a candle whose last minute is missing completes in the next session."""
    raw = df.groupby("trading_day").agg(hi=("high", "max"), lo=("low", "min"))
    pos = raw.index.searchsorted(days)
    ok = pos > 0
    prev = np.maximum(pos - 1, 0)
    hi = np.where(ok, np.round(raw["hi"].to_numpy()[prev] / TICK), 0).astype(np.int64)
    lo = np.where(ok, np.round(raw["lo"].to_numpy()[prev] / TICK), 0).astype(np.int64)
    return ok, hi, lo
