"""juda_swing_point: one synthetic long setup trades on one contract and is refused across a roll (Codex review
2026-11-18: prices are not back-adjusted, so a roll could fake the sweep, confirmation and stop)."""

import numpy as np
import pandas as pd
import pytest

from cltester.data import add_session
from cltester.strategy import load

WARMUP = 60
B = 80.0


def _candles() -> list[tuple[float, float, float, float, str]]:
    """15m candles (open, high, low, close, order). order 'hl': high prints before low; 'lh': low first."""
    out = []
    for i in range(WARMUP):  # steady uptrend: EMA 10 > 20 > 50, no swing points (every candle higher)
        lo = 70.0 + 0.10 * i
        out.append((lo + 0.02, lo + 0.10, lo, lo + 0.10, "lh"))
    out += [
        (B + 0.02, B + 0.10, B, B + 0.10, "lh"),              # k0
        (B + 0.10, B + 0.30, B + 0.05, B + 0.28, "lh"),       # k1: swing high 80.30
        (B + 0.25, B + 0.25, B + 0.10, B + 0.20, "hl"),       # k2: lower high confirms k1
        (B + 0.20, B + 0.35, B + 0.05, B + 0.20, "hl"),       # k3: breaks 80.30, then takes k2's low: manipulation
        (B + 0.20, B + 0.30, B + 0.15, B + 0.25, "lh"),       # k4: holds above 80.05: confirmation
        (B + 0.25, B + 0.27, B + 0.22, B + 0.25, "lh"),
        (B + 0.25, B + 0.27, B + 0.22, B + 0.25, "lh"),
    ]
    return out


def _bars(roll_at: int | None) -> pd.DataFrame:
    """1m bars from 17:00 CT; candles from index roll_at on trade on CLG5 (CLF5 before)."""
    rows = []
    t0 = pd.Timestamp("2024-12-09 17:00", tz="America/Chicago")
    for k, (o, h, lo, c, order) in enumerate(_candles()):
        sym = "CLG5" if roll_at is not None and k >= roll_at else "CLF5"
        mid_h, mid_l = max(o, c), min(o, c)
        first, second = (2, 6) if order == "hl" else (6, 2)  # minute of the high / of the low
        for i in range(15):
            bh = h if i == first else mid_h
            bl = lo if i == second else mid_l
            bo = o if i == 0 else mid_l
            bc = c if i == 14 else mid_l
            rows.append((t0 + pd.Timedelta(minutes=15 * k + i), sym, bo, max(bh, bo, bc), min(bl, bo, bc), bc))
    df = pd.DataFrame(rows, columns=["ts", "raw_symbol", "open", "high", "low", "close"])
    df["ts"] = df["ts"].dt.tz_convert("UTC")
    df["volume"], df["vendor"] = 1, "test"
    return add_session(df)


@pytest.mark.parametrize("stop,limit,stop_px", [("confirm", 80.25, 80.15), ("manip", 80.20, 80.05)])
def test_one_contract_trades(stop, limit, stop_px):
    s = load("juda_swing_point")
    sig = s.signals(_bars(None), {**s.PARAMS, "stop": stop})
    assert len(sig) == 1 and sig["side"].iat[0] == 1
    assert sig["limit"].iat[0] == pytest.approx(limit) and sig["stop"].iat[0] == pytest.approx(stop_px)
    assert sig.index[0] == (WARMUP + 5) * 15 - 1  # close of the confirmation candle's last minute


@pytest.mark.parametrize("stop", ["confirm", "manip"])
# roll at: k1 swing high (its left candle k0 is the old contract), k2 (manipulation reference), k3 manipulation,
# k4 confirmation
@pytest.mark.parametrize("roll_at", [WARMUP + 1, WARMUP + 2, WARMUP + 3, WARMUP + 4])
def test_roll_inside_the_setup_is_refused(stop, roll_at):
    s = load("juda_swing_point")
    p = {**s.PARAMS, "stop": stop}
    setups = s.setups(_bars(roll_at), p)
    assert s.signals(_bars(roll_at), p).empty
    assert (setups["why"] == "contract roll inside the setup").sum() == 1
    assert not np.isfinite(setups["limit"].to_numpy(float)).any()


def test_roll_before_the_swing_reference_still_trades():
    """Roll at k0: the swing high's left candle onward is one contract, so the setup is clean."""
    s = load("juda_swing_point")
    assert len(s.signals(_bars(WARMUP), s.PARAMS)) == 1


def _tp_bar(open_: float, low: float) -> pd.DataFrame:
    """Control setup (stop confirm: buy 80.25, stop 80.15, TP 15 = 80.40); the first working bar reaches the TP."""
    df = _bars(None)
    i = (WARMUP + 5) * 15  # first bar after the signal
    df.loc[i, ["open", "high", "low", "close"]] = [open_, 80.40, low, 80.30]
    return df


def _trades(df: pd.DataFrame, through: int = 0) -> pd.DataFrame:
    from cltester.data import Bars
    from cltester.engine import Fills, backtest

    s = load("juda_swing_point")
    sig = s.signals(df, {**s.PARAMS, "cancel": "tp", "stop": "confirm"})
    assert len(sig) == 1 and sig["expire"].iat[0] == 1 and sig["kill"].iat[0] == pytest.approx(80.40)
    return backtest(Bars.from_frame(df), sig, Fills(through=through))


def test_tp_cancel_keeps_an_order_filled_at_the_open_before_the_tp_touch():
    """Codex review 2026-11-18: the bar opens at the limit, so the fill came first; the trade must exist."""
    t = _trades(_tp_bar(80.25, 80.10))
    assert len(t) == 1 and t["reason"].iat[0] == "stop"  # stop on the fill bar (worst case)


def test_tp_cancel_drops_the_order_when_the_tp_bar_opens_above_the_limit():
    """Opens above the limit, reaches TP and the limit: order inside the bar unknown, cancelled."""
    assert _trades(_tp_bar(80.30, 80.10)).empty


def test_tp_cancel_with_strict_fills_needs_the_open_beyond_the_fill_level():
    """Codex review 2026-11-18 (2nd): --through 1, open at the limit 80.25 is not a fill; low 80.24 and TP in the same
    bar: order unknown, cancelled. Touch fills: the open filled first."""
    assert _trades(_tp_bar(80.25, 80.24), through=1).empty
    assert len(_trades(_tp_bar(80.25, 80.24))) == 1
