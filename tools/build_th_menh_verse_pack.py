"""Generates data/pack_thuc_hanh_menh_verse.json: couplets of the Nam Mệnh phú (Tử Vi Thực Hành pp.82-88) plus career/trait paragraphs of p.78
that the first verse pack did not encode. Paraphrased. Skipped on purpose: physical-appearance lines, harm/crime/early-death lines, and anything
whose stars are the unverified auxiliary placements (Long Phượng, Cái, Hình, Riêu, Khốc Hư, Quan Phúc, Ấn...)."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPS, TPH = "palace.own_stars", "palace.own_major_stars", "palace.rel.tp_stars", "palace.rel.tp_hoa"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
allof = lambda *x: {"all": list(x)}
nt = lambda x: {"not": x}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}
own = lambda *ss: [has(OWN, s) for s in ss]
tp = lambda *ss: [has(TPS, s) for s in ss]
GOOD, MV = ["miếu", "vượng", "đắc"], ["miếu", "vượng"]
TUMO = ("Thìn", "Tuất", "Sửu", "Mùi")
SAT = anyof(*tp("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh"))
CAT = anyof(*tp("Tử Vi", "Thiên Phủ", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật"))
ys = lambda *s: {"fact": "chart.year_stem", "operator": "in", "value": list(s)}
R = []
def add(pal, rid, conds, claim, status, page, phrase, effect="support", exceptions=None):
    R.append((pal, rid, conds, claim, effect, status, page, phrase, exceptions or []))
M = "Mệnh"
V = "Nam Mệnh phú"
add(M, "TU_PHU_TRONG_HAU", [anyof(*own("Tử Vi", "Thiên Phủ"))], "tu_phu_trong_hau", "verified", "p.82", "tính trọng hậu khác thường (Tử Vi hoặc Thiên Phủ ở Mệnh)")
add(M, "VU_THAM_THAM", own("Vũ Khúc", "Tham Lang"), "vu_tham_tham_loi", "verified", "p.82", "dễ nặng lòng tham lợi (Vũ Khúc đồng cung Tham Lang)", "limit")
add(M, "LIEM_THAM_TY_HOI", own("Liêm Trinh", "Tham Lang") + [br("Tỵ", "Hợi")], "liem_tham_tham_cua", "verified", "p.82", "tính tham, thấy của là muốn nắm (Liêm Tham ở Tỵ hoặc Hợi)", "limit")
add(M, "PHU_TUONG_CHAP_NHAT", [anyof(*[has(OWNM, s) for s in ("Thiên Phủ", "Thiên Tướng")]), br("Thìn", "Tuất")], "phu_tuong_chap_nhat_da_nghi", "verified", "p.82", "tính hay chấp nhất, đa nghi mọi bề (Thiên Phủ hoặc Thiên Tướng ở Thìn, Tuất)", "limit")
add(M, "PHA_LIEM_HON_THUA", own("Phá Quân", "Liêm Trinh"), "pha_liem_hon_thua_xoc_xech", "verified", "p.82", "tính xốc nổi, hay đo sức hơn thua với người (Phá Quân đồng cung Liêm Trinh)", "limit")
add(M, "XUONG_KHUC_THANH_NHAN", own("Văn Xương", "Văn Khúc"), "xuong_khuc_thanh_nhan", "verified", "p.82", "đời sống thanh nhàn (Xương, Khúc đồng cung ở Mệnh)")
add(M, "DONG_LUONG_THAT_THA", own("Thiên Đồng", "Thiên Lương"), "dong_luong_that_tha_dung_dan", "verified", "p.82", "thật thà, đứng đắn (Thiên Đồng đồng cung Thiên Lương)")
add(M, "KHOI_VIET_VAN_CHUONG", tp("Thiên Khôi", "Thiên Việt"), "khoi_viet_cach_van_chuong", "draft", "p.82", "có cách văn chương (Khôi, Việt hội Mệnh); 'cách' đọc là hội trong tam phương tứ chính")
add(M, "VIET_DA_KHOAN_THAI", own("Thiên Việt", "Đà La"), "viet_da_noi_khoan_thai", "draft", "p.83", "tiếng nói khoan thai (Việt, Đà); câu thơ chỉ nêu hai sao, đọc là đồng cung")
add(M, "PHU_MA_LUAN_BAN", own("Thiên Phủ", "Thiên Mã"), "phu_ma_luan_ban_thap_cao", "verified", "p.83", "giỏi luận bàn cao thấp (Thiên Phủ đồng cung Thiên Mã)")
add(M, "MA_TUYET", own("Thiên Mã", "Tuyệt"), "ma_tuyet_vo_phuong", "verified", "p.84", "bế tắc, khó định hướng, 'ngựa gặp đò' không lối (Thiên Mã đồng cung sao Tuyệt)", "limit")
add(M, "PHU_SAT_TAO_BAO", own("Thiên Phủ") + tp("Thất Sát"), "phu_sat_tao_bao_hon_nguoi", "draft", "p.84", "chí khôn, việc làm táo bạo muốn hơn người (Thiên Phủ gặp Thất Sát); 'phùng' đọc là hội")
add(M, "TRUONG_SINH_DE_VUONG", [anyof(*own("Trường Sinh", "Đế Vượng"))], "truong_sinh_de_vuong_thien_luong", "verified", "p.84", "bản tính thiện lương (Trường Sinh hoặc Đế Vượng ở Mệnh)")
add(M, "KK_TY_HOI", own("Địa Không", "Địa Kiếp") + [br("Tỵ", "Hợi")], "khong_kiep_ty_hoi_cong_danh_nhoanh_phat", "verified", "p.85", "công danh có thể phát nhanh nhưng cần thấy rõ cơ vi (Không, Kiếp đồng cung ở Tỵ hoặc Hợi)")
add(M, "HONG_LOAN_TY", own("Hồng Loan") + [br("Tý"), anyof(*tp("Văn Xương", "Văn Khúc"))], "hong_loan_ty_van_tinh_danh_som", "verified", "p.85", "tiếng tăm từ thuở nhỏ (Hồng Loan ở Tý, văn tinh hội chiếu)")
add(M, "DONG_DOI_THAY", [has(OWNM, "Thiên Đồng")], "thien_dong_tinh_khi_doi_thay", "verified", "p.85", "tính khí hay đổi thay, khó chiều (Thiên Đồng thủ Mệnh)", "limit")
add(M, "AM_KINH_NGO", own("Thái Âm", "Kình Dương") + [br("Ngọ")], "am_kinh_ngo_uy_hung_tuong_quan", "verified", "p.85", "uy hùng như tướng quân (Thái Âm đồng cung Kình Dương ở Ngọ)")
add(M, "NHAT_HOI_TAM_HOA", own("Thái Dương") + [br("Hợi")] + [has(TPH, h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")], "nhat_hoi_tam_hoa_ven_muoi", "verified", "p.85", "'mười phân vẹn mười' (Thái Dương ở Hợi được Khoa, Quyền, Lộc hội)")
add(M, "CO_MIEU_VUONG", [has(OWNM, "Thiên Cơ"), dig("Thiên Cơ", MV)], "co_mieu_vuong_da_tai_tam_tu", "verified", "p.85", "đa tài, lòng từ, tính cấp, dễ hiển vinh (Thiên Cơ miếu hoặc vượng ở Mệnh)")
add(M, "KHOI_VIET_TRUONG_HUYNH", [anyof(*own("Thiên Khôi", "Thiên Việt"))], "khoi_viet_dung_vi_tren", "draft", "p.85", "hay giữ ngôi trên trong gia đình, xã hội (Khôi hoặc Việt ở Mệnh); sách nói 'miếu địa' nhưng bảng độ sáng Khôi Việt không có")
add(M, "LIEM_HAM", [has(OWNM, "Liêm Trinh"), dig("Liêm Trinh", ["hãm"])], "liem_ham_uu_phien", "verified", "p.85", "nhiều ưu phiền (Liêm Trinh lạc hãm ở Mệnh)", "limit")
add(M, "XK_TAO_KHACH", [anyof(*own("Văn Xương", "Văn Khúc"))], "xuong_khuc_tao_khach_duoc_khen", "verified", "p.86", "là người tao nhã, được xa gần khen ngợi (Xương hoặc Khúc ở Mệnh)")
add(M, "KHOI_XUONG_LANH", own("Thiên Khôi", "Văn Xương"), "khoi_xuong_bac_lanh", "draft", "p.86", "người hiền lành tử tế (Khôi, Xương ở Mệnh); câu 'bậc lành' mơ hồ")
add(M, "TU_SAT_VUONG", own("Tử Vi", "Thất Sát") + [dig("Thất Sát", GOOD)], "tu_sat_vuong_dia_minh_huy", "verified", "p.86", "rạng rỡ (Tử Vi đồng cung Thất Sát ở thế sáng)")
add(M, "PHA_HAM_TUE", [has(OWNM, "Phá Quân"), dig("Phá Quân", ["hãm"]), has(OWN, "Thái Tuế")], "pha_ham_tue_noi_nhu_sam", "verified", "p.86", "ăn nói to tiếng, gay gắt như sấm (Phá Quân hãm đồng cung Thái Tuế)", "limit")
add(M, "NN_SUU_MUI_SAT", own("Thái Dương", "Thái Âm") + [br("Sửu", "Mùi"), anyof(*tp("Đà La", "Địa Không", "Địa Kiếp"))], "nhat_nguyet_suu_mui_sat_kho_hien_danh", "verified", "p.86", "khó hiển công danh (Nhật Nguyệt đồng cung ở Sửu/Mùi bị Đà, Không, Kiếp hội)", "limit")
add(M, "GIAP_KHONG_KIEP", [has("palace.rel.flank_stars", "Địa Không"), has("palace.rel.flank_stars", "Địa Kiếp")], "giap_khong_kiep_bat_loi", "verified", "p.87", "bất lợi, thế bị kẹp giữa Không và Kiếp ('giáp cung Không Kiếp')", "limit")
add(M, "NGUYET_HAM_LUONG", [has(OWNM, "Thái Âm"), dig("Thái Âm", ["hãm"])] + tp("Thiên Lương"), "nguyet_ham_luong_gian_truan", "draft", "p.87", "nhiều gian truân (Thái Âm hãm gặp Thiên Lương); 'gặp' đọc là hội", "limit")
add(M, "CO_CU_MAO", own("Thiên Cơ", "Cự Môn") + [br("Mão"), anyof(*tp("Văn Xương", "Văn Khúc")), anyof(*tp("Tả Phụ", "Hữu Bật"))], "co_cu_mao_cong_danh_rang_ro", "verified", "p.87", "công danh rạng rỡ (Cơ Cự ở Mão hợp Xương Khúc, Tả Hữu)")
add(M, "TU_NGO_TAM_CONG", own("Tử Vi") + [br("Ngọ"), nt(SAT), ys("Đinh", "Kỷ")], "tu_vi_ngo_dinh_ky_tam_cong", "verified", "p.88", "có thể đến chức cao 'tam công' (Tử Vi ở Ngọ không sát tinh, tuổi Đinh hoặc Kỷ)")
add(M, "TU_NGO_AT_GIAP", own("Tử Vi") + [br("Ngọ"), nt(SAT), ys("Ất", "Giáp")], "tu_vi_ngo_at_giap_kha_mong", "verified", "p.88", "khá mong được nhờ vả, thành đạt (Tử Vi ở Ngọ không sát tinh, tuổi Ất hoặc Giáp)")
add(M, "PHU_TUAT_HOA_CUC", own("Thiên Phủ") + [br("Tuất"), CAT, ys("Giáp", "Kỷ"), {"fact": "chart.cuc", "value": "Hỏa lục cục"}], "phu_tuat_giap_ky_hoa_cuc_ven_muoi", "verified", "p.88", "'vẹn vẻ mười phân' (Thiên Phủ ở Tuất hợp cát tinh, tuổi Giáp hoặc Kỷ, Hỏa lục cục)")
add(M, "TU_MO_UY_QUYEN", [br(*TUMO), anyof(*own("Tham Lang", "Vũ Khúc")), anyof(*own("Hỏa Tinh", "Linh Tinh"))], "tu_mo_hoa_linh_tham_vu_uy_quyen", "verified", "p.88", "có uy quyền (Tham hoặc Vũ ở Tứ mộ đồng cung Hỏa hoặc Linh), kỵ gặp Kình Dương", exceptions=[anyof(*tp("Kình Dương"))])
add(M, "LIEM_TUONG", own("Liêm Trinh", "Thiên Tướng"), "liem_tuong_anh_hung_vu_dung", "verified", "p.88", "dáng anh hùng, vũ dũng (Liêm Trinh đồng cung Thiên Tướng)")
add(M, "KK_TUE", [anyof(*own("Địa Không", "Địa Kiếp")), has(OWN, "Thái Tuế")], "khong_kiep_tue_suy_vi", "verified", "p.88", "dễ suy vi (Không hoặc Kiếp đồng cung Thái Tuế)", "limit")
add(M, "LOC_MA_TRIET", own("Lộc Tồn", "Thiên Mã") + [{"fact": "palace.triet", "value": True}], "loc_ma_gap_triet_vo_ich", "verified", "p.88", "Lộc Mã gặp Triệt thì mất ích lợi", "limit")
add(M, "XK_TY_HOI_LIEM", [anyof(*own("Văn Xương", "Văn Khúc")), br("Tỵ", "Hợi")] + tp("Liêm Trinh"), "xuong_khuc_ty_hoi_liem_hay", "draft", "p.88", "trở nên hay (Xương hoặc Khúc ở Tỵ/Hợi có Liêm Trinh); hai chữ cung trong thơ khó đọc")
add(M, "CU_THIN_TUAT_LOC", own("Cự Môn") + [br("Thìn", "Tuất"), has("palace.tu_hoa", "Hóa Lộc")], "cu_ham_hoa_loc_van_hay", "verified", "p.88", "Cự Môn hãm ở Thìn/Tuất nhưng hóa Lộc (tuổi Tân) thì vẫn khá")
# p.78 career/trait paragraphs
add(M, "KINH_THUONG_TU_PHU_KINH", [anyof(*own("Tử Vi", "Thiên Phủ")), has(OWN, "Kình Dương")], "tu_phu_kinh_thuong_gia_gioi", "verified", "p.78", "có thể thành thương gia giỏi (Tử Vi hoặc Thiên Phủ đắc địa đồng cung Kình Dương)")
add("Thiên Di", "THI_TU_MO_VU_LOC", own("Vũ Khúc") + [br(*TUMO), anyof(has(TPH, "Hóa Lộc"), has(OWN, "Lộc Tồn"), has(TPS, "Lộc Tồn"))], "di_tu_mo_vu_loc_buon_ban_hanh_phat", "verified", "p.78", "buôn bán hanh phát (cung Thiên Di ở Tứ mộ có Vũ Khúc hợp Lộc)")
add(M, "KY_NGHE_VU_PHA", [anyof(allof(*own("Vũ Khúc", "Phá Quân"), br("Hợi", "Tỵ")), allof(*own("Liêm Trinh", "Phá Quân"), br("Dậu", "Mão")))], "ky_nghe_tinh_kheo", "verified", "p.78", "khéo tay về kỹ nghệ (Vũ Phá đồng cung ở Hợi/Tỵ hoặc Liêm Phá đồng cung ở Dậu/Mão)")
add(M, "VAN_CHUONG_NHIEU_VAN_TINH", [{"fact": "palace.khi.cat_tp", "operator": "gte", "value": 3}] + [anyof(*tp("Văn Xương", "Văn Khúc"))], "van_chuong_nhieu_van_tinh_tho_phu", "draft", "p.78", "giỏi văn chương, thơ phú (nhiều văn tinh hội Mệnh); 'nhiều' quy ước từ ba cát tinh")
add(M, "TU_HANH_TU_THAM", own("Tử Vi", "Tham Lang") + [br("Mão", "Dậu"), anyof(*own("Địa Không", "Địa Kiếp"))], "cach_tu_hanh_tu_tham_khong_kiep", "verified", "p.78", "hợp nếp tu hành, thích lánh mùi tục lụy (Tử Tham đồng cung ở Mão/Dậu gặp Không hoặc Kiếp)")
add(M, "TU_HANH_VCD", [{"fact": "palace.has_no_major", "value": True}, {"fact": "palace.khi.sat_tp", "operator": "gte", "value": 3}], "cach_tu_hanh_vcd_nhieu_sat", "draft", "p.78", "thiên về tu hành, lánh tục lụy (Mệnh vô chính diệu gặp nhiều sát tinh); sách dặn xem thêm cung Phụ Mẫu, Phối, Tử")
add(M, "HOANG_DANG_THAM_DAO", own("Tham Lang", "Đào Hoa") + [anyof(*tp("Đại Hao", "Tiểu Hao"))], "cach_hoang_dang_tham_dao_hao", "draft", "p.78", "dễ đam mê tửu sắc, chuốc tai ương (Tham, Đào gặp song Hao); sách còn kể Diêu, Hỷ, Mộc Dục", "limit")

slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for pal, rid, conds, claim, effect, status, loc, vi, exc in R:
    rules.append({"id": f"TV_TH_MV_{slug(pal)}_{rid}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "th_menh_verse",
        "description": f"Tử Vi Thực Hành, phú/luận Mệnh (paraphrased), cung {pal}: {vi} [TH {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": claim, "effect": effect, "scope": "natal"}],
        "exceptions": exc, "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_THUC_HANH"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims.setdefault(claim, ("khuynh hướng " if effect == "support" else "hạn chế: ") + vi)
    if effect == "limit":
        claims.setdefault("limit:" + claim, "hạn chế: " + vi)
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_thuc_hanh_menh_verse.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
