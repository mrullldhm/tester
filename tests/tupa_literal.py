"""Literal bar-by-bar transcription of strategies/tupa_trade.pine, used as the reference for the vectorized
strategies/tupa_trade.py. Every bar runs the same steps in the same order as the Pine script: feed the bar to each
timeframe accumulator (closing candles), update the 1m swings, then the order logic."""

import numpy as np

from tvtester.engine import LONG, SHORT
from tvtester.strategy import Strategy

NY = "America/New_York"
SH, SL = 1, -1
TFS = ("5m", "15m", "1h", "4h", "1d")


def pine_eq(a, b):
    """Pine equality is false when either operand is na (represented by None)."""
    return a is not None and b is not None and a == b


def pine_ne(a, b):
    """Pine inequality is also false for na; it is not the negation of pine_eq."""
    return a is not None and b is not None and a != b


def open_rule(o, h, l):
    return (h - o) < (o - l)


class Zig:
    def copy(self):
        other = Zig()
        other.__dict__ = {k: v.copy() if k == "before" and v is not None else v
                          for k, v in self.__dict__.items()}
        return other

    def __init__(self):
        self.last_type, self.last_price = 0, None
        self.cur_h = self.prev_h = self.cur_l = self.prev_l = None
        self.n_h = self.n_l = 0
        self.bar_h = self.bar_l = None
        self.hi_since_l = self.lo_since_h = None
        self.pending = False
        self.before = None
        self.min_since_l = self.max_since_h = None

    def invalidate(self, h, l):
        if self.min_since_l is not None:
            self.min_since_l = min(self.min_since_l, l)
        if self.max_since_h is not None:
            self.max_since_h = max(self.max_since_h, h)
        if self.before is not None:
            if self.before["min_since_l"] is not None:
                self.before["min_since_l"] = min(self.before["min_since_l"], l)
            if self.before["max_since_h"] is not None:
                self.before["max_since_h"] = max(self.before["max_since_h"], h)
        if not self.pending or not (h >= self.last_price if self.last_type == SH else l <= self.last_price):
            return False
        if self.last_type == SH:
            self.n_h += 1
        else:
            self.n_l += 1
        observed_h, observed_l = self.hi_since_l, self.lo_since_h
        for name, value in self.before.items():
            setattr(self, name, value)
        self.pending = False
        self.before = None
        if observed_h is not None:
            self.hi_since_l = observed_h if self.hi_since_l is None else max(self.hi_since_l, observed_h)
        if observed_l is not None:
            self.lo_since_h = observed_l if self.lo_since_h is None else min(self.lo_since_h, observed_l)
        if self.hi_since_l is not None:
            self.hi_since_l = max(self.hi_since_l, h)
        if self.lo_since_h is not None:
            self.lo_since_h = min(self.lo_since_h, l)
        return True

    def visit(self, t, p, b, is_pivot):
        extreme = (self.hi_since_l is None or p >= self.hi_since_l) if t == SH else (
            self.lo_since_h is None or p <= self.lo_since_h)
        added = self.push(t, p, b) if is_pivot and extreme else False
        if added:
            if t == SH:
                self.lo_since_h = p
            else:
                self.hi_since_l = p
        if self.before is not None:
            name = "hi_since_l" if t == SH else "lo_since_h"
            if self.before[name] is not None:
                self.before[name] = max(self.before[name], p) if t == SH else min(self.before[name], p)
        if t == SH and self.hi_since_l is not None:
            self.hi_since_l = max(self.hi_since_l, p)
        if t == SL and self.lo_since_h is not None:
            self.lo_since_h = min(self.lo_since_h, p)
        return added

    def push(self, t, p, b):
        accepts = self.last_type != t or (p >= self.last_price if t == SH else p <= self.last_price)
        if accepts:
            if self.last_type != t or not self.pending:
                self.before = {name: getattr(self, name) for name in (
                    "last_type", "last_price", "cur_h", "prev_h", "cur_l", "prev_l", "bar_h", "bar_l",
                    "hi_since_l", "lo_since_h", "min_since_l", "max_since_h")}
            self.pending = True
        if self.last_type == t:
            more = p >= self.last_price if t == SH else p <= self.last_price
            if not more:
                return False
            self.last_price = p
            if t == SH:
                self.cur_h, self.bar_h, self.n_h = p, b, self.n_h + 1
            else:
                self.cur_l, self.bar_l, self.n_l = p, b, self.n_l + 1
            return True
        if t == SH:
            self.prev_h, self.cur_h, self.bar_h, self.n_h = self.cur_h, p, b, self.n_h + 1
        else:
            self.prev_l, self.cur_l, self.bar_l, self.n_l = self.cur_l, p, b, self.n_l + 1
        self.last_type, self.last_price = t, p
        return True

    def hl(self):
        return self.cur_l is not None and self.prev_l is not None and self.cur_l > self.prev_l

    def lh(self):
        return self.cur_h is not None and self.prev_h is not None and self.cur_h < self.prev_h


