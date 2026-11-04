"""Exit study: breakeven / trailing stop / time exit rules swept on each variant's frozen feature-1 baseline.

    .venv/bin/python -m tvtester.cli exits fair_price_reversal [--jobs 6] [--variants ny]

- Interval: the feature-1 interval, frozen (START .. END exclusive), every bar incl. the reserved 2024+ bars
  (owner decision 2026-11-01). Not feature 2: exit winners picked here cannot be validated on 2024+.
- Baseline: mod.BASELINES[variant] (the feature-1 top combination) + mod.VARIANTS[variant], unchanged.
- Rules: tvtester.exits.study_rules() (396, fixed order, declared before the v2 runs). One engine run each, 0 ticks.
- Objective (declared first): net profit + open P&L at the end, 0 ticks ("net0", as feature 2, so a losing
  position left open cannot hide). Ties: profit factor (no losers ranks first), then rule order. No minimum-trade
  rule (the entries are fixed).
- Winners: the best rule of each family (exits.ExitRule.family) and the best overall (one of them). Each winner is
  rerun without added slippage; a winner is never re-picked from the final reports.
- Ledger: `exit_study_declared` (planned runs) before the runs; one `exit_study_run` / `exit_study_stress` event per
  engine run as it finishes (an interrupted study still counts them); `exit_study` closes the run (0 runs).
- Files: results/<name>/exits/<run_id>/<variant>/, never overwritten.
History: v1 (330 rules, T-fraction styles only) ran on fair_price_reversal (run 20261031T192917Z_a0dab0, no rule
beat any baseline) and part of supertrend_kalman (stopped); both are in the ledger and count as tries.
"""

import hashlib
import importlib
import json
import time
from dataclasses import asdict
from datetime import datetime, timezone

import pandas as pd
from joblib import Parallel, delayed

from . import experiment, metrics, report
from .config import DEFAULT, ROOT, SLIPPAGE_SCENARIOS
from .data import Bars, load_bars
from .engine import run
from .exits import COMBINED_BE, UNVERIFIED, ExitRule, study_rules
from .report import plt  # Agg backend set there

START, END = None, None  # same full available CL history as the current feature-1 run
OBJECTIVE = "net0 (net profit + open P&L at the end, 0 ticks)"
FAMILIES = ("be_touch", "be_close", "be_time", "trail_frac", "trail_atr", "trail_swing", "trail_step",
            "trail_close", "trail_ema", "trail_sar", "both", "time_exit")
FAMILY_TEXT = {
    "be_touch": "Breakeven when the high / low reaches be_x x T",
    "be_close": "Breakeven when a close reaches be_x x T",
    "be_time": "Breakeven after N bars if the close is in profit",
    "trail_frac": "Trail a fixed fraction of T behind the best price",
    "trail_atr": "Trail k x ATR(14) behind the best price (chandelier)",
    "trail_swing": "Trail at the last confirmed owner 1m swing low / high (fixed detection; TradingView export pending)",
    "trail_step": "Ratchet: lock one step behind every step of T reached",
    "trail_close": "Trail a fraction of T behind the best close",
    "trail_ema": "Trail at the 1m EMA while it is on the trade's side",
    "trail_sar": "Trail at the 1m Parabolic SAR while it is on the trade's side (UNVERIFIED SAR)",
    "both": "Every trailing rule with one of 3 declared breakevens: " + ", ".join(
        f"{s} {x:g}{'T' if s != 'time' else ' bars'} +{o}t" for s, x, o in COMBINED_BE),
    "time_exit": "Close at market after N bars in the trade",
}
CHUNKS = 28
_BARS: dict = {}


def _bars() -> Bars:
    if "b" not in _BARS:
        _BARS["b"] = Bars.from_frame(load_bars(START, END))
    return _BARS["b"]


def _config(mod, variant: str, rule: ExitRule) -> dict:
    return {**mod.VARIANTS[variant], **mod.BASELINES[variant], **rule.params()}


def _row(mod, variant: str, order: int, rule: ExitRule, bars: Bars) -> dict:
    s = mod.STRATEGY(**_config(mod, variant, rule))
    res = run(s, bars, DEFAULT)
    m = metrics.summary(res)
    a = m["all"]
    return {"order": order, "family": rule.family(), "rule": rule.label(), **asdict(rule),
            "objective": a["net_profit"] + m["open_pnl"], "net_profit": a["net_profit"], "open_pnl": m["open_pnl"],
            "total_closed_trades": a["total_closed_trades"], "percent_profitable": a["percent_profitable"],
            "profit_factor": a["profit_factor"], "avg_trade": a["avg_trade"],
            "max_equity_drawdown": m["max_equity_drawdown"], "sharpe_ratio": m["sharpe_ratio"],
            "trades_stop_moved": len(s.exits.moved), "trades_time_exit": _timed(res),
            "unverified": _unverified(rule)}


