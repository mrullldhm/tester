"""Add new CL1! 1-minute bars after the last stored bar.

    .venv/bin/python -m tvtester.update                      # Databento (default): shows the cost, asks first
    .venv/bin/python -m tvtester.update --yes                # Databento without the prompt
    .venv/bin/python -m tvtester.update --source massive     # Massive REST (no per-request cost quote)
    .venv/bin/python -m tvtester.update --end 2026-11-15     # stop before this UTC date

Front-month rule (both sources): Databento CL.v.0 = the contract with the highest previous-UTC-day volume,
switching at 00:00 UTC. Massive has no continuous symbol, so the same rule is rebuilt from its outrights.
Databento is the primary vendor: a Databento update first replaces any Massive bars it now covers.
API keys come from .env (DATABENTO_API_KEY, MASSIVE_API_KEY). CL only: any other root is refused.
"""

import sys

if __name__ == "__main__":
    from .resource_guard import entrypoint
    entrypoint(["-m", "tvtester.update", *sys.argv[1:]])

import argparse
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

from .config import ROOT
from .data import COLUMNS, DATA_DIR, MANIFEST, load_bars, write_year

DATASET = "GLBX.MDP3"
FRONT = "CL.v.0"
MASSIVE_API = "https://api.massive.com/futures/v1/aggs/{ticker}"
MONTHS = "FGHJKMNQUVXZ"


def assert_cl(symbol: str) -> None:
    """CL outrights (NYMEX Light Crude) only. MCL, spreads and every other market are refused."""
    if not re.fullmatch(r"CL[FGHJKMNQUVXZ]\d{1,2}", symbol):
        raise ValueError(f"{symbol}: only CL is allowed in this repo")


def key(name: str) -> str:
    load_dotenv(ROOT / ".env")
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f"{name} missing in .env")
    return v


def check_bars(df: pd.DataFrame) -> pd.DataFrame:
    px = df[["open", "high", "low", "close"]].astype(float)
    if not np.isfinite(px.to_numpy()).all() or df["raw_symbol"].isna().any() or df["volume"].isna().any():
        raise ValueError("bars with missing or non-finite values")
    for k in ("open", "high", "low", "close"):
        ticks = df[k].astype(float) * 100
        if (ticks - ticks.round()).abs().max() > 1e-6:
            raise ValueError(f"{k} not on the $0.01 tick")
        df[k] = ticks.round() / 100
    bad = (df["low"] > df[["open", "close"]].min(axis=1)) | (df["high"] < df[["open", "close"]].max(axis=1))
    if bad.any():
        raise ValueError(f"{int(bad.sum())} bars break low <= open/close <= high")
    if not df["ts"].is_unique:
        raise ValueError("duplicate bar times")
    for s in df["raw_symbol"].unique():
        assert_cl(s)
    return df


# --- Databento ---------------------------------------------------------------------------------------------
def from_databento(start: pd.Timestamp, end: pd.Timestamp | None, yes: bool) -> pd.DataFrame:
    import databento as db

    client = db.Historical(key("DATABENTO_API_KEY"))
    avail = pd.Timestamp(client.metadata.get_dataset_range(dataset=DATASET)["end"]).tz_convert("UTC")
    end = min(end, avail) if end is not None else avail
    if end <= start:
        print(f"[databento] nothing new: data available to {avail}")
        return pd.DataFrame(columns=COLUMNS)
    req = dict(dataset=DATASET, symbols=[FRONT], stype_in="continuous", schema="ohlcv-1m", start=start, end=end)
    cost = client.metadata.get_cost(**req)
    print(f"[databento] {FRONT} ohlcv-1m {start} -> {end}: quoted cost ${cost:.4f}")
    if not yes and input("Download? [y/N] ").strip().lower() != "y":
        raise SystemExit("cancelled")
    bars = client.timeseries.get_range(**req).to_df().reset_index()
    if bars.empty:
        return pd.DataFrame(columns=COLUMNS)
    ids = sorted(bars["instrument_id"].unique().tolist())
    defs = client.timeseries.get_range(dataset=DATASET, symbols=ids, stype_in="instrument_id", schema="definition",
                                       start=start - pd.Timedelta(days=7), end=end).to_df()
    names = defs.drop_duplicates("instrument_id", keep="last").set_index("instrument_id")["raw_symbol"]
    out = pd.DataFrame({"ts": pd.to_datetime(bars["ts_event"], utc=True),
                        "raw_symbol": bars["instrument_id"].map(names)})
    if out["raw_symbol"].isna().any():
        raise ValueError(f"no definition for instrument ids {bars.loc[out['raw_symbol'].isna(), 'instrument_id'].unique()}")
    for k in ("open", "high", "low", "close"):
        out[k] = bars[k].astype(float)
    out["volume"] = bars["volume"].astype("int64")
    out["vendor"] = "databento"
    return out


# --- Massive -----------------------------------------------------------------------------------------------
def next_contracts(raw: str, n: int) -> list[str]:
    """CLZ6 -> [CLZ6, CLF7, CLG7, ...]"""
    m, y = MONTHS.index(raw[2]), int(raw[3:])
    return [f"CL{MONTHS[(m + i) % 12]}{(y + (m + i) // 12) % 10}" for i in range(n)]


