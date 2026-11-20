"""CBR optimize study (plan: studies/cbr_optimize/README.md). Dev only, setup level, in-sample.

Every rth type-3 setup with a 20-min run (`dur`), risk >= 5 ticks, is simulated ALONE with the engine's rules
(touch fill at min(open, limit), 15-bar expiry, target-touch cancel, stop first inside a bar, no target on the fill
bar, flat at the first bar >= 15:10 CT at its open, day end / roll at the close, fee $4.04). Paths are kept so every
exit rule replays the same fills. Outcome: net R. H1 = 2010-06..2015 (learn), H2 = 2016..2021 (confirm).
Run: .venv/bin/python -m studies.cbr_optimize.run
"""

import numpy as np
import pandas as pd

from cltester.config import COMBINE_50K, FEE_ROUND_TURN, ROOT, TICK_VALUE
from cltester.data import load_period, session_minute, to_ticks
from strategies.cbr import EXPIRE_BARS, MIN_RISK, _local_minutes, _ref_hours, candidates

OUT = ROOT / "studies" / "cbr_optimize"
SPLIT = pd.Timestamp("2016-01-01")
FLAT = session_minute(COMBINE_50K.flatten)
FEE_T = FEE_ROUND_TURN / TICK_VALUE  # fee in ticks per contract


