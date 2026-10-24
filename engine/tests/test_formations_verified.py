"""formations_verified.json (tools/build_formations_verified.py, plan W4 data part, owner review item 13): the ten cách cục re-defined
from the book pages. Every kept condition has a source whose quote is on its page of the PDF (skipped when the books are absent), every
draft condition is either kept or dropped with a reason, the file loads in the Formation schema, and the conditions behave as the
pages say on synthetic charts and occur on real ones."""
import json
import random
import sys
from pathlib import Path

import pytest

from phase1_helpers import base_facts
from tvbt import tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.formation import from_dict, validate_formations
from tvbt.reasoning import facts as rfacts
from tvbt.reasoning.formation_eval import evaluate_formation
from tvbt.tuvi import PALACES

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import book_text  # noqa: E402

DATA = json.loads((ROOT / "engine" / "data" / "formations_verified.json").read_text("utf-8"))
DRAFT = json.loads((ROOT / "engine" / "data" / "experimental" / "formations_experimental.json").read_text("utf-8"))["formations"]
FORMS = [from_dict(f) for f in DATA["formations"]]
BY_ID = {f.id: f for f in FORMS}
EV = DATA["evidence"]
KINDS = ("boosters", "breakers", "rescuers", "refutations")
KNOWN = {"palace.*", "chart.*"}
DEEP3 = {"CACH_X_TU_PHU_TRIEU_VIEN", "CACH_X_PHU_TUONG_TRIEU_VIEN", "CACH_X_THAN_DONG", "CACH_X_TOA_QUY_HUONG_QUY", "CACH_X_TAI_LOC_GIAP_MA",
         "CACH_X_DOI_KIM_TICH_NGOC", "CACH_X_PHU_HUU_LAU_DAI", "CACH_X_TIEN_CAI_HAU_MA", "CACH_X_VAN_LONG_TE_HOI", "CACH_X_TIEN_HINH_HAU_AN",
         "CACH_X_TUONG_PHUC_HONG_DAO", "CACH_X_THAI_TOA_GIAP_MENH", "CACH_X_XUAT_TUONG_NHAP_TUONG", "CACH_X_SONG_LONG", "CACH_X_LONG_PHUONG_HO_CAI",
         "CACH_X_HOA_KY_SUU_MUI", "CACH_X_THIEN_DONG_DINH_MAO", "CACH_X_THIEN_DONG_NGO_VIET", "CACH_X_THIEN_LUONG_NGO_KHOI"}


def all_quotes():
    for fid, e in EV.items():
        for s in e["core"] + e["effect"] + [x for it in e["items"].values() for x in it["sources"]] + [x for v in e["variants"] for x in v["sources"]] \
                + list(e.get("meaning", {}).values()):
            yield fid, s
    for d in DATA["dropped"]:
        for s in d["sources"]:
            yield d["formation"], s


def test_schema_and_statuses():
    # the ten re-defined drafts, plus the cát / kỳ cách of KL pp.43-48 added by DEEP-3 (2026-10-24)
    assert set(BY_ID) == {f["id"] for f in DRAFT} | DEEP3 and DATA["rejected"] == []
    errs = validate_formations(FORMS, KNOWN, set(PALACES))
    allowed = {f"{f.id}: formations cannot be 'verified' without a verified source with locator (none supported yet)" for f in FORMS}
    allowed |= {f"{f.id}: needs at least one booster (else thành is undefined)" for f in FORMS if EV[f.id]["core_alone"] == "thanh"}
    assert set(errs) <= allowed, sorted(set(errs) - allowed)
    for f in FORMS:
        assert f.reviewStatus in ("verified", "disputed") and not f.experimental and f.sourceIds, f.id
        assert f.anchor == "Mệnh" and not f.rescuers, f.id          # no page names a rescuer for any of the ten
        assert EV[f.id]["core_alone"] in ("thanh", "hinh_thuc") and EV[f.id]["core"] and EV[f.id]["effect"], f.id
        if not f.boosters:
            assert EV[f.id]["core_alone"] == "thanh", f.id
    assert BY_ID["CACH_X_MA_DAU_DOI_KIEM"].reviewStatus == "disputed"
    assert sum(f.reviewStatus == "verified" for f in FORMS) == 9 + len(DEEP3)
    for fid in DEEP3:                                                # KL gives the cách, one condition and one effect line
        assert EV[fid]["core_alone"] == "thanh" and all(s["book"] in ("KL", "TT") for s in EV[fid]["core"] + EV[fid]["effect"]), fid


