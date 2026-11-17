import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
import numpy as np
import pandas as pd
from cltester.data import load_period, Bars
O=Path('studies/all_strategies_improve/codex')
C=pd.read_csv(O/'cells.csv');M=json.loads((O/'metadata.json').read_text());R=pd.read_csv(O/'replay_checks.csv')
assert R['match'].all(),R[~R['match']]
assert len(C)==M['evaluated_cells']
p=C.loc[C.p.notna(),'p'].to_numpy();order=np.argsort(p);q=np.empty(len(p));q[order]=np.minimum(1,np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1])
assert np.allclose(q,C.loc[C.p.notna(),'BH'])
assert np.allclose(np.minimum(1,q*sum(1/np.arange(1,len(q)+1))),C.loc[C.p.notna(),'BY'])
for r in C[C.kind=='paired_change'].to_dict('records'):
 fill=int(r['label'][-1]);d=pd.read_csv(O/f'purple_pa_rth_through{fill}_paired_days.csv')
 assert len(d)==M['dev_days']
 assert np.isclose(d.delta.sum(),r['total_delta'])
 assert np.isclose(d.delta.mean(),r['mean'])
 assert np.isclose(d.delta.std(ddof=1)/np.sqrt(len(d)),r['se'])
B=Bars.from_frame(load_period('dev'));S=json.loads((O/'selections.json').read_text());checks=[]
for sel in S:
 if sel['selection']!='best':continue
 n=sel['strategy'];sig=pd.read_csv(O/f'{n}_best_dev_signals.csv',index_col=0)
 for label,fill,fp in [('best',sel['fill'],O/f'{n}_best_dev_trades.csv'),('strict',1,O/f'{n}_best_strict_dev_trades.csv')]:
  t=pd.read_csv(fp); assert np.isfinite(t[['gross_ticks','gross_R','net_R','risk']].to_numpy()).all();assert (t.risk>0).all()
  si=sig.loc[t.signal_bar.to_numpy()];risk=np.abs(np.rint(si.limit.to_numpy()*100)-np.rint(si.stop.to_numpy()*100));assert np.array_equal(risk,t.risk)
  assert np.allclose(t.gross_R,t.gross/(10*t.qty*risk))
  for k in sorted(set([0,len(t)//2,len(t)-1])) if len(t) else []:
   tr=t.iloc[k];s=sig.loc[int(tr.signal_bar)];side=int(tr.side);j=int(tr.entry_bar);x=int(tr.exit_bar);lim=round(s.limit*100)
   reach=B.l[j]<=lim-fill if side==1 else B.h[j]>=lim+fill
   expected=min(B.o[j],lim) if side==1 else max(B.o[j],lim)
   ok=bool(reach and round(tr.entry*100)==expected and B.l[x]<=round(tr.exit*100)<=B.h[x] and B.sym_id[j]==B.sym_id[x] and int(tr.signal_bar)<j)
   checks.append(dict(strategy=n,portfolio=label,entry_ts=tr.entry_ts,exit_ts=tr.exit_ts,entry_open=B.o[j]/100,entry_low=B.l[j]/100,entry_high=B.h[j]/100,limit=s.limit,entry=tr.entry,exit=tr.exit,reason=tr.reason,ok=ok))
   assert ok,checks[-1]
for fill in [0,1]:
 fp=O/f'purple_pa_rth_through{fill}_dev_trades.csv'
 if not fp.exists():continue
 t=pd.read_csv(fp);mins=pd.to_datetime(t.entry_ts,utc=True).dt.tz_convert('America/Chicago');clock=mins.dt.hour*60+mins.dt.minute
 assert ((clock>=510)&(clock<810)).all()
pd.DataFrame(checks).to_csv(O/'verification_spot_checks.csv',index=False)
print(json.dumps({'selected_replays':len(R),'all_replays_match':bool(R['match'].all()),'strict_and_touch_raw_checks':len(checks),'all_raw_checks_pass':all(c['ok'] for c in checks),'cell_count':len(C),'inference_count':len(p),'BH_BY_recomputed':True,'paired_daily_SE_verified':True},indent=2))
