"""cbr_optimize replay keeps the bracket frozen from the intended limit after a better fill (Codex adversarial
review 2026-11-20: limit 1000, stop 990, target 1020, fill 995 must lose, not win at a target rebuilt from 5 ticks)."""

import numpy as np
import pytest

from studies.cbr_optimize.run import FEE_T, sim


def _path(highs, lows, fill=995, limit=1000, stop=990):
    h, lo = np.array(highs) - fill, np.array(lows) - fill
    o = c = np.zeros(len(h), dtype=np.int64)
    return {"o": o, "h": h, "l": lo, "c": c, "flat_open": None, "risk": fill - stop, "e_off": limit - fill,
            "r0": limit - stop}


def test_improved_fill_keeps_intended_target():
    p = _path(highs=[995, 1010, 995], lows=[995, 995, 990])  # +15 then the stop; target 1020 never trades
    assert sim(p, tgt=2.0) == pytest.approx(-1 - FEE_T / 5)


def test_intended_target_hit_after_improved_fill():
    p = _path(highs=[995, 1020], lows=[995, 995])
    assert sim(p, tgt=2.0) == pytest.approx(25 / 5 - FEE_T / 5)  # 1020 - 995 = 25 ticks on 5 ticks of risk


def test_fill_bar_high_does_not_trigger_break_even():
    """Fill bar reaches +1R (maybe before the fill); next bar dips to the entry, then the 2R target trades. With the
    fill-bar high counted, BE would stop the trade at entry; excluding it, the trade reaches 2R."""
    p = _path(highs=[1010, 1000, 1020], lows=[1000, 1000, 1000], fill=1000)
    assert sim(p, tgt=2.0, be=1.0) == pytest.approx(2 - FEE_T / 10)


def test_fill_bar_high_does_not_arm_the_runner():
    p = _path(highs=[1010, 1005, 1020], lows=[1000, 1000, 1000], fill=1000)
    assert sim(p, tgt=2.0, runner=5) == pytest.approx(2 - FEE_T / 10)  # runner never armed: exits at 2R


@pytest.mark.parametrize("fill", [990, 989])
def test_fill_at_or_through_the_stop_exits_at_the_fill_fee_only(fill):
    """Codex adversarial review 2026-11-20: limit 1000, stop 990; an open at 990 or 989 fills and is stopped on the
    fill bar at the fill price (engine: min(entry, stop) = the fill), net = -fee, normalised by the intended risk."""
    p = _path(highs=[fill, 1020], lows=[fill - 1, 1000], fill=fill)
    r = sim(p, tgt=2.0)
    assert np.isfinite(r) and r == pytest.approx(-FEE_T / 10)
