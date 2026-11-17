# Study: swing point through the previous day's low/high (setup count, 4h and 1h)

A count, not a strategy: no orders, no outcomes, no Combine. It answers "how often does this shape happen?"
before any strategy is built on it. Owner request 2026-11-17: short side first (below), then the long mirror and
the 1h timeframe (section "Long and 1h").

## Data

CL 1m bars, trading days 2010-06-01 to 2024-12-31 (dev + validation). Holdout (2025+) is not loaded. Reported per
period (dev, validation) and per year. 4h candles and swing points from `cltester/swings.py` (owner rule only).

## Definitions

- **4h candle**: `build_candles(df, "4h")`, blocks from the 17:00 CT open.
- **Swing points**: point-in-time. The swing low at candle c2 is the event when the state after processing c2
  (known at c3's close) has `newest = swing low` at candle c2. A rule-5 replacement is a new event.
- **SH0**: the swing high before that swing low in the same state (`sh`).
- **PDL**: low of the CME trading day before the trading day of the swing low candle c2.

## Groups

| Group | Rule |
|---|---|
| C1 PDL cross | SH0 > PDL and swing low price ≤ PDL (touch or break) |
| C2 any | every swing low event, PDL not a factor (owner 2026-11-17) |
| SL above PDL | swing low price > PDL (info: C2 minus C1 minus other) |
| other | SH0 ≤ PDL already (swing structure was already below PDL) |

Candle shape after the swing low (c1 = left candle, c2 = swing low, c3, c4 = next two 4h candles):

| Shape | Rule |
|---|---|
| C3 | c3 is the swing high: c3.high ≥ c2.high and c4.high < c3.high (rule 3); c4.low ≤ c2.low (touch/break swing low) |
| C4 | c3.high ≥ c2.high; c4.high ≥ c3.high **first**, then c4.low ≤ c2.low (1m order inside c4) |
| C4? | as C4 but both prices in the same 1m bar (order unknown) |
| none | anything else (c3 not a swing high shape, or c4 never touched the swing low) |

Report: count of each Shape inside each Group, per period and per year.

## Note on C4 and the swing rule

Under the owner rule a swing high needs its right candle strictly lower (rule 3). If c4 touches c3's high, c3 is
**not** a swing high: c4 takes over as the high (owner confirmed 2026-11-17). So C4 is a candle shape, counted at
c4's close; whether c4 later becomes a confirmed swing high needs c5 and is not part of this count.

A swing low that comes back after rule 4 removed a newer one is not a new event (only a later candle counts).

## Long and 1h (owner 2026-11-17)

**Long** is the exact mirror: swing high vs PDH (previous trading day's high). C1: swing low before it < PDH and
swing high ≥ PDH. C2: every swing high. c3 = swing low (c3.low ≤ c2.low); C3: c4.high ≥ swing high and
c4.low > c3.low; C4: c4 touches c3.low first, then the swing high. `run.py` implements it as the short logic on
negated prices. **1h**: same rules on 1h candles (clock aligned); PDL/PDH stay daily.

Same-minute C4 touches: a minute that opens beyond a threshold touched it first; otherwise "unknown".
Events on the first data day, or before any opposite point exists, count in C2 only.

## Results (2026-11-17, in-sample descriptive count, one frozen spec, no tuning)

Two independent implementations: `studies/pdl_swing_4h/run.py` (Claude) and `codex_count.py` (Codex; review in
`codex_review.md`, v2 output `codex_counts_v2.txt`). Event-by-event diff on 1h: every shared event has the same
shape; the only differences are boundary conventions (Codex drops a c2 whose c4 falls in the next period: one
1h long C3 on 2021-12-31). 4h cells match exactly.

C = count in dev 2010-06..2021 / validation 2022..2024. C4 = correct order only.

| TF | Side | Group | C3 dev | C4 dev | C3 val | C4 val |
|---|---|---|---:|---:|---:|---:|
| 4h | short | C1 PDL cross | 68 | 19 | 21 | 7 |
| 4h | short | C2 any | 209 | 84 | 55 | 38 |
| 4h | long | C1 PDH cross | 103 | 26 | 23 | 8 |
| 4h | long | C2 any | 265 | 77 | 70 | 21 |
| 1h | short | C1 PDL cross | 155 | 39 | 54 | 4 |
| 1h | short | C2 any | 1,123 | 277 | 281 | 81 |
| 1h | long | C1 PDH cross | 187 | 50 | 71 | 12 |
| 1h | long | C2 any | 1,160 | 271 | 306 | 76 |

Unknown-order C4 (same minute, open undecided): 1h short C2 dev 3; 1h long C1 dev 2, C2 dev 4, C2 val 1; none on 4h.
Full tables (with wrong-order C4 and event totals): run `.venv/bin/python -m studies.pdl_swing_4h.run`.

Owner example 2026-11-16 (MYT 07:00/11:00/15:00/19:00 = CT 17:00/21:00/01:00/05:00) after a $0.006 Databento
update: 4h short C1 + C3. SH0 89.64 > PDL 87.80 (13 Nov low); SL 87.59; c3 high 89.49; c4 high 88.50 < 89.49,
c4 low 86.67.

Spot checks on raw 1m bars: 4h long C1/C4 2012-03-08 07:00 UTC (PDH 106.58, SH 107.19, c4 touches c3 low 106.16
at 15:06 then 107.20 at 16:29); Codex: 4h and 1h long C1/C3 and C1/C4 in `codex_counts_v2.txt`, all pass.
