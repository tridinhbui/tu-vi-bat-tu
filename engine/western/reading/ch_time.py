"""Chapter 'Thời vận': one paragraph per technique (profection, transits, solar return, progressions), never a merged score."""
from __future__ import annotations

import datetime as dt

from .. import dignity, progressions as PR, returns as R, transits as T
from ..zodiac import SIGNS, sign_index
from .ch_core import M, lilly_condition
from .compose import Para, ev_planet, ev_point, listing, planet_list, srcs
from .facts import CLASSICAL, Facts
from .vocab import ASPECT_NOUN, ASPECT_VI, ASPECT_WITH, P, S, num

UTC = dt.timezone.utc
SLOW = ("jupiter", "saturn", "uranus", "neptune", "pluto", "mars")


def _d(iso: str) -> str:
    d = dt.datetime.fromisoformat(iso)
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def cycles(f: Facts, when: dt.datetime) -> list[Para]:
    c, out = f.c, []
    if not f.time_known:
        out.append(Para("tv.no_time", "Thời vận", "Annual profection và Solar Return cần giờ sinh (cung Mọc là điểm xuất phát), nên phần này chỉ còn Secondary Progressions của Mặt Trời "
                        "và các hành tinh chậm; Mặt Trăng tiến triển không xác định được vì nó đi 13° mỗi ngày.", "calc", [], [], "overview", tier="calc", topic="thoi_van"))
    age = R.age_at(c, when) if f.time_known else None
    if f.time_known:
        pr = R.profection(c, age)
        lord = pr["lord"]
        h = pr["house"]
        th = M["houses"][str(h)]
        t = (f"⟦Valens đếm năm theo cách 'chuyển giao': mỗi năm tuổi, cung Mọc tiến thêm một cung (IV.11); Lilly dùng cùng nguyên tắc và bắt đầu mỗi năm đúng lúc Mặt Trời trở về vị trí lúc sinh (tr.715-716).⟧ "
             f"Năm nay ({_d(pr['start_utc'])} đến {_d(pr['end_utc'])}) bạn tròn {age} tuổi, nên cung của năm là {S(pr['sign'])}, Nhà {h} của lá số: "
             f"nơi Valens gắn với {th['valens']['vi']}, Lilly gắn với {th['lilly']['vi']}. ")
        t += (f"Chủ của năm là {P(lord)}, chủ của {S(pr['sign'])}. Lilly bảo xét trước hết vị trí và tình trạng của chủ năm trong lá số gốc (tr.726-727): "
              f"{P(lord)} {lilly_condition(f, lord)}.")
        if pr["natal_planets_in_sign"]:
            t += f" Trong lá số gốc, {planet_list(pr['natal_planets_in_sign'])} đứng ở {S(pr['sign'])}, nên năm nay những sao này cũng được 'đánh thức'."
        out.append(Para("tv.profection", f"Năm {age} tuổi: Annual Profection", t, "compare", srcs("VALENS_ANTH:IV.11", "LILLY_CA:pp.715-716", "LILLY_CA:pp.726-727"),
                        [ev_planet(c, lord, f.place_ws(lord))], "overview", topic="thoi_van", keys=[f"profection:{pr['sign']}:{lord}"],
                        steps=[f"Tuổi {age} → {age} cung tính từ cung Mọc {S(c['angles']['asc']['sign'])} → {S(pr['sign'])} (Nhà {h} trọn cung).",
                               "Chu kỳ lặp lại sau mỗi 12 năm; Valens nói những lần chuyển giao giống nhau trở lại nhưng với sức mạnh khác (IV.11)."]))
        topics = {"sun": "địa vị", "moon": "người mẹ", "mc": "nghề nghiệp", "fortune": "thành công"}
        bits = []
        for k, lab in topics.items():
            lon = c["lots"]["fortune"]["lon"] if k == "fortune" else (c["angles"]["mc"]["lon"] if k == "mc" else f.lon[k])
            s = SIGNS[(sign_index(lon) + age) % 12]
            bits.append(f"tính từ {'Thiên Đỉnh' if k == 'mc' else 'Lot of Fortune' if k == 'fortune' else P(k)} ({lab}) năm nay rơi vào {S(s)}, chủ là {P(dignity.domicile_lord(s))}")
        out.append(Para("tv.profection_topics", "Các điểm đếm khác của Valens", "Valens không chỉ đếm từ cung Mọc mà còn từ Mặt Trời, Mặt Trăng, Thiên Đỉnh và Lot of Fortune, mỗi điểm cho một mảng đời (IV.11): "
                        + "; ".join(bits) + ". Khi một hành tinh làm chủ nhiều điểm cùng lúc, năm ấy chủ đề của nó nổi lên rõ hơn.", "hellenistic", srcs("VALENS_ANTH:IV.11"), [], "deep", topic="thoi_van"))
        start, end = dt.datetime.fromisoformat(pr["start_utc"]), dt.datetime.fromisoformat(pr["end_utc"])
        ev = T.find(c, start, end, transiting=SLOW, aspects=("conjunction", "opposition", "square", "trine"))
        slow = ("jupiter", "saturn", "uranus", "neptune", "pluto")
        sel = [e for e in ev if (e["transiting"] in slow and (e["natal"] in (lord, "sun", "moon", "asc", "mc")))
               or (e["transiting"] == lord and e["transiting"] in slow) or (e["transiting"] == "mars" and e["natal"] == lord and e["aspect"] == "conjunction")]
        groups: dict = {}
        for e in sel:
            groups.setdefault((e["transiting"], e["natal"], e["aspect"]), []).append(e)
        items = sorted(groups.items(), key=lambda kv: min((x["exact"][0] if x["exact"] else x["start"] or x["end"] or "") for x in kv[1]))[:5]
        if items:
            lines = []
            for (tp, na, asp), es in items:
                exacts = [x for e in es for x in e["exact"]]
                if exacts:
                    when_s = listing([_d(x) for x in exacts])
                    lines.append(f"{P(tp)} {ASPECT_WITH[asp]} {P(na)} lúc sinh, chính xác {when_s}")
                else:
                    e = es[0]
                    lines.append(f"{P(tp)} trong orb {ASPECT_NOUN[asp]} với {P(na)} lúc sinh ({_d(e['start']) if e['start'] else '…'} – {_d(e['end']) if e['end'] else '…'}), chưa chính xác trong năm này")
            t2 = ("⟦Valens dặn xác nhận năm chuyển giao bằng các hành tinh đang đi qua (transit) lặp lại cấu hình lúc sinh (IV.11); Alan Leo xếp Sao Mộc, Sao Thổ, Sao Hỏa và Sao Thiên Vương là những transit đáng kể nhất (The Progressed Horoscope).⟧ "
                  f"Trong năm chuyển giao này, xét các hành tinh chậm tới chủ năm {P(lord)}, hai sao sáng và hai góc chính: " + "; ".join(lines) +
                  ". ⟦Với Leo, transit chỉ châm ngòi cho điều đã có trong lá số gốc và trong các progression đang hoạt động, không tự nó tạo ra biến cố.⟧")
            out.append(Para("tv.transits", "Transit đáng chú ý trong năm", t2, "compare", srcs("VALENS_ANTH:IV.11", "LEO:The Progressed Horoscope"),
                            [{"kind": "aspect", "id": f"{k[0]}-{k[2]}-{k[1]}", "label": f"{P(k[0])} {ASPECT_WITH[k[2]]} {P(k[1])}"} for k, _ in items[:3]], "overview", topic="thoi_van",
                            steps=[f"Orb transit {num(T.orb_table()['jupiter'])}° cho hành tinh chậm (quy ước Thiên Bàn); khoảng xét: năm chuyển giao {_d(pr['start_utc'])} – {_d(pr['end_utc'])}."]))
        sr = R.solar_return(c, start.year)            # the profection year begins at this return
        rel = sr["relation"]
        hits = rel.get("sr_angles_on_natal_planets", [])
        t3 = (f"Lilly lập lá số 'hồi quy' (revolution) cho đúng lúc Mặt Trời trở về độ và phút lúc sinh (tr.734): năm nay là {_d(sr['exact_utc'])} "
              f"lúc {dt.datetime.fromisoformat(sr['exact_utc']).astimezone(UTC):%H:%M} UTC, tính cho nơi sinh. Cung Mọc của lá hồi quy là {S(sr['chart']['angles']['asc']['sign'])}, "
              f"rơi vào Nhà {rel.get('sr_asc_in_natal_house')} của lá số gốc. ")
        lp = sr["chart"]["bodies"][lord]
        t3 += f"Chủ năm {P(lord)} đứng ở {S(lp['sign'])}, Nhà {lp['house']} của lá hồi quy. "
        if hits:
            t3 += "Các góc của lá hồi quy trùng với hành tinh gốc: " + listing([f"{ {'asc': 'cung Mọc', 'mc': 'Thiên Đỉnh', 'dsc': 'điểm Lặn', 'ic': 'Thiên Để'}[h['sr_angle']]} trên {P(h['natal'])} (cách {num(h['orb'])}°)" for h in hits[:3]]) + ". "
        t3 += "Lilly đọc lá hồi quy cùng với lá gốc và lá chuyển giao của năm (tr.726); Valens thì dựng lại lá năm theo cách khác (lấy cung Mọc khi Mặt Trăng trở về độ lúc sinh, V.5) mà Thiên Bàn chưa tính."
        out.append(Para("tv.solar_return", "Solar Return năm nay", t3, "compare", srcs("LILLY_CA:p.734", "LILLY_CA:p.726", "VALENS_ANTH:V.5"),
                        [ev_planet(c, lord)], "deep", topic="thoi_van"))
    pc = PR.chart(c, when)
    tl = PR.timeline(c, max(0.0, pc["age_years"] - 1.5), pc["age_years"] + 1.5, bodies=("sun", "moon"))
    sun_asp = [e for e in tl["events"] if e["type"] == "aspect" and e["progressed"] == "sun"]
    sun_ing = [e for e in tl["events"] if e["type"] == "ingress" and e["progressed"] == "sun"]
    moon_ev = [e for e in tl["events"] if e["progressed"] == "moon"]
    ps, pm = pc["bodies"]["sun"], pc["bodies"]["moon"]
    t4 = (f"⟦Theo Alan Leo, mỗi ngày sau khi sinh ứng với một năm cuộc đời (The Progressed Horoscope, tr.27).⟧ Ở tuổi {num(pc['age_years'])}, Mặt Trời tiến triển ở {ps['fmt']} {S(ps['sign'])}"
          + (f", Mặt Trăng tiến triển ở {pm['fmt']} {S(pm['sign'])}" + (f" (Nhà {pm['natal_house']} của lá gốc)" if pm.get("natal_house") else "") if f.time_known else "") + ". ")
    if sun_ing:
        e = sun_ing[0]
        t4 += (f"Mặt Trời tiến triển {'đã sang' if e['age'] < pc['age_years'] else 'sẽ sang'} {S(e['sign'])} vào {_d(e['date'])}; với Leo, khi Mặt Trời tiến triển đổi cung, "
               f"sắc thái của cung mới thấm dần vào cá tính trong nhiều năm, còn cung gốc vẫn là nền. ")
    if sun_asp:
        e = sun_asp[0]
        t4 += (f"Mặt Trời tiến triển {'đã' if e['age'] < pc['age_years'] else 'sẽ'} {ASPECT_WITH[e['aspect']]} {P(e['natal'])} gốc, chính xác vào {_d(e['date'])}; "
               f"Leo coi các góc của Mặt Trời tiến triển như 'kim giờ', mỗi góc kéo dài khoảng ba năm (một năm tới gần, một năm chính xác, một năm tách ra).")
    else:
        t4 += "Trong khoảng ba năm quanh hiện tại, Mặt Trời tiến triển không tạo góc chính nào với lá gốc; Leo nói năm không có góc Mặt Trời thì ít biến động hơn."
    if f.time_known and moon_ev:
        nxt = [e for e in moon_ev if e["age"] >= pc["age_years"]][:2]
        if nxt:
            t4 += " Mặt Trăng tiến triển là 'kim phút', định lúc các xu hướng ấy hiện ra: sắp tới " + listing([
                (f"{ASPECT_NOUN[e['aspect']]} với {P(e['natal'])} gốc ({_d(e['date'])})" if e["type"] == "aspect"
                 else f"vào {S(e['sign'])} ({_d(e['date'])})" if e["type"] == "ingress" else f"sang Nhà {e['house']} ({_d(e['date'])})") for e in nxt]) + "."
        t4 += " Leo dặn góc của Mặt Trăng chỉ thật sự quan trọng khi cùng tính chất với góc của Mặt Trời đang có."
    out.append(Para("tv.progressions", "Secondary Progressions", t4, "modern", srcs("LEO:The Progressed Horoscope p.27"),
                    [ev_planet(c, "sun")], "overview" if not f.time_known else "deep", topic="thoi_van",
                    steps=["Năm chí tuyến 365,24219 ngày; góc Mặt Trời tiến triển với orb 1° (suy từ 'ba năm' của Leo).", f"Ngày tương ứng trong lịch thiên văn: {pc['progressed_date_utc'][:10]}."]))
    return out
