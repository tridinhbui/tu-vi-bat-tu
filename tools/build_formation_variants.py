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


def variant(base, school, page, title, rules, keep=None, add=None, core=None, note="", name_vi=None):
    """rules: {"core"|"<role>.<id>": (cite ids, assumption text or None[, forced level])} — every rule of the variant must have an entry."""
    cites = list(dict.fromkeys(c for r in rules.values() for c in r[0]))
    readings = list(dict.fromkeys(r[1] for r in rules.values() if r[1]))
    V.append(dict(base=base, school=school, page=page, title=title, cites=cites, keep=keep or {}, add=add or {}, core=core,
                  readings=readings, rules=rules, note=note, name_vi=name_vi))


T = "CACH_X_"
# ---- Tử Phủ Vũ Tướng ------------------------------------------------------------------------------------------------------
TP4 = "4 sao trong tam phương của Mệnh là cách mô hình hóa; sách chỉ nêu tên cách, không nêu vị trí"
ANCHOR = "TH tr.72 cho phép đóng ở Mệnh hay Thân; mô hình chỉ neo ở Mệnh"
HAT = "phạm vi hội của sao không được câu sách nêu; đọc là tam phương"
variant(T + "TU_PHU_VU_TUONG", "kl", "132_193", "KL: cần Tả Hữu, Xương Khúc",
        rules={"core": (["TH72_TPVT"], TP4), "boosters.ta_huu_hoi": (["KL132_TPVT_TAHUU"], HAT),
               "boosters.xuong_khuc_hoi": (["KL193_TPVT_XK"], HAT + "; sách nói Xương Khúc, baseline chấp nhận một trong hai"),
               "refutations.tuan_triet_an_ngu": (["KL222_VT_TUAN"], "KL tr.222 nói về Vũ Tướng; áp cho cả cách là mở rộng")},
        keep={"boosters": ["ta_huu_hoi", "xuong_khuc_hoi"], "refutations": ["tuan_triet_an_ngu"]},
        note="KL nói Tử Phủ Vũ Tướng cần Tả Hữu, Xương Khúc và sợ Tuần/Triệt. Sát tinh/Kỵ làm phá chỉ được TH p.116 nói trong ngữ cảnh đại tiểu hạn nên không đưa vào bản này.")
variant(T + "TU_PHU_VU_TUONG", "th", "115", "TH: gặp Lộc, Tả Hữu (đại tiểu hạn)",
        rules={"core": (["TH72_TPVT"], TP4), "boosters.loc_hoi": (["TH115_TPVT"], "TH tr.115 nói về đại tiểu hạn, không về bản cách; " + HAT),
               "boosters.ta_huu_hoi": (["TH115_TPVT"], "TH tr.115 nói về đại tiểu hạn, không về bản cách; " + HAT),
               "refutations.tuan_triet_an_ngu": (["TH94_PHU", "TH95_TUONG"], "TH tr.94-95 nói về từng sao Phủ/Tướng, không về cả cách")},
        keep={"boosters": ["loc_hoi", "ta_huu_hoi"], "refutations": ["tuan_triet_an_ngu"]},
        note="Phá cách (Tam Không, Kiếp, Kỵ, Hình, Đà, Linh Hỏa) có ở TH p.116 nhưng là 'gặp' trong hạn nên chưa mô hình hóa.")
variant(T + "TU_PHU_DONG_CUNG", "tt", "22", "TT: vô sát tấu mới hưởng phúc",
        rules={"core": (["TH72_TPDC", "TT22_TPDC_SAT"], ANCHOR + "; TT tr.22 còn nhắc Tỵ/Hợi mà mô hình không có Tử Phủ đồng cung ở đó"),
               "breakers.sat_dong_cung": (["TT22_TPDC_SAT"], "'gặp sát tinh' đọc là đồng cung (cách hẹp nhất); tập sáu sát tinh là của baseline"),
               "refutations.tuan_triet_an_ngu": (["KL55_TP_TUAN"], "nguồn là KL, không phải TT; TT tr.22/tr.160 cùng ý 'hiềm Triệt Tuần' nhưng chưa trích")},
        keep={"breakers": ["sat_dong_cung"], "refutations": ["tuan_triet_an_ngu"]},
        note="Đối lập với bản KL p.50. Hai bản KHÔNG được hợp nhất: TT coi sát tinh là phá, KL coi Kình Dương đồng cung vẫn giàu.")
