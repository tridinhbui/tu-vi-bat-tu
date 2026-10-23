"""The 'why' behind the Bát Tự verdicts, as computed facts for the reader prose (plan: deeper Bát Tự reading, 2026-10-22). Nothing here decides
anything new: it takes apart what the verified methods already computed and names the parts with the vocabulary of the page they come from.
  - score:     Thiệu Vĩ Hoa's 40% verdict taken apart (pp.331-355): phe mình in degrees against 40% of the total, heaven / earth, the month's
               +1/5 and -1/5 (and whether the verdict stands without them), the margin in degrees and in rooted stems (36 degrees each, p.332).
  - stems:     each stem's degrees and why they moved: chỗ dựa or hư phù (p.333), ngũ hợp hóa / không hóa and the reason (p.336), khắc between
               stems (p.332), the same-pillar can-chi relation; the day master's roots by name.
  - units:     the branch combinations considered by the score and whether they hóa (pp.338-346).
  - flow:      the five elements as ten-god groups in degrees, and which sinh links of the groups the chart holds (the cycle Tỉ Kiếp ->
               Thực Thương -> Tài -> Quan Sát -> Ấn -> Tỉ Kiếp, by element; the link names are the ones of TVH pp.367-369, 377-383).
  - yong:      the useful god of the cách table with the book's reason (pp.377-383, data/bazi_deep/tvh_mechanism.json), its fallback order
               ("không có X thì lấy Y"), where it stands in the chart, and what in the chart sinh / khắc / hợp / xung it (hỉ / kỵ thần by
               relation, p.382).
  - luck/year: the stem governs the first five years of a luck pillar, the branch the last five (p.382); what a luck pillar or a year does
               to the natal useful god (sinh, khắc, hợp, xung: p.382).
  - dh_note:   the printed note of the chart's điều hậu cell (pp.391-397), with whether a 'cục' it names is formed in the chart."""
from __future__ import annotations

import json

from ..bazi import HIDDEN_STEMS, SIX_CLASH, STEM_COMBINE
from ..ganzhi import BRANCH_ELEMENT, BRANCHES_VI, ELEMENTS, STEM_ELEMENT, STEMS_VI, controls, generates
from .model import PILLARS, ChartView
from .profile import DATA
from .strength import group_of_element

GROUP_VI = {"Ti": "Tỉ Kiếp", "ThucThuong": "Thực Thương", "Tai": "Tài", "QuanSat": "Quan Sát", "An": "Ấn"}
VI_GROUP = {v: k for k, v in GROUP_VI.items()}
MECH = json.loads((DATA / "tvh_mechanism.json").read_text("utf-8"))
DH = json.loads((DATA / "tvh_dieuhau.json").read_text("utf-8"))
UNIT_VI = {"hoi": "tam hội", "hop": "tam hợp", "ban": "bán tam hợp", "luc": "lục hợp"}


def _mother(el: str) -> str:
    return ELEMENTS[(ELEMENTS.index(el) - 1) % 5]


def _el_of_group(dm_el: str, g: str) -> str:
    i = ELEMENTS.index(dm_el)
    return {"Ti": dm_el, "ThucThuong": ELEMENTS[(i + 1) % 5], "Tai": ELEMENTS[(i + 2) % 5], "QuanSat": ELEMENTS[(i + 3) % 5], "An": ELEMENTS[(i + 4) % 5]}[g]


def score(view: ChartView, tvh: dict) -> dict:
    """Thiệu Vĩ Hoa's verdict in degrees, the way the book sets out its own examples (p.355: phe mình = own degrees; 40% of the total)."""
    dm_el = tvh["dm_element"]
    own_els = [dm_el, _mother(dm_el)]
    tot, pre = tvh["totals"], tvh["totals_before_lenh"]
    total, own = sum(tot.values()), sum(tot[e] for e in own_els)
    total0, own0 = sum(pre.values()), sum(pre[e] for e in own_els)
    need = 0.4 * total
    lenh = tvh["lenh"]
    minus = next((e for e in ELEMENTS if controls(lenh, e)), None)
    share0 = own0 / (total0 or 1)
    els = [{"el": e, "group": GROUP_VI[group_of_element(dm_el, e)], "heaven": round(tvh["heaven"][e], 1), "earth": round(tvh["earth"][e], 1),
            "lenh": "+" if e == lenh else "-" if e == minus else None, "total": round(tot[e], 1)} for e in ELEMENTS]
    return {"own_elements": own_els, "own": round(own, 1), "total": round(total, 1), "need": round(need, 1), "gap": round(own - need, 1),
            "gap_stems": round(abs(own - need) / 36, 1), "lenh": lenh, "lenh_minus": minus, "share_without_lenh": round(share0, 4),
            "lenh_decides": (share0 >= 0.4) != bool(tvh["dm_strong"]), "elements": els,
            "heaven_own": round(sum(tvh["heaven"][e] for e in own_els), 1), "earth_own": round(sum(tvh["earth"][e] for e in own_els), 1),
            "src": "TVH pp.331-355"}


