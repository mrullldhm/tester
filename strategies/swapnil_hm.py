"""Port of Swapnil227-arch Hilega Milega (HM) strategy. Hypothesis: docs/strategies/swapnil_hm/README.md."""

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.indicators import ema, in_session, on_1m, rsi_wilder, session_vwap, sma, tf_candles, tf_minutes, wma
from cltester.strategy import Base

REF = 145.0  # USDJPY price level the source values were set for


class Strategy(Base):
    NAME = "swapnil_hm"
    ABOUT = "Hilega Milega + BB basis + VWAP + extreme RSI; fixed % target, candle-based stop."
    PARAMS = {"tf": "4h", "rsi_buy": 75, "rsi_sell": 20, "five": 0.1, "trail": 4.5, "start": 0.5, "tgt": 3.0,
              "tgt_s": 2.8, "trail_s": 2.1, "start_s": 0.5}
    GRID = {"tf": ["4h", "1h"]}

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        n = len(df)
        cd = tf_candles(df, p["tf"])
        av = cd["avail"].to_numpy()
        o, c = cd["open"].to_numpy(), cd["close"].to_numpy()
        r9 = rsi_wilder(cd["close"], 9)
        ps, vs = ema(r9, 3).to_numpy(), wma(r9, 21).to_numpy()
        rsi = rsi_wilder(cd["close"], 14).to_numpy()
        basis = sma(cd["close"], 20).to_numpy()
        vw = session_vwap(df)[cd["last"].to_numpy()]  # VWAP of the candle's own session at its last bar
        buy = (vs < ps) & (c > basis) & (c > vw) & (rsi > p["rsi_buy"])
        sell = (vs > ps) & (c < basis) & (c < vw) & (rsi < p["rsi_sell"])
        ks = np.flatnonzero((buy | sell) & in_session(df, cd))
        rows, idx = [], []
        self._sig_candle = {}
        for k in ks:
            sd = 1 if buy[k] else -1
            entry = round(c[k] / TICK) * TICK
            u = entry / REF  # 1 source price unit in CL $
            five = p["five"] * u
            stop = None
            for q in range(k, max(k - 5000, -1), -1):
                body = (c[q] - o[q]) * sd
                if body >= five and (entry - o[q]) * sd > five:
                    stop = o[q] - sd * (p["trail"] if sd == 1 else p["trail_s"]) * u
                    break
            if stop is None:
                stop = entry - sd * (p["start"] if sd == 1 else p["start_s"]) * u
            tgt = entry + sd * (p["tgt"] if sd == 1 else p["tgt_s"]) * u
            stop = round(stop / TICK) * TICK
            if (entry - stop) * sd < TICK:
                continue
            rows.append((sd, entry, stop, round(tgt / TICK) * TICK, tf_minutes(p["tf"])))
            idx.append(av[k])
            self._sig_candle[int(av[k])] = int(k)
        self._o, self._c = o, c
        self._cand = on_1m(np.arange(len(cd)), av, n)  # newest complete candle per 1m bar
        self._p = p
        out = pd.DataFrame(rows, columns=["side", "limit", "stop", "target", "expire_min"], index=idx)
        # two candles complete on one bar (missing minutes): the newer decides, as in _sig_candle
        return out[~out.index.duplicated(keep="last")]

    def manage(self, ctx):
        """After each completed candle from the entry candle on, reset the stop from that candle (source trade())."""
        p = self._p
        k_now = self._cand[ctx.m - 1]
        first = self._sig_candle[ctx.i] + 1  # the entry candle
        last = ctx.state.get("done", first - 1)
        if np.isnan(k_now) or int(k_now) <= last:
            return ctx.S, False
        S = ctx.S
        for k in range(last + 1, int(k_now) + 1):
            o, c = self._o[k], self._c[k]
            u = c / REF
            five = p["five"] * u
            if ctx.side == 1:
                if c - o >= five:
                    S = round((o - p["trail"] * u) / TICK)
                elif c - o <= -five:
                    S = round((c - p["trail"] * u) / TICK)
            else:
                if o - c >= five:
                    S = -round((o + p["trail_s"] * u) / TICK)
                elif o - c <= -five:
                    S = -round((c + p["trail_s"] * u) / TICK)
        ctx.state["done"] = int(k_now)
        return int(S), False