variant(T + "TU_PHU_DONG_CUNG", "kl", "50", "KL: Kình Dương hoặc Kỵ + Quyền đồng cung vẫn tốt",
        rules={"core": (["TH72_TPDC", "KL55_TP_TUAN"], ANCHOR), "boosters.kinh_luc_si_dong_cung": (["KL50_TP_KINH"], None),
               "boosters.ky_quyen_dong_cung": (["KL50_TP_KY"], None), "refutations.tuan_triet_an_ngu": (["KL55_TP_TUAN"], None)},
        keep={"refutations": ["tuan_triet_an_ngu"]},
        add={"boosters": [ev("kinh_luc_si_dong_cung", "Kình Dương và Lực Sĩ đồng cung với Tử Phủ (buôn bán giàu có, KL tr.50)",
                             f("palace.rel.self_stars", "contains_all", ["Kình Dương", "Lực Sĩ"])),
                          ev("ky_quyen_dong_cung", "Mệnh ở Dần có Hóa Kỵ và Hóa Quyền đồng cung với Tử Phủ (mưu cơ tài trí, KL tr.50)",
                             A(f("palace.branch", "eq", "Dần"), f("palace.rel.self_hoa", "contains_all", ["Hóa Kỵ", "Hóa Quyền"])))]},
        note="Ngược với TT p.22: ở đây Kình Dương/Kỵ đồng cung là yếu tố tăng thế, không phải phá.")
variant(T + "CO_NGUYET_DONG_LUONG", "tt", "24", "TT: Kiếp, Không, Hóa Kị trong tam hợp xung chiếu thì hạ cách",
        rules={"core": (["TT24_CNDL_CORE"], "TT tr.24 cho Mệnh hoặc Thân; mô hình chỉ neo ở Mệnh"),
               "boosters.cat_tinh_hoi": (["TT24_CNDL_CORE", "TH77_CNDL"], "tập sáu cát tinh và phạm vi hội là của baseline; sách chỉ nói 'cát tinh trợ lực'"),
               "breakers.khong_kiep_trong_tam_phuong": (["TT24_CNDL_BREAK"], "câu liệt kê Kiếp, Không, Kị; hiểu là một trong số đó là đủ"),
               "breakers.ky_trong_tam_phuong": (["TT24_CNDL_BREAK"], "câu liệt kê Kiếp, Không, Kị; hiểu là một trong số đó là đủ")},
        keep={"boosters": ["cat_tinh_hoi"]},
        add={"breakers": [ev("khong_kiep_trong_tam_phuong", "Địa Không hoặc Địa Kiếp trong tam phương của Mệnh (TT tr.24)",
                             f("palace.rel.tp_stars", "contains_any", ["Địa Không", "Địa Kiếp"])),
                          ev("ky_trong_tam_phuong", "Hóa Kỵ trong tam phương của Mệnh (TT tr.24)", has("tp", "hoa", "Hóa Kỵ"))]},
        note="Sửa lỗi lá số đối chứng Hạng Võ / Mậu Tý: baseline chỉ tính đồng cung Mệnh. Phạm vi tam phương do chính câu TT tr.24 nêu ('các cung tam hợp xung chiếu'). Tuần/Triệt không được TT p.24 nêu nên không là phá.")
