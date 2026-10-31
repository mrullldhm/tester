"""CL1! 1-minute bars: storage layout, loading, and the arrays the engine runs on.

Layout: data/cl1/year=YYYY.parquet, one row per minute, ts = bar open time (UTC).
Prices are kept as floats on disk; the engine works in integer ticks so comparisons are exact
(CL traded below zero on 2020-04-20, so ticks can be negative).
"""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from .config import ROOT, TICK

DATA_DIR = ROOT / "data" / "cl1"
MANIFEST = ROOT / "data" / "manifest.json"
COLUMNS = ["ts", "raw_symbol", "open", "high", "low", "close", "volume", "vendor"]


def year_path(year: int) -> Path:
    return DATA_DIR / f"year={year}.parquet"


def write_year(df: pd.DataFrame, year: int) -> Path:
    path = year_path(year)
    out = df[COLUMNS].sort_values("ts").reset_index(drop=True)
    if not out["ts"].is_unique:
        raise ValueError(f"duplicate bar times in {year}")
    out.to_parquet(path, index=False)
    return path


def load_bars(start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """All bars with start <= ts < end (UTC dates or timestamps)."""
    paths = sorted(DATA_DIR.glob("year=*.parquet"))
    if not paths:
        raise FileNotFoundError(f"no bars in {DATA_DIR}; run tools/import_market_tester.py or tvtester.update")
    lo = pd.Timestamp(start, tz="UTC") if start else None
    hi = pd.Timestamp(end, tz="UTC") if end else None
    last_year = None if hi is None else (hi.year - 1 if hi == pd.Timestamp(year=hi.year, month=1, day=1, tz="UTC")
                                         else hi.year)  # an exclusive end on 1 January never opens that year
    keep = [p for p in paths if (lo is None or int(p.stem[5:]) >= lo.year)
            and (last_year is None or int(p.stem[5:]) <= last_year)]
    df = pd.concat((pd.read_parquet(p) for p in keep), ignore_index=True)
    if lo is not None:
        df = df[df["ts"] >= lo]
    if hi is not None:
        df = df[df["ts"] < hi]
    return df.sort_values("ts").reset_index(drop=True)


def to_ticks(prices) -> np.ndarray:
    return np.round(np.asarray(prices, dtype=float) / TICK).astype(np.int64)


@dataclass
class Bars:
    """Column arrays for the engine. Index i = i-th bar."""

    ts: pd.DatetimeIndex  # UTC bar open
    t_ms: np.ndarray  # bar open, ms since epoch (Pine `time`)
    o: np.ndarray  # ticks
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    volume: np.ndarray
    raw_symbol: np.ndarray
    last_of_contract: np.ndarray  # True on the last bar before raw_symbol changes (roll exit bar)
    cache: dict = field(default_factory=dict, repr=False, compare=False)  # derived arrays; lives as long as the bars

    def __len__(self) -> int:
        return len(self.o)

    @classmethod
    def from_frame(cls, df: pd.DataFrame) -> "Bars":
        ts = pd.DatetimeIndex(df["ts"])
        sym = df["raw_symbol"].to_numpy()
        last = np.zeros(len(df), dtype=bool)
        last[:-1] = sym[:-1] != sym[1:]
        return cls(
            ts=ts,
            t_ms=(ts.as_unit("ms").asi8),
            o=to_ticks(df["open"]), h=to_ticks(df["high"]), l=to_ticks(df["low"]), c=to_ticks(df["close"]),
            volume=df["volume"].to_numpy(), raw_symbol=sym, last_of_contract=last,
        )
