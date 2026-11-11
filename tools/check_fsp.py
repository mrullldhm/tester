"""Independent FSP ledger / fill audit. Does NOT import tvtester or strategies or detect swings.

Uses saved signals as inputs, raw CL parquet bars for execution, and integer cents for P&L.
Run through tools/run_limited.py --jobs 1 after a completed baseline.
"""
import argparse
from datetime import date, timedelta
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def ticks(value):
    return int((Decimal(str(value)) * 100).to_integral_value())


def session_close_minute(d):
    """Independent cutoff calculation for the performance interval ending in 2023."""
    assert 2010 <= d.year <= 2023
    y = d.year
    def nth(month, weekday, n):
        first = date(y, month, 1)
        return first + timedelta(days=(weekday-first.weekday()) % 7 + 7*(n-1))
    def observed(v):
        return v + timedelta(days=-1 if v.weekday()==5 else 1 if v.weekday()==6 else 0)
    memorial = date(y, 5, 31)
    memorial -= timedelta(days=memorial.weekday())
    holidays = {nth(1,0,3), nth(2,0,3), memorial, observed(date(y,7,4)), nth(9,0,1), nth(11,3,4)}
    cutoff = 13*60 if y < 2022 and d in holidays else 14*60+30
    if d == nth(11,3,4)+timedelta(days=1) or (d.month==12 and d.day==24 and d.weekday()<4):
        cutoff = min(cutoff, 13*60+45)
    return cutoff


