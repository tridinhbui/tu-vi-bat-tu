"""Miếu/Vượng/Đắc/Bình/Hãm lookup for the 14 chính tinh and the phụ tinh (dignity_aux.json, see minor_dignity_cell). Two published variants are kept apart (school variants):
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
def _aux() -> dict:
    return json.loads((_DATA / "dignity_aux.json").read_text("utf-8"))


AUX_SCHOOLS = ("thuc_hanh", "toan_thu", "khao_luan")
# every phụ tinh that has a production table in at least one book (tools/build_aux_dignity.py); others are never classified
MINOR_STARS = tuple(dict.fromkeys(s for sc in AUX_SCHOOLS for s in _aux()["tables"][sc]))


def minor_dignity_cell(star: str, branch: str, school: str = "toan_thu") -> dict | None:
    """{level, term, school, locator} for an auxiliary star, or None when unknown.
    The chosen book is used if it tabulates the star at all; otherwise the next book in `fallback` (star by star, never cell by
    cell, so books are not mixed inside one star). A branch that table does not name is unknown. Experimental cells never show."""
    a = _aux()
    for sc in a["fallback"].get(school, a["fallback"]["toan_thu"]):
        t = a["tables"][sc].get(star)
        if t:
            c = t["cells"].get(branch)
            return {**c, "school": sc, "locator": t["locator"]} if c else None
    return None


def minor_dignity(star: str, branch: str, school: str = "toan_thu") -> str | None:
    """Auxiliary-star level on the five-step scale (see minor_dignity_cell)."""
    c = minor_dignity_cell(star, branch, school)
    return c["level"] if c else None
