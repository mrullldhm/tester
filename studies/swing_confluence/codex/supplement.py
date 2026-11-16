"""Extra audit evidence and entry-bar-complete limit variant; run before mine.py."""
import json
import numpy as np
import pandas as pd
from studies.swing_confluence.codex.prepare import raw, OUT
from studies.swing_confluence.build import RangeExtreme
from cltester.data import to_ticks
from cltester.swings import swing_state, build_candles

d=raw(); e=pd.read_parquet(OUT/'enriched.parquet'); h=to_ticks(d.high); l=to_ticks(d.low); n=len(d)
i=e.bar.to_numpy(); side=e.side.to_numpy(); ev=e.price.to_numpy(); op=e.opp.to_numpy(); lo=np.minimum(ev,op); hi=np.maximum(ev,op)
rx=RangeExtreme(h,l); end=e.end_bar.to_numpy(); limit=ev+side*np.ceil(e.leg.to_numpy()*.25).astype(int)
ent=np.where(side==1,rx.first_below(i+1,limit+1),rx.first_above(i+1,limit-1))
# Include stop on entry bar. Exclude same-bar entry+target: ordering cannot be established.
first_stop=np.where(side==1,rx.first_below(i+1,lo),rx.first_above(i+1,hi))
first_target=np.where(side==1,rx.first_above(i+1,hi),rx.first_below(i+1,lo))
fill=(ent<=end)&(ent<n)&~e['roll'].to_numpy()
ambig=fill&(first_target==ent)
good=fill&~ambig&(end<n)&(e.outcome.to_numpy()>=0)
e['limit_fill']=good; e['limit_outcome']=e.outcome.clip(lower=0)
ts=pd.DatetimeIndex(d.ts).as_unit('ns').asi8
e['limit_elapsed']=np.where(good,(ts[np.minimum(end,n-1)]-ts[np.minimum(ent,n-1)])/6e10,np.nan)
day=d.trading_day.to_numpy(); e['limit_same_day']=day[np.minimum(end,n-1)]==day[i]
a=json.loads((OUT/'audit_evidence.json').read_text()); a['limit_entry_target_ambiguous']=int(ambig.sum()); a['limit_filled_eligible']=int(good.sum()); a['limit_entry_stop_included']=int((good&(first_stop==ent)).sum())
# Definite rule-5 mislabels: both current-candle points added; event was second, preceded by opposite.
wrong=pd.Series(False,index=e.index)
for b in e.base.unique(): wrong|=(e.base==b)&(e.dual==1)&e['replace']&(e[f'{b}_leg']==1)
a['definite_rule5_false_positive_count']=int(wrong.sum()); a['definite_rule5_example']=e[wrong].iloc[0][['base','side','bar','ts','price','opp','replace']].astype(str).to_dict()
# Fair=1 but later fails, proving clipping is not the fair probability of this outcome.
bad=e[(e.fair==1)&(e.outcome==0)&~e['roll']].iloc[0]
a['clipped_fair_counterexample']=bad[['base','side','bar','ts','price','opp','fair','outcome','end_bar']].astype(str).to_dict()
a['clipped_fair_counterexample']['close']=int(to_ticks(d.close)[int(bad.bar)])
a['clipped_fair_one_loses_count']=int(((e.fair==1)&(e.outcome==0)&~e['roll']).sum())
# Recompute raw before-level and show exact event+pre-event state; useful for hand audit.
a['sweep_checks']=[]
for ex in a['examples'][::2]:
    b=ex['base']; si=ex['side']; ii=ex['bar']; first=int(d.ts.searchsorted(pd.Timestamp(ex['pivot_start']))); s=swing_state(d.iloc[:ii+1],b,prev=True,newest=True)
    key='sl' if si==1 else 'sh'; old=s[f'{b}_{key}'].iloc[max(first-1,0)]; ee=e[(e.base==b)&(e.side==si)&(e.bar==ii)].iloc[0]
    a['sweep_checks'].append({'base':b,'bar':ii,'before_ts':str(d.ts.iloc[max(first-1,0)]),'old_level':None if pd.isna(old) else round(old*100),'price':int(ee.price),'stored':int(ee[f'{b}_sweep'])})
# Side mirroring tie issue: strict trend specification versus <= used in source.
for tf in ['1m','1h']:
    g=e[(e[f'{tf}_sh']==e[f'{tf}_sh2'])&(e[f'{tf}_sl']>e[f'{tf}_sl2'])&(e[f'{tf}_sl2']>=0)]
    if len(g): a.setdefault('equal_trend_examples',[]).append(g.iloc[0][['base','side','ts',tf+'_sh',tf+'_sh2',tf+'_sl',tf+'_sl2',tf+'_trend']].astype(str).to_dict())
e.to_parquet(OUT/'enriched.parquet',index=False)
(OUT/'audit_evidence.json').write_text(json.dumps(a,indent=2))
print({k:a[k] for k in ['definite_rule5_false_positive_count','definite_rule5_example','clipped_fair_counterexample','limit_entry_stop_included','limit_entry_target_ambiguous']},flush=True)
