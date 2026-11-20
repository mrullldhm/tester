"""RLM session / hour / daylight-saving test (declared in docs/strategies/rlm/README.md before the run).

1. The frozen lead with 58 signal windows on three clocks (ct = exchange candle number, myt = Malaysia wall clock,
   ldn = London clock): dev gates, halves, White Reality Check over the 58.
2. Clock attribution on all-hours trades (lead, and lead with score 0): leave-one-year-out prediction of each trade's
   R from the other years' hour means, keyed by exchange candle vs Malaysia hour; day-block bootstrap CI of the
   error difference; and per exchange candle, mean R in US summer vs US winter.
Dev only, in-sample. Run: .venv/bin/python -m studies.rlm.sessions > studies/rlm/sessions_dev.txt
"""

import numpy as np
import pandas as pd

from cltester import topstep
from cltester.config import ROOT, TICK_VALUE
from cltester.data import Bars, load_period
from cltester.engine import backtest
from strategies.rlm import CLOCKS, Strategy
from studies.rlm.family import stationary_index
from studies.rlm.grid import evaluate

OUT = ROOT / "studies" / "rlm"
LEAD = {"sig_tf": "1h", "reg": "confirm", "sources": "all", "weight": "flat", "tol": 0.4, "score": 50, "clv": 0.6,
        "entry": "close", "stop": "band", "exit": "r1", "session": "all"}
WINDOWS = (["ct:17-01", "ct:02-06", "ct:07-10", "ct:11-14", "ct:02-10", "ct:02-14"]
           + [f"ct:{h:02d}-{h:02d}" for h in [*range(17, 24), *range(0, 16)]]
           + ["myt:07-15", "myt:16-20", "myt:21-00", "myt:01-04"]
           + [f"myt:{h:02d}-{h:02d}" for h in range(24)]
           + ["ldn:08-12"])
GATES = {"trades": 200, "pf": 1.25, "years_pos_all": 0.7, "pass_rate": 0.5, "cost_per_pass": 500}


def run(df, bars, days, p):
    s = Strategy()
    o = s.orders(df, p).set_index("bar")
    t = backtest(bars, s.signals(df, p), manage=s.manage)
    t = t.drop(columns="path").join(o[["c_open", "R"]], on="signal_bar")
    return t


def daily(t, days):
    row = np.zeros(len(days))
    if len(t):
        by = t.groupby("trading_day")["net"].sum()
        row[pd.Index(days).get_indexer(pd.to_datetime(by.index))] = by.to_numpy()
    return row


def reality_check(x: np.ndarray, boots: int = 2000, block: float = 5.0) -> tuple[np.ndarray, np.ndarray]:
    n = x.shape[1]
    mu, sd = x.mean(1), x.std(1, ddof=1)
    ok = sd > 0
    t = np.where(ok, mu / np.where(ok, sd, 1) * np.sqrt(n), -np.inf)
    rng = np.random.default_rng(9)
    xc = x - mu[:, None]
    mx = np.array([np.where(ok, xc[:, ix].mean(1) / np.where(ok, sd, 1) * np.sqrt(n), -np.inf).max()
                   for ix in (stationary_index(n, block, rng) for _ in range(boots))])
    return t, mx


