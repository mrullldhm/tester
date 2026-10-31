import math

import pandas as pd
import pytest

from tvtester import metrics


def trades(rows):
    return pd.DataFrame(
        {"exit_time": pd.to_datetime([r[0] for r in rows], utc=True), "profit": [r[1] for r in rows]}
    )


TF = trades([
    ("2022-12-31T23:30:00+00:00", 100.0),   # Saturday: week of Monday 2022-12-26, year 2022
    ("2023-01-01T22:59:00+00:00", -40.0),   # Sunday 17:59 New York: still UTC 2023-01-01, week of 2022-12-26
    ("2023-01-02T00:05:00+00:00", 60.0),    # Monday: new week 2023-01-02
    ("2023-01-02T14:00:00+00:00", 0.0),     # break-even: not a win, not a loss
    ("2023-02-15T10:00:00+00:00", -20.0),
])


def test_year_matches_by_year():
    y = metrics.by_year(TF)
    p = metrics.by_period(TF, "year")
    assert list(y.columns) == ["year", "trades", "net_profit", "percent_profitable", "profit_factor"]
    assert y["year"].tolist() == p["period"].tolist() == [2022, 2023]
    pd.testing.assert_frame_equal(y.drop(columns="year"), p.drop(columns="period"))


def test_month_week_day_buckets_use_utc_exit_date():
    assert metrics.by_period(TF, "month")["period"].tolist() == ["2022-12", "2023-01", "2023-02"]
    weeks = metrics.by_period(TF, "week")
    assert weeks["period"].tolist() == ["2022-12-26", "2023-01-02", "2023-02-13"]
    assert weeks["trades"].tolist() == [2, 2, 1]
    days = metrics.by_period(TF, "day")
    assert days["period"].tolist() == ["2022-12-31", "2023-01-01", "2023-01-02", "2023-02-15"]


def test_period_stats():
    w = metrics.by_period(TF, "week").set_index("period")
    first = w.loc["2022-12-26"]
    assert first["net_profit"] == 60.0
    assert first["percent_profitable"] == 50.0
    assert first["profit_factor"] == pytest.approx(100.0 / 40.0)
    second = w.loc["2023-01-02"]
    assert second["percent_profitable"] == 50.0       # the 0.0 trade counts as a trade, not a win
    assert math.isnan(second["profit_factor"])        # no losing trade: undefined, never infinite


@pytest.mark.parametrize("grain", metrics.PERIOD_GRAINS)
def test_every_grain_sums_to_the_whole(grain):
    p = metrics.by_period(TF, grain)
    assert p["trades"].sum() == len(TF)
    assert p["net_profit"].sum() == pytest.approx(TF["profit"].sum())


@pytest.mark.parametrize("grain", metrics.PERIOD_GRAINS)
def test_empty_trade_list(grain):
    out = metrics.by_period(TF.iloc[0:0], grain)
    assert out.empty
    assert list(out.columns) == ["period", "trades", "net_profit", "percent_profitable", "profit_factor"]


def test_unknown_grain_fails():
    with pytest.raises(ValueError, match="unknown period grain"):
        metrics.by_period(TF, "quarter")
    with pytest.raises(ValueError, match="unknown period grain"):
        metrics.by_period(TF.iloc[0:0], "quarter")
