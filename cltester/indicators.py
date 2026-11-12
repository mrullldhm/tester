"""Vectorised indicators and higher-timeframe candles for strategy signals.

Higher timeframes come from cltester.swings.build_candles (same candles as the swing rule: clock aligned 5m-1h,
4h blocks from 17:00 CT, CME trading day). A candle is usable only from the 1m bar at whose close it is complete
(`avail`), so `on_1m` never shows an unfinished candle.

Formulas follow TradingView where the name says so (RMA = Wilder smoothing); `rsi_sma` / `atr_sma` are the simple
moving average variants some MT5 code uses.
"""

import numpy as np
import pandas as pd

from .config import TICK
from .data import add_session
from .swings import build_candles


def tf_candles(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    """Completed candles of timeframe tf: open, high, low, close ($), avail (1m bar index where complete: use it
    for timing only), first / last (1m bar indexes inside the candle) and day (CME trading day of the candle's own
    bars; avail can fall in the next session when the candle's last minute is missing)."""
    if "trading_day" not in df:
        df = add_session(df)
    cd = build_candles(df, tf)
    day = df["trading_day"].to_numpy()[cd.first] if len(cd) else df["trading_day"].to_numpy()[:0]
    return pd.DataFrame({"ts": cd.ts, "open": cd.o * TICK, "high": cd.h * TICK, "low": cd.l * TICK,
                         "close": cd.c * TICK, "avail": cd.avail, "first": cd.first, "last": cd.last, "day": day})


def in_session(df: pd.DataFrame, cd: pd.DataFrame) -> np.ndarray:
    """Bool per candle: complete inside its own trading day. False when its last minute is missing and it only
    completes on the next session's first bar: a signal then would trade a stale candle in a new session."""
    av = cd["avail"].to_numpy()
    ok = av < len(df)
    out = np.zeros(len(cd), dtype=bool)
    out[ok] = df["trading_day"].to_numpy()[av[ok]] == cd["day"].to_numpy()[ok]
    return out


def on_1m(values, avail: np.ndarray, n: int) -> np.ndarray:
    """Per 1m bar, the value of the newest candle complete at that bar's close (NaN before the first)."""
    v = np.asarray(values, dtype=float)
    if len(v) == 0:  # warm-up: no candle complete yet
        return np.full(n, np.nan)
    src = np.full(n, -1, dtype=np.int64)
    ok = avail < n
    src[avail[ok]] = np.flatnonzero(ok)  # several candles on one bar: the last one wins
    src = np.maximum.accumulate(src)
    out = np.where(src >= 0, v[np.maximum(src, 0)], np.nan)
    return out


def new_candle(avail: np.ndarray, n: int) -> np.ndarray:
    """Bool per 1m bar: a candle of this timeframe completed at this bar's close."""
    m = np.zeros(n, dtype=bool)
    m[avail[avail < n]] = True
    return m


def tf_minutes(tf: str) -> int:
    from .swings import TIMEFRAMES
    return TIMEFRAMES[tf]


def close_ticks(df: pd.DataFrame) -> np.ndarray:
    """1m closes as integer ticks (for trade management, which works in ticks)."""
    return np.round(df["close"].to_numpy() / TICK).astype(np.int64)


def _s(x) -> pd.Series:
    return x if isinstance(x, pd.Series) else pd.Series(np.asarray(x, dtype=float))


def sma(x, n: int) -> pd.Series:
    return _s(x).rolling(n).mean()


def ema(x, n: int) -> pd.Series:
    return _s(x).ewm(span=n, adjust=False).mean()


def rma(x, n: int) -> pd.Series:
    """Wilder smoothing (TradingView ta.rma): seeded with the SMA of the first n values."""
    series = _s(x)
    s = series.to_numpy(float)
    out = np.full(len(s), np.nan)
    ok = np.flatnonzero(~np.isnan(s))
    if len(ok) < n:
        return pd.Series(out, index=series.index)
    start = ok[0] + n - 1
    out[start] = np.mean(s[ok[0]:start + 1])
    a = 1.0 / n
    for k in range(start + 1, len(s)):
        out[k] = out[k - 1] + a * (s[k] - out[k - 1])
    return pd.Series(out, index=series.index)


def wma(x, n: int) -> pd.Series:
    series = _s(x)
    w = np.arange(1, n + 1, dtype=float)
    v = series.to_numpy(float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=series.index)


def true_range(h, l, c) -> pd.Series:
    h, l, c = _s(h), _s(l), _s(c)
    pc = c.shift()
    return pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)


