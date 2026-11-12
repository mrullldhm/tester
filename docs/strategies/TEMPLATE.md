# <Strategy name>

Status: hypothesis | dev | validation | holdout | forward | dropped
Code: `strategies/<name>.py`

## Hypothesis
What behaviour of CL this trades, and why it should exist (who is on the other side).

## Rules
- Session / time window (CT):
- Entry (limit price, side, when placed, expiry):
- Stop:
- Target / time exit:
- Size:

## Parameters and trial budget
| Parameter | Default | Grid |
|---|---|---|
Total combinations to be tried on dev: N (declared before the first run).

## Pass criteria
Gates from docs/PROTOCOL.md, plus anything specific to this idea.

## Results
| Date | Period | Fills | Trades | Net | PF | Pass rate | Cost/pass | Note |
|---|---|---|---|---|---|---|---|---|
All results in-sample unless the period is holdout or forward; tuned rows say best of N.
