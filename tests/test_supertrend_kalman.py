"""Supertrend + Kalman (M15 signals on 1m): indicators against independent transcriptions, no look-ahead through
the M15 mapping, event and order rules, and grid chunking."""

import math

import numpy as np
import pytest

from strategies import supertrend_kalman as sk
from tvtester import optimize, ta
from tvtester.data import DATA_DIR, Bars, load_bars
from tvtester.engine import LONG, run

HAS_DATA = any(DATA_DIR.glob("*.parquet"))
needs_data = pytest.mark.skipif(not HAS_DATA, reason="no data")


@pytest.fixture(scope="module")
def bars():
    return Bars.from_frame(load_bars("2023-03-01", "2023-05-01"))


# --- indicators: independent transcriptions of the Pine formulas -----------------------------------------
def pine_atr(h, l, c, n):
    out, prev = [], None
    trs = []
    for i in range(len(c)):
        tr = h[i] - l[i] if i == 0 else max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
        trs.append(tr)
        if i < n - 1:
            out.append(math.nan)
        elif i == n - 1:
            prev = sum(trs) / n
            out.append(prev)
        else:
            prev = (prev * (n - 1) + tr) / n
            out.append(prev)
    return out


def pine_supertrend(h, l, c, factor, n):
    a = pine_atr(h, l, c, n)
    U, L, ST, D = [], [], [], []
    for i in range(len(c)):
        bu = (h[i] + l[i]) / 2 + factor * a[i]
        bl = (h[i] + l[i]) / 2 - factor * a[i]
        pu = 0.0 if i == 0 or math.isnan(U[-1]) else U[-1]
        pl = 0.0 if i == 0 or math.isnan(L[-1]) else L[-1]
        c1 = c[i - 1] if i else math.nan
        u = bu if (bu < pu or c1 > pu) else pu
        lo = bl if (bl > pl or c1 < pl) else pl
        if i == 0 or math.isnan(a[i - 1]):
            d = 1
        elif ST[-1] == pu:
            d = -1 if c[i] > u else 1
        else:
            d = 1 if c[i] < lo else -1
        U.append(u), L.append(lo), D.append(d), ST.append(lo if d == -1 else u)
    return np.array(ST), np.array(D)


def kalman_matrix(z, q, r=1.0):
    F = np.array([[1.0, 1.0], [0.0, 1.0]])
    H = np.array([[1.0, 0.0]])
    Q = q * np.array([[0.25, 0.5], [0.5, 1.0]])
    x = np.array([z[0], 0.0])
    P = 100.0 * np.eye(2)
    out = [x[1]]
    for zi in z[1:]:
        x = F @ x
        P = F @ P @ F.T + Q
        K = (P @ H.T) / (H @ P @ H.T + r)
        x = x + (K * (zi - H @ x)).ravel()
        IKH = np.eye(2) - K @ H
        P = IKH @ P @ IKH.T + K @ K.T * r
        out.append(x[1])
    return np.array(out)


@needs_data
def test_supertrend_matches_transcription(bars):
    m = sk.m15(bars)
    h, l, c = m["h"], m["l"], m["c"]
    line, d = ta.supertrend(h, l, c, 3.0, 10)
    eline, ed = pine_supertrend(h.tolist(), l.tolist(), c.tolist(), 3.0, 10)
    assert np.array_equal(d, ed)
    assert np.allclose(line, eline, equal_nan=True)
    assert (d == -1).sum() > 100 and (d == 1).sum() > 100


@needs_data
def test_kalman_matches_matrix_form(bars):
    c = sk.m15(bars)["c"] * 0.01
    for q in (0.01, 0.0001):
        assert np.allclose(ta.kalman_trend(c, q)[1], kalman_matrix(c, q), rtol=1e-9, atol=1e-12)


def test_ut_stop_recursion():
    c = np.array([10.0, 11, 12, 11.5, 9, 8, 8.5, 12])
    loss = np.array([np.nan, 1, 1, 1, 1, 1, 1, 1])
    t = ta.atr_trailing_stop(c, loss)
    # bar1: p = nz(nan) = 0, both closes above -> max(0, 10); then ratchets up, resets below on the drop
    assert math.isnan(t[0])
    assert list(t[1:]) == [10.0, 11.0, 11.0, 10.0, 9.0, 9.0, 11.0]


def test_ema_seed_and_stdev():
    x = np.array([np.nan, np.nan, 1.0, 2.0, 4.0])
    e = ta.ema(x, 3)  # Pine: seeded with the first valid value (Codex R7 case [1, 2, 4] -> [1, 1.5, 2.75])
    assert np.isnan(e[:2]).all() and list(e[2:]) == [1.0, 1.5, 2.75]
    assert ta.stdev(np.array([1.0, 2.0, 3.0]), 3)[2] == pytest.approx(np.std([1, 2, 3]))


# --- M15 mapping: no look-ahead ---------------------------------------------------------------------------
@needs_data
def test_m15_buckets(bars):
    m = sk.m15(bars)
    key = bars.t_ms // sk.BUCKET_MS
    starts = m["starts"]
    assert np.all(np.diff(key[starts]) > 0)  # nonempty buckets only, never manufactured
    j = 100
    seg = slice(starts[j], starts[j + 1])
    assert m["h"][j] == bars.h[seg].max() and m["l"][j] == bars.l[seg].min()
    assert m["o"][j] == bars.o[starts[j]] and m["c"][j] == bars.c[starts[j + 1] - 1]
    i = starts[j + 1]
    assert m["prev"][i] == j and m["prev"][i - 1] == j - 1  # bucket j is seen only from the next bucket


