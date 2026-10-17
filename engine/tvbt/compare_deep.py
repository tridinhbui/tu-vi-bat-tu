"""Multi-layer comparison of two charts (facts only; no compatibility score, no verdict on marriage or character).

Order of work, as the books read a chart: (1) the structure of each chart on its own — nguyệt lệnh, which side of the 40% line the Nhật Chủ is on,
roots and thấu can; (2) only then the contacts between the two: four pillars × four pillars, Thập Thần seen from both sides, Thiên can and Địa chi
relations, groups of three branches that need characters from both people; (3) Tử Vi (compare_tuvi, an independent engine); (4) a tier for every item:
  direct        a relation between specific characters (tables of 八字真宗 pp.19-20)
  support/limit factors that make a relation more or less supported; ONLY from rules marked verified or partial — today none qualify, so they appear
                in experimental mode only (see data/compare_rules.json)
  insufficient  what this comparison does NOT decide, with the reason
Every item carries its rule id, status and source so the UI can show them. Items whose rule is `draft` are returned only when experimental=True."""
from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path

from . import compare_tuvi
from .bazi import (DESTROY, HARM, MEETING, PENALTY_PAIR, PENALTY_TRIPLES, SELF_PENALTY, SIX_CLASH, SIX_COMBINE, STEM_CLASH, STEM_COMBINE, TRIAD, BaziChart)
from .bazi_deep import position, season, tvh_cach, tvh_score
from .bazi_deep.model import PILLARS, PIL_VI, ChartView, group_of
from .bazi_deep.profile import TVH_40
from .ganzhi import BRANCHES_VI, BRANCH_ELEMENT, ELEMENTS, STEMS_VI, STEM_ELEMENT
from .tuvi import TuViChart

DATA = Path(__file__).resolve().parent.parent / "data"
RULES: dict = json.loads((DATA / "compare_rules.json").read_text("utf-8"))["rules"]
OWNER_VI = {"a": "A", "b": "B"}
PAIR_TABLES = [("branch_six_combine", "lục hợp", SIX_COMBINE), ("branch_clash", "xung", SIX_CLASH), ("branch_harm", "hại", HARM), ("branch_destroy", "phá", DESTROY)]
ROLES = {"year": "gốc gác, ông bà (cách gọi thông dụng)", "month": "cha mẹ, môi trường làm việc; chi tháng là nguyệt lệnh",
         "day": "bản thân (Nhật Chủ) và bạn đời (qua Nhật Chi)", "hour": "con cái, giai đoạn sau"}
FOCUS_MARGIN = TVH_40.tvh_margin


@dataclass
class Side:
    bz: BaziChart
    view: ChartView
    tv: TuViChart


def _sources() -> dict:
    out = {}
    for f in (DATA / "sources.json", DATA / "bazi_deep" / "sources_books.json"):
        for s in json.loads(f.read_text("utf-8"))["sources"]:
            out[s["id"]] = {"id": s["id"], "title": s["title"], "verified": bool(s.get("verified")), "edition_note": s.get("note")}
    return out


SOURCES = _sources()


def rule_info(rid: str) -> dict:
    r = RULES[rid]
    src = SOURCES.get(r["source"]) if r["source"] else None
    return {"id": rid, "title": r["title"], "text": r["text"], "status": r["status"], "evidence": r["evidence"],
            "source": ({**src, "locator": r["locator"]} if src else None)}


def make_item(id_: str, layer: str, tier: str, kind: str, title: str, plain: str, data, rule: str, *, kind_vi: str = "", school_dependent: bool = False) -> dict:
    return {"id": id_, "layer": layer, "tier": tier, "kind": kind, "kind_vi": kind_vi, "title": title, "plain": plain, "data": data, "rule": rule,
            "status": RULES[rule]["status"], "evidence": RULES[rule]["evidence"], "experimental": RULES[rule]["status"] == "draft", "school_dependent": school_dependent}


# ---------------------------------------------------------------- characters
def _tokens(side: str, v: ChartView) -> list[dict]:
    t = []
    for p in PILLARS:
        t.append({"owner": side, "slot": p, "type": "stem", "idx": v.stem(p), "name": STEMS_VI[v.stem(p)]})
        t.append({"owner": side, "slot": p, "type": "branch", "idx": v.branch(p), "name": BRANCHES_VI[v.branch(p)]})
    return t


