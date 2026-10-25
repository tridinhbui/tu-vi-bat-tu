"""Chapters 'Sự nghiệp', 'Tài chính và kinh doanh', 'Quan hệ', 'Gia đình', 'Định hướng cuộc sống'."""
from __future__ import annotations

from .. import dignity, houses as H, kb
from ..zodiac import SIGNS, angdiff, sign_distance, sign_index
from .ch_core import M, lilly_condition
from .compose import Para, cap, ev_house, ev_planet, ev_point, listing, planet_list, srcs
from .facts import BENEFICS, CLASSICAL, FIVE, MALEFICS, OPERATIONAL, Facts
from .vocab import ASPECT_NOUN, ASPECT_VI, P, S, num

SIGN_TYPE = {"anthropomorphic": ("gemini", "virgo", "libra", "sagittarius"), "quadrupedal": ("leo", "sagittarius"),
             "tropical_equinoctial": ("cancer", "capricorn", "aries", "libra"), "terrestrial_aquatic": ("aries", "taurus", "scorpio", "pisces", "cancer", "capricorn")}
GRADE_PLACE = lambda pl: "angular" if pl in (1, 4, 7, 10) else "succedent" if pl in (2, 5, 8, 11) else "cadent"


NEEDS = {"su_nghiep": "Ptolemy tìm chủ hành nghiệp từ Thiên Đỉnh và Lilly xét danh vọng qua Nhà 10, nên chương này cần giờ sinh",
         "tai_chinh": "cả Lot of Fortune của Ptolemy lẫn Nhà 2 của Lilly đều tính từ cung Mọc, nên chương này cần giờ sinh",
         "quan_he": "Lilly và Valens đều đọc hôn nhân qua Nhà 7 và các điểm tính từ cung Mọc, nên chương này cần giờ sinh"}


def _need_time(chapter: str, title: str) -> Para:
    return Para(f"{chapter}.no_time", title, NEEDS[chapter] + ". Khi chưa có giờ sinh, Thiên Bàn để trống thay vì đoán.",
                "calc", [], [], "overview", tier="calc", topic=chapter)