variant(T + "CO_NGUYET_DONG_LUONG", "kl", "221", "KL: hội Tả Hữu Quang Quý / Khoa Quyền Lộc, Khôi Việt, Xương Khúc",
        rules={"core": (["KL51_CNDL"], "KL tr.51 chỉ nói 'hội chiếu'; mô hình neo ở Mệnh, tam phương"),
               "boosters.cat_tinh_hoi": (["KL221_CNDL_CAT"], "tập sáu cát tinh của baseline khác danh sách của KL (Tả Hữu Quang Quý Thiên quan); phạm vi hội không nêu"),
               "boosters.khoa_quyen_loc_hoi": (["KL221_CNDL_KQL"], "chữ 'Khoa' mất ở lớp chữ của trang (đọc bổ sung từ ảnh); phạm vi hội không nêu")},
        keep={"boosters": ["cat_tinh_hoi", "khoa_quyen_loc_hoi"]},
        note="KL không nêu yếu tố phá cho CNDL, nên bản này không có breaker.")
variant(T + "SAT_PHA_LIEM_THAM", "th", "76_77", "TH: hội cát tinh (Khoa Quyền Lộc) / hạ cách khi nhiều sát tinh",
        rules={"core": (["TH72_SPLT"], "tên cách ở TH tr.72 đọc từ ảnh; ngưỡng 3 trong 4 sao là quy ước thiết kế", "chua_du_nguon"),
               "boosters.khoa_quyen_hoi": (["TH76_CATTINH"], "sách đòi Khoa Quyền Lộc, baseline chấp nhận Khoa hoặc Quyền; phạm vi hội không nêu"),
               "breakers.ba_sat_va_ky_trong_tam_phuong": (["TH77_SPLT_HA", "TH116_SPLT"], "'nhiều' sát tinh → ngưỡng 3 sát tinh + Hóa Kỵ là quy ước thiết kế", "chua_du_nguon")},
        keep={"boosters": ["khoa_quyen_hoi"], "breakers": ["ba_sat_va_ky_trong_tam_phuong"]},
        note="TH p.76 lại xếp Kình, Không vào nhóm cát hội của Thân Sát Phá Liêm Tham: bất đồng nội bộ TH, ghi nhận trong ma trận.")
variant(T + "NHAT_NGUYET_TINH_MINH", "th", "72", "TH: vị trí cố định (Nhật Thìn/Tỵ, Nguyệt Dậu/Tuất, Mệnh ở Nhật hay Nguyệt)",
        rules={"core": (["TH72_NNTM"], None), "boosters.nhat_nguyet_deu_sang": (["TT142_NNTM"], "nguồn là TT ('miếu vượng'); baseline dùng ngưỡng từ đắc trở lên"),
               "breakers.nhat_nguyet_ham_gap_sat": (["TH74_NN_TAN_HUNG"], "trang TH tr.74 đọc từ ảnh; tập sáu sát tinh và phạm vi tam phương là của baseline", "chua_du_nguon")},
        core=O(A(f("palace.branch", "eq", "Thìn"), has("self", "majors", "Thái Dương"), has("opp", "majors", "Thái Âm")),
               A(f("palace.branch", "eq", "Tuất"), has("self", "majors", "Thái Âm"), has("opp", "majors", "Thái Dương")),
               A(f("palace.branch", "eq", "Tỵ"), has("self", "majors", "Thái Dương"), has("trine1", "majors", "Thái Âm")),
               A(f("palace.branch", "eq", "Dậu"), has("self", "majors", "Thái Âm"), has("trine2", "majors", "Thái Dương"))),
        keep={"boosters": ["nhat_nguyet_deu_sang"], "breakers": ["nhat_nguyet_ham_gap_sat"]},
        note="Định nghĩa theo vị trí của TH p.72; hẹp hơn bản KL p.53 (hợp chiếu tịnh minh).")
