"""Bảng điều hậu 10 can × 12 tháng (窮通寶鑑), nhập dạng draft từ trí nhớ; xem data/bazi_deep/dieu_hau_ctbg_draft.json.
lookup() trả về các can dụng theo thứ tự ưu tiên, quy ra thập thần so với Nhật Chủ, kèm việc chúng có mặt trong lá số hay không."""
from __future__ import annotations

import json

from ..ganzhi import BRANCHES_HAN, BRANCHES_VI, STEMS_HAN, STEMS_VI
from .model import PILLARS, ChartView, group_of
from .profile import DATA

_DATA = json.loads((DATA / "dieu_hau_ctbg_draft.json").read_text("utf-8"))
TABLE = _DATA["cells"]
ROLE_GROUP = {"Quan": "QuanSat", "Sat": "QuanSat", "Thuc": "ThucThuong", "Thuong": "ThucThuong"}


def lookup(view: ChartView, extra_stems: list[int] | None = None) -> dict:
    cell = TABLE[STEMS_HAN[view.dm]][BRANCHES_HAN[view.month_branch]]
    present_vis = {view.stem(p) for p in PILLARS if p != "day"} | set(extra_stems or [])
    present_hid = {h["stem"] for p in PILLARS for h in view.hidden(p)}
    out = []
    for i, ch in enumerate(cell):
        s = STEMS_HAN.index(ch)
        g = group_of(view.god(s)) if s != view.dm else "Ti"
        out.append({"stem": STEMS_VI[s], "han": ch, "rank": "chính" if i == 0 else "phụ", "ten_god": view.god(s), "group": ROLE_GROUP.get(g, g),
                    "visible": s in present_vis, "hidden": s in present_hid and s not in present_vis})
    return {"cell": f"{STEMS_HAN[view.dm]} sinh tháng {BRANCHES_HAN[view.month_branch]} ({BRANCHES_VI[view.month_branch]})", "yong_stems": out,
            "satisfied": any(x["visible"] for x in out[:1]), "any_present": any(x["visible"] or x["hidden"] for x in out),
            "status": "draft_tu_tri_nho", "checked": f"{STEMS_HAN[view.dm]}{BRANCHES_HAN[view.month_branch]}" in _DATA["checked_cells"]}
