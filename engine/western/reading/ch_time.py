"""Chapter 'Thời vận': the coming twelve months, one technique per paragraph, never a merged score.

  tv.tom_tat      the year in plain words: the profected place and its lord, the strongest transits, one progressed event
  tv.explain      what each of the four techniques answers, with this chart's own example of each
  tv.periods      quarter by quarter: what each technique has in that quarter, side by side
  tv.profection   the year by Valens (IV.11) and Lilly (pp.715-727)
  tv.transits     the transits picked by the written score of western/reading/milestones.py, with their area and dates
  tv.solar_return Lilly's revolution (p.734)
  tv.progressions Alan Leo's secondary progressions (The Progressed Horoscope)
"""
from __future__ import annotations

import datetime as dt

from .. import dignity, ephemeris as E, progressions as PR, returns as R, transits as T
from ..zodiac import SIGNS, sign_index
from . import milestones as MS
from .ch_core import M, lilly_condition
from .compose import Para, cap, ev_planet, listing, planet_list, srcs
from .facts import CLASSICAL, Facts
from .vocab import ASPECT_WITH, P, S, num

UTC = dt.timezone.utc
SLOW = ("mars", "jupiter", "saturn", "uranus", "neptune", "pluto")
POINT_AREA = {"asc": "thân thể và cách bạn hiện ra", "mc": "nghề nghiệp và địa vị"}
TOP = 6
MIN_SCORE = MS.NOTABLE
KIND = {"conjunction": "trùng tụ: hai việc trộn vào nhau", "opposition": "góc đối: hai phía kéo nhau, cần cân bằng",
        "square": "góc vuông: va chạm, thúc ép, vẫn còn đường hòa giải", "trine": "tam hợp: nâng đỡ", "sextile": "lục hợp: thuận, cần chút chủ động"}
ANGLE_VI = {"asc": "cung Mọc", "mc": "Thiên Đỉnh", "dsc": "điểm Lặn", "ic": "Thiên Để"}


_TZ: list = [None]          # the birth time zone while a reading is built (Western requests run one at a time)


def _d(iso: str) -> str:
    """A date as the reader's calendar shows it at the birthplace (the engine's instants are UTC)."""
    d = dt.datetime.fromisoformat(iso)
    if _TZ[0] is not None and d.tzinfo is not None:
        d = d.astimezone(_TZ[0])
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def _area(f: Facts, p: str) -> str:
    """The life area a natal point stands in, by Lilly's house meanings read in Lilly's own houses (pp.50-56)."""
    if p in POINT_AREA:
        return POINT_AREA[p]
    h = f.house_lilly(p) if f.time_known and p in f.lon else None
    if not h:
        return ""
    words = [w.strip() for w in M["houses"][str(h)]["lilly"]["vi"].split(";")[0].split(",")][:2]
    return f"{', '.join(words)} (nghĩa của Nhà {h} theo Lilly)"


def _label(e: dict) -> str:
    return f"{P(e['transiting'])} {ASPECT_WITH[e['aspect']]} {P(e['natal'])} gốc"


def _period(e: dict) -> str:
    a = _d(e["start"]) if e["start"] else "trước đó"
    b = _d(e["end"]) if e["end"] else "sau khung xem"
    return f"{a} – {b}"


def _why(e: dict) -> str:
    return ", ".join(f"{MS.WHY[k]} +{v}" for k, v in e["score_parts"])


def _active(e: dict, a: dt.datetime, b: dt.datetime) -> bool:
    s = dt.datetime.fromisoformat(e["start"]) if e["start"] else a
    t = dt.datetime.fromisoformat(e["end"]) if e["end"] else b
    return s <= b and t >= a


def _ev_transit(e: dict) -> dict:
    return {"kind": "transit", "id": f"{e['transiting']}-{e['aspect']}-{e['natal']}", "transiting": e["transiting"], "natal": e["natal"],
            "aspect": e["aspect"], "label": _label(e)}


