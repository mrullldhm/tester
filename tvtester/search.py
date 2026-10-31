"""Feature 2 search: random (drawn up front from the seed) or Optuna TPE over a strategy's declared SPACES.

A configuration is {"params": {...}, "filters": [[feature, op, threshold], ...]}: base parameters (variant fixed
parameters included) and entry filters, filters sorted by feature. Thresholds sit on the declared step grid, so
configurations compare exactly and duplicates are evaluated once. docs/OPTIMIZE.md has the protocol.
"""

import json
import math
import time

import numpy as np
import pandas as pd

from . import experiment, metrics
from .config import DEFAULT
from .engine import run

SCENARIOS = (0, 1, 2)
MODES = ("off", "min", "max")
P_OFF = 0.6  # random sampler: chance a filter is off (min / max share the rest)

_WORKER: dict = {}  # per process: the development bars, loaded once


def _bars():
    if "bars" not in _WORKER:
        _WORKER["bars"] = experiment.dev_bars()
    return _WORKER["bars"]


def snap(x: float, lo: float, step: float) -> float:
    """Threshold on the declared step grid (rounded so JSON / CSV round trips compare equal)."""
    return round(lo + round((x - lo) / step) * step, 10)


def canonical(params: dict, filters) -> dict:
    fs = sorted([f[0], f[1], float(f[2])] for f in filters)
    return {"params": dict(sorted(params.items())), "filters": fs}


def key(cfg: dict) -> str:
    return json.dumps(cfg, sort_keys=True, default=str)


def label(cfg: dict, base: dict) -> str:
    p = [f"{k}={v}" for k, v in cfg["params"].items() if base.get(k) != v or k not in base]
    f = [f"{ft} {'>=' if op == 'min' else '<='} {thr:g}" for ft, op, thr in cfg["filters"]]
    return ", ".join(p + f) or "baseline"


# --- evaluation ------------------------------------------------------------------------------------------
def evaluate(mod, cfg: dict) -> dict:
    """Engine runs at 0 / 1 / 2 ticks (separate runs: slippage changes fills, exits and later entries)."""
    bars = _bars()
    out = {}
    for k in SCENARIOS:
        res = run(mod.STRATEGY(**cfg["params"], filters=cfg["filters"]), bars, DEFAULT.with_slippage(k))
        s = metrics.summary(res)
        a = s["all"]
        out.update({f"net{k}": a["net_profit"], f"open{k}": s["open_pnl"], f"trades{k}": a["total_closed_trades"],
                    f"pf{k}": a["profit_factor"], f"win{k}": a["percent_profitable"], f"avg{k}": a["avg_trade"],
                    f"dd{k}": s["max_equity_drawdown"], f"sharpe{k}": s["sharpe_ratio"]})
    return out


def _eval_chunk(module_name: str, cfgs: list[dict]) -> list[dict]:
    import importlib

    mod = importlib.import_module(f"strategies.{module_name}")
    return [evaluate(mod, c) for c in cfgs]


def score(row: dict, objective: str) -> tuple[bool, float]:
    k = experiment.OBJECTIVES[objective]
    eligible = row[f"trades{k}"] >= experiment.MIN_TRADES
    return eligible, row[f"net{k}"] + row[f"open{k}"]


def rank(df: pd.DataFrame, objective: str) -> pd.DataFrame:
    """Eligible first, objective desc, profit factor desc (no losers ranks above any number), trial asc."""
    k = experiment.OBJECTIVES[objective]
    if df.empty:
        return df.assign(eligible=pd.Series(dtype=bool), objective=pd.Series(dtype=float))
    df = df.copy()
    df["eligible"] = df[f"trades{k}"] >= experiment.MIN_TRADES
    df["objective"] = df[f"net{k}"] + df[f"open{k}"]
    df["_pf"] = df[f"pf{k}"].astype(float).fillna(np.inf).where(df[f"trades{k}"] > 0, -1.0)
    df = df.sort_values(["eligible", "objective", "_pf", "trial"], ascending=[False, False, False, True])
    return df.drop(columns="_pf").reset_index(drop=True)


# --- spaces ----------------------------------------------------------------------------------------------
def space_of(mod, variant: str, name: str) -> dict:
    sp = mod.SPACES[name]
    base = {**mod.VARIANTS[variant], **mod.BASELINES[variant]}
    return {"base": base, "params": sp["params"], "filters": sp["filters"]}


def draw_random(space: dict, n: int, seed: int) -> list[dict]:
    """N unique configurations, trial 0 = the baseline (no filters). Same seed, same list."""
    rng = np.random.default_rng(seed)
    out = [canonical(space["base"], [])]
    seen = {key(out[0])}
    attempts = 0
    while len(out) < n and attempts < 100 * n:
        attempts += 1
        params = dict(space["base"])
        for p, values in space["params"].items():
            params[p] = values[int(rng.integers(len(values)))]
        filters = []
        for ft, (lo, hi, step) in space["filters"].items():
            u = rng.random()
            if u < P_OFF:
                continue
            op = "min" if u < P_OFF + (1 - P_OFF) / 2 else "max"
            steps = int(round((hi - lo) / step))
            filters.append([ft, op, snap(lo + int(rng.integers(steps + 1)) * step, lo, step)])
        c = canonical(params, filters)
        if key(c) not in seen:
            seen.add(key(c))
            out.append(c)
    return out


