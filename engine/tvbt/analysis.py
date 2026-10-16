"""Structure analysis: deterministic, sourced prose built from the CALCULATED charts (no rule needed for a fact to be stated).
Each block carries its layer (Tượng/Khí/Thế/Cách/Dụng/Biến/Phản/Tổng) and its basis:
  tinh_toan = computed fact · sach = reading attributed to a cited book page · he_thong = definition chosen by this system.
Nothing here predicts events; sentences state what the chart contains and what the cited books say about it."""
from __future__ import annotations

import json
from pathlib import Path

from .bazi import BaziChart, growth_stage, ten_god
from .ganzhi import BRANCHES_VI, BRANCH_ELEMENT, ELEMENTS, STEM_ELEMENT, STEMS_VI, generates
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
    ch: dict[str, list] = {k: [] for k in ["tong-quan", "ban-menh", "tinh-cach", "cong-danh", "tai-bach", "quan-he", "dai-van", "cach-cuc"]}

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
    ql, td = v.by_n["Quan Lộc"], v.by_n["Thiên Di"]
    ch["cong-danh"] += [B(f"Cung Quan Lộc ({ql['stem']} {ql['branch']}) nói về {PALACE_ROLE['Quan Lộc']}: " + (_join(v.star_phrase(ql)) or "vô chính diệu") + f". Cung đối là Thiên Di ({td['branch']}): " + (_join(v.star_phrase(td)) or "vô chính diệu") + ".", "Thế", "sach", PALACE_SRC)]
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
    for key, vi in [("branch_six_combine", "lục hợp"), ("branch_clash", "xung"), ("branch_harm", "hại"), ("branch_destroy", "phá"), ("stem_combine", "can hợp"), ("stem_clash", "can xung")]:
        for r in rel[key]:
            rel_txt.append(f"{vi} giữa trụ {r['pillars'].replace('-', ' và trụ ')}")
    ch["quan-he"].append(B("Bát Tự, quan hệ giữa các trụ: " + ("; ".join(rel_txt) if rel_txt else "không có hợp, xung, hại, phá nào giữa các trụ gốc") + ". Mỗi quan hệ chỉ cho biết có tương tác; việc nó hóa, hợp mà không hóa hay có lực hay không cần điều kiện mà hệ thống chưa xét.", "Thế", "sach", ["八字真宗 PDF pp.19-20"]))

    # ---------- Đại vận
    dh_lines = []
    for d in tv.dai_han[:10]:
        p = v.by_n[d["palace"]]
        dh_lines.append(f"{d['age_from']}–{d['age_to']} tuổi: cung {d['palace']} ({d['stem']} {d['branch']}) — " + (_join(p["major_stars"]) or "vô chính diệu") + (f"; {_join(v.hoa_at.get(p['branch_index'], []))}" if v.hoa_at.get(p["branch_index"]) else ""))
    ch["dai-van"].append(B(f"Đại hạn Tử Vi chạy {tv.dai_han_direction}, bắt đầu từ cung Mệnh ở tuổi {tv.cuc['n']} (cục {tv.cuc['name']}). Mỗi hạn 10 năm đi qua một cung, và cung ấy được xét như “Mệnh của giai đoạn”: " + " | ".join(dh_lines) + ".", "Biến", "sach", ["TH p.27"]))
    lp = [f"{l.start_age:.0f} tuổi: {l.name} ({l.ten_god})" for l in bz.luck_pillars[:8]]
    ch["dai-van"].append(B(f"Bát Tự: đại vận {bz.luck_direction}, khởi vận sau khoảng {bz.luck_start['years']} năm {bz.luck_start['months']} tháng. Các đại vận: " + "; ".join(lp) + ". Thập thần ghi theo Nhật Chủ.", "Biến", "sach", ["八字真宗 PDF p.23"]))
    ch["dai-van"].append(B("Tiểu hạn Tử Vi (mỗi năm một cung) và lưu niên/lưu nguyệt Bát Tự xem bằng thanh chọn năm bên dưới. Hệ thống chỉ trình bày cấu trúc thời gian và các tương tác Can Chi với nguyên cục; không suy ra sự kiện cụ thể cho từng năm.", "Biến", "he_thong"))

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
    ch["cach-cuc"].append(B("Tàng can của nguyệt lệnh " + BRANCHES_VI[mb] + ": " + (_join([f"{h['name']} ({h['ten_god']})" for h in mon_h])) + "; " + ("các chữ lộ ra thiên can: " + _join(thau) if thau else "không có chữ nào lộ ra thiên can khác") + ". Việc nguyệt lệnh “thấu can” được các sách Tử Bình dùng để định cách; hệ thống chỉ nêu dữ kiện vì quy tắc định cách chưa được xác minh.", "Cách", "he_thong"))
    ch["cach-cuc"].append(B("Bát Tự: hệ thống chưa có quy tắc cách cục đã xác minh (Tử Bình Chân Thuyên chưa được đưa vào), nên không xác định cách cục từ nguyệt lệnh.", "Cách", "he_thong"))

    # ---------- Phản + Tổng ở mỗi chương liên quan
    ch["tong-quan"].append(B("Điều cần nhớ khi đọc: một sao hay một cách cục chưa nói lên điều gì khi tách khỏi độ sáng, sao đi cùng, Tuần/Triệt và vận hạn. Phần “diễn giải truyền thống” liệt kê từng quy tắc đã khớp kèm trạng thái nguồn; các quy tắc đối lập được tách riêng để bạn tự cân nhắc, không có điểm tổng.", "Tổng"))
    return ch
