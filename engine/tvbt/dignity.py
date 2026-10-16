"""Miếu/Vượng/Đắc/Bình/Hãm lookup for the 14 chính tinh. Two published variants are kept apart (school variants):
  thuc_hanh : Tử Vi Thực Hành (default; transcribed from page images)
  toan_thu  : Tử Vi Đẩu Số Toàn Thư, Vũ Tài Lục (transcribed from the PDF text layer)
Unlisted (star, branch) pairs return None = unspecified; nothing is guessed."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent.parent / "data"
FILES = {"thuc_hanh": "dignity_vn.json", "toan_thu": "dignity_toanthu.json"}


@lru_cache(maxsize=None)
def _table(school: str) -> dict:
    return json.loads((_DATA / FILES[school]).read_text("utf-8"))["stars"]


def dignity(star: str, branch: str, school: str = "thuc_hanh") -> str | None:
    s = _table(school).get(star)
    return s["levels"].get(branch) if s else None


def compare(branches: list[str]) -> list[dict]:
    """Cells where both schools specify a level and disagree (also lists cells only one school specifies)."""
    a, b = _table("thuc_hanh"), _table("toan_thu")
    out = []
    for star in a:
        for br in branches:
            x, y = a[star]["levels"].get(br), b.get(star, {}).get("levels", {}).get(br)
            if x and y and x != y:
                out.append({"star": star, "branch": br, "thuc_hanh": x, "toan_thu": y})
    return out


@lru_cache(maxsize=1)
def _minor() -> dict:
    return json.loads((_DATA / "dignity_minor.json").read_text("utf-8"))["stars"]


MINOR_STARS = ("Văn Xương", "Văn Khúc", "Kình Dương", "Đà La", "Hỏa Tinh")


def minor_dignity(star: str, branch: str) -> str | None:
    s = _minor().get(star)
    return s["levels"].get(branch) if s else None
