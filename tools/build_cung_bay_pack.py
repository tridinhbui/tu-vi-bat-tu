"""Generates engine/data/pack_cung_bay.json: the seven thin palaces (Nô Bộc, Thiên Di, Phúc Đức, Phụ Mẫu, Tử Tức, Huynh Đệ, Tật Ách) from the
'X ở các cung' entries of Tử Vi Khảo Luận (KL pp.55-220) and the palace verses of Tử Vi Thực Hành (TH pp.99-113) — plan 2026-10-23 P1.

Source of every rule: one entry of the raw, page-image-checked mining in engine/data/kg/mined/*.json (named by its mined id here); the quote
and page are taken from that entry, so the quote checked there is the quote checked by engine/tests/test_cung_bay.py. The reading is the
entry's own paraphrase, cleaned for a reader; the condition is the book's (never wider: a book's 'gặp' with no position word is read in the
palace itself, a list naming a group of stars ('lũ …') needs two of them, 'đắc địa' / 'sáng' = miếu, vượng, đắc). Left out on purpose
(recorded in SKIPPED with the reason): death, khắc, mất sớm, illness and every health state (Tật Ách keeps only what the book says the stars
DO there: cứu giải or tối kỵ), prison, theft, sexual reputation, appearance, twins / half-siblings / adopted children and counts of children
or siblings (events), lines whose pairing cannot occur on a chart (Tham–Vũ at Thìn/Tuất, Liêm–Tham at Dần/Thân, Tử–Phá at Tí/Ngọ, Thiên Tướng
'kết hợp' with Tử/Liêm/Vũ at Tỵ Hợi Sửu Mùi) and lines whose reading the miner could not settle from the page."""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "engine" / "data"
MINED = {}
for f in sorted((D / "kg" / "mined").glob("kl_*.json")):
    for e in json.loads(f.read_text("utf-8"))["entries"]:
        MINED[e["id"]] = e

OWNM, OWN, HOA, TPS, TPH = "palace.own_major_stars", "palace.own_stars", "palace.tu_hoa", "palace.tam_phuong_stars", "palace.tam_phuong_tu_hoa"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
allof = lambda *x: {"all": list(x)}
nt = lambda x: {"not": x}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
M = lambda *ss: [has(OWNM, s) for s in ss]
S = lambda s: has(OWN, s)
anyS = lambda *ss: anyof(*[has(OWN, s) for s in ss])
anyM = lambda *ss: anyof(*[has(OWNM, s) for s in ss])
H = lambda h: has(HOA, h)
atleast = lambda n, *xs: {"count": list(xs), "operator": "gte", "value": n}
MAJORS = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân"]
alone = lambda s: [has(OWNM, s), nt(anyof(*[has(OWNM, x) for x in MAJORS if x != s]))]
BRIGHT = ["miếu", "vượng", "đắc"]
dig = lambda school, star, lv: {"fact": f"palace.dignity@{school}.{star}", "operator": "in", "value": lv}
KLD = lambda star, lv: dig("khao_luan", star, lv)
THD = lambda star, lv: dig("thuc_hanh", star, lv)
TRIET = {"fact": "palace.triet", "value": True}
TT = anyof({"fact": "palace.tuan", "value": True}, TRIET)
VCD = {"fact": "palace.has_no_major", "value": True}
KK = anyS("Địa Không", "Địa Kiếp")
LOC = anyof(has(OWN, "Lộc Tồn"), H("Hóa Lộc"))
ref = lambda pal, f, v: {"ref": {"palace": pal, "fact": f}, "operator": "contains", "value": v}

R = []
A, W = "affirms", "weakens"
NO, DI, PHUC, PM, TU, HD, TA = "Nô Bộc", "Thiên Di", "Phúc Đức", "Phụ Mẫu", "Tử Tức", "Huynh Đệ", "Tật Ách"


def add(mid, pal, slug, conds, claim, cond_vi, effect, links, strength=None):
    R.append((mid, pal, slug, conds, claim, cond_vi, effect, links, strength))


