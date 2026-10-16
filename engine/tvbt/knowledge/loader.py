"""Loads the rule packs + source library + Vietnamese claim phrasing shipped in engine/data."""
from __future__ import annotations

import json
from pathlib import Path

from .schema import KnowledgeRule, Source, load_pack

DATA = Path(__file__).resolve().parent.parent.parent / "data"
PACKS = ["pack_vn_draft.json", "pack_khao_luan.json", "pack_thuc_hanh.json", "pack_thuc_hanh_palaces.json", "pack_thuc_hanh_combos.json", "pack_bazi_zhenzong.json"]


def load_all() -> tuple[list[KnowledgeRule], list[Source]]:
    sources = [Source(**s) for s in json.loads((DATA / "sources.json").read_text("utf-8"))["sources"]]
    rules: list[KnowledgeRule] = []
    seen = {s.id for s in sources}
    for name in PACKS:
        r, s = load_pack(DATA / name)
        rules += r
        for x in s:
            if x.id not in seen:
                sources.append(x); seen.add(x.id)
    return rules, sources


def load_claims() -> dict[str, dict[str, str]]:
    raw = json.loads((DATA / "claims_vi.json").read_text("utf-8"))
    return {k: {"label": v, "gloss": ""} for k, v in raw.items()}
