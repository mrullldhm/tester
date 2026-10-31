# Fair Price Reversal: feature 2 (optimize) results

**Start here.** Verdict at the bottom. Other files in this folder:

| File | What |
|---|---|
| [`features_ny.md`](features_ny.md), [`features_london.md`](features_london.md), [`features_asia.md`](features_asia.md) | E1: which feature values go with good / bad trades |
| `search_<session>_filters_random_net1_s1_n200.md` | E2 search reports: baseline vs winner, neighbours, top 20 |
| `search_<session>_full_tpe_net1_s1_n300.md` | E3 search reports |
| `winner_<same name>.md` + `.png` | Full TradingView-style report of each frozen winner |

The two candidates: [`winner_ny_filters_random_net1_s1_n200.md`](winner_ny_filters_random_net1_s1_n200.md) and
[`winner_london_filters_random_net1_s1_n200.md`](winner_london_filters_random_net1_s1_n200.md). The feature-1
result is [`../README.md`](../README.md).

Lab notebook (docs/OPTIMIZE.md, "Agent loop"). Hypotheses and budgets are written **before** the runs they
describe. Every run is in `results/fair_price_reversal/ledger.jsonl`. All numbers are in-sample, development
interval (bars before 2024-01-01 UTC).

## Protocol declared 2026-10-31, before any feature-2 run
- Baselines: the feature-1 top combination of each variant (`BASELINES` in the strategy). They were picked on
  2010-06 .. 2026-10, so the baselines themselves already saw the reserved interval (lineage line of the ledger).
- Objective for every search: `net1` (net profit + open P&L at 1 tick slippage), at least 300 closed trades at
  1 tick. Reason: every feature-1 top combination lost money at 1 tick; a 0-tick objective would reward edges
  smaller than one tick of slippage per fill.
- Budget (trials per variant; each trial = 3 engine runs at 0 / 1 / 2 ticks; neighbours extra):

| Step | What | Sampler | Trials per variant | Seed |
|---|---|---|---|---|
| E1 | Association report, asia / london / ny | none | 2 engine runs | 0 |
| E2 | `filters` space: baseline parameters frozen, filters searched | random (reproducible) | 200 | 1 |
| E3 | `full` space: base parameters and filters | TPE, 4 jobs (not reproducible) | 300 | 1 |

  Nothing beyond this budget is run without a new dated entry here first.

**Exceptions (disclosed 2026-10-31, found by Codex R6).** Three looks happened outside this budget and were logged
after the fact (ledger lines `manual`): a RAM / timing benchmark (6 configurations, development interval), a TPE
plumbing smoke test (6 trials, development interval), and code checks on **all bars including the reserved
interval** before the cutoff was enforced: the NY baseline (already known from feature 1) and NY baseline +
`risk_ticks <= 30` (net -11,345 USD at 0 ticks over 2010-2026). The later candidate filter is the opposite
direction (`risk_ticks >= 30` / `>= 32`) and was chosen on development data, but this is still exposure: the
selection was not purely development-only, and validation must count it.

## Hypotheses (written before E1)
- **H1 anchor body.** A tiny anchor body is not a real "fair price" level: trades with low `anchor_body_atr` do worse.
- **H2 risk size.** With a small stop, one tick of slippage per fill is a large share of R, so trades with low
  `risk_ticks` lose most at 1 tick. A `risk_ticks` minimum helps the 1-tick result.
- **H3 regime.** `range_ratio` matters, direction unknown (two-sided, so weak prior).
- **H4 timing.** Late signals (`minutes_from_open` high) have less session left to reach the target.

## Results

### E1: association reports (2026-10-31)
[`features_asia.md`](features_asia.md), [`features_london.md`](features_london.md), [`features_ny.md`](features_ny.md).
Run twice (the second run only fixed bucket labels; both are in the ledger). At 1 tick:
- **H2 supported in every session.** The smallest-`risk_ticks` quintile loses with its 90% interval below zero
  (NY 6-19 ticks: -$22.00 a trade; London 4-11: -$19.00; Asia 3-8: -$13.36).
- **H1 partly.** Low `anchor_body_atr` buckets lose in NY and London; the pattern is not monotonic.
- **H3, H4: no pattern** beyond noise; weekday and direction differences sit inside their intervals.
- Asia has only 342 development trades at the baseline, so almost any filter takes it under the 300-trade minimum.

### E2: filters only, random, 200 trials per variant, objective `net1` (2026-10-31)
| Variant | Winner | Net 0 / 1 / 2 ticks | Trades | Baseline net 1 tick | Neighbours (net 1 tick) |
|---|---|---|---|---|---|
| ny | `anchor_body_atr >= 0.3`, `risk_ticks >= 32` | +63,293 / +49,297 / +34,592 | 927 | +2,423 | 6 of 6 above zero, median +48,069 |
| london | `risk_ticks >= 30` | +39,017 / +32,197 / +23,121 | 436 | -13,754 | 28 and 32 ticks: +29,712 / +32,865 |
| asia | `minutes_from_open >= 15` | +1,216 / -2,924 / -8,744 | 302 | -4,085 | still losing; no eligible profitable trial |

