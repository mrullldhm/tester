"""Round 3 (docs/studies/swing_confluence/README.md): H1 nested manipulation, H2 forming higher-TF candle,
H3 previous-day high/low. Dev only. Run: .venv/bin/python -m studies.swing_confluence.round3"""

from math import erfc, sqrt

import numpy as np
import pandas as pd

from cltester.data import load_period, to_ticks
from cltester.swings import build_candles
from studies.swing_confluence.scan import PATH, bh

ORDER = ["1m", "5m", "15m", "1h", "4h", "1d"]


def bar_features(df: pd.DataFrame) -> dict[str, np.ndarray]:
    h, l = to_ticks(df["high"]), to_ticks(df["low"])  # noqa: E741
    idx = np.arange(len(df))
    out = {}
    for tf in ["15m", "1h", "4h", "1d"]:
        cd = build_candles(df, tf)
        cid = np.searchsorted(cd.first, idx, side="right") - 1  # candle holding each bar
        run_lo = pd.Series(l).groupby(cid).cummin().to_numpy()  # forming candle's low through this bar
        run_hi = pd.Series(h).groupby(cid).cummax().to_numpy()
        prev_ok = cid >= 1
        prev_lo = np.where(prev_ok, cd.l[np.maximum(cid - 1, 0)], 0)
        prev_hi = np.where(prev_ok, cd.h[np.maximum(cid - 1, 0)], 0)
        out[f"{tf}_took_lo"] = np.where(prev_ok, run_lo < prev_lo, False)
        out[f"{tf}_took_hi"] = np.where(prev_ok, run_hi > prev_hi, False)
        out[f"{tf}_run_lo"], out[f"{tf}_run_hi"] = run_lo, run_hi
        out[f"{tf}_open"] = cd.avail[np.maximum(cid, 0)] > idx  # holding candle not complete at this bar's close
    day = pd.factorize(df["trading_day"])[0]
    dh = pd.Series(h).groupby(day).max().to_numpy()
    dl = pd.Series(l).groupby(day).min().to_numpy()
    out["pd_ok"] = day >= 1  # explicit availability: CL prices can be negative
    out["pdh"] = dh[np.maximum(day - 1, 0)]
    out["pdl"] = dl[np.maximum(day - 1, 0)]
    out["day_lo"] = pd.Series(l).groupby(day).cummin().to_numpy()  # through this bar
    out["day_hi"] = pd.Series(h).groupby(day).cummax().to_numpy()
    out["day"] = day
    return out


def stat(d: pd.DataFrame) -> dict:
    r = d["outcome"] - d["fair"]
    yr = r.groupby(d["year"]).mean()
    s = np.sign(r.mean())
    return {"n": len(d), "edge": r.mean(), "z": r.sum() / np.sqrt((d["fair"] * (1 - d["fair"])).sum()),
            "e1": r[d["year"] < 2016].mean(), "e2": r[d["year"] >= 2016].mean(),
            "yrs": int((np.sign(yr) == s).sum()), "short": r[d["side"] == -1].mean(), "long": r[d["side"] == 1].mean()}


