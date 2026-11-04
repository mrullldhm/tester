"""Feature 2 protocol: the development interval, provenance hashes and the append-only ledger.

Every feature-2 command that reads results (`features`, `search`, `replay`) loads bars through `dev_bars`, so
none can see bars at or after DEV_END. docs/OPTIMIZE.md has the rules.
"""

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .config import DEFAULT, ROOT
from .data import MANIFEST, Bars, load_bars

DEV_START = None  # first bar on file (2010-06-06)
DEV_END = "2024-01-01"  # exclusive, UTC. 2024-01-01 onward was exposed by feature 1 and is reserved
PROTOCOL_FROZEN = "2026-10-31"  # bars after this date were never looked at
MIN_TRADES = 300  # a trial needs this many closed trades in the objective scenario to be eligible
OBJECTIVES = {"net0": 0}  # objective -> slippage ticks; value = net profit + open P&L at the end


def dev_bars() -> Bars:
    return Bars.from_frame(load_bars(DEV_START, DEV_END))


def data_hash(bars: Bars) -> str:
    """Every input the engine uses: times, prices, volume and contract (roll exits come from contract changes)."""
    h = hashlib.sha256()
    for a in (np.asarray(bars.t_ms), bars.o, bars.h, bars.l, bars.c, np.asarray(bars.volume, dtype=float)):
        h.update(np.ascontiguousarray(a).tobytes())
    h.update("\x1f".join(map(str, bars.raw_symbol)).encode())
    return h.hexdigest()[:16]


def _sha(paths) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(str(Path(p).relative_to(ROOT)).encode())
        h.update(Path(p).read_bytes())
    return h.hexdigest()[:16]


def provenance(strategy: str, bars: Bars) -> dict:
    import optuna
    import pandas as pd

    code = list((ROOT / "tvtester").glob("*.py")) + [ROOT / "strategies" / f"{strategy}.py"]
    return {
        "dev_interval": [str(bars.ts[0]), str(bars.ts[-1]), f"end exclusive {DEV_END}"],
        "bars": len(bars),
        "data_hash": data_hash(bars),
        "manifest_hash": _sha([MANIFEST]) if MANIFEST.exists() else None,
        "code_hash": _sha(code),
        "execution_version": EXECUTION_VERSION,
        "properties": {"initial_capital": DEFAULT.initial_capital, "qty": DEFAULT.qty,
                       "commission_per_order": DEFAULT.commission_per_order},
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                     "optuna": optuna.__version__},
    }


def ledger_path(strategy: str) -> Path:
    return ROOT / "results" / strategy / "ledger.jsonl"


def log(strategy: str, kind: str, evaluations: int, **info) -> dict:
    """Append one event. `evaluations` = engine runs (one strategy configuration at one slippage scenario)."""
    path = ledger_path(strategy)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        import importlib

        note = importlib.import_module(f"strategies.{strategy}").LINEAGE  # each strategy states its own
        lineage = {"time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "kind": "lineage",
                   "evaluations": 0, "note": note}
        try:  # exclusive create: two first writers must not truncate each other's events
            with path.open("x") as f:
                f.write(json.dumps(lineage) + "\n")
        except FileExistsError:
            pass
    event = {"time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "kind": kind,
             "evaluations": int(evaluations), **info}
    with path.open("a") as f:
        f.write(json.dumps(event, default=str) + "\n")
    return event


def total_evaluations(strategy: str) -> int:
    path = ledger_path(strategy)
    if not path.exists():
        return 0
    return sum(json.loads(line)["evaluations"] for line in path.read_text().splitlines() if line.strip())


EXECUTION_VERSION = "limit-close-tp-expiry-v1"


def check_execution(cfg: dict) -> None:
    """A saved market-entry winner is not a winner of the new limit-entry search."""
    if cfg.get("execution_version") != EXECUTION_VERSION or cfg.get("source", {}).get("objective") != "net0":
        raise SystemExit("This configuration uses the previous execution rules. Run a new net0 search for limit entries; "
                         "historical configurations and results are preserved.")
