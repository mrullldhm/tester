"""CL1! 1-minute bars: storage, loading, Chicago session fields, and integer-tick arrays for the engine.

Layout: data/cl1/year=YYYY.parquet, one row per minute, ts = bar open time (UTC), prices in $.
Front month (raw_symbol) = Databento CL.v.0: highest previous-UTC-day volume, switching at 00:00 UTC.
Prices are not back-adjusted: a raw_symbol change is a price jump, so the engine never holds across it.
"""

import os
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DATA_DIR, EXCHANGE_TZ, PERIODS, SESSION_OPEN, TICK

COLUMNS = ["ts", "raw_symbol", "open", "high", "low", "close", "volume", "vendor"]


def year_path(year: int) -> Path:
    return DATA_DIR / f"year={year}.parquet"


def write_year(df: pd.DataFrame, year: int) -> Path:
    out = df[COLUMNS].sort_values("ts").reset_index(drop=True)
    if not out["ts"].is_unique:
        raise ValueError(f"duplicate bar times in {year}")
    path = year_path(year)
    tmp = path.with_suffix(".parquet.tmp")
    out.to_parquet(tmp, index=False)
    os.replace(tmp, path)  # readers never see a half-written file
    return path


def load_bars(start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """Bars with start <= ts < end (UTC dates or timestamps; end exclusive)."""
    paths = sorted(DATA_DIR.glob("year=*.parquet"))
    if not paths:
        raise FileNotFoundError(f"no bars in {DATA_DIR}")
    lo = pd.Timestamp(start, tz="UTC") if start else None
    hi = pd.Timestamp(end, tz="UTC") if end else None
    hi_year = None if hi is None else (hi - pd.Timedelta(microseconds=1)).year
    keep = [p for p in paths if (lo is None or int(p.stem[5:]) >= lo.year)
            and (hi_year is None or int(p.stem[5:]) <= hi_year)]
    if not keep:
        dtypes = ["datetime64[ns, UTC]", "str", *["float64"] * 4, "int64", "str"]
        return pd.DataFrame({c: pd.Series(dtype=t) for c, t in zip(COLUMNS, dtypes, strict=True)})
    df = pd.concat((pd.read_parquet(p) for p in keep), ignore_index=True)
    if lo is not None:
        df = df[df["ts"] >= lo]
    if hi is not None:
        df = df[df["ts"] < hi]
    return df.sort_values("ts").reset_index(drop=True)


def load_period(name: str) -> pd.DataFrame:
    """Bars whose trading_day lies in [start, end). Periods cut on whole CME trading days, never mid-session."""
    start, end = PERIODS[name]
    pad = pd.Timedelta(days=1)
    df = add_session(load_bars(str(pd.Timestamp(start) - pad) if start else None,
                               str(pd.Timestamp(end) + pad) if end else None))
    keep = np.ones(len(df), dtype=bool)
    if start:
        keep &= df["trading_day"] >= pd.Timestamp(start)
    if end:
        keep &= df["trading_day"] < pd.Timestamp(end)
    return df[keep].reset_index(drop=True)


def add_session(df: pd.DataFrame) -> pd.DataFrame:
    """Add Chicago fields. trading_day = CME/Topstep day: 17:00 CT opens the next day's session
    (Sunday 17:00 CT belongs to Monday)."""
    out = df.copy()
    ct = out["ts"].dt.tz_convert(EXCHANGE_TZ)
    out["ct"] = ct
    out["ct_minute"] = (ct.dt.hour * 60 + ct.dt.minute).astype("int32")
    open_min = SESSION_OPEN.hour * 60 + SESSION_OPEN.minute
    out["sess_minute"] = ((out["ct_minute"] - open_min) % 1440).astype("int32")  # minutes since 17:00 CT
    day = ct.dt.tz_localize(None).dt.normalize()
    out["trading_day"] = day.where(out["ct_minute"] < open_min, day + timedelta(days=1))
    return out


def session_minute(t) -> int:
    """CT clock time -> minutes since the 17:00 CT session open."""
    return (t.hour * 60 + t.minute - SESSION_OPEN.hour * 60 - SESSION_OPEN.minute) % 1440


def to_ticks(prices) -> np.ndarray:
    return np.round(np.asarray(prices, dtype=float) / TICK).astype(np.int64)


@dataclass
class Bars:
    """Arrays the engine runs on. Index i = i-th bar. Prices in integer ticks so comparisons are exact."""

    ts: pd.DatetimeIndex
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray  # noqa: E741
    c: np.ndarray
    sess_minute: np.ndarray  # minutes since 17:00 CT session open
    trading_day: np.ndarray  # datetime64 date of the CME/Topstep trading day
    day_id: np.ndarray  # trading day as an int code
    sym_id: np.ndarray  # raw_symbol as an int code
    last_of_day: np.ndarray  # last bar of its trading day
    last_of_sym: np.ndarray  # last bar before raw_symbol changes

    def __len__(self) -> int:
        return len(self.o)

    @classmethod
    def from_frame(cls, df: pd.DataFrame) -> "Bars":
        if "trading_day" not in df:
            df = add_session(df)
        day = pd.factorize(df["trading_day"])[0]
        sym = pd.factorize(df["raw_symbol"])[0]
        n = len(df)
        last_day = np.ones(n, dtype=bool)
        last_sym = np.ones(n, dtype=bool)
        last_day[:-1] = day[:-1] != day[1:]
        last_sym[:-1] = sym[:-1] != sym[1:]
        return cls(ts=pd.DatetimeIndex(df["ts"]), o=to_ticks(df["open"]), h=to_ticks(df["high"]),
                   l=to_ticks(df["low"]), c=to_ticks(df["close"]), sess_minute=df["sess_minute"].to_numpy(),
                   trading_day=df["trading_day"].to_numpy(), day_id=day, sym_id=sym,
                   last_of_day=last_day, last_of_sym=last_sym)
