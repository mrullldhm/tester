"""Tupa Trade v2: Tupa Trade v1 (strategies/tupa_trade.py, owner spec docs/strategies/tupa_trade/README.md
sections 3b and 3c) plus five switches for Claude's open interpretation choices. All switches at their first
value = v1 trade for trade (tests/test_tupa_trade_v2.py). CL1! 1-minute bars.

Pure price action on the owner swing points (indicators/structure_swings.pine, Python twin tvtester/swings.py).
Short side below; the long side is the exact mirror.

1. Tested timeframe T: the lowest timeframe from `t_min` up to 1d whose newest swing is a swing low (a candidate:
   no swing high confirmed after it). Bias short when every timeframe below T, down to 5m, is in downtrend (its last
   uptrend HL touched by a closed candle). Closed higher-timeframe candles only.
2. Entry, 1m market structure shift: the newest confirmed 1m swing is a swing high, the swing low before it is a HL
   and has not been touched since it formed. Sell stop-limit: stop (trigger) = that HL (break point), touch counts;
   limit = the break point, or stop loss - `max_risk` ticks when the stop loss is more than `max_risk` ticks away.
3. Stop loss exactly at the newest 1m swing high; take profit `tp` ticks from the fill.
4. Before the trigger the order follows the setup at every 1m close (moved when the levels change, cancelled when
   the setup goes). After the trigger it stays until it fills or the next 1m swing high is confirmed (cancel).
5. New York session only, 09:00-14:30 New York: orders work from the 09:00 bar; at the close of the 14:29 bar an
   open trade is closed (fills at the next open) and an unfilled order is cancelled. One trade per session.

Claude's choices where the owner has not decided yet (v1 README section 3d) are the switches below; steps 1-4
above describe their v1 values.

Feature-2 interpretation study (docs/strategies/tupa_trade_v2/optimize/README.md). Each switch's first value is v1:
- `t_rule`: "lowest" | "highest" timeframe from `t_min` up to 1d with a candidate swing is T.
- `trend`: "sticky" (down until the LH is touched) | "fresh" (cleared by that timeframe's next swing high after
  the break; tvtester/swings.py).
- `touched`: "skip" | "retest": place the order even when the break point was already touched. With the close
  at or through the break point the order is a plain limit (already triggered) that waits for price to come back.
- `order`: "follow" (moved / cancelled with the setup before the trigger) | "freeze" (kept from placement until
  the next 1m swing high (long: low) is confirmed, the planned TP is reached, the session ends or it fills).
- `tp_expiry`: "on" (cancel the unfilled order when the planned TP is reached) | "off".
"""

import numpy as np

from tvtester import swings as sw
from tvtester.data import Bars
from tvtester.engine import LONG, SHORT, Context
from tvtester.sessions import SESSIONS, local_clock
from tvtester.strategy import Strategy

T_CHOICES = ("15m", "1h", "4h", "1d")
SWITCHES = {"t_rule": ("lowest", "highest"), "trend": ("sticky", "fresh"), "touched": ("skip", "retest"),
            "order": ("follow", "freeze"), "tp_expiry": ("on", "off")}  # first value = v1


def _shared(bars: Bars, key, fn):
    k = ("tupa_trade_v2", key)
    if k not in bars.cache:
        bars.cache[k] = fn()
    return bars.cache[k]


def tf_states(bars: Bars) -> dict:
    """Per timeframe: (state, per-bar index of the state that applies)."""
    def build():
        out = {}
        for tf in sw.TIMEFRAMES:
            st = sw.timeframe_state(bars, tf)
            out[tf] = (st, st.at_bars(len(bars)))
        return out
    return _shared(bars, "tf", build)


def bias(bars: Bars, t_min: str, t_rule: str = "lowest", trend: str = "sticky") -> np.ndarray:
    """+1 long bias, -1 short bias, 0 none, at each 1m bar close."""
    def build():
        st = tf_states(bars)
        n = len(bars)
        lt, tr = [], []
        for tf in sw.TIMEFRAMES:
            s, at = st[tf]
            ok = at >= 0
            j = np.maximum(at, 0)
            lt.append(np.where(ok, s.last_type[j], 0))
            tr.append(np.where(ok, (s.trend if trend == "sticky" else s.fresh)[j], 0))
        out = np.zeros(n, dtype=np.int8)
        k0 = sw.TIMEFRAMES.index(t_min)
        ks = range(k0, len(sw.TIMEFRAMES))
        for d, cand in ((SHORT, sw.SL), (LONG, sw.SH)):
            found = np.zeros(n, dtype=bool)
            for k in (ks if t_rule == "lowest" else reversed(ks)):
                here = ~found & (lt[k] == cand)
                below = np.ones(n, dtype=bool)
                for j in range(k):
                    below &= tr[j] == d
                out[here & below] = d
                found |= here
        return out
    return _shared(bars, ("bias", t_min, t_rule, trend), build)


