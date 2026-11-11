# Reverse FSP

This optional implementation is excluded from the default FSP runner and default validation suite.
There is no reverse-order comparison in the first-default test.

Direction-reversal variant of the first FSP default. Uses the standard FSP setup and signal generator,
without changing the mandatory swing detector, setup timing, 15m confirmation or 1m MSS conditions.

Defaults inherit **50-tick TP, New York entries only and a daily no-carry reset** from FSP.
No performance results are recorded.

- Original short signals place **buy limits**; original long signals place **sell limits**.
- Keep the original planned limit price.
- Let R be the original planned stop distance, 1–25 ticks. Mirror that distance across the planned entry:
  `reverse stop = 2 × planned entry − original stop`.
- TP is **50 ticks from the actual fill**, both directions.
- The originating setup's fixed breach-candle high/low bounds MSS eligibility. Later 1H points do not
  expire it. Already-placed orders are unaffected by the MSS cutoff, as in the standard implementation.
- Entry/fill window is 09:00–14:30 New York time; pending limits cancel at that cutoff. At the scheduled
  daily close, flatten remaining positions, cancel all orders and discard all failed setups. Wait for a
  fresh failure setup. One account position, fresh attempts allowed, fixed pending limit, roll exits and
  $2.01 commission per filled order remain. No added slippage; performance ends before 2024.

Examples of planned prices:

| Original short limit / stop | Reverse long limit / stop | Reverse TP if filled at its limit |
|---|---|---|
| 86.97 / 87.22 | 86.97 / 86.72 | 87.47 |
| 85.37 / 85.54 | 85.37 / 85.20 | 85.87 |

This is not a guaranteed inversion of the original ledger. A buy limit is marketable when the open is
at or below it; a sell limit is marketable when the open is at or above it. Reversing the side can change
the fill time and price, how many later signals are available while flat, stops and targets, and commissions.
Better gaps can reach/pass the mirrored stop; these fills follow the same broker rules and are counted
explicitly as having nonpositive initial stop distance. Gaps can also exceed the planned risk on exits.

Any future test of this separate implementation needs its own explicit scope and provenance.
Commission remains $2.01 per filled order,
or $4.02 per completed one-contract round trip.
