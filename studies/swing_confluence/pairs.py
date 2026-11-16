"""Pairwise scan: every pair of context features on bases 5m, 15m, 1h. Edge vs fair, BH over all cells."""

from itertools import combinations
from math import erfc, sqrt

import numpy as np
import pandas as pd

from studies.swing_confluence.build import CONTEXT
from studies.swing_confluence.scan import PATH, bh


def fail_count(e: pd.DataFrame) -> pd.Series:
    """Consecutive rule-5 replacements before this event (0 = fresh point, 1 = first sweep of the prior point ...)."""
    out = np.zeros(len(e), dtype=np.int64)
    for _, g in e.sort_values("bar").groupby(["base", "side"]):
        r = g["replace"].to_numpy()
        run = np.zeros(len(r), dtype=np.int64)
        for k in range(1, len(r)):
            run[k] = run[k - 1] + 1 if r[k] else 0
        out[g.index.to_numpy()] = run
    return pd.Series(out, index=e.index)


if __name__ == "__main__":
    e = pd.read_parquet(PATH)
    e = e[e["base"].isin(["5m", "15m", "1h"])].reset_index(drop=True)
    e["fails"] = fail_count(e).clip(upper=3)
    e = e[(e["outcome"] >= 0) & (~e["roll"]) & e["fair"].notna()].reset_index(drop=True)
    f = {"fails": e["fails"].astype(str)}
    for tf in CONTEXT:
        f[f"{tf}_trend"] = e[f"{tf}_trend"].astype(str)
        f[f"{tf}_leg"] = e[f"{tf}_leg"].astype(str)
        f[f"{tf}_pos"] = pd.cut(e[f"{tf}_pos"], [-np.inf, 0, .33, .67, 1, np.inf],
                                labels=["<0", "lo", "mid", "hi", ">1"]).astype(str)
        f[f"{tf}_sweep"] = e[f"{tf}_sweep"].astype(str)
    F = pd.DataFrame(f)
    resid = (e["outcome"] - e["fair"]).to_numpy()
    var = (e["fair"] * (1 - e["fair"])).to_numpy()
    half = (e["year"] >= 2016).to_numpy()
    rows = []
    keys = list(F.columns)
    for a, b in combinations(keys, 2):
        if a.split("_")[0] == b.split("_")[0] and a != "fails":
            continue  # same timeframe pairs are mostly redundant
        g = pd.DataFrame({"base": e["base"], "a": F[a], "b": F[b], "r": resid, "v": var, "h": half, "y": e["year"]})
        agg = g.groupby(["base", "a", "b"]).agg(n=("r", "size"), s=("r", "sum"), v=("v", "sum"))
        agg = agg[agg["n"] >= 300]
        if agg.empty:
            continue
        h1 = g[~g["h"]].groupby(["base", "a", "b"])["r"].mean().rename("edge_1")
        h2 = g[g["h"]].groupby(["base", "a", "b"])["r"].mean().rename("edge_2")
        yr = g.groupby(["base", "a", "b", "y"])["r"].mean().unstack("y")  # per-year mean residual per cell
        sign = np.sign(agg["s"]).reindex(yr.index)
        agg = agg.join(np.sign(yr).eq(sign, axis=0).sum(axis=1).rename("years_same_sign"))
        agg = agg.join(h1).join(h2).reset_index()
        agg["fa"], agg["fb"] = a, b
        rows.append(agg)
    t = pd.concat(rows, ignore_index=True)
    t["edge"] = t["s"] / t["n"]
    t["z"] = t["s"] / np.sqrt(t["v"])
    t["p"] = [erfc(abs(z) / sqrt(2)) for z in t["z"]]
    t["bh"] = bh(t["p"].to_numpy())
    t["pass"] = t["bh"] & (t["edge"].abs() >= .03) & (np.sign(t["edge_1"]) == np.sign(t["edge_2"])) \
        & (t["edge_1"].abs() >= .02) & (t["edge_2"].abs() >= .02) & (t["years_same_sign"] >= 9)
    print(f"cells tested: {len(t)}  bh: {t['bh'].sum()}  pass (both halves >= 2pt, >= 9/12 years): {t['pass'].sum()}")
    pd.set_option("display.width", 220)
    cols = ["base", "fa", "a", "fb", "b", "n", "edge", "edge_1", "edge_2", "years_same_sign", "z"]
    top = t[t["pass"]].sort_values("z", key=abs, ascending=False)
    print(top[cols].head(40).round(3).to_string())
    print(top.groupby("base").size())
    t.to_parquet(PATH.with_name("pairs_scan.parquet"))