def stems(view: ChartView, tvh: dict) -> dict:
    """Each stem's degrees and what moved them (TVH pp.332-336), and the day master's roots by name (p.333)."""
    d = tvh.get("detail") or {}
    root = d.get("root") or [True] * 4
    out = []
    for i, p in enumerate(PILLARS):
        s = view.stem(p)
        x = {"pillar": p, "stem": STEMS_VI[s], "ten_god": "Nhật chủ" if p == "day" else view.god(s), "element": STEM_ELEMENT[s], "deg": tvh["stem_deg"][i],
             "rooted": bool(root[i])}
        for h in d.get("hop", []):
            if i in h["pair"]:
                j = h["pair"][1] if h["pair"][0] == i else h["pair"][0]
                x["hop"] = {"with": PILLARS[j], "with_stem": STEMS_VI[view.stems[j]], "el": h["el"], "outcome": h["outcome"], "why": h.get("why"),
                            "victim": h.get("victim") == i if "victim" in h else None}
        for k in d.get("khac", []):
            if k["target"] == i:
                x["khac"] = {"by": [PILLARS[a] for a in k["by"]], "by_stem": [STEMS_VI[view.stems[a]] for a in k["by"]], "loss": k["loss"], "kep": k["kep"]}
        for t in d.get("tru", []):
            if t["pillar"] == i:
                x["tru"] = {"kind": t["kind"], "loss": t["loss"], "branch": BRANCHES_VI[view.branch(p)]}
        out.append(x)
    # the day master's roots: hidden stems anywhere of its element or the one that generates it (p.333), after the combinations and xung
    dm_el = tvh["dm_element"]
    roots = []
    units = d.get("units", [])
    khu = set(tvh.get("khu_bi", []))
    for i, p in enumerate(PILLARS):
        formed = next((u for u in units if u["hoa"] and u["taken"] and i in u["idx"]), None)
        hs = HIDDEN_STEMS[view.branch(p)]
        if formed:
            if formed["el"] == dm_el or generates(formed["el"], dm_el):
                roots.append({"pillar": p, "branch": BRANCHES_VI[view.branch(p)], "via": f"cuc_{formed['el']}"})
            continue
        for k, h in enumerate(hs[:1] if i in khu else hs):
            e = STEM_ELEMENT[h]
            if e == dm_el or generates(e, dm_el):
                roots.append({"pillar": p, "branch": BRANCHES_VI[view.branch(p)], "stem": STEMS_VI[h], "same": e == dm_el, "main": k == 0})
    return {"stems": out, "dm_roots": roots, "dm_rooted": bool(root[2]), "dm_root_main": bool((tvh.get("root_main") or [True] * 4)[2]),
            "hua_day": (tvh.get("hua_stem") or {}).get("day"), "src": "TVH pp.332-336"}


def units(view: ChartView, tvh: dict) -> list[dict]:
    """Branch combinations the score considered, with whether they hóa (TVH pp.338-346): formed ones add their degrees, the others keep the
    main qi only (khử bì)."""
    out = []
    for u in (tvh.get("detail") or {}).get("units", []):
        if not u["taken"]:
            continue
        out.append({"kind": u["kind"], "kind_vi": UNIT_VI[u["kind"]], "el": u["el"], "pillars": [PILLARS[i] for i in u["idx"]],
                    "branches": [BRANCHES_VI[view.branches[i]] for i in u["idx"]], "hoa": u["hoa"]})
    return out


