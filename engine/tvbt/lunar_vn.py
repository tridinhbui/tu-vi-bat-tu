"""Lunisolar calendar for an arbitrary civil UTC offset, built on astronomical new moons and
solar terms (not on a truncated series). Vietnamese calendar = UTC+7 (UTC+8 before 1968).

Rules implemented (standard East-Asian lunisolar rules):
  * month starts on the civil day (in the calendar's offset) containing the new moon;
  * the month containing the winter solstice is month 11;
  * when 13 months lie between two such months, the first month without a major term
    (zhongqi) is the leap month and takes the number of the preceding month.
"""
from __future__ import annotations

import datetime as dt
from functools import lru_cache
from math import floor

from . import astro


def jdn_of_date(d: dt.date) -> int:
    return d.toordinal() + 1721425  # proleptic Gregorian civil day number (noon-based JDN)


def _day_number(jd_utc: float, tz_hours: float) -> int:
    return floor(jd_utc + 0.5 + tz_hours / 24)


@lru_cache(maxsize=None)
def _structure(year: int, tz_hours: float):
    # new_moons(y) spans Oct(y-1)..Mar(y+1); a date in December of `year` needs the NEXT winter-solstice month as the end of its interval, so the window must reach
    # Dec(year+1) (Phase 8: with the old one-year window 2033-12-22..31 lost its leap month 11)
    moons = sorted({_day_number(j, tz_hours) for y in (year, year + 1) for j in astro.new_moons(y)})
    terms = astro.all_terms_around(year)
    zhongqi_days = sorted((_day_number(jd, tz_hours), idx) for idx, jd in terms if idx % 2 == 0)
    return moons, zhongqi_days, [d for d, idx in zhongqi_days if idx == 0]


def solar_to_lunar(date: dt.date, tz_hours: float) -> tuple[int, int, int, bool]:
    """Return (lunar_day, lunar_month, lunar_year, is_leap_month)."""
    n = jdn_of_date(date)
    moons, zq, sols = _structure(date.year, tz_hours)

    def month11_start(sol_day: int) -> int:
        return max(m for m in moons if m <= sol_day)

    starts11 = [month11_start(s) for s in sols]
    # pick the m11 interval [A, B) containing n
    ai = max(i for i, a in enumerate(starts11) if a <= n)
    A, B = starts11[ai], starts11[ai + 1]
    sol_year = _solstice_year(sols[ai])
    months = [m for m in moons if A <= m < B]
    months.append(B)
    nmonths = len(months) - 1
    leap_idx = None
    if nmonths == 13:
        zq_days = [d for d, _ in zq]
        for k in range(1, 13):
            lo, hi = months[k], months[k + 1]
            if not any(lo <= z < hi for z in zq_days):
                leap_idx = k
                break
    k = max(i for i in range(nmonths) if months[i] <= n)
    is_leap = leap_idx is not None and k == leap_idx
    if leap_idx is not None and k >= leap_idx:
        num = ((11 - 1 + (k - 1)) % 12) + 1
    else:
        num = ((11 - 1 + k) % 12) + 1
    year = sol_year if num in (11, 12) else sol_year + 1
    return n - months[k] + 1, num, year, is_leap


def _solstice_year(jdn: int) -> int:
    y, m, d = _civil_from_jdn(jdn)
    return y


def _civil_from_jdn(jdn: int) -> tuple[int, int, int]:
    d = dt.date.fromordinal(jdn - 1721425)
    return d.year, d.month, d.day
