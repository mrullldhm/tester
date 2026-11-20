"""Random-entry null for one RLM version (README step 2, Codex round 1).

Keeps everything of the version's orders except the level logic: each signal keeps its CT minute of day, side,
entry offset from the signal close (0 for `close`, band edge - close for `band`), risk ticks, target multiple,
expiry and the BE rule, but is moved to a random dev trading day (same CT minute, bar must exist). The engine runs
these brackets as usual. If the real version is not better than most null runs, the levels add nothing.
Run: .venv/bin/python -m studies.rlm.null --set sig_tf=1h ... [--runs 500] [--through 0]
Memory: one dev frame (~1.1 GB); keep it alone beside a running grid.
"""

import argparse

import numpy as np
import pandas as pd

from cltester.config import ROOT, TICK
from cltester.data import Bars, load_period, to_ticks
from cltester.engine import Fills, backtest
from cltester.swings import TIMEFRAMES
from strategies.rlm import EXPIRE_BARS, Strategy
from studies.rlm.trades import parse

OUT = ROOT / "studies" / "rlm" / "null"


def pf(net: pd.Series) -> float:
    loss = -net[net < 0].sum()
    return float(net[net > 0].sum() / loss) if loss else np.nan


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--runs", type=int, default=500)
    ap.add_argument("--through", type=int, default=0)
    ap.add_argument("--tag", default="null")
    a = ap.parse_args()
    p = {**Strategy.PARAMS, **parse(a.set)}
    df = load_period("dev")
    bars, fills = Bars.from_frame(df), Fills(through=a.through)
    s = Strategy()
    real = backtest(bars, s.signals(df, p), fills, s.manage)
    o = s.orders(df, p)
    side = o["side"].to_numpy()
    k = {"r1": 1, "r2": 2, "r3": 3, "be3": 3}[p["exit"]]
    off = (o["E"] - side * o["cl"]).to_numpy()  # side space: limit - signal close
    risk = o["R"].to_numpy().astype(np.int64)
    minute = o["ct_min"].to_numpy()
    close = to_ticks(df["close"])
    day = df["trading_day"].to_numpy()
    days = np.unique(day)
    ctm = df["ct_minute"].to_numpy()
    # bar index of (trading day, CT minute)
    key = pd.Series(np.arange(len(df)), index=pd.MultiIndex.from_arrays([day, ctm]))
    side_hi = {1: to_ticks(df["high"]), -1: -to_ticks(df["low"])}
    rng = np.random.default_rng(11)
    exp = EXPIRE_BARS * TIMEFRAMES[p["sig_tf"]]
    rows = []
    for r in range(a.runs):
        pick = days[rng.integers(0, len(days), len(o) * 2)]
        bar = key.reindex(pd.MultiIndex.from_arrays([pick, np.r_[minute, minute]])).to_numpy()
        bar = np.where(np.isnan(bar[: len(o)]), bar[len(o):], bar[: len(o)])  # one retry when the minute is missing
        ok = ~np.isnan(bar)
        b = bar[ok].astype(np.int64)
        sd, E = side[ok], side[ok] * close[b] + off[ok]
        S, T = E - risk[ok], E + k * risk[ok]
        sig = pd.DataFrame({"side": sd, "limit": sd * E * TICK, "stop": sd * S * TICK, "target": sd * T * TICK,
                            "expire_min": exp, "kill": sd * T * TICK, "bar": b, "tp1": E + risk[ok]})
        sig = sig.drop_duplicates("bar").set_index("bar").sort_index()
        s._p, s._side_hi = p, side_hi
        s._tp1 = dict(zip(sig.index, sig["tp1"].astype(int), strict=True))
        t = backtest(bars, sig[["side", "limit", "stop", "target", "expire_min", "kill"]], fills, s.manage)
        rows.append({"run": r, "trades": len(t), "net": t["net"].sum(), "pf": pf(t["net"])})
        if r % 50 == 0:
            print(r, flush=True)
    n = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    n.to_csv(OUT / f"{a.tag}.csv", index=False)
    rpf = pf(real["net"])
    print(p)
    print(f"real: trades {len(real)} net {real['net'].sum():.0f} PF {rpf:.3f}  (dev, in-sample)")
    print(f"null: median PF {n['pf'].median():.3f}, share net>0 {(n['net'] > 0).mean():.1%}, "
          f"runs with PF >= real {(n['pf'] >= rpf).mean():.1%} of {len(n)}")


if __name__ == "__main__":
    main()
