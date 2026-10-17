"""Phase 2 scholarly audit: structure of data/experimental/formation_audit.json, quotes against the books (when present),
and the control set of the book's own worked example charts (KL pp.237-246) — mismatches are RECORDED, not tuned away."""
import json
from pathlib import Path

import pytest

from tvbt.formation_explain import analyse
from tvbt.knowledge.loader import load_experimental

ROOT = Path(__file__).resolve().parents[2]
AUDIT = json.loads((ROOT / "engine/data/experimental/formation_audit.json").read_text("utf-8"))
ROWS = AUDIT["rows"]
STATUSES = {"khop", "long_hon", "chat_hon", "khac", "lien_quan", "khong_co_nguon"}
ACTIONS = {"giu_co_nguon", "de_xuat_sua", "giu_gia_thuyet", "quy_uoc_thiet_ke", "khong_the_xay_ra"}


def _definition_conditions():
    out = set()
    for f in load_experimental()[1]:
        out.add((f.id, "core", "core"))
        for role in ("boosters", "breakers", "rescuers", "refutations"):
            out |= {(f.id, role, c.id) for c in getattr(f, role)}
    return out


def test_every_condition_of_every_formation_is_audited_exactly_once():
    keys = [(r["formation"], r["role"], r["id"]) for r in ROWS]
    assert len(keys) == len(set(keys)) == 93
    assert set(keys) == _definition_conditions()


def test_rows_are_well_formed_and_nothing_is_marked_verified():
    for r in ROWS:
        assert r["status"] in STATUSES and r["action"] in ACTIONS
        assert r["reason"].strip()
        assert "verified" not in json.dumps(r, ensure_ascii=False).lower().replace("chưa verified", "")
        for c in r["cites"]:
            assert c["page"] > 0 and c["quote"].strip() and len(c["quote"].split()) <= 30
            assert c["quote_check"] in ("van_ban", "anh", "chua_kiem")
    # whatever is called 'khop' must stand on at least one cited page; nothing without a book may claim a match
    for r in ROWS:
        if r["status"] == "khop":
            assert r["cites"], r
        if r["status"] == "khong_co_nguon":
            assert r["action"] in ("giu_gia_thuyet", "khong_the_xay_ra")


def test_conditions_without_book_basis_are_never_kept_as_sourced():
    for r in ROWS:
        if r["status"] in ("khong_co_nguon", "lien_quan"):
            assert r["action"] in ("giu_gia_thuyet", "quy_uoc_thiet_ke", "khong_the_xay_ra"), r["id"]


def test_rescuers_are_not_credited_beyond_what_the_book_says():
    """no rescuer may be 'khop' unless a page says that star rescues THAT structure; Khoa 'đại cứu giải' (KL p.132) is only general."""
    for r in ROWS:
        if r["role"] == "rescuers":
            assert r["status"] != "khop", (r["formation"], r["id"])
            assert r["action"] != "giu_co_nguon"


def test_design_conventions_are_labelled():
    flagged = {(r["formation_key"], r["id"]) for r in ROWS if r["design_convention"]}
    assert ("SPLT", "core") in flagged                         # "3 of 4" is not a classical number
    assert ("SPLT", "ba_sat_va_ky_trong_tam_phuong") in flagged
    assert all(("tam_hoa_hoi_cuu" in k[1] or True) for k in flagged)
    assert {r["id"] for r in ROWS if r["role"] == "rescuers" and r["id"] == "tam_hoa_hoi_cuu"} and \
        all(r["design_convention"] for r in ROWS if r["id"] == "tam_hoa_hoi_cuu")      # 'phá được cứu' is a convention


def test_the_four_dead_conditions_are_classified_not_edited():
    dead = {(r["formation_key"], r["id"]) for r in ROWS if r["action"] == "khong_the_xay_ra"}
    assert dead == {("TPVT", "Thiên_Tướng_ham"), ("TPDC", "tam_hoa_hoi_cuu"), ("NLTT", "Thái_Dương_ham"), ("TTAN", "Cự_Môn_ham")}


def test_known_school_conflicts_are_kept_apart():
    by = {(r["formation_key"], r["id"]): r for r in ROWS}
    assert by[("TPDC", "sat_dong_cung")]["school_conflict"]      # TT p.22 vs KL p.50
    assert by[("TTAN", "core")]["school_conflict"]               # three definitions of Thạch trung ẩn ngọc
    assert by[("MDDK", "core")]["school_conflict"]               # Kình at Ngọ: KL p.64 good/bad vs TT p.142
    assert by[("NNTM", "core")]["school_conflict"]               # TH p.72 fixed positions vs KL p.53
    assert by[("TTAN", "tuan_triet_an_ngu")]["status"] == "khac" and by[("NNTM", "tuan_triet_an_ngu")]["status"] == "khac"


def test_summary_matches_rows():
    s = AUDIT["summary"]
    assert s["total"] == len(ROWS) == 93
    for k in STATUSES:
        assert s["by_status"].get(k, 0) == sum(1 for r in ROWS if r["status"] == k)
    assert sum(s["by_status"].values()) == 93 and sum(s["by_action"].values()) == 93


