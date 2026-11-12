import numpy as np
import pandas as pd
import pytest

from cltester.config import Combine
from cltester.topstep import _by_day, rolling, run_attempt, sequential, subscription_cost, summary

DAYS = list(pd.date_range("2024-01-01", periods=10, freq="B"))


def trades(rows):
    """rows of (day index, net, mae)"""
    return pd.DataFrame([{"trading_day": DAYS[d], "net": n, "mae": m, "qty": 1} for d, n, m in rows])


def attempt(rows, rules=None):
    rules = rules or Combine()
    return run_attempt(_by_day(trades(rows), rules), DAYS, 0, rules)


def test_pass_needs_target_and_consistency():
    a = attempt([(0, 1600, -10), (1, 1450, -10)])  # 3,050 profit, best day 1,600 <= 55%
    assert (a.outcome, a.days) == ("pass", 2)
    a = attempt([(0, 2000, -10), (1, 1100, -10)])  # 3,100 but best day 2,000 needs 3,637
    assert a.outcome == "open"
    a = attempt([(0, 2000, -10), (1, 1100, -10), (2, 600, -10)])  # 3,700 >= 3,636.4
    assert (a.outcome, a.days) == ("pass", 3)


def test_intraday_mae_fails_account():
    a = attempt([(0, 500, -10), (1, -100, -1999)])
    assert a.outcome == "open"  # MLL trailed to 48,500; 50,500 - 1,999 = 48,501 survives
    a = attempt([(0, 500, -10), (1, -100, -2000)])
    assert (a.outcome, a.days) == ("fail", 2)
    a = attempt([(0, -100, -2000)])
    assert (a.outcome, a.days) == ("fail", 1)


def test_mll_trails_eod_and_locks():
    # day 0 +1,500 -> MLL 49,500; day 1 an open loss of 2,000 from 51,500 touches it
    a = attempt([(0, 1500, -10), (1, 0, -2000)])
    assert (a.outcome, a.days) == ("fail", 2)
    # lock: MLL never above 50,000 even after a 2,900 EOD gain
    rules = Combine(profit_target=10_000)
    a = run_attempt(_by_day(trades([(0, 1600, -10), (1, 1300, -10), (2, 0, -2899)]), rules), DAYS, 0, rules)
    assert a.outcome == "open"  # 52,900 - 2,899 = 50,001 > 50,000


def test_daily_loss_limit_stops_day_not_account():
    rules = Combine(daily_loss=1000)
    a = run_attempt(_by_day(trades([(0, -800, -900), (0, -300, -1200), (0, 500, -10)]), rules), DAYS, 0, rules)
    assert a.outcome == "open" and a.profit == pytest.approx(-1000)  # DLL at 49,000 sits above MLL 48,000
    a = run_attempt(_by_day(trades([(0, 1500, -10), (1, 0, -2500)]), rules), DAYS, 0, rules)
    assert a.outcome == "open"  # MLL 49,500 below DLL level 50,500: DLL stops the day first


def test_contract_cap():
    t = trades([(0, 10, -1)])
    t["qty"] = 6
    with pytest.raises(ValueError):
        _by_day(t, Combine())


def test_sequential_restarts_after_fail():
    s = sequential(trades([(0, -100, -2000), (1, 1600, -10), (2, 1450, -10)]), DAYS)
    assert list(s["outcome"]) == ["fail", "pass", "open"]


def path_trade(day, opens, worsts, net):
    return {"trading_day": DAYS[day], "net": net, "mae": min(worsts), "qty": 1,
            "path": (np.array(opens, float), np.array(worsts, float))}


def test_gap_through_both_limits_fails_even_with_dll():
    rules = Combine(daily_loss=1000)
    t = pd.DataFrame([path_trade(0, [0, 50, -3004], [-20, -100, -3004], -3004)])
    a = run_attempt(_by_day(t, rules), DAYS, 0, rules)
    assert a.outcome == "fail"


def test_gap_past_dll_liquidates_at_open_price():
    rules = Combine(daily_loss=1000)
    t = pd.DataFrame([path_trade(0, [0, -1500], [-20, -1600], -1600), path_trade(0, [0], [0], 500)])
    a = run_attempt(_by_day(t, rules), DAYS, 0, rules)
    assert a.outcome == "open" and a.profit == pytest.approx(-1500)  # gap to -1,500, not the -1,000 limit


def test_intrabar_move_liquidates_at_dll_level():
    rules = Combine(daily_loss=1000)
    t = pd.DataFrame([path_trade(0, [0, -200], [-20, -2500], -2500)])
    a = run_attempt(_by_day(t, rules), DAYS, 0, rules)
    assert a.outcome == "open" and a.profit == pytest.approx(-1000)


def test_short_pass_pays_a_full_month():
    s = sequential(trades([(0, 1600, -10), (1, 1450, -10)]), DAYS)
    assert subscription_cost(s.iloc[:1], DAYS[-1]) == 49.0  # a 2-day pass still pays one month
    assert subscription_cost(s, DAYS[-1]) == 98.0  # the next account, still open at data end, is paid too


def test_each_pass_starts_a_new_subscription_and_fails_cost_resets():
    days = list(pd.date_range("2024-01-01", periods=80, freq="B"))
    rows = [(0, -100, -2000), (1, 1600, -10), (2, 1450, -10), (40, 1600, -10), (41, 1450, -10)]
    t = pd.DataFrame([{"trading_day": days[d], "net": n, "mae": m, "qty": 1} for d, n, m in rows])
    s = sequential(t, days)
    assert list(s["outcome"]) == ["fail", "pass", "pass", "open"]
    # sub 1: day 0..2 -> 1 month + 1 reset; sub 2: day 3..41 (8 weeks) -> 2 months; sub 3: day 42..79 -> 2 months
    assert subscription_cost(s, days[-1]) == 49 + 49 + 2 * 49 + 2 * 49


def test_empty_period_has_stable_schema():
    t = trades([])
    r, s = rolling(t, []), sequential(t, [])
    assert list(r.columns) == list(s.columns) and "outcome" in r.columns
    assert summary(r, s, [])["rolling_attempts"] == 0
