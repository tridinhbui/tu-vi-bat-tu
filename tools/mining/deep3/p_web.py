family("web")
# ---------------------------------------------------------------- 紫微斗數全書 卷二 (zh.wikisource snapshot, engine/data/sources_web/zwds_quanshu_2.txt).
# The 'page' of a WEB entry is the section heading. 庙 / 旺 / 陷 are read on the Toàn Thư brightness table (dignity@toan_thu): the nearest
# table the engine has for this book. Counts of siblings / children, their sex, 刑克 (death), adoption and step-parents are left out by policy.
W2 = "WEB:zwds_quanshu_2"
page(W2, "二兄弟", "兄弟 (siblings): per star, counts + 和 / 不和; the counts are not used.", img=False)
page(W2, "四子女", "子女 (children): mostly counts, sex and 刑克; used: 貴子 / 不成器 / 強橫敗家.", img=False)
page(W2, "八奴仆", "奴仆 (servants, subordinates, friends of lower rank): 得力 / 欠力 / 背主 / 怨主 / 一呼百諾.", img=False)
page(W2, "十二父母", "父母: mostly 刑克 (death of a parent) and adoption; used: 榮貴, 庇蔭, 破父財, 欠和.", img=False)
HD, TU, NO, PM = "Huynh Đệ", "Tử Tức", "Nô Bộc", "Phụ Mẫu"


def W(id, sec, pal, quote, cond, reading, pol, concepts, **k):
    E(id, W2, sec, pal, f"紫微斗數全書 卷二 · {sec}", quote, cond, reading, pol, concepts, **k)


# 二兄弟
W("w2_bao_tu_sat", "二兄弟", HD, "加羊陀火铃空劫克害有则欠和", "Huynh Đệ có Tử Vi, thêm Kình, Đà, Hỏa, Linh, Không hoặc Kiếp", "anh em kém hòa thuận", "limit", ["kin.strain"],
  notes="紫微有倚靠年长之兄 ... 加羊陀火铃空劫克害有则欠和 (the counts are left out)")
W("w2_bao_co_ham", "二兄弟", HD, "陷地，相背不一心", "Huynh Đệ có Thiên Cơ hãm", "anh em không cùng một lòng", "limit", ["kin.strain"],
  notes="天机庙旺有二人，与巨门同二人，陷地，相背不一心")
W("w2_bao_nhat_ham", "二兄弟", HD, "陷地，不和欠力", "Huynh Đệ có Thái Dương hãm", "anh em không hòa, ít giúp được nhau", "limit", ["kin.strain"],
  notes="太阳 ... 陷地，不和欠力")
W("w2_bao_vu_khong_hop", "二兄弟", HD, "武曲庙旺有二人，不合", "Huynh Đệ có Vũ Khúc miếu, vượng", "anh em không hợp nhau", "limit", ["kin.strain"])
W("w2_bao_vu_pha_sat", "二兄弟", HD, "破军七杀同有一人，不和睦", "Huynh Đệ có Vũ Khúc đồng cung Phá Quân hoặc Thất Sát", "anh em không hòa thuận", "limit", ["kin.strain"])
W("w2_bao_dong_sat_ky", "二兄弟", HD, "见羊陀火铃空劫忌，少宜分居不和", "Huynh Đệ có Thiên Đồng, thêm Kình, Đà, Hỏa, Linh, Không, Kiếp hoặc Hóa Kỵ",
  "anh em nên ở riêng, không hòa", "limit", ["kin.apart", "kin.strain"])
W("w2_bao_liem_tham", "二兄弟", HD, "贪狼同招怨", "Huynh Đệ có Liêm Trinh đồng cung Tham Lang", "anh em sinh oán", "limit", ["kin.strain"])
W("w2_bao_liem_note", "二兄弟", HD, "兄弟感情融洽，但兄弟不多", "Liêm Trinh", "", "support", [],
  skip="a modern note added to the transcription (vernacular, not classical); not used")
