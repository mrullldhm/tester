"""Fixed interaction/sequence scan. Saves every tested cell, including failures."""
from itertools import combinations
from pathlib import Path
from math import erfc, sqrt
import json
import numpy as np
import pandas as pd
from studies.swing_confluence.scan import bh

OUT=Path('studies/swing_confluence/codex')
TFS=['1m','5m','15m','1h','4h','1d','1w','1mo']

def categories(g):
    f={}
    for t in TFS:
        f[t+'_trend']=g[t+'_trend'].where(g[t+'_trend']!=0)
        f[t+'_leg']=g[t+'_leg'].where(g[t+'_leg']!=0)
        f[t+'_sweep']=g[t+'_sweep'].where(g[t+'_sweep']>=0)
        p=g[t+'_pos']
        f[t+'_pos']=pd.Series(np.select([p<=0,p<=.25,p<.75,p<1,p>=1],[0,1,2,3,4],default=-1),index=g.index).where(p.notna())
    f['speed']=pd.cut(g.speed,[-np.inf,1,5,np.inf],labels=False)
    f['touches']=g.touches.clip(upper=2)
    f['reclaim']=g.reclaim.where(g.reclaim>=0)
    f['sweep_depth']=pd.cut(g.sweep_depth,[0,.1,.5,np.inf],labels=False)
    f['nested']=g.nested
    f['prior_failed']=g.prior_failed
    f['replacement']=g['replace'].astype(int).where(g.dual==0)
    return pd.DataFrame(f,index=g.index)

def definitions(base):
    higher=TFS[TFS.index(base)+1:]
    defs=[]
    for a,b in combinations(higher,2):
        defs += [(a+'_trend',b+'_trend'),(a+'_leg',b+'_leg'),(a+'_leg',b+'_pos'),(a+'_sweep',b+'_trend')]
    for a,b,c in combinations(higher,3):
        defs += [(a+'_leg',b+'_leg',c+'_pos')]
    seq=['speed','touches','reclaim','sweep_depth','nested','prior_failed','replacement']
    for a in seq:
        defs.append((a,))
        for t in higher:
            defs += [(a,t+'_leg'),(a,t+'_pos')]
    return defs

def main():
    e=pd.read_parquet(OUT/'enriched.parquet')
    # Audit-motivated restrictions declared in analysis_notes before this first scan.
    e=e[(e.outcome>=0)&~e['roll']&(e.leg>=6)&(e.origin_roll==0)&(e.backward==0)&~e.confirm_beyond].copy()
    rows=[]; small=0; total_groups=0; details={}
    for base,g in e.groupby('base',sort=False):
        f=categories(g)
        for dd in definitions(base):
            # every observed category cell is enumerated; small cells are counted but not tested
            group=f.groupby(list(dd),observed=True,dropna=True).indices
            for vals,idx in group.items():
                total_groups+=1
                if len(idx)<300: small+=1; continue
                vals=vals if isinstance(vals,tuple) else (vals,)
                v=g.iloc[idx]
                for model,fc,yc in [('original','fair','outcome'),('tick','fair_tick','outcome'),('limit','limit_fair','limit_outcome')]:
                    # Limit variant tested for sequence definitions only (single or paired).
                    if model=='limit' and dd[0] not in ['speed','touches','reclaim','sweep_depth','nested','prior_failed','replacement']: continue
                    w=v[v.limit_fill] if model=='limit' else v
                    if len(w)<300:
                        if model=='limit': small+=1
                        continue
                    r=w[yc]-w[fc]; var=(w[fc]*(1-w[fc])).sum(); z=r.sum()/sqrt(max(var,1e-9)); edge=r.mean()
                    yr=r.groupby(w.year).mean().reindex(range(2010,2022)); ysign=int((np.sign(yr)==np.sign(edge)).sum())
                    a=w.year<=2015
                    row=dict(base=base,family='sequence' if dd[0] in ['speed','touches','reclaim','sweep_depth','nested','prior_failed','replacement'] else 'interaction',features=' & '.join(dd),values=' & '.join(str(int(x)) for x in vals),model=model,n=len(w),edge=edge,half1=r[a].mean(),half2=r[~a].mean(),n_half1=int(a.sum()),n_half2=int((~a).sum()),years_same=ysign,z=z,p=erfc(abs(z)/sqrt(2)),leg_q25=w.leg.quantile(.25),leg_median=w.leg.median(),leg_q75=w.leg.quantile(.75),leg_le5=float((w.leg<=5).mean()),leg_le10=float((w.leg<=10).mean()),elapsed_median=w.limit_elapsed.median() if model=='limit' else w.elapsed.median(),same_day=w.limit_same_day.mean() if model=='limit' else w.same_day.mean(),hold=w[yc].mean(),fair=w[fc].mean())
                    rows.append(row)
                    if abs(edge)>=.03 and ysign>=9 and row['half1']*edge>0 and row['half2']*edge>0:
                        # daily cluster standard error, center scores by observed mean for a descriptive check
                        daily=(r-edge).groupby(w.trading_day).sum()
                        zc=r.sum()/sqrt(max((daily**2).sum()*len(daily)/max(len(daily)-1,1),1e-9))
                        row['cluster_z']=zc
                        details[len(rows)-1]={'year_edge':{str(y):float(x) for y,x in yr.items()},'retest_quantiles':w.loc[w.outcome==1,'retest'].quantile([.25,.5,.75]).to_dict(),'run_quantiles':w.loc[w.outcome==0,'run'].quantile([.25,.5,.75]).to_dict(),'days':len(daily)}
        print(base,'tests so far',len(rows),flush=True)
    t=pd.DataFrame(rows); t['bh']=bh(t.p.to_numpy()); t['pass']=t.bh&(t.edge.abs()>=.03)&(t.years_same>=9)&(t.half1*t.edge>0)&(t.half2*t.edge>0)
    t.to_csv(OUT/'cells.csv',index=False)
    (OUT/'mining_summary.json').write_text(json.dumps({'tested':len(t),'observed_category_groups':total_groups,'sparse_not_tested':small,'bh':int(t.bh.sum()),'passes':int(t['pass'].sum()),'eligible_by_base':e.groupby('base').size().to_dict(),'details':details},indent=2))
    print(t[t['pass']].sort_values('edge',key=abs,ascending=False).head(60).to_string(index=True),flush=True)

if __name__=='__main__':main()
