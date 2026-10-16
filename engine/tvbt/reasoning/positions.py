"""Typed positional facts (Phase 1 of docs/NANG_CAP_LUAN_GIAI.md): who stands WHERE relative to a palace.

The older facts `palace.tam_phuong_*` merge own + tam hợp + xung chiếu. These new facts keep the role, so a rule can say
"X đồng cung, Y xung chiếu, Z giáp" instead of "X somewhere in the tam phương". Everything here is geometry or counting over
the calculated chart; no doctrine, no interpretation. Existing facts are untouched (additive only).
"""
from __future__ import annotations

# Roles are offsets in branch index from the palace: the 12 palaces sit on the 12 branches.
ROLES = {"self": 0, "opp": 6, "trine1": 4, "trine2": 8, "flank_prev": -1, "flank_next": 1}
NHI_HOP_ROLE = "nhi_hop"                       # lục hợp pair: branch b <-> (1 - b) mod 12 (same pairing as van_han / Khảo Luận pp.230-233)
ALL_ROLES = list(ROLES) + [NHI_HOP_ROLE]

# Brightness as an ordinal so rules can compare ("sáng = rank >= 2") instead of listing strings.
# 'unspecified' (the book gives no level) is deliberately absent: a rule reading it gets UNKNOWN, never a guess.
RANK = {"miếu": 4, "vượng": 3, "đắc": 2, "bình": 1, "hãm": 0}

CAT_STARS = ("Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt")       # same lists as analysis.py
SAT_STARS = ("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp")
HOA_NAMES = ("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ")


def branch_of(role: str, b: int) -> int:
    return (1 - b) % 12 if role == NHI_HOP_ROLE else (b + ROLES[role]) % 12


def rank_of(level: str | None) -> int | None:
    return RANK.get(level) if level else None


def typed_facts(palaces: list[dict], tu_hoa: dict) -> dict[str, dict]:
    """palaces: list of the TuViChart palace dicts (branch_index, name, stars, major_stars, major_dignity, minor_dignity, tuan, triet).
    tu_hoa: {'Hóa Lộc': {'star':..., 'branch': idx|None}, ...}. Returns {palace name: {new fact: value}}."""
    by_b = {p["branch_index"]: p for p in palaces}
    hoa_at: dict[int, list[str]] = {}
    for k, v in tu_hoa.items():
        if v.get("branch") is not None:
            hoa_at.setdefault(v["branch"], []).append(k)
    out: dict[str, dict] = {}
    for p in palaces:
        b = p["branch_index"]
        f: dict = {"palace.index": b}
        names, roles_stars, roles_major, roles_hoa = {}, {}, {}, {}
        for role in ALL_ROLES:
            q = by_b[branch_of(role, b)]
            names[role] = q["name"]
            roles_stars[role], roles_major[role] = list(q["stars"]), list(q["major_stars"])
            roles_hoa[role] = sorted(hoa_at.get(q["branch_index"], []), key=HOA_NAMES.index)
            f[f"palace.rel.{role}_stars"] = roles_stars[role]
            f[f"palace.rel.{role}_majors"] = roles_major[role]
            f[f"palace.rel.{role}_hoa"] = roles_hoa[role]
        f["palace.rel_names"] = names
        f["palace.rel.trine_stars"] = roles_stars["trine1"] + roles_stars["trine2"]
        f["palace.rel.trine_majors"] = roles_major["trine1"] + roles_major["trine2"]
        f["palace.rel.trine_hoa"] = sorted(set(roles_hoa["trine1"] + roles_hoa["trine2"]), key=HOA_NAMES.index)
        f["palace.rel.flank_stars"] = roles_stars["flank_prev"] + roles_stars["flank_next"]
        tp_roles = ("self", "opp", "trine1", "trine2")
        f["palace.rel.tp_names"] = [names[r] for r in tp_roles]          # the four palaces of the tam phương tứ chính, by name
        f["palace.rel.tp_stars"] = [s for r in tp_roles for s in roles_stars[r]]
        f["palace.rel.tp_majors"] = [s for r in tp_roles for s in roles_major[r]]
        f["palace.rel.tp_hoa"] = sorted({h for r in tp_roles for h in roles_hoa[r]}, key=HOA_NAMES.index)
        opp = by_b[branch_of("opp", b)]
        f["palace.rel.opp_tuan"], f["palace.rel.opp_triet"] = bool(opp["tuan"]), bool(opp["triet"])
        # brightness as rank, for the palace's own stars and (separately) for any star found in the tam phương
        dig = {**p["minor_dignity"], **p["major_dignity"]}
        for s, lv in dig.items():
            if rank_of(lv) is not None:
                f[f"palace.dignity_rank.{s}"] = rank_of(lv)
        for r in tp_roles:
            q = by_b[branch_of(r, b)]
            for s, lv in {**q["minor_dignity"], **q["major_dignity"]}.items():
                if rank_of(lv) is not None:
                    f[f"palace.tp_rank.{s}"] = rank_of(lv)
        # counting facts (objective): how many cát / sát stars stand in each role
        for tag, group in (("cat", CAT_STARS), ("sat", SAT_STARS)):
            f[f"palace.khi.{tag}_self"] = sum(1 for s in roles_stars["self"] if s in group)
            f[f"palace.khi.{tag}_tp"] = sum(1 for s in f["palace.rel.tp_stars"] if s in group)
            f[f"palace.khi.{tag}_flank"] = sum(1 for s in f["palace.rel.flank_stars"] if s in group)
        out[p["name"]] = f
    return out
