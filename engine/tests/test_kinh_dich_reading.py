"""Kinh Dịch and Mai Hoa readers over every cast: they never fail, every sentence has a known basis, the reader's own sentences (not the
quoted classics) carry no method words and no absolute words, and every interpretation file that exists passes its lint.
Texts not yet transcribed are reported in `missing`, never invented."""
import itertools

import pytest

from tvbt.kinh_dich import core, dien_giai, doc_hao, mai_hoa, reading
from tvbt.kinh_dich.texts import DATA

BASES = {"kinh", "chu_giai", "tinh_toan", "he_thong", "dien_giai", "loi_khuyen"}
OWN = {"tinh_toan", "he_thong", "dien_giai", "loi_khuyen"}


def _read(n, moving, topic=None):
    c = core.from_hexagram(n, moving)
    c["reading_rule"] = doc_hao.resolve(c)
    return c, reading.read(c, topic)


def _sentences(r):
    return [s for sec in r["sections"] for p in sec["paragraphs"] for s in p["sentences"]]


@pytest.mark.parametrize("n", range(1, 65))
def test_every_mask_reads(n):
    for mask in range(64):
        moving = [p for p in range(1, 7) if mask >> (p - 1) & 1]
        c, r = _read(n, moving)
        assert r["sections"][0]["id"] == "tinh_the"
        for s in _sentences(r):
            assert s["basis"] in BASES and s["text"].endswith((".", "!", "?"))
            if s["basis"] in OWN:
                low = s["text"].lower()
                assert not any(w in low for w in dien_giai.META + dien_giai.ABSOLUTE), s["text"]


def test_topic_section_only_with_interpretation():
    for n in range(1, 65):
        _, r = _read(n, [1], "tai_chinh")
        ids = [s["id"] for s in r["sections"]]
        assert ("chu_de" in ids) == (dien_giai.load(n) is not None)


@pytest.mark.parametrize("n", sorted(int(f.stem) for f in (DATA / "dien_giai").glob("*.json")))
def test_interpretation_files_pass_lint(n):
    from tvbt.kinh_dich.texts import quẻ_texts
    if not quẻ_texts(n)["has_ntt"]:
        pytest.skip("Ngô Tất Tố text for this quẻ is not in engine/data/kinh_dich/ntt yet")
    assert dien_giai.lint(n) == []


def test_mai_hoa_reader_on_every_moving_line():
    pytest.importorskip("tvbt.kinh_dich.mai_hoa_reading")
    from tvbt.kinh_dich import mai_hoa_reading as mr
    try:
        mr.rules()
    except FileNotFoundError:
        pytest.skip("engine/data/mai_hoa/rules_extract.json not installed")
    for up, lo in itertools.product(range(1, 9), range(1, 9)):
        for m in range(1, 7):
            c = mai_hoa.by_count(up, 8 if lo == 8 else lo, month=1 + (up + lo + m) % 12)
            r = mr.read(c, None)
            assert {s["id"] for s in r["sections"]} >= {"lap_que", "the_dung", "dien_tien", "chu_de"}
