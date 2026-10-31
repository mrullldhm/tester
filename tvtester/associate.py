"""Feature association report: baseline trades bucketed by each feature's value at their signal bar.

Descriptive only. Continuous features: quintiles of the trades' own values, labelled lower .. upper edge (upper
edge included; pandas qcut). A bucket's numbers are not what a filter would earn: removing a trade can let in
another trade the baseline never took, so a filter's effect is only known from an engine run. Intervals come from
a block bootstrap by ISO week and are not adjusted for picking the largest spread among many buckets.
"""

import numpy as np
import pandas as pd

from . import metrics
from .config import DEFAULT
from .engine import run

RESAMPLES = 2000
BINS = 5


def trade_features(mod, params: dict, bars, ticks: int) -> pd.DataFrame:
    """Trades of one engine run with every feature value at the trade's signal bar."""
    s = mod.STRATEGY(**params)
    res = run(s, bars, DEFAULT.with_slippage(ticks))
    tf = metrics.trade_frame(res)
    vals = s.features(bars)
    sb = tf["signal_bar"].to_numpy()
    for name, arr in vals.items():
        tf[name] = arr[sb]
    tz = getattr(getattr(s, "s", None), "tz", "UTC")
    tf["weekday"] = tf["signal_time"].dt.tz_convert(tz).dt.day_name().str[:3]
    tf["direction"] = tf["type"]
    iso = tf["signal_time"].dt.tz_convert("UTC").dt.isocalendar()
    tf["week"] = iso["year"].astype(int) * 100 + iso["week"].astype(int)
    return tf


def _interval(profits: np.ndarray, weeks: np.ndarray, rng) -> tuple[float, float]:
    """90% interval of the average trade, resampling whole ISO weeks."""
    if len(profits) < 2:
        return float("nan"), float("nan")
    u, inv = np.unique(weeks, return_inverse=True)
    sums = np.bincount(inv, weights=profits)
    counts = np.bincount(inv).astype(float)
    pick = rng.integers(len(u), size=(RESAMPLES, len(u)))
    avg = sums[pick].sum(axis=1) / counts[pick].sum(axis=1)
    return float(np.percentile(avg, 5)), float(np.percentile(avg, 95))


def buckets(tf: pd.DataFrame, feature: str, categorical: bool, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    if categorical:
        groups = tf[feature].astype(str)
    else:
        v = tf[feature]
        groups = pd.Series("NaN", index=tf.index, dtype=object)
        ok = v.notna()
        if v[ok].nunique() < BINS:  # too few distinct values for quintiles: one bucket per value
            groups[ok] = [f"{x:.4g} .. {x:.4g}" for x in v[ok]]
        elif ok.any():
            q, edges = pd.qcut(v[ok], BINS, duplicates="drop", retbins=True, labels=False)
            names = [f"{edges[j]:.4g} .. {edges[j + 1]:.4g}" for j in range(len(edges) - 1)]
            groups[ok] = [names[int(j)] for j in q]
    rows = []
    order = sorted(groups.unique(), key=lambda g: (g == "NaN", _left(g)))
    for g in order:
        sub = tf[groups == g]
        p = sub["profit"].to_numpy()
        lo, hi = _interval(p, sub["week"].to_numpy(), rng)
        rows.append({"bucket": g, "trades": len(sub), "percent_profitable": (p > 0).mean() * 100 if len(p) else None,
                     "avg_trade": p.mean() if len(p) else None, "avg_lo90": lo, "avg_hi90": hi,
                     "net_profit": p.sum()})
    return pd.DataFrame(rows)


def _left(g: str):
    try:
        return float(g.split(" .. ")[0])
    except ValueError:
        return g
