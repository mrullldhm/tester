"""Level regime study (docs/studies/level_regime/README.md). Run: .venv/bin/python -m studies.level_regime.run"""

import numpy as np
import pandas as pd

from cltester.config import ROOT, TICK
from cltester.data import add_session, load_bars, to_ticks
from cltester.indicators import tf_candles
from strategies.purple_levels import Strategy as Levels
from studies.swing_confluence.build import RangeExtreme

END = "2025-01-01"  # trading days before 2025: holdout is never loaded
FAMILIES = ("pd", "pw", "sw4h", "sw1d")
OUT = ROOT / "studies" / "level_regime"


def load() -> pd.DataFrame:
    df = add_session(load_bars("2010-06-01", END))
    return df[(df["trading_day"] >= "2010-06-01") & (df["trading_day"] < END)].reset_index(drop=True)


def events(df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    h1, l1, c1 = to_ticks(df["high"]), to_ticks(df["low"]), to_ticks(df["close"])
    sym1 = pd.factorize(df["raw_symbol"])[0]
    day1 = pd.factorize(df["trading_day"])[0]
    rx = RangeExtreme(h1, l1)
    cd = tf_candles(df, "5m")
    cd = cd[cd["avail"].to_numpy() < n].reset_index(drop=True)
    h, l = (np.round(cd[k].to_numpy() / TICK).astype(np.int64) for k in ("high", "low"))  # noqa: E741
    o = np.round(cd["open"].to_numpy() / TICK).astype(np.int64)
    first, last = cd["first"].to_numpy(), cd["last"].to_numpy()
    days, day_id = np.unique(cd["day"].to_numpy(), return_inverse=True)
    starts = np.flatnonzero(np.r_[True, day_id[1:] != day_id[:-1]])
    ends = np.r_[starts[1:], len(cd)]
    raw = df.groupby("trading_day").agg(hi=("high", "max"), lo=("low", "min"))
    rng = np.round((raw["hi"] - raw["lo"]).to_numpy() / TICK).astype(np.int64)
    pos = raw.index.searchsorted(days)
    prev_range = np.where(pos > 0, rng[np.maximum(pos - 1, 0)], 0)
    rows = []
    for fam in FAMILIES:
        levels = Levels.day_levels(df, cd, days, day_id, starts, fam)
        for a, b in zip(starts, ends, strict=True):
            d = day_id[a]
            x = max(3, int(round(prev_range[d] * 0.1)))
            for lev in levels[d]:
                side = 1 if o[a] > lev else -1 if o[a] < lev else 0
                t = -1
                for k in range(a, b):
                    if side == 0:
                        side = 1 if l[k] > lev else -1 if h[k] < lev else 0
                        continue
                    if (side == 1 and l[k] <= lev) or (side == -1 and h[k] >= lev):
                        t = k
                        break
                if t < 0:
                    continue
                bars = np.arange(first[t], last[t] + 1)
                hit = bars[(l1[bars] <= lev) if side == 1 else (h1[bars] >= lev)]
                if len(hit) == 0:
                    continue
                i = int(hit[0])  # the 1m bar that touched
                if i + 1 >= n:
                    continue
                up, dn = (lev + x, lev - x)
                # the search starts after the touch minute: price starts at its close, not at the level. Strict
                # breaks: absorbing barriers dn-1 and up+1 (random-walk fair rate). A close outside: no baseline.
                if not dn <= c1[i] <= up:
                    continue
                fair_up = (c1[i] - dn + 1) / (up - dn + 2)
                j_up = int(rx.first_above(np.array([i + 1]), np.array([up]))[0])
                j_dn = int(rx.first_below(np.array([i + 1]), np.array([dn]))[0])
                if j_up == j_dn or min(j_up, j_dn) >= n:
                    continue
                r = min(j_up, j_dn)
                if day1[r] != day1[i] or sym1[r] != sym1[i]:
                    continue
                bounce = (j_up < j_dn) if side == 1 else (j_dn < j_up)
                depth = ((lev - l1[i]) if side == 1 else (h1[i] - lev)) / x  # how far the touch bar went through
                gap = False
                for q in range(t + 1, min(t + 5, b)):
                    if q - 2 < max(t - 1, a):
                        continue
                    if (h[q - 2] < l[q]) if side == 1 else (l[q - 2] > h[q]):
                        gap = True
                        break
                rows.append({"family": fam, "day": days[d], "year": pd.Timestamp(days[d]).year, "side": side,
                             "x": x, "bounce": bool(bounce),
                             "fair": fair_up if side == 1 else 1 - fair_up, "depth": depth, "gap": gap,
                             "minutes": int((df["ts"].iat[r] - df["ts"].iat[i]).total_seconds() // 60)})
    return pd.DataFrame(rows)


def context(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("trading_day").agg(hi=("high", "max"), lo=("low", "min"))
    g["range"] = np.round((g["hi"] - g["lo"]) / TICK)
    g["took_prev"] = (g["hi"] > g["hi"].shift()) | (g["lo"] < g["lo"].shift())
    g["year"] = pd.DatetimeIndex(g.index).year
    return g.iloc[1:].groupby("year").agg(median_range=("range", "median"), took_prev=("took_prev", "mean"))


def per_year(e: pd.DataFrame) -> pd.DataFrame:
    e = e.assign(r=e["bounce"] - e["fair"], v=e["fair"] * (1 - e["fair"]))
    y = e.groupby("year").agg(n=("bounce", "size"), bounce=("bounce", "mean"), fair=("fair", "mean"),
                              edge=("r", "mean"), gap_rate=("gap", "mean"), depth=("depth", "median"),
                              minutes=("minutes", "median"))
    y["z"] = e.groupby("year")["r"].sum() / np.sqrt(e.groupby("year")["v"].sum())
    y["edge_if_gap"] = e[e["gap"]].groupby("year")["r"].mean()
    y["edge_no_gap"] = e[~e["gap"]].groupby("year")["r"].mean()
    return y


def main() -> None:
    df = load()
    e = events(df)
    e.to_csv(OUT / "events.csv", index=False)
    pd.set_option("display.width", 200)
    print(f"{len(e)} first touches, {e['year'].min()}-{e['year'].max()}")
    ctx = context(df)
    print("\nAll level sets:\n", per_year(e).join(ctx).round(3).to_string())
    e = e.assign(r=e["bounce"] - e["fair"])
    fam = e.groupby(["family", "year"])["r"].mean().unstack("family")
    print("\nBounce edge vs fair by level set:\n", fam.round(3).to_string())
    era = e.assign(era=np.where(e["year"] >= 2022, "2022-24", "2010-21")).groupby(["family", "era"])
    print("\nBy era:\n", era.agg(n=("r", "size"), bounce=("bounce", "mean"), fair=("fair", "mean"),
                                  edge=("r", "mean")).round(3).to_string())


if __name__ == "__main__":
    main()