W("w2_bao_cu_ham", "二兄弟", HD, "巨门庙旺二人，陷地，各胞有，宜分居", "Huynh Đệ có Cự Môn hãm", "anh em nên ở riêng", "limit", ["kin.apart"],
  notes="各胞 (half-siblings) left out")
W("w2_bao_cu_co", "二兄弟", HD, "天机同有二人，更乖违不一心", "Huynh Đệ có Cự Môn đồng cung Thiên Cơ", "anh em càng trái ý, không cùng lòng", "limit", ["kin.strain"])
W("w2_bao_luong_mieu", "二兄弟", HD, "天梁庙旺二人和顺", "Huynh Đệ có Thiên Lương miếu, vượng", "anh em hòa thuận", "support", ["kin.harmony"])
W("w2_bao_that_sat", "二兄弟", HD, "七杀主孤克，在子午寅申宫方有三人，也不和宜各人", "Huynh Đệ có Thất Sát", "anh em không hòa, nên mỗi người một nơi", "limit",
  ["kin.strain", "kin.apart"], notes="孤克 (death / loneliness) and the counts left out")
W("w2_bao_pha_xuong_khuc", "二兄弟", HD, "加昌曲左右有三人和睦", "Huynh Đệ có Phá Quân, thêm Văn Xương, Văn Khúc, Tả Phụ hoặc Hữu Bật", "anh em hòa thuận", "support",
  ["kin.harmony"], notes="破军入庙三人 ... 加昌曲左右有三人和睦")
W("w2_bao_ta_huu_kk", "二兄弟", HD, "有空劫欠力不和", "Huynh Đệ có Tả Phụ hoặc Hữu Bật, thêm Địa Không hoặc Địa Kiếp", "anh em ít giúp được nhau, không hòa", "limit",
  ["kin.strain"], notes="the same clause closes both the 左辅 and 右弼 lines")
W("w2_bao_loc_ton_sat", "二兄弟", HD, "禄存相生有兄弟见杀克害招怨", "Huynh Đệ có Lộc Tồn, thêm sát tinh", "anh em sinh oán", "limit", ["kin.strain"])

# 四子女
W("w2_tu_count_sex", "四子女", TU, "凡看子女先看本宫星宿主有几子", "", "", "limit", [], skip="counts and sex of children, 刑克 and 絕祀 (the bulk of the section)")
W("w2_tu_thien_dong_count", "四子女", TU, "天同庙旺五子有贵", "", "", "support", [], skip="a count of children")
W("w2_tu_tu_phu_cat", "四子女", TU, "加昌曲左右有贵子", "Tử Tức có Tử Vi và Thiên Phủ, thêm Văn Xương, Văn Khúc, Tả Phụ hoặc Hữu Bật", "có con quý hiển", "support",
  ["kin.talented"], notes="紫微 ... 天府同加吉星四五人，加昌曲左右有贵子")
W("w2_tu_liem_phu", "四子女", TU, "天府同主贵子三人", "Tử Tức có Liêm Trinh và Thiên Phủ", "có con quý hiển", "support", ["kin.talented"],
  notes="廉贞一人，天府同主贵子三人 (the count left out)")
W("w2_tu_am_mieu", "四子女", TU, "庙旺有贵子", "Tử Tức có Thái Âm miếu, vượng", "có con quý hiển", "support", ["kin.talented"],
  notes="太阴女三男二先女后男，庙旺有贵子 (sex and count left out)")
W("w2_tu_am_ham", "四子女", TU, "招软弱之子，或虚花不成器", "Tử Tức có Thái Âm hãm", "con cái dễ yếu đuối, khó thành người", "limit", ["kin.adverse"],
  notes="陷地减半，招软弱之子，或虚花不成器")
W("w2_tu_sat_sat", "四子女", TU, "纵有不成器，必强横败家之子", "Tử Tức có Thất Sát, thêm Kình, Đà, Hỏa, Linh, Không hoặc Kiếp", "con cái dễ ngang tàng, phá gia", "limit",
  ["kin.wayward"], notes="七杀 ... 见羊陀火铃空劫全无，纵有不成器，必强横败家之子 (全无 = a count: left out)")