class Tf:
    """One higher timeframe: candle accumulator, last three closed candles, swings, trend."""

    def __init__(self):
        self.id = None
        self.buf = []  # closed candles (h, l, hi_first), last three
        self.z = Zig()
        self.trend, self.dn_used, self.up_used = 0, False, False

    def levels(self):
        dn = self.z.cur_l if (self.z.hl() and not self.dn_used) else None
        up = self.z.cur_h if (self.z.lh() and not self.up_used) else None
        return dn, up

    def start(self, cid, i, o, h, l):
        self.opening = self.z.copy()
        self.id, self.h, self.l = cid, h, l
        self.hi_i = self.lo_i = i
        self.same_hf = open_rule(o, h, l)
        self.fd = self.fu = None
        self.tie_hf = None
        self.touch(i, o, h, l)

    def add(self, i, o, h, l):
        if h > self.h:
            self.h, self.hi_i = h, i
        if l < self.l:
            self.l, self.lo_i = l, i
        if self.hi_i == i and self.lo_i == i:
            self.same_hf = open_rule(o, h, l)
        self.touch(i, o, h, l)

    def touch(self, i, o, h, l):
        dn, up = self.levels()
        new_d = self.fd is None and dn is not None and l <= dn
        new_u = self.fu is None and up is not None and h >= up
        if new_d:
            self.fd = i
        if new_u:
            self.fu = i
        if new_d and new_u:
            self.tie_hf = open_rule(o, h, l)

    def close(self):
        if self.hi_i < self.lo_i:
            hf = True
        elif self.hi_i > self.lo_i:
            hf = False
        else:
            hf = self.same_hf
        if self.fd is not None and self.fu is not None:
            up_last = (not self.tie_hf) if pine_eq(self.fd, self.fu) else self.fu > self.fd
            self.trend, self.dn_used, self.up_used = (1 if up_last else -1), True, True
        elif self.fd is not None:
            self.trend, self.dn_used = -1, True
        elif self.fu is not None:
            self.trend, self.up_used = 1, True
        self.buf.append((self.h, self.l, hf))
        self.buf = self.buf[-3:]
        if len(self.buf) == 3:
            (h1, l1, _), (hk, lk, hfk), (h2, l2, _) = self.buf
            is_h = h1 <= hk and h2 < hk
            is_l = l1 >= lk and l2 > lk
            order = [(SH, hk), (SL, lk)] if hfk else [(SL, lk), (SH, hk)]
            if self.opening.pending and not self.z.pending:
                probe = self.opening.copy()
                accepted = [probe.visit(t, p, None, is_h if t == SH else is_l) for t, p in order]
                if any(accepted):
                    nh, nl = self.z.n_h, self.z.n_l
                    self.z = self.opening.copy()
                    self.z.n_h, self.z.n_l = nh, nl
            for t, p in order:
                if self.z.visit(t, p, None, is_h if t == SH else is_l):
                    if t == SH:
                        self.up_used = False
                    else:
                        self.dn_used = False
        self.id = None