def build(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    n = len(df)
    H, L, O, C = (to_ticks(df[k]) for k in ("high", "low", "open", "close"))
    sess = df["sess_minute"].to_numpy()
    day = pd.factorize(df["trading_day"])[0]
    sym = pd.factorize(df["raw_symbol"])[0]
    cut = np.r_[True, (sym[1:] != sym[:-1]) | (day[1:] != day[:-1])]
    seg_id = np.cumsum(cut) - 1
    seg_first = np.flatnonzero(cut)
    seg_last = np.r_[seg_first[1:] - 1, n - 1]
    day_first = np.unique(day, return_index=True)[1]
    rng = H - L
    atr30 = pd.Series(rng).rolling(30, min_periods=30).mean().to_numpy()
    refs = _ref_hours(df, _local_minutes(df), sym, H, L, O, C)["rth"]
    cand = candidates(df)
    x = cand[(cand["window"] == "rth") & cand["ll"].astype(bool) & cand["A_dur"].notna()].copy()
    rows, paths = [], []
    for r in x.itertuples(index=False):
        s, i = int(r.side), int(r.signal)
        h, lo, o, c = (H, L, O, C) if s == 1 else (-L, -H, -O, -C)
        L2, U = int(r.L2), int(r.U)
        E = L2 + (U - L2) // 2
        risk = E - L2
        if risk < MIN_RISK:
            continue
        T2 = E + int(np.ceil(2 * risk))
        last = seg_last[seg_id[i]]
        j = -1
        for k in range(i + 1, min(i + EXPIRE_BARS, last) + 1):  # expire 15 bars: works bars i+1 .. i+15
            if sess[k] >= FLAT:
                break
            if o[k] <= E:  # open at/through the limit fills first
                j = k
                break
            if h[k] >= T2:  # target touched first (or both, order unknown): cancelled
                break
            if lo[k] <= E:
                j = k
                break
        if j < 0:
            continue
        fill = min(o[j], E)
        end = j
        while end + 1 <= last and sess[end + 1] < FLAT:
            end += 1
        flat_bar = end + 1 if end + 1 <= last and sess[end + 1] >= FLAT else -1
        seg = slice(j, end + 1)
        p = {"o": o[seg] - fill, "h": h[seg] - fill, "l": lo[seg] - fill, "c": c[seg] - fill,
             "flat_open": (o[flat_bar] - fill) if flat_bar >= 0 else None, "risk": fill - L2,
             # the bracket is frozen at the signal from the intended limit E (strategy + engine): a better fill
             # (open through the limit) keeps E's target and thresholds; actual risk only normalises the outcome
             "e_off": E - fill, "r0": risk}
        paths.append(p)
        a = r.T_dur
        t = int(a)
        leg = int(r.A_dur) - L2
        runmin = np.minimum.accumulate(lo[t:int(r.l2c)])
        bounce = (h[t + 1:int(r.l2c) + 1] - runmin).max(initial=0) / leg
        eff = abs(c[int(r.l2c)] - c[t]) / max(np.abs(np.diff(c[t:int(r.l2c) + 1])).sum(), 1)
        d = int(day[i])
        ref = refs.loc[d] if d in refs.index else None
        sess_open = o[day_first[d]]
        rows.append({
            "day": df["trading_day"].iloc[i], "side": s, "signal": i, "fill_bar": j, "fill_delay": j - i,
            # entry features use the intended risk (limit - L2), known at the signal; the fill is not (README:
            # "risk ticks (entry - L2)"); fill - L2 can be 0 or negative after an open through the stop
            "risk": risk, "risk_atr": risk / atr30[i] if atr30[i] > 0 else np.nan,
            "room": (int(r.A_dur) - L2) / risk, "dur": int(r.l2c) - t, "bounce": bounce, "eff": eff,
            "e20": not np.isnan(r.A_e20), "sweep_depth": (int(r.L1) - L2) / risk,
            "minute": int(r.sig_rel) - 60, "ref_range_atr": ((ref["h"] - ref["l"]) / atr30[i])
            if ref is not None and atr30[i] > 0 else np.nan,
            "wed": pd.Timestamp(df["trading_day"].iloc[i]).day_of_week == 2,
            "trend_aligned": (c[i] - sess_open) > 0, "body": int(r.body) == 1, "struct": int(r.struct) == 1,
            "sweep_fh": bool(r.sweep_fh), "sweep_30": bool(r.sweep_30),
        })
    return pd.DataFrame(rows), paths


def sim(p: dict, tgt: float = 2.0, be: float | None = None, tstop: int | None = None,
        runner: int | None = None) -> float:
    """Net R of one filled setup under an exit rule (side space, ticks relative to the fill). Target and management
    thresholds come from the intended limit and risk (frozen at the signal, as in the strategy). R = actual risk
    (fill - stop); when an open through the limit also reached the stop (actual risk <= 0) the engine exits at the
    fill price on the fill bar (fee only), normalised by the intended risk (Codex adversarial review 2026-11-20)."""
    o, h, lo, c, risk = p["o"], p["h"], p["l"], p["c"], p["risk"]
    e_off, r0 = p["e_off"], p["r0"]
    stop, target = -risk, e_off + int(np.ceil(tgt * r0))
    norm = risk if risk > 0 else r0
    fee = FEE_T / norm
    if lo[0] <= stop:  # stop on the fill bar (assume the low came after the fill): exit at min(entry, stop)
        return min(0, stop) / norm - fee
    # the fill bar's high may have printed before the fill (intrabar order unknown): management thresholds use bars
    # after the fill bar only, as the RLM manage() does (Codex adversarial review 2026-11-20)
    best = -10**9
    for k in range(1, len(o)):
        # management with data up to k-1
        if be is not None and best >= e_off + be * r0:
            stop = max(stop, 0)
        if runner is not None and k - 1 <= runner and best >= e_off + r0:
            target = max(target, e_off + int(np.ceil(4 * r0)))
        if tstop is not None and k - 1 == tstop and c[k - 1] < e_off + 0.5 * r0:
            return o[k] / norm - fee
        if o[k] <= stop:
            return o[k] / norm - fee
        if o[k] >= target:
            return o[k] / norm - fee
        if lo[k] <= stop:
            return stop / norm - fee
        if h[k] >= target:
            return target / norm - fee
        best = max(best, h[k])
    if p["flat_open"] is not None:
        return p["flat_open"] / norm - fee
    return c[-1] / norm - fee


EXITS = {"tp1R": {"tgt": 1.0}, "tp1.5R": {"tgt": 1.5}, "tp2R (base)": {"tgt": 2.0}, "tp3R": {"tgt": 3.0},
         "tp4R": {"tgt": 4.0}, "2R + BE at 1R": {"be": 1.0}, "2R + time stop 10": {"tstop": 10},
         "2R + time stop 20": {"tstop": 20}, "2R + time stop 30": {"tstop": 30},
         "2R, runner 4R if 1R within 5": {"runner": 5}, "2R, runner 4R if 1R within 10": {"runner": 10}}
CONT = ["risk", "risk_atr", "room", "dur", "bounce", "eff", "sweep_depth", "minute", "ref_range_atr", "fill_delay"]
FLAGS = ["side", "e20", "wed", "trend_aligned", "body", "struct", "sweep_fh", "sweep_30"]


def main() -> None:
    df = load_period("dev")
    f, paths = build(df)
    f["h1"] = pd.to_datetime(f["day"]) < SPLIT
    for name, kw in EXITS.items():
        f[name] = [sim(p, **kw) for p in paths]
    f.to_csv(OUT / "setups_dev.csv", index=False)
    base = "tp2R (base)"
    print(f"setups filled: {len(f)} (H1 {f.h1.sum()}, H2 {(~f.h1).sum()}); dev, in-sample, setup level")
    better = sum(p["e_off"] > 0 for p in paths)
    through = sum(p["risk"] <= 0 for p in paths)
    print(f"fills better than the limit (open through it): {better}; their bracket stays frozen at the limit "
          "(fixed 2026-11-20, Codex adversarial review)")
    print(f"fills at or through the stop (exit at the fill, fee only): {through}")
    vals = f[list(EXITS)].to_numpy(float)
    if not np.isfinite(vals).all():
        raise SystemExit(f"non-finite outcomes: {int((~np.isfinite(vals)).sum())}")
    print("all outcomes finite\n")
    print("EXIT RULES: mean net R (H1 / H2 / all), win share")
    for name in EXITS:
        a, b = f.loc[f.h1, name].mean(), f.loc[~f.h1, name].mean()
        better = "  beats base in both" if name != base and a > f.loc[f.h1, base].mean() and \
            b > f.loc[~f.h1, base].mean() else ""
        print(f"  {name:<32} {a:+.3f} / {b:+.3f} / {f[name].mean():+.3f}  win {(f[name] > 0).mean():.1%}{better}")
    print("\nENTRY FEATURES vs base mean R. Terciles from H1. q1 / q2 / q3 (H1 | H2)")
    keep = []
    for k in CONT:
        v = f[k].astype(float)
        e1, e2 = v[f.h1].quantile([1 / 3, 2 / 3])
        q = np.where(v <= e1, 0, np.where(v <= e2, 1, 2))
        q = np.where(v.isna(), -1, q)
        m = [[f.loc[(q == t) & (f.h1 == h), base].mean() for t in range(3)] for h in (True, False)]
        lo_t = int(np.argmin(m[0]))
        hi_t = int(np.argmax(m[0]))
        mono = lambda r: (r[0] <= r[1] <= r[2]) or (r[0] >= r[1] >= r[2])  # noqa: E731
        ok = (m[0][hi_t] - m[0][lo_t] >= 0.10 and m[1][hi_t] - m[1][lo_t] >= 0.10
              and ((mono(m[0]) and mono(m[1])) or (m[0][lo_t] < 0 and m[1][lo_t] < 0)) and lo_t in (0, 2))
        if ok:
            keep.append((k, lo_t, e1, e2))
        print(f"  {k:<14} cuts {e1:7.2f} {e2:7.2f} | " + " ".join(f"{x:+.3f}" for x in m[0]) + " | "
              + " ".join(f"{x:+.3f}" for x in m[1]) + (f"   QUALIFIES (skip q{lo_t + 1})" if ok else ""))
    print("\nFLAGS: mean R when False / True (H1 | H2)")
    for k in FLAGS:
        v = (f[k] == 1) if k == "side" else f[k].astype(bool)
        m = [[f.loc[(v == t) & (f.h1 == h), base].mean() for t in (False, True)] for h in (True, False)]
        n = [int(((v == t) & f.h1).sum()) for t in (False, True)]
        lab = "short/long" if k == "side" else "F/T"
        ok = all(abs(r[1] - r[0]) >= 0.10 for r in m) and np.sign(m[0][1] - m[0][0]) == np.sign(m[1][1] - m[1][0])
        print(f"  {k:<14} {lab:<10} {m[0][0]:+.3f} {m[0][1]:+.3f} | {m[1][0]:+.3f} {m[1][1]:+.3f}  n(H1) {n}"
              + ("   QUALIFIES" if ok else ""))
    print("\nqualifying continuous filters:", [(k, f"skip q{t + 1}") for k, t, _, _ in keep])


if __name__ == "__main__":
    main()
