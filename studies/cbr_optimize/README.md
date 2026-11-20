# CBR optimize: skip losers, cut losers early, let winners run (plan, written before any run)

2026-11-19, owner request. Base: the frozen CBR lead (rth 09:30-10:30 CT, context reb, no bias, 1m type 3, limit at
50% of the MSB move, stop at L2). That version **failed validation 2022-2024** (PF 1.02), so validation is spent:
it may be shown as a contaminated sanity line, never used to choose. The only clean test left is **holdout
2025-01..2026-11-11** (once, owner's yes) and forward.

## Data and sample
Setup-level, dev only: every rth type-3 setup with a 20-min run (`dur` filter, `e20` kept as a feature), risk ≥ 5
ticks, simulated alone (no one-order-at-a-time), engine rules (touch fills, fill at min(open, limit), target-touch
cancel, stop first inside a bar, no target on the fill bar, flat 15:10 CT or day end/roll, fee $4.04). Outcome in R
(net, fee included). Learn on **H1 = 2010-06..2015**, confirm on **H2 = 2016..2021**.

## Entry features (known at the signal close; declared now, nothing added after looking)
| # | Feature | Why it might matter |
|---|---|---|
| 1 | risk ticks (entry − L2) | tiny stops die to noise, big stops to fees/size |
| 2 | risk / ATR(30 1m bars) | stop size relative to current noise |
| 3 | room = (run origin − L2) / risk | how far the rebalance target is in R |
| 4 | run duration (bars from origin to L2) | longer run, more trapped traders |
| 5 | run bounce ratio and close efficiency | cleaner run |
| 6 | sweep depth: L1 − L2 in ticks / risk | the stop hunt |
| 7 | minutes into the window at the signal | early vs late |
| 8 | side | long vs short |
| 9 | ref-hour range / ATR | quiet vs busy morning |
| 10 | Wednesday (EIA 09:30 CT) | report hour |
| 11 | session trend aligned: signal close vs 17:00 CT open, in trade direction | with/against the day |
| 12 | ref body aligned, 1h structure aligned, fh sweep, 30m sweep | PDF confluences |

## Exit rules (declared now; small set)
| Rule | Values |
|---|---|
| fixed target | 1R, 1.5R, 2R (base), 3R, 4R |
| breakeven: stop to entry after +x R | x = 1 |
| time stop: exit at the close of bar k after fill if open P&L < +0.5R | k = 10, 20, 30 |
| runner: target 2R, but if +1R comes within m bars of the fill, target 4R | m = 5, 10 |

## Selection rule (anti-overfit)
1. Entry feature: thresholds = H1 terciles. A feature qualifies only if, in H1 **and** H2 separately, the worst
   tercile has mean R below the best tercile by ≥ 0.10 R, in the same direction, and the middle tercile sits
   between them (monotone) or the skipped tercile alone is negative in both halves.
2. At most **2** filters combined. Skip only the worst tercile (never keep only a thin slice).
3. Exit rule: must beat 2R-fixed in mean R in both H1 and H2.
4. The chosen spec is run through the engine (`cli test --period dev`, touch and `--through 1`) with Combine stats.
5. Count: ~16 features × terciles + 11 exit variants are looked at; every result says best of that.
6. Then stop. Holdout only with the owner's yes.
