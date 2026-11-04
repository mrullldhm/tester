"""Fair Price Reversal (LuxAlgo "9:29 ET Fair Price Reversal", MPL-2.0) as a CL1! strategy, one per session.

Signals: line-for-line port of the 1-minute path of strategies/reference/fair_price_reversal_luxalgo.pine,
with the 9:29 / 9:30 ET anchor moved to each session's open (anchor = the candle before the open).
Indicators run over every bar (ATR, pivot buffer, last swing high / low), as Pine does.

Trade rules (ours: the indicator has none; the Pine twin is strategies/fair_price_reversal.pine):
- Entry: limit at the signal close, active from the next bar, only when flat.
- Stop: the excursion extreme frozen at the signal bar (lowest low for longs / highest high for shorts from
  the bar that started the excursion to the signal bar).
- Target: "near" / "far" body edge of the anchor candle (limit price), or "rr1" / "rr2": 1R / 2R in ticks
  from the actual fill, R = |signal close - stop| (Pine `profit=` in ticks).
- Flat: close_all at the close of the first bar outside [open, flat - 1 min) local time, so the exit fills
  at the next open (usually the flat minute). Entries are only placed while inside that range.
- Filters (feature 2, default none): veto an entry at the signal bar; the vetoed signal still uses up that day's
  long / short signal (docs/OPTIMIZE.md has the feature contracts).
- Exit management (exit study, default off): breakeven / trailing stop / time exit at each bar close while in a
  position (tvtester/exits.py). T = the profit ticks (rr) or |limit - fill| (near / far). A time exit cancels the
  bracket and closes at the next open; the session-end close keeps the bracket working (unchanged).
"""

import numpy as np

from tvtester import features as fx
from tvtester import ta
from tvtester.data import Bars
from tvtester.engine import LONG, SHORT, Context
from tvtester.exits import ExitRule, Manager
from tvtester.entries import PendingEntry
from tvtester.sessions import SESSIONS, local_clock
from tvtester.strategy import Strategy

MAX_PIVOT_BUFFER = 21
TARGETS = ("near", "far", "rr1", "rr2")
RANGE_BARS = 1380  # about one 23-hour CL trading day of 1-minute bars
RANGE_DAYS = 20
FEATURES = ("minutes_from_open", "anchor_body_atr", "risk_ticks", "risk_atr", "range_ratio")

def _shared(bars: Bars, key, fn):
    """Arrays shared by every combination on the same bars, cached on the Bars object itself."""
    k = ("fair_price_reversal", key)
    if k not in bars.cache:
        bars.cache[k] = fn()
    return bars.cache[k]


def _last_before(values: np.ndarray) -> np.ndarray:
    """Most recent non-NaN value strictly before each bar (Pine `var` updated after use)."""
    idx = np.where(~np.isnan(values), np.arange(len(values)), -1)
    idx = np.maximum.accumulate(idx)
    prev = np.concatenate([[-1], idx[:-1]])
    out = np.full(len(values), np.nan)
    ok = prev >= 0
    out[ok] = values[prev[ok]]
    return out


