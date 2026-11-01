"""Supertrend + ATR trailing stop + Kalman trend + volatility filter, M15 signals traded on CL1! 1-minute bars.

Plan and Codex review: docs/research/supertrend_kalman_plan.md. Pine twin: strategies/supertrend_kalman.pine.

M15 mapping (non-repainting, Pine `request.security(.., "15", expr[1], lookahead = barmerge.lookahead_on)`):
M15 buckets are 1m bars grouped by UTC bar-open time floored to 15 minutes. A bucket's values are used from the
first 1m bar of the next bucket that exists; the strategy decides at that bar's close, so a market entry fills
at the following 1m open.

Signals on the completed bucket k (all need the Kalman slope on the trade side):
- trigger `st`: Supertrend direction flips to the trade side.
- trigger `trail`: the ATR trailing stop (UT Bot) flips to the trade side while Supertrend points that way.
- trigger `both`: Supertrend and ATR trail agree on bucket k and did not agree on bucket k - 1.
Stop: last confirmed M15 swing low (long) / high (short); no trade when it is not beyond the decision close.
Target: `rr` x risk in ticks from the actual fill (Pine `profit=`), risk = |decision close - stop|.
Volatility filter `vol`: `none`, `stop_atr:X` (risk <= X x ATR14 of the bucket, in ticks), `atr_ratio:X`
(ATR14 / ATR100 <= X), `rvi` (TradingView RVI > 50 for longs, < 50 for shorts). NaN fails.
Exit `exit`: `fixed` (bracket only), `trail` (stop moved to the ATR trail level at each new bucket when it is
tighter and on the right side of the close, never looser), `flip` (bracket plus close_all on an opposite
Supertrend flip).
Exit management (exit study, default off): breakeven / trailing stop / time exit at every 1m close while in a
position (tvtester/exits.py), T = the profit ticks; with exit=trail the tighter of the ATR level and these levels
wins. Order at a close: session end, ST flip, time exit, stop moves.
Hours (variant): `all` (no forced flat; only the owner roll exit) or a sessions.py session (entries inside
[open, flat - 1 min), close_all after it).
Filters (feature 2, default none): veto an entry at the decision bar; the M15 event expires as any untaken
event does (docs/strategies/supertrend_kalman/optimize/README.md has the feature definitions).
"""

import numpy as np

from tvtester import features as fx
from tvtester import ta
from tvtester.config import TICK
from tvtester.data import Bars
from tvtester.engine import LONG, SHORT, Context
from tvtester.exits import ExitRule, Manager
from tvtester.sessions import SESSIONS, local_clock
from tvtester.strategy import Strategy

BUCKET_MS = 15 * 60 * 1000
TRIGGERS = ("st", "trail", "both")
VOLS = ("none", "stop_atr", "atr_ratio", "rvi")
EXITS = ("fixed", "trail", "flip")
KALMAN_Q = 0.01
ER_LEN = 20
GLOBEX_OPEN_NY = 18 * 60  # CME Globex trading day opens 18:00 New York
FEATURES = ("risk_ticks", "risk_atr", "atr_ratio", "er", "hours_since_open", "rvi_side")


def _shared(bars: Bars, key, fn):
    k = ("supertrend_kalman", key)
    if k not in bars.cache:
        bars.cache[k] = fn()
    return bars.cache[k]


def m15(bars: Bars) -> dict:
    """M15 OHLC (ticks, as floats) and the 1m -> bucket map. `prev[i]` = index of the last completed bucket at
    1m bar i (-1 before the second bucket); `first[i]` = bar i opens a new bucket."""
    def build():
        if len(bars) and bars.t_ms[0] % BUCKET_MS:
            raise ValueError("bars must start on a 15-minute boundary (a partial first M15 bucket would be wrong)")
        key = bars.t_ms // BUCKET_MS
        first = np.ones(len(key), dtype=bool)
        first[1:] = key[1:] != key[:-1]
        starts = np.flatnonzero(first)
        cur = np.cumsum(first) - 1  # bucket index of each 1m bar
        o = bars.o[starts].astype(float)
        h = np.maximum.reduceat(bars.h, starts).astype(float)
        l = np.minimum.reduceat(bars.l, starts).astype(float)
        ends = np.concatenate([starts[1:], [len(key)]]) - 1
        c = bars.c[ends].astype(float)
        return {"o": o, "h": h, "l": l, "c": c, "prev": cur - 1, "first": first, "starts": starts}
    return _shared(bars, "m15", build)


