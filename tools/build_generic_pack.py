"""Generates data/pack_thuc_hanh_combos.json: the 'star in good/bad position meets auxiliary stars / Tuần-Triệt' readings of
Tử Vi Thực Hành pp.30-49, paraphrased. Auxiliary sets are the ones each passage names; 'hội/gặp' is operationalised as 'in the tam phương
of Mệnh' (own palace or tam phương) — stated in each description."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
GOOD = ["miếu", "vượng", "đắc"]
TPS, TPH, OWNM = "palace.tam_phuong_stars", "palace.tam_phuong_tu_hoa", "palace.own_major_stars"
c = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *cs: {"any": list(cs)}
stars = lambda *ss: [c(TPS, s) for s in ss]
hoa = lambda *hs: [c(TPH, h) for h in hs]
TAM_HOA = hoa("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")
XK_KV_TH = stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA
SAT6 = stars("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp")
TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}

# (star, id, dignity levels or None, extra condition, claim, status, page, Vietnamese phrase)
T = [
 ("Tử Vi", "CAT", GOOD, anyof(*(stars("Thiên Khôi", "Thiên Việt", "Văn Xương", "Văn Khúc", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "tu_vi_cat_uy_quyen", "verified", "p.30", "uy quyền hiển hách khi có các trung tinh (Khôi Việt, Xương Khúc, Tả Hữu, Tam Hóa) hội chiếu"),
 ("Tử Vi", "KIEP_KHONG", None, anyof(*stars("Địa Không", "Địa Kiếp")), "tu_vi_gap_khong_kiep", "verified", "p.30", "khó phát huy được khả năng, đời nhiều trắc trở lao tâm (Tử Vi gặp Địa Không, Địa Kiếp)"),
 ("Tử Vi", "TUAN_TRIET", None, TT, "tu_vi_tuan_triet_xa_que", "verified", "p.30", "dễ phải xa quê sớm (Tử Vi đóng ở Mệnh gặp Tuần hoặc Triệt)"),
 ("Tử Vi", "THAT_SAT", None, c(OWNM, "Thất Sát"), "tu_vi_dong_that_sat", "verified", "p.30", "thế mạnh thêm, quyền lực rõ nét (Tử Vi đồng cung Thất Sát)"),
 ("Tử Vi", "THAM_LANG", None, {"all": [c(OWNM, "Tham Lang"), {"fact": "palace.branch", "operator": "in", "value": ["Tý", "Hợi", "Mão", "Dậu"]}]}, "tu_vi_tham_bi_quan", "verified", "p.30", "dễ bi quan, yếm thế, thiên về đời sống tu hành (Tử Vi Tham Lang ở Tý, Hợi, Mão hoặc Dậu)"),
 ("Thiên Cơ", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "co_cat_phu_quy_uy_danh", "verified", "p.31", "phú quý song toàn, uy danh khi có các trung tinh (Xương Khúc, Khôi Việt, Tả Hữu, Tam Hóa) hội chiếu"),
 ("Thiên Cơ", "TUAN_TRIET", GOOD, TT, "co_tot_tuan_triet_ly_huong", "verified", "p.31", "phải xa quê bôn ba, sinh kế khó khăn (Thiên Cơ đắc địa gặp Tuần hoặc Triệt)"),
 ("Thiên Cơ", "HAM_TUAN_TRIET", ["hãm"], TT, "co_ham_tuan_triet_do_phan", "verified", "p.31", "bớt được phần nào bất lợi (Thiên Cơ hãm gặp Tuần hoặc Triệt)"),
 ("Thái Dương", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "duong_cat_tai_quan_vinh_hien", "verified", "p.33", "tài và quan vinh hiển (Thái Dương đắc địa gặp Xương Khúc, Tả Hữu, Tam Hóa, Khôi Việt)"),
 ("Thái Dương", "TUAN_TRIET", GOOD, TT, "duong_tot_tuan_triet_ly_huong", "verified", "p.33", "không toại ý, thường phải xa quê lập nghiệp (Thái Dương đắc địa gặp Tuần hoặc Triệt)"),
 ("Thái Dương", "SAT", GOOD, anyof(*stars("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp")), "duong_tot_gap_sat_tac_tuong", "verified", "p.33", "công danh tiền tài lúc có lúc không (Thái Dương đắc địa gặp Kình, Đà, Không, Kiếp)"),
 ("Thái Dương", "HAM_CAT", ["hãm"], anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "duong_ham_gap_cat_tot_tai_danh", "verified", "p.33", "biến ra tốt đẹp về tài danh (Thái Dương hãm gặp Tam Hóa, Xương Khúc, Tả Hữu, Khôi Việt)"),
 ("Thái Âm", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "am_cat_phu_quy_tot_do", "verified", "p.40", "phú quý đến mức cao (Thái Âm đắc địa gặp Xương Khúc, Khôi Việt, Tả Hữu, Tam Hóa)"),
 ("Thái Âm", "TUAN_TRIET", GOOD, TT, "am_tot_tuan_triet_lao_dao", "verified", "p.40", "lao đao, vất vả, dễ phải xa quê (Thái Âm đắc địa gặp Tuần hoặc Triệt)"),
 ("Thái Âm", "HAM_CAT", ["hãm"], anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA + [TT])), "am_ham_gap_cat_hoac_tuan_triet_tot", "verified", "p.40", "trở nên tốt và thọ hơn (Thái Âm hãm gặp sao tốt hoặc Tuần, Triệt)"),
 ("Vũ Khúc", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "vu_cat_phu_quy_hien_vinh", "verified", "p.34", "phú quý hiển vinh trọn đời nhưng thường phải ngoài 30 tuổi mới thành đạt (Vũ Khúc đắc địa gặp Tam Hóa, Tả Hữu, Khôi Việt, Xương Khúc)"),
 ("Vũ Khúc", "KIEP_SAT", GOOD, anyof(*stars("Địa Kiếp", "Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh")), "vu_tot_gap_kiep_sat_tien_phu_hau_ban", "draft", "p.34", "tiền phú hậu bần, của cải lúc nhiều lúc sút (Vũ Khúc đắc địa gặp Kiếp, Sát); 'Sát' đọc là Kình Đà Hỏa Linh: giả định của hệ thống"),
 ("Thiên Đồng", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "dong_cat_phu_quy_tot_buc", "verified", "p.36", "phú quý rất cao (Thiên Đồng gặp nhiều cát tinh hội)"),
 ("Thiên Đồng", "SAT", GOOD, anyof(*SAT6), "dong_gap_sat_lao_tam_kho_tu", "draft", "p.36", "no ấm nhưng cả đời lao tâm khổ tứ (Thiên Đồng gặp Kình, Đà, Hỏa, Linh, Không, Kiếp); sách còn kể Hình, Kỵ: chưa dựng được"),
 ("Liêm Trinh", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Tả".replace("Tả Tả", "Tả Phụ"), "Hữu Bật") + TAM_HOA)), "liem_cat_uy_danh_phu_quy", "verified", "p.37", "uy danh lừng lẫy, phú quý vẹn toàn (Liêm Trinh gặp Tam Hóa, Tả Hữu, Xương Khúc, Khôi Việt)"),
 ("Liêm Trinh", "HUNG", GOOD, anyof(*SAT6), "liem_gap_hung_tinh_tru_tr", "draft", "p.37", "công danh trắc trở, tiền của tụ rồi tán (Liêm Trinh gặp hung tinh ám); 'hung tinh' đọc là Kình Đà Hỏa Linh Không Kiếp: giả định"),
 ("Thiên Phủ", "CAT", ["miếu", "vượng", "đắc", "bình"], anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "phu_cat_phuc_loc_tang", "draft", "p.39", "phúc lộc càng tăng khi có cát tinh hội (Thiên Phủ); sách không gắn với độ sáng cụ thể nên chỉ xét khi độ sáng đã được nêu"),
 ("Thiên Phủ", "TT_KK", None, anyof(TT, *stars("Địa Không", "Địa Kiếp")), "phu_gap_tuan_triet_khong_kiep", "draft", "p.39", "tính hơi cao ngạo, phóng đãng, hay thích viễn vông (Thiên Phủ gặp Tuần, Triệt, Không, Kiếp)"),
 ("Tham Lang", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "tham_cat_toan_my", "verified", "p.42", "mọi bề thuận lợi, trọn vẹn hơn (Tham Lang đắc địa gặp nhiều cát tinh)"),
 ("Cự Môn", "VAN_TAI", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Thái Tuế") + hoa("Hóa Khoa"))), "cu_van_tai_loi_lac", "verified", "p.43", "văn tài lỗi lạc, ăn nói hùng hồn, hợp ngành chính trị, ngoại giao (Cự Môn gặp Xương Khúc, Khôi Việt, Khoa, Tuế)"),
 ("Thiên Tướng", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "tuong_cat_hoan_my", "verified", "p.44", "mọi bề hoàn mỹ (Thiên Tướng gặp nhiều cát tinh)"),
 ("Thiên Tướng", "TUAN_TRIET", GOOD, TT, "tuong_tuan_triet_cong_danh_tr", "verified", "p.44", "công danh trắc trở, tiền bạc eo hẹp (Thiên Tướng gặp Tuần hoặc Triệt)"),
 ("Thiên Lương", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "luong_cat_phu_quy_uy_quyen", "verified", "p.46", "phú quý và có uy quyền (Thiên Lương gặp Xương Khúc, Khôi Việt, Tả Hữu, Tam Hóa)"),
 ("Thiên Lương", "TUAN_TRIET", GOOD, TT, "luong_tuan_triet_lao_kho", "verified", "p.46", "cuộc đời lao khó, nhiều trở ngại (Thiên Lương gặp Tuần hoặc Triệt)"),
 ("Thất Sát", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật") + TAM_HOA)), "sat_cat_quyen_lon", "verified", "p.47", "quyền uy lớn, thịnh đạt (Thất Sát gặp nhiều cát tinh hội)"),
 ("Phá Quân", "CAT", GOOD, anyof(*(stars("Văn Xương", "Văn Khúc", "Tả Phụ", "Hữu Bật", "Thiên Tướng") + TAM_HOA)), "pha_cat_cong_danh_thang_buoc", "verified", "p.49", "công danh thẳng bước, uy quyền hiển hách (Phá Quân đắc địa gặp Tam Hóa, Tả Hữu, Xương Khúc, Tướng Ấn)"),
]
rules, claims = [], {}
for star, tag, lv, extra, claim, status, loc, vi in T:
    conds = [{"fact": "palace.name", "value": "Mệnh"}, c(OWNM, star)]
    if lv: conds.append(dig(star, lv))
    conds.append(extra)
    rules.append({"id": f"TV_TH_COMBO_{star.upper().replace(' ', '_')}_{tag}".replace("Ử", "U").replace("Ơ", "O").replace("Ư", "U").replace("Â", "A").replace("Ê", "E").replace("Ô", "O").replace("Ă", "A").replace("Đ", "D").replace("Ạ", "A").replace("Ể","E").replace("Ấ","A").replace("Ớ","O").replace("Ủ","U").replace("Ợ","O").replace("Ị","I").replace("Ỉ","I"),
        "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "star_combination",
        "description": f"Tử Vi Thực Hành: {vi} [TH {loc}]. 'Hội/gặp' = trong tam phương của Mệnh (our reading).",
        "conditions": {"all": conds}, "consequences": [{"kind": "finding", "claim": claim, "effect": "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 4, "sourceIds": ["SRC_THUC_HANH"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims[claim] = "khuynh hướng " + vi.split(" (")[0] + (" (" + vi.split(" (", 1)[1] if " (" in vi else "")
json.dump({"sources": [], "rules": rules}, open(D / "pack_thuc_hanh_combos.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8")); cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules), len({r["id"] for r in rules}))