variant(T + "NHAT_NGUYET_TINH_MINH", "kl", "53_68", "KL: Nhật Nguyệt hợp chiếu Mệnh, hãm cần Khôi Việt chiếu",
        rules={"core": (["KL53_NN_TINHMINH"], "'hợp chiếu' mô hình là cả hai sao trong tam phương"),
               "boosters.nhat_nguyet_deu_sang": (["KL53_NN_TINHMINH"], "KL nói 'đắc địa'; baseline ngưỡng từ đắc trở lên"),
               "breakers.nhat_nguyet_ham_gap_sat": (["KL56_NN_HAM"], "KL liệt kê Kình Đà Không Kiếp; baseline dùng sáu sát tinh; 'gặp' không nêu phạm vi"),
               "refutations.nhat_nguyet_ham_khong_khoi_viet": (["KL68_NN_KHOIVIET"], "'Khôi Việt chiếu' đọc là hội chiếu tam phương")},
        keep={"boosters": ["nhat_nguyet_deu_sang"], "breakers": ["nhat_nguyet_ham_gap_sat"]},
        add={"refutations": [ev("nhat_nguyet_ham_khong_khoi_viet", "Nhật hoặc Nguyệt hãm mà không có Khôi/Việt chiếu (KL tr.68)",
                                A(O(f("palace.tp_rank.Thái Dương", "lte", 0), f("palace.tp_rank.Thái Âm", "lte", 0)),
                                  f("palace.rel.tp_stars", "not_contains", "Thiên Khôi"), f("palace.rel.tp_stars", "not_contains", "Thiên Việt")))]},
        note="Tuần/Triệt KHÔNG là phản chứng ở bản này: KL p.53 mục 11 và p.85 coi Tuần/Triệt là điều kiện thuận cho Nhật Nguyệt.")
variant(T + "NHAT_LE_TRUNG_THIEN", "kl", "52_85", "KL: Thái Dương ngọ, thích Xương Khúc, Khoa Quyền Lộc",
        rules={"core": (["TH72_NLTT", "KL52_NLTT"], None),
               "boosters.khoa_quyen_hoi": (["KL85_NLTT"], "'thích' không nêu phạm vi; sách kể Khoa Quyền Lộc, baseline chấp nhận Khoa hoặc Quyền"),
               "boosters.xuong_khuc_hoi": (["KL85_NLTT"], "'thích' không nêu phạm vi; đọc là tam phương")},
        keep={"boosters": ["khoa_quyen_hoi", "xuong_khuc_hoi"]},
        note="Kỵ/Đà 'ghét' (KL p.85) không nêu phạm vi nên không đưa vào làm phá.")
variant(T + "THACH_TRUNG_AN_NGOC", "kl", "44", "KL tr.44: Mệnh Cự Môn, Di Thiên Cơ ở Tý/Ngọ",
        rules={"core": (["KL44_TTAN"], None)},
        core=A(f("palace.branch", "in", ["Tý", "Ngọ"]), has("self", "majors", "Cự Môn"), has("opp", "majors", "Thiên Cơ")),
        note="Định nghĩa thứ nhất; không có yếu tố tăng thế/phá trong sách.")
variant(T + "THACH_TRUNG_AN_NGOC", "kl", "58", "KL tr.58 / TT tr.34: Cự Môn Tý/Ngọ được Khoa Quyền Lộc tam hợp chiếu",
        rules={"core": (["KL58_TTAN", "TT142_KQL"], "'tam hợp chiếu' được mô hình là tam phương tứ chính (gồm cả đồng cung và đối cung)")},
        core=A(f("palace.branch", "in", ["Tý", "Ngọ"]), has("self", "majors", "Cự Môn"), f("palace.rel.tp_hoa", "contains_all", ["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"])),
        note="Định nghĩa thứ hai: Tam Hóa là điều kiện LÕI, không phải tăng thế.")
variant(T + "THACH_TRUNG_AN_NGOC", "kl", "106", "KL tr.106 / TH tr.43: Cự Môn Tý/Ngọ gặp Tuần/Triệt hoặc Hóa Lộc",
        rules={"core": (["KL106_TTAN", "TH43_TTAN"], "'gặp' Tuần/Triệt/Hóa Lộc được hiểu hẹp nhất là cùng cung Mệnh; sách không nêu phạm vi")},
        core=A(f("palace.branch", "in", ["Tý", "Ngọ"]), has("self", "majors", "Cự Môn"),
               O(f("palace.tuan", "eq", True), f("palace.triet", "eq", True), has("self", "hoa", "Hóa Lộc"))),
        note="Định nghĩa thứ ba: Tuần/Triệt là điều kiện THUẬN — trái với baseline dùng Tuần/Triệt làm phản chứng.")
