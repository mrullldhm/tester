"""Feature 2: feature values, entry vetoes and the search helpers.

- Features match a literal bar-by-bar Pine-style transcription (independent stop tracking, `var` resets).
- Features and signals are causal: a prefix of the bars gives the same earlier values, and changing later bars
  changes nothing earlier.
- No filters = the feature-1 strategy trade for trade; a vetoed signal is never traded.
"""

import math

import numpy as np
import pandas as pd
import pytest

from strategies import fair_price_reversal as fpr
from tests.test_fair_price_reversal import literal
from tvtester import features as fx
from tvtester import associate, experiment, metrics, search, ta
from tvtester.config import ROOT
from tvtester.data import DATA_DIR, Bars, load_bars
from tvtester.engine import run
from tvtester.sessions import SESSIONS, local_clock

has_data = pytest.mark.skipif(not any(DATA_DIR.glob("*.parquet")), reason="no data")
COMBOS = [(120, 0.5, 3), (60, 1.0, 2), (30, 2.0, 1)]


def literal_features(bars, session, window, mult, swing, atr_len=14):
    """{signal bar: {feature: value}}, computed the way the Pine twin does it."""
    s = SESSIONS[session]
    mod, day = local_clock(bars.ts, s.tz)
    atr1 = ta.shift(ta.atr(bars.h, bars.l, bars.c, atr_len), 1)
    sigs = {i: stop for i, _, stop in literal(bars, session, window, mult, swing, atr_len, with_stop=True)}
    last_day = None
    body_atr = rr = math.nan
    hist = []
    out = {}
    for i in range(len(bars)):
        if mod[i] == s.anchor_minute and (last_day is None or day[i] != last_day):
            last_day = day[i]
            a = atr1[i]
            body_atr = abs(bars.c[i] - bars.o[i]) / a if a == a and a > 0 else math.nan
            rng = float(max(bars.h[i - 1380:i]) - min(bars.l[i - 1380:i])) if i >= 1380 else math.nan
            rr = math.nan
            if rng == rng:
                if len(hist) == 20 and sum(hist) > 0:
                    rr = rng / (sum(hist) / 20)
                hist.append(rng)
                hist = hist[-20:]
        if i in sigs:
            risk = abs(bars.c[i] - sigs[i])
            a = atr1[i]
            out[i] = {"minutes_from_open": mod[i] - s.open_minute, "anchor_body_atr": body_atr,
                      "risk_ticks": risk, "risk_atr": risk / a if a == a and a > 0 else math.nan, "range_ratio": rr}
    return out


def computed(bars, session, window, mult, swing):
    sg = fpr.signals(bars, session, window, mult, swing)
    return sg, fpr.feature_values(bars, session, sg)


def same(a, b) -> bool:
    return (a == b) or (a != a and b != b) or (isinstance(a, float) and math.isclose(a, b, rel_tol=1e-12))


@has_data
@pytest.mark.parametrize("session", ["asia", "london", "ny"])
@pytest.mark.parametrize("window,mult,swing", COMBOS)
def test_features_match_literal_pine(session, window, mult, swing):
    bars = Bars.from_frame(load_bars("2024-02-20", "2024-04-15"))  # code check only; spans US / UK DST changes
    sg, fv = computed(bars, session, window, mult, swing)
    want = literal_features(bars, session, window, mult, swing)
    assert sorted(want) == [int(i) for i in np.flatnonzero(sg["sig"])]
    assert len(want) > 5 and any(v["range_ratio"] == v["range_ratio"] for v in want.values())
    for i, feats in want.items():
        for k, v in feats.items():
            assert same(float(fv[k][i]), float(v)), (i, k, fv[k][i], v)


