"""Port of hungpixi ICT System EA v2 with the owner swing rule. Hypothesis: docs/strategies/ict_ea/README.md."""

import numpy as np
import pandas as pd

from cltester.config import TICK, TICK_VALUE
from cltester.indicators import close_ticks, in_session, on_1m, tf_candles
from cltester.strategy import Base
from cltester.swings import swing_state

BULL, BEAR, NONE = 1, -1, 0
S_NONE, S_BOS, S_CHOCH, S_CISD = 0, 1, 2, 3


def _newest(flag: np.ndarray, lo_off: int, hi_off: int) -> np.ndarray:
    """Per candle t: newest q in [t-hi_off, t-lo_off] with flag[q], else -1."""
    n = len(flag)
    last = np.where(flag, np.arange(n), -1)
    last = np.maximum.accumulate(last)
    out = np.full(n, -1)
    t = np.arange(n)
    src = t - lo_off
    ok = src >= 0
    out[ok] = last[src[ok]]
    out[(out >= 0) & (out < t - hi_off)] = -1
    return out


def daily_bias(day: np.ndarray, o: np.ndarray, h: np.ndarray, l: np.ndarray, eps_frac: float) -> np.ndarray:
    """Source DetermineFirstExtreme on 5m candles of the trading day so far. +1 OLHC (bull), -1 OHLC (bear).
    Tolerance = eps_frac x the day's open, so it never depends on later prices."""
    out = np.zeros(len(day), dtype=np.int64)
    if len(day) == 0:
        return out
    starts = np.flatnonzero(np.r_[True, day[1:] != day[:-1]])
    ends = np.r_[starts[1:], len(day)]
    for a, b in zip(starts, ends, strict=True):
        hh, ll = h[a:b], l[a:b]
        op = o[a]
        eps = max(eps_frac * op, 1e-9)
        k = b - a
        H, L = np.maximum.accumulate(hh), np.minimum.accumulate(ll)
        idx = np.arange(k)
        hit_h = np.abs(hh[None, :] - H[:, None]) < eps  # [t, s]
        hit_l = np.abs(ll[None, :] - L[:, None]) < eps
        valid = idx[None, :] <= idx[:, None]
        brk = (hit_h | hit_l) & valid
        b_idx = np.where(brk.any(1), brk.argmax(1), k - 1)
        b_is_high = hit_h[idx, b_idx]
        b_is_low = ~b_is_high & hit_l[idx, b_idx]
        up = np.flatnonzero(hh > op)
        dn = np.flatnonzero(ll < op)
        up0 = up[0] if len(up) else k
        dn0 = dn[0] if len(dn) else k
        hT = np.where(b_is_high, b_idx, np.where(up0 <= b_idx, up0, -1))
        lT = np.where(b_is_low, b_idx, np.where(dn0 <= b_idx, dn0, -1))
        high_first = (hT >= 0) & (lT >= 0) & (hT < lT)
        out[a:b] = np.where(high_first, BEAR, BULL)
    return out


