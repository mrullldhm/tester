"""Swing Point Failure Reversal (owner, 2026-11-15).
Spec and trial budget: docs/strategies/swing_point_failure_reversal/README.md.

Long: an SPF short signal's stop is touched (filled or not). At the close of the pullback-timeframe candle holding
the touch, buy limit with the stop at the lowest low since the newest swing high, target 2 x risk. Short is the
mirror, from an SPF long.

Each source is scanned in its own side space (strategies/swing_point_failure.py): an SPF short as is, an SPF long
negated. There the reversal is always a long, and real price = reversal side x side-space price.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.data import to_ticks
from cltester.strategy import Base
from cltester.swings import TIMEFRAMES, build_candles, swing_state
from strategies.swing_point_failure import LTFS, MIN_NS, NO_EXPIRY, _ns
from strategies.swing_point_failure import Strategy as Spf

NEVER = np.iinfo(np.int64).max
# Stop timeframes whose candles are clock aligned (the stop window start uses clock arithmetic). 4h and 1d candles
# follow the 17:00 CT session in cltester.swings, so they are not accepted here.
SL_TFS = ("pullback", "1m", "5m", "15m", "30m", "1h")


@dataclass
class Swing:
    """One timeframe's swing highs in side space, per 1m bar."""

    step: int  # candle length (ns)
    sh_ts: np.ndarray  # newest swing high candle's first traded minute (ns) at this bar's close (int64 min = none)


@dataclass
class Tf:
    """One pullback timeframe in side space, per 1m bar."""

    done: np.ndarray  # 1m bar at whose close the candle holding this bar completes (NEVER: not in the data)
    end: np.ndarray  # last 1m bar of that candle; earlier than done when the candle's last minute is missing
    swing: Swing


@dataclass
class Source:
    """One SPF signal in side space."""

    bar: int  # SPF signal bar
    stop: float  # its stop H (ticks)
    tf: str  # its pullback timeframe
    nxt: int  # the next SPF signal bar (either side), len(bars) if none
    last: int  # last bar of its trading day and contract


