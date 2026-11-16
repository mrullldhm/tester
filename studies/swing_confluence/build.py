"""Event table for the swing confluence study (docs/studies/swing_confluence/README.md).

One row per new swing point on a base timeframe, with the point-in-time swing state of every timeframe and the
hold/fail outcome. Run: .venv/bin/python -m studies.swing_confluence.build [--period dev]
"""

import argparse
import time

import numpy as np
import pandas as pd

from cltester.config import ROOT
from cltester.data import load_period, to_ticks
from cltester.swings import swing_state

CONTEXT = ["1m", "5m", "15m", "1h", "4h", "1d", "1w", "1mo"]
BASES = ["1m", "5m", "15m", "1h", "4h", "1d"]
OUT_DIR = ROOT / "data" / "studies"


class RangeExtreme:
    """Sparse tables for O(1) range max of highs / min of lows and vectorised first-passage search."""

    def __init__(self, h: np.ndarray, l: np.ndarray):  # noqa: E741
        self.n = len(h)
        self.mx = [h.astype(np.int32)]
        self.mn = [l.astype(np.int32)]
        k = 1
        while (1 << k) <= self.n:
            half = 1 << (k - 1)
            a, b = self.mx[-1], self.mn[-1]
            self.mx.append(np.maximum(a[:-half], a[half:]))
            self.mn.append(np.minimum(b[:-half], b[half:]))
            k += 1

    def range_max(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """max h[a..b] inclusive; -inf-like where b < a."""
        return self._range(a, b, self.mx, np.maximum, np.iinfo(np.int32).min)

    def range_min(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return self._range(a, b, self.mn, np.minimum, np.iinfo(np.int32).max)

    def _range(self, a, b, tab, op, empty):
        out = np.full(len(a), empty, dtype=np.int64)
        ok = b >= a
        a, b = a[ok], b[ok]
        k = np.floor(np.log2(b - a + 1)).astype(np.int64)
        res = np.empty(len(a), dtype=np.int64)
        for kk in np.unique(k):
            m = k == kk
            t = tab[kk]
            res[m] = op(t[a[m]], t[b[m] - (1 << kk) + 1])
        out[ok] = res
        return out

    def first_above(self, start: np.ndarray, level: np.ndarray) -> np.ndarray:
        """First index j >= start with h[j] > level; n if none."""
        return self._first(start, level, self.mx, lambda block, lv: block <= lv)

    def first_below(self, start: np.ndarray, level: np.ndarray) -> np.ndarray:
        return self._first(start, level, self.mn, lambda block, lv: block >= lv)

    def _first(self, start, level, tab, still_ok):
        pos = start.astype(np.int64).copy()
        for k in range(len(tab) - 1, -1, -1):
            t = tab[k]
            can = pos + (1 << k) <= self.n
            idx = np.flatnonzero(can)
            jump = still_ok(t[pos[idx]], level[idx])  # whole block [pos, pos+2^k) does not cross
            pos[idx[jump]] += 1 << k
        return pos


MISSING = np.iinfo(np.int64).min  # no level; never a price sign test (CL can trade below zero)


def _ticks(x: pd.Series) -> np.ndarray:
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), MISSING, dtype=np.int64)
    ok = ~np.isnan(v)
    out[ok] = to_ticks(v[ok])
    return out


