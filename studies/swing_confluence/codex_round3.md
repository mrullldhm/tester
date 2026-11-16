# Codex round 3 — ordered swing sequences, independent analysis and audit

**Dev, in-sample only: no qualifying edge.** The ordered nested-recovery tests do not rescue the owner's theory at the study's gates. Reclaiming a lower high raises the raw probability of reaching the old high, but largely because the reclaim moves price nearer that high. After restarting the fair baseline at the reclaim, there is no qualifying positive excess. This is evidence against these precise operationalisations, not proof that every contextual swing hypothesis fails. Claude's outcome-labelling explanation is plausible; these tests cannot establish why someone remembers a chart pattern.

Purple has both better observed gross expectancy and less fee drag than the swing strategies. It is misleading to explain all of the difference as fees, or to infer its win probability from its net profit factor. The repository still has no passing purple candidate.

## Scope, artifacts and multiplicity

Read CLAUDE.md, docs/PROTOCOL.md, docs/SWINGS.md, the study README including Round 3, the rebuilt-data notes, and the strategy code/results. Loaded only CL dev using `load_period("dev")`: **3,983,238 one-minute bars**, 2010-06-07 00:00 UTC through 2021-12-31 21:59 UTC. Actual rebuilt table: **1,914,711 events**, including `pt_ts` and `opp_ts`. Some prose elsewhere gives an older event count. No downloads, CLI strategy tests, ledger writes, git operations, validation or holdout reads. Final artifacts are confined to `codex3/` and this report. A lint command briefly created one `.ruff_cache` file outside that scope; that generated file was removed immediately after discovery, and subsequent checks used `--no-cache`. No existing cache file was removed or changed by the cleanup.

Hypotheses were written in [codex3/PLAN.md](codex3/PLAN.md) before calculation. Initially 39 cells: 24 nested-sequence cells and 15 next-candle cells. An implementation audit corrected two points: reject an HL already breached before HH confirmation, and distinguish the higher-TF **right candle's** completion from its parent candle's completion. Initial results were retained, with no qualifying cell, rather than discarded from multiplicity. **Conservative Codex trial count: 117 = three implementations × 39**, including duplicates and inadequate/empty cells. A final precision repair rounded swing prices to integer ticks before exact comparisons; the second implementation is retained in `interim_cells.csv` and counted too. No hypothesis or parameter changed. The correction history is in PLAN.md; the superseded results are `initial_cells.csv`.

For the widest audit count, I also include all **148 cells enumerated by Claude's source** (141 have n ≥ 300; seven receive p=1). **Joint BH family: 265 = 117 + 148**, duplicates retained. All tables below use the joint two-sided fair-score BH at 5%; nothing meets the full gates under either the Codex-only or joint family. The Claude reproduction is an audit, not 148 new independent discoveries. This count does not erase the much larger Round 1/2 selection history; it is no fresh out-of-sample evidence.

Every corrected cell, both halves and both sides: [codex3/cells.csv](codex3/cells.csv). Every cell-year: [codex3/years.csv](codex3/years.csv). All implementations and Claude's reproduced eligible cells: [codex3/all_cells.csv](codex3/all_cells.csv). Event-level decisions: [codex3/sequences.parquet](codex3/sequences.parquet); reproducible code: [codex3/run.py](codex3/run.py), [codex3/audit.py](codex3/audit.py), [codex3/verify.py](codex3/verify.py). All values below are in-sample; these are study outcomes, not strategy returns.

## 1. An ordered operationalisation of nested recovery

Long rules below; shorts negate prices and swap highs/lows exactly. Pairs are fixed: 1m/5m, 5m/15m, 15m/1h, 1h/4h.

