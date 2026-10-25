"""Civil birth time -> UTC for the Western chart: IANA history (DST, wartime zones), birthplace mean time before standard time.

Before a zone adopted standard time the tz database gives Local Mean Time of the zone's reference city ("LMT"). A chart needs
the birthplace's own mean time, so in that case the offset is replaced by longitude / 15 hours, as the Astrodienst atlas does;
the trace says so. Northern Vietnam uses tzdb's backzone Asia/Hanoi (tvbt.calendar_core.zone_of), as the Tử Vi pages do.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from tvbt.calendar_core import zone_of
from tvbt.trace import Trace


class TimeError(ValueError):
    pass


@dataclass
class ResolvedTime:
    utc: dt.datetime
    local: dt.datetime            # aware civil time (offset as used)
    offset_hours: float
    dst: bool
    lmt: bool                     # birthplace mean time used
    ambiguous: bool               # wall time repeated at a DST fall-back; `fold` chose one
    trace: Trace = field(default_factory=Trace)


def resolve(year: int, month: int, day: int, hour: int, minute: int, tz: str, lon: float, second: int = 0,
            fold: int = 0, utc_offset_hours: float | None = None) -> ResolvedTime:
    tr = Trace()
    try:
        naive = dt.datetime(year, month, day, hour, minute, second)
    except ValueError as e:
        raise TimeError(f"ngày giờ không hợp lệ: {e}") from e
    if utc_offset_hours is not None:                      # the user typed the offset themselves (e.g. a birth certificate says so)
        off = dt.timedelta(hours=utc_offset_hours)
        local = naive.replace(tzinfo=dt.timezone(off))
        utc = (naive - off).replace(tzinfo=dt.timezone.utc)
        tr.add("time.manual_offset", "UTC offset given by the user", {"local": naive.isoformat(), "offset_h": utc_offset_hours},
               utc.isoformat())
        return ResolvedTime(utc, local, utc_offset_hours, False, False, False, tr)
    try:
        zone = zone_of(tz)
    except Exception as e:  # noqa: BLE001 - zoneinfo raises several types
        raise TimeError(f"không nhận ra múi giờ {tz!r}") from e
    local = naive.replace(tzinfo=zone, fold=fold)
    back = local.astimezone(dt.timezone.utc).astimezone(zone).replace(tzinfo=None)
    if back != naive:
        raise TimeError(f"giờ {naive:%H:%M} ngày {naive:%d/%m/%Y} không tồn tại ở {tz} (đồng hồ được vặn tới khi bắt đầu giờ mùa hè); "
                        f"hãy kiểm tra lại giờ trên giấy khai sinh")
    ambiguous = local.replace(fold=0).utcoffset() != local.replace(fold=1).utcoffset()
    lmt = local.tzname() == "LMT"
    if lmt:
        off = dt.timedelta(seconds=round(lon / 15.0 * 3600))
        local = naive.replace(tzinfo=dt.timezone(off, "LMT"))
    utc = local.astimezone(dt.timezone.utc)
    offset_h = local.utcoffset().total_seconds() / 3600
    is_dst = bool(local.dst()) if not lmt else False
    tr.add("time.zone", "Civil time resolved with the IANA time-zone history",
           {"local": naive.isoformat(), "tz": tz, "fold": fold},
           {"utc": utc.isoformat(), "offset_h": round(offset_h, 6), "dst": is_dst, "ambiguous": ambiguous,
            "birthplace_mean_time": lmt},
           rule="LMT -> birthplace longitude/15 h" if lmt else "tzdb")
    return ResolvedTime(utc, local, offset_h, is_dst, lmt, ambiguous, tr)
