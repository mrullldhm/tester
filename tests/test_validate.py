"""Feature 3 (docs/VALIDATE.md): selection, walk-forward, CSCV, deflated Sharpe, daily marked equity, fold runs."""

import json
import math
from statistics import NormalDist

import numpy as np
import pandas as pd
import pytest

from tvtester import experiment, metrics, validate
from tvtester.config import DEFAULT
from tvtester.data import Bars
from tvtester.engine import LONG, run
from tvtester.strategy import Strategy


def bars_at(times, closes):
    ts = pd.DatetimeIndex(pd.to_datetime(times, utc=True))
    c = np.asarray(closes, dtype=np.int64)
    sym = np.asarray(["CLF4"] * len(c), dtype=object)
    return Bars(ts, ts.as_unit("ms").asi8, c, c + 1, c - 1, c, np.ones(len(c)), sym, np.zeros(len(c), dtype=bool))


class Script(Strategy):
    def __init__(self, actions):
        super().__init__()
        self.actions = actions

    def prepare(self, bars):
        m = np.zeros(len(bars), dtype=bool)
        m[list(self.actions)] = True
        return m

    def on_bar(self, ctx, i):
        if i in self.actions:
            self.actions[i](ctx)


# --- selection --------------------------------------------------------------------------------------------
def test_select_eligibility_ties_and_cash():
    obj = np.array([5.0, 9.0, 9.0, 20.0])
    closed = np.array([10, 10, 10, 2])
    assert validate.select(obj, closed, 5) == 1  # 3 is best but ineligible; 1 and 2 tie: lower trial wins
    assert validate.select(obj, closed, 11) is None  # nobody eligible: the fold is in cash


def test_select_profit_factor_tie_break_as_e2():
    # equal objectives with different paths: [200, -100] (PF 2) beats [300, -200] (PF 1.5); no loser = inf
    obj = np.array([100.0, 100.0, 100.0])
    closed = np.array([2, 2, 2])
    pf = validate.profit_factor(np.array([300.0, 200.0, 100.0]), np.array([200.0, 100.0, 0.0]), closed)
    assert pf.tolist() == [1.5, 2.0, np.inf]
    assert validate.select(obj, closed, 1, pf) == 2
    assert validate.select(obj, closed, 1, np.array([1.5, 2.0, 1.0])) == 1
    assert validate.profit_factor(np.array([0.0]), np.array([0.0]), np.array([0])).tolist() == [-1.0]


def test_min_trades_scales_and_rounds_up():
    assert validate.min_trades(1000, 1000) == 300
    assert validate.min_trades(1, 1000) == 1
    assert validate.min_trades(501, 1000) == math.ceil(300 * 501 / 1000)


def _days(start, end):
    return np.arange(validate._day(start), validate._day(end))


def test_wfo_anchored_uses_only_days_before_the_cutoff():
    day = _days("2013-01-01", "2016-01-01")
    eq = np.full((2, len(day)), 50_000.0)
    cl = np.tile(np.arange(len(day)), (2, 1))
    cut = int(np.searchsorted(day, validate._day("2014-01-01")))
    eq[0, :cut] += 100.0  # config 0 ahead before 2014
    out = validate.wfo_select(day, eq, cl, 50_000.0, years=(2014,))
    assert out[0]["pick"] == 0 and out[0]["train_obj"] == 100.0
    eq2 = eq.copy()
    eq2[1, cut:] += 1e6  # a huge future gain for config 1 must not change the 2014 pick
    assert validate.wfo_select(day, eq2, cl, 50_000.0, years=(2014,))[0]["pick"] == 0