1. Seed from a new, nonreplacement higher high published by `swing_state`. At confirmation its two highs and two lows satisfy HH+HL. Require strict point-candle order **previous low → previous high → HL → new HH**, and no price below the HL from its own candle through seed confirmation. The first listed high is not separately required to be higher than a third earlier high; this tests the broken-HL example, not every preceding HH in the owner's longer trend sketch.
2. After seed confirmation, the first strict break of the HL must precede another strict break of the frozen HH. This is the observable lower-low print; do not wait for an eventually surviving LL pivot to label it.
3. At that break's close, freeze the higher-TF swing low then known through `swing_state`. Require it remained intact across seed-to-break and is below the frozen HH. It is not retrospectively replaced with the low that ultimately becomes an HTF HL. Test both all such contexts and the subset where the HTF has HH+HL at the break. Context availability is at the decision close, not before the break minute.
4. **Break decision:** measure whether price strictly breaks the frozen HH before the frozen HTF low, starting after the break close.
5. **Reclaim decision:** before either barrier breaks, wait for the first new confirmed LTF swing high whose candle starts after the break and whose price is below the original HH. This is the post-break lower high relative to that original high. Wait for a later strict break of that high. Reject a reclaim on the same minute as either original barrier crossing. Do not backdate this decision to the original HL break.
6. From the reclaim close, test the original HH versus (a) the frozen HTF low and (b) the lowest low observed from the break through the reclaim minute. Each has its own fair probability. If no reclaim arrives first, it supplies no reclaim signal; it remains in the break cohort when eligible.

Greedily suppress overlapping seeds per pair and direction until the original HH/HTF bracket resolves, before checking outcome eligibility. No extra thresholds, minimum leg, or horizons were searched. Opposite directions and different pairs can still overlap. The frozen HTF barrier can differ from the HTF level at seed time; this is explicitly the level actionable at the break close.

For every decision with close c inside [L,H], fair upside probability is **(c−L+1)/(H−L+2)** for strict tick barriers L−1 and H+1; mirror for shorts. Close is used only for the baseline. Exclude outside-bracket closes, unresolved outcomes, same-minute ties and contract-roll crossings. Decisions and sequences use highs/lows and owner `swing_state`, with no candle close/open predictor. C is a decision timestamp, not a fill assumption.

This fair model is a driftless nearest-neighbour tick walk. Gaps, overshoots, discrete observation and excluded ties mean it is a diagnostic benchmark, not a complete generative model of CL. Nominal p uses the Bernoulli fair variance; an additional CME-decision-day clustered residual-SE test addresses some within-day dependence. Clustered inference can be stronger or weaker than nominal, and does not remove multi-day or cross-cell dependence. Both versions give zero full-gate passes. Insufficient cells get p=1; annual diagnostics are not separately mined hypotheses.

### Results at break and reclaim

| Cell | n | Hold / fair % | Edge pp | 2010–15 / 2016–21 pp | Years same sign | BH 265 |
| --- | --- | --- | --- | --- | --- | --- |
| N_break 1m/5m all | 60,054 | 48.15 / 47.25 | +0.89 | +0.97 / +0.83 | 11/12 | yes |
| N_reclaim_htf 1m/5m all | 24,402 | 68.59 / 68.80 | -0.22 | -0.69 / +0.21 | 7/12 | no |
| N_reclaim_local 1m/5m all | 24,379 | 55.90 / 56.67 | -0.77 | -1.62 / -0.00 | 7/12 | yes |
| N_break 5m/15m all | 15,319 | 43.25 / 42.92 | +0.33 | +0.41 / +0.26 | 6/12 | no |
| N_reclaim_htf 5m/15m all | 5,317 | 70.08 / 70.45 | -0.38 | +0.25 / -0.96 | 7/12 | no |
| N_reclaim_local 5m/15m all | 5,325 | 57.78 / 59.02 | -1.23 | -0.54 / -1.87 | 10/12 | no |
| N_break 15m/1h all | 5,731 | 44.91 / 45.10 | -0.19 | +0.02 / -0.39 | 5/12 | no |
| N_reclaim_htf 15m/1h all | 1,980 | 72.17 / 72.95 | -0.78 | -0.43 / -1.10 | 8/12 | no |
| N_reclaim_local 15m/1h all | 1,988 | 57.65 / 59.32 | -1.68 | -1.00 / -2.31 | 9/12 | no |
| N_break 1h/4h all | 1,272 | 49.14 / 48.25 | +0.88 | +0.85 / +0.91 | 8/12 | no |
| N_reclaim_htf 1h/4h all | 397 | 74.06 / 73.35 | +0.71 | -1.89 / +2.99 | 6/12 | no |
| N_reclaim_local 1h/4h all | 408 | 61.03 / 59.68 | +1.35 | +1.77 / +0.98 | 8/12 | no |

