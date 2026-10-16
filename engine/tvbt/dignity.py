"""Miếu/Vượng/Đắc/Bình/Hãm lookup for the 14 chính tinh, transcribed from Tử Vi Thực Hành (see data/dignity_vn.json).
Unlisted (star, branch) pairs return None = unspecified; nothing is guessed."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "data" / "dignity_vn.json"


@lru_cache(maxsize=1)
def _table() -> dict:
    return json.loads(_PATH.read_text("utf-8"))["stars"]


def dignity(star: str, branch: str) -> str | None:
    s = _table().get(star)
    return s["levels"].get(branch) if s else None
