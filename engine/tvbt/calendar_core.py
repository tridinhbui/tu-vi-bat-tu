"""Birth-input normalisation and calendar facts (no interpretation here).

Design decisions (all recorded in the CalculationTrace):
  * Solar-term instants are absolute (UTC). BaZi year/month pillars compare the *actual instant*
    of birth with those instants, never the wall-clock date.
  * The wall clock used for day rollover / hour pillar is the civil clock, or true solar time
    when `use_true_solar_time` is on (longitude correction + equation of time).
  * Tu Vi uses the lunar calendar (Vietnamese UTC+7/+8 or Chinese UTC+8), BaZi uses solar terms.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field
from typing import Literal
from zoneinfo import ZoneInfo

import sxtwl

from . import astro, lunar_vn
from .trace import Trace

ZiRule = Literal["early_zi_next_day", "late_zi_same_day"]


@dataclass(frozen=True)
class BirthInput:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    tz: str                       # IANA, e.g. "Asia/Ho_Chi_Minh"
    gender: Literal["male", "female"]
    longitude: float | None = None  # degrees east, required for true solar time
    calendar: Literal["vn", "cn"] = "vn"
    zi_rule: ZiRule = "early_zi_next_day"
    use_true_solar_time: bool = False
    fold: int = 0                 # disambiguates repeated wall times at DST end


@dataclass(frozen=True)
class LunarDate:
    day: int
    month: int
    year: int
    is_leap: bool


@dataclass
class NormalizedBirth:
    input: BirthInput
    local: dt.datetime            # aware, civil clock
    utc: dt.datetime
    clock: dt.datetime            # naive wall clock used for day/hour boundaries
    rule_date: dt.date            # civil date after Zi-hour rule (day-pillar date)
    lunar: LunarDate
    calendar_tz_hours: float
    trace: Trace = field(default_factory=Trace)


def _equation_of_time_minutes(t_utc: dt.datetime) -> float:
    """NOAA/Meeus equation of time (accuracy ~ seconds). Flagged in trace as non-ephemeris."""
    n = t_utc.timetuple().tm_yday + (t_utc.hour - 12) / 24
    g = 2 * math.pi / 365.25 * n
    return 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                     - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))


def vn_calendar_offset(year: int) -> float:
    """Vietnamese lunar calendar offset: UTC+8 until 1967, UTC+7 from 1968 (legal reform)."""
    return 8.0 if year < 1968 else 7.0


def normalize(b: BirthInput) -> NormalizedBirth:
    tr = Trace()
    zone = ZoneInfo(b.tz)
    naive = dt.datetime(b.year, b.month, b.day, b.hour, b.minute)
    local = naive.replace(tzinfo=zone, fold=b.fold)
    # detect non-existent wall times (spring-forward gap)
    rt = local.astimezone(dt.timezone.utc).astimezone(zone).replace(tzinfo=None)
    if rt != naive:
        raise ValueError(f"wall time {naive} does not exist in {b.tz} (DST gap); nearest valid is {rt}")
    utc = local.astimezone(dt.timezone.utc)
    ambiguous = (local.replace(fold=0).utcoffset() != local.replace(fold=1).utcoffset())
    tr.add("tz.resolve", "Resolve civil time with IANA zone",
           {"naive": naive.isoformat(), "tz": b.tz, "fold": b.fold},
           {"utc": utc.isoformat(), "offset": str(local.utcoffset()), "dst": str(local.dst()),
            "ambiguous_wall_time": ambiguous})

    clock = naive
    if b.use_true_solar_time:
        if b.longitude is None:
            raise ValueError("longitude required for true solar time")
        std_meridian = local.utcoffset().total_seconds() / 3600 * 15  # includes DST shift on purpose
        lon_corr = (b.longitude - std_meridian) * 4
        eot = _equation_of_time_minutes(utc)
        clock = naive + dt.timedelta(minutes=lon_corr + eot)
        tr.add("clock.true_solar", "True solar time = civil + 4min*(lon - zone meridian) + equation of time",
               {"longitude": b.longitude, "zone_meridian": std_meridian},
               {"longitude_minutes": round(lon_corr, 3), "eot_minutes": round(eot, 3), "clock": clock.isoformat()},
               rule="EOT: NOAA/Meeus approximation (not JPL ephemeris)")

    rule_date = clock.date()
    if clock.hour == 23 and b.zi_rule == "early_zi_next_day":
        rule_date = rule_date + dt.timedelta(days=1)
    tr.add("day.rule_date", "Date used for day pillar & lunar day after Zi-hour rule",
           {"clock": clock.isoformat(), "zi_rule": b.zi_rule}, rule_date.isoformat())

    if b.calendar == "vn":
        tzh = vn_calendar_offset(rule_date.year)
        ld, lm, ly, leap = lunar_vn.solar_to_lunar(rule_date, tzh)
        src = f"astronomical lunisolar rules @UTC{tzh:+g} (PyEphem new moons + sxtwl solar terms)"
    else:
        tzh = 8.0
        s = sxtwl.fromSolar(rule_date.year, rule_date.month, rule_date.day)
        ld, lm, ly, leap = s.getLunarDay(), s.getLunarMonth(), s.getLunarYear(), bool(s.isLunarLeap())
        src = "sxtwl (Chinese calendar, UTC+8)"
    lunar = LunarDate(ld, lm, ly, leap)
    tr.add("lunar.date", "Solar -> lunar date", {"date": rule_date.isoformat(), "calendar": b.calendar},
           {"day": ld, "month": lm, "year": ly, "leap": leap}, rule=src)
    return NormalizedBirth(b, local, utc, clock, rule_date, lunar, tzh, tr)