# ================= Nô Bộc =================
add("kl080_no_co_luong_ta_huu", NO, "CO_LUONG_TA_HUU", M("Thiên Cơ", "Thiên Lương") + [anyS("Tả Phụ", "Hữu Bật")], "có bạn bè tốt giúp đỡ", "Thiên Cơ, Thiên Lương cùng Tả Phụ, Hữu Bật ở Nô Bộc", "support", [("ally.helpful", A)])
add("kl084_no_nhat_nguyet_sang", NO, "NHAT_SANG", M("Thái Dương") + [KLD("Thái Dương", BRIGHT)], "người dưới quyền dễ lạm quyền", "Thái Dương sáng ở Nô Bộc", "limit", [("ally.overstep", A)])
add("kl084_no_nhat_nguyet_ham", NO, "NHAT_HAM", M("Thái Dương") + [KLD("Thái Dương", ["hãm"])], "người giúp việc ra vào luôn, ít ai ở được lâu", "Thái Dương hãm ở Nô Bộc", "limit", [("ally.fickle", A)])
add("kl093_no_liem_lam_on_nen_oan", NO, "LIEM_LAM_ON", M("Liêm Trinh"), "giúp bạn bè, người dưới mà dễ bị oán lại", "Liêm Trinh ở Nô Bộc", "limit", [("ally.resent", A)])
add("kl099_no_nhat_nguyet_sang", NO, "NGUYET_SANG", M("Thái Âm") + [KLD("Thái Âm", BRIGHT)], "người dưới dễ lạm quyền, nhưng có phụ tá đắc lực", "Thái Âm sáng ở Nô Bộc", "support", [("ally.helpful", A), ("ally.overstep", A)])
add("kl105_no_cu_mon_oan_trach", NO, "CU_OAN", M("Cự Môn"), "bạn bè, người giúp việc hay oán trách", "Cự Môn ở Nô Bộc", "limit", [("ally.resent", A)])
add("kl105_no_cu_mon_ham_phan_boi", NO, "CU_HAM", M("Cự Môn") + [KLD("Cự Môn", ["hãm"])], "dễ bị bạn bè, người dưới phản bội", "Cự Môn hãm ở Nô Bộc", "limit", [("ally.disloyal", A)])
add("kl121_no_ta_huu", NO, "TA_HUU", [anyS("Tả Phụ", "Hữu Bật")], "có nhiều bạn và người giúp đỡ", "Tả Phụ, Hữu Bật ở Nô Bộc", "support", [("ally.many", A)])
add("kl127_no_khong_kiep_phan_chu", NO, "KHONG_KIEP", [KK], "người dưới dễ phản chủ, bạn bè dễ phụ bạc", "Địa Không, Địa Kiếp ở Nô Bộc", "limit", [("ally.disloyal", A)])
add("kl139_no_quan_phu", NO, "QUAN_PHU", [S("Quan Phủ")], "dễ có kiện tụng, cãi vã với bạn bè, người dưới", "Quan Phủ ở Nô Bộc", "limit", [("ally.dispute", A)])
add("kl153_no_co_qua", NO, "CO_QUA", [anyS("Cô Thần", "Quả Tú")], "ít bạn bè vì tính lạnh lùng, không thích giao thiệp", "Cô Thần, Quả Tú ở Nô Bộc", "limit", [("ally.few", A)])
add("kl156_no_hoa_quyen", NO, "HOA_QUYEN", [H("Hóa Quyền")], "có bạn bè có uy quyền", "Hóa Quyền ở Nô Bộc", "support", [("ally.powerful", A)])
add("kl157_no_hoa_ky", NO, "HOA_KY", [H("Hóa Kỵ")], "người giúp việc, người dưới hay nói xấu chủ", "Hóa Kỵ ở Nô Bộc", "limit", [("ally.slander", A)])
add("kl219_no_pha_liem", NO, "PHA_LIEM", M("Phá Quân", "Liêm Trinh"), "có bạn cũng như không", "Phá Quân, Liêm Trinh ở Nô Bộc", "limit", [("ally.weak", A)])
add("kl219_no_liem_doc_thu", NO, "LIEM_DOC", alone("Liêm Trinh"), "bạn bè được việc nhưng không giàu", "Liêm Trinh độc thủ ở Nô Bộc", "support", [("ally.helpful", A)])
add("kl219_no_liem_tham", NO, "LIEM_THAM", M("Liêm Trinh", "Tham Lang"), "bạn bè bất lực, không làm được việc", "Liêm Trinh, Tham Lang ở Nô Bộc", "limit", [("ally.weak", A)])
add("kl219_no_liem_sat", NO, "LIEM_SAT", M("Liêm Trinh", "Thất Sát"), "bạn bè, người giúp việc dễ phản chủ", "Liêm Trinh, Thất Sát ở Nô Bộc", "limit", [("ally.disloyal", A)])
add("kl219_no_tham_tu_vu", NO, "THAM_TU_VU", M("Tham Lang") + [anyM("Tử Vi", "Vũ Khúc")], "bạn bè tham lam", "Tham Lang đi với Tử Vi hoặc Vũ Khúc ở Nô Bộc", "limit", [("ally.greedy", A)])
add("kl219_no_nhat_nguyet_dac", NO, "NHAT_NGUYET_DAC", [anyof(allof(has(OWNM, "Thái Dương"), KLD("Thái Dương", BRIGHT)), allof(has(OWNM, "Thái Âm"), KLD("Thái Âm", BRIGHT)))], "bạn bè được việc", "Thái Dương, Thái Âm đắc địa ở Nô Bộc", "support", [("ally.helpful", A)])
add("kl219_no_nhat_nguyet_ham", NO, "NHAT_NGUYET_HAM", [anyof(allof(has(OWNM, "Thái Dương"), KLD("Thái Dương", ["hãm"])), allof(has(OWNM, "Thái Âm"), KLD("Thái Âm", ["hãm"])))], "bạn bè, người giúp việc hay thay đổi, chỉ ăn hại", "Thái Dương, Thái Âm hãm ở Nô Bộc", "limit", [("ally.fickle", A), ("ally.drain", A)])
add("kl219_no_quy_tinh", NO, "QUY_TINH", [anyS("Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Ân Quang", "Thiên Quý", "Thiên Đức", "Nguyệt Đức")], "đường bạn bè, người giúp việc nhờ đó mà tốt hơn", "có thêm quý tinh, phúc tinh như Tả Hữu, Xương Khúc, Quang Quý, Thiên Đức, Nguyệt Đức ở Nô Bộc", "support", [("ally.helpful", A)], "condition")

