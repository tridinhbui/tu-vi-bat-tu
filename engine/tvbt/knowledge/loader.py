"""Loads the rule packs + source library + Vietnamese claim phrasing shipped in engine/data."""
from __future__ import annotations

import json
from pathlib import Path

from .schema import KnowledgeRule, Source, load_pack

DATA = Path(__file__).resolve().parent.parent.parent / "data"
PACKS = ["pack_vn_draft.json", "pack_khao_luan.json", "pack_thuc_hanh.json", "pack_thuc_hanh_palaces.json", "pack_thuc_hanh_combos.json", "pack_khao_luan_phu.json", "pack_khao_luan_phu2.json", "pack_khao_luan_cung.json", "pack_khao_luan_chinh_tinh.json", "pack_toan_thu.json", "pack_khao_luan_aux.json", "pack_thuc_hanh_aux.json", "pack_thuc_hanh_aux2.json", "pack_thuc_hanh_cach.json", "pack_thuc_hanh_menh_verse.json", "pack_thuc_hanh_star_menh.json", "pack_thuc_hanh_palaces2.json", "pack_bazi_zhenzong.json", "pack_bazi_napam.json"]


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


EXPERIMENTAL = DATA / "experimental"


def load_experimental():
    """Draft structures that production NEVER loads (not in PACKS): cách cục formations + engine-demo rules.
    Returns (rules, formations, sources). Used only by tests and by the opt-in `experimental` flag of /api/reasoning."""
    from .formation import load_formations
    rules, sources = load_pack(EXPERIMENTAL / "pack_engine_demo.json")
    return rules, load_formations(EXPERIMENTAL / "formations_experimental.json"), sources


def load_claims() -> dict[str, dict[str, str]]:
    raw = json.loads((DATA / "claims_vi.json").read_text("utf-8"))
    return {k: {"label": v, "gloss": ""} for k, v in raw.items()}
