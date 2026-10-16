"""Generates data/pack_khao_luan_phu.json from Tử Vi Khảo Luận 'phú đoán' explanations (pp.49-63), paraphrased.
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

# id, extra conditions (Mệnh implied), claim, status, page, Vietnamese phrase
R = [
 ("TU_VI_NGO_KHONG_SAT", [br("Ngọ"), *oM("Tử Vi"), nt(anyof(*SAT))], "tu_vi_ngo_chuc_lon", "draft", "p.49", "đường chức vị cao (Tử Vi ở Ngọ, không gặp Kình, Đà, Không, Kiếp); 'không gặp' đọc là không có trong tam phương"),
 ("TU_VI_KHONG_TA_HUU", [*oM("Tử Vi"), nt(anyof(*tS("Tả Phụ", "Hữu Bật")))], "tu_vi_thieu_phu_tro", "verified", "p.49", "thiếu người phò trợ, thế cô độc dù có địa vị (Tử Vi không có Tả Hữu hội họp)"),
 ("TU_VI_TA_HUU", [*oM("Tử Vi"), *oS("Tả Phụ", "Hữu Bật")], "tu_vi_ta_huu_uy_quyen", "verified", "p.49", "có uy quyền, hiệu lệnh được nhiều người nghe (Tử Vi đồng cung Tả Phụ, Hữu Bật)"),
 ("TU_PHU_DAN_THAN", [br("Dần", "Thân"), *oM("Tử Vi", "Thiên Phủ")], "tu_phu_dan_than_thuan_loi", "verified", "p.49", "đời sống thuận lợi, dễ chịu (Tử Vi đồng cung Thiên Phủ ở Dần hoặc Thân)"),
 ("TU_VI_NGO_TAM_HOA", [br("Ngọ"), *oM("Tử Vi"), *TAM3], "tu_vi_ngo_tam_hoa_cach_tot", "verified", "p.49", "thế rất tốt, đường hiển đạt rõ (Tử Vi ở Ngọ được Khoa, Quyền, Lộc hội chiếu)"),
 ("TU_VI_LOC_TON_TA_HUU", [*oM("Tử Vi"), *oS("Lộc Tồn"), *tS("Tả Phụ", "Hữu Bật")], "tu_vi_loc_ton_quy_hien", "verified", "p.49", "rất quý hiển (Tử Vi đồng cung Lộc Tồn, Tả Hữu hội chiếu)"),
 ("TU_VI_XUONG_KHUC", [*oM("Tử Vi"), *oS("Văn Xương", "Văn Khúc")], "tu_vi_xuong_khuc_giau_sang", "verified", "p.49", "giàu sang nổi bật (Tử Vi đồng cung Văn Xương, Văn Khúc)"),
 ("TU_SAT_TY_HOI", [br("Tỵ", "Hợi"), *oM("Tử Vi", "Thất Sát")], "tu_sat_giau_sang", "verified", "p.50", "vừa giàu vừa sang (Tử Vi đồng cung Thất Sát ở Tỵ hoặc Hợi)"),
 ("TU_THAM_MAO_DAU_KHONG_KIEP", [br("Mão", "Dậu"), *oM("Tử Vi", "Tham Lang"), anyof(*oS("Địa Không", "Địa Kiếp"))], "tu_tham_thoat_tuc", "verified", "p.50", "thiên về đời sống tu hành, thoát tục (Tử Vi Tham Lang ở Mão hoặc Dậu đồng cung Không hoặc Kiếp)"),
 ("TU_PHU_PHUC_LOC", [*oM("Tử Vi", "Thiên Phủ")], "tu_phu_phuc_loc", "verified", "p.55", "hưởng nhiều phúc lộc (Tử Vi đồng cung Thiên Phủ)"),
 ("TU_PHU_TUAN_TRIET", [*oM("Tử Vi", "Thiên Phủ"), anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})], "tu_phu_phuc_loc", "verified", "p.55", "phúc lộc kém đi (Tử Phủ bị Tuần hoặc Triệt án ngữ); đây là điều kiện hạn chế của chính nhận định trên"),
 ("PHU_XUONG_KHUC_TA_HUU", [*oM("Thiên Phủ"), anyof(*tS("Văn Xương", "Văn Khúc")), anyof(*tS("Tả Phụ", "Hữu Bật"))], "phu_hoc_van_danh_vong", "draft", "p.55", "học vấn đỗ đạt cao, danh vọng lớn (Thiên Phủ được Xương Khúc, Tả Hữu hợp chiếu); sách liệt kê cả bốn, hệ thống đọc là ít nhất một sao mỗi cặp"),
 ("DUONG_NGO", [br("Ngọ"), *oM("Thái Dương")], "duong_ngo_danh_vong", "verified", "p.52", "danh vọng và tài lộc nổi bật, như mặt trời giữa trưa (Thái Dương ở Ngọ)"),
 ("VCD_NHAT_NGUYET", [{"fact": "palace.has_no_major", "value": True}, *[has(TPM, s) for s in ("Thái Dương", "Thái Âm")]], "vcd_nhat_nguyet_thong_minh", "verified", "p.53", "thông minh, học một biết mười (Mệnh vô chính diệu được Nhật Nguyệt chiếu)"),
 ("DUONG_TY_CU_HOI", [br("Tỵ"), *oM("Thái Dương"), has(TPM, "Cự Môn")], "duong_ty_loc_lau_dai", "verified", "p.53", "lộc kéo dài (Thái Dương ở Tỵ, Cự Môn ở Hợi xung chiếu)"),
 ("DUONG_HOI_CU_TY", [br("Hợi"), *oM("Thái Dương"), has(TPM, "Cự Môn")], "duong_hoi_cong_danh_trac_tro", "verified", "p.53", "công danh nhiều trắc trở (Thái Dương ở Hợi, Cự Môn ở Tỵ xung chiếu)"),
 ("VU_DAC_DIA", [*oM("Vũ Khúc"), dig("Vũ Khúc", GOOD)], "vu_dac_dia_uy_quyen", "verified", "p.54", "có uy quyền, nổi danh (Vũ Khúc đắc địa)"),
 ("VU_PHA_XUONG_KHUC", [*oM("Vũ Khúc", "Phá Quân"), *oS("Văn Xương", "Văn Khúc")], "vu_pha_ky_nghe_may_moc", "verified", "p.54", "giỏi kỹ nghệ, máy móc (Vũ Khúc Phá Quân đồng cung Xương Khúc)"),
 ("VU_LOC_MA", [*oM("Vũ Khúc"), *tS("Lộc Tồn", "Thiên Mã")], "vu_loc_ma_lap_nghiep_xa", "verified", "p.54", "lập nghiệp nơi xa, giàu sang lớn (Vũ Khúc được Lộc, Mã hợp chiếu)"),
 ("VU_VAN_KHUC", [*oM("Vũ Khúc"), *oS("Văn Khúc")], "vu_van_khuc_hoc_rong", "verified", "p.54", "học rộng, tài cao (Vũ Khúc đồng cung Văn Khúc)"),
 ("VU_KHOI_VIET", [*oM("Vũ Khúc"), *oS("Thiên Khôi", "Thiên Việt")], "vu_khoi_viet_quan_tai_chinh", "verified", "p.54", "hợp làm quan lớn về tài chính (Vũ Khúc đồng cung Khôi, Việt)"),
 ("THAM_VU_SUU_MUI", [br("Sửu", "Mùi"), *oM("Tham Lang", "Vũ Khúc")], "tham_vu_truoc_ngheo_sau_giau", "verified", "p.54", "trước vất vả, sau khá giả (Tham Lang đồng cung Vũ Khúc ở Sửu hoặc Mùi)"),
 ("DONG_LUONG_DAN_THAN", [br("Dần", "Thân"), *oM("Thiên Đồng", "Thiên Lương")], "dong_luong_tot_giau_sang", "verified", "p.55", "rất tốt, vừa giàu vừa sang (Đồng Lương đồng cung ở Dần hoặc Thân)"),
 ("AM_HOI_SANG", [br("Hợi"), *oM("Thái Âm"), dig("Thái Âm", ["miếu", "vượng"])], "am_hoi_phu_quy_chuc_cao", "verified", "p.56", "phú quý, chức vị cao (Thái Âm sáng đẹp ở Hợi)"),
 ("AM_KINH_DA", [*oM("Thái Âm"), anyof(*oS("Kình Dương", "Đà La"))], "am_kinh_da_tinh_cam_hao_tai", "verified", "p.56", "dễ trục trặc trong tình cảm đôi lứa và hao tài (Thái Âm đồng cung Kình hoặc Đà)"),
 ("THAM_HOA_LINH_TU_MO", [br("Thìn", "Tuất", "Sửu", "Mùi"), *oM("Tham Lang"), anyof(*oS("Hỏa Tinh", "Linh Tinh"))], "tham_hoa_linh_tu_mo_quyen_the", "verified", "p.56", "giàu sang, quyền thế (Tham Lang đồng cung Hỏa hoặc Linh ở Tứ Mộ)"),
 ("CU_TY_NGO_TAM_HOA", [br("Tý", "Ngọ"), *oM("Cự Môn"), *TAM3], "cu_ngoc_trong_da", "verified", "p.58", "như ngọc trong đá, phú quý khi được Khoa, Quyền, Lộc hội chiếu (Cự Môn ở Tý hoặc Ngọ)"),
 ("CU_NHAT_DAN_THAN", [br("Dần", "Thân"), *oM("Cự Môn", "Thái Dương")], "cu_nhat_danh_gia", "verified", "p.58", "danh giá, thế sáng như mặt trời (Cự Môn đồng cung Thái Dương ở Dần hoặc Thân)"),
 ("CU_CO_MAO_DAU", [br("Mão", "Dậu"), *oM("Cự Môn", "Thiên Cơ")], "cu_co_quan_lon", "verified", "p.58", "có đường làm quan lớn (Cự Môn Thiên Cơ ở Mão hoặc Dậu)"),
 ("TUONG_TA_HUU", [*oM("Thiên Tướng"), *oS("Tả Phụ", "Hữu Bật")], "tuong_ta_huu_phu_quy", "verified", "p.58", "phú quý, giàu sang (Thiên Tướng đồng cung Tả Phụ, Hữu Bật)"),
 ("TU_TUONG_THIN_TUAT", [br("Thìn", "Tuất"), *oM("Tử Vi", "Thiên Tướng")], "tu_tuong_co_cong_danh", "verified", "p.59", "có công danh (Tử Vi Thiên Tướng ở Thìn hoặc Tuất)"),
 ("LUONG_MA", [*oM("Thiên Lương"), *oS("Thiên Mã")], "luong_ma_hay_di_chuyen", "verified", "p.59", "thích đi đây đó, hay di chuyển (Thiên Lương đồng cung Thiên Mã)"),
 ("SAT_TU_MENH", [br("Dần", "Thân", "Tý", "Ngọ"), *oM("Thất Sát")], "sat_tu_tinh_phu_quy", "verified", "p.60", "giàu sang, phú quý (Thất Sát tọa thủ ở Dần, Thân, Tý hoặc Ngọ)"),
 ("XUONG_KHUC_MENH", [*oS("Văn Xương", "Văn Khúc")], "xuong_khuc_hoc_rong_tai_cao", "verified", "p.61", "học rộng, tài cao (Văn Xương, Văn Khúc ở Mệnh)"),
 ("XUONG_KHUC_LOC_TON", [*oS("Văn Xương", "Văn Khúc", "Lộc Tồn")], "xuong_khuc_loc_ton_tai_la", "verified", "p.61", "có tài năng nổi bật (Xương Khúc đồng cung Lộc Tồn)"),
 ("KHOI_VIET_MENH", [*oS("Thiên Khôi", "Thiên Việt")], "khoi_viet_van_chuong", "verified", "p.62", "giỏi văn chương, thi cử thuận lợi (Khôi, Việt ở Mệnh)"),
 ("LOC_TON_MENH", [*oS("Lộc Tồn")], "loc_ton_an_ngon_mac_dep", "verified", "p.62", "đời sống đầy đủ, ăn ngon mặc đẹp (Lộc Tồn ở Mệnh)"),
 ("LOC_TON_TY_NGO", [br("Tý", "Ngọ"), *oS("Lộc Tồn")], "loc_ton_ty_ngo_tien_bac_nhieu", "verified", "p.62", "tiền bạc dồi dào (Lộc Tồn ở Mệnh tại Tý hoặc Ngọ)"),
 ("LOC_TON_HOA_LOC", [*oS("Lộc Tồn"), has("palace.tu_hoa", "Hóa Lộc")], "loc_ton_hoa_loc_doc_doan", "verified", "p.62", "tính độc đoán, thích nắm quyền (Lộc Tồn đồng cung Hóa Lộc)"),
 ("TA_HUU_MENH", [*oS("Tả Phụ", "Hữu Bật")], "ta_huu_menh_giau_sang", "verified", "p.63", "đời sống sung túc, nhiều người giúp (Tả Phụ, Hữu Bật đồng cung ở Mệnh)"),
]
rules, claims = [], {}
for rid, extra, claim, status, loc, vi in R:
    rules.append({"id": "TV_KL_PHU_" + rid, "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "kl_phu_doan",
        "description": f"Tử Vi Khảo Luận, phú đoán (paraphrased): {vi} [KL {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": "Mệnh"}] + extra},
        "consequences": [{"kind": "finding", "claim": claim, "effect": "limit" if rid == "TU_PHU_TUAN_TRIET" else "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 4, "sourceIds": ["SRC_KHAO_LUAN"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    if rid == "TU_PHU_TUAN_TRIET":
        claims["limit:" + claim] = "phúc lộc kém đi vì Tuần hoặc Triệt án ngữ (Tử Phủ đồng cung Mệnh)"
    elif claim not in claims:
        claims[claim] = "khuynh hướng " + vi.split(" (")[0] + (" (" + vi.split(" (", 1)[1] if " (" in vi else "")
json.dump({"sources": [], "rules": rules}, open(D / "pack_khao_luan_phu.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8")); cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules), len({r['id'] for r in rules}))