W("w2_tu_pha_mieu", "四子女", TU, "破军入庙三人，刚强之子", "Tử Tức có Phá Quân miếu", "con cái cương cường", "support", [],
  skip="'cương cường' (刚强) has no concept in the KG and is neither good nor bad on the page")
W("w2_tu_ta_phu_tu_phu", "四子女", TU, "见紫微天府诸吉星主贵子", "Tử Tức có Tả Phụ, thêm Tử Vi hoặc Thiên Phủ", "có con quý hiển", "support", ["kin.talented"],
  notes="左辅单居男三女一，见紫微天府诸吉星主贵子")
W("w2_tu_ta_phu_sat", "四子女", TU, "有也不成器", "Tử Tức có Tả Phụ, thêm Phá Quân, Thất Sát, Kình, Đà, Hỏa, Linh, Không hoặc Kiếp", "con cái khó thành người", "limit",
  ["kin.adverse"], notes="见破杀羊陀火铃空劫止二人，有也不成器 (the count left out)")
W("w2_tu_huu_bat_cat", "四子女", TU, "右弼三人加吉星有贵子", "Tử Tức có Hữu Bật, thêm cát tinh", "có con quý hiển", "support", ["kin.talented"])
W("w2_tu_khoi_viet", "四子女", TU, "魁钺单守主有贵子", "Tử Tức không chính tinh, có Thiên Khôi hoặc Thiên Việt", "có con quý hiển", "support", ["kin.talented"])
W("w2_tu_tuong_thanh_khi", "四子女", TU, "天相无羊陀火铃同有二子成器", "", "", "support", [], skip="a count of sons")

# 八奴仆
W("w2_no_tu_vi", "八奴仆", NO, "紫微成行得力", "Nô Bộc có Tử Vi", "người dưới đắc lực", "support", ["ally.helpful"])
W("w2_no_tu_vi_sat", "八奴仆", NO, "加擎羊火铃陀罗欠力", "Nô Bộc có Tử Vi, thêm Kình Dương, Hỏa Tinh, Linh Tinh hoặc Đà La", "người dưới kém đắc lực", "limit", ["ally.weak"])
W("w2_no_tu_tuong_kk", "八奴仆", NO, "加空劫招怨逃走", "Nô Bộc có Tử Vi, Thiên Tướng, thêm Địa Không hoặc Địa Kiếp", "người dưới sinh oán rồi bỏ đi", "limit",
  ["ally.resent", "ally.fickle"], notes="紫微 ... 天相同得力，加空劫招怨逃走")
