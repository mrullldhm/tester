"""Lifecycle and clock checks; manually scheduled orders test execution, not swing qualification."""
from datetime import date
import unittest

import numpy as np
import pandas as pd

from strategies.failed_swing_point import FailedSwingPoint, Setup, Signal
from tvtester.data import Bars
from tvtester.engine import LONG, SHORT, run
from tvtester.fsp_clock import cl_daily_close_minutes, trading_clock


def make(times, high=101, low=99):
    ts = pd.DatetimeIndex(times)
    if ts.tz is None:
        ts = ts.tz_localize("America/New_York")
    ts = ts.tz_convert("UTC")
    n = len(ts)
    return Bars(ts, ts.as_unit("ms").asi8, np.full(n, 100), np.full(n, high),
                np.full(n, low), np.full(n, 100), np.ones(n), np.full(n, "CLG3"), np.zeros(n, bool))


class LifecycleMixin:
    """Inject an execution-only order into the real owner-prepared lifecycle."""
    pending_order = False
    stale_next_day = False

    def prepare(self, b):
        super().prepare(b)  # use the real detector; no alternative pivots
        direction = SHORT if self.pending_order else LONG
        limit = 110 if self.pending_order else 100
        stop = 120 if self.pending_order else 90
        setup = Setup(0, direction, 95, 0, 0, -1)
        self.setups = [setup]
        self.signals = {0: [Signal(0, 0, direction, 0, 95, 0, stop, limit)]}
        if self.stale_next_day:
            for i in range(1, len(b)):
                if self.clock.signal_window[i] and self.clock.day[i] != self.clock.day[0]:
                    self.signals[i] = [Signal(i, 0, direction, 0, 95, 0, stop, limit)]
                    break
        return np.ones(len(b), dtype=bool)


class OriginalLifecycle(LifecycleMixin, FailedSwingPoint):
    pass


