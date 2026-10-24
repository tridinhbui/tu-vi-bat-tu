"""Generates the DEEP-3 Tử Vi rule packs (plan pasted-content-id-885b … radiant-donut, Workstream B, 2026-10-24) from the raw page-checked
mining in engine/data/kg/mined/deep3_*.json (tools/mining/deep3/build.py):

    engine/data/pack_toan_thu_ca.json         Toàn Thư (Vũ Tài Lục): Nam Mệnh ca pp.64-76, nữ mệnh pp.113-118, phú nôm Tật Ách / Huynh Đệ /
                                              Tử Tức pp.91-93, cách cục pp.141-143 (formation rules), hợp cách / phá cách pp.143-149
    engine/data/pack_khao_luan_cach.json      Khảo Luận: hạ cách / kỳ cách pp.46-47 (formation rules), Khốc Hư, Song Hao, Tuần Triệt pp.202-204,
                                              Mệnh vô chính diệu pp.204-206, Bài thơ Liên Giáp p.205 (the cát cách of pp.43-48 are formations_verified.json)
    engine/data/pack_toan_thu_han_van.json    紫微斗數全書 卷二 (zh.wikisource snapshot): 兄弟, 子女, 奴仆, 父母 — cited 'TTH 2 <section>'
    engine/data/quotes_deep3_tuvi.json        the quote of every rule (from its mined entry), the skipped entries with their reason, the duplicates

Every rule names the mined entry it comes from; the quote and page are that entry's, so the quote checked by tools/mining/deep3/build.py is
the one engine/tests/test_deep3_tuvi.py re-checks. Conditions are the page's and never wider: a 'gặp' with no position is read in the palace
itself, a named group of stars ('Hỏa Linh Kình Đà') needs two of them, brightness is read in the rule's own book (dignity@toan_thu for Toàn
Thư and 紫微斗數全書, dignity@khao_luan for Khảo Luận; a star in the tam phương is read on the chart's table, palace.tp_rank), the Nam Mệnh ca
are for men (TT p.64) and the nữ mệnh ca for women. Left out (quotes_deep3_tuvi.json 'skipped', reasons from the mined entries): death,
illness, injury, prison, sexual reputation, appearance, counts and sex of children / siblings, marriage events, lines that cannot occur on a
chart and lines whose reading the page does not settle. Packs are patched in place after generation as the others are: rerun only before
such patches, then re-apply them.  .venv/bin/python tools/build_deep3_tuvi_pack.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "engine" / "data"
MINED = {}
FAM = {}
for f in sorted((D / "kg" / "mined").glob("deep3_*.json")):
    for e in json.loads(f.read_text("utf-8"))["entries"]:
        MINED[e["id"]] = e
        FAM[e["id"]] = f.stem

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
T = lambda s: has(TPS, s)
TH3 = [has(TPH, "Hóa Lộc"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Khoa")]
atleast = lambda n, *xs: {"count": list(xs), "operator": "gte", "value": n}
MAJORS = ["Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng",
          "Thiên Lương", "Thất Sát", "Phá Quân"]
SAT6 = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]
SAT4 = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh"]
alone = lambda s: [has(OWNM, s), nt(anyof(*[has(OWNM, x) for x in MAJORS if x != s]))]
dig = lambda school, star, lv: {"fact": f"palace.dignity@{school}.{star}", "operator": "in", "value": lv}
TTD = lambda star, lv: dig("toan_thu", star, lv)
TPR = lambda star, op, v: {"fact": f"palace.tp_rank.{star}", "operator": op, "value": v}
RANK = lambda star, op, v: {"fact": f"palace.dignity_rank.{star}", "operator": op, "value": v}
CAT = lambda n=1: {"fact": "palace.khi.cat_tp", "operator": "gte", "value": n}
SAT = lambda n=1: {"fact": "palace.khi.sat_tp", "operator": "gte", "value": n}
TUAN, TRIET = {"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True}
VCD = {"fact": "palace.has_no_major", "value": True}
NAM, NU = {"fact": "chart.gender", "value": "nam"}, {"fact": "chart.gender", "value": "nữ"}
STEM = lambda *s: {"fact": "chart.year_stem", "operator": "in", "value": list(s)}
YB = lambda *b: {"fact": "chart.year_branch", "operator": "in", "value": list(b)}
ref = lambda pal, f, v: {"ref": {"palace": pal, "fact": f}, "operator": "contains", "value": v}
PREV, NEXT, OPP, TRINE = "palace.rel.flank_prev_stars", "palace.rel.flank_next_stars", "palace.rel.opp_stars", "palace.rel.trine_stars"
giap = lambda a, b: anyof(allof(has(PREV, a), has(NEXT, b)), allof(has(PREV, b), has(NEXT, a)))
TU_MO = ["Thìn", "Tuất", "Sửu", "Mùi"]
A, W = "affirms", "weakens"
MENH, NO, PM, TU, HD, TA = "Mệnh", "Nô Bộc", "Phụ Mẫu", "Tử Tức", "Huynh Đệ", "Tật Ách"

R = []      # (pack, mined id, palace, conditions, claim, cond_vi, effect, links, kind, also)


def add(pack, mid, pal, conds, claim, cond_vi, effect, links, kind=None, also=()):
    R.append((pack, mid, pal, conds, claim, cond_vi, effect, links, kind, list(also)))


tt = lambda *a, **k: add("pack_toan_thu_ca.json", *a, **k)
kl = lambda *a, **k: add("pack_khao_luan_cach.json", *a, **k)
qs = lambda *a, **k: add("pack_toan_thu_han_van.json", *a, **k)

# ================= Toàn Thư: Nam Mệnh ca (pp.64-76), men only =================
tt("tt65_tu_vi_menh", MENH, [NAM, *M("Tử Vi")], "phúc lộc, tiền tài hưng vượng", "nam, Tử Vi thủ Mệnh", "support", [("fin.abundance", A), ("life.blessed", A)])
tt("tt65_tu_vi_sat_tinh_chua", MENH, [NAM, *M("Tử Vi"), atleast(2, *[T(s) for s in SAT4])], "chỉ hợp đường tu hành, xa lánh việc đời",
   "nam, Tử Vi thủ Mệnh gặp Kình, Đà, Hỏa, Linh hội", "limit", [("spirit.unworldly", A)])
tt("tt65_tu_vi_thin_tuat_pha", MENH, [NAM, *M("Tử Vi"), br("Thìn", "Tuất")], "có thể giàu mà chẳng sang, chỉ được hư danh", "nam, Tử Vi ở Thìn, Tuất hội Phá Quân",
   "limit", [("career.status", W)])
tt("tt65_tu_tham_mao_dau", MENH, [NAM, *M("Tử Vi", "Tham Lang"), br("Mão", "Dậu")], "làm tôi mà dễ bất trung", "nam, Tử Vi gặp Tham Lang ở Mão, Dậu", "limit",
   [("values.integrity", W)])
tt("tt65_tu_sat_bon_sat", MENH, [NAM, *M("Tử Vi", "Thất Sát"), atleast(2, *[T(s) for s in SAT4])], "dễ du thủ du thực, hay lừa dối, cô độc",
   "nam, Tử Vi, Thất Sát thủ Mệnh bị Hỏa, Linh, Kình, Đà vây", "limit", [("values.integrity", W), ("social.isolated", A)])
CNDL_NHAT = [NAM, *M("Thiên Cơ"), T("Thái Âm"), T("Thiên Lương"), T("Thái Dương"), TPR("Thái Dương", "gte", 2)]
tt("tt65_co_nguyet_luong_nhat", MENH, CNDL_NHAT, "người bình thường cũng nên giàu, có nhà cửa", "nam, Thiên Cơ thủ Mệnh hợp Thái Âm, Thiên Lương, Thái Dương đắc địa",
   "support", [("fin.abundance", A), ("prop.rich", A)])
tt("tt65_co_nguyet_luong_tam_hoa", MENH, CNDL_NHAT + TH3, "người có chức tước thì chức vị lên cao", "như trên, thêm Khoa, Quyền, Lộc", "support", [("career.status", A)])
tt("tt65_co_hoa_ky_ty", MENH, [NAM, *M("Thiên Cơ"), br("Tỵ"), H("Hóa Kỵ"), STEM("Mậu")], "dù có chức vị, tiền tài rồi cũng dễ mất, có khi bỏ đời mà đi tu",
   "nam, Thiên Cơ hóa Kỵ ở Tỵ", "limit", [("fin.volatile", A), ("spirit.unworldly", A)])
tt("tt66_nhat_quyen_loc_cat", MENH, [NAM, *M("Thái Dương"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc"), T("Thiên Khôi"), T("Văn Xương"), T("Tả Phụ"), T("Hữu Bật")],
   "phú quý lớn", "nam, Thái Dương thủ Mệnh có Quyền, Lộc, Khôi, Xương, Tả Hữu hội", "support", [("fin.abundance", A), ("career.status", A)])
NN_SM = [NAM, *M("Thái Dương"), br("Sửu", "Mùi"), nt(anyof(*TH3))]
tt("tt66_nhat_suu_mui_vo_hoa", MENH, NN_SM, "phúc bạc", "nam, Thái Dương ở Sửu, Mùi mà tam phương không có Khoa, Quyền, Lộc", "limit", [("life.blessed", W)])
tt("tt66_nhat_suu_mui_sat", MENH, NN_SM + [SAT(1)], "dễ túng thiếu cả đời", "như trên, thêm sát tinh xung phá", "limit", [("fin.scarcity", A)])
tt("tt66_nhat_ham_ky", MENH, [NAM, *M("Thái Dương"), TTD("Thái Dương", ["hãm"]), has(TPH, "Hóa Kỵ")],
   "việc gì cũng mờ ám, trục trặc, dễ gặp việc bất ngờ mà hao tổn sản nghiệp", "nam, Thái Dương hãm thủ Mệnh hội Hóa Kỵ", "limit",
   [("life.hardship", A), ("fin.volatile", A)])
tt("tt66_vu_quyen_cat", MENH, [NAM, *M("Vũ Khúc"), H("Hóa Quyền"), STEM("Canh"), CAT(1)], "chí khí và tinh thần hơn người", "nam, Vũ Khúc hóa Quyền thủ Mệnh có cát tinh",
   "support", [("amb.drive", A)])
tt("tt66_vu_nhieu_sat", MENH, [NAM, *M("Vũ Khúc"), SAT(2)], "dù giàu có rồi cũng dễ lụn bại", "nam, Vũ Khúc thủ Mệnh bị nhiều sát tinh xung phá", "limit",
   [("fin.volatile", A)])
tt("tt67_dong_on_hoa", MENH, [NAM, *M("Thiên Đồng")], "tính tình ôn hòa, tử tế, có phúc lộc", "nam, Thiên Đồng thủ Mệnh", "support", [("values.kind", A)])
tt("tt67_dong_mieu_vuong", MENH, [NAM, *M("Thiên Đồng"), TTD("Thiên Đồng", ["miếu", "vượng"])], "không những có lộc mà còn có danh tiếng",
   "nam, Thiên Đồng miếu, vượng thủ Mệnh", "support", [("career.fame", A)])
tt("tt67_dong_cat", MENH, [NAM, *M("Thiên Đồng"), CAT(1)], "thông minh, lanh lợi, làm việc gì cũng dễ", "nam, Thiên Đồng thủ Mệnh gặp cát tinh", "support", [("cog.sharp", A)])
tt("tt67_dong_ham_hoa_da", MENH, [NAM, *M("Thiên Đồng"), TTD("Thiên Đồng", ["hãm"]), T("Hỏa Tinh"), T("Đà La")], "rất hung, chỉ nên an phận",
   "nam, Thiên Đồng hãm thủ Mệnh bị Hỏa Tinh, Đà La xung phá", "limit", [("life.hardship", A)])
tt("tt67_liem_ngang", MENH, [NAM, *M("Liêm Trinh")], "con người khác thường, chí khí mạnh, ưa ngang ngược", "nam, Liêm Trinh thủ Mệnh", "limit", [("temper.headstrong", A)])
tt("tt67_phu_quyen_loc_cat", MENH, [NAM, *M("Thiên Phủ"), has(TPH, "Hóa Quyền"), has(TPH, "Hóa Lộc"), T("Văn Xương"), T("Thiên Khôi"), T("Tả Phụ"), T("Hữu Bật")],
   "được dựa vào người quyền quý mà có chức tước", "nam, Thiên Phủ thủ Mệnh hội Quyền, Lộc, Xương, Khôi, Tả Hữu", "support", [("career.status", A), ("social.support", A)])
tt("tt67_phu_bon_sat", MENH, [NAM, *M("Thiên Phủ"), atleast(2, *[T(s) for s in SAT4])], "dễ gian trá, cuộc đời lận đận", "nam, Thiên Phủ thủ Mệnh bị Hỏa, Linh, Kình, Đà vây",
   "limit", [("values.integrity", W), ("life.hardship", A)])
tt("tt67_phu_khong_kiep", MENH, [NAM, *M("Thiên Phủ"), S("Địa Không"), S("Địa Kiếp")], "không hay, chỉ hưởng phúc nơi cửa thiền", "nam, Thiên Phủ đồng cung Không, Kiếp",
   "limit", [("spirit.unworldly", A)])
tt("tt68_am_dau_tuat_hoi", MENH, [NAM, *M("Thái Âm"), br("Dậu", "Tuất", "Hợi")], "sáng rực rỡ, có tiếng tăm", "nam, Thái Âm thủ Mệnh ở Dậu, Tuất, Hợi", "support",
   [("career.fame", A)])
tt("tt68_am_mieu_quyen", MENH, [NAM, *M("Thái Âm"), TTD("Thái Âm", ["miếu"]), H("Hóa Quyền"), STEM("Mậu")], "bẩm tính ôn lương, cung kiệm, khiêm nhường; dễ làm quan thanh hiển",
   "nam, Thái Âm nhập miếu hóa Quyền", "support", [("comm.gentle", A), ("career.status", A)])
tt("tt68_co_am_dan_xuong_khuc", MENH, [NAM, *M("Thiên Cơ", "Thái Âm"), br("Dần"), anyS("Văn Xương", "Văn Khúc")], "dù có sao tốt phù trợ cũng khó làm nên cơ nghiệp",
   "nam, Mệnh ở Dần có Thiên Cơ, Thái Âm gặp Xương Khúc", "limit", [("career.obstacle", A)], also=["tt147_pha_dan_co_xuong_khuc_nguyet"])
tt("tt68_vu_tham_liem_pha_kk", MENH, [NAM, *M("Vũ Khúc", "Tham Lang"), T("Liêm Trinh"), T("Phá Quân"), anyof(T("Địa Không"), T("Địa Kiếp"))],
   "nghề nào ra nghề nấy mà suốt đời vất vả", "nam, Tham Vũ thủ Mệnh lại ngộ Liêm, Phá, Không Kiếp", "limit", [("life.hardship", A)])
THAM_MO = [NAM, *M("Tham Lang"), br(*TU_MO), S("Tả Phụ"), S("Hữu Bật")]
tt("tt69_tham_tu_mo_ta_huu", MENH, THAM_MO, "thành phú ông", "nam, Tham Lang ở Tứ mộ gặp Tả Hữu", "support", [("fin.abundance", A)])
tt("tt69_tham_tu_mo_tam_hoa", MENH, THAM_MO + TH3, "tài năng văn võ đều đủ", "như trên, thêm Khoa, Quyền, Lộc", "support", [("exp.talent", A)])
tt("tt69_cu_ham_hung", MENH, [NAM, *M("Cự Môn"), TTD("Cự Môn", ["hãm"]), SAT(1)], "càng thêm tai họa, tính tình thô lỗ", "nam, Cự Môn hãm thủ Mệnh bị hung tinh phá",
   "limit", [("comm.friction", A)])
tt("tt69_cu_kinh_hoa_linh", MENH, [NAM, *M("Cự Môn"), S("Kình Dương"), anyS("Hỏa Tinh", "Linh Tinh")], "mọi việc dễ thành bất tường, tính nóng nảy, điên đảo",
   "nam, Cự Môn thủ Mệnh gặp Kình Dương và Linh, Hỏa", "limit", [("temper.hot", A)])
tt("tt69_tuong_ca_quyet", MENH, [NAM, *M("Thiên Tướng")], "là người quả quyết, tự chủ", "nam, Thiên Tướng thủ Mệnh", "support", [("temper.assertive", A)])
tt("tt69_tuong_vu_pha_sat", MENH, [NAM, *M("Thiên Tướng"), T("Vũ Khúc"), T("Phá Quân"), atleast(2, *[T(s) for s in SAT4])],
   "thiên về làm thợ, buôn bán, nếu không thì đi tu", "nam, Thiên Tướng gặp Vũ Khúc, Phá Quân và Kình Đà, Linh Hỏa", "limit", [("exp.craft", A), ("path.business", A)])
tt("tt70_luong_ta_huu_xuong_khuc", MENH, [NAM, *M("Thiên Lương"), T("Tả Phụ"), T("Hữu Bật"), T("Văn Xương"), T("Văn Khúc")], "làm quan, phú quý",
   "nam, Thiên Lương thủ Mệnh gặp Tả Hữu, Xương Khúc", "support", [("career.status", A)])
tt("tt70_luong_co_nhat_mieu", MENH, [NAM, *M("Thiên Lương"), br("Tý", "Ngọ", "Dần", "Thân"), T("Thiên Cơ"), T("Thái Dương"), T("Văn Xương"), T("Tả Phụ"), T("Hữu Bật")],
   "quan lộ thanh hiển", "nam, Thiên Lương ở Tý, Ngọ, Dần, Thân gặp Thiên Cơ, Thái Dương, Văn Xương, Tả Hữu", "support", [("career.status", A)])
tt("tt71_sat_dan_than_ty_ngo_cat", MENH, [NAM, *M("Thất Sát"), br("Dần", "Thân", "Tý", "Ngọ"), T("Thiên Khôi"), T("Thiên Việt"), T("Tả Phụ"), T("Hữu Bật")],
   "danh cao, giàu sang phú quý", "nam, Thất Sát ở Dần, Thân, Tý, Ngọ gặp Khôi Việt, Tả Hữu", "support", [("career.fame", A), ("fin.abundance", A)])
tt("tt71_sat_ham", MENH, [NAM, *M("Thất Sát"), TTD("Thất Sát", ["hãm"])], "hung họa nhiều, như ôm hổ mà ngủ", "nam, Thất Sát hãm thủ Mệnh", "limit", [("life.hardship", A)])
tt("tt71_pha_ty_ngo_xuong_ta_huu", MENH, [NAM, *M("Phá Quân"), br("Tý", "Ngọ"), T("Văn Xương"), T("Tả Phụ"), T("Hữu Bật")], "tính khảng khái, tiền bạc đầy kho",
   "nam, Phá Quân ở Tý, Ngọ gặp Văn Xương, Tả Hữu", "support", [("fin.abundance", A)])
tt("tt71_pha_doc_tam_hoa", MENH, [NAM, *alone("Phá Quân"), *TH3], "lại tốt dị thường", "nam, Phá Quân đơn thủ Mệnh có Khoa, Quyền, Lộc hội", "support",
   [("life.blessed", A), ("career.success", A)])
tt("tt71_pha_ham_sat", MENH, [NAM, *M("Phá Quân"), TTD("Phá Quân", ["hãm"]), SAT(1)], "dễ bỏ tổ nghiệp mà đi lập thân nơi xa", "nam, Phá Quân hãm thủ Mệnh gặp sát tinh",
   "limit", [("fortune.away", A)])
tt("tt72_xuong_vuong", MENH, [NAM, S("Văn Xương"), TTD("Văn Xương", ["miếu", "vượng"])], "chí lớn, tài cao, văn học tinh thông", "nam, Văn Xương thủ Mệnh ở vượng cung",
   "support", [("exp.letters", A), ("amb.drive", A)])
tt("tt72_khuc_ky_hoa", MENH, [NAM, S("Văn Khúc"), H("Hóa Kỵ"), S("Hỏa Tinh")], "là người biện thuyết tài giỏi", "nam, Văn Khúc thủ Mệnh ngộ Hóa Kỵ, Hỏa Tinh", "support",
   [("comm.persuasive", A)])
tt("tt72_ta_phu_don_hau", MENH, [NAM, S("Tả Phụ")], "là người đôn hậu, hiểu biết rộng", "nam, Tả Phụ thủ Mệnh", "support", [("values.kind", A)])
tt("tt72_ta_phu_bon_sat", MENH, [NAM, S("Tả Phụ"), atleast(2, *[T(s) for s in SAT4])], "dù tiền nhiều, chức trọng cũng không bền", "nam, Tả Phụ thủ Mệnh, tam phương Kình Đà Hỏa Linh chiếu",
   "limit", [("fortune.brief_luck", A)])
tt("tt73_huu_bat_co_muu", MENH, [NAM, S("Hữu Bật")], "người có cơ mưu, thông minh", "nam, Hữu Bật thủ Mệnh", "support", [("cog.sharp", A)])
tt("tt73_huu_bat_cat_khong_sat", MENH, [NAM, S("Hữu Bật"), nt(anyof(T("Hỏa Tinh"), has(TPH, "Hóa Kỵ"), T("Kình Dương"), T("Đà La"))), CAT(2)],
   "tiền tài, danh vọng dễ tìm", "nam, Hữu Bật thủ Mệnh không bị Hỏa, Kỵ, Kình, Đà xung phá mà có cát tinh phù trợ", "support", [("fin.abundance", A), ("career.success", A)])
tt("tt73_loc_ton_qua_quyet", MENH, [NAM, S("Lộc Tồn")], "tính quả quyết, làm việc gì cũng thành", "nam, Lộc Tồn thủ Mệnh", "support",
   [("temper.assertive", A), ("career.success", A)])
tt("tt73_loc_ton_xuong_khuc", MENH, [NAM, S("Lộc Tồn"), T("Văn Xương"), T("Văn Khúc")], "y lộc đầy đủ, nhà cao cửa rộng", "nam, Lộc Tồn thủ Mệnh có Xương Khúc hội",
   "support", [("prop.rich", A), ("fin.abundance", A)])
tt("tt73_loc_ton_co_kk_ky", MENH, [NAM, S("Lộc Tồn"), T("Thiên Cơ"), has(TPH, "Hóa Kỵ"), anyof(T("Địa Không"), T("Địa Kiếp"))], "chỉ hợp tìm thanh nhàn nơi cửa chùa",
   "nam, Lộc Tồn thủ Mệnh gặp Thiên Cơ, Không Kiếp, Kỵ", "limit", [("spirit.unworldly", A)])
tt("tt74_kinh_cung_ran", MENH, [NAM, S("Kình Dương")], "tính nết cứng rắn", "nam, Kình Dương thủ Mệnh", "limit", [("temper.headstrong", A)])
tt("tt74_kinh_tu_mo_tu_phu", MENH, [NAM, S("Kình Dương"), br(*TU_MO), T("Tử Vi"), T("Thiên Phủ")], "tiền tài, thóc gạo đầy kho", "nam, Kình Dương ở Tứ mộ có Tử Phủ hội hợp",
   "support", [("fin.abundance", A)])
tt("tt74_da_tu_mo_tu_phu", MENH, [NAM, S("Đà La"), br(*TU_MO), T("Tử Vi"), T("Thiên Phủ")], "tiền tài, danh vọng đều hay", "nam, Đà La ở Tứ mộ có Tử Vi, Thiên Phủ hội hợp",
   "support", [("fin.abundance", A), ("career.fame", A)])
tt("tt74_da_ham", MENH, [NAM, S("Đà La"), TTD("Đà La", ["hãm"])], "dễ vướng thị phi khẩu thiệt, làm gì cũng khó toại ý", "nam, Đà La hãm thủ Mệnh", "limit",
   [("comm.friction", A), ("life.hardship", A)])
tt("tt75_hoa_loc_menh", MENH, [NAM, H("Hóa Lộc")], "tự nhiên có phúc, theo văn hay võ đều dễ nổi danh", "nam, Hóa Lộc ở Mệnh", "support",
   [("life.blessed", A), ("career.fame", A)])
tt("tt75_loc_dong_nhat", MENH, [NAM, *M("Thiên Đồng"), H("Hóa Lộc"), STEM("Bính"), T("Thái Dương")], "người bình thường cũng thành đại phú, nhà cửa ruộng vườn hưng vượng",
   "nam, Thiên Đồng hóa Lộc gặp Thái Dương", "support", [("fin.abundance", A), ("prop.rich", A)])
tt("tt75_hoa_quyen_cat", MENH, [NAM, H("Hóa Quyền"), CAT(1)], "sự nghiệp hiên ngang, đảm lược hơn người", "nam, Hóa Quyền ở Mệnh có sao tốt phù trợ", "support",
   [("career.success", A), ("temper.assertive", A)])
tt("tt75_hoa_quyen_cu_vu", MENH, [NAM, H("Hóa Quyền"), T("Cự Môn"), T("Vũ Khúc")], "nắm quyền lớn, hợp võ nghiệp", "nam, Hóa Quyền ở Mệnh hội Cự Môn, Vũ Khúc", "support",
   [("career.authority", A), ("exp.martial", A)])
tt("tt76_hoa_khoa_van", MENH, [NAM, H("Hóa Khoa")], "văn chương giỏi, thi cử hanh thông", "nam, Hóa Khoa thủ Mệnh", "support", [("exp.letters", A)])
tt("tt76_hoa_khoa_xk_kv", MENH, [NAM, H("Hóa Khoa"), T("Văn Xương"), T("Văn Khúc"), T("Thiên Khôi"), T("Thiên Việt")], "công danh sáng lạn",
   "nam, Hóa Khoa ở Mệnh hội Xương Khúc, Khôi Việt", "support", [("career.fame", A)])
tt("tt76_hoa_ky_hung", MENH, [NAM, H("Hóa Kỵ"), SAT(1)], "càng thêm hung", "nam, Hóa Kỵ ở Mệnh gặp thêm hung tinh", "limit", [("life.hardship", A)])
tt("tt76_hoa_ky_cat_lo", MENH, [NAM, H("Hóa Kỵ"), CAT(1)], "dù có cát tinh trợ cứu mà giàu sang thì giàu sang ấy kèm nhiều lo lắng", "nam, Hóa Kỵ ở Mệnh có cát tinh trợ cứu",
   "limit", [("inner.unrest", A)])
tt("tt76_tham_pha_ham_ky", MENH, [NAM, H("Hóa Kỵ"), anyof(allof(has(OWNM, "Tham Lang"), TTD("Tham Lang", ["hãm"])), allof(has(OWNM, "Phá Quân"), TTD("Phá Quân", ["hãm"])))],
   "bất lợi", "nam, Tham Lang hoặc Phá Quân hãm thủ Mệnh gặp Hóa Kỵ", "limit", [("life.hardship", A)])
tt("tt76_hong_loan_bat_toa", MENH, [S("Hồng Loan"), S("Bát Tọa")], "có công danh từ khi còn trẻ", "Hồng Loan, Bát Tọa ở Mệnh", "support", [("career.early", A)])
tt("tt76_kinh_da_menh", MENH, [anyS("Kình Dương", "Đà La")], "nói năng hay loạn thuyết, điêu ngoa", "Kình Dương hoặc Đà La ở Mệnh", "limit", [("comm.friction", A)])

# ================= Toàn Thư: nữ mệnh (pp.113-118), women only =================
tt("tt113_tuong_nu_thong_minh", MENH, [NU, *M("Thiên Tướng")], "thông minh, giỏi giang, y lộc tiền bạc đầy đủ", "nữ, Thiên Tướng thủ Mệnh", "support",
   [("cog.sharp", A), ("fin.abundance", A)])
tt("tt114_sat_nu_thong_minh", MENH, [NU, *M("Thất Sát")], "rất lanh lợi, thông minh, dù đời nhiều gian lao", "nữ, Thất Sát thủ Mệnh", "support", [("cog.sharp", A)])
tt("tt114_pha_nu_ty_ngo", MENH, [NU, *M("Phá Quân"), br("Tý", "Ngọ")], "tính mạnh bạo hơn người, có tài năng, có tiếng tăm", "nữ, Phá Quân ở Tý, Ngọ", "support",
   [("temper.assertive", A), ("exp.talent", A)])
tt("tt115_xuong_nu_tu_phu", MENH, [NU, S("Văn Xương"), T("Tử Vi"), T("Thiên Phủ")], "phú quý", "nữ, Văn Xương thủ Mệnh có Tử Vi, Thiên Phủ tam hợp chiếu", "support",
   [("fin.abundance", A)])
tt("tt115_khuc_nu_thong_minh", MENH, [NU, S("Văn Khúc")], "thông minh, lanh lợi khác người", "nữ, Văn Khúc thủ Mệnh", "support", [("cog.sharp", A)])
tt("tt115_ta_huu_nu", MENH, [NU, anyS("Tả Phụ", "Hữu Bật")], "hiền lương, giỏi giang, quán xuyến", "nữ, Tả Phụ hoặc Hữu Bật ở Mệnh", "support",
   [("values.kind", A), ("exp.talent", A)])
tt("tt115_ta_huu_nu_tu_phu", MENH, [NU, anyS("Tả Phụ", "Hữu Bật"), T("Tử Vi"), T("Thiên Phủ")], "phúc lộc dồi dào", "nữ, Tả Hữu ở Mệnh có Tử Vi, Thiên Phủ hợp", "support",
   [("life.blessed", A)])
tt("tt116_ma_menh_ton_di", MENH, [NU, S("Thiên Mã"), ref("Thiên Di", OWN, "Lộc Tồn")], "có tài buôn bán, nhiều bề giỏi giắn", "nữ, Thiên Mã ở Mệnh, Lộc Tồn ở Thiên Di",
   "support", [("path.business", A)])
tt("tt116_kinh_nu_hoa_co_cu", MENH, [NU, S("Kình Dương"), T("Hỏa Tinh"), T("Thiên Cơ"), T("Cự Môn")], "đời tầm thường", "nữ, Kình Dương thủ Mệnh gặp Hỏa Tinh, Thiên Cơ, Cự Môn",
   "limit", [("life.blessed", W)])
tt("tt117_hoa_linh_nu_tham", MENH, [NU, anyS("Hỏa Tinh", "Linh Tinh"), T("Tham Lang"), TPR("Tham Lang", "gte", 2), {"fact": "palace.khi.sat_tp", "operator": "lte", "value": 1}],
   "hạnh phúc, giàu sang", "nữ, Hỏa hoặc Linh thủ Mệnh hội Tham Lang đắc địa, tam phương không sát tinh khác", "support", [("life.blessed", A), ("fin.abundance", A)])
tt("tt117_hoa_quyen_nu_cat", MENH, [NU, H("Hóa Quyền"), CAT(1)], "phú quý song toàn", "nữ, Hóa Quyền ở Mệnh thêm cát tinh", "support",
   [("fin.abundance", A), ("career.status", A)])
tt("tt117_hoa_khoa_nu", MENH, [NU, H("Hóa Khoa")], "đức độ, tính tình thanh cao", "nữ, Hóa Khoa ở Mệnh", "support", [("values.integrity", A)])
tt("tt117_hoa_ky_nu_hung", MENH, [NU, H("Hóa Kỵ"), SAT(1)], "cuộc sống cơ cực, túng thiếu", "nữ, Hóa Kỵ ở Mệnh lại thêm hung tinh xung phá", "limit",
   [("fin.scarcity", A), ("life.hardship", A)])
tt("tt118_liem_nu_thanh_bach", MENH, [NU, *M("Liêm Trinh"), nt(TTD("Liêm Trinh", ["hãm"]))], "bản chất thanh bạch", "nữ, Liêm Trinh thủ Mệnh không hãm", "support",
   [("values.integrity", A)])
tt("tt118_tu_nhat_nu_trung_thuc", MENH, [NU, anyM("Tử Vi", "Thái Dương")], "tính nết trung thực", "nữ, Tử Vi hoặc Thái Dương thủ Mệnh", "support", [("values.integrity", A)])
tt("tt118_nhat_dan_ngo_cat", MENH, [NU, *M("Thái Dương"), br("Dần", "Mão", "Thìn", "Tỵ", "Ngọ"), CAT(1)], "hưởng phúc", "nữ, Thái Dương ở Dần đến Ngọ có cát tinh phù trợ",
   "support", [("life.blessed", A)])
tt("tt118_huu_tuong_nu", MENH, [NU, S("Hữu Bật"), *M("Thiên Tướng")], "phúc thường đến", "nữ, Hữu Bật, Thiên Tướng ở Mệnh", "support", [("life.blessed", A)])
tt("tt118_loc_ton_nu", MENH, [NU, S("Lộc Tồn")], "đầy đủ cơm áo", "nữ, Lộc Tồn ở Mệnh", "support", [("fin.abundance", A)])
tt("tt118_co_cu_nu", MENH, [NU, *M("Thiên Cơ", "Cự Môn")], "dù đắc địa cuối cùng cũng dễ phá tán", "nữ, Thiên Cơ, Cự Môn ở Mệnh", "limit", [("fin.volatile", A)])
tt("tt118_xuong_khuc_nu", MENH, [NU, anyS("Văn Xương", "Văn Khúc")], "phúc không trọn", "nữ, Văn Xương hoặc Văn Khúc ở Mệnh", "limit", [("life.blessed", W)])
tt("tt118_vu_nu_co_doc", MENH, [NU, *M("Vũ Khúc")], "Vũ Khúc là sao cô độc", "nữ, Vũ Khúc thủ Mệnh", "limit", [("social.isolated", A)])
tt("tt118_sat_nu_don", MENH, [NU, *alone("Thất Sát")], "không phải là phúc", "nữ, Thất Sát đơn thủ Mệnh", "limit", [("life.blessed", W)])
tt("tt118_song_loc_nu", MENH, [NU, T("Lộc Tồn"), has(TPH, "Hóa Lộc")], "giàu sang, có chức tước", "nữ, song Lộc thủ chiếu Mệnh", "support",
   [("fin.abundance", A), ("career.status", A)])

# ================= Toàn Thư: phú nôm Tật Ách / Huynh Đệ / Tử Tức (pp.91-93) =================
tt("tt91_tat_tuan_triet", TA, [anyof(TUAN, TRIET)], "có Tuần Triệt giải được tai nạn", "Tuần hoặc Triệt ở Tật Ách", "support", [("health.shielded", A)])
tt("tt91_bao_kk_don_so", HD, [anyS("Địa Không", "Địa Kiếp")], "anh em ít, lẻ loi", "Địa Không hoặc Địa Kiếp ở Huynh Đệ", "limit", [("kin.few", A)])
tt("tt92_bao_pha_hinh_ky", HD, [*M("Phá Quân"), S("Thiên Hình"), H("Hóa Kỵ")], "anh em bất thuận, nhiều đường tranh nhau", "Phá Quân gặp Thiên Hình, Hóa Kỵ ở Huynh Đệ",
   "limit", [("kin.strain", A)])
tt("tt92_bao_tuong_quan_loc_ma", HD, [S("Tướng Quân"), S("Thiên Mã"), anyof(S("Lộc Tồn"), H("Hóa Lộc"))], "anh em có người quyền quý",
   "Tướng Quân, Lộc, Thiên Mã đồng cung ở Huynh Đệ", "support", [("kin.talented", A)])
tt("tt92_tu_hinh_hao", TU, [S("Thiên Hình"), anyS("Đại Hao", "Tiểu Hao")], "hiếm con", "Thiên Hình gặp Hao ở Tử Tức", "limit", [("kin.few", A)])
tt("tt92_tu_truong_sinh_de_vuong", TU, [anyS("Trường Sinh", "Đế Vượng")], "đông con", "Trường Sinh hoặc Đế Vượng ở Tử Tức", "support", [("kin.many", A)])
tt("tt93_tu_da_ky", TU, [S("Đà La"), H("Hóa Kỵ")], "hiếm con", "Đà La, Hóa Kỵ ở Tử Tức", "limit", [("kin.few", A)])
tt("tt93_tu_quyen_loc", TU, [H("Hóa Quyền"), H("Hóa Lộc")], "con cái hiển vinh", "Hóa Quyền, Hóa Lộc ở Tử Tức", "support", [("kin.talented", A)])
tt("tt93_tu_khoi_viet_van", TU, [anyS("Thiên Khôi", "Thiên Việt"), anyS("Văn Xương", "Văn Khúc")], "con cái học hành đỗ đạt cao", "Khôi Việt và văn tinh ở Tử Tức",
   "support", [("kin.talented", A)])
tt("tt93_tu_long_phuong", TU, [S("Long Trì"), S("Phượng Các")], "con cái sang giàu", "Long Trì, Phượng Các ở Tử Tức", "support", [("kin.prosper", A)])
tt("tt93_tu_xuong_khuc", TU, [anyS("Văn Xương", "Văn Khúc")], "con cái dễ thành người ham ăn chơi", "Văn Xương hoặc Văn Khúc ở Tử Tức", "limit", [("kin.wayward", A)])
tt("tt93_tu_sat_ham_hinh", TU, [*M("Thất Sát"), TTD("Thất Sát", ["hãm"]), S("Thiên Hình")], "con cái dễ ngang tàng, phóng đãng", "Thất Sát hãm gặp Thiên Hình ở Tử Tức",
   "limit", [("kin.wayward", A)])

# ================= Toàn Thư: cách cục (pp.141-143) — formation rules =================
tt("tt142_nhat_nguyet_hiep_tai", MENH, [*M("Vũ Khúc"), giap("Thái Dương", "Thái Âm")], "cách Nhật Nguyệt hiệp tài, một phú cách", "Vũ Khúc thủ Mệnh, Nhật Nguyệt giáp Mệnh",
   "support", [("fin.abundance", A)], kind="+")
tt("tt142_nn_chieu_bich", "Điền Trạch", [*M("Thái Dương", "Thái Âm")], "cách Nhật Nguyệt chiếu bích ở Điền Trạch, một phú cách", "Nhật Nguyệt ở Điền Trạch", "support",
   [("prop.rich", A)], kind="+")
tt("tt142_nhat_xuat_phu_tang_quan", "Quan Lộc", [*M("Thái Dương"), br("Mão")], "cách Nhật xuất phù tang ở Quan Lộc, một quý cách", "Thái Dương ở Mão thủ Quan Lộc",
   "support", [("career.status", A)], kind="+")
tt("tt142_nguyet_sinh_suong_hai", "Điền Trạch", [*M("Thái Âm"), br("Tý")], "cách Nguyệt sinh thương hải ở Điền Trạch, một quý cách", "Thái Âm ở Tý thủ Điền Trạch",
   "support", [("prop.rich", A)], kind="+")
tt("tt142_quan_than_khanh_hoi", MENH, [*M("Tử Vi"), S("Tả Phụ"), S("Hữu Bật"), T("Vũ Khúc"), T("Thiên Tướng")], "cách Quân thần khánh hội, một quý cách",
   "Tử Vi, Tả Hữu cùng ở Mệnh, Vũ Khúc, Thiên Tướng chiếu", "support", [("career.status", A), ("social.support", A)], kind="+")
tt("tt142_hinh_tu_hiep_an", MENH, [*M("Thiên Tướng", "Liêm Trinh"), S("Thiên Hình")], "cách Hình tù hiệp ấn, quý về võ nghiệp", "Thiên Tướng thủ Mệnh có Thiên Hình, Liêm Trinh",
   "support", [("exp.martial", A), ("career.status", A)], kind="+")
tt("tt143_quan_tu_tai_da", MENH, [atleast(2, *[S(s) for s in SAT4]), anyof(*[allof(has(OWNM, s), TTD(s, ["hãm"])) for s in MAJORS])],
   "cách Quân tử tại dã, một bần tiện cách: như người quân tử phải lang thang", "Mệnh có Tứ Sát, chính tinh hãm", "limit", [("life.hardship", A)], kind="-")
tt("tt143_nhat_sinh_co_ban", MENH, [*M("Phá Quân"), TTD("Phá Quân", ["hãm"])], "cách Nhất sinh cô bần, một bần tiện cách", "Phá Quân hãm thủ Mệnh", "limit",
   [("fin.scarcity", A), ("social.isolated", A)], kind="-")
tt("tt143_luong_trung_hoa_cai", MENH, [S("Lộc Tồn"), H("Hóa Lộc"), anyS("Địa Không", "Địa Kiếp")], "cách Lưỡng trùng Hoa Cái, một bần tiện cách", "Lộc Tồn, Hóa Lộc ở Mệnh gặp Không Kiếp",
   "limit", [("fin.volatile", A)], kind="-")

# ================= Toàn Thư: hợp cách / phá cách theo cung Mệnh (pp.143-149) =================
tt("tt143_hop_ty", MENH, [br("Tý"), anyM("Tham Lang", "Thất Sát", "Thái Âm"), T("Thiên Cơ"), T("Thiên Lương"), STEM("Canh", "Tân", "Ất", "Quý")], "suốt đời phú quý, hạnh phúc",
   "Mệnh ở Tý có Tham Lang, Thất Sát hoặc Thái Âm, Cơ Lương củng chiếu, tuổi Canh, Tân, Ất, Quý", "support", [("fin.abundance", A), ("life.blessed", A)])
tt("tt144_hop_dan", MENH, [br("Dần"), anyof(allof(*M("Cự Môn", "Thái Dương")), has(OWNM, "Thất Sát"), has(OWNM, "Thiên Lương")), anyof(YB("Thân", "Tỵ"), STEM("Canh"))],
   "việc gì cũng thông suốt", "Mệnh ở Dần có Cự Nhật, hoặc Thất Sát, Thiên Lương, tuổi Thân, Tỵ hoặc Canh", "support", [("career.success", A)])
tt("tt144_hop_mao", MENH, [br("Mão"), anyof(allof(*M("Cự Môn", "Thiên Cơ")), has(OWNM, "Vũ Khúc")), STEM("Tân", "Ất")], "nhiều phúc lộc, giàu sang",
   "Mệnh ở Mão có Cự Cơ hoặc Vũ Khúc, tuổi Tân, Ất", "support", [("life.blessed", A), ("fin.abundance", A)])
tt("tt144_hop_ty", MENH, [br("Tỵ"), anyM("Thiên Cơ", "Thiên Tướng", "Tử Vi"), STEM("Mậu", "Tân", "Nhâm", "Bính")], "tốt phúc, dễ toại ý, ít tai họa",
   "Mệnh ở Tỵ có Thiên Cơ, Thiên Tướng hoặc Tử Vi, tuổi Mậu, Tân, Nhâm, Bính", "support", [("life.blessed", A)])
tt("tt144_hop_ngo", MENH, [br("Ngọ"), anyM("Tử Vi", "Thái Dương", "Thất Sát", "Phá Quân"), STEM("Giáp", "Đinh", "Kỷ", "Quý")], "làm lớn, bổng lộc dồi dào",
   "Mệnh ở Ngọ có Tử Vi, Thái Dương, Thất Sát hoặc Phá Quân, tuổi Giáp, Đinh, Kỷ, Quý", "support", [("career.status", A)])
tt("tt145_hop_than", MENH, [br("Thân"), anyM("Tử Vi", "Liêm Trinh", "Thiên Lương", "Vũ Khúc", "Cự Môn"), STEM("Giáp", "Canh", "Quý")], "được phú quý, thỏa chí",
   "Mệnh ở Thân có Tử Vi, Liêm Trinh, Thiên Lương, Vũ Khúc hoặc Cự Môn, tuổi Giáp, Canh, Quý", "support", [("fin.abundance", A), ("career.success", A)])
tt("tt145_hop_dau", MENH, [br("Dậu"), *M("Thái Âm")], "cực tốt", "Mệnh ở Dậu có Thái Âm", "support", [("life.blessed", A)])
tt("tt147_pha_co_ty_ngo_cu_linh", MENH, [anyof(allof(br("Tý", "Ngọ"), has(OWNM, "Thiên Cơ")), allof(br("Sửu"), has(OWNM, "Cự Môn"), S("Linh Tinh")))],
   "phá cách: dù có cát tinh mà phú quý cũng chẳng bền", "Mệnh ở Tý, Ngọ có Thiên Cơ, hoặc ở Sửu có Cự Môn, Linh Tinh", "limit", [("fortune.brief_luck", A)])
tt("tt147_pha_mao_am_kinh", MENH, [br("Mão"), *M("Thái Âm"), S("Kình Dương")], "phá cách: dù hóa cát cũng không toàn mỹ", "Mệnh ở Mão có Thái Âm gặp Kình Dương", "limit",
   [("life.blessed", W)])
tt("tt147_pha_thin_cu_tu", MENH, [br("Thìn"), anyM("Cự Môn", "Tử Vi")], "phá cách: dù hóa cát cũng không toàn mỹ", "Mệnh ở Thìn có Cự Môn hoặc Tử Vi", "limit", [("life.blessed", W)])
tt("tt147_pha_ty", MENH, [br("Tỵ"), anyM("Vũ Khúc", "Thái Âm", "Thiên Lương", "Cự Môn", "Tham Lang", "Liêm Trinh")], "phá cách: dù cát tinh chiếu cũng vô ích, đời vất vả thiếu thốn",
   "Mệnh ở Tỵ có Vũ Khúc, Thái Âm, Thiên Lương, Cự Môn, Tham Lang hoặc Liêm Trinh", "limit", [("fin.scarcity", A), ("life.hardship", A)])
tt("tt147_pha_ngo_kinh", MENH, [br("Ngọ"), anyof(has(OWNM, "Tham Lang"), has(OWNM, "Cự Môn"), has(OWNM, "Thái Âm"), S("Văn Xương")), T("Kình Dương")],
   "phá cách: hoạnh thành hoạnh phá, khó lâu bền", "Mệnh ở Ngọ có Tham, Cự, Thái Âm hoặc Văn Xương, Kình Dương xung", "limit", [("fin.volatile", A)])
tt("tt148_pha_mui", MENH, [br("Mùi"), anyM("Cự Môn", "Thái Dương")], "phá cách: vất vả bôn ba, chìm nổi, hay rắc rối quan tụng", "Mệnh ở Mùi có Cự Môn hoặc Thái Dương", "limit",
   [("life.hardship", A), ("life.legal", A)])
tt("tt148_pha_than_nam", MENH, [NAM, br("Thân"), anyM("Cự Môn", "Thiên Cơ")], "phá cách: dễ phiêu bạt", "nam, Mệnh ở Thân có Cự Môn hoặc Thiên Cơ", "limit", [("life.transient", A)])
tt("tt148_pha_than_nu", MENH, [NU, br("Thân"), anyM("Cự Môn", "Thiên Cơ")], "phá cách: dễ túng thiếu", "nữ, Mệnh ở Thân có Cự Môn hoặc Thiên Cơ", "limit", [("fin.scarcity", A)])
tt("tt148_pha_tuat", MENH, [br("Tuất"), anyM("Tử Vi", "Phá Quân", "Thiên Đồng", "Thái Dương")], "phá cách: chủ hung, vất vả thiếu thốn",
   "Mệnh ở Tuất có Tử Vi, Phá Quân, Thiên Đồng hoặc Thái Dương", "limit", [("life.hardship", A)])
tt("tt149_tham_hoa_loc_tu_mo", MENH, [br(*TU_MO), *M("Tham Lang"), H("Hóa Lộc"), STEM("Mậu")], "dù gặp cát tinh cũng chỉ trung bình", "Tham Lang hóa Lộc ở Tứ mộ", "limit",
   [("life.blessed", W)])

# ================= Khảo Luận: hạ cách / kỳ cách (pp.46-47, formation rules) and the special stars (pp.202-206) =================
kl("kl46_nn_tang_hung", MENH, [T("Thái Dương"), T("Thái Âm"), TPR("Thái Dương", "lte", 0), TPR("Thái Âm", "lte", 0)], "cách Nhật Nguyệt tàng hung, một hạ cách: trời đất tối tăm",
   "Thái Dương, Thái Âm hãm địa thủ hoặc chiếu Mệnh", "limit", [("life.hardship", A)], kind="-")
kl("kl46_phu_ngo_tuan", MENH, [*M("Thiên Phủ"), TUAN], "cách Thiên phủ ngộ Tuần, một hạ cách: kho tàng trống rỗng", "Thiên Phủ thủ Mệnh gặp Tuần", "limit", [("fin.scarcity", A)],
   kind="-")
kl("kl47_de_ngo_hung_do", MENH, [*M("Tử Vi", "Thiên Phủ"), anyS("Địa Không", "Địa Kiếp")], "cách Đế ngộ hung đồ, một hạ cách: dễ táng gia bại sản",
   "Tử Phủ thủ Mệnh gặp Không Kiếp đồng cung", "limit", [("fin.volatile", A)], kind="-")
kl("kl47_khong_kiep_ty_hoi", MENH, [br("Tỵ", "Hợi"), S("Địa Không"), S("Địa Kiếp")], "cách Không Kiếp Tỵ Hợi, một kỳ cách: bạo phát bạo tàn", "Mệnh ở Tỵ, Hợi có Không Kiếp thủ",
   "limit", [("fin.volatile", A)], kind="-")
# Thiên Không and Đào Hoa always stand in one tam hợp group (the year's): the pair is read together, in Mệnh or in one tam hợp palace
pair_in = lambda f: allof(has(f, "Thiên Không"), has(f, "Đào Hoa"))
kl("kl47_dao_hoa_thien_khong", MENH, [anyof(pair_in(OWN), pair_in("palace.rel.trine1_stars"), pair_in("palace.rel.trine2_stars"))],
   "cách Đào hoa Thiên không, một kỳ cách: có danh thì nghèo, lên voi xuống chó", "Thiên Không, Đào Hoa ở Mệnh hoặc tam hợp chiếu", "limit", [("fin.volatile", A)], kind="-")
kl("kl202_khoc_hu_ty_ngo", MENH, [br("Tý", "Ngọ"), S("Thiên Khốc"), S("Thiên Hư")], "cách Khốc Hư Tý Ngọ: thuở đầu chưa thuận, về sau mới thành và khá lên", "Khốc Hư ở Mệnh tại Tý, Ngọ", "support",
   [("life.late_bloom", A)], kind="+")
# Đại Hao and Tiểu Hao always face each other (Lộc Tồn ring +9 / +3): 'Song Hao ở X' is the pair on X's axis, one of them in X
SH = [anyS("Đại Hao", "Tiểu Hao")]
kl("kl203_song_hao_menh", MENH, [*SH, nt(br("Dần", "Thân", "Mão", "Dậu"))], "cách Song Hao ở Mệnh: hao tán, hay thay đổi công việc", "Song Hao ở Mệnh, một Hao ở Mệnh, một ở Thiên Di, ngoài Dần Thân Mão Dậu", "limit",
   [("fin.volatile", A)], kind="-")
kl("kl203_song_hao_dan_than_mao_dau", MENH, [*SH, br("Dần", "Thân", "Mão", "Dậu")], "cách Song Hao Dần Thân Mão Dậu: hoạnh phá nhưng cũng hoạnh phát", "Song Hao ở Mệnh tại Dần, Thân, Mão, Dậu", "support",
   [("fin.windfall", A), ("fin.volatile", A)], kind="+")
SH_MIEU = anyof(allof(S("Đại Hao"), dig("khao_luan", "Đại Hao", ["miếu"])), allof(S("Tiểu Hao"), dig("khao_luan", "Tiểu Hao", ["miếu"])))
kl("kl203_song_hao_tai_mieu", "Tài Bạch", [*SH, SH_MIEU], "tiền bạc hoạnh phá, hoạnh phát", "Song Hao miếu địa ở Tài Bạch", "support", [("fin.windfall", A), ("fin.volatile", A)])
kl("kl203_song_hao_tai_khong_cu", "Tài Bạch", [*SH, nt(has(OWNM, "Cự Môn")), nt(SH_MIEU)], "tiền bạc chỉ có hao tán", "Song Hao ở Tài Bạch không có Cự Môn đồng cung",
   "limit", [("fin.volatile", A)])
kl("kl203_tuan_triet_mieu", MENH, [anyof(allof(TRIET, br("Thân", "Dậu")), allof(TUAN, br("Dần", "Mão")))], "cách Tuần Triệt miếu địa: Mệnh lại khá",
   "Triệt ở Mệnh tại Thân, Dậu hoặc Tuần ở Mệnh tại Dần, Mão", "support", [("life.mitigated", A)], kind="+")
kl("kl204_menh_triet", MENH, [TRIET], "thuở nhỏ chịu nhiều khó khăn", "Mệnh gặp Triệt", "limit", [("life.early_hardship", A)])
kl("kl204_menh_tuan", MENH, [TUAN], "luôn bị kìm hãm, trục trặc ngay khi bắt tay vào việc", "Mệnh gặp Tuần", "limit", [("career.obstacle", A)])
kl("kl204_vcd_khong_kiep", MENH, [VCD, br("Dần", "Thân", "Tỵ", "Hợi"), anyof(allof(S("Địa Không"), S("Địa Kiếp")), allof(has(OPP, "Địa Không"), has(OPP, "Địa Kiếp")))],
   "làm việc liều mạng, bất chấp hiểm nguy, tìm đường sống trong chỗ chết", "Mệnh vô chính diệu ở Dần Thân Tỵ Hợi có Không Kiếp đồng cung hay xung chiếu", "limit",
   [("temper.reckless", A)])
kl("kl205_giap_long_phuong", MENH, [giap("Long Trì", "Phượng Các")], "cách Long Phượng giáp Mệnh: vinh quang", "Long Trì, Phượng Các giáp Mệnh", "support", [("career.fame", A)], kind="+")
kl("kl205_giap_kinh_da", MENH, [giap("Kình Dương", "Đà La")], "cách Kình Đà giáp Mệnh: gian nan vất vả", "Kình Dương, Đà La giáp Mệnh", "limit", [("life.hardship", A)], kind="-")
kl("kl205_giap_kiep_khong", MENH, [giap("Địa Không", "Địa Kiếp")], "cách Không Kiếp giáp Mệnh: cuộc đời dễ tàn tạ", "Địa Không, Địa Kiếp giáp Mệnh", "limit", [("life.hardship", A)], kind="-")
kl("kl206_vcd_ta_huu_nhat_nguyet", MENH, [VCD, S("Tả Phụ"), S("Hữu Bật"), T("Thái Dương"), T("Thái Âm"), TPR("Thái Dương", "gte", 2), TPR("Thái Âm", "gte", 2)],
   "thông minh tài giỏi, được mọi người kính phục", "Mệnh vô chính diệu có Tả Hữu đồng cung, Nhật Nguyệt đắc địa hợp chiếu", "support", [("cog.sharp", A), ("social.support", A)])
kl("kl206_vcd_sat_dac_tam_hoa", MENH, [VCD, anyof(*[allof(S(s), RANK(s, "gte", 2)) for s in SAT6]), *TH3], "mở mày mở mặt với đời",
   "Mệnh vô chính diệu có sát tinh đắc địa, Khoa Quyền Lộc tam hợp chiếu", "support", [("career.success", A)])

# ================= 紫微斗數全書 卷二 (Toàn Thư Hán văn): 兄弟, 子女, 奴仆, 父母 =================
any6 = lambda: anyS(*SAT6)
mm = lambda star, *lv: [has(OWNM, star), TTD(star, list(lv))]
qs("w2_bao_tu_sat", HD, [*M("Tử Vi"), any6()], "anh em kém hòa thuận", "Tử Vi ở Huynh Đệ gặp sát tinh", "limit", [("kin.strain", A)])
qs("w2_bao_co_ham", HD, mm("Thiên Cơ", "hãm"), "anh em không cùng một lòng", "Thiên Cơ hãm ở Huynh Đệ", "limit", [("kin.strain", A)])
qs("w2_bao_nhat_ham", HD, mm("Thái Dương", "hãm"), "anh em không hòa, ít giúp được nhau", "Thái Dương hãm ở Huynh Đệ", "limit", [("kin.strain", A)])
qs("w2_bao_vu_khong_hop", HD, mm("Vũ Khúc", "miếu", "vượng"), "anh em không hợp nhau", "Vũ Khúc miếu, vượng ở Huynh Đệ", "limit", [("kin.strain", A)])
qs("w2_bao_vu_pha_sat", HD, [*M("Vũ Khúc"), anyM("Phá Quân", "Thất Sát")], "anh em không hòa thuận", "Vũ Khúc đồng cung Phá Quân hoặc Thất Sát ở Huynh Đệ", "limit",
   [("kin.strain", A)])
qs("w2_bao_dong_sat_ky", HD, [*M("Thiên Đồng"), anyof(any6(), H("Hóa Kỵ"))], "anh em nên ở riêng, không hòa", "Thiên Đồng ở Huynh Đệ gặp sát tinh hoặc Hóa Kỵ", "limit",
   [("kin.apart", A), ("kin.strain", A)])
qs("w2_bao_liem_tham", HD, M("Liêm Trinh", "Tham Lang"), "anh em sinh oán", "Liêm Trinh, Tham Lang ở Huynh Đệ", "limit", [("kin.strain", A)])
qs("w2_bao_cu_ham", HD, mm("Cự Môn", "hãm"), "anh em nên ở riêng", "Cự Môn hãm ở Huynh Đệ", "limit", [("kin.apart", A)])
qs("w2_bao_cu_co", HD, M("Cự Môn", "Thiên Cơ"), "anh em trái ý, không cùng lòng", "Cự Môn, Thiên Cơ ở Huynh Đệ", "limit", [("kin.strain", A)])
qs("w2_bao_luong_mieu", HD, mm("Thiên Lương", "miếu", "vượng"), "anh em hòa thuận", "Thiên Lương miếu, vượng ở Huynh Đệ", "support", [("kin.harmony", A)])
qs("w2_bao_that_sat", HD, M("Thất Sát"), "anh em không hòa, nên mỗi người một nơi", "Thất Sát ở Huynh Đệ", "limit", [("kin.strain", A), ("kin.apart", A)])
qs("w2_bao_pha_xuong_khuc", HD, [*M("Phá Quân"), anyS("Văn Xương", "Văn Khúc", "Tả Phụ", "Hữu Bật")], "anh em hòa thuận", "Phá Quân ở Huynh Đệ có Xương Khúc, Tả Hữu",
   "support", [("kin.harmony", A)])
qs("w2_bao_ta_huu_kk", HD, [anyS("Tả Phụ", "Hữu Bật"), anyS("Địa Không", "Địa Kiếp")], "anh em ít giúp được nhau, không hòa", "Tả Phụ hoặc Hữu Bật ở Huynh Đệ gặp Không Kiếp",
   "limit", [("kin.strain", A)])
qs("w2_bao_loc_ton_sat", HD, [S("Lộc Tồn"), any6()], "anh em sinh oán", "Lộc Tồn ở Huynh Đệ gặp sát tinh", "limit", [("kin.strain", A)])
qs("w2_tu_tu_phu_cat", TU, [*M("Tử Vi", "Thiên Phủ"), anyS("Văn Xương", "Văn Khúc", "Tả Phụ", "Hữu Bật")], "có con quý hiển", "Tử Phủ ở Tử Tức có Xương Khúc, Tả Hữu",
   "support", [("kin.talented", A)])
qs("w2_tu_liem_phu", TU, M("Liêm Trinh", "Thiên Phủ"), "có con quý hiển", "Liêm Trinh, Thiên Phủ ở Tử Tức", "support", [("kin.talented", A)])
qs("w2_tu_am_mieu", TU, mm("Thái Âm", "miếu", "vượng"), "có con quý hiển", "Thái Âm miếu, vượng ở Tử Tức", "support", [("kin.talented", A)])
qs("w2_tu_am_ham", TU, mm("Thái Âm", "hãm"), "con cái dễ yếu đuối, khó thành người", "Thái Âm hãm ở Tử Tức", "limit", [("kin.adverse", A)])
qs("w2_tu_sat_sat", TU, [*M("Thất Sát"), any6()], "con cái dễ ngang tàng, phá gia", "Thất Sát ở Tử Tức gặp sát tinh", "limit", [("kin.wayward", A)])
qs("w2_tu_ta_phu_tu_phu", TU, [S("Tả Phụ"), anyM("Tử Vi", "Thiên Phủ")], "có con quý hiển", "Tả Phụ ở Tử Tức gặp Tử Vi, Thiên Phủ", "support", [("kin.talented", A)])
qs("w2_tu_ta_phu_sat", TU, [S("Tả Phụ"), anyof(anyM("Phá Quân", "Thất Sát"), any6())], "con cái khó thành người", "Tả Phụ ở Tử Tức gặp Phá Quân, Thất Sát hoặc sát tinh",
   "limit", [("kin.adverse", A)])
qs("w2_tu_huu_bat_cat", TU, [S("Hữu Bật"), anyS("Tả Phụ", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt")], "có con quý hiển", "Hữu Bật ở Tử Tức thêm cát tinh", "support",
   [("kin.talented", A)])
qs("w2_tu_khoi_viet", TU, [VCD, anyS("Thiên Khôi", "Thiên Việt")], "có con quý hiển", "Khôi hoặc Việt đơn thủ Tử Tức", "support", [("kin.talented", A)])
qs("w2_no_tu_vi", NO, M("Tử Vi"), "người dưới giúp được việc", "Tử Vi ở Nô Bộc", "support", [("ally.helpful", A)])
qs("w2_no_tu_vi_sat", NO, [*M("Tử Vi"), anyS("Kình Dương", "Hỏa Tinh", "Linh Tinh", "Đà La")], "người dưới ít giúp được việc", "Tử Vi ở Nô Bộc gặp Kình, Đà, Hỏa, Linh", "limit",
   [("ally.weak", A)])
qs("w2_no_tu_tuong_kk", NO, [*M("Tử Vi", "Thiên Tướng"), anyS("Địa Không", "Địa Kiếp")], "người dưới sinh oán rồi bỏ đi", "Tử Tướng ở Nô Bộc gặp Không Kiếp", "limit",
   [("ally.resent", A), ("ally.fickle", A)])
qs("w2_no_co_mieu", NO, mm("Thiên Cơ", "miếu"), "người dưới giúp được việc", "Thiên Cơ miếu ở Nô Bộc", "support", [("ally.helpful", A)])
qs("w2_no_co_ham", NO, mm("Thiên Cơ", "hãm"), "người dưới oán chủ", "Thiên Cơ hãm ở Nô Bộc", "limit", [("ally.resent", A)])
qs("w2_no_nhat_mieu", NO, mm("Thái Dương", "miếu"), "người dưới làm được việc, chủ nhờ đó phát đạt", "Thái Dương miếu ở Nô Bộc", "support", [("ally.helpful", A)])
qs("w2_no_nhat_ham", NO, mm("Thái Dương", "hãm"), "ít người dưới, có cũng oán chủ và bỏ đi", "Thái Dương hãm ở Nô Bộc", "limit", [("ally.resent", A), ("ally.fickle", A)])
qs("w2_no_vu_vuong", NO, mm("Vũ Khúc", "miếu", "vượng"), "người dưới đông, một tiếng gọi trăm người dạ", "Vũ Khúc miếu, vượng ở Nô Bộc", "support", [("ally.many", A)])
qs("w2_no_vu_phu", NO, M("Vũ Khúc", "Thiên Phủ"), "nhiều người giúp việc", "Vũ Khúc, Thiên Phủ ở Nô Bộc", "support", [("ally.many", A)])
qs("w2_no_vu_pha", NO, M("Vũ Khúc", "Phá Quân"), "người dưới sinh oán, bỏ đi", "Vũ Khúc, Phá Quân ở Nô Bộc", "limit", [("ally.resent", A), ("ally.fickle", A)])
qs("w2_no_vu_sat", NO, M("Vũ Khúc", "Thất Sát"), "người dưới phản chủ", "Vũ Khúc, Thất Sát ở Nô Bộc", "limit", [("ally.disloyal", A)])
qs("w2_no_vu_tham", NO, M("Vũ Khúc", "Tham Lang"), "người dưới ít giúp được việc", "Vũ Khúc, Tham Lang ở Nô Bộc", "limit", [("ally.weak", A)])
qs("w2_no_dong", NO, M("Thiên Đồng"), "người dưới giúp được việc", "Thiên Đồng ở Nô Bộc", "support", [("ally.helpful", A)])
qs("w2_no_dong_sat", NO, [*M("Thiên Đồng"), anyS(*SAT4)], "có người dưới phản chủ", "Thiên Đồng ở Nô Bộc gặp Kình, Đà, Hỏa, Linh", "limit", [("ally.disloyal", A)])
qs("w2_no_liem_ham", NO, mm("Liêm Trinh", "hãm"), "người dưới phản chủ", "Liêm Trinh hãm ở Nô Bộc", "limit", [("ally.disloyal", A)])
qs("w2_no_liem_mieu", NO, mm("Liêm Trinh", "miếu"), "người dưới đông, một tiếng gọi trăm người dạ", "Liêm Trinh miếu ở Nô Bộc", "support", [("ally.many", A)])
qs("w2_no_phu", NO, M("Thiên Phủ"), "người dưới giúp được việc, đông người theo", "Thiên Phủ ở Nô Bộc", "support", [("ally.helpful", A), ("ally.many", A)])
qs("w2_no_phu_sat", NO, [*M("Thiên Phủ"), any6()], "người dưới hay phản chủ, bỏ đi", "Thiên Phủ ở Nô Bộc gặp sát tinh", "limit", [("ally.disloyal", A)])
qs("w2_no_am_mieu", NO, mm("Thái Âm", "miếu"), "người dưới giúp được việc", "Thái Âm miếu ở Nô Bộc", "support", [("ally.helpful", A)])
qs("w2_no_am_ham", NO, mm("Thái Âm", "hãm"), "ít người dưới", "Thái Âm hãm ở Nô Bộc", "limit", [("ally.few", A)])
qs("w2_no_tham", NO, M("Tham Lang"), "dễ gặp người dưới làm hại chủ", "Tham Lang ở Nô Bộc", "limit", [("ally.drain", A)])
qs("w2_no_cu_mieu", NO, mm("Cự Môn", "miếu"), "người dưới gây thị phi, không ở lâu", "Cự Môn miếu ở Nô Bộc", "limit", [("ally.dispute", A), ("ally.fickle", A)])
qs("w2_no_tuong_vu", NO, M("Thiên Tướng", "Vũ Khúc"), "người dưới oán chủ", "Thiên Tướng, Vũ Khúc ở Nô Bộc", "limit", [("ally.resent", A)])
qs("w2_no_tuong_tu", NO, M("Thiên Tướng", "Tử Vi"), "nhiều người giúp việc", "Thiên Tướng, Tử Vi ở Nô Bộc", "support", [("ally.many", A)])
qs("w2_no_luong", NO, M("Thiên Lương"), "người dưới đông, chủ nhờ đó thịnh", "Thiên Lương ở Nô Bộc", "support", [("ally.many", A), ("ally.helpful", A)])
qs("w2_no_luong_co", NO, M("Thiên Lương", "Thiên Cơ"), "người dưới không một lòng", "Thiên Lương, Thiên Cơ ở Nô Bộc", "limit", [("ally.fickle", A)])
qs("w2_no_that_sat", NO, M("Thất Sát"), "người dưới cứng đầu, lấn chủ, hay lấy của", "Thất Sát ở Nô Bộc", "limit", [("ally.overstep", A), ("ally.disloyal", A)])
qs("w2_no_pha_mieu", NO, mm("Phá Quân", "miếu"), "người dưới giúp được việc", "Phá Quân miếu ở Nô Bộc", "support", [("ally.helpful", A)])
qs("w2_no_pha_ham", NO, mm("Phá Quân", "hãm"), "người dưới oán và phản chủ", "Phá Quân hãm ở Nô Bộc", "limit", [("ally.resent", A), ("ally.disloyal", A)])
qs("w2_no_xuong_doc", NO, [VCD, S("Văn Xương"), TTD("Văn Xương", ["miếu"])], "người dưới giúp được việc, đỡ đần cho chủ", "Văn Xương miếu đơn thủ Nô Bộc", "support", [("ally.helpful", A)])
qs("w2_no_khuc_mieu", NO, [S("Văn Khúc"), TTD("Văn Khúc", ["miếu"])], "người dưới giúp được việc", "Văn Khúc miếu ở Nô Bộc", "support", [("ally.helpful", A)])
qs("w2_no_ta_doc", NO, [VCD, S("Tả Phụ")], "người dưới đông, một tiếng gọi trăm người dạ", "Tả Phụ đơn thủ Nô Bộc", "support", [("ally.many", A)])
qs("w2_no_huu_doc", NO, [VCD, S("Hữu Bật")], "người dưới đông", "Hữu Bật đơn thủ Nô Bộc", "support", [("ally.many", A)])
qs("w2_no_ta_huu_sat", NO, [anyS("Tả Phụ", "Hữu Bật"), any6()], "người dưới phản chủ, lấy của mà đi", "Tả Phụ hoặc Hữu Bật ở Nô Bộc gặp sát tinh", "limit", [("ally.disloyal", A)])
qs("w2_no_loc_ton", NO, [S("Lộc Tồn")], "nhiều người giúp việc", "Lộc Tồn ở Nô Bộc", "support", [("ally.many", A)])
qs("w2_no_kinh", NO, [S("Kình Dương")], "người dưới oán và phản chủ, ít giúp được việc", "Kình Dương ở Nô Bộc", "limit", [("ally.disloyal", A), ("ally.resent", A)])
qs("w2_no_da", NO, [S("Đà La")], "người dưới ít giúp được việc, oán chủ", "Đà La ở Nô Bộc", "limit", [("ally.weak", A), ("ally.resent", A)])
qs("w2_no_hoa_doc", NO, [VCD, S("Hỏa Tinh")], "người dưới oán chủ, ít giúp được việc", "Hỏa Tinh đơn thủ Nô Bộc", "limit", [("ally.resent", A)])
qs("w2_no_linh_doc", NO, [VCD, S("Linh Tinh")], "người dưới ít giúp được việc", "Linh Tinh đơn thủ Nô Bộc", "limit", [("ally.weak", A)])
qs("w2_pm_khoi_viet", PM, [anyS("Thiên Khôi", "Thiên Việt")], "cha mẹ vinh hiển", "Thiên Khôi hoặc Thiên Việt ở Phụ Mẫu", "support", [("parents.prosper", A)])
qs("w2_pm_huu_bat", PM, [VCD, S("Hữu Bật"), anyS("Tả Phụ", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt")], "được cha mẹ che chở",
   "Hữu Bật đơn thủ Phụ Mẫu thêm cát tinh", "support", [("fortune.protected", A)])
qs("w2_pm_loc_ton_sat", PM, [S("Lộc Tồn"), any6()], "thuở nhỏ của cải của cha mẹ hao tổn", "Lộc Tồn ở Phụ Mẫu gặp sát tinh", "limit", [("parents.poor", A)])
qs("w2_pm_dong_cu", PM, M("Thiên Đồng", "Cự Môn"), "với cha mẹ kém hòa thuận", "Thiên Đồng, Cự Môn ở Phụ Mẫu", "limit", [("parents.strain", A)])
qs("w2_pm_cu_nhat", PM, M("Cự Môn", "Thái Dương"), "với cha mẹ ít hòa thuận", "Cự Môn, Thái Dương ở Phụ Mẫu", "limit", [("parents.strain", A)])

# the book's own turn: a modifier line weakens the bare line of the same star (relations.manual.json, applied only when both fire)
QUALIFIES = [("w2_no_tu_vi_sat", ["w2_no_tu_vi"]), ("w2_no_tu_tuong_kk", ["w2_no_tu_vi", "w2_no_tuong_tu"]), ("w2_no_dong_sat", ["w2_no_dong"]),
             ("w2_no_phu_sat", ["w2_no_phu"]), ("w2_no_ta_huu_sat", ["w2_no_ta_doc", "w2_no_huu_doc"]), ("tt66_nhat_suu_mui_sat", []),
             ("w2_tu_ta_phu_sat", ["w2_tu_ta_phu_tu_phu"]), ("tt72_ta_phu_bon_sat", ["tt72_ta_phu_don_hau"]), ("tt67_phu_bon_sat", []),
             ("tt76_hoa_ky_cat_lo", [])]

PACK_INFO = {
    "pack_toan_thu_ca.json": ("SRC_TOAN_THU", "Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục)", "TT"),
    "pack_khao_luan_cach.json": ("SRC_KHAO_LUAN", "Tử Vi Khảo Luận", "KL"),
    "pack_toan_thu_han_van.json": ("SRC_TOAN_THU_HAN", "紫微斗數全書 (Toàn Thư Hán văn)", "TTH"),
}
HEAD = {"tt": "Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục), {h}", "kl": "Tử Vi Khảo Luận, {h}", "web": "Toàn Thư Hán văn, {h}"}
SRC_TTH = {"id": "SRC_TOAN_THU_HAN", "title": "紫微斗數全書 (Tử Vi Đẩu Số Toàn Thư, Hán văn)", "author": "La Hồng Tiên biên / Hi Di Trần Đoàn",
           "edition": "zh.wikisource, bản chép điện tử; ảnh chụp lưu trong engine/data/sources_web (卷一 rev 7913704, 卷二 rev 1963110), lấy ngày 2026-10-24",
           "locator": "theo quyển và mục (không có trang): 'TTH 2 八奴仆'", "verified": True,
           "note": "Văn bản cổ thuộc phạm vi công cộng. Chủ dự án quyết định 2026-10-24: câu trích đối chiếu được với bản lưu thì tính là sách đã kiểm (tools/book_text.py quote_on_page('WEB:zwds_quanshu_2', mục, câu))."}


def cite(e):
    if e["book"].startswith("WEB:"):
        n = e["book"].rsplit("_", 1)[1]
        return f"TTH {n} {e['page']}"
    return f"{e['book']} p.{e['page']}"


# the 12-cung hợp cách / phá cách verses (TT pp.143-149) are cách: formation rules told in the Cách cục chapter, with no concept of their own, so
# that a Mệnh-branch verse does not speak as a trait of the person in the Mệnh chapter
CACH_BY_BRANCH = ("tt143_hop_", "tt144_hop_", "tt145_hop_", "tt147_pha_", "tt148_pha_", "tt149_tham_hoa_loc")


ABSOLUTE = ("chắc chắn", "nhất định", "suốt đời", "trọn đời", "không bao giờ", "luôn luôn", "tuyệt đối", "định mệnh")   # prose/lint.ts


def _plain(t):
    """the reader's text never states an absolute (prose/lint.ts ABSOLUTE): 'suốt đời' etc. are the book's emphasis, kept in the quote"""
    for w in ABSOLUTE:
        t = t.replace(w + " ", "").replace(w, "")
    return t.strip(" ,")


def _as_cach(x):
    """a formation rule's reading is 'cách <name> (<condition>: <effect>)', as the Thực Hành cách rules: the narrative takes the name before the
    parenthesis and the condition inside it"""
    pack, mid, pal, conds, claim, cond_vi, effect, ls, kind, also = x
    if mid.startswith(CACH_BY_BRANCH):
        head = MINED[mid]["heading"]                  # 'Hợp cách: Mệnh tại Tí', 'Phá cách: Mệnh tại Tị', 'Thất hãm bần tiện luận'
        name = ("đắc địa của " if head.startswith("Hợp") else "thất hãm của ") + head.split(": ", 1)[1].replace("tại", "ở") if ": " in head \
            else "thất hãm Tham Lang hóa Lộc ở Tứ mộ"
        body = claim.split(": ", 1)[1] if claim.startswith(("phá cách:", "hợp cách:")) else claim
        kind = "+" if effect == "support" else "-"
    elif kind:
        name = claim[len("cách "):].split(":")[0].split(",")[0].strip()
        body = claim.split(": ", 1)[1] if ": " in claim else claim.split(", ", 1)[-1]
    else:
        return pack, mid, pal, conds, _plain(claim), cond_vi, effect, ls, kind, also
    return pack, mid, pal, conds, f"cách {name}", f"{cond_vi}: {_plain(body)}", effect, [], kind, also


def main():
    global R
    dropped = [x[1] for x in R if MINED[x[1]].get("skip")]      # reviewed after the pack was first built: kept out with the mined entry's reason
    R = [_as_cach(x) for x in R if not MINED[x[1]].get("skip")]
    packs = {k: [] for k in PACK_INFO}
    claims, links, quotes, rel = {}, {}, [], []
    used = set()
    for pack, mid, pal, conds, claim, cond_vi, effect, ls, kind, also in R:
        e = MINED[mid]
        assert not e.get("skip") and not e.get("duplicate_of"), mid
        assert mid not in used, mid
        used.add(mid)
        src, bookname, bk = PACK_INFO[pack]
        rid = "TV_D3_" + mid.upper()
        fam = FAM[mid].split("_", 1)[1]
        cites = "".join(f" [{cite(x)}]" for x in [e] + [MINED[a] for a in also])
        desc = f"{HEAD[fam].format(h=e['heading'])} (paraphrased), cung {pal}: {claim} ({cond_vi}){cites}"
        cl = "d3_" + mid
        r = {"id": rid, "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "deep3", "description": desc,
             "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
             "consequences": [{"kind": "finding", "claim": cl, "effect": effect, "scope": "natal"}],
             "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": [src], "reviewStatus": "verified", "version": "0.1.0", "subject": "palace"}
        packs[pack].append(r)
        claims[cl] = ("khuynh hướng " if effect == "support" else "hạn chế: ") + f"{claim} ({cond_vi})"
        if effect == "limit":
            claims["limit:" + cl] = f"hạn chế: {claim} ({cond_vi})"
        ent = {"asserts": [{"concept": c, "stance": s} for c, s in ls], "src": "manual", "review": "draft"}
        if kind:                                  # a cách: told in the Cách cục chapter, no concept of its own (as the Thực Hành cách rules)
            ent = {"kind": "formation", "pol": kind, "asserts": [], "src": "manual", "review": "draft"}
        links[rid] = ent
        for x in [mid] + also:
            m = MINED[x]
            quotes.append({"rule": rid, "book": m["book"], "page": m["page"], "quote": m["quote"], "mined": x})
    for frm, tos in QUALIFIES:
        tos = [t for t in tos if t in used]
        if frm in used and tos:
            rel.append({"id": "REL_D3_" + frm.upper(), "type": "qualifies", "from": "TV_D3_" + frm.upper(), "to": ["TV_D3_" + t.upper() for t in tos],
                        "effect": "weaken", "basis": "sach", "cite": cite(MINED[frm]),
                        "note": "Sách nói câu gốc rồi nói thêm điều kiện làm nó kém đi (cùng một dòng hoặc dòng kế); khi cả hai cùng ứng, câu sau làm nhẹ câu trước."})
    skipped = {k: e["skip"] for k, e in MINED.items() if e.get("skip")}
    dups = {k: e["duplicate_of"] for k, e in MINED.items() if e.get("duplicate_of")}
    unused = sorted(k for k, e in MINED.items() if not e.get("skip") and not e.get("duplicate_of") and k not in used and e.get("target") in (None, "rule")
                    and FAM[k] in ("deep3_tt", "deep3_kl", "deep3_web") and not e["book"].startswith("WEB:zwds_quanshu_1"))
    for pack, rs in packs.items():
        srcs = [SRC_TTH] if pack == "pack_toan_thu_han_van.json" else []
        (D / pack).write_text(json.dumps({"sources": srcs, "rules": rs}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    (D / "quotes_deep3_tuvi.json").write_text(json.dumps({
        "note": "page quotes of pack_toan_thu_ca.json, pack_khao_luan_cach.json and pack_toan_thu_han_van.json (tools/build_deep3_tuvi_pack.py, from "
                "engine/data/kg/mined/deep3_*.json), checked by engine/tests/test_deep3_tuvi.py; 'skipped' and 'duplicates' cover every mined entry not made a rule",
        "quotes": quotes, "skipped": skipped, "duplicates": dups, "not_rules": unused}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
    cur = {k: v for k, v in cur.items() if not k.startswith(("d3_", "limit:d3_"))}      # a rerun replaces this builder's own entries
    cur.update(claims)
    (D / "claims_vi.json").write_text(json.dumps(cur, ensure_ascii=False, indent=1), "utf-8")
    man = json.loads((D / "kg" / "rule_concepts.manual.json").read_text("utf-8"))
    man["entries"] = {k: v for k, v in man["entries"].items() if not k.startswith("TV_D3_")}
    man["entries"].update(links)
    (D / "kg" / "rule_concepts.manual.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), "utf-8")
    rm = json.loads((D / "kg" / "relations.manual.json").read_text("utf-8"))
    rm["relations"] = [x for x in rm["relations"] if not x["id"].startswith("REL_D3_")] + rel
    (D / "kg" / "relations.manual.json").write_text(json.dumps(rm, ensure_ascii=False, indent=1), "utf-8")
    print({k: len(v) for k, v in packs.items()}, "relations", len(rel), "not made a rule (reported):", unused, "| dropped after review:", len(dropped))


if __name__ == "__main__":
    main()
