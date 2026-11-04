"""Feature 3 (validation A, development interval only): walk-forward re-selection, CSCV / PBO and the deflated
Sharpe ratio of a frozen feature-2 candidate. docs/VALIDATE.md has the protocol and the verdict rules.

The pure functions (`select`, `wfo_select`, `cscv`, `dsr`, `sharpe_stats`) take arrays and know nothing about
strategies, so tests can check them on synthetic numbers. `cmd_validate` runs the engine and writes the report.
"""

import hashlib
import gc
import importlib
import itertools
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

from . import experiment, metrics, search
from .config import DEFAULT, ROOT, TICK_VALUE
from .data import Bars, load_bars
from .engine import run

SCENARIOS = (0,)
SELECT_TICKS = 0  # selection uses baseline net0
FOLD_YEARS = tuple(range(2014, 2024))
ROLLING_YEARS = 4
S_BLOCKS = 16
BOOT_BLOCK, BOOT_N, BOOT_SEED = 20, 2000, 0
RULES = {"min_positive_folds": 7, "pbo_max": 0.5, "dsr_min": 0.95}
EULER = 0.5772156649015329
E2_SEARCH = {"space_name": "filters", "sampler": "random", "seed": 1, "trials": 200, "objective": "net0"}
_N = NormalDist()
_W: dict = {}  # per worker process: the development frame and bars


