"""Apply the declared screen (docs/strategies/rlm/README.md) to grid_dev.csv. In-sample, best of 13,824.

Gate: trades >= 200, PF >= 1.25, years positive (all dev years) >= 70%, pass rate >= 50%, cost/pass <= $500,
both dev halves net > 0, and >= 60% of one-step neighbours (one parameter changed) net > 0.
Run: .venv/bin/python -m studies.rlm.screen [grid csv]
"""

import sys

import pandas as pd

from cltester.config import ROOT
from strategies.rlm import Strategy

KEYS = list(Strategy.GRID)


def neighbours_positive(g: pd.DataFrame) -> pd.Series:
    idx = g.set_index(KEYS)["net"]
    out = []
    for r in g.itertuples(index=False):
        base = {k: getattr(r, k) for k in KEYS}
        nets = []
        for k in KEYS:
            for v in Strategy.GRID[k]:
                if v == base[k]:
                    continue
                key = tuple(v if kk == k else base[kk] for kk in KEYS)
                if key in idx.index:
                    nets.append(idx.loc[key])
        out.append(sum(n > 0 for n in nets) / len(nets) if nets else 0.0)
    return pd.Series(out, index=g.index)


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else ROOT / "studies" / "rlm" / "grid_dev.csv"
    g = pd.read_csv(path)
    g["nb_pos"] = neighbours_positive(g)
    gates = {
        "trades>=200": g.trades >= 200,
        "PF>=1.25": g.pf >= 1.25,
        "years>=70%": g.years_pos_all >= 0.7,
        "pass>=50%": g.pass_rate >= 0.5,
        "cost<=500": g.cost_per_pass <= 500,
        "halves>0": (g.net_h1 > 0) & (g.net_h2 > 0),
        "neighbours>=60%": g.nb_pos >= 0.6,
    }
    allg = pd.concat(gates, axis=1).all(axis=1)
    print(f"versions {len(g)}; net > 0: {(g.net > 0).mean():.1%}; PF median {g.pf.median():.3f}")
    for k, m in gates.items():
        print(f"  {k:<16} {m.sum():>5}")
    print(f"  ALL gates        {allg.sum():>5}")
    cols = KEYS + ["trades", "net", "pf", "win", "years_pos_all", "pass_rate", "cost_per_pass", "net_h1", "net_h2",
                   "nb_pos"]
    with pd.option_context("display.width", 220, "display.max_columns", 30):
        print("\nTop 15 by PF (trades >= 200):")
        print(g[g.trades >= 200].sort_values("pf", ascending=False)[cols].head(15).to_string(index=False))
        print("\nTop 15 by pass rate (trades >= 100):")
        print(g[g.trades >= 100].sort_values("pass_rate", ascending=False)[cols].head(15).to_string(index=False))
        for k in KEYS:
            print(f"\nby {k}: median PF / share net>0 / median trades")
            print(g.groupby(k).agg(pf=("pf", "median"), pos=("net", lambda s: (s > 0).mean()),
                                   trades=("trades", "median")).round(3).to_string())
    g.assign(all_gates=allg).to_csv(str(path).replace(".csv", "_screened.csv"), index=False)


if __name__ == "__main__":
    main()
