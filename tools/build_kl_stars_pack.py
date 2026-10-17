"""Generates data/pack_khao_luan_stars.json: Tử Vi Khảo Luận pp.63-67 (phú on Lộc, Tả Hữu, Kình Đà, Hỏa Linh, Không Kiếp, Tứ Hóa, Lục Bại) and
pp.74-83 ('Ý nghĩa các sao': Tử Vi, Thiên Cơ, Thái Dương by position and by palace). Paraphrased with page cites. Left out on purpose: death,
injury, disability, theft/robbery, sexual-reputation lines, and couplets needing unverified auxiliary stars (Long Phượng, Hình, Riêu, Khốc Hư, Giải...).
Khảo Luận's own brightness statements (pp.79-83) are used as branch lists; its note that miếu/vượng/đắc are not clearly distinguished is kept."""
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
O = lambda *ss: anyof(*[has(OWN, s) for s in ss])
OA = lambda *ss: allof(*[has(OWN, s) for s in ss])
T = lambda *ss: anyof(*[has(TPS, s) for s in ss])
TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})
SATS = ("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh")
SAT_TP = anyof(*[has(TPS, s) for s in SATS])
CATN = lambda n: {"fact": "palace.khi.cat_tp", "operator": "gte", "value": n}
LOC = anyof(has(OWN, "Lộc Tồn"), has("palace.tu_hoa", "Hóa Lộc"))
TUMO = ("Thìn", "Tuất", "Sửu", "Mùi")
R = []
def add(pal, rid, conds, claim, status, page, phrase, effect="support"):
    R.append((pal, rid, conds, claim, effect, status, page, phrase))