W("w2_no_co_mieu", "八奴仆", NO, "天机入庙得力", "Nô Bộc có Thiên Cơ miếu", "người dưới đắc lực", "support", ["ally.helpful"])
W("w2_no_co_ham", "八奴仆", NO, "陷空怨主", "Nô Bộc có Thiên Cơ hãm", "người dưới oán chủ", "limit", ["ally.resent"])
W("w2_no_nhat_mieu", "八奴仆", NO, "太阳入庙旺主发", "Nô Bộc có Thái Dương miếu", "người dưới giúp chủ phát đạt", "support", ["ally.helpful"])
W("w2_no_nhat_ham", "八奴仆", NO, "陷宫无分，有也怨主，会走", "Nô Bộc có Thái Dương hãm", "ít người dưới, có cũng oán chủ và bỏ đi", "limit", ["ally.resent", "ally.fickle"])
W("w2_no_vu_vuong", "八奴仆", NO, "武曲旺宫不少，一呼百诺", "Nô Bộc có Vũ Khúc miếu, vượng", "người dưới đông, một tiếng gọi trăm người dạ", "support", ["ally.many"])
W("w2_no_vu_phu", "八奴仆", NO, "天府同多奴多婢", "Nô Bộc có Vũ Khúc, Thiên Phủ", "nhiều người giúp việc", "support", ["ally.many"])
W("w2_no_vu_pha", "八奴仆", NO, "破军同招怨，会走", "Nô Bộc có Vũ Khúc, Phá Quân", "người dưới sinh oán, bỏ đi", "limit", ["ally.resent", "ally.fickle"])
W("w2_no_vu_sat", "八奴仆", NO, "七杀同，背主", "Nô Bộc có Vũ Khúc, Thất Sát", "người dưới phản chủ", "limit", ["ally.disloyal"])
W("w2_no_vu_tham", "八奴仆", NO, "贪狼同欠力", "Nô Bộc có Vũ Khúc, Tham Lang", "người dưới kém đắc lực", "limit", ["ally.weak"])
W("w2_no_dong", "八奴仆", NO, "天同得力旺相", "Nô Bộc có Thiên Đồng", "người dưới đắc lực", "support", ["ally.helpful"])
W("w2_no_dong_sat", "八奴仆", NO, "加羊陀火铃有背主之奴", "Nô Bộc có Thiên Đồng, thêm Kình, Đà, Hỏa hoặc Linh", "có người dưới phản chủ", "limit", ["ally.disloyal"])
W("w2_no_liem_ham", "八奴仆", NO, "廉贞陷地奴背主", "Nô Bộc có Liêm Trinh hãm", "người dưới phản chủ", "limit", ["ally.disloyal"])
W("w2_no_liem_mieu", "八奴仆", NO, "入庙一呼百诺", "Nô Bộc có Liêm Trinh miếu", "người dưới đông, một tiếng gọi trăm người dạ", "support", ["ally.many"],
  notes="廉贞陷地奴背主，晚年方招得，入庙一呼百诺")
W("w2_no_liem_sat", "八奴仆", NO, "贪狼同欠力，七杀同背主", "Nô Bộc có Liêm Trinh, Thất Sát", "người dưới phản chủ", "limit", ["ally.disloyal"],
  dup="TV_KL7_NO_BOC_LIEM_SAT", notes="KL p.219 reads Liêm Sát at Nô Bộc the same way")
W("w2_no_phu", "八奴仆", NO, "天府得力一呼百诺", "Nô Bộc có Thiên Phủ", "người dưới đắc lực, đông người theo", "support", ["ally.helpful", "ally.many"])
W("w2_no_phu_sat", "八奴仆", NO, "加陀羊火铃空劫多背主，逃走", "Nô Bộc có Thiên Phủ, thêm Kình, Đà, Hỏa, Linh, Không hoặc Kiếp", "người dưới hay phản chủ, bỏ đi", "limit",
  ["ally.disloyal"])
W("w2_no_am_mieu", "八奴仆", NO, "太阴庙地得力成行", "Nô Bộc có Thái Âm miếu", "người dưới đắc lực", "support", ["ally.helpful"])
W("w2_no_am_ham", "八奴仆", NO, "虽有而走，陷地全无", "Nô Bộc có Thái Âm hãm", "ít người dưới", "limit", ["ally.few"])
W("w2_no_tham", "八奴仆", NO, "贪狼初难招败主之奴", "Nô Bộc có Tham Lang", "dễ gặp người dưới làm hại chủ", "limit", ["ally.drain"])
W("w2_no_cu_mieu", "八奴仆", NO, "巨门入庙早年不得力，招是非，不能久居", "Nô Bộc có Cự Môn miếu", "người dưới gây thị phi, không ở lâu", "limit",
  ["ally.dispute", "ally.fickle"])
