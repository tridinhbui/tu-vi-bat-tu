"""Stem -> (Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ) star tables.

Only ONE table is present: `tam_hop_vn`, the table the engine already uses for the natal Tứ Hóa and that Thực Hành p.21 and Khảo Luận
pp.196-197 agree on for all ten stems. Whether the Phi Tinh school uses the same star for every stem is NOT verified here: published
Phi Tinh tables differ from the tam hợp one for some stems, and no alternative table has been added because none has been checked.
`fly()` therefore takes the table id explicitly and refuses unknown ids; adding a verified variant means adding one entry to TABLES."""
from __future__ import annotations

from ..tuvi import TU_HOA

HOA = ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ")

TABLES: dict[str, dict] = {
    "tam_hop_vn": {
        "stars": TU_HOA,                                  # stem index -> (Lộc, Quyền, Khoa, Kỵ)
        "status": "reused_unverified_for_phi_tinh",
        "note": "Same table as the natal Tứ Hóa (verified for the tam hợp school). Its use by the Phi Tinh school is not verified.",
    },
}


def stars_for(stem: int, table_id: str = "tam_hop_vn") -> dict[str, str]:
    if table_id not in TABLES:
        raise ValueError(f"unknown Phi Hóa table {table_id!r}; known: {sorted(TABLES)}")
    return dict(zip(HOA, TABLES[table_id]["stars"][stem]))
