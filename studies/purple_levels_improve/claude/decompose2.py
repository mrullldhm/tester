"""Dev-only, in-sample. Session and risk-size splits in R units, per year."""
import numpy as np, pandas as pd
t = pd.read_csv("results/purple_levels/dev_" + __import__("sys").argv[1] + ".csv", parse_dates=["entry_ts"])
ts = t["entry_ts"]
ts = ts.dt.tz_localize("UTC") if ts.dt.tz is None else ts
ct = ts.dt.tz_convert("America/Chicago")
m = ct.dt.hour * 60 + ct.dt.minute
t["sess"] = np.select([(m >= 17*60) | (m < 2*60), m < 7*60, m < 8*60+30, m < 13*60+30], ["asia 17-02", "london 02-07", "pre 07-0830", "rth 0830-1330"], "late 1330+")
# risk ticks: target trades exit at +R exactly; stop trades exit at -R (no slippage) -> |ticks| on target/stop
t["R"] = t["ticks"].abs().where(t.reason.isin(["target", "stop"]))
t["Rnet"] = t["net"] / (t["R"] * 10)  # CL $10/tick
t["Rgross"] = t["gross"] / (t["R"] * 10)
t["year"] = t["trading_day"].str[:4]
def g(by, d=t):
    print(d.groupby(by).agg(n=("net", "size"), win=("net", lambda s: (s > 0).mean()), Rgross=("Rgross", "mean"), Rnet=("Rnet", "mean"), net=("net", "sum")).round(3)); print()
g("sess")
t["Rb"] = pd.cut(t["R"], [0, 8, 12, 18, 25, 40, 1000])
g("Rb")
t["rth"] = t["sess"].isin(["pre 07-0830", "rth 0830-1330"])
print(t.pivot_table(index="year", columns="rth", values="net", aggfunc=["sum", "count"]).round(0)); print()
t["bigR"] = t["R"] > 12
print(t.pivot_table(index="year", columns="bigR", values="Rnet", aggfunc="mean").round(3)); print()
print(t.pivot_table(index="sess", columns="bigR", values="Rnet", aggfunc=["mean", "count"]).round(3))
print("median R by sess"); print(t.groupby("sess")["R"].median())
