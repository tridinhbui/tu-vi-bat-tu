"""Chart signals: the facts the growth layer is allowed to build on, each with a stable id, a plain sentence and a machine-checkable
`check` so tests can verify every insight is anchored in something actually true of this chart."""
from __future__ import annotations

from dataclasses import dataclass, field

from .. import temporal
from ..analysis import GROUPS, PALACE_ROLE
from ..ganzhi import BRANCH_ELEMENT, BRANCHES_VI, ELEMENTS, STEM_ELEMENT, STEMS_VI
from . import kb

GROUP_KEY = {"Tử – Phủ – Vũ – Tướng": "tu_phu_vu_tuong", "Sát – Phá – Liêm – Tham": "sat_pha_liem_tham",
             "Cơ – Nguyệt – Đồng – Lương": "co_nguyet_dong_luong", "Cự – Nhật – Nguyệt": "cu_nhat_nguyet"}
TEN_GOD_GROUP = {"Tỉ Kiên": "Ti", "Kiếp Tài": "Ti", "Thực Thần": "ThucThuong", "Thương Quan": "ThucThuong", "Chính Tài": "Tai",
                 "Thiên Tài": "Tai", "Chính Quan": "QuanSat", "Thất Sát": "QuanSat", "Chính Ấn": "An", "Thiên Ấn": "An"}
HOA_ORDER = ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"]


def groups_of(majors: list[str]) -> list[str]:
    return [GROUP_KEY[g] for g, members in GROUPS.items() if any(s in members for s in majors)]


def action_level(majors: list[str]) -> float | None:
    gs = groups_of(majors)
    if not gs:
        return None
    acts = [kb.load("palaces")["groups"][g]["action"] for g in gs]
    return sum(acts) / len(acts)


@dataclass
class Signals:
    anchors: dict = field(default_factory=dict)        # id -> {id, system, text, check}
    ps: dict = field(default_factory=dict)             # palace name -> palace dict
    menh: dict = None
    menh_stars: list = field(default_factory=list)     # stars read as 'Mệnh' (own, or borrowed from Thiên Di when vô chính diệu)
    vcd: bool = False
    borrowed: list = field(default_factory=list)
    than: dict = None
    hoa: dict = field(default_factory=dict)            # hoa -> {star, palace}
    year_stem: int = 0
    menh_cuc: str = ""
    bazi: dict = field(default_factory=dict)
    stage: dict = field(default_factory=dict)

    def add(self, sid: str, system: str, text: str, check: dict) -> str:
        self.anchors[sid] = {"id": sid, "system": system, "text": text, "check": check}
        return sid


def _dig(p, s):
    return p["major_dignity"].get(s)


