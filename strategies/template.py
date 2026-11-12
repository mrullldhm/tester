"""Plumbing check, not research: shows the strategy contract end to end. Do not optimise or report it.

At a fixed CT time, place a buy limit a few ticks under the close, with a fixed stop and target.
"""

import pandas as pd

from cltester.config import TICK
from cltester.strategy import Base


class Strategy(Base):
    NAME = "template"
    ABOUT = "Fixed-time buy limit below the close. Engine plumbing check only."
    PARAMS = {"ct_minute": 8 * 60 + 30, "offset": 5, "stop": 20, "target": 40, "expire": 15}

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        at = df.index[df["ct_minute"].to_numpy() == p["ct_minute"]]
        close = df["close"].to_numpy()[at]
        limit = close - p["offset"] * TICK
        return pd.DataFrame({"side": 1, "limit": limit, "stop": limit - p["stop"] * TICK,
                             "target": limit + p["target"] * TICK, "expire": p["expire"]}, index=at)
