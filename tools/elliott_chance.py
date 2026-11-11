"""Pre-registered Elliott Wave chance checks (docs/strategies/elliott_wave/optimize/README.md).

Run through the resource guard:  .venv/bin/python tools/run_limited.py tools/elliott_chance.py
Development interval only. Writes the results table to stdout and one ledger line per test.
"""

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np

from strategies.elliott_wave import setups
from tvtester import swings as sw
from tvtester.experiment import DEV_END, data_hash, dev_bars
from tvtester.sessions import SESSIONS, local_clock

LONG, SHORT = 1, -1
WINDOW = 120
MIN_LEG = 20
SESSION_NAMES = ("asia", "london", "ny")
DEGREES = ("1m", "5m", "15m")
HYPOTHESES = ("H1", "H2", "H3", "H4", "H5")
PASS_MEAN, PASS_T = 0.4, 3.0
LEDGER = ROOT / "results" / "elliott_wave" / "ledger.jsonl"


def rnd(x: float) -> int:
    return int(np.floor(x + 0.5))


class Series:
    """One degree: 1m bars or closed candles, with the 1m bar at whose close each step is known."""

    def __init__(self, bars, degree: str):
        if degree == "1m":
            self.o, self.h, self.l, self.c = (np.asarray(x, dtype=np.int64) for x in (bars.o, bars.h, bars.l, bars.c))
            self.visible = np.arange(len(bars))
            self.hi_first = sw.open_rule_high_first(bars.o, bars.h, bars.l)
        else:
            cd = sw.candles(bars, degree)
            self.o, self.h, self.l, self.c = cd.o, cd.h, cd.l, cd.c
            self.visible, self.hi_first = cd.visible, cd.hi_first
        self.n = len(self.h)


def replay_swings(se: Series):
    """Owner Zig per series step: current swing high / low, and new-pivot events with the pivot list.

    Returns cur_h, cur_l (NONE when absent) and events {step: [(type, price, pivot step), ...]} recorded at
    the step where an opposite-type pivot is first appended (the list ends with that new pivot).
    """
    z = sw.Zig()
    H, L, hf = se.h.tolist(), se.l.tolist(), se.hi_first.tolist()
    n = se.n
    cur_h = np.full(n, sw.NONE, dtype=np.int64)
    cur_l = np.full(n, sw.NONE, dtype=np.int64)
    pivots: list[list] = []
    events: dict[int, list] = {}
    mismatch = 0
    for s in range(n):
        if s >= 2:
            k = s - 1
            hi_first = hf[k]
            add_h, add_l = z.pivots(H[k - 1], H[k], H[s], L[k - 1], L[k], L[s], bool(hi_first), k)
            order = ((sw.SH, add_h, H[k]), (sw.SL, add_l, L[k])) if hi_first else ((sw.SL, add_l, L[k]), (sw.SH, add_h, H[k]))
            for t, added, price in order:
                if not added:
                    continue
                if pivots and pivots[-1][0] == t:
                    pivots[-1] = [t, price, k]
                else:
                    pivots.append([t, price, k])
                    events[s] = (t, tuple(p[1] for p in pivots[-5:]))
                    if len(pivots) > 64:
                        del pivots[:-16]
        if z.invalidate(H[s], L[s]) and pivots:
            pivots.pop()
            events.pop(s, None)
        if pivots and z.pending and (pivots[-1][0] != z.last_type or pivots[-1][1] != z.last_price):
            mismatch += 1
        cur_h[s] = sw.NONE if z.cur_h is None else z.cur_h
        cur_l[s] = sw.NONE if z.cur_l is None else z.cur_l
    return cur_h, cur_l, events, mismatch


def awesome(se: Series) -> tuple[np.ndarray, np.ndarray]:
    s = se.h + se.l
    cs = np.concatenate([[0], np.cumsum(s)])
    ao = np.zeros(se.n, dtype=np.int64)
    valid = np.arange(se.n) >= 33
    i = np.flatnonzero(valid)
    ao[i] = 34 * (cs[i + 1] - cs[i - 4]) - 5 * (cs[i + 1] - cs[i - 33])
    return ao, valid


