"""Reaction Level Matrix [WillyAlgoTrader] mapped to CL (2026-11-19, Claude + Codex).
Spec, CL mapping and trial budget: docs/strategies/rlm/README.md. Original logic: studies/rlm/rlm_logic.pine.

Levels are price bands built online from swing points. The original finds swings with ta.pivothigh(6, 6) and weights
each touch by its reaction size; here every swing is an owner-rule point (cltester.swings) on one of several
timeframes and its weight is the TIMEFRAME (owner: the bigger the TF, the stronger the swing). One turning point counts
once: when a higher TF confirms the same extreme, the touch is upgraded to the higher weight.

A point becomes a touch when it is LOCKED: a newer opposite point exists after it in the structure, so rule 5 can no
longer replace it. Known at the close of the candle that makes it locked (detect state[k] is known when candle k+1
completes).

The level engine runs on completed candles of the signal timeframe S: age + cross with the candle close, register the
touches locked up to the candle's completion, pick the 3 nearest active levels per side, test the rejection candle.
Levels reset at every contract change (prices are not back-adjusted).
"""

import hashlib
from bisect import bisect_left

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.data import to_ticks
from cltester.indicators import atr_rma
from cltester.strategy import Base
from cltester.swings import HIGH, LOW, TIMEFRAMES, build_candles, detect

# --- original constants (rlm_logic.pine) ---
STRUCT_ATR_LEN = 34
RISK_ATR_LEN = 14
MIN_HALF_WIDTH_ATR = 0.15
SCORE_SCALE = 6.0
POLARITY_BONUS = 1.25
CROSS_PENALTY = 0.7
MIN_STRENGTH = 0.25
MAX_LEVELS = 60
MERGE_PASSES = 5
MIN_TOUCHES = 2
HALF_LIFE = 500  # signal-TF bars
PER_SIDE = 3
COOLDOWN = 10  # signal-TF bars per level
WICK_BUFFER_ATR = 0.25
WICK_MIN_ATR = 0.5

# --- CL mapping ---
SOURCES = ("5m", "15m", "1h", "4h", "1d")
# same 1..3.5 range as the original reaction weight
TF_WEIGHT = {"5m": 1.0, "15m": 1.5, "1h": 2.0, "4h": 3.0, "1d": 3.5}
COMBOS = [(clv, score) for clv in (0.6, 0.75) for score in (0, 50, 70)]  # rejection close strength x min level score
MIN_RISK = 5  # ticks
EXPIRE_BARS = 1  # signal-TF bars an unfilled entry works (also killed by a target touch)
RTH = (8 * 60 + 30, 13 * 60 + 30)  # CT minutes: signal candle completes inside [08:30, 13:30)
CAP = MAX_LEVELS + 2

CAND_COLS = ["c", "bar", "side", "combo", "mid", "lo", "hi", "score", "touches", "polar", "maxw", "strength",
             "crosses", "age", "atr34", "atr14", "o", "h", "l", "cl", "c_open"]


def _content_key(df: pd.DataFrame) -> str:
    hsh = hashlib.sha256()
    hsh.update(str(len(df)).encode())
    hsh.update(df["ts"].to_numpy("datetime64[ns]").view("int64").tobytes())
    for k in ("open", "high", "low", "close"):
        hsh.update(to_ticks(df[k]).tobytes())
    hsh.update(pd.util.hash_pandas_object(df["raw_symbol"], index=False).to_numpy().tobytes())
    return hsh.hexdigest()


_EVENTS: dict[tuple, pd.DataFrame] = {}
_CANDS: dict[tuple, pd.DataFrame] = {}
EV_COLS = ["known", "op", "kind", "price", "first", "last", "ref_first", "candle"]


