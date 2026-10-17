"""Phương pháp tính điểm (độ) vượng suy của nhật chủ, theo Thiệu Vĩ Hoa, "Dự Đoán Theo Tứ Trụ" (bản dịch Việt), trang 331–355.
Đây là cài đặt các bước THỂ HIỆN TRONG VĂN BẢN; chỗ nào sách chỉ nêu qua ví dụ hoặc mơ hồ thì ghi vào `unsupported`/`assumptions`:
  - Thiên can: 36 độ nếu có chỗ dựa, 9 độ nếu hư phù; ngũ hợp (hóa: 60 độ/cặp; không hóa: bên bị khắc còn 24; tranh hợp: ba can còn 24);
    khắc gần −12, cách ngôi −6, xa 0, kẹp −24; chi cùng trụ: can sinh chi −6, can khắc chi −12, chi khắc can −18.
  - Địa chi: 30 độ chia bản khí/tạp khí theo bảng; tam hội 72, tam hợp 60, bán tam hợp 40, lục hợp 36 khi hóa; không hóa thì khử bì (chỉ bản khí);
    lục xung kề nhau: khử bì rồi hao 1/3 hoặc 1/2 (bảng chi tháng), kẹp xung 1/3 và 2/3; bản khí +6 / −8 theo can trực đỉnh.
  - Chi tháng nắm lệnh: hành nắm lệnh +1/5, hành bị nó khắc −1/5. Nhật chủ vượng khi 'phe mình' (cùng hành + sinh) lớn hơn 40% tổng (đúng 40%: sách không nói, hệ thống tính là vượng).
Chưa hỗ trợ: phu tòng thê hóa / thê tòng phu hóa / uyên ương hợp hóa (mục 5, 6, 8 trang 337–338): coi là hợp mà không hóa và ghi `unsupported`.
Các ví dụ của sách có vài chỗ số học không khớp (ví dụ trang 347–348); test chỉ so các thành phần nhất quán với phần văn xuôi."""
from __future__ import annotations

from ..bazi import MEETING, SIX_CLASH, SIX_COMBINE, STEM_COMBINE, TRIAD
from ..ganzhi import BRANCH_ELEMENT, ELEMENTS, STEM_ELEMENT, STEMS_VI, controls, generates
from .model import PILLARS, ChartView

# trang 342, bảng độ vượng các địa chi tàng nhân nguyên: (can, độ) từ bản khí đến tạp khí
HID_DEG = {
    0: [(9, 30)], 1: [(5, 18), (9, 9), (7, 3)], 2: [(0, 18), (2, 9), (4, 3)], 3: [(1, 30)], 4: [(4, 18), (1, 9), (9, 3)], 5: [(2, 18), (6, 9), (4, 3)],
    6: [(3, 21), (5, 9)], 7: [(5, 18), (3, 9), (1, 3)], 8: [(6, 18), (4, 9), (8, 3)], 9: [(7, 30)], 10: [(4, 18), (7, 9), (3, 3)], 11: [(8, 21), (0, 9)],
}
SEASON_EL = {2: "Mộc", 3: "Mộc", 4: "Mộc", 5: "Hỏa", 6: "Hỏa", 7: "Hỏa", 8: "Kim", 9: "Kim", 10: "Kim", 11: "Thủy", 0: "Thủy", 1: "Thủy"}
KHO = {1, 4, 7, 10}
UNIT_DEG = {"hoi": 72, "hop": 60, "ban": 40, "luc": 36}
GROUP = {2: (2, 3), 3: (2, 3), 5: (5, 6), 6: (5, 6), 8: (8, 9), 9: (8, 9), 11: (11, 0), 0: (11, 0)}   # month -> its season group (Dần Mão, Tỵ Ngọ, Thân Dậu, Hợi Tý)
OPPOSITE = {2: 8, 3: 9, 8: 2, 9: 3, 5: 11, 6: 0, 11: 5, 0: 6}


THRESHOLD = 0.40     # SRC_TVH_DIEM tr.355: 'phe mình' lớn hơn 40% tổng độ → vượng, nhỏ hơn → nhược (ví dụ 6: 78 < 78,8 nhược; ví dụ 7: 115 > 87,2 vượng)


def decide(own: float, total: float) -> tuple[float, bool]:
    """The book's 40% rule on the scored totals. The book only says 'lớn hơn' / 'nhỏ hơn'; exactly 40% counts as vượng here by this system's choice."""
    share = own / (total or 1.0)
    return share, share >= THRESHOLD