@has_data
@pytest.mark.parametrize("session", ["asia", "ny"])
def test_features_and_signals_are_causal(session):
    df = load_bars("2024-02-20", "2024-04-15")
    full = Bars.from_frame(df)
    k = len(df) * 2 // 3
    sg_f, fv_f = computed(full, session, 120, 0.5, 3)
    sg_p, fv_p = computed(Bars.from_frame(df.iloc[:k].reset_index(drop=True)), session, 120, 0.5, 3)
    moved = df.copy()
    moved.loc[k:, "high"] += 0.5
    moved.loc[k:, "low"] -= 0.5
    moved.loc[k:, "close"] = moved.loc[k:, "open"] + 0.2
    sg_m, fv_m = computed(Bars.from_frame(moved), session, 120, 0.5, 3)
    assert (sg_f["sig"][:k] == sg_p["sig"]).all() and (sg_f["sig"][:k] == sg_m["sig"][:k]).all()
    for name in fpr.FEATURES:
        a, p, m = fv_f[name][:k], fv_p[name], fv_m[name][:k]
        assert np.array_equal(a, p, equal_nan=True), name
        assert np.array_equal(a, m, equal_nan=True), name


@has_data
def test_no_filters_reproduces_feature_1_and_vetoes_hold():
    """Development interval only: the unfiltered run equals the feature-1 trade list cut at the same date."""
    bars = experiment.dev_bars()
    assert bars.ts[-1] < pd.Timestamp(experiment.DEV_END, tz="UTC")
    p = {"session": "ny", **fpr.BASELINES["ny"]}
    tf = metrics.trade_frame(run(fpr.FairPriceReversal(**p), bars))
    f1 = pd.read_csv(ROOT / "results" / "fair_price_reversal" / "ny" / "trades_slippage0.csv", parse_dates=["entry_time"])
    f1 = f1[f1["entry_time"] < pd.Timestamp(experiment.DEV_END, tz="UTC")]
    assert len(tf) == len(f1) > 2000
    assert (tf["entry_time"].to_numpy() == f1["entry_time"].to_numpy()).all()
    assert np.allclose(tf["profit"], f1["profit"]) and (tf["exit_reason"].to_numpy() == f1["exit_reason"].to_numpy()).all()
    f = [("risk_ticks", "max", 30), ("range_ratio", "min", 0.8)]
    s = fpr.FairPriceReversal(**p, filters=f)
    rf = run(s, bars)
    sb = np.array([t.signal_bar for t in rf.trades])
    fv = s.features(bars)
    assert len(rf.trades) > 300
    assert (fv["risk_ticks"][sb] <= 30).all() and (fv["range_ratio"][sb] >= 0.8).all()
    # a vetoed signal bar where the engine still calls on_bar (a position open or closing) never becomes a trade
    vetoed = np.flatnonzero((s.sig["sig"] != 0) & ~s.allow)
    assert len(vetoed) > 0 and not set(vetoed.tolist()) & set(sb.tolist())


def test_filter_ops_and_nan():
    v = np.array([1.0, 2.0, np.nan])
    assert fx.Filter("x", "min", 2).passes(v).tolist() == [False, True, False]
    assert fx.Filter("x", "max", 1).passes(v).tolist() == [True, False, False]
    with pytest.raises(ValueError):
        fx.Filter("x", "between", 1)
    with pytest.raises(KeyError):
        fx.gate((fx.Filter("nope", "min", 1),), {"x": v}, 3)


def test_point_in_time_helpers():
    assert np.array_equal(fx.carry_forward(np.array([1, 3]), np.array([5.0, 7.0]), 5),
                          np.array([np.nan, 5, 5, 7, 7]), equal_nan=True)
    h = np.array([5, 9, 6, 7, 8]); l = np.array([1, 2, 0, 3, 4])
    assert np.array_equal(fx.prior_range(h, l, np.array([1, 3, 4]), 3), [np.nan, 9.0, 9.0], equal_nan=True)
    x = np.array([2.0, np.nan, 4.0, 6.0, 0.0])
    assert np.array_equal(fx.ratio_to_trailing_mean(x, 2), [np.nan, np.nan, np.nan, 2.0, 0.0], equal_nan=True)


