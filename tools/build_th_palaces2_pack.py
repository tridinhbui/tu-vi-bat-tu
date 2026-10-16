"""Generates data/pack_thuc_hanh_palaces2.json: verse of the other palaces and the Nữ mệnh phú, Tử Vi Thực Hành pp.96-113 (Huynh Đệ, Phu Thê, Tử Tức,
Tài Bạch, Thiên Di, Nô Bộc, Quan Lộc, Điền Trạch, Phúc Đức, Phụ Mẫu, Nữ mệnh). Paraphrased. Left out on purpose: Giải Ách (illness), death/injury/prison,
sexual-reputation lines, child-survival counts, and every line that needs the unverified auxiliary stars (Long Phượng, Cái, Hình, Riêu, Khốc Hư, Quan Phúc,
Ấn Quang, Thiên Quý, Cô Quả, Thai-Tọa...). Reading policy: đồng cung = own palace; hội/chiếu = tam phương; bare 'gặp'/'giáp' -> noted per rule."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPS, TPH, FL = "palace.own_stars", "palace.own_major_stars", "palace.rel.tp_stars", "palace.rel.tp_hoa", "palace.rel.flank_stars"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
allof = lambda *x: {"all": list(x)}
nt = lambda x: {"not": x}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}
O = lambda *ss: anyof(*[has(OWN, s) for s in ss])           # any of these stars in the palace
OA = lambda *ss: allof(*[has(OWN, s) for s in ss])          # all of these in the palace
T = lambda *ss: anyof(*[has(TPS, s) for s in ss])           # any of these in the tam phương
TA = lambda *ss: allof(*[has(TPS, s) for s in ss])
TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})
LOC = anyof(has(OWN, "Lộc Tồn"), has("palace.tu_hoa", "Hóa Lộc"))
GOOD, MV, HAM = ["miếu", "vượng", "đắc"], ["miếu", "vượng"], ["hãm"]
TUMO = ("Thìn", "Tuất", "Sửu", "Mùi")
YANG = ("Tý", "Dần", "Thìn", "Ngọ", "Thân", "Tuất")
YIN = ("Sửu", "Mão", "Tỵ", "Mùi", "Dậu", "Hợi")
G = lambda g: {"fact": "chart.gender", "value": g}
R = []
def add(pal, rid, conds, claim, status, page, phrase, effect="support"):
    R.append((pal, rid, conds, claim, effect, status, page, phrase))

# ---------- Nữ mệnh phú (pp.96-99), Mệnh palace, female only
add("Mệnh", "NU_TU_VI", [G("nữ"), O("Tử Vi")], "nu_tu_vi_hien_vuong_phu", "verified", "p.96", "người hiền, vượng phu ích tử, thêm sang giàu (nữ mệnh có Tử Vi)")
add("Mệnh", "NU_LIEM", [G("nữ"), O("Liêm Trinh"), dig("Liêm Trinh", GOOD), br("Dần", "Thân", "Tý", "Ngọ")], "nu_liem_dac_dia_trinh_nu", "verified", "p.96", "nết na, đoan chính, đáng mong (nữ mệnh Liêm Trinh đắc địa ở Dần, Thân, Tý, Ngọ)")
add("Mệnh", "NU_NHAT", [G("nữ"), has(OWNM, "Thái Dương"), br("Dần", "Mão", "Thìn", "Tỵ", "Ngọ"), {"fact": "palace.khi.cat_tp", "operator": "gte", "value": 1}], "nu_nhat_dan_ngo_phong_luu", "verified", "p.96", "tăng phong lưu (nữ mệnh Thái Dương ở Dần đến Ngọ, có cát tinh)")
add("Mệnh", "NU_PHU_TUONG", [G("nữ"), has("palace.rel.tp_majors", "Thiên Phủ"), has("palace.rel.tp_majors", "Thiên Tướng"), {"fact": "chart.year_stem", "operator": "in", "value": ["Giáp", "Canh", "Tân", "Ất"]}], "nu_phu_tuong_trieu_minh_giau", "verified", "p.96", "càng giàu, càng thanh tú (nữ mệnh có Phủ, Tướng chầu, tuổi Giáp, Canh, Tân, Ất)")
add("Mệnh", "NU_LOC_MA", [G("nữ"), anyof(has(OWN, "Lộc Tồn"), has(TPS, "Lộc Tồn")), anyof(has(OWN, "Thiên Mã"), has(TPS, "Thiên Mã"))], "nu_loc_ma_doan_trang_vuong_phu", "verified", "p.98", "đoan trang, vượng phu ích tử (nữ mệnh có Lộc Mã thủ hoặc chiếu)")
add("Mệnh", "NU_VU_QUYEN", [G("nữ"), O("Vũ Khúc"), has("palace.tu_hoa", "Hóa Quyền")], "nu_vu_quyen_khon_phu_quan_ne", "verified", "p.99", "khôn ngoan, được chồng nể vì (nữ mệnh Vũ Khúc đồng cung Hóa Quyền)")
add("Mệnh", "NU_MA_TON_DI", [G("nữ"), O("Thiên Mã"), has("palace.rel.opp_stars", "Lộc Tồn")], "nu_ma_menh_ton_di_buon_ban", "verified", "p.99", "giỏi buôn bán nhiều bề (Thiên Mã ở Mệnh, Lộc Tồn ở Thiên Di)")
# ---------- Huynh Đệ (pp.99-101)
HD = "Huynh Đệ"
add(HD, "TT", [TT], "hd_tuan_triet_anh_em_it_ly_tan", "verified", "p.99", "anh em ít, mỗi người một ngả (Tuần hoặc Triệt ở Huynh Đệ)", "limit")
add(HD, "KHONG_KIEP", [O("Địa Kiếp", "Thiên Không")], "hd_khong_kiep_anh_em_khong_nhieu", "verified", "p.99", "anh em không nhiều (Địa Kiếp hoặc Thiên Không ở Huynh Đệ)", "limit")
add(HD, "TUONG_LOC_MA", [OA("Tướng Quân", "Thiên Mã"), LOC], "hd_tuong_loc_ma_anh_em_quyen_cao", "verified", "p.99", "anh em có người thành danh, có quyền (Tướng Quân, Lộc, Mã đồng cung)")
add(HD, "TS_DV", [O("Trường Sinh", "Đế Vượng")], "hd_truong_sinh_de_vuong_da_nhan", "verified", "p.100", "anh em đông (Trường Sinh hoặc Đế Vượng ở Huynh Đệ)")
add(HD, "LOC_MA", [O("Lộc Tồn"), O("Thiên Mã")], "hd_loc_ma_buon_ban_giau", "verified", "p.100", "anh em buôn bán nên giàu (Lộc Tồn, Thiên Mã ở Huynh Đệ)")
add(HD, "PHA_KY", [O("Phá Quân"), has("palace.tu_hoa", "Hóa Kỵ")], "hd_pha_ky_bat_thuan", "draft", "p.100", "anh em bất thuận, hay tranh chấp (Phá Quân, Hóa Kỵ); sách còn kể Thiên Hình", "limit")
add(HD, "LOC_TON_IT", [O("Lộc Tồn")], "hd_loc_ton_it_anh_em", "draft", "p.100", "ít anh em (Lộc Tồn ở Huynh Đệ); câu thơ ghép với Cô Quả", "limit")
add(HD, "KHOI_VIET_HOA", [T("Thiên Khôi"), T("Thiên Việt")] + [has(TPH, h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")], "hd_khoi_viet_tam_hoa_anh_hung", "draft", "p.101", "anh em có người nổi bật (Khôi Việt, Tam Hóa hội); 'được ngôi anh hùng' đọc là hội")
# ---------- Phu Thê (pp.101-103)
PT = "Phu Thê"
add(PT, "TA_HUU_LOAN", [O("Tả Phụ", "Hữu Bật"), O("Hồng Loan")], "pt_ta_huu_loan_phu_quy", "verified", "p.101", "vợ chồng cao sang, phú quý một nhà (Tả hoặc Hữu đồng cung Hồng Loan)")
add(PT, "TUONG_DAO_HONG", [O("Thiên Tướng"), O("Đào Hoa", "Hồng Loan")], "pt_tuong_dao_hong_tot", "verified", "p.101", "hôn nhân tốt đẹp (Thiên Tướng đồng cung Đào hoặc Hồng)")
add(PT, "MA_TON_LONG", [O("Thiên Mã"), O("Lộc Tồn"), O("Thanh Long")], "pt_ma_ton_long_tot", "verified", "p.101", "hôn nhân tốt (Thiên Mã, Lộc Tồn, Thanh Long đồng cung)")
for a, b in (("Thiên Lương", "Thiên Đồng"), ("Thiên Lương", "Tử Vi"), ("Thiên Lương", "Thiên Phủ"), ("Thiên Đồng", "Tử Vi"), ("Thiên Đồng", "Thiên Phủ"), ("Tử Vi", "Thiên Phủ")):
    add(PT, f"CHINH_PHONG_{a}_{b}".replace(" ", "_"), [OA(a, b)], "pt_luong_dong_tu_phu_net_na", "draft", "p.101", "người phối ngẫu nết na, thảo ngay (Lương, Đồng, Tử, Phủ hợp bầy); 'hợp bầy' đọc là đồng cung hai sao trở lên")
add(PT, "LIEM", [O("Liêm Trinh")], "pt_liem_vien_phoi_ban_han", "draft", "p.101", "kết duyên nơi xa, hoàn cảnh còn thanh bạch (Liêm Trinh ở Phu Thê); câu thơ khó đọc", "limit")
add(PT, "CU_LINH_HOA", [O("Cự Môn"), O("Hỏa Tinh", "Linh Tinh")], "pt_cu_linh_hoa_moi_lai_tro_ngai", "verified", "p.102", "chuyện mối lái trắc trở, nhiều lần mới xong (Cự Môn gặp Linh hoặc Hỏa ở Phu Thê)", "limit")
add(PT, "PHA_TT", [O("Phá Quân"), TT], "pt_pha_tuan_triet_nhieu_lan_moi_thanh", "verified", "p.102", "hôn nhân phải qua nhiều lần mới thành (Phá Quân gặp Tuần/Triệt)", "limit")
add(PT, "VU_SAT", [OA("Vũ Khúc", "Thất Sát")], "pt_vu_sat_nhieu_lan_hon_phoi", "verified", "p.102", "hôn nhân phải qua nhiều lần mới yên (Vũ Khúc đồng cung Thất Sát)", "limit")
add(PT, "KHONG_KIEP", [O("Địa Không", "Địa Kiếp")], "pt_khong_kiep_hai_ba_do", "verified", "p.102", "hai ba lần dang dở mới toàn (Không hoặc Kiếp ở Phu Thê)", "limit")
add(PT, "TT_KHONG_KIEP", [TT, O("Địa Không", "Địa Kiếp")], "pt_tt_khong_kiep_moi_mai_dang_do", "verified", "p.102", "mối mai dang dở nhiều lần mới nên (Tuần/Triệt gặp Không, Kiếp)", "limit")
add(PT, "TUONG", [O("Thiên Tướng")], "pt_tuong_dung_dan", "draft", "p.102", "người phối ngẫu đứng đắn (Thiên Tướng ở Phu Thê)")
add(PT, "LIEM_DAC", [O("Liêm Trinh"), dig("Liêm Trinh", GOOD)], "pt_liem_dac_dia_doan_chinh", "draft", "p.102", "người phối ngẫu đoan chính (Liêm Trinh đắc địa)")
add(PT, "PHA_TIEN_TRO", [O("Phá Quân")], "pt_pha_tien_tro_hau_thanh", "draft", "p.102", "lúc đầu trắc trở, về sau mới nên (Phá Quân ở Phu Thê)", "limit")
add(PT, "XK_TA_HUU", [T("Văn Xương", "Văn Khúc"), T("Tả Phụ", "Hữu Bật")], "pt_xuong_khuc_ta_huu_tai_hoa", "draft", "p.102", "người phối ngẫu tài hoa (Xương Khúc, Tả Hữu hội); 'ấy làng tài hoa' đọc là hội")
add(PT, "LINH", [O("Linh Tinh")], "pt_linh_ha_tien", "draft", "p.102", "người phối ngẫu hà tiện (Linh Tinh ở Phu Thê)", "limit")
add(PT, "XK_TUE", [O("Văn Xương", "Văn Khúc"), O("Thái Tuế")], "pt_xuong_khuc_tue_da_ngon", "draft", "p.103", "người phối ngẫu hay nói, miệng lưỡi (Xương/Khúc đồng cung Thái Tuế)", "limit")
# ---------- Tử Tức (pp.103-105)
TU = "Tử Tức"
add(TU, "KHOI_VIET", [O("Thiên Khôi", "Thiên Việt")], "tu_khoi_viet_con_do_dau", "verified", "p.103", "con học giỏi, đỗ đạt (Khôi hoặc Việt ở Tử Tức)")
add(TU, "DONG_AM", [O("Thiên Đồng"), O("Thái Âm")], "tu_dong_am_trai_gai_du", "verified", "p.103", "có đủ cả con trai và con gái (Thiên Đồng, Thái Âm ở Tử Tức)")
add(TU, "TU_PHU", [O("Tử Vi", "Thiên Phủ")], "tu_tu_phu_con_dong_luong", "verified", "p.104", "con cái làm được việc lớn, đáng làm rường cột (Tử Vi hoặc Thiên Phủ ở Tử Tức)")
add(TU, "CO_TUONG", [O("Thiên Cơ", "Thiên Tướng")], "tu_co_tuong_muon_con_hiem", "draft", "p.104", "con muộn, số hiếm (Tướng, Cơ ở Tử Tức)", "limit")
add(TU, "NHAT_DUONG", [has(OWNM, "Thái Dương"), br(*YANG)], "tu_nhat_cung_duong_con_dau_trai", "draft", "p.104", "con đầu có xu hướng là con trai (Thái Dương ở cung dương); câu thơ khó đọc")
add(TU, "AM_AM", [has(OWNM, "Thái Âm"), br(*YIN)], "tu_am_cung_am_con_dau_gai", "draft", "p.104", "con đầu có xu hướng là con gái (Thái Âm ở cung âm); câu thơ khó đọc")
add(TU, "HIEM_CON", [T("Địa Không", "Địa Kiếp"), T("Hỏa Tinh", "Linh Tinh"), TT], "tu_khong_kiep_linh_hoa_tt_hiem_con", "verified", "p.105", "số hiếm con dù chính tinh đắc cách (Tử Tức gặp Không/Kiếp, Linh/Hỏa và Tuần/Triệt)", "limit")
# ---------- Tài Bạch (pp.105-106)
TB = "Tài Bạch"
add(TB, "VAN_TINH_TA_HUU", [O("Văn Xương", "Văn Khúc", "Tả Phụ", "Hữu Bật")], "tai_van_tinh_ta_huu_co_du", "draft", "p.105", "tiền của có dư (Xương, Khúc, Tả, Hữu ở Tài Bạch)")
add(TB, "LIEM_PHA_HOANH_PHAT", [anyof(allof(O("Liêm Trinh"), br("Dần", "Thân")), allof(O("Phá Quân"), br("Tý", "Ngọ")))], "tai_liem_pha_hoanh_phat", "verified", "p.105", "tiền của có thể phát bất ngờ (Liêm Trinh ở Dần/Thân hoặc Phá Quân ở Tý/Ngọ)")
add(TB, "CO_LUONG_LOC_MA", [OA("Thiên Cơ", "Thiên Lương"), O("Lộc Tồn"), O("Thiên Mã")], "tai_co_luong_loc_ma_giau_nhu_thach_sung", "verified", "p.105", "giàu sang lớn (Cơ, Lương, Lộc, Mã đồng cung: 'Thạch Sùng')")
add(TB, "TU_PHU_PHU_GIA", [O("Tử Vi", "Thiên Phủ")], "tai_tu_phu_phu_gia", "draft", "p.105", "nhà giàu có (Tử Vi hoặc Thiên Phủ ở Tài Bạch); sách không nêu điều kiện sáng tối")
add(TB, "KY", [has("palace.tu_hoa", "Hóa Kỵ")], "tai_hoa_ky_tien_tai_kem", "verified", "p.106", "tiền tài kém, khó dư (Hóa Kỵ ở Tài Bạch)", "limit")
add(TB, "LINH", [O("Linh Tinh")], "tai_linh_ha_tien_nen_giau", "verified", "p.106", "tiết kiệm nên giàu (Linh Tinh ở Tài Bạch)")
add(TB, "HOA_MIEU", [O("Hỏa Tinh"), dig("Hỏa Tinh", ["miếu"])], "tai_hoa_mieu_phat_nhieu_phen", "verified", "p.106", "phát tài nhiều phen (Hỏa Tinh miếu ở Tài Bạch)")
add(TB, "KHOI_VIET", [O("Thiên Khôi", "Thiên Việt")], "tai_khoi_viet_phat_thanh_cao", "draft", "p.106", "tiền của đến từ việc thanh cao (Khôi, Việt ở Tài Bạch)")
add(TB, "MA_TON", [O("Thiên Mã"), O("Lộc Tồn")], "tai_ma_ton_phu_gia", "verified", "p.106", "phường phú gia (Thiên Mã gặp Lộc Tồn ở Tài Bạch)")
add(TB, "VU_THIN_TUAT", [O("Vũ Khúc"), br("Thìn", "Tuất")], "tai_vu_thin_tuat_phu_gia", "verified", "p.106", "phường phú gia (Vũ Khúc ở Thìn hoặc Tuất)")
add(TB, "PHU_VU", [OA("Thiên Phủ", "Vũ Khúc")], "tai_phu_vu_cua_truyen_nhieu_doi", "verified", "p.106", "của cải truyền đến ba bốn đời (Thiên Phủ, Vũ Khúc một nhà)")
add(TB, "MO_LOC", [O("Mộ"), has("palace.tu_hoa", "Hóa Lộc")], "tai_mo_hoa_loc_tien_chao_moi", "verified", "p.106", "tiền của tìm đến tận tay (sao Mộ đồng cung Hóa Lộc)")
add(TB, "MO_CO_LUONG", [O("Mộ"), O("Thiên Cơ"), O("Thiên Lương")], "tai_mo_co_luong_de_kiem_de_tieu", "verified", "p.106", "tiền dễ kiếm mà cũng dễ tiêu (sao Mộ đồng cung Cơ, Lương)")
add(TB, "THAM_DONG_MV", [anyof(allof(O("Tham Lang"), dig("Tham Lang", MV)), allof(O("Thiên Đồng"), dig("Thiên Đồng", MV)))], "tai_tham_dong_bach_thu_nen_giau", "verified", "p.106", "khi xưa tay trắng, nay sang giàu (Tham hoặc Đồng miếu vượng ở Tài Bạch)")
add(TB, "HAO", [O("Đại Hao", "Tiểu Hao")], "tai_hao_tien_tan", "verified", "p.106", "tiền bạc hao tán (Đại hoặc Tiểu Hao ở Tài Bạch)", "limit")
add(TB, "DA_KHONG", [O("Đà La"), O("Địa Không")], "tai_da_khong_ngheo_kho", "draft", "p.106", "nghèo khó (Đà La, Địa Không ở Tài Bạch)", "limit")
add(TB, "CO_TUE", [O("Thiên Cơ"), O("Thái Tuế")], "tai_co_tue_gian_nan", "draft", "p.106", "kiếm tiền gian nan mọi đường (Thiên Cơ, Thái Tuế ở Tài Bạch)", "limit")
add(TB, "KHONG_KIEP", [O("Địa Không", "Địa Kiếp")], "tai_khong_kiep_khon_kho", "verified", "p.106", "tiền bạc khốn khó (Kiếp hoặc Không ở Tài Bạch)", "limit")
add(TB, "HOA_LINH", [O("Hỏa Tinh", "Linh Tinh")], "tai_hoa_linh_bien_lan", "draft", "p.106", "bủn xỉn, so đo (Hỏa hoặc Linh ở Tài Bạch)", "limit")
add(TB, "PHA_HAO_KK", [O("Phá Quân"), O("Đại Hao", "Tiểu Hao"), O("Địa Không", "Địa Kiếp")], "tai_pha_hao_khong_kiep_trang_tay", "verified", "p.106", "dễ trắng tay (Phá Quân, Hao, Không/Kiếp đồng cung)", "limit")
add(TB, "TT", [TT], "tai_tuan_triet_khong_san_tay", "draft", "p.106", "tiền của không có sẵn, phải tự gây dựng (Tuần/Triệt ở Tài Bạch)", "limit")
# ---------- Thiên Di (pp.108-109)
DI = "Thiên Di"
add(DI, "TAM_HOA", [has(TPH, h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")], "di_tam_hoa_ban_nhieu_quy_nhan", "verified", "p.108", "bạn nhiều, gặp quý nhân yêu dùng (Khoa Quyền Lộc hội Thiên Di)")
add(DI, "KHOI", [O("Thiên Khôi")], "di_khoi_gap_nguoi_sang", "verified", "p.108", "hay gặp người sang giúp (Thiên Khôi ở Thiên Di)")
add(DI, "VIET", [O("Thiên Việt")], "di_viet_nho_ban", "verified", "p.108", "hay nhờ bạn bè (Thiên Việt ở Thiên Di)")
add(DI, "LOC_MA", [T("Lộc Tồn"), T("Thiên Mã")], "di_loc_ma_ngoai_tai", "verified", "p.108", "nhiều khi có ngoại tài (Lộc, Mã hội Thiên Di)")
add(DI, "VU_THAM", [O("Vũ Khúc", "Tham Lang")], "di_vu_tham_tai_phat_ngoai", "verified", "p.108", "tài phát ở phương ngoài (Vũ Khúc hoặc Tham Lang ở Thiên Di)")
add(DI, "VAN_TA_HUU", [T("Văn Xương", "Văn Khúc"), T("Tả Phụ", "Hữu Bật")], "di_van_tinh_ta_huu_quy_nhan", "draft", "p.108", "gặp người quý nhân (Xương Khúc, Tả Hữu hội Thiên Di); 'gặp' đọc là hội")
add(DI, "LUC_SI_TUONG_QUAN", [O("Lực Sĩ"), O("Tướng Quân")], "di_luc_si_tuong_quan_san_quy_quyen", "verified", "p.108", "ra vào chốn quý quyền (Lực Sĩ, Tướng Quân ở Thiên Di)")
add(DI, "CO", [O("Thiên Cơ")], "di_co_can_quy_nhan", "draft", "p.108", "gần được quý nhân (Thiên Cơ ở Thiên Di)")
add(DI, "LUONG_DONG", [OA("Thiên Lương", "Thiên Đồng")], "di_luong_dong_gap_anh_tai", "verified", "p.108", "gặp người anh tài (Thiên Lương, Thiên Đồng cùng ở Thiên Di)")
add(DI, "PHA_SAT_HAM", [anyof(allof(O("Phá Quân"), dig("Phá Quân", HAM)), allof(O("Thất Sát"), dig("Thất Sát", HAM)))], "di_pha_sat_ham_thi_phi", "verified", "p.108", "suốt đời thị phi ở ngoài (Phá Quân hoặc Thất Sát hãm ở Thiên Di)", "limit")
add(DI, "VU_DA_KINH", [O("Vũ Khúc"), O("Đà La", "Kình Dương")], "di_vu_da_kinh_au_lo", "draft", "p.108", "hay âu lo khi ra ngoài (Vũ Khúc gặp Đà hoặc Kình)", "limit")
add(DI, "TUONG_QUAN_TRIET", [O("Tướng Quân"), {"fact": "palace.triet", "value": True}], "di_tuong_quan_triet_khong_lanh", "verified", "p.108", "ra ngoài khó thuận (Tướng Quân gặp Triệt)", "limit")
add(DI, "CO_MA_HAM", [OA("Thiên Cơ", "Thiên Mã"), dig("Thiên Cơ", HAM)], "di_co_ma_ham_long_dong", "verified", "p.108", "long đong đông tây (Cơ, Mã ở Thiên Di, Cơ hãm)", "limit")
add(DI, "KHONG_KIEP", [O("Địa Không", "Địa Kiếp")], "di_khong_kiep_khong_thuan_ben_ngoai", "verified", "p.109", "ngoài giao thiệp lắm trắc trở (Không, Kiếp ở Thiên Di)", "limit")
add(DI, "LUONG_NGUYET", [OA("Thiên Lương", "Thái Âm"), dig("Thái Âm", MV)], "di_luong_nguyet_mieu_phu_gia", "verified", "p.109", "thành phú gia ở bên ngoài (Lương, Nguyệt miếu ở Thiên Di)")
# ---------- Nô Bộc (p.109)
NO = "Nô Bộc"
add(NO, "VU_TUONG_TA_HUU", [O("Vũ Khúc", "Thiên Tướng"), O("Tả Phụ", "Hữu Bật")], "no_vu_tuong_ta_huu_nhat_ho_bach_nap", "verified", "p.109", "một tiếng hô trăm người ứng, người dưới quyền đông (Vũ/Tướng đồng cung Tả/Hữu)")
add(NO, "NN_HAM", [anyof(allof(has(OWNM, "Thái Dương"), dig("Thái Dương", HAM)), allof(has(OWNM, "Thái Âm"), dig("Thái Âm", HAM)))], "no_nhat_nguyet_ham_luc_o_luc_di", "verified", "p.109", "người dưới quyền, bạn bè lúc ở lúc đi (Nhật hoặc Nguyệt hãm ở Nô Bộc)", "limit")
add(NO, "QUYEN_CU", [O("Cự Môn"), has("palace.tu_hoa", "Hóa Quyền")], "no_quyen_cu_oan_chu_tranh_quyen", "verified", "p.109", "người dưới oán chủ, tranh quyền (Hóa Quyền đồng cung Cự Môn)", "limit")
add(NO, "PHA_VU", [OA("Phá Quân", "Vũ Khúc")], "no_pha_vu_phan_boi", "verified", "p.109", "người dưới, bạn bè dễ phản bội (Phá Quân đồng cung Vũ Khúc)", "limit")
add(NO, "DA_KY", [O("Kình Dương", "Đà La"), has("palace.tu_hoa", "Hóa Kỵ")], "no_kinh_da_ky_ban_be_kho_luong", "draft", "p.109", "bạn bè, người dưới khó lường (Kình/Đà gặp Hóa Kỵ); sách còn kể Phá hãm", "limit")
add(NO, "LUONG_CO_VAN_TINH", [anyof(allof(O("Thiên Lương"), dig("Thiên Lương", GOOD)), allof(O("Thiên Cơ"), dig("Thiên Cơ", GOOD))), O("Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc")], "no_luong_co_cat_tinh_ket_giao", "verified", "p.109", "kết giao thuận mọi đường (Lương hoặc Cơ ở thế sáng, gặp Tả Hữu hoặc Xương Khúc)")
# ---------- Quan Lộc (pp.109-111)
QL = "Quan Lộc"
add(QL, "SAT_MIEU", [O("Thất Sát"), dig("Thất Sát", MV)], "quan_sat_mieu_chuc_truong_quan_cong", "verified", "p.109", "uy hùng, nắm chức, có quân công (Thất Sát miếu ở Quan Lộc)")
add(QL, "THAM_VU", [OA("Tham Lang", "Vũ Khúc")], "quan_tham_vu_cong_danh_muon", "verified", "p.109", "công danh đến muộn (Tham Vũ đồng cung ở Quan Lộc)", "limit")
add(QL, "NHAT_NGUYET", [anyof(allof(has(OWNM, "Thái Dương"), dig("Thái Dương", GOOD)), allof(has(OWNM, "Thái Âm"), dig("Thái Âm", GOOD)))], "quan_nhat_nguyet_giau_sang_san", "verified", "p.109", "giàu sang như đã có sẵn (Nhật hoặc Nguyệt sáng ở Quan Lộc)")
add(QL, "HOA_LINH_SUU_MUI", [O("Hỏa Tinh", "Linh Tinh"), br("Sửu", "Mùi")], "quan_hoa_linh_suu_mui_chien_cong", "verified", "p.110", "hợp đường chiến công, binh nghiệp (Hỏa/Linh ở Sửu, Mùi ở Quan Lộc)")
add(QL, "DAO_HONG", [O("Đào Hoa", "Hồng Loan")], "quan_dao_hong_cong_danh_som", "verified", "p.110", "công danh sớm, thoả chí trai (Đào, Hồng ở Quan Lộc)")
add(QL, "KINH_TU_MO_MA", [O("Kình Dương"), br(*TUMO), T("Thiên Mã")], "quan_kinh_tu_mo_ma_vo_cong", "verified", "p.110", "ra biên cương lập võ công (Kình ở Tứ mộ, Mã hội)")
add(QL, "GIAP_XK", [has(FL, "Văn Xương"), has(FL, "Văn Khúc")], "quan_giap_xuong_khuc_hanh_thong", "verified", "p.110", "một đường hanh thông (Quan Lộc giáp Xương, Khúc)")
add(QL, "TUE_HO_PHU", [T("Thái Tuế"), T("Bạch Hổ"), T("Văn Xương", "Văn Khúc")], "quan_tue_ho_phu_hung_bien_van_chuong", "draft", "p.110", "tài hùng biện, văn chương hơn người (Thái Tuế, Hổ, Phù hợp Xương Khúc); 'Phù' chưa rõ là sao nào")
add(QL, "GIAP_LIEM_SAT", [has(FL, "Liêm Trinh"), has(FL, "Thất Sát")], "quan_giap_liem_sat_cong_danh_muon", "verified", "p.110", "tuổi già mới rạng công danh (Quan Lộc giáp Liêm, Sát)", "limit")
add(QL, "HOA_LINH_MA", [O("Hỏa Tinh", "Linh Tinh"), O("Thiên Mã")], "quan_hoa_linh_ma_co_khi_van_tai", "verified", "p.110", "hợp nghề cơ khí hoặc vận chuyển (Hỏa/Linh đồng cung Mã)")
add(QL, "THAM_LUONG_KHUC", [O("Tham Lang", "Thiên Lương"), T("Văn Khúc")], "quan_tham_luong_khuc_danh_chuc", "draft", "p.110", "có danh chức, quyền uy (Tham hoặc Lương hội Khúc)")
add(QL, "TAU_BAC_SI", [O("Tấu Thư"), O("Bác Sĩ")], "quan_tau_thu_bac_si_van_hoc_rong", "verified", "p.110", "đường văn học rộng, con nhà trâm anh (Tấu Thư, Bác Sĩ ở Quan Lộc)")
add(QL, "TUONG_KHONG_KIEP", [O("Thiên Tướng"), O("Địa Không", "Địa Kiếp")], "quan_tuong_khong_kiep_gian_truan", "verified", "p.110", "gian truân (Thiên Tướng đồng cung Không/Kiếp)", "limit")
add(QL, "TU_PHU_TAM_HOA", [T("Tử Vi", "Thiên Phủ")] + [has(TPH, h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")], "quan_tu_phu_tam_hoa_cat_tuong", "verified", "p.110", "công danh cát tường (Tử, Phủ ba phương, Tam Hóa triều)")
add(QL, "KHOI_VIET", [T("Thiên Khôi"), T("Thiên Việt")], "quan_khoi_viet_cat_tuong", "verified", "p.110", "công danh cát tường (Khôi, Việt hội Quan Lộc)")
add(QL, "TA_HUU", [T("Tả Phụ"), T("Hữu Bật")], "quan_ta_huu_van_vo_ven_toan", "verified", "p.110", "văn võ vẹn toàn nếu sáng, hãm vẫn giữ được phần công danh (Tả Hữu hội Quan Lộc)")
add(QL, "KINH_DA_MA", [O("Kình Dương", "Đà La"), T("Thiên Mã")], "quan_kinh_da_ma_chien_cong", "draft", "p.110", "xuôi ngược để dành chiến công (Kình/Đà gặp Mã); 'ngộ' đọc là hội")
add(QL, "NN_SUU_MUI", [OA("Thái Dương", "Thái Âm"), br("Sửu", "Mùi")], "quan_nhat_nguyet_suu_mui_bat_thong", "verified", "p.111", "đường công danh không thông (Nhật Nguyệt đồng cung Sửu/Mùi ở Quan Lộc)", "limit")
add(QL, "NHAT_XUONG", [O("Thái Dương"), O("Văn Xương")], "quan_nhat_xuong_thuan_duong_trieu_dinh", "verified", "p.111", "thuận đường chốn triều chính (Thái Dương, Văn Xương ở Quan Lộc)")
# ---------- Điền Trạch (p.111)
DT = "Điền Trạch"
add(DT, "TAU_XK", [O("Tấu Thư"), O("Văn Xương", "Văn Khúc")], "dien_tau_xuong_khuc_sinh_tien_tai", "verified", "p.111", "sinh tiền tài, nhà đất (Tấu Thư đồng cung Xương/Khúc)")
add(DT, "MO_SINH_VUONG", [O("Mộ"), T("Trường Sinh", "Đế Vượng")], "dien_mo_sinh_vuong_lau_dai", "draft", "p.111", "nhà cửa lớn, nguy nga (Mộ gặp Trường Sinh/Đế Vượng); 'phùng' đọc là hội")
add(DT, "CU_CO_MAO", [OA("Cự Môn", "Thiên Cơ"), br("Mão")], "dien_cu_co_mao_giau_hao_hoa", "verified", "p.111", "giàu có, nhà cửa hào hoa (Cự, Cơ ở Mão)")
add(DT, "PHU_VU", [OA("Thiên Phủ", "Vũ Khúc")], "dien_phu_vu_nhieu_toa_nha", "verified", "p.111", "nhiều nhà cửa (Thiên Phủ, Vũ Khúc ở Điền Trạch)")
add(DT, "HONG_LOAN", [O("Hồng Loan")], "dien_hong_loan_ruong_dat_giau_sang", "verified", "p.111", "ruộng đất giàu sang (Hồng Loan ở Điền Trạch)")
add(DT, "TU_DONG_NN", [O("Tử Vi", "Thiên Đồng", "Thái Dương", "Thái Âm")], "dien_tu_dong_nhat_nguyet_hanh_thong", "draft", "p.111", "một đường hanh thông về nhà đất (Tử, Đồng, Nhật hoặc Nguyệt ở Điền Trạch)")
add(DT, "DONG_THAM_MV", [anyof(allof(O("Thiên Đồng"), dig("Thiên Đồng", MV)), allof(O("Tham Lang"), dig("Tham Lang", MV)))], "dien_dong_tham_bach_thu_lap_cua_nha", "verified", "p.111", "tay trắng lập nên cửa nhà (Đồng hoặc Tham miếu vượng ở Điền Trạch)")
add(DT, "LOC_MO", [has("palace.tu_hoa", "Hóa Lộc"), anyof(has(OWN, "Mộ"), has(FL, "Mộ"))], "dien_hoa_loc_mo_phu_gia", "draft", "p.111", "nhà giàu (Hóa Lộc giáp sao Mộ); 'giáp' đọc là kề bên hoặc đồng cung")
add(DT, "LUONG_CO", [anyof(allof(O("Thiên Lương"), dig("Thiên Lương", GOOD)), allof(O("Thiên Cơ"), dig("Thiên Cơ", GOOD)))], "dien_luong_co_dac_dia_nha_xenh_xoang", "verified", "p.111", "cửa nhà khang trang (Lương hoặc Cơ đắc địa ở Điền Trạch)")
add(DT, "PHA", [O("Phá Quân")], "dien_pha_tan_tai_to_nghiep", "verified", "p.111", "dễ tán tổ nghiệp, về sau tự tạo dựng lại (Phá Quân ở Điền Trạch)", "limit")
add(DT, "TANG_HO", [T("Tang Môn"), T("Bạch Hổ")], "dien_tang_ho_cua_nha_vua_du", "draft", "p.111", "cửa nhà vừa đủ (Tang Môn, Bạch Hổ chiếu nhau)", "limit")
# ---------- Phúc Đức (pp.112-113)
PD = "Phúc Đức"
add(PD, "VU_THAM_KHOA", [O("Vũ Khúc", "Tham Lang", "Thiên Phủ"), has(TPH, "Hóa Khoa")], "phuc_vu_tham_phu_khoa_vo_nghiep_anh_hung", "draft", "p.112", "họ hàng phát về võ, nhiều anh hùng (Vũ/Tham/Phủ hội Hóa Khoa)")
add(PD, "KHONG_KIEP", [O("Địa Không", "Địa Kiếp")], "phuc_khong_kiep_ho_hang_bien_dong", "draft", "p.112", "họ hàng nhiều người sống xa, biến động (Không/Kiếp ở Phúc Đức)", "limit")
add(PD, "TAU_XK", [O("Tấu Thư"), O("Văn Xương", "Văn Khúc")], "phuc_tau_xuong_khuc_than_dong", "verified", "p.112", "trong họ có người thông minh (Tấu Thư đồng cung Xương/Khúc)")
add(PD, "KHOI_VIET_DAO", [T("Thiên Khôi", "Thiên Việt"), T("Đào Hoa")], "phuc_khoi_viet_dao_phuc_nha_kha", "draft", "p.112", "phúc nhà khá (Khôi/Việt gặp Đào Hoa)")
add(PD, "TU_NHAT_MV", [anyof(allof(O("Tử Vi"), dig("Tử Vi", MV)), allof(O("Thái Dương"), dig("Thái Dương", MV)))], "phuc_tu_nhat_mieu_ho_co_nguoi_quy_quyen", "draft", "p.112", "trong họ có người quyền quý (Tử Vi hoặc Thái Dương miếu vượng ở Phúc Đức)")
add(PD, "TS_DV", [O("Trường Sinh", "Đế Vượng")], "phuc_truong_sinh_de_vuong_nhan_dinh", "verified", "p.112", "họ hàng đông đúc, thịnh vượng (Trường Sinh hoặc Đế Vượng ở Phúc Đức)")
add(PD, "TUE_PHU", [O("Thái Tuế"), O("Quan Phù")], "phuc_tue_phu_tung_su_tranh", "draft", "p.112", "họ hàng hay tranh chấp (Thái Tuế, Quan Phù ở Phúc Đức); 'Phù' đọc là Quan Phù", "limit")
add(PD, "THIEN_HY", [O("Thiên Hỷ")], "phuc_thien_hy_dat_quy", "draft", "p.112", "đất quý, sinh tương (Thiên Hỷ ở Phúc Đức)")
add(PD, "VAN_HOC", [T("Văn Xương", "Văn Khúc"), T("Thiên Khôi", "Thiên Việt"), has(TPH, "Hóa Khoa")], "phuc_van_hoc_co_du_anh_tai", "draft", "p.112", "họ có người văn học, anh tài (Khôi, Khoa, Xương/Khúc hội Phúc Đức)")
add(PD, "TT", [TT], "phuc_tuan_triet_it_hy_vong", "verified", "p.113", "phúc bị kìm hãm, ít hy vọng (Tuần/Triệt án ngữ Phúc Đức)", "limit")
# ---------- Phụ Mẫu (p.113)
PM = "Phụ Mẫu"
add(PM, "VIET_KHOA", [O("Thiên Khôi", "Thiên Việt"), has("palace.tu_hoa", "Hóa Khoa")], "pm_viet_khoa_hien_vang", "verified", "p.113", "cha mẹ hiển vang (Khôi/Việt đồng cung Hóa Khoa)")
add(PM, "CAT_TINH", [{"fact": "palace.khi.cat_self", "operator": "gte", "value": 2}], "pm_cat_tinh_hanh_thong", "draft", "p.113", "mọi đường hanh thông (Xương Khúc, Tả Hữu... ở Phụ Mẫu); 'từ hai cát tinh' là quy ước")
add(PM, "CO_LUONG", [OA("Thiên Cơ", "Thiên Lương")], "pm_co_luong_dang_yeu", "verified", "p.113", "cha mẹ nhân hậu, hợp ý (Cơ, Lương đồng cung ở Phụ Mẫu)")
add(PM, "LOC_KHONG_KIEP", [O("Lộc Tồn"), O("Địa Không", "Địa Kiếp")], "pm_loc_ton_khong_kiep_pha_gia", "draft", "p.113", "gia sản cha mẹ dễ hao tán (Lộc Tồn gặp Không/Kiếp)", "limit")
add(PM, "BAT_TUONG", [O("Hữu Bật"), O("Thiên Tướng")], "pm_bat_tuong_danh_mon", "draft", "p.113", "cha mẹ danh môn (Hữu Bật, Thiên Tướng ở Phụ Mẫu); câu thơ ghép nhiều sao")
add(PM, "KINH_DA", [O("Kình Dương", "Đà La")], "pm_kinh_da_cha_me_bat_dong", "verified", "p.113", "cha mẹ và con bất đồng (Kình hoặc Đà ở Phụ Mẫu)", "limit")
add(PM, "LY_TONG", [anyof(*[has(OWNM, s) for s in ("Cự Môn", "Liêm Trinh", "Vũ Khúc", "Thất Sát", "Phá Quân", "Tham Lang")])], "pm_sat_pha_tham_ly_tong", "draft", "p.113", "dễ xa cha mẹ, rời tổ nghiệp (Cự, Liêm, Vũ, Sát, Phá, Tham ở Phụ Mẫu)", "limit")
add(PM, "LUONG_MV", [has(OWNM, "Thiên Lương"), dig("Thiên Lương", MV)], "pm_luong_vuong_cha_me_ung_dung", "verified", "p.113", "cha mẹ sống ung dung (Thiên Lương vượng ở Phụ Mẫu)")
add(PM, "CO_HOI_TY_SUU", [has(OWNM, "Thiên Cơ"), br("Hợi", "Tý", "Sửu")], "pm_co_hoi_ty_suu_xung_khac", "verified", "p.113", "cha mẹ và con dễ xung khắc (Thiên Cơ ở Phụ Mẫu tại Hợi, Tý, Sửu)", "limit")

slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for pal, rid, conds, claim, effect, status, loc, vi in R:
    rules.append({"id": f"TV_TH_P2_{slug(pal)}_{slug(rid)}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "th_palace_verse2",
        "description": f"Tử Vi Thực Hành, phú các cung (paraphrased), cung {pal}: {vi} [TH {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": claim, "effect": effect, "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_THUC_HANH"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims.setdefault(claim, ("khuynh hướng " if effect == "support" else "hạn chế: ") + vi)
    if effect == "limit":
        claims.setdefault("limit:" + claim, "hạn chế: " + vi)
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_thuc_hanh_palaces2.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