def test_every_kept_condition_has_a_source():
    for f in FORMS:
        ids = {f"{k}:{e.id}" for k in KINDS for e in getattr(f, k)}
        assert ids == set(EV[f.id]["items"]), f.id
        for key, it in EV[f.id]["items"].items():
            assert it["sources"] and it["reading"] and it["scope"] in ("cach", "cach_ghep"), (f.id, key)


def test_every_draft_condition_is_kept_or_dropped_with_reason():
    dropped = {(d["formation"], d["kind"], d["id"]) for d in DATA["dropped"]}
    assert all(d["reason"] for d in DATA["dropped"])
    for f in DRAFT:
        new = BY_ID[f["id"]]
        for k in KINDS:
            for e in f.get(k, []):
                kept = any(x.id == e["id"] for x in getattr(new, k))
                assert kept != ((f["id"], k, e["id"]) in dropped), (f["id"], k, e["id"])
    # the draft had Tuần/Triệt as a refutation of Thạch trung ẩn ngọc; TH p.43 and KL p.106 say the cách needs it
    assert ("CACH_X_THACH_TRUNG_AN_NGOC", "refutations", "tuan_triet_an_ngu") in dropped
    assert any(e.id == "tuan_triet_an_ngu" for e in BY_ID["CACH_X_THACH_TRUNG_AN_NGOC"].boosters)


@pytest.mark.skipif(not all(book_text.available(b) for b in ("KL", "TH", "TT")), reason="Tử Vi Khảo Luận / Thực Hành / Toàn Thư PDF not present")
def test_meaning_per_state():
    """Every verified cách says what it brings in at least one state, from a page; only formation_eval's states; plain words."""
    absolute = ("chắc chắn", "nhất định", "suốt đời", "trọn đời", "không bao giờ", "luôn luôn", "tuyệt đối", "định mệnh")
    for f in DATA["formations"]:
        mm = EV[f["id"]].get("meaning", {})
        if f["reviewStatus"] != "verified":
            assert not mm, f["id"]
            continue
        assert mm and set(mm) <= {"thanh", "thanh_thuong", "hinh_thuc", "bi_pha"}, f["id"]
        if EV[f["id"]]["core_alone"] == "thanh":
            assert "thanh" in mm, f["id"]
        for st, x in mm.items():
            assert x["text"] and {"book", "page", "quote"} <= set(x), (f["id"], st)
            assert not any(w in x["text"] for w in absolute), (f["id"], st, x["text"])
        if "thanh_thuong" in mm:
            assert f["boosters"], f["id"]
        if "bi_pha" in mm:
            assert f["breakers"], f["id"]


def test_quotes_are_on_their_page():
    bad = [(fid, s["book"], s["page"], s["quote"]) for fid, s in all_quotes() if not book_text.quote_on_page(s["book"], s["page"], s["quote"])]
    assert not bad, bad


def state(fid, ops, menh="Tý"):
    bf = base_facts(ops, menh)
    d = evaluate_formation(BY_ID[fid], {**bf["chart"], **bf["palace:Mệnh"]})
    return d["state"], set(d["boosters"]) | set(d["breakers"]) | set(d["refutations"])


