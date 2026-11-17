"""purple_levels all 5m, signals only in 08:30-13:30 CT. Frozen 2026-11-17: docs/strategies/purple_levels_rth/."""

import numpy as np
import pandas as pd

from cltester.data import add_session
from cltester.strategy import Base
from strategies.purple_levels import Strategy as PurpleLevels

RTH_START, RTH_END = 8 * 60 + 30, 13 * 60 + 30  # CT minutes of day
FROZEN = {"levels": "all", "tf": "5m", "confirm": 4, "rr": 1.0, "expire_candles": 4}


def rth_filter(df: pd.DataFrame, sig: pd.DataFrame) -> pd.DataFrame:
    """Keep signals decided (signal bar close, CT) in [08:30, 13:30); the order stops working at 13:30."""
    if sig.empty:
        return sig
    if "ct_minute" not in df:
        df = add_session(df)
    decision = df["ct_minute"].to_numpy()[sig.index.to_numpy()] + 1  # bar ts is its open; decision at its close
    is_rth = (decision >= RTH_START) & (decision < RTH_END)
    out = sig[is_rth].copy()
    out["expire_min"] = np.minimum(out["expire_min"].to_numpy(float), RTH_END - decision[is_rth])
    return out


class Strategy(Base):
    NAME = "purple_levels_rth"
    ABOUT = "purple_levels (all fixed levels, 5m) with signals only in regular trading hours 08:30-13:30 CT."
    PARAMS = dict(FROZEN)
    GRID: dict = {}
    DEPENDS = ("purple_levels", "purple_pa")

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        changed = sorted(k for k in FROZEN if p.get(k) != FROZEN[k])
        if changed:  # forward test of one pre-registered spec; a change is a new strategy
            raise ValueError(f"purple_levels_rth is frozen; cannot override {changed}")
        return rth_filter(df, PurpleLevels().signals(df, p))
