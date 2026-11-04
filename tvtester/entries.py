"""Pending limit-entry lifetime, evaluated at the one-minute bar close like the Pine twins.

The engine processes the candle before this check. An entry filled during that candle is
already a trade; TP expiry cancels only an entry that remains unfilled at the close.
"""
from dataclasses import dataclass

from .engine import LONG, Context
from .data import Bars


@dataclass
class PendingEntry:
    entry_id: str | None = None
    direction: int = 0
    target: int = 0
    closed: int = 0

    def place(self, entry_id: str, direction: int, target: int) -> None:
        self.entry_id, self.direction, self.target = entry_id, direction, target

    def waiting(self, ctx: Context, bars: Bars, i: int, in_session: bool) -> bool:
        if ctx.position_size or ctx.closed_trades != self.closed:
            self.entry_id = None  # includes entry and exit on the same candle
        self.closed = ctx.closed_trades
        if self.entry_id is None:
            return False
        reached = bars.h[i] >= self.target if self.direction == LONG else bars.l[i] <= self.target
        if reached or not in_session or bars.last_of_contract[i]:
            ctx.cancel(self.entry_id)
            ctx.cancel("Exit")
            self.entry_id = None
            return False
        return True
