"""FSP (Failed Swing Point): owner specification, 11 November 2026.

All swing qualification is delegated to tvtester.swings.Zig. The highest/lowest price used
for a stop is a risk anchor, not an alternative swing detector. Prices are integer CL ticks.
"""
from dataclasses import dataclass

import numpy as np

from tvtester import swings as sw
from tvtester.engine import LONG, SHORT, Context
from tvtester.fsp_clock import trading_clock
from tvtester.strategy import Strategy


@dataclass
class Setup:
    id: int
    direction: int
    candidate: int
    origin: int
    touch: int
    ready: int
    end: int | None = None
    reason: str = ""
    confirmation_candle: int = -1
    confirmation_end: int = -1
    confirmation_high: int | None = None
    confirmation_low: int | None = None
    first_signal: int | None = None


@dataclass(frozen=True)
class Signal:
    bar: int
    setup: int
    direction: int
    structure_bar: int
    structure: int
    stop_bar: int
    stop: int
    limit: int


def confirmation_window_hit(setup, i, high, low, candles):
    """Entry-eligibility filter only. Freeze the breach candle after it closes, never from future prices."""
    if i < setup.ready:
        return False
    if setup.confirmation_high is None:
        setup.confirmation_high = int(candles.h[setup.confirmation_candle])
        setup.confirmation_low = int(candles.l[setup.confirmation_candle])
    if i <= setup.confirmation_end:
        return False  # the confirmation candle touching its own high/low cannot invalidate itself
    return high >= setup.confirmation_high if setup.direction == SHORT else low <= setup.confirmation_low


class OwnerFrame:
    """Feed existing owner Zig at its documented source-candle close, using ordered 1m extremes."""

    def __init__(self, bars, timeframe):
        self.c = sw.candles(bars, timeframe)
        self.z = sw.Zig()
        self.opening = self.z.copy()
        self.j = 0

    def finish(self, j):
        c = self.c
        if j < 2:
            return False, False
        k = j - 1
        add_h, add_l = self.z.pivots(int(c.h[k - 1]), int(c.h[k]), int(c.h[j]),
                                    int(c.l[k - 1]), int(c.l[k]), int(c.l[j]), bool(c.hi_first[k]), k,
                                    opening=self.opening)
        return add_h or self.z.recovered_type == sw.SH, add_l or self.z.recovered_type == sw.SL

    def begin(self, i):
        added = False, False
        if i > self.c.end[self.j]:
            if self.c.visible[self.j] == i:
                added = self.finish(self.j)
            self.j += 1
            self.opening = self.z.copy()
        return added

    def close(self, i):
        if self.c.visible[self.j] == i and self.c.end[self.j] == i:
            return self.finish(self.j)
        return False, False


def stop_anchor(bars, pivot, signal, direction):
    """Extreme AFTER the structure point, including its own candle only when extreme order permits.

    The selected stop extreme needs left equality/strict improvement, never a right neighbour.
    Equal extremes select the later candle. No swing qualification is performed here.
    """
    hf = sw.open_rule_high_first(bars.o[pivot], bars.h[pivot], bars.l[pivot])
    start = pivot + (int(hf) if direction == SHORT else int(not hf))
    if start > signal:
        return None
    prices = bars.h if direction == SHORT else bars.l
    window = prices[start:signal + 1]
    extreme = int(window.max() if direction == SHORT else window.min())
    at = start + int(np.flatnonzero(window == extreme)[-1])
    if at == 0 or not (prices[at - 1] <= extreme if direction == SHORT else prices[at - 1] >= extreme):
        return None
    return at, extreme


