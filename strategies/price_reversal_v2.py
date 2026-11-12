"""Price Reversal v2: the Fair Price Reversal setup anchored to any Globex hourly candle, with optional entry cap
and fixed take-profit tiers. Pine twin: strategies/price_reversal_v2.pine.

Anchors (`anchor`):
- "h01".."h23": Globex hour number. Hour 1 opens 18:00 America/New_York (the CME reopen; 06:00 Malaysia in US
  summer time, 07:00 in US winter time), hour 23 opens 16:00 ET. The anchor candle is the bar just before the
  hour's first bar of that Globex trading date (hour 1: the previous session's last bar). Entries from the hour
  open to `flat - 1 min`, flat = hour open + HOLD_MINUTES, never later than 16:59 ET (so the session-end market
  close fills at 16:59, before the 17:00 ET halt).
- "asia" / "london" / "ny": the Fair Price Reversal sessions, identical rules (parity reference).

Signal: tvtester's Fair Price Reversal setup (strategies/fair_price_reversal.py, shared `setup_signals`).

Entry (`entry_cap`, ticks; 0 = original):
- 0: limit at the signal close (Fair Price Reversal).
- N > 0: if |signal close - stop| > N, limit at stop + N (long) / stop - N (short), i.e. the stop distance is
  capped at N ticks; otherwise limit at the signal close. The stop never moves.
Target (`tp_mode`):
- "default": the `target` rule with R = |planned limit - stop| (rr1 / rr2 ticks from the fill; near / far =
  anchor body edge prices).
- "fixed": profit = 2 x tier ticks from the fill, tier = smallest of 20, 25, 30, ... that is >= R
  (R <= 20 -> 40 ticks, R <= 25 -> 50, R <= 30 -> 60, ...). `target` is ignored.
Pending entry lifetime, flat rule, roll rule and filters are those of Fair Price Reversal.
"""

from contextlib import contextmanager

import numpy as np
import pandas as pd

from strategies.fair_price_reversal import (
    FILTER_SPACE as FPR_FILTER_SPACE,
)
from strategies.fair_price_reversal import (
    RANGE_BARS,
    RANGE_DAYS,
    TARGETS,
    FairPriceReversal,
    _shared,
    setup_signals,
)
from tvtester import features as fx
from tvtester import ta
from tvtester.data import Bars
from tvtester.engine import LONG, Context
from tvtester.sessions import Session

ET = "America/New_York"
GLOBEX_OPEN = 18 * 60  # ET minute of hour 1
LAST_MINUTE = 1379  # Globex minute of 16:59 ET; the 17:00 ET halt follows
HOLD_MINUTES = 300  # an hourly anchor trades for 5 hours (FPR sessions: 5 to 6 hours)
TP_MODES = ("default", "fixed")
TIER_STEP, TIER_MIN = 5, 20
HOURS = [f"h{k:02d}" for k in range(1, 24)]


def globex_clock(bars: Bars) -> tuple[np.ndarray, np.ndarray]:
    """(minute since 18:00 ET, Globex trading date as yyyymmdd) of each bar open. The trading date is the ET date
    of the bar open plus 6 hours (18:00 ET Sunday belongs to Monday)."""
    k = ("price_reversal_v2", "globex_clock")
    if k not in bars.cache:
        et = bars.ts.tz_convert(ET)
        g = ((et.hour * 60 + et.minute).to_numpy() - GLOBEX_OPEN) % 1440
        d = et + pd.Timedelta(hours=6)
        bars.cache[k] = (g, (d.year * 10000 + d.month * 100 + d.day).to_numpy())
    return bars.cache[k]


def hour_session(anchor: str) -> Session:
    """An hourly anchor as a Session on the Globex clock (minutes since 18:00 ET)."""
    h = int(anchor[1:])
    if not 1 <= h <= 23:
        raise ValueError("hour anchors are h01..h23")
    start = (h - 1) * 60
    return Session(anchor, ET, start, min(start + HOLD_MINUTES, LAST_MINUTE))


def hour_anchors(g: np.ndarray, day: np.ndarray, start: int) -> np.ndarray:
    """Bar before the first bar of the hour [start, start + 60) on each Globex date."""
    in_hour = (g >= start) & (g < start + 60)
    idx = np.flatnonzero(in_hour)
    if len(idx) == 0:
        return idx
    first = idx[np.concatenate([[True], day[idx[1:]] != day[idx[:-1]]])]
    return first[first > 0] - 1