S = lambda star, where="Mệnh": ("star", star, where)          # noqa: E731
H = lambda hoa, where="Mệnh": ("hoa", hoa, where)             # noqa: E731
TPVT = [S("Tử Vi"), S("Thiên Phủ", "Quan Lộc"), S("Vũ Khúc", "Tài Bạch"), S("Thiên Tướng", "Thiên Di")]
CNDL = [S("Thiên Cơ"), S("Thái Âm", "Quan Lộc"), S("Thiên Đồng", "Tài Bạch"), S("Thiên Lương", "Thiên Di")]
TAM_HOA = [H("Hóa Lộc", "Quan Lộc"), H("Hóa Quyền", "Tài Bạch"), H("Hóa Khoa", "Thiên Di")]


def test_book_conditions():
    # TH p.43 / KL p.106: Cự Môn Tý Ngọ needs Tuần, Triệt or Hóa Lộc; with Lộc Tồn the jade stays sunk
    assert state("CACH_X_THACH_TRUNG_AN_NGOC", [S("Cự Môn")])[0] == "hinh_thuc"
    assert state("CACH_X_THACH_TRUNG_AN_NGOC", [S("Cự Môn"), ("tuan", "Mệnh")])[0] == "thanh"
    assert state("CACH_X_THACH_TRUNG_AN_NGOC", [S("Cự Môn"), ("triet", "Mệnh"), S("Lộc Tồn", "Quan Lộc")])[0] == "bi_pha"
    assert state("CACH_X_THACH_TRUNG_AN_NGOC", [S("Cự Môn"), ("tuan", "Mệnh"), S("Kình Dương", "Thiên Di")])[0] == "thanh"   # 'Sát' not encoded
    assert state("CACH_X_THACH_TRUNG_AN_NGOC", [S("Cự Môn")], menh="Dần")[0] == "khong_hien"
    # TH p.72: Nhật ở Thìn Tỵ, Nguyệt ở Dậu Tuất, Mệnh đóng ở Nhật hay Nguyệt
    assert state("CACH_X_NHAT_NGUYET_TINH_MINH", [S("Thái Dương"), S("Thái Âm", "Thiên Di")], menh="Thìn")[0] == "hinh_thuc"
    assert state("CACH_X_NHAT_NGUYET_TINH_MINH", [S("Thái Âm"), S("Thái Dương", "Thiên Di")], menh="Tuất")[0] == "hinh_thuc"
    assert state("CACH_X_NHAT_NGUYET_TINH_MINH", [S("Thái Dương"), S("Thái Âm", "Thiên Di")], menh="Tý")[0] == "khong_hien"
    # TH p.77 hạ cách: no complete cát pair AND hung/sát đóng Mệnh; a complete pair keeps it from hạ cách
    assert state("CACH_X_TU_PHU_VU_TUONG", TPVT + [S("Kình Dương"), S("Đà La")])[0] == "bi_pha"
    assert state("CACH_X_TU_PHU_VU_TUONG", TPVT + [S("Kình Dương")])[0] == "hinh_thuc"
    assert state("CACH_X_TU_PHU_VU_TUONG", TPVT + [S("Kình Dương"), S("Đà La"), S("Tả Phụ", "Thiên Di"), S("Hữu Bật", "Quan Lộc")])[0] == "thanh"
    assert state("CACH_X_TU_PHU_VU_TUONG", TPVT + [S("Tả Phụ", "Thiên Di")])[0] == "hinh_thuc"            # one star of a pair is not 'đủ bộ'
    assert state("CACH_X_TU_PHU_VU_TUONG", TPVT + TAM_HOA + [S("Văn Xương", "Tài Bạch"), S("Văn Khúc", "Thiên Di")])[0] == "thanh_thuong"
    assert state("CACH_X_TU_PHU_VU_TUONG", TPVT + TAM_HOA + [S("Văn Xương", "Tài Bạch"), S("Văn Khúc", "Thiên Di"),
                                                              ("dig", "Thiên Tướng", "Thiên Di", "hãm")])[0] == "thanh"          # TH p.76: needs miếu/vượng/đắc
    # TT p.24 Kiếp Không Hóa Kỵ, TH p.159 Hỏa Linh
    assert state("CACH_X_CO_NGUYET_DONG_LUONG", CNDL + [S("Địa Không", "Thiên Di"), H("Hóa Kỵ", "Tài Bạch")])[0] == "bi_pha"
    assert state("CACH_X_CO_NGUYET_DONG_LUONG", CNDL + [S("Địa Không", "Thiên Di")])[0] == "hinh_thuc"
    assert state("CACH_X_CO_NGUYET_DONG_LUONG", CNDL + [S("Hỏa Tinh", "Thiên Di"), S("Linh Tinh", "Quan Lộc")])[0] == "bi_pha"
    # TT p.22 vô sát tấu; KL p.55 Tuần Triệt only lowers
    tpdc = [S("Tử Vi"), S("Thiên Phủ")]
    assert state("CACH_X_TU_PHU_DONG_CUNG", tpdc + [S("Lộc Tồn", "Quan Lộc")], menh="Dần")[0] == "thanh_thuong"
    assert state("CACH_X_TU_PHU_DONG_CUNG", tpdc + [S("Lộc Tồn", "Quan Lộc"), ("tuan", "Mệnh")], menh="Dần")[0] == "thanh"
    assert state("CACH_X_TU_PHU_DONG_CUNG", tpdc + [S("Hỏa Tinh", "Tài Bạch")], menh="Dần")[0] == "bi_pha"
    # KL p.66: Kỵ, Kình đồng cung hoặc chiếu
    assert state("CACH_X_TAM_KY_GIA_HOI", TAM_HOA + [S("Kình Dương", "Thiên Di")])[0] == "bi_pha"
    # KL p.64: Thất Sát or Thiên Hình đồng cung
    assert state("CACH_X_MA_DAU_DOI_KIEM", [S("Kình Dương"), S("Thiên Hình")], menh="Ngọ")[0] == "bi_pha"
    assert state("CACH_X_MA_DAU_DOI_KIEM", [S("Kình Dương"), S("Thất Sát", "Thiên Di")] + TAM_HOA, menh="Ngọ")[0] == "thanh_thuong"
    # KL p.52: tuổi Canh Tân Đinh Kỷ (the synthetic base chart for Mệnh Ngọ falls in lunar Kỷ Tỵ)
    assert base_facts([], "Ngọ")["chart"]["chart.year_stem"] == "Kỷ"
    assert state("CACH_X_NHAT_LE_TRUNG_THIEN", [S("Thái Dương")], menh="Ngọ") == ("thanh_thuong", {"tuoi_canh_tan_dinh_ky"})


