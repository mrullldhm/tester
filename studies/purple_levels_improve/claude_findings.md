# Claude findings (dev 2010-06..2021, in-sample; runs already best of 12+)

Scripts: `claude/decompose.py`, `claude/decompose2.py <hash>`. Session by entry time, Chicago. R = planned risk
ticks (|ticks| of target/stop exits). Rgross / Rnet = P&L per trade in R units (removes the dollar-scale effect of
bigger stops).

| Session (CT) | all touch: n / win / Rgross | all strict (e0799b1e4110): n / win / Rgross | nopd touch: n / Rgross |
|---|---|---|---|
| Asia 17:00-02:00 | 483 / 54.7% / +0.09 | 420 / 50.5% / +0.01 | 342 / +0.09 |
| London 02:00-07:00 | 286 / 53.1% / +0.06 | 257 / 49.4% / −0.01 | 191 / +0.12 |
| Pre 07:00-08:30 | 79 / 51.9% / +0.04 | 77 / 49.4% / −0.01 | 59 / +0.02 |
| RTH 08:30-13:30 | 279 / 63.1% / +0.27 | 270 / 61.1% / +0.23 | 231 / +0.29 |

Within RTH, R > 12 ticks: +0.28R (n 246); Asia R > 12: +0.06R (n 212). So the session effect is not only stop size.
RTH net by year (touch): positive 11/12 (2019 −$2,247). Overnight under strict fills ≈ 0R.

Reading: overnight trades exist on dev only through touch fills (thin book, adverse selection); the RTH trades carry
the edge and survive strict fills. Proposed (a priori mechanism: the participants who reference fixed day/week
levels trade in RTH; overnight touches occur in thin books): RTH-only signals, 1 binary choice, no window tuning
(08:30-13:30 CT = the old pit session). Cost: ~24 trades/yr, too slow for the Combine at 1 contract.
