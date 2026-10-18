#!/usr/bin/env python3
"""Apply tools/data/evidence_corrections.json to engine/data packs (idempotent).

The pack generators (tools/build_*_pack.py) rewrite whole pack files, so run this AFTER any generator; tests/test_source_evidence.py
fails if a correction is missing. Touched: status / page / description notes / claim *wording* of claims used by a single rule.
Conditions and claim ids never change here (those would change which findings fire: see docs/source_audit_fix_impact.csv).

Entries:  description_replace, description_append, set (pack fields), claims {claim_id: new text}.
Block 'description_tag': appends one note to every rule whose evidence verdict equals tag.verdict (and is not already tagged)."""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "engine" / "data"


def main():
    cfg = json.loads((ROOT / "tools" / "data" / "evidence_corrections.json").read_text("utf-8"))
    corr = cfg["corrections"]
    packs = {}

    def pack(name):
        if name not in packs:
            p = next(Path(x) for x in glob.glob(str(DATA / "**" / name), recursive=True))
            packs[name] = (p, json.loads(p.read_text("utf-8")))
        return packs[name][1]

    changed = 0
    for c in corr:
        d = pack(c["pack"])
        r = next(x for x in d["rules"] if x["id"] == c["rule_id"])
        if "description_replace" in c:
            old, new = c["description_replace"]
            if old in r["description"]:
                r["description"] = r["description"].replace(old, new); changed += 1
            elif new not in r["description"]:
                sys.exit(f"{c['rule_id']}: neither old nor new text found")
        if "description_append" in c and c["description_append"].strip() not in r["description"]:
            r["description"] += c["description_append"]; changed += 1
        for k, v in c.get("set", {}).items():
            if r.get(k) != v:
                r[k] = v; changed += 1
    # description tag for 'partly' findings
    tag = cfg.get("description_tag")
    if tag:
        ev = json.loads((DATA / "source_evidence.json").read_text("utf-8"))["entries"]
        want = {e["rule_id"] for e in ev if e["verdict"] == tag["verdict"]}
        for f in glob.glob(str(DATA / "**" / "pack_*.json"), recursive=True):
            name = Path(f).name
            d = pack(name)
            for r in d["rules"]:
                if r["id"] in want and tag["text"].strip() not in r["description"]:
                    r["description"] += tag["text"]; changed += 1
    for p, d in packs.values():
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), "utf-8")
    # claim wording (claims_vi.json is shared, so only claims used by exactly one rule may be reworded)
    claims_p = DATA / "claims_vi.json"
    claims = json.loads(claims_p.read_text("utf-8"))
    use = {}
    for f in glob.glob(str(DATA / "**" / "pack_*.json"), recursive=True):
        for r in json.loads(Path(f).read_text("utf-8"))["rules"]:
            for x in r.get("consequences", []):
                if isinstance(x, dict) and x.get("claim"):
                    use.setdefault(x["claim"], set()).add(r["id"])
    for c in corr:
        for k, v in c.get("claims", {}).items():
            base = k.removeprefix("limit:")
            if use.get(base, set()) != {c["rule_id"]}:
                sys.exit(f"claim {base} is shared by {sorted(use.get(base, []))}: refusing to reword it")
            if claims.get(k) != v:
                claims[k] = v; changed += 1
    claims_p.write_text(json.dumps(claims, ensure_ascii=False, indent=1), "utf-8")
    print("corrections applied:", changed)


if __name__ == "__main__":
    main()
