"""Exit management (breakeven / trailing stop, tvtester/exits.py) through the real strategy on_bar code, on
hand-made bars (prices in ticks). One long (or short) signal at bar 0, market fill at bar 1's open."""

import numpy as np
import pytest

from strategies import fair_price_reversal as fpr
from strategies import supertrend_kalman as sk
from tests.test_engine import make_bars
from tvtester import exits, metrics
from tvtester.config import DEFAULT, ROOT
from tvtester.data import Bars, load_bars
from tvtester.engine import LONG, SHORT, run


class FPR(fpr.FairPriceReversal):
    """Signal at bar 0 (close 100, stop 90 for a long / 110 for a short): R = 10 ticks; inside the session."""

    def __init__(self, d=LONG, at=(0,), **kw):
        super().__init__(**{"target": "rr2", **kw})
        self.d, self.at = d, list(at)

    def prepare(self, bars):
        n = len(bars)
        self.bars = bars
        self.exits.prepare(bars)
        sig = np.zeros(n, dtype=np.int8)
        sig[self.at] = self.d
        stop = np.zeros(n, dtype=np.int64)
        stop[self.at] = bars.c[self.at] - 10 * self.d
        self.sig = {"sig": sig, "stop": stop, "body_up": np.full(n, 130), "body_lo": np.full(n, 70)}
        self.mod = np.full(n, self.s.open_minute + 10)
        self.allow = np.ones(n, dtype=bool)
        return sig != 0


def bars_after(rows, first=(100, 100, 100, 100)):
    return make_bars([first, *rows])


def trade(strategy, rows, props=DEFAULT):
    res = run(strategy, bars_after(rows), props)
    assert len(res.trades) == 1, res.trades
    return res.trades[0]


# --- the rule itself --------------------------------------------------------------------------------------
def test_rnd_is_half_up():
    assert [exits.rnd(x) for x in (2.5, 3.5, 2.49, 0.25 * 10, 0.75 * 10)] == [3, 4, 2, 3, 8]


def test_study_rules_count_and_order():
    r = exits.study_rules()
    assert len(r) == 428 and len(set(r)) == 428
    fam = [x.family() for x in r]
    assert fam[0] == "baseline" and r[0] == exits.ExitRule()
    assert fam[1:22] == ["be_touch"] * 9 + ["be_close"] * 6 + ["be_time"] * 6
    assert {f for f in fam[22:122]} == {f"trail_{t}" for t in exits.TRAIL_STYLES[1:]}
    assert fam[122:422] == ["both"] * 300 and fam[422:] == ["time_exit"] * 6
    counts = {f: fam.count(f) for f in set(fam)}
    assert (counts["trail_frac"], counts["trail_atr"], counts["trail_swing"], counts["trail_step"],
            counts["trail_close"], counts["trail_ema"], counts["trail_sar"]) == (32, 16, 12, 4, 16, 12, 8)


@pytest.mark.parametrize("kw", [dict(be="touch", be_x=0.5, keep_target=False), dict(be="touch"),
                                dict(be_x=0.5), dict(trail="atr"), dict(trail="ema", trail_x=9.5),
                                dict(trail="sar", trail_x=2), dict(trail="step", trail_x=0.5, trail_at=0.5),
                                dict(trail="nope", trail_x=1)])
def test_invalid_rules_refused(kw):
    with pytest.raises(ValueError):
        exits.ExitRule(**kw)


def test_unknown_exit_kwarg_refused():
    with pytest.raises(TypeError):
        fpr.FairPriceReversal(be_at=0.5)


def test_defaults_add_no_params():
    assert fpr.FairPriceReversal().params == fpr.FairPriceReversal(be="none", trail="none", time_exit=0).params
    assert "be" not in sk.SupertrendKalman().params


# --- breakeven (T = 2R = 20 ticks; be_at 0.5 -> trigger at +10) -------------------------------------------
def test_breakeven_moves_stop_from_next_bar():
    # bar1: entry 100, high 111 (+11 >= 10) -> stop to 101 at bar1 close; bar2 falls to 95 -> exit at 101
    t = trade(FPR(be="touch", be_x=0.5, be_offset=1), [(100, 111, 100, 105), (105, 105, 95, 96)])
    assert (t.entry_price, t.exit_bar, t.exit_price, t.exit_reason) == (100, 2, 101, "stop")
    assert t.profit == pytest.approx(10 - 4.02)


