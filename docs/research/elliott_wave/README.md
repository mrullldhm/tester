# Elliott Wave: research and loss study (12 November 2026)

Purpose: understand Elliott Wave (EW) deeply enough to build a testable, mechanical intraday version, and
learn from the losing trades of the first version ([`docs/strategies/elliott_wave/`](../../strategies/elliott_wave/)).
Loss study uses the development interval only (2010-06 to 2023-12); 2024+ stays reserved.

Source tags: **[V]** checked online, **[B]** from the book (check the chapter before coding), **[?]** uncertain.
Research was gathered by web search and summarised; quotes are not verbatim.

## 1. What the theory says

### Schools
| School | How waves are found | Objectivity claim | Entry style |
|---|---|---|---|
| Frost & Prechter, *Elliott Wave Principle* (EWP) | Price structure, by eye, by degree | None: rules + guidelines + "right look" | None defined |
| Neely, NEoWave, *Mastering Elliott Wave* (1990) | Monowaves, measured retracement rules 1-7, similarity 1/3 rule | High: structure from measured ratios | None defined |
| Bill Williams, *Trading Chaos* | AO 5/34 peaks (tallest in 100-140 bars = wave 3) | High, but orthodox EW rejects oscillator counts | **Stop orders** on confirmation (fractal, AO saucer, divergent bar) |
| Tom Joseph, Advanced GET | Elliott Oscillator 5/35 + price count | High (vendor) | Type 1: limit inside wave 4 **with filters**; Type 2: breakout at wave-5 end |
| iTradeAIMS book (owner's PDF) | Williams' AO method | High | Breakout of a tight range ("Setup One", paywalled) |
| markokrivokapic.com | Orthodox EWP + Fibonacci | None | None defined |

### Hard rules (all orthodox schools) [B]
- Wave 2 never retraces more than 100 % of wave 1.
- Wave 3 is never the shortest of 1, 3, 5.
- Wave 4 never enters wave 1's price territory (exception: diagonals; EWP also allows rare brief overlap in
  leveraged futures intraday).
- Motive waves subdivide 5-3-5-3-5; zigzag 5-3-5; flat 3-3-5; triangle 3-3-3-3-3, only as wave 4 / B / X / last.

### Guidelines (tendencies, not rules) [B]
- Alternation: sharp wave 2 implies sideways wave 4, and vice versa.
- Wave 4 usually ends in the range of sub-wave 4 of wave 3; usually 0.236-0.382 of an extended wave 3.
- One wave extends. In **commodities, fifth-wave extensions are common** (EWP commodities chapter).
- Wave 5 = wave 1, or 0.618 x (start of 1 to end of 3); truncation after a very strong wave 3.
- Neely (stricter): one of 1/3/5 must be >= 1.618 x the next longest; adjacent waves are the same degree only
  if each is >= 1/3 of the other in price or time; post-pattern time confirmation (the 2-4 line must break
  within the time wave 5 took).

### Advanced GET Type 1 (the closest relative of our version) [V, eSignal help]
- Oscillator pulls back at least 90 % of its wave-3 peak (or to zero) **and no more than 1.40 x** the peak.
- PTI > 35 (proprietary wave-4 vs wave-3 momentum ratio). Below 35, wave 5 often fails.
- Entry at a Fibonacci level (e.g. 0.382), stop two levels below (below 0.618). Take only if reward / risk > 1.5.

Our version is Type 1 **without** the 1.40 rule, without PTI and without the reward / risk gate.

## 2. What the evidence says

