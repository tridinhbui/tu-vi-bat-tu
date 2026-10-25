"""Chapters 'Tổng quan', 'Tính cách', 'Tư duy và học tập', 'Cảm xúc'. Every sentence voices a cited rule applied to this chart."""
from __future__ import annotations

from .. import dignity, kb
from ..zodiac import ELEMENT, MODALITY, SIGNS, sign_index
from .compose import Para, cap, ev_aspect, ev_house, ev_planet, ev_point, listing, pick, planet_list, srcs
from .facts import CLASSICAL, FIVE, OPERATIONAL, Facts
from .vocab import ASPECT_NOUN, ASPECT_VI, DIGNITY_VI, ELEMENT_VI, MODALITY_VI, P, S, SOLAR_VI, TEMPERAMENT_VI, at, num

M = kb.load("meanings")
VALENS_REJOICE_DAY_ABOVE = ("sun", "jupiter", "saturn")          # Valens III.5
GRADE_VI = {"fortunate": "một nơi thuận vì là góc hoặc nơi 'hữu hiệu'", "moderate": "một nơi trung bình vì theo sau một góc",
            "base": "một nơi yếu vì đứng ngay trước một góc"}


def lilly_condition(f: Facts, p: str, with_house: bool = True) -> str:
    """'ở nhà của mình, đứng ở góc Nhà 10, đang nghịch hành' — from Lilly's points (pp.101-115). The full description is given
    the first time a planet comes up in a reading; later mentions use the short form, so chapters do not repeat each other."""
    e = f.lilly_essential(p)
    seen = f.__dict__.setdefault("_described", set())
    if p in seen:
        st = f.lilly_state(p)
        word = {"well": "đắc thế", "ill": "thất thế", "mixed": "phẩm vị lưng chừng"}[st]
        key = (e["has"][:1] or e["debilities"][:1] or (["peregrine"] if e["peregrine"] else []))
        return f"{word} ({DIGNITY_VI[key[0]].split(' (')[0]})" if key else word
    seen.add(p)
    bits = []
    if e["has"]:
        bits.append(listing([DIGNITY_VI[h] for h in e["has"]]))
    if e["debilities"]:
        bits.append(listing([DIGNITY_VI[d] for d in e["debilities"]]))
    if e["peregrine"] and not e["debilities"]:
        bits.append("không có phẩm vị nào ở độ đang đứng (lạc chỗ)")
    elif e["peregrine"]:
        bits.append("lại không có phẩm vị nào bù vào")
    if with_house and f.house_lilly(p):
        h = f.house_lilly(p)
        kind = "nhà góc" if h in (1, 4, 7, 10) else "nhà kế góc" if h in (2, 5, 8, 11) else "nhà suy"
        bits.append(f"ở Nhà {h} theo cách chia nhà Regiomontanus của Lilly ({kind})")
    sol = f.c["conditions"][p].get("solar", {}).get("phase")
    if sol:
        bits.append(SOLAR_VI[sol])
    if f.b[p].get("retrograde"):
        bits.append("đang đi nghịch")
    return listing(bits)


def described(f: Facts, p: str) -> bool:
    return p in f.__dict__.get("_described", set())


