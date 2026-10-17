"""Generates data/pack_bazi_zz_direct.json from 八字真宗 pp.51-58: occupation by the hour pillar (干为表: ten-god group of the hour stem; the stem itself) and
marriage by the month branch (月令) and day branch (日支). Paraphrased, page-cited. Skipped: infidelity, second-marriage, officialdom/prison, parents' lifespan, illness."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
eq = lambda f, v: {"fact": f, "value": v}
inn = lambda f, v: {"fact": f, "operator": "in", "value": v}
R = []
def add(rid, cond, claim, page, phrase, tone="neutral", status="verified", cat="occupation"):
    R.append((rid, cond, claim, page, phrase, tone, status, cat))
GROUP = {"thuc_thuong": "ăn uống, thủ công, kỹ thuật, biểu diễn, chăn nuôi (Thực Thần, Thương Quan)", "an": "văn hóa, giáo dục (Ấn)", "quan": "hành chính (Quan, Sát)",
         "tai": "tài chính (Tài)", "ty_kiep": "nghề tự do, việc tạp (Tỉ Kiếp)"}
for g, ph in GROUP.items():
    add(f"HOUR_GROUP_{g}", eq("bazi.hour_stem_group", g), f"bt_zz_nghe_tru_gio_{g}", "p.52", f"nghề hợp thiên về {ph} (thập thần của can trụ giờ: 'can là biểu')")
STEM = {"Giáp": "y sĩ, thương nhân, chính pháp, kiến trúc, nông lâm, hóa học, âm nhạc", "Ất": "vườn cảnh, môi giới, thủ công, in ấn, du lịch",
        "Bính": "giải trí, kiểm sát, giám định, xét nghiệm, thẩm mỹ, luyện kim, nhãn khoa, quà tặng, thời trang, hóa học, điện",
        "Đinh": "họa sĩ, biểu diễn, sử học, thẩm mỹ, ẩm thực", "Mậu": "chăn nuôi, nông nghiệp, xây dựng, giết mổ, da lông, đồ gỗ",
        "Kỷ": "thư ký, đánh máy, sắp chữ, phục vụ, nghệ nhân dân gian, địa chính, mầm non, sản phụ khoa, đô thị, vệ sinh, vật tư",
        "Canh": "kim loại, điêu khắc, tư pháp, y sĩ, đạo diễn, võ thuật, đồ tể", "Tân": "trang sức, khóa, luật sư, nghị sĩ, thẩm phán, bói toán",
        "Nhâm": "vận tải, đóng tàu, thủy lợi, chữa cháy, thủy sản, môi trường", "Quý": "tâm lý học, tham mưu, điều độ, thiết kế, hoạch định"}
for s, ph in STEM.items():
    add(f"HOUR_STEM_{s}", eq("bazi.hour_stem", s), f"bt_zz_nghe_can_gio_{unicodedata.normalize('NFD', s.replace('Đ', 'D').replace('đ', 'd')).encode('ascii', 'ignore').decode().lower()}", "p.52", f"nghề có thể thuộc nhóm: {ph} (can trụ giờ {s})", status="draft")
add("YIN_SHEN_JIA", eq("bazi.has_yin_shen_jia", True), "bt_zz_dan_than_giap_buon_ban", "p.51", "hợp việc kinh doanh, buôn bán (trong tứ trụ có đủ Dần, Thân và can Giáp)")
M = lambda *g: inn("bazi.month_main_god", list(g))
add("M_HURT", eq("bazi.month_branch_hurt", True), "bt_zz_hn_nguyet_lenh_hinh_xung", "p.57", "hôn nhân thiếu ổn định (nguyệt lệnh gặp hình, xung, xuyên, tuyệt); hệ thống chưa tính quan hệ 'tuyệt' nên chỉ kiểm hình, xung, hại", "limit", "draft", cat="marriage")
add("M_COMBINED", eq("bazi.month_branch_combined", True), "bt_zz_hn_nguyet_lenh_hop", "p.57", "hôn nhân êm đẹp (nguyệt lệnh được hợp)", cat="marriage")
add("M_KONG", eq("bazi.month_branch_kong", True), "bt_zz_hn_nguyet_lenh_khong_vong", "p.57", "hôn nhân hình thức, tình cảm vợ chồng không thật sâu (nguyệt lệnh gặp không vong)", "limit", cat="marriage")
add("M_THUONG_KIEU_SAT", M("Thương Quan", "Thiên Ấn", "Thất Sát"), "bt_zz_hn_nguyet_kien_thuong_kieu_sat", "p.57", "vợ chồng hay cãi nhau vì chuyện nhỏ (nguyệt kiến là Thương, Kiêu hoặc Sát)", "limit", cat="marriage")
add("M_TAI_QUAN_AN", M("Thiên Tài", "Chính Tài", "Chính Quan", "Chính Ấn"), "bt_zz_hn_nguyet_kien_tai_quan_an", "p.57", "tình cảm vợ chồng hòa thuận (nguyệt kiến là Tài, Quan hoặc Ấn)", cat="marriage")
add("M_NHAN_LOC", M("Tỉ Kiên", "Kiếp Tài"), "bt_zz_hn_nguyet_kien_nhan_loc", "p.57", "hay cãi vã, ồn ào (nguyệt kiến là Tỉ hoặc Kiếp: nhận, lộc)", "limit", cat="marriage")
add("D_HURT", eq("bazi.day_branch_hurt", True), "bt_zz_hn_nhat_chi_hinh_xung", "p.57", "vợ chồng hay xung đột, cãi vã (nhật chi gặp hình, xung, xuyên, tuyệt); hệ thống chưa tính quan hệ 'tuyệt' nên chỉ kiểm hình, xung, hại", "limit", "draft", cat="marriage")
add("D_QUAN_SAT", inn("bazi.day_main_god", ["Chính Quan", "Thất Sát"]), "bt_zz_hn_nhat_chi_quan_sat", "p.57", "người phối ngẫu có sức ràng buộc mạnh, hay hạn chế mình (nhật chi là Quan hoặc Sát)", "limit", cat="marriage")
add("D_TAI", inn("bazi.day_main_god", ["Thiên Tài", "Chính Tài"]), "bt_zz_hn_nhat_chi_tai", "p.57", "được lợi về tiền của nhờ người phối ngẫu (nhật chi là Tài)", cat="marriage")
add("D_THUC_THUONG", inn("bazi.day_main_god", ["Thực Thần", "Thương Quan"]), "bt_zz_hn_nhat_chi_thuc_thuong", "p.57", "người phối ngẫu tốn kém tiền của (nhật chi là Thực hoặc Thương)", "limit", cat="marriage")
G = lambda g: eq("chart.gender", g)          # "nam" / "nữ" (same vocabulary as the Tử Vi facts)
add("W_CHINH_TAI_ROOT", {"all": [eq("bazi.chinh_tai_tho_can", True), eq("bazi.chinh_tai_rooted", True)]}, "bt_zz_tai_chinh_tai_tho_can_co_can", "p.50", "tài vận tốt (Chính Tài thấu can và có gốc)", cat="wealth")
add("W_THIEN_TAI_TD", eq("bazi.thien_tai_tho_can", True), "bt_zz_tai_thien_tai_tho_can_tieu_nhieu", "p.50", "tiêu xài mạnh tay (Thiên Tài thấu can)", "limit", cat="wealth")
add("W_THIEN_TAI_ROOT", {"all": [eq("bazi.thien_tai_tho_can", True), eq("bazi.thien_tai_rooted", True)]}, "bt_zz_tai_thien_tai_tho_can_co_can", "p.50", "tài vận tốt (Thiên Tài thấu can và có gốc)", cat="wealth")
add("W_NO_STAR", eq("bazi.no_wealth_star", True), "bt_zz_tai_khong_hien_xem_thuc_thuong", "p.50", "tài tinh không hiện: phải xét thêm Thực, Thương để luận tài vận", cat="wealth")
add("E_AN_ROOT", {"all": [eq("bazi.an_tho_can", True), eq("bazi.an_rooted", True)]}, "bt_zz_hoc_an_tho_can_co_can", "p.56", "học vấn, bằng cấp cao (Ấn thấu can có gốc)", cat="education")
add("E_AN_VOID", {"all": [eq("bazi.an_tho_can", True), eq("bazi.an_rooted", False)]}, "bt_zz_hoc_an_tho_hu", "p.56", "học vấn ở mức bình thường (Ấn thấu can nhưng không có gốc)", cat="education")
add("O_QUAN_SAT_ROOT", eq("bazi.quan_sat_both_rooted", True), "bt_zz_quan_quan_sat_deu_tho_co_can", "p.52", "một người đảm nhiều chức vụ (Quan và Sát đều thấu can, có gốc)", cat="career")
add("S_PURE_YIN_M", {"all": [eq("bazi.all_yin", True), G("nam")]}, "bt_zz_nam_thuan_am_mem_yeu", "p.59", "tính mềm, thiếu quyết đoán (nam mệnh thuần âm: kiểu 'nam hóa nữ')", "limit", "draft", cat="character")
add("S_PURE_YANG_F", {"all": [eq("bazi.all_yang", True), G("nữ")]}, "bt_zz_nu_thuan_duong_cuong", "p.59", "tính mạnh mẽ, quyết đoán (nữ mệnh thuần dương: kiểu 'nữ cường nhân')", status="draft", cat="character")
add("S_TMM_YIN_M", {"all": [eq("bazi.tmm_all_yin", True), G("nam")]}, "bt_zz_nam_thai_than_menh_am", "p.59", "tính mềm, nặng về tình (nam mệnh thai, thân, mệnh đều âm)", "limit", "draft", cat="character")
add("S_TMM_YANG_F", {"all": [eq("bazi.tmm_all_yang", True), G("nữ")]}, "bt_zz_nu_thai_than_menh_duong", "p.59", "tính mạnh mẽ (nữ mệnh thai, thân, mệnh đều dương)", status="draft", cat="character")
add("REN_MANY", {"fact": "bazi.ren_count", "operator": "gte", "value": 2}, "bt_zz_nhan_nhieu_gia_dinh_bat_loi", "p.73", "gia đình kém thuận lợi (tứ trụ thấy nhiều dương nhẫn)", "limit", cat="blade")
add("REN_TMM", eq("bazi.ren_in_tmm", True), "bt_zz_nhan_thai_than_menh_ich_ky", "p.73", "tính ích kỷ, hay so đo (dương nhẫn cư thai, thân, mệnh)", "limit", cat="blade")
add("REN_COMBINED", eq("bazi.ren_combined", True), "bt_zz_nhan_hop_kheo_nhieu_lao", "p.73", "khéo léo nhưng nhiều vất vả (dương nhẫn được hợp)", cat="blade")
add("REN_SAT_AN", eq("bazi.ren_sat_an_all", True), "bt_zz_nhan_sat_an_cung_hien_qui", "p.73", "có thể sang quý (trong tứ trụ có đủ nhẫn, sát và ấn)", cat="blade")
add("MA_IN_CHART", eq("bazi.ma_in_chart", True), "bt_zz_ma_trong_menh_hieu_dong", "p.74", "ưa hoạt động, khó ngồi yên (trong mệnh cục có dịch mã)", cat="horse")
add("MA_HOUR", eq("bazi.ma_in_hour", True), "bt_zz_ma_o_gio_than_khong_yen", "p.74", "thân không yên, hay bận rộn đi lại (dịch mã ở trụ giờ)", "limit", cat="horse")
add("MA_VOID", eq("bazi.ma_void", True), "bt_zz_ma_khong_vong_kem_thanh_tuu", "p.74", "khó thành tựu, hay lười biếng (dịch mã gặp không vong)", "limit", cat="horse")
add("MA_CLASH", eq("bazi.ma_clashed", True), "bt_zz_ma_gap_xung_khong_nhan_ha", "p.74", "thân không được thanh nhàn (dịch mã bị xung, xuyên)", "limit", cat="horse")
add("MA_COMBINED", eq("bazi.ma_combined", True), "bt_zz_ma_gap_hop_phat_muon", "p.74", "bị ràng buộc, phát muộn (dịch mã gặp hợp)", "limit", cat="horse")
add("WEN_CHANG", eq("bazi.wen_chang_in_chart", True), "bt_zz_van_xuong_co_trong_menh_hoc_hanh", "p.56", "có văn xương trong mệnh cục, thuận cho học hành thi cử (tính theo can năm sinh)", cat="education")
add("SIB_MONTH_STEM", eq("bazi.month_stem_hurt_god", True), "bt_zz_anh_em_can_thang_kieu_thuong_sat", "p.64", "anh em dễ bất hòa (can tháng là Kiêu, Thương hoặc Sát)", "limit", cat="siblings")
add("SIB_MONTH_KONG", eq("bazi.month_branch_kong", True), "bt_zz_anh_em_nguyet_lenh_khong_vong", "p.64", "anh em ít qua lại (nguyệt lệnh gặp không vong)", "limit", cat="siblings")
slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper()
rules, claims = [], {}
for rid, cond, claim, page, vi, tone, status, cat in R:
    effect = {"neutral": "neutral", "limit": "limit"}.get(tone, "support")
    rules.append({"id": f"BT_ZZ_DIRECT_{slug(rid)}", "system": "bat_tu", "schoolId": "bazi_zhenzong_popular", "category": f"zz_direct_{cat}",
        "description": f"八字真宗 直断 (paraphrased): {vi} [PDF {page}]", "conditions": cond,
        "consequences": [{"kind": "finding", "claim": claim, "effect": effect, "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_BAZI_ZHENZONG"], "reviewStatus": status, "version": "0.1.0", "subject": "chart"})
    claims[claim] = ("hạn chế: " if effect == "limit" else "") + vi
    if effect == "limit":
        claims["limit:" + claim] = "hạn chế: " + vi
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids))
json.dump({"sources": [], "rules": rules}, open(D / "pack_bazi_zz_direct.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
