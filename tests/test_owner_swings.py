"""The owner's swing contract applies to every strategy and research feature.

Run with unittest; this does not run the repository's pytest suite.
"""
import hashlib
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from strategies.fair_price_reversal import FairPriceReversal, GRID, SPACES
from tvtester.data import Bars
from tvtester.exits import ExitRule, levels, study_rules
from tvtester.strategy import Strategy
from tvtester.swings import minute_swing_series
from tvtester import ta


def make_bars(rows):
    a = np.asarray(rows, dtype=np.int64)
    n = len(a)
    ts = pd.date_range("2023-03-06 14:00", periods=n, freq="min", tz="UTC")
    return Bars(ts, ts.as_unit("ms").asi8, *a.T, np.ones(n), np.full(n, "CLJ3"), np.zeros(n, bool))


class OwnerSwingContract(unittest.TestCase):
    def test_active_pine_twins_keep_fixed_minute_swings(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("fair_price_reversal", "tupa_trade"):
            source = (root / "strategies" / f"{name}.pine").read_text()
            self.assertIn("timeframe.isminutes and timeframe.multiplier == 1", source)
            self.assertNotIn("ta.pivotlow(", source)
            self.assertNotIn("ta.pivothigh(", source)
            self.assertNotIn("swingInput", source)

    def test_authoritative_indicator_is_unchanged(self):
        source = Path(__file__).resolve().parents[1] / "indicators/structure_swings.pine"
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         "77692c498f0d7f76bb91108840956563f8f4df71d40f7ad0769b5eda530745f5")

    def test_left_equal_right_strict_and_confirmation(self):
        bars = make_bars([(9, 10, 5, 8), (10, 12, 6, 11), (10, 12, 7, 11), (9, 11, 8, 10)])
        s = minute_swing_series(bars)
        self.assertTrue(np.isnan(s["high"][:3]).all())
        self.assertEqual(s["high"][3], 12)
        self.assertTrue(np.isnan(s["last_high"][:3]).all())
        self.assertEqual(s["last_high"][3], 12)

    def test_outside_candle_path_changes_alternation(self):
        # Existing high 12. Outside high 11 is dropped if high-first; low-first
        # establishes the opposite swing before accepting that lower high.
        rows = [(8, 10, 5, 8), (10, 12, 6, 10), (8, 10, 7, 8), (5, 11, 4, 8), (8, 10, 6, 8)]
        low_first = minute_swing_series(make_bars(rows))
        self.assertEqual(low_first["high"][4], 11)
        self.assertEqual(low_first["prev_high"][4], 12)
        rows[3] = (10, 11, 4, 8)
        high_first = minute_swing_series(make_bars(rows))
        self.assertTrue(np.isnan(high_first["high"][4]))
        self.assertEqual(high_first["last_high"][4], 12)
        self.assertEqual(high_first["last_low"][4], 4)

    def test_swing_exit_reuses_owner_state(self):
        bars = make_bars([(100, 100, 100, 100), (100, 105, 95, 100), (100, 104, 98, 102)])
        owner = minute_swing_series(bars)
        trailing = levels(bars, ExitRule(trail="swing"))
        np.testing.assert_equal(trailing["pl"], owner["last_low"])
        np.testing.assert_equal(trailing["ph"], owner["last_high"])

    def test_alternative_settings_are_rejected(self):
        for strength in (0, 2, 3, 5):
            with self.subTest(strength=strength):
                with self.assertRaises(ValueError):
                    FairPriceReversal(swing=strength)
                with self.assertRaises(ValueError):
                    Strategy(swing=strength)
        for setting in (1, 2, 3, 5):
            with self.assertRaises(ValueError):
                ExitRule(trail="swing", trail_x=setting)
        with self.assertRaises(ValueError):
            ta.buffer_pivots(np.array([1, 2, 1]), 1, True)
        self.assertEqual(GRID["swing"], [1])
        self.assertEqual(SPACES["full"]["params"]["swing"], [1])
        self.assertTrue(all(r.trail_x == 0 for r in study_rules() if r.trail == "swing"))


if __name__ == "__main__":
    unittest.main()