The raw HTF-barrier reclaim hold rates are **68.6%, 70.1%, 72.2%, 74.1%**, but fair is **68.8%, 70.5%, 73.0%, 73.3%**. Calling a reclaim predictive from its raw hit rate alone would manufacture the hoped-for result. These are selected later decision points, not evidence that the original break was manipulation.

The aligned HTF-up subset does not help:

| Cell | n | Hold / fair % | Edge pp | 2010–15 / 2016–21 pp | Years same sign | BH 265 |
| --- | --- | --- | --- | --- | --- | --- |
| N_break 1m/5m up | 18,627 | 46.62 / 46.58 | +0.04 | -0.27 / +0.30 | 6/12 | no |
| N_reclaim_htf 1m/5m up | 7,922 | 66.50 / 67.72 | -1.22 | -2.02 / -0.50 | 9/12 | no |
| N_reclaim_local 1m/5m up | 7,916 | 53.58 / 55.04 | -1.46 | -2.70 / -0.35 | 8/12 | yes |
| N_break 5m/15m up | 4,922 | 42.87 / 42.88 | -0.01 | -1.38 / +1.29 | 6/12 | no |
| N_reclaim_htf 5m/15m up | 1,842 | 67.59 / 69.58 | -1.99 | -2.82 / -1.22 | 9/12 | no |
| N_reclaim_local 5m/15m up | 1,846 | 54.71 / 57.71 | -2.99 | -3.82 / -2.23 | 8/12 | yes |
| N_break 15m/1h up | 1,698 | 43.58 / 44.99 | -1.41 | -1.66 / -1.15 | 9/12 | no |
| N_reclaim_htf 15m/1h up | 601 | 70.72 / 71.55 | -0.83 | -0.78 / -0.88 | 9/12 | no |
| N_reclaim_local 15m/1h up | 604 | 54.80 / 57.17 | -2.37 | -0.17 / -4.49 | 9/12 | no |
| N_break 1h/4h up | 420 | 50.95 / 50.75 | +0.20 | -1.51 / +1.70 | 7/12 | no |
| N_reclaim_htf 1h/4h up | 142 | 72.54 / 75.28 | -2.74 | -7.76 / +0.82 | 5/12 | no |
| N_reclaim_local 1h/4h up | 147 | 59.18 / 61.93 | -2.74 | -4.46 / -1.53 | 7/12 | no |

The 1h/4h HTF-up reclaim cells have fewer than 300 observations and only 11 represented years. Among eligible corrected cells, the largest absolute edge anywhere is **2.993 pp**, a negative 5m/15m local-barrier reclaim cell, below the 3 pp gate. There is no qualifying avoid-filter discovery either. A statistically detectable 1m break effect of +0.89 pp is too small; it is not a strategy finding.

Annual edges for the main HTF-barrier reclaim test, all contexts (pp; full annual n and every other cell-year are in years.csv):

