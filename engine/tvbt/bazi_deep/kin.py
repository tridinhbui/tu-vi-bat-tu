"""Tài, nghề, lục thân and lưu niên facts for the 八字真宗 direct judgements (pp.50-65, 73; DEEP-BAZI-2, 2026-10-23), and the rules that read them
(data/bazi_deep/pack_zz_kin.json, raw page text in data/bazi_deep/mined/). Nothing here is a reading: every fact is a position or a count, and the
words the manual itself defines are computed the way its own examples use them:
  - nodes:     the seven characters other than the day master (three stems, four branches by their main hidden stem, 本气), each with its ten god
               and ten-god group; two nodes are next to each other (相邻) when they are the stem and branch of one pillar or the same row of two
               neighbouring pillars. p.58 example 2 ("天干金不生异柱地支水": a stem does not feed the branch of another pillar) rules out the
               diagonal.
  - 流入日主:   p.50 condition 1, "财生官，官生印，印星要落在日支、月干、时干这三个位置之一": a Tài node next to a Quan Sát node next to an Ấn node
               standing at the day branch, the month stem or the hour stem (the three places next to the day master). For the work judgements
               (p.51 #3-5, p.53 example 3 "七杀...又生月干印星，谓官旺流入日主") the chain starts at Quan Sát.
  - 有根 / 通根: the stem's own branch or a neighbouring pillar's branch holds a same-element stem as main or middle qi (Chart.rooted: the
               manual's examples call a stem with only a residual or a distant root "无根"); 坐下通根 (p.53 example 1: "甲坐下通根旺效益好"): the
               stem's own branch hides one.
  - 得生 / 受生: a node next to it generates its element. 截脚: its own branch's element controls the stem; 盖头: the stem controls its own
               branch.
  - 墓 / 库:    the stem's growth stage on its own branch is Mộ (the 12-stage table of pp.24-25 the pillars already use); p.63 note: "月日之墓
               ...为墓，年时胎身命之墓为库".
  - 左柱:       p.52 #6-7 "以官星左柱论", "年柱的左柱为时柱"; p.53 examples 1-2 read the year pillar for a Quan in the month and the hour pillar for a
               Quan in the year: the left pillar is the one before, the year's is the hour's. The Quan pillar is the one pillar holding Quan
               Sát (a transparent Quan first); with none, Tài (p.51 #3 "官星不现，以财星论").
  - 胎身命:     胎元, 身宫, 命宫 by pp.35-38 (bazi.thai_yuan / ming_gong_branch / shen_gong_branch).
  - vượng / nhược of a ten-god group: its share of Thiệu Vĩ Hoa's degrees (pp.331-355) at least 25 % / under 12 % (the manual gives no measure:
               a system convention, said so in the note of every sentence that rests on it); "không có" = no stem and no hidden stem of the group.
"""
from __future__ import annotations

import json
from functools import lru_cache

from ..bazi import (HARM, HIDDEN_STEMS, PENALTY_PAIR, PENALTY_PAIRS, SELF_PENALTY, SIX_CLASH, SIX_COMBINE, STEM_COMBINE, growth_stage,
                    kong_wang, ming_gong_branch, shen_gong_branch, ten_god, thai_yuan)
from ..ganzhi import BRANCHES_VI, STEM_ELEMENT, STEMS_VI, branch_stem_from_year, controls, generates
from ..knowledge.schema import KnowledgeRule, Source
from ..reasoning import engine
from .model import PILLARS, ChartView
from .profile import DATA

GROUP = {"Tỉ Kiên": "Ti", "Kiếp Tài": "Ti", "Thực Thần": "ThucThuong", "Thương Quan": "ThucThuong", "Chính Tài": "Tai", "Thiên Tài": "Tai",
         "Chính Quan": "QuanSat", "Thất Sát": "QuanSat", "Chính Ấn": "An", "Thiên Ấn": "An"}
GROUP_VI = {"Ti": "Tỉ Kiếp", "ThucThuong": "Thực Thương", "Tai": "Tài", "QuanSat": "Quan Sát", "An": "Ấn"}
PIL_VI = {"year": "năm", "month": "tháng", "day": "ngày", "hour": "giờ"}
ZZ_REN = [3, 2, 6, 5, 6, 5, 9, 8, 0, 11]          # 羊刃 by day stem, the p.72 table (as reasoning/facts.py)
VUONG, NHUOC = 0.25, 0.12                        # group share of the TVH degrees: system convention (no page gives a measure)
TOMBS = {1, 4, 7, 10}                            # 辰戌丑未, the four 库 of p.64 #1
NEAR_DM = {("day", "branch"), ("month", "stem"), ("hour", "stem")}   # p.50 condition 1: 日支、月干、时干


