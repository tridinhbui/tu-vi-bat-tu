"""Generates engine/data/pack_planb.json: readings of seven thin palaces (Huynh Đệ, Tật Ách, Tử Tức, Điền Trạch, Phu Thê, Nô Bộc, Phụ Mẫu)
mined from Tử Vi Khảo Luận (KL), Tử Vi Thực Hành (TH) and Tử Vi Đẩu Số Toàn Thư (TT) — plan (b), docs/audit/PLAN-B-MINING-2026-10-25.md.

Input: tools/data/planb_{kl,th,tt}.json, one entry per book line, each with its printed page and a verbatim quote that
engine/tests/test_planb.py finds on that page (skipped when the book is absent); TH lines were read on the page image (TH's text layer
scrambles line order) and the full line is in the entry's note. Conditions are the book's, never wider. Before an entry becomes a rule it is
compared with every verified rule already loaded (tools/interpret/planb_overlap.py): an entry with the same conditions and the same concept
as an existing rule adds nothing to a reading and is left out (recorded in quotes_planb.json "duplicates"); an entry with the same
conditions and the opposite side on the same facet is kept, and kg_draft.ts records the pair as two books that disagree.
Left out by the miners (see each file's pages_read): appearance, illness names and any health verdict (Tật Ách keeps only what stars do
there), death, khắc, prison, theft, sexual conduct, events, hạn lines, rejected or unsettled lines.
    .venv/bin/python tools/build_planb_pack.py"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "engine" / "data"
SRC = {"KL": "SRC_KHAO_LUAN", "TH": "SRC_THUC_HANH", "TT": "SRC_TOAN_THU"}
SCHOOL = {"KL": "khao_luan", "TH": "thuc_hanh", "TT": "toan_thu"}
BOOK_VI = {"KL": "Tử Vi Khảo Luận", "TH": "Tử Vi Thực Hành", "TT": "Tử Vi Đẩu Số Toàn Thư"}
PALACES = ["Huynh Đệ", "Tật Ách", "Tử Tức", "Điền Trạch", "Phu Thê", "Nô Bộc", "Phụ Mẫu"]
DROP = set(json.loads((ROOT / "tools" / "data" / "planb_overlap.json").read_text("utf-8"))["duplicates"]) if (ROOT / "tools" / "data" / "planb_overlap.json").exists() else set()

ENTRIES = []
for b in ("kl", "th", "tt"):
    p = ROOT / "tools" / "data" / f"planb_{b}.json"
    if p.exists():
        ENTRIES += json.loads(p.read_text("utf-8"))["entries"]

def expand(c):
    """'giap' (the two flanking palaces hold the pair, either way round) -> engine DSL; everything else is engine DSL already."""
    if isinstance(c, dict) and "giap" in c:
        a, b = c["giap"]
        side = lambda s, t: {"fact": f"palace.rel.flank_{s}_stars", "operator": "contains", "value": t}
        return {"any": [{"all": [side("prev", a), side("next", b)]}, {"all": [side("prev", b), side("next", a)]}]}
    if isinstance(c, dict):
        return {k: ([expand(x) for x in v] if k in ("all", "any", "count") else expand(v) if k == "not" else v) for k, v in c.items()}
    return c


slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_").replace("-", "_")
rules, claims, links, quotes, dups = [], {}, {}, [], []
for e in ENTRIES:
    assert e["palace"] in PALACES, e
    assert e["book"] in SRC, e
    eff = e["effect"] if e["effect"] in ("support", "limit") else "neutral"
    rid = f"TV_PB_{e['book']}_{slug(e['palace'])}_{slug(e['id'])}"
    if rid in DROP:
        dups.append({"rule": rid, "page": e["page"], "quote": e["quote"]})
        continue
    claim = "pb_" + rid[len("TV_PB_"):].lower()
    rules.append({"id": rid, "system": "tu_vi", "schoolId": SCHOOL[e["book"]], "category": "planb_cung",
                  "description": f"{BOOK_VI[e['book']]} (paraphrased), cung {e['palace']}: {e['reading']} [{e['book']} p.{e['page']}]",
                  "conditions": {"all": [{"fact": "palace.name", "value": e["palace"]}] + [expand(c) for c in e["conds"]]},
                  "consequences": [{"kind": "finding", "claim": claim, "effect": eff, "scope": "natal"}],
                  "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": [SRC[e["book"]]], "reviewStatus": "verified", "version": "0.1.0",
                  "subject": "palace"})
    claims[claim] = ("khuynh hướng " if eff == "support" else "hạn chế: " if eff == "limit" else "") + e["reading"]
    if eff == "limit":
        claims["limit:" + claim] = "hạn chế: " + e["reading"]
    if e.get("concepts"):
        links[rid] = {"asserts": [{"concept": c, "stance": s} for c, s in e["concepts"]], "src": "manual", "review": "draft"}
    quotes.append({"rule": rid, "book": e["book"], "page": e["page"], "quote": e["quote"]})
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), sorted({i for i in ids if ids.count(i) > 1})
json.dump({"sources": [], "rules": rules}, open(D / "pack_planb.json", "w"), ensure_ascii=False, indent=1)
json.dump({"note": "page quotes of pack_planb.json (tools/build_planb_pack.py), checked by engine/tests/test_planb.py; 'duplicates' are mined lines left out because a loaded rule already says the same on the same conditions",
           "quotes": quotes, "duplicates": dups}, open(D / "quotes_planb.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
cur = {k: v for k, v in cur.items() if not (k.startswith("pb_") or k.startswith("limit:pb_"))}
cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
man = json.loads((D / "kg" / "rule_concepts.manual.json").read_text("utf-8"))
man["entries"] = {k: v for k, v in man["entries"].items() if not k.startswith("TV_PB_")}
man["entries"].update(links)
json.dump(man, open(D / "kg" / "rule_concepts.manual.json", "w"), ensure_ascii=False, indent=1)
print(len(rules), "rules,", len(links), "linked,", len(dups), "duplicates left out")