def _sect_paragraph(f: Facts) -> Para | None:
    if not f.time_known:
        return None
    c = f.c
    s = c["sect"]
    vl = f.valens_sect_lords()
    light = P(vl["light"])
    day = s["is_day"]
    first, second, co = vl["first"], vl["second"], vl["co"]
    above = {p: (f.b[p].get("house") or 0) >= 7 for p in ("sun", "moon", "mars", "venus", "jupiter", "saturn")}   # houses 7-12 = above the horizon
    glad = [p for p in above if (above[p] if ((p in VALENS_REJOICE_DAY_ABOVE) == day) else not above[p])]
    t1 = (f"Bạn sinh {'ban ngày' if day else 'ban đêm'}: lúc ấy Mặt Trời {'ở trên' if day else 'ở dưới'} đường chân trời "
          f"(cách chân trời {num(abs(s['sun_altitude']))}°). Trong chiêm tinh Hy Lạp, điều này định ra 'phe' (sect) của lá số: "
          f"{light} là sao sáng của phe, {P(s['benefic_of_sect'])} là cát tinh cùng phe, còn {P(s['malefic_contrary'])} là hung tinh khác phe, "
          f"thứ mà Valens coi là khó chịu nhất.")
    if s["borderline"]:
        t1 += " Mặt Trời nằm sát đường chân trời (dưới 1°), nên nếu giờ sinh lệch vài phút thì phe của lá số có thể đổi; hãy coi phần này là tạm."
    g1, g2 = vl["grades"][first], vl["grades"][second]
    course = {("fortunate", "fortunate"): "cả hai chặng đời đều có chỗ dựa",
              ("fortunate", "moderate"): "chặng đầu thuận hơn, chặng sau giữ được ở mức vừa",
              ("fortunate", "base"): "Valens đọc đây là thành công đến trước, rồi phải gìn giữ kỹ ở chặng sau",
              ("moderate", "fortunate"): "chặng đầu ở mức vừa, chặng sau mạnh lên",
              ("moderate", "moderate"): "cả hai chặng đều ở mức trung bình, không có bước nhảy lớn",
              ("moderate", "base"): "chặng đầu ở mức vừa, chặng sau cần dè dặt hơn",
              ("base", "fortunate"): "Valens đọc đây là những năm đầu nhiều lên xuống, về sau mới có sức bật",
              ("base", "moderate"): "những năm đầu nhiều lên xuống, chặng sau khá dần nhưng không bùng nổ",
              ("base", "base"): "cả hai chủ tam hợp đều ở nơi yếu, nên Valens dặn phải xét tiếp Lot of Fortune và chủ của nó"}[(g1, g2)]
    t2 = (f"{light} đang ở {S(f.b[vl['light']]['sign'])}, thuộc tam hợp {ELEMENT_VI[vl['element']]}; "
          f"chủ thứ nhất của tam hợp này với lá số {'ngày' if day else 'đêm'} là {P(first)}, đứng ở Nhà {vl['places'][first]} (tính trọn cung), {GRADE_VI[g1]}; "
          f"chủ thứ hai là {P(second)}, ở Nhà {vl['places'][second]}, {GRADE_VI[g2]}. Theo Valens (II.2), chủ thứ nhất nói về chặng đầu đời và chủ thứ hai về chặng sau: "
          f"{course}. Valens không chốt tuổi chuyển giao; ông chỉ nói nó đến theo vòng của các chủ thời gian.")
    t3 = ""
    if glad:
        t3 = (f" Thêm một chi tiết của Valens (III.5): {planet_list(glad)} đang ở đúng nửa trời mà phe {'ngày' if day else 'đêm'} ưa, "
              f"nên chúng 'vui' và làm việc của mình trọn vẹn hơn.")
    return Para("tq.sect", "Lá số ngày hay đêm, và hai chặng đời theo Valens", t1 + " " + t2 + t3, "hellenistic",
                srcs("PTOL_TETRA:I.7 p.43", "VALENS_ANTH:II.1", "VALENS_ANTH:II.2", "VALENS_ANTH:III.5"),
                [ev_planet(c, vl["light"]), ev_planet(c, first, vl["places"][first]), ev_planet(c, second, vl["places"][second])],
                "overview", steps=[f"Độ cao Mặt Trời lúc sinh: {s['sun_altitude']:.2f}° → lá số {'ngày' if day else 'đêm'}.",
                                   f"Tam hợp của {light}: {ELEMENT_VI[vl['element']]}; chủ ngày/đêm/đồng chủ theo Valens II.1: {P(vl['first'] if day else vl['second'])} / {P(vl['second'] if day else vl['first'])} / {P(co)}.",
                                   f"Xếp hạng nơi chốn theo Valens II.2: Nhà 1, 4, 7, 10, 11, 5 thuận; Nhà 2, 8 trung bình; Nhà 3, 6, 9, 12 yếu (tính trọn cung)."],
                polarity=+1 if (g1, g2).count("fortunate") >= 1 and "base" not in (g1, g2) else -1 if (g1, g2) == ("base", "base") else 0,
                topic="tong_quan", keys=[f"sect:{'day' if day else 'night'}"])


def _geniture_paragraph(f: Facts) -> Para | None:
    lg = f.lord_of_geniture
    if not lg:
        return None
    c = f.c
    lords = lg["lords"]
    p = lords[0]
    tot = lg["totals"]
    ranked = sorted(tot.items(), key=lambda x: -x[1])
    nature = M["planets"][p]["lilly_nature"]["vi"]
    second = ranked[1]
    t = (f"Lilly chọn 'hành tinh chủ lá số' (Lord of the Geniture) là sao gom được nhiều điểm phẩm vị nhất, cả bản chất lẫn ngẫu nhiên, "
         f"đứng tốt và cao nhất trên bầu trời (tr.531). Cộng theo bảng điểm của ông (tr.104 và tr.115), {P(p)} dẫn đầu với {tot[p]:+d} điểm"
         + (f", ngang với {planet_list(lords[1:])}, nên Lilly cho các sao này cùng chia vai" if len(lords) > 1 else
            f", trên {P(second[0])} ({second[1]:+d})") + ". "
         f"{P(p)} đang {lilly_condition(f, p)}. Với Lilly, {P(p)} mang bản chất {nature}; "
         f"là sao chủ lá số, nó nhuộm màu lên khí chất và cách hành xử của cả đời người.")
    if tot[p] < 5:
        t += " Có điều, điểm cao nhất ở lá số này vẫn khá khiêm tốn, nghĩa là không sao nào thật sự áp đảo; ảnh hưởng chia đều hơn cho nhiều hành tinh."
    acc = f.lilly_total(p)["accidental"]
    steps = [f"Điểm (bản chất + ngẫu nhiên) theo Lilly tr.104, 115: " + ", ".join(f"{P(k)} {v:+d}" for k, v in ranked) + ".",
             f"Chi tiết điểm ngẫu nhiên của {P(p)}: " + ", ".join(f"{k} {v:+d}" for k, v in acc) + ".",
             "Lilly không tính định tinh (Regulus, Spica, Algol) vào bảng này ở đây: Thiên Bàn chưa đưa phần định tinh vào điểm."]
    return Para("tq.geniture", "Hành tinh chủ lá số theo Lilly", t, "traditional", srcs("LILLY_CA:p.531", "LILLY_CA:p.104", "LILLY_CA:p.115"),
                [ev_planet(c, x, f.house_lilly(x)) for x in lords], "overview", steps=steps, topic="tong_quan", keys=[f"geniture:{p}"])