def massive_fetch(ticker: str, start: pd.Timestamp, end: pd.Timestamp, api_key: str) -> pd.DataFrame:
    assert_cl(ticker)
    url = MASSIVE_API.format(ticker=ticker)
    params = {"resolution": "1min", "window_start.gte": str(start.value), "window_start.lt": str(end.value),
              "limit": 50000, "sort": "window_start.asc"}
    rows = []
    while url:
        for attempt in range(5):
            r = requests.get(url, params=params, headers={"Authorization": f"Bearer {api_key}"}, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            break
        else:
            r.raise_for_status()
        js = r.json()
        rows.extend(js.get("results") or [])
        url, params = js.get("next_url"), None
        print(f"  {ticker}: {len(rows):,} bars", flush=True)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if (df["ticker"] != ticker).any():
        raise ValueError(f"{ticker}: response holds other tickers")
    return pd.DataFrame({"ts": pd.to_datetime(df["window_start"], unit="ns", utc=True), "raw_symbol": ticker,
                         "open": df["open"].astype(float), "high": df["high"].astype(float),
                         "low": df["low"].astype(float), "close": df["close"].astype(float),
                         "volume": df["volume"].astype("int64")}).drop_duplicates("ts")


def from_massive(start: pd.Timestamp, end: pd.Timestamp | None, last_front: str) -> pd.DataFrame:
    api_key = key("MASSIVE_API_KEY")
    end = end or pd.Timestamp.now(tz="UTC").floor("min")
    fetch_from = (start - pd.Timedelta(days=1)).floor("D")  # previous day's volume ranks the first new day
    months = (end.year - fetch_from.year) * 12 + end.month - fetch_from.month
    contracts = next_contracts(last_front, months + 3)  # every contract that can be front through `end`
    parts = [massive_fetch(t, fetch_from, end, api_key) for t in contracts]
    m = pd.concat([p for p in parts if len(p)], ignore_index=True)
    day = m["ts"].dt.floor("D")
    vol = m.assign(d=day).groupby(["d", "raw_symbol"])["volume"].sum().unstack(fill_value=0).sort_index()
    front = {}
    for d in vol.index:
        k = vol.index.get_loc(d)
        front[d] = last_front if k == 0 else vol.iloc[k - 1].idxmax()
    pick = m[m["raw_symbol"].to_numpy() == day.map(front).to_numpy()]
    pick = pick[pick["ts"] >= start].copy()
    if contracts[-1] in set(front.values()):
        raise ValueError(f"front month reached {contracts[-1]}, the last contract fetched: a later one may be missing")
    pick["vendor"] = "massive"
    print("[massive] front by UTC day: " + ", ".join(f"{d.date()}={s}" for d, s in front.items()))
    return pick[COLUMNS]


# --- store -------------------------------------------------------------------------------------------------
def store(new: pd.DataFrame, replace_from: pd.Timestamp, source: str) -> None:
    years = sorted(set(new["ts"].dt.year) | {replace_from.year})
    for y in years:
        old = load_bars(f"{y}-01-01", f"{y + 1}-01-01") if (DATA_DIR / f"year={y}.parquet").exists() else None
        keep = old[old["ts"] < replace_from] if old is not None else pd.DataFrame(columns=COLUMNS)
        add = new[new["ts"].dt.year == y]
        write_year(pd.concat([keep, add], ignore_index=True), y)
    man = json.loads(MANIFEST.read_text())
    allb = load_bars(f"{years[0]}-01-01")
    man["last_bar"] = str(allb["ts"].iloc[-1])
    man["files_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DATA_DIR.glob("*.parquet"))}
    man["rows"] = int(sum(len(pd.read_parquet(p, columns=["ts"])) for p in DATA_DIR.glob("*.parquet")))
    man["updates"].append({"utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source": source,
                           "replaced_from": str(replace_from), "rows_added": len(new),
                           "first": str(new["ts"].min()), "last": str(new["ts"].max())})
    MANIFEST.write_text(json.dumps(man, indent=2))
    print(f"[update] stored {len(new):,} bars {new['ts'].min()} -> {new['ts'].max()}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["databento", "massive"], default="databento")
    ap.add_argument("--end", help="UTC date or time, exclusive")
    ap.add_argument("--yes", action="store_true", help="skip the Databento cost prompt")
    a = ap.parse_args()
    end = pd.Timestamp(a.end, tz="UTC") if a.end else None
    last_year = max(int(p.stem[5:]) for p in DATA_DIR.glob("year=*.parquet"))
    tail = load_bars(f"{last_year - 1}-01-01")
    last = tail.iloc[-1]
    if a.source == "databento":
        massive = tail[tail["vendor"] == "massive"]
        start = massive["ts"].min() if len(massive) else last["ts"] + pd.Timedelta(minutes=1)
        new = from_databento(start, end, a.yes)
    else:
        start = last["ts"] + pd.Timedelta(minutes=1)
        new = from_massive(start, end, last["raw_symbol"])
    if new.empty:
        print("[update] no new bars")
        return
    new = check_bars(new.sort_values("ts").reset_index(drop=True))
    if a.source == "databento" and new["ts"].max() < tail["ts"].max():
        # Databento does not yet reach the end of the Massive bars: keep the Massive bars after it
        rest = tail[tail["ts"] > new["ts"].max()]
        new = pd.concat([new, rest], ignore_index=True)
    store(new[COLUMNS], start, a.source)
    gaps = new["ts"].diff().dt.total_seconds().div(60)
    print(f"[update] largest gap between new bars: {gaps.max():.0f} min (weekends and the daily halt are normal)")


if __name__ == "__main__":
    main()
