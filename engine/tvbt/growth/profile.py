"""Growth profile: life lessons, blind spots, life compass per domain, current-stage lens and the practice list, built from chart signals.

House rules (each is tested):
  1. every insight names the chart anchors it rests on (signal ids that are verifiably true of this chart);
  2. the three layers are separate fields; `bieu_tuong.source` says whether the symbol is from a book page ('sach'), common tradition
     ('pho_thong') or this system ('he_thong'); `tam_ly` always carries a named concept and the note that the chart does not prove it;
  3. every insight has reflection questions, a real-life situation and a practice of 7–30 days;
  4. no prediction and no decision is made for the reader (language guard in text.lint).
"""
from __future__ import annotations

from . import kb
from .signals import Signals, action_level, groups_of
from .text import slug

VERSION = "growth-0.1"
PSY_NOTE = "Giả thuyết để bạn tự kiểm chứng bằng trải nghiệm; lá số không chứng minh khái niệm này và khái niệm này không chứng minh lá số."
SRC = {"sach": "theo sách", "pho_thong": "cách hiểu phổ thông của truyền thống, không trích trang sách", "he_thong": "cách đọc do hệ thống đặt ra"}
HOA_CONCEPT = {"Hóa Lộc": "hedonic_adaptation", "Hóa Quyền": "uncertainty_control", "Hóa Khoa": "contingent_self_worth", "Hóa Kỵ": "rumination"}
GROUP_CONCEPT = {"tu_phu_vu_tuong": "reversibility", "sat_pha_liem_tham": "emotion_regulation", "co_nguyet_dong_luong": "implementation_intention",
                 "cu_nhat_nguyet": "hostile_attribution"}


def _area(palace: str) -> str:
    return kb.load("palaces")["growth_area"][palace]["area"]


def _domain(palace: str) -> str:
    return kb.load("palaces")["growth_area"][palace]["domain"]


def _symbol(text: str, source: str, cites: list[str] | None = None) -> dict:
    return {"text": text, "source": source, "source_label": SRC[source], "cites": cites or []}


def _psych(cid: str, text: str | None = None) -> dict:
    c = kb.concept(cid)
    return {"text": text or c["gist"], "concept": c, "note": PSY_NOTE}


def _ins(iid, kind, title, anchors, symbol, psych, life, questions, scenario, practices, domains, priority, **extra) -> dict:
    return {"id": iid, "kind": kind, "title": title, "anchors": anchors, "priority": priority, "domains": sorted(set(domains)),
            "layers": {"bieu_tuong": symbol, "tam_ly": psych, "doi_song": {"text": life}},
            "exercise": {"questions": questions, "scenario": scenario, "practices": practices}, **extra}


def _star_symbol(star: str, palace: dict | None, ref_text: str) -> dict:
    prof = kb.book("star_profiles")["stars"].get(star, {})
    dig = palace["major_dignity"].get(star) if palace else None
    t = f"{star}: {prof.get('dau', '')}, chủ {prof.get('domain', '')} ({prof.get('element', '')}). {ref_text}"
    if dig:
        t += f" Độ sáng tại cung này theo bảng Thực Hành: {dig}."
    return _symbol(t, "sach", [prof.get("locator", "TH pp.29-48")] + (["TH pp.29-48 (bảng độ sáng)"] if dig else []))


def _star_domains(sg: Signals, star: str) -> list[str]:
    ds = ["self"]
    for d, cfg in kb.load("concepts")["domains"].items():
        if any(star in sg.ps[p]["major_stars"] for p in cfg["palaces"]):
            ds.append(d)
    return ds


