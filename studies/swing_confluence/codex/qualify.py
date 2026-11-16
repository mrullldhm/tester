"""Preserve full tried budget; disqualify order-ambiguous limit inference."""
import json
import numpy as np
import pandas as pd
from studies.swing_confluence.codex.prepare import OUT
from studies.swing_confluence.scan import bh

t=pd.read_csv(OUT/'cells.csv')
# Lower-bound limit labels include entry-bar losses but censor entry-bar target wins.
# They are diagnostics, NOT valid binomial null tests. Keep all in the tried budget
# but give them p=1 so invalid evidence cannot help other cells pass BH.
t['valid_p']=np.where(t.model=='limit',1,t.p)
t['bh_valid']=bh(t.valid_p.to_numpy())
order=np.argsort(t.valid_p.to_numpy()); q=t.valid_p.to_numpy()[order]*len(t)/np.arange(1,len(t)+1)
q=np.minimum.accumulate(q[::-1])[::-1].clip(0,1); t['q_valid']=0.; t.loc[order,'q_valid']=q
t['qualified']=t.bh_valid&(t.edge.abs()>=.03)&(t.years_same>=9)&(t.half1*t.edge>0)&(t.half2*t.edge>0)&(t.model!='limit')
t.to_csv(OUT/'cells.csv',index=False)
print(t.groupby('model')[['bh_valid','qualified']].sum())
print(t[t.qualified].to_string(index=True))
