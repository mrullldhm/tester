"""Swing Point Manipulation (owner, 2026-11-15).
Spec and trial budget: docs/strategies/swing_point_manipulation/README.md.

Long: newest 1H points are swing high then swing low. Candle 2 high >= candle 1 high; candle 3 first takes candle 2's
low, then its high. At the close of the 15m candle that took the high, buy limit (stop = that 15m low, max risk
ticks), target the latest 1H swing high. Short is the mirror.

Both sides run through one scan written for longs: short inputs are negated ("side space"), so a swing low becomes
a swing high and the result is negated back.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.data import to_ticks
from cltester.strategy import Base
from cltester.swings import build_candles, swing_state

NO_EXPIRY = 100_000  # bars; the engine still cancels at the day change, contract change and 3:10 PM CT
# An order placed at the signal and cancelled by the TP touch on the next bar: no trade, but it still cancels an
# older unfilled order (README rule 7).
PLACED_THEN_CANCELLED = "TP touched at the first working bar"
SIGNAL_AFTER_SESSION = "signal after the session or contract ended"
OUTSIDE = ("skip", "strict")  # newest swing high on the swing low's own candle: ignore it, or no setup (README)


@dataclass
class Frame:
    """Candles of one timeframe in side space (ticks) with their 1m bar positions."""

    h: np.ndarray
    lo: np.ndarray
    ts: np.ndarray  # candle open (ns)
    first: np.ndarray  # first 1m bar
    last: np.ndarray  # last 1m bar
    avail: np.ndarray  # 1m bar at whose close the candle is complete


@dataclass
class State:
    """1H swing state in side space, per 1m bar (as known at that bar's close)."""

    armed: np.ndarray  # newest point is the swing low and a swing high exists
    tp: np.ndarray  # latest swing high (ticks)
    base_ts: np.ndarray  # newest swing low candle open (ns)


def _ns(s: pd.Series) -> np.ndarray:
    """Timestamps as int64 ns; NaT becomes the smallest int64."""
    return pd.DatetimeIndex(s).as_unit("ns").asi8


def _states(s: pd.DataFrame, outside: str) -> dict[int, State]:
    """Per side: armed, TP and swing low candle, from swing_state(df, "1h", prev=True, newest=True).
    Long armed: the newest point is the swing low and a swing high exists (TP = that swing high).
    outside "skip" also arms when the newest swing high sits on the swing low's own candle (an outside candle that
    printed the low first): that high is ignored and TP = the swing high before it. Short is the mirror."""
    px = {k: np.round(s[f"1h_{k}"].to_numpy(float) / TICK) for k in ("sh", "sl", "sh2", "sl2")}
    sh_ts, sl_ts = _ns(s["1h_sh_ts"]), _ns(s["1h_sl_ts"])
    newest = s["1h_newest"].to_numpy()
    both = ~np.isnan(px["sh"]) & ~np.isnan(px["sl"])
    same = both & (sh_ts == sl_ts)
    out = {}
    for side, opp, me_ts, want in ((1, "sh", sl_ts, -1), (-1, "sl", sh_ts, 1)):
        armed, tp = both & (newest == want), px[opp].copy()
        if outside == "skip":
            alt = same & (newest == -want) & ~np.isnan(px[f"{opp}2"])
            armed |= alt
            tp[alt] = px[f"{opp}2"][alt]
        out[side] = State(armed, side * tp, me_ts)
    return out


def _frame(cd, side: int) -> Frame:
    h, lo = (cd.h, cd.l) if side == 1 else (-cd.l, -cd.h)
    return Frame(h.astype(float), lo.astype(float), cd.ts.as_unit("ns").asi8, cd.first, cd.last, cd.avail)


def scan(hi, lo, cl, h1: Frame, c3_bars: tuple[np.ndarray, np.ndarray], m15: Frame, m15_of: np.ndarray, st: State,
         last: np.ndarray, risk: int, confirm: bool = False) -> list[dict]:
    """Every candle 3 in side space (long). Returns setup records; limit is NaN when there is no trade.
    c3_bars: per complete 1H candle (as candle 2), first and last 1m bar of the next clock hour in the data (-1: none).
    That hour may be unfinished: its signals must exist before the hour closes (live, forward data).
    m15_of: per 1m bar, the 15m candle holding it (-1: candle not complete in the data).
    last: per 1m bar, the last bar of its trading day and contract.
    confirm: place the order at the close of the next 15m candle, only if it stayed above the break candle's low."""
    rows = []
    for k in range(2, len(h1.h) + 1):  # k = candle 3; len(h1.h) is the unfinished last hour
        a = int(h1.avail[k - 1])  # candle 2 complete at this bar's close
        if not st.armed[a] or h1.ts[k - 2] < st.base_ts[a] or h1.h[k - 1] < h1.h[k - 2]:
            continue
        tp = float(st.tp[a])
        rec = {"c3": k, "lo_touch": -1, "hi_touch": -1, "why": "", "limit": np.nan, "stop": np.nan,
               "target": tp, "end": -1, "expire": np.nan}
        rows.append(rec)
        f, e = int(c3_bars[0][k - 1]), int(c3_bars[1][k - 1])
        if f < 0:
            continue
        lt = np.flatnonzero(lo[f:e + 1] <= h1.lo[k - 1])
        ht = np.flatnonzero(hi[f:e + 1] >= h1.h[k - 1])
        if not len(lt) or not len(ht):
            rec["why"] = "no touch of both sides"
            continue
        tl, th = f + int(lt[0]), f + int(ht[0])
        rec.update(lo_touch=tl, hi_touch=th)
        if tl >= th:
            rec["why"] = "high first or same 1m bar"
            continue
        q = int(m15_of[th])
        if q < 0:
            rec["why"] = "15m candle not complete"
            continue
        sig, qe = int(m15.avail[q]), int(m15.last[q])
        stop, close = m15.lo[q], cl[qe]
        rec.update(end=sig, stop=stop)
        session_end = int(last[th])
        if confirm and sig <= session_end:
            if q + 1 >= len(m15.lo) or m15.first[q + 1] > session_end:
                rec["why"] = "no next 15m candle in the session"
                continue
            if m15.lo[q + 1] <= stop:
                rec["why"] = "next 15m candle took the low"
                continue
            sig = int(m15.avail[q + 1])
            rec["end"] = sig
        # A candle missing its last minute completes at the next bar, which can open the next session or contract.
        if sig > session_end:
            rec["why"] = SIGNAL_AFTER_SESSION
            continue
        if hi[th:sig + 1].max() >= tp:
            rec["why"] = "TP touched before the order"
            continue
        if close <= stop:
            rec["why"] = "no risk (close at the low)"
            continue
        limit = close if close - stop <= risk else stop + risk  # <= close < TP (TP not touched through sig)
        end = int(last[sig])
        hit = np.flatnonzero(hi[sig + 1:end + 1] >= tp)
        expire = int(hit[0]) if len(hit) else NO_EXPIRY  # works bars sig+1 .. the bar before the TP touch
        if expire < 1:
            rec["why"] = PLACED_THEN_CANCELLED
            continue
        rec.update(why="trigger", limit=limit, expire=expire)
    return rows


class Strategy(Base):
    NAME = "swing_point_manipulation"
    ABOUT = ("Owner: 1H swing high then swing low; candle 2 high >= candle 1 high; candle 3 takes candle 2's low then "
             "its high. Buy limit at the 15m break candle close (max risk ticks above its low), target the latest "
             "1H swing high. Short is the mirror.")
    PARAMS = {"risk": 15, "outside": "skip", "confirm": 0, "swing_tf": "1h", "entry_tf": "15m"}
    GRID = {"risk": [15, 20, 25], "outside": list(OUTSIDE)}  # confirm 1 with outside strict only: README

    def setups(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        cols = ["side", "c3", "lo_touch", "hi_touch", "why", "limit", "stop", "target", "end", "expire"]
        if (p["swing_tf"], p["entry_tf"]) != ("1h", "15m"):
            raise ValueError("swing_tf 1h and entry_tf 15m are fixed (README)")
        if p["outside"] not in OUTSIDE:
            raise ValueError(f"outside must be one of {OUTSIDE}")
        if p["confirm"] not in (0, 1):
            raise ValueError("confirm must be 0 or 1")
        n = len(df)
        h1c, m15c = build_candles(df, "1h"), build_candles(df, "15m")
        if n < 2 or len(h1c) < 2 or len(m15c) == 0:
            return pd.DataFrame(columns=cols)
        lo, hi, cl = (to_ticks(df[k]).astype(float) for k in ("low", "high", "close"))
        day, sym = (pd.factorize(df[k])[0] for k in ("trading_day", "raw_symbol"))
        cut = (day[1:] != day[:-1]) | (sym[1:] != sym[:-1])
        last = np.r_[np.flatnonzero(cut), n - 1][np.cumsum(np.r_[False, cut])]
        m15_of = np.full(n, -1)
        size = m15c.last - m15c.first + 1  # candles are contiguous from bar 0
        m15_of[:size.sum()] = np.repeat(np.arange(len(m15c)), size)
        hour = _ns(df["ts"]) // (3_600 * 10**9)
        starts = np.flatnonzero(np.r_[True, hour[1:] != hour[:-1]])
        ends = np.r_[starts[1:] - 1, n - 1]
        nxt = np.searchsorted(starts, h1c.first, side="right")  # the hour after each complete candle
        has = nxt < len(starts)
        c3_bars = (np.where(has, starts[np.minimum(nxt, len(starts) - 1)], -1),
                   np.where(has, ends[np.minimum(nxt, len(starts) - 1)], -1))
        states = _states(swing_state(df, "1h", prev=True, newest=True), p["outside"])
        space = {1: (hi, lo, cl), -1: (-lo, -hi, -cl)}
        rows = []
        for side in (1, -1):
            h_, l_, c_ = space[side]
            for rec in scan(h_, l_, c_, _frame(h1c, side), c3_bars, _frame(m15c, side), m15_of, states[side],
                            last, int(p["risk"]), bool(p["confirm"])):
                for key in ("limit", "stop", "target"):
                    if not np.isnan(rec[key]):
                        rec[key] = round(side * rec[key] * TICK, 2)
                rows.append({"side": side, **rec})
        return pd.DataFrame(rows, columns=cols)

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        setups = self.setups(df, p)
        placed = np.sort(setups.loc[setups["limit"].notna() | (setups["why"] == PLACED_THEN_CANCELLED), "end"]
                         .astype(int).to_numpy())
        if len(placed) != len(np.unique(placed)):
            raise RuntimeError("two setups on one bar; each candle 3 gives one 15m break candle")
        s = setups[setups["limit"].notna()].sort_values("end", kind="stable")
        ends = s["end"].astype(int).to_numpy()
        # a newer placed order cancels an unfilled one: it works through the newer signal's bar (README rule 7)
        nxt = np.searchsorted(placed, ends, side="right")
        cap = np.where(nxt < len(placed), placed[np.minimum(nxt, len(placed) - 1)] - ends, NO_EXPIRY)
        expire = np.minimum(s["expire"].astype(int).to_numpy(), cap)
        return pd.DataFrame({"side": s["side"].astype(int).to_numpy(), "limit": s["limit"].to_numpy(float),
                             "stop": s["stop"].to_numpy(float), "target": s["target"].to_numpy(float),
                             "expire": expire}, index=ends)