def _ref(tok: dict) -> dict:
    return {"owner": tok["owner"], "slot": tok["slot"], "type": tok["type"], "name": tok["name"]}


def _label(tok: dict) -> str:
    return f"{tok['name']} (trụ {PIL_VI[tok['slot']]} của {OWNER_VI[tok['owner']]})"


def _anchors(*toks: dict) -> list[str]:
    """Which structural pillars a relation touches: month branch commands the season; day is the Nhật Chủ / Nhật Chi."""
    out = []
    for t in toks:
        if t["slot"] == "month" and t["type"] == "branch":
            out.append(f"nguyệt lệnh của {OWNER_VI[t['owner']]}")
        if t["slot"] == "day":
            out.append("Nhật Chủ của " + OWNER_VI[t["owner"]] if t["type"] == "stem" else "Nhật Chi của " + OWNER_VI[t["owner"]])
    return out


# ---------------------------------------------------------------- structure of one chart
def _element_counts(v: ChartView) -> dict:
    c = {e: 0 for e in ELEMENTS}
    for p in PILLARS:
        c[STEM_ELEMENT[v.stem(p)]] += 1
        c[BRANCH_ELEMENT[v.branch(p)]] += 1
    return c


def structure(owner: str, s: Side) -> dict:
    """Facts about one chart on its own. `strength.decided` is False (and `side` None) when the 40% line cannot honestly be applied:
    the chart is within FOCUS_MARGIN of it, shows signs of a special structure (cách đặc biệt / tòng), or the calculation failed."""
    v = s.view
    from .bazi_deep.strength import group_of_element, GROUP_VI
    mb = BRANCHES_VI[v.month_branch]
    roots = [{"pillar": r["pillar"], "branch": r["branch"], "hidden": r["hidden"], "class": r["class"], "same_char": r["same_char"]}
             for r in position.roots(v, v.dm)]
    out = {
        "owner": owner, "pillars": v.name(), "day_master": STEMS_VI[v.dm], "dm_element": v.dm_element, "elements": _element_counts(v),
        "month": {"pillar": f"{STEMS_VI[v.stem('month')]} {mb}", "branch": mb,
                  "hidden": [{"stem": STEMS_VI[h["stem"]], "class": h["class"], "ten_god": h["ten_god"]} for h in v.hidden("month")]},
        "roots": roots, "has_root": bool(roots), "tou": position.tou(v), "special": [], "unsupported": [],
        "strength": {"decided": False, "side": None, "own_share": None, "threshold": 0.4, "borderline": False, "margin": None, "reason": "missing",
                     "method": "Thiệu Vĩ Hoa, quy tắc 40%"},
    }
    try:
        sc = tvh_score.score(v)
        specials = tvh_cach.special(v, {"tvh": sc}, TVH_40)
    except Exception as e:  # a failed step must never be papered over with a guess
        out["error"] = f"{type(e).__name__}: {e}"
        return out
    own, margin = sc["own_share"], abs(sc["own_share"] - sc["threshold"])
    lenh_el = sc["lenh"]
    out["month"].update({"ruling_element": lenh_el, "ruling_group": GROUP_VI[group_of_element(v.dm_element, lenh_el)],
                         "ruling_in_own_camp": group_of_element(v.dm_element, lenh_el) in ("Ti", "An")})
    border = margin < FOCUS_MARGIN
    reason = "special" if specials else "borderline" if border else "ok"
    out["special"] = [{"name": x["name"], "kind": x["kind"]} for x in specials]
    out["unsupported"] = sc["notes"].get("unsupported", [])
    out["strength"] = {"decided": reason == "ok", "side": ("vượng" if sc["dm_strong"] else "nhược") if reason == "ok" else None, "own_share": own,
                       "threshold": sc["threshold"], "borderline": border, "margin": round(margin, 4), "reason": reason, "method": "Thiệu Vĩ Hoa, quy tắc 40%"}
    return out


# ---------------------------------------------------------------- cross relations
def _stem_rel(ta: dict, tb: dict) -> dict | None:
    pair = frozenset((ta["idx"], tb["idx"]))
    if ta["idx"] == tb["idx"]:
        return {"kind": "stem_same", "vi": "cùng một Thiên can"}
    if pair in STEM_COMBINE:
        return {"kind": "stem_combine", "vi": "Thiên can hợp", "element": STEM_COMBINE[pair]}
    if pair in STEM_CLASH:
        return {"kind": "stem_clash", "vi": "Thiên can xung"}
    return None


