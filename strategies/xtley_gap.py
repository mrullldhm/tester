"""Port of Xtley001 Mean-Reversion-Gap EA (USOIL settings). Hypothesis: docs/strategies/xtley_gap/README.md."""

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.indicators import atr_sma, close_ticks, ema, in_session, on_1m, rsi_sma, tf_candles, tf_minutes
from cltester.strategy import Base


class Strategy(Base):
    NAME = "xtley_gap"
    ABOUT = "EMA360 gap mean reversion with EMA20/RSI/ATR filters, 1.5 ATR stop, 5R target, R-step + ATR trail."
    PARAMS = {"tf": "15m", "trail": True, "gap_pct": 0.6, "sl_atr": 1.5, "rr": 5.0, "trail_atr": 2.0,
              "offset": 2, "min_gap_bars": 5}
    GRID = {"tf": ["5m", "15m", "30m"], "trail": [True, False]}

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        n = len(df)
        cd = tf_candles(df, p["tf"])
        av = cd["avail"].to_numpy()
        c = cd["close"]
        e360, e20 = ema(c, 360), ema(c, 20)
        a10, a20 = atr_sma(cd["high"], cd["low"], c, 10), atr_sma(cd["high"], cd["low"], c, 20)
        rsi = rsi_sma(c, 20)
        gap = e360 * p["gap_pct"] / 100
        calm = a10 < a20
        buy = calm & (c < e360 - gap) & (c > e20) & (rsi.shift() > rsi) & (rsi < 70)
        sell = calm & (c > e360 + gap) & (c < e20) & (rsi.shift() < rsi) & (rsi > 30)
        buy &= e360.notna() & (np.arange(len(cd)) >= 360)
        sell &= e360.notna() & (np.arange(len(cd)) >= 360)
        side_c = np.where(buy, 1, np.where(sell, -1, 0))
        keep, last = [], -10**9
        for k in np.flatnonzero(side_c):
            if k - last >= p["min_gap_bars"]:
                keep.append(k)
                last = k
        keep = np.array(keep, dtype=np.int64)
        keep = keep[in_session(df, cd)[keep]] if len(keep) else keep
        idx = av[keep]
        sd = side_c[keep]
        close = c.to_numpy()[keep]
        atr = a10.to_numpy()[keep]
        limit = np.round(close / TICK - sd * p["offset"]) * TICK
        risk = np.maximum(np.round(p["sl_atr"] * atr / TICK), 1) * TICK
        minutes = tf_minutes(p["tf"])
        # trade management needs the 1m closes and the timeframe ATR known at each 1m bar
        self._c = close_ticks(df)
        self._atr = on_1m(a10.to_numpy() / TICK, av, n)
        self._p = p
        out = pd.DataFrame({"side": sd, "limit": limit, "stop": limit - sd * risk,
                            "target": limit + sd * risk * p["rr"], "expire_min": 5 * minutes}, index=idx)
        return out[~out.index.duplicated(keep="last")]  # 2 candles done on 1 bar: newer wins

    def manage(self, ctx):
        p = self._p
        if not p["trail"]:
            return ctx.S, False
        if "R" not in ctx.state:
            ctx.state["R"] = ctx.E - ctx.S
        R = ctx.state["R"]
        px = ctx.to_side(int(self._c[ctx.m - 1]))  # last 1m close (source: live bid/ask)
        units = (px - ctx.E) // R
        if units < 1:
            return ctx.S, False
        new = ctx.E + units * R
        atr = self._atr[ctx.m - 1]
        if np.isfinite(atr):
            new = max(new, px - int(round(p["trail_atr"] * atr)))
        if ctx.S < new < px:
            return new, False
        return ctx.S, False
