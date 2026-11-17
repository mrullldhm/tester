from pathlib import Path
import pandas as pd
import json
from math import ceil
p=Path('studies/purple_levels_improve/codex')
c=pd.read_csv(p/'dev_cells.csv'); meta=json.loads((p/'dev_metadata.json').read_text())
lines=[]
def add(s=''): lines.append(s)
def table(headers,rows):
    add('| '+' | '.join(headers)+' |'); add('| '+' | '.join(['---']*len(headers))+' |')
    for row in rows: add('| '+' | '.join(map(str,row))+' |')
    add()
def cash(x): return ('−' if x < 0 else '') + f'${abs(x):,.0f}'
add('# Independent audit of purple_levels')
add()
add('**Verdict: stop optimising this family. Freeze one version and paper-test it forward.** There is a plausible liquidity/reversal mechanism and a positive dev result under traded-through entries, but neither tested revision establishes an improvement. The spent validation described in the brief lowers confidence; more dev selection cannot restore independent evidence.')
add()
add('**Scope and multiplicity.** Every performance number below is **dev / in-sample**, 2010-06-07–2021-12-31. Only `load_period("dev")` was called: 3,983,238 bars and 2,976 trading days. No validation/holdout bars, other researcher’s files, git, downloads, CLI tests or ledger writes. Changes are confined to this report and `codex/`. Production source was instrumented in memory to recover setup metadata; all four baseline trade lists reproduced exactly on count, signal/entry/exit bars, side, prices and net. Instrumented order columns equal the original strategy’s signals. Twelve deterministic first/middle/last raw-bar checks passed for setup, contract continuity, entry and exit; this is a spot check, not a full execution audit.')
add()
add('The pre-run [plan](codex/plan.md) declares **8 portfolio cells**: 4 baseline reproductions and 4 fresh revision runs (2 changes × 2 level universes), all 5m. There are **132 nonempty decomposition cells + 4 paired daily comparisons = 144 expectancy tests including portfolios**. Empty bins are not tested. Additional accounting: 8 execution cohorts, 4 top-ten-day removal summaries and 8 power scenarios: **164 evaluated strategy/diagnostic/scenario cells in total**; multiple statistics within a cell are not separate variants. Full results, including years and both fill models, are in [dev_cells.csv](codex/dev_cells.csv). No hidden parameter search or combined revision. Historical selection was already at least 12 candidates plus earlier purple_pa trials and fill sensitivities; this audit is additional research, not a new clean discovery.')
add()
add('Tests use one-sided positive net expectancy, a daily-cluster ratio standard error, and a normal reference. For trade mean μ, SE = √[D/(D−1) Σday(Pday−μNday)²]/N, including zero-trade days. BH covers all 144 tests, retaining overlapping/duplicate cells. Because those tests overlap, the CSV also gives dependence-robust Benjamini–Yekutieli (BY) q-values. BH flags 69 cells; BY flags 36, many describing the same trades. Neither correction accounts for the earlier research history, serial dependence between days, or turns selected dev performance into an out-of-sample claim. Paired revision tests compare total daily P&L, not just a changed mix of trades.')
add()
add('**Baseline and revision results — dev / in-sample; $4.04 round-turn fee, one CL contract, no exit slippage.** “Strict” requires a one-tick trade-through at entry, still executing at the stated limit or better open.')
add()
rows=[]
for lab in ('all_touch','all_strict','nopd_touch','nopd_strict','all_first_only_strict','nopd_first_only_strict','all_midpoint_strict','nopd_midpoint_strict'):
    r=c[c.label==lab].iloc[0]; tr=pd.read_csv(p/f'dev_{lab}_trades.csv'); y=tr.groupby(pd.to_datetime(tr.trading_day).dt.year).net.sum()
    rows.append([lab,int(r.n),cash(r.net),f'${r["mean"]:.2f}',f'{r.pf:.3f}',f'{sum(y>0)}/12',f'{r.q:.4f}',f'{r.q_BY:.4f}'])
