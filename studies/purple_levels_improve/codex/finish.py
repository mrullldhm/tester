from pathlib import Path
import json
import numpy as np
import pandas as pd
out=Path('studies/purple_levels_improve/codex')
c=pd.read_csv(out/'dev_cells.csv'); m=json.loads((out/'dev_metadata.json').read_text())
c['q_BY']=(c.q*sum(1/i for i in range(1,len(c)+1))).clip(upper=1)
c.to_csv(out/'dev_cells.csv',index=False)
account=[]
for f in ('all','nopd'):
    a=pd.read_csv(out/f'dev_{f}_touch_trades.csv').set_index('signal_bar')
    b=pd.read_csv(out/f'dev_{f}_strict_trades.csv').set_index('signal_bar')
    common=a.index.intersection(b.index)
    same=common[a.loc[common,'entry_bar'].to_numpy()==b.loc[common,'entry_bar'].to_numpy()]
    delayed=common.difference(same)
    for name,ix in [('same_signal_same_bar',same),('same_signal_delayed',delayed),('touch_run_only',a.index.difference(b.index)),('strict_run_only',b.index.difference(a.index))]:
        an=a.reindex(ix).net.sum(); bn=b.reindex(ix).net.sum()
        account.append(dict(family=f,cohort=name,n=len(ix),touch_net=an,strict_net=bn,delta=bn-an))
pd.DataFrame(account).to_csv(out/'dev_execution_accounting.csv',index=False)
print(pd.DataFrame(account).to_string(index=False))
print('BY passing',sum(c.q_BY<=.05))
for label in ['all_touch','all_strict','nopd_touch','nopd_strict','all_first_only_strict','all_midpoint_strict','nopd_first_only_strict','nopd_midpoint_strict']:
    t=pd.read_csv(out/f'dev_{label}_trades.csv'); y=t.groupby(pd.to_datetime(t.trading_day).dt.year).net.sum()
    r=c[c.label==label].iloc[0]
    print(label,'years+',sum(y>0),'BH',r.q,'BY',r.q_BY)
