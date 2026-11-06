# Current owner-swing results, 4 November 2026

> **Superseded pending rerun — 5 November 2026.** Pine and Python now enforce the owner's clarified
> leg-extreme validity condition, including intervening non-pivot candles. All results on this page
> predate that correction and must not be presented as current. No reruns have been performed yet.

Only Fair Price Reversal and Tupa Trade are active. All current runs, features, exits, charts and future
strategies must use only [`indicators/structure_swings.pine`](../indicators/structure_swings.pine).
Swing detection is fixed: one neighbour per side, left equality/right strictness, next-close confirmation,
alternation, same-type extreme replacement (equal: later), ordered outside candles, equal HH/LL labels,
and continuity across contract rolls. No feature can tune these rules.

Source SHA-256: `162bba6a226acdcc518042b100f7ff33186501479dd4d0634be1c48a70f5be13`.

Execution: limit entries; $2.01 commission per order ($4.02 round trip), one CL contract, no added slippage.
F0/F1/exit studies use all available bars, 2010-06-07 through 2026-11-03 (5,674,164 one-minute bars).
F2/F3 use development data before 2024 only. F1 starting settings were selected on full history, so the
reserved interval is not clean out-of-sample data.

## F0: default configurations

| Strategy | Closed trades | Net profit (USD) |
|---|---:|---:|
| fair_price_reversal | 3,656 | -21,527.12 |
| tupa_trade | 3,406 | -36,432.12 |

## F1: net-profit references and 13 metric winners

| Strategy / session | Grid settings | Closed trades | Best net profit (USD) |
|---|---:|---:|---:|
| fair_price_reversal / asia | 64 | 1,634 | -6,418.68 |
| fair_price_reversal / london | 64 | 1,967 | +11,712.66 |
| fair_price_reversal / ny | 64 | 4,664 | +60,180.72 |
| tupa_trade / ny | 4 | 855 | -13,547.10 |

All values are in-sample selections. Each session also has separate saved winners for 13 objectives;
the table above shows the unconstrained net-profit reference. Current source reports:
[Fair Price Reversal](strategies/fair_price_reversal/README.md),
[Tupa Trade](strategies/tupa_trade/results.md).

## F2: current searches

| Session / space | Trials | Winner net (USD) | Trades | Positive tested neighbours |
|---|---:|---:|---:|---:|
| asia / filters | 200 | +5,038.40 | 580 | 6 / 6 |
| asia / full | 300 | +7,838.14 | 493 | 15 / 15 |
| london / filters | 200 | +15,599.54 | 1,423 | 6 / 6 |
| london / full | 300 | +14,922.76 | 1,462 | 9 / 9 |
| ny / filters | 200 | +84,729.22 | 1,739 | 3 / 3 |
| ny / full | 300 | +85,071.32 | 1,634 | 11 / 11 |

Six completed current-rule searches used 1,500 trials in total. The NY wider search was completed
before the interruption; London and Asia wider searches have new recovery IDs. Incomplete attempts
remain preserved and count as research expenditure. Neighbour checks are exploratory, not validation.
Full-search candidates need a separately declared validation protocol; current F3 covers the 200-trial
random filters-only searches.

## F3: validation of the random-filter searches

| Session | Walk-forward net (USD) | Positive years | PBO | DSR probability | Advance to F4 |
|---|---:|---:|---:|---:|---|
| asia | -2,967.60 | 5 / 10 | 0.7724 | 0.0848 | No |
| london | -1,045.58 | 6 / 10 | 0.1663 | 0.4732 | No |
| ny | +39,463.24 | 7 / 10 | 0.0107 | 0.7591 | No |

None of the three validated candidates advances. F4 and F5 have not been run.

## Exit study: fixed swing detection

| Session | Rules | Baseline net (USD) | Best rule | Best closed net (USD) |
|---|---:|---:|---|---:|
| asia | 396 | -6,418.68 | BE after 60 bars +1t | -2,258.68 |
| london | 396 | +11,712.66 | none | +11,712.66 |
| ny | 396 | +60,180.72 | none | +60,180.72 |

The exit study ranks net profit plus final open P&L; the table shows closed-trade net profit.
Only exit management varies. Swing trailing uses the same owner swing state; its detection has no setting.
See [the exit report](strategies/fair_price_reversal/exits/README.md) for every family and winner.

## Verification and recovery

- 19 unittest checks passed for owner swings, limit entries and recovery safety. Pytest was not run.
- An independent owner-rule calculation matched all six swing series across 12,267 CL bars, prefix checks,
  roll continuity and 512 browser states. FPR signals matched an independent Pine transcription for all sessions.
- Arithmetic audit: 34 current summaries and 84,273 saved trades matched fill-price P&L and round-trip fees.
- The authoritative Pine source is unchanged; alternative strengths and generic pivots are rejected.
- Heavy recovery commands ran sequentially through `tools/run_limited.py`, with an 8 GiB address-space limit.
- [Crash evidence and safeguards](WSL_RECOVERY_2026-11-04.md); durable logs:
  `logs/owner-swing-recovery-20261104/`.

Both website exports were refreshed. Astro check passed with no errors or warnings; the static build
generated 38 pages. Built F1 totals match the current tester summaries, and the retired strategy route is absent.
No commits were made.
