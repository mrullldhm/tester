# Independent construction audit — CL dev only

All numbers are dev, in-sample. I read the requested protocol, swing rules, builder, scanner and three strategy documents before running research. No source fixes were made. Scripts and evidence are in `codex/`; the supplied event parquet was not changed. The independent loader reads only year files 2010–2021, with UTC and trading-day filters. It loaded **3,983,238** bars, matched every stored event bar/timestamp, and checked all **1,936,238** event labels against recomputed first passages.

## Findings requiring correction or an explicit decision

1. **Restored points are mislabeled as newly confirmed events** — `studies/swing_confluence/build.py:107–109`. Any state change is counted, even when rule 4 removes a recent point and exposes an older point. **21,527 rows** move the same-side timestamp backward. Concrete example: 1m, 2010-06-07 05:38 UTC, bar 336: the last low changes from the 05:33 candle to the 05:23 candle (70.27), and the high changes from 05:34 to 05:25 (70.34). Neither old point was newly confirmed at 05:38. This changes event sampling, retrace, sweep and replacement counts. Require a genuinely offered/accepted candidate identity, or at minimum distinguish restoration from new confirmation; do not treat an old timestamp as a new candidate.

2. **The rule-5 flag does not establish rule-5 replacement** — `build.py:114`. Prior newest kind alone is insufficient because both points can be added in one update. There are at least **111,203 definite false positives**: both timestamps update and the event is the second point of that candle, so the newly accepted opposite point intervenes. Example: 1m low, bar 151, 2010-06-07 02:31 UTC, candidate 02:30 low 69.95/high 70.14. Prior newest is a low, so `replace=True`; the resulting newest is the new low, meaning the new high was accepted before that low. It is not a second low with no high between. Restorations also get the flag: 5m at 2010-06-07 05:44 UTC restores the low from 04:00 while marking replacement. The audit's larger `flag_mismatch` counts are comparisons with a conservative single-update proxy, **not** a count of proven bugs. Mining treats replacement as missing on dual-point updates.

3. **Fair-rate domain and strict-break geometry disagree with the outcome** — `build.py:119–128`. Original fair uses barriers L/H, but the outcome requires prices strictly outside them; on a one-tick nearest-neighbor walk, absorbing barriers are L−1/H+1. For a low, fair is `(c−L+1)/(H−L+2)`; mirror for a high. E.g. 2015-07-07 12:56 UTC, L=5258, H=5267, c=5262: supplied fair=4/9=.4444, strict-tick fair=5/11=.4545. A 1-tick leg at c=L produces original fair=0 versus strict-tick fair=1/3. This is baseline misspecification, not evidence of an exploitable pattern. With jumps/overshoots, neither formula is an exact empirical CL model.

   Worse, **181,790** confirmations have c outside [L,H]. Clipping makes fair=0/1 although a search beginning on the next bar can subsequently lose/win. Concrete failure: 1m low, 2010-06-07 02:25 UTC, bar 145, L=7003, H=7009, c=7013, fair=1; bar 146 resolves **fail**. Thus a probability-one event fails under the actual label. Either classify already resolved geometry consistently, or exclude these observations when using this baseline. Mining excludes them and reports original and strict-tick models in the same multiplicity budget.

4. **Weekly/monthly completion is future-dependent and fails prefix replay** — `cltester/swings.py:79–80`, with `:93–94` and `:226–230`. `last_minute` checks the next row's group ID, not an exchange calendar. At the end of a live prefix that row does not exist: final group is always incomplete, even at its scheduled close. Concrete weekly example, 2016-01-15 21:59 UTC: full-history last SH=38.39, candle 2016-01-03 23:00; prefix ending at that exact bar reports SH=38.28, candle 2015-12-20 23:00. Monthly example, 2016-07-29 20:59 UTC: full-history SH=51.67 (May 31 22:00), prefix SH=50.92 (September 30 2015 22:00). An online replay does not publish the historical signal until the next period's first bar. This uses future row existence/group membership for availability; I found no use of future weekly/monthly high/low prices before completion. A calendar-driven completion rule is needed. The week-group arithmetic itself matches Monday–Friday trading days, and monthly IDs use trading-day calendar months correctly.

5. **`minutes` counts observations, not elapsed minutes** — `build.py:146` (`r-i`). **187,806** resolved rows disagree with timestamp elapsed time, including quiet missing minutes, halts, weekends and holidays. Example: 1m low at 2010-06-07 00:41 UTC: stored 230 versus actual 232 minutes. All intraday-resolution reporting here uses timestamp subtraction. `same_day` correctly compares CME trading days; it does not mean before the 15:10 CT trading flatten.