# ======================================================================================================== Sự nghiệp
def career(f: Facts) -> list[Para]:
    if not f.time_known:
        return [_need_time("su_nghiep", "Sự nghiệp")]
    c, out = f.c, []
    la = f.lord_of_action()
    lords, q, tst = la["lords"], la["quality"], la["testimony"]
    why = []
    if la["morning"]:
        why.append(f"{P(la['morning'])} là sao vừa mọc buổi sáng gần Mặt Trời nhất")
    if la["at_mc"]:
        why.append(f"{planet_list(la['at_mc'])} đứng ở chỗ Thiên Đỉnh")
    t = "⟦Ptolemy tìm 'chủ hành nghiệp' (lord of action) từ hai phía: Mặt Trời và Thiên Đỉnh (IV.4).⟧ "
    if la["fallback"]:
        t += (f"Ở lá số này không có sao nào vừa mọc buổi sáng hay đứng ở Thiên Đỉnh, nên ông lấy chủ của cung Thiên Đỉnh, {P(lords[0])}, "
              f"và nói thêm rằng những người như vậy 'phần nhiều ít hoạt động', tức không bị một nghề duy nhất cuốn đi.")
    else:
        t += cap(listing(why)) + f", nên {planet_list(lords)} là chủ hành nghiệp theo Ptolemy. "
    keyset = "+".join(sorted(q, key=["mercury", "venus", "mars"].index))
    acts = M["ptolemy_action"]
    shown = []
    if keyset in acts:
        a = acts[keyset]
        shown.append(f"{P(keyset) if '+' not in keyset else planet_list(keyset.split('+'))} cai quản hành nghiệp thì Ptolemy nói tới lĩnh vực {a['field']} (ví dụ của ông: {listing(a['ex'], 4)})")
    for w in tst:
        k = keyset + "+" + w
        if k in acts:
            shown.append(f"có {P(w)} làm chứng thì nghiêng về {acts[k]['field']} ({listing(acts[k]['ex'], 3)})")
    if keyset == "mars" and f.platick("mars", "sun"):
        shown.append(f"Sao Hỏa chiếu Mặt Trời thì là {acts['mars+sun']['field']}")
    if shown:
        t += " " + cap("; ".join(shown)) + ". Đó là nghề nghiệp của thế kỷ II; điều nên giữ lại là loại năng lực, không phải tên nghề."
    elif q:
        t += " Tổ hợp này Ptolemy có nói tới nhưng Thiên Bàn không dẫn lại vì lời của ông ở đây mang tính phán xét nặng nề."
    sig = q[0] if q else lords[0]
    for typ, ss in SIGN_TYPE.items():
        if f.b[sig]["sign"] in ss:
            t += f" {P(sig)} ở {S(f.b[sig]['sign'])}, loại cung mà Ptolemy gắn với {acts['signs'][typ]['vi']}."
            break
    pl = f.place_ptolemy(sig)
    if pl in (1, 10, 7, 4):
        t += f" Sao này đứng ở góc, nên theo Ptolemy người ta có xu hướng {acts['amplitude']['angular']}."
    elif pl in (3, 6, 9, 12):
        t += f" Sao này ở chỗ suy, nên theo Ptolemy người ta dễ {acts['amplitude']['cadent']}."
    steps = [f"Sao mọc buổi sáng (đi trước Mặt Trời ≥ 15°, gần nhất): {P(la['morning']) if la['morning'] else 'không có'}.",
             f"Sao ở chỗ thứ 10 theo Ptolemy: {planet_list(la['at_mc']) or 'không có'}.", OPERATIONAL["morning_appearance"], OPERATIONAL["ptolemy_place"]]
    out.append(Para("sn.ptolemy", "Chủ hành nghiệp theo Ptolemy", t, "hellenistic", srcs("PTOL_TETRA:IV.4 pp.381-391"),
                    [ev_planet(c, p, f.place_ptolemy(p), "chỗ") for p in lords], "overview", steps=steps, topic="su_nghiep",
                    keys=[f"action:{'+'.join(lords)}"]))
    # Lilly honour
    mc_sign = c["angles"]["mc"]["sign"]
    lord_mc = dignity.domicile_lord(mc_sign)
    in10 = [p for p in CLASSICAL if f.house_lilly(p) == 10]
    sigs = ["sun", lord_mc] + in10
    def grade(p):
        e = f.lilly_essential(p)
        h = f.house_lilly(p)
        g = "high" if set(e["has"]) & {"domicile", "exaltation"} else "mid" if e["has"] else "low"
        a = "angular" if h in (1, 4, 7, 10) else "succedent" if h in (2, 5, 11) else "cadent"
        return g, a
    g_sun, a_sun = grade("sun")
    g_l, a_l = grade(lord_mc)
    word = {"high": "đủ phẩm vị để Lilly hứa danh vọng và chức việc", "mid": "phẩm vị vừa phải, Lilly đọc là mức trung bình", "low": "không có phẩm vị, Lilly đọc là ít danh vọng"}
    t2 = (f"⟦Lilly xét danh vọng và chức vị từ Mặt Trời, chủ của Thiên Đỉnh và các sao đứng ở Nhà 10 (tr.615-617).⟧ Theo Lilly, "
          f"Mặt Trời {word[g_sun]} và đứng ở {'nhà góc' if a_sun == 'angular' else 'nhà kế góc' if a_sun == 'succedent' else 'nhà suy'}; "
          f"Thiên Đỉnh ở {S(mc_sign)}, chủ là {P(lord_mc)}: {word[g_l]}, {'ở nhà góc' if a_l == 'angular' else 'ở nhà kế góc' if a_l == 'succedent' else 'ở nhà suy'}.")
    ben10 = [p for p in in10 if p in BENEFICS]
    mal10 = [p for p in in10 if p in MALEFICS]
    if ben10:
        t2 += f" {planet_list(ben10)} là cát tinh ở Nhà 10; Lilly coi đó là lời hứa thăng tiến."
    if mal10:
        t2 += f" {planet_list(mal10)} là hung tinh ở Nhà 10; Lilly coi đó là sức cản cho đường danh vọng."
    asc_lord = dignity.domicile_lord(c["angles"]["asc"]["sign"])
    if f.house_lilly(asc_lord) == 10:
        t2 += f" Chủ cung Mọc là {P(asc_lord)} lại đứng ở Nhà 10: Lilly nói đó là dấu hiệu có tiếng tốt."
    elif f.house_lilly(lord_mc) == 1:
        t2 += f" Chủ Thiên Đỉnh là {P(lord_mc)} đứng ở Nhà 1: Lilly nói đó là dấu hiệu có tiếng tốt."
    t2 += " ⟦Lilly tự dặn không được kết luận từ một câu cách ngôn riêng lẻ, và cùng một lời hứa thì mỗi người nhận theo hoàn cảnh của mình (tr.617).⟧"
    out.append(Para("sn.lilly", "Danh vọng và chức vị theo Lilly", t2, "traditional", srcs("LILLY_CA:pp.615-617", "LILLY_CA:p.104"),
                    [ev_planet(c, "sun", f.house_lilly("sun")), ev_planet(c, lord_mc, f.house_lilly(lord_mc)), ev_point(c, "mc")], "overview",
                    polarity=+1 if "high" in (g_sun, g_l) and not mal10 else -1 if (g_sun, g_l) == ("low", "low") else 0, topic="su_nghiep",
                    keys=[f"honour:{g_sun}:{g_l}"]))
    lp = f.lilly_profession()
    if lp and lp["significator"]:
        sg = lp["significator"]
        LP = M["lilly_profession"]
        test_vi = {1: "đứng ở Nhà 10, 1 hoặc 7 với phẩm vị của chính nó và không bị Mặt Trời đốt", 2: "làm chủ cung Thiên Đỉnh và có phẩm vị",
                   3: "chiếu Mặt Trăng đúng độ (partile)", 4: "chiếu Mặt Trăng trong phạm vi orb", 5: "mọc trước Mặt Trời"}[lp["test"]]
        t5 = (f"⟦Lilly chọn sao chủ nghề trong ba sao Sao Hỏa, Sao Kim và Sao Thủy, theo năm phép thử lần lượt (tr.624-625).⟧ Ở lá số này {P(sg)} là sao chủ nghề theo Lilly, "
              f"vì nó {test_vi}. ")
        key = "+".join(sorted([sg, lp["partner"]], key=["mercury", "venus", "mars"].index)) if lp["partner"] else sg
        info = LP.get(key) or LP.get(sg)
        if info:
            ex = info.get("ex") or (info.get("ex_well") if lp["fame"] == "strong" else info.get("ex_mean"))
            t5 += (f"{P(sg)}" + (f" kết hợp chặt với {P(lp['partner'])}" if lp["partner"] and key in LP else "") +
                   f" cho {info['field']}; ví dụ của Lilly: {listing(ex, 5)} ({info['loc'].replace('pp.', 'tr.').replace('p.', 'tr.')}). ")
        mod_vi = {"jupiter": "Sao Mộc giúp sức", "saturn": "Sao Thổ gây trở ngại", "sun": "Mặt Trời cho uy tín với người cầm quyền", "moon": "Mặt Trăng cho tín nhiệm với số đông"}
        if lp["modifiers"]:
            t5 += f"Lilly còn nói các sao khác chiếu sao chủ nghề sẽ điều chỉnh nó: ở đây {listing([mod_vi[m] for m in lp['modifiers']])} (tr.626). "
        if not lp["skilled"]:
            t5 += ("Không sao nào trong ba sao đạt hai phép thử đầu (đứng ở góc với phẩm vị của mình, hoặc làm chủ Thiên Đỉnh mà có phẩm vị), nên Lilly cho rằng người ấy khó theo một nghề "
                   "có tay nghề rõ rệt (tr.625); với đời sống hiện nay, điều đó có thể hiểu là con đường nghề nghiệp ít theo khuôn và hay đổi hướng. ")
        t5 += {"strong": f"{P(sg)} có phẩm vị, ở góc và mọc trước Mặt Trời: Lilly đọc là người dễ nổi tiếng trong nghề (tr.631).",
               "weak": f"{P(sg)} yếu hoặc ở nhà suy: Lilly đọc là tay nghề khó được ghi nhận, nên cần chủ động tạo chỗ đứng (tr.631-632).",
               "middle": f"Sức của {P(sg)} ở mức vừa, nên Lilly không hứa danh tiếng lớn mà cũng không coi là trở ngại (tr.631-632)."}[lp["fame"]]
        out.append(Para("sn.lilly_prof", "Nghề nghiệp theo Lilly", t5, "traditional", srcs("LILLY_CA:pp.624-632"),
                        [ev_planet(c, sg, f.house_lilly(sg))], "overview", topic="su_nghiep", keys=[f"profession_lilly:{sg}"],
                        steps=[f"Phép thử đạt: số {lp['test']}; ứng viên: {planet_list(lp['candidates'])}.", OPERATIONAL["partile"]]))
    # Valens 10th place
    p10 = [p for p in CLASSICAL if f.place_ws(p) == 10]
    t3 = (f"Theo Valens, chỗ thứ 10 (tính trọn cung, ở đây là {S(SIGNS[(sign_index(f.lon['asc']) + 9) % 12])}) nói về {M['houses']['10']['valens']['vi']} (IV.12). ")
    if p10:
        t3 += f"{planet_list(p10)} đứng ở đó, nên những việc của chỗ này mang tính chất của {('chúng' if len(p10) > 1 else 'sao ấy')}. "
    lot = c["lots"]["fortune"]["lon"]
    rank_sign = SIGNS[(sign_index(lot) + 9) % 12]
    rr = dignity.domicile_lord(rank_sign)
    g = GRADE_PLACE(f.place_ws(rr))
    t3 += (f"Valens còn coi Lot of Fortune như một cung Mọc thứ hai và gọi chỗ thứ 10 tính từ nó là 'Địa vị' (II.17): ở lá số này đó là {S(rank_sign)}, "
           f"chủ là {P(rr)} đang {'ở góc, dấu hiệu Valens đọc là địa vị vững' if g == 'angular' else 'ở chỗ kế góc, mức vừa' if g == 'succedent' else 'ở chỗ suy, địa vị phải tự gây dựng nhiều hơn'}.")
    out.append(Para("sn.valens", "Nghề nghiệp và địa vị theo Valens", t3, "hellenistic", srcs("VALENS_ANTH:IV.12", "VALENS_ANTH:II.17"),
                    [ev_house(10, "Nhà 10")] + [ev_planet(c, p, 10) for p in p10] + [ev_planet(c, rr, f.place_ws(rr))], "deep", topic="su_nghiep",
                    steps=[f"Lot of Fortune lấy theo quy tắc đang chọn ({c['lots']['rule']}): {c['lots']['fortune']['fmt']} {S(c['lots']['fortune']['sign'])}."]))
    # compare
    lp = set(lords)
    if lord_mc in lp:
        t4 = f"Ptolemy và Lilly gặp nhau ở {P(lord_mc)}: với Ptolemy đó là sao định loại công việc, với Lilly là chủ của Thiên Đỉnh. Hai lớp đọc củng cố nhau."
    else:
        t4 = (f"Ptolemy đọc loại công việc qua {planet_list(lords)}, còn Lilly đọc danh vọng qua chủ Thiên Đỉnh là {P(lord_mc)}. "
              f"Đây là hai câu hỏi khác nhau, làm gì và được ghi nhận ra sao, nên hai câu trả lời khác nhau không mâu thuẫn.")
    out.append(Para("sn.compare", "Đối chiếu", t4, "compare", srcs("PTOL_TETRA:IV.4 p.381", "LILLY_CA:pp.615-617"), [], "deep", topic="su_nghiep"))
    return out


