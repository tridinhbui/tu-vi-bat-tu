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
    calendar: Literal["vn", "vn_south", "vn_utc7", "cn"] = "vn"   # vn_utc7: UTC+7 for every year (what popular boards use)
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


def vn_calendar_offset(year: int, south: bool = False) -> float:
    """Offset used for the Vietnamese lunar calendar. North/unified: UTC+8 until 1967, UTC+7 from 1968 (VASTI bulletin 1/2019;
    Wikipedia dates the change to Aug 1967 — sources differ). South: UTC+8 until reunification (cut at end of 1975 here: UNVERIFIED)."""
    return 8.0 if year < (1976 if south else 1968) else 7.0


class _Backzone(dt.tzinfo):
    """A zone the installed tzdata does not ship (it lives in tzdb's 'backzone' file), from its Zone lines: (until local wall time, offset)."""

    def __init__(self, name: str, lines: list[tuple[dt.datetime | None, dt.timedelta]]):
        self.name, self.lines = name, lines

    def _off(self, wall: dt.datetime) -> dt.timedelta:
        w = wall.replace(tzinfo=None)
        return next(off for until, off in self.lines if until is None or w < until)

    def utcoffset(self, d):
        return self._off(d)

    def dst(self, d):
        return dt.timedelta(0)

    def tzname(self, d):
        return self.name

    def fromutc(self, d):
        u = d.replace(tzinfo=None)
        for until, off in self.lines:                # the first line whose end, as a UTC instant, is after `u`
            if until is None or u + off < until:
                return (u + off).replace(tzinfo=self)
        raise ValueError(d)


_H = lambda h, m=0, s=0: dt.timedelta(hours=h, minutes=m, seconds=s)
# tzdb 'backzone', Zone Asia/Hanoi (north Vietnam; from Trần Tiến Bình, "Lịch Việt Nam thế kỷ XX-XXI", pp.49-50, as quoted in the tzdb 'asia'
# comments): +08 from 1947-04-01 until October 1954, +07 since. Asia/Ho_Chi_Minh is the south: +08 from 1959-12-31 23:00 to 1975-06-13,
# so a northern birth of 1960-1975 given that zone was an hour off (audit BZ-8). The page maps each city to its zone (web/js/app.js PLACES).
ASIA_HANOI = _Backzone("Asia/Hanoi", [(dt.datetime(1906, 7, 1), _H(7, 3, 24)), (dt.datetime(1911, 5, 1), _H(7, 6, 30)),
                                      (dt.datetime(1942, 12, 31, 23), _H(7)), (dt.datetime(1945, 3, 14, 23), _H(8)),
                                      (dt.datetime(1945, 9, 2), _H(9)), (dt.datetime(1947, 4, 1), _H(7)),
                                      (dt.datetime(1954, 10, 1), _H(8)), (None, _H(7))])


def zone_of(name: str) -> dt.tzinfo:
    """IANA zone by name; Asia/Hanoi (tzdb backzone, not in the installed tzdata) from its Zone lines."""
    return ASIA_HANOI if name == "Asia/Hanoi" else ZoneInfo(name)


def normalize(b: BirthInput) -> NormalizedBirth:
    tr = Trace()
    zone = zone_of(b.tz)
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

    if b.calendar in ("vn", "vn_south", "vn_utc7"):
        # vn / vn_south: the historical offset (UTC+8 before 1968 / 1976); vn_utc7: UTC+7 for every year. They differ only for births before
        # 1968 when a new moon falls between 23:00 and 24:00 Vietnam time (e.g. 31/12/1910 23:21 UTC+7 -> 1/1/1911 is day 1 or day 2).
        tzh = 7.0 if b.calendar == "vn_utc7" else vn_calendar_offset(rule_date.year, b.calendar == "vn_south")
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
