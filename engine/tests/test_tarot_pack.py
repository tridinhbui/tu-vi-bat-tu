"""pack_tarot_pkt.json (tools/build_tarot_pack.py): the committed pack is what the builder makes from tools/data/tarot_pkt_entries.json;
every entry names a real card, an orientation, a page, Waite's words (at least 4) and a Vietnamese paraphrase free of the banned wording;
every quote is on its printed page of the 1916 issue (PictorialKeyToTheTarot.pdf, PDF page = printed + 8; skipped only when the book is
absent); all 78 cards have upright readings and all but the Two of Cups (Waite gives none) have reversed ones."""
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build_tarot_pack as b  # noqa: E402

PACK = json.loads((ROOT / "engine" / "data" / "tarot" / "pack_tarot_pkt.json").read_text("utf-8"))
DECK = [c["id"] for c in json.loads((ROOT / "engine" / "data" / "tarot" / "deck.json").read_text("utf-8"))["cards"]]
SOURCES = {s["id"]: s for s in json.loads((ROOT / "engine" / "data" / "sources.json").read_text("utf-8"))["sources"]}


def test_builder_reads_the_shared_banned_list():
    pats = b.banned()
    assert len(pats) >= 14
    assert any(p.search("định mệnh") for p in pats) and any(p.search("sẽ bị phạt") for p in pats)


def test_pack_is_up_to_date_and_well_formed():
    entries = b.SRC["entries"]
    assert len(PACK["entries"]) == len(entries)
    assert PACK["source"] == b.SOURCE and PACK["source"]["cite"] == "PKT (1916)"
    assert {(e["card"], e["orientation"], e["quote_en"]) for e in PACK["entries"]} == {(e["card"], e["orientation"], e["quote_en"]) for e in entries}
    assert not b.problems(entries, b.banned())
    assert b.SRC["pdf_offset"] == 8


def test_edition_is_recorded_in_sources():
    s = SOURCES["SRC_PKT"]
    assert s["verified"] and "1916" in s["edition"] and "de Laurence" in s["author"] and "illustratedkeyto01dela" in s["edition"]
    assert "NOT the 1911" in s["edition"]


def test_every_card_is_covered():
    n = Counter((e["card"], e["orientation"]) for e in PACK["entries"])
    assert all(n[(c, "upright")] >= 1 for c in DECK)
    assert [c for c in DECK if not n[(c, "reversed")]] == ["C02"]
    assert all(2 <= n[(c, "upright")] + n[(c, "reversed")] <= 8 for c in DECK)


def test_framing_is_a_suggestion_and_left_out_meanings_are_noted():
    for e in b.SRC["entries"]:
        assert e["text_vi"].startswith(("Theo Waite, lá này", "Khi lá ngược", "Waite ghi thêm", "Trong phần tả lá bài")), e
        assert "gợi đến" in e["text_vi"] or "ý nghĩa vẫn" in e["text_vi"] or "các cách đọc khác nhau" in e["text_vi"], e
    notes = " ".join(e.get("note", "") for e in b.SRC["entries"])
    for cat in ("death", "illness", "pregnancy", "legal", "sexual", "crime", "prison", "accidents", "financial", "certain"):
        assert cat in notes, cat


def test_builder_refuses_bad_entries():
    good = {"card": "M00", "orientation": "upright", "page": 147, "quote_en": "Folly, mania, extravagance, intoxication",
            "text_vi": "Theo Waite, lá này gợi đến sự dại dột.", "category": "divinatory"}
    assert not b.problems([good], b.banned())
    assert b.problems([good, good], b.banned())                                         # the same quote twice
    assert b.problems([{**good, "card": "X1"}], b.banned())
    assert b.problems([{**good, "page": None}], b.banned())
    assert b.problems([{**good, "quote_en": "Folly, mania"}], b.banned())
    assert b.problems([{**good, "category": "guess"}], b.banned())
    assert b.problems([{**good, "text_vi": "Bạn chắc chắn gặp may"}], b.banned())
    assert b.words("Riot, quarrel, dispute, … defeat") == 4 and b.parts("a … b c") == ["a", "b c"]


@pytest.mark.skipif(not b.pdf_path(), reason="PictorialKeyToTheTarot.pdf not present")
def test_quotes_are_on_their_page():
    bad, fuzzy = b.quotes_off_page(b.SRC["entries"], b.pdf_path(), b.SRC["pdf_offset"])
    assert not bad, bad
    assert len(fuzzy) <= 15, fuzzy                       # OCR-tolerant matches stay the exception
    # a quote is not found on the wrong page
    e = next(x for x in b.SRC["entries"] if x["card"] == "M00" and x["page"] == 147)
    assert not b.check_quote({**e, "page": 146}, b.pdf_path(), b.SRC["pdf_offset"])[0]
