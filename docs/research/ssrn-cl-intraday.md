# SSRN intraday CL strategy survey (2026-10-31)

Claude + Codex literature sweep for published **intraday** trading rules on NYMEX WTI crude oil (CL), then a quick
screen of every explicit rule on our own CL 1m data (`data/cl1`, 2010-06 .. 2026-10).

**Access note.** ssrn.com and papers.ssrn.com return HTTP 403 (bot block) to the browser, curl and fetch tools.
Papers were found through web search on SSRN ids, then read from open mirrors (journal open access, university
repositories). Every paper below has its SSRN id or source link; rules marked *verified* were read in full text.

## Screen method (not TV-exact)
`tools/ssrn_screen.py`. Clock times are America/New_York. A trade at clock time T fills at the open of the first
1m bar at or after T (= market order sent on the bar before, TV default). 1 contract, $4.02 round trip, slippage
scenarios 1 and 2 ticks per side ($20 / $40 per round trip). No trade if the signal and the trade use different
contracts (roll). "EIA day" = Wednesday with 10:30 bar volume > 3x the 10:29 bar (671 days). t = mean/sd*sqrt(n)
of per-trade net $. All in-sample, no parameter fitting except the ORB range length and the jump grid.
Full output: hashed log in the session (sha256 f28cc91c...46d).

## A. Explicit tradable intraday rules tested on crude oil

| # | Paper (SSRN) | Instrument in paper | Rule | Paper result | Our CL 2010-26 screen, net $ (t) |
|---|---|---|---|---|---|
| 1 | Wen, Gong, Ma, Xu, *Intraday momentum and return predictability: evidence from the crude oil market*, Economic Modelling 2020 (SSRN 3553682; earlier 3416022) | USO ETF 1m, 2006-2018, 9:30-16:00 ET | Sign of first half-hour return (prev 16:00 close -> 10:00) -> long/short 15:30, flat 16:00 | Significant in and out of sample; gross, no costs | USO clock: **-$18,865 (t -1.91)**; CL pit clock (prev 14:30 -> 9:30, trade 14:00-14:30): -$11,361 (-0.51) |
| 2 | Wen, Indriawan, Lien, Xu, *Intraday return predictability in the crude oil market: the role of EIA inventory announcements*, Energy Journal 44(5) 2023 (SSRN 3822093) *verified* | USO ETF 1m, 2006-04 .. 2019-07, 591 Wednesday EIA days | Non-EIA days: sign of r1 (or of overnight part) -> trade last half hour. EIA Wednesdays: sign of 10:30-11:00 return -> long/short 15:30, flat 16:00 | 1.88% / 2.39% / 4.14% per year gross, no costs, t 2.10 / 2.45 / 1.88 | EIA r3 -> 15:30-16:00: **-$6,029 (-1.66)**; -> 14:00-14:30: -$4,239 (-0.44); our variant hold 11:00-14:30: +$25,601 (1.04). Overnight sign, non-EIA: -$10,073 (-1.13) |
| 3 | Baltussen, Da, Lammers, Martens, *Hedging demand and market intraday momentum*, JFE 142 (2021) 377-403 (SSRN 3760365 per Codex) *verified, full text* | 60+ futures incl. **CL 1987-2020, 9:00-14:30** | Sign of rest-of-day return (prev close -> 14:00) -> long/short 14:00, flat 14:30 | Commodity basket SR 1.42 gross. **CL alone (Table B3): ROD beta 0.67, t 0.25, OOS R2 -1.04%; ONFH beta 2.00, t 0.72** | **+$13,615 (t 0.61)**, 2018-26 -$11,020; 1 tick -$63,725 |
| 4 | Holmberg, Lönnbark, Lundström, *Assessing the profitability of intraday opening range breakout strategies*, Umeå Econ. Studies 845 (2012; later journal version not confirmed) | CL futures (keywords) | Breakout of opening range, enter on threshold, hold intraday | Returns > 0, success rate > fair game | 9:00 ET open, stop entry, stop at other side, flat 14:30: 5m range **+$89,014 (t 1.90)** but 2010-17 -$895, 1 tick +$4,754, 2 ticks -$79,506. 30m: +$53,258 (1.00) |
| 5 | Ficura, *Profitability of trading in the direction of asset price jumps* (2017, SSRN 2903629) | CL futures 1987-2015, 1m..1d | Return / rolling sd > z -> enter in jump direction next bar, hold k bars | Journal version (Prague Econ. Papers 2019, Table 6), OOS 1 contract after 1 tick + $2.20: 1m -$35,882, 5m -$3,734, 15m -$37,192, 30m +$127, 1h -$13,354 | 5m, 27 combos: best (lb 256, z 2.58, hold 16) +$395,967 at 0 ticks over 33,359 trades, avg $11.9: **1 tick -$271,213**. Dead after slippage |
| 6 | Geman, Li, *An analysis of intraday market response to crude oil inventory shocks*, J. Energy Markets (risk.net 5728636) | WTI futures intraday | Reaction to EIA shock lasts ~25 min, fast reversion; momentum trade around release | Abstract only (paywall) | Follow 10:30-10:35 sign, hold to 10:55: -$10,558 (-1.00); fade: +$2,382 (0.23) |
| 7 | Liu, Liu, Wang, Zhou, Zhu, *Overnight-intraday reversal everywhere* (SSRN 2730304); Della Corte, Kosowski, Wang | Cross-section of futures incl. commodities | Buy overnight losers / sell overnight winners, hold the day session | High SR cross-sectionally | Single-asset CL version, fade prev 14:30 -> 9:00, trade 9:00-14:30: -$65,925 (-0.91); follow: +$34,875 (0.48), 2018-26 -$49,828 |
| 8 | Fetna, *Opening-range breakout does not survive trading costs: a pre-registered 225-cell study on sixteen years of futures data* (2026, SSRN 7428398) | CL 1m continuous, 2010-06 .. 2026-08, 1 contract | 5/15/30/60m range after 09:00 ET or 18:00 ET; first close outside range, fill next open; exits: opposite-side stop + 10R, or 10% ATR stop, or half-range target; flat 14:30 | CL 18/25 configs profitable gross, **1/25 at $25 round trip** | Matches our ORB row: 5m +$4,754 at 1 tick (~$24 RT) |
| 9 | Alturki, Kurov, *Market inefficiencies surrounding energy announcements*, J. Futures Markets 2022 (SSRN 3747330) | WTI front futures, 2011-01 .. 2019-08, 385 EIA events | Sign of (API reported change - Bloomberg EIA consensus): positive short, negative long; enter EIA-60 min (09:30), exit EIA-1 min (10:29). Best on top/bottom decile signal | Event Sharpe 0.67 all, 2.10 extreme deciles | **Not testable**: needs point-in-time API figures + Bloomberg consensus (no owned data) |

