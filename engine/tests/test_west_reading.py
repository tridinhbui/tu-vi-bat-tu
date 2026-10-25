"""Western reading: every paragraph traceable to a source of its own school, nothing forbidden, deterministic, robust to edge charts."""
import datetime as dt

import pytest

from western import synastry
from western.chart import BirthData, compute
from western.reading import build
from western.reading import synastry as RS

WHEN = dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc)
CHARTS = [
    BirthData(1990, 5, 17, 10, 30, 10.8231, 106.6297, "Asia/Ho_Chi_Minh"),
    BirthData(1962, 2, 5, 0, 0, 28.6139, 77.2090, "Asia/Kolkata"),          # seven planets in Aquarius
    BirthData(1975, 12, 1, 4, 10, -33.8688, 151.2093, "Australia/Sydney"),
    BirthData(2001, 7, 9, 18, 45, 40.7128, -74.006, "America/New_York"),
    BirthData(1990, 1, 10, 12, 0, 69.65, 18.96, "Europe/Oslo"),             # beyond the polar circle
    BirthData(1984, 3, 3, None, None, 21.0285, 105.8542, "Asia/Hanoi"),     # time unknown
]


@pytest.fixture(scope="module")
def readings():
    return [build(compute(b), "deep", g, WHEN) for b, g in zip(CHARTS, ["male", None, "female", None, "male", None])]


def test_audit_finds_no_traceability_school_or_forbidden_issue(readings):
    for r in readings:
        bad = [i for i in r["audit"]["issues"] if i["kind"] in ("untraceable", "school_mix", "forbidden", "duplicate", "template", "house_system", "summary", "opener")]
        assert not bad, bad


def test_every_paragraph_names_its_school_and_sources(readings):
    for r in readings:
        for ch in r["chapters"]:
            for p in ch["paragraphs"]:
                assert p["school"] in ("hellenistic", "traditional", "modern", "compare", "calc")
                assert p["text"].strip() and p["heading"]
                if p["tier"] == "src":
                    assert p["sources"]


def test_overview_is_a_subset_and_every_chapter_says_something(readings):
    r = build(compute(CHARTS[0]), "overview", "male", WHEN)
    assert all(p["level"] == "overview" for ch in r["chapters"] for p in ch["paragraphs"])
    assert all(ch["paragraphs"] for ch in r["chapters"])


def test_deterministic():
    a = build(compute(CHARTS[0]), "deep", None, WHEN)
    b = build(compute(CHARTS[0]), "deep", None, WHEN)
    assert [p["text"] for ch in a["chapters"] for p in ch["paragraphs"]] == [p["text"] for ch in b["chapters"] for p in ch["paragraphs"]]


def test_no_time_chart_skips_house_chapters_honestly(readings):
    r = readings[-1]
    texts = {p["id"]: p["text"] for ch in r["chapters"] for p in ch["paragraphs"]}
    assert "su_nghiep.no_time" in texts and "cần giờ sinh" in texts["su_nghiep.no_time"]


def test_synastry_reading():
    a, b = compute(CHARTS[0]), compute(CHARTS[3])
    syn = synastry.compare(a, b)
    assert set(syn["ptolemy"]["places"]) == {"sun", "moon", "asc", "lot"}
    paras = RS.build(syn, gender_a="male", gender_b="female")
    assert paras[0]["sources"] and "IV.7" in paras[0]["sources"][0]["label"]


def test_each_life_chapter_opens_with_a_plain_summary_that_rests_on_evidence(readings):
    from western.reading.argue import SUMMARIES
    for b, r in zip(CHARTS, readings):
        for ch in r["chapters"]:
            if ch["id"] not in SUMMARIES or (b.hour is None and ch["id"] in ("su_nghiep", "tai_chinh", "quan_he", "gia_dinh", "dinh_huong")):
                continue
            first = ch["paragraphs"][0]
            assert first["layer"] == "summary" and first["level"] == "overview" and first["evidence"], (ch["id"], first["id"])
            assert any(k.startswith("verdict:") for k in first["keys"]) and first["steps"][0].startswith("Cách gom")
            # the summary speaks to the reader first: it does not open with a book or an author
            assert not first["text"].startswith(("Theo ", "Với Lilly", "Lilly", "Ptolemy", "Valens", "Alan Leo")), first["text"][:60]