def _branch_rels(ta: dict, tb: dict) -> list[dict]:
    pair, out = frozenset((ta["idx"], tb["idx"])), []
    if ta["idx"] == tb["idx"]:
        out.append({"kind": "branch_same", "vi": "cùng một Địa chi"})
        if ta["idx"] in SELF_PENALTY:
            out.append({"kind": "branch_self_penalty", "vi": "tự hình"})
    for kind, vi, tbl in PAIR_TABLES:
        if pair in tbl:
            out.append({"kind": kind, "vi": f"Địa chi {vi}"})
    if pair == PENALTY_PAIR:
        out.append({"kind": "branch_penalty", "vi": "hình vô lễ (Tý–Mão)"})
    return out


def _relation_items(tok_a: list[dict], tok_b: list[dict]) -> list[dict]:
    items = []
    for ta, tb in product(tok_a, tok_b):
        if ta["type"] != tb["type"]:
            continue
        rels = [_stem_rel(ta, tb)] if ta["type"] == "stem" else _branch_rels(ta, tb)
        for r in [x for x in rels if x]:
            rule = "CMP_STEM_REL" if ta["type"] == "stem" else "CMP_BRANCH_REL"
            same_slot = ta["slot"] == tb["slot"]
            plain = f"{_label(ta)} và {_label(tb)}: {r['vi']}"
            if r["kind"] == "stem_combine":
                plain += f" (theo bảng hóa {r['element']}; có hóa thật hay không chưa xét)"
            plain += "."
            anchors = _anchors(ta, tb)
            data = {"members": [_ref(ta), _ref(tb)], "relation": r["vi"], "same_slot": same_slot, "anchors": anchors}
            if "element" in r:
                data["table_element"] = r["element"]
            it = make_item(f"bz.{r['kind']}.{ta['slot']}-{tb['slot']}.{ta['type']}", "bazi", "direct", r["kind"], f"{ta['name']} (A, {PIL_VI[ta['slot']]}) – {tb['name']} (B, {PIL_VI[tb['slot']]})", plain, data, rule, kind_vi=r["vi"])
            items.append(it)
    return items


def _groups(tok_a: list[dict], tok_b: list[dict]) -> list[dict]:
    """Groups of 2-3 branches from the two charts together that contain at least one character from each person."""
    br = [t for t in tok_a + tok_b if t["type"] == "branch"]
    items, seen_full = [], []

    def combos(need: tuple[int, ...]):
        cands = [[t for t in br if t["idx"] == b] for b in need]
        if any(not c for c in cands):
            return
        done = set()
        for pick in product(*cands):
            if len({id(x) for x in pick}) < len(pick) or len({x["owner"] for x in pick}) < 2:
                continue
            key = frozenset((x["owner"], x["slot"]) for x in pick)
            if key not in done:
                done.add(key)
                yield list(pick)

    def emit(kind, vi, rule, members, extra, *, school=False, tag=""):
        names = " – ".join(_label(m) for m in members)
        plain = f"{names}: {vi}" + (f" ({extra['element']})" if "element" in extra else "") + "."
        slots = "+".join(f"{m['owner']}{m['slot']}" for m in members)
        items.append(make_item(f"bz.{kind}{tag}.{slots}", "bazi", "direct", kind, " + ".join(m["name"] for m in members), plain,
                               {"members": [_ref(m) for m in members], "relation": vi, **extra, "anchors": _anchors(*members)}, rule, kind_vi=vi, school_dependent=school))

    for el, tri in TRIAD.items():
        for m in combos(tri):
            seen_full.append(frozenset((x["owner"], x["slot"]) for x in m)); emit("branch_triad", "tam hợp", "CMP_BRANCH_GROUP", m, {"element": el})
    for el, tri in MEETING.items():
        for m in combos(tri):
            seen_full.append(frozenset((x["owner"], x["slot"]) for x in m)); emit("branch_meeting", "tam hội", "CMP_BRANCH_GROUP", m, {"element": el})
    for name, tri in PENALTY_TRIPLES.items():
        for m in combos(tri):
            seen_full.append(frozenset((x["owner"], x["slot"]) for x in m)); emit("branch_penalty", f"hình ba chi ({name})", "CMP_BRANCH_GROUP", m, {"subtype": name}, school=True)
    covered = lambda m: any(frozenset((x["owner"], x["slot"]) for x in m) <= f for f in seen_full)
    for el, tri in TRIAD.items():
        for (x, y), rule, vi in (((0, 1), "CMP_SEMI_TRIAD", "bán tam hợp sinh–vượng"), ((1, 2), "CMP_SEMI_TRIAD", "bán tam hợp vượng–mộ"), ((0, 2), "CMP_CUNG_TRIAD", "cặp sinh–mộ của tam hợp")):
            for m in combos((tri[x], tri[y])):
                if not covered(m):
                    emit("branch_semi_triad", vi, rule, m, {"element": el}, school=True, tag="." + el)
    for name, tri in PENALTY_TRIPLES.items():
        for x, y in ((0, 1), (1, 2), (0, 2)):
            for m in combos((tri[x], tri[y])):
                if not covered(m):
                    emit("branch_ban_hinh", f"bán hình ({name})", "CMP_BAN_HINH", m, {"subtype": name}, school=True, tag="." + name)
    return items