def main() -> None:
    df = load_period("dev")
    bf = bar_features(df)
    e = pd.read_parquet(PATH)
    e = e[(e["outcome"] >= 0) & (~e["roll"]) & e["fair"].notna() & (e["leg"] >= 6)].reset_index(drop=True)
    i = e["bar"].to_numpy()
    side = e["side"].to_numpy()
    ev = e["price"].to_numpy()
    ts_ns = pd.DatetimeIndex(df["ts"]).as_unit("ns").asi8
    first = np.searchsorted(ts_ns, pd.DatetimeIndex(e["pt_ts"]).as_unit("ns").asi8)  # event candle's first bar
    before = np.maximum(first - 1, 0)
    rows = []

    # H1: the ordered base sequence HH-HL-HH-LL for a low event (mirror LL-LH-LL-HH for a high), from the
    # point-in-time state at the event: previous opposite point, previous same-side point (the HL), opposite point
    # (the HH), the event (the LL), strictly in time; HH above the earlier high, LL below the HL; no rule-5 replacement
    keys = ("opp2_ts", "prev_ts", "opp_ts", "pt_ts")
    t_o2, t_p2, t_o, t_e = (pd.DatetimeIndex(e[k]).as_unit("ns").asi8 for k in keys)
    ordered = (e["opp2_ts"].notna() & e["prev_ts"].notna()).to_numpy() & (t_o2 < t_p2) & (t_p2 < t_o) & (t_o < t_e)
    higher = np.where(side == 1, e["opp"] > e["opp2_price"], e["opp"] < e["opp2_price"])
    broke = np.where(side == 1, e["price"] < e["prev_price"], e["price"] > e["prev_price"])
    seq = ordered & higher & broke & ~e["replace"].to_numpy()
    for b in ORDER[:4]:
        mb = (e["base"] == b) & seq
        for t in ORDER[ORDER.index(b) + 1:]:
            for sw in (0, 1):
                for tr_name, tr in (("with", e[f"{t}_trend"] == 1), ("other", e[f"{t}_trend"] != 1)):
                    m = mb & (e[f"{t}_sweep"] == sw) & tr
                    rows.append({"h": "H1", "base": b, "cell": f"{b} HH-HL-HH-LL, {t} sweep={sw}, {t} trend {tr_name}",
                                 **stat(e[m])})
            m = mb & (e[f"{t}_sweep"] == 0) & (e[f"{t}_leg"] == 1)
            rows.append({"h": "H1", "base": b, "cell": f"{b} HH-HL-HH-LL, {t} low intact, {t} leg with", **stat(e[m])})
        rows.append({"h": "H1", "base": b, "cell": f"{b} HH-HL-HH-LL (all)", **stat(e[mb])})

    # H2: forming higher-TF candle already took the previous candle's same-side extreme; event is its extreme so far
    for t in ["15m", "1h", "4h", "1d"]:
        took = np.where(side == 1, bf[f"{t}_took_lo"][i], bf[f"{t}_took_hi"][i])
        own = np.where(side == 1, bf[f"{t}_run_lo"][i] == ev, bf[f"{t}_run_hi"][i] == ev)
        for b in ORDER[:ORDER.index(t)]:
            mb = (e["base"] == b).to_numpy() & bf[f"{t}_open"][i]  # still-forming candles only (Codex round 3)
            for tk in (0, 1):
                for ow in (0, 1):
                    m = mb & (took == tk) & (own == ow)
                    rows.append({"h": "H2", "base": b, "cell": f"{b} event, forming {t} took prev={tk}, "
                                 f"event is forming {t} extreme={ow}", **stat(e[m])})

    # H3: previous CME day's low (low event; high mirrored): first take today, retake, untouched
    lvl = np.where(side == 1, bf["pdl"][first], bf["pdh"][first])
    took_now = np.where(side == 1, ev < lvl, ev > lvl)
    taken_before = np.where(side == 1, bf["day_lo"][before] < lvl, bf["day_hi"][before] > lvl)
    taken_before &= bf["day"][before] == bf["day"][first]
    cat = np.select([took_now & ~taken_before, took_now & taken_before], ["first take", "retake"], "no take")
    ok = bf["pd_ok"][first] & (bf["day"][first] == bf["day"][i])
    for b in ORDER:
        for c in ("first take", "retake", "no take"):
            m = ok & (e["base"] == b).to_numpy() & (cat == c)
            rows.append({"h": "H3", "base": b, "cell": f"{b} event, previous-day level: {c}", **stat(e[m])})

    t = pd.DataFrame(rows)
    print(f"cells enumerated: {len(t)}")
    t = t[t["n"] >= 300].reset_index(drop=True)
    t["p"] = [erfc(abs(z) / sqrt(2)) for z in t["z"]]
    t["bh"] = bh(t["p"].to_numpy())
    t["pass"] = t["bh"] & (t["edge"].abs() >= .03) & (np.sign(t["e1"]) == np.sign(t["e2"])) & (t["yrs"] >= 9)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 80)
    print(f"cells tested: {len(t)}  bh: {t['bh'].sum()}  pass: {t['pass'].sum()}")
    cols = ["cell", "n", "edge", "e1", "e2", "yrs", "long", "short", "z", "pass"]
    for hyp in ("H1", "H2", "H3"):
        print(f"\n== {hyp}")
        print(t[t["h"] == hyp][cols].round(3).to_string(index=False))
    t.to_csv(PATH.with_name("round3_cells.csv"), index=False)


if __name__ == "__main__":
    main()