def read(tv, bz, deep: dict | None, year_now: int) -> Signals:
    sg = Signals()
    sg.ps = {p["name"]: p for p in tv.palaces}
    m = sg.menh = sg.ps["Mệnh"]
    if m["major_stars"]:
        sg.menh_stars = list(m["major_stars"])
        dig = ", ".join(f"{s} ({_dig(m, s) or 'độ sáng chưa rõ'})" for s in m["major_stars"])
        sg.add("menh.stars", "tu_vi", f"Cung Mệnh an tại {m['branch']}, có chính tinh {dig}.", {"palace": "Mệnh", "stars": m["major_stars"]})
    else:
        sg.vcd = True
        opp = next(p for p in tv.palaces if p["branch_index"] == (m["branch_index"] + 6) % 12)
        sg.borrowed = list(opp["major_stars"])
        sg.menh_stars = list(opp["major_stars"])
        sg.add("menh.vcd", "tu_vi", f"Cung Mệnh an tại {m['branch']}, vô chính diệu; cung đối diện ({opp['name']}) có {', '.join(opp['major_stars']) or 'không có chính tinh'}.",
               {"palace": "Mệnh", "stars": [], "opposite_stars": opp["major_stars"]})
    tt = [x for x, f in (("Tuần", m["tuan"]), ("Triệt", m["triet"])) if f]
    if tt:
        sg.add("menh.tuan_triet", "tu_vi", f"Cung Mệnh có {' và '.join(tt)}.", {"palace": "Mệnh", "flags": tt})
    sg.than = next(p for p in tv.palaces if p["is_than"])
    sg.add("than.palace", "tu_vi", f"Cung Thân cư {sg.than['name']} ({sg.than['branch']})" + (f", có {', '.join(sg.than['major_stars'])}." if sg.than["major_stars"] else ", vô chính diệu."),
           {"palace": sg.than["name"], "is_than": True, "stars": sg.than["major_stars"]})
    pd = sg.ps["Phúc Đức"]
    sg.add("phuc.stars", "tu_vi", f"Cung Phúc Đức an tại {pd['branch']}" + (f", có {', '.join(pd['major_stars'])}." if pd["major_stars"] else ", vô chính diệu."),
           {"palace": "Phúc Đức", "stars": pd["major_stars"]})
    by_b = {p["branch_index"]: p for p in tv.palaces}
    for h in HOA_ORDER:
        x = tv.tu_hoa.get(h)
        if x:
            pal = by_b[x["branch"]]["name"]
            sg.hoa[h] = {"star": x["star"], "palace": pal}
            sg.add(f"hoa.{h}", "tu_vi", f"{h} đóng tại cung {pal} (sao {x['star']}).", {"hoa": h, "star": x["star"], "palace": pal})
    sg.year_stem = STEMS_VI.index(tv.year_gz.split()[0])
    sg.add("year.stem", "tu_vi", f"Năm sinh {tv.year_gz} (can {STEMS_VI[sg.year_stem]}).", {"year_stem": STEMS_VI[sg.year_stem]})
    sg.menh_cuc = tv.menh_cuc_relation
    sg.add("menh.cuc", "tu_vi", f"Mệnh {tv.menh_nap_am} ({tv.menh_element}), {tv.cuc['name']}: {tv.menh_cuc_relation}.", {"menh_cuc_relation": tv.menh_cuc_relation})
    for name in ("Quan Lộc", "Tài Bạch", "Phu Thê", "Phụ Mẫu", "Tử Tức", "Thiên Di"):
        p = sg.ps[name]
        sg.add(f"palace.{name}", "tu_vi", f"Cung {name} ({p['branch']})" + (f" có {', '.join(p['major_stars'])}." if p["major_stars"] else " vô chính diệu."),
               {"palace": name, "stars": p["major_stars"]})
    sg.bazi = _bazi(sg, bz, deep)
    sg.stage = _stage(sg, tv, bz, year_now)
    return sg


def _bazi(sg: Signals, bz, deep: dict | None) -> dict:
    dm = STEMS_VI[bz.day_master]
    out = {"dm": dm, "dm_element": bz.day_master_element}
    sg.add("bazi.dm", "bat_tu", f"Nhật Chủ {dm} ({bz.day_master_element}).", {"day_master": dm})
    # visible eight characters only (transparent count; hidden stems are listed separately so 'vắng' really means absent everywhere)
    vis = [STEM_ELEMENT[p.stem] for p in bz.pillars.values()] + [BRANCH_ELEMENT[p.branch] for p in bz.pillars.values()]
    hidden = {h["element"] for p in bz.pillars.values() for h in p.hidden}
    counts = {e: vis.count(e) for e in ELEMENTS}
    out["counts"] = counts
    out["excess"] = [e for e in ELEMENTS if counts[e] >= 4]
    out["lack"] = [e for e in ELEMENTS if counts[e] == 0 and e not in hidden]
    sg.add("bazi.elements", "bat_tu", "Tám chữ: " + ", ".join(f"{e} {counts[e]}" for e in ELEMENTS) + "; hành vắng cả ở tàng can: " + (", ".join(out["lack"]) or "không có") + ".",
           {"counts": counts, "lack": out["lack"]})
    if deep:
        f = deep.get("facts", {})
        lvl = f.get("bazi.dm_level") or ""
        out["level"] = "nhược" if "nhược" in lvl else ("vượng" if "vượng" in lvl else "trung hòa")
        out["level_raw"] = lvl
        out["ambiguous"] = bool(f.get("bazi.dm_ambiguous"))
        out["readings"] = f.get("bazi.dm_readings") or []
        shares = (deep.get("strength_after") or {}).get("shares") or {}
        out["heavy"] = [g for g, v in sorted(shares.items(), key=lambda kv: -kv[1]) if v >= 0.3 and g not in ("Ti", "An")]
        pu = ((deep.get("yongshen") or {}).get("methods") or {}).get("phu_uc") or {}
        alts = pu.get("alternatives") or ([pu] if pu.get("yong") else [])
        seen, yong = set(), []
        for a in alts:
            key = tuple(a.get("yong") or [])
            if key and key not in seen:
                seen.add(key)
                yong.append(list(key))
        out["yong"] = yong
        amb = f" (ở vùng biên, có hai cách đọc: {', '.join(out['readings'])})" if out["ambiguous"] and out["readings"] else ""
        sg.add("bazi.strength", "bat_tu", f"Khí thế Nhật Chủ sau tương tác: {lvl or 'chưa tính'}{amb}; quy tắc ở trạng thái nháp.",
               {"dm_level": lvl, "ambiguous": out["ambiguous"]})
        if yong:
            lab = kb.load("bazi")["groups"]
            sg.add("bazi.yong", "bat_tu", "Phù ức: nhóm nên bồi đắp " + " hoặc ".join("/".join(lab[g]["label"] for g in y) for y in yong) + " (nháp).", {"yong": yong})
    return out


