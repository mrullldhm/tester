"""RLM trade study: every filled trade of one version joined to its signal features, then win/loss correlations.

Features are the predeclared list in docs/strategies/rlm/README.md (step 4). Outcome: net $ and R (net / risk $).
Per feature: quintile (or category) table of trades, win rate, avg R, PF, and a day-clustered bootstrap CI of avg R.
Any filter read off this table is a NEW trial; it needs data it was not found on (validation once, or forward).
Run: .venv/bin/python -m studies.rlm.trades --set sig_tf=15m exit=r2 ... [--period dev] [--tag name]
"""

import argparse

import numpy as np
import pandas as pd

from cltester.config import ROOT, TICK_VALUE
from cltester.data import Bars, load_period
from cltester.engine import Fills, backtest
from strategies.rlm import Strategy

OUT = ROOT / "studies" / "rlm" / "trades"
FEATURES = ["maxw", "touches", "score", "polar", "age", "crosses", "band_atr", "clv", "risk", "ct_hour", "side",
            "atr14", "pen_atr", "dist_atr"]


def parse(items: list[str]) -> dict:
    out = {}
    for it in items:
        k, v = it.split("=")
        try:
            out[k] = float(v) if "." in v else int(v)
        except ValueError:
            out[k] = v
    return out


def study(df: pd.DataFrame, p: dict, through: int = 0) -> pd.DataFrame:
    s = Strategy()
    o = s.orders(df, p).set_index("bar")
    tr = backtest(Bars.from_frame(df), s.signals(df, p), Fills(through=through), s.manage)
    t = tr.drop(columns="path").join(o, on="signal_bar", rsuffix="_o")
    rng = (t["h"] - t["l"]).replace(0, np.nan)
    t["clv"] = np.where(t["side"] == 1, (t["cl"] - t["l"]) / rng, (t["h"] - t["cl"]) / rng)
    t["band_atr"] = (t["hi"] - t["lo"]) / t["atr34"]
    t["pen_atr"] = np.where(t["side"] == 1, t["hi"] - t["l"], t["h"] - t["lo"]) / t["atr34"]  # wick depth into band
    t["dist_atr"] = np.where(t["side"] == 1, t["cl"] - t["hi"], t["lo"] - t["cl"]) / t["atr34"]  # close away
    t["risk"] = t["R"]
    t["ct_hour"] = t["ct_min"] // 60
    t["Rmult"] = t["net"] / (t["R"] * TICK_VALUE)
    t["year"] = pd.to_datetime(t["trading_day"]).dt.year
    return t


def table(t: pd.DataFrame, f: str, rng: np.random.Generator, boots: int = 300) -> pd.DataFrame:
    x = t[f]
    grp = pd.qcut(x.rank(method="first"), 5, labels=False) if x.nunique() > 6 else x
    rows = []
    for g, d in t.groupby(grp):
        days = d["trading_day"].to_numpy()
        ud = np.unique(days)
        by = d.groupby("trading_day")["Rmult"].agg(["sum", "count"])
        bs = []
        for _ in range(boots):  # day-clustered bootstrap of avg R
            pick = by.iloc[rng.integers(0, len(by), len(by))]
            bs.append(pick["sum"].sum() / pick["count"].sum())
        win, loss = d.loc[d["net"] > 0, "net"].sum(), -d.loc[d["net"] < 0, "net"].sum()
        rows.append({"feature": f, "bin": g, "lo": round(float(d[f].min()), 3), "hi": round(float(d[f].max()), 3),
                     "trades": len(d), "days": len(ud), "win": round((d["net"] > 0).mean(), 3),
                     "avgR": round(d["Rmult"].mean(), 3), "ci05": round(np.quantile(bs, 0.05), 3),
                     "ci95": round(np.quantile(bs, 0.95), 3), "pf": round(win / loss, 3) if loss else np.nan,
                     "net": round(d["net"].sum())})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--period", default="dev", choices=["dev"])
    ap.add_argument("--through", type=int, default=0)
    ap.add_argument("--tag", default="study")
    a = ap.parse_args()
    p = {**Strategy.PARAMS, **parse(a.set)}
    df = load_period(a.period)
    t = study(df, p, a.through)
    OUT.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT / f"{a.tag}_{a.period}.csv", index=False)
    rng = np.random.default_rng(7)
    tabs = pd.concat([table(t, f, rng) for f in FEATURES], ignore_index=True)
    tabs.to_csv(OUT / f"{a.tag}_{a.period}_features.csv", index=False)
    print(p, f"\ntrades {len(t)} net {t['net'].sum():.0f} avgR {t['Rmult'].mean():.3f} (in-sample, {a.period})")
    with pd.option_context("display.width", 200, "display.max_rows", 200):
        print(tabs.to_string(index=False))


if __name__ == "__main__":
    main()
