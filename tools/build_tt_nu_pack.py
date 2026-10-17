"""Generates data/pack_toan_thu_nu.json: the positive readings of the 'Nữ mệnh ca' of Tử Vi Đẩu Số Toàn Thư pp.108-113 (female charts only).
The book's lines on adultery, 'khắc phu / khắc tử', concubinage and early death are deliberately not encoded."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}
OM = lambda s: has("palace.own_major_stars", s)
O = lambda s: has("palace.own_stars", s)
CAT = {"fact": "palace.khi.cat_tp", "operator": "gte", "value": 1}
NOSAT = {"fact": "palace.khi.sat_tp", "operator": "lte", "value": 0}
HOA = lambda h: has("palace.rel.tp_hoa", h)
NU = {"fact": "chart.gender", "value": "nữ"}
GOOD, MV = ["miếu", "vượng", "đắc"], ["miếu", "vượng"]
R = [
 ("CO_CAT_QUYEN_LOC", [OM("Thiên Cơ"), CAT, HOA("Hóa Quyền"), HOA("Hóa Lộc")], "tt_nu_co_cat_quyen_loc_vinh_hoa", "p.108", "làm việc giỏi hơn nhiều người, được Quyền Lộc thì vinh hoa (nữ mệnh Thiên Cơ có cát tinh phù trì)", "draft"),
 ("NHAT_TAO_VAT", [OM("Thái Dương"), dig("Thái Dương", GOOD)], "tt_nu_nhat_thao_vat_gioi_giang", "p.108", "rất tháo vát, giỏi giang (nữ mệnh Thái Dương đắc địa)", "verified"),
 ("NHAT_CAT_TINH", [OM("Thái Dương"), dig("Thái Dương", GOOD), CAT], "tt_nu_nhat_cat_tinh_phu_nhan", "p.108", "đoan trang, có thể được trọng vọng, danh phận cao (nữ mệnh Thái Dương sáng có cát tinh)", "verified"),
 ("VU_PHU", [OM("Vũ Khúc"), OM("Thiên Phủ")], "tt_nu_vu_phu_chi_khi_hung", "p.109", "chí khí hùng tráng (nữ mệnh Vũ Khúc đồng cung Thiên Phủ)", "verified"),
 ("VU_PHU_TA_HUU_LOC", [OM("Vũ Khúc"), OM("Thiên Phủ"), {"any": [has("palace.rel.tp_stars", "Tả Phụ"), has("palace.rel.tp_stars", "Hữu Bật")]}, {"any": [has("palace.rel.tp_stars", "Lộc Tồn"), HOA("Hóa Lộc")]}], "tt_nu_vu_phu_ta_huu_loc_phu_qui_song_toan", "p.109", "phú quý song toàn (nữ mệnh Vũ Phủ gặp Tả Hữu, Lộc)", "verified"),
 ("DONG_XK", [OM("Thiên Đồng"), {"any": [has("palace.rel.tp_stars", "Văn Xương"), has("palace.rel.tp_stars", "Văn Khúc")]}], "tt_nu_dong_xuong_khuc_tai_loc_tu_den", "p.110", "thông minh lanh lợi, tài lộc tự nhiên đến (nữ mệnh Thiên Đồng hội Xương Khúc)", "verified"),
 ("LIEM_DAC_CAT", [OM("Liêm Trinh"), dig("Liêm Trinh", GOOD), CAT, NOSAT], "tt_nu_liem_dac_cat_thanh_sach_sang_qui", "p.110", "quán xuyến giỏi, thanh sạch, sang quý từ sớm (nữ mệnh Liêm Trinh đắc địa, cát tinh, không sát)", "verified"),
 ("PHU_TU_VI", [OM("Thiên Phủ"), {"any": [has("palace.rel.tp_majors", "Tử Vi")]}], "tt_nu_phu_tu_vi_hoi_chieu_phu_nhan", "p.110", "thông minh, có địa vị cao (nữ mệnh Thiên Phủ được Tử Vi hội chiếu)", "verified"),
 ("NGUYET_NHAT_CAT", [OM("Thái Âm"), OM("Thái Dương"), CAT, NOSAT], "tt_nu_nguyet_nhat_phu_qui_song_toan", "p.111", "phú quý song toàn (nữ mệnh Nhật Nguyệt đồng cung, cát tinh chiếu, không sát)", "verified"),
 ("THAM_TU_MO_TA_HUU", [OM("Tham Lang"), {"fact": "palace.branch", "operator": "in", "value": ["Thìn", "Tuất", "Sửu", "Mùi"]}, {"any": [has("palace.rel.tp_stars", "Tả Phụ"), has("palace.rel.tp_stars", "Hữu Bật")]}], "tt_nu_tham_tu_mo_ta_huu_tai_loc", "p.111", "tài lộc phong phú, tính cương cường, chí khí (nữ mệnh Tham Lang ở Tứ mộ gặp Tả Hữu)", "verified"),
 ("CU_VUONG_TA_HUU", [OM("Cự Môn"), dig("Cự Môn", MV), {"any": [has("palace.rel.tp_stars", "Tả Phụ"), has("palace.rel.tp_stars", "Hữu Bật")]}], "tt_nu_cu_vuong_ta_huu_tot_lanh", "p.112", "nhiều điều tốt lành, có phần quý (nữ mệnh Cự Môn vượng gặp Tả Hữu)", "verified"),
]
slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for rid, conds, claim, loc, vi, status in R:
    rules.append({"id": f"TV_TT_NU_{rid}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "tt_nu",
        "description": f"Tử Vi Đẩu Số Toàn Thư, nữ mệnh ca (paraphrased), cung Mệnh: {vi} [TT {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": "Mệnh"}, NU] + conds},
        "consequences": [{"kind": "finding", "claim": claim, "effect": "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_TOAN_THU"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims[claim] = "khuynh hướng " + vi
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids))
json.dump({"sources": [], "rules": rules}, open(D / "pack_toan_thu_nu.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
