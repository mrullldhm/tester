"""Read-only reproduction of Claude's source, outputs redirected inside codex3."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

import studies.swing_confluence.round3 as r3
from cltester.data import load_period
from cltester.swings import build_candles

O = Path(__file__).parent
original_read = pd.read_parquet
r3.PATH = O / "reproduction.parquet"


def redirected(path, *a, **kw):
    return original_read("data/studies/swing_confluence_dev.parquet" if path == r3.PATH else path, *a, **kw)


r3.pd.read_parquet = redirected
r3.main()
r3.pd.read_parquet = original_read
saved = pd.read_csv("data/studies/round3_cells.csv")
new = pd.read_csv(O / "round3_cells.csv")
diff = {k: float((saved[k] - new[k]).abs().max()) for k in ["n", "edge", "e1", "e2", "z"]}
df = load_period("dev")
e = original_read("data/studies/swing_confluence_dev.parquet")
e = e[(e.outcome >= 0) & (~e["roll"]) & e.fair.notna() & (e.leg >= 6)].reset_index(drop=True)
f = r3.bar_features(df)
ts = pd.DatetimeIndex(df.ts).as_unit("ns").asi8
first = np.searchsorted(ts, pd.DatetimeIndex(e.pt_ts).as_unit("ns").asi8)
i = e.bar.to_numpy()
before = np.maximum(first - 1, 0)
side = e.side.to_numpy()
ev = e.price.to_numpy()
lvl = np.where(side == 1, f["pdl"][first], f["pdh"][first])
prior = np.where(side == 1, f["day_lo"][before] < lvl, f["day_hi"][before] > lvl)
prior &= f["day"][before] == f["day"][first]
now = np.where(side == 1, ev < lvl, ev > lvl)
negative = (lvl < 0) & (f["day"][first] > 0) & (f["day"][first] == f["day"][i])
# -1 is the missing sentinel, a valid negative price is not missing.
neg = e[negative].assign(level=lvl[negative], first_take=(now & ~prior)[negative])
neg[["base", "side", "bar", "ts", "price", "level", "first_take"]].to_csv(O / "negative_pdh_pdl.csv", index=False)
# Quantify completed bars included as 'forming' in H2, using source feature groups.

closed = {}
for t in ["15m", "1h", "4h", "1d"]:
    cd = build_candles(df, t)
    cid = np.searchsorted(cd.first, i, side="right") - 1
    mask = e.base.map(r3.ORDER.index).to_numpy() < r3.ORDER.index(t)
    closed[t] = dict(events=int(mask.sum()), already_complete=int(((cd.avail[cid] <= i) & mask).sum()))
# H1 expansion does not enforce alternating HH-HL-HH-LL timestamp order.
orders = {}
for b in r3.ORDER[:4]:
    g = e[(e.base == b) & (e[f"{b}_trend"] == 2)]
    orders[b] = dict(
        n=len(g), opposite_not_earlier=int((g.opp_ts >= g.pt_ts).sum()), replacement=int(g["replace"].sum())
    )
(O / "audit.json").write_text(
    json.dumps(
        dict(
            saved_cells=len(saved),
            source_enumerated_cells=148,
            reproduced_cells=len(new),
            max_abs_diff=diff,
            negative_level_events=len(neg),
            negative_first_take=int(neg.first_take.sum()),
            closed_H2=closed,
            H1_orders=orders,
        ),
        indent=2,
    )
)
print((O / "audit.json").read_text())