def test_cores_occur_on_real_charts():
    rng, seen = random.Random(23), set()
    for _ in range(1500):
        b = BirthInput(rng.randint(1940, 2010), rng.randint(1, 12), rng.randint(1, 28), rng.randint(0, 23), 0, "Asia/Ho_Chi_Minh", rng.choice(["male", "female"]))
        bf = rfacts.tuvi_facts(tuvi.compute(normalize(b)))
        fx = {**bf["chart"], **bf["palace:Mệnh"]}
        seen |= {f.id for f in FORMS if evaluate_formation(f, fx)["state"] not in ("khong_hien", "chua_du_du_kien")}
    # every draft core occurs; of the DEEP-3 cách, the common ones (the rare ones are checked on synthetic charts below)
    rare = {"CACH_X_DOI_KIM_TICH_NGOC", "CACH_X_PHU_HUU_LAU_DAI", "CACH_X_TUONG_PHUC_HONG_DAO", "CACH_X_HOA_KY_SUU_MUI", "CACH_X_TAI_LOC_GIAP_MA",
            "CACH_X_TIEN_HINH_HAU_AN", "CACH_X_VAN_LONG_TE_HOI", "CACH_X_THIEN_DONG_DINH_MAO", "CACH_X_THIEN_DONG_NGO_VIET", "CACH_X_THIEN_LUONG_NGO_KHOI",
            "CACH_X_THAN_DONG"}
    assert seen >= set(BY_ID) - rare, set(BY_ID) - rare - seen