M = "Mệnh"
# ---- pp.63-67 phú
add(M, "SONG_LOC", [has(TPS, "Lộc Tồn"), has(TPH, "Hóa Lộc")], "kl_song_loc_phu_qui_chung_than", "verified", "p.63", "giàu sang suốt đời (Lộc Tồn và Hóa Lộc chiếu nhau hoặc cùng chiếu Mệnh)")
add(M, "LOC_XUNG_PHA", [O("Lộc Tồn"), has("palace.rel.opp_majors", "Phá Quân")], "kl_loc_ton_pha_xung_ngheo", "verified", "p.63", "tốt hóa xấu, đời nhiều thiếu thốn (Lộc Tồn bị Phá Quân xung chiếu)", "limit")
add(M, "MINH_AM_LOC", [anyof(allof(O("Lộc Tồn"), has("palace.rel.nhi_hop_hoa", "Hóa Lộc")), allof(has("palace.tu_hoa", "Hóa Lộc"), has("palace.rel.nhi_hop_stars", "Lộc Tồn")))], "kl_minh_loc_am_loc_cong_danh_lon", "verified", "p.63", "có công danh lớn (Lộc Tồn được Hóa Lộc nhị hợp hoặc ngược lại)")
add(M, "LOC_MA_GIAO_TRI", [anyof(allof(O("Lộc Tồn"), has("palace.rel.opp_stars", "Thiên Mã")), allof(O("Thiên Mã"), has("palace.rel.opp_stars", "Lộc Tồn")))], "kl_loc_ma_giao_tri_chung_nhan_sung_ai", "verified", "p.63", "giàu sang, được mọi người yêu mến (Lộc Tồn và Thiên Mã xung chiếu nhau)")
add(M, "LOC_MA_KHONG_KIEP", [anyof(allof(O("Lộc Tồn"), has("palace.rel.opp_stars", "Thiên Mã")), allof(O("Thiên Mã"), has("palace.rel.opp_stars", "Lộc Tồn"))), T("Địa Không", "Địa Kiếp")], "kl_loc_ma_dao_ky_khong_kiep", "verified", "p.63", "sự nghiệp dễ đổ vỡ (Lộc Mã xung chiếu mà bị Không, Kiếp hội)", "limit")
add(M, "TA_HUU_XUONG", [T("Tả Phụ", "Hữu Bật"), T("Văn Xương")], "kl_ta_huu_xuong_chuc_lon", "verified", "p.63", "làm nên chức lớn (Tả Hữu gặp Văn Xương)")
add(M, "HUU_TUONG", [OA("Hữu Bật", "Thiên Tướng")], "kl_huu_tuong_phuc_phu_qui", "verified", "p.63", "hưởng phúc đức phú quý (Hữu Bật đồng cung Thiên Tướng)")
add(M, "TA_HUU_GIAP_TU", [has(OWNM, "Tử Vi"), has(FL, "Tả Phụ"), has(FL, "Hữu Bật")], "kl_phu_bat_giap_de", "verified", "p.63", "được hưởng phúc, có uy quyền hiển hách (Tử Vi được Tả, Hữu giáp hai bên)")
add(M, "TA_HUU_VCD", [{"fact": "palace.has_no_major", "value": True}, OA("Tả Phụ", "Hữu Bật")], "kl_ta_huu_don_thu_ly_tong_lap_nghiep", "verified", "p.63", "phải lập nghiệp phương xa (Mệnh vô chính diệu chỉ có Tả Hữu đồng cung)")
add(M, "TA_HUU_TU_MO", [br(*TUMO), T("Tả Phụ", "Hữu Bật")], "kl_ta_huu_tu_mo_som_cong_danh", "verified", "p.63", "sớm có công danh (Mệnh ở Tứ mộ có Tả Hữu)")
add(M, "SAT4_THU_MENH", [anyof(*[has(OWN, s) for s in ("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh")])], "kl_tu_sat_thu_menh_vat_va", "draft", "p.64", "đời nhiều vất vả ('còng lưng kiếm ăn') khi Kình, Đà, Hỏa hoặc Linh thủ Mệnh; sách không nêu điều kiện sáng tối", "limit")
add(M, "KINH_PHUC_LOC", [O("Kình Dương"), anyof(has(TPH, "Hóa Khoa"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc")), br("Ngọ"), nt(T("Thất Sát"))], "kl_ma_dau_dai_kiem_tran_ngu_bien_cuong", "draft", "p.64", "có sự nghiệp lớn, hiển đạt võ nghiệp (Kình ở Ngọ, tránh Sát và Hình, gặp Khoa Quyền Lộc); sao Hình chưa được kiểm nên chỉ loại trừ Thất Sát")
add(M, "KINH_DONG_AM_NGO", [OA("Kình Dương", "Thiên Đồng", "Thái Âm"), br("Ngọ")], "kl_kinh_dong_am_ngo_uy_danh", "draft", "p.64", "nổi danh, giàu sang (Kình đồng cung Đồng, Âm ở Ngọ); sách còn kể Phượng Các, Giải Thần")
add(M, "KINH_LUC_SI", [O("Kình Dương"), O("Lực Sĩ")], "kl_kinh_luc_si_huu_cong_vo_lao", "verified", "p.64", "hay lập công nhưng ít được khen thưởng (Kình đi kèm Lực Sĩ, Tấu Thư và Tiểu Hao hợp chiếu)")
add(M, "HOA_LINH_TUONG_NGO", [anyof(allof(O("Hỏa Tinh"), has("palace.rel.opp_stars", "Linh Tinh")), allof(O("Linh Tinh"), has("palace.rel.opp_stars", "Hỏa Tinh")))], "kl_hoa_linh_tuong_ngo_tai_lon", "verified", "p.65", "tài năng lớn, quyền hành rộng (Hỏa hoặc Linh thủ Mệnh được Linh hoặc Hỏa chiếu)")
add(M, "HOA_LINH_KINH", [O("Hỏa Tinh", "Linh Tinh"), O("Kình Dương")], "kl_hoa_linh_kinh_ha_cach", "verified", "p.65", "công danh trắc trở, cách xoàng (Hỏa hoặc Linh đồng cung Kình Dương)", "limit")
add(M, "HOA_LINH_GIAP", [has(FL, "Hỏa Tinh"), has(FL, "Linh Tinh")], "kl_hoa_linh_giap_menh_bai_cuc", "verified", "p.65", "cuộc sống long đong, vất vả (Hỏa, Linh giáp hai bên Mệnh)", "limit")
for pal in ("Tài Bạch", "Phúc Đức"):
    add(pal, "KHONG_KIEP", [O("Địa Không", "Địa Kiếp")], "kl_khong_kiep_tai_phuc_ngheo", "verified", "p.65", "số nghèo khổ (Không, Kiếp thủ cung Tài hoặc cung Phúc)", "limit")
add(M, "KK_GIAP_TY_HOI", [br("Tỵ", "Hợi"), has(FL, "Địa Không"), has(FL, "Địa Kiếp")], "kl_khong_kiep_giap_menh_ty_hoi_bai_cuc", "verified", "p.65", "đời lang thang vất vả, thiếu thốn (Mệnh ở Tỵ/Hợi có Không, Kiếp giáp hai bên)", "limit")
add(M, "KK_DAN_THAN", [br("Dần", "Thân"), O("Địa Không", "Địa Kiếp"), T("Tử Vi", "Thiên Phủ", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật")], "kl_khong_kiep_dan_than_thang_tram", "verified", "p.65", "đời lên xuống bất thường dù gặp quý tinh (Không/Kiếp thủ Mệnh ở Dần/Thân)", "limit")
add(M, "KIEP_THAM", [OA("Địa Kiếp", "Tham Lang")], "kl_kiep_tham_long_dong", "verified", "p.65", "long đong, lênh đênh, vất vả (Địa Kiếp đồng cung Tham Lang)", "limit")
add(M, "QUYEN_LOC", [anyof(allof(has("palace.tu_hoa", "Hóa Quyền"), has(TPH, "Hóa Lộc")), allof(has("palace.tu_hoa", "Hóa Lộc"), has(TPH, "Hóa Quyền")))], "kl_quyen_loc_tai_quan_song_my", "verified", "p.66", "vừa giàu vừa sang (Hóa Quyền được Hóa Lộc chiếu hoặc ngược lại)")
add(M, "LOC_DAN_MAO", [has("palace.tu_hoa", "Hóa Lộc"), br("Dần", "Mão")], "kl_hoa_loc_dan_mao_giu_cua", "verified", "p.66", "ham tiền, giữ của chặt (Hóa Lộc ở Mệnh tại Dần/Mão)")
add(M, "KHOA_LOC_GIAP", [has(FL, "Hóa Khoa"), has(FL, "Hóa Lộc")], "kl_khoa_loc_giap_menh_qui_cach", "draft", "p.66", "cách giàu sang (Khoa, Lộc kẹp hai bên Mệnh); sách ví dụ Mệnh Tý, Khoa ở Hợi, Lộc ở Sửu; facts hiện chỉ có sao ở giáp, chưa có Tứ Hóa ở giáp")
for pal in ("Tài Bạch", "Phúc Đức"):
    add(pal, "QUYEN_LOC", [has("palace.tu_hoa", "Hóa Quyền"), has("palace.tu_hoa", "Hóa Lộc")], "kl_quyen_loc_thu_tai_phuc", "verified", "p.66", "giàu sang nổi tiếng (Hóa Quyền, Hóa Lộc thủ cung Tài hoặc cung Phúc)")
add(M, "LOC_TON_CO_LUONG", [O("Lộc Tồn"), O("Thiên Cơ"), O("Thiên Lương")], "kl_loc_ton_co_luong_phu_gia_dich_quoc", "verified", "p.66", "rất giàu, không ai bì kịp (Lộc Tồn thêm Cơ, Lương)")
add(M, "VCD_TAM_KHONG_SONG_LOC", [{"fact": "palace.has_no_major", "value": True}, anyof(TT, O("Thiên Không", "Địa Không")), has(TPS, "Lộc Tồn"), has(TPH, "Hóa Lộc")], "kl_vcd_tam_khong_song_loc_phu_qui", "verified", "p.66", "giàu sang lạ lùng (Mệnh vô chính diệu được Tuần/Thiên Không/Địa Không, lại gặp song Lộc)")
add(M, "TAM_KY_KY_KINH", [has(TPH, "Hóa Khoa"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc"), anyof(has("palace.tu_hoa", "Hóa Kỵ"), O("Kình Dương"))], "kl_tam_ky_gap_ky_kinh_mo_mit", "verified", "p.66", "đường công danh mờ mịt (Khoa Quyền Lộc hội mà Hóa Kỵ hoặc Kình đồng cung)", "limit")
add(M, "KY_VAN_NHAN", [has("palace.tu_hoa", "Hóa Kỵ"), T("Tử Vi", "Thiên Phủ", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật")], "kl_hoa_ky_van_nhan_cong_danh_tro", "draft", "p.66", "giỏi văn chương nhưng công danh vẫn trắc trở (Hóa Kỵ gặp phúc tinh, quý tinh); 'phúc tinh' chưa kiểm", "limit")
add(M, "KY_KHOA", [has("palace.tu_hoa", "Hóa Kỵ"), br("Hợi", "Tý"), has(TPH, "Hóa Khoa")], "kl_ky_khoa_hoi_ty_ngon_hanh", "verified", "p.67", "cẩn trọng lời ăn tiếng nói nên được kính nể (Hóa Kỵ ở Hợi/Tý gặp Hóa Khoa)")
add(M, "HAO_THAM", [O("Đại Hao", "Tiểu Hao"), O("Tham Lang")], "kl_hao_tham_ham_muon_kin", "draft", "p.67", "ham mê kín đáo (Hao đồng cung Tham Lang); sách dùng lời nặng, chỉ giữ ý 'kín đáo'", "limit")
add(M, "HAO_MAO_DAU_KY", [O("Đại Hao", "Tiểu Hao"), br("Mão", "Dậu"), has("palace.tu_hoa", "Hóa Lộc")], "kl_song_hao_mao_dau_gap_loc_troi_cua", "verified", "p.67", "của cải trôi đi (Song Hao ở Mão/Dậu gặp Hóa Lộc)", "limit")
add(M, "HAO_MAO_DAU_CU_CO", [O("Đại Hao", "Tiểu Hao"), br("Mão", "Dậu"), has(TPS, "Cự Môn"), has(TPS, "Thiên Cơ")], "kl_song_hao_mao_dau_cu_co_phu_qui", "verified", "p.67", "được hưởng phú quý (Song Hao ở Mão/Dậu gặp Cự, Cơ)")
# ---- pp.74-78 Tử Vi
add(M, "TV_SAT_DE_HUE", [has(OWNM, "Tử Vi"), has(OWNM, "Thất Sát")], "kl_tu_sat_de_hue_bao_kiem", "verified", "p.75", "tăng nhiều uy lực ('đế huề bảo kiếm': Tử Vi đồng cung Thất Sát)")
add(M, "TV_PHU", [has(OWNM, "Tử Vi"), has(OWNM, "Thiên Phủ")], "kl_tu_phu_tai_loc_doi_dao", "verified", "p.75", "tài lộc dồi dào (Tử Vi đồng cung Thiên Phủ)")
add(M, "TV_TUONG", [has(OWNM, "Tử Vi"), has(OWNM, "Thiên Tướng")], "kl_tu_tuong_vua_co_toi_hien", "verified", "p.75", "như vua có tôi hiền (Tử Vi đồng cung Thiên Tướng)")
add(M, "TV_LUONG_DONG", [has(OWNM, "Tử Vi"), CATN(3)], "kl_tu_vi_nhieu_cat_tinh_phu_qui_cuc_do", "draft", "p.75", "phú quý đến cực độ (Tử Vi có nhiều bầy tôi: Tả Hữu, Xương Khúc, Khôi Việt...); ngưỡng 'nhiều' = từ ba cát tinh")
add(M, "TV_CO_QUAN", [has(OWNM, "Tử Vi"), nt(T("Tả Phụ")), nt(T("Hữu Bật"))], "kl_tu_vi_co_quan_giam_tot", "verified", "p.75", "như vua mất triều thần ('cô quân'), giảm tốt nhiều (Tử Vi không có Tả, Hữu)", "limit")
add(M, "TV_TUAN_TRIET", [has(OWNM, "Tử Vi"), TT], "kl_tu_vi_tuan_triet_gian_kho_thieu_thoi", "verified", "p.75", "gian khổ lúc thiếu thời, nên xa nhà lập nghiệp (Tử Vi gặp Tuần/Triệt án ngữ)", "limit")
add(M, "TV_THAM_SAT", [OA("Tử Vi", "Tham Lang"), anyof(*[has(OWN, s) for s in SATS])], "kl_tu_tham_sat_tu_hanh_yen_than", "verified", "p.75", "chỉ có tu hành mới yên thân (Tử Vi, Tham Lang đồng cung có sát tinh)", "limit")
add(M, "TV_DE_NGO_HUNG_DO", [has(OWNM, "Tử Vi"), TT, SAT_TP], "kl_de_ngo_hung_do_mat_quyen", "verified", "p.75", "như vua bị cướp vây, mất quyền lực ('đế ngộ hung đồ': Tử Vi có Tuần/Triệt lại gặp sát tinh)", "limit")
add(M, "TV_TY_NGO", [has(OWNM, "Tử Vi"), br("Tý", "Ngọ"), nt(has(OWNM, "Thiên Phủ"))], "kl_tu_vi_don_thu_doc_lap_doc_doan", "verified", "p.77", "độc lập, độc đoán, nổi danh, nhân hậu (Tử Vi đơn thủ ở Tý/Ngọ)")
add(M, "TV_NGO", [has(OWNM, "Tử Vi"), br("Ngọ")], "kl_tu_vi_ngo_dung_dau_nganh_phu_quy", "verified", "p.77", "đứng đầu một ngành, phú quý, gặp may (Tử Vi ở Ngọ: 'đế cư đế vị')")
add(M, "TV_TY", [has(OWNM, "Tử Vi"), br("Tý")], "kl_tu_vi_ty_hien_lanh_tieu_cuc", "verified", "p.77", "hiền lành hưởng phúc nhưng hơi tiêu cực, ít giúp được ai (Tử Vi ở Tý)")
add(M, "TV_TUONG_THIN_TUAT", [OA("Tử Vi", "Thiên Tướng")], "kl_tu_tuong_gioi_giang_vat_va", "verified", "p.77", "giỏi giang, tích cực nhưng vất vả ngược xuôi (Tử Tướng ở Thìn/Tuất)")
add(M, "TV_PHU_DAN_THAN", [OA("Tử Vi", "Thiên Phủ"), br("Dần", "Thân")], "kl_tu_phu_dan_than_on_dinh_an_phan", "verified", "p.77", "ổn định, thịnh vượng nhưng an phận, thiếu thực tài (Tử Phủ ở Dần/Thân)")
add(M, "TV_SAT_TY_HOI", [OA("Tử Vi", "Thất Sát"), br("Tỵ", "Hợi")], "kl_tu_sat_ty_hoi_thoat_ly_de_kiem_de_mat", "verified", "p.77", "thích rời nhà lập nghiệp sớm, dễ kiếm tiền nhưng cũng dễ mất (Tử Sát ở Tỵ/Hợi)")
add(M, "TV_THAM_MAO_DAU", [OA("Tử Vi", "Tham Lang"), br("Mão", "Dậu")], "kl_tu_tham_giau_co_gian_doi", "verified", "p.77", "có sự nghiệp lớn nhờ mánh khóe, giàu nhưng hay gian dối, ham hưởng thụ (Tử Tham ở Mão/Dậu)")
add(M, "TV_PHA_SUU_MUI", [OA("Tử Vi", "Phá Quân"), br("Sửu", "Mùi")], "kl_tu_pha_lieu_linh_vo_on", "verified", "p.77", "liều lĩnh dám làm, xoay sở giỏi nhưng dễ vô ơn vì tự cao (Tử Phá ở Sửu/Mùi)")
add(M, "GIAP_TU_PHU", [has(FL, "Tử Vi"), has(FL, "Thiên Phủ")], "kl_tu_phu_giap_menh_qui_cach", "verified", "p.78", "cách sang trọng, thiên về quan văn hưởng nhàn (Tử Vi, Thiên Phủ giáp hai bên Mệnh)")
add(M, "TU_PHU_TRIEU_VIEN", [OA("Vũ Khúc", "Thiên Tướng"), br("Dần", "Thân"), has("palace.rel.tp_majors", "Tử Vi"), has("palace.rel.tp_majors", "Thiên Phủ")], "kl_tu_phu_trieu_vien_thuc_loc_van_chung", "verified", "p.78", "hưởng lộc nhiều vô kể, phú quý từ thiếu thời (Tử Phủ triều viên)")
for pal, rid, conds, claim, ph in (
    ("Phụ Mẫu", "SANG", [has(OWNM, "Tử Vi"), anyof(br("Tý", "Ngọ"), has(OWNM, "Thiên Phủ"), has(OWNM, "Thiên Tướng"))], "kl_tu_vi_phu_cha_me_sang", "cha mẹ sang trọng (Tử Vi ở Phụ Mẫu tại Tý/Ngọ hoặc đồng cung Phủ, Tướng)"),
    ("Phúc Đức", "LAU_DAI", [has(OWNM, "Tử Vi"), anyof(br("Tý", "Ngọ"), has(OWNM, "Thiên Phủ"), has(OWNM, "Thiên Tướng"))], "kl_tu_vi_phuc_loc_lau_dai", "phúc lộc lâu dài (Tử Vi ở Phúc Đức tại Tý/Ngọ hoặc đồng cung Phủ, Tướng)"),
    ("Điền Trạch", "TOT", [has(OWNM, "Tử Vi"), anyof(has(OWNM, "Thiên Phủ"), has(OWNM, "Thiên Tướng"))], "kl_tu_vi_dien_phu_tuong_tot", "nhà đất tốt (Tử Vi đồng cung Phủ hoặc Tướng ở Điền Trạch)"),
    ("Quan Lộc", "SAT", [has(OWNM, "Tử Vi"), has(OWNM, "Thất Sát")], "kl_tu_sat_quan_khieu_vo_nghiep", "có khiếu võ nghiệp (Tử Vi đồng cung Thất Sát ở Quan Lộc)"),
    ("Tài Bạch", "PHU_VU", [has(OWNM, "Tử Vi"), anyof(has(OWNM, "Thiên Phủ"), has(OWNM, "Vũ Khúc"))], "kl_tu_vi_tai_phu_vu_thinh_vuong", "tiền bạc thịnh vượng (Tử Vi đi với Phủ, Vũ ở Tài Bạch)"),
    ("Tử Tức", "PHU_TUONG", [has(OWNM, "Tử Vi"), anyof(has(OWNM, "Thiên Phủ"), has(OWNM, "Thiên Tướng"))], "kl_tu_vi_tu_phu_tuong_dong_con", "đông con (Tử Vi đồng cung Phủ, Tướng ở Tử Tức)"),
):
    add(pal, "TV_" + rid, conds, claim, "verified", "p.76", ph)
for pal, rid, st, claim, ph in (
    ("Phụ Mẫu", "THAT_SAT", ["Thất Sát"], "kl_tu_sat_phu_me_bat_hoa", "cha mẹ hay bất hòa (Tử Vi đồng cung Thất Sát ở Phụ Mẫu)"),
    ("Phúc Đức", "THAT_SAT", ["Thất Sát"], "kl_tu_sat_phuc_tha_phuong", "dễ phải tha phương cầu thực (Tử Vi đi với Thất Sát ở Phúc Đức)"),
):
    add(pal, "TV_" + rid, [has(OWNM, "Tử Vi"), has(OWNM, st[0])], claim, "verified", "p.75-76", ph, "limit")
add("Điền Trạch", "TV_SPT", [has(OWNM, "Tử Vi"), anyof(*[has(OWNM, s) for s in ("Thất Sát", "Phá Quân", "Tham Lang")])], "kl_tu_vi_dien_sat_pha_tham_khong_nha", "verified", "p.76", "khó có nhà cửa, dễ phá sản (Tử Vi đi với Sát, Phá, Tham ở Điền Trạch)", "limit")
add("Quan Lộc", "TV_PHA_THAM", [has(OWNM, "Tử Vi"), anyof(has(OWNM, "Phá Quân"), has(OWNM, "Tham Lang"))], "kl_tu_vi_quan_pha_tham_thang_tram", "verified", "p.76", "đường quan lộc thăng trầm (Tử Vi đi với Phá hoặc Tham ở Quan Lộc)", "limit")
add("Thiên Di", "TV_PHA_THAM", [has(OWNM, "Tử Vi"), anyof(has(OWNM, "Phá Quân"), has(OWNM, "Tham Lang"))], "kl_tu_vi_di_pha_tham_dem_pha", "verified", "p.76", "ra ngoài hay bị dèm pha, quấy nhiễu (Tử Vi đi với Phá hoặc Tham ở Thiên Di)", "limit")
add("Phu Thê", "TV_SPT", [has(OWNM, "Tử Vi"), anyof(*[has(OWNM, s) for s in ("Thất Sát", "Phá Quân", "Tham Lang")])], "kl_tu_vi_phu_sat_pha_tham_tro", "verified", "p.76", "hôn nhân trắc trở (Tử Vi đi với Sát, Phá, Tham ở Phu Thê: Sát thì muộn, Phá thì hao tán, Tham thì hay ghen)", "limit")
# ---- pp.79-82 Thiên Cơ
CO = has(OWNM, "Thiên Cơ")
add(M, "CO_CAT_TINH", [CO, CATN(1)], "kl_co_phuc_tinh_giau_noi_tieng", "verified", "p.79", "giàu có và nổi tiếng (Thiên Cơ có phúc tinh đi kèm)")
add(M, "CO_TUAN_TRIET", [CO, TT], "kl_co_tuan_triet_long_dong", "draft", "p.79", "dễ phải lang thang, vất vả (Thiên Cơ gặp Tuần/Triệt); sách ghi thêm ý kiến ngược lại rằng Tuần Triệt giúp Cơ 'không trơn tuột'", "limit")
add(M, "CO_LUONG_THIN_TT", [OA("Thiên Cơ", "Thiên Lương"), br("Thìn", "Tuất"), anyof(TT, SAT_TP)], "kl_co_luong_thin_tuat_tuan_triet_gian_truan", "verified", "p.79", "gian truân, có xu hướng nương cửa tu (Cơ Lương ở Thìn/Tuất gặp Tuần Triệt, sát tinh)", "limit")
add(M, "CU_CO_MAO_DAU", [OA("Cự Môn", "Thiên Cơ"), br("Mão", "Dậu")], "kl_cu_co_mao_dau_tai_duc_giau", "verified", "p.79", "có tài đức và rất giàu (Cự Cơ ở Mão/Dậu)")
add(M, "CO_VAN_VO", [CO, T("Thiên Lương", "Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc")], "kl_co_dac_dia_quan_van_thanh_hien", "draft", "p.80", "làm quan văn thì thanh hiển, võ chức thì trung lương (Thiên Cơ đắc địa đi cùng Lương, Tả Hữu, Xương Khúc); sách không nêu bảng đắc địa riêng nên dùng cát tinh hội")
add(M, "CO_THIN_TUAT", [CO, br("Thìn", "Tuất")], "kl_co_thin_tuat_chien_thuat_chien_luoc", "verified", "p.80", "khả năng chiến thuật, chiến lược cao (Thiên Cơ ở Thìn/Tuất)")
add(M, "CO_MAO_DAU", [CO, br("Mão", "Dậu")], "kl_co_mao_dau_tai_nang_hien_hach", "verified", "p.80", "tài năng hiển hách, phú quý song toàn (Thiên Cơ ở Mão/Dậu)")
add("Phu Thê", "CO_TY_NGO_MUI", [CO, br("Tỵ", "Ngọ", "Mùi")], "kl_co_phu_the_som_lap_gia_dinh", "verified", "p.80", "sớm lập gia đình, người hôn phối nhỏ tuổi hơn nhiều (Thiên Cơ ở Phu Thê tại Tỵ/Ngọ/Mùi)")
add("Tài Bạch", "CO_NGO_MUI", [CO, anyof(OA("Thiên Cơ", "Cự Môn"), OA("Thiên Cơ", "Thiên Lương"), br("Ngọ", "Mùi"))], "kl_co_tai_phat_tai", "draft", "p.80", "phát tài (Cơ Cự, Cơ Lương hoặc Cơ đơn thủ ở Ngọ/Mùi); sách nói ở cung khác thì chật vật; điều kiện 'đơn thủ' hệ thống chưa tách")
add("Tài Bạch", "CO_LOC_MA", [CO, LOC, O("Thiên Mã")], "kl_co_loc_ma_dai_phu", "verified", "p.80", "đại phú (Thiên Cơ đi với Lộc, Mã ở Tài Bạch)")
add("Quan Lộc", "CO_LUONG_CU", [CO, anyof(has(OWNM, "Thiên Lương"), has(OWNM, "Cự Môn"))], "kl_co_quan_van_vo_kiem_toan", "verified", "p.80", "văn võ kiêm toàn (Cơ Lương hoặc Cơ Cự ở Quan Lộc)")
add("Quan Lộc", "CO_NGUYET", [OA("Thiên Cơ", "Thái Âm"), br("Dần", "Thân")], "kl_co_nguyet_dan_than_khieu_y_duoc", "verified", "p.80", "có khiếu y dược (Cơ Nguyệt ở Dần/Thân ở Quan Lộc)")
add("Điền Trạch", "CO_NHIEU", [CO, anyof(has(OWNM, "Thiên Lương"), allof(has(OWNM, "Thái Âm"), br("Thân")), allof(has(OWNM, "Cự Môn"), br("Mão")))], "kl_co_dien_nhieu_nha_dat", "verified", "p.80", "có nhiều nhà đất (Cơ Lương đồng cung, Cơ Nguyệt ở Thân hoặc Cơ Cự ở Mão)")
add("Điền Trạch", "CO_CU_DAU", [OA("Thiên Cơ", "Cự Môn"), br("Dậu")], "kl_co_cu_dau_nha_dat_it", "verified", "p.80", "nhà đất ít, dễ phá sản (Cơ Cự ở Dậu tại Điền Trạch)", "limit")
add("Phúc Đức", "CO_HOI_TY_SUU", [CO, br("Hợi", "Tý", "Sửu")], "kl_co_phuc_bac_phuc", "verified", "p.81", "phúc mỏng (Thiên Cơ ở Phúc Đức tại Hợi, Tý, Sửu)", "limit")
add("Phúc Đức", "CO_TY_NGO_MUI", [CO, br("Tỵ", "Ngọ", "Mùi")], "kl_co_phuc_huong_phuc", "verified", "p.81", "hưởng phúc (Thiên Cơ ở Phúc Đức tại Tỵ, Ngọ, Mùi)")
add("Phụ Mẫu", "CU_CO", [OA("Cự Môn", "Thiên Cơ")], "kl_cu_co_phu_me_xa_cach", "verified", "p.81", "cha mẹ xa cách (Cơ Cự ở Phụ Mẫu)", "limit")
add(M, "CO_LOC", [CO, LOC], "kl_co_loc_phat_dat", "verified", "p.81", "phát đạt (Thiên Cơ gặp Lộc)")
add(M, "CO_PHU_QUI", [CO, CATN(3)], "kl_co_nhieu_cat_tinh_phu_qui", "draft", "p.81", "hưởng phú quý (Cơ gặp Xương Khúc, Tả Hữu, Khoa Quyền Lộc, Khôi Việt); ngưỡng 'nhiều' = từ ba cát tinh")
add(M, "CO_KY_NGHE", [CO, T("Tả Phụ", "Hữu Bật"), T("Hỏa Tinh", "Linh Tinh")], "kl_co_ta_huu_hoa_linh_ky_nghe", "draft", "p.81", "thiên về kỹ nghệ, máy móc (Cơ gặp Tả Hữu, Hỏa Linh); sách còn kể Hình")
add(M, "CO_CU_KINH_DA", [OA("Thiên Cơ", "Cự Môn"), br("Mão", "Dậu"), T("Kình Dương", "Đà La")], "kl_co_cu_mao_dau_kinh_da_khau_thiet", "verified", "p.81", "dễ vướng khẩu thiệt, kiện tụng (Cự Cơ ở Mão/Dậu gặp Kình, Đà)", "limit")
add(M, "CO_CU_SONG_HAO", [OA("Thiên Cơ", "Cự Môn"), br("Mão", "Dậu"), T("Đại Hao"), T("Tiểu Hao")], "kl_co_cu_mao_dau_song_hao_phu_qui", "verified", "p.81", "hưởng phú quý (Cự Cơ ở Mão/Dậu gặp song Hao)")
add(M, "CO_NGO", [CO, br("Ngọ")], "kl_co_ngo_ben_nhay_muu_luoc", "verified", "p.81", "bén nhạy, mưu lược, lịch thiệp (Thiên Cơ ở Ngọ)")
add(M, "CO_TY", [CO, br("Tỵ")], "kl_co_ty_uy_tin_thao_luoc", "verified", "p.81", "đầy uy tín, có tài thao lược, giàu sang, hòa đồng (Thiên Cơ ở Tỵ)")
add(M, "CO_LUONG_THIN", [OA("Thiên Cơ", "Thiên Lương"), br("Thìn", "Tuất")], "kl_co_luong_uy_tin_nhan_hau", "verified", "p.81", "có uy tín, nhân hậu, mưu lược, trong sạch (Cơ Lương ở Thìn/Tuất)")
add(M, "CO_CU_MAO", [OA("Thiên Cơ", "Cự Môn"), br("Mão", "Dậu")], "kl_co_cu_mao_dau_thanh_cong_de_mang_hoa", "verified", "p.82", "tài năng mưu lược, thành công nhưng dễ mang họa miệng lưỡi (Cơ Cự ở Mão/Dậu)")
add(M, "CO_NGUYET_DAN", [OA("Thiên Cơ", "Thái Âm"), br("Dần")], "kl_co_nguyet_dan_vien_vong_dam_bac", "verified", "p.82", "dễ mơ mộng viễn vông, sống đạm bạc (Cơ Nguyệt ở Dần)", "limit")
add(M, "CO_NGUYET_THAN", [OA("Thiên Cơ", "Thái Âm"), br("Thân")], "kl_co_nguyet_than_tho_phu_giau", "verified", "p.82", "say mê thơ phú, văn chương, có thể nổi danh và giàu (Cơ Nguyệt ở Thân)")
add(M, "CO_SUU_MUI", [CO, br("Sửu", "Mùi")], "kl_co_suu_mui_duoc_ne_trong", "verified", "p.82", "được nể trọng vì mưu lược, giàu sang (Thiên Cơ ở Sửu/Mùi)")
add(M, "CO_TY2", [CO, br("Tý")], "kl_co_ty_bat_thiep_sang_suot", "verified", "p.82", "bặt thiệp, sáng suốt, thành công (Thiên Cơ ở Tý)")
# ---- pp.82-83 Thái Dương
NHAT = has(OWNM, "Thái Dương")
add(M, "NHAT_DAN_THIN", [NHAT, br("Dần", "Mão", "Thìn", "Tỵ", "Ngọ")], "kl_nhat_ban_ngay_thong_minh_quyen_qui", "verified", "p.83", "thông minh, quyền quý, giàu sang (Thái Dương ở cung ban ngày)")
add(M, "NHAT_BAN_DEM", [NHAT, br("Thân", "Dậu", "Tuất", "Hợi")], "kl_nhat_ban_dem_kem_minh_man", "verified", "p.83", "kém minh mẫn, hay nhầm lẫn (Thái Dương ở cung ban đêm)", "limit")
add(M, "NHAT_TAM_MINH", [NHAT, T("Đào Hoa"), T("Hồng Loan"), T("Thiên Hỷ")], "kl_nhat_tam_minh_rat_sang", "verified", "p.83", "Thái Dương rất sáng khi tam hợp Đào, Hồng, Hỷ ('tam minh')")
add(M, "NHAT_KY_SUU_MUI", [NHAT, has("palace.tu_hoa", "Hóa Kỵ"), br("Sửu", "Mùi")], "kl_nhat_ky_suu_mui_toan_my", "verified", "p.83", "thật toàn mỹ (Thái Dương đồng cung Hóa Kỵ ở Sửu/Mùi)")
add(M, "NHAT_HAM_HOI_TY", [NHAT, br("Hợi", "Tý")], "kl_nhat_ham_hoi_ty_thanh_liem_nho_nha", "verified", "p.83", "thanh liêm, nho nhã, từ thiện, say mê văn chương triết lý (Thái Dương hãm ở Hợi/Tý)")
add(M, "NHAT_HAM_CAT", [NHAT, br("Thân", "Dậu", "Tuất", "Hợi"), CATN(2)], "kl_nhat_ham_gap_quy_nhan_giau_danh", "draft", "p.83", "vẫn có thể giàu có, danh vọng khi được quý nhân nâng đỡ (Thái Dương hãm gặp Khôi Việt, Xương Khúc, Khoa Quyền Lộc, Đào Hồng Hỷ); ngưỡng 'nhiều' = từ hai cát tinh")
add(M, "NHAT_HAM_TT", [NHAT, br("Thân", "Dậu", "Tuất", "Hợi"), TT], "kl_nhat_ham_gap_tuan_triet_sang_lai", "verified", "p.83", "sáng lại, như người tài được thả khỏi tù (Thái Dương hãm gặp Tuần/Triệt)")
add(M, "NHAT_NGUYET_SUU_MUI", [OA("Thái Dương", "Thái Âm")], "kl_nhat_nguyet_day_dut_luong_lu", "verified", "p.83", "hay day dứt nội tâm, lưỡng lự, khó quyết đoán (Nhật Nguyệt đồng cung)", "limit")

slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for pal, rid, conds, claim, effect, status, loc, vi in R:
    rules.append({"id": f"TV_KL_STAR_{slug(pal)}_{slug(rid)}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "kl_stars",
        "description": f"Tử Vi Khảo Luận, phú và ý nghĩa các sao (paraphrased), cung {pal}: {vi} [KL {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": claim, "effect": effect, "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_KHAO_LUAN"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims.setdefault(claim, ("khuynh hướng " if effect == "support" else "hạn chế: ") + vi)
    if effect == "limit":
        claims.setdefault("limit:" + claim, "hạn chế: " + vi)
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_khao_luan_stars.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