def _leo_centres(f: Facts) -> Para:
    c = f.c
    sun, moon = f.b["sun"]["sign"], f.b["moon"]["sign"]
    t = (f"Alan Leo đọc một lá số từ ba trung tâm, Mặt Trời trước hết (Astrology for All; How to Judge a Nativity). "
         f"Mặt Trời ở {S(sun)} cho phần 'cá tính' (individuality), cái lõi bền của con người: theo Leo, {M['leo_sun'][sun]}. "
         f"Mặt Trăng ở {S(moon)} cho phần 'nhân cách' (personality), tức cảm xúc và giác quan: {M['leo_moon'][moon]}.")
    if f.time_known:
        asc = c["angles"]["asc"]["sign"]
        t += (f" Cung Mọc {S(asc)} là trung tâm thứ ba, nói về thân thể và khuynh hướng bẩm sinh; Leo cho rằng khi con người trưởng thành, "
              f"cung Mọc dần hòa vào Mặt Trăng rồi vào Mặt Trời.")
        q = f.leo_centres()
        vals = list(q.values())
        if len(set(vals)) == 1:
            t += (f" Cả ba cùng thuộc nhóm {MODALITY_VI[vals[0]]} ({vals[0]}): theo phép thứ hai của Leo (The Art of Synthesis), "
                  f"đó là ý chí được nhấn mạnh theo kiểu {({'cardinal': 'nhanh, chủ động', 'fixed': 'bền, chịu đựng', 'mutable': 'linh hoạt, khéo thích nghi'})[vals[0]]}.")
        elif len(set(vals)) == 2:
            maj = max(set(vals), key=vals.count)
            t += (f" Hai trong ba trung tâm thuộc nhóm {MODALITY_VI[maj]}: theo Leo, nhóm này trội hơn và được nhóm còn lại làm mềm đi.")
    else:
        t += " Không có giờ sinh nên không có cung Mọc, trung tâm thứ ba của Leo; Mặt Trăng cũng có thể đã sang cung khác trong ngày (xem dữ kiện)."
    return Para("tq.leo", "Ba trung tâm theo Alan Leo", t, "modern", srcs("LEO:How to Judge a Nativity pp.72-86", "LEO:The Art of Synthesis"),
                [ev_planet(c, "sun"), ev_planet(c, "moon")] + ([ev_point(c, "asc")] if f.time_known else []), "overview",
                steps=["Leo xếp thứ tự quan trọng: vị trí Mặt Trời, vị trí Mặt Trăng, cung Mọc, rồi các góc hợp (Astrology for All)."],
                topic="tong_quan", keys=[f"sun_sign:{sun}", f"moon_sign:{moon}"])


def _complexion(f: Facts) -> Para | None:
    cx = f.lilly_complexion()
    if not cx:
        return None
    t = cx["tally"]
    kind = cx["temperament"]
    lines = cx["lines"]
    if kind:
        head = (f"Gộp các 'chứng' nóng, lạnh, ẩm, khô từ năm nguồn Lilly chỉ định (cung Mọc và chủ của nó, sao ở Nhà 1, Mặt Trăng và các sao chiếu nó, "
                f"mùa Mặt Trời đang ở, và sao chủ lá số; tr.533), lá số này có {t['hot']} chứng nóng, {t['cold']} lạnh, {t['moist']} ẩm, {t['dry']} khô. "
                f"Nóng {'thắng' if cx['hot_minus_cold'] > 0 else 'thua'} lạnh, ẩm {'thắng' if cx['moist_minus_dry'] > 0 else 'thua'} khô, nên khí chất là {TEMPERAMENT_VI[kind]}. "
                f"Lilly mô tả người thuộc khí chất này là {M['lilly_temperament_manners'][kind]} (tr.539).")
        close = [a for a, v in (("nóng và lạnh", cx["hot_minus_cold"]), ("ẩm và khô", cx["moist_minus_dry"])) if abs(v) <= 1]
        if close:
            head += f" Giữa {listing(close)} chỉ chênh một chứng, nên khí chất này nghiêng nhẹ chứ không rõ nét; Lilly gọi đó là khí chất pha."
    else:
        head = (f"Gộp các chứng nóng, lạnh, ẩm, khô theo cách của Lilly (tr.533) cho kết quả hòa ({t['hot']} nóng, {t['cold']} lạnh, {t['moist']} ẩm, {t['dry']} khô), "
                f"nên lá số không nghiêng hẳn về khí chất nào; Lilly nói các chứng trái nhau thì triệt tiêu nhau.")
    if cx["malefic_mixture"]:
        head += (f" Lilly còn dặn: {planet_list(cx['malefic_mixture'])} chiếu xấu vào cung Mọc hay Mặt Trăng thì luôn pha phần thất thường của chúng vào khí chất, "
                 f"dù các chứng khác có đồng thuận.")
    steps = ["Các chứng đã đếm: " + "; ".join(f"{l['from']} → {'/'.join(l['qualities'])}{' ×' + str(l['weight']) if l['weight'] > 1 else ''}" for l in lines) + ".",
             "Chất của các sao theo bảng tr.533 (đông/tây so với Mặt Trời), Mặt Trăng theo pha, Mặt Trời theo mùa; La Hầu tính như Sao Mộc, Kế Đô như Sao Thổ và Sao Hỏa.",
             OPERATIONAL["partile"]]
    return Para("tq.complexion", "Khí chất theo Lilly", head, "traditional", srcs("LILLY_CA:pp.532-534", "LILLY_CA:p.539"),
                [ev_point(f.c, "asc"), ev_planet(f.c, "moon")], "deep", steps=steps, topic="tong_quan", keys=[f"temperament:{kind}"])