def swing_events(df: pd.DataFrame, tf: str, reg: str, key: str | None = None) -> pd.DataFrame:
    """Owner swing points on tf as touch events, in the order they become known (1m bar `known`, at whose close the
    detect state of candle k is known = avail[k+1]).
    reg="lock": op +1 when the point is locked (a newer opposite point exists above it in the structure, so rule 5
    can no longer replace it); read from the top-4 state. A locked point removed later by a deep rule-4 cascade
    stays registered (documented approximation).
    reg="confirm": exact structure changes from the detector (observer hook): op +1 when a point enters the
    structure, op -1 when it leaves it (rule-5 replacement or rule-4 removal at any depth; a point that resurfaces
    after a cascade enters again). Codex adversarial review 2026-11-20 replaced an inference from the top-4 state.
    first / last: 1m bars of the extreme's candle; ref_first: first 1m bar of the candle left of it (its rule-2/3
    reference, used by the roll guard)."""
    key = key or _content_key(df)
    if (key, tf, reg) in _EVENTS:
        return _EVENTS[(key, tf, reg)]
    cd = build_candles(df, tf)
    n_c, n = len(cd), len(df)
    rows = []

    def row(known: int, op: int, kind: int, cnd: int, price: int) -> tuple:
        return (known, op, kind, price, int(cd.first[cnd]), int(cd.last[cnd]), int(cd.first[max(cnd - 1, 0)]), cnd)

    if reg == "lock":
        _, st = detect(cd)
        seen: set[tuple[int, int]] = set()
        cols = (("sh", HIGH), ("sl", LOW), ("sh2", HIGH), ("sl2", LOW))
        for k in range(n_c - 1):
            known = int(cd.avail[k + 1])
            if known >= n:
                break
            nw = st["newest"][k]
            if nw == 0:
                continue
            top = "sh" if nw == HIGH else "sl"
            for col, kind in cols:
                cnd = int(st[f"{col}_candle"][k])
                if col != top and cnd >= 0 and (kind, cnd) not in seen:
                    seen.add((kind, cnd))
                    rows.append(row(known, 1, kind, cnd, int(st[f"{col}_price"][k])))
    else:
        mirror: list = []  # the structure as last seen (Point objects); only its top changes between candles

        def observe(k: int, stack: list) -> None:
            i = min(len(mirror), len(stack))
            while i > 0 and mirror[i - 1] is not stack[i - 1]:  # below the first identical point nothing changed
                i -= 1
            old = {(p.kind, p.candle): p.price for p in mirror[i:]}
            new = {(p.kind, p.candle): p.price for p in stack[i:]}
            mirror[i:] = stack[i:]
            if k + 1 >= n_c or int(cd.avail[k + 1]) >= n:
                return
            known = int(cd.avail[k + 1])
            for (kind, cnd), price in old.items():
                if (kind, cnd) not in new:
                    rows.append(row(known, -1, kind, cnd, price))
            for (kind, cnd), price in new.items():
                if (kind, cnd) not in old:
                    rows.append(row(known, 1, kind, cnd, price))

        detect(cd, observer=observe)
    out = pd.DataFrame(rows, columns=EV_COLS)
    _EVENTS[(key, tf, reg)] = out
    return out


