"""FSP New York session entry/reset clock; no swing detection or future-bar gap inference.

Regular CL close changed from 17:15 ET to 17:00 ET in September 2015. Holiday-close facts
follow the CL schedule in pandas_market_calendars' CME Globex calendar (reviewed 2026-11-11):
https://github.com/rsheftel/pandas_market_calendars/blob/master/pandas_market_calendars/calendars/cme_globex_energy_and_metals.py
https://github.com/rsheftel/pandas_market_calendars/blob/master/pandas_market_calendars/holidays/cme_globex.py
This is a bounded local schedule through 2026, not a claim of a complete future exchange calendar.
Missing deadline bars cannot be replaced with a hindsight-selected previous price.
"""
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

from .sessions import NEW_YORK, local_clock


def _weekday(year, month, weekday, occurrence):
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (occurrence - 1))


def _observed(day):
    return day - timedelta(days=1) if day.weekday() == 5 else day + timedelta(days=1) if day.weekday() == 6 else day


def cl_daily_close_minutes(day):
    """Scheduled closing minute in New York time; None means no trading session."""
    if not 2010 <= day.year <= 2026:
        raise ValueError("FSP CL daily-close calendar is verified only for 2010–2026")
    year = day.year
    from dateutil.easter import easter

    ny = date(year, 1, 1)
    ny_observed = ny + timedelta(days=1) if ny.weekday() == 6 else ny
    if day.weekday() >= 5 or day in (ny_observed, _observed(date(year, 12, 25)), easter(year) - timedelta(days=2)):
        return None
    close = 17 * 60 + (15 if day < date(2015, 9, 21) else 0)
    thanksgiving = _weekday(year, 11, 3, 4)
    memorial = date(year, 5, 31)
    memorial -= timedelta(days=memorial.weekday())
    holidays = {_weekday(year, 1, 0, 3), _weekday(year, 2, 0, 3), memorial,
                _observed(date(year, 7, 4)), _weekday(year, 9, 0, 1), thanksgiving}
    if year >= 2022:
        holidays.add(_observed(date(year, 6, 19)))
    if day in holidays:
        close = 14 * 60 + 30 if year >= 2022 else 13 * 60
    if day == thanksgiving + timedelta(days=1):
        close = 14 * 60 + 45 if year >= 2024 else 13 * 60 + 45
    if day.month == 12 and day.day == 24 and day.weekday() < 4:
        close = 13 * 60 + 45
    if day in (date(2025, 7, 4), date(2026, 6, 19), date(2026, 7, 3)):
        close = 13 * 60
    if day == date(2010, 12, 31):
        close = 16 * 60 + 15
    return close


@dataclass
class FSPClock:
    day: np.ndarray
    deadline: np.ndarray  # earlier of NY session close and CL exchange close, in UTC ms
    session_close: np.ndarray
    signal_window: np.ndarray
    fill_window: np.ndarray


def trading_clock(bars):
    local_ts = bars.ts.tz_convert(NEW_YORK.tz)
    # A reset cycle ends at the next scheduled NY close. A NEW setup after today's
    # cutoff belongs to the next cycle, including before the CL evening reopen.
    # Only the schedule determines the cycle; no future price bars are consulted.
    dates = pd.date_range(local_ts[0].date() - timedelta(days=1),
                          local_ts[-1].date() + timedelta(days=10), freq="D")
    deadlines = []
    keys = []
    for stamp in dates:
        d = stamp.date()
        if not 2010 <= d.year <= 2026:
            continue
        minute = cl_daily_close_minutes(d)
        if minute is None:
            continue
        minute = min(minute, NEW_YORK.flat_minute)
        local = pd.Timestamp(d) + pd.Timedelta(minutes=minute)
        deadlines.append(local.tz_localize(NEW_YORK.tz).tz_convert("UTC").value // 1_000_000)
        keys.append(d.year * 10000 + d.month * 100 + d.day)
    scheduled = np.asarray(deadlines, dtype=np.int64)
    cycle = np.searchsorted(scheduled, bars.t_ms, side="right")
    if not len(scheduled) or np.any(cycle == len(scheduled)):
        raise ValueError("FSP NY reset schedule must cover every bar and its next session close")
    deadline = scheduled[cycle]
    day = np.asarray(keys, dtype=np.int64)[cycle]
    mod, local_day = local_clock(bars.ts, NEW_YORK.tz)
    close_ms = bars.t_ms + 60_000
    # Signals at the 08:59 close may place orders active from 09:00. No new 14:30 entries.
    close_mod = (mod + 1) % 1440
    signals = ((close_mod >= NEW_YORK.open_minute) & (close_mod < NEW_YORK.flat_minute)
               & (close_ms < deadline) & (local_day == day))
    fills = ((mod >= NEW_YORK.open_minute) & (mod < NEW_YORK.flat_minute)
             & (bars.t_ms < deadline) & (local_day == day))
    return FSPClock(day, deadline, close_ms == deadline, signals, fills)
