"""Year-stratified day-schedule randomization; all orders, not filled-trade selection.
No strategy features on destination dates. Original exact CT signal minute, side,
close-to-limit offset, stop/target/kill offsets, expiry and within-day order schedule
preserved. Destination days sampled without replacement within year, maintaining
at most one source schedule per day. Engine touch fills, day_rules attempts=1.
Nominal tail probability is descriptive after a 1728-version screen, not a
familywise inference. Only dev data saved by round3.py is loaded.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
import json,time
import numpy as np
import pandas as pd
from cltester.data import Bars, load_period
from cltester.engine import backtest
from strategies.cbr import Strategy
OUT=Path(__file__).resolve().parent
SEED=20261120
N=1000

def main():
    rng=np.random.default_rng(SEED)
    cache=OUT/'round3_rth_bars.pkl'
    if cache.exists():
        df=pd.read_pickle(cache)
    else:
        df=load_period('dev')
        df=df[(df.ct_minute>=570)&(df.ct_minute<=960)].reset_index(drop=True)
    templates=pd.read_pickle(OUT/'round3_templates.pkl').reset_index(drop=True)
    days=np.sort(df.trading_day.unique())
    did=pd.Index(days).get_indexer(df.trading_day)
    minute=df.ct_minute.to_numpy()-570
    lookup=np.full((len(days),391),-1,dtype=np.int64)
    lookup[did,minute]=np.arange(len(df))
    # Require all possible signal minutes; missing destination minutes would change the schedule.
    eligible=(lookup[:,:60]>=0).all(axis=1)
    source_days=np.sort(templates.day.unique())
    source_id=pd.Index(source_days).get_indexer(templates.day)
    years=pd.DatetimeIndex(source_days).year
    dst_year=pd.DatetimeIndex(days).year
    groups=[(np.flatnonzero(years==y),np.flatnonzero((dst_year==y)&eligible)) for y in np.unique(years)]
    orig_minute=templates.minute.to_numpy()-570
    offsets=templates[['limit','stop','target','kill']].to_numpy(dtype=int)
    close=np.rint(df.close.to_numpy()*100).astype(int)
    base=templates[['side','expire']].copy()
    bars=Bars.from_frame(df)
    strategy=Strategy()
    actual=pd.read_pickle(OUT/'round3_trades.pkl')
    orig_dst=pd.Index(days).get_indexer(templates.day)
    original_indices=lookup[orig_dst,orig_minute]
    check_sig=base.copy()
    check_sig[['limit','stop','target','kill']]=(close[original_indices,None]+offsets)/100
    check_sig.index=original_indices
    replay=strategy.day_rules(backtest(bars,check_sig),{'attempts':1})
    assert len(replay)==len(actual) and np.allclose(replay.net,actual.net)
    print('Compact replay matches full dev bars exactly',flush=True)
    results=[]; start=time.time()
    for rep in range(N):
        mapping=np.empty(len(source_days),dtype=int)
        for src,dst in groups: mapping[src]=rng.choice(dst,len(src),replace=False)
        indices=lookup[mapping[source_id],orig_minute]
        assert (indices>=0).all() and len(np.unique(indices))==len(indices)
        sig=base.copy()
        sig[['limit','stop','target','kill']]=(close[indices,None]+offsets)/100
        sig.index=indices
        tr=strategy.day_rules(backtest(bars,sig),{'attempts':1})
        net=tr.net.to_numpy()
        results.append(dict(rep=rep,trades=len(tr),net=float(net.sum()),pf=float(net[net>0].sum()/-net[net<0].sum()),long_net=float(tr.loc[tr.side==1,'net'].sum()),short_net=float(tr.loc[tr.side==-1,'net'].sum())))
        if rep%50==0: print(rep,round(time.time()-start,1),'seconds',flush=True)
    r=pd.DataFrame(results)
    r.to_csv(OUT/'round3_null.csv',index=False)
    result=dict(seed=SEED,replicates=N,source_days=len(source_days),eligible_destination_days=int(eligible.sum()),orders=len(templates),actual_net=float(actual.net.sum()),net_mean=float(r.net.mean()),net_median=float(r.net.median()),net_ci95=r.net.quantile([.025,.975]).tolist(),fraction_profitable=float((r.net>0).mean()),pf_median=float(r.pf.median()),trades_median=float(r.trades.median()),trades_ci95=r.trades.quantile([.025,.975]).tolist(),one_sided_nominal_p_plus_one=float((1+(r.net>=actual.net.sum()).sum())/(N+1)),mean_long_net=float(r.long_net.mean()),mean_short_net=float(r.short_net.mean()))
    (OUT/'round3_null_summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__': main()
