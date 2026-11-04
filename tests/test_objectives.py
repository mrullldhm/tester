import math
import unittest

import numpy as np
import pandas as pd

from tvtester import metrics
from tvtester.data import Bars
from tvtester.engine import LONG, SHORT, run
from tvtester.objectives import OBJECTIVES, rank_metric, selection, trade_metrics
from tvtester.strategy import Strategy


class Script(Strategy):
    def __init__(self, actions):
        super().__init__()
        self.actions = actions

    def prepare(self, bars):
        return np.ones(len(bars), dtype=bool)

    def on_bar(self, ctx, i):
        if i in self.actions:
            self.actions[i](ctx)


def bars(values):
    a = np.asarray(values, dtype=np.int64)
    n = len(a)
    ts = pd.date_range("2024-01-01", periods=n, freq="min", tz="UTC")
    return Bars(
        ts,
        ts.as_unit("ms").asi8,
        *a.T,
        np.ones(n),
        np.array(["CLG4"] * n),
        np.zeros(n, dtype=bool),
    )


def frame(profits, rs=None):
    return pd.DataFrame(
        {
            "profit": profits,
            "drawdown": [10] * len(profits),
            "run_up": [20] * len(profits),
            "r_multiple": rs if rs is not None else [np.nan] * len(profits),
        }
    )


