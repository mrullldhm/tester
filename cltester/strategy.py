"""Strategy contract and loader.

A strategy is strategies/<name>.py defining class Strategy(Base):
    NAME, ABOUT       short id and one-paragraph description (the hypothesis lives in docs/strategies/<name>/)
    PARAMS            default parameters (dict)
    GRID              optional {param: [values]} for later optimisation
    signals(df, p)    vectorised over every bar of df (add_session columns present); returns the engine's
                      signal frame indexed by bar position (see cltester.engine)
Signals must only use information up to and including bar i: the order works from bar i+1.
"""

import hashlib
import importlib.util
import json

import pandas as pd

from .config import ROOT


class Base:
    NAME: str = ""
    ABOUT: str = ""
    PARAMS: dict = {}
    GRID: dict = {}

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        raise NotImplementedError


def load(name: str) -> Base:
    path = ROOT / "strategies" / f"{name}.py"
    if not path.exists():
        raise SystemExit(f"no strategy file {path}")
    spec = importlib.util.spec_from_file_location(f"strategies.{name}", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    strategy = mod.Strategy()
    if not isinstance(strategy, Base):
        raise SystemExit(f"{path}: Strategy must subclass cltester.strategy.Base")
    return strategy


def params_hash(name: str, p: dict) -> str:
    code = (ROOT / "strategies" / f"{name}.py").read_bytes()
    blob = json.dumps(p, sort_keys=True).encode() + code
    return hashlib.sha256(blob).hexdigest()[:12]
