import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json, math, time
import numpy as np
import pandas as pd
from cltester.data import load_period, Bars
from cltester.strategy import load, params_hash
from cltester.engine import backtest, Fills
from strategies.purple_levels_rth import rth_filter
O=Path('studies/all_strategies_improve/codex')
L=pd.read_csv('results/ledger.csv'); names=L.strategy.unique().tolist()
rows=[]; summary=[]; audit=[]; selections=[]; replay=[]; details={}; cells=[]; spots=[]
def log(s): print(s,flush=True)
def cell(kind,name,label,x,days,unit,extra=None):
 x=np.asarray(x,float); days=np.asarray(days); good=np.isfinite(x); x=x[good];days=days[good]
 n=len(x); mu=x.mean() if n else np.nan
 if n:
  z=pd.DataFrame({'x':x-mu,'day':days}).groupby('day').x.sum().reindex(DAYS,fill_value=0).to_numpy()
  se=np.sqrt(D/(D-1)*np.sum(z*z))/n
 else: se=np.nan
 p=.5*math.erfc(mu/se/math.sqrt(2)) if n and se>0 else np.nan
 r=dict(kind=kind,strategy=name,label=label,unit=unit,n=n,mean=mu,se=se,p=p,lo=mu-1.96*se,hi=mu+1.96*se)
 if extra:r.update(extra)
 cells.append(r);return r

def contrast(name,label,t,a,unit):
 a=np.asarray(a,bool);x=t[unit].to_numpy(); days=t.trading_day
 means=[]; influences=[]
 for mask in [a,~a]:
  n=mask.sum();m=x[mask].mean() if n else np.nan
  z=pd.DataFrame({'day':days[mask],'x':x[mask]-m}).groupby('day').x.sum().reindex(DAYS,fill_value=0).to_numpy()/n if n else np.full(D,np.nan)
  means.append(m);influences.append(z)
 z=influences[0]-influences[1];m=means[0]-means[1];se=np.sqrt(D/(D-1)*np.sum(z*z))
 r=dict(kind='session_contrast',strategy=name,label=label,unit=unit,n=len(t),n_rth=int(a.sum()),n_other=int((~a).sum()),mean=m,se=se,p=.5*math.erfc(m/se/math.sqrt(2)) if se>0 else np.nan,lo=m-1.96*se,hi=m+1.96*se,rth=means[0],other=means[1]);cells.append(r)
 return r,z

def enrich(t,sig):
 t=t.copy();t['trading_day']=pd.to_datetime(t.trading_day); b=t.signal_bar.to_numpy(int)
 s=sig.reindex(b); risk=np.abs(np.rint(s.limit.to_numpy(float)*100)-np.rint(s.stop.to_numpy(float)*100))
 t['risk']=risk;t['gross_ticks']=t.gross/(10*t.qty);t['gross_R']=t.gross/(10*t.qty*risk);t['net_R']=t.net/(10*t.qty*risk)
 j=t.entry_bar.to_numpy(int);side=t.side.to_numpy();lim=np.rint(s.limit.to_numpy()*100)
 t['through']=np.where(side==1,B.l[j]<=lim-1,B.h[j]>=lim+1)
 ct=df.ct_minute.to_numpy()[j];t['rth']=(ct>=510)&(ct<810)
 t['session']=np.select([(ct>=1020)|(ct<120),(ct>=120)&(ct<420),(ct>=420)&(ct<510),(ct>=510)&(ct<810)],['Asia','London','Pre','RTH'],default='Late')
 t['stop_bin']=pd.cut(risk,[0,8,16,np.inf],labels=['<=8','9-16','>16']).astype(str)
 t['regime']=regime.reindex(t.trading_day).to_numpy()
 return t

def run(st,sig,p,through):return st.day_rules(backtest(B,sig,Fills(through=through),manage=st.manage,overlap=st.OVERLAP),p)

