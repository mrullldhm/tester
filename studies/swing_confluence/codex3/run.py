"""Frozen sequence study; run with PYTHONDONTWRITEBYTECODE=1 python -B -m ...codex3.run."""

import json
from math import erfc, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

from cltester.data import load_period, to_ticks
from cltester.swings import build_candles, swing_state
from studies.swing_confluence.build import RangeExtreme
from studies.swing_confluence.scan import bh

OUT = Path(__file__).parent


def main():
    df = load_period("dev")
    n = len(df)
    ts = pd.DatetimeIndex(df.ts).as_unit("ns").asi8
    h, l, c = (to_ticks(df[k]) for k in ("high", "low", "close"))
    day = df.trading_day.to_numpy()
    yr = pd.DatetimeIndex(df.ts).tz_convert("America/Chicago").year.to_numpy()
    rolls = np.r_[0, np.cumsum(df.raw_symbol.to_numpy()[1:] != df.raw_symbol.to_numpy()[:-1])]
    print("raw", n, df.ts.min(), df.ts.max(), flush=True)
    rx = RangeExtreme(h, l)
    states = {}
    for tf in ("1m", "5m", "15m", "1h", "4h"):
        path = OUT / f"state_{tf}.parquet"
        if path.exists():
            s = pd.read_parquet(path)
        else:
            s = swing_state(df, tf, prev=True, newest=True)
            s.to_parquet(path, index=False)
        states[tf] = s
        print("state", tf, flush=True)
    events = pd.read_parquet("data/studies/swing_confluence_dev.parquet")
    rows = []
    counts = {}

    def passage(start, upper, lower, d):
        if d == 1:
            return rx.first_above(start, upper), rx.first_below(start, lower)
        return rx.first_below(start, -upper), rx.first_above(start, -lower)

    def sample(phase, b, t, d, start, upper, lower, up, down, trend, **extra):
        end = min(up, down)
        if end >= n or up == down or start >= n or upper <= lower:
            return
        if rolls[end] != rolls[start]:
            return
        cc = d * c[start]
        if not lower <= cc <= upper:
            return
        rows.append(
            dict(
                family=phase,
                base=b,
                htf=t,
                side=d,
                bar=int(start),
                end=int(end),
                year=int(yr[start]),
                day=str(day[start]),
                fair=(cc - lower + 1) / (upper - lower + 2),
                outcome=int(up < down),
                trend=bool(trend),
                upper=int(upper),
                lower=int(lower),
                **extra,
            )
        )

    # N: HH/HL ordered by actual state timestamps, opposite mirror for shorts.
    for b, t in [("1m", "5m"), ("5m", "15m"), ("15m", "1h"), ("1h", "4h")]:
        s, hs = states[b], states[t]
        for d in (1, -1):
            high, low = ("sh", "sl") if d == 1 else ("sl", "sh")
            seed = events[
                (events.base == b) & (events.side == -d) & (~events["replace"]) & (events[f"{b}_trend"] == -1)
            ].sort_values("bar")
            a = seed.bar.to_numpy()
            point = pd.DatetimeIndex(s[f"{b}_{high}_ts"]).as_unit("ns").asi8
            prev = pd.DatetimeIndex(s[f"{b}_{high}2_ts"]).as_unit("ns").asi8
            lp = pd.DatetimeIndex(s[f"{b}_{low}_ts"]).as_unit("ns").asi8
            lp2 = pd.DatetimeIndex(s[f"{b}_{low}2_ts"]).as_unit("ns").asi8
            valid = (lp2[a] < prev[a]) & (prev[a] < lp[a]) & (lp[a] < point[a])
            a = a[valid]
            # The HL must not already have broken before the HH became actionable.
            low_start = np.searchsorted(ts, lp[a])
            protected = np.rint(d * s[f"{b}_{low}"].to_numpy()[a] * 100)
            observed = rx.range_min(low_start, a) if d == 1 else -rx.range_max(low_start, a)
            a = a[observed >= protected]
            top = np.rint(d * s[f"{b}_{high}"].to_numpy()[a] * 100).astype(int)
            hl = np.rint(d * s[f"{b}_{low}"].to_numpy()[a] * 100).astype(int)
            up, br = passage(a + 1, top, hl, d)
            ok = (br < up) & (br < n)
            a, top, br = a[ok], top[ok], br[ok]
            htlo = np.rint(d * hs[f"{t}_{low}"].to_numpy() * 100)
            htlo2 = np.rint(d * hs[f"{t}_{low}2"].to_numpy() * 100)
            hthi = np.rint(d * hs[f"{t}_{high}"].to_numpy() * 100)
            hthi2 = np.rint(d * hs[f"{t}_{high}2"].to_numpy() * 100)
            # Only intact frozen HTF low, across the seed-to-break interval.
            adverse = rx.range_min(a, br) if d == 1 else -rx.range_max(a, br)
            good = np.isfinite(htlo[br]) & (adverse >= htlo[br]) & (htlo[br] < top)
            a, top, br = a[good], top[good], br[good]
            lower = np.rint(htlo[br]).astype(int)
            hit, fail = passage(br + 1, top, lower, d)
            lh = events[(events.base == b) & (events.side == -d)].sort_values("bar")
            lhb = lh.bar.to_numpy()
            lhp = d * lh.price.to_numpy()
            lht = pd.DatetimeIndex(lh.pt_ts).as_unit("ns").asi8
            occupied = -1
            ct = 0
            for aa, bb, uu, ll, hh, ff in zip(a, br, top, lower, hit, fail, strict=True):
                if bb <= occupied:
                    continue
                # Reserve the seed before seeing whether its decision close is usable.
                occupied = min(hh, ff)
                if rolls[bb] != rolls[aa]:
                    continue
                ct += 1
                tr = (htlo[bb] > htlo2[bb]) and (hthi[bb] > hthi2[bb])
                sample("N_break", b, t, d, bb, uu, ll, hh, ff, tr, seed=int(aa))
                end = min(hh, ff)
                p = np.searchsorted(lhb, bb + 1)
                while p < len(lhb) and lhb[p] < end:
                    if lht[p] > ts[bb] and lhp[p] < uu:
                        # First confirmed lower high after the break; one chance only.
                        j = int(lhb[p])
                        level = int(lhp[p])
                        break
                    p += 1
                else:
                    continue
                r, _ = passage(np.array([j + 1]), np.array([level]), np.array([ll]), d)
                r = int(r[0])
                if r >= end:
                    continue  # includes same-minute barrier/reclaim ambiguity
                # Reclaim's bar must not also cross the frozen HTF low.
                if (d * l[r] if d == 1 else -h[r]) < ll:
                    continue
                nh, nf = passage(np.array([r + 1]), np.array([uu]), np.array([ll]), d)
                sample(
                    "N_reclaim_htf",
                    b,
                    t,
                    d,
                    r,
                    uu,
                    ll,
                    int(nh[0]),
                    int(nf[0]),
                    tr,
                    seed=int(aa),
                    break_bar=int(bb),
                    lh_bar=j,
                )
                local = (
                    int(rx.range_min(np.array([bb]), np.array([r]))[0])
                    if d == 1
                    else -int(rx.range_max(np.array([bb]), np.array([r]))[0])
                )
                nh, nf = passage(np.array([r + 1]), np.array([uu]), np.array([local]), d)
                sample(
                    "N_reclaim_local",
                    b,
                    t,
                    d,
                    r,
                    uu,
                    local,
                    int(nh[0]),
                    int(nf[0]),
                    tr,
                    seed=int(aa),
                    break_bar=int(bb),
                    lh_bar=j,
                )
            counts[f"N_{b}_{d}_seeds"] = ct
        print("N", b, len(rows), flush=True)
    # M: full owner confirmation on B at C completion, never a final-structure pivot.
    for b, t in [("5m", "1h"), ("15m", "4h"), ("1h", "4h")]:
        cd, hd = build_candles(df, b), build_candles(df, t)
        s = states[b]
        k = np.arange(1, len(cd) - 1)
        before = cd.first[k] - 1
        decision = cd.avail[k + 1]
        for d in (1, -1):
            key = "sh" if d == 1 else "sl"
            known = np.rint(s[f"{b}_{key}"].to_numpy() * 100) * d
            pt = pd.DatetimeIndex(s[f"{b}_{key}_ts"]).as_unit("ns").asi8
            level = known[before]
            first = np.searchsorted(ts, pt[before])
            valid = np.isfinite(level) & (first < cd.first[k])
            safe = np.minimum(first, n - 1)
            prior = rx.range_max(safe, cd.first[k] - 1) if d == 1 else -rx.range_min(safe, cd.first[k] - 1)
            top = d * (cd.h[k] if d == 1 else cd.l[k])
            bottom = d * (cd.l[k] if d == 1 else cd.h[k])
            nextlow = d * (cd.l[k + 1] if d == 1 else cd.h[k + 1])
            m = (
                valid
                & (prior <= level)
                & (top > level)
                & (nextlow < bottom)
                & (pt[decision] == pd.DatetimeIndex(cd.ts[k]).as_unit("ns").asi8)
            )
            kk = k[m]
            dd = decision[m]
            uu = top[m]
            ll = nextlow[m]
            up, dn = passage(dd + 1, uu, ll, d)
            for q, j, u, v, hu, hdn in zip(kk, dd, uu, ll, up, dn, strict=True):
                if rolls[j] != rolls[cd.first[q]]:
                    continue
                cid = int(np.searchsorted(hd.first, cd.first[q], side="right") - 1)
                if cid < 1:
                    continue
                parent_forming = bool(hd.avail[cid] > j)
                forming = bool(cid + 1 >= len(hd) or hd.avail[cid + 1] > j)  # right candle not yet complete
                prev = cid - 1
                # Opposite extreme = low on a failed bullish breakout, high on bearish.
                extreme = (
                    rx.range_min(np.array([hd.first[cid]]), np.array([j]))[0]
                    if d == 1
                    else -rx.range_max(np.array([hd.first[cid]]), np.array([j]))[0]
                )
                prev_ext = hd.l[prev] if d == 1 else -hd.h[prev]
                sample(
                    "M",
                    b,
                    t,
                    d,
                    int(j),
                    int(u),
                    int(v),
                    int(hu),
                    int(hdn),
                    False,
                    breakout=int(cd.first[q]),
                    forming=forming,
                    parent_forming=parent_forming,
                    took=bool(extreme < prev_ext),
                )
        print("M", b, len(rows), flush=True)
    r = pd.DataFrame(rows)
    r.to_parquet(OUT / "sequences.parquet", index=False)
    cells = []
    years = []

    def stat(g, label):
        resid = g.outcome - g.fair
        edge = resid.mean()
        sign = np.sign(edge)
        annual = resid.groupby(g.year).mean()
        var = (g.fair * (1 - g.fair)).sum()
        z = resid.sum() / sqrt(var) if var > 0 else 0
        # Cluster-robust SE for the mean under zero average residual, centered day sums.
        cluster = pd.DataFrame({"day": g.day, "res": resid - edge}).groupby("day").res.sum()
        G = len(cluster)
        se = sqrt((cluster**2).sum() * G / max(G - 1, 1)) / max(len(g), 1)
        zc = edge / se if se > 0 else 0
        e1 = resid[g.year < 2016].mean()
        e2 = resid[g.year >= 2016].mean()
        cells.append(
            dict(
                cell=label,
                n=len(g),
                hold=g.outcome.mean(),
                fair=g.fair.mean(),
                edge=edge,
                e1=e1,
                e2=e2,
                years_same=int((np.sign(annual) == sign).sum()),
                years=len(annual),
                days=G,
                long=resid[g.side == 1].mean(),
                short=resid[g.side == -1].mean(),
                z=z,
                zc=zc,
                p=erfc(abs(z) / sqrt(2)) if len(g) >= 300 else 1,
                pc=erfc(abs(zc) / sqrt(2)) if len(g) >= 300 else 1,
            )
        )
        for year, val in annual.items():
            years.append(dict(cell=label, year=year, n=int((g.year == year).sum()), edge=val))

    for b, t in [("1m", "5m"), ("5m", "15m"), ("15m", "1h"), ("1h", "4h")]:
        for phase in ("N_break", "N_reclaim_htf", "N_reclaim_local"):
            g = r[(r.base == b) & (r.family == phase)]
            for name, sub in [("all", g), ("up", g[g.trend])]:
                stat(sub, f"{phase} {b}/{t} {name}")
    for b, t in [("5m", "1h"), ("15m", "4h"), ("1h", "4h")]:
        g = r[(r.base == b) & (r.family == "M")]
        for name, sub in [
            ("all", g),
            ("forming", g[g.forming.eq(True)]),
            ("complete", g[g.forming.eq(False)]),
            ("forming_took", g[(g.forming.eq(True)) & (g.took.eq(True))]),
            ("forming_intact", g[(g.forming.eq(True)) & (g.took.eq(False))]),
        ]:
            stat(sub, f"M {b}/{t} {name}")
    out = pd.DataFrame(cells)
    assert len(out) == 39
    out["bh"] = bh(out.p.to_numpy())
    out["bh_cluster"] = bh(out.pc.to_numpy())
    gate = (out.n >= 300) & (out.edge.abs() >= 0.03) & (out.e1 * out.e2 > 0) & (out.years_same >= 9)
    out["pass_nominal"] = gate & out.bh
    out["pass_cluster"] = gate & out.bh_cluster
    out.to_csv(OUT / "cells.csv", index=False)
    pd.DataFrame(years).to_csv(OUT / "years.csv", index=False)
    (OUT / "counts.json").write_text(
        json.dumps(
            dict(
                raw_n=n,
                first=str(df.ts.min()),
                last=str(df.ts.max()),
                events=len(events),
                sequence_rows=len(r),
                **counts,
            ),
            indent=2,
        )
    )
    print(out.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