def atr_sma(h, l, c, n: int) -> pd.Series:
    return true_range(h, l, c).rolling(n).mean()


def atr_rma(h, l, c, n: int) -> pd.Series:
    tr = true_range(h, l, c)
    if len(tr):
        tr.iloc[0] = (_s(h) - _s(l)).iloc[0]
    return rma(tr, n)


def rsi_sma(c, n: int) -> pd.Series:
    d = _s(c).diff()
    up, dn = d.clip(lower=0).rolling(n).mean(), (-d.clip(upper=0)).rolling(n).mean()
    return 100 - 100 / (1 + up / dn)


def rsi_wilder(c, n: int) -> pd.Series:
    """TradingView ta.rsi."""
    d = _s(c).diff()
    up, dn = rma(d.clip(lower=0), n), rma(-d.clip(upper=0), n)
    rs = up / dn
    return pd.Series(np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + rs))), index=rs.index)


def supertrend(h, l, c, n: int, mult: float) -> tuple[np.ndarray, np.ndarray]:
    """TradingView ta.supertrend (Pine v5 reference code). Returns (direction +1 up / -1 down, line). ATR = RMA.
    Pine's own direction is the opposite sign (-1 = up)."""
    h, l, c = (_s(x).to_numpy(float) for x in (h, l, c))
    atr = atr_rma(h, l, c, n).to_numpy()
    hl2 = (h + l) / 2
    k = len(c)
    lower, upper, dirn, line = (np.full(k, np.nan) for _ in range(4))
    for t in range(k):
        if np.isnan(atr[t]):
            continue
        lo, up = hl2[t] - mult * atr[t], hl2[t] + mult * atr[t]
        first = t == 0 or np.isnan(atr[t - 1])
        if not first:
            lo = lo if (lo > lower[t - 1] or c[t - 1] < lower[t - 1]) else lower[t - 1]
            up = up if (up < upper[t - 1] or c[t - 1] > upper[t - 1]) else upper[t - 1]
        lower[t], upper[t] = lo, up
        if first:
            dirn[t] = -1  # Pine starts in a downtrend
        elif dirn[t - 1] == -1:  # previous line was the upper band
            dirn[t] = 1 if c[t] > up else -1
        else:
            dirn[t] = -1 if c[t] < lo else 1
        line[t] = lo if dirn[t] == 1 else up
    return dirn, line


def vortex(h, l, c, n: int = 14) -> tuple[pd.Series, pd.Series]:
    """Vortex indicator (VI+, VI-), TradingView default length 14."""
    h, l = _s(h), _s(l)
    vmp, vmm = (h - l.shift()).abs(), (l - h.shift()).abs()
    tr = true_range(h, l, c).rolling(n).sum()
    return vmp.rolling(n).sum() / tr, vmm.rolling(n).sum() / tr


def session_vwap(df: pd.DataFrame) -> np.ndarray:
    """VWAP of the CME trading day so far, per 1m bar, from typical price (h+l+c)/3."""
    tp = (df["high"] + df["low"] + df["close"]).to_numpy(float) / 3
    v = df["volume"].to_numpy(float)
    g = pd.factorize(df["trading_day"])[0]
    pv = pd.Series(tp * v).groupby(g).cumsum().to_numpy()
    cv = pd.Series(v).groupby(g).cumsum().to_numpy()
    return np.where(cv > 0, pv / np.maximum(cv, 1e-12), tp)
