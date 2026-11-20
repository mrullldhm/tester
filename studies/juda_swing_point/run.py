"""Juda Swing Point (15m swing break + manipulation candle): setup count (owner idea, 2026-11-18).

Long (short is the mirror):
  1. 15m candles, EMA 10 > EMA 20 > EMA 50 on 15m closes (checked at the confirmation candle close; variant: also
     at the manipulation candle close).
  2. Owner swing rule (cltester.swings.detect). Newest point is a swing high P.
  3. Invalidation: a later candle j touches/breaks P (high >= P) before any swing low forms after P.
  4. From candle j on (j itself included), while the structure is unchanged (newest point still P: no swing low,
     no new swing high confirmed), the manipulation candle m: high >= high[m-1] first, then low < low[m-1]
     (order from the 1m bars inside m).
  5. Confirmation candle m+1: low > low[m] (no touch). That also makes m a swing low candidate (rules 2: left
     low >= low[m], right low > low[m]).
Short runs the same code on negated prices (highs become lows), so every rule mirrors exactly.
Holdout (2025+) is never loaded. Setups are counted on dev + validation; outcomes are computed for dev setups only
(validation outcomes are never calculated or written). Outcome race is descriptive, not a backtest: entry at the
confirmation close (the availability bar's close when the candle's last minute is missing), stop = manipulation
low, first touch of +1R / +2R vs stop, flat 15:10 CT. A setup gets a race only if its confirmation closes before
15:10 CT and the manipulation candle through the entry bar is one contract; a race reaching a contract change before
stop/target ends as 'roll' (unadjusted prices), not 'flat'.
Run: .venv/bin/python -m studies.juda_swing_point.run"""

import numpy as np
import pandas as pd

from cltester.config import ROOT
from cltester.data import add_session, load_bars, to_ticks
from cltester.indicators import ema
from cltester.swings import HIGH, LOW, Candles, build_candles, detect

END = "2025-01-01"  # holdout is never loaded
OUT = ROOT / "studies" / "juda_swing_point"
FLAT = 1330  # 15:10 CT in minutes since the 17:00 CT open
DEV_END = "2022-01-01"  # outcomes are computed only before this trading day


def load() -> pd.DataFrame:
    df = add_session(load_bars("2010-05-31", END))
    return df[(df["trading_day"] >= "2010-06-01") & (df["trading_day"] < END)].reset_index(drop=True)


def first_order(h1, l1, o1, a, b, hi_lvl, lo_lvl) -> str:
    """Inside 1m bars a..b: did high >= hi_lvl print before low < lo_lvl? 'hi', 'lo' first, 'unknown', or 'none'."""
    th = np.flatnonzero(h1[a:b + 1] >= hi_lvl)
    tl = np.flatnonzero(l1[a:b + 1] < lo_lvl)
    if not len(th) or not len(tl):
        return "none"
    th, tl = a + int(th[0]), a + int(tl[0])
    if th == tl:  # same minute: an open already beyond a level touched it first
        th -= o1[th] >= hi_lvl
        tl -= o1[tl] < lo_lvl
    return "hi" if th < tl else "lo" if tl < th else "unknown"


def confirmation_entry(cd: Candles, c1: np.ndarray, k: int) -> tuple[int, int, bool]:
    """(availability bar, entry ticks, delayed?) for confirmation candle k. A missing closing minute delays
    availability to the next observed bar; entry is that bar's close, the first tradable price once k is known."""
    start = int(cd.avail[k])
    entry = int(c1[start]) if start < len(c1) else int(cd.c[k])
    return start, entry, bool(start != cd.last[k])


def race_status(sess, sym, day, first_m: int, start: int, risk: int) -> str:
    """Why a setup does or does not get an outcome race: 'ok', 'validation', 'late', 'roll_setup', 'no_risk'."""
    if risk <= 0:
        return "no_risk"
    if str(day[start])[:10] >= DEV_END:
        return "validation"
    if sess[start] >= FLAT or day[start] != day[first_m]:
        return "late"
    if sym[first_m] != sym[start] or len(set(sym[first_m:start + 1])) != 1:
        return "roll_setup"
    return "ok"


def race(h1, l1, c1, sess, day, sym, start, entry, stop) -> dict:
    """From 1m bar start+1: first of stop / +1R / +2R, flat at 15:10 CT or day change, 'roll' at a contract change.
    Same bar: stop first."""
    risk = entry - stop
    out = {"r1": "flat", "r2": "flat", "flat_r": np.nan}
    n = len(h1)
    e = start + 1
    while e < n and day[e] == day[start] and sess[e] < FLAT and sym[e] == sym[start]:
        e += 1
    rolled = e < n and day[e] == day[start] and sess[e] < FLAT and sym[e] != sym[start]
    hi, lo = h1[start + 1:e], l1[start + 1:e]
    st = np.flatnonzero(lo <= stop)
    st = st[0] if len(st) else np.inf
    for k, mult in (("r1", 1), ("r2", 2)):
        tp = np.flatnonzero(hi >= entry + mult * risk)
        tp = tp[0] if len(tp) else np.inf
        out[k] = "stop" if st <= tp and st < np.inf else "target" if tp < np.inf else "roll" if rolled else "flat"
    if e - 1 > start and not rolled:
        out["flat_r"] = (c1[e - 1] - entry) / risk
    return out


