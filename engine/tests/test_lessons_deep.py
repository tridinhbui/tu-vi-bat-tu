"""Levels 4-5 of the learning journey (lessons_deep.json): quotations are real, statistics resolve to measured data, and the
explanations agree with the engine."""
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "engine" / "web" / "js"
DATA = ROOT / "engine" / "data"
sys.path.insert(0, str(ROOT / "tools"))

L = json.loads((WEB / "lessons_deep.json").read_text("utf-8"))["lessons"]
REF = json.loads((WEB / "reference.json").read_text("utf-8"))
JS = (WEB / "learn.js").read_text("utf-8")
EVW = json.loads((DATA / "source_evidence_web.json").read_text("utf-8"))


def test_titles_and_tracks_match_the_js_registry():
    for k, v in L.items():
        m = re.search(rf"'{k}': \{{ title: \"([^\"]+)\", min: (\d+), sys: '(\w+)', deep: true \}}", JS)
        assert m, k
        assert (m.group(1), int(m.group(2)), m.group(3)) == (v["title"], v["min"], v["sys"])
        assert f"'{k}'" in JS.split("export const LESSONS")[0], f"{k} missing from TRACKS"
    ids = set(L)
    for blk in (b for v in L.values() for b in v["blocks"]):
        if blk.get("lesson"):
            assert blk["lesson"] in ids or f"'{blk['lesson']}'" in JS
        if blk["t"] == "dignity":
            for s in blk["stars"]:
                assert s in REF["tu_vi"]["stars"]


def _resolve(src):
    kind, _, rest = src.partition(":")
    if kind == "ref":
        node = REF
        for p in rest.split("."):
            node = node[p]
        return node
    if kind == "docs":
        node = json.loads((ROOT / "docs" / "reading_base_rate.json").read_text("utf-8"))
        for p in rest.split("."):
            node = node[p]
        return node
    if kind == "grep":
        path, needle = rest.rsplit(":", 1)
        assert needle in (ROOT / path).read_text("utf-8"), src
        return None
    raise AssertionError(src)


def test_every_statistic_matches_its_measured_source():
    n = 0
    for k, v in L.items():
        for b in v["blocks"]:
            if b["t"] != "stat":
                continue
            n += 1
            got = _resolve(b["src"])
            if got is not None:
                assert got == b["v"], (k, b["label"], got, b["v"])
    assert n >= 10


def test_book_example_numbers_match_the_engine():
    """tv-11 quotes the Hán Cao Tổ chart: recompute it so a rule-pack change forces the lesson to be revisited."""
    from fastapi.testclient import TestClient
    from tvbt import lunar_input
    from tvbt.api import app
    sol = lunar_input.lunar_to_solar(13, 11, 2014, False, "vn")[0]
    f = TestClient(app).post("/api/reasoning", json=dict(year=sol.year, month=sol.month, day=sol.day, hour=12, minute=0, gender="male")).json()["systems"]["tu_vi"]["findings"]
    doc = json.loads((ROOT / "docs" / "reading_base_rate.json").read_text("utf-8"))["book_example_han_cao_to"]
    assert doc["findings"] == len(f), "rule packs changed: rerun tools/measure_reading_base_rate.py and revisit lesson tv-11"
    assert doc["menh_supporting"] == len([x for x in f if x["status"] == "supported" and x.get("effect") == "support" and x["subject"] == "palace:Mệnh"])


def _tbct_text():
    return " ".join(e["quote"] + " " + " ".join(a["quote"] for a in (e.get("also") or [])) for e in EVW["entries"])


def test_quotations_are_real():
    from build_source_evidence import fold_q
    book_ok = True
    show = None
    try:
        import fitz  # noqa: F401
        import book_text
        show = __import__("show_page")
        book_ok = all(book_text.available(b) for b in ("KL", "TH", "TT"))
    except Exception:
        book_ok = False
    web = fold_q(_tbct_text())
    checked = 0
    for k, v in L.items():
        for b in v["blocks"]:
            if b["t"] != "quote":
                continue
            q = fold_q(b["x"])
            if b["book"] == "TBCT":
                assert q in web, (k, b["x"])
            elif b.get("img"):
                continue
            elif book_ok and b["book"] in ("KL", "TH", "TT", "ZZ", "TTT"):
                assert q in fold_q(show.text(b["book"], int(b["page"]))), (k, b["book"], b["page"], b["x"])
                checked += 1
    if not book_ok:
        pytest.skip("books not on disk: printed-book quotations could not be re-read (TBCT quotes were still checked)")
    assert checked >= 12


def test_chinese_quotes_have_glosses_and_no_prediction_language():
    banned = re.compile(r"sẽ (giàu|chết|ly (hôn|dị)|bệnh)|chắc chắn (giàu|thành công)", re.I)
    for k, v in L.items():
        for b in v["blocks"]:
            if b["t"] == "quote" and b.get("lang") == "zh":
                assert b.get("gloss"), (k, b["x"])
            text = json.dumps(b, ensure_ascii=False)
            assert not banned.search(text), (k, text[:80])


def test_explanations_agree_with_the_engine():
    # tv-1 (existing beginner lesson): 'Hỏa lục cục' -> first đại hạn at age 6
    from tvbt import tuvi
    assert tuvi.CUC_NAME[6] == "Hỏa lục cục"
    # tv-9: Tham Lang at Ngọ is 'bình' (Thực Hành) vs 'vượng' (Toàn Thư): the lesson's example
    d = REF["tu_vi"]["stars"]["Tham Lang"]["dignity"]
    assert (d["thuc_hanh"]["Ngọ"], d["toan_thu"]["Ngọ"]) == ("bình", "vượng")
    body = json.dumps(L["tv-9"], ensure_ascii=False)
    assert "bình" in body and "vượng" in body
    # bt-5/bt-7 figures are documented in docs/BAZI_DEEP_BOOKS.md and tested in test_bazi_deep_fidelity.py
    doc = (ROOT / "docs" / "BAZI_DEEP_BOOKS.md").read_text("utf-8")
    assert "29/31" in doc and "40%" in doc