def hour_features(bars: Bars, start: int, anchors: np.ndarray, sg: dict, atr_len: int = 14) -> dict[str, np.ndarray]:
    """The five FPR features for an hour anchor, on the Globex clock (docs/OPTIMIZE.md, FPR contracts): minutes
    from the hour open, anchor body / ATR[1] and range ratio at the anchor bar (carried forward), risk at the
    signal bar in ticks and in ATR[1]."""
    n = len(bars)
    g, _ = globex_clock(bars)
    move_atr = _shared(bars, ("atr1", atr_len), lambda: ta.shift(ta.atr(bars.h, bars.l, bars.c, atr_len), 1))

    def anchored():
        a = anchors
        body = np.abs(bars.c[a] - bars.o[a]).astype(float)
        with np.errstate(invalid="ignore", divide="ignore"):
            body_atr = np.where(move_atr[a] > 0, body / move_atr[a], np.nan)
        rr = fx.ratio_to_trailing_mean(fx.prior_range(bars.h, bars.l, a, RANGE_BARS), RANGE_DAYS)
        return fx.carry_forward(a, body_atr, n), fx.carry_forward(a, rr, n)

    # anchors depend only on the hour start, never on window / atr_mult
    body_atr, range_ratio = _shared(bars, ("v2_anchored", start, atr_len), anchored)
    risk = np.full(n, np.nan)
    at = np.flatnonzero(sg["sig"])
    risk[at] = np.abs(bars.c[at] - sg["stop"][at])
    with np.errstate(invalid="ignore", divide="ignore"):
        risk_atr = np.where(move_atr > 0, risk / move_atr, np.nan)
    return {"minutes_from_open": (g - start).astype(float), "anchor_body_atr": body_atr,
            "risk_ticks": risk, "risk_atr": risk_atr, "range_ratio": range_ratio}


