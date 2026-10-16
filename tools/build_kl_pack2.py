"""Generates data/pack_khao_luan_phu2.json from Tử Vi Khảo Luận 'phú đoán' explanations, second batch (pp.66-73), paraphrased.
Reading policy: 'đồng cung' = own palace; 'hội/chiếu/tam hợp/xung chiếu' = tam phương (verified when the text says so);
a bare 'gặp' is ambiguous -> tam phương used and the rule stays draft. Harm predictions (death, prison, suicide) and moral
verdicts are deliberately not encoded."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPS, TPM, TPH = "palace.own_stars", "palace.own_major_stars", "palace.tam_phuong_stars", "palace.tam_phuong_majors", "palace.tam_phuong_tu_hoa"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
nt = lambda x: {"not": x}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}
GOOD = ["miếu", "vượng", "đắc"]
oM = lambda *ss: [has(OWNM, s) for s in ss]
oS = lambda *ss: [has(OWN, s) for s in ss]
tS = lambda *ss: [has(TPS, s) for s in ss]
TAM3 = [has(TPH, h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")]
SAT = [has(TPS, s) for s in ("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp")]

# id, extra conditions (Mệnh implied unless a palace name is given as first condition), claim, status, page, phrase
HL = has("palace.tu_hoa", "Hóa Lộc")
nb = lambda *ss: [has("palace.neighbor_majors", s) for s in ss]
R = [
 ("HOA_LOC", [HL], "hoa_loc_tai_loc_tot", "verified", "p.66", "tài lộc thuận lợi (Hóa Lộc tại Mệnh)"),
 ("HOA_LOC_TU_MO", [HL, br("Thìn", "Tuất", "Sửu", "Mùi")], "hoa_loc_tai_loc_tot", "verified", "p.66", "tài lộc giảm đi nhiều (Hóa Lộc ở Mệnh nhưng đóng Tứ Mộ); đây là điều kiện hạn chế của nhận định trên"),
 ("HOA_LOC_TY_NGO", [HL, br("Tý", "Ngọ")], "hoa_loc_ty_ngo_van_chuong", "verified", "p.66", "giỏi văn chương (Hóa Lộc ở Mệnh tại Tý hoặc Ngọ)"),
 ("LOC_TON_CO_LUONG", [*oS("Lộc Tồn"), *oM("Thiên Cơ", "Thiên Lương")], "loc_ton_co_luong_rat_giau", "verified", "p.66", "rất giàu có, ít người sánh kịp (Lộc Tồn đồng cung Thiên Cơ, Thiên Lương)"),
 ("KHONG_KIEP_TY_HOI", [br("Tỵ", "Hợi"), *oS("Địa Không", "Địa Kiếp")], "khong_kiep_ty_hoi_thanh_cong_nhanh", "verified", "p.68", "đường công danh đến nhanh, một bước thành công (Địa Không, Địa Kiếp đồng cung ở Tỵ hoặc Hợi)"),
 ("CO_DAC_DIA", [*oM("Thiên Cơ"), dig("Thiên Cơ", GOOD)], "co_dac_dia_tai_nang", "verified", "p.68", "nhiều tài năng, giỏi hơn người (Thiên Cơ đắc địa)"),
 ("THIEN_MA", [*oS("Thiên Mã")], "thien_ma_tai_chiu_kho", "verified", "p.68", "nhiều tài, chịu khó (Thiên Mã ở Mệnh)"),
 ("MA_TRUONG_SINH", [*oS("Thiên Mã", "Trường Sinh")], "ma_truong_sinh_cong_danh_de", "verified", "p.68", "đường công danh dễ dàng (Thiên Mã đồng cung Trường Sinh)"),
 ("HONG_LOAN_TY", [br("Tý"), *oS("Hồng Loan")], "hong_loan_ty_som_do_dat", "verified", "p.68", "sớm thành đạt về học hành thi cử (Hồng Loan ở Mệnh tại Tý)"),
 ("TUAN_TRIET", [anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})], "thoi_tre_van_va_lo_toan", "verified", "p.68", "thời trẻ nhiều vất vả (Tuần hoặc Triệt án ngữ Mệnh); cùng nhận định với Tử Vi Thực Hành"),
 ("BA_KHONG", [anyof(*oS("Địa Không", "Thiên Không"), {"fact": "palace.tuan", "value": True})], "ba_khong_kho_giau_sang", "verified", "p.68", "khó giàu sang (Mệnh có một trong ba Không: Tuần Không, Địa Không, Thiên Không)"),
 ("KHOA_QUYEN_LOC", [has("palace.tu_hoa", "Hóa Khoa"), has("palace.tu_hoa", "Hóa Quyền"), HL], "khoa_quyen_loc_phuc_may_man", "verified", "p.69", "phúc đức, may mắn liên tục (Khoa, Quyền, Lộc cùng thủ Mệnh)"),
 ("DUONG_MUI", [br("Mùi"), *oM("Thái Dương")], "duong_mui_dau_cham_sau_luoi", "verified", "p.69", "lúc đầu chăm chỉ, về sau dễ chểnh mảng (Thái Dương ở Mùi)"),
 ("AM_DAN", [br("Dần"), *oM("Thái Âm")], "am_dan_de_bo_do", "verified", "p.69", "dễ bỏ dở việc giữa chừng (Thái Âm ở Dần)"),
 ("LUONG_PHUC", [*oM("Thiên Lương")], "luong_hao_phong_lam_phuc", "verified", "p.69", "sẵn lòng dùng của cải giúp người, làm phúc (Thiên Lương thủ Mệnh)"),
 ("PHU_THE_AM_KHUC_HOI", [br("Hợi"), *oM("Thái Âm"), *oS("Văn Khúc")], "phu_the_am_khuc_hoi_bat_doi_sang", "verified", "p.70", "bạn đời có địa vị, sang quý (cung Phu Thê có Thái Âm đồng cung Văn Khúc ở Hợi)"),
 ("DUONG_XUONG_NGO", [br("Ngọ"), *oM("Thái Dương"), *oS("Văn Xương")], "duong_xuong_ngo_lich_thiep", "verified", "p.70", "lịch thiệp, nổi bật (Thái Dương đồng cung Văn Xương ở Ngọ)"),
 ("MA_VU", [*oS("Thiên Mã"), *oM("Vũ Khúc")], "ma_vu_can_kiem_giau_som", "verified", "p.70", "cần kiệm, khá giả trước tuổi 40 (Thiên Mã đồng cung Vũ Khúc)"),
 ("LUONG_VU_SUU", [br("Sửu"), anyof(*oM("Thiên Lương", "Vũ Khúc"))], "luong_vu_suu_tien_bac_day", "verified", "p.70", "tiền bạc dồi dào (Thiên Lương hoặc Vũ Khúc ở Mệnh tại Sửu)"),
 ("DONG_THAM_NGO", [br("Ngọ"), anyof(*oM("Thiên Đồng", "Tham Lang")), anyof(dig("Thiên Đồng", GOOD), dig("Tham Lang", GOOD))], "dong_tham_ngo_nha_cua", "verified", "p.70", "nhà cửa, bất động sản nhiều (Thiên Đồng hoặc Tham Lang đắc địa ở Mệnh tại Ngọ)"),
 ("TU_THAM_DAU", [br("Dậu"), *oM("Tử Vi", "Tham Lang")], "tu_tham_dau_thieu_quyen_luc", "verified", "p.70", "thiếu sức mạnh quyền hành (Tử Vi Tham Lang ở Mệnh tại Dậu)"),
 ("SAT_THAN", [br("Thân"), *oM("Thất Sát")], "sat_than_phu_quy_tron_ven", "verified", "p.70", "phú quý trọn vẹn (Thất Sát ở Mệnh tại Thân)"),
 ("TUONG_TA_HUU_Y", [*oM("Thiên Tướng"), *oS("Tả Phụ", "Hữu Bật")], "tuong_ta_huu_hop_nghe_y", "verified", "p.71", "hợp nghề thầy thuốc, chữa bệnh (Thiên Tướng đồng cung Tả Hữu)"),
 ("DAO_HONG_CO", [*oS("Đào Hoa", "Hồng Loan"), has(TPM, "Thiên Cơ")], "dao_hong_co_nghe_thuat", "draft", "p.71", "thiên hướng nghệ thuật, hội họa (Đào Hoa, Hồng Loan gặp Thiên Cơ); 'gặp' đọc là hội trong tam phương"),
 ("LIEM_SAT_GIAP", [*nb("Liêm Trinh", "Thất Sát")], "liem_sat_giap_danh_muon", "verified", "p.71", "công danh đến muộn, về già mới rõ (Liêm Trinh, Thất Sát giáp hai bên Mệnh)"),
 ("TUE_SAT", [*oS("Thái Tuế"), *oM("Thất Sát")], "tue_sat_muu_luoc_dung_manh", "verified", "p.71", "mưu lược và dũng mãnh (Thái Tuế đồng cung Thất Sát)"),
 ("KHOA_VAN_TINH", [has("palace.tu_hoa", "Hóa Khoa"), *oS("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt")], "khoa_van_tinh_thi_cu_mot_lan", "verified", "p.71", "thi cử thuận lợi, đỗ cao ngay lần đầu (Hóa Khoa đồng cung Xương Khúc Khôi Việt)"),
 ("KHOA_QUYEN_KHOI_VIET", [has("palace.tu_hoa", "Hóa Khoa"), has("palace.tu_hoa", "Hóa Quyền"), *tS("Thiên Khôi", "Thiên Việt")], "khoa_quyen_khoi_viet_thanh_cong", "verified", "p.73", "thành công lớn (Hóa Khoa, Hóa Quyền ở Mệnh, Khôi Việt hợp chiếu)"),
 ("XUONG_KHUC_NHAT_NGUYET", [*oS("Văn Xương", "Văn Khúc"), *[has(TPM, s) for s in ("Thái Dương", "Thái Âm")]], "xuong_khuc_nhat_nguyet_thanh_cong", "verified", "p.73", "thành công mạnh mẽ (Xương Khúc ở Mệnh, Nhật Nguyệt hợp chiếu)"),
]
rules, claims = [], {}
for rid, extra, claim, status, loc, vi in R:
    rules.append({"id": "TV_KL_PHU2_" + rid, "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "kl_phu_doan",
        "description": f"Tử Vi Khảo Luận, phú đoán (paraphrased): {vi} [KL {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": "Phu Thê" if rid.startswith("PHU_THE") else "Mệnh"}] + extra},
        "consequences": [{"kind": "finding", "claim": claim, "effect": "limit" if rid == "HOA_LOC_TU_MO" else "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 4, "sourceIds": ["SRC_KHAO_LUAN"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    if rid == "HOA_LOC_TU_MO":
        claims["limit:" + claim] = "tài lộc bị giảm đi nhiều khi Hóa Lộc đóng ở Tứ Mộ (Thìn, Tuất, Sửu, Mùi)"
    elif claim not in claims:
        claims[claim] = "khuynh hướng " + vi.split(" (")[0] + (" (" + vi.split(" (", 1)[1] if " (" in vi else "")
json.dump({"sources": [], "rules": rules}, open(D / "pack_khao_luan_phu2.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8")); cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules), len({r['id'] for r in rules}))
