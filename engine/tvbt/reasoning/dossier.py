"""Six-layer palace dossier (docs/REASONING-ENGINE-DESIGN.md §3). For every one of the twelve palaces:

  1 ban_cung      the palace itself: chính tinh with brightness ONLY from a source table (else 'chưa có trong bảng'), phụ tinh split by
                  placement status (đã đối chiếu / công thức phổ biến), Tứ Hóa, Tuần/Triệt, Trường Sinh stage, thủ/đồng/vô chính diệu.
  2 tam_phuong    đồng cung, xung chiếu, hội chiếu (tam hợp) and giáp kept apart, with the chủ/khách split of Toàn Thư tr.17-18 and,
                  for a vô chính diệu palace, the explicit borrowing rule of Toàn Thư tr.18.
  3 cach          named configurations: rule-recognised ones (with their qualifiers) and name-only detections (cach_cuc.py, unverified);
                  for Mệnh and Thân also the 'thành phá' test of Toàn Thư tr.18.
  4 menh_than_cuc Mệnh/Thân/Cục facts (only on the Mệnh and Thân palaces).
  5 van           which đại hạn this palace rules, and whether the year's đại hạn / tiểu hạn / lưu Thái Tuế / lưu stars touch it.
  6 tong_hop      the palace's conclusions grouped as themes, supports, limits, conditions, alternatives and open questions.

Facts and source labels only; every sentence that interprets cites a conclusion (rule ids) or a page. No event is predicted.
"""
from __future__ import annotations

from ..aux_stars import GROUP as AUX_UNVERIFIED_GROUP
from ..ganzhi import BRANCHES_VI
from ..tuvi import PALACES, TuViChart
from .positions import CAT_STARS, SAT_STARS

TRUONG_SINH = ("Trường Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng")
TU_HOA_NAMES = ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ")
TU_CAT = ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc", "Lộc Tồn")                      # Toàn Thư tr.18: "Khoa Quyền Lộc Quý"
QUY = ("Thiên Khôi", "Thiên Việt")                                            # operationalisation of "Quý" (open question)
TU_HUNG = ("Hỏa Tinh", "Linh Tinh", "Kình Dương", "Đà La")                     # Toàn Thư tr.18: "tứ hung Hỏa Linh Dương Đà"
GIAP_PAIRS = [("Kình Dương", "Đà La"), ("Tả Phụ", "Hữu Bật"), ("Văn Xương", "Văn Khúc"), ("Thiên Khôi", "Thiên Việt"),
              ("Địa Không", "Địa Kiếp"), ("Hỏa Tinh", "Linh Tinh"), ("Thái Dương", "Thái Âm")]
DIGNITY_SRC = {"thuc_hanh": "Tử Vi Thực Hành tr.29-48", "toan_thu": "Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục)"}
MINOR_DIGNITY_SRC = "Tử Vi Đẩu Số Toàn Thư (bảng phụ tinh, dignity_minor.json)"

DOMAIN = {"Mệnh": "con người, khí chất", "Phụ Mẫu": "cha mẹ, bề trên", "Phúc Đức": "đời sống tinh thần, phúc phần, họ hàng",
          "Điền Trạch": "nhà cửa, của cải tích lũy", "Quan Lộc": "công việc, địa vị", "Nô Bộc": "bạn bè, người cộng tác, cấp dưới",
          "Thiên Di": "ra ngoài, môi trường xã hội", "Tật Ách": "thể trạng theo nghĩa biểu tượng", "Tài Bạch": "tiền bạc, thu nhập",
          "Tử Tức": "con cái, người đi sau, sản phẩm sáng tạo", "Phu Thê": "hôn nhân, bạn đời", "Huynh Đệ": "anh chị em, người đồng hành"}
GUARD = {
    "Tật Ách": "Cung Tật Ách chỉ được đọc như biểu tượng truyền thống về thể trạng; không có câu nào ở đây là chẩn đoán hay dự báo bệnh.",
    "Phu Thê": "Các câu về hôn nhân là khuynh hướng theo sách cổ, không phải dự đoán chuyện cưới hỏi, ly hợp hay số lần kết hôn.",
    "Tử Tức": "Các câu về con cái là khuynh hướng theo sách cổ, không phải dự đoán số con, giới tính hay sức khỏe của con.",
}
VCD_RULE = ("Toàn Thư tr.18: cung không có chính tinh thì mượn sao ở cung xung chiếu làm chủ, sao ở cung tam hợp làm khách; nếu cả hai "
            "cung xung chiếu đều vô chính diệu thì chỉ lấy sao khách mà luận.")
