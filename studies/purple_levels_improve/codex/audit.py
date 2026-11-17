import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
import numpy as np
import pandas as pd
from statistics import NormalDist
from math import erfc, sqrt
class student:
    @staticmethod
    def sf(x, df): return .5 * erfc(x / sqrt(2))
class norm:
    ppf = NormalDist().inv_cdf
from cltester.data import load_period, Bars
from cltester.engine import backtest, Fills
from strategies.purple_levels import Strategy

OUT = Path('studies/purple_levels_improve/codex')
print('Loading dev only', flush=True)
df = load_period('dev')
bars = Bars.from_frame(df)
days = pd.Index(df.trading_day.unique())
D = len(days)
years = (df.trading_day.max()-df.trading_day.min()).days/365.25
# Instrument an in-memory copy; production files are never changed.
src = Path('strategies/purple_levels.py').read_text()
src = src.replace('cols = ["side", "limit", "stop", "target", "expire_min"]', 'cols = ["side", "limit", "stop", "target", "expire_min", "level", "test_number", "gap_ticks", "touch_candle", "confirm_candle"]')
src = src.replace('p["expire_candles"] * tf_minutes(p["tf"])))', 'p["expire_candles"] * tf_minutes(p["tf"]), lev, tests, abs(int((l[q] - h[q-2]) if sd == 1 else (l[q-2] - h[q]))), t, q))')
ns = {'__name__':'audit_instrumented'}
exec(compile(src, 'instrumented_purple_levels', 'exec'), ns)
Instrumented = ns['Strategy']
original_day_levels = Strategy.day_levels
cache = {}
def cached(df, cd, ds, di, starts, fam):
    if not cache:
        for f in ('pd','pw','sw4h','sw1d'):
            cache[f] = original_day_levels(df, cd, ds, di, starts, f)
        cache['days'] = ds
    fs = ns['UNIONS'].get(fam, (fam,))
    return [list(dict.fromkeys(v for f in fs for v in cache[f][d])) for d in range(len(ds))]
Strategy.day_levels = staticmethod(cached)
Instrumented.day_levels = staticmethod(cached)
cols = ['side','limit','stop','target','expire_min']
cells=[]
portfolios={}
signals={}
checks=[]
power=[]
def stats(tr, label, kind):
    n=len(tr)
    mu=tr.net.mean()
    pday=tr.groupby('trading_day').net.sum().reindex(days,fill_value=0).to_numpy()
    nday=tr.groupby('trading_day').size().reindex(days,fill_value=0).to_numpy()
    se=np.sqrt(D/(D-1)*np.square(pday-mu*nday).sum())/n if n else np.nan
    p=float(student.sf(mu/se,D-1)) if se>0 else 1.
    row=dict(label=label,kind=kind,n=n,net=tr.net.sum(),mean=mu,pf=tr.net.clip(lower=0).sum()/(-tr.net.clip(upper=0).sum()),se=se,p=p)
    cells.append(row)
    return row
