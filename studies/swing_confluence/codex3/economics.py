import json
from pathlib import Path

import pandas as pd

P = Path(__file__).parent
ledger = pd.read_csv("results/ledger.csv")
rows = []
for name, hash_, budget in [
    ("purple_pa", "3d5c120f1b1e", 2),
    ("purple_pa", "82329909b22a", 2),
    ("swing_point_failure", None, 15),
    ("swing_point_failure_reversal", "ebbbdce3e44c", 5),
    ("swing_point_failure_reversal", "b614116a4633", 5),
    ("swing_point_manipulation", "31949a423a66", 14),
    ("swing_point_manipulation", "8cf495b86d35", 14),
]:
    if hash_ is None:
        a = ledger[(ledger.strategy == name) & (ledger.period == "dev")]
        a = a[a.params.map(lambda x: json.loads(x) == dict(swing_tf="1h", risk=25, rr=2, tie="5m"))].iloc[-1]
        hash_ = a["hash"]
    else:
        a = ledger[(ledger.strategy == name) & (ledger["hash"] == hash_)].iloc[-1]
    d = pd.read_csv(f"results/{name}/dev_{hash_}.csv")
    w = d[d.net > 0]
    loss = d[d.net < 0]
    st = d[d.reason == "stop"]
    tar = d[d.reason == "target"]
    row = dict(
        strategy=name,
        hash=hash_,
        best_of=budget,
        params=a.params,
        trades=len(d),
        net=d.net.sum(),
        gross=d.gross.sum(),
        fees=d.fee.sum(),
        gross_per=d.gross.mean(),
        net_per=d.net.mean(),
        pf_net=w.net.sum() / -loss.net.sum(),
        pf_gross=d.loc[d.gross > 0, "gross"].sum() / -d.loc[d.gross < 0, "gross"].sum(),
        win=(d.net > 0).mean(),
        avg_win=w.net.mean(),
        avg_loss=-loss.net.mean(),
        breakeven_win=-loss.net.mean() / (w.net.mean() - loss.net.mean()),
        stop_median_ticks=-st.ticks.median(),
        target_median_ticks=tar.ticks.median(),
        year_pos=int((d.groupby(pd.to_datetime(d.trading_day).dt.year).net.sum() > 0).sum()),
        stop_fillbar=(st.entry_bar == st.exit_bar).mean(),
        pass_rate=a.pass_rate,
    )
    rows.append(row)
pd.DataFrame(rows).to_csv(P / "economics.csv", index=False)
print(pd.DataFrame(rows).to_string(index=False))