# ---------------------------------------------------------------- Thập Thần, both ways
def _seen_from(viewer: ChartView, other: ChartView, other_tokens: list[dict]) -> dict:
    rows = []
    for p in PILLARS:
        st = other.stem(p)
        god = viewer.god(st)
        rows.append({"slot": p, "kind": "stem", "char": STEMS_VI[st], "ten_god": god, "group": group_of(god), "is_day_master": p == "day"})
        for h in other.hidden(p):
            g = viewer.god(h["stem"])
            rows.append({"slot": p, "kind": "hidden", "char": STEMS_VI[h["stem"]], "class": h["class"], "ten_god": g, "group": group_of(g)})
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["ten_god"]] = counts.get(r["ten_god"], 0) + 1
    return {"rows": rows, "counts": counts}


def _ten_god_items(a: Side, b: Side, tok_a, tok_b) -> list[dict]:
    items = []
    for x, y, vx, vy, tk in (("a", "b", a.view, b.view, tok_b), ("b", "a", b.view, a.view, tok_a)):
        sf = _seen_from(vx, vy, tk)
        dm_row = next(r for r in sf["rows"] if r["kind"] == "stem" and r["is_day_master"])
        plain = f"Nhìn từ Nhật Chủ {OWNER_VI[x]} ({STEMS_VI[vx.dm]}), Nhật Chủ của {OWNER_VI[y]} ({STEMS_VI[vy.dm]}) mang tính {dm_row['ten_god']}. Cả bốn Thiên can và các can ẩn của {OWNER_VI[y]} được đọc lại theo góc nhìn này."
        items.append(make_item(f"bz.ten_god.{x}_sees_{y}", "bazi", "direct", "ten_god_view", f"{OWNER_VI[y]} nhìn từ Nhật Chủ {OWNER_VI[x]}", plain,
                               {"viewer": x, "viewer_day_master": STEMS_VI[vx.dm], "other": y, **sf}, "CMP_TEN_GOD", kind_vi="Thập Thần hai chiều"))
    return items


