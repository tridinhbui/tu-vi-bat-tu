"""Ngô Tất Tố's Kinh Dịch transcription (engine/data/kinh_dich/ntt/<n>.json, book id KD): structure, Hán against zh.wikisource 周易
(tests/fixtures/zhouyi_han_segments.json), page order and layers.  How the files were made: docs/KINH-DICH-NTT-TRANSCRIPTION.md."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import kinh_dich_ntt as kd  # noqa: E402

NTT = ROOT / "engine" / "data" / "kinh_dich" / "ntt"
DOCS = {n: json.loads((NTT / f"{n}.json").read_text("utf-8")) for n in range(1, 65) if (NTT / f"{n}.json").exists()}
MISPRINTS = json.loads((NTT / "misprints.json").read_text("utf-8"))["han"] if (NTT / "misprints.json").exists() else []


def test_all_64_present():
    assert sorted(DOCS) == list(range(1, 65))


@pytest.mark.parametrize("n", range(1, 65))
def test_structure(n):
    doc = DOCS[n]
    assert doc["number"] == n and doc["name_han"] == kd.NAME_HAN[n - 1] and doc["name_vi"] == kd.TOC[n - 1][0]
    kinds = [kd.seg_key(s) for s in doc["segments"]]
    assert sorted({h for k, h in kinds if k == "hao"}) == [1, 2, 3, 4, 5, 6]      # a text may be printed as several LỜI KINH blocks
    assert sorted({h for k, h in kinds if k == "tieu_tuong" and h != "dung"}) == [1, 2, 3, 4, 5, 6]
    assert kd.structure_problems(doc) == []
    assert any(k == "thoan" for k, _ in kinds) and any(k == "thoan_truyen" for k, _ in kinds)
    assert sum(k == "dai_tuong" for k, _ in kinds) >= 1
    assert not any(k == "unknown" for k, _ in kinds)
    special = {("dung", None), ("tieu_tuong", "dung")} | {k for k in kinds if k[0] == "van_ngon"}
    if n in (1, 2):
        assert special <= set(kinds) and ("dung", None) in kinds and ("tieu_tuong", "dung") in kinds and ("van_ngon", None) in kinds
    else:
        assert not (special & set(kinds))


@pytest.mark.parametrize("n", range(1, 65))
def test_pages_monotonic_and_in_book(n):
    doc = DOCS[n]
    pages = [s["page"] for s in doc["segments"]]
    assert pages == sorted(pages)
    first, last = doc["pages"]
    start = kd.TOC[n - 1][1]
    end = kd.TOC[n][1] if n < 64 else kd.LAST_PAGE
    assert first == start and start <= last <= end
    assert all(first <= s["page"] <= s.get("page_end", s["page"]) <= last for s in doc["segments"])


@pytest.mark.parametrize("n", range(1, 65))
def test_layers_not_empty(n):
    """every LỜI KINH block has Hán, Dịch âm and Dịch nghĩa, and some commentary; an empty layer is allowed only where the book has none
    (recorded as the segment's `absent` list after looking at the page)"""
    for s in DOCS[n]["segments"]:
        absent = set(s.get("absent", []))
        need = ("han", "am", "nghia") if s["kind"] != "intro" else ()
        for layer in need:
            assert s.get(layer, "").strip() or layer in absent, (n, kd.seg_key(s), layer)
        assert any(s.get(k, "").strip() for k in ("trinh_di", "chu_hy")) or s.get("other_commentary") or absent, (n, kd.seg_key(s))
        assert "[?]" not in json.dumps(s, ensure_ascii=False) or s.get("status") != "verified"


@pytest.mark.parametrize("n", range(1, 65))
def test_han_matches_zhouyi(n):
    """check (a): every place where the Hán of a block differs from 周易 is in misprints.json, either seen on the print or listed as
    open, and a segment holding an open difference is 'unverified'"""
    ref = kd.han_reference()[n]
    known = {(m["number"], m["kind"], m.get("hao")): m for m in MISPRINTS}
    for key, (ok, book, want) in kd.han_check(DOCS[n], ref).items():
        if ok:
            continue
        m = known[(n, key[0], key[1])]
        assert m["book"] == book and m["reference"] == want, (n, key)
        diffs = kd.han_diffs(DOCS[n], ref)
        assert len(m["differences"]) + len(m.get("open", [])) == len([d for d in diffs if (d["kind"], d["hao"]) == key])
        for o in m.get("open", []):
            seg = DOCS[n]["segments"][o["segment"]]
            assert kd.seg_key(seg) == key and seg["status"] == "unverified", (n, key, o)


@pytest.mark.parametrize("n", range(1, 65))
def test_verified_only_when_checked(n):
    for s in DOCS[n]["segments"]:
        assert s.get("status") in ("verified", "unverified"), (n, kd.seg_key(s))


def test_page_text_from_transcription():
    import book_text
    assert book_text.page_text("KD", 160).strip()
    assert book_text.pdf_page("KD", 63) == 59 and book_text.pdf_page("KD", 367) == 362 and book_text.pdf_page("KD", 667) == 661
    with pytest.raises(KeyError):
        book_text.pdf_page("KD", 366)
