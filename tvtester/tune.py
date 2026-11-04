"""Feature 2 commands: `features` (association report), `search`, `replay` (frozen configuration).

All three read only the development interval (tvtester/experiment.py) and log to the strategy's ledger.
docs/OPTIMIZE.md has the protocol.
"""

import importlib
import json
import time
from datetime import datetime, timezone

import pandas as pd

from . import associate, experiment, metrics, report, search
from .config import DEFAULT, ROOT
from .engine import run

CONFIG_DIR = ROOT / "strategies" / "configs"


def doc_dir(name: str):
    """Every readable feature-2 document of a strategy lives here; results/ keeps only raw data."""
    return ROOT / "docs" / "strategies" / name / "optimize"
IN_SAMPLE = ("> **In-sample.** Development interval only (bars before {end} UTC). {extra}Nothing here shows a "
             "tradable edge: out-of-sample validation is a later feature.")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")


def _usd(x) -> str:
    return report.usd(x) if x is not None and x == x else "—"


# --- features --------------------------------------------------------------------------------------------
def cmd_features(name: str, variant: str) -> str:
    mod = importlib.import_module(f"strategies.{name}")
    bars = experiment.dev_bars()
    params = {**mod.VARIANTS[variant], **mod.BASELINES[variant]}
    out = ROOT / "results" / name / "features" / variant
    out.mkdir(parents=True, exist_ok=True)
    doc = doc_dir(name) / f"features_{variant}.md"
    lines = [f"# {mod.TITLE}: feature association, {variant}", "",
             f"Generated {_now()} UTC by `python -m tvtester.cli features {name} --variant {variant}`.", "",
             IN_SAMPLE.format(end=experiment.DEV_END, extra=""), "",
             "> **Descriptive only.** A bucket shows the baseline trades whose feature value fell in it. It is not "
             "what a filter would earn: removing trades can let in others the baseline never took. Intervals: 90% "
             "block bootstrap of the average trade by ISO week, not adjusted for picking the best bucket out of "
             "many.", "",
             f"Baseline (feature-1 top combination): {', '.join(f'`{k}={v}`' for k, v in params.items())}. "
             f"Bars: {bars.ts[0]} to {bars.ts[-1]} ({len(bars):,}).", ""]
    feats = list(getattr(mod, "FEATURES", ()))
    experiment.log(name, "association", len(search.SCENARIOS), variant=variant, params=params, doc=str(doc.relative_to(ROOT)),
                   features=feats, code_hash=experiment.provenance(name, bars)["code_hash"])  # logged before running
    for k in search.SCENARIOS:
        tf = associate.trade_features(mod, params, bars, k)
        tf.to_csv(out / f"trades_features_slippage{k}.csv", index=False)
        lines += [f"## Baseline, commission included: {len(tf):,} trades, net {_usd(tf['profit'].sum())}",
                  ""]
        for ft, cat in [(f, False) for f in feats] + [("direction", True), ("weekday", True)]:
            b = associate.buckets(tf, ft, cat, seed=k)
            head = f"### `{ft}`" + (f" ({mod.STRATEGY(**params).report_tz} clock)" if ft == "weekday" else "")
            lines += [head, "", "| Bucket | Trades | % profitable | Avg trade | 90% interval | Net profit |",
                      "|---|---|---|---|---|---|"]
            for _, r in b.iterrows():
                lines.append(f"| {r['bucket']} | {r['trades']:,} | {report.pct(r['percent_profitable'])} | "
                             f"{_usd(r['avg_trade'])} | {_usd(r['avg_lo90'])} .. {_usd(r['avg_hi90'])} | "
                             f"{_usd(r['net_profit'])} |")
            lines.append("")
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("\n".join(lines))
    return str(doc)


