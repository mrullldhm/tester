"""Tupa Trade v2 interpretation study: paired main effect of each switch (docs/strategies/tupa_trade_v2/optimize).

For every switch, pair each configuration at its first value with the same configuration at the alternative
(all other parameters equal) and report how often, and by how much, the alternative changes net0 and trades.
Reads only the search's trials.csv (no engine runs, nothing logged). Usage:
    .venv/bin/python tools/tupa_v2_effects.py results/tupa_trade_v2/search/<run_id>/trials.csv
"""

import json
import sys

import pandas as pd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from strategies.tupa_trade_v2 import SWITCHES


def effects(trials: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(paired effect per switch, net0 by t_min/t_rule group)."""
    df = trials[~trials["duplicate"]].copy()
    params = df["config"].map(lambda c: json.loads(c)["params"])
    keys = sorted(params.iloc[0])
    df["key"] = params.map(lambda p: tuple(p[k] for k in keys))
    by_key = dict(zip(df["key"], df.index))
    rows = []
    for sw, (a, b) in SWITCHES.items():
        i = keys.index(sw)
        diffs, dtr = [], []
        for k, idx in by_key.items():
            if k[i] != a:
                continue
            k2 = k[:i] + (b,) + k[i + 1:]
            if k2 in by_key:
                j = by_key[k2]
                diffs.append(df.at[j, "objective"] - df.at[idx, "objective"])
                dtr.append(int(df.at[j, "trades0"]) - int(df.at[idx, "trades0"]))
        s = pd.Series(diffs, dtype=float)
        rows.append({"switch": sw, "alternative": b, "pairs": len(s), "better": int((s > 0).sum()),
                     "share_better": (s > 0).mean() if len(s) else float("nan"), "median_change": s.median(),
                     "mean_change": s.mean(), "min_change": s.min(), "max_change": s.max(),
                     "median_trade_change": pd.Series(dtr).median()})
    group = params.map(lambda p: p["t_min"] + "/" + p["t_rule"])
    by_group = df.assign(group=group).groupby("group")["objective"].agg(["count", "median", "max"])
    return pd.DataFrame(rows), by_group


if __name__ == "__main__":
    t = pd.read_csv(sys.argv[1])
    eff, groups = effects(t)
    pd.set_option("display.width", 200)
    print(eff.to_string(index=False))
    print(groups.to_string())
