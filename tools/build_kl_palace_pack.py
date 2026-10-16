"""Generates data/pack_khao_luan_cung.json from Tử Vi Khảo Luận pp.214-220 (summary of what each of the 12 palaces needs / avoids).
Paraphrased. Policy: stars named for a palace are looked up in that palace (own); 'hội/chiếu' in its tam phương; star groups use the
group facts derived by the group rules (multi-hop). Rules whose wording is loose ('gặp', 'lũ', 'độc thủ') are draft."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPS, TPH = "palace.own_stars", "palace.own_major_stars", "palace.tam_phuong_stars", "palace.tam_phuong_tu_hoa"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
allof = lambda *x: {"all": list(x)}
nt = lambda x: {"not": x}
grp = lambda g: {"fact": f"derived.group.{g}", "value": True}
oM = lambda *ss: [has(OWNM, s) for s in ss]
oAny = lambda *ss: anyof(*[has(OWNM, s) for s in ss])
oSAny = lambda *ss: anyof(*[has(OWN, s) for s in ss])
MAJ = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân"]


def solo(star, *allowed):
    """star is the only chính tinh of the palace, besides any named companions ('độc thủ')."""
    others = [m for m in MAJ if m != star and m not in allowed]
    return allof(has(OWNM, star), nt(anyof(*[has(OWNM, m) for m in others])))


TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})
SATS = ["Kình Dương", "Đà La", "Địa Không", "Địa Kiếp"]
# (palace, id, conditions list, claim, status, page, phrase)
R = [
 ("Tài Bạch", "LOC_TON", [has(OWN, "Lộc Tồn")], "tai_loc_ton_khong_so_ngheo", "verified", "p.216", "không lo thiếu thốn (Lộc Tồn tại Tài Bạch)"),
 ("Tài Bạch", "SONG_LOC", [has(OWN, "Lộc Tồn"), has(TPH, "Hóa Lộc")], "tai_song_loc_giau", "verified", "p.216", "tài lộc dồi dào, nhất là Song Lộc (Lộc Tồn thủ có Hóa Lộc chiếu)"),
 ("Tài Bạch", "LOC_MA", [has(OWN, "Lộc Tồn"), has(TPS, "Thiên Mã")], "tai_loc_ma_giao_tri", "verified", "p.216", "giàu sang có ngày (Lộc Mã giao trì: Lộc Tồn thủ, Thiên Mã chiếu)"),
 ("Tài Bạch", "KQL_MA", [has(TPH, "Hóa Khoa"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc"), has(TPS, "Thiên Mã")], "tai_khoa_quyen_loc_ma", "verified", "p.216", "giàu sang rõ nét (Khoa, Quyền, Lộc hội, có Thiên Mã chiếu)"),
 ("Tài Bạch", "KHOA_LT_HL", [has(OWN, "Lộc Tồn"), has(TPH, "Hóa Khoa"), has(TPH, "Hóa Lộc")], "tai_dai_phu_thien_an", "verified", "p.216", "cách đại phú, của trời cho (Hóa Khoa, Lộc Tồn, Hóa Lộc cùng hội)"),
 ("Tài Bạch", "THAN_CU_TAI", [{"fact": "palace.is_than", "value": True}, has(OWN, "Lộc Tồn")], "than_cu_tai_cang_giau", "verified", "p.216", "càng đúng cách càng giàu sang (Thân cư Tài, có Lộc Tồn)"),
 ("Tài Bạch", "KHONG_KIEP", [anyof(has(TPS, "Địa Không"), has(TPS, "Địa Kiếp"), allof(has(TPS, "Liêm Trinh"), has(TPS, "Tham Lang")))], "tai_khong_kiep_ngheo", "draft", "p.216", "khó tích lũy, tài lộc hao hụt (Không, Kiếp hoặc Liêm Tham ghé vào Tài Bạch); 'ghé vào' đọc là hội trong tam phương"),
 ("Quan Lộc", "TU_VI_DAC_DIA", [has(OWNM, "Tử Vi"), {"fact": "palace.dignity.Tử Vi", "operator": "in", "value": ["miếu", "vượng", "đắc"]}], "quan_tu_vi_danh_vong_cao", "draft", "p.216", "danh vọng, địa vị cao (Tử Vi đắc địa tại Quan Lộc); sách còn đòi có Tả Hữu, Xương Khúc, Khôi Việt, Khoa Quyền Lộc đi kèm: chưa kiểm"),
 ("Quan Lộc", "LIEM_TUONG_SAT", [has("palace.tam_phuong_majors", s) for s in ("Liêm Trinh", "Thiên Tướng", "Thất Sát")], "quan_liem_tuong_sat", "draft", "p.216", "đường danh vọng thuận (bộ ba Liêm Trinh, Thiên Tướng, Thất Sát hội ở Quan Lộc); sách yêu cầu đắc địa: chưa kiểm"),
 ("Quan Lộc", "VU_THAM_PHA", [has("palace.tam_phuong_majors", s) for s in ("Vũ Khúc", "Tham Lang", "Phá Quân")], "quan_vu_tham_pha", "draft", "p.216", "đường danh vọng thuận (bộ ba Vũ Khúc, Tham Lang, Phá Quân hội ở Quan Lộc)"),
 ("Quan Lộc", "SAT_TT", [TT, anyof(*[has(TPS, s) for s in SATS + ["Hỏa Tinh", "Linh Tinh"]])], "quan_do_vo_co_do", "draft", "p.216", "công sức xây dựng dễ đổ vỡ (Quan Lộc gặp sát tinh lại bị Tuần hoặc Triệt)"),
 ("Phúc Đức", "TU_PHU_VU_TUONG", [grp("tu_phu_vu_tuong")], "phuc_nhom_tu_phu_vu_tuong", "draft", "p.217", "gốc gác danh giá, tài lộc bền (Phúc Đức có nhóm Tử Phủ Vũ Tướng)"),
 ("Phúc Đức", "SAT_PHA_LIEM_THAM", [grp("sat_pha_liem_tham")], "phuc_nhom_sat_pha_liem_tham", "draft", "p.217", "khó giữ nếp nhà gốc, nhiều hao tâm (Phúc Đức có nhóm Sát Phá Liêm Tham)"),
 ("Phúc Đức", "CO_NGUYET_DONG_LUONG", [grp("co_nguyet_dong_luong")], "phuc_nhom_dong_luong_nhat_nguyet", "draft", "p.217", "bình an, giàu có bậc trung (Phúc Đức có nhóm Đồng Lương Nhật Nguyệt)"),
 ("Phu Thê", "DEP_DOI", [oAny("Tử Vi", "Thiên Phủ", "Thiên Tướng", "Thiên Lương", "Thiên Đồng")], "phoi_dep_doi_hoa_thuan", "verified", "p.217", "vợ chồng hòa thuận, đẹp đôi, bền lâu (Phu Thê có Tử Vi, Thiên Phủ, Thiên Tướng, Thiên Lương hoặc Thiên Đồng)"),
 ("Phu Thê", "THAI_AM", [has(OWNM, "Thái Âm")], "phoi_thai_am_hop_phuc", "verified", "p.217", "bạn đời hợp phúc, đẹp đôi (Thái Âm tại Phu Thê)"),
 ("Phu Thê", "THAI_DUONG", [has(OWNM, "Thái Dương")], "phoi_thai_duong_lap_gia_dinh_tre", "verified", "p.217", "dễ bất hòa lúc trẻ vì cùng tự ái, nên lập gia đình muộn để lâu dài (Thái Dương tại Phu Thê)"),
 ("Phu Thê", "SAT_PHA_LIEM_THAM", [grp("sat_pha_liem_tham")], "phoi_nhom_sat_pha_bat_hoa", "draft", "p.217", "dễ bất hòa, xa cách (Phu Thê có nhóm Sát Phá Liêm Tham)"),
 ("Phu Thê", "KINH_DA_KHONG_KIEP", [oSAny(*SATS)], "phoi_sat_tinh_de_tan_vo", "draft", "p.217", "tình cảm khó bền, dễ đổ vỡ (Phu Thê gặp Kình, Đà, Không, Kiếp)"),
 ("Phu Thê", "TT", [TT], "phoi_tuan_triet_hoan_canh_dac_biet", "verified", "p.217", "hôn nhân xảy ra trong hoàn cảnh đặc biệt, đôi lứa ban đầu ngỡ ngàng (Phu Thê có Tuần hoặc Triệt); sách nhấn mạnh không nên 'sổ toẹt'"),
 ("Tử Tức", "CHINH_TINH_DAC", [anyof(grp("tu_phu_vu_tuong"), grp("co_nguyet_dong_luong"))], "tu_chinh_tinh_de_co_con_kha_gia", "draft", "p.218", "thuận lợi về con cái (Tử Tức có Tử Phủ Vũ Tướng hoặc Cơ Nguyệt Đồng Lương); sách đòi đắc địa: chưa kiểm"),
 ("Tử Tức", "PHU_TINH", [oSAny("Thai", "Dưỡng", "Mộc Dục", "Trường Sinh", "Đế Vượng", "Tả Phụ", "Hữu Bật", "Thanh Long", "Thiên Hỷ", "Hỷ Thần")], "tu_phu_tinh_con_cai_kha_gia", "verified", "p.218", "con cái dễ có, khá giả, xinh đẹp (Tử Tức có các phụ tinh Thai, Dưỡng, Trường Sinh, Đế Vượng, Tả Hữu, Thanh Long, Thiên Hỷ, Hỷ Thần…)"),
 ("Tật Ách", "CUOI_DOI", [anyof(*[has(OWN, s) for s in ("Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng", "Tả Phụ", "Hữu Bật", "Thiên Khôi", "Thiên Việt")], has(TPH, "Hóa Khoa"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc"))], "tat_cuoi_doi_sung_tuc", "verified", "p.218", "về già sung túc, an nhàn (Cung Tật có Tử Phủ Vũ Tướng, Tả Hữu, Khoa Quyền Lộc hoặc Khôi Việt)"),
 ("Thiên Di", "VO_CHINH_DIEU", [{"fact": "palace.has_no_major", "value": True}], "di_vo_chinh_dieu_tha_noi", "verified", "p.218", "môi trường thả nổi, thành bại tùy người mình gặp (Thiên Di vô chính diệu)"),
 ("Thiên Di", "QUY_NHAN", [oAny("Tử Vi", "Thiên Phủ", "Thái Dương", "Thái Âm", "Thiên Tướng", "Liêm Trinh", "Thiên Đồng"), ], "di_hay_gap_quy_nhan", "draft", "p.219", "hay gặp quý nhân (Thiên Di có Tử Phủ, Nhật Nguyệt, Tướng, Liêm, Đồng…); sách còn kể Xương Khúc, Tả Hữu, Khoa Quyền Lộc"),
 ("Thiên Di", "VU_CU", [oAny("Vũ Khúc", "Cự Môn")], "di_vu_cu_lao_tam", "verified", "p.219", "nhiều lao tâm, khổ trí ở môi trường bên ngoài (Thiên Di có Vũ Khúc hoặc Cự Môn)"),
 ("Thiên Di", "SAT_PHA_THAM", [oAny("Thất Sát", "Phá Quân", "Tham Lang")], "di_sat_pha_tham_tranh_gianh", "draft", "p.219", "môi trường nhiều tranh giành, vất vả (Thiên Di có Sát Phá Tham)"),
 ("Nô Bộc", "SAT_ALONE_TU", [anyof(solo("Thất Sát", "Tử Vi"))], "no_sat_ban_tan_tam", "draft", "p.219", "bạn bè tận tâm (Thất Sát độc thủ hoặc đi với Tử Vi tại Nô Bộc)"),
 ("Nô Bộc", "SAT_VU", [*oM("Thất Sát", "Vũ Khúc")], "no_sat_vu_ban_phan_boi", "verified", "p.219", "bạn bè dễ phản bội (Thất Sát đi với Vũ Khúc tại Nô Bộc)"),
 ("Nô Bộc", "PHA_ALONE_TU", [anyof(solo("Phá Quân", "Tử Vi"))], "no_pha_ban_dac_luc", "draft", "p.219", "bạn bè đắc lực (Phá Quân độc thủ hoặc đi với Tử Vi tại Nô Bộc)"),
 ("Nô Bộc", "PHA_VU", [*oM("Phá Quân", "Vũ Khúc")], "no_pha_vu_ban_gay_oan", "verified", "p.219", "bạn bè dễ gây oán rồi bỏ đi (Phá Quân đi với Vũ Khúc tại Nô Bộc)"),
 ("Nô Bộc", "LIEM_PHU", [*oM("Liêm Trinh", "Thiên Phủ")], "no_liem_phu_dong_ban", "verified", "p.219", "đông bạn bè (Liêm Trinh đi với Thiên Phủ tại Nô Bộc)"),
 ("Nô Bộc", "LIEM_TUONG", [*oM("Liêm Trinh", "Thiên Tướng")], "no_liem_tuong_ban_tot", "verified", "p.219", "bạn tốt (Liêm Trinh đi với Thiên Tướng tại Nô Bộc)"),
 ("Nô Bộc", "THAM_ALONE", [anyof(solo("Tham Lang"))], "no_tham_ban_khong_trung_thanh", "draft", "p.219", "bạn bè không trung thành (Tham Lang độc thủ tại Nô Bộc)"),
 ("Nô Bộc", "TU_PHU_VU_TUONG", [grp("tu_phu_vu_tuong")], "no_nhom_tu_phu_ban_quy_tan_tam", "draft", "p.219", "bạn bè quý, tận tâm (Nô Bộc có nhóm Tử Phủ Vũ Tướng)"),
 ("Nô Bộc", "CU_CO", [anyof(allof(*oM("Cự Môn", "Thiên Cơ")), allof(*oM("Thiên Cơ", "Thái Âm")))], "no_cu_co_ban_khong_that_long", "verified", "p.219", "bạn bè không thật lòng, ít giúp được (Cự Cơ hoặc Cơ Âm tại Nô Bộc)"),
 ("Nô Bộc", "PHUC_BINH_KY", [has(OWN, "Phục Binh"), has("palace.tu_hoa", "Hóa Kỵ")], "no_phuc_binh_ky_phan_chu", "draft", "p.219", "bạn bè, người giúp việc dễ phản chủ (Phục Binh, Hóa Kỵ tại Nô Bộc); sách còn kể Phá Toái"),
 ("Điền Trạch", "THAI_AM", [has(OWNM, "Thái Âm")], "dien_thai_am_nhieu_nha_cua", "verified", "p.219", "nhiều nhà cửa (Thái Âm là sao chủ về điền trạch)"),
 ("Điền Trạch", "KQL", [has(TPH, "Hóa Khoa"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc")], "dien_khoa_quyen_loc_dinh_thu", "verified", "p.219", "nhà cửa tốt, có điều kiện ở nơi khang trang (Khoa, Quyền, Lộc hội tại Điền)"),
 ("Điền Trạch", "NGHEO", [anyof(oAny("Thất Sát", "Phá Quân", "Tham Lang"), oSAny("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp"), TT)], "dien_kho_tich_luy_nha_dat", "draft", "p.220", "khó có cơ nghiệp nhà đất, cố gắng cả đời chủ yếu đủ một mái che thân (Điền có Sát Phá Tham, Kình Đà, Không Kiếp hoặc Tuần Triệt)"),
 ("Phụ Mẫu", "TU_VI", [has(OWNM, "Tử Vi")], "mau_tu_vi_cha_me_quy_hien", "verified", "p.220", "cha mẹ có địa vị, khá giả (Tử Vi tại Phụ Mẫu)"),
 ("Phụ Mẫu", "TU_VI_SPLT", [has(OWNM, "Tử Vi"), oAny("Thất Sát", "Phá Quân", "Liêm Trinh", "Tham Lang")], "mau_tu_vi_sat_con_khong_hop_tinh", "verified", "p.220", "dù cha mẹ khá giả, con cái khó hợp tính cha mẹ (Tử Vi đi với Sát, Phá, Liêm, Tham tại Phụ Mẫu)"),
 ("Phụ Mẫu", "SAO_TOT", [oAny("Thiên Đồng", "Thiên Cơ", "Thái Âm", "Thiên Phủ", "Thiên Tướng", "Thiên Lương")], "mau_cha_me_kha_gia_hoa_thuan", "verified", "p.220", "cha mẹ khá giả, con cái hòa thuận (Phụ Mẫu có Thiên Đồng, Thiên Cơ, Thái Âm, Thiên Phủ, Thiên Tướng hoặc Thiên Lương)"),
 ("Phụ Mẫu", "HUNG", [anyof(has(OWNM, "Cự Môn"), oSAny("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"))], "mau_cha_me_vat_va", "verified", "p.220", "cha mẹ vất vả, chẳng giàu (Phụ Mẫu có Cự Môn, Kình Đà, Hỏa Linh hoặc Không Kiếp)"),
 ("Mệnh", "GIAP_NHAT_NGUYET", [has("palace.neighbor_majors", "Thái Dương"), has("palace.neighbor_majors", "Thái Âm")], "menh_giap_nhat_nguyet_hien_dat", "verified", "p.215", "đường hiển đạt (Nhật Nguyệt giáp hai bên Mệnh)"),
 ("Mệnh", "GIAP_TA_HUU", [has("palace.neighbor_stars", "Tả Phụ"), has("palace.neighbor_stars", "Hữu Bật")], "menh_giap_ta_huu_giau_co", "verified", "p.215", "khá giả, nhiều người giúp (Tả Phụ, Hữu Bật giáp hai bên Mệnh)"),
 ("Mệnh", "GIAP_KHOI_VIET", [has("palace.neighbor_stars", "Thiên Khôi"), has("palace.neighbor_stars", "Thiên Việt")], "menh_giap_khoi_viet_duoc_quy_men", "verified", "p.215", "được người quý trọng, mến chuộng (Khôi, Việt giáp hai bên Mệnh)"),
 ("Mệnh", "GIAP_XUONG_KHUC", [has("palace.neighbor_stars", "Văn Xương"), has("palace.neighbor_stars", "Văn Khúc")], "menh_giap_xuong_khuc_nguoi_tren_giup", "verified", "p.215", "được người bề trên giúp đỡ (Xương, Khúc giáp hai bên Mệnh)"),
]
rules, claims = [], {}
for pal, rid, conds, claim, status, loc, vi in R:
    slug = unicodedata.normalize("NFD", pal.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
    rules.append({"id": f"TV_KL_CUNG_{slug}_{rid}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "kl_cung",
        "description": f"Tử Vi Khảo Luận, tóm tắt từng cung (paraphrased), cung {pal}: {vi} [KL {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": claim, "effect": "support", "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_KHAO_LUAN"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims[claim] = "khuynh hướng " + vi.split(" (")[0] + (" (" + vi.split(" (", 1)[1] if " (" in vi else "")
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_khao_luan_cung.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8")); cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
