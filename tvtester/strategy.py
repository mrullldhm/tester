"""Base class for strategies.

A strategy is the Python twin of a Pine `strategy()` script:
- `prepare(bars)` runs once. Compute every indicator over the full bar sequence here (Pine runs the script on
  every bar, so state must never depend on which bars `on_bar` sees). Return a bool mask of the bars where
  `on_bar` must run while the strategy is flat with no working orders.
- `on_bar(ctx, i)` runs at the close of bar i (and on every bar while a position or order exists).
  Use ctx.entry / ctx.exit / ctx.close_all / ctx.cancel like strategy.entry / exit / close_all / cancel.
- `filters` (feature 2): entry vetoes checked at the signal bar, in `on_bar` (docs/OPTIMIZE.md). A strategy that
  takes filters exposes its feature values; with no filters it is the plain strategy.
"""

import numpy as np

from .data import Bars
from .features import Filter, as_filter
from .engine import Context


class Strategy:
    name = "strategy"

    def __init__(self, filters=(), **params):
        self.params = params
        self.filters: tuple[Filter, ...] = tuple(as_filter(f) for f in filters)

    def prepare(self, bars: Bars) -> np.ndarray:
        raise NotImplementedError

    def on_bar(self, ctx: Context, i: int) -> None:
        raise NotImplementedError

    def features(self, bars: Bars) -> dict[str, np.ndarray]:
        """Feature values per bar (after `prepare`), for filters and the association report."""
        return {}

    def label(self) -> str:
        out = ", ".join(f"{k}={v}" for k, v in self.params.items())
        return out + "".join(f", filter {f}" for f in self.filters)