# ---------------------------------------------------------------- experimental (draft) items
def _experimental_items(a: Side, b: Side, sa: dict, sb: dict, rel_items: list[dict]) -> list[dict]:
    items = []
    # roles of the four pillars
    for p in PILLARS:
        items.append(make_item(f"bz.role.{p}", "bazi", "direct", "role", f"Trụ {PIL_VI[p].capitalize()}: vai trò thường gán", f"Trụ {PIL_VI[p]}: {ROLES[p]}.",
                               {"slot": p, "role": ROLES[p], "a": f"{STEMS_VI[a.view.stem(p)]} {BRANCHES_VI[a.view.branch(p)]}", "b": f"{STEMS_VI[b.view.stem(p)]} {BRANCHES_VI[b.view.branch(p)]}"}, "CMP_ROLES", kind_vi="Vai trò trụ"))
    # element fill
    def count(v):
        c = {e: 0 for e in ELEMENTS}
        for p in PILLARS:
            c[STEM_ELEMENT[v.stem(p)]] += 1; c[BRANCH_ELEMENT[v.branch(p)]] += 1
        return c
    ca, cb = count(a.view), count(b.view)
    for x, y, cx, cy in (("a", "b", ca, cb), ("b", "a", cb, ca)):
        fill = [e for e in ELEMENTS if cx[e] == 0 and cy[e] >= 3]
        if fill:
            items.append(make_item(f"bz.fill.{x}_{y}", "bazi", "support", "element_fill", f"Hành {OWNER_VI[x]} thiếu mà {OWNER_VI[y]} có nhiều", f"{OWNER_VI[x]} không có hành {', '.join(fill)} trên tám chữ; {OWNER_VI[y]} có từ ba chữ trở lên. Chưa biết hành đó có phải hành {OWNER_VI[x]} cần hay không.",
                                   {"needy": x, "elements": fill, "counts_needy": cx, "counts_other": cy}, "CMP_ELEMENT_FILL", kind_vi="Bù hành"))
    # the other person's day master in my month
    for x, y, vx, vy in (("a", "b", a.view, b.view), ("b", "a", b.view, a.view)):
        st = season.season_states(vx.month_branch)[vy.dm_element]
        items.append(make_item(f"bz.season.{x}_{y}", "bazi", "direct", "season_other", f"Nhật Chủ {OWNER_VI[y]} trong tháng sinh của {OWNER_VI[x]}", f"Nguyệt lệnh của {OWNER_VI[x]} là {BRANCHES_VI[vx.month_branch]}; hành {vy.dm_element} của Nhật Chủ {OWNER_VI[y]} ở trạng thái {st} trong tháng đó.",
                               {"month_branch": BRANCHES_VI[vx.month_branch], "element": vy.dm_element, "state": st}, "CMP_SEASON_OTHER", kind_vi="Mùa của người kia"))
    # balance direction (support / limit), from the 40% side of each chart
    for x, y, sx, vx, vy in (("a", "b", sa, a.view, b.view), ("b", "a", sb, b.view, a.view)):
        if not sx["strength"]["decided"]:
            continue
        pref = {"Ti", "An"} if sx["strength"]["side"] == "nhược" else {"Thuc", "Thuong", "Tai", "Quan", "Sat"}
        sf = _seen_from(vx, vy, [])
        same_dir = [r for r in sf["rows"] if r["group"] in pref]
        opp = [r for r in sf["rows"] if r["group"] not in pref]
        side = sx["strength"]["side"]
        head = f"Nhật Chủ {OWNER_VI[x]} đứng ở phía {side} của ngưỡng 40%"
        items.append(make_item(f"bz.balance.support.{x}", "bazi", "support", "balance", f"Chữ của {OWNER_VI[y]} đi cùng hướng cân bằng của {OWNER_VI[x]}", f"{head}. Có {len(same_dir)} chữ của {OWNER_VI[y]} thuộc nhóm {'Tỉ Kiếp, Ấn' if side == 'nhược' else 'Thực Thương, Tài, Quan Sát'}. Đây không phải dụng thần.", {"viewer": x, "side": side, "rows": same_dir}, "CMP_BALANCE", kind_vi="Hướng cân bằng"))
        items.append(make_item(f"bz.balance.limit.{x}", "bazi", "limit", "balance", f"Chữ của {OWNER_VI[y]} đi ngược hướng cân bằng của {OWNER_VI[x]}", f"{head}. Có {len(opp)} chữ của {OWNER_VI[y]} thuộc nhóm còn lại; thêm chúng chỉ làm lá số nghiêng thêm về phía đã có, chưa nói tốt hay xấu.", {"viewer": x, "side": side, "rows": opp}, "CMP_BALANCE", kind_vi="Hướng cân bằng"))
    # reinforcement and dispersal among the relations already found
    by_slot: dict[tuple, dict] = {}
    for it in rel_items:
        if it["kind"] in ("stem_combine", "stem_clash", "branch_six_combine", "branch_clash"):
            m = it["data"]["members"]
            by_slot.setdefault((m[0]["slot"], m[1]["slot"]), {})[it["kind"]] = it
    for (sa_, sb_), d in by_slot.items():
        for sk, bk, vi in (("stem_combine", "branch_six_combine", "cùng hợp"), ("stem_clash", "branch_clash", "cùng xung")):
            if sk in d and bk in d:
                items.append(make_item(f"bz.reinforce.{sa_}-{sb_}.{sk}", "bazi", "support", "reinforce", f"Trụ {PIL_VI[sa_]} của A và trụ {PIL_VI[sb_]} của B: Thiên can và Địa chi {vi}", f"Cả Thiên can lẫn Địa chi của hai trụ này đều {vi}, nên quan hệ hiện ra ở hai tầng. Chưa nói quan hệ đó thuận hay nghịch.", {"slots": [sa_, sb_], "relation": vi, "ids": [d[sk]["id"], d[bk]["id"]]}, "CMP_REINFORCE", kind_vi="Hai tầng cùng chiều"))
    partners: dict[tuple, list] = {}
    for it in rel_items:
        if it["kind"] in ("stem_combine", "branch_six_combine"):
            for m in it["data"]["members"]:
                partners.setdefault((m["owner"], m["slot"], m["type"], it["kind"]), []).append(it)
    for key, lst in partners.items():
        if len(lst) >= 2:
            o, sl, ty, kd = key
            items.append(make_item(f"bz.disperse.{o}{sl}.{ty}.{kd}", "bazi", "limit", "disperse", f"Một chữ của {OWNER_VI[o]} hợp với nhiều chữ", f"Chữ {ty == 'stem' and 'Thiên can' or 'Địa chi'} ở trụ {PIL_VI[sl]} của {OWNER_VI[o]} cùng lúc hợp với {len(lst)} chữ bên kia, nên quan hệ bị chia ra. Hệ thống chưa xét hợp nào là chính.", {"owner": o, "slot": sl, "ids": [x["id"] for x in lst]}, "CMP_REINFORCE", kind_vi="Hợp bị chia"))
    return items


