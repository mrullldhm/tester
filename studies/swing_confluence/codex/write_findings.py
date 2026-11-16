from pathlib import Path
import json
import pandas as pd

P=Path('studies/swing_confluence'); O=P/'codex'; t=pd.read_csv(O/'cells.csv'); budget=json.loads((O/'final_budget.json').read_text()); desc=json.loads((O/'descriptive.json').read_text()); stress=pd.read_csv(O/'stress.csv')
# Stable names are references, not newly selected hypotheses.
ids=[13235,10336,13205,13402,13339,13357,14329,15400]
labels={13235:'A',10336:'B',13205:'C',13402:'D',13339:'E',13357:'F',14329:'G',15400:'H'}
s='''# Independent findings — CL dev, exploratory in-sample

## Reverse-engineering the owner

My reading is that the three strategies share a **structural expectation → attempted violation → response → transfer of control** model. A swing low is a claim that sellers have finished a transition and buyers should produce the next high. Price returning to the low before that high challenges the claim. The reaction to that challenge matters more than the existence of the point. Timeframes supply roles: a larger structure defines the claim, a smaller structure reveals whether the counterparty can defend it, and a limit order prices the attempted entry.

- **Swing Point Failure:** a low fails to produce its expected successor; the return to it signals seller control. The first smaller-timeframe higher-low pullback is the opposing attempt; breaking it provides the entry.
- **Swing Point Failure Reversal:** the attempted failure trade also fails. Taking back its pullback high invalidates seller control and suggests that the original low's broader upward attempt is still alive. It is a failure of a failure, not simply the opposite of a low-win-rate trade.
- **Swing Point Manipulation:** the apparent violation is quickly undone in a specific order. Taking a low first and the high second inside the hour distinguishes a sweep-and-return narrative from continuation. Larger swing structure supplies an unfinished destination.

The common generative concepts are **expectation failure, trapped positioning, ordered level interaction, structural invalidation, nested auctions, and a second attempt**. “Liquidity sweep” alone is insufficient: a breached level is observable; actual stops, trapped traders and intent are not. I can formulate these hypotheses from highs/lows, but cannot infer actual liquidity or manipulation from OHLC extremes. I could have invented members of this family if explicitly asked to model *what should have happened next, and what it means when it does not*. I would not honestly claim to have independently recovered your exact candle order, timeframe choices, stop windows or parameters from an unprompted instruction to find confluence. The missing framing was **a sequence of falsifiable expectations with opposing traders' invalidation levels**, rather than a static checklist of swing features.

The same model generates neighbours that are not specified in the three supplied strategy documents (this is not a claim about everything you have ever tried):

| Neighbour | Measurable prospective definition |
|---|---|
| Failed reclaim / second failure | Freeze the pre-sweep same-side swing level; breach it, reach it from the other side, then break the post-breach smaller-TF counter-swing before the larger opposite point confirms. Trade continuation only after that ordered sequence. |
| Second sweep after a successful first defence | Freeze a larger-TF level at first touch; count distinct touch episodes separated by a confirmed owner-rule opposite swing. Compare the second breach with the first; never retrospectively replace the frozen level. |
| Slow approach versus abrupt breach | Elapsed minutes from the current opposite base pivot's candle start to the event pivot start, divided by base leg ticks; interact with larger-TF newest point and location. No volatility indicator is needed. |
| Nested failure inside a surviving larger leg | While 4h newest remains the same low, observe a 15m low fail, then its post-failure high get taken back. The 4h low must remain unbroken throughout; entry follows the reclaim and uses the newly confirmed 5m low for invalidation. |
| Repeated equal extremes as an unfinished auction | Exact-tick equality to a level fixed before the first test; count nonadjacent touch episodes. A separate planned version could allow one tick, but it was not tested here. |
| Last higher-TF level touched | At each raw bar update the last observed touch time of each frozen PIT 1h/4h/daily level; label the most recent one before the trigger. Same-minute opposing touches remain unknown. This richer identity feature was not implemented in this round. |

The implemented tests below approximate some of these ideas; they do **not** fully implement the nested-failure or last-level state machines. In particular, repeated touches during formation are not a lifetime count of retests, and the prior-failure feature is not a complete failure-of-failure strategy.

Questions I would ask you: Which exact expectation makes a low valid: breaking the last high, confirming any next high, or simply holding the low? Is failure a touch or a strict break? How long can a sweep remain un-reclaimed before you call it acceptance? Must a defence be visible on the base timeframe, or is lower-TF structure enough? Are equal extremes one unfinished level or fresh swing identities? Does each level get one attempt or several, and what resets the count? Which larger timeframe has authority when 1h and 4h disagree? Should a contract roll invalidate old levels? Is your intended payoff tied to the structure that failed, or to a fixed maximum risk? The supplied SPF results show why win rate alone is not a reason to reverse a strategy: tiny stops, far targets and fees can generate that win rate without predictive content.

## Scope, trial budget and statistical method

**No validated or proven tradeable strategy emerged.** There are eight main-scan cells that meet the requested statistical gates with both the supplied fair baseline and a strict-tick sensitivity baseline. They are hypotheses for repair and execution testing. Several weaken by side, at a larger leg floor, or when dual-point updates are removed. All observations are **CL dev, 2010-06 through 2021-12, in-sample, selected from 15,643 tested cells**. The 2010 calendar year is partial. No validation/holdout bars were loaded, no data were downloaded, and no strategy or ledger runs were made.

The supplied table has 1,936,238 events. After removing ambiguous/unresolved outcomes, resolution rolls, legs below six ticks, candidate-origin-to-confirmation rolls, backward/restored points and confirmation closes outside the original barrier interval, eligible counts are 856,622 (1m), 265,671 (5m), 96,315 (15m), 23,747 (1h), 5,648 (4h), 807 (1d). Close is used only to establish the fair-baseline domain and probabilities, never as a predictive feature. This cleaned population differs from the original single-feature scan, so its unconditional edge should not be presumed zero.

The exact **trial budget is 15,643**: 6,379 supplied-fair cells, the same 6,379 strict-tick-fair cells, 2,850 attempted limit cells, plus 35 eligible follow-up stress cells. Main enumeration observed 6,938 category groups; 637 sparse configurations, including sparse limit subsets, were counted but received no inferential test. Five additional stress subsets had n<300 and were not tested. All numerical categories and primary families were recorded before the first scan in `codex/hypotheses.md` and `analysis_notes.md`. Later audit exclusions and the single stress round are documented in that notes file; no parameters were optimized afterward.

Each valid cell uses edge=mean(outcome−fair), z=sum(outcome−fair)/sqrt(sum(fair*(1−fair))), and two-sided normal p. Final BH at 5% is joint over **every test**, including the disqualified limit tests assigned p=1. This conservative handling prevents invalid limit evidence from helping other hypotheses pass. Final main qualification also requires |edge|>=.03, same sign in >=9 of the twelve years, and that sign in both 2010–2015 and 2016–2021. There are 27 qualifying main model/cell rows: 19 supplied-fair and eight tick-fair, with eight shared definitions. 2,417 total main/stress rows pass BH alone; small statistically detectable effects are not thereby useful.

The initial limit implementation included entry-bar stop losses but censored entry-bar target ambiguity. Its negative-edge p-values were therefore invalid; I retained the tried cells and original diagnostic columns, then set their inferential p-values to 1. No profitable/negative limit discovery is claimed from that scan. Final decisions use `qualified_final`, `bh_final`, `q_final` in `cells.csv`, not the initial `pass`/`bh` columns. A separate descriptive touch analysis gives ambiguity bounds below without additional hypothesis tests.

Events overlap and multiple cells reuse the same paths. The requested binomial z and ordinary BH procedure do not establish independent-observation validity or general dependence-robust false-discovery control. Daily cluster z values are descriptive checks of precision, not a replacement multiple-testing analysis. No independent miner comparison was performed: I did not read Claude's findings, and cannot claim independent agreement.

## Exact feature definitions

For a low event, “with” means upward; high events mirror all price directions. All levels are from owner `swing_state`. Features stop at the confirmation bar.

- `T_leg=1`: T's newest point is the event's same kind (low for low event); −1 is opposite. `T_pos` is event price's position in T's current SL–SH interval, mirrored for highs. Position category 0 is <=0; 1 is (0,.25]; 2 is (.25,.75); 3 is [.75,1); 4 is >=1. Thus “beyond opposite extreme” means category 4, not “near own extreme.” Missing ranges are excluded.
- `speed`: elapsed **wall-clock** minutes between the current opposite base pivot's candle start and the candidate's candle start, divided by leg ticks; negative chronology is missing. Categories 0<=1, 1=(1,5], 2>5 minutes/tick. This is structural duration, including overnight/weekend time, not the speed of a regression or an indicator. A contains a low only if its high-to-low transition is that slow.
- `touches`: number of disjoint raw 1m episodes exactly touching the event extreme between its candidate-candle start and confirmation inclusive; 2 means two or more. Adjacent minutes at the same extreme are one episode. This does not count tests after confirmation.
- `reclaim`: freeze the last same-side base swing level known before the candidate candle. 0=no strict sweep by confirmation; 1=sweep followed in a **later** raw 1m bar by a high touching that old low (low event), or a low touching that old high (high event); 2=sweep without that return. No closing-price reclaim is used; this is a high/low return, not demonstrated acceptance.
- `sweep_depth`: direction-aligned distance from that frozen old level to the candidate extreme, divided by event leg; tested strictly positive depth buckets (0,.1], (.1,.5], >.5. `nested`: sign of direction-aligned (number of new 1m highs minus new 1m lows) from candidate start through confirmation, using PIT state changes. Zero means equal counts, not necessarily no structure or balanced order flow. Restored 1m state changes can enter those counts, which limits interpretation of G.
- `prior_failed=1`: the immediately preceding same-side event on this base had outcome fail and its first-passage resolution bar was at or before current confirmation. Its later outcome is never used before that resolution. Zero includes prior events not yet resolved and prior holds; this is an approximation of repeated failed attempts, not a clean frozen-level test count. The preceding source-table event can itself be a restored or roll-contaminated event; H needs a rebuilt event history before interpretation.
- `replacement` is the stored flag only on a single-point update; dual-point updates are missing. Trend uses the supplied 1/−1/2/3 codes, but its equal-level reflection bug means trend cells cannot be promoted without repair.

Pairwise families test all higher-TF pairs for trend/trend, leg/leg, first leg/second position, first sweep/second trend; triple families test first leg/second leg/third position. Each sequence feature is tested alone and with each higher TF's leg or position. All observed category values are enumerated subject to n>=300. This is distinct from merely repeating single-feature confluence scans. No hours or Fibonacci retrace thresholds were optimized.

## Eight shared-baseline candidates

Definitions below are exact conjunctions within the common cleaned population:

| ID | Definition |
|---|---|
| A | 1h event; structural speed>5 minutes/tick; 4h leg with event. |
| B | 15m event; 1h leg with event; 4h leg against event; event in own-side weekly quarter: 0<weekly position<=.25. |
| C | 1h event; daily and weekly legs with event; .25<monthly position<.75. |
| D | 1h event; speed>5; weekly position>=1. |
| E | 1h event; speed>5; daily position>=1. |
| F | 1h event; speed>5; weekly leg with event. |
| G | 1h event; equal counts of new 1m highs/lows during formation; .75<=monthly position<1. Negative hold edge. |
| H | 4h event; prior same-side event already failed; 0<daily position<=.25. |

All edges below are percentage points. “Halves” are 2010–2015 / 2016–2021; both supplied and tick versions are shown. Years refer to the tick model. q is final joint BH-adjusted p across 15,643 tests.

| ID | n | Edge supplied / tick | Supplied halves | Tick halves | Years same sign | Tick z / daily-cluster z | q |
|---|---:|---:|---:|---:|---:|---:|---:|
'''
for k in ids:
    r=t.loc[k]; o=t[(t.model=='original')&(t.base==r.base)&(t.features==r.features)&(t['values']==r['values'])].iloc[0]
    s+=f"| {labels[k]} | {int(r.n):,} | {100*o.edge:+.2f} / {100*r.edge:+.2f} | {100*o.half1:+.2f} / {100*o.half2:+.2f} | {100*r.half1:+.2f} / {100*r.half2:+.2f} | {int(r.years_same)}/12 | {r.z:.2f} / {r.cluster_z:.2f} | {r.q_final:.4f} |\n"
