"""pack_tarot_pkt.json (tools/build_tarot_pack.py): the committed pack is what the builder makes from tools/data/tarot_pkt_entries.json,
every entry names a real card, an orientation, a page, the book's line and a Vietnamese text free of the banned wording, and (when the
PDF of The Pictorial Key to the Tarot is present and its page offset is set) every quote is on its page."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build_tarot_pack as b  # noqa: E402

PACK = json.loads((ROOT / "engine" / "data" / "tarot" / "pack_tarot_pkt.json").read_text("utf-8"))


def test_builder_reads_the_shared_banned_list():
    pats = b.banned()
    assert len(pats) >= 14
    assert any(p.search("định mệnh") for p in pats) and any(p.search("sẽ bị phạt") for p in pats)


def test_pack_is_up_to_date_and_well_formed():
    entries = b.SRC["entries"]
    assert len(PACK["entries"]) == len(entries)
    assert PACK["source"] == b.SOURCE
    assert not b.problems(PACK["entries"], b.banned())


def test_builder_refuses_bad_entries():
    good = {"card": "M00", "orientation": "upright", "page": 153, "quote_en": "Folly, mania", "text_vi": "Sự dại dột"}
    assert not b.problems([good], b.banned())
    assert b.problems([good, good], b.banned())                                         # duplicate
    assert b.problems([{**good, "card": "X1"}], b.banned())
    assert b.problems([{**good, "page": None}], b.banned())
    assert b.problems([{**good, "text_vi": "Bạn chắc chắn gặp may"}], b.banned())


@pytest.mark.skipif(not (b.pdf_path() and isinstance(b.SRC.get("pdf_offset"), int) and b.SRC["entries"]),
                    reason="The Pictorial Key to the Tarot PDF, its page offset or the entries are not present yet")
def test_quotes_are_on_their_page():
    assert not b.quotes_off_page(b.SRC["entries"], b.pdf_path(), b.SRC["pdf_offset"])