W("w2_no_tuong_vu", "八奴仆", NO, "武曲同怨主", "Nô Bộc có Thiên Tướng, Vũ Khúc", "người dưới oán chủ", "limit", ["ally.resent"], notes="天相末年招得，紫微同多奴多婢，武曲同怨主")
W("w2_no_tuong_tu", "八奴仆", NO, "紫微同多奴多婢", "Nô Bộc có Thiên Tướng, Tử Vi", "nhiều người giúp việc", "support", ["ally.many"])
W("w2_no_luong", "八奴仆", NO, "天梁奴多旺主", "Nô Bộc có Thiên Lương", "người dưới đông, giúp chủ thịnh", "support", ["ally.many", "ally.helpful"])
W("w2_no_luong_co", "八奴仆", NO, "天机同不一心", "Nô Bộc có Thiên Lương, Thiên Cơ", "người dưới không một lòng", "limit", ["ally.fickle"])
W("w2_no_that_sat", "八奴仆", NO, "七杀欺主有刚强之仆，多盗家财", "Nô Bộc có Thất Sát", "người dưới cứng đầu, lấn chủ, hay lấy của", "limit", ["ally.overstep", "ally.disloyal"])
W("w2_no_pha_mieu", "八奴仆", NO, "破军入庙得力", "Nô Bộc có Phá Quân miếu", "người dưới đắc lực", "support", ["ally.helpful"])
W("w2_no_pha_ham", "八奴仆", NO, "陷宫招怨背主", "Nô Bộc có Phá Quân hãm", "người dưới oán và phản chủ", "limit", ["ally.resent", "ally.disloyal"])
W("w2_no_xuong_doc", "八奴仆", NO, "文昌入庙独守得力助主", "Nô Bộc không chính tinh, có Văn Xương miếu", "người dưới đắc lực, giúp chủ", "support", ["ally.helpful"])
W("w2_no_khuc_mieu", "八奴仆", NO, "文曲入庙得力，陷宫无分", "Nô Bộc có Văn Khúc miếu", "người dưới đắc lực", "support", ["ally.helpful"])
W("w2_no_ta_doc", "八奴仆", NO, "左辅独守旺相一呼百诺", "Nô Bộc không chính tinh, có Tả Phụ", "người dưới đông, một tiếng gọi trăm người dạ", "support", ["ally.many"])
W("w2_no_huu_doc", "八奴仆", NO, "右弼独守成行", "Nô Bộc không chính tinh, có Hữu Bật", "người dưới đông", "support", ["ally.many"])
W("w2_no_ta_huu_sat", "八奴仆", NO, "背主盗财而走", "Nô Bộc có Tả Phụ hoặc Hữu Bật, thêm Kình, Đà, Hỏa, Linh, Không hoặc Kiếp", "người dưới phản chủ, lấy của mà đi", "limit",
  ["ally.disloyal"], notes="左辅 ... 加羊陀火铃空劫耗忌背主难招; 右弼 ... 加羊陀火铃空劫耗忌，背主盗财而走")
W("w2_no_loc_ton", "八奴仆", NO, "禄存奴仆多", "Nô Bộc có Lộc Tồn", "nhiều người giúp việc", "support", ["ally.many"])
W("w2_no_kinh", "八奴仆", NO, "擎羊背主招怨不得力", "Nô Bộc có Kình Dương", "người dưới oán và phản chủ, không đắc lực", "limit", ["ally.disloyal", "ally.resent"])
W("w2_no_da", "八奴仆", NO, "陀罗奴仆欠力怨主", "Nô Bộc có Đà La", "người dưới kém đắc lực, oán chủ", "limit", ["ally.weak", "ally.resent"])
W("w2_no_hoa_doc", "八奴仆", NO, "火星独守怨主不得力", "Nô Bộc không chính tinh, có Hỏa Tinh", "người dưới oán chủ, không đắc lực", "limit", ["ally.resent"])
W("w2_no_linh_doc", "八奴仆", NO, "铃星独守不得力", "Nô Bộc không chính tinh, có Linh Tinh", "người dưới không đắc lực", "limit", ["ally.weak"])

# 十二父母
W("w2_pm_khac", "十二父母", PM, "太阳在陷宫主先克父", "", "", "limit", [], skip="刑克 (a parent's death), adoption, step-parents: most of the section")
W("w2_pm_khoi_viet", "十二父母", PM, "魁钺主父母荣贵同吉星双全", "Phụ Mẫu có Thiên Khôi hoặc Thiên Việt", "cha mẹ vinh hiển", "support", ["parents.prosper"],
  notes="the 双全 clause (both parents alive) is left out")
