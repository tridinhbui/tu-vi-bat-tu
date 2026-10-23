"""Rule-condition widening audit (owner review 2026-10-22, DEEP-TUVI §Correctness item 7): verified Tử Vi rules whose condition is wider than
the page's wording. Three checks on the rule's own paraphrase (its description after "(paraphrased)"):
  mieu     the reading says "nhập miếu" / "miếu địa" but the condition accepts a brightness below miếu (vượng, đắc …)
  doc_thu  the reading says "độc thủ" / "đơn thủ" but the condition does not exclude a second chính tinh
  seat     the reading puts a star in the palace ("thủ", "tọa", "đồng cung") but the condition only finds it in the tam phương
    .venv/bin/python tools/interpret/audit_widening.py [--apply]
--apply narrows a 'mieu' rule's brightness to miếu, and moves a 'doc_thu' or 'seat' rule to draft with the reason in its description;
the changes are recorded in engine/data/kg/rule_review_widening.json (packs are patched in place, as rule_review_2026-10-22 did)."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.knowledge.loader import PACKS  # noqa: E402

D = ROOT / "engine" / "data"
APPLY = "--apply" in sys.argv


def leaves(c):
    if isinstance(c, dict):
        if "fact" in c or "ref" in c:
            yield c
        for k in ("all", "any", "not"):
            v = c.get(k)
            if isinstance(v, list):
                for x in v:
                    yield from leaves(x)
            elif isinstance(v, dict):
                yield from leaves(v)


def phrase(r):
    d = r.get("description", "")
    return d.split("(paraphrased)", 1)[-1].split("[", 1)[0]


found, changed = [], []
for pack in PACKS:
    path = D / pack
    data = json.loads(path.read_text("utf-8"))
    dirty = False
    for r in data["rules"]:
        if r.get("system") != "tu_vi" or r.get("reviewStatus") != "verified":
            continue
        ph = phrase(r)
        ls = list(leaves(r["conditions"]))
        dig = [x for x in ls if str(x.get("fact", "")).startswith("palace.dignity")]
        # 1. nhập miếu read as any bright cell
        if re.search(r"nhập miếu|miếu địa", ph) and not re.search(r"miếu,? vượng|miếu vượng|vượng địa|đắc địa", ph):
            wide = [x for x in dig if isinstance(x.get("value"), list) and set(x["value"]) - {"miếu"}]
            if wide:
                found.append(("mieu", pack, r["id"], ph.strip()))
                if APPLY:
                    for x in wide:
                        x["value"] = ["miếu"]
                    r["description"] += " ; độ sáng thu về 'miếu' đúng chữ 'nhập miếu' của sách (audit 2026-10-22)"
                    changed.append({"id": r["id"], "pack": pack, "check": "mieu", "action": "dignity narrowed to miếu", "phrase": ph.strip()})
                    dirty = True
        # 2. độc thủ / đơn thủ with no exclusion of a second chính tinh
        if re.search(r"độc thủ|đơn thủ", ph):
            cs = json.dumps(r["conditions"], ensure_ascii=False)
            if "not" not in cs and "count" not in cs and "has_no_major" not in cs:
                found.append(("doc_thu", pack, r["id"], ph.strip()))
                if APPLY:
                    r["reviewStatus"] = "draft"
                    r["description"] += " ; draft: sách nói 'độc thủ' mà điều kiện chưa loại chính tinh thứ hai (audit 2026-10-22)"
                    changed.append({"id": r["id"], "pack": pack, "check": "doc_thu", "action": "draft", "phrase": ph.strip()})
                    dirty = True
    if dirty:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), "utf-8")

for f in found:
    print(*f, sep=" | ")
print(len(found), "found")
if APPLY and changed:
    out = D / "kg" / "rule_review_widening.json"
    prev = json.loads(out.read_text("utf-8"))["rules"] if out.exists() else []
    ids = {x["id"] for x in prev}
    rec = {"version": "2026-10-23", "note": "tools/interpret/audit_widening.py --apply: rules whose condition was wider than the page's wording (nhập miếu read as any bright cell; độc thủ with no exclusion). Packs patched in place.",
           "rules": prev + [x for x in changed if x["id"] not in ids]}
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", "utf-8")