# --- search ----------------------------------------------------------------------------------------------
def cmd_search(name: str, variant: str, space_name: str, sampler: str, trials: int, objective: str, seed: int,
               jobs: int, run_tag: str = "") -> str:
    if objective not in experiment.OBJECTIVES:
        raise SystemExit(f"objective must be one of {list(experiment.OBJECTIVES)}")
    mod = importlib.import_module(f"strategies.{name}")
    space = search.space_of(mod, variant, space_name)
    run_id = experiment.tagged_run_id(f"{variant}_{space_name}_{sampler}_{objective}_s{seed}_n{trials}", run_tag)
    out = ROOT / "results" / name / "search" / run_id
    if out.exists():
        raise SystemExit(f"{out} already exists: a search id is used once (an interrupted run is not resumed; "
                         "its evaluations.jsonl and the ledger's search_start event record what it spent)")
    out.mkdir(parents=True)
    bars = search._bars()
    prov = experiment.provenance(name, bars)
    meta = {"strategy": name, "variant": variant, "space_name": space_name, "space": space, "sampler": sampler,
            "trials": trials, "objective": objective, "seed": seed, "jobs": jobs,
            "min_trades": experiment.MIN_TRADES, "started_utc": _now(), **prov}
    (out / "run.json").write_text(json.dumps(meta, indent=2, default=str))
    experiment.log(name, "search_start", 0, run_id=run_id, planned_trials=trials)
    t0 = time.time()
    evals = out / "evaluations.jsonl"  # every finished engine-run triple, written as it completes
    claimed = [0]

    def claim(new_cfgs, what="trials"):
        """Ledger first, engine after: an interruption over-counts engine runs, never under-counts."""
        n = len(search.SCENARIOS) * len(new_cfgs)
        if n:
            experiment.log(name, "search_batch", n, run_id=run_id, part=what, configurations=len(new_cfgs))
            claimed[0] += n

    def progress(n_done, new_rows, new_cfgs):
        with evals.open("a") as f:
            for c, r in zip(new_cfgs, new_rows):
                f.write(json.dumps({"config": c, "row": r}, default=float) + "\n")
        print(f"  {run_id}: {n_done}/{trials} trials, {search.elapsed(t0)}", flush=True)

    if sampler == "random":
        cfgs = search.draw_random(space, trials, seed)
        rows = []
        step = max(1, jobs) * 8
        for i in range(0, len(cfgs), step):
            claim(cfgs[i:i + step])
            part = search.run_configs(name, cfgs[i:i + step], jobs)
            rows += part
            progress(len(rows), part, cfgs[i:i + step])
        dups = [False] * len(cfgs)
    elif sampler == "tpe":
        cfgs, rows, dups = search.run_tpe(name, space, out, trials, seed, objective, jobs, progress, claim)
    else:
        raise SystemExit("sampler must be random or tpe")
    df = search.rank(search.table(cfgs, rows, space["base"], dups), objective)
    df.to_csv(out / "trials.csv", index=False)
    print(f"  {run_id}: {len(df)} trials in {search.elapsed(t0)}", flush=True)

    best = df.iloc[0]
    winner = json.loads(best["config"]) if bool(best["eligible"]) else None
    nb_df = pd.DataFrame()
    if winner is not None:
        nbs = search.neighbours(winner, space)
        claim(nbs, "neighbours")
        nb_rows = search.run_configs(name, nbs, jobs)
        nb_df = search.rank(search.table(nbs, nb_rows, space["base"]), objective)
        nb_df.to_csv(out / "neighbours.csv", index=False)
    cfg_path = None
    if winner is not None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        cfg_path = CONFIG_DIR / f"{name}_{run_id}.json"
        cfg_path.write_text(json.dumps({
            "strategy": name, "variant": variant, "execution_version": experiment.EXECUTION_VERSION, **winner, "interval": [experiment.DEV_START, experiment.DEV_END],
            "source": {"search": str(out.relative_to(ROOT)), "trial": int(best["trial"]), "objective": objective},
            "expected": {f"{m}{k}": (int(best[f"{m}{k}"]) if m == "trades" else float(best[f"{m}{k}"]))
                         for m in ("net", "open", "trades") for k in search.SCENARIOS} | {"objective": float(best["objective"])},
        }, indent=2, default=float))
    doc = write_search_report(out, meta, df, nb_df, winner, cfg_path, claimed[0])
    experiment.log(name, "search", 0, engine_runs=claimed[0], run_id=run_id, variant=variant, space=space_name, sampler=sampler,
                   objective=objective, seed=seed, trials=len(df), duplicates=int(df["duplicate"].sum()),
                   eligible=int(df["eligible"].sum()), winner=None if winner is None else best["label"],
                   code_hash=prov["code_hash"], data_hash=prov["data_hash"])
    return str(doc)


