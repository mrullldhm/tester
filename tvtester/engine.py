"""TradingView broker emulator and the bar loop.

Semantics (docs/ENGINE.md has the full list):
- The strategy runs at each bar's close. Orders it places work from the next bar.
- Intrabar path: O-H-L-C when the high is nearer the open, else O-L-H-C (tie goes O-L-H-C).
- Market orders fill at the next open. A stop or limit the open gaps through fills at the open; otherwise it
  fills at its own price when the path reaches it. A stop already through the close when it was placed is
  triggered and fills at the next open like a market order.
- Stop-limit entries (stop and limit both given): the stop is only a trigger. When the path reaches it (or the open
  gaps through it) the order becomes a limit order at its limit price, which can fill later on the same bar
  along the path (at once, at the trigger point, when the limit is already marketable there).
- Exits (strategy.exit) wait for their entry and can fill on the entry bar, from the fill point on.
- Slippage: market and stop fills move N ticks against the trader; limits never slip.
- Commission per filled order.
- Roll rule: a position open on the last bar of a contract is closed at that bar's close (reason "roll").
All prices are integer ticks.
"""

from dataclasses import dataclass, field

import numpy as np

from .config import DEFAULT, TICK_VALUE, Properties
from .data import Bars

LONG, SHORT = 1, -1


@dataclass
class Order:
    id: str
    kind: str  # "entry" | "exit" | "close"
    side: int  # +1 buys, -1 sells
    stop: int | None = None
    limit: int | None = None
    from_entry: str | None = None
    profit: int | None = None  # exit: ticks from the entry fill
    loss: int | None = None
    oca: str | None = None
    placed_bar: int = -1
    comment: str = ""
    placed_in_position: bool = False
    abs_stop: int | None = None  # exit: absolute levels as given, kept apart from profit / loss distances
    abs_limit: int | None = None
    triggered: bool = False  # stop-limit entry: the stop has been reached, only the limit works now


@dataclass
class Trade:
    direction: int
    entry_id: str
    entry_bar: int
    entry_price: int
    signal_bar: int = -1  # bar whose close placed the entry order
    exit_id: str = ""
    exit_bar: int = -1
    exit_price: int = 0
    exit_reason: str = ""
    best: int = 0  # most favourable price while exposed (ticks)
    worst: int = 0
    commission: float = 0.0
    profit: float = 0.0  # net of commission, $
    qty: int = 1
    initial_risk_ticks: int | None = None  # actual fill to attached initial stop; frozen before any stop move


@dataclass
class Result:
    trades: list[Trade]
    open_trade: Trade | None
    bars: Bars
    props: Properties
    last_bar: int


class Context:
    """What a strategy sees and calls at a bar's close (Pine `strategy.*`)."""

    def __init__(self, engine: "Engine"):
        self._e = engine

    @property
    def position_size(self) -> int:
        t = self._e.pos
        return 0 if t is None else t.direction * t.qty

    @property
    def position_avg_price(self) -> int | None:
        return None if self._e.pos is None else self._e.pos.entry_price

    @property
    def position_entry_bar(self) -> int | None:
        """Bar index of the open position's entry fill (Pine strategy.opentrades.entry_bar_index(0))."""
        return None if self._e.pos is None else self._e.pos.entry_bar

    @property
    def closed_trades(self) -> int:
        """Number of closed trades (Pine strategy.closedtrades)."""
        return len(self._e.trades)

    @property
    def bar_index(self) -> int:
        return self._e.i

    def entry(self, id: str, direction: int, stop: int | None = None, limit: int | None = None,
              oca: str | None = None, comment: str = "") -> None:
        if stop is not None and limit is not None:
            c = self._e.c[self._e.i]
            if (direction == LONG and stop <= c) or (direction == SHORT and stop >= c):
                raise NotImplementedError("stop-limit entry with its stop already through the close: TradingView's "
                                          "behaviour is not verified")
        self._e.orders[id] = Order(id, "entry", direction, stop, limit, oca=oca, placed_bar=self._e.i, comment=comment)

    def exit(self, id: str, from_entry: str, stop: int | None = None, limit: int | None = None,
             profit: int | None = None, loss: int | None = None, comment: str = "") -> None:
        """One bracket per id: placing it again amends it (Pine strategy.exit). One exit id per entry: Pine's
        quantity reservation across several exits of one entry is not emulated."""
        if any(o.kind == "exit" and o.from_entry == from_entry and o.id != id for o in self._e.orders.values()):
            raise NotImplementedError(f"a second strategy.exit for entry {from_entry!r} is not supported")
        self._e.orders[id] = Order(id, "exit", 0, stop, limit, from_entry, profit, loss, placed_bar=self._e.i,
                                   comment=comment, placed_in_position=self._e.pos is not None,
                                   abs_stop=stop, abs_limit=limit)

    def close_all(self, comment: str = "Close", immediately: bool = False) -> None:
        if self._e.pos is None:
            return
        if immediately:
            self._e.fill_exit(self._e.c[self._e.i], comment or "Close", "close", slip=True)
        else:
            self._e.orders["__close__"] = Order("__close__", "close", -self._e.pos.direction,
                                                placed_bar=self._e.i, comment=comment)

    def cancel(self, id: str) -> None:
        self._e.orders.pop(id, None)

    def cancel_all(self) -> None:
        self._e.orders.clear()