def _hurt(a: int, b: int) -> bool:
    """刑冲穿 between two branches (穿 = 害); 绝 is not modelled, so a fact built on this can miss a case but never adds one"""
    p = frozenset((a, b))
    return p in SIX_CLASH or p in HARM or p == PENALTY_PAIR or p in PENALTY_PAIRS or (a == b and a in SELF_PENALTY)


def _hurt_vi(a: int, b: int) -> str:
    """the relation's name for the text: xung, hại, hình, tự hình"""
    p = frozenset((a, b))
    return "xung" if p in SIX_CLASH else "hại" if p in HARM else "tự hình với" if a == b else "hình" if (p == PENALTY_PAIR or p in PENALTY_PAIRS) else ""


def _void_of(stem: int, branch: int) -> list[int]:
    return kong_wang(stem, branch)


class Chart:
    """the seven nodes, their gods and the positions the judgements name"""

    def __init__(self, view: ChartView, tvh: dict | None):
        self.v, self.dm = view, view.dm
        self.nodes = [(p, r) for p in PILLARS for r in ("stem", "branch") if (p, r) != ("day", "stem")]
        self.tvh = tvh or {}

    def stem_of(self, n) -> int:
        p, r = n
        return self.v.stem(p) if r == "stem" else HIDDEN_STEMS[self.v.branch(p)][0]

    def god(self, n) -> str:
        return ten_god(self.dm, self.stem_of(n))

    def group(self, n) -> str:
        return GROUP[self.god(n)]

    def el(self, n) -> str:
        return STEM_ELEMENT[self.stem_of(n)]

    @staticmethod
    def adj(a, b) -> bool:
        if a == b:
            return False
        ia, ib = PILLARS.index(a[0]), PILLARS.index(b[0])
        return (ia == ib) or (a[1] == b[1] and abs(ia - ib) == 1)

    def of(self, *groups: str, gods: tuple[str, ...] = ()) -> list:
        return [n for n in self.nodes if self.group(n) in groups or self.god(n) in gods]

    def hidden_gods(self) -> set[str]:
        return {ten_god(self.dm, h) for p in PILLARS for h in HIDDEN_STEMS[self.v.branch(p)]} | {self.god(n) for n in self.nodes if n[1] == "stem"}

    def absent(self, g: str) -> bool:
        return not any(GROUP[x] == g for x in self.hidden_gods())

    def rooted(self, n) -> bool:
        """有根 as the manual's examples use it: a same-element main or middle hidden stem in the stem's own branch or a neighbouring pillar's.
        p.51 example 2 calls 戊 of 戊申 (with 戊 only as 申's residual qi, and as the main qi of 辰 two pillars away) "透干无根"; p.53 example 3
        calls 庚 of 庚寅 (with 辛 only in the 戌 of the day and hour pillars) "无根"."""
        e, i = self.el(n), PILLARS.index(n[0])
        return any(STEM_ELEMENT[h] == e for q in PILLARS if abs(PILLARS.index(q) - i) <= 1 for h in HIDDEN_STEMS[self.v.branch(q)][:2])

    def sits_on_root(self, p: str) -> bool:
        return any(STEM_ELEMENT[h] == STEM_ELEMENT[self.v.stem(p)] for h in HIDDEN_STEMS[self.v.branch(p)])

    def generated(self, n) -> bool:
        return any(generates(self.el(m), self.el(n)) for m in self.nodes + [("day", "stem")] if self.adj(m, n) and m != n)

    def cut(self, p: str) -> bool:        # 截脚
        return controls(STEM_ELEMENT[HIDDEN_STEMS[self.v.branch(p)][0]], STEM_ELEMENT[self.v.stem(p)])

    def covered(self, p: str) -> bool:    # 盖头
        return controls(STEM_ELEMENT[self.v.stem(p)], STEM_ELEMENT[HIDDEN_STEMS[self.v.branch(p)][0]])

    def tomb(self, p: str) -> bool:
        return growth_stage(self.v.stem(p), self.v.branch(p)) == "Mộ"

    def share(self, g: str) -> float | None:
        tot = self.tvh.get("totals")
        if not tot:
            return None
        from .depth import _el_of_group
        s = sum(tot.values()) or 1
        return tot[_el_of_group(STEM_ELEMENT[self.dm], g)] / s

    def flows(self, start: str) -> list:
        """the chain of p.50 condition 1 from `start` ('Tai' or 'QuanSat') to the day master, as the list of nodes, or [] when there is none"""
        ans = [n for n in self.of("An") if n in NEAR_DM]
        for a in ans:
            for q in self.of("QuanSat"):
                if not self.adj(q, a):
                    continue
                if start == "QuanSat":
                    return [q, a]
                for t in self.of("Tai"):
                    if t not in (q, a) and self.adj(t, q):
                        return [t, q, a]
        return []

    def tmm(self) -> list[tuple[str, int, int]]:
        ys, ms, mb, hb = self.v.stem("year"), self.v.stem("month"), self.v.branch("month"), self.v.branch("hour")
        ts, tb = thai_yuan(ms, mb)
        mg, sg = ming_gong_branch(mb, hb), shen_gong_branch(mb, hb)
        return [("thai", ts, tb), ("menh", branch_stem_from_year(ys, mg), mg), ("than", branch_stem_from_year(ys, sg), sg)]


