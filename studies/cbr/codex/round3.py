"""Independent, dev-only CBR audit. Writes only beside this script; no validation reads.
Run PYTHONDONTWRITEBYTECODE=1 .venv/bin/python studies/cbr/codex/round3.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import json
import hashlib
import numpy as np
import pandas as pd
from cltester.data import load_period, Bars
from cltester.engine import backtest, Fills
from cltester import metrics, topstep
from strategies.cbr import Strategy

OUT = Path(__file__).resolve().parent
P = dict(window='rth', context='reb', bias='none', ext='e20', target='r2', attempts=1)
SEED = 20261119

def main():
    rng = np.random.default_rng(SEED)
    print('Loading dev only', flush=True)
    df = load_period('dev')
    days = topstep.trading_days(df)
    s = Strategy()
    cache = OUT / 'round3_signals.pkl'
    print('Building signals', flush=True)
    sig = s.signals(df, P)
    sig.to_pickle(cache)
    bars = Bars.from_frame(df)
    t = s.day_rules(backtest(bars, sig), P)
    t.to_pickle(OUT/'round3_trades.pkl')
    t.drop(columns='path').to_csv(OUT/'round3_trades.csv', index=False)
    st = metrics.summary(t, days)
    grid = pd.read_csv(OUT.parent/'grid_dev_screened.csv')
    row = grid[np.logical_and.reduce([grid[k].eq(v) for k,v in P.items()])].iloc[0]
    assert len(t)==row.trades and abs(t.net.sum()-row.net)<0.01, (st, row.to_dict())
    print('Rebuilt', len(sig), 'signals', st, flush=True)
    per = t.assign(year=pd.to_datetime(t.trading_day).dt.year).groupby('year').apply(lambda x: pd.Series(dict(trades=len(x),net=x.net.sum(),pf=x.loc[x.net>0,'net'].sum()/-x.loc[x.net<0,'net'].sum(),long_net=x.loc[x.side==1,'net'].sum(),short_net=x.loc[x.side==-1,'net'].sum())),include_groups=False)
    per.to_csv(OUT/'round3_years.csv')
    side = t.groupby('side').apply(lambda x: pd.Series(metrics.summary(x, days)),include_groups=False)
    side.to_csv(OUT/'round3_sides.csv')
    daily = metrics.daily_pnl(t, days).to_numpy()
    boots = {}
    for block in (1,5,20):
        # Circular moving blocks on complete ordered dev trading days, including zero-trade days.
        sums = []
        for _ in range(10000):
            starts=rng.integers(len(daily),size=int(np.ceil(len(daily)/block)))
            ix=(starts[:,None]+np.arange(block))%len(daily)
            sums.append(daily[ix.ravel()[:len(daily)]].sum())
        sums=np.asarray(sums)
        boots[str(block)]=dict(net_ci95=np.quantile(sums,[.025,.975]).tolist(),fraction_nonpositive=float(np.mean(sums<=0)))
    concentration = dict(top10_net=float(np.sort(daily)[-10:].sum()),top10_share=float(np.sort(daily)[-10:].sum()/daily.sum()),net_without_top10=float(daily.sum()-np.sort(daily)[-10:].sum()),largest_win=float(daily.max()),largest_loss=float(daily.min()))
    # Five deterministic checks: first/last target, first/last stop, largest absolute gross.
    choices = [t[t.reason=='target'].index[0],t[t.reason=='target'].index[-1],t[t.reason=='stop'].index[0],t[t.reason=='stop'].index[-1],t.gross.abs().idxmax()]
    checks=[]
    for ix in dict.fromkeys(choices):
        tr=t.loc[ix]; i,j,k=map(int,(tr.signal_bar,tr.entry_bar,tr.exit_bar)); z=sig.loc[i]; sd=int(tr.side)
        E=round(tr.entry*100); S=round(z.stop*100)*sd; T=round(z.target*100)*sd; L=round(z.limit*100)*sd
        O,H,LO=(bars.o,bars.h,bars.l) if sd==1 else (-bars.o,-bars.l,-bars.h)
        assert j>i and LO[j]<=L and E*sd==min(O[j],L)
        # Independently inspect every prior order bar: no eligible earlier fill or kill.
        assert all(LO[m]>L and H[m]<T for m in range(i+1,j))
        # Engine disallows target on fill bar, takes stop first in ambiguous later bar.
        assert LO[j]>S or k==j
        for m in range(j+1,k):
            assert LO[m]>S and H[m]<T
        expected = (min(E*sd,S) if k==j else (O[k] if O[k]<=S else S)) if tr.reason=='stop' else (O[k] if O[k]>=T else T)
        assert round(tr.exit*100)*sd==expected
        def bar(m):
            return dict(ts=str(bars.ts[m]),ct=str(df.ct.iloc[m]),raw_symbol=str(df.raw_symbol.iloc[m]),open=float(df.open.iloc[m]),high=float(df.high.iloc[m]),low=float(df.low.iloc[m]),close=float(df.close.iloc[m]))
        checks.append(dict(signal=bar(i),entry_bar=bar(j),exit_bar=bar(k),side=sd,limit=float(z.limit),stop=float(z.stop),target=float(z.target),entry=float(tr.entry),exit=float(tr.exit),reason=tr.reason,net=float(tr.net),both_stop_target=bool(LO[k]<=S and H[k]>=T),passed=True))
    (OUT/'round3_spotchecks.json').write_text(json.dumps(checks,indent=2))
    # Size sensitivity uses actual intratrade paths (scaled fees and P&L), same untouched signals.
    sizing=[]
    for q in range(1,6):
        u=t.copy()
        for c in ('net','gross','fee','mae','mfe'): u[c]=u[c]*q
        u['qty']=q
        u['path']=u.path.map(lambda a: (a[0]*q,a[1]*q))
        seq=topstep.sequential(u,days)
        roll=topstep.rolling(u,days)
        summary=topstep.summary(roll,seq,days)
        sizing.append(dict(qty=q,**summary,**{'max_closed_drawdown':metrics.summary(u,days)['max_drawdown']}))
        seq.to_csv(OUT/f'round3_combine_q{q}.csv',index=False)
        print('Sizing', q, summary, flush=True)
    result=dict(params=P,seed=SEED,period='dev, in-sample; selected after best-of-1728 screen',signals=len(sig),stats=st,bootstrap=boots,concentration=concentration,sizing=sizing)
    prev=t.net.cumsum()-t.net
    result['max_eod_peak_to_intratrade_trough']=float((prev.cummax().clip(lower=0)-(prev+t.mae)).max())
    result['source_sha256']={f:hashlib.sha256((OUT.parents[2]/f).read_bytes()).hexdigest() for f in ['strategies/cbr.py','cltester/engine.py','cltester/topstep.py','docs/strategies/cbr/README.md','studies/cbr/grid_dev_screened.csv']}
    (OUT/'round3_summary.json').write_text(json.dumps(result,indent=2))
    print('Saved initial summary',json.dumps(result),flush=True)
    # Keep only window through flatten, preserving raw minutes/contracts; signals retain original expiry.
    compact=df[(df.ct_minute>=570)&(df.ct_minute<=960)].reset_index(drop=True)
    compact.to_pickle(OUT/'round3_rth_bars.pkl')
    # Convert original signal indices to their CT minute/day and price offsets; all signals, including unfilled.
    templates=sig.copy()
    templates['day']=df.trading_day.iloc[sig.index].to_numpy()
    templates['minute']=df.ct_minute.iloc[sig.index].to_numpy()
    close=df.close.iloc[sig.index].to_numpy()
    for c in ('limit','stop','target','kill'): templates[c]=np.rint((templates[c].to_numpy()-close)*100).astype(int)
    templates.to_pickle(OUT/'round3_templates.pkl')

if __name__=='__main__': main()
