"""Generates data/pack_thuc_hanh_aux2.json from Tử Vi Thực Hành pp.56-69 (Trường Sinh/Thái Tuế/Bác Sĩ rings, sát tinh, Lục Bại, Không Kiếp,
Tuần Triệt), paraphrased. Only legible sentences are encoded; harm predictions (death, injury, prison, illness) are skipped on purpose.
Branch lists follow the book's own dignity statements. Reading policy: đồng cung = own palace; hội/chiếu = tam phương; bare 'gặp' -> draft."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPM, TPS, TPH = "palace.own_stars", "palace.own_major_stars", "palace.tam_phuong_majors", "palace.tam_phuong_stars", "palace.tam_phuong_tu_hoa"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
nt = lambda x: {"not": x}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
nbr = lambda *b: {"fact": "palace.branch", "operator": "not_in", "value": list(b)}
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}
own = lambda *ss: [has(OWN, s) for s in ss]
tam = lambda *ss: [has(TPS, s) for s in ss]
hoa = lambda h: has("palace.tu_hoa", h)
GOOD = ["miếu", "vượng", "đắc"]
TUMO = ("Thìn", "Tuất", "Sửu", "Mùi")
SAT = anyof(*tam("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh"))
CAT = anyof(*tam("Tử Vi", "Thiên Phủ", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật"))
TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})
H = lambda *s: anyof(*own(*s))
R = [  # palace, id, conds, claim, status, page, phrase
 # --- sát tinh
 ("Mệnh", "KINH_DAC", [has(OWN, "Kình Dương"), br(*TUMO)], "kinh_dac_dia_cuong_cuong_dung_manh", "verified", "p.62", "tính khí cương cường, dũng mãnh, quả quyết, nhiều cơ mưu nhưng hay tự đắc, kiêu căng (Kình đắc địa ở Tứ mộ)"),
 ("Mệnh", "KINH_KHAC", [has(OWN, "Kình Dương"), nbr(*TUMO, "Tý", "Ngọ", "Mão", "Dậu")], "kinh_cung_khac_hung_bao_lieu_linh", "verified", "p.62", "tính hung bạo, liều lĩnh, bướng bỉnh, hay gian trá (Kình ở các cung ngoài Tứ mộ)"),
 ("Mệnh", "KINH_LUC_SI", [has(OWN, "Kình Dương"), has(OWN, "Lực Sĩ")], "kinh_luc_si_to_lon_khoe_binh_su", "verified", "p.63", "to lớn khoẻ mạnh, có tài về binh sự (Kình đồng cung Lực Sĩ)"),
 ("Mệnh", "KINH_HOA_TU_MO", [has(OWN, "Kình Dương"), has(OWN, "Hỏa Tinh"), br(*TUMO)], "kinh_hoa_tu_mo_oai_quyen_danh_tieng", "verified", "p.63", "có oai quyền, danh tiếng (Kình đồng cung Hỏa ở Tứ mộ)"),
 ("Mệnh", "KINH_HOA_THAM_VU", [has(OWN, "Kình Dương"), has(OWN, "Hỏa Tinh"), br(*TUMO), has(TPM, "Tham Lang"), has(TPM, "Vũ Khúc")], "kinh_hoa_tham_vu_cai_the_anh_hung", "draft", "p.63", "khí chất anh hùng, oai vệ khiến người khiếp sợ (Kình Hỏa ở Tứ mộ gặp Tham, Vũ); 'gặp' đọc là hội trong tam phương"),
 ("Mệnh", "LOC_TON_GIAP_KY", [has(OWN, "Lộc Tồn"), hoa("Hóa Kỵ")], "loc_ton_giap_kinh_da_ky_ly_huong", "verified", "p.63", "túng thiếu, nên sớm rời quê mưu sinh mới đủ cơm áo (Lộc Tồn bị Kình, Đà kẹp và Mệnh có Hóa Kỵ)"),
 ("Mệnh", "DA_DAC", [has(OWN, "Đà La"), br(*TUMO)], "da_dac_dia_can_dam_tham_tram_muu_mo", "verified", "p.63", "can đảm, uy dũng nhưng thâm trầm, lắm thủ đoạn mưu mô (Đà La đắc địa ở Tứ mộ)"),
 ("Mệnh", "HOA_DAC", [has(OWN, "Hỏa Tinh"), br("Dần", "Ngọ", "Tuất", "Tỵ", "Dậu", "Sửu")], "hoa_linh_dac_dia_co_chi_khi", "verified", "p.64", "có chí khí, sức khoẻ bền (Hỏa đắc địa ở Mệnh)"),
 ("Mệnh", "HOA_HAM", [has(OWN, "Hỏa Tinh"), br("Thân", "Tý", "Thìn")], "hoa_linh_ham_nham_hiem_gian_ta", "verified", "p.64", "nham hiểm, gian tà, hay liều lĩnh, dễ sa vào đam mê (Hỏa hãm địa thủ Mệnh)"),
 ("Mệnh", "HOA_KHOA_QUYEN", [has(OWN, "Hỏa Tinh"), anyof(hoa("Hóa Khoa"), hoa("Hóa Quyền"), has(TPH, "Hóa Khoa"), has(TPH, "Hóa Quyền"))], "hoa_khoa_quyen_gioi_van_vo", "draft", "p.64", "giỏi cả văn lẫn võ (Hỏa gặp Khoa, Quyền); 'gặp' đọc là hội trong tam phương"),
 ("Tài Bạch", "HOA_TAI", [has(OWN, "Hỏa Tinh")], "hoa_o_tai_tan_tai", "draft", "p.64", "dễ tán tài (Hỏa đóng cung Tài); câu sách bị đứt chữ, chủ ngữ suy từ đoạn trên"),
 ("Mệnh", "LINH_MENH", [has(OWN, "Linh Tinh")], "linh_menh_ha_tien_so_do", "verified", "p.65", "hà tiện, hay so đo chi tiêu (Linh Tinh thủ Mệnh)"),
 ("Tài Bạch", "LINH_TAI", [has(OWN, "Linh Tinh"), br("Dần", "Tuất", "Thìn", "Mùi")], "linh_dac_dia_tai_ben_vung", "draft", "p.65", "tiền của bền vững (Linh đắc địa đóng Tài); bảng miếu địa Linh trong sách tự mâu thuẫn nên chỉ lấy các cung miếu rõ ràng"),
 ("Mệnh", "LINH_TU_PHU", [has(OWN, "Linh Tinh"), anyof(*tam("Tử Vi", "Thiên Phủ")), anyof(*tam("Tả Phụ", "Hữu Bật"))], "linh_tu_phu_ta_huu_quy_hien", "draft", "p.65", "quý hiển (Linh gặp Tử, Phủ, Tả, Hữu); câu sách bị mất chữ"),
 # --- Lục bại
 ("Mệnh", "HAO_MENH", [anyof(*own("Đại Hao", "Tiểu Hao"))], "song_hao_tieu_xai_choi_boi", "verified", "p.65", "không kiên chí, thích ăn ngon mặc đẹp, dễ đam mê chơi bời, vung phí tiền bạc (Đại/Tiểu Hao thủ Mệnh)"),
 ("Mệnh", "HAO_MAO_DAU", [anyof(*own("Đại Hao", "Tiểu Hao")), br("Mão", "Dậu")], "hao_mao_dau_thong_minh_ham_choi_hoc_say", "verified", "p.65", "thông minh, tuy ham chơi nhưng lúc học cũng say mê, hiểu rộng; về sau có thể giàu sang (Hao đắc địa ở Mão hoặc Dậu)"),
 ("Mệnh", "HAO_THUY_TRIEU", [anyof(*own("Đại Hao", "Tiểu Hao")), br("Mão", "Dậu")], "hao_thuy_trieu_dong_tien_vao_ra", "verified", "p.65", "tiền vào như nước, ra cũng như nước (cách 'chúng thuỷ triều đông' của Hao ở Mão, Dậu)"),
 ("Mệnh", "HAO_TUYET", [anyof(*own("Đại Hao", "Tiểu Hao")), has(OWN, "Tuyệt")], "hao_tuyet_khon_ngoan_man_tra", "verified", "p.65", "khôn ngoan nhưng hơi man trá (Hao đồng cung Tuyệt)"),
 ("Mệnh", "HAO_PHA_QUAN", [anyof(*own("Đại Hao", "Tiểu Hao")), anyof(*tam("Phá Quân"))], "hao_pha_quan_tung_thieu", "draft", "p.65", "dễ túng thiếu (Song Hao gặp Phá Quân); 'gặp' đọc là hội"),
 ("Mệnh", "HO_DAC_BAN_DEM", [has(OWN, "Bạch Hổ"), br("Dần", "Thân", "Mão", "Dậu")], "ho_dac_dia_thao_luoc_ly_luan", "verified", "p.66", "có thao lược, lý luận giỏi, hợp chính trị hoặc nghề luật (Tang, Hổ đắc địa)"),
 ("Mệnh", "HO_TAU_THU", [has(OWN, "Bạch Hổ"), has(OWN, "Tấu Thư")], "ho_tau_thu_van_tai_hien_dat", "verified", "p.66", "văn tài hiển đạt (Hổ gặp Tấu Thư: 'cọp đội hòm sắc')"),
 ("Mệnh", "HO_PHI_LIEM", [has(OWN, "Bạch Hổ"), has(OWN, "Phi Liêm")], "ho_phi_liem_nhe_buoc_cong_danh", "draft", "p.66", "nhẹ bước công danh ('cọp mọc cánh'); 'gặp' nên chỉ lấy khi đồng cung"),
 # --- Không Kiếp, Thiên Không
 ("Mệnh", "KK_DAC", [anyof(*own("Địa Không", "Địa Kiếp")), br("Tỵ", "Hợi", "Dần", "Thân")], "khong_kiep_dac_tram_tinh_co_muu_som_cong_danh", "verified", "p.67", "trầm tĩnh, suy tư, có cơ mưu, can đảm, sớm đoạt công danh (Kiếp/Không đắc địa ở Tỵ, Hợi, Dần, Thân)"),
 ("Mệnh", "KK_HAM", [anyof(*own("Địa Không", "Địa Kiếp")), nbr("Tỵ", "Hợi", "Dần", "Thân")], "khong_kiep_ham_quy_quyet_ich_ky", "verified", "p.68", "quỷ quyệt, ích kỷ, suốt đời khó vừa lòng với mình (Kiếp/Không hãm ở Mệnh)"),
 ("Mệnh", "KK_DAO_HONG", [anyof(*own("Địa Không", "Địa Kiếp")), anyof(*tam("Đào Hoa", "Hồng Loan"))], "khong_kiep_dao_hong_duyen_dang_do", "verified", "p.67", "duyên nợ dang dở, phải trải qua vài lần cưới xin (Kiếp/Không hội Đào, Hồng)"),
 ("Mệnh", "KK_QUYEN", [anyof(*own("Địa Không", "Địa Kiếp")), hoa("Hóa Quyền")], "khong_kiep_quyen_cong_danh_trac_tro", "draft", "p.68", "công danh trắc trở (Kiếp/Không gặp Hóa Quyền)"),
 ("Quan Lộc", "KK_HAM", [anyof(*own("Địa Không", "Địa Kiếp")), nbr("Tỵ", "Hợi", "Dần", "Thân")], "khong_kiep_quan_ham_kho_dat_cong_danh", "verified", "p.68", "khó đạt công danh (Kiếp/Không hãm đóng cung Quan)"),
 ("Mệnh", "TK_DAO", [has(OWN, "Thiên Không"), anyof(*tam("Đào Hoa"))], "thien_khong_dao_hoa_gian_hung_xao_tra", "draft", "p.67", "đa mưu nhưng xảo trá (Thiên Không hội Đào Hoa)"),
 ("Mệnh", "TK_HONG", [has(OWN, "Thiên Không"), anyof(*tam("Hồng Loan"))], "thien_khong_hong_loan_an_dat_tu", "draft", "p.67", "thiên về nơi vắng vẻ, ở ẩn hoặc tu hành (Thiên Không hội Hồng Loan)"),
 ("Mệnh", "TK_TUONG", [has(OWN, "Thiên Không"), has(OWNM, "Thiên Tướng"), dig("Thiên Tướng", GOOD)], "thien_khong_tuong_uy_quyen_vo_tuong", "draft", "p.67", "có uy quyền thống lãnh, phát về võ (Thiên Tướng đắc địa gặp Thiên Không)"),
 # --- Thái Tuế / Quan Phù / Tướng Quân / các vòng khác
 ("Mệnh", "TUE_MENH", [has(OWN, "Thái Tuế")], "thai_tue_lanh_lung_ly_luan", "verified", "p.60", "lạnh lùng, hay xét đoán, giỏi lý luận (Thái Tuế thủ Mệnh)"),
 ("Mệnh", "TUE_VAN_TINH", [has(OWN, "Thái Tuế"), anyof(*tam("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"))], "thai_tue_van_tinh_thi_cu_cong_danh", "verified", "p.60", "lợi cho thi cử, cầu công danh (Thái Tuế hội Xương, Khúc, Khôi, Việt)"),
 ("Mệnh", "TUE_KY_DA", [has(OWN, "Thái Tuế"), anyof(hoa("Hóa Kỵ"), has(TPH, "Hóa Kỵ"), *tam("Đà La"))], "thai_tue_ky_da_thi_phi", "verified", "p.60", "trắc trở, bất lợi công danh, dễ tai tiếng thị phi (Thái Tuế hội Hóa Kỵ hoặc Đà La)"),
 ("Mệnh", "TUONG_QUAN", [has(OWN, "Tướng Quân")], "tuong_quan_can_truong_lanh_dao", "verified", "p.59", "can trường, hiên ngang, kiêu căng, thích lãnh đạo (Tướng Quân thủ Mệnh)"),
 ("Mệnh", "TUONG_TUONG", [has(OWN, "Tướng Quân"), has(OWNM, "Thiên Tướng"), dig("Thiên Tướng", GOOD)], "luong_tuong_uy_quyen_hien_hach", "verified", "p.59", "uy quyền hiển hách (Tướng Quân đồng cung Thiên Tướng đắc địa: 'lưỡng tướng')"),
 ("Mệnh", "TUONG_TT", [has(OWN, "Tướng Quân"), TT], "tuong_quan_tuan_triet_ton_hai_cong_danh", "verified", "p.60", "tổn hại công danh ('tướng cụt đầu', Tướng Quân gặp Tuần hoặc Triệt)"),
 ("Mệnh", "TAU_THU", [has(OWN, "Tấu Thư")], "tau_thu_vui_ve_kheo_noi", "verified", "p.60", "vui vẻ, khôn khéo, ưa nói vừa lòng người (Tấu Thư thủ Mệnh)"),
 ("Tử Tức", "PHI_LIEM", [has(OWN, "Phi Liêm")], "phi_liem_tu_tuc_giam_so_con", "verified", "p.60", "số con có phần ít đi (Phi Liêm ở cung Tử Tức)"),
 ("Huynh Đệ", "PHI_LIEM", [has(OWN, "Phi Liêm")], "phi_liem_huynh_de_giam_anh_em", "verified", "p.60", "số anh em có phần ít đi (Phi Liêm ở cung Huynh Đệ)"),
 ("Mệnh", "THANH_LONG", [has(OWN, "Thanh Long"), nt(SAT)], "thanh_long_tai_bien_hoa_cong_viec", "verified", "p.56", "có tài biến hoá công việc (Thanh Long ở Mệnh, không sát tinh)"),
 ("Phúc Đức", "HONG_NGA_MI", [has(OWN, "Hồng Loan")], "hong_phuc_nga_mi_tac_an", "verified", "p.56", "đem lại sự rực rỡ ('nga mi tác án', Hồng Loan đóng cung Phúc)"),
 # --- Trường Sinh ring
 ("Mệnh", "QUAN_DOI", [has(OWN, "Quan Đới")], "quan_doi_ham_cong_danh_chuc_vi", "verified", "p.58", "ham mê công danh, chức vị, quyền hành (Quan Đới)"),
 ("Mệnh", "LAM_QUAN", [has(OWN, "Lâm Quan")], "lam_quan_noi_nang_kieu_ky", "verified", "p.58", "nói năng kiêu kỳ, thích khoe điệu bộ (Lâm Quan)"),
 ("Mệnh", "MOC_DUC", [has(OWN, "Mộc Dục")], "moc_duc_chai_chuot_thich_doi", "verified", "p.58", "ưa chải chuốt, làm dáng, thích thay đổi, hay nhầm lẫn (Mộc Dục)"),
 ("Mệnh", "MOC_DUC_VCD", [has(OWN, "Mộc Dục"), {"fact": "palace.has_no_major", "value": True}], "moc_duc_vcd_hoc_hanh_do", "verified", "p.58", "học hành dở, dù cố cũng khó hiển danh bằng học vấn (Mộc Dục ở Mệnh vô chính diệu)"),
 ("Mệnh", "DE_VUONG_TU_VI", [has(OWN, "Đế Vượng"), has(OWNM, "Tử Vi")], "luong_de_tai_lanh_dao", "verified", "p.58", "có tài lãnh đạo ('lưỡng đế': Đế Vượng đồng cung Tử Vi)"),
 ("Phúc Đức", "SUY", [has(OWN, "Suy")], "suy_phuc_ho_mac_sa_sut", "verified", "p.59", "họ mạc dễ sa sút, ly tán (sao Suy đóng cung Phúc Đức)"),
 ("Phúc Đức", "MO_QUYEN", [has(OWN, "Mộ"), br(*TUMO), hoa("Hóa Quyền")], "mo_quyen_dai_phuc_duc", "verified", "p.59", "nhà đại phúc đức, bốn đời vinh hiển (sao Mộ ở Tứ mộ gặp Hóa Quyền, cung Phúc)"),
 ("Điền Trạch", "MO", [has(OWN, "Mộ")], "mo_dien_tai_tan_tien_giu_cua", "verified", "p.59", "tần tiện, chịu dành dụm giữ của (sao Mộ ở Điền/Tài)"),
 ("Tài Bạch", "MO", [has(OWN, "Mộ")], "mo_dien_tai_tan_tien_giu_cua", "verified", "p.59", "tần tiện, chịu dành dụm giữ của (sao Mộ ở Điền/Tài)"),
 ("Mệnh", "DUONG", [has(OWN, "Dưỡng")], "duong_menh_nguoi_men_nhan_con_nuoi", "verified", "p.59", "được nhiều người mến, có người muốn nhận làm con nuôi (sao Dưỡng ở Mệnh hoặc Phúc)"),
 ("Phúc Đức", "DUONG", [has(OWN, "Dưỡng")], "duong_menh_nguoi_men_nhan_con_nuoi", "verified", "p.59", "được nhiều người mến, có người muốn nhận làm con nuôi (sao Dưỡng ở Mệnh hoặc Phúc)"),
 # --- Tuần Triệt vị trí
 ("Mệnh", "TUAN_DAN_MAO", [{"fact": "palace.tuan", "value": True}, br("Dần", "Mão")], "tuan_dan_mao_hoanh_phat", "verified", "p.62", "có thể hoạnh phát (Tuần đóng Dần hoặc Mão: khí dương tụ thanh khiết)"),
 ("Mệnh", "TRIET_THAN_DAU", [{"fact": "palace.triet", "value": True}, br("Thân", "Dậu")], "triet_than_dau_dac_cach_hung_vuong", "verified", "p.62", "đắc cách, hưng vượng (Triệt đóng Thân hoặc Dậu)"),
 ("Mệnh", "TT_NGO_MUI", [TT, br("Ngọ", "Mùi")], "tuan_triet_ngo_mui_rong_rai_hoa_nhu", "verified", "p.62", "tính rộng rãi, hoà nhã, êm đềm (Tuần/Triệt đóng Ngọ hoặc Mùi, giữa hai cung âm dương)"),
]
slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for pal, rid, conds, claim, status, loc, vi in R:
    rules.append({"id": f"TV_TH_AUX2_{slug(pal)}_{rid}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "th_aux2",
        "description": f"Tử Vi Thực Hành, sao phụ/vòng sao (paraphrased), cung {pal}: {vi} [TH {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": claim, "effect": "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_THUC_HANH"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims.setdefault(claim, "khuynh hướng " + vi)
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_thuc_hanh_aux2.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