def flow(view: ChartView, tvh: dict) -> dict:
    """The groups in degrees and the sinh links the chart holds. A group 'is there' when a stem other than the day master, or a branch's
    main qi, belongs to it; a link is told when both ends are there."""
    dm_el = tvh["dm_element"]
    by = {}
    for e in ELEMENTS:
        g = group_of_element(dm_el, e)
        by[g] = by.get(g, 0) + tvh["totals"][e]
    there = {}
    for p in PILLARS:
        if p != "day":
            there.setdefault(group_of_element(dm_el, STEM_ELEMENT[view.stem(p)]), []).append({"pillar": p, "part": "stem", "stem": STEMS_VI[view.stem(p)]})
        h = HIDDEN_STEMS[view.branch(p)][0]
        there.setdefault(group_of_element(dm_el, STEM_ELEMENT[h]), []).append({"pillar": p, "part": "branch", "stem": STEMS_VI[h]})
    cyc = ["Ti", "ThucThuong", "Tai", "QuanSat", "An"]
    links = [{"from": GROUP_VI[a], "to": GROUP_VI[b] if b != "Ti" else "thân", "visible": any(x["part"] == "stem" for x in there.get(a, [])) and (b == "Ti" or any(x["part"] == "stem" for x in there.get(b, [])))}
             for a, b in zip(cyc, cyc[1:] + cyc[:1]) if a in there and (b in there or b == "Ti")]
    tot = sum(by.values()) or 1
    return {"groups": sorted(({"group": GROUP_VI[g], "el": _el_of_group(dm_el, g), "deg": round(v, 1), "share": round(v / tot, 3)} for g, v in by.items()), key=lambda x: -x["deg"]),
            "there": {GROUP_VI[g]: xs for g, xs in there.items()}, "links": links}


def _why(G: str, D: str, strong: bool) -> dict | None:
    """The book's reason for taking group G as the useful god when D is the largest group (TVH pp.378-383)."""
    for r in MECH["dungthan_why"]["rows"]:
        if r["yong"] == G and r["dom"] in (D, "*") and r["dm"] in ("strong" if strong else "weak", "*"):
            return {"text": r["text"], "page": r["page"]}
    return None


def _place(view: ChartView, el: str) -> dict:
    """Where an element stands in the four pillars: stems (the day master aside) and hidden stems."""
    vis = [{"pillar": p, "stem": STEMS_VI[view.stem(p)]} for p in PILLARS if p != "day" and STEM_ELEMENT[view.stem(p)] == el]
    hid = [{"pillar": p, "branch": BRANCHES_VI[view.branch(p)], "stem": STEMS_VI[h], "main": k == 0} for p in PILLARS for k, h in enumerate(HIDDEN_STEMS[view.branch(p)]) if STEM_ELEMENT[h] == el]
    return {"visible": vis, "hidden": hid}


def touches(view: ChartView, stem: int | None, branch: int | None, yong_el: str) -> list[dict]:
    """What a stem / branch does to the useful god (TVH p.382: what sinh it or khắc the kỵ is hỉ; what khắc, xung or hợp it is kỵ). For a
    luck pillar or a year: its own element against the useful god's, its hợp with a natal useful-god stem, its xung with a natal branch whose
    main qi is the useful god. Elements only; the meaning is p.382's."""
    out = []
    ky_el = next(e for e in ELEMENTS if controls(e, yong_el))
    if stem is not None:
        e = STEM_ELEMENT[stem]
        if e == yong_el:
            out.append({"kind": "mang_yong", "part": "stem", "who": STEMS_VI[stem]})
        elif generates(e, yong_el):
            out.append({"kind": "sinh_yong", "part": "stem", "who": STEMS_VI[stem]})
        elif controls(e, yong_el):
            out.append({"kind": "khac_yong", "part": "stem", "who": STEMS_VI[stem]})
        for p in PILLARS:
            ns = view.stem(p)
            if p == "day" or frozenset((stem, ns)) not in STEM_COMBINE:
                continue
            if STEM_ELEMENT[ns] == yong_el:           # it binds a natal useful-god stem
                out.append({"kind": "hop_yong", "part": "stem", "who": STEMS_VI[stem], "target": p, "target_stem": STEMS_VI[ns]})
            elif e == yong_el:                        # it is a useful-god stem, bound by a natal stem
                out.append({"kind": "yong_bi_hop", "part": "stem", "who": STEMS_VI[stem], "target": p, "target_stem": STEMS_VI[ns]})
        if controls(e, ky_el):
            hit = [p for p in PILLARS if p != "day" and STEM_ELEMENT[view.stem(p)] == ky_el]
            if hit:
                out.append({"kind": "khac_ky", "part": "stem", "who": STEMS_VI[stem], "targets": hit, "target_stems": [STEMS_VI[view.stem(p)] for p in hit]})
    if branch is not None:
        h = HIDDEN_STEMS[branch][0]
        if STEM_ELEMENT[h] == yong_el:
            out.append({"kind": "mang_yong", "part": "branch", "who": BRANCHES_VI[branch], "stem": STEMS_VI[h]})
        elif generates(STEM_ELEMENT[h], yong_el):
            out.append({"kind": "sinh_yong", "part": "branch", "who": BRANCHES_VI[branch], "stem": STEMS_VI[h]})
        elif controls(STEM_ELEMENT[h], yong_el):
            out.append({"kind": "khac_yong", "part": "branch", "who": BRANCHES_VI[branch], "stem": STEMS_VI[h]})
        for p in PILLARS:
            nb = view.branch(p)
            if frozenset((branch, nb)) in SIX_CLASH and STEM_ELEMENT[HIDDEN_STEMS[nb][0]] == yong_el:
                out.append({"kind": "xung_yong", "part": "branch", "who": BRANCHES_VI[branch], "target": p, "target_branch": BRANCHES_VI[nb]})
    return out


