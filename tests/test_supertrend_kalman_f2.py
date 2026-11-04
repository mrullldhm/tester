"""Supertrend + Kalman feature 2: feature values against a literal bar-by-bar transcription, causality, the
veto (never blocks an exit, never depends on the position) and no filters = the feature-1 strategy."""

import math
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

pytest.skip("Supertrend Kalman is retired", allow_module_level=True)

from strategies import supertrend_kalman as sk
from tvtester import experiment, metrics
from tvtester.config import ROOT
from tvtester.data import DATA_DIR, Bars, load_bars
from tvtester.engine import LONG, run
from tests.test_supertrend_kalman import pine_atr

needs_data = pytest.mark.skipif(not any(DATA_DIR.glob("*.parquet")), reason="no data")
NY = ZoneInfo("America/New_York")
KW = [dict(hours="all", **sk.BASELINES["all"]), dict(hours="asia", **sk.BASELINES["asia"]),
      dict(hours="london", **sk.BASELINES["london"]), dict(hours="ny", **sk.BASELINES["ny"])]


@pytest.fixture(scope="module")
def bars():
    return Bars.from_frame(load_bars("2023-03-01", "2023-05-01"))  # code check only; spans the US DST change


def literal_pivot(x, n, is_high):
    """Strict pivot confirmed n buckets after its centre, last confirmed value carried (Pine lastPivot)."""
    out, last = [], math.nan
    for k in range(len(x)):
        if k >= 2 * n:
            c = x[k - n]
            win = [x[j] for j in range(k - 2 * n, k + 1) if j != k - n]
            if all((c > v) if is_high else (c < v) for v in win):
                last = c
        out.append(last)
    return out


def literal(bars, s):
    """{decision bar: {feature: value}}, the Pine way: one bar at a time. ATR14 / ATR100, swing levels and ER come
    from their own transcriptions here (tests/test_supertrend_kalman.py checks the M15 buckets, signals and RVI)."""
    m = sk.m15(bars)
    h15, l15, c15 = list(m["h"]), list(m["l"]), list(m["c"])
    a14, a100 = pine_atr(h15, l15, c15, 14), pine_atr(h15, l15, c15, 100)
    sw = int(s.params["swing"])
    sw_lo, sw_hi = literal_pivot(l15, sw, False), literal_pivot(h15, sw, True)
    kind, x = s.vol_kind, s.vol_x
    rvi = s.ind["rvi"]
    out = {}
    for i in range(len(bars)):
        k = int(m["prev"][i])
        if not m["first"][i] or k < 0 or s.sig[i] == 0 or not s.in_hours[i]:
            continue
        d, c = int(s.sig[i]), int(bars.c[i])
        lvl = sw_lo[k] if d == LONG else sw_hi[k]
        if lvl != lvl or (d == LONG and lvl >= c) or (d != LONG and lvl <= c):
            continue
        risk = abs(c - int(lvl))
        ok = {"stop_atr": lambda: risk <= x * a14[k], "atr_ratio": lambda: a14[k] <= x * a100[k],
              "rvi": lambda: rvi[k] > 50 if d == LONG else rvi[k] < 50}.get(kind, lambda: True)()
        if not ok:
            continue
        if k >= 20:
            den = sum(abs(c15[j] - c15[j - 1]) for j in range(k - 19, k + 1))
            er = abs(c15[k] - c15[k - 20]) / den if den > 0 else math.nan
        else:
            er = math.nan
        t = bars.ts[i].tz_convert(NY)
        hours = ((t.hour * 60 + t.minute - 18 * 60 + 1440) % 1440) // 60
        r = rvi[k]
        out[i] = {"risk_ticks": risk, "risk_atr": risk / a14[k] if a14[k] > 0 else math.nan,
                  "atr_ratio": a14[k] / a100[k] if a100[k] > 0 else math.nan, "er": er, "hours_since_open": hours,
                  "rvi_side": r if d == LONG else 100 - r}
    return out


def same(a, b) -> bool:
    return (a == b) or (a != a and b != b) or math.isclose(a, b, rel_tol=1e-9)


@needs_data
def test_window_crosses_dst_and_a_roll(bars):
    """The feature tests below run on a window with the US and UK DST changes and a CL contract roll."""
    off = bars.ts.tz_convert(NY).map(lambda t: t.utcoffset())
    assert len(set(off)) == 2
    uk = bars.ts.tz_convert("Europe/London").map(lambda t: t.utcoffset())
    assert len(set(uk)) == 2
    assert len(set(bars.raw_symbol)) >= 2


@needs_data
@pytest.mark.parametrize("kw", KW)
def test_features_match_literal(bars, kw):
    s = sk.SupertrendKalman(**kw)
    s.prepare(bars)
    fv = s.features(bars)
    want = literal(bars, s)
    assert len(want) >= 5
    have = np.flatnonzero(~np.isnan(fv["risk_ticks"]))
    assert sorted(want) == have.tolist()
    for i, feats in want.items():
        for name, v in feats.items():
            assert same(float(fv[name][i]), float(v)), (i, name, fv[name][i], v)


