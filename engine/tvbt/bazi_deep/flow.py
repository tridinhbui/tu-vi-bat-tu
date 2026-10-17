"""Nguyên lưu (源流): Trích Thiên Tủy PDF pp.79-81. Nguyên lưu là hành vượng nhất trong tứ trụ, không phân biệt tài quan ấn thực thương tỉ kiếp;
cần lưu thông sinh hóa. 'Khởi tại Tỉ Kiếp, kết thúc tại Tài Quan là hỉ; khởi tại Tài Quan, kết thúc tại Tỉ Kiếp là kỵ.'
Nếu giữa đường bị ngăn trở thì xem thần ngăn trở là gì. Hệ thống: nguồn = hành có sức lớn nhất; theo chuỗi 'sinh' qua các hành có mặt
(từ flow_min trở lên); điểm dừng là hành kế tiếp vắng mặt. Ngưỡng 'có mặt' là draft."""
from __future__ import annotations

from ..ganzhi import ELEMENTS, controls, generates
from .profile import SchoolProfile
from .strength import GROUP_VI, group_of_element


def nguyen_luu(S: dict, profile: SchoolProfile) -> dict:
    tot = sum(S["by_element"].values()) or 1.0
    sh = {e: S["by_element"][e] / tot for e in ELEMENTS}
    dm = S["dm_element"]
    src = max(ELEMENTS, key=lambda e: sh[e])
    path = [src]
    cur = src
    blocked_by = None
    for _ in range(4):
        nxt = next(x for x in ELEMENTS if generates(cur, x))
        if nxt in path:
            break
        if sh[nxt] >= profile.flow_min:
            path.append(nxt)
            cur = nxt
            continue
        # the next link is absent: what stands in the way? an element that controls it, or the lack of it
        blocked_by = next((e for e in ELEMENTS if controls(e, nxt) and sh[e] >= profile.flow_min and e != cur), None) or f"vắng {nxt}"
        break
    start_g, end_g = group_of_element(dm, path[0]), group_of_element(dm, path[-1])
    if start_g in ("Ti", "An") and end_g in ("Tai", "QuanSat") and len(path) >= 2:
        verdict = "hi"
    elif start_g in ("Tai", "QuanSat") and end_g in ("Ti",) and len(path) >= 2:
        verdict = "ky"
    else:
        verdict = "khong_ket_luan"
    return {"source": path[0], "path": path, "start_group": start_g, "end_group": end_g, "start_label": GROUP_VI[start_g], "end_label": GROUP_VI[end_g],
            "blocked_by": blocked_by, "verdict": verdict, "shares": {e: round(sh[e], 3) for e in ELEMENTS}, "src": "SRC_TTT_NGUYENLUU"}
