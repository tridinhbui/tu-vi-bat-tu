"""Generates data/pack_khao_luan_cases.json: general principles that Tử Vi Khảo Luận pp.237-246 states while reading its worked example charts
(can-chi relation of the birth year, Mệnh on a palace of its own polarity, sex vs year polarity, tứ chính birth years, Mệnh at Tứ mộ, and a few
star-in-palace readings). Paraphrased with page cites. The book's death/illness/accident remarks inside those examples are not encoded."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPS = "palace.own_stars", "palace.own_major_stars", "palace.rel.tp_stars"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
eq = lambda f, v: {"fact": f, "value": v}
anyof = lambda *x: {"any": list(x)}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}
TUMO = ("Thìn", "Tuất", "Sửu", "Mùi")
GOOD = ["miếu", "vượng", "đắc"]
R = []
def add(pal, rid, conds, claim, status, page, phrase, effect="support"):
    R.append((pal, rid, conds, [(claim, effect)] if isinstance(claim, str) else claim, status, page, phrase))
M = "Mệnh"
add(M, "GOC_NUOI_NGON", [eq("chart.can_chi_relation", "can_sinh_chi")], "kl_goc_nuoi_ngon_huong_phuc_sau", "verified", "p.244", "gốc nuôi ngọn: được hưởng phúc về sau (Can năm sinh sinh Chi năm sinh)")
add(M, "NGON_NUOI_GOC", [eq("chart.can_chi_relation", "chi_sinh_can")], "kl_ngon_nuoi_goc_phuc_khong_ben", "verified", "p.238", "ngọn nuôi gốc là nghịch lý, phúc không được lâu dài (Chi năm sinh sinh Can)", "limit")
add(M, "GOC_PHA_NGON", [eq("chart.can_chi_relation", "can_khac_chi")], "kl_goc_pha_ngon_phuc_khong_lau", "verified", "p.242", "gốc phá ngọn: không hưởng phúc lâu dài (Can năm sinh khắc Chi năm sinh)", "limit")
add(M, "DAC_CHINH_AM", [eq("chart.menh_dac_chinh", True), eq("chart.year_polarity", "âm")], "kl_menh_am_cung_am_mem_deo", "verified", "p.240", "mềm dẻo, khôn khéo (Mệnh âm đóng cung âm: đắc chính)")
add(M, "DAC_CHINH_DUONG", [eq("chart.menh_dac_chinh", True), eq("chart.year_polarity", "dương")], "kl_menh_duong_cung_duong_dac_chinh", "verified", "p.238", "đúng chỗ của mình (Mệnh dương đóng cung dương: đắc chính)")
add(M, "KHONG_DAC_CHINH", [eq("chart.menh_dac_chinh", False)], "kl_menh_khong_dac_chinh_tro_ngai_ban_dau", "verified", "p.244", "ra đời gặp trở ngại, khó khăn lúc ban đầu vì chưa đúng chỗ của mình (Mệnh âm ở cung dương hoặc Mệnh dương ở cung âm)", "limit")
add(M, "CUC_KHAC_MENH", [eq("chart.menh_cuc_relation", "Cục khắc Mệnh")], "kl_cuc_khac_menh_tro_ngai", "verified", "p.238", "dễ gặp trở ngại trên đường đời (Cục khắc Mệnh)", "limit")
add(M, "AM_NU", [eq("chart.year_polarity", "âm"), eq("chart.gender", "nữ")], "kl_am_nu_lo_su_nghiep_som", "verified", "p.244", "lo sự nghiệp, tiền bạc sớm, ít màng đến công danh (nữ tuổi âm, thuận lý âm dương)")
add(M, "TU_CHINH", [{"fact": "chart.year_branch", "operator": "in", "value": ["Tý", "Ngọ", "Mão", "Dậu"]}], "kl_tuoi_tu_chinh_trach_nhiem_cao", "verified", "p.244", "tinh thần trách nhiệm cao, luôn lo giữ uy tín (tuổi Tý, Ngọ, Mão, Dậu nằm trong tứ chính)")
add(M, "TU_MO", [br(*TUMO)], "kl_menh_tu_mo_phai_gianh_cho_dung", "verified", "p.244", "phải cố gắng giành một chỗ đứng trong xã hội, nên khiêm nhường khéo léo để vươn lên (Mệnh ở Tứ mộ, đất tối hơn các cung khác)", "limit")
add(M, "AM_HAM_QUYEN", [has(OWNM, "Thái Âm"), dig("Thái Âm", ["hãm"]), has("palace.tu_hoa", "Hóa Quyền")], "kl_am_ham_quyen_su_nghiep_khong_ben", "verified", "p.246", "có sự nghiệp nhưng không bền: có quyền khi có tiền, hết tiền thì hết quyền (Thái Âm hãm hóa Quyền ở Mệnh)", "limit")
add(M, "NHAT_LUONG_MAO", [has(OWNM, "Thái Dương"), has(OWNM, "Thiên Lương"), br("Mão")], "kl_nhat_xuat_phu_tang", "verified", "p.240", "cách Nhật xuất phù tang (Thái Dương, Thiên Lương đắc địa ở Mão), sang quý")
add("Tài Bạch", "NHAT_LUONG_MAO", [has(OWNM, "Thái Dương"), has(OWNM, "Thiên Lương"), br("Mão"), eq("palace.is_than", True)], "kl_nhat_xuat_phu_tang_than_cu_tai", "verified", "p.240", "cách Nhật xuất phù tang (Thân cư Tài ở Mão có Thái Dương, Thiên Lương đắc địa), sang quý")
add(M, "VCD_NN_TA_HUU", [{"fact": "palace.has_no_major", "value": True}, has("palace.rel.tp_majors", "Thái Dương"), has("palace.rel.tp_majors", "Thái Âm"), has(OWN, "Tả Phụ"), has(OWN, "Hữu Bật")], "kl_vcd_nhat_nguyet_chieu_ta_huu_tai_ba", "draft", "p.240", "thông minh, tài ba xuất chúng, được kính nể (Mệnh vô chính diệu có Nhật Nguyệt chiếu, Tả Hữu đồng cung); sách còn nói người sinh tháng 4 và cô đơn vì Cô Quả")
add("Phụ Mẫu", "TU_SAT", [has(OWNM, "Tử Vi"), has(OWNM, "Thất Sát")], [("kl_tu_sat_phu_som_thoat_ly_lap_nghiep", "support"), ("kl_tu_sat_phu_de_hao_tai_bat_ngo", "limit")], "verified", "p.244", "sớm rời gia đình lập nghiệp từ nhỏ, có dịp làm giàu nhanh nhưng cũng dễ hao tài đột ngột (Tử Vi, Thất Sát ở Phụ Mẫu)")
add("Tử Tức", "TU_PHA_TRIET", [has(OWNM, "Tử Vi"), has(OWNM, "Phá Quân"), eq("palace.triet", True)], "kl_tu_pha_triet_giao_thiep_gioi_bao_ton", "verified", "p.246", "cả đời phải giao thiệp với giới làm ăn bạo tợn, hay vô ơn (Tử Phá ở Tử Tức gặp Triệt)", "limit")
add("Tài Bạch", "THAN", [eq("palace.is_than", True)], "kl_than_cu_tai_tien_bac_la_moi_lo_chinh", "verified", "p.246", "tiền bạc là mối lo chính của cuộc đời (Thân cư Tài Bạch)", "limit")
add("Tài Bạch", "THAI_TUE", [has(OWN, "Thái Tuế")], "kl_tai_thai_tue_tranh_chap_kien_tung", "verified", "p.246", "dễ có tranh chấp, kiện tụng liên quan đến tiền bạc (Thái Tuế ở Tài Bạch)", "limit")
add("Tài Bạch", "CO_KY_HOA_LINH", [has(OWNM, "Thiên Cơ"), has("palace.tu_hoa", "Hóa Kỵ"), anyof(has(TPS, "Hỏa Tinh"), has(TPS, "Linh Tinh"))], "kl_co_ky_hoa_linh_tai_tan", "verified", "p.246", "dễ tranh chấp lớn và hao tán tiền bạc (Thiên Cơ hóa Kỵ gặp Hỏa, Linh ở Tài Bạch)", "limit")
add("Tài Bạch", "DONG_LUONG_TRIET_KIEP", [has(OWNM, "Thiên Đồng"), has(OWNM, "Thiên Lương"), eq("palace.triet", True), has(OWN, "Địa Kiếp")], "kl_dong_luong_triet_kiep_su_nghiep_khong_ben", "verified", "p.238", "khó giữ được sự nghiệp lâu dài dù có Tướng, Ấn (Đồng Lương ở Tài Bạch gặp Triệt và Địa Kiếp)", "limit")
add("Tài Bạch", "VU_TUONG_LOC", [has(OWNM, "Vũ Khúc"), has(OWNM, "Thiên Tướng"), has(OWN, "Lộc Tồn")], "kl_vu_tuong_loc_giau_ben_vung", "draft", "p.237", "giàu sang bền vững (Vũ Tướng, Lộc Tồn ở Tài Bạch); sách còn kể Đẩu Quân, sao chưa được kiểm")
add("Quan Lộc", "AM_TUAN", [has(OWNM, "Thái Âm"), dig("Thái Âm", GOOD), eq("palace.tuan", True)], "kl_quan_am_dac_dia_gap_tuan_lui_tan", "verified", "p.238", "sự nghiệp đáng lẽ tốt đẹp lại lụi tàn như trăng sáng bị mây che (Thái Âm đắc địa ở Quan Lộc gặp Tuần)", "limit")
add("Quan Lộc", "LIEM_PHU_QUAN_PHU", [has(OWNM, "Liêm Trinh"), has(OWNM, "Thiên Phủ"), has(OWN, "Quan Phù")], "kl_liem_phu_quan_phu_than_trong_uy_tin", "verified", "p.237", "thận trọng, có uy tín với mọi người xung quanh (Liêm Phủ, Quan Phù ở Quan Lộc)")
add("Quan Lộc", "AM_HOI", [has(OWNM, "Thái Âm"), br("Hợi")], "kl_thiem_cung_chiet_que", "verified", "p.241", "cách Thiềm cung chiết quế, sang quý (Thái Âm đắc địa ở Hợi tại Quan Lộc)")

slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for pal, rid, conds, cl, status, loc, vi in R:
    rules.append({"id": f"TV_KL_CASE_{slug(pal)}_{rid}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "kl_cases",
        "description": f"Tử Vi Khảo Luận, nguyên tắc nêu trong các lá số mẫu (paraphrased), cung {pal}: {vi} [KL {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": c, "effect": e, "scope": "natal"} for c, e in cl],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_KHAO_LUAN"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    for c, e in cl:
        claims.setdefault(c, ("khuynh hướng " if e == "support" else "hạn chế: ") + vi)
        if e == "limit":
            claims.setdefault("limit:" + c, "hạn chế: " + vi)
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_khao_luan_cases.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