class TupaTradeV2(Strategy):
    name = "tupa_trade_v2"

    def __init__(self, t_min: str = "1h", tp: int = 25, max_risk: int = 25, session: str = "ny",
                 t_rule: str = "lowest", trend: str = "sticky", touched: str = "skip", order: str = "follow",
                 tp_expiry: str = "on", filters=()):
        if t_min not in T_CHOICES:
            raise ValueError(f"t_min must be one of {T_CHOICES}")
        sel = {"t_rule": t_rule, "trend": trend, "touched": touched, "order": order, "tp_expiry": tp_expiry}
        for k, v in sel.items():
            if v not in SWITCHES[k]:
                raise ValueError(f"{k} must be one of {SWITCHES[k]}")
        if filters:
            raise NotImplementedError("tupa_trade_v2 has no feature-2 filters yet")
        super().__init__((), t_min=t_min, tp=tp, max_risk=max_risk, session=session, **sel)
        self.s = SESSIONS[session]
        self.report_tz = self.s.tz

    # --- indicators (every bar) --------------------------------------------------------------------------
    def prepare(self, bars: Bars) -> np.ndarray:
        p = self.params
        self.bars = bars
        self.bias = bias(bars, p["t_min"], p["t_rule"], p["trend"])
        self.m1 = _shared(bars, "m1", lambda: sw.minute_swings(bars))
        self.mod, self.day = _shared(bars, ("clock", self.s.tz), lambda: local_clock(bars.ts, self.s.tz))
        self.win = (self.mod >= self.s.open_minute - 1) & (self.mod < self.s.flat_minute - 1)
        self.cur_day, self.traded, self.n_closed = None, False, 0
        self.pend = None  # (direction, break point, stop loss, limit, swing count, placed bar)
        self.trig = False
        self.expired = None
        return self.win

    def setup(self, i: int):
        """(direction, break point, stop loss, limit, swing count) of the MSS order wanted at bar i's close."""
        d = int(self.bias[i])
        e = int(self.m1.at[i])
        if d == 0 or e < 0:
            return None
        m, b = self.m1, self.bars
        if d == SHORT:
            if m.last_type[e] != sw.SH or m.prev_l[e] == sw.NONE or m.cur_l[e] <= m.prev_l[e]:
                return None
            bp, sl, cnt = int(m.cur_l[e]), int(m.cur_h[e]), int(m.n_h[e])
            if self.params["touched"] == "skip" and b.l[m.idx_l[e] + 1: i + 1].min() <= bp:
                return None  # break point already touched: the MSS happened before the order could exist
            risk = sl - bp
            lim = sl - self.params["max_risk"] if risk > self.params["max_risk"] else bp
        else:
            if m.last_type[e] != sw.SL or m.prev_h[e] == sw.NONE or m.cur_h[e] >= m.prev_h[e]:
                return None
            bp, sl, cnt = int(m.cur_h[e]), int(m.cur_l[e]), int(m.n_l[e])
            if self.params["touched"] == "skip" and b.h[m.idx_h[e] + 1: i + 1].max() >= bp:
                return None
            risk = bp - sl
            lim = sl + self.params["max_risk"] if risk > self.params["max_risk"] else bp
        return d, bp, sl, lim, cnt

    # --- orders at each bar close ------------------------------------------------------------------------
    def _cancel(self, ctx: Context) -> None:
        if self.pend is not None:
            ctx.cancel("Long" if self.pend[0] == LONG else "Short")
            ctx.cancel("Exit")
        self.pend, self.trig = None, False

    def on_bar(self, ctx: Context, i: int) -> None:
        if self.day[i] != self.cur_day:
            self.cur_day, self.traded = self.day[i], False
        if ctx.position_size != 0 or ctx.closed_trades != self.n_closed:
            self.n_closed, self.traded = ctx.closed_trades, True
            self.pend, self.trig = None, False
        if ctx.position_size != 0:
            if not self.win[i]:
                ctx.close_all("Session end")
            return
        if not self.win[i] or self.traded or self.bars.last_of_contract[i]:
            self._cancel(ctx)
            return
        if self.pend is not None:
            d, bp, _, lim = self.pend[:4]
            planned_tp = lim + d * self.params["tp"]
            reached = self.bars.h[i] >= planned_tp if d == LONG else self.bars.l[i] <= planned_tp
            if reached and self.params["tp_expiry"] == "on":
                self.expired = self.pend[:5]
                self._cancel(ctx)
                return
            if not self.trig and i > self.pend[5] and (self.bars.l[i] <= bp if d == SHORT else self.bars.h[i] >= bp):
                self.trig = True  # the stop-limit is now a limit order
            if self.trig or self.params["order"] == "freeze":
                e = int(self.m1.at[i])
                cnt = int(self.m1.n_h[e] if d == SHORT else self.m1.n_l[e])
                if cnt == self.pend[4]:
                    return
                self._cancel(ctx)  # next 1m swing high (long: swing low) confirmed before a fill (freeze: or trigger)
        want = self.setup(i)
        if want is None or want == self.expired:
            self._cancel(ctx)
            return
        if self.pend is not None and self.pend[:4] == want[:4]:
            return
        self._cancel(ctx)
        d, bp, sl, lim, cnt = want
        eid = "Long" if d == LONG else "Short"
        c = self.bars.c[i]
        through = bp >= c if d == SHORT else bp <= c  # only with touched="retest": already triggered
        if through:
            ctx.entry(eid, d, limit=lim)
        else:
            ctx.entry(eid, d, stop=bp, limit=lim)
        ctx.exit("Exit", eid, stop=sl, profit=self.params["tp"])
        self.pend, self.trig = (d, bp, sl, lim, cnt, i), through


