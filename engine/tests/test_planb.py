"""pack_planb.json (tools/build_planb_pack.py, plan (b) KL/TH/TT mining of seven thin palaces): every rule has a quote on its printed page
(skipped when the book is absent), a page cite and a claim, the pack is loaded, and no rule repeats an existing rule on the same conditions."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import book_text  # noqa: E402

from tvbt.knowledge.loader import load_all  # noqa: E402

PACK = json.loads((ROOT / "engine" / "data" / "pack_planb.json").read_text("utf-8"))["rules"]
Q = json.loads((ROOT / "engine" / "data" / "quotes_planb.json").read_text("utf-8"))
CLAIMS = json.loads((ROOT / "engine" / "data" / "claims_vi.json").read_text("utf-8"))
RULES, _ = load_all()


def test_every_rule_has_a_quote_a_page_cite_and_a_claim():
    q = {x["rule"]: x for x in Q["quotes"]}
    assert {r["id"] for r in PACK} == set(q)
    for r in PACK:
        x = q[r["id"]]
        assert f"[{x['book']} p.{x['page']}]" in r["description"], r["id"]
        assert r["consequences"][0]["claim"] in CLAIMS, r["id"]
        assert r["conditions"]["all"][0]["value"] in {"Huynh Đệ", "Tật Ách", "Tử Tức", "Điền Trạch", "Phu Thê", "Nô Bộc", "Phụ Mẫu"}


def test_pack_is_loaded_and_duplicates_are_not():
    ids = {r.id for r in RULES}
    assert {r["id"] for r in PACK} <= ids
    assert not ({d["rule"] for d in Q["duplicates"]} & ids)


@pytest.mark.parametrize("book", ["KL", "TH", "TT"])
def test_quotes_are_on_their_page(book):
    if not book_text.available(book):
        pytest.skip(f"{book} PDF not present")
    bad = [x for x in Q["quotes"] if x["book"] == book and not book_text.quote_on_page(book, x["page"], x["quote"])]
    assert not bad, bad[:5]
