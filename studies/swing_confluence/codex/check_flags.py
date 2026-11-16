import json
import pandas as pd
from cltester.swings import swing_state
from studies.swing_confluence.codex.prepare import raw, OUT

d=raw(); e=pd.read_parquet(OUT/'enriched.parquet',columns=['base','bar','side','replace','dual']); count=0; examples=[]
for b in e.base.unique():
    g=e[(e.base==b)&e['replace']&(e.dual==1)]; s=swing_state(d,b,newest=True)
    i=g.bar.to_numpy(); sh=s[f'{b}_sh_ts'].iloc[i].reset_index(drop=True); sl=s[f'{b}_sl_ts'].iloc[i].reset_index(drop=True)
    same=(sh==sl).to_numpy(); second=s[f'{b}_newest'].to_numpy()[i]==-g.side.to_numpy()
    wrong=same&second; count+=int(wrong.sum())
    if wrong.any():
        j=int(wrong.nonzero()[0][0]); ii=int(i[j]); examples.append({'base':b,'bar':ii,'known':str(d.ts.iloc[ii]),'pivot':str(sh.iloc[j]),'side':int(g.side.iloc[j]),'newest':int(s[f'{b}_newest'].iloc[ii])})
    print(b,int(wrong.sum()),flush=True)
a=json.loads((OUT/'audit_evidence.json').read_text()); a['definite_rule5_false_positive_count']=count; a['definite_rule5_same_candle_examples']=examples
(OUT/'audit_evidence.json').write_text(json.dumps(a,indent=2))