def _last_value(x: np.ndarray) -> np.ndarray:
    """Most recent non-NaN value at or before each index (Pine `var` set when the value appears)."""
    idx = np.where(~np.isnan(x), np.arange(len(x)), -1)
    idx = np.maximum.accumulate(idx)
    out = np.full(len(x), np.nan)
    ok = idx >= 0
    out[ok] = x[idx[ok]]
    return out


def efficiency_ratio(c: np.ndarray, n: int) -> np.ndarray:
    """Kaufman ER at k: abs(c[k] - c[k-n]) / sum of abs(c[j] - c[j-1]), j = k-n+1..k. NaN before k = n or when
    the sum is 0 (Pine: division by zero gives na)."""
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    step = np.abs(np.diff(c))
    cs = np.concatenate([[0.0], np.cumsum(step)])  # cs[k] = sum of step[0..k-1] = moves up to bucket k
    den = cs[n:] - cs[:-n]
    num = np.abs(c[n:] - c[:-n])
    with np.errstate(invalid="ignore", divide="ignore"):
        out[n:] = np.where(den > 0, num / den, np.nan)
    return out


def indicators(bars: Bars, st_factor: float, trail_mult: float, swing: int, atr_len: int, kalman_q: float) -> dict:
    """Per-bucket M15 series, each cached on the bars by its own parameters."""
    m = m15(bars)
    h, l, c = m["h"], m["l"], m["c"]
    st_dir = _shared(bars, ("st", st_factor, atr_len), lambda: ta.supertrend(h, l, c, st_factor, atr_len)[1])
    tr_stop = _shared(bars, ("trail", trail_mult, atr_len),
                      lambda: ta.atr_trailing_stop(c, trail_mult * ta.atr(h, l, c, atr_len)))
    k_slope = _shared(bars, ("kalman", kalman_q), lambda: ta.kalman_trend(c * TICK, kalman_q)[1])
    sw_lo = _shared(bars, ("swl", swing), lambda: _last_value(ta.buffer_pivots(l, swing, False)))
    sw_hi = _shared(bars, ("swh", swing), lambda: _last_value(ta.buffer_pivots(h, swing, True)))
    atr14 = _shared(bars, ("atr", 14), lambda: ta.atr(h, l, c, 14))
    atr100 = _shared(bars, ("atr", 100), lambda: ta.atr(h, l, c, 100))
    rvi = _shared(bars, "rvi", lambda: ta.rvi(c))
    er = _shared(bars, ("er", ER_LEN), lambda: efficiency_ratio(c, ER_LEN))
    return {"c": c, "st_dir": st_dir, "tr_stop": tr_stop, "k_slope": k_slope, "sw_lo": sw_lo,
            "sw_hi": sw_hi, "atr14": atr14, "atr100": atr100, "rvi": rvi, "er": er}


def bucket_signals(ind: dict, trigger: str) -> np.ndarray:
    """+1 / -1 / 0 per completed bucket."""
    st_up = ind["st_dir"] == -1  # Pine: direction -1 = up trend, +1 = down trend
    st_dn = ind["st_dir"] == 1
    c, t = ind["c"], ind["tr_stop"]
    c1, t1 = ta.shift(c, 1), ta.shift(t, 1)
    k_up, k_dn = ind["k_slope"] > 0, ind["k_slope"] < 0  # zero slope admits neither side

    def prev(x):
        return np.concatenate([[False], x[:-1]])

    if trigger == "st":
        lg, sh = st_up & prev(st_dn), st_dn & prev(st_up)
    elif trigger == "trail":  # UT Bot buy / sell events (NaN compares false)
        lg = (c > t) & (c1 <= t1) & st_up
        sh = (c < t) & (c1 >= t1) & st_dn
    else:  # alignment of Supertrend and the side of the close vs the UT stop, entered on its first bucket
        a_up, a_dn = st_up & (c > t), st_dn & (c < t)
        lg, sh = a_up & ~prev(a_up), a_dn & ~prev(a_dn)
    return np.where(lg & k_up, LONG, np.where(sh & k_dn, SHORT, 0)).astype(np.int8)


