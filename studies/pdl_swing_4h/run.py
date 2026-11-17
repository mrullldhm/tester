"""Swing point through the previous day's low/high: shape count (docs/studies/pdl_swing_4h/README.md).
Short: swing low vs PDL. Long: mirror, swing high vs PDH. Timeframes 4h and 1h.
Run: .venv/bin/python -m studies.pdl_swing_4h.run"""

import numpy as np
import pandas as pd

from cltester.config import ROOT
from cltester.data import add_session, load_bars, to_ticks
from cltester.swings import build_candles, detect

END = "2025-01-01"  # holdout is never loaded
OUT = ROOT / "studies" / "pdl_swing_4h"
TFS = ("4h", "1h")
SIDES = ("short", "long")
SHAPES = ["C3", "C4", "C4 unknown", "C4 wrong order", "none"]


def load() -> pd.DataFrame:
    df = add_session(load_bars("2010-06-01", END))
    return df[(df["trading_day"] >= "2010-06-01") & (df["trading_day"] < END)].reset_index(drop=True)


def events(df: pd.DataFrame, tf: str = "4h", side: str = "short") -> pd.DataFrame:
    """One row per new swing point on the setup side (short: swing low, long: swing high).
    Long is the short logic on negated prices: highs become lows, PDH becomes PDL, so every rule mirrors exactly."""
    s = 1 if side == "short" else -1
    tday = df["trading_day"].to_numpy()
    cd = build_candles(df, tf)
    _, st = detect(cd)
    # in the short frame: "lo" = the side the setup point sits on, "hi" = the opposite side
    h1, l1 = (to_ticks(df["high"]), to_ticks(df["low"])) if s == 1 else (-to_ticks(df["low"]), -to_ticks(df["high"]))
    o1 = s * to_ticks(df["open"])
    hi, lo = (cd.h, cd.l) if s == 1 else (-cd.l, -cd.h)
    pt, opp = ("sl", "sh") if s == 1 else ("sh", "sl")
    daily = df.groupby("trading_day").agg(lo=("low", "min"), hi=("high", "max"))
    days = daily.index.to_numpy()
    lvl = to_ticks(daily["lo"]) if s == 1 else -to_ticks(daily["hi"])  # PDL, or -PDH
    p_c = st[f"{pt}_candle"]
    rows = []
    seen = -1  # newest point candle already counted: a rule-4 restore of an older point is not a new event
    for k in range(len(cd)):
        c2 = p_c[k]
        if c2 <= seen:
            continue
        seen = c2
        # opposite point before it: the current one unless it sits on/after c2 (outside candle, setup point first)
        oc = st[f"{opp}_candle"][k]
        before = oc >= 0 and (oc < c2 or st["newest"][k] == -s)
        key = opp if before else f"{opp}2"
        ok0 = st[f"{key}_candle"][k] >= 0
        p0 = s * st[f"{key}_price"][k]
        p = s * st[f"{pt}_price"][k]
        day = tday[cd.first[c2]]
        pos = np.searchsorted(days, day)
        level = lvl[pos - 1] if pos > 0 else 0
        if pos == 0 or not ok0:
            group = "no level"  # first day or no opposite point yet: C2 only (C2 ignores the level)
        else:
            group = "level not reached" if p > level else "C1 cross" if p0 > level else "other"
        shape = "none"
        c3, c4 = c2 + 1, c2 + 2
        if c4 < len(cd) and hi[c3] >= hi[c2] and lo[c4] <= p:
            if hi[c4] < hi[c3]:
                shape = "C3"
            else:
                bars = np.arange(cd.first[c4], cd.last[c4] + 1)
                t_hi = bars[np.argmax(h1[bars] >= hi[c3])]
                t_lo = bars[np.argmax(l1[bars] <= p)]
                if t_hi == t_lo:  # same minute: an open beyond a threshold touched it first
                    t_hi -= o1[t_hi] >= hi[c3]
                    t_lo -= o1[t_lo] <= p
                shape = "C4" if t_hi < t_lo else "C4 unknown" if t_hi == t_lo else "C4 wrong order"
        rows.append({"tf": tf, "side": side, "ts": cd.ts[c2], "day": day, "group": group, "shape": shape,
                     "point": s * p, "prev_point": s * p0, "level": s * level})
    ev = pd.DataFrame(rows)
    ev["period"] = np.where(ev["day"] < "2022-01-01", "dev", "validation")
    return ev


def table(ev: pd.DataFrame) -> pd.DataFrame:
    """Rows: C1 cross, C2 any (no level filter); columns: shapes per period."""
    out = {}
    for period, g in ev.groupby("period"):
        for name, sub in (("C1 cross", g[g["group"] == "C1 cross"]), ("C2 any", g)):
            c = sub["shape"].value_counts().reindex(SHAPES, fill_value=0)
            out[(period, name)] = {**c.to_dict(), "events": len(sub)}
    return pd.DataFrame(out).T


def main() -> None:
    df = load()
    allev = []
    for tf in TFS:
        for side in SIDES:
            ev = events(df, tf, side)
            allev.append(ev)
            lvl = "PDL" if side == "short" else "PDH"
            print(f"\n== {tf} {side} (C1 = crosses {lvl}) ==\n{table(ev)}")
    pd.concat(allev).to_csv(OUT / "events.csv", index=False)


if __name__ == "__main__":
    main()
