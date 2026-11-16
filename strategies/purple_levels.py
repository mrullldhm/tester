"""purple_pa mechanics on more levels fixed at the day's open. Hypothesis: docs/strategies/purple_levels/README.md."""

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.indicators import in_session, tf_candles, tf_minutes
from cltester.strategy import Base
from cltester.swings import swing_state
from strategies.purple_pa import previous_day_levels, side_changed

FAMILIES = ("pd", "pw", "sw4h", "sw1d", "all", "sw", "nopd")
UNIONS = {"all": ("pd", "pw", "sw4h", "sw1d"), "sw": ("sw4h", "sw1d"), "nopd": ("pw", "sw4h", "sw1d")}


def previous_week_levels(df: pd.DataFrame, days: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per trading day: (has a previous week, its high, its low) in ticks, from raw 1m bars. Weeks are Monday-Friday
    trading days (Sunday evening belongs to Monday), as cltester.swings 1w."""
    tday = pd.DatetimeIndex(df["trading_day"])
    wk = ((tday.as_unit("ns").asi8 // 86_400_000_000_000) + 3) // 7
    raw = pd.DataFrame({"wk": wk, "hi": df["high"].to_numpy(), "lo": df["low"].to_numpy()}).groupby("wk").agg(
        hi=("hi", "max"), lo=("lo", "min"))
    dwk = ((pd.DatetimeIndex(days).as_unit("ns").asi8 // 86_400_000_000_000) + 3) // 7
    pos = raw.index.searchsorted(dwk)  # this week's row; the previous row is the previous traded week
    ok = pos > 1  # the first loaded week can start mid-week, so it is never used as a complete previous week
    prev = np.maximum(pos - 1, 0)
    hi = np.where(ok, np.round(raw["hi"].to_numpy()[prev] / TICK), 0).astype(np.int64)
    lo = np.where(ok, np.round(raw["lo"].to_numpy()[prev] / TICK), 0).astype(np.int64)
    return ok, hi, lo


class Strategy(Base):
    NAME = "purple_levels"
    ABOUT = "purple_pa on previous-day, previous-week, 4h and daily swing levels fixed at the day's open."
    PARAMS = {"levels": "pd", "tf": "15m", "confirm": 4, "rr": 1.0, "expire_candles": 4}
    GRID = {"levels": list(FAMILIES), "tf": ["15m", "5m"]}
    DEPENDS = ("purple_pa",)

    @staticmethod
    def day_levels(df: pd.DataFrame, cd: pd.DataFrame, days: np.ndarray, day_id: np.ndarray, starts: np.ndarray,
                   family: str) -> list[list[int]]:
        """Per trading day (index into days): the level prices in ticks, fixed at the day's open."""
        out: list[list[int]] = [[] for _ in days]
        fams = UNIONS.get(family, (family,))
        first = cd["first"].to_numpy()
        for fam in fams:
            if fam in ("pd", "pw"):
                ok, hi, lo = (previous_day_levels if fam == "pd" else previous_week_levels)(df, days)
                for d in range(len(days)):
                    if ok[d]:
                        out[d] += [int(hi[d]), int(lo[d])]
            else:
                tf = fam[2:]
                st = swing_state(df, tf)
                for a in starts:
                    d_at = first[a] - 1  # the 1m bar before the day's first candle
                    if d_at < 0:
                        continue
                    d = day_id[a]
                    for k in ("sh", "sl"):
                        v = st[f"{tf}_{k}"].iloc[d_at]
                        if not np.isnan(v):
                            out[d].append(int(round(v / TICK)))
        if family in UNIONS:  # equal prices count once, first family order kept
            out = [list(dict.fromkeys(x)) for x in out]
        return out

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        if p["levels"] not in FAMILIES:
            raise ValueError(f"levels {p['levels']} not in {FAMILIES}")
        cols = ["side", "limit", "stop", "target", "expire_min"]
        n = len(df)
        cd = tf_candles(df, p["tf"])
        av = cd["avail"].to_numpy()
        ok = av < n
        cd, av = cd[ok].reset_index(drop=True), av[ok]
        if len(cd) == 0:  # warm-up: no candle complete yet
            return pd.DataFrame(columns=cols, index=pd.Index([], dtype=int))
        h, l = (np.round(cd[k].to_numpy() / TICK).astype(np.int64) for k in ("high", "low"))  # noqa: E741
        o = np.round(cd["open"].to_numpy() / TICK).astype(np.int64)
        live = in_session(df, cd)
        sym1 = pd.factorize(df["raw_symbol"])[0]
        sym = sym1[cd["first"].to_numpy()]  # contract of each candle's first bar
        days, day_id = np.unique(cd["day"].to_numpy(), return_inverse=True)
        starts = np.flatnonzero(np.r_[True, day_id[1:] != day_id[:-1]])
        ends = np.r_[starts[1:], len(cd)]
        levels = self.day_levels(df, cd, days, day_id, starts, p["levels"])
        rows, idx = [], []
        for a, b in zip(starts, ends, strict=True):  # purple_pa's loop, levels from the family
            for lev in levels[day_id[a]]:
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
                    sd = side
                    for q in range(t + 1, min(t + 1 + p["confirm"], b)):
                        if q - 2 < max(t - 1, a):
                            continue
                        # the setup (touch through the signal bar) must stay on one contract, else it is over;
                        # a gap candidate reading a candle from before a roll is skipped, not the whole setup
                        if len(set(sym[t:q + 1])) != 1 or sym1[av[q]] != sym[t]:
                            break
                        if len(set(sym[q - 2:q + 1])) != 1:
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
        out = pd.DataFrame(rows, columns=cols, index=pd.Index(idx, dtype=int))
        out = out[~out.index.duplicated(keep="first")]  # two levels on one candle: keep the first found
        return out.sort_index()
