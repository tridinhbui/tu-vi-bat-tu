"""Generates data/pack_toan_thu_phu.json: the numbered phú of Tử Vi Đẩu Số Toàn Thư pp.150-165 (Trần Đoàn / Ma Thị / Huỳnh Kim couplets with the translator's
explanation in brackets) that the Khảo Luận and Thực Hành packs do not already hold. Only the explanatory clause is encoded, never the couplet;
death, injury, prison, sexual-reputation and early-death lines are skipped. Reading policy: đồng cung = own palace; hội/chiếu = tam phương."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWN, OWNM, TPS, TPH, FL = "palace.own_stars", "palace.own_major_stars", "palace.rel.tp_stars", "palace.rel.tp_hoa", "palace.rel.flank_stars"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
allof = lambda *x: {"all": list(x)}
nt = lambda x: {"not": x}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
dig = lambda s, lv: {"fact": f"palace.dignity.{s}", "operator": "in", "value": lv}
OM = lambda s: has(OWNM, s)
O = lambda *ss: anyof(*[has(OWN, s) for s in ss])
T = lambda *ss: anyof(*[has(TPS, s) for s in ss])
CATN = lambda n: {"fact": "palace.khi.cat_tp", "operator": "gte", "value": n}
SATN = lambda n: {"fact": "palace.khi.sat_tp", "operator": "gte", "value": n}
TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})
G = lambda g: {"fact": "chart.gender", "value": g}
GOOD, MV = ["miếu", "vượng", "đắc"], ["miếu", "vượng"]
TUMO = ("Thìn", "Tuất", "Sửu", "Mùi")
R = []
def add(pal, rid, conds, claim, status, page, phrase, effect="support"):
    R.append((pal, rid, conds, claim, effect, status, page, phrase))
M = "Mệnh"
add(M, "CO_PHA_KINH", [O("Cự Môn", "Phá Quân", "Kình Dương")], "tt_phu_cu_pha_kinh_tinh_ngang", "verified", "p.151", "tính tình ngang ngược, cương (Cự, Phá hoặc Kình Dương thủ Mệnh)", "limit")
add(M, "PHU_TUONG_DONG_LUONG", [anyof(OM("Thiên Phủ"), OM("Thiên Tướng"), OM("Thiên Đồng"), OM("Thiên Lương"))], "tt_phu_phu_tuong_dong_luong_hieu_thuan", "verified", "p.151", "tính tình hiếu thuận (Phủ, Tướng, Đồng hoặc Lương thủ Mệnh)")
add(M, "SAT_KIEP_THAM", [anyof(OM("Thất Sát"), OM("Tham Lang"), has(OWN, "Địa Kiếp"), has(OWN, "Địa Không"))], "tt_phu_sat_kiep_khong_tham_bat_thuong", "verified", "p.151", "tính tình thất thường (Thất Sát, Tham Lang, Kiếp hoặc Không thủ Mệnh)", "limit")
add(M, "VCD_TU_SAT_DAC", [{"fact": "palace.has_no_major", "value": True}, anyof(allof(O("Kình Dương", "Đà La"), br(*TUMO)), allof(O("Địa Không", "Địa Kiếp"), br("Tỵ", "Hợi", "Dần", "Thân")))], [("tt_phu_vcd_sat_dac_phat_nhanh", "support"), ("tt_phu_vcd_sat_dac_khong_ben", "limit")], "verified", "p.151", "oanh liệt, phát nhanh nhưng không lâu bền (Mệnh vô chính diệu có Kình, Đà, Không hoặc Kiếp đắc địa)")
add(M, "VU_TAM_MENH", [OM("Vũ Khúc"), OM("Tham Lang")], "tt_phu_vu_tham_tien_ban_hau_phu", "verified", "p.152", "trước nghèo sau mới phú quý (Vũ Khúc đồng cung Tham Lang ở Mệnh/Thân)")
add(M, "LIEM_TY_HOI", [OM("Liêm Trinh"), br("Tỵ", "Hợi"), nt(CATN(1))], "tt_phu_liem_ty_hoi_khong_cat_tinh_ngheo", "verified", "p.152", "đời nghèo khốn nếu không có cát tinh trừ giảm (Liêm Trinh hãm ở Tỵ/Hợi)", "limit")
add(M, "AM_DAU_HOI", [OM("Thái Âm"), br("Dậu", "Tuất", "Hợi")], "tt_phu_am_dau_hoi_nhan_nha", "verified", "p.152", "một đời nhàn nhã (Thái Âm thủ Mệnh từ Dậu đến Hợi)")
for pal in ("Mệnh", "Tài Bạch", "Quan Lộc"):
    add(pal, "QUYEN_LOC_VINH_HOA", [anyof(has("palace.tu_hoa", "Hóa Quyền"), has("palace.tu_hoa", "Hóa Lộc"))], "tt_phu_quyen_loc_vinh_hoa", "draft", "p.152", f"vinh hoa (Hóa Quyền hoặc Hóa Lộc nhập miếu ở {pal}); sách đòi 'nhập miếu' mà bảng độ sáng không có cho Tứ Hóa")
add(M, "VAN_VU_KHUC", [O("Văn Khúc"), OM("Vũ Khúc"), br("Thìn", "Tuất", "Tỵ", "Hợi", "Mão", "Dậu")], "tt_phu_khuc_vu_da_hoc_da_nang", "verified", "p.153", "đa học đa năng (Văn Khúc, Vũ Khúc ở Thìn/Tuất, Tỵ/Hợi, Mão/Dậu)")
add(M, "TA_HUU_KHOAN_HAU", [O("Tả Phụ", "Hữu Bật")], "tt_phu_ta_huu_tinh_khoan_hau", "verified", "p.153", "tính tình khoan hậu (Tả Phụ hoặc Hữu Bật ở Mệnh)")
add(M, "THAM_KHOA_QUYEN", [OM("Tham Lang"), anyof(has(TPH, "Hóa Khoa"), has(TPH, "Hóa Quyền"))], "tt_phu_tham_khoa_quyen_hoc_tinh_thong", "verified", "p.153", "việc học tinh thông (Tham Lang vốn lười, gặp Khoa Quyền thì học giỏi)")
add(M, "PHU_TUAT_CAT", [OM("Thiên Phủ"), br("Tuất"), CATN(1)], "tt_phu_phu_tuat_cat_tinh_chuc_lon", "verified", "p.153", "chức vị lớn (Thiên Phủ ở Tuất có cát tinh phù trợ)")
add(M, "VU_TU_MO", [OM("Vũ Khúc"), br(*TUMO)], "tt_phu_vu_tu_mo_uy_danh", "verified", "p.153", "uy danh lẫy lừng (Vũ Khúc ở Thìn/Tuất tốt nhất, Sửu/Mùi kém hơn), cần thêm Quyền Lộc, Tả Hữu, Xương Khúc mới tuyệt đỉnh")
add(M, "KHOA_LOC_AM", [has("palace.tu_hoa", "Hóa Khoa"), has("palace.rel.nhi_hop_stars", "Lộc Tồn")], "tt_phu_khoa_minh_loc_am", "verified", "p.153", "danh phận hơn người (Hóa Khoa ở Mệnh, Lộc Tồn nhị hợp: 'Khoa sáng Lộc ngầm')")
add(M, "LOC_MA_TU_SINH", [O("Lộc Tồn"), O("Thiên Mã"), br("Dần", "Thân", "Tỵ", "Hợi"), nt(SATN(2))], "tt_phu_loc_ma_tu_sinh_de_do_dat", "verified", "p.153", "dễ đỗ đạt (Lộc Tồn, Thiên Mã thủ Mệnh ở Dần, Thân, Tỵ, Hợi, không nhiều sát tinh)")
add(M, "THAM_LINH_TU_MO", [OM("Tham Lang"), O("Linh Tinh"), br(*TUMO)], "tt_phu_tham_linh_tu_mo_van_vo", "verified", "p.153", "lẫy lừng cả văn lẫn võ (Tham Lang, Linh Tinh ở Tứ mộ)")
add(M, "KHOA_QUYEN_SOM", [has("palace.tu_hoa", "Hóa Khoa"), has(TPH, "Hóa Quyền")], "tt_phu_khoa_quyen_cong_danh_som", "draft", "p.154", "công danh dễ dàng, sớm hiển đạt (Mệnh có Hóa Khoa, Quyền chiếu); sách kể Khoa Quyền ở Di, Tài, Quan")
add(M, "LUONG_VU_SUU", [br("Sửu"), T("Thiên Lương"), T("Vũ Khúc")], "tt_phu_luong_vu_chieu_suu_kim_bach", "verified", "p.154", "vàng ngọc đầy kho (Mệnh ở Sửu, Lương, Vũ chiếu)")
add(M, "NHAT_NGUYET_MUI", [br("Mùi"), has("palace.rel.trine_majors", "Thái Dương"), has("palace.rel.trine_majors", "Thái Âm")], "tt_phu_minh_chau_hai", "verified", "p.154", "tiền bạc, danh phận đều hay ('minh châu hải': Mệnh ở Mùi, Nhật Nguyệt tam hợp chiếu)")
add(M, "NHAT_THIN", [OM("Thái Dương"), br("Thìn"), has("palace.rel.opp_majors", "Thái Âm")], "tt_phu_nhat_thin_nguyet_tuat_qui", "verified", "p.154", "quý nhiều hơn phú (Thái Dương ở Thìn, Thái Âm ở Tuất chiếu)")
add(M, "CNDL_DAN_THAN", [br("Dần", "Thân")] + [has("palace.rel.tp_majors", s) for s in ("Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương")], "tt_phu_cndl_dan_than_cong_chuc", "verified", "p.154", "thường làm công chức, văn thư (Cơ Nguyệt Đồng Lương hội ở Dần/Thân)")
add(M, "DONG_LUONG_DAN_THAN", [br("Dần", "Thân"), OM("Thiên Đồng"), OM("Thiên Lương")], "tt_phu_dong_luong_dan_than_rat_tot", "verified", "p.156", "rất tốt (Đồng Lương ở Dần/Thân)")
add(M, "GIAP_NHAT_NGUYET", [has(FL, "Thái Dương"), has(FL, "Thái Âm")], "tt_phu_giap_nhat_nguyet_phu_tac_qui", "verified", "p.155", "không giàu thì sang (Nhật, Nguyệt giáp hai bên Mệnh)")
add(M, "LIEM_MAO_DAU", [OM("Liêm Trinh"), br("Mão", "Dậu")], "tt_phu_liem_mao_dau_cong_mon", "verified", "p.155", "thường làm việc ở chốn công môn, chức vụ nhỏ (Liêm Trinh ở Mão/Dậu)")
add(M, "NHAT_NGUYET_SUU_MUI_GIAP", [OM("Thái Dương"), OM("Thái Âm"), br("Sửu", "Mùi"), anyof(allof(has(FL, "Văn Xương"), has(FL, "Văn Khúc")), allof(has(FL, "Tả Phụ"), has(FL, "Hữu Bật"))), G("nam")], "tt_phu_nhat_nguyet_xuong_khuc_giap_nam_qui", "verified", "p.155", "sang quý (nam mệnh Nhật Nguyệt ở Sửu/Mùi được Xương Khúc hoặc Tả Hữu giáp)")
add(M, "DONG_MIEU", [OM("Thiên Đồng"), dig("Thiên Đồng", GOOD)], "tt_phu_dong_bach_thu_thanh_gia", "verified", "p.156", "tay trắng làm nên (Thiên Đồng đắc địa thủ Mệnh)")
add(M, "PHA_THIN_TUAT_XK", [OM("Phá Quân"), br("Thìn", "Tuất"), T("Văn Xương", "Văn Khúc")], "tt_phu_pha_thin_tuat_xuong_khuc_lao_bac", "verified", "p.156", "cuộc đời bôn tẩu vất vả, không toàn mỹ (Phá Quân ở Thìn/Tuất gặp Xương Khúc)", "limit")
add(M, "DONG_NGO_KINH", [OM("Thiên Đồng"), br("Ngọ"), O("Kình Dương")], "tt_phu_dong_ngo_kinh_uy_tran_bien_ai", "verified", "p.156", "uy danh lẫy lừng nơi biên ải (Thiên Đồng ở Ngọ gặp Kình Dương)")
add(M, "LUONG_KHUC_NGO", [br("Ngọ"), OM("Thiên Lương"), anyof(has(OWN, "Văn Khúc"), has("palace.rel.opp_stars", "Văn Khúc"))], "tt_phu_luong_khuc_ngo_dai_cuong", "verified", "p.156", "quý đến bậc tam phẩm (Mệnh ở Ngọ có Lương, Văn Khúc thủ hoặc Khúc ở Tý chiếu)")
add(M, "CO_LOC_XK", [OM("Thiên Cơ"), O("Lộc Tồn"), O("Văn Xương", "Văn Khúc")], "tt_phu_xuong_khuc_loc_co_thanh_tu_kheo_leo", "draft", "p.157", "thanh tú, khéo léo (Xương/Khúc, Lộc, Cơ ở Mệnh); câu thơ liệt kê bốn sao, đọc là đồng cung")
add(M, "LOC_TT", [O("Lộc Tồn"), TT], "tt_phu_loc_tuan_triet_gia_nghiep_do", "verified", "p.157", "gia nghiệp dễ đổ nát (Lộc Tồn gặp Tuần/Triệt)", "limit")
add(M, "CO_LUONG_THIN", [OM("Thiên Cơ"), OM("Thiên Lương"), br("Thìn", "Tuất"), CATN(1)], "tt_phu_co_luong_thin_tuat_dai_luong_bao_dung", "verified", "p.158", "người đại lượng, bao dung (Cơ Lương thủ Mệnh ở Thìn/Tuất có cát tinh trợ)")
add(M, "AM_TY", [OM("Thái Âm"), br("Tý")], "tt_phu_am_ty_thanh_qui_trung_hau", "verified", "p.158", "thanh quý, lòng trung hậu, hợp chức giám sát (Thái Âm ở Tý)")
add("Tài Bạch", "TU_PHU_VU_KHOA_QUYEN", [anyof(OM("Tử Vi"), OM("Thiên Phủ"), OM("Vũ Khúc")), has(TPH, "Hóa Khoa"), has(TPH, "Hóa Quyền")], "tt_phu_tai_tu_phu_vu_khoa_quyen_giau", "verified", "p.158", "số giàu (Tử, Phủ hoặc Vũ ở Tài Bạch gặp Khoa Quyền)")
add(M, "THAM_HOI_TY", [OM("Tham Lang"), br("Hợi", "Tý")], "tt_phu_tham_hoi_ty_phiem_thuy_dao_hoa", "verified", "p.158", "ưa ăn chơi, đào hoa (Tham Lang ở Hợi/Tý, 'phiếm thủy đào hoa')", "limit")
add(M, "TAM_QUAN_DE", [OM("Tử Vi"), anyof(OM("Thiên Phủ"), OM("Thiên Tướng"), T("Thiên Lương", "Thiên Đồng")), T("Văn Xương", "Văn Khúc")], "tt_phu_quan_than_khanh_hoi_kinh_bang", "draft", "p.159", "rất giàu, có tài kinh bang (Tử Vi thủ Mệnh gặp Xương Khúc, Phủ, Tướng, Lương, Đồng); sách nói thêm gặp tứ sát, Kỵ thì thành kẻ làm loạn")
add(M, "THAM_KINH_DAN", [OM("Tham Lang"), O("Kình Dương"), br("Dần")], "tt_phu_tham_kinh_dan_thong_minh_hao_hoa", "verified", "p.159", "rất thông minh, hào hoa phong lưu (Tham Lang đồng cung Kình Dương ở Dần)")
add("Nô Bộc", "LOC_NO", [anyof(has(OWN, "Lộc Tồn"), has("palace.tu_hoa", "Hóa Lộc"))], "tt_phu_loc_no_bo_phai_kho_nhoc", "verified", "p.159", "có khá cũng phải khó nhọc xoay xở (Lộc ở Nô Bộc)", "limit")
for pal in ("Tài Bạch", "Điền Trạch"):
    add(pal, "LOC_TON", [O("Lộc Tồn")], "tt_phu_loc_ton_dien_tai_doi_kim_tich_ngoc", "verified", "p.159", "vàng ngọc đầy kho (Lộc Tồn ở Điền Trạch hoặc Tài Bạch)")
add(M, "MA_LUONG", [O("Thiên Mã"), OM("Thiên Lương")], "tt_phu_ma_luong_choi_boi_khong_chan", "verified", "p.159", "ăn chơi không biết chán (Thiên Mã, Thiên Lương ở Mệnh)", "limit")
add(M, "HUNG_TINH_DAC", [O("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh"), {"any": [dig("Kình Dương", GOOD), dig("Hỏa Tinh", GOOD), br(*TUMO)]}], "tt_phu_hung_tinh_dac_dia_phat_nhu_loi", "draft", "p.160", "lúc phát như sấm sét (sát tinh đắc địa); sách đối lập với cát tinh đắc địa 'dề dà'")
add(M, "CO_LUONG", [OM("Thiên Cơ"), OM("Thiên Lương")], "tt_phu_co_luong_quyen_bien_da_tai", "verified", "p.160", "quyền biến, tài giỏi (Cơ, Lương ở Mệnh)")
add(M, "CO_LUONG_XK", [OM("Thiên Cơ"), OM("Thiên Lương"), T("Văn Xương", "Văn Khúc")], "tt_phu_co_luong_xuong_khuc_man_tiep", "verified", "p.160", "thêm mẫn tiệp, hoàn toàn hơn (Cơ Lương gặp Xương Khúc)")
add(M, "XK_TUE_KINH", [O("Văn Xương", "Văn Khúc"), T("Thái Tuế"), T("Kình Dương")], "tt_phu_xuong_khuc_tue_kinh_nghe_phap_ly", "draft", "p.160", "hợp nghề pháp lý, tranh tụng (Xương Khúc học nhiều gặp Thái Tuế, Kình); 'gặp' đọc là hội")
add("Phu Thê", "XUONG", [O("Văn Xương")], "tt_phu_the_xuong_thanh_khiet_ich_phu", "verified", "p.160", "người phối ngẫu thanh khiết, giúp ích gia đình (Văn Xương ở Phu Thê)")
add("Tử Tức", "TU_VU", [OM("Tử Vi"), OM("Vũ Khúc")], "tt_phu_tu_tu_vu_qui_tu_da_nam", "verified", "p.157", "con cái quý hiển, nhiều con trai (Tử Vi hội Vũ Khúc ở Tử Tức)")
add(M, "MA_HO_SINH", [O("Thiên Mã"), O("Bạch Hổ"), O("Trường Sinh")], "tt_phu_ma_ho_truong_sinh_cong_danh_dac_lo", "verified", "p.161", "công danh đắc lộ (Thiên Mã, Bạch Hổ ở Tràng Sinh)")
add(M, "KHOA_QUYEN_NGO", [br("Ngọ"), has("palace.tu_hoa", "Hóa Khoa"), has("palace.tu_hoa", "Hóa Quyền")], "tt_phu_khoa_quyen_ngo_bien_cuong", "verified", "p.161", "cai quản việc lớn nơi biên cương (Khoa, Quyền gặp nhau ở Mệnh tại Ngọ)")
add(M, "LUONG_TY", [OM("Thiên Lương"), br("Tỵ")], "tt_phu_luong_ty_choi_boi_bieng_nhac", "verified", "p.161", "chơi bời, biếng nhác (Thiên Lương ở Tỵ)", "limit")
add(M, "DONG_LUONG_KHOI_QUYEN", [OM("Thiên Đồng"), OM("Thiên Lương"), O("Thiên Khôi"), has("palace.tu_hoa", "Hóa Quyền"), anyof(has(OWN, "Lộc Tồn"), has("palace.tu_hoa", "Hóa Lộc"))], "tt_phu_doanh_thuong_de_phu", "draft", "p.162", "số doanh thương, dễ đại phú (Đồng Lương miếu địa gặp Khôi, Quyền, Lộc); sách còn kể Kỵ, Linh")
add(M, "PHA_TUE_HAM", [OM("Phá Quân"), dig("Phá Quân", ["hãm"]), O("Thái Tuế")], "tt_phu_pha_tue_ham_noi_ram_sam_vang", "verified", "p.163", "ăn nói to tiếng, gay gắt (Phá Quân hãm cùng Thái Tuế)", "limit")
add("Tài Bạch", "VU_THAM_KHONG_SAT", [OM("Vũ Khúc"), OM("Tham Lang"), nt(SATN(1))], "tt_phu_tai_vu_tham_khong_sat_hoanh_tai", "verified", "p.163", "hoạnh phát về tiền (Vũ Tham ở Tài Bạch, không có ác sát)")
add(M, "VU_THAM_SUU", [OM("Vũ Khúc"), OM("Tham Lang"), anyof(has(TPH, "Hóa Khoa"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc"))], "tt_phu_vu_tham_tu_mo_quyen_qui", "draft", "p.152", "thêm quyền quý (Vũ Tham đồng cung có Khoa Quyền Lộc hội); sách còn kể Tả Hữu")
slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims = [], {}
for pal, rid, conds, cl, effect, status, loc, vi in R:
    cls = cl if isinstance(cl, list) else [(cl, effect)]
    rules.append({"id": f"TV_TT_PHU_{slug(pal)}_{rid}", "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "tt_phu",
        "description": f"Tử Vi Đẩu Số Toàn Thư, phú (paraphrased), cung {pal}: {vi} [TT {loc}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": c, "effect": e, "scope": "natal"} for c, e in cls],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_TOAN_THU"], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    for c, e in cls:
        claims.setdefault(c, ("khuynh hướng " if e == "support" else "hạn chế: ") + vi)
        if e == "limit":
            claims.setdefault("limit:" + c, "hạn chế: " + vi)
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_toan_thu_phu.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur.setdefault(k, v)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
