# Tupa Trade (owner strategy, being written down)

Status: **v1 coded and backtested; no demonstrated edge; collecting more owner walkthroughs** (2026-11-05).
Section 3c is coded as `strategies/tupa_trade.py` with the Pine twin `strategies/tupa_trade.pine` (section 3d).
The historical [results report](results.md), generated 4 November, reports a best-of-four in-sample result of
855 trades and **-$13,547.10** after commission, with no added slippage; all four combinations lose.
The earlier independently replicated run recorded in section 6 had 858 trades and **-$14,149.16**;
that historical replication does not verify the newer report. TradingView export parity remains open.
Both reports predate the 5 November swing correction below and are **superseded pending rerun**.
Rules were captured from one owner walkthrough (26 October short). Further walkthroughs will identify
differences between the owner's decisions and the implementation. Anything marked *open* still needs
the owner's answer; section 3d identifies Claude's provisional choices. Local price bars are in `data/cl1/`.

## 1. Core idea

Pure price action. No indicators except the owner swing points (`indicators/structure_swings.pine`).

- Price always travels swing low to swing high, then swing high to swing low.
- So the next swing is always one of two outcomes:

| Last confirmed swing | Next swing must be | Then |
|---|---|---|
| HL (swing low) | swing high: **HH** or **LH** | |
| LL (swing low) | swing high: **HH** or **LH** | |
| HH (swing high) | swing low: **HL** or **LL** | |
| LH (swing high) | swing low: **HL** or **LL** | |

- Equality (owner, 2026-11-02): a swing low exactly equal to the previous swing low is **LL**; mirror, a swing high
  equal to the previous one is **HH**. Same "or equal" as the pivot rule's left candle. No EQH / EQL labels.
- A confirmed swing is not final while it is the newest one: a higher high (or lower low) before the opposite swing
  appears replaces it (indicator rule 2).
- Entries come from reading which branch price is taking *right now* (current price action behaviour). Exact
  entry trigger: *open* (owner has not explained it yet).

## 2. Swing point rule (owner, from the indicator)

- Swing high at candle k: `high[k-1] <= high[k]` and `high[k+1] < high[k]`. Swing low mirror.
- Known when candle k+1 closes (one candle late).
- Two swing highs with no swing low between: the higher stays (equal: the later). Lows mirror.
- Owner clarification (5 November): a local high must also be the highest high since the accepted low,
  counting intervening non-pivot candles; low mirror. Observe same-candle extremes in their existing
  1m order. A smaller later local peak cannot finalize the low. The fixed pivot test still applies.
- Outside candle that is both: added in the order its extremes printed (1m data decides). Both extremes in the same
  1m candle, or no 1m data: open nearer the high = high first; equal distance = low first; no-data case marked `?`.

## 3. Top-down process

Daily -> 4H -> 1H -> 15m -> 5m -> 1m. Trades only in the **New York session** (to cut overtrading).
Exact NY session window in Malaysia time: *open* (see `docs/SESSIONS.md`).

Prices: CL tick 0.01, so always 2 decimals. Daily OHLC from `data/cl1` (CME trading day starts 18:00 ET;
CLZ6 from 19 Oct), matches the owner's TradingView chart.

Owner lives and trades in **Malaysia time (UTC+8, no DST)**. All times in the walkthrough are MYT unless stated.

## 3b. Trade rules (owner, 2026-11-03)

| Item | Rule |
|---|---|
| Entry timeframe | 1m, on a **market structure shift (MSS)**: last confirmed 1m swing low is a HL and price touches it (break point). Mirror for a long. No waiting for 5m/15m confirmation. |
| Order type | **Stop-limit.** Stop (trigger) = the break point, touch counts. Limit = entry price. |
| Stop loss | **Exactly at** the last confirmed 1m swing high (short) / swing low (long). |
| Long side | Mirror: last confirmed 1m swing high is a LH (downtrend) and price touches it = break point, stop at the swing low, buy limit = stop + 25 ticks if the gap is over 25 ticks. |
| Max risk | **25 ticks** ($250 per contract, before $4.02 costs). If stop - break point > 25 ticks, the limit moves toward the stop so that stop - limit = 25 ticks. Otherwise the limit = the break point. |
| Take profit | **25 ticks** from entry (owner: "at least"; no rule yet for larger). |
| Trades | **One per NY session** (until the edge is proven). Open trade **closed at NY session end**. |
| HTF candles | Closed candles only. |
| Downtrend (per timeframe) | The last uptrend HL is touched or broken. |
| Bias | Every timeframe **below the one whose worst case is tested** is in downtrend + 1m flips up to down = short (mirror long). 26 Oct: worst case on 4H/1H (100.60 holds), so 15m and 5m down. How to pick that timeframe: *open* (Q27). |
| Cancel | Limit not filled: cancel when the next 1m swing high is confirmed (mirror: swing low for a long). |

Example (26 Oct): break point 100.76, stop 101.02 = 26 ticks > 25, so sell limit 100.77 (stop - limit = 25 ticks),
triggered once price touches 100.76. If the break point were 100.81, sell limit 100.81.

Backtest note: the engine now supports stop-limit entries (`docs/ENGINE.md`, fills rule 8): trigger at the stop,
then a limit order that fills when the rest of the bar path (or a later bar) touches it. Convention until checked
against a TradingView export of the Pine twin.

## 3c. Draft algorithm (Claude, from answers 4, 10, 18-28; owner to confirm)

All swings from **closed** candles only, per the indicator. Short side shown; long is the mirror.

1. **Tested timeframe T**: the timeframe with a **candidate** swing low (confirmed by the indicator but not real:
   no swing high confirmed after it on T). 26 Oct: **1H** HL 100.63 (owner answer 29). T itself need not be down. Worst case = the
   candidate holds and T builds its swing high.
2. **Bias short** when **every timeframe below T** (down to 5m) is in downtrend: its last uptrend HL has been
   touched or broken. 26 Oct: 15m HL 101.21 broken, 5m HL broken (LL 100.72).
3. **Entry (1m MSS)**: last confirmed 1m swing low is a HL; price touches it. Break point = that HL, stop = last
   confirmed 1m swing high (exactly). Sell limit = break point, or stop - 25 ticks if the gap is over 25 ticks.
