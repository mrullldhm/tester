"""Out-of-family RTH test, dev, in-sample. Per-run analysis, PLAN.md amendments 1-2."""
import csv
import math

import numpy as np
import pandas as pd

SKIP = {"purple_levels", "purple_levels_rth", "purple_pa"}
MIN_TRADES, MIN_SIDE, MIN_DEFINED_SHARE = 100, 30, 0.5
BLOCK_DAYS, RESAMPLES, SEED = 20, 2000, 20261118
OUT = "studies/all_strategies_improve/claude/"
ledger = [r for r in csv.DictReader(open("results/ledger.csv")) if r["period"] == "dev" and "through" not in r["params"]]


def mean_se(d: pd.DataFrame) -> tuple[float, float]:
    if len(d) == 0:
        return math.nan, math.nan
    mu = d["gticks"].mean()
    g = d.groupby("trading_day")["gticks"].agg(["sum", "count"])
    days = len(g)
    if days < 2:
        return mu, math.nan
    return mu, math.sqrt(days / (days - 1) * ((g["sum"] - mu * g["count"]) ** 2).sum()) / len(d)


runs, trades = [], []
for strat in sorted({r["strategy"] for r in ledger} - SKIP):
    for h in sorted({r["hash"] for r in ledger if r["strategy"] == strat}):
        try:
            t = pd.read_csv(f"results/{strat}/dev_{h}.csv", usecols=["entry_ts", "gross", "qty", "trading_day"])
        except FileNotFoundError:
            continue
        if len(t) < MIN_TRADES:
            continue
        ct = pd.to_datetime(t["entry_ts"], utc=True).dt.tz_convert("America/Chicago")
        minute = ct.dt.hour * 60 + ct.dt.minute
        t["is_rth"] = (minute >= 510) & (minute < 810)
        t["gticks"] = t["gross"] / (10 * t["qty"])
        mu, se = mean_se(t)
        rth, rth_se = mean_se(t[t.is_rth])
        other, other_se = mean_se(t[~t.is_rth])
        n_rth = int(t.is_rth.sum())
        defined = n_rth >= MIN_SIDE and len(t) - n_rth >= MIN_SIDE
        runs.append(dict(strategy=strat, hash=h, n=len(t), gross_ticks=mu, se=se, lo95=mu - 1.96 * se,
                         hi95=mu + 1.96 * se, n_rth=n_rth, n_other=len(t) - n_rth, defined=defined,
                         rth_ticks=rth, other_ticks=other, diff=rth - other if defined else math.nan,
                         diff_se=math.hypot(rth_se, other_se) if defined else math.nan))
        if defined:
            trades.append(t.assign(run=len(runs) - 1)[["run", "trading_day", "is_rth", "gticks"]])
runs = pd.DataFrame(runs)
runs.round(4).to_csv(OUT + "rth_cross_runs.csv", index=False)


def summarise(g: pd.DataFrame) -> pd.Series:
    d = g[g.defined]
    eligible = len(d) / len(g) >= MIN_DEFINED_SHARE
    return pd.Series(dict(
        runs=len(g), defined_runs=len(d), median_trades=g.n.median(),
        gross_median=g.gross_ticks.median(), gross_min=g.gross_ticks.min(), gross_max=g.gross_ticks.max(),
        all_runs_ci_below_0=bool((g.hi95 < 0).all()), all_runs_ci_above_0=bool((g.lo95 > 0).all()),
        eligible=eligible, diff_median=d["diff"].median() if eligible else math.nan,
        diff_min=d["diff"].min() if eligible else math.nan, diff_max=d["diff"].max() if eligible else math.nan,
        share_defined_rth_better=(d["diff"] > 0).mean() if len(d) else math.nan))


summary = runs.groupby("strategy")[runs.columns.drop("strategy")].apply(summarise)
summary.round(4).to_csv(OUT + "rth_cross.csv")
print(summary.round(2).to_string())

# joint circular block bootstrap over trading days, same days for every run
eligible_strats = list(summary.index[summary.eligible])
tr = pd.concat(trades)
days = np.sort(tr.trading_day.unique())
day_ix = pd.Series(np.arange(len(days)), index=days)
tr["d"] = day_ix[tr.trading_day].to_numpy()
run_ids = sorted(tr.run.unique())
pos = {r: i for i, r in enumerate(run_ids)}
mats = {}
for key, mask in (("rs", tr.is_rth), ("os", ~tr.is_rth)):
    for kind in ("sum", "count"):
        m = np.zeros((len(run_ids), len(days)))
        sub = tr[mask]
        np.add.at(m, (sub.run.map(pos).to_numpy(), sub.d.to_numpy()), sub.gticks.to_numpy() if kind == "sum" else 1.0)
        mats[key + kind[0]] = m
run_strat = runs.loc[run_ids, "strategy"].to_numpy()


def statistic(w: np.ndarray) -> np.ndarray:
    """w: (B, days) day weights -> mean over eligible strategies of median-run RTH - other, per resample."""
    rth = (w @ mats["rss"].T) / (w @ mats["rsc"].T)
    other = (w @ mats["oss"].T) / (w @ mats["osc"].T)
    diff = rth - other
    per_strat = [np.nanmedian(diff[:, run_strat == s], axis=1) for s in eligible_strats]
    return np.nanmean(np.column_stack(per_strat), axis=1)


rng = np.random.default_rng(SEED)
n_days, n_blocks = len(days), math.ceil(len(days) / BLOCK_DAYS)
w = np.zeros((RESAMPLES, n_days))
for b in range(RESAMPLES):
    starts = rng.integers(0, n_days, n_blocks)
    idx = ((starts[:, None] + np.arange(BLOCK_DAYS)) % n_days).ravel()[:n_days]
    np.add.at(w[b], idx, 1.0)
observed = statistic(np.ones((1, n_days)))[0]
boot = statistic(w)
lo, hi = np.percentile(boot, [2.5, 97.5])
votes = summary.loc[eligible_strats, "diff_median"]
print(f"\neligible strategies {len(eligible_strats)}; positive votes {int((votes > 0).sum())}/{len(votes)} (descriptive)")
print(f"mean of median-run RTH - other = {observed:.3f} ticks, block-bootstrap 95% [{lo:.3f}, {hi:.3f}], "
      f"share <= 0 = {(boot <= 0).mean():.4f}")