## B. Intraday predictability findings without a full rule (mapped to a test where possible)

| Paper | Finding | Test |
|---|---|---|
| Rousse, Sévi, *Informed trading in the WTI oil futures market*, Energy Journal 40(2) 2019 | Informed trading before EIA release; over-reaction partly reversed in the hours after | Follow 10:00-10:30 sign into 10:30-11:00: -$21,962 (-1.48). Fade 10:30-10:35 to 14:30: +$11,952 (0.39) |
| Luo (AUT working paper), *CL inventory news* | Leakage 10:00-10:30 Wednesday, 5m data | same as above |
| Ye, Karali (AAEA 2015) | API and EIA surprises move CL immediately; needs consensus forecasts | not testable (no survey data) |
| Ewald, Haugom, Ouyang, Smith-Meyer, Størdal, Quantitative Finance 2025 (SSRN 5037563) | Intraday time-of-day seasonality, long/short at fixed times | **Brent** ICE only; can port the method to CL (rolling same-minute mean) |
| Wong, *Predicting intraday crude oil returns with higher-order risk-neutral moments* (SSRN 4019829) | Option semi-moments predict CL intraday returns | needs CL options data (not owned) |
| Wen, Wang, Zhang, Economic Modelling 2021 | INE Shanghai crude: intraday reversal, not momentum | different contract (INE SC) |
| Armstrong, Cardella, Sabah, *Information shocks, disagreement, and drift*, JFE 2021 (SSRN 3314221) | Bearish inventory news drifts ~5 min; bullish priced in 0.5 s | needs surprise data; 1m delayed version possible |
| Ready, Ready, *Order flows and financial investor impacts in commodity futures* (SSRN 3164757) | Temporary flow impact near 14:30 settlement | needs aggressor-side trade data |
| Chang, Daouk, Wang, *Do investors learn about analyst accuracy? oil futures* (SSRN 1531886) | 15 min post-EIA drift vs forecast error, accuracy-weighted | needs archived analyst forecasts |
| Bjursell, Wang, Zheng, *VPIN, jump dynamics and inventory announcements* (SSRN 2937436) | VPIN peaks after, not before, events | no directional rule |
| Ge, Kang, Tang, Yang, *Closing pressure, predatory trading and the negative price of oil* | TAS / 14:28-14:30 settlement pressure | event study (20 Apr 2020), no rule |

## C. Read and rejected (not intraday or not CL)
Ewald et al. Energy Economics 2022 (trading-month seasonality, monthly), Liu et al. JEF 2023 (SSRN 3584014,
daily TSMOM with intraday semivariance), Szakmary/Wang technical rules (daily), Zarattini et al. SSRN 4824172
(SPY noise-area; idea portable, not tested on CL in the paper), Boyarchenko et al. overnight drift (ES only),
Jin et al. (Chinese commodity futures), news-sentiment papers (daily/weekly), Psaradellis et al. SSRN 2832600 (7,846 daily rules on WTI, no persistence), Cummins-Bucca SSRN 1932471 (multi-day crack spreads), Caporale-Plastun SSRN 3662052 (MetaQuotes CFD, not CL), Känzig SSRN 3185839 (OPEC, daily window).

Coverage gaps: no admissible CL-specific VWAP, gap-fill or minute-bar ML paper found; SSRN revision parity unverified (403).

## Verdict
- No published intraday CL rule we found survives on CL **futures** 2010-2026 at TV costs with |t| > 2.
- The intraday-momentum family (rows 1-3) was found on **USO ETF**, gross of costs; on CL futures it is flat to
  negative, and Baltussen et al. already show CL alone is not significant.
- Independent confirmation: Fetna (2026) finds the same ORB collapse after costs on CL 1m; Ficura's journal
  version is negative out of sample.
- Only leads worth a full TV-semantics build: **ORB 5m** (row 4; positive only since 2018, thin after 1 tick) and
  the EIA-day variant "sign of 10:30-11:00, hold 11:00-14:30" (+$25,601, t 1.04, 1 tick +$12,221). Both are
  in-sample screens, not results.
