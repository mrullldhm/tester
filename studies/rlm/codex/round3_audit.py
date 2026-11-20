"""Dev-only independent audit. Run under the user-specified 3 GB virtual-memory limit."""
import json
import inspect
import numpy as np
import pandas as pd
from cltester.data import load_period, Bars
from cltester.engine import backtest, Fills
from cltester.swings import build_candles
from strategies.rlm import Strategy
import cltester.swings as sw
import strategies.rlm as rlm

# Equivalent timestamp indexing avoids materializing four million Python Timestamp objects.
# Local process only; production sources remain untouched.
source=inspect.getsource(sw.build_candles)
source=source.replace('df["ts"].to_numpy()[start[done]]', 'df["ts"].iloc[start[done]]')
exec(source,sw.__dict__)
rlm.build_candles=sw.build_candles
build_candles=sw.build_candles

OUT = 'studies/rlm/codex/'
P = dict(sig_tf='1h', reg='confirm', sources='all', weight='flat', tol=.4,
         score=50, clv=.6, entry='close', stop='band', exit='r1', session='all')
def stats(t):
    v = t.net
    return dict(n=len(t), net=float(v.sum()), pf=float(v[v>0].sum() / -v[v<0].sum()) if (v<0).any() else None)
result = {}
df = load_period('dev')
df.drop(columns=['vendor','volume','ct'],inplace=True)
df['raw_symbol']=df.raw_symbol.astype('category')
print('loaded', len(df), flush=True)
bars = Bars.from_frame(df)
s = Strategy()
sig = s.signals(df, P)
orders = s.orders(df, P).set_index('bar')
orders.to_csv(OUT+'round3_orders.csv')
t = backtest(bars, sig, Fills(), s.manage)
print('real', stats(t), 'orders',len(orders), flush=True)
result['real'] = stats(t)
cd = build_candles(df, '1h')
ci = orders.c.to_numpy(int)
av = orders.index.to_numpy(int)
result['timing'] = dict(orders=len(orders), before_completion=int((av<cd.avail[ci]).sum()),
    delayed_completion=int((cd.avail[ci]>cd.last[ci]).sum()),
    incomplete_minutes=int(((cd.last[ci]-cd.first[ci]+1)<60).sum()),
    close_mismatch=int((orders.cl.to_numpy()!=cd.c[ci]).sum()),
    cross_day=int((bars.day_id[cd.first[ci]]!=bars.day_id[av]).sum()),
    cross_contract=int((bars.sym_id[cd.first[ci]]!=bars.sym_id[av]).sum()))
i=t.signal_bar.to_numpy(int); j=t.entry_bar.to_numpy(int)
sd=t.side.to_numpy(int); lim=orders.loc[i,'E'].to_numpy()
improve=lim-sd*bars.o[j]
next_improve=lim-sd*bars.o[i+1]
t['improvement_ticks']=np.maximum(improve,0)
t['next_bar']=j==i+1
t['open_through']=improve>0
t['next_open_through']=(j==i+1)&(next_improve>0)
t['late']=df.ct_minute.to_numpy()[j]>=840
t['late'] &= df.ct_minute.to_numpy()[j]<1020
# Early-close proxy: trading-day final observed CT minute < 15:10; report as proxy, not a holiday calendar.
lasts=df.groupby('trading_day',sort=False).tail(1)
early=lasts.loc[lasts.ct_minute<910,'trading_day'].to_numpy()
t['early_close_day']=np.isin(t.trading_day.to_numpy(),early)
roll_ix=np.flatnonzero(bars.sym_id[1:]!=bars.sym_id[:-1])+1
roll_days=np.unique(bars.trading_day[roll_ix]).astype('datetime64[D]').astype(int)
td=t.trading_day.to_numpy().astype('datetime64[D]').astype(int)
near=np.zeros(len(t),bool)
for r in roll_days: near |= np.abs(td-r)<=3
t['roll_window']=near
t['incomplete_candle']=(cd.last[orders.loc[i,'c'].to_numpy(int)]-cd.first[orders.loc[i,'c'].to_numpy(int)]+1)<60
result['subgroups']={}
for col in ['next_bar','open_through','next_open_through','late','early_close_day','roll_window','incomplete_candle']:
    result['subgroups'][col]={'yes':stats(t[t[col]]),'no':stats(t[~t[col]])}