def build(period: str = "dev") -> pd.DataFrame:
    t0 = time.time()
    df = load_period(period)
    n = len(df)
    h, l, c = to_ticks(df["high"]), to_ticks(df["low"]), to_ticks(df["close"])
    ts = pd.DatetimeIndex(df["ts"]).as_unit("ns")
    sym = pd.factorize(df["raw_symbol"])[0]
    roll_count = np.r_[0, np.cumsum(sym[1:] != sym[:-1])]  # rolls up to bar i
    day = pd.factorize(df["trading_day"])[0]
    rx = RangeExtreme(h, l)

    st: dict[str, dict[str, np.ndarray]] = {}
    for tf in CONTEXT:
        s = swing_state(df, tf, prev=True, newest=True)
        st[tf] = {k: _ticks(s[f"{tf}_{k}"]) for k in ("sh", "sl", "sh2", "sl2")}
        st[tf]["newest"] = s[f"{tf}_newest"].to_numpy()
        for k in ("sh", "sl", "sh2", "sl2"):
            st[tf][f"{k}_ts"] = pd.DatetimeIndex(s[f"{tf}_{k}_ts"]).as_unit("ns").asi8  # NaT = int64 min
        print(f"  state {tf}: {time.time() - t0:.0f}s", flush=True)

    frames = []
    for base in BASES:
        b = st[base]
        for side, key, opp in ((1, "sl", "sh"), (-1, "sh", "sl")):  # side +1: swing low (hold = up)
            pts = b[f"{key}_ts"]
            opp_ts = b[f"{opp}_ts"]
            # a new point has a later candle than every same-side point seen so far; rule 4 can restore an older
            # point (earlier candle), which is not a new confirmation
            seen = np.r_[np.iinfo(np.int64).min, np.maximum.accumulate(pts)[:-1]]
            new = (pts > seen) & (b[key] != MISSING) & (b[opp] != MISSING)
            new[0] = False
            i = np.flatnonzero(new)
            if len(i) == 0:
                continue
            ev = b[key][i]  # event price (ticks)
            op = b[opp][i]  # opposite level on the base timeframe
            # rule 5 replacement: no opposite point after the previous same-side point (same candle: order by newest)
            prev_pt = pts[i - 1]
            replace = (prev_pt != np.iinfo(np.int64).min) & ((opp_ts[i] < prev_pt)
                                                            | ((opp_ts[i] == prev_pt) & (b["newest"][i - 1] == -side)))
            first_bar = np.searchsorted(ts.asi8, pts[i])  # event candle's first 1m bar
            before = np.maximum(first_bar - 1, 0)

            lo_lvl, hi_lvl = (ev, op) if side == 1 else (op, ev)
            j_up = rx.first_above(i + 1, hi_lvl)
            j_dn = rx.first_below(i + 1, lo_lvl)
            j_hold, j_fail = (j_up, j_dn) if side == 1 else (j_dn, j_up)
            resolved = np.minimum(j_up, j_dn)
            outcome = np.where(j_up == j_dn, -1, (j_hold < j_fail).astype(int))  # -1 tie or unresolved
            outcome[resolved >= n] = -1
            r = np.minimum(resolved, n - 1)
            leg = np.abs(op - ev)
            # random walk on ticks with strict breaks: absorbing barriers at L-1 and H+1 (Codex audit 2026-11-16).
            # A confirmation close outside [L, H] has no fair rate: those events are left out (NaN).
            inside = (c[i] >= lo_lvl) & (c[i] <= hi_lvl)
            fair = (c[i] - lo_lvl + 1) / (hi_lvl - lo_lvl + 2)
            fair = np.where(inside, fair if side == 1 else 1 - fair, np.nan)
            # deepest return toward the event price before a hold; furthest run before a fail (leg units)
            end_h = np.minimum(j_hold, n) - 1
            end_f = np.minimum(j_fail, n) - 1
            if side == 1:
                retest = (rx.range_min(i + 1, end_h) - ev) / np.maximum(leg, 1)
                run = (rx.range_max(i + 1, end_f) - ev) / np.maximum(leg, 1)
            else:
                retest = (ev - rx.range_max(i + 1, end_h)) / np.maximum(leg, 1)
                run = (ev - rx.range_min(i + 1, end_f)) / np.maximum(leg, 1)
            prev_same = b[f"{key}2"][i]  # the same-side point before this one (sl2 / sh2)
            prev_leg = np.where(prev_same != MISSING, np.abs(op - prev_same), 0)
            ct = ts[i].tz_convert("America/Chicago")

            row = {
                "base": base, "side": side, "bar": i, "ts": ts[i],
                "pt_ts": pd.DatetimeIndex(pts[i], tz="UTC"),
                "opp_ts": pd.DatetimeIndex(opp_ts[i], tz="UTC"),
                # the points before them on the base timeframe: same side (sl2 for a low) and opposite (sh2)
                "prev_ts": pd.DatetimeIndex(b[f"{key}2_ts"][i], tz="UTC"),
                "opp2_ts": pd.DatetimeIndex(b[f"{opp}2_ts"][i], tz="UTC"),
                "prev_price": np.where(b[f"{key}2"][i] != MISSING, b[f"{key}2"][i], np.nan),
                "opp2_price": np.where(b[f"{opp}2"][i] != MISSING, b[f"{opp}2"][i], np.nan),
                "trading_day": df["trading_day"].to_numpy()[i],
                "year": ct.year, "ct_hour": ct.hour, "weekday": ct.day_of_week, "price": ev, "opp": op, "leg": leg,
                "replace": replace, "retrace": np.where(prev_leg > 0, leg / np.maximum(prev_leg, 1), np.nan),
                "outcome": outcome, "fair": fair, "minutes": (ts.asi8[r] - ts.asi8[i]) // 60_000_000_000,
                "same_day": day[r] == day[i], "roll": roll_count[r] != roll_count[i],
                "retest": np.where((outcome == 1) & (end_h >= i + 1), retest, np.nan),  # NaN: held on the next bar
                "run": np.where((outcome == 0) & (end_f >= i + 1), run, np.nan),
            }
            for tf in CONTEXT:
                s = st[tf]
                sh, sl, sh2, sl2 = (s[k][i] for k in ("sh", "sl", "sh2", "sl2"))
                ok = (sh != MISSING) & (sl != MISSING) & (sh2 != MISSING) & (sl2 != MISSING)
                hh, lh, hl, ll = sh > sh2, sh < sh2, sl > sl2, sl < sl2
                trend = np.select([hh & hl, lh & ll, hh & ll, lh & hl], [1, -1, 2, 3], 4)  # 4: an equal high or low
                if side == -1:
                    trend = np.where(np.abs(trend) == 1, -trend, trend)
                # 1 with, -1 against, 2 expand, 3 contract, 4 equal (mirror-symmetric), 0 none
                row[f"{tf}_trend"] = np.where(ok, trend, 0)
                row[f"{tf}_leg"] = np.where(s["newest"][i] != 0, np.where(s["newest"][i] == -side, 1, -1), 0)
                rng = np.where((sh != MISSING) & (sl != MISSING), sh - sl, 0)
                pos = (ev - sl) / np.maximum(rng, 1) if side == 1 else (sh - ev) / np.maximum(rng, 1)
                row[f"{tf}_pos"] = np.where(rng > 0, pos, np.nan)
                lvl_before = s[key][before]
                took = ev < lvl_before if side == 1 else ev > lvl_before
                row[f"{tf}_sweep"] = np.where(lvl_before != MISSING, took.astype(int), -1)
                for k in ("sh", "sl", "sh2", "sl2"):
                    row[f"{tf}_{k}"] = np.where(s[k][i] != MISSING, s[k][i], np.nan)
            frames.append(pd.DataFrame(row))
        print(f"  events {base}: {time.time() - t0:.0f}s", flush=True)
    out = pd.concat(frames, ignore_index=True)
    out["side"] = out["side"].astype("int8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default="dev", choices=["dev"])  # the study is dev-only by design
    args = ap.parse_args()
    ev = build(args.period)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"swing_confluence_{args.period}.parquet"
    ev.to_parquet(path, index=False)
    print(f"{len(ev)} events -> {path}")
    print(ev.groupby("base")["outcome"].value_counts().unstack())


if __name__ == "__main__":
    main()
