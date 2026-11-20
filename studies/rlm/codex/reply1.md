1. **The original win rate is a TP1-touch rate, not a profitable-trade rate.**

The [logic excerpt](/home/mrullldhm/personal/tradingview-tester/studies/rlm/rlm_logic.pine) labels a completed trade a win if it touched 1R. With one contract held toward 3R, touching 1R realizes nothing; a subsequent breakeven exit loses fees. Targets receive optimistic priority when stop and target occur in the same candle, and TP1/TP3 touches can block a stop exit. Entry assumes execution at the signal close; costs and P&L are absent. Opposite-signal reversals further separate this statistic from bracket expectancy. It cannot establish profitability or Combine suitability.

2. **My CL translation, including disagreements.**

- **Clock:** retain completed signal candles S = 5m/15m/1h. Maintain levels through all trading hours; restrict order eligibility separately. Process decay/crosses, swing registrations, merges, selection, then rejection, matching the source.
- **Swings:** exclusively owner `swing_state`, with timestamp identities and `newest=True, prev=True`. I prefer **registration at first confirmation**, with replacement/removal reconciled prospectively. Confirmation is usable information; waiting for an opposite swing adds variable, potentially multi-day latency. Never erase historical signals, but withdraw invalidated contributions from future level state.
- **Locking:** acceptable as a separately named interpretation, not an immutable truth. Opposite confirmation prevents ordinary rule-5 replacement; rule 4 can still remove earlier points. A `newest` flip alone misses outside-candle and replacement cases. Snapshot differences also cannot guarantee visibility into deep cascades; implementation needs audited owner-rule event reconciliation.
- **TF strength:** use the draft’s monotone weights **instead of** reaction-distance weights, not multiplied by them. The numeric ladder is a research assumption; the owner mandated TF ordering, not those numbers. Feed weight into strength and weighted band moments; keep `touches` an independent-event count. Retain score scale 6 and threshold 50 initially. These imply effective strength ≥4.16, or ≥3.33 with polarity bonus; equal weight ranges do not imply equal signal frequencies.
- **Double counting:** agree with one economic extreme counted once across TFs. Require same kind, integer-tick price, and nested candle provenance. Upgrade only when higher-TF evidence becomes available; do not reset age, increment touches, or backdate stronger scores. Preserve distinct later revisits at the same price. Track provenance through merges.
- **Geometry:** ATR34(S) for joining/bands, ATR14(S) for risk is defensible. Source-TF ATR would let daily observations create enormous bands. Preserve tolerance 0.6, minimum half-width 0.15 ATR, 500-S-bar decay, 0.7 cross penalty, pruning below 0.25, cap 60, five merge passes, three nearest eligible levels, polarity bonus, CLV 0.6 and ten-S-bar cooldown. Refit only at declared events, as the source does.
- **Execution:** close-limit versus support `hi`/resistance `lo` retest-limit; freeze geometry at signal. Expire after **one S interval in clock minutes**, with window-end cancellation. Wick stop: long `min(low−0.25ATR14, limit−0.5ATR14)`; mirror shorts. Round explicitly to ticks and reject invalid brackets. Targets use intended limit risk; report actual-fill risk separately. One CL, touch fills, fees, no exit slippage, flat 15:10 CT.
- **Management:** compare 1R fixed against 3R with BE after 1R. BE becomes effective next minute; exclude ambiguous fill-bar highs. Drop opposite-signal reversals initially.
- **Rolls:** reset levels, orders and ATR warmup. **Do not silently reset owner swings:** their documented structure continues across rolls. Reject mixed-contract candles and roll-dependent swing references/transitions; current-contract extreme timestamps alone are insufficient.

3. **Budget and selection discipline.**

Drop band stops, expiry tuning, locking, and `htf` sourcing from the initial grid. Fix sources to S..1d. Test:

**3 S × 2 weight schemes × 2 entries × 2 sessions × 2 exits = 48 configurations.**

Sessions: all versus 08:30–13:30 CT; enforce the window on fills too. Flat weights are an attribution control. Reserve six predefined tolerance/score/half-life neighbour checks around one selected candidate: **54 configurations maximum, 108 dev backtests including strict fills**.

Require protocol gates, positive chronological halves, neighbour profitability, and acceptable concentration under both fill assumptions. Predeclare ranking and use a block-bootstrap maximum-statistic check that repeats selection across the family. Overlapping Combine attempts are not independent evidence. Freeze at most one candidate for one validation event, reporting both fill assumptions. No exceptions for almost passing cost/pass.

4. **Point-in-time hazards.**

Use candle `avail`, never candle-open timestamps as availability. Swing k becomes known at k+1 completion; do not register it at its historical extreme. Multiple updates can share one availability bar. Preserve outside-candle ordering and NaN removals; never forward-fill invalidated points.

Orders start next minute. Distinguish candle `last` from `avail`; reject stale rejection signals completing in another session/contract. Respect clock-aligned versus session-aligned TFs, DST, holidays and missing minutes. Session filters must not suppress overnight level evolution. Verify live-prefix equivalence and spot-check rolls, replacements, merges, delayed completion and ambiguous fills.

5. **Feature study without another optimization loop.**

Log every signal/order, including unfilled and blocked ones: point IDs, TF provenance, weights/upgrades, touches, polarity, score components, age, crosses, band width, ATRs, CLV, wick/body, penetration, approach distance, side, CT time, volatility, stop ticks, target distance, fill delay and cancellation. Log outcomes separately: net dollars/R, MAE/MFE, exit reason, ambiguity and touch-only status.

Predeclare a short feature list and continuous associations; control for year, session, S and risk, cluster by day, and correct multiplicity. Study net expectancy alongside win probability. Fill status and MFE are diagnostics, not entry predictors. Any discovered filter spends another research trial; confirm it on forward data. Repo validation/holdout were historically viewed, so neither is pristine.

Read only; no files written.