import pandas as pd

from cltester.metrics import realized_equity, summary


def test_drawdown_follows_exit_order_when_trades_overlap():
    # signal order +995.96, -204.04, -204.04; exits: second (bar 5), first (bar 8), third (bar 9)
    t = pd.DataFrame({"trading_day": ["2024-03-05"] * 3, "net": [995.96, -204.04, -204.04], "exit_bar": [8, 5, 9],
                      "gross": 0.0, "fee": 0.0, "reason": "stop"})
    assert list(realized_equity(t).round(2)) == [-204.04, 791.92, 587.88]
    assert summary(t, [pd.Timestamp("2024-03-05")])["max_drawdown"] == -204.04


def test_trades_exiting_on_one_bar_are_booked_together():
    t = pd.DataFrame({"net": [-300.0, 500.0], "exit_bar": [7, 7]})
    assert list(realized_equity(t)) == [200.0]
