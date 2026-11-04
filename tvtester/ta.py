"""Pine `ta.*` equivalents on full bar arrays (one value per bar, NaN where Pine gives na)."""

import numpy as np


def tr(h: np.ndarray, l: np.ndarray, c: np.ndarray) -> np.ndarray:
    """ta.tr(true): high - low on the first bar, else the max of the three ranges."""
    prev = np.concatenate([[np.nan], c[:-1]]).astype(float)
    out = np.maximum(h - l, np.maximum(np.abs(h - prev), np.abs(l - prev)))
    out[0] = h[0] - l[0]
    return out.astype(float)


def rma(x: np.ndarray, length: int) -> np.ndarray:
    """ta.rma: seeded with the SMA of the first `length` values, then alpha = 1 / length."""
    out = np.full(len(x), np.nan)
    if len(x) < length:
        return out
    a = 1.0 / length
    v = float(np.mean(x[:length]))
    out[length - 1] = v
    xs = x.tolist()
    vals = out.tolist()
    for i in range(length, len(xs)):
        v = a * xs[i] + (1 - a) * v
        vals[i] = v
    return np.asarray(vals)


def atr(h: np.ndarray, l: np.ndarray, c: np.ndarray, length: int) -> np.ndarray:
    return rma(tr(h, l, c), length)


def shift(x: np.ndarray, n: int) -> np.ndarray:
    """x[n] in Pine terms: the value n bars ago."""
    out = np.full(len(x), np.nan)
    if n < len(x):
        out[n:] = x[: len(x) - n]
    return out


def buffer_pivots(x: np.ndarray, strength: int, high: bool) -> np.ndarray:
    """Removed: use the complete owner swing state, never independent adjustable pivots."""
    raise ValueError("Use tvtester.swings; indicators/structure_swings.pine is the only permitted swing rule")


def ema(x: np.ndarray, length: int) -> np.ndarray:
    """ta.ema (Pine reference): sum := na(sum[1]) ? src : alpha * src + (1 - alpha) * nz(sum[1]), alpha =
    2 / (length + 1). Seeded with the first non-NaN value; NaN before it stays NaN."""
    out = np.full(len(x), np.nan)
    ok = np.flatnonzero(~np.isnan(x))
    if len(ok) == 0:
        return out
    s = int(ok[0])
    a = 2.0 / (length + 1)
    xs = x.tolist()
    v = xs[s]
    vals = out.tolist()
    vals[s] = v
    for i in range(s + 1, len(xs)):
        v = a * xs[i] + (1 - a) * v
        vals[i] = v
    return np.asarray(vals)


def stdev(x: np.ndarray, length: int) -> np.ndarray:
    """ta.stdev (biased, population): NaN for the first length - 1 bars."""
    out = np.full(len(x), np.nan)
    if len(x) < length:
        return out
    w = np.lib.stride_tricks.sliding_window_view(x.astype(float), length)
    out[length - 1:] = w.std(axis=1)
    return out


def supertrend(h: np.ndarray, l: np.ndarray, c: np.ndarray, factor: float, atr_len: int):
    """ta.supertrend(factor, atr_len): (line, direction), direction -1 = up trend, +1 = down trend (Pine).
    Pine reference: bands ratchet on their own reassigned history (nz -> 0 before the first ATR)."""
    a = atr(h, l, c, atr_len)
    src = (h + l) / 2.0
    n = len(c)
    line = np.full(n, np.nan)
    dirn = np.full(n, np.nan)
    ub_prev = lb_prev = 0.0  # nz(band[1])
    st_prev = np.nan
    a_l, s_l, c_l = a.tolist(), src.tolist(), c.astype(float).tolist()
    line_l, dir_l = line.tolist(), dirn.tolist()
    for i in range(n):
        ai = a_l[i]
        ub = s_l[i] + factor * ai
        lb = s_l[i] - factor * ai
        cp = c_l[i - 1] if i > 0 else np.nan
        lb = lb if (lb > lb_prev or cp < lb_prev) else lb_prev
        ub = ub if (ub < ub_prev or cp > ub_prev) else ub_prev
        if i == 0 or a_l[i - 1] != a_l[i - 1]:
            d = 1
        elif st_prev == ub_prev:
            d = -1 if c_l[i] > ub else 1
        else:
            d = 1 if c_l[i] < lb else -1
        st = lb if d == -1 else ub
        line_l[i], dir_l[i] = st, d
        st_prev, ub_prev, lb_prev = st, (0.0 if ub != ub else ub), (0.0 if lb != lb else lb)
    return np.asarray(line_l), np.asarray(dir_l)


