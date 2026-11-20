"""CBR 1h/1m model (Tom Gratwicke / itstomtrades, XAUUSD PDF, mapped to CL 2026-11-19 by Claude + Codex).
Spec, CL mapping and trial budget: docs/strategies/cbr/README.md.

Long (short is the mirror): in a 1-hour entry window after a reference hour, price over-extends down for 20+
minutes with no big bounce (extension filter), then makes a 1m "type 3 shift" (owner swing rule): swing low L1,
swing high H1, lower low L2 < L1, and the first 1m close above H1 (MSB). Buy limit at the middle of L2..U (U =
highest high from L2 through the MSB close), stop at L2, target the extension midpoint or 1.5R / 2R.

Both sides run through one scan written for longs: short prices are negated ("side space").
"""

import hashlib

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.data import to_ticks
from cltester.strategy import Base
from cltester.swings import LOW, build_candles, detect, swing_state

MIN_RISK = 5  # ticks: entry - stop below this is fee/noise dominated ($4.04 fee = 8% of 5 ticks)
LOOKBACK = 60  # bars: the extension origin lies 20..60 minutes before L2
EXPIRE_BARS = 15  # 1m bars an unfilled entry works (also cancelled by a target touch and by a newer setup)

# window: (clock, reference-hour start minute of day in that clock, weekday filter or None). Entry window = the
# hour after the reference hour. Clocks: "utc", "ct" (Chicago), "ldn" (Europe/London).
WINDOWS = {
    "asia_utc": ("utc", 0, None),   # literal PDF: Asia opens 00:00 UTC, trade 01:00-02:00 UTC
    "globex": ("ct", 17 * 60, None),  # CL reopen 17:00 CT, trade 18:00-19:00 CT
    "london": ("ldn", 8 * 60, None),  # London 08:00, trade 09:00-10:00 London (03:00-04:00 CT usually)
    "ny": ("ct", 8 * 60, None),       # 08:00 CT NY open anchor, trade 09:00-10:00 CT
    "rth": ("ct", 8 * 60 + 30, None),  # 08:30 CT RTH anchor, trade 09:30-10:30 CT
    "eia": ("ct", 9 * 60 + 30, 2),    # Wednesday 09:30 CT EIA release, trade 10:30-11:30 CT (holiday shifts ignored)
}
# extension variants: (min duration bars, max counter-retracement of the leg, min close efficiency). Thresholds set
# by setup frequency on dev before any P&L was seen (share of all type-3 candidates passing): e20 ~24%, e30 ~20%,
# e20loose ~39%, dur ~69% (duration only, control). 1m CL close efficiency: median 0.17, 90th percentile 0.37.
EXTENSIONS = {"e20": (20, 0.5, 0.30), "e30": (30, 0.5, 0.25), "e20loose": (20, 0.6, 0.20), "dur": (20, np.inf, 0.0)}
CONTEXTS = ("fh", "reb", "reb30")
BIASES = ("none", "body", "engulf", "struct")
TARGETS = ("mid", "r1.5", "r2")


def _local_minutes(df: pd.DataFrame) -> dict[str, np.ndarray]:
    ts = df["ts"].dt
    utc = (ts.hour * 60 + ts.minute).to_numpy()
    ldn = df["ts"].dt.tz_convert("Europe/London")
    return {"utc": utc, "ct": df["ct_minute"].to_numpy(), "ldn": (ldn.dt.hour * 60 + ldn.dt.minute).to_numpy(),
            "wd": df["ct"].dt.day_of_week.to_numpy()}


def _extension(h, lo, c, l2c: int, start_min: int, dur: int, retr: float, eff: float) -> int:
    """Side space (long: the leg runs down into L2). Origin of the over-extension: the EARLIEST bar t
    (max(start_min, l2c - LOOKBACK) <= t <= l2c - dur) whose high is the highest high of t..l2c, with
    counter-retracement <= retr of (high[t] - low[l2c]) and close efficiency >= eff. Earliest, so the leg is the
    whole one-way move (the PDF's target is its 50%). Returns t or -1."""
    m, best = -np.inf, -1
    for t in range(l2c, max(start_min, l2c - LOOKBACK) - 1, -1):
        if h[t] < m:  # ties: an earlier equal high is still a record, so the earliest one can win
            continue
        m = h[t]
        if l2c - t < dur:
            continue
        leg = h[t] - lo[l2c]
        if leg <= 0:
            continue
        runmin = np.minimum.accumulate(lo[t:l2c])
        bounce = (h[t + 1:l2c + 1] - runmin).max(initial=0)
        if bounce > retr * leg:
            continue
        path = np.abs(np.diff(c[t:l2c + 1])).sum()
        if path == 0 or abs(c[l2c] - c[t]) / path < eff:
            continue
        best = t
    return best