# ======================================================================================================== Tài chính
def money(f: Facts) -> list[Para]:
    if not f.time_known:
        return [_need_time("tai_chinh", "Tài chính")]
    c, out = f.c, []
    fr = f.fortune_ruler_ptolemy()
    lot = fr["lot"]
    r = fr["rulers"][0]
    power = f.honourable(r) or f.place_ptolemy(r) in (1, 10, 7, 4, 11)
    t = (f"⟦Ptolemy xét của cải từ Lot of Fortune, tính theo một công thức cho cả ngày lẫn đêm: lấy khoảng cách từ Mặt Trời đến Mặt Trăng đặt từ cung Mọc (III.10, IV.2).⟧ "
         f"Lot of Fortune theo Ptolemy rơi vào {S(SIGNS[sign_index(lot)])}; hành tinh nắm nhiều quyền nhất trên điểm ấy là {P(r)}. ")
    src_w = M["ptolemy_wealth"].get(r)
    if src_w and power:
        t += f"{P(r)} đang có sức (ở chỗ của mình hoặc ở góc), nên theo Ptolemy của cải dễ đến qua {src_w}."
        pol = +1
    elif src_w:
        t += f"Ptolemy gắn {P(r)} với nguồn lợi từ {src_w}, nhưng sao này đang yếu, nên nguồn ấy khó dồi dào, phải bền bỉ mới thành."
        pol = 0
    else:
        t += "Ptolemy không cho nguồn lợi riêng cho trường hợp này."
        pol = 0
    if {"saturn", "jupiter"} <= set(fr["rulers"]):
        t += " Sao Thổ cùng Sao Mộc nắm Lot: Ptolemy nói tới của thừa kế."
    out.append(Para("tc.ptolemy", "Của cải theo Ptolemy", t, "hellenistic", srcs("PTOL_TETRA:IV.2 pp.373-375", "PTOL_TETRA:III.10 p.275"),
                    [ev_planet(c, r, f.place_ptolemy(r), "chỗ")], "overview", polarity=pol, topic="tai_chinh",
                    steps=[f"Lot (Ptolemy) = ASC + Mặt Trăng − Mặt Trời = {lot:.2f}°.",
                           "Quyền trên điểm Lot: " + "; ".join(f"{P(k)}: {', '.join(v)}" for k, v in fr["claims"].items()) + "."],
                    keys=[f"wealth_ruler:{r}"]))
    cs = f.regio
    sign2 = SIGNS[sign_index(cs[1])] if cs else None
    l2 = dignity.domicile_lord(sign2)
    in2 = [p for p in CLASSICAL if f.house_lilly(p) == 2]
    st2, stj = f.lilly_state(l2), f.lilly_state("jupiter")
    fort = c["lots"]["fortune"]
    lf = dignity.domicile_lord(fort["sign"])
    stf = f.lilly_state(lf)
    good = [x for x, s in ((f"chủ Nhà 2 là {P(l2)}", st2), (f"chủ của Part of Fortune là {P(lf)}", stf), ("Sao Mộc", stj)) if s == "well"]
    weak = [x for x, s in ((f"chủ Nhà 2 là {P(l2)}", st2), (f"chủ của Part of Fortune là {P(lf)}", stf), ("Sao Mộc", stj)) if s == "ill"]
    t2 = (f"⟦Lilly xét tiền bạc qua đỉnh Nhà 2 và chủ của nó, Part of Fortune và chủ của nó, Sao Mộc như sao chủ của cải nói chung, cùng các sao ở Nhà 2 (tr.552).⟧ "
          f"Với Lilly, đỉnh Nhà 2 (Regiomontanus) ở {S(sign2)}. ")
    if good:
        t2 += f"{cap(listing(good))} đắc thế: đó là những chứng thuận cho việc kiếm và giữ tiền. "
    if weak:
        t2 += f"{cap(listing(weak))} thất thế: chứng nghịch, nghĩa là tiền bạc cần kỷ luật và kế hoạch hơn là trông vào vận. "
    mid = [x for x, s_ in ((f"chủ Nhà 2 là {P(l2)}", st2), (f"chủ của Part of Fortune là {P(lf)}", stf), ("Sao Mộc", stj)) if s_ == "mixed"]
    if not good and not weak:
        t2 += "Các sao này đều ở mức lưng chừng, nên Lilly không đưa ra lời hứa mạnh theo chiều nào. "
    elif mid:
        t2 += f"{cap(listing(mid))} ở mức lưng chừng, không thêm không bớt. "
    if in2:
        bn = [p for p in in2 if p in BENEFICS]
        ml = [p for p in in2 if p in MALEFICS]
        t2 += (f"Ở Nhà 2 có {planet_list(in2)}" + (f"; {planet_list(bn)} là cát tinh, thêm một chứng thuận" if bn else "") +
               (f"; {planet_list(ml)} là hung tinh, thêm một chứng cần dè chừng" if ml else "") + ".")
    out.append(Para("tc.lilly", "Tiền bạc theo Lilly", t2.strip(), "traditional", srcs("LILLY_CA:p.552", "LILLY_CA:pp.143-144", "LILLY_CA:p.104"),
                    [ev_house(2, f"Nhà 2: {S(sign2)}"), ev_planet(c, l2, f.house_lilly(l2)), ev_planet(c, lf, f.house_lilly(lf)), ev_planet(c, "jupiter", f.house_lilly("jupiter"))],
                    "overview", polarity=(len(good) - len(weak) > 0) - (len(weak) - len(good) > 0), topic="tai_chinh",
                    steps=[OPERATIONAL["well_dignified"], "Lilly tính đỉnh Nhà 2 từ 5° trước đỉnh; Thiên Bàn dùng đúng đỉnh Regiomontanus và chưa xét cung bị chặn (intercepted)."],
                    keys=[f"money_lilly:{len(good)}:{len(weak)}"]))
    acc_sign = SIGNS[(sign_index(fort["lon"]) + 10) % 12]
    ar = dignity.domicile_lord(acc_sign)
    occ = [p for p in CLASSICAL if f.b[p]["sign"] == acc_sign]
    t3 = (f"Valens gọi chỗ thứ 11 tính từ Lot of Fortune là 'nơi thành tựu', nơi ban của cải và tài sản (II.20). Ở lá số này đó là {S(acc_sign)}, chủ là {P(ar)}"
          + (f"; trong đó có {planet_list(occ)}" if occ else "") + ". "
          + ("Chủ này ở góc hoặc chỗ thuận, nên Valens đọc là của cải có nơi bồi đắp." if GRADE_PLACE(f.place_ws(ar)) != "cadent"
             else "Chủ này ở chỗ suy, nên Valens dặn phải xét thêm Lot of Fortune và chủ của nó để thấy chỗ dựa."))
    out.append(Para("tc.valens", "Nơi thành tựu theo Valens", t3, "hellenistic", srcs("VALENS_ANTH:II.20", "VALENS_ANTH:II.2"),
                    [ev_point(c, "fortune"), ev_planet(c, ar, f.place_ws(ar))], "deep", topic="tai_chinh"))
    merc = f.lilly_state("mercury")
    t4 = (f"Về buôn bán và kinh doanh, cả Ptolemy (IV.2, IV.4) lẫn Lilly (tr.77) đều gắn chúng với Sao Thủy. Sao Thủy ở lá số này "
          + ("đắc thế, một chứng thuận cho đầu óc buôn bán." if merc == "well" else "thất thế, nên việc buôn bán cần dựa vào quy trình chặt chẽ hơn là sự nhanh nhạy." if merc == "ill"
             else "ở mức lưng chừng, không nghiêng hẳn về phía nào."))
    out.append(Para("tc.business", "Kinh doanh", t4, "compare", srcs("PTOL_TETRA:IV.2 p.375", "PTOL_TETRA:IV.4 p.383", "LILLY_CA:p.77"),
                    [ev_planet(c, "mercury", f.house_lilly("mercury"))], "deep", topic="tai_chinh", keys=[f"merc_state:{merc}"]))
    return out


