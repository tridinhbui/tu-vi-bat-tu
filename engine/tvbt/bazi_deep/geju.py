"""Nền tảng cách cục: định cách từ nguyệt lệnh (ứng viên, không phải một đáp án), thành/bại/cứu bằng vị ngữ có từ vựng đóng,
ngoại cách (Hóa, Tòng) và phân xử nội/ngoại. Toàn bộ điều kiện nằm trong data/bazi_deep/geju_defs.json và là `draft`
(chưa đối chiếu Tử Bình Chân Thuyên). Vị ngữ chỉ đọc các dữ kiện đã tính (vị trí, tương tác đã giải, khí thế sau tương tác)."""
from __future__ import annotations

import json

from ..bazi import HIDDEN_STEMS
from ..ganzhi import BRANCHES_VI, STEM_ELEMENT, STEMS_VI, controls, generates
from .interact import Resolved
from .model import GOD_GROUPS, PILLARS, PIL_VI, ChartView
from .position import root_grade, roots, tou
from .profile import DEFAULT, LEVELS, DATA, SchoolProfile

LU = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}      # stem -> its Lộc branch
NHAN = {0: 3, 2: 6, 4: 6, 6: 9, 8: 0}                                    # yang stem -> Dương Nhận branch
NHAN_YIN = {1: 2, 3: 7, 5: 7, 7: 10, 9: 1}
DEFS = json.loads((DATA / "geju_defs.json").read_text("utf-8"))["defs"]
NAME_OF_GOD = {"Chính Quan": "Chính Quan", "Thất Sát": "Thất Sát", "Chính Ấn": "Chính Ấn", "Thiên Ấn": "Thiên Ấn", "Chính Tài": "Chính Tài",
               "Thiên Tài": "Thiên Tài", "Thực Thần": "Thực Thần", "Thương Quan": "Thương Quan"}


class Ctx:
    def __init__(self, view: ChartView, profile: SchoolProfile, R: Resolved, S: dict, extra: list | None = None):
        self.view, self.profile, self.R, self.S = view, profile, R, S
        self.vis = []        # active visible non-day stems: (cid, pillar, stem, god)
        for p in PILLARS:
            if p == "day":
                continue
            cid = f"{p}.stem"
            if cid in R.stem_element or R.mult.get(cid, 1.0) < profile.active_min:
                continue
            self.vis.append((cid, p, view.stem(p), view.god(view.stem(p))))
        self.hid = []        # active hidden stems of ban_khi / trung_khi
        for p in PILLARS:
            if R.mult.get(f"{p}.branch", 1.0) < profile.active_min:
                continue
            for h in view.hidden(p):
                if h["class"] != "du_khi":
                    self.hid.append((p, h["stem"], h["ten_god"]))
        # temporal pillars (luck / year / month): (cid, label, stem, branch); they act on the whole chart so they count as adjacent to every natal pillar
        for cid, label, st, br in (extra or []):
            if R.mult.get(cid, 1.0) >= profile.active_min:
                self.vis.append((cid, label, st, view.god(st)))
            for i, h in enumerate(HIDDEN_STEMS[br][:2]):
                self.hid.append((label, h, view.god(h)))
        self.rel = R.interactions

    def vis_in(self, G):
        return [v for v in self.vis if v[3] in GOD_GROUPS[G]]

    def lenh_recs(self, kinds, statuses=None):
        return [r for r in self.rel if r["kind"] in kinds and "month.branch" in r["members"] and (statuses is None or r.get("status") in statuses)]


def _dist(a: str, b: str) -> int:
    return ChartView.dist(a, b) if a in PILLARS and b in PILLARS else 1


