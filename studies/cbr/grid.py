"""CBR full-factorial screen (docs/strategies/cbr/README.md, trial budget 1,728). Every version once on one period.

Per version: engine backtest (touch fills, no exit slippage), strategy day_rules, metrics, Combine rolling +
sequential, net of each dev half (2010-06..2015, 2016..2021). All rows kept in studies/cbr/grid_<period>.csv.
Every number is in-sample and best of 1,728.
Run: .venv/bin/python -m studies.cbr.grid [--period dev] [--through 0] [--workers 8]
"""

import argparse
import itertools
import os
from multiprocessing import get_context

import pandas as pd

from cltester import metrics, topstep
from cltester.config import ROOT
from cltester.data import Bars, load_period
from cltester.engine import Fills, backtest
from strategies.cbr import Strategy, candidates

OUT = ROOT / "studies" / "cbr"
SPLIT = pd.Timestamp("2016-01-01")
_G: dict = {}


def _years_pos(trades: pd.DataFrame, days: list) -> float:
    """Share of the period's calendar years with net > 0; a year without trades is not positive (Codex 2026-11-19)."""
    years = sorted({d.year for d in days})
    if trades.empty:
        return 0.0
    by = trades.groupby(pd.to_datetime(trades["trading_day"]).dt.year)["net"].sum()
    return round(sum(by.get(y, 0.0) > 0 for y in years) / len(years), 3)


def run_one(p: dict) -> dict:
    df, bars, days, fills = _G["df"], _G["bars"], _G["days"], _G["fills"]
    s = Strategy()
    trades = s.day_rules(backtest(bars, s.signals(df, p), fills), p)
    st = metrics.summary(trades, days)
    cb = topstep.summary(topstep.rolling(trades, days), topstep.sequential(trades, days), days)
    td = pd.to_datetime(trades["trading_day"]) if len(trades) else pd.Series(dtype="datetime64[ns]")
    net = trades["net"] if len(trades) else pd.Series(dtype=float)
    return {**p, "trades": st.get("trades", 0), "net": st.get("net", 0.0), "pf": st.get("profit_factor"),
            "win": st.get("win_rate"), "avg": st.get("avg_trade"), "maxdd": st.get("max_drawdown"),
            "years_pos": st.get("years_positive"), "years_pos_all": _years_pos(trades, days),
            "pass_rate": cb["pass_rate"], "seq_passes": cb["seq_passes"],
            "seq_fails": cb["seq_fails"], "cost_per_pass": cb["seq_cost_per_pass_usd"],
            "net_h1": float(net[td < SPLIT].sum()), "net_h2": float(net[td >= SPLIT].sum()),
            "longs": int((trades["side"] == 1).sum()) if len(trades) else 0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default="dev", choices=["dev"])  # screen is dev-only by protocol
    ap.add_argument("--through", type=int, default=0)
    ap.add_argument("--window", nargs="*", help="only these windows")
    ap.add_argument("--shift", default="t3", choices=["t3", "any"])
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    a = ap.parse_args()
    df = load_period(a.period)
    candidates(df)  # build once in the parent; forked workers inherit the cache
    _G.update(df=df, bars=Bars.from_frame(df), days=topstep.trading_days(df), fills=Fills(through=a.through))
    g = {**Strategy.GRID, **({"window": a.window} if a.window else {})}
    combos = [{**dict(zip(g, v, strict=True)), "shift": a.shift} for v in itertools.product(*g.values())]
    print(f"{len(combos)} versions on {a.period}, through={a.through}, workers={a.workers}", flush=True)
    with get_context("fork").Pool(a.workers) as pool:
        rows = []
        for k, r in enumerate(pool.imap(run_one, combos, chunksize=8)):
            rows.append(r)
            if k % 100 == 0:
                print(k, flush=True)
    tag = (f"_through{a.through}" if a.through else "") + (f"_{a.shift}" if a.shift != "t3" else "") \
        + ("_" + "-".join(a.window) if a.window else "")
    pd.DataFrame(rows).to_csv(OUT / f"grid_{a.period}{tag}.csv", index=False)
    print("done", len(rows))


if __name__ == "__main__":
    main()
