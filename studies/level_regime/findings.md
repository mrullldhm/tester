# Level regime findings (2026-11-16, corrected after the Codex review the same day)

Trading days 2010-06 to 2024-12 (dev + validation, descriptive; holdout not loaded). `run.py`, `events.csv`.
Correction: the first version compared bounce rates with 50%, but the outcome is measured from the close of the touch
minute, not from the level. Each event now has its own random-walk fair rate from that close (strict-tick barriers;
closes outside the bracket are left out, 9,866 to 9,211 events) and every edge is bounce minus fair. The first
version's claim that touched levels break more often than chance was an artefact of that baseline and is withdrawn.

## 1. A bare first touch of a fixed level is a coin flip
Bounce minus fair, all level sets, per year: −3.4 to +2.4 points, no year beyond |z| 1.9. By set, 2010-2021 /
2022-2024: previous day −0.9 / +0.8, 4h swing −1.4 / +1.0, daily swing −0.5 / −2.7, previous week +2.4 / +3.1 points.
Levels neither hold nor break by themselves. Only the previous week's level leans to holding, by 2-3 points in both
eras (n 1,203 / 344; not significant on its own).

## 2. The edge lives in the departure, and it did not change after 2021
A purple gap (3-candle gap away from the level within 4 candles) comes with a bounce 15-40 points above fair in
every year, 25-33 points in 2022-2024; without a gap 2-11 points below fair. This is circular (the gap is the start of
the bounce), so it shows the behaviour, not a tradeable rate. The behaviour looks the same before and after 2021.

## 3. What failed in 2022-2024 is the trade from the gap, and the size of the miss is within noise
`purple_levels` all 5m trades by year (touch fills; unchanged by this correction): win rate 2010-2021 mostly 50-61%
(2019: 41.5%), overall about 54.5%; 2022 45.9%, 2023 55.7%, 2024 47.2%, overall 49.6% (n 353), about 1.8 standard
errors lower. Risk / previous-day range stays 0.07-0.12 every year, including 2022 when the median daily range doubled
(390 ticks vs 140-200): not a volatility-size problem. Touches followed by a gap: 12-19% in 2010-2021, 20-21% in
2022-2024, so the gap filter is a little less selective.

## Answer
No structural break is visible in how price behaves at fixed levels: the bare touch is a coin flip in every era and
the touch-then-departure behaviour is unchanged. The 2022-2024 shortfall is the size expected from a best-of-16 dev
result shrinking toward a smaller true edge, plus noise. The edge is probably smaller than dev suggested, not proven
gone; only new data can settle it (forward / paper).

## Withdrawn
The first version's "no departure, then break" continuation idea rested on the uncorrected 50% baseline. With the fair
baseline, touches without a gap are only 2-11 points below fair, and that number is circular in the same way as §2.
Not a basis for a new hypothesis as it stands.