class Strategy(Base):
    NAME = "ict_ea"
    ABOUT = "ICT confluence (owner swings on 1h, FVG/OB/PDA on 5m, daily OLHC bias), 2R, BE/partial/trail/timeout."
    PARAMS = {"min_conf": 3, "rr": 2.0, "pt_frac": 6.7e-6, "sl_buf": 20, "max_sl": 400, "min_sl": 30,
              "be_r": 0.5, "be_buf": 5, "trail_start": 100, "trail_step": 30, "timeout_min": 120,
              "risk_usd": 250.0, "max_trades": 3, "max_losses": 2, "day_loss": 1000.0, "day_gain": 750.0}

    def signals(self, df: pd.DataFrame, p: dict) -> pd.DataFrame:
        n = len(df)
        m5 = tf_candles(df, "5m")
        av = m5["avail"].to_numpy()
        keep = av < n
        m5, av = m5[keep].reset_index(drop=True), av[keep]
        o, h, l, c = (m5[k].to_numpy() for k in ("open", "high", "low", "close"))
        T = len(m5)
        # --- 1h structure inputs as known at each 5m candle's completion ---
        sw = swing_state(df, "1h", prev=True)
        sh1, sh2, sl1, sl2 = (sw[f"1h_{k}"].to_numpy()[av] for k in ("sh", "sh2", "sl", "sl2"))
        h1 = tf_candles(df, "1h")
        h1a = h1["avail"].to_numpy()
        hc, ho, hh, hl = (on_1m(h1[k], h1a, n)[av] for k in ("close", "open", "high", "low"))
        # --- 5m FVG and order blocks (newest first, as the source scans) ---
        bull_g = np.r_[False, False, h[:-2] < l[2:]]  # gap between candle q-2 and q
        bear_g = np.r_[False, False, h[2:] < l[:-2]]
        fq = _newest(bull_g | bear_g, 0, 18)
        rng = h - l
        body = np.abs(c - o)
        nxt_big = np.r_[(body[1:] / np.where(rng[1:] > 0, rng[1:], np.inf) > 0.6) & (rng[1:] > rng[:-1]), False]
        nxt_up = np.r_[c[1:] > o[1:], False]
        ob_bull = (c < o) & nxt_up & nxt_big
        ob_bear = (c > o) & np.r_[c[1:] < o[1:], False] & nxt_big
        oq = _newest(ob_bull | ob_bear, 1, 28)  # pair (q, q+1) with q+1 <= t
        hi50 = pd.Series(h).rolling(50, min_periods=1).max().to_numpy()
        lo50 = pd.Series(l).rolling(50, min_periods=1).min().to_numpy()
        day = pd.factorize(m5["day"].to_numpy())[0]
        live = in_session(df, m5)
        bias = daily_bias(day, o, h, l, 10 * p["pt_frac"])
        # --- structure state machine, updated every 5m candle like the source ---
        trend, last_sig = NONE, S_NONE
        rows, idx = [], []
        for t in range(T):
            if not (np.isnan(sh1[t]) or np.isnan(sh2[t]) or np.isnan(sl1[t]) or np.isnan(sl2[t]) or np.isnan(hc[t])):
                if sh1[t] > sh2[t] and sl1[t] > sl2[t]:
                    trend = BULL
                elif sh1[t] < sh2[t] and sl1[t] < sl2[t]:
                    trend = BEAR
                if trend == BULL and hc[t] > sh1[t]:
                    last_sig = S_BOS
                elif trend == BEAR and hc[t] < sl1[t]:
                    last_sig = S_BOS
                if trend == BULL and hc[t] < sl1[t]:
                    last_sig, trend = S_CHOCH, BEAR
                elif trend == BEAR and hc[t] > sh1[t]:
                    last_sig, trend = S_CHOCH, BULL
                if last_sig == S_CHOCH:
                    r = hh[t] - hl[t]
                    if r > 0 and abs(hc[t] - ho[t]) / r > 0.6:
                        last_sig = S_CISD
            # PDA
            swh, swl = sh1[t], sl1[t]
            if np.isnan(swh) or np.isnan(swl) or swh <= swl:
                swh, swl = hi50[t], lo50[t]
            eq = (swh + swl) / 2
            bull = bear = 0
            bull += trend == BULL
            bear += trend == BEAR
            if last_sig in (S_CISD, S_BOS):
                bull += trend == BULL
                bear += trend == BEAR
            bull += c[t] < eq
            bear += c[t] > eq
            q = fq[t]
            if q >= 0:
                bull += bool(bull_g[q])
                bear += bool(bear_g[q]) and not bull_g[q]
            k = oq[t]
            if k >= 0:
                bull += bool(ob_bull[k])
                bear += bool(ob_bear[k])
            bull += 2 * (bias[t] == BULL)
            bear += 2 * (bias[t] == BEAR)
            if bull >= p["min_conf"] and bull > bear:
                sd = 1
            elif bear >= p["min_conf"] and bear > bull:
                sd = -1
            else:
                continue
            if not live[t]:
                continue
            entry = round(c[t] / TICK) * TICK
            pt = p["pt_frac"] * entry
            if sd == 1:
                base = l[k] if (k >= 0 and ob_bull[k]) else sl1[t]
                stop = base - p["sl_buf"] * pt
            else:
                base = h[k] if (k >= 0 and ob_bear[k]) else sh1[t]
                stop = base + p["sl_buf"] * pt
            if np.isnan(stop):
                continue
            dist = (entry - stop) * sd
            if dist > p["max_sl"] * pt:
                dist = p["max_sl"] * pt
            dist_t = int(round(dist / TICK))
            if dist <= 0 or dist < p["min_sl"] * pt or dist_t < 1:
                continue
            qty = int(np.clip(np.floor(p["risk_usd"] / (dist_t * TICK_VALUE)), 1, 5))
            stop_px = entry - sd * dist_t * TICK
            tgt = entry + sd * round(dist_t * p["rr"]) * TICK
            part_q = qty - 1 if qty >= 2 else 0
            part_t = entry + sd * dist_t * TICK if part_q else np.nan
            rows.append((sd, entry, stop_px, tgt, 5, qty, part_q, part_t))
            idx.append(av[t])
        self._c = close_ticks(df)
        self._minute = pd.DatetimeIndex(df["ts"]).as_unit("ns").asi8 // 60_000_000_000
        self._pt_ticks = p["pt_frac"] * df["close"].to_numpy() / TICK
        self._p = p
        out = pd.DataFrame(rows, columns=["side", "limit", "stop", "target", "expire_min", "qty", "part_qty",
                                          "part_target"], index=idx)
        return out[~out.index.duplicated(keep="last")]  # two candles complete on one bar: the newer decides

    def manage(self, ctx):
        p = self._p
        if "R" not in ctx.state:
            ctx.state["R"] = ctx.E - ctx.S
        R = ctx.state["R"]
        px = ctx.to_side(int(self._c[ctx.m - 1]))
        prof = px - ctx.E
        if self._minute[ctx.m - 1] + 1 - self._minute[ctx.j] >= p["timeout_min"] and prof < 0:  # clock time
            return ctx.S, True
        S = ctx.S
        pt = self._pt_ticks[ctx.m - 1]
        if prof >= p["be_r"] * R:
            S = max(S, ctx.E + int(round(p["be_buf"] * pt)))
        if prof >= p["trail_start"] * pt:
            S = max(S, px - max(int(round(p["trail_step"] * pt)), 1))
        return S, False

    def day_rules(self, trades: pd.DataFrame, p: dict) -> pd.DataFrame:
        keep = []
        for _, g in trades.groupby("trading_day", sort=False):
            count = losses = 0
            pnl = 0.0
            for i, net, last_leg, part in zip(g.index, g["net"], g["ticks"], g["part_exit"], strict=True):
                if count >= p["max_trades"] or losses >= p["max_losses"] or pnl <= -p["day_loss"] \
                        or pnl >= p["day_gain"]:
                    break
                keep.append(i)
                count += 1
                pnl += net
                # source counts closing deals by their profit before commission; a partial close is a win
                # (resets the count) and the last leg decides
                if not np.isnan(part):
                    losses = 0  # the partial sits past the entry, so it is always a winning deal
                losses = losses + 1 if last_leg < 0 else 0
        return trades.loc[keep]