def pred(ctx: Ctx, expr: str) -> tuple[bool, str]:
    name, _, arg = expr.partition(":")
    if name == "all":
        subs = arg.split("+")
        res = [pred(ctx, s) for s in subs]
        return all(r[0] for r in res), " & ".join(r[1] for r in res)
    if name == "visible":
        v = ctx.vis_in(arg)
        return bool(v), f"thấu {arg}: {[x[0] for x in v]}"
    if name == "any":
        v = ctx.vis_in(arg)
        h = [(p, STEMS_VI[s]) for p, s, g in ctx.hid if g in GOD_GROUPS[arg]]
        return bool(v or h), f"{arg}: thấu {[x[0] for x in v]}, tàng {h[:3]}"
    if name == "both_visible":
        a, b = arg.split("+")
        va, vb = ctx.vis_in(a), ctx.vis_in(b)
        return bool(va and vb), f"{a}:{[x[0] for x in va]} {b}:{[x[0] for x in vb]}"
    if name == "count_visible_ge":
        g, n = arg.split("=")
        v = ctx.vis_in(g)
        return len(v) >= int(n), f"{g} thấu {len(v)}"
    if name in ("controls_adjacent", "chain_adjacent"):
        a, b = arg.split(">")
        rel = controls if name == "controls_adjacent" else generates
        for ca, pa, sa, ga in ctx.vis_in(a):
            for cb, pb, sb, gb in ctx.vis_in(b) + ([(f"day.stem", "day", ctx.view.dm, "Nhật Chủ")] if b == "DM" else []):
                if pa != pb and _dist(pa, pb) == 1 and rel(STEM_ELEMENT[sa], STEM_ELEMENT[sb]):
                    return True, f"{ca} {'khắc' if name.startswith('controls') else 'sinh'} {cb} (kề)"
        return False, f"không có {a}→{b} kề sát"
    if name == "adjacent_dm":
        v = [x for x in ctx.vis_in(arg) if x[1] in PILLARS and _dist(x[1], "day") == 1 or x[1] not in PILLARS]
        return bool(v), f"{arg} kề Nhật Chủ: {[x[0] for x in v]}"
    if name == "both_any":
        a, b = arg.split("+")
        return pred(ctx, f"any:{a}")[0] and pred(ctx, f"any:{b}")[0], f"{a} và {b} cùng hiện diện"
    if name == "bound":
        hits = []
        for r in ctx.rel:
            if r["kind"] == "stem_combine" and r.get("status") in ("hop_khong_hoa", "gia_hoa", "tranh_hop"):
                for m in r["members"]:
                    p = m.split(".")[0]
                    if p in PILLARS and p != "day" and ctx.view.god(ctx.view.stem(p)) in GOD_GROUPS[arg]:
                        hits.append(m)
        return bool(hits), f"{arg} bị hợp trói: {hits}"
    if name == "lenh_clashed":
        rs = [r for r in ctx.lenh_recs(("branch_clash",)) if r["adjacent"] and r.get("status") != "hop_giai_xung"]
        return bool(rs), f"nguyệt lệnh bị xung kề: {[r['id'] for r in rs]}"
    if name == "lenh_clash_resolved":
        rs = ctx.lenh_recs(("branch_clash",), ("hop_giai_xung",))
        return bool(rs), f"xung nguyệt lệnh được hợp giải: {[r['id'] for r in rs]}"
    if name == "lenh_penalized":
        rs = ctx.lenh_recs(("branch_penalty", "branch_self_penalty"), ("co_hieu_luc",))
        return bool(rs), f"nguyệt lệnh bị hình: {[r['id'] for r in rs]}"
    if name in ("level_ge", "level_le"):
        i, j = ctx.S["level_index"], LEVELS.index(arg)
        return (i >= j if name == "level_ge" else i <= j), f"khí thế {ctx.S['level']}"
    if name == "sat_unrestrained":
        ok = bool(ctx.vis_in("Sat")) and not pred(ctx, "any:Thuc")[0] and not pred(ctx, "any:An")[0]
        return ok, "Sát thấu mà không có Thực Thần/Ấn chế hóa"
    if name == "none_of":
        gs = arg.split(",")
        return all(not pred(ctx, f"any:{g}")[0] for g in gs), f"không có {gs}"
    raise ValueError(f"unknown predicate {expr!r}")


def evaluate(ctx: Ctx, cach: str) -> dict:
    d = DEFS[{"Âm Nhận": "Dương Nhận"}.get(cach, cach)]
    thanh = [(e, *pred(ctx, e)) for e in d["thanh_any"]]
    ok_thanh = [t for t in thanh if t[1]]
    bai, unsaved, strong, weak = [], [], [], []
    for bid, e in d["bai"].items():
        hit, why = pred(ctx, e)
        if not hit:
            continue
        cuu = [(c, *pred(ctx, c)) for c in d["cuu"].get(bid, [])]
        # a rescue that is only hidden (tàng, `any:`) is weak: present but not shown on the heavenly stems next to the problem
        by = next((c for c in cuu if c[1] and not c[0].startswith("any:")), None)
        wk = next((c for c in cuu if c[1] and c[0].startswith("any:")), None)
        pick = by or wk
        bai.append({"id": bid, "evidence": why, "saved_by": pick[0] if pick else None, "saved_evidence": pick[2] if pick else None,
                    "saved_strength": ("mạnh" if by else "yếu (chỉ tàng)") if pick else None})
        (unsaved if not pick else strong if by else weak).append(bid)
    if unsaved:
        state = "bai"
    elif weak:
        state = "bai_cuu_yeu"
    elif strong:
        state = "bai_co_cuu"
    elif ok_thanh:
        state = "thanh"
    else:
        state = "chua_ro"
    if state == "thanh" and (pred(ctx, "lenh_clashed")[0] or pred(ctx, "lenh_penalized")[0]):
        state = "thanh_nhung_bi_pha"
    yong = [g for g in d["yong"] if pred(ctx, f"any:{g}")[0]]
    return {"state": state, "thanh": [{"cond": t[0], "evidence": t[2]} for t in ok_thanh], "bai": bai, "yong_groups": yong, "review_status": "draft"}


