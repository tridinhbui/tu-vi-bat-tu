"""Side-by-side FACTS for two Bát Tự charts: Nhật Chủ and day branch. No compatibility score, no verdict:
a 'hợp' or 'xung' only says the two characters touch each other (see 八字真宗 pp.19-20 for the relation tables)."""
from __future__ import annotations

from .bazi import BaziChart, DESTROY, HARM, SIX_CLASH, SIX_COMBINE, STEM_CLASH, STEM_COMBINE, ten_god
from .ganzhi import BRANCHES_VI, STEMS_VI, STEM_ELEMENT, controls, generates, stem_polarity


def _element_link(a: str, b: str) -> dict:
    if a == b:
        return {"kind": "cùng hành", "text": f"Hai Nhật Chủ cùng hành {a}."}
    for x, y, who in ((a, b, "A"), (b, a, "B")):
        if generates(x, y):
            return {"kind": "sinh", "from": who, "text": f"Hành {x} (người {who}) sinh hành {y}."}
        if controls(x, y):
            return {"kind": "khắc", "from": who, "text": f"Hành {x} (người {who}) khắc hành {y}."}
    raise AssertionError("two distinct elements are always linked")


def compare(a: BaziChart, b: BaziChart) -> dict:
    sa, sb = a.day_master, b.day_master
    ea, eb = STEM_ELEMENT[sa], STEM_ELEMENT[sb]
    pair = frozenset((sa, sb))
    if sa != sb and pair in STEM_COMBINE:
        stem_rel = {"kind": "can_hợp", "text": f"{STEMS_VI[sa]} và {STEMS_VI[sb]} là một cặp Thiên can hợp (hóa {STEM_COMBINE[pair]} theo bảng; việc có hóa thật hay không chưa xét).", "transforms": None}
    elif pair in STEM_CLASH:
        stem_rel = {"kind": "can_xung", "text": f"{STEMS_VI[sa]} và {STEMS_VI[sb]} là một cặp Thiên can xung."}
    elif sa == sb:
        stem_rel = {"kind": "trùng", "text": f"Hai Nhật Chủ cùng là {STEMS_VI[sa]}."}
    else:
        stem_rel = {"kind": "không", "text": f"{STEMS_VI[sa]} và {STEMS_VI[sb]} không hợp cũng không xung theo bảng Thiên can."}

    ba, bb = a.pillars["day"].branch, b.pillars["day"].branch
    bp = frozenset((ba, bb))
    names = f"{BRANCHES_VI[ba]} và {BRANCHES_VI[bb]}"
    branch_rels = []
    if ba == bb:
        branch_rels.append({"kind": "chi_trùng", "text": f"Hai ngày chi cùng là {BRANCHES_VI[ba]}."})
    for name, tbl in (("lục hợp", SIX_COMBINE), ("xung", SIX_CLASH), ("hại", HARM), ("phá", DESTROY)):
        if bp in tbl:
            branch_rels.append({"kind": f"chi_{name}", "text": f"{names} là một cặp Địa chi {name}."})
    if not branch_rels:
        branch_rels.append({"kind": "không", "text": f"{names} không thuộc cặp lục hợp, xung, hại hay phá nào trong bảng."})

    def side(c: BaziChart) -> dict:
        d = c.pillars["day"]
        return {"day_pillar": d.name, "day_master": STEMS_VI[c.day_master], "element": c.day_master_element,
                "polarity": stem_polarity(c.day_master), "day_branch": BRANCHES_VI[d.branch]}

    return {"a": side(a), "b": side(b),
            "ten_god_of_b_for_a": ten_god(sa, sb), "ten_god_of_a_for_b": ten_god(sb, sa),
            "element_link": _element_link(ea, eb), "day_master_stems": stem_rel, "day_branches": branch_rels,
            "note": "Chỉ là dữ kiện về hai chữ chạm nhau, không phải điểm hợp hay khắc và không kết luận về mối quan hệ."}


def compare_full(na, bz_a: BaziChart, tv_a, gender_a: str, nb, bz_b: BaziChart, tv_b, gender_b: str, experimental: bool = False) -> dict:
    """Result of compare() plus the multi-layer analysis under "v2" (see compare_deep). na/nb are the normalized births."""
    from .bazi_deep.model import ChartView
    from .compare_deep import Side, analyse
    out = compare(bz_a, bz_b)
    out["v2"] = analyse(Side(bz_a, ChartView.from_bazi(bz_a, na.utc, gender_a), tv_a), Side(bz_b, ChartView.from_bazi(bz_b, nb.utc, gender_b), tv_b), experimental)
    return out
