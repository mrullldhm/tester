# CL1! sessions: verified open times

CL (NYMEX WTI crude oil futures) trades on CME Globex almost 24 hours: Sunday to Friday, 18:00 to 17:00
New York time, with a 60-minute halt every day. The exchange does not define "Asia", "London" or "New York"
sessions. A session open is the minute when that region's traders arrive and volume jumps. We measured that
jump on our own CL front-month data instead of trusting rules of thumb.

## Method
Median contracts traded per 1-minute bar, front month, all trading days in 2024 and 2025, by local clock time
in each region's own time zone. The open minute is the one where the median jumps.

| Session | Minutes before the open (median volume) | Open minute | Open-minute volume | Jump |
|---|---|---|---|---|
| Asia, 09:00 Asia/Shanghai (UTC+8) | 08:55-08:58: 16-17 | **09:00** | 204 | about 12x |
| Asia, 09:00 Asia/Tokyo (UTC+9), for comparison | 08:55-08:58: 8-9 | 09:00 | 93 | weaker |
| London, 08:00 Europe/London | 07:55-07:58: 41-46 | **08:00** | 168 | about 4x |
| London, 07:00 Europe/London, for comparison | 06:55-06:58: 18-19 | 07:00 | 51 | weaker |
| New York, 09:00 America/New_York | 08:55-08:58: 158-175 | **09:00** | 1,001 | about 6x |
| New York, 08:30 (US data releases), for comparison | 08:25-08:29: 99-125 | 08:30 | 212 | smaller |

## Result

| Session | Open | Anchor candle (the "9:29" of this session) | Malaysia time (UTC+8) | Flat time used |
|---|---|---|---|---|
| Asia | 09:00 UTC+8 (Shanghai, Singapore, Kuala Lumpur). No daylight saving | 08:59 | **09:00** all year | 15:00 UTC+8 |
| London | 08:00 London (GMT in winter, BST in summer) | 07:59 | **15:00** UK summer, **16:00** UK winter | 13:00 London |
| New York | 09:00 New York (EST / EDT), the NYMEX crude open | 08:59 | **21:00** US summer, **22:00** US winter | 14:30 New York (settlement) |

**Your statement is correct:** the CL New York open is 21:00 Malaysia time during US daylight saving time and 22:00
when the US is on standard time. (US daylight saving time ends on Sunday 1 November 2026, so the NY open moves to
22:00 Malaysia time from Monday 2 November 2026.)

## Why each session uses its own time zone
The US and the UK change their clocks on different dates. For about three weeks in March and one week around
late October / early November, London and New York are 4 hours apart instead of 5. Asia (UTC+8) never changes.
A fixed UTC offset would put the anchor candle on the wrong minute during those weeks. The tester converts every
bar to the session's own time zone (`tvtester/sessions.py`). A test checks the port across the March 2024
transition weeks.
