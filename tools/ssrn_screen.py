"""Quick screen of SSRN intraday CL rules on data/cl1 1m bars. Not TV-exact: fills at the open of the minute bar
at the clock time (= market order sent the bar before). Costs $4.02 RT; slippage scenarios 1 and 2 ticks per side."""
import sys, glob
import numpy as np, pandas as pd

ROOT = sys.argv[1]
df = pd.concat(pd.read_parquet(f) for f in sorted(glob.glob(f"{ROOT}/data/cl1/year=*.parquet")))
df = df.sort_values("ts").reset_index(drop=True)
et = df.ts.dt.tz_convert("America/New_York")
df["d"] = et.dt.date
df["hm"] = et.dt.hour * 60 + et.dt.minute
df = df[et.dt.dayofweek < 5]


def hm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


# price "at" a clock time = open of the first bar at or after it (within 5 min), keyed by ET date
def px(t):
    sub = df[(df.hm >= hm(t)) & (df.hm < hm(t) + 5)]
    first = sub.groupby("d").head(1).set_index("d")
    return first.open, first.raw_symbol


def vol_at(t):
    return df[df.hm == hm(t)].set_index("d").volume


COST, TICK = 4.02, 10.0


def stats(name, pnl_pts, note=""):
    p = pnl_pts.dropna()
    p = p[p != 0] if False else p
    usd = p * 1000 - COST
    if len(usd) == 0:
        print(f"{name:52s} no trades"); return
    yrs = pd.Series(pd.to_datetime(usd.index).year, index=usd.index)
    h1 = usd[yrs <= 2017].sum(); h2 = usd[yrs > 2017].sum()
    gp, gl = usd[usd > 0].sum(), -usd[usd < 0].sum()
    t = usd.mean() / usd.std() * np.sqrt(len(usd))
    s1 = (usd - 2 * TICK).sum(); s2 = (usd - 4 * TICK).sum()
    print(f"{name:52s} n={len(usd):5d} net=${usd.sum():>9,.0f} avg=${usd.mean():>6.1f} win={100*(usd>0).mean():4.1f}% "
          f"PF={gp/gl if gl else np.inf:4.2f} t={t:5.2f} 10-17=${h1:>8,.0f} 18-26=${h2:>8,.0f} | 1tk=${s1:>9,.0f} 2tk=${s2:>9,.0f} {note}")


def same(*syms):
    base = syms[0]
    m = pd.Series(True, index=base.index)
    for s in syms[1:]:
        m &= base.reindex(base.index).eq(s.reindex(base.index))
    return m


def prev(s):  # previous trading day's value
    return s.shift(1)


P = {}; S = {}
for t in ["9:00", "9:30", "10:00", "10:30", "10:35", "10:55", "11:00", "14:00", "14:30", "15:30", "16:00"]:
    P[t], S[t] = px(t)
days = P["14:30"].index
idx = sorted(set(days))
for k in P:
    P[k] = P[k].reindex(idx); S[k] = S[k].reindex(idx)


def timing(sig, a, b, extra_mask=None, mode=1):
    ok = same(S[a], S[b]) & sig.notna()
    if extra_mask is not None:
        ok &= extra_mask.reindex(idx).fillna(False).astype(bool)
    d = np.sign(sig) * mode
    r = (P[b] - P[a]) * d
    return r[ok & (d != 0)]


wd = pd.Series(pd.to_datetime(idx).dayofweek, index=idx)
v1030, v1029 = vol_at("10:30").reindex(idx), vol_at("10:29").reindex(idx)
eia = (v1030 > 3 * v1029)  # release-minute volume spike
eia_wed = eia & (wd == 2)
print(f"days={len(idx)} eia-spike days={int(eia.sum())} (Wed {int(eia_wed.sum())})\n")

pc1430 = prev(P["14:30"]); ps1430 = prev(S["14:30"])
pc1600 = prev(P["16:00"]); ps1600 = prev(S["16:00"])
okp = ps1430.eq(S["14:00"]); okp16 = ps1600.eq(S["15:30"])

print("== Wen et al. / Baltussen et al. intraday momentum (signal sign -> last half hour) ==")
stats("Always long 14:00-14:30 (benchmark)", (P["14:30"] - P["14:00"])[same(S["14:00"], S["14:30"])])
stats("Always long 15:30-16:00 (USO clock benchmark)", (P["16:00"] - P["15:30"])[same(S["15:30"], S["16:00"])])
stats("ONFH pit: sign(prev14:30->9:30) trade 14:00-14:30", timing((P["9:30"] - pc1430).where(okp), "14:00", "14:30"))
stats("ONFH USO: sign(prev16:00->10:00) trade 15:30-16:00", timing((P["10:00"] - pc1600).where(okp16), "15:30", "16:00"))
stats("  same, non-EIA days only", timing((P["10:00"] - pc1600).where(okp16), "15:30", "16:00", ~eia))
stats("ON pit: sign(prev14:30->9:00) trade 14:00-14:30", timing((P["9:00"] - pc1430).where(okp), "14:00", "14:30"))
stats("ON USO: sign(prev16:00->9:30) trade 15:30-16:00 nonEIA", timing((P["9:30"] - pc1600).where(okp16), "15:30", "16:00", ~eia))
stats("ROD: sign(prev14:30->14:00) trade 14:00-14:30", timing((P["14:00"] - pc1430).where(okp), "14:00", "14:30"))
both = np.sign(P["9:30"] - pc1430) == np.sign(P["14:00"] - pc1430)
stats("ONFH&ROD agree, trade 14:00-14:30", timing((P["14:00"] - pc1430).where(okp & both), "14:00", "14:30"))

