"""Generates data/pack_toan_thu.json from Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục, PDF pp.21-28): second, independent statement of classical
phú (same tradition as Khảo Luận). Where a claim id equals one already encoded from Khảo Luận, this adds a SECOND supporting source."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPM, TPS, TPH = "palace.own_stars", "palace.own_major_stars", "palace.tam_phuong_majors", "palace.tam_phuong_stars", "palace.tam_phuong_tu_hoa"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
nt = lambda x: {"not": x}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
ys = lambda *s: {"fact": "chart.year_stem", "operator": "in", "value": list(s)}
oM = lambda *ss: [has(OWNM, s) for s in ss]
TAM3 = [has(TPH, h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")]
dig = lambda st, lv: {"fact": f"palace.dignity.{st}", "operator": "in", "value": lv}
GOOD = ["miếu", "vượng", "đắc"]
SAT4 = ("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh")
noSat = nt(anyof(*[has(TPS, x) for x in SAT4]))
R = [  # palace, id, conditions, claim, status, page, phrase
 ("Mệnh", "TV_TY_NGO_TAM_HOA", [br("Tý", "Ngọ"), *oM("Tử Vi"), *TAM3], "tu_vi_ngo_tam_hoa_cach_tot", "verified", "p.21", "thế rất tốt, đường hiển đạt rõ (Tử Vi ở Tý hoặc Ngọ được Khoa, Quyền, Lộc tam phương chiếu)"),
 ("Mệnh", "TU_VI_TA_HUU", [*oM("Tử Vi"), has(OWN, "Tả Phụ"), has(OWN, "Hữu Bật")], "tu_vi_ta_huu_uy_quyen", "verified", "p.22", "có uy quyền, hiệu lệnh được nhiều người nghe (Tử Vi đồng cung Tả Phụ, Hữu Bật; ở tam hợp hay xung chiếu thì kém hơn)"),
 ("Mệnh", "TU_VI_XUONG_KHUC", [*oM("Tử Vi"), has(OWN, "Văn Xương"), has(OWN, "Văn Khúc")], "tu_vi_xuong_khuc_giau_sang", "verified", "p.22", "giàu sang nổi bật (Tử Vi hội Văn Xương, Văn Khúc)"),
 ("Mệnh", "TU_PHU_LOC_TON", [*oM("Tử Vi", "Thiên Phủ"), has(TPS, "Lộc Tồn")], "tu_phu_loc_ton_phuc_hau", "verified", "p.22", "phúc hậu, địa vị cao (Tử Phủ ở Dần hoặc Thân lại có Lộc Tồn và các sao tốt)"),
 ("Mệnh", "TU_PHU_GIAP", [has("palace.neighbor_majors", "Tử Vi"), has("palace.neighbor_majors", "Thiên Phủ")], "menh_giap_tu_phu_quy_cach", "verified", "p.22", "quý cách (Tử Vi, Thiên Phủ giáp hai bên Mệnh)"),
 ("Mệnh", "TU_SAT_QUYEN", [*oM("Tử Vi", "Thất Sát"), has("palace.tu_hoa", "Hóa Quyền")], "tu_sat_quyen_hien_dat", "verified", "p.22", "công danh hiển đạt (Tử Vi chế được Thất Sát lại có Hóa Quyền)"),
 ("Mệnh", "TU_LOC_NHAT_NGUYET", [*oM("Tử Vi"), anyof(has(OWN, "Lộc Tồn"), has("palace.tu_hoa", "Hóa Lộc")), has(TPM, "Thái Dương"), has(TPM, "Thái Âm")], "tu_vi_loc_nhat_nguyet_dai_quy", "draft", "p.22", "rất quý (Tử Vi cùng cung Lộc, có Nhật Nguyệt chiếu); 'Lộc' đọc là Lộc Tồn hoặc Hóa Lộc: giả định của hệ thống"),
 ("Mệnh", "CNDL_CONG_CHUC", [*[has(TPM, s) for s in ("Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương")], nt(anyof(*[has(TPS, s) for s in ("Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt")]))], "huong_cong_chuc", "verified", "p.24", "chỉ ở mức công chức bình thường nếu không có cát tinh khác trợ lực (Mệnh đủ bốn sao Cơ Nguyệt Đồng Lương trong tam phương)"),
 ("Mệnh", "DUONG_NGO_NAM", [br("Ngọ"), *oM("Thái Dương"), ys("Canh", "Tân", "Đinh", "Kỷ")], "duong_ngo_tuoi_tot_phu_quy", "verified", "p.26", "phú quý song toàn (Thái Dương ở Ngọ, người tuổi Canh, Tân, Đinh hoặc Kỷ)"),
 ("Mệnh", "DUONG_THAN", [br("Thân"), *oM("Thái Dương")], "duong_mui_dau_cham_sau_luoi", "verified", "p.26", "lúc đầu chăm chỉ, về sau dễ chểnh mảng (Thái Dương ở Thân)"),
 ("Mệnh", "DONG_TUAT_KY_DINH", [br("Tuất"), *oM("Thiên Đồng"), has("palace.tu_hoa", "Hóa Kỵ"), ys("Đinh")], "dong_tuat_ky_tuoi_dinh_tot", "verified", "p.28", "lại tốt (Thiên Đồng ở Tuất gặp Hóa Kỵ, người tuổi Đinh)"),
 ("Thiên Di", "VU_KHUC", [*oM("Vũ Khúc")], "vu_thien_di_buon_ban_lon", "verified", "p.27", "hợp việc buôn bán lớn (Vũ Khúc đóng cung Thiên Di)"),
 ("Tài Bạch", "VU_THAM", [*oM("Vũ Khúc", "Tham Lang")], "vu_tham_tai_dien_hoanh_phat", "verified", "p.27", "dễ phát về tiền bạc (Vũ Khúc đi đôi Tham Lang ở Tài Bạch)"),
 ("Điền Trạch", "VU_THAM", [*oM("Vũ Khúc", "Tham Lang")], "vu_tham_tai_dien_hoanh_phat", "verified", "p.27", "dễ phát về tiền bạc (Vũ Khúc đi đôi Tham Lang ở Điền Trạch)"),
 ("Mệnh", "VU_KINH_DOANH", [*oM("Vũ Khúc"), anyof(*oM("Liêm Trinh", "Tham Lang", "Thất Sát"))], "vu_nhom_kinh_doanh", "verified", "p.27", "hợp nghề kinh doanh (Vũ Khúc cùng Liêm Trinh, Tham Lang hoặc Thất Sát)"),
 ("Mệnh", "VU_PHA", [*oM("Vũ Khúc", "Phá Quân")], "vu_pha_kho_giu_co_nghiep", "verified", "p.27", "vất vả, khó giữ cơ nghiệp nhà (Vũ Khúc gặp Phá Quân)"),

 ("Mệnh", "PHU_TUONG_NGO_TUAT_GIAP", [br("Ngọ", "Tuất"), *oM("Thiên Phủ"), has(TPM, "Thiên Tướng"), ys("Giáp")], "phu_tuong_ngo_tuat_giap_cao_quy", "verified", "p.31", "địa vị rất cao (Thiên Phủ ở Ngọ hoặc Tuất có Thiên Tướng chầu, người tuổi Giáp)"),
 ("Mệnh", "PHU_TUONG_TRIEU_VIEN", [br("Dần", "Thân"), has(TPM, "Thiên Phủ"), has(TPM, "Thiên Tướng"), nt(anyof(*oM("Thiên Phủ", "Thiên Tướng")))], "phu_tuong_trieu_vien_luong_cao", "verified", "p.31", "thượng cách, thu nhập và bổng lộc cao (Mệnh Dần/Thân, Phủ Tướng ở Tài Bạch và Quan Lộc chầu vào)"),
 ("Mệnh", "PHU_LOC_XUONG_KHUC", [*oM("Thiên Phủ"), has(TPS, "Lộc Tồn"), has(TPS, "Văn Xương"), has(TPS, "Văn Khúc")], "phu_loc_xuong_khuc_du_da", "verified", "p.31", "của cải dư dả (Thiên Phủ gặp Lộc Tồn, Xương Khúc)"),
 ("Mệnh", "PHU_XUONG_KHUC_TA_HUU", [*oM("Thiên Phủ"), anyof(has(TPS, "Văn Xương"), has(TPS, "Văn Khúc")), anyof(has(TPS, "Tả Phụ"), has(TPS, "Hữu Bật"))], "phu_hoc_van_danh_vong", "draft", "p.31", "học vấn đỗ đạt cao (Thiên Phủ gặp Xương Khúc, Tả Hữu); 'gặp' đọc là hội trong tam phương"),
 ("Tài Bạch", "PHU_VU_QUYEN_LOC", [*oM("Thiên Phủ", "Vũ Khúc"), anyof(has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc"), has(OWN, "Lộc Tồn"))], "phu_vu_tai_dien_giau", "verified", "p.31", "giàu có (Thiên Phủ, Vũ Khúc ở Tài Bạch được Quyền, Lộc hoặc Lộc Tồn tụ vào)"),
 ("Điền Trạch", "PHU_VU_QUYEN_LOC", [*oM("Thiên Phủ", "Vũ Khúc"), anyof(has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc"), has(OWN, "Lộc Tồn"))], "phu_vu_tai_dien_giau", "verified", "p.31", "giàu có (Thiên Phủ, Vũ Khúc ở Điền Trạch được Quyền, Lộc hoặc Lộc Tồn tụ vào)"),
 ("Mệnh", "PHU_TUAT_GIAP_KY", [br("Tuất"), *oM("Thiên Phủ"), noSat, ys("Giáp", "Kỷ")], "phu_tuat_giap_ky_kha_gia", "verified", "p.31", "khá giả (Thiên Phủ ở Tuất không bị Tứ Sát xung phá, người tuổi Giáp hoặc Kỷ)"),
 ("Phu Thê", "AM_VAN_KHUC", [*oM("Thái Âm"), has(OWN, "Văn Khúc")], "phu_the_am_khuc_hoi_bat_doi_sang", "verified", "p.31", "bạn đời có địa vị, sang quý (Thái Âm đồng cung Văn Khúc ở Phu Thê)"),
 ("Mệnh", "AM_VU_LOC_TA_HUU", [*oM("Thái Âm"), has(TPM, "Vũ Khúc"), has(TPS, "Lộc Tồn"), anyof(has(TPS, "Tả Phụ"), has(TPS, "Hữu Bật"))], "am_vu_loc_ta_huu_giau_sang", "draft", "p.31", "giàu sang (Thái Âm gặp Vũ Khúc, Lộc Tồn, Tả Hữu); 'gặp' đọc là hội trong tam phương"),
 ("Mệnh", "AM_TY_BINH_DINH", [br("Tý"), *oM("Thái Âm"), ys("Bính", "Đinh")], "am_ty_tuoi_binh_dinh_phu_quy", "verified", "p.31", "giàu sang, trung tín (Thái Âm ở Tý, người tuổi Bính hoặc Đinh)"),
 ("Mệnh", "AM_HOI", [br("Hợi"), *oM("Thái Âm")], "am_hoi_phu_quy_chuc_cao", "verified", "p.32", "nắm chức quyền cao (Thái Âm ở Hợi: trăng sáng cửa trời)"),
 ("Mệnh", "THAM_HOA_LINH_TU_MO", [br("Thìn", "Tuất", "Sửu", "Mùi"), *oM("Tham Lang"), anyof(has(OWN, "Hỏa Tinh"), has(OWN, "Linh Tinh"))], "tham_hoa_linh_tu_mo_quyen_the", "verified", "p.33", "giàu có, quyền thế (Tham Lang gặp Hỏa hoặc Linh ở Tứ Mộ)"),
 ("Mệnh", "THAM_VU_MUON", [*oM("Tham Lang", "Vũ Khúc")], "tham_vu_muon_phat_sau_40", "verified", "p.33", "công danh có thể rực rỡ nhưng đến muộn, thường ngoài 40 tuổi (Tham Lang đi với Vũ Khúc)"),
 ("Mệnh", "CU_NHAT_DAN", [br("Dần"), *oM("Cự Môn", "Thái Dương")], "cu_nhat_dan_danh_loc", "verified", "p.34", "danh tiếng và bổng lộc (Cự Nhật thủ Mệnh ở Dần)"),
 ("Mệnh", "DUONG_TY_CU_HOI", [br("Tỵ"), *oM("Thái Dương"), has(TPM, "Cự Môn")], "duong_ty_loc_lau_dai", "verified", "p.34", "danh tiếng và bổng lộc (Cự Môn ở Hợi, Thái Dương thủ Mệnh ở Tỵ)"),
 ("Mệnh", "DUONG_HOI_CU_TY", [br("Hợi"), *oM("Thái Dương"), has(TPM, "Cự Môn")], "duong_hoi_cong_danh_trac_tro", "verified", "p.34", "kém thuận vì Thái Dương rơi vào thế yếu (Cự Môn ở Tỵ, Thái Dương thủ Mệnh ở Hợi)"),
 ("Mệnh", "CU_CO_MAO_TUOI", [br("Mão"), *oM("Cự Môn", "Thiên Cơ"), ys("Ất", "Tân", "Kỷ", "Bính")], "cu_co_mao_cong_khanh", "verified", "p.34", "có thể lên đến địa vị cao (Cự Cơ ở Mão, người tuổi Ất, Tân, Kỷ hoặc Bính)"),
 ("Mệnh", "CU_TY_NGO_TAM_HOA", [br("Tý", "Ngọ"), *oM("Cự Môn"), *TAM3], "cu_ngoc_trong_da", "verified", "p.34", "như ngọc ẩn trong đá, hưởng phúc lớn (Cự Môn ở Tý hoặc Ngọ hội Khoa, Quyền, Lộc)"),
 ("Mệnh", "TUONG_HUU_BAT", [*oM("Thiên Tướng"), has(OWN, "Hữu Bật")], "tuong_huu_bat_phuc_lanh", "verified", "p.36", "dễ gặp điều tốt lành (Thiên Tướng đi cặp Hữu Bật)"),
 ("Mệnh", "LUONG_NGO", [br("Ngọ"), *oM("Thiên Lương")], "luong_ngo_chuc_lon_trieu_dinh", "verified", "p.37", "có thể giữ chức vị lớn (Thiên Lương thủ Mệnh ở Ngọ)"),
 ("Mệnh", "CNDL_DAN_THAN", [br("Dần", "Thân"), *[has(TPM, s) for s in ("Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương")]], "cndl_dan_than_suon_se", "verified", "p.37", "làm ăn suôn sẻ, sáng suốt (Cơ Nguyệt Đồng Lương hội ở Mệnh tại Dần hoặc Thân)"),
 ("Mệnh", "LUONG_TY_XUONG_LOC_NHAT", [br("Tý"), *oM("Thiên Lương"), has(TPS, "Văn Xương"), has(TPS, "Lộc Tồn"), has(TPM, "Thái Dương")], "luong_ty_xuong_loc_nhat_do_dat", "verified", "p.37", "thi cử nổi bật, đỗ đạt cao (Thiên Lương thủ Mệnh ở Tý, Xương Lộc hội, Nhật chiếu)"),
 ("Mệnh", "LUONG_XUONG", [*oM("Thiên Lương"), has(OWN, "Văn Xương"), dig("Thiên Lương", GOOD)], "luong_xuong_hien_dat", "verified", "p.38", "hiển đạt (Thiên Lương hội Văn Xương ở thế miếu vượng)"),
 ("Mệnh", "LUONG_MA", [*oM("Thiên Lương"), has(OWN, "Thiên Mã")], "luong_ma_hay_di_chuyen", "verified", "p.38", "phong lưu, thích phiêu lãng, hay di chuyển (Thiên Lương hội Thiên Mã)"),
 ("Thiên Di", "LUONG_CAT", [*oM("Thiên Lương"), anyof(has(TPS, "Văn Xương"), has(TPS, "Văn Khúc"), has(TPS, "Tả Phụ"), has(TPS, "Hữu Bật"), has(TPS, "Thiên Khôi"), has(TPS, "Thiên Việt"))], "luong_thien_di_buon_ban_lon", "draft", "p.38", "hợp buôn bán lớn (Thiên Lương ở Thiên Di nhiều sao tốt trợ); 'nhiều sao tốt' đọc là có ít nhất một cát tinh"),
 ("Mệnh", "SAT_TU_MENH", [br("Dần", "Thân", "Tý", "Ngọ"), *oM("Thất Sát")], "sat_tu_tinh_phu_quy", "verified", "p.39", "tước lộc, vinh hiển (Thất Sát thủ Mệnh ở Dần, Thân, Tý hoặc Ngọ)"),
 ("Mệnh", "PHA_TY_NGO_VO_SAT", [br("Tý", "Ngọ"), *oM("Phá Quân"), noSat], "pha_ty_ngo_vo_sat_quan_cao", "draft", "p.40", "có thể giữ địa vị cao (Phá Quân thủ Mệnh ở Tý hoặc Ngọ, không gặp sát tinh); 'không gặp' đọc là không có trong tam phương"),
 ("Mệnh", "PHA_TY_NGO_GIAP_QUY", [br("Tý", "Ngọ"), *oM("Phá Quân"), ys("Giáp", "Quý")], "pha_ty_ngo_hop_tuoi_giap_quy", "verified", "p.40", "đặc biệt hợp người tuổi Giáp hoặc Quý (Phá Quân thủ Mệnh ở Tý hoặc Ngọ)"),
]
rules, claims = [], {}
for pal, rid, conds, claim, status, loc, vi in R:
    rules.append({"id": "TV_TT_" + unicodedata.normalize("NFD", pal.replace("Đ", "D")).encode("ascii", "ignore").decode().upper().replace(" ", "_") + "_" + rid, "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "tt_phu",
        "description": f"Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục), paraphrased: {vi} [TT {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": claim, "effect": "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_TOAN_THU"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims.setdefault(claim, "khuynh hướng " + vi.split(" (")[0] + (" (" + vi.split(" (", 1)[1] if " (" in vi else ""))
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), ids
json.dump({"sources": [], "rules": rules}, open(D / "pack_toan_thu.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