def _balance(f: Facts) -> Para:
    cnt = f.leo_counts()
    el = {k: len(v) for k, v in cnt["element"].items()}
    mo = {k: len(v) for k, v in cnt["modality"].items()}
    top_e = max(el, key=el.get)
    top_m = max(mo, key=mo.get)
    tie_e = [k for k, v in el.items() if v == el[top_e]]
    tie_m = [k for k, v in mo.items() if v == mo[top_m]]
    t = ("Đếm mười hành tinh theo bốn nguyên tố: " + ", ".join(f"{ELEMENT_VI[k]} {v}" for k, v in el.items()) +
         "; theo ba tính chất: " + ", ".join(f"{MODALITY_VI[k]} {v}" for k, v in mo.items()) + ". ")
    if len(tie_e) == 1 and len(tie_m) == 1:
        t += (f"Phép thứ nhất của Alan Leo (The Art of Synthesis) lấy cặp trội nhất làm 'kiểu' của lá số: ở đây là {MODALITY_VI[top_m]}–{ELEMENT_VI[top_e]}, "
              f"rồi đặt nó cạnh cung Mọc để đọc tiếp.")
    else:
        t += "Có nhóm ngang điểm nhau, nên theo Leo phải nhờ vị trí hai sao sáng và cung Mọc để phân xử, không chốt một 'kiểu' duy nhất."
    missing = [ELEMENT_VI[k] for k, v in el.items() if v == 0]
    if missing:
        t += f" Không có hành tinh nào ở nguyên tố {listing(missing)}; đây là một dữ kiện đếm, Leo không cho câu luận riêng cho trường hợp này."
    return Para("tq.balance", "Phân bố nguyên tố và tính chất", t, "modern", srcs("LEO:The Art of Synthesis"),
                [], "deep", tier="src", topic="tong_quan", keys=[f"element_top:{top_e}"])


def _configs(f: Facts) -> Para | None:
    c = f.c
    pats = c.get("patterns", [])
    stell = [s for s in c.get("stelliums", []) if s["by"] == "sign"]
    if not pats and not stell:
        return None
    names = kb.aspects()["patterns"]
    bits = []
    for pt in pats:
        bits.append(f"{names[pt['type']]['vi']} giữa {planet_list(pt['bodies'])}")
    for s in stell:
        bits.append(f"{len(s['bodies'])} hành tinh tụ ở {S(s['where'])} ({planet_list(s['bodies'])})")
    t = ("Về hình học, lá số có " + listing(bits) + ". Đây là những cấu hình do chiêm tinh hiện đại đặt tên; "
         "các sách trong thư viện của Thiên Bàn không cho câu luận riêng cho chúng, nên ở đây chỉ ghi nhận, phần nghĩa đến từ từng góc hợp và từng hành tinh ở các chương sau.")
    return Para("tq.configs", "Các cấu hình nổi bật", t, "calc", srcs("CONV_PATTERNS"), [], "deep", tier="calc", topic="tong_quan")


def overview(f: Facts) -> list[Para]:
    return [p for p in (_sect_paragraph(f), _geniture_paragraph(f), _leo_centres(f), _complexion(f), _balance(f), _configs(f)) if p]


