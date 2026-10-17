#!/usr/bin/env python3
"""Export every non-faithful source-evidence entry as docs/source_audit_findings.csv (for the data owner to triage).

Columns: rule_id, book, page, verdict, status_now (pack), applied (what this audit already changed), issue, qualifier.
Nothing here changes a rule: conditions/claims are the data owner's call (it would change engine output)."""
import csv
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "engine" / "data"
R = {}
for f in glob.glob(str(DATA / "**" / "pack_*.json"), recursive=True):
    for r in json.loads(Path(f).read_text("utf-8"))["rules"]:
        R[r["id"]] = (r, Path(f).name)
corr = {c["rule_id"]: c for c in json.loads((ROOT / "tools" / "data" / "evidence_corrections.json").read_text("utf-8"))["corrections"]}
ev = json.loads((DATA / "source_evidence.json").read_text("utf-8"))["entries"]
web = json.loads((DATA / "source_evidence_web.json").read_text("utf-8"))["entries"]
order = {"misread": 0, "unsupported_on_page": 1, "partly": 2}
rows = []
for e in sorted([e for e in ev if e["verdict"] != "faithful"], key=lambda e: (order.get(e["verdict"], 3), e["rule_id"])):
    r, pack = R[e["rule_id"]]
    applied = ""
    if e["rule_id"] in corr:
        c = corr[e["rule_id"]]
        applied = "; ".join(filter(None, ["hạ xuống nháp" if c.get("set", {}).get("reviewStatus") == "draft" else "", "sửa số trang" if "description_replace" in c else ""]))
    rows.append([e["rule_id"], e["quote_book"], e["quote_page"], e["verdict"], f"{pack}:{r.get('reviewStatus')}", applied,
                 (e.get("issue") or e.get("override_note") or "").replace("\n", " "), (e.get("qualifier") or "").replace("\n", " ")])
for e in sorted([e for e in web if e["verdict"] != "faithful"], key=lambda e: e["rule_id"]):
    rows.append([e["rule_id"], "TBCT", e.get("chapter"), e["verdict"], "bazi_deep/geju_defs|patterns_defs:draft", "", (e.get("issue") or "").replace("\n", " "),
                 (e.get("qualifier") or "").replace("\n", " ")])
with open(ROOT / "docs" / "source_audit_findings.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["rule_id", "book", "page_or_chapter", "verdict", "pack:status_now", "applied_by_this_audit", "issue", "qualifier"])
    w.writerows(rows)
print(len(rows), "findings written")