def yong(view: ChartView, tvh: dict, cct: dict, ttv: dict) -> dict | None:
    """The useful god with its reason, fallback, place in the chart and natal health (TVH pp.377-383)."""
    dm_el = tvh["dm_element"]
    if cct.get("status") == "ap_dung":
        alts = list(cct.get("yong_alternatives") or cct.get("yong") or [])
        strong = cct.get("dm") == "vượng"
        dom = cct.get("dominant")
        rows = []
        for g in alts:
            el = _el_of_group(dm_el, g)
            pl = _place(view, el)
            rows.append({"group": GROUP_VI[g], "el": el, "present": bool(pl["visible"] or pl["hidden"]), "visible": bool(pl["visible"]), **pl})
        use = next((r for r in rows if r["present"]), rows[0] if rows else None)
        why = _why(alts[rows.index(use)], dom, strong) if alts and use else None     # the reason of the group actually used (after a fallback)
        kind = "cach"
    elif ttv.get("status") == "ap_dung" and (ttv.get("need_elements") or ttv.get("yong")):
        # a special cách (TVH p.381): chuyên vượng and hóa take the cách's own element; tòng tài / sát / nhi the groups of the book's row
        els = ttv.get("need_elements") or [_el_of_group(dm_el, g) for g in ttv["yong"]]
        rows = []
        for el in els:
            pl = _place(view, el)
            rows.append({"group": GROUP_VI[group_of_element(dm_el, el)], "el": el, "present": bool(pl["visible"] or pl["hidden"]), "visible": bool(pl["visible"]), **pl})
        use, why, kind, strong, dom = rows[0], None, "special", None, None
    else:
        return None
    if not use:
        return None
    el = use["el"]
    ky_el = next(e for e in ELEMENTS if controls(e, el))
    hy_el = _mother(el)
    natal = []
    for p in PILLARS:
        if p == "day":
            continue
        s = view.stem(p)
        if STEM_ELEMENT[s] == ky_el:
            natal.append({"kind": "khac_yong", "part": "stem", "pillar": p, "who": STEMS_VI[s]})
        elif STEM_ELEMENT[s] == hy_el:
            natal.append({"kind": "sinh_yong", "part": "stem", "pillar": p, "who": STEMS_VI[s]})
    for p in PILLARS:                     # a natal hợp that binds a useful-god stem, a natal xung on a branch whose main qi is the useful god
        s = view.stem(p)
        if STEM_ELEMENT[s] == el and p != "day":
            for q in PILLARS:
                if q != p and abs(PILLARS.index(q) - PILLARS.index(p)) == 1 and frozenset((s, view.stem(q))) in STEM_COMBINE:
                    natal.append({"kind": "hop_yong", "part": "stem", "pillar": p, "who": STEMS_VI[s], "with": q, "with_stem": STEMS_VI[view.stem(q)]})
        b = view.branch(p)
        if STEM_ELEMENT[HIDDEN_STEMS[b][0]] == el:
            for q in PILLARS:
                if q != p and frozenset((b, view.branch(q))) in SIX_CLASH:
                    natal.append({"kind": "xung_yong", "part": "branch", "pillar": p, "who": BRANCHES_VI[b], "with": q, "with_branch": BRANCHES_VI[view.branch(q)]})
    hy_g, ky_g = GROUP_VI[group_of_element(dm_el, hy_el)], GROUP_VI[group_of_element(dm_el, ky_el)]
    out = {"kind": kind, "group": use["group"], "el": el, "first": rows[0]["group"], "fallback": use is not rows[0], "alternatives": rows,
           "why": why, "dm": "vượng" if strong else "nhược" if strong is not None else None, "dominant": GROUP_VI.get(dom) if dom else None,
           "hy": {"group": hy_g, "el": hy_el}, "ky": {"group": ky_g, "el": ky_el}, "natal": natal, "src": "TVH pp.377-383"}
    if kind == "cach":
        tot = [GROUP_VI[g] for g in cct.get("van_tot") or []]
        xau = [GROUP_VI[g] for g in cct.get("van_xau") or []]
        # the hỉ / kỵ of p.382 against the luck table of the same cách (pp.382-386): a group the table leaves out is told by relation only
        out["table_vs_relation"] = {"hy_in_tot": hy_g in tot, "hy_in_xau": hy_g in xau, "ky_in_xau": ky_g in xau, "ky_in_tot": ky_g in tot}
    return out


