"""Generates engine/data/bazi_deep/pack_ttt_kin.json and quotes_ttt_kin.json from Trích Thiên Tủy Phần II (the Vietnamese PDF's text layer, committed
in engine/data/bazi_deep/mined/ttt_pNNN.txt): Phu Thê pp.128-129, Phụ Mẫu p.133, Huynh Đệ p.135, Hà Tri pp.137-141 (phú, quý, bần, tiện), Địa Vị
p.224 (DEEP-BAZI-2, 2026-10-23). Each rule keeps the printed words of its condition (quote), the page, and a paraphrase split into effect and
condition; read by tvbt.bazi_deep.kin on its own facts.
    .venv/bin/python tools/build_bazi_ttt_kin_pack.py
"vượng / trọng" and "nhược / khinh" of a ten-god group: its share of the TVH degrees from 25 % / under 12 % (system convention, as for 八字真宗);
"không có X": no stem and no hidden stem of X; "X không hiện / ẩn": X has no stem; "hỉ X" / "kỵ X": X among the groups Thiệu Vĩ Hoa's cách
table (pp.378-386) calls the useful god or a good luck / a bad luck (so these rules hold only if the cách stands; trace.conditional cach_partial);
"X sinh / phá / chế Y": an X character next to a Y character (same pillar, or the same row of two neighbouring pillars).
Left out on purpose: every "khắc vợ / khắc con / không con / số con / con trai, con gái" judgement (Phu Thê, Tử Nữ pp.128-132), the lifespan
pages (thọ / yểu pp.145-148), the parents' judgements that shame a family ("bại tổ nhục tông", p.133), and what needs the cách's own reading
(thanh / trọc, chân / giả thần, hóa thần) or an idiom the page does not explain (Tư Mã, ngũ chung, Xuất Thân pp.219-223)."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data" / "bazi_deep"
eq = lambda f, v: {"fact": f, "value": v}
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda f, v: {"fact": f, "operator": "contains_any", "value": v}
no = lambda c: {"not": c}
ALL = lambda *c: {"all": list(c)}
ANY = lambda *c: {"any": list(c)}
STRONG, WEAK = eq("bazi.k.dm_strong", True), eq("bazi.k.dm_strong", False)
V = lambda g: has("bazi.k.vuong", g)
N = lambda g: has("bazi.k.nhuoc", g)
A = lambda g: has("bazi.k.absent", g)
P = lambda g: has("bazi.k.present", g)
T = lambda g: has("bazi.k.trans", g)
HI = lambda g: has("bazi.k.hi", g)
KY = lambda g: has("bazi.k.ky", g)
ADJ = lambda a, b: has("bazi.k.adj", "|".join(sorted((a, b))))
MALE = eq("bazi.k.gender", "nam")
CONV = ("'Vượng / trọng', 'nhược / khinh' của một nhóm thập thần: phần độ của nhóm trên tổng độ Thiệu Vĩ Hoa (tr.331-355) từ 25 % / dưới 12 % (Tỉ Kiếp không tính độ của chính nhật chủ) — "
        "ngưỡng của hệ thống; 'không có': không có cả can lẫn tàng can; 'sinh, phá, chế': hai chữ đứng sát nhau.")
HI_NOTE = "'Hỉ', 'kỵ': theo bảng dụng thần và vận tốt, xấu của cách (Thiệu Vĩ Hoa tr.378-386), nên lời này chỉ đứng khi cách đứng được."
R = []


def add(rid, page, quote, topic, tone, effect, cause, cond, note=None, hi=False):
    R.append({"id": f"BT_TTTK_{rid}", "page": page, "quote": quote, "topic": topic, "tone": tone, "effect": effect, "cause": cause, "cond": cond,
              "note": " ".join(x for x in (note, CONV, HI_NOTE if hi else None) if x), "hi": hi})


# ---------------- Hà Tri: sao biết người giàu (p.137) — "đều là Tài khí thông môn hộ vậy"
RICH = "tiền của có đường thông suốt, là dấu hiệu giàu có"
add("PHU1", "p.137", "Thân vượng Tài nhược mà không có Quan, tất cần có Thực Thương", "wealth", "pos", RICH, "nhật chủ vượng, Tài nhược, không có Quan Sát nhưng có Thực Thương",
    ALL(STRONG, N("Tai"), A("QuanSat"), P("ThucThuong")))
add("PHU2", "p.137", "thân vượng Tài vượng không có Thực Thương, tất cần có Quan có Sát", "wealth", "pos", RICH, "nhật chủ vượng, Tài vượng, không có Thực Thương nhưng có Quan Sát",
    ALL(STRONG, V("Tai"), A("ThucThuong"), P("QuanSat")))
add("PHU3", "p.137", "Thân vượng Ấn vượng Thực Thương khinh, Tài tinh đắc cục", "wealth", "pos", RICH, "nhật chủ vượng, Ấn vượng, Thực Thương nhẹ mà Tài thành cục",
    ALL(STRONG, V("An"), N("ThucThuong"), eq("bazi.k.tai_cuc", True)), "Tài thành cục: địa chi đủ tam hợp hoặc tam hội của hành Tài.")
add("PHU4", "p.137", "thân vượng Quan suy Ấn thụ trọng, Tài được nắm lệnh", "wealth", "pos", RICH, "nhật chủ vượng, Quan Sát suy, Ấn nặng mà Tài nắm lệnh tháng",
    ALL(STRONG, N("QuanSat"), V("An"), eq("bazi.k.month_group", "Tai")))
add("PHU5", "p.137", "thân vượng Kiếp vượng, không có Tài Ấn mà có Thực Thương", "wealth", "pos", RICH, "nhật chủ vượng, Tỉ Kiếp vượng, không có Tài và Ấn nhưng có Thực Thương",
    ALL(STRONG, V("Ti"), A("Tai"), A("An"), P("ThucThuong")))
add("PHU6", "p.137", "thân nhược Tài trọng, không có Quan Ấn mà có Tỉ Kiếp", "wealth", "pos", RICH, "nhật chủ nhược, Tài nặng, không có Quan Sát và Ấn nhưng có Tỉ Kiếp",
    ALL(WEAK, V("Tai"), A("QuanSat"), A("An"), P("Ti")))
# ---------------- Hà Tri: sao biết người bần (p.139) — Tài bất chân, "bần nhiều mà phú ít"
POOR = "tiền của khó thành thật, nghèo nhiều hơn giàu"
add("BAN1", "p.139", "Tài trọng mà Thực Thương nhiều, là 1 bất chân", "wealth", "neg", POOR, "Tài nặng mà Thực Thương cũng nhiều", ALL(V("Tai"), V("ThucThuong")))
add("BAN2", "p.139", "Tài khinh hỉ Thực Thương mà Ấn vượng, là 2 bất chân", "wealth", "neg", POOR, "Tài nhẹ, lá số cần Thực Thương mà Ấn lại vượng",
    ALL(N("Tai"), HI("ThucThuong"), V("An")), hi=True)
add("BAN3", "p.139", "Tài khinh Kiếp trọng, Thực Thương không hiện là 3 bất chân", "wealth", "neg", POOR, "Tài nhẹ, Tỉ Kiếp nặng, Thực Thương không lộ can",
    ALL(N("Tai"), V("Ti"), no(T("ThucThuong"))))
add("BAN4", "p.139", "Tài nhiều hỉ Kiếp, mà Quan tinh chế Kiếp là 4 bất chân", "wealth", "neg", POOR, "Tài nhiều, lá số cần Tỉ Kiếp mà Quan Sát lại đứng sát chế Tỉ Kiếp",
    ALL(V("Tai"), HI("Ti"), ADJ("QuanSat", "Ti")), hi=True)
add("BAN5", "p.139", "Hỉ Ấn mà Tài tinh phá Ấn là 5 bất chân", "wealth", "neg", POOR, "lá số cần Ấn mà Tài lại đứng sát phá Ấn", ALL(HI("An"), ADJ("Tai", "An")), hi=True)
add("BAN6", "p.139", "Kỵ Ấn mà Tài tinh sinh Quan là 6 bất chân", "wealth", "neg", POOR, "lá số kỵ Ấn mà Tài lại đứng sát sinh Quan Sát", ALL(KY("An"), ADJ("Tai", "QuanSat")), hi=True)
add("BAN9", "p.139", "Quan Sát vượng hỉ Ấn, Tài tinh lại đắc cục, là 9 bất", "wealth", "neg", POOR, "Quan Sát vượng, lá số cần Ấn mà Tài lại thành cục",
    ALL(V("QuanSat"), HI("An"), eq("bazi.k.tai_cuc", True)), hi=True)
# ---------------- Hà Tri: sao biết người quý (p.138) — "đều là Quan tinh hữu lý hội, cho nên là quý hiển vậy"
NOBLE = "đường chức vụ có chỗ dựa, là dấu hiệu quý hiển"
add("QUY1", "p.138", "Thân vượng Quan nhược, Tài có thể sinh Quan", "rank", "pos", NOBLE, "nhật chủ vượng, Quan Sát nhược mà có Tài đứng sát sinh Quan",
    ALL(STRONG, N("QuanSat"), ADJ("Tai", "QuanSat")))
add("QUY2", "p.138", "Quan vượng thân nhược, Quan có thể sinh Ấn", "rank", "pos", NOBLE, "Quan Sát vượng, nhật chủ nhược mà Quan đứng sát sinh Ấn",
    ALL(V("QuanSat"), WEAK, ADJ("QuanSat", "An")))
add("QUY3", "p.138", "Ấn vượng Quan suy, Tài có thể phá Ấn", "rank", "pos", NOBLE, "Ấn vượng, Quan Sát suy mà có Tài đứng sát chế Ấn",
    ALL(V("An"), N("QuanSat"), ADJ("Tai", "An")))
add("QUY4", "p.138", "Ấn suy Quan vượng, Tài không hiện", "rank", "pos", NOBLE, "Ấn suy, Quan Sát vượng mà Tài không lộ can", ALL(N("An"), V("QuanSat"), no(T("Tai"))))
add("QUY5", "p.138", "Kiếp trọng Tài khinh, Quan có thể khử Kiếp", "rank", "pos", NOBLE, "Tỉ Kiếp nặng, Tài nhẹ mà có Quan Sát đứng sát chế Tỉ Kiếp",
    ALL(V("Ti"), N("Tai"), ADJ("QuanSat", "Ti")))
add("QUY6", "p.138", "Tài tinh phá Ấn, Quan có thể sinh Ấn", "rank", "pos", NOBLE, "Tài đứng sát phá Ấn nhưng có Quan Sát đứng sát sinh Ấn",
    ALL(ADJ("Tai", "An"), ADJ("QuanSat", "An")))
# ---------------- Hà Tri: sao biết người tiện (pp.141-142) — "Quan tinh không thấy"
LOW = "chức vụ khó hiển đạt"
add("TIEN4", "p.142", "Quan vượng hỉ Ấn, mà Tài tinh phá Ấn", "rank", "neg", LOW, "Quan Sát vượng, lá số cần Ấn mà Tài lại phá Ấn, không có Quan sinh Ấn cứu",
    ALL(V("QuanSat"), HI("An"), ADJ("Tai", "An"), no(ADJ("QuanSat", "An"))), "Khi có Quan Sát đứng sát sinh Ấn, tr.138 ('Tài phá Ấn, Quan có thể sinh Ấn') đứng thay.", hi=True)
add("TIEN5", "p.142", "Quan Sát trọng mà không có Ấn, Thực Thương cưỡng chế", "rank", "neg", LOW, "Quan Sát nặng, không có Ấn mà Thực Thương đứng sát chế Quan",
    ALL(V("QuanSat"), A("An"), ADJ("ThucThuong", "QuanSat")))
add("TIEN6", "p.142", "Quan nhiều kỵ Tài, Tài tinh lại đắc cục", "rank", "neg", LOW, "Quan Sát nhiều, lá số kỵ Tài mà Tài lại thành cục", ALL(V("QuanSat"), KY("Tai"), eq("bazi.k.tai_cuc", True)), hi=True)
add("TIEN7", "p.142", "thân nhược Ấn khinh, Quan vượng không có Tài", "rank", "neg", "khó thoát cảnh túng thiếu", "nhật chủ nhược, Ấn nhẹ, Quan Sát vượng mà không có Tài",
    ALL(WEAK, N("An"), V("QuanSat"), A("Tai")))
add("TIEN8", "p.142", "thân vượng Quan nhược, Tài tinh không hiện", "rank", "neg", "khó thoát cảnh túng thiếu", "nhật chủ vượng, Quan Sát nhược mà Tài không lộ can",
    ALL(STRONG, N("QuanSat"), no(T("Tai")), no(ADJ("Tai", "QuanSat"))), "Khi Tài ẩn đứng sát sinh Quan, tr.138 ('thân vượng Quan nhược, Tài có thể sinh Quan') đứng thay.")
# ---------------- Địa Vị (p.224): Sát Nhận thần thanh
add("DV1", "p.224", "Trong cục Sát vượng không có tài, Ấn thụ dụng Nhận, hoặc không có Ấn mà có Dương Nhận", "rank", "pos",
    "có khí thế của người nắm quyền kỷ cương (binh, hình)", "Thất Sát vượng, không có Tài, trong tứ trụ có dương nhẫn",
    ALL(V("QuanSat"), has("bazi.k.gods", "Thất Sát"), A("Tai"), eq("bazi.k.ren_present", True)), "Tr.224-225 gọi đây là 'Sát Nhận thần thanh'; nhẫn nắm lệnh tháng thì khí thế càng rõ.")
# ---------------- Phụ Mẫu (p.133): năm tháng là gốc
YM = lambda a, b: ANY(ALL(has("bazi.k.year_groups", a), has("bazi.k.month_groups", b)), ALL(has("bazi.k.year_groups", b), has("bazi.k.month_groups", a)))
add("PM3", "p.133", "Năm Quan tháng Ấn, tháng Quan năm Ấn, tổ thượng thanh cao", "parents", "pos", "gốc gác gia đình thanh cao", "trụ năm và trụ tháng có Quan và Ấn sinh nhau",
    YM("QuanSat", "An"), "Năm, tháng: can hoặc chính khí của chi trụ ấy.")
add("PM1", "p.133", "ngày giờ Tài Thương không phạm, thì được bề trên che chở, dưới nhận mà lấy vinh", "parents", "pos", "được người trên che chở, người dưới nể",
    "năm, tháng có Quan Ấn sinh nhau mà ngày, giờ không có Tài, Thương Quan phạm vào",
    ALL(YM("QuanSat", "An"), no(has("bazi.k.dayhour_groups", "Tai")), no(has("bazi.k.dayhour_gods", "Thương Quan"))))
add("PM2", "p.133", "Năm tháng Quan Ấn tương sinh, ngày giờ hình thương xung phá, thì phá sạch tổ nghiệp", "parents", "neg", "dễ làm hao tổ nghiệp",
    "năm, tháng có Quan Ấn sinh nhau nhưng chi ngày, giờ hình, xung, hại chi năm, tháng", ALL(YM("QuanSat", "An"), eq("bazi.k.ym_hurt_by_dh", True)))
add("PM5", "p.133", "Năm Tài tháng Ấn, nhật chủ hỉ Ấn, ngày giờ gặp Quan Ấn, biết là giúp cha chấn hưng gia đình", "parents", "pos", "giúp cha chấn hưng gia đình",
    "năm có Tài, tháng có Ấn, lá số cần Ấn và ngày, giờ gặp Quan, Ấn",
    ALL(has("bazi.k.year_groups", "Tai"), has("bazi.k.month_groups", "An"), HI("An"), anyof("bazi.k.dayhour_groups", ["QuanSat", "An"])), hi=True)
add("PM6", "p.133", "Năm Quan tháng Ấn, nhật chủ hỉ Ấn, ngày giờ gặp Quan, mà biết định tự bản thân cha mẹ thành lập gia môn", "parents", "pos", "cha mẹ tự gây dựng cơ nghiệp",
    "năm có Quan, tháng có Ấn, lá số cần Ấn và ngày, giờ gặp Quan",
    ALL(has("bazi.k.year_groups", "QuanSat"), has("bazi.k.month_groups", "An"), HI("An"), has("bazi.k.dayhour_groups", "QuanSat")), hi=True)
add("PM7", "p.133", "nhật chủ hỉ Tài, ngày giờ gặp Tài hoặc Thương, xuất thân nghèo khốn, mệnh tự thân lập nghiệp", "parents", "neutral", "xuất thân khó khăn, tự mình lập nghiệp",
    "tháng có Tỉ Kiếp (năm là Quan, Kiếp hoặc Ấn), lá số cần Tài và ngày, giờ gặp Tài hoặc Thương Quan",
    ALL(has("bazi.k.month_groups", "Ti"), anyof("bazi.k.year_groups", ["QuanSat", "Ti", "An"]), HI("Tai"),
        ANY(has("bazi.k.dayhour_groups", "Tai"), has("bazi.k.dayhour_gods", "Thương Quan"))), hi=True)
add("PM8", "p.133", "Năm Kiếp tháng Tài, nhật chủ hỉ Tài, sản nghiệp hùng hậu", "parents", "pos", "gia sản dày dặn", "năm có Tỉ Kiếp, tháng có Tài và lá số cần Tài",
    ALL(has("bazi.k.year_groups", "Ti"), has("bazi.k.month_groups", "Tai"), HI("Tai")), hi=True)
add("PM9", "p.133", "nhật chủ hỉ Kiếp, là thanh cao bần hàn", "parents", "neutral", "thanh cao mà thanh bần", "năm có Tỉ Kiếp, tháng có Tài và lá số cần Tỉ Kiếp",
    ALL(has("bazi.k.year_groups", "Ti"), has("bazi.k.month_groups", "Tai"), HI("Ti"), no(HI("Tai"))), hi=True)
add("PM10", "p.133", "Tài Quan Ấn thụ, quyết định ở năm tháng, là hỉ thần của nhật chủ, cha mẹ không phú cũng quý", "parents", "pos", "cha mẹ không giàu cũng sang",
    "Tài, Quan hay Ấn ở năm, tháng là chữ lá số cần",
    ANY(*[ALL(anyof("bazi.k.year_groups", [g]), HI(g)) for g in ("Tai", "QuanSat", "An")], *[ALL(anyof("bazi.k.month_groups", [g]), HI(g)) for g in ("Tai", "QuanSat", "An")]), hi=True)
# ---------------- Huynh Đệ (p.135)
add("HD1", "p.135", "Sát vượng không có Thực, Sát trọng không có Ấn, được Bại tài (Kiếp) hợp Sát, tất được em trợ lực", "siblings", "pos", "được em giúp sức",
    "Sát vượng, không có Thực Thần và Ấn, mà Kiếp Tài hợp Thất Sát",
    ALL(V("QuanSat"), no(has("bazi.k.gods", "Thực Thần")), A("An"), eq("bazi.k.kiep_hop_sat", True)))
add("HD2", "p.135", "Sát vượng Thực khinh, Ấn nhược gặp Tài, được Tỉ kiên địch Sát, tất được anh trợ lực", "siblings", "pos", "được anh giúp sức",
    "Sát vượng, Thực Thương nhẹ, Ấn yếu lại gặp Tài, mà Tỉ Kiên đứng sát chống Thất Sát",
    ALL(V("QuanSat"), N("ThucThuong"), N("An"), P("Tai"), eq("bazi.k.ti_vs_sat", True)))
add("HD4", "p.135", "Tài Quan thất thế, Kiếp Nhận làm càn, lo buồn giống như Chu Công", "siblings", "neg", "dễ phải lo buồn vì anh em", "Tài và Quan Sát đều yếu, Tỉ Kiếp lấn át",
    ALL(N("Tai"), N("QuanSat"), V("Ti")))
add("HD6", "p.135", "Sát trọng không có Ấn, nhật chủ suy Thương lại ẩn, anh em không thể không than thở", "siblings", "neg", "anh em nhiều điều phải than thở",
    "Sát nặng, không có Ấn, nhật chủ suy mà Thương Quan chỉ ẩn trong tàng can", ALL(V("QuanSat"), A("An"), WEAK, has("bazi.k.hidden_only", "ThucThuong")))
add("HD9", "p.135", "Nhật chủ tuy suy, Ấn vượng ở đề cương tháng, anh em hợp thành bầy", "siblings", "pos", "anh em đông vui, gắn bó", "nhật chủ suy nhưng Ấn vượng ở chi tháng",
    ALL(WEAK, eq("bazi.k.month_group", "An"), V("An")))
add("HD10", "p.135", "Thân vượng gặp Kiêu, Kiếp trọng không có Quan, một thân chủ trì", "siblings", "neutral", "một mình gánh vác việc nhà", "nhật chủ vượng gặp Thiên Ấn, Tỉ Kiếp nặng mà không có Quan Sát",
    ALL(STRONG, has("bazi.k.gods", "Thiên Ấn"), V("Ti"), A("QuanSat")))
add("HD11", "p.135", "Tài khinh Kiếp trọng, Thực Thương hóa Kiếp, có thể yên ổn", "siblings", "pos", "anh em có thể yên ổn", "Tài nhẹ, Tỉ Kiếp nặng mà có Thực Thương đứng sát rút khí Tỉ Kiếp",
    ALL(N("Tai"), V("Ti"), ADJ("ThucThuong", "Ti")))
add("HD12", "p.135", "Tài khinh gặp Kiếp, Quan được lộ rõ, không xảy ra chuyện nồi da nấu thịt", "siblings", "pos", "anh em không đến nỗi tranh hại nhau", "Tài nhẹ gặp Tỉ Kiếp mà Quan Sát lộ can",
    ALL(N("Tai"), P("Ti"), T("QuanSat")))
add("HD13", "p.135", "Kiêu Kiếp trọng phùng, Tài khinh Sát ẩn, không tránh khỏi đau buồn hao tổn", "siblings", "neg", "khó tránh buồn phiền, hao tổn vì anh em",
    "Thiên Ấn và Tỉ Kiếp đều nặng, Tài nhẹ, Quan Sát chỉ ẩn", ALL(has("bazi.k.gods", "Thiên Ấn"), V("An"), V("Ti"), N("Tai"), has("bazi.k.hidden_only", "QuanSat")))
add("HD14", "p.135", "Nhật chủ suy có Ấn, Tài tinh gặp Kiếp, trái lại anh em có thể hưng vinh", "siblings", "pos", "anh em lại có thể hưng vượng", "nhật chủ suy, có Ấn, Tài gặp Tỉ Kiếp đứng sát",
    ALL(WEAK, P("An"), ADJ("Tai", "Ti")))
# ---------------- Phu Thê (pp.128-129), lá số nam; không có lời nào về khắc vợ
add("PT1", "p.128", "Kiếp Nhận vượng, mà Tài khinh, có Thực Thương, vợ hiền mà không khắc", "marriage", "pos", "vợ hiền, vợ chồng giữ được nhau", "Tỉ Kiếp vượng, Tài nhẹ mà có Thực Thương",
    ALL(MALE, V("Ti"), N("Tai"), P("ThucThuong")))
add("PT3A", "p.128", "Thân cường Sát nhẹ, Tài tinh sinh Sát", "marriage", "pos", "vợ hiền, hoặc nhờ của vợ mà khá giả", "nhật chủ vượng, Sát nhẹ, có Tài đứng sát sinh Sát",
    ALL(MALE, STRONG, N("QuanSat"), ADJ("Tai", "QuanSat")), "Câu sách: 'chủ vợ hiền mà đẹp, hoặc được thê tài dẫn đến giàu có'.")
add("PT3B", "p.128", "Quan khinh Thương quan trọng, Tài tinh hóa Thương quan", "marriage", "pos", "vợ hiền, hoặc nhờ của vợ mà khá giả", "Quan nhẹ, Thương Quan nặng, có Tài đứng sát nhận khí Thương Quan",
    ALL(MALE, N("QuanSat"), V("ThucThuong"), ADJ("Tai", "ThucThuong")), "Câu sách: 'chủ vợ hiền mà đẹp, hoặc được thê tài dẫn đến giàu có'.")
add("PT3C", "p.128", "Ấn thụ trùng điệp, Tài tinh đắc khí", "marriage", "pos", "vợ hiền, hoặc nhờ của vợ mà khá giả", "Ấn trùng điệp mà Tài có gốc",
    ALL(MALE, V("An"), eq("bazi.k.tai_rooted_any", True), no(ADJ("Tai", "An"))), "Câu sách: 'chủ vợ hiền mà đẹp, hoặc được thê tài dẫn đến giàu có'. Khi Tài đứng sát phá Ấn thì không xét câu này.")
add("PT4A", "p.129", "Sát trọng thân khinh, Tài tinh bè đảng với Sát", "marriage", "neg", "vợ khó hiền, có khi vì vợ mà vướng chuyện", "Sát nặng, nhật chủ nhẹ, Tài đứng sát sinh thêm cho Sát",
    ALL(MALE, V("QuanSat"), WEAK, ADJ("Tai", "QuanSat")), "Câu sách: 'chủ vợ không hiền mà xấu, hoặc vì vợ mà mang họa vào thân'.")
add("PT4B", "p.129", "Quan nhiều dụng Ấn, Tài tinh phá Ấn", "marriage", "neg", "vợ khó hiền, có khi vì vợ mà vướng chuyện", "Quan Sát nhiều, dụng thần là Ấn mà Tài đứng sát phá Ấn",
    ALL(MALE, V("QuanSat"), has("bazi.k.yong", "An"), ADJ("Tai", "An")), "Câu sách: 'chủ vợ không hiền mà xấu, hoặc vì vợ mà mang họa vào thân'.", hi=True)
add("PT5", "p.129", "Nhật chủ tọa Tài, Tài là hỉ dụng thần, tất được vợ cùng tài sản", "marriage", "pos", "được vợ và cả tài sản", "nhật chủ ngồi trên Tài mà Tài là chữ lá số cần",
    ALL(MALE, eq("bazi.k.day_group", "Tai"), HI("Tai")), hi=True)

SAY = {
    "PM10": "{pm10} là chữ lá số cần", "PM3": "{ym} có Quan và Ấn sinh nhau", "PM1": "{ym} có Quan và Ấn sinh nhau, mà ngày, giờ không có Tài, Thương Quan phạm vào",
    "PM5": "{ym}: năm có Tài, tháng có Ấn; lá số cần Ấn và ngày, giờ gặp Quan, Ấn", "PM6": "{ym}: năm có Quan, tháng có Ấn; lá số cần Ấn và ngày, giờ gặp Quan",
    "PM7": "{ym}: tháng có Tỉ Kiếp; lá số cần Tài và ngày, giờ gặp Tài hoặc Thương Quan", "PM8": "{ym}: năm có Tỉ Kiếp, tháng có Tài, và lá số cần Tài",
    "PM9": "{ym}: năm có Tỉ Kiếp, tháng có Tài, và lá số cần Tỉ Kiếp",
}
SRC = {"id": "SRC_TTT_P2_KIN", "title": "Trích Thiên Tủy — Phần II: Phu Thê, Phụ Mẫu, Huynh Đệ, Hà Tri, Địa Vị", "author": "Lưu Bá Ôn / Nhậm Thiết Tiều",
       "locator": "PDF pp.128-141, 224 (text layer in data/bazi_deep/mined/)", "verified": True, "edition": None,
       "note": "Đọc trực tiếp lớp chữ của bản PDF (Claude, 2026-10-23); mỗi luật giữ câu in nguyên văn trong quotes_ttt_kin.json, test đối chiếu với trang đã chép."}
rules, meta = [], {}
for r in R:
    rules.append({"id": r["id"], "system": "bat_tu", "schoolId": "ttt_nham_thi", "category": f"ttt_kin_{r['topic']}",
                  "description": f"Trích Thiên Tủy {r['page']}: {r['quote']} — {r['effect']} ({r['cause']})", "conditions": r["cond"],
                  "consequences": [{"kind": "finding", "claim": r["id"].lower(), "effect": {"pos": "support", "neg": "limit"}.get(r["tone"], "neutral"), "scope": "natal"}],
                  "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": [SRC["id"]], "reviewStatus": "verified", "version": "0.1.0", "subject": "chart"})
    short = r["id"].removeprefix("BT_TTTK_")
    meta[r["id"]] = {k: r[k] for k in ("page", "quote", "topic", "tone", "effect", "cause")} | {"book": "ttt"} | ({"say": SAY[short]} if short in SAY else {}) | ({"note": r["note"]} if r["note"] else {}) | ({"hi": True} if r["hi"] else {})
assert len({r["id"] for r in rules}) == len(rules)
(D / "pack_ttt_kin.json").write_text(json.dumps({"sources": [SRC], "rules": rules}, ensure_ascii=False, indent=1) + "\n", "utf-8")
(D / "quotes_ttt_kin.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", "utf-8")
print(len(rules), "rules")