| Year | 1m/5m | 5m/15m | 15m/1h | 1h/4h |
| --- | --- | --- | --- | --- |
| 2010 | -2.17 | -2.15 | +1.49 | -16.85 |
| 2011 | -1.00 | -1.21 | -0.62 | -4.87 |
| 2012 | -1.82 | +2.32 | -1.79 | +1.11 |
| 2013 | -0.43 | +0.79 | -2.32 | +5.78 |
| 2014 | +0.74 | +2.14 | +0.57 | -0.45 |
| 2015 | +0.05 | -1.19 | +0.29 | -5.00 |
| 2016 | -0.51 | -1.28 | -1.79 | -1.82 |
| 2017 | +1.86 | -0.62 | -0.21 | +5.87 |
| 2018 | -0.71 | +0.00 | -1.24 | -4.24 |
| 2019 | -0.29 | +1.39 | -3.59 | +1.64 |
| 2020 | +0.23 | -2.87 | -2.20 | +5.24 |
| 2021 | +0.77 | -2.39 | +2.65 | +11.69 |

## 2. Breakout candle taken out by the next candle; the 4h issue

For base/context pairs 5m/1h, 15m/4h, 1h/4h, freeze the swing high known **before breakout candle B starts**. B must be the first strict break: no earlier raw high since that point's candle exceeds the level. Next candle C must strictly take B's low. At C's known completion, B must actually be the current swing high published by `swing_state`, with its exact candle timestamp. Thus full owner rules, including transitions/replacements/outside-candle order, apply; a two-neighbour pivot is insufficient. Short is the exact mirror. The study asks whether the bullish breakout direction subsequently resumes: strict B-high break before strict C-low break, from C decision close; shorts reverse that bracket. It does not retrospectively identify a later recovery as the setup, and is not the existing manipulation strategy's low-then-high-in-C entry rule.

At C decision, store the HTF parent containing B and whether **that parent's right-hand HTF candle has completed**. No unclosed HTF candle confirms a swing. Also classify whether the observed parent-through-decision window has taken the preceding HTF candle's opposite extreme. This window can include the current right-hand candle, so it is a path feature, not the eventual OHLC of one completed candle.

| Cell | n | Hold / fair % | Edge pp | 2010–15 / 2016–21 pp | Years same sign | BH 265 |
| --- | --- | --- | --- | --- | --- | --- |
| M 5m/1h all | 28,139 | 27.27 / 28.52 | -1.25 | -1.61 / -0.85 | 12/12 | yes |
| M 5m/1h forming_took | 7,938 | 27.80 / 28.28 | -0.48 | -0.05 / -0.95 | 8/12 | no |
| M 5m/1h forming_intact | 20,201 | 27.06 / 28.61 | -1.55 | -2.23 / -0.81 | 10/12 | yes |
| M 15m/4h all | 10,706 | 27.47 / 28.09 | -0.62 | -1.12 / -0.14 | 8/12 | no |
| M 15m/4h forming_took | 3,419 | 26.85 / 27.43 | -0.58 | -0.79 / -0.36 | 8/12 | no |
| M 15m/4h forming_intact | 7,287 | 27.76 / 28.41 | -0.64 | -1.28 / -0.03 | 8/12 | no |
| M 1h/4h all | 2,980 | 27.89 / 28.29 | -0.40 | +0.40 / -1.15 | 7/12 | no |
| M 1h/4h forming_took | 1,220 | 26.56 / 26.40 | +0.16 | -0.06 / +0.39 | 6/12 | no |
| M 1h/4h forming_intact | 1,760 | 28.81 / 29.60 | -0.79 | +0.75 / -2.12 | 6/12 | no |

**All immediate-next-base-candle decisions have HTF confirmation pending; each "complete" cell has n=0.** This follows from the timeframes: the next small candle cannot also finish the higher-TF right candle. Pending/complete is therefore not an independent predictive split here. The parent containing B itself can already be closed, which was the timing distinction missed by the initial implementation. The initial parent-open splits also produced no qualifying result and remain counted in the trial family.