def _label(c: Chart, n) -> str:
    p, r = n
    return f"{'can' if r == 'stem' else 'chi'} {PIL_VI[p]} {STEMS_VI[c.v.stem(p)] if r == 'stem' else BRANCHES_VI[c.v.branch(p)]}"


def natal_facts(view: ChartView, tvh: dict | None) -> tuple[dict, dict]:
    """(facts for the rules, detail for the prose: which characters, which pillar)"""
    c = Chart(view, tvh)
    v, dm = view, view.dm
    gender = {"male": "nam", "female": "nữ"}.get(view.gender or "")
    strong = (tvh or {}).get("dm_strong")
    share = {g: c.share(g) for g in GROUP_VI}
    vuong = [g for g, s in share.items() if s is not None and s >= VUONG]
    nhuoc = [g for g, s in share.items() if s is not None and s < NHUOC]
    absent = [g for g in GROUP_VI if g != "Ti" and c.absent(g)]
    stems = {p: ten_god(dm, v.stem(p)) for p in PILLARS if p != "day"}
    trans = lambda *gods: [p for p, g in stems.items() if g in gods]
    branch_main = {p: c.god((p, "branch")) for p in PILLARS}
    kw = _void_of(v.stem("day"), v.branch("day"))
    void_nodes = [(p, "branch") for p in PILLARS if p != "day" and v.branch(p) in kw]
    tmm = c.tmm()
    D: dict = {"tmm": [{"key": k, "stem": STEMS_VI[s], "branch": BRANCHES_VI[b], "god_stem": ten_god(dm, s), "god_branch": ten_god(dm, HIDDEN_STEMS[b][0])} for k, s, b in tmm]}
    F: dict = {"chart.system": "bat_tu", "bazi.k.gender": gender or "", "bazi.k.dm_strong": strong, "bazi.k.vuong": vuong, "bazi.k.nhuoc": nhuoc,
               "bazi.k.absent": absent}
    # ---- 流入日主 (p.50 condition 1, p.51 #3-5)
    tf, qf = c.flows("Tai"), c.flows("QuanSat")
    F["bazi.k.tai_flow"], F["bazi.k.quan_flow"] = bool(tf), bool(qf)
    D["tai_flow"], D["quan_flow"] = [_label(c, n) for n in tf], [_label(c, n) for n in qf]
    D["near_dm"] = [{"at": _label(c, n), "god": c.god(n)} for n in sorted(NEAR_DM, key=lambda x: (PILLARS.index(x[0]), x[1]))]
    qt = trans("Chính Quan", "Thất Sát")
    F["bazi.k.quan_trans"] = bool(qt)
    F["bazi.k.quan_trans_rooted"] = any(c.rooted((p, "stem")) for p in qt)
    D["quan_trans"] = [_label(c, (p, "stem")) for p in qt]
    # ---- 左柱 (p.52 #6-8, p.53 examples 1-2)
    q_pil = sorted({n[0] for n in c.of("QuanSat")}, key=PILLARS.index)
    basis = "quan"
    if not q_pil:
        q_pil, basis = sorted({n[0] for n in c.of("Tai")}, key=PILLARS.index), "tai"
    pick = q_pil[0] if len(q_pil) == 1 else (qt[0] if basis == "quan" and len(qt) == 1 else (trans("Chính Tài", "Thiên Tài")[0] if basis == "tai" and len(trans("Chính Tài", "Thiên Tài")) == 1 else None))
    left = PILLARS[(PILLARS.index(pick) - 1) % 4] if pick else None
    F["bazi.k.work_basis"] = basis if pick else ""
    F["bazi.k.work_pillar"] = left or ""
    F["bazi.k.work_group"] = GROUP[ten_god(dm, v.stem(left))] if left and left != "day" else ""
    F["bazi.k.work_stem"] = STEMS_VI[v.stem(left)] if left else ""
    F["bazi.k.work_strong"] = c.sits_on_root(left) if left else None
    D["work"] = {"from": pick, "from_name": f"{STEMS_VI[v.stem(pick)]} {BRANCHES_VI[v.branch(pick)]}" if pick else "", "basis": basis if pick else "",
                 "left": left, "left_name": f"{STEMS_VI[v.stem(left)]} {BRANCHES_VI[v.branch(left)]}" if left else "",
                 "stem_god": (ten_god(dm, v.stem(left)) if left and left != "day" else None), "candidates": q_pil}
    # ---- Tài (p.50)
    ct, tt = trans("Chính Tài"), trans("Thiên Tài")
    ct_nodes = [n for n in c.nodes if c.god(n) == "Chính Tài"]
    tt_nodes = [n for n in c.nodes if c.god(n) == "Thiên Tài"]
    F["bazi.k.ct_trans"], F["bazi.k.tt_trans"] = bool(ct), bool(tt)
    F["bazi.k.ct_rooted"] = any(c.rooted((p, "stem")) for p in ct)
    F["bazi.k.tt_rooted"] = any(c.rooted((p, "stem")) for p in tt)
    F["bazi.k.ct_gen_unrooted"] = any(c.generated((p, "stem")) and not c.rooted((p, "stem")) for p in ct)
    F["bazi.k.tt_gen_unrooted"] = any(c.generated((p, "stem")) and not c.rooted((p, "stem")) for p in tt)
    F["bazi.k.ct_tomb"] = any(p in ("month",) and c.tomb(p) for p in ct)            # 墓: month / day (the day stem is the day master)
    F["bazi.k.tt_kho"] = any(p in ("year", "hour") and c.tomb(p) for p in tt)       # 库: year / hour
    lone = [p for p in ct if not c.rooted((p, "stem")) and not c.generated((p, "stem"))]
    F["bazi.k.ct_lone"] = bool(lone)
    F["bazi.k.ct_lone_hurt"] = any(any(_hurt(v.branch(p), v.branch(q)) for q in PILLARS if q != p) for p in lone)
    F["bazi.k.ct_hidden_gen"] = not ct and any(c.generated(n) for n in ct_nodes if n[1] == "branch")
    F["bazi.k.tt_hidden_gen"] = not tt and any(c.generated(n) for n in tt_nodes if n[1] == "branch")
    F["bazi.k.tt_hidden_covered"] = not tt and any(c.covered(n[0]) for n in tt_nodes if n[1] == "branch")
    F["bazi.k.ct_cut"] = any(c.cut(p) for p in ct)
    F["bazi.k.tt_cut"] = any(c.cut(p) for p in tt)
    F["bazi.k.both_tai_rooted"] = any(c.rooted((p, "stem")) for p in ct) and any(c.rooted((p, "stem")) for p in tt)
    ti_n = len(c.of("Ti"))
    F["bazi.k.ti_count"] = ti_n
    F["bazi.k.tai_count"] = len(c.of("Tai"))
    # 争合: one Tài stem with two partners, or two Tài stems on one partner (the day master included)
    all_stems = [(p, v.stem(p)) for p in PILLARS]
    contested = False
    for p, s in all_stems:
        if p == "day" or GROUP[ten_god(dm, s)] != "Tai":
            continue
        partners = [q for q, t in all_stems if q != p and frozenset((s, t)) in STEM_COMBINE]
        twins = [q for q, t in all_stems if q != p and t == s]
        contested |= len(partners) >= 2 or (len(partners) >= 1 and len(twins) >= 1)
    F["bazi.k.tai_contested"] = contested
    F["bazi.k.tmm_hurt"] = any(_hurt(b, v.branch(p)) for _, _, b in tmm for p in PILLARS)
    F["bazi.k.tai_tmm"] = any("Tai" in (GROUP[x["god_stem"]], GROUP[x["god_branch"]]) for x in D["tmm"])
    F["bazi.k.tai_void"] = any(c.group(n) == "Tai" for n in void_nodes)
    comb_s = [p for p in PILLARS for q in PILLARS if p != q and frozenset((v.stem(p), v.stem(q))) in STEM_COMBINE]
    comb_b = [p for p in PILLARS for q in PILLARS if p != q and frozenset((v.branch(p), v.branch(q))) in SIX_COMBINE]
    F["bazi.k.tai_combined"] = any(p != "day" and GROUP[ten_god(dm, v.stem(p))] == "Tai" for p in comb_s) or any(c.group((p, "branch")) == "Tai" for p in comb_b)
    D["tai"] = {"trans": [_label(c, (p, "stem")) for p in ct + tt], "hidden": [_label(c, n) for n in ct_nodes + tt_nodes if n[1] == "branch"],
                "share": share.get("Tai")}
    # ---- quan chức (pp.52-53)
    qs_nodes = c.of("QuanSat")
    hs = v.stem("hour")
    hour_q = ten_god(dm, hs) == "Chính Quan"
    from ..bazi import STEM_CLASH_KIND
    hour_free = not any(frozenset((hs, v.stem(p))) in STEM_COMBINE or frozenset((hs, v.stem(p))) in STEM_CLASH_KIND for p in ("year", "month", "day"))
    F["bazi.k.quan_sat_both"] = all(any(c.rooted((p, "stem")) for p in trans(g)) for g in ("Chính Quan", "Thất Sát"))
    F["bazi.k.hour_lone_quan"] = hour_q and len(qs_nodes) == 1 and hour_free
    F["bazi.k.quan_an_adj"] = any(c.adj(q, a) for q in qs_nodes for a in c.of("An"))
    F["bazi.k.quan_near_dm"] = any(n in NEAR_DM for n in qs_nodes)
    F["bazi.k.quan_kho_clash"] = any(v.branch(p) in TOMBS and any(GROUP[ten_god(dm, h)] == "QuanSat" for h in HIDDEN_STEMS[v.branch(p)])
                                     and any(frozenset((v.branch(p), v.branch(q))) in SIX_CLASH for q in PILLARS if q != p) for p in ("year", "hour"))
    F["bazi.k.thuong_present"] = any(c.god(n) == "Thương Quan" for n in c.nodes)
    # ---- cha mẹ (p.55 #1-5, non-lifespan)
    father = "Thiên Tài" if tt_nodes else ("Thực Thần" if any(c.god(n) == "Thực Thần" for n in c.nodes) else None)
    an_nodes = c.of("An")
    mother = "Ấn" if an_nodes else ("Quan" if qs_nodes else None)
    D["parents"] = {"father": father, "father_at": [_label(c, n) for n in c.nodes if c.god(n) == father] if father else [],
                    "mother": mother, "mother_at": [_label(c, n) for n in (an_nodes if mother == "Ấn" else qs_nodes if mother else [])]}
    war = [(t, a) for t in c.of("Tai") for a in an_nodes if c.adj(t, a)]
    F["bazi.k.tai_an_war"] = bool(war)
    F["bazi.k.quan_present"] = bool(qs_nodes)
    D["tai_an_war"] = [f"{_label(c, t)} khắc {_label(c, a)}" for t, a in war]
    # ---- hôn nhân (pp.57-58, p.73)
    F["bazi.k.md_hurt"] = _hurt(v.branch("month"), v.branch("day"))
    F["bazi.k.day_god"] = branch_main["day"]
    all7 = [v.branch(p) for p in PILLARS] + [b for _, _, b in tmm]
    F["bazi.k.triple_branch"] = any(all7.count(b) >= 3 for b in set(all7))
    D["triple"] = [BRANCHES_VI[b] for b in sorted(set(all7)) if all7.count(b) >= 3]
    F["bazi.k.spouse_fuyin"] = v.branch("day") in (v.branch("month"), v.branch("hour"))
    F["bazi.k.tmm_combine_day"] = any(frozenset((b, v.branch("day"))) in SIX_COMBINE for _, _, b in tmm)
    F["bazi.k.dm_tomb_day"] = growth_stage(dm, v.branch("day")) == "Mộ"
    spouse = "Tai" if gender == "nam" else "QuanSat" if gender == "nữ" else None
    F["bazi.k.spouse_flow"] = bool(spouse) and spouse in vuong and bool(tf if spouse == "Tai" else qf)
    F["bazi.k.spouse_void"] = bool(spouse) and any(c.group(n) == spouse for n in void_nodes)
    D["spouse"] = {"group": spouse and GROUP_VI[spouse], "at": [_label(c, n) for n in c.of(spouse)] if spouse else [],
                   "hidden_only": bool(spouse) and not any(n[1] == "stem" for n in c.of(spouse))}
    # ---- anh em (pp.63-64, non-lifespan)
    ti_stems = [p for p in ("year", "month", "hour") if GROUP[stems[p]] == "Ti"]
    F["bazi.k.ti_weak_near"] = bool(strong) and any(p in ("month", "hour") and not c.sits_on_root(p) for p in ti_stems)
    F["bazi.k.ti_an_dm"] = GROUP[stems["year"]] == "Ti" and GROUP[stems["month"]] == "An"
    F["bazi.k.ti_tai_dm"] = GROUP[stems["year"]] == "Ti" and GROUP[stems["month"]] == "Tai"
    F["bazi.k.ti_sat_dm"] = GROUP[stems["year"]] == "Ti" and stems["month"] == "Thất Sát"
    F["bazi.k.ti_over_dm"] = strong is False and any(branch_main[p] in ("Chính Ấn", "Thiên Ấn") or c.rooted((p, "stem")) for p in ti_stems)
    F["bazi.k.dm_over_ti"] = any(GROUP[branch_main[p]] in ("QuanSat", "ThucThuong") for p in ti_stems) and (
        GROUP[branch_main["day"]] == "An" or c.sits_on_root("day"))
    D["siblings"] = {"star": "Tỉ Kiếp" if ti_n else ("Ấn" if an_nodes else None),
                     "at": [_label(c, n) for n in (c.of("Ti") if ti_n else an_nodes)]}
    # ---- con cái (p.60: the child stars; no sex of a child is told)
    tai_any, qs_any, tt_any = bool(c.of("Tai")), bool(c.of("QuanSat")), bool(c.of("ThucThuong"))
    if gender == "nam":
        kids = () if not (qs_any or tt_any) else ("Thất Sát", "Thương Quan") if tai_any else ("Thực Thần", "Chính Quan")
    elif gender == "nữ":
        kids = ("Thương Quan", "Thực Thần") if tt_any else ("Chính Tài", "Thiên Tài") if tai_any else ()
    else:
        kids = None
    D["children"] = {"stars": list(kids or ()), "at": [_label(c, n) for n in c.nodes if c.god(n) in (kids or ())],
                     "hour": kids == () and gender is not None}      # no child star: the hour stem and branch (p.60)
    # ---- the layout by pillar and the stems that combine with the day stem (computed facts, voiced as such)
    D["layout"] = {p: {"stem": stems.get(p), "branch": branch_main[p]} for p in PILLARS}
    D["day_combine"] = [{"pillar": p, "stem": STEMS_VI[v.stem(p)], "god": stems[p]} for p in ("year", "month", "hour")
                        if frozenset((v.stem(p), dm)) in STEM_COMBINE]
    D["share"] = {GROUP_VI[g]: (round(s, 3) if s is not None else None) for g, s in share.items()}
    D["vuong"], D["nhuoc"], D["absent"] = [GROUP_VI[g] for g in vuong], [GROUP_VI[g] for g in nhuoc], [GROUP_VI[g] for g in absent]
    # the characters each judgement names, for its condition in the text ("Thiên Tài ở can năm Tân bị chi Tỵ ngay dưới khắc")
    lab = lambda ns: _join([_label(c, n) for n in ns])
    tmm_vi = {"thai": "thai nguyên", "menh": "mệnh cung", "than": "thân cung"}
    near_q = [n for n in qs_nodes if n in NEAR_DM]
    D["vars"] = {
        "ct": lab([(p, "stem") for p in ct]), "tt": lab([(p, "stem") for p in tt]),
        "ct_cut": _join([f"{_label(c, (p, 'stem'))} bị chi {BRANCHES_VI[v.branch(p)]} ngay dưới khắc" for p in ct if c.cut(p)]),
        "tt_cut": _join([f"{_label(c, (p, 'stem'))} bị chi {BRANCHES_VI[v.branch(p)]} ngay dưới khắc" for p in tt if c.cut(p)]),
        "ct_hidden": lab([n for n in ct_nodes if n[1] == "branch"]), "tt_hidden": lab([n for n in tt_nodes if n[1] == "branch"]),
        "tt_cover": _join([f"chi {PIL_VI[n[0]]} {BRANCHES_VI[v.branch(n[0])]} bị can {STEMS_VI[v.stem(n[0])]} trên nó khắc" for n in tt_nodes if n[1] == "branch" and c.covered(n[0])]),
        "tai_void": lab([n for n in void_nodes if c.group(n) == "Tai"]), "spouse_void": lab([n for n in void_nodes if spouse and c.group(n) == spouse]),
        "tmm_tai": _join([f"{tmm_vi[k]} {STEMS_VI[s_]} {BRANCHES_VI[b_]}" for k, s_, b_ in tmm if "Tai" in (GROUP[ten_god(dm, s_)], GROUP[ten_god(dm, HIDDEN_STEMS[b_][0])])]),
        "tmm_day": _join([f"{tmm_vi[k]} {STEMS_VI[s_]} {BRANCHES_VI[b_]}" for k, s_, b_ in tmm if frozenset((b_, v.branch("day"))) in SIX_COMBINE]),
        "tmm_hurt": _join([f"{tmm_vi[k]} {STEMS_VI[s_]} {BRANCHES_VI[b_]}" for k, s_, b_ in tmm if any(_hurt(b_, v.branch(p)) for p in PILLARS)]),
        "qtrans": lab([(p, "stem") for p in qt]), "qnear": lab(near_q), "dm": STEMS_VI[dm], "db": BRANCHES_VI[v.branch("day")],
        "mb": BRANCHES_VI[v.branch("month")],
        "fuyin": _join([f"chi {PIL_VI[p]}" for p in ("month", "hour") if v.branch(p) == v.branch("day")]),
        "day_god": branch_main["day"], "triple": _join(D["triple"]), "tai_pct": _pct(share.get("Tai")), "qs_pct": _pct(share.get("QuanSat")),
        "ti": lab(c.of("Ti")), "ti_n": str(ti_n), "tai_n": str(len(c.of("Tai"))),
        "war": _join(D["tai_an_war"]), "md": f"chi tháng {BRANCHES_VI[v.branch('month')]} {_hurt_vi(v.branch('month'), v.branch('day'))} chi ngày {BRANCHES_VI[v.branch('day')]}",
    }
    return F, D


