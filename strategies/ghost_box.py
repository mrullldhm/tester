"""Ghost Box, futures translation of a 0DTE SPX iron-condor checklist. Spec: docs/strategies/ghost_box/README.md.

Box = 17:00-07:59 CT high/low. Ghost wick = first 5m candle from 08:00 CT that pokes strictly through a wall and
closes back inside. Fade it inside the 08:30-09:00 CT window: sell limit (wick above) or buy limit (wick below) at the
wall or at the signal close; stop 1 tick beyond the wick; target box middle or opposite wall. Exit at the next open
after a 5m close beyond the losing-side wall, or at 13:30 CT.
"""

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.data import to_ticks
from cltester.strategy import Base
from cltester.swings import Candles, build_candles

BOX_END = 900  # sess_minute of 08:00 CT (minutes since 17:00 CT)
WIN_START = 930  # 08:30 CT
WIN_END = 960  # 09:00 CT
SETTLE = 1230  # 13:30 CT
MIN_BOX_BARS = 600
OPEN_LATE = 5  # 08:00 bar may be missing; first bar by 08:05 is the open

DAY_COLS = ["day", "status", "top", "bot", "open", "width_pct", "gap_pct", "side", "wick_ext", "signal",
            "sig_close", "expire_min"]


def mid_target(top: int, bot: int, side: int) -> int:
    """Box middle in ticks; a half tick rounds toward the entry (up for a short, down for a long)."""
    return (top + bot) // 2 if side == 1 else -(-(top + bot) // 2)