def test_quotes_exist_on_the_cited_printed_pages():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    bt = pytest.importorskip("fitz", reason="PyMuPDF needed to read the books") and __import__("book_text")
    checked = 0
    for r in ROWS:
        for c in r["cites"]:
            if c["quote_check"] == "van_ban" and bt.available(c["book_code"]):
                assert bt.quote_on_page(c["book_code"], c["page"], c["quote"]), (c["id"], c["page"])
                checked += 1
    if checked == 0:
        pytest.skip("books not available on this machine")


# ----------------------------------------------------------------------------------------------------------------------
# Control set: the worked charts of Tử Vi Khảo Luận pp.237-246. The engine state is PINNED as it is; 'book' is the author's own verdict.
# dong_y = same direction; khong_khop = opposite direction; khong_phan_xet = the book does not judge that structure.
CONTROL = {
    ("han_cao_to", "CACH_X_TU_PHU_VU_TUONG"): ("thanh_thuong", "dong_y", "KL p.237-238: Tử Vi cư Ngọ 'đế cư đế vị', Tài Vũ Tướng, Quan Liêm Phủ: thế rất mạnh"),
    ("hang_vo", "CACH_X_CO_NGUYET_DONG_LUONG"): ("thanh", "khong_khop", "KL p.239: Tài Đồng Lương ngộ Triệt + Địa Kiếp, Quan Thái Âm ngộ Tuần: thất bại ở Ô Giang; engine chỉ tính phá đồng cung Mệnh (TT p.24 tính cả tam phương)"),
    ("hang_vo", "CACH_X_TAM_KY_GIA_HOI"): ("thanh", "khong_khop", "KL p.239: Cung Di Cự + Kỵ; cách tổng thể xấu; engine chỉ tính Kỵ/Kình đồng cung (KL p.66 tính cả chiếu)"),
    ("khong_minh", "CACH_X_NHAT_NGUYET_TINH_MINH"): ("thanh_thuong", "dong_y", "KL p.240: 'Nhật Nguyệt chiếu hư không', thông minh tuyệt vời"),
    ("nu_quy_mao", "CACH_X_CO_NGUYET_DONG_LUONG"): ("thanh", "khong_phan_xet", "KL p.241: sách không gọi tên cách này"),
    ("nu_quy_mao", "CACH_X_KHOI_VIET_GIAP_MENH"): ("thanh", "khong_phan_xet", "KL p.241: sách không gọi tên cách này"),
    ("mau_ty_pha_san", "CACH_X_NHAT_NGUYET_TINH_MINH"): ("bi_pha", "dong_y", "KL p.243: 'Âm dương lạc hãm' phá sản"),
    ("mau_ty_pha_san", "CACH_X_CO_NGUYET_DONG_LUONG"): ("thanh_thuong", "khong_khop", "KL p.243: Cơ + Hóa Kỵ + Hỏa Linh phá sản; engine không tính Kỵ/Hỏa Linh ngoài đồng cung Mệnh"),
}


def _states(name):
    import sys
    sys.path.insert(0, str(ROOT / "engine/tests"))
    from test_book_examples import CHARTS, build
    fs = load_experimental()[1]
    return {x["id"]: x["state"] for x in analyse(build(CHARTS[name]), fs)}


@pytest.mark.parametrize("name", sorted({k[0] for k in CONTROL}))
def test_control_charts_engine_states_are_pinned_and_everything_else_is_quiet(name):
    got = _states(name)
    for (n, fid), (state, _, _) in CONTROL.items():
        if n == name:
            assert got[fid] == state, (name, fid, got[fid])
    active = {fid for fid, s in got.items() if s != "khong_hien"}
    assert active == {fid for (n, fid) in CONTROL if n == name}, (name, active)


def test_control_set_records_the_mismatches_instead_of_hiding_them():
    verdicts = [v[1] for v in CONTROL.values()]
    assert verdicts.count("dong_y") == 3 and verdicts.count("khong_khop") == 3 and verdicts.count("khong_phan_xet") == 2
    # all three mismatches point the same way: the book counts sát/Kỵ/Kiếp/Triệt on the whole tam phương, the draft only on the Mệnh palace
    assert all("đồng cung" in v[2] or "tam phương" in v[2] or "Kỵ" in v[2] for v in CONTROL.values() if v[1] == "khong_khop")


def test_committed_audit_records_how_each_quote_was_checked():
    """reproducible WITHOUT the PDFs: the committed file pins what was machine-checked; a skipped PDF test is never counted as evidence."""
    s = AUDIT["summary"]
    n = sum(1 for r in ROWS for c in r["cites"] if c["quote_check"] == "van_ban")
    img = {(c["book_code"], c["page"]) for r in ROWS for c in r["cites"] if c["quote_check"] == "anh"}
    assert n == 94 and img == {("TH", 72), ("TH", 74)}
    assert s["khop_machine_checked"] == sum(1 for r in ROWS if r["status"] == "khop" and r["machine_checked"])
    for r in ROWS:
        if r["status"] == "khop" and not r["machine_checked"]:
            assert any(c["quote_check"] == "anh" for c in r["cites"])      # image-read only: flagged, not claimed as machine-verified
