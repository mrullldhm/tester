"""purple_pa / purple_levels: a contract roll inside a setup never supplies the gap (Codex review 2026-11-16)."""

import numpy as np
import pandas as pd
import pytest

from cltester.data import add_session
from cltester.strategy import load


def _bars(new_contract_after_roll: bool) -> pd.DataFrame:
    """Previous trading day low 70.00; today arms above it, touches it at 17:50 CT (before 00:00 UTC = 18:00 CST),
    then from 18:00 CT trades about $1 higher: on a new contract (roll) or the same one (a real move)."""
    rows = []
    for ts in pd.date_range("2024-12-10 08:00", "2024-12-10 08:59", freq="min", tz="America/Chicago"):
        rows.append((ts, "CLF5", 70.50, 70.60, 70.00 if ts.minute == 30 else 70.40, 70.50))
    for ts in pd.date_range("2024-12-10 17:00", "2024-12-10 19:59", freq="min", tz="America/Chicago"):
        sym = "CLF5"
        if ts.hour == 17 and 50 <= ts.minute <= 54:
            o, h, l, c = 70.20, 70.25, 70.00, 70.10  # the touch candle
        elif ts.hour == 17:
            o, h, l, c = 70.30, 70.35, 70.25, 70.30  # wholly above the level: armed
        else:
            sym = "CLG5" if new_contract_after_roll else "CLF5"
            o, h, l, c = 71.00, 71.05, 70.95, 71.00
        rows.append((ts, sym, o, h, l, c))
    df = pd.DataFrame(rows, columns=["ts", "raw_symbol", "open", "high", "low", "close"])
    df["ts"] = df["ts"].dt.tz_convert("UTC")
    df["volume"], df["vendor"] = 1, "test"
    return add_session(df)


@pytest.mark.parametrize("name,extra", [("purple_pa", {}), ("purple_levels", {"levels": "pd"})])
def test_gap_across_a_roll_is_refused_and_the_same_move_on_one_contract_is_not(name, extra):
    s = load(name)
    p = {**s.PARAMS, "tf": "5m", **extra}
    same = s.signals(_bars(False), p)
    rolled = s.signals(_bars(True), p)
    assert len(same) == 1 and same["side"].iat[0] == 1  # control: a real departure on one contract trades
    assert rolled.empty
    assert np.isclose(same["stop"].iat[0], 69.99)


def _bars_touch_after_roll() -> pd.DataFrame:
    """Previous day low 70.00. Today the old contract trades 70.30 until 17:59 CT; the roll comes at 18:00 CT (00:00
    UTC) and the first new-contract candle touches 70.00. The candle after it only drifts, the next one gaps up: a
    setup wholly on the new contract."""
    rows = []
    for ts in pd.date_range("2024-12-10 08:00", "2024-12-10 08:59", freq="min", tz="America/Chicago"):
        rows.append((ts, "CLF5", 70.50, 70.60, 70.00 if ts.minute == 30 else 70.40, 70.50))
    for ts in pd.date_range("2024-12-10 17:00", "2024-12-10 18:59", freq="min", tz="America/Chicago"):
        if ts.hour == 17:
            sym, (o, h, l, c) = "CLF5", (70.30, 70.35, 70.25, 70.30)  # old contract, wholly above: armed
        elif ts.minute < 5:
            sym, (o, h, l, c) = "CLG5", (70.03, 70.05, 70.00, 70.02)  # touch: first new-contract candle
        elif ts.minute < 10:
            sym, (o, h, l, c) = "CLG5", (70.04, 70.08, 70.02, 70.06)  # no gap yet
        else:
            sym, (o, h, l, c) = "CLG5", (70.30, 70.35, 70.20, 70.30)  # high[touch] 70.05 < low 70.20: gap
        rows.append((ts, sym, o, h, l, c))
    df = pd.DataFrame(rows, columns=["ts", "raw_symbol", "open", "high", "low", "close"])
    df["ts"] = df["ts"].dt.tz_convert("UTC")
    df["volume"], df["vendor"] = 1, "test"
    return add_session(df)


@pytest.mark.parametrize("name,extra", [("purple_pa", {}), ("purple_levels", {"levels": "pd"})])
def test_touch_right_after_a_roll_can_still_trade_a_later_gap(name, extra):
    s = load(name)
    sig = s.signals(_bars_touch_after_roll(), {**s.PARAMS, "tf": "5m", **extra})
    assert len(sig) == 1 and sig["side"].iat[0] == 1
    assert np.isclose(sig["limit"].iat[0], 70.20) and np.isclose(sig["stop"].iat[0], 69.99)