6. **Strict no-validation-load rule is violated by the existing dev loader path** — `build.py:85`, `cltester/data.py:59–62`, `:43–49`. Dev ends 2022-01-01; padding requests through 2022-01-02. Year selection therefore includes `year=2022.parquet`, and `pd.read_parquet` materializes it before filtering. Returned dev features need not leak validation prices, but running the original build is incompatible with the owner's stronger prohibition on even loading validation bars. I did not call it. The independent loader enumerates 2010..2021 only.

7. **Trend categories break reflection symmetry when levels tie** — `build.py:155–160`. `~hh` conflates lower and equal highs, and `~hl` conflates lower and equal lows. Actual example at 2010-06-07 00:31 UTC, low event: 1m SH=SH2=7024, SL=7017>SL2=7010, stored trend=3 (contract). Reflect all prices around K=15000 and mirror the event: SH'=7983<SH2'=7990, SL'=SL2'=7976. The code calls this raw down, then side-mirrors to with=1, instead of preserving contract=3. Equality needs its own category or a symmetric policy. The same issue occurs on 1h: 2010-06-23 14:04 UTC, SH=SH2=7783, SL=7729>7704. Trend-containing scan cells inherit this defect and are not clean strategy candidates until rebuilt.

8. **Latent signed-price validity bug** — `build.py:75–79`, `:108`, `:139`, `:154`, `:162–168`. Missing prices use −1, and every validity check requires >=0. A legitimately confirmed low at −5.00 (−500 ticks), high −3.00 (−300), or a previous negative level is silently excluded/missing. This is a concrete synthetic failing input, **not an observed dev failure**: this permitted continuous-contract dataset has zero bars with negative highs/lows. Preserve explicit missingness/point identity rather than sign. The sparse search itself supports signed prices.

## Checks that passed and limits of the audit

- **Point-in-time mapping:** builder uses `swing_state`, never `swing_points`. Candidate k becomes visible at the right candle k+1's availability. Six real-data prefix comparisons (both sides on 5m, 1h, 1d) matched SH/SL/previous levels/newest exactly. That is a spot audit, not an exhaustive proof of all possible rule-4 cascades. Weekly/monthly exceptions are above.
- **Before-level sweep:** candidate timestamp is the first observed 1m bar of its candle. Index `first_bar−1` is the last available bar before that candle's observations. Strict lower/higher comparison mirrors correctly and does not use the level at confirmation. Missing clock minutes before the first observed bar do not introduce extra observations. Six raw checks below agree.
- **First passage / RangeExtreme:** no mismatch on any stored outcome. 1,200 deterministic sampled events were also searched directly with linear high/low comparisons. Synthetic lengths 1,2,3,17,63, starts through n, signed levels, no hits, equality and terminal hits passed. Strict >/< is implemented consistently. Search starts after the confirmation bar. Same-bar opposing breaches and unresolved cases are −1; excluding ties can itself cause selection bias if order ambiguity depends on context.
- **Mirroring:** non-tied trend direction negates, expansion/contraction stay unchanged; newest=-side is the with leg; position is `(event−SL)/(SH−SL)` for lows and `(SH−event)/(SH−SL)` for highs; sweep inequality reverses. Equality defect is above. The leg calculation can operate when only a high exists; missing range levels should remain unknown rather than implying a complete context.
- **Roll exclusion:** `roll_count[r] != roll_count[i]` correctly identifies any symbol change from confirmation through resolution. It catches change-and-return, not just endpoint symbol inequality. It deliberately does not reject a pivot formed on a prior contract or older context levels from prior contracts. Counts of candidate-origin-to-confirmation roll crossings are 71/99/86/93/111/120 for 1m/5m/15m/1h/4h/1d; mining excludes these as an extra sensitivity restriction. Retaining older context across rolls is specified owner behavior, but such levels can encode unadjusted contract jumps. This is a modeling limitation, not a violation of the documented resolution-roll rule.
- **Run/retest:** the stored values exclude the entire resolution bar. They avoid inventing within-minute order, but cannot tell whether a limit was touched before a same-bar exit. `run` before fail is structurally capped at the original leg because crossing the other boundary would already label hold. It is not a measurement of continuation after a hold. The prospective limit experiment rechecks raw touches including entry-bar stops and separately counts entry/target ambiguity.

## Raw-bar manual arithmetic spot checks

