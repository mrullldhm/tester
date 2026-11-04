"""Retired strategy. Only Fair Price Reversal and Tupa Trade are active.

Kept as an explicit rejection for old commands/configurations. Historical artifacts
outside data/ and web/ remain audit records, not runnable strategy definitions.
"""
from tvtester.strategy import Strategy


class SupertrendKalman(Strategy):
    name = "supertrend_kalman"

    def __init__(self, *args, **kwargs):
        raise ValueError("Supertrend Kalman is retired; use fair_price_reversal or tupa_trade")


STRATEGY = SupertrendKalman
