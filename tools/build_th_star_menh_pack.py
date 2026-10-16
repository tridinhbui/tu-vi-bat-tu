"""Generates data/pack_thuc_hanh_star_menh.json from Tử Vi Thực Hành pp.93-96 ('Phụ giải' per major star for Nam mệnh and Nữ mệnh).
Paraphrased, page-cited. Brightness comes from palace.dignity.<star> (the chosen school's table); 'hội cát tinh' = palace.khi.cat_tp >= 1,
'sát tinh hội' = palace.khi.sat_tp >= 1. Deliberately not encoded: death, illness, prison, accident, 'sát phu / hại con' and sexual-reputation lines."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWNM = "palace.own_major_stars"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}
G = lambda g: {"fact": "chart.gender", "value": g}
CAT = {"fact": "palace.khi.cat_tp", "operator": "gte", "value": 1}
SAT = {"fact": "palace.khi.sat_tp", "operator": "gte", "value": 1}
SAT2 = {"fact": "palace.khi.sat_tp", "operator": "gte", "value": 2}
TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})
GOOD, MV, HAM = ["miếu", "vượng", "đắc"], ["miếu", "vượng"], ["hãm"]
R = []
def add(star, sex, rid, extra, claim, status, page, phrase, effect="support", dg=GOOD):
    conds = [G(sex), has(OWNM, star)] + ([dig(star, dg)] if dg else []) + extra
    R.append((star, sex, rid, conds, claim, effect, status, page, phrase))

N, F = "nam", "nữ"
# ---- Nam mệnh
add("Thiên Cơ", N, "MV", [br("Thìn", "Tuất", "Mão", "Dậu")], "nam_co_da_muu_tuc_tri", "verified", "p.93", "đa mưu túc trí, giỏi chiến lược chiến thuật (Cơ miếu vượng ở Thìn, Tuất, Mão, Dậu)", dg=MV)
add("Thiên Cơ", N, "HAO", [br("Mão", "Dậu"), has("palace.rel.tp_stars", "Đại Hao"), has("palace.rel.tp_stars", "Tiểu Hao")], "nam_co_mao_dau_song_hao_van_vo", "verified", "p.93", "tài kiêm văn võ (Cơ ở Mão/Dậu có song Hao)", dg=MV)
add("Thiên Cơ", N, "HAM", [], "nam_co_ham_phieu_bac", "verified", "p.93", "cuộc đời hay phiêu bạt, nhiều trắc trở (Thiên Cơ hãm)", "limit", HAM)
add("Thái Dương", N, "MV_CAT", [CAT], "nam_nhat_thao_luoc_uy_quyen", "verified", "p.93", "thao lược, có uy quyền hiển hách (Thái Dương miếu vượng hội cát tinh)", dg=MV)
add("Thái Dương", N, "HAM_HOI_TAM_HOA", [br("Hợi")] + [has("palace.rel.tp_hoa", h) for h in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")], "nam_nhat_ham_hoi_tam_hoa_ruc_ro", "verified", "p.93", "vẫn rực rỡ (Thái Dương hãm ở Hợi được Tam Hóa)", dg=HAM)
add("Thái Dương", N, "HAM_SAT", [SAT], "nam_nhat_ham_sat_phieu_bat", "verified", "p.93", "đời lang thang phiêu bạt, hay gặp trắc trở (Thái Dương hãm hội sát tinh)", "limit", HAM)
add("Vũ Khúc", N, "MV_CAT", [CAT], "nam_vu_hien_dat_vo_nghiep", "verified", "p.94", "hiển đạt về võ nghiệp (Vũ Khúc miếu vượng hội cát tinh)")
add("Vũ Khúc", N, "HAM_CAT", [CAT], "nam_vu_ham_ky_nghe_kinh_doanh", "verified", "p.94", "chuyên về kỹ nghệ hay kinh doanh, trở nên khá giả (Vũ Khúc hãm hội nhiều cát tinh)", dg=HAM)
add("Vũ Khúc", N, "HAM_SAT", [SAT], "nam_vu_ham_sat_tha_phuong", "verified", "p.94", "cùng khổ, phải tha phương cầu thực (Vũ Khúc hãm hội sát tinh)", "limit", HAM)
add("Thiên Đồng", N, "MV_CAT", [CAT], "nam_dong_phuc_tho_song_toan", "verified", "p.94", "phúc thọ song toàn (Thiên Đồng miếu vượng hội cát tinh)")
add("Thiên Đồng", N, "HAM_SAT", [SAT2], "nam_dong_ham_doi_thay_vo_do", "verified", "p.94", "đời đổi thay vô độ, lao khổ về sinh kế (Thiên Đồng hãm gặp nhiều sao xấu); 'nhiều sao xấu' quy ước từ hai sát tinh", "limit", HAM)
add("Liêm Trinh", N, "MV_CAT", [CAT], "nam_liem_uy_quyen_hien_hach", "verified", "p.94", "có uy quyền hiển hách (Liêm Trinh miếu vượng hội cát tinh)")
add("Liêm Trinh", N, "HAM_SAT", [SAT], "nam_liem_ham_sat_cung_kho", "verified", "p.94", "suốt đời cùng khổ (Liêm Trinh hãm hội sát tinh)", "limit", HAM)
add("Thiên Phủ", N, "CAT", [CAT], "nam_phu_phuc_loc_song_toan", "verified", "p.94", "phúc lộc song toàn (Thiên Phủ hội cát tinh)", dg=None)
add("Thiên Phủ", N, "TUAN_TRIET", [anyof(TT, has("palace.rel.tp_stars", "Thiên Không"), has("palace.rel.tp_stars", "Địa Không"))], "nam_phu_ky_tuan_triet_khong_cung_kho", "verified", "p.94", "cùng khổ, chỉ tu hành mới yên thân (Thiên Phủ kỵ nhất gặp Tuần, Triệt hoặc Thiên, Địa Không)", "limit", None)
add("Thái Âm", N, "MV_CAT", [CAT], "nam_am_phu_quy_tot_do", "verified", "p.94", "hưởng phú quý tột độ (Thái Âm miếu vượng hay đắc địa hội cát tinh)")
add("Tham Lang", N, "MV", [], "nam_tham_hao_thang_kinh_doanh", "verified", "p.95", "háo thắng, thích kinh doanh, có tài tổ chức, hay mưu tính lớn, về sau hưởng giàu sang (Tham Lang miếu vượng đắc địa)")
add("Tham Lang", N, "THIEU_THOI", [], "nam_tham_thieu_thoi_vat_va", "verified", "p.95", "thuở thiếu thời hay vất vả (Tham Lang thủ Mệnh)", "limit", None)
add("Cự Môn", N, "MV_CAT", [CAT], "nam_cu_phu_quy_toan_my", "verified", "p.95", "hưởng phú quý toàn mỹ (Cự Môn miếu vượng đắc địa hội cát tinh)")
add("Cự Môn", N, "HAM_SAT", [SAT], "nam_cu_ham_sat_cung_kho_co_don", "verified", "p.95", "suốt đời cùng khổ, cô đơn (Cự Môn hãm hội sát tinh)", "limit", HAM)
add("Thiên Tướng", N, "MV", [], "nam_tuong_thong_minh_uy_nghi", "verified", "p.95", "thông minh, dáng uy nghi, phúc hậu, có uy quyền và danh tiếng (Thiên Tướng miếu vượng đắc địa)")
add("Thiên Tướng", N, "TUAN_TRIET", [TT], "nam_tuong_gap_tuan_triet_lao_dao", "verified", "p.95", "như Tướng hãm địa: lao đao, chỉ tu hành mới tránh đơn độc, phiền lụy (Thiên Tướng đắc địa gặp Tuần/Triệt án ngữ)", "limit")
add("Thiên Lương", N, "MV", [], "nam_luong_thong_minh", "verified", "p.95", "thông minh (Thiên Lương miếu vượng đắc địa)")
add("Thiên Lương", N, "THIN_TUAT", [br("Thìn", "Tuất")], "nam_luong_thin_tuat_co_muu_chinh_tri", "verified", "p.95", "nhiều cơ mưu, giỏi chính trị và chiến lược (Thiên Lương ở Thìn, Tuất)")
add("Thiên Lương", N, "HAM", [], "nam_luong_ham_doi_viec_chi_huong", "verified", "p.95", "không bao giờ yên thân, luôn thay đổi công việc và chí hướng (Thiên Lương hãm)", "limit", HAM)
add("Thất Sát", N, "OWN", [], "nam_sat_uong_nganh", "verified", "p.96", "tính ương ngạnh (Thất Sát thủ Mệnh)", "limit", None)
add("Thất Sát", N, "DAC", [], "nam_sat_dac_dia_can_dam", "verified", "p.96", "rất can đảm (Thất Sát đắc địa)")
add("Thất Sát", N, "MV_CAT", [CAT], "nam_sat_hien_dat_vo_nghiep", "verified", "p.96", "thường hiển đạt về võ nghiệp (Thất Sát đắc địa hội cát tinh)")
add("Thất Sát", N, "HAM", [], "nam_sat_ham_lang_thang_phieu_bat", "verified", "p.96", "đời lang thang phiêu bạt (Thất Sát hãm)", "limit", HAM)
add("Phá Quân", N, "MV", [], "nam_pha_hien_dat_vo_nghiep", "verified", "p.96", "hiển đạt về võ nghiệp, uy quyền hiển hách (Phá Quân miếu vượng đắc địa)")
add("Phá Quân", N, "HAM", [], "nam_pha_ham_co_don_cung_khon", "verified", "p.96", "cô đơn, cùng khốn (Phá Quân hãm)", "limit", HAM)
# ---- Nữ mệnh
add("Thiên Cơ", F, "MV", [], "nu_co_dam_dang_vuong_phu", "verified", "p.93", "có tài đảm đang, vượng phu ích tử, giàu sang (Cơ miếu hoặc đắc địa)")
add("Thiên Cơ", F, "HAM", [], "nu_co_ham_gioi_dang_xao_tra", "verified", "p.93", "giỏi giang nhưng hay xảo trá (Thiên Cơ hãm)", "limit", HAM)
add("Thái Dương", F, "MV", [], "nu_nhat_cuong_nghi_vuong_phu", "verified", "p.93", "cương nghị, vượng phu ích tử, phúc lộc (Thái Dương miếu vượng)", dg=MV)
add("Thái Dương", F, "HAM", [], "nu_nhat_ham_da_sau_da_cam", "verified", "p.93", "đa sầu đa cảm nhưng vẫn đủ ăn, có chuyện buồn thương (Thái Dương hãm)", "limit", HAM)
add("Vũ Khúc", F, "MV", [], "nu_vu_dam_dang_muon_lap_gia_dinh", "verified", "p.94", "đảm đang, hưởng giàu sang, nhưng nên muộn lập gia đình (Vũ Khúc miếu vượng đắc địa)")
add("Vũ Khúc", F, "HAM", [], "nu_vu_ham_dam_dang_hung_bao_lan_at", "verified", "p.94", "đảm đang nhưng hung bạo, tham lận, hay lấn át chồng con (Vũ Khúc hãm)", "limit", HAM)
add("Thiên Đồng", F, "MV", [], "nu_dong_duc_do_dam_dang", "verified", "p.94", "đức độ, đảm đang, vượng phu ích tử (Thiên Đồng rực rỡ hoặc đắc địa)")
add("Liêm Trinh", F, "MV", [], "nu_liem_nghiem_nghi_doan_chinh", "verified", "p.94", "nghiêm nghị, đoan chính, thanh cao, đảm đang giàu sang, nên muộn lập gia đình (Liêm Trinh miếu vượng đắc địa)")
add("Thiên Phủ", F, "CAT", [CAT], "nu_phu_giau_sang_loi_chong_con", "verified", "p.94", "giàu sang, lợi chồng con (Thiên Phủ hội cát tinh)", dg=None)
add("Thiên Phủ", F, "TUAN_TRIET", [anyof(TT, has("palace.rel.tp_stars", "Thiên Không"), has("palace.rel.tp_stars", "Địa Không"))], "nu_phu_tuan_triet_lao_tam_vi_chong_con", "verified", "p.94", "lao tâm, đau khổ vì chồng con (Thiên Phủ gặp Tuần, Triệt hoặc Thiên, Địa Không)", "limit", None)
add("Thái Âm", F, "MV", [], "nu_am_nhan_sac_vuong_phu", "verified", "p.94", "có nhan sắc, vượng phu ích tử, giàu sang (Thái Âm miếu vượng đắc địa)")
add("Thái Âm", F, "TUAN_TRIET", [TT], "nu_am_tuan_triet_muon_lap_gia_dinh", "verified", "p.94", "nên muộn lập gia đình hoặc làm lẽ mới tránh dở dang (Thái Âm gặp Tuần/Triệt án ngữ)", "limit")
add("Tham Lang", F, "MV", [], "nu_tham_dam_dang_bao_ton_ghen", "verified", "p.95", "đảm đang, bạo tợn, hay ghen tuông, hưởng giàu sang (Tham Lang miếu vượng đắc địa)")
add("Cự Môn", F, "MV", [], "nu_cu_duc_do_vuong_phu", "verified", "p.95", "có đức độ, vượng phu ích tử (Cự Môn miếu vượng đắc địa)")
add("Cự Môn", F, "HAM", [], "nu_cu_ham_noi_dieu_ghen_vat_va", "verified", "p.95", "ăn nói điêu ngoa, hay ghen tuông, đời nhiều vất vả (Cự Môn hãm)", "limit", HAM)
add("Thiên Tướng", F, "MV", [], "nu_tuong_co_tai_hay_ghen", "verified", "p.95", "có tài nhưng hay ghen tuông, hưởng phúc lộc (Thiên Tướng miếu vượng đắc địa)")
add("Thiên Tướng", F, "MV_CAT", [CAT], "nu_tuong_cat_tinh_phu_quy_tot_buc", "verified", "p.95", "phú quý tột bực (Thiên Tướng đắc địa có cát tinh hội)")
add("Thiên Tướng", F, "TUAN_TRIET", [TT], "nu_tuong_tuan_triet_khon_kho_vi_chong_con", "verified", "p.95", "tuy có tài nhưng suốt đời khốn khổ, buồn khổ vì chồng con (Thiên Tướng gặp Tuần/Triệt như Tướng hãm)", "limit")
add("Thiên Lương", F, "MV", [], "nu_luong_sang_y_hien_phu", "verified", "p.95", "sáng ý, làm gì cũng chóng có kết quả, là bậc hiền phụ (Thiên Lương miếu vượng đắc địa)")
add("Thiên Lương", F, "TUAN_TRIET", [TT], "nu_luong_tuan_triet_tinh_duyen_trac_tro", "verified", "p.95", "tình duyên trắc trở (Thiên Lương gặp Tuần/Triệt)", "limit")
add("Thất Sát", F, "OWN", [], "nu_sat_hay_ghen_muon_lap_gia_dinh", "verified", "p.96", "tính hay ghen, nên muộn lập gia đình mới êm (Thất Sát thủ Mệnh nữ)", "limit", None)
add("Phá Quân", F, "MV", [], "nu_pha_tao_bao_muon_lap_gia_dinh", "verified", "p.96", "táo bạo, hưởng phúc lộc nhưng nên muộn lập gia đình (Phá Quân miếu vượng đắc địa)")

slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for star, sex, rid, conds, claim, effect, status, loc, vi in R:
    rules.append({"id": f"TV_TH_STAR_{slug(star)}_{sex.upper() if sex == 'nam' else 'NU'}_{rid}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "th_star_menh",
        "description": f"Tử Vi Thực Hành, phụ giải sao chính ở Mệnh {sex} (paraphrased): {vi} [TH {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": "Mệnh"}] + conds},
        "consequences": [{"kind": "finding", "claim": claim, "effect": effect, "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_THUC_HANH"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims.setdefault(claim, ("khuynh hướng " if effect == "support" else "hạn chế: ") + vi)
    if effect == "limit":
        claims.setdefault("limit:" + claim, "hạn chế: " + vi)
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_thuc_hanh_star_menh.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
