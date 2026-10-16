"""Generates data/pack_khao_luan_aux.json from Tử Vi Khảo Luận pp.225-230: what each auxiliary star means when it sits at Mệnh, the
Thiên Không passage, and the twelve 'Đào – Hồng – Thiên Không by birth year' readings. Paraphrased."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, TPS = "palace.own_stars", "palace.tam_phuong_stars"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
own = lambda *ss: [has(OWN, s) for s in ss]
TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})
M = [  # id, conds, claim, status, page, phrase
 ("KINH_DA", [anyof(*own("Kình Dương", "Đà La"))], "kinh_da_menh_ngang_nguoc", "verified", "p.228", "tính ngang ngược, tự đắc (Kình hoặc Đà ở Mệnh)"),
 ("KHONG_KIEP", [anyof(*own("Địa Không", "Địa Kiếp"))], "khong_kiep_menh_ich_ky_lieu_linh", "verified", "p.228", "thiên về ích kỷ, liều lĩnh (Địa Không hoặc Địa Kiếp ở Mệnh)"),
 ("HOA_LINH", [anyof(*own("Hỏa Tinh", "Linh Tinh"))], "hoa_linh_menh_nong_nay", "verified", "p.228", "nghĩa khí nhưng nóng nảy (Hỏa hoặc Linh ở Mệnh)"),
 ("TUAN_TRIET", [TT], "tuan_triet_menh_vui_it_buon_nhieu", "verified", "p.228", "vui ít buồn nhiều (Tuần hoặc Triệt đóng ở Mệnh)"),
 ("THIEN_KHONG", own("Thiên Không"), "thien_khong_menh_khong_tham_may_cuoi", "verified", "p.225", "không tham tiền tài nhưng may mắn đến vào lúc cuối (Thiên Không ở Mệnh)"),
 ("HONG_KHONG", [*own("Hồng Loan"), anyof(has(OWN, "Thiên Không"), has(TPS, "Thiên Không"))], "hong_thien_khong_thoat_tuc", "verified", "p.225", "thảnh thơi, thoát tục, coi nhẹ danh vọng, có thể hướng về tu hành (Hồng Loan gặp Thiên Không đồng cung hoặc xung chiếu)"),
 ("XUONG_KHUC_DAC_DIA", [br("Thìn", "Tuất", "Sửu", "Mùi", "Tỵ", "Hợi"), anyof(*own("Văn Xương", "Văn Khúc"))], "xuong_khuc_dac_dia_tai_hoa", "verified", "p.228", "tài hoa, có công danh (Xương Khúc ở Thìn, Tuất, Sửu, Mùi, Tỵ hoặc Hợi)"),
 ("THIEN_MA", own("Thiên Mã"), "thien_ma_menh_vat_va_hanh_dong", "verified", "p.229", "năng động, ý chí hành động nhưng vất vả (Thiên Mã ở Mệnh nằm trong tam hợp Tuế Phá – Tang Môn – Điếu Khách)"),
 ("TA_HUU", [anyof(*own("Tả Phụ", "Hữu Bật"))], "ta_huu_menh_cham_chi_gioi_giang", "verified", "p.229", "chăm chỉ, giỏi giang (Tả hoặc Hữu ở Mệnh)"),
 ("LOC_TON", own("Lộc Tồn"), "loc_ton_menh_nhan_tu_deo_dat", "verified", "p.229", "nhân từ, hay cứu giúp, dè dặt khôn ngoan nhưng dễ keo kiệt và cô đơn (Lộc Tồn ở Mệnh)"),
 ("SONG_HAO", own("Đại Hao", "Tiểu Hao"), "song_hao_menh_vat_va_hao_tai", "verified", "p.229", "vất vả ngược xuôi, hao hụt tài lộc (Song Hao ở Mệnh)"),
 ("TUONG_QUAN", own("Tướng Quân"), "tuong_quan_menh_tu_cao", "verified", "p.229", "tự cao, ‘ta đây’ (Tướng Quân ở Mệnh)"),
 ("TAU_THU", own("Tấu Thư"), "noi_ngot_de_thuyet_phuc", "verified", "p.229", "lời nói ngọt, dễ thuyết phục (Tấu Thư ở Mệnh)"),
 ("HY_THAN", own("Hỷ Thần"), "hy_than_menh_buon_van_tuoi_vui", "verified", "p.229", "có buồn vẫn giữ vẻ tươi vui (Hỷ Thần ở Mệnh)"),
 ("BENH_PHU", own("Bệnh Phù"), "benh_phu_menh_vui_van_u_sau", "verified", "p.229", "vui cũng mang vẻ u sầu (Bệnh Phù ở Mệnh)"),
 ("PHUC_BINH", own("Phục Binh"), "phuc_binh_menh_sau_trong_long", "verified", "p.229", "hay giấu nỗi sầu trong lòng (Phục Binh ở Mệnh)"),
 ("QUAN_PHU_VIET", own("Quan Phủ"), "hay_dinh_viec_cong_mon", "verified", "p.229", "dễ bị miệng tiếng, vướng thủ tục quan phủ (Quan Phủ ở Mệnh)"),
 ("THAI_TUE", own("Thái Tuế"), "thai_tue_menh_tu_kieu_xet_doan", "verified", "p.229", "tự kiêu, ít giao thiệp, lạnh lùng, thích xét đoán và lý luận (Thái Tuế ở Mệnh)"),
 ("TANG_HO", own("Tang Môn", "Bạch Hổ"), "tang_ho_menh_tai_ba_nhieu_tro_ngai", "verified", "p.229", "tài ba nhưng dễ gặp nhiều trở ngại, hao tổn (Tang Môn, Bạch Hổ ở Mệnh)"),
 ("THIEU_AM", own("Thiếu Âm"), "thieu_am_menh_kheo_leo_ngoai_mat", "verified", "p.229", "khéo léo bên ngoài (Thiếu Âm ở Mệnh)"),
 ("QUAN_PHU", own("Quan Phù"), "quan_phu_menh_tu_cao_ly_luan", "verified", "p.229", "tự cao, hay xét đoán và lý luận, liên quan việc pháp luật; tốt nếu gặp Xương Khúc và Thái Tuế (Quan Phù ở Mệnh)"),
 ("TUE_PHA", own("Tuế Phá"), "tue_pha_menh_hay_tranh_cai", "verified", "p.229", "hay tranh cãi (Tuế Phá ở Mệnh)"),
 ("DIEU_KHACH", own("Điếu Khách"), "dieu_khach_menh_noi_nhieu_khoe_khoang", "verified", "p.229", "nói nhiều, thích khoe khoang, ham vui chơi (Điếu Khách ở Mệnh)"),
 ("TRUC_TU_PHU", [anyof(*own("Trực Phù", "Tử Phù"))], "truc_tu_phu_menh_thich_phu_hoa", "verified", "p.229", "thích phụ họa, dễ làm rối công việc (Trực Phù hoặc Tử Phù ở Mệnh)"),
]
YR = {  # year branch -> phrases (KL pp.225-227)
 "Tý": "Đào Hồng đối mặt: phong nhã hào hoa, công danh đến chậm, chung thủy tận tâm",
 "Sửu": "Đào hoa giữa chợ, chim hồng bay bổng: tình duyên ngang trái, công danh sớm, có căn tu",
 "Dần": "Đào hoa đồng cung Thiên Không: công danh sớm, tình cảm mau tàn, khôn ngoan biết nắm cơ hội",
 "Mão": "Đào Hồng cặp đôi: thông minh lãng mạn, công danh bền bỉ, chỉ tội dễ đèo bòng",
 "Thìn": "Đào hoa cắm lọ: công danh đến trễ, mộng ước cao",
 "Tỵ": "Đào hoa gặp Thiên Không: duyên đến sớm nhưng dễ bẽ bàng, khôn ngoan biết nắm cơ hội",
 "Ngọ": "Đào Hồng đối mặt: công danh sớm, yêu sớm, về sau nhiều ngậm ngùi",
 "Mùi": "Đào Hồng lạc lối: công danh sớm, thông minh lãng mạn, giao thiệp rộng rãi",
 "Thân": "Đào hoa gặp Thiên Không: công danh đến chậm, tình đầu ngang trái, khôn ngoan biết nắm cơ hội",
 "Dậu": "Đào Hồng cặp đôi: tình đầu dang dở, công danh khó bền",
 "Tuất": "Hồng Loan đối mặt Thiên Không: hoa đào nở đẹp ban mai, ước vọng cao, công danh sớm, sự nghiệp lớn",
 "Hợi": "Đào hoa gặp Thiên Không: tình vừa chớm đã tàn mau, công danh sự nghiệp khó bền",
}
slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for rid, conds, claim, status, loc, vi in M:
    rules.append({"id": "TV_KL_AUX_" + rid, "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "kl_aux_menh",
        "description": f"Tử Vi Khảo Luận, phụ tinh ở Mệnh (paraphrased): {vi} [KL {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": "Mệnh"}] + list(conds)},
        "consequences": [{"kind": "finding", "claim": claim, "effect": "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_KHAO_LUAN"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims.setdefault(claim, "khuynh hướng " + vi.split(" (")[0] + (" (" + vi.split(" (", 1)[1] if " (" in vi else ""))
for i, (yb, txt) in enumerate(YR.items()):
    claim = f"dao_hong_khong_tuoi_{i:02d}_" + slug(yb).lower()
    rules.append({"id": f"TV_KL_DHK_{i:02d}_" + slug(yb), "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "kl_dao_hong_khong",
        "description": f"Tử Vi Khảo Luận: thế đứng Đào – Hồng – Thiên Không của người tuổi {yb} (paraphrased): {txt} [KL pp.225-227]; sách nói xác suất 'khá tốt', không phải chắc chắn",
        "conditions": {"fact": "chart.year_branch", "value": yb},
        "consequences": [{"kind": "finding", "claim": claim, "effect": "neutral", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 1, "sourceIds": ["SRC_KHAO_LUAN"], "reviewStatus": "verified", "version": "0.1.0", "subject": "chart"})
    claims[claim] = f"thế đứng Đào – Hồng – Thiên Không của người tuổi {yb}: {txt}"
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids))
json.dump({"sources": [], "rules": rules}, open(D / "pack_khao_luan_aux.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
