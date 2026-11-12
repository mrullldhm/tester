"""Scribd "Crude Oil 10-15 points" setup. Hypothesis: docs/strategies/scribd_supertrend/README.md."""

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.indicators import atr_rma, close_ticks, ema, in_session, on_1m, supertrend, tf_candles, vortex
from cltester.strategy import Base

INR_REF = 4500.0  # MCX crude price level when the document was written


class Strategy(Base):
    NAME = "scribd_supertrend"
    ABOUT = "15m Supertrend(10,1.8) + EMA8/21 + Vortex > 1.1; ATR+4pt stop; trail after 10 pts or 15-pt target."
    PARAMS = {"exit": "trail", "st_len": 10, "st_mult": 1.8, "vi_len": 14, "atr_len": 14, "stop_pts": 4,
              "trail_pts": 10, "target_pts": 15}
    GRID = {"exit": ["trail", "fixed"]}

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        n = len(df)
        cd = tf_candles(df, "15m")
        av = cd["avail"].to_numpy()
        h, l, c = cd["high"], cd["low"], cd["close"]
        d, _ = supertrend(h, l, c, p["st_len"], p["st_mult"])
        e8, e21 = ema(c, 8).to_numpy(), ema(c, 21).to_numpy()
        vp, vm = (x.to_numpy() for x in vortex(h, l, c, p["vi_len"]))
        atr = atr_rma(h, l, c, p["atr_len"]).to_numpy()
        buy = (d == 1) & (e8 > e21) & (vp > 1.1) & (vm < 0.9)
        sell = (d == -1) & (e8 < e21) & (vm > 1.1) & (vp < 0.9)
        day = cd["day"].to_numpy()
        same_day = np.r_[False, day[1:] == day[:-1]]
        fresh_b = buy & ~(np.r_[False, buy[:-1]] & same_day)
        fresh_s = sell & ~(np.r_[False, sell[:-1]] & same_day)
        side = np.where(fresh_b, 1, np.where(fresh_s, -1, 0))
        k = np.flatnonzero((side != 0) & in_session(df, cd) & np.isfinite(atr))
        sd = side[k]
        entry = np.round(c.to_numpy()[k] / TICK) * TICK
        pt = entry / INR_REF
        risk = np.maximum(np.round((atr[k] + p["stop_pts"] * pt) / TICK), 1) * TICK
        tgt = entry + sd * np.maximum(np.round(p["target_pts"] * pt / TICK), 1) * TICK
        out = pd.DataFrame({"side": sd, "limit": entry, "stop": entry - sd * risk,
                            "target": tgt if p["exit"] == "fixed" else np.nan, "expire_min": 15}, index=av[k])
        self._c = close_ticks(df)
        self._atr = on_1m(atr / TICK, av, n)
        self._trail_t = p["trail_pts"] * df["close"].to_numpy() / INR_REF / TICK
        self._p = p
        return out[~out.index.duplicated(keep="last")]

    def manage(self, ctx):
        if self._p["exit"] != "trail":
            return ctx.S, False
        px = ctx.to_side(int(self._c[ctx.m - 1]))
        if not ctx.state.get("on") and px - ctx.E >= self._trail_t[ctx.m - 1]:
            ctx.state["on"] = True
        atr = self._atr[ctx.m - 1]
        if ctx.state.get("on") and np.isfinite(atr):
            new = px - int(round(atr))
            if ctx.S < new < px:
                return new, False
        return ctx.S, False