SPACE = {"base": {"session": "ny", "window": 60, "atr_mult": 1.0, "swing": 2, "target": "near"},
         "params": {"window": [30, 60, 90], "target": ["near", "far"]},
         "filters": {"risk_ticks": (6, 20, 2), "range_ratio": (0.5, 1.0, 0.1)}}


def test_random_draw_is_reproducible_unique_and_starts_with_baseline():
    a, b = search.draw_random(SPACE, 40, 7), search.draw_random(SPACE, 40, 7)
    assert a == b and len({search.key(c) for c in a}) == len(a) == 40
    assert a[0] == search.canonical(SPACE["base"], [])
    for c in a:
        for ft, op, thr in c["filters"]:
            lo, hi, step = SPACE["filters"][ft]
            assert lo - 1e-9 <= thr <= hi + 1e-9 and thr == search.snap(thr, lo, step)


def test_neighbours():
    cfg = search.canonical({**SPACE["base"], "window": 30}, [["risk_ticks", "max", 20.0]])
    nb = search.neighbours(cfg, SPACE)
    labels = {search.label(c, SPACE["base"]) for c in nb}
    assert labels == {"risk_ticks <= 20", "target=far, window=30, risk_ticks <= 20", "window=30",
                      "window=30, risk_ticks <= 18"} and len(nb) == 4
    assert all(search.key(c) != search.key(cfg) for c in nb)


def test_rank_puts_ineligible_last():
    rows = pd.DataFrame([
        {"trial": 0, "net1": 5000.0, "open1": 0.0, "trades1": 10, "pf1": 3.0},
        {"trial": 1, "net1": 100.0, "open1": 0.0, "trades1": 400, "pf1": 1.1},
        {"trial": 2, "net1": 100.0, "open1": 0.0, "trades1": 400, "pf1": 1.3},
        {"trial": 3, "net1": 90.0, "open1": 20.0, "trades1": 400, "pf1": 1.0},
    ])
    assert search.rank(rows, "net1")["trial"].tolist() == [3, 2, 1, 0]


def _fake_rows(module_name, cfgs, jobs):
    """Stand-in for the engine: objective grows with the number of filters, trades fall."""
    calls.append(len(cfgs))
    return [{"net0": 0.0, "open0": 0.0, "trades0": 1000, "pf0": 1.0, "win0": 50.0, "avg0": 0.0, "dd0": 0.0,
             "sharpe0": 0.0, "net1": 100.0 * len(c["filters"]) + c["params"]["window"], "open1": 0.0,
             "trades1": 1000 - 200 * len(c["filters"]), "pf1": 1.0, "win1": 50.0, "avg1": 0.0, "dd1": 0.0,
             "sharpe1": 0.0, "net2": 0.0, "open2": 0.0, "trades2": 1000, "pf2": 1.0, "win2": 50.0, "avg2": 0.0,
             "dd2": 0.0, "sharpe2": 0.0} for c in cfgs]


calls: list[int] = []


def test_tpe_budget_exact_duplicates_reused_and_reproducible(tmp_path, monkeypatch):
    monkeypatch.setattr(search, "run_configs", _fake_rows)
    small = {**SPACE, "params": {"window": [30, 60]}, "filters": {"risk_ticks": (6, 8, 2)}}  # 2 x 5 configs
    runs = []
    for n in (1, 2):
        calls.clear()
        (tmp_path / str(n)).mkdir()
        cfgs, rows, dups = search.run_tpe("x", small, tmp_path / str(n), 14, 3, "net1", 3)
        assert len(cfgs) == 14 and cfgs[0] == search.canonical(SPACE["base"], [])
        assert sum(calls) == len({search.key(c) for c in cfgs}) == 14 - sum(dups)  # each config run once
        runs.append([search.key(c) for c in cfgs])
    assert runs[0] == runs[1]


