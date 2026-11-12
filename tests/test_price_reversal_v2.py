"""Price Reversal v2: Globex hour clock, hourly anchors, entry cap, fixed TP tiers, FPR parity."""
import numpy as np
import pandas as pd
import pytest

from strategies import fair_price_reversal as fpr
from strategies import price_reversal_v2 as v2
from tvtester import engine, metrics
from tvtester.config import DEFAULT
from tvtester.data import DATA_DIR, Bars, load_bars


def _bars(ts):
    n = len(ts)
    one = np.full(n, 7000, dtype=np.int64)
    return Bars(ts, ts.as_unit("ms").asi8, one, one + 1, one - 1, one, np.ones(n), np.full(n, "CLZ3"),
                np.zeros(n, dtype=bool))


def test_hour_one_is_1800_new_york_in_both_dst_states():
    # 22:00 UTC = 18:00 EDT (06:00 Malaysia); 23:00 UTC = 18:00 EST (07:00 Malaysia)
    ts = pd.DatetimeIndex(["2023-07-10 22:00", "2023-12-11 23:00", "2023-12-11 21:59", "2023-07-11 20:59"], tz="UTC")  # 16:59 EST / EDT
    g, day = v2.globex_clock(_bars(ts))
    assert list(g // 60 + 1) == [1, 1, 23, 23]
    assert list(day) == [20230711, 20231212, 20231211, 20230711]  # 18:00 ET belongs to the next trading date


def test_hour_session_flat_never_reaches_the_halt():
    assert (v2.hour_session("h16").open_minute, v2.hour_session("h16").flat_minute) == (900, 1200)
    assert v2.hour_session("h23").flat_minute == v2.LAST_MINUTE
    assert v2.hour_session("h20").flat_minute == v2.LAST_MINUTE
    with pytest.raises(ValueError):
        v2.hour_session("h24")


def test_hour_anchor_is_the_bar_before_the_first_bar_of_the_hour():
    # Monday trading date: Sunday 16:58-16:59 ET is the previous date (Friday in reality), then 18:00 ET reopens.
    ts = pd.DatetimeIndex(["2023-07-09 20:58", "2023-07-09 20:59", "2023-07-09 22:00", "2023-07-09 22:01",
                           "2023-07-09 23:00", "2023-07-09 23:02"], tz="UTC")
    g, day = v2.globex_clock(_bars(ts))
    assert list(v2.hour_anchors(g, day, 0)) == [1]  # hour 1: anchor = last bar before the reopen
    assert list(v2.hour_anchors(g, day, 60)) == [3]  # hour 2 first bar is 19:00 ET -> anchor 18:01


def test_fixed_tp_tiers():
    assert [v2.tier_profit(r) for r in (5, 20, 21, 25, 26, 30, 50, 51)] == [40, 40, 50, 50, 60, 60, 100, 110]


def test_entry_cap_moves_only_far_entries():
    assert v2.planned_limit(1, 7050, 7000, 0) == 7050
    assert v2.planned_limit(1, 7050, 7000, 30) == 7030
    assert v2.planned_limit(1, 7020, 7000, 30) == 7020  # within the cap: signal close
    assert v2.planned_limit(-1, 6950, 7000, 20) == 6980
    assert v2.planned_limit(-1, 6990, 7000, 20) == 6990


def _fixture(entry_cap, tp_mode, target="rr2"):
    """One long signal at bar 0: close 100, stop 50 (R 50 ticks)."""
    class F(v2.PriceReversalV2):
        def prepare(self, data):
            n = len(data)
            self.bars, self.pending, self.allow = data, type(self.pending)(), np.ones(n, dtype=bool)
            self.exits.prepare(data)
            sig = np.zeros(n, dtype=np.int8)
            sig[0] = 1
            self.sig = {"sig": sig, "stop": np.full(n, 50), "body_lo": np.full(n, 120), "body_up": np.full(n, 140)}
            self.mod = np.full(n, self.s.open_minute + 10)
            return sig != 0
    return F(anchor="h16", entry_cap=entry_cap, tp_mode=tp_mode, target=target)


def _ticks(tf, col):
    return round(float(tf.loc[0, col]) * 100)  # trade prices are in USD, 1 tick = $0.01


def _run(strategy, rows):
    a = np.asarray(rows, dtype=np.int64)
    n = len(a)
    ts = pd.date_range("2023-03-06 14:00", periods=n, freq="min", tz="UTC")
    b = Bars(ts, ts.as_unit("ms").asi8, *a.T, np.ones(n), np.full(n, "CLJ3"), np.zeros(n, dtype=bool))
    return metrics.trade_frame(engine.run(strategy, b, DEFAULT))


def test_capped_entry_fills_at_stop_plus_cap_with_rr2_from_the_new_risk():
    tf = _run(_fixture(20, "default"), [[100, 100, 100, 100], [95, 96, 69, 75], [75, 111, 74, 110]])
    assert len(tf) == 1 and _ticks(tf, "entry_price") == 70 and _ticks(tf, "exit_price") == 110  # TP = 70 + 2 x 20
    tf = _run(_fixture(20, "fixed"), [[100, 100, 100, 100], [95, 96, 69, 75], [75, 111, 74, 110]])
    assert _ticks(tf, "exit_price") == 110  # R = 20 -> fixed 40 ticks
    tf = _run(_fixture(0, "fixed"), [[100, 100, 100, 100], [100, 101, 99, 100], [100, 201, 99, 200]])
    assert _ticks(tf, "entry_price") == 100 and _ticks(tf, "exit_price") == 200  # R = 50 -> fixed 100 ticks


def test_capped_entry_is_cancelled_when_the_planned_tp_trades_first():
    # cap 20: limit 70, planned TP 110; price reaches 110 before ever dipping to 70
    tf = _run(_fixture(20, "default"), [[100, 100, 100, 100], [100, 111, 99, 110], [110, 111, 60, 65]])
    assert tf.empty


@pytest.mark.skipif(not any(DATA_DIR.glob("*.parquet")), reason="no data")
def test_session_anchor_with_original_entry_is_fair_price_reversal():
    bars = Bars.from_frame(load_bars("2022-01-01", "2022-07-01"))
    for session, base in v2.ENTRY_BASE.items():
        a = metrics.trade_frame(engine.run(fpr.FairPriceReversal(session=session, swing=1, **base), bars, DEFAULT))
        b = metrics.trade_frame(engine.run(v2.PriceReversalV2(anchor=session, swing=1, **base), bars, DEFAULT))
        assert len(a) > 10
        pd.testing.assert_frame_equal(a, b)


@pytest.mark.skipif(not any(DATA_DIR.glob("*.parquet")), reason="no data")
def test_hour16_anchor_signals_match_ny_session_signals():
    """h16 opens 09:00 ET like the FPR NY session; with the 08:59 bar present both use the same anchor."""
    bars = Bars.from_frame(load_bars("2022-01-01", "2022-04-01"))
    s_ny = fpr.signals(bars, "ny", 60, 1.0, 1)
    g, day = v2.globex_clock(bars)
    s16 = fpr.setup_signals(bars, v2.hour_anchors(g, day, 900), (g >= 900) & (g < 960), g >= 960, 1.0)
    assert (s_ny["sig"] != 0).sum() > 10
    np.testing.assert_array_equal(s_ny["sig"], s16["sig"])
    np.testing.assert_array_equal(s_ny["stop"], s16["stop"])


@pytest.mark.skipif(not any(DATA_DIR.glob("*.parquet")), reason="no data")
def test_hour16_features_match_ny_session_features_at_signals():
    bars = Bars.from_frame(load_bars("2022-01-01", "2022-04-01"))
    ny = fpr.FairPriceReversal(session="ny", window=60, atr_mult=1.0, swing=1)
    ny.prepare(bars)
    h = v2.PriceReversalV2(anchor="h16", window=60, atr_mult=1.0, swing=1)
    h.prepare(bars)
    a, b = ny.features(bars), h.features(bars)
    at = np.flatnonzero(ny.sig["sig"])
    assert len(at) > 10
    for k in v2.FEATURES:
        np.testing.assert_allclose(a[k][at], b[k][at], equal_nan=True, err_msg=k)


@pytest.mark.skipif(not any(DATA_DIR.glob("*.parquet")), reason="no data")
def test_hour_features_are_prefix_invariant():
    full = Bars.from_frame(load_bars("2022-01-01", "2022-03-01"))
    cut = len(full) * 2 // 3
    part = Bars.from_frame(load_bars("2022-01-01", "2022-03-01").iloc[:cut])
    def features_on(bars):
        strategy = v2.PriceReversalV2(anchor="h03", window=60)
        strategy.prepare(bars)
        return strategy.features(bars)

    fa, fb = features_on(full), features_on(part)
    for k in v2.FEATURES:
        np.testing.assert_allclose(fa[k][: cut - 1], fb[k][: cut - 1], equal_nan=True, err_msg=k)


@pytest.mark.skipif(not any(DATA_DIR.glob("*.parquet")), reason="no data")
def test_session_anchor_with_filters_is_fpr_with_filters():
    """Regression 2026-11-12: a filtered session-anchor run raised KeyError('session') (nested prepare/features)."""
    bars = Bars.from_frame(load_bars("2022-01-01", "2022-07-01"))
    base, filt = v2.ENTRY_BASE["london"], [("risk_ticks", "max", 20.0)]
    a = metrics.trade_frame(engine.run(fpr.FairPriceReversal(session="london", swing=1, filters=filt, **base), bars, DEFAULT))
    s = v2.PriceReversalV2(anchor="london", swing=1, filters=filt, **base)
    b = metrics.trade_frame(engine.run(s, bars, DEFAULT))
    assert len(a) > 5 and "session" not in s.params
    pd.testing.assert_frame_equal(a, b)


@pytest.mark.parametrize("size", [1, 16, 64])
@pytest.mark.parametrize("chunks", [1, 3, 16, 100])
def test_chunk_orders_cover_every_grid_order_once(size, chunks):
    from tvtester.cli import chunk_orders
    parts = chunk_orders(size, chunks)
    flat = sorted(o for part in parts for o in part)
    assert flat == list(range(1, size + 1)) and all(parts)


def test_grid_of_uses_the_variant_grid():
    from tvtester.cli import grid_of
    assert grid_of(v2, "entry_ny") == v2.ENTRY_GRID
    assert grid_of(v2, "h01") == v2.GRID
    assert grid_of(fpr, "ny") == fpr.GRID  # modules without GRIDS keep GRID


def test_distinct_configs_skips_a_header_only_neighbours_file(tmp_path, monkeypatch):
    import json

    from tvtester import search, validate
    d = tmp_path / "results" / "price_reversal_v2" / "search" / "entry_ny_x"
    d.mkdir(parents=True)
    cfg = search.canonical({**v2.VARIANTS["entry_ny"], "entry_cap": 20, "tp_mode": "fixed"}, [])
    pd.DataFrame({"trial": [0], "config": [json.dumps(cfg)]}).to_csv(d / "trials.csv", index=False)
    (d / "neighbours.csv").write_text("eligible,objective\n")
    monkeypatch.setattr(validate, "ROOT", tmp_path)
    assert validate.distinct_configs(v2, "price_reversal_v2", ["entry_ny"]) == len(v2.ENTRY_CAPS) * len(v2.TP_MODES)


def test_us_dst_flags_new_york_summer_time_only():
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "tools" / "price_reversal_v2_study.py"
    spec = importlib.util.spec_from_file_location("pr_v2_study", path)
    study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study)
    ts = pd.Series(pd.DatetimeIndex(["2023-03-12 06:59", "2023-03-12 07:00", "2023-11-05 05:59", "2023-11-05 06:00"],
                                    tz="UTC"))
    assert list(study.us_dst(ts)) == [False, True, True, False]
