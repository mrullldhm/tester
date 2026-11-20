"""Juda Swing Point (owner, 2026-11-18). Spec and trial budget: docs/strategies/juda_swing_point/README.md.

Long: 15m swing high taken out before any swing low; manipulation candle takes the previous high then the previous
low (1m order); the next candle stays above its low; EMA 10 > 20 > 50. Buy limit at the confirmation close (max
risk ticks above the confirmation low), stop = confirmation low, target = limit + tp ticks. Short is the mirror.

Both sides run through one scan written for longs: short candles are negated ("side space"), so a swing low becomes
a swing high and prices are negated back at the end.
"""

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.data import to_ticks
from cltester.indicators import ema
from cltester.strategy import Base
from cltester.swings import HIGH, Candles, build_candles, detect

NO_EXPIRY = 100_000  # bars; the engine still cancels at the day change, contract change and 3:10 PM CT
EMA_WARMUP = 50


def _high_first(h1, l1, o1, a: int, b: int, hi_lvl: int, lo_lvl: int) -> str:
    """1m bars a..b: 'hi' if high >= hi_lvl printed before low < lo_lvl, 'lo' if after, 'unknown' if same bar and
    the open does not settle it, 'none' if one never happens."""
    th = np.flatnonzero(h1[a:b + 1] >= hi_lvl)
    tl = np.flatnonzero(l1[a:b + 1] < lo_lvl)
    if not len(th) or not len(tl):
        return "none"
    th, tl = a + int(th[0]), a + int(tl[0])
    if th == tl:  # same minute: an open already beyond a level touched it first
        th -= int(o1[th] >= hi_lvl)
        tl -= int(o1[tl] < lo_lvl)
    return "hi" if th < tl else "lo" if tl < th else "unknown"


def lhll_cancel(cd: Candles, st: dict[str, np.ndarray], c: int, end_bar: int) -> int:
    """1m bar at whose close the first lower high or lower low after confirmation candle c is known, or -1.
    Side space (long). The state known at candle k's close is st[k-1]. A new swing high (sh_candle changes) priced
    below the swing high before it (sh2) is a lower high; a new swing low below sl2 is a lower low."""
    prev_sh, prev_sl = st["sh_candle"][c - 1], st["sl_candle"][c - 1]
    k = c + 1
    while k < len(cd) and cd.avail[k] <= end_bar:
        s = k - 1
        sh, sl = st["sh_candle"][s], st["sl_candle"][s]
        if sh >= 0 and sh != prev_sh and st["sh2_candle"][s] >= 0 and st["sh_price"][s] < st["sh2_price"][s]:
            return int(cd.avail[k])
        if sl >= 0 and sl != prev_sl and st["sl2_candle"][s] >= 0 and st["sl_price"][s] < st["sl2_price"][s]:
            return int(cd.avail[k])
        prev_sh, prev_sl = sh, sl
        k += 1
    return -1


def scan(cd: Candles, h1, l1, o1) -> tuple[list[tuple[int, int, int]], dict[str, np.ndarray]]:
    """Setups in side space (long): list of (swing high candle, manipulation candle m, confirmation candle m+1), and
    the swing state.
    Point-in-time: detect state[k] is known when candle k+1 closes; candle m's checks use state[m-1]."""
    _, st = detect(cd)
    e10, e20, e50 = (ema(cd.c.astype(float), n).to_numpy() for n in (10, 20, 50))
    trend = (e10 > e20) & (e20 > e50)
    trend[:EMA_WARMUP] = False
    h, lo, n = cd.h, cd.l, len(cd)
    out, used = [], set()
    for j in range(2, n):
        if st["newest"][j - 1] != HIGH:
            continue
        p, pc = st["sh_price"][j - 1], int(st["sh_candle"][j - 1])
        if pc < 0 or pc in used or h[j] < p:
            continue
        used.add(pc)  # one invalidation per swing high
        for m in range(j, n - 1):
            if m > j and (st["newest"][m - 1] != HIGH or st["sh_candle"][m - 1] != pc):
                break  # swing low formed or a new swing high confirmed
            if h[m] < h[m - 1] or lo[m] >= lo[m - 1]:
                continue
            order = _high_first(h1, l1, o1, int(cd.first[m]), int(cd.last[m]), int(h[m - 1]), int(lo[m - 1]))
            if order == "unknown":
                break
            if order != "hi":
                continue
            if lo[m + 1] > lo[m]:
                if trend[m + 1]:
                    out.append((pc, m, m + 1))
                break  # m is now a swing low candidate: the structure has changed
    return out, st