def test_wfo_rolling_scores_the_window_change_only():
    day = _days("2009-01-01", "2015-01-01")
    eq = np.full((2, len(day)), 50_000.0)
    cl = np.tile(np.arange(len(day)), (2, 1))
    q = int(np.searchsorted(day, validate._day("2010-01-01")))
    eq[0, :q] += 500.0  # config 0 earned before the 4-year window, then fell back
    eq[1, q:] += 10.0
    a = validate.wfo_select(day, eq, cl, 50_000.0, years=(2014,))[0]
    r = validate.wfo_select(day, eq, cl, 50_000.0, years=(2014,), rolling=4)[0]
    assert a["pick"] == 1 and r["pick"] == 1
    eq[0, : q] = 50_000.0
    eq[0, q - 1] = 49_000.0  # config 0 starts the window 1,000 down and recovers: +1,000 inside the window
    assert validate.wfo_select(day, eq, cl, 50_000.0, years=(2014,), rolling=4)[0]["pick"] == 0


# --- CSCV -------------------------------------------------------------------------------------------------
def test_blocks_cover_every_day_once():
    bl = validate.blocks(35, 16)
    assert bl[0] == (0, 3) and bl[2] == (6, 9) and bl[3] == (9, 11) and bl[-1][1] == 35
    assert sum(b - a for a, b in bl) == 35


def test_avg_rank_ties():
    v = np.array([1.0, 2.0, 2.0, 3.0])
    assert validate.avg_rank(v, 2.0) == 2.5 and validate.avg_rank(v, 3.0) == 4 and validate.avg_rank(v, 1.0) == 1


def test_cscv_dominant_config_is_not_overfit():
    rng = np.random.default_rng(1)
    pnl = rng.normal(0, 1, (20, 320))
    pnl[7] += 5.0  # best in every block
    out = validate.cscv(pnl, np.ones_like(pnl, dtype=int), s=8)
    assert out["splits"] == math.comb(8, 4) and out["skipped"] == 0
    assert out["pbo"] == 0.0 and out["p_oos_loss"] == 0.0


def test_cscv_noise_is_near_one_half_and_ineligible_splits_are_skipped():
    rng = np.random.default_rng(2)
    pnl = rng.normal(0, 1, (60, 640))
    out = validate.cscv(pnl, np.ones_like(pnl, dtype=int), s=8)
    assert 0.3 < out["pbo"] < 0.7
    none = validate.cscv(pnl, np.zeros_like(pnl, dtype=int), s=8)
    assert none["skipped"] == none["splits"] and none["pbo"] is None


def test_cscv_lucky_block_winners_are_overfit():
    # config j earns +10 a day in block j only and loses 1 a day elsewhere: the in-sample winner is the config
    # whose lucky block sits in the in-sample half, so out of sample it only loses and ranks at the bottom
    s, per = 8, 20
    pnl = np.full((s, s * per), -1.0)
    for j in range(s):
        pnl[j, j * per:(j + 1) * per] = 10.0
    out = validate.cscv(pnl, np.full(pnl.shape, 5), s=s)
    assert out["pbo"] == 1.0 and out["p_oos_loss"] == 1.0


# --- deflated Sharpe --------------------------------------------------------------------------------------
def test_sharpe_stats_normal_moments_and_zero_variance():
    r = np.random.default_rng(3).normal(0.01, 0.02, 200_000)
    st = validate.sharpe_stats(r)
    assert st["sr"] == pytest.approx(0.5, abs=0.01)
    assert abs(st["skew"]) < 0.02 and st["kurt"] == pytest.approx(3.0, abs=0.05)
    assert validate.sharpe_stats(np.zeros(10))["sr"] is None


def test_expected_max_sr_formula():
    n, v = 100, 0.04
    g = validate.EULER
    want = math.sqrt(v) * ((1 - g) * NormalDist().inv_cdf(1 - 1 / n) + g * NormalDist().inv_cdf(1 - 1 / (n * math.e)))
    assert validate.expected_max_sr(v, n) == pytest.approx(want)
    assert validate.expected_max_sr(v, 1) == 0.0
    assert validate.expected_max_sr(v, 1000) > validate.expected_max_sr(v, 100)  # more trials, higher luck bar