# --------------------------------------------------------------------------------------------------------------- lessons
def lessons(sg: Signals) -> list[dict]:
    S, P, out = kb.stars(), kb.load("palaces"), []
    anchor_menh = ["menh.vcd" if sg.vcd else "menh.stars"]
    if sg.vcd:
        v = P["vcd"]
        out.append(_ins("L_MENH_VCD", "lesson", v["lesson_title"], anchor_menh,
                        _symbol("Cung Mệnh vô chính diệu; truyền thống đọc bằng cách mượn chính tinh cung đối diện.", "pho_thong"),
                        _psych("values_clarification"), v["lesson"].format(borrowed=", ".join(sg.borrowed) or "cũng vô chính diệu"),
                        [v["question"], "Lần gần nhất bạn đổi môi trường, điều gì trong bạn vẫn giữ nguyên?"], v["scenario"], [v["practice"]],
                        ["self", "career"], 100, skill=v["skill"]))
    for i, star in enumerate(sg.menh_stars):
        d = S[star]
        where = sg.menh if not sg.vcd else None
        ref = "Sao này " + ("ở cung Mệnh." if not sg.vcd else "được mượn từ cung đối diện vì Mệnh vô chính diệu.")
        life = f"Thế mạnh theo hình tượng: {d['gift']}. {d['lesson']['text']}"
        if where and where["major_dignity"].get(star) == "hãm":
            life += " " + d["ham_note"]
        out.append(_ins(f"L_STAR_{slug(star).upper()}", "lesson", d["lesson"]["title"], anchor_menh, _star_symbol(star, where, ref),
                        _psych(d["psych"]["concept"], d["psych"]["text"]), life, d["questions"], d["scenario"], d["practices"],
                        _star_domains(sg, star), 95 - i, skill=d["skill"], star=star, gift=d["gift"]))
    gs = groups_of(sg.menh_stars)
    for g in gs:
        gd = P["groups"][g]
        out.append(_ins(f"L_GROUP_{g.upper()}", "lesson", f"Cung Mệnh thuộc {gd['kl']}", anchor_menh,
                        _symbol(f"Khảo Luận chia chính tinh thành bốn nhóm; {gd['label']} là {gd['kl']}.", "sach", ["Khảo Luận pp.50-51"]),
                        _psych(GROUP_CONCEPT[g]), gd["lesson"], [gd["question"], "Bạn ra quyết định tốt nhất khi nào: lúc đã nghĩ kỹ, hay lúc bắt tay vào làm?"],
                        P["action_gap_scenario"], [P["action_gap_practice"]], ["self", "career"], 80))
    adv = kb.book("tu_hoa_vi")["by_stem"][str(sg.year_stem)]
    pos, caution = adv[:3], adv[3]
    from ..ganzhi import STEMS_VI
    stem = STEMS_VI[sg.year_stem]
    out.append(_ins("L_YEAR_STEM_ADVICE", "lesson", f"Năng lực sách gợi ý cho người tuổi {stem}", ["year.stem"],
                    _symbol(f"Khảo Luận, khi bàn về Tứ Hóa theo can năm {stem}: " + "; ".join(f"{a['star']}: {a['advice']}" for a in pos) +
                            f". Lời nhắc: {caution['star']}: {caution['advice']}.", "sach", ["Khảo Luận pp.195-197"]),
                    _psych("growth_mindset", "Sách nói 'làm được như thế thì có…'. Tâm lý học về tư duy phát triển đọc tương tự: phẩm chất là thứ rèn được qua luyện tập, không phải thứ có sẵn hay không."),
                    "Ba năng lực nên rèn: " + "; ".join(a["advice"].split(" thì ")[0] for a in pos) + f". Điều cần tránh: {caution['advice'].split(' thì ')[0]}.",
                    [f"Trong ba năng lực trên, năng lực nào bạn đã có và năng lực nào bạn còn né?", f"Bạn đã từng rơi vào điều sách nhắc ('{caution['advice'].split(' thì ')[0]}') chưa? Trong hoàn cảnh nào?"],
                    {"situation": "Bạn sắp bước vào một việc mới (dự án, công việc, mối quan hệ).", "try": f"Chọn một trong ba năng lực trên và viết ra một hành vi cụ thể thể hiện nó trong tuần đầu tiên."},
                    [{"days": 30, "action": "Mỗi tuần chọn một năng lực trong ba năng lực trên và thực hành có chủ đích ở một tình huống cụ thể.", "track": "Ghi tình huống, hành vi đã làm, và phản hồi nhận được."}],
                    ["self", "career", "money"], 75))
    for h, prio in (("Hóa Kỵ", 85), ("Hóa Khoa", 60)):
        x = sg.hoa.get(h)
        if not x:
            continue
        hd, area = P["hoa"][h], _area(x["palace"])
        meaning = kb.book("tu_hoa_vi")["meaning"][h]
        note = kb.book("tu_hoa_vi")["position_notes"].get(h, "")
        out.append(_ins(f"L_HOA_{slug(h).upper()}", "lesson", f"{h} tại {x['palace']}: {hd['theme']}", [f"hoa.{h}"],
                        _symbol(f"{h} chủ {meaning}; {note}.", "sach", ["Khảo Luận pp.195-197"]), _psych(HOA_CONCEPT[h]),
                        hd["lesson"].format(area=area), [hd["question"].format(area=area), kb.load("concepts")["domain_questions"][_domain(x["palace"])][0]],
                        {k: v.format(area=area) for k, v in hd["scenario"].items()}, [{**hd["practice"], "action": hd["practice"]["action"].format(area=area)}],
                        [_domain(x["palace"])], prio, palace=x["palace"]))
    if sg.than["name"] != "Mệnh":
        area = _area(sg.than["name"])
        out.append(_ins("L_THAN", "lesson", f"Thân cư {sg.than['name']}: nơi đời sống dần đặt trọng tâm", ["than.palace"],
                        _symbol("Cung Thân được đọc như phần hậu thiên, nơi đời sống dần dồn trọng tâm về sau.", "pho_thong"),
                        _psych("growth_mindset"), P["than_lesson"].format(palace=sg.than["name"], area=area),
                        [f"Nhìn lại mười năm qua, {area} đã chiếm bao nhiêu phần tâm trí bạn so với trước?", "Bạn muốn lĩnh vực này trưởng thành theo hướng nào trong năm năm tới?"],
                        {"situation": f"Một lựa chọn ở {area} đến cùng lúc với một lựa chọn ở lĩnh vực khác.", "try": "Hỏi: lựa chọn nào phục vụ con người bạn muốn trở thành trong mười năm tới?"},
                        [{"days": 30, "action": f"Mỗi tuần dành một giờ có chủ đích cho {area}: học, trò chuyện hoặc sắp xếp lại.", "track": "Ghi điều bạn hiểu thêm về mình qua lĩnh vực này."}],
                        [_domain(sg.than["name"])], 55, palace=sg.than["name"]))
    b, B = sg.bazi, kb.load("bazi")
    st = B["stems"][b["dm"]]
    out.append(_ins(f"L_DM_{slug(b['dm']).upper()}", "lesson", f"Nhật Chủ {b['dm']}: hình ảnh {st['image']}", ["bazi.dm"],
                    _symbol(f"Thập Can {b['dm']} ({b['dm_element']}) thường được ví với {st['image']}.", "pho_thong"),
                    _psych("barnum", "Hình ảnh Thập Can là ẩn dụ, không có khái niệm tâm lý học tương ứng trực tiếp. Giá trị của ẩn dụ nằm ở việc bạn đối chiếu nó với hành vi cụ thể của mình, không phải ở cảm giác 'nghe đúng quá'."),
                    f"Thế mạnh theo hình ảnh: {st['gift']}. {st['lesson']}", [st["question"], f"Khi nào bạn thấy mình {st['shadow']}?"],
                    {"situation": f"Bạn nhận ra mình đang {st['shadow']}.", "try": f"Nhớ lại hình ảnh {st['image']} và hỏi: phiên bản trưởng thành của hình ảnh này sẽ làm gì lúc này?"},
                    [st["practice"]], ["self"], 70))
    if b.get("yong"):
        lab = B["groups"]
        if len(b["yong"]) >= 2:
            a, c = ("/".join(lab[g]["resource"] for g in b["yong"][0]), "/".join(lab[g]["resource"] for g in b["yong"][1]))
            txt = B["yong_two"].format(a=a, b=c)
        else:
            gs2 = b["yong"][0]
            txt = B["yong_lesson"].format(groups=", ".join(lab[g]["label"] for g in gs2), resources="; ".join(lab[g]["resource"] for g in gs2))
        res = [lab[g]["resource"] for y in b["yong"] for g in y]
        out.append(_ins("L_BAZI_YONG", "lesson", "Nguồn lực giúp bạn cân bằng (Bát Tự)", ["bazi.yong", "bazi.strength"],
                        _symbol("Phép phù ức: Nhật Chủ nhược thì bồi, vượng thì tiết; hệ thống chạy mọi cách đọc và không chọn khi ở vùng biên.", "he_thong"),
                        _psych("self_compassion", "Chăm sóc nguồn lực trước khi cạn (nghỉ ngơi, học hỏi, người đồng hành) là điều tâm lý học về phục hồi nhấn mạnh; ở đây nó được đặt cạnh khái niệm dụng thần như một ẩn dụ."),
                        txt, ["Gần đây, lúc bạn thấy vững vàng nhất, bạn đang có những nguồn lực nào quanh mình?", "Nguồn lực nào trong số này bạn đang bỏ bê?"],
                        {"situation": "Một tuần quá tải, bạn thấy hụt sức.", "try": f"Chọn một nguồn lực ({res[0]}) và dành cho nó 30 phút trước khi làm thêm bất cứ việc gì."},
                        [{"days": 14, "action": f"Mỗi ngày làm một việc nhỏ bồi đắp nguồn lực: {res[0]}.", "track": "Ghi mức năng lượng buổi tối (1–5) và so ngày có làm với ngày không làm."}],
                        ["self", "career", "money"], 50))
    return sorted(out, key=lambda x: -x["priority"])


# ----------------------------------------------------------------------------------------------------------- blind spots
def blind_spots(sg: Signals) -> list[dict]:
    S, P, B, out = kb.stars(), kb.load("palaces"), kb.load("bazi"), []
    anchor_menh = ["menh.vcd" if sg.vcd else "menh.stars"]
    for i, star in enumerate(sg.menh_stars):
        d, sh = S[star], S[star]["shadow"]
        out.append(_ins(f"B_STAR_{slug(star).upper()}", "blind_spot", f"Mâu thuẫn nội tâm theo hình tượng {star}", anchor_menh,
                        _star_symbol(star, sg.menh if not sg.vcd else None, f"Nhu cầu cốt lõi theo hình tượng: {d['need']}."),
                        _psych(d["psych"]["concept"], d["psych"]["text"]),
                        f"Thói quen tự cản trở có thể gặp: {sh['habit']}. Cách điều chỉnh: {sh['adjust']}",
                        d["questions"][1:] + d["questions"][:1], d["scenario"], d["practices"][:1], _star_domains(sg, star), 95 - i,
                        star=star, shadow={"conflict": sh["conflict"], "habit": sh["habit"], "signals": sh["signals"], "adjust": sh["adjust"]},
                        signal_words=d["signal_words"]))
    if len(sg.menh_stars) >= 2:
        a, c = sg.menh_stars[:2]
        shared = set(groups_of([a])) & set(groups_of([c]))
        if shared:
            txt = (f"{a} và {c} cùng nhóm nên cùng hướng: điểm mạnh được nhân đôi, và điểm mù cũng vậy. "
                   f"Hai thói quen cần để ý cùng lúc: {S[a]['shadow']['habit'].split(',')[0]}; {S[c]['shadow']['habit'].split(',')[0]}.")
        else:
            txt = (f"Hai nhu cầu có thể kéo hai hướng: lúc muốn {S[a]['need']}, lúc muốn {S[c]['need']}. Dấu hiệu: bạn đổi qua lại giữa hai trạng thái và tự hỏi đâu mới là mình. "
                   "Cả hai đều là bạn; việc cần làm là nhận ra tình huống nào kích hoạt phía nào.")
        out.append(_ins(f"B_PAIR_{slug(a).upper()}_{slug(c).upper()}", "blind_spot", f"Hai nhu cầu trong cùng cung Mệnh: {a} và {c}", anchor_menh,
                        _symbol(f"Cung Mệnh {'mượn' if sg.vcd else 'có'} hai chính tinh {a} và {c}.", "he_thong"), _psych("values_clarification"),
                        txt, [f"Trong tuần qua, lúc nào phía '{S[a]['need']}' dẫn dắt bạn, lúc nào phía '{S[c]['need']}'?", "Khi hai phía xung đột, bạn thường để phía nào thắng, và có hài lòng với điều đó không?"],
                        {"situation": "Một quyết định khiến bạn giằng co giữa hai mong muốn.", "try": f"Viết riêng điều phía {a} muốn và điều phía {c} muốn; tìm một bước đáp ứng một phần cả hai."},
                        [{"days": 14, "action": f"Mỗi tối ghi: hôm nay phía {a} hay phía {c} dẫn dắt mình, trong tình huống nào.", "track": "Sau 14 ngày, tìm quy luật: tình huống nào kích hoạt phía nào."}],
                        ["self", "love", "career"], 88))
    la = action_level(sg.menh_stars)
    for key, pal, prio in (("than", sg.than, 82), ("phuc", sg.ps["Phúc Đức"], 78)):
        if pal["name"] == "Mệnh" or la is None or (key == "phuc" and sg.than["name"] == "Phúc Đức"):   # Thân cư Phúc Đức: told once, as Thân
            continue
        lb = action_level(pal["major_stars"])
        if lb is None or abs(lb - la) < 1.0:
            continue
        g1, g2 = groups_of(sg.menh_stars)[0], groups_of(pal["major_stars"])[0]
        conflict = P["action_gap_conflict"][f"{key}_{'more' if lb > la else 'less'}_action"]
        txt = P["action_gap"].format(g1=P["groups"][g1]["kl"], p2=pal["name"], g2=P["groups"][g2]["kl"], d1=_desc(la), d2=_desc(lb), conflict=conflict)
        out.append(_ins(f"B_GAP_{key.upper()}", "blind_spot", f"Bên ngoài và bên trong đi hai nhịp (Mệnh ↔ {pal['name']})", anchor_menh + [f"{'than.palace' if key == 'than' else 'phuc.stars'}"],
                        _symbol("Khảo Luận chia chính tinh thành nhóm thiên về hành động và nhóm thiên về lý luận; ở đây hai cung thuộc hai nhóm cách xa nhau.", "sach", ["Khảo Luận pp.50-51"]),
                        _psych("emotion_regulation" if lb > la else "rumination"), txt,
                        ["Có lúc nào bạn bất ngờ với chính phản ứng của mình, như thể đó là một người khác?", "Phía nào trong bạn đang ít được lắng nghe?"],
                        P["action_gap_scenario"], [P["action_gap_practice"]], ["self"], prio))
    lo, ky = sg.hoa.get("Hóa Lộc"), sg.hoa.get("Hóa Kỵ")
    same = bool(lo and ky and lo["palace"] == ky["palace"])
    for h, prio in (("Hóa Kỵ", 84), ("Hóa Quyền", 58), ("Hóa Lộc", 52)):
        x = sg.hoa.get(h)
        if not x or (same and h == "Hóa Lộc"):
            continue
        hd, area = P["hoa"][h], _area(x["palace"])
        out.append(_ins(f"B_HOA_{slug(h).upper()}", "blind_spot", f"{h} tại {x['palace']}: điểm dễ không nhận ra", [f"hoa.{h}"],
                        _symbol(f"{h} chủ {kb.book('tu_hoa_vi')['meaning'][h]}.", "sach", ["Khảo Luận pp.195-197"]), _psych(HOA_CONCEPT[h]),
                        hd["blind"].format(area=area), [hd["question"].format(area=area), kb.load("concepts")["domain_questions"][_domain(x["palace"])][1]],
                        {k: v.format(area=area) for k, v in hd["scenario"].items()}, [{**hd["practice"], "action": hd["practice"]["action"].format(area=area)}],
                        [_domain(x["palace"])], prio, palace=x["palace"]))
    if same:
        area = _area(lo["palace"])
        out.append(_ins("B_LOC_KY_SAME", "blind_spot", f"Lộc và Kỵ cùng ở {lo['palace']}", ["hoa.Hóa Lộc", "hoa.Hóa Kỵ"],
                        _symbol("Hóa Lộc chủ sự dễ chịu về vật chất, Hóa Kỵ gây điều không êm ở cung nó đóng; ở đây cả hai cùng một cung.", "sach", ["Khảo Luận pp.195-197"]),
                        _psych("rumination"), P["loc_ky_same"].format(palace=lo["palace"], area=area),
                        [f"Ở {area}, điều gì cho bạn năng lượng và điều gì lấy đi năng lượng?", "Kỳ vọng nào của bạn ở lĩnh vực này cần được nói ra hoặc điều chỉnh?"],
                        {"situation": f"Một chuyện ở {area} vừa làm bạn vui vừa làm bạn lo.", "try": "Viết hai cột: phần cho năng lượng, phần lấy năng lượng; chọn một việc nhỏ ở cột thứ hai để xử lý."},
                        [{"days": 14, "action": f"Mỗi ngày ghi một điều tích cực và một điều vướng ở {area}.", "track": "Sau 14 ngày, xem điều vướng nào lặp lại."}],
                        [_domain(lo["palace"])], 86, palace=lo["palace"]))
    if "menh.tuan_triet" in sg.anchors:
        tt = sg.anchors["menh.tuan_triet"]["check"]["flags"]
        out.append(_ins("B_MENH_TUAN_TRIET", "blind_spot", "Cảm giác 'bị chặn' ở giai đoạn đầu", ["menh.tuan_triet"],
                        _symbol(P["tuan_triet_menh"].format(tt=" và ".join(tt)), "pho_thong", ["data/deep/conflict_matrix.json R07"]),
                        _psych("growth_mindset"), "Điểm mù có thể gặp: diễn giải mọi trở ngại như bằng chứng rằng mình 'không có số', và bỏ cuộc sớm. Điều chỉnh: ghi lại lần bạn đã đi vòng qua một trở ngại thành công.",
                        ["Trở ngại nào bạn đã vượt qua bằng cách đi vòng thay vì đâm thẳng?", "Khi bị chặn, câu chuyện bạn tự kể về mình là gì?"],
                        {"situation": "Một kế hoạch bị trì hoãn vì lý do ngoài tầm tay.", "try": "Liệt kê ba con đường khác dẫn đến cùng mục tiêu, kể cả những con đường chậm hơn."},
                        [{"days": 30, "action": "Mỗi tuần ghi một trở ngại và cách bạn đã đi vòng qua nó (dù nhỏ).", "track": "Sau 30 ngày, đọc lại danh sách như bằng chứng về sức bền của bạn."}],
                        ["self"], 60))
    mc = next((v for k, v in P["menh_cuc"].items() if sg.menh_cuc.startswith(k)), None)
    if mc:
        out.append(_ins("B_MENH_CUC", "blind_spot", "Nhịp giữa bản thân và hoàn cảnh (Mệnh – Cục)", ["menh.cuc"],
                        _symbol(f"Quan hệ ngũ hành giữa Mệnh và Cục: {sg.menh_cuc}.", "pho_thong"), _psych("dichotomy_control"), mc,
                        ["Trong hoàn cảnh hiện tại, bạn đang nhận nhiều hơn hay cho đi nhiều hơn?", "Áp lực nào bạn đang cố đáp ứng mà thực ra chỉ cần chấp nhận?"],
                        {"situation": "Hoàn cảnh (công việc, gia đình) đòi hỏi bạn nhiều hơn thường lệ.", "try": "Chia các đòi hỏi thành ba nhóm: cần đáp ứng, có thể thương lượng, chỉ cần chấp nhận."},
                        [{"days": 7, "action": "Mỗi ngày nhận diện một đòi hỏi của hoàn cảnh và xếp nó vào một trong ba nhóm trên.", "track": "Cuối tuần xem nhóm nào nhiều nhất."}],
                        ["self"], 40))
    b = sg.bazi
    if b.get("level"):
        sd = B["strength"][b["level"]]
        heavy = ", ".join(B["groups"][g]["label"] for g in b.get("heavy") or []) or "các nhóm tiêu hao"
        txt = sd["blind"].format(heavy=heavy)
        if b.get("ambiguous"):
            txt += " Lưu ý: khí thế ở vùng biên nên có hai cách đọc; hãy coi đây là câu hỏi để tự kiểm chứng, không phải kết luận."
        out.append(_ins("B_BAZI_STRENGTH", "blind_spot", sd["title"], ["bazi.strength"],
                        _symbol(f"Bát Tự: khí thế Nhật Chủ {b['level_raw'] or b['level']} (quy tắc nháp).", "he_thong"),
                        _psych("boundaries" if b["level"] == "nhược" else "emotion_regulation"), txt,
                        ["Tuần qua bạn đã nhận thêm bao nhiêu việc so với sức mình?" if b["level"] == "nhược" else "Năng lượng của bạn tuần qua đã đi vào đâu?", "Điều gì giúp bạn hồi sức nhanh nhất?"],
                        {"situation": "Có thêm một lời mời hoặc một trách nhiệm mới.", "try": "Trước khi trả lời, đánh giá sức hiện tại (1–5); nếu dưới 3, hẹn trả lời sau 24 giờ."},
                        [{"days": 14, "action": "Mỗi sáng chấm mức năng lượng (1–5) và chỉ nhận thêm việc vào ngày từ 3 trở lên.", "track": "Sau 14 ngày, xem năng lượng trung bình thay đổi thế nào."}],
                        ["self", "career"], 65))
        if sg.menh_stars:
            al = action_level(sg.menh_stars) or 0
            key = "action_weak" if al >= 2.5 and b["level"] == "nhược" else ("reason_strong" if al <= 1.5 and b["level"] == "vượng" else None)
            if key:
                out.append(_ins("B_CROSS_SYSTEM", "blind_spot", "Hai hệ thống, hai bức tranh", anchor_menh + ["bazi.strength"],
                                _symbol("Đối chiếu nhóm sao cung Mệnh (Tử Vi) với khí thế Nhật Chủ (Bát Tự).", "he_thong"), _psych("emotion_regulation"),
                                B["cross_system"][key], ["Bạn nhận ra mình trong mô tả nào nhiều hơn: người hành động hay người cân nhắc?", "Nhịp làm việc nào giúp bạn bền nhất?"],
                                {"situation": "Bạn bắt đầu một dự án dài.", "try": "Lên lịch nghỉ và mốc đánh giá ngay từ đầu, trước khi bắt tay vào làm."},
                                [{"days": 30, "action": "Làm việc theo chu kỳ: 3 ngày tập trung, 1 buổi nghỉ có chủ đích.", "track": "Ghi năng lượng cuối mỗi chu kỳ."}],
                                ["self", "career"], 62))
    for e in b.get("excess", []):
        pct = round(100 * b["counts"][e] / 8)
        out.append(_elem("excess", e, B["element_excess"][e].format(pct=pct)))
    for e in b.get("lack", []):
        out.append(_elem("lack", e, B["element_lack"][e]))
    pd = sg.ps["Phúc Đức"]
    for star in pd["major_stars"][:1]:
        if star in sg.menh_stars:
            continue
        sh = S[star]["shadow"]
        out.append(_ins(f"B_PHUC_{slug(star).upper()}", "blind_spot", f"Đời sống nội tâm: {S[star]['need']}", ["phuc.stars"],
                        _star_symbol(star, pd, "Sao này ở cung Phúc Đức (đời sống nội tâm, sự bình yên trong lòng — Khảo Luận pp.214-220)."),
                        _psych(S[star]["psych"]["concept"], S[star]["psych"]["text"]),
                        f"Bề ngoài có thể không thấy, nhưng bên trong bạn có thể mang mâu thuẫn: {sh['conflict']}. Điều chỉnh: {sh['adjust']}",
                        S[star]["questions"][:2], S[star]["scenario"], S[star]["practices"][1:], ["self"], 45, star=star,
                        shadow={"conflict": sh["conflict"], "habit": sh["habit"], "signals": sh["signals"], "adjust": sh["adjust"]}, signal_words=S[star]["signal_words"]))
    return sorted(out, key=lambda x: -x["priority"])


def _desc(level: float) -> str:
    d = kb.load("palaces")["action_desc"]
    return d[min(d, key=lambda k: abs(float(k) - level))]


def _elem(kind: str, e: str, text: str) -> dict:
    return _ins(f"B_ELEM_{kind.upper()}_{slug(e).upper()}", "blind_spot", f"Ngũ hành {'thiên' if kind == 'excess' else 'vắng'}: {e}", ["bazi.elements"],
                _symbol(f"Đếm ngũ hành trên tám chữ (không tính tàng can khi đếm, có xét tàng can khi nói 'vắng'): hành {e} {'nhiều' if kind == 'excess' else 'không có'}.", "pho_thong"),
                _psych("barnum", "Liên hệ giữa ngũ hành và tính khí là ẩn dụ truyền thống, không phải kết quả tâm lý học. Hãy dùng nó như một câu hỏi để quan sát chính mình."),
                text, [f"Mô tả về hành {e} ở trên có khớp với hành vi cụ thể nào của bạn tuần này không? Nếu không, hãy ghi lại.", "Thói quen nào giúp bạn cân bằng hơn?"],
                {"situation": "Một tuần căng thẳng.", "try": "Thử đúng bài tập gợi ý ở trên một lần và ghi lại cảm giác."},
                [{"days": 7, "action": text.rsplit("Thử: ", 1)[-1], "track": "Đánh dấu ngày đã làm và ghi một dòng cảm nhận."}], ["self"], 35)


# --------------------------------------------------------------------------------------------------------------- compass
def compass(sg: Signals) -> dict:
    S, C, P = kb.stars(), kb.load("concepts"), kb.load("palaces")
    out = {}
    for dom in ("career", "money", "love", "family"):
        cfg = C["domains"][dom]
        tend, anchors = [], ["menh.vcd" if sg.vcd else "menh.stars"]
        for star in sg.menh_stars:
            tend.append({"from": f"Hình tượng {star} ở cung Mệnh" + (" (mượn)" if sg.vcd else ""), "text": S[star]["domains"][dom], "source": "he_thong"})
        for pal in cfg["palaces"][:2]:
            p = sg.ps[pal]
            if f"palace.{pal}" in sg.anchors:
                anchors.append(f"palace.{pal}")
            for star in p["major_stars"]:
                if star not in sg.menh_stars:
                    tend.append({"from": f"{star} ở cung {pal}", "text": S[star]["domains"][dom], "source": "he_thong"})
            for h, x in sg.hoa.items():
                if x["palace"] == pal:
                    anchors.append(f"hoa.{h}")
                    tend.append({"from": f"{h} ở cung {pal}", "text": P["hoa"][h]["lesson"].format(area=_area(pal)), "source": "sach+he_thong"})
        vals = []
        for star in sg.menh_stars:
            vals += [v for v in S[star]["values"] if v not in vals]
        out[dom] = {"label": cfg["label"], "palaces": cfg["palaces"], "anchors": sorted(set(anchors)), "tendencies": tend,
                    "questions": C["domain_questions"][dom], "chart_values": [{"id": v, "label": C["values"][v]} for v in vals],
                    "reminder": "Đây là những xu hướng để bạn soi lại khi quyết định, không phải chỉ dẫn. Lựa chọn và trách nhiệm là của bạn."}
    return out


def stage(sg: Signals) -> dict:
    st, B = sg.stage, kb.load("bazi")
    lines = []
    if st.get("dai_han"):
        d = st["dai_han"]
        lines.append(f"Đại hạn {d['age_from']}–{d['age_to']} tuổi ở cung {d['palace']}: theo truyền thống, giai đoạn này đặt trọng tâm vào {d['area']}.")
    if st.get("luck") and st["luck"].get("group"):
        g = B["groups"][st["luck"]["group"]]
        lines.append(f"Đại vận {st['luck']['pillar']} mang can {st['luck']['ten_god']} (nhóm {g['label']}): chủ đề tương ứng là {g['resource']}; mặt dễ quá đà là {g['overuse']}.")
    return {"year": st.get("year"), "age_tuoi_mu": st.get("age_tuoi_mu"), "lines": lines,
            "anchors": [a for a in ("stage.dai_han", "stage.luck") if a in sg.anchors],
            "how_to_use": "Dùng như một lăng kính để đặt câu hỏi cho giai đoạn hiện tại, không phải dự báo sự kiện.",
            "questions": ["Lĩnh vực nêu trên đang chiếm bao nhiêu chỗ trong tâm trí bạn năm nay?", "Nếu giai đoạn này là một lớp học, bài bạn đang học là gì?"]}


def practices(items: list[dict]) -> list[dict]:
    out, seen = [], set()
    for it in items:
        for i, p in enumerate(it["exercise"]["practices"]):
            key = p["action"]
            if key in seen:
                continue
            seen.add(key)
            out.append({"id": f"{it['id']}#{i}", "insight": it["id"], "title": it["title"], "days": p["days"], "action": p["action"], "track": p["track"], "domains": it["domains"]})
    return out


def build(sg: Signals) -> dict:
    ls, bs = lessons(sg), blind_spots(sg)
    C = kb.load("concepts")
    used = {a for it in ls + bs for a in it["anchors"]}
    return {
        "version": VERSION, "status": "draft",
        "disclaimer": ("Tầng Trưởng thành dùng lá số như một tấm gương để tự hỏi, không phải để biết trước. Mỗi nhận định tách ba tầng: biểu tượng truyền thống (có nguồn khi có), "
                       "góc nhìn tâm lý học (giả thuyết để tự kiểm chứng) và đời sống thực (câu hỏi, tình huống, việc nhỏ để thử). Nếu điều gì không đúng với trải nghiệm của bạn, hãy tin trải nghiệm."),
        "barnum": kb.concept("barnum"),
        "layers_legend": {"bieu_tuong": "Biểu tượng truyền thống: điều sách hoặc truyền thống nói về cấu trúc lá số.",
                          "tam_ly": "Góc nhìn tâm lý học: một khái niệm được đặt cạnh biểu tượng như giả thuyết, không phải kết luận từ lá số.",
                          "doi_song": "Đời sống thực: điều này có thể trông thế nào hằng ngày, và việc bạn có thể thử."},
        "anchors": [sg.anchors[a] for a in sg.anchors if a in used or a.startswith(("stage.", "palace."))],
        "lessons": ls, "blind_spots": bs, "compass": compass(sg), "stage": stage(sg), "practices": practices(ls + bs),
        "values": [{"id": k, "label": v} for k, v in C["values"].items()],
        "control_bias": _control_bias(sg),
    }


def _control_bias(sg: Signals) -> dict:
    S, C = kb.stars(), kb.load("concepts")
    bias = [S[s]["control_bias"] for s in sg.menh_stars] or ["mixed"]
    pick = max(("over", "under", "mixed"), key=lambda b: (bias.count(b), b == "mixed"))
    return {"kind": pick, "text": C["control_bias"][pick], "anchors": ["menh.vcd" if sg.vcd else "menh.stars"]}