def _candle_bars(df: pd.DataFrame, name: str, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Per 1m bar: the bar its candle completes at, and the candle's last bar (NEVER: candle not in the data)."""
    if name == "1m":
        return np.arange(n), np.arange(n)
    cd = build_candles(df, name)
    done, end = np.full(n, NEVER), np.full(n, NEVER)
    size = cd.last - cd.first + 1  # candles are contiguous from bar 0
    done[:size.sum()], end[:size.sum()] = np.repeat(cd.avail, size), np.repeat(cd.last, size)
    return done, end


def scan(hi, lo, cl, ts, src: Source, tfs: dict, risk: int, rr: float, sl: Swing | None = None) -> dict:
    """One source in side space. Returns the setup record; limit is NaN when there is no trade.
    sl: swing timeframe for the stop (sl_tf); None = the source's pullback timeframe."""
    rec = {"src": src.bar, "touch": None, "end": None, "why": "no touch", "ref_ts": None,
           "limit": np.nan, "stop": np.nan, "target": np.nan, "expire": np.nan}
    last = min(src.nxt - 1, src.last)
    hit = np.flatnonzero(hi[src.bar + 1:last + 1] >= src.stop)
    if not len(hit):
        return rec
    u = src.bar + 1 + int(hit[0])
    f = tfs[src.tf]
    c, e = int(f.done[u]), int(f.end[u])  # signal at c; prices from the trigger candle only (through e)
    rec.update(touch=u)
    if c > last:
        rec["why"] = "trigger candle closes after the window"
        return rec
    hb = src.bar
    while hi[hb] != src.stop:  # H is the max of the SPF stop window, which ends at the signal bar
        hb -= 1
        if hb < 0:
            raise RuntimeError(f"SPF stop {src.stop} not found at or before bar {src.bar}")
    g = sl or f.swing
    sh = int(g.sh_ts[c])
    # clock-aligned candle opens: a candle's first minute can be missing
    step = g.step if sh > ts[hb] else f.swing.step
    ref = (sh if sh > ts[hb] else int(ts[hb])) // step * step
    a = int(np.searchsorted(ts, ref + step))
    if a > e:
        rec.update(end=c, ref_ts=ref, why="empty stop window")
        return rec
    stop, close = lo[a:e + 1].min(), cl[e]
    rec.update(end=c, ref_ts=ref, stop=stop)
    if stop >= close:
        rec["why"] = "no risk (stop at the close)"
        return rec
    limit = close if close - stop <= risk else stop + risk
    expire = src.nxt - c if src.nxt < len(hi) else NO_EXPIRY
    rec.update(why="trigger", limit=limit, target=limit + rr * risk, expire=expire)
    return rec


class Strategy(Base):
    NAME = "swing_point_failure_reversal"
    ABOUT = ("Owner: when an SPF short's (long's) stop is touched, buy (sell) limit at the pullback candle close; "
             "stop = lowest low since the newest swing high, max risk ticks, target 2R.")
    PARAMS = {"swing_tf": "1h", "risk": 25, "rr": 2, "tie": "5m", "sl_tf": "pullback"}
    GRID = {"risk": [15, 20, 25]}  # sl_tf 5m and 15m at risk 25: README
    OVERLAP = True
    DEPENDS = ("swing_point_failure",)  # its setups are the sources

    def setups(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        cols = ["side", "src", "touch", "end", "why", "ref_ts", "limit", "stop", "target", "expire"]
        if p["sl_tf"] not in SL_TFS:
            raise ValueError(f"sl_tf must be one of {SL_TFS}")
        n = len(df)
        spf = Spf().setups(df, p)
        spf = spf[spf["limit"].notna()].sort_values("end", kind="stable").reset_index(drop=True)
        if n < 2 or spf.empty:
            return pd.DataFrame(columns=cols)
        lo, hi, cl = (to_ticks(df[k]).astype(float) for k in ("low", "high", "close"))
        ts = _ns(df["ts"])
        day, sym = (pd.factorize(df[k])[0] for k in ("trading_day", "raw_symbol"))
        cut = (day[1:] != day[:-1]) | (sym[1:] != sym[:-1])  # a new trading day or contract starts at i+1
        last = np.r_[np.flatnonzero(cut), n - 1][np.cumsum(np.r_[False, cut])]
        tfs: dict[int, dict[str, Tf]] = {-1: {}, 1: {}}
        for name in LTFS:
            s = swing_state(df, name)
            (done, end), step = _candle_bars(df, name, n), TIMEFRAMES[name] * MIN_NS
            tfs[-1][name] = Tf(done, end, Swing(step, _ns(s[f"{name}_sh_ts"])))  # SPF short: reversal long
            tfs[1][name] = Tf(done, end, Swing(step, _ns(s[f"{name}_sl_ts"])))  # SPF long: reversal short
        sl: dict[int, Swing | None] = {-1: None, 1: None}
        if p["sl_tf"] != "pullback":
            s, step = swing_state(df, p["sl_tf"]), TIMEFRAMES[p["sl_tf"]] * MIN_NS
            sl = {-1: Swing(step, _ns(s[f"{p['sl_tf']}_sh_ts"])), 1: Swing(step, _ns(s[f"{p['sl_tf']}_sl_ts"]))}
        space = {-1: (hi, lo, cl), 1: (-lo, -hi, -cl)}
        ends = spf["end"].astype(int).to_numpy()
        nxt = np.r_[ends[1:], n]
        rows = []
        for i, (side_value, stop_price, tf) in enumerate(zip(spf["side"], spf["stop"], spf["tf"], strict=True)):
            side = int(side_value)
            h_, l_, c_ = space[side]
            src = Source(int(ends[i]), -side * round(stop_price / TICK), tf, int(nxt[i]), int(last[ends[i]]))
            rec = scan(h_, l_, c_, ts, src, tfs[side], int(p["risk"]), float(p["rr"]), sl[side])
            for key in ("limit", "stop", "target"):
                if not np.isnan(rec[key]):
                    rec[key] = round(-side * rec[key] * TICK, 2)  # reversal side = -side
            rows.append({"side": -side, **rec})
        return pd.DataFrame(rows, columns=cols)

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        s = self.setups(df, p)
        s = s[s["limit"].notna()]
        sig = pd.DataFrame({"side": s["side"].astype(int).to_numpy(), "limit": s["limit"].to_numpy(float),
                            "stop": s["stop"].to_numpy(float), "target": s["target"].to_numpy(float),
                            "expire": s["expire"].astype(int).to_numpy()}, index=s["end"].astype(int).to_numpy())
        if not sig.index.is_unique:
            raise RuntimeError("two reversals on one bar; each reversal ends before the next SPF signal")
        return sig.sort_index()
