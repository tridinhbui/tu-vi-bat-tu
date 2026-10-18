"""Read-only access to the growth knowledge files (engine/data/growth/*.json) and the existing book-derived tables they cite."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent.parent / "data"


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    return json.loads((DATA / "growth" / f"{name}.json").read_text("utf-8"))


@lru_cache(maxsize=None)
def book(name: str) -> dict:
    """Existing tables the growth layer quotes as 'bieu_tuong' (star_profiles, tu_hoa_vi)."""
    return json.loads((DATA / f"{name}.json").read_text("utf-8"))


def stars() -> dict:
    return load("stars")["stars"]


def concept(cid: str) -> dict:
    c = load("concepts")["concepts"][cid]
    return {"id": cid, "name": c["name"], "gist": c["gist"], "ref": c["ref"]}
