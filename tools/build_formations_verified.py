"""Build engine/data/formations_verified.json: the ten cách cục of engine/data/experimental/formations_experimental.json re-defined from
the book pages (owner review item 13, plan W4 data part). Every kept condition carries a quote that is on its page of the PDF
(book_text.quote_on_page); TH pages scramble line order, so a TH quote is a contiguous fragment of the text layer and `image` holds the
sentence as read on the page image. Draft conditions with no page are listed in `dropped` with the reason.

    python tools/build_formations_verified.py          # writes the file, then re-checks every quote (needs the PDFs)

Layout of the output:
  formations  Formation dicts in the schema of engine/tvbt/knowledge/formation.py (nothing else, so load_formations reads them);
              reviewStatus 'verified' (core and every kept condition paged) or 'disputed' (the books disagree on the core).
  evidence    per formation: core / effect quotes, `core_alone` (what the books call the bare core: 'thanh' when a book lists the core
              itself as a quý cách, 'hinh_thuc' when a book says it needs more), per-condition sources with `scope` and `reading`, variants.
  dropped     every draft condition not kept, with the reason (and the page that shows why, when there is one).
  rejected    formations with no page for the core (none in this version).
scope: 'cach' = the book says it of this cách; 'cach_ghep' = a book-named cách made of this one plus the extra condition."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import book_text  # noqa: E402

OUT = ROOT / "engine" / "data" / "formations_verified.json"
DRAFT = ROOT / "engine" / "data" / "experimental" / "formations_experimental.json"
BOOK_ID = {"KL": "SRC_KHAO_LUAN", "TH": "SRC_THUC_HANH", "TT": "SRC_TOAN_THU"}

SAT6 = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]
TAM_HOA = ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]


def q(book: str, page: int, quote: str, image: str | None = None) -> dict:
    d = {"book": book, "page": page, "quote": quote}
    if image:
        d["image"] = image
    return d


def fact(name: str, op: str, value) -> dict:
    return {"fact": name, "operator": op, "value": value}


def ev(id_: str, label: str, when: dict, rescues: list[str] | None = None) -> dict:
    d = {"id": id_, "label": label, "when": when}
    if rescues:
        d["rescues"] = rescues
    return d


# ---------------------------------------------------------------- TH pp.76-77: thượng cách / hạ cách of the chính tinh groups

TH76_THUONG = q("TH", 76, "ắc địa hội Tả, Hữu, Xương Khúc, Khôi Việt, Long Phượng, Hồng Đào, Tam Hóa, phát đến",
                "2. Thượng cách: có những cách sau đây đóng Mệnh Thân: Tử, Phủ, Vũ, Tướng, Cơ Nguyệt, Đồng, Lương, Sát, Phá, Liêm, Tham. "
                "Cự, Nhật, Nhật, Nguyệt đồng cung. Tất cả những cách này cần được nhập miếu hay vượng địa, đắc địa hội Tả, Hữu, Xương Khúc, "
                "Khôi Việt, Long Phượng, Hồng Đào, Tam Hóa, phát đến Tam công.")
TH76_LIST = q("TH", 76, "2. Thượng cách: có những cách sau đây đóng Mệnh Thân:")
TH76_SANG = q("TH", 76, "Tất cả những cách này cần được nhập miếu hay v", TH76_THUONG["image"])
TH77_HA = q("TH", 77, "Hạ cách: Có những cách chính tinh như trên, nhưng không gặp được cát tinh hội đủ b",
            "4. Hạ cách: Có những cách chính tinh như trên, nhưng không gặp được cát tinh hội đủ bộ, mà lại gặp Hung tinh và sát tinh đóng. "
            "Ví dụ: Sát Phá Liêm Tham hội Vũ, Kình Đà, Thiên địa Không sát, Song Hao, Hóa Kỵ. Tất cả chính tinh cùng hung tinh sát tinh "
            "nhiều ở vào nơi hãm địa. Gặp phải cách ấy thì thật suốt đời lao khổ, chịu tật nguyền, hoặc lang thang lo miếng ăn từng bữa.")
TH77_HA_DONG = q("TH", 77, "Hung tinh và sát tinh đóng", TH77_HA["image"])
TH77_VI_DU = q("TH", 77, "Sát Phá Liêm Tham hội Vũ, Kình Đà, Thiên địa Kho", TH77_HA["image"])
TH77_HA_EFFECT = q("TH", 77, "phải cách ấy thì thật suốt đời lao khổ, chịu tật nguyền", TH77_HA["image"])

PAIRS = [  # (id, label, expr): "cát tinh hội đủ bộ" = the pair complete in the tam phương tứ chính
    ("ta_huu_hoi", "Tả Phụ, Hữu Bật hội đủ bộ trong tam phương", fact("palace.rel.tp_stars", "contains_all", ["Tả Phụ", "Hữu Bật"])),
    ("xuong_khuc_hoi", "Văn Xương, Văn Khúc hội đủ bộ trong tam phương", fact("palace.rel.tp_stars", "contains_all", ["Văn Xương", "Văn Khúc"])),
    ("khoi_viet_hoi", "Thiên Khôi, Thiên Việt hội đủ bộ trong tam phương", fact("palace.rel.tp_stars", "contains_all", ["Thiên Khôi", "Thiên Việt"])),
    ("long_phuong_hoi", "Long Trì, Phượng Các hội đủ bộ trong tam phương", fact("palace.rel.tp_stars", "contains_all", ["Long Trì", "Phượng Các"])),
    ("hong_dao_hoi", "Hồng Loan, Đào Hoa hội đủ bộ trong tam phương", fact("palace.rel.tp_stars", "contains_all", ["Hồng Loan", "Đào Hoa"])),
    ("tam_hoa_hoi", "Hóa Lộc, Hóa Quyền, Hóa Khoa cùng hội trong tam phương (Tam Hóa)", fact("palace.rel.tp_hoa", "contains_all", TAM_HOA)),
]
PAIR_READING = ("TH p.76 kể các bộ cát tinh; TH p.77 nói hạ cách là 'không gặp được cát tinh hội đủ bộ', nên mỗi bộ chỉ tính khi đủ cả "
                "hai sao (Tam Hóa: đủ ba) trong tam phương tứ chính. Ngưỡng thành cách thế mạnh = hai bộ là quy ước của hệ thống.")
HUNG_SAT_SELF = [fact("palace.rel.self_stars", "contains", s) for s in SAT6 + ["Đại Hao", "Tiểu Hao"]] + [fact("palace.rel.self_hoa", "contains", "Hóa Kỵ")]
HA_CACH = ev("ha_cach", "hạ cách: không bộ cát tinh nào hội đủ (Tả Hữu, Xương Khúc, Khôi Việt, Long Phượng, Hồng Đào, Tam Hóa) mà Mệnh có "
             "từ hai hung, sát tinh đóng (Kình, Đà, Hỏa, Linh, Không, Kiếp, Song Hao, Hóa Kỵ)",
             {"all": [{"not": {"any": [p[2] for p in PAIRS]}}, {"count": HUNG_SAT_SELF, "operator": "gte", "value": 2}]})
HA_CACH_READING = ("TH p.77: hạ cách khi không có cát tinh hội đủ bộ VÀ có hung tinh, sát tinh đóng; danh sách hung sát lấy từ ví dụ của "
                   "sách (Kình Đà, Không Kiếp, Song Hao, Hóa Kỵ) cộng Hỏa Linh là sát tinh; 'đóng' đọc là ở chính cung Mệnh; ngưỡng "
                   "'nhiều' = từ hai sao là quy ước của hệ thống.")


def kem_sang(stars: list[str]) -> dict:
    return ev("chinh_tinh_kem_sang", "chính tinh của cách không nhập miếu, vượng hay đắc địa (bình hoặc hãm)",
              {"any": [fact(f"palace.tp_rank.{s}", "lte", 1) for s in stars]})


KEM_SANG_READING = ("TH p.76: các cách này 'cần được nhập miếu hay vượng địa, đắc địa' mới lên thượng cách; hệ thống đọc là phản chứng hạ "
                    "một bậc khi một chính tinh của cách chỉ bình hoặc hãm (độ sáng theo bảng mặc định của hệ thống).")


def group(fid, name, core, members, extra_breakers=(), extra_src=None, core_src=(), effect=(), variants=()):
    """TPVT / CNĐL / SPLT: TH p.76 thượng cách boosters, TH p.77 hạ cách breaker, TH p.76 brightness refutation."""
    f = {"id": fid, "name_vi": name, "anchor": "Mệnh", "core": core, "kind": "cat",
         "boosters": [ev(i, lab, w) for i, lab, w in PAIRS], "breakers": [HA_CACH, *extra_breakers], "rescuers": [],
         "refutations": [kem_sang(members)], "thuong_at": 2}
    items = {f"boosters:{i}": {"scope": "cach", "sources": [TH76_THUONG], "reading": PAIR_READING} for i, _, _ in PAIRS}
    items["breakers:ha_cach"] = {"scope": "cach", "sources": [TH77_HA, TH77_HA_DONG, TH77_VI_DU], "reading": HA_CACH_READING}
    items["refutations:chinh_tinh_kem_sang"] = {"scope": "cach", "sources": [TH76_SANG], "reading": KEM_SANG_READING}
    items.update(extra_src or {})
    return f, {"core": [TH76_LIST, *core_src], "effect": [TH76_THUONG, TH77_HA_EFFECT, *effect], "core_alone": "hinh_thuc",
               "core_alone_reading": "TH pp.76-77: cách chính tinh cần miếu vượng và cát tinh hội mới là thượng cách; thiếu cát tinh mà gặp "
                                     "hung sát là hạ cách. Lõi đơn thuần chỉ là có hình thức.",
               "items": items, "variants": list(variants)}


# ---------------------------------------------------------------- the ten formations

F, E = [], {}


def add(f: dict, e: dict, status: str = "verified", note: str = ""):
    srcs = sorted({BOOK_ID[s["book"]] for s in e["core"] + [x for it in e["items"].values() for x in it["sources"]]})
    f.update(school="sach_doi_chieu", sourceIds=srcs, reviewStatus=status, experimental=False, definition_version=3,
             provenance="Đối chiếu trang sách (KL/TH/TT) ngày 2026-10-23; trích dẫn và lý do giữ/bỏ ở evidence, dropped.", note=note)
    F.append(f)
    E[f["id"]] = e


# 1. Tử Phủ Vũ Tướng
add(*group("CACH_X_TU_PHU_VU_TUONG", "Tử Phủ Vũ Tướng",
           fact("palace.rel.tp_majors", "contains_all", ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"]),
           ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"],
           core_src=[q("TH", 72, "7. Tử, Phủ, Vũ, Tướng cách."), q("KL", 166, "a. Tử Phủ Vũ Tướng (Hành động có lý luận)")],
           effect=[q("KL", 96, "Các cách Tử Phủ, Tử Phủ Vũ Tướng, Phủ Vũ đều rất tốt về mọi mặt công danh, tài lộc, phúc")],
           extra_src={"boosters:ta_huu_hoi": {"scope": "cach", "sources": [TH76_THUONG, q("KL", 132, "Cho nên người xưa vẫn quan niệm rằng cách Tử Phủ Vũ Tướng mà thiếu Tả Hữu thì đi tìm Tham")],
                                              "reading": PAIR_READING + " KL p.132: cách Tử Phủ Vũ Tướng cần Tả Hữu phụ tá."}},
           variants=[{"note": "Sách không định nghĩa hình học của nhóm; hệ thống đọc là đủ bốn sao trong tam phương tứ chính của Mệnh, như TT p.24 "
                              "định nghĩa nhóm song song Cơ Nguyệt Đồng Lương ('các cung tam hợp xung chiếu có đủ bốn sao').",
                      "sources": [q("TT", 24, "đủ bốn sao trên đây nếu không có những cát tinh khác trợ lực chỉ làm công chức quèn")]}]))

# 2. Tử Phủ đồng cung
TT22_SAT = q("TT", 22, "Tử Phủ đồng cung vô sát tấu, Giáp nhân hưởng phúc chung thân")
add({"id": "CACH_X_TU_PHU_DONG_CUNG", "name_vi": "Tử Phủ đồng cung", "anchor": "Mệnh", "kind": "cat",
     "core": fact("palace.rel.self_majors", "contains_all", ["Tử Vi", "Thiên Phủ"]),
     "boosters": [ev("loc_ton_hoi", "Lộc Tồn hội trong tam phương", fact("palace.rel.tp_stars", "contains", "Lộc Tồn"))],
     "breakers": [ev("sat_tinh_hoi", "sát tinh (Kình, Đà, Hỏa, Linh, Không, Kiếp) hội trong tam phương",
                     fact("palace.rel.tp_stars", "contains_any", SAT6))],
     "rescuers": [],
     "refutations": [ev("tuan_triet_an_ngu", "Tuần hoặc Triệt án ngữ ở cung Mệnh",
                        {"any": [fact("palace.tuan", "eq", True), fact("palace.triet", "eq", True)]})],
     "thuong_at": 1},
    {"core": [q("TH", 72, "1. Tử, Phủ đồng cung cáh (đóng ở Mệnh hay Thân)"),
              q("KL", 49, "Cung Mệnh ở Dần, Thâm có Tử vi, Thiên phủ đồng cung, cả đời sung sướng.")],
     "effect": [q("KL", 49, "4 . Tử Phủ đồng cung, chung thân phúc hậu"),
                q("KL", 55, "Mệnh có Tử Phủ thì được hưởng phúc lộc tốt rất nhiều, chỉ sợ Triệt Tuần án ngữ thì kém đi thôi.")],
     "core_alone": "thanh", "core_alone_reading": "TH p.72 kể Tử Phủ đồng cung là quý cách; KL p.49: cả đời sung sướng.",
     "items": {
         "boosters:loc_ton_hoi": {"scope": "cach", "sources": [q("TT", 22, "cùng ở Thân hoặc Dần lập mệnh lại thêm các sao tốt khác nhất là sao Lộc Tồn suốt đời phúc hậu,")],
                                  "reading": "TT p.22 (Tử Phủ triền viên, lộc phùng): Tử Vi, Thiên Phủ cùng ở Dần/Thân lập Mệnh, thêm sao tốt nhất là Lộc Tồn "
                                             "thì suốt đời phúc hậu, chức đến tam công; 'phùng' đọc là hội trong tam phương."},
         "breakers:sat_tinh_hoi": {"scope": "cach", "sources": [TT22_SAT, q("TT", 22, "gặp những sát tinh làm hỗn"),
                                                                q("KL", 49, "không gặp sát tinh như Kình Đà Không Kiếp thì làm đến chức lớn")],
                                   "reading": "TT p.22: Tử Phủ đồng cung 'vô sát tấu' mới hưởng phúc, nếu không gặp sát tinh làm hỗn; 'sát tấu' hiểu "
                                              "theo lời giảng cùng chữ ở KL p.49 (sát tinh như Kình Đà Không Kiếp), cộng Hỏa Linh; 'gặp' đọc là hội "
                                              "trong tam phương. Sách nói thêm tuổi Giáp; điều kiện tuổi không đưa vào điều phá."},
         "refutations:tuan_triet_an_ngu": {"scope": "cach", "sources": [q("KL", 55, "1 . Tử Phủ đồng cung tối vi phúc hậu, thiết hiềm nội trở Triệt Tuần"),
                                                                       q("TT", 160, "Tử Vi, Thiên Phủ đồng cung thật là phúc hậu chỉ hiềm Tuần Triệt cản trở")],
                                           "reading": "Tuần Triệt chỉ làm 'kém đi' (KL p.55), không phá hẳn, nên là phản chứng hạ một bậc."}},
     "variants": [{"note": "TT p.22 có câu 'Tử Phủ đồng cung lâm Tị Hợi'; Tử Vi và Thiên Phủ chỉ đồng cung ở Dần, Thân nên câu này không dùng.",
                   "sources": [q("TT", 22, "Tử Phủ đồng cung lâm Tị Hợi nhất triều phú quí song toàn")]}]})

# 3. Cơ Nguyệt Đồng Lương
TT24 = q("TT", 24, "đủ bốn sao trên đây nếu không có những cát tinh khác trợ lực chỉ làm công chức quèn")
add(*group("CACH_X_CO_NGUYET_DONG_LUONG", "Cơ Nguyệt Đồng Lương",
           fact("palace.rel.tp_majors", "contains_all", ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"]),
           ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"],
           extra_breakers=[
               ev("khong_kiep_ky_hoi", "Địa Không, Địa Kiếp, Hóa Kỵ (từ hai trong ba) hội trong tam phương",
                  {"count": [fact("palace.rel.tp_stars", "contains", "Địa Không"), fact("palace.rel.tp_stars", "contains", "Địa Kiếp"),
                             fact("palace.rel.tp_hoa", "contains", "Hóa Kỵ")], "operator": "gte", "value": 2}),
               ev("hoa_linh_hoi", "Hỏa Tinh, Linh Tinh cùng hội trong tam phương", fact("palace.rel.tp_stars", "contains_all", ["Hỏa Tinh", "Linh Tinh"]))],
           core_src=[q("TT", 24, "Mệnh thân và các cung tam hợp xang chiếu có"), TT24,
                     q("KL", 51, "Mệnh có Cơ Nguyệt Đồng Lương hội chiếu thường là công chức.")],
           effect=[q("KL", 51, "4 . Cơ Nguyệt Đồng Lương tác lại nhân"), TT24],
           extra_src={
               "breakers:khong_kiep_ky_hoi": {"scope": "cach", "sources": [q("TT", 24, "Không Hoá Kị xuống hạ cách")],
                                              "reading": "TT p.24: Cơ Nguyệt Đồng Lương 'gặp Kiếp Không Hoá Kị xuống hạ cách'; 'gặp' đọc là hội trong tam "
                                                         "phương; một nhóm sao kể liền nhau cần từ hai sao (quy ước đã dùng cho 'lũ Riêu Đà Kỵ', "
                                                         "engine/tests/test_cung_bay.py)."},
               "breakers:hoa_linh_hoi": {"scope": "cach", "sources": [q("TH", 159, "Cơ Nguyệt Đồng Lương tối kỵ Hỏa L",
                                                                         "10. Khoa Quyền Lộc Mã tu phòng Không Kiếp ám xung / Cơ Nguyệt Đồng Lương tối kỵ Hỏa Linh xâm phá.")],
                                         "reading": "TH p.159 (Cách cuộc luận): Cơ Nguyệt Đồng Lương tối kỵ Hỏa Linh xâm phá; cặp Hỏa Linh tính khi đủ hai sao."}},
           variants=[{"note": "TT p.37: Cơ Nguyệt Đồng Lương thủ Mệnh ở Dần Thân thì suốt đời làm ăn suôi lọt (vị trí tốt nhất của cách).",
                      "sources": [q("TT", 37, "Cơ Nguyệt đồng Lương thủ mệnh ở Dần Thân thì suốt đời làm ăn suôi lọt")]}]))

# 4. Sát Phá Liêm Tham
add(*group("CACH_X_SAT_PHA_LIEM_THAM", "Sát Phá Liêm Tham",
           fact("palace.rel.tp_majors", "contains_all", ["Thất Sát", "Phá Quân", "Tham Lang"]),
           ["Thất Sát", "Phá Quân", "Tham Lang"],
           core_src=[q("KL", 167, "b. Sát Phá Liêm Tham (Hành động mạch mẽ)")],
           variants=[{"note": "Sách gọi nhóm bốn sao; Thất Sát, Phá Quân, Tham Lang luôn đứng thành bộ tam hợp, Liêm Trinh chỉ nhập bộ ở một số vị trí, "
                              "nên lõi là đủ ba sao Sát Phá Tham trong tam phương (tương đương ngưỡng 'ba trong bốn' của bản nháp).",
                      "sources": [q("TH", 77, "Sát, Phá, Liêm, Tham hội Hồng, Đào, Tấu, Long Phượng làm thợ vẽ hay hoạ sĩ có biệt tài.")]},
                     {"note": "TH p.76 (phi thường cách): Thân thì Sát Phá Liêm Tham nhập miếu vượng địa hội cát tinh, kể cả Kình, Không, Kiếp, Hình Hổ, "
                              "phát đến Vương Tể. Nói cho Thân, nên không thành điều kiện ở Mệnh; ghi lại vì trái chiều với việc coi Kình, Không, Kiếp "
                              "luôn là phá.",
                      "sources": [q("TH", 76, "Thân thí Sát,  Phá, Liêm, Tham nhập miếu, vượng")]}]))

# 5. Nhật Nguyệt tịnh minh
add({"id": "CACH_X_NHAT_NGUYET_TINH_MINH", "name_vi": "Nhật Nguyệt tịnh minh", "anchor": "Mệnh", "kind": "cat",
     "core": {"any": [
         {"all": [fact("palace.branch", "in", ["Thìn", "Tỵ"]), fact("palace.rel.self_majors", "contains", "Thái Dương"),
                  fact("palace.rel.tp_majors", "contains", "Thái Âm")]},
         {"all": [fact("palace.branch", "in", ["Dậu", "Tuất"]), fact("palace.rel.self_majors", "contains", "Thái Âm"),
                  fact("palace.rel.tp_majors", "contains", "Thái Dương")]}]},
     "boosters": [], "breakers": [], "rescuers": [], "refutations": [], "thuong_at": 2},
    {"core": [q("TH", 72, "21. Nhật, Nguyệt tinh minh cách (Nhật ở Thìn, Tỵ, Nguyệt ở Dậu, Tuất, mà Mệnh đóng ở"),
              q("TH", 72, "Nguyệt hay Nhật đều tốt)")],
     "effect": [q("KL", 53, "hưởng giàu sang.")],
     "effect_reading": "KL p.53 (Nhật Nguyệt tịnh tranh quang, Quyền lộc phi tàn): Mệnh ở Thìn có Thái Dương, Nguyệt ở Tuất chiếu, hoặc ngược lại, "
                       "suốt đời được hưởng giàu sang.",
     "core_alone": "thanh", "core_alone_reading": "TH p.72 kể là quý cách với chính điều kiện vị trí; không trang nào nêu điều tăng thế hay phá riêng.",
     "items": {},
     "variants": [{"note": "KL p.53: Nhật Nguyệt thủ Mệnh không bằng hợp chiếu tịnh minh (Mệnh ở Sửu có Nhật Tỵ, Nguyệt Dậu chiếu; Mệnh ở Mùi có "
                           "Nhật Mão, Nguyệt Hợi chiếu). Biến thể chiếu, chưa mã hóa.",
                   "sources": [q("KL", 53, "6. Nhật nguyệt thủ Mệnh bất như hợp chiếu tịnh minh")]},
                  {"note": "TT p.142: Nhật Nguyệt tinh minh là Thái Âm, Thái Dương đều ở miếu vượng địa chiếu sáng; khớp với các vị trí của TH p.72.",
                   "sources": [q("TT", 142, "Thái Aâm, Thái Dương đều đứng ở miếu vượng địa chiếu sáng")]},
                  {"note": "KL p.53: Mệnh có Nhật Nguyệt bị sát tinh hãm hại thì gian, dâm. Nói về tính cách, không nói phá cách này; không dùng làm điều phá.",
                   "sources": [q("KL", 53, "12 . Nhật Nguyệt sát hại, nam đa gian, nữ đa dâm")]}]})

# 6. Nhật lệ trung thiên
add({"id": "CACH_X_NHAT_LE_TRUNG_THIEN", "name_vi": "Nhật lệ trung thiên", "anchor": "Mệnh", "kind": "cat",
     "core": {"all": [fact("palace.branch", "eq", "Ngọ"), fact("palace.rel.self_majors", "contains", "Thái Dương")]},
     "boosters": [ev("tuoi_canh_tan_dinh_ky", "tuổi Canh, Tân, Đinh, Kỷ", fact("chart.year_stem", "in", ["Canh", "Tân", "Đinh", "Kỷ"]))],
     "breakers": [], "rescuers": [], "refutations": [], "thuong_at": 1},
    {"core": [q("TH", 72, "22. Nhật lệ trung thiên cách ( Nhật cư Ngọ có Mệnh)"),
              q("KL", 52, "2 . Thái dương cư Ngọ, Nhật lệ trung thiên, chuyên quyền chi vị, địch quốc chi phú"),
              q("TT", 158, "Sao Thái Dương đóng cung Ngọ thủ mệnh là cách Nhật lệ trung thiên")],
     "effect": [q("KL", 52, "Mệnh có Thái dương ở Ngọ, vi như mặt  trời chiếu sáng giữa trưa, đứng đầu thiên hạ, giàu có nhất"),
                q("TT", 158, "nhất phẩm quyền hành nếu không thì cũng là phú gia địch quốc")],
     "core_alone": "thanh", "core_alone_reading": "TH p.72 kể là quý cách; KL p.52, TT p.158 nêu hiệu lực ngay với lõi.",
     "items": {"boosters:tuoi_canh_tan_dinh_ky": {"scope": "cach", "sources": [q("KL", 52, "3 . Thái dương cư Ngọ, Canh Tân Đinh Kỷ phú quí song toàn")],
                                                  "reading": "KL p.52: Thái Dương ở Ngọ, tuổi Canh Tân Đinh Kỷ được giàu sang phú quý mọi mặt."}},
     "variants": [{"note": "TT p.142 gọi Thái Dương đơn thủ Mệnh ở Ngọ là 'Kim sán quang huy' (cùng lõi, tên khác).",
                   "sources": [q("TT", 142, "Kim sán quang huy (Thái Dương đơn thủ mệnh cung ở Ngọ)")]}]})

# 7. Thạch trung ẩn ngọc
TH43_IMG = ("Cự ở cung Tí, Ngọ là ngọc trong đá (Thạch trung ẩn ngọc) nên cần gặp được Tuần, Triệt hay Hóa Lộc thì ngọc mới lộ ra được, thì mới "
            "đẹp rực rỡ. Nếu không gặp được cách này hay lại gặp Lộc tồn thì là chìm, ấy là hạng đa học đa năng, nhưng không gặp được thời vận "
            "hiển hách. Nếu lại gặp hung tinh như Kỵ, Hình, Sát, thì tuy có thọ, song không bao giờ được toại ý vừa lòng.")
TH43_CORE = q("TH", 43, "Cự ở cung Tí, Ngọ là ngọc trong đá (Thạch trung ẩn ngọc) nên cần gặp được Tuần, Triệt", TH43_IMG)
add({"id": "CACH_X_THACH_TRUNG_AN_NGOC", "name_vi": "Thạch trung ẩn ngọc", "anchor": "Mệnh", "kind": "cat",
     "core": {"all": [fact("palace.branch", "in", ["Tý", "Ngọ"]), fact("palace.rel.self_majors", "contains", "Cự Môn")]},
     "boosters": [
         ev("tuan_triet_an_ngu", "Tuần hoặc Triệt ở cung Mệnh (đẽo đá lộ ngọc)", {"any": [fact("palace.tuan", "eq", True), fact("palace.triet", "eq", True)]}),
         ev("hoa_loc_hoi", "Hóa Lộc hội trong tam phương", fact("palace.rel.tp_hoa", "contains", "Hóa Lộc")),
         ev("tam_hoa_hoi_du", "Hóa Khoa, Hóa Quyền, Hóa Lộc cùng hội trong tam phương", fact("palace.rel.tp_hoa", "contains_all", TAM_HOA)),
         ev("song_hao", "Song Hao (Đại Hao, Tiểu Hao) ở cung Mệnh cùng Cự Môn", fact("palace.rel.self_stars", "contains_any", ["Đại Hao", "Tiểu Hao"]))],
     "breakers": [
         ev("loc_ton_hoi", "Lộc Tồn hội trong tam phương (ngọc chìm)", fact("palace.rel.tp_stars", "contains", "Lộc Tồn")),
         ev("ky_hinh_hoi", "Hóa Kỵ hoặc Thiên Hình hội trong tam phương",
            {"any": [fact("palace.rel.tp_hoa", "contains", "Hóa Kỵ"), fact("palace.rel.tp_stars", "contains", "Thiên Hình")]})],
     "rescuers": [], "refutations": [], "thuong_at": 2},
    {"core": [q("KL", 44, "Mệnh có Cự môn, Di có Thiên cơ  ở Tí Ngọ"), TH43_CORE, q("TT", 123, "Tí Ngọ Cự Môn thạch trung ẩn ngọc.")],
     "effect": [q("KL", 106, "nằm trong đá, có thợ đẽo đá cắt gọt thành viên ngọc quí, có nghĩa là tài năng gặp thời."),
                q("TT", 34, "Ngọ hội với Khoa, Quyền lộc là cách ngọc ẩn trong đá, hưởng phúc lớn")],
     "core_alone": "hinh_thuc", "core_alone_reading": "TH p.43: không gặp Tuần, Triệt hay Hóa Lộc thì ngọc còn chìm, chưa gặp thời.",
     "items": {
         "boosters:tuan_triet_an_ngu": {"scope": "cach", "sources": [TH43_CORE, q("KL", 106, "Cự môn ở Tí Ngọ gặp Tuần Triệt là kỳ cách, người xưa gọi là “Thạch trung ẩn ngọc” ví như ngọc")],
                                        "reading": "Tuần Triệt ở Mệnh là điều cần cho cách này (TH p.43, KL p.106); bản nháp để nó là phản chứng, ngược với sách."},
         "boosters:hoa_loc_hoi": {"scope": "cach", "sources": [q("TH", 43, "hay Hóa Lộc thì ngọc mới lộ ra được, thì mới đẹp rực rỡ", TH43_IMG)],
                                  "reading": "TH p.43: cần Tuần, Triệt hay Hóa Lộc; 'gặp' đọc là hội trong tam phương."},
         "boosters:tam_hoa_hoi_du": {"scope": "cach", "sources": [q("KL", 57, "1. Cự môn Tí Ngọ, Khoa Quyền Lộc, Thạch trung ẩn ngọc, phúc hưng long"),
                                                                  q("TT", 34, "Cư Môn Tí, Ngọ khoa quyền lộc trạch trung ẩn ngọc phúc hưng long")],
                                     "reading": "KL p.57 và TT p.34: Cự Môn ở Tý Ngọ hội Khoa, Quyền, Lộc. Câu phú gốc chữ Hán (bản web) chỉ nói Khoa, Lộc; "
                                                "giữ đủ ba theo hai sách in."},
         "boosters:song_hao": {"scope": "cach", "sources": [q("KL", 203, "Song Hao cần cho Cự môn ở các cung Tài, Mệnh vì cách Thạch trung ẩn ngọc của Cự môn cần"),
                                                            q("KL", 106, "Cự môn cần Song Hao (Mão, Dậu) ví như phải khổ công gánh nước sôn nghĩa là lớn rửa sạch viên")],
                               "reading": "KL p.203: cách Thạch trung ẩn ngọc cần Song Hao để rửa ngọc, Song Hao cùng cung với Cự Môn; Đại Hao và Tiểu Hao "
                                          "luôn xung chiếu nhau nên một sao ở Mệnh thì sao kia ở Thiên Di."},
         "breakers:loc_ton_hoi": {"scope": "cach", "sources": [q("TH", 43, "Nếu không ặp được cách này hay lại gặp", TH43_IMG)],
                                  "reading": "TH p.43: không gặp Tuần Triệt, Hóa Lộc, hay lại gặp Lộc Tồn thì ngọc chìm, không gặp thời vận hiển hách."},
         "breakers:ky_hinh_hoi": {"scope": "cach", "sources": [q("TH", 43, "lại gặp hung tinh như Kỵ, Hình, S", TH43_IMG),
                                                                       q("TH", 43, "gặp được sát tinh hội tất phú quí vẹn toa",
                                                                         "Nếu gặp được sát tinh hội tất phú quí vẹn toàn, uy quyền hiển hách, danh tiếng lẫy lừng.")],
                                  "reading": "TH p.43, liền sau câu về cách: gặp hung tinh như Kỵ, Hình, Sát thì không bao giờ toại ý. Chỉ giữ Kỵ và Hình: "
                                             "cùng trang nói Cự đắc địa 'gặp được sát tinh hội tất phú quí vẹn toàn', nên chữ 'Sát' không mã hóa."}},
     "variants": [{"note": "KL p.44 ghi thêm 'Di có Thiên cơ'; mục 7 (Tam hóa liên châu) ở KL p.44 lặp nguyên văn mục 6, là lỗi in.",
                   "sources": [q("KL", 44, "6. Thạch trung ẩn ngọc")]}]})

# 8. Mã đầu đới kiếm (disputed core)
KL64_PHA = q("KL", 64, "Mệnh ở Ngọ, có Kình dương, gặp Thất sát, Thiên hình đồng cung là cách kiếm kể cổ ngựa, thì")
KL64_THANH = q("KL", 64, "Mệnh ở Ngọ, có Kình dương đồng cung, nhưng xa lánh được Thất sát, Thiên hình mà lại gặp được")
add({"id": "CACH_X_MA_DAU_DOI_KIEM", "name_vi": "Mã đầu đới kiếm", "anchor": "Mệnh", "kind": "cat",
     "core": {"all": [fact("palace.branch", "eq", "Ngọ"), fact("palace.rel.self_stars", "contains", "Kình Dương")]},
     "boosters": [ev("khoa_quyen_loc_hoi", "Hóa Khoa, Hóa Quyền, Hóa Lộc cùng hội trong tam phương", fact("palace.rel.tp_hoa", "contains_all", TAM_HOA))],
     "breakers": [ev("that_sat_thien_hinh_dong_cung", "Thất Sát hoặc Thiên Hình đồng cung với Kình Dương ở Mệnh",
                     fact("palace.rel.self_stars", "contains_any", ["Thất Sát", "Thiên Hình"]))],
     "rescuers": [], "refutations": [], "thuong_at": 1},
    {"core": [q("KL", 64, "6 . Mã đầu đới kiếm, trấn ngự biên cương:"), KL64_THANH,
              q("TT", 50, "Mệnh viên Ngọ toạ Kình Dương")],
     "effect": [q("KL", 64, "Khoa Quyền Lộc thì tại có sự nghiệp lớn, hiển đạt về võ nghiệp."),
                q("KL", 64, "không chết yểu cũng mang tàn tật khổ sở.")],
     "core_alone": "hinh_thuc", "core_alone_reading": "KL p.64: phải xa Thất Sát, Thiên Hình và gặp Khoa Quyền Lộc mới trấn ngự biên cương.",
     "items": {
         "boosters:khoa_quyen_loc_hoi": {"scope": "cach", "sources": [KL64_THANH], "reading": "KL p.64: gặp được Khoa Quyền Lộc (đọc là đủ ba, hội trong tam phương)."},
         "breakers:that_sat_thien_hinh_dong_cung": {"scope": "cach", "sources": [q("KL", 64, "5 . Mã đầu đới kiếm, phi yểu chiết nhi hình thương"), KL64_PHA],
                                                    "reading": "KL p.64: Kình ở Ngọ gặp Thất Sát, Thiên Hình đồng cung thì không chết yểu cũng tàn tật."}},
     "variants": [{"note": "TT p.142: 'Mã đầu đới nhẫn' là Kình Dương gặp Thiên Mã, phải ở tứ mộ mới hay, ở Ngọ cung xấu. Trái với lõi của KL p.64.",
                   "sources": [q("TT", 142, "Nhẫn là sao Kình Dương gặp Thiên Mã, nhưng phải ở tứ mộ địa mới hay, ở Ngọ cung xấu")]},
                  {"note": "KL p.200: Mệnh ở Ngọ có Kình, ngộ Thiên Mã, Tham Lang là cách Mã đầu đái kiếm, phát võ nhưng không bền (lõi chặt hơn).",
                   "sources": [q("KL", 200, "Mệnh ở cung Ngọ (Mã), có Kình (thanh kiếm), ngộ Thiên mã, Tham lang là cách Mã đầu đái")]},
                  {"note": "KL p.60: Mệnh ở Ngọ có Thất Sát, Kình Dương tọa thủ thêm nhiều sát tinh hội chiếu, tuổi Bính Mậu tất gặp tai nạn binh đao "
                           "(cùng chiều với điều phá Thất Sát đồng cung).",
                   "sources": [q("KL", 60, "6. Sát kình tại Ngọ, Mã đầu đới kiếm tương giao sát diệu, Bính Mậu nhân, mệnh nan toàn :")]}]},
    status="disputed", note="Các sách không thống nhất lõi (KL p.64 Kình ở Ngọ; TT p.142 Kình gặp Mã ở tứ mộ, ở Ngọ xấu; KL p.200 thêm Mã, Tham). "
                            "Không đưa ra người đọc như cách đã xác định.")

# 9. Tam kỳ gia hội
add({"id": "CACH_X_TAM_KY_GIA_HOI", "name_vi": "Tam kỳ gia hội", "anchor": "Mệnh", "kind": "cat",
     "core": fact("palace.rel.tp_hoa", "contains_all", TAM_HOA),
     "boosters": [ev("van_chuc_cach", "Xương Khúc, Khôi Việt, Tả Hữu đủ cả ba bộ trong tam phương (Văn chức cách)",
                     fact("palace.rel.tp_stars", "contains_all", ["Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ", "Hữu Bật"]))],
     "breakers": [ev("ky_hoac_kinh_hoi", "Hóa Kỵ hoặc Kình Dương đồng cung hay chiếu vào Mệnh (trong tam phương)",
                     {"any": [fact("palace.rel.tp_hoa", "contains", "Hóa Kỵ"), fact("palace.rel.tp_stars", "contains", "Kình Dương")]})],
     "rescuers": [], "refutations": [], "thuong_at": 1},
    {"core": [q("KL", 66, "Cung mệnh có Khoa, Quyền, Lộc hội họp mà lại bị Hóa kỵ, Kình dương đồng cung hoặc chiếu"),
              q("TH", 73, "26. Lộc hội Khoa Quyền cách (Tức Tam Hóa triều)"),
              q("TT", 142, "Khoa, Quyền lộc củng (Chiếu thủ có cả ba Khoa, Quyền, Lộc)")],
     "effect": [q("TH", 77, "và có Tam Hóa triều về, tất nhiên công danh thành đạt.")],
     "core_alone": "thanh", "core_alone_reading": "TH p.73 kể Lộc hội Khoa Quyền (Tam Hóa triều) là quý cách.",
     "items": {
         "boosters:van_chuc_cach": {"scope": "cach_ghep", "sources": [q("TH", 77, "ăn chức cách: Ba cung Mệnh, Thân Quan cầ",
                                                                         "d. Văn chức cách: Ba cung Mệnh, Thân Quan cần có Xương Khúc, Khôi Việt, Tả Hữu, đóng và "
                                                                         "có Tam Hóa triều về, tất nhiên công danh thành đạt."),
                                                                       q("TH", 77, "n có Xương Khúc, Khôi Việt, Tả Hữu, đóng")],
                                    "reading": "TH p.77 Văn chức cách = Tam Hóa triều cộng Xương Khúc, Khôi Việt, Tả Hữu ở Mệnh, Thân, Quan; hệ thống xét "
                                               "trong tam phương tứ chính của Mệnh (Thân không cố định)."},
         "breakers:ky_hoac_kinh_hoi": {"scope": "cach", "sources": [q("KL", 66, "10. Tam kỳ giao hội, mặc ngộ Kỵ, Kình giáng lộ thanh vân :"),
                                                                    q("KL", 66, "vào thì đường công danh mờ mịt như sương tụ đầy đường đi.")],
                                       "reading": "KL p.66: Hóa Kỵ, Kình Dương đồng cung hoặc chiếu vào Mệnh thì công danh mờ mịt; 'chiếu' đọc là trong tam "
                                                  "phương tứ chính (bản nháp chỉ xét đồng cung)."}},
     "variants": [{"note": "TH p.72 mục 12 'Tam Hoá liên châu' (Khoa, Quyền, Lộc đi liền ba cung đến Mệnh có một hóa) là cách khác, không gộp.",
                   "sources": [q("TH", 72, "ệnh có 1 hóa)")]}]})

# 10. Khôi Việt giáp Mệnh
add({"id": "CACH_X_KHOI_VIET_GIAP_MENH", "name_vi": "Khôi Việt giáp Mệnh", "anchor": "Mệnh", "kind": "cat",
     "core": {"any": [
         {"all": [fact("palace.rel.flank_prev_stars", "contains", "Thiên Khôi"), fact("palace.rel.flank_next_stars", "contains", "Thiên Việt")]},
         {"all": [fact("palace.rel.flank_prev_stars", "contains", "Thiên Việt"), fact("palace.rel.flank_next_stars", "contains", "Thiên Khôi")]}]},
     "boosters": [], "breakers": [], "rescuers": [], "refutations": [], "thuong_at": 2},
    {"core": [q("KL", 44, "Mệnh ở giữa, Khôi một bên, Việt một bên"), q("KL", 62, "3 . Khôi tinh lâm Mệnh vị chí tam công, Khôi tinh giáp mệnh vi kỳ cách"),
              q("TT", 46, "Khôi Việt hiệp mệnh vi kỳ cách. (Giáp mệnh là cách kỳ lạ).")],
     "effect": [q("KL", 44, "Học giỏi, gần người quyền quí"), q("KL", 62, "nếu được Khôi Việt giáp mệnh thì được mọi người kính")],
     "core_alone": "thanh", "core_alone_reading": "KL p.44 kể là quý cách; KL p.62, TT p.46 gọi là kỳ cách. Không trang nào nêu điều tăng thế hay phá riêng.",
     "items": {},
     "variants": [{"note": "KL p.62 mục 4 (Khôi Việt trùng phùng sát thấu) và TT p.46 câu thứ hai nói Khôi Việt Ở Mệnh gặp sát tinh, không phải giáp Mệnh; "
                           "không dùng làm điều phá.",
                   "sources": [q("KL", 62, "Cung mệnh có Khôi Việt lại bị sát tinh hội chiếu thì mang bệnh tật khó chữa khỏi.")]}]})


# ---------------------------------------------------------------- DEEP-3 (2026-10-24): the cát / kỳ cách of KL pp.43-48 not already a cách of
# the engine (the raw entries: engine/data/kg/mined/deep3_kl.json). KL gives a name, an image, the condition and one effect line; no page names a
# booster or breaker for them, so the core alone is the cách ('thanh'). The hạ cách of p.46-47 are formation rules (pack_khao_luan_cach.json):
# the Cách cục chapter tells every formation here as a cát cách. Cách that duplicate a TH / KL cách already in the engine, misprinted ones and
# impossible ones are listed in the raw entries with the reason (dup / skip) and in docs/audit/DEEP-3-mining-tuvi.md.
self_has = lambda s: fact("palace.rel.self_stars", "contains", s)
self_all = lambda *ss: fact("palace.rel.self_stars", "contains_all", list(ss))
giap = lambda a, b: {"any": [{"all": [fact("palace.rel.flank_prev_stars", "contains", a), fact("palace.rel.flank_next_stars", "contains", b)]},
                             {"all": [fact("palace.rel.flank_prev_stars", "contains", b), fact("palace.rel.flank_next_stars", "contains", a)]}]}
KL_ALONE = "KL pp.43-48 kể cách cùng điều kiện và một câu ý nghĩa; không trang nào nêu điều tăng thế hay điều phá riêng cho cách này."


def kl_cach(fid, name, core, core_src, effect, reading=KL_ALONE, boosters=(), items=None, variants=(), thuong_at=2):
    add({"id": fid, "name_vi": name, "anchor": "Mệnh", "kind": "cat", "core": core, "boosters": [ev(*b) for b in boosters], "breakers": [], "rescuers": [],
         "refutations": [], "thuong_at": thuong_at},
        {"core": core_src, "effect": effect, "core_alone": "thanh", "core_alone_reading": reading, "items": items or {}, "variants": list(variants)})


kl_cach("CACH_X_TU_PHU_TRIEU_VIEN", "Tử Phủ triều viên",
        {"all": [fact("palace.rel.self_majors", "contains", "Tử Vi"), fact("palace.dignity_rank.Tử Vi", "gte", 2),
                 {"any": [fact("palace.rel.opp_majors", "contains", "Thiên Phủ"), fact("palace.rel.trine_majors", "contains", "Thiên Phủ")]}]},
        [q("KL", 43, "Mệnh có Tử vi đắc địa, có Thiên phủ chính chiếu")], [q("KL", 43, "-Vua quan hội họp")],
        variants=[{"note": "KL kể các thế có cách: Thiên Phủ xung chiếu (Tử Sát Tỵ Hợi) hoặc tam hợp chiếu (Tử Vi Tý Ngọ, Tử Tướng Thìn Tuất); "
                           "Tử Phủ đồng cung là một cách khác (CACH_X_TU_PHU_DONG_CUNG). 'Đắc địa' đọc trên bảng mặc định (Khảo Luận).",
                   "sources": [q("KL", 43, "tam hợp chiếu (trong cách Tử vi cư Tí Ngọ,hoặc Tử Tướng Thìn Tuất)")]}])
kl_cach("CACH_X_PHU_TUONG_TRIEU_VIEN", "Phủ Tướng triều viên",
        {"all": [fact("palace.rel.self_majors", "contains", "Thiên Phủ"), fact("palace.rel.trine_majors", "contains", "Thiên Tướng")]},
        [q("KL", 43, "Mệnh Thiên phủ, có Thiên tướng đứng hầu")],
        [q("KL", 43, "-Nữ hoàng dự yến tiệc."), q("TT", 118, "Phú Tướng triều viên mệnh tất vinh")],
        reading="KL p.43: khi Mệnh có Thiên Phủ thì Thiên Tướng đương nhiên ở tam hợp, nên lõi đã là cách; TT p.118 (nữ mệnh cốt tủy phú) cũng nói Phủ Tướng triều viên thì Mệnh vinh.")
kl_cach("CACH_X_THAN_DONG", "Thần đồng", self_all("Tử Vi", "Tấu Thư"), [q("KL", 43, "Mệnh có Tử vi đồng cung Tấu thư")], [q("KL", 43, "Thông minh tuyệt vời")])
kl_cach("CACH_X_TOA_QUY_HUONG_QUY", "Tọa quý hướng quý",
        {"any": [{"all": [self_has("Thiên Khôi"), fact("palace.rel.opp_stars", "contains", "Thiên Việt")]},
                 {"all": [self_has("Thiên Việt"), fact("palace.rel.opp_stars", "contains", "Thiên Khôi")]}]},
        [q("KL", 44, "Mệnh có Khôi, Di có Việt hoặc ngược lại")], [q("KL", 44, "-Là người sang quí")],
        variants=[{"note": "TT p.142 đọc rộng hơn (Khôi Việt chiếu Mệnh, hoặc Khôi ở Mệnh, Việt hướng vào); hệ thống giữ cách đọc hẹp của KL (schools.json).",
                   "sources": [q("TT", 142, "(Khôi Việt chiếu mệnh, hoặc Khôi ở mệnh Việt hướng vào và ngược lại)")]}])
kl_cach("CACH_X_TAI_LOC_GIAP_MA", "Tài Lộc giáp Mã",
        {"all": [self_has("Thiên Mã"), {"any": [
            {"all": [fact("palace.rel.flank_prev_stars", "contains", "Vũ Khúc"),
                     {"any": [fact("palace.rel.flank_next_stars", "contains", "Lộc Tồn"), fact("palace.rel.flank_next_hoa", "contains", "Hóa Lộc")]}]},
            {"all": [fact("palace.rel.flank_next_stars", "contains", "Vũ Khúc"),
                     {"any": [fact("palace.rel.flank_prev_stars", "contains", "Lộc Tồn"), fact("palace.rel.flank_prev_hoa", "contains", "Hóa Lộc")]}]}]}]},
        [q("KL", 45, "Mệnh có Thiên mã, Tài (tên gọi của Vũ khúc), Lộc tồn đứng ở cung hai bên"), q("TT", 142, "Thiên Mã thủ Mệnh, giáp Vũ Khúc, Hóa Lộc")],
        [q("KL", 45, "Thương gia giàu có")],
        reading="KL p.45 (Lộc Tồn) và TT p.142 (Hóa Lộc) đều kể là phú cách; lõi nhận cả hai cách đọc 'Lộc' của hai sách (schools.json).")
kl_cach("CACH_X_DOI_KIM_TICH_NGOC", "Đôi kim tích ngọc",
        {"all": [fact("palace.branch", "in", ["Tý", "Ngọ"]), fact("palace.rel.self_majors", "contains_all", ["Thiên Phủ", "Vũ Khúc"]), self_has("Lộc Tồn")]},
        [q("KL", 45, "Mệnh có Thiên phủ – Vũ khúc đồng cung với Lộc tồn ở Tí Ngọ")], [q("KL", 45, "Tiền của đầy nhà")])
kl_cach("CACH_X_PHU_HUU_LAU_DAI", "Phú hữu lâu đài",
        {"all": [fact("palace.branch", "in", ["Mão", "Dậu"]), fact("palace.rel.self_majors", "contains_all", ["Cự Môn", "Thiên Cơ"]),
                 fact("palace.rel.self_stars", "contains_any", ["Đại Hao", "Tiểu Hao"])]},
        [q("KL", 45, "Mệnh có Cự – Cơ, Song Hao ở Mão Dậu")], [q("KL", 45, "Nhà cao cửa rộng, tiền dư của để"), q("KL", 81, "Cự Cơ ở Mão Dậu gặp Song Hao thì được")],
        reading="KL p.45 kể là phú cách, KL p.81 nói Cự Cơ Mão Dậu gặp Song Hao thì hưởng phú quý. Đại Hao và Tiểu Hao luôn xung chiếu nhau: 'Song Hao ở Mão Dậu' là một Hao ở Mệnh, một ở Thiên Di.")
kl_cach("CACH_X_TIEN_CAI_HAU_MA", "Tiền Cái hậu Mã", giap("Hoa Cái", "Thiên Mã"),
        [q("KL", 45, "Mệnh ở giữa, Hoa cái ở  cung đằng trước, Thiên Mã ở cung đằng sau")], [q("KL", 45, "Danh giá hưởng lộc")],
        reading=KL_ALONE + " Hoa Cái và Thiên Mã giáp một cung thì luôn đúng thứ tự trước / sau này, nên lõi chỉ cần hai sao giáp Mệnh.")
kl_cach("CACH_X_VAN_LONG_TE_HOI", "Vân long tế hội",
        {"all": [self_all("Thanh Long", "Lưu Hà"), fact("palace.rel.self_hoa", "contains", "Hóa Kỵ")]},
        [q("KL", 45, "Mệnh có Thanh long gặp Hóa kỵ, Lưu hà đồng cung")], [q("KL", 45, "Được dịp làm giàu")])
kl_cach("CACH_X_TIEN_HINH_HAU_AN", "Tiền Hình hậu Ấn",
        {"all": [fact("palace.rel.flank_next_stars", "contains", "Thiên Hình"), fact("palace.rel.flank_prev_stars", "contains", "Quốc Ấn")]},
        [q("KL", 45, "Mệnh ở giữa Thiên hình đóng ở cung ở cung đằng trước, Quốc ấn theo sau")], [q("KL", 45, "Có chức có tiền")],
        reading=KL_ALONE + " 'Đằng trước' là cung kề theo chiều thuận, như KL p.42 đặt Lưu Kình 'trước' Lưu Lộc Tồn (Lộc Tồn ở Tỵ, Kình ở Ngọ).",
        variants=[{"note": "KL p.42: chiều 'trước' (Lưu Lộc Tồn ở Tỵ, Lưu Kình dương ở Ngọ).",
                   "sources": [q("KL", 42, "Nếu Lưu Lộc tồn ở cung Tỵ, Lưu Kình dương ở Ngọ")]}])
kl_cach("CACH_X_TUONG_PHUC_HONG_DAO", "Tướng Phục Hồng Đào", self_all("Thiên Tướng", "Phục Binh", "Hồng Loan", "Đào Hoa"),
        [q("KL", 46, "Mệnh có Thiên tướng Phục binh Hồng loan, Đào hoa")], [q("KL", 46, "Tuổi trẻ gặp may sớm làm giàu")])
kl_cach("CACH_X_THAI_TOA_GIAP_MENH", "Thai Tọa giáp Mệnh", giap("Tam Thai", "Bát Tọa"), [q("KL", 46, "Mệnh ở giữa, hai bên có Thai Tọa đứng chầu")],
        [q("KL", 46, "Tuổi trẻ sớm hiển đạt"), q("KL", 205, "Giáp Thai giáp Tọa nhẹ đường công danh")])
kl_cach("CACH_X_XUAT_TUONG_NHAP_TUONG", "Xuất Tướng nhập Tướng",
        {"any": [{"all": [fact("palace.rel.self_majors", "contains", "Thiên Tướng"), fact("palace.rel.opp_stars", "contains", "Tướng Quân")]},
                 {"all": [self_has("Tướng Quân"), fact("palace.rel.opp_majors", "contains", "Thiên Tướng")]}]},
        [q("KL", 46, "Mệnh có Thiên tướng, Di có Tướng quân hoặc người ngược lại")], [q("KL", 46, "Giàu có từ trong ra ngoài")])
kl_cach("CACH_X_SONG_LONG", "Song Long vượt uyên", self_all("Thanh Long", "Long Đức"), [q("KL", 46, "Mệnh có Thanh long, Long đức đồng cung")],
        [q("KL", 46, "Gặp thời làm ăn lớn")])
LPHC = ["Long Trì", "Phượng Các", "Bạch Hổ", "Hoa Cái"]
kl_cach("CACH_X_LONG_PHUONG_HO_CAI", "Long Phượng Hổ Cái",
        {"all": [*[{"any": [self_has(s), fact("palace.rel.trine_stars", "contains", s)]} for s in LPHC], fact("palace.rel.self_stars", "contains_any", LPHC)]},
        [q("KL", 46, "Mệnh có một hoặc 2 sao trong 4 sao kể trên, còn lại làm tam hợp chiếu")],
        [q("KL", 46, "Sự nghiệp đã có sẵn sàng"), q("KL", 46, "Có quí nhân nâng đỡ")],
        reading="KL p.46: một hoặc hai sao ở Mệnh, các sao còn lại tam hợp chiếu, là cách; có Bạch Hổ ở Mệnh thì hay hơn (điều tăng thế).",
        boosters=[("bach_ho_o_menh", "Bạch Hổ ở ngay Mệnh", self_has("Bạch Hổ"))], thuong_at=1,
        items={"boosters:bach_ho_o_menh": {"scope": "cach", "sources": [q("KL", 46, "thường thì Mệnh nên có Bạch Hổ thì hay hơn")],
                                           "reading": "KL p.46 nói ngay trong định nghĩa của cách: Mệnh nên có Bạch Hổ thì hay hơn."}})
kl_cach("CACH_X_HOA_KY_SUU_MUI", "Hóa kỵ Sửu Mùi",
        {"all": [fact("palace.branch", "in", ["Sửu", "Mùi"]), fact("palace.rel.self_majors", "contains", "Cự Môn"), fact("palace.rel.self_hoa", "contains", "Hóa Kỵ")]},
        [q("KL", 47, "Mệnh có Cự môn gặp Hóa kỵ đồng cung ở Sửu Mùi")], [q("KL", 47, "Giàu sang phú quí")])
kl_cach("CACH_X_THIEN_DONG_DINH_MAO", "Thiên đồng Đinh Mão",
        {"all": [fact("chart.year_stem", "eq", "Đinh"), fact("chart.year_branch", "eq", "Mão"), fact("palace.rel.self_majors", "contains", "Thiên Đồng")]},
        [q("KL", 47, "Mệnh người Đinh Mão có Thiên đồng thủ mệnh")], [q("KL", 47, "Phát  phúc, phát lộc")])
kl_cach("CACH_X_THIEN_DONG_NGO_VIET", "Thiên đồng ngộ Việt", {"all": [fact("palace.rel.self_majors", "contains", "Thiên Đồng"), self_has("Thiên Việt")]},
        [q("KL", 48, "Mệnh có Thiên đồng – Thiên việt đồng cung")], [q("KL", 48, "Sang quí như sao trên trời")])
kl_cach("CACH_X_THIEN_LUONG_NGO_KHOI", "Thiên lương ngộ Khôi", {"all": [fact("palace.rel.self_majors", "contains", "Thiên Lương"), self_has("Thiên Khôi")]},
        [q("KL", 48, "Mệnh có Thiên lương, Thiên khôi đồng cung")], [q("KL", 48, "Được hưởng phước lớn")])


# ---------------------------------------------------------------- what the cách brings, per state (evidence[id].meaning)
# state -> {text, book, page, quote}: text is a short paraphrase no wider than the page (sensitive parts of a line left out, never added); a state
# with no page stating its effect is left out. States are formation_eval's: thanh_thuong / thanh / hinh_thuc / bi_pha. For a cách whose
# core_alone is 'thanh' the bare core (state hinh_thuc) is already the cách: read meaning.thanh. Mã đầu đới kiếm (disputed) has none.
def m(text: str, book: str, page: int, quote: str, image: str | None = None) -> dict:
    return {"text": text, **q(book, page, quote, image)}


TH76_M = m("thượng cách: phát đến Tam công", "TH", 76, TH76_THUONG["quote"], TH76_THUONG["image"])
TH77_M = m("hạ cách: lao khổ, phải lo miếng ăn từng bữa", "TH", 77, "ang thang lo miếng ăn từng", TH77_HA["image"])
MEANING = {
    "CACH_X_TU_PHU_VU_TUONG": {"thanh_thuong": TH76_M, "bi_pha": TH77_M,
                               "thanh": m("rất tốt về công danh, tài lộc, phúc", "KL", 96, "Các cách Tử Phủ, Tử Phủ Vũ Tướng, Phủ Vũ đều rất tốt về mọi mặt công danh, tài lộc, phúc")},
    "CACH_X_TU_PHU_DONG_CUNG": {"thanh": m("phúc hậu, được hưởng phúc lộc tốt", "KL", 49, "4 . Tử Phủ đồng cung, chung thân phúc hậu"),
                                "thanh_thuong": m("thêm Lộc Tồn thì phúc hậu, chức đến tam công", "TT", 22, "chức đến tam công"),
                                "hinh_thuc": m("phúc lộc kém đi vì Tuần, Triệt án ngữ", "KL", 55,
                                               "Mệnh có Tử Phủ thì được hưởng phúc lộc tốt rất nhiều, chỉ sợ Triệt Tuần án ngữ thì kém đi thôi.")},
    "CACH_X_CO_NGUYET_DONG_LUONG": {"thanh_thuong": TH76_M, "bi_pha": TH77_M,
                                    "thanh": m("thường làm công chức", "KL", 51, "Mệnh có Cơ Nguyệt Đồng Lương hội chiếu thường là công chức."),
                                    "hinh_thuc": m("không có cát tinh trợ lực thì chỉ làm công chức nhỏ", "TT", 24, TT24["quote"])},
    "CACH_X_SAT_PHA_LIEM_THAM": {"thanh_thuong": TH76_M, "bi_pha": TH77_M},
    "CACH_X_NHAT_NGUYET_TINH_MINH": {"thanh": m("được hưởng giàu sang", "KL", 53, "hưởng giàu sang.")},
    "CACH_X_NHAT_LE_TRUNG_THIEN": {"thanh": m("quyền hành bậc cao, không thì cũng giàu có lớn", "TT", 158, "nhất phẩm quyền hành nếu không thì cũng là phú gia địch quốc"),
                                   "thanh_thuong": m("tuổi Canh, Tân, Đinh, Kỷ thì giàu sang phú quý mọi mặt", "KL", 52,
                                                     "3 . Thái dương cư Ngọ, Canh Tân Đinh Kỷ phú quí song toàn")},
    "CACH_X_THACH_TRUNG_AN_NGOC": {"thanh": m("ngọc lộ ra: tài năng gặp thời", "KL", 106,
                                              "nằm trong đá, có thợ đẽo đá cắt gọt thành viên ngọc quí, có nghĩa là tài năng gặp thời."),
                                   "hinh_thuc": m("ngọc còn chìm: học nhiều biết nhiều nhưng chưa gặp thời vận hiển hách", "TH", 43,
                                                  "hưng không gặp đươc thời vận hiển hách", TH43_IMG),
                                   "bi_pha": m("gặp Kỵ, Hình thì khó được toại ý vừa lòng", "TH", 43, "song không bao giờ được toại ý vừa", TH43_IMG)},
    "CACH_X_TAM_KY_GIA_HOI": {"thanh": m("quý cách (TT p.142 xếp Khoa, Quyền, Lộc củng vào quý cách)", "TT", 142, "QUÍ CÁCH"),
                              "thanh_thuong": m("có thêm Xương Khúc, Khôi Việt, Tả Hữu (Văn chức cách) thì công danh thành đạt", "TH", 77,
                                                 "và có Tam Hóa triều về, tất nhiên công danh thành đạt."),
                              "bi_pha": m("gặp Hóa Kỵ, Kình Dương thì đường công danh mờ mịt", "KL", 66, "vào thì đường công danh mờ mịt như sương tụ đầy đường đi.")},
    "CACH_X_KHOI_VIET_GIAP_MENH": {"thanh": m("học giỏi, gần người quyền quý", "KL", 44, "Học giỏi, gần người quyền quí")},
    # DEEP-3 KL pp.43-48: the meaning line printed under each cách (the image line when that is all the page gives, with the group heading)
    "CACH_X_TU_PHU_TRIEU_VIEN": {"thanh": m("quý cách (danh vọng, uy quyền): như vua quan hội họp", "KL", 43, "-Vua quan hội họp")},
    "CACH_X_PHU_TUONG_TRIEU_VIEN": {"thanh": m("Mệnh vinh hiển", "TT", 118, "Phú Tướng triều viên mệnh tất vinh")},
    "CACH_X_THAN_DONG": {"thanh": m("thông minh tuyệt vời", "KL", 43, "Thông minh tuyệt vời")},
    "CACH_X_TOA_QUY_HUONG_QUY": {"thanh": m("là người sang quý", "KL", 44, "-Là người sang quí")},
    "CACH_X_TAI_LOC_GIAP_MA": {"thanh": m("thương gia giàu có", "KL", 45, "Thương gia giàu có")},
    "CACH_X_DOI_KIM_TICH_NGOC": {"thanh": m("tiền của đầy nhà", "KL", 45, "Tiền của đầy nhà")},
    "CACH_X_PHU_HUU_LAU_DAI": {"thanh": m("nhà cao cửa rộng, tiền dư của để", "KL", 45, "Nhà cao cửa rộng, tiền dư của để")},
    "CACH_X_TIEN_CAI_HAU_MA": {"thanh": m("danh giá, hưởng lộc", "KL", 45, "Danh giá hưởng lộc")},
    "CACH_X_VAN_LONG_TE_HOI": {"thanh": m("được dịp làm giàu", "KL", 45, "Được dịp làm giàu")},
    "CACH_X_TIEN_HINH_HAU_AN": {"thanh": m("có chức, có tiền", "KL", 45, "Có chức có tiền")},
    "CACH_X_TUONG_PHUC_HONG_DAO": {"thanh": m("tuổi trẻ gặp may, sớm làm giàu", "KL", 46, "Tuổi trẻ gặp may sớm làm giàu")},
    "CACH_X_THAI_TOA_GIAP_MENH": {"thanh": m("tuổi trẻ sớm hiển đạt", "KL", 46, "Tuổi trẻ sớm hiển đạt")},
    "CACH_X_XUAT_TUONG_NHAP_TUONG": {"thanh": m("giàu có từ trong ra ngoài", "KL", 46, "Giàu có từ trong ra ngoài")},
    "CACH_X_SONG_LONG": {"thanh": m("gặp thời làm ăn lớn", "KL", 46, "Gặp thời làm ăn lớn")},
    "CACH_X_LONG_PHUONG_HO_CAI": {"thanh": m("sự nghiệp có sẵn, có quý nhân nâng đỡ", "KL", 46, "Sự nghiệp đã có sẵn sàng"),
                                  "thanh_thuong": m("Mệnh có Bạch Hổ thì cách hay hơn", "KL", 46, "thường thì Mệnh nên có Bạch Hổ thì hay hơn")},
    "CACH_X_HOA_KY_SUU_MUI": {"thanh": m("giàu sang phú quý", "KL", 47, "Giàu sang phú quí")},
    "CACH_X_THIEN_DONG_DINH_MAO": {"thanh": m("phát phúc, phát lộc", "KL", 47, "Phát  phúc, phát lộc")},
    "CACH_X_THIEN_DONG_NGO_VIET": {"thanh": m("sang quý", "KL", 48, "Sang quí như sao trên trời")},
    "CACH_X_THIEN_LUONG_NGO_KHOI": {"thanh": m("được hưởng phước lớn", "KL", 48, "Được hưởng phước lớn")},
}
for _fid, _mm in MEANING.items():
    E[_fid]["meaning"] = _mm


# ---------------------------------------------------------------- dropped draft conditions

TH74_CUU = q("TH", 74, "Gặp Bại địa và Tuyệt địa cần được cứu giải băng Tam hóa hội hay c")
KL67_KY_KHOA = q("KL", 67, "Cung mệnh tại Hợi, Tí có Hóa kỵ tọa thủ gặp Hoá khoa đồng cung hay xung chiếu là người cẩn")
KL228 = "KL p.228 nói chung về Tuần Triệt ở Mệnh, không nói về cách này"
REASONS = {
    "tam_hoa_hoi_cuu": ("TH p.74 chỉ nói Tam Hóa hội cứu Mệnh an ở bại địa, tuyệt địa; không trang nào nói Tam Hóa cứu một điều phá của cách này.", [TH74_CUU]),
    "khoa_dong_cung": ("KL p.67 chỉ nói Hóa Kỵ gặp Hóa Khoa ở Mệnh Hợi, Tý thì người cẩn thận lời ăn tiếng nói; không nói cứu phá cách.", [KL67_KY_KHOA]),
    "sat_dong_cung": ("Không trang nào nói một sát tinh đồng cung phá cách này.", []),
    "ky_dong_cung": ("Không trang nào nói Hóa Kỵ đồng cung phá cách này.", []),
    "khong_kiep_dong_cung": ("Không trang nào nói riêng Không Kiếp đồng cung phá cách này.", []),
    "sat_khac_dong_cung": ("Không trang nào nói Hỏa, Linh, Không, Kiếp đồng cung phá cách này.", []),
    "hoa_o_ban_cung": ("Không trang nào nói một hóa ở chính Mệnh làm Tam kỳ mạnh thêm (TH p.72 'Tam Hoá liên châu' là cách khác).", []),
    "ta_huu_giai_ky": ("Không trang nào nói Tả Hữu giải Kỵ, Kình cho Tam kỳ.", []),
    "co_chinh_tinh": ("Không trang nào nói Khôi Việt giáp Mệnh mạnh hơn khi Mệnh có chính tinh.", []),
    "vo_chinh_dieu": ("Không trang nào nói Mệnh vô chính diệu làm yếu Khôi Việt giáp Mệnh.", []),
    "loc_hoi": ("KL p.96 nói Thiên Phủ đi với Lộc thì thịnh đạt, về sao Thiên Phủ chứ không về cách; điều tăng thế của cách lấy theo TH p.76.",
                [q("KL", 96, "Nếu Thiên phủ đi với Hóa lộc, Lộc tồn thì càng thịnh đạt.")]),
    "cat_tinh_hoi": ("Thay bằng các bộ cát tinh đủ bộ của TH p.76 (bản nháp tính một sao lẻ).", []),
    "khoa_quyen_loc_hoi": ("Thay bằng bộ Tam Hóa đủ ba của TH p.76 (bản nháp tính một hóa lẻ; KL p.221 chỉ nói về nghề dạy học).", []),
    "khoa_quyen_hoi": ("Không trang nào nói Khoa hoặc Quyền lẻ làm cách này mạnh thêm (TH p.76 tính Tam Hóa đủ bộ).", []),
    "ba_sat_va_ky_trong_tam_phuong": ("Thay bằng điều hạ cách của TH p.77 (thiếu cát tinh đủ bộ VÀ hung sát tinh đóng Mệnh).", [TH77_HA]),
    "Thiên_Tướng_ham": ("Thay bằng phản chứng 'chính tinh kém sáng' của TH p.76 cho cả bốn sao.", [TH76_SANG]),
    "Thất_Sát_ham": ("Thay bằng phản chứng 'chính tinh kém sáng' của TH p.76 cho Sát, Phá, Tham.", [TH76_SANG]),
    "Thái_Dương_ham": ("Lõi theo TH p.72 đặt Thái Dương ở Thìn, Tỵ hoặc Ngọ (vị trí sáng); 'Nhật Nguyệt tàn hung' ở TH p.74 là một bần cách riêng.", []),
    "Thái_Âm_ham": ("Lõi theo TH p.72 đặt Thái Âm ở Dậu, Tuất (vị trí sáng); 'Nhật Nguyệt tàn hung' ở TH p.74 là một bần cách riêng.", []),
    "Cự_Môn_ham": ("Cự Môn ở Tý, Ngọ không bao giờ hãm, nên điều này không bao giờ xảy ra.", []),
    "nhat_nguyet_deu_sang": ("Lõi theo TH p.72 đã đặt Nhật, Nguyệt ở vị trí sáng.", []),
    "nhat_nguyet_ham_gap_sat": ("'Nhật Nguyệt tàn hung' (TH p.74) là bần cách riêng khi Nhật Nguyệt hãm; lõi tịnh minh không chứa vị trí hãm.",
                                [q("TH", 74, "7. Nhật, Nguyệt t")]),
    "ky_hoac_kinh_dong_cung": ("KL p.66 nói Kỵ, Kình phá Tam kỳ giao hội, không nói về Cự Môn Tý Ngọ; điều phá của cách lấy theo TH p.43.",
                               [q("KL", 66, "10. Tam kỳ giao hội, mặc ngộ Kỵ, Kình giáng lộ thanh vân :")]),
    "that_sat_trong_tam_phuong": ("KL p.64 nói Thất Sát, Thiên Hình ĐỒNG CUNG; thay bằng điều phá đồng cung.", [KL64_PHA]),
}
PER_FORMATION = {  # (formation, draft id) -> reason when the general one does not fit
    ("CACH_X_THACH_TRUNG_AN_NGOC", "tuan_triet_an_ngu"): ("Ngược với sách: TH p.43 và KL p.106 nói Cự Môn Tý Ngọ CẦN Tuần Triệt; chuyển thành điều tăng thế.", [TH43_CORE]),
    ("CACH_X_CO_NGUYET_DONG_LUONG", "tuan_triet_an_ngu"): ("TH p.75 nói Mệnh Tuần, Thân Triệt thì rất cần Cơ Nguyệt Đồng Lương sáng sủa (ngược hướng); "
                                                          "KL p.228 chỉ nói chung về Tuần Triệt.", [q("TH", 75, "3. Mệnh Tuần, Thân Triệt thì ở Mệnh hay Thân rất cần có Cơ Nguyệt Đồng Lương sáng sủa")]),
    ("CACH_X_TU_PHU_VU_TUONG", "tuan_triet_an_ngu"): ("TH p.94 nói về sao Thiên Phủ, không về cả cách; phản chứng của cách lấy theo TH p.76.", []),
    ("CACH_X_TU_PHU_VU_TUONG", "sat_dong_cung"): ("Thay bằng điều hạ cách của TH p.77 (thiếu cát tinh đủ bộ VÀ hung sát tinh đóng Mệnh).", [TH77_HA]),
    ("CACH_X_TU_PHU_VU_TUONG", "ky_dong_cung"): ("Gộp vào điều hạ cách của TH p.77 (Hóa Kỵ là một hung tinh trong ví dụ của sách).", [TH77_HA]),
    ("CACH_X_SAT_PHA_LIEM_THAM", "ky_dong_cung"): ("Gộp vào điều hạ cách của TH p.77 (Hóa Kỵ là một hung tinh trong ví dụ của sách).", [TH77_HA]),
    ("CACH_X_CO_NGUYET_DONG_LUONG", "ky_dong_cung"): ("Gộp vào điều phá Không Kiếp Kỵ của TT p.24.", [TT24]),
    ("CACH_X_CO_NGUYET_DONG_LUONG", "khong_kiep_dong_cung"): ("Thay bằng điều phá Không Kiếp Kỵ trong tam phương của TT p.24.", [TT24]),
    ("CACH_X_TU_PHU_DONG_CUNG", "sat_dong_cung"): ("Thay bằng sát tinh hội trong tam phương theo TT p.22 ('vô sát tấu').", [TT22_SAT]),
    ("CACH_X_TU_PHU_DONG_CUNG", "ta_huu_hoi"): ("Không trang nào nói Tả Hữu làm Tử Phủ đồng cung mạnh thêm (KL p.49 mục 3 nói về sao Tử Vi).", []),
    ("CACH_X_TU_PHU_DONG_CUNG", "xuong_khuc_hoi"): ("KL p.55 mục 5 nói về sao Thiên Phủ với Xương Khúc Tả Hữu, không về cách; không giữ.", []),
    ("CACH_X_TAM_KY_GIA_HOI", "ky_hoac_kinh_dong_cung"): ("Thay bằng ky_hoac_kinh_hoi: KL p.66 nói Kỵ, Kình 'đồng cung hoặc chiếu vào', "
                                                         "nên xét cả tam phương chứ không chỉ đồng cung.",
                                                         [q("KL", 66, "Cung mệnh có Khoa, Quyền, Lộc hội họp mà lại bị Hóa kỵ, Kình dương đồng cung hoặc chiếu")]),
    ("CACH_X_MA_DAU_DOI_KIEM", "ky_dong_cung"): ("Không trang nào nói Hóa Kỵ đồng cung phá cách này (KL p.200 nói Kình gặp Kỵ thì có tật, về sao Kình).", []),
}
KEPT_AS = {  # draft id kept under the same id (possibly with a changed expression): no dropped entry
    "CACH_X_TU_PHU_VU_TUONG": {"ta_huu_hoi", "xuong_khuc_hoi"},
    "CACH_X_TU_PHU_DONG_CUNG": {"tuan_triet_an_ngu"},
    "CACH_X_SAT_PHA_LIEM_THAM": {"ta_huu_hoi", "xuong_khuc_hoi", "khoi_viet_hoi"},
    "CACH_X_THACH_TRUNG_AN_NGOC": {"tam_hoa_hoi_du"},
    "CACH_X_MA_DAU_DOI_KIEM": {"khoa_quyen_loc_hoi"},
}


def dropped() -> list[dict]:
    out = []
    draft = {f["id"]: f for f in json.loads(DRAFT.read_text("utf-8"))["formations"]}
    for fid, d in draft.items():
        new = next(f for f in F if f["id"] == fid)
        new_ids = {e["id"] for k in ("boosters", "breakers", "rescuers", "refutations") for e in new[k]}
        for kind in ("boosters", "breakers", "rescuers", "refutations"):
            for e in d.get(kind, []):
                if e["id"] in KEPT_AS.get(fid, set()) or (e["id"] in new_ids and fid != "CACH_X_THACH_TRUNG_AN_NGOC"):
                    continue
                generic = (f"{KL228}." if e["id"] == "tuan_triet_an_ngu" else "Không trang nào nói điều này cho cách này.", [])
                reason, srcs = PER_FORMATION.get((fid, e["id"])) or REASONS.get(e["id"]) or generic
                if e["id"] in ("ta_huu_hoi", "xuong_khuc_hoi", "khoi_viet_hoi") and (fid, e["id"]) not in PER_FORMATION:
                    reason = "Không trang nào nói sao này làm cách này mạnh thêm (bộ cát tinh của TH p.76 chỉ áp cho các cách chính tinh ở đó)."
                out.append({"formation": fid, "kind": kind, "id": e["id"], "label": e["label"], "reason": reason, "sources": srcs})
    return out


def main() -> int:
    data = {"version": 1, "generated_by": "tools/build_formations_verified.py", "date": "2026-10-24",
            "note": "Mười cách cục định nghĩa lại theo trang sách (KL, TH, TT), thêm 19 cách cát / kỳ cách của KL pp.43-48 (DEEP-3, 2026-10-24). Chỉ formations có "
                    "reviewStatus 'verified' được đưa ra người đọc; 'disputed' là các sách không thống nhất lõi. Báo cáo: docs/audit/CACH-CUC-SOURCES.md, "
                    "docs/audit/DEEP-3-mining-tuvi.md.",
            "formations": F, "evidence": E, "dropped": dropped(), "rejected": []}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(F)} formations, {len(data['dropped'])} dropped conditions")
    if not all(book_text.available(b) for b in BOOK_ID):
        print("books absent: quotes not re-checked")
        return 0
    quotes = [(fid, s) for fid, e in E.items() for s in e["core"] + e["effect"] + [x for it in e["items"].values() for x in it["sources"]]
              + [x for v in e["variants"] for x in v["sources"]] + list(e.get("meaning", {}).values())] +[(d["formation"], s) for d in data["dropped"] for s in d["sources"]]
    bad = [(fid, s["book"], s["page"], s["quote"]) for fid, s in quotes if not book_text.quote_on_page(s["book"], s["page"], s["quote"])]
    for b in bad:
        print("NOT ON PAGE:", *b)
    print(f"{len(quotes) - len(bad)}/{len(quotes)} quotes on their page")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
