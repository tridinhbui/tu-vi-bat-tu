"""Month calendar for the "Xem ngày" page: only what the engine can COMPUTE.

Per civil day: solar date, lunar date (Vietnamese calendar UTC+7, UTC+8 before 1968; or Chinese UTC+8), can chi of the day,
of the lunar month and of the lunar year, the Bát Tự month/year pillars (solar-term boundaries, as the chart uses), the solar
terms that fall on the day, and whether the day branch is in lục xung with a given birth-year branch (SIX_CLASH, 八字真宗
pp.19-20 relation tables, the same table the chart and compare use).

Deliberately NOT here: hoàng đạo / hắc đạo days, day stars (thần sát ngày), "giờ hoàng đạo" and any good/bad score. Those
come from almanac books (Ngọc Hạp Thông Thư, Hiệp Kỷ Biện Phương Thư) that the project does not have; nothing is guessed.
"""
from __future__ import annotations

import calendar as _cal
import datetime as dt

import sxtwl

from . import astro, lunar_vn
from .bazi import SIX_CLASH
from .calendar_core import vn_calendar_offset
from .ganzhi import BRANCHES_VI, STEMS_VI, from_cycle, gz_name, tiger_month_stem, year_cycle_index

# sxtwl jqIndex order: 0 = Đông Chí; odd = tiết (jie, starts a Bát Tự month), even = trung khí.
TERM_NAMES = ["Đông Chí", "Tiểu Hàn", "Đại Hàn", "Lập Xuân", "Vũ Thủy", "Kinh Trập", "Xuân Phân", "Thanh Minh", "Cốc Vũ",
              "Lập Hạ", "Tiểu Mãn", "Mang Chủng", "Hạ Chí", "Tiểu Thử", "Đại Thử", "Lập Thu", "Xử Thử", "Bạch Lộ", "Thu Phân",
              "Hàn Lộ", "Sương Giáng", "Lập Đông", "Tiểu Tuyết", "Đại Tuyết"]
WEEKDAYS_VI = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
YEAR_MIN, YEAR_MAX = 1901, 2099

NOT_COMPUTED = ("Ngày hoàng đạo / hắc đạo, sao tốt xấu của ngày, giờ hoàng đạo và mọi điểm \"tốt xấu\" không được tính: "
                "các phần đó lấy từ sách lịch pháp (Ngọc Hạp Thông Thư, Hiệp Kỷ Biện Phương Thư) mà Thiên Bàn chưa có trong kho "
                "nguồn, nên không tự đặt ra.")


def _offset(year: int, calendar: str) -> float:
    """vn: historical Vietnamese offset (UTC+8 before 1968); vn_utc7: UTC+7 for every year, as the chart option; cn: UTC+8."""
    return 8.0 if calendar == "cn" else 7.0 if calendar == "vn_utc7" else vn_calendar_offset(year, False)


def _gz(n: int) -> dict:
    s, b = from_cycle(n % 60)
    return {"stem": s, "branch": b, "name": gz_name(s, b)}