4. **Cancel** the unfilled limit when the next 1m swing high is confirmed.
5. **Exit**: TP 25 ticks, SL at the swing high, or close at NY session end. One trade per NY session.

Check on 26 Oct 22:32 (owner answer 29): tested timeframe T = **1H** (candidate HL 100.63, still unbroken at
22:32; 4H candidate 100.60 just below). Below T: 15m HL 101.21 broken, 5m HL 101.21 broken, so bias short; the
1H itself does **not** need to be down. 1m MSS at 100.76 then gives the trade. Draft algorithm reproduces it.

Open points for code: which timeframes count as "T" candidates (daily, 4H, 1H?), what if two timeframes both
have a candidate, and whether T itself must also be checked against the daily bias (answer 9: daily decides).

## 3d. Code (Claude, draft; owner to confirm the marked choices)

Chart helper (owner requested, 5 November): [`indicators/tupa.pine`](../../../indicators/tupa.pine)
combines the existing owner swing display with possible next-swing levels. Auto follows the latest
confirmed chart swing: after a high it marks the previous closed candle low and the latest confirmed
lower-timeframe swing low; after a low it mirrors to highs. Daily automatically uses 4H below it.
Lines default to thin solid white (previous candle) and blue (lower swing); source visibility, colors,
width, labels, lower timeframe and display direction are configurable. These are prospective levels,
not entries or confirmed next swings. It currently shows the latest level from each source.
[Usage and verification limits](../../../indicators/README.md). TradingView compilation is pending;
the research guard refused the scripted source check for insufficient available RAM.

Owner refinement: remove failed level candidates. If candle B raids candle A's low or a lower-timeframe
swing low, B is a possible swing low. Candle C must keep its low strictly above B's low. If C touches
or breaks B's low, remove the old tested level; the previous-candle line then marks B's low. Mirror
for highs. `tupa.pine` tracks this separately from swing detection, with **Remove failed swing
candidates** enabled by default. An invalidated lower-source level remains hidden until a newer
confirmed lower swing is available. Price action before a lower swing was confirmed is excluded
from its touch tracking. Intrabar display invalidation does not confirm an indicator swing or
authorize intrabar HTF structure inputs to the strategy. TradingView verification remains pending.

Further chart refinement: level lines start at their source candle, not their confirmation candle.
The level sources now use a fixed configurable **Reference timeframe** (default Daily, Auto lower
= 4H), independently of the viewing chart. Daily source levels appear on Daily and every smaller
chart; 4H source levels appear on 4H and smaller charts and are hidden on Daily. Reference 4H
similarly uses 4H previous-candle levels and 1H confirmed swings. Candidate invalidation still uses
reference candles on every viewing timeframe. A historical line anchor does not make the level
knowable before its confirmation. No changes to swing detection were made for this refinement.

Files: `strategies/tupa_trade.py` (strategy), `tvtester/swings.py` (owner swings, timeframe candles, trend),
`strategies/tupa_trade.pine` (Pine twin), tests `tests/test_tupa_trade.py` (vectorized code = literal bar-by-bar
transcription of the Pine script, `tests/tupa_literal.py`, on synthetic bars; plus the 26 Oct trade on real bars).

| Item | Coded as | Source |
|---|---|---|
| Swings | Indicator rule, all timeframes, 1m order for outside candles | owner (section 2) |
| Timeframes | 5m, 15m, 1H (clock), 4H from 18:00 New York (last one 14:00-18:00), daily = CME day from 18:00 New York. Bars in the 17:00-18:00 halt (2010 data) stay in the day's last candle | owner charts (4H table); R19 |
| Closed candle | at the close of its last 1m bar if that is the candle's last minute, else when the next bar closes (so the day's last 4H and daily candles close on the 18:00 reopen bar; no trade decision falls between 14:30 and 09:00) | answer 4 |
| Trend | down when the current swing low, labelled HL, is touched (low <= HL) by a closed candle; up when the current LH is touched. Stays until the opposite touch. Both in one candle: the later touch (1m) | answers 21, 28 |
| Tested timeframe T | **lowest** timeframe from `t_min` up to daily whose newest swing is a swing low (short) / high (long) | answer 27; *Claude: "lowest" and `t_min`* |
| Bias | every timeframe below T, down to 5m, in downtrend (long: uptrend) | answers 25, 29 |
| Entry | newest 1m swing is a swing high, the swing low before it is a HL. Sell stop-limit, stop = HL, limit = HL or stop loss - 25 ticks | section 3b, answer 18 |
| Not armed | when that HL was already touched before the order could be placed (MSS already happened) | *Claude* |
| Before trigger | the order follows the setup each 1m close: moved when the levels change, cancelled when the bias or setup goes | *Claude* |
| After trigger | stays until filled or the next 1m swing high is confirmed (long: swing low) | answers 23, 26 |
| Exits | stop loss at the 1m swing high, TP 25 ticks from the fill, close at 14:30 New York (order at the 14:29 close) | answers 19, 20, 24 |
| Session | orders work 09:00-14:29 New York; one filled trade per session | answers 6, 22 |
| Daily bias override (answer 9) | not coded | *open* |

Interpretation study (2026-11-12): the Claude choices above are switches in **Tupa Trade v2**
([`../tupa_trade_v2/`](../tupa_trade_v2/README.md)); v1 is unchanged.

Grid: `t_min` in 15m / 1h / 4h / 1d (which timeframes may be T, open point Q27/29). On 26 Oct, `t_min` = 15m or 1h
gives T = 1H (15m newest swing was the LH 101.92), 4h gives T = 4H, which needs the 1H down too, so no trade.

## 4. Worked example: week of 26-30 Oct 2026

### 26 Oct, Daily (chart: `charts/2026-10-26_daily.png`)

Last daily candle (**Fri 23 Oct**; owner first wrote 25 Oct, corrected 2026-11-02): big bull candle, O 99.10 H 103.92 L 98.84 C 103.44.
Its high is above the last confirmed HH (101.37). That HH and the HL 95.25 sit on the **same outside candle**
(Tue 20 Oct, long-wick doji), so the indicator ordered its high and low by 1m data. It is a **candidate** swing high: not
confirmed yet, because the next candle has not closed.

