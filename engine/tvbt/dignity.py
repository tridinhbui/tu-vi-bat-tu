"""Miếu/Vượng/Đắc/Bình/Hãm for every star the engine places — one authoritative knowledge base, engine/data/dignity_kb.json
(built by tools/build_dignity_kb.py from page images of Thực Hành, Toàn Thư and Khảo Luận; src/interpret/dignity.ts reads the same file).

classify(star, branch, school) -> {status: VERIFIED|CONFLICT|UNVERIFIED|NOT_APPLICABLE, ...} with source provenance.
Only VERIFIED carries a level; dignity() / minor_dignity() return it or None, and None reaches the rules as 'unspecified'.
Nothing is guessed: no default 'bình', no level from a star's cát/hung nature or from another star in the palace.
Schools: thuc_hanh (default), toan_thu, khao_luan. Phụ tinh fall back star by star to the next book when the chosen book has no table
for that star (the result names the book used); chính tinh never fall back."""
from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent.parent / "data"
SCHOOLS = ("thuc_hanh", "toan_thu", "khao_luan")


@lru_cache(maxsize=1)
def kb() -> dict:
    return json.loads((_DATA / "dignity_kb.json").read_text("utf-8"))


@lru_cache(maxsize=1)
def _ids() -> dict[str, str]:
    return {m["id"]: n for n, m in kb()["stars"].items()}


def _slug(name: str) -> str:
    s = unicodedata.normalize("NFD", name.replace("Đ", "D").replace("đ", "d"))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower().strip().replace(" ", "_")


def normalize_star(star: str) -> str | None:
    """Canonical star name for a name, id or alias (any case / tone placement / NFC-NFD). None when unknown or ambiguous."""
    k = kb()
    nfc = unicodedata.normalize("NFC", star.strip())
    if nfc in k["stars"]:
        return nfc
    for n in k["stars"]:
        if n.casefold() == nfc.casefold():
            return n
    key = nfc if nfc in _ids() else _slug(nfc)
    if key in _ids():
        return _ids()[key]
    sid = k["aliases"].get(key)
    return _ids().get(sid) if sid else None


def classify(star: str, branch: str, school: str = "thuc_hanh") -> dict:
    """Classification of `star` standing in `branch` under `school` (see the module docstring)."""
    k = kb()
    name = normalize_star(star)
    if school not in k["resolved"]:
        raise ValueError(f"unknown school {school!r}")
    if branch not in k["branches"]:
        raise ValueError(f"unknown branch {branch!r}")
    if name is None:
        return {"status": "UNVERIFIED", "reason": f"unknown star {star!r}"}
    return {"star": name, "id": k["stars"][name]["id"], **k["resolved"][school][name][branch]}


def dignity(star: str, branch: str, school: str = "thuc_hanh") -> str | None:
    r = classify(star, branch, school)
    return r["value"] if r["status"] == "VERIFIED" else None


@lru_cache(maxsize=None)
def _table(school: str) -> dict:
    """Chính tinh of one book in the old shape {star: {locator, levels}} (VERIFIED cells only)."""
    k = kb()
    out = {}
    for n, m in k["stars"].items():
        if m["kind"] != "chinh_tinh":
            continue
        cells = {b: r for b, r in k["resolved"][school][n].items() if r["status"] == "VERIFIED"}
        if cells:
            out[n] = {"locator": next(iter(cells.values()))["locator"], "levels": {b: r["value"] for b, r in cells.items()}}
    return out


def compare(branches: list[str]) -> list[dict]:
    """Cells where both schools specify a level and disagree."""
    a, b = _table("thuc_hanh"), _table("toan_thu")
    out = []
    for star in a:
        for br in branches:
            x, y = a[star]["levels"].get(br), b.get(star, {}).get("levels", {}).get(br)
            if x and y and x != y:
                out.append({"star": star, "branch": br, "thuc_hanh": x, "toan_thu": y})
    return out


# every phụ tinh with at least one VERIFIED cell in some book; the others are never given a level
MINOR_STARS = tuple(n for n, m in kb()["stars"].items() if m["kind"] == "phu_tinh"
                    and any(r["status"] == "VERIFIED" for sc in SCHOOLS for r in kb()["resolved"][sc][n].values()))


def minor_dignity_cell(star: str, branch: str, school: str = "toan_thu") -> dict | None:
    """{level, term, school, locator[, legacy]} for a VERIFIED auxiliary-star cell, else None."""
    r = classify(star, branch, school)
    if r["status"] != "VERIFIED":
        return None
    return {"level": r["value"], "term": r["term"], "school": r["school"], "locator": r["locator"], **({"legacy": True} if r.get("legacy") else {})}


def minor_dignity(star: str, branch: str, school: str = "toan_thu") -> str | None:
    c = minor_dignity_cell(star, branch, school)
    return c["level"] if c else None