class FailedSwingPoint(Strategy):
    name = "failed_swing_point"

    def __init__(self, setup_tf="1h", confirmation="15m", max_risk=25, tp=50, session="ny", filters=()):
        if filters:
            raise ValueError("FSP default has no entry filters")
        if setup_tf not in sw.TIMEFRAMES:
            raise ValueError("Use an owner-supported setup timeframe")
        if confirmation not in ("15m", "30m"):
            raise ValueError("FSP confirmation must be 15m or 30m")
        if max_risk != 25 or tp != 50 or session != "ny":
            raise ValueError("FSP default fixes max risk 25 ticks, TP 50 ticks and New York entries")
        super().__init__((), setup_tf=setup_tf, confirmation=confirmation, max_risk=max_risk, tp=tp, session=session)

    def prepare(self, bars):
        self.bars = bars
        self.signals = {}
        self.setups = []
        self.actions = []
        self.pending = None
        self.attempted_setups = set()
        self.closed = 0
        self.clock = trading_clock(bars)
        source = OwnerFrame(bars, self.params["setup_tf"])
        confirm = sw.candles(bars, self.params["confirmation"])
        z = sw.Zig()
        active = {}
        consumed = set()
        mask = np.zeros(len(bars), dtype=bool)
        mask[self.clock.session_close] = True
        cj = 0

        def expire(setup_id, i, reason):
            setup = active.pop(setup_id, None)
            if setup is not None:
                setup.end, setup.reason = i, reason
                mask[i] = True

        def expire_all(i, reason):
            for setup_id in tuple(active):
                expire(setup_id, i, reason)

        o, h, l, close = bars.o, bars.h, bars.l, bars.c
        for i in range(len(bars)):
            if i and self.clock.day[i] != self.clock.day[i - 1]:
                expire_all(i, "new_session_cycle")
            source.begin(i)
            hi, lo = int(h[i]), int(l[i])
            while cj + 1 < len(confirm.start) and i >= confirm.start[cj + 1]:
                cj += 1
            sz = source.z
            if sz.pending and (lo <= sz.last_price if sz.last_type == sw.SL else hi >= sz.last_price):
                side = SHORT if sz.last_type == sw.SL else LONG
                origin = int(source.c.start[sz.idx_l if side == SHORT else sz.idx_h])
                if bars.t_ms[i] + 60_000 < self.clock.deadline[i]:
                    setup = Setup(len(self.setups), side, int(sz.last_price), origin, i, int(confirm.visible[cj]),
                                  confirmation_candle=cj, confirmation_end=int(confirm.end[cj]))
                    self.setups.append(setup)
                    active[setup.id] = setup

            # Freeze the specific breach candle's range only once it is known closed. Never use
            # a later confirmation candle's levels, or invalidate from the breach candle's own range.
            for setup in tuple(active.values()):
                if confirmation_window_hit(setup, i, hi, lo, confirm):
                    expire(setup.id, i, "confirmation_high_touch" if setup.direction == SHORT else "confirmation_low_touch")

            touched = []
            if z.low_is_hl and lo <= z.cur_l:
                touched.append((SHORT, z.idx_l, int(z.cur_l)))
            if z.high_is_lh and hi >= z.cur_h:
                touched.append((LONG, z.idx_h, int(z.cur_h)))
            proposals = []
            for side, pivot, level in touched:
                key = side, pivot, level
                if key in consumed:
                    continue
                consumed.add(key)  # a touch before confirmation closes consumes this MSS too
                eligible = [setup for setup in active.values() if setup.direction == side
                            and setup.first_signal is None and pivot >= setup.touch and i > setup.ready]
                if not eligible or not self.clock.signal_window[i]:
                    continue
                anchor = stop_anchor(bars, pivot, i, side)
                if anchor is None:
                    continue
                at, stop = anchor
                risk = side * (int(close[i]) - stop)
                if risk <= 0:
                    continue
                limit = max(int(close[i]), stop - 25) if side == SHORT else min(int(close[i]), stop + 25)
                for setup in eligible:
                    proposals.append(Signal(i, setup.id, side, pivot, level, at, stop, limit))
            if i >= 2:
                k = i - 1
                z.pivots(int(h[k - 1]), int(h[k]), hi, int(l[k - 1]), int(l[k]), lo,
                         bool(sw.open_rule_high_first(o[k], h[k], l[k])), k)
            z.invalidate(hi, lo)
            source.close(i)
            sz.invalidate(hi, lo)
            if self.clock.session_close[i]:
                expire_all(i, "session_close")
            proposals = [s for s in proposals if self.setups[s.setup].end is None]
            if proposals:
                # At most one position. If both directions signal together, the newest setup wins;
                # same-minute ties use the minute's owner extreme order (the later touch).
                hf = bool(sw.open_rule_high_first(o[i], hi, lo))
                proposals.sort(key=lambda s: (self.setups[s.setup].touch, s.direction == (SHORT if hf else LONG)),
                               reverse=True)
                # Each failed source setup has one opportunity: its first valid MSS.
                # If another position/order prevents execution, never queue or replace that signal.
                for signal in proposals:
                    self.setups[signal.setup].first_signal = i
                self.signals[i] = proposals
                mask[i] = True
        return mask

    def before_bar(self, ctx: Context, i):
        """Enforce entry hours and the NY session no-carry boundary before this minute."""
        self._check_session_boundary(ctx, i)

    def _check_session_boundary(self, ctx, i):
        if ctx.position_size != 0:
            entry = ctx.position_entry_bar
            if self.bars.t_ms[i] >= self.clock.deadline[entry]:
                # The cutoff passed without a tradable closing minute. Queue the overdue
                # market close BEFORE processing the first reopening bar, so it fills at
                # that bar's OPEN, before any intrabar stop/target or new entry can act.
                self._cancel(ctx, i, "halt_session_close")
                ctx.cancel_all()
                ctx.close_all("New York halt reopen")
        if self.pending is not None:
            if not self.clock.fill_window[i]:
                self._cancel(ctx, i, "entry_session_end")
            elif self.clock.day[i] != self.clock.day[self.setups[self.pending.setup].touch]:
                self._cancel(ctx, i, "session_reset")

    def _session_flat(self, ctx, i):
        if not self.clock.session_close[i]:
            return False
        self._cancel(ctx, i, "session_close")
        ctx.cancel_all()
        if ctx.position_size != 0:
            ctx.close_all("New York close", immediately=True)
        self.closed = ctx.closed_trades
        return True

    def _cancel(self, ctx, i, reason):
        if self.pending is not None:
            self.actions.append((i, "cancel", self.pending.bar, reason))
            ctx.cancel("FSP")
            ctx.cancel("FSP exit")
            self.pending = None

    def on_bar(self, ctx, i):
        # Filled orders belong to their own position; subsequent setup expiry does not close it.
        filled = ctx.position_size != 0 or ctx.closed_trades != self.closed
        self.closed = ctx.closed_trades
        if filled:
            self.pending = None
        if self._session_flat(ctx, i):
            return
        if ctx.position_size != 0:
            return
        if self.pending is not None:
            if not ctx.has_entry("FSP"):
                self._cancel(ctx, i, "entry_order_removed")
        if self.bars.last_of_contract[i]:
            self._cancel(ctx, i, "roll")
            return
        if self.pending is not None:
            return  # fixed pending limit; no re-pricing or replaying already used MSS signals
        if not self.clock.signal_window[i]:
            return
        for signal in self.signals.get(i, ()):
            setup = self.setups[signal.setup]
            if setup.id in self.attempted_setups:
                continue
            if setup.first_signal is not None and setup.first_signal != i:
                continue
            if self.clock.day[setup.touch] != self.clock.day[i]:
                continue
            if setup.end is not None and setup.end <= i:
                continue
            ctx.entry("FSP", signal.direction, limit=signal.limit)
            ctx.exit("FSP exit", "FSP", stop=signal.stop, profit=self.params["tp"])
            self.attempted_setups.add(setup.id)
            self.pending = signal
            self.actions.append((i, "place", signal.bar, ""))
            break


