"""engine/data/kg/star_nature.json: every star-nature and palace-relation entry quotes Tử Vi Khảo Luận on the page it cites (skipped when the
book is absent), names a star the chart can hold and a domain the depth layer reads."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import book_text  # noqa: E402

KB = json.loads((ROOT / "engine" / "data" / "kg" / "star_nature.json").read_text("utf-8"))
USE = {"career", "money", "marriage", "property", "self", "allies", "travel", "fortune", "children", "siblings", "parents", "health"}


def test_shape():
    ids = [e["id"] for e in KB["entries"] + KB["relations"]]
    assert len(ids) == len(set(ids))
    for e in KB["entries"]:
        assert e["star"] and e["text"] and e["quote"] and isinstance(e["page"], int), e["id"]
        assert set(e["use"]) <= USE and e["use"], e["id"]
        assert not e["text"].endswith("."), e["id"]


@pytest.mark.skipif(not book_text.available("KL"), reason="Tử Vi Khảo Luận PDF not present")
def test_quotes_on_page():
    bad = [(e["id"], e["page"]) for e in KB["entries"] + KB["relations"] if not book_text.quote_on_page(e.get("book", "KL"), e["page"], e["quote"])]
    assert not bad, bad
