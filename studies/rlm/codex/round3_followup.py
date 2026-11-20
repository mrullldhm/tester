"""Lightweight summaries from round3 CSVs, run after the main Python process exits."""
import json
import pandas as pd
OUT='studies/rlm/codex/'
t=pd.read_csv(OUT+'round3_trade_audit.csv')
o=pd.read_csv(OUT+'round3_orders.csv').set_index('bar')
def stats(x):
    v=x.net
    return dict(n=len(x),net=float(v.sum()),pf=float(v[v>0].sum()/-v[v<0].sum()))
r={}
r['delayed_hour_completion_trades']=stats(t[t.signal_bar.isin(o.index[o.ct_min%60!=59])])
r['exclude_all_flagged']=stats(t[~(t.late|t.early_close_day|t.roll_window|t.incomplete_candle|t.open_through)])
r['early_close_dates']=sorted(t.loc[t.early_close_day,'trading_day'].unique().tolist())
r['filled_intended_risk_ticks_quantiles']=o.loc[t.signal_bar,'R'].quantile([0,.5,.9,.95,.99,1]).to_dict()
r['five_cl_planned_loss_ge_2000_trades']=int(((o.loc[t.signal_bar,'R']*10+4.04)*5>=2000).sum())
r['one_cl_planned_loss_ge_2000_trades']=int(((o.loc[t.signal_bar,'R']*10+4.04)>=2000).sum())
r['planned_loss_at_most_200_trades']=int(((o.loc[t.signal_bar,'R']*10+4.04)<=200).sum())
r['late_hours']=pd.to_datetime(t.loc[t.late,'entry_ts']).dt.tz_convert('America/Chicago').dt.hour.value_counts().to_dict()
with open(OUT+'round3_followup.json','w') as f:json.dump(r,f,indent=2)
print(json.dumps(r,indent=2))