def _bazi_pillars(jd_utc: float) -> tuple[dict, dict]:
    """Bát Tự year and month pillars in force at the instant jd_utc (Lập Xuân / tiết boundaries, as bazi.compute)."""
    year = astro.jd_to_utc(jd_utc).year
    jie = sorted(((i, jd) for i, jd in astro.all_terms_around(year) if i % 2 == 1), key=lambda t: t[1])
    ly = max(jd for i, jd in jie if i == 3 and jd <= jd_utc)
    ys, yb = from_cycle((astro.jd_to_utc(ly).astimezone(astro.BEIJING).year - 4) % 60)
    idx, _ = max(((i, jd) for i, jd in jie if jd <= jd_utc), key=lambda t: t[1])
    mb = ((idx + 1) // 2) % 12
    ms = (tiger_month_stem(ys) + (mb - 2) % 12) % 10
    return {"stem": ys, "branch": yb, "name": gz_name(ys, yb)}, {"stem": ms, "branch": mb, "name": gz_name(ms, mb)}


def _terms_by_day(year: int, month: int, tzh: float) -> dict[int, list[dict]]:
    tz = dt.timezone(dt.timedelta(hours=tzh))
    out: dict[int, list[dict]] = {}
    for idx, jd in astro.all_terms_around(year):
        local = astro.jd_to_utc(jd).astimezone(tz)
        if local.year == year and local.month == month:
            out.setdefault(local.day, []).append({"index": idx, "name": TERM_NAMES[idx], "kind": "tiết" if idx % 2 else "trung khí",
                                                  "time": local.strftime("%H:%M"), "jd": jd})
    return out


def day_info(d: dt.date, calendar: str = "vn", birth_branch: int | None = None, _terms: dict | None = None) -> dict:
    tzh = _offset(d.year, calendar)
    ld, lm, ly, leap = lunar_vn.solar_to_lunar(d, tzh)
    g = sxtwl.fromSolar(d.year, d.month, d.day).getDayGZ()
    day = {"stem": g.tg, "branch": g.dz, "name": gz_name(g.tg, g.dz)}
    year_gz = _gz(year_cycle_index(ly))
    # Lunar month can chi by ngũ hổ độn from the lunar year stem (month 1 = Dần). A leap month gets none: which can chi it
    # carries is a convention the project has no source for, so it is left empty rather than guessed.
    month_gz = None
    if not leap:
        mb = (lm + 1) % 12
        ms = (tiger_month_stem(year_gz["stem"]) + (mb - 2) % 12) % 10
        month_gz = {"stem": ms, "branch": mb, "name": gz_name(ms, mb)}
    tz = dt.timezone(dt.timedelta(hours=tzh))
    start_jd = astro.utc_to_jd(dt.datetime(d.year, d.month, d.day, tzinfo=tz))
    by, bm = _bazi_pillars(start_jd)
    terms = (_terms if _terms is not None else _terms_by_day(d.year, d.month, tzh)).get(d.day, [])
    term_out = []
    for t in terms:
        item = {k: t[k] for k in ("index", "name", "kind", "time")}
        if t["index"] % 2 == 1:   # a tiết changes the Bát Tự month (Lập Xuân also the year) from that instant
            ny, nm = _bazi_pillars(t["jd"] + 1e-6)
            item["bazi_month_after"] = nm["name"]
            if t["index"] == 3:
                item["bazi_year_after"] = ny["name"]
        term_out.append(item)
    out = {
        "date": d.isoformat(), "day": d.day, "weekday": WEEKDAYS_VI[d.weekday()],
        "lunar": {"day": ld, "month": lm, "year": ly, "leap": leap},
        "can_chi": {"day": day, "month": month_gz, "year": year_gz},
        "bazi": {"year": by, "month": bm, "at": "00:00"},
        "terms": term_out,
    }
    if birth_branch is not None:
        out["clash"] = frozenset((day["branch"], birth_branch)) in SIX_CLASH
    return out


def month_view(year: int, month: int, calendar: str = "vn", birth_branch: int | None = None) -> dict:
    if not (YEAR_MIN <= year <= YEAR_MAX) or not (1 <= month <= 12):
        raise ValueError(f"năm phải trong {YEAR_MIN}-{YEAR_MAX}, tháng 1-12")
    if calendar not in ("vn", "vn_utc7", "cn"):
        raise ValueError("calendar phải là vn, vn_utc7 hoặc cn")
    if birth_branch is not None and not (0 <= birth_branch <= 11):
        raise ValueError("chi tuổi phải trong 0-11")
    tzh = _offset(year, calendar)
    terms = _terms_by_day(year, month, tzh)
    n = _cal.monthrange(year, month)[1]
    days = [day_info(dt.date(year, month, k), calendar, birth_branch, terms) for k in range(1, n + 1)]
    out = {
        "year": year, "month": month, "calendar": calendar, "utc_offset": tzh,
        "first_weekday": dt.date(year, month, 1).weekday(),   # 0 = Monday
        "days": days,
        "computed": ["âm lịch", "can chi ngày, tháng, năm", "trụ năm và trụ tháng Bát Tự theo tiết khí", "tiết khí", "lục xung với chi tuổi"],
        "not_computed": NOT_COMPUTED,
        "sources": {
            "lunar": "Lịch âm tính từ sóc (trăng mới) và trung khí thiên văn, múi giờ UTC+7 cho lịch Việt Nam (UTC+8 trước 1968)",
            "terms": "Thời điểm tiết khí từ thư viện thiên văn sxtwl, đổi sang giờ địa phương",
            "clash": "Bảng lục xung địa chi (八字真宗 tr.19-20), cùng bảng lá số dùng",
        },
    }
    if birth_branch is not None:
        out["birth_branch"] = {"branch": birth_branch, "name": BRANCHES_VI[birth_branch],
                               "clashes_with": BRANCHES_VI[(birth_branch + 6) % 12]}
    return out
