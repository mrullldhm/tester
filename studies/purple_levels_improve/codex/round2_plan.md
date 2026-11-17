# Round 2 declared before calculations
Dev only; no ledger, CLI tests, git, downloads or production changes. Outputs here and codex_round2.md only.
Re-use Round 1 instrumented signals, independently join stops, verify against supplied baseline CSVs.
Reproduce Claude's five entry-time sessions for four baselines, including omitted late session.
Use planned limit-to-stop ticks for corrected R (all exits); also audit Claude's exit-ticks denominator.
For all-strict: six Claude stop bins (0,8,12,18,25,40,infinity), RTH vs every non-RTH trade;
pooled-bin weighted difference, and RTH coefficient controlling bin and year, daily clustered.
All-strict each year: RTH/non-RTH and their contrast. All-touch yearly exact RTH and pre+RTH
audit Claude's yearly definition. Reproduce all-touch >12 ticks Asia/RTH comparison.
All-strict first/retest x RTH/non-RTH four cells and three first-minus-retest contrasts (incl interaction).
Each nonempty diagnostic/contrast counted once, even if overlapping. Positive-mean/difference
normal-reference daily-cluster p-values pooled with previous 144 tests for exploratory BH/BY.
Three executable RTH all-level strict-fill sizing scenarios: one CL; $250 risk; $500 risk.
RTH order eligibility: signal closes 08:30 <= CT < 13:30; cancel unfilled orders at 13:30;
positions keep original exit rules. No boundary tuning. Full prior-session setup history retained.
Qty=min(5,floor(budget/(planned stop ticks*10+4.04))); skip orders over budget at one contract.
No size changes with account profit; no MCL. Neither budget selected as winner.
Re-run engine using dev bars only; full intrabar paths into existing Combine simulator, configured
$3,000 target/$2,000 trailing loss/55% consistency/DLL off. Rolling starts every dev trading day
and sequential cost/pass; these are rough in-sample operational scenarios, not new edge evidence.
Count three scenarios, including positive-expectancy tests; count each raw-bar spotcheck only as
verification, not a performance cell. No extra variants after results.

Audit correction after first execution: Claude's proxy is zero on some stop exits, so Rnet
can be -infinity. Preserve literal reproduction, but compare denominator differences only
where finite (four already-counted diagnostic cells). Add two counted literal-proxy >12
Asia/RTH cells to verify Claude's exact quoted threshold counts, alongside planned-risk cells.
Re-execute unchanged sizing scenarios only to regenerate a complete corrected output bundle;
these are duplicate calculations, not additional candidate selections.