class Engine:
    def __init__(self, bars: Bars, props: Properties = DEFAULT):
        self.bars, self.props = bars, props
        self.o, self.h, self.l, self.c = bars.o, bars.h, bars.l, bars.c
        self.orders: dict[str, Order] = {}
        self.pos: Trade | None = None
        self.trades: list[Trade] = []
        self.i = 0
        self.ctx = Context(self)


    # --- fills -------------------------------------------------------------------------------------------
    def _slip(self, price: int, side: int) -> int:
        return price + side * self.props.slippage_ticks

    def _commission(self) -> float:
        return self.props.commission_per_order * self.props.qty

    def fill_entry(self, order: Order, price: int, slip: bool) -> None:
        if self.pos is not None:
            if self.pos.direction == order.side:
                self.orders.pop(order.id, None)  # pyramiding = 0: same-direction entry is ignored
                return
            self.fill_exit(price, order.id, "reverse", slip=slip, keep_entry=order.id)  # TV reverses
        px = self._slip(price, order.side) if slip else price
        self.pos = Trade(order.side, order.id, self.i, px, order.placed_bar, best=price, worst=price,
                         commission=self._commission(), qty=self.props.qty)
        for bracket in self.orders.values():
            if bracket.kind == "exit" and bracket.from_entry == order.id:
                self._resolve_one(bracket)
                if bracket.stop is not None:
                    risk = order.side * (px - bracket.stop)
                    self.pos.initial_risk_ticks = risk if risk > 0 else None
        self.orders.pop(order.id, None)
        if order.oca:
            for k in [k for k, o in self.orders.items() if o.kind == "entry" and o.oca == order.oca]:
                del self.orders[k]

    def fill_exit(self, price: int, exit_id: str, reason: str, slip: bool, keep_entry: str | None = None) -> None:
        t = self.pos
        self._mark(price)
        px = self._slip(price, -t.direction) if slip else price
        t.exit_id, t.exit_bar, t.exit_price, t.exit_reason = exit_id, self.i, px, reason
        t.commission += self._commission()
        t.profit = (px - t.entry_price) * t.direction * t.qty * TICK_VALUE - t.commission
        self.trades.append(t)
        self.pos = None
        for k in [k for k, o in self.orders.items()
                  if o.kind == "close" or (o.kind == "exit" and o.from_entry != keep_entry)]:
            del self.orders[k]

    def _working(self) -> list[Order]:
        """Orders that can fill right now (exits only for the open position's entry)."""
        out = []
        for o in self.orders.values():
            if o.kind == "entry":
                out.append(o)
            elif self.pos is not None and (o.kind == "close" or o.from_entry == self.pos.entry_id):
                if o.kind == "exit":
                    self._resolve_one(o)
                out.append(o)
        return out

    def _resolve_one(self, o: Order) -> None:
        """Turn profit/loss distances into prices from the actual entry fill. When a level is given both ways,
        the one price reaches first wins (Pine v6)."""
        t = self.pos
        d = o.side = -t.direction
        lim = [x for x in (o.abs_limit, None if o.profit is None else t.entry_price + t.direction * o.profit)
               if x is not None]
        stp = [x for x in (o.abs_stop, None if o.loss is None else t.entry_price - t.direction * o.loss)
               if x is not None]
        o.limit = (max(lim) if d == LONG else min(lim)) if lim else None  # buy-to-cover limit: higher is nearer
        o.stop = (min(stp) if d == LONG else max(stp)) if stp else None

    def _fill(self, o: Order, price: int, leg: str) -> None:
        slip = leg in ("market", "stop")
        if o.kind == "entry":
            self.fill_entry(o, price, slip)
        else:
            reason = "close" if o.kind == "close" else ("stop" if leg == "stop" else "limit")
            self.fill_exit(price, o.comment or o.id, reason, slip)

    # --- one bar -----------------------------------------------------------------------------------------
    def process_bar(self, i: int) -> None:
        self.i = i
        o, h, l, c = self.o[i], self.h[i], self.l[i], self.c[i]
        path = [o, l, h, c] if (h - o) >= (o - l) else [o, h, l, c]  # tie -> O-L-H-C
        prev_close = self.c[i - 1] if i > 0 else o
        self._at_open(o, prev_close)
        for a, b in zip(path[:-1], path[1:]):
            self._segment(a, b)

    def _at_open(self, o: int, prev_close: int) -> None:
        """Market orders, triggered stops and anything the open gaps through fill at the open."""
        changed = True
        while changed:
            changed = False
            for order in self._working():
                leg = self._open_leg(order, o, prev_close)
                if leg:
                    self._fill(order, o, leg)
                    changed = True
                    break
        self._mark(o)

    def _open_leg(self, order: Order, o: int, prev_close: int) -> str | None:
        if order.kind == "close" or (order.stop is None and order.limit is None):
            return "market"
        s = order.side
        if order.kind == "entry" and order.stop is not None and order.limit is not None:
            if not order.triggered and ((s == LONG and order.stop <= o) or (s == SHORT and order.stop >= o)):
                order.triggered = True  # the open gapped through the trigger: the limit works from the open
            if order.triggered and ((s == LONG and order.limit >= o) or (s == SHORT and order.limit <= o)):
                return "limit"
            return None
        if order.stop is not None:
            fresh = order.placed_bar == self.i - 1 and (order.kind == "entry" or order.placed_in_position)
            if (s == LONG and order.stop <= o) or (s == SHORT and order.stop >= o):
                return "stop"
            if fresh and ((s == LONG and order.stop <= prev_close) or (s == SHORT and order.stop >= prev_close)):
                return "stop"  # triggered when placed: fills at this open whatever the open is
        if order.limit is not None and ((s == LONG and order.limit >= o) or (s == SHORT and order.limit <= o)):
            return "limit"
        return None

    def _segment(self, a: int, b: int) -> None:
        """Fill orders in the order the price reaches them while moving from a to b."""
        up = b > a
        cur = a
        while True:
            best = None  # (distance, order, price, leg)
            for order in self._working():
                legs = (("stop", order.stop), ("limit", order.limit))
                if order.kind == "entry" and order.stop is not None and order.limit is not None:
                    legs = (("limit", order.limit),) if order.triggered else (("trigger", order.stop),)
                for leg, px in legs:
                    if px is None:
                        continue
                    s = order.side
                    hit = (leg in ("stop", "trigger") and ((s == LONG and up) or (s == SHORT and not up))) or \
                          (leg == "limit" and ((s == LONG and not up) or (s == SHORT and up)))
                    if not hit:
                        continue
                    if up and not (cur <= px <= b):
                        continue
                    if not up and not (b <= px <= cur):
                        continue
                    dist = abs(px - cur)
                    if best is None or dist < best[0]:
                        best = (dist, order, px, leg)
            if best is None:
                break
            _, order, px, leg = best
            self._mark(px)
            if leg == "trigger":
                order.triggered = True  # now a limit order; it fills here if the limit is already marketable
                cur = px
                s = order.side
                if (s == LONG and order.limit >= px) or (s == SHORT and order.limit <= px):
                    self._fill(order, px, "limit")
                    if self.pos is not None:
                        self._marketable_now(px)
                continue
            had_pos = self.pos is not None
            self._fill(order, px, leg)
            cur = px
            if self.pos is not None and not had_pos:
                self._marketable_now(px)
        self._mark(b)

    def _marketable_now(self, px: int) -> None:
        """Exits placed on the wrong side of a fresh fill fill at once at the fill point."""
        for order in self._working():
            if order.kind == "entry":
                continue
            s = order.side
            if order.stop is not None and ((s == LONG and order.stop <= px) or (s == SHORT and order.stop >= px)):
                self._fill(order, px, "stop")
                return
            if order.limit is not None and ((s == LONG and order.limit >= px) or (s == SHORT and order.limit <= px)):
                self._fill(order, px, "limit")
                return

    def _mark(self, px: int) -> None:
        t = self.pos
        if t is None:
            return
        if t.direction == LONG:
            t.best, t.worst = max(t.best, px), min(t.worst, px)
        else:
            t.best, t.worst = min(t.best, px), max(t.worst, px)


def run(strategy, bars: Bars, props: Properties = DEFAULT, start: int = 0) -> Result:
    """Run a strategy over the bars. The strategy is called only on bars where it asked to be (`prepare`
    returns a bool mask) or while it has a position or working orders, which TV-equivalent strategies allow
    when they are flat and idle outside their mask.

    `start` (feature 3 fold runs): indicators are still prepared over every bar, but the account starts flat and
    `on_bar` is first called on the first active bar at or after `start`."""
    e = Engine(bars, props)
    active = np.asarray(strategy.prepare(bars), dtype=bool)
    idx = np.flatnonzero(active)
    n = len(bars)
    k0 = int(np.searchsorted(idx, start))
    i = int(idx[k0]) if k0 < len(idx) else n
    while i < n:
        e.process_bar(i)
        strategy.on_bar(e.ctx, i)
        if e.pos is not None and bars.last_of_contract[i]:
            e.i = i
            e.fill_exit(e.c[i], "Roll", "roll", slip=True)
        if e.pos is not None or e.orders:
            i += 1
        else:
            k = np.searchsorted(idx, i + 1)
            i = int(idx[k]) if k < len(idx) else n
    return Result(e.trades, e.pos, bars, props, n - 1)