table(['Portfolio','Trades','Net','Net/trade','PF','Years +','BH q','BY q'],rows)
add('The original strict all/nopd portfolios remain positive after removing their ten best days: **$15,586 / $15,540 dev / in-sample**. Their worst dev year is 2019; positive aggregate expectancy does not ensure a viable Combine path. No new Combine pass-rate or cost-per-pass simulation was performed, so none of these revisions is shown to meet the owner’s actual objective.')
add()
add('**Mechanism and decomposition.** A watched high/low can concentrate resting liquidity and breakout stops. A failed break followed by a fast departure could reflect aggressive reversal flow and forced liquidation by trapped breakout traders. The limit buyer/seller then supplies liquidity to a pullback, with the structural extreme defining failure. This could repeat when those participants and order-placement habits persist. Bars do not identify participants or orders: this is an economic hypothesis, not an observed explanation. The supplied level-regime findings give no standalone first-touch edge; a gap partly records a reversal already underway. A bounce conditional on that gap is not an executable profit probability.')
add()
add('The following table attributes accepted original trades, **dev / in-sample**, to the first family in production order at duplicate prices. It is not a family ablation: competing levels, first-family tie-breaking and one-position blocking affect attribution. Clock bins use the signal bar in Chicago time; overnight includes 17:00–07:59. Gap and signed entry distance use the original planned stop distance R. Stop bins are planned entry-to-stop ticks; gap size is the three-candle gap width.')
add()
rows=[]
for dim in ('family','clock','gap_bin','test_number','side','distance_bin','stop_bin'):
    subset=c[c.label.str.startswith('all_strict/'+dim+'/')]
    for _,r in subset.iterrows():
        value=r.label.split('/')[-1]
        other=c[c.label==f'nopd_strict/{dim}/{value}']
        if len(other):
            o=other.iloc[0]; rhs=f'{int(o.n)} / {cash(o.net)} / ${o["mean"]:.1f}'
        else: rhs='—'
        rows.append([dim+': '+value,f'{int(r.n)} / {cash(r.net)} / ${r["mean"]:.1f}',rhs])
table(['Component/bin','all strict: N / net / mean','nopd strict: N / net / mean'],rows)
add('The empty distance >1R bin was declared but has no trades. Conclusions are descriptive: both sides contribute; first tests look stronger than retests; the higher average return at larger stop sizes and during daytime may reflect volatility and dollar exposure rather than predictive skill. All-strict gap/R bins have no monotonic improvement with larger gaps. Its individual family positive-mean tests all have BH q > .05. These observations do not justify choosing a family, time window, minimum stop or gap threshold after this look. No no-gap, random-level or alternative-stop counterfactual was run, so the gap, level identity and structural stop cannot be causally separated. The exact four-candle confirmation/expiry, 1R target, 5m aggregation and family priority remain unproven choices. First-only removes one exception without inventing a threshold.')
add()
add('**Fill realism — dev / in-sample.** Classifying the original touch run by its first fill bar:')
add()
rows=[]
for fam in ('all','nopd'):
    for typ in ('touch_only','through'):
        r=c[c.label==f'{fam}_touch/fill_type/{typ}'].iloc[0]
        rows.append([fam,typ,int(r.n),cash(r.net),f'${r["mean"]:.2f}',f'{r.pf:.3f}'])
