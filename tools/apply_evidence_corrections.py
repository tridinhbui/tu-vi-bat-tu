#!/usr/bin/env python3
"""Apply tools/data/evidence_corrections.json to engine/data packs (idempotent).

The pack generators (tools/build_*_pack.py) rewrite whole pack files, so run this AFTER any generator; tests/test_source_evidence.py
fails if a correction is missing. Only status / page / description notes are touched: conditions and claims never change here."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "engine" / "data"


def main():
    corr = json.loads((ROOT / "tools" / "data" / "evidence_corrections.json").read_text("utf-8"))["corrections"]
    by_pack = {}
    for c in corr:
        by_pack.setdefault(c["pack"], []).append(c)
    changed = 0
    for pack, items in by_pack.items():
        p = DATA / pack
        d = json.loads(p.read_text("utf-8"))
        idx = {r["id"]: r for r in d["rules"]}
        for c in items:
            r = idx[c["rule_id"]]
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
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), "utf-8")
    print("corrections applied:", changed)


if __name__ == "__main__":
    main()
