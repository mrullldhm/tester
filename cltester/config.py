"""Fixed facts: paths, the CL contract, Topstep costs and rules, research periods.

Topstep numbers come from third-party guides of 2026 (Topstep's help centre could not be read on 2026-11-12).
Every value marked VERIFY must be checked against the owner's Topstep dashboard; docs/TOPSTEP.md lists them.
"""

from dataclasses import dataclass
from datetime import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "cl1"
MANIFEST = ROOT / "data" / "manifest.json"
RESULTS = ROOT / "results"
LEDGER = RESULTS / "ledger.csv"

# --- CL (NYMEX Light Sweet Crude, 1,000 barrels). MCL is banned in this repo. ---
TICK = 0.01  # $ per barrel
TICK_VALUE = 10.0  # $ per tick per contract
EXCHANGE_TZ = "America/Chicago"
SESSION_OPEN = time(17, 0)  # CT; bars from 17:00 belong to the next trading day

# --- Topstep costs ---
FEE_ROUND_TURN = 4.04  # $ per contract, TopstepX CL incl. exchange+NFA. VERIFY (exchange fees changed 2026-10-01)


@dataclass(frozen=True)
class Combine:
    """Topstep Trading Combine rules. Defaults = 50K Combine."""

    name: str = "50K Trading Combine"
    start_balance: float = 50_000.0
    profit_target: float = 3_000.0
    max_loss: float = 2_000.0  # trails the highest end-of-day balance, checked against intraday equity
    mll_lock: float = 50_000.0  # MLL stops trailing at this level. VERIFY
    daily_loss: float | None = None  # optional DLL on TopstepX ($1,000 when enabled); None = off. VERIFY
    consistency: float = 0.55  # best day <= 55% of total profit; else target rises to best_day / 0.55. VERIFY
    max_contracts: int = 5  # CL minis
    flatten: time = time(15, 10)  # CT: Topstep closes every position at 3:10 PM CT. VERIFY for CL
    monthly_fee: float = 49.0  # $ subscription. VERIFY
    reset_fee: float = 49.0  # $ per reset after a failure. VERIFY


COMBINE_50K = Combine()

# --- Research periods: trading_day dates, end exclusive. See docs/PROTOCOL.md. ---
RESET_DATE = "2026-11-12"  # repo restarted from zero; bars after this date are the only truly unseen data
PERIODS: dict[str, tuple[str | None, str | None]] = {
    "dev": ("2010-06-01", "2022-01-01"),
    "validation": ("2022-01-01", "2025-01-01"),
    "holdout": ("2025-01-01", RESET_DATE),
    "forward": (RESET_DATE, None),
    "all": (None, None),
}