# ======================================================================================================== Quan hệ
def relations(f: Facts) -> list[Para]:
    if not f.time_known:
        return [_need_time("quan_he", "Quan hệ")]
    c, out = f.c, []
    cs = f.regio
    s7 = SIGNS[sign_index(cs[6])]
    l7 = dignity.domicile_lord(s7)
    in7 = [p for p in CLASSICAL if f.house_lilly(p) == 7]
    t = (f"⟦Lilly xét hôn nhân và người phối ngẫu qua Nhà 7 và chủ của nó, rồi các sao trong Nhà 7 (tr.587, tr.600).⟧ Theo Lilly, Nhà 7 ở {S(s7)}, chủ là {P(l7)}, "
         f"đang {lilly_condition(f, l7)}. ")
    t += (f"Lilly lấy dấu hiệu cung Nhà 7 để tả dáng người kia và chủ của nó để tả tính nết (tr.600-602): {P(l7)} {'đắc thế' if f.lilly_state(l7) == 'well' else 'thất thế' if f.lilly_state(l7) == 'ill' else 'ở mức lưng chừng'}. ")
    if in7:
        t += f"Trong Nhà 7 có {planet_list(in7)}, {'cũng là sao' if len(in7) == 1 else 'cũng là những sao'} Lilly bảo phải tính tới."
    gendered = []
    if f.gender in ("male", "female"):
        a, b = (("venus", "moon") if f.gender == "male" else ("sun", "mars"))
        sa, sb = f.lilly_state(a), f.lilly_state(b)
        conc = None
        for x, y in ((a, b), (dignity.domicile_lord(c["angles"]["asc"]["sign"]), l7)):
            if x != y:
                asp = f.platick(x, y)
                if asp in ("sextile", "trine"):
                    conc = (x, y, asp)
                    break
        gendered.append(f"Với lá số {'nam' if f.gender == 'male' else 'nữ'}, Lilly đặt {P(a)} và {P(b)} lên trước (tr.{587 if f.gender == 'male' else 600}): "
                        f"{P(a)} {'đắc thế' if sa == 'well' else 'thất thế' if sa == 'ill' else 'lưng chừng'}, {P(b)} {'đắc thế' if sb == 'well' else 'thất thế' if sb == 'ill' else 'lưng chừng'}.")
        if conc:
            gendered.append(f"{P(conc[0])} và {P(conc[1])} chiếu nhau bằng {ASPECT_NOUN[conc[2]]}: Lilly coi đây là dấu hiệu hòa thuận (tr.602).")
    t += " " + " ".join(gendered)
    if not gendered:
        t += " (Lilly còn dùng hai sao khác nhau cho lá số nam và nữ; khi bạn cho biết giới tính, Thiên Bàn sẽ thêm phần đó.)"
    t += " Những dấu hiệu này nói về khuynh hướng, không đủ để đoán chắc chuyện cưới hỏi."
    out.append(Para("qh.lilly", "Hôn nhân và người phối ngẫu theo Lilly", t, "traditional", srcs("LILLY_CA:p.587", "LILLY_CA:pp.600-602"),
                    [ev_house(7, f"Nhà 7: {S(s7)}"), ev_planet(c, l7, f.house_lilly(l7))] + [ev_planet(c, p, 7) for p in in7], "overview",
                    polarity=+1 if f.lilly_state(l7) == "well" else -1 if f.lilly_state(l7) == "ill" else 0, topic="quan_he", keys=[f"seventh_lord:{l7}"]))
    day = f.is_day
    lot = (f.lon["asc"] + (f.lon["venus"] - f.lon["jupiter"] if day else f.lon["jupiter"] - f.lon["venus"])) % 360
    ls = SIGNS[sign_index(lot)]
    lr = dignity.domicile_lord(ls)
    pl = sign_distance(f.lon["asc"], lot) + 1
    t2 = (f"Valens tính một điểm hôn nhân (Lot of Marriage): {'ban ngày' if day else 'ban đêm'} lấy khoảng cách từ {'Sao Mộc đến Sao Kim' if day else 'Sao Kim đến Sao Mộc'} rồi đặt từ cung Mọc (II.37). "
          f"Ở lá số này điểm ấy ở {S(ls)}, Nhà {pl} tính trọn cung, chủ là {P(lr)} ({'ở góc' if GRADE_PLACE(f.place_ws(lr)) == 'angular' else 'ở chỗ kế góc' if GRADE_PLACE(f.place_ws(lr)) == 'succedent' else 'ở chỗ suy'}). "
          f"Điểm đối diện là Lot of Adultery theo chính Valens; Thiên Bàn không luận điểm đó.")
    out.append(Para("qh.valens", "Điểm hôn nhân theo Valens", t2, "hellenistic", srcs("VALENS_ANTH:II.37"), [ev_planet(c, lr, f.place_ws(lr))], "deep",
                    topic="quan_he", steps=[f"Lot of Marriage = ASC + {'Kim − Mộc' if day else 'Mộc − Kim'} = {lot:.2f}°."]))
    if f.gender in ("male", "female"):
        lum = "moon" if f.gender == "male" else "sun"
        east = f.place_ptolemy(lum) in (10, 11, 12, 4, 5, 6) if lum == "sun" else (c["moon_phase"]["elongation"] % 180) < 90
        t3 = (f"Ptolemy đọc hôn nhân của {'nam' if f.gender == 'male' else 'nữ'} qua {P(lum)} (IV.5). {P(lum)} ở {'phần phía đông' if east else 'phần phía tây'} "
              f"theo cách ông định nghĩa, nên theo ông người ta {'dễ lập gia đình sớm hoặc với người trẻ hơn' if east else 'thường lập gia đình muộn hoặc với người lớn tuổi hơn'}. "
              f"Ông cũng đọc cách yêu từ {'Sao Hỏa' if f.gender == 'male' else 'Sao Kim'}.")
        out.append(Para("qh.ptolemy", "Hôn nhân theo Ptolemy", t3, "hellenistic", srcs("PTOL_TETRA:IV.5 pp.393-397"), [ev_planet(c, lum)], "deep", topic="quan_he"))
    return out