In the supplied example, 1h B at 14:00 MYT is inside the 4h parent at 11:00 MYT; when the next 1h candle takes B's low, the 4h 15:00–19:00 right candle is unfinished. A valid 1h point does not imply a confirmed 4h point. **No reproduction of 13 November 2026 was attempted: dev ends in 2021.** The time interpretation above comes from the supplied description, not observed 2026 bars. A later 4h confirmation would be a later decision with a new baseline, never permission to label the earlier bar using that future knowledge.

## 3. Audit of Claude's round3.py

Read-only reproduction redirects its output to codex3; no original script/data was changed. [codex3/audit.json](codex3/audit.json) records exact agreement with every saved cell's n, edge, both halves and z (maximum difference **zero**).

| Check | Finding / impact |
| --- | --- |
| Look-ahead in prior-day levels | No current-day future extreme is used. `factorize(trading_day)` is chronological on sorted dev bars; dh/dl are indexed at day−1. CME trading-day alignment is correct, including the evening session. |
| Look-ahead in forming extrema | Cummin/cummax include only observations through the decision minute. Prior HTF candle extrema are available at that close. Full-data candle membership does not itself leak its eventual high/low into these features. |
| Direction mirroring | H1 aligned trend/sweep, H2 low/high selection, H3 PDL/PDH selection are correctly mirrored on this rebuilt table. No wrong-mirroring defect found. |
| H1 is not the claimed sequence | `base_trend==2` says HH+LL, not the full temporal history. It permits replacements and same-candle opposite points. Among filtered H1 events, replacement counts are 29,003 / 7,832 / 3,106 / 936 on 1m/5m/15m/1h. Opposite point is on the same candle in 9,818 / 2,340 / 814 / 204 cases; two 5m events even have it later. Same-candle points can be valid under the owner order rule, but need an explicit order check to support the claimed multi-candle sequence. Snapshot H1's null is not an exhaustive ordered-theory test. |
| H1 "intact" is not a path condition | Sweep compares the event extreme with a level known before the event candle, whereas trend/leg use confirmation-time state. It does not freeze one HTF low and verify its survival through a later reclaim. Not look-ahead, but a different hypothesis. |
| H2 "forming" includes completed candles | It never checks `cd.avail[cid] > event_bar`. Already complete: 138,128 / 1,122,316 eligible lower-base events for 15m (12.3%); 58,441 / 1,218,656 for 1h (4.8%); 19,943 / 1,242,445 for 4h (1.6%); 2,328 / 1,248,187 for 1d (0.19%). This is a definition bug if interpreting the cells as still-open candles. It also does not test the owner's higher-TF right-candle confirmation gate. |
| H3 price-sign missingness | `ok = lvl >= 0` wrongly treats a valid negative CL level as missing, contrary to the repaired table's rule. Use explicit previous-day availability instead. **Zero eligible dev events affected in this sample**, so it does not explain the reported edge. |
| H3 first take vs purple | It tests a strict crossing by an event candle, with no earlier strict crossing before that candle starts, plus same-day confirmation. It is a first-crossing-candle category, not necessarily the first swing signal after a first intrabar crossing. Purple uses a touch, an armed approach from a known side, a possible role flip, a gap, then a limit fill. H3 lacks those filters and execution selection. "No take" also includes arbitrary distances from the level. It is not a test of purple's full mechanism. |
| Trial count / reporting | Current source enumerates **148**, drops seven n<300, writes **141** cells; source and saved CSV reproduce exactly. README's **175** is stale/inconsistent with this version. BH in Claude's code uses only the 141 eligible cells. This report conservatively counts all 148. |
| Statistical inference | Overlapping event paths/shared HTF regimes violate an independent-Bernoulli reading of the z statistic. BH does not repair that sampling dependence. This limits significant small effects, not evidence of a hidden positive ≥3 pp finding. |

The initial commentary raised a possible repeated-replacement issue within a candle. On review, that is not an established H3 bug: rebuilt events identify new point candles. The supported H3 differences are its candle-level first-crossing definition and missing purple mechanics, as stated above.

