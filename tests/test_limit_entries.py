"""Limit execution regressions. Run with python -B -m unittest tests.test_limit_entries."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd

from strategies.fair_price_reversal import FairPriceReversal
from strategies.supertrend_kalman import SupertrendKalman
from strategies.tupa_trade import TupaTrade
from tvtester import engine, optimize, search, validate, experiment, metrics
from tvtester.config import DEFAULT, SLIPPAGE_SCENARIOS
from tvtester.data import Bars
from tvtester.entries import PendingEntry


def bars(rows):
    a = np.asarray(rows, dtype=np.int64)
    n = len(a)
    ts = pd.date_range('2023-03-06 14:00', periods=n, freq='min', tz='UTC')
    return Bars(ts, ts.as_unit('ms').asi8, *a.T, np.ones(n), np.full(n, 'CLJ3'), np.zeros(n, dtype=bool))


def prepared(base, direction=1, signals=(0,), outside=()):
    class Fixture(base):
        def prepare(self, data):
            n = len(data)
            self.bars = data
            self.exits.prepare(data)
            self.pending = PendingEntry()
            self.allow = np.ones(n, dtype=bool)
            sig = np.zeros(n, dtype=np.int8)
            sig[list(signals)] = direction
            if base is FairPriceReversal:
                self.sig = dict(sig=sig, stop=np.full(n, 100 - direction * 10),
                                body_lo=np.full(n, 80), body_up=np.full(n, 120))
                self.mod = np.full(n, self.s.open_minute + 10)
                self.mod[list(outside)] = self.s.flat_minute
            else:
                self.sig = sig
                self.prev = np.zeros(n, dtype=int)
                self.first = np.ones(n, dtype=bool)
                self.in_hours = np.ones(n, dtype=bool)
                self.in_hours[list(outside)] = False
                self.ind = dict(sw_lo=np.full(n, 90), sw_hi=np.full(n, 110),
                                st_dir=np.full(n, -direction), tr_stop=np.full(n, np.nan))
            return np.ones(n, dtype=bool)
    return Fixture(target='rr2') if base is FairPriceReversal else Fixture(hours='ny', rr=2)


class LimitEntries(unittest.TestCase):
    def each(self):
        for cls in (FairPriceReversal, SupertrendKalman):
            for d in (1, -1):
                yield cls, d

    @staticmethod
    def mirror(rows, d):
        return rows if d == 1 else [(200-o, 200-l, 200-h, 200-c) for o,h,l,c in rows]

    def test_waits_for_limit_and_keeps_commission(self):
        rows = [(100,100,100,100), (105,110,103,107), (104,108,100,104), (110,121,109,120)]
        for cls,d in self.each():
            with self.subTest(strategy=cls.__name__, direction=d):
                r=engine.run(prepared(cls,d),bars(self.mirror(rows,d)))
                self.assertEqual(len(r.trades),1)
                t=r.trades[0]
                self.assertEqual((t.entry_bar,t.entry_price,t.exit_price),(2,100,100+d*20))
                self.assertAlmostEqual(t.profit,195.98)

    def test_target_before_fill_cancels_entry_and_bracket(self):
        rows=[(100,100,100,100),(105,120,104,115),(100,101,89,95)]
        for cls,d in self.each():
            r=engine.run(prepared(cls,d),bars(self.mirror(rows,d)))
            self.assertEqual(r.trades,[])
            self.assertIsNone(r.open_trade)

    def test_same_candle_entry_and_target_is_a_real_trade(self):
        rows=[(100,100,100,100),(100,121,99,120)]
        for cls,d in self.each():
            r=engine.run(prepared(cls,d),bars(self.mirror(rows,d)))
            self.assertEqual(len(r.trades),1)
            self.assertEqual(r.trades[0].entry_bar,r.trades[0].exit_bar)

    def test_better_gap_price_is_preserved(self):
        rows=[(100,100,100,100),(98,120,97,119)]
        for cls,d in self.each():
            r=engine.run(prepared(cls,d),bars(self.mirror(rows,d)))
            self.assertEqual(r.trades[0].entry_price,100-2*d)

    def test_session_cancels_pending_order(self):
        rows=[(100,100,100,100),(105,110,103,107),(100,101,99,100)]
        for cls,d in self.each():
            r=engine.run(prepared(cls,d,outside=(1,2)),bars(self.mirror(rows,d)))
            self.assertEqual(r.trades,[])
            self.assertIsNone(r.open_trade)

    def test_roll_cancels_pending_order(self):
        rows=[(100,100,100,100),(105,110,103,107),(100,101,99,100)]
        for cls,d in self.each():
            b=bars(self.mirror(rows,d));b.last_of_contract[1]=True
            r=engine.run(prepared(cls,d),b)
            self.assertEqual(r.trades,[])
            self.assertIsNone(r.open_trade)

    def test_filled_then_closed_state_allows_a_later_signal(self):
        rows=[(100,100,100,100),(100,121,99,100),(100,121,99,120)]
        for cls,d in self.each():
            r=engine.run(prepared(cls,d,signals=(0,1)),bars(self.mirror(rows,d)))
            self.assertEqual(len(r.trades),2)

    def test_tupa_target_expiry_does_not_rearm_same_setup(self):
        class Fixture(TupaTrade):
            def prepare(self,b):
                self.bars=b;self.day=np.ones(len(b));self.win=np.ones(len(b),dtype=bool)
                self.cur_day=None;self.traded=False;self.n_closed=0;self.pend=None;self.trig=False;self.expired=None
                self.m1=SimpleNamespace(at=np.zeros(len(b),dtype=int),n_h=np.ones(len(b),dtype=int))
                return self.win
            def setup(self,i): return (-1,120,150,125,1)
        b=bars([(130,131,129,130),(115,119,99,110),(125,126,124,125),(125,126,99,100)])
        r=engine.run(Fixture(),b)
        self.assertEqual(r.trades,[])
        self.assertIsNone(r.open_trade)

    def test_only_one_baseline_run_in_grid_and_search(self):
        self.assertEqual(SLIPPAGE_SCENARIOS,())
        self.assertEqual(search.SCENARIOS,(0,))
        self.assertEqual(validate.SCENARIOS,(0,))
        self.assertEqual(experiment.OBJECTIVES,{'net0':0})
        b=bars([(100,100,100,100),(100,121,99,120)])
        with patch.object(optimize,'run',wraps=engine.run) as spy:
            out=optimize.stress(lambda **kw:prepared(FairPriceReversal),{},b)
            self.assertEqual(list(out),[0]);self.assertEqual(spy.call_count,1)
        mod=SimpleNamespace(STRATEGY=lambda **kw:prepared(FairPriceReversal))
        with patch.object(search,'_bars',return_value=b), patch.object(search,'run',wraps=engine.run) as spy:
            row=search.evaluate(mod,{'params':{},'filters':[]})
            self.assertEqual(spy.call_count,1)
            self.assertIn('net0',row);self.assertNotIn('net1',row)
            self.assertEqual(search.score(row,'net0')[1],row['net0']+row['open0'])

    def test_baseline_report_and_artifacts_need_no_extra_scenarios(self):
        import json
        import tempfile
        from pathlib import Path
        from tvtester import cli, report
        b=bars([(100,100,100,100),(100,121,99,120)])
        result=engine.run(prepared(FairPriceReversal),b)
        summary=metrics.summary(result)
        grid=pd.DataFrame([{"target":"rr2", **summary["all"], "max_equity_drawdown":summary["max_equity_drawdown"]}])
        mod=SimpleNamespace(TITLE="Synthetic limit report", ABOUT="Synthetic bars only.", GRID={"target":["rr2"]},
                            VARIANTS={"ny":{}}, CONCLUSION="")
        with tempfile.TemporaryDirectory(prefix="limit-report-") as folder:
            root=Path(folder)
            out=root/"results/fixture/ny"
            sums=report.save_variant({0:result},grid,out)
            doc=root/"docs/strategies/fixture";doc.mkdir(parents=True)
            output=("ny",{"target":"rr2"},grid,sums,{0:metrics.trade_frame(result)},[],len(b),str(b.ts[0]),str(b.ts[-1]))
            with patch.object(cli,"ROOT",root), patch.object(report,"ROOT",root):
                path=cli.write_doc(mod,"fixture",[output],1)
            text=Path(path).read_text()
            self.assertIn("Results after commission",text)
            self.assertNotIn("Slippage scenarios",text)
            data=json.loads((out/"summary.json").read_text())
            self.assertEqual(set(data),{"execution_version","slippage_0"})
            self.assertEqual(data["execution_version"],experiment.EXECUTION_VERSION)
            self.assertEqual([p.name for p in out.glob("trades_*.csv")],["trades_slippage0.csv"])

    def test_historical_configuration_is_rejected(self):
        with self.assertRaises(SystemExit): experiment.check_execution({'source':{'objective':'net1'}})
        experiment.check_execution({'execution_version':experiment.EXECUTION_VERSION,'source':{'objective':'net0'}})


if __name__=='__main__': unittest.main()