def _trial_rows(df: pd.DataFrame, n: int) -> list[str]:
    out = ["| # | Trial | Configuration | Net profit | Trades | % profitable | PF | Max DD | Eligible |",
           "|---|---|---|---|---|---|---|---|---|"]
    for i, (_, r) in enumerate(df.head(n).iterrows(), 1):
        out.append(f"| {i} | {r['trial']} | {r['label']} | {_usd(r['net0'])} | {int(r['trades0']):,} | "
                   f"{report.pct(r['win0'])} | {search.fmt_pf(r['pf0'])} | {_usd(r['dd0'])} | "
                   f"{'yes' if r['eligible'] else 'no'} |")
    return out


def write_search_report(out, meta, df, nb_df, winner, cfg_path, n_eval) -> None:
    k = experiment.OBJECTIVES[meta["objective"]]
    base = df[df["trial"] == 0]  # trial 0 is the baseline; a sampler may suggest the same configuration again later
    lines = [f"# Search {out.name}", "",
             f"Generated {_now()} UTC. Strategy `{meta['strategy']}`, variant `{meta['variant']}`, space "
             f"`{meta['space_name']}`, sampler `{meta['sampler']}`, seed {meta['seed']}, objective "
             f"`{meta['objective']}` (net profit + open P&L without added slippage), at least "
             f"{meta['min_trades']} closed trades.", "",
             IN_SAMPLE.format(end=experiment.DEV_END,
                              extra=f"The winner is the best of {len(df)} trials ({int(df['duplicate'].sum())} "
                                    f"duplicates) and {len(nb_df)} neighbours: {n_eval} engine runs. "), "",
             "## Baseline vs winner", ""]
    lines += _trial_rows(pd.concat([base, df.head(1)]).drop_duplicates("trial"), 2)
    if winner is None:
        lines += ["", "**No eligible trial.** No configuration reached the minimum trade count."]
    else:
        lines += ["", f"Frozen configuration: `{cfg_path.relative_to(ROOT)}`. Replay it with "
                      f"`python -m tvtester.cli replay {cfg_path.relative_to(ROOT)}`.", "",
                  "## Neighbours of the winner (diagnostic, never candidates)", "",
                  "Each searched parameter one step either way, each filter switched off, each threshold one step "
                  "either way. A winner whose neighbours collapse is a spike, not a plateau.", ""]
        lines += _trial_rows(nb_df, len(nb_df))
        obj = nb_df["objective"] if len(nb_df) else pd.Series(dtype=float)
        lines += ["", (f"Neighbour objective: median {_usd(obj.median())}, worst {_usd(obj.min())}, "
                       f"{int((obj > 0).sum())} of {len(obj)} above zero; winner {_usd(df.iloc[0]['objective'])}.")
                  if len(obj) else "No neighbours (the winner has no searched parameter or filter to move)."]
    lines += ["", "## Top 20 trials", ""] + _trial_rows(df, 20)
    lines += ["", f"Eligible trials: {int(df['eligible'].sum())} of {len(df)}. Trials with objective above zero: "
                  f"{int(((df['objective'] > 0) & df['eligible']).sum())}.", "",
              f"Raw files in `{out.relative_to(ROOT)}/`: `trials.csv` (every trial, baseline metrics), "
              "`neighbours.csv`, `run.json` (space, hashes, versions)."]
    doc = doc_dir(meta["strategy"]) / f"search_{out.name}.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("\n".join(lines) + "\n")
    return doc