def _timed(res) -> int:
    """Closed trades that the time exit actually closed (a request on the last bar never fills)."""
    return sum(t.exit_id == "Time exit" for t in res.trades)


def _unverified(rule: ExitRule) -> bool:
    return rule.trail in UNVERIFIED


def _mark(rule_text: str, unverified) -> str:
    return rule_text + (" (unverified)" if bool(unverified) else "")


def _chunk(name: str, variant: str, orders: list[int], run_id: str) -> list[dict]:
    """Grid rows of rules `orders`; the engine runs are logged as soon as the chunk is done."""
    mod = importlib.import_module(f"strategies.{name}")
    rules = study_rules()
    bars = _bars()
    rows = []
    for n in orders:  # logged one engine run at a time: an interrupted study still counts every finished run
        rows.append(_row(mod, variant, n, rules[n], bars))
        experiment.log(name, "exit_study_run", 1, run_id=run_id, variant=variant, order=n, slippage=0)
    return rows


def rank(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["_pf"] = df["profit_factor"].fillna(float("inf")).where(df["total_closed_trades"] > 0, -1.0)
    df = df.sort_values(["objective", "_pf", "order"], ascending=[False, False, True]).drop(columns="_pf")
    return df.reset_index(drop=True)


def _stress(name: str, variant: str, order: int, run_id: str) -> dict:
    mod = importlib.import_module(f"strategies.{name}")
    rule = study_rules()[order]
    bars = _bars()
    out = {}
    for k in (0, *SLIPPAGE_SCENARIOS):
        s = mod.STRATEGY(**_config(mod, variant, rule))
        res = run(s, bars, DEFAULT.with_slippage(k))
        out[k] = {"summary": metrics.summary(res), "trades": metrics.trade_frame(res), "moved": len(s.exits.moved),
                  "timed": _timed(res)}
        experiment.log(name, "exit_study_stress", 1, run_id=run_id, variant=variant, order=order, slippage=k)
    return out


def _hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def cmd_exits(name: str, jobs: int = 1, variants: list[str] | None = None) -> str:
    mod = importlib.import_module(f"strategies.{name}")
    variants = variants or list(mod.VARIANTS)
    rules = study_rules()
    bars = _bars()
    prov = experiment.provenance(name, bars)
    prov["dev_interval"] = [str(bars.ts[0]), str(bars.ts[-1]), f"end exclusive {END}; FULL feature-1 interval"]
    grid_hash = _hash([r.params() for r in rules])
    run_id = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_{grid_hash[:6]}"
    for v in variants:
        experiment.log(name, "exit_study_declared", 0, run_id=run_id, variant=v, rules=len(rules),
                       planned_runs=len(rules) + (1 + len(SLIPPAGE_SCENARIOS)) * (len(FAMILIES) + 2),  # upper bound (winners dedup)
                       objective=OBJECTIVE, grid_hash=grid_hash,
                       baseline=_config(mod, v, ExitRule()), provenance=prov,
                       artifacts=f"results/{name}/exits/{run_id}/{v}")
    t0 = time.time()
    n = len(rules)
    k = min(CHUNKS, n)
    tasks = [(v, list(range(j, n, k))) for v in variants for j in range(k)]  # interleaved: even chunk cost
    parts = Parallel(n_jobs=jobs, verbose=5)(delayed(_chunk)(name, v, o, run_id) for v, o in tasks)
    rows = {v: [] for v in variants}
    for (v, _), r in zip(tasks, parts):
        rows[v] += r
    grids = {v: rank(rows[v]) for v in variants}
    print(f"  grid done in {time.time() - t0:.0f}s", flush=True)

    picks = {}
    for v, g in grids.items():
        roles = {"baseline": g[g["order"] == 0].iloc[0]}
        for fam in FAMILIES:
            roles[fam] = g[g["family"] == fam].iloc[0]
        roles["overall"] = g.iloc[0]
        picks[v] = roles
    uniq = sorted({(v, int(r["order"])) for v, roles in picks.items() for r in roles.values()})
    stressed = Parallel(n_jobs=jobs)(delayed(_stress)(name, v, o, run_id) for v, o in uniq)
    stress = dict(zip(uniq, stressed))
    for v in variants:  # engine runs were logged per chunk / stress: this event counts 0
        runs = len(rules) + (1 + len(SLIPPAGE_SCENARIOS)) * len({o for (vv, o) in uniq if vv == v})
        experiment.log(name, "exit_study", 0, run_id=run_id, runs_done=runs, variant=v, rules=len(rules),
                       objective=OBJECTIVE, grid_hash=grid_hash,
                       winners={k: int(r["order"]) for k, r in picks[v].items()},
                       best=picks[v]["overall"]["rule"], best_objective=float(picks[v]["overall"]["objective"]),
                       baseline_objective=float(picks[v]["baseline"]["objective"]),
                       code_hash=prov["code_hash"], data_hash=prov["data_hash"])
    return write(mod, name, variants, grids, picks, stress, rules, bars, prov, grid_hash, run_id)


# --- outputs ----------------------------------------------------------------------------------------------
_usd = report.usd


def _save(name: str, v: str, g: pd.DataFrame, picks: dict, stress: dict, run_id: str) -> None:
    out = ROOT / "results" / name / "exits" / run_id / v
    if out.exists():
        raise FileExistsError(f"{out} exists: a study run is never overwritten")
    out.mkdir(parents=True)
    g.to_csv(out / "grid.csv", index=False)
    summ = {}
    for role, r in picks.items():
        o = int(r["order"])
        summ[role] = {"order": o, "rule": r["rule"], "family": r["family"], "unverified": bool(r["unverified"]),
                      **{f"slippage_{k}": x["summary"] for k, x in stress[(v, o)].items()}}
    (out / "summary.json").write_text(json.dumps(summ, indent=2, default=str))
    best = stress[(v, int(picks["overall"]["order"]))]
    for k, x in best.items():
        x["trades"].to_csv(out / f"best_trades_slippage{k}.csv", index=False)


def _png(v: str, title: str, picks: dict, stress: dict, path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4), dpi=110)
    cap = DEFAULT.initial_capital
    for role, style in (("baseline", {"lw": 1.0, "color": "#888"}), ("overall", {"lw": 1.3, "color": "#1f77b4"})):
        o = int(picks[role]["order"])
        for k, ls in ((0, "-"),):
            tf = stress[(v, o)][k]["trades"]
            if tf.empty:
                continue
            lab = ("baseline (no exit rule)" if role == "baseline" else f"best: {picks[role]['rule']}") + f", {k} tick"
            ax.plot(tf["exit_time"], cap + tf["cum_profit"], ls=ls, label=lab, **style)
    ax.axhline(cap, color="#bbb", lw=0.6, ls="--")
    ax.set_title(title)
    ax.set_ylabel("Closed-trade equity (USD)")
    ax.grid(alpha=0.25)
    ax.legend(loc="best", fontsize=7)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def write(mod, name, variants, grids, picks, stress, rules, bars, prov, grid_hash, run_id) -> str:
    doc_dir = ROOT / "docs" / "strategies" / name / "exits"
    doc_dir.mkdir(parents=True, exist_ok=True)
    n = len(rules)
    nf = {f: sum(r.family() == f for r in rules) for f in FAMILIES}
    sl = (0, *SLIPPAGE_SCENARIOS)

    def nets(v, o):
        return " / ".join(_usd(stress[(v, o)][k]["summary"]["all"]["net_profit"]) for k in sl)

    def opens(v, o):
        return " / ".join(_usd(stress[(v, o)][k]["summary"]["open_pnl"]) for k in sl)

    lines = [
        f"# {mod.TITLE}: exit study (breakeven, trailing stop, time exit)", "",
        f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC by `python -m tvtester.cli exits {name}`.", "",
        "> **Read this first.** Exploratory **in-sample** exit sweep. Each variant's feature-1 top combination is "
        f"frozen and only the exit rule changes. The best rule is the **best of {n}** tries per variant (each family "
        "below says its own N), conditional on baselines that were themselves the best of the feature-1 grid, and "
        "after an earlier 330-rule version of this study (ledger). The interval is the full feature-1 interval, "
        "**including the reserved 2024+ bars**, so these exit winners cannot be validated on 2024+. Only the baseline is run, with commission and no added slippage.", "",
        "## Settings", "",
        "| Setting | Value |", "|---|---|",
        f"| Data | {bars.ts[0]} to {bars.ts[-1]} UTC, {len(bars):,} bars (data hash `{prov['data_hash']}`, code hash "
        f"`{prov['code_hash']}`, grid hash `{grid_hash}`) |",
        "| Properties | as feature 1: $50,000, 1 contract, $2.01 per order ($4.02 round trip), no added slippage |",
        f"| Objective (declared first) | {OBJECTIVE}; ties: profit factor, then rule order |",
        "| Baseline | the variant's feature-1 top combination, unchanged (entries, initial stop and target) |",
        f"| Run | `{run_id}` (ledger `results/{name}/ledger.jsonl`; files never overwritten) |", "",
        "## Exit rules", "",
        "Units: **T** = the trade's target distance in ticks (rr x signal risk). All rules run at every 1-minute bar "
        "close while in a position; a moved stop works from the next bar, a time exit fills at the next open. "
        "**best** = most favourable high (long) / low (short) since the entry bar. A stop never loosens. Trailing "
        "rules come with the target kept or removed, and most start either at once or after 0.5T. Full rules: "
        "`docs/ENGINE.md` (Exit management) and `tvtester/exits.py`.", "",
        "| Family | Rule | Rules |", "|---|---|---|",
        *[f"| `{f}` | {FAMILY_TEXT[f]} | {nf[f]} |" for f in FAMILIES],
        f"| | **Total (with the baseline)** | **{n}** |", "",
        f"Every rule that trails with {' or '.join(f'`{u}`' for u in UNVERIFIED)} (their own families and the matching "
        "`both` rules, marked **(unverified)** below) uses the owner swing twin / Pine `ta.sar` that "
        "have **not been checked against a TradingView export** yet.", "",
        "Breakeven is a stop price, not a guaranteed result: a gap can fill worse, and "
        "the round trip still costs $4.02 (1 tick offset = $10).", "",
        "## Summary: best rule per variant", "",
        "| Variant | Baseline net | Best rule (of " + str(n) + ") | Family | Best net | Rules beating the baseline |", "|---|---|---|---|---|---|",
    ]
    for v in variants:
        g, p = grids[v], picks[v]
        b, o = int(p["baseline"]["order"]), int(p["overall"]["order"])
        beat = int((g["objective"] > p["baseline"]["objective"]).sum())
        lines.append(f"| {v} | {nets(v, b)} | {_mark(p['overall']['rule'], p['overall']['unverified'])} | "
                     f"{p['overall']['family']} | {nets(v, o)} | "
                     f"{beat} of {n - 1} |")
    lines.append("")
    for v in variants:
        g, p = grids[v], picks[v]
        _save(name, v, g, p, stress, run_id)
        png = doc_dir / f"equity_{v}.png"
        _png(v, f"{mod.TITLE}: {v}, exit study", p, stress, png)
        res_dir = ROOT / "results" / name / "exits" / run_id / v
        base = p["baseline"]["objective"]
        lines += [
            f"## Variant: {v}", "",
            "**Frozen baseline:** " + ", ".join(f"`{k}={x}`" for k, x in _config(mod, v, ExitRule()).items()), "",
            f"![Closed-trade equity: baseline vs best rule]({png.name})", "",
            "Chart: closed trades only (an open position at the end is in the Open P&L column).", "",
            f"Files: [grid]({report.rel(res_dir / 'grid.csv', doc_dir)}), "
            f"[summary]({report.rel(res_dir / 'summary.json', doc_dir)}), best rule trades "
            + ", ".join(f"[{k} ticks]({report.rel(res_dir / f'best_trades_slippage{k}.csv', doc_dir)})" for k in sl),
            "",
            "### Best rule of each family", "",
            "| Family | Best rule | Best of | Net profit | Open P&L at the end | Trades "
            "| % profitable | PF | Avg trade | Max DD | Trades with stop moved / closed by time exit | Family rules beating "
            "the baseline |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for role in ("baseline", *FAMILIES, "overall"):
            r = p[role]
            o = int(r["order"])
            x0 = stress[(v, o)][0]
            s0 = x0["summary"]
            of = {"baseline": 1, "overall": n}.get(role, nf.get(role))
            fam_beat = "" if role in ("baseline", "overall") else \
                f"{int((g[g['family'] == role]['objective'] > base).sum())} of {nf[role]}"
            lines.append(
                f"| {'**overall**' if role == 'overall' else role} | {_mark(r['rule'], r['unverified'])} | {of} | "
                f"{nets(v, o)} | "
                f"{opens(v, o)} | {s0['all']['total_closed_trades']:,} | {report.pct(s0['all']['percent_profitable'])} "
                f"| {report.num(s0['all']['profit_factor'])} | {_usd(s0['all']['avg_trade'])} | "
                f"{_usd(s0['max_equity_drawdown'])} | {x0['moved']:,} / {x0['timed']:,} | {fam_beat} |")
        top = g.head(10)
        lines += ["", f"### Top 10 of {n} (0 ticks)", "",
                  "| # | Rule | Family | Objective | Trades | % profitable | PF | Max DD |",
                  "|---|---|---|---|---|---|---|---|",
                  *[f"| {i} | {_mark(r['rule'], r['unverified'])} | {r['family']} | {_usd(r['objective'])} | "
                    f"{int(r['total_closed_trades']):,} | {report.pct(r['percent_profitable'])} | "
                    f"{report.num(r['profit_factor'])} | {_usd(r['max_equity_drawdown'])} |"
                    for i, (_, r) in enumerate(top.iterrows(), 1)],
                  "", f"Rules with a positive objective: {(g['objective'] > 0).sum()} of {n}. Rules beating the "
                  f"baseline: {(g['objective'] > base).sum()} of {n - 1}.", ""]
    path = doc_dir / "README.md"
    path.write_text("\n".join(lines))
    return str(path)
