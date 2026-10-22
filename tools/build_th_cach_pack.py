"""Generates data/pack_thuc_hanh_cach.json from Tử Vi Thực Hành pp.72-77 (quý cách / bần tiện cách by named patterns, sinh-vượng-bại-tuyệt địa,
mùa và giờ sinh, Thân cư, phi thường cách, nghề nghiệp). Paraphrased with page cites. Geometry uses typed facts palace.rel.*
(self/opp/trine/flank/nhi_hop). Only verified-placement stars are consumed (aux_stars are unverified and deliberately not used)."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPS, TPH = "palace.own_stars", "palace.own_major_stars", "palace.rel.tp_stars", "palace.rel.tp_hoa"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
eq = lambda f, v: {"fact": f, "operator": "eq", "value": v}
anyof = lambda *x: {"any": list(x)}
allof = lambda *x: {"all": list(x)}
nt = lambda x: {"not": x}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
nbr = lambda *b: {"fact": "palace.branch", "operator": "not_in", "value": list(b)}
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}
own = lambda *ss: [has(OWN, s) for s in ss]
tp = lambda *ss: [has(TPS, s) for s in ss]
flank = lambda *ss: [has("palace.rel.flank_stars", s) for s in ss]
TUMO = ("Thìn", "Tuất", "Sửu", "Mùi")
GOOD = ["miếu", "vượng", "đắc"]
MV = ["miếu", "vượng"]
TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})
LOC = anyof(has(OWN, "Lộc Tồn"), has("palace.tu_hoa", "Hóa Lộc"))
SAT_TP = anyof(*tp("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh"))
CATN = lambda n: {"fact": "palace.khi.cat_tp", "operator": "gte", "value": n}
P = lambda name: {"fact": "palace.name", "value": name}
THAN = {"fact": "palace.is_than", "value": True}
R = []  # (scope, id, conds, [(claim, effect)], status, page, phrase)
def add(scope, rid, conds, claims, status, page, phrase):
    R.append((scope, rid, conds, claims if isinstance(claims, list) else [(claims, "support")], status, page, phrase))

# --- quý cách (pp.72-73), on the Mệnh palace
Q = "Mệnh"
add(Q, "TU_PHU", own("Tử Vi", "Thiên Phủ"), "cach_tu_phu_dong_cung", "verified", "p.72", "cách Tử Phủ đồng cung ở Mệnh")
add(Q, "THAM_VU", own("Tham Lang", "Vũ Khúc") + [br("Sửu", "Mùi")], "cach_tham_vu_dong_hanh", "verified", "p.72", "cách Tham Vũ đồng hành (Sửu hoặc Mùi có Mệnh)")
add(Q, "NHAT_NGUYET", own("Thái Dương", "Thái Âm"), "cach_nhat_nguyet_dong_cung", "verified", "p.72", "cách Nhật Nguyệt đồng cung")
add(Q, "CU_NHAT", own("Cự Môn", "Thái Dương"), "cach_cu_nhat_dong_cung", "verified", "p.72", "cách Cự Nhật đồng cung (ở Dần tốt hơn ở Thân)")
add(Q, "CU_CO", own("Cự Môn", "Thiên Cơ") + [br("Mão", "Dậu")], "cach_cu_co_dong_cung", "verified", "p.72", "cách Cự Cơ đồng cung ở Mão hoặc Dậu")
add(Q, "TA_HUU", own("Tả Phụ", "Hữu Bật"), "cach_ta_huu_dong_cung", "verified", "p.72", "cách Tả Hữu đồng cung")
add(Q, "XK_SUU_MUI", own("Văn Xương", "Văn Khúc") + [br("Sửu", "Mùi")], "cach_van_que_van_hoa", "verified", "p.72", "cách Văn Quế, Văn Hoa (Xương Khúc đồng cung ở Sửu hoặc Mùi: thượng cách)")
add(Q, "VU_VAN_VO", [has(OWNM, "Vũ Khúc"), dig("Vũ Khúc", MV), anyof(*tp("Văn Xương", "Văn Khúc"))], "cach_vu_khuc_van_vo", "verified", "p.72", "cách Vũ Khúc văn võ (Vũ Khúc nhập miếu hợp Xương, Khúc: văn võ toàn tài)")
add(Q, "KHOI_VIET", [anyof(allof(has(OWN, "Thiên Khôi"), has("palace.rel.opp_stars", "Thiên Việt")), allof(has(OWN, "Thiên Việt"), has("palace.rel.opp_stars", "Thiên Khôi")))], "cach_thien_at_quy_nhan", "verified", "p.72", "cách Thiên Ất quý nhân (Khôi, Việt chiếu Mệnh)")
add(Q, "GIAP_TA_HUU", flank("Tả Phụ", "Hữu Bật"), "cach_quy_tinh_giap_menh", "verified", "p.72", "cách quý tinh giáp Mệnh (Tả, Hữu kẹp hai bên)")
add(Q, "GIAP_XK", flank("Văn Xương", "Văn Khúc"), "cach_quy_tinh_giap_menh", "verified", "p.72", "cách quý tinh giáp Mệnh (Xương, Khúc kẹp hai bên)")
add(Q, "GIAP_KV", flank("Thiên Khôi", "Thiên Việt"), "cach_quy_tinh_giap_menh", "verified", "p.72", "cách quý tinh giáp Mệnh (Khôi, Việt kẹp hai bên)")
add(Q, "GIAP_NN", [has(OWNM, "Thiên Phủ"), br("Sửu", "Mùi")] + flank("Thái Dương", "Thái Âm"), "cach_quy_tinh_giap_menh", "verified", "p.72", "cách quý tinh giáp Mệnh (Thiên Phủ ở Sửu/Mùi, giáp Nhật và Nguyệt)")
add(Q, "PHA_MAO_DAU", own("Phá Quân") + [br("Mão", "Dậu")], "cach_pha_quan_mao_dau", "verified", "p.72", "cách Phá Quân ở Mão hoặc Dậu (chỉ ở hai cung này mới hợp cách tốt)")
for pal in ("Mệnh", "Tài Bạch", "Quan Lộc", "Thiên Di"):
    add(pal, "LOC_MA", [LOC, has(OWN, "Thiên Mã")], "cach_loc_ma_giao_tri", "verified", "p.72", f"cách Lộc Mã giao trì (Lộc và Mã đồng cung) ở cung {pal}")
add(Q, "NN_TINH_MINH", [anyof(allof(has(OWNM, "Thái Dương"), br("Thìn", "Tỵ")), allof(has(OWNM, "Thái Âm"), br("Dậu", "Tuất")))], "cach_nhat_nguyet_tinh_minh", "verified", "p.72", "cách Nhật Nguyệt tịnh minh (Nhật ở Thìn/Tỵ, Nguyệt ở Dậu/Tuất)")
add(Q, "NHAT_NGO", own("Thái Dương") + [br("Ngọ")], "cach_nhat_le_trung_thien", "verified", "p.72", "cách Nhật lệ trung thiên (Thái Dương cư Ngọ có Mệnh)")
add(Q, "NHAT_MAO", own("Thái Dương") + [br("Mão")], "cach_nhat_chieu_loi_mon", "verified", "p.73", "cách Nhật chiếu lôi môn (Thái Dương ở Mão có Mệnh)")
add(Q, "NGUYET_HOI", own("Thái Âm") + [br("Hợi")], "cach_nguyet_lang_thien_mon", "verified", "p.73", "cách Nguyệt lãng thiên môn (Thái Âm ở Hợi có Mệnh)")
add(Q, "NGUYET_TY", own("Thái Âm") + [br("Tý")], "cach_nguyet_sinh_thuong_hai", "verified", "p.73", "cách Nguyệt sinh thương hải (Thái Âm ở Tý)")
add(Q, "SONG_LOC", own("Lộc Tồn") + [has("palace.tu_hoa", "Hóa Lộc")], "cach_song_loc", "verified", "p.72", "cách Song Lộc (Lộc Tồn và Hóa Lộc cùng đóng Mệnh, đẹp hơn là chiếu về)")
add(Q, "NN_CHIEU_BICH", [br("Sửu", "Mùi"), has("palace.rel.opp_majors", "Thái Dương"), has("palace.rel.opp_majors", "Thái Âm")], "cach_nhat_nguyet_chieu_bich", "verified", "p.73", "cách Nhật Nguyệt chiếu bích (Nhật, Nguyệt ở Sửu chiếu Mùi có Mệnh, hoặc ngược lại)")
for pal in ("Mệnh", "Quan Lộc"):
    add(pal, "KIM_DU", own("Tử Vi") + [anyof(allof(*flank("Tả Phụ", "Hữu Bật")), allof(*flank("Thiếu Dương", "Thiếu Âm")))], "cach_kim_du_phu_gia", "verified", "p.73", f"cách Kim dư phù giá (Tử Vi ở cung {pal} giáp Tả Hữu hoặc Thiếu Dương, Thiếu Âm)")
    add(pal, "PHU_BAT", own("Tử Vi") + [has(TPS, "Tả Phụ"), has(TPS, "Hữu Bật")], "cach_phu_bat_cung_de", "verified", "p.73", f"cách Phụ Bật củng đế (Tử Vi ở cung {pal}, Tả Hữu hợp chiếu)")
    add(pal, "THAM_HOA", own("Tham Lang") + [br(*TUMO), has(TPS, "Hỏa Tinh")], "cach_tham_hoa_tuong_hoi", "verified", "p.73", f"cách Tham Hỏa tương hội (cung {pal} ở Tứ mộ có Tham Lang gặp Hỏa: phát về võ hoặc kinh thương)")
    add(pal, "LOC_MA_BOI_AN", own("Thiên Tướng") + [dig("Thiên Tướng", GOOD)] + flank("Lộc Tồn", "Thiên Mã"), "cach_loc_ma_boi_an", "verified", "p.73", f"cách Lộc Mã bội ấn (cung {pal} có Thiên Tướng đắc địa, Lộc và Mã giáp hai bên)")
add(Q, "SAT_TRIEU_DAU", own("Thất Sát") + [br("Dần", "Thân")], "cach_that_sat_trieu_dau", "verified", "p.73", "cách Thất Sát triều đẩu (Dần hoặc Thân có Mệnh)")
add(Q, "SAT_NGUONG_DAU", own("Thất Sát") + [br("Ngọ")], "cach_that_sat_nguong_dau", "verified", "p.73", "cách Thất Sát ngưỡng đẩu (Thất Sát cư Ngọ)")
add(Q, "PHA_TY_NGO", own("Phá Quân") + [br("Tý", "Ngọ")], [("cach_pha_quan_ty_ngo_hoanh_phat", "support"), ("cach_pha_quan_ty_ngo_hoanh_pha", "limit")], "verified", "p.73", "Phá Quân ở Tý, Ngọ: hoạnh phát nhưng cũng hoạnh phá")
add(Q, "TA_HUU_TU_MO", own("Tả Phụ", "Hữu Bật") + [br(*TUMO)], "cach_ta_huu_tu_mo", "verified", "p.73", "cách Tả Hữu Tứ mộ (Tả, Hữu đồng cung ở Tứ mộ)")
add(Q, "KINH_NHAP_MIEU", own("Kình Dương") + [br(*TUMO), {"fact": "chart.year_branch", "operator": "in", "value": list(TUMO)}], "cach_kinh_duong_nhap_mieu", "verified", "p.73", "cách Kình Dương nhập miếu (Kình ở Tứ mộ và tuổi thuộc Tứ mộ)")
add(Q, "MINH_AM_LOC", [anyof(allof(has(OWN, "Lộc Tồn"), has("palace.rel.nhi_hop_hoa", "Hóa Lộc")), allof(has("palace.tu_hoa", "Hóa Lộc"), has("palace.rel.nhi_hop_stars", "Lộc Tồn")))], "cach_minh_loc_am_loc", "verified", "p.73", "cách Minh Lộc, Ám Lộc (Mệnh có Lộc, cung nhị hợp có Lộc Tồn hoặc ngược lại: 'uyên ương lộc hội')")
add(Q, "CHUNG_THUY", [br("Mão", "Dậu"), has(OWN, "Đại Hao"), has(OWN, "Tiểu Hao")], "cach_chung_thuy_trieu_dong", "verified", "p.73", "cách Chúng thuỷ triều đông (Mệnh ở Mão, Dậu có song Hao)")
# --- bần tiện cách (pp.73-74)
add(Q, "BT_SINH_BAT_PHUNG", own("Liêm Trinh") + [br("Dần", "Thân"), TT], [("cach_sinh_bat_phung_thoi", "limit")], "verified", "p.73", "cách Sinh bất phùng thời (Liêm Trinh ở Dần/Thân gặp Tuần hoặc Triệt án ngữ)")
add(Q, "BT_THAT_SINH", own("Phá Quân") + [br("Dần", "Thân"), SAT_TP], [("cach_that_sinh_co_ban", "limit")], "draft", "p.73", "cách Thất sinh cô bần (Phá Quân ở Dần/Thân gặp sát tinh); 'gặp' đọc là hội trong tam phương tứ chính")
add(Q, "BT_LOC_LUONG_SAT", [LOC, has(OWN, "Địa Không"), has(OWN, "Địa Kiếp")], [("cach_loc_phung_luong_sat", "limit")], "verified", "p.73", "cách Lộc phùng lưỡng sát (Lộc Tồn hoặc Hóa Lộc ở Mệnh gặp Không, Kiếp đồng cung)")
add(Q, "BT_MA_LAC", own("Thiên Mã") + [TT], [("cach_ma_lac_khong_vong", "limit")], "verified", "p.74", "cách Mã lạc Không vong (Thiên Mã ở Mệnh gặp Tuần hoặc Triệt án ngữ)")
add(Q, "BT_TAI_TU_CUU", [anyof(allof(has(OWNM, "Vũ Khúc"), dig("Vũ Khúc", ["hãm"])), allof(has(OWNM, "Liêm Trinh"), dig("Liêm Trinh", ["hãm"]))), SAT_TP], [("cach_tai_du_tu_cuu", "limit")], "draft", "p.74", "cách Tài dữ tù cừu (Vũ hoặc Liêm hãm ở Mệnh gặp sát tinh); 'gặp' đọc là hội")
add(Q, "BT_NN_TAN_HUNG", [anyof(allof(has(OWNM, "Thái Dương"), dig("Thái Dương", ["hãm"])), allof(has(OWNM, "Thái Âm"), dig("Thái Âm", ["hãm"]))), SAT_TP], [("cach_nhat_nguyet_tan_hung", "limit")], "draft", "p.74", "cách Nhật Nguyệt tàn hung (Nhật hoặc Nguyệt hãm ở Mệnh gặp sát tinh); sách còn nói 'không có cứu tinh' mà hệ thống chưa kiểm")
add(Q, "BT_KK_SAT", [anyof(*own("Địa Không", "Địa Kiếp")), nbr("Tỵ", "Hợi", "Dần", "Thân"), anyof(*tp("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh"))], [("cach_khong_kiep_sat_hoi", "limit")], "verified", "p.74", "cách Không Kiếp sát hội (Mệnh có Không hoặc Kiếp hãm địa, hội sát tinh khác)")
# --- sinh / vượng / bại / tuyệt địa (p.74) and season/hour of birth (pp.75-76): chart-level facts, read on the Mệnh palace
add(Q, "SV_SINH_VUONG", [{"fact": "chart.menh_stage_th", "operator": "in", "value": ["sinh", "vuong"]}], "menh_sinh_vuong_dia", "draft", "p.74", "Mệnh an ở sinh địa hoặc vượng địa của hành bản mệnh (nền thuận); sách nêu bảng nhưng chỉ nói rõ phần bại, tuyệt")
add(Q, "SV_CUU_GIAI", [{"fact": "chart.menh_stage_th", "operator": "in", "value": ["bai", "tuyet"]}, has("palace.rel.tp_hoa", "Hóa Khoa"), has("palace.rel.tp_hoa", "Hóa Quyền"), has("palace.rel.tp_hoa", "Hóa Lộc")], "menh_tuyet_xu_phung_sinh", "verified", "p.74", "Mệnh an ở bại địa hoặc tuyệt địa nhưng được Tam Hóa hội: 'tuyệt xứ phùng sinh', được cứu giải")
add(Q, "SV_BAI_TUYET", [{"fact": "chart.menh_stage_th", "operator": "in", "value": ["bai", "tuyet"]}, nt(allof(*[has("palace.rel.tp_hoa", h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")])), {"fact": "palace.has_no_major", "value": True}], [("menh_bai_tuyet_dia_tham_tram", "limit")], "verified", "p.74", "Mệnh ở bại hoặc tuyệt địa, không Tam Hóa hội và không có chính diệu sinh bản mệnh: cuộc đời thăng trầm đáng ngại")
add(Q, "MUA_SINH", [{"fact": "chart.season_relation", "operator": "in", "value": ["vuong", "tuong"]}], "menh_thuan_mua_sinh", "verified", "p.75", "thuận mùa sinh (Mệnh Vượng hoặc Mệnh Tướng theo mùa): độ số được tăng; mùa lấy theo tháng âm 1-3 xuân, 4-6 hạ, 7-9 thu, 10-12 đông")
add(Q, "GIO_SINH", [eq("chart.hour_matches_season", True)], "menh_thuan_gio_sinh", "verified", "p.76", "thuận giờ sinh (mùa xuân giờ Dậu/Thìn/Tỵ, hạ Mão/Mùi/Hợi, thu Ngọ/Thân/Dần, đông Sửu/Tuất/Tý): độ số gia tăng")
add(Q, "THUAN_LY", [eq("chart.hour_menh_polarity", "thuan_ly")], "menh_gio_thuan_ly", "verified", "p.76", "giờ sinh thuận lý (giờ dương mà Mệnh an ở cung dương, giờ âm mà Mệnh ở cung âm): độ số gia tăng")
add(Q, "NGHICH_LY", [eq("chart.hour_menh_polarity", "nghich_ly")], [("menh_gio_nghich_ly", "limit")], "verified", "p.76", "giờ sinh nghịch lý (giờ dương mà Mệnh ở cung âm hoặc ngược lại): độ số bị kém bớt")
# --- Thân cư (p.75)
add("Thiên Di", "THAN", [THAN, anyof(*tp("Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"))], "than_cu_di_lap_nghiep_xa", "verified", "p.75", "Thân cư Thiên Di có cát tinh hội: lập nghiệp phương xa thịnh vượng")
add("Tài Bạch", "THAN_TU_VI", [THAN] + own("Tử Vi"), "than_cu_tai_co_danh_gia_tien_tai", "verified", "p.75", "Thân cư Tài Bạch có Tử Vi tọa thủ: có danh giá hoặc tiền tài")
# page image checked 2026-10-22 (TH p.75 "Quan Lộc: Có Tuần Triệt, Kiếp Hỏa, Kỵ hội đàn ông muộn công danh"): verified with the page's own
# gender condition; the women's line of the same entry (Tuần Triệt hội sát tinh …) is not built
add("Quan Lộc", "THAN_TT", [THAN, eq("chart.gender", "nam"), anyof(TT, *tp("Địa Kiếp", "Hỏa Tinh"), has(TPH, "Hóa Kỵ"))], [("than_cu_quan_muon_cong_danh", "limit")], "verified", "p.75", "công danh đến muộn (Thân cư Quan Lộc gặp Tuần Triệt, Kiếp Hỏa hoặc Hóa Kỵ hội; sách nói cho đàn ông)")
# the next sentence of the same entry, read on the page image 2026-10-22: "Nếu có Cát tinh hội cũng phải ngoài 40 tuổi mới nhẹ bước thanh vân"
# (still the men's line, still with Tuần Triệt / Kiếp Hỏa / Kỵ); cát tinh = the six the Thiên Di line of the same page is built with
add("Quan Lộc", "THAN_TT_CAT", [THAN, eq("chart.gender", "nam"), anyof(TT, *tp("Địa Kiếp", "Hỏa Tinh"), has(TPH, "Hóa Kỵ")),
    anyof(*tp("Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"))], [("than_cu_quan_cat_ngoai_40", "limit")], "verified", "p.75",
    "dù có cát tinh hội, cũng phải ngoài 40 tuổi mới nhẹ bước thanh vân (Thân cư Quan Lộc gặp Tuần Triệt, Kiếp Hỏa hoặc Hóa Kỵ hội, lại có cát tinh hội; sách nói cho đàn ông)")
# --- phi thường / nghề nghiệp (pp.76-77)
MAJ4 = ("Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng")
add(Q, "PHI_THUONG", [anyof(*[allof(has(OWNM, s), dig(s, MV)) for s in MAJ4]), CATN(2)], "cach_phi_thuong", "draft", "p.76", "phi thường cách (Tử, Phủ, Vũ, Tướng nhập miếu ở Mệnh, hội nhiều cát tinh); ngưỡng 'nhiều cát tinh' là quy ước của hệ thống (từ hai sao trở lên)")
add("Thiên Di", "THAN_SPLT", [THAN, anyof(*[allof(has(OWNM, s), dig(s, MV)) for s in ("Thất Sát", "Phá Quân", "Liêm Trinh", "Tham Lang")]), CATN(2)], "cach_phi_thuong_than", "draft", "p.76", "Thân cư Sát Phá Liêm Tham nhập miếu vượng, hội nhiều cát tinh: có thể phát mạnh")
add(Q, "BACH_OC", own("Thiên Tướng") + [dig("Thiên Tướng", GOOD)] + tp("Thiên Mã", "Văn Xương"), "cach_bach_oc_phat_cong_danh", "draft", "p.76", "cách bạch ốc phát công danh (Thiên Tướng đắc địa hội Thiên Mã, Văn Xương); sách còn kể Thiên Phúc nhưng sao này chưa được kiểm")
add(Q, "VCD_TAM_KHONG", [{"fact": "palace.has_no_major", "value": True}, anyof(TT, *tp("Thiên Không", "Địa Không")), CATN(1), has("palace.rel.tp_majors", "Thái Dương"), has("palace.rel.tp_majors", "Thái Âm")], "cach_vcd_tam_khong_nhat_nguyet_chieu", "draft", "p.76", "Mệnh vô chính diệu đắc tam không, hội cát tinh, có Nhật Nguyệt chiếu: có thể phát công danh khá")
CNDL = [has("palace.rel.tp_majors", s) for s in ("Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương")]
add(Q, "NGHE_IN_AN", CNDL + tp("Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc"), "nghe_cndl_in_an_thuong_gia", "draft", "p.77", "hợp nghề ấn loát, công nghệ hay làm thương gia khá (Cơ Nguyệt Đồng Lương hội Tả Hữu, Xương Khúc)")
add(Q, "NGHE_DAY_HOC", CNDL + tp("Tả Phụ", "Hữu Bật", "Thiên Khôi", "Thiên Việt", "Văn Xương", "Văn Khúc", "Tấu Thư") + [has(TPH, "Hóa Khoa"), has(TPH, "Hóa Quyền")], "nghe_cndl_day_hoc_viet_van", "draft", "p.77", "giỏi dạy học, viết văn (Cơ Nguyệt Đồng Lương hội Tả Hữu, Khôi Việt, Khoa Quyền, Xương Khúc, Tấu Thư)")
add(Q, "HA_CACH", [anyof(*[has(OWNM, s) for s in ("Thất Sát", "Phá Quân", "Liêm Trinh", "Tham Lang")]), {"fact": "palace.khi.sat_tp", "operator": "gte", "value": 3}, has(TPH, "Hóa Kỵ")], [("cach_ha_cach_lao_kho", "limit")], "draft", "p.77", "hạ cách: chính tinh Sát Phá Liêm Tham mà hung tinh, sát tinh hội nhiều, có Hóa Kỵ; đời nhiều vất vả (ngưỡng 'nhiều' = từ ba sát tinh)")

slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for scope, rid, conds, cl, status, loc, vi in R:
    rules.append({"id": f"TV_TH_CACH_{slug(scope)}_{rid}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "th_cach",
        "description": f"Tử Vi Thực Hành, cách cuộc (paraphrased), cung {scope}: {vi} [TH {loc}]",
        "conditions": {"all": [P(scope)] + conds},
        "consequences": [{"kind": "finding", "claim": c, "effect": e, "scope": "natal"} for c, e in cl],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_THUC_HANH"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    for c, e in cl:
        claims.setdefault(c, "khuynh hướng " + vi)
        if e == "limit":
            claims.setdefault("limit:" + c, "hạn chế: " + vi)
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_thuc_hanh_cach.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