VCD_LIMIT = ("Sách không nói sao mượn có đủ sức như sao thủ cung, nên hệ thống không áp các câu viết cho sao thủ cung lên sao mượn; "
             "Khảo Luận tr.141-142 thêm rằng Tuần, Triệt đóng ở cung vô chính diệu lại là tốt, tùy hoàn cảnh.")


def _offsets(b: int) -> dict[str, int]:
    return {"self": b, "opp": (b + 6) % 12, "trine1": (b + 4) % 12, "trine2": (b + 8) % 12, "flank_prev": (b - 1) % 12, "flank_next": (b + 1) % 12}


def _star_groups(tv: TuViChart) -> dict[str, str]:
    return {s.name: s.group for s in tv.stars} if hasattr(tv, "stars") else {}


def _hoa_at(tv: TuViChart) -> dict[int, list[tuple[str, str]]]:
    out: dict[int, list[tuple[str, str]]] = {}
    for k, v in tv.tu_hoa.items():
        if v.get("branch") is not None:
            out.setdefault(v["branch"], []).append((k, v["star"]))
    return out


def _brief(p: dict, hoa: list[tuple[str, str]]) -> dict:
    """Short view of a palace used in the tam phương layer."""
    majors = [{"star": m, "dignity": p["major_dignity"].get(m)} for m in p["major_stars"]]
    return {"palace": p["name"], "branch": p["branch"], "majors": majors,
            "cat": [s for s in p["stars"] if s in CAT_STARS], "sat": [s for s in p["stars"] if s in SAT_STARS],
            "loc_ma": [s for s in p["stars"] if s in ("Lộc Tồn", "Thiên Mã")],
            "hoa": [f"{k} ({s})" for k, s in hoa], "tuan": p["tuan"], "triet": p["triet"]}


def _maj_txt(majors: list[dict]) -> str:
    return ", ".join(f"{m['star']} ({m['dignity']})" if m.get("dignity") else m["star"] for m in majors) or "vô chính diệu"


def thanh_pha(tv: TuViChart, b: int) -> dict:
    """Toàn Thư tr.18-19 'thành phá' / 'cứu khí' for a Mệnh or Thân palace: which of the four good (Khoa Quyền Lộc Quý) and the four
    harsh stars (Hỏa Linh Dương Đà) meet the palace from its tam hợp and xung chiếu. The book's four outcomes are reported as printed; the
    reading of 'Quý' as Thiên Khôi / Thiên Việt and of 'gặp' as the three other palaces of the tam phương are operationalisations."""
    by = {p["branch_index"]: p for p in tv.palaces}
    hoa = _hoa_at(tv)
    meet_b = [(b + 4) % 12, (b + 8) % 12, (b + 6) % 12]
    stars = {s: by[x]["name"] for x in meet_b for s in by[x]["stars"]}
    hoas = {k: by[x]["name"] for x in meet_b for k, _ in hoa.get(x, [])}
    good = [f"{s} ({stars[s]})" for s in ("Lộc Tồn",) + QUY if s in stars] + [f"{k} ({hoas[k]})" for k in TU_CAT[:3] if k in hoas]
    bad = [f"{s} ({stars[s]})" for s in TU_HUNG if s in stars]
    if good and bad:
        verdict, label = "thanh_co_pha", "trong thành có phá (“bạch khuê hữu điểm”: ngọc trắng có vết)"
    elif good:
        verdict, label = "thanh", "cách thành (“giao long đắc vân vũ”)"
    elif bad:
        verdict, label = "pha", "phá cách (“miêu nhi bất tú”: nảy mầm mà không tốt)"
    else:
        verdict, label = "chua_thanh", "chưa thành nhưng không bị phá, chờ vận hạn (“hỗn kim phác ngọc”)"
    return {"method": "Thành phá tứ pháp", "source": "Tử Vi Đẩu Số Toàn Thư, tr.18", "good_met": good, "harsh_met": bad,
            "verdict": verdict, "label": label,
            "open_questions": ["“Quý” được hiểu là Thiên Khôi, Thiên Việt; “gặp” được hiểu là ở ba cung tam hợp và xung chiếu. Cả hai là cách hiểu của hệ thống.",
                               "Toàn Thư áp phép này khi bản cung có sao tốt; sách không định nghĩa “sao tốt” cho 14 chính tinh, nên hệ thống không lọc điều kiện ấy.",
                               "Sách không nói Tuần/Triệt ở cung chiếu có làm mất tác dụng của sao chiếu hay không."]}


