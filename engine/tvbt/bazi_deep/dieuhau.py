"""Bảng điều hậu 10 can × 12 tháng (窮通寶鑑), nhập dạng draft từ trí nhớ; xem data/bazi_deep/dieu_hau_ctbg_draft.json.
lookup() trả về các can dụng theo thứ tự ưu tiên, quy ra thập thần so với Nhật Chủ, kèm việc chúng có mặt trong lá số hay không."""
from __future__ import annotations

import json

from ..ganzhi import BRANCHES_HAN, BRANCHES_VI, STEMS_HAN, STEMS_VI
from .model import PILLARS, ChartView, group_of
from .profile import DATA

_DATA = json.loads((DATA / "dieu_hau_ctbg_draft.json").read_text("utf-8"))      # memory-based 窮通寶鑑 table: only the ORDER inside a cell is used now
TABLE = _DATA["cells"]
_TVH = json.loads((DATA / "tvh_dieuhau.json").read_text("utf-8"))["cells"]          # Thiệu Vĩ Hoa pp.389-390: verified sets of usable stems
ROLE_GROUP = {"Quan": "QuanSat", "Sat": "QuanSat", "Thuc": "ThucThuong", "Thuong": "ThucThuong"}
VI_MONTH = {2: "Dần", 3: "Mão", 4: "Thìn", 5: "Tỵ", 6: "Ngọ", 7: "Mùi", 8: "Thân", 9: "Dậu", 10: "Tuất", 11: "Hợi", 0: "Tý", 1: "Sửu"}


def lookup(view: ChartView, extra_stems: list[int] | None = None) -> dict:
    """The SET of usable stems is Thiệu Vĩ Hoa's verified table (pp.389-390). Which stem is 'chính' comes from the first stem of the memory-based
    窮通寶鑑 draft cell when that stem belongs to the verified set; otherwise no stem is ranked."""
    dm_vi, mon_vi = STEMS_VI[view.dm], VI_MONTH[view.month_branch]
    cell = _TVH[mon_vi][dm_vi]
    draft = TABLE[STEMS_HAN[view.dm]][BRANCHES_HAN[view.month_branch]]
    chu = STEMS_VI[STEMS_HAN.index(draft[0])]
    chu = chu if chu in cell else None
    present_vis = {view.stem(p) for p in PILLARS if p != "day"} | set(extra_stems or [])
    present_hid = {h["stem"] for p in PILLARS for h in view.hidden(p)}
    out = []
    for name in cell:
        s = STEMS_VI.index(name)
        g = group_of(view.god(s)) if s != view.dm else "Ti"
        out.append({"stem": name, "han": STEMS_HAN[s], "rank": "chính (thứ hạng theo bảng nháp)" if name == chu else "có thể dùng", "ten_god": view.god(s),
                    "group": ROLE_GROUP.get(g, g), "visible": s in present_vis, "hidden": s in present_hid and s not in present_vis})
    out.sort(key=lambda x: x["stem"] != chu)
    return {"cell": f"{STEMS_HAN[view.dm]} sinh tháng {BRANCHES_HAN[view.month_branch]} ({BRANCHES_VI[view.month_branch]})", "yong_stems": out, "chu": chu,
            "satisfied": any(x["visible"] for x in out[:1]), "any_present": any(x["visible"] or x["hidden"] for x in out),
            "status": "tap_verified_TVH_thu_hang_draft", "src": "SRC_TVH_DIEUHAU", "checked": True}
