"""The shared star-dignity knowledge base (engine/data/dignity_kb.json, tools/build_dignity_kb.py): completeness, statuses, provenance,
the image-checked corrections, school conflicts, identifier normalisation, and that the chart (badges), the level fields and the rule
facts all come from it — on all 12 palaces over a wide sweep."""
import importlib.util
import json
from functools import lru_cache
from pathlib import Path

import pytest

from tvbt import dignity, tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.loader import DATA
from tvbt.reasoning import facts

ROOT = Path(__file__).resolve().parents[2]
KB = dignity.kb()
BR = KB["branches"]
SCHOOLS = list(KB["schools"])


@lru_cache(maxsize=1)
def _builder():
    spec = importlib.util.spec_from_file_location("bdk", ROOT / "tools" / "build_dignity_kb.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_committed_kb_and_legacy_tables_are_the_builder_output():
    m = _builder()
    kb = m.build()
    assert kb == KB, "run .venv/bin/python tools/build_dignity_kb.py"
    for fname, d in m.legacy_tables(kb).items():
        assert d == json.loads((DATA / fname).read_text("utf-8")), fname


def test_every_placed_star_is_inventoried_with_one_status_per_branch_and_school():
    placed = _builder().inventory()
    assert set(placed) | {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"} == set(KB["stars"])
    for sc in SCHOOLS:
        for star in KB["stars"]:
            row = KB["resolved"][sc][star]
            assert list(row) == BR
            for r in row.values():
                assert r["status"] in KB["statuses"]
                if r["status"] == "VERIFIED":
                    assert r["value"] in KB["levels"] and r["locator"].split()[0] in ("TH", "TT", "KL") and r["school"] in SCHOOLS
                else:
                    assert "value" not in r                         # never a level outside VERIFIED (no default 'bình')
                if r["status"] == "CONFLICT":
                    assert len(r["alternatives"]) >= 2 and len({(a["value"], a["term"]) for a in r["alternatives"]}) >= 2


def test_dignity_never_comes_from_polarity_or_group():
    # stars with no book table stay unclassified whatever their cát/hung group; sát tinh can be đắc, cát tinh can be unknown
    for star, m in KB["stars"].items():
        rows = [KB["resolved"][sc][star][b] for sc in SCHOOLS for b in BR]
        if star in ("Thiên Khôi", "Thiên Việt", "Đào Hoa", "Hồng Loan", "Thiên Hỷ", "Bác Sĩ", "Thái Tuế", "Trường Sinh", "Tam Thai"):
            assert all(r["status"] == "UNVERIFIED" for r in rows), star
    assert dignity.dignity("Kình Dương", "Thìn") == "đắc" and dignity.dignity("Địa Kiếp", "Dần") == "đắc"
    assert dignity.classify("Thiên Khôi", "Tý")["status"] == "UNVERIFIED"


# (school, star, branch) -> expected; read off the page images (see tools/build_dignity_kb.py)
PINNED = {
    ("thuc_hanh", "Thiên Cơ", "Dần"): ("VERIFIED", "đắc"),        # TH p.30 'Địa Dần Thân' (was vượng)
    ("thuc_hanh", "Thiên Cơ", "Thân"): ("VERIFIED", "đắc"),
    ("thuc_hanh", "Thiên Cơ", "Thìn"): ("UNVERIFIED", None),      # printed 'Ích' (was bình)
    ("thuc_hanh", "Thiên Cơ", "Mão"): ("VERIFIED", "vượng"),
    ("thuc_hanh", "Tham Lang", "Tý"): ("VERIFIED", "bình"),       # 'bính' in print, p.42 'BINH địa Tí Ngọ'
    ("thuc_hanh", "Liêm Trinh", "Mão"): ("VERIFIED", "hãm"),      # settled by p.37 prose
    ("thuc_hanh", "Vũ Khúc", "Mão"): ("UNVERIFIED", None),        # 'khá'
    ("thuc_hanh", "Thái Âm", "Thân"): ("VERIFIED", "đắc"),        # 'lợi ích', p.40 prose 'đắc địa thôi'
    ("thuc_hanh", "Thiên Đồng", "Dần"): ("VERIFIED", "đắc"),      # 'Lợi', legacy reading
    ("toan_thu", "Thái Âm", "Tý"): ("CONFLICT", None),            # TT p.31 phú vượng vs Hi Di đắc
    ("toan_thu", "Thái Âm", "Dậu"): ("VERIFIED", "miếu"),
    ("toan_thu", "Tham Lang", "Tý"): ("CONFLICT", None),
    ("toan_thu", "Thất Sát", "Thìn"): ("UNVERIFIED", None),       # 'vô hãm địa' names no branch
    ("toan_thu", "Văn Xương", "Ngọ"): ("CONFLICT", None),         # TT p.41 phú hãm vs ca lợi
    ("toan_thu", "Văn Xương", "Thân"): ("VERIFIED", "đắc"),       # lợi, legacy
    ("toan_thu", "Kình Dương", "Tý"): ("CONFLICT", None),
    ("thuc_hanh", "Linh Tinh", "Tỵ"): ("CONFLICT", None),
    ("khao_luan", "Thiên Cơ", "Thìn"): ("VERIFIED", "miếu"),      # KL p.187
    ("khao_luan", "Tham Lang", "Dần"): ("CONFLICT", None),        # KL p.189 đắc vs p.101 vượng
    ("khao_luan", "Tham Lang", "Mùi"): ("VERIFIED", "miếu"),
    ("khao_luan", "Tử Vi", "Ngọ"): ("UNVERIFIED", None),          # KL gives no Tử Vi table
    ("khao_luan", "Phá Quân", "Tỵ"): ("VERIFIED", "hãm"),         # p.115
    ("thuc_hanh", "Thiên Thương", "Dậu"): ("NOT_APPLICABLE", None),
    ("thuc_hanh", "Lộc Tồn", "Hợi"): ("VERIFIED", "miếu"),        # TT p.47 via fallback
    ("thuc_hanh", "Hóa Kỵ", "Tý"): ("UNVERIFIED", None),          # Tứ Hóa experimental
}


@pytest.mark.parametrize("key", sorted(PINNED))
def test_pinned(key):
    sc, star, b = key
    r = dignity.classify(star, b, sc)
    assert (r["status"], r.get("value")) == PINNED[key]


def test_provenance_and_school_variants():
    r = dignity.classify("Thiên Phủ", "Tý")
    assert r["locator"] == "TH p.37" and {(v["school"], v["value"]) for v in r["variants"]} == {("toan_thu", "miếu"), ("khao_luan", "miếu")}
    assert dignity.classify("Lộc Tồn", "Ngọ")["school"] == "toan_thu"            # fallback is named, never hidden
    assert dignity.classify("Thiên Đồng", "Dần")["legacy"] is True
    r = dignity.classify("Thiên Tướng", "Thìn", "toan_thu")
    assert r["status"] == "UNVERIFIED" and any(v.get("reported") for v in r["variants"])   # phú nôm variant shown, not used


def test_normalize_star():
    for n, m in KB["stars"].items():
        assert dignity.normalize_star(n) == n and dignity.normalize_star(m["id"]) == n and dignity.normalize_star(n.upper()) == n
    assert dignity.normalize_star("Thiên Diêu") == "Thiên Riêu" and dignity.normalize_star("kinh duong") == "Kình Dương"
    assert dignity.normalize_star("Quan Phu") is None and dignity.normalize_star("Quan Phủ") == "Quan Phủ"
    with pytest.raises(ValueError):
        dignity.classify("Tử Vi", "Tý", "school_x")


@lru_cache(maxsize=None)
def _sweep(school):
    return [tuvi.compute(normalize(BirthInput(y, m, 1 + (y * 7 + m) % 28, h, 10, "Asia/Ho_Chi_Minh", ("male", "female")[(y + h) % 2])),
                         dignity_school=school)
            for y in range(1984, 1996) for m in range(1, 13) for h in range(0, 24, 2)]


@pytest.mark.parametrize("school", ["thuc_hanh", "toan_thu"])
def test_chart_badges_levels_and_facts_share_the_knowledge_base(school):
    seen_status, majors_seen = set(), set()
    for c in _sweep(school):
        f = facts.tuvi_facts(c)
        for p in c.palaces:
            assert set(p["dignity_status"]) == set(p["stars"])
            for s in p["stars"]:
                full = dignity.classify(s, p["branch"], school)
                ds = p["dignity_status"][s]
                assert ds["status"] == full["status"] and ds.get("value") == full.get("value") and ds.get("variants") == full.get("variants")
                seen_status.add(ds["status"])
                lvl = full.get("value") if full["status"] == "VERIFIED" else None
                if s in p["major_dignity"]:
                    assert p["major_dignity"][s] == lvl
                    majors_seen.add((s, p["branch"]))
                if s in p["minor_dignity"]:
                    assert p["minor_dignity"][s] == lvl
                if f"palace.dignity.{s}" in f[f"palace:{p['name']}"]:
                    assert f[f"palace:{p['name']}"][f"palace.dignity.{s}"] == (lvl or "unspecified")
    assert seen_status >= {"VERIFIED", "UNVERIFIED"}
    assert len(majors_seen) == 14 * 12                       # every chính tinh in every địa chi occurs in the sweep


def test_api_classify():
    from fastapi.testclient import TestClient
    from tvbt.api import app
    c = TestClient(app)
    r = c.get("/api/dignity/classify", params={"star": "thien co", "branch": "Thân"}).json()
    assert r["status"] == "VERIFIED" and r["value"] == "đắc" and r["locator"] == "TH p.30"
    assert c.get("/api/dignity/classify", params={"star": "Tử Vi", "branch": "X"}).status_code == 422