| Claim | Evidence | Verdict |
|---|---|---|
| Mechanical EW count is profitable out of sample after costs | No peer-reviewed study found (WASP 2011, neural classifiers: accuracy only, no costs) | **Unsupported** |
| Swing ratios cluster at Fibonacci numbers | Batchelor & Ramyar 2006 (DJIA, bootstrap): no more than chance | **Rejected** (daily data) |
| Price reacts at watched levels more than at random levels | Osler 2000 (FX intraday, published levels vs 10,000 random sets): yes | Supported, but for published / round levels, not Fibonacci |
| AO / Williams indicators | No peer-reviewed test. MA-type rules on 15 commodity futures die after snooping correction (Marshall, Cahan & Cahan 2008) | **Unsupported** |
| Intraday continuation after a pullback in futures | Safari & Schmidhuber 2025 (16 futures incl. crude, 1-minute, 2010-2023): **trends revert below ~30 minutes**, persist above ~1 hour | **Against our degree** |
| Intraday momentum in crude | First half-hour predicts last half-hour (Wen et al. 2021, 2023; Baltussen et al. 2021); EIA window | Time-of-day effects, not structure |
| Opening range breakout on CL | Holmberg et al. 2013: positive, bootstrap-significant (older sample) | Breakout, not pullback |

Full citations are in section 6.

## 3. What our losing trades say (development interval, class-default settings)

Settings: window 120, entry 0.382, stop 0.618, target 0.618, min length 20 (chosen before any result).
3,270 trades in three sessions: **29.7 % winners, -$35,225**. Stops: 2,179 (67 %).

| Finding | Number | Reading |
|---|---|---|
| Best move before a stop | median 0.12 L; only 22 % reach 0.25 L | Losers barely bounce: the pullback simply continues |
| Stop hit within 5 bars of the fill | 25 % of stops | Knife-catching |
| Stopped trades that later hit the target the same session | 23 % | Mostly wrong direction, not a stop that was too tight |
| Wider stop (0.786) | 39.6 % winners but -$42,785 | Wider stop does not fix it |
| Fill within 2 bars of the signal | 25.5 % winners (1,819 trades) vs 34-44 % for slower fills | Adverse selection: fast fills = momentum against us |
| Price already past the 0.382 level at the signal (limit at the close) | 21.6 % vs 34.2 % winners | Late, deep entries lose most |
| First hour of the session | 24 % winners vs 37 % after 4 hours | Opening volatility breaks the pattern |
| Higher-timeframe owner trend aligned (15m) | 30.5 % vs 26.6 % | Small effect |

**Is the count better than chance?** For every signal (4,005), from the signal close: does price make a new
wave-3 extreme (a real wave 5) before the stop level?

| Stop | Random-walk expectation | Actual |
|---|---|---|
| 0.618 | 49.3 % | **46.3 %** |
| 0.786 | 55.8 % | **53.6 %** |

The random-walk expectation is distance-to-stop / (distance-to-top + distance-to-stop) from the same close.
The count is slightly **worse than a coin flip**. When the stop level is hit first, 44 % of the time price then
retraces the whole "wave 3": that leg was not a wave 3 of an impulse at all.

## 4. Why the losers lose (theory + evidence + data agree)

1. **Wrong degree.** AO 5/34 on 1m measures ~30-minute swings, inside the documented mean-reversion regime
   (< 30 min). The theory's wave 4 to 5 continuation needs the trending regime (> 1 hour).
2. **Entering at the start of wave 4, not its end.** The AO zero cross marks the beginning / depth of wave 4.
   Williams and Joseph Type 2 both wait for confirmation and use stop orders.
3. **Limit fills select the wrong counts.** Real fourth waves usually end at 0.236-0.382 of an extended wave 3
   and often do not reach our limit; the fills come disproportionately from pullbacks that keep going.
4. **No wave 1, so no hard rule is checked.** The 0.5-0.786 levels are usually inside wave 1's territory
   unless wave 3 >= ~2-2.6 x wave 1; a stop there is not at an EW invalidation.
5. **Fifth-extension trap (commodities).** The tallest AO peak can be wave 5; our "wave 4" is then the start
   of the whole correction.
6. **No filter for complex or deep fourth waves** (GET 1.40 rule, PTI, alternation, Neely 1/3 similarity).

## 5. Testable hypotheses