class MetricChecks(unittest.TestCase):
    def test_known_trade_distribution(self):
        s = trade_metrics(
            frame(
                [200, -100, -50, 0, -20, -30, -40, 300],
                [2, -1, -0.5, 0, -0.2, -0.3, -0.4, 3],
            )
        )
        self.assertEqual(s["expectancy"], 32.5)
        self.assertAlmostEqual(s["payoff_ratio"], 250 / 48)
        self.assertEqual(s["max_consecutive_losses"], 3)
        self.assertAlmostEqual(s["r_multiple"], 0.325)
        self.assertEqual(s["mae"], 10)
        self.assertEqual(s["mfe"], 20)
        self.assertAlmostEqual(
            s["risk_of_ruin"],
            100
            * math.exp(
                -2 * 32.5 * 25000 / np.var([200, -100, -50, 0, -20, -30, -40, 300])
            ),
        )

    def test_zero_activity_and_missing_risk(self):
        s = trade_metrics(frame([]))
        self.assertTrue(
            all(
                s[k] is None
                for k in [
                    "expectancy",
                    "payoff_ratio",
                    "r_multiple",
                    "mae",
                    "mfe",
                    "risk_of_ruin",
                    "max_consecutive_losses",
                ]
            )
        )
        s = trade_metrics(frame([10, -5], [1, np.nan]))
        self.assertIsNone(s["r_multiple"])
        self.assertEqual(s["r_valid_trades"], 1)
        self.assertIsNone(trade_metrics(frame([10, 20]))["payoff_ratio"])

    def test_ruin_degenerate_and_negative_edge(self):
        self.assertEqual(trade_metrics(frame([-1, 1]))["risk_of_ruin"], 100)
        self.assertEqual(trade_metrics(frame([-1, -1]))["risk_of_ruin"], 100)
        self.assertEqual(trade_metrics(frame([1, 1]))["risk_of_ruin"], 0)
        self.assertEqual(trade_metrics(frame([0, 0]))["risk_of_ruin"], 0)
        self.assertIsNone(trade_metrics(frame([1]))["risk_of_ruin"])

    def test_all_directions_eligibility_and_ties(self):
        rows = []
        for order, value in [(1, 1), (2, 2), (3, 0)]:
            row = {o.key: value for o in OBJECTIVES}
            row.update(
                order=order,
                net_profit=value,
                profit_factor=value,
                total_closed_trades=40 if order < 3 else 0,
                risk_of_ruin_log=-3 + value,
            )
            rows.append(row)
        grid = pd.DataFrame(rows)
        for o in OBJECTIVES:
            self.assertEqual(
                int(rank_metric(grid, o.key).iloc[0]["order"]),
                1 if o.direction == "min" else 2,
                o.key,
            )
        self.assertEqual(len(selection(grid, [])["winners"]), 13)
        grid.loc[1, "net_profit"] = 1
        grid.loc[1, "profit_factor"] = 1
        self.assertEqual(int(rank_metric(grid, "net_profit").iloc[0]["order"]), 1)
        grid.loc[0, "profit_factor"] = None
        self.assertEqual(int(rank_metric(grid, "profit_factor").iloc[0]["order"]), 2)
        self.assertTrue(rank_metric(grid, "net_profit", 100).empty)

    def test_initial_risk_and_exposed_path_long_and_short(self):
        for d in (LONG, SHORT):
            # Entry gaps in our favor. Actual risk is 5 ticks, not the signal's 10 ticks.
            values = (
                [(100, 100, 100, 100), (95, 96, 94, 95), (95, 96, 90, 95)]
                if d == LONG
                else [(100, 100, 100, 100), (105, 106, 104, 105), (105, 110, 104, 105)]
            )
            stop = 90 if d == LONG else 110
            res = run(
                Script(
                    {
                        0: lambda c, d=d, stop=stop: (
                            c.entry("E", d, limit=100),
                            c.exit("X", "E", stop=stop),
                        )
                    }
                ),
                bars(values),
            )
            t = res.trades[0]
            self.assertEqual(t.initial_risk_ticks, 5)
            tf = metrics.trade_frame(res)
            self.assertEqual(tf.iloc[0]["initial_risk"], 50)
            self.assertAlmostEqual(tf.iloc[0]["r_multiple"], -54.02 / 50)

    def test_intrabar_excursions_exclude_before_fill_and_after_exit(self):
        # O-H-L-C: high 104 before long limit fill at 100; low 90 after exit at 97.
        res = run(
            Script(
                {
                    0: lambda c: (
                        c.entry("E", LONG, limit=100),
                        c.exit("X", "E", stop=97),
                    )
                }
            ),
            bars([(102, 102, 102, 102), (102, 104, 90, 100)]),
        )
        tf = metrics.trade_frame(res)
        self.assertEqual(tf.iloc[0]["run_up"], 0)
        self.assertEqual(tf.iloc[0]["drawdown"], 30)

    def test_risk_is_frozen_when_stop_moves(self):
        res = run(
            Script(
                {
                    0: lambda c: (c.entry("E", LONG), c.exit("X", "E", loss=10)),
                    1: lambda c: c.exit("X", "E", stop=99),
                    2: lambda c: c.close_all(),
                }
            ),
            bars([(100, 100, 100, 100)] * 4),
        )
        self.assertEqual(res.trades[0].initial_risk_ticks, 10)

    def test_ruin_underflow_does_not_change_ranking(self):
        grid = pd.DataFrame(
            [
                {
                    "order": i,
                    "net_profit": 100 - i,
                    "profit_factor": 1,
                    "total_closed_trades": 30,
                    "risk_of_ruin": 0,
                    "risk_of_ruin_log": -1000 * i,
                }
                for i in [1, 2]
            ]
        )
        self.assertEqual(int(rank_metric(grid, "risk_of_ruin").iloc[0]["order"]), 2)

    def test_nonfinite_secondary_values_are_serializable_and_ineligible(self):
        import json

        grid = pd.DataFrame(
            [
                {
                    "order": 1,
                    "net_profit": 100,
                    "profit_factor": 1.1,
                    "total_closed_trades": 30,
                    "sharpe_ratio": math.inf,
                    "r_consistency": math.nan,
                }
            ]
        )
        selected = selection(grid, [])
        self.assertIsNone(selected["winners"]["sharpe_ratio"])
        self.assertIsNone(selected["winners"]["net_profit"]["metrics"]["sharpe_ratio"])
        json.dumps(selected, allow_nan=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
