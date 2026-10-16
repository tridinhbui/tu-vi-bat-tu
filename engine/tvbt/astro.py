"""Astronomical event sources: solar terms (sxtwl) and new moons (PyEphem), as UTC Julian dates."""
from __future__ import annotations

import datetime as dt
from functools import lru_cache

import ephem
import sxtwl

BEIJING = dt.timezone(dt.timedelta(hours=8))
UTC = dt.timezone.utc

# sxtwl JDs are expressed in Beijing time (UTC+8) as if they were JD.
_SXTWL_OFFSET_DAYS = 8 / 24


@lru_cache(maxsize=None)
def solar_terms(year: int) -> tuple[tuple[int, float], ...]:
    """(jqIndex, jd_utc) for the 25 terms from Lichun(year) to Lichun(year+1). 0=Winter Solstice,
    odd index = jie (month-starting term), even index = zhongqi (major term)."""
    return tuple((j.jqIndex, j.jd - _SXTWL_OFFSET_DAYS) for j in sxtwl.getJieQiByYear(year))


@lru_cache(maxsize=None)
def all_terms_around(year: int) -> tuple[tuple[int, float], ...]:
    seen: dict[float, int] = {}
    for y in (year - 1, year, year + 1):
        for idx, jd in solar_terms(y):
            seen[round(jd, 6)] = idx
    return tuple(sorted(((idx, jd) for jd, idx in seen.items()), key=lambda t: t[1]))


def jd_to_utc(jd_utc: float) -> dt.datetime:
    return dt.datetime(2000, 1, 1, 12, tzinfo=UTC) + dt.timedelta(days=jd_utc - 2451545.0)


def utc_to_jd(t: dt.datetime) -> float:
    return 2451545.0 + (t.astimezone(UTC) - dt.datetime(2000, 1, 1, 12, tzinfo=UTC)).total_seconds() / 86400


@lru_cache(maxsize=None)
def new_moons(year: int) -> tuple[float, ...]:
    """UTC JD of every new moon from Nov of year-1 to Mar of year+1."""
    out = []
    d = ephem.Date(f"{year - 1}/10/01")
    end = ephem.Date(f"{year + 1}/04/01")
    while d < end:
        d = ephem.next_new_moon(d)
        out.append(float(d) + 2415020.0)
        d = ephem.Date(float(d) + 1)
    return tuple(out)