def signals(bars: Bars, session: str, window: int, atr_mult: float, swing: int, atr_len: int = 14) -> dict:
    """Port of the indicator's 1-minute path. Returns per-bar arrays: sig (+1 / -1 / 0), stop, body edges."""
    s = SESSIONS[session]
    mod, day = _shared(bars, ("clock", s.tz), lambda: local_clock(bars.ts, s.tz))
    move_atr = _shared(bars, ("atr1", atr_len), lambda: ta.shift(ta.atr(bars.h, bars.l, bars.c, atr_len), 1))
    ph = _shared(bars, ("ph", swing), lambda: ta.buffer_pivots(bars.h, swing, True))
    pl = _shared(bars, ("pl", swing), lambda: ta.buffer_pivots(bars.l, swing, False))
    sh_before = _shared(bars, ("shb", swing), lambda: _last_before(ph))
    sl_before = _shared(bars, ("slb", swing), lambda: _last_before(pl))

    start, end = s.open_minute, s.open_minute + window
    in_win = (mod >= start) & (mod < end)
    after = mod >= end
    first_after = after & np.concatenate([[False], in_win[:-1]])
    todo = np.flatnonzero((mod == s.anchor_minute) | in_win | first_after)

    n = len(bars)
    sig = np.zeros(n, dtype=np.int8)
    stop = np.zeros(n, dtype=np.int64)
    body_up = np.zeros(n, dtype=np.int64)
    body_lo = np.zeros(n, dtype=np.int64)
    o, h, l, c = bars.o, bars.h, bars.l, bars.c

    last_day = None
    bu = bl = None
    up_seen = lo_seen = long_sent = short_sent = False
    up_t = lo_t = None  # bar index of the excursion (bar time order == index order)
    long_ready = short_ready = False
    long_trig = short_trig = None
    direction = 0
    for i in todo.tolist():
        pivot_t = i - swing  # buffer center; the buffer is always full after the first 21 bars
        piv_h, piv_l = ph[i], pl[i]
        if mod[i] == s.anchor_minute and (last_day is None or day[i] != last_day):
            bu, bl = max(o[i], c[i]), min(o[i], c[i])
            up_seen = lo_seen = long_sent = short_sent = False
            direction = 0
            up_t = lo_t = None
            long_ready = short_ready = False
            long_trig = short_trig = None
            last_day = day[i]
        win = in_win[i]
        atr_i = move_atr[i]
        if win and atr_i == atr_i and atr_i > 0 and bu is not None:
            md = atr_i * atr_mult
            if up_seen and direction != -1 and not short_sent and c[i] < bu + md:
                up_seen = False
            if lo_seen and direction != 1 and not long_sent and c[i] > bl - md:
                lo_seen = False
            up_hit = not up_seen and not short_sent and h[i] >= bu + md
            lo_hit = not lo_seen and not long_sent and l[i] <= bl - md
            if up_hit and lo_hit:
                up_seen = lo_seen = True
                up_t = lo_t = i
                direction = 0
                long_ready = short_ready = False
                long_trig = short_trig = None
            elif up_hit:
                up_seen, up_t, direction = True, i, -1
                long_ready = short_ready = False
                long_trig = short_trig = None
            elif lo_hit:
                lo_seen, lo_t, direction = True, i, 1
                long_ready = short_ready = False
                long_trig = short_trig = None
        if piv_h == piv_h:
            last_sh = sh_before[i]
            if (win and direction == 1 and lo_seen and not long_sent and last_sh == last_sh
                    and lo_t is not None and pivot_t > lo_t and piv_h < last_sh):
                long_ready, long_trig = True, piv_h
        if piv_l == piv_l:
            last_sl = sl_before[i]
            if (win and direction == -1 and up_seen and not short_sent and last_sl == last_sl
                    and up_t is not None and pivot_t > up_t and piv_l > last_sl):
                short_ready, short_trig = True, piv_l
        if win and direction == 1 and long_ready and not long_sent and c[i] > long_trig and c[i] < bl:
            long_sent, long_ready, direction = True, False, 0
            sig[i], stop[i] = LONG, l[lo_t: i + 1].min()
            body_up[i], body_lo[i] = bu, bl
        if win and direction == -1 and short_ready and not short_sent and c[i] < short_trig and c[i] > bu:
            short_sent, short_ready, direction = True, False, 0
            sig[i], stop[i] = SHORT, h[up_t: i + 1].max()
            body_up[i], body_lo[i] = bu, bl
        if after[i]:
            long_ready = short_ready = False
    return {"sig": sig, "stop": stop, "body_up": body_up, "body_lo": body_lo}


def anchor_bars(mod: np.ndarray, day: np.ndarray, anchor_minute: int) -> np.ndarray:
    """Bars that reset the setup: the first anchor-minute bar of each local day (as in `signals`)."""
    idx = np.flatnonzero(mod == anchor_minute)
    if len(idx) == 0:
        return idx
    keep = np.concatenate([[True], day[idx[1:]] != day[idx[:-1]]])
    return idx[keep]


def feature_values(bars: Bars, session: str, sg: dict, atr_len: int = 14) -> dict[str, np.ndarray]:
    """Per-bar feature values (meaningful at signal bars). Each value uses the signal bar and earlier bars only."""
    s = SESSIONS[session]
    n = len(bars)
    mod, day = _shared(bars, ("clock", s.tz), lambda: local_clock(bars.ts, s.tz))
    move_atr = _shared(bars, ("atr1", atr_len), lambda: ta.shift(ta.atr(bars.h, bars.l, bars.c, atr_len), 1))

    def anchored():
        a = anchor_bars(mod, day, s.anchor_minute)
        body = np.abs(bars.c[a] - bars.o[a]).astype(float)
        atr_a = move_atr[a]
        with np.errstate(invalid="ignore", divide="ignore"):
            body_atr = np.where(atr_a > 0, body / atr_a, np.nan)
        rr = fx.ratio_to_trailing_mean(fx.prior_range(bars.h, bars.l, a, RANGE_BARS), RANGE_DAYS)
        return fx.carry_forward(a, body_atr, n), fx.carry_forward(a, rr, n)

    body_atr, range_ratio = _shared(bars, ("anchored", session, atr_len), anchored)
    risk = np.full(n, np.nan)
    at = np.flatnonzero(sg["sig"])
    risk[at] = np.abs(bars.c[at] - sg["stop"][at])
    with np.errstate(invalid="ignore", divide="ignore"):
        risk_atr = np.where(move_atr > 0, risk / move_atr, np.nan)
    return {"minutes_from_open": (mod - s.open_minute).astype(float), "anchor_body_atr": body_atr,
            "risk_ticks": risk, "risk_atr": risk_atr, "range_ratio": range_ratio}


