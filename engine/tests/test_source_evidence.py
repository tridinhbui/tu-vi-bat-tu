"""Source-evidence file (data/source_evidence.json, source_evidence_web.json): schema, links to rules, applied corrections,
and (when the books are on disk) that every machine-verified quote really sits on its page."""
import glob
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "engine" / "data"
sys.path.insert(0, str(ROOT / "tools"))

VERDICTS = {"faithful", "partly", "unsupported_on_page", "misread", "cannot_verify"}


def rules():
    out = {}
    for f in glob.glob(str(DATA / "**" / "pack_*.json"), recursive=True):
        for r in json.loads(Path(f).read_text("utf-8"))["rules"]:
            out[r["id"]] = r
    return out


EV = json.loads((DATA / "source_evidence.json").read_text("utf-8"))["entries"]


def test_every_entry_has_schema_and_a_real_rule():
    R = rules()
    seen = set()
    for e in EV:
        assert e["rule_id"] in R, e["rule_id"]
        assert e["rule_id"] not in seen
        seen.add(e["rule_id"])
        assert e["verdict"] in VERDICTS
        assert e["quote_verified"] in (True, None), f"{e['rule_id']}: quote not found on its page"
        if e["verdict"] != "faithful":
            assert e.get("issue") or e.get("override_note"), f"{e['rule_id']}: non-faithful verdict without an explanation"
        if e["quote_book"] == "ZZ":
            assert e.get("gloss_vi"), f"{e['rule_id']}: Chinese quote without a Vietnamese gloss"
        assert len(e["quote"].split()) <= 40 or e["quote_book"] == "ZZ"        # short quotations only


def test_sample_is_large_enough_and_findings_are_real():
    assert len(EV) >= 200
    bad = [e for e in EV if e["verdict"] in ("misread", "unsupported_on_page")]
    assert bad, "audit found nothing wrong: suspicious"          # the audit did find real defects; keep them on record
    assert sum(e["quote_verified"] is None for e in EV) <= 10     # image-read quotes stay rare


def test_corrections_are_applied():
    R = rules()
    for c in json.loads((ROOT / "tools" / "data" / "evidence_corrections.json").read_text("utf-8"))["corrections"]:
        r = R[c["rule_id"]]
        if "description_replace" in c:
            assert c["description_replace"][1] in r["description"], c["rule_id"]
            assert c["description_replace"][0] not in r["description"], c["rule_id"]
        if "description_append" in c:
            assert c["description_append"].strip() in r["description"], c["rule_id"]
        for k, v in c.get("set", {}).items():
            assert r[k] == v, c["rule_id"]


def test_misread_rules_are_not_presented_as_verified():
    R = rules()
    for e in EV:
        if e["verdict"] == "misread":
            assert R[e["rule_id"]]["reviewStatus"] == "draft", e["rule_id"]


def test_quotes_sit_on_their_pages():
    bt = pytest.importorskip("fitz", reason="PyMuPDF needed to read the books") and __import__("show_page")
    import book_text
    try:
        for b in ("KL", "TH", "TT"):
            if not book_text.available(b):
                pytest.skip("books not on disk ($TVBT_BOOKS_DIR)")
    except Exception:
        pytest.skip("books not on disk")
    from build_source_evidence import fold_q
    for e in EV:
        if e["quote_verified"] is True:
            page = bt.text(e["quote_book"], int(e["quote_page"]))
            assert fold_q(e["quote"]) in fold_q(page), (e["rule_id"], e["quote_page"])


def test_web_evidence_covers_all_tbct_definitions():
    W = json.loads((DATA / "source_evidence_web.json").read_text("utf-8"))
    geju = json.loads((DATA / "bazi_deep" / "geju_defs.json").read_text("utf-8"))["defs"]
    pats = json.loads((DATA / "bazi_deep" / "patterns_defs.json").read_text("utf-8"))["defs"]
    ids = {e["rule_id"] for e in W["entries"]}
    assert ids == {f"geju:{k}" for k in geju} | {f"pattern:{k}" for k in pats}
    for e in W["entries"]:
        assert e["quote_url"].startswith("https://") and re.search(r"[一-鿿]", e["quote"])
        assert e["verdict"] in {"faithful", "partly", "not_in_text", "misread", "cannot_verify"}
    # the definitions are still unverified drafts: the comparison must not have promoted them
    assert json.loads((DATA / "bazi_deep" / "geju_defs.json").read_text("utf-8"))["_status"] == "draft"