def ao_setups(se: Series, cur_h, cur_l):
    """H1 wave-4 crosses on the series: list of (step, dir, top, top step, base, base step, L, peak)."""
    ao, valid = awesome(se)
    H, L, a = se.h.tolist(), se.l.tolist(), ao.tolist()
    out = []
    bull = bear = None  # [extreme, extreme step, after, ao extreme]
    for s in range(se.n):
        if not valid[s]:
            continue
        prev = a[s - 1] if valid[s - 1] else None
        if a[s] >= 0 and prev is not None and prev < 0:
            bull = [H[s], s, None, a[s]]
        elif bull is not None:
            if H[s] >= bull[0]:
                bull[0], bull[1], bull[2] = H[s], s, None
            else:
                bull[2] = L[s] if bull[2] is None else min(bull[2], L[s])
            bull[3] = max(bull[3], a[s])
        if a[s] < 0 and prev is not None and prev >= 0:
            bear = [L[s], s, None, a[s]]
        elif bear is not None:
            if L[s] <= bear[0]:
                bear[0], bear[1], bear[2] = L[s], s, None
            else:
                bear[2] = H[s] if bear[2] is None else max(bear[2], H[s])
            bear[3] = min(bear[3], a[s])
        if s < WINDOW + 32 or prev is None:
            continue
        w = a[s - WINDOW + 1: s + 1]
        wmax, wmin = max(w), min(w)
        if a[s] < 0 <= prev and bull is not None and bull[2] is not None:
            top = bull[0]
            if wmax > 0 and bull[3] == wmax and wmax > -wmin and cur_h[s] == top:
                lows = L[s - WINDOW + 1: s + 1]
                base = min(lows)
                out.append((s, LONG, top, bull[1], base, s - WINDOW + 1 + lows.index(base), top - base, wmax, bull[2]))
        if a[s] >= 0 > prev and bear is not None and bear[2] is not None:
            bot = bear[0]
            if wmin < 0 and bear[3] == wmin and -wmin > wmax and cur_l[s] == bot:
                highs = H[s - WINDOW + 1: s + 1]
                base = max(highs)
                out.append((s, SHORT, bot, bear[1], base, s - WINDOW + 1 + highs.index(base), base - bot, wmin, bear[2]))
    return out, ao


class Market:
    def __init__(self, bars):
        self.bars = bars
        self.o, self.h, self.l, self.c = (np.asarray(x, dtype=np.int64) for x in (bars.o, bars.h, bars.l, bars.c))
        self.clock = {name: local_clock(bars.ts, SESSIONS[name].tz) for name in SESSION_NAMES}

    def in_session(self, name: str, j: int, day_key) -> bool:
        s = SESSIONS[name]
        mod, day = self.clock[name]
        return day[j] == day_key and s.open_minute <= mod[j] < s.flat_minute - 1

    def session_of(self, j: int):
        for name in SESSION_NAMES:
            s = SESSIONS[name]
            mod, day = self.clock[name]
            if s.open_minute <= mod[j] < s.flat_minute - 1:
                return name, day[j]
        return None, None

    def simulate(self, name, day_key, v, d, lim, stop, target, cancel_bar=None):
        """Limit placed at bar v's close. Returns None if never filled, else a result dict."""
        o, h, l, c, n = self.o, self.h, self.l, self.c, len(self.o)
        j, fill = v + 1, None
        while j < n:
            if not self.in_session(name, j, day_key):
                return None
            if (l[j] <= lim) if d == LONG else (h[j] >= lim):
                fill = min(o[j], lim) if d == LONG else max(o[j], lim)
                break
            if (h[j] >= target) if d == LONG else (l[j] <= target):
                return None
            if cancel_bar is not None and j >= cancel_bar:
                return None
            j += 1
        if fill is None:
            return None
        rw = 0.0 if (fill - stop) * d <= 0 else (fill - stop) / (target - stop)
        res = {"fill": int(fill), "rw": float(rw), "resolved": True, "top_first": False}
        if (l[j] <= stop) if d == LONG else (h[j] >= stop):
            exit_ = stop if (fill - stop) * d > 0 else fill
            return {**res, "pnl": int((exit_ - fill) * d)}
        k = j + 1
        while k < n:
            exit_ = None
            if (o[k] <= stop) if d == LONG else (o[k] >= stop):
                exit_ = o[k]
            elif (o[k] >= target) if d == LONG else (o[k] <= target):
                exit_, res["top_first"] = o[k], True
            elif (l[k] <= stop) if d == LONG else (h[k] >= stop):
                exit_ = stop
            elif (h[k] >= target) if d == LONG else (l[k] <= target):
                exit_, res["top_first"] = target, True
            elif not self.in_session(name, k, day_key):
                exit_, res["resolved"] = c[k], False
            if exit_ is not None:
                return {**res, "pnl": int((exit_ - fill) * d)}
            k += 1
        return {**res, "pnl": int((c[n - 1] - fill) * d), "resolved": False}


