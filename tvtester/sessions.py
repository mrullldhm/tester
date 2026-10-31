"""CL1! trading sessions. Each uses its own IANA time zone: the US, the UK and Asia change clocks on
different dates (or not at all), so a fixed UTC offset would be wrong for weeks every year.

Open times verified on CL front-month volume (median contracts per minute, 2024-2025): the session-open
minute is 4-12x the minutes before it. docs/SESSIONS.md has the table.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Session:
    name: str
    tz: str
    open_minute: int  # local minute of day the session opens
    flat_minute: int  # local minute of day every position must be flat

    @property
    def anchor_minute(self) -> int:
        """The candle before the open (9:29 ET in the original 9:30 ET script)."""
        return self.open_minute - 1


ASIA = Session("asia", "Asia/Shanghai", 9 * 60, 15 * 60)  # 09:00 UTC+8 (Shanghai/Singapore/KL), no DST
LONDON = Session("london", "Europe/London", 8 * 60, 13 * 60)  # 08:00 London (GMT/BST)
NEW_YORK = Session("ny", "America/New_York", 9 * 60, 14 * 60 + 30)  # 09:00 ET, NYMEX crude open; 14:30 settle
SESSIONS = {s.name: s for s in (ASIA, LONDON, NEW_YORK)}


def local_clock(ts: pd.DatetimeIndex, tz: str) -> tuple[np.ndarray, np.ndarray]:
    """(minute of day, yyyymmdd day key) of each bar open in the given time zone."""
    lt = ts.tz_convert(tz)
    return (lt.hour * 60 + lt.minute).to_numpy(), (lt.year * 10000 + lt.month * 100 + lt.day).to_numpy()
