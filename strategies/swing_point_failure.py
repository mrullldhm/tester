"""Swing Point Failure (owner model). Spec and trial budget: docs/strategies/swing_point_failure/README.md.

Short: the newest swing-timeframe point is a swing low and price comes back to it before any swing high is
confirmed (the low failed). Wait for the first 1m/5m pullback with a confirmed higher low, then sell when a candle
of that timeframe breaks the newest higher low. Long is the mirror.

Both sides run through one scan written for shorts: long inputs are negated ("side space"), so a swing high becomes
a swing low, a lower high a higher low, and the result is negated back.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.data import to_ticks
from cltester.strategy import Base
from cltester.swings import TIMEFRAMES, Candles, build_candles, swing_state

LTFS = ("1m", "5m")  # pullback (execution) timeframe candidates
NO_EXPIRY = 100_000  # bars; the engine still cancels at the day change, contract change and 3:10 PM CT
MIN_NS = 60_000_000_000


@dataclass
class Ltf:
    """One pullback timeframe in side space, per 1m bar (state as known at that bar's close)."""

    name: str
    sl: np.ndarray  # newest swing low (ticks, NaN = none)
    sl2: np.ndarray  # the swing low before it
    sl_ts: np.ndarray  # newest swing low candle open (ns)
    start: np.ndarray  # open (ns) of this timeframe's candle that holds the bar
    done_lo: np.ndarray  # low of the candle that completes at this bar's close, NaN if none


@dataclass
class Side:
    """Swing-timeframe inputs and 1m prices in side space (shorts as is, longs negated)."""

    lo: np.ndarray
    hi: np.ndarray
    cl: np.ndarray
    lvl: np.ndarray  # newest swing low price (ticks)
    lvl_id: np.ndarray  # its candle open (ns): the setup identity
    armed: np.ndarray  # the newest point is that swing low (no swing high confirmed after it)
    opp_id: np.ndarray  # newest swing high candle open (ns)
    inval: np.ndarray  # high of the swing-timeframe candle before the one holding the bar
    ltfs: list


def _ns(s: pd.Series) -> np.ndarray:
    """Timestamps as int64 ns; NaT becomes the smallest int64, so it compares below every real time."""
    return pd.DatetimeIndex(s).as_unit("ns").asi8


def _first_touches(sd: Side) -> np.ndarray:
    """First 1m bar per swing low whose low reaches it while armed (state known at the previous close)."""
    n = len(sd.lo)
    if n < 2:
        return np.zeros(0, dtype=np.int64)
    touch = np.flatnonzero(sd.armed[:-1] & (sd.lo[1:] <= sd.lvl[:-1])) + 1
    _, first = np.unique(sd.lvl_id[touch - 1], return_index=True)
    return np.sort(touch[first])


def _completed_extremes(cd: Candles, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Per 1m bar: lowest low and highest high of the candles that complete at its close (NaN if none).
    Two candles can complete on one bar when the first one misses its last minute."""
    lows, highs = np.full(n, np.inf), np.full(n, -np.inf)
    np.minimum.at(lows, cd.avail, cd.l)
    np.maximum.at(highs, cd.avail, cd.h)
    return np.where(np.isinf(lows), np.nan, lows), np.where(np.isinf(highs), np.nan, highs)


def scan(sd: Side, ts: np.ndarray, day: np.ndarray, risk: int, rr: float, tie: str) -> list[dict]:
    """Every setup in side space, one dict each. Setups of different swing lows never overlap: a setup ends as soon
    as its low is no longer the newest point, and the next low's first touch comes after that."""
    n = len(sd.lo)
    out = []
    for t0 in _first_touches(sd):
        sid, inval = sd.lvl_id[t0 - 1], sd.inval[t0]
        rec = {"touch": int(t0), "level": sd.lvl[t0 - 1], "inval": inval, "tf": None, "hl": np.nan,
               "end": None, "why": "data end", "limit": np.nan, "stop": np.nan, "target": np.nan, "expire": np.nan}
        if np.isnan(inval):
            rec.update(end=int(t0), why="no previous candle")
            out.append(rec)
            continue
        k = None  # locked pullback timeframe
        level, hl_ts = np.nan, 0
        for t in range(t0 + 1, n):
            if sd.hi[t] >= inval:
                rec.update(end=t, why="invalidation level")
                break
            if not sd.armed[t] or sd.lvl_id[t] != sid:
                rec.update(end=t, why="swing low replaced or swing high")
                break
            if k is None:
                hits = [f for f in sd.ltfs if f.sl[t] > f.sl2[t] and f.sl_ts[t] >= f.start[t0]]
                if hits:
                    k = hits[0] if len(hits) == 1 else next(f for f in hits if f.name == tie)
                    level, hl_ts = k.sl[t], k.sl_ts[t]
                    rec.update(tf=k.name)
                continue
            if k.sl[t] > k.sl2[t] and k.sl_ts[t] >= k.start[t0]:
                level, hl_ts = k.sl[t], k.sl_ts[t]  # trail to the newest higher low
            if k.done_lo[t] <= level:
                rec.update(end=t, why="trigger", hl=level)
                step = TIMEFRAMES[k.name] * MIN_NS
                # hl_ts is the HL candle's first traded minute; the clock-aligned boundary is the next candle's open
                a = int(np.searchsorted(ts, hl_ts // step * step + step))
                close, stop = sd.cl[t], sd.hi[a:t + 1].max()
                if stop <= close:
                    rec["why"] = "no risk (stop at the close)"
                    break
                limit = close if stop - close <= risk else stop - risk
                expire = NO_EXPIRY
                for u in range(t + 1, n):
                    if day[u] != day[t]:
                        break
                    if sd.opp_id[u] > sid:  # a swing high after the failed low is confirmed: cancel
                        expire = u - t
                        break
                rec.update(limit=limit, stop=stop, target=limit - rr * risk, expire=expire)
                break
        out.append(rec)
    return out


class Strategy(Base):
    NAME = "swing_point_failure"
    ABOUT = ("Owner model: a swing low (high) retested before the next swing high (low) is confirmed; enter at the "
             "break of the first 1m/5m pullback's higher (lower) low. Stop = pullback swing, max risk ticks, 2R.")
    PARAMS = {"swing_tf": "1h", "risk": 25, "rr": 2, "tie": "5m"}
    GRID = {"swing_tf": ["1h", "4h"], "risk": [25, 20, 15], "tie": ["5m", "1m"]}
    OVERLAP = True  # owner: a new setup cancels an unfilled order; a filled trade keeps running

    def _sides(self, df: pd.DataFrame, p: dict) -> dict[int, Side]:
        n = len(df)
        lo, hi, cl = (to_ticks(df[k]).astype(float) for k in ("low", "high", "close"))
        ts = _ns(df["ts"])
        sw = swing_state(df, p["swing_tf"], newest=True)
        newest = sw[f"{p['swing_tf']}_newest"].to_numpy()
        sh, sl = (np.round(sw[f"{p['swing_tf']}_{k}"].to_numpy(float) / TICK) for k in ("sh", "sl"))
        sh_id, sl_id = _ns(sw[f"{p['swing_tf']}_sh_ts"]), _ns(sw[f"{p['swing_tf']}_sl_ts"])
        cd = build_candles(df, p["swing_tf"])
        p_hi, p_lo = np.full(n, np.nan), np.full(n, np.nan)
        if len(cd):
            bar = np.arange(n)
            c = np.searchsorted(cd.first, bar, side="right") - 1
            inside = (c >= 0) & (bar <= cd.last[np.maximum(c, 0)])
            prev = np.where(inside, c - 1, c)  # the last bars of the data sit in an unfinished candle
            ok = prev >= 0
            p_hi = np.where(ok, cd.h[np.maximum(prev, 0)], np.nan)
            p_lo = np.where(ok, cd.l[np.maximum(prev, 0)], np.nan)
        short_ltfs, long_ltfs = [], []
        for name in LTFS:
            s = swing_state(df, name, prev=True)
            low1, low2, high1, high2 = (np.round(s[f"{name}_{k}"].to_numpy(float) / TICK)
                                        for k in ("sl", "sl2", "sh", "sh2"))
            step = TIMEFRAMES[name] * MIN_NS
            start = ts // step * step
            if name == "1m":
                done_lo, done_hi = lo, hi
            else:
                done_lo, done_hi = _completed_extremes(build_candles(df, name), n)
            short_ltfs.append(Ltf(name, low1, low2, _ns(s[f"{name}_sl_ts"]), start, done_lo))
            long_ltfs.append(Ltf(name, -high1, -high2, _ns(s[f"{name}_sh_ts"]), start, -done_hi))
        short = Side(lo, hi, cl, sl, sl_id, newest == -1, sh_id, p_hi, short_ltfs)
        long = Side(-hi, -lo, -cl, -sh, sh_id, newest == 1, sl_id, -p_lo, long_ltfs)
        return {-1: short, 1: long}

    def setups(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        """Every setup with how it ended (trigger or not), real prices. For spot checks."""
        if p["tie"] not in LTFS:
            raise ValueError(f"tie must be one of {LTFS}")
        cols = ["side", "touch", "level", "inval", "tf", "hl", "end", "why", "limit", "stop", "target", "expire"]
        if len(df) < 2:
            return pd.DataFrame(columns=cols)
        ts = _ns(df["ts"])
        day = pd.factorize(df["trading_day"])[0]
        rows = []
        for side, sd in self._sides(df, p).items():
            for r in scan(sd, ts, day, int(p["risk"]), float(p["rr"]), p["tie"]):
                for key in ("level", "inval", "hl", "limit", "stop", "target"):
                    if not np.isnan(r[key]):
                        r[key] = round(-side * r[key] * TICK, 2)  # side space back to $ (shorts: side -1)
                rows.append({"side": side, **r})
        out = pd.DataFrame(rows, columns=cols)
        return out.sort_values("touch", kind="stable").reset_index(drop=True)

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        s = self.setups(df, p)
        s = s[s["limit"].notna()]
        sig = pd.DataFrame({"side": s["side"].astype(int).to_numpy(), "limit": s["limit"].to_numpy(float),
                            "stop": s["stop"].to_numpy(float), "target": s["target"].to_numpy(float),
                            "expire": s["expire"].astype(int).to_numpy()}, index=s["end"].astype(int).to_numpy())
        if not sig.index.is_unique:
            raise RuntimeError("two setups triggered on one bar; short and long setups should never overlap")
        return sig.sort_index()
