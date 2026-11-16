"""Blind chart test: real 2021 (dev) moments where a 1m higher low breaks inside a 1m uptrend (short: mirror).
Charts stop at the break bar. Outcome (kept out of the page): price reaches the 1m swing high first (A, "it was a
manipulation") or falls one full leg below the broken low first (B, "real break"). Only moments where that bracket
is near 50/50 by geometry (fair 0.40-0.60) are used, so the picture, not the distance, must decide.
Run: .venv/bin/python -m studies.swing_confluence.blind.make"""

import json

import numpy as np
import pandas as pd

from cltester.data import load_period, to_ticks
from cltester.swings import swing_state
from studies.swing_confluence.build import RangeExtreme

HERE = __file__.rsplit("/", 1)[0]
PER_CELL = 10  # setups per (side, outcome): 40 total
MYT = "Asia/Kuala_Lumpur"


def candles(df: pd.DataFrame, end: int, minutes: int, count: int) -> list[list]:
    """Clock-aligned candles from 1m bars up to and including bar `end` (the last one may be unfinished)."""
    lo = max(0, end - minutes * (count + 2))
    w = df.iloc[lo:end + 1]
    key = w["ts"].dt.floor(f"{minutes}min")
    g = w.groupby(key, sort=True).agg(o=("open", "first"), h=("high", "max"), l=("low", "min"), c=("close", "last"))
    g = g.tail(count)
    return [[t.tz_convert(MYT).strftime("%H:%M"), r.o, r.h, r.l, r.c] for t, r in g.iterrows()]


def main() -> None:
    df = load_period("dev")
    df = df[df["trading_day"] >= pd.Timestamp("2020-12-20")].reset_index(drop=True)  # 2021 plus warm-up
    st = swing_state(df, "1m", prev=True, newest=True)
    h, l, c = to_ticks(df["high"]), to_ticks(df["low"]), to_ticks(df["close"])
    sym = pd.factorize(df["raw_symbol"])[0]
    day = pd.factorize(df["trading_day"])[0]
    rx = RangeExtreme(h, l)
    n = len(df)
    tk = {k: np.round(st[f"1m_{k}"].to_numpy() * 100) for k in ("sh", "sl", "sh2", "sl2")}
    newest = st["1m_newest"].to_numpy()
    rows = []
    for side in (1, -1):
        sh, sl, sh2, sl2 = tk["sh"][:-1], tk["sl"][:-1], tk["sh2"][:-1], tk["sl2"][:-1]
        t = np.arange(1, n)
        if side == 1:  # uptrend HH+HL, newest point the HH, bar t breaks the HL
            ok = (sh > sh2) & (sl > sl2) & (newest[:-1] == 1) & (l[1:] < sl)
            lvl, opp = sl, sh
        else:
            ok = (sh < sh2) & (sl < sl2) & (newest[:-1] == -1) & (h[1:] > sh)
            lvl, opp = sh, sl
        ok &= ~np.isnan(sh2) & ~np.isnan(sl2)
        idx = np.flatnonzero(ok)
        t, lv, op = t[idx], lvl[idx].astype(np.int64), opp[idx].astype(np.int64)
        leg = np.abs(op - lv)
        far = lv - side * leg  # one full leg beyond the broken level
        up_lvl, dn_lvl = (op, far) if side == 1 else (far, op)
        j_up = rx.first_above(t + 1, up_lvl)
        j_dn = rx.first_below(t + 1, dn_lvl)
        res = np.minimum(np.minimum(j_up, j_dn), n - 1)
        fair_up = (c[t] - dn_lvl + 1) / (up_lvl - dn_lvl + 2)
        a_first = (j_up < j_dn) if side == 1 else (j_dn < j_up)  # A: back to the swing point (manipulation)
        good = (leg >= 8) & (j_up != j_dn) & (np.minimum(j_up, j_dn) < n) & (day[res] == day[t]) \
            & (sym[res] == sym[t]) & (t >= 600) & (df["trading_day"].to_numpy()[t] >= np.datetime64("2021-01-01"))
        fair_a = fair_up if side == 1 else 1 - fair_up
        good &= (fair_a >= 0.4) & (fair_a <= 0.6)
        for k in np.flatnonzero(good):
            rows.append({"bar": int(t[k]), "side": side, "level": int(lv[k]), "target": int(op[k]), "far": int(far[k]),
                         "outcome": "A" if a_first[k] else "B", "fair_a": float(fair_a[k]), "day": int(day[t[k]]),
                         "minutes": int(res[k] - t[k])})
    cand = pd.DataFrame(rows)
    print(cand.groupby(["side", "outcome"]).size(), f"\nfair_a mean A {cand[cand.outcome == 'A'].fair_a.mean():.3f}"
          f" B {cand[cand.outcome == 'B'].fair_a.mean():.3f}")
    rng = np.random.default_rng(20261116)
    pick = []
    for (_, _), g in cand.groupby(["side", "outcome"]):
        g = g.sample(frac=1, random_state=int(rng.integers(1e9))).drop_duplicates("day")  # one per day per cell
        pick.append(g.head(PER_CELL))
    pick = pd.concat(pick).sample(frac=1, random_state=7).reset_index(drop=True)
    pick = pick.drop_duplicates("day").reset_index(drop=True)
    setups, answers = [], []
    for k, r in pick.iterrows():
        b = r["bar"]
        when = df["ts"].iloc[b].tz_convert(MYT)
        sid = f"s{k + 1:02d}"
        setups.append({"id": sid, "side": "long" if r["side"] == 1 else "short",
                       "when": when.strftime("%a %d %b %Y %H:%M MYT"),
                       "level": r["level"] / 100, "target": r["target"] / 100, "far": r["far"] / 100,
                       "m1": candles(df, b, 1, 90), "m5": candles(df, b, 5, 60), "h1": candles(df, b, 60, 36)})
        answers.append({"id": sid, "bar": b, "ts": str(df["ts"].iloc[b]), **{k2: r[k2] for k2 in
                        ("side", "level", "target", "far", "outcome", "fair_a", "minutes")}})
    with open(f"{HERE}/setups.json", "w") as f:
        json.dump(setups, f, separators=(",", ":"))
    pd.DataFrame(answers).to_csv(f"{HERE}/answers.csv", index=False)
    print(len(setups), "setups;", pd.DataFrame(answers).groupby(["side", "outcome"]).size().to_dict())


if __name__ == "__main__":
    main()