def _join(xs: list[str]) -> str:
    xs = [x for x in xs if x]
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " và " + xs[-1] if xs else ""


def _pct(x: float | None) -> str:
    return "" if x is None else str(round(x * 100))


def year_facts(view: ChartView, tvh: dict | None, nat: dict, stem: int, branch: int, luck: tuple[int, int] | None) -> dict:
    """the facts of one lưu niên for the pp.64-65 judgements (流年 = the year pillar; 行X乡/运/地 read as the year's stem or branch bringing X)"""
    c = Chart(view, tvh)
    v, dm = view, view.dm
    sg, bg = ten_god(dm, stem), ten_god(dm, HIDDEN_STEMS[branch][0])
    kw = _void_of(v.stem("day"), v.branch("day"))
    yv = _void_of(stem, branch)
    tmm = c.tmm()
    natal_void = sorted({c.god((p, "branch")) for p in PILLARS if v.branch(p) in yv})
    F = {"chart.system": "bat_tu", **{k: nat[k] for k in ("bazi.k.dm_strong", "bazi.k.vuong", "bazi.k.nhuoc", "bazi.k.absent", "bazi.k.gender")},
         "bazi.ky.stem_god": sg, "bazi.ky.branch_god": bg, "bazi.ky.groups": sorted({GROUP[sg], GROUP[bg]}), "bazi.ky.gods": sorted({sg, bg}),
         "bazi.ky.blade": branch == ZZ_REN[dm], "bazi.ky.tai_on_blade": GROUP[sg] == "Tai" and branch == ZZ_REN[dm],
         "bazi.ky.fill_void": branch in kw, "bazi.ky.natal_void_gods": natal_void,
         "bazi.ky.tomb_clash": branch in TOMBS and any(frozenset((branch, v.branch(p))) in SIX_CLASH for p in PILLARS),
         "bazi.ky.same_as_luck": luck is not None and (stem, branch) == tuple(luck),
         "bazi.ky.tmm_hurt": any(_hurt(branch, b) for _, _, b in tmm),
         "bazi.ky.guan_mixed": any(c.god(n) == "Chính Quan" for n in c.nodes) and any(c.god(n) == "Thất Sát" for n in c.nodes)}
    tmm_vi = {"thai": "thai nguyên", "menh": "mệnh cung", "than": "thân cung"}
    V = {"ys": STEMS_VI[stem], "yb": BRANCHES_VI[branch], "sg": sg, "bg": bg, "dm": STEMS_VI[dm],
         "vat": _join([f"{_label(c, (p, 'branch'))} ({c.god((p, 'branch'))})" for p in PILLARS if v.branch(p) in yv]),
         "tmm": _join([f"{_hurt_vi(branch, b_)} {tmm_vi[k]} {STEMS_VI[s_]} {BRANCHES_VI[b_]}" for k, s_, b_ in tmm if _hurt(branch, b_)]),
         "tomb": _join([f"chi {PIL_VI[p]} {BRANCHES_VI[v.branch(p)]}" for p in PILLARS if frozenset((branch, v.branch(p))) in SIX_CLASH and v.branch(p) in TOMBS]),
         "luck": f"{STEMS_VI[luck[0]]} {BRANCHES_VI[luck[1]]}" if luck else "",
         "tai_y": _join([f"{x}" for x in (sg, bg) if GROUP[x] == "Tai"]), "qs_y": _join([x for x in dict.fromkeys((sg, bg)) if GROUP[x] == "QuanSat"]),
         "tt_y": _join([x for x in dict.fromkeys((sg, bg)) if GROUP[x] == "ThucThuong"]), "an_y": _join([x for x in dict.fromkeys((sg, bg)) if GROUP[x] == "An"])}
    return F, V