def test_deep3_cores_on_synthetic_charts():
    """each KL cách holds on a chart built to its page condition, and not when one piece is missing"""
    cases = {
        "CACH_X_THAN_DONG": ([S("Tử Vi"), S("Tấu Thư")], [S("Tử Vi")], "Tý"),
        "CACH_X_TOA_QUY_HUONG_QUY": ([S("Thiên Khôi"), S("Thiên Việt", "Thiên Di")], [S("Thiên Khôi"), S("Thiên Việt", "Quan Lộc")], "Tý"),
        "CACH_X_TAI_LOC_GIAP_MA": ([S("Thiên Mã"), S("Vũ Khúc", "Huynh Đệ"), H("Hóa Lộc", "Phụ Mẫu")], [S("Thiên Mã"), S("Vũ Khúc", "Huynh Đệ")], "Dần"),
        "CACH_X_DOI_KIM_TICH_NGOC": ([S("Thiên Phủ"), S("Vũ Khúc"), S("Lộc Tồn")], [S("Thiên Phủ"), S("Vũ Khúc")], "Tý"),
        "CACH_X_PHU_HUU_LAU_DAI": ([S("Cự Môn"), S("Thiên Cơ"), S("Đại Hao"), S("Tiểu Hao", "Thiên Di")], [S("Cự Môn"), S("Thiên Cơ")], "Mão"),
        "CACH_X_TIEN_CAI_HAU_MA": ([S("Hoa Cái", "Phụ Mẫu"), S("Thiên Mã", "Huynh Đệ")], [S("Hoa Cái", "Phụ Mẫu")], "Mão"),
        "CACH_X_TIEN_HINH_HAU_AN": ([S("Thiên Hình", "Phụ Mẫu"), S("Quốc Ấn", "Huynh Đệ")], [S("Thiên Hình", "Huynh Đệ"), S("Quốc Ấn", "Phụ Mẫu")], "Mão"),
        "CACH_X_VAN_LONG_TE_HOI": ([S("Thanh Long"), S("Lưu Hà"), H("Hóa Kỵ")], [S("Thanh Long"), S("Lưu Hà")], "Tý"),
        "CACH_X_HOA_KY_SUU_MUI": ([S("Cự Môn"), H("Hóa Kỵ")], [S("Cự Môn")], "Sửu"),
        "CACH_X_THIEN_LUONG_NGO_KHOI": ([S("Thiên Lương"), S("Thiên Khôi")], [S("Thiên Lương"), S("Thiên Khôi", "Thiên Di")], "Tý"),
    }
    for fid, (yes, no, menh) in cases.items():
        assert state(fid, yes, menh)[0] != "khong_hien", fid
        assert state(fid, no, menh)[0] == "khong_hien", fid
    lphc = [S("Bạch Hổ"), S("Long Trì", "Quan Lộc"), S("Phượng Các", "Tài Bạch"), S("Hoa Cái", "Quan Lộc")]
    assert state("CACH_X_LONG_PHUONG_HO_CAI", lphc)[0] == "thanh_thuong"           # KL p.46: Bạch Hổ ở Mệnh thì hay hơn
    assert state("CACH_X_LONG_PHUONG_HO_CAI", [S("Long Trì")] + lphc[1:] + [S("Bạch Hổ", "Tài Bạch")])[0] == "hinh_thuc"
    assert state("CACH_X_LONG_PHUONG_HO_CAI", [S("Long Trì", "Thiên Di")] + lphc[1:3] + [S("Bạch Hổ", "Tài Bạch")])[0] == "khong_hien"