STRATEGY = FailedSwingPoint
TITLE = "FSP — Failed Swing Point, CL1!"
DOC = "results.md"
GRID = {"setup_tf": ["1h"], "confirmation": ["15m"], "max_risk": [25], "tp": [50]}
VARIANTS = {"ny": {"session": "ny"}}
ABOUT = """
Fixed default FSP, owner specification: [README.md](README.md). Provisional 1H owner swing failure;
wait for the containing 15m candle to close, then a fresh post-breach owner 1m HL/LH touch and that
minute's close. Limit at the signal close or 25 ticks from the stop when closer to the stop is required.
TP 50 ticks from actual fill; stop is the post-structure price extreme with left equality permitted,
without requiring right confirmation. Both directions, New York entries 09:00–14:30 ET.
Only the first valid 1m MSS per failed 1H setup is eligible; no retries after fill, TP, SL or cancellation.
After the breach confirmation candle closes, an equal touch of its fixed high invalidates later short
MSS signals; an equal touch of its fixed low invalidates later long MSS signals. Reject the MSS minute
itself if it reaches that boundary before its close. Already-placed limits retain their price and stop;
there is no additional 1H or 15m-boundary pending-order cancellation. New York close at 14:30 ET
(or earlier scheduled exchange close) cancels limits, flattens positions and discards setups. Only a
new failed setup can arm another trade. Swings continue across days/rolls. If a halt spans the cutoff,
close the existing position at the first tradable reopening price; cancel old orders before processing that bar.
This is one fixed baseline, not a parameter search. Performance data ends before 2024-01-01 UTC.
"""