table(['Universe','First fill bar','N','Net','Mean','PF'],rows)
add('Dev profit is **not confined to exact-touch fills**: traded-through fills have the higher mean in both universes. But that partition understates the economic cost of waiting for a fill. The complete strict rerun loses $12,432 (32.9%) of all net and $8,971 (26.7%) of nopd net. Matching by original signal explains it:')
add()
a=pd.read_csv(p/'dev_execution_accounting.csv')
table(['Universe / execution cohort','N','Touch net','Strict net','Difference'],[[r.family+' / '+r.cohort,int(r.n),cash(r.touch_net),cash(r.strict_net),cash(r.delta)] for _,r in a.iterrows()])
add('Most lost profit comes from signals absent from the strict portfolio. Matching alone cannot separate missing trade-throughs from signals blocked by another working order or position. Waiting also delays many fills; those delayed setups are much weaker than the immediately traded-through cohort. That is consistent with a fill-selection problem: profitable departures can run away, while continued selling into a bid / buying into an offer selects worse opportunities. It is not proof of live queue behaviour or universal adverse selection. One-minute OHLC cannot establish queue position, volume ahead or stop slippage. Strict fills are a sensitivity, not a guarantee of execution; unchanged touch-based targets remain optimistic.')
add()
add('All-strict planned stop median is **17 ticks** (quartiles 11/27), versus a fee of **0.404 tick**: 2.38% of median planned risk. Both <=8 and 9–16 tick stop bins lose after fees in all-strict, while >16 ticks supplies all its net. This is not explained by fees alone: larger dollar risk also changes payoff scale and trade composition. Net/trade before additional execution costs is only **2.41 ticks all-strict / 3.21 ticks nopd-strict**; that is the entire budget for any unmodelled round-trip cost before estimated expectancy reaches zero. Do not turn the observed 16-tick boundary into another filter.')
add()
add('**Two changes only; one parameter value each, no combined version.** The dev reason and rules were written before simulations in the plan. Neither was derived from validation behaviour.')
add()
table(['Change','Exact rule and a-priori reason','Dev / in-sample cost versus original strict'],[
['First tests only','After production signal construction and duplicate tie-breaking, discard test_number=2. Keep all other rules. Removes role-flip retests and their exception; fresh resting liquidity should be less depleted on first encounter. No threshold to tune. Robustness is plausible, not established.','all: −486 trades, −$4,557 net; nopd: −350 trades, −$6,446 net. PF/mean rise but total earning rate falls.'],
['Inside-gap entry','Move limit toward stop by floor(gap_ticks/2) ticks (half-gap, one value). Keep structural stop, reset target to 1R from new limit; retain 20-minute expiry. Require through1. Better price compensates for supplying pullback liquidity; normalises placement to the gap rather than an optimised tick offset. One-tick gaps leave limit unchanged.','all: −143 trades, −$6,952 net; nopd: −108 trades, −$4,804 net. Lower risk/closer target and missed fills consume the entry improvement.']])
add('The midpoint test is an entry inside the gap that does not book exact-touch entry fills. It still needs an actual traded-through passive fill in paper trading. It retains the original deduplicated signals; it does not revive discarded same-bar candidates. All four paired positive-improvement tests have **BH q ≥ .848 dev / in-sample**: there is no demonstrated gain in total daily profit. Neither revision is a recommended replacement. First-only is the more defensible simplification if the owner insists on freezing a new hypothesis; any such choice now inherits this dev look and must be judged on new data.')
add()
add('**Honest test plan and power.** The brief says all/nopd touch/strict validation is spent. Renaming or filtering them does not create an independent 2022–2024 test. The family-unused 2025–2026-11-12 holdout could be used once as a locked family-level audit after choosing exactly one specification, execution model, primary metric and stopping rule. It is not truly unseen: the protocol says the owner researched those years before the reset. A failure ends the candidate; no subgroup rescue or second holdout pass. Prefer to preserve it and use forward/paper data strictly after 2026-11-12, excluding any bars inspected before the specification is frozen. Log every signal, cancellation, unfilled order, queue-dependent fill, fees and actual execution; compare daily net profit with the frozen strict prediction. Do not inspect rolling results and stop at the first significant win.')
add()
add('The estimates below are **dev / in-sample inputs and planning projections, not forward observations**. Two-sided α=.05, 80% power against zero: N ≈ [(1.960+0.842) σeffective/μ]², with σeffective = daily-cluster SE × √Ndev. Keep the current dev annual trade rate and variance; half-effect scenarios require four times as many trades. This assumes independent days, a stable distribution and a fixed single primary candidate. Positive serial correlation, multiple future candidates, missing fills and a smaller true edge require more data. It tests average net expectancy, not Combine pass probability.')
add()
pow=pd.read_csv(p/'dev_power.csv')
rows=[]
for _,r in pow.iterrows(): rows.append([r.portfolio,f'{r.rate:.1f}',f'${r["mean"]:.2f}',f'{ceil(r.n80):,}',f'{r.n80/r.rate:.1f}',f'{ceil(r.n80_half):,}',f'{r.n80_half/r.rate:.1f}'])
table(['Dev inputs','Trades/year','Observed mean','N at mean','Years','N at half mean','Years'],rows)
add('A holdout of roughly the stated two-year span is therefore too short for 80% power at the dev strict-fill edge. A practical fixed one-year paper review can reject bad execution assumptions and assess operational feasibility, but cannot certify this small edge. Calendar review dates should be fixed in advance; any interim safety stops must also be specified. Keep maximum drawdown, daily concentration and Combine feasibility as separate operational criteria. A positive dev t-statistic is no substitute for that evidence.')
add()
add('There is a credible path to **measuring** the frozen idea, with strict execution accounting and realistic costs. There is no demonstrated path from these dev edits to a robust improved strategy. Freeze the original all-5m specification as one primary forward experiment if continuing, retain nopd and these revisions as documented research rather than competing live selections, and spend effort on execution records instead of further optimisation.')
add()
add('Reproducibility: [audit.py](codex/audit.py), [run log](codex/run.log), [setup verification](codex/verify_setups.py), [setup checks](codex/dev_setup_checks.csv), [entry/exit checks](codex/dev_spot_checks.csv), [power inputs](codex/dev_power.csv), [execution accounting](codex/dev_execution_accounting.csv). Run from the repository root with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. .venv/bin/python studies/purple_levels_improve/codex/audit.py`, then `verify_setups.py` and `finish.py`; `write_report.py` renders this report. All generated trade and signal files are dev / in-sample and remain under `codex/`.')
Path('studies/purple_levels_improve/codex_report.md').write_text('\n'.join(lines)+'\n')
print('Report written:',len('\n'.join(lines).split()),'words')
