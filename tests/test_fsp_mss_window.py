"""Frozen 15m entry-eligibility boundary; broker fixtures do not define alternative swing detection."""
import unittest

import numpy as np
import pandas as pd

from strategies.failed_swing_point import Setup, confirmation_window_hit
from tests.test_fsp_daily import OriginalLifecycle, make
from tvtester import swings as sw
from tvtester.engine import LONG, SHORT, run


class MSSWindowContract(unittest.TestCase):
    def fixture(self, side=SHORT):
        b = make(pd.date_range("2023-01-03 09:00", periods=31, freq="min"), high=110, low=90)
        b.h[15:30] = 120  # the next 15m candle must not move the original boundary
        candles = sw.candles(b, "15m")
        setup = Setup(0, side, 95, 0, 2, 14, confirmation_candle=0, confirmation_end=14)
        return setup, candles

    def test_range_is_unknown_until_confirmation_and_own_high_is_not_invalidation(self):
        s, c = self.fixture()
        self.assertFalse(confirmation_window_hit(s, 13, 999, 1, c))
        self.assertIsNone(s.confirmation_high)
        self.assertFalse(confirmation_window_hit(s, 14, 110, 90, c))
        self.assertEqual((s.confirmation_high, s.confirmation_low), (110, 90))

    def test_short_equal_touch_uses_original_fixed_high(self):
        s, c = self.fixture()
        self.assertFalse(confirmation_window_hit(s, 15, 109, 91, c))
        self.assertTrue(confirmation_window_hit(s, 16, 110, 91, c))
        self.assertEqual(s.confirmation_high, 110)

    def test_long_equal_touch_uses_original_fixed_low(self):
        s, c = self.fixture(LONG)
        self.assertFalse(confirmation_window_hit(s, 15, 109, 91, c))
        self.assertTrue(confirmation_window_hit(s, 16, 109, 90, c))

    def test_late_confirmation_checks_the_first_post_candle_minute(self):
        s, c = self.fixture()
        s.ready = 15  # missing final minute: source close is known on the next bar
        self.assertTrue(confirmation_window_hit(s, 15, 110, 91, c))

    def test_placed_limit_is_not_cancelled_by_later_setup_invalidation(self):
        class WaitingLimit(OriginalLifecycle):
            pending_order = True

            def prepare(self, b):
                active = super().prepare(b)
                self.setups[0].end = 1
                self.setups[0].reason = "confirmation_high_touch"
                return active

        b = make(pd.date_range("2023-01-03 08:59", periods=3, freq="min"))
        b.h[2] = 115  # reaches the sell limit after the setup's MSS eligibility ended
        result = run(WaitingLimit(), b)
        self.assertIsNotNone(result.open_trade)
        self.assertEqual(result.open_trade.entry_price, 110)

    def test_gap_after_mss_obeys_limit_fill_and_stop_not_old_cancellation(self):
        class GapLimit(OriginalLifecycle):
            pending_order = True

        b = make(pd.date_range("2023-01-03 08:59", periods=3, freq="min"))
        b.o[2] = b.h[2] = b.l[2] = b.c[2] = 125
        result = run(GapLimit(), b)
        self.assertEqual(len(result.trades), 1)
        self.assertEqual((result.trades[0].entry_price, result.trades[0].exit_price), (125, 125))


if __name__ == "__main__":
    unittest.main()
