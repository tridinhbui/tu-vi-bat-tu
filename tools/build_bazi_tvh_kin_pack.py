"""Generates engine/data/bazi_deep/pack_tvh_kin.json and quotes_tvh_kin.json from Thiệu Vĩ Hoa, Dự Đoán Theo Tứ Trụ (bản quét; the pages were
transcribed from the page images into engine/data/bazi_deep/mined/tvh_pNNN.txt and checked line by line against the images): Lục thân pp.149-155,
tài vận pp.520-527, quan vận pp.533-537, hôn nhân pp.463-478 (DEEP-BAZI-2, 2026-10-23). Read by tvbt.bazi_deep.kin on its own facts.
    .venv/bin/python tools/build_bazi_tvh_kin_pack.py
Conventions as tools/build_bazi_ttt_kin_pack.py ("vượng / nhược" of a group by share of the TVH degrees, a system threshold; "hỉ / kỵ / dụng" by the
cách table pp.378-386). Chosen: the judgements with a condition the facts can decide without a judgement call and a judgement that is not about death,
illness, injury, infidelity, remarriage, number / sex / appearance of children or spouse. Left out (see DEEP-BAZI-2.md §5): thần sát conditions
(đào hoa, hoa cái, quý nhân, lộc mã, tam kì, củng lộc, khôi canh, thiên / nguyệt đức), titles of the old court (tể tướng, vương hầu, nội các), the
judgements about a luck pillar ("hành đến vận …": they belong to the đại vận chapter, not the year), the children by the hour branch (the plan reads
the hour pillar as children only through 八字真宗 p.60), and the book-internal contradictions (p.527 vs p.553 thân vượng ấn vượng; p.152 vs p.153
nhật chủ vượng tỉ kiếp vượng: only the milder p.152 kept, the other named in the note)."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data" / "bazi_deep"
eq = lambda f, v: {"fact": f, "value": v}
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda f, v: {"fact": f, "operator": "contains_any", "value": v}
inn = lambda f, v: {"fact": f, "operator": "in", "value": v}
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
YONG = lambda g: has("bazi.k.yong", g)
GOD = lambda g: has("bazi.k.gods", g)
ADJ = lambda a, b: has("bazi.k.adj", "|".join(sorted((a, b))))
MALE, FEMALE = eq("bazi.k.gender", "nam"), eq("bazi.k.gender", "nữ")
DAY = lambda *gods: inn("bazi.k.day_god", list(gods))
CONV = ("'Vượng / nhiều', 'nhược / yếu' của một nhóm thập thần: phần độ của nhóm trên tổng độ Thiệu Vĩ Hoa (tr.331-355) từ 25 % / dưới 12 % "
        "(Tỉ Kiếp không tính độ của chính nhật chủ) — ngưỡng của hệ thống; 'sinh, chế': hai chữ đứng sát nhau.")
PT_NOTE = ("Tổ hợp Thập thần (REVIEW-19 W6): hai chữ của tổ hợp 'đứng sát' nhau theo cùng quy ước trên (tvbt.bazi_deep.kin._patterns); "
           "sách không định nghĩa khoảng cách, đây là quy ước của hệ thống.")
PT = lambda pid: has("bazi.k.pt", pid)
PT_OK = lambda pid: ALL(PT(pid), no(has("bazi.k.pt_pha", pid)))
HI_NOTE = "'Hỉ', 'kỵ', 'dụng thần': theo bảng dụng thần và vận tốt, xấu của cách (Thiệu Vĩ Hoa tr.378-386), nên lời này chỉ đứng khi cách đứng được."
R = []


def add(rid, page, quote, topic, tone, effect, cause, cond, note=None, hi=False, say=None, pt=None, book="tvh"):
    R.append({"id": f"BT_TVHK_{rid}", "page": page, "quote": quote, "topic": topic, "tone": tone, "effect": effect, "cause": cause, "cond": cond,
              "note": " ".join(x for x in (note, CONV, PT_NOTE if pt else None, HI_NOTE if hi else None) if x), "hi": hi, "say": say, "pt": pt, "book": book})


# ---------------- tài vận (pp.520-527)
add("W01", "p.520", "Tài nên tàng ẩn, tàng thì phong phú hùng hậu", "wealth", "pos", "của cải dồi dào", "Tài chỉ tàng trong địa chi, không lộ ra can",
    ALL(P("Tai"), no(T("Tai"))))
add("W02", "p.520", "Thân vượng, tài nhiều là tiền của vừa ý", "wealth", "pos", "tiền của vừa ý", "nhật chủ vượng mà Tài nhiều", ALL(STRONG, V("Tai")))
add("W03", "p.520", "Tài làm dụng thần là người giàu có", "wealth", "pos", "là người giàu có", "dụng thần là Tài", YONG("Tai"), hi=True)
add("W04", "p.520", "Thân vượng, tài nhược, nếu được thực thương sinh tài thì mới giàu", "wealth", "pos", "có thể giàu lên", "nhật chủ vượng, Tài nhược nhưng có Thực Thương đứng sát sinh Tài",
    ALL(STRONG, N("Tai"), ADJ("ThucThuong", "Tai")))
add("W05", "p.520", "Tài gặp trường sinh là ruộng vườn vạn mẫu", "wealth", "pos", "giàu ruộng đất", "can Tài ngồi trên đất Trường Sinh của nó", eq("bazi.k.tai_changsinh", True),
    "Trường Sinh theo bảng mười hai giai đoạn (Bát Tự Chân Tông tr.24-25), xét can Tài trên chi của chính trụ ấy.")
add("W06", "p.521", "Trong trụ đủ cả tài, quan, ấn là người không sang thì giàu", "wealth", "pos", "không sang thì giàu", "tứ trụ có đủ Tài, Quan Sát và Ấn",
    ALL(P("Tai"), P("QuanSat"), P("An")))
add("W07", "p.522", "Tài nhiều lại lộ rõ thì thành bại thất thường", "wealth", "neg", "thành bại thất thường", "Tài nhiều mà lại lộ can", ALL(V("Tai"), T("Tai")))
add("W08", "p.522", "Tài nhiều gặp tỉ kiếp trợ giúp là nhà giàu thịnh vượng", "wealth", "pos", "nhà giàu thịnh vượng", "Tài nhiều mà có Tỉ Kiếp đỡ thân",
    ALL(V("Tai"), P("Ti"), WEAK))
add("W09", "p.523", "Trước tỉ, sau tài là trước nghèo sau giàu", "wealth", "neutral", "trước nghèo sau giàu", "Tỉ Kiếp ở trụ năm, tháng, còn Tài ở trụ ngày, giờ",
    eq("bazi.k.front_ti_back_tai", True), "Trước: trụ năm, tháng; sau: chi ngày, trụ giờ (cách đọc của hệ thống cho 'trước, sau').")
add("W10", "p.522", "trước tài sau ấn thì chuyển thành người có phúc", "wealth", "pos", "về sau thành người có phúc", "Tài ở trụ năm, tháng, còn Ấn ở trụ ngày, giờ",
    eq("bazi.k.front_tai_back_an", True), "Trước: trụ năm, tháng; sau: chi ngày, trụ giờ (cách đọc của hệ thống cho 'trước, sau').")
add("W11", "p.527", "Tài nhiều, thân nhược là nhà cửa nhiều, nhưng của cải ít", "wealth", "neg", "nhà cửa có thể nhiều nhưng của cải ít", "Tài nhiều mà nhật chủ nhược",
    ALL(V("Tai"), WEAK, no(P("Ti"))), "Khi có Tỉ Kiếp đỡ thân, tr.522 ('Tài nhiều gặp tỉ kiếp trợ giúp là nhà giàu thịnh vượng') đứng thay.")
add("W12", "p.527", "Thân vượng, ấn vượng là tiền hao tán không tụ", "wealth", "neg", "tiền hao tán khó tụ, giữ bằng bất động sản thì hơn", "nhật chủ vượng mà Ấn cũng vượng",
    ALL(STRONG, V("An")), "Tr.553 (công danh) lại viết 'thân vượng ấn vượng là hiển đạt cao quý': lời ấy nói về danh, lời này về tiền.")
add("W13", "p.527", "Thực thần gặp kiêu là tài vật hao tán", "wealth", "neg", "tài vật dễ hao tán", "Thực Thần gặp Thiên Ấn", ALL(GOD("Thực Thần"), GOD("Thiên Ấn")), pt="kieu_doat_thuc")
add("W14", "p.527", "Tứ trụ không có tài để giữ cho mình thì khi ra ngoài cầu tài cần phải cẩn thận", "wealth", "neutral", "đi xa cầu tài nên thận trọng", "tứ trụ không có Tài", A("Tai"))
# ---------------- quan vận (pp.533-537)
add("Q01", "p.533", "Trong trụ sát vượng, thân vượng là bậc quan thanh liêm cao quý", "rank", "pos", "dễ giữ chức vụ mà vẫn thanh liêm", "Sát vượng mà nhật chủ cũng vượng",
    ALL(STRONG, V("QuanSat"), GOD("Thất Sát")))
add("Q02", "p.535", "Tài vượng sinh quan là tự mình thành đạt", "rank", "pos", "tự mình thành đạt", "Tài vượng, đứng sát sinh Quan Sát", ALL(V("Tai"), ADJ("Tai", "QuanSat")), pt="tai_quan_song_my")
add("Q04", "p.534", "Quan, sát rơi vào tuần không vong thì lênh đênh không có chức gì ra hồn", "rank", "neg", "khó có chức vụ vững", "chữ Quan Sát rơi vào không vong",
    eq("bazi.k.qs_void", True), "Không vong tính theo trụ ngày (cùng phép của tr.24, 37 Bát Tự Chân Tông), xét chính khí của chi.")
add("Q05", "p.536", "Có một ngôi chính quan là quý nhân, quân tử; thuần tuý là quan cương trực, liêm chính", "rank", "pos", "là người ngay thẳng, cương trực",
    "tứ trụ chỉ có một chữ Chính Quan, không lẫn Thất Sát", eq("bazi.k.one_cq", True))
add("Q06", "p.535", "Trước tài sau ấn là thăng chức luôn luôn", "rank", "pos", "đường chức vụ dễ đi lên đều", "Tài ở trụ năm, tháng, còn Ấn ở trụ ngày, giờ",
    eq("bazi.k.front_tai_back_an", True), "Trước: trụ năm, tháng; sau: chi ngày, trụ giờ (cách đọc của hệ thống).")
add("Q07", "p.535", "Trụ năm có quan tinh, gặp được tài, ấn, thân vượng là phúc khí dồi dào, phát đạt rất sớm", "rank", "pos", "phát đạt sớm",
    "trụ năm có Quan, tứ trụ có Tài và Ấn, nhật chủ vượng", ALL(has("bazi.k.year_groups", "QuanSat"), P("Tai"), P("An"), STRONG))
add("Q08", "p.537", "Trụ năm chính ấn, trụ tháng chính quan là người nhậm chức ngành giáo dục", "rank", "pos", "hợp với ngành giáo dục", "trụ năm có Chính Ấn, trụ tháng có Chính Quan",
    eq("bazi.k.ya_mq", True))
# ---------------- lục thân (pp.149-155)
add("L01", "p.149", "có người trụ năm là dụng thần, có lực thì người đó xuất thân ở gia đình cha ông có sản nghiệp", "parents", "pos", "xuất thân trong nhà có sản nghiệp",
    "can trụ năm là dụng thần", eq("bazi.k.year_stem_yong", True), "'Có lực': dụng thần lộ ở can năm (cách đọc của hệ thống).", hi=True, say="can năm {ys_name} mang dụng thần {yong_vi}")
add("L02", "p.150", "Nếu trụ năm là: kiêu thần, thất sát, kình dương, kiếp tài, là kị thần thì tổ tiên và người đó xuất thân đều nghèo đói", "parents", "neg", "xuất thân khó khăn",
    "trụ năm mang Thiên Ấn, Thất Sát, dương nhẫn hoặc Kiếp Tài, mà đó là chữ lá số kỵ", eq("bazi.k.year_bad_ky", True), hi=True)
add("L03", "p.150", "Nếu nhật chủ là hỉ quan, ngày giờ lại gặp tài, nhật chủ là hỉ ấn, ngày giờ lại gặp quan thì người đó nhất định hơn ông cha", "parents", "pos", "làm nên hơn đời cha ông",
    "lá số cần Quan mà ngày, giờ gặp Tài, hoặc cần Ấn mà ngày, giờ gặp Quan",
    ANY(ALL(HI("QuanSat"), has("bazi.k.dayhour_groups", "Tai")), ALL(HI("An"), has("bazi.k.dayhour_groups", "QuanSat"))), hi=True)
add("L04", "p.150", "Ngược lại nhật chủ là hỉ quan, nhưng ngày giờ gặp thương; nhật chủ là hỉ ấn, nhưng ngày, giờ gặp tài thì người đó sa sút hơn ông cha", "parents", "neg",
    "khó giữ được bằng đời cha ông", "lá số cần Quan mà ngày, giờ gặp Thương Quan, hoặc cần Ấn mà ngày, giờ gặp Tài",
    ALL(ANY(ALL(HI("QuanSat"), has("bazi.k.dayhour_gods", "Thương Quan")), ALL(HI("An"), has("bazi.k.dayhour_groups", "Tai"))),
        no(ANY(ALL(HI("QuanSat"), has("bazi.k.dayhour_groups", "Tai")), ALL(HI("An"), has("bazi.k.dayhour_groups", "QuanSat"))))),
    "Khi ngày, giờ cũng gặp chữ làm 'hơn cha ông' (cùng trang), lời ấy và lời này đi hai chiều: hệ thống không nói lời này.", hi=True)
add("L05", "p.150", "Chi năm là thực thần, không có kiêu thần thì cha mẹ cao to, béo, tính cách thành thực, của cải nhiều", "parents", "pos", "cha mẹ tính thành thực, có của",
    "chi năm mang Thực Thần, lá số không có Thiên Ấn", ALL(eq("bazi.k.year_branch_god", "Thực Thần"), no(GOD("Thiên Ấn"))), "Vế về vóc dáng của câu sách không đưa vào văn.")
add("L06", "p.150", "Chi năm là chính quan, cha mẹ đôn hậu hòa nhã", "parents", "pos", "cha mẹ đôn hậu, hòa nhã", "chi năm mang Chính Quan", eq("bazi.k.year_branch_god", "Chính Quan"))
add("L07", "p.151", "Dụng thần hiện ở can tháng hoặc chi tháng là anh chị em không sang thì cũng giàu, người đó được nhờ", "siblings", "pos", "anh chị em khá giả, mình được nhờ",
    "dụng thần có ở trụ tháng", eq("bazi.k.month_yong", True), hi=True, say="dụng thần {yong_vi} có ở trụ tháng {mp_name}")
add("L08", "p.152", "nhật chủ vượng lại gặp tỉ kiếp vượng là mình giúp anh em nhiều", "siblings", "neutral", "mình giúp anh em nhiều", "nhật chủ vượng, Tỉ Kiếp cũng vượng",
    ALL(STRONG, V("Ti")), "Tr.153 lại viết 'Nhật chủ vượng mà tỉ kiếp nhiều thì anh em bại gia, bất hoà': hai lời cùng điều kiện, hệ thống chỉ nói lời này.")
add("L09", "p.153", "Nếu nhật chủ nhược thì lại là người được anh em, bạn bè giúp đỡ", "siblings", "pos", "được anh em, bạn bè giúp đỡ", "nhật chủ nhược mà có Tỉ Kiếp",
    ALL(WEAK, P("Ti")))
# vợ theo chi ngày (lá số nam, pp.154-155)
add("S01", "p.154", "Chi ngày là chính quan thì vợ tướng mạo đoan trang, ôn hoà, hiền thục, nội trợ tốt", "marriage", "pos", "vợ đoan trang, hiền thục, giỏi việc nhà",
    "chi ngày mang Chính Quan", ALL(MALE, DAY("Chính Quan")))
add("S02", "p.154", "Chi ngày đóng tài tinh là hỉ, người đó được vợ giúp đỡ hoặc có của nhờ vợ", "marriage", "pos", "được vợ giúp đỡ hoặc có của nhờ vợ", "chi ngày mang Tài mà Tài là chữ lá số cần",
    ALL(MALE, DAY("Chính Tài", "Thiên Tài"), HI("Tai")), hi=True)
add("S03", "p.154", "Chi ngày đóng chính ấn là vợ hiền, được vợ giúp, thân nhược càng tốt", "marriage", "pos", "vợ hiền, được vợ giúp", "chi ngày mang Chính Ấn",
    ALL(MALE, DAY("Chính Ấn")))
add("S04", "p.154", "Chi ngày đóng tỉ kiếp mà thân nhược là vợ tháo vát", "marriage", "pos", "vợ tháo vát", "chi ngày mang Tỉ Kiếp mà nhật chủ nhược",
    ALL(MALE, DAY("Tỉ Kiên", "Kiếp Tài"), WEAK))
add("S05", "p.155", "Chi ngày là thiên ấn mà thân nhược là vợ hiền, tháo vát", "marriage", "pos", "vợ hiền, tháo vát", "chi ngày mang Thiên Ấn mà nhật chủ nhược",
    ALL(MALE, DAY("Thiên Ấn"), WEAK))
add("S06", "p.155", "Thất sát đóng chi ngày và là dụng thần cũng là được vợ giúp đỡ", "marriage", "pos", "được vợ giúp đỡ", "chi ngày mang Thất Sát mà Quan Sát là dụng thần",
    ALL(MALE, DAY("Thất Sát"), YONG("QuanSat")), hi=True)
add("S07", "p.155", "Nhật chủ vượng, chi ngày là tỉ kiếp là vợ làm hao tài, hay cãi cọ", "marriage", "neg", "vợ làm hao tài, hay cãi cọ", "nhật chủ vượng mà chi ngày mang Tỉ Kiếp",
    ALL(MALE, DAY("Tỉ Kiên", "Kiếp Tài"), STRONG), "Vế 'nặng ra có thể phá sản' của câu sách không đưa vào văn.")
add("S08", "p.463", "Nam gặp tài nhiều và thân nhược là chồng hay nghe lời vợ", "marriage", "neutral", "người chồng hay nghe lời vợ", "lá số nam, Tài nhiều mà nhật chủ nhược",
    ALL(MALE, V("Tai"), WEAK))
add("S09", "p.464", "Tỷ kiếp vượng lại có thực thương sinh tài thì gặp vợ hiền", "marriage", "pos", "gặp vợ hiền", "Tỉ Kiếp vượng, có Thực Thương đứng sát sinh Tài",
    ALL(MALE, V("Ti"), ADJ("ThucThuong", "Tai")))
add("S10", "p.469", "Kình dương đóng ở trụ ngày thì vợ không hiền và hao tài", "marriage", "neg", "vợ khó hiền, dễ hao tài", "chi ngày là dương nhẫn của nhật chủ",
    ALL(MALE, eq("bazi.k.day_ren", True)))
# chồng (lá số nữ, pp.465-466, 478)
add("H01", "p.465", "Mệnh nữ có một quan hay một sát rõ là tốt. Có cả quan và sát là kém", "marriage", "pos", "đường chồng tốt", "lá số nữ chỉ có Quan hoặc chỉ có Sát, lộ rõ trên can",
    ALL(FEMALE, eq("bazi.k.one_qs_clear", True)))
add("H02", "p.465", "Có cả quan và sát là kém", "marriage", "neg", "đường chồng kém", "lá số nữ có cả Chính Quan lẫn Thất Sát", ALL(FEMALE, GOD("Chính Quan"), GOD("Thất Sát")))
add("H03", "p.465", "Quan rõ là chồng vinh hoa, vàng bạc đầy nhà", "marriage", "pos", "chồng vinh hiển, nhà sung túc", "lá số nữ có Quan lộ can", ALL(FEMALE, T("QuanSat"), no(ALL(GOD("Chính Quan"), GOD("Thất Sát")))))
add("H04", "p.466", "Người có quan vượng lại tài cũng vượng là lấy được chồng hiền chồng tốt", "marriage", "pos", "lấy được chồng hiền, chồng tốt", "lá số nữ, Quan Sát vượng và Tài cũng vượng",
    ALL(FEMALE, V("QuanSat"), V("Tai")))
add("H05", "p.466", "Người có đủ tài quan ấn thụ là lấy chồng thịnh vượng", "marriage", "pos", "lấy chồng thịnh vượng", "lá số nữ có đủ Tài, Quan Sát và Ấn",
    ALL(FEMALE, P("Tai"), P("QuanSat"), P("An")))
add("H06", "p.466", "Ấn vượng quan yếu là chồng tự tìm đến mình", "marriage", "neutral", "người chồng tự tìm đến", "lá số nữ, Ấn vượng mà Quan Sát yếu", ALL(FEMALE, V("An"), N("QuanSat")))
add("H07", "p.466", "Quan mạnh thương yếu là giúp chồng xây dựng cơ đồ", "marriage", "pos", "giúp chồng gây dựng cơ đồ", "lá số nữ, Quan Sát mạnh mà Thực Thương yếu",
    ALL(FEMALE, V("QuanSat"), N("ThucThuong")))
add("H08", "p.466", "Quan, sát yếu, có tài sinh quan là giúp đỡ chồng được nhiều", "marriage", "pos", "giúp đỡ chồng được nhiều", "lá số nữ, Quan Sát yếu mà có Tài đứng sát sinh Quan",
    ALL(FEMALE, N("QuanSat"), ADJ("Tai", "QuanSat")))
add("H09", "p.478", "Quan sát vượng quá lại không bị chế ngự là chồng không theo lời vợ", "marriage", "neg", "chồng không nghe lời vợ", "lá số nữ, Quan Sát vượng mà không có Thực Thương đứng sát chế",
    ALL(FEMALE, V("QuanSat"), no(ADJ("ThucThuong", "QuanSat"))))
add("H10", "p.478", "Mệnh nữ tài quá yếu thì khó giúp đỡ được chồng", "marriage", "neg", "khó giúp đỡ chồng", "lá số nữ, Tài quá yếu", ALL(FEMALE, N("Tai")))
# vợ chồng nói chung (pp.467-471)
add("C01", "p.467", "can sinh chi là chồng yêu vợ, chi sinh can là vợ yêu chồng", "marriage", "pos", "vợ chồng thương nhau", "can ngày và chi ngày sinh cho nhau",
    eq("bazi.k.day_sheng", True), "Can sinh chi: chồng thương vợ; chi sinh can: vợ thương chồng (xét hành của can ngày và chính khí của chi ngày).", say="{day_sheng}")
add("C02", "p.470", "Trụ ngày bị thương quan là vợ chồng không hoà thuận nhau", "marriage", "neg", "vợ chồng khó hòa thuận", "chi ngày mang Thương Quan", DAY("Thương Quan"))
add("C03", "p.471", "Ngày giờ đối xung nhau thì vợ chồng bất hoà", "marriage", "neg", "vợ chồng dễ bất hòa", "chi ngày và chi giờ xung nhau", eq("bazi.k.dh_clash", True),
    "Vế 'không lợi cho con' của câu sách không đưa vào văn.")

# ---------------- tổ hợp Thập thần (REVIEW-19 W6, 2026-10-23): the named shapes, found by kin._patterns; a good shape's line only while it is not
# broken (pt_pha), a fault's line with its rescue where a page names one. Thực chế Sát p.535 was Q03 (same words): now keyed on the shape.
add("PT_TCS1", "p.535", "Thực thần chế ngự sát là anh hùng áp đảo hàng vạn người", "rank", "pos", "có bản lĩnh trội hơn người, đứng ra gánh việc được",
    "Thực Thần đứng sát chế Thất Sát", PT_OK("thuc_che_sat"), pt="thuc_che_sat")
add("PT_TCS2", "p.533", "Thực thần chế ngự sát thì vợ vinh hiển, con hiển đạt", "marriage", "pos", "vợ con được nhờ, hiển đạt", "Thực Thần đứng sát chế Thất Sát",
    ALL(PT_OK("thuc_che_sat"), MALE), pt="thuc_che_sat")
add("PT_TCS3", "p.533", "trong trụ không có kiêu thần là bậc quan quản việc giáo dục trong triều", "work", "pos", "hợp việc quản lý, nhất là ngành giáo dục",
    "Thực Thần đứng sát chế Thất Sát, lá số không có Thiên Ấn", ALL(PT("thuc_che_sat"), no(GOD("Thiên Ấn"))), pt="thuc_che_sat")
add("PT_TCS4", "p.535", "Sát có chế ngự mà không gặp kiêu, nếu không nắm quyền sinh sát thì cũng giữ chức tòa án binh", "work", "pos",
    "hợp việc cần quyền quyết và kỷ luật (tư pháp, quân đội)", "Thất Sát được Thực Thần đứng sát chế, lá số không có Thiên Ấn",
    ALL(PT("thuc_che_sat"), no(GOD("Thiên Ấn"))), pt="thuc_che_sat", note="'Tòa án binh', 'quyền sinh sát': chữ của sách; văn nói nhóm việc tương ứng ngày nay.")
add("PT_SAT1", "p.551", "Sát ấn tương sinh cho nhau thì có lợi cho công danh", "rank", "pos", "có lợi cho công danh", "Thất Sát sinh Ấn, chữ Ấn đứng sát nhật chủ",
    PT_OK("sat_an_tuong_sinh"), pt="sat_an_tuong_sinh")
add("PT_SAT2", "p.547", "Sát ấn đều có là văn, võ song toàn", "rank", "pos", "văn võ song toàn: làm được cả việc chữ nghĩa lẫn việc cần quyết đoán",
    "tứ trụ có cả Thất Sát lẫn Ấn", ALL(GOD("Thất Sát"), P("An")), pt="sat_an_tuong_sinh")
add("PT_TST1", "p.521", "Thương quan sinh tài thì sẽ tự nhiên giàu có", "wealth", "pos", "tự nhiên giàu có", "Thương Quan đứng sát sinh Tài",
    PT_OK("thuong_sinh_tai"), pt="thuong_sinh_tai")
add("PT_TST2", "p.522", "Trong Tứ trụ thương quan sinh ra tài thì nguồn của dồi dào", "wealth", "pos", "của cải đến dồi dào", "Thương Quan đứng sát sinh Tài",
    PT_OK("thuong_sinh_tai"), pt="thuong_sinh_tai")
add("PT_TST3", "p.535", "Thương quan gặp tài là chức cao mà của nhiều", "rank", "pos", "chức cao mà của nhiều", "lá số có Thương Quan gặp Tài, không có Chính Quan",
    ALL(GOD("Thương Quan"), P("Tai"), no(GOD("Chính Quan"))), pt="thuong_sinh_tai",
    note="Khi lá số có cả Chính Quan, tr.541 ('thương quan gặp quan là vừa không có quan vừa không có của') đứng thay: hai lời không nói cùng lúc.")
add("PT_TSS1", "p.525", "Thương quan thực thần mừng được sinh tài, thì phú quý do trời sắp sặt", "wealth", "pos", "phú quý tự đến", "Thực Thần đứng sát sinh Tài",
    ALL(PT_OK("thuc_sinh_tai"), no(V("Tai"))), pt="thuc_sinh_tai",
    note="Câu sách được dẫn ở tr.525 cho một lá số ví dụ. Khi Tài nhiều, tr.521 ('Thực thần gặp tài, nhưng tài nhiều thì không sang mà chỉ là trọc phú') đứng thay.")
add("PT_TSS2", "p.521", "Thực thần gặp tài, nhưng tài nhiều thì không sang mà chỉ là trọc phú", "wealth", "neutral", "giàu mà không sang", "Thực Thần đứng sát sinh Tài mà Tài nhiều",
    ALL(PT("thuc_sinh_tai"), V("Tai")), pt="thuc_sinh_tai")
add("PT_TQ1", "p.165", "Thân vượng, tài quan tương sinh là phú quý song toàn", "wealth", "pos", "phú quý song toàn", "nhật chủ vượng, Tài đứng sát sinh Chính Quan",
    ALL(PT_OK("tai_quan_song_my"), STRONG), pt="tai_quan_song_my")
add("PT_HSQ", "p.533", "Quan tinh xen kẽ với thất sát, nếu hợp với thất sát là quý", "rank", "pos", "được quý: đường danh, chức sáng", "Chính Quan và Thất Sát cùng có, Thất Sát bị hợp đi",
    PT("hop_sat_luu_quan"), pt="hop_sat_luu_quan")
add("PT_HQS", "p.533", "nếu hợp mất quan tinh thì không tốt", "rank", "neg", "đường chức vụ không tốt", "Chính Quan và Thất Sát cùng có, Chính Quan bị hợp đi",
    PT("hop_quan_luu_sat"), pt="hop_quan_luu_sat")
add("PT_TPA1", "p.166", "Tài là kị thần vượng, dụng thần là ấn. Tài phá ấn nên nghèo", "wealth", "neg", "dễ túng thiếu", "Tài nhiều đứng sát phá Ấn, mà Ấn là dụng thần",
    ALL(PT("tai_pha_an"), YONG("An"), V("Tai"), no(has("bazi.k.pt_cuu", "tai_pha_an"))), pt="tai_pha_an", hi=True)
add("PT_TKQ", "p.541", "Trong trụ thương quan gặp quan là vừa không có quan vừa không có của", "rank", "neg", "khó giữ chức mà cũng khó giữ của",
    "Thương Quan đứng sát khắc Chính Quan", PT("thuong_kien_quan"), pt="thuong_kien_quan")
add("PT_TKD1", "p.166", "Thân vượng, tài yếu lại không có nguồn, huynh đệ tỉ kiếp chia nhau cướp đoạt nên mất tài", "wealth", "neg", "dễ hao tiền vì người khác chia phần",
    "nhật chủ vượng, Tài yếu, Thực Thương không lộ can, có Tỉ Kiếp", ALL(PT("ti_kiep_doat_tai"), no(T("ThucThuong")), no(has("bazi.k.pt_cuu", "ti_kiep_doat_tai"))), pt="ti_kiep_doat_tai")
add("PT_TKD2", "p.167", "Kiếp nặng tài nhẹ, quan có thể khắc kiếp. Thân vượng kiếp tài quan có thể bảo hộ tài, tài nhẹ cho nên sang nhiều hơn giàu", "wealth", "neutral",
    "sang nhiều hơn giàu: danh, chức dễ đến hơn tiền", "nhật chủ vượng, Tỉ Kiếp nặng, Tài nhẹ mà có Quan Sát giữ Tài",
    ALL(PT("ti_kiep_doat_tai"), V("Ti"), P("QuanSat")), pt="ti_kiep_doat_tai")
# ---------------- từng nhóm Thập thần mạnh / yếu (REVIEW-19 W6): tính cách, nghề, tiền theo các trang đã chép (pp.520-554, 166)
add("G01", "p.520", "Tài lộ rõ là người hào phóng khảng khái", "character", "pos", "là người hào phóng, khảng khái", "Tài lộ trên thiên can", T("Tai"))
add("G02", "p.520", "Tài nhiều, thân nhược cần có ấn thụ để hỗ trợ thân", "wealth", "neutral", "cần có Ấn đỡ thân thì mới giữ được Tài", "Tài nhiều mà nhật chủ nhược",
    ALL(V("Tai"), WEAK))
add("G03", "p.521", "thân suy không thắng tài là người vất vả", "wealth", "neg", "dễ vất vả vì tiền", "Tài nhiều mà nhật chủ nhược, không có Tỉ Kiếp đỡ",
    ALL(V("Tai"), WEAK, no(P("Ti"))), "Khi có Tỉ Kiếp đỡ thân, tr.522 ('Tài nhiều gặp tỉ kiếp trợ giúp là nhà giàu thịnh vượng') đứng thay.")
add("G04", "p.522", "Chính tài là của ít", "wealth", "neutral", "của cải đến đều nhưng không lớn", "Tài trong lá số chỉ là Chính Tài",
    ALL(GOD("Chính Tài"), no(GOD("Thiên Tài"))))
add("G05", "p.522", "thiên tài là của nhiều", "wealth", "pos", "của cải có thể lớn", "Tài trong lá số chỉ là Thiên Tài", ALL(GOD("Thiên Tài"), no(GOD("Chính Tài"))))
add("G06", "p.522", "Thực thần gặp ấn là tiền của ngày một nhiều", "wealth", "pos", "tiền của ngày một nhiều", "lá số có Thực Thần gặp Chính Ấn, không có Thiên Ấn",
    ALL(GOD("Thực Thần"), GOD("Chính Ấn"), no(GOD("Thiên Ấn"))), "Thiên Ấn (kiêu) gặp Thực Thần thì tr.527 ('Thực thần gặp kiêu là tài vật hao tán') đứng thay.")
add("G07", "p.522", "Quan hưu tù, ấn vượng là được nhiều tiền của", "wealth", "pos", "được nhiều tiền của", "Quan Sát yếu, Ấn vượng, nhật chủ nhược",
    ALL(P("QuanSat"), N("QuanSat"), V("An"), WEAK), "Khi nhật chủ vượng, tr.527 ('Thân vượng, ấn vượng là tiền hao tán không tụ') đứng thay.")
add("G08", "p.522", "Thân mạnh, tài vượng thì có lợi cho thanh danh", "rank", "pos", "có lợi cho thanh danh", "nhật chủ vượng mà Tài cũng vượng", ALL(STRONG, V("Tai")))
add("G09", "p.530", "Trong mệnh không có tài thì không nên làm gắng", "work", "neutral", "không nên gắng theo đường buôn bán", "tứ trụ không có Tài", A("Tai"),
    "Câu sách được dẫn ở tr.530 cho một lá số ví dụ (người buôn bán thua lỗ).")
add("G10", "p.541", "Trong trụ không có quan tinh thì khó mà làm quan", "rank", "neg", "khó đi đường chức vụ", "tứ trụ không có Quan Sát", ALL(A("QuanSat"), no(A("Tai"))))
add("G11", "p.541", "Vừa không có quan tinh lại không có tài tinh thì không thể làm quan", "rank", "neg", "đường chức vụ khó thành", "tứ trụ không có cả Quan Sát lẫn Tài",
    ALL(A("QuanSat"), A("Tai")))
add("G12", "p.541", "Người mà thương quan nhiều thì khó mà làm quan, nếu có thì chức nhỏ", "rank", "neg", "khó theo đường chức vụ, nếu có thì chức nhỏ",
    "Thực Thương nhiều, có Thương Quan", ALL(GOD("Thương Quan"), V("ThucThuong")))
add("G13", "p.541", "Có quan mà không có ấn thì chỉ là tạm thời", "rank", "neg", "chức vụ dễ chỉ là tạm thời", "có Quan Sát mà không có Ấn", ALL(P("QuanSat"), A("An")))
add("G14", "p.542", "Ngày nhược gặp quan tinh thì thành đạt không lâu", "rank", "neg", "thành đạt khó lâu bền", "nhật chủ nhược mà có Quan Sát", ALL(WEAK, P("QuanSat")))
add("G15", "p.548", "Ấn thụ nhiều là người thông minh", "character", "pos", "là người thông minh", "Ấn nhiều", V("An"))
add("G16", "p.554", "Có thương quan mà không có tài quan thì tuy thông minh khéo léo nhưng vẫn không thành đạt gì", "character", "neg",
    "thông minh khéo léo nhưng khó thành đạt", "có Thương Quan mà không có Tài và Quan Sát", ALL(GOD("Thương Quan"), A("Tai"), A("QuanSat")))
add("G17", "p.547", "Tài quan thực đều có thì thông minh tuấn tú, văn chương xuất chúng", "character", "pos", "thông minh, giỏi chữ nghĩa", "có đủ Tài, Quan Sát và Thực Thần",
    ALL(P("Tai"), P("QuanSat"), GOD("Thực Thần")))
add("G18", "p.166", "Thân nhược tài nặng lại gặp thực thương nặng, thực thương sẽ xì hơi thân, sinh tài, làm cho thân không gánh được tài nên nghèo", "wealth", "neg",
    "dễ túng thiếu vì thân không gánh nổi Tài", "nhật chủ nhược, Tài nặng, Thực Thương cũng nặng, không có Tỉ Kiếp đỡ", ALL(WEAK, V("Tai"), V("ThucThuong"), no(P("Ti"))),
    "Khi có Tỉ Kiếp đỡ thân, tr.522 ('Tài nhiều gặp tỉ kiếp trợ giúp là nhà giàu thịnh vượng') đứng thay.")
add("G19", "p.521", "Tài nhiều lại dựa vào ấn thụ để hộ thân là người có vợ hiền, con đẹp, cuối đời hạnh phúc", "marriage", "pos", "gia đạo êm ấm, cuối đời yên vui",
    "Tài nhiều, nhật chủ nhược mà có Ấn hộ thân", ALL(V("Tai"), WEAK, P("An")), "Vế về dung mạo con cái của câu sách không đưa vào văn.")

rules, meta = [], {}
SRC = {"id": "SRC_TVH_KIN", "title": "Dự Đoán Theo Tứ Trụ (Thiệu Vĩ Hoa) — lục thân, tài vận, quan vận, hôn nhân", "author": "Thiệu Vĩ Hoa",
       "locator": "trang in 149-155, 463-478, 520-537 (bản scan; chép lại trong data/bazi_deep/mined/tvh_pNNN.txt)", "verified": True, "edition": None,
       "note": "Chép từ ảnh trang (Claude, 2026-10-23), đối chiếu từng câu được dùng với ảnh; câu in nguyên văn trong quotes_tvh_kin.json."}
for r in R:
    rules.append({"id": r["id"], "system": "bat_tu", "schoolId": "tvh_tu_tru", "category": f"tvh_kin_{r['topic']}",
                  "description": f"Thiệu Vĩ Hoa {r['page']}: {r['quote']} — {r['effect']} ({r['cause']})", "conditions": r["cond"],
                  "consequences": [{"kind": "finding", "claim": r["id"].lower(), "effect": {"pos": "support", "neg": "limit"}.get(r["tone"], "neutral"), "scope": "natal"}],
                  "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": [SRC["id"]], "reviewStatus": "verified", "version": "0.1.0", "subject": "chart"})
    meta[r["id"]] = {k: r[k] for k in ("page", "quote", "topic", "tone", "effect", "cause")} | {"book": r["book"]} | ({"note": r["note"]} if r["note"] else {}) \
        | ({"hi": True} if r["hi"] else {}) | ({"say": r["say"]} if r["say"] else {}) | ({"pt": r["pt"]} if r["pt"] else {})
assert len({r["id"] for r in rules}) == len(rules)
(D / "pack_tvh_kin.json").write_text(json.dumps({"sources": [SRC], "rules": rules}, ensure_ascii=False, indent=1) + "\n", "utf-8")
(D / "quotes_tvh_kin.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", "utf-8")
print(len(rules), "rules")