Claude's reproduced H3 first-take results (dev, in-sample):

| Base | n | Edge pp | 2010–15 / 2016–21 pp | Years same sign | Joint BH |
| --- | --- | --- | --- | --- | --- |
| 1m | 1,638 | +0.43 | +1.72 / −0.70 | 7/12 | no |
| 5m | 1,516 | +2.69 | +3.02 / +2.40 | 8/12 | no |
| 15m | 1,526 | +2.40 | +3.02 / +1.89 | 9/12 | no |
| 1h | 1,397 | +1.98 | +0.90 / +2.94 | 10/12 | no |
| 4h | 1,109 | +0.87 | −0.91 / +1.95 | 8/12 | no |

The 1d first-take cell is below 300 and absent from the saved eligible CSV; it remains counted among all 148 enumerated cells with p=1. These are weak leads, not passing findings or purple expectancy estimates.

Claude's qualitative conclusion of no qualifying H1/H2/H3 cell reproduces. Its snapshot label and economic explanation need the distinctions above. No source repair was made because writes outside the allowed paths are prohibited.

## 4. Purple versus the owner strategies: prediction and economics

Read current ledger rows and saved trade CSVs, without rerunning any strategy. [codex3/economics.csv](codex3/economics.csv) contains exact hashes, parameters and calculations; the following are **dev, in-sample, selected from the declared budgets**, not fresh runs. Purple's two settings trade off net/PF/years; 15m is best net, 5m best PF, so "best of 2" is metric dependent. SPF row is its default rather than its best; other swing rows are labelled by setting within best-of-5/14 research.

| Setting | n | Gross $ | Fees $ | Net $ | Net PF | Gross $/trade | Net win % | Stop-exit median ticks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Purple 15m (2 tried) | 545 | 16,710 | 2,201.80 | 14,508.20 | 1.196 | +30.66 | 54.13 | 28 |
| Purple 5m (2 tried) | 591 | 15,120 | 2,387.64 | 12,732.36 | 1.239 | +25.58 | 54.48 | 17 |
| SPF default (15 tried) | 7,364 | -43,620 | 29,750.56 | -73,370.56 | 0.821 | -5.92 | 10.14 | 4 |
| SPF reversal risk15 (5 tried) | 6,468 | 2,700 | 26,130.72 | -23,430.72 | 0.940 | +0.42 | 19.90 | 6 |
| SPF reversal 15m stop (5 tried) | 6,410 | 8,880 | 25,896.40 | -17,016.40 | 0.968 | +1.39 | 18.63 | 8 |
| Manipulation swing TP (14 tried) | 715 | 5,190 | 2,888.60 | 2,301.40 | 1.044 | +7.26 | 23.64 | 9 |
| Manipulation TP60 (14 tried) | 1,437 | 11,190 | 5,805.48 | 5,384.52 | 1.042 | +7.79 | 17.81 | 11 |

A stop-exit median describes realised stop losses, not the exact scheduled stop distribution; entry price improvement and exit rules matter. The saved CSV does not record every original bracket price, so no scheduled-risk distribution is invented here. The median 15m-stop reversal exit is 8 ticks while its README's median entry-to-stop is 10; these measure different populations.

