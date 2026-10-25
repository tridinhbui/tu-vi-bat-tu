"""Knowledge base loader: rule records and tables in engine/data/horary/*.json (schema: docs/HORARY-KB.md)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "horary"
WORKS = {
    "LILLY": "William Lilly, Christian Astrology (London, 1647)",
    "BONATUS_1886": "Guido Bonatti, 146 Considerations, tr. H. Coley (1676), reprint 1886",
    "BONATUS_1676": "Anima Astrologiae (London, 1676)",
    "PTOLEMY": "Ptolemy, Tetrabiblos, tr. J. M. Ashmand (1822)",
}


@lru_cache(maxsize=None)
def _file(name: str) -> dict:
    p = DATA / name
    return json.loads(p.read_text()) if p.exists() else {"rules": [], "tables": {}}


@lru_cache(maxsize=1)
def rules() -> dict[str, dict]:
    out = {}
    for f in sorted(DATA.glob("*.json")):
        for r in _file(f.name).get("rules", []):
            out[r["id"]] = r | {"_file": f.name}
    return out


def rule(rid: str) -> dict | None:
    return rules().get(rid)


def tables() -> dict:
    return _file("tables_lilly.json").get("tables", {})


def cite(rid: str) -> list[dict]:
    """Short citations of a rule: [{work, page, label}] for traces and the 'căn cứ' panel."""
    r = rule(rid)
    if not r:
        return []
    return [{"work": s["work"], "page": s.get("page"), "label": f"{WORKS.get(s['work'], s['work'])}, tr. {s.get('page')}"}
            for s in r.get("sources", [])]


def lower(x):
    """Planet names in the tables are capitalised English; the engine uses western's lowercase ids."""
    if isinstance(x, str):
        return x.lower().replace(" ", "_")
    if isinstance(x, list):
        return [lower(v) for v in x]
    if isinstance(x, dict):
        return {k: lower(v) for k, v in x.items()}
    return x
