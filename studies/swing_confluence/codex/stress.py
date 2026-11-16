"""One declared stress round on all eight tick-model survivors; every eligible test is counted."""
import json
from math import sqrt, erfc
import numpy as np
import pandas as pd
from studies.swing_confluence.codex.prepare import OUT
from studies.swing_confluence.codex.mine import categories
from studies.swing_confluence.scan import bh

t=pd.read_csv(OUT/'cells.csv'); selected=t[t.qualified&(t.model=='tick')]
e=pd.read_parquet(OUT/'enriched.parquet'); e=e[(e.outcome>=0)&~e['roll']&(e.leg>=6)&(e.origin_roll==0)&(e.backward==0)&~e.confirm_beyond]
ct=e.ts.dt.tz_convert('America/Chicago'); not_end=~((ct.dt.hour==15)&(ct.dt.minute==59)); rows=[]; small=0
for orig,r in selected.iterrows():
    g=e[e.base==r.base]; f=categories(g); mask=pd.Series(True,index=g.index)
    for name,v in zip(r.features.split(' & '),r['values'].split(' & '),strict=True): mask &= f[name]==int(v)
    g=g[mask]
    for name,m in [('leg>=11',g.leg>=11),('not_15:59_CT',not_end.loc[g.index]),('single_point_update',g.dual==0),('low_events',g.side==1),('high_events',g.side==-1)]:
        w=g[m]
        if len(w)<300: small+=1; continue
        res=w.outcome-w.fair_tick; edge=res.mean(); z=res.sum()/sqrt((w.fair_tick*(1-w.fair_tick)).sum()); aa=w.year<=2015
        yr=res.groupby(w.year).mean().reindex(range(2010,2022))
        rows.append(dict(parent=int(orig),base=r.base,features=r.features,values=r['values'],restriction=name,n=len(w),edge=edge,half1=res[aa].mean(),half2=res[~aa].mean(),years_same=int((np.sign(yr)==np.sign(edge)).sum()),z=z,p=erfc(abs(z)/sqrt(2))))
s=pd.DataFrame(rows); p=np.r_[t.valid_p.to_numpy(),s.p.to_numpy()]; passed=bh(p)
s['bh_joint']=passed[len(t):]; t['bh_final']=passed[:len(t)]
t['qualified_final']=t.bh_final&(t.edge.abs()>=.03)&(t.years_same>=9)&(t.half1*t.edge>0)&(t.half2*t.edge>0)&(t.model!='limit')
idx=np.argsort(p); q=np.minimum.accumulate((p[idx]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1].clip(0,1); qq=np.empty(len(p)); qq[idx]=q
t['q_final']=qq[:len(t)]; s['q_final']=qq[len(t):]
s.to_csv(OUT/'stress.csv',index=False); t.to_csv(OUT/'cells.csv',index=False)
(OUT/'final_budget.json').write_text(json.dumps({'main_tests':len(t),'stress_tests':len(s),'stress_sparse_not_tested':small,'total':len(p),'bh_valid':int(passed.sum()),'main_qualified':int(t.qualified_final.sum()),'tick_qualified':int((t.qualified_final&(t.model=='tick')).sum())},indent=2))
print(s.to_string(index=False))