variant(T + "MA_DAU_DOI_KIEM", "kl", "64_xau", "KL tr.64 mục 5: Kình + Thất Sát, Thiên Hình đồng cung là cách xấu",
        rules={"core": (["KL64_MDDK_XAU"], None), "breakers.that_sat_thien_hinh_dong_cung": (["KL64_MDDK_XAU"], None)},
        add={"breakers": [ev("that_sat_thien_hinh_dong_cung", "Thất Sát và Thiên Hình đồng cung với Kình Dương (KL tr.64 mục 5)",
                             f("palace.rel.self_stars", "contains_all", ["Thất Sát", "Thiên Hình"]))]},
        note="Kết cục xấu của cùng thế Kình Dương ở Ngọ. TT p.142 coi Kình ở Ngọ là xấu mà 'tứ mộ mới hay': định nghĩa khác, chưa mô hình hóa.")
variant(T + "MA_DAU_DOI_KIEM", "kl", "64_tot", "KL tr.64 mục 6: Kình đồng cung, xa lánh Thất Sát/Thiên Hình, gặp Khoa Quyền Lộc là cách tốt",
        rules={"core": (["KL64_MDDK_TOT"], None),
               "boosters.khoa_quyen_loc_xa_sat_hinh": (["KL64_MDDK_TOT"], "'xa lánh' = không đồng cung; 'gặp Khoa Quyền Lộc' = hội chiếu cả ba; sách không nêu phạm vi rõ hơn")},
        add={"boosters": [ev("khoa_quyen_loc_xa_sat_hinh", "Khoa, Quyền, Lộc hội chiếu và không có Thất Sát/Thiên Hình đồng cung (KL tr.64 mục 6)",
                             A(f("palace.rel.tp_hoa", "contains_all", ["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"]),
                               f("palace.rel.self_stars", "not_contains", "Thất Sát"), f("palace.rel.self_stars", "not_contains", "Thiên Hình")))]},
        note="Đối lập với mục 5 cùng trang: hai bản được giữ tách, không gộp.")
variant(T + "TAM_KY_GIA_HOI", "kl", "66", "KL tr.66: Khoa Quyền Lộc hội họp mà Kỵ, Kình đồng cung hoặc chiếu",
        rules={"core": (["KL66_TKGH", "TT142_KQL"], "'hội họp' mô hình là cả ba Hóa trong tam phương"),
               "breakers.ky_kinh_dong_cung_hoac_doi_cung": (["KL66_TKGH"], "'chiếu' được hiểu là xung chiếu (đối cung) — cách hẹp nhất cho chữ 'chiếu'; chưa mở ra toàn tam phương vì sách không nói")},
        add={"breakers": [ev("ky_kinh_dong_cung_hoac_doi_cung", "Hóa Kỵ hoặc Kình Dương đồng cung hay xung chiếu (đối cung) với Mệnh (KL tr.66)",
                             O(f("palace.rel.self_hoa", "contains", "Hóa Kỵ"), f("palace.rel.opp_hoa", "contains", "Hóa Kỵ"),
                               f("palace.rel.self_stars", "contains", "Kình Dương"), f("palace.rel.opp_stars", "contains", "Kình Dương")))]},
        note="Sửa lỗi lá số đối chứng Hạng Võ: Cự + Kỵ ở cung Di (đối cung của Mệnh).")