def neighbours(cfg: dict, space: dict) -> list[dict]:
    """Each searched base parameter one step either way in its list (categorical: every other value), each
    filter off, and each filter threshold one step either way (inside the declared range)."""
    out = []
    for p, values in space["params"].items():
        v = cfg["params"][p]
        i = values.index(v)
        cands = [values[j] for j in (i - 1, i + 1) if 0 <= j < len(values)] if not isinstance(v, str) else \
            [x for x in values if x != v]
        for x in cands:
            out.append(canonical({**cfg["params"], p: x}, cfg["filters"]))
    for n, (ft, op, thr) in enumerate(cfg["filters"]):
        rest = [f for m, f in enumerate(cfg["filters"]) if m != n]
        out.append(canonical(cfg["params"], rest))
        lo, hi, step = space["filters"][ft]
        for t in (thr - step, thr + step):
            if lo - 1e-9 <= t <= hi + 1e-9:
                out.append(canonical(cfg["params"], rest + [[ft, op, snap(t, lo, step)]]))
    uniq, seen = [], {key(cfg)}
    for c in out:
        if key(c) not in seen:
            seen.add(key(c))
            uniq.append(c)
    return uniq


# --- runners ---------------------------------------------------------------------------------------------
def run_configs(module_name: str, cfgs: list[dict], jobs: int) -> list[dict]:
    from joblib import Parallel, delayed

    if not cfgs:
        return []
    if jobs <= 1:
        return _eval_chunk(module_name, cfgs)
    chunks = [cfgs[i::jobs * 4] for i in range(jobs * 4)]  # loky reuses worker processes: bars load once each
    parts = Parallel(n_jobs=jobs)(delayed(_eval_chunk)(module_name, c) for c in chunks if c)
    by_key = {}
    for c_list, rows in zip([c for c in chunks if c], parts):
        for c, r in zip(c_list, rows):
            by_key[key(c)] = r
    return [by_key[key(c)] for c in cfgs]


def _suggest(trial, space: dict) -> dict:
    params = dict(space["base"])
    for p, values in space["params"].items():
        params[p] = trial.suggest_categorical(p, values)
    filters = []
    for ft, (lo, hi, step) in space["filters"].items():
        mode = trial.suggest_categorical(f"mode_{ft}", MODES)
        if mode != "off":
            filters.append([ft, mode, snap(trial.suggest_float(f"thr_{ft}", lo, hi, step=step), lo, step)])
    return canonical(params, filters)


def run_tpe(module_name: str, space: dict, out_dir, n_trials: int, seed: int, objective: str, jobs: int,
            progress=None, claim=None):
    """Optuna TPE with ask / tell in this process; each batch of `jobs` suggestions is evaluated in parallel.
    The budget is exact, a configuration already evaluated (or claimed earlier in the same batch) is reused, not
    re-run, and the same seed and jobs give the same trials (batches are told back in order)."""
    import warnings

    import optuna
    from optuna.storages import JournalStorage
    from optuna.storages.journal import JournalFileBackend

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    warnings.filterwarnings("ignore", category=optuna.exceptions.ExperimentalWarning)
    storage = JournalStorage(JournalFileBackend(str(out_dir / "journal.log")))
    sampler = optuna.samplers.TPESampler(seed=seed, multivariate=True, group=True, constant_liar=True)
    study = optuna.create_study(study_name="search", storage=storage, direction="maximize", sampler=sampler)
    base = {p: space["base"][p] for p in space["params"]}
    study.enqueue_trial({**base, **{f"mode_{ft}": "off" for ft in space["filters"]}})
    cfgs, rows, dups = [], [], []
    done: dict[str, dict] = {}
    while len(cfgs) < n_trials:
        batch = [study.ask() for _ in range(min(max(1, jobs), n_trials - len(cfgs)))]
        bc = [_suggest(t, space) for t in batch]
        new, seen = [], set()
        for c in bc:
            k = key(c)
            if k not in done and k not in seen:
                seen.add(k)
                new.append(c)
        if claim:
            claim(new)
        for c, r in zip(new, run_configs(module_name, new, jobs)):
            done[key(c)] = r
        claimed = set()
        for t, c in zip(batch, bc):
            k = key(c)
            dup = k not in seen or k in claimed  # evaluated in an earlier batch, or a repeat inside this one
            claimed.add(k)
            row = done[k]
            t.set_user_attr("cfg", c)
            t.set_user_attr("duplicate", dup)
            eligible, value = score(row, objective)
            study.tell(t, value if eligible else -1e12)  # ineligible trials can never be picked
            cfgs.append(c)
            rows.append(row)
            dups.append(dup)
        if progress:
            progress(len(cfgs), [r for c, r in zip(new, [done[key(c)] for c in new])], new)
    return cfgs, rows, dups


def table(cfgs, rows, base, dups=None) -> pd.DataFrame:
    recs = []
    for n, (c, r) in enumerate(zip(cfgs, rows)):
        recs.append({"trial": n, "label": label(c, base), "config": key(c),
                     "duplicate": bool(dups[n]) if dups else False, **r})
    return pd.DataFrame(recs)


def fmt_pf(x) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"


def elapsed(t0: float) -> str:
    return f"{time.time() - t0:.0f}s"