W("w2_pm_huu_bat", "十二父母", PM, "加吉星得父母庇荫", "Phụ Mẫu không chính tinh, có Hữu Bật, thêm cát tinh", "được cha mẹ che chở", "support", ["fortune.protected"],
  notes="右弼独守无刑，加吉星得父母庇荫")
W("w2_pm_loc_ton_sat", "十二父母", PM, "早年有破父财", "Phụ Mẫu có Lộc Tồn, thêm Kình, Đà, Hỏa, Linh, Không hoặc Kiếp", "thuở nhỏ của cải của cha mẹ hao tổn", "limit",
  ["parents.poor"], notes="禄存无克，加空劫羊陀火铃，早年有破父财")
W("w2_pm_dong_cu", "十二父母", PM, "巨门同欠和", "Phụ Mẫu có Thiên Đồng, Cự Môn", "với cha mẹ kém hòa thuận", "limit", ["parents.strain"],
  notes="天同独守 ... 巨门同欠和")
W("w2_pm_cu_nhat", "十二父母", PM, "太阳同少和", "Phụ Mẫu có Cự Môn, Thái Dương", "với cha mẹ ít hòa thuận", "limit", ["parents.strain"], notes="巨门陷地 ... 太阳同少和")

# ---------------------------------------------------------------- 紫微斗數全書 卷一: the 局 lists and the 十二宮 hợp cách / phá cách verses, the originals of TT
# pp.141-149 (Vũ Tài Lục's translation); used to settle readings and to record school differences (schools.json), not made into rules here.
W1 = "WEB:zwds_quanshu_1"
for _sec, _note in [("定富局", "6 phú cục"), ("定贵局", "quý cục"), ("定贫贱局", "bần tiện cục"), ("十二宫诸星得地合格诀", "hợp cách by Mệnh branch"),
                    ("十二宫诸星失陷破格诀", "phá cách by Mệnh branch"), ("十二宫诸星得地富贵论", "đắc địa phú quý luận"),
                    ("十二宫诸星失陷贫贱论", "thất hãm bần tiện luận"), ("斗数骨髓赋", "cốt tủy phú")]:
    page(W1, _sec, _note, img=False)


def W1E(id, sec, quote, topic, reading):
    E(id, W1, sec, "Mệnh", f"紫微斗數全書 卷一 · {sec}", quote, topic, reading, "neutral", [], target="schools")


