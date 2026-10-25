"""DEEP-3 Bát Tự mining (2026-10-24): adds the newly page-checked judgements to the three kin packs IN PLACE (the older builders
build_bazi_{kin,ttt_kin,tvh_kin}_pack.py regenerate whole packs and would drop later fixes, so this one only replaces the rules it owns):
  - Trích Thiên Tủy (text layer, mined/ttt_pNNN.txt): Thể Dụng p.63 / Cương Nhu p.109 / Phản cục p.188 dụng-thần choice (topic 'yong'), Nguyệt
    Lệnh p.67, Thanh Khí p.101, Trọc Khí p.103, Chân Thần p.105, Hà Tri pp.143-144 (topic 'fortune'), Trung Hòa p.77, Tài Đức p.161, Con Cái p.130;
  - Thiệu Vĩ Hoa (scan, transcribed in mined/tvh_pNNN.txt): con cái pp.158-159, phú / bần / quý / tiện pp.162-171, quan / danh pp.532, 546,
    552-553;
  - 八字真宗 (text layer, mined/zz_pNN.txt): 日干五行直断 p.26, 五行缺 pp.26-27, 日月合化直断夫妻 pp.28-29, 四柱干支合化 p.29.
Every entry of the mined lists (mined/rules_ttt_deep3.md, rules_zz_26_30.md, rules_148_173.md, rules_519_556.md) that is not packed here carries
its reason there; docs/audit/DEEP-3-mining-bazi.md counts them.
    .venv/bin/python tools/build_bazi_deep3_pack.py
Rules flagged HARSH (a printed verdict on morality / intelligence, or a slur on a spouse) are packed with their quote but stay `draft` (draft
rules never fire) until the owner decides."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data" / "bazi_deep"
eq = lambda f, v: {"fact": f, "value": v}
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
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
L = lambda g: ALL(P(g), N(g))                      # 'khinh / nhẹ / suy': present but light (absent is told by A)
HI = lambda g: has("bazi.k.hi", g)
KY = lambda g: has("bazi.k.ky", g)
YONG = lambda g: has("bazi.k.yong", g)
GOD = lambda g: has("bazi.k.gods", g)
TG = lambda g: has("bazi.k.trans_gods", g)
ADJ = lambda a, b: has("bazi.k.adj", "|".join(sorted((a, b))))
PT = lambda pid: has("bazi.k.pt", pid)
PT_OK = lambda pid: ALL(PT(pid), no(has("bazi.k.pt_pha", pid)))
MONTH = lambda g: eq("bazi.k.month_group", g)
MALE, FEMALE = eq("bazi.k.gender", "nam"), eq("bazi.k.gender", "nữ")
HOUR_B = lambda *gods: inn("bazi.k.hour_branch_god", list(gods))
GROUPS = ("Ti", "ThucThuong", "Tai", "QuanSat", "An")
CONV = ("'Vượng / nhiều / nặng', 'nhược / khinh / nhẹ' của một nhóm thập thần: phần độ của nhóm trên tổng độ Thiệu Vĩ Hoa (tr.331-355) từ 25 % / "
        "dưới 12 % (Tỉ Kiếp không tính độ của chính nhật chủ), 'khinh' còn đòi nhóm có mặt — ngưỡng của hệ thống; 'không có': không có cả can lẫn "
        "tàng can; 'sinh, phá, chế, kề': hai chữ đứng sát nhau (cùng trụ, hoặc cùng hàng của hai trụ liền nhau).")
HI_NOTE = ("'Dụng', 'hỉ', 'kỵ': theo bảng dụng thần và vận tốt, xấu của cách (Thiệu Vĩ Hoa tr.378-386; hỉ gồm cả dụng), nên lời này chỉ đứng khi "
           "cách đứng được.")
SRC = {
    "ttt": {"id": "SRC_TTT_DEEP3", "title": "Trích Thiên Tủy — Bát Cách, Thể Dụng, Nguyệt Lệnh, Trung Hòa, Thanh / Trọc, Chân / Giả thần, Con Cái, "
            "Hà Tri, Tài Đức, Nhàn Thần, Phản cục", "author": "Lưu Bá Ôn / Nhậm Thiết Tiều",
            "locator": "PDF pp.59-78, 101-112, 130-132, 143-148, 161-170, 183-201, 229-233 (text layer in data/bazi_deep/mined/)", "verified": True,
            "edition": None, "note": "Đọc trực tiếp lớp chữ của bản PDF (Claude, DEEP-3, 2026-10-24); danh sách đầy đủ các câu đã đọc và lý do bỏ "
            "trong mined/rules_ttt_deep3.md."},
    "tvh": {"id": "SRC_TVH_DEEP3", "title": "Dự Đoán Theo Tứ Trụ (Thiệu Vĩ Hoa) — con cái, phú quý bần tiện, cát hung theo dụng thần, công danh",
            "author": "Thiệu Vĩ Hoa", "locator": "trang in 158-159, 162-171, 532, 546, 552-553 (bản scan; chép lại trong data/bazi_deep/mined/tvh_pNNN.txt)",
            "verified": True, "edition": None, "note": "Chép từ ảnh trang (2026-10-23), đóng gói DEEP-3 (2026-10-24); mọi câu được dùng đối chiếu "
            "với trang chép; danh sách đầy đủ trong mined/rules_148_173.md, rules_519_556.md."},
    "zz": {"id": "SRC_ZZ_DEEP3", "title": "八字真宗 — 日干五行直断、五行强旺弱缺、日月合化直断夫妻、四柱干支合化直断",
           "author": "unknown (PDF circulated via ChienNguyen)", "locator": "PDF pp.26-29 (text layer in data/bazi_deep/mined/)", "verified": True,
           "edition": "PDF, simplified Chinese, 96 pp.", "note": "Đọc trực tiếp lớp chữ của bản PDF (DEEP-3, 2026-10-24); danh sách đầy đủ trong "
           "mined/rules_zz_26_30.md."},
}
PREFIX = {"ttt": "BT_TTTK_", "tvh": "BT_TVHK_", "zz": "BT_ZZK_"}
SCHOOL = {"ttt": "ttt_nham_thi", "tvh": "tvh_tu_tru", "zz": "bazi_zhenzong_popular"}
NAME = {"ttt": "Trích Thiên Tủy", "tvh": "Thiệu Vĩ Hoa", "zz": "八字真宗"}
TOPICS = {"wealth", "work", "rank", "parents", "marriage", "siblings", "year", "character", "children", "study", "fortune", "yong"}
R = {"ttt": [], "tvh": [], "zz": []}


def add(book, rid, page, quote, topic, tone, effect, cause, cond, note=None, hi=False, say=None, pt=None, harsh=False, yong=None, conv=True):
    assert topic in TOPICS, topic
    R[book].append({"id": PREFIX[book] + rid, "page": page, "quote": quote, "topic": topic, "tone": tone, "effect": effect, "cause": cause,
                    "cond": cond, "note": " ".join(x for x in (note, CONV if conv else None, HI_NOTE if hi else None) if x), "hi": hi, "say": say,
                    "pt": pt, "harsh": harsh, "yong": yong})


def any_group(f):
    return ANY(*[f(g) for g in GROUPS])


# ================================================================ Trích Thiên Tủy
# ---- dụng thần by Thể Dụng p.63 (and Cương Nhu p.109, Phản cục p.188): topic 'yong' = which group this book takes as dụng thần
add("ttt", "DT01", "p.63", "nhật chủ vượng, ấn thụ nhiều, cần phải lấy tài tinh làm dụng thần", "yong", "neutral", "lấy Tài làm dụng thần",
    "nhật chủ vượng, Ấn nhiều", ALL(STRONG, V("An")), yong="Tai")
add("ttt", "DT02", "p.63", "nhật chủ vượng, quan sát khinh, cũng lấy tài tinh làm dụng thần", "yong", "neutral", "lấy Tài làm dụng thần",
    "nhật chủ vượng, Quan Sát nhẹ", ALL(STRONG, L("QuanSat")), yong="Tai")
add("ttt", "DT03", "p.63", "Nhật chủ vượng, tỉ kiếp nhiều, gánh được tài tinh, lấy thực thương làm dụng thần", "yong", "neutral",
    "lấy Thực Thương làm dụng thần", "nhật chủ vượng, Tỉ Kiếp nhiều, Tài có mặt mà không nhẹ", ALL(STRONG, V("Ti"), P("Tai"), no(N("Tai"))), yong="ThucThuong")
add("ttt", "DT04", "p.63", "nhật chủ vượng, tỉ kiếp nhiều, mà tài tinh khinh, cũng lấy thực thương làm dụng thần", "yong", "neutral",
    "lấy Thực Thương làm dụng thần", "nhật chủ vượng, Tỉ Kiếp nhiều, Tài nhẹ", ALL(STRONG, V("Ti"), L("Tai")), yong="ThucThuong")
add("ttt", "DT05", "p.63", "Nhật chủ vượng, quan tinh khinh, ấn thụ trọng điệp, lấy tài tinh làm dụng thần", "yong", "neutral", "lấy Tài làm dụng thần",
    "nhật chủ vượng, Quan nhẹ, Ấn trùng điệp", ALL(STRONG, L("QuanSat"), V("An")), yong="Tai")
add("ttt", "DT06", "p.63", "Nhật chủ nhược, thực thương nhiều, lấy ấn thụ làm dụng thần", "yong", "neutral", "lấy Ấn làm dụng thần",
    "nhật chủ nhược, Thực Thương nhiều", ALL(WEAK, V("ThucThuong")), yong="An",
    note="Cùng trang: vì vậy không thể cứ thấy Thiên Ấn gặp Thực Thần mà luận 'kiêu đoạt thực'; phải xét nhật chủ mạnh yếu trước.")
add("ttt", "DT07", "p.63", "nhật chủ nhược, tài tinh vượng, tất lấy tỉ kiếp làm dụng thần", "yong", "neutral", "lấy Tỉ Kiếp làm dụng thần",
    "nhật chủ nhược, Tài vượng", ALL(WEAK, V("Tai")), yong="Ti")
add("ttt", "DT08", "p.109", "Nói chung đắc thời đương lệnh, tứ trụ không có khắc chế, dụng thực thần thuận theo khí thế, tiết kỳ tinh anh", "yong",
    "neutral", "lấy Thực Thương làm dụng thần, thuận theo khí thế mà tiết", "nhật chủ vượng, đắc lệnh tháng, tứ trụ không có Quan Sát",
    ALL(STRONG, MONTH("Ti"), A("QuanSat")), yong="ThucThuong", note="'Đắc thời đương lệnh': chính khí chi tháng cùng hành với nhật chủ.")
add("ttt", "DT09", "p.188", "trong cục Ấn thụ tuy vượng, trong trụ Tài tinh có khí, có thể dụng Tài phá Ấn vậy", "yong", "neutral",
    "lấy Tài phá Ấn", "Ấn vượng mà Tài có khí", ALL(V("An"), P("Tai"), no(N("Tai"))), yong="Tai")
add("ttt", "DT10", "p.188", "Mẫu từ diệt Tử, dẫu có Tài tinh mà vô khí, không thể lấy Tài tinh phá Ấn vậy", "yong", "neutral",
    "không lấy Tài phá Ấn được, phải thuận theo Ấn mà đi đất Tỉ Kiếp", "Ấn vượng mà Tài yếu hoặc không có", ALL(V("An"), N("Tai")), yong="Ti",
    note="Cùng trang: 'Tuế vận vẫn hành đất Tỉ Kiếp, để Mẫu từ mà Tử an'.")
# ---- cát / hung by dụng, hỉ, kỵ (topic 'fortune')
add("ttt", "HK01", "p.143", "không có hỉ thần mà dụng thần đắc lệnh hùng tráng, đại thế kiên cố, tứ trụ an hòa, dụng thần đứng cạnh, không tranh không đố, "
    "tức gặp kỵ thần cũng không hung hiểm", "fortune", "pos", "gốc vững: dù gặp chữ kỵ cũng khó thành hung hiểm", "dụng thần nắm lệnh tháng và vượng",
    any_group(lambda g: ALL(YONG(g), MONTH(g), V(g))), hi=True, say="dụng thần {yong_vi} nắm lệnh tháng và vượng")
add("ttt", "HK02", "p.143", "Như nguyên cục không có hỷ thần, có kỵ thần (hoặc ám phục hoặc xuất hiện), hoặc đứng sát bên dụng thần", "fortune", "neg",
    "dễ gặp trắc trở khi vận, năm dẫn chữ kỵ lên", "lá số không có chữ hỉ (ngoài dụng thần), mà chữ kỵ đứng sát dụng thần",
    ALL(eq("bazi.k.hi_absent", True), eq("bazi.k.ky_adj_yong", True)), hi=True,
    note="Câu sách viết tiếp 'hung họa lập tức đến' khi tuế vận trợ kỵ thần; văn nói mức nhẹ, không nói tai họa.")
add("ttt", "HK03", "p.144", "Tài Quan vô khí, dụng thần vô lực, chẳng qua không thể phát đạt được mà thôi, cũng không có hình hung vậy", "fortune",
    "neutral", "khó phát đạt lớn, nhưng cũng không vì thế mà có hung họa", "Tài và Quan Sát đều yếu, dụng thần cũng yếu",
    ALL(N("Tai"), N("QuanSat"), eq("bazi.k.yong_weak", True)), hi=True)
add("ttt", "HK05", "p.67", "hỉ thần đắc lệnh thì cát lợi", "fortune", "pos", "cát lợi, vì chữ lá số cần nắm được lệnh tháng", "chữ hỉ (hoặc dụng) nắm lệnh tháng",
    any_group(lambda g: ALL(HI(g), MONTH(g))), hi=True)
add("ttt", "HK06", "p.101", "hỉ thần nên đắc địa phùng sanh, cùng nhật chủ kề cận là cát lợi", "fortune", "pos", "chữ có lợi ở ngay bên mình, dễ được trợ lực",
    "chữ hỉ (hoặc dụng) đứng kề nhật chủ, chữ kỵ không đứng kề", ALL(eq("bazi.k.hi_near", True), eq("bazi.k.ky_near", False)), hi=True,
    note="'Kề nhật chủ': chi ngày, can tháng, can giờ (ba chỗ kề nhật chủ, như Bát Tự Chân Tông tr.50). Tr.165 nói cùng ý: 'thần yêu thích, gần thì "
    "càng thân thiết'.")
add("ttt", "HK07", "p.101", "kỵ thần nên thất thế lâm tuyệt địa, cùng nhật chủ xa cách thì đẹp vậy", "fortune", "neg",
    "chữ bất lợi ở ngay bên mình, sức cản đến gần", "chữ kỵ đứng kề nhật chủ, chữ hỉ không đứng kề",
    ALL(eq("bazi.k.ky_near", True), eq("bazi.k.hi_near", False)), hi=True,
    note="'Kề nhật chủ': chi ngày, can tháng, can giờ. Tr.165: 'thần đáng ghét, may mắn là ở xa'.")
add("ttt", "CT01", "p.105", "Nói nhật chủ có dụng thần, nắm lệnh tại đề cương, lại thấu xuất thiên can gọi là tụ đắc chân thần, cuộc đời phú quý hĩ",
    "fortune", "pos", "được 'chân thần': đời dễ phú quý", "dụng thần nắm lệnh tháng lại lộ ra can", any_group(lambda g: ALL(YONG(g), MONTH(g), T(g))),
    hi=True, say="dụng thần {yong_vi} nắm lệnh tháng và lộ can")
add("ttt", "CT02", "p.105", "Nhưng nếu kề sát chân thần, hoặc tương khắc tương xung chân thần, hoặc hợp chân thần, ám hóa kỵ thần, chung thân lục đục",
    "fortune", "neg", "đời nhiều va vấp, lục đục", "dụng thần nắm lệnh tháng mà có chữ khắc nó đứng sát chi tháng", eq("bazi.k.yong_month_hit", True),
    hi=True, note="Chỉ xét vế 'kề sát ... tương khắc' (chữ khắc nhóm dụng thần đứng sát chi tháng); vế xung, hợp chưa xét.")
# ---- Trọc khí p.103: which character makes the chart turbid
TROC_EFF = "thành bại không đều, nhiều trắc trở; gặp vận khử được chữ ấy mới có cơ khởi phát"
add("ttt", "TR01", "p.103", "Hoặc quan suy hỉ ấn, tài tinh khắc ấn, cách này tài là trọc vậy", "fortune", "neg", TROC_EFF,
    "Quan yếu, lá số cần Ấn mà Tài đứng sát khắc Ấn: Tài là chữ làm đục", ALL(N("QuanSat"), HI("An"), ADJ("Tai", "An")), hi=True,
    note="Hậu quả của trọc: cùng trang, 'tuy thành bại không đều, có nhiều hiểm trở, nhưng ngộ đắc hành vận, khử đi trọc khí, cũng có cơ hội khởi phát'.")
add("ttt", "TR02", "p.103", "Hoặc quan suy hỉ tài, tỉ kiếp tranh tài, cách này kiếp là trọc vậy", "fortune", "neg", TROC_EFF,
    "Quan yếu, lá số cần Tài mà Tỉ Kiếp đứng sát tranh Tài: Kiếp là chữ làm đục", ALL(N("QuanSat"), HI("Tai"), ADJ("Ti", "Tai")), hi=True)
add("ttt", "TR03", "p.103", "Hoặc tài vượng hỉ kiếp, quan tinh chế kiếp, cách này quan là trọc vậy", "fortune", "neg", TROC_EFF,
    "Tài vượng, lá số cần Tỉ Kiếp mà Quan Sát đứng sát chế Kiếp: Quan là chữ làm đục", ALL(V("Tai"), HI("Ti"), ADJ("QuanSat", "Ti")), hi=True)
add("ttt", "TR04", "p.103", "Hoặc thân cường sát thiển, thực thương chế sát, cách này thực thương là trọc vậy", "fortune", "neg", TROC_EFF,
    "nhật chủ mạnh, Sát nhẹ mà Thực Thương đứng sát chế Sát: Thực Thương là chữ làm đục",
    ALL(STRONG, L("QuanSat"), GOD("Thất Sát"), ADJ("ThucThuong", "QuanSat")))
# ---- Trung Hòa p.77
add("ttt", "TH01", "p.77", "quan suy thương quan vượng thiếu danh vị", "rank", "neg", "thiếu danh vị", "Quan yếu mà Thương Quan vượng",
    ALL(L("QuanSat"), GOD("Thương Quan"), V("ThucThuong")))
add("ttt", "TH02", "p.77", "sát cường chế nhược tiền bạc thiếu thốn", "wealth", "neg", "tiền bạc dễ thiếu thốn", "Thất Sát mạnh mà chữ chế Sát (Thực Thương) yếu",
    ALL(GOD("Thất Sát"), V("QuanSat"), N("ThucThuong")), note="Cùng câu sách còn hai vế về vợ, con ('không có vợ', 'không có con'): không đưa vào văn.")
# ---- Tài Đức p.161 (character)
DUC_GOOD = ANY(ALL(HI("QuanSat"), ADJ("Tai", "QuanSat")), ALL(HI("Tai"), ADJ("QuanSat", "Ti")), ALL(KY("An"), ADJ("Tai", "An")), ALL(HI("An"), ADJ("QuanSat", "An")))
DUC_BAD = ANY(ALL(HI("QuanSat"), ADJ("Ti", "QuanSat")), ALL(HI("Tai"), ADJ("Tai", "An")), ALL(KY("An"), ADJ("QuanSat", "An")), ALL(HI("An"), ADJ("Tai", "An")))
add("ttt", "DUC1", "p.161", "hỉ Quan mà Tài có thể sinh Quan; hỉ Tài mà Quan có thể khắc chế Kiếp, kỵ Ấn mà Tài có thể phá Ấn; hỉ Ấn mà Quan có thể sinh Ấn",
    "character", "pos", "hành xử ngay thẳng, có phong thái người quân tử", "chữ lá số cần được chữ đứng sát nó giúp đúng chiều",
    ALL(DUC_GOOD, no(DUC_BAD)), hi=True, note="Cùng trang, đó là dấu hiệu của 'cách chính cục thanh', 'đều là phong cách quân tử vậy'.")
add("ttt", "DUC2", "p.161", "hỉ Quan mà lâm Kiếp địa, hỉ Tài mà cư nơi Ấn, kỵ Ấn mà Quan tinh sinh Ấn, hỉ Ấn mà Tài phá Ấn", "character", "neg",
    "dễ chạy theo thế và lợi", "chữ lá số cần bị chữ đứng sát nó làm hỏng", ALL(DUC_BAD, no(DUC_GOOD)), hi=True,
    note="Cùng trang gọi là 'tượng đa năng', và nói thêm: 'được khí thế hòa bình, dụng thần rõ ràng, hành động nhất định cũng chân chính vậy'.")
# ---- Con cái p.130 (only the non-number, non-sex judgements)
add("ttt", "CC02", "p.130", "Nhật chủ vượng, Ấn thụ trọng, Thực Thương khinh, có Tài tinh, dự phòng con nhiều mà hiền", "children", "pos", "con cái hiền",
    "nhật chủ vượng, Ấn nặng, Thực Thương nhẹ, có Tài", ALL(STRONG, V("An"), L("ThucThuong"), P("Tai"), no(N("QuanSat"))),
    note="Vế về số con của câu sách không đưa vào văn. Khi Quan Sát cũng nhẹ, cùng trang 'có con tất nghịch' đứng thay (hai lời không nói cùng lúc).")
add("ttt", "CC03", "p.130", "Nhật chủ vượng, Ấn thụ trọng, Quan Sát khinh, có Ấn thụ, gặp Tài, có con tất nghịch", "children", "neg", "con cái có đứa ương bướng",
    "nhật chủ vượng, Ấn nặng, Quan Sát nhẹ, có Tài", ALL(STRONG, V("An"), N("QuanSat"), P("Tai"), no(L("ThucThuong"))))

# ================================================================ Thiệu Vĩ Hoa
# ---- con cái pp.158-159 (rows flagged '-' in mined/rules_148_173.md; thần sát rows left out as in DEEP-BAZI-2)
add("tvh", "K01", "p.158", "Quan sát vượng, có ấn thụ, gặp tài tinh là con ngỗ ngược", "children", "neg", "con cái dễ ngỗ ngược", "Quan Sát vượng, có Ấn, có Tài",
    ALL(V("QuanSat"), P("An"), P("Tai")))
add("tvh", "K02", "p.158", "Chi giờ đóng tài tinh là con cái thành gia lập nghiệp, hiếu thuận, có phúc", "children", "pos", "con cái thành gia lập nghiệp, hiếu thuận",
    "chi giờ mang Tài", HOUR_B("Chính Tài", "Thiên Tài"), conv=False)
add("tvh", "K03", "p.158", "Chi giờ lâm thiên quan là con cái đôn hậu, tính tình dịu dàng, hiền hiếu, trung thực", "children", "pos",
    "con cái đôn hậu, hiền hiếu, trung thực", "chi giờ mang Thất Sát (thiên quan)", HOUR_B("Thất Sát"), conv=False)
add("tvh", "K04", "p.158", "Chi giờ lâm thực thần, không bị kiêu thần đoạt", "children", "pos", "con cái thành thục, thông minh, nhanh nhẹn; cuối đời yên vui",
    "chi giờ mang Thực Thần, lá số không có Thiên Ấn", ALL(HOUR_B("Thực Thần"), no(GOD("Thiên Ấn"))), conv=False,
    note="Câu sách: '... hoặc thực thần là lộc thần là con cái to lớn, thành thục, thông minh, nhanh nhẹn, cuối đời hạnh phúc'; vế lộc thần chưa xét.")
add("tvh", "K05", "p.158", "Chi giờ lâm chính ấn thì con cái hiếu thuận, dựng nhà lập nghiệp, người đó thân nhược càng tốt", "children", "pos",
    "con cái hiếu thuận, tự dựng nhà lập nghiệp", "chi giờ mang Chính Ấn", HOUR_B("Chính Ấn"), conv=False)
add("tvh", "K06", "p.158", "Thực thần là dụng thần thì con cái hiền lành, thành đạt", "children", "pos", "con cái hiền lành, thành đạt",
    "Thực Thương là dụng thần, lá số có Thực Thần", ALL(YONG("ThucThuong"), GOD("Thực Thần")), hi=True, conv=False)
add("tvh", "K07", "p.158", "Chi giờ là thiên ấn thì con cái tính tình không tốt", "children", "neg", "con cái tính khí khó",
    "chi giờ mang Thiên Ấn, mà Ấn không phải chữ lá số cần", ALL(HOUR_B("Thiên Ấn"), no(HI("An"))), conv=False,
    note="Khi Ấn là hỉ, dụng thần, cùng trang 'thì con cái thành đạt' đứng thay.")
add("tvh", "K08", "p.158", "Nếu thiên ấn là hỉ, dụng thần thì con cái thành đạt", "children", "pos", "con cái thành đạt", "chi giờ mang Thiên Ấn mà Ấn là chữ lá số cần",
    ALL(HOUR_B("Thiên Ấn"), HI("An")), hi=True, conv=False)
add("tvh", "K09", "p.159", "Nếu nhật nhược lại gặp kình dương thì con cái đắc lực", "children", "pos", "con cái đắc lực", "nhật chủ nhược, chi giờ là dương nhận",
    ALL(WEAK, eq("bazi.k.hour_ren", True)), note="Dương nhận theo bảng tr.72 Bát Tự Chân Tông (như mọi chỗ khác của lớp này).")
# ---- phú / bần / quý / tiện pp.162-171 (DUP rows of earlier packs left out: see the md)
add("tvh", "F01", "p.162", "Tài có thể sinh quan, quan bảo hộ cho tài; quan có thể sinh ấn, ấn bảo hộ cho quan. Cho nên tài quan ấn có cả là tiêu chí quan cao, lộc hậu",
    "rank", "pos", "dễ có chức cao, lộc hậu", "Tài đứng sát sinh Quan Sát, Quan Sát đứng sát sinh Ấn", ALL(ADJ("Tai", "QuanSat"), ADJ("QuanSat", "An")))
add("tvh", "F02", "p.164", "Ấn nặng, quan suy, tài nắm lệnh. Tài là dụng thần có thể làm tổn ấn, lại nhờ quan suy, tài không bị chuyển hóa nên giàu", "wealth", "pos",
    "giàu", "Ấn nặng, Quan yếu, Tài nắm lệnh tháng và là dụng thần", ALL(V("An"), N("QuanSat"), MONTH("Tai"), YONG("Tai")), hi=True)
add("tvh", "F03", "p.164", "Ấn vượng, thực thương nhẹ, tài tinh được cách cục. Tài cục có thể đối địch được ấn vượng", "wealth", "pos", "giàu",
    "Ấn vượng, Thực Thương nhẹ, Tài thành cục (tam hợp hoặc tam hội)", ALL(V("An"), N("ThucThuong"), eq("bazi.k.tai_cuc", True)),
    note="Trang này liệt kê các 'điều kiện giàu'.")
add("tvh", "F04", "p.165", "Thân vượng, tỉ kiếp vượng, thực thương vượng, tài ấn suy. Khi tài là dụng thần, tỉ kiếp sinh thực thương, thực thương vượng sinh tài tinh",
    "wealth", "pos", "giàu nhờ Thực Thương sinh Tài", "nhật chủ vượng, Tỉ Kiếp và Thực Thương vượng, Tài và Ấn yếu, Tài là dụng thần",
    ALL(STRONG, V("Ti"), V("ThucThuong"), N("Tai"), N("An"), YONG("Tai")), hi=True)
add("tvh", "F05", "p.165", "Thân vượng lại có tài khí thông thương. Tài vượng lại còn được thực thương sinh nên nguồn rất dồi dào", "wealth", "pos",
    "nguồn tiền rất dồi dào", "nhật chủ vượng, Tài vượng, có Thực Thương đứng sát sinh Tài", ALL(STRONG, V("Tai"), ADJ("ThucThuong", "Tai")))
add("tvh", "F06", "p.166", "Quan sát vượng, gặp tài cục hoặc tài vượng có lợi cho ấn nên tài là kị thần. Thân quá yếu thắng không nổi tài quan vượng nên nghèo",
    "wealth", "neg", "dễ túng thiếu: thân không gánh nổi Tài Quan", "nhật chủ nhược, Quan Sát vượng, Tài cũng vượng hoặc thành cục",
    ALL(WEAK, V("QuanSat"), ANY(V("Tai"), eq("bazi.k.tai_cuc", True))))
add("tvh", "F07", "p.166", "Thực thương nhiều mà dụng thần là ấn, tài được thực thương sinh lại phá hoại ấn thành kị thần", "wealth", "neg", "dễ túng thiếu",
    "Thực Thương nhiều, Ấn là dụng thần, Tài đứng sát phá Ấn", ALL(V("ThucThuong"), YONG("An"), ADJ("Tai", "An")), hi=True)
add("tvh", "F08", "p.166", "Thân nhược, dụng thần là kiếp, quan tinh chế ngự kiếp. Kiếp bị khống chế làm cho thân càng nhược", "wealth", "neg",
    "khó giữ được của: thân đã yếu lại mất chỗ dựa", "nhật chủ nhược, Tỉ Kiếp là dụng thần mà Quan Sát đứng sát chế Kiếp",
    ALL(WEAK, YONG("Ti"), ADJ("QuanSat", "Ti")), hi=True)
add("tvh", "F09", "p.167", "Thân vượng là hỉ của thực thương, nhưng lại bị tài nhẹ, ấn vượng", "wealth", "neg", "khó giàu: Tài nhẹ mà không được sinh",
    "nhật chủ vượng, Thực Thương là chữ cần, Tài nhẹ, Ấn vượng", ALL(STRONG, HI("ThucThuong"), L("Tai"), V("An")), hi=True)
add("tvh", "F10", "p.167", "Thân vượng, quan sát càng vượng, tài nhẹ", "wealth", "neg", "khó giàu: Quan Sát hút hết Tài", "nhật chủ vượng mà Quan Sát cũng vượng, Tài nhẹ",
    ALL(STRONG, V("QuanSat"), L("Tai")), note="Cùng trang: 'đó gọi là kị thần quan sát vượng làm xì hơi tài nên mệnh nghèo'.")
add("tvh", "F11", "p.167", "Thực thương nặng, thân nhược, ấn nhẹ mà ấn là dụng thần", "wealth", "neg", "khó giàu: thân không gánh nổi Tài",
    "nhật chủ nhược, Thực Thương nặng, Ấn nhẹ mà là dụng thần", ALL(WEAK, V("ThucThuong"), L("An"), YONG("An")), hi=True)
add("tvh", "F12", "p.167", "Ấn là dụng thần, tài tinh phá hoại ấn, còn quan tinh sinh hóa hợp lý, ấn tinh được cứu nên tuy nghèo nhưng sang", "rank", "neutral",
    "tuy không giàu nhưng sang", "Ấn là dụng thần bị Tài phá, có Quan Sát nối Tài sang Ấn", ALL(YONG("An"), ADJ("Tai", "An"), ADJ("Tai", "QuanSat"), ADJ("QuanSat", "An")), hi=True)
add("tvh", "F13", "p.167", "Quan sát vượng, thân nhược, tài tinh sinh trợ cho quan sát nhờ có ấn nên dễ được làm quan nhưng vẫn nghèo", "rank", "neutral",
    "dễ có chức nhưng không giàu", "nhật chủ nhược, Quan Sát vượng được Tài sinh, có Ấn", ALL(WEAK, V("QuanSat"), ADJ("Tai", "QuanSat"), P("An")))
add("tvh", "F14", "p.167", "Thân vượng, có ấn, thực thương vượng xì hơi ấn nên không có tài. Chỉ là loại thư sinh, bần nho", "wealth", "neg",
    "học nhiều mà ít của", "nhật chủ vượng, có Ấn, Thực Thương vượng, không có Tài", ALL(STRONG, P("An"), V("ThucThuong"), A("Tai")))
add("tvh", "F15", "p.167", "Trong mệnh không kị tài, còn quan là dụng thần thì phú quý song toàn", "rank", "pos", "phú quý song toàn",
    "Quan Sát là dụng thần và không yếu, có Tài mà Tài không phải chữ kỵ",
    ALL(YONG("QuanSat"), no(N("QuanSat")), P("Tai"), no(KY("Tai"))), hi=True, note="Đòi Quan Sát không yếu và có Tài: hẹp hơn câu sách (cách đọc của hệ thống).")
add("tvh", "F16", "p.168", "Kị tỉ kiếp, quan vượng tài vượng có thể kháng được tỉ kiếp, nên giàu sang", "wealth", "pos", "giàu sang",
    "Tỉ Kiếp là chữ kỵ, Quan Sát và Tài đều vượng", ALL(KY("Ti"), V("QuanSat"), V("Tai")), hi=True)
add("tvh", "F17", "p.168", "Quan tinh vượng là dụng thần, có ấn thụ bảo vệ quan thì nhất định sang", "rank", "pos", "sang: dễ có danh, có chức",
    "Quan Sát vượng và là dụng thần, có Ấn", ALL(V("QuanSat"), YONG("QuanSat"), P("An")), hi=True)
add("tvh", "F18", "p.168", "Quan vượng mà làm dụng thần là mệnh có tài", "character", "pos", "là người có tài năng", "Quan Sát vượng và là dụng thần",
    ALL(V("QuanSat"), YONG("QuanSat")), hi=True, note="Cùng câu: 'Quan gặp tuế vận là có quan chức' — lời về năm, vận: chưa đưa vào.")
add("tvh", "F19", "p.168", "Quan vượng thân nhược, quan có thể sinh ấn. Quan quá vượng là nặng sẽ khắc thân quá mức, cho nên quan vượng có thể lấy ấn vượng làm dụng thần thông quan",
    "rank", "pos", "sang: Ấn hóa sức ép của Quan thành chỗ dựa", "nhật chủ nhược, Quan Sát vượng, Ấn vượng và là dụng thần",
    ALL(WEAK, V("QuanSat"), V("An"), YONG("An")), hi=True)
add("tvh", "F20", "p.168", "Thân vượng, quan vượng, ấn suy, tài tinh không hiện, nhưng ấn tỉ giúp thân chặt chẽ là quan và dân đồng đều nhau nên sang", "rank", "pos",
    "sang", "nhật chủ vượng, Quan Sát vượng, Ấn yếu, Tài không lộ can", ALL(STRONG, V("QuanSat"), L("An"), no(T("Tai"))))
add("tvh", "F21", "p.168", "Sát, thân đều vượng, không có ấn, thực thương là dụng thần có lực", "rank", "pos", "sang: thân và Sát cân nhau, có chữ chế",
    "nhật chủ vượng, Thất Sát vượng, không có Ấn, Thực Thương là dụng thần và không yếu",
    ALL(STRONG, GOD("Thất Sát"), V("QuanSat"), A("An"), YONG("ThucThuong"), no(N("ThucThuong"))), hi=True)
add("tvh", "F22", "p.168", "Thân vượng, quan nhược, tài có lực. Tài vượng có thể sinh cho quan nhược, quan nhờ thế mà vinh hiển nên phú quý", "rank", "pos",
    "phú quý", "nhật chủ vượng, Quan yếu, Tài vượng đứng sát sinh Quan", ALL(STRONG, L("QuanSat"), V("Tai"), ADJ("Tai", "QuanSat")))
add("tvh", "F23", "p.168", "Ấn vượng, quan suy, tài làm hại ấn. Thân vượng ấn là kị thần", "rank", "pos", "phú quý: Tài vừa chế Ấn vừa sinh Quan",
    "nhật chủ vượng, Ấn vượng là chữ kỵ, Quan yếu, Tài đứng sát chế Ấn và sinh Quan",
    ALL(STRONG, V("An"), KY("An"), N("QuanSat"), ADJ("Tai", "An"), ADJ("Tai", "QuanSat")), hi=True, note="Câu sách kết: 'đó là mệnh phú quý'.")
add("tvh", "F24", "p.168", "Thân nhược, dụng thần là tỉ kiếp, tài suy, quan có thể sinh ấn", "rank", "pos", "sang", "nhật chủ nhược, Tỉ Kiếp là dụng thần, Tài yếu, Quan Sát vượng đứng sát sinh Ấn",
    ALL(WEAK, YONG("Ti"), N("Tai"), V("QuanSat"), ADJ("QuanSat", "An")), hi=True, note="Lời kết của câu sách ở đầu tr.169: 'do đó mà trở thành sang'.")
add("tvh", "F25", "p.169", "Thần nhược, tài vượng có ấn, tỉ kiếp, quan tuy không nhiều nhưng không bị phá. Dụng thần quan tinh có thể thông với tài ấn để sinh thân",
    "rank", "pos", "phú quý song toàn", "nhật chủ nhược, Tài vượng, có Ấn, Tỉ Kiếp và Quan Sát, Quan Sát là dụng thần",
    ALL(WEAK, V("Tai"), P("An"), P("Ti"), P("QuanSat"), YONG("QuanSat")), hi=True, note="'Thần nhược': chữ in, nghĩa là thân nhược.")
add("tvh", "F26", "p.169", "Dụng thần là ấn, kị tài tinh làm thương tổn ấn, có vượng quan hóa tài liên tục sinh cho ấn", "rank", "pos", "tiền vừa phải mà danh lớn (tiểu phú đại quý)",
    "Ấn là dụng thần, Tài là chữ kỵ, Quan Sát vượng nối Tài sang Ấn", ALL(YONG("An"), KY("Tai"), V("QuanSat"), ADJ("Tai", "QuanSat"), ADJ("QuanSat", "An")), hi=True)
add("tvh", "F27", "p.169", "Quan nhiều kị gặp tài, thân lại nhược. Tài tinh nắm lệnh hoặc tài cục, thân nhược không gánh nổi tài quan nên nghèo hèn", "rank", "neg",
    "khó lên: thân không gánh nổi Tài Quan", "nhật chủ nhược, Quan Sát nhiều, Tài nắm lệnh tháng hoặc thành cục",
    ALL(WEAK, V("QuanSat"), ANY(MONTH("Tai"), eq("bazi.k.tai_cuc", True))))
add("tvh", "F28", "p.169", "Thân nhược, dụng thần là ấn, nhưng tài tinh lại phá hoại ấn. Dụng thần bị tài khắc cho thương tổn, không có vượng quan để sinh ấn", "rank", "neg",
    "khó lên", "nhật chủ nhược, Ấn là dụng thần bị Tài đứng sát phá, Quan Sát không vượng", ALL(WEAK, YONG("An"), ADJ("Tai", "An"), no(V("QuanSat"))), hi=True)
add("tvh", "F29", "p.169", "Quan sát nặng mà không có ấn", "rank", "neg", "khó lên: thân bị Quan Sát đè mà không có chỗ hóa", "Quan Sát nặng, không có Ấn",
    ALL(V("QuanSat"), A("An")), note="Cùng trang: 'thành ra thân bị quan sát khắc, do đó mà hèn'.")
add("tvh", "F30", "p.169", "Chính quan nặng, không có ấn, thực thương mạnh để áp lại", "rank", "neg", "khó lên, của cũng hao", "nhật chủ nhược, Chính Quan nặng, không có Ấn, Thực Thương mạnh",
    ALL(WEAK, GOD("Chính Quan"), V("QuanSat"), A("An"), V("ThucThuong")))
add("tvh", "F31", "p.169", "Quan nặng, ấn nhẹ, thân nhược", "rank", "neg", "khó lên: Ấn yếu không đỡ nổi thân", "nhật chủ nhược, Quan Sát nặng, Ấn nhẹ",
    ALL(WEAK, V("QuanSat"), L("An")))
add("tvh", "F32", "p.169", "Quan nhược, kiếp nặng, không có tài", "rank", "neg", "khó lên, của cũng khó giữ", "Quan yếu, Kiếp Tài nặng, không có Tài",
    ALL(L("QuanSat"), V("Ti"), GOD("Kiếp Tài"), A("Tai")))
add("tvh", "F33", "p.169", "Quan nhẹ, ấn nặng, thân vượng. Ấn hóa quan mà không có quan, thân vượng không có quan là hèn", "rank", "neg", "khó có chức vị",
    "nhật chủ vượng, Ấn nặng, Quan nhẹ hoặc không có", ALL(STRONG, V("An"), N("QuanSat")))
add("tvh", "F34", "p.170", "Quan tàng không thấu, tài nhẹ, kiếp nặng. Vì thân vượng, tài quan nhẹ", "rank", "neg", "khó lên, của cũng mỏng",
    "nhật chủ vượng, Quan Sát chỉ tàng trong chi, Tài nhẹ, Tỉ Kiếp nặng", ALL(STRONG, P("QuanSat"), no(T("QuanSat")), L("Tai"), V("Ti")))
# p.173 (kỵ thần càng vượng càng ...): only the kỵ rows with the kỵ group itself vượng (the 'càng vượng' of the page)
add("tvh", "F40", "p.173", "Nghèo: Nhật chủ mạnh, tỉ kiếp là kị thần. Kị thần càng vượng càng nghèo", "wealth", "neg", "khó giữ tiền", "nhật chủ mạnh, Tỉ Kiếp là chữ kỵ và vượng",
    ALL(STRONG, KY("Ti"), V("Ti")), hi=True)
add("tvh", "F41", "p.173", "Nhật chủ nhược, tài tinh là kị thần. Tài tinh càng vượng càng nghèo", "wealth", "neg", "khó giữ tiền", "nhật chủ nhược, Tài là chữ kỵ và vượng",
    ALL(WEAK, KY("Tai"), V("Tai")), hi=True)
add("tvh", "F42", "p.173", "Hèn: nhật chủ mạnh, ấn tinh là kị thần. Ấn tinh càng vượng càng hèn", "rank", "neg", "khó lên chức vị", "nhật chủ mạnh, Ấn là chữ kỵ và vượng",
    ALL(STRONG, KY("An"), V("An")), hi=True)
add("tvh", "F43", "p.173", "Nhật chủ nhược, quan sát là kị thần. Quan sát càng vượng càng hèn", "rank", "neg", "khó lên chức vị", "nhật chủ nhược, Quan Sát là chữ kỵ và vượng",
    ALL(WEAK, KY("QuanSat"), V("QuanSat")), hi=True)
add("tvh", "F44", "p.173", "Nhật chủ yếu, tỉ kiếp là dụng thần. Tỉ kiếp càng vượng càng giàu", "wealth", "pos", "có thể giàu", "nhật chủ yếu, Tỉ Kiếp là dụng thần và không yếu",
    ALL(WEAK, YONG("Ti"), no(N("Ti"))), hi=True)
add("tvh", "F45", "p.173", "Nhật chủ nhược, ấn tinh là dụng thần. Ấn tinh càng vượng càng sang", "rank", "pos", "có thể sang", "nhật chủ nhược, Ấn là dụng thần và vượng",
    ALL(WEAK, YONG("An"), V("An")), hi=True)
# p.170-171 cát / hung by dụng thần (topic 'fortune')
add("tvh", "CH01", "p.170", "Thân vượng dụng thần là tài, có thực thương sinh tài; hoặc có quan sát bảo vệ tài", "fortune", "pos", "cát, vì dụng thần được sinh và được giữ",
    "nhật chủ vượng, Tài là dụng thần, có Thực Thương sinh hoặc Quan Sát giữ", ALL(STRONG, YONG("Tai"), ANY(ADJ("ThucThuong", "Tai"), P("QuanSat"))), hi=True)
add("tvh", "CH02", "p.170", "Thân vượng, dụng thần là sát, sát nặng có thực thương chế ngự; hoặc sát nhẹ có tài sinh", "fortune", "pos", "cát",
    "nhật chủ vượng, Sát là dụng thần: Sát nặng có Thực Thương chế, hoặc Sát nhẹ có Tài sinh",
    ALL(STRONG, YONG("QuanSat"), GOD("Thất Sát"), ANY(ALL(V("QuanSat"), ADJ("ThucThuong", "QuanSat")), ALL(N("QuanSat"), ADJ("Tai", "QuanSat")))), hi=True)
add("tvh", "CH03", "p.170", "Thân vượng, dụng thần là thực thương, có tài lưu thông và bảo vệ thực thương, đều là cát", "fortune", "pos", "cát",
    "nhật chủ vượng, Thực Thương là dụng thần, có Tài", ALL(STRONG, YONG("ThucThuong"), P("Tai")), hi=True)
add("tvh", "CH04", "p.170", "Thân nhược, dụng thần là tỉ kiếp, quan tinh nặng, có ấn sinh thân xì hơi quan", "fortune", "pos", "cát",
    "nhật chủ nhược, Tỉ Kiếp là dụng thần, Quan Sát nặng, có Ấn", ALL(WEAK, YONG("Ti"), V("QuanSat"), P("An")), hi=True)
add("tvh", "CH05", "p.170", "Thân nhược, dụng thần là tỉ kiếp, thực thương nặng, có ấn chế ngự thực thương mà sinh thân", "fortune", "pos", "cát",
    "nhật chủ nhược, Tỉ Kiếp là dụng thần, Thực Thương nặng, có Ấn", ALL(WEAK, YONG("Ti"), V("ThucThuong"), P("An")), hi=True)
add("tvh", "CH06", "p.170", "Thân nhược, dụng thần là ấn, có quan tinh sinh ấn; hoặc tỉ kiếp bảo vệ ấn", "fortune", "pos", "cát",
    "nhật chủ nhược, Ấn là dụng thần, có Quan Sát sinh Ấn hoặc Tỉ Kiếp", ALL(WEAK, YONG("An"), ANY(ADJ("QuanSat", "An"), P("Ti"))), hi=True)
add("tvh", "CH10", "p.171", "Tài nặng: tài vượng, thân nhược, kiếp và ấn nhẹ", "fortune", "neg", "hung, vì Tài quá nặng so với thân", "Tài vượng, nhật chủ nhược, Tỉ Kiếp và Ấn nhẹ",
    ALL(V("Tai"), WEAK, N("Ti"), N("An")))
add("tvh", "CH11", "p.171", "Tài nhẹ: dụng thần là tài, tài nhẹ còn kiếp nặng, ấn nặng", "fortune", "neg", "hung, vì dụng thần Tài quá nhẹ", "Tài là dụng thần mà nhẹ, Tỉ Kiếp và Ấn nặng",
    ALL(YONG("Tai"), N("Tai"), V("Ti"), V("An")), hi=True)
add("tvh", "CH12", "p.171", "Quan nặng: quan nhiều, thân nhược lại không có ấn", "fortune", "neg", "hung, vì Quan quá nặng", "Quan Sát nhiều, nhật chủ nhược, không có Ấn",
    ALL(V("QuanSat"), WEAK, A("An")))
add("tvh", "CH13", "p.171", "Quan nhẹ: dụng thần là quan, ấn nặng", "fortune", "neg", "hung, vì dụng thần Quan quá nhẹ", "Quan Sát là dụng thần, Ấn nặng",
    ALL(YONG("QuanSat"), V("An")), hi=True)
add("tvh", "CH14", "p.171", "Sát nặng: thân nhẹ lại không có thực thương, ấn thụ", "fortune", "neg", "hung, vì Sát nặng không có chữ chế, chữ hóa",
    "nhật chủ nhẹ, có Thất Sát, không có Thực Thương và Ấn", ALL(WEAK, GOD("Thất Sát"), A("ThucThuong"), A("An")))
add("tvh", "CH15", "p.171", "Sát nhẹ: dụng thần là sát, sát nhẹ không chế ngự được nặng lại còn không có tài", "fortune", "neg", "hung, vì dụng thần Sát quá nhẹ",
    "Sát là dụng thần mà nhẹ, không có Tài", ALL(YONG("QuanSat"), GOD("Thất Sát"), N("QuanSat"), A("Tai")), hi=True)
add("tvh", "CH16", "p.171", "Ấn nặng: ấn kiếp đều nặng mà quan thì nhẹ", "fortune", "neg", "hung, vì Ấn Kiếp quá nặng", "Ấn và Tỉ Kiếp đều nặng, Quan nhẹ",
    ALL(V("An"), V("Ti"), L("QuanSat")), note="Tr.171 viết cùng điều kiện hai lần (dưới 'Ấn nặng' và 'Tỉ kiếp nặng').")
add("tvh", "CH17", "p.171", "Ấn nhẹ: dụng thần là ấn mà gặp tài nhiều", "fortune", "neg", "hung, vì dụng thần Ấn bị Tài nhiều đè", "Ấn là dụng thần, Tài nhiều",
    ALL(YONG("An"), V("Tai")), hi=True)
add("tvh", "CH18", "p.171", "Thực thương nặng: Thực thương nhiều lại không có ấn", "fortune", "neg", "hung, vì Thực Thương quá nặng", "Thực Thương nhiều, không có Ấn",
    ALL(V("ThucThuong"), A("An")))
add("tvh", "CH19", "p.171", "Thực thương nhẹ: dụng thần là thực thương lại gặp nhiều kiêu thần", "fortune", "neg", "hung, vì dụng thần Thực Thương bị Thiên Ấn đoạt",
    "Thực Thương là dụng thần, Thiên Ấn nhiều", ALL(YONG("ThucThuong"), GOD("Thiên Ấn"), V("An")), hi=True)
add("tvh", "CH20", "p.171", "Tỉ kiếp nặng: Tứ trụ tỉ kiếp nhiều mà không có quan sát", "fortune", "neg", "hung, vì Tỉ Kiếp quá nặng", "Tỉ Kiếp nhiều, không có Quan Sát",
    ALL(V("Ti"), A("QuanSat")))
add("tvh", "CH21", "p.171", "Tỉ kiếp nhẹ: Dụng thần là tỉ kiếp mà quan sát nhiều", "fortune", "neg", "hung, vì dụng thần Tỉ Kiếp bị Quan Sát đè", "Tỉ Kiếp là dụng thần, Quan Sát nhiều",
    ALL(YONG("Ti"), V("QuanSat")), hi=True)
# ---- quan / danh pp.532, 546, 552-553 (court titles left out; see rules_519_556.md)
add("tvh", "D01", "p.532", "Quan sát rất nặng, thân lại mạnh, nếu gặp chế phục là bậc trung thần", "character", "pos", "là người trung thành, tận tụy",
    "nhật chủ mạnh, Quan Sát rất nặng mà có Thực Thương đứng sát chế", ALL(STRONG, V("QuanSat"), ADJ("ThucThuong", "QuanSat")))
add("tvh", "D02", "p.532", "Sát vượng, ấn yếu là xuất thân ở văn nhưng cuối cùng là võ tướng", "work", "neutral",
    "khởi đầu từ việc chữ nghĩa, về sau thiên về việc cần quyết đoán, kỷ luật", "Thất Sát vượng, Ấn yếu", ALL(GOD("Thất Sát"), V("QuanSat"), L("An")),
    note="'Võ tướng': chữ của sách; văn nói nhóm việc tương ứng ngày nay.")
add("tvh", "D03", "p.532", "Quan không có kình dương mà có ấn, không phải là quan cảnh sát thì cũng là quan trấn ải biên cương", "work", "pos",
    "hợp việc giữ gìn an ninh, trật tự", "Chính Quan lộ can, có Ấn, không có dương nhận", ALL(TG("Chính Quan"), P("An"), eq("bazi.k.ren_present", False)))
add("tvh", "D04", "p.532", "Ấn, kình dương đều gặp làm quan ở chức cao", "rank", "pos", "dễ giữ chức cao", "có Ấn không yếu và dương nhận", ALL(P("An"), no(N("An")), eq("bazi.k.ren_present", True)))
add("tvh", "D05", "p.552", "Thất sát gặp kình dương thì công danh hiển đạt", "rank", "pos", "công danh hiển đạt", "có Thất Sát và dương nhận",
    ALL(GOD("Thất Sát"), eq("bazi.k.ren_present", True)))
add("tvh", "D06", "p.553", "Ấn ẩn, tài lộ, thân vượng thì công danh vinh hiển, phúc đức đều có", "rank", "pos", "công danh vinh hiển",
    "nhật chủ vượng, Tài lộ can, Ấn chỉ tàng trong chi", ALL(STRONG, T("Tai"), P("An"), no(T("An"))), note="Tr.552 viết gần như cùng câu: 'Ấn tàng, tài lộ, thân vượng thì công danh vinh hiển'.")
add("tvh", "D07", "p.553", "Tài khí gặp chính quan, tên tuổi vang xa sáu nước", "rank", "pos", "tên tuổi được nhiều người biết", "Tài đứng sát sinh Chính Quan",
    PT_OK("tai_quan_song_my"), pt="tai_quan_song_my")
add("tvh", "D08", "p.553", "Quan tinh ấn vượng, là công danh bậc nhất", "rank", "pos", "công danh vững", "có Chính Quan, Ấn vượng", ALL(GOD("Chính Quan"), V("An")))
add("tvh", "D09", "p.553", "Thân vượng ấn vượng là hiển đạt cao quý", "rank", "pos", "dễ hiển đạt", "nhật chủ vượng, Ấn vượng mà Ấn không phải chữ kỵ", ALL(STRONG, V("An"), no(KY("An"))),
    note="Tr.173 với nhật chủ mạnh và Ấn là chữ kỵ nói ngược lại ('Ấn tinh càng vượng càng hèn'); tr.527 với cùng điều kiện nói về tiền "
    "('tiền hao tán không tụ'). Hai trang của cùng sách: lời này chỉ đứng khi Ấn không phải chữ kỵ (schools.json).")
add("tvh", "D10", "p.553", "Thực thần vượng gặp tài thì chắc chắn sẽ có công danh", "rank", "pos", "có công danh", "Thực Thần vượng, có Tài",
    ALL(GOD("Thực Thần"), V("ThucThuong"), P("Tai")))
add("tvh", "D11", "p.552", "Sát tàng, quan lộ tức là ác mờ, thiện rõ, người như thế tên tuổi nổi tiếng", "rank", "pos", "tên tuổi nổi tiếng",
    "Chính Quan lộ can, Thất Sát chỉ tàng trong chi", ALL(TG("Chính Quan"), GOD("Thất Sát"), no(TG("Thất Sát"))))
add("tvh", "D12", "p.553", "Thiên tài ở trụ giờ gặp quan thì đỗ đạt từ bé", "study", "pos", "đỗ đạt sớm", "can giờ là Thiên Tài, lá số có Quan Sát",
    ALL(eq("bazi.k.hour_stem_god", "Thiên Tài"), P("QuanSat")), conv=False)
# ---- học hành, thi cử p.546, p.148
add("tvh", "HT01", "p.546", "Tài quan ấn đều có là có lợi cho thi đỗ", "study", "pos", "có lợi cho thi cử", "có đủ Tài, Quan Sát và Ấn", ALL(P("Tai"), P("QuanSat"), P("An")), conv=False)
add("tvh", "HT02", "p.546", "Thân vượng gặp quan thì nhất định thi đỗ", "study", "pos", "thi cử dễ đỗ", "nhật chủ vượng, có Chính Quan", ALL(STRONG, GOD("Chính Quan")),
    note="Tr.552: 'Thân vượng gặp quan là tên treo bảng vàng'.")
add("tvh", "HT03", "p.546", "Thương quan bị chế ngự, hoặc thương quan hợp sát thì lợi cho thi cử", "study", "pos", "lợi cho thi cử", "Thương Quan bị Ấn đứng sát chế",
    ALL(GOD("Thương Quan"), ADJ("An", "ThucThuong")), note="Chỉ xét vế 'bị chế ngự' (Ấn đứng sát); vế 'hợp sát' chưa xét.")
add("tvh", "HT04", "p.546", "Thất sát hóa ấn là tuổi trẻ đã thi đỗ", "study", "pos", "đỗ đạt sớm", "Thất Sát sinh Ấn, Ấn đứng sát nhật chủ", PT_OK("sat_an_tuong_sinh"),
    pt="sat_an_tuong_sinh", conv=False)
add("tvh", "HT05", "p.546", "Ấn vượng, sát yếu thì thi đỗ", "study", "pos", "thi cử dễ đỗ", "Ấn vượng, Thất Sát yếu", ALL(V("An"), GOD("Thất Sát"), N("QuanSat")))
add("tvh", "HT06", "p.148", "ấn tinh được sinh là có sinh phù, được lệnh là vượng, tính tình hiền lành, đi học văn chương giỏi, thích hợp với công việc văn chương, hành chính",
    "study", "pos", "học văn giỏi, hợp việc văn chương, hành chính", "Ấn nắm lệnh tháng, có Quan Sát đứng sát sinh Ấn", ALL(MONTH("An"), ADJ("QuanSat", "An")), conv=False)

# ================================================================ 八字真宗
# 日干五行直断 p.26 is already in the base pack data/pack_bazi_zhenzong.json (voiced in the Bát Tự portrait): not repeated here.
EL = [("Mộc", "p.26", "为人吝啬小气，不通情理", "keo kiệt, khó thông cảm"), ("Hỏa", "p.26", "内外软弱，语言表达不清，消极", "mềm yếu, nói khó rõ ý, tiêu cực"),
      ("Thổ", "p.27", "无情无义", "bạc tình"), ("Kim", "p.27", "无礼无义", "thiếu lễ nghĩa"), ("Thủy", "p.27", "智力不高，无常反复", "trí lực không cao, thất thường")]
for i, (el, pg, q, e) in enumerate(EL, 1):
    add("zz", f"EL{i}", pg, q, "character", "neg", e, f"tứ trụ (cả tàng can) không có hành {el}", has("bazi.k.absent_el", el), harsh=True, conv=False,
        note="HARSH: lời phán về đạo đức / trí lực dựa trên việc thiếu một hành; giữ draft cho đến khi chủ dự án quyết.")
add("zz", "HH1", "p.29", "男命：必得贤妻，妻助得财", "marriage", "pos", "được vợ hiền, vợ giúp chồng có của", "lá số nam: can ngày hợp can tháng, hóa theo hành của can dương (妻从夫化)",
    ALL(MALE, eq("bazi.k.zz_hh", "uu")), conv=False, note="Điều kiện tr.28: can ngày hợp can tháng; chi tháng là lộc hoặc nhận (bảng tr.28) của can mang hành hóa; "
    "hai chi ngồi dưới cùng hành ấy hoặc sinh ra nó (ví dụ 2 của tr.29 tính 酉 dưới 癸 là 比: cách đọc của hệ thống); can ngày nam là can dương. Ví dụ tr.29: 月辛巳、日丙午.")
add("zz", "HH2", "p.29", "男命：怕妻胆小，妇人当家", "marriage", "neutral", "vợ nắm việc nhà, chồng hay nhường vợ", "lá số nam: can ngày hợp can tháng, hóa theo hành của can âm (夫从妻化)",
    ALL(MALE, eq("bazi.k.zz_hh", "liet")), conv=False, note="Cùng điều kiện tr.28 như HH1.")
add("zz", "HH3", "p.29", "女命：柔顺贤慧，贤妻良母", "marriage", "pos", "dịu dàng, hiền thục, giỏi vun vén gia đình", "lá số nữ: can ngày hợp can tháng, hóa theo hành của can dương (妻从夫化)",
    ALL(FEMALE, eq("bazi.k.zz_hh", "uu")), conv=False, note="Cùng điều kiện tr.28 như HH1; can ngày nữ là can âm.")
add("zz", "HH4", "p.29", "女命：是母老虎，欺夫骂翁", "marriage", "neg", "lấn át chồng", "lá số nữ: can ngày hợp can tháng, hóa theo hành của can âm (夫从妻化)",
    ALL(FEMALE, eq("bazi.k.zz_hh", "liet")), harsh=True, conv=False, note="HARSH: lời miệt thị người vợ; giữ draft. Ví dụ tr.29: 月戊子，日癸酉.")
HZ = [("Thổ", "甲己合化土：为正中之合，主安分守己，淳正厚朴", "an phận, ngay thẳng, chất phác", False),
      ("Kim", "乙庚合化金：为仁义之合，主刚柔兼备，重信守义", "cương nhu đủ cả, trọng chữ tín, giữ nghĩa", False),
      ("Thủy", "丙辛合化水：为威严之合，主仪表威严，智力优秀", "dáng vẻ uy nghiêm, trí lực tốt", False),
      ("Mộc", "丁壬合化木：为仁寿之合，主心地仁慈", "lòng dạ nhân từ", False),
      ("Hỏa", "戊癸合化火：为无情之合，主娇媚之合，薄情寡义", "bạc tình", True)]
for i, (el, q, e, harsh) in enumerate(HZ, 1):
    add("zz", f"HZ{i}", "p.29", q, "character", "neg" if harsh else "pos", e, f"hai can liền nhau hợp hóa {el} đúng phép (chi tháng và hai chi ngồi dưới đều là {el})",
        has("bazi.k.zz_zhenghua", el), harsh=harsh, conv=False,
        note=("HARSH: giữ draft. " if harsh else "") + ("Vế 长命多寿 (sống lâu) của câu sách không đưa vào văn. " if el == "Mộc" else "") +
        "Điều kiện cùng trang: '正五行合化条件：月令必须为化神物，而且两干坐支为合化之物'; hai can phải liền trụ (quy ước của hệ thống).")
add("zz", "HZ0", "p.29", "正化之人性情刚直，办事认真，人际关系处理得当", "character", "pos", "tính cương trực, làm việc nghiêm túc, khéo cư xử",
    "hai can liền nhau hợp hóa đúng phép", ANY(*[has("bazi.k.zz_zhenghua", x) for x in ("Mộc", "Hỏa", "Thổ", "Kim", "Thủy")]), conv=False)
add("zz", "DH1", "p.29", "命局逢此，主猜疑心强，妒忌心强，挑拨是非", "character", "neg", "dễ đa nghi, hay ghen tị", "ba can của ba trụ liền nhau tạo 妒合 (甲己乙, 庚乙辛, 丙辛丁, 壬丁癸, 戊癸己)",
    eq("bazi.k.zz_duhe", True), conv=False, note="妒合 tr.29: '三干须相连'.")
add("zz", "YY1", "p.29", "出现在：年月二柱，主少青家境富有", "parents", "pos", "thời trẻ nhà khá giả", "trụ năm và trụ tháng: can hợp can, chi hợp chi (干支鸳鸯合)",
    has("bazi.k.zz_yuanyang", "year_month"), conv=False, note="'合化之物互相引化': hai hành hóa giống nhau hoặc sinh nhau (cách đọc của hệ thống); 午未 hợp tính cả Hỏa lẫn Thổ.")
add("zz", "YY2", "p.29", "出现在：月日二柱，主34～45 岁富贵", "wealth", "pos", "khoảng 34-45 tuổi giàu sang", "trụ tháng và trụ ngày: can hợp can, chi hợp chi (干支鸳鸯合)",
    has("bazi.k.zz_yuanyang", "month_day"), conv=False, note="Cùng cách đọc như YY1.")

# ================================================================ write (in place)
for book, rs in R.items():
    pack_f, quotes_f = D / f"pack_{book}_kin.json", D / f"quotes_{book}_kin.json"
    pack, quotes = json.loads(pack_f.read_text("utf-8")), json.loads(quotes_f.read_text("utf-8"))
    mine = {r["id"] for r in rs}
    assert len(mine) == len(rs), book
    owned = mine | {i for i, m in quotes.items() if m.get("deep3")}      # this builder's rules, including any it no longer makes
    pack["rules"] = [r for r in pack["rules"] if r["id"] not in owned]
    quotes = {i: m for i, m in quotes.items() if i not in owned or i in mine}
    clash = [i for i in mine if i in quotes and not quotes[i].get("deep3")]
    assert not clash, clash          # an id of an older pack: never overwrite it
    pack["sources"] = [s for s in pack["sources"] if s["id"] != SRC[book]["id"]] + [SRC[book]]
    for r in rs:
        pack["rules"].append({"id": r["id"], "system": "bat_tu", "schoolId": SCHOOL[book], "category": f"{book}_kin_{r['topic']}",
                              "description": f"{NAME[book]} {r['page']}: {r['quote']} — {r['effect']} ({r['cause']})", "conditions": r["cond"],
                              "consequences": [{"kind": "finding", "claim": r["id"].lower(), "effect": {"pos": "support", "neg": "limit"}.get(r["tone"], "neutral"),
                                                "scope": "natal"}],
                              "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": [SRC[book]["id"]],
                              "reviewStatus": "draft" if r["harsh"] else "verified", "version": "0.1.0", "subject": "chart"})
        m = {k: r[k] for k in ("page", "quote", "topic", "tone", "effect", "cause")}
        if book != "zz":
            m["book"] = book
        for k in ("note", "say", "pt", "yong"):
            if r[k]:
                m[k] = r[k]
        if r["hi"]:
            m["hi"] = True
        if r["harsh"]:
            m["harsh"] = True
        m["deep3"] = True
        quotes[r["id"]] = m
    pack_f.write_text(json.dumps(pack, ensure_ascii=False, indent=1) + "\n", "utf-8")
    quotes_f.write_text(json.dumps(quotes, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(book, len(rs), "rules (", sum(r["harsh"] for r in rs), "draft / harsh )")
