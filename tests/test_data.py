import json

import pandas as pd
import pytest

from cltester.config import DATA_DIR, MANIFEST
from cltester.update import assert_cl, next_contracts


@pytest.mark.parametrize("bad", ["MCLZ6", "MCL", "CL", "NGZ6", "CLZ6-CLF7", "QMZ6"])
def test_only_cl_allowed(bad):
    with pytest.raises(ValueError):
        assert_cl(bad)


def test_cl_allowed():
    assert_cl("CLZ6")
    assert next_contracts("CLZ6", 3) == ["CLZ6", "CLF7", "CLG7"]


@pytest.mark.skipif(not MANIFEST.exists(), reason="no local data")
def test_stored_data_is_clean():
    man = json.loads(MANIFEST.read_text())
    df = pd.read_parquet(DATA_DIR / f"year={pd.Timestamp(man['last_bar']).year}.parquet")
    assert df["ts"].is_monotonic_increasing and df["ts"].is_unique
    assert df["raw_symbol"].str.fullmatch(r"CL[FGHJKMNQUVXZ]\d").all()
    assert ((df["low"] <= df[["open", "close"]].min(axis=1)) & (df["high"] >= df[["open", "close"]].max(axis=1))).all()


@pytest.mark.skipif(not MANIFEST.exists(), reason="no local data")
def test_periods_cut_on_whole_trading_days():
    from cltester.data import load_period

    v = load_period("holdout")
    last_day = v["trading_day"].max()
    assert last_day < pd.Timestamp("2026-11-12")
    assert (v["ct_minute"].iloc[-1] < 17 * 60)  # ends before the 17:00 CT reopen, not mid-session


def test_holdout_guard_covers_overlapping_periods():
    from cltester.cli import _touches_holdout

    assert _touches_holdout("holdout") and _touches_holdout("all")
    assert not any(_touches_holdout(p) for p in ("dev", "validation", "forward"))


def test_second_update_is_refused_while_one_runs():
    import fcntl

    from cltester import update

    with open(DATA_DIR.parent / ".update.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with pytest.raises(SystemExit, match="another update"):
            update.run("massive")