def atr_trailing_stop(c: np.ndarray, n_loss: np.ndarray) -> np.ndarray:
    """UT Bot ATR trailing stop (QuantNomad "UT Bot Alerts", close source, no Heikin-Ashi). p = nz(stop[1], 0):
    both closes above p ratchet max(p, c - loss), both below ratchet min(p, c + loss), else reset to the side of
    the current close. NaN loss (ATR warm-up) gives NaN, which the next bar reads as 0 (nz)."""
    n = len(c)
    cs, ls = c.astype(float).tolist(), n_loss.tolist()
    stop = [np.nan] * n
    p = 0.0
    for i in range(n):
        s, nl = cs[i], ls[i]
        s1 = cs[i - 1] if i > 0 else np.nan
        if nl != nl:
            v = np.nan
        elif s > p and s1 > p:
            v = max(p, s - nl)
        elif s < p and s1 < p:
            v = min(p, s + nl)
        elif s > p:
            v = s - nl
        else:
            v = s + nl
        stop[i] = v
        p = 0.0 if v != v else v
    return np.asarray(stop)


def kalman_trend(z: np.ndarray, q: float, r: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """2-state constant-velocity Kalman filter (level, slope), one step per bar. F = [[1, 1], [0, 1]], H = [1, 0],
    Q = q * [[1/4, 1/2], [1/2, 1]], R = r. First bar: x = [z, 0], P = 100 * I, no predict / update. Joseph-form
    covariance update. z in dollars (R = 1 is in dollars squared)."""
    n = len(z)
    zs = z.astype(float).tolist()
    lvl, slp = [np.nan] * n, [np.nan] * n
    if n == 0:
        return np.asarray(lvl), np.asarray(slp)
    x0, x1 = zs[0], 0.0
    a, b, d = 100.0, 0.0, 100.0  # P = [[a, b], [b, d]]
    lvl[0], slp[0] = x0, x1
    for i in range(1, n):
        x0 = x0 + x1
        a, b, d = a + 2 * b + d + 0.25 * q, b + d + 0.5 * q, d + q
        s = a + r
        k0, k1 = a / s, b / s
        y = zs[i] - x0
        x0, x1 = x0 + k0 * y, x1 + k1 * y
        # Joseph: P = (I - K H) P (I - K H)^T + K R K^T, with I - K H = [[1 - k0, 0], [-k1, 1]]
        a2 = (1 - k0) ** 2 * a + k0 * k0 * r
        b2 = (1 - k0) * (b - k1 * a) + k0 * k1 * r
        d2 = k1 * k1 * a - 2 * k1 * b + d + k1 * k1 * r
        a, b, d = a2, b2, d2
        lvl[i], slp[i] = x0, x1
    return np.asarray(lvl), np.asarray(slp)


def rvi(c: np.ndarray, std_len: int = 10, length: int = 14) -> np.ndarray:
    """TradingView Relative Volatility Index: EMA of stdev on up / down closes, 100 * up / (up + down)."""
    sd = stdev(c, std_len)
    ch = np.concatenate([[np.nan], np.diff(c.astype(float))])
    up = np.where(np.isnan(sd) | np.isnan(ch), np.nan, np.where(ch <= 0, 0.0, sd))
    dn = np.where(np.isnan(sd) | np.isnan(ch), np.nan, np.where(ch > 0, 0.0, sd))
    u, d = ema(up, length), ema(dn, length)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(u + d > 0, 100 * u / (u + d), np.nan)