def test_efficiency_ratio_edges():
    c = np.array([5.0] * 30)
    assert np.isnan(sk.efficiency_ratio(c, 20)).all()  # flat closes: 0 / 0 = NaN
    c = np.arange(30, dtype=float)
    er = sk.efficiency_ratio(c, 20)
    assert np.isnan(er[:20]).all() and np.allclose(er[20:], 1.0)


@needs_data
@pytest.mark.parametrize("kw", [KW[0], KW[3]])
def test_features_are_causal(kw):
    df = load_bars("2023-03-01", "2023-05-01")
    k = len(df) * 2 // 3 + 7  # the prefix ends inside an M15 bucket
    moved = df.copy()
    moved.loc[k:, "high"] += 0.5
    moved.loc[k:, "low"] -= 0.5
    moved.loc[k:, "close"] = moved.loc[k:, "open"] + 0.2
    out = []
    for frame in (df, df.iloc[:k].reset_index(drop=True), moved):
        b = Bars.from_frame(frame)
        s = sk.SupertrendKalman(**kw)
        s.prepare(b)
        out.append(s.features(b))
    for name in sk.FEATURES:
        a = out[0][name][:k]
        assert np.array_equal(a, out[1][name], equal_nan=True), name
        assert np.array_equal(a, out[2][name][:k], equal_nan=True), name


@needs_data
def test_features_do_not_depend_on_filters_or_position(bars):
    """Signal B after a vetoed signal A gets the same value as when A was traded (no position-based NaN)."""
    p = KW[0]
    s0 = sk.SupertrendKalman(**p)
    s0.prepare(bars)
    f = [("risk_ticks", "min", 60)]
    s1 = sk.SupertrendKalman(**p, filters=f)
    s1.prepare(bars)
    f0, f1 = s0.features(bars), s1.features(bars)
    for name in sk.FEATURES:
        assert np.array_equal(f0[name], f1[name], equal_nan=True), name
    r0, r1 = run(s0, bars), run(s1, bars)
    sb1 = {t.signal_bar for t in r1.trades}
    assert sb1 and all(f1["risk_ticks"][i] >= 60 for i in sb1)
    vetoed = set(np.flatnonzero((s1.sig != 0) & s1.in_hours & ~s1.allow).tolist())
    assert vetoed and not vetoed & sb1
    # a signal skipped in the plain run because a position was open is traded once the filter frees the strategy
    sb0 = {t.signal_bar for t in r0.trades}
    assert sb1 - sb0


@needs_data
@pytest.mark.parametrize("hours,exit", [("ny", "flip"), ("london", "trail"), ("asia", "fixed")])
def test_filter_never_blocks_an_exit(bars, hours, exit):
    """Every bar vetoed from the first entry on: the open trade still exits exactly as in the plain run
    (flip close, trail amends, session close, bracket)."""
    p = dict(hours=hours, **{**sk.BASELINES[hours], "exit": exit})

    class VetoAfterEntry(sk.SupertrendKalman):
        def on_bar(self, ctx, i):
            super().on_bar(ctx, i)
            if hasattr(self, "eid"):  # an entry was placed: veto every later bar
                self.allow[:] = False

    plain = run(sk.SupertrendKalman(**p), bars)
    s = VetoAfterEntry(**p)
    vetoed = run(s, bars)
    assert len(plain.trades) >= 2 and len(vetoed.trades) == 1 and vetoed.open_trade is None
    a, b = plain.trades[0], vetoed.trades[0]
    assert (a.entry_bar, a.exit_bar, a.exit_price, a.exit_reason) == (b.entry_bar, b.exit_bar, b.exit_price,
                                                                        b.exit_reason)
    assert not s.allow.any()


@pytest.fixture(scope="module")
def dev():
    return experiment.dev_bars()


@needs_data
@pytest.mark.parametrize("variant", ["all", "asia", "london", "ny"])
def test_no_filters_reproduces_feature_1(dev, variant):
    """Development interval only: the unfiltered run equals the feature-1 trade list cut at the same date (a
    feature-1 trade still open at the cutoff is open, not closed, in the development run)."""
    import json
    from tvtester.experiment import EXECUTION_VERSION
    if json.loads((ROOT / "results/supertrend_kalman" / variant / "summary.json").read_text()).get("execution_version") != EXECUTION_VERSION:
        pytest.skip("Saved feature-1 trades predate the limit-entry revision; regenerate the golden results first.")
    end = pd.Timestamp(experiment.DEV_END, tz="UTC")
    assert dev.ts[-1] < end
    res = run(sk.SupertrendKalman(hours=variant, **sk.BASELINES[variant]), dev)
    tf = metrics.trade_frame(res)
    f1 = pd.read_csv(ROOT / "results" / "supertrend_kalman" / variant / "trades_slippage0.csv",
                     parse_dates=["entry_time", "exit_time"])
    f1 = f1[f1["exit_time"] < end]
    assert len(tf) == len(f1) > 500
    assert (tf["entry_time"].to_numpy() == f1["entry_time"].to_numpy()).all()
    assert (tf["exit_time"].to_numpy() == f1["exit_time"].to_numpy()).all()
    assert np.allclose(tf["profit"], f1["profit"]) and (tf["exit_reason"].to_numpy() == f1["exit_reason"].to_numpy()).all()


def test_report_clock():
    assert sk.SupertrendKalman().report_tz == "America/New_York"
