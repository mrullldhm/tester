# Superseded results (before the multi-timeframe dedupe fix, 2026-11-20)

Codex adversarial review found that one extreme could still count as several touches when a larger candle enclosed
several smaller-timeframe touches at the same price (~65 registrations in 2010 5m). Fixed in strategies/rlm.py
(Book._absorb, tests/test_rlm.py). Everything in this folder was produced by the old code and is kept for the record
only; the current results are one level up.

Also superseded by the exact confirm-mode withdrawal fix (same day, Codex adversarial review): the old code missed
points removed by deep rule-4 cascades.
