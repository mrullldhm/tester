"""Price Reversal v2 study page: every hour's whole grid, US DST split, and the entry-cap / fixed-TP comparison
with a per-signal account of missed winners and avoided losers. Needs `python -m tvtester.cli test
price_reversal_v2` first (reads results/price_reversal_v2/*/grid.csv and trades_slippage0.csv).

    .venv/bin/python tools/run_limited.py tools/price_reversal_v2_study.py
"""
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from strategies import price_reversal_v2 as v2
from tvtester import metrics, report
from tvtester.config import DEFAULT
from tvtester.data import Bars, load_bars
from tvtester.engine import run

RES = ROOT / "results" / "price_reversal_v2"
DOC = ROOT / "docs" / "strategies" / "price_reversal_v2" / "study.md"
usd, pct, num = report.usd, report.pct, report.num


def us_dst(ts: pd.Series) -> pd.Series:
    """True where New York is on daylight saving time (UTC-4)."""
    et = ts.dt.tz_convert(v2.ET)
    return (et.dt.tz_localize(None) - ts.dt.tz_convert("UTC").dt.tz_localize(None)) == pd.Timedelta(hours=-4)


def malaysia_open(h: int) -> str:
    base = (18 + h - 1) % 24  # ET hour of the open
    return f"{(base + 12) % 24:02d}:00 / {(base + 13) % 24:02d}:00"