def luck_reason(view: ChartView, tvh: dict, group: str, verdict: str | None, yong_d: dict | None) -> list[dict]:
    """Why the cách table calls a luck group good or bad, in the words of TVH pp.377-382 (data tvh_mechanism.json `van_why`): a group that
    is the useful god or sinh it, or khắc what khắc it (hỉ, p.382); one that khắc it (kị, p.382), what it does to the day master, and whether
    it adds to the largest group (the bệnh, p.377). At most two reasons, the first the strongest."""
    if not verdict or not yong_d:
        return []
    if yong_d["kind"] == "special":                    # p.381: a special cách follows its own momentum; the luck list pp.385-386 is what agrees with it
        k = "thuan_the" if verdict == "tot" else "nghich_the"
        return [{"key": k, **MECH["van_why"][k]}]
    dm_el = tvh["dm_element"]
    g = VI_GROUP.get(group, group)
    el = _el_of_group(dm_el, g)
    y_el = yong_d["el"]
    W = MECH["van_why"]
    R = lambda k: {"key": k, **W[k]}
    if verdict == "tot":
        if group == yong_d["group"] or el == y_el:
            return [R("is_yong")]
        if generates(el, y_el):
            return [R("sinh_yong")]
        if controls(el, yong_d["ky"]["el"]):
            return [R("khac_ky")]
        return []
    out = []
    if controls(el, y_el):
        out.append(R("khac_yong"))
    key = f"{'strong' if yong_d['dm'] == 'vượng' else 'weak'}_{g}"
    if key in W and not (out and y_el == dm_el):       # "khắc dụng thần" already says it when the useful god is the day master's own element
        out.append(R(key))
    dom = VI_GROUP.get(yong_d.get("dominant") or "")
    if dom and g == dom:
        out.append(R("add_dom"))
    elif dom and generates(el, _el_of_group(dm_el, dom)):
        out.append(R("sinh_dom"))
    return out[:2]


def halves(first_year: int | None) -> dict | None:
    """TVH p.382: in a luck pillar the stem governs the first five years, the branch the last five."""
    if first_year is None:
        return None
    return {"stem": [first_year, first_year + 4], "branch": [first_year + 5, first_year + 9], "src": "TVH p.382"}


def dh_note(view: ChartView, tvh: dict) -> dict | None:
    """The printed note of the điều hậu cell (TVH pp.391-397), following 'như tháng X' to the note it points to, and which 'cục' it names
    the chart has (the formed branch combinations of the score)."""
    notes = DH.get("notes_text") or {}
    mb, dm = BRANCHES_VI[view.month_branch], STEMS_VI[view.dm]
    n = (notes.get(mb) or {}).get(dm)
    if not n:
        return None
    say, ref = n.get("say"), n.get("ref")
    seen = {mb}
    while not say and ref and ref not in seen:
        seen.add(ref)
        m = (notes.get(ref) or {}).get(dm) or {}
        say, ref = m.get("say"), m.get("ref")
    if not say:
        return None
    formed = {u["el"] for u in tvh.get("branch_units", [])}
    named = [e for e in ELEMENTS if f"{e.lower()} cục" in say.lower() or f"{e} cục" in say]
    return {"cell": f"{dm}/{mb}", "text": n.get("text"), "say": say, "via": n.get("ref"), "page": n.get("page"),
            "cuc": [{"el": e, "formed": e in formed} for e in named], "id": f"BT_TVH_DHN_{STEMS_VI.index(dm)}_{view.month_branch}"}
