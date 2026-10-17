"""Phase 5: SCHOOL / SOURCE variants of the 10 draft formations -> engine/data/experimental/formations_school_variants.json

The baseline (formations_experimental.json, owned by another session) is NEVER edited and NEVER merged into one rule. Each variant is a
separate, labelled definition for ONE book's reading (school kl / th / tt), built from the baseline by:
  - keeping only the conditions the audit found supported IN THAT ROLE by that book (everything else is listed under `dropped`);
  - replacing a condition whose SCOPE the book states explicitly (đồng cung / đối cung / tam phương / hội chiếu);
  - adding the book's own conditions the baseline lacks (e.g. KL p.50 Tử Phủ + Kình Dương as a *booster*, opposite to TT p.22).
Contradicting definitions stay contradicting: they are different variants with different ids (`<baseline id>@<school>_<page>`), none is "the right one".

Scope vocabulary (kept apart; a book's word "gặp" is NOT widened unless the sentence fixes the scope):
  dong_cung = same palace as Mệnh | doi_cung = opposite palace (xung chiếu) | tam_phuong = Mệnh + đối + 2 tam hợp (hội chiếu)
Rescuers: no source says a given star rescues a given formation, so NO variant carries a rescuer ("phá được cứu" exists only in the baseline hypothesis).
Everything stays reviewStatus="draft", experimental=True.  Nothing is promoted to verified here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_formation_audit as au  # noqa: E402  (citation table Q)

BASE = ROOT / "engine/data/experimental/formations_experimental.json"
OUT = ROOT / "engine/data/experimental/formations_school_variants.json"

SCHOOL_VI = {"kl": "Tử Vi Khảo Luận", "th": "Tử Vi Thực Hành", "tt": "Tử Vi Đẩu Số Toàn Thư"}


def f(name, op, val):
    return {"fact": name, "operator": op, "value": val}


def A(*xs):
    return {"all": list(xs)}


def O(*xs):
    return {"any": list(xs)}


def ev(i, label, when):
    return {"id": i, "label": label, "when": when}


def has(role, kind, star):
    return f(f"palace.rel.{role}_{kind}", "contains", star)


CAT6 = ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]
V = []   # variant specs


def variant(base, school, page, title, cites, keep=None, add=None, core=None, readings=(), note="", name_vi=None):
    V.append(dict(base=base, school=school, page=page, title=title, cites=cites, keep=keep or {}, add=add or {}, core=core,
                  readings=list(readings), note=note, name_vi=name_vi))


T = "CACH_X_"
# ---- Tử Phủ Vũ Tướng ------------------------------------------------------------------------------------------------------
variant(T + "TU_PHU_VU_TUONG", "kl", "132_193", "KL: cần Tả Hữu, Xương Khúc", ["KL132_TPVT_TAHUU", "KL193_TPVT_XK", "KL222_VT_TUAN"],
        keep={"boosters": ["ta_huu_hoi", "xuong_khuc_hoi"], "refutations": ["tuan_triet_an_ngu"]},
        readings=["KL p.132, p.193 không nêu phạm vi của Tả Hữu/Xương Khúc; baseline đọc là hội trong tam phương"],
        note="KL nói Tử Phủ Vũ Tướng cần Tả Hữu, Xương Khúc và sợ Tuần/Triệt. Sát tinh/Kỵ làm phá chỉ được TH p.116 nói trong ngữ cảnh đại tiểu hạn nên không đưa vào bản này.")
variant(T + "TU_PHU_VU_TUONG", "th", "115", "TH: gặp Lộc, Tả Hữu (đại tiểu hạn)", ["TH72_TPVT", "TH115_TPVT", "TH94_PHU", "TH95_TUONG"],
        keep={"boosters": ["loc_hoi", "ta_huu_hoi"], "refutations": ["tuan_triet_an_ngu"]},
        readings=["TH p.115-116 viết về đại tiểu hạn; ở đây chỉ dùng như thước đo của bản cách"],
        note="Phá cách (Tam Không, Kiếp, Kỵ, Hình, Đà, Linh Hỏa) có ở TH p.116 nhưng là 'gặp' trong hạn nên chưa mô hình hóa.")
# ---- Tử Phủ đồng cung: hai trường phái đối nghịch ---------------------------------------------------------------------------
variant(T + "TU_PHU_DONG_CUNG", "tt", "22", "TT: vô sát tấu mới hưởng phúc", ["TT22_TPDC_SAT", "KL55_TP_TUAN"],
        keep={"breakers": ["sat_dong_cung"], "refutations": ["tuan_triet_an_ngu"]},
        readings=["'gặp sát tinh' của TT p.22 được hiểu là đồng cung (cách hẹp nhất); sách không nêu phạm vi"],
        note="Đối lập với bản KL p.50. Hai bản KHÔNG được hợp nhất: TT coi sát tinh là phá, KL coi Kình Dương đồng cung vẫn giàu.")
variant(T + "TU_PHU_DONG_CUNG", "kl", "50", "KL: Kình Dương hoặc Kỵ + Quyền đồng cung vẫn tốt", ["KL50_TP_KINH", "KL50_TP_KY", "KL55_TP_TUAN"],
        keep={"refutations": ["tuan_triet_an_ngu"]},
        add={"boosters": [ev("kinh_luc_si_dong_cung", "Kình Dương và Lực Sĩ đồng cung với Tử Phủ (buôn bán giàu có, KL tr.50)",
                             f("palace.rel.self_stars", "contains_all", ["Kình Dương", "Lực Sĩ"])),
                          ev("ky_quyen_dong_cung", "Hóa Kỵ và Hóa Quyền đồng cung với Tử Phủ (mưu cơ tài trí, KL tr.50)",
                             f("palace.rel.self_hoa", "contains_all", ["Hóa Kỵ", "Hóa Quyền"]))]},
        note="Ngược với TT p.22: ở đây Kình Dương/Kỵ đồng cung là yếu tố tăng thế, không phải phá.")
# ---- Cơ Nguyệt Đồng Lương -------------------------------------------------------------------------------------------------
variant(T + "CO_NGUYET_DONG_LUONG", "tt", "24", "TT: Kiếp, Không, Hóa Kị trong tam hợp xung chiếu thì hạ cách", ["TT24_CNDL_CORE", "TT24_CNDL_BREAK"],
        keep={"boosters": ["cat_tinh_hoi"]},
        add={"breakers": [ev("khong_kiep_trong_tam_phuong", "Địa Không hoặc Địa Kiếp trong tam phương của Mệnh (TT tr.24)",
                             f("palace.rel.tp_stars", "contains_any", ["Địa Không", "Địa Kiếp"])),
                          ev("ky_trong_tam_phuong", "Hóa Kỵ trong tam phương của Mệnh (TT tr.24)", has("tp", "hoa", "Hóa Kỵ"))]},
        readings=["TT p.24 nói ngay trong câu 'Mệnh thân và các cung tam hợp xung chiếu': phạm vi = tam phương (đã xác định, không suy rộng)"],
        note="Sửa lỗi lá số đối chứng Hạng Võ / Mậu Tý: baseline chỉ tính đồng cung Mệnh. Tuần/Triệt không được TT p.24 nêu nên không là phá.")
variant(T + "CO_NGUYET_DONG_LUONG", "kl", "221", "KL: hội Khoa Quyền Lộc, Khôi Việt, Xương Khúc", ["KL51_CNDL", "KL221_SPLT"],
        keep={"boosters": ["cat_tinh_hoi", "khoa_quyen_loc_hoi"]},
        readings=["KL p.221 được đọc từ ảnh trang (lớp chữ hỏng)"],
        note="KL không nêu yếu tố phá cho CNDL, nên bản này không có breaker.")
# ---- Sát Phá Liêm Tham ----------------------------------------------------------------------------------------------------
variant(T + "SAT_PHA_LIEM_THAM", "th", "76_77", "TH: hội cát tinh (Khoa Quyền Lộc) / hạ cách khi nhiều sát tinh",
        ["TH72_SPLT", "TH76_CATTINH", "TH77_SPLT_HA", "TH116_SPLT"],
        keep={"boosters": ["khoa_quyen_hoi"], "breakers": ["ba_sat_va_ky_trong_tam_phuong"]},
        readings=["'nhiều' sát tinh của TH p.77 → ngưỡng 3 sát tinh + Hóa Kỵ là QUY ƯỚC THIẾT KẾ, không phải số của sách",
                  "'3 trong 4 sao' của lõi cũng là quy ước"],
        note="TH p.76 lại xếp Kình, Không vào nhóm cát hội của Thân Sát Phá Liêm Tham: bất đồng nội bộ TH, ghi nhận trong ma trận.")
# ---- Nhật Nguyệt tịnh minh: hai định nghĩa vị trí ---------------------------------------------------------------------------
variant(T + "NHAT_NGUYET_TINH_MINH", "th", "72", "TH: vị trí cố định (Nhật Thìn/Tỵ, Nguyệt Dậu/Tuất, Mệnh ở Nhật hay Nguyệt)", ["TH72_NNTM", "TT142_NNTM"],
        core=O(A(f("palace.branch", "eq", "Thìn"), has("self", "majors", "Thái Dương"), has("opp", "majors", "Thái Âm")),
               A(f("palace.branch", "eq", "Tuất"), has("self", "majors", "Thái Âm"), has("opp", "majors", "Thái Dương")),
               A(f("palace.branch", "eq", "Tỵ"), has("self", "majors", "Thái Dương"), has("trine1", "majors", "Thái Âm")),
               A(f("palace.branch", "eq", "Dậu"), has("self", "majors", "Thái Âm"), has("trine2", "majors", "Thái Dương"))),
        keep={"boosters": ["nhat_nguyet_deu_sang"], "breakers": ["nhat_nguyet_ham_gap_sat"]},
        note="Định nghĩa theo vị trí của TH p.72; hẹp hơn bản KL p.53 (hợp chiếu tịnh minh).")
variant(T + "NHAT_NGUYET_TINH_MINH", "kl", "53_68", "KL: Nhật Nguyệt hợp chiếu Mệnh, hãm cần Khôi Việt chiếu", ["KL53_NN_TINHMINH", "KL56_NN_HAM", "KL68_NN_KHOIVIET"],
        keep={"boosters": ["nhat_nguyet_deu_sang"], "breakers": ["nhat_nguyet_ham_gap_sat"]},
        add={"refutations": [ev("nhat_nguyet_ham_khong_khoi_viet", "Nhật hoặc Nguyệt hãm mà không có Khôi/Việt chiếu (KL tr.68)",
                                A(O(f("palace.tp_rank.Thái Dương", "lte", 0), f("palace.tp_rank.Thái Âm", "lte", 0)),
                                  f("palace.rel.tp_stars", "not_contains", "Thiên Khôi"), f("palace.rel.tp_stars", "not_contains", "Thiên Việt")))]},
        readings=["'Khôi Việt chiếu' (KL p.68) được đọc là hội chiếu = tam phương"],
        note="Tuần/Triệt KHÔNG là phản chứng ở bản này: KL p.53 mục 11 và p.85 coi Tuần/Triệt là điều kiện thuận cho Nhật Nguyệt.")
# ---- Nhật lệ trung thiên --------------------------------------------------------------------------------------------------
variant(T + "NHAT_LE_TRUNG_THIEN", "kl", "52_85", "KL: Thái Dương ngọ, thích Xương Khúc, Khoa Quyền Lộc", ["TH72_NLTT", "KL52_NLTT", "KL85_NLTT"],
        keep={"boosters": ["khoa_quyen_hoi", "xuong_khuc_hoi"]},
        readings=["KL p.85 'thích' không nêu phạm vi; baseline đọc là hội trong tam phương"],
        note="Kỵ/Đà 'ghét' (KL p.85) không nêu phạm vi nên không đưa vào làm phá.")
# ---- Thạch trung ẩn ngọc: ba định nghĩa -----------------------------------------------------------------------------------------
variant(T + "THACH_TRUNG_AN_NGOC", "kl", "44", "KL tr.44: Mệnh Cự Môn, Di Thiên Cơ ở Tý/Ngọ", ["KL44_TTAN"],
        core=A(f("palace.branch", "in", ["Tý", "Ngọ"]), has("self", "majors", "Cự Môn"), has("opp", "majors", "Thiên Cơ")),
        note="Định nghĩa thứ nhất; không có yếu tố tăng thế/phá trong sách.")
variant(T + "THACH_TRUNG_AN_NGOC", "kl", "58", "KL tr.58 / TT tr.34: Cự Môn Tý/Ngọ được Khoa Quyền Lộc tam hợp chiếu", ["KL58_TTAN", "TT142_KQL"],
        readings=["'tam hợp chiếu' được mô hình là tam phương tứ chính (gồm cả đồng cung và đối cung)"],
        core=A(f("palace.branch", "in", ["Tý", "Ngọ"]), has("self", "majors", "Cự Môn"), f("palace.rel.tp_hoa", "contains_all", ["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"])),
        note="Định nghĩa thứ hai: Tam Hóa là điều kiện LÕI, không phải tăng thế.")
variant(T + "THACH_TRUNG_AN_NGOC", "kl", "106", "KL tr.106 / TH tr.43: Cự Môn Tý/Ngọ gặp Tuần/Triệt hoặc Hóa Lộc",
        ["KL106_TTAN", "TH43_TTAN"],
        core=A(f("palace.branch", "in", ["Tý", "Ngọ"]), has("self", "majors", "Cự Môn"),
               O(f("palace.tuan", "eq", True), f("palace.triet", "eq", True), has("self", "hoa", "Hóa Lộc"))),
        readings=["'gặp' Tuần/Triệt/Hóa Lộc được hiểu hẹp nhất là cùng cung Mệnh; sách không nêu phạm vi"],
        note="Định nghĩa thứ ba: Tuần/Triệt là điều kiện THUẬN — trái với baseline dùng Tuần/Triệt làm phản chứng.")
# ---- Mã đầu đới kiếm: hai kết cục trái nhau trong cùng KL p.64 ----------------------------------------------------------------
variant(T + "MA_DAU_DOI_KIEM", "kl", "64_xau", "KL tr.64 mục 5: Kình + Thất Sát, Thiên Hình đồng cung là cách xấu", ["KL64_MDDK_XAU", "KL60_MDDK_SAT"],
        keep={},
        add={"breakers": [ev("that_sat_thien_hinh_dong_cung", "Thất Sát và Thiên Hình đồng cung với Kình Dương (KL tr.64 mục 5)",
                             f("palace.rel.self_stars", "contains_all", ["Thất Sát", "Thiên Hình"]))]},
        note="Kết cục xấu của cùng thế Kình Dương ở Ngọ. TT p.142 coi Kình ở Ngọ là xấu mà 'tứ mộ mới hay': định nghĩa khác, chưa mô hình hóa.")
variant(T + "MA_DAU_DOI_KIEM", "kl", "64_tot", "KL tr.64 mục 6: Kình đồng cung, xa lánh Thất Sát/Thiên Hình, gặp Khoa Quyền Lộc là cách tốt", ["KL64_MDDK_TOT"],
        add={"boosters": [ev("khoa_quyen_loc_xa_sat_hinh", "Khoa, Quyền, Lộc hội chiếu và không có Thất Sát/Thiên Hình đồng cung (KL tr.64 mục 6)",
                             A(f("palace.rel.tp_hoa", "contains_all", ["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"]),
                               f("palace.rel.self_stars", "not_contains", "Thất Sát"), f("palace.rel.self_stars", "not_contains", "Thiên Hình")))]},
        readings=["'xa lánh' = không đồng cung; 'gặp Khoa Quyền Lộc' = hội chiếu cả ba (sách không nêu phạm vi rõ hơn)"],
        note="Đối lập với mục 5 cùng trang: hai bản được giữ tách, không gộp.")
# ---- Tam kỳ gia hội -------------------------------------------------------------------------------------------------------
variant(T + "TAM_KY_GIA_HOI", "kl", "66", "KL tr.66: Khoa Quyền Lộc hội họp mà Kỵ, Kình đồng cung hoặc chiếu", ["KL66_TKGH", "TT142_KQL"],
        add={"breakers": [ev("ky_kinh_dong_cung_hoac_doi_cung", "Hóa Kỵ hoặc Kình Dương đồng cung hay xung chiếu (đối cung) với Mệnh (KL tr.66)",
                             O(f("palace.rel.self_hoa", "contains", "Hóa Kỵ"), f("palace.rel.opp_hoa", "contains", "Hóa Kỵ"),
                               f("palace.rel.self_stars", "contains", "Kình Dương"), f("palace.rel.opp_stars", "contains", "Kình Dương")))]},
        readings=["'chiếu' được hiểu là xung chiếu (đối cung) — cách hẹp nhất cho chữ 'chiếu'; chưa mở ra toàn tam phương vì sách không nói"],
        note="Sửa lỗi lá số đối chứng Hạng Võ: Cự + Kỵ ở cung Di (đối cung của Mệnh).")
# ---- Khôi Việt giáp Mệnh --------------------------------------------------------------------------------------------------
variant(T + "KHOI_VIET_GIAP_MENH", "kl", "44_62", "KL: Mệnh giữa Khôi Việt; hội Xương Khúc tốt, sát tinh hội chiếu có bệnh", ["KL44_KVGM", "KL62_KV_XUONGKHUC", "KL62_KV_SAT"],
        keep={"boosters": ["xuong_khuc_hoi"]},
        add={"breakers": [ev("sat_tinh_hoi_chieu", "sát tinh hội chiếu (tam phương) cung Mệnh (KL tr.62 mục 4)", f("palace.khi.sat_tp", "gte", 1))]},
        readings=["'hội chiếu' của KL p.62 mục 4 = tam phương (từ ngữ hội chiếu đã xác định phạm vi)"],
        note="Kỵ/Thiên Hình 'cản phá' (mục 2) không nêu phạm vi nên không đưa vào.")

# ------------------------------------------------------------------------------------------------------------------------------


AUDIT = ROOT / "engine/data/experimental/formation_audit.json"
CHECKED = "doi_chieu_truc_tiep"       # this session compared the rule with the printed page (quote machine-checked); NOT a scholar's review
ASSUMING = "co_nguon_con_gia_dinh"   # a book speaks to it, but a scope/threshold reading or an unchecked (image) page is still assumed


def rule_levels(b, v, cites, audit):
    """per-rule (not per-formation) level. A rule is CHECKED only if every cited quote was machine-checked against the page text and the
    rule needs no scope reading of ours; kept baseline rules must additionally be 'khop' in the audit."""
    rows = {(r["formation"], r["role"], r["id"]): r for r in audit["rows"]}
    machine = all(c["read"] == "van_ban" and c.get("checked", True) for c in cites)
    out = {}

    def lvl(role, cid, kept):
        if kept:
            r = rows[(b["id"], role, cid)]
            return CHECKED if r["status"] == "khop" and r["machine_checked"] and not v["readings"] else ASSUMING
        return CHECKED if machine and not v["readings"] else ASSUMING

    out["core"] = lvl("core", "core", v["core"] is None)
    for role in ("boosters", "breakers", "refutations"):
        for c in b[role]:
            if c["id"] in v["keep"].get(role, []):
                out[f"{role}.{c['id']}"] = lvl(role, c["id"], True)
        for c in v["add"].get(role, []):
            out[f"{role}.{c['id']}"] = lvl(role, c["id"], False)
    return out


def build():
    audit = json.load(open(AUDIT, encoding="utf-8"))
    base = {x["id"]: x for x in json.load(open(BASE, encoding="utf-8"))["formations"]}
    out, meta = [], {}
    for v in V:
        b = base[v["base"]]
        vid = f"{b['id']}@{v['school']}_{v['page']}"
        d = {k: b[k] for k in ("name_vi", "anchor")}
        d.update(id=vid, core=v["core"] or b["core"], kind="cat", school=f"nguon_{v['school']}_draft",
                 thuong_at=b.get("thuong_at", 2), sourceIds=[], reviewStatus="draft", experimental=True,
                 definition_version=1, provenance=f"Biến thể theo {SCHOOL_VI[v['school']]}: {v['title']}. Đối chiếu trang sách đọc trực tiếp (xem formation_audit.json).",
                 note=v["note"])
        d["name_vi"] = f"{b['name_vi']} — {SCHOOL_VI[v['school']]} ({v['title']})"
        kept, dropped = {}, []
        for role in ("boosters", "breakers", "rescuers", "refutations"):
            items = [dict(c) for c in b[role] if c["id"] in v["keep"].get(role, [])]
            items += v["add"].get(role, [])
            d[role] = items
            kept[role] = [c["id"] for c in items]
            dropped += [{"role": role, "id": c["id"], "reason": "baseline chưa có nguồn đúng vai trò này trong bản " + SCHOOL_VI[v["school"]] + " (xem audit); chỉ còn ở giả thuyết gốc"}
                        for c in b[role] if c["id"] not in v["keep"].get(role, [])]
        cites = []
        for q in v["cites"]:
            book, page, quote, method = au.Q[q]
            cites.append({"id": q, "book": au.bt.BOOK_NAMES[book], "book_code": book, "page": page, "quote": quote, "read": method})
        meta[vid] = {"base": b["id"], "school": v["school"], "school_vi": SCHOOL_VI[v["school"]], "title": v["title"], "cites": cites,
                     "readings": v["readings"], "kept": kept, "dropped": dropped, "core_replaced": v["core"] is not None,
                     "rescuers": "không có: không nguồn nào nói sao nào cứu cách nào",
                     "rules": rule_levels(b, v, cites, audit),
                     "reviewer": "đối chiếu trang sách bởi phiên AI; chưa có thẩm định của chuyên gia Tử Vi"}
        out.append(d)
    return out, meta


if __name__ == "__main__":
    fs, meta = build()
    OUT.write_text(json.dumps({"version": 1, "note": "Biến thể theo nguồn/trường phái; draft, không vào luận giải chính; không hợp nhất định nghĩa mâu thuẫn.",
                               "formations": fs, "meta": meta}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(fs), "variants ->", OUT)