@needs_data
@pytest.mark.parametrize("trigger", sk.TRIGGERS)
def test_prefix_no_lookahead(bars, trigger):
    """Signals and the decision inputs at a bar never change when later bars change (cut mid-bucket)."""
    full = sk.SupertrendKalman(trigger=trigger, kalman_q=0.0001)
    full.prepare(bars)
    cut = 30_007  # not a bucket boundary
    sub = Bars.from_frame(load_bars("2023-03-01", "2023-05-01").iloc[:cut].reset_index(drop=True))
    part = sk.SupertrendKalman(trigger=trigger, kalman_q=0.0001)
    part.prepare(sub)
    assert np.array_equal(full.sig[:cut], part.sig)
    k = part.prev[cut - 1]
    for name in ("st_dir", "tr_stop", "k_slope", "sw_lo", "sw_hi", "atr14", "rvi"):
        assert np.allclose(full.ind[name][: k + 1], part.ind[name][: k + 1], equal_nan=True), name


# --- events and orders ------------------------------------------------------------------------------------
@needs_data
@pytest.mark.parametrize("kw", [dict(trigger="st"), dict(trigger="both", exit="trail"),
                                dict(trigger="trail", exit="flip", vol="stop_atr:1.5"),
                                dict(hours="ny", vol="atr_ratio:1.2"), dict(vol="rvi")])
def test_entries_at_bucket_open_with_valid_stop(bars, kw):
    s = sk.SupertrendKalman(**kw)
    r = run(s, bars)
    assert r.trades
    for t in r.trades:
        i = t.signal_bar
        assert s.first[i] and s.sig[i] == t.direction  # one decision per completed bucket
        k = s.prev[i]
        stop = s.ind["sw_lo"][k] if t.direction == LONG else s.ind["sw_hi"][k]
        risk = abs(bars.c[i] - stop)
        assert (bars.c[i] - stop) * t.direction > 0
        if s.vol_kind == "stop_atr":
            assert risk <= s.vol_x * s.ind["atr14"][k]
        if s.vol_kind == "atr_ratio":
            assert s.ind["atr14"][k] <= s.vol_x * s.ind["atr100"][k]
        if s.vol_kind == "rvi":
            assert (s.ind["rvi"][k] - 50) * t.direction > 0
        if kw.get("hours") == "ny":
            assert s.in_hours[i]


@needs_data
def test_trail_stop_never_loosens(bars):
    s = sk.SupertrendKalman(trigger="both", exit="trail")
    stops = []
    orig = s.on_bar

    def spy(ctx, i):
        before = (ctx.position_size, getattr(s, "stop", None))
        orig(ctx, i)
        if before[0] != 0:
            stops.append((s.eid, before[0], before[1], s.stop))

    s.on_bar = spy
    run(s, bars)
    moved = [(d, a, b) for _, d, a, b in stops if a != b]
    assert moved, "trail never moved a stop"
    assert all((b > a) if d > 0 else (b < a) for d, a, b in moved)


@needs_data
def test_partial_first_bucket_refused():
    df = load_bars("2023-03-01", "2023-03-02").iloc[7:].reset_index(drop=True)
    with pytest.raises(ValueError):
        sk.SupertrendKalman().prepare(Bars.from_frame(df))


def test_session_close_cancels_bracket_first():
    """Codex R7: long, target 72.00, session close queued, next open 73.00 -> market close at 73 minus slippage,
    not the unslipped limit."""
    import pandas as pd
    from tvtester.config import DEFAULT
    from tvtester.engine import Engine

    ts = pd.date_range("2023-03-01 14:00", periods=3, freq="1min", tz="America/New_York").tz_convert("UTC")
    df = pd.DataFrame({"ts": ts, "raw_symbol": "CLJ3", "open": [70.0, 70.0, 73.0], "high": [70.0, 70.0, 73.0],
                       "low": [70.0, 70.0, 73.0], "close": [70.0, 70.0, 73.0], "volume": 1, "vendor": "t"})
    b = Bars.from_frame(df)
    s = sk.SupertrendKalman(hours="ny")
    s.in_hours = np.array([True, False, False])
    s.prev = np.zeros(3, dtype=int)
    s.first = np.zeros(3, dtype=bool)
    s.params["exit"] = "fixed"
    e = Engine(b, DEFAULT.with_slippage(1))
    e.process_bar(0)
    e.ctx.entry("Long", LONG)
    e.ctx.exit("Exit", "Long", stop=6900, limit=7200)
    e.process_bar(1)
    s.bars, s.ind = b, {}
    s.on_bar(e.ctx, 1)
    e.process_bar(2)
    t = e.trades[0]
    assert t.exit_reason == "close" and t.exit_price == 7300 - 1


@needs_data
def test_flip_exit_is_market_close(bars):
    r = run(sk.SupertrendKalman(trigger="trail", exit="flip"), bars)
    flips = [t for t in r.trades if t.exit_id == "ST flip"]
    assert flips and all(t.exit_reason == "close" for t in flips)


def test_vol_parsing():
    assert sk.SupertrendKalman(vol="stop_atr:1.5").vol_x == 1.5
    with pytest.raises(ValueError):
        sk.SupertrendKalman(vol="stop_atr")
    with pytest.raises(ValueError):
        sk.SupertrendKalman(vol="rvi:2")


# --- grid chunking (cli --chunks) gives the same ranked grid ----------------------------------------------
@needs_data
def test_grid_chunks_equal_serial(bars):
    grid = {"trigger": ["st", "both"], "exit": ["fixed", "trail"], "rr": [2, 3]}
    f = sk.SupertrendKalman
    serial = optimize.run_grid(f, grid, bars)
    n = len(optimize.combos(grid))
    rows = []
    for j in range(3):
        rows += optimize.grid_rows(f, grid, bars, orders=list(range(j + 1, n + 1, 3)))
    assert optimize.rank(rows).equals(serial)