def test_breakeven_not_before_trigger():
    # high +9 only: stop stays 90; bar2 low 95 does not fill; bar3 low 89 -> original stop 90
    t = trade(FPR(be="touch", be_x=0.5), [(100, 109, 100, 105), (105, 105, 95, 96), (96, 96, 89, 89)])
    assert (t.exit_bar, t.exit_price) == (3, 90)


def test_breakeven_not_on_the_trigger_bar():
    # bar1 path O-L-H-C: 100, 95, 111, 99 -> no exit on bar1 (the stop moves only at its close); the close 99 is
    # already below the new stop 100 -> triggered stop, fills at the next open 97
    t = trade(FPR(be="touch", be_x=0.5), [(100, 111, 95, 99), (97, 98, 96, 97)])
    assert (t.exit_bar, t.exit_price, t.exit_reason) == (2, 97, "stop")


def test_amended_stop_through_close_is_triggered():
    # close 99 below the new stop 100: triggered when placed, so it fills at the next open even when that open
    # gaps back up to 105 (an ordinary resting stop would not fill at 105)
    t = trade(FPR(be="touch", be_x=0.5), [(100, 111, 95, 99), (105, 106, 104, 105)])
    assert (t.exit_bar, t.exit_price, t.exit_reason) == (2, 105, "stop")


def test_amended_stop_through_close_is_triggered_short():
    t = trade(FPR(d=SHORT, be="touch", be_x=0.5), [(100, 105, 89, 101), (95, 96, 94, 95)])
    assert (t.direction, t.exit_bar, t.exit_price, t.exit_reason) == (SHORT, 2, 95, "stop")


def test_triggered_stop_wins_over_gapped_target():
    # convention (ENGINE.md): next open 125 is past both the triggered stop and the 120 target -> the stop leg
    # fills at the open (with stop slippage), not the limit
    t = trade(FPR(be="touch", be_x=0.5), [(100, 111, 95, 99), (125, 126, 124, 125)], DEFAULT.with_slippage(1))
    assert (t.exit_price, t.exit_reason) == (124, "stop")


def test_breakeven_short_mirror():
    t = trade(FPR(d=SHORT, be="touch", be_x=0.5, be_offset=2), [(100, 100, 89, 95), (95, 104, 95, 103)])
    assert (t.direction, t.exit_bar, t.exit_price) == (SHORT, 2, 98)


def test_breakeven_rounds_trigger_half_up():
    # rr1: T = 10, be_at 0.25 -> 2.5 -> 3 ticks. +2 does not trigger, +3 does
    no = trade(FPR(target="rr1", be="touch", be_x=0.25), [(100, 102, 100, 101), (101, 101, 95, 95), (95, 95, 89, 89)])
    assert no.exit_price == 90
    yes = trade(FPR(target="rr1", be="touch", be_x=0.25), [(100, 103, 100, 101), (101, 101, 95, 95)])
    assert (yes.exit_bar, yes.exit_price) == (2, 100)


def test_breakeven_uses_slipped_fill():
    # 1 tick slippage: entry fills 101; level = 101 + 1 = 102; stop fill 102 - 1 = 101 -> 0 ticks - $4.02
    t = trade(FPR(be="touch", be_x=0.5, be_offset=1), [(100, 112, 100, 106), (106, 106, 95, 96)], DEFAULT.with_slippage(1))
    assert (t.entry_price, t.exit_price) == (101, 101)
    assert t.profit == pytest.approx(-4.02)


def test_target_kept_after_breakeven():
    t = trade(FPR(be="touch", be_x=0.5), [(100, 111, 100, 110), (110, 121, 110, 120)])
    assert (t.exit_price, t.exit_reason) == (120, "limit")