class SupertrendKalman(Strategy):
    name = "supertrend_kalman"
    report_tz = "America/New_York"  # weekday buckets on the New York clock (CME hours)

    def __init__(self, hours: str = "all", trigger: str = "st", vol: str = "none", exit: str = "fixed",
                 rr: float = 2.0, swing: int = 3, st_factor: float = 3.0, trail_mult: float = 2.0, atr_len: int = 10,
                 kalman_q: float = KALMAN_Q, filters=(), **exit_rule):
        kind, _, x = vol.partition(":")
        self.rule = ExitRule(**exit_rule)  # exit management (tvtester/exits.py), default off
        if (trigger not in TRIGGERS or kind not in VOLS or exit not in EXITS
                or (kind in ("stop_atr", "atr_ratio")) != bool(x)):
            raise ValueError(f"trigger in {TRIGGERS}, vol in {VOLS}, exit in {EXITS}")
        if hours != "all" and hours not in SESSIONS:
            raise ValueError("hours must be 'all' or a session name")
        self.vol_kind, self.vol_x = kind, float(x) if x else 0.0
        super().__init__(filters, hours=hours, trigger=trigger, vol=vol, exit=exit, rr=rr, swing=swing,
                         st_factor=st_factor, trail_mult=trail_mult, atr_len=atr_len, kalman_q=kalman_q,
                         **self.rule.params())
        self.exits = Manager(self.rule)

    def prepare(self, bars: Bars) -> np.ndarray:
        p = self.params
        self.bars = bars
        self.exits.prepare(bars)  # exit-management state starts fresh with every run
        m = m15(bars)
        self.ind = indicators(bars, p["st_factor"], p["trail_mult"], p["swing"], p["atr_len"], p["kalman_q"])
        self.bsig = bucket_signals(self.ind, p["trigger"])
        self.prev, self.first = m["prev"], m["first"]
        if p["hours"] == "all":
            self.in_hours = np.ones(len(bars), dtype=bool)
        else:
            s = SESSIONS[p["hours"]]
            mod, _ = _shared(bars, ("clock", s.tz), lambda: local_clock(bars.ts, s.tz))
            self.in_hours = (mod >= s.open_minute) & (mod < s.flat_minute - 1)
        k = self.prev
        ok = self.first & (k >= 0)
        sig = np.zeros(len(bars), dtype=np.int8)
        sig[ok] = self.bsig[k[ok]]
        self.sig = sig
        self.allow = np.ones(len(bars), dtype=bool)
        if self.filters:
            self.allow = fx.gate(self.filters, self.features(bars), len(bars))
        return (sig != 0) & self.in_hours & self.allow

    def features(self, bars: Bars) -> dict[str, np.ndarray]:
        """Feature values at candidate decision bars (signal, in hours, stop beyond the close, base `vol` filter
        passed); NaN elsewhere. Every value uses bucket k = the last completed M15 bucket and bar i itself."""
        ind, n = self.ind, len(bars)
        out = {f: np.full(n, np.nan) for f in FEATURES}
        cand = np.flatnonzero((self.sig != 0) & self.in_hours)
        keep = []
        for i in cand.tolist():
            d, k, c = int(self.sig[i]), int(self.prev[i]), int(bars.c[i])
            risk = self._risk(d, k, c)
            if risk is not None and self._vol_ok(d, k, risk):
                keep.append((i, d, k, risk))
        if not keep:
            return out
        idx = np.array([x[0] for x in keep])
        d = np.array([x[1] for x in keep])
        k = np.array([x[2] for x in keep])
        risk = np.array([x[3] for x in keep], dtype=float)
        a14, a100 = ind["atr14"][k], ind["atr100"][k]
        with np.errstate(invalid="ignore", divide="ignore"):
            out["risk_ticks"][idx] = risk
            out["risk_atr"][idx] = np.where(a14 > 0, risk / a14, np.nan)
            out["atr_ratio"][idx] = np.where(a100 > 0, a14 / a100, np.nan)
        out["er"][idx] = ind["er"][k]
        mod, _ = _shared(bars, ("clock", "America/New_York"), lambda: local_clock(bars.ts, "America/New_York"))
        out["hours_since_open"][idx] = ((mod[idx] - GLOBEX_OPEN_NY) % 1440) // 60
        r = ind["rvi"][k]
        out["rvi_side"][idx] = np.where(d == LONG, r, 100 - r)
        return out

    def _risk(self, d: int, k: int, c: int):
        """Signal risk in ticks, or None when there is no swing level beyond the decision close."""
        lvl = self.ind["sw_lo"][k] if d == LONG else self.ind["sw_hi"][k]
        if lvl != lvl:
            return None
        stop = int(lvl)
        if (d == LONG and stop >= c) or (d == SHORT and stop <= c):
            return None
        return abs(c - stop)

    def _vol_ok(self, d: int, k: int, risk: int) -> bool:
        ind = self.ind
        if self.vol_kind == "stop_atr":
            return risk <= self.vol_x * ind["atr14"][k]  # NaN ATR fails
        if self.vol_kind == "atr_ratio":
            return ind["atr14"][k] <= self.vol_x * ind["atr100"][k]
        if self.vol_kind == "rvi":
            v = ind["rvi"][k]
            return v > 50 if d == LONG else v < 50
        return True

    def on_bar(self, ctx: Context, i: int) -> None:
        p, ind = self.params, self.ind
        k = int(self.prev[i])
        c = int(self.bars.c[i])
        if ctx.position_size != 0:
            if not self.in_hours[i] and p["hours"] != "all":
                ctx.cancel("Exit")  # as the ST flip: only the market close works at the next open
                ctx.close_all("Session end")
                return
            d = LONG if ctx.position_size > 0 else SHORT
            stop = None  # the amended stop, if any
            if self.first[i] and k >= 0:
                if p["exit"] == "flip" and ind["st_dir"][k] == (1 if d == LONG else -1):
                    ctx.cancel("Exit")  # only the market close works at the next open (no bracket race)
                    ctx.close_all("ST flip")
                    return
                if p["exit"] == "trail":
                    t = ind["tr_stop"][k]
                    if t == t:
                        # 1e-6 guard: the Pine twin divides dollars by mintick, so a whole tick can land just below
                        t = int(np.floor(t + 1e-6)) if d == LONG else int(np.ceil(t - 1e-6))
                        if (d == LONG and self.stop < t < c) or (d == SHORT and c < t < self.stop):
                            stop = t
            if self.rule.active:  # breakeven / trailing stop / time exit at every 1m close (tvtester/exits.py)
                eb = ctx.position_entry_bar
                if self.exits.time_up(eb, i):
                    ctx.cancel("Exit")  # as the ST flip: only the market close works at the next open
                    ctx.close_all("Time exit")
                    return
                s = self.exits.new_stop(i, d, eb, ctx.position_avg_price, self.profit,
                                        self.stop if stop is None else stop)
                if s is not None:
                    stop = s
            if stop is not None:
                self.stop = stop
                self._bracket(ctx, stop)
            return
        d = int(self.sig[i])
        if d == 0 or not self.in_hours[i] or not self.allow[i]:
            return  # a vetoed event expires here too: on_bar also runs on the bar a position closes
        risk = self._risk(d, k, c)
        if risk is None or not self._vol_ok(d, k, risk):
            return
        stop = c - risk if d == LONG else c + risk
        self.eid = "Long" if d == LONG else "Short"
        self.stop, self.profit = stop, int(round(p["rr"] * risk))
        ctx.entry(self.eid, d)
        self._bracket(ctx, stop)

    def _bracket(self, ctx: Context, stop: int) -> None:
        """The one `Exit` bracket: stop plus the profit leg (none with keep_target=False)."""
        ctx.exit("Exit", self.eid, stop=stop, profit=self.profit if self.rule.keep_target else None)


