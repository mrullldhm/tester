import sys
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
import pandas as pd
from cltester.data import load_period
from cltester.indicators import tf_candles
out=Path('studies/purple_levels_improve/codex')
df=load_period('dev')
cd=tf_candles(df,'5m'); cd=cd[cd.avail<len(df)].reset_index(drop=True)
rows=[]
for label in ('all_touch','all_strict','nopd_touch','nopd_strict'):
    tr=pd.read_csv(out/f'dev_{label}_trades.csv')
    for k in (0,len(tr)//2,len(tr)-1):
        s=tr.iloc[k]; t=int(s.touch_candle); q=int(s.confirm_candle); sd=int(s.side)
        h2=int(round(cd.high.iloc[q-2]/.01)); l2=int(round(cd.low.iloc[q-2]/.01))
        hq=int(round(cd.high.iloc[q]/.01)); lq=int(round(cd.low.iloc[q]/.01))
        assert (lq>h2 if sd==1 else hq<l2)
        a=int(cd['first'].iloc[t]); b=int(cd['last'].iloc[q])+1
        stop=int(round(df.low.iloc[a:b].min()/.01))-1 if sd==1 else int(round(df.high.iloc[a:b].max()/.01))+1
        risk=int(s.risk_ticks); limit=lq if sd==1 else hq
        assert (limit-stop)*sd==risk
        assert int(cd.avail.iloc[q])==int(s.signal_bar)
        assert df.raw_symbol.iloc[a:int(s.signal_bar)+1].nunique()==1
        level=int(s.level)
        assert (int(round(cd.low.iloc[t]/.01))<=level if sd==1 else int(round(cd.high.iloc[t]/.01))>=level)
        rows.append(dict(portfolio=label,signal_bar=int(s.signal_bar),level=level,touch_candle=t,confirm_candle=q,earlier_high=h2,earlier_low=l2,confirm_high=hq,confirm_low=lq,limit=limit,stop=stop,risk=risk,status='PASS'))
pd.DataFrame(rows).to_csv(out/'dev_setup_checks.csv',index=False)
print('PASS: 12 raw setup checks; all four baseline signal streams and trade lists reproduced in audit.py')