s+='''
| ID | Leg ticks Q25 / median / Q75 | Legs <=10 ticks | Resolution median elapsed minutes | Resolved in same CME day | Intraday limit-entry assessment |
|---|---:|---:|---:|---:|---|
'''
assess={'A':'Timing fits; quarter-leg entry loses after fees in the diagnostic.', 'B':'Timing often fits; quarter-leg gross return is below fees.', 'C':'Slower and 18% cross day; quarter-leg return is negative.', 'D':'Timing fits; execution edge below fees; sensitive to dual updates.', 'E':'Timing fits; only tiny positive fee-adjusted diagnostic; weak early half.', 'F':'Timing fits; quarter-leg entry loses.', 'G':'Potential avoidance filter; reversal trading was not tested.', 'H':'Usually too slow: median >11 hours, ~46% cross day.'}
for k in ids:
    r=t.loc[k]; s+=f"| {labels[k]} | {r.leg_q25:g} / {r.leg_median:g} / {r.leg_q75:g} | {100*r.leg_le10:.1f}% | {r.elapsed_median:g} | {100*r.same_day:.1f}% | {assess[labels[k]]} |\n"
s+='''
All these cells have zero legs of 1–5 ticks by construction. “Same day” is not proof of an executable intraday bracket: session-end flatten at 15:10 CT, order expiry, missed fills, overlap and risk limits are not modeled here. Exact yearly edges and half sample counts are available in `cells.csv` / `descriptive.json`. H is a structural clue, not a practical short-horizon candidate.

A is the most useful next hypothesis because it combines a sequence property with higher-timeframe alignment and survives larger-leg, single-update and boundary-bar restrictions. B is a genuinely multi-timeframe interaction but barely clears the .03 edge gate; C has more stable single-update sensitivity but frequently crosses the day. D/E/F overlap A heavily and should not be counted as independent discoveries.

The complete follow-up stress round is `stress.csv` (35 tested restrictions, five too sparse). Specific limitations:

- A: leg>=11 retains n=1,729, tick edge +3.57 points, 9/12 years, q=.0065. Single-point updates: n=1,763, +3.87, 9/12, q=.0023. **High events** n=892 retain +4.89 points, +5.51/+4.53 halves, 12/12 years, q=.0073; low events are +2.59, only 7/12, early half essentially zero. The apparently symmetric pooled effect is stronger for shorts.
- B: leg>=11 gives +2.98 points and single-point updates +2.81, below the economic gate despite BH significance. Low events +4.58 pass; high events +2.10 do not. It is a marginal, side-sensitive candidate.
- C: single-point updates give +3.56 points, 10/12, q=.0036. Splitting sides retains roughly +3.11 on each, but neither side passes BH or yearly consistency (8/12 low, 6/12 high).
- D: removing dual updates loses BH (q=.0644); low-only misses yearly consistency and BH. E's early-half edge is only +0.84 points, versus +7.21 later: sign stability hides a substantial magnitude imbalance.
- F: single-point updates lose the 9-year gate (8/12); low events turn slightly negative in the early half. G loses BH after removing 15:59 CT bars (q=.0611), and its nested count inherits state-restoration ambiguity. H narrowly loses BH on single-point updates (q=.0508).

## Touch-limit and excursion variants

For a low, the prospective limit is `L+ceil(.25*leg)` ticks, stop `L−1`, target `H+1`; high events mirror. The order begins after confirmation and expires at the original first barrier passage. A touch fills; entry-bar stop losses are counted. Entry and target on the same raw minute have unknown order, so the table reports lower/upper descriptive bounds including them as failures/successes. Favorable gap entry improvements are not credited: actual open-price fills would require the engine. The bounds concern within-minute order at fixed limit prices, **not all execution uncertainty**. There is no intraday flatten or fee-aware strategy optimization.

| ID | Touch fills / events | Entry-target ambiguous | Edge at limit lower / upper (points) | Gross ticks/fill lower / upper | Held-event retest median (leg units) | Failed-event run median (leg units) |
|---|---:|---:|---:|---:|---:|---:|
'''
for k in ids:
    x=desc[str(k)]; s+=f"| {labels[k]} | {x['fills']:,} / {x['n']:,} ({100*x['fill_fraction']:.1f}%) | {x['target_on_entry_bar']} | {100*x['edge_lower']:+.2f} / {100*x['edge_upper']:+.2f} | {x['gross_ticks_lower']:+.3f} / {x['gross_ticks_upper']:+.3f} | {x['hold_retest_quantiles']['0.5']:.3f} | {x['fail_run_quantiles']['0.5']:.3f} |\n"
