"""Generates data/pack_thuc_hanh_aux.json from Tử Vi Thực Hành pp.50-55 prose on Xương Khúc, Tả Hữu, Lộc Tồn, Thiên Mã, Tứ Hóa and Đào Hồng
(Mệnh-palace readings), paraphrased. Reading policy as elsewhere: đồng cung = own palace; hội/chiếu/gặp = tam phương (loose 'gặp' -> draft)."""
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
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}
own = lambda *ss: [has(OWN, s) for s in ss]
tam = lambda *ss: [has(TPS, s) for s in ss]
hoa = lambda h: has("palace.tu_hoa", h)
TAM3 = [has(TPH, h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")]
GOOD = ["miếu", "vượng", "đắc"]
CAT = anyof(*tam("Tử Vi", "Thiên Phủ", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật"), *[has(TPH, h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")])
SAT = anyof(*tam("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh"))
TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})
XK = lambda *x: anyof(*[has(OWN, s) for s in ("Văn Xương", "Văn Khúc")])
R = [  # palace, id, conds, claim, status, page, phrase
 ("Mệnh", "XK_CAT", [anyof(allof(has(OWN, "Văn Xương"), dig("Văn Xương", GOOD)), allof(has(OWN, "Văn Khúc"), dig("Văn Khúc", GOOD))), CAT], "xuong_khuc_som_do_dat_hien_vinh", "verified", "p.50", "sớm đỗ đạt, hiển vinh (Xương Khúc ở thế miếu vượng đắc hợp với cát tinh Tử Phủ, Khôi Việt, Tả Hữu, Tam Hóa)"),
 ("Mệnh", "KHUC_VU", [has(OWN, "Văn Khúc"), dig("Văn Khúc", GOOD), has(OWNM, "Vũ Khúc")], "khuc_vu_van_vo_uy_quyen", "verified", "p.50", "tay văn võ có uy quyền (Văn Khúc đắc địa đồng cung Vũ Khúc)"),
 ("Mệnh", "XK_HAM", [anyof(allof(has(OWN, "Văn Xương"), dig("Văn Xương", ["hãm"])), allof(has(OWN, "Văn Khúc"), dig("Văn Khúc", ["hãm"])))], "xuong_khuc_ham_nghe_thu_cong", "verified", "p.50", "hợp nghề thủ công khéo (Xương Khúc hãm địa)"),
 ("Mệnh", "XK_NOI_KHEO", [XK(), anyof(*tam("Thái Tuế", "Tấu Thư"))], "xuong_khuc_noi_kheo_hat_hay", "draft", "p.50", "nói khéo, hát hay, thích ca múa (Xương Khúc gặp Thái Tuế, Tấu Thư, Long Trì, Phượng Các); hai sao sau chưa có trong hệ thống"),
 ("Mệnh", "XK_LOC_TON", [XK(), has(OWN, "Lộc Tồn"), anyof(dig("Văn Xương", GOOD), dig("Văn Khúc", GOOD))], "xuong_khuc_loc_ton_tai_la", "verified", "p.50", "có tài đặc biệt (Xương Khúc miếu vượng gặp Lộc Tồn)"),
 ("Mệnh", "XK_TY_HOI", [br("Tỵ", "Hợi"), XK()], "xuong_khuc_ty_hoi_quy_hoac_phu", "verified", "p.50", "giàu sang (Xương Khúc ở Mệnh tại Tỵ hoặc Hợi)"),
 ("Mệnh", "TA_HUU_NHAN_HAU", [anyof(*own("Tả Phụ", "Hữu Bật"))], "ta_huu_nhan_hau_muu_tri", "verified", "p.51", "nhân hậu, thích giúp người khốn cùng, nhiều mưu trí (Tả hoặc Hữu ở Mệnh)"),
 ("Mệnh", "TA_HUU_LY_TONG", [anyof(*own("Tả Phụ", "Hữu Bật"))], "ta_huu_ly_tong_lap_nghiep", "verified", "p.51", "sớm rời nhà, tự tay lập nghiệp (Tả hoặc Hữu ở Mệnh, dù cát hay hung tinh)"),
 ("Mệnh", "TA_HUU_TU_PHU", [anyof(*own("Tả Phụ", "Hữu Bật")), anyof(*tam("Tử Vi", "Thiên Phủ")), anyof(*tam("Thiên Khôi", "Thiên Việt", "Văn Xương", "Văn Khúc"))], "ta_huu_tu_phu_qui_tuong", "draft", "p.51", "tướng quý, phúc lộc đầy đủ (Tả Hữu gặp Tử Phủ và các cát tinh); 'gặp' đọc là hội trong tam phương"),
 ("Mệnh", "TA_HUU_SUU_MUI", [br("Sửu", "Mùi"), *own("Tả Phụ", "Hữu Bật"), *TAM3], "ta_huu_suu_mui_khoa_quyen_loc_phu_quy", "verified", "p.51", "phú quý song toàn (Tả Hữu đồng cung ở Sửu hoặc Mùi, Khoa Quyền Lộc hội)"),
 ("Mệnh", "TA_HUU_GIAP_TU_VI", [has("palace.neighbor_stars", "Tả Phụ"), has("palace.neighbor_stars", "Hữu Bật"), has(OWNM, "Tử Vi")], "ta_huu_giap_tu_vi_oai_quyen", "verified", "p.51", "được nhiều người kính phục, rất oai quyền (Tả Hữu giáp Mệnh có Tử Vi)"),
 ("Mệnh", "LOC_HOA_LOC", [has(OWN, "Lộc Tồn"), hoa("Hóa Lộc"), nt(SAT)], "loc_ton_hoa_loc_lanh_tu", "draft", "p.51", "tính lãnh tụ, chuyên quyền độc đoán (Lộc Tồn gặp Hóa Lộc không bị sát chiếu); sách còn đòi sao tốt cùng chiếu"),
 ("Mệnh", "LOC_PHA", [has(OWN, "Lộc Tồn"), has(TPM, "Phá Quân")], "loc_ton_pha_chieu_tien_thieu", "verified", "p.52", "tiền tài thiếu thốn, sinh kế lẫn quẩn (Lộc Tồn ở Mệnh có Phá Quân chính chiếu)"),
 ("Mệnh", "LOC_MA", [has(OWN, "Lộc Tồn"), anyof(has(OWN, "Thiên Mã"), has(TPS, "Thiên Mã"))], "loc_ma_giao_tri_menh", "verified", "p.52", "dễ ra tiền, được nhiều người quý mến (Lộc Tồn và Thiên Mã chiếu nhau)"),
 ("Mệnh", "VCD_TAM_KHONG_LOC", [{"fact": "palace.has_no_major", "value": True}, anyof(*tam("Thiên Không", "Địa Không"), {"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True}), has(TPS, "Lộc Tồn")], "vcd_tam_khong_loc_giau_khong_ben", "draft", "p.53", "giàu sang nhưng không bền (Mệnh vô chính diệu gặp tam không và Lộc, Tồn); 'tam không' đọc là Tuần, Triệt, Thiên Không, Địa Không"),
 ("Mệnh", "MA_TAI_NANG", [has(OWN, "Thiên Mã")], "thien_ma_tai_nang_man_tiep", "verified", "p.52", "tài năng mẫn tiệp, tháo vát, nhanh nhẹn (Thiên Mã ở Mệnh, gọi là Dịch Mã)"),
 ("Mệnh", "CHIEN_MA", [has(OWN, "Thiên Mã"), anyof(*own("Hỏa Tinh", "Linh Tinh"))], "chien_ma_binh_quyen", "verified", "p.52", "binh quyền rực rỡ (Thiên Mã đồng cung Hỏa hoặc Linh: Chiến mã)"),
 ("Mệnh", "PHU_DU_MA", [br("Dần", "Thân"), has(OWN, "Thiên Mã"), anyof(*tam("Tử Vi", "Thiên Phủ"))], "phu_du_ma_tai_can_uy_quyen", "verified", "p.52", "tài cán, uy quyền hiển hách (Thiên Mã ở Dần hoặc Thân gặp Tử Phủ: Phù dư mã)"),
 ("Mệnh", "CHIEN_TUC_MA", [has(OWN, "Thiên Mã"), anyof(has(OWN, "Đà La"), has(TPS, "Đà La"))], "chien_tuc_ma_trac_tro", "verified", "p.52", "nhiều trắc trở (Thiên Mã đồng cung hoặc chiếu với Đà La: Chiến túc mã)"),
 ("Mệnh", "THU_HUNG_MA", [has(OWN, "Thiên Mã"), has(TPM, "Thái Dương"), has(TPM, "Thái Âm")], "thu_hung_ma_hanh_thong", "draft", "p.52", "mọi sự hanh thông (Thiên Mã gặp Nhật Nguyệt đắc địa: Thư hùng mã); độ sáng chưa kiểm"),
 ("Mệnh", "HL_MENH", [hoa("Hóa Lộc")], "hoa_loc_menh_thang_sanh_an_tai_loc", "verified", "p.52", "tính thẳng, sành ăn, tài lộc vinh vượng (Hóa Lộc ở Mệnh)"),
 ("Mệnh", "HL_TU_MO", [hoa("Hóa Lộc"), br("Thìn", "Tuất", "Sửu", "Mùi")], "hoa_loc_tai_loc_tot", "verified", "p.52", "tài lộc giảm đi quá nửa phần phú quý (Hóa Lộc đóng ở Tứ Mộ); gặp Tham, Vũ thì lại rực rỡ"),
 ("Mệnh", "HL_DAN_MAO", [hoa("Hóa Lộc"), br("Dần", "Mão")], "hoa_loc_dan_mao_tien_ben", "verified", "p.52", "giàu mà tiền bạc bền vững (Hóa Lộc ở Dần hoặc Mão)"),
 ("Mệnh", "HL_TY_NGO", [hoa("Hóa Lộc"), br("Tý", "Ngọ")], "hoa_loc_ty_ngo_van_chuong", "verified", "p.52", "giỏi văn chương (Hóa Lộc ở Tý hoặc Ngọ)"),
 ("Mệnh", "HL_LUONG", [hoa("Hóa Lộc"), has(OWNM, "Thiên Lương"), dig("Thiên Lương", GOOD)], "loc_luong_giau_giup_nguoi", "verified", "p.53", "giàu có, hay đem của giúp người khốn khó (Hóa Lộc đồng cung Thiên Lương miếu địa)"),
 ("Mệnh", "HQ_TU_PHU", [hoa("Hóa Quyền"), anyof(*tam("Tử Vi", "Thiên Phủ"))], "quyen_tu_phu_uy_quyen", "verified", "p.53", "tạo được uy quyền hiển hách (Hóa Quyền gặp Tử, Phủ)"),
 ("Mệnh", "HQ_CU_VU", [hoa("Hóa Quyền"), has(TPM, "Cự Môn"), has(TPM, "Vũ Khúc")], "quyen_cu_vu_nguoi_ne_so", "verified", "p.53", "xuất tướng nhập tướng, được nhiều người kính sợ (Hóa Quyền gặp Cự, Vũ)"),
 ("Mệnh", "HQ_SAT", [hoa("Hóa Quyền"), SAT], "quyen_sat_lieu_linh", "draft", "p.53", "tính hay liều lĩnh, làm việc dễ thất bại (Hóa Quyền gặp sát tinh); 'gặp' đọc là hội trong tam phương"),
 ("Mệnh", "HQ_TT", [hoa("Hóa Quyền"), TT], "quyen_tuan_triet_cong_danh_trac_tro", "verified", "p.53", "công danh trắc trở, thành ít bại nhiều (Hóa Quyền gặp Tuần hoặc Triệt)"),
 ("Mệnh", "HK_VAN_TINH", [hoa("Hóa Khoa"), anyof(*tam("Văn Xương", "Văn Khúc")), anyof(*tam("Thiên Khôi", "Thiên Việt"))], "khoa_van_tinh_cong_danh_hien_dat", "verified", "p.53", "công danh tất hiển đạt (Hóa Khoa gặp Xương Khúc, Khôi Việt kết thành bộ văn tinh)"),
 ("Mệnh", "HK_QUYEN_LOC", [hoa("Hóa Khoa"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc")], "khoa_quyen_loc_tai_danh_hung_vuong", "verified", "p.53", "tài và danh hùng vượng (Hóa Khoa gặp Quyền, Lộc: bộ Quý tinh)"),
 ("Mệnh", "HK_SAT", [hoa("Hóa Khoa"), SAT], "khoa_bi_sat_cong_danh_kho", "draft", "p.53", "công danh khó thành đạt, tiền của khó khăn (Hóa Khoa bị hung tinh xâm phạm); 'nhiều hung tinh' đọc là có sát tinh trong tam phương"),
 ("Mệnh", "HKY_VAN_TINH", [hoa("Hóa Kỵ"), anyof(*tam("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"))], "ky_van_tinh_da_hoc_it_thanh_dat", "verified", "p.54", "học nhiều nhưng ít thành đạt công danh (Hóa Kỵ gặp văn tinh Xương Khúc, Khôi Việt)"),
 ("Mệnh", "HKY_KHOA", [hoa("Hóa Kỵ"), has(TPH, "Hóa Khoa"), br("Hợi", "Tý")], "ky_khoa_hoi_ty_can_trong", "verified", "p.53", "cẩn trọng lời nói và việc làm, nhiều người kính trọng (Hóa Kỵ gặp Hóa Khoa ở Hợi hoặc Tý)"),
 ("Mệnh", "HKY_CU", [hoa("Hóa Kỵ"), has(OWNM, "Cự Môn")], "ky_cu_thi_phi_kien_tung", "verified", "p.54", "dễ có thị phi, tranh cãi (Hóa Kỵ đồng cung Cự Môn)"),
 ("Mệnh", "HKY_DAO_HONG", [hoa("Hóa Kỵ"), anyof(*tam("Hồng Loan", "Đào Hoa"))], "ky_dao_hong_duyen_rac_roi", "verified", "p.54", "chuyện tình duyên lắm rắc rối (Hóa Kỵ gặp Hồng, Đào)"),
 ("Mệnh", "HKY_MIEU", [hoa("Hóa Kỵ"), br("Hợi", "Tý", "Dần", "Mão")], "ky_mieu_dia_it_bat_loi", "verified", "p.53", "ít bất lợi hơn (Hóa Kỵ ở thế miếu địa tại Hợi, Tý, Dần, Mão)"),
 ("Mệnh", "HKY_TU_MO_NHAT_NGUYET", [hoa("Hóa Kỵ"), br("Thìn", "Tuất", "Sửu", "Mùi"), anyof(*[has(OWNM, s) for s in ("Thái Dương", "Thái Âm")])], "ky_tu_mo_nhat_nguyet_ruc_ro", "verified", "p.54", "rực rỡ, như mây ngũ sắc chầu mặt trời mặt trăng (Hóa Kỵ ở Tứ Mộ gặp Nhật hoặc Nguyệt)"),
 ("Quan Lộc", "DAO_HONG", [anyof(*own("Đào Hoa", "Hồng Loan"))], "quan_dao_hong_giau_sang", "verified", "p.55", "giàu sang (Đào, Hồng ở Quan Lộc)"),
 ("Mệnh", "DH_VAN_TINH", [anyof(*own("Đào Hoa", "Hồng Loan")), anyof(*tam("Văn Xương", "Văn Khúc"))], "dao_hong_van_tinh_do_som", "verified", "p.55", "đỗ đạt sớm (Đào, Hồng gặp văn tinh)"),
 ("Thiên Di", "DAO_HONG", [anyof(*own("Đào Hoa", "Hồng Loan"))], "di_dao_hong_ly_tong_lap_nghiep", "verified", "p.55", "rời nhà lập nghiệp (Đào, Hồng ở Thiên Di)"),
 ("Mệnh", "DH_OWN", [anyof(*own("Đào Hoa", "Hồng Loan"))], "dao_hong_menh_may_man_chong_qua", "verified", "p.55", "may mắn đến nhanh rồi qua nhanh (Đào, Hồng đóng ở Mệnh)"),
 ("Mệnh", "DH_CHIEU", [anyof(*tam("Đào Hoa", "Hồng Loan")), nt(anyof(*own("Đào Hoa", "Hồng Loan")))], "dao_hong_chieu_menh_dep", "verified", "p.55", "đẹp hơn khi Đào, Hồng chỉ xung chiếu Mệnh (không đóng ở Mệnh)"),
]
slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for pal, rid, conds, claim, status, loc, vi in R:
    effect = "limit" if rid == "HL_TU_MO" else "support"
    exc = [anyof(has(TPM, "Tham Lang"), has(TPM, "Vũ Khúc"))] if rid == "HL_TU_MO" else []
    rules.append({"id": f"TV_TH_AUX_{slug(pal)}_{rid}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "th_aux",
        "description": f"Tử Vi Thực Hành, sao phụ (paraphrased), cung {pal}: {vi} [TH {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": claim, "effect": effect, "scope": "natal"}],
        "exceptions": exc, "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_THUC_HANH"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims.setdefault(claim, "khuynh hướng " + vi.split(" (")[0] + (" (" + vi.split(" (", 1)[1] if " (" in vi else ""))
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_thuc_hanh_aux.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
cur["limit:hoa_loc_tai_loc_tot"] = cur.get("limit:hoa_loc_tai_loc_tot", "tài lộc giảm nhiều khi Hóa Lộc đóng ở Tứ Mộ")
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
