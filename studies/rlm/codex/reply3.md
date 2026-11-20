**Conditional yes to ONE frozen validation, with no parameter changes.** The close-entry audit did not break the result. However, the declared family maximum-PF bootstrap remains outstanding; finish that dev-only guard before a protocol-compliant validation go. I did not access validation.

All performance numbers below are **dev, in-sample, selected from 13,824 versions**.

1. **Execution and timing**

   Independent replay reproduced **1,281 trades, $61,525 net, PF 1.309**.

   - **Open-through fills:** 1,206 trades filled on the next minute bar; 335 opened strictly through the limit, with PF 1.228. Across all fill bars, 346 received price improvement. Excluding those trades leaves PF **1.352**. Subtracting their $4,970 improvement from P&L, keeping exits unchanged, leaves PF **1.280**. No fill opened beyond its stop.
   - **Activation delay:** a full engine rerun delaying activation one additional minute gives 1,241 trades, PF **1.322**. Queue priority remains unmodelled.
   - **Late entries:** of 91 entries at/after 14:00 CT, **90 flatten and one stops**, contributing $2,152. Excluding late signals and rerunning leaves 1,190 trades, PF **1.303**.
   - **Completion:** across 1,393 orders, zero signals precede hourly completion, zero hourly-close mismatches, and zero signal candles cross sessions or contracts. There are 31 delayed completions from missing final minutes; their 28 trades lose $893, PF **0.800**.
   - **Missing minutes:** 289 trades originate from hourly candles containing fewer than 60 observed minutes: PF **1.128**. Complete candles: 992 trades, PF **1.362**.
   - **Early-ending sessions:** 40 trades, PF 1.924; excluding them leaves PF **1.292**. This is a holiday/data-gap proxy, not a verified holiday calendar.
   - **Roll windows:** within ±3 calendar days of contract switches, 177 trades, PF 1.611; outside, 1,104 trades, PF **1.268**. Five trades explicitly exit at roll.

   Removing all flagged trades together leaves **599 trades, PF 1.328**. These are diagnostics, not proposed filters.

2. **Stronger null**

   The random-date null breaks daily volatility, directional conditions and bracket-risk compatibility.

   I relocated each order to **another completed hour on the same trading day**, requiring the same side, side-adjusted CLV ≥0.6, and broad time bucket: overnight, 08:30–13:59, or 14:00–15:09 CT. Original risk ticks, 1R target, expiry, fees and engine rules remain; the level condition disappears.

   Of 1,393 orders, 1,279 have another eligible hour. The matched real subset produces **1,187 trades, PF 1.357**.

   Across **300 null runs**:

   | In-sample statistic | Result |
   |---|---:|
   | Median trades | 1,176 |
   | Median PF | **0.845** |
   | Central 95% PF range | **0.774–0.919** |
   | Maximum PF | **0.948** |
   | Runs reaching PF 1.309 | **0/300** |

   This controls daily conditions and rejection direction more closely, although exact local ATR and band geometry remain unmatched. Zero exceedances gives a plus-one Monte Carlo p-value of approximately **0.0033**, not family-adjusted significance. The reported z=5.2 does not resolve selection across 13,824 trials.

3. **Freeze and sizing**

   Keep the exact version and existing validation gates: **PF ≥1.10, pass ≥40%**. Add no filters. Flat versus TF weights changes effective selectivity, so that sibling comparison does not cleanly isolate weighting.

   **One CL at most; never automatically five.** Planned one-CL stop loss including fees has median **$374**, 95th percentile **$924**, maximum **$2,354**. At five CL, **581/1,281** planned losses exceed the entire initial $2,000 cushion.

   Even one CL is sometimes too large. For eventual execution, I would cap planned risk including fees/slippage at 10% of remaining MLL cushion, skipping when one CL exceeds it. That creates a separate variant and cannot inherit the reported 52% pass rate. The MLL trails EOD balance but is enforced intraday, including open P&L. [Topstep rules](https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit)

Saved [reply and methodology](studies/rlm/codex/reply3.md), [audit script](studies/rlm/codex/round3_audit.py), and [results](studies/rlm/codex/round3_summary.json). All new files are under the authorized directory; Python ran sequentially under the specified memory limit.