# CBR optimize: findings (2026-11-19, corrected 2026-11-20)

Correction 2026-11-20 (Codex adversarial review): the replay rebuilt the target from the actual risk when a
fill was better than the limit (open through it); the strategy freezes it from the limit. Fixed and re-run
(`tests/test_cbr_optimize.py`): 18 of 1,695 fills were affected, every number moved by ≤ 0.008 R, and no conclusion
changed. Second correction 2026-11-20 (Codex adversarial review): break-even and runner management counted the
fill bar's high, which may print before the fill; they now use bars after the fill bar only (as RLM does; tests in
`tests/test_cbr_optimize.py`). Only those two rules moved (BE +0.030/+0.019 to +0.044/+0.024; runner 5 / 10 bars
H2 +0.027/+0.001 to +0.004/−0.007); fixed targets, time stops and entry features are unchanged. Conclusions hold.
Third correction 2026-11-20 (Codex adversarial review): an open through the limit that also reached the stop gave a
non-finite or −1R outcome; it now exits at the fill on the fill bar (fee only, as the engine), normalised by the
intended risk, and entry features use the intended risk known at the signal. 1 of 1,695 fills was affected; the
study now refuses non-finite outcomes. Every displayed number is unchanged.
Numbers below are the corrected run.

Plan (declared before any run): `README.md`. Code: `run.py`. Per-setup rows: `setups_dev.csv`. Output:
`results_dev.txt`, `fill_delay_check.txt`. Dev only, setup level (1,695 filled rth setups, each simulated alone),
in-sample; H1 2010-06..2015 learn, H2 2016..2021 confirm. Looked at: 18 entry features + 11 exit rules.
Fills for every exit rule are those of the 2R base (the 2R target-touch cancel); a 1R or 4R version would cancel a
few orders differently.

## Base edge decays
Mean net R per setup, 2R target: **H1 +0.173, H2 +0.022** (validation 2022-24, contaminated: +0.053). The edge
lives mostly in 2010-15. That alone explains the validation fail.

## Exits: nothing beats 2R fixed in both halves
| Rule | H1 | H2 |
|---|---|---|
| 2R (base) | +0.173 | +0.022 |
| 1R / 1.5R | +0.139 / +0.136 | −0.009 / +0.017 |
| 3R / 4R | +0.161 / +0.150 | +0.026 / +0.032 |
| breakeven at 1R | +0.044 | +0.024 |
| time stop 10 / 20 / 30 bars (< +0.5R) | +0.173 / +0.148 / +0.156 | +0.014 / +0.005 / +0.014 |
| runner to 4R if 1R within 5 / 10 bars | +0.159 / +0.165 | +0.004 / −0.007 |

- Breakeven at 1R is the worst: CL pulls back through entry after +1R on most eventual winners.
- Early exits (time stops) cut winners as often as losers: a slow start does not predict a loser.
- Aiming higher (3R, 4R) helps in H2 and hurts in H1, and the runner now trails 2R in both halves: no stable
  "this one can run" signal.

## Entry features: 17 of 18 flip between halves
Only `fill_delay` passed the declared rule (orders filled in the first 2 bars after the signal: H1 +0.128 vs
+0.215, H2 −0.038 vs +0.074). Day-block bootstrap of the difference: H1 [−0.11, +0.30], H2 [−0.06, +0.30], dev
[−0.04, +0.24]: every interval includes 0. On validation (contaminated) it reverses: fast fills +0.103, slow +0.010.
With 18 features tested, one passing by chance is expected. **Not adopted.**

Everything else (risk size, risk/ATR, room to target, run length, run cleanliness, sweep depth, minute in window,
morning range, side, Wednesday/EIA, day trend, PDF confluences) changes sign or size between H1 and H2.

## Verdict
No skip rule, early exit or "let it run" rule is stable enough to trust. Adopting any of them would be fitting
noise in ~1,700 trades with a +0.09R average edge. CBR stays dropped; holdout not used.
