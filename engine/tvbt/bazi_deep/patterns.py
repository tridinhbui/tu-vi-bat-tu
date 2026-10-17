"""Cấu trúc thập thần có tên (Sát Ấn tương sinh, Thực chế Sát, Tài phá Ấn, Thương kiến Quan...). Mỗi cấu trúc là một mẫu vị ngữ
trong data/bazi_deep/patterns_defs.json (draft); engine chỉ đánh giá, không có logic riêng cho từng cấu trúc.
Trạng thái: thanh | thanh_bi_pha[_co_cuu|_cuu_yeu] | co_ten_khong_ke (đủ chữ nhưng không kề sát) cho cấu trúc thuận;
co_benh | co_benh_co_cuu | co_benh_cuu_yeu | co_ten_khong_ke cho cấu trúc bệnh."""
from __future__ import annotations

import json

from .geju import Ctx, pred
from .profile import DATA

DEFS = json.loads((DATA / "patterns_defs.json").read_text("utf-8"))["defs"]


def _rescue(ctx: Ctx, exprs: list[str]):
    res = [(e, *pred(ctx, e)) for e in exprs]
    strong = next((r for r in res if r[1] and not r[0].startswith("any:")), None)
    weak = next((r for r in res if r[1] and r[0].startswith("any:")), None)
    return strong, weak


def evaluate_all(ctx: Ctx) -> list[dict]:
    out = []
    for pid, d in DEFS.items():
        formed = [(e, *pred(ctx, e)) for e in d["formed"]]
        ok = all(f[1] for f in formed)
        weak_ok = (not ok) and d["weak"] and all(pred(ctx, e)[0] for e in d["weak"])
        if not ok and not weak_ok:
            continue
        rec = {"id": pid, "name": d["vi"], "polarity": d["polarity"], "review_status": "draft", "evidence": [f[2] for f in formed if f[1]] or [pred(ctx, e)[1] for e in d["weak"]]}
        if not ok:
            rec["state"] = "co_ten_khong_ke"
            out.append(rec)
            continue
        if d["polarity"] == "benh":
            strong, weak = _rescue(ctx, d["cuu"].get("formed", []))
            rec["state"] = "co_benh_co_cuu" if strong else "co_benh_cuu_yeu" if weak else "co_benh"
            rec["saved_by"] = (strong or weak or (None,))[0]
        else:
            hits, unsaved, weak_ids = [], [], []
            for bid, e in d["bai"].items():
                hit, why = pred(ctx, e)
                if not hit:
                    continue
                strong, weak = _rescue(ctx, d["cuu"].get(bid, []))
                hits.append({"id": bid, "evidence": why, "saved_by": (strong or weak or (None,))[0], "saved_strength": "mạnh" if strong else "yếu (chỉ tàng)" if weak else None})
                if not strong and not weak:
                    unsaved.append(bid)
                elif not strong:
                    weak_ids.append(bid)
            rec["bai"] = hits
            rec["state"] = ("thanh_bi_pha" if unsaved else "thanh_bi_pha_cuu_yeu" if weak_ids else "thanh_bi_pha_co_cuu" if hits else "thanh")
        out.append(rec)
    return out
