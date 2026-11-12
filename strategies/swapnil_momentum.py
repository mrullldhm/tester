"""Port of Swapnil227-arch candle momentum. Hypothesis: docs/strategies/swapnil_momentum/README.md."""

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.indicators import in_session, tf_candles, tf_minutes
from cltester.strategy import Base


class Strategy(Base):
    NAME = "swapnil_momentum"
    ABOUT = "Two same-colour candles: enter, stop past the signal candle, 1R/3R target by stop size."
    PARAMS = {"tf": "4h", "x_pct": 0.05, "bucket_a": 2.0, "bucket_b": 2.5, "y": [1, 3, 1]}
    GRID = {"tf": ["4h", "1h", "15m"]}

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        cd = tf_candles(df, p["tf"])
        o, h, l, c = (cd[k].to_numpy() for k in ("open", "high", "low", "close"))
        green, red = c > o, c < o
        prev_g, prev_r = np.r_[False, green[:-1]], np.r_[False, red[:-1]]
        side = np.where(green & prev_g, 1, np.where(red & prev_r, -1, 0))
        k = np.flatnonzero(side != 0)
        k = k[in_session(df, cd)[k]]
        sd = side[k]
        limit = np.round(c[k] / TICK) * TICK
        x = np.maximum(np.round(c[k] * p["x_pct"] / 100 / TICK), 1) * TICK
        stop = np.where(sd == 1, l[k] - x, h[k] + x)
        risk = np.abs(limit - stop)
        ok = risk >= TICK  # signal candle closed at its extreme plus x: still at least one tick of risk
        frac = risk / limit * 100
        y = np.where(frac < p["bucket_a"], p["y"][0], np.where(frac <= p["bucket_b"], p["y"][1], p["y"][2]))
        target = limit + sd * risk * y
        idx = cd["avail"].to_numpy()[k]
        out = pd.DataFrame({"side": sd, "limit": limit, "stop": np.round(stop / TICK) * TICK,
                            "target": np.round(target / TICK) * TICK, "expire_min": tf_minutes(p["tf"])}, index=idx)
        out = out[ok]
        return out[~out.index.duplicated(keep="last")]  # 2 candles done on 1 bar: newer wins