def main():
    import numpy as np
    import pandas as pd

    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, choices=[1], default=1)
    ap.add_argument("run", type=Path)
    a = ap.parse_args()
    out = a.run.resolve()
    status = json.loads((out / "status.json").read_text())
    assert status["status"] == "complete"
    summary = json.loads((out / "summary.json").read_text())
    provenance = json.loads((out / "provenance.json").read_text())
    target_ticks = int(provenance["parameters"]["tp"])
    halt_reopen = status.get("lifecycle") == "ny_session_first_mss_halt_v5"
    first_mss = halt_reopen or status.get("lifecycle") == "ny_session_flat_first_mss_v4"
    session_flat = first_mss or status.get("lifecycle") == "ny_session_flat_mss15_v3"
    mss15 = session_flat or status.get("lifecycle") == "ny_entries_daily_flat_mss15_v2"
    daily_flat = session_flat or status.get("lifecycle") in ("ny_entries_daily_flat_v1", "ny_entries_daily_flat_mss15_v2")
    trades = pd.read_csv(out / "trades.csv")
    signals = pd.read_csv(out / "signals.csv")
    setups = pd.read_csv(out / "setups.csv").set_index("id")
    signals["direction"] = signals.direction.astype(int)
    by_signal = {}
    for r in signals.itertuples():
        by_signal.setdefault((int(r.bar), int(r.direction)), r)
    if first_mss:
        assert not signals.setup.duplicated().any(), "multiple MSS opportunities for one setup"
        for s in signals.itertuples():
            assert int(setups.loc[int(s.setup)].first_signal) == int(s.bar)
        orders = pd.read_csv(out / "orders.csv")
        placed = orders[orders.action == "place"]
        assert not placed.signal_bar.duplicated().any(), "replayed entry opportunity"
    lo = pd.Timestamp(status["start"], tz="UTC") if status["start"] else None
    hi = pd.Timestamp(status["end_exclusive"], tz="UTC")
    paths = [p for p in sorted((ROOT / "data" / "cl1").glob("year=*.parquet"))
             if int(p.stem[5:]) <= hi.year and (lo is None or int(p.stem[5:]) >= lo.year)
             and not (int(p.stem[5:]) == hi.year and hi == pd.Timestamp(year=hi.year, month=1, day=1, tz="UTC"))]
    data = pd.concat([pd.read_parquet(p, columns=["ts", "open", "high", "low", "close", "raw_symbol"])
                      for p in paths], ignore_index=True)
    data = data[data.ts < hi]
    if lo is not None:
        data = data[data.ts >= lo]
    data = data.sort_values("ts").reset_index(drop=True)
    ts = pd.DatetimeIndex(data.ts)
    local = ts.tz_convert("America/New_York")
    local_mod = np.asarray(local.hour * 60 + local.minute)
    # Observed normal-session closing minutes provide an independent stale-setup check.
    # Early holiday deadlines are separately covered by clock regression checks.
    ny_closes = np.flatnonzero(local_mod == 14 * 60 + 29)
    trade_dates = np.asarray([t.date() + pd.Timedelta(days=int(t.hour >= 18)) for t in local]) if daily_flat else None
    prices = np.rint(data[["open", "high", "low", "close"]].to_numpy() * 100).astype(np.int64)
    hour = ts.floor("h")
    hours = data.assign(hour=hour).groupby("hour", sort=True).agg(high=("high", "max"), low=("low", "min"))
    prev_hi = np.rint(hours.high.shift().reindex(hour).to_numpy() * 100)
    prev_lo = np.rint(hours.low.shift().reindex(hour).to_numpy() * 100)
    symbols = data.raw_symbol.to_numpy()
    pnl_cents = []
    traded_setups = set()
    for row in trades.itertuples():
        side = 1 if row.type == "Long" else -1
        sb = int(row.signal_bar)
        signal = by_signal[sb, side]
        setup = setups.loc[int(signal.setup)]
        if first_mss:
            assert int(signal.setup) not in traded_setups, "repeated trade from one failed setup"
            traded_setups.add(int(signal.setup))
        assert int(signal.structure_bar) >= int(setup.touch)
        assert sb > int(setup.ready) and int(signal.stop_bar) <= sb
        limit, stop = int(signal.limit), int(signal.stop)
        assert 0 < side * (limit - stop) <= 25
        setup_side = int(setup.direction)
        cancel_upper = setup_side == -1
        entry_idx = ts.get_loc(pd.Timestamp(row.entry_time))
        exit_idx = ts.get_loc(pd.Timestamp(row.exit_time))
        entry_px, exit_px = ticks(row.entry_price), ticks(row.exit_price)
        deadline = None
        reopening_exit = halt_reopen and row.exit_signal == "New York halt reopen"
        if halt_reopen:
            entry_day = local[entry_idx].date()
            deadline = (pd.Timestamp(entry_day).tz_localize("America/New_York")
                        + pd.Timedelta(minutes=session_close_minute(entry_day))).tz_convert("UTC")
        assert entry_idx > sb
        if mss15:
            # Source the frozen boundary independently from the raw containing confirmation candle.
            duration = int(provenance["parameters"]["confirmation"].removesuffix("m"))
            bucket = ts[int(setup.touch)].floor(f"{duration}min")
            # Sorted raw bars: slice the original candle without rescanning the full history per trade.
            first = ts.searchsorted(bucket)
            last = ts.searchsorted(bucket + pd.Timedelta(minutes=duration))
            part = prices[first:last]
            assert int(setup.confirmation_high) == int(part[:, 1].max())
            assert int(setup.confirmation_low) == int(part[:, 2].min())
            after = prices[int(setup.confirmation_end) + 1:sb + 1]
            if setup_side == -1:
                assert after[:, 1].max() < int(setup.confirmation_high), (row.trade, "MSS after 15m high touch")
            else:
                assert after[:, 2].min() > int(setup.confirmation_low), (row.trade, "MSS after 15m low touch")
        if daily_flat:
            assert 9 * 60 <= local_mod[entry_idx] < 14 * 60 + 30, (row.trade, "entry outside New York")
            if not reopening_exit:
                assert trade_dates[entry_idx] == trade_dates[exit_idx], (row.trade, "overnight carry")
            if not session_flat:
                assert trade_dates[int(setup.touch)] == trade_dates[sb], (row.trade, "stale daily setup")
        if session_flat:
            if reopening_exit:
                assert exit_idx == ts.searchsorted(deadline), (row.trade, "not the first reopening bar")
                assert deadline-pd.Timedelta(minutes=1) not in ts, (row.trade, "cutoff bar was tradable")
                assert exit_px == int(prices[exit_idx,0]), (row.trade, "halt exit not at opening price")
            else:
                assert local_mod[exit_idx] < 14 * 60 + 30, (row.trade, "position survived New York close")
                assert local[entry_idx].date() == local[exit_idx].date(), (row.trade, "overnight carry")
                if deadline is not None:
                    assert ts[exit_idx] < deadline, (row.trade, "missed earlier exchange close")
            assert ny_closes.searchsorted(sb) == ny_closes.searchsorted(int(setup.touch)), (row.trade, "setup crossed NY reset")
        assert entry_px <= limit if side == 1 else entry_px >= limit
        actual_entry = actual_exit = None
        found_entry = False
        for i in range(sb + 1, exit_idx + 1):
            o, h, l, c = map(int, prices[i])
            if halt_reopen and found_entry and ts[i] >= deadline:
                assert reopening_exit, (row.trade, "missing overdue market exit")
                actual_exit = i, o, "close"
                break
            path = [o, h, l, c] if h - o < o - l else [o, l, h, c]
            target = None if not found_entry else actual_entry[1] + side * target_ticks
            if not found_entry:
                if daily_flat:
                    assert 9 * 60 <= local_mod[i] < 14 * 60 + 30, (row.trade, "pending limit survived session end")
                if not mss15:
                    assert pd.isna(setup.end) or i <= int(setup.end), (row.trade, "expired before fill")
                cancel = prev_hi[i] if cancel_upper else prev_lo[i]
                if not mss15:
                    assert not (o >= cancel if cancel_upper else o <= cancel), (row.trade, "gap cancellation")
                if o <= limit if side == 1 else o >= limit:
                    actual_entry = i, o
                    found_entry = True
                    target = o + side * target_ticks
            if found_entry:
                if o <= stop if side == 1 else o >= stop:
                    actual_exit = i, o, "stop"
                elif o >= target if side == 1 else o <= target:
                    actual_exit = i, o, "limit"
            if actual_exit:
                break
            for pa, pb in zip(path[:-1], path[1:]):
                if not found_entry:
                    moving_to_entry = pb < pa if side == 1 else pb > pa
                    moving_to_cancel = not mss15 and (pb > pa if cancel_upper else pb < pa)
                    levels = ([] if not moving_to_cancel else [("cancel", cancel)])
                    if moving_to_entry:
                        levels.append(("entry", limit))
                    events = [(abs(px - pa), kind, px) for kind, px in levels if min(pa, pb) <= px <= max(pa, pb)]
                    if not events:
                        continue
                    _, kind, at = min(events)  # cancellation wins equal-price ties
                    assert kind == "entry", (row.trade, "intrabar cancellation before fill")
                    actual_entry = i, int(at)
                    found_entry = True
                    target = int(at) + side * target_ticks
                    pa = int(at)
                    if pa <= stop if side == 1 else pa >= stop:
                        actual_exit = i, pa, "stop"
                        break
                # The remaining segment after entry belongs to the position.
                hits = [(abs(px - pa), kind, px) for kind, px in (("stop", stop), ("limit", target))
                        if min(pa, pb) <= px <= max(pa, pb)]
                if hits:
                    _, kind, px = min(hits, key=lambda item: item[0])
                    actual_exit = i, int(px), kind
                    break
            if actual_exit:
                break
            if daily_flat and found_entry and i == exit_idx and row.exit_reason == "close":
                assert row.exit_signal == ("New York close" if session_flat else "Daily close"), (row.trade, "unexpected forced close")
                actual_exit = i, c, "close"
                break
            if found_entry and i + 1 < len(symbols) and symbols[i + 1] != symbols[i]:
                actual_exit = i, c, "roll"
                break
        assert actual_entry == (entry_idx, entry_px), (row.trade, "entry", actual_entry, entry_idx, entry_px)
        assert actual_exit == (exit_idx, exit_px, row.exit_reason), (row.trade, "exit", actual_exit, row.exit_reason)
        cents = (exit_px - entry_px) * side * 1000 * int(row.contracts) - 402 * int(row.contracts)
        assert cents == int((Decimal(str(row.profit)) * 100).to_integral_value()), row.trade
        pnl_cents.append(cents)
    net = sum(pnl_cents) / 100
    wins = sum(v > 0 for v in pnl_cents)
    gp = sum(v for v in pnl_cents if v > 0)
    gl = -sum(v for v in pnl_cents if v < 0)
    pf = gp / gl if gl else None
    assert abs(net - summary["all"]["net_profit"]) < 0.000001
    assert len(pnl_cents) == summary["all"]["total_closed_trades"]
    assert abs(wins / len(pnl_cents) * 100 - summary["all"]["percent_profitable"]) < 0.000001
    if pf is not None:
        assert abs(pf - summary["all"]["profit_factor"]) < 0.000001
    audit = {"scope": "Independent ledger math and raw CL execution replay; signals supplied, swings not independently detected",
             "trades_checked": len(pnl_cents), "net_profit": net, "reported_net_profit": summary["all"]["net_profit"],
             "difference": net - summary["all"]["net_profit"], "winning_trades": wins, "profit_factor": pf,
             "all_entry_exit_prices_and_times_match": True}
    (out / "independent_audit.json").write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