class Book:
    """Level memory in fixed-size numpy arrays (slot per level, `alive` mask). Prices in ticks (float).

    A touch is one turning point (key = int). Its entry holds the weight of every swing point (pid = (tf, kind,
    candle)) that confirmed the same extreme; the touch weighs max of them. Strength share of a touch:
    base[key] * exp(ls[slot]), ls = log of every decay and cross penalty the slot took. When a level dies its touches
    die with it (entries, pids and shares are purged)."""

    def __init__(self, n_combo: int, tol: float):
        self.tol = tol
        z = lambda: np.zeros(CAP)  # noqa: E731
        self.lo, self.hi, self.mid = z(), z(), z()
        self.sw, self.swp, self.swp2, self.strength = z(), z(), z(), z()
        self.touches, self.ht, self.lt, self.crosses = z(), z(), z(), z()
        self.side, self.sidebar, self.first_c, self.maxw, self.ls = z(), z(), z(), z(), z()
        self.alive = np.zeros(CAP, dtype=bool)
        self.lastsig = np.full((CAP, n_combo), -1e9)
        self.decay = 0.5 ** (1.0 / HALF_LIFE)
        self.clear()

    def clear(self) -> None:
        self.alive[:] = False
        self.keys: list[list[int]] = [[] for _ in range(CAP)]  # touch keys owned by each slot
        self.owner: dict[int, int] = {}  # key -> slot
        self.entries: dict[int, dict] = {}  # key -> {kind, price, first, last, high, w: {pid: weight}}
        self.registry: dict[tuple[int, int], list[int]] = {}  # (kind, price) -> keys
        self.pid2key: dict[tuple, int] = {}
        self.base: dict[int, float] = {}
        self.next_key = 0

    def _purge(self, key: int) -> None:
        e = self.entries.pop(key)
        for pid in e["w"]:
            self.pid2key.pop(pid, None)
        self.registry[(e["kind"], e["price"])].remove(key)
        self.owner.pop(key, None)
        self.base.pop(key, None)

    def _kill(self, s: int) -> None:
        self.alive[s] = False
        for k in self.keys[s]:
            self._purge(k)
        self.keys[s] = []

    def _w(self, key: int) -> float:
        w = self.entries[key]["w"]
        return max(w.values()) if w else 0.0

    def refit(self, s: int, a: float) -> None:
        m = self.swp[s] / self.sw[s]
        vr = self.swp2[s] / self.sw[s] - m * m
        hw = min(max(np.sqrt(max(vr, 0.0)), a * MIN_HALF_WIDTH_ATR), a * self.tol)
        self.mid[s], self.lo[s], self.hi[s] = m, m - hw, m + hw

    def _add(self, s: int, key: int, price: float, w: float, is_high: bool, a: float) -> None:
        self.sw[s] += w
        self.swp[s] += w * price
        self.swp2[s] += w * price * price
        self.strength[s] += w
        self.base[key] = w * np.exp(-self.ls[s])
        self.touches[s] += 1
        self.ht[s] += is_high
        self.lt[s] += not is_high
        self.maxw[s] = max(self.maxw[s], w)
        self.keys[s].append(key)
        self.owner[key] = s
        self.refit(s, a)

    def _merge(self, t: int, o: int, a: float) -> None:
        for arr in (self.sw, self.swp, self.swp2, self.strength, self.touches, self.ht, self.lt):
            arr[t] += arr[o]
        self.crosses[t] = max(self.crosses[t], self.crosses[o])
        self.first_c[t] = min(self.first_c[t], self.first_c[o])
        self.maxw[t] = max(self.maxw[t], self.maxw[o])
        self.lastsig[t] = np.maximum(self.lastsig[t], self.lastsig[o])
        for k in self.keys[o]:
            self.owner[k] = t
            self.base[k] *= np.exp(self.ls[o] - self.ls[t])
        self.keys[t].extend(self.keys[o])
        self.keys[o] = []
        self.alive[o] = False
        self.refit(t, a)

    def _shift(self, s: int, key: int, dw: float, frac: float, price: float) -> None:
        """Change one touch's weight by dw on slot s. Upgrade (dw > 0): strength + dw from now on (no backdating).
        Removal: the touch gives back `frac` of its current strength share (decays and cross penalties included)."""
        self.sw[s] += dw
        self.swp[s] += dw * price
        self.swp2[s] += dw * price * price
        if dw > 0:
            self.strength[s] += dw
            self.base[key] += dw * np.exp(-self.ls[s])
        else:
            b = self.base[key]
            self.strength[s] = max(self.strength[s] - frac * b * np.exp(self.ls[s]), 0.0)
            self.base[key] = b * (1.0 - frac)

    def touch(self, pid: tuple, kind: int, price: int, first: int, last: int, w: float, a: float, close: float,
              c: int) -> None:
        """Register a swing point (pid = (tf, kind, candle)). Same extreme already a live touch (same kind and price,
        one candle inside the other): the touch takes the larger weight, no extra touch. When the new candle encloses
        several live touches of that price (e.g. a 5m double bottom inside one 1h candle), they are one extreme on
        this timeframe and coalesce into one touch (Codex adversarial review 2026-11-20). A touch's candle bounds
        widen to the largest enclosing candle, so later points inside it match too."""
        nested = [k for k in self.registry.get((kind, price), [])
                  if (first <= self.entries[k]["first"] and self.entries[k]["last"] <= last)
                  or (self.entries[k]["first"] <= first and last <= self.entries[k]["last"])]
        if nested:
            key = nested[0]
            e = self.entries[key]
            old = self._w(key)
            for k2 in nested[1:]:
                self._absorb(key, k2, a)
            e["w"][pid] = w
            self.pid2key[pid] = key
            e["first"], e["last"] = min(e["first"], first), max(e["last"], last)
            new = self._w(key)
            s = self.owner[key]
            if new > old:
                self._shift(s, key, new - old, 0.0, price)
                self.maxw[s] = max(self.maxw[s], new)
                self.refit(s, a)
                self._merge_overlaps(s, a)
            return
        key = self.next_key
        self.next_key += 1
        self.entries[key] = {"kind": kind, "price": price, "first": first, "last": last, "high": kind == HIGH,
                             "w": {pid: w}}
        self.registry.setdefault((kind, price), []).append(key)
        self.pid2key[pid] = key
        is_high = kind == HIGH
        alive = np.flatnonzero(self.alive)
        t = -1
        if len(alive):
            d = np.abs(self.mid[alive] - price)
            ok = np.flatnonzero(d <= a * self.tol)
            if len(ok):
                best = d[ok].min()
                t = int(alive[ok[np.flatnonzero(d[ok] == best)[-1]]])  # ties: the later level (Pine `<=`)
        if t >= 0:
            self._add(t, key, price, w, is_high, a)
            self._merge_overlaps(t, a)
        else:
            s = int(np.flatnonzero(~self.alive)[0])
            for arr in (self.sw, self.swp, self.swp2, self.strength, self.touches, self.ht, self.lt, self.crosses,
                        self.maxw, self.ls):
                arr[s] = 0.0
            self.lastsig[s] = -1e9
            self.keys[s] = []
            self.side[s] = 1 if close > price else -1
            self.sidebar[s] = c
            self.first_c[s] = c
            self.alive[s] = True
            self._add(s, key, price, w, is_high, a)
        while self.alive.sum() > MAX_LEVELS:
            al = np.flatnonzero(self.alive)
            self._kill(int(al[np.argmin(self.strength[al])]))

    def _absorb(self, key: int, k2: int, a: float) -> None:
        """Touch k2 is the same extreme as touch key: take k2 off its level (its current strength share, one touch)
        and move its swing points into key's entry. The caller re-weighs key."""
        e, e2 = self.entries[key], self.entries.pop(k2)
        s2 = self.owner.pop(k2)
        w2 = max(e2["w"].values())
        self._shift(s2, k2, -w2, 1.0, e2["price"])
        self.base.pop(k2, None)
        self.touches[s2] -= 1
        self.ht[s2] -= e2["high"]
        self.lt[s2] -= not e2["high"]
        self.keys[s2].remove(k2)
        self.registry[(e2["kind"], e2["price"])].remove(k2)
        for p2, w in e2["w"].items():
            e["w"][p2] = w
            self.pid2key[p2] = key
        e["first"], e["last"] = min(e["first"], e2["first"]), max(e["last"], e2["last"])
        if s2 != self.owner[key] and (self.touches[s2] <= 0 or self.sw[s2] <= 1e-9):
            self._kill(s2)
        elif self.alive[s2]:
            self.maxw[s2] = max((self._w(k) for k in self.keys[s2]), default=0.0)
            self.refit(s2, a)

    def withdraw(self, pid: tuple, a: float, c: int) -> None:
        """confirm mode: a swing point left the owner structure. Its weight leaves the touch (the touch drops to the
        strongest point that still holds the same extreme, or goes away). History is not rewritten."""
        key = self.pid2key.pop(pid, None)
        if key is None:
            return
        e = self.entries[key]
        old = self._w(key)
        del e["w"][pid]
        new = self._w(key)
        s = self.owner[key]
        if new < old:
            self._shift(s, key, new - old, (old - new) / old, e["price"])
        if not e["w"]:
            self.touches[s] -= 1
            self.ht[s] -= e["high"]
            self.lt[s] -= not e["high"]
            self.keys[s].remove(key)
            self._purge(key)
        self.maxw[s] = max((self._w(k) for k in self.keys[s]), default=0.0)
        if self.touches[s] <= 0 or self.sw[s] <= 1e-9:
            self._kill(s)
        else:
            self.refit(s, a)

    def _merge_overlaps(self, t: int, a: float) -> None:
        for _ in range(MERGE_PASSES):
            again = False
            for k in np.flatnonzero(self.alive)[::-1]:
                if k != t and self.alive[k] and self.lo[k] <= self.hi[t] and self.lo[t] <= self.hi[k]:
                    self._merge(t, int(k), a)
                    again = True
            if not again:
                break

    def age_cross(self, close: float, decay: float, c: int) -> None:
        al = self.alive
        self.strength[al] *= decay
        self.ls[al] += np.log(decay)
        new = np.where(close > self.hi, 1.0, np.where(close < self.lo, -1.0, self.side))
        ch = al & (new != self.side)
        hit = ch & (self.touches >= MIN_TOUCHES)
        self.crosses[hit] += 1
        self.strength[hit] *= CROSS_PENALTY
        self.ls[hit] += np.log(CROSS_PENALTY)
        self.side[ch] = new[ch]
        self.sidebar[ch] = c
        for s in np.flatnonzero(al & (self.strength < MIN_STRENGTH)):
            self._kill(int(s))

    def score(self, s) -> np.ndarray:
        polar = (self.ht[s] > 0) & (self.lt[s] > 0)
        return 100.0 * (1.0 - np.exp(-self.strength[s] * np.where(polar, POLARITY_BONUS, 1.0) / SCORE_SCALE))

    def nearest(self, side: int, close: float) -> np.ndarray:
        cand = np.flatnonzero(self.alive & (self.touches >= MIN_TOUCHES) & (self.side == side))
        if not len(cand):
            return cand
        order = np.argsort(np.abs(close - self.mid[cand]), kind="stable")
        return cand[order[:PER_SIDE]]