# --- trailing (T = 20; dist 0.25 -> 5 ticks) ---------------------------------------------------------------
def test_trailing_follows_best_and_never_loosens():
    rows = [(100, 108, 100, 107),  # best 108 -> stop 103
            (107, 112, 107, 111),  # best 112 -> stop 107
            (111, 111, 108, 109),  # best stays 112: stop stays 107 (no loosening)
            (109, 109, 105, 105)]  # hits 107
    t = trade(FPR(trail="frac", trail_x=0.25), rows)
    assert (t.exit_bar, t.exit_price) == (4, 107)


def test_trailing_waits_for_start():
    # trail_at 0.5 -> starts at +10. +8 does nothing: bar2 low 99 does not fill (stop 90)
    rows = [(100, 108, 100, 107), (107, 107, 99, 100), (100, 111, 100, 110), (110, 110, 105, 105)]
    t = trade(FPR(trail="frac", trail_at=0.5, trail_x=0.25), rows)
    assert (t.exit_bar, t.exit_price) == (4, 106)


def test_trailing_without_target_lets_it_run():
    rows = [(100, 125, 100, 124), (124, 130, 124, 129), (129, 129, 120, 121)]
    t = trade(FPR(trail="frac", trail_x=0.25, keep_target=False), rows)
    assert (t.exit_bar, t.exit_price) == (3, 125)  # past the 120 target; trailing 130 - 5


def test_trailing_with_target_takes_target():
    t = trade(FPR(trail="frac", trail_x=0.25), [(100, 125, 100, 124)])
    assert (t.exit_bar, t.exit_price, t.exit_reason) == (1, 120, "limit")


def test_both_tightest_wins():
    # +11: BE level 100, trail level 111 - 15 = 96 -> 100 wins; +20 later: trail 105 wins
    rows = [(100, 111, 100, 110), (110, 120, 110, 119), (119, 119, 104, 104)]
    t = trade(FPR(target="rr2", be="touch", be_x=0.5, trail="frac", trail_x=0.75, keep_target=False), rows)
    assert (t.exit_bar, t.exit_price) == (3, 105)


def test_state_resets_between_trades():
    # trade 1: best 115 -> stop 110, hit on bar2. Signal again at bar2 (close 101): trade 2 enters bar3 at 101,
    # best must restart at 104 -> stop 99 (a stale best 115 would put the stop at 110, through the close)
    rows = [(100, 115, 100, 114), (114, 114, 100, 101), (101, 104, 101, 103), (103, 103, 98, 98)]
    res = run(FPR(trail="frac", trail_x=0.25, at=(0, 2)), bars_after(rows))
    assert [(t.entry_bar, t.exit_bar, t.exit_price) for t in res.trades] == [(1, 2, 110), (3, 4, 99)]


# --- other breakeven styles -----------------------------------------------------------------------------
def test_breakeven_close_needs_a_close():
    # high +11 but close +5: no move; next close +10 -> stop 101 (offset 1); then falls
    rows = [(100, 111, 100, 105), (105, 110, 104, 110), (110, 110, 95, 96)]
    t = trade(FPR(be="close", be_x=0.5, be_offset=1), rows)
    assert (t.exit_bar, t.exit_price) == (3, 101)


def test_breakeven_time_needs_age_and_profit():
    # be_x 3 bars, offset 1: bar 3 (age 3) close +1 is not > 1 -> no; bar 4 (age 4) close +3 -> stop 101
    rows = [(100, 103, 99, 101), (101, 102, 100, 101), (101, 102, 100, 101), (101, 104, 100, 103),
            (103, 103, 95, 96)]
    t = trade(FPR(be="time", be_x=3, be_offset=1), rows)
    assert (t.exit_bar, t.exit_price) == (5, 101)


# --- other trailing styles (T = 20) -----------------------------------------------------------------------
def test_trail_step_ratchet():
    # step 0.25T = 5: best +12 -> m = 2 -> stop entry + 5 = 105; several steps in one bar
    t = trade(FPR(trail="step", trail_x=0.25), [(100, 112, 100, 111), (111, 111, 104, 104)])
    assert (t.exit_bar, t.exit_price) == (2, 105)


