"""Cung hoàng đạo (Western sun sign): which twelfth of the ecliptic the Sun was in at the instant of birth. Computation only.

The Sun enters a sign when its apparent ecliptic longitude reaches a multiple of 30°. Those twelve instants are exactly the twelve
trung khí the calendar already computes (astro.solar_terms, sxtwl): Xuân Phân = 0° (Bạch Dương), Cốc Vũ = 30° (Kim Ngưu), …,
Đông Chí = 270° (Ma Kết), Đại Hàn = 300° (Bảo Bình), Vũ Thủy = 330° (Song Ngư). No date table decides the sign: the birth instant
(calendar_core.normalize, so historical zones such as UTC+8 in the South 1959-1975 are kept) is compared with the ingress instants.
engine/tests/test_hoang_dao.py checks the instants against an independent PyEphem computation (within 2 minutes, 1900-2049).

Readings (what a sign means) are NOT computed here: every reading cites a book page and comes from engine/data/hoang_dao/pack.json,
built by tools/build_hoang_dao_pack.py from tools/data/hoang_dao_rules.json (Alan Leo for the character of each sign; Lilly and
Ptolemy for element, modality and ruler, each value shown with the pages that state it). A sign without readings in the pack gets
the neutral NOT_READ line instead.
"""
from __future__ import annotations

import datetime as dt
import json
from functools import lru_cache
from pathlib import Path

from . import astro
from .calendar_core import BirthInput, NormalizedBirth, normalize, zone_of
from .xem_ngay import TERM_NAMES

PACK = Path(__file__).resolve().parent.parent / "data" / "hoang_dao" / "pack.json"
CUSP_HOURS = 24          # within this many hours of an ingress the card says "sinh sát ranh giới" and gives the exact time

# (slug, Vietnamese name, other common Vietnamese name, Latin name, approximate date span). Index i covers longitude 30i..30i+30.
# The span is a conventional label only ("khoảng"): the real boundary moves by a day or so from year to year and is never read from it.
SIGNS = [
    ("bach-duong", "Bạch Dương", None, "Aries", "21/3–19/4"),
    ("kim-nguu", "Kim Ngưu", None, "Taurus", "20/4–20/5"),
    ("song-tu", "Song Tử", None, "Gemini", "21/5–20/6"),
    ("cu-giai", "Cự Giải", None, "Cancer", "21/6–22/7"),
    ("su-tu", "Sư Tử", None, "Leo", "23/7–22/8"),
    ("xu-nu", "Xử Nữ", None, "Virgo", "23/8–22/9"),
    ("thien-binh", "Thiên Bình", None, "Libra", "23/9–22/10"),
    ("bo-cap", "Bọ Cạp", "Thiên Yết", "Scorpio", "23/10–21/11"),
    ("nhan-ma", "Nhân Mã", None, "Sagittarius", "22/11–21/12"),
    ("ma-ket", "Ma Kết", None, "Capricorn", "22/12–19/1"),
    ("bao-binh", "Bảo Bình", None, "Aquarius", "20/1–18/2"),
    ("song-ngu", "Song Ngư", None, "Pisces", "19/2–20/3"),
]