class Strategy(Base):
    NAME = "juda_swing_point"
    ABOUT = ("Owner: 15m swing high taken out before a swing low; manipulation candle takes the previous high then "
             "low; next candle holds its low; EMA 10>20>50. Buy limit at the confirmation close (max risk ticks), "
             "stop at the confirmation low, fixed tp ticks. Short is the mirror.")
    PARAMS = {"risk": 15, "tp": 15, "tf": "15m", "cancel": "lhll", "stop": "confirm"}
    GRID = {"tp": [15, 30]}

    def setups(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        cols = ["side", "m_ts", "c_ts", "signal", "limit", "stop", "target", "expire", "why"]
        if p["tf"] != "15m" or int(p["risk"]) != 15 or int(p["tp"]) not in (15, 30):
            raise ValueError("tf 15m and risk 15 are fixed; tp 15 or 30 (README)")
        if p["cancel"] not in ("tp", "lhll"):
            raise ValueError("cancel must be tp (first TP touch) or lhll (15m lower high / lower low)")
        if p["stop"] not in ("confirm", "manip"):
            raise ValueError("stop must be confirm (confirmation candle low) or manip (manipulation candle low)")
        n = len(df)
        base = build_candles(df, "15m")
        if n < 2 or len(base) < EMA_WARMUP + 2:
            return pd.DataFrame(columns=cols)
        day, sym = (pd.factorize(df[k])[0] for k in ("trading_day", "raw_symbol"))
        cut = (day[1:] != day[:-1]) | (sym[1:] != sym[:-1])
        last = np.r_[np.flatnonzero(cut), n - 1][np.cumsum(np.r_[False, cut])]
        contract = np.cumsum(np.r_[False, sym[1:] != sym[:-1]])  # one id per uninterrupted raw_symbol run
        risk, tp = int(p["risk"]), int(p["tp"])
        hi_, lo_, op_ = (to_ticks(df[k]) for k in ("high", "low", "open"))
        rows = []
        for side in (1, -1):
            cd = base if side == 1 else base.mirrored()
            h1, l1, o1 = (hi_, lo_, op_) if side == 1 else (-lo_, -hi_, -op_)
            found, st = scan(cd, h1, l1, o1)
            for pc, m, c in found:
                sig = int(cd.avail[c])
                rec = {"side": side, "m_ts": cd.ts[m], "c_ts": cd.ts[c], "signal": sig, "limit": np.nan,
                       "stop": np.nan, "target": np.nan, "expire": np.nan, "why": ""}
                rows.append(rec)
                stop, close = int(cd.l[c] if p["stop"] == "confirm" else cd.l[m]), int(cd.c[c])
                if sig >= n or last[sig] != last[int(cd.last[c])]:
                    rec["why"] = "confirmation completes in the next session or contract"
                    continue
                # prices are not back-adjusted: a roll anywhere from the candle left of the swing high (its rule-3
                # reference) to the signal could fake the swing, the break, the sweep, the confirmation and the stop
                # (Codex reviews 2026-11-18)
                if contract[int(cd.first[max(pc - 1, 0)])] != contract[sig]:
                    rec["why"] = "contract roll inside the setup"
                    continue
                if close <= stop:
                    rec["why"] = "no risk (close at the low)"
                    continue
                limit = close if close - stop <= risk else stop + risk
                target = limit + tp
                end = int(last[sig])
                if p["cancel"] == "tp":
                    hit = np.flatnonzero(h1[sig + 1:end + 1] >= target)
                    # works through the first TP-touch bar; the engine's kill (= target) decides that bar with its
                    # own fill rule (open at/through the fill level fills first, else cancelled; Codex 2026-11-18)
                    expire, why = (int(hit[0]) + 1 if len(hit) else NO_EXPIRY), "trigger"
                else:
                    gone = lhll_cancel(cd, st, c, end)  # known at that bar's close: the order works through it
                    expire, why = (gone - sig if gone >= 0 else NO_EXPIRY), "trigger"
                rec.update(limit=side * limit * TICK, stop=side * stop * TICK, target=side * target * TICK,
                           expire=expire, why=why)
        s = pd.DataFrame(rows, columns=cols)
        for k in ("limit", "stop", "target"):
            s[k] = s[k].astype(float).round(2)
        return s

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        setups = self.setups(df, p)
        placed = setups[setups["why"] == "trigger"]
        bars = np.sort(placed["signal"].astype(int).to_numpy())
        s = placed.sort_values("signal", kind="stable")
        s = s.drop_duplicates("signal", keep="first")  # long and short on one bar: long first (never seen; guard)
        ends = s["signal"].astype(int).to_numpy()
        # a newer placed order cancels an unfilled one: it works through the newer signal's bar
        nxt = np.searchsorted(bars, ends, side="right")
        cap = np.where(nxt < len(bars), bars[np.minimum(nxt, len(bars) - 1)] - ends, NO_EXPIRY)
        expire = np.minimum(s["expire"].astype(int).to_numpy(), cap)
        return pd.DataFrame({"side": s["side"].astype(int).to_numpy(), "limit": s["limit"].to_numpy(float),
                             "stop": s["stop"].to_numpy(float), "target": s["target"].to_numpy(float),
                             "expire": expire, "kill": s["target"].to_numpy(float) if p["cancel"] == "tp"
                             else np.nan}, index=ends)
