# Tupa 1

Status: Research · Historical setup census

Tupa 1 looks for an outside candle that sweeps both levels of the previous candle in order, followed by a retest while the higher-timeframe swing still applies. The study tests whether this sequence occurs often enough in CL to research entry and exit rules.

## Rules

| Swing timeframe | Catalyst timeframe | Reference for candle 1 and the catalyst swing |
|---|---|---|
| 4H | 1H | Previous daily candle |
| 1H | 15m | Previous 4H candle |

Candle 2 is a **swing low for a long** and a **swing high for a short** under [the owner's swing-point rule](../../SWINGS.md).

For a long, candle 1 closes at or below the low of the reference candle immediately before the one containing it. A single catalyst inside candle 1 touches or breaks its preceding candle's high first, then its low. When it reaches the prior low, the latest confirmed catalyst-timeframe swing must be a high strictly above the reference low. For a short, candle 1 closes at or above the reference high. The catalyst takes the prior low first, then the high. When it reaches the prior high, the latest confirmed catalyst-timeframe swing must be a low strictly below the reference high.

If the second-touch minute also invalidates the required paired swing, the second touch qualifies only when the minute opens at or beyond the second-touch level and the swing is still active at the open.

### 4. Retest and setup confirmation

After candle 2 closes, look for the first touch or break of the original catalyst's high for a long or low for a short. A retest by the close of candle 3 can confirm in one of two ways.

- **Swing-timeframe confirmation.** Wait for candle 3 to close and confirm candle 2 as the latest swing point. For a long, candle 3's low is strictly higher than candle 2's low. For a short, its high is strictly lower than candle 2's high.
- **Catalyst-timeframe confirmation.** Inside candle 3, a single 1H or 15m candle touches or breaks its preceding candle's low first, then its high for a long. A short requires high first, then low. The setup confirms once the original retest and this sweep have both occurred inside candle 3 and candle 2 meets the owner's swing rule against candle 3's range so far. The scan evaluates this at the close of the one-minute bar that completes the conditions.

For a retest after candle 3 closes, candle 2 must still be the latest swing point. If a gap delays candle 3's close, a retest during the minute that closes it still requires confirmation at that close. If the retest minute also touches and invalidates candle 2's paired swing, the retest qualifies only if it was reached at the open before that invalidation.

Each catalyst contributes at most one setup, using its earliest confirmation. An early confirmation is recorded as it was known at the time, even if price later breaks candle 2's swing level before candle 3 closes. One-minute bars resolve touch order. If both levels are first reached in one minute, use the open if it has already reached either level. Exclude sweeps whose order remains unknown. Contract rolls are included and marked.

## Historical setup count

One descriptive census across the local CL history from 7 June 2010 to 17 November 2026. The charts show the first retest and mark early confirmation separately when it occurs. The example used to define the rules comes from this history. This stage has no entry, exit, P&L or Combine results.

| Timeframes | Retest timing | Long | Short | Confirmed early |
|---|---|---:|---:|---:|
| 4H–1H | By candle 3 close | 41 | 42 | 23 |
| 4H–1H | After candle 3 closed | 11 | 25 | — |
| 1H–15m | By candle 3 close | 324 | 318 | 163 |
| 1H–15m | After candle 3 closed | 102 | 110 | — |

Run `cd web && npm run export:tupa-setups` to rebuild the census and its charts from local CL bars. The results stay in the ignored `results/tupa_1/` directory.

## CLJ6 example, 18 March 2026

The 2 p.m. 4H candle was a swing low at 91.96, so the setup was long. The latest confirmed 1H swing high was 96.41 when the 1 p.m. catalyst reached the prior hour's low, above the previous daily low of 93.83. Price retested the catalyst high of 93.56 in the 6 p.m. minute. Inside 4H candle 3, the 7 p.m. 1H candle broke the 6 p.m. low of 94.45 in the 7:12 p.m. minute, then its high of 94.97 in the 7:26 p.m. minute. The setup confirmed at 7:27 p.m. The 4H candle closed at 10 p.m. All times are Malaysia time.
