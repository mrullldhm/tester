"""Owner's 5 November clarification: local pivots must also be leg extremes."""

import numpy as np
import pandas as pd

from tvtester.data import Bars
from tvtester import swings as sw


def rebound_bars(mirror=False):
    # High 100 follows low 50 but is not a pivot (left high 110).
    # Later local high 95 is below 100 and must not finalize low 50.
    rows = [(110, 120, 100, 110), (90, 110, 50, 60), (60, 100, 60, 90),
            (80, 90, 70, 80), (80, 95, 65, 90), (80, 90, 40, 50), (50, 80, 50, 70)]
    if mirror:
        rows = [(-o, -l, -h, -c) for o, h, l, c in rows]
    a = np.asarray(rows, dtype=np.int64)
    n = len(a)
    return Bars(pd.date_range("2026-11-04", periods=n, freq="min", tz="UTC"),
                np.arange(n, dtype=np.int64) * 60000, a[:, 0], a[:, 1], a[:, 2], a[:, 3],
                np.ones(n, dtype=np.int64), np.full(n, "CLZ6", dtype=object), np.zeros(n, dtype=bool))


def test_nonpivot_high_blocks_smaller_later_pivot():
    m = sw.minute_swings(rebound_bars())
    assert m.bar.tolist() == [2, 5, 6]  # low, immediate removal, then new lower candidate
    assert m.cur_l.tolist() == [50, sw.NONE, 40]
    assert m.n_h.tolist() == [0, 0, 0]
    assert m.prev_l.tolist() == [sw.NONE, sw.NONE, sw.NONE]


def test_nonpivot_low_blocks_higher_later_pivot():
    m = sw.minute_swings(rebound_bars(mirror=True))
    assert m.bar.tolist() == [2, 5, 6]
    assert m.cur_h.tolist() == [-50, sw.NONE, -40]
    assert m.n_l.tolist() == [0, 0, 0]
    assert m.prev_h.tolist() == [sw.NONE, sw.NONE, sw.NONE]


def test_equal_leg_high_is_allowed_and_later_equal_replaces():
    z = sw.Zig()
    z.push(sw.SL, 50, 0)
    z.visit(sw.SH, 100, 1, False)
    assert not z.visit(sw.SH, 95, 2, True)
    assert z.visit(sw.SH, 100, 3, True)
    assert z.visit(sw.SH, 100, 4, True)
    assert z.idx_h == 4 and z.n_h == 2 and z.prev_h is None


def test_outside_extreme_order_resets_boundary_at_the_low():
    z = sw.Zig()
    z.push(sw.SL, 50, 0)
    z.visit(sw.SH, 100, 1, False)
    assert z.visit(sw.SL, 40, 2, True)
    # The old leg's high 100 precedes the new low: it must not block this high.
    assert z.visit(sw.SH, 90, 2, True)
    assert z.last_type == sw.SH and z.cur_h == 90 and z.cur_l == 40


def test_right_candle_confirmation_remains_causal():
    b = rebound_bars()
    for n in range(3, len(b) + 1):
        prefix = Bars(b.ts[:n], b.t_ms[:n], b.o[:n], b.h[:n], b.l[:n], b.c[:n],
                      b.volume[:n], b.raw_symbol[:n], b.last_of_contract[:n])
        m, full = sw.minute_swings(prefix), sw.minute_swings(b)
        known = full.bar < n
        for name in ("bar", "last_type", "cur_h", "cur_l", "prev_h", "prev_l", "idx_h", "idx_l"):
            assert np.array_equal(getattr(m, name), getattr(full, name)[known]), name