# ---------------------------------------------------------------- what is not decided
def _insufficient(sa: dict, sb: dict, rel_items: list[dict]) -> list[dict]:
    out = []
    combos = [i for i in rel_items if i["kind"] == "stem_combine"]
    if combos:
        out.append(make_item("ins.hoa", "bazi", "insufficient", "unresolved", "Thiên can hợp có hóa hay không", f"Có {len(combos)} cặp Thiên can hợp giữa hai lá số. Việc hợp hóa thành hành khác hay chỉ hợp mà không hóa cần điều kiện về mùa, vị trí và sự giúp sức, chưa được xét cho hai người cùng lúc.", {"ids": [c["id"] for c in combos]}, "CMP_STEM_REL", kind_vi="Chưa đủ căn cứ"))
    for o, s in (("a", sa), ("b", sb)):
        st = s["strength"]
        if st["reason"] == "missing":
            out.append(make_item(f"ins.missing.{o}", "bazi", "insufficient", "missing", f"Thiếu dữ kiện để xét thế mạnh của {OWNER_VI[o]}", f"Bước tính thế mạnh của {OWNER_VI[o]} không chạy được ({s.get('error', 'không rõ lý do')}), nên so sánh không nêu vượng hay nhược.", {"error": s.get("error")}, "CMP_DATA_MISSING", kind_vi="Chưa đủ căn cứ"))
        elif st["reason"] == "special":
            names = ", ".join(x["name"] for x in s["special"])
            out.append(make_item(f"ins.special.{o}", "bazi", "insufficient", "special", f"Lá số {OWNER_VI[o]} có dấu hiệu cách đặc biệt", f"Lá số {OWNER_VI[o]} có dấu hiệu của {names}. Với các cách này không áp dụng cách xét vượng/nhược thông thường, nên so sánh không nói Nhật Chủ {OWNER_VI[o]} vượng hay nhược và không xếp chữ nào của người kia vào hướng cân bằng.", {"special": s["special"], "own_share": st["own_share"]}, "CMP_SPECIAL", kind_vi="Chưa đủ căn cứ"))
        elif st["reason"] == "borderline":
            out.append(make_item(f"ins.border.{o}", "bazi", "insufficient", "borderline", f"Nhật Chủ {OWNER_VI[o]} sát ngưỡng 40%", f"Phe của Nhật Chủ {OWNER_VI[o]} chiếm {st['own_share']:.1%}, cách ngưỡng {st['threshold']:.0%} chưa tới {FOCUS_MARGIN:.0%}; hệ thống không nói vượng hay nhược.", st, "CMP_STRENGTH_40", kind_vi="Chưa đủ căn cứ"))
        if s["unsupported"]:
            out.append(make_item(f"ins.unsupported.{o}", "bazi", "insufficient", "unsupported", f"Phần phương pháp 40% chưa hỗ trợ ({OWNER_VI[o]})", "; ".join(s["unsupported"]), {"notes": s["unsupported"]}, "CMP_STRENGTH_40", kind_vi="Chưa đủ căn cứ"))
    out.append(make_item("ins.yongshen", "bazi", "insufficient", "unresolved", "Dụng thần và cách cục của từng người", "So sánh này không ghép cách cục hay dụng thần của hai người, nên chưa nói chữ nào của người kia là thứ lá số này cần hoặc kỵ.", {}, "CMP_STRENGTH_40", kind_vi="Chưa đủ căn cứ"))
    out.append(make_item("ins.time", "bazi", "insufficient", "unresolved", "Đại vận và lưu niên của hai người", "Chưa so sánh vận theo thời gian: hai người đi qua các đại vận và năm khác nhau, và sách trong kho chưa nêu cách đặt chúng cạnh nhau.", {}, "CMP_TEN_GOD", kind_vi="Chưa đủ căn cứ"))
    out.append(make_item("ins.tuvi", "tuvi", "insufficient", "unresolved", "Ý nghĩa khi cung của hai người gặp nhau", "Sách Tử Vi trong kho nêu ý nghĩa của sao và cung trong lá số của một người. Khi hai cung thuộc hai người, hệ thống chỉ nêu vị trí và sao chung, không diễn giải.", {}, "CMP_TV_GEOMETRY", kind_vi="Chưa đủ căn cứ"))
    return out