# --- test definition (python -m tvtester.cli test tupa_trade_v2) -------------------------------------------
STRATEGY = TupaTradeV2
DOC = "results.md"  # README.md in the same folder describes v2; the owner spec is docs/strategies/tupa_trade/README.md
TITLE = "Tupa Trade v2 (owner price action, MSS stop-limit, interpretation switches), CL1! New York session"
GRID = {"t_min": list(T_CHOICES)}
VARIANTS = {"ny": {"session": "ny"}}

# --- optimize definition (feature 2; protocol: docs/strategies/tupa_trade_v2/optimize/README.md) -------------
# Baseline = the feature-1 top combination (all bars, owner swings v4), with every switch at its v1 value.
BASELINES: dict[str, dict] = {"ny": {"t_min": "1d", "tp": 25, "max_risk": 25, **{k: v[0] for k, v in SWITCHES.items()}}}
# Interpretation study: every combination of the five open choices. With t_min = 1d the only candidate timeframe
# is the daily, so "highest" equals "lowest" there: excluded (112 behaviour-distinct configurations).
SPACES = {"interpretation": {"params": {"t_min": list(T_CHOICES), **{k: list(v) for k, v in SWITCHES.items()}},
                             "filters": {}, "exclude": [{"t_min": "1d", "t_rule": "highest"}]}}
LINEAGE = ("Tupa Trade v2 = v1 (strategies/tupa_trade.py) plus interpretation switches, created 2026-11-12. v1 was "
           "run in feature 1 on all CL bars (4 t_min combinations, 2026-11-03/04); v2 feature 1 (switches at v1) "
           "reruns that grid. No earlier feature-2 work on either.")
ABOUT = """
**Tupa Trade v2** = v1 plus five interpretation switches ([README.md](README.md)); this feature-1 run keeps every
switch at its v1 value, so it is v1 under the current owner swings. Owner spec:
[`../tupa_trade/README.md`](../tupa_trade/README.md) (sections 3b and 3c). Pure price action on the owner swing points
([`indicators/structure_swings.pine`](../../../indicators/structure_swings.pine)), New York session only
(09:00-14:30 New York = 21:00-02:30 Malaysia time in US summer time, 22:00-03:30 in US winter time). Short side
below; the long side is the mirror.

- **Bias.** Tested timeframe T = the lowest timeframe from `t_min` up to daily whose newest swing is a swing low
  (a candidate: no swing high confirmed after it). Short bias when every timeframe below T, down to 5m, is in
  downtrend (its last uptrend HL touched by a closed candle). Timeframes 5m, 15m, 1H, 4H (anchored 18:00 New York),
  daily (CME trading day). Closed candles only.
- **Entry (1m market structure shift).** Newest confirmed 1m swing is a swing high and the swing low before it is
  a HL, not touched yet. Sell **stop-limit**: trigger = that HL (touch counts), limit = the HL, or stop loss - 25
  ticks when the stop loss is more than 25 ticks away.
- **Exits.** Stop loss exactly at the 1m swing high, take profit 25 ticks from the fill, or close at the New York
  session end (next open after the 14:29 bar). An unfilled triggered limit is cancelled when the next 1m swing high
  is confirmed. One trade per session.
- **Grid.** `t_min` (lowest timeframe allowed as T) is Claude's open point, not an owner rule. Everything else is
  fixed by the owner: TP 25 ticks, max risk 25 ticks.

Stop-limit fills follow the engine's stop-limit rule (`docs/ENGINE.md`, fills rule 8), not yet checked against a
TradingView export. A runnable Pine v6 twin is in [`strategies/tupa_trade_v2.pine`](../../../strategies/tupa_trade_v2.pine).
"""


def notes(tf, params) -> list[str]:
    s = SESSIONS[params["session"]]
    out = []
    if not tf.empty:
        lt = tf["exit_time"].dt.tz_convert(s.tz)
        mod = lt.dt.hour * 60 + lt.dt.minute
        late = ((tf["exit_reason"] == "close") & ((mod > s.flat_minute + 5) | (mod < s.open_minute))).sum()
        out.append(f"Session-end exits more than 5 minutes after the flat time (missing bars / early closes): {late}.")
        out.append(f"Roll exits: {(tf['exit_reason'] == 'roll').sum()}.")
    return out
