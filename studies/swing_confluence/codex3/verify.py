import json
from pathlib import Path

import numpy as np
import pandas as pd

from cltester.data import load_period, to_ticks
from cltester.swings import swing_state
from studies.swing_confluence.scan import bh

O = Path(__file__).parent
r = pd.read_parquet(O / "sequences.parquet")
c = pd.read_csv(O / "cells.csv")
old = pd.read_csv(O / "initial_cells.csv")
interim = pd.read_csv(O / "interim_cells.csv")
claude = pd.read_csv(O / "round3_cells.csv")
# All three versions plus every enumerated Claude cell, with p=1 for 7 insufficient cells.
combined = pd.concat(
    [
        old.assign(version="initial"),
        interim.assign(version="interim"),
        c.assign(version="corrected"),
        claude.assign(version="claude"),
    ],
    ignore_index=True,
)
ps = np.r_[combined.p.to_numpy(), np.ones(148 - len(claude))]
combined["bh_all265"] = bh(ps)[: len(combined)]
combined.to_csv(O / "all_cells.csv", index=False)
c["bh_117"] = bh(np.r_[old.p, interim.p, c.p])[len(old) + len(interim) :]
c["bh_cluster_117"] = bh(np.r_[old.pc, interim.pc, c.pc])[len(old) + len(interim) :]
c["bh_all265"] = combined.loc[combined.version == "corrected", "bh_all265"].to_numpy()
gate = (c.n >= 300) & (c.edge.abs() >= 0.03) & (c.e1 * c.e2 > 0) & (c.years_same >= 9)
c["pass_117"] = gate & c.bh_117
c["pass_cluster_117"] = gate & c.bh_cluster_117
c["pass_all265"] = gate & c.bh_all265
c.to_csv(O / "cells.csv", index=False)
df = load_period("dev")
ts = pd.DatetimeIndex(df.ts).as_unit("ns").asi8
h, l, close = (to_ticks(df[k]) for k in ("high", "low", "close"))
checked = []
# Raw bar first passage and fair geometry, 2 deterministic examples per family/base/side.
for _, g in r.groupby(["family", "base", "side"]):
    for row in g.iloc[[0, -1]].itertuples():
        i, j, d = int(row.bar), int(row.end), int(row.side)
        hi, lo = (h, l) if d == 1 else (-l, -h)
        target = np.flatnonzero(hi[i + 1 :] > row.upper)
        stop = np.flatnonzero(lo[i + 1 :] < row.lower)
        a = i + 1 + target[0] if len(target) else len(df)
        b = i + 1 + stop[0] if len(stop) else len(df)
        assert min(a, b) == j and a != b
        assert int(a < b) == row.outcome
        assert abs((d * close[i] - row.lower + 1) / (row.upper - row.lower + 2) - row.fair) < 1e-12
        if row.family.startswith("N_reclaim"):
            assert row.break_bar < row.lh_bar < i
            pt = (
                pd.DatetimeIndex(
                    pd.read_parquet(
                        O / f"state_{row.base}.parquet", columns=[f"{row.base}_{'sh' if d == 1 else 'sl'}_ts"]
                    ).iloc[:, 0]
                )
                .as_unit("ns")
                .asi8
            )
            assert pt[int(row.lh_bar)] > ts[int(row.break_bar)]
        checked.append(
            dict(
                family=row.family,
                base=row.base,
                side=d,
                bar=i,
                end=j,
                ts=str(df.ts.iloc[i]),
                outcome=row.outcome,
                fair=row.fair,
            )
        )
# Prefix checks: early examples ensure owner state already published, full history did not add the point.
prefix = []
for b, g in r[r.family == "M"].groupby("base"):
    for d in (1, -1):
        row = g[g.side == d].iloc[0]
        i = int(row.bar)
        key = "sh" if d == 1 else "sl"
        s = swing_state(df.iloc[: i + 1], b, prev=True, newest=True)
        final = pd.read_parquet(O / f"state_{b}.parquet").iloc[i]
        assert s.iloc[-1][f"{b}_{key}_ts"] == final[f"{b}_{key}_ts"]
        assert s.iloc[-1][f"{b}_{key}"] == final[f"{b}_{key}"]
        prefix.append(dict(base=b, side=d, bar=i))
(O / "verification.json").write_text(
    json.dumps(dict(raw_checks=checked, prefix_checks=prefix, total_BH=265, codex_BH=117), indent=2)
)
print(
    c[["cell", "n", "edge", "e1", "e2", "years_same", "bh_all265", "pass_all265", "pass_cluster_117"]].to_string(
        index=False
    )
)