def candidates(df: pd.DataFrame, sig_tf: str, reg: str, sources: str, weight: str, tol: float) -> pd.DataFrame:
    """Every rejection signal of the level engine, for all COMBOS at once (one row per candle, side and combo)."""
    key = _content_key(df)
    ck = (key, sig_tf, reg, sources, weight, tol)
    if ck in _CANDS:
        return _CANDS[ck]
    cd = build_candles(df, sig_tf)
    n_c = len(cd)
    m_sig = TIMEFRAMES[sig_tf]
    tfs = [t for t in SOURCES if (TIMEFRAMES[t] >= m_sig if sources == "all" else TIMEFRAMES[t] > m_sig)]
    ev = pd.concat([swing_events(df, t, reg, key).assign(tf=i, w=TF_WEIGHT[t] if weight == "tf" else 1.0)
                    for i, t in enumerate(tfs)], ignore_index=True)
    ev = ev.sort_values(["known", "tf", "op"], kind="stable")  # same bar: lower TF first, withdrawals first
    lk = ev[["known", "op", "kind", "price", "first", "last", "ref_first", "candle", "tf", "w"]].to_numpy()
    lk_known = ev["known"].to_numpy()
    h, lo, cl, opn = (cd.h.astype(float), cd.l.astype(float), cd.c.astype(float), cd.o.astype(float))
    sym = pd.factorize(df["raw_symbol"])[0]
    contract = np.cumsum(np.r_[False, sym[1:] != sym[:-1]])
    c_contract = contract[cd.last]
    mixed = contract[cd.first] != c_contract  # candle straddles a roll
    a34, a14 = np.full(n_c, np.nan), np.full(n_c, np.nan)  # ATR restarts with each contract (no roll gap in TR)
    for g in np.split(np.arange(n_c), np.flatnonzero(np.diff(c_contract)) + 1):
        g = g[~mixed[g]]
        if len(g):
            a34[g] = atr_rma(h[g], lo[g], cl[g], STRUCT_ATR_LEN).to_numpy()
            a14[g] = atr_rma(h[g], lo[g], cl[g], RISK_ATR_LEN).to_numpy()
    c_start = np.r_[0, np.flatnonzero(np.diff(contract)) + 1][c_contract]  # 1m bar where the candle's contract began
    tday = pd.factorize(df["trading_day"])[0]
    decay = 0.5 ** (1.0 / HALF_LIFE)
    book = Book(len(COMBOS), tol)
    rows = []
    p = 0  # next lock to register
    for c in range(n_c):
        if c and c_contract[c] != c_contract[c - 1]:
            book.clear()
        av = int(cd.avail[c])
        close = cl[c]
        a = a34[c] if np.isfinite(a34[c]) else 0.0
        if a > 0:
            book.age_cross(close, decay, c)
        while p < len(lk_known) and lk_known[p] <= av:
            kn, op, kind, price, first, last, ref_first, cnd, tfi, w = lk[p]
            p += 1
            pid = (int(tfi), int(kind), int(cnd))
            if op < 0:
                book.withdraw(pid, a, c)
                continue
            # the extreme and its left reference candle must be in the current contract (unadjusted prices)
            if a <= 0 or ref_first < c_start[c] or contract[int(kn)] != c_contract[c]:
                continue
            book.touch(pid, int(kind), int(price), int(first), int(last), float(w), a, close, c)
        # no signal from a candle that straddles a roll or completes in the next session (missing last minute)
        if a <= 0 or mixed[c] or contract[av] != c_contract[c] or not np.isfinite(a14[c]) \
                or tday[cd.first[c]] != tday[av]:
            continue
        rng = h[c] - lo[c]
        for side in (1, -1):
            sel = book.nearest(side, close)
            if not len(sel):
                continue
            if side == 1:
                clv = (close - lo[c]) / rng if rng > 0 else 0.5
                geo = (book.sidebar[sel] < c) & (lo[c] <= book.hi[sel]) & (close > book.hi[sel])
            else:
                clv = (h[c] - close) / rng if rng > 0 else 0.5
                geo = (book.sidebar[sel] < c) & (h[c] >= book.lo[sel]) & (close < book.lo[sel])
            if not geo.any():
                continue
            sc = book.score(sel)
            for ci, (cmin, smin) in enumerate(COMBOS):
                if clv < cmin:
                    continue
                ok = geo & (sc >= smin) & (c - book.lastsig[sel, ci] >= COOLDOWN)
                hit = np.flatnonzero(ok)
                if not len(hit):
                    continue
                s = int(sel[hit[0]])
                book.lastsig[s, ci] = c
                rows.append((c, av, side, ci, book.mid[s], book.lo[s], book.hi[s], float(sc[hit[0]]),
                             book.touches[s], bool(book.ht[s] > 0 and book.lt[s] > 0), book.maxw[s],
                             book.strength[s], book.crosses[s], c - book.first_c[s], a, a14[c], opn[c], h[c], lo[c],
                             close, cd.ts[c]))
    out = pd.DataFrame(rows, columns=CAND_COLS)
    out["sig_tf"] = sig_tf
    _CANDS[ck] = out
    return out