result['late_reasons']=t[t.late].reason.value_counts().to_dict()
result['reasons']=t.reason.value_counts().to_dict()
result['improvement']=dict(total_ticks=float(t.improvement_ticks.sum()),median=float(t.improvement_ticks.median()),
    max=float(t.improvement_ticks.max()),opens_beyond_stop=int((sd*bars.o[j]<=orders.loc[i,'S'].to_numpy()).sum()))
cost=t.copy();cost.net-=10*cost.improvement_ticks
result['remove_improvement_pnl_only']=stats(cost)
for name,ss in [('exclude_late',sig.loc[~((df.ct_minute.to_numpy()[sig.index]>=839)&(df.ct_minute.to_numpy()[sig.index]<1020))]),
                ('delay_one_minute',sig.set_axis(sig.index+1).loc[lambda x:x.index<len(df)-1])]:
    tx=backtest(bars,ss,Fills(),s.manage)
    result[name]=stats(tx)
    del tx
result['risk_quantiles_dollars']={str(q):float(x) for q,x in (orders.loc[i,'R']*10+4.04).quantile([0,.5,.9,.95,.99,1]).items()}
t.drop(columns='path').to_csv(OUT+'round3_trade_audit.csv',index=False)
del cost
# Same trading day, same side, CLV>=.6, another completed 1h candle; same absolute bracket risk.
# Candidate hours match overnight (17..08:29), daytime (08:30..13:59), late (14..15:09) buckets.
# This preserves coarse time of day as well as daily market regime. All draws precede engine outcome calculation.
ctm=df.ct_minute.to_numpy(); day=bars.day_id
bucket=lambda m: np.where((m>=840)&(m<1020),2,np.where((m>=510)&(m<840),1,0))
avc=cd.avail
valid=(avc==cd.last)&(bars.day_id[cd.first]==day[avc])&(bars.sym_id[cd.first]==bars.sym_id[avc])
valid &= bars.sess_minute[avc]<1329 # no order can start at/after 15:10
clv=np.divide(cd.c-cd.l,cd.h-cd.l,out=np.full(len(cd),.5),where=cd.h!=cd.l)
pools={}
for side in (1,-1):
    ids=np.flatnonzero(valid & ((clv>=.6) if side==1 else (clv<=.4)))
    for c in ids:
        b=int(avc[c]);key=(int(day[b]),side,int(bucket(ctm[b])))
        pools.setdefault(key,[]).append(b)
choices=[]; keep=[]
for r,row in enumerate(orders.itertuples()):
    key=(int(day[row.Index]),int(row.side),int(bucket(ctm[row.Index])))
    other=np.array([b for b in pools.get(key,[]) if b!=row.Index],int)
    if len(other): keep.append(r); choices.append(other)
oo=orders.iloc[keep]
result['null_design']=dict(runs=300,seed=20261120,eligible_orders=len(oo),total_orders=len(orders),
    excluded_no_other_hour=len(orders)-len(oo),buckets='overnight,08:30-13:59,14:00-15:09 CT',risk='original ticks')
matched=backtest(bars,sig.loc[oo.index],Fills(),s.manage)
result['matched_real']=stats(matched)
del matched
rng=np.random.default_rng(20261120); rows=[]
side=oo.side.to_numpy(int);risk=oo.R.to_numpy(int)
for run in range(300):
    b=np.array([x[rng.integers(len(x))] for x in choices])
    E=side*bars.c[b]
    ns=pd.DataFrame(dict(side=side,limit=side*E*.01,stop=side*(E-risk)*.01,target=side*(E+risk)*.01,
                         expire_min=60,kill=side*(E+risk)*.01),index=b)
    ns=ns.loc[~ns.index.duplicated()].sort_index()
    nt=backtest(bars,ns,Fills(),s.manage)
    rows.append(dict(run=run,orders=len(ns),**stats(nt)))
    del nt
    if run%25==0: print('null',run,flush=True)
n=pd.DataFrame(rows);n.to_csv(OUT+'round3_same_day_null.csv',index=False)
result['null_summary']=dict(pf_quantiles={str(q):float(x) for q,x in n.pf.quantile([0,.025,.5,.95,.975,1]).items()},
    mean=float(n.pf.mean()),sd=float(n.pf.std()),exceed_real=int((n.pf>=result['real']['pf']).sum()),
    exceed_matched=int((n.pf>=result['matched_real']['pf']).sum()),median_trades=float(n.n.median()))
with open(OUT+'round3_summary.json','w') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2),flush=True)
