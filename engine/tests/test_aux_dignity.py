"""Phụ tinh brightness (engine/data/dignity_aux.json, built by tools/build_aux_dignity.py from page images of TH / TT / KL).

Pins: the transcription cell by cell, the "unknown stays unknown" policy, the star-level book fallback, the disputed cells kept out
of production, the 'lợi' level, the chart output on all 12 palaces over a wide sweep, rare configurations, and the rules the
new levels switch on or off."""
import importlib.util
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import pytest

from tvbt import dignity, tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.loader import DATA, load_all
from tvbt.reasoning import engine, facts

BR = "Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi".split()
AUX = json.loads((DATA / "dignity_aux.json").read_text("utf-8"))
RULES, SOURCES = load_all()


def test_committed_json_is_the_builder_output():
    spec = importlib.util.spec_from_file_location("bad", Path(__file__).resolve().parents[2] / "tools" / "build_aux_dignity.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.build() == AUX, "run python tools/build_aux_dignity.py"


def test_table_integrity():
    levels = set(AUX["levels"])
    for school, table in AUX["tables"].items():
        assert school in AUX["sources"]
        for star, t in table.items():
            assert t["cells"], (school, star)
            assert t["locator"].split()[0] == {"thuc_hanh": "TH", "toan_thu": "TT", "khao_luan": "KL"}[school]
            for br, c in t["cells"].items():
                assert br in BR and c["level"] in levels and c["term"] in AUX["term_to_level"]
                if c["term"] == "lợi":                       # lợi is its own level; read as đắc only for the legacy Văn Xương cells
                    assert c["level"] == ("đắc" if star == "Văn Xương" else "lợi") and ("legacy" in c) == (star == "Văn Xương")
                else:
                    assert c["level"] == AUX["term_to_level"][c["term"]] and "legacy" not in c
    for star in AUX["no_table"]:                           # explicitly unclassified stars never enter the lookup
        assert star not in dignity.MINOR_STARS


# (school, star, branch) -> (level, printed term); one or more cells per star and book, read off the page images
PINNED = {
    ("thuc_hanh", "Văn Xương", "Tỵ"): ("miếu", "miếu"), ("thuc_hanh", "Văn Xương", "Thìn"): ("đắc", "đắc"),
    ("thuc_hanh", "Văn Xương", "Hợi"): ("đắc", "lợi"), ("thuc_hanh", "Văn Khúc", "Dần"): ("bình", "bình"),
    ("thuc_hanh", "Văn Khúc", "Mão"): ("vượng", "vượng"), ("thuc_hanh", "Tả Phụ", "Mùi"): ("đắc", "đắc cách"),
    ("thuc_hanh", "Hữu Bật", "Thìn"): ("đắc", "đắc cách"), ("thuc_hanh", "Thiên Mã", "Dần"): ("đắc", "đắc"),
    ("thuc_hanh", "Long Trì", "Sửu"): ("đắc", "đắc"), ("thuc_hanh", "Phượng Các", "Mùi"): ("đắc", "đắc"),
    ("thuc_hanh", "Kình Dương", "Thìn"): ("đắc", "đắc"), ("thuc_hanh", "Kình Dương", "Tý"): ("hãm", "hãm"),
    ("thuc_hanh", "Đà La", "Hợi"): ("hãm", "hãm"), ("thuc_hanh", "Đà La", "Sửu"): ("đắc", "đắc"),
    ("thuc_hanh", "Hỏa Tinh", "Ngọ"): ("miếu", "miếu"), ("thuc_hanh", "Hỏa Tinh", "Dậu"): ("đắc", "đắc"),
    ("thuc_hanh", "Hỏa Tinh", "Hợi"): ("lợi", "lợi"), ("thuc_hanh", "Hỏa Tinh", "Thìn"): ("hãm", "hãm"),
    ("thuc_hanh", "Linh Tinh", "Dần"): ("miếu", "miếu"), ("thuc_hanh", "Linh Tinh", "Sửu"): ("hãm", "hãm"),
    ("thuc_hanh", "Đại Hao", "Mão"): ("đắc", "đắc"), ("thuc_hanh", "Tiểu Hao", "Hợi"): ("hãm", "hãm"),
    ("thuc_hanh", "Tang Môn", "Thân"): ("đắc", "đắc"), ("thuc_hanh", "Bạch Hổ", "Dậu"): ("đắc", "đắc"),
    ("thuc_hanh", "Thiên Khốc", "Ngọ"): ("miếu", "miếu"), ("thuc_hanh", "Thiên Hư", "Sửu"): ("lợi", "lợi"),
    ("thuc_hanh", "Thiên Hư", "Tuất"): ("hãm", "hãm"), ("thuc_hanh", "Thiên Hình", "Mão"): ("đắc", "đắc"),
    ("thuc_hanh", "Địa Không", "Tỵ"): ("đắc", "đắc"), ("thuc_hanh", "Địa Kiếp", "Thân"): ("đắc", "đắc"),
    ("thuc_hanh", "Thiên Riêu", "Tuất"): ("đắc", "đắc"),
    ("toan_thu", "Văn Xương", "Mão"): ("đắc", "lợi"), ("toan_thu", "Văn Khúc", "Tý"): ("miếu", "miếu"),
    ("toan_thu", "Kình Dương", "Sửu"): ("miếu", "miếu"), ("toan_thu", "Kình Dương", "Ngọ"): ("hãm", "hãm"),
    ("toan_thu", "Đà La", "Tỵ"): ("bình", "bình"), ("toan_thu", "Hỏa Tinh", "Hợi"): ("hãm", "hãm"),
    ("toan_thu", "Hỏa Tinh", "Sửu"): ("bình", "bình"), ("toan_thu", "Lộc Tồn", "Tý"): ("miếu", "miếu"),
    ("khao_luan", "Tả Phụ", "Tý"): ("hãm", "hãm"), ("khao_luan", "Đà La", "Tỵ"): ("đắc", "đắc"),
    ("khao_luan", "Địa Kiếp", "Ngọ"): ("hãm", "hãm"), ("khao_luan", "Kiếp Sát", "Hợi"): ("đắc", "đắc"),
    ("khao_luan", "Thiên Hình", "Tý"): ("hãm", "hãm"), ("khao_luan", "Thiên Không", "Dần"): ("đắc", "đắc"),
    ("khao_luan", "Thiên Khốc", "Mão"): ("đắc", "đắc"),
}


@pytest.mark.parametrize("key", sorted(PINNED))
def test_pinned_transcription(key):
    school, star, br = key
    c = AUX["tables"][school][star]["cells"][br]
    assert (c["level"], c["term"]) == PINNED[key]


def test_unknown_stays_unknown():
    for sc in ("thuc_hanh", "toan_thu"):
        for star in ("Thiên Khôi", "Thiên Việt", "Đào Hoa", "Hồng Loan", "Thiên Hỷ", "Hoa Cái", "Ân Quang", "Thiên Quý", "Tam Thai"):
            assert all(dignity.minor_dignity(star, b, sc) is None for b in BR), star
    # a tabulated star's unnamed branch is unknown, even when another book names it (books are never mixed inside one star)
    assert dignity.minor_dignity("Thiên Hình", "Tý", "thuc_hanh") is None and AUX["tables"]["khao_luan"]["Thiên Hình"]["cells"]["Tý"]
    assert dignity.minor_dignity("Thiên Mã", "Thân", "thuc_hanh") is None
    assert dignity.minor_dignity("Văn Xương", "Mão", "thuc_hanh") is None          # printed 'Lợi địa: Hợi Dậu' — second branch unreadable


def test_disputed_cells_are_experimental_not_production():
    assert dignity.minor_dignity("Kình Dương", "Tý", "toan_thu") is None            # TT p.50 prints vượng and hãm
    for b in ("Thìn", "Mùi", "Tỵ"):
        assert dignity.minor_dignity("Linh Tinh", b, "thuc_hanh") is None            # TH p.64 label missing / printed twice
    assert dignity.minor_dignity("Hồng Loan", "Dần", "toan_thu") is None            # second-hand quote in TT p.62
    exp = {(e["school"], e["star"]) for e in AUX["experimental"]}
    assert {("toan_thu", "Kình Dương"), ("thuc_hanh", "Linh Tinh"), ("toan_thu", "Thiên Khốc"), ("thuc_hanh", "Hóa Kỵ")} <= exp
    for e in AUX["experimental"]:                                                    # none of them leaks into the lookup
        for b in e["cells"]:
            got = dignity.minor_dignity_cell(e["star"], b, e["school"]) if e["school"] != "khao_luan" else None
            if got:
                assert got["school"] != e["school"] or AUX["tables"][e["school"]][e["star"]]["cells"].get(b), (e["star"], b)


def test_star_level_fallback_and_source():
    c = dignity.minor_dignity_cell("Lộc Tồn", "Ngọ", "thuc_hanh")                   # TH has no Lộc Tồn table -> TT p.47
    assert c == {"level": "miếu", "term": "miếu", "school": "toan_thu", "locator": "TT p.47"}
    assert dignity.minor_dignity_cell("Kiếp Sát", "Dần", "toan_thu")["school"] == "khao_luan"
    assert dignity.minor_dignity_cell("Linh Tinh", "Dần", "toan_thu")["school"] == "thuc_hanh"   # TT tabulates no Linh Tinh
    assert dignity.minor_dignity_cell("Kình Dương", "Thìn", "thuc_hanh")["level"] == "đắc"        # TH's own table, not TT's miếu
    assert dignity.minor_dignity_cell("Kình Dương", "Thìn", "toan_thu")["level"] == "miếu"


@lru_cache(maxsize=None)
def _sweep(school: str):
    out = []
    for y in range(1984, 1996):                     # every year stem and branch (so every Lộc Tồn / Kình / Đà / Hỏa / Linh seat)
        for m in range(1, 13):                      # every month (Tả Hữu, Hình, Riêu)
            for h in range(0, 24, 2):               # every hour branch (Xương Khúc, Không Kiếp, Mệnh seat)
                out.append(tuvi.compute(normalize(BirthInput(y, m, 1 + (y + m) % 27, h, 10, "Asia/Ho_Chi_Minh", ("male", "female")[h % 4 // 2])),
                                        dignity_school=school))
    return out


@pytest.mark.parametrize("school", ["thuc_hanh", "toan_thu"])
def test_all_twelve_palaces_match_the_lookup(school):
    seen, names = defaultdict(set), defaultdict(int)
    for c in _sweep(school):
        assert len(c.palaces) == 12
        for p in c.palaces:
            here = {s for s in p["stars"] if s in dignity.MINOR_STARS}
            assert set(p["minor_dignity"]) == here, p["name"]
            for s in here:
                cell = dignity.minor_dignity_cell(s, p["branch"], school)
                assert p["minor_dignity"][s] == (cell and cell["level"])
                assert (s in p["minor_dignity_src"]) == (cell is not None)
                if cell:
                    assert p["minor_dignity_src"][s] == {k: cell[k] for k in ("term", "school", "locator")}
                    names[p["name"]] += 1
                seen[s].add(p["branch"])
    assert set(names) == {p["name"] for p in _sweep(school)[0].palaces}      # every palace shows auxiliary badges somewhere
    assert set(seen) == set(dignity.MINOR_STARS)                               # every tabulated star occurs in the sweep
    assert seen["Lộc Tồn"] == set(BR) - {"Thìn", "Tuất", "Sửu", "Mùi"}         # Lộc Tồn never sits in the tứ mộ
    assert seen["Kình Dương"] == {"Tý", "Sửu", "Mão", "Thìn", "Ngọ", "Mùi", "Dậu", "Tuất"}
    assert all(len(seen[s]) == 12 for s in ("Văn Xương", "Văn Khúc", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh", "Tả Phụ"))


def _find(pred, school="thuc_hanh"):
    for c in _sweep(school):
        for p in c.palaces:
            if pred(p):
                return c, p
    raise AssertionError("configuration not in sweep")


def test_rare_configurations():
    _, p = _find(lambda p: {"Tả Phụ", "Hữu Bật"} <= set(p["stars"]) and p["branch"] in ("Sửu", "Mùi"))   # Tả Hữu đồng cung
    assert p["minor_dignity"]["Tả Phụ"] == p["minor_dignity"]["Hữu Bật"] == "đắc"
    _, p = _find(lambda p: {"Địa Không", "Địa Kiếp"} <= set(p["stars"]))                              # Không Kiếp đồng cung (Tỵ/Hợi)
    assert p["branch"] in ("Tỵ", "Hợi") and p["minor_dignity"]["Địa Không"] == p["minor_dignity"]["Địa Kiếp"] == "đắc"
    _, p = _find(lambda p: "Kình Dương" in p["stars"] and p["branch"] == "Tý")                         # Nhâm year: Kình at Tý
    assert p["minor_dignity"]["Kình Dương"] == "hãm" and p["minor_dignity_src"]["Kình Dương"]["locator"] == "TH p.62"
    _, p = _find(lambda p: "Kình Dương" in p["stars"] and p["branch"] == "Tý", "toan_thu")
    assert p["minor_dignity"]["Kình Dương"] is None and "Kình Dương" not in p["minor_dignity_src"]     # disputed in TT
    _, p = _find(lambda p: "Đà La" in p["stars"] and p["branch"] == "Hợi")                             # Quý year: Đà at Hợi
    assert p["minor_dignity"]["Đà La"] == "hãm"
    _, p = _find(lambda p: {"Hỏa Tinh", "Linh Tinh"} <= set(p["stars"]))                              # Hỏa Linh đồng cung
    assert set(p["minor_dignity"]) >= {"Hỏa Tinh", "Linh Tinh"}
    _, p = _find(lambda p: not p["major_stars"] and any(p["minor_dignity"].values()))                  # vô chính diệu still gets badges
    assert not p["major_dignity"]


def _fired(c, rid):
    res = engine.run(RULES, SOURCES, facts.tuvi_facts(c), system="tu_vi")
    return [f for f in res.findings if f.rule_id == rid]


def test_rules_the_new_levels_switch():
    # TT 'Linh Tinh ở Tài Bạch, thế hãm' could never fire before (no Linh Tinh level existed); TH p.64 now supplies hãm at Sửu.
    c, _ = _find(lambda p: p["name"] == "Tài Bạch" and "Linh Tinh" in p["stars"] and p["branch"] == "Sửu")
    assert _fired(c, "TV_TT_PAL_TAI_BACH_LINH_TINH_HAM_M")
    # 'lợi' is not bright: Hỏa Tinh at Hợi in Điền Trạch does not fire the 'thế sáng' rule (TT itself calls Hợi hãm).
    c, p = _find(lambda p: p["name"] == "Điền Trạch" and "Hỏa Tinh" in p["stars"] and p["branch"] == "Hợi")
    assert p["minor_dignity"]["Hỏa Tinh"] == "lợi" and not _fired(c, "TV_TT_PAL_DIEN_TRACH_HOA_TINH_MIEU_P")
    # TH p.64 Hỏa đắc at Tỵ, but this is a Toàn Thư rule: it reads Toàn Thư's own table (bình at Tỵ) and the book's 'nhập miếu'
    # (audit 2026-10-23: each rule's brightness in its own book; nhập miếu no longer read as any bright cell), so it does not fire
    c, _ = _find(lambda p: p["name"] == "Điền Trạch" and "Hỏa Tinh" in p["stars"] and p["branch"] == "Tỵ")
    assert not _fired(c, "TV_TT_PAL_DIEN_TRACH_HOA_TINH_MIEU_P")
    # unknown -> 'unspecified' in the facts, so neither the bright nor the hãm rule fires
    c, _ = _find(lambda p: p["name"] == "Tài Bạch" and "Kình Dương" in p["stars"] and p["branch"] == "Tý", "toan_thu")
    f = facts.tuvi_facts(c)["palace:Tài Bạch"]
    assert f["palace.dignity.Kình Dương"] == "unspecified"
    assert not _fired(c, "TV_TT_PAL_TAI_BACH_KINH_DUONG_MIEU_P") and not _fired(c, "TV_TT_PAL_TAI_BACH_KINH_DUONG_HAM_M")


def test_facts_endpoint_carries_the_same_levels():
    from fastapi.testclient import TestClient
    from tvbt.api import app
    b = {"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male"}
    got = TestClient(app).post("/api/facts", json={**b, "dignity_school": "thuc_hanh"}).json()["palaces"]
    want = tuvi.compute(normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male"))).palaces
    assert [(p["minor_dignity"], p["minor_dignity_src"]) for p in got] == [(p["minor_dignity"], p["minor_dignity_src"]) for p in want]