- **Prediction/selection is part of it.** Purple 15m earns +$16,710 gross (+3.07 ticks/trade); 5m +$15,120 (+2.56 ticks/trade). SPF default loses $43,620 before fees. SPF reversal's best larger-stop setting earns only $1.39 gross/trade versus a $4.04 fee. Removing fees would not make SPF default work, and would leave reversal very thin. Purple may select better reversals via level + approach + rapid gap departure, but those components have not been causally isolated by an ablation. H3's +2–3 pp lean does not prove which component generates filled-trade expectancy.
- **Bracket economics is part of it.** Purple targets 1R against the whole touch-to-gap extreme; its stop exits are median 28 ticks (15m) / 17 (5m). Fee drag is about 1.44% / 2.38% of those median dollar losses, versus 10.1% for SPF's four-tick median. A fair symmetric 28-tick bracket needs about 50.72% wins after fees; 17 ticks needs 51.19%. SPF's 4-tick stop/50-tick target needs about 8.16% under the oversimplified fixed-bracket net equation, not 50%; its varying stops/early exits mean that toy threshold cannot be applied to its ledger aggregate. Actual SPF gross is negative despite its ~10% aggregate wins. A tiny stop is not mathematically a losing edge by itself; fair probability falls as reward distance rises.
- **Trade count is part of it.** Purple pays $2.2–2.4k fees across ~550–590 trades over dev, versus ~$26–30k for ~6,400–7,400 swing failure/reversal trades. Reducing trade count alone does not create gross alpha; it helps only if removed trades have insufficient expectancy after costs.
- **PF is not win probability.** Current 15m purple win rate is **54.13%**, not an inference from PF 1.196. The identity PF/(1+PF) needs equal average net wins and losses. Here average net wins/losses are $300.60/$296.68, with variable risk and flatten/roll/gap exits; 5m is $205.21/$198.32 and 54.48% wins. Its gross expectancy and success rate are evidence of selected reversal behaviour in dev, not validation of a 4–5 pp swing-study excess.
- **Still below the gates.** Purple 15m: 10/12 positive years, 38.6% rolling Combine pass rate, PF 1.196. Purple 5m: 7/12 positive years, 55.0% pass rate, PF 1.239. Both miss PF 1.25; each also misses another gate. Current 15m net is **$14,508.20**, not older README rows of $14,938 or $14,430. The README documents 400 raw-bar checks and positive traded-through-fill subsets, but those subset diagnostics predate later fixes and should not be presented as exact current-hash estimates.

The owner-aligned part of purple is **a reference extreme → first encounter → observed response → later decision**. Yesterday's extremes are fixed before today and cannot be retroactively replaced, whereas live swing points can change under the owner rule. A three-candle gap is fast departure measured from highs/lows; it is not itself proof of manipulation or of institutional liquidity. Purple also permits a level's role flip, consistent with context-dependent acceptance/rejection. Its fixed prior-day reference and modest trading frequency may make its hypothesis easier to specify and falsify than a retrospectively labelled HTF HL.

## 5. Declared follow-up hypotheses — proposals only, not run results

Do not infer profitability from these definitions. Freeze a new strategy document before any test. **Proposed budget: 8 dev configurations total**: two unchanged purple controls (5m,15m; counted even though previously researched) plus three families × two fixed base/context pairs (5m/1h,15m/4h). No stop-size/RR/expiry grids; no new time-of-day, indicators, volume, news, or validation looks.

Shared variant mechanics: prior **CME trading day** highs/lows from raw bars; a level arms only after a completed base candle lies wholly above it (support/long) or wholly below it (resistance/short), using highs/lows only. A touch consumes the level's attempt for the day, even if no trade follows; at most one attempt per level per day, no role-flip retest in these variants. Bullish gap at q means high[q−2] < low[q], bearish mirror. Entry limit at low[q] long/high[q] short, works from the next minute for four base-candle clock durations. One tick beyond the adverse extreme over the specified touch/setup-through-q window; target **1 actual initial R**, no max-risk clipping. One contract/position at a time; touch fills and existing engine expiry/session/roll/15:10 CT flatten rules. Reject ambiguous same-minute orderings rather than infer a path. These deliberate variants differ from purple's open-based initial arming and second role-flip test; the unchanged controls remain the attribution reference.

