"""Lunar -> solar conversion for users who only know their lunar birthday.

Strategy: seed from sxtwl's Chinese-calendar inverse, then confirm with the same solar->lunar routine the chart uses
(so Vietnamese-calendar differences are respected). Only exact matches are returned; nothing is guessed.
"""
from __future__ import annotations

import datetime as dt

import sxtwl

from . import lunar_vn
from .calendar_core import vn_calendar_offset


def lunar_to_solar(day: int, month: int, year: int, leap: bool = False, calendar: str = "vn") -> list[dt.date]:
    try:
        d = sxtwl.fromLunar(year, month, day, leap)
    except Exception as e:  # invalid combination for sxtwl
        raise ValueError(f"không tìm thấy ngày âm lịch {day}/{month}/{year}{' nhuận' if leap else ''}") from e
    seed = dt.date(d.getSolarYear(), d.getSolarMonth(), d.getSolarDay())
    if calendar == "cn":
        return [seed]
    hits = []
    for k in range(-5, 6):
        s = seed + dt.timedelta(days=k)
        tzh = vn_calendar_offset(s.year, False)
        ld, lm, ly, lp = lunar_vn.solar_to_lunar(s, tzh)
        if (ld, lm, ly, lp) == (day, month, year, leap):
            hits.append(s)
    return hits