def tier_profit(risk: int) -> int:
    """Fixed take-profit in ticks: 2 x the smallest tier (20, 25, 30, ...) at least `risk`."""
    tier = max(TIER_MIN, -(-risk // TIER_STEP) * TIER_STEP)
    return 2 * tier


def planned_limit(direction: int, close: int, stop: int, cap: int) -> int:
    """Entry limit: the signal close, or stop +/- cap when the close is more than `cap` ticks from the stop."""
    if cap > 0 and abs(close - stop) > cap:
        return stop + direction * cap
    return close


class PriceReversalV2(FairPriceReversal):
    name = "price_reversal_v2"

    def __init__(self, anchor: str = "h16", window: int = 60, atr_mult: float = 1.0, swing: int = 1,
                 target: str = "rr2", atr_len: int = 14, entry_cap: int = 0, tp_mode: str = "default",
                 filters=(), **exit_rule):
        hourly = anchor.startswith("h")
        if tp_mode not in TP_MODES:
            raise ValueError(f"tp_mode must be one of {TP_MODES}")
        if entry_cap < 0:
            raise ValueError("entry_cap must be >= 0 ticks")
        super().__init__("ny" if hourly else anchor, window, atr_mult, swing, target, atr_len, filters, **exit_rule)
        self.params = {"anchor": anchor, **{k: v for k, v in self.params.items() if k != "session"},
                       "entry_cap": int(entry_cap), "tp_mode": tp_mode}
        self.hourly = hourly
        if hourly:
            self.s = hour_session(anchor)
            self.report_tz = ET

    def prepare(self, bars: Bars) -> np.ndarray:
        if not self.hourly:
            with self._as_session():
                return super().prepare(bars)
        p = self.params
        self.bars = bars
        self.exits.prepare(bars)
        self.pending = type(self.pending)()
        self.t_bar = -1
        g, day = globex_clock(bars)
        key = (p["anchor"], p["window"], p["atr_mult"], p["atr_len"])
        cached = bars.cache.get(("price_reversal_v2", "signals"))
        if cached is None or cached[0] != key:
            start = self.s.open_minute
            in_win = (g >= start) & (g < start + p["window"])
            after = g >= start + p["window"]
            anchors = hour_anchors(g, day, start)
            cached = (key, setup_signals(bars, anchors, in_win, after, p["atr_mult"], p["atr_len"]), anchors)
            bars.cache[("price_reversal_v2", "signals")] = cached
        self.sig, self.anchors = cached[1], cached[2]
        self.mod = g
        self.allow = np.ones(len(bars), dtype=bool)
        if self.filters:
            self.allow = fx.gate(self.filters, self.features(bars), len(bars))
        return (self.sig["sig"] != 0) & self.allow

    def features(self, bars: Bars) -> dict[str, np.ndarray]:
        if self.hourly:
            return hour_features(bars, self.s.open_minute, self.anchors, self.sig, self.params["atr_len"])
        with self._as_session():
            return super().features(bars)

    @contextmanager
    def _as_session(self):
        """FPR's code reads params["session"]; v2 names it `anchor`. Re-entrant: FPR's prepare calls features."""
        added = "session" not in self.params
        if added:
            self.params["session"] = self.params["anchor"]
        try:
            yield
        finally:
            if added:
                del self.params["session"]

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
            return
        sg, p = self.sig, self.params
        stop = int(sg["stop"][i])
        entry = planned_limit(d, int(self.bars.c[i]), stop, p["entry_cap"])
        eid = "Long" if d == LONG else "Short"
        ctx.entry(eid, d, limit=entry)
        self.eid, self.stop, self.limit, self.profit = eid, stop, None, None
        risk = abs(entry - stop)
        if p["tp_mode"] == "fixed":
            self.profit = tier_profit(risk)
        elif p["target"] in ("near", "far"):
            near = sg["body_lo"][i] if d == LONG else sg["body_up"][i]
            far = sg["body_up"][i] if d == LONG else sg["body_lo"][i]
            self.limit = int(near if p["target"] == "near" else far)
        else:
            self.profit = risk * (1 if p["target"] == "rr1" else 2)
        planned_tp = self.limit if self.limit is not None else entry + d * self.profit
        self.pending.place(eid, d, planned_tp)
        self._bracket(ctx, stop)


# --- test definition (python -m tvtester.cli test price_reversal_v2) -------------------------------------
STRATEGY = PriceReversalV2
TITLE = "Price Reversal v2 (hourly anchors, entry cap, fixed TP), CL1!"
DOC = "README.md"
BASE_GRID = {"window": [30, 60, 90, 120], "atr_mult": [0.5, 1.0, 1.5, 2.0], "swing": [1], "target": list(TARGETS)}
ENTRY_CAPS = [0, 20, 25, 30, 35, 40, 45, 50]
# Entry study: Fair Price Reversal's frozen per-session baselines (strategies/fair_price_reversal.py BASELINES).
ENTRY_BASE = {
    "asia": {"window": 30, "atr_mult": 2.0, "target": "rr2"},
    "london": {"window": 30, "atr_mult": 1.5, "target": "rr2"},
    "ny": {"window": 120, "atr_mult": 0.5, "target": "rr2"},
}
ENTRY_GRID = {"entry_cap": ENTRY_CAPS, "tp_mode": list(TP_MODES)}
GRID = BASE_GRID
VARIANTS = {**{h: {"anchor": h} for h in HOURS},
            **{f"entry_{s}": {"anchor": s, "swing": 1, **b} for s, b in ENTRY_BASE.items()}}
GRIDS = {f"entry_{s}": ENTRY_GRID for s in ENTRY_BASE}  # per-variant grid (default GRID)

# --- optimize definition (feature 2; protocol: docs/strategies/price_reversal_v2/optimize/README.md) -----
FEATURES = ("minutes_from_open", "anchor_body_atr", "risk_ticks", "risk_atr", "range_ratio")
FILTER_SPACE = dict(FPR_FILTER_SPACE)
# Feature-1 top combinations (2026-11-12, all bars) of the variants that passed the declared gate.
BASELINES: dict[str, dict] = {
    "h01": {"window": 60, "atr_mult": 2.0, "swing": 1, "target": "rr2"},
    "h02": {"window": 60, "atr_mult": 0.5, "swing": 1, "target": "far"},
    "entry_london": {"entry_cap": 50, "tp_mode": "default"},
}
SPACES = {"filters": {"params": {}, "filters": FILTER_SPACE}}
LINEAGE = ("Price Reversal v2 shares Fair Price Reversal's setup code. Entry-study baselines are the FPR "
           "owner-swing F1 winners of 2026-11-04 (pre 2026-11-05 swing fix), chosen on all available CL bars.")
ABOUT = """
New strategy built 12 November 2026 from the owner's two questions about Fair Price Reversal (FPR):

1. **Does the hourly candle matter?** The FPR setup is anchored to the candle before each of the 23 Globex
   hours. Hour 1 opens 18:00 New York (06:00 Malaysia in US summer time, 07:00 in US winter time); hour 16 is
   09:00 ET (the FPR NY open); hour 23 is 16:00 ET. Because the clock is New York time, the hour number moves
   with US daylight saving time exactly as the owner defined it. Each hour variant runs the full FPR grid and
   trades for up to 5 hours after its open, never past 16:59 ET (the 17:00 ET halt).
2. **Entry cap and fixed TP.** On FPR's frozen session baselines (`entry_asia`, `entry_london`, `entry_ny`):
   `entry_cap` N > 0 places the limit N ticks from the stop when the signal close is further than N ticks from
   it (otherwise at the close, as FPR); `tp_mode = fixed` uses 2 x the 5-tick tier at or above the stop
   distance (<= 20 -> 40, <= 25 -> 50, <= 30 -> 60, ...). `entry_cap = 0, tp_mode = default` is FPR itself.

**Signal:** unchanged FPR setup (anchor body = fair price, `atr_mult` x ATR(14) move away, owner swing
market-structure shift back toward the body; one long and one short per anchor day).

**Trade rules:** limit entry from the next bar, stop = excursion extreme, target `near` / `far` / `rr1` / `rr2`
(R = planned entry to stop) or fixed tiers, unfilled entry cancelled when the planned TP is reached at a
one-minute close or the session ends, flat at the next bar open after the flat time.

Per-hour and entry-study comparisons across every combination (not only the top one):
[study.md](study.md). Pine v6 twin:
[`strategies/price_reversal_v2.pine`](../../../strategies/price_reversal_v2.pine).
"""
CONCLUSION = """
In-sample, all available bars (2024+ included), best of the grid per variant. Read study.md before drawing
conclusions: a best-of-64 hour result is biased upward; the study page shows the whole grid per hour.
Independent replication (Codex) and a TradingView comparison of the Pine twin are pending.
"""


def notes(tf, params) -> list[str]:
    out = []
    if not tf.empty:
        out.append(f"Session-end exits: {(tf['exit_reason'] == 'close').sum()}.")
        out.append(f"Roll exits: {(tf['exit_reason'] == 'roll').sum()}.")
    return out
