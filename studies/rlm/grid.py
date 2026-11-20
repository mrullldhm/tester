"""RLM full-factorial dev screen (docs/strategies/rlm/README.md, trial budget 13,824). Every version once.

Work unit = one level configuration (sig_tf, reg, sources, weight, tol): its candidates are built once, then every
downstream version (score, clv, entry, stop, exit, session) runs through the engine (touch fills, no exit slippage),
metrics, Combine rolling + sequential, and the net of each dev half. One CSV part per unit in studies/rlm/grid_parts/
(resumable); `--merge` joins them into grid_<period>.csv. Every number is in-sample, best of 13,824.
Run: .venv/bin/python -m studies.rlm.grid [--workers 5] [--through 0] [--merge]
"""

import argparse
import hashlib
import itertools
import os
from multiprocessing import get_context

import pandas as pd

from cltester import metrics, topstep
from cltester.config import ROOT
from cltester.data import Bars, load_period
from cltester.engine import Fills, backtest
from strategies.rlm import SOURCES, Strategy, _content_key, candidates, swing_events

OUT = ROOT / "studies" / "rlm"
SPLIT = pd.Timestamp("2016-01-01")
LEVEL_KEYS = ["sig_tf", "reg", "sources", "weight", "tol"]
_G: dict = {}
CODE = ("strategies/rlm.py", "cltester/engine.py", "cltester/swings.py", "cltester/topstep.py", "cltester/metrics.py",
        "cltester/indicators.py", "cltester/config.py", "cltester/data.py", "cltester/strategy.py",
        "studies/rlm/grid.py")


def fingerprint(df: pd.DataFrame) -> str:
    """Hash of every code file the results depend on plus the content of the bars used (timestamps, OHLC,
    contracts): a part from other code, config (fees, periods) or data is never reused or merged (Codex adversarial
    review 2026-11-20)."""
    h = hashlib.sha256()
    for f in CODE:
        h.update((ROOT / f).read_bytes())
    h.update(_content_key(df).encode())
    return h.hexdigest()[:10]


def years_pos(trades: pd.DataFrame, days: list) -> float:
    """Share of the period's calendar years with net > 0; a year without trades is not positive."""
    years = sorted({d.year for d in days})
    if trades.empty:
        return 0.0
    by = trades.groupby(pd.to_datetime(trades["trading_day"]).dt.year)["net"].sum()
    return round(sum(by.get(y, 0.0) > 0 for y in years) / len(years), 3)


def evaluate(trades: pd.DataFrame, days: list) -> dict:
    st = metrics.summary(trades, days)
    if st.get("net", 0.0) > 0:
        cb = topstep.summary(topstep.rolling(trades, days), topstep.sequential(trades, days), days)
    else:  # a losing version cannot pass the screen: skip the Combine simulation (speed); recorded as NaN
        cb = {"pass_rate": float("nan"), "seq_passes": 0, "seq_fails": 0, "seq_cost_per_pass_usd": float("nan")}
    td = pd.to_datetime(trades["trading_day"]) if len(trades) else pd.Series(dtype="datetime64[ns]")
    net = trades["net"] if len(trades) else pd.Series(dtype=float)
    return {"trades": st.get("trades", 0), "net": st.get("net", 0.0), "pf": st.get("profit_factor"),
            "win": st.get("win_rate"), "avg": st.get("avg_trade"), "maxdd": st.get("max_drawdown"),
            "years_pos_all": years_pos(trades, days), "pass_rate": cb["pass_rate"], "seq_passes": cb["seq_passes"],
            "seq_fails": cb["seq_fails"], "cost_per_pass": cb["seq_cost_per_pass_usd"],
            "net_h1": float(net[td < SPLIT].sum()), "net_h2": float(net[td >= SPLIT].sum()),
            "longs": int((trades["side"] == 1).sum()) if len(trades) else 0}


def run_unit(unit: dict) -> str:
    df, bars, days, fills, tag = _G["df"], _G["bars"], _G["days"], _G["fills"], _G["tag"]
    name = "_".join(str(unit[k]) for k in LEVEL_KEYS)
    path = OUT / "grid_parts" / f"{tag}{name}.csv"
    if path.exists():
        return f"skip {name}"
    candidates(df, unit["sig_tf"], unit["reg"], unit["sources"], unit["weight"], float(unit["tol"]))
    g = {k: v for k, v in Strategy.GRID.items() if k not in LEVEL_KEYS}
    rows = []
    for vals in itertools.product(*g.values()):
        p = {**unit, **dict(zip(g, vals, strict=True))}
        s = Strategy()
        trades = backtest(bars, s.signals(df, p), fills, s.manage)
        rows.append({**p, **evaluate(trades, days)})
    tmp = path.with_suffix(".tmp")
    pd.DataFrame(rows).to_csv(tmp, index=False)
    tmp.rename(path)
    return f"done {name}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--through", type=int, default=0)
    ap.add_argument("--workers", type=int, default=min(5, os.cpu_count() or 1))
    ap.add_argument("--only", nargs="*", help="unit filters key=value (e.g. sig_tf=1h)")
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args()
    df = load_period("dev")
    tag = (f"through{a.through}_" if a.through else "") + fingerprint(df) + "_"
    (OUT / "grid_parts").mkdir(exist_ok=True)
    if a.merge:
        parts = sorted((OUT / "grid_parts").glob(f"{tag}*.csv"))
        g = pd.concat([pd.read_csv(q) for q in parts], ignore_index=True)
        want = 1
        for v in Strategy.GRID.values():
            want *= len(v)
        keys = list(Strategy.GRID)
        if len(g) != want or g.duplicated(keys).any():
            raise SystemExit(f"incomplete family: {len(g)} rows, {g.duplicated(keys).sum()} duplicates, want {want}")
        g.to_csv(OUT / f"grid_dev{'_' + tag.rstrip('_') if tag else ''}.csv", index=False)
        print("merged", len(parts), "units", len(g), "rows")
        return
    for reg in ("lock", "confirm"):
        for tf in SOURCES:
            swing_events(df, tf, reg)  # once in the parent; forked workers inherit the cache
    _G.update(df=df, bars=Bars.from_frame(df), days=topstep.trading_days(df), fills=Fills(through=a.through), tag=tag)
    units = [dict(zip(LEVEL_KEYS, v, strict=True)) for v in itertools.product(*(Strategy.GRID[k] for k in LEVEL_KEYS))]
    for f in a.only or []:
        k, v = f.split("=")
        units = [u for u in units if str(u[k]) == v]
    order = {"5m": 0, "15m": 1, "1h": 2}
    units.sort(key=lambda u: order[u["sig_tf"]])  # longest first
    print(f"{len(units)} level units, through={a.through}, workers={a.workers}", flush=True)
    with get_context("fork").Pool(a.workers, maxtasksperchild=1) as pool:
        for msg in pool.imap_unordered(run_unit, units):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