def events(df: pd.DataFrame, side: int) -> pd.DataFrame:
    cd = build_candles(df, "15m")
    tday, sess = df["trading_day"].to_numpy(), df["sess_minute"].to_numpy()
    sym = pd.factorize(df["raw_symbol"])[0]
    h1, l1, o1, c1 = (to_ticks(df[k]) for k in ("high", "low", "open", "close"))
    if side == -1:
        cd = cd.mirrored()
        h1, l1, o1, c1 = -l1, -h1, -o1, -c1
    _, st = detect(cd)
    e10, e20, e50 = (ema(cd.c.astype(float), n).to_numpy() for n in (10, 20, 50))
    stack_ok = (e10 > e20) & (e20 > e50)
    stack_ok[:50] = False  # EMA warm-up
    h, lo = cd.h, cd.l
    n = len(cd)
    rows, used = [], set()
    for j in range(2, n):
        s = j - 1  # state known at candle j's close
        if st["newest"][s] != HIGH:
            continue
        p, pc = st["sh_price"][s], st["sh_candle"][s]
        if pc < 0 or pc in used or h[j] < p:
            continue
        used.add(pc)
        attempts, why, m_hit = 0, "structure changed", -1
        for m in range(j, n - 1):
            if m > j and (st["newest"][m - 1] != HIGH or st["sh_candle"][m - 1] != pc):
                why = "swing low formed" if st["newest"][m - 1] == LOW else "new swing high"
                break
            if h[m] < h[m - 1] or lo[m] >= lo[m - 1]:
                continue
            order = first_order(h1, l1, o1, cd.first[m], cd.last[m], h[m - 1], lo[m - 1])
            if order != "hi":
                if order == "unknown":
                    why = "manip order unknown"
                    m_hit = m
                    break
                continue  # low first: not a manipulation candle, keep waiting
            attempts += 1
            if lo[m + 1] > lo[m]:
                why, m_hit = "setup", m
                break
            # confirmation broke the low: keep waiting (structure check decides the end)
        else:
            why = "data end"
        rec = {"side": "long" if side == 1 else "short", "sh_ts": cd.ts[pc], "break_ts": cd.ts[j],
               "why": why, "attempts": attempts, "m_ts": pd.NaT, "same_candle": False, "ema_conf": False,
               "ema_manip": False, "ema_break": bool(stack_ok[j]), "wait": np.nan, "risk": np.nan,
               "race": "no_setup"}
        if m_hit >= 0:
            m = m_hit
            rec.update(m_ts=cd.ts[m], same_candle=m == j, ema_conf=bool(stack_ok[m + 1]),
                       ema_manip=bool(stack_ok[m] and stack_ok[m + 1]), wait=m - j)
            if why == "setup":
                start, entry, rec["entry_delayed"] = confirmation_entry(cd, c1, m + 1)
                stop = lo[m]
                rec.update(risk=int(entry - stop), conf_ts=cd.ts[m + 1], day=tday[start]
                           if start < len(df) else pd.NaT, conf_sess=sess[cd.last[m + 1]])
                if start >= len(df):
                    rec["race"] = "data_end"
                else:
                    rec["race"] = race_status(sess, sym, tday, int(cd.first[m]), start, int(entry - stop))
                    if rec["race"] == "ok":
                        rec.update(race(h1, l1, c1, sess, tday, sym, start, entry, stop))
        rows.append(rec)
    ev = pd.DataFrame(rows)
    ev["period"] = np.where(ev["break_ts"] < pd.Timestamp("2022-01-01", tz="UTC"), "dev", "validation")
    ev["year"] = ev["break_ts"].dt.year
    return ev


def main() -> None:
    df = load()
    ev = pd.concat([events(df, 1), events(df, -1)], ignore_index=True)
    ev.to_csv(OUT / "events.csv", index=False)
    pd.set_option("display.width", 200)
    print("\n== funnel per period/side ==")
    f = ev.groupby(["period", "side"]).agg(
        invalidations=("why", "size"),
        setups_no_ema=("why", lambda w: (w == "setup").sum()),
        setups_ema_conf=("ema_conf", lambda e: (e & (ev.loc[e.index, "why"] == "setup")).sum()),
        setups_ema_manip_conf=("ema_manip", lambda e: (e & (ev.loc[e.index, "why"] == "setup")).sum()),
        order_unknown=("why", lambda w: (w == "manip order unknown").sum()))
    print(f)
    print("\nend reasons:\n", ev.groupby(["period", "side", "why"]).size().unstack(fill_value=0))
    s = ev[(ev["why"] == "setup") & ev["ema_conf"]]
    print("\n== setups (EMA at confirmation) per year ==\n", s.groupby(["year", "side"]).size().unstack(fill_value=0))
    print("\nmanip = break candle itself:", s.groupby("side")["same_candle"].mean().round(2).to_dict())
    print("wait candles (break to manip) median:", s.groupby("side")["wait"].median().to_dict())
    print("risk ticks quantiles:\n", s.groupby("side")["risk"].quantile([.25, .5, .75, .95]).unstack())
    ct_hour = (s["conf_sess"] // 60 + 17) % 24
    print("\nconfirmation close hour CT:\n", pd.crosstab(ct_hour, s["side"]))
    d = s[s["period"] == "dev"]
    print("\nrace eligibility (setups, EMA at confirmation):\n", pd.crosstab(s["period"], s["race"]))
    d = d[d["race"] == "ok"]
    print("\n== dev only, descriptive race (market at confirmation close, no fees; eligible setups) ==")
    assert s.loc[s["period"] == "validation", ["r1", "r2"]].isna().all().all() if "r1" in s else True
    for k in ("r1", "r2"):
        print(k, "\n", pd.crosstab(d["side"], d[k], margins=True))
    print("mean R at flat-time close (no stop/target):", d.groupby("side")["flat_r"].mean().round(3).to_dict())


if __name__ == "__main__":
    main()