# ======================================================================================================== Tính cách
def _lilly_manners(f: Facts) -> list[Para]:
    ms = f.manners_significator()
    if not ms:
        return []
    c = f.c
    sig = ms["planets"]
    why = {"in_ascending_sign": f"{planet_list(sig)} đứng trong cung Mọc {S(c['angles']['asc']['sign'])}, nên theo Lilly (tr.535) {'nó' if len(sig) == 1 else 'chúng'} là sao chủ tính cách",
           "joined_moon_or_mercury": f"không sao nào đứng trong cung Mọc, nhưng {planet_list(sig)} đi sát Mặt Trăng hoặc Sao Thủy, nên theo thứ tự Lilly đặt ra (tr.536) {'nó' if len(sig) == 1 else 'chúng'} giữ vai sao chủ tính cách",
           "lord_of_ascendant": f"không sao nào đứng trong cung Mọc {S(c['angles']['asc']['sign'])} hay đi sát Mặt Trăng, Sao Thủy, nên theo thứ tự Lilly đặt ra (tr.536) vai sao chủ tính cách thuộc về chủ của cung Mọc là {P(sig[0])}"}[ms["why"]]
    out = []
    for p in sig[:2]:
        portrait_planet = p
        note_lum = ""
        if p in ("sun", "moon"):
            disp = dignity.domicile_lord(f.b[p]["sign"])
            portrait_planet = disp
            note_lum = (f" Lilly không vẽ chân dung riêng cho {P(p)} và dặn rằng chủ tinh của hai sao sáng nói nhiều hơn chính chúng (tr.542); "
                        f"{P(p)} ở {S(f.b[p]['sign'])} nên ta đọc qua {P(disp)}, chủ của cung ấy.")
            if portrait_planet in ("sun", "moon"):
                continue
        state = f.lilly_state(portrait_planet)
        mm = M["lilly_manners"][portrait_planet]
        cond = lilly_condition(f, portrait_planet)
        tot = f.lilly_total(portrait_planet)
        if state == "well":
            core = (f"{P(portrait_planet)} đang {cond}, tức đắc thế theo phẩm vị của Lilly. Khi sao này mạnh, ông mô tả người mang nó là "
                    f"{listing(mm['well'], 5)} ({mm['loc'].replace('p.', 'tr.')}).")
            pol = +1
        elif state == "ill":
            core = (f"{P(portrait_planet)} đang {cond}, tức thất thế theo phẩm vị của Lilly. Với một {P(portrait_planet)} yếu, ông ghi những nét cần để ý là "
                    f"{listing(mm['ill'], 4)} ({mm['loc'].replace('p.', 'tr.')}); bản chất gốc của sao vẫn còn, chỉ là khó phát huy trọn.")
            pol = -1
            if tot["accidental_score"] >= 8:
                core += (f" Tuy vậy, {P(portrait_planet)} lại có nhiều điểm ngẫu nhiên ({tot['accidental_score']:+d}: vị trí, tốc độ, khoảng cách với Mặt Trời), "
                         f"nên những nét tốt của nó ({listing(mm['well'], 3)}) vẫn có chỗ để lộ ra.")
                pol = 0
        else:
            core = (f"{P(portrait_planet)} đang {cond}: phẩm vị ở mức lưng chừng. Vì vậy cả hai bức chân dung của Lilly đều có phần đúng: "
                    f"lúc thuận thì {listing(mm['well'], 3)}, lúc nghịch thì {listing(mm['ill'], 2)}.")
            pol = 0
        disp = dignity.domicile_lord(f.b[portrait_planet]["sign"])
        tail = ""
        if disp != portrait_planet:
            ds = f.lilly_state(disp)
            tail = (f" Lilly bảo xét luôn chủ tinh (dispositor) của sao này (tr.535): {P(disp)} {'đắc thế, nâng sao chủ tính cách lên' if ds == 'well' else 'thất thế, kéo sao chủ tính cách xuống thêm' if ds == 'ill' else 'ở mức lưng chừng, không thêm bớt nhiều'}.")
        mix = ""
        if portrait_planet == "saturn" and (f.platick("saturn", "jupiter") or f.b["saturn"]["sign"] == f.b["jupiter"]["sign"]) and f.lilly_state("jupiter") != "ill":
            mix = " " + M["lilly_manners"]["jupiter_tempers_saturn"]["vi"] + " (tr.542)."
        if portrait_planet in ("saturn", "mars") and f.platick("saturn", "mars"):
            mix += " " + M["lilly_manners"]["mars_with_saturn"]["vi"] + " (tr.542)."
        opening = cap(why) + "." if not out else f"Sao thứ hai cùng giữ vai sao chủ tính cách là {P(p)}."
        text = opening + note_lum + " " + core + tail + mix
        out.append(Para(f"tc.lilly.{p}", "Tính cách theo phép của Lilly", text, "traditional",
                        srcs("LILLY_CA:pp.535-536", f"LILLY_CA:{mm['loc']}", "LILLY_CA:p.104"),
                        [ev_planet(c, p, f.house_lilly(p))] + ([ev_planet(c, portrait_planet, f.house_lilly(portrait_planet))] if portrait_planet != p else []),
                        "overview" if not out else "deep", steps=[OPERATIONAL["well_dignified"],
                        f"Điểm bản chất của {P(portrait_planet)}: {tot['essential']['score']:+d} ({', '.join(tot['essential']['has'] + tot['essential']['debilities']) or 'lạc chỗ'}); điểm ngẫu nhiên {tot['accidental_score']:+d}."],
                        polarity=pol, topic="tinh_cach", keys=[f"manners:{portrait_planet}:{state}"]))
    return out


