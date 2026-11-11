"""Owner's 10 November touch-removal rule. Run directly with unittest, never pytest implicitly."""
import unittest

import numpy as np
import pandas as pd

from tvtester.data import Bars
from tvtester import swings as sw


def make(rows, freq="min"):
    a = np.asarray(rows, dtype=np.int64)
    ts = pd.date_range("2026-11-10", periods=len(a), freq=freq, tz="UTC")
    return Bars(ts, ts.as_unit("ms").asi8, *a.T, np.ones(len(a)),
                np.full(len(a), "CLZ6"), np.zeros(len(a), dtype=bool))


class TouchRemoval(unittest.TestCase):
    def test_equal_touch_removes_both_sides_without_a_new_pivot(self):
        for t, p, h, l in ((sw.SL, 50, 80, 50), (sw.SH, 100, 100, 70)):
            with self.subTest(side=t):
                z = sw.Zig()
                z.push(t, p, 1)
                self.assertTrue(z.invalidate(h, l))
                self.assertEqual(z.candidate_type, 0)
                self.assertIsNone(z.cur_l if t == sw.SL else z.cur_h)
                self.assertFalse(z.invalidate(h, l))

    def test_only_provisional_endpoint_removed_and_labels_restore(self):
        z = sw.Zig()
        z.push(sw.SL, 50, 0)
        z.push(sw.SH, 100, 1)
        z.push(sw.SL, 70, 2)
        self.assertTrue(z.low_is_hl)
        self.assertTrue(z.invalidate(90, 70))
        self.assertEqual((z.cur_h, z.cur_l, z.prev_l), (100, 50, None))
        self.assertEqual(z.candidate_type, 0)
        # The surviving high is fixed, not made provisional again by removal of the low.
        self.assertFalse(z.invalidate(100, 60))
        self.assertTrue(z.push(sw.SL, 60, 3))
        self.assertEqual(z.prev_l, 50)
        self.assertTrue(z.low_is_hl)

    def test_replaced_candidate_does_not_reappear_on_removal(self):
        z = sw.Zig()
        z.push(sw.SL, 50, 0)
        z.push(sw.SL, 40, 1)
        self.assertTrue(z.invalidate(80, 40))
        self.assertIsNone(z.cur_l)

    def test_opposite_swing_protects_preceding_endpoint(self):
        z = sw.Zig()
        z.push(sw.SL, 50, 0)
        z.push(sw.SH, 100, 1)
        self.assertFalse(z.invalidate(90, 40))
        self.assertEqual(z.cur_l, 50)

    def test_removal_is_a_state_event_not_a_pivot_signal(self):
        # Low 50 confirms at bar 2. Bar 4 touches it while still descending: no new low pivot.
        b = make([(100, 120, 90, 100), (90, 110, 50, 60), (60, 100, 60, 90),
                  (80, 90, 70, 80), (80, 85, 50, 60)])
        m = sw.minute_swings(b)
        self.assertEqual(m.bar.tolist(), [2, 4])
        self.assertEqual(m.last_type.tolist(), [sw.SL, 0])
        s = sw.minute_swing_series(b)
        self.assertEqual(s["last_low"][3], 50)
        self.assertTrue(np.isnan(s["last_low"][4]))
        self.assertTrue(np.isnan(s["low"][4]))

    def test_unqualified_opposite_does_not_rescue_removed_endpoint(self):
        z = sw.Zig()
        z.push(sw.SL, 50, 0)
        z.visit(sw.SH, 110, 1, False)
        z.push(sw.SH, 110, 2)
        z.push(sw.SL, 70, 3)
        z.invalidate(100, 70)
        # Removed low cannot reset the leg boundary to permit a smaller high.
        self.assertFalse(z.visit(sw.SH, 100, 4, True))

    def test_opposite_confirmation_secures_high_before_equal_touch(self):
        rows = [(100, 110, 90, 100), (90, 105, 50, 60), (60, 100, 60, 90),
                (90, 110, 80, 100), (100, 105, 70, 90), (90, 105, 80, 100),
                (100, 112, 95, 105), (105, 109, 90, 105), (105, 112, 94, 110)]
        for mirror in (False, True):
            values = [(-o, -l, -h, -c) for o, h, l, c in rows] if mirror else rows
            b = make(values)
            m = sw.minute_swings(b)
            e = m.at[-1]
            if mirror:
                self.assertEqual((m.cur_l[e], m.cur_h[e], m.prev_h[e]), (-112, -90, -70))
            else:
                self.assertEqual((m.cur_h[e], m.cur_l[e], m.prev_l[e]), (112, 90, 70))

    def test_forming_htf_removal_can_be_secured_at_right_close_without_backdating(self):
        candles = [(100, 110, 90, 100), (90, 105, 50, 60), (60, 100, 60, 90),
                   (90, 110, 80, 100), (100, 105, 70, 90), (90, 105, 80, 100),
                   (100, 112, 95, 105), (105, 109, 90, 105), (105, 112, 94, 110)]
        rows = [row for row in candles for _ in range(5)]
        b = make(rows)
        st = sw.timeframe_state(b, "5m")
        at = st.at_bars(len(b))
        self.assertEqual(st.last_type[at[40]], 0)  # early live touch removes high, low not yet known
        self.assertEqual((st.cur_h[at[44]], st.cur_l[at[44]]), (112, 90))
        self.assertEqual(st.last_type[at[44]], sw.SL)
        partial = sw.timeframe_state(make(rows[:41]), "5m")
        self.assertEqual(partial.last_type[partial.at_bars(41)[40]], 0)

    def test_higher_timeframe_removes_during_incomplete_candle_and_is_causal(self):
        # Three complete 5m candles confirm low 50; the next forming 5m candle touches it.
        rows = ([(100, 120, 90, 100)] * 5 + [(90, 110, 50, 60)] * 5
                + [(60, 100, 60, 90)] * 5 + [(80, 90, 70, 80), (70, 85, 50, 60)])
        b = make(rows)
        full = sw.timeframe_state(b, "5m")
        at = full.at_bars(len(b))
        self.assertEqual(full.last_type[at[14]], sw.SL)
        self.assertEqual(full.last_type[at[15]], sw.SL)
        self.assertEqual(full.last_type[at[16]], 0)
        self.assertEqual(full.cur_l[at[16]], sw.NONE)
        for n in (15, 16, 17):
            prefix = make(rows[:n])
            partial = sw.timeframe_state(prefix, "5m")
            pa = partial.at_bars(n)
            for name in ("last_type", "cur_h", "cur_l", "trend"):
                np.testing.assert_array_equal(getattr(partial, name)[pa[14:]],
                                              getattr(full, name)[at[14:n]])


if __name__ == "__main__":
    unittest.main()