class FairPriceReversal(Strategy):
    name = "fair_price_reversal"

    def __init__(self, session: str = "ny", window: int = 60, atr_mult: float = 1.0, swing: int = 2,
                 target: str = "near", atr_len: int = 14, filters=(), **exit_rule):
        if target not in TARGETS:
            raise ValueError(f"target must be one of {TARGETS}")
        self.rule = ExitRule(**exit_rule)  # exit management (tvtester/exits.py), default off
        super().__init__(filters, session=session, window=window, atr_mult=atr_mult, swing=swing, target=target,
                         atr_len=atr_len, **self.rule.params())
        self.s = SESSIONS[session]
        self.report_tz = self.s.tz
        self.exits = Manager(self.rule)
        self.pending = PendingEntry()
        self.t_bar = -1

    def prepare(self, bars: Bars) -> np.ndarray:
        p = self.params
        self.bars = bars
        self.exits.prepare(bars)  # exit-management state starts fresh with every run
        self.pending = PendingEntry()
        self.t_bar = -1
        self.sig = signals(bars, p["session"], p["window"], p["atr_mult"], p["swing"], p["atr_len"])
        self.mod, _ = _shared(bars, ("clock", self.s.tz), lambda: local_clock(bars.ts, self.s.tz))
        self.allow = np.ones(len(bars), dtype=bool)
        if self.filters:
            self.allow = fx.gate(self.filters, self.features(bars), len(bars))
        return (self.sig["sig"] != 0) & self.allow

    def features(self, bars: Bars) -> dict[str, np.ndarray]:
        return feature_values(bars, self.params["session"], self.sig, self.params["atr_len"])

    def _in_session(self, i: int) -> bool:
        return self.s.open_minute <= self.mod[i] < self.s.flat_minute - 1

    def on_bar(self, ctx: Context, i: int) -> None:
        waiting = self.pending.waiting(ctx, self.bars, i, self._in_session(i))
        if ctx.position_size != 0 and not self._in_session(i):
            ctx.close_all("Session end")
            return
        if ctx.position_size != 0:
            if self.rule.active:
                self._manage(ctx, i)
            return
        if waiting or self.bars.last_of_contract[i]:
            return
        d = int(self.sig["sig"][i])
        if d == 0 or not self.allow[i] or not self._in_session(i):
            return  # a vetoed signal is dropped here too: on_bar also runs on bars where a position closes
        sg, target, c = self.sig, self.params["target"], int(self.bars.c[i])
        stop = int(sg["stop"][i])
        eid = "Long" if d == LONG else "Short"
        ctx.entry(eid, d, limit=c)
        self.eid, self.stop, self.limit, self.profit = eid, stop, None, None
        if target in ("near", "far"):
            near = sg["body_lo"][i] if d == LONG else sg["body_up"][i]
            far = sg["body_up"][i] if d == LONG else sg["body_lo"][i]
            self.limit = int(near if target == "near" else far)
        else:
            self.profit = abs(c - stop) * (1 if target == "rr1" else 2)
        planned_tp = self.limit if self.limit is not None else c + d * self.profit
        self.pending.place(eid, d, planned_tp)
        self._bracket(ctx, stop)

    def _bracket(self, ctx: Context, stop: int) -> None:
        """The one `Exit` bracket: stop plus the target leg (none with keep_target=False)."""
        keep = self.rule.keep_target
        ctx.exit("Exit", self.eid, stop=stop, limit=self.limit if keep else None,
                 profit=self.profit if keep else None)

    def _manage(self, ctx: Context, i: int) -> None:
        """Breakeven / trailing stop / time exit at the bar close (tvtester/exits.py)."""
        d = LONG if ctx.position_size > 0 else SHORT
        eb, entry = ctx.position_entry_bar, ctx.position_avg_price
        if eb != self.t_bar:  # T frozen at the entry fill
            self.t_bar = eb
            self.t_ticks = self.profit if self.profit is not None else abs(self.limit - entry)
        if self.exits.time_up(eb, i):
            ctx.cancel("Exit")  # only the market close works at the next open
            ctx.close_all("Time exit")
            return
        s = self.exits.new_stop(i, d, eb, entry, self.t_ticks, self.stop)
        if s is not None:
            self.stop = s
            self._bracket(ctx, s)


