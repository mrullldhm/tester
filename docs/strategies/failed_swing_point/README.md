# FSP — Failed Swing Point

First default settings, 11 November 2026. CL1! only, one contract, both directions, **New York entries only**.
This is a separate strategy from Tupa Trade. Default performance interval ends before 2024-01-01 UTC.

**First default:** TP **50 ticks from actual fill**, maximum planned risk **25 ticks**, New York
entry/fill window **09:00–14:30 America/New_York**, and no overnight positions, orders or failed setups.
This is the default FSP test, with no reverse-order comparison.

## Setup and confirmation

Track provisional **1H** swings using only `indicators/structure_swings.pine` / `tvtester/swings.py`.
An equal touch/breach of a provisional low before an opposite swing is accepted creates a short setup;
a provisional high failure creates a long setup. Retain the failed level and its first touching minute
even though the detector removes that provisional endpoint.

Wait until the containing **15m** candle closes. Its close may be on either side of the failed level.
An entry-triggering minute must occur after that close. Default tests do not compare 30m or other setup
timeframes; those remain future variations. A missing last minute uses the existing owner candle-close timing.

Every failed setup has its own fixed confirmation-candle boundary. Later 1H points do not expire it;
multiple independent failure setups, including setups in the same direction, can coexist until their
own 15m boundary is reached or the New York session ends.

## One-minute entry

For shorts, wait for a touch/break of an owner **HL** formed after the initial source failure. For longs,
use the mirror touch/break of an owner **LH**. The structure may form inside the confirming 15m candle,
but its break must occur after that candle closes. A structure on the first breach minute is eligible
because its directional extreme follows the source-level touch. It must still pass all owner swing rules
and have become known at its right candle's close before a later minute can trigger it.

An equal touch triggers the signal. Wait for that **1m candle to close**, then place a limit order active
from the next minute. The signal candle need not close beyond the HL/LH. A structure touched before entry
becomes eligible is used up; later re-touches do not become delayed signals.

**Only the first valid entry signal per failed 1H setup is eligible:** the first qualifying 1m HL break
for shorts, or LH break for longs, after confirmation and within New York entry hours. That setup cannot
supply a later MSS or another limit after TP, SL or cancellation. If its first valid signal arrives while
another position or unchanged limit is active, skip that opportunity; do not defer it to a later break.
A further trade requires a new failed 1H setup.

## Stop, limit, target

For a short, use the **highest high after the HL formed**, through the signal minute inclusive. The high
must have an equal/lower high immediately to its left; do not wait for a right candle to confirm it.
For longs, use the lowest low after the LH, with equal/higher low to its left. Equal extremes select the
later candle. The structure candle's opposite extreme counts only if it follows the structure point in
the mandatory minute extreme order. These are stop-price anchors, never alternative swing points.

- Planned initial risk at the signal close of 1–25 ticks: limit at that close.
- Risk above 25 ticks: short limit = stop minus 25 ticks; long limit = stop plus 25 ticks.
- A nonpositive planned stop distance cannot place an order.
- Freeze the stop and limit at placement. Limit fills may be at the limit or better.
- TP is **50 ticks from the actual fill**, with the fixed stop bracket attached to the entry.
- Commission is **$2.01 per fill**, **$4.02 round trip**. No added slippage.

## MSS validity and waiting limits

Freeze the high and low of the **15m candle containing the initial 1H-candidate breach**, only when that
confirmation candle is known closed. Do not count that candle touching its own high or low as invalidation.

- **Short:** a later equal touch/breach of that fixed 15m high ends eligibility for subsequent 1m HL-break MSS signals.
- **Long:** a later equal touch/breach of that fixed 15m low ends eligibility for subsequent 1m LH-break MSS signals.

The boundary never moves to a newer 15m candle. The MSS minute must close before an order can be placed;
if it reaches the boundary within that same minute, reject its entry signal. Late confirmation after a
missing source close minute also checks the observed post-candle price at the moment the range becomes known.

This is an **entry-trigger validity rule**, not an additional cancellation of an already placed limit.
An order created by an earlier valid MSS keeps its planned price and bracket. On a normal retracement
path, entry is reached before the confirmation-candle boundary; gaps follow the same limit/stop broker
rules. No new 1H candidate, previous-1H-candle extreme or later 15m boundary touch cancels that waiting order.
An expired setup cannot supply later MSS attempts, but expiry does not undo a valid earlier signal/order.