def test_dsr_hand_value_and_undefined():
    st = {"sr": 0.1, "skew": -0.5, "kurt": 6.0, "t": 1001}
    out = validate.dsr(st, 0.0004, 50)
    sr0 = validate.expected_max_sr(0.0004, 50)
    z = (0.1 - sr0) * math.sqrt(1000) / math.sqrt(1 + 0.5 * 0.1 + 5 / 4 * 0.01)
    assert out["dsr"] == pytest.approx(NormalDist().cdf(z))
    assert validate.dsr({"sr": None, "skew": None, "kurt": None, "t": 10}, 0.1, 5)["dsr"] is None
    assert validate.dsr({"sr": 2.0, "skew": 5.0, "kurt": 3.0, "t": 10}, 0.0, 1)["dsr"] is None  # 1 - 10 + 2 < 0


def test_universe_variance_skips_zero_variance_configs():
    r = np.vstack([np.zeros(50), np.random.default_rng(4).normal(0, 1, (3, 50))])
    v, zero = validate.universe_variance(r)
    srs = [validate.sharpe_stats(x)["sr"] for x in r[1:]]
    assert zero == 1 and v == pytest.approx(np.var(srs, ddof=1))


def test_bootstrap_interval_brackets_the_sr():
    r = np.random.default_rng(5).normal(0.05, 1, 2000)
    lo, hi = validate.bootstrap_sr(r, n=300)
    assert lo < validate.sharpe_stats(r)["sr"] < hi


def test_monthly_sums_by_utc_month():
    day = _days("2020-01-30", "2020-02-03")
    pnl = np.array([[1.0, 2.0, 3.0, 4.0]])
    assert validate.monthly(day, pnl).tolist() == [[3.0, 7.0]]


# --- daily marked equity, engine start, fold value -------------------------------------------------------
TIMES = ["2023-01-02 14:00", "2023-01-02 14:01", "2023-01-02 23:59", "2023-01-03 14:00", "2023-01-03 14:01",
         "2023-01-04 14:00"]


def test_daily_equity_marks_open_positions_at_day_end():
    bars = bars_at(TIMES, [100, 100, 104, 110, 120, 130])
    res = run(Script({0: lambda c: c.entry("L", LONG), 3: lambda c: c.close_all()}), bars)
    t = res.trades[0]
    assert (t.entry_bar, t.exit_bar, t.entry_price, t.exit_price) == (1, 4, 100, 120)
    de = metrics.daily_equity(res)
    assert de["end_bar"].tolist() == [2, 4, 5]
    cap = DEFAULT.initial_capital
    assert de["equity"][0] == pytest.approx(cap + 4 * 10 - 2.01)  # open at 104, entry commission paid
    assert de["equity"][1] == pytest.approx(cap + t.profit) and de["closed"].tolist() == [0, 1, 1]
    assert de["equity"][-1] == pytest.approx(cap + sum(x.profit for x in res.trades) + metrics.open_pnl(res))


def test_daily_equity_last_value_includes_a_final_open_trade():
    bars = bars_at(TIMES, [100, 100, 104, 110, 120, 130])
    res = run(Script({0: lambda c: c.entry("L", LONG)}), bars)
    de = metrics.daily_equity(res)
    assert res.open_trade is not None
    assert de["equity"][-1] == pytest.approx(DEFAULT.initial_capital + metrics.open_pnl(res))


def test_engine_start_skips_earlier_bars_and_starts_flat():
    bars = bars_at(TIMES, [100, 100, 104, 110, 120, 130])
    acts = {0: lambda c: c.entry("A", LONG), 3: lambda c: c.entry("B", LONG), 4: lambda c: c.close_all()}
    full = run(Script(dict(acts)), bars)
    late = run(Script(dict(acts)), bars, start=3)
    assert [t.entry_id for t in full.trades] == ["A"]  # B is ignored while A is open
    assert [t.entry_id for t in late.trades] == ["B"] and late.trades[0].entry_bar == 4
    assert run(Script(dict(acts)), bars, start=0).trades[0].profit == full.trades[0].profit