# --- test definition (python -m tvtester.cli test supertrend_kalman) -------------------------------------
STRATEGY = SupertrendKalman
TITLE = "Supertrend + ATR trail + Kalman trend, M15 signals, CL1! 1m"
GRID = {
    "trigger": list(TRIGGERS),
    "vol": ["none", "stop_atr:1.5", "stop_atr:3", "atr_ratio:1.0", "atr_ratio:1.3", "rvi"],
    "exit": list(EXITS),
    "rr": [2, 3],
    "swing": [3, 5],
    "trail_mult": [1, 2],
    "st_factor": [2, 3],
    "kalman_q": [0.01, 0.0001],  # 0.01 agrees with ~97% of Supertrend flips (2023), 0.0001 with ~40%
}
VARIANTS = {"all": {"hours": "all"}, "asia": {"hours": "asia"}, "london": {"hours": "london"}, "ny": {"hours": "ny"}}

# --- optimize definition (feature 2: python -m tvtester.cli features / search / replay) -------------------
# Baselines: the feature-1 top combination of each variant (picked on 2010-06 .. 2026-10, see the ledger).
BASELINES = {
    "all": {"trigger": "both", "vol": "atr_ratio:1.3", "exit": "fixed", "rr": 3, "swing": 3, "trail_mult": 1,
            "st_factor": 3, "kalman_q": 0.0001},
    "asia": {"trigger": "trail", "vol": "none", "exit": "trail", "rr": 3, "swing": 3, "trail_mult": 2,
             "st_factor": 3, "kalman_q": 0.01},
    "london": {"trigger": "both", "vol": "stop_atr:3", "exit": "trail", "rr": 2, "swing": 5, "trail_mult": 2,
               "st_factor": 3, "kalman_q": 0.0001},
    "ny": {"trigger": "both", "vol": "rvi", "exit": "flip", "rr": 3, "swing": 5, "trail_mult": 1, "st_factor": 2,
           "kalman_q": 0.0001},
}
FILTER_SPACE = {  # feature: (lowest threshold, highest threshold, step), declared before any feature-2 run
    "risk_ticks": (10, 200, 5),
    "risk_atr": (0.5, 5.0, 0.25),
    "atr_ratio": (0.6, 2.0, 0.1),
    "er": (0.05, 0.8, 0.05),
    "hours_since_open": (0, 23, 1),
    "rvi_side": (30, 80, 5),
}
SPACES = {
    "filters": {"params": {}, "filters": FILTER_SPACE},  # baseline parameters frozen, filters searched
    "full": {"params": GRID, "filters": FILTER_SPACE},  # base parameters and filters together
}
LINEAGE = ("baselines are the feature-1 top combinations, picked from 1,728 grid combinations per variant "
           "(6,912 in all) on 2010-06-06 .. 2026-10-27 (includes the reserved interval)")