# ======================================================================================================== Gia đình
def family(f: Facts) -> list[Para]:
    c, out = f.c, []
    fa = [p for p in ("sun", "saturn")]
    mo = [p for p in ("moon", "venus")]
    def strength(p):
        return "đáng trọng" if f.honourable(p) else "ở chỗ lạ"
    t = (f"⟦Ptolemy dùng Mặt Trời và Sao Thổ để nói về người cha, Mặt Trăng và Sao Kim để nói về người mẹ (III.4).⟧ Với các sao Ptolemy dùng cho cha mẹ, "
         f"Ở lá số này Mặt Trời {strength('sun')}, Sao Thổ {strength('saturn')}; Mặt Trăng {strength('moon')}, Sao Kim {strength('venus')}. "
         f"Ptolemy dùng các sao này chủ yếu để xét vận của cha mẹ và tuổi thọ của họ; Thiên Bàn không luận các phần ấy, chỉ ghi lại tình trạng sao để bạn đối chiếu.")
    out.append(Para("gd.ptolemy", "Cha mẹ theo Ptolemy", t, "hellenistic", srcs("PTOL_TETRA:III.4 p.241"), [ev_planet(c, p) for p in fa + mo], "deep", topic="gia_dinh"))
    if f.time_known:
        LF = M["lilly_family"]
        day = f.is_day
        rows = []
        for n, who, extra in ((4, "người cha", "sun" if day else "saturn"), (10, "người mẹ", "venus" if day else "moon")):
            sg = SIGNS[sign_index(f.regio[n - 1])]
            l = dignity.domicile_lord(sg)
            inn = [p for p in CLASSICAL if f.house_lilly(p) == n]
            ok = [x for x in dict.fromkeys([l, extra] + inn) if f.lilly_state(x) == "well"]
            bad = [x for x in dict.fromkeys([l, extra] + inn) if f.lilly_state(x) == "ill"]
            who_sig = (f"chủ là {P(l)}, cũng chính là sao Lilly dùng cho {who} khi sinh {'ban ngày' if day else 'ban đêm'}" if l == extra
                       else f"chủ là {P(l)}, thêm {P(extra)} vì bạn sinh {'ban ngày' if day else 'ban đêm'}")
            state = (f"{planet_list(ok)} đắc thế" if ok else "") + (", " if ok and bad else "") + (f"{planet_list(bad)} thất thế" if bad else "")
            rows.append(f"với {who}, ông xét Nhà {n} ở {S(sg)}, {who_sig}" + (f"; trong Nhà {n} có {planet_list(inn)}" if inn else "")
                        + (f" ({state})" if state else ""))
        pat = [x for x in (["sun"] if day else ["saturn", "moon"]) if any(f.platick(x, b) in ("conjunction", "sextile", "trine") for b in BENEFICS)]
        t2 = ("⟦Lilly đọc cha mẹ qua những sao cụ thể (tr.569-570); ông nói khi phần lớn các sao này mạnh và được cát tinh chiếu thì hoàn cảnh của cha mẹ thuận. "
              "Thiên Bàn chỉ dùng điều đó như bức tranh về chỗ dựa gia đình, không luận số phận của cha mẹ.⟧ Theo Lilly, " + "; ".join(rows) + ".")
        if pat:
            t2 += f" {planet_list(pat)} được Sao Mộc hay Sao Kim chiếu tốt: theo Lilly (tr.572-573) gia sản có nền và người sinh làm nó tăng thêm."
        s3 = SIGNS[sign_index(f.regio[2])]
        l3 = dignity.domicile_lord(s3)
        t2 += f" Về anh chị em, Lilly xét {LF['brethren']['vi']} (tr.564-565): Nhà 3 ở {S(s3)}, chủ là {P(l3)} {'đắc thế' if f.lilly_state(l3) == 'well' else 'thất thế' if f.lilly_state(l3) == 'ill' else 'ở mức lưng chừng'}."
        out.append(Para("gd.lilly", "Gia đình theo Lilly", t2, "traditional", srcs("LILLY_CA:pp.564-573", "LILLY_CA:p.104"),
                        [ev_house(4, "Nhà 4"), ev_house(10, "Nhà 10"), ev_house(3, "Nhà 3")], "overview", topic="gia_dinh"))
    return out