def build(tv: TuViChart, conclusions: list, layered: dict | None = None, dignity_school: str = "thuc_hanh") -> list[dict]:
    from .. import cach_cuc
    by = {p["branch_index"]: p for p in tv.palaces}
    groups = _star_groups(tv)
    hoa = _hoa_at(tv)
    detected = tv.extras.get("cach_cuc") or cach_cuc.detect(tv)
    out = []
    order = sorted(tv.palaces, key=lambda p: PALACES.index(p["name"]) if p["name"] in PALACES else 99)
    for p in order:
        b, name = p["branch_index"], p["name"]
        off = _offsets(b)
        mine = [c for c in conclusions if getattr(c, "palace", None) == name]
        # 1. bản cung
        majors = [{"star": m, "dignity": p["major_dignity"].get(m),
                   "dignity_source": DIGNITY_SRC[dignity_school] if p["major_dignity"].get(m) else "bảng đang dùng không ghi vị trí này"}
                  for m in p["major_stars"]]
        aux = [s for s in p["stars"] if s not in p["major_stars"]]
        stage = next((s for s in aux if s in TRUONG_SINH), None)
        ban = {"palace": name, "branch": p["branch"], "stem": p.get("stem"), "domain": DOMAIN.get(name, ""),
               "structure": "vô chính diệu" if not majors else ("thủ" if len(majors) == 1 else "đồng"),
               "majors": majors,
               "aux_verified": [s for s in aux if groups.get(s) != AUX_UNVERIFIED_GROUP and s not in TRUONG_SINH],
               "aux_unverified": [s for s in aux if groups.get(s) == AUX_UNVERIFIED_GROUP],
               "aux_dignity": {s: v for s, v in p["minor_dignity"].items() if v},
               "aux_dignity_source": MINOR_DIGNITY_SRC if any(p["minor_dignity"].values()) else None,
               "tu_hoa": [f"{k} ({s})" for k, s in hoa.get(b, [])],
               "tuan": p["tuan"], "triet": p["triet"], "truong_sinh": stage, "is_than": p["is_than"]}
        # 2. tam phương tứ chính + giáp
        roles = {r: _brief(by[x], hoa.get(x, [])) for r, x in off.items()}
        flank = [by[off["flank_prev"]], by[off["flank_next"]]]
        giap = [f"{a} – {c}" for a, c in GIAP_PAIRS if (a in flank[0]["stars"] and c in flank[1]["stars"]) or (c in flank[0]["stars"] and a in flank[1]["stars"])]
        chu = [m["star"] for m in majors]
        borrowed = None
        if not chu:
            opp_m = roles["opp"]["majors"]
            borrowed = {"rule": VCD_RULE, "limit": VCD_LIMIT, "from": roles["opp"]["palace"],
                        "chu": [m["star"] for m in opp_m], "khach_only": not opp_m}
        # khách: tam hợp + xung chiếu; when the xung chiếu stars are borrowed as chủ (vô chính diệu), only the tam hợp remain khách
        khach = [m["star"] for r in (("trine1", "trine2") if borrowed and borrowed["chu"] else ("trine1", "trine2", "opp")) for m in roles[r]["majors"]]
        tp = {"relations": {"dong_cung": roles["self"], "xung_chieu": roles["opp"], "hoi_chieu": [roles["trine1"], roles["trine2"]],
                            "giap": [roles["flank_prev"], roles["flank_next"]]},
              "giap_pairs": giap,
              "chu": chu or (borrowed["chu"] if borrowed else []), "khach": khach,
              "chu_khach_source": "Tử Vi Đẩu Số Toàn Thư, tr.17-18 (bản phương là chủ, tam hợp và xung chiếu là khách)",
              "vo_chinh_dieu": borrowed,
              "cat_in_tp": sorted({s for r in ("self", "opp", "trine1", "trine2") for s in roles[r]["cat"]}),
              "sat_in_tp": sorted({s for r in ("self", "opp", "trine1", "trine2") for s in roles[r]["sat"]}),
              "hoa_in_tp": sorted({h for r in ("self", "opp", "trine1", "trine2") for h in roles[r]["hoa"]})}
        # 3. cách cục
        cach = {"recognised": [{"conclusion": c.conclusion_id, "reading": "; ".join(r["reading"] for r in c.supporting_rules),
                                "qualifiers": [q for q in c.invalidating_conditions if q["status"] != "not_met" or q["effect"] == "requires_for_durability"]}
                               for c in mine if c.polarity == "neutral" and c.aspect == "nhan_dien"],
                "by_name_only": [{**d, "note": "chỉ nhận diện tên theo vị trí sao; ý nghĩa chưa đối chiếu sách"} for d in detected if d.get("where") == name]}
        if name == "Mệnh" or p["is_than"]:
            cach["thanh_pha"] = thanh_pha(tv, b)
        # 4. Mệnh – Thân – Cục
        mtc = None
        if name == "Mệnh" or p["is_than"]:
            mtc = {"cuc": tv.cuc["name"], "menh_nap_am": tv.menh_nap_am, "menh_element": tv.menh_element, "relation": tv.menh_cuc_relation,
                   "than_cu": next(q["name"] for q in tv.palaces if q["is_than"]),
                   "menh_chu": tv.extras.get("menh_chu"), "than_chu": tv.extras.get("than_chu"),
                   "note": "Mệnh chủ, Thân chủ theo bảng phổ biến; ba sách đã đối chiếu không in bảng này (NEEDS SOURCE)."}
        # 5. vận
        dh = next((d for d in tv.dai_han if d["palace"] == name), None)
        van = {"dai_han": {"age_from": dh["age_from"], "age_to": dh["age_to"], "stem": dh["stem"]} if dh else None}
        if layered:
            here = lambda key: layered.get(key) == name
            tp_names = {roles[r]["palace"] for r in ("self", "opp", "trine1", "trine2")}
            van.update({"year": layered["year"], "is_dai_han": here("dai_han_palace"), "is_tieu_han": here("tieu_han_palace"),
                        "is_luu_thai_tue": here("luu_thai_tue_palace"),
                        "in_tp_of_dai_han": layered.get("dai_han_palace") in tp_names,
                        "in_tp_of_tieu_han": layered.get("tieu_han_palace") in tp_names,
                        "luu_tinh": [k for k, v in (layered.get("luu_tinh") or {}).items() if v == name],
                        "luu_hoa": [k for k, v in (layered.get("luu_hoa") or {}).items() if v == name],
                        "dai_han_hoa": [k for k, v in (layered.get("dai_han_hoa") or {}).items() if v == name]})
        # 6. tổng hợp
        sup = [c for c in mine if c.polarity == "support"]
        lim = [c for c in mine if c.polarity == "limit"]
        neu = [c for c in mine if c.polarity == "neutral" and c.aspect != "nhan_dien"]
        tong = {"themes": [c.conclusion_id for c in sup if not c.generic], "supports": [c.conclusion_id for c in sup],
                "limits": [c.conclusion_id for c in lim], "neutral": [c.conclusion_id for c in neu],
                "conditions": sorted({f"{q['text']} ({q['source']})" for c in mine for q in c.invalidating_conditions if q["status"] == "met"}),
                "alternatives": [{"a": c.conclusion_id, **k} for c in mine for k in c.conflicts if c.polarity == "support"],
                "open_questions": sorted({u for c in mine for u in c.unresolved_questions}),
                "generic_only": bool(mine) and all(c.generic for c in mine),
                "no_verified_rule": not mine, "guard": GUARD.get(name)}
        out.append({"palace": name, "layers": {"ban_cung": ban, "tam_phuong": tp, "cach": cach, "menh_than_cuc": mtc, "van": van, "tong_hop": tong},
                    "summary": summary_vi(name, ban, tp, van, mine)})
    return out


