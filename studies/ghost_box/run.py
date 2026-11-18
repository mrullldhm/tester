"""Ghost Box premise study (docs/strategies/ghost_box/README.md): does the overnight box hold after a ghost wick?

Box and wick from strategies.ghost_box.ghost_days (same code as the strategy). For each usable dev day, from a start
bar to the 13:29 CT bar (13:30 CT = 0DTE expiry analog) it records:
  close_held  no 5m candle closes outside the box (the PDF's exit rule never fires)
  end_inside  the 13:29 CT close is inside the box (a condor with short strikes at the walls keeps the full credit)
  touch_held  no 1m bar trades beyond the box (a short strike right at the wall is never in the money)
Start bar: the setup's signal bar for wick days, the last bar before 08:30 CT for every other day (setups start up
to 29 min later, which favours them). Days with a roll before 13:29 CT are skipped.
Groups: ghost-wick setups (with and without the PDF's gap / width filters) vs "intact" days: no 5m close outside
the box from 08:00 to the start bar, wick or not (the fair baseline: a box still standing at 08:30).
Dev only (validation and holdout never loaded). Descriptive, in-sample, no P&L (no options prices).
Run: .venv/bin/python -m studies.ghost_box.run"""

import numpy as np
import pandas as pd

from cltester.config import ROOT
from cltester.data import load_period, to_ticks
from cltester.swings import build_candles
from strategies.ghost_box import BOX_END, SETTLE, WIN_START, ghost_days

OUT = ROOT / "studies" / "ghost_box"
USABLE = ("no_push", "both", "broken", "broken_after", "late", "setup")


def outcomes(df: pd.DataFrame, days: pd.DataFrame) -> pd.DataFrame:
    sess = df["sess_minute"].to_numpy()
    day = pd.factorize(df["trading_day"])[0]
    sym = pd.factorize(df["raw_symbol"])[0]
    h, lo, c = (to_ticks(df[k]) for k in ("high", "low", "close"))
    cd = build_candles(df, "5m")
    c_day, c_start = day[cd.first], (sess[cd.first] // 5) * 5
    starts = np.r_[0, np.flatnonzero(day[1:] != day[:-1]) + 1]
    ends = np.r_[starts[1:], len(df)]
    rec = []
    for d, r in enumerate(days.to_dict("records")):
        if r["status"] not in USABLE:
            continue
        a = starts[d]
        idx = a + np.flatnonzero(sess[a:ends[d]] < SETTLE)
        pre = idx[sess[idx] < WIN_START]
        start = int(r["signal"]) if r["status"] == "setup" else int(pre[-1])
        top, bot = int(r["top"]), int(r["bot"])
        k_day = (c_day == d) & (c_start >= BOX_END) & (c_start < SETTLE)
        early = k_day & (cd.avail <= start)
        late = k_day & (cd.avail > start)
        out5 = (cd.c > top) | (cd.c < bot)
        if len(np.unique(sym[idx])) != 1:
            continue  # roll before 13:29 CT: unadjusted prices would fake a break
        hold = idx[idx > start]
        last = int(idx[-1])
        rec.append({**{k: r[k] for k in ("day", "status", "side", "width_pct", "gap_pct")},
                    "intact": not out5[early].any(),
                    "close_held": not out5[late].any(),
                    "end_inside": bot <= c[last] <= top,
                    "touch_held": not ((h[hold] > top).any() or (lo[hold] < bot).any()),
                    "dow": pd.Timestamp(r["day"]).day_name()[:3]})
    return pd.DataFrame(rec)


def rates(x: pd.DataFrame) -> str:
    if not len(x):
        return "| 0 | - | - | - |"
    return (f"| {len(x)} | {x.close_held.mean():.1%} | {x.end_inside.mean():.1%} | {x.touch_held.mean():.1%} |")


def main() -> None:
    df = load_period("dev")
    days = ghost_days(df)
    o = outcomes(df, days)
    o.to_csv(OUT / "days.csv", index=False)
    wide, flat = o.width_pct >= 0.4, o.gap_pct < 0.5
    setup = o.status == "setup"
    pushed = o.status.isin(["setup", "late", "both"])
    groups = [
        ("ghost wick, PDF filters (the trade set)", setup & wide & flat),
        ("ghost wick, width only (no gap filter)", setup & wide),
        ("ghost wick, gap >= 0.5% (filtered out)", setup & wide & ~flat),
        ("intact box at 08:30, PDF filters, any wick", o.intact & wide & flat),
        ("intact box at 08:30, PDF filters, no wick", o.intact & wide & flat & ~pushed),
        ("intact box at 08:30, no filters, any wick", o.intact),
        ("no push 08:00-09:00, PDF filters", (o.status == "no_push") & wide & flat),
    ]
    lines = ["| Group | Days | 5m close never outside | 13:29 close inside | never traded outside |",
             "|---|---|---|---|---|"]
    lines += [f"| {name} {rates(o[m])}" for name, m in groups]
    print("\n".join(lines))
    s = o[setup & wide & flat]
    print("\nTrade set by side")
    for sd, nm in ((-1, "wick above (short)"), (1, "wick below (long)")):
        print(nm, rates(s[s.side == sd]))
    print("\nTrade set by year")
    for y, g in s.groupby(pd.DatetimeIndex(s.day).year):
        b = o[o.intact & wide & flat & (pd.DatetimeIndex(o.day).year == y)]
        print(y, rates(g), "baseline", rates(b))
    print("\nTrade set by weekday (EIA crude stocks: Wed 09:30 CT)")
    for dw, g in s.groupby("dow"):
        print(dw, rates(g))
    print("\nStatus counts (usable dev days)")
    print(o.status.value_counts().to_string())


if __name__ == "__main__":
    main()
