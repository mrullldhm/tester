# Independent dev-only hypotheses, declared before mining

Scope: CL dev trading days 2010-06-01 through 2021-12-31; explicit year-file reads 2010..2021 only. No strategy/ledger runs. All results exploratory in-sample. No downloads.

Mental model: a structural level creates an expectation; a breach tests it; a subsequent reversal or failed reversal transfers control. Context might distinguish a stop run from continuation.

Families: (1) pairwise higher-timeframe trend/leg/position/sweep interaction, (2) triple timeframe leg/position alignment, (3) structural speed, repeated extreme touches, sweep-and-return and nested 1m structure at confirmation, combined with higher-timeframe leg/position, (4) prior same-side event failure already observed by confirmation, (5) descriptive pre-resolution excursion and a prospective touch-limit experiment.

Primary scan excludes legs below 6 ticks, ambiguous outcomes, resolution rolls and nonpositive ranges. 1m is diagnostic. Category boundaries fixed: position <=0, (0,.25], (.25,.75), [.75,1), >=1; leg speed <=1, (1,5], >5 minutes per tick; counts 0,1,2+; sweep depth divided by leg <=.1, .1..5, >.5; nested opposing/with point counts ratio. Retain all tested cells with n>=300, including nonsignificant cells; BH 5% over the complete combined budget. Report attempted sparse cells separately. Two-sided normal p from z=sum(outcome-fair)/sqrt(sum(fair*(1-fair))). Require absolute edge >=.03, same sign in >=9 of calendar 2010..2021, both temporal halves same sign. Overlapping events invalidate independent-binomial inference as a standalone trading claim; daily cluster checks for shortlisted effects.

Limit variant: buy/sell at 25% of original event leg from its extreme, stop one tick beyond the event extreme, target one tick beyond opposite level. Order starts after confirmation; original barrier hit before entry cancels. A touch fills; entry-bar stop/target ambiguity is excluded and counted. No open or close feature. Entry fair probability uses limit-to-barrier geometry. Include all tested limit cells in the combined BH budget. Descriptive run/retest distributions have no significance claims and are not additional tested hypotheses.

Audit: independently linear-check first passage; truncated-prefix state comparisons; raw candle arithmetic for >=5 events across bases/sides; synthetic signed-price sentinel and strict-tick fair geometry; inspect weekly/monthly final-boundary behavior and raw roll contamination. Source files remain unchanged.