# --- test definition (python -m tvtester.cli test fair_price_reversal) -----------------------------------
STRATEGY = FairPriceReversal
TITLE = "Fair Price Reversal (LuxAlgo 9:29 ET), CL1! sessions"
GRID = {"window": [30, 60, 90, 120], "atr_mult": [0.5, 1.0, 1.5, 2.0], "swing": [1, 2, 3], "target": list(TARGETS)}
VARIANTS = {"asia": {"session": "asia"}, "london": {"session": "london"}, "ny": {"session": "ny"}}

# --- optimize definition (feature 2: python -m tvtester.cli features / search / replay) -------------------
# Baselines: the feature-1 top combination of each variant (picked on 2010-06 .. 2026-10, see the ledger).
BASELINES = {
    "asia": {"window": 30, "atr_mult": 2.0, "swing": 3, "target": "rr1"},
    "london": {"window": 120, "atr_mult": 2.0, "swing": 3, "target": "rr2"},
    "ny": {"window": 120, "atr_mult": 0.5, "swing": 3, "target": "rr2"},
}
FILTER_SPACE = {  # feature: (lowest threshold, highest threshold, step)
    "minutes_from_open": (5, 115, 5),
    "anchor_body_atr": (0.1, 2.0, 0.1),
    "risk_ticks": (6, 60, 2),
    "risk_atr": (1.0, 6.0, 0.25),
    "range_ratio": (0.5, 2.0, 0.1),
}
SPACES = {
    "filters": {"params": {}, "filters": FILTER_SPACE},  # baseline parameters frozen, filters searched
    "full": {"params": GRID, "filters": FILTER_SPACE},  # base parameters and filters together
}
LINEAGE = ("baselines are the feature-1 top combinations, picked from 192 grid combinations per variant on "
           "2010-06-06 .. 2026-10-27 (includes the reserved interval)")
ABOUT = """
Source: LuxAlgo, [9:29 ET Fair Price Reversal](https://www.luxalgo.com/library/indicator/9-29-et-fair-price-reversal/)
(Pine v6, MPL-2.0). The original reads NQ around the 9:30 ET stock open. Here it runs on CL1! with the anchor
moved to the candle before each CL session open:

| Variant | Session open | Anchor candle | Malaysia time (UTC+8) | Flat at |
|---|---|---|---|---|
| asia | 09:00 Asia/Shanghai (same clock as Singapore / Kuala Lumpur, no DST) | 08:59 | 09:00 all year | 15:00 Asia/Shanghai |
| london | 08:00 Europe/London | 07:59 | 15:00 (UK summer) / 16:00 (UK winter) | 13:00 London |
| ny | 09:00 America/New_York (NYMEX crude open) | 08:59 | 21:00 (US summer) / 22:00 (US winter) | 14:30 New York |

**Signal (unchanged from the indicator):** the anchor candle's body (open/close) is the fair price. Inside the
setup window that starts at the session open, price must move at least `atr_mult` x ATR(14) of the previous
bar beyond the body. A long needs a lower swing high to form after a move down, then a close above that swing
high while still below the body ("MSS LONG"); a short is the mirror ("MSS SHORT"). At most one long and one
short signal per session day. Swing highs / lows use `swing` bars on each side.

**Trade rules (ours, the indicator has none):**
- Entry: limit at the signal close, active from the next bar, only when flat.
- Stop: the excursion extreme, fixed at the signal bar (lowest low since the move down began for a long,
  highest high since the move up began for a short).
- Target (`target`): `near` = nearest body edge, `far` = far body edge (limit orders), `rr1` / `rr2` = 1R / 2R
  measured in ticks from the actual fill, where R = signal close to stop.
- Session end: any open position is closed at the next bar open after the flat time.

A runnable Pine v6 twin for checking trades in TradingView is in
[`strategies/fair_price_reversal.pine`](../../../strategies/fair_price_reversal.pine).
"""

CONCLUSION = """
Execution rules changed to limit entries at the decision close, with unfilled entries cancelled after the
planned target is reached at a one-minute close. Historical market-entry conclusions do not apply. Read
the newly generated tables as in-sample research; independent replication and TradingView comparison are
pending.
"""


def notes(tf, params) -> list[str]:
    """Late session exits (a missing bar or an early close) and roll exits."""
    s = SESSIONS[params["session"]]
    out = []
    if not tf.empty:
        lt = tf["exit_time"].dt.tz_convert(s.tz)
        mod = lt.dt.hour * 60 + lt.dt.minute
        late = ((tf["exit_reason"] == "close") & ((mod > s.flat_minute + 5) | (mod < s.open_minute))).sum()
        out.append(f"Session-end exits more than 5 minutes after the flat time (missing bars / early closes): {late}.")
        out.append(f"Roll exits: {(tf['exit_reason'] == 'roll').sum()}.")
    return out