def test_rank_and_neighbours_of_a_filterless_winner():
    assert search.rank(pd.DataFrame(), "net1").empty
    sp = {"base": SPACE["base"], "params": {}, "filters": SPACE["filters"]}
    assert search.neighbours(search.canonical(SPACE["base"], []), sp) == []


def test_dev_loader_never_opens_the_reserved_year(monkeypatch):
    opened = []
    real = pd.read_parquet

    def spy(path, *a, **k):
        opened.append(str(path))
        return real(path, *a, **k)

    monkeypatch.setattr(pd, "read_parquet", spy)
    try:
        from tvtester.data import load_bars as lb
        lb("2023-12-20", experiment.DEV_END)
    except FileNotFoundError:
        pytest.skip("no data")
    assert opened and not any("year=2024" in p for p in opened)


def test_data_hash_sees_contract_changes():
    from tests.test_engine import make_bars
    a = make_bars([(1, 1, 1, 1)] * 2, ["CLF3", "CLF3"])
    b = make_bars([(1, 1, 1, 1)] * 2, ["CLF3", "CLG3"])
    assert experiment.data_hash(a) != experiment.data_hash(b)


def test_constant_feature_buckets():
    tf = pd.DataFrame({"x": [2.0] * 6 + [np.nan], "profit": np.arange(7.0), "week": [1, 1, 2, 2, 3, 3, 4]})
    b = associate.buckets(tf, "x", False)
    assert b["bucket"].tolist() == ["2 .. 2", "NaN"] and b["trades"].tolist() == [6, 1]


def test_search_report_baseline_row_is_trial_0_even_if_resuggested(tmp_path):
    from tvtester import tune
    row = _fake_rows("x", [search.canonical(SPACE["base"], [])], 1)[0]
    cfgs = [search.canonical(SPACE["base"], []), search.canonical(SPACE["base"], [["risk_ticks", "min", 8.0]]),
            search.canonical(SPACE["base"], [])]
    rows = [row, {**row, "net1": 999.0}, row]
    df = search.rank(search.table(cfgs, rows, SPACE["base"], [False, False, True]), "net1")
    meta = {"strategy": "x", "variant": "ny", "space_name": "filters", "sampler": "tpe", "seed": 1,
            "objective": "net1", "min_trades": 300}
    tune.write_search_report(tmp_path, meta, df, pd.DataFrame(), None, None, 6)
    text = (tmp_path / "report.md").read_text()
    head = text.split("## Baseline vs winner")[1].split("## Top 20")[0]
    assert "| 1 | 0 | baseline |" in head and "| 2 | 1 | risk_ticks >= 8 |" in head


def test_search_ledger_claims_runs_before_a_failure(tmp_path, monkeypatch):
    """Engine runs are in the ledger before they run: a crash in the second batch still counts both batches."""
    from tests.test_engine import make_bars
    from tvtester import tune

    monkeypatch.setattr(tune, "ROOT", tmp_path)
    monkeypatch.setattr(tune, "CONFIG_DIR", tmp_path / "configs")
    monkeypatch.setattr(experiment, "ledger_path", lambda name: tmp_path / "ledger.jsonl")
    monkeypatch.setattr(search, "_bars", lambda: make_bars([(1, 1, 1, 1)] * 3))
    batches = []

    def flaky(module_name, cfgs, jobs):
        batches.append(len(cfgs))
        if len(batches) == 2:
            raise RuntimeError("engine died")
        return _fake_rows(module_name, cfgs, jobs)

    monkeypatch.setattr(search, "run_configs", flaky)
    with pytest.raises(RuntimeError):
        tune.cmd_search("fair_price_reversal", "ny", "filters", "random", 20, "net1", 1, 1)  # batches of 8
    assert batches == [8, 8]
    assert experiment.total_evaluations("x") == 3 * 16