def _prog_text(e: dict) -> str:
    who = P(e["progressed"])
    if e["type"] == "aspect":
        return f"{who} tiến trình {ASPECT_WITH[e['aspect']]} {P(e['natal'])} gốc ({_d(e['date'])})"
    if e["type"] == "ingress":
        return f"{who} tiến trình {'đi lùi, trở lại' if e.get('retrograde') else 'sang'} {S(e['sign'])} ({_d(e['date'])})"
    if e["type"] == "station":
        return f"{who} tiến trình đứng lại rồi {'bắt đầu đi lùi' if e['turns'] == 'retrograde' else 'đi thuận trở lại'} ({_d(e['date'])})"
    return f"{who} tiến trình {'lùi lại' if e.get('retrograde') else 'sang'} Nhà {e['house']} gốc ({_d(e['date'])})"


def _next_return(c: dict, when: dt.datetime) -> dict:
    y = when.year if R.solar_return_jd(c, when.year) > float(E.time_utc(when).ut1) else when.year + 1
    return R.solar_return(c, y)


def cycles(f: Facts, when: dt.datetime) -> list[Para]:
    from tvbt.calendar_core import zone_of
    try:
        _TZ[0] = zone_of(f.c["input"]["tz"])
        return _cycles(f, when)
    finally:
        _TZ[0] = None