All times below UTC; prices in integer ticks (100 ticks=$1). Each left/candidate/right triple was aggregated from its underlying raw 1m bars, using owner candle boundaries. Low rule is left.low>=candidate.low and right.low>candidate.low; high rule mirrors. The full twelve side/base examples, confirming-candle extremes, close baseline, resolution bar and prior range extrema are in `codex/audit_evidence.json`. These checks verify candidate inequalities, known time, fair arithmetic and first crossing; they do not independently reimplement all historical swing-stack transitions.

| Base/side | Known at | Left / candidate / right relevant extreme | Event / opposite | Fair arithmetic | First later strict crossing |
|---|---|---|---|---|---|
| 1m low | 2015-07-07 12:56:00+00:00 | 5258 / 5258 / 5259 | 5258 / 5267 | 4/9=0.4444 | 2015-07-07 12:57:00+00:00: H=5266, L=5255; fail |
| 1m high | 2015-07-13 02:56:00+00:00 | 5185 / 5187 / 5186 | 5187 / 5181 | 1/6=0.1667 | 2015-07-13 02:57:00+00:00: H=5191, L=5187; fail |
| 5m high | 2015-12-08 13:59:00+00:00 | 3681 / 3686 / 3679 | 3686 / 3670 | 15/16=0.9375 | 2015-12-08 14:00:00+00:00: H=3679, L=3665; hold |
| 15m low | 2016-02-16 04:14:00+00:00 | 3084 / 3080 / 3084 | 3080 / 3094 | 9/14=0.6429 | 2016-02-16 04:22:00+00:00: H=3085, L=3077; fail |
| 1h low | 2016-02-05 00:59:00+00:00 | 3168 / 3142 / 3154 | 3142 / 3360 | 19/218=0.0872 | 2016-02-05 08:03:00+00:00: H=3150, L=3141; fail |
| 1h high | 2016-02-25 06:59:00+00:00 | 3200 / 3228 / 3226 | 3228 / 3185 | 35/43=0.8140 | 2016-02-25 07:02:00+00:00: H=3188, L=3183; hold |
| 1d low | 2016-03-30 20:59:00+00:00 | 3886 / 3791 / 3814 | 3791 / 4014 | 39/223=0.1749 | 2016-03-31 02:48:00+00:00: H=3793, L=3782; fail |
| 1d high | 2016-06-01 20:59:00+00:00 | 4972 / 5010 / 4925 | 5010 / 4869 | 119/141=0.8440 | 2016-06-02 12:35:00+00:00: H=4883, L=4867; hold |

For example, the 1h low confirmed 2016-02-05 00:59 has left/candidate/right lows 3168/3142/3154. The last opposite swing is 3360; c=3161 gives 19/218=.08716. Before 08:03, subsequent highs never exceed 3199 and lows stay >=3147. At 08:03 low=3141<3142, so fail is correct. The 1h high on February 25 has H=3228, opposite L=3185; prior-to-resolution low=3185 is an equality, so it must not resolve. At 07:02 low=3183 gives hold. The daily high's confirming candle had already traded below its opposite before confirmation, but the specified outcome starts after confirmation; the later 12:35 crossing still matches that definition.

| Base | Last bar before candidate | Same-side level then | Candidate price | Stored strict sweep |
|---|---|---:|---:|---:|
| 1m | 2015-07-07 12:54:00+00:00 | 5251 | 5258 | 0 |
| 5m | 2015-12-07 08:39:00+00:00 | 3957 | 3955 | 1 |
| 15m | 2016-02-16 03:44:00+00:00 | 3063 | 3080 | 0 |
| 1h | 2016-02-04 21:59:00+00:00 | 3153 | 3142 | 1 |
| 4h | 2016-04-06 09:59:00+00:00 | 3524 | 3656 | 0 |
| 1d | 2016-03-28 20:59:00+00:00 | 3833 | 3791 | 1 |

## Reproduction

From repository root, use only `.venv/bin/python`:

```bash
.venv/bin/python -m studies.swing_confluence.codex.prepare
.venv/bin/python -m studies.swing_confluence.codex.supplement
.venv/bin/python -m studies.swing_confluence.codex.check_flags
.venv/bin/python -m studies.swing_confluence.codex.mine
.venv/bin/python -m studies.swing_confluence.codex.qualify
.venv/bin/python -m studies.swing_confluence.codex.stress
.venv/bin/python -m studies.swing_confluence.codex.describe
.venv/bin/python -m studies.swing_confluence.codex.write_audit
```

The supplement completes the conservative prospective limit calculation before mining. No test suite or strategy backtest was needed: source implementation is unchanged. No `git` mutation, ledger write, data download, validation or holdout load occurred. These findings should be fixed upstream before promotion; this audit does not certify the existing parquet as fully correct.