def _day(date: str) -> int:
    """UTC epoch day of a date (the day number `metrics.daily_equity` uses)."""
    return int(pd.Timestamp(date, tz="UTC").value // 86_400_000_000_000)


def min_trades(days: int, total_days: int) -> int:
    return math.ceil(experiment.MIN_TRADES * days / total_days)


# --- selection --------------------------------------------------------------------------------------------
def profit_factor(gp: np.ndarray, gl: np.ndarray, closed: np.ndarray) -> np.ndarray:
    """E2's tie-break value: gross profit / gross loss; no losing trade ranks above any number (inf); no trade -1."""
    with np.errstate(divide="ignore", invalid="ignore"):
        pf = np.where(gl > 0, gp / np.where(gl > 0, gl, 1.0), np.inf)
    return np.where(closed > 0, pf, -1.0)


def select(objective: np.ndarray, closed: np.ndarray, need: int, pf: np.ndarray | None = None) -> int | None:
    """E2 rule on one window: highest objective among configurations with `need`+ closed trades; ties: higher
    profit factor, then lower index (= lower trial number). None when no configuration is eligible (cash)."""
    ok = closed >= need
    if not ok.any():
        return None
    v = np.where(ok, objective, -np.inf)
    tied = np.flatnonzero(v == v.max())
    if pf is not None and len(tied) > 1:
        p = pf[tied]
        tied = tied[p == p.max()]
    return int(tied[0])


def wfo_select(day: np.ndarray, equity: np.ndarray, closed: np.ndarray, cap: float, years=FOLD_YEARS,
               rolling: int | None = None, gp: np.ndarray | None = None, gl: np.ndarray | None = None) -> list[dict]:
    """Pick one configuration per test year from the selection-scenario matrix (configs x days).

    Anchored (rolling None): window = first day .. last day before Y-01-01; objective = equity there - capital.
    Rolling: window = Y-rolling-01-01 .. Y-01-01; objective = equity change over it, trades closed inside it.
    gp / gl (cumulative gross profit / loss of closed trades per day end) give the profit-factor tie-break."""
    total = len(day)
    out = []
    for y in years:
        p = int(np.searchsorted(day, _day(f"{y}-01-01"))) - 1  # last day end before the cutoff
        if p < 0:
            out.append({"year": y, "pick": None, "train_days": 0, "need": 0, "train_obj": None})
            continue
        if rolling is None:
            q, base_eq, base_n = 0, np.full(equity.shape[0], cap), np.zeros(equity.shape[0], dtype=np.int64)
        else:
            q = int(np.searchsorted(day, _day(f"{y - rolling}-01-01")))
            base_eq = equity[:, q - 1] if q > 0 else np.full(equity.shape[0], cap)
            base_n = closed[:, q - 1] if q > 0 else np.zeros(equity.shape[0], dtype=np.int64)
        obj, n = equity[:, p] - base_eq, closed[:, p] - base_n
        days = p - q + 1
        need = min_trades(days, total)
        pf = None
        if gp is not None:
            zero = np.zeros(equity.shape[0])
            pf = profit_factor(gp[:, p] - (gp[:, q - 1] if q > 0 else zero),
                               gl[:, p] - (gl[:, q - 1] if q > 0 else zero), n)
        pick = select(obj, n, need, pf)
        out.append({"year": y, "pick": pick, "train_days": days, "need": need,
                    "train_obj": None if pick is None else float(obj[pick]),
                    "train_years": days / total * (day[-1] - day[0] + 1) / 365.25})
    return out


# --- CSCV / PBO -------------------------------------------------------------------------------------------
def blocks(n_days: int, s: int = S_BLOCKS) -> list[tuple[int, int]]:
    """S contiguous blocks of equal day count; the first n_days mod S blocks get one more day."""
    size, extra = divmod(n_days, s)
    out, a = [], 0
    for i in range(s):
        b = a + size + (1 if i < extra else 0)
        out.append((a, b))
        a = b
    return out


def avg_rank(values: np.ndarray, x: float) -> float:
    """Ascending rank of x among values (1 = worst), ties averaged."""
    less = int((values < x).sum())
    eq = int((values == x).sum())
    return less + (eq + 1) / 2


def cscv(pnl: np.ndarray, closed_daily: np.ndarray, s: int = S_BLOCKS, eligible_only: bool = False,
         gp_daily: np.ndarray | None = None, gl_daily: np.ndarray | None = None) -> dict:
    """Probability of backtest overfitting. pnl / closed_daily: configs x days (daily P&L, closed trades per day);
    gp_daily / gl_daily (gross profit / loss closed per day) give the profit-factor tie-break."""
    c, d = pnl.shape
    bl = blocks(d, s)

    def per_block(x):
        return np.stack([x[:, a:b].sum(axis=1) for a, b in bl], axis=1)  # configs x blocks

    bp, bt = per_block(pnl), per_block(closed_daily)
    bgp = per_block(gp_daily) if gp_daily is not None else None
    bgl = per_block(gl_daily) if gl_daily is not None else None
    bd = np.array([b - a for a, b in bl])
    logits, w_is, w_oos, skipped = [], [], [], 0
    for combo in itertools.combinations(range(s), s // 2):
        m = np.zeros(s, dtype=bool)
        m[list(combo)] = True
        is_net, oos_net = bp[:, m].sum(axis=1), bp[:, ~m].sum(axis=1)
        is_n = bt[:, m].sum(axis=1)
        need = min_trades(int(bd[m].sum()), d)
        pf = None if bgp is None else profit_factor(bgp[:, m].sum(axis=1), bgl[:, m].sum(axis=1), is_n)
        pick = select(is_net, is_n, need, pf)
        if pick is None:
            skipped += 1
            continue
        pool = oos_net[is_n >= need] if eligible_only else oos_net
        w = avg_rank(pool, oos_net[pick]) / (len(pool) + 1)
        logits.append(math.log(w / (1 - w)))
        w_is.append(is_net[pick])
        w_oos.append(oos_net[pick])
    lg, wi, wo = np.array(logits), np.array(w_is), np.array(w_oos)
    slope = np.polyfit(wi, wo, 1) if len(wi) > 1 and np.ptp(wi) > 0 else [float("nan"), float("nan")]
    return {"splits": len(lg) + skipped, "skipped": skipped,
            "pbo": float((lg <= 0).mean()) if len(lg) else None,
            "p_oos_loss": float((wo < 0).mean()) if len(wo) else None,
            "median_logit": float(np.median(lg)) if len(lg) else None,
            "slope": float(slope[0]), "intercept": float(slope[1]),
            "median_is": float(np.median(wi)) if len(wi) else None,
            "median_oos": float(np.median(wo)) if len(wo) else None,
            "logits": lg.tolist()}


# --- deflated Sharpe --------------------------------------------------------------------------------------
def sharpe_stats(r: np.ndarray) -> dict:
    """Per-period SR (ddof 1), biased skewness, Pearson kurtosis (normal = 3)."""
    r = np.asarray(r, dtype=float)
    sd = r.std(ddof=1) if len(r) > 1 else 0.0
    m2 = ((r - r.mean()) ** 2).mean()
    if sd == 0 or m2 == 0:
        return {"sr": None, "skew": None, "kurt": None, "t": len(r)}
    z = r - r.mean()
    return {"sr": float(r.mean() / sd), "skew": float((z ** 3).mean() / m2 ** 1.5),
            "kurt": float((z ** 4).mean() / m2 ** 2), "t": len(r)}


def expected_max_sr(v: float, n: int) -> float:
    """SR0: expected maximum SR of n trials with SR variance v and true SR 0 (Bailey & Lopez de Prado 2014)."""
    if n <= 1:
        return 0.0
    return math.sqrt(v) * ((1 - EULER) * _N.inv_cdf(1 - 1 / n) + EULER * _N.inv_cdf(1 - 1 / (n * math.e)))


def dsr(stats: dict, v: float, n: int) -> dict:
    """Deflated Sharpe ratio; None (a fail) when SR is undefined or the variance term is not positive."""
    sr, g3, g4, t = stats["sr"], stats["skew"], stats["kurt"], stats["t"]
    sr0 = expected_max_sr(v, n)
    if sr is None or t < 2:
        return {"sr0": sr0, "dsr": None, "n": n, "v": v}
    den = 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2
    if den <= 0:
        return {"sr0": sr0, "dsr": None, "n": n, "v": v}
    return {"sr0": sr0, "dsr": _N.cdf((sr - sr0) * math.sqrt(t - 1) / math.sqrt(den)), "n": n, "v": v}


def universe_variance(r_all: np.ndarray) -> tuple[float, int]:
    """Variance (ddof 1) of the per-config SRs, configurations with zero variance excluded (count returned)."""
    srs = [sharpe_stats(r)["sr"] for r in r_all]
    ok = np.array([x for x in srs if x is not None])
    return (float(ok.var(ddof=1)) if len(ok) > 1 else 0.0), len(srs) - len(ok)


def bootstrap_sr(r: np.ndarray, block: int = BOOT_BLOCK, n: int = BOOT_N, seed: int = BOOT_SEED) -> tuple:
    """90% interval of the SR from a stationary block bootstrap (Politis-Romano, mean block length `block`)."""
    rng = np.random.default_rng(seed)
    t = len(r)
    out = np.empty(n)
    for k in range(n):
        start = rng.integers(t, size=t)
        new = rng.random(t) < 1 / block
        idx = np.empty(t, dtype=np.int64)
        idx[0] = start[0]
        for i in range(1, t):
            idx[i] = start[i] if new[i] else (idx[i - 1] + 1) % t
        x = r[idx]
        sd = x.std(ddof=1)
        out[k] = x.mean() / sd if sd > 0 else 0.0
    return float(np.quantile(out, 0.05)), float(np.quantile(out, 0.95))


def monthly(day: np.ndarray, pnl: np.ndarray) -> np.ndarray:
    """Daily P&L (configs x days) summed by UTC calendar month (configs x months)."""
    month = pd.to_datetime(day, unit="D").to_period("M").astype(str).to_numpy()
    keys, inv = np.unique(month, return_inverse=True)
    out = np.zeros((pnl.shape[0], len(keys)))
    np.add.at(out.T, inv, pnl.T)
    return out


# --- engine work (worker processes) ----------------------------------------------------------------------
def _frame() -> pd.DataFrame:
    if "df" not in _W:
        _W["df"] = load_bars(experiment.DEV_START, experiment.DEV_END)  # never a bar at or after DEV_END
    return _W["df"]


def _matrix_chunk(module_name: str, cfgs: list[dict]) -> list[dict]:
    mod = importlib.import_module(f"strategies.{module_name}")
    bars = search._bars()
    out = []
    for c in cfgs:
        row = {}
        for k in SCENARIOS:
            res = run(mod.STRATEGY(**c["params"], filters=c["filters"]), bars, DEFAULT.with_slippage(k))
            de = metrics.daily_equity(res)
            ex = np.array([t.exit_bar for t in res.trades], dtype=np.int64)
            pr = np.array([t.profit for t in res.trades], dtype=float)
            o = np.argsort(ex, kind="stable")
            gp = np.concatenate([[0.0], np.cumsum(np.maximum(pr[o], 0))])[de["closed"]]
            gl = np.concatenate([[0.0], np.cumsum(np.maximum(-pr[o], 0))])[de["closed"]]
            row[k] = {"day": de["day"], "equity": de["equity"], "closed": de["closed"], "gp": gp, "gl": gl,
                      "net": float(sum(t.profit for t in res.trades)), "open": metrics.open_pnl(res),
                      "trades": len(res.trades)}
        out.append(row)
    return out


def fold_value(res, ticks: int) -> float:
    """Closed profit + a market close of a position still open at the last bar (exit commission + slippage)."""
    v = float(sum(t.profit for t in res.trades))
    t = res.open_trade
    if t is not None:
        v += metrics.open_pnl(res) - (res.props.commission_per_order + ticks * TICK_VALUE) * t.qty
    return v


def _fold_chunk(module_name: str, jobs: list[tuple]) -> list[dict]:
    """jobs: (config, year, ticks). Indicators over every development bar before Y+1-01-01, flat at Y-01-01."""
    mod = importlib.import_module(f"strategies.{module_name}")
    search._WORKER.clear()  # a reused worker may still hold the matrix step's bars: free them first
    df = _frame()
    if "roll" not in _W:  # the development set's roll flags: a prefix must not lose its last bar's roll exit
        sym = df["raw_symbol"].to_numpy()
        _W["roll"] = np.r_[sym[:-1] != sym[1:], False]
    cache: dict[int, Bars] = {}
    out: list = [None] * len(jobs)
    for n in sorted(range(len(jobs)), key=lambda n: jobs[n][1]):  # by year: one prefix build per year
        c, y, k = jobs[n]
        if y not in cache:
            # Result retains its Bars. Release every previous-prefix reference before
            # allocating the next prefix, including the old result during run().
            res = bars = b = None
            cache.clear()  # one prefix at a time keeps a worker's memory bounded
            gc.collect()
            b = Bars.from_frame(df[df["ts"] < pd.Timestamp(f"{y + 1}-01-01", tz="UTC")].reset_index(drop=True))
            b.last_of_contract = _W["roll"][:len(b)].copy()
            cache[y] = b
        bars = cache[y]
        i0 = int(np.searchsorted(bars.t_ms, pd.Timestamp(f"{y}-01-01", tz="UTC").value // 1_000_000))
        res = run(mod.STRATEGY(**c["params"], filters=c["filters"]), bars, DEFAULT.with_slippage(k), start=i0)
        de = metrics.daily_equity(res)
        keep = de["end_bar"] >= i0
        out[n] = {"value": fold_value(res, k), "trades": len(res.trades), "open_at_end": res.open_trade is not None,
                  "day": de["day"][keep], "equity": de["equity"][keep]}
    return out


def _parallel(fn, module_name: str, items: list, jobs: int) -> list:
    from joblib import Parallel, delayed

    if not items:
        return []
    if jobs <= 1:
        return fn(module_name, items)
    idx = list(range(len(items)))
    chunks = [idx[i::jobs * 4] for i in range(jobs * 4)]
    chunks = [c for c in chunks if c]
    parts = Parallel(n_jobs=jobs)(delayed(fn)(module_name, [items[i] for i in c]) for c in chunks)
    out = [None] * len(items)
    for c, rows in zip(chunks, parts, strict=True):
        for i, r in zip(c, rows, strict=True):
            out[i] = r
    return out


# --- universe and accounting -----------------------------------------------------------------------------
def universe(cfg: dict) -> tuple[list[dict], pd.DataFrame]:
    """The 200 E2 configurations in trial order (trials.csv is saved ranked, so sort by its `trial` column)."""
    df = pd.read_csv(ROOT / cfg["source"]["search"] / "trials.csv").sort_values("trial").reset_index(drop=True)
    if df["trial"].tolist() != list(range(len(df))):
        raise SystemExit("trials.csv trial numbers are not 0..N-1")
    return [json.loads(x) for x in df["config"]], df


def distinct_configs(mod, name: str, variants) -> int:
    """Distinct configurations seen: the feature-1 grid of each variant + every search trial and neighbour."""
    from .optimize import combos

    keys = set()
    for v in variants:
        for p in combos(mod.GRID):
            keys.add(search.key(search.canonical({**mod.VARIANTS[v], **p}, [])))
        for d in sorted((ROOT / "results" / name / "search").glob(f"{v}_*")):
            for f in ("trials.csv", "neighbours.csv"):
                if (d / f).exists():
                    keys |= {search.key(json.loads(x)) for x in pd.read_csv(d / f)["config"]}
    return len(keys)


def _sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


# --- command ----------------------------------------------------------------------------------------------
def doc_dir(name: str) -> Path:
    return ROOT / "docs" / "strategies" / name / "validate"


def cmd_validate(cfg_file: str, jobs: int = 1, run_tag: str = "") -> str:
    path = (ROOT / cfg_file) if not cfg_file.startswith("/") else Path(cfg_file)
    cfg = json.loads(path.read_text())
    if cfg["interval"] != [experiment.DEV_START, experiment.DEV_END]:
        raise SystemExit("feature 3 validates development-interval configurations only")
    experiment.check_execution(cfg)
    name, variant = cfg["strategy"], cfg["variant"]
    mod = importlib.import_module(f"strategies.{name}")
    tag = experiment.tagged_run_id(path.stem.removeprefix(f"{name}_"), run_tag)
    out = ROOT / "results" / name / "validate" / tag
    if out.exists():
        raise SystemExit(f"{out} already exists: a validation tag is run once. A rerun (a bug, never a result) "
                         "needs a dated entry in the lab notebook, then this folder moved aside by hand")
    run_meta = json.loads((ROOT / cfg["source"]["search"] / "run.json").read_text())
    wrong = {k: run_meta.get(k) for k, x in E2_SEARCH.items() if run_meta.get(k) != x}
    if wrong or run_meta.get("strategy") != name or run_meta.get("variant") != variant:
        raise SystemExit(f"source search is not the declared E2 search of {name} {variant} "
                         f"(feature 3 re-selects only over a data-independent random draw): {wrong}")
    cfgs, trials = universe(cfg)
    if len(cfgs) != E2_SEARCH["trials"]:
        raise SystemExit(f"expected {E2_SEARCH['trials']} trials, found {len(cfgs)}")
    cand = int(cfg["source"]["trial"])
    if search.key(cfgs[cand]) != search.key(search.canonical(cfg["params"], cfg["filters"])):
        raise SystemExit("frozen configuration is not trial %d of its search" % cand)
    out.mkdir(parents=True)
    bars = search._bars()
    prov = experiment.provenance(name, bars)
    meta = {"strategy": name, "variant": variant, "config": str(path.relative_to(ROOT)), "candidate_trial": cand,
            "universe": len(cfgs), "scenarios": SCENARIOS, "select_ticks": SELECT_TICKS, "fold_years": FOLD_YEARS,
            "rolling_years": ROLLING_YEARS, "s_blocks": S_BLOCKS, "rules": RULES, "started_utc": _now(), **prov,
            "hashes": {"trials_csv": _sha_file(ROOT / cfg["source"]["search"] / "trials.csv"),
                       "config": _sha_file(path), "validate_md": _sha_file(ROOT / "docs" / "VALIDATE.md")}}
    (out / "run.json").write_text(json.dumps(meta, indent=2, default=str))
    t0 = time.time()

    # step 1: matrix
    experiment.log(name, "validate_matrix", len(SCENARIOS) * len(cfgs), tag=tag, configurations=len(cfgs))
    rows = _parallel(_matrix_chunk, name, cfgs, jobs)
    day = rows[0][0]["day"]
    eq = np.stack([np.stack([r[k]["equity"] for r in rows]) for k in SCENARIOS])  # scenario x config x day
    cl = np.stack([np.stack([r[k]["closed"] for r in rows]) for k in SCENARIOS])
    gp = np.stack([np.stack([r[k]["gp"] for r in rows]) for k in SCENARIOS])
    gl = np.stack([np.stack([r[k]["gl"] for r in rows]) for k in SCENARIOS])
    cap = DEFAULT.initial_capital
    bad = []
    for i, r in enumerate(rows):
        t = trials.iloc[i]
        for k in SCENARIOS:
            x = r[k]
            if not (np.array_equal(x["day"], day) and abs(x["equity"][-1] - cap - x["net"] - x["open"]) < 1e-6
                    and abs(x["net"] - t[f"net{k}"]) < 1e-6 and abs(x["open"] - t[f"open{k}"]) < 1e-6
                    and x["trades"] == t[f"trades{k}"] and x["closed"][-1] == x["trades"]):
                bad.append((i, k))
    np.savez_compressed(out / "matrix.npz", day=day, equity=eq, closed=cl, gross_profit=gp, gross_loss=gl)
    if bad:
        raise SystemExit(f"matrix does not match trials.csv for (trial, ticks) {bad[:10]}")
    print(f"  {tag}: matrix {eq.shape} matches trials.csv, {time.time() - t0:.0f}s", flush=True)

    # Only daily matrices are needed below. In serial mode the local reference
    # otherwise keeps all full-history indicator caches alive during every fold.
    del bars, rows
    search._WORKER.clear()
    gc.collect()

    # step 2: walk-forward
    s = SCENARIOS.index(SELECT_TICKS)
    sel = {"anchored": wfo_select(day, eq[s], cl[s], cap, gp=gp[s], gl=gl[s]),
           "rolling": wfo_select(day, eq[s], cl[s], cap, rolling=ROLLING_YEARS, gp=gp[s], gl=gl[s])}
    fold_jobs = [(cfgs[f["pick"]], f["year"], k) for kind in sel for f in sel[kind] if f["pick"] is not None
                 for k in SCENARIOS]
    experiment.log(name, "validate_folds", len(fold_jobs), tag=tag,
                   configurations=len({search.key(j[0]) for j in fold_jobs}))
    fold_res = iter(_parallel(_fold_chunk, name, fold_jobs, jobs))
    folds = {}
    for kind in sel:
        recs = []
        for f in sel[kind]:
            rec = {"year": f["year"], "trial": f["pick"], "train_days": f["train_days"], "need": f["need"],
                   "train_obj": f["train_obj"], "train_years": f.get("train_years"),
                   "config": None if f["pick"] is None else search.label(cfgs[f["pick"]], cfgs[0]["params"])}
            for k in SCENARIOS:
                if f["pick"] is None:
                    rec.update({f"net{k}": 0.0, f"trades{k}": 0, f"open_end{k}": False, f"slice{k}": 0.0})
                    continue
                fr = next(fold_res)
                a = int(np.searchsorted(day, _day(f"{f['year']}-01-01")))
                b = int(np.searchsorted(day, _day(f"{f['year'] + 1}-01-01"))) - 1
                prev = eq[k, f["pick"], a - 1] if a > 0 else cap
                rec.update({f"net{k}": fr["value"], f"trades{k}": fr["trades"], f"open_end{k}": fr["open_at_end"],
                            f"slice{k}": float(eq[k, f["pick"], b] - prev),  # same config, full run: boundary check
                            f"_curve{k}": (fr["day"], fr["equity"])})
            a = int(np.searchsorted(day, _day(f"{f['year']}-01-01")))
            b = int(np.searchsorted(day, _day(f"{f['year'] + 1}-01-01"))) - 1
            for k in SCENARIOS:  # reference: the frozen candidate in the same year (in-sample)
                prev = eq[k, cand, a - 1] if a > 0 else cap
                rec[f"cand{k}"] = float(eq[k, cand, b] - prev)
            recs.append(rec)
        folds[kind] = recs
        pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in recs]).to_csv(
            out / f"folds{'' if kind == 'anchored' else '_rolling'}.csv", index=False)

    # step 3: CSCV
    pnl = np.diff(np.concatenate([np.full((*eq.shape[:2], 1), cap), eq], axis=2), axis=2)
    cl_daily = np.diff(np.concatenate([np.zeros((*cl.shape[:2], 1), dtype=cl.dtype), cl], axis=2), axis=2)
    def daily(x):
        return np.diff(np.concatenate([np.zeros((*x.shape[:2], 1)), x], axis=2), axis=2)

    gpd, gld = daily(gp), daily(gl)
    pbo = {"primary": cscv(pnl[s], cl_daily[s], gp_daily=gpd[s], gl_daily=gld[s]),
           "eligible_only": cscv(pnl[s], cl_daily[s], eligible_only=True, gp_daily=gpd[s], gl_daily=gld[s])}
    pbo["identical_paths"] = int(len(cfgs) - len(np.unique(pnl[s], axis=0)))
    (out / "pbo.json").write_text(json.dumps(pbo, indent=1))

    # step 4: DSR
    n_var = distinct_configs(mod, name, [variant])
    n_all = distinct_configs(mod, name, list(mod.VARIANTS))
    dsr_out = {}
    for k in SCENARIOS:
        r_all = pnl[k] / cap
        v, zero = universe_variance(r_all)
        st = sharpe_stats(r_all[cand])
        mr = monthly(day, pnl[k]) / cap
        vm, _ = universe_variance(mr)
        dsr_out[f"ticks{k}"] = {
            "stats": st, "v": v, "zero_variance_configs": zero,
            "primary": dsr(st, v, len(cfgs)), "variant_n": dsr(st, v, n_var), "strategy_n": dsr(st, v, n_all),
            "monthly": dsr(sharpe_stats(mr[cand]), vm, len(cfgs)), "monthly_stats": sharpe_stats(mr[cand]),
            "psr0": dsr(st, 0.0, 1),
            "boot90": bootstrap_sr(r_all[cand]) if st["sr"] is not None else None}
    dsr_out["n"] = {"paired": len(cfgs), "variant_distinct": n_var, "strategy_distinct": n_all}
    (out / "dsr.json").write_text(json.dumps(dsr_out, indent=1, default=float))

    # verdicts
    an = folds["anchored"]
    tot = {k: sum(r[f"net{k}"] for r in an) for k in SCENARIOS}
    pos = sum(r[f"net{SELECT_TICKS}"] > 0 for r in an)
    pb = pbo["primary"]["pbo"]
    dv = dsr_out["ticks0"]["primary"]["dsr"]
    proc = {"wfo_net0": tot[0] > 0, "folds": pos >= RULES["min_positive_folds"],
            "pbo": pb is not None and pb <= RULES["pbo_max"]}
    candv = {"dsr": dv is not None and dv >= RULES["dsr_min"]}
    verdict = {"procedure": all(proc.values()), "procedure_checks": proc, "candidate": all(candv.values()),
               "candidate_checks": candv, "advance": all(proc.values()) and all(candv.values()),
               "wfo_total": tot, "positive_folds": pos, "pbo": pb, "dsr": dv}
    (out / "verdict.json").write_text(json.dumps(verdict, indent=1, default=bool))
    png = doc_dir(name) / f"{tag}.png"
    _png(folds, pbo, png, f"{mod.TITLE}: {variant} {tag}")
    doc = _write_doc(name, mod, variant, tag, cfg, path, meta, folds, pbo, dsr_out, verdict, cfgs, cand,
                     len(fold_jobs), out)
    experiment.log(name, "validate", 0, tag=tag, engine_runs=len(SCENARIOS) * len(cfgs) + len(fold_jobs),
                   advance=verdict["advance"], procedure=verdict["procedure"], candidate=verdict["candidate"],
                   code_hash=prov["code_hash"], data_hash=prov["data_hash"])
    return str(doc)


# --- report -----------------------------------------------------------------------------------------------
def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")


def _usd(x) -> str:
    from .report import usd

    return "—" if x is None or x != x else usd(x)


def _f(x, d=3) -> str:
    return "—" if x is None or x != x else f"{x:.{d}f}"


def _ok(b: bool) -> str:
    return "pass" if b else "**fail**"


def _png(folds, pbo, path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4), dpi=110, gridspec_kw={"width_ratios": [2, 1]})
    for k in SCENARIOS:
        xs, ys, acc = [], [], 0.0
        for r in folds["anchored"]:
            if f"_curve{k}" not in r:
                continue
            d, e = r[f"_curve{k}"]
            if len(e) == 0:
                continue
            start = DEFAULT.initial_capital
            y = acc + e - start
            y[-1] = acc + r[f"net{k}"]  # the fold's last day includes the market close of a position left open
            xs += list(pd.to_datetime(d, unit="D"))
            ys += list(y)
            acc += r[f"net{k}"]
        a1.plot(xs, ys, lw=1.2 if k == 0 else 0.9, label=f"{k} tick{'s' if k != 1 else ''}")
    a1.axhline(0, color="#888", lw=0.6, ls="--")
    a1.set_title("Walk-forward: picked config each year, cumulative (USD)", fontsize=9)
    a1.grid(alpha=0.25)
    a1.legend(fontsize=8)
    lg = pbo["primary"]["logits"]
    if lg:
        a2.hist(lg, bins=40, color="#6a8caf")
    a2.axvline(0, color="#c44", lw=0.8)
    a2.set_title(f"CSCV logits (PBO = share <= 0: {_f(pbo['primary']['pbo'], 2)})", fontsize=9)
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def _write_doc(name, mod, variant, tag, cfg, path, meta, folds, pbo, dsr_out, verdict, cfgs, cand, n_fold_runs,
               out) -> Path:
    v, an, ro = verdict, folds["anchored"], folds["rolling"]
    L = [f"# {mod.TITLE}: limit-entry validation, {variant} ({tag})", "",
         f"Generated {_now()} UTC. Execution: {experiment.EXECUTION_VERSION}. Commission included; no added slippage.", "",
         "> **Development interval only, in-sample research.** The starting settings were selected using the full "
         "history. Walk-forward re-selection does not remove that exposure. Passing is not proof of a tradable edge.", "",
         f"Candidate: trial {cand} of `{cfg['source']['search']}`; {len(cfgs)} configurations in the search universe.", "",
         "## Verdict", "", "| Check | Result | Need |", "|---|---|---|",
         f"| Walk-forward net profit | {_usd(v['wfo_total'][0])} | > 0 |",
         f"| Positive years | {v['positive_folds']} of {len(an)} | >= {RULES['min_positive_folds']} |",
         f"| PBO | {_f(v['pbo'])} | <= {RULES['pbo_max']} |",
         f"| DSR | {_f(v['dsr'])} | >= {RULES['dsr_min']} |", "",
         f"Procedure: {_ok(v['procedure'])}. Candidate: {_ok(v['candidate'])}. Advance to F4: {v['advance']}.", "",
         f"Engine runs: {len(cfgs)} matrix configurations + {n_fold_runs} fold runs, baseline only.", "",
         f"![Walk-forward and CSCV]({tag}.png)", ""]
    for title, rows in (("Walk-forward, anchored", an), ("Sensitivity: rolling four-year training", ro)):
        L += [f"## {title}", "", "Each test year starts flat. Selection uses prior development data only, "
              "net profit plus open P&L, and the scaled minimum trade count. Sensitivities cannot rescue a failure.", "",
              "| Year | Picked trial | Configuration | Training result | Net profit | Trades | Frozen candidate (in-sample) |",
              "|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append(f"| {r['year']} | {r['trial'] if r['trial'] is not None else 'cash'} | {r['config'] or 'cash'} | "
                     f"{_usd(r['train_obj'])} | {_usd(r['net0'])} | {r['trades0']} | {_usd(r['cand0'])} |")
        totals = fold_totals(rows)
        L += [f"| Total | | | | {_usd(totals['net0'])} | {totals['trades0']} | |", "",
              f"Walk-forward efficiency: {_wfe(rows)}. Fold-end open positions: {sum(r['open_end0'] for r in rows)}.",
              f"Fold/full-history boundary difference: {_usd(sum(abs(r['net0'] - r['slice0']) for r in rows))}.", ""]
    L += ["## Probability of backtest overfitting", "",
          "Daily marked-to-market P&L, split into complementary halves. PBO is the fraction where the in-sample "
          "winner ranks at or below the out-of-sample median. This diagnostic is not time ordered.", "",
          "| Version | PBO | P(OOS loss) | Median logit | Skipped |", "|---|---|---|---|---|"]
    for key in ("primary", "eligible_only"):
        p = pbo[key]
        L.append(f"| {key} | {_f(p['pbo'])} | {_f(p['p_oos_loss'])} | {_f(p['median_logit'])} | {p['skipped']} |")
    d = dsr_out["ticks0"]
    L += ["", "## Deflated Sharpe", "",
          "Daily returns use fixed starting capital, idle days included, and are not annualized. The luck bar uses "
          "the search universe's Sharpe spread. Broader-N sensitivities reuse that spread as an assumption.", "",
          "| Version | N | Luck bar | DSR |", "|---|---|---|---|"]
    for key in ("primary", "variant_n", "strategy_n", "monthly"):
        x = d[key]
        L.append(f"| {key} | {x['n']} | {_f(x['sr0'], 4)} | {_f(x['dsr'])} |")
    L += ["", f"Daily Sharpe: {_f(d['stats']['sr'], 4)}. PSR above zero: {_f(d['psr0']['dsr'])}. "
          f"90% block-bootstrap Sharpe interval: {d['boot90']}. Identical paths: {pbo['identical_paths']}.", "",
          f"Raw files: `{out.relative_to(ROOT)}`. The statistical formula assumes independent returns; "
          "the block bootstrap checks sensitivity to dependence."]
    doc = doc_dir(name) / f"{tag}.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("\n".join(L) + "\n")
    return doc


def fold_totals(folds, select_ticks=SELECT_TICKS, scenarios=SCENARIOS) -> dict:
    """Sums of a fold table (rows with net0..2 and trades0): the walk-forward totals the report and the site show."""
    rows = folds.to_dict("records") if hasattr(folds, "to_dict") else list(folds)
    return {**{f"net{k}": float(sum(r[f"net{k}"] for r in rows)) for k in scenarios},
            f"trades{select_ticks}": int(sum(r[f"trades{select_ticks}"] for r in rows)),
            f"positive{select_ticks}": int(sum(r[f"net{select_ticks}"] > 0 for r in rows))}


def _wfe(folds) -> str:
    rs = [r for r in folds if r["trial"] is not None and r["train_years"]]
    if not rs:
        return "n/a"
    den = np.mean([r["train_obj"] / r["train_years"] for r in rs])
    if den <= 0:
        return "n/a (training result not positive)"
    return f"{np.mean([r['net0'] for r in folds]) / den:.2f}"
