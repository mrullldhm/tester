"""Previous-day level + owner swing structure. Hypothesis and rules: docs/strategies/pd_swing/README.md."""

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.indicators import in_session, tf_candles, tf_minutes
from cltester.strategy import Base
from cltester.swings import swing_state
from strategies.purple_pa import previous_day_levels

MISSING = np.iinfo(np.int64).min
VARIANTS = ("P1", "P2a", "P2b", "P3a", "P3b")
PAIRS = {"5m": "1h", "15m": "4h"}  # declared base/context pairs (docs/strategies/pd_swing/README.md)


def context_tf(tf: str, ctx: str) -> str:
    """The context timeframe for base tf: "auto" picks the declared pair; any other pair is refused."""
    if tf not in PAIRS:
        raise ValueError(f"tf {tf} not in {sorted(PAIRS)}")
    if ctx not in ("auto", PAIRS[tf]):
        raise ValueError(f"ctx {ctx} does not pair with tf {tf}; declared pairs: {PAIRS}")
    return PAIRS[tf]


def _ticks(s: pd.Series) -> np.ndarray:
    v = s.to_numpy(dtype=float)
    out = np.full(len(v), MISSING, dtype=np.int64)
    ok = ~np.isnan(v)
    out[ok] = np.round(v[ok] / TICK).astype(np.int64)
    return out


def _state(df: pd.DataFrame, tf: str) -> dict[str, np.ndarray]:
    s = swing_state(df, tf, prev=True)
    out = {k: _ticks(s[f"{tf}_{k}"]) for k in ("sh", "sl", "sh2", "sl2")}
    for k in ("sh", "sl"):
        out[f"{k}_ts"] = pd.DatetimeIndex(s[f"{tf}_{k}_ts"]).as_unit("ns").asi8  # NaT = int64 min
    return out


def find_gap(lo_q: int, hi_q: int, min_q2: int, sd: int, w0: int, prot: int, end: int, c: dict) -> int:
    """First gap candle q in [lo_q, hi_q] with q < end, or -1. The window w0 .. q (through the bar where q is known)
    stays on one contract, else the setup ends; a candidate whose gap reads a candle from another contract is skipped.
    Protection must hold on the raw 1m bars from w0's first bar through the bar where q is known (av[q]: later than
    q's own bars when its last minute is missing). c: candle arrays h, l, sym, live,
    first, av and 1m arrays h1, l1, sym1 (contract per 1m bar)."""
    h, l, sym = c["h"], c["l"], c["sym"]  # noqa: E741
    for q in range(lo_q, min(hi_q, end - 1) + 1):
        if q < 2:
            continue
        raw = c["sym1"][c["first"][w0]:c["av"][q] + 1]  # the setup's 1m bars through the signal bar
        if (raw != raw[0]).any():  # a roll inside the setup (or before q is known) ends it
            return -1
        if len(set(sym[q - 2:q + 1])) != 1:  # the gap reads a candle from before a roll: skip this candidate
            continue
        a, z = c["first"][w0], c["av"][q] + 1
        broke = c["l1"][a:z].min() < prot if sd == 1 else c["h1"][a:z].max() > prot
        if broke:
            return -1
        gap = h[q - 2] < l[q] if sd == 1 else l[q - 2] > h[q]
        if q - 2 >= min_q2 and gap and c["live"][q]:
            return q
    return -1


