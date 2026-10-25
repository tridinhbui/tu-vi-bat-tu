"""Layer 1: considerations before judgment (radicality). Lilly pp.121-123, Bonatti Considerations (Coley).

Each consideration is reported with what Lilly says it does: most are cautions about the astrologer's judgment ("it is not
safe to judge"), one is a testimony about the matter (the void Moon), none by itself voids the chart. The engine therefore
never refuses a chart on its own: it lists the cautions, says how strong each is in the source, and the judgment layer
lowers its confidence accordingly.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict

from . import dignity, kb
from .questions import ruler_of_house

VI = {"sun": "Mặt Trời", "moon": "Mặt Trăng", "mercury": "Thủy tinh", "venus": "Kim tinh", "mars": "Hỏa tinh", "jupiter": "Mộc tinh",
      "saturn": "Thổ tinh"}

SHORT_ASCENSION = {9, 10, 11, 0, 1, 2}          # Capricorn .. Gemini (northern hemisphere reading; Lilly's London)
VOC_SOFT_SIGNS = {1, 3, 8, 11}                  # Taurus, Cancer, Sagittarius, Pisces (lilly.consider.moon_void_of_course)


@dataclass
class Consideration:
    id: str
    applies: bool
    severity: str           # info | caution | strong_caution | testimony_against
    vi: str                 # what was found, in Vietnamese
    effect_vi: str          # what the source says it means
    detail: dict

    def as_dict(self):
        return asdict(self) | {"sources": kb.cite(self.id)}


def _nature(p: str) -> set[str] | None:
    r = kb.rule(f"lilly.planet.{p}.nature")
    if not r:
        return None
    m = re.search(r"qualities:\s*([a-z ,/]+)", r.get("conditions", ""))
    return {q.strip() for q in m.group(1).replace("/", ",").split(",") if q.strip()} if m else None


def _triplicity_lords(lon: float) -> set[str]:
    r = dignity.table()[dignity.sign_of(lon)]["triplicity"]
    return {r["day"], r["night"]}


def check(chart, frame: dict, moon_course: dict) -> list[Consideration]:
    out: list[Consideration] = []
    asc_deg = chart.asc % 30
    asc_sign = dignity.sign_of(chart.asc)
    moon = chart.bodies["moon"]
    lord1 = ruler_of_house(chart, 1)
    lord7 = ruler_of_house(chart, 7)

    # hour ruler and ascendant ruler
    ph = chart.planetary_hour
    if ph.get("available"):
        hr = ph["hour_ruler"]
        same = hr == lord1
        trip = hr in _triplicity_lords(chart.asc)
        n1, n2 = _nature(hr), _nature(lord1)
        nat = bool(n1 and n2 and ({"hot", "cold"} & n1 & n2) and ({"dry", "moist"} & n1 & n2))
        ok = same or trip or nat
        out.append(Consideration("lilly.consider.hour_ruler_agreement", not ok, "info" if ok else "caution",
            f"Chủ giờ hành tinh là {VI[hr]}, chủ nhà 1 là {VI[lord1]}: " + (
                "trùng nhau" if same else "cùng tam hợp" if trip else "cùng tính chất" if nat else "không trùng, không cùng tam hợp, không cùng tính chất"),
            "Theo Lilly, lá số 'căn bản' (radical) khi chủ giờ và chủ nhà 1 trùng, cùng tam hợp hoặc cùng tính chất. "
            "Lilly không nói phải làm gì khi không đạt: chỉ là lời lưu ý.",
            {"hour_ruler": hr, "asc_ruler": lord1, "same": same, "triplicity": trip, "nature": nat if n1 and n2 else None}))
    if asc_deg < 3:
        strong = asc_sign in SHORT_ASCENSION
        out.append(Consideration("lilly.consider.asc_early_degrees", True, "strong_caution" if strong else "caution",
            f"Điểm Mọc ở {asc_deg:.2f}° của cung, tức mới mọc",
            "Lilly: độ 0-2 của cung đang mọc thì không nên mạo hiểm luận (nhất là cung mọc nhanh, Ma Kết đến Song Tử), "
            "trừ khi người hỏi còn rất trẻ hoặc dáng vẻ khớp với cung.", {"asc_deg": asc_deg, "short_ascension": strong}))
    if asc_deg >= 27:
        out.append(Consideration("lilly.consider.asc_late_degrees", True, "strong_caution",
            f"Điểm Mọc ở {asc_deg:.2f}° của cung, tức đã gần hết cung",
            "Lilly: độ 27-29 đang mọc thì 'không hề an toàn' để luận, trừ khi tuổi người hỏi ứng với số độ, hoặc lá số lập "
            "cho một thời điểm có thật (ví dụ lúc một người bỏ đi).", {"asc_deg": asc_deg}))
    md = moon.lon % 30
    ms = dignity.sign_of(moon.lon)
    if md >= 27:
        out.append(Consideration("lilly.consider.moon_late_degrees_via_combusta", True,
            "strong_caution" if ms in (2, 7, 9) else "caution",
            f"Mặt Trăng ở {md:.2f}° của cung (độ cuối)",
            "Lilly: Trăng ở các độ cuối cung (nhất là Song Tử, Bọ Cạp, Ma Kết) thì luận không an toàn. Lilly không cho số độ; "
            "Thiên Bàn tính từ 27°, như quy tắc điểm Mọc cùng trang.", {"moon_deg": md, "sign": ms}))
    if 195.0 <= moon.lon < 225.0:
        out.append(Consideration("lilly.consider.moon_late_degrees_via_combusta", True, "caution",
            "Mặt Trăng trong 'via combusta' (15° Thiên Bình đến 15° Bọ Cạp)",
            "Lilly ghi đây là ý kiến của 'một số người' (some), không phải quy tắc của chính ông.", {"moon_lon": moon.lon}))
    if moon_course["voc_by_sign"]:
        soft = ms in VOC_SOFT_SIGNS
        out.append(Consideration("lilly.consider.moon_void_of_course", True, "testimony_against",
            "Mặt Trăng vô hành (void of course): không tạo thêm góc hợp chính xác nào trước khi rời cung"
            + (" — nhưng đang ở Kim Ngưu/Cự Giải/Nhân Mã/Song Ngư" if soft else ""),
            "Lilly: Trăng vô hành thì mọi việc khó thành, trừ khi các chủ tinh chính rất mạnh; Trăng vô hành ở Kim Ngưu, "
            "Cự Giải, Nhân Mã, Song Ngư thì 'vẫn làm được phần nào'. Đây là chứng cứ về sự việc, không làm lá số vô hiệu.",
            {"soft_sign": soft, "voc_by_orb": moon_course["voc_by_orb"]}))
    elif moon_course["voc_by_orb"]:
        out.append(Consideration("lilly.voc.definition", False, "info",
            "Mặt Trăng chưa trong orb của góc hợp nào đang tiến tới, nhưng vẫn sẽ tạo góc hợp trước khi rời cung",
            "Theo cách đọc 'trong cung' (Thiên Bàn dùng mặc định) Trăng không vô hành; theo cách đọc 'theo orb' thì có. "
            "Hai cách đọc được nêu cả hai.", {}))
    if frame["quesited_house"] != 7:
        c7 = chart.cusps[6]
        r7 = chart.bodies[lord7]
        afflicted = []
        for m in ("saturn", "mars"):
            if abs((chart.bodies[m].lon - c7 + 180) % 360 - 180) <= 5:
                afflicted.append(f"{VI[m]} sát đỉnh nhà 7")
        if r7.retrograde:
            afflicted.append(f"chủ nhà 7 ({VI[lord7]}) nghịch hành")
        sp = dignity.solar_phase(chart, lord7) if lord7 != "sun" else {"state": "sun"}
        if sp["state"] == "combust":
            afflicted.append(f"chủ nhà 7 ({VI[lord7]}) bị đốt")
        if afflicted:
            out.append(Consideration("lilly.consider.seventh_afflicted", True, "caution", (lambda x: x[:1].upper() + x[1:])("; ".join(afflicted)),
                "Lilly: nhà 7 (vị trí của chính nhà chiêm tinh) bị hại khi câu hỏi không thuộc nhà 7 thì lời luận khó làm người "
                "hỏi hài lòng. Đây là lưu ý về người luận, không về sự việc.", {"items": afflicted}))
    sat = chart.bodies["saturn"]
    if sat.house == 1:
        out.append(Consideration("lilly.consider.saturn_in_ascendant", True, "strong_caution" if sat.retrograde else "caution",
            "Thổ tinh ở nhà 1" + (" và đang nghịch hành" if sat.retrograde else ""),
            "Lilly (theo các tác giả Ả Rập): Thổ tinh ở nhà 1, nhất là khi nghịch hành, thì việc hỏi hiếm khi đến kết cục tốt.",
            {"retrograde": sat.retrograde}))
    if sat.house == 7:
        out.append(Consideration("lilly.consider.saturn_in_seventh", True, "caution", "Thổ tinh ở nhà 7",
            "Lilly: Thổ tinh ở nhà 7 hoặc làm hỏng lời luận của nhà chiêm tinh, hoặc báo việc đi từ rủi này sang rủi khác.", {}))
    if lord1 != "sun" and dignity.solar_phase(chart, lord1)["state"] == "combust":
        out.append(Consideration("lilly.consider.lord_asc_combust", True, "strong_caution", f"Chủ nhà 1 ({VI[lord1]}) bị Mặt Trời đốt",
            "Lilly: chủ nhà 1 bị đốt thì câu hỏi 'không thành' và người hỏi khó nghe lời khuyên.", {}))
    es7 = dignity.essential(lord7, chart.bodies[lord7].lon, chart.is_day)
    term7 = es7.lords["term"]
    bad7 = []
    if "fall" in es7.debilities:
        bad7.append("ở thế suy (fall)")
    if term7 in ("saturn", "mars") and lord7 != term7:
        bad7.append(f"ở giới hạn (term) của {VI[term7]}")
    if bad7:
        out.append(Consideration("lilly.consider.lord_seventh_unfortunate", True, "caution", f"Chủ nhà 7 ({VI[lord7]}) " + ", ".join(bad7),
            "Lilly: chủ nhà 7 bất lợi, ở thế suy hoặc trong giới hạn của sao hung thì nhà chiêm tinh khó đưa ra lời luận chắc.",
            {"lord7": lord7, "items": bad7}))
    return out