_CACHE: dict[str, pd.DataFrame] = {}
CAND_COLS = ["side", "signal", "window", "l1c", "l2c", "h1c", "L2", "L1", "ll", "H1", "U", "close", "ws", "l2_rel",
             "sig_rel", "ref_lo", "sweep_fh", "sweep_30", "body", "engulf", "struct", *(f"A_{e}" for e in EXTENSIONS),
             *(f"T_{e}" for e in EXTENSIONS)]


def _content_key(df: pd.DataFrame) -> str:
    """Hash of every input the candidates read (timestamps, OHLC, contract), so a frame with the same span but other
    prices or contracts never reuses a cached result (Codex adversarial review 2026-11-19)."""
    hsh = hashlib.sha256()
    hsh.update(str(len(df)).encode())
    hsh.update(df["ts"].to_numpy("datetime64[ns]").view("int64").tobytes())
    for k in ("open", "high", "low", "close"):
        hsh.update(to_ticks(df[k]).tobytes())
    hsh.update(pd.util.hash_pandas_object(df["raw_symbol"], index=False).to_numpy().tobytes())
    return hsh.hexdigest()


def candidates(df: pd.DataFrame) -> pd.DataFrame:
    """Every type-3 MSB in any window, both sides, with the features all versions filter on. Cached per frame
    content (one entry)."""
    key = _content_key(df)
    if key in _CACHE:
        return _CACHE[key]
    out = _candidates(df)
    _CACHE.clear()
    _CACHE[key] = out
    return out


def _ref_hours(df: pd.DataFrame, mins: dict, sym, h, lo, o, c) -> dict[str, pd.DataFrame]:
    """Per window and trading day: reference hour OHLC, the 60 bars before it (open/close), first window bar."""
    day = pd.factorize(df["trading_day"])[0]
    out = {}
    for w, (clock, ref, wd) in WINDOWS.items():
        m = mins[clock]
        rel = (m - ref) % 1440
        in_ref = rel < 60
        idx = np.flatnonzero(in_ref)
        g = pd.DataFrame({"day": day[idx], "i": idx})
        agg = g.groupby("day")["i"].agg(["first", "last", "count"])
        a, b = agg["first"].to_numpy(), agg["last"].to_numpy()
        # ref high/low over a..b: reduceat over the ref bars (contiguous per day)
        starts = np.searchsorted(idx, a)
        hi = np.maximum.reduceat(h[idx], starts)
        lw = np.minimum.reduceat(lo[idx], starts)
        prev_a = np.maximum(a - 60, 0)
        out[w] = pd.DataFrame({"first": a, "last": b, "count": agg["count"].to_numpy(), "o": o[a], "c": c[b],
                               "h": hi, "l": lw, "po": o[prev_a], "pc": c[np.maximum(a - 1, 0)],
                               "prev_ok": (a - 60 >= 0) & (sym[prev_a] == sym[a])}, index=agg.index)
        out[w]["wd_ok"] = True if wd is None else (mins["wd"][a] == wd)
    return out


