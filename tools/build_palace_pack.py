"""Generates data/pack_thuc_hanh_palaces.json: aphorism-based rules from Tử Vi Thực Hành (verse sections, pp.83-105).
Verse is ambiguous, so only literal, computable, benign statements are encoded; paraphrased in Vietnamese, page-cited."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPM = "palace.own_stars", "palace.own_major_stars", "palace.tam_phuong_majors"
c = lambda f, v: {"fact": f, "operator": "contains", "value": v}
eq = lambda f, v: {"fact": f, "value": v}
name = lambda n: eq("palace.name", n)
RULES = [
 # id, palace, conditions(list for all), claim, effect, status, loc, vi
 ("MENH_TRIET_TUAN", [name("Mệnh"), {"any": [eq("palace.tuan", True), eq("palace.triet", True)]}], "thoi_tre_van_va_lo_toan", "verified", "p.83",
  "thời trẻ nhiều vất vả, lo toan (Tuần hoặc Triệt đóng ở Mệnh)"),
 ("MENH_LOC_TON", [name("Mệnh"), c(OWN, "Lộc Tồn")], "tai_loc_ve_sau", "verified", "p.83", "tài lộc thường khá lên về sau (Lộc Tồn tại Mệnh)"),
 ("MENH_CU_HOA_KY", [name("Mệnh"), c(OWNM, "Cự Môn"), c("palace.tu_hoa", "Hóa Kỵ")], "hay_lo_nghi_vien_vong", "verified", "p.83",
  "hay lo nghĩ viển vông (Cự Môn hóa Kỵ tại Mệnh)"),
 ("MENH_TAU_THU", [name("Mệnh"), c(OWN, "Tấu Thư")], "noi_ngot_de_thuyet_phuc", "verified", "p.83", "lời nói ngọt, dễ thuyết phục người (Tấu Thư tại Mệnh)"),
 ("MENH_THANH_LONG", [name("Mệnh"), c(OWN, "Thanh Long")], "co_bien_linh_hoat", "verified", "p.83", "biết cơ biến, ứng xử linh hoạt (Thanh Long tại Mệnh)"),
 ("MENH_THAI", [name("Mệnh"), c(OWN, "Thai")], "hoc_nhieu_kho_thanh_tuu", "verified", "p.85",
  "học nhiều nhưng khó đạt thành tựu tương xứng (sao Thai tại Mệnh)"),
 ("MENH_QUAN_PHU_THAI_TUE", [name("Mệnh"), c(OWN, "Quan Phủ"), c(OWN, "Thái Tuế")], "hay_dinh_viec_cong_mon", "verified", "p.86",
  "hay dính đến việc quan, thủ tục pháp lý (Quan Phủ và Thái Tuế đồng cung Mệnh)"),
 ("MENH_CU_THIN_TUAT", [name("Mệnh"), c(OWNM, "Cự Môn"), {"fact": "palace.branch", "operator": "in", "value": ["Thìn", "Tuất"]}],
  "de_vuong_thi_phi", "verified", "p.88", "dễ vướng thị phi, tranh cãi (Cự Môn thủ Mệnh ở Thìn hoặc Tuất)"),
 ("MENH_LUONG_KHUC_DAN_NGO", [name("Mệnh"), c(OWNM, "Thiên Lương"), c(OWN, "Văn Khúc"), {"fact": "palace.branch", "operator": "in", "value": ["Dần", "Ngọ"]}],
  "chuc_vi_cao_danh_rang_ro", "verified", "p.88", "đường chức vị cao, công danh rạng rỡ (Thiên Lương đồng cung Văn Khúc ở Dần hoặc Ngọ)"),
 ("MENH_TU_VI_NGO_PHU_TUAT", [name("Mệnh"), eq("palace.branch", "Ngọ"), c(OWNM, "Tử Vi"), c(TPM, "Thiên Phủ")],
  "quyen_quy_cong_khanh", "verified", "p.87", "địa vị cao, quyền quý (Tử Vi thủ Mệnh ở Ngọ, Thiên Phủ hội ở Tuất)"),
 ("MENH_TAM_HOA_HOI", [name("Mệnh")] + [c("palace.tam_phuong_tu_hoa", x) for x in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")],
  "tieng_tam_van_chuong", "verified", "p.87", "tiếng tăm về văn chương, học vấn (Tam Hóa hội chiếu Mệnh)"),
 ("TAI_VU_THAM", [name("Tài Bạch"), c(OWNM, "Vũ Khúc"), c(OWNM, "Tham Lang")], "giau_ben_sau_30_tuoi", "verified", "p.105",
  "tài lộc bền, thường vững vàng sau khoảng 30 tuổi (Vũ Khúc đồng cung Tham Lang tại Tài Bạch)"),
 ("TAI_CU_MON", [name("Tài Bạch"), c(OWNM, "Cự Môn")], "tay_trang_lap_nghiep", "verified", "p.105",
  "có xu hướng tay trắng làm nên (Cự Môn tại Tài Bạch)"),
 ("DI_KHONG_KIEP", [name("Thiên Di"), {"any": [c(OWN, "Địa Không"), c(OWN, "Địa Kiếp")]}], "danh_den_muon", "verified", "p.86",
  "danh vọng đến muộn, khi tuổi đã cao (Địa Không hoặc Địa Kiếp tại Thiên Di)"),
 ("TU_QUYEN_LOC", [name("Tử Tức"), {"any": [c("palace.tu_hoa", "Hóa Quyền"), c("palace.tu_hoa", "Hóa Lộc")]}], "con_cai_hien_vinh", "draft", "p.103",
  "con cái có xu hướng thành đạt (Quyền hoặc Lộc tại Tử Tức); 'Quyền Lộc' đọc là một trong hai: giả định của hệ thống"),
]
rules, claims = [], {}
for rid, conds, claim, status, loc, vi in RULES:
    rules.append({"id": "TV_TH_VERSE_" + rid, "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "palace_aphorism",
        "description": f"Verse aphorism of Tử Vi Thực Hành, paraphrased: {vi} [TH {loc}]",
        "conditions": {"all": conds}, "consequences": [{"kind": "finding", "claim": claim, "effect": "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_THUC_HANH"], "reviewStatus": status,
        "version": "0.1.0", "subject": "palace"})
    claims[claim] = "khuynh hướng " + vi.split(" (")[0] + " (" + vi.split(" (", 1)[1] if " (" in vi else vi
json.dump({"sources": [], "rules": rules}, open(D / "pack_thuc_hanh_palaces.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8")); cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