def attribution(t: pd.DataFrame, label: str, rng: np.random.Generator) -> None:
    t = t.copy()
    op = pd.DatetimeIndex(t["c_open"])
    t["ct"] = op.tz_convert(CLOCKS["ct"]).hour
    t["myt"] = op.tz_convert(CLOCKS["myt"]).hour
    t["summer"] = op.tz_convert(CLOCKS["ct"]).strftime("%z") == "-0500"  # CDT
    t["R"] = t["net"] / (t["R"] * TICK_VALUE)
    t["year"] = pd.to_datetime(t["trading_day"]).dt.year
    err = {}
    for key in ("ct", "myt"):
        pred = np.empty(len(t))
        for y in t["year"].unique():  # leave one year out: hour means from the other years
            tr, te = t["year"] != y, t["year"] == y
            means = t[tr].groupby(key)["R"].mean()
            pred[te.to_numpy()] = t.loc[te, key].map(means).fillna(t.loc[tr, "R"].mean()).to_numpy()
        err[key] = (t["R"].to_numpy() - pred) ** 2
    d = err["ct"] - err["myt"]  # < 0: the exchange candle predicts better
    day = t["trading_day"].to_numpy()
    by = pd.DataFrame({"d": d, "day": day}).groupby("day")["d"].agg(["sum", "count"])
    bs = [by.iloc[rng.integers(0, len(by), len(by))].pipe(lambda b: b["sum"].sum() / b["count"].sum())
          for _ in range(2000)]
    print(f"\n[{label}] {len(t)} trades, all hours. Leave-one-year-out squared error of R, by hour key:")
    print(f"  exchange candle (ct) {err['ct'].mean():.4f} | Malaysia hour (myt) {err['myt'].mean():.4f} | "
          f"ct - myt {d.mean():+.5f}, day-bootstrap 90% [{np.quantile(bs, 0.05):+.5f}, {np.quantile(bs, 0.95):+.5f}]"
          "  (negative = the exchange candle explains better)")
    print(f"  US summer trades {t['summer'].sum()}, winter {(~t['summer']).sum()}")
    tab = t.pivot_table(index="ct", columns="summer", values="R", aggfunc=["mean", "count"])
    tab.columns = [f"{a}_{'summer' if b else 'winter'}" for a, b in tab.columns]
    order = [*range(17, 24), *range(0, 16)]
    tab = tab.reindex([h for h in order if h in tab.index])
    tab.insert(0, "candle#", [order.index(h) + 1 for h in tab.index])
    tab.insert(1, "myt_summer", [(h + 13) % 24 for h in tab.index])
    tab.insert(2, "myt_winter", [(h + 14) % 24 for h in tab.index])
    s, w = tab["mean_summer"], tab["mean_winter"]
    print("  mean R per exchange candle, US summer vs winter (Malaysia open hour shown for each season):")
    print(tab.round(3).to_string())
    same = np.corrcoef(s, w)[0, 1]
    shifted = np.corrcoef(s.to_numpy()[1:], w.to_numpy()[:-1])[0, 1]  # winter profile one candle later in summer
    print(f"  corr(summer, winter) same candle {same:+.2f} | summer candle k vs winter candle k-1 "
          f"(= same Malaysia hour) {shifted:+.2f}")


def main() -> None:
    df = load_period("dev")
    bars, days = Bars.from_frame(df), topstep.trading_days(df)
    rows, mats = [], []
    for w in ["all", *WINDOWS]:
        p = {**LEAD, "session": w}
        t = run(df, bars, days, p)
        r = {"window": w, **evaluate(t, days)}
        rows.append(r)
        mats.append(daily(t, days))
        if w == "all":
            base = t
    g = pd.DataFrame(rows)
    gate = ((g.trades >= GATES["trades"]) & (g.pf >= GATES["pf"]) & (g.years_pos_all >= GATES["years_pos_all"])
            & (g.pass_rate >= GATES["pass_rate"]) & (g.cost_per_pass <= GATES["cost_per_pass"])
            & (g.net_h1 > 0) & (g.net_h2 > 0))
    g["gates"] = gate
    tstat, mx = reality_check(np.array(mats[1:]))
    g["t"] = np.r_[np.nan, tstat]
    g["rc_p"] = np.r_[np.nan, [(mx >= x).mean() for x in tstat]]
    g.to_csv(OUT / "sessions_dev.csv", index=False)
    cols = ["window", "trades", "net", "pf", "win", "years_pos_all", "pass_rate", "cost_per_pass", "net_h1",
            "net_h2", "t", "rc_p", "gates"]
    print("RLM lead by signal window (dev 2010-06..2021, in-sample; 58 windows declared, total trials 13,882)")
    print(f"White RC over the 58 windows: bootstrap max t median {np.median(mx):.2f}, 95% {np.quantile(mx, .95):.2f}")
    with pd.option_context("display.width", 220, "display.max_rows", 100):
        print(g[cols].round(3).to_string(index=False))
    rng = np.random.default_rng(3)
    attribution(base, "lead", rng)
    attribution(run(df, bars, days, {**LEAD, "score": 0}), "lead with score 0", rng)


if __name__ == "__main__":
    main()