def _cycles(f: Facts, when: dt.datetime) -> list[Para]:
    c, out = f.c, []
    w0, w1 = when - dt.timedelta(days=30), when + dt.timedelta(days=365)
    age = R.age_at(c, when) if f.time_known else None
    pr = R.profection(c, age) if f.time_known else None
    lord = pr["lord"] if pr else None
    ruler = MS.chart_ruler(c)
    movers = SLOW + ((ruler,) if ruler in ("sun", "mercury", "venus") else ())
    ev = T.find(c, w0, w1, transiting=movers, aspects=("conjunction", "opposition", "square", "trine", "sextile"))
    ranked = MS.rank(ev, c, lord)
    top = [e for e in ranked if e["score"] >= MIN_SCORE][:TOP] or ranked[:3]
    pc = PR.chart(c, when)
    tl = PR.timeline(c, max(0.0, pc["age_years"] - 1.5), pc["age_years"] + 1.5)
    prog = [e for e in tl["events"] if f.time_known or (e["progressed"] != "moon" and e["type"] != "house")]
    soon = [e for e in prog if w0 <= dt.datetime.fromisoformat(e["date"]) <= w1 and e["type"] != "house"]
    sr = _next_return(c, when) if f.time_known else None
    pm = pc["bodies"]["moon"]

    # ---------------------------------------------------------------- the year in plain words
    if pr:
        th = M["houses"][str(pr["house"])]
        theme = ", ".join(w.strip() for w in th["lilly"]["vi"].split(";")[0].split(",")[:2])
        t = (f"Năm tuổi {age} của bạn ({_d(pr['start_utc'])} – {_d(pr['end_utc'])}) là năm của {S(pr['sign'])}, Nhà {pr['house']} tính từ cung Mọc: "
             f"mảng đời được nhắc tới nhiều là {theme}, và {P(lord)} làm chủ năm. ")
    else:
        t = "Không có giờ sinh nên không có phép đếm năm và lá Solar Return; phần dưới chỉ còn transit và tiến trình. "
    if top:
        t += ("Trong mười hai tháng tới, những lúc chủ đề của lá gốc được nhắc tới rõ nhất (chọn theo điểm ghi ở phần Transit) là "
              + listing([f"{_label(e)} ({_period(e)}; {KIND[e['aspect']]})" for e in top[:3]]) + ". ")
    else:
        t += "Mười hai tháng tới không có transit nào của các hành tinh chậm đạt mức nổi bật theo tiêu chí của Thiên Bàn. "
    key_prog = (next((e for e in soon if e["progressed"] == "sun" and e["type"] == "aspect"), None)
                or next((e for e in soon if e["type"] in ("station", "ingress") and e["progressed"] in ("sun", "mercury", "venus", "mars")), None)
                or next((e for e in soon if e["progressed"] == "moon"), None))
    if key_prog:
        past = dt.datetime.fromisoformat(key_prog["date"]) < when
        t += f"Về tiến trình, {'vừa có' if past else 'đáng để ý sắp tới là'} {_prog_text(key_prog)}. "
    t += "Mỗi kỹ thuật được đọc riêng ở dưới; chúng cho thấy lúc nào chủ đề nào của lá gốc được nhắc tới, không cộng lại thành một lời đoán chung."
    out.append(Para("tv.tom_tat", "Tóm tắt: mười hai tháng tới", t, "compare",
                    srcs("VALENS_ANTH:IV.11", "LILLY_CA:pp.726-727", "LEO:The Progressed Horoscope p.193", "LEO:The Progressed Horoscope p.68"),
                    ([ev_planet(c, lord)] if lord else []) + [_ev_transit(e) for e in top[:3]] or [ev_planet(c, "sun")],
                    "overview", topic="thoi_van", layer="summary", keys=[f"year_lord:{lord}"] if lord else [],
                    steps=["Khung xem: từ 30 ngày trước ngày đọc đến 365 ngày sau.", MS.__doc__.strip()]))

    # ---------------------------------------------------------------- four techniques, four questions
    ex_tr = f"như {_label(top[0])} ({_period(top[0])})" if top else "khi một hành tinh đi tạo góc với một điểm gốc"
    bits = []
    if pr:
        bits.append(f"phép đếm năm (profection) trả lời câu 'năm nay mảng đời nào được gọi tên': cứ mỗi năm tuổi, cung Mọc tiến thêm một cung, nên năm nay của bạn rơi vào Nhà {pr['house']}")
    bits.append(f"transit là bầu trời thật của từng ngày đặt lên lá gốc, trả lời câu 'lúc nào thì châm ngòi', {ex_tr}")
    bits.append("tiến trình thứ cấp lấy bầu trời của ngày thứ N sau khi sinh làm năm tuổi thứ N, nên đổi rất chậm và cho bức tranh của nhiều năm"
                + (f": Mặt Trăng tiến trình của bạn hiện ở {pm['fmt']} {S(pm['sign'])}" if f.time_known else ""))
    if sr:
        bits.append(f"Solar Return là lá số của đúng khoảnh khắc Mặt Trời trở về độ lúc sinh, mỗi năm một lần: lần tới của bạn là {_d(sr['exact_utc'])}")
    t2 = ("Bốn kỹ thuật dưới đây hỏi bốn câu khác nhau. " + "; ".join(cap(b) if i == 0 else b for i, b in enumerate(bits)) + ". "
          "Chúng thuộc các trường phái khác nhau (Valens và Lilly cho phép đếm năm và Solar Return, Alan Leo cho tiến trình và thứ bậc transit), "
          "nên được đặt cạnh nhau chứ không gộp làm một.")
    out.append(Para("tv.explain", "Bốn kỹ thuật khác nhau thế nào", t2, "compare",
                    srcs("VALENS_ANTH:IV.11", "LEO:The Progressed Horoscope p.193", "LEO:The Progressed Horoscope p.27", "LILLY_CA:p.734"),
                    [ev_planet(c, "moon")] + ([_ev_transit(top[0])] if top else []), "overview", topic="thoi_van", layer="summary"))

    # ---------------------------------------------------------------- quarter by quarter
    rows = []
    for q in range(4):
        a, b = when + dt.timedelta(days=91 * q), when + dt.timedelta(days=91 * (q + 1))
        tr = [e for e in top if _active(e, a, b)][:2]
        pg = [e for e in soon if a <= dt.datetime.fromisoformat(e["date"]) < b][:2]
        bits = []
        if tr:
            bits.append("transit: " + listing([_label(e) for e in tr]))
        if pg:
            bits.append("tiến trình: " + listing([_prog_text(e) for e in pg]))
        if sr and a <= dt.datetime.fromisoformat(sr["exact_utc"]) < b:
            nl = dignity.domicile_lord(SIGNS[(sign_index(f.lon["asc"]) + age + 1) % 12])
            bits.append(f"Solar Return {_d(sr['exact_utc'])} mở năm tuổi {age + 1}, chủ năm mới là {P(nl)}")
        rows.append(f"Quý {q + 1} ({_d(a.isoformat())} – {_d(b.isoformat())}): " + ("; ".join(bits) if bits else "không có mốc nào đạt tiêu chí nổi bật"))
    out.append(Para("tv.periods", "Từng quý trong năm tới", ". ".join(rows) + ".", "compare",
                    srcs("LEO:The Progressed Horoscope p.193", "LEO:The Progressed Horoscope p.68", "LILLY_CA:p.734"),
                    [_ev_transit(e) for e in top[:4]], "overview", topic="thoi_van",
                    steps=["Mỗi quý chỉ liệt kê tối đa hai transit (trong số đã chọn theo điểm) và hai sự kiện tiến trình; mỗi kỹ thuật đứng riêng."]))

    # ---------------------------------------------------------------- profection
    if pr:
        h = pr["house"]
        th = M["houses"][str(h)]
        t = (f"⟦Valens đếm năm theo cách 'chuyển giao': mỗi năm tuổi, cung Mọc tiến thêm một cung (IV.11); Lilly dùng cùng nguyên tắc và bắt đầu mỗi năm đúng lúc Mặt Trời trở về vị trí lúc sinh (tr.715-716).⟧ "
             f"Năm nay ({_d(pr['start_utc'])} đến {_d(pr['end_utc'])}) bạn tròn {age} tuổi, nên cung của năm là {S(pr['sign'])}, Nhà {h} tính trọn cung: "
             f"nơi Valens gắn với {th['valens']['vi']}, Lilly gắn với {th['lilly']['vi'].split(';')[0]}. "
             f"Chủ của năm là {P(lord)}, chủ của {S(pr['sign'])}. Lilly bảo xét trước hết vị trí và tình trạng của chủ năm trong lá số gốc (tr.726-727): "
             f"{P(lord)} {lilly_condition(f, lord)}.")
        woke = [p for p in pr["natal_planets_in_sign"] if p in CLASSICAL]
        if woke:
            t += (f" Trong lá số gốc, {planet_list(woke)} đứng ở {S(pr['sign'])}, nên năm nay "
                  + ("sao này cũng được nhắc tới." if len(woke) == 1 else "những sao này cũng được nhắc tới."))
        out.append(Para("tv.profection", f"Năm {age} tuổi: phép đếm năm (profection)", t, "compare", srcs("VALENS_ANTH:IV.11", "LILLY_CA:pp.715-716", "LILLY_CA:pp.726-727"),
                        [ev_planet(c, lord)], "overview", topic="thoi_van", keys=[f"profection:{pr['sign']}:{lord}"],
                        steps=[f"Tuổi {age} → {age} cung tính từ cung Mọc {S(c['angles']['asc']['sign'])} → {S(pr['sign'])} (Nhà {h} trọn cung).",
                               "Chu kỳ lặp lại sau mỗi 12 năm; Valens nói những lần chuyển giao giống nhau trở lại nhưng với sức mạnh khác (IV.11).",
                               "Chỉ bảy hành tinh cổ điển được nói là 'được nhắc tới'; Thiên Vương, Hải Vương, Diêm Vương không có trong phép này."]))
        topics = {"sun": "địa vị", "moon": "người mẹ", "mc": "nghề nghiệp", "fortune": "thành công"}
        bits = []
        for k, lab in topics.items():
            lon = c["lots"]["fortune"]["lon"] if k == "fortune" else (c["angles"]["mc"]["lon"] if k == "mc" else f.lon[k])
            s = SIGNS[(sign_index(lon) + age) % 12]
            bits.append(f"tính từ {'Thiên Đỉnh' if k == 'mc' else 'Lot of Fortune' if k == 'fortune' else P(k)} ({lab}) năm nay rơi vào {S(s)}, chủ là {P(dignity.domicile_lord(s))}")
        out.append(Para("tv.profection_topics", "Các điểm đếm khác của Valens", "Valens không chỉ đếm từ cung Mọc mà còn từ Mặt Trời, Mặt Trăng, Thiên Đỉnh và Lot of Fortune, mỗi điểm cho một mảng đời (IV.11): "
                        + "; ".join(bits) + ". Khi một hành tinh làm chủ nhiều điểm cùng lúc, năm ấy chủ đề của nó nổi lên rõ hơn.", "hellenistic", srcs("VALENS_ANTH:IV.11"), [], "deep", topic="thoi_van"))

    # ---------------------------------------------------------------- transits, picked by a written score
    if top:
        lines = []
        for e in top:
            area = _area(f, e["natal"])
            ex = (", chính xác " + listing([_d(x) + (" (đang nghịch hành)" if r else "") for x, r in zip(e["exact"], e["retro_at_exact"])])) if e["exact"] else ", chưa tới điểm chính xác trong khung này"
            lines.append(f"{_label(e)}: hiệu lực {_period(e)}{ex}" + (f"; mảng đời liên quan: {area}" if area else "")
                         + (f"; vòng nghịch hành đưa nó qua cùng một điểm {e['spans']} lần" if e.get("spans", 1) > 1 else "")
                         + f" (điểm {e['score']}: {_why(e)})")
        t = ("⟦Alan Leo xếp Sao Mộc, Sao Thổ, Sao Hỏa và Sao Thiên Vương là những hành tinh transit chính (The Progressed Horoscope tr.193), và coi transit chỉ châm ngòi "
             "cho điều đã có trong lá gốc và trong các tiến trình đang hoạt động (tr.192, tr.202); Valens dặn xác nhận năm chuyển giao bằng các hành tinh đang đi qua (IV.11).⟧ "
             f"Trong {len(ranked)} góc transit của các hành tinh chậm tìm thấy cho mười hai tháng tới, {len(top)} mốc được chọn: " + "; ".join(lines) + ".")
        out.append(Para("tv.transits", "Transit đáng chú ý và vì sao", t, "compare",
                        srcs("LEO:The Progressed Horoscope p.193", "LEO:The Progressed Horoscope p.192", "LEO:The Progressed Horoscope p.202", "VALENS_ANTH:IV.11", "LILLY_CA:pp.50-56"),
                        [_ev_transit(e) for e in top], "overview", topic="thoi_van",
                        steps=[MS.__doc__.strip(), f"Orb transit {num(T.orb_table()['jupiter'])}° cho hành tinh chậm, {num(T.orb_table()['mars'])}° cho Sao Hỏa (quy ước Thiên Bàn).",
                               "Các lần chạm trong cùng một vòng nghịch hành được tính là một mốc."]))

    # ---------------------------------------------------------------- solar return
    if sr:
        rel = sr["relation"]
        hits = rel.get("sr_angles_on_natal_planets", [])
        t3 = (f"Lilly lập lá số 'hồi quy' (revolution) cho đúng lúc Mặt Trời trở về độ và phút lúc sinh (tr.734): lần tới là {_d(sr['exact_utc'])} "
              f"lúc {dt.datetime.fromisoformat(sr['exact_utc']).astimezone(UTC):%H:%M} UTC, tính cho nơi sinh. Cung Mọc của lá hồi quy là {S(sr['chart']['angles']['asc']['sign'])}, "
              f"rơi vào Nhà {rel.get('sr_asc_in_natal_house')} của lá số gốc ({f.system_vi('modern')}). ")
        nl = dignity.domicile_lord(SIGNS[(sign_index(f.lon["asc"]) + age + 1) % 12])
        lp = sr["chart"]["bodies"][nl]
        t3 += f"Chủ của năm tuổi {age + 1} là {P(nl)}, đứng ở {S(lp['sign'])}, Nhà {lp['house']} của lá hồi quy ({f.system_vi('modern')}). "
        if hits:
            t3 += "Các góc của lá hồi quy trùng với hành tinh gốc: " + listing([f"{ANGLE_VI[h['sr_angle']]} trên {P(h['natal'])} (cách {num(h['orb'])}°)" for h in hits[:3]]) + ". "
        t3 += "Lilly đọc lá hồi quy cùng với lá gốc và lá chuyển giao của năm (tr.726); Valens thì dựng lại lá năm theo cách khác (lấy cung Mọc khi Mặt Trăng trở về độ lúc sinh, V.5) mà Thiên Bàn chưa tính."
        out.append(Para("tv.solar_return", "Solar Return sắp tới", t3, "compare", srcs("LILLY_CA:p.734", "LILLY_CA:p.726", "VALENS_ANTH:V.5"),
                        [ev_planet(c, nl)], "deep", topic="thoi_van"))

    # ---------------------------------------------------------------- progressions
    sun_asp = [e for e in tl["events"] if e["type"] == "aspect" and e["progressed"] == "sun"]
    ps = pc["bodies"]["sun"]
    t4 = (f"⟦Theo Alan Leo, mỗi ngày sau khi sinh ứng với một năm cuộc đời (The Progressed Horoscope, tr.27).⟧ Ở tuổi {num(pc['age_years'])}, Mặt Trời tiến triển ở {ps['fmt']} {S(ps['sign'])}"
          + (f", Mặt Trăng tiến triển ở {pm['fmt']} {S(pm['sign'])}" + (f" (Nhà {pm['natal_house']} của lá gốc, {f.system_vi('modern')})" if pm.get("natal_house") else "") if f.time_known else "") + ". ")
    if sun_asp:
        e = sun_asp[0]
        t4 += (f"Mặt Trời tiến triển {'đã' if e['age'] < pc['age_years'] else 'sẽ'} {ASPECT_WITH[e['aspect']]} {P(e['natal'])} gốc, chính xác vào {_d(e['date'])}; "
               f"Leo coi góc của Mặt Trời tiến triển như 'kim giờ' báo giai đoạn, kéo dài khoảng ba năm (một năm tới gần, một năm chính xác, một năm tách ra; tr.68). ")
    else:
        t4 += "Trong khoảng ba năm quanh hiện tại, Mặt Trời tiến triển không tạo góc chính nào với lá gốc; Leo nói năm không có góc Mặt Trời thì ít biến động hơn (tr.69). "
    others = [e for e in tl["events"] if e["progressed"] in ("mercury", "venus", "mars") and e["type"] in ("station", "ingress")]
    if others:
        t4 += ("Các hành tinh khác cũng đổi trạng thái trong khoảng này: " + listing([_prog_text(e) for e in others[:3]])
               + "; Leo không cho câu luận riêng cho các thay đổi này trong phần Thiên Bàn đã đọc, nên ở đây chỉ ghi lại. ")
    moon_ev = [e for e in tl["events"] if e["progressed"] == "moon" and e["age"] >= pc["age_years"]][:2] if f.time_known else []
    if moon_ev:
        t4 += ("Mặt Trăng tiến triển là 'kim phút', định lúc các xu hướng ấy hiện ra (tr.68): sắp tới " + listing([_prog_text(e).replace("Mặt Trăng tiến trình ", "") for e in moon_ev])
               + ". Leo dặn góc của Mặt Trăng chỉ thật sự quan trọng khi cùng tính chất với góc của Mặt Trời đang có (tr.95).")
    out.append(Para("tv.progressions", "Tiến trình thứ cấp (secondary progressions)", t4, "modern",
                    srcs("LEO:The Progressed Horoscope p.27", "LEO:The Progressed Horoscope p.68", "LEO:The Progressed Horoscope p.69", "LEO:The Progressed Horoscope p.95"),
                    [ev_planet(c, "sun")] + ([ev_planet(c, "moon")] if f.time_known else []), "overview" if not f.time_known else "deep", topic="thoi_van",
                    steps=["Năm chí tuyến 365,24219 ngày; góc Mặt Trời tiến triển với orb 1° (suy từ 'ba năm' của Leo, tr.68).",
                           f"Ngày tương ứng trong lịch thiên văn: {pc['progressed_date_utc'][:10]}."]))
    return out
