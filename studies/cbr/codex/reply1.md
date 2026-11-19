**1. Independent CL translation**

I agree with Claude’s type-3 sequence. The diagrams support it, but several execution details remain discretionary.

For longs; reverse everything for shorts:

- **Bias/wick concept:** establish bullish bias from completed CL hourly data, then seek a bearish excursion that could become the current hour’s lower wick. Never require that unfinished hour to *eventually* close bullish.
- **Extension:** require ≥20 elapsed minutes moving against bias. “Without substantial pullbacks” needs a numerical definition; it does not mean every candle must fall.
- **Context:** either sweep the reference first-hour low, or rebalance a recent trending range. Define sweep as ≥1 tick beyond the low, followed by a close back above before entry.
- **Type 3:** owner-rule L1 → H1 → L2, with L2<L1, then a 1m close strictly above H1’s wick high. Freeze H1’s identity before the break.
- **Entry:** limit at `(L2+U)/2`; stop exactly L2. For the baseline, U is the highest high from L2 through the first qualifying MSB close. Freeze both then; round entry down to ticks.
- **Target:** extension midpoint `(A+L2)/2`, where A is the declared extension origin; alternatively 1.5R or 2R. Reject midpoint targets at/below entry.
- **Attempts:** maximum two filled trades per session; stop for the CME trading day after the first net-positive exit. An expired order is not an attempt.

**Differences from Claude:** the eventual MSB-push high is unknowable at the break; using it requires a separate delayed-confirmation version. The 30m sweep is optional confluence, not mandatory context. The PDF’s 2R example supports testing 2R, although the principal text specifies 1.5R. Its claimed missed-entry percentage is not evidence for CL.

Fix additional mechanics: one working order/position, ten-minute order expiry capped at window end, target-touch cancellation, no chasing, one contract, engine exits/15:10 CT flatten.

**2. CL windows**

These are hypotheses about comparable participation changes, not established CL edges. Windows are half-open; the reference hour immediately precedes each.

| Analog | Entry window, CT | Rationale |
|---|---|---|
| Literal gold clock | 19:00–20:00 CST / 20:00–21:00 CDT | Preserves 01:00–02:00 UTC |
| Globex reopening | 18:00–19:00 | Second hour after 17:00 reopening; structurally closest |
| London participation | 03:00–04:00 normally; 04:00–05:00 during UK/US DST mismatch | Second hour after 08:00 London |
| Owner’s 08:00 NY anchor | 09:00–10:00 | First-hour US range sweep |
| Owner’s 08:30 RTH proxy | 09:30–10:30 | More active US participation |
| EIA event analog | 10:30–11:30 normally Wednesday | Second hour after release; separate event hypothesis |

CME confirms CL’s 17:00–16:00 CT electronic session. London’s 08:00 opening supplies a reproducible participation anchor, not a CL exchange opening. [CME](https://www.cmegroup.com/education/courses/event-contracts-underlying-markets/wti-overview.hideSubnav.educationIframe.html?hideAddThisExt=y&hideFooter=y&hideRightRail=y), [LSE](https://www.londonstockexchange.com/en/resources/faqs/personal-investing?lang=en)

EIA normally releases at 09:30 CT, with exceptions: use historical release dates/times. For ordinary windows, predeclare exclusion from 09:25–09:45 on release days, including working orders/positions. [EIA schedule](https://www.eia.gov/petroleum/supply/weekly/schedule.php)

**3. CL-only bias proxies**

Use four alternatives: no-bias control; last completed hourly candle body direction; strict hourly body engulfing in the trade direction; owner hourly structure with both higher highs/higher lows bullish, both lower bearish, otherwise abstain. Freeze bias at window start.

None reproduces DXY’s independent cross-market information. VWAP is another possible proxy only if volume is available; exclude it from this initial budget.

**4. Version dimensions and testing**

| Dimension | Concrete values |
|---|---|
| Window | Six rows above |
| Context | First-hour sweep; extension-only rebalance proxy; rebalance plus previous completed 30m sweep in window’s final 30 minutes |
| Bias | Four alternatives above |
| Extension | `(duration, maximum counter-retracement, efficiency)` = `(20m,25%,0.65)`, `(30m,25%,0.65)`, `(20m,33%,0.55)` |
| Target | Extension midpoint; 1.5R; 2R |
| Attempts | One; two, both stopping after first win |

Define A as the most recent confirmed owner high 20–60 minutes before L2 satisfying the extension filter. Counter-retracement is the largest subsequent low-to-high recovery divided by A−L2; efficiency is absolute endpoint close change divided by summed absolute minute-close changes. Mirror shorts. “Extension-only rebalance” is explicitly a simplified proxy, not a reconstructed Kane model.

That is **1,296 combinations**. Do not exhaust them. Predeclare **48 dev runs maximum**, including robustness and strict-fill checks. Screen windows with fixed baseline, retain at most two, then compare dimensions sequentially. Reserve twelve runs for neighbours and fill sensitivity. Log every trial; report best-of-N, annual stability, day concentration, and day-block uncertainty. Freeze one finalist for one validation run, then one holdout run under protocol gates. Earlier history was previously researched; only forward data is clean.

**5. Point-in-time pitfalls**

Use `swing_state(..., prev=True, newest=True)`; never final `swing_points`. Candle k becomes known at k+1’s close; raw `detect` state[k] therefore belongs one candle later. Replacements, removals, equal-price later winners, and dual-point candles require identities/event order, not prices alone; never forward-fill removed levels.

Reject setups spanning rolls—from bias/reference/extension inputs and swing left-neighbours through signal—not merely entries crossing rolls. Swings continue across unadjusted contracts, so engine roll exits alone are insufficient.

Use completed HTF candles and `avail`; clock minutes, DST, missing bars, and offset-30m alignment matter. Orders start next bar. Preserve engine stop-first ambiguity, prohibited fill-bar targets, fees, and causal attempt accounting; spot-check raw bars. No files were edited or backtests run.