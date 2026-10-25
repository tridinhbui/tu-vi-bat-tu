"""Structure analysis: deterministic, sourced prose built from the CALCULATED charts (no rule needed for a fact to be stated).
Each block carries its layer (Tượng/Khí/Thế/Cách/Dụng/Biến/Phản/Tổng) and its basis:
  tinh_toan = computed fact · sach = reading attributed to a cited book page · he_thong = definition chosen by this system.
Nothing here predicts events; sentences state what the chart contains and what the cited books say about it."""
from __future__ import annotations

import json
from pathlib import Path

from .bazi import BaziChart, growth_stage, ten_god
from .ganzhi import BRANCHES_VI, BRANCH_ELEMENT, ELEMENTS, STEM_ELEMENT, STEMS_VI, controls, generates
from .tuvi import TuViChart

_TUHOA = json.loads((Path(__file__).resolve().parent.parent / "data" / "tu_hoa_vi.json").read_text("utf-8"))
_PROFILES = json.loads((Path(__file__).resolve().parent.parent / "data" / "star_profiles.json").read_text("utf-8"))["stars"]
CAT = ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]
SAT = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]
PALACE_ROLE = {  # as defined in Tử Vi Khảo Luận pp.214-220
    "Mệnh": "thể chất, khả năng, quyền hành, tài lộc và cách ứng xử nền tảng", "Phụ Mẫu": "cha mẹ và tuổi thơ",
    "Phúc Đức": "sự thỏa mãn bình yên trong lòng, hạnh kiểm của chính mình và liên hệ họ hàng",
    "Điền Trạch": "nhà cửa, đất đai, cơ nghiệp vật chất", "Quan Lộc": "danh vọng, địa vị trong xã hội",
    "Nô Bộc": "bạn bè và người giúp việc (tấm gương soi bản thân)", "Thiên Di": "giao thiệp bên ngoài và môi trường sống, đối diện với Mệnh",
    "Tật Ách": "hình ảnh thuở thơ ấu và tuổi già", "Tài Bạch": "tiền bạc, của cải", "Tử Tức": "con cái, sợi dây nối quá khứ với tương lai",
    "Phu Thê": "hôn nhân, người hội phối", "Huynh Đệ": "anh chị em, người đồng hàng"}
PALACE_SRC = ["Khảo Luận pp.214-220"]
GROUPS = {"Tử – Phủ – Vũ – Tướng": ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"], "Sát – Phá – Liêm – Tham": ["Thất Sát", "Phá Quân", "Liêm Trinh", "Tham Lang"],
          "Cơ – Nguyệt – Đồng – Lương": ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"], "Cự – Nhật – Nguyệt": ["Cự Môn", "Thái Dương", "Thái Âm"]}
GROUP_NOTE = {"Tử – Phủ – Vũ – Tướng": "nhóm “hành động có lý luận”", "Sát – Phá – Liêm – Tham": "nhóm “hành động mạnh mẽ”",
              "Cơ – Nguyệt – Đồng – Lương": "nhóm “lý luận thuần túy”", "Cự – Nhật – Nguyệt": "nhóm “lý luận thực hành”"}


TRIAD_ELEM = {8: "Thủy", 0: "Thủy", 4: "Thủy", 11: "Mộc", 3: "Mộc", 7: "Mộc", 2: "Hỏa", 6: "Hỏa", 10: "Hỏa", 5: "Kim", 9: "Kim", 1: "Kim"}
DV_EVENT = {"Phu Thê": "chuyện hôn nhân, cưới hỏi", "Tài Bạch": "chuyện tiền bạc", "Tật Ách": "các vấn đề về thể trạng"}


def age_vs_dai_van(age_e: str, dv_e: str) -> tuple[str, str]:
    if age_e == dv_e:
        return "cùng hành", "thoải mái, mức trung bình"
    if controls(age_e, dv_e):
        return "tuổi khắc đại vận", "tự thắng được hoàn cảnh bằng nỗ lực bản thân, tốt"
    if generates(age_e, dv_e):
        return "tuổi sinh xuất cho đại vận", "khó khăn rồi mới thành công, đời sống vất vả, hơi bất lợi"
    if generates(dv_e, age_e):
        return "đại vận sinh nhập cho tuổi", "thuận lợi cho đương số, tốt nhiều"
    return "đại vận khắc tuổi", "bất lợi nhất: dễ gặp trở ngại, thất bại trong làm ăn"


def dai_van_facts(tv, branch_index: int, year_branch: int) -> dict:
    """Khảo Luận pp.230-233 as data for one vận palace (the TS prose voices it): the tam hợp of the vận against the birth year's, whether
    the vận's tam hợp controls the opposite palace's (it then takes the opposite's good stars and refuses its bad ones), whether the nhị hợp
    palace generates the vận (its stars then count), whether the vận sits in the Thái Tuế – Quan Phù – Bạch Hổ triad, and the palace topic."""
    age_e, dv_e = TRIAD_ELEM[year_branch], TRIAD_ELEM[branch_index]
    rel, verdict = age_vs_dai_van(age_e, dv_e)
    opp, nh = (branch_index + 6) % 12, (1 - branch_index) % 12
    by_b = {p["branch_index"]: p for p in tv.palaces}
    return {"src": "Khảo Luận pp.230-233", "age_element": age_e, "van_element": dv_e, "relation": rel, "verdict": verdict,
            "xung_controlled": controls(dv_e, TRIAD_ELEM[opp]), "opp_majors": by_b[opp]["major_stars"],
            "nhi_hop": {"branch": BRANCHES_VI[nh], "palace": by_b[nh]["name"], "counts": generates(TRIAD_ELEM[nh], dv_e), "majors": by_b[nh]["major_stars"]},
            "thai_tue_triad": branch_index in {year_branch, (year_branch + 4) % 12, (year_branch + 8) % 12},
            "event": DV_EVENT.get(by_b[branch_index]["name"])}


def dai_van_reading(v, tv, year_branch: int):
    """Khảo Luận pp.230-233: five-step reading of a đại hạn palace (element of the tam hợp vs the birth year, xung chiếu, nhị hợp, stars, palace topic)."""
    age_e = TRIAD_ELEM[year_branch]
    out = []
    for d in tv.dai_han[:10]:
        p = v.by_n[d["palace"]]
        br_ = p["branch_index"]
        dv_e = TRIAD_ELEM[br_]
        rel, verdict = age_vs_dai_van(age_e, dv_e)
        opp = (br_ + 6) % 12
        opp_e = TRIAD_ELEM[opp]
        xc = (f"tam hợp đại vận ({dv_e}) khắc tam hợp xung chiếu ({opp_e}) nên theo sách là thế tốt (nhận sao tốt, từ chối sao xấu của cung xung chiếu)"
              if controls(dv_e, opp_e) else f"tam hợp đại vận ({dv_e}) không khắc tam hợp xung chiếu ({opp_e})")
        nh = (1 - br_) % 12
        nh_e = TRIAD_ELEM[nh]
        nh_txt = (f"cung nhị hợp {BRANCHES_VI[nh]} ({nh_e}) sinh cho đại vận nên sao của cung này được tính: " + (_join(v.by_b[nh]["major_stars"]) or "vô chính diệu")
                  if generates(nh_e, dv_e) else f"cung nhị hợp {BRANCHES_VI[nh]} ({nh_e}) không sinh cho đại vận nên không tính sao của nó")
        lucky = br_ in {year_branch, (year_branch + 4) % 12, (year_branch + 8) % 12}
        stars = v.star_phrase(p)
        txt = (f"{d['age_from']}–{d['age_to']} tuổi, cung {d['palace']} ({d['stem']} {d['branch']}): chính tinh {_join(stars) or 'vô chính diệu'}. "
               f"Tam hợp {BRANCHES_VI[br_]} thuộc {dv_e}, tuổi {BRANCHES_VI[year_branch]} thuộc {age_e}: {rel}, sách đọc là {verdict}. Xung chiếu: {xc}. {nh_txt[:1].upper() + nh_txt[1:]}.")
        if lucky:
            txt += " Cung này nằm ở tam hợp Thái Tuế – Quan Phù – Bạch Hổ, vị trí sách cho là hanh thông bất kể Mệnh ở đâu."
        if d["palace"] in DV_EVENT:
            txt += f" Hạn đi qua cung {d['palace']} nên sách cho các biến cố của hạn này liên quan đến {DV_EVENT[d['palace']]}."
        out.append(txt)
    return out


def B(text, layer, basis="tinh_toan", src=None):
    return {"layer": layer, "text": text, "basis": basis, "src": src or []}


def _join(xs):
    xs = [x for x in xs if x]
    return ", ".join(xs[:-1]) + " và " + xs[-1] if len(xs) > 1 else (xs[0] if xs else "")


class View:
    def __init__(self, tv: TuViChart, bz: BaziChart):
        self.tv, self.bz = tv, bz
        self.by_b = {p["branch_index"]: p for p in tv.palaces}
        self.by_n = {p["name"]: p for p in tv.palaces}
        self.hoa_at = {}
        for k, v in tv.tu_hoa.items():
            if v["branch"] is not None:
                self.hoa_at.setdefault(v["branch"], []).append(f"{k} ({v['star']})")

    def tam(self, name):
        i = self.by_n[name]["branch_index"]
        return [self.by_b[(i + d) % 12] for d in (0, 4, 8, 6)]

    def stars(self, p, group=None):
        return [s for s in p["stars"] if group is None or s in group]

    def dig(self, p, star):
        return p["major_dignity"].get(star)

    def star_phrase(self, p):
        out = []
        for s in p["major_stars"]:
            d = self.dig(p, s)
            out.append(f"{s} ({d})" if d else f"{s} (độ sáng chưa được sách nêu)")
        return out


def star_profile_blocks(v: View, name: str):
    p = v.by_n[name]
    out = []
    for s in p["major_stars"]:
        pr = _PROFILES.get(s)
        if not pr:
            continue
        d = v.dig(p, s)
        dtxt = f"đứng ở vị trí {d} tại {p['branch']}" if d else f"đứng ở {p['branch']}, vị trí mà bảng độ sáng của sách không nêu"
        out.append(B(f"{s} thuộc {pr['element']}, là {pr['dau']}, được sách gắn với {pr['domain']}; ở cung {name} sao này {dtxt}.", "Tượng", "sach", [pr["locator"]]))
    return out


def reach_note(v: View, name: str):
    tam = v.tam(name)
    cat = sorted({s for p in tam for s in v.stars(p, CAT)})
    hoa = [h for p in tam for h in v.hoa_at.get(p["branch_index"], [])]
    sat = sorted({s for p in tam for s in v.stars(p, SAT)})
    tt = [p["name"] for p in tam if p["tuan"] or p["triet"]]
    return (f"Trong tam phương tứ chính của cung {name} (gồm {_join([p['name'] for p in tam])}): cát tinh {_join(cat) or 'không có'}; "
            f"Tứ Hóa {_join(hoa) or 'không có'}; sát tinh {_join(sat) or 'không có'}; Tuần/Triệt {('ở ' + _join(tt)) if tt else 'không có'}.")


PIL_VI = {"year": "năm", "month": "tháng", "hour": "giờ", "day": "ngày"}
PIL = {"year": "năm", "month": "tháng", "day": "ngày", "hour": "giờ"}


def bazi_core(bz: BaziChart):
    dm = bz.day_master
    dm_el = STEM_ELEMENT[dm]
    mb = bz.pillars["month"].branch
    stage = growth_stage(dm, mb)
    mel = BRANCH_ELEMENT[mb]
    tiet = (mel == dm_el) or generates(mel, dm_el)
    roots = [f"trụ {k}" for k, p in bz.pillars.items() for h in p.hidden if STEM_ELEMENT[h["stem"]] == dm_el]
    vis = {k: p for k, p in bz.pillars.items() if k != "day"}
    helpers = [f"{p.name.split()[0]} ({p.stem_ten_god})" for k, p in vis.items() if p.stem_ten_god in ("Tỉ Kiên", "Kiếp Tài", "Chính Ấn", "Thiên Ấn")]
    return dm_el, mb, stage, tiet, sorted(set(roots), key=roots.index), helpers


def analyse(tv: TuViChart, bz: BaziChart) -> dict:
    v = View(tv, bz)
    dm_el, mb, stage, tiet, roots, helpers = bazi_core(bz)
    dm_name = STEMS_VI[bz.day_master]
    menh = v.by_n["Mệnh"]
    ch: dict[str, list] = {k: [] for k in ["tong-quan", "muoi-hai-cung", "ban-menh", "tinh-cach", "cong-danh", "tai-bach", "quan-he", "dai-van", "cach-cuc"]}

    # ---------- Tổng quan
    comp = v.star_phrase(menh)
    ch["tong-quan"] += [
        B(f"Cung Mệnh an tại {menh['stem']} {menh['branch']}" + (f", có {_join(comp)}" if comp else ", không có chính tinh (vô chính diệu)") + f". Cung Thân cư tại {v.by_b[tv.than_branch]['name']} ({v.by_b[tv.than_branch]['branch']}).", "Thế"),
        B(f"Cục là {tv.cuc['name']}; bản mệnh {tv.menh_nap_am} thuộc hành {tv.menh_element}, nên quan hệ giữa Cục và Mệnh được ghi là “{tv.menh_cuc_relation}”. Đây là quan hệ sinh khắc nền giữa hai hành, chưa phải một phán đoán tốt hay xấu.", "Khí"),
        B(f"Bát Tự: Nhật Chủ {dm_name} thuộc hành {dm_el}, sinh vào tháng {BRANCHES_VI[mb]} (hành {BRANCH_ELEMENT[mb]}); Nhật Chủ ở giai đoạn “{stage}” so với nguyệt lệnh.", "Khí", "sach", ["八字真宗 PDF pp.24-25"]),
        B(f"Hai hệ thống được tính độc lập từ cùng thời điểm sinh đã chuẩn hóa (Tử Vi theo năm âm lịch {tv.year_gz}, Bát Tự theo tiết khí). Hai bên không chung một bộ quy tắc, nên bên dưới không có chỗ nào “cộng điểm” hay lấy hai hệ thống xác nhận lẫn nhau.", "Tổng"),
    ]
    groups = [GROUP_NOTE[g] + f" ({g})" for g, ss in GROUPS.items() if any(s in menh["major_stars"] for s in ss)]
    if groups:
        ch["tong-quan"].append(B("Theo cách phân nhóm của Tử Vi Khảo Luận, các chính tinh ở Mệnh thuộc " + _join(groups) + ". Đây là phân loại tính chất hoạt động của sao, không phải kết luận về kết quả.", "Cách", "sach", ["Khảo Luận pp.166-167"]))

    ex = bz.extras
    if ex:
        vo = ex["kong_wang_in_chart"]
        ch["tong-quan"].append(B(f"Bát Tự còn có ba “cung” phụ tính từ tháng và giờ sinh: thai nguyên {ex['thai_yuan']}, mệnh cung {ex['ming_gong']}, thân cung {ex['shen_gong']}. Thêm vào đó, trụ Ngày {bz.pillars['day'].name} có không vong ở {_join(ex['kong_wang_day'])}" + (f"; chi của trụ {_join([PIL_VI[k] for k in vo])} rơi vào hai chi này." if vo else "; không chi nào của các trụ còn lại rơi vào hai chi này."), "Thế", "sach", ["八字真宗 PDF pp.20, 24, 35-38"]))

    from . import shensha
    ss = shensha.find(bz.pillars)
    if ss:
        cat = [x for x in ss if x["kind"] == "cat"]; tr = [x for x in ss if x["kind"] == "trung"]; hu = [x for x in ss if x["kind"] == "hung"]
        parts = []
        if cat:
            parts.append("các thần sát sách xếp vào nhóm tốt: " + "; ".join(f"{x['vi']} ở trụ {x['pillar_vi']} ({x['at']}) — {x['gloss']}" for x in cat))
        if tr:
            parts.append("nhóm trung tính: " + "; ".join(f"{x['vi']} ở trụ {x['pillar_vi']} ({x['at']}) — {x['gloss']}" for x in tr))
        if hu:
            parts.append("các sao sách xếp vào nhóm hung, hệ thống chỉ ghi vị trí không suy ra kết quả: " + "; ".join(f"{x['vi']} ở trụ {x['pillar_vi']} ({x['at']})" for x in hu))
        ch["cach-cuc"].append(B("Thần sát tra theo bảng của 八字真宗: " + "; ".join(parts) + ". Thần sát là lớp phụ của Bát Tự; không có thần sát nào quyết định một nhận định riêng lẻ.", "Thế", "sach", ["八字真宗 PDF pp.21-22"]))

    # ---------- Bản Mệnh
    ch["ban-menh"] += star_profile_blocks(v, "Mệnh")
    aux = [s for s in menh["stars"] if s not in menh["major_stars"]]
    cat_in = [s for s in aux if s in CAT]
    sat_in = [s for s in aux if s in SAT]
    ch["ban-menh"].append(B("Các sao khác cùng cung Mệnh: " + (_join(aux) if aux else "không có") + ("; trong đó cát tinh " + _join(cat_in) if cat_in else "") + ("; sát tinh " + _join(sat_in) if sat_in else "") + ".", "Thế"))
    ch["ban-menh"].append(B(reach_note(v, "Mệnh"), "Thế"))
    if menh["tuan"] or menh["triet"]:
        ch["ban-menh"].append(B(f"Cung Mệnh có {'Tuần' if menh['tuan'] else ''}{' và ' if menh['tuan'] and menh['triet'] else ''}{'Triệt' if menh['triet'] else ''}. Sách nêu Tuần, Triệt là yếu tố làm các sao ở cung đó bị kìm lại hoặc đổi cách biểu hiện, tùy sao và tùy trường hợp (ví dụ Tử Vi gặp chúng ở Mệnh thì dễ xa quê sớm).", "Phản", "sach", ["TH p.30", "TH p.31"]))
    hoa_menh = v.hoa_at.get(menh["branch_index"], [])
    if hoa_menh:
        ch["ban-menh"].append(B("Tứ Hóa của năm " + tv.year_gz + " rơi ngay vào cung Mệnh: " + _join(hoa_menh) + ".", "Biến"))
    from .tuvi import TU_HOA as _TH
    year_stem = next(i for i, n in enumerate(STEMS_VI) if tv.year_gz.startswith(n))
    adv = _TUHOA["by_stem"][str(year_stem)]
    names = ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"]
    assert [a["star"] for a in adv] == list(_TH[year_stem])        # the book table and the calculation table agree
    ch["ban-menh"].append(B(f"Theo Tử Vi Khảo Luận, Tứ Hóa là bốn dạng của một ngôi sao: Lộc nói về {_TUHOA['meaning']['Hóa Lộc']}, Quyền về {_TUHOA['meaning']['Hóa Quyền']}, Khoa về {_TUHOA['meaning']['Hóa Khoa']}, Kỵ về {_TUHOA['meaning']['Hóa Kỵ']}. Với tuổi {tv.year_gz.split()[0]}, sách mô tả cách mỗi sao “thành” Lộc, Quyền, Khoa, Kỵ như sau: " + "; ".join(f"{n} là {a['star']} — {a['advice']}" for n, a in zip(names, adv)) + ".", "Tượng", "sach", ["Khảo Luận pp.195-197"]))
    pos = []
    for n, x in tv.tu_hoa.items():
        if x["branch"] is not None and n in _TUHOA["position_notes"]:
            pal = v.by_b[x["branch"]]["name"]
            spec = _TUHOA.get("position_notes_by_palace", {}).get(n, {}).get(pal)
            pos.append(f"{n} ở cung {pal}: " + (spec if spec else _TUHOA["position_notes"][n]))
    ch["ban-menh"].append(B("Vị trí các sao hóa trên lá số này và điều sách nói về chúng: " + "; ".join(pos) + ". " + _TUHOA["weight_note"], "Thế", "sach", ["Khảo Luận p.197"]))
    ch["ban-menh"].append(B("Tứ Hóa theo can năm: " + "; ".join(f"{k} tại {x['star']}" + (f" (cung {v.by_b[x['branch']]['name']})" if x['branch'] is not None else "") for k, x in tv.tu_hoa.items()) + ".", "Biến"))

    # ---------- Tính cách
    pd = v.by_n["Phúc Đức"]
    ch["tinh-cach"] += [
        B(f"Cung Mệnh nói về {PALACE_ROLE['Mệnh']}: {_join(comp) or 'vô chính diệu'}. Cung Phúc Đức nói về {PALACE_ROLE['Phúc Đức']}: " + (_join(v.star_phrase(pd)) or "vô chính diệu") + ".", "Dụng", "sach", PALACE_SRC),
    ]
    ch["tinh-cach"] += star_profile_blocks(v, "Phúc Đức")
    ch["tinh-cach"].append(B(reach_note(v, "Phúc Đức"), "Thế"))
    ch["tinh-cach"].append(B(f"Về Bát Tự, tính cách thường được đọc từ Nhật Chủ {dm_name}. Các bảng “nhật can lâm thập thần” và “nhật can ngũ hành” của 八字真宗 (pp.25-26) cho hai mô tả riêng cho {dm_name}; chúng được hiển thị ở phần diễn giải truyền thống bên dưới, cùng cấp độ xác minh của từng quy tắc.", "Dụng", "sach", ["八字真宗 PDF pp.25-26"]))
    crit = []
    crit.append(f"đắc lệnh: {'có' if tiet else 'không'} (tháng {BRANCHES_VI[mb]} hành {BRANCH_ELEMENT[mb]}, {'cùng hành hoặc sinh cho' if tiet else 'không cùng hành và không sinh cho'} Nhật Chủ hành {dm_el}; giai đoạn {stage})")
    crit.append(f"có căn trong tàng can: {('có, ở ' + _join(roots)) if roots else 'không'}")
    crit.append(f"có trợ lực lộ trên thiên can: {('có, ' + _join(helpers)) if helpers else 'không có Ấn hay Tỉ Kiếp trên thiên can'}")
    ch["tinh-cach"].append(B("Ba tiêu chí mà 八字真宗 (p.26) dùng để xét một hành mạnh hay yếu là đắc lệnh, đắc vị, đắc sinh. Với Nhật Chủ của lá số này, theo cách hệ thống định nghĩa từng tiêu chí: " + "; ".join(crit) + ". Hệ thống chỉ nêu từng tiêu chí, không gộp thành nhãn “thân vượng/nhược” vì sách không đưa ngưỡng tính.", "Khí", "he_thong", ["八字真宗 PDF p.26"]))

    # ---------- Công danh
    # the palace opposite Quan Lộc is the one six branches away (always Phu Thê); Thiên Di is in its tam hợp, not opposite it
    ql = v.by_n["Quan Lộc"]
    qd = v.by_b[(ql["branch_index"] + 6) % 12]
    ch["cong-danh"] += [B(f"Cung Quan Lộc ({ql['stem']} {ql['branch']}) nói về {PALACE_ROLE['Quan Lộc']}: " + (_join(v.star_phrase(ql)) or "vô chính diệu") + f". Cung đối là {qd['name']} ({qd['branch']}): " + (_join(v.star_phrase(qd)) or "vô chính diệu") + ".", "Thế", "sach", PALACE_SRC)]
    ch["cong-danh"] += star_profile_blocks(v, "Quan Lộc")
    ch["cong-danh"].append(B(reach_note(v, "Quan Lộc"), "Thế"))
    ql_aux = v.stars(ql, SAT)
    if ql_aux or ql["tuan"] or ql["triet"]:
        ch["cong-danh"].append(B("Yếu tố làm giảm, theo cách sách mô tả chung: " + (_join(ql_aux) + " ở cung Quan Lộc" if ql_aux else "") + (" và " if ql_aux and (ql["tuan"] or ql["triet"]) else "") + ("Tuần/Triệt tại Quan Lộc" if ql["tuan"] or ql["triet"] else "") + ". Sách cho rằng các yếu tố này khiến sao tốt kém phát huy; mức độ cụ thể tùy sao đi cùng.", "Phản", "sach", ["TH pp.29-47"]))
    god_groups = {}
    for k, p in bz.pillars.items():
        for label, tg in ([(f"thiên can trụ {PIL[k]}", p.stem_ten_god)] if p.stem_ten_god else []) + [(f"tàng can trụ {PIL[k]}", h["ten_god"]) for h in p.hidden]:
            if tg in ("Chính Quan", "Thất Sát"):
                god_groups.setdefault("Quan Sát", []).append(label)
            if tg in ("Chính Ấn", "Thiên Ấn"):
                god_groups.setdefault("Ấn", []).append(label)
    ch["cong-danh"].append(B("Bát Tự: " + ("Quan Sát xuất hiện ở " + _join(god_groups["Quan Sát"]) if "Quan Sát" in god_groups else "không có Quan Sát") + "; " + ("Ấn xuất hiện ở " + _join(god_groups["Ấn"]) if "Ấn" in god_groups else "không có Ấn") + ". Đây là vị trí các thập thần, chưa xét việc chúng có thành cách hay không (cần quy tắc cách cục có nguồn).", "Thế"))

    # ---------- Tài bạch
    tb, dt = v.by_n["Tài Bạch"], v.by_n["Điền Trạch"]
    lt = next((p for p in tv.palaces if "Lộc Tồn" in p["stars"]), None)
    mtm = next((p for p in tv.palaces if "Thiên Mã" in p["stars"]), None)
    ch["tai-bach"] += [B(f"Cung Tài Bạch ({tb['stem']} {tb['branch']}) nói về {PALACE_ROLE['Tài Bạch']}: " + (_join(v.star_phrase(tb)) or "vô chính diệu") + f". Cung Điền Trạch ({dt['branch']}): " + (_join(v.star_phrase(dt)) or "vô chính diệu") + ".", "Thế", "sach", PALACE_SRC)]
    ch["tai-bach"] += star_profile_blocks(v, "Tài Bạch")
    ch["tai-bach"].append(B(reach_note(v, "Tài Bạch"), "Thế"))
    if lt:
        ch["tai-bach"].append(B(f"Lộc Tồn nằm ở cung {lt['name']} ({lt['branch']})" + (f", cùng cung với Thiên Mã" if mtm and mtm["branch_index"] == lt["branch_index"] else (f"; Thiên Mã ở cung {mtm['name']}" if mtm else "")) + ". Vị trí này cho biết tài lộc “tọa” ở lĩnh vực nào của lá số; sách có nhắc Lộc Mã gặp nhau nhưng chưa có quy tắc kiểm chứng nên hệ thống chỉ nêu vị trí.", "Thế"))
    tai_vis = sorted({f"{p.name.split()[0]} ({p.stem_ten_god})" for p in bz.pillars.values() if p.stem_ten_god in ("Chính Tài", "Thiên Tài")})
    tai_hid = sum(1 for p in bz.pillars.values() for h in p.hidden if h["ten_god"] in ("Chính Tài", "Thiên Tài"))
    ch["tai-bach"].append(B("Bát Tự: " + (("Tài lộ trên thiên can: " + _join(tai_vis)) if tai_vis else "không có Tài lộ trên thiên can") + f"; trong các tàng can có {tai_hid} chữ thuộc nhóm Tài (Chính Tài, Thiên Tài).", "Thế"))
    hl = next(((k, x) for k, x in tv.tu_hoa.items() if k == "Hóa Lộc"), None)
    if hl and hl[1]["branch"] is not None:
        ch["tai-bach"].append(B(f"Hóa Lộc của năm {tv.year_gz} rơi vào {hl[1]['star']} ở cung {v.by_b[hl[1]['branch']]['name']}; đây là nơi sao “lộc” của lá số tụ lại, nên khi xét tiền bạc nên nhìn song song cung này với cung Tài Bạch.", "Thế"))

    # ---------- Quan hệ
    for name in ["Phu Thê", "Tử Tức", "Huynh Đệ", "Phụ Mẫu", "Nô Bộc"]:
        p = v.by_n[name]
        ch["quan-he"].append(B(f"Cung {name} ({p['branch']}) nói về {PALACE_ROLE[name]}: " + (_join(v.star_phrase(p)) or "vô chính diệu") + (f"; sát tinh {_join(v.stars(p, SAT))}" if v.stars(p, SAT) else "") + (f"; cát tinh {_join(v.stars(p, CAT))}" if v.stars(p, CAT) else "") + (" ; có Tuần/Triệt" if p["tuan"] or p["triet"] else "") + ".", "Thế", "sach", PALACE_SRC))
    dp = bz.pillars["day"]
    ch["quan-he"].append(B(f"Nhật chi {BRANCHES_VI[dp.branch]} (vị trí bạn đời trong Bát Tự theo cách gọi thông dụng) tàng " + _join([f"{h['name']} ({h['ten_god']})" for h in dp.hidden]) + ".", "Thế", "he_thong"))
    rel = bz.relations
    rel_txt = []
    # every pairwise relation of 八字真宗 pp.19-20 the chart has, hình and bán hợp included (audit BZ-17; the hình used to be left out here
    # although the relation panel showed it); 干冲克 says xung or khắc per pair (BZ-1)
    for key, vi in [("branch_six_combine", "lục hợp"), ("branch_semi_triad", "bán hợp"), ("branch_clash", "xung"), ("branch_harm", "hại"), ("branch_destroy", "phá"),
                    ("branch_penalty", "hình"), ("branch_self_penalty", "tự hình"), ("stem_combine", "can hợp"), ("stem_clash", "can xung")]:
        for r in rel.get(key, []):
            label = f"can {r['kind']}" if key == "stem_clash" and r.get("kind") else vi
            if "pillars" not in r:                  # a full 三刑 set: named by its three branches, not by a pair of pillars
                rel_txt.append(f"{vi} đủ bộ " + "–".join(BRANCHES_VI[x] for x in r.get("branches", [])))
                continue
            # pillar ids are 'year-hour'; the reader sees "trụ năm và trụ giờ"
            pv = {"year": "năm", "month": "tháng", "day": "ngày", "hour": "giờ"}
            rel_txt.append(f"{label} giữa " + " và ".join("trụ " + pv.get(x, x) for x in r["pillars"].split("-")))
    ch["quan-he"].append(B("Bát Tự, quan hệ giữa các trụ: " + ("; ".join(rel_txt) if rel_txt else "không có hợp, xung, hình, hại, phá nào giữa các trụ gốc") + ". Mỗi quan hệ chỉ cho biết có tương tác; việc nó hóa, hợp mà không hóa hay có lực hay không cần điều kiện mà hệ thống chưa xét.", "Thế", "sach", ["八字真宗 PDF pp.19-20"]))

    # ---------- Đại vận
    dh_lines = []
    for d in tv.dai_han[:10]:
        p = v.by_n[d["palace"]]
        dh_lines.append(f"{d['age_from']}–{d['age_to']} tuổi: cung {d['palace']} ({d['stem']} {d['branch']}) — " + (_join(p["major_stars"]) or "vô chính diệu") + (f"; {_join(v.hoa_at.get(p['branch_index'], []))}" if v.hoa_at.get(p["branch_index"]) else ""))
    ch["dai-van"].append(B(f"Đại hạn Tử Vi chạy {tv.dai_han_direction}, bắt đầu từ cung Mệnh ở tuổi {tv.cuc['n']} (cục {tv.cuc['name']}). Mỗi hạn 10 năm đi qua một cung; bên dưới là cách Khảo Luận hướng dẫn xét từng hạn: so hành của tam hợp cung đại vận với hành của tam hợp tuổi, so với tam hợp xung chiếu, xét cung nhị hợp, rồi mới xét các sao.", "Biến", "sach", ["TH p.27", "Khảo Luận pp.230-233"]))
    year_branch_idx = BRANCHES_VI.index(tv.year_gz.split()[1])
    from . import van_han
    for d, line in zip(tv.dai_han[:10], dai_van_reading(v, tv, year_branch_idx)):
        stage = van_han.life_stage(tv.dai_han_direction, d["palace"])
        extra = van_han.read(tv, d["palace"], han="dai")
        txt = line + (f" Theo Khảo Luận, hạn này ứng với giai đoạn “{stage}”." if stage else "")
        if extra:
            txt += " Mệnh gặp vận: " + " ".join(e["text"] for e in extra)
        ch["dai-van"].append(B(txt, "Biến", "sach", ["Khảo Luận pp.230-236"]))
    ch["dai-van"].append(B("Sách nhấn mạnh thêm: chính tinh đắc địa thì tốt, hãm địa thì xấu và cần Tuần Triệt giải; hung tinh đắc địa lại có thể tốt, nhất là khi gặp đúng “quan thầy” trong bộ Sát Phá Tham (Không Kiếp gặp Phá Quân, Hỏa Linh gặp Tham Lang, Kình Đà gặp Thất Sát). Hệ thống chưa tự đánh giá hạn tốt hay xấu bằng các điều này: độ sáng phụ tinh nay đã có bảng đối chiếu sách (có sao, có cung sách không nêu), nhưng cách “quan thầy” và Tuần Triệt giải chưa thành quy tắc kiểm chứng.", "Phản", "sach", ["Khảo Luận p.233"]))
    lp = [f"{l.start_age:.0f} tuổi: {l.name} ({l.ten_god})" for l in bz.luck_pillars[:8]]
    ch["dai-van"].append(B(f"Bát Tự: đại vận {bz.luck_direction}, khởi vận sau khoảng {bz.luck_start['years']} năm {bz.luck_start['months']} tháng. Các đại vận: " + "; ".join(lp) + ". Thập thần ghi theo Nhật Chủ.", "Biến", "sach", ["八字真宗 PDF p.23"]))
    ch["dai-van"].append(B("Tiểu hạn Tử Vi (mỗi năm một cung) và lưu niên/lưu nguyệt Bát Tự xem bằng thanh chọn năm bên dưới. Hệ thống chỉ trình bày cấu trúc thời gian và các tương tác Can Chi với nguyên cục; không suy ra sự kiện cụ thể cho từng năm.", "Biến", "he_thong"))

    # ---------- Mười hai cung
    for name in ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]:
        p = v.by_n[name]
        tam = v.tam(name)
        own = v.star_phrase(p)
        extra = [s_ for s_ in p["stars"] if s_ not in p["major_stars"]]
        grp = [GROUP_NOTE[g] for g, ss_ in GROUPS.items() if any(x in p["major_stars"] for x in ss_)]
        txt = (f"Cung {name} ({p['stem']} {p['branch']}{' · Thân cư' if p['is_than'] else ''}) nói về {PALACE_ROLE[name]}. "
               f"Chính tinh: {_join(own) or 'vô chính diệu (mượn sao cung đối để xét)'}"
               + (f"; thuộc {_join(grp)}" if grp else "")
               + (f". Phụ tinh: {_join(extra[:9])}" if extra else "")
               + (f". Cung này có Tuần/Triệt" if p["tuan"] or p["triet"] else "")
               + (f". Sao hóa của năm: {_join(v.hoa_at.get(p['branch_index'], []))}" if v.hoa_at.get(p["branch_index"]) else "")
               + ". " + reach_note(v, name))
        ch["muoi-hai-cung"].append(B(txt, "Thế", "sach", ["Khảo Luận pp.214-220"]))
        if not p["major_stars"]:
            opp = v.by_b[(p["branch_index"] + 6) % 12]
            ch["muoi-hai-cung"].append(B(f"Cung {name} vô chính diệu: khi xét, cung đối {opp['name']} ({opp['branch']}) có {_join(v.star_phrase(opp)) or 'cũng vô chính diệu'} chiếu sang và được dùng thay cho chính tinh của cung này.", "Thế", "sach", ["Khảo Luận pp.220-222"]))

    # ---------- Cách cục
    det = []
    for g, ss in GROUPS.items():
        present = [s for p in v.tam("Mệnh") for s in p["major_stars"] if s in ss]
        if len(set(present)) >= 3:
            det.append((g, sorted(set(present))))
    if det:
        for g, present in det:
            ch["cach-cuc"].append(B(f"Trong tam phương của Mệnh có từ ba sao trở lên của nhóm {g}: {_join(present)}. Đây mới là điều kiện hình thành sơ khởi của một thế cục; việc thế cục ấy thành hay bị phá còn tùy sao phụ, độ sáng và Tuần/Triệt, mà quy tắc hiện chưa phủ hết.", "Cách", "sach", ["Khảo Luận pp.166-167"]))
    else:
        ch["cach-cuc"].append(B("Trong tam phương của Mệnh không có đủ ba sao của một nhóm cách cục nào (Tử Phủ Vũ Tướng, Sát Phá Liêm Tham, Cơ Nguyệt Đồng Lương, Cự Nhật Nguyệt), nên hệ thống không gán nhãn cách cục.", "Cách", "sach", ["Khảo Luận pp.166-167"]))
    spt = [p["name"] for p in tv.palaces if all(s in {x for q in v.tam(p["name"]) for x in q["major_stars"]} for s in ("Thất Sát", "Phá Quân", "Tham Lang"))]
    if spt:
        ch["cach-cuc"].append(B("Cấu trúc Sát – Phá – Tham cùng nằm trong tam phương của các cung: " + _join(spt) + ". Đây là vị trí hình học của ba sao; sách chia ba sao này thành các thế khác nhau tùy cung và sao đi kèm.", "Cách", "sach", ["Khảo Luận pp.166-167"]))
    mon_h = [h for h in bz.pillars["month"].hidden]
    vis_st = {bz.pillars[k].stem: PIL[k] for k in ("year", "month", "hour")}
    thau = [f"{h['name']} (lộ ở thiên can trụ {vis_st[h['stem']]})" for h in mon_h if h["stem"] in vis_st]
    # Bát Tự cách: ONE status everywhere (owner review 2026-10-22). The reading (bazi_deep, prose/bazi_deep.ts) names the cách from the month
    # and draws the dụng thần and the luck verdicts from Thiệu Vĩ Hoa's table; that method is "partial" (yongshen.METHOD_META cach_cuc_tvh: the
    # table is transcribed as printed, the rule that names the cách is only partly checked against TVH pp.356-366). Said so here too.
    cach_name, cach_ver = None, "partial"
    try:
        from .bazi_deep import pipeline as _bp
        from .bazi_deep.model import ChartView as _CV
        _a = _bp.analyse(_CV.from_bazi(bz), with_rules=False)
        cach_name = (_a["geju"]["inner"][0]["name"] if _a["geju"]["inner"] else None)
        cach_ver = ((_a["yongshen"]["methods"].get("cach_cuc_tvh") or {}).get("meta") or {}).get("verification") or "partial"
    except Exception:  # the structure analysis is an extra here
        pass
    ch["cach-cuc"].append(B("Tàng can của nguyệt lệnh " + BRANCHES_VI[mb] + ": " + (_join([f"{h['name']} ({h['ten_god']})" for h in mon_h])) + "; " + ("các chữ lộ ra thiên can: " + _join(thau) if thau else "không có chữ nào lộ ra thiên can khác") + ". Chữ của nguyệt lệnh lộ ra thiên can là căn cứ để định cách; phép định cách này mới được đối chiếu một phần với Thiệu Vĩ Hoa (Dự Đoán Theo Tứ Trụ tr.356-366).", "Cách", "he_thong"))
    ch["cach-cuc"].append(B(("Bát Tự: cách lập từ nguyệt lệnh là cách " + cach_name + "; trạng thái: xác lập một phần" + ("" if cach_ver == "partial" else f" ({cach_ver})") + ". Dụng thần và vận tốt, vận xấu tra theo bảng của Thiệu Vĩ Hoa cho cách này (tr.378-386) vì vậy đều có điều kiện: chúng đúng nếu cách " + cach_name + " được xác lập.")
                            if cach_name else "Bát Tự: không lập được cách từ nguyệt lệnh (hoặc lá số theo một cách đặc biệt), nên phần dụng thần theo cách không áp dụng.", "Cách", "he_thong"))

    # ---------- Phản + Tổng ở mỗi chương liên quan
    ch["tong-quan"].append(B("Điều cần nhớ khi đọc: một sao hay một cách cục chưa nói lên điều gì khi tách khỏi độ sáng, sao đi cùng, Tuần/Triệt và vận hạn. Phần “diễn giải truyền thống” liệt kê từng quy tắc đã khớp kèm trạng thái nguồn; các quy tắc đối lập được tách riêng để bạn tự cân nhắc, không có điểm tổng.", "Tổng"))
    return ch