def build_orders(cand: pd.DataFrame, df: pd.DataFrame, p: dict) -> pd.DataFrame:
    """Orders (ticks, side space resolved) from the candidates of one combo. One row per signal bar; a long and a
    short on one candle: long only (original). Columns include features for the trade study."""
    ci = COMBOS.index((float(p["clv"]), int(p["score"])))
    s = cand[cand["combo"] == ci].copy()
    if s.empty:
        return s
    s = s.sort_values(["bar", "side"], ascending=[True, False], kind="stable").drop_duplicates("bar", keep="first")
    ctm = df["ct_minute"].to_numpy()[s["bar"].to_numpy()]
    s["ct_min"] = ctm
    if p["session"] == "rth":
        s = s[(s["ct_min"] >= RTH[0]) & (s["ct_min"] < RTH[1])]
    elif p["session"] != "all":
        s = s[in_window(pd.DatetimeIndex(s["c_open"]), p["session"])]
    side = s["side"].to_numpy()
    # side space: long as is, short negated
    cl, lo_c = (side * s["cl"]).to_numpy(), np.where(side == 1, s["l"], -s["h"])
    lvl_near = np.where(side == 1, s["hi"], -s["lo"])  # band edge price came back to
    lvl_far = np.where(side == 1, s["lo"], -s["hi"])
    a14 = s["atr14"].to_numpy()
    entry = np.where(p["entry"] == "close", cl, np.floor(lvl_near)).astype(float)
    if p["stop"] == "wick":
        raw = np.minimum(lo_c - WICK_BUFFER_ATR * a14, entry - WICK_MIN_ATR * a14)
    else:
        raw = np.minimum(lvl_far - WICK_BUFFER_ATR * a14, entry - WICK_MIN_ATR * a14)
    stop = np.floor(raw)
    risk = entry - stop
    k = {"r1": 1, "r2": 2, "r3": 3, "be3": 3, "be3opp": 3}[p["exit"]]
    target = entry + np.ceil(k * risk)
    s = s.assign(E=entry, S=stop, R=risk, T=target)
    return s[s["R"] >= MIN_RISK]


