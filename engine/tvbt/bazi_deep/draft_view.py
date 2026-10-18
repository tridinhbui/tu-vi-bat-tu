"""Presentation envelope for the opt-in draft view of the deep Bát Tự analysis (docs/BAZI_DEEP_API_CONTRACT.md).
It adds labels, mandatory strings and review status AROUND the analysis; it never reads, sorts, scores or changes a method's conclusion. The analysis itself is untouched,
so a request without the flag returns exactly what it returned before."""
from __future__ import annotations

import json

from .profile import DATA

CONTRACT_VERSION = "bazi-deep-draft/1"
UI = json.loads((DATA / "ui_strings_vi.json").read_text("utf-8"))
REVIEW = json.loads((DATA / "review_status.json").read_text("utf-8"))


def envelope(analysis: dict) -> dict:
    Y = analysis["yongshen"]
    return {
        "contract_version": CONTRACT_VERSION,
        "draft_label": UI["states"]["draft_label"],
        "banner": UI["states"]["draft_banner"],
        "ui_strings": UI,
        "method_order": list(Y["methods"]),
        "review_status": REVIEW,
        "book_internal_conflict": (Y["methods"]["dieu_hau"].get("table") or {}).get("book_internal_conflict"),
        "contract_doc": "docs/BAZI_DEEP_API_CONTRACT.md",
    }