variant(T + "KHOI_VIET_GIAP_MENH", "kl", "44_62", "KL: Mệnh giữa Khôi Việt; hội Xương Khúc tốt, sát tinh hội chiếu có bệnh",
        rules={"core": (["KL44_KVGM"], None),
               "boosters.xuong_khuc_hoi": (["KL62_KV_XUONGKHUC"], "KL nói 'đồng cung hay hội chiếu' cùng Lộc Tồn; baseline tam phương, không đòi Lộc Tồn"),
               "breakers.sat_tinh_hoi_chieu": (["KL62_KV_SAT"], "'hội chiếu' = tam phương (từ ngữ đã xác định phạm vi); tập sát tinh sáu sao là của baseline")},
        keep={"boosters": ["xuong_khuc_hoi"]},
        add={"breakers": [ev("sat_tinh_hoi_chieu", "sát tinh hội chiếu (tam phương) cung Mệnh (KL tr.62 mục 4)", f("palace.khi.sat_tp", "gte", 1))]},
        note="Kỵ/Thiên Hình 'cản phá' (mục 2) không nêu phạm vi nên không đưa vào.")

# ------------------------------------------------------------------------------------------------------------------------------


AUDIT = ROOT / "engine/data/experimental/formation_audit.json"
CHECKED = "doi_chieu_truc_tiep"       # this session compared the rule with the printed page (quote machine-checked); NOT a scholar's review
ASSUMING = "co_nguon_con_gia_dinh"   # a book speaks to it, but a scope/threshold reading or an unchecked (image) page is still assumed


NOSRC = "chua_du_nguon"              # image-only page, design convention, or the baseline rule is only 'liên quan'/'không có nguồn' for this role


def rule_levels(b, v, cite_info, audit):
    """per-rule level, from the rule's OWN cites and assumption (never from the variant as a whole)."""
    rows = {(r["formation"], r["role"], r["id"]): r for r in audit["rows"]}
    keys = ["core"] + [f"{role}.{c['id']}" for role in ("boosters", "breakers", "refutations")
                       for c in b[role] if c["id"] in v["keep"].get(role, [])] + \
           [f"{role}.{c['id']}" for role in ("boosters", "breakers", "refutations") for c in v["add"].get(role, [])]
    assert set(keys) == set(v["rules"]), (b["id"], v["page"], sorted(set(keys) ^ set(v["rules"])))
    out, detail = {}, {}
    for key in keys:
        spec = v["rules"][key]
        ids, assumption = spec[0], spec[1]
        forced = spec[2] if len(spec) > 2 else None
        cs = [cite_info[i] for i in ids]
        role, cid = ("core", "core") if key == "core" else key.split(".", 1)
        kept = (role == "core" and v["core"] is None) or (role != "core" and cid in v["keep"].get(role, []))
        arow = rows.get((b["id"], role, cid)) if kept else None
        if forced:
            level = forced
        elif any(c["read"] != "van_ban" for c in cs):
            level = NOSRC
        elif arow and arow["status"] in ("lien_quan", "khong_co_nguon"):
            level = NOSRC
        elif assumption or (arow and arow["status"] != "khop"):
            level = ASSUMING
        else:
            level = CHECKED
        out[key] = level
        detail[key] = {"level": level, "cites": ids, "assumption": assumption, "audit_status": arow["status"] if arow else "viet_moi_tu_trang_sach"}
    return out, detail


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
        levels, detail = rule_levels(b, v, {c["id"]: c for c in cites}, audit)
        meta[vid] = {"base": b["id"], "school": v["school"], "school_vi": SCHOOL_VI[v["school"]], "title": v["title"], "cites": cites,
                     "readings": v["readings"], "kept": kept, "dropped": dropped, "core_replaced": v["core"] is not None,
                     "rescuers": "không có: không nguồn nào nói sao nào cứu cách nào",
                     "rules": levels, "rule_detail": detail,
                     "reviewer": "đối chiếu trang sách bởi phiên AI; chưa có thẩm định của chuyên gia Tử Vi"}
        out.append(d)
    return out, meta


if __name__ == "__main__":
    fs, meta = build()
    OUT.write_text(json.dumps({"version": 1, "note": "Biến thể theo nguồn/trường phái; draft, không vào luận giải chính; không hợp nhất định nghĩa mâu thuẫn.",
                               "formations": fs, "meta": meta}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(fs), "variants ->", OUT)
