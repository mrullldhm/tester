"""Focused unittest checks for FSP. No pytest runner is required."""
import unittest

import numpy as np
import pandas as pd

from strategies.failed_swing_point import FailedSwingPoint, stop_anchor
from tvtester.data import Bars
from tvtester.engine import LONG, SHORT, run


def bars(rows, start="2023-01-03 00:00"):
    a = np.asarray(rows, dtype=np.int64)
    ts = pd.date_range(start, periods=len(a), freq="min", tz="UTC")
    return Bars(ts, ts.as_unit("ms").asi8, *a.T, np.ones(len(a)),
                np.full(len(a), "CLG3"), np.zeros(len(a), dtype=bool))


class SingleOrder:
    def __init__(self, side=SHORT, limit=100, cancel=110, stop=None, change=None):
        self.side, self.limit, self.cancel, self.stop, self.change = side, limit, cancel, stop, change

    def prepare(self, b):
        return np.ones(len(b), dtype=bool)

    def before_bar(self, ctx, i):
        if i == 1 and self.change is not None:
            ctx.entry_cancel_touch("entry", self.change)

    def on_bar(self, ctx, i):
        if i == 0:
            ctx.entry("entry", self.side, limit=self.limit, cancel_touch=self.cancel)
            if self.stop is not None:
                ctx.exit("exit", "entry", stop=self.stop, profit=25)


class FSPContract(unittest.TestCase):
    def test_equal_touch_cancels_unfilled_short_before_later_fill(self):
        b = bars([(90, 90, 90, 90), (90, 100, 85, 90), (90, 115, 85, 110)])
        res = run(SingleOrder(limit=110, cancel=100), b)
        self.assertIsNone(res.open_trade)
        self.assertEqual(res.trades, [])

    def test_equal_touch_cancels_long_mirror(self):
        b = bars([(110, 110, 110, 110), (110, 115, 100, 110), (110, 115, 85, 90)])
        res = run(SingleOrder(side=LONG, limit=90, cancel=100), b)
        self.assertIsNone(res.open_trade)
        self.assertEqual(res.trades, [])

    def test_cancel_wins_when_gap_crosses_limit_and_cancellation(self):
        b = bars([(90, 90, 90, 90), (115, 120, 95, 100)])
        res = run(SingleOrder(), b)
        self.assertIsNone(res.open_trade)

    def test_fill_before_cancellation_remains_a_trade_and_uses_stop(self):
        b = bars([(90, 90, 90, 90), (95, 115, 90, 100)])
        res = run(SingleOrder(stop=105), b)
        self.assertEqual(len(res.trades), 1)
        t = res.trades[0]
        self.assertEqual((t.entry_price, t.exit_price, t.exit_reason), (100, 105, "stop"))
        self.assertAlmostEqual(t.profit, -54.02)

    def test_cancellation_updates_before_open_without_repricing_entry(self):
        b = bars([(90, 90, 90, 90), (105, 110, 95, 100)])
        res = run(SingleOrder(cancel=120, change=105), b)
        self.assertIsNone(res.open_trade)

    def test_optional_cancellation_preserves_existing_limit_semantics(self):
        b = bars([(90, 90, 90, 90), (115, 120, 100, 110)])
        res = run(SingleOrder(cancel=None), b)
        self.assertEqual(res.open_trade.entry_price, 115)
        self.assertEqual(res.open_trade.signal_bar, 0)

    def test_tp_uses_actual_gap_fill(self):
        b = bars([(90, 90, 90, 90), (110, 112, 80, 90)])
        res = run(SingleOrder(stop=120, cancel=130), b)
        self.assertEqual((res.trades[0].entry_price, res.trades[0].exit_price), (110, 85))
        self.assertAlmostEqual(res.trades[0].profit, 245.98)

    def test_stop_is_price_anchor_without_right_confirmation(self):
        b = bars([(100, 105, 95, 100), (98, 100, 90, 99), (99, 103, 97, 102), (102, 108, 89, 90)])
        # The highest post-HL price is on the signal candle; no right candle exists.
        self.assertEqual(stop_anchor(b, 1, 3, SHORT), (3, 108))
        mirrored = bars([(-o, -l, -h, -c) for o, h, l, c in zip(b.o, b.h, b.l, b.c)])
        self.assertEqual(stop_anchor(mirrored, 1, 3, LONG), (3, -108))

    def test_default_parameters_are_fixed(self):
        s = FailedSwingPoint()
        self.assertEqual(s.params, {"setup_tf": "1h", "confirmation": "15m", "max_risk": 25, "tp": 50, "session": "ny"})
        with self.assertRaises(ValueError):
            FailedSwingPoint(max_risk=30)


if __name__ == "__main__":
    unittest.main()