# ======================================================================================================== Định hướng
def direction(f: Facts) -> list[Para]:
    c, out = f.c, []
    if f.time_known:
        asc = c["angles"]["asc"]["sign"]
        lord = dignity.domicile_lord(asc)
        h = f.house_lilly(lord)
        ruler_ok = f.lilly_state(lord) == "well" or h in (1, 10, 7, 9, 11)
        lg = f.lord_of_geniture
        strongest = lg["lords"][0] if lg else lord
        if ruler_ok:
            t = (f"⟦Alan Leo phân biệt chủ cung Mọc với 'hành tinh cai quản' lá số: chủ cung Mọc là hành tinh cai quản khi nó có phẩm vị, đứng ở góc, ở Nhà 9, 11 hay ở trên cao (The Art of Synthesis).⟧ "
                 f"Chủ của {S(asc)} là {P(lord)}, đang ở Nhà {h}" + (" và đắc thế" if f.lilly_state(lord) == "well" else "") +
                 f", nên với Leo nó giữ vai trò dẫn dắt cả đời người.")
            ruler = lord
        else:
            t = (f"Alan Leo phân biệt chủ cung Mọc với 'hành tinh cai quản' lá số. Chủ của {S(asc)} là {P(lord)} nhưng không đủ điều kiện Leo đặt ra (có phẩm vị, ở góc hay ở cao), "
                 f"nên theo ông một hành tinh mạnh hơn có thể giành vai này; ở đây {P(strongest)} là sao mạnh nhất theo bảng điểm cổ điển.")
            ruler = strongest
        t += f" Mặt Trời ở {S(f.b['sun']['sign'])} vẫn là phần cá tính bền nhất: {M['leo_sun'][f.b['sun']['sign']]}."
        out.append(Para("dh.leo", "Hành tinh dẫn dắt theo Alan Leo", t, "modern", srcs("LEO:The Art of Synthesis", "LEO:How to Judge a Nativity"),
                        [ev_planet(c, ruler), ev_planet(c, "sun")], "overview", topic="dinh_huong", keys=[f"ruler:{ruler}"]))
        fort, spirit = c["lots"]["fortune"], c["lots"]["spirit"]
        fr, sr = dignity.domicile_lord(fort["sign"]), dignity.domicile_lord(spirit["sign"])
        t2 = (f"⟦Valens đặt hai điểm cạnh nhau: Lot of Fortune nói về thân thể và việc của đôi tay, Lot of Daimon (Spirit) nói về tâm trí, dự định và việc cho nhận (II.19).⟧ "
              f"Theo Valens, Fortune ở {S(fort['sign'])} (Nhà {fort['house_ws']} tính trọn cung, chủ {P(fr)}); Daimon ở {S(spirit['sign'])} (Nhà {spirit['house_ws']}, chủ {P(sr)}). ")
        if dignity.domicile_lord(spirit["sign"]) and f.b[sr]["sign"] in (fort["sign"], SIGNS[(sign_index(fort["lon"]) + 9) % 12]):
            where = "ngay ở cung của Fortune" if f.b[sr]["sign"] == fort["sign"] else f"ở chỗ thứ 10 tính từ Fortune ({S(f.b[sr]['sign'])})"
            t2 += f"Chủ của Daimon là {P(sr)} đứng {where}: Valens coi đây là trường hợp tốt nhất, khi điều mình định làm và cái mình gặt được đi cùng một hướng."
        else:
            t2 += "Hai điểm này không nối với nhau theo kiểu Valens khen nhất, nên điều mình muốn và điều đời mang tới có thể đi hai đường; biết điều đó giúp chọn việc cho đúng sức."
        out.append(Para("dh.valens", "Fortune và Daimon theo Valens", t2, "hellenistic", srcs("VALENS_ANTH:II.19"),
                        [ev_point(c, "fortune"), ev_point(c, "spirit")], "deep", topic="dinh_huong",
                        steps=[f"Quy tắc Lot đang dùng: {c['lots']['rule']}. Valens tự đảo công thức ban đêm khi Mặt Trăng còn trên chân trời (III.14)."]))
    else:
        out.append(Para("dh.leo", "Hành tinh dẫn dắt theo Alan Leo",
                        f"Không có giờ sinh nên không xác định được cung Mọc và chủ của nó. Theo Leo, Mặt Trời là trung tâm quan trọng nhất: ở {S(f.b['sun']['sign'])}, {M['leo_sun'][f.b['sun']['sign']]}.",
                        "modern", srcs("LEO:Astrology for All"), [ev_planet(c, "sun")], "overview", topic="dinh_huong"))
    return out