files={'all_touch':'018fdfd1eb22','all_strict':'e0799b1e4110','nopd_touch':'b777ef9ec188','nopd_strict':'17242b70a399'}
for fam in ('all','nopd'):
    print('Signals',fam,flush=True)
    p={**Strategy.PARAMS,'levels':fam,'tf':'5m'}
    sig=Instrumented().signals(df,p)
    plain=Strategy().signals(df,p)
    pd.testing.assert_frame_equal(sig[cols], plain)
    signals[fam]=sig
    sig.to_csv(OUT/f'dev_{fam}_signals.csv')
    fam_order=ns['UNIONS'][fam]
    day_positions={day:i for i,day in enumerate(cache['days'])}
    attribution=[]
    for i,s in sig.iterrows():
        d=day_positions[df.trading_day.iloc[i].to_datetime64()]
        attribution.append(next(f for f in fam_order if s.level in cache[f][d]))
    sig['family']=attribution
    for through in (0,1):
        label=f'{fam}_{"strict" if through else "touch"}'
        tr=backtest(bars,sig[cols],fills=Fills(through=through))
        old=pd.read_csv(f'results/purple_levels/dev_{files[label]}.csv')
        for c in ('signal_bar','entry_bar','exit_bar','side','entry','exit','net'):
            np.testing.assert_allclose(tr[c],old[c],atol=1e-8)
        tr=tr.join(sig.drop(columns=cols),on='signal_bar')
        ss=sig.loc[tr.signal_bar]
        tr['risk_ticks']=np.round((ss.limit.to_numpy()-ss.stop.to_numpy())*tr.side/0.01).astype(int)
        tr['gap_risk']=tr.gap_ticks/tr.risk_ticks
        tr['distance_R']=(tr.entry/0.01-tr.level)*tr.side/tr.risk_ticks
        j=tr.entry_bar.to_numpy()
        lim=np.round(ss.limit.to_numpy()/0.01).astype(int)
        penetration=np.where(tr.side==1,lim-bars.l[j],bars.h[j]-lim)
        tr['fill_type']=np.where(penetration>=1,'through','touch_only')
        ct=df.ct.iloc[tr.signal_bar].dt.hour.to_numpy()+df.ct.iloc[tr.signal_bar].dt.minute.to_numpy()/60
        tr['clock']=np.select([ct<8,ct<10,ct<12,ct<17],['17-08','08-10','10-12','12-15:10'],default='17-08')
        tr['gap_bin']=pd.cut(tr.gap_risk,[-np.inf,.1,.25,np.inf],labels=['<=.10','.10-.25','>.25'])
        tr['distance_bin']=pd.cut(tr.distance_R,[-np.inf,.5,1,np.inf],labels=['<=.5','.5-1','>1'])
        tr['stop_bin']=pd.cut(tr.risk_ticks,[0,8,16,np.inf],labels=['<=8','9-16','>16'])
        tr['year']=pd.to_datetime(tr.trading_day).dt.year
        portfolios[label]=tr
        row=stats(tr,label,'portfolio')
        for col in ('family','clock','gap_bin','fill_type','test_number','side','distance_bin','stop_bin','year'):
            for val,g in tr.groupby(col,observed=True):
                stats(g,f'{label}/{col}/{val}','decomposition')
        for k in (0,len(tr)//2,len(tr)-1):
            s=tr.iloc[k]; i=int(s.signal_bar); j=int(s.entry_bar); x=int(s.exit_bar); side=int(s.side)
            L=int(round(sig.loc[i,'limit']/.01)); S=int(round(sig.loc[i,'stop']/.01)); T=int(round(sig.loc[i,'target']/.01))
            assert j>i and bars.sym_id[i]==bars.sym_id[j] and bars.day_id[i]==bars.day_id[j]
            assert (bars.l[j]<=L-through if side==1 else bars.h[j]>=L+through)
            assert round(s.entry/.01)==(min(bars.o[j],L) if side==1 else max(bars.o[j],L))
            assert np.isclose(s.net,s.ticks*10-4.04)
            if s.reason=='target': assert (bars.h[x]>=T if side==1 else bars.l[x]<=T)
            if s.reason=='stop': assert (bars.l[x]<=S if side==1 else bars.h[x]>=S)
            checks.append(dict(portfolio=label,signal=i,entry=j,exit=x,ts=str(s.entry_ts),side=side,limit=L,stop=S,target=T,entry_low=int(bars.l[j]),entry_high=int(bars.h[j]),exit_low=int(bars.l[x]),exit_high=int(bars.h[x]),reason=s.reason,net=s.net))
        top=tr.groupby('trading_day').net.sum().sort_values(ascending=False)
        observed=row['mean']; sd=row['se']*np.sqrt(len(tr)); z=norm.ppf(.975)+norm.ppf(.8)
        power.append(dict(portfolio=label,rate=len(tr)/years,mean=observed,sd_cluster=sd,n80=(z*sd/observed)**2,n80_half=(z*sd/(observed/2))**2,without_top10=tr.net.sum()-top.head(10).sum(),median_risk=tr.risk_ticks.median(),mean_risk=tr.risk_ticks.mean(),risk_q25=tr.risk_ticks.quantile(.25),risk_q75=tr.risk_ticks.quantile(.75)))
        tr.drop(columns='path').to_csv(OUT/f'dev_{label}_trades.csv',index=False)
    for change in ('first_only','midpoint'):
        s=sig[cols].copy()
        if change=='first_only': s=s.loc[sig.test_number==1]
        else:
            move=(sig.gap_ticks//2).astype(int)
            s['limit']=((s['limit']/.01).round().astype(int)-s.side*move)*.01
            risk=np.round((s.limit-s.stop)*s.side/.01).astype(int)
            s['target']=s.limit+s.side*risk*.01
        tr=backtest(bars,s,fills=Fills(through=1))
        label=f'{fam}_{change}_strict'
        stats(tr,label,'portfolio')
        base=portfolios[f'{fam}_strict']
        diff=tr.groupby('trading_day').net.sum().reindex(days,fill_value=0)-base.groupby('trading_day').net.sum().reindex(days,fill_value=0)
        se=diff.std(ddof=1)/np.sqrt(D)
        cells.append(dict(label=label+'/paired_daily_difference',kind='paired_difference',n=D,net=diff.sum(),mean=diff.mean(),pf=np.nan,se=se,p=float(student.sf(diff.mean()/se,D-1))))
        tr.drop(columns='path').to_csv(OUT/f'dev_{label}_trades.csv',index=False)
        print(label,len(tr),tr.net.sum(),flush=True)
# BH once across every positive-mean test, with overlapping bins deliberately retained.
res=pd.DataFrame(cells)
order=np.argsort(res.p.to_numpy()); pv=res.p.to_numpy()[order]
q=np.minimum.accumulate((pv*len(pv)/np.arange(1,len(pv)+1))[::-1])[::-1].clip(0,1)
res['q']=np.nan; res.loc[order,'q']=q
res.to_csv(OUT/'dev_cells.csv',index=False)
pd.DataFrame(checks).to_csv(OUT/'dev_spot_checks.csv',index=False)
pd.DataFrame(power).to_csv(OUT/'dev_power.csv',index=False)
meta=dict(period='dev, in-sample',bars=len(df),days=D,years=years,start=str(df.trading_day.min()),end=str(df.trading_day.max()),cells=len(res),kind_counts=res.kind.value_counts().to_dict(),bh_discoveries=int((res.q<=.05).sum()),baseline_reproduction='four exact matches on trade count, bars, side, entry, exit, net; instrumented signals equal original signals')
(OUT/'dev_metadata.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta),flush=True)
print(res[res.kind!='decomposition'].to_string(index=False),flush=True)
