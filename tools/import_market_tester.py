"""One-time import of CL1 1-minute price data from the market-tester repo.

    .venv/bin/python tools/import_market_tester.py [--src ../market-tester]

Takes only the front-month series (Databento CL.v.0) plus the Massive extension bars after the last
Databento bar, and writes data/cl1/year=YYYY.parquet and data/manifest.json. Nothing else is copied.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tvtester.data import COLUMNS, DATA_DIR, MANIFEST, write_year  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(ROOT.parent / "market-tester"))
    src = Path(ap.parse_args().src) / "data" / "processed"

    parts = []
    for p in sorted((src / "ohlcv-1m").glob("year=*/cl.parquet")):
        df = pd.read_parquet(p, filters=[("continuous_symbol", "==", "CL.v.0")])
        parts.append(df.assign(vendor="databento"))
        print(f"  {p.parent.name}: {len(df):,} bars", flush=True)
    db = pd.concat(parts, ignore_index=True)

    ext = pd.read_parquet(src / "ohlcv-1m-ext" / "cl_massive.parquet")
    ext = ext[(ext["continuous_symbol"] == "CL.v.0") & (ext["ts_event_utc"] > db["ts_event_utc"].max())]
    print(f"  massive extension: {len(ext):,} bars", flush=True)

    bars = pd.concat([db, ext.assign(vendor="massive")], ignore_index=True)
    bars = bars.rename(columns={"ts_event_utc": "ts"})[COLUMNS]
    bars = bars.sort_values("ts").drop_duplicates("ts", keep="first").reset_index(drop=True)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    files = {}
    for year, g in bars.groupby(bars["ts"].dt.year):
        path = write_year(g, int(year))
        files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()

    MANIFEST.write_text(json.dumps({
        "written_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "market-tester data/processed: ohlcv-1m CL.v.0 (Databento GLBX.MDP3) + ohlcv-1m-ext (Massive)",
        "first_bar": str(bars["ts"].iloc[0]),
        "last_bar": str(bars["ts"].iloc[-1]),
        "rows": len(bars),
        "rows_by_vendor": bars["vendor"].value_counts().to_dict(),
        "updates": [],
        "files_sha256": files,
    }, indent=2))
    print(f"wrote {len(bars):,} bars {bars['ts'].iloc[0]} -> {bars['ts'].iloc[-1]}")


if __name__ == "__main__":
    main()