# ---------------------------------------------------------------- entry point
TIER_NOTE = {
    "direct": "Quan hệ giữa các chữ cụ thể, lấy từ bảng đã đối chiếu sách.",
    "support": "Yếu tố làm quan hệ hoặc cấu trúc được nâng đỡ. Chưa có quy tắc đã xác minh đủ để kết luận; các gợi ý bản nháp chỉ hiện ở chế độ thử nghiệm.",
    "limit": "Yếu tố làm quan hệ bị hạn chế hoặc phân tán. Chưa có quy tắc đã xác minh đủ để kết luận; các gợi ý bản nháp chỉ hiện ở chế độ thử nghiệm.",
    "insufficient": "Điều so sánh này không kết luận, kèm lý do.",
}


def analyse(a: Side, b: Side, experimental: bool = False) -> dict:
    sa, sb = structure("a", a), structure("b", b)
    tok_a, tok_b = _tokens("a", a.view), _tokens("b", b.view)
    rel = _relation_items(tok_a, tok_b)
    grp = _groups(tok_a, tok_b)
    items = rel + grp + _ten_god_items(a, b, tok_a, tok_b)
    items += _experimental_items(a, b, sa, sb, rel)
    items.append(make_item("bz.elements", "bazi", "direct", "element_count", "Ngũ Hành trên tám chữ của hai người", "Số chữ theo từng hành trên tám chữ (Thiên can và chữ chính của Địa chi) của mỗi người.", {"a": sa["elements"], "b": sb["elements"]}, "CMP_ELEMENT_COUNT", kind_vi="Đếm hành"))
    tv_struct, tv_items = compare_tuvi.build(a.tv, b.tv, make_item, experimental)
    items += tv_items + _insufficient(sa, sb, rel)
    hidden = sum(1 for i in items if i["experimental"])
    if not experimental:
        items = [i for i in items if not i["experimental"]]
    used = {i["rule"] for i in items} | {"CMP_MONTH_ORDER", "CMP_STRENGTH_40"}
    tiers = {t: {"note": TIER_NOTE[t], "ids": [i["id"] for i in items if i["tier"] == t]} for t in ("direct", "support", "limit", "insufficient")}
    pillars = [{"slot": p, "a": f"{STEMS_VI[a.view.stem(p)]} {BRANCHES_VI[a.view.branch(p)]}", "b": f"{STEMS_VI[b.view.stem(p)]} {BRANCHES_VI[b.view.branch(p)]}",
                "a_ten_god": None if p == "day" else a.view.god(a.view.stem(p)), "b_ten_god": None if p == "day" else b.view.god(b.view.stem(p))} for p in PILLARS]
    return {"version": 2, "experimental": experimental, "hidden_experimental": hidden,
            "principle": "Chỉ nêu dữ kiện và mức căn cứ. Không có điểm tương hợp, không kết luận về hôn nhân hay tính cách, và sinh hay khắc không mặc định là tốt hay xấu.",
            "structure": {"a": sa, "b": sb}, "pillars": pillars, "tuvi_structure": tv_struct, "items": items, "tiers": tiers,
            "rules": {r: rule_info(r) for r in sorted(used)},
            "sources": sorted({r["source"]["id"]: r["source"] for r in (rule_info(x) for x in used) if r["source"]}.values(), key=lambda x: x["id"])}