# The traditional glyph of each sign as one SVG path (24x24, stroke only), drawn for this site so no emoji character is needed.
# The same strings are in engine/web/js/hoangdao.js (test_hoang_dao checks they match).
GLYPHS = {
    "bach-duong": "M12 21V10M12 10C12 6 10.5 3.5 7.5 3.5S3 5.5 3 8s2 3.5 3.5 3.5M12 10c0-4 1.5-6.5 4.5-6.5S21 5.5 21 8s-2 3.5-3.5 3.5",
    "kim-nguu": "M3 3.5c1.2 4 4.5 6 9 6s7.8-2 9-6M12 9.5a5.5 5.5 0 1 0 0 11a5.5 5.5 0 1 0 0-11",
    "song-tu": "M4.5 3.5c4.5 1.6 10.5 1.6 15 0M4.5 20.5c4.5-1.6 10.5-1.6 15 0M9 4.6v14.8M15 4.6v14.8",
    "cu-giai": "M4 9a3 3 0 1 0 6 0a3 3 0 1 0-6 0M7 6c4.2-2.6 10-2 13.5 1.8M14 15a3 3 0 1 0 6 0a3 3 0 1 0-6 0M17 18c-4.2 2.6-10 2-13.5-1.8",
    "su-tu": "M9.5 16a3 3 0 1 1-6 0a3 3 0 1 1 6 0C9.5 11.5 7.5 9.5 7.5 7a4.5 4.5 0 0 1 9 0c0 4-3 6-3 10c0 2.4 1.4 3.5 3.2 3.5c1.8 0 3.3-1.2 3.3-3",
    "xu-nu": "M3 5.5c1.3 0 2 .8 2 2.2V18M5 8.5c0-1.9 1.2-3 2.8-3s2.7 1.1 2.7 3V18M10.5 8.5c0-1.9 1.2-3 2.8-3s2.7 1.1 2.7 3v6.5c0 3 1.5 5 4.5 6M16 13c1.8-1.6 5-1.2 5 1.2c0 2.6-3 4.6-6.5 5.8",
    "thien-binh": "M3 20h18M3 16h5.2a4.5 4.5 0 1 1 7.6 0H21",
    "bo-cap": "M3 5.5c1.3 0 2 .8 2 2.2V18M5 8.5c0-1.9 1.2-3 2.8-3s2.7 1.1 2.7 3V18M10.5 8.5c0-1.9 1.2-3 2.8-3s2.7 1.1 2.7 3V17c0 1.8 1.1 3 2.8 3H21M18.8 17.8l2.2 2.2-2.2 2.2",
    "nhan-ma": "M4 20L20 4M12.5 4H20v7.5M6.5 11.5l6 6",
    "ma-ket": "M3 5c1.4 0 2.5 1 2.5 3v10.5M5.5 8c0-2.2 1.5-3.5 3.5-3.5s3.5 1.3 3.5 3.5v8.5c0 2.7 1.9 4.5 4.3 4.5a3.4 3.4 0 0 0 0-6.8c-2 0-3.5 1.3-4.3 3",
    "bao-binh": "M3 10l3-3 3 3 3-3 3 3 3-3 3 3M3 17l3-3 3 3 3-3 3 3 3-3 3 3",
    "song-ngu": "M5.5 3c4 4.5 4 13.5 0 18M18.5 3c-4 4.5-4 13.5 0 18M4.5 12h15",
}

NOT_READ = "Phần luận về cung hoàng đạo này đang được soạn từ sách có ghi trang; Thiên Bàn chưa đưa câu luận nào khi chưa có trang sách để dẫn."


def sign_index_of_term(jq: int) -> int:
    """sxtwl jqIndex (0 = Đông Chí, even = trung khí) -> index in SIGNS of the sign the Sun enters at that term."""
    assert jq % 2 == 0, jq
    return ((270 + 15 * jq) % 360) // 30


@lru_cache(maxsize=None)
def ingresses(year: int) -> tuple[tuple[int, float, int], ...]:
    """(sign index, UTC Julian date, sxtwl jqIndex) of every ingress from about a year before `year` to a year after, in time order."""
    return tuple((sign_index_of_term(jq), jd, jq) for jq, jd in astro.all_terms_around(year) if jq % 2 == 0)


def sign_info(i: int) -> dict:
    s, name, alt, latin, span = SIGNS[i]
    return {"index": i, "slug": s, "name": name, "alt_name": alt, "label": f"{name} ({alt})" if alt else name, "latin": latin,
            "longitude_from": 30 * i, "longitude_to": 30 * i + 30, "approx_dates": f"khoảng {span}", "approx_dates_note": "ước lượng"}


def _fmt(t: dt.datetime, seconds: bool = False) -> str:
    sec = f":{t.second:02d}" if seconds else ""
    return f"{t.hour:02d}:{t.minute:02d}{sec} ngày {t.day:02d}/{t.month:02d}/{t.year}"


def _instant(i: int, jd: float, jq: int, zone: dt.tzinfo) -> dict:
    utc = astro.jd_to_utc(jd).replace(microsecond=0)
    local = utc.astimezone(zone)
    off = local.utcoffset().total_seconds() / 3600
    return {"sign": SIGNS[i][1], "slug": SIGNS[i][0], "term": TERM_NAMES[jq], "longitude": 30 * i, "utc": utc.isoformat(),
            "local": local.isoformat(), "utc_offset": f"UTC{off:+g}", "text": _fmt(local), "text_seconds": _fmt(local, True)}


@lru_cache(maxsize=1)
def _pack() -> dict:
    try:
        return json.loads(PACK.read_text("utf-8"))
    except FileNotFoundError:
        return {"readings": [], "facts": {}}


