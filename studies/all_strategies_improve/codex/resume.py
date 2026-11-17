"""Resume from completed triage artifacts; no new selection or parameter cells.
The first invocation's strict replay instantiated manage without its signal-initialized state.
run.py is corrected; this resumes its saved triage rather than rerunning the expensive audit.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
source=Path('studies/all_strategies_improve/codex/run.py').read_text()
exec(compile(source.split("log('Loading dev only')")[0],'<audit definitions>','exec'))
log('Resuming completed triage; dev only')
df=load_period('dev');B=Bars.from_frame(df);DAYS=pd.Index(df.trading_day.unique());D=len(DAYS);YEARS=(df.trading_day.max()-df.trading_day.min()).days/365.25
daily=df.groupby('trading_day').agg(high=('high','max'),low=('low','min'));rng=daily.high-daily.low;prior=rng.shift(1);cut=prior.rolling(60,min_periods=20).median();regime=pd.Series(np.where(cut.isna(),'unknown',np.where(prior<=cut,'prior_quiet','prior_large')),index=daily.index)
selections=json.loads((O/'selections.json').read_text())
cells=pd.read_csv(O/'cells_partial.csv').to_dict('records')
replay=pd.read_csv(O/'replay_checks.csv').to_dict('records')
for sel in selections:
 if sel['selection']!='best':continue
 name=sel['strategy'];sig=pd.read_csv(O/f'{name}_best_dev_signals.csv',index_col=0);sig.index=sig.index.astype(int)
 t=pd.read_csv(O/f'{name}_best_dev_trades.csv');t['trading_day']=pd.to_datetime(t.trading_day)
 details[tuple(sel['key'])]=(t,sig)
exec(compile(source[source.index('# All other families:'):],'<audit continuation>','exec'))