def test_trail_close_uses_best_close():
    # best close 110 (high 115 ignored) - 5 = 105
    t = trade(FPR(trail="close", trail_x=0.25), [(100, 115, 100, 110), (110, 110, 104, 104)])
    assert (t.exit_bar, t.exit_price) == (2, 105)


def test_trail_atr_chandelier():
    s = FPR(trail="atr", trail_x=2)
    bars = bars_after([(100, 115, 100, 114), (114, 114, 108, 109)])
    s.prepare(bars)
    atr = s.exits.ind["atr"]
    atr[:] = 3.0  # the 1m ATR is only read at bar closes; fix it to a known value
    bars.cache[("exits", "atr", 14)] = atr
    res = run(s, bars)
    assert (res.trades[0].exit_bar, res.trades[0].exit_price) == (2, 109)  # 115 - 2 x 3


def test_trail_ema_only_on_trade_side():
    s = FPR(trail="ema", trail_x=9)
    bars = bars_after([(100, 104, 100, 103), (103, 106, 102, 104), (104, 104, 97, 97)])
    bars.cache[("exits", "ema", 9)] = np.array([0, 105.0, 101.4, 99.0])  # bar1: EMA above the close, ignored
    t = run(s, bars).trades[0]
    assert (t.exit_bar, t.exit_price) == (3, 101)  # bar2: EMA 101.4 below the close 104 -> stop floor = 101


def test_trail_swing_uses_confirmed_pivot():
    s = FPR(trail="swing", trail_x=2)
    bars = bars_after([(100, 104, 100, 103), (103, 106, 102, 105), (105, 106, 101, 101)])
    bars.cache[("exits", "pl", 2)] = np.array([np.nan, 95.0, 102.0, 102.0])
    bars.cache[("exits", "ph", 2)] = np.full(4, np.nan)
    t = run(s, bars).trades[0]
    assert (t.exit_bar, t.exit_price) == (3, 102)  # stop 90 -> 95 (bar1 pivot) -> 102 (bar2 pivot)


def test_time_exit_closes_at_next_open():
    t = trade(FPR(time_exit=2), [(100, 105, 99, 104), (104, 106, 103, 105), (107, 108, 106, 107)])
    assert (t.exit_bar, t.exit_price, t.exit_reason) == (3, 107, "close")


def test_time_exit_without_target():
    t = trade(FPR(time_exit=2, keep_target=False), [(100, 125, 99, 124), (124, 126, 123, 125), (127, 128, 126, 127)])
    assert (t.exit_bar, t.exit_price) == (3, 127)  # the 120 target was removed


# --- indicator transcriptions ------------------------------------------------------------------------------
def test_pivots_tie_rule_and_confirmation_lag():
    low = np.array([5, 4, 3, 3, 4, 5, 6], dtype=float)
    pl = exits.pivots(low, 2, high=False)
    # bar 2 (3) is not < bar 3 (3): no pivot; bar 3 (3) <= older 3, 4 and < newer 4, 5: pivot, known at bar 5
    assert np.isnan(pl[:5]).all() and pl[5] == 3 and np.isnan(pl[6])
    cp = exits.carry(pl)
    assert np.isnan(cp[4]) and cp[5] == 3 and cp[6] == 3


def test_sar_transcription_start():
    h = np.array([10, 11, 12, 13, 12, 9], dtype=float)
    l = np.array([9, 10, 11, 12, 10, 7], dtype=float)
    c = np.array([9.5, 10.5, 11.5, 12.5, 10.5, 7.5])
    s = exits.sar(h, l, c, 0.02, 0.02, 0.2)
    assert np.isnan(s[0])
    assert s[1] == pytest.approx(9.0)  # rising close: below price, seeded at low[0], clamped to low[0]
    assert s[2] == pytest.approx(min(9.0 + 0.02 * (11 - 9.0), 10, 9))  # ep 11 at bar 1, clamp low[1], low[0]
    assert all(s[i] <= l[i] for i in (1, 2, 3))  # below price while the trend is up
    assert s[5] > h[5] or s[5] >= l[5]  # reversal on the drop puts it above


