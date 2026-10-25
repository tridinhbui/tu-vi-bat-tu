"""Loader for the Western knowledge base (engine/data/western/kb/*.json). Read-only, cached."""
from __future__ import annotations

import json
import pathlib
from functools import lru_cache

KB = pathlib.Path(__file__).resolve().parents[1] / "data" / "western" / "kb"


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    return json.loads((KB / f"{name}.json").read_text(encoding="utf-8"))


def aspects() -> dict:
    return load("aspects")


def core() -> dict:
    return load("core")


def dignities() -> dict:
    return load("dignities")


def sources() -> dict:
    return load("sources")
