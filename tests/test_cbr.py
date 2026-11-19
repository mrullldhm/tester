"""CBR rules (docs/strategies/cbr/README.md) on a crafted 1m path in the rth window (Wed 2019-07-10, CDT).

Ticks: reference hour 08:30-09:29 CT zigzags 5990..6010. From 09:30 a 25-bar down leg (highs 6012 -> 5964, lows
6008 -> 5960 = L1), bounce to 5966 (H1), lower low 5950 (L2, below the ref low), then a bar closing 5968 > H1 (MSB).
"""

import numpy as np
import pandas as pd

from cltester.data import add_session
from strategies.cbr import Strategy, _candidates, orders

T0 = pd.Timestamp("2019-07-10 13:30", tz="UTC")  # 08:30 CT


def _bars() -> tuple[list[int], list[int], list[int]]:
    hi, lo, cl = [], [], []
    for k in range(60):  # ref hour zigzag, 6-bar cycles: real swing highs and lows
        up = (k % 6) < 3
        base = 5996 + (k % 3) * 4 if up else 6004 - (k % 3) * 4
        hi.append(base + 6)
        lo.append(base - 6)
        cl.append(base)
    for k in range(25):  # down leg
        hi.append(6012 - 2 * k)
        lo.append(6008 - 2 * k)
        cl.append(6009 - 2 * k)
    for h, low, c in ((5964, 5961, 5963), (5966, 5962, 5963), (5963, 5956, 5957), (5958, 5950, 5953),
                      (5960, 5952, 5958), (5970, 5958, 5968)):
        hi.append(h)
        lo.append(low)
        cl.append(c)
    for _ in range(30):  # drift after
        hi.append(5972)
        lo.append(5966)
        cl.append(5969)
    return hi, lo, cl


def _frame(sign: int = 1) -> pd.DataFrame:
    hi, lo, cl = (np.array(x) for x in _bars())
    if sign == -1:  # mirror around 60.00: a short setup
        hi, lo, cl = 12000 - lo, 12000 - hi, 12000 - cl
    n = len(hi)
    op = np.r_[cl[0], cl[:-1]]
    op = np.clip(op, lo, hi)
    df = pd.DataFrame({"ts": T0 + pd.to_timedelta(np.arange(n), "min"), "raw_symbol": "CLU9",
                       "open": op / 100, "high": hi / 100, "low": lo / 100, "close": cl / 100, "volume": 1,
                       "vendor": "t"})
    return add_session(df)


MSB = 60 + 25 + 5  # bar index of the MSB close


def _one(sign: int) -> pd.Series:
    c = _candidates(_frame(sign))
    c = c[(c["signal"] == MSB) & (c["window"] == "rth")]
    assert len(c) == 1
    return c.iloc[0]


def test_type3_long_found_with_structure_and_extension():
    r = _one(1)
    assert r["side"] == 1 and r["L2"] == 5950 and r["L1"] == 5960 and r["H1"] == 5966 and r["U"] == 5970
    assert r["A_e20"] == 6012  # origin: the leg's first bar, 29 bars before L2
    assert not r["sweep_fh"]  # L2 swept the ref low (5990) but the MSB close 5968 did not reclaim it


def test_short_is_the_mirror():
    r = _one(-1)
    assert r["side"] == -1 and r["L2"] == 5950 - 12000 and r["U"] == 5970 - 12000  # side space: negated prices


def test_orders_price_the_bracket():
    c = _candidates(_frame(1))
    c = c[c["signal"] == MSB]
    p = {"window": "rth", "context": "reb", "bias": "none", "ext": "e20", "target": "mid"}
    o = orders(c, p)
    assert len(o) == 1
    row = o.iloc[0]
    assert round(row["limit"], 2) == 59.60  # L2 + (U - L2) // 2
    assert round(row["stop"], 2) == 59.50  # L2
    assert round(row["target"], 2) == 59.81  # (6012 + 5950) // 2
    o2 = orders(c, {**p, "target": "r2"})
    assert round(o2.iloc[0]["target"], 2) == 59.80  # entry + 2 * 10 ticks
    assert orders(c, {**p, "context": "fh"}).empty


def test_day_rules_stop_after_win_and_cap_attempts():
    t = pd.DataFrame({"trading_day": ["d1"] * 3 + ["d2"] * 3, "net": [-10, 20, -5, -1, -1, 30]})
    kept = Strategy().day_rules(t, {"attempts": 2})
    assert kept.index.tolist() == [0, 1, 3, 4]
    assert Strategy().day_rules(t, {"attempts": 1}).index.tolist() == [0, 3]


def test_cache_never_reuses_another_frames_candidates():
    """Same timestamps, other prices: the cache must recompute (Codex adversarial review 2026-11-19)."""
    from strategies.cbr import candidates

    long_c = candidates(_frame(1))
    short_c = candidates(_frame(-1))
    assert set(long_c.loc[long_c["signal"] == MSB, "side"]) == {1}
    assert set(short_c.loc[short_c["signal"] == MSB, "side"]) == {-1}


def test_no_candidates_gives_empty_signals():
    """Flat prices and frames under 3 bars: no setups, an empty engine signal frame, an empty backtest."""
    from cltester.data import Bars
    from cltester.engine import Fills, backtest

    p = {**Strategy.PARAMS, "window": "rth", "context": "reb"}
    flat = _frame(1)
    for k in ("open", "high", "low", "close"):
        flat[k] = 60.0
    for df in (flat, flat.iloc[:2].reset_index(drop=True)):
        sig = Strategy().signals(df, p)
        assert sig.empty and {"side", "limit", "stop", "target", "expire", "kill"} <= set(sig.columns)
        assert backtest(Bars.from_frame(df), sig, Fills()).empty
