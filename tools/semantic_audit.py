"""Rule-library audit for the synthesis engine (Phase 1 evidence). Read-only: it never edits a pack.

Checks over every Tử Vi rule:
  shared_claims        claims reused by several rules (one label, several conditions) — why the label cannot be read as the rule's meaning
  label_condition      the shared label's parenthetical condition differs from the rule's own paraphrase
  limit_positive_label effect='limit' rules whose label reads as a positive outcome (the old renderer printed 'thuận lợi' for a limitation)
  scope_mismatch       the paraphrase names 'đồng cung' / 'xung chiếu' / 'đối cung' only, but the pack condition reads tam phương facts
  corroboration        groups of verified rules from DIFFERENT books that stand on the same normalised chart facts and reach the same concept
                       (one fact, several voices: counted once by the synthesis engine)
  mapping_sample       reading -> concepts for a deterministic sample, for human review of the concept lexicon
Run:  .venv/bin/python tools/semantic_audit.py [--out docs/synthesis/rule_audit.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))

from tvbt.knowledge.loader import load_all, load_claims  # noqa: E402
from tvbt.synthesis import semantics as sm  # noqa: E402

NARROW = re.compile(r"đồng cung|xung chiếu|đối cung")
WIDE = re.compile(r"hội|gặp|tam phương|chiếu Mệnh|hợp chiếu|giáp")


def _facts(expr) -> set[str]:
    return {x[0] for x in sm.leaves(expr)}


def main(out: Path | None):
    rules, _ = load_all()
    claims = load_claims()
    tv = [r for r in rules if r.system == "tu_vi"]
    by_claim = defaultdict(list)
    for r in tv:
        for c in r.consequences:
            if c.get("kind") == "finding":
                by_claim[c["claim"]].append((r, c))
    shared = {k: [r.id for r, _ in v] for k, v in by_claim.items() if len(v) > 1}
    label_cond, limit_pos, scope, mapping = [], [], [], []
    corro = defaultdict(list)
    for r in tv:
        for c in r.consequences:
            if c.get("kind") != "finding":
                continue
            label = (claims.get(c["claim"]) or {}).get("label", c["claim"])
            own, src = sm.reading_of(r, label)
            lcore, ltrig = sm.split_reading(label)
            ocore, otrig = sm.split_reading(own)
            if src == "description" and ltrig and otrig and _norm(ltrig) != _norm(otrig):
                label_cond.append({"rule": r.id, "claim": c["claim"], "label_condition": ltrig, "rule_condition": otrig})
            if c.get("effect") == "limit":
                pos = [h[0] for h in sm.match_concepts(lcore) if sm.lexicon()["concepts"][h[0]]["pol"] == "+"]
                neg = [h[0] for h in sm.match_concepts(lcore) if sm.lexicon()["concepts"][h[0]]["pol"] == "-"]
                if pos and not neg and not lcore.startswith("hạn chế"):
                    limit_pos.append({"rule": r.id, "label": label, "own_reading": ocore, "concepts_in_label": pos})
            f = _facts(r.conditions)
            if otrig and NARROW.search(otrig) and not WIDE.search(otrig) and any(x.startswith("palace.tam_phuong") for x in f):
                scope.append({"rule": r.id, "book_condition": otrig, "pack_facts": sorted(x for x in f if x != "palace.name")})
            if r.reviewStatus == "verified":
                lv = [x for x in sm.leaves(r.conditions) if x[0] != "palace.name"]
                pal = next((x[2] for x in sm.leaves(r.conditions) if x[0] == "palace.name"), "chart")
                for cid, _, _ in sm.match_concepts(ocore):
                    corro[(str(pal), cid, sm.root_of(lv))].append((r.id, tuple(sorted(r.sourceIds))))
            if len(mapping) < 400 and hash(r.id) % 3 == 0:
                mapping.append({"rule": r.id, "reading": ocore, "concepts": [h[0] for h in sm.match_concepts(ocore)]})
    groups = [{"palace": k[0], "concept": k[1], "root": list(k[2]), "rules": [x[0] for x in v], "books": sorted({s for x in v for s in x[1]})}
              for k, v in corro.items() if len({s for x in v for s in x[1]}) > 1]
    report = {
        "rules_tu_vi": len(tv), "claims": len(by_claim),
        "shared_claims": {"count": len(shared), "max_rules_per_claim": max(map(len, shared.values())) if shared else 0, "examples": dict(list(shared.items())[:15])},
        "label_condition": {"count": len(label_cond), "items": label_cond},
        "limit_positive_label": {"count": len(limit_pos), "items": limit_pos},
        "scope_mismatch": {"count": len(scope), "items": scope},
        "corroboration": {"count": len(groups), "items": groups},
        "mapping_sample": sorted(mapping, key=lambda x: x["rule"])[:200],
    }
    print(json.dumps({k: (v["count"] if isinstance(v, dict) and "count" in v else v) for k, v in report.items() if k != "mapping_sample"}, ensure_ascii=False, indent=1))
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=1), "utf-8")
        print("written", out)


def _norm(s: str) -> str:
    return re.sub(r"[^\wÀ-ỹ]+", " ", s.lower()).strip()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    main(ap.parse_args().out)