def _ptolemy_soul(f: Facts) -> Para:
    c = f.c
    sr = f.soul_ruler()
    r = sr["rulers"][0]
    hon = f.honourable(r)
    soul = M["ptolemy_soul"][r]
    claims = ", ".join(sorted(set(sr["claims_mercury"].get(r, []) + sr["claims_moon"].get(r, []))))
    t = (f"Ptolemy tách phần lý trí của tâm hồn (đọc từ Sao Thủy) với phần cảm và bản năng (đọc từ Mặt Trăng), rồi tìm hành tinh 'cai quản' cả hai (III.13). "
         f"Sao Thủy ở {S(f.b['mercury']['sign'])}, Mặt Trăng ở {S(f.b['moon']['sign'])}; hành tinh nắm nhiều quyền nhất trên hai vị trí này là {P(r)}"
         + (f" (cùng {planet_list(sr['rulers'][1:])})" if len(sr["rulers"]) > 1 else "") + ". ")
    if hon:
        t += (f"{P(r)} lại đứng ở chỗ quen thuộc của mình và không bị Mặt Trời che, nên Ptolemy đọc theo vế 'đáng trọng': "
              f"{listing(soul['honourable'], 5)} ({soul['loc'].replace('pp.', 'tr.').replace('p.', 'tr.')}).")
        pol = +1
    else:
        why_not = ("đang nằm dưới tia Mặt Trời" if f.c["conditions"][r].get("solar", {}).get("phase") else
                   f"đang ở {S(f.b[r]['sign'])}, không phải nhà, cung tôn vinh hay tam hợp của nó")
        t += (f"Nhưng {P(r)} {why_not}, nên Ptolemy nghiêng về vế ngược lại: "
              f"{listing(soul['opposite'], 4)}; đó là những nét dễ trượt vào khi sao cai quản yếu, chứ không phải bản án.")
        pol = -1
    mods = []
    ph = c["moon_phase"]
    mods.append(M["ptolemy_soul_mod"]["moon_waxing" if ph["waxing"] else "moon_waning"]["vi"])
    if abs(f.b["moon"]["lat"]) > 4.9:
        mods.append(M["ptolemy_soul_mod"]["moon_limits"]["vi"])
    from ..zodiac import angdiff as _ad
    if min(abs(_ad(f.lon["moon"], f.lon["north_node"])), abs(_ad(f.lon["moon"], f.lon["south_node"]))) < 5:
        mods.append(M["ptolemy_soul_mod"]["moon_nodes"]["vi"])
    t += (f" Mặt Trăng {'đang tròn dần' if ph['waxing'] else 'đang khuyết dần'}, nên theo Ptolemy tính cách có thêm nét {listing(mods)} (tr.361).")
    if f.time_known:
        h = f.place_ptolemy(r)
        if h in (1, 10):
            t += " " + cap(M["ptolemy_soul_mod"]["orient" if h == 1 else "morning_station_or_culminating"]["vi"]) + ": đó là thêm điều Ptolemy nói khi sao cai quản đứng ở phía đông hay ở đỉnh trời (tr.335)."
    steps = [f"Năm cách nắm quyền (III.2) trên Sao Thủy: " + "; ".join(f"{P(k)}: {', '.join(v)}" for k, v in sr["claims_mercury"].items()) + ".",
             f"Trên Mặt Trăng: " + "; ".join(f"{P(k)}: {', '.join(v)}" for k, v in sr["claims_moon"].items()) + ".",
             "Mặt Trời và Mặt Trăng không bao giờ là sao cai quản tâm hồn ở III.13, chỉ là yếu tố điều chỉnh.",
             "'Đáng trọng' (honourable) được Thiên Bàn hiểu là ở nhà, cung tôn vinh hay tam hợp của chính sao đó và không bị Mặt Trời che; Ptolemy không định nghĩa từ này."]
    return Para("tc.ptolemy", "Tâm hồn theo Ptolemy", t, "hellenistic", srcs("PTOL_TETRA:III.13 pp.333-361", "PTOL_TETRA:III.2 p.233"),
                [ev_planet(c, "mercury"), ev_planet(c, "moon"), ev_planet(c, r)], "overview", steps=steps, polarity=pol,
                topic="tinh_cach", keys=[f"soul_ruler:{r}:{'hon' if hon else 'opp'}"])


def _manners_compare(f: Facts, lilly_paras: list[Para], ptol: Para) -> Para | None:
    if not lilly_paras:
        return None
    lk = [k.split(":")[1] for p in lilly_paras for k in p.keys if k.startswith("manners:")]
    pk = [k.split(":")[1] for k in ptol.keys if k.startswith("soul_ruler:")]
    same = set(lk) & set(pk)
    if same:
        s = list(same)[0]
        t = (f"Hai con đường khác nhau cùng dẫn về {P(s)}: Lilly đi từ cung Mọc và chủ của nó, Ptolemy đi từ Sao Thủy và Mặt Trăng. "
             f"Khi hai phép độc lập trùng nhau như vậy, nét tính cách của {P(s)} là điều lá số này nói rõ nhất.")
        if (lilly_paras[0].polarity < 0) != (ptol.polarity < 0):
            t += " Có điều, hai phép đánh giá sức mạnh của sao khác nhau (Lilly dùng bảng điểm, Ptolemy xét chỗ quen thuộc), nên một bên đọc vế thuận, một bên đọc vế nghịch; thực tế thường là cả hai cùng có mặt."
    else:
        t = (f"Lilly và Ptolemy chỉ về hai hành tinh khác nhau ({planet_list(lk)} và {planet_list(pk)}), vì họ bắt đầu từ hai chỗ khác nhau: "
             f"Lilly từ cung Mọc, Ptolemy từ Sao Thủy và Mặt Trăng. Có thể hiểu {planet_list(lk)} là cách bạn hiện ra và hành xử với bên ngoài, "
             f"còn {planet_list(pk)} là cách bạn nghĩ và cảm bên trong; hai lớp này không loại trừ nhau.")
    return Para("tc.compare", "Đối chiếu hai phép", t, "compare", srcs("LILLY_CA:pp.535-536", "PTOL_TETRA:III.13 p.333"), [], "overview",
                tier="src", topic="tinh_cach")


