"""Read-only audit probes; outputs only, no data/code mutations."""
import numpy as np
import pandas as pd
import cltester.swings as sw
from cltester.data import load_period
from strategies.rlm import Book, COMBOS, swing_events

df = load_period('dev')
df = df[df.trading_day < pd.Timestamp('2011-01-01')].reset_index(drop=True)
print('bars', len(df), flush=True)
contract = np.cumsum(np.r_[False, df.raw_symbol.to_numpy()[1:] != df.raw_symbol.to_numpy()[:-1]])
for tf in ('5m', '15m', '1h'):
    cd = sw.build_candles(df, tf)
    mixed = contract[cd.first] != contract[cd.last]
    delayed_roll = contract[cd.last] != contract[cd.avail]
    print('roll', tf, 'mixed', mixed.sum(), 'delayed', delayed_roll.sum(), flush=True)

cd = sw.build_candles(df, '5m')
orig = sw._record
snap = []
def record(stack, state, k):
    snap.append(tuple((p.kind, p.candle) for p in stack))
    orig(stack, state, k)
sw._record = record
sw.detect(cd)
sw._record = orig
ev = swing_events(df, '5m', 'confirm')
actual = {(int(r.known), int(r.kind), int(r.candle)) for r in ev.itertuples() if r.op < 0}
missed = []
false = []
for k in range(1, len(snap)-1):
    old, new = snap[k-1], snap[k]
    for pt in old[-4:]:
        want = pt not in new
        got = (int(cd.avail[k+1]), *pt) in actual
        if want and not got:
            missed.append((k, pt, old[-4:], new[-4:]))
        if got and not want:
            false.append((k, pt, old[-4:], new[-4:]))
print('withdraw missed', len(missed), 'false', len(false), flush=True)
print('examples', missed[:2], false[:2], flush=True)

# Crossed contributions must be withdrawn at their remaining, rather than initial, strength.
b = Book(len(COMBOS), .6)
b.touch((0, sw.LOW, 1), sw.LOW, 1000, 10, 14, 1., 10., 1010., 0)
b.touch((0, sw.LOW, 2), sw.LOW, 1001, 20, 24, 1., 10., 1010., 0)
b.age_cross(980., b.decay, 1)
b.withdraw((0, sw.LOW, 1), 10., 1)
s = np.flatnonzero(b.alive)[0]
print('withdraw_cross actual', b.strength[s], 'expected', b.decay * .7, flush=True)

# Same TF may have two pids contained in the higher-TF representative.
b = Book(len(COMBOS), .6)
b.touch((2, sw.LOW, 0), sw.LOW, 1000, 0, 59, 2., 10., 1010., 0)
b.touch((0, sw.LOW, 1), sw.LOW, 1000, 10, 14, 1., 10., 1010., 0)
b.touch((0, sw.LOW, 2), sw.LOW, 1000, 20, 24, 1., 10., 1010., 0)
b.withdraw((0, sw.LOW, 1), 10., 0)
b.withdraw((2, sw.LOW, 0), 10., 0)
print('dedupe surviving lower pid', (0, sw.LOW, 2) in b.pid, 'alive', b.alive.sum(), flush=True)
