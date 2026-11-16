"""Single-feature scan: hold rate minus fair rate per (base, feature, value). Dev only, rolls excluded."""

import numpy as np
import pandas as pd

from cltester.config import ROOT
from studies.swing_confluence.build import CONTEXT

PATH = ROOT / "data" / "studies" / "swing_confluence_dev.parquet"


def bucket_pos(x: pd.Series) -> pd.Series:
    labels = ["<0", "0-.25", ".25-.5", ".5-.75", ".75-1", ">1"]
    return pd.cut(x, [-np.inf, 0, 0.25, 0.5, 0.75, 1, np.inf], labels=labels)


def cells(e: pd.DataFrame) -> pd.DataFrame:
    feats = {"retrace": pd.cut(e["retrace"], [0, .382, .618, 1, 1.618, np.inf]).astype(str),
             "replace": e["replace"].astype(str), "ct_hour": e["ct_hour"].astype(str)}
    for tf in CONTEXT:
        feats[f"{tf}_trend"] = e[f"{tf}_trend"].astype(str)
        feats[f"{tf}_leg"] = e[f"{tf}_leg"].astype(str)
        feats[f"{tf}_pos"] = bucket_pos(e[f"{tf}_pos"]).astype(str)
        feats[f"{tf}_sweep"] = e[f"{tf}_sweep"].astype(str)
    rows = []
    resid = e["outcome"] - e["fair"]
    for name, v in feats.items():
        d = pd.DataFrame({"base": e["base"], "v": v, "r": resid, "fair": e["fair"], "year": e["year"]})
        for (b, val), g in d.groupby(["base", "v"], observed=True):
            n = len(g)
            if n < 300:
                continue
            var = (g["fair"] * (1 - g["fair"])).sum()  # binomial variance under the fair model
            z = g["r"].sum() / np.sqrt(max(var, 1e-9))
            yr = g.groupby("year")["r"].mean()
            rows.append({"base": b, "feature": name, "value": val, "n": n, "edge": g["r"].mean(), "z": z,
                         "years_same_sign": int((np.sign(yr) == np.sign(g["r"].mean())).sum()), "years": len(yr)})
    return pd.DataFrame(rows)


def bh(p: np.ndarray, q: float = 0.05) -> np.ndarray:
    order = np.argsort(p)
    ranked = p[order] * len(p) / (np.arange(len(p)) + 1)
    passed = np.zeros(len(p), dtype=bool)
    below = np.flatnonzero(ranked <= q)
    if len(below):
        passed[order[: below.max() + 1]] = True
    return passed


if __name__ == "__main__":
    from math import erfc, sqrt
    e = pd.read_parquet(PATH)
    e = e[(e["outcome"] >= 0) & (~e["roll"]) & e["fair"].notna()]
    t = cells(e)
    t["p"] = [erfc(abs(z) / sqrt(2)) for z in t["z"]]
    t["bh"] = bh(t["p"].to_numpy())
    t["pass"] = t["bh"] & (t["edge"].abs() >= 0.03) & (t["years_same_sign"] >= 9)
    print(f"cells tested: {len(t)}  bh-significant: {t['bh'].sum()}  full pass: {t['pass'].sum()}")
    pd.set_option("display.width", 200)
    print(t[t["pass"]].sort_values("edge", key=abs, ascending=False).head(60).round(3).to_string())
