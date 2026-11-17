"""Independent v2 descriptive count; owner decisions supersede codex_review.md.

Run: .venv/bin/python -m studies.pdl_swing_4h.codex_count > studies/pdl_swing_4h/codex_counts_v2.txt
Never imports or reads the other study implementation. All comparisons use ticks.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from cltester.config import TICK
from cltester.data import add_session, load_bars, to_ticks
from cltester.swings import HIGH, LOW, build_candles, detect

GROUPS = ("C1 cross", "C2 any")
SHAPES = ("C3", "C4", "C4 unknown order", "none")


def period(day):
    return "dev" if pd.Timestamp(day) < pd.Timestamp("2022-01-01") else "validation"


def first_hits(df, cd, c4, upper, lower):
    """First threshold hits, not timestamps of the final candle extremes.

    An opening gap beyond a threshold counts at that minute's open. If both
    thresholds occur in that minute, its open can resolve their order; otherwise
    1m OHLC cannot resolve it. No synthetic path through missing minutes.
    """
    start, end = int(cd.first[c4]), int(cd.last[c4]) + 1
    hi = to_ticks(df["high"].iloc[start:end])
    lo = to_ticks(df["low"].iloc[start:end])
    hs, ls = np.flatnonzero(hi >= upper), np.flatnonzero(lo <= lower)
    if not len(hs) or not len(ls):
        return "missing", None, None
    h, l = int(hs[0]), int(ls[0])
    if h < l:
        order = "high first"
    elif l < h:
        order = "low first"
    else:
        opening = int(to_ticks(df["open"].iloc[start + h:start + h + 1])[0])
        if upper > lower and opening >= upper:
            order = "high first"
        elif upper > lower and opening <= lower:
            order = "low first"
        else:
            order = "unknown"
    return order, df["ts"].iloc[start + h], df["ts"].iloc[start + l]


def count(df, cd, st, previous_daily, side):
    """Count only points on the candle being processed, never restored old points."""
    short = side == "short"
    setup, opposite = ("sl", "sh") if short else ("sh", "sl")
    opposite_kind = HIGH if short else LOW
    days = df["trading_day"].to_numpy()[cd.first]
    rows = []
    audit = {"current-candle points": 0, "censored points": 0,
             "included setup-first outside candles": 0, "restored older-point transitions ignored": 0,
             "C3 local shapes rejected by structure": 0, "C4 wrong order": 0}
    for k in range(1, len(cd)):
        point = int(st[f"{setup}_candle"][k])
        if point != k:
            if point >= 0 and point != st[f"{setup}_candle"][k - 1]:
                audit["restored older-point transitions ignored"] += 1
            continue
        audit["current-candle points"] += 1
        setup_first = st[f"{opposite}_candle"][k] == k and st["newest"][k] == opposite_kind
        # The opposite point printed AFTER the setup is not its predecessor.
        prior = opposite + ("2" if setup_first else "")
        audit["included setup-first outside candles"] += int(setup_first)
        c3, c4 = k + 1, k + 2
        if c4 >= len(cd) or period(days[c4]) != period(days[k]):
            audit["censored points"] += 1
            continue
        level = previous_daily.get(pd.Timestamp(days[k]), np.nan)
        prior_candle = int(st[f"{prior}_candle"][k])
        prior_price = int(st[f"{prior}_price"][k])
        cross = (not pd.isna(level) and prior_candle >= 0 and
                 ((prior_price > level and cd.l[k] <= level) if short else
                  (prior_price < level and cd.h[k] >= level)))
        local_opposite = cd.h[c3] >= cd.h[k] if short else cd.l[c3] <= cd.l[k]
        trigger = cd.l[c4] <= cd.l[k] if short else cd.h[c4] >= cd.h[k]
        strict_right = cd.h[c4] < cd.h[c3] if short else cd.l[c4] > cd.l[c3]
        actual_opposite = (st["newest"][c3] == opposite_kind and
                           st[f"{opposite}_candle"][c3] == c3 and
                           st[f"{setup}_candle"][c3] == k)
        shape, order = "none", "not both"
        if local_opposite and trigger:
            if strict_right:
                if actual_opposite:
                    shape = "C3"
                else:
                    audit["C3 local shapes rejected by structure"] += 1
            else:
                upper, lower = (cd.h[c3], cd.l[k]) if short else (cd.h[k], cd.l[c3])
                order, _, _ = first_hits(df, cd, c4, int(upper), int(lower))
                if order == ("high first" if short else "low first"):
                    shape = "C4"
                elif order == "unknown":
                    shape = "C4 unknown order"
                elif order != "missing":
                    audit["C4 wrong order"] += 1
                else:
                    raise AssertionError("c4 range implies both threshold hits")
        rows.append({"c2": k, "day": pd.Timestamp(days[k]), "period": period(days[k]),
                     "cross": cross, "shape": shape, "level": level,
                     "prior_price": prior_price, "prior_candle": prior_candle, "order": order})
    rows = pd.DataFrame(rows)
    assert len(rows) + audit["censored points"] == audit["current-candle points"]
    assert rows.c2.is_unique
    return rows, audit


def table(rows, title):
    print(f"\n{title}")
    print(f'{"Group":<12}{"C3":>10}{"C4 (correct order)":>22}{"C4 unknown order":>21}{"Total events":>16}')
    for label, subset in (("C1 cross", rows[rows.cross]), ("C2 any", rows)):
        nums = [int((subset["shape"] == shape).sum()) for shape in SHAPES[:-1]]
        assert sum(nums) <= len(subset)
        print(f'{label:<12}{nums[0]:>10,}{nums[1]:>22,}{nums[2]:>21,}{len(subset):>16,}')


def raw_bar(df, i):
    row = df.iloc[int(i)]
    prices = "/".join(f"{row[key]:.2f}" for key in ("open", "high", "low", "close"))
    return f"{row.ts} O/H/L/C={prices}"


def spot_check(df, cd, st, rows, tf, shape):
    row = rows[rows.cross & (rows["shape"] == shape)].iloc[0]
    k = int(row.c2)
    level, prior = int(row.level), int(row.prior_candle)
    print(f"\n{tf} long C1/{shape} raw-1m spot check (all times UTC)")
    print(f"c2 trading day={row.day.date()}, PDH={level*TICK:.2f}; "
          f"preceding SL={row.prior_price*TICK:.2f} at {cd.ts[prior]}")
    days = df.trading_day.drop_duplicates().tolist()
    previous_day = days[days.index(row.day) - 1]
    daily_raw = df[df.trading_day == previous_day]
    assert int(to_ticks(daily_raw.high).max()) == level
    print(f"Previous observed trading day={previous_day.date()}, PDH witness: "
          f"{raw_bar(df, daily_raw.high.idxmax())}")
    prior_raw = df.iloc[cd.first[prior]:cd.last[prior] + 1]
    assert int(to_ticks(prior_raw.low).min()) == row.prior_price
    print(f"Preceding SL witness: {raw_bar(df, prior_raw.low.idxmin())}")
    for label, j in zip(("c1", "c2", "c3", "c4"), range(k - 1, k + 3), strict=True):
        raw = df.iloc[cd.first[j]:cd.last[j] + 1]
        for key, expected in (("open", cd.o[j]), ("high", cd.h[j]),
                              ("low", cd.l[j]), ("close", cd.c[j])):
            ticks = to_ticks(raw[key])
            actual = {"open": ticks[0], "high": ticks.max(), "low": ticks.min(), "close": ticks[-1]}[key]
            assert actual == expected
        print(f"{label} {cd.ts[j]} raw bars={len(raw)}, "
              f"O/H/L/C={cd.o[j]*TICK:.2f}/{cd.h[j]*TICK:.2f}/{cd.l[j]*TICK:.2f}/{cd.c[j]*TICK:.2f}")
        print(f"  high witness: {raw_bar(df, raw.high.idxmax())}")
        print(f"  low witness:  {raw_bar(df, raw.low.idxmin())}")
    assert row.prior_price < level <= cd.h[k]
    assert cd.l[k + 1] <= cd.l[k] and cd.h[k + 2] >= cd.h[k]
    if shape == "C3":
        assert cd.l[k + 2] > cd.l[k + 1]
        assert st["newest"][k + 1] == LOW and st["sl_candle"][k + 1] == k + 1
        assert st["sh_candle"][k + 1] == k
        print("PASS: SL0 < PDH <= c2.high; c3.low <= c2.low; "
              "c4.high >= c2.high; c4.low > c3.low; snapshot confirms c3 SL and retains c2 SH.")
    else:
        order, high_ts, low_ts = first_hits(df, cd, k + 2, int(cd.h[k]), int(cd.l[k + 1]))
        assert order == "low first"
        print(f"First c3.low touch={low_ts}; first c2.high touch={high_ts}; order={order}")
        for ts in dict.fromkeys((low_ts, high_ts)):
            print(f"  threshold witness: {raw_bar(df, df.index[df.ts == ts][0])}")
        print("PASS: SL0 < PDH <= c2.high; c3.low <= c2.low; "
              "c4 touches c3.low before c2.high (provisional candle shape).")


def main():
    print("Independent CL v2 counts: 4h/1h x short/long; in-sample descriptive, no tuning.")
    print("Dev: trading days 2010-06-01..2021-12-31; validation: 2022-01-01..2024-12-31.")
    print("C1 is a subset of C2 any; total events includes shapes labelled none.")
    print("C1 short: preceding SH > PDL >= c2.low; long: preceding SL < PDH <= c2.high.")
    print("C3 requires actual opposite-swing snapshot at c3, retaining c2 setup point.")
    print("C4 is provisional; correct order = high first (short), low first (long).")
    print("Same-minute first hits use minute open when decisive; otherwise unknown. Touches inclusive.")
    print("Setup-first outside points included; restored older points excluded; rule-5 new points included.")
    print("Adjacent observed candles; c3/c4 completed within c2 period; continuous swing history.")
    print("Previous daily level uses c2 day and previous observed CME session; no calendar completeness claim.")
    print("No warmup before prescribed load; first observed session may be partial; raw contract rolls included.")
    df = add_session(load_bars("2010-06-01", "2025-01-01"))
    df = df[(df.trading_day >= pd.Timestamp("2010-06-01")) &
            (df.trading_day < pd.Timestamp("2025-01-01"))].reset_index(drop=True)
    assert df.trading_day.max() < pd.Timestamp("2025-01-01")
    print(f"Research 1m bars={len(df):,}; UTC coverage={df.ts.min()} .. {df.ts.max()}; no holdout loaded.")
    daily = pd.DataFrame({"day": df.trading_day, "high": to_ticks(df.high), "low": to_ticks(df.low)})
    daily = daily.groupby("day", sort=True).agg({"high": "max", "low": "min"})
    previous = daily.shift(1)
    for tf in ("4h", "1h"):
        cd = build_candles(df, tf)
        _, st = detect(cd)
        print(f"\nCompleted {tf} candles={len(cd):,}")
        for side in ("short", "long"):
            levels = previous["low" if side == "short" else "high"].to_dict()
            rows, audit = count(df, cd, st, levels, side)
            for p in ("dev", "validation"):
                table(rows[rows.period == p], f"{tf} / {side} / {p}")
            print(f"Audit {tf}/{side}: " + "; ".join(f"{key}={value:,}" for key, value in audit.items()))
            if side == "long":
                for shape in ("C3", "C4"):
                    spot_check(df, cd, st, rows, tf, shape)


if __name__ == "__main__":
    main()
