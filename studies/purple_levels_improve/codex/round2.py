"""Round 2: dev / in-sample only. Run with bytecode disabled from repo root."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
from math import erfc, sqrt
import numpy as np
import pandas as pd
from cltester.config import COMBINE_50K, TICK_VALUE, FEE_ROUND_TURN
from cltester.data import load_period, Bars
from cltester.engine import backtest, Fills
from cltester import topstep

OUT = Path('studies/purple_levels_improve/codex')
meta = json.loads((OUT/'dev_metadata.json').read_text())
D, years = meta['days'], meta['years']
cells, portfolios, sessions, denominator, yearly, matched, interaction = [], {}, [], [], [], [], []
def infer(label, estimate, influence, days, n):
    u = pd.Series(np.asarray(influence)).groupby(np.asarray(days)).sum()
    se = sqrt(D/(D-1)*np.square(u).sum())
    p = .5*erfc(estimate/se/sqrt(2)) if se else 1.
    row = dict(label=label, n=n, estimate=estimate, se=se, p=p)
    cells.append(row)
    return row
def mean_cell(g, label, col='rnet'):
    v = g[col].dropna()
    h = g.loc[v.index]
    return infer(label, v.mean(), (v-v.mean())/len(v), h.trading_day, len(v))
def diff_cell(a,b,label):
    av,bv = a.rnet,b.rnet
    return infer(label,av.mean()-bv.mean(),np.r_[(av-av.mean())/len(a),-(bv-bv.mean())/len(b)],
                 pd.concat([a.trading_day,b.trading_day]),len(a)+len(b))
def session(ts):
    ct=pd.to_datetime(ts,utc=True).dt.tz_convert('America/Chicago')
    m=ct.dt.hour*60+ct.dt.minute
    return np.select([(m>=1020)|(m<120),m<420,m<510,m<810],['Asia','London','Pre','RTH'],'Late')
hashes={'all_touch':'018fdfd1eb22','all_strict':'e0799b1e4110','nopd_touch':'b777ef9ec188','nopd_strict':'17242b70a399'}
signals={f:pd.read_csv(OUT/f'dev_{f}_signals.csv',index_col=0) for f in ('all','nopd')}
for label, h in hashes.items():
    t=pd.read_csv(f'results/purple_levels/dev_{h}.csv')
    old=pd.read_csv(OUT/f'dev_{label}_trades.csv')
    for col in ('signal_bar','entry_bar','exit_bar','entry','exit','net'):
        np.testing.assert_allclose(t[col],old[col],atol=1e-8)
    s=signals[label.split('_')[0]].loc[t.signal_bar].reset_index(drop=True)
    t['risk']=np.rint((s.limit-s.stop)*s.side/.01).astype(int)
    np.testing.assert_array_equal(t.risk,old.risk_ticks)
    t['test']=s.test_number.astype(int)
    t['sess']=session(t.entry_ts)
    t['rth']=t.sess.eq('RTH')
    t['year']=pd.to_datetime(t.trading_day).dt.year
    t['rgross']=t.gross/(t.risk*TICK_VALUE)
    t['rnet']=t.net/(t.risk*TICK_VALUE)
    proxy=t.ticks.abs().where(t.reason.isin(['target','stop']))
    t['claude_gross']=t.gross/(proxy*TICK_VALUE)
    t['claude_net']=t.net/(proxy*TICK_VALUE)
    denominator.append(dict(portfolio=label,n=len(t),excluded=int(proxy.isna().sum()),
        changed=int(((proxy-t.risk).abs()>1e-8).sum()),zero_proxy=int(proxy.eq(0).sum()),min_risk=int(t.risk.min())))
    t['proxy_risk']=proxy
    t['denominator_difference']=(t.claude_net-t.rnet).replace([np.inf,-np.inf],np.nan)
    mean_cell(t,label+'/denominator_difference',col='denominator_difference')
    for sess,g in t.groupby('sess',sort=False):
        row=mean_cell(g,label+'/session/'+sess)
        sessions.append(dict(portfolio=label,session=sess,n=len(g),win=(g.net>0).mean(),
             proxy_gross=g.claude_gross.mean(),proxy_net=g.claude_net.mean(),
             gross_R=g.rgross.mean(),net_R=g.rnet.mean(),net=g.net.sum(),**{'p':row['p']}))
    portfolios[label]=t
t=portfolios['all_strict']
bins=[0,8,12,18,25,40,np.inf]
t['bin']=pd.cut(t.risk,bins)
for bn,g in t.groupby('bin',observed=True):
    row=dict(bin=str(bn))
    for isr,h in g.groupby('rth'):
        mean_cell(h,f'all_strict/bin/{bn}/{isr}')
        row.update({('rth' if isr else 'other')+'_n':len(h),('rth' if isr else 'other')+'_R':h.rnet.mean()})
    matched.append(row)
# Standardize both groups to the same pooled stop-bin distribution.
estimate=0.; inf=np.zeros(len(t))
for bn,g in t.groupby('bin',observed=True):
    a,b=g[g.rth],g[~g.rth]
    assert len(a) and len(b)
    w=len(g)/len(t)
    estimate+=w*(a.rnet.mean()-b.rnet.mean())
    inf[a.index]+=w*(a.rnet-a.rnet.mean())/len(a)
    inf[b.index]-=w*(b.rnet-b.rnet.mean())/len(b)
matched_test=infer('all_strict/stop_standardized_RTH_minus_other',estimate,inf,t.trading_day,len(t))
# OLS with stop-bin and year fixed effects; daily cluster sandwich (CR1).
X=np.column_stack([np.ones(len(t)),t.rth.astype(float),
    pd.get_dummies(t['bin'],drop_first=True,dtype=float),pd.get_dummies(t.year,drop_first=True,dtype=float)])
y=t.rnet.to_numpy(); inv=np.linalg.pinv(X.T@X); beta=inv@X.T@y
score=X*(y-X@beta)[:,None]
us=pd.DataFrame(score).groupby(t.trading_day).sum().to_numpy()
cov=inv@(us.T@us)@inv*D/(D-1)*(len(t)-1)/(len(t)-X.shape[1])
regse=sqrt(cov[1,1]); reg=dict(label='all_strict/RTH_bin_year_adjusted',n=len(t),estimate=beta[1],se=regse,p=.5*erfc(beta[1]/regse/sqrt(2)))
cells.append(reg)
for yr,g in t.groupby('year'):
    row={'year':int(yr)}
    for isr,h in g.groupby('rth'):
        mean_cell(h,f'all_strict/year/{yr}/{isr}')
        row.update({('rth' if isr else 'other')+'_n':len(h),('rth' if isr else 'other')+'_R':h.rnet.mean(),
                    ('rth' if isr else 'other')+'_net':h.net.sum()})
    diff_cell(g[g.rth],g[~g.rth],f'all_strict/year/{yr}/contrast')
    yearly.append(row)
touch=portfolios['all_touch']
for name,mask in [('Asia',touch.sess.eq('Asia')),('RTH',touch.rth)]:
    g=touch[mask & (touch.risk>12)]
    mean_cell(g,'all_touch/>12/'+name)
    print('BIG_R',name,len(g),g.rgross.mean(),g.rnet.mean(),flush=True)
    g=touch[mask & (touch.proxy_risk>12)]
    mean_cell(g,'all_touch/proxy>12/'+name,col='claude_net')
    print('CLAUDE_BIG_R',name,len(g),g.claude_gross.mean(),g.claude_net.mean(),flush=True)
touchyear=[]
for yr,g in touch.groupby('year'):
    for label,mask in [('RTH',g.rth),('Pre_RTH',g.sess.isin(['Pre','RTH']))]:
        h=g[mask]; mean_cell(h,f'all_touch/year/{yr}/{label}')
        touchyear.append(dict(year=int(yr),window=label,n=len(h),net=h.net.sum(),R=h.rnet.mean()))
for isr in (False,True):
    for test in (1,2):
        g=t[(t.rth==isr)&(t.test==test)]
        mean_cell(g,f'all_strict/interaction/{isr}/{test}')
        interaction.append(dict(rth=isr,test=test,n=len(g),mean_net=g.net.mean(),mean_R=g.rnet.mean(),net=g.net.sum()))
    g=t[t.rth==isr]
    diff_cell(g[g.test==1],g[g.test==2],f'all_strict/first_minus_retest/{isr}')
di=0.; ii=np.zeros(len(t))
for isr in (False,True):
    for test in (1,2):
        g=t[(t.rth==isr)&(t.test==test)]
        sign=(1 if isr else -1)*(1 if test==1 else -1)
        di+=sign*g.rnet.mean(); ii[g.index]+=sign*(g.rnet-g.rnet.mean())/len(g)
interaction_test=infer('all_strict/first_RTH_interaction',di,ii,t.trading_day,len(t))
print('Loading dev for executable RTH sizing scenarios',flush=True)
df=load_period('dev'); bars=Bars.from_frame(df)
assert len(df)==meta['bars']
days=topstep.trading_days(df)
s=signals['all'][['side','limit','stop','target','expire_min']].copy()
# A bar's timestamp is its open; decision is available at its close, one minute later.
ct=df.ct.iloc[s.index]+pd.Timedelta(minutes=1)
m=(ct.dt.hour*60+ct.dt.minute).to_numpy()
s=s[(m>=510)&(m<810)].copy(); mm=m[(m>=510)&(m<810)]
s.expire_min=np.minimum(s.expire_min,810-mm)
scenarios=[]
for budget in (None,250,500):
    name='one_CL' if budget is None else f'risk_{budget}'
    sig=s.copy(); risk=np.rint((sig.limit-sig.stop)*sig.side/.01).astype(int)
    sig['qty']=1 if budget is None else np.minimum(COMBINE_50K.max_contracts,np.floor(budget/(risk*TICK_VALUE+FEE_ROUND_TURN))).astype(int)
    dropped=int((sig.qty==0).sum()); sig=sig[sig.qty>=1]
    tr=backtest(bars,sig,fills=Fills(through=1))
    assert tr.qty.between(1,5).all()
    entryct=pd.to_datetime(tr.entry_ts,utc=True).dt.tz_convert('America/Chicago')
    entryminute=entryct.dt.hour*60+entryct.dt.minute
    assert entryminute.between(510,809).all()
    mean_cell(tr,f'RTH_sizing/{name}',col='net')
    # Check deterministic first/middle/last against raw bars and signal sizing.
    for k in (0,len(tr)//2,len(tr)-1):
        z=tr.iloc[k]; j=int(z.entry_bar); q=int(z.qty); sd=int(z.side)
        lmt=round(sig.loc[z.signal_bar,'limit']/.01)
        assert (bars.l[j]<=lmt-1 if sd==1 else bars.h[j]>=lmt+1)
        assert np.isclose(z.net,(z.ticks*TICK_VALUE-FEE_ROUND_TURN)*q)
    roll=topstep.rolling(tr,days); seq=topstep.sequential(tr,days)
    su=topstep.summary(roll,seq,days)
    su.update(scenario=name,n=len(tr),rate=len(tr)/years,net=tr.net.sum(),mean=tr.net.mean(),
              avg_qty=tr.qty.mean(),max_qty=int(tr.qty.max()),skipped_signals=dropped,
              drift_trades=COMBINE_50K.profit_target/tr.net.mean(),
              drift_months=12*COMBINE_50K.profit_target/(tr.net.sum()/years),
              max_planned_risk=float(((sig.limit-sig.stop).abs()/.01*TICK_VALUE*sig.qty+sig.qty*FEE_ROUND_TURN).max()))
    scenarios.append(su)
    tr.drop(columns='path').to_csv(OUT/f'round2_dev_{name}_trades.csv',index=False)
    roll.to_csv(OUT/f'round2_dev_{name}_rolling.csv',index=False)
    seq.to_csv(OUT/f'round2_dev_{name}_sequential.csv',index=False)
    print('SIZING',json.dumps(su),flush=True)
new=pd.DataFrame(cells); old=pd.read_csv(OUT/'dev_cells.csv')[['label','p']]
assert np.isfinite(new[['estimate','se','p']].to_numpy()).all()
pooled=pd.concat([old,new],ignore_index=True); order=np.argsort(pooled.p.to_numpy())
pv=pooled.p.to_numpy()[order]; q=np.minimum.accumulate((pv*len(pv)/np.arange(1,len(pv)+1))[::-1])[::-1].clip(0,1)
pooled['q_BH']=np.nan; pooled.loc[order,'q_BH']=q
pooled['q_BY']=(pooled.q_BH*sum(1/i for i in range(1,len(pooled)+1))).clip(upper=1)
pooled.to_csv(OUT/'round2_dev_multiplicity.csv',index=False)
for name,rows in [('sessions',sessions),('denominator',denominator),('matched_bins',matched),('strict_years',yearly),('touch_years',touchyear),('interaction',interaction),('sizing',scenarios),('cells',cells)]:
    pd.DataFrame(rows).to_csv(OUT/f'round2_dev_{name}.csv',index=False)
summary=dict(scope='dev / in-sample',new_cells=len(new),pooled_tests=len(pooled),
             prior_evaluated_cells=164,total_codex_evaluated_cells=164+len(new),
             matched=matched_test,regression=reg,interaction=interaction_test)
(OUT/'round2_dev_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2),flush=True)
print(pd.DataFrame(sessions).to_string(index=False))
print(pd.DataFrame(matched).to_string(index=False))
print(pd.DataFrame(yearly).to_string(index=False))
print(pd.DataFrame(interaction).to_string(index=False))
print(pd.DataFrame(denominator).to_string(index=False))
print(pd.DataFrame(touchyear).to_string(index=False))