At **14:30 New York time**, or the earlier scheduled CL exchange close on a holiday, cancel all orders,
close any remaining position at that minute's close, and discard every failed setup. No position continues
beyond the New York session. Afterward wait for a new failure setup; never re-arm a discarded setup.
Fresh failures after the cutoff belong to the next New York reset cycle and may supply next-session
entries if still valid. The CL evening reopen does not impose an additional reset. Swing context continues.
There is no one-trade-per-day cap, but each independent failed 1H setup has at most one entry attempt.
There is no additional TP-before-fill cancellation. The repository's contract-roll rule closes
positions and cancels unfilled orders at the old contract's last bar; swing detection continues across rolls.
There is one account position and one pending order. If independent setups signal simultaneously while
flat, use the most recent failed setup; ties use the later touch in the mandatory minute path.

## Verification and execution

Focused checks use unittest, not pytest. Historical minute fills use the repository's open/nearer-extreme/
other-extreme/close path. No tick sequence is inferred beyond that convention. Stop gaps can exceed planned
risk; better entry gaps through a stop can create a zero/nonpositive initial-risk trade, which must be reported.

FSP does not attach an intrabar high/low cancellation boundary to pending entries. The broker still
supports optional boundaries for separate consumers; that generic functionality does not change this
strategy's rules. TradingView compilation and export parity are not established.

Session flattening uses **14:30 America/New_York**, capped by the earlier scheduled CL exchange close,
not the swing helper's delayed daily confirmation at the next reopen. The bounded local
calendar in `tvtester/fsp_clock.py` includes holiday early closes through 2026. The date/time schedule,
not the next observed data gap, determines the normal exit. **Halt exception (owner, 11 November):**
if the cutoff passes without a tradable closing minute, cancel the old orders and close the position
at the **open of the first available reopening bar**, before its intrabar SL/TP movements. That overdue
exit is labeled `New York halt reopen`; no historical closing price is fabricated. The failed setups
still reset at the session boundary. Calendar coverage beyond 2026 must be extended before a later-date run.

Schedule references: [CME WTI hours](https://www.cmegroup.com/education/courses/introduction-to-energy/introduction-to-crude-oil/wti-overview),
[CL holiday-close calendar rules](https://github.com/rsheftel/pandas_market_calendars/blob/master/pandas_market_calendars/calendars/cme_globex_energy_and_metals.py).

All 43 focused unittest checks pass, including first-signal-only entry, no retry after TP/SL/cancellation,
busy-account signals, session flattening, DST, early closes, missing close
prices, reopening exits before intrabar brackets, stale setups, the fixed 15m boundary and preservation
of already placed limits before cutoff.
A replay of all 2023 CL data also passes the entry/exit session, forced-close, no-carry and setup-reset
checks. This integration check records no performance baseline.
The 13 February 2012 Globex halt has no tradable 14:30 ET closing price in the minute data;
trading resumes at 15:15 ET, so the owner-approved reopening exception applies.
[S&P Global's contemporaneous notice](https://www.spglobal.com/commodity-insights/en/pricing-benchmarks/our-methodology/subscriber-notes/021312-platts-americas-moc-futures-assessments-february-13)
confirms the halt. The current [fixed default baseline](first_default_first_mss_halt_2023.md)
covers the complete available history through 2023. Independent raw CL replay matches all 3,198
entry/exit prices and times and net P&L to the cent, with no repeated trade from one failed setup.
It audits execution from supplied signals; it does not independently detect the owner swings.
No reverse comparison is part of the default test.

Run the auditable fixed default through the shared memory guard:

```bash
.venv/bin/python tools/run_limited.py tools/run_fsp.py --jobs 1 --run-tag first_default_first_mss_halt_2023
```

Each new run tag creates a separate result directory, status/provenance record, trades, setups, signals,
order actions and report. It refuses an existing tag and rejects a performance end later than 2024-01-01.
The ordinary CLI also supports `test failed_swing_point --end 2024-01-01 --jobs 1`.
