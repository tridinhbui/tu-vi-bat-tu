"""Generates data/pack_thien_luong.json: readings of Thiên Lương, Tử Vi Nghiệm Lý Toàn Thư (school 'thien_luong'), paraphrased.

Edition: the forum transcription (hội viên Tử Vi Lý Số, 2007) published at online.fliphtml5.com/dqkgf/htsb; page numbers are the PRINTED
pages, which the transcription carries inline (a number before the text of its page). A 21-page scan of the opening chapters
(tuviglobal.com) exists; the chapters used here are beyond it, so they are cited from the transcription and say so.

Thiên Lương reasons in two camps of chính tinh: Cơ Nguyệt Đồng Lương Cự Nhật ("A") and Tử Phủ Vũ Tướng Sát Phá Liêm Tham ("B"). A palace
is read 'đắc địa' when every chính tinh in it is miếu/vượng/đắc, 'hãm' when any of them is hãm (bình is neither, and an empty palace
is neither): the system's reading of the book's 'đắc địa / hãm địa', stated in each description.
    .venv/bin/python tools/build_thien_luong_pack.py"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "engine" / "data"
SRC = "SRC_TVNL_TOAN_THU"
A = ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương", "Cự Môn", "Thái Dương"]
B = ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng", "Thất Sát", "Phá Quân", "Tham Lang", "Liêm Trinh"]
MAJORS = A + B
SPT_CU = ["Thất Sát", "Phá Quân", "Tham Lang", "Cự Môn"]


def fact(f, op, v, pal=None):
    """A leaf on the subject palace, or (pal) on another palace through `ref`."""
    return {"ref": {"palace": pal, "fact": f}, "operator": op, "value": v} if pal else {"fact": f, "operator": op, "value": v}


def name(p):
    return {"fact": "palace.name", "value": p}


def group_is(camp, pal=None):
    """The palace has chính tinh, all of them in `camp`."""
    other = B if camp is A else A
    return {"all": [fact("palace.has_no_major", "eq", False, pal), {"not": fact("palace.own_major_stars", "contains_any", other, pal)}]}


def bright(pal=None):
    """Every chính tinh of the palace is miếu / vượng / đắc."""
    return {"all": [fact("palace.has_no_major", "eq", False, pal),
                    {"not": {"any": [{"all": [fact("palace.own_major_stars", "contains", s, pal), fact(f"palace.dignity.{s}", "in", ["bình", "hãm"], pal)]} for s in MAJORS]}}]}


def dim(pal=None):
    """At least one chính tinh of the palace is hãm."""
    return {"any": [{"all": [fact("palace.own_major_stars", "contains", s, pal), fact(f"palace.dignity.{s}", "eq", "hãm", pal)]} for s in MAJORS]}


def both(state, pals):
    return {"all": [state(p) for p in pals]}


rules, claims = [], {}


SRC_NL = "SRC_TVNL_1974"
NL_BOOK = "Thiên Lương, Tử Vi Nghiệm Lý (1974, tái bản lần thứ nhất), bản scan Tủ sách HELEN, số trang theo chân trang HELEN"


def rule(rid, palace, cond, claim, vi, page, effect="support", status="verified", note="", nl=False):
    book, code, src = (NL_BOOK, "NL", SRC_NL) if nl else ("Thiên Lương, Tử Vi Nghiệm Lý Toàn Thư (bản gõ 2007)", "TL", SRC)
    rules.append({"id": f"TV_{code}_{rid}" if nl else f"TV_TL_{rid}", "system": "tu_vi", "schoolId": "thien_luong", "category": "tl_palace",
                  "description": f"{book}, paraphrased, cung {palace}: {vi} [{code} p.{page}]{('; ' + note) if note else ''}",
                  "conditions": {"all": [name(palace), cond]},
                  "consequences": [{"kind": "finding", "claim": claim, "effect": effect, "scope": "natal"}],
                  "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": [src], "reviewStatus": status, "version": "0.1.0", "subject": "palace"})
    claims[claim] = ("hạn chế: " if effect == "limit" else "khuynh hướng ") + vi


# ---- Bào và Nô theo Mệnh (pp.124-125): eight principles, each read at Huynh Đệ (anh em) and at Nô Bộc (bạn bè, người dưới) ----
STATE = "'đắc địa' = mọi chính tinh của cung ở miếu/vượng/đắc, 'hãm' = có chính tinh hãm: cách đọc của hệ thống"
BN = [  # (tag, Mệnh camp, Mệnh state, Bào/Nô state, Huynh Đệ phrase, Nô Bộc phrase, page)
    ("A_SANG_BN_SANG", A, bright, bright, "việc lớn dễ thành nhưng hay bất hòa với anh em", "bạn bè, người dưới trung thành", "124-125"),
    ("A_SANG_BN_HAM", A, bright, dim, "anh em xác xơ, hay oán trách", "người dưới xác xơ, hay oán trách", "125"),
    ("A_HAM_BN_SANG", A, dim, bright, "anh em được việc nhưng hay lấn quyền", "người dưới được việc nhưng hay lấn quyền", "125"),
    ("A_HAM_BN_HAM", A, dim, dim, "anh em phân tán", "người dưới, bạn bè phân tán, dễ phản bội", "125"),
    ("B_SANG_BN_SANG", B, bright, bright, "anh em tận tâm", "người dưới trung thành, dù thành quả chưa vừa ý chủ", "125"),
    ("B_SANG_BN_HAM", B, bright, dim, "anh em bất lực, trông cậy vào mình", "người dưới bất lực, ăn bám", "125"),
    ("B_HAM_BN_SANG", B, dim, bright, "anh em vẫn giúp được việc", "người dưới vẫn giúp công việc tiến hành", "125"),
    ("B_HAM_BN_HAM", B, dim, dim, "anh em phân tán", "bạn bè phần đông vô tài, phân tán", "125"),
]
for tag, camp, ms, bn, hd_vi, nb_vi, page in BN:
    camp_vi = "Cơ Nguyệt Đồng Lương Cự Nhật" if camp is A else "Tử Phủ Vũ Tướng Sát Phá Liêm Tham"
    cond_vi = f"Mệnh {camp_vi} {'đắc địa' if ms is bright else 'hãm'}, Bào và Nô {'đắc địa' if bn is bright else 'hãm'}"
    base = {"all": [group_is(camp, "Mệnh"), ms("Mệnh"), both(bn, ["Huynh Đệ", "Nô Bộc"])]}
    rule(f"BAO_{tag}", "Huynh Đệ", base, f"tl_bao_{tag.lower()}", f"{hd_vi} ({cond_vi})", page,
         effect="support" if "SANG_BN_SANG" in tag and camp is B or tag == "B_HAM_BN_SANG" else "limit", note=STATE)
    rule(f"NO_{tag}", "Nô Bộc", base, f"tl_no_{tag.lower()}", f"{nb_vi} ({cond_vi})", page,
         effect="support" if tag in ("A_SANG_BN_SANG", "B_SANG_BN_SANG", "B_HAM_BN_SANG") else "limit", note=STATE)

# ---- Phụ Mẫu và Tật Ách (pp.127-128) ----
own = lambda *ss: fact("palace.own_major_stars", "contains_all", list(ss))
rule("PHU_MAU_TU_SAT", "Phụ Mẫu", own("Tử Vi", "Thất Sát"), "tl_pm_tu_sat_bat_hoa", "cha mẹ có sự bất hòa (Tử Vi đi với Thất Sát ở Phụ Mẫu)", "127", "limit")
rule("PHU_MAU_TU_PHA", "Phụ Mẫu", own("Tử Vi", "Phá Quân"), "tl_pm_tu_pha_li_khac", "cha mẹ có sự lìa khắc (Tử Vi đi với Phá Quân ở Phụ Mẫu)", "127", "limit")
rule("PHU_MAU_TU_THAM", "Phụ Mẫu", own("Tử Vi", "Tham Lang"), "tl_pm_tu_tham_phan_ly", "cha mẹ phải phân ly (Tử Vi đi với Tham Lang ở Phụ Mẫu)", "127", "limit")
rule("PHU_MAU_CU_MON", "Phụ Mẫu", {"any": [fact("palace.own_major_stars", "contains", "Cự Môn"), fact("palace.rel.trine_majors", "contains", "Cự Môn")]},
     "tl_pm_cu_mon_chang_lanh", "nhiều chuyện chẳng lành với cha mẹ (Cự Môn ở Phụ Mẫu hoặc tam hợp chiếu)", "127", "limit")
rule("PHU_MAU_SPT_CU", "Phụ Mẫu", fact("palace.own_major_stars", "contains_any", ["Thất Sát", "Phá Quân", "Tham Lang", "Cự Môn", "Thái Dương"]),
     "tl_pm_spt_cu_vat_va", "cha mẹ vất vả, chia ly hay náo loạn (Phụ Mẫu có Sát Phá Tham hoặc Cự Nhật)", "128", "limit")
tu_with_spt = {"all": [fact("palace.own_major_stars", "contains", "Tử Vi", "Phụ Mẫu"), fact("palace.own_major_stars", "contains_any", ["Thất Sát", "Phá Quân", "Tham Lang"], "Phụ Mẫu")]}
rule("TAT_ACH_NHE", "Tật Ách", {"any": [tu_with_spt, fact("palace.own_major_stars", "contains_any", ["Thất Sát", "Phá Quân", "Tham Lang", "Cự Môn"], "Phụ Mẫu")]},
     "tl_ta_benh_nhe", "bệnh tật nhẹ, phần nhiều nội thương, dễ gặp thầy thuốc: cha mẹ gánh phần vất vả thay (Phụ Mẫu có Sát Phá Tham hoặc Cự Môn)", "127-128")
gentle_parents = {"all": [fact("palace.own_major_stars", "contains_any", ["Tử Vi", "Thiên Phủ", "Thiên Tướng", "Thiên Đồng", "Thiên Lương"], "Phụ Mẫu"),
                          {"not": fact("palace.own_major_stars", "contains_any", SPT_CU, "Phụ Mẫu")}]}
rule("TAT_ACH_NANG", "Tật Ách", gentle_parents, "tl_ta_benh_nang",
     "dễ gặp tai ách hay bạo bệnh: cha mẹ hiền (Tử Phủ, Tử Tướng, Đồng Lương) không đủ sức chống bộ Sát Phá Tham, Cự Nhật đóng ở Tật Ách", "127", "limit")
rule("TAT_ACH_GIAM", "Tật Ách", {"any": [{"fact": "palace.tuan", "value": True}, {"fact": "palace.triet", "value": True}, {"fact": "palace.has_no_major", "value": True}]},
     "tl_ta_giam_cuong_do", "cường độ tật ách được giảm bớt (Tật Ách có Tuần, Triệt hoặc vô chính diệu)", "128")

# ---- Phụ, Bào, Thê không nên có Sát Phá Tham, Cự Môn (p.130); vị trí người vợ hiền (pp.130-131) ----
spt = fact("palace.own_major_stars", "contains_any", SPT_CU)
rule("PHU_MAU_SPT_CHANG_LANH", "Phụ Mẫu", spt, "tl_pm_spt_chang_lanh", "chuyện chẳng lành với cha mẹ, dù sao đắc hay hãm (Sát Phá Tham hoặc Cự Môn ở Phụ Mẫu)", "130", "limit")
rule("HUYNH_DE_SPT_CHANG_LANH", "Huynh Đệ", spt, "tl_hd_spt_chang_lanh", "chuyện chẳng lành với anh em, dù sao đắc hay hãm (Sát Phá Tham hoặc Cự Môn ở Huynh Đệ)", "130", "limit")
rule("PHU_THE_SPT_CHANG_LANH", "Phu Thê", spt, "tl_pt_spt_chang_lanh", "chuyện chẳng lành trong hôn nhân, dù sao đắc hay hãm (Sát Phá Tham hoặc Cự Môn ở Phu Thê)", "130", "limit")
at = lambda branches: fact("palace.branch", "in", branches)
sole = lambda s: {"all": [own(s), fact("palace.own_major_stars", "eq", [s])]}
GOOD_WIFE = {"any": [
    {"all": [sole("Tử Vi"), at(["Tý", "Ngọ"])]}, {"all": [sole("Thiên Phủ"), at(["Tỵ", "Hợi"])]}, own("Tử Vi", "Thiên Phủ"),
    {"all": [sole("Thiên Lương"), at(["Ngọ"])]}, {"all": [sole("Thiên Đồng"), at(["Mão"])]}, own("Thiên Đồng", "Thiên Lương"),
    {"all": [sole("Thiên Cơ"), at(["Tỵ"])]}, own("Thiên Cơ", "Thiên Lương"),
    {"all": [sole("Thái Âm"), fact("palace.dignity.Thái Âm", "in", ["miếu", "vượng", "đắc"])]},
    {"all": [own("Thiên Đồng", "Thái Âm"), at(["Tý"])]}, {"all": [own("Thiên Cơ", "Thái Âm"), at(["Thân"])]}]}
rule("PHU_THE_VO_HIEN", "Phu Thê", {"all": [{"fact": "chart.gender", "value": "nam"}, GOOD_WIFE]}, "tl_pt_vo_hien_bac_dau",
     "người vợ hiền hậu, vợ chồng chung lưng đến bạc đầu (Phu Thê nam mệnh có Tử Vi Tý Ngọ, Thiên Phủ Tỵ Hợi, Tử Phủ, Lương Ngọ, Đồng Mão, Đồng Lương, Cơ Tỵ, Cơ Lương, Thái Âm đắc, Đồng Âm Tý hoặc Cơ Âm Thân)",
     "130-131", note="sách nói về người vợ; hệ thống chỉ áp cho nam mệnh")
rule("NO_BOC_SPT_DAC_MENH_A", "Nô Bộc", {"all": [fact("palace.own_major_stars", "contains_any", ["Thất Sát", "Phá Quân", "Tham Lang"]), bright(), group_is(A, "Mệnh"), bright("Mệnh")]},
     "tl_no_spt_dac_trung_thanh", "người dưới được việc, không làm xằng phản bội (Nô Bộc có Sát Phá Tham đắc địa, Mệnh Cơ Nguyệt Đồng Lương Cự Nhật đắc địa)", "130", note=STATE)

# ---- Tử Vi Nghiệm Lý (1974), the case essays: two money readings stated as general principles (HELEN pp.67, 83-84, 86) ----
rule("TAI_BACH_KY_LOC_TON", "Tài Bạch", {"all": [{"fact": "chart.year_stem", "value": "Kỷ"}, fact("palace.own_stars", "contains", "Lộc Tồn")]},
     "nl_tb_ky_loc_ton", "có Lộc Tồn mà khó được thụ hưởng: với tuổi Kỷ, sách kể như không có Lộc Tồn (tuổi Kỷ, Lộc Tồn ở Tài Bạch)", "67, 86", "limit", nl=True,
     note="sách nói chung cho tuổi Kỷ; hệ thống chỉ áp khi Lộc Tồn ở Tài Bạch; khác cách đọc phổ thông")
rule("TAI_BACH_PHU_PHUNG_KHONG", "Tài Bạch", {"all": [fact("palace.own_major_stars", "contains", "Thiên Phủ"),
     {"any": [fact("palace.tuan", "eq", True), fact("palace.triet", "eq", True), fact("palace.own_stars", "contains_any", ["Địa Không", "Thiên Không"])]}]},
     "nl_tb_phu_phung_khong", "tiền bạc túng thiếu: Thiên Phủ gặp Không thì kho bị phá (Thiên Phủ ở Tài Bạch gặp Tuần, Triệt, Địa Không hoặc Thiên Không)", "83-84", "limit", nl=True,
     note="lá số mẫu của sách có Thiên Phủ ở Quan Lộc dưới Tuần; hệ thống áp nguyên lý 'Phủ phùng Không' vào Tài Bạch")

# ---- Mệnh vô chính diệu đắc Tam Không (p.232): Thiên Lương does not accept the classical formula ----
th = {r["id"]: r for r in json.loads((D / "pack_thuc_hanh_cach.json").read_text("utf-8"))["rules"]}
vcd = th["TV_TH_CACH_MENH_VCD_TAM_KHONG"]["conditions"]
rules.append({"id": "TV_TL_MENH_VCD_TAM_KHONG_BAC_BO", "system": "tu_vi", "schoolId": "thien_luong", "category": "tl_palace",
              "description": "Thiên Lương, Tử Vi Nghiệm Lý Toàn Thư (bản gõ 2007), paraphrased, cung Mệnh: không nhận công thức 'Mệnh vô chính diệu đắc Tam Không thì phú quý'; đắc Tam Không là trái âm dương nên không thể phú quý như sách cổ nói; điều kiện trùng với câu của Thực Hành [TL p.232]",
              "conditions": vcd, "consequences": [{"kind": "finding", "claim": "tl_menh_vcd_tam_khong_bac_bo", "effect": "limit", "scope": "natal"}],
              "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": [SRC], "reviewStatus": "verified", "version": "0.1.0", "subject": "palace"})
claims["tl_menh_vcd_tam_khong_bac_bo"] = "hạn chế: không thể phú quý chỉ nhờ đắc Tam Không (Thiên Lương không nhận công thức Mệnh vô chính diệu đắc Tam Không)"

json.dump({"sources": [{"id": SRC, "title": "Tử Vi Nghiệm Lý Toàn Thư", "author": "Thiên Lương",
                        "edition": "Bản gõ của hội viên diễn đàn Tử Vi Lý Số (2007), online.fliphtml5.com/dqkgf/htsb (NXB Thời Đại); trang in ghi trong văn bản. Bản scan trích 21 trang đầu: tuviglobal.com",
                        "locator": "pp.124-132, 232", "verified": True,
                        "note": "Học phái Thiên Lương (schoolId thien_luong). Trích dẫn theo trang in mà bản gõ ghi lại; phần này nằm ngoài bản scan nên chưa đối chiếu với ảnh trang."},
                       {"id": SRC_NL, "title": "Tử Vi Nghiệm Lý", "author": "Thiên Lương",
                        "edition": "Tái bản lần thứ nhất, Sài Gòn 1974 (giấy phép 6028/74); bản scan Tủ sách HELEN, phần 02 (TVnghiemly-LyMenhHoc-02.pdf, 80 trang)",
                        "locator": "HELEN pp.38-114 (lá số danh nhân)", "verified": True,
                        "note": "Số trang theo chân trang HELEN (= trang PDF + 35); trang của sách gốc chỉ có ở mục lục. Phần lý thuyết (phần 01) không có trong bản này."}],
           "rules": rules}, open(D / "pack_thien_luong.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8")); cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
print(len(rules), "rules")