def personality(f: Facts) -> list[Para]:
    lp = _lilly_manners(f)
    pp = _ptolemy_soul(f)
    cmp = _manners_compare(f, lp, pp)
    return [x for x in lp + [pp, cmp] if x]


# ======================================================================================================== Tư duy
def mind(f: Facts) -> list[Para]:
    c = f.c
    out = []
    asp = next((a for a in c["aspects"] if {a["a"], a["b"]} == {"mercury", "moon"} and a["family"] == "major"), None)
    lm = f.platick("mercury", "moon")
    wm, wl = f.lilly_state("mercury"), f.lilly_state("moon")
    good = lm in ("sextile", "trine")
    hard = lm in ("square", "opposition")
    t = "Lilly đọc trí tuệ chủ yếu từ Sao Thủy và mối liên hệ của nó với Mặt Trăng (tr.543). "
    t += f"Sao Thủy đang {lilly_condition(f, 'mercury')}; Mặt Trăng {lilly_condition(f, 'moon')}. "
    if good:
        t += (f"Hai sao chiếu nhau bằng {ASPECT_NOUN[lm]}, góc mà Lilly coi là thuận; " +
              ("cùng với việc cả hai đều đủ mạnh, đó là dấu hiệu Lilly gọi là trí óc rất tốt." if wm != "ill" and wl != "ill"
               else "nhưng một trong hai sao đang yếu, nên cái lợi của góc chiếu bị giới hạn: đầu óc nhanh nhưng cần rèn để bền."))
        pol = +1
    elif hard:
        t += (f"Hai sao chiếu nhau bằng {ASPECT_NOUN[lm]}. Lilly xếp góc vuông và góc đối vào nhóm khiến năng lực tiếp thu kém trơn tru; "
              f"ở người hiện đại có thể hiểu là suy nghĩ và cảm xúc hay giằng co, học tốt nhất khi có phương pháp và thời gian.")
        pol = -1
    else:
        t += ("Hai sao không chiếu nhau trong phạm vi orb của Lilly. Ông coi đây là trường hợp trí tuệ không được hai sao cùng nâng đỡ, "
              "nên sức học dựa nhiều hơn vào riêng Sao Thủy và vào các sao chiếu nó.")
        pol = 0
    out.append(Para("td.lilly", "Trí tuệ theo Lilly", t, "traditional", srcs("LILLY_CA:p.543", "LILLY_CA:p.107"),
                    [ev_planet(c, "mercury", f.house_lilly("mercury")), ev_planet(c, "moon", f.house_lilly("moon"))], "overview",
                    steps=[f"Góc chiếu Sao Thủy–Mặt Trăng trong nửa tổng orb của Lilly (tr.107): {ASPECT_VI.get(lm, 'không có') if lm else 'không có'}.", OPERATIONAL["well_dignified"]],
                    polarity=pol, topic="tu_duy", keys=[f"mind:{'good' if good else 'hard' if hard else 'none'}"]))
    mk = MODALITY[sign_index(f.lon["mercury"])]
    lk = MODALITY[sign_index(f.lon["moon"])]
    cls = lambda m: "solid" if m == "fixed" else "bicorporeal" if m == "mutable" else "solstitial_equinoctial"
    ss = M["sign_soul"]
    t2 = (f"Ptolemy cho rằng loại cung chứa Sao Thủy và Mặt Trăng góp phần lớn vào tâm hồn (III.13, tr.335). Sao Thủy ở {S(f.b['mercury']['sign'])} "
          f"(cung {MODALITY_VI[mk]}): {ss[cls(mk)]}. Mặt Trăng ở {S(f.b['moon']['sign'])} (cung {MODALITY_VI[lk]})"
          + (": cùng loại, nên nét này được nhân đôi." if mk == lk else f": {ss[cls(lk)]}; hai nét này cùng tồn tại, một bên thiên về lý trí, một bên thiên về cảm giác."))
    out.append(Para("td.ptolemy", "Kiểu tâm trí theo Ptolemy", t2, "hellenistic", srcs("PTOL_TETRA:III.13 p.335"),
                    [ev_planet(c, "mercury"), ev_planet(c, "moon")], "deep", topic="tu_duy", keys=[f"mind_signs:{mk}:{lk}"]))
    if f.time_known:
        h3 = [p for p in CLASSICAL if f.place_ws(p) == 3]
        h9 = [p for p in CLASSICAL if f.place_ws(p) == 9]
        if h3 or h9:
            bits = []
            if h9:
                bits.append(f"{planet_list(h9)} ở Nhà 9, nơi Lilly gắn với {M['houses']['9']['lilly']['vi']} và Valens gắn với {M['houses']['9']['valens']['vi']}")
            if h3:
                bits.append(f"{planet_list(h3)} ở Nhà 3, nơi Lilly gắn với {M['houses']['3']['lilly']['vi']}")
            t3 = ("Về chuyện học hành và những gì mở mang đầu óc, " + listing(bits) +
                  f". Sao ở {'Nhà 3 và Nhà 9' if h3 and h9 else 'Nhà 9' if h9 else 'Nhà 3'} không quyết định trí thông minh, nhưng cho biết đầu óc thường được dùng vào đâu.")
            out.append(Para("td.houses", "Học vấn và đi xa", t3, "compare", srcs("LILLY_CA:p.52", "LILLY_CA:p.55", "VALENS_ANTH:IV.12"),
                            [ev_planet(c, p, f.place_ws(p), "Nhà") for p in h3 + h9], "deep", topic="tu_duy"))
    return out


