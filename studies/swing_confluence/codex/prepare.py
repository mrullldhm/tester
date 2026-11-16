"""Read only CL dev files, audit construction and derive PIT features. Run from repo root."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from cltester.data import add_session, to_ticks
from cltester.swings import swing_state, build_candles
from studies.swing_confluence.build import RangeExtreme

OUT=Path('studies/swing_confluence/codex')

def raw():
    # Never invoke load_period: its padded loader opens year=2022 before filtering.
    cols=['ts','raw_symbol','high','low','close','open']
    d=pd.concat([pd.read_parquet(f'data/cl1/year={y}.parquet',columns=cols,
        filters=[('ts','>=',pd.Timestamp('2010-06-01',tz='UTC')),('ts','<',pd.Timestamp('2022-01-01',tz='UTC'))])
        for y in range(2010,2022)],ignore_index=True)
    d=add_session(d.sort_values('ts').reset_index(drop=True))
    return d[(d.trading_day>='2010-06-01')&(d.trading_day<'2022-01-01')].reset_index(drop=True)

def main():
    d=raw(); e=pd.read_parquet('data/studies/swing_confluence_dev.parquet')
    assert d.trading_day.max()<pd.Timestamp('2022-01-01')
    assert (d.ts.iloc[e.bar.to_numpy()].to_numpy()==e.ts.to_numpy()).all()
    ts=pd.DatetimeIndex(d.ts).as_unit('ns').asi8; h=to_ticks(d.high); l=to_ticks(d.low); c=to_ticks(d.close)
    n=len(d); print('raw',n,flush=True)
    rx=RangeExtreme(h,l); i=e.bar.to_numpy(); side=e.side.to_numpy(); ev=e.price.to_numpy(); op=e.opp.to_numpy()
    lo=np.minimum(ev,op); hi=np.maximum(ev,op)
    ju=rx.first_above(i+1,hi); jd=rx.first_below(i+1,lo); end=np.minimum(ju,jd); valid=end<n
    e['end_bar']=end
    e['elapsed']=np.where(valid,(ts[np.minimum(end,n-1)]-ts[i])/6e10,np.nan)
    e['fair_tick']=np.where(side==1,(c[i]-(lo-1))/(hi-lo+2),((hi+1)-c[i])/(hi-lo+2)).clip(0,1)
    e['confirm_beyond']=(c[i]<lo)|(c[i]>hi)
    checks={"raw_bars":n,"event_count":len(e),"outcome_mismatch":int((np.where(ju==jd,-1,np.where(side==1,ju<jd,jd<ju).astype(int))!=e.outcome).sum()),
        "minutes_not_wall_clock":int((valid & (e.elapsed.to_numpy()!=e.minutes.to_numpy())).sum()),"confirmation_outside_range":int(e.confirm_beyond.sum()),
        "negative_raw_bars":int(((h<0)|(l<0)).sum())}
    # Independent direct linear first-passage checks, deterministic sample.
    rng=np.random.default_rng(20261116); sampled=rng.choice(len(e),1200,replace=False)
    for k in sampled:
        a=i[k]+1; b=min(int(end[k])+1,n)
        uu=np.flatnonzero(h[a:b]>hi[k]); dd=np.flatnonzero(l[a:b]<lo[k])
        assert (a+uu[0] if len(uu) else n)==ju[k] or ju[k]>=b
        assert (a+dd[0] if len(dd) else n)==jd[k] or jd[k]>=b
    checks['linear_first_passage_checks']=len(sampled)
    # Synthetic sparse-table edge cases including negative levels, start==n and no crossing.
    for size in [1,2,3,17,63]:
        hh=rng.integers(-20,21,size); ll=hh-rng.integers(0,6,size); rr=RangeExtreme(hh,ll)
        for start in range(size+1):
            levels=np.arange(-25,26); starts=np.full(len(levels),start)
            aa=rr.first_above(starts,levels); bb=rr.first_below(starts,levels)
            for k,v in enumerate(levels):
                u=np.flatnonzero(hh[start:]>v); z=np.flatnonzero(ll[start:]<v)
                assert aa[k]==(start+u[0] if len(u) else size)
                assert bb[k]==(start+z[0] if len(z) else size)
    print('passage checked',flush=True)
    # Prospective quarter-leg touch limit: strict break barriers become touch levels +/-1 tick.
    limit=ev+side*np.ceil(e.leg.to_numpy()*.25).astype(int)
    ent_up=rx.first_below(i+1,limit+1); ent_dn=rx.first_above(i+1,limit-1)
    ent=np.where(side==1,ent_up,ent_dn)
    fill=(ent<end)&(ent<n)&~e['roll'].to_numpy() # Exclude original roll as well; conservative.
    # post-entry passage; same-bar stop/target included, ambiguity tracked.
    a=np.minimum(ent,n)
    lu=rx.first_above(a,hi); ld=rx.first_below(a,lo)
    le=np.minimum(lu,ld); y=np.where(side==1,lu<ld,ld<lu).astype(int)
    sym=pd.factorize(d.raw_symbol)[0]; rc=np.r_[0,np.cumsum(sym[1:]!=sym[:-1])]
    good=fill&(lu!=ld)&(le<n)&(rc[np.minimum(le,n-1)]==rc[i])
    e['limit_fill']=good
    e['limit_outcome']=y
    e['limit_fair']=np.where(side==1,(limit-(lo-1))/(hi-lo+2),((hi+1)-limit)/(hi-lo+2))
    e['limit_elapsed']=np.where(good,(ts[np.minimum(le,n-1)]-ts[np.minimum(ent,n-1)])/6e10,np.nan)
    days=d.trading_day.to_numpy(); e['limit_same_day']=days[np.minimum(le,n-1)]==days[i]
    checks['limit_entry_bar_ambiguous']=int((fill&(lu==ld)).sum())
    checks['limit_filled_eligible']=int(good.sum())
    # Event-derived sequential features require historical event to have resolved before current i.
    for name in ['speed','delay','touches','sweep_depth','reclaim','prior_failed','nested','origin_roll','backward','dual','flag_mismatch']:
        e[name]=np.nan
    evidence=[]; audit_examples=[]; prefix=[]
    # 1m PIT state counts for nested structure, no final swings.
    s1=swing_state(d,'1m',prev=True,newest=True)
    chh=s1['1m_sh_ts'].ne(s1['1m_sh_ts'].shift()).to_numpy() & s1['1m_sh'].notna().to_numpy()
    chl=s1['1m_sl_ts'].ne(s1['1m_sl_ts'].shift()).to_numpy() & s1['1m_sl'].notna().to_numpy()
    cumh=np.r_[0,np.cumsum(chh)]; cuml=np.r_[0,np.cumsum(chl)]
    for base in ['1m','5m','15m','1h','4h','1d']:
        s=s1 if base=='1m' else swing_state(d,base,prev=True,newest=True)
        cd=build_candles(d,base)
        for si,key,opp in [(1,'sl','sh'),(-1,'sh','sl')]:
            ids=e.index[(e.base==base)&(e.side==si)].to_numpy(); ee=e.loc[ids]; ii=ee.bar.to_numpy()
            pt=pd.DatetimeIndex(s[f'{base}_{key}_ts']).as_unit('ns').asi8
            ot=pd.DatetimeIndex(s[f'{base}_{opp}_ts']).as_unit('ns').asi8
            first=np.searchsorted(ts,pt[ii]); before=np.maximum(first-1,0)
            e.loc[ids,'origin_roll']=(rc[ii]!=rc[first]).astype(int)
            e.loc[ids,'backward']=(pt[ii]<=pt[ii-1]).astype(int)
            # Same update changed both levels; newest-before alone cannot classify replacement.
            other=pd.DatetimeIndex(s[f'{base}_{opp}_ts']).as_unit('ns').asi8
            dual=(other[ii]!=other[ii-1])
            e.loc[ids,'dual']=dual.astype(int)
            prevp=s[f'{base}_{key}'].to_numpy()[ii-1]
            true_simple=(s[f'{base}_newest'].to_numpy()[ii-1]==-si)&~dual&np.isfinite(prevp)
            e.loc[ids,'flag_mismatch']=(ee['replace'].to_numpy()!=true_simple).astype(int)
            duration=(pt[ii]-ot[ii])/6e10
            e.loc[ids,'speed']=np.where(duration>=0,duration/ee.leg,np.nan)
            e.loc[ids,'delay']=(ts[ii]-pt[ii])/6e10
            old=to_ticks(s[f'{base}_{key}'].fillna(-.01))[before]
            dep=si*(old-ee.price.to_numpy())/ee.leg.to_numpy()
            dep[old<0]=np.nan
            e.loc[ids,'sweep_depth']=dep
            # Count disjoint exact-level touch episodes during candidate+confirmation, not after signal.
            count=[]; rec=[]
            for a,b,p,v in zip(first,ii,ee.price.to_numpy(),old,strict=True):
                hits=(l[a:b+1]==p) if si==1 else (h[a:b+1]==p)
                count.append(int((hits & ~np.r_[False,hits[:-1]]).sum()))
                if v<0: rec.append(-1); continue
                swept=np.flatnonzero(l[a:b+1]<v) if si==1 else np.flatnonzero(h[a:b+1]>v)
                if not len(swept): rec.append(0); continue
                u=a+swept[0]+1
                recovered=(h[u:b+1]>=v).any() if si==1 else (l[u:b+1]<=v).any()
                rec.append(1 if recovered else 2)
            e.loc[ids,'touches']=count; e.loc[ids,'reclaim']=rec
            nh=cumh[ii+1]-cumh[first]; nl=cuml[ii+1]-cuml[first]
            e.loc[ids,'nested']=np.sign((nh-nl)*si)
            prev=np.r_[-1,ids[:-1]]; pidx=np.maximum(prev,0)
            e.loc[ids,'prior_failed']=np.where(prev>=0,(e.loc[pidx,'outcome'].to_numpy()==0)&(end[pidx]<=ii),False).astype(int)
            # One raw-bar spot check for each side/base except very small sample.
            eligible=ids[(ee.outcome.to_numpy()>=0)&~ee['roll'].to_numpy()&(ee.leg.to_numpy()>=6)]
            k=int(eligible[len(eligible)//2]); row=e.loc[k]; b=int(row.bar); p=int(np.searchsorted(ts,pt[b])); q=int(np.searchsorted(cd.first,p)); q=min(q,len(cd)-2)
            # q should be exact first index of event candle.
            q=int(np.flatnonzero(cd.first==p)[0]); rr=int(end[k]); stop=min(rr+1,n)
            aa={"base":base,"side":si,"bar":b,"known":str(d.ts.iloc[b]),"pivot_start":str(d.ts.iloc[p]),"event":int(row.price),"opp":int(row.opp),"close_baseline":int(c[b]),"fair":float(row.fair),"outcome":int(row.outcome),"resolve":str(d.ts.iloc[rr]),"resolve_high":int(h[rr]),"resolve_low":int(l[rr]),"pre_max":int(h[b+1:rr].max()) if rr>b+1 else None,"pre_min":int(l[b+1:rr].min()) if rr>b+1 else None,
                "candles":[{"start":str(cd.ts[t]),"high":int(cd.h[t]),"low":int(cd.l[t]),"avail":str(d.ts.iloc[cd.avail[t]])} for t in range(max(q-1,0),q+2)]}
            audit_examples.append(aa)
            if base in ['5m','1h','1d']:
                cut=swing_state(d.iloc[:b+1],base,prev=True,newest=True)
                cols=[f'{base}_{v}' for v in ['sh','sl','sh2','sl2','newest']]
                prefix.append({'base':base,'side':si,'bar':b,'equal':all((pd.isna(s[x].iloc[b]) and pd.isna(cut[x].iloc[-1])) or s[x].iloc[b]==cut[x].iloc[-1] for x in cols)})
            # Concrete problematic examples with raw state evidence.
            for label,mask in [('backward',e.loc[ids,'backward'].to_numpy()==1),('dual_replace',dual&ee['replace'].to_numpy()),('origin_roll',e.loc[ids,'origin_roll'].to_numpy()==1)]:
                ix=np.flatnonzero(mask)
                if len(ix):
                    z=int(ix[0]); bb=int(ii[z]); evidence.append({'type':label,'base':base,'side':si,'ts':str(d.ts.iloc[bb]),'bar':bb,'price':int(ee.price.iloc[z]),'old_same_ts':str(s[f'{base}_{key}_ts'].iloc[bb-1]),'new_same_ts':str(s[f'{base}_{key}_ts'].iloc[bb]),'old_opp_ts':str(s[f'{base}_{opp}_ts'].iloc[bb-1]),'new_opp_ts':str(s[f'{base}_{opp}_ts'].iloc[bb]),'newest_before':int(s[f'{base}_newest'].iloc[bb-1]),'replace':bool(ee['replace'].iloc[z])})
        print('features',base,flush=True)
    del s1
    # w/mo point-in-time availability at a completed group close vs truncated prefix.
    for tf in ['1w','1mo']:
        full=build_candles(d,tf)
        # choose completed right candle in 2016 with state update
        ss=swing_state(d,tf,prev=True,newest=True)
        changes=np.flatnonzero(ss[f'{tf}_sh_ts'].ne(ss[f'{tf}_sh_ts'].shift()).to_numpy()&ss[f'{tf}_sh'].notna().to_numpy()&(d.ts.dt.year.to_numpy()==2016))
        b=int(changes[0]); cc=swing_state(d.iloc[:b+1],tf,prev=True,newest=True)
        prefix.append({'base':tf,'bar':b,'ts':str(d.ts.iloc[b]),'full_sh':float(ss[f'{tf}_sh'].iloc[b]),'prefix_sh':float(cc[f'{tf}_sh'].iloc[-1]),'full_sh_ts':str(ss[f'{tf}_sh_ts'].iloc[b]),'prefix_sh_ts':str(cc[f'{tf}_sh_ts'].iloc[-1])})
        print('prefix',tf,flush=True)
    e.to_parquet(OUT/'enriched.parquet',index=False)
    checks['prefix']=prefix; checks['examples']=audit_examples; checks['evidence']=evidence
    checks['counts']=e.groupby('base')[['backward','dual','flag_mismatch','origin_roll']].sum().to_dict()
    bad=e[valid & (e.elapsed.to_numpy()!=e.minutes.to_numpy())].iloc[0]
    checks['minutes_example']={k:str(bad[k]) for k in ['base','side','ts','minutes','elapsed','end_bar']}
    checks['negative_example']=d[(h<0)|(l<0)][['ts','high','low']].head(1).astype(str).to_dict('records')
    (OUT/'audit_evidence.json').write_text(json.dumps(checks,indent=2,allow_nan=True))
    print('saved',flush=True)

if __name__=='__main__': main()
