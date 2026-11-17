"""Dev-only decomposition of purple_levels all 5m (touch) trades. In-sample."""
import numpy as np, pandas as pd
from cltester.config import TICK
from cltester.data import load_period
t = pd.read_csv("results/purple_levels/dev_018fdfd1eb22.csv", parse_dates=["entry_ts", "exit_ts"])
df = load_period("dev")
lo, hi = df["low"].to_numpy(), df["high"].to_numpy()
eb = t["entry_bar"].to_numpy()
lim = t["entry"].to_numpy()
side = t["side"].to_numpy()
through = np.where(side == 1, lo[eb] < lim - TICK / 2, hi[eb] > lim + TICK / 2)
t["through"] = through
risk_t = (t["ticks"].abs())  # placeholder
t["year"] = t["trading_day"].str[:4]
ct = t["entry_ts"].dt.tz_convert("America/Chicago") if t["entry_ts"].dt.tz is not None else t["entry_ts"].dt.tz_localize("UTC").dt.tz_convert("America/Chicago")
t["hr"] = ct.dt.hour
t["win"] = t["net"] > 0
def g(by):
    x = t.groupby(by).agg(n=("net", "size"), gross_pt=("gross", "mean"), net_pt=("net", "mean"), win=("win", "mean"), net=("net", "sum"))
    print(x.round(2)); print()
print("fees per trade", t["fee"].mean(), " gross/trade", t["gross"].mean().round(2), " net/trade", t["net"].mean().round(2))
g("through"); g("side"); g("reason")
bins = [0, 6, 10, 15, 25, 40, 1000]
# stop size: from exits at stop
stopticks = (t.loc[t.reason == "stop", "ticks"]).abs()
t["hrb"] = pd.cut(t["hr"], [-1, 6, 8, 10, 12, 14, 24], labels=["17-07", "07-09", "09-11", "11-13", "13-15", "15+"])
g("hrb")
# risk in ticks reconstructed: target hits = +R ticks, stops = -R-ish; use |ticks| of first exit, approx
t["R"] = t["ticks"].abs()
t["Rb"] = pd.cut(t["R"], bins)
g("Rb")
g("year")
g(["through", "side"])