def inner_candidates(view: ChartView, profile: SchoolProfile, extra: list | None = None) -> list[dict]:
    mb, dm = view.month_branch, view.dm
    hid = view.hidden("month")
    tous = {t["stem"]: t for t in tou(view)}
    for cid, label, st, br in (extra or []):         # a temporal stem that equals a hidden stem of the month branch makes it 'thấu'
        if STEMS_VI[st] in tous:
            tous[STEMS_VI[st]] = {**tous[STEMS_VI[st]], "tou_same_char": tous[STEMS_VI[st]]["tou_same_char"] + [label]}
    out = []
    if LU[dm] == mb:
        out.append({"name": "Kiến Lộc", "basis": f"chi tháng {BRANCHES_VI[mb]} là Lộc của {STEMS_VI[dm]}", "tou": None})
    nhan = NHAN.get(dm) if dm % 2 == 0 else (NHAN_YIN.get(dm) if profile.yin_nhan else None)
    if nhan == mb:
        out.append({"name": "Dương Nhận" if dm % 2 == 0 else "Âm Nhận", "basis": f"chi tháng {BRANCHES_VI[mb]} là Nhận của {STEMS_VI[dm]}", "tou": None})
    elif hid[0]["ten_god"] == "Kiếp Tài":
        out.append({"name": "Nguyệt Kiếp", "basis": f"bản khí của chi tháng {BRANCHES_VI[mb]} là Kiếp Tài", "tou": None})
    if out:
        return out
    thau = [h for h in hid if h["ten_god"] not in GOD_GROUPS["Ti"] and tous[STEMS_VI[h["stem"]]]["tou_same_char"]]
    pick, how = (thau, "thấu can") if thau else ([], "")
    if not pick:
        main = next((h for h in hid if h["ten_god"] not in GOD_GROUPS["Ti"]), None)
        if main:
            pick, how = [main], "bản khí không thấu" if main is hid[0] else "bản khí là Tỉ Kiên nên lấy tàng can kế tiếp"
    for h in pick:
        out.append({"name": h["ten_god"], "basis": f"{how}: {STEMS_VI[h['stem']]} ({h['class']}) trong chi tháng {BRANCHES_VI[mb]}",
                    "tou": tous[STEMS_VI[h["stem"]]]["tou_same_char"], "class": h["class"]})
    return out


def outer_candidates(view: ChartView, profile: SchoolProfile, R: Resolved, S: dict) -> list[dict]:
    out = []
    for r in R.interactions:
        if r["kind"] == "stem_combine" and "day.stem" in r["members"] and r.get("status") in ("chan_hoa", "gia_hoa"):
            out.append({"name": f"Hóa {r['element']}", "kind": "hoa", "quality": "chân" if r["status"] == "chan_hoa" else "giả",
                        "evidence": {"interaction": r["id"], "met": r["hua_met"], "unmet": r["hua_unmet"]}})
    sh = S["shares"]
    for g, nm in (("Tai", "Tòng Tài"), ("QuanSat", "Tòng Sát"), ("ThucThuong", "Tòng Nhi")):
        if sh[g] >= profile.tong_dominant_share and S["ratio"] <= profile.tong_max_ratio and S["axes"]["de_dia"] in ("không", "yếu"):
            chan = S["ratio"] <= profile.tong_chan_tia and S["axes"]["de_dia"] == "không" and S["axes"]["de_the"] == "không"
            out.append({"name": nm, "kind": "tong", "quality": "chân" if chan else "giả",
                        "evidence": {"dominant_share": sh[g], "ratio": S["ratio"], "root": S["axes"]["de_dia"], "visible_help": S["axes"]["de_the"]}})
    return out


def analyse(view: ChartView, profile: SchoolProfile, R: Resolved, S: dict, extra: list | None = None) -> dict:
    ctx = Ctx(view, profile, R, S, extra)
    inner = []
    for c in inner_candidates(view, profile, extra):
        ev = evaluate(ctx, c["name"])
        inner.append({**c, **ev})
    outer = outer_candidates(view, profile, R, S)
    readings, note = [], ""
    chan = [o for o in outer if o["quality"] == "chân"]
    if chan:
        readings = [{"cach": chan[0]["name"], "kind": "ngoai_cach", "why": "ngoại cách đạt điều kiện chân nên thay nội cách"}]
        note = "ngoại cách chân thay nội cách"
    else:
        for c in inner[:1]:
            readings.append({"cach": c["name"], "kind": "noi_cach", "why": c["basis"]})
        for o in outer:
            readings.append({"cach": o["name"], "kind": "ngoai_cach_gia", "why": "điều kiện còn thiếu: " + ", ".join(o["evidence"].get("unmet", [])) if "unmet" in o["evidence"] else "còn tia cứu Nhật Chủ"})
        note = "giữ cả hai cách đọc" if outer else ("không định được cách từ nguyệt lệnh" if not inner else "nội cách")
    if len(inner) > 1 and not chan:
        for c in inner[1:]:
            readings.append({"cach": c["name"], "kind": "noi_cach_khac", "why": "ứng viên thấu can khác trong nguyệt lệnh"})
    return {"inner": inner, "outer": outer, "readings": readings, "arbitration": note, "review_status": "draft", "source": "SRC_TBCT (chưa verified)"}