# ======================================================================================================== Cảm xúc
def emotions(f: Facts) -> list[Para]:
    c = f.c
    out = []
    mc = f.moon_contacts()
    sep, app = mc["separated_from"], mc["applies_to"]
    t = ("Ptolemy đọc phần cảm và bản năng của tâm hồn từ Mặt Trăng và từ những sao mà Mặt Trăng vừa rời khỏi và sắp gặp (III.13, tr.333). ")
    if sep:
        t += f"Lúc bạn sinh, Mặt Trăng vừa rời {ASPECT_NOUN[sep['aspect']]} với {P(sep['planet'])} ({num(sep['days'])} ngày trước)"
    if app:
        t += f"{' và' if sep else 'Mặt Trăng'} đang tiến tới {ASPECT_NOUN[app['aspect']]} với {P(app['planet'])} (sau {num(app['days'])} ngày)"
    t += ". "
    nature = lambda p: "cát tinh" if p in ("jupiter", "venus") else "hung tinh" if p in ("mars", "saturn") else "sao trung tính"
    if app:
        pa = app["planet"]
        kind = "hài hòa" if app["aspect"] in ("trine", "sextile") else "căng" if app["aspect"] in ("square", "opposition") else "hợp"
        t += (f"Sao mà Mặt Trăng hướng tới tô màu lên cách cảm xúc vận hành: {P(pa)} là {nature(pa)}, mối liên hệ {kind}, "
              + ("nên phản ứng cảm xúc có xu hướng tìm đến sự dễ chịu và hòa giải." if pa in ("jupiter", "venus") and kind != "căng"
                 else "nên cảm xúc dễ gặp sức cản, cần thời gian để lắng." if pa in ("mars", "saturn")
                 else "nên cảm xúc gắn với lý trí hay với cái tôi nhiều hơn với người khác."))
    out.append(Para("cx.ptolemy", "Mặt Trăng và phần cảm theo Ptolemy", t, "hellenistic", srcs("PTOL_TETRA:III.13 p.333"),
                    [ev_planet(c, "moon")] + ([ev_planet(c, app["planet"])] if app else []), "overview", topic="cam_xuc",
                    steps=["Tìm lần chính xác gần nhất của các góc Ptolemy (0°, 60°, 90°, 120°, 180°) giữa Mặt Trăng và các hành tinh cổ điển, trong khoảng 2,4 ngày trước và sau giờ sinh."],
                    keys=[f"moon_applies:{app['planet'] if app else None}"]))
    moon_sign = f.b["moon"]["sign"]
    st = f.lilly_state("moon")
    mm = M["planets"]["moon"]
    word = 'đắc thế' if st == 'well' else 'thất thế' if st == 'ill' else 'ở mức lưng chừng'
    t2 = (f"Với Lilly, Mặt Trăng {word}" + ("" if described(f, "moon") else f": {lilly_condition(f, 'moon', f.time_known)}") + ". "
          + (f"Mặt Trăng mạnh cho người {listing(mm['lilly_well']['vi'], 4)} (tr.81)." if st != "ill"
             else f"Mặt Trăng yếu, theo ông, dễ khiến người ta {listing(mm['lilly_ill']['vi'], 2)}; ngày nay có thể hiểu đó là những lúc thiếu điểm tựa cảm xúc, cần nề nếp để giữ mình (tr.81)."))
    out.append(Para("cx.lilly", "Mặt Trăng theo Lilly", t2, "traditional", srcs("LILLY_CA:p.81", "LILLY_CA:p.104"), [ev_planet(c, "moon")], "deep",
                    polarity=+1 if st == "well" else -1 if st == "ill" else 0, topic="cam_xuc", keys=[f"moon_state:{st}"]))
    t3 = f"Alan Leo đọc Mặt Trăng ở {S(moon_sign)} là {M['leo_moon'][moon_sign]}."
    ph = c["moon_phase"]["phase"]
    phase_vi = {"new": "trăng non", "waxing_crescent": "trăng lưỡi liềm đầu tháng", "first_quarter": "thượng huyền", "waxing_gibbous": "trăng gần tròn",
                "full": "trăng tròn", "waning_gibbous": "trăng bắt đầu khuyết", "last_quarter": "hạ huyền", "waning_crescent": "trăng lưỡi liềm cuối tháng"}[ph]
    t3 += f" Lúc sinh là {phase_vi}; Leo coi khoảng cách Mặt Trăng–Mặt Trời là một phần của 'nhân cách' (How to Judge a Nativity), nhưng không cho câu luận riêng từng pha."
    out.append(Para("cx.leo", "Mặt Trăng theo Alan Leo", t3, "modern", srcs("LEO:How to Judge a Nativity pp.72-86"), [ev_planet(c, "moon")], "deep",
                    topic="cam_xuc", keys=[f"moon_sign:{moon_sign}"]))
    return out