# --- supertrend_kalman: every 1m close, stacked with the ATR trail -----------------------------------------
class ST(sk.SupertrendKalman):
    """Long decision at bar 0 (close 100, swing stop 90, R = 10, rr 2 -> T = 20). Bucket bars every 3 bars."""

    def __init__(self, tr_stop=np.nan, **kw):
        super().__init__(**{"rr": 2, **kw})
        self.tr = tr_stop

    def prepare(self, bars):
        n = len(bars)
        self.bars = bars
        self.exits.prepare(bars)
        self.sig = np.zeros(n, dtype=np.int8)
        self.sig[0] = LONG
        self.first = np.arange(n) % 3 == 0
        self.prev = np.arange(n) // 3
        self.in_hours = np.ones(n, dtype=bool)
        self.allow = np.ones(n, dtype=bool)
        self.ind = {"sw_lo": np.full(n, 90.0), "sw_hi": np.full(n, 110.0), "st_dir": np.full(n, -1),
                    "tr_stop": np.full(n, self.tr, dtype=float)}
        return self.sig != 0


def test_st_breakeven_between_buckets():
    # bar1 is not a bucket bar; BE still moves at its close
    t = trade(ST(be="touch", be_x=0.5), [(100, 111, 100, 110), (110, 110, 95, 96)])
    assert (t.exit_bar, t.exit_price) == (2, 100)


def test_st_atr_trail_and_new_trail_tightest():
    # ATR trail level 102 at bucket bar 3; new trail (0.5 T = 10) from best 115 -> 105: 105 wins
    rows = [(100, 115, 100, 114), (114, 114, 110, 111), (111, 111, 108, 109), (109, 109, 103, 104)]
    t = trade(ST(tr_stop=102.0, exit="trail", trail="frac", trail_x=0.5), rows)
    assert (t.exit_bar, t.exit_price) == (4, 105)
    # ATR level tighter (108 at bucket bar 3, close 109): ATR wins
    t = trade(ST(tr_stop=108.0, exit="trail", trail="frac", trail_x=0.75),
              [(100, 115, 100, 114), (114, 114, 110, 111), (111, 111, 109, 109), (109, 109, 103, 104)])
    assert (t.exit_bar, t.exit_price) == (4, 108)


def test_st_keep_target_off():
    t = trade(ST(trail="frac", trail_x=0.25, keep_target=False), [(100, 125, 100, 124), (124, 124, 115, 116)])
    assert (t.exit_bar, t.exit_price) == (2, 120)


# --- defaults equal feature 1, trade for trade, at 0 / 1 / 2 ticks (needs data) ---------------------------
needs_data = pytest.mark.skipif(not (ROOT / "data" / "cl1").exists(), reason="no bar data")


@needs_data
@pytest.mark.parametrize("mod,variant", [(fpr, "ny"), (fpr, "asia"), (sk, "asia"), (sk, "london"), (sk, "ny")])
def test_defaults_equal_feature1(mod, variant):
    """Trade for trade against the feature-1 trades CSV (FPR rr targets; ST fixed via ny's flip, asia/london
    trail). `all` (fixed exit) is left out for run time; Codex checked all seven baselines on 2023 bars."""
    import pandas as pd

    bars = Bars.from_frame(load_bars(None, "2026-10-28"))
    cols = ["entry_time", "exit_time", "entry_price", "exit_price", "profit", "exit_signal"]
    for k in (0, 1, 2):
        p = {**mod.VARIANTS[variant], **mod.BASELINES[variant]}
        tf = metrics.trade_frame(run(mod.STRATEGY(**p, be="none", trail="none"), bars, DEFAULT.with_slippage(k)))
        ref = pd.read_csv(ROOT / "results" / mod.STRATEGY.name / variant / f"trades_slippage{k}.csv")
        assert len(tf) == len(ref)
        for c in cols:
            a, b = tf[c], ref[c]
            if c.endswith("time"):
                assert (pd.to_datetime(a, utc=True).to_numpy() == pd.to_datetime(b, utc=True).to_numpy()).all(), c
            elif c == "exit_signal":
                assert (a.astype(str).to_numpy() == b.astype(str).to_numpy()).all(), c
            else:
                assert np.allclose(a.astype(float), b.astype(float), atol=1e-6), c
