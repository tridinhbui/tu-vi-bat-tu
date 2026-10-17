"""Explain the draft cách-cục verdicts: which stars, which palaces, which relation and which condition produced each state.

Read-only layer over `reasoning.formation_eval` (which stays the single source of the verdict). For every condition of a
formation it adds (a) a Vietnamese sentence built from the chart and (b) the exact stars/palaces involved, so the UI can
highlight them. Nothing here decides a state, adds a rule or marks anything verified.
"""
from __future__ import annotations

import re

from .knowledge import dsl
from .reasoning import facts as rfacts
from .reasoning.formation_eval import STATE_VI, evaluate_formation
from .reasoning.positions import CAT_STARS, SAT_STARS

ROLE_VI = {"self": "đồng cung", "opp": "xung chiếu", "trine1": "tam hợp", "trine2": "tam hợp", "flank_prev": "giáp cung",
           "flank_next": "giáp cung", "nhi_hop": "nhị hợp"}
GROUPS = {"self": ["self"], "opp": ["opp"], "trine": ["trine1", "trine2"], "trine1": ["trine1"], "trine2": ["trine2"],
          "flank": ["flank_prev", "flank_next"], "flank_prev": ["flank_prev"], "flank_next": ["flank_next"],
          "tp": ["self", "opp", "trine1", "trine2"], "nhi_hop": ["nhi_hop"]}
REL_FACT = re.compile(r"^palace\.rel\.(self|opp|trine|trine1|trine2|flank|flank_prev|flank_next|tp|nhi_hop)_(stars|majors|hoa)$")
KHI_FACT = re.compile(r"^palace\.khi\.(cat|sat)_(self|tp|flank)$")
TP_RANK = re.compile(r"^palace\.tp_rank\.(.+)$")
KIND_VI = {"boosters": "Tăng thế", "breakers": "Phá cách", "rescuers": "Cứu giải", "refutations": "Phản chứng"}


class _Chart:
    def __init__(self, tv):
        self.tv = tv
        self.by_name = {p["name"]: p for p in tv.palaces}
        self.base = rfacts.tuvi_facts(tv)
        self.star_at = {s: p["name"] for p in tv.palaces for s in p["stars"]}

    def facts_of(self, subject: str):
        return self.base.get(subject, {})

    def world(self, name: str):
        return self.base.get(f"palace:{name}")

    def role_palaces(self, anchor: str, group: str) -> list[tuple[str, str]]:
        names = self.base[f"palace:{anchor}"]["palace.rel_names"]
        return [(r, names[r]) for r in GROUPS[group]]


def _items_for_stars(ch: _Chart, anchor: str, group: str, wanted: list[str]) -> list[dict]:
    out = []
    for role, pname in ch.role_palaces(anchor, group):
        for s in wanted:
            if s in ch.by_name[pname]["stars"]:
                out.append({"kind": "star", "star": s, "palace": pname, "role": ROLE_VI[role]})
    return out


def _items_for_hoa(ch: _Chart, anchor: str, group: str, wanted: list[str]) -> list[dict]:
    out = []
    for role, pname in ch.role_palaces(anchor, group):
        bi = ch.by_name[pname]["branch_index"]
        for h in wanted:
            v = ch.tv.tu_hoa.get(h)
            if v and v.get("branch") == bi:
                out.append({"kind": "hoa", "hoa": h, "star": v["star"], "palace": pname, "role": ROLE_VI[role]})
    return out


def highlight(ch: _Chart, expr: dict, anchor: str) -> list[dict]:
    """Items (stars / hóa / palaces) that make the TRUE parts of `expr` true. Parts that are false or unknown contribute nothing."""
    facts = ch.facts_of(f"palace:{anchor}")
    if dsl.evaluate(expr, facts, ch.world) is not True:
        return []
    if "all" in expr or "any" in expr or "count" in expr:
        key = next(k for k in ("all", "any", "count") if k in expr)
        return [i for e in expr[key] for i in highlight(ch, e, anchor)]
    if "not" in expr:
        return []
    name, tgt = (expr["fact"], anchor) if "fact" in expr else (expr["ref"]["fact"], dsl.resolve_palace(expr["ref"]["palace"], facts) or anchor)
    tfacts = ch.facts_of(f"palace:{tgt}")
    want = expr.get("value")
    want = want if isinstance(want, list) else [want]
    m = REL_FACT.match(name)
    if m:
        group, what = m.groups()
        if what == "hoa":
            return _items_for_hoa(ch, tgt, group, want)
        return _items_for_stars(ch, tgt, group, want)
    if name in ("palace.tuan", "palace.triet"):
        return [{"kind": "palace", "palace": tgt, "note": "Tuần" if name.endswith("tuan") else "Triệt"}]
    if name in ("palace.rel.opp_tuan", "palace.rel.opp_triet"):
        opp = tfacts["palace.rel_names"]["opp"]
        return [{"kind": "palace", "palace": opp, "note": "Tuần" if name.endswith("tuan") else "Triệt"}]
    m = TP_RANK.match(name)
    if m:
        return _items_for_stars(ch, tgt, "tp", [m.group(1)])
    m = KHI_FACT.match(name)
    if m:
        tag, grp = m.groups()
        pool = CAT_STARS if tag == "cat" else SAT_STARS
        return _items_for_stars(ch, tgt, {"self": "self", "tp": "tp", "flank": "flank"}[grp], list(pool))
    return [{"kind": "palace", "palace": tgt, "note": ""}]


