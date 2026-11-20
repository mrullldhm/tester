"""Family-wise check for the RLM dev screen (README step 2): White's Reality Check on all 13,824 versions.

Step 1 (`--collect`): per level unit, every version's daily net P&L on dev (engine only, touch fills) ->
studies/rlm/family_parts/<fingerprint>_<unit>.npy (versions x trading days, float32).
Step 2 (default): t_v = mean / sd * sqrt(days) of each version's daily P&L. Stationary bootstrap of days (mean block
5 days, same resampled days for every version, so correlation between versions is kept), statistic recentred on each
version's own mean (null: no version has positive expectancy). p = share of bootstrap max_v t*_v >= observed max_v t_v,
and the same for the lead version's t. Mean-zero is a generous null: random-entry nulls give PF < 1 (studies/rlm/null).
Run: .venv/bin/python -m studies.rlm.family --collect [--workers 3]; then .venv/bin/python -m studies.rlm.family
"""

import argparse
import itertools
from multiprocessing import get_context

import numpy as np
import pandas as pd

from cltester import topstep
from cltester.config import ROOT
from cltester.data import Bars, load_period
from cltester.engine import backtest
from strategies.rlm import SOURCES, Strategy, candidates, swing_events
from studies.rlm.grid import LEVEL_KEYS, fingerprint

OUT = ROOT / "studies" / "rlm" / "family_parts"
LEAD = {"sig_tf": "1h", "reg": "confirm", "sources": "all", "weight": "flat", "tol": 0.4, "score": 50, "clv": 0.6,
        "entry": "close", "stop": "band", "exit": "r1", "session": "all"}
_G: dict = {}


def versions() -> list[str]:
    return [k for k in Strategy.GRID if k not in LEVEL_KEYS]


def run_unit(unit: dict) -> str:
    df, bars, days, fp = _G["df"], _G["bars"], _G["days"], _G["fp"]
    name = "_".join(str(unit[k]) for k in LEVEL_KEYS)
    path = OUT / f"{fp}_{name}.npy"
    if path.exists():
        return f"skip {name}"
    candidates(df, unit["sig_tf"], unit["reg"], unit["sources"], unit["weight"], float(unit["tol"]))
    g = {k: Strategy.GRID[k] for k in versions()}
    pos = pd.Index(days)
    mat = []
    for vals in itertools.product(*g.values()):
        p = {**unit, **dict(zip(g, vals, strict=True))}
        s = Strategy()
        t = backtest(bars, s.signals(df, p), manage=s.manage)
        row = np.zeros(len(days), dtype=np.float32)
        if len(t):
            by = t.groupby("trading_day")["net"].sum()
            row[pos.get_indexer(pd.to_datetime(by.index))] = by.to_numpy()
        mat.append(row)
    np.save(path.with_suffix(".tmp.npy"), np.array(mat))
    path.with_suffix(".tmp.npy").rename(path)
    return f"done {name}"


def collect(workers: int) -> None:
    OUT.mkdir(exist_ok=True)
    df = load_period("dev")
    for reg in ("lock", "confirm"):
        for tf in SOURCES:
            swing_events(df, tf, reg)
    _G.update(df=df, bars=Bars.from_frame(df), days=pd.DatetimeIndex(topstep.trading_days(df)), fp=fingerprint(df))
    units = [dict(zip(LEVEL_KEYS, v, strict=True)) for v in itertools.product(*(Strategy.GRID[k] for k in LEVEL_KEYS))]
    units.sort(key=lambda u: {"5m": 0, "15m": 1, "1h": 2}[u["sig_tf"]])
    print(len(units), "units", flush=True)
    with get_context("fork").Pool(workers, maxtasksperchild=1) as pool:
        for msg in pool.imap_unordered(run_unit, units):
            print(msg, flush=True)


def stationary_index(n: int, mean_block: float, rng: np.random.Generator) -> np.ndarray:
    idx = np.empty(n, dtype=np.int64)
    idx[0] = rng.integers(n)
    new = rng.random(n) < 1.0 / mean_block
    starts = rng.integers(0, n, n)
    for i in range(1, n):
        idx[i] = starts[i] if new[i] else (idx[i - 1] + 1) % n
    return idx


def check(boots: int, block: float, spa: bool = False) -> None:
    fp = fingerprint(load_period("dev"))
    units = [dict(zip(LEVEL_KEYS, v, strict=True)) for v in itertools.product(*(Strategy.GRID[k] for k in LEVEL_KEYS))]
    labels, mats = [], []
    g = {k: Strategy.GRID[k] for k in versions()}
    for u in units:
        name = "_".join(str(u[k]) for k in LEVEL_KEYS)
        mats.append(np.load(OUT / f"{fp}_{name}.npy"))
        labels += [{**u, **dict(zip(g, vals, strict=True))} for vals in itertools.product(*g.values())]
    x = np.vstack(mats).astype(np.float64)  # versions x days
    n = x.shape[1]
    mu, sd = x.mean(1), x.std(1, ddof=1)
    ok = sd > 0
    t = np.where(ok, mu / np.where(ok, sd, 1) * np.sqrt(n), -np.inf)
    lead = next(i for i, lb in enumerate(labels) if all(lb[k] == v for k, v in LEAD.items()))
    rng = np.random.default_rng(5)
    if spa:  # Hansen SPA (consistent): clearly bad versions keep their own negative mean instead of zero
        keep = t <= -np.sqrt(2 * np.log(np.log(n)))
        xc = x - np.where(keep, 0.0, mu)[:, None]
    else:
        xc = x - mu[:, None]  # recentred: every version has zero expectancy under the null (White)
    mx = np.empty(boots)
    for b in range(boots):
        ix = stationary_index(n, block, rng)
        xb = xc[:, ix]
        tb = np.where(ok, xb.mean(1) / np.where(ok, sd, 1) * np.sqrt(n), -np.inf)
        mx[b] = tb.max()
    top = np.argsort(-t)[:5]
    print(f"{'SPA' if spa else 'White RC'}: family {x.shape[0]} versions x {n} days (dev, in-sample); "
          f"stationary bootstrap {boots}, block {block}")
    print(f"observed max t {t.max():.2f}; lead t {t[lead]:.2f} (rank {int((t > t[lead]).sum()) + 1})")
    q95, q99 = np.quantile(mx, [0.95, 0.99])
    print(f"bootstrap max t: median {np.median(mx):.2f}, 95% {q95:.2f}, 99% {q99:.2f}")
    print(f"p(max t* >= observed max) = {(mx >= t.max()).mean():.4f}; "
          f"p(max t* >= lead t) = {(mx >= t[lead]).mean():.4f}")
    for i in top:
        print(f"  t {t[i]:.2f}", {k: labels[i][k] for k in Strategy.GRID})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--boots", type=int, default=1000)
    ap.add_argument("--block", type=float, default=5.0)
    ap.add_argument("--spa", action="store_true", help="Hansen SPA recentring (post-hoc sensitivity, 2026-11-20)")
    a = ap.parse_args()
    if a.collect:
        collect(a.workers)
    else:
        check(a.boots, a.block, a.spa)


if __name__ == "__main__":
    main()
