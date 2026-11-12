# Topstep 50K Trading Combine: rules as simulated

Target account: **Topstep 50K Trading Combine** on TopstepX. Market: **CL only** (MCL banned, non-syariah for the
owner). Code: `cltester/config.py` (`Combine`) and `cltester/topstep.py`.

Source status (2026-11-12): Topstep's help centre could not be read from this machine. The numbers below come from
several 2026 third-party guides that agree with each other. Every row marked **VERIFY** must be checked against the
owner's Topstep dashboard or help.topstep.com, and this file and `config.py` updated together.

| Rule | Value used | Status |
|---|---|---|
| Starting balance | $50,000 | agreed by all sources |
| Profit target | $3,000 | agreed by all sources |
| Maximum Loss Limit (MLL) | $2,000 below the highest end-of-day balance; checked against intraday equity (open P&L included) | agreed |
| MLL stops trailing | at $50,000 (starting balance) | VERIFY |
| Daily Loss Limit (DLL) | off by default (optional on TopstepX; $1,000 when on). A DLL hit liquidates and ends the day, it does not fail the account | VERIFY |
| Consistency target | best day ≤ 55% of total profit; if broken, target becomes best_day / 0.55 (account does not fail) | VERIFY (older pages say 50%) |
| Max size | 5 CL | agreed |
| Flatten time | 3:10 PM CT, all positions closed | VERIFY for CL |
| Trading day | 5:00 PM CT to 4:00 PM CT next day | CME standard |
| CL fee | $4.04 per contract round turn (commission + exchange + NFA) | VERIFY (CME fee change 2026-10-01; Rithmic rate is higher) |
| Subscription / reset | $49 / $49 | VERIFY |

## How the simulator applies them

1. Trades come from the engine with net P&L and a per-bar path (open and worst P&L, fees included).
2. Within a day, each trade is walked bar by bar:
   - A bar that **opens** at or past a limit executes at the open: below the MLL the account **fails**; below only
     the DLL the trade is liquidated at that open price (worse than the DLL) and the day ends.
   - Inside a bar price moves continuously, so the higher limit is hit first: DLL first means liquidation at exactly
     −DLL for the day; MLL first means the account **fails**.
3. End of day: balance += day P&L; MLL = min(max(MLL, highest EOD balance − $2,000), $50,000).
4. Pass at end of day when profit ≥ max($3,000, best day / 0.55).

Reported per run:
- **Rolling**: one attempt starting on every trading day. Gives the pass rate and days to pass/fail. Attempts overlap,
  so they are not independent samples.
- **Sequential**: back-to-back attempts as lived: after a pass or fail, restart the next day. Gives passes, fails and
  cost per pass. Billing model (VERIFY): a subscription starts with the first attempt and again after every pass,
  paid at the start and every 30 days until the pass; each fail inside it costs one reset.

## Not modelled yet

- Express Funded Account (XFA) rules and payouts: the next stage after the Combine passes.
- Tier-1 news restrictions (none listed for the standard Combine; check before relying on news trades).
- MAE uses 1-minute bar extremes, so it is the worst case inside each bar, not a tick path.