# ---------------------------------------------------------------- rules

@lru_cache(maxsize=1)
def pack() -> tuple[list[KnowledgeRule], list[Source], dict]:
    d = json.loads((DATA / "pack_zz_kin.json").read_text("utf-8"))
    meta = json.loads((DATA / "quotes_zz_kin.json").read_text("utf-8"))
    return [KnowledgeRule(**r) for r in d["rules"]], [Source(**s) for s in d["sources"]], meta


def _fill(t: str, V: dict) -> str | None:
    """the condition with this chart's characters, or None when a slot has nothing to name"""
    import re
    keys = re.findall(r"\{(\w+)\}", t)
    if any(not V.get(k) for k in keys):
        return None
    return re.sub(r"\{(\w+)\}", lambda m: str(V[m.group(1)]), t)


def fire(facts: dict, V: dict | None = None) -> list[dict]:
    rules, sources, meta = pack()
    res = engine.run(rules, sources, {"chart": facts}, system="bat_tu")
    out = []
    for f in sorted(res.findings, key=lambda x: x.rule_id):
        if f.basis != "verified":
            continue
        m = meta[f.rule_id]
        said = _fill(m["say"], V or {}) if m.get("say") else None
        out.append({"rule_id": f.rule_id, "topic": m["topic"], "tone": m["tone"], "effect": m["effect"], "cause": said or m["cause"], "page": m["page"],
                    **({"note": m["note"]} if m.get("note") else {})})
    return out


def natal(view: ChartView, tvh: dict | None) -> dict:
    F, D = natal_facts(view, tvh)
    return {"facts": {k: v for k, v in F.items() if k != "chart.system"}, "detail": D, "findings": fire(F, D["vars"])}


def year(view: ChartView, tvh: dict | None, nat_facts: dict, stem: int, branch: int, luck: tuple[int, int] | None) -> dict:
    F, V = year_facts(view, tvh, nat_facts, stem, branch, luck)
    return {"gods": [F["bazi.ky.stem_god"], F["bazi.ky.branch_god"]], "fill_void": F["bazi.ky.fill_void"], "natal_void_gods": F["bazi.ky.natal_void_gods"],
            "findings": fire(F, V)}