class Strategy(Base):
    NAME = "pd_swing"
    ABOUT = "First touch of the previous day's high/low filtered by owner swing structure; purple gap entry, 1R."
    PARAMS = {"variant": "P1", "tf": "5m", "ctx": "auto", "expire_candles": 4, "rr": 1.0}
    GRID = {"variant": list(VARIANTS), "tf": ["5m", "15m"]}  # ctx "auto" follows tf (PAIRS)
    DEPENDS = ("purple_pa",)

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        if p["variant"] not in VARIANTS:
            raise ValueError(f"variant {p['variant']} not in {VARIANTS}")
        ctx = context_tf(p["tf"], p["ctx"])
        cols = ["side", "limit", "stop", "target", "expire_min", "void"]
        n = len(df)
        cd = tf_candles(df, p["tf"])
        cd = cd[cd["avail"].to_numpy() < n].reset_index(drop=True)
        if len(cd) < 3:
            return pd.DataFrame(columns=cols, index=pd.Index([], dtype=int))
        h, l = (np.round(cd[k].to_numpy() / TICK).astype(np.int64) for k in ("high", "low"))  # noqa: E741
        av, first = cd["avail"].to_numpy(), cd["first"].to_numpy()
        cts = pd.DatetimeIndex(cd["ts"]).as_unit("ns").asi8
        live = in_session(df, cd)
        sym1 = pd.factorize(df["raw_symbol"])[0]
        sym = sym1[first]
        h1 = np.round(df["high"].to_numpy() / TICK).astype(np.int64)
        l1 = np.round(df["low"].to_numpy() / TICK).astype(np.int64)
        ts1 = pd.DatetimeIndex(df["ts"]).as_unit("ns").asi8
        bs, cs = _state(df, p["tf"]), _state(df, ctx)
        days, day_id = np.unique(cd["day"].to_numpy(), return_inverse=True)
        prev_ok, dh, dl = previous_day_levels(df, days)
        v = p["variant"]

        arrays = {"h": h, "l": l, "sym": sym, "live": live, "first": first, "av": av, "h1": h1, "l1": l1, "sym1": sym1}

        def find(lo_q: int, hi_q: int, min_q2: int, sd: int, w0: int, prot: int, end: int) -> int:
            return find_gap(lo_q, hi_q, min_q2, sd, w0, prot, end, arrays)

        def kept(w0: int, q: int, sd: int, prot: int) -> bool:
            return bool(l[w0:q + 1].min() >= prot) if sd == 1 else bool(h[w0:q + 1].max() <= prot)

        rows, idx = [], []
        starts = np.flatnonzero(np.r_[True, day_id[1:] != day_id[:-1]])
        ends = np.r_[starts[1:], len(cd)]
        for a, b in zip(starts, ends, strict=True):
            d = day_id[a]
            if not prev_ok[d]:
                continue
            for lev in (dh[d], dl[d]):
                # arm on the first candle wholly on one side, then the first touch uses the level up for the day
                sd, t = 0, -1
                for x in range(a, b):
                    if sd == 0:
                        sd = 1 if l[x] > lev else -1 if h[x] < lev else 0
                        continue
                    if (sd == 1 and l[x] <= lev) or (sd == -1 and h[x] >= lev):
                        t = x
                        break
                if t < 1 or first[t] < 1:
                    continue
                bt = first[t] - 1  # last 1m bar before the touch candle
                q, w0 = -1, t
                if v in ("P1", "P2a", "P2b"):
                    prot = cs["sl"][bt] if sd == 1 else cs["sh"][bt]
                    if prot == MISSING:
                        continue
                    if v == "P1":
                        k2 = ("sh", "sh2", "sl", "sl2")
                        sh, sh2, sl, sl2 = (cs[k][bt] for k in k2)
                        if MISSING in (sh, sh2, sl, sl2):
                            continue
                        up = sh > sh2 and sl > sl2
                        down = sh < sh2 and sl < sl2
                        if (sd == 1 and up) or (sd == -1 and down):
                            q = find(t + 1, t + 4, t - 1, sd, t, prot, b)
                    else:
                        hl = bs["sl"][bt] if sd == 1 else bs["sh"][bt]  # base HL (long) / LH (short) at the touch
                        if hl == MISSING:
                            continue
                        k = next((x for x in range(t, min(t + 4, b - 1) + 1)
                                  if (l[x] < hl if sd == 1 else h[x] > hl)), -1)
                        if k < 0 or not kept(t, k, sd, prot):
                            continue
                        if v == "P2a":
                            q = find(k + 1, t + 4, k - 1, sd, t, prot, b)
                        else:
                            q = self._p2b(sd, t, k, b, prot, h, l, av, cts, bs, find, kept)
                else:  # P3: touch candle is B or C
                    for bb in (t - 1, t):
                        q, w0, prot = self._p3(v, sd, bb, b, a, h, l, av, first, cts, h1, l1, ts1, bs, cs, find)
                        if q >= 0:
                            break
                if q < 0:
                    continue
                entry = l[q] if sd == 1 else h[q]
                stop = l[w0:q + 1].min() - 1 if sd == 1 else h[w0:q + 1].max() + 1
                risk = (entry - stop) * sd
                if risk < 1:
                    continue
                # protection stays frozen until the fill: the engine cancels the order if it breaks first
                rows.append((sd, entry * TICK, stop * TICK, (entry + sd * max(int(round(risk * p["rr"])), 1)) * TICK,
                             p["expire_candles"] * tf_minutes(p["tf"]), prot * TICK))
                idx.append(av[q])
        out = pd.DataFrame(rows, columns=cols, index=pd.Index(idx, dtype=int)).astype(
            {"side": int, "limit": float, "stop": float, "target": float, "expire_min": int, "void": float})
        out = out[~out.index.duplicated(keep="first")]
        return out.sort_index()

    @staticmethod
    def _p2b(sd, t, k, b, prot, h, l, av, cts, bs, find, kept) -> int:  # noqa: E741
        """After the HL break at k: the first base swing on the other side whose candle starts after k (the LH for a
        long), then the first candle that strictly breaks it, then the gap within 4 candles."""
        lh, m = MISSING, -1
        key, kts = ("sh", "sh_ts") if sd == 1 else ("sl", "sl_ts")
        for x in range(k, b):
            if bs[kts][av[x]] > cts[k] and bs[key][av[x]] != MISSING:
                lh, m = bs[key][av[x]], x
                break
        if m < 0 or not kept(t, m, sd, prot):
            return -1
        for r in range(m + 1, b):
            took = h[r] > lh if sd == 1 else l[r] < lh
            broke = l[r] < prot if sd == 1 else h[r] > prot
            if broke:
                return -1
            if took:
                return find(r + 1, r + 4, r - 1, sd, t, prot, b)
        return -1

    @staticmethod
    def _p3(v, sd, bb, b, a, h, l, av, first, cts, h1, l1, ts1, bs, cs, find) -> tuple[int, int, int]:  # noqa: E741
        """Owner manipulation at the level (long: B breaks a base swing high, C touches B's low, B confirmed swing
        high; short mirror). Returns (q, window start B, protection) or (-1, -1, MISSING)."""
        cc = bb + 1
        if bb < a or cc >= b or first[bb] < 1:
            return -1, -1, MISSING
        bt = first[bb] - 1
        key, kts = ("sh", "sh_ts") if sd == 1 else ("sl", "sl_ts")
        lvl, lts = bs[key][bt], bs[kts][bt]
        prot = cs["sl"][bt] if sd == 1 else cs["sh"][bt]
        if MISSING in (lvl, prot):
            return -1, -1, MISSING
        j = int(np.searchsorted(ts1, lts))  # first 1m bar of the swing point's candle
        if j > bt:
            return -1, -1, MISSING
        since_h = h1[j:bt + 1].max() if sd == 1 else None
        since_l = l1[j:bt + 1].min() if sd == -1 else None
        if sd == 1 and not (since_h <= lvl < h[bb] and l[cc] <= l[bb]):
            return -1, -1, MISSING
        if sd == -1 and not (since_l >= lvl > l[bb] and h[cc] >= h[bb]):
            return -1, -1, MISSING
        own = h[bb] if sd == 1 else l[bb]  # B must be the owner swing point at C's completion
        if bs[key][av[cc]] != own or bs[kts][av[cc]] != cts[bb]:
            return -1, -1, MISSING
        if v == "P3a":
            return find(cc + 1, cc + 4, cc - 1, sd, bb, prot, b), bb, prot
        for r in range(cc + 1, min(cc + 3, b - 1) + 1):
            back = h[r] > h[bb] if sd == 1 else l[r] < l[bb]
            lost = l[r] < l[cc] if sd == 1 else h[r] > h[cc]
            if lost:
                return -1, -1, MISSING
            if back:
                return find(r + 1, cc + 4, r - 1, sd, bb, prot, b), bb, prot
        return -1, -1, MISSING
