"""Tester settings: the TradingView strategy() properties used for every run."""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYMBOL = "CL1!"  # NYMEX Light Crude Oil, front month. The only market this repo trades.
TICK = 0.01  # price per tick
TICK_VALUE = 10.0  # $ per tick per contract (1,000 bbl)
POINT_VALUE = TICK_VALUE / TICK  # $ per 1.00 price move


@dataclass(frozen=True)
class Properties:
    """Mirror of the TradingView strategy() properties tab."""

    initial_capital: float = 50_000.0
    qty: int = 1  # default_qty_type = fixed, contracts
    commission_per_order: float = 2.01  # cash per contract per order = $4.02 round trip
    slippage_ticks: int = 0  # market and stop fills only, as in TradingView
    risk_free_rate: float = 0.02  # TradingView Sharpe / Sortino use 2% a year

    def with_slippage(self, ticks: int) -> "Properties":
        return Properties(self.initial_capital, self.qty, self.commission_per_order, ticks, self.risk_free_rate)


DEFAULT = Properties()
SLIPPAGE_SCENARIOS = (1, 2)  # ticks per market/stop fill, reported separately from the 0-tick baseline