def ghost_days(df: pd.DataFrame, cd: Candles | None = None) -> pd.DataFrame:
    """One row per trading day: box, filters and ghost-wick result. Prices in ticks. status:
    data / roll / no_open / no_settle (unusable), no_push, both, broken, broken_after, late, setup.
    Width and gap are reported for every usable day and applied only by the caller (the study needs all days).
    Point-in-time: a setup uses bars up to its signal bar only."""
    n = len(df)
    if n == 0:
        return pd.DataFrame(columns=DAY_COLS)
    sess = df["sess_minute"].to_numpy()
    day = pd.factorize(df["trading_day"])[0]
    sym = pd.factorize(df["raw_symbol"])[0]
    o, h, lo, c = (to_ticks(df[k]) for k in ("open", "high", "low", "close"))
    cd = build_candles(df, "5m") if cd is None else cd
    c_start = (sess[cd.first] // 5) * 5
    c_day = day[cd.first]  # candles are in bar order, so c_day is sorted
    starts = np.r_[0, np.flatnonzero(day[1:] != day[:-1]) + 1]
    ends = np.r_[starts[1:], n]
    tdays = df["trading_day"].to_numpy()
    rows: list[dict[str, object]] = []
    prev_settle: tuple[int, int] | None = None  # (close ticks, sym) of the previous day's last bar before 13:30 CT
    for d, (a, b) in enumerate(zip(starts, ends, strict=True)):
        s = sess[a:b]
        rec: dict[str, object] = {k: np.nan for k in DAY_COLS}
        rec.update(day=tdays[a], status="data", side=0)
        rows.append(rec)
        settle_i = np.flatnonzero(s < SETTLE)
        this_settle = (int(c[a + settle_i[-1]]), int(sym[a + settle_i[-1]])) if len(settle_i) else None
        settle_prev, prev_settle = prev_settle, this_settle
        box = a + np.flatnonzero(s < BOX_END)
        if len(box) < MIN_BOX_BARS:
            continue
        op = np.flatnonzero((s >= BOX_END) & (s <= BOX_END + OPEN_LATE))
        if not len(op):
            rec["status"] = "no_open"
            continue
        if len(np.unique(sym[a:a + op[0] + 1])) != 1:
            rec["status"] = "roll"
            continue
        if settle_prev is None or settle_prev[1] != sym[a]:
            rec["status"] = "no_settle"
            continue
        top, bot = int(h[box].max()), int(lo[box].min())
        opn = int(o[a + op[0]])
        rec.update(top=top, bot=bot, open=opn, width_pct=100 * (top - bot) / opn,
                   gap_pct=100 * abs(opn - settle_prev[0]) / settle_prev[0])
        k0, k1 = np.searchsorted(c_day, [d, d + 1])
        ks = k0 + np.flatnonzero((c_start[k0:k1] >= BOX_END) & (c_start[k0:k1] < WIN_END))
        push = [k for k in ks if cd.h[k] > top or cd.l[k] < bot]
        if not push:
            rec["status"] = "no_push"
            continue
        w = push[0]
        up, dn = cd.h[w] > top, cd.l[w] < bot
        if up and dn:
            rec["status"] = "both"
            continue
        if not bot <= cd.c[w] <= top:
            rec["status"] = "broken"
            continue
        side = -1 if up else 1
        rec.update(side=side, wick_ext=int(cd.h[w] if up else cd.l[w]))
        pre = a + np.flatnonzero(s < WIN_START)
        sig = max(int(cd.avail[w]), int(pre[-1]))
        if sig >= b:
            rec["status"] = "late"
            continue
        if sess[sig] < WIN_START - 1:
            rec["status"] = "data"  # 08:29 bar missing: the order would start before 08:30
            continue
        if len(np.unique(sym[a:sig + 1])) != 1:
            rec["status"] = "roll"
            continue
        after = [k for k in ks if k > w and cd.avail[k] <= sig]
        if any(not bot <= cd.c[k] <= top for k in after):
            rec["status"] = "broken_after"
            continue
        left = WIN_END - (int(sess[sig]) + 1)
        if left < 1:
            rec["status"] = "late"
            continue
        rec.update(status="setup", signal=sig, sig_close=int(c[sig]), expire_min=left)
    return pd.DataFrame(rows, columns=DAY_COLS)


class Strategy(Base):
    NAME = "ghost_box"
    ABOUT = ("Ghost Box (0DTE SPX condor checklist) as a CL fade: overnight box, first 08:00+ CT 5m push that closes "
             "back inside, limit fade 08:30-09:00 CT, stop beyond the wick, target box mid or opposite wall, exit on a "
             "5m close beyond the wall or at 13:30 CT.")
    PARAMS = {"entry": "wall", "target": "mid", "width_pct": 0.4, "gap_pct": 0.5}
    GRID = {"entry": ["wall", "close"], "target": ["mid", "opposite"]}

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        if p["entry"] not in ("wall", "close") or p["target"] not in ("mid", "opposite"):
            raise ValueError("entry: wall|close; target: mid|opposite")
        if float(p["width_pct"]) != 0.4 or float(p["gap_pct"]) != 0.5:
            raise ValueError("width_pct 0.4 and gap_pct 0.5 are fixed (PDF, README)")
        n = len(df)
        cd = build_candles(df, "5m")
        days = ghost_days(df, cd)
        ok = (days["status"] == "setup") & (days["width_pct"] >= p["width_pct"]) & (days["gap_pct"] < p["gap_pct"])
        d = days[ok]
        rows, walls = [], {}
        for r in d.itertuples(index=False):
            side, top, bot = int(r.side), int(r.top), int(r.bot)
            wall = top if side == -1 else bot
            limit = wall if p["entry"] == "wall" else int(r.sig_close)
            if p["target"] == "mid":
                target = mid_target(top, bot, side)
            else:
                target = bot if side == -1 else top
            if side * (target - limit) <= 0 or side * (target - int(r.sig_close)) <= 0:
                continue  # already at or beyond the target
            stop = int(r.wick_ext) - side
            rows.append((int(r.signal), side, limit * TICK, stop * TICK, target * TICK, float(r.expire_min)))
            walls[int(r.signal)] = wall
        # manage(): 5m close per 1m bar where a candle completes, and the clock
        c5 = np.full(n, np.nan)
        okc = cd.avail < n
        c5[cd.avail[okc]] = cd.c[okc]
        self._c5, self._sess, self._walls = c5, df["sess_minute"].to_numpy(), walls
        if not rows:
            return pd.DataFrame(columns=["side", "limit", "stop", "target", "expire_min"])
        cols = list(zip(*rows, strict=True))
        out = pd.DataFrame(dict(zip(["side", "limit", "stop", "target", "expire_min"], cols[1:], strict=True)),
                           index=pd.Index(cols[0], dtype=int))
        for k in ("limit", "stop", "target"):
            out[k] = out[k].round(2)
        return out

    def manage(self, ctx):
        m = ctx.m
        if self._sess[m] >= SETTLE:
            return ctx.S, True
        c5 = self._c5[m - 1]
        if np.isfinite(c5) and ctx.to_side(int(c5)) < ctx.to_side(self._walls[ctx.i]):
            return ctx.S, True
        return ctx.S, False
