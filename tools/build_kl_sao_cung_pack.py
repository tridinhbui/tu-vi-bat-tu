"""Generates data/pack_khao_luan_sao_cung.json: Tử Vi Khảo Luận pp.84-117, the 'X ở các cung' entries of the chính tinh from Thái Dương to Phá
Quân for the palaces of career (Quan), money (Tài), property (Điền) and marriage (Phu thê / Phối) — the part of 'Ý nghĩa các sao' that
build_kl_stars_pack.py (pp.63-83) did not reach (plan DEEP-TUVI, 2026-10-22).

Every entry was read on the page image (line order and the heading it sits under) and its quote is checked against the PDF text layer by
engine/tests/test_kl_sao_cung.py (`QUOTES`, skipped when the book is absent). Paraphrased with page cites; the condition is the book's, nothing
added: a line naming a branch tests palace.branch, a pair tests both chính tinh in the palace. Left out on purpose: Mệnh and vận lines,
health, prison, theft, sexual reputation, appearance; for Phu thê every timing or event line (sớm / muộn lập gia đình, bỏ nhau, xa cách lần
nào); lines whose condition needs a star outside the chart facts; lines whose pairing cannot occur (the book's Tham–Vũ at Thìn/Tuất, Tham–Liêm
at Tí/Ngọ, Đồng–Lương at Tí/Mão) and lines whose words are too vague to read ('phú quý bất thường')."""
import json
import unicodedata
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
OWNM = "palace.own_major_stars"
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda *x: {"any": list(x)}
allof = lambda *x: {"all": list(x)}
nt = lambda x: {"not": x}
br = lambda *b: {"fact": "palace.branch", "operator": "in", "value": list(b)}
M = lambda *ss: [has(OWNM, s) for s in ss]
TT = anyof({"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True})

# (palace, id, conditions, reading, effect, page, quote, concept links [(concept, stance)])
R = []
def add(pal, rid, conds, vi, effect, page, quote, links):
    R.append((pal, rid, conds, vi, effect, page, quote, links))
Q, T, P, DT = "Quan Lộc", "Tài Bạch", "Phu Thê", "Điền Trạch"
A, W = "affirms", "weakens"

# ---- Vũ Khúc pp.87-88
add(T, "VU", M("Vũ Khúc"), "giàu có (Vũ Khúc ở Tài Bạch)", "support", "p.88", "Tài và Điền: Giầu có", [("fin.abundance", A)])
add(DT, "VU", M("Vũ Khúc"), "giàu có về nhà đất (Vũ Khúc ở Điền Trạch)", "support", "p.88", "Tài và Điền: Giầu có", [("prop.rich", A)])
add(Q, "VU_PHU", M("Vũ Khúc", "Thiên Phủ"), "công danh hiển đạt (Vũ Khúc đồng cung Thiên Phủ ở Quan Lộc)", "support", "p.88", "Đồng cung Thiên phủ thì công danh hoạnh đạt", [("career.success", A)])
add(Q, "VU_SAT", M("Vũ Khúc", "Thất Sát"), "thiên về võ nghiệp (Vũ Khúc đồng cung Thất Sát ở Quan Lộc)", "support", "p.88", "Đồng cung Thất sát: võ biển", [("exp.martial", A)])
add(Q, "VU_THAM", M("Vũ Khúc", "Tham Lang"), "buôn bán giàu có (Vũ Khúc đồng cung Tham Lang ở Quan Lộc)", "support", "p.88", "Đồng cung Tham lang: buôn bán giầu có", [("path.business", A)])
# ---- Thiên Đồng p.90
add(Q, "DONG_DAU", M("Thiên Đồng") + [br("Dậu")], "công danh đến muộn (Thiên Đồng ở Quan Lộc tại Dậu)", "limit", "p.90", "hoặc tại Dậu thì muộn công danh", [("career.late", A)])
add(Q, "DONG_CU", M("Thiên Đồng", "Cự Môn"), "đường công danh không tốt (Thiên Đồng đồng cung Cự Môn ở Quan Lộc)", "limit", "p.90", "Xấu nếu gặp Cự đồng cung", [("career.obstacle", A)])
add(T, "DONG_AM_TY", M("Thiên Đồng", "Thái Âm") + [br("Tý")], "tay trắng làm giàu (Thiên Đồng, Thái Âm ở Tài Bạch tại Tý)", "support", "p.90", "Gặp Nguyệt ở Tí, tay trắng làm giầu (bạch thủ thành gia)", [("fin.self_made", A)])
add(T, "DONG_THIN_TUAT", M("Thiên Đồng") + [br("Thìn", "Tuất")], "túng thiếu (Thiên Đồng ở Tài Bạch tại Thìn, Tuất)", "limit", "p.90", "Tại Thìn Tuất thì túng thiếu", [("fin.scarcity", A)])
add(T, "DONG_CU", M("Thiên Đồng", "Cự Môn"), "túng thiếu, dễ vì tiền mà sinh kiện tụng (Thiên Đồng đồng cung Cự Môn ở Tài Bạch)", "limit", "p.90", "Đồng cung với Cự cũng túng thiếu mà còn bị kiện tụng vì tiền", [("fin.scarcity", A)])
add(P, "DONG_TY_DAU", M("Thiên Đồng") + [br("Tỵ", "Dậu")], "gia đạo không êm (Thiên Đồng ở Phu Thê tại Tỵ, Dậu)", "limit", "p.90", "Gia đạo xấu nếu Đồng cung ở Dậu, ở Tỵ", [("rel.strain", A)])
add(P, "DONG_THIN_TUAT", M("Thiên Đồng") + [br("Thìn", "Tuất")], "vợ chồng bất hòa (Thiên Đồng ở Phu Thê tại Thìn, Tuất)", "limit", "p.90", "Thìn Tuất thì bất hòa, xa cách", [("rel.strain", A)])
# ---- Liêm Trinh pp.93-94
add(Q, "LIEM_QUYEN", M("Liêm Trinh") + [anyof(br("Dần", "Thân"), has(OWNM, "Thiên Phủ"), has(OWNM, "Thiên Tướng"))], "có uy quyền, được người kính nể (Liêm Trinh ở Quan Lộc tại Dần, Thân hoặc đồng cung Phủ, Tướng)", "support", "p.94", "Tại Dần Thân, hoặc đồng cung với Thiên phủ, Thiên tướng có uy quyền được người kính nể", [("career.authority", A)])
add(Q, "LIEM_SAT", M("Liêm Trinh", "Thất Sát"), "công danh chậm (Liêm Trinh đồng cung Thất Sát ở Quan Lộc)", "limit", "p.94", "Khi đi với Thất sát, công danh chậm", [("career.late", A)])
add(Q, "LIEM_PHA", M("Liêm Trinh", "Phá Quân"), "công danh không toại ý (Liêm Trinh đồng cung Phá Quân ở Quan Lộc)", "limit", "p.94", "Khi có Phá quân đồng cung bất toại công danh", [("career.obstacle", A)])
add(T, "LIEM_PHU_TUONG", M("Liêm Trinh") + [anyof(has(OWNM, "Thiên Phủ"), has(OWNM, "Thiên Tướng"))], "giàu có lớn (Liêm Trinh đồng cung Phủ hoặc Tướng ở Tài Bạch)", "support", "p.93", "Giầu có lớn khi có Thiên phủ, Thiên tướng đồng cung", [("fin.abundance", A)])
add(T, "LIEM_DAN_THAN", M("Liêm Trinh") + [br("Dần", "Thân")], "tiền bạc khá nhưng phải cạnh tranh mới giàu (Liêm Trinh ở Tài Bạch tại Dần, Thân)", "support", "p.93", "Tốt ở Dần Thân, nhưng phải cạnh tranh với giầu có", [("fin.effortful", A)])
add(T, "LIEM_SAT", M("Liêm Trinh", "Thất Sát"), "giàu có nhưng thất thường (Liêm Trinh đồng cung Thất Sát ở Tài Bạch)", "limit", "p.93", "Nếu đồng cung với Thất sát thì giầu có thất thường", [("fin.volatile", A)])
add(T, "LIEM_PHA", M("Liêm Trinh", "Phá Quân"), "tiền bạc đi liền với tai ương (Liêm Trinh đồng cung Phá Quân ở Tài Bạch)", "limit", "p.93", "Đồng cung với Phá quân thì tiền bạc đi liền với tai ương", [("fin.volatile", A)])
add(P, "LIEM", M("Liêm Trinh"), "hầu hết các vị trí đều bất lợi cho gia đạo (Liêm Trinh ở Phu Thê)", "limit", "p.93", "Hầu hết các vị thế đều bất lợi cho gia đạo", [("rel.strain", A)])
add(DT, "LIEM_DAN_THAN", M("Liêm Trinh") + [br("Dần", "Thân")], "khó có điền sản (Liêm Trinh ở Điền Trạch tại Dần, Thân)", "limit", "p.94", "Ở Dần Thân không có điền sản", [("prop.poor", A)])
add(DT, "LIEM_THAM", M("Liêm Trinh", "Tham Lang"), "tổ nghiệp dễ bị phá (Liêm Trinh đồng cung Tham Lang ở Điền Trạch)", "limit", "p.94", "Có Tham lang đồng cung, tổ nghiệp bị phá sản", [("prop.poor", A)])
# ---- Thiên Phủ p.96
for pal, c in ((T, "fin.abundance"), (DT, "prop.rich"), (Q, "career.success")):
    add(pal, "PHU", M("Thiên Phủ"), f"thường rất tốt (Thiên Phủ ở {pal})", "support", "p.96", "Thường rất tốt đặc biệt ở Tỵ, Hợi", [(c, A)])
add(P, "PHU_TY_HOI", M("Thiên Phủ") + [anyof(br("Tỵ", "Hợi"), has(OWNM, "Tử Vi"), has(OWNM, "Vũ Khúc"), has(OWNM, "Liêm Trinh"))], "gia đạo đẹp nhất (Thiên Phủ ở Phu Thê tại Tỵ, Hợi hoặc đồng cung Tử, Vũ, Liêm)", "support", "p.96", "Thiên phủ đẹp nhất ở Tỵ Hợi", [("rel.harmony", A)])
add(P, "PHU_BAT_HOA", M("Thiên Phủ") + [br("Sửu", "Mùi", "Mão", "Dậu")], "vợ chồng bất hòa (Thiên Phủ ở Phu Thê tại Sửu, Mùi, Mão, Dậu)", "limit", "p.96", "Ở Sửu Mùi Mão Dậu thì vợ chồng bất hòa", [("rel.strain", A)])
# ---- Thái Âm p.99
add(Q, "NHAT_NGUYET_SUU_MUI", M("Thái Dương", "Thái Âm") + [br("Sửu", "Mùi"), nt(TT)], "bất đắc chí trong công danh (Nhật Nguyệt đồng cung ở Quan Lộc tại Sửu, Mùi, không gặp Tuần, Triệt)", "limit", "p.99", "Nhật Nguyệt đồng cung Sửu Mùi không gặp Tuần Triệt : bất đắc chí", [("career.obstacle", A)])
# ---- Tham Lang p.102
add(T, "THAM_TY_NGO", M("Tham Lang") + [br("Tý", "Ngọ")], "dễ thiếu thốn (Tham Lang ở Tài Bạch tại Tý, Ngọ)", "limit", "p.102", "Tham lang đơn thủ Tí Ngọ cũng nghèo", [("fin.scarcity", A)])
add(P, "THAM_THIN_TUAT", M("Tham Lang") + [br("Thìn", "Tuất")], "dễ có chuyện ghen tuông (Tham Lang ở Phu Thê tại Thìn, Tuất)", "limit", "p.102", "Tham lang ở Thìn Tuất : vợ ghen tuông, chồng chơi bời", [("rel.jealous", A)])
# ---- Cự Môn pp.105-106
add(Q, "CU_TY_NGO", M("Cự Môn") + [br("Tý", "Ngọ")], "văn võ kiêm toàn (Cự Môn ở Quan Lộc tại Tý, Ngọ)", "support", "p.105", "Tại Tí Ngọ: văn võ kiêm toàn", [("exp.versatile", A)])
add(Q, "CU_TY", M("Cự Môn") + [br("Tỵ")], "công danh trắc trở (Cự Môn ở Quan Lộc tại Tỵ)", "limit", "p.105", "Tại Tỵ công danh trắc trở", [("career.obstacle", A)])
add(Q, "CU_THIN_TUAT", M("Cự Môn") + [br("Thìn", "Tuất")], "công danh về sau mới phát (Cự Môn ở Quan Lộc tại Thìn, Tuất)", "support", "p.105", "Tại Thìn Tuất công danh về sau mới phát", [("career.late", A)])
add(T, "CU_HOI_TY_NGO", M("Cự Môn") + [br("Hợi", "Tý", "Ngọ")], "tay trắng làm nên (Cự Môn ở Tài Bạch tại Hợi, Tý, Ngọ)", "support", "p.105", "Tại Hợi, Tí, Ngọ tay trắng làm nên", [("fin.self_made", A)])
add(T, "CU_DAN", M("Cự Môn") + [br("Dần")], "giàu có lớn (Cự Môn ở Tài Bạch tại Dần)", "support", "p.105", "Tại Dần giầu có lớn", [("fin.abundance", A)])
add(T, "CU_THIN_TUAT", M("Cự Môn") + [br("Thìn", "Tuất")], "tiền tài lúc vào lúc ra (Cự Môn ở Tài Bạch tại Thìn, Tuất)", "limit", "p.105", "Tại Thìn, Tuất tiền tài khi vô khi ra", [("fin.volatile", A)])
add(T, "CU_CO", M("Cự Môn", "Thiên Cơ"), "buôn bán giàu có (Cự Môn đồng cung Thiên Cơ ở Tài Bạch)", "support", "p.105", "Cự môn Thiên cơ buôn bán giầu có", [("fin.abundance", A)])
add(P, "CU_TY_NGO_HOI", M("Cự Môn") + [br("Tý", "Ngọ", "Hợi")], "vợ chồng quý hiển nhưng bất hòa (Cự Môn ở Phu Thê tại Tý, Ngọ, Hợi)", "limit", "p.105", "Cự môn Tí, Ngọ, Hợi: vợ chồng quí hiển nhưng bất hòa", [("rel.strain", A)])
add(P, "CU", M("Cự Môn"), "Cự Môn ở Phu Thê là vị trí xấu nhất của sao này (Cự Môn ở Phu Thê)", "limit", "p.106", "Cự môn đóng ở cung Phu Thê là xấu nhất", [("rel.strain", A)])
# ---- Thiên Tướng p.108
add(P, "TUONG", M("Thiên Tướng"), "vợ chồng nể nhau nhưng gia đạo hay cãi vã (Thiên Tướng ở Phu Thê)", "limit", "p.108", "Ở Phối có nghĩa là nể vợ, nể chồng, gia đạo hay có cãi vã", [("rel.strain", A)])
add(P, "TUONG_TU_VU", M("Thiên Tướng") + [anyof(has(OWNM, "Tử Vi"), has(OWNM, "Vũ Khúc"))], "vợ chồng giàu có (Thiên Tướng đồng cung Tử Vi hoặc Vũ Khúc ở Phu Thê)", "support", "p.108", "Đi cùng Tử vi, Vũ khúc vợ chồng giầu có", [("fin.abundance", A)])
add(P, "TUONG_LIEM", M("Thiên Tướng", "Liêm Trinh"), "vợ chồng bất hòa (Thiên Tướng đồng cung Liêm Trinh ở Phu Thê)", "limit", "p.108", "Đi với Liêm vợ chồng bất hòa", [("rel.strain", A)])
add(P, "TUONG_MAO_DAU", M("Thiên Tướng") + [br("Mão", "Dậu")], "hôn nhân trắc trở (Thiên Tướng ở Phu Thê tại Mão, Dậu)", "limit", "p.108", "Ở Mão, Dậu hôn nhân trắc trở", [("rel.strain", A)])
# ---- Thiên Lương pp.110-111
add(P, "LUONG_NHAT_MAO", M("Thiên Lương", "Thái Dương") + [br("Mão")], "hôn nhân hạnh phúc (Thiên Lương, Thái Dương ở Phu Thê tại Mão)", "support", "p.110", "Lương Nhật ở Mão: hạnh phúc", [("rel.harmony", A)])
add(P, "LUONG_CO", M("Thiên Lương", "Thiên Cơ"), "vợ chồng hiền lương (Thiên Lương đồng cung Thiên Cơ ở Phu Thê)", "support", "p.110", "Lương Cơ đồng cung: vợ chồng hiền lương", [("values.kind", A)])
add(T, "LUONG_TY_NGO", M("Thiên Lương") + [br("Tý", "Ngọ")], "giàu có (Thiên Lương ở Tài Bạch tại Tý, Ngọ)", "support", "p.110", "Lương Tí Ngọ: giầu có", [("fin.abundance", A)])
add(T, "LUONG_TY_HOI", M("Thiên Lương") + [br("Tỵ", "Hợi")], "dễ kiếm tiền nhưng cũng dễ tiêu (Thiên Lương ở Tài Bạch tại Tỵ, Hợi)", "limit", "p.110", "Lương Tỵ Hợi: dễ kiếm tiền nhưng cũng dễ tiêu", [("fin.volatile", A)])
add(T, "LUONG_NHAT_DAU", M("Thiên Lương", "Thái Dương") + [br("Dậu")], "kiếm tiền chật vật (Thiên Lương, Thái Dương ở Tài Bạch tại Dậu)", "limit", "p.110", "Lương Nhật ở Dậu: kiếm tiền chật vật", [("fin.scarcity", A)])
add(Q, "LUONG_QUY", M("Thiên Lương") + [anyof(has(OWNM, "Thiên Đồng"), br("Tý", "Ngọ"), has(OWNM, "Thiên Cơ"), allof(has(OWNM, "Thái Dương"), br("Mão")))],
    "quý hiển, có tài sư phạm, chính trị, chiến lược, có khiếu y dược (Thiên Lương ở Quan Lộc: đồng cung Đồng, Cơ, ở Tý Ngọ, hoặc với Thái Dương ở Mão)", "support", "p.111", "Lương Đồng Dần Thân, Lương Tí Ngọ, Lương Cơ đồng cung, Lương Nhật ở Mão: quí hiển, có tài sư phạm, chính trị, chiến lược, có khiếu về Y Dược", [("career.status", A), ("exp.talent", A)])
add(Q, "LUONG_TY_HOI", M("Thiên Lương") + [br("Tỵ", "Hợi")], "chóng chán, hay thay đổi việc (Thiên Lương ở Quan Lộc tại Tỵ, Hợi)", "limit", "p.111", "Lương Tỵ Hợi: phóng chán, hay thay đổi", [("adapt.unsteady", A)])
# ---- Thất Sát pp.113-114
add(P, "SAT_DAN_THAN", M("Thất Sát") + [br("Dần", "Thân")], "vợ chồng tài cán, đảm đang, danh giá (Thất Sát ở Phu Thê tại Dần, Thân)", "support", "p.113", "Chỉ trừ hai cung Dần Thân vợ chồng tài cán đảm đang, danh giá", [("exp.talent", A)])
add(P, "SAT_TY_NGO", M("Thất Sát") + [br("Tý", "Ngọ")], "vợ chồng xung khắc (Thất Sát ở Phu Thê tại Tý, Ngọ)", "limit", "p.113", "Tí Ngọ: hình khắc", [("rel.strain", A)])
add(T, "SAT_DAN_THAN", M("Thất Sát") + [br("Dần", "Thân")], "kiếm tiền dễ dàng (Thất Sát ở Tài Bạch tại Dần, Thân)", "support", "p.113", "Thất sát Dần Thân kiếm tiền dễ dàng", [("fin.abundance", A)])
add(T, "SAT_TY_NGO", M("Thất Sát") + [br("Tý", "Ngọ")], "tiền bạc thất thường (Thất Sát ở Tài Bạch tại Tý, Ngọ)", "limit", "p.113", "Thất sát Tí Ngọ tiền bạc thất thường", [("fin.volatile", A)])
add(T, "SAT_TU_TY", M("Thất Sát", "Tử Vi") + [br("Tỵ")], "dễ làm giàu (Thất Sát đồng cung Tử Vi ở Tài Bạch tại Tỵ)", "support", "p.113", "Thất sát Tử vi ở Tỵ dễ làm giầu", [("fin.abundance", A)])
add(T, "SAT_VU", M("Thất Sát", "Vũ Khúc"), "tự lực lập nghiệp, vất vả lúc đầu (Thất Sát đồng cung Vũ Khúc ở Tài Bạch)", "support", "p.113", "Sát Vũ dồng cung lập nghiệp tự lực, vất vả buổi đầu", [("fin.self_made", A)])
add(T, "SAT_THIN_TUAT", M("Thất Sát") + [br("Thìn", "Tuất")], "thiếu thốn (Thất Sát ở Tài Bạch tại Thìn, Tuất)", "limit", "p.113", "Sát Thìn Tuất: thiếu thốn", [("fin.scarcity", A)])
add(Q, "SAT", M("Thất Sát"), "thường theo nghiệp võ (Thất Sát ở Quan Lộc)", "support", "p.114", "Khi đóng ở Quan, Thất sát thương là quân nhân", [("exp.martial", A)])
add(Q, "SAT_TRIEU", M("Thất Sát") + [anyof(has(OWNM, "Tử Vi"), br("Dần", "Thân", "Tý", "Ngọ"))], "văn võ kiêm toàn, uy quyền lớn nhưng may rủi liền nhau (Thất Sát ở Quan Lộc tại Dần, Thân, Tý, Ngọ hoặc đồng cung Tử Vi)", "support", "p.114", "Nếu đồng cung với Tử vi hay ở vị trí triều đẩu ở Dần Thân, ngưỡng đẩu ở Tí Ngọ thì rất đẹp, văn võ kiêm toàn, uy quyền lớn, nhưng may rủi liền nhau", [("career.authority", A)])
# ---- Phá Quân pp.116-117
add(P, "PHA", M("Phá Quân"), "vợ chồng hay hao tán (Phá Quân ở Phu Thê)", "limit", "p.116", "Phu thê hao tán", [("rel.strain", A)])
add(P, "PHA_TY_NGO", M("Phá Quân") + [br("Tý", "Ngọ")], "vợ chồng khá giả (Phá Quân ở Phu Thê tại Tý, Ngọ)", "support", "p.116", "Tí Ngọ: chận phu thê, vợ chồng khá giả", [("fin.abundance", A)])
add(P, "PHA_LIEM", M("Phá Quân", "Liêm Trinh"), "vợ chồng bất hòa, nghèo khó (Phá Quân đồng cung Liêm Trinh ở Phu Thê)", "limit", "p.116", "Phá quân Liêm trinh đồng cung: bất hòa, xa cách, nghèo khó", [("rel.strain", A)])
add(T, "PHA_TY_NGO", M("Phá Quân") + [br("Tý", "Ngọ")], "giàu có (Phá Quân ở Tài Bạch tại Tý, Ngọ)", "support", "p.116", "Tí Ngọ giầu có", [("fin.abundance", A)])
add(T, "PHA_THIN_TUAT", M("Phá Quân") + [br("Thìn", "Tuất")], "tiền bạc vào ra thất thường (Phá Quân ở Tài Bạch tại Thìn, Tuất)", "limit", "p.116", "Thìn Tuất: tiền bạc vô ra thất thường", [("fin.volatile", A)])
add(T, "PHA_TU_VU", M("Phá Quân") + [anyof(has(OWNM, "Tử Vi"), has(OWNM, "Vũ Khúc"))], "chật vật lúc đầu, về sau sung túc (Phá Quân đồng cung Tử Vi hoặc Vũ Khúc ở Tài Bạch)", "support", "p.116", "Đồng cung với Tử hoặc Vũ: chật vật lúc đầu, sau sung túc", [("fin.effortful", A)])
add(T, "PHA_DAN_THAN", M("Phá Quân") + [br("Dần", "Thân")], "khó kiếm tiền (Phá Quân ở Tài Bạch tại Dần, Thân)", "limit", "p.116", "Dần Thân: khó kiếm tiền", [("fin.scarcity", A)])
add(Q, "PHA_THIN_TUAT", M("Phá Quân") + [br("Thìn", "Tuất")], "văn võ kiêm toàn, có uy quyền (Phá Quân ở Quan Lộc tại Thìn, Tuất)", "support", "p.117", "Ở Thìn Tuất: văn võ kiêm toàn, có uy quyền", [("exp.versatile", A), ("career.authority", A)])

add(Q, "PHA_VO", M("Phá Quân") + [anyof(br("Tý", "Ngọ"), has(OWNM, "Tử Vi"))], "thành công trong võ nghiệp nhưng thất thường (Phá Quân ở Quan Lộc tại Tý, Ngọ hoặc đồng cung Tử Vi)", "support", "p.117",
    "Ở Tí Ngọ hay đồng cung với Tử vi: thành công trong võ nghiệp nhưng thất thường", [("exp.martial", A)])
add(Q, "PHA_DAN_THAN", M("Phá Quân") + [anyof(br("Dần", "Thân"), has(OWNM, "Vũ Khúc"))], "theo binh nghiệp thì chật vật, chậm lên chức; buôn bán hay làm kỹ nghệ thì khéo tay (Phá Quân ở Quan Lộc tại Dần, Thân hoặc đồng cung Vũ Khúc)", "support", "p.117",
    "Ở Dần Thân hay đồng cung với Vũ khúc: quân nhân thường chật vật, chậm lên chức, buôn bán, lay làm kỹ nghệ thì khéo tay", [("exp.craft", A)])
add(Q, "SAT_LIEM_VU", M("Thất Sát") + [anyof(has(OWNM, "Liêm Trinh"), has(OWNM, "Vũ Khúc"))], "hiển đạt binh nghiệp nhưng thăng giáng thất thường (Thất Sát đồng cung Liêm Trinh hoặc Vũ Khúc ở Quan Lộc)", "support", "p.114",
    "Sái Liêm, Sát Vũ hiển đạt binh nghiệp nhưng thăng giáng thất thường", [("exp.martial", A)])
add(DT, "CU", M("Cự Môn"), "rất nhiều nhà cửa (Cự Môn ở Điền Trạch)", "support", "p.105", "Rất nhiều nhà cửa", [("prop.rich", A)])
add(DT, "SAT", M("Thất Sát"), "thường gặp bất lợi về điền sản (Thất Sát ở Điền Trạch)", "limit", "p.114", "Thường gặp bất lợi về điền sản", [("prop.poor", A)])
add(DT, "PHA", M("Phá Quân") + [nt(br("Thìn", "Tuất")), nt(has(OWNM, "Tử Vi"))], "có sản nghiệp cũng khó giữ (Phá Quân ở Điền Trạch, trừ khi ở Thìn, Tuất hoặc đồng cung Tử Vi)", "limit", "p.117",
    "Rất xấu, có sản nghiệp cũng khó giữ, trừ khi đóng ở Thìn Tuất hay đòng cung với Tử vi", [("prop.poor", A)])
# ---- phụ tinh pp.124-142
OWN = "palace.own_stars"
KK = anyof(has(OWN, "Địa Không"), has(OWN, "Địa Kiếp"))
HAO = anyof(has(OWN, "Đại Hao"), has(OWN, "Tiểu Hao"))
add(Q, "KHONG_KIEP", [KK], "công danh kém (Địa Không, Địa Kiếp ở Quan Lộc)", "limit", "p.127", "Công danh kém", [("career.obstacle", A)])
add(T, "KHONG_KIEP", [KK], "phát nhanh mà tàn cũng nhanh (Địa Không, Địa Kiếp ở Tài Bạch)", "limit", "p.127", "Hoạnh phát, hoạch tàn", [("fin.volatile", A)])
add(T, "SONG_HAO", [HAO], "tán tài (Đại Hao, Tiểu Hao ở Tài Bạch)", "limit", "p.136", "Tán tài, không có điền sản", [("fin.volatile", A)])
add(DT, "SONG_HAO", [HAO], "khó có điền sản (Đại Hao, Tiểu Hao ở Điền Trạch)", "limit", "p.136", "Tán tài, không có điền sản", [("prop.poor", A)])
add(Q, "SONG_HAO", [HAO], "hay thay đổi chỗ làm (Đại Hao, Tiểu Hao ở Quan Lộc)", "limit", "p.136", "Thay đổi chỗ làm, ra ngoài tốn tiền", [("adapt.unsteady", A)])
add(T, "LOC_TON", [has(OWN, "Lộc Tồn"), nt(KK)], "chắc chắn giàu, cách 'lộc cư lộc vị' (Lộc Tồn ở Tài Bạch, không có Không, Kiếp đồng cung)", "support", "p.142",
    "Đóng ở cung Tài là cách \"lộc cư lộc vị\", chắc chắn là giầu", [("fin.abundance", A)])
add(T, "LOC_TON_KHONG_KIEP", [has(OWN, "Lộc Tồn"), KK], "kho tiền như bị lấy sạch (Lộc Tồn ở Tài Bạch gặp Không, Kiếp đồng cung)", "limit", "p.142",
    "ngoại trừ có Không Kiếp đồng cung thì là số ăn mày, có nghĩa là kho tàng bị cướp sạch", [("fin.scarcity", A)])
add(T, "XUONG_KHUC", [anyof(has(OWN, "Văn Xương"), has(OWN, "Văn Khúc"))], "của cải dễ phá tán (Văn Xương, Văn Khúc ở Tài Bạch)", "limit", "p.124", "Phá tán của cải", [("fin.volatile", A)])

slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_")
rules, claims, links, quotes = [], {}, {}, []
for pal, rid, conds, vi, effect, page, quote, ls in R:
    rid_full = f"TV_KL_SAO_CUNG_{slug(pal)}_{rid}"
    claim = "kl_sc_" + rid_full[len("TV_KL_SAO_CUNG_"):].lower()
    rules.append({"id": rid_full, "system": "tu_vi", "schoolId": "vn_dlhc_draft", "category": "kl_sao_cung",
        "description": f"Tử Vi Khảo Luận, ý nghĩa các sao ở các cung (paraphrased), cung {pal}: {vi} [KL {page}]",
        "conditions": {"all": [{"fact": "palace.name", "value": pal}] + conds},
        "consequences": [{"kind": "finding", "claim": claim, "effect": effect, "scope": "natal"}],
        "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": ["SRC_KHAO_LUAN"], "reviewStatus": "verified", "version": "0.1.0", "subject": "palace"})
    claims[claim] = ("khuynh hướng " if effect == "support" else "hạn chế: ") + vi
    if effect == "limit":
        claims["limit:" + claim] = "hạn chế: " + vi
    links[rid_full] = {"asserts": [{"concept": c, "stance": s} for c, s in ls], "src": "manual", "review": "draft"}
    quotes.append({"rule": rid_full, "page": int(page[2:]), "quote": quote})
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({"sources": [], "rules": rules}, open(D / "pack_khao_luan_sao_cung.json", "w"), ensure_ascii=False, indent=1)
json.dump({"note": "page quotes of pack_khao_luan_sao_cung.json (tools/build_kl_sao_cung_pack.py), checked by engine/tests/test_kl_sao_cung.py", "quotes": quotes},
          open(D / "pack_khao_luan_sao_cung.quotes.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
for k, v in claims.items():
    cur[k] = v
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
man = json.loads((D / "kg" / "rule_concepts.manual.json").read_text("utf-8"))
man["entries"].update(links)
json.dump(man, open(D / "kg" / "rule_concepts.manual.json", "w"), ensure_ascii=False, indent=1)
print(len(rules))