def h2_cancel_step(se, ao, setup, end_step):
    """First series step after the decision where the GET filters fail (1.40 rule or PTI proxy)."""
    s, d, top, top_s, _base, base_s, length, peak, after = setup
    w3_speed = length / max(1, top_s - base_s)
    low = after
    for t in range(s + 1, min(se.n, end_step)):
        low = min(low, int(se.l[t])) if d == LONG else max(low, int(se.h[t]))
        if (ao[t] < -0.40 * peak) if d == LONG else (ao[t] > -0.40 * peak):
            return t
        if abs(top - low) / max(1, t - top_s) > w3_speed:
            return t
    return None


def collect(hyp, degree, se, market, swings_cache, ao_cache):
    _cur_h, _cur_l, events, _ = swings_cache
    results = []

    def place(step, d, lim, stop, target, cancel_step=None):
        v = int(se.visible[step])
        if v >= len(market.o) - 1:
            return
        name, day_key = market.session_of(v)
        if name is None or (lim - stop) * d <= 0 or (target - lim) * d <= 0:
            return
        cancel_bar = None if cancel_step is None else int(se.visible[cancel_step])
        r = market.simulate(name, day_key, v, d, lim, stop, target, cancel_bar)
        results.append((name, day_key, r))

    if hyp in ("H1", "H2", "H4"):
        ao_list, ao = ao_cache
        for setup in ao_list:
            s, d, top, _top_s, _base, _base_s, length, _peak, after = setup
            if length < MIN_LEG:
                continue
            stop = top - d * rnd(0.618 * length)
            if ((after <= stop) if d == LONG else (after >= stop)):
                continue
            target = top + d
            if hyp in ("H1", "H2"):
                fib = top - d * rnd(0.382 * length)
                close = int(se.c[s])
                lim = min(fib, close) if d == LONG else max(fib, close)
                cancel = h2_cancel_step(se, ao, setup, s + 2000) if hyp == "H2" else None
                place(s, d, lim, stop, target, cancel)
            else:
                low = after
                for t in range(s + 1, min(se.n, s + 2000)):
                    low = min(low, int(se.l[t])) if d == LONG else max(low, int(se.h[t]))
                    if ((se.h[t] > top) if d == LONG else (se.l[t] < top)) or ((low <= stop) if d == LONG else (low >= stop)):
                        break
                    if (ao[t] >= 0) if d == LONG else (ao[t] < 0):
                        place(t, d, int(se.c[t]), low, target)
                        break
    else:
        for step, (last_t, piv) in events.items():
            if len(piv) < 4:
                continue
            d = LONG if last_t == sw.SL else SHORT
            if hyp == "H3":
                if len(piv) < 5:
                    continue
                p0, p1, p2, p3, p4 = piv[-5:]
                w1, w3 = (p1 - p0) * d, (p3 - p2) * d
                ok = w1 > 0 and (p2 - p0) * d > 0 and (p3 - p1) * d > 0 and w3 >= 1.618 * w1 and w3 >= MIN_LEG
                ok = ok and (p4 - p1) * d > 0
                if not ok:
                    continue
                fib = p3 - d * rnd(0.382 * w3)
                close = int(se.c[step])
                lim = min(fib, close) if d == LONG else max(fib, close)
                if (lim - p1) * d <= 0:
                    continue
                place(step, d, lim, p1, p3 + d)
            else:  # H5
                hp, p0, p1, p2 = piv[-4:]
                w1 = (p1 - p0) * d
                if not ((p1 - hp) * d > 0 and w1 >= MIN_LEG and (p2 - p0) * d > 0):
                    continue
                fib = p1 - d * rnd(0.618 * w1)
                close = int(se.c[step])
                lim = min(fib, close) if d == LONG else max(fib, close)
                if (lim - p0) * d <= 0:
                    continue
                place(step, d, lim, p0, p1 + d)
    return results