**Run 12 November 2026: 0 of 15 pass** (5 hypotheses x 1m / 5m / 15m, pre-registered). Results and reading:
[`docs/strategies/elliott_wave/optimize/README.md`](../../strategies/elliott_wave/optimize/README.md).

Ranked by theory support and fit with our constraints (limit entries, fixed owner swings, intraday, flat).

| # | Hypothesis | Change | Falsified if |
|---|---|---|---|
| H1 | **Higher degree.** The count works where the trend regime starts | Same rules on closed 5m / 15m candles (AO on that timeframe, owner swings on that timeframe), entries on 1m | Top-first rate still <= random walk on 5m and 15m |
| H2 | **GET Type 1 complete.** Filters remove fake wave 4s | Add 1.40 oscillator rule, PTI proxy (wave-4 AO area / wave-3 AO area), reward / risk >= 1.5 | Top-first rate with filters <= random walk |
| H3 | **Find wave 1, enforce hard rules.** | Wave 1 = the owner-swing leg before wave 3; entry above wave 1's top, stop at wave 1's top; W3 >= 1.618 W1 (Neely extension) | Same |
| H4 | **Confirmation, then limit.** Enter after wave 4 has ended | Arm only after AO turns back (Williams saucer / zero recross); limit at that close (like FPR) | Same, or loses after costs |
| H5 | **Wave-3 from wave 2 ("1-2 setup").** Stop at the strongest invalidation (wave-1 origin) | Limit at 0.618 of wave 1 after wave 1 breaks the prior owner swing | Same |

First test for every hypothesis is the cheap one: **top-first rate vs the random-walk expectation**, no P&L,
no optimisation. Only hypotheses that beat chance on the development interval get a strategy run, and only
that run counts as a trial in the ledger. Expectations: the literature finds no EW edge anywhere; a small
filter effect is the realistic best case.

## 6. Sources

Theory: Frost & Prechter, *Elliott Wave Principle* (Ch. 1, 2, 4, commodities chapter) [B]; Neely, *Mastering
Elliott Wave* (Ch. 3-5) [B]; Williams, *Trading Chaos* (1995 / 2004), *New Trading Dimensions* (1998) [B];
C. Brown, *Mastering Elliott Wave Principle* (2012) [B]; Advanced GET Type I / II / PTI, eSignal help:
https://scanner.esignal.com/help/type_i_buy.html , https://scanner.esignal.com/help/type_ii_buy.html [V];
iTradeAIMS, *10 Seconds Elliott Wave*, 2nd ed. (2023, owner's PDF); markokrivokapic.com (31 articles, owner's list).

Evidence: Batchelor & Ramyar (2006) "Magic numbers in the Dow", https://openaccess.city.ac.uk/id/eprint/16276/ ;
Osler (2000) FRBNY EPR 6(2), https://www.newyorkfed.org/research/epr/00v06n2/0007osle ; Marshall, Cahan & Cahan
(2008) J. Banking & Finance 32 ; Safari & Schmidhuber (2025) Physica A 675, arXiv 2501.16772 ; Wen, Gong, Ma &
Xu (2021) Economic Modelling 95 ; Wen, Indriawan, Lien & Xu (2023) Energy Journal 44(5) ; Baltussen, Da, Lammers
& Martens (2021) J. Financial Economics 142 ; Holmberg, Lönnbark & Lundström (2013) Finance Research Letters 10(1) ;
Atsalakis et al. (2011) Expert Systems with Applications 38(8) ; Bajgrowicz & Scaillet (2012) JFE.

Practice: Elliott Wave Rule Engine, https://www.tradingview.com/script/pU115xkA-Elliott-Wave-Rule-Engine ;
LuxAlgo Elliott Wave and NeoWave Logic, https://www.luxalgo.com/library/indicator/neowave-logic.md ; Martynyuk,
MQL5 article 260, https://www.mql5.com/en/articles/260 ; Trendoscope recursive zigzag,
https://www.tradingview.com/script/nBHR6svi-rzigzag/ ; taew, https://pypi.org/project/taew/ .
