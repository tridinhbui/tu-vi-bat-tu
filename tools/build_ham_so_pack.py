"""Generates data/pack_ham_so.json: Tử Vi Hàm Số (Nguyễn Phát Lộc, Sài Gòn 1972), Quyển Nhì pp.84-233 — the readings of each chính
tinh and phụ tinh: tính tình by the star's brightness, công danh / tài lộc, the bộ sao the book reads at Mệnh, and 'X ở các cung'.

Input: tools/data/ham_so_rules.json, hand-reviewed entries (one per book line or tight group of bullets), each with the printed page
and a verbatim quote that engine/tests/test_ham_so.py finds on that page of the PDF (skipped when the book is absent). The book's
'đắc địa / hãm địa' is read in the book's OWN table (engine/data/ham_so_dignity.json): a {"hs_dignity": star, "in": levels} leaf is
expanded into the branches that table prints for those levels; a branch the page prints twice (Thiên Lương Tý, Vũ Khúc Dần) or
leaves out (Thiên Lương Tỵ, Vũ Khúc Dậu) is in neither list, so such a rule does not fire there.
Left out on purpose (see the entries' review): appearance, body, illness, death, prison, theft, sexual conduct, every hạn / vận
line, marriage and children events, lines the author quotes only to reject, lines whose condition the chart facts cannot test.
Entries marked "use": "reference" are kept in the data but not made rules: a phụ tinh's (or the book's star group's) general meaning
at Mệnh with no other condition, and the Âm Dương thuận / nghịch lý line the author calls a first, non-decisive factor (p.30). They fire
on a large share of all charts (Quang Quý 44 %, Tứ Đức 26 %, Tam giải 25 %), so as Mệnh readings they would say little about one chart
and crowd out what does (the author himself weighs chính tinh above phụ tinh, p.49); they stay as star meanings for later use.
    .venv/bin/python tools/build_ham_so_pack.py"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "engine" / "data"
SRC = "SRC_HAM_SO"
ENTRIES = [e for e in json.loads((ROOT / "tools" / "data" / "ham_so_rules.json").read_text("utf-8"))["entries"] if e.get("use") != "reference"]
DIG = json.loads((D / "ham_so_dignity.json").read_text("utf-8"))
TABLE = {**DIG["stars"], **DIG["aux"]}
PALACES = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]
HOA = {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"}


def hs_branches(star, levels):
    t = TABLE[star]
    bad = set(t.get("conflicts", {}))
    out = []
    for lv in levels:
        assert lv in DIG["levels"], lv
        out += [b for b in t.get(lv, []) if b not in bad and b not in out]
    return out


def expand(c):
    """The entry DSL -> the engine DSL (dsl.py / dsl.ts)."""
    if "hs_dignity" in c:
        star, levels = c["hs_dignity"], c["in"]
        hoa = star in HOA
        on = {"fact": "palace.tu_hoa" if hoa else "palace.own_stars", "operator": "contains", "value": star}
        brs = hs_branches(star, levels)
        assert brs, c
        return {"all": [on, {"fact": "palace.branch", "operator": "in", "value": brs}]}
    if "giap" in c:
        a, b = c["giap"]
        side = lambda s, t: {"fact": f"palace.rel.flank_{s}_stars", "operator": "contains", "value": t}
        return {"any": [{"all": [side("prev", a), side("next", b)]}, {"all": [side("prev", b), side("next", a)]}]}
    if "any" in c:
        return {"any": [expand(x) for x in c["any"]]}
    if "all" in c:
        return {"all": [expand(x) for x in c["all"]]}
    if "not" in c:
        return {"not": expand(c["not"])}
    assert "fact" in c, c
    return c


slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_").replace("-", "_")
rules, claims, links, quotes = [], {}, {}, []
for e in ENTRIES:
    assert e["palace"] in PALACES, e
    assert e["effect"] in ("support", "limit"), e
    rid = f"TV_HS_{slug(e['star'])}_{slug(e['palace'])}_{e['id']}"
    claim = "hs_" + rid[len("TV_HS_"):].lower()
    menh = e["palace"] == "Mệnh"
    rules.append({"id": rid, "system": "tu_vi", "schoolId": "ham_so", "category": "hs_menh" if menh else "hs_sao_cung",
                  "description": f"Tử Vi Hàm Số, ý nghĩa sao {e['star']} (paraphrased), cung {e['palace']}: {e['reading']} [HS p.{e['page']}]",
                  "conditions": {"all": [{"fact": "palace.name", "value": e["palace"]}] + [expand(c) for c in e["conds"]]},
                  "consequences": [{"kind": "finding", "claim": claim, "effect": e["effect"], "scope": "natal"}],
                  "exceptions": [], "conflictsWith": [], "priority": 3, "sourceIds": [SRC], "reviewStatus": "verified", "version": "0.1.0",
                  "subject": "palace"})
    claims[claim] = ("khuynh hướng " if e["effect"] == "support" else "hạn chế: ") + e["reading"]
    if e["effect"] == "limit":
        claims["limit:" + claim] = "hạn chế: " + e["reading"]
    if e.get("concepts"):
        links[rid] = {"asserts": [{"concept": c, "stance": s} for c, s in e["concepts"]], "src": "manual", "review": "draft"}
    quotes.append({"rule": rid, "page": e["page"], "quote": e["quote"]})
ids = [r["id"] for r in rules]
assert len(ids) == len(set(ids)), sorted({i for i in ids if ids.count(i) > 1})
# The Mệnh readings are staged (2026-10-24): engine/data/experimental/pack_ham_so_menh.json, not in the loader's PACKS. Loaded, they
# crowd the Mệnh chapter (about 24 more firings per chart) and move the corpus base rates every Mệnh measure is read against; they
# go in as their own step with the Mệnh chapter tuned for them. Until then they get no claim and no KG link (kg_draft.ts refuses a link
# to a rule it does not know); their quotes are still checked.
menh = [r for r in rules if r["category"] == "hs_menh"]
json.dump({"sources": [], "rules": [r for r in rules if r["category"] != "hs_menh"]}, open(D / "pack_ham_so.json", "w"), ensure_ascii=False, indent=1)
json.dump({"note": "STAGED, not loaded (tools/build_ham_so_pack.py): the Mệnh readings of Tử Vi Hàm Số", "sources": [], "rules": menh},
          open(D / "experimental" / "pack_ham_so_menh.json", "w"), ensure_ascii=False, indent=1)
off = {r["id"] for r in menh}
claims = {k: v for k, v in claims.items() if k.split(":")[-1] not in {r["consequences"][0]["claim"] for r in menh}}
links = {k: v for k, v in links.items() if k not in off}
json.dump({"note": "page quotes of pack_ham_so.json (tools/build_ham_so_pack.py), checked by engine/tests/test_ham_so.py; printed pages (PDF = printed + 1)",
           "quotes": quotes}, open(D / "quotes_ham_so.json", "w"), ensure_ascii=False, indent=1)
cur = json.loads((D / "claims_vi.json").read_text("utf-8"))
cur = {k: v for k, v in cur.items() if not (k.startswith("hs_") or k.startswith("limit:hs_"))}
cur.update(claims)
json.dump(cur, open(D / "claims_vi.json", "w"), ensure_ascii=False, indent=1)
man = json.loads((D / "kg" / "rule_concepts.manual.json").read_text("utf-8"))
man["entries"] = {k: v for k, v in man["entries"].items() if not k.startswith("TV_HS_")}
man["entries"].update(links)
json.dump(man, open(D / "kg" / "rule_concepts.manual.json", "w"), ensure_ascii=False, indent=1)
print(len(rules), "rules,", len(links), "linked")