log('Loading dev only');df=load_period('dev');B=Bars.from_frame(df);DAYS=pd.Index(df.trading_day.unique());D=len(DAYS); YEARS=(df.trading_day.max()-df.trading_day.min()).days/365.25
daily=df.groupby('trading_day').agg(high=('high','max'),low=('low','min'));rng=daily.high-daily.low;prior=rng.shift(1);cut=prior.rolling(60,min_periods=20).median();regime=pd.Series(np.where(cut.isna(),'unknown',np.where(prior<=cut,'prior_quiet','prior_large')),index=daily.index)
log(f'{len(df)} bars, {D} days')
# Audit all unique historical hashes in ticks; rank canonical latest parameter records for primary work.
canon={}
for name in names:
 g=L[(L.strategy==name)&(L.period=='dev')].copy();g['key']=g.params.map(lambda v:json.dumps(json.loads(v),sort_keys=True));c=g.drop_duplicates('key',keep='last').sort_values(['net','hash']);canon[name]=c
 for _,r in g.drop_duplicates('hash',keep='last').iterrows():
  t=pd.read_csv(f'results/{name}/dev_{r.hash}.csv');days=pd.to_datetime(t.trading_day)
  cell('historical_ticks',name,r.hash,t.gross/(10*t.qty),days,'gross_ticks')
 h=g.drop_duplicates('hash',keep='last').sort_values(['net','hash'])
 for typ,i in [('best',-1),('median',(len(h)-1)//2)]:
  r=h.iloc[i];cc=[z for z in cells if z['strategy']==name and z['label']==r.hash][-1];audit.append(dict(selection=typ,hash=r.hash,ledger_net=r.net,**cc))
 summary.append(dict(strategy=name,dev_rows=len(g),dev_hashes=g.hash.nunique(),param_sets=len(c),validation_rows=int(((L.strategy==name)&(L.period=='validation')).sum()),holdout_rows=int(((L.strategy==name)&(L.period=='holdout')).sum())))
pd.DataFrame(summary).to_csv(O/'ledger_inventory.csv',index=False);pd.DataFrame(audit).to_csv(O/'archive_best_median.csv',index=False)
# Generate selected signals once per exact parameter key. Current replays quantify obsolete-row discrepancies.
for name,c in canon.items():
 for typ,i in [('best',-1),('median',(len(c)-1)//2)]:
  r=c.iloc[i];p=json.loads(r.params);fill=1 if p.pop('fills','touch')=='through1' else 0;st=load(name);p={**st.PARAMS,**p};key=(name,json.dumps(p,sort_keys=True),fill)
  if key in details:t,sig=details[key]
  else:
   log(f'signals/replay {name} {typ} {r.hash}');sig=st.signals(df,p);t=run(st,sig,p,fill);t=enrich(t,sig);details[key]=(t,sig)
  old=pd.read_csv(f'results/{name}/dev_{r.hash}.csv');cols=['signal_bar','entry_bar','exit_bar','side','qty','entry','exit','gross','net']
  same=len(t)==len(old) and np.allclose(t[cols].to_numpy(float),old[cols].to_numpy(float))
  replay.append(dict(strategy=name,selection=typ,hash=r.hash,current_hash=params_hash(name,{**p,**({'fills':'through1'} if fill else {})},st.DEPENDS),ledger_n=len(old),replay_n=len(t),ledger_net=old.net.sum(),replay_net=t.net.sum(),match=same))
  for u in ['gross_ticks','gross_R']:
   cc=cell('triage',name,typ,t[u],t.trading_day,u,dict(hash=r.hash,ledger_match=same,net=t.net.sum(),fill=fill,param_sets=len(c)))
  selections.append(dict(strategy=name,selection=typ,hash=r.hash,params=p,fill=fill,key=list(key)))
  if typ=='best':
   t.drop(columns=['path'],errors='ignore').to_csv(O/f'{name}_best_dev_trades.csv',index=False)
   sig.to_csv(O/f'{name}_best_dev_signals.csv')
  # deterministic two raw-bar fill and exit checks per selected portfolio
  for k in sorted(set([0,len(t)-1])) if len(t) else []:
   tr=t.iloc[k];j=int(tr.entry_bar);ex=int(tr.exit_bar);si=sig.loc[int(tr.signal_bar)];sd=int(tr.side);lim=round(si.limit*100);ent=round(tr.entry*100)
   reached=B.l[j]<=lim-fill if sd==1 else B.h[j]>=lim+fill
   expected=min(B.o[j],lim) if sd==1 else max(B.o[j],lim)
   exit_in_bar=B.l[ex]<=round(tr.exit*100)<=B.h[ex]
   spots.append(dict(strategy=name,selection=typ,entry_ts=str(tr.entry_ts),reason=tr.reason,entry_ok=bool(reached and ent==expected),exit_in_raw_range=bool(exit_in_bar),signal_before_fill=int(tr.signal_bar)<j,same_contract=B.sym_id[j]==B.sym_id[ex]))
 pd.DataFrame(cells).to_csv(O/'cells_partial.csv',index=False)
pd.DataFrame(replay).to_csv(O/'replay_checks.csv',index=False);pd.DataFrame(spots).to_csv(O/'spot_checks.csv',index=False)
(O/'selections.json').write_text(json.dumps(selections,indent=2))
# All other families: mandatory session check even when triage fails.
pool={u:[] for u in ['gross_R','net_R']};session_results=[];strict_best={}
for sel in [s for s in selections if s['selection']=='best']:
 name=sel['strategy'];p=sel['params'];key=tuple(sel['key']);touch,sig=details[key];st=load(name)
 log('Strict session replay '+name)
 if st.manage is not None: st.signals(df,p)  # initialize state used by manage on strict replay
 strict=touch if sel['fill']==1 else enrich(run(st,sig,p,1),sig);strict_best[name]=strict
 strict.drop(columns=['path'],errors='ignore').to_csv(O/f'{name}_best_strict_dev_trades.csv',index=False)
 cell('strict_baseline',name,'unchanged_strict',strict.net,strict.trading_day,'net_dollars')
 if name not in ['purple_levels','purple_levels_rth','purple_pa']:
  for u in ['gross_R','net_R']:
   rr,z=contrast(name,'strict_RTH_minus_other',strict,strict.rth,u);pool[u].append(z);session_results.append(rr)
   for label,mask in [('RTH',strict.rth),('other',~strict.rth)]:cell('session_group',name,'strict_'+label,strict.loc[mask,u],strict.loc[mask,'trading_day'],u)
for u,zz in pool.items():
 rs=[r for r in session_results if r['unit']==u and np.isfinite(r['mean'])];zz=[z for z in zz if np.isfinite(z).all()];z=np.mean(zz,axis=0);mu=np.mean([r['mean'] for r in rs]);se=np.sqrt(D/(D-1)*np.sum(z*z));cells.append(dict(kind='session_pooled',strategy='equal_strategy',label='strict_RTH_minus_other',unit=u,n=len(rs),mean=mu,se=se,p=.5*math.erfc(mu/se/math.sqrt(2)),lo=mu-1.96*se,hi=mu+1.96*se))
log('Triage done; starting predeclared survivor decompositions')
survivors=[s['strategy'] for s in selections if s['selection']=='best' and next(r for r in cells if r['kind']=='triage' and r['strategy']==s['strategy'] and r['label']=='best' and r['unit']=='gross_ticks')['p']<.05]
log('Survivors '+str(survivors))
for name in survivors:
 sel=next(s for s in selections if s['strategy']==name and s['selection']=='best');touch,_=details[tuple(sel['key'])]
 for mode,t in [('touch',touch),('strict',strict_best[name])]:
  for field in ['session','side','stop_bin','through','regime']:
   for val,sub in t.groupby(field):
    for u in ['gross_ticks','gross_R','net_R']:
     cell('decomposition',name,f'{mode}/{field}/{val}',sub[u],sub.trading_day,u,dict(net=sub.net.sum(),risk_mean=sub.risk.mean()))
# Maximum one allowed new revision: purple_pa RTH only if it survives, frozen levels family untouched.
for name in [n for n in survivors if n=='purple_pa']:
 sel=next(s for s in selections if s['strategy']==name and s['selection']=='best');p=sel['params'];touch,sig=details[tuple(sel['key'])];st=load(name);filtered=rth_filter(df,sig)
 for fill,base in [(0,touch),(1,strict_best[name])]:
  log(f'Revision {name} RTH through{fill}');t=enrich(run(st,filtered,p,fill),filtered)
  t.drop(columns=['path'],errors='ignore').to_csv(O/f'{name}_rth_through{fill}_dev_trades.csv',index=False)
  cell('revision',name,f'RTH_through{fill}',t.net,t.trading_day,'net_dollars',dict(total_net=t.net.sum(),pf=t.loc[t.net>0,'net'].sum()/-t.loc[t.net<0,'net'].sum(),risk_mean=t.risk.mean()))
  a=t.groupby('trading_day').net.sum().reindex(DAYS,fill_value=0);b=base.groupby('trading_day').net.sum().reindex(DAYS,fill_value=0);delta=a-b
  cell('paired_change',name,f'RTH_through{fill}',delta,DAYS,'daily_net_dollars',dict(total_delta=delta.sum(),base_net=b.sum(),new_net=a.sum()))
  pd.DataFrame({'baseline':b,'revision':a,'delta':delta}).to_csv(O/f'{name}_rth_through{fill}_paired_days.csv')
  for year,g in t.groupby(t.trading_day.dt.year):
   # counted descriptive annual cells, no additional inference
   cells.append(dict(kind='revision_year',strategy=name,label=f'through{fill}/{year}',unit='net_dollars',n=len(g),mean=g.net.mean(),total_net=g.net.sum()))
# power for each best strict portfolio and changes; no new tuned cells
for name,t in strict_best.items():
 rr=cell('power_input',name,'strict_net_R',t.net_R,t.trading_day,'net_R');n=rr['n'];mu=rr['mean'];se=rr['se'];need=(2.802*se/mu)**2*n if mu>0 and n else np.inf
 cells.append(dict(kind='power',strategy=name,label='selected_strict_effect',unit='trades',n=n,mean=need,years=need/(n/YEARS)) )
for r in list(cells):
 if r['kind']=='paired_change':
  need=(2.802*r['se']/r['mean'])**2*D if r['mean']>0 else np.inf
  cells.append(dict(kind='power',strategy=r['strategy'],label=r['label'],unit='days',n=D,mean=need,years=need/(D/YEARS)))
C=pd.DataFrame(cells);ix=C.p.notna();pvals=C.loc[ix,'p'].to_numpy();order=np.argsort(pvals);m=len(order);adjust=np.minimum.accumulate((pvals[order]*m/np.arange(1,m+1))[::-1])[::-1];q=np.empty(m);q[order]=np.minimum(1,adjust);C.loc[ix,'BH']=q;C.loc[ix,'BY']=np.minimum(1,q*np.sum(1/np.arange(1,m+1)));C.to_csv(O/'cells.csv',index=False)
(O/'metadata.json').write_text(json.dumps(dict(dev_bars=len(df),dev_days=D,first=str(df.trading_day.min()),last=str(df.trading_day.max()),survivors=survivors,evaluated_cells=len(C),inferential_cells=m,cell_counts=C.kind.value_counts().to_dict(),all_replays_match=all(r['match'] for r in replay)),indent=2))
log('COMPLETE '+(O/'metadata.json').read_text())