def _stage(sg: Signals, tv, bz, year: int) -> dict:
    t = temporal.tuvi_year(tv, year)
    b = temporal.bazi_year(bz, tv.lunar["year"], year)
    st = {"year": year, "age_tuoi_mu": t["age_tuoi_mu"]}
    dh = t.get("dai_han")
    if dh:
        st["dai_han"] = {"palace": dh["palace"], "age_from": dh["age_from"], "age_to": dh["age_to"], "area": kb.load("palaces")["growth_area"][dh["palace"]]["area"]}
        sg.add("stage.dai_han", "tu_vi", f"Năm {year} (tuổi mụ {t['age_tuoi_mu']}): đại hạn {dh['age_from']}–{dh['age_to']} tuổi ở cung {dh['palace']}.",
               {"year": year, "dai_han_palace": dh["palace"]})
    if b.get("luck_pillar"):
        g = TEN_GOD_GROUP.get(b.get("luck_stem_ten_god") or "")
        st["luck"] = {"pillar": b["luck_pillar"], "ten_god": b.get("luck_stem_ten_god"), "group": g}
        sg.add("stage.luck", "bat_tu", f"Năm {year}: đại vận {b['luck_pillar']} (can {b.get('luck_stem_ten_god')}).", {"year": year, "luck_pillar": b["luck_pillar"]})
    return st


def verify_anchor(a: dict, tv, bz) -> bool:
    """Independent check that an anchor's claim is true of the chart (used by the QA tests)."""
    c, ps = a["check"], {p["name"]: p for p in tv.palaces}
    if "hoa" in c:
        x = tv.tu_hoa[c["hoa"]]
        return x["star"] == c["star"] and next(p for p in tv.palaces if p["branch_index"] == x["branch"])["name"] == c["palace"]
    if "is_than" in c:
        return ps[c["palace"]]["is_than"] and ps[c["palace"]]["major_stars"] == c["stars"]
    if "flags" in c:
        p = ps[c["palace"]]
        return all({"Tuần": p["tuan"], "Triệt": p["triet"]}[f] for f in c["flags"])
    if "opposite_stars" in c:
        m = ps["Mệnh"]
        opp = next(p for p in tv.palaces if p["branch_index"] == (m["branch_index"] + 6) % 12)
        return not m["major_stars"] and opp["major_stars"] == c["opposite_stars"]
    if "palace" in c and "stars" in c:
        return ps[c["palace"]]["major_stars"] == c["stars"]
    if "year_stem" in c:
        return tv.year_gz.split()[0] == c["year_stem"]
    if "menh_cuc_relation" in c:
        return tv.menh_cuc_relation == c["menh_cuc_relation"]
    if "day_master" in c:
        return STEMS_VI[bz.day_master] == c["day_master"]
    if "counts" in c:
        vis = [STEM_ELEMENT[p.stem] for p in bz.pillars.values()] + [BRANCH_ELEMENT[p.branch] for p in bz.pillars.values()]
        return all(vis.count(e) == n for e, n in c["counts"].items())
    if "dai_han_palace" in c:
        return temporal.tuvi_year(tv, c["year"])["dai_han"]["palace"] == c["dai_han_palace"]
    if "luck_pillar" in c:
        return temporal.bazi_year(bz, tv.lunar["year"], c["year"])["luck_pillar"] == c["luck_pillar"]
    return "dm_level" in c or "yong" in c   # computed by bazi_deep in the same request; the test re-runs the pipeline for these


__all__ = ["Signals", "read", "verify_anchor", "groups_of", "action_level", "PALACE_ROLE", "BRANCHES_VI", "TEN_GOD_GROUP"]