def summary_vi(name: str, ban: dict, tp: dict, van: dict, mine: list) -> str:
    """Plain-language structural sentence for the palace (facts only), used when no verified rule speaks to it and as each chapter's base."""
    s = f"{name} ({DOMAIN.get(name, '')}) ở {ban['branch']}: "
    if ban["majors"]:
        s += ("chính tinh " if len(ban["majors"]) == 1 else "hai chính tinh ") + _maj_txt(ban["majors"])
    else:
        vcd = tp["vo_chinh_dieu"] or {}
        s += "vô chính diệu" + (f", theo Toàn Thư mượn {', '.join(vcd['chu'])} từ {vcd['from']} làm chủ" if vcd.get("chu") else
                                ", cung xung chiếu cũng vô chính diệu nên chỉ lấy sao khách")
    extra = []
    if ban["tu_hoa"]:
        extra.append("có " + ", ".join(ban["tu_hoa"]))
    if ban["tuan"] or ban["triet"]:
        extra.append("có " + " và ".join(x for x, y in (("Tuần", ban["tuan"]), ("Triệt", ban["triet"])) if y))
    good = [s for s in ban["aux_verified"] if s in CAT_STARS + ("Lộc Tồn", "Thiên Mã")]
    bad = [s for s in ban["aux_verified"] if s in SAT_STARS]
    if good:
        extra.append("phụ tinh " + ", ".join(good))
    if bad:
        extra.append("sát tinh " + ", ".join(bad))
    if extra:
        s += "; " + "; ".join(extra)
    s += f". Khách từ tam phương: {', '.join(tp['khach']) or 'không có chính tinh'}"
    if tp["sat_in_tp"]:
        s += f"; sát tinh trong tam phương: {', '.join(tp['sat_in_tp'])}"
    if tp["giap_pairs"]:
        s += f"; bị giáp bởi {', '.join(tp['giap_pairs'])}"
    s += "."
    if van.get("dai_han"):
        d = van["dai_han"]
        s += f" Cung này là đại hạn {d['age_from']}–{d['age_to']} tuổi."
    return s