def summarize(results):
    filled = [(name, day, r) for name, day, r in results if r is not None]
    out = {"setups": len(results), "filled": len(filled)}
    if not filled:
        return {**out, "mean": None, "t": None}
    pnl = np.array([r["pnl"] for _, _, r in filled], dtype=float)
    m = pnl.mean()
    clusters = {}
    for (name, day, r), x in zip(filled, pnl):
        clusters.setdefault((name, day), []).append(x)
    resid = np.array([sum(v) - m * len(v) for v in clusters.values()])
    se = np.sqrt((resid ** 2).sum()) / len(pnl)
    out.update(mean=float(m), t=float(m / se) if se > 0 else None, days=len(clusters),
               top_first=float(np.mean([r["top_first"] for _, _, r in filled])),
               rw_expected=float(np.mean([r["rw"] for _, _, r in filled])),
               unresolved=float(np.mean([not r["resolved"] for _, _, r in filled])),
               by_session={name: round(float(np.mean([r["pnl"] for nm, _, r in filled if nm == name] or [np.nan])), 3)
                           for name in SESSION_NAMES})
    out["pass"] = bool(out["t"] is not None and m >= PASS_MEAN and out["t"] >= PASS_T)
    return out


def agreement(bars, degree, cur_h, cur_l):
    st = sw.timeframe_state(bars, degree)
    cd = sw.candles(bars, degree)
    at = st.at_bars(len(bars))
    ok = total = 0
    for k, v in enumerate(cd.visible.tolist()):
        if v >= len(bars) or at[v] < 0:
            continue
        total += 1
        ok += st.cur_h[at[v]] == cur_h[k] and st.cur_l[at[v]] == cur_l[k]
    return ok / max(1, total)


def main():
    bars = dev_bars()
    market = Market(bars)
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]
    meta = {"data_hash": data_hash(bars), "script_hash": script_hash, "dev_end_exclusive": DEV_END}
    rows = []
    for degree in DEGREES:
        se = Series(bars, degree)
        swings_cache = replay_swings(se)
        ao_cache = ao_setups(se, swings_cache[0], swings_cache[1])
        note = {"pivot_list_mismatch": swings_cache[3]}
        if degree == "1m":
            mine = set()
            for s, d, top, _, _, _, length, _, after in ao_cache[0]:
                stop = top - d * rnd(0.618 * length)
                if length >= MIN_LEG and (after - stop) * d > 0 and market.session_of(s)[0] is not None:
                    mine.add((s, d))
            ref = set()
            for name in SESSION_NAMES:
                g = setups(bars, name, WINDOW, 0.382, 0.618, 0.618, MIN_LEG)
                ref |= {(int(i), int(g["sig"][i])) for i in np.flatnonzero(g["sig"])}
            note["h1_equals_strategy_setups"] = ref == mine
            note["h1_setups"] = len(mine)
        else:
            note["swing_agreement_with_timeframe_state"] = round(agreement(bars, degree, swings_cache[0], swings_cache[1]), 5)
        print(f"[{degree}] {note}", flush=True)
        for hyp in HYPOTHESES:
            res = summarize(collect(hyp, degree, se, market, swings_cache, ao_cache))
            row = {"hypothesis": hyp, "degree": degree, **res, **note}
            rows.append(row)
            print(json.dumps(row), flush=True)
            with LEDGER.open("a") as f:
                f.write(json.dumps({"time_utc": datetime.now(UTC).isoformat(timespec="seconds"),
                                    "kind": "chance_check", "evaluations": 1, **meta, **row}) + "\n")
    print("\n| Hyp | Degree | Setups | Filled | Mean ticks | t (day-clustered) | Top-first | RW expected | Unresolved | Pass |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        fmt = lambda x, p=3: "-" if x is None else f"{x:.{p}f}"
        print(f"| {r['hypothesis']} | {r['degree']} | {r['setups']} | {r['filled']} | {fmt(r.get('mean'))} | "
              f"{fmt(r.get('t'), 2)} | {fmt(r.get('top_first'))} | {fmt(r.get('rw_expected'))} | "
              f"{fmt(r.get('unresolved'))} | {'yes' if r.get('pass') else 'no'} |")


if __name__ == "__main__":
    main()
