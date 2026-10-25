"""Generates engine/data/hoang_dao/pack.json and quotes.json: the readings of the twelve cung hoàng đạo (Western sun signs).

Input: tools/data/hoang_dao_rules.json, hand-reviewed entries (one per book line or tight group of lines), each with its printed page
and a verbatim English quote (6 words or more) that engine/tests/test_hoang_dao.py finds on that page of the PDF (tools/book_text.py,
books AL / CA / TB; skipped only while a PDF is absent). Owner's rule: no reading without a cited page, so the card and the sign pages
show only what this pack holds. Books (owner, 2026-10-25): Alan Leo "Astrology for All" (1910) for the character of each sign;
William Lilly "Christian Astrology" (1647) and Ptolemy "Tetrabiblos" (J. M. Ashmand's 1822 translation) only for a sign's
classification as the page states it (element / triplicity, cardinal / fixed / mutable, the planet whose house it is).

Entry topics: 'trait' (character, temperament, tendency), 'work' (the callings the author names), 'classification' (with `facts`:
element, modality, ruler). The pack also folds every sign's facts into one summary with all the pages that state each value; two
books giving different values for the same fact stop the build (a disagreement must be decided, not hidden).

Kept apart from the Tử Vi / Bát Tự rule packs on purpose: the output goes to engine/data/hoang_dao/ (a subfolder), not to
engine/data/pack_*.json, and is NOT in knowledge/loader.py PACKS, so the reasoning engine, the chapters and the base rates never see it.
Entries with "use": "reference" stay in the data but are not shown.
    .venv/bin/python tools/build_hoang_dao_pack.py   (then tools/build_site.py: the sign pages show the readings)"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.hoang_dao import SIGNS  # noqa: E402

OUT = ROOT / "engine" / "data" / "hoang_dao"
SRC = ROOT / "tools" / "data" / "hoang_dao_rules.json"
_SOURCES = {s["id"]: s for s in json.loads((ROOT / "engine" / "data" / "sources.json").read_text("utf-8"))["sources"]}
BOOKS = {  # book code -> engine/data/sources.json id, and the short name the cite shows ("[Alan Leo, tr. 13]")
    "AL": {"id": "SRC_ALAN_LEO_AFA", "short": "Alan Leo"},
    "CA": {"id": "SRC_LILLY_CA", "short": "Lilly"},
    "TB": {"id": "SRC_PTOLEMY_TETRABIBLOS", "short": "Ptolemy"},
}
for _b in BOOKS.values():
    _b.update(title=_SOURCES[_b["id"]]["title"], author=_SOURCES[_b["id"]]["author"], edition=_SOURCES[_b["id"]]["edition"])
SLUGS = [s[0] for s in SIGNS]
USES = ("reading", "reference")
TOPICS = ("trait", "work", "classification")
FACTS = {  # fact -> value -> Vietnamese label
    "element": {"fire": "Lửa", "earth": "Đất", "air": "Khí", "water": "Nước"},
    "modality": {"cardinal": "tiên phong (cardinal)", "fixed": "kiên định (fixed)", "mutable": "linh hoạt (mutable)"},
    "ruler": {"Sun": "Mặt Trời", "Moon": "Mặt Trăng", "Mercury": "Sao Thủy", "Venus": "Sao Kim", "Mars": "Sao Hỏa", "Jupiter": "Sao Mộc",
              "Saturn": "Sao Thổ"},
}
FACT_NAMES = {"element": "Nguyên tố", "modality": "Tính chất", "ruler": "Chủ tinh"}


def check(e: dict) -> list[str]:
    """Problems of one entry (empty list = fine)."""
    p = []
    for k in ("id", "sign", "book", "page", "topic", "quote", "reading", "use"):
        if e.get(k) in (None, ""):
            p.append(f"missing {k}")
    if e.get("sign") not in SLUGS:
        p.append(f"unknown sign {e.get('sign')!r}")
    if e.get("book") not in BOOKS:
        p.append(f"unknown book {e.get('book')!r} (AL, CA, TB)")
    if not isinstance(e.get("page"), int) or e.get("page", 0) < 1:
        p.append("page must be a positive int (printed page)")
    if e.get("use") not in USES:
        p.append(f"use must be one of {USES}")
    if e.get("topic") not in TOPICS:
        p.append(f"topic must be one of {TOPICS}")
    if len((e.get("quote") or "").split()) < 6:
        p.append("quote shorter than 6 words")
    for k, v in (e.get("facts") or {}).items():
        if v not in FACTS.get(k, {}):
            p.append(f"fact {k}={v!r} unknown")
    if e.get("facts") and e.get("topic") != "classification":
        p.append("facts only on a classification entry")
    if e.get("book") in ("CA", "TB") and e.get("topic") != "classification":
        p.append("Lilly and Ptolemy are used for classification only")
    r = e.get("reading") or ""
    if re.search(r"\bcung\b(?! hoàng đạo)", r, re.I):
        p.append("reading says 'cung' without 'hoàng đạo'")
    if re.search(r"\bAI\b", r):
        p.append("reading contains 'AI'")
    return p


def _rid(e: dict) -> str:
    return f"HD_{e['book']}_{e['sign']}_{e['id']}"


def build(entries: list[dict]) -> tuple[dict, dict]:
    bad = {e.get("id", "?"): check(e) for e in entries}
    bad = {k: v for k, v in bad.items() if v}
    assert not bad, bad
    keys = [(e["sign"], e["book"], e["id"]) for e in entries]
    assert len(keys) == len(set(keys)), "duplicate (sign, book, id)"
    order = lambda e: (SLUGS.index(e["sign"]), TOPICS.index(e["topic"]) if e["topic"] != "classification" else -1,
                       list(BOOKS).index(e["book"]), e["page"], e["id"])
    shown = sorted((e for e in entries if e["use"] == "reading"), key=order)
    cite = lambda e: {"book": e["book"], "source_id": BOOKS[e["book"]]["id"], "source_title": BOOKS[e["book"]]["title"],
                      "short": BOOKS[e["book"]]["short"], "page": e["page"]}
    readings = [{"id": _rid(e), "sign": e["sign"], "topic": e["topic"], **({"facts": e["facts"]} if e.get("facts") else {}),
                 **cite(e), "reading": e["reading"]} for e in shown]
    facts: dict[str, dict] = {}
    for e in shown:
        for k, v in (e.get("facts") or {}).items():
            slot = facts.setdefault(e["sign"], {}).setdefault(k, {"name": FACT_NAMES[k], "value": v, "label": FACTS[k][v], "cites": []})
            assert slot["value"] == v, f"{e['sign']} {k}: {slot['value']} vs {v} ({_rid(e)}): books disagree, decide before building"
            c = cite(e)
            if c not in slot["cites"]:
                slot["cites"].append(c)
    used = sorted({e["book"] for e in entries}, key=list(BOOKS).index)
    pack = {"note": "cung hoàng đạo readings (tools/build_hoang_dao_pack.py from tools/data/hoang_dao_rules.json); not a rule pack, not in the loader",
            "sources": [{"code": b, **BOOKS[b]} for b in used],
            "facts": {s: {k: facts[s][k] for k in FACT_NAMES if k in facts.get(s, {})} for s in SLUGS if s in facts},
            "readings": readings}
    quotes = {"note": "page quotes of every entry (shown and reference), checked by engine/tests/test_hoang_dao.py; printed pages (tools/book_text.py EN_PAGE_RANGES)",
              "quotes": [{"id": _rid(e), "book": e["book"], "page": e["page"], "quote": e["quote"]} for e in entries]}
    return pack, quotes


def main() -> None:
    entries = json.loads(SRC.read_text("utf-8"))["entries"]
    pack, quotes = build(entries)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=1) + "\n", "utf-8")
    (OUT / "quotes.json").write_text(json.dumps(quotes, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(len(pack["readings"]), "readings shown,", len(quotes["quotes"]), "quotes,", len(pack["facts"]), "signs with facts")


if __name__ == "__main__":
    main()
