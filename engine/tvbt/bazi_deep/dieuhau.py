"""Bảng điều hậu 10 can × 12 tháng (窮通寶鑑), nhập dạng draft từ trí nhớ; xem data/bazi_deep/dieu_hau_ctbg_draft.json.
lookup() trả về các can dụng theo thứ tự ưu tiên, quy ra thập thần so với Nhật Chủ, kèm việc chúng có mặt trong lá số hay không."""
from __future__ import annotations

import json

from ..ganzhi import BRANCHES_HAN, BRANCHES_VI, STEMS_HAN, STEMS_VI
from .model import PILLARS, ChartView, group_of
from .profile import DATA

_DATA = json.loads((DATA / "dieu_hau_ctbg_draft.json").read_text("utf-8"))      # memory-based 窮通寶鑑 table: only the ORDER inside a cell is used now
TABLE = _DATA["cells"]
_TVH_DOC = json.loads((DATA / "tvh_dieuhau.json").read_text("utf-8"))
_TVH = _TVH_DOC["cells"]                    # Thiệu Vĩ Hoa pp.389-390: verified sets of usable stems
_ORDER = _TVH_DOC["notes_order"]            # pp.391-396 chú thích: ordered priority per cell (first = chủ)
ROLE_GROUP = {"Quan": "QuanSat", "Sat": "QuanSat", "Thuc": "ThucThuong", "Thuong": "ThucThuong"}
VI_MONTH = {2: "Dần", 3: "Mão", 4: "Thìn", 5: "Tỵ", 6: "Ngọ", 7: "Mùi", 8: "Thân", 9: "Dậu", 10: "Tuất", 11: "Hợi", 0: "Tý", 1: "Sửu"}


def lookup(view: ChartView, extra_stems: list[int] | None = None) -> dict:
    """The SET of usable stems is Thiệu Vĩ Hoa's table (pp.389-390); the ORDER (first = chủ) is his note list (pp.391-396), restricted to the table set.
    The memory-based 窮通寶鑑 draft is only a fallback ranking for stems the notes do not mention."""
    dm_vi, mon_vi = STEMS_VI[view.dm], VI_MONTH[view.month_branch]
    cell = _TVH[mon_vi][dm_vi]
    draft = TABLE[STEMS_HAN[view.dm]][BRANCHES_HAN[view.month_branch]]
    ranked = [x for x in _ORDER[mon_vi][dm_vi] if x in cell] + [x for x in cell if x not in _ORDER[mon_vi][dm_vi]]
    chu = ranked[0] if ranked else None
    if chu is None and draft:
        c = STEMS_VI[STEMS_HAN.index(draft[0])]
        chu = c if c in cell else None
    present_vis = {view.stem(p) for p in PILLARS if p != "day"} | set(extra_stems or [])
    present_hid = {h["stem"] for p in PILLARS for h in view.hidden(p)}
    out = []
    for name in ranked:
        s = STEMS_VI.index(name)
        g = group_of(view.god(s)) if s != view.dm else "Ti"
        out.append({"stem": name, "han": STEMS_HAN[s], "rank": "chính (thứ tự chú thích TVH tr.391-396)" if name == chu else "có thể dùng", "ten_god": view.god(s),
                    "group": ROLE_GROUP.get(g, g), "visible": s in present_vis, "hidden": s in present_hid and s not in present_vis})
    out.sort(key=lambda x: x["stem"] != chu)
    return {"cell": f"{STEMS_HAN[view.dm]} sinh tháng {BRANCHES_HAN[view.month_branch]} ({BRANCHES_VI[view.month_branch]})", "yong_stems": out, "chu": chu,
            "satisfied": any(x["visible"] for x in out[:1]), "any_present": any(x["visible"] or x["hidden"] for x in out),
            "status": "tap_va_thu_tu_TVH_verified", "src": "SRC_TVH_DIEUHAU", "checked": True}