ABOUT = """
Owner idea: Supertrend plus an ATR trailing stop on M15, a Kalman filter for the trend, a volatility filter so it
does not trade with a wide stop, stop at the swing high / low, target 1:2 to 1:3. The owner left every design fork
open, so each fork is a grid parameter (`trigger`, `vol`, `exit`) or a variant (trading hours). Plan and Codex
review: [`docs/research/supertrend_kalman_plan.md`](../../research/supertrend_kalman_plan.md).

**M15 on a 1-minute chart.** M15 bars are the 1m bars grouped by UTC time floored to 15 minutes (CL's 18:00 New
York session open is a 15-minute boundary). A bucket's values are used only after it is complete: from the first
1m bar of the next bucket, which decides at its close, so a market entry fills at the next 1m open (normally
hh:16 for the hh:00-hh:15 bucket). Pine twin: `request.security(.., "15", expr[1], lookahead = barmerge.lookahead_on)`.

**Indicators (M15):** Supertrend(`st_factor`, ATR 10, Pine `ta.supertrend`); UT Bot ATR trailing stop
(ATR 10 x `trail_mult`, close source); 2-state constant-velocity Kalman filter on close (`kalman_q` = 0.01 or
0.0001, R = 1, P0 = 100 I, Joseph update), trend = sign of its slope. q = 0.01 alone agreed with about 97% of
Supertrend flips on 2023 bars (hardly a filter), so the slower 0.0001 (about 40%) was added; that choice used
signal counts only, no profit numbers; ATR14, ATR100, TradingView RVI(10, 14); swing highs /
lows with `swing` bars each side (strictly above / below), last confirmed value.

**Entry (`trigger`), only when flat, Kalman slope on the trade side:**
- `st`: Supertrend flips to the trade side.
- `trail`: UT Bot buy / sell (close crosses the trailing stop) while Supertrend points the trade side.
- `both`: Supertrend and the close-vs-UT-stop side agree on this bucket and did not on the previous one.

**Stop and target:** stop = last confirmed M15 swing low (long) / high (short); no trade when it is not beyond the
decision close. Target = `rr` x signal risk (risk = decision close to stop) in ticks from the actual fill. The
fill is one minute after the decision, so the realised initial RR differs slightly from `rr`.

**Volatility filter (`vol`):** `none`; `stop_atr:X` skips when the risk is wider than X x ATR14 (M15), the direct
"no wide stop" rule; `atr_ratio:X` skips when ATR14 / ATR100 > X (volatile regime); `rvi` takes longs only when
RVI > 50 and shorts only when RVI < 50 (RVI is directional volatility, not a stop-width measure). CBOE OVX (crude
oil VIX) is not tested: it is not in the repo's data.

**Exit (`exit`):** `fixed` = swing stop + target; `trail` = the stop also moves to the UT trailing stop at each new
M15 bucket when that is tighter and still on the right side of the close (never looser, target unchanged);
`flip` = fixed bracket, plus a market close when Supertrend flips against the position (the bracket is cancelled
first, so only the close works at the next open).

**Hours (variant):** `all` = any time, no forced flat (holds through the daily halt and weekends; only the owner
roll exit); `asia` / `london` / `ny` = decision bar inside the sessions.py session [open, flat - 1 min), open
positions closed at the next open after it, as fair_price_reversal (the bracket is cancelled first, as for `flip`).

A runnable Pine v6 twin is in [`strategies/supertrend_kalman.pine`](../../../strategies/supertrend_kalman.pine).
The twin does not have the owner roll exit, so trades open at a contract roll differ from TradingView: mostly in `all`,
but a contract's last bar can fall inside a session too (NY: 10 roll exits 2010-2023).
"""