# ================= Thiên Di =================
add("kl084_di_nhat_nguyet_tam_hoa", DI, "NHAT_TAM_HOA", [anyM("Thái Dương", "Thái Âm"), has(TPH, "Hóa Lộc"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Khoa")], "ra ngoài được phú quý, có quyền uy", "Nhật Nguyệt ở Thiên Di gặp Tam Hóa", "support", [("outside.favorable", A), ("career.status", A)])
add("kl088_di_vu_khuc_di_xa", DI, "VU", M("Vũ Khúc"), "đi xa làm ăn tốt hơn ở nhà", "Vũ Khúc ở Thiên Di", "support", [("travel.gain", A)])
add("kl088_di_vu_khuc_phu_tuong", DI, "VU_PHU_TUONG", M("Vũ Khúc") + [anyM("Thiên Phủ", "Thiên Tướng")], "ra ngoài rất tốt", "Vũ Khúc đồng cung Thiên Phủ hoặc Thiên Tướng ở Thiên Di", "support", [("outside.favorable", A)])
add("kl093_di_liem_phu_tuong_dan_than", DI, "LIEM_TOT", [has(OWNM, "Liêm Trinh"), anyof(has(OWNM, "Thiên Phủ"), has(OWNM, "Thiên Tướng"), allof(*alone("Liêm Trinh"), br("Dần", "Thân")))], "ra ngoài rất tốt", "Liêm Trinh đồng cung Phủ, Tướng, hoặc đơn thủ tại Dần, Thân ở Thiên Di", "support", [("outside.favorable", A)])
add("kl093_di_liem_pha", DI, "LIEM_PHA", M("Liêm Trinh", "Phá Quân"), "ra ngoài may rủi đi liền nhau", "Liêm Trinh đồng cung Phá Quân ở Thiên Di", "limit", [("travel.mixed", A)])
add("kl093_di_liem_lam_on_nen_oan", DI, "LIEM_LAM_ON", M("Liêm Trinh"), "ra ngoài làm ơn dễ hóa thành oán", "Liêm Trinh ở Thiên Di", "limit", [("travel.dispute", A)])
add("kl099_di_nhat_nguyet_sang_tam_hoa", DI, "NGUYET_TAM_HOA", M("Thái Âm") + [KLD("Thái Âm", BRIGHT), has(TPH, "Hóa Lộc"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Khoa")], "ra ngoài được nhiều người quý trọng", "Thái Âm sáng ở Thiên Di gặp Tam Hóa", "support", [("travel.helped", A)])
add("kl105_di_cu_mon_khau_thiet", DI, "CU", M("Cự Môn"), "ra ngoài hay bị khẩu thiệt, điều tiếng", "Cự Môn ở Thiên Di", "limit", [("travel.dispute", A)])
add("kl111_di_luong_kinh_ne", DI, "LUONG_TOT", [has(OWNM, "Thiên Lương"), anyof(allof(has(OWNM, "Thiên Đồng"), br("Dần", "Thân")), allof(has(OWNM, "Thái Dương"), br("Mão")), has(OWNM, "Thiên Cơ"), br("Tý", "Ngọ"))], "ra ngoài được người kính nể, giúp đỡ", "Thiên Lương ở Thiên Di: cùng Thiên Đồng ở Dần, Thân, cùng Thái Dương ở Mão, cùng Thiên Cơ, hoặc ở Tý, Ngọ", "support", [("travel.helped", A)])
add("kl111_di_luong_ty_hoi_lang_thang", DI, "LUONG_TY_HOI", M("Thiên Lương") + [br("Tỵ", "Hợi")], "ra ngoài lang thang, không ổn định", "Thiên Lương ở Thiên Di tại Tỵ, Hợi", "limit", [("travel.toil", A)])
add("kl117_di_pha_ty_ngo", DI, "PHA_TY_NGO", M("Phá Quân") + [br("Tý", "Ngọ")], "ra ngoài được trọng nể, dễ kiếm tiền", "Phá Quân ở Thiên Di tại Tý, Ngọ", "support", [("travel.helped", A), ("travel.gain", A)])
add("kl117_di_pha_tu_vi", DI, "PHA_TU", M("Phá Quân", "Tử Vi"), "ra ngoài gặp quý nhân", "Phá Quân đồng cung Tử Vi ở Thiên Di", "support", [("travel.helped", A)])
add("kl117_di_pha_vu_liem", DI, "PHA_VU_LIEM", M("Phá Quân") + [anyM("Vũ Khúc", "Liêm Trinh")], "ra ngoài may ít rủi nhiều", "Phá Quân đồng cung Vũ Khúc hoặc Liêm Trinh ở Thiên Di", "limit", [("outside.adverse", A)])
add("kl121_di_ta_huu_lang_bat", DI, "TA_HUU", [anyS("Tả Phụ", "Hữu Bật")], "hay lang bạt, bôn ba nhiều nơi", "Tả Phụ, Hữu Bật ở Thiên Di", "support", [("life.mobility", A)])
add("kl136_di_song_hao_ton_tien", DI, "SONG_HAO", [anyS("Đại Hao", "Tiểu Hao")], "ra ngoài tốn tiền", "Đại Hao, Tiểu Hao ở Thiên Di", "limit", [("travel.costly", A)])
add("kl142_di_loc_ma_giao_tri", DI, "LOC_MA_MENH", [anyof(allof(ref("Mệnh", OWN, "Lộc Tồn"), S("Thiên Mã")), allof(ref("Mệnh", OWN, "Thiên Mã"), S("Lộc Tồn"))), nt(anyof(has(TPS, "Địa Không"), has(TPS, "Địa Kiếp")))],
    "ra ngoài đem lại lộc, cách Lộc Mã giao trì", "Lộc Tồn ở Mệnh, Thiên Mã ở Thiên Di hay ngược lại, không có Không, Kiếp chiếu", "support", [("travel.gain", A)])
add("kl147_di_thai_tue", DI, "THAI_TUE", [S("Thái Tuế")], "ra ngoài hay bị miệng tiếng, cãi vã", "Thái Tuế ở Thiên Di", "limit", [("travel.dispute", A)])
add("kl149_di_tue_pha", DI, "TUE_PHA", [S("Tuế Phá")], "ra ngoài hay châm chọc người khác", "Tuế Phá ở Thiên Di", "limit", [("travel.dispute", A)])
add("kl153_di_thien_ma", DI, "THIEN_MA", [S("Thiên Mã")], "hay đi xa, đi nước ngoài", "Thiên Mã ở Thiên Di", "support", [("life.mobility", A)])
add("kl153_di_co_qua", DI, "CO_QUA", [anyS("Cô Thần", "Quả Tú")], "khó hòa vào xã hội bên ngoài vì tính lạnh lùng, ít giao thiệp", "Cô Thần, Quả Tú ở Thiên Di", "limit", [("social.isolated", A)])
add("kl156_di_hoa_quyen", DI, "HOA_QUYEN", [H("Hóa Quyền")], "có thế lực ngoài xã hội", "Hóa Quyền ở Thiên Di", "support", [("outside.favorable", A)])
add("kl219_di_rieu_da_ky_khong_kiep", DI, "RIEU_DA_KY_KK", [atleast(2, S("Thiên Riêu"), S("Đà La"), H("Hóa Kỵ"), S("Địa Không"), S("Địa Kiếp"), S("Kình Dương"))],
    "ra ngoài long đong vất vả, sống tạm bợ", "Thiên Di gặp lũ Riêu, Đà, Kỵ, Không, Kiếp, Kình (ít nhất hai sao trong cung)", "limit", [("travel.toil", A)])

# ================= Phúc Đức =================
add("kl076_phuc_tu_pha_tham", PHUC, "TU_PHA_THAM", M("Tử Vi") + [anyM("Phá Quân", "Tham Lang")], "phúc đức kém", "Tử Vi đi với Phá Quân hoặc Tham Lang ở Phúc Đức", "limit", [("life.hardship", A)])
add("kl076_phuc_tu_sat_tinh", PHUC, "TU_SAT", M("Tử Vi") + [anyS("Địa Không", "Địa Kiếp", "Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh")], "rất bất lợi cho phúc phần", "Tử Vi ở Phúc Đức gặp Không Kiếp, Kình Đà, Hỏa Linh", "limit", [("life.hardship", A)])
add("kl081_phuc_co_dan", PHUC, "CO_DAN", M("Thiên Cơ") + [br("Dần")], "kém phúc", "Thiên Cơ ở Phúc Đức tại Dần", "limit", [("life.hardship", A)])
add("kl111_phuc_luong_cung_tot", PHUC, "LUONG_TOT", [has(OWNM, "Thiên Lương"), anyof(allof(has(OWNM, "Thiên Đồng"), br("Dần", "Thân")), br("Tý", "Ngọ"), has(OWNM, "Thiên Cơ"), allof(has(OWNM, "Thái Dương"), br("Mão")))], "phúc đức tốt", "Thiên Lương ở Phúc Đức: cùng Thiên Đồng ở Dần, Thân, ở Tý, Ngọ, cùng Thiên Cơ, hoặc cùng Thái Dương ở Mão", "support", [("life.blessed", A)])
add("kl111_phuc_luong_ty_hoi", PHUC, "LUONG_TY_HOI", M("Thiên Lương") + [br("Tỵ", "Hợi")], "phúc đức kém", "Thiên Lương ở Phúc Đức tại Tỵ, Hợi", "limit", [("life.hardship", A)])
add("kl114_phuc_sat_trieu_nguong_dau", PHUC, "SAT_TRIEU", M("Thất Sát") + [br("Dần", "Thân", "Tý", "Ngọ")], "được phúc nhưng phải rời quê lập nghiệp", "Thất Sát ở Phúc Đức tại Dần, Thân, Tý, Ngọ", "support", [("life.blessed", A), ("fortune.away", A)])
add("kl114_phuc_sat_tu", PHUC, "SAT_TU", M("Thất Sát", "Tử Vi"), "phải rời quê mới khá lên", "Thất Sát đồng cung Tử Vi ở Phúc Đức", "support", [("fortune.away", A)])
add("kl117_phuc_pha_base", PHUC, "PHA", M("Phá Quân") + [nt(br("Tý", "Ngọ"))], "họ hàng ly tán, bản thân phải tha hương lập nghiệp", "Phá Quân ở Phúc Đức, trừ ở Tý, Ngọ", "limit", [("fortune.clan_scattered", A), ("fortune.away", A)])
add("kl117_phuc_pha_ti_ngo", PHUC, "PHA_TY_NGO", M("Phá Quân") + [br("Tý", "Ngọ")], "được hưởng phúc", "Phá Quân ở Phúc Đức tại Tý, Ngọ", "support", [("life.blessed", A)])
add("kl117_phuc_pha_dan_than", PHUC, "PHA_DAN_THAN", M("Phá Quân") + [br("Dần", "Thân")], "kém phúc, họ hàng sa sút", "Phá Quân ở Phúc Đức tại Dần, Thân", "limit", [("fortune.clan_decline", A)])
add("kl117_phuc_pha_vu_liem_tu", PHUC, "PHA_VU_LIEM_TU", M("Phá Quân") + [anyM("Vũ Khúc", "Liêm Trinh", "Tử Vi")], "vất vả, phải xa quê", "Phá Quân đồng cung Vũ Khúc, Liêm Trinh hoặc Tử Vi ở Phúc Đức", "limit", [("fortune.away", A), ("life.hardship", A)])
add("kl127_phuc_khong_kiep_dac", PHUC, "KK_DAC", [anyof(allof(S("Địa Không"), KLD("Địa Không", BRIGHT)), allof(S("Địa Kiếp"), KLD("Địa Kiếp", BRIGHT)))], "được hưởng lộc một thời gian nhưng không bền", "Không, Kiếp đắc địa ở Phúc Đức", "limit", [("fin.volatile", A)])
add("kl127_phuc_khong_kiep_ham", PHUC, "KK_HAM", [anyof(allof(S("Địa Không"), KLD("Địa Không", ["hãm"])), allof(S("Địa Kiếp"), KLD("Địa Kiếp", ["hãm"])))], "bất hạnh lớn", "Không, Kiếp hãm ở Phúc Đức", "limit", [("life.hardship", A)])
add("kl132_phuc_quang_quy_than_linh", PHUC, "QUANG_QUY", [S("Ân Quang"), S("Thiên Quý")], "được che chở, mong gì được nấy", "Ân Quang, Thiên Quý ở Phúc Đức", "support", [("fortune.protected", A)])
add("kl135_phuc_da_dan_than_vcd", PHUC, "DA_VCD", [S("Đà La"), br("Dần", "Thân"), VCD], "được phúc, may mắn", "Đà La ở Phúc Đức vô chính diệu tại Dần, Thân", "support", [("life.blessed", A)])
add("kl136_phuc_song_hao", PHUC, "SONG_HAO", [anyS("Đại Hao", "Tiểu Hao")], "nghèo khó, họ hàng ly tán", "Đại Hao, Tiểu Hao ở Phúc Đức", "limit", [("fortune.clan_scattered", A), ("life.hardship", A)])
add("kl149_phuc_long_phuong", PHUC, "LONG_PHUONG", [S("Long Trì"), S("Phượng Các")], "rất tốt cho phúc phần", "Long Trì, Phượng Các ở Phúc Đức", "support", [("life.blessed", A)])
add("kl188_phuc_thien_dong", PHUC, "DONG", M("Thiên Đồng"), "rất tốt cho phúc phần", "Thiên Đồng ở Phúc Đức", "support", [("life.blessed", A)])
add("kl217_phuc_vu_cu_co", PHUC, "VU_CU_CO", [anyM("Vũ Khúc", "Cự Môn", "Thiên Cơ")], "cũng khá giả, có danh, nhưng hay gặp chuyện rắc rối bất ngờ", "Vũ Khúc, Cự Môn hoặc Thiên Cơ ở Phúc Đức", "support", [("fin.stable", A), ("fortune.mishap", A)])
add("kl217_phuc_rieu_da_ky", PHUC, "RIEU_DA_KY", [atleast(2, S("Thiên Riêu"), S("Đà La"), H("Hóa Kỵ"))], "trong đời có lúc mang tai tiếng", "Phúc Đức gặp lũ Riêu, Đà, Kỵ (ít nhất hai sao trong cung)", "limit", [("fortune.reputation", A)])
add("th112_phuc_tuong_binh_de_tuyet", PHUC, "TUONG_BINH", [has(TPS, "Tướng Quân"), has(TPS, "Phục Binh"), has(TPS, "Đế Vượng"), has(TPS, "Tuyệt")], "trong họ có người theo nghiệp võ", "Tướng Quân, Phục Binh, Đế Vượng, Tuyệt đóng ở tam phương Phúc Đức", "support", [("fortune.clan_military", A)])
add("th112_phuc_cu_loc_ma", PHUC, "CU_LOC_MA", M("Cự Môn") + [LOC, S("Thiên Mã")], "đất phúc phát về võ công", "Cự Môn, Lộc, Thiên Mã gặp nhau ở Phúc Đức", "support", [("fortune.clan_military", A)])
add("th112_phuc_loc_co_qua", PHUC, "LOC_CO_QUA", [S("Lộc Tồn"), S("Cô Thần"), S("Quả Tú")], "dòng họ ít người nối dõi", "Lộc Tồn, Cô Thần, Quả Tú ở Phúc Đức", "limit", [("fortune.clan_few", A)])
add("th112_phuc_quan_phuc", PHUC, "QUAN_PHUC", [S("Thiên Quan"), S("Thiên Phúc")], "tốt lành, trong họ có người hiển đạt", "Thiên Quan, Thiên Phúc ở Phúc Đức", "support", [("fortune.clan_prosper", A)])
add("th112_phuc_vu_vuong", PHUC, "VU_VUONG", M("Vũ Khúc") + [THD("Vũ Khúc", ["vượng"])], "trong họ có người theo võ ban", "Vũ Khúc vượng địa ở Phúc Đức", "support", [("fortune.clan_military", A)])
add("th113_phuc_da_khong_kiep", PHUC, "DA_KK", [S("Đà La"), S("Địa Không"), S("Địa Kiếp")], "họ hàng suy hao", "Đà La, Địa Không, Địa Kiếp ở Phúc Đức", "limit", [("fortune.clan_decline", A)])

# ================= Phụ Mẫu =================
add("kl094_phu_liem_phu_tuong", PM, "LIEM_PHU_TUONG", M("Liêm Trinh") + [anyM("Thiên Phủ", "Thiên Tướng")], "cha mẹ khá giả", "Liêm Trinh đồng cung Thiên Phủ hoặc Thiên Tướng ở Phụ Mẫu", "support", [("parents.prosper", A)])
add("kl105_phu_cu_bat_hoa", PM, "CU", M("Cự Môn"), "cha mẹ bất hòa", "Cự Môn ở Phụ Mẫu", "limit", [("parents.strain", A)])
add("kl108_phu_tuong_moi_cung", PM, "TUONG", M("Thiên Tướng"), "cha mẹ khá giả", "Thiên Tướng ở Phụ Mẫu", "support", [("parents.prosper", A)])
add("kl111_phu_luong_cung_tot", PM, "LUONG_TOT", [has(OWNM, "Thiên Lương"), anyof(allof(has(OWNM, "Thiên Đồng"), br("Dần", "Thân")), br("Tý", "Ngọ"), has(OWNM, "Thiên Cơ"), allof(has(OWNM, "Thái Dương"), br("Mão")))], "đường cha mẹ tốt", "Thiên Lương ở Phụ Mẫu: cùng Thiên Đồng ở Dần, Thân, ở Tý, Ngọ, cùng Thiên Cơ, hoặc cùng Thái Dương ở Mão", "support", [("fam.positive", A)])
add("kl111_phu_luong_ty_hoi", PM, "LUONG_TY_HOI", M("Thiên Lương") + [br("Tỵ", "Hợi")], "đường cha mẹ kém", "Thiên Lương ở Phụ Mẫu tại Tỵ, Hợi", "limit", [("fam.negative", A)])
add("kl126_phu_khong_kiep_ly_cach", PM, "KK_LY", [KK], "cha mẹ xa cách nhau", "Địa Không, Địa Kiếp ở Phụ Mẫu", "limit", [("parents.apart", A)])
add("kl126_phu_khong_kiep_ganh_no", PM, "KK_NO", [KK], "không nhờ được cha mẹ, lại phải gánh phần nợ để lại", "Địa Không, Địa Kiếp ở Phụ Mẫu", "limit", [("parents.burden", A)])
add("kl157_phu_hoa_ky", PM, "HOA_KY", [H("Hóa Kỵ")], "cha mẹ bất hòa", "Hóa Kỵ ở Phụ Mẫu", "limit", [("parents.strain", A)])
add("kl220_phu_xuong_khuc_khoa_quyen_loc", PM, "XUONG_KHUC_HOA", [anyof(S("Văn Xương"), S("Văn Khúc"), H("Hóa Khoa"), H("Hóa Quyền"), H("Hóa Lộc"))], "đem lại điều tốt lành cho đường cha mẹ", "Văn Xương, Văn Khúc, Hóa Khoa, Quyền, Lộc ở Phụ Mẫu", "support", [("fam.positive", A)])
add("kl220_phu_ma_ky_tuan_triet_co_qua", PM, "MA_KY_CO_QUA", [anyof(S("Thiên Mã"), H("Hóa Kỵ"), TT), anyS("Cô Thần", "Quả Tú")], "cha mẹ bất hòa, dễ xa cách nhau", "Thiên Mã, Hóa Kỵ hoặc Tuần, Triệt ở Phụ Mẫu, lại thêm Cô Thần, Quả Tú", "limit", [("parents.strain", A), ("parents.apart", A)])

# ================= Tử Tức =================
add("kl73_tu_thien_hy_nhat_nguyet", TU, "HY_NHAT_NGUYET_NU", [{"fact": "chart.gender", "value": "nữ"}, S("Thiên Hỷ"), has(TPS, "Thái Dương"), has(TPS, "Thái Âm")], "có con quý", "nữ mệnh, Thiên Hỷ ở Tử Tức được Thái Dương, Thái Âm hội chiếu", "support", [("kin.talented", A)])
add("kl80_tu_co_luong_nguyet", TU, "CO_LUONG_AM", M("Thiên Cơ") + [anyM("Thiên Lương", "Thái Âm")], "con cái khá đông", "Thiên Cơ cùng Thiên Lương hoặc Thái Âm ở Tử Tức", "support", [("kin.many", A)])
add("kl90_tu_dong_mao", TU, "DONG_MAO", M("Thiên Đồng") + [br("Mão")], "đông con", "Thiên Đồng ở Tử Tức tại Mão", "support", [("kin.many", A)])
add("kl90_tu_dong_ty_hoi", TU, "DONG_TY_HOI", M("Thiên Đồng") + [br("Tỵ", "Hợi")], "ít con", "Thiên Đồng ở Tử Tức tại Tỵ, Hợi", "limit", [("kin.few", A)])
add("kl90_tu_dong_thin_tuat_cu", TU, "DONG_THIN_TUAT", M("Thiên Đồng") + [br("Thìn", "Tuất")], "hiếm con", "Thiên Đồng ở Tử Tức tại Thìn, Tuất", "limit", [("kin.few", A)])
add("kl93_tu_liem_cham_it", TU, "LIEM", M("Liêm Trinh") + [nt(has(OWNM, "Thiên Phủ"))], "chậm con, ít con", "Liêm Trinh ở Tử Tức, không đồng cung Thiên Phủ", "limit", [("kin.few", A), ("kin.late", A)])
add("kl102_tu_tham_lang", TU, "THAM", M("Tham Lang"), "muộn con, hoặc con cái hay phá của", "Tham Lang ở Tử Tức", "limit", [("kin.late", A), ("kin.wayward", A)])
add("kl108_tu_tuong_liem_vu", TU, "TUONG_LIEM_VU", M("Thiên Tướng") + [anyM("Liêm Trinh", "Vũ Khúc")], "ít con, muộn con", "Thiên Tướng đi với Liêm Trinh hoặc Vũ Khúc ở Tử Tức", "limit", [("kin.few", A), ("kin.late", A)])
add("kl110_tu_luong_dong_ti_ngo", TU, "LUONG_DONG_TY_NGO", [has(OWNM, "Thiên Lương"), anyof(allof(has(OWNM, "Thiên Đồng"), br("Dần", "Thân")), br("Tý", "Ngọ"))], "đông con", "Thiên Lương cùng Thiên Đồng ở Dần, Thân, hoặc Thiên Lương ở Tý, Ngọ, tại Tử Tức", "support", [("kin.many", A)])
add("kl110_tu_luong_nhat_co", TU, "LUONG_NHAT_CO", [has(OWNM, "Thiên Lương"), anyof(allof(has(OWNM, "Thái Dương"), br("Mão")), has(OWNM, "Thiên Cơ"))], "đông con, con cái khá giả", "Thiên Lương cùng Thái Dương ở Mão, hoặc cùng Thiên Cơ, tại Tử Tức", "support", [("kin.many", A), ("kin.prosper", A)])
add("kl110_tu_luong_ty_hoi", TU, "LUONG_TY_HOI", M("Thiên Lương") + [br("Tỵ", "Hợi")], "ít con", "Thiên Lương ở Tử Tức tại Tỵ, Hợi", "limit", [("kin.few", A)])
add("kl113_tu_that_sat", TU, "SAT", M("Thất Sát") + [nt(br("Dần", "Thân"))], "đường con cái kém thuận", "Thất Sát ở Tử Tức, trừ ở Dần, Thân", "limit", [("kin.adverse", A)])
add("kl116_tu_pha_hiem", TU, "PHA", M("Phá Quân"), "hiếm con", "Phá Quân ở Tử Tức", "limit", [("kin.few", A)])
add("kl121_tu_ta_huu", TU, "TA_HUU", [anyS("Tả Phụ", "Hữu Bật")], "nhiều con", "Tả Phụ, Hữu Bật ở Tử Tức", "support", [("kin.many", A)])
add("kl126_tu_kk_du_dang", TU, "KK", [KK], "con cái du đãng, hay phá tán của cải", "Địa Không, Địa Kiếp ở Tử Tức", "limit", [("kin.wayward", A)])
add("kl131_tu_quang_qui_hieu", TU, "QUANG_QUY", [S("Ân Quang"), S("Thiên Quý")], "con cái hiếu thảo", "Ân Quang, Thiên Quý ở Tử Tức", "support", [("kin.filial", A)])
add("kl133_tu_loc_ton", TU, "LOC_TON", [S("Lộc Tồn")], "chậm con và hiếm con", "Lộc Tồn ở Tử Tức", "limit", [("kin.late", A), ("kin.few", A)])
add("kl135_tu_da_kk_hoa", TU, "DA_KK_HOA", [atleast(2, S("Đà La"), S("Địa Không"), S("Địa Kiếp"), S("Hỏa Tinh"), S("Linh Tinh"))], "con cái ngỗ ngược", "Đà La, Không, Kiếp, Hỏa, Linh ở Tử Tức (ít nhất hai sao)", "limit", [("kin.wayward", A)])
add("kl149_tu_long_phuong", TU, "LONG_PHUONG", [S("Long Trì"), S("Phượng Các")], "rất tốt cho đường con cái", "Long Trì, Phượng Các ở Tử Tức", "support", [("kin.good", A)])
add("kl153_tu_co_qua", TU, "CO_QUA", [anyS("Cô Thần", "Quả Tú")], "hiếm muộn con", "Cô Thần, Quả Tú ở Tử Tức", "limit", [("kin.few", A), ("kin.late", A)])
add("kl157_tu_hoa_ky", TU, "HOA_KY", [H("Hóa Kỵ")], "cha mẹ và con cái xung khắc, không hợp nhau", "Hóa Kỵ ở Tử Tức", "limit", [("kin.strain", A)])
add("kl161_tu_moc_duc", TU, "MOC_DUC", [S("Mộc Dục")], "hiếm muộn con", "Mộc Dục ở Tử Tức", "limit", [("kin.few", A), ("kin.late", A)])
add("kl162_tu_suy", TU, "SUY", [S("Suy")], "hiếm con", "Suy ở Tử Tức", "limit", [("kin.few", A)])
add("kl193_tu_dau_quan", TU, "DAU_QUAN", [S("Đẩu Quân")], "hiếm con", "Đẩu Quân ở Tử Tức", "limit", [("kin.few", A)])
add("kl218_tu_hiem_con_sat_pha_tham", TU, "SAT_PHA_THAM_VU_LOC", [anyS("Thất Sát", "Phá Quân", "Tham Lang", "Vũ Khúc", "Lộc Tồn")], "có thể hiếm con", "Thất Sát, Phá Quân, Tham Lang, Vũ Khúc hoặc Lộc Tồn ở Tử Tức", "limit", [("kin.few", A)], "potential")

# ================= Huynh Đệ =================
add("kl116_bao_pha_hiem", HD, "PHA_HIEM", M("Phá Quân"), "hiếm anh em", "Phá Quân ở Huynh Đệ", "limit", [("kin.few", A)])
add("kl116_bao_pha_bat_hoa", HD, "PHA_BAT_HOA", M("Phá Quân"), "anh em bất hòa", "Phá Quân ở Huynh Đệ", "limit", [("kin.strain", A)])
add("kl121_bao_ta_huu", HD, "TA_HUU", [anyS("Tả Phụ", "Hữu Bật")], "đông anh em", "Tả Phụ, Hữu Bật ở Huynh Đệ", "support", [("kin.many", A)])
add("kl126_bao_kk_ly_tan", HD, "KK_LY_TAN", [KK], "anh em ly tán", "Địa Không, Địa Kiếp ở Huynh Đệ", "limit", [("kin.apart", A)])
add("kl126_bao_kk_con_do", HD, "KK_NGANG", [KK], "anh em có tính ngang ngược", "Địa Không, Địa Kiếp ở Huynh Đệ", "limit", [("kin.wayward", A)])
add("kl126_bao_kk_lien_luy", HD, "KK_LIEN_LUY", [KK], "dễ bị liên lụy vì anh em", "Địa Không, Địa Kiếp ở Huynh Đệ", "limit", [("kin.burden", A)])
add("kl153_bao_co_qua", HD, "CO_QUA", [anyS("Cô Thần", "Quả Tú")], "ít anh em", "Cô Thần, Quả Tú ở Huynh Đệ", "limit", [("kin.few", A)])
add("kl156_bao_hoa_ky", HD, "HOA_KY", [H("Hóa Kỵ")], "anh em xung khắc, không hợp nhau", "Hóa Kỵ ở Huynh Đệ", "limit", [("kin.strain", A)])
add("th99_bao_tuong_loc_ma_trieu", HD, "TUONG_LOC_MA", [has(TPS, "Tướng Quân"), anyof(has(TPS, "Lộc Tồn"), has(TPH, "Hóa Lộc")), has(TPS, "Thiên Mã")], "anh em có người thuận đường công danh", "Tướng Quân, Lộc, Thiên Mã chiếu về Huynh Đệ", "support", [("kin.talented", A)])
add("th100_bao_tang_ma", HD, "TANG_MA", [S("Tang Môn"), S("Thiên Mã")], "anh em mỗi người một xứ", "Tang Môn gặp Thiên Mã ở Huynh Đệ", "limit", [("kin.apart", A)])
add("th100_bao_thien_hinh", HD, "HINH", [S("Thiên Hình")], "anh em xung khắc", "Thiên Hình ở Huynh Đệ", "limit", [("kin.strain", A)])
add("th100_bao_xuong_khuc_thai_tue", HD, "XUONG_KHUC_THAI_TUE", [S("Văn Xương"), S("Văn Khúc"), S("Thai"), S("Thái Tuế")], "có người anh cả tung hoành", "Văn Xương, Văn Khúc, Thai, Thái Tuế ở Huynh Đệ", "support", [("kin.talented", A)])
add("th101_bao_duong_da", HD, "KINH_DA", [anyS("Kình Dương", "Đà La")], "anh em xung khắc", "Kình Dương, Đà La ở Huynh Đệ", "limit", [("kin.strain", A)])

# ================= Tật Ách (what the stars DO there: cứu giải or tối kỵ; no health state) =================
add("kl76_tat_tu_vi", TA, "TU_VI", M("Tử Vi"), "có Tử Vi là sao cứu giải, rất tốt cho cung này", "Tử Vi ở Tật Ách", "support", [("health.shielded", A)])
add("kl218_tat_thien_khong", TA, "THIEN_KHONG", [S("Thiên Không")], "có Thiên Không cứu giải bất ngờ", "Thiên Không ở Tật Ách", "support", [("health.shielded", A)])
add("kl218_tat_pha_sat_doc_tri_doc", TA, "PHA_SAT", [anyS("Phá Quân", "Phá Toái", "Thất Sát")], "có sao lấy độc trị độc, phá được hạn xấu", "Phá Quân, Phá Toái hoặc Thất Sát ở Tật Ách", "support", [("health.shielded", A)])
add("kl218_tat_song_hao", TA, "SONG_HAO", [anyS("Đại Hao", "Tiểu Hao")], "có Song Hao giải trừ nạn xấu", "Đại Hao, Tiểu Hao ở Tật Ách", "support", [("health.shielded", A)])
add("kl218_tat_toi_ky", TA, "TOI_KY", [anyof(has(OWNM, "Tham Lang"), H("Hóa Kỵ"), S("Địa Không"), S("Địa Kiếp"))], "có sao mà sách bảo là tối kỵ ở cung này", "Tham Lang, Hóa Kỵ, Địa Không, Địa Kiếp ở Tật Ách", "limit", [("health.exposed", A)])

SKIPPED = {
    "kl113_di_sat_dan_than_tu_vi": "'Ngoài vị trí Dần Thân' can be read as 'except Dần Thân' or 'ra ngoài at Dần Thân': the page does not settle it",
    "kl142_di_loc_dao": "'chiếu vào' does not say which palace Không Kiếp aim at",
    "kl102_phuc_tham_vu_thin_tuat": "Tham–Vũ share a palace only at Sửu/Mùi: the printed Thìn/Tuất cannot occur",
    "kl108_phuc_tuong_tu_liem_vu": "Thiên Tướng is alone at Tỵ Hợi Sửu Mùi: 'kết hợp với Tử, Liêm, Vũ' has no position the page states",
    "kl132_phuc_quang_quy_tho": "longevity (health policy)",
    "kl153_phuc_co_qua": "the line under 'Phúc. Tử, Bào' speaks of siblings and children",
    "kl217_phuc_sat_tinh": "illness (health policy)",
    "kl217_phuc_cat_tinh_cuu_giai": "a rescue on the sát line before it: which stars must stand together is not stated",
    "th112_phuc_cu_loc_tuong": "'Lộc' and 'Tướng' are both ambiguous on the verse",
    "th112_phuc_am_tu_hong_dao_cai": "cung phi (archaic, appearance)",
    "th112_phuc_tang_linh_hoa": "fire (an event)",
    "th113_phuc_chinh_dieu": "any chính tinh: too broad to tell a chart apart, and about siblings",
    "kl094_phu_liem_tham_dan_than": "Liêm–Tham share a palace only at Tỵ/Hợi: the printed Dần/Thân cannot occur",
    "kl117_phu_pha_ti_ngo_tu": "Tử–Phá share a palace only at Sửu/Mùi: the printed 'Tí Ngọ đồng cung Tử vi' cannot occur",
    "th113_phu_dong_co_tu_phu": "whether 'Nhật Nguyệt sinh địa' is a second condition is not clear from the verse",
    "kl84_tu_nhat_nguyet_thai": "twins (an event)", "kl105_tu_cu_co": "half-siblings (an event)", "kl131_tu_quang_qui_con_nuoi": "adoption (an event)",
    "kl108_tu_tuong_tu_vi": "Tử Vi and Thiên Tướng are not together at Tỵ Hợi Sửu Mùi: 'đi với' has no position the page states",
    "kl80_bao_co_cu_di_bao": "half-siblings (an event)", "kl99_bao_nhat_nguyet_giap_thai": "twins (an event)",
    "th100_bao_thai_nhat_nguyet": "twins (an event)", "th100_bao_duong_thai_triet_vuong": "half-siblings (an event)", "th100_bao_am_phuc_di_bao": "half-siblings (an event)",
    "th100_bao_tuong_thai_vuong_di_bao": "half-siblings (an event)", "th100_bao_tam_khong_duong": "adoption (an event)", "th100_bao_khoi_viet_counts": "a count of siblings",
    "th100_bao_counts_chinh_tinh": "a count of siblings", "th101_bao_counts": "a count of siblings", "th100_bao_hoa_ky": "the KL p.156 line says the same (one rule kept)",
    "th100_bao_tuong_phuc_y_cong": "'Tướng phục' and the trade it names are the miner's reading, not the page's",
    "th101_bao_dau_quan_ky": "the verse's second half ('còn hưng') is read either way", "th100_bao_tu_tang_ta_huu": "a sister's marriage (an event about another person's fate)",
    "kl127_no_khong_kiep_ban_xau": "the same page line as kl127_no_khong_kiep_phan_chu (one rule, both clauses)",
    "kl148_tat_thien_khong": "the KL p.218 line says the same (one rule kept)", "kl218_tat_triet": "TV_TL_TAT_ACH_GIAM (TL p.128) already reads Triệt at Tật Ách",
    "kl55_tat_thien_phu": "a health state (no conclusion on health)", "kl88_tat_vu_khuc_kim_thuy": "a health state", "kl88_tat_vu_khuc_moc_hoa": "a health state",
    "kl121_tat_ta_huu": "a health state", "kl131_tat_quang_qui_it_benh": "a health state", "kl132_tat_quang_qui_chong_khoi": "a health state",
    "kl140_tat_quan_phuc_thien_su": "longevity (health policy)", "kl142_tat_tuan_triet_vcd": "the book itself says 'phải xét tùy từng hoàn cảnh'",
    "kl161_tat_truong_sinh_sao_xau": "a health state", "kl246_tat_vcd_trong_khong": "a worked case, not a rule of the palace", "kl282_tat_phuc_qui_tinh": "a health state",
}

slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims, links, quotes = [], {}, {}, []
SCHOOL = {"KL": "SRC_KHAO_LUAN", "TH": "SRC_THUC_HANH"}
for mid, pal, rid, conds, claim, cond_vi, effect, ls, strength in R:
    e = MINED[mid]
    assert not e.get("skip"), mid
    book, page = e["book"], e["page"]
    rid_full = f"TV_{book}7_{slug(pal)}_{rid}"
    cl = "c7_" + rid_full[len("TV_"):].lower()
    rules.append({"id": rid_full, "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "cung_bay",
        "description": f"{'Tử Vi Khảo Luận, ý nghĩa các sao ở các cung' if book == 'KL' else 'Tử Vi Thực Hành, phú các cung'} (paraphrased), cung {pal}: {claim} ({cond_vi}) [{book} p.{page}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": cl, "effect": effect, "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": [SCHOOL[book]], "reviewStatus": "verified", "version": "0.1.0", "subject": "palace"})
    claims[cl] = ("khuynh hướng " if effect == "support" else "hạn chế: ") + f"{claim} ({cond_vi})"
    if effect == "limit":
        claims["limit:" + cl] = f"hạn chế: {claim} ({cond_vi})"
    links[rid_full] = {"asserts": [{"concept": c, "stance": s, **({"strength": strength} if strength else {})} for c, s in ls], "src": "manual", "review": "draft"}
    quotes.append({"rule": rid_full, "book": book, "page": page, "quote": e["quote"], "mined": mid})
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
for k in SKIPPED:
    assert k in MINED, k
json.dump({"sources": [], "rules": rules}, open(D / "pack_cung_bay.json", "w"), ensure_ascii=False, indent=1)
json.dump({"note": "page quotes of pack_cung_bay.json (tools/build_cung_bay_pack.py, from engine/data/kg/mined), checked by engine/tests/test_cung_bay.py",
           "quotes": quotes, "skipped": SKIPPED}, open(D / "quotes_cung_bay.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
man = json.loads((D / "kg" / "rule_concepts.manual.json").read_text("utf-8"))
man["entries"].update(links)
json.dump(man, open(D / "kg" / "rule_concepts.manual.json", "w"), ensure_ascii=False, indent=1)
print(len(rules), "rules")
