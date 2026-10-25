"""Builds engine/data/van_han_rules.json: the vận-palace readings of tvbt/van_han.py (Khảo Luận pp.233-236, Thực Hành pp.115-117)
expressed as DATA (DSL conditions over `vh.*` facts + text templates) instead of if/else code.
The first 28 rules are carried over VERBATIM from the code they replace; tests/test_van_han_rules.py proves their output is identical to
the frozen old implementation on random and real charts. The TH p.115 IX / p.117 6n rules below them were added from the page images
(2026-10-24)."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "engine" / "data" / "van_han_rules.json"
SRC, SRC_TH = "SRC", "SRC_TH"          # resolved to the citation strings in van_han.py
TPVT = ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"]
SPT = ["Thất Sát", "Phá Quân", "Tham Lang"]
CNDL = ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"]
NDCC = ["Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"]
HOA3 = ["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"]


def f(n, op="eq", v=True):
    return {"fact": f"vh.{n}", "operator": op, "value": v}


def any_(n, vs):
    return f(n, "contains_any", vs)


def all_(n, vs):
    return f(n, "contains_all", vs)


def has(n, v):
    return f(n, "contains", v)


def R(id, when, text, src=SRC, tails=None, han=None):
    d = {"id": id, "src": src, "when": when, "text": text}
    if tails:
        d["tails"] = tails
    if han:
        d["han"] = han          # "tieu": the page names the tiểu hạn only; "trung_phung": đại and tiểu hạn on this one palace
    return d


DHH = any_("v_stars", ["Đào Hoa", "Hồng Loan", "Thiên Hỷ"])
RULES = [
    R("VH_TPVT_SAT", {"all": [any_("m_major", TPVT), f("sat_in_n", "gte", 1)]},
      "Mệnh có Tử Phủ Vũ Tướng mà cung vận có {sat_in}: theo sách đây lại là dịp đi lên."),
    R("VH_TPVT_CNDL", {"all": [any_("m_major", TPVT), {"any": [any_("v_major", CNDL), any_("v_major", ["Tử Vi", "Thiên Phủ"])]}]},
      "Mệnh có Tử Phủ Vũ Tướng gặp cung vận có Cơ Nguyệt Đồng Lương hoặc Tử Phủ: theo sách là thế đi xuống."),
    R("VH_VCD_SPT", {"all": [f("m_no_major"), any_("v_major", SPT)]},
      "Mệnh vô chính diệu gặp cung vận có Sát Phá Tham: theo sách là dịp đi lên, như người thất nghiệp lâu ngày có việc thực tế."),
    R("VH_TUAN_TRIET", {"any": [{"all": [f("m_tuan"), f("v_triet")]}, {"all": [f("m_triet"), f("v_tuan")]}]},
      "Mệnh bị Tuần mà vận có Triệt (hoặc ngược lại): theo sách như được tháo cũi xổ lồng."),
    R("VH_NN_DAO_HONG", {"all": [all_("m_major", ["Thái Dương", "Thái Âm"]), DHH]},
      "Mệnh có Nhật Nguyệt cần vận có Đào, Hồng, Hỷ mới khá được phần nào: cung vận này có."),
    R("VH_NN_KINH_DA", {"all": [all_("m_major", ["Thái Dương", "Thái Âm"]), {"not": DHH}, any_("sat_in", ["Kình Dương", "Đà La"])]},
      "Mệnh có Nhật Nguyệt mà vận gặp Kình, Đà thì theo sách càng tồi hơn."),
    R("VH_CU_NHAT_SPT", {"all": [all_("m_major", ["Cự Môn", "Thái Dương"]), any_("v_major", SPT)]},
      "Mệnh có Cự Nhật cần vận có Sát Phá Tham mới là dịp làm nên sự nghiệp lớn: cung vận này có."),
    R("VH_CNDL_TOT", {"all": [any_("m_major", CNDL), f("good_n", "gte", 1)]},
      "Mệnh có Cơ Nguyệt Đồng Lương cần vận có Xương Khúc, Khoa Quyền Lộc thì có địa vị, tài lộc: cung vận có {good}."),
    R("VH_CNDL_XAU", {"all": [any_("m_major", CNDL), any_("v_stars", ["Kình Dương", "Đà La", "Địa Không", "Địa Kiếp"])]},
      "Mệnh có Cơ Nguyệt Đồng Lương mà vận gặp Kình, Đà, Không, Kiếp: theo sách dễ trắng tay."),
    R("VH_VT_TP", {"all": [all_("m_major", ["Vũ Khúc", "Thiên Tướng"]), any_("v_major", ["Tử Vi", "Thiên Phủ"])]},
      "Mệnh có Vũ Tướng gặp vận Tử Phủ: theo sách là một bước lên quan."),
    R("VH_VT_SPT", {"all": [all_("m_major", ["Vũ Khúc", "Thiên Tướng"]), any_("v_major", SPT)]},
      "Mệnh có Vũ Tướng gặp vận Sát Phá Tham: theo sách là giàu sang chóng vánh."),
    R("VH_THAI_TUE", has("v_stars", "Thái Tuế"),
      "Vận đến cung có Thái Tuế: sách xem là một trong ba vận lớn về công danh, mừng nhiều hơn lo",
      tails=[{"when": any_("v_stars", ["Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]),
              "text": "gặp Xương Khúc hoặc Khôi Việt thì tài lộc công danh rực rỡ"},
             {"when": {"any": [has("v_stars", "Đà La"), f("ky_here_star")]}, "text": "gặp Đà, Kỵ thì dễ vướng thị phi, kiện tụng"}]),
    R("VH_QUAN_PHU", has("v_stars", "Quan Phù"), "Vận đến cung có Quan Phù: sách xem là vận để mong công danh",
      tails=[{"when": any_("v_stars", ["Văn Xương", "Văn Khúc"]), "text": "gặp Xương Khúc thì công danh đến dễ"},
             {"when": {"all": [has("v_major", "Liêm Trinh"), f("ky_here")]}, "text": "gặp Liêm trinh hóa Kỵ thì dễ kiện tụng"}]),
    R("VH_BACH_HO", has("v_stars", "Bạch Hổ"), "Vận đến cung có Bạch Hổ: sách xem là vận cần can đảm dám làm dám chịu mới giàu sang uy quyền",
      tails=[{"when": any_("v_stars", ["Tấu Thư", "Phi Liêm"]), "text": "gặp Tấu Thư, Phi Liêm thì giàu sang"}]),
]
SAT_POS = [("Thất Sát", ["Dần", "Thân"], "muôn sự dễ thành"), ("Thất Sát", ["Mão", "Dậu"], "muôn sự dở dang"),
           ("Phá Quân", ["Tý", "Ngọ"], "bạn bè đông đủ"), ("Phá Quân", ["Mão", "Dậu"], "cô đơn, lẻ bóng"),
           ("Tham Lang", ["Thìn", "Tuất", "Mùi"], "giàu sang hiển hách"), ("Tham Lang", ["Tý", "Ngọ", "Mão", "Dậu"], "hao tài, phóng túng")]
for i, (star, brs, txt) in enumerate(SAT_POS):
    RULES.append(R(f"VH_POS_{i + 1}", {"all": [has("v_major", star), f("v_branch", "in", brs)]},
                   f"Vận có {star} ở " + "{v_branch}" + f": theo sách {txt}."))

RULES += [
    R("TH_TPVT_LOC_TA_HUU", {"all": [any_("v_major", TPVT), f("loc"), f("ta_huu")]},
      "Cung vận có Tử Phủ Vũ Tướng gặp Lộc và Tả Hữu: theo sách là dịp có thể phát giàu lớn.", SRC_TH),
    R("TH_NDCC_HOA3", {"all": [any_("v_major", NDCC), any_("v_hoa", HOA3), f("khoi_viet"), f("ta_huu")]},
      "Cung vận có Nguyệt Đồng Cơ Cự gặp Khoa Quyền Lộc, Khôi Việt, Tả Hữu: theo sách là dịp thăng quan hoặc đăng khoa.", SRC_TH),
    R("TH_CU_NHAT_SONG_LOC", {"all": [all_("v_major", ["Cự Môn", "Thái Dương"]), has("v_stars", "Lộc Tồn"), has("v_hoa", "Hóa Lộc"), f("ta_huu")]},
      "Cung vận có Cự Nhật gặp song Lộc và Tả Hữu: theo sách là dịp phát mạnh về buôn bán.", SRC_TH),
    R("TH_CNDL_TAM_HOA", {"all": [any_("v_major", CNDL), f("xk"), f("dao_hong"), f("hoa3_n", "gte", 3)]},
      "Cung vận có Cơ Nguyệt Đồng Lương gặp Xương Khúc, Hồng Đào và Tam Hóa: theo sách là dịp phát công danh và giàu có.", SRC_TH),
    R("TH_SPLT_KINH_DOANH", {"all": [any_("v_major", SPT + ["Liêm Trinh"]), f("ta_huu"), any_("v_hoa", ["Hóa Quyền", "Hóa Lộc"]), f("khoi_viet")]},
      "Cung vận có Sát Phá Liêm Tham gặp Tả Hữu, Quyền hoặc Lộc, Khôi Việt: theo sách là dịp phát về kinh doanh.", SRC_TH),
    R("TH_DAO_HONG_KHOA_QUYEN", {"all": [{"any": [f("khoi_viet"), f("xk")]}, any_("v_hoa", ["Hóa Khoa", "Hóa Quyền"]), f("dao_hong")]},
      "Cung vận có Đào, Hồng, Xương Khúc hoặc Khôi Việt cùng Khoa, Quyền: theo sách là điều kiện để đăng khoa hay thăng chức.", SRC_TH),
    R("TH_TPVT_KHONG_KIEP_KY", {"all": [any_("v_major", TPVT), any_("v_stars", ["Địa Không", "Địa Kiếp"]), has("v_hoa", "Hóa Kỵ")]},
      "Cung vận có Tử Phủ Vũ Tướng gặp Không hoặc Kiếp và Hóa Kỵ: theo sách là thế bất lợi, dễ bị giáng chức hay hao tài.", SRC_TH),
    R("TH_NDCC_KHONG_KIEP", {"all": [any_("v_major", NDCC), any_("v_stars", ["Địa Không", "Địa Kiếp"]),
                                     {"any": [has("v_stars", "Thái Tuế"), has("v_hoa", "Hóa Kỵ")]}]},
      "Cung vận có Nguyệt Đồng Cơ Cự gặp Không hoặc Kiếp cùng Thái Tuế hoặc Kỵ: theo sách dễ vướng kiện cáo hay giáng chức.", SRC_TH),
]
# TH p.115 IX.6, 9, 10 and p.117 6n (image-checked 2026-10-24). 'Lưỡng hạn' is read as the đại hạn and the tiểu hạn alike (IX.7-8 say
# 'trùng phùng' when both must sit on one palace), so each rule reads one vận palace. 'gặp' with no position = in the vận palace itself;
# 'hội' = in its tam phương tứ chính (Tang Môn and Bạch Hổ always face each other, so they can never share one palace).
# IX.9 and 6n are told as 'theo sách rất bất lợi', without the book's 'tai họa' / 'tai ương' (owner's decision 2026-10-24).
# IX.5 cannot be met on one palace (Cự Môn never stands in the tam phương of Sát / Phá / Tham). See docs/INDICES-TH115-117.md.
TU_MO = ["Thìn", "Tuất", "Sửu", "Mùi"]
KD = any_("v_stars", ["Kình Dương", "Đà La"])
PHU_XK = any_("v_stars", ["Tử Vi", "Thiên Phủ", "Văn Xương", "Văn Khúc"])
RULES += [
    R("TH_IX6_GIAP_THUONG_SU", {"all": [f("year_stem", "eq", "Giáp"), f("v_branch", "eq", "Dần"), any_("v_stars", ["Thiên Thương", "Thiên Sứ"])]},
      "Tuổi Giáp, cung vận ở Dần có {thuong_su}: theo sách rất kỵ.", SRC_TH),
    R("TH_IX6_CANH_THUONG_SU", {"all": [f("year_stem", "eq", "Canh"), f("v_branch", "eq", "Thân"), any_("v_stars", ["Thiên Thương", "Thiên Sứ"])]},
      "Tuổi Canh, cung vận ở Thân có {thuong_su}: theo sách rất kỵ.", SRC_TH),
    R("TH_IX9_THAN_THUONG", {"all": [f("year_branch", "eq", "Thân"), has("v_stars", "Thiên Thương")]},
      "Tuổi Thân, cung vận có Thiên Thương: theo sách rất bất lợi.", SRC_TH),
    R("TH_IX10_TU_MO_KINH_DA", {"all": [f("year_branch", "in", TU_MO), KD, {"not": PHU_XK}]},
      "Tuổi {year_branch}, cung vận có {kinh_da}: theo sách không hề gì.", SRC_TH),
    R("TH_IX10_TU_MO_KINH_DA_PHAT", {"all": [f("year_branch", "in", TU_MO), KD, PHU_XK]},
      "Tuổi {year_branch}, cung vận có {kinh_da} cùng Tử, Phủ, Xương hoặc Khúc: theo sách trái lại là hoạnh phát.", SRC_TH),
    R("TH_6N_SPT_TANG_HO", {"all": [any_("v_major", SPT),
                                    all_("tp_stars", ["Tang Môn", "Bạch Hổ", "Thiên Khốc", "Điếu Khách", "Đà La", "Thiên Thương"])]},
      "Cung vận có Sát Phá Tham, tam phương hội Tang Môn, Bạch Hổ, Thiên Khốc, Điếu Khách, Đà La, Thiên Thương: theo sách rất bất lợi.",
      SRC_TH),
]

# ---- the grave rules of TH pp.115-117 (death, prison, injury, illness, burns, drowning, mourning), added on the owner's decision of
# 2026-10-24: every one is told only as "theo sách rất bất lợi", never with the book's event. The star a sentence is about (its chính tinh,
# or the star it opens with) stands in the vận palace; the stars it "gặp / ngộ / gia" stand there too, unless two of the groups the book
# joins can never share one palace (Tang Môn / Bạch Hổ with Điếu Khách or Thái Tuế, the Hao with Phục Binh): then they are read in the
# tam phương tứ chính. Within a pair the book names together (Kình Đà, Không Kiếp, Cô Quả, Tang Hổ, song Hao, Khốc Hư, Hỏa Linh, Thương
# Sứ) one star is enough, as in TH_TPVT_KHONG_KIEP_KY. "Kỵ" = Hóa Kỵ; "Tuế" = Thái Tuế; "Diêu" = Thiên Riêu; "Hình" = Thiên Hình;
# "Sát" beside Phục Binh = Kiếp Sát; "Nhị tam Không" = two or more of Địa Không, Thiên Không, Tuần, Triệt.
BAD = ": theo sách rất bất lợi."
KY, KY_T = has("v_hoa", "Hóa Kỵ"), has("tp_hoa", "Hóa Kỵ")
P = lambda *xs: any_("v_stars", list(xs))       # noqa: E731
T = lambda *xs: any_("tp_stars", list(xs))      # noqa: E731
NN = all_("v_major", ["Thái Dương", "Thái Âm"])
PHU_TUONG = any_("v_major", ["Thiên Phủ", "Thiên Tướng"])
SPLT = any_("v_major", SPT + ["Liêm Trinh"])
KHONG_KIEP = P("Địa Không", "Địa Kiếp")
HAO = P("Đại Hao", "Tiểu Hao")
TANG_HO = P("Tang Môn", "Bạch Hổ")
KHOC_HU = P("Thiên Khốc", "Thiên Hư")
CO_QUA = P("Cô Thần", "Quả Tú")
RULES += [
    R("TH_IX7_TRUNG_PHUNG_TY", {"all": [f("v_branch", "eq", "Tý"), T("Thiên Thương", "Thiên Sứ"), T("Kình Dương", "Đà La"), T("Thái Tuế")]},
      "Đại hạn và tiểu hạn cùng ở cung Tý, tam phương có Thiên Thương hoặc Thiên Sứ, Kình hoặc Đà, Thái Tuế" + BAD, SRC_TH, han="trung_phung"),
    R("TH_IX8_THUONG_SU_TUE", {"all": [{"any": [{"all": [P("Thiên Thương"), f("v_branch", "in", ["Tý", "Thìn", "Mão", "Ngọ", "Mùi"])]},
                                                 {"all": [P("Thiên Sứ"), f("v_branch", "in", ["Dần", "Thân", "Tỵ", "Hợi"])]}]}, T("Thái Tuế")]},
      "Cung vận ở {v_branch} có {thuong_su}, tam phương có Thái Tuế" + BAD, SRC_TH),
    R("TH_IX11_SAT_HAM_HINH_HO", {"all": [has("v_ham", "Thất Sát"), T("Thiên Hình"), T("Bạch Hổ"), T("Quan Phủ")]},
      "Cung vận có Thất Sát hãm, tam phương có Thiên Hình, Bạch Hổ, Quan Phủ" + BAD, SRC_TH),
    R("TH_DC5_PHOI", {"all": [f("v_name", "eq", "Phu Thê"), {"any": [
        {"all": [CO_QUA, KHONG_KIEP]},
        {"all": [P("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp"), {"any": [f("v_tuan"), f("v_triet")]}]},
        {"all": [TANG_HO, HAO]},
        {"all": [P("Thiên Hình", "Thiên Riêu", "Thiên Không"), KY]},
        {"all": [P("Thất Sát", "Phá Toái"), KHOC_HU]},
        {"all": [P("Linh Tinh", "Hỏa Tinh"), P("Kình Dương", "Đà La"), KHONG_KIEP]},
        {"all": [has("v_major", "Cự Môn"), P("Linh Tinh", "Hỏa Tinh")]}]}]},
      "Cung vận là Phu Thê, có một cách cung Phối dang dở của sách" + BAD, SRC_TH),
    R("TH_6A_CNDL_SAT", {"all": [{"any": [any_("v_major", CNDL), all_("v_major", ["Cự Môn", "Thái Dương"])]},
                                 P("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Phá Toái", "Kiếp Sát")]},
      "Cung vận có Cơ Nguyệt Đồng Lương hoặc Cự Nhật, gặp Kình, Đà, Không, Kiếp, Phá Toái hoặc Kiếp Sát" + BAD, SRC_TH),
    R("TH_6B_SPLT_KHONG", {"all": [SPLT, {"any": [
        f("khong_n", "gte", 2),
        {"all": [P("Linh Tinh", "Hỏa Tinh"), P("Kình Dương"), KY]},
        {"all": [T("Đại Hao", "Tiểu Hao"), T("Thiên Hình"), T("Kiếp Sát"), T("Phục Binh"), T("Tang Môn", "Bạch Hổ")]}]}]},
      "Cung vận có Sát Phá Liêm Tham gặp Nhị tam Không, hoặc Linh Hỏa Kình Kỵ, hoặc Hao, Hình, Kiếp Sát, Phục Binh, Tang Hổ" + BAD, SRC_TH),
    R("TH_6D_CU_CO_DONG_LUONG", {"all": [{"any": [all_("v_major", ["Cự Môn", "Thiên Cơ"]), all_("v_major", ["Thiên Đồng", "Thiên Lương"])]},
                                         {"any": [P("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Đại Hao", "Tiểu Hao", "Phá Toái"), KY]}]},
      "Cung vận có Cự Cơ hoặc Đồng Lương, gặp Kình, Đà, Không, Kiếp, Hao, Phá Toái hoặc Kỵ" + BAD, SRC_TH),
    R("TH_6F_NHAT_NGUYET", {"all": [NN, {"any": [{"all": [KHONG_KIEP, P("Thiên Riêu")]}, {"all": [P("Linh Tinh", "Hỏa Tinh"), CO_QUA]}]}]},
      "Cung vận có Nhật Nguyệt gặp Không Kiếp và Thiên Riêu, hoặc Linh Hỏa và Cô Quả" + BAD, SRC_TH),
    R("TH_6G_PHA_LIEM_THAM", {"all": [any_("v_major", ["Phá Quân", "Liêm Trinh", "Tham Lang"]), P("Thiên Riêu"), KY, P("Mộc Dục")]},
      "Cung vận có Phá Liêm Tham gặp Thiên Riêu, Hóa Kỵ, Mộc Dục" + BAD, SRC_TH),
    R("TH_6H_THIEN_DONG", {"all": [has("v_major", "Thiên Đồng"), {"any": [
        {"all": [P("Kình Dương"), KY]},
        {"all": [P("Mộc Dục"), P("Hỏa Tinh"), KHONG_KIEP]},
        {"all": [has("v_major", "Cự Môn"), KY, P("Thái Tuế"), P("Đà La"), KHONG_KIEP]}]}]},
      "Cung vận có Thiên Đồng gặp Kình Kỵ, hoặc Mộc Dục Hỏa Không Kiếp, hoặc Cự Kỵ Tuế Đà Không Kiếp" + BAD, SRC_TH),
    R("TH_6I_TANG_HOA_LINH", {"all": [P("Tang Môn"), P("Hỏa Tinh"), P("Linh Tinh")]},
      "Tiểu hạn có Tang Môn, Hỏa Tinh, Linh Tinh" + BAD, SRC_TH, han="tieu"),
    R("TH_6J_CO_LUONG_THIN_TUAT", {"all": [all_("v_major", ["Thiên Cơ", "Thiên Lương"]), f("v_branch", "in", ["Thìn", "Tuất"]),
                                           P("Tang Môn", "Điếu Khách", "Thái Tuế"), KHOC_HU]},
      "Tiểu hạn ở Cơ Lương tại {v_branch} gặp Tang, Điếu hoặc Tuế cùng Khốc hoặc Hư" + BAD, SRC_TH, han="tieu"),
    R("TH_6K_SPLT_TANG_HO", {"any": [
        {"all": [SPLT, T("Tang Môn", "Bạch Hổ"), T("Kình Dương", "Đà La"), T("Điếu Khách")]},
        {"all": [has("v_major", "Tham Lang"), f("v_branch", "in", ["Thìn", "Tuất"]), T("Bạch Hổ"), T("Thiên Riêu"), T("Thái Tuế")]}]},
      "Cung vận có Sát Phá Liêm Tham, tam phương hội Tang Hổ, Kình Đà, Điếu Khách; hoặc Tham Lang ở Thìn Tuất hội Hổ, Riêu, Tuế" + BAD, SRC_TH),
    R("TH_6L_KINH_KHONG_PHUC_BINH", {"all": [P("Kình Dương", "Địa Không", "Địa Kiếp"), P("Quan Phù", "Tử Phù", "Trực Phù"), P("Phục Binh")]},
      "Cung vận có Kình, Không hoặc Kiếp cùng Quan Phù, Tử Phù hoặc Trực Phù và Phục Binh" + BAD, SRC_TH),
    R("TH_6M_THAM_LIEM_VU", {"all": [{"any": [{"all": [all_("v_major", ["Tham Lang", "Liêm Trinh"]), f("v_branch", "in", ["Tỵ", "Hợi"])]},
                                               {"all": [all_("v_major", ["Tham Lang", "Vũ Khúc"]), f("v_branch", "in", ["Dần", "Thân"])]}]},
                                     KY, P("Đà La"), KHONG_KIEP]},
      "Cung vận có Tham Liêm ở Tỵ Hợi hoặc Tham Vũ ở Dần Thân, gặp Kỵ, Đà, Không hoặc Kiếp" + BAD, SRC_TH),
    R("TH_6O_THAM_LIEM_KY_KIEP", {"any": [
        {"all": [all_("v_major", ["Tham Lang", "Liêm Trinh"]), P("Kình Dương", "Đà La"), P("Hỏa Tinh", "Linh Tinh")]},
        {"all": [KY, P("Địa Kiếp"), P("Thiên Không")]}]},
      "Cung vận có Tham Liêm gặp Kình Đà và Hỏa Linh, hoặc có Kỵ, Địa Kiếp, Thiên Không" + BAD, SRC_TH),
    R("TH_7A_NHAT_NGUYET_DA", {"all": [NN, P("Đà La"), P("Thiên Không"), KY]},
      "Cung vận có Nhật Nguyệt ngộ Đà La, Thiên Không, Hóa Kỵ" + BAD, SRC_TH),
    R("TH_7B_PHU_TUONG_CO_QUA", {"all": [PHU_TUONG, CO_QUA, P("Thiên Không"), P("Kiếp Sát")]},
      "Cung vận có Phủ hoặc Tướng ngộ Cô Quả, Thiên Không, Kiếp Sát" + BAD, SRC_TH),
    R("TH_7C_PHU_TUONG_TANG_HO", {"all": [PHU_TUONG, TANG_HO, KHOC_HU, HAO]},
      "Cung vận có Phủ hoặc Tướng ngộ Tang Hổ, Khốc Hư, Hao" + BAD, SRC_TH),
    R("TH_7D_SPLT_HAO_TANG", {"all": [SPLT, {"any": [{"all": [HAO, TANG_HO]}, {"all": [P("Kình Dương", "Đà La"), KHONG_KIEP, KHOC_HU]}]}]},
      "Cung vận có Sát Phá Liêm Tham ngộ Hao và Tang Hổ, hoặc Kình Đà, Không Kiếp, Khốc Hư" + BAD, SRC_TH),
    R("TH_7E_CO_QUA_DAO_HONG", {"all": [CO_QUA, P("Đào Hoa", "Hồng Loan"), P("Thiên Không"), KY]},
      "Cung vận có Cô Quả, Đào Hồng, Thiên Không, Hóa Kỵ" + BAD, SRC_TH),
    R("TH_7F_TPVT_CO_QUA_HAO", {"all": [any_("v_major", TPVT), CO_QUA, HAO]},
      "Cung vận có Tử Phủ Vũ Tướng ngộ Cô Quả và Hao" + BAD, SRC_TH),
    R("TH_7G_KHONG_TANG_HO", {"all": [f("khong_n", "gte", 2), T("Tang Môn", "Bạch Hổ"), T("Điếu Khách", "Thái Tuế")]},
      "Cung vận có Nhị tam Không, tam phương ngộ Tang Hổ, Điếu Tuế" + BAD, SRC_TH),
    R("TH_7H_HINH_KINH_TANG", {"all": [P("Thiên Hình", "Thiên Riêu"), P("Kình Dương", "Đà La"), KHONG_KIEP, TANG_HO]},
      "Cung vận có Hình hoặc Riêu, Kình hoặc Đà, Không hoặc Kiếp, Tang hoặc Hổ" + BAD, SRC_TH),
    R("TH_7I_CNDL_TANG_HO", {"all": [any_("v_major", CNDL), TANG_HO]},
      "Cung vận có Cơ Nguyệt Đồng Lương ngộ Tang Hổ" + BAD, SRC_TH),
]


if __name__ == "__main__":
    OUT.write_text(json.dumps({"note": "Vận-palace readings as data (Khảo Luận pp.233-236, Thực Hành pp.115-117); built by tools/build_van_han_rules.py.",
                               "rules": RULES}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(len(RULES), "rules")