# --- replay ----------------------------------------------------------------------------------------------
def cmd_replay(cfg_file: str) -> str:
    path = (ROOT / cfg_file) if not cfg_file.startswith("/") else __import__("pathlib").Path(cfg_file)
    cfg = json.loads(path.read_text())
    if cfg["interval"] != [experiment.DEV_START, experiment.DEV_END]:
        raise SystemExit(f"configuration interval {cfg['interval']} is not the development interval "
                         f"{[experiment.DEV_START, experiment.DEV_END]}: feature 2 replays only that interval")
    experiment.check_execution(cfg)
    name, variant = cfg["strategy"], cfg["variant"]
    mod = importlib.import_module(f"strategies.{name}")
    bars = experiment.dev_bars()
    tag = path.stem.removeprefix(f"{name}_")
    experiment.log(name, "replay", 2 * len(search.SCENARIOS), config=str(path.relative_to(ROOT)),
                   data_hash=experiment.provenance(name, bars)["data_hash"])  # logged before running
    results = {k: run(mod.STRATEGY(**cfg["params"], filters=cfg["filters"]), bars, DEFAULT.with_slippage(k))
               for k in search.SCENARIOS}
    base_p = {**mod.VARIANTS[variant], **mod.BASELINES[variant]}
    base = {k: metrics.summary(run(mod.STRATEGY(**base_p), bars, DEFAULT.with_slippage(k))) for k in search.SCENARIOS}
    out = ROOT / "results" / name / "replay" / tag
    out.mkdir(parents=True, exist_ok=True)
    sums = {}
    for k, res in results.items():
        sums[k] = metrics.summary(res)
        metrics.trade_frame(res).to_csv(out / f"trades_slippage{k}.csv", index=False)
    (out / "summary.json").write_text(json.dumps({f"slippage_{k}": v for k, v in sums.items()}, indent=2, default=str))
    exp = cfg.get("expected", {})
    obj_k = experiment.OBJECTIVES[cfg["source"]["objective"]]
    match = (all(abs(sums[k]["all"]["net_profit"] - exp[f"net{k}"]) < 1e-6
                 and abs(sums[k]["open_pnl"] - exp[f"open{k}"]) < 1e-6
                 and sums[k]["all"]["total_closed_trades"] == exp[f"trades{k}"] for k in search.SCENARIOS)
             and abs(sums[obj_k]["all"]["net_profit"] + sums[obj_k]["open_pnl"] - exp["objective"]) < 1e-6) if exp else None
    png = doc_dir(name) / f"winner_{tag}.png"
    report.equity_png(results, png, f"{mod.TITLE}: {variant} {tag} (in-sample)")
    tf0 = metrics.trade_frame(results[0])
    filt = ", ".join(f"`{f} {'>=' if o == 'min' else '<='} {t:g}`" for f, o, t in cfg["filters"]) or "none"
    lines = [f"# {mod.TITLE}: optimized `{variant}` ({tag})", "",
             f"Generated {_now()} UTC by `python -m tvtester.cli replay {path.relative_to(ROOT)}`.", "",
             IN_SAMPLE.format(end=experiment.DEV_END, extra=f"Picked by search `{cfg['source']['search']}` "
                              f"(trial {cfg['source']['trial']}, objective `{cfg['source']['objective']}`); see its "
                              "report for how many trials it took. "), "",
             f"**Parameters:** {', '.join(f'`{k}={v}`' for k, v in cfg['params'].items())}", "",
             f"**Filters:** {filt}", "",
             f"Replay matches the search trial: **{'yes' if match else 'NO' if match is False else 'n/a'}**.", "",
             f"![Equity curve](winner_{tag}.png)", "",
             "## Against the baseline (same interval, same costs)", "",
             "| Scenario | Baseline net | Optimized net | Baseline trades | Optimized trades | Baseline PF | "
             "Optimized PF | Baseline max DD | Optimized max DD |", "|---|---|---|---|---|---|---|---|---|"]
    for k in search.SCENARIOS:
        b, o = base[k], sums[k]
        lines.append(f"| {k} tick{'s' if k != 1 else ''} | {_usd(b['all']['net_profit'])} | "
                     f"{_usd(o['all']['net_profit'])} | {b['all']['total_closed_trades']:,} | "
                     f"{o['all']['total_closed_trades']:,} | {search.fmt_pf(b['all']['profit_factor'])} | "
                     f"{search.fmt_pf(o['all']['profit_factor'])} | {_usd(b['max_equity_drawdown'])} | "
                     f"{_usd(o['max_equity_drawdown'])} |")
    lines += ["", "## Results after commission", "", report.full_report(sums[0], tf0, level=3),
              "### By year (extra)", "", report.by_year(tf0), ""]
    for k in search.SCENARIOS[1:]:
        lines += [f"## {k} tick{'s' if k > 1 else ''} slippage", "",
                  report.full_report(sums[k], metrics.trade_frame(results[k]), level=3)]
    doc = doc_dir(name) / f"winner_{tag}.md"
    doc.write_text("\n".join(lines))
    print(f"  replay matches search trial: {match}")
    return str(doc)
