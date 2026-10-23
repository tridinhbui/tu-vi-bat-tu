"""Generates engine/data/bazi_deep/pack_zz_kin.json (rules, read by tvbt.bazi_deep.kin on its own facts) and quotes_zz_kin.json (per rule: the
page, the printed words as they stand in the text layer engine/data/bazi_deep/mined/zz_pNN.txt, the topic, the tone and the paraphrase split into
effect and chart condition) from 八字真宗 (DEEP-BAZI-2, 2026-10-23).
    .venv/bin/python tools/build_bazi_kin_pack.py
Left out on purpose (sensitive): infidelity, second marriage, lovers (p.57 #9, 13-17, 22, 26, 31-32, 35-38; p.58 #29-30 second halves), the
officialdom-disaster and prison pages (pp.53-54), parents' lifespan and death (p.55 #6-21, 送终), siblings' early death, adoption, illegitimacy
(pp.63-64 #1-19), children's sex and fertility (p.60), illness and injury (pp.61-63), the years of mourning, illness and fire (pp.64-65 #4-7, 17, 39-41,
43). Not computable without a guess: 纳音财星/官星 (p.50 #3, p.53 #13), 女命财优官地 (p.50 #15), 小岁运并临 (p.64 #9-12: the small luck is not
computed), 命前五辰 / 命后三辰 (p.64 #2-3: which 命), 大限 (p.64 #18-19). Book-internal conflicts are kept apart by the conditions (see `excl`)."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data" / "bazi_deep"
eq = lambda f, v: {"fact": f, "value": v}
has = lambda f, v: {"fact": f, "operator": "contains", "value": v}
anyof = lambda f, v: {"fact": f, "operator": "contains_any", "value": v}
gte = lambda f, v: {"fact": f, "operator": "gte", "value": v}
inn = lambda f, v: {"fact": f, "operator": "in", "value": v}
no = lambda c: {"not": c}
ALL = lambda *c: {"all": list(c)}
STRONG, WEAK = eq("bazi.k.dm_strong", True), eq("bazi.k.dm_strong", False)
V = lambda g: has("bazi.k.vuong", g)
N = lambda g: has("bazi.k.nhuoc", g)
A = lambda g: has("bazi.k.absent", g)
R = []
CONV = ("'vượng' / 'nhược' của một nhóm thập thần: phần độ của nhóm trên tổng độ Thiệu Vĩ Hoa (tr.331-355) từ 25 % / dưới 12 % (Tỉ Kiếp không tính độ của chính nhật chủ) — ngưỡng của hệ thống, "
        "sách không cho thước đo.")


def add(rid, page, quote, topic, tone, effect, cause, cond, note=None, status="verified"):
    R.append({"id": f"BT_ZZK_{rid}", "page": page, "quote": quote, "topic": topic, "tone": tone, "effect": effect, "cause": cause, "cond": cond,
              "note": note, "status": status})


# ---------------- Tài, p.50 (财运直断真诀 and its 断语条件)
add("W01", "p.50", "身旺比劫重重无财，巨富", "wealth", "pos", "có thể giàu lớn", "nhật chủ vượng, Tỉ Kiếp trùng điệp mà không có Tài",
    ALL(STRONG, gte("bazi.k.ti_count", 3), A("Tai")), "'Trùng điệp': từ ba chữ Tỉ Kiếp trở lên ngoài nhật chủ (quy ước của hệ thống).")
add("W02R", "p.50", "正财透干有根或得生，财运佳", "wealth", "pos", "tài vận tốt", "Chính Tài thấu can và có gốc", ALL(eq("bazi.k.ct_trans", True), eq("bazi.k.ct_rooted", True)),
    "Có gốc: chi của chính trụ ấy hoặc trụ liền bên có cùng hành ở chính khí hay trung khí (ví dụ tr.51 gọi Mậu chỉ có dư khí trong Thân là 'không gốc'). "
    "Thay cho luận điểm cũ BT_ZZ_DIRECT_W_CHINH_TAI_ROOT, vốn tính gốc ở bất cứ chi nào.")
add("W02", "p.50", "正财透干有根或得生，财运佳", "wealth", "pos", "tài vận tốt", "Chính Tài thấu can, tuy không có gốc nhưng được chữ đứng sát bên sinh cho",
    eq("bazi.k.ct_gen_unrooted", True), "Vế 'có gốc' của câu này đã có ở luận điểm Chính Tài thấu can có gốc; đây là vế 'được sinh'.")
add("W04", "p.50", "正财坐墓地，靠勤俭持家", "wealth", "neutral", "giữ của nhờ cần kiệm", "Chính Tài ở can tháng ngồi trên đất Mộ của nó",
    eq("bazi.k.ct_tomb", True), "Mộ theo bảng mười hai giai đoạn (tr.24-25); tr.63 ghi mộ ở trụ tháng, ngày là 'mộ', ở trụ năm, giờ là 'khố'.")
add("W05", "p.50", "正财无根且不受生，劳碌之格", "wealth", "neg", "phải lao lực mới có tiền", "Chính Tài thấu can mà không có gốc, cũng không được chữ nào đứng sát bên sinh cho",
    ALL(eq("bazi.k.ct_lone", True), eq("bazi.k.ct_lone_hurt", False)))
add("W06", "p.50", "正财无根不受生，受刑冲，贫寒", "wealth", "neg", "dễ túng thiếu", "Chính Tài thấu can không gốc, không được sinh, lại bị hình xung",
    eq("bazi.k.ct_lone_hurt", True), "Hình, xung, hại xét giữa chi của trụ có Chính Tài và các chi khác.")
add("W07", "p.50", "正财不透干受生，财运佳，勤俭", "wealth", "pos", "tài vận tốt, lại biết cần kiệm", "Chính Tài không lộ ra can mà nằm trong chi, được chữ đứng sát bên sinh cho",
    eq("bazi.k.ct_hidden_gen", True))
add("W08", "p.50", "正财透干被截脚，花钱大手脚", "wealth", "neg", "tiêu tiền mạnh tay", "Chính Tài thấu can nhưng bị chi ngay dưới nó khắc (bị chặt chân)",
    eq("bazi.k.ct_cut", True))
add("W09", "p.50", "偏财透干，花钱大", "wealth", "neg", "tiêu xài mạnh tay", "Thiên Tài thấu can", eq("bazi.k.tt_trans", True))
add("W10R", "p.50", "偏财透干有根或得生，财运佳", "wealth", "pos", "tài vận tốt", "Thiên Tài thấu can và có gốc", ALL(eq("bazi.k.tt_trans", True), eq("bazi.k.tt_rooted", True)),
    "Có gốc: chi của chính trụ ấy hoặc trụ liền bên có cùng hành ở chính khí hay trung khí. Thay cho BT_ZZ_DIRECT_W_THIEN_TAI_ROOT.")
add("W10", "p.50", "偏财透干有根或得生，财运佳", "wealth", "pos", "tài vận tốt", "Thiên Tài thấu can, tuy không có gốc nhưng được chữ đứng sát bên sinh cho",
    eq("bazi.k.tt_gen_unrooted", True), "Vế 'có gốc' của câu này đã có ở luận điểm Thiên Tài thấu can có gốc; đây là vế 'được sinh'.")
add("W11", "p.50", "偏财坐库，财运佳", "wealth", "pos", "tài vận tốt", "Thiên Tài ở trụ năm hoặc trụ giờ ngồi trên khố của nó",
    eq("bazi.k.tt_kho", True), "Khố: giai đoạn Mộ của can trên chi của chính trụ ấy, ở trụ năm hoặc giờ (tr.63).")
add("W12", "p.50", "偏财被截脚，穷，爱花钱", "wealth", "neg", "dễ thiếu thốn, lại ưa tiêu xài", "Thiên Tài thấu can nhưng bị chi ngay dưới nó khắc (bị chặt chân)",
    eq("bazi.k.tt_cut", True))
add("W13", "p.50", "偏财不透受生，财运佳", "wealth", "pos", "tài vận tốt", "Thiên Tài không lộ ra can mà nằm trong chi, được chữ đứng sát bên sinh cho",
    ALL(eq("bazi.k.tt_hidden_gen", True), eq("bazi.k.tt_hidden_covered", False)))
add("W14", "p.50", "偏财不透被盖头，贫命流", "wealth", "neg", "khó khá lên về tiền bạc", "Thiên Tài chỉ nằm trong chi, lại bị can ngay trên nó khắc (bị che đầu)",
    ALL(eq("bazi.k.tt_hidden_covered", True), eq("bazi.k.tt_hidden_gen", False)))
add("W16", "p.50", "偏财、正财两旺，身兼多职", "wealth", "pos", "có thể kiêm nhiều việc một lúc", "Chính Tài và Thiên Tài đều thấu can và có gốc",
    eq("bazi.k.both_tai_rooted", True))
add("W18", "p.50", "财星被争合，花钱不计花", "wealth", "neg", "tiêu tiền không tính toán", "chữ Tài bị hai chữ tranh nhau hợp",
    eq("bazi.k.tai_contested", True))
add("W19", "p.50", "财星守胎身命，财运佳", "wealth", "pos", "tài vận tốt", "Tài nằm ở thai nguyên, mệnh cung hoặc thân cung",
    eq("bazi.k.tai_tmm", True), "Thai nguyên, mệnh cung, thân cung tính theo tr.35-38; xét can và chính khí của chi.")
add("W21", "p.50", "财星空亡，一生财不聚", "wealth", "neg", "tiền khó tụ lại", "chữ Tài rơi vào không vong",
    eq("bazi.k.tai_void", True), "Không vong tính theo trụ ngày (tr.24, 37), xét chính khí của chi.")
add("W22", "p.50", "财星遇合，反主失", "wealth", "neg", "dễ mất tiền", "chữ Tài gặp hợp",
    eq("bazi.k.tai_combined", True))
add("W23", "p.50", "财星不现，看食伤", "wealth", "neutral", "chuyện tiền bạc phải xét qua Thực Thương", "lá số không có Tài, kể cả trong tàng can", A("Tai"))
add("W24", "p.50", "财星旺，但未流入日，则财运平常", "wealth", "neutral", "tài vận ở mức bình thường",
    "Tài vượng nhưng chưa chảy vào nhật chủ (chưa có chuỗi Tài sinh Quan, Quan sinh Ấn với Ấn đứng ở chi ngày, can tháng hoặc can giờ)",
    ALL(V("Tai"), eq("bazi.k.tai_flow", False)),
    "Điều kiện 1-2 cuối tr.50 áp cho cả bảng tài vận: Tài vượng thì phải 'chảy vào nhật chủ' mới thành tài vận tốt. " + CONV)
add("W25", "p.50", "财星旺，流入日主，则本人财运佳", "wealth", "pos", "tài vận tốt", "Tài vượng và chảy được vào nhật chủ qua chuỗi Tài sinh Quan, Quan sinh Ấn",
    ALL(V("Tai"), eq("bazi.k.tai_flow", True), eq("bazi.k.tmm_hurt", False)), "Điều kiện 1 và 3 cuối tr.50. " + CONV)
add("W26", "p.50", "财运佳，如果“胎身命”遇“刑穿冲绝”时，只为布衣平民", "wealth", "neutral", "tiền bạc chỉ ở mức người thường",
    "Tài vượng, chảy vào nhật chủ, nhưng thai nguyên, mệnh cung hoặc thân cung bị chi trong tứ trụ hình, xung, hại",
    ALL(V("Tai"), eq("bazi.k.tai_flow", True), eq("bazi.k.tmm_hurt", True)), "Điều kiện 4 cuối tr.50; hệ thống chưa tính 'tuyệt', nên chỉ xét hình, xung, hại. " + CONV)

# ---------------- công việc, pp.51-52 (工作、职业直断)
QT = eq("bazi.k.quan_trans", True)
QR = eq("bazi.k.quan_trans_rooted", True)
QF = eq("bazi.k.quan_flow", True)
add("O03A", "p.51", "官星（正官、七杀）透干有气流入日主，工作好", "work", "pos", "công việc tốt", "Quan Sát thấu can, có gốc và chảy vào nhật chủ qua Ấn",
    ALL(QT, QR, QF, no(V("QuanSat"))))
add("O03B", "p.51", "透干有气流入日主，工作好；若不流入日主，工作一般", "work", "neutral", "công việc ở mức bình thường",
    "Quan Sát thấu can, có gốc nhưng chưa chảy vào nhật chủ (không có Ấn đứng sát nhật chủ nối với nó)", ALL(QT, QR, no(QF), no(V("QuanSat"))))
add("O04A", "p.51", "官星透干无气流入日主，工作一般", "work", "neutral", "công việc ở mức bình thường", "Quan Sát thấu can không có gốc, nhưng chảy được vào nhật chủ qua Ấn",
    ALL(QT, no(QR), QF, no(V("QuanSat"))))
add("O04B", "p.51", "若不流入日主，工作便差", "work", "neg", "công việc kém thuận", "Quan Sát thấu can không có gốc, lại không chảy vào nhật chủ",
    ALL(QT, no(QR), no(QF), no(V("QuanSat"))))
add("O05A", "p.51", "官星旺流入日主，工作极佳", "work", "pos", "công việc rất tốt", "Quan Sát vượng và chảy vào nhật chủ qua Ấn", ALL(V("QuanSat"), QF), CONV)
add("O05B", "p.51", "若不流入日主，没有凶灾", "work", "neutral", "công việc không đến nỗi gặp chuyện dữ", "Quan Sát vượng nhưng không chảy vào nhật chủ",
    ALL(V("QuanSat"), no(QF)), CONV)
LEFT_NOTE = ("Trụ bên trái trụ có Quan (tr.52 mục 6-7; trụ năm thì bên trái là trụ giờ). Hai ví dụ tr.53 lấy trụ năm cho Quan ở trụ tháng và trụ giờ "
             "cho Quan ở trụ năm, nên 'bên trái' là trụ đứng trước. Khi không có Quan, sách (tr.51 mục 3) lấy Tài thay. Quan ở nhiều trụ: lấy trụ có "
             "Quan thấu can nếu chỉ một; còn lại không xác định được trụ, không có lời.")
add("O06A", "p.52", "左柱旺：工作单位大，效益好", "work", "pos", "nơi làm việc thường lớn, hiệu quả tốt", "can của trụ bên trái trụ Quan ngồi trên gốc của nó",
    eq("bazi.k.work_strong", True), LEFT_NOTE + " 'Vượng': can ngồi trên chi có cùng hành (tr.53 ví dụ 1: 'Giáp ngồi trên gốc').")
add("O06B", "p.52", "左柱弱：工作单位小，效益差", "work", "neg", "nơi làm việc thường nhỏ, hiệu quả không cao", "can của trụ bên trái trụ Quan không có gốc ngay dưới nó",
    eq("bazi.k.work_strong", False), LEFT_NOTE + " Tr.53 ví dụ 2: 'trụ bên trái khí yếu, Bính hỏa Ấn yếu'.")
GROUPS = {"ThucThuong": ("干为食伤：为餐饮业、手工业、技术业、演艺业、饲养业", "ăn uống, thủ công, kỹ thuật, biểu diễn, chăn nuôi"),
          "An": ("干为印星：为文化业、教育业", "văn hóa, giáo dục"), "QuanSat": ("干为官星：为行政业", "hành chính"),
          "Tai": ("干为财星：为金融业", "tài chính"), "Ti": ("干为比劫：为自由业、杂工", "nghề tự do, việc tạp")}
GVI = {"ThucThuong": "Thực Thương", "An": "Ấn", "QuanSat": "Quan Sát", "Tai": "Tài", "Ti": "Tỉ Kiếp"}
for g, (q, ph) in GROUPS.items():
    add(f"OG_{g.upper()}", "p.52", q, "work", "neutral", f"nghề hợp thiên về {ph}", f"can của trụ bên trái trụ Quan là {GVI[g]}",
        eq("bazi.k.work_group", g), LEFT_NOTE + " Thay cho luận điểm cũ đọc can trụ giờ (BT_ZZ_DIRECT_HOUR_GROUP_*).")
STEM = {"Giáp": ("干为甲木：医生、商人、政法、建筑、农林、化学、音乐", "y khoa, buôn bán, chính pháp, kiến trúc, nông lâm, hóa học, âm nhạc"),
        "Ất": ("干为乙木：园林、中介、手艺、印刷、旅游", "vườn cảnh, môi giới, nghề thủ công, in ấn, du lịch"),
        "Bính": ("干为丙火：游乐、检查官、鉴定师、化验师、美容师、冶炼业", "vui chơi giải trí, kiểm tra, giám định, xét nghiệm, làm đẹp, luyện kim, nhãn khoa, quà tặng, may mặc, hóa học, điện"),
        "Đinh": ("干为丁火：画家、演艺、历史学者、美容业、烹饪业", "hội họa, biểu diễn, nghiên cứu lịch sử, làm đẹp, nấu ăn"),
        "Mậu": ("干为戊土：牧业、农业、建筑、屠宰业、皮草业、家具业", "chăn nuôi, nông nghiệp, xây dựng, giết mổ, da lông, đồ gỗ"),
        "Kỷ": ("干为己土：秘书、打字员、排版员、服务员、民俗艺人", "thư ký, đánh máy, sắp chữ, phục vụ, nghệ nhân dân gian, địa chính, giáo viên mầm non, sản phụ khoa, đô thị, vệ sinh, vật tư"),
        "Canh": ("干为庚金：金属业、雕刻、司法、医生、导演、武术、屠夫", "kim loại, điêu khắc, tư pháp, y khoa, đạo diễn, võ thuật, giết mổ"),
        "Tân": ("干为辛金：首饰、锁业、律师、议员、法官、占卜", "kim hoàn, khóa, luật sư, nghị sĩ, thẩm phán, bói toán"),
        "Nhâm": ("干为壬水：运输业、造船业、水利、消防、水产、环保", "vận tải, đóng tàu, thủy lợi, phòng cháy, thủy sản, môi trường"),
        "Quý": ("干为癸水：心理学、参谋、调度、设计、策划", "tâm lý học, tham mưu, điều độ, thiết kế, hoạch định")}
for s, (q, ph) in STEM.items():
    slug = {"Giáp": "GIAP", "Ất": "AT", "Bính": "BINH", "Đinh": "DINH", "Mậu": "MAU", "Kỷ": "KY", "Canh": "CANH", "Tân": "TAN", "Nhâm": "NHAM", "Quý": "QUY"}[s]
    add(f"OS_{slug}", "p.52", q, "work", "neutral", f"nghề có thể thuộc nhóm {ph}", f"can của trụ bên trái trụ Quan là {s}", eq("bazi.k.work_stem", s),
        LEFT_NOTE + " Mục 8 ghi thêm '(tức hành của can trụ giờ)'; hệ thống đọc theo cùng trụ bên trái như mục 6-7 và hai ví dụ tr.53.")
# ---------------- quan chức, pp.52-53 (官职质量直断)
add("R01", "p.52", "时上一位贵而清和，必在仕途发达", "rank", "pos", "đường công danh dễ hanh thông", "can giờ là Chính Quan duy nhất trong lá số, không bị hợp, xung",
    eq("bazi.k.hour_lone_quan", True), "'Thanh hòa': can giờ không hợp, không xung với can nào (cách hiểu của hệ thống).")
add("R03", "p.52", "官星印：一气互通，仕途明亮", "rank", "pos", "đường công danh sáng sủa", "Quan Sát nối với Ấn đứng sát nhật chủ, khí thông một mạch",
    ALL(QF, no(ALL(QT, no(QR)))), "'Một khí thông nhau': Quan sinh Ấn, Ấn đứng sát nhật chủ (cùng chuỗi 'chảy vào nhật chủ' của tr.50-51). Khi Quan thấu can mà "
    "không gốc thì tr.53 mục 6 ('Quan hư thấu, dù chảy vào nhật chủ, cũng không có chức') đứng thay.")
add("R04", "p.52", "官杀均透而通根，无破流入日主，一身多职", "rank", "pos", "một người kiêm nhiều chức vụ", "Chính Quan và Thất Sát đều thấu can, có gốc và chảy vào nhật chủ",
    ALL(eq("bazi.k.quan_sat_both", True), QF), "Thay cho BT_ZZ_DIRECT_O_QUAN_SAT_ROOT, vốn bỏ qua điều kiện 'chảy vào nhật chủ'; 'không bị phá' chưa được tính riêng.")
add("R05", "p.52", "官旺透干而未流入日主，一生无官", "rank", "neg", "khó có chức vụ", "Quan Sát vượng, thấu can mà không chảy vào nhật chủ",
    ALL(V("QuanSat"), QT, no(QF)), CONV)
add("R06", "p.53", "官虚透，虽流入日主，而无官", "rank", "neg", "khó có chức vụ", "Quan Sát thấu can mà không có gốc, dù chảy được vào nhật chủ",
    ALL(QT, no(QR), QF))
add("R08", "p.53", "官星近身，虽与官人亲近，而无官缘", "rank", "neg", "gần gũi người có chức quyền nhưng bản thân ít duyên chức vụ",
    "Quan Sát đứng sát nhật chủ (ở can tháng, can giờ hoặc chi ngày) mà không qua Ấn", ALL(eq("bazi.k.quan_near_dm", True), eq("bazi.k.hour_lone_quan", False), no(QF)),
    "Khi Quan chảy vào nhật chủ qua Ấn thì là 'một khí thông nhau' (tr.52 mục 3), không còn là Quan đứng sát thân; khi can giờ là Chính Quan duy nhất, "
    "thanh hòa (tr.52 mục 1), lời ấy cụ thể hơn và đứng thay câu này (quy ước của hệ thống).")
add("R10", "p.53", "官星伏库逢冲，官场显达", "rank", "pos", "có thể hiển đạt trên đường quan chức", "Quan Sát ẩn trong khố ở trụ năm hoặc giờ, khố ấy bị xung mở",
    eq("bazi.k.quan_kho_clash", True), "Khố: Thìn, Tuất, Sửu, Mùi ở trụ năm hoặc giờ (tr.63).")
# ---------------- cha mẹ, p.55 (non-lifespan items)
add("P03", "p.55", "财印相战无官流通，父母不和", "parents", "neg", "cha mẹ không hòa thuận", "Tài và Ấn đứng sát nhau khắc nhau mà không có Quan Sát thông khí",
    ALL(eq("bazi.k.tai_an_war", True), eq("bazi.k.quan_present", False)))
add("P04", "p.55", "财印相战有官流通，父母感情浓厚", "parents", "pos", "cha mẹ tình cảm đằm thắm", "Tài và Ấn đứng sát nhau khắc nhau nhưng có Quan Sát thông khí",
    ALL(eq("bazi.k.tai_an_war", True), eq("bazi.k.quan_present", True)))
add("P05", "p.55", "财星重重无印，父母感情深", "parents", "pos", "cha mẹ tình cảm sâu nặng", "Tài trùng điệp mà không có Ấn",
    ALL(gte("bazi.k.tai_count", 3), A("An")), "Vế sau của câu sách nói về tuổi thọ của mẹ: không đưa vào văn.")
# ---------------- hôn nhân, pp.57-58
add("M07", "p.57", "月日为刑冲穿绝：被父母所迫婚姻，夫妻不和", "marriage", "neg", "hôn nhân dễ chịu sức ép từ cha mẹ, vợ chồng khó hòa",
    "chi tháng và chi ngày hình, xung hoặc hại nhau", eq("bazi.k.md_hurt", True), "Hệ thống chưa tính 'tuyệt', nên chỉ xét hình, xung, hại (xuyên).")
add("M18", "p.57", "日支为枭伤劫杀者：配偶不佳", "marriage", "neg", "người phối ngẫu khó được như ý", "chi ngày mang chính khí Thiên Ấn, Thương Quan, Kiếp Tài hoặc Thất Sát",
    inn("bazi.k.day_god", ["Thiên Ấn", "Thương Quan", "Kiếp Tài", "Thất Sát"]))
add("M19", "p.57", "命局七柱构成三连、四连字者：婚姻不吉", "marriage", "neg", "hôn nhân kém thuận", "một địa chi lặp từ ba lần trở lên trong bảy trụ (tứ trụ cùng thai, mệnh, thân)",
    eq("bazi.k.triple_branch", True), "Ví dụ 1 tr.58 đếm 'ba Dần' trên bảy trụ; hệ thống chỉ đếm địa chi.")
add("M20", "p.57", "配偶宫在月时伏吟：感情风波", "marriage", "neg", "tình cảm dễ có sóng gió", "chi ngày (cung phối ngẫu) trùng chi tháng hoặc chi giờ",
    eq("bazi.k.spouse_fuyin", True))
add("M23", "p.57", "胎身命合日支：婚姻美满", "marriage", "pos", "hôn nhân êm đẹp", "thai nguyên, mệnh cung hoặc thân cung lục hợp với chi ngày",
    eq("bazi.k.tmm_combine_day", True))
add("M24M", "p.57", "日主入日支墓：男惧内", "marriage", "neutral", "người chồng thường nể vợ", "nhật chủ ở giai đoạn Mộ trên chính chi ngày",
    ALL(eq("bazi.k.dm_tomb_day", True), eq("bazi.k.gender", "nam")))
add("M24F", "p.57", "日主入日支墓：男惧内，女从夫", "marriage", "neutral", "người vợ thường thuận theo chồng", "nhật chủ ở giai đoạn Mộ trên chính chi ngày",
    ALL(eq("bazi.k.dm_tomb_day", True), eq("bazi.k.gender", "nữ")))
add("M29", "p.58", "男命财旺流入日主：得妻助", "marriage", "pos", "được vợ giúp sức", "lá số nam, Tài (sao vợ) vượng và chảy vào nhật chủ",
    ALL(eq("bazi.k.spouse_flow", True), eq("bazi.k.gender", "nam")), "Vế sau của câu (Tài chảy vào trụ khác) nói chuyện ngoại tình: không đưa vào văn. " + CONV)
add("M30", "p.58", "女命官旺流入日主：夫妻感情深", "marriage", "pos", "vợ chồng tình cảm sâu nặng", "lá số nữ, Quan Sát (sao chồng) vượng và chảy vào nhật chủ",
    ALL(eq("bazi.k.spouse_flow", True), eq("bazi.k.gender", "nữ")), "Vế sau của câu nói chuyện ngoại tình: không đưa vào văn. " + CONV)
add("M33", "p.58", "夫妻星空亡：配偶感情不真", "marriage", "neg", "tình cảm của người phối ngẫu khó thật lòng", "sao phối ngẫu rơi vào không vong",
    eq("bazi.k.spouse_void", True), "Sao phối ngẫu: nam là Tài, nữ là Quan Sát (tr.57).")
# ---------------- anh em, pp.63-64 (非夭折 items)
add("S21", "p.64", "比劫过盛，为兄弟所累", "siblings", "neg", "dễ vì anh em mà vất vả", "Tỉ Kiếp quá nhiều", gte("bazi.k.ti_count", 3),
    "'Quá nhiều': từ ba chữ Tỉ Kiếp trở lên ngoài nhật chủ (quy ước của hệ thống).")
add("S22", "p.64", "身旺而比劫弱近身，则扶助兄弟", "siblings", "pos", "thường là người đỡ đần anh em", "nhật chủ vượng, có Tỉ Kiếp yếu (không ngồi trên gốc) đứng sát bên",
    eq("bazi.k.ti_weak_near", True))
add("S24", "p.64", "比劫与日主夹印，为家产反目", "siblings", "neg", "anh em dễ bất hòa vì tài sản trong nhà", "Tỉ Kiếp ở can năm và nhật chủ kẹp Ấn ở can tháng",
    eq("bazi.k.ti_an_dm", True))
add("S25", "p.64", "比劫与日主夹财，为家财争夺", "siblings", "neg", "anh em dễ tranh nhau của cải trong nhà", "Tỉ Kiếp ở can năm và nhật chủ kẹp Tài ở can tháng",
    eq("bazi.k.ti_tai_dm", True))
add("S26", "p.64", "比劫与日主夹杀，同心同德", "siblings", "pos", "anh em đồng lòng", "Tỉ Kiếp ở can năm và nhật chủ kẹp Thất Sát ở can tháng",
    eq("bazi.k.ti_sat_dm", True))
add("S27", "p.64", "比劫坐印或通根而日弱，兄弟强", "siblings", "neutral", "anh em mạnh hơn mình", "Tỉ Kiếp ngồi trên Ấn hoặc có gốc, còn nhật chủ nhược",
    eq("bazi.k.ti_over_dm", True))
add("S28", "p.64", "比劫坐支克泄而日主坐印或通根", "siblings", "neutral", "mình mạnh hơn anh em", "Tỉ Kiếp ngồi trên chi khắc hoặc rút khí nó, còn nhật chủ ngồi trên Ấn hoặc có gốc",
    ALL(eq("bazi.k.dm_over_ti", True), eq("bazi.k.ti_over_dm", False)), "Kết câu in ở dòng sau: '…弱，己强于兄弟' (mình mạnh hơn anh em).")
# ---------------- lưu niên, pp.64-65 (断命流金口: 流年)
Y = lambda f, v: eq(f"bazi.ky.{f}", v)
YG = lambda g: has("bazi.ky.groups", g)
YD = lambda g: has("bazi.ky.gods", g)
add("Y01", "p.64", "四库相冲：换房或修造装饰", "year", "neutral", "dễ đổi chỗ ở hoặc sửa sang nhà cửa", "chi năm là một trong bốn khố, xung một khố trong tứ trụ",
    Y("tomb_clash", True))
add("Y08", "p.64", "大岁运并临：定多忧", "year", "neg", "nhiều điều lo nghĩ", "năm trùng hẳn can chi với đại vận đang đi", Y("same_as_luck", True),
    "'Đại': đại vận (tr.64 mục 9-12 nói 'tiểu' vận, hệ thống chưa tính tiểu vận).")
add("Y13", "p.64", "刃头财年运：必破财", "year", "neg", "dễ hao tài", "can năm là Tài đứng trên chi dương nhẫn của nhật chủ", Y("tai_on_blade", True))
add("Y14", "p.64", "空亡填实之年是什么，则什么凶", "year", "neg", "chuyện ứng với chữ ấy dễ trắc trở", "chi năm lấp đúng chỗ không vong của lá số", Y("fill_void", True))
add("Y21", "p.65", "刑冲穿绝胎身命，年运者：必凶", "year", "neg", "dễ có trắc trở", "chi năm hình, xung hoặc hại thai nguyên, mệnh cung hoặc thân cung",
    Y("tmm_hurt", True), "Hệ thống chưa tính 'tuyệt', nên chỉ xét hình, xung, hại.")
add("Y22", "p.65", "命局中印官财为流年空亡字：必应凶", "year", "neg", "dễ có chuyện không như ý", "chữ Ấn, Quan hoặc Tài trong tứ trụ rơi vào không vong của năm",
    anyof("bazi.ky.natal_void_gods", ["Chính Ấn", "Thiên Ấn", "Chính Quan", "Chính Tài", "Thiên Tài"]))
add("Y23", "p.65", "命局中杀伤枭刃为流年空亡字：必应凶", "year", "neg", "dễ có chuyện không như ý", "chữ Sát, Thương hoặc Kiêu trong tứ trụ rơi vào không vong của năm",
    ALL(anyof("bazi.ky.natal_void_gods", ["Thất Sát", "Thương Quan", "Thiên Ấn"]), no(anyof("bazi.ky.natal_void_gods", ["Chính Ấn", "Thiên Ấn", "Chính Quan", "Chính Tài", "Thiên Tài"]))),
    "Khi chữ Ấn, Quan hoặc Tài của lá số cũng rơi vào không vong, mục 22 đã nói cùng một lời; Kiêu (Thiên Ấn) thuộc cả hai mục.")
add("Y24", "p.65", "身弱官杀旺行杀运：必应凶", "year", "neg", "dễ gặp chuyện không thuận", "nhật chủ nhược, Quan Sát vượng, năm lại mang Thất Sát", ALL(WEAK, V("QuanSat"), YD("Thất Sát")), CONV)
add("Y25", "p.65", "身旺印枭旺入枭地：必应凶", "year", "neg", "dễ gặp chuyện không thuận", "nhật chủ vượng, Ấn vượng, năm lại mang Thiên Ấn", ALL(STRONG, V("An"), YD("Thiên Ấn")), CONV)
add("Y26", "p.65", "身旺比劫旺入刃地：必应灾", "year", "neg", "dễ gặp chuyện không thuận", "nhật chủ vượng, Tỉ Kiếp vượng, chi năm lại là dương nhẫn", ALL(STRONG, V("Ti"), Y("blade", True)), CONV)
add("Y28", "p.65", "弱伤行官杀旺地：应灾", "year", "neg", "dễ gặp chuyện không thuận", "Thực Thương yếu, năm lại mang Quan Sát", ALL(N("ThucThuong"), YG("QuanSat")), CONV)
add("Y29", "p.65", "官杀混杂而旺入杀运：应凶", "year", "neg", "dễ gặp chuyện không thuận", "Chính Quan và Thất Sát lẫn nhau mà vượng, năm lại mang Thất Sát",
    ALL(Y("guan_mixed", True), V("QuanSat"), YD("Thất Sát")), CONV)
add("Y30", "p.65", "官杀旺身弱入刃地：应凶", "year", "neg", "dễ gặp chuyện không thuận", "Quan Sát vượng, nhật chủ nhược, chi năm là dương nhẫn", ALL(V("QuanSat"), WEAK, Y("blade", True)), CONV)
add("Y31", "p.65", "身弱印弱行财乡：应凶", "year", "neg", "dễ gặp chuyện không thuận", "nhật chủ nhược, Ấn yếu, năm lại mang Tài", ALL(WEAK, N("An"), YG("Tai")), CONV)
add("Y32", "p.65", "身弱印弱行食伤旺地：应凶", "year", "neg", "dễ gặp chuyện không thuận", "nhật chủ nhược, Ấn yếu, năm lại mang Thực Thương", ALL(WEAK, N("An"), YG("ThucThuong")), CONV)
add("Y34", "p.65", "身旺官杀弱行刃地：应凶", "year", "neg", "dễ gặp chuyện không thuận", "nhật chủ vượng, Quan Sát yếu, chi năm là dương nhẫn", ALL(STRONG, N("QuanSat"), Y("blade", True)), CONV)
add("Y35", "p.65", "身旺官杀弱行食伤运：应凶", "year", "neg", "dễ gặp chuyện không thuận", "nhật chủ vượng, Quan Sát yếu, năm lại mang Thực Thương", ALL(STRONG, N("QuanSat"), YG("ThucThuong")), CONV)
add("Y36", "p.65", "财旺无印枭入印运：应凶", "year", "neg", "dễ gặp chuyện không thuận", "Tài vượng mà không có Ấn, năm lại mang Ấn", ALL(V("Tai"), A("An"), YG("An")), CONV)
add("Y37", "p.65", "印旺无食伤入食运：应凶", "year", "neg", "dễ gặp chuyện không thuận", "Ấn vượng mà không có Thực Thương, năm lại mang Thực Thần", ALL(V("An"), A("ThucThuong"), YD("Thực Thần")), CONV)
add("Y38", "p.65", "食伤旺无官杀入官运：应凶", "year", "neg", "dễ gặp chuyện không thuận", "Thực Thương vượng mà không có Quan Sát, năm lại mang Chính Quan", ALL(V("ThucThuong"), A("QuanSat"), YD("Chính Quan")), CONV)
add("Y42", "p.65", "比劫刃禄旺入财乡：应凶", "year", "neg", "dễ gặp chuyện không thuận", "Tỉ Kiếp vượng, năm lại mang Tài", ALL(V("Ti"), YG("Tai")), CONV)
add("Y44", "p.65", "身弱财旺行官杀乡：应灾", "year", "neg", "dễ gặp chuyện không thuận", "nhật chủ nhược, Tài vượng, năm lại mang Quan Sát", ALL(WEAK, V("Tai"), YG("QuanSat")), CONV)


# the condition said with this chart's characters (kin.fire fills the slots; a slot with nothing to name keeps the general wording above)
SAY = {
    "W01": "nhật chủ vượng, Tỉ Kiếp có {ti_n} chữ ({ti}) mà lá số không có Tài", "W02R": "Chính Tài lộ ở {ct} và có gốc",
    "W02": "Chính Tài lộ ở {ct}, tuy không có gốc nhưng được chữ đứng sát bên sinh cho", "W04": "Chính Tài ở {ct} ngồi trên đất Mộ của nó",
    "W05": "Chính Tài lộ ở {ct} mà không có gốc, cũng không được chữ nào đứng sát bên sinh cho", "W06": "Chính Tài lộ ở {ct} không gốc, không được sinh, lại bị hình xung",
    "W07": "Chính Tài không lộ ra can mà nằm ở {ct_hidden}, được chữ đứng sát bên sinh cho", "W08": "Chính Tài ở {ct_cut}",
    "W09": "Thiên Tài lộ ở {tt}", "W10R": "Thiên Tài lộ ở {tt} và có gốc", "W10": "Thiên Tài lộ ở {tt}, tuy không có gốc nhưng được chữ đứng sát bên sinh cho",
    "W11": "Thiên Tài ở {tt} ngồi trên khố của nó", "W12": "Thiên Tài ở {tt_cut}",
    "W13": "Thiên Tài không lộ ra can mà nằm ở {tt_hidden}, được chữ đứng sát bên sinh cho", "W14": "Thiên Tài chỉ nằm ở {tt_cover}",
    "W16": "Chính Tài ({ct}) và Thiên Tài ({tt}) đều lộ can và có gốc", "W19": "Tài nằm ở {tmm_tai}", "W21": "chữ Tài ở {tai_void} rơi vào không vong",
    "O03A": "Quan lộ ở {qtrans}, có gốc và chảy vào nhật chủ ({qchain})", "O03B": "Quan lộ ở {qtrans}, có gốc nhưng chưa chảy vào nhật chủ",
    "O04A": "Quan lộ ở {qtrans} không có gốc, nhưng chảy được vào nhật chủ ({qchain})", "O04B": "Quan lộ ở {qtrans} không có gốc, lại không chảy vào nhật chủ",
    "O05A": "Quan Sát vượng ({qs_pct}% số độ) và chảy vào nhật chủ ({qchain})", "O05B": "Quan Sát vượng ({qs_pct}% số độ) nhưng không chảy vào nhật chủ",
    "R05": "Quan Sát vượng, lộ ở {qtrans} mà không chảy vào nhật chủ", "R06": "Quan lộ ở {qtrans} mà không có gốc, dù chảy được vào nhật chủ",
    "R08": "Quan Sát ở {qnear} đứng sát nhật chủ mà không qua Ấn",
    "R03": "Quan Sát và Ấn nối nhau ({qchain}), Ấn đứng sát nhật chủ, khí thông một mạch", "R04": "Chính Quan và Thất Sát đều lộ can, có gốc và chảy vào nhật chủ ({qchain})", "P03": "{war} mà không có Quan Sát thông khí", "P04": "{war}, có Quan Sát thông khí",
    "P05": "Tài có {tai_n} chữ mà lá số không có Ấn", "M07": "{md}", "M18": "chi ngày {db} mang chính khí {day_god}",
    "M19": "địa chi {triple} lặp từ ba lần trở lên trong bảy trụ", "M20": "chi ngày {db}, cung phối ngẫu, trùng {fuyin}", "M23": "{tmm_day} lục hợp với chi ngày {db}",
    "M24M": "nhật chủ {dm} ở giai đoạn Mộ trên chính chi ngày {db}", "M24F": "nhật chủ {dm} ở giai đoạn Mộ trên chính chi ngày {db}",
    "M33": "sao phối ngẫu ở {spouse_void} rơi vào không vong", "S21": "Tỉ Kiếp có {ti_n} chữ ({ti})",
    "Y01": "chi {yb} của năm là một khố, xung {tomb}", "Y08": "năm trùng hẳn đại vận {luck}", "Y13": "can {ys} là Tài, đứng trên chi {yb} là dương nhẫn của nhật chủ {dm}",
    "Y14": "chi {yb} lấp đúng chỗ không vong của lá số", "Y21": "chi {yb} {tmm}", "Y22": "{vat} rơi vào không vong của năm",
    "Y23": "{vat} rơi vào không vong của năm", "Y31": "nhật chủ nhược, Ấn yếu, năm lại mang {tai_y}", "Y32": "nhật chủ nhược, Ấn yếu, năm lại mang {tt_y}",
    "Y36": "Tài vượng mà không có Ấn, năm lại mang {an_y}", "Y42": "Tỉ Kiếp vượng, năm lại mang {tai_y}", "Y44": "nhật chủ nhược, Tài vượng, năm lại mang {qs_y}",
    "Y28": "Thực Thương yếu, năm lại mang {qs_y}", "Y35": "nhật chủ vượng, Quan Sát yếu, năm lại mang {tt_y}",
}
SRC = {"id": "SRC_BAZI_ZHENZONG_KIN", "title": "八字真宗 (Bát Tự Chân Tông) — 财运、工作、官职、父母、婚姻、兄弟、流年直断", "author": "unknown (PDF circulated via ChienNguyen)",
       "locator": "PDF pp.50-58, 63-65 (text layer in data/bazi_deep/mined/)", "verified": True, "edition": "PDF, simplified Chinese, 96 pp.",
       "note": "Đọc trực tiếp lớp chữ của bản PDF (Claude, 2026-10-23); mỗi luật có câu in nguyên văn trong quotes_zz_kin.json, test đối chiếu với trang đã chép."}
rules, meta = [], {}
for r in R:
    rules.append({"id": r["id"], "system": "bat_tu", "schoolId": "bazi_zhenzong_popular", "category": f"zz_kin_{r['topic']}",
                  "description": f"八字真宗 {r['page']}: {r['quote']} — {r['effect']} ({r['cause']})", "conditions": r["cond"],
                  "consequences": [{"kind": "finding", "claim": r["id"].lower(), "effect": {"pos": "support", "neg": "limit"}.get(r["tone"], "neutral"), "scope": "natal"}],
                  "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": [SRC["id"]], "reviewStatus": r["status"], "version": "0.1.0", "subject": "chart"})
    short = r["id"].removeprefix("BT_ZZK_")
    meta[r["id"]] = {k: r[k] for k in ("page", "quote", "topic", "tone", "effect", "cause")} | ({"say": SAY[short]} if short in SAY else {}) | ({"note": r["note"]} if r["note"] else {})
assert len({r["id"] for r in rules}) == len(rules)
(D / "pack_zz_kin.json").write_text(json.dumps({"sources": [SRC], "rules": rules}, ensure_ascii=False, indent=1) + "\n", "utf-8")
(D / "quotes_zz_kin.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", "utf-8")
print(len(rules), "rules")
