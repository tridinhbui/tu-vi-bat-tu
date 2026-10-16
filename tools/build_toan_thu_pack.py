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