CONCLUSION = """
**No tradable edge on CL.** The top combination of every variant loses money at 2 ticks of slippage; `all`,
London and New York stay above zero at 1 tick, Asia does not. These are the best of 1,728 combinations per variant (6,912 in
all) on the same 16 years they are reported on (in-sample), so even the 0-tick numbers are an upper bound.

- **`all` (24 h):** +128,887 / +42,087 / -37,225 USD at 0 / 1 / 2 ticks over 4,471 trades (+28.83 USD per
  trade before slippage, while 1 tick costs 20 USD per trade). Max drawdown 51,169 USD = 102% of the 50,000 USD
  account: it would have been wiped out on the way. 1,264 of 1,728 combinations lose money at 0 ticks (grid
  median -20,476 USD). The ten best trades earn 101,700 USD, 79% of the total.
- **`ny`:** +84,714 / +22,574 / -39,556 USD, 3,188 trades; 2022 alone is 37,586 USD. The only variant where the
  grid median is above zero at 0 ticks (+959 USD), still far below the cost of 1 tick.
- **`asia`, `london`:** small at 0 ticks (+18,112, +16,242 USD) and gone by 1 to 2 ticks.
- **The owner's filters:** the "no wide stop" rule (`stop_atr`) only tops London; the Kalman filter helps mainly
  in its slow setting (q = 0.0001, in 3 of 4 tops); `trail` exits top only Asia and London.

**Independent check:** Codex rebuilt the `all` top combination with its own code from the raw parquet files:
4,471 trades, +128,886.58 USD at 0 ticks; 4,461 trades, +42,086.78 USD at 1 tick. Every trade matched
(docs/REVIEWS.md, R8). Not checked on TradingView itself yet: run the Pine twin on NYMEX:CL1! 1m to confirm.
"""


def notes(tf, params) -> list[str]:
    out = []
    if not tf.empty:
        out.append(f"Roll exits (owner rule, not in TradingView): {(tf['exit_reason'] == 'roll').sum()}.")
        out.append(f"Median bars in trade: {int(tf['bars'].median())}.")
    return out
