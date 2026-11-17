# Predeclared dev-only audit
Only load_period('dev'); no CLI, git, downloads or ledger writes. Python bytecode disabled.
Reproduce all/nopd 5m touch/through1 (four portfolio cells).
Two changes only, each one value, independently applied to original all and nopd with through1:
1. First test only: discard test_number != 1 before engine execution (two cells).
2. Gap midpoint: move limit toward stop by floor(gap_ticks/2), retain structural stop,
   recompute 1R target from new limit; original 20-minute expiry; through1 (two cells).
No combinations, parameter searches or winner selection. Total eight portfolios.
Economic reasons: remove role-flip exceptions; avoid paying the full departure and seek price
improvement at the cost of fewer fills. Neither depends on validation findings.
For each of four original portfolios: decompose by attributed level family (four bins; nopd three),
signal CT clock (17-08,08-10,10-12,12-15:10), gap/risk (<=.1, .1-.25, >.25),
original fill-bar exact touch vs through, test number (first/retest), side,
side-adjusted actual entry distance from level / original risk (<=.5,.5-1,>1),
original stop ticks (<=8,9-16,>16), and each calendar year.
Count every nonempty group cell plus portfolio cells. Positive net expectancy tests use daily-cluster
ratio standard errors with normal reference (scipy unavailable; amended before any data run); BH across ALL cells (including overlapping baselines).
These are exploratory in-sample tests, not causal attribution or proof after historical selection.
Report paired daily differences for four revisions as another four evaluated cells included in BH.
Power: two-sided 5%, 80%, normal approximation with daily-cluster effective per-trade variance;
show observed effect and half effect, no claim of iid trades or known population effect.
Raw-bar spot checks: deterministic first/middle/last trades of each original portfolio.
