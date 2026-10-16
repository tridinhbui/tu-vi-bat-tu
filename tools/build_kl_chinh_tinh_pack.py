"""Generates data/pack_khao_luan_chinh_tinh.json from Tử Vi Khảo Luận pp.220-224 ('Chính tinh cung Mệnh': what each star or pair means
at Mệnh, with the positions the text names). Paraphrased. 'đồng cung/đi với' = same palace; 'chiếu/hội' = tam phương; Tử Vi's own
position is a chart-level fact (chart.tu_vi_branch)."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPM, TPS, TPH = "palace.own_stars", "palace.own_major_stars", "palace.tam_phuong_majors", "palace.tam_phuong_stars", "palace.tam_phuong_tu_hoa"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
allof = lambda *x: {"all": list(x)}
nt = lambda x: {"not": x}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
oM = lambda *ss: [has(OWNM, s) for s in ss]
MAJ = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân"]
solo = lambda star: allof(has(OWNM, star), nt(anyof(*[has(OWNM, m) for m in MAJ if m != star])))
tuvi_at = lambda *b: {"fact": "chart.tu_vi_branch", "operator": "in", "value": list(b)}
NOMAJ = {"fact": "palace.has_no_major", "value": True}
nhat_nguyet = [has(TPM, "Thái Dương"), has(TPM, "Thái Âm")]

R = [  # id, conditions, claim, status, page, phrase
 ("TV_TUONG_THIN_TUAT", [br("Thìn", "Tuất"), *oM("Tử Vi", "Thiên Tướng")], "tv_tuong_co_danh_vat_va", "verified", "p.220-221", "có danh nhưng phải vất vả mới thành công (Tử Vi đi với Thiên Tướng ở Thìn hoặc Tuất)"),
 ("TV_THAM_MAO_DAU", [br("Mão", "Dậu"), *oM("Tử Vi", "Tham Lang")], "tv_tham_tham_vong_ech_che", "verified", "p.221", "nhiều tham vọng, thành đạt thì cũng kèm điều tiếng (Tử Vi đi với Tham Lang ở Mão hoặc Dậu)"),
 ("TV_PHU_DAN_THAN", [br("Dần", "Thân"), *oM("Tử Vi", "Thiên Phủ")], "tv_phu_phuc_lon_on_dinh", "verified", "p.221", "phúc lớn, giàu sang, ổn định (Tử Vi đi với Thiên Phủ ở Dần hoặc Thân)"),
 ("TV_PHA_SUU_MUI", [br("Sửu", "Mùi"), *oM("Tử Vi", "Phá Quân")], "tv_pha_lieu_linh_noi_danh", "verified", "p.221", "đa đoan, liều lĩnh nhưng cũng nổi danh một thời (Tử Vi đi với Phá Quân ở Sửu hoặc Mùi)"),
 ("TV_SAT_TY_HOI", [br("Tỵ", "Hợi"), *oM("Tử Vi", "Thất Sát")], "tv_sat_thoat_ly_thanh_cong_som", "verified", "p.220", "rời xa gia đình sớm nhưng thành công sớm (Tử Vi đi với Thất Sát ở Tỵ hoặc Hợi)"),
 ("SAT_PHA_THAM", [anyof(*[has(OWNM, s) for s in ("Thất Sát", "Phá Quân", "Tham Lang")])], "spt_tich_cuc_thanh_cong_hoac_thanh_nhan", "verified", "p.221", "sống tích cực: không thành công thì cũng thành nhân (Sát Phá Tham ở Mệnh)"),
 ("CNDL", [{"fact": "derived.group.co_nguyet_dong_luong", "value": True}], "cndl_tri_thuc_cong_boc_yen_phan", "verified", "p.221", "hàng trí thức, công bộc, giỏi chữ nghĩa nhưng hay giữ phận, ngại mất cái mình có (Cơ Nguyệt Đồng Lương)"),
 ("CNDL_KQL_KV_XK", [{"fact": "derived.group.co_nguyet_dong_luong", "value": True}, *[has(TPH, h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")], anyof(has(TPS, "Thiên Khôi"), has(TPS, "Thiên Việt")), anyof(has(TPS, "Văn Xương"), has(TPS, "Văn Khúc"))], "cndl_hoc_thuat_danh_tieng", "draft", "p.221", "hợp con đường học thuật, giảng dạy có tiếng (Cơ Nguyệt Đồng Lương hội Khoa Quyền Lộc, Khôi Việt, Xương Khúc); hệ thống đọc 'Khôi Việt, Xương Khúc' là ít nhất một sao mỗi cặp"),
 ("CU_NHAT", [*oM("Cự Môn", "Thái Dương")], "cu_nhat_noi_gioi_ly_luan_yen_phan", "verified", "p.221", "ăn nói giỏi, thông minh nhưng thiên về lý luận, hợp phận phục vụ có bổng lộc (Cự Môn đồng cung Thái Dương)"),
 ("CAP_DOI_BAC_TRUNG", [anyof(allof(*oM("Cự Môn", "Thiên Cơ")), allof(*oM("Thái Dương", "Thiên Lương")), allof(*oM("Thiên Cơ", "Thiên Lương")), allof(*oM("Thiên Đồng", "Thái Âm")), allof(*oM("Cự Môn", "Thiên Đồng")), allof(*oM("Thái Dương", "Thái Âm")), allof(*oM("Tham Lang", "Vũ Khúc")), allof(*oM("Thiên Đồng", "Thiên Lương")))], "cap_doi_sao_bac_trung", "verified", "p.221", "không quá nổi bật cũng không thấp kém, thường ở mức trung (các cặp Cự Cơ, Dương Lương, Cơ Lương, Đồng Âm, Cự Đồng, Nhật Nguyệt, Tham Vũ, Đồng Lương)"),
 ("VCD_TY_NGO", [NOMAJ, br("Sửu", "Mùi"), tuvi_at("Tý", "Ngọ"), *nhat_nguyet], "vcd_ty_ngo_thong_minh_noi_danh", "verified", "p.222", "thông minh giỏi giang, có thể không giàu nhưng nổi danh đáng nể (Mệnh vô chính diệu ở Sửu/Mùi, thế Tử Vi Tý Ngọ, Nhật Nguyệt chiếu)"),
 ("VCD_TU_SAT", [NOMAJ, br("Thìn", "Tuất"), tuvi_at("Tỵ", "Hợi"), has(TPM, "Thiên Cơ"), has(TPM, "Thiên Lương")], "vcd_tu_sat_gioi_dao_duc_khong_giau", "verified", "p.222", "giỏi giang, đạo đức nhưng không nhất thiết giàu (Mệnh vô chính diệu ở Thìn/Tuất, thế Tử Sát Tỵ Hợi, Cơ Lương chiếu)"),
 ("VCD_TU_TUONG", [NOMAJ, br("Sửu", "Mùi"), tuvi_at("Thìn", "Tuất"), *nhat_nguyet], "vcd_tu_tuong_thong_minh_khong_giau", "verified", "p.222", "thông minh giỏi giang nhưng không giàu tiền bạc (Mệnh vô chính diệu ở Sửu/Mùi, thế Tử Tướng Thìn Tuất, Nhật Nguyệt chiếu)"),
 ("VU_DON_THU", [solo("Vũ Khúc")], "vu_don_thu_giau", "verified", "p.222", "thiên về giàu có (Vũ Khúc đứng một mình)"),
 ("LIEM_DON_THU", [solo("Liêm Trinh")], "liem_don_thu_sang", "verified", "p.222", "thiên về sang, địa vị (Liêm Trinh đứng một mình)"),
 ("VU_PHA_TY_HOI", [br("Tỵ", "Hợi"), *oM("Vũ Khúc", "Phá Quân")], "vu_pha_lam_an_bao", "verified", "p.222", "làm ăn bạo dạn, dễ lấn qua ranh giới luật lệ (Vũ Khúc Phá Quân ở Tỵ hoặc Hợi)"),
 ("VU_SAT_MAO_DAU", [br("Mão", "Dậu"), *oM("Vũ Khúc", "Thất Sát")], "vu_sat_quyet_liet", "verified", "p.222", "quyết liệt, ít nể nang (Vũ Khúc Thất Sát ở Mão hoặc Dậu)"),
 ("VU_THAM_SUU_MUI", [br("Sửu", "Mùi"), *oM("Vũ Khúc", "Tham Lang")], "vu_tham_chu_trong_tien_bam_giu", "verified", "p.222", "chú trọng tiền bạc, bám giữ của cải (Vũ Khúc Tham Lang ở Sửu hoặc Mùi)"),
 ("VU_TUONG_DAN_THAN", [br("Dần", "Thân"), *oM("Vũ Khúc", "Thiên Tướng")], "vu_tuong_phuc_giau_thanh_cong", "verified", "p.222", "tốt phúc, giàu sang, thành công may mắn (Vũ Khúc Thiên Tướng ở Dần hoặc Thân)"),
 ("VU_TUONG_KHONG_TT", [*oM("Vũ Khúc", "Thiên Tướng"), nt({"fact": "palace.tuan", "value": True}), nt({"fact": "palace.triet", "value": True})], "vu_tuong_doi_suon_se", "verified", "p.222", "đời suôn sẻ, hưởng phúc (Vũ Tướng không bị Tuần Triệt án ngữ)"),
 ("LIEM_TUONG_NGO", [br("Ngọ"), *oM("Liêm Trinh", "Thiên Tướng")], "liem_tuong_nghiem_chinh_can_co", "verified", "p.222", "nghiêm chỉnh, trung thực, căn cơ chắt bóp (Liêm Tướng ở Ngọ)"),
 ("LIEM_PHA_MAO_DAU", [br("Mão", "Dậu"), *oM("Liêm Trinh", "Phá Quân")], "liem_pha_non_nong_giau_mau", "verified", "p.222", "nôn nóng, liều lĩnh, giàu mau mà mất cũng gọn (Liêm Phá ở Mão hoặc Dậu)"),
 ("LIEM_SAT_SUU_MUI", [br("Sửu", "Mùi"), *oM("Liêm Trinh", "Thất Sát")], "liem_sat_li_lom_deo_bam", "verified", "p.222", "kiên gan, bám việc, không ngại gian nguy nhưng dễ vướng việc lớn (Liêm Sát ở Sửu hoặc Mùi)"),
 ("PHU_VU_TY_NGO", [br("Tý", "Ngọ"), *oM("Thiên Phủ", "Vũ Khúc")], "phu_vu_yen_phan_tich_coc", "verified", "p.222", "cách yên phận, tích cóp phòng xa, khá giả nhờ cần kiệm (Phủ Vũ ở Tý hoặc Ngọ)"),
 ("PHU_LIEM_THIN_TUAT", [br("Thìn", "Tuất"), *oM("Thiên Phủ", "Liêm Trinh")], "phu_liem_quan_tu", "verified", "p.222", "cách quân tử: nghèo thì không muốn, giàu thì không ham (Phủ Liêm ở Thìn hoặc Tuất)"),
 ("PHU_LAC_KHONG_VONG", [*oM("Thiên Phủ"), anyof(has(TPS, "Địa Không"), has(TPS, "Địa Kiếp"), {"fact": "palace.tuan", "value": True})], "phu_lac_khong_vong_phieu_bat", "draft", "p.222", "dễ phiêu bạt, mất mát lớn như hoa rơi giữa rừng gươm (Thiên Phủ gặp Không, Kiếp hoặc Tuần Không); 'gặp' đọc là hội trong tam phương"),
 ("PHU_THU_MENH", [*oM("Thiên Phủ")], "phu_thu_menh_ta_day_de_bi_ganh", "verified", "p.222", "tự tin ('ta đây'), dễ bị ganh ghét (Thiên Phủ thủ Mệnh)"),
 ("SAT_THU_MENH", [*oM("Thất Sát")], "sat_thu_menh_non_nong_lam_giau", "verified", "p.222-223", "ương ngạnh, nóng nảy, cương nghị, thích ăn to nói lớn, dễ thành công về võ nghiệp, nôn nóng làm giàu (Thất Sát thủ Mệnh)"),
 ("PHA_THU_MENH", [*oM("Phá Quân")], "pha_thu_menh_nang_dong_hieu_thang", "verified", "p.223", "năng động, hiếu thắng, tự đắc, thích nghe nịnh, khí khái hiên ngang nhưng thăng trầm (Phá Quân thủ Mệnh)"),
 ("DONG_THU_MENH", [*oM("Thiên Đồng")], "dong_thu_menh_thong_minh_nhan_hau_hay_doi", "verified", "p.223", "thông minh, nhân hậu, từ thiện nhưng hay thay đổi ý kiến, có thể tay trắng làm nên (Thiên Đồng thủ Mệnh)"),
 ("CU_THU_MENH", [*oM("Cự Môn")], "cu_thu_menh_muu_tri_phan_xet", "verified", "p.223", "thông minh, mưu trí, phán xét sáng suốt (Cự Môn thủ Mệnh)"),
 ("CU_CO_MAO_DAU", [br("Mão", "Dậu"), *oM("Cự Môn", "Thiên Cơ")], "cu_co_giau_nhung_ngang_trai", "verified", "p.223", "giàu nhưng hay gặp chuyện ngang trái (Cự Cơ ở Mão hoặc Dậu)"),
 ("CU_NHAT_DAN_THAN", [br("Dần", "Thân"), *oM("Cự Môn", "Thái Dương")], "cu_nhat_suong_tu_nho", "verified", "p.223", "thuận lợi từ nhỏ (Cự Nhật ở Dần hoặc Thân)"),
 ("CU_KHOA", [*oM("Cự Môn"), has("palace.tu_hoa", "Hóa Khoa")], "cu_khoa_gioi_van_chuong", "verified", "p.223", "giỏi văn chương (Cự Môn thêm Hóa Khoa)"),
 ("TUONG_THU_MENH", [*oM("Thiên Tướng")], "tuong_thu_menh_don_hau_thang_than", "verified", "p.223", "đôn hậu, thẳng thắn, thích ăn ngon mặc đẹp (Thiên Tướng thủ Mệnh)"),
 ("TUONG_TUAN", [*oM("Thiên Tướng"), {"fact": "palace.tuan", "value": True}], "tuong_tuan_su_nghiep_be_tac", "verified", "p.223", "sự nghiệp dễ bế tắc (Thiên Tướng gặp Tuần)"),
 ("TUONG_TRIET", [*oM("Thiên Tướng"), {"fact": "palace.triet", "value": True}], "tuong_triet_de_roi_chuc_vu", "verified", "p.223", "dễ phải rời bỏ chức vụ giữa chừng (Thiên Tướng gặp Triệt)"),
 ("TUONG_LIEM", [*oM("Thiên Tướng", "Liêm Trinh")], "tuong_liem_quan_xuyen", "verified", "p.223", "quán xuyến mọi bề (Thiên Tướng đi với Liêm Trinh)"),
 ("TUONG_TU_VI", [*oM("Thiên Tướng", "Tử Vi")], "tuong_tu_vi_tham_cong_tiec_viec", "verified", "p.223", "tham công tiếc việc (Thiên Tướng đi với Tử Vi)"),
 ("TUONG_VU", [*oM("Thiên Tướng", "Vũ Khúc")], "tuong_vu_tai_dam_duoc_ne", "verified", "p.223", "tài đảm, được nể vì (Thiên Tướng đi với Vũ Khúc)"),
 ("LUONG_THU_MENH", [*oM("Thiên Lương")], "luong_thu_menh_khoan_hoa_nha_nhan", "verified", "p.223", "tính từ lâm, khoan hòa, nhã nhặn; thích làm việc thiện và hay nói đạo đức (Thiên Lương thủ Mệnh)"),
 ("LUONG_DUONG", [*oM("Thiên Lương", "Thái Dương")], "luong_duong_do_dat_som", "verified", "p.223", "đỗ đạt sớm, giàu sang nổi tiếng (Thiên Lương đồng cung Thái Dương)"),
 ("LUONG_AM", [*oM("Thiên Lương", "Thái Âm")], "luong_am_bon_tau_leng_denh", "draft", "p.224", "dễ bôn tẩu, lênh đênh (Thiên Lương gặp Thái Âm); 'gặp' đọc là đồng cung"),
 ("DUONG_THU_MENH", [*oM("Thái Dương")], "duong_thu_menh_lo_cong_danh", "verified", "p.224", "lo công danh, địa vị (Thái Dương ở Mệnh)"),
 ("AM_THU_MENH", [*oM("Thái Âm")], "am_thu_menh_lo_su_nghiep_tien_tai", "verified", "p.224", "lo sự nghiệp, tiền tài (Thái Âm ở Mệnh)"),
 ("NHAT_NGUYET_DONG_CUNG", [*oM("Thái Dương", "Thái Âm")], "nhat_nguyet_dong_cung_soi_sang_nguoi", "verified", "p.224", "lo soi sáng cho người khác, bản thân chưa hẳn hơn người (Nhật Nguyệt đồng cung)"),
 ("NHAT_NGUYET_CHIEU", [*nhat_nguyet, nt(allof(*oM("Thái Dương", "Thái Âm")))], "nhat_nguyet_chieu_menh_tot_dep", "verified", "p.224", "thông minh sáng suốt, làm việc tài giỏi, dễ thành công (Nhật Nguyệt chiếu Mệnh)"),
 ("HONG_LOAN", [has(OWN, "Hồng Loan")], "hong_loan_phong_nha_hao_hoa", "verified", "p.224", "phong nhã, hào hoa (Hồng Loan ở Mệnh)"),
 ("DAO_HOA", [has(OWN, "Đào Hoa")], "dao_hoa_long_dong_vat_va", "verified", "p.224", "đường đời nhiều lận đận, vất vả (Đào Hoa ở Mệnh)"),
 ("DAO_TY", [br("Tý"), has(OWN, "Đào Hoa")], "dao_ty_som_nem_trai_doi", "verified", "p.224", "sớm nếm trải cuộc đời (Đào Hoa ở Tý)"),
 ("DAO_MAO", [br("Mão"), has(OWN, "Đào Hoa")], "dao_mao_thanh_cong_som_chong_tan", "verified", "p.224", "thành công sớm thì dễ chóng tàn (Đào Hoa ở Mão)"),
 ("DAO_NGO", [br("Ngọ"), has(OWN, "Đào Hoa")], "dao_ngo_danh_ech_che_tinh_do_dang", "verified", "p.224", "có danh cũng kèm điều tiếng, tình cảm dễ dang dở (Đào Hoa ở Ngọ)"),
 ("DAO_DAU", [br("Dậu"), has(OWN, "Đào Hoa")], "dao_dau_cong_danh_cham", "verified", "p.224", "công danh chậm trễ, sớm yên phận (Đào Hoa ở Dậu)"),
 ("DAO_HONG_CUNG", [br("Tý", "Ngọ", "Mão", "Dậu"), has(OWN, "Đào Hoa"), has(OWN, "Hồng Loan")], "dao_hong_cung_cong_danh_tinh_cam_den_mau", "verified", "p.224", "công danh và tình cảm đến nhanh (Đào Hồng đồng cung ở Tý, Ngọ, Mão hoặc Dậu)"),
 ("HONG_DON_THU", [br("Tý", "Ngọ", "Mão", "Dậu"), has(OWN, "Hồng Loan"), nt(has(OWN, "Đào Hoa"))], "hong_don_thu_luy_tinh", "verified", "p.224", "dễ lụy tình, khó tiến xa (Hồng Loan đơn thủ ở Tý, Ngọ, Mão hoặc Dậu)"),
 ("HONG_TU_SINH", [br("Dần", "Thân", "Tỵ", "Hợi"), has(OWN, "Hồng Loan")], "hong_tu_sinh_dac_cach", "verified", "p.224", "đắc cách: công danh rộng mở, độ lượng bao dung (Hồng Loan ở Dần, Thân, Tỵ hoặc Hợi)"),
 ("NHAT_NGUYET_DAO_HONG", [anyof(has(OWNM, "Thái Dương"), has(OWNM, "Thái Âm")), has(TPS, "Đào Hoa"), has(TPS, "Hồng Loan")], "nhat_nguyet_dao_hong_dep_do", "verified", "p.224", "đẹp đẽ, công danh sự nghiệp tình ái vẹn toàn hơn (Nhật hoặc Nguyệt có Đào Hồng đồng cung hoặc tam hợp chiếu)"),
]
rules, claims = [], {}
for rid, conds, claim, status, loc, vi in R:
    is_chart = False
    base = [{"fact": "palace.name", "value": "Mệnh"}]
    rules.append({"id": "TV_KL_CT_" + rid, "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "kl_chinh_tinh",
        "description": f"Tử Vi Khảo Luận, chính tinh cung Mệnh (paraphrased): {vi} [KL {loc}]",
        "conditions": {"all": base + conds}, "consequences": [{"kind": "finding", "claim": claim, "effect": "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_KHAO_LUAN"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims[claim] = "khuynh hướng " + vi.split(" (")[0] + (" (" + vi.split(" (", 1)[1] if " (" in vi else "")
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids))
json.dump({"sources": [], "rules": rules}, open(D / "pack_khao_luan_chinh_tinh.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8")); cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