def cid(t, tf):
    """Candle id of a UTC pandas Timestamp (and its New York minute of day)."""
    lt = t.tz_convert(NY)
    m = lt.hour * 60 + lt.minute
    if tf in ("5m", "15m", "1h"):
        ms = {"5m": 300_000, "15m": 900_000, "1h": 3_600_000}[tf]
        return t.value // 1_000_000 // ms, m
    import pandas as pd
    d = (t + pd.Timedelta(hours=6)).tz_convert(NY)
    day = d.year * 10000 + d.month * 100 + d.day
    return (day * 10 + ((m + 360) % 1440) // 240 if tf == "4h" else day), m


class LiteralTupa(Strategy):
    name = "tupa_literal"

    def __init__(self, t_min="1h", tp=25, max_risk=25, open_minute=9 * 60, flat_minute=14 * 60 + 30):
        super().__init__(t_min=t_min, tp=tp, max_risk=max_risk)
        self.k0 = TFS.index(t_min)
        self.open_minute, self.flat_minute = open_minute, flat_minute

    def prepare(self, bars):
        import pandas as pd
        self.bars = bars
        self.tfs = [Tf() for _ in TFS]
        self.z1 = Zig()
        self.cur_day, self.traded, self.n_closed = None, False, 0
        self.expired = None
        self.pend, self.trig = None, False
        self.next_t = bars.ts + pd.Timedelta(minutes=1)
        self.bias_log = np.zeros(len(bars), dtype=np.int8)
        return np.ones(len(bars), dtype=bool)

    def _indicators(self, i):
        b = self.bars
        o, h, l = int(b.o[i]), int(b.h[i]), int(b.l[i])
        t, tn = b.ts[i], self.next_t[i]
        for tf, f in zip(TFS, self.tfs):
            c, _ = cid(t, tf)
            cn, _ = cid(tn, tf)
            if f.id is not None and pine_ne(c, f.id):
                f.close()  # the previous candle missed its last minute: closed now
            if f.id is None:
                f.start(c, i, o, h, l)
            else:
                f.add(i, o, h, l)
            if cn != c:
                f.close()
            f.z.invalidate(h, l)
        # 1m swings: candle i-1 confirmed by bar i
        z = self.z1
        if i >= 2:
            hk1, hk, lk1, lk = int(b.h[i - 2]), int(b.h[i - 1]), int(b.l[i - 2]), int(b.l[i - 1])
            is_h = hk1 <= hk and h < hk
            is_l = lk1 >= lk and l > lk
            hf = open_rule(int(b.o[i - 1]), hk, lk)
            order = [(SH, hk), (SL, lk)] if hf else [(SL, lk), (SH, hk)]
            for tp_, p in order:
                if z.visit(tp_, p, i - 1, is_h if tp_ == SH else is_l):
                    if tp_ == SH:
                        z.max_since_h = h
                    else:
                        z.min_since_l = l
        z.invalidate(h, l)

    def _bias(self):
        for d, cand in ((SHORT, SL), (LONG, SH)):
            for k in range(self.k0, len(TFS)):
                if self.tfs[k].z.pending and self.tfs[k].z.last_type == cand:
                    if all(self.tfs[j].trend == d for j in range(k)):
                        return d
                    break
        return 0

    def _setup(self, bias):
        z, R = self.z1, self.params["max_risk"]
        if bias == SHORT and z.pending and z.last_type == SH and z.hl() and z.min_since_l > z.cur_l:
            bp, sl = z.cur_l, z.cur_h
            return SHORT, bp, sl, (sl - R if sl - bp > R else bp), z.n_h
        if bias == LONG and z.pending and z.last_type == SL and z.lh() and z.max_since_h < z.cur_h:
            bp, sl = z.cur_h, z.cur_l
            return LONG, bp, sl, (sl + R if bp - sl > R else bp), z.n_l
        return None

    def _cancel(self, ctx):
        if self.pend is not None:
            ctx.cancel("Long" if self.pend[0] == LONG else "Short")
            ctx.cancel("Exit")
        self.pend, self.trig = None, False

    def on_bar(self, ctx, i):
        self._indicators(i)
        bias = self._bias()
        self.bias_log[i] = bias
        lt = self.bars.ts[i].tz_convert(NY)
        mod = lt.hour * 60 + lt.minute
        day = lt.year * 10000 + lt.month * 100 + lt.day
        win = self.open_minute - 1 <= mod < self.flat_minute - 1
        if self._new_session(day):
            self.cur_day, self.traded = day, False
        if ctx.position_size != 0 or ctx.closed_trades != self.n_closed:
            self.n_closed, self.traded = ctx.closed_trades, True
            self.pend, self.trig = None, False
        if ctx.position_size != 0:
            if not win:
                ctx.close_all("Session end")
            return
        if not win or self.traded or self.bars.last_of_contract[i]:
            self._cancel(ctx)
            return
        b = self.bars
        if self.pend is not None:
            d, bp, _, lim = self.pend[:4]
            target = lim + d * self.params["tp"]
            if (b.h[i] >= target) if d == LONG else (b.l[i] <= target):
                self.expired = self.pend[:5]
                self._cancel(ctx)
                return
            if not self.trig and i > self.pend[5] and (b.l[i] <= bp if d == SHORT else b.h[i] >= bp):
                self.trig = True
            if self.trig:
                cnt = self.z1.n_h if d == SHORT else self.z1.n_l
                if cnt == self.pend[4]:
                    return
                self._cancel(ctx)
        want = self._setup(bias)
        if want is None or want == self.expired:
            self._cancel(ctx)
            return
        if self.pend is not None and self.pend[:4] == want[:4]:
            return
        self._cancel(ctx)
        d, bp, sl, lim, cnt = want
        eid = "Long" if d == LONG else "Short"
        ctx.entry(eid, d, stop=bp, limit=lim)
        ctx.exit("Exit", eid, stop=sl, profit=self.params["tp"])
        self.pend, self.trig = (d, bp, sl, lim, cnt, i), False

    def _new_session(self, day):
        # Pine: if na(curDay) or dayKey != curDay
        return self.cur_day is None or pine_ne(day, self.cur_day)