1. **P1: fixed daily reference plus live HTF structure (2 trials).** On the first armed touch, freeze the HTF protective swing low for a long/high for a short from `swing_state` at the prior minute. Require aligned HH+HL/LH+LL then known. The level must remain unbroken through confirmation q. Use the first gap completed 1–4 base candles after the touch, with q−2 no earlier than the candle before touch. Stop covers touch through q. Hypothesis: HTF structure filters the first daily-level bounce without shrinking the economic bracket.
2. **P2: daily-level touch plus ordered LTF recovery (2 trials).** Same first touch; freeze HTF protection as P1 but do not require its trend. Within four base candles after the touch, price must strictly break a previously confirmed base HL (LH for shorts), then confirm a new opposite swing after that break, then strictly reclaim it before the HTF protection breaks. Previous HL/LH must already be known at touch. Require the first directional gap at or after reclaim, still within that original four-candle deadline. Stop covers touch through q. This is an actionable ordered recovery at a fixed reference, with its baseline/entry assessed after recovery rather than labelling the touch a manipulation using its future.
3. **P3: breakout-candle failure plus recovery, with daily location and whole-excursion stop (2 trials).** Long: B first breaks a pre-known base swing high; next C takes B's low and confirms B as the owner swing high. PDL must be the day's first armed support touch during B or C. Freeze HTF swing low before B starts; it must survive through q. After C completion, require B-high reclaim strictly before C-low break, then first bullish gap at or after reclaim, all within four base candles after C. Stop covers B through q. Short mirrors around PDH, failed downside breakout, HTF high. Parent/right-HTF status is recorded as known then, never required to become a final HTF HL/LH in hindsight. Hypothesis: daily location and whole-excursion 1R economics improve the owner's recovery mechanics; it is deliberately stricter than bare M.

All proposals use owner `swing_state`, no final swing labels. Cancel if protection breaks before an order/fill. For frozen-barrier checks and all gaps, require same contract; use clock deadlines when minutes are missing. Report all eight, comparisons to controls, annual concentration, fills/fees, actual risk distributions and trade spot checks. Gates remain PROTOCOL.md, including neighbouring-parameter robustness declared separately before any expansion; no candidate gets validation until qualified. Any attempted further combinations consume a new explicitly reported budget. The two pre-existing controls are comparisons, not new independent evidence.

## 6. Questions for the owner

1. Does "the breakout candle gets taken out" require a **strict break or a touch**, and must the next candle remain below its high for an owner-confirmed swing high? If C also breaks B's high, what exact 1m ordering is required?
2. Which observable event authorises the trade: the HL break, the first LH reclaim, B-high reclaim, or the right candle's close? Which fixed level is the invalidation at that moment?
3. For the 4h example, should the 1h setup be vetoed until 4h confirms, traded with smaller-TF evidence while 4h remains pending, or recorded as two distinct hypotheses? Confirmation later cannot make it valid earlier.
4. Does an unbroken HTF level stay frozen from setup start, or should a newly confirmed/replaced `swing_state` level replace it while waiting? This changes the sequence being tested.
5. Which losing case with the same information available at decision time would you still call manipulation? A side-by-side successful/failed pair with the decision time hidden from later bars would clarify whether the label is predictive or retrospective.

## Verification and practical limits

Scoped Ruff checks pass with caching disabled. The state parquet files cache this run's `swing_state` outputs; regenerate them if raw inputs or `cltester/swings.py` change. `manifest.json` fingerprints the dev inputs, ledger and relevant source.

`verify.py` independently scans raw future highs/lows for 60 deterministic sequence examples (first/last per family/base/side), confirms barrier order and fair geometry, checks ordered reclaim timestamps, and recomputes six early M examples on truncated input to verify the owner point was already available. See [codex3/verification.json](codex3/verification.json). These are study event checks, not a claim that a new strategy's fills have been validated. Existing trade economics are read from saved ledgers; prior README spot checks are attributed, not rerun. No new strategy was submitted to the engine.

Neither this study nor purple establishes a robust Combine solution. The useful conclusion is narrower: fixed references, explicitly ordered evidence, a baseline restarted at the actual decision, and actual trade economics are testable; eventual higher-TF swing membership is not an available entry feature.
