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


def R(id, when, text, src=SRC, tails=None):
    d = {"id": id, "src": src, "when": when, "text": text}
    if tails:
        d["tails"] = tails
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
# The rules that name death, prison, injury, illness, burns, drowning or mourning (IX.7, 8, 11; 6a, b, d, f-m, o; 7a-i) wait for the owner's
# content review; IX.5 cannot be met on one palace (Cự Môn never stands in the tam phương of Sát / Phá / Tham). See docs/INDICES-EVAL.md.
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

if __name__ == "__main__":
    OUT.write_text(json.dumps({"note": "Vận-palace readings as data (Khảo Luận pp.233-236, Thực Hành pp.115-117); built by tools/build_van_han_rules.py.",
                               "rules": RULES}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(len(RULES), "rules")