def readings(slug: str) -> list[dict]:
    """The cited readings of one sign (engine/data/hoang_dao/pack.json): each {topic, reading, book, short, page, source_title, ...}."""
    return [r for r in _pack().get("readings", []) if r.get("sign") == slug]


def facts(slug: str) -> dict:
    """Element / modality / ruler of one sign as the books state them: {fact: {name, value, label, cites: [{short, page, ...}]}}."""
    return _pack().get("facts", {}).get(slug, {})


def sun_sign_at(utc: dt.datetime, zone: dt.tzinfo) -> dict:
    """The sun sign at an aware instant; ingress times are given in `zone` (the birth place's civil clock)."""
    jd = astro.utc_to_jd(utc)
    ing = ingresses(utc.astimezone(dt.timezone.utc).year)
    k = max(n for n, (_, t, _) in enumerate(ing) if t <= jd)       # the last ingress at or before the birth instant
    (i, t0, q0), (i1, t1, q1) = ing[k], ing[k + 1]
    after, before = (jd - t0) * 24, (t1 - jd) * 24
    near = "ingress" if after <= before else "next_ingress"
    cusp = round(min(after, before), 1)
    cur, nxt = _instant(i, t0, q0, zone), _instant(i1, t1, q1, zone)
    sign = sign_info(i)
    rd = readings(sign["slug"])
    out = {"sun_sign": sign, "ingress": cur, "next_ingress": nxt, "cusp_hours": cusp, "near_cusp": cusp < CUSP_HOURS,
           "nearest_boundary": near, "note": None, "facts": facts(sign["slug"]), "readings": rd,
           "reading_status": None if rd else NOT_READ}
    if cusp < CUSP_HOURS:
        h = _hours(min(after, before))
        when = "text_seconds" if min(after, before) < 1 else "text"     # within the hour the minute alone could read the wrong way
        if near == "ingress":
            out["note"] = (f"Sinh sát ranh giới cung hoàng đạo: Mặt Trời vào {sign['name']} lúc {cur[when]} (giờ nơi sinh, {cur['utc_offset']}), "
                           f"{h} trước giờ sinh, nên cung hoàng đạo là {sign['name']}.")
        else:
            out["note"] = (f"Sinh sát ranh giới cung hoàng đạo: Mặt Trời vào {nxt['sign']} lúc {nxt[when]} (giờ nơi sinh, {nxt['utc_offset']}), "
                           f"{h} sau giờ sinh, nên cung hoàng đạo vẫn là {sign['name']}.")
    return out


def _hours(h: float) -> str:
    if h < 1:
        return f"{max(1, round(h * 60))} phút"
    return f"{round(h, 1):g} giờ".replace(".", ",")


def sun_sign(nb: NormalizedBirth) -> dict:
    """The sun sign of a normalised birth (civil clock and historical zone already resolved by calendar_core.normalize)."""
    return sun_sign_at(nb.utc, zone_of(nb.input.tz))


def lookup(year: int, month: int, day: int, hour: int, minute: int, tz: str = "Asia/Ho_Chi_Minh") -> dict:
    """Standalone lookup (GET /api/hoang-dao): the birth goes through the same normalisation as a chart. Raises ValueError on a bad date."""
    nb = normalize(BirthInput(year, month, day, hour, minute, tz, "male"))
    return sun_sign(nb)


def sign_periods(slug: str, years, tz: str = "Asia/Ho_Chi_Minh") -> list[dict]:
    """For each year: when the Sun enters the sign (local date in that year) and when it leaves it (the next ingress)."""
    zone, i = zone_of(tz), next(n for n, s in enumerate(SIGNS) if s[0] == slug)
    out = []
    for y in years:
        ing = ingresses(y)
        for k, (si, jd, jq) in enumerate(ing):
            a = _instant(si, jd, jq, zone)
            if si == i and a["local"][:4] == str(y):
                out.append({"year": y, "from": a, "to": _instant(*ing[k + 1], zone)})
    return out


def year_table(year: int, tz: str = "Asia/Ho_Chi_Minh") -> list[dict]:
    """The twelve ingresses whose local date falls in `year` (for the article pages), in time order."""
    zone = zone_of(tz)
    out = []
    for i, jd, jq in ingresses(year):
        x = _instant(i, jd, jq, zone)
        if x["local"][:4] == str(year):
            out.append(x)
    return out
