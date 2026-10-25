"""Plan (b): compare each mined entry (tools/data/planb_*.json) with the verified rules already in the knowledge, before it becomes a rule.
    .venv/bin/python tools/interpret/planb_overlap.py
Same conditions = the same condition tree once its leaves and lists are put in a canonical order (a 'not' stays a 'not', so "trừ Dần Thân"
and "ở Dần Thân" differ). Writes tools/data/planb_overlap.json:
  duplicates      entries whose conditions AND a concept equal an existing rule's: they add nothing a reading could say (left out of the pack)
  contradictions  entries whose conditions equal an existing rule's and whose side is the opposite on the same facet (kept; the books disagree)
  same_conditions entries with the conditions of an existing rule but other concepts (kept: another thing the books say of that placement)"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
K = json.loads((ROOT / "src" / "interpret" / "generated" / "knowledge.json").read_text("utf-8"))
CON = {c["id"]: c for c in K["concepts"]["concepts"]}
LINKS = K["kg"]["ruleConcepts"]
slug = lambda t: unicodedata.normalize("NFD", t.replace("Đ", "D").replace("đ", "d")).encode("ascii", "ignore").decode().upper().replace(" ", "_").replace("-", "_")


def canon(x):
    if isinstance(x, dict):
        if "all" in x or "any" in x:
            k = "all" if "all" in x else "any"
            items = sorted((canon(y) for y in x[k]), key=json.dumps)
            # a one-element group is its element; an 'all' inside an 'all' is flattened
            flat = []
            for it in items:
                flat += it["all"] if k == "all" and isinstance(it, dict) and "all" in it else [it]
            return flat[0] if len(flat) == 1 else {k: sorted(flat, key=json.dumps)}
        if "not" in x:
            return {"not": canon(x["not"])}
        return {k: (sorted(v, key=lambda y: json.dumps(y, ensure_ascii=False, sort_keys=True)) if isinstance(v, list) else v) for k, v in sorted(x.items())}
    if isinstance(x, list):
        return canon({"all": x})
    return x


def side(cid, stance):
    c = CON.get(cid)
    if not c or c["pol"] not in "+-":
        return None
    return c["pol"] if stance == "affirms" else ("-" if c["pol"] == "+" else "+")


index = {}
for r in K["rules"]:
    if r["reviewStatus"] == "verified":
        index.setdefault(json.dumps(canon(r["conditions"]), ensure_ascii=False, sort_keys=True), []).append(r["id"])

out = {"duplicates": [], "contradictions": [], "same_conditions": []}
for b in ("kl", "th", "tt"):
    p = ROOT / "tools" / "data" / f"planb_{b}.json"
    if not p.exists():
        continue
    for e in json.loads(p.read_text("utf-8"))["entries"]:
        rid = f"TV_PB_{e['book']}_{slug(e['palace'])}_{slug(e['id'])}"
        cond = {"all": [{"fact": "palace.name", "value": e["palace"]}] + e["conds"]}
        hits = index.get(json.dumps(canon(cond), ensure_ascii=False, sort_keys=True), [])
        if not hits:
            continue
        mine = {(c, s) for c, s in e.get("concepts", [])}
        dup = con = None
        for h in hits:
            theirs = {(a["concept"], a.get("stance", "affirms")) for a in LINKS.get(h, {}).get("asserts", [])}
            if {c for c, _ in mine} & {c for c, _ in theirs}:
                dup = h
                break
            fa = lambda c: CON.get(c, {}).get("facet")
            for c, s in mine:
                for c2, s2 in theirs:
                    if fa(c) == fa(c2) and side(c, s) and side(c2, s2) and side(c, s) != side(c2, s2):
                        con = (h, c, c2)
        if dup:
            out["duplicates"].append(rid)
        elif con:
            out["contradictions"].append({"rule": rid, "existing": con[0], "concepts": [con[1], con[2]], "page": f"{e['book']} p.{e['page']}", "reading": e["reading"]})
        else:
            out["same_conditions"].append({"rule": rid, "existing": hits})
(ROOT / "tools" / "data" / "planb_overlap.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", "utf-8")
print({k: len(v) for k, v in out.items()})