def hours_section() -> list[str]:
    rows = []
    for h in v2.HOURS:
        g = pd.read_csv(RES / h / "grid.csv")
        best = g.iloc[0]
        tf = pd.read_csv(RES / h / "trades_slippage0.csv", parse_dates=["signal_time"])
        dst = us_dst(tf["signal_time"])
        rows.append({"h": h, "g": g, "best": best, "tf": tf, "dst": dst})
    out = ["## 1. Hourly anchors (all available bars, 0 ticks)", "",
           "Each hour ran the same 64-setting FPR grid. **Median net** and **positive settings** describe the whole "
           "grid, so they are not inflated by picking the best of 64; **best net** is the in-sample top setting. "
           "The DST columns split the best setting's trades by US clock (summer = EDT, hour 1 opens 06:00 "
           "Malaysia; winter = EST, 07:00 Malaysia).", "",
           "| Hour | Opens ET | Opens Malaysia (US summer / winter) | Median net (64) | Positive settings | "
           "Best net | Best setting | Trades | PF | Max DD | US summer net | US winter net |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        g, b, tf, dst = r["g"], r["best"], r["tf"], r["dst"]
        k = int(r["h"][1:])
        out.append(f"| {k} | {(18 + k - 1) % 24:02d}:00 | {malaysia_open(k)} | {usd(g['net_profit'].median())} | "
                   f"{(g['net_profit'] > 0).sum()} / {len(g)} | {usd(b['net_profit'])} | "
                   f"w{b['window']} x{b['atr_mult']} {b['target']} | {int(b['total_closed_trades']):,} | "
                   f"{num(b['profit_factor'])} | {usd(b['max_equity_drawdown'])} | "
                   f"{usd(tf.loc[dst, 'profit'].sum())} ({int(dst.sum())}) | "
                   f"{usd(tf.loc[~dst, 'profit'].sum())} ({int((~dst).sum())}) |")
    med = pd.DataFrame({r["h"]: r["g"].groupby("target")["net_profit"].median() for r in rows}).T
    out += ["", "### Median net by target, per hour", "",
            "| Hour | " + " | ".join(med.columns) + " |", "|---" * (len(med.columns) + 1) + "|",
            *[f"| {int(h[1:])} | " + " | ".join(usd(v) for v in med.loc[h]) + " |" for h in med.index], ""]
    return out


def outcome(tf: pd.DataFrame) -> pd.Series:
    return pd.Series(np.where(tf["profit"] > 0, "W", "L"), index=tf["signal_bar"].to_numpy())


def entry_section(bars: Bars) -> list[str]:
    out = ["## 2. Entry cap and fixed TP on the FPR session baselines (all available bars)", "",
           "`cap 0 / default` is Fair Price Reversal unchanged. A cap N moves the limit to N ticks from the stop "
           "only when the signal close is further away; otherwise the entry is the signal close. Limits never "
           "slip; the 1 / 2 tick columns slip stops and session-end market exits only.", ""]
    for s, base in v2.ENTRY_BASE.items():
        res, sums = {}, {}
        for cap in v2.ENTRY_CAPS:
            for tp in v2.TP_MODES:
                p = dict(anchor=s, swing=1, entry_cap=cap, tp_mode=tp, **base)
                for k in (0, 1, 2):
                    strat = v2.PriceReversalV2(**p)
                    r = run(strat, bars, DEFAULT.with_slippage(k))
                    stops = strat.sig["stop"]
                    sums[(cap, tp, k)] = metrics.summary(r)
                    if k == 0:
                        res[(cap, tp)] = metrics.trade_frame(r)
        out += [f"### {s} (`window={base['window']}`, `atr_mult={base['atr_mult']}`, `target={base['target']}`)", "",
                "| Cap | TP | Net 0 / 1 / 2 ticks | Trades | % win | PF | Avg trade | Avg win | Avg loss | "
                "Largest loss | Max DD | Net / max DD |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for (cap, tp), tf in res.items():
            a, z = sums[(cap, tp, 0)]["all"], sums[(cap, tp, 0)]
            dd = z["max_equity_drawdown"]
            nets = " / ".join(usd(sums[(cap, tp, k)]["all"]["net_profit"]) for k in (0, 1, 2))
            out.append(f"| {cap or 'close'} | {tp} | {nets} | {a['total_closed_trades']:,} | {pct(a['percent_profitable'])} | "
                       f"{num(a['profit_factor'])} | {usd(a['avg_trade'])} | {usd(a['avg_winning_trade'])} | "
                       f"-{usd(a['avg_losing_trade'])} | -{usd(a['largest_losing_trade'])} | {usd(dd)} | "
                       f"{num(a['net_profit'] / dd if dd else float('nan'), 2)} |")
        base_tf = res[(0, "default")]
        bo = outcome(base_tf)
        bp = pd.Series(base_tf["profit"].to_numpy(), index=base_tf["signal_bar"].to_numpy())
        sb = base_tf["signal_bar"].to_numpy()
        risk = pd.Series(np.abs(bars.c[sb] - stops[sb]), index=sb)  # signal close to stop, ticks
        out += ["", "**What the cap changes, signal by signal** (against `close / default`, same TP mode = default). "
                "*Affected* = original trades whose stop was further than the cap. Net change = capped minus "
                "original profit on those signals.", "",
                "| Cap | Affected trades | Missed winners (not filled) | Avoided losers (not filled) | "
                "Loser -> winner | Winner -> loser | Still win / still lose | Net change from missed winners | "
                "Net change from avoided losers | Net change, all filled ones | New trades (no original) | "
                "Lost unaffected trades (blocked by a capped order) | Net change, total |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for cap in v2.ENTRY_CAPS[1:]:
            tf = res[(cap, "default")]
            no, np_ = outcome(tf), pd.Series(tf["profit"].to_numpy(), index=tf["signal_bar"].to_numpy())
            aff = risk.index[risk > cap]
            o_aff, n_aff = bo.reindex(aff), no.reindex(aff)
            missed = aff[(o_aff == "W") & n_aff.isna()]
            avoided = aff[(o_aff == "L") & n_aff.isna()]
            filled = aff[n_aff.notna()]
            l2w = ((o_aff == "L") & (n_aff == "W")).sum()
            w2l = ((o_aff == "W") & (n_aff == "L")).sum()
            same = ((o_aff == n_aff) & n_aff.notna()).sum()
            new = no.index.difference(bo.index)
            lost = bo.index.difference(aff).difference(no.index)
            parts = (-bp.reindex(missed).sum() - bp.reindex(avoided).sum()
                     + (np_.reindex(filled) - bp.reindex(filled)).sum() + np_.reindex(new).sum()
                     - bp.reindex(lost).sum())
            unaffected_kept = bo.index.difference(aff).intersection(no.index)
            parts += (np_.reindex(unaffected_kept) - bp.reindex(unaffected_kept)).sum()
            total = np_.sum() - bp.sum()
            if abs(parts - total) > 0.01:
                raise SystemExit(f"{s} cap {cap}: per-signal columns {parts:.2f} != net change {total:.2f}")
            out.append(f"| {cap} | {len(aff):,} | {len(missed):,} | {len(avoided):,} | {l2w:,} | {w2l:,} | {same:,} | "
                       f"-{usd(bp.reindex(missed).sum())} | +{usd(-bp.reindex(avoided).sum())} | "
                       f"{usd((np_.reindex(filled) - bp.reindex(filled)).sum())} | {len(new):,} "
                       f"({usd(np_.reindex(new).sum())}) | {len(lost):,} ({usd(-bp.reindex(lost).sum())}) | {usd(total)} |")
        out.append("")
    return out


def main() -> None:
    bars = Bars.from_frame(load_bars(None, None))
    lines = ["# Price Reversal v2: hour and entry study", "",
             f"Generated {datetime.now(UTC):%Y-%m-%d %H:%M} UTC by `tools/price_reversal_v2_study.py` "
             f"on {bars.ts[0]} to {bars.ts[-1]} ({len(bars):,} one-minute bars).", "",
             "> **In-sample, all available bars including the reserved 2024+ interval.** The hour table covers 23 x 64 "
             "= 1,472 settings and the entry table 3 x 16 = 48; the best of many looks better than it is. This page "
             "is for choosing what to test in feature 2 on the development interval, not a result.", "",
             "Properties: $50,000, 1 contract, $2.01 per order ($4.02 round trip), limit entries.", "",
             *hours_section(), *entry_section(bars)]
    DOC.write_text("\n".join(lines))
    print(f"wrote {DOC}")


if __name__ == "__main__":
    main()