def _candidates(df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    if n < 3:
        return pd.DataFrame(columns=CAND_COLS)
    mins = _local_minutes(df)
    day = pd.factorize(df["trading_day"])[0]
    sym = pd.factorize(df["raw_symbol"])[0]
    H, L, O, C = (to_ticks(df[k]) for k in ("high", "low", "open", "close"))
    base = build_candles(df, "1m")
    if len(base) != n or not (base.avail == np.arange(n)).all():
        raise RuntimeError("1m candles must map 1:1 onto bars")
    refs = _ref_hours(df, mins, sym, H, L, O, C)
    # first bar of each run of one contract and one trading day (unadjusted prices: no input may cross it)
    cut = np.r_[True, (sym[1:] != sym[:-1]) | (day[1:] != day[:-1])]
    seg_start = np.maximum.accumulate(np.where(cut, np.arange(n), 0))
    # 1h owner-rule structure as known at each bar's close (both sides read it in original space)
    s1h = swing_state(df, "1h", prev=True)
    bull = (s1h["1h_sh"] > s1h["1h_sh2"]) & (s1h["1h_sl"] > s1h["1h_sl2"])
    bear = (s1h["1h_sh"] < s1h["1h_sh2"]) & (s1h["1h_sl"] < s1h["1h_sl2"])
    struct = np.where(bull.to_numpy(), 1, np.where(bear.to_numpy(), -1, 0))
    # the oldest 1h point in the comparison, minus its left candle, must be in the bar's contract
    oldest = np.minimum(s1h["1h_sh2_ts"].to_numpy("datetime64[ns]").astype("int64"),
                        s1h["1h_sl2_ts"].to_numpy("datetime64[ns]").astype("int64"))
    tsv = df["ts"].to_numpy("datetime64[ns]").astype("int64")
    ob = np.clip(np.searchsorted(tsv, oldest) - 60, 0, n - 1)
    struct = np.where(sym[ob] == sym, struct, 0)  # NaT (no points) gives a huge negative -> bar 0: abstain below
    struct[(s1h["1h_sh2"].isna() | s1h["1h_sl2"].isna()).to_numpy()] = 0
    c30 = build_candles(df, "30m")
    rows = []
    for side in (1, -1):
        cd = base if side == 1 else base.mirrored()
        h, lo, c = cd.h, cd.l, cd.c
        _, st = detect(cd)
        # state known at bar i = st[i-1] (candle i-1 is processed when candle i closes)
        sh_p, sh_c, sl_p, sl_c, sl2_p, sl2_c, newest = (
            np.r_[-1, st[k][:-1]] for k in ("sh_price", "sh_candle", "sl_price", "sl_candle", "sl2_price",
                                               "sl2_candle", "newest"))
        newest[0] = 0
        above = (sh_c >= 0) & (c > sh_p)
        idx = np.flatnonzero(above)
        _, first = np.unique(sh_c[idx], return_index=True)
        msb = idx[first]  # the first close above each swing high (MSB candidate)
        # alternation (owner rule 1) puts H1 between L1 and L2; one candle may hold two points (Codex 2026-11-19)
        # the lower low (type 3) is kept as a column: `shift` = any is a control without it (not in GRID)
        ok = (newest[msb] == LOW) & (sl2_c[msb] >= 0) & (sl_c[msb] >= 0)
        msb = msb[ok]
        l30 = c30.l if side == 1 else -c30.h
        for w, (clock, ref, _) in WINDOWS.items():
            rel = (mins[clock][msb] - ref) % 1440
            sel = msb[(rel >= 60) & (rel < 120)]
            R = refs[w]
            for i in sel:
                d = day[i]
                if d not in R.index:
                    continue
                r = R.loc[d]
                if not r["wd_ok"] or r["last"] >= i:
                    continue
                l2c, l1c, h1c = int(sl_c[i]), int(sl2_c[i]), int(sh_c[i])
                a = max(l1c - 1, 0)
                if a < seg_start[i] or int(r["first"]) < seg_start[i]:
                    continue  # unadjusted prices: structure and reference hour in one contract and one session
                ws = int(r["last"]) + 1  # first window bar
                rl = (mins[clock][l2c] - ref) % 1440
                ref_lo = r["l"] if side == 1 else -r["h"]
                j30 = np.searchsorted(c30.avail, l2c, side="left") - 1  # last 30m candle complete before L2's bar
                rows.append({
                    "side": side, "signal": int(i), "window": w, "l1c": l1c, "l2c": l2c, "h1c": h1c,
                    "L2": int(lo[l2c]), "L1": int(lo[l1c]), "ll": bool(lo[l2c] < lo[l1c]),
                    "H1": int(sh_p[i]), "U": int(h[l2c:i + 1].max()),
                    "close": int(c[i]), "ws": ws, "l2_rel": int(rl), "sig_rel": int((mins[clock][i] - ref) % 1440),
                    "ref_lo": int(ref_lo), "sweep_fh": bool(lo[l2c] < ref_lo and l2c >= ws and c[i] > ref_lo),
                    "sweep_30": bool(j30 >= 0 and c30.avail[j30] < l2c and lo[l2c] < l30[j30]
                                     and c30.first[j30] >= int(r["first"])),
                    "body": int(np.sign(r["c"] - r["o"])) * side,
                    "engulf": bool(r["prev_ok"] and np.sign(r["c"] - r["o"]) == side
                                   and np.sign(r["pc"] - r["po"]) == -side
                                   and max(r["o"], r["c"]) > max(r["po"], r["pc"])
                                   and min(r["o"], r["c"]) < min(r["po"], r["pc"])),
                    "struct": int(struct[ws - 1]) * side,
                })
                rec = rows[-1]
                for e, (dur, retr, eff) in EXTENSIONS.items():
                    t = _extension(h, lo, c, l2c, int(seg_start[i]), dur, retr, eff)  # bounded before choosing
                    rec[f"A_{e}"] = int(h[t]) if t >= 0 else np.nan
                    rec[f"T_{e}"] = int(t) if t >= 0 else np.nan  # origin bar (studies)
    return pd.DataFrame(rows, columns=CAND_COLS)  # same schema when nothing qualifies


def orders(cand: pd.DataFrame, p: dict) -> pd.DataFrame:
    """Filter candidates to one version and price its bracket (side space ticks -> $)."""
    w, ctx, bias, ext, tgt = p["window"], p["context"], p["bias"], p["ext"], p["target"]
    if w not in WINDOWS or ctx not in CONTEXTS or bias not in BIASES or ext not in EXTENSIONS or tgt not in TARGETS:
        raise ValueError(f"bad params {p}")
    x = cand.loc[(cand["window"] == w).to_numpy(bool)]
    if p.get("shift", "t3") == "t3":
        x = x.loc[x["ll"].to_numpy(bool)]  # .loc + numpy mask: an empty object column must not select columns
    elif p["shift"] != "any":
        raise ValueError("shift must be t3 (lower low, the PDF) or any (control)")
    x = x[x[f"A_{ext}"].notna()]
    if ctx == "fh":
        x = x.loc[x["sweep_fh"].to_numpy(bool)]
    elif ctx == "reb30":
        x = x.loc[(x["sweep_30"].to_numpy(bool)) & (x["l2_rel"].to_numpy(float) >= 90)]
    if bias == "body":
        x = x[x["body"] == 1]
    elif bias == "engulf":
        x = x.loc[x["engulf"].to_numpy(bool)]
    elif bias == "struct":
        x = x[x["struct"] == 1]
    L2, U = x["L2"].to_numpy(), x["U"].to_numpy()
    entry = L2 + (U - L2) // 2
    risk = entry - L2
    if tgt == "mid":
        target = (x[f"A_{ext}"].to_numpy().astype(np.int64) + L2) // 2  # floor: the nearer tick to entry
    else:
        k = 1.5 if tgt == "r1.5" else 2.0
        target = entry + np.ceil(k * risk).astype(np.int64)  # at least k R (side-space ceiling)
    keep = (risk >= MIN_RISK) & (target > entry)
    x, entry, target, L2 = x[keep], entry[keep], target[keep], L2[keep]
    sd = x["side"].to_numpy()
    return pd.DataFrame({"signal": x["signal"].to_numpy(), "side": sd, "limit": sd * entry * TICK,
                         "stop": sd * L2 * TICK, "target": sd * target * TICK}).sort_values("signal", kind="stable")


class Strategy(Base):
    NAME = "cbr"
    ABOUT = ("Tomtrades CBR 1h/1m model mapped to CL: in the hour after a reference hour, a 20+ minute one-way "
             "extension ends in a 1m type-3 shift (owner swings: lower low then close above the last swing high). "
             "Limit at 50% of the MSB move, stop at the shift low, target extension midpoint or 1.5R/2R.")
    PARAMS = {"window": "asia_utc", "context": "fh", "bias": "none", "ext": "e20", "target": "mid", "attempts": 2,
              "shift": "t3"}
    GRID = {"window": list(WINDOWS), "context": list(CONTEXTS), "bias": list(BIASES), "ext": list(EXTENSIONS),
            "target": list(TARGETS), "attempts": [1, 2]}

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        o = orders(candidates(df), p)
        o = o.drop_duplicates("signal", keep="first")  # long and short on one bar: long first (guard)
        bars = o["signal"].to_numpy(np.int64)
        # a newer setup cancels an unfilled older order: it works through the newer signal's bar
        nxt = np.r_[np.diff(bars), 100_000][:len(bars)]  # [:len] keeps the empty case empty
        cap = np.minimum(nxt, EXPIRE_BARS)
        f = o["target"].to_numpy()
        return pd.DataFrame({"side": o["side"].astype(int).to_numpy(), "limit": o["limit"].round(2).to_numpy(),
                             "stop": o["stop"].round(2).to_numpy(), "target": np.round(f, 2),
                             "expire": cap.astype(np.int64), "kill": np.round(f, 2)}, index=bars)

    def day_rules(self, trades: pd.DataFrame, p: dict) -> pd.DataFrame:
        """At most `attempts` filled trades per trading day; done for the day after the first winning exit."""
        if trades.empty:
            return trades
        keep = []
        for _, g in trades.groupby("trading_day", sort=False):
            for k, (i, net) in enumerate(zip(g.index, g["net"], strict=True)):
                if k >= p["attempts"]:
                    break
                keep.append(i)
                if net > 0:
                    break
        return trades.loc[keep]