s+='''
One CL round-trip fee is **0.404 ticks** ($4.04 at $10/tick). A/B/D's gross touch-limit estimates do not cover that fee. E exceeds it by only about **0.12–0.17 ticks/fill** in this diagnostic, before session exits, overlap and gap effects; it is a small selected in-sample arithmetic result, not an execution-tested edge. C/F/G/H are negative even gross. Unweighted probability edge need not create positive tick P&L because variable leg size weights wins/losses differently, and selecting only limit fills changes the population.

For example A's held-event retest quartiles are approximately .133/.302/.529 leg units and failed-event run quartiles .315/.500/.738. These are observed after confirmation and **outcomes, never signal features**. They exclude the resolution bar and next-bar holds with no pre-resolution observations. They suggest an entry-design question, but do not establish that a .25-leg limit can capture the confirmation-time edge. The descriptive touch experiment actually shows how much of that apparent edge disappears at entry.

## Negative results and disqualified apparent discoveries

- **No 1m or 5m cell** survives the full gates under strict-tick fair. Seven 1m supplied-fair cells survive the original gates despite excluding 1–5-tick legs, but most still have small legs. Example: speed (1,5] minutes/tick plus 4h position<=0 gives n=2,796, supplied edge +4.33 points, legs 6/8/11 ticks (74.2% <=10), 10/12 years, +3.48/+4.81 halves, median seven minutes and 97.8% same day. It does not clear the full tick-baseline gates. Tick discretization extends beyond just 1–5-tick legs.
- Exact repeated-touch counts, simple sweep/return categories and unambiguous replacement conditions did not yield a shared-baseline full-gate candidate by themselves or in their tested pairings. The one sweep-depth/daily-position supplied-fair clue on 1h does not survive the full tick gates. This does not rule out frozen-level lifetime tests or an ordered reclaim state machine that was not implemented.
- The 1d sample is too small for rich interactions: only 18 cells per baseline meet n>=300; none qualify. The main interaction search produced just two shared-baseline candidates (B and C), versus six sequence/context cells; confluence is not generally predictive across the grid.
- A 1h daily-contract/monthly-with trend pairing qualifies under supplied fair, but misses the full tick/BH combination and inherits the equal-level trend bug. I do not interpret it as evidence of a trend effect.
- All 2,850 original limit-cell significance results are disqualified for the ambiguity-censoring reason above. They remain in the trial budget; apparently significant adverse-selection results from that implementation are not findings.
- The reports cannot establish the owner's causal story about trapped traders. No execution backtest, net profit factor, Combine pass rate, independent validation, or cross-miner replication was performed. The construction audit identifies defects that should be repaired before any candidate is promoted.

For completeness, these are the **11 supplied-fair-only qualifying definitions**, disqualified from the shortlist because the matched strict-tick cell fails at least one gate. Numeric definitions use the dictionary above; full rows and all negative tests are retained in `cells.csv`. No selective hiding of the unsuccessful matched tests is intended.

| Base | Features = values | n | Edge points | Halves points | Years | Leg Q25/median/Q75 | Elapsed median min / same day |
|---|---|---:|---:|---:|---:|---:|---:|
'''
shared=set((t.loc[k,'base'],t.loc[k,'features'],t.loc[k,'values']) for k in ids)
for _,r in t[t.qualified_final&(t.model=='original')].iterrows():
    if (r.base,r.features,r['values']) in shared:continue
    s+=f"| {r.base} | {r.features} = {r['values']} | {int(r.n):,} | {100*r.edge:+.2f} | {100*r.half1:+.2f} / {100*r.half2:+.2f} | {int(r.years_same)}/12 | {r.leg_q25:g}/{r.leg_median:g}/{r.leg_q75:g} | {r.elapsed_median:g} / {100*r.same_day:.1f}% |\n"