print("\n== Wen, Indriawan, Lien, Xu (EIA third half-hour) ==")
r3 = P["11:00"] - P["10:30"]
stats("EIA Wed: sign(10:30-11:00) trade 14:00-14:30", timing(r3, "14:00", "14:30", eia_wed))
stats("EIA Wed: sign(10:30-11:00) trade 15:30-16:00", timing(r3, "15:30", "16:00", eia_wed))
stats("EIA Wed: sign(10:30-11:00) trade 11:00-14:30", timing(r3, "11:00", "14:30", eia_wed))
stats("non-EIA: sign(10:30-11:00) trade 14:00-14:30 (control)", timing(r3, "14:00", "14:30", ~eia))

print("\n== Geman & Li / Rousse & Sevi (EIA release reaction) ==")
r5 = P["10:35"] - P["10:30"]
stats("EIA: follow sign(10:30-10:35) hold 10:35-10:55", timing(r5, "10:35", "10:55", eia))
stats("EIA: fade sign(10:30-10:35) hold 10:35-10:55", timing(r5, "10:35", "10:55", eia, -1))
stats("EIA: follow sign(10:30-10:35) hold 10:35-14:30", timing(r5, "10:35", "14:30", eia))
stats("EIA: fade sign(10:30-10:35) hold 10:35-14:30", timing(r5, "10:35", "14:30", eia, -1))
pre = P["10:30"] - P["10:00"]
stats("EIA leak: follow sign(10:00-10:30) hold 10:30-11:00", timing(pre, "10:30", "11:00", eia))

print("\n== Overnight-intraday (Liu/Zhou; Della Corte et al.; Boyarchenko) ==")
on = (P["9:00"] - pc1430).where(ps1430.eq(S["9:00"]))
stats("Reversal: fade sign(prev14:30->9:00) trade 9:00-14:30", timing(on, "9:00", "14:30", None, -1))
stats("Momentum: follow sign(prev14:30->9:00) trade 9:00-14:30", timing(on, "9:00", "14:30"))

print("\n== Holmberg/Lonnbark/Lundstrom opening range breakout (9:00 ET open, stop entry, opposite-side stop, flat 14:30) ==")
day = df[(df.hm >= hm("9:00")) & (df.hm < hm("14:30"))]
for orm in (5, 15, 30, 60):
    res = {}
    for d, g in day.groupby("d", sort=True):
        if g.raw_symbol.nunique() > 1: continue
        o = g[g.hm < hm("9:00") + orm]; r = g[g.hm >= hm("9:00") + orm]
        if len(o) < orm // 2 or len(r) < 10: continue
        H, L = o.high.max(), o.low.min()
        hi, lo, op = r.high.values, r.low.values, r.open.values
        up = np.argmax(hi > H) if (hi > H).any() else None
        dn = np.argmax(lo < L) if (lo < L).any() else None
        if up is None and dn is None: continue
        if dn is None or (up is not None and up < dn): k, side, ent, stop = up, 1, max(H, op[up]), L
        elif up is None or dn < up: k, side, ent, stop = dn, -1, min(L, op[dn]), H
        else: continue  # both on same bar: ambiguous, skip
        ex = r.close.values[-1]
        after = slice(k + 1, None)
        hit = np.where(lo[after] <= stop)[0] if side == 1 else np.where(hi[after] >= stop)[0]
        if len(hit): ex = min(stop, op[k + 1 + hit[0]]) if side == 1 else max(stop, op[k + 1 + hit[0]])
        res[d] = (ex - ent) * side
    stats(f"ORB {orm}m breakout, stop at range edge, exit 14:30", pd.Series(res))

print("\n== Ficura jump momentum (5m bars, all hours, z vs rolling std, hold k bars; 1st-half fit / 2nd-half test) ==")
b = df.set_index("ts")
b5 = b.groupby([pd.Grouper(freq="5min"), "raw_symbol"]).agg(open=("open", "first"), close=("close", "last")).reset_index().sort_values("ts")
b5["ret"] = np.log(b5.close / b5.open)
b5["d"] = b5.ts.dt.tz_convert("America/New_York").dt.date
grid = []
for lb in (16, 64, 256):
    sd = b5.groupby("raw_symbol").ret.transform(lambda s: s.rolling(lb).std().shift(1))
    for z in (1.96, 2.58, 3.29):
        sig = np.sign(b5.ret).where(b5.ret.abs() > z * sd, 0)
        for k in (1, 4, 16):
            ent = b5.groupby("raw_symbol").open.shift(-1); ex = b5.groupby("raw_symbol").open.shift(-1 - k)
            pnl = ((ex - ent) * sig)[sig != 0]
            pnl.index = b5.d[sig != 0]
            grid.append((lb, z, k, pnl.dropna()))
yrs = lambda p: pd.to_datetime(pd.Series(p.index)).dt.year.values
best = max(grid, key=lambda g: (g[3][yrs(g[3]) <= 2017] * 1000 - COST).sum())
for lb, z, k, p in grid:
    if (lb, z, k) == best[:3]: stats(f"jump lb={lb} z={z} hold={k} (best in 2010-17)", p)
tot = [((p * 1000 - COST).sum()) for *_, p in grid]
print(f"   jump grid: {sum(t > 0 for t in tot)}/{len(tot)} combos net positive; median net ${np.median(tot):,.0f}")
