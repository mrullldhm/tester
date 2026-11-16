"""Descriptive touch-limit bounds and excursions for all eight tick finalists; no new tests."""
import json
import numpy as np
import pandas as pd
from studies.swing_confluence.codex.prepare import raw,OUT
from studies.swing_confluence.codex.mine import categories
from cltester.data import to_ticks

t=pd.read_csv(OUT/'cells.csv'); sel=t[t.qualified&(t.model=='tick')]; e=pd.read_parquet(OUT/'enriched.parquet')
e=e[(e.outcome>=0)&~e['roll']&(e.leg>=6)&(e.origin_roll==0)&(e.backward==0)&~e.confirm_beyond]
d=raw(); h=to_ticks(d.high); l=to_ticks(d.low); out={}
for ident,r in sel.iterrows():
    g=e[e.base==r.base]; f=categories(g); mask=pd.Series(True,index=g.index)
    for name,val in zip(r.features.split(' & '),r['values'].split(' & '),strict=True):mask &= f[name]==int(val)
    g=g[mask]; outcomes=[]; fairs=[]; amb=[]; tickslo=[]; tickshi=[]
    for row in g.itertuples():
        lim=int(row.price+row.side*np.ceil(row.leg*.25)); a=int(row.bar)+1; b=int(row.end_bar)+1
        hits=np.flatnonzero(l[a:b]<=lim) if row.side==1 else np.flatnonzero(h[a:b]>=lim)
        if not len(hits):continue
        entry=a+int(hits[0]); ambiguous=(entry==row.end_bar and row.outcome==1)
        ylo=0 if ambiguous else row.outcome; yhi=row.outcome
        stop=row.price-row.side; target=row.opp+row.side
        risk=abs(lim-stop); reward=abs(target-lim)
        outcomes.append((ylo,yhi)); fairs.append(row.limit_fair); amb.append(ambiguous)
        tickslo.append(ylo*reward-(1-ylo)*risk); tickshi.append(yhi*reward-(1-yhi)*risk)
    yy=np.array(outcomes); ff=np.array(fairs)
    res=g.outcome-g.fair_tick
    out[str(ident)]={'definition':r.features+' = '+r['values'],'n':len(g),'year_edges':res.groupby(g.year).mean().to_dict(),'fills':len(yy),'fill_fraction':len(yy)/len(g),'target_on_entry_bar':int(sum(amb)),'edge_lower':float((yy[:,0]-ff).mean()),'edge_upper':float((yy[:,1]-ff).mean()),'gross_ticks_lower':float(np.mean(tickslo)),'gross_ticks_upper':float(np.mean(tickshi)),
        'hold_retest_quantiles':g.loc[g.outcome==1,'retest'].quantile([.25,.5,.75]).to_dict(),'hold_next_bar_nan':int(((g.outcome==1)&g.retest.isna()).sum()),'fail_run_quantiles':g.loc[g.outcome==0,'run'].quantile([.25,.5,.75]).to_dict()}
(OUT/'descriptive.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