s+='''
## Ranked next steps and owner questions

1. **Top finding:** slow 1h transition with a matching 4h leg (A), especially high events. Repair the table, freeze the definition, and test a touch-limit bracket with actual intraday expiry and flatten rules on dev. Its present quarter-leg diagnostic is below fees, so a profitable entry rule is unproven.
2. **Next structural clues:** B (15m within opposing 1h/4h legs near the weekly own-side quarter), then C (daily/weekly leg alignment in the monthly middle). B's effect shrinks below three points on larger/single-update subsets; C's entry diagnostic loses gross. Neither should proceed to validation as a profitable strategy.
3. **Next hypotheses to measure:** frozen-level second-test versus first-test; a strict smaller-TF failure followed by an ordered reclaim inside an unbroken larger leg; which higher-TF level was touched most recently. Declare sequence clocks, expiry, equality policy, trial budget and limit-price geometry before running them. These are not additional tests performed here.
4. **Questions for the owner:** What exactly is the expected next structural event? When does a breach become accepted rather than manipulated? Which timeframe overrules the others? What resets a level's attempt count? Is touch enough at each stage? Should old-contract levels remain actionable? Must the entry be a retest of the reclaimed level, or any bounded-risk limit? Those answers define a much more faithful test than searching more static confluence cells.

Artifacts: `codex_audit.md`; complete tried cells `codex/cells.csv`; all stress results `codex/stress.csv`; exact yearly edges and touch arithmetic `codex/descriptive.json`; source audit examples `codex/audit_evidence.json`; declarations `codex/hypotheses.md`, `codex/analysis_notes.md`; scripts under `codex/`. Reproduction order is in the audit. Every script uses only the permitted dev parquet and explicit 2010–2021 CL files.
'''
(P/'codex_findings.md').write_text(s)