class FSPDailyContract(unittest.TestCase):
    def test_first_signal_cannot_retry_after_tp_or_sl_in_either_direction(self):
        class ReplayedSetup(OriginalLifecycle):
            def prepare(self, b):
                active = super().prepare(b)
                self.setups[0].first_signal = 0
                first = self.signals[0][0]
                self.signals[2] = [Signal(2, 0, first.direction, 1, 95, 1, first.stop, first.limit)]
                return active

        for short in (False, True):
            for tp in (False, True):
                with self.subTest(short=short, tp=tp):
                    s = ReplayedSetup()
                    s.pending_order = short
                    b = make(pd.date_range("2023-01-03 08:59", periods=5, freq="min"))
                    if short:
                        b.h[1], b.l[1] = (111, 60) if tp else (120, 99)
                        b.h[3] = 111
                    else:
                        b.h[1], b.l[1] = (150, 99) if tp else (101, 90)
                    r = run(s, b)
                    self.assertEqual(len(r.trades), 1)
                    self.assertIsNone(r.open_trade)
                    self.assertEqual(sum(a[1] == "place" for a in s.actions), 1)
                    self.assertEqual(s.attempted_setups, {0})

    def test_cancelled_first_limit_cannot_be_replaced(self):
        class CancelledSetup(OriginalLifecycle):
            pending_order = True

            def prepare(self, b):
                active = super().prepare(b)
                self.setups[0].first_signal = 0
                self.signals[2] = [Signal(2, 0, SHORT, 1, 95, 1, 120, 110)]
                return active

            def on_bar(self, ctx, i):
                if i == 1:
                    self._cancel(ctx, i, "execution_fixture_cancel")
                super().on_bar(ctx, i)

        s = CancelledSetup()
        b = make(pd.date_range("2023-01-03 08:59", periods=4, freq="min"))
        b.h[3] = 115
        r = run(s, b)
        self.assertEqual(r.trades, [])
        self.assertIsNone(r.open_trade)
        self.assertEqual(sum(a[1] == "place" for a in s.actions), 1)

    def test_busy_first_opportunity_cannot_be_deferred_to_later_signal(self):
        class BusySetup(OriginalLifecycle):
            def prepare(self, b):
                active = super().prepare(b)
                self.setups[0].first_signal = 0
                self.setups.append(Setup(1, LONG, 95, 0, 0, -1, first_signal=2))
                self.signals[2] = [Signal(2, 1, LONG, 1, 95, 1, 90, 100)]
                self.signals[4] = [Signal(4, 1, LONG, 3, 95, 3, 90, 100)]
                return active

        s = BusySetup()
        b = make(pd.date_range("2023-01-03 08:59", periods=6, freq="min"))
        b.h[3] = 150
        r = run(s, b)
        self.assertEqual(len(r.trades), 1)
        self.assertIsNone(r.open_trade)
        self.assertEqual(s.attempted_setups, {0})

    def test_new_york_flat_at_same_close(self):
        b = make(pd.date_range("2023-01-03 08:59", "2023-01-03 16:59", freq="min"))
        at = b.ts.get_loc(pd.Timestamp("2023-01-03 14:29", tz="America/New_York").tz_convert("UTC"))
        b.c[at], b.h[at], b.l[at] = 103, 104, 99
        for cls in (OriginalLifecycle,):
            with self.subTest(variant=cls.__name__):
                result = run(cls(), b)
                self.assertIsNone(result.open_trade)
                self.assertEqual(len(result.trades), 1)
                t = result.trades[0]
                self.assertEqual((t.entry_bar, t.exit_bar, t.exit_price, t.exit_reason), (1, at, 103, "close"))
                self.assertEqual(t.exit_id, "New York close")

    def test_pending_limit_cannot_fill_outside_new_york(self):
        b = make(pd.date_range("2023-01-03 08:59", "2023-01-03 14:31", freq="min"))
        at = b.ts.get_loc(pd.Timestamp("2023-01-03 14:30", tz="America/New_York").tz_convert("UTC"))
        b.h[at:] = 115  # would fill the waiting sell limit if it survived the NY cutoff
        for cls in (OriginalLifecycle,):
            s = cls()
            s.pending_order = True
            result = run(s, b)
            self.assertEqual(result.trades, [])
            self.assertIsNone(result.open_trade)
            self.assertIsNone(s.pending)
            self.assertTrue(any(a[1] == "cancel" and a[3] == "session_close" for a in s.actions))

    def test_used_setup_cannot_rearm_next_day(self):
        first = pd.date_range("2023-01-03 08:59", "2023-01-03 16:59", freq="min")
        second = pd.date_range("2023-01-04 08:59", "2023-01-04 09:02", freq="min")
        for cls in (OriginalLifecycle,):
            s = cls()
            s.stale_next_day = True
            r = run(s, make(first.append(second)))
            self.assertEqual(len(r.trades), 1)
            self.assertIsNone(r.open_trade)
            self.assertEqual(sum(a[1] == "place" for a in s.actions), 1)

    def test_halt_exit_uses_first_reopening_open_before_brackets_in_both_directions(self):
        first = pd.date_range("2023-01-03 08:59", "2023-01-03 14:28", freq="min")
        times = first.append(pd.DatetimeIndex([pd.Timestamp("2023-01-03 15:15")]))
        for short in (False, True):
            with self.subTest(short=short):
                b = make(times)
                s = OriginalLifecycle()
                s.pending_order = short
                if short:
                    b.h[1] = 111
                b.o[-1] = 115 if short else 105
                b.h[-1], b.l[-1], b.c[-1] = 160, 50, 120
                r = run(s, b)
                self.assertIsNone(r.open_trade)
                self.assertEqual(len(r.trades), 1)
                t = r.trades[0]
                self.assertEqual((t.exit_bar, t.exit_price, t.exit_reason, t.exit_id),
                                 (len(b)-1, int(b.o[-1]), "close", "New York halt reopen"))
                self.assertAlmostEqual(t.commission, 4.02)
                # Reopening intrabar extremes happen after the market close and cannot affect exposure.
                self.assertNotIn(160, (t.best, t.worst))
                self.assertNotIn(50, (t.best, t.worst))

    def test_old_limit_cannot_fill_when_halt_reopens_during_next_ny_session(self):
        first = pd.date_range("2023-01-03 08:59", "2023-01-03 14:28", freq="min")
        times = first.append(pd.DatetimeIndex([pd.Timestamp("2023-01-04 09:00")]))
        b = make(times)
        b.h[-1] = 115
        s = OriginalLifecycle()
        s.pending_order = True
        r = run(s, b)
        self.assertEqual(r.trades, [])
        self.assertIsNone(s.pending)

    def test_tp_is_fifty_from_actual_fill(self):
        b = make(pd.date_range("2023-01-03 08:59", "2023-01-03 09:01", freq="min"))
        b.h[1] = 150
        r = run(OriginalLifecycle(), b)
        self.assertEqual((r.trades[0].entry_price, r.trades[0].exit_price), (100, 150))
        self.assertAlmostEqual(r.trades[0].profit, 495.98)

    def test_clock_handles_dst_and_exact_session_boundaries(self):
        times = pd.DatetimeIndex(["2023-03-10 13:59Z", "2023-03-10 14:00Z", "2023-03-10 19:30Z",
                                  "2023-03-13 12:59Z", "2023-03-13 13:00Z", "2023-03-13 18:30Z"])
        clock = trading_clock(make(times))
        self.assertEqual(clock.fill_window.tolist(), [False, True, False, False, True, False])
        self.assertEqual(clock.signal_window.tolist(), [True, True, False, True, True, False])

    def test_early_close_and_historical_cutoff_are_scheduled(self):
        self.assertEqual(cl_daily_close_minutes(date(2023, 11, 24)), 13 * 60 + 45)
        self.assertEqual(cl_daily_close_minutes(date(2013, 1, 3)), 17 * 60 + 15)
        self.assertEqual(cl_daily_close_minutes(date(2023, 1, 3)), 17 * 60)
        self.assertIsNone(cl_daily_close_minutes(date(2023, 12, 25)))
        clock = trading_clock(make(pd.date_range("2023-11-24 13:43", periods=3, freq="min")))
        self.assertEqual(clock.session_close.tolist(), [False, True, False])
        self.assertEqual(clock.signal_window.tolist(), [True, False, False])

    def test_ny_reset_deadline_in_both_dst_seasons(self):
        times = pd.DatetimeIndex(["2023-03-10 19:29Z", "2023-03-10 19:30Z",
                                  "2023-03-13 18:29Z", "2023-03-13 18:30Z"])
        b = make(times)
        clock = trading_clock(b)
        self.assertEqual(clock.session_close.tolist(), [True, False, True, False])
        self.assertEqual(clock.deadline.tolist(), [int(t.value // 1_000_000) for t in
            pd.DatetimeIndex(["2023-03-10 19:30Z", "2023-03-13 18:30Z",
                              "2023-03-13 18:30Z", "2023-03-14 18:30Z"])])

    def test_fresh_after_close_setup_belongs_to_next_session_without_evening_reset(self):
        b = make(pd.DatetimeIndex(["2023-01-03 14:29", "2023-01-03 14:30",
                                   "2023-01-03 15:00", "2023-01-03 18:00",
                                   "2023-01-04 09:00"]))
        clock = trading_clock(b)
        self.assertEqual(clock.day.tolist(), [20230103, 20230104, 20230104, 20230104, 20230104])
        self.assertEqual(clock.fill_window.tolist(), [True, False, False, False, True])


if __name__ == "__main__":
    unittest.main()