def sentence(items: list[dict]) -> str:
    parts = []
    for i in items:
        if i["kind"] == "star":
            parts.append(f"{i['star']} ở cung {i['palace']} ({i['role']})")
        elif i["kind"] == "hoa":
            parts.append(f"{i['hoa']} rơi vào {i['star']} ở cung {i['palace']} ({i['role']})")
        else:
            parts.append(f"{i['note'] or 'cung'} ở cung {i['palace']}".strip())
    return "; ".join(dict.fromkeys(parts))


def _evidence(ch: _Chart, f, d: dict) -> list[dict]:
    out = []
    for kind in ("boosters", "breakers", "rescuers", "refutations"):
        active_ids = set(d[kind])
        for e in getattr(f, kind):
            on = e.id in active_ids
            items = highlight(ch, e.when, f.anchor) if on else []
            row = {"id": e.id, "kind": kind, "kind_vi": KIND_VI[kind], "label": e.label, "active": on, "items": items,
                   "because": sentence(items) if on else ""}
            if kind == "rescuers":
                bl = {b.id: b.label for b in f.breakers}
                row["rescues"] = [bl[x] for x in (bl if "*" in e.rescues else e.rescues) if x in bl]
            out.append(row)
    return out


def _chain(f, d: dict, core_items: list[dict], ev: list[dict]) -> list[dict]:
    act = lambda k: [e for e in ev if e["kind"] == k and e["active"]]
    rel = sorted({f"{i['palace']} ({i['role']})" for i in core_items if i.get("role")}) or [f"cung {f.anchor}"]
    steps = [{"step": "Dữ kiện", "text": sentence(core_items) or f"cung {f.anchor}"},
             {"step": "Quan hệ", "text": "các cung liên quan: " + ", ".join(rel)},
             {"step": "Cách cục", "text": f"cấu trúc {f.name_vi} " + ("hiện hình" if d["core"] is True else "chưa hiện hình")}]
    if d["state"] in ("khong_hien", "chua_du_du_kien"):
        steps.append({"step": "Tổng luận", "text": STATE_VI[d["state"]] + (": cấu trúc lõi chưa đủ nên không xét tiếp." if d["state"] == "khong_hien" else ": thiếu dữ kiện nên không kết luận.")})
        return steps
    steps.append({"step": "Yếu tố hỗ trợ", "text": "; ".join(f"{e['label']} ({e['because']})" for e in act("boosters")) or "chưa có"})
    steps.append({"step": "Yếu tố phá và cứu", "text": ("phá: " + "; ".join(f"{e['label']} ({e['because']})" for e in act("breakers")) if act("breakers") else "không có yếu tố phá")
                  + (" | cứu: " + "; ".join(f"{e['label']} ({e['because']})" for e in act("rescuers")) if act("rescuers") else "")})
    steps.append({"step": "Phản chứng", "text": "; ".join(f"{e['label']} ({e['because']})" for e in act("refutations")) or "không có"})
    why = {"thanh_thuong": "không có yếu tố phá và có từ hai yếu tố tăng thế", "thanh": "không có yếu tố phá, có ít nhất một yếu tố tăng thế",
           "hinh_thuc": "không có yếu tố phá nhưng chưa có yếu tố tăng thế", "bi_pha": "có yếu tố phá chưa được cứu",
           "pha_duoc_cuu": "có yếu tố phá nhưng mọi yếu tố phá đều đã được cứu giải"}[d["state"]]
    if d["downgraded_by_refutation"]:
        why += "; phản chứng hạ xuống một bậc"
    steps.append({"step": "Tổng luận", "text": f"{STATE_VI[d['state']]}: {why}."})
    return steps


def _caveats_vi(f, d: dict) -> list[str]:
    """Replace the engine's id-based caveat by plain Vietnamese (labels, and why the data is missing)."""
    out = [c for c in d["caveats"] if not c.startswith("có điều kiện chưa đủ")]
    if d["unknown"]:
        lab = {(k, e.id): e for k in ("boosters", "breakers", "rescuers", "refutations") for e in getattr(f, k)}
        parts = []
        for u in d["unknown"]:
            kind, eid = u.split(":", 1)
            e = lab[(kind, eid)]
            why = " (bảng độ sáng chưa ghi vị trí này của sao)" if "tp_rank" in str(e.when) else ""
            parts.append(f"{KIND_VI[kind].lower()}: {e.label}{why}")
        out.append("có điều kiện chưa đủ dữ kiện nên không được tính là sai: " + "; ".join(parts))
    return out


def analyse(tv, formations) -> list[dict]:
    ch = _Chart(tv)
    out = []
    from .reasoning.formation_eval import render_vi
    for f in formations:
        subj = f"palace:{f.anchor}"
        if subj not in ch.base:
            continue
        d = evaluate_formation(f, ch.facts_of(subj), ch.world)
        d["caveats"] = _caveats_vi(f, d)
        core_items = highlight(ch, f.core, f.anchor) if d["core"] is True else []
        ev = _evidence(ch, f, d)
        out.append({"id": f.id, "name_vi": f.name_vi, "anchor": f.anchor, "state": d["state"], "state_vi": STATE_VI[d["state"]],
                    "text": render_vi(f, d), "core": {"active": d["core"] is True, "items": core_items, "because": sentence(core_items)},
                    "evidence": ev, "chain": _chain(f, d, core_items, ev), "missing": d["missing_for_next_level"],
                    "caveats": d["caveats"], "downgraded": d["downgraded_by_refutation"], "uncovered": d["uncovered_breakers"],
                    "experimental": True, "review": "draft"})
    return out