W1E("w1_kim_du_phu_gia", "定贵局", "金舆扶驾 紫微守命前后有日月来夹是也", "Kim dư phù giá", "Tử Vi thủ Mệnh, trước sau có Nhật Nguyệt giáp")
W1E("w1_that_sat_trieu_dau", "斗数骨髓赋", "七杀朝斗爵禄荣昌", "Thất Sát triều đẩu", "Thất Sát triều đẩu thì tước lộc vinh xương (không ghi vị trí)")
W1E("w1_nhat_xuat_phu_tang", "定贵局", "日出扶桑 日在卯守命是也，守官禄宫亦然", "Nhật xuất phù tang", "Thái Dương ở Mão thủ Mệnh; thủ Quan Lộc cũng vậy")
W1E("w1_nguyet_sinh_thuong_hai", "定贵局", "月生沧海 月在子宫守田宅是也", "Nguyệt sinh thương hải", "Thái Âm ở Tý thủ Điền Trạch")
W1E("w1_toa_quy_huong_quy", "定贵局", "坐贵向贵 谓魁钺在命迭相坐拱是也", "Tọa quý hướng quý", "Khôi Việt ở Mệnh, thay nhau tọa và củng")
W1E("w1_tham_hoa", "定贵局", "贪火相逢 谓二星守命同居庙旺是也", "Tham Hỏa tương phùng", "Tham Lang, Hỏa Tinh cùng thủ Mệnh, đều miếu vượng")
W1E("w1_tai_loc_giap_ma", "定富局", "财禄夹马 马守命武禄来夹是也，逢生旺尤妙", "Tài Lộc giáp Mã", "Thiên Mã thủ Mệnh, Vũ Khúc và Lộc giáp; ở đất sinh vượng càng tốt")
W1E("w1_tai_am_giap_an", "定富局", "财荫夹印 相守命武梁来夹是也，田宅宫亦然", "Tài ấm giáp ấn", "Thiên Tướng thủ Mệnh, Vũ Khúc và Thiên Lương GIÁP (夾); Điền Trạch cũng vậy")
W1E("w1_tai_an_giap_loc", "定贵局", "财印夹禄 禄守命梁相来夹是也，入财亦然", "Tài ấn giáp lộc", "Lộc thủ Mệnh, Thiên Lương và Thiên Tướng GIÁP; ở Tài Bạch cũng vậy")
W1E("w1_nn_chieu_bich", "定富局", "日月照璧 日月临田宅宫是也，喜居墓库", "Nhật Nguyệt chiếu bích", "Nhật Nguyệt ở Điền Trạch, ưa ở Tứ mộ")
W1E("w1_loc_phung_luong_sat", "定贫贱局", "禄逢两杀 禄坐空亡又逢空劫杀星是也", "Lộc phùng lưỡng sát", "Lộc ngồi Không Vong lại gặp Không Kiếp sát tinh")
W1E("w1_nn_tang_huy", "定贫贱局", "日月藏辉 日月反背又逢巨暗是也", "Nhật Nguyệt tàng huy", "Nhật Nguyệt phản bối (cả hai hãm) lại gặp Cự Môn")
W1E("w1_hinh_tu_giap_an", "定贵局", "刑囚夹印 天刑廉贞同临身命主武勇之人", "Hình tù giáp ấn", "Thiên Hình, Liêm Trinh cùng ở Thân Mệnh: người võ dũng")
W1E("w1_pha_cach_ty_suu", "十二宫诸星失陷破格诀", "子丑安命 子午天机丑巨铃", "phá cách Mệnh Tý Sửu", "Thiên Cơ ở Tý Ngọ, Cự Môn Linh Tinh ở Sửu")
W1E("w1_co_luong_thin_tuat", "十二宫诸星得地富贵论", "辰戍机梁非小补", "Cơ Lương Thìn Tuất", "Cơ Lương ở Thìn Tuất 'không phải lợi nhỏ' (trong bài đắc địa phú quý)")
W1E("w1_pha_mao_dau", "十二宫诸星失陷贫贱论", "破军卯酉不为清", "Phá Quân Mão Dậu", "Phá Quân ở Mão Dậu không thanh (trong bài thất hãm bần tiện)")
W1E("w1_tham_hoa_loc_tu_mo", "十二宫诸星失陷贫贱论", "贪狼化禄居四墓，纵然遇吉亦中平", "Tham Lang hóa Lộc ở Tứ mộ", "dù gặp cát tinh cũng chỉ trung bình")
W1E("w1_hop_suu", "十二宫诸星得地合格诀", "丙戍生人福禄饶，正坐平常中局论", "hợp cách Mệnh Sửu", "tuổi '丙戍' phúc lộc nhiều; Nhật Nguyệt chính tọa chỉ là trung cục")
W1E("w1_hop_tuat", "十二宫诸星得地合格诀", "戍宫紫微对冲辰，富而不贵有虚名", "hợp cách Mệnh Tuất", "Tử Vi ở Tuất xung Thìn: giàu mà không sang, có hư danh")
W1E("w1_nn_dong_cung_suu_mui", "十二宫诸星得地合格诀", "丑宫立命日月朝", "Nhật Nguyệt Sửu Mùi", "Mệnh Sửu có Nhật Nguyệt chiếu (triều) mới tốt; chính tọa là trung cục")