def test_fold_value_charges_a_market_close_of_an_open_trade():
    bars = bars_at(TIMES, [100, 100, 104, 110, 120, 130])
    res = run(Script({0: lambda c: c.entry("L", LONG)}), bars)
    open_pnl = metrics.open_pnl(res)
    assert validate.fold_value(res, 0) == pytest.approx(open_pnl - 2.01)
    assert validate.fold_value(res, 2) == pytest.approx(open_pnl - 2.01 - 20.0)


# --- guards -----------------------------------------------------------------------------------------------
def test_fold_frame_never_reads_reserved_bars(monkeypatch):
    seen = {}

    def fake(start, end):
        seen["args"] = (start, end)
        return pd.DataFrame({"ts": pd.to_datetime([], utc=True)})

    monkeypatch.setattr(validate, "load_bars", fake)
    validate._W.clear()
    validate._frame()
    validate._W.clear()
    assert seen["args"] == (experiment.DEV_START, "2024-01-01")


def test_cmd_validate_rejects_a_non_development_config(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"strategy": "fair_price_reversal", "variant": "ny", "params": {}, "filters": [],
                             "interval": [None, "2026-10-31"], "source": {"search": "x", "trial": 0}}))
    with pytest.raises(SystemExit, match="development-interval"):
        validate.cmd_validate(str(p))


def test_cmd_validate_rejects_a_search_that_is_not_the_declared_e2():
    # the TPE search chose its trials adaptively from data: re-selecting over it would not be a blind search
    p = validate.ROOT / "strategies" / "configs" / "fair_price_reversal_ny_full_tpe_net1_s1_n300.json"
    if not p.exists():
        pytest.skip("frozen TPE configuration not on file")
    with pytest.raises(SystemExit, match="not the declared E2 search"):
        validate.cmd_validate(str(p))


def test_fold_totals_sum_every_scenario_and_count_positive_years():
    rows = [{"net0": 10.0, "net1": 5.0, "net2": -1.0, "trades1": 3},
            {"net0": -4.0, "net1": -6.0, "net2": -8.0, "trades1": 2}]
    assert validate.fold_totals(rows) == {"net0": 6.0, "net1": -1.0, "net2": -9.0, "trades1": 5, "positive1": 1}
    assert validate.fold_totals(pd.DataFrame(rows)) == validate.fold_totals(rows)


def test_wfo_and_cscv_use_the_profit_factor_tie_break():
    day = _days("2013-01-01", "2015-01-01")
    eq = np.full((2, len(day)), 50_000.0)
    cl = np.tile(np.arange(1, len(day) + 1), (2, 1))
    gp = np.vstack([np.full(len(day), 300.0), np.full(len(day), 200.0)])  # same objective, PF 1.5 vs 2.0
    gl = np.vstack([np.full(len(day), 200.0), np.full(len(day), 100.0)])
    assert validate.wfo_select(day, eq, cl, 50_000.0, years=(2014,))[0]["pick"] == 0
    assert validate.wfo_select(day, eq, cl, 50_000.0, years=(2014,), gp=gp, gl=gl)[0]["pick"] == 1
    pnl = np.zeros((2, 160))
    gpd, gld = np.zeros_like(pnl), np.zeros_like(pnl)
    gpd[0, ::2], gld[0, ::2] = 3.0, 2.0  # config 0: PF 1.5 in every block
    gpd[1, ::2], gld[1, ::2] = 2.0, 1.0  # config 1: PF 2.0, same net
    out = validate.cscv(pnl, np.full(pnl.shape, 5), s=4, gp_daily=gpd, gl_daily=gld)
    assert out["splits"] == 6 and out["skipped"] == 0