Owner's two scenarios for the 26 Oct candle:

1. **26 Oct makes a higher high than 23 Oct.** 23 Oct is not a swing high. The up leg from HL 95.25 continues;
   26 Oct becomes the new candidate.
2. **26 Oct does not break the 23 Oct high** (whether or not it breaks the 23 Oct low). When 26 Oct closes, the
   23 Oct high is confirmed as a swing high, labelled **HH** (above 101.37). Per section 1 the next daily swing is
   then a swing low: HL (above 95.25) or LL (at or below 95.25; equal = LL).

Exact split by the indicator (A = 23 Oct candle, B = 26 Oct candle):

| B high vs A high | Result at B close |
|---|---|
| `H_B < H_A` | A confirmed swing high, HH. True even if B also breaks A's low. |
| `H_B = H_A` | A not confirmed (right side must be strictly lower). B is the new candidate. |
| `H_B > H_A` | A not confirmed. B is the new candidate. If B also breaks A's low, B is an outside candle and may later be both a swing high and a swing low; 1m order of its extremes decides which comes first. |

### 26 Oct, 4H (chart: `charts/2026-10-26_4h.png`)

4H candles in MYT (US daylight time, CL session opens 06:00 MYT): 06:00, 10:00, 14:00, 18:00, 22:00, 02:00.
The 02:00 candle is 3 h (session ends 05:00 MYT).