Reports: [`search_ny_filters_random_net1_s1_n200.md`](search_ny_filters_random_net1_s1_n200.md), [`search_london_filters_random_net1_s1_n200.md`](search_london_filters_random_net1_s1_n200.md), [`search_asia_filters_random_net1_s1_n200.md`](search_asia_filters_random_net1_s1_n200.md).

**Reading.** The one pre-declared, cost-based hypothesis (H2) is what the search found in both sessions with
enough trades, and its neighbours form a plateau, not a spike. Mechanism: at 1 tick a round trip costs
$4.02 commission + $10 entry slippage + $10 exit slippage = $24.02 when it exits by stop or at session end, and
$14.02 when it exits at the limit target (limits never slip), whatever the stop size. So trades with a small R
lose most of their edge to costs; with a `rr2` target a larger stop also means a larger target. The separate
engine runs per scenario, not this arithmetic, are the measure. Still in-sample, best of 200.

### E3: base parameters + filters, TPE, 300 trials per variant, objective `net1` (2026-10-31)
| Variant | Winner | Net 0 / 1 / 2 ticks | Trades | Neighbours (net 1 tick) |
|---|---|---|---|---|
| ny | `atr_mult=1.0`, `anchor_body_atr >= 0.3`, `risk_ticks >= 34` | +48,319 / +35,687 / +22,471 | 856 | 13 of 13 above zero, median +24,486 |
| london | `atr_mult=1.5`, `window=90`, `minutes_from_open <= 75`, `range_ratio <= 0.7`, `risk_atr >= 1.75` | +12,869 / +5,929 / -951 | 428 | 11 of 17 above zero, median +5,248 |
| asia | `atr_mult=0.5`, `swing=2`, `target=far`, `range_ratio <= 1.2` | +3,605 / -1,345 / -6,295 | 357 | 0 of 10 above zero |

**Reading.** In these runs the bigger search found **lower** objectives than E2 in NY and London (one seed each,
so this does not prove why; 14 dimensions for 300 TPE trials is the likely reason). Its best NY neighbour is the
E2-style configuration (baseline parameters, `anchor_body_atr >= 0.3`, `risk_ticks >= 34`: +47,764 at 1 tick), so
here changing the base parameters showed no improvement on top of the risk filter. The London E3 winner (two
changed parameters and three filters) loses at 2 ticks and 6 of its 17 neighbours lose at 1 tick: it fails the
plateau check, so it is not a candidate. Asia: no **eligible** trial (300+ trades) made money at 1 tick in 500
trials; 76 trials with fewer trades did, which is the minimum-trade rule doing its job, not evidence.

Report bug found and fixed while reading E3: the "Baseline vs winner" table picked rows by the label `baseline`,
and TPE had suggested the baseline again as a later trial, which hid the real winner. It now uses trial 0, there
is a test, and all six reports were re-rendered from their saved CSVs (no engine re-runs). The frozen
configurations were never affected.

### Replays
All six frozen configurations replayed through `cli replay` and matched their search trials exactly (net, open
P&L, trades, objective, every scenario): the `winner_*.md` files in this folder.

### By year: the candidates depend on high-volatility years
At 1 tick, development interval:

| Candidate | Positive years | Largest year |
|---|---|---|
| ny, E2 (`anchor_body_atr >= 0.3`, `risk_ticks >= 32`) | 11 of 14 | 2023: +18,014 of +49,297 (37%) |
| london, E2 (`risk_ticks >= 30`) | 9 of 14 | 2022: +18,656 of +32,197 (58%); 180 of 436 trades |

A stop of 30+ ticks happens mostly when crude is volatile, so a fixed tick threshold is partly a volatility-regime
filter, and its trade count swings with the price level (2017: 7 trades in NY, 2 in London). The scale-free
`risk_atr` did not win. This is a question for out-of-sample validation (feature 3), not for more tuning here.

## Verdict (feature 2, 2026-10-31)
- **Candidates for validation:** NY E2 and London E2 (the risk filter). On the development interval, London goes
  from -13,754 to +32,197 at 1 tick; NY's baseline already made +2,423 at 1 tick and goes to +49,297. Both stay
  positive at 2 ticks, with plateau-shaped neighbours and a cost-based mechanism (H2) declared before the search.
- **Independent replication:** Codex rebuilt NY E2 with its own engine, signal and feature code from the 2010-2023
  parquet files only: 927 trades / +63,293.46 USD at 0 ticks, 926 / +49,297.48 USD at 1 tick, every trade matched
  (`docs/REVIEWS.md`, R6).
- **Not candidates:** Asia (no eligible profitable trial), London E3 (fails the plateau check), NY E3 (below NY E2).
- **Exposure:** see the exceptions under the protocol; the selection was not purely development-only.
- **Still in-sample.** Picked from 1,500 search trials (plus neighbours), 4,534 engine runs in the ledger, on top
  of the feature-1 grid (192 combinations per variant) that picked the baselines with the reserved data included.
  Nothing here shows a tradable edge.
- Next (feature 3): walk-forward and the reserved interval for the two candidates, with the ledger's trial count
  in a deflated-Sharpe style correction; check whether a scale-free risk filter holds up better than ticks.