CLOCKS = {"ct": "America/Chicago", "myt": "Asia/Kuala_Lumpur", "ldn": "Europe/London"}


def in_window(candle_open: pd.DatetimeIndex, window: str) -> np.ndarray:
    """window "<clock>:<a>-<b>": keep candles whose OPEN hour on that clock is in a..b inclusive (wraps past
    midnight when a > b). Clocks: ct = exchange time (the n-th candle after the 17:00 CT open), myt = Malaysia
    (UTC+8, no daylight saving), ldn = London. Session/DST test: docs/strategies/rlm/README.md."""
    clock, _, span = window.partition(":")
    if clock not in CLOCKS or "-" not in span:
        raise ValueError(f"session must be all, rth or <ct|myt|ldn>:<a>-<b>, got {window!r}")
    a, b = (int(x) for x in span.split("-"))
    hour = candle_open.tz_convert(CLOCKS[clock]).hour.to_numpy()
    return (hour >= a) & (hour <= b) if a <= b else (hour >= a) | (hour <= b)


class Strategy(Base):
    NAME = "rlm"
    ABOUT = ("Reaction Level Matrix (WillyAlgoTrader) on CL: price levels from owner-rule swing points weighted by "
             "timeframe; buy a rejection candle at support (sell at resistance) with a limit, wick or band stop, "
             "R-multiple target.")
    PARAMS = {"sig_tf": "15m", "reg": "lock", "sources": "all", "weight": "tf", "tol": 0.6, "score": 50, "clv": 0.6,
              "entry": "close", "stop": "wick", "exit": "be3", "session": "all"}
    GRID = {"sig_tf": ["5m", "15m", "1h"], "reg": ["lock", "confirm"], "sources": ["all", "htf"],
            "weight": ["tf", "flat"], "tol": [0.4, 0.6, 1.0], "score": [0, 50, 70], "clv": [0.6, 0.75],
            "entry": ["close", "band"],
            "stop": ["wick", "band"], "exit": ["r1", "r2", "r3", "be3"], "session": ["all", "rth"]}

    def __init__(self) -> None:
        self._p: dict = {}
        self._opp: dict[int, list[int]] = {}
        self._side_hi: dict[int, np.ndarray] = {}

    def orders(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        cand = candidates(df, p["sig_tf"], p["reg"], p["sources"], p["weight"], float(p["tol"]))
        return build_orders(cand, df, p)

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        self._p = p
        o = self.orders(df, p)
        cols = ["side", "limit", "stop", "target", "expire_min", "kill"]
        if o.empty:
            return pd.DataFrame(columns=cols)
        side = o["side"].to_numpy()
        self._opp = {sd: sorted(o.loc[o["side"] == -sd, "bar"].astype(int)) for sd in (1, -1)}
        self._side_hi = {1: to_ticks(df["high"]), -1: -to_ticks(df["low"])}
        # frozen TP1 per signal (side-space ticks): intended limit + intended risk
        self._tp1 = dict(zip(o["bar"].astype(int), (o["E"] + o["R"]).astype(int), strict=True))
        tgt = side * o["T"].to_numpy() * TICK
        return pd.DataFrame({"side": side, "limit": np.round(side * o["E"].to_numpy() * TICK, 2),
                             "stop": np.round(side * o["S"].to_numpy() * TICK, 2), "target": np.round(tgt, 2),
                             "expire_min": EXPIRE_BARS * TIMEFRAMES[p["sig_tf"]], "kill": np.round(tgt, 2)},
                            index=o["bar"].astype(int).to_numpy())

    def manage(self, ctx):
        """be3: stop to the actual fill price once a bar after the fill bar reached the frozen TP1 (intended limit + 1R
        of the intended risk), effective from the next bar. be3opp (not in the grid): also close at the open after an
        opposite signal bar at or after the fill bar (original reversal exit)."""
        ex = self._p.get("exit")
        if ex not in ("be3", "be3opp"):
            return ctx.S, False
        st = ctx.state
        if "mx" not in st:
            st["mx"] = -10**12
        if ctx.m - 1 > ctx.j:
            st["mx"] = max(st["mx"], int(self._side_hi[ctx.side][ctx.m - 1]))
        stop = ctx.E if st["mx"] >= self._tp1[ctx.i] else ctx.S
        stop = max(stop, ctx.S)
        if ex == "be3opp":
            opp = self._opp[ctx.side]
            k = bisect_left(opp, ctx.j)
            if k < len(opp) and opp[k] <= ctx.m - 1:
                return stop, True
        return stop, False