| 4H candle (MYT) | O | H | L | C | Swing |
|---|---|---|---|---|---|
| Fri 23 06:00 | 99.10 | 100.57 | **98.84** | 100.38 | HL (last 4H swing low before the HH), confirmed 14:00 Fri |
| Sat 24 02:00 | 102.84 | **103.92** | 102.83 | 103.44 | HH, confirmed 10:00 Mon 26 (06:00 candle close) |
| Mon 26 06:00 | 102.61 | 102.63 | 101.27 | 101.32 | |
| Mon 26 10:00 | 101.31 | 101.42 | 100.69 | 100.90 | |
| Mon 26 14:00 | 100.90 | 101.72 | **100.60** | 101.32 | candidate HL (owner's "2pm candle") |
| Mon 26 18:00 | 101.32 | 102.19 | 100.63 | 101.81 | low 100.63 > 100.60: confirms 14:00 low at its close, 22:00 |
| Mon 26 22:00 | 101.81 | **103.13** | **100.33** | 101.91 | outside: low first (22:36), high later (00:40). HL 100.33 replaces 100.60, then LH 103.13 |
| Tue 27 02:00 | 101.92 | 102.45 | 101.23 | 101.25 | confirms both 22:00 swings at its close, **05:00** Tue (3 h candle) |

Owner's reading (owner words, condensed):

1. At 21:00 the 18:00 candle is still open; at 22:00 it closes. The 14:00 candle (low 100.60) is then a
   **candidate swing low (HL)**. Indicator view: already confirmed at 22:00, but provisional (replaceable). Above the last swing low 98.84, after HH 103.92.
2. If the candidate is real, price should **respect its low (100.60)** and go make a swing high:
   - **HH**: must break the recent HH 103.92 (exact 103.92 is enough, owner 2026-11-03; same as indicator).
   - **LH**: a swing high below 103.92, made **without raiding 100.60 first**.
3. A candidate is only a candidate. A swing low is only real once a swing high is made after it. Until then
   price can take its low and print a new, real swing low.
4. ~~HTF input~~ answered 2026-11-04: **closed candles only**; a forming candle can change any time.
   then made the LH 103.13 (00:40).
5. So on the lower timeframe (1H) carry **both** cases at once:
   - Case A (first assumption): the 14:00 low holds; price builds the swing high (HH or LH).
   - Case B: the real swing low is still to come; 100.60 gets taken and a lower swing low forms first.

Owner rules from answers (2026-11-03):
- Raid = low **at or below** the candidate low (touch counts). HH = high **at or above** the last HH.
- A lower-timeframe LL does not cancel the long bias while the higher-timeframe swing low (daily 95.25 here) is
  intact: the daily can still form a HL.

- A swing is **real** only when the opposite swing is confirmed on the **same timeframe** (2pm 4H low 100.60
  would be real after a confirmed 4H swing high). Lower-timeframe swings (1H and below) are **bias only**: they
  guide the entry decision, they do not make the higher-timeframe swing real.

Rule this gives (confirmed by owner 2026-11-03): a swing is **confirmed** by the indicator one candle late, but it is **final** only
when the opposite swing is confirmed after it. Before that, the scenario tree stays open.

### 26 Oct, 1H (chart: `charts/2026-10-26_1h.png`)

1H swings on Mon 26 Oct (MYT). Pivots per the indicator; a swing is confirmed when the next 1H candle closes.

| 1H candle | O | H | L | C | Swing | Confirmed |
|---|---|---|---|---|---|---|
| 11:00 | 100.94 | 101.10 | **100.69** | 100.98 | LL | 13:00 |
| 15:00 | 101.25 | **101.72** | 101.15 | 101.55 | LH | 17:00 |
| 16:00 | 101.55 | 101.55 | **100.60** | 101.05 | LL (the 4H 14:00 candle's low) | 18:00 |
| 18:00 | 101.32 | **101.62** | 100.87 | 100.91 | LH | 20:00 |
| 19:00 | 100.91 | 101.37 | **100.63** | 101.08 | HL (above 100.60) | 21:00 |
| 21:00 | 101.26 | **102.19** | 100.96 | 101.81 | HH (above 101.62), owner's "9pm candle" | 23:00 |
| 22:00 | 101.81 | 101.85 | **100.33** | 101.05 | raids 100.60 at 22:36; next 1H swing low | |

(The 14:00 1H low 100.83 is dropped: two swing lows with no swing high between, the lower 100.69 stays.)

Owner's reading:

1. The 9pm 1H candle is the case "b": a 1H swing high. Read it as price **trying to build the 4H swing high**
   that would make the 4H low 100.60 real.
2. If so, the next 1H swing low must **not touch 100.60** (touch counts as raid). Any 1H swing low above 100.60 keeps
   case A alive: HL (above 100.63) or even a 1H LL between 100.60 and 100.63.
3. To see whether that 1H swing low holds, go down to **15m**.

What happened: the 22:00 1H candle took 100.60 (low 100.33 at 22:36) before the 9pm high was even confirmed
(23:00). So case A failed; case B (real low still ahead) played out, as seen on 4H.

Pattern so far (working description of this example, not yet a general rule):
- Higher timeframe gives a candidate swing and the level that must hold (here 4H low 100.60).
- Next timeframe down shows price trying to build the opposite swing (1H swing high 102.19) and the new level
  that must hold (the coming 1H swing low, above 100.60).
- Then step down again (15m) to watch that.

### 26 Oct, 15m (chart: `charts/2026-10-26_15m.png`, snapshot just after the 22:00 15m candle closed)

| 15m candle | O | H | L | C | Swing | Confirmed |
|---|---|---|---|---|---|---|
| 19:45 | 101.18 | 101.37 | **100.63** | 101.08 | outside, high first (19:48, low 19:53): LH 101.37 then **15m LL** 100.63 (same price is the 1H HL) | 20:15 |
| 21:00 | 101.26 | 101.99 | **100.96** | 101.94 | none: pivot low dropped (higher than 100.63, no swing high between). Its low = the 9pm 1H candle's low | |
| 21:15 | 101.94 | **102.19** | 101.45 | 101.56 | HH (owner "9:15pm") | 21:45 |
| 21:30 | 101.55 | 101.73 | **101.21** | 101.44 | HL vs 100.63 (owner "9:30pm") | 22:00 |
| 21:45 | 101.42 | **101.92** | 101.40 | 101.81 | LH (owner "9:45pm") | 22:15 |
| 22:00 | 101.81 | 101.85 | **100.77** | 100.86 | closes 22:15: confirms LH, breaks 100.96 | |
| 22:30 | 100.85 | 100.94 | **100.33** | 100.92 | LL; first trade at/below 100.60 at 22:33, low 100.33 at 22:36 | 23:00 |

Data note: the owner's chart has a 100.76 marker near the 22:00 15m low; our data says 100.77 at 22:10. Unverified
(marker may not be the candle low); either value changes no level here.

Owner's reading:

1. On 15m price just made **HH 9:15pm (102.19) then HL 9:30pm (101.21)**.
2. When the 10pm 15m candle closes (22:15) it confirms **HH - HL - LH (9:45pm, 101.92)**. The same candle also
   **breaks the 9pm 1H candle's low (100.96)**: a 1H swing low may now be forming.
3. The 9:45pm LH is confirmed by the indicator but not final (not real): a later 15m candle (10:15pm or after)
   could still go above it, until a 15m swing low is confirmed after it.
4. Context from 1H: the 9pm 1H candle just broke the previous 1H swing high (101.62, so HH 102.19). The next 1H
   swing is a swing low, HL or LL. (1H levels: HL if above 100.63; the 4H level 100.60 must not be touched for
   case A.)
5. So go one timeframe deeper (5m).

Indicator detail: a new high above 101.92 but below 102.19 replaces the LH and is still LH; at or above 102.19 it
becomes HH.

Levels live at 22:15 MYT: 102.19 (15m HH; 1H HH only provisional, confirmed 23:00), 101.92 (15m LH), 101.21 (15m HL), 100.96 (9pm 1H low, broken),
100.77 (current 15m low), 100.63 (1H HL), **100.60** (4H candidate low).

Owner's conclusion at 22:15 (2026-11-03): the **15m HL 101.21 decides** the setup, and it is broken.

- 4H: must not touch 100.60 to build its swing high.
- 1H: must not touch 100.60 to build its swing high.
- 15m: broke its uptrend structure (HH 102.19 - HL 101.21, then LH 101.92 and price below 101.21). Now forming
  **LH then LL**: the next 15m swing low will be below 101.21.
- Whole picture: the **lower timeframe that decides has turned down**, so the higher-timeframe condition
  ("don't touch 100.60") is now more likely to fail. More chance price reaches **100.60**.

Possible general rule (Claude's reading, owner to confirm): the lowest timeframe that has a broken structure decides the
near-term direction; the higher-timeframe levels are its targets.

### 26 Oct, 5m (chart: `charts/2026-10-26_5m.png`, snapshot about 22:30, after the 22:25 5m candle closed)

Shaded box on the owner chart = the 22:15 15m candle (22:15-22:30).

| 5m candle | O | H | L | C | Swing | Confirmed |
|---|---|---|---|---|---|---|
| 21:55 | 101.66 | **101.92** | 101.64 | 101.81 | LH (= 15m LH) | 22:05 |
| 22:15 | 100.86 | 100.88 | **100.72** | 100.84 | swing low, LL | 22:25 |
| 22:20 | 100.84 | 100.97 | **100.76** | 100.96 | | |
| 22:25 | 100.95 | **101.02** | **100.78** | 100.85 | LH candidate at snapshot (needs 22:30 high < 101.02); confirmed LH | 22:35 |
| 22:30 | 100.85 | 100.92 | **100.50** | 100.53 | touches 100.78 (22:30), 100.76 (22:32), 100.72 and 100.60 (22:33) | |
| 22:35 | 100.52 | 100.73 | **100.33** | 100.58 | LL 100.33 (22:36) | 22:45 |

Owner's reading (at about 22:30):

1. If price is going to make the **4H / 1H HL** (100.60 holds), the **15m must stop making LH-LL**.
2. For the 15m to stop making LH-LL, the **5m must start making HH-HL**.
3. 5m now: last swing low **100.72**, last swing high **101.02** (not confirmed yet, but it can happen).
4. If the 5m next swing low is a **HL** (above 100.72), it will likely come **after raiding the 22:20 low
   (100.76) or the 22:25 low (100.78)**.
5. These levels (100.76 / 100.78 raided, 100.72 holding) decide the high-probability trade. Mark them, then go
   to **1m**.

Chain of conditions (Claude's summary of the notes; not yet an entry rule):

| Timeframe | Needed for the long | Level |
|---|---|---|
| 4H / 1H | HL: low 100.60 not touched | 100.60 |
| 15m | stop making LH-LL | |
| 5m | start making HH-HL: next low stays above 100.72 (owner: it *might* first raid 100.76 / 100.78; raid not stated as required) | 100.72 |
| 1m | entry (next step) | |

What happened: 22:30 touched 100.78, 22:32 took 100.76, 22:33 broke 100.72 and 100.60 in one 1m candle (low 100.50).
The 5m made LL, not HL, so the whole chain failed; the low came at 100.33 (22:36).

### 26 Oct, 1m: the trade (chart: `charts/2026-10-26_1m.png`)

1m structure before the entry (MYT):

| 1m candle | O | H | L | C | Swing |
|---|---|---|---|---|---|
| 22:15 | 100.86 | 100.86 | **100.72** | 100.75 | LL (the 5m low), confirmed 22:17 |
| 22:22 | 100.82 | 100.93 | **100.76** | 100.93 | HL, confirmed 22:24 = **break point** |
| 22:25 | 100.95 | **101.02** | 100.91 | 100.92 | HH, confirmed 22:27 = **stop** |
| 22:30 | 100.85 | **100.92** | 100.78 | 100.84 | local pivot high, **dropped** by alternation (no swing low since 101.02); touches 100.78, the 5m level |
| 22:31 | 100.84 | 100.87 | 100.77 | 100.80 | |
| 22:32 | 100.83 | 100.86 | **100.76** | 100.78 | touches 100.76: **MSS, stop-limit triggers**; closes 100.78 after the low, so passes 100.77 |
| 22:33 | 100.78 | 100.80 | **100.50** | 100.55 | reaches TP 100.52 |
| 22:36 | 100.40 | 100.50 | **100.33** | 100.49 | low of the move |

The trade (owner's rules, our data, 1 contract):

| | Price | Note |
|---|---|---|
| Trigger | 100.76 | touched 22:32 |
| Entry (sell limit) | 100.77 | fills 22:32 (price rose from the 100.76 low to the 100.78 close) |
| Stop | 101.02 | 25 ticks, never reached |
| Target | 100.52 | 25 ticks, reached 22:33 (low 100.50) |
| Result | **+25 ticks** | +$250.00 - $4.02 = **+$245.98** (0 slippage; limit fills never slip) |

Why it was a short (owner): every worst case for the short failed in turn. The 4H/1H needed 100.60 untouched,
the 15m needed to stop LH-LL (it broke HL 101.21 instead), the 5m needed a HL above 100.72 (only 100.78 was
needed for a 5m swing low), and the 1m broke its swing low 100.76.

*Next walkthrough: 2 November 2026 (section 4b).*

## 4b. Continuation: Mon 2 Nov 2026 (awaiting owner charts)

Purpose: compare further owner walkthroughs with v1, including a long, a no-trade day, a losing trade,
and a day whose tested timeframe is not 1H. These categories are still wanted; the outcome and tested
timeframe for 2 November have not been supplied.

- NY window: **2 Nov 22:00 to 3 Nov 03:30 MYT** (09:00-14:30 America/New_York, US winter time).
- Data: the memory's Massive cutoff of 3 Nov 00:30 MYT is historical. The current `data/manifest.json`
  records bars through 3 Nov 18:29 UTC (4 Nov 02:29 MYT), beyond this session's end. No extension appears
  necessary from the manifest; verify the relevant bars when checking each chart.
- Sequence: Daily -> 4H -> 1H -> 15m -> 5m -> 1m, with the owner's chart and notes at each step.
- At each step, record the owner's reading, verify prices to two decimals against local CL data, and add
  Codex's independent review. Respect the chart's analysis cutoff and closed-candle availability; do not
  reveal later price action or the code's later decisions before the owner analyses that part of the day.
- Use only the mandatory owner swing definition. Ask about unclear decisions; mark any inferred rule
  as unconfirmed rather than changing the strategy.
- When the walkthrough reaches the trade decision, compare v1's trade/no-trade, direction, entry,
  stop and target with the owner. Report all four `t_min` settings, since that choice remains unresolved,
  and identify the code/data version used. Distinguish the historical v1 from subsequent lifecycle changes.

No chart analysis, trade outcome or code comparison has been recorded for this day yet.

## 4c. Owner clarification: possible swing locations before confirmation (5 Nov 2026)

This is a separate weekly/daily teaching example supplied while discussing Q27/29, not the 2 November
walkthrough. Six screenshots supplied, filenames `Screenshot 2026-11-05 022858.png`, `023141.png`,
`023234.png`, `023317.png`, `024447.png`, `024521.png` in the owner's Screenshots directory.
The annotations are readable. Prices below are chart readings, not yet independently verified from bars;
the current November candles extend beyond the saved data cutoff. Header OHLC may describe a selected
historical candle rather than the rightmost candle.

Owner's explanation:

- Applies to every timeframe; weekly is used because the current example is clear.
- A possible next swing location can arise from a raid/touch of a previous candle's low/high on the
  same timeframe, or a raid/touch of a swing point on the nearest lower timeframe. Do not wait for
  swing confirmation to consider the location a candidate.
- Images 1-2: highlighted weekly low-to-high leg runs from the 24 August to 14 September weekly
  candles. White weekly levels mark possible locations for the next weekly low. The daily yellow
  swing-low level is another possible location (chart label 82.76). White labels read 93.14, 87.24,
  86.63. Images 3-4 show the subsequent chart state supplied by the owner; no claim of a confirmed
  weekly swing low is inferred from those images.
- Images 5-6: after the 12 October weekly candle closes, the owner considers the 5 October candle
  as a possible swing-low candidate. The weekly red line and daily green lines identify further
  possible swing locations. Owner corrected and confirmed: **5 October** is the possible weekly
  swing low; **12 October** might be the next weekly swing high, labelled **LH or HH**.
- If weekly and daily share the same HL-to-HH swing points, inspect 4H for swing points that could
  locate the next weekly swing low (HL). Also consider previous candle lows on weekly and daily.

Codex review: distinguish an anticipated swing location from a swing already confirmed by the indicator
but still replaceable. Section 3c and v1 currently select T from the newest indicator-confirmed swing;
that does not explicitly represent this anticipatory, cross-timeframe location process. No changes to
the mandatory swing detector are implied or authorized. Weekly is absent from v1's timeframe set.
Whether this explanation changes the closed-candle rule or merely adds prospective scenarios is open.
Still to clarify: which lower-timeframe swings qualify, and how
these possible locations determine the trade's governing timeframe. Historical prices and swing
identities remain pending independent data verification.

### 4 November teaching example: weekly/daily context and replay cutoff

Owner supplied weekly `Screenshot 2026-11-05 030111.png` and daily
`Screenshot 2026-11-05 030342 - Copy.png` / `Screenshot 2026-11-05 030342.png`
(the two daily images show the same annotations).

- Weekly annotation: weekly remains in an uptrend, with HL-HH in formation. Daily price action might
  form the next weekly swing low (HL). This is a possibility, not a confirmed swing.
- White daily levels **99.44**, **95.25**, **88.18** mark possible locations for formation of a
  weekly swing low (HL). Blue **93.59** marks a possible daily swing low (LL). These are the owner's
  chart labels, pending independent parquet verification. A level's weekly role and its daily role
  must be kept separate; no claim that touching a line confirms a swing or requires a trade.
- The owner hid the forming 4 November daily candle using replay. Treat the replay view as the
  information cutoff, setting aside the forming candle already shown in an earlier screenshot.
- Free-account replay is unavailable on the next lower timeframe. Owner will mark the beginning of
  the 4 November candle with a vertical line. Ignore candles to the right when discussing what was
  knowable at that point. Exact line timestamp/session alignment awaits the next chart.

Codex review: the weekly HL scenario can coexist with a possible daily LL. The labels describe
different timeframes. This adds weekly context and prospective levels absent from v1's simple
confirmed-candidate selection, but does not yet resolve how the owner chooses the governing
timeframe or enters a trade. No later price action or trade outcome is inferred here.

### 4 November teaching example: 4H scenarios before NY open

Owner supplied `Screenshot 2026-11-05 033318.png`, followed by the clearer annotation in
`Screenshot 2026-11-05 033350.png`.

- The arrow identifies the **19:00 MYT 4H candle**. At NY open (22:00 MYT) it has not closed;
  owner says to treat it as nonexistent for this 4H reading. Do not use its eventual OHLC or any
  later candles visible in the screenshot to decide the setup.
- Blue line **94.60** is at the preceding 15:00 candle's low on the chart. White **93.59** is the
  previous daily low. Owner considers several prospective paths: break blue while holding white,
  break white, or hold both. These are scenarios, not confirmed swing points.
- Owner's annotation says to seek long confirmation on lower timeframes for a hold of blue/white,
  or aim for a short if price continues. Exact lower-timeframe confirmation and selection between
  the branches have not been explained yet. The trailing text "or maybe 7pm" is unfinished.

Independent OHLC check (pandas directly from 2026 parquet; no strategy/swing imports, run through
`tools/run_limited.py`): previous daily candle O **96.30**, H **98.82**, L **93.59**, C **96.76**,
matching the earlier replay chart (four differences **0.00**). The 4 November 15:00 candle's available
portion through 18:54 MYT has low **94.60**, matching the blue label so far. Minutes 18:55-18:59
are not in the saved data, so its completed low remains unverified. No 19:00-or-later bars were read.

Codex review: the owner explicitly excludes the unclosed 4H candle while considering hypothetical
future touches of existing levels. This supports separating closed-candle inputs from prospective
scenarios; it does not authorize using forming HTF OHLC as confirmed structure. No entry decision
or code trade comparison is established yet.

### Owner flags the 1H indicator sequence (5 November, clarification pending)

Screenshot `Screenshot 2026-11-05 033900.png` annotates the low near 4 November 18:00:
"This is not LL because there is no LH after it. LH should be the highest swing point price after LL."
Owner requests an indicator fix. Exact intended validity condition for that LH is not yet established.
Do not assume this authorizes an alternative pivot algorithm or a new tunable setting.

Source inspection: `Zig.push` in the Pine indicator accepts an opposite-type pivot without comparing
its price to the preceding opposite swing's price. Same-type pivots use extreme replacement.
The detector uses the fixed neighbouring-candle rule and orders dual pivots by 1m extremes.
This source observation alone does not establish the cause of the marked sequence. In particular,
the screenshot's later labels require bars beyond the saved 18:54 MYT cutoff. No numerical
replication of the disputed sequence or indicator change has been made.

Owner clarification: **both** conditions apply. The LH must be the highest candle high between
that low and the next lower low, and that high must satisfy the existing fixed swing rule.
Do not substitute an arbitrary candle high for an indicator swing. Application to the marked
sequence remains pending bar-level verification; the clarification alone does not prove which
displayed pivot is invalid or resolve provisional versus final LL presentation.

Implementation (5 November, owner authorized): Pine indicator, Python twin, both active strategy
Pine copies and Tupa's literal Pine transcription now observe every intervening candle's extremes.
A local high below the highest price since the accepted low is rejected (low mirror). Accepting or
replacing a low resets the high boundary at that low, and conversely for highs. Same-candle order
is preserved, so extremes before the new swing do not leak into its next leg. Processing remains
causal at the right candle close; there is no scan ahead to the eventual next low. Rule identity is
`structure-swings-v2-leg-extremes`; earlier results are superseded pending rerun.

Verification: five focused checks passed by direct function invocation through the research guard
(pytest not run): non-pivot high blocks smaller local peak, mirrored low case, equal/later high,
outside-candle boundary reset, and prefix causality. Python and the literal Pine transcription agree
on 15,746 real CL minute bars (20 October through 4 November before 19:00 MYT), for 1m and all five
higher timeframes, including trend and carried levels. This is Python transcription parity, not a
TradingView compilation or execution check. Massive refresh reaches only 4 November 19:48 MYT;
the exact later marked LH in the screenshot remains unavailable for real-bar reproduction.

### 4 November teaching example: 1H attempted turn, then lower-timeframe failure

Owner supplied `Screenshot 2026-11-05 035714.png` after updating the indicator.
The disputed intermediate low/high pair is no longer visible in this chart; exact real-bar
reproduction remains pending the missing late-evening data.

- Arrow marks the **22:00 MYT 1H candle**. Owner clarified that the **completed 23:00 1H candle**
  raids the 22:00 candle's low, so the 22:00 candle fails as a candidate swing low. This is known
  at **00:00 MYT on 5 November**, not at the beginning of 23:00. The earlier wording is superseded.
- For the **19:00 4H candle** to qualify as a swing low, its right neighbour, the **23:00 4H candle**,
  must not raid/touch its low: the right candle's low must be strictly higher. That 4H right-candle
  confirmation is available at **03:00 MYT on 5 November**. The left-side and other mandatory swing
  conditions still apply. Raiding the 22:00 1H low and raiding the 19:00 4H low are distinct events;
  do not infer the second solely from the first.
- Upper white levels **96.87** and **96.44** are described as possible levels for the 4H candle
  to make a swing point. Exact swing-high/low role and whether either level suffices remain open.
- White **93.59** carries the previous daily low. Owner also marks the 4H candle low, chart label
  **91.67**, as another possible place for a short. The timestamp at which this 4H low becomes
  available must be respected; it is not automatically known at the 22:00 session open.
- Next step: examine a still lower timeframe for the **failed uptrend**. This is not yet an
  entry instruction or a claim that merely touching one of the white lines gives a trade.

Codex review: candidate formation, failure, and entry remain separate stages. The 22:00 1H candle
closes at 23:00; its right neighbour closes at 00:00, establishing the failure described by the owner.
The 4H candidate has a separate 03:00 confirmation boundary. Prospective analysis can precede these
closes but must not borrow their completed OHLC. All new late-evening prices above are chart readings pending parquet checks.
Ignore the later fall visible on the right when evaluating this decision point.

### 4 November teaching example: 15m rebound candidates

Owner supplied `Screenshot 2026-11-05 040235.png` and explains that 15m tries to make a swing
high before continuing back. The owner examines each possible case at **22:15, 22:30 and 22:45 MYT**.
These are prospective swing-high formation cases, not a requirement to wait for the final indicator
label visible later in the screenshot. Evaluate each case using only information available then.

The chart marks a low near 22:00 with an arrow and carries upper white levels 96.87 / 96.44 and
the 4H low 91.67. Three short white levels near the rebound are labelled **93.50, 93.47, 93.44**.
Owner confirmed the respective mapping: **22:15 low 93.50**, **22:30 low 93.47**, **22:45 low 93.44**.
Each is a low watched for a raid to signal possible swing-high formation for that candle.
These remain chart readings, not parquet-verified prices. A raid is a prospective formation signal,
not a substitute for the indicator's right-candle-close confirmation. Do not infer entry, stop,
target or a requirement to raid all three levels.

Codex review: this describes evaluating successive possible turns during the rebound, consistent
with the anticipatory process missing from v1's confirmed-candidate selection. The later swing
label and decline cannot be borrowed to select a successful setup retrospectively. Exact candidate
checks and the next lower-timeframe entry analysis remain to be supplied.

## 5. Open questions for the owner

1. ~~Daily candle date~~ answered 2026-11-02: the last daily candle is Fri 23 Oct.
2. ~~Entry trigger~~ answered 2026-11-03: see section 3b (1m market structure shift, stop-limit).
3. ~~Stop / target~~ answered 2026-11-03: see section 3b.
4. Higher timeframe input: closed candles only, or the still-forming candle too?
5. How do the higher timeframes filter the lower ones? Merged into question 25.
6. ~~NY window~~ confirmed 2026-11-04 (repo default, `docs/SESSIONS.md`): **09:00-14:30 New
   York** = 21:00-02:30 MYT in US summer time, 22:00-03:30 MYT in US winter time (from 2 Nov 2026).
7. ~~Equal swings~~ answered 2026-11-02: equal low = LL, equal high = HH.
8. ~~Raid~~ answered 2026-11-03: an exact touch counts. Low <= 100.60 raids the candidate (same as indicator).
9. ~~4H LL kills long?~~ answered 2026-11-03: no. A 4H LL (<= 98.84) does not end the long idea while the
   **daily** can still print a HL, i.e. price stays above the daily swing low 95.25. The higher timeframe decides.
10. ~~"Swing high is made"~~ answered 2026-11-03: a swing is **real** on a timeframe only when the opposite swing
    is confirmed on the **same** timeframe (4H low real after a confirmed 4H swing high). A lower-timeframe (1H)
    swing high is not proof; it is used only as a working bias to time the long/short entry on lower timeframes.
11. When do you step down from 1H to 15m: during the 9pm candle, at its close (22:00), or after the indicator
    confirms it (23:00)?
12. On 15m, which level matters: the 4H low 100.60, the forming 1H swing low, or both?
13. ~~15m entry event~~ answered via 17/18: entry is on the 1m MSS, not on 15m.
14. ~~Governing level at 22:15~~ answered 2026-11-03: the **15m HL 101.21**. It is broken, so the 15m uptrend
    structure is broken (see 15m section).
15. ~~Short or long?~~ answered 2026-11-03: the plan is a **short**. The long chain (4H/1H HL, 15m stops LH-LL,
    5m HH-HL) is the **worst case** the owner always imagines. Each time price breaks the worst case, the bias
    (short) gets more likely right.
16. ~~5m raid~~ answered 2026-11-03: only **100.78** matters, and it is the pivot rule, not a guess. 100.78 is the
    22:25 candle's low, the left neighbour of the 22:30 candle; for the 22:30 candle to become a 5m swing low its
    low must be **at or below 100.78** (touch counts).
17. ~~Wait for 5m confirmation?~~ answered 2026-11-03: no. Entry comes on the **1m market structure shift**,
    before any 5m confirmation; waiting for 5m is too late because the target range is small.
18. ~~MSS definition~~ answered 2026-11-04: yes. Short MSS = the last confirmed 1m swing low is a **HL** (uptrend)
    and price **touches** it; break point = that HL, stop = the last confirmed 1m swing high. Also when the last
    high is already a LH (HL-HH-HL-**LH**, then price touches the HL = LL): still a break point.
19. ~~Stop placement~~ answered 2026-11-04: exactly at the swing high (101.02).
20. TP above 25 ticks: **no rule yet** (owner 2026-11-04). Use 25 ticks for now.
21. ~~Bias~~ answered 2026-11-04: higher timeframes in **downtrend structure**, then the 1m changes from uptrend
    to downtrend = high-probability short. Mirror for longs. (Which timeframes count: see question 25.)
22. ~~Trades per session~~ answered 2026-11-04: **one** per NY session for now; more only once the edge is proven.
23. ~~Order arming~~ answered 2026-11-04: the stop-limit acts at the **touch of the break point** (100.76); the
    limit order is live from that touch. Cancel rule if the limit never fills: open (question 26).
24. ~~Session end~~ answered 2026-11-04: **close** any open trade at the end of the NY session.
25. ~~Which timeframes must be down~~ answered 2026-11-04: **every timeframe below the one whose worst case is
    being tested.** 26 Oct: the 4H/1H worst case was "100.60 holds", so 15m and 5m must be in downtrend.
26. ~~Unfilled limit~~ answered 2026-11-04: cancel when the **next 1m swing high is confirmed** before a fill.
27. ~~Picking the tested timeframe~~ answered 2026-11-04: the timeframe with a **candidate** swing. The candidate
    creates the bias: if it is valid price should do X, if not it should do Y; all timeframes must align from
    higher to lower. (Draft algorithm: section 3c.)
28. ~~Downtrend structure~~ answered 2026-11-04: **(a) the last uptrend HL is broken** (touch counts), like the
    15m HL 101.21. Mirror: uptrend = the last downtrend LH is broken.
29. ~~1H must be down too?~~ answered 2026-11-04: **no**. At 22:32 the 1H was still up (HL 100.63 broken only at
    22:33); only 15m and 5m had to be down. So on 26 Oct the tested timeframe is **1H** (candidate HL 100.63; the
    4H candidate 100.60 sits just below it). How T is picked in general: watch it in the 27-30 Oct examples.

## 6. Codex discussion log

- 2026-11-01, daily step: Codex review (read-only). Agreed chart reading (high ~103.9, low ~98.9, close ~103.44;
  102.95 is a separate axis marker, not the close). Added: EQH/EQL case, newest swing can still be replaced,
  outside-candle branch of the 26 Oct split, outside ordering fallbacks, sharper date question. Codex top open
  items: entry trigger, closed vs forming HTF candles, timeframe conflict rule, stop/target, NY window with DST.
- 2026-11-02: owner fixed the indicator labels: equal swing high = HH, equal swing low = LL (no EQH / EQL). The
  EQH/EQL note from the 2026-11-01 review is superseded. Pivot rule itself unchanged (left `<=`, right strict `<`).
- 2026-11-03, 4H step: Codex replicated all 4H OHLC rows from the parquet (32/32, diff 0.00) and the swing
  sequence. Fixed: Tue 02:00 candle ends 05:00 MYT (confirmation time), "candidate" vs indicator-confirmed
  wording, exact-103.92 HH note. New owner questions 8-10.
- 2026-11-03, 1H step: Codex replicated the 1H swing sequence and confirmation times (incl. the dropped 100.83 low).
  Fixed: next 1H low only has to stay above 100.60 (a 1H LL between 100.60 and 100.63 also keeps case A);
  "pattern so far" marked as a working description. New questions 11-13.
- 2026-11-03, 15m step: Codex replicated 7/7 15m rows (28/28 values, diff 0.00) and every swing, drop and
  confirmation time. Fixed: 19:45 low is a 15m LL, 1H HH 102.19 provisional at 22:15, raid of 100.60 first at
  22:33, 100.76 vs 100.77 unverified, LH replacement detail. New question 14.
- 2026-11-03, 5m step: Codex replicated 24/24 5m values (diff 0.00), 1m event times and all swing confirmations.
  Fixed: raid is a possibility, not a requirement; 100.78 first touched 22:30; both 5m highs labelled LH; chain
  table marked as summary. New questions 16-17.
- 2026-11-03, 1m trade: Codex replicated 32/32 1m values and the trade independently: fill 100.77 at 22:32, TP
  100.52 at 22:33, +$245.98 net, difference $0.00, no intrabar-path ambiguity. Fixed: 22:30 high is dropped by
  alternation (not a swing). Codex: section 3b fits this example but is not yet codeable; needs order arming /
  cancel time, MSS swing choice, deterministic TP, NY window, trades per day, session-end exit (questions 18-24).
- 2026-11-03, [R19](../../REVIEWS.md): old log 195 passed, SHA-256 `079711c5c3a91c469ca70046835c812e1988acfb8f384ad38a63633bc151b84a` verified; prior review found no engine fill, swing, candle-boundary or Python order defects.
  High fixed: Pine line 300 now guards `curDay` with `na()`; no other affected Pine comparison. Literal na semantics, static guard and multi-session regressions: old one trade, fixed four, matching Python in synthetic and October 2026 CL windows.
  New log `logs/pytest_tupa_r19.log`: 203 passed, SHA-256 `d0878544c2ac88fe8a3d74a4000d90fd3884b7930cff2f50a67a4cc7019dc87b` verified. Python strategy / engine unchanged.
  Own code on all 5,672,666 bars: 26 Oct short 22:32 MYT @ 100.77, exit 22:33 @ 100.52, +245.98; top ny / 1d / TP 25 / max risk 25: 858 trades, net -14,149.16 / -20,179.16 / -26,209.16 at 0/1/2 ticks, all differences 0.
  In-sample, best of 4, a loss; internal consistency, not TV parity (export still needed). Additional High: historical bars in the assumed halt produce eight literal vs two Python trades over 7 June-9 July 2010; separate candle-grouping fix needed (R19).

- 2026-11-03, rerun at `890e02b` ([R19](../../REVIEWS.md)): 211 tests passed; all four combinations match every trade field over all 5,672,666 bars; no swing-state or bias divergence, including historical halt-hour bars.
  Top NY / 1d / TP 25 / max risk 25 unchanged: 858 trades; net -14,149.16 / -20,179.16 / -26,209.16 USD at 0/1/2 ticks. All four grid nets unchanged.
  Independent in-memory replication (no project imports): 858 trades at each slippage level, all net differences 0.00 USD. Internal consistency, not TradingView parity.
  Low documentation caveat: a present 17:59 ET bar closes the day's last 4H/daily candle on that bar (2018-08-05); the reopen-bar wording needs qualification. Source left unchanged.