def _el(stem: int) -> str:
    return STEM_ELEMENT[stem]


def _pillar_idx(p: str) -> int:
    return PILLARS.index(p)


def _stem_hop_el(a: int, b: int):
    return STEM_COMBINE.get(frozenset((a, b)))


def score(view: ChartView) -> dict:
    st, br = list(view.stems), list(view.branches)
    notes: dict = {"unsupported": [], "assumptions": [], "steps": []}
    dm_i = 2

    # ---------- địa chi: các tổ hợp (tam hội 72, tam hợp 60, bán tam hợp 40, lục hợp 36)
    stem_els = {_el(s) for s in st}
    potential = set()                    # potential hóa elements brought by adjacent ngũ hợp of stems ('dẫn xuất')
    for i in range(3):
        e = _stem_hop_el(st[i], st[i + 1])
        if e:
            potential.add(e)
    can_dan = stem_els | potential
    units: list[dict] = []
    present = {b: [i for i in range(4) if br[i] == b] for b in range(12)}
    for kind, table, deg in (("hoi", MEETING, 72), ("hop", {k: v for k, v in TRIAD.items()}, 60)):
        for el, tri in table.items():
            if all(present[b] for b in tri):
                members = [present[b][0] for b in tri]
                units.append({"kind": kind, "el": el, "branches": list(tri), "idx": members, "hoa": el in can_dan})
    for el, tri in TRIAD.items():
        for (x, y) in ((0, 1), (1, 2)):                    # sinh–vượng, vượng–mộ
            for i in present[tri[x]]:
                for j in present[tri[y]]:
                    if abs(i - j) == 1 and not all(present[b] for b in tri):
                        units.append({"kind": "ban", "el": el, "branches": [tri[x], tri[y]], "idx": [i, j], "hoa": el in can_dan})
    month_main_el = BRANCH_ELEMENT[br[1]]
    for pair in SIX_COMBINE:
        a, b = sorted(pair)
        for i in present[a]:
            for j in present[b]:
                if abs(i - j) == 1:
                    el = {frozenset((0, 1)): "Thổ", frozenset((2, 11)): "Mộc", frozenset((3, 10)): "Hỏa", frozenset((4, 9)): "Kim", frozenset((5, 8)): "Thủy", frozenset((6, 7)): "Hỏa"}[pair]
                    month_support = month_main_el == el or generates(month_main_el, el)
                    units.append({"kind": "luc", "el": el, "branches": [a, b], "idx": [i, j], "hoa": el in can_dan and month_support})
    prio = {"hoi": 0, "hop": 1, "ban": 2, "luc": 3}
    units.sort(key=lambda u: (prio[u["kind"]], u["idx"]))
    taken, formed, khu_bi = set(), [], set()
    for u in units:
        if any(i in taken for i in u["idx"]):
            continue
        if u["kind"] == "luc":
            # tranh hợp: a branch hợp-able with two neighbours -> hợp mà không hóa
            tranh = any(sum(1 for v in units if v["kind"] == "luc" and i in v["idx"]) > 1 for i in u["idx"])
            u["hoa"] = u["hoa"] and not tranh
        taken |= set(u["idx"])
        (formed if u["hoa"] else []).append(u)
        if not u["hoa"]:
            khu_bi |= set(u["idx"])
        u["deg"] = UNIT_DEG[u["kind"]]
    in_unit = {i: u for u in formed for i in u["idx"]}
    # tham hợp quên xung: any branch that is part of a 3-chi / bán / lục combination (formed or not) is exempt from xung
    in_combo = set(i for u in units for i in u["idx"])
    xung_hit: dict[int, float] = {}                      # branch pillar index -> list of attackers
    attackers: dict[int, list[int]] = {}
    for i in range(3):
        j = i + 1
        if frozenset((br[i], br[j])) in map(frozenset, [(k, k + 6) for k in range(6)]) and i not in in_combo and j not in in_combo:
            attackers.setdefault(i, []).append(j)
            attackers.setdefault(j, []).append(i)
    xung = set(attackers)
    khu_bi |= xung

    # ---------- thiên can
    avail: list[set] = []                                # elements available in each branch for the root test
    for i in range(4):
        if i in in_unit:
            avail.append({in_unit[i]["el"]})
        elif i in khu_bi:
            avail.append({_el(HID_DEG[br[i]][0][0])})
        else:
            avail.append({_el(s) for s, _ in HID_DEG[br[i]]})
    all_av = set().union(*avail)
    root = [any(e == _el(s) or generates(e, _el(s)) for e in all_av) for s in st]
    main_av = set(in_unit[i]["el"] if i in in_unit else _el(HID_DEG[br[i]][0][0]) for i in range(4))     # bản khí (or the hóa cục element) only: the stricter "có khí gốc" used for tòng
    root_main = [any(e == _el(s) or generates(e, _el(s)) for e in main_av) for s in st]
    deg = [36.0 if root[i] else 9.0 for i in range(4)]
    notes["steps"].append({"step": "chỗ dựa", "root": root, "deg": deg[:]})
    hop_pairs = []
    for i in range(3):
        e = _stem_hop_el(st[i], st[i + 1])
        if e:
            hop_pairs.append((i, i + 1, e))
    stem_hop = set()
    stem_el = [_el(s) for s in st]
    hua_stem = {}
    # PDF p.336 lists 'nhân nguyên tàng trong chi tháng'; the book's own example 6 (Mùi tháng, Ất 3 độ) does not let a 3-degree tạp khí qualify, so only >= 9 degrees count
    lenh_branch_el = {_el(s) for s, g in HID_DEG[br[1]] if g >= 9} | {month_main_el}
    for (i, j, e) in hop_pairs:
        stem_hop |= {i, j}
        partners = sum(1 for (a, b, _) in hop_pairs if i in (a, b)) > 1 or sum(1 for (a, b, _) in hop_pairs if j in (a, b)) > 1
        if partners:
            for k in {i, j} | {x for (a, b, _) in hop_pairs for x in (a, b) if {a, b} & {i, j}}:
                deg[k] = max(0.0, 36.0 - 12) if root[k] or True else 9
            notes["steps"].append({"step": "tranh hợp", "pairs": [i, j]})
            continue
        both_xu = not root[i] and not root[j]
        if both_xu:
            deg[i] = deg[j] = 9.0
            stem_hop -= {i, j}
            continue
        deg[i] = deg[j] = 36.0               # a hư phù stem in a hợp is not counted as hư phù
        support = any(BRANCH_ELEMENT[br[p]] == e or generates(BRANCH_ELEMENT[br[p]], e) for p in (i, j)) or any(u["el"] == e for u in formed)
        lenh_hit = e in lenh_branch_el
        season_hit = SEASON_EL[br[1]] == e
        if lenh_hit or (season_hit and support):
            deg[i] = deg[j] = 30.0
            hua_stem[i] = hua_stem[j] = e
        else:
            ctrl_i = controls(stem_el[i], stem_el[j])
            victim = j if ctrl_i else i
            deg[victim] = 24.0
    notes["steps"].append({"step": "ngũ hợp", "deg": deg[:], "hoa": dict(hua_stem)})
    # khắc between stems (stems in a hợp neither attack nor are attacked)
    base = deg[:]
    for v in range(4):
        if v in stem_hop:
            continue
        atk = [a for a in range(4) if a not in stem_hop and a != v and controls(stem_el[a], stem_el[v]) and base[a] > 18 and root[a]]
        if not atk:
            continue
        left = [a for a in atk if a < v and v - a == 1]
        right = [a for a in atk if a > v and a - v == 1]
        if left and right:
            deg[v] = max(0.0, deg[v] - 24)
            continue
        loss = 0
        for a in atk:
            d = abs(a - v)
            loss = max(loss, 12 if d == 1 else 6 if d == 2 else 0)
        deg[v] = max(0.0, deg[v] - loss)
    notes["steps"].append({"step": "khắc can", "deg": deg[:]})
    # same-pillar can–chi relation, on the effective branch element
    for i in range(4):
        be = in_unit[i]["el"] if i in in_unit else BRANCH_ELEMENT[br[i]]
        se = stem_el[i]
        if se == be or generates(be, se):
            continue
        loss = 6 if generates(se, be) else 12 if controls(se, be) else 18
        deg[i] = max(0.0, deg[i] - loss)
    notes["steps"].append({"step": "can–chi cùng trụ", "deg": deg[:]})

    # ---------- địa chi
    br_deg: list[dict[str, float]] = []
    for i in range(4):
        d: dict[str, float] = {}
        if i in in_unit:
            br_deg.append({})                     # unit degrees are added once below
            continue
        items = HID_DEG[br[i]]
        if i in khu_bi:
            items = items[:1]
        for k, (s, g) in enumerate(items):
            d[_el(s)] = d.get(_el(s), 0.0) + g
        main_el = _el(HID_DEG[br[i]][0][0])
        # +6 / -8 for the bản khí by the stem directly above (only when the branch is not in any combination or xung)
        if i not in in_combo and i not in xung:
            if (stem_el[i] == main_el or generates(stem_el[i], main_el)) and deg[i] >= 18:
                d[main_el] += 6
            elif controls(stem_el[i], main_el):
                d[main_el] = max(0.0, d[main_el] - 8)
        if i in xung and br[i] not in KHO:
            m = br[1]
            grp = GROUP.get(m)
            half = grp is not None and br[i] == OPPOSITE.get(grp[0]) or grp is not None and br[i] == OPPOSITE.get(grp[1])
            frac = 1 / 2 if half else 1 / 3
            att = len(attackers[i])
            if att >= 2:
                frac = 2 / 3
            elif any(len(attackers.get(a, [])) >= 2 for a in attackers[i]):
                frac = 1 / 3
            for e in d:
                d[e] = d[e] * (1 - frac)
        br_deg.append(d)
    totals = {e: 0.0 for e in ELEMENTS}
    for i in range(4):
        totals[hua_stem.get(i, stem_el[i])] += deg[i] if i not in hua_stem else 0
    done = set()
    for i, e in hua_stem.items():
        if i not in done:
            partner = next((j for j in hua_stem if j != i and abs(j - i) == 1 and j not in done), None)
            totals[e] += 60.0 if partner is not None else 30.0
            done |= {i, partner}
    heaven = dict(totals)
    for d in br_deg:
        for e, g in d.items():
            totals[e] += g
    for u in formed:
        totals[u["el"]] += u["deg"]
    earth = {e: round(totals[e] - heaven[e], 2) for e in ELEMENTS}
    # ---------- chi tháng nắm lệnh
    m = br[1]
    lenh = in_unit[1]["el"] if 1 in in_unit else None
    if lenh is None:
        if m in KHO:
            d = view.days_into_month
            lenh = "Thổ" if d is None or d >= 12.5 else SEASON_EL[m]
            if d is None:
                notes["assumptions"].append("tháng Thìn/Tuất/Sửu/Mùi và không biết ngày vào tiết: coi Thổ nắm lệnh (như các ví dụ của sách)")
        else:
            lenh = SEASON_EL[m]
    adj = dict(totals)
    for e in ELEMENTS:
        if e == lenh:
            adj[e] = totals[e] * 1.2
        elif controls(lenh, e):
            adj[e] = totals[e] * 0.8
    # ---------- nhật chủ
    dm_el = hua_stem.get(dm_i, stem_el[dm_i])
    mine = [e for e in ELEMENTS if e == dm_el or generates(e, dm_el)]
    total = sum(adj.values()) or 1.0
    own = sum(adj[e] for e in mine)
    notes["assumptions"].append("điều kiện hóa thần cùng loại nhân nguyên tháng: chỉ tính nhân nguyên từ 9 độ trở lên (suy từ ví dụ 6, trang 350)")
    notes["unsupported"].append("phu tòng thê hóa / thê tòng phu hóa / uyên ương hợp hóa chưa hỗ trợ (coi là hợp mà không hóa)")
    return {"stem_deg": [round(x, 2) for x in deg], "hua_stem": {PILLARS[k]: v for k, v in hua_stem.items()}, "branch_units": [{"kind": u["kind"], "el": u["el"], "branches": u["branches"], "deg": u["deg"]} for u in formed],
            "khu_bi": sorted(khu_bi), "xung": sorted(xung), "heaven": {e: round(v, 2) for e, v in heaven.items()}, "earth": earth, "lenh": lenh,
            "totals_before_lenh": {e: round(v, 2) for e, v in totals.items()}, "totals": {e: round(v, 2) for e, v in adj.items()},
            "root_main": root_main, "dm_element": dm_el, "own_share": round(own / total, 4), "dm_strong": decide(own, total)[1], "threshold": THRESHOLD, "notes": notes, "src": "SRC_TVH_DIEM"}
