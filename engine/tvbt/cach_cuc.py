"""Mệnh chủ / Thân chủ and recognition of classic Tử Vi patterns (cách cục) by NAME ONLY.

Detection is purely positional (which stars lie in the Mệnh palace, its opposite, its two tam-hợp palaces or its
two neighbours). No cát/hung meaning is asserted here: the pattern names and the star groupings are the commonly
printed ones, not yet checked against a cited page, so every entry carries review="unverified".
"""
from __future__ import annotations

from .ganzhi import BRANCHES_VI

# Mệnh chủ by the branch of the Mệnh palace; Thân chủ by the year branch.
MENH_CHU = ["Tham Lang", "Cự Môn", "Lộc Tồn", "Văn Khúc", "Liêm Trinh", "Vũ Khúc",
            "Phá Quân", "Vũ Khúc", "Liêm Trinh", "Văn Khúc", "Lộc Tồn", "Cự Môn"]
THAN_CHU = ["Linh Tinh", "Thiên Tướng", "Thiên Lương", "Thiên Đồng", "Văn Xương", "Thiên Cơ",
            "Hỏa Tinh", "Thiên Tướng", "Thiên Lương", "Thiên Đồng", "Văn Xương", "Thiên Cơ"]


def menh_chu(menh_branch: int) -> dict:
    return {"star": MENH_CHU[menh_branch], "by": f"chi cung Mệnh ({BRANCHES_VI[menh_branch]})", "review": "unverified"}


def than_chu(year_branch: int) -> dict:
    return {"star": THAN_CHU[year_branch], "by": f"chi năm sinh ({BRANCHES_VI[year_branch]})", "review": "unverified"}


FOUR = {
    "Tử Phủ Vũ Tướng": ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"],
    "Cơ Nguyệt Đồng Lương": ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"],
    "Sát Phá Liêm Tham": ["Thất Sát", "Phá Quân", "Liêm Trinh", "Tham Lang"],
}
PAIRS = {frozenset(k.split("|")): v for k, v in {
    "Tử Vi|Thiên Phủ": "Tử Phủ", "Tử Vi|Thiên Tướng": "Tử Tướng", "Tử Vi|Thất Sát": "Tử Sát", "Tử Vi|Tham Lang": "Tử Tham",
    "Tử Vi|Phá Quân": "Tử Phá", "Thiên Cơ|Thái Âm": "Cơ Nguyệt", "Thiên Cơ|Cự Môn": "Cơ Cự", "Thiên Cơ|Thiên Lương": "Cơ Lương",
    "Thái Dương|Thái Âm": "Nhật Nguyệt", "Thái Dương|Cự Môn": "Nhật Cự", "Thái Dương|Thiên Lương": "Nhật Lương",
    "Vũ Khúc|Thiên Phủ": "Vũ Phủ", "Vũ Khúc|Thiên Tướng": "Vũ Tướng", "Vũ Khúc|Thất Sát": "Vũ Sát", "Vũ Khúc|Tham Lang": "Vũ Tham",
    "Vũ Khúc|Phá Quân": "Vũ Phá", "Thiên Đồng|Thái Âm": "Đồng Âm", "Thiên Đồng|Cự Môn": "Đồng Cự", "Thiên Đồng|Thiên Lương": "Đồng Lương",
    "Liêm Trinh|Thiên Phủ": "Liêm Phủ", "Liêm Trinh|Thiên Tướng": "Liêm Tướng", "Liêm Trinh|Thất Sát": "Liêm Sát",
    "Liêm Trinh|Tham Lang": "Liêm Tham", "Liêm Trinh|Phá Quân": "Liêm Phá",
}.items()}


def detect(tv) -> list[dict]:
    """Return the patterns that hold for this chart, each with the evidence that triggered it."""
    pal = {p["branch"]: p for p in tv.palaces}
    menh = next(p for p in tv.palaces if p["name"] == "Mệnh")
    s = tv.structure[menh["branch"]]
    tpt = [pal[menh["branch"]], pal[s["opposite"]], *[pal[b] for b in s["tam_hop"]]]   # tam phương tứ chính
    flank = [pal[b] for b in s["giap"]]
    in_tpt = {x for p in tpt for x in p["stars"]}
    out: list[dict] = []

    def add(pid, name, evidence, kind):
        out.append({"id": pid, "name": name, "evidence": evidence, "where": kind, "review": "unverified"})

    where = lambda name: next((f"cung {p['name']}" for p in tpt if name in p["stars"]), "")
    for nm, stars in FOUR.items():
        have = [x for x in stars if x in in_tpt]
        if len(have) == 4:
            add("cach_" + nm.lower().replace(" ", "_"), nm, "; ".join(f"{x} ở {where(x)}" for x in stars) + " (cả bốn sao đều nằm trong tam phương tứ chính của Mệnh)", "Mệnh")
    maj = menh["major_stars"]
    if len(maj) >= 2:
        for i in range(len(maj)):
            for j in range(i + 1, len(maj)):
                nm = PAIRS.get(frozenset((maj[i], maj[j])))
                if nm:
                    add("dong_cung_" + nm.lower().replace(" ", "_"), f"{nm} đồng cung", f"{maj[i]} và {maj[j]} cùng ở cung Mệnh", "Mệnh")
    if not maj:
        add("menh_vo_chinh_dieu", "Mệnh vô chính diệu", "cung Mệnh không có chính tinh", "Mệnh")
    names = lambda ps: {x for p in ps for x in p["stars"]}
    fl = names(flank)
    for nm, a, b in [("Tả Hữu giáp Mệnh", "Tả Phụ", "Hữu Bật"), ("Xương Khúc giáp Mệnh", "Văn Xương", "Văn Khúc"),
                     ("Khôi Việt giáp Mệnh", "Thiên Khôi", "Thiên Việt"), ("Kình Đà giáp Mệnh", "Kình Dương", "Đà La"),
                     ("Không Kiếp giáp Mệnh", "Địa Không", "Địa Kiếp"), ("Nhật Nguyệt giáp Mệnh", "Thái Dương", "Thái Âm")]:
        pa = next((p for p in flank if a in p["stars"]), None); pb = next((p for p in flank if b in p["stars"]), None)
        if pa and pb and pa is not pb:
            add("giap_" + a.lower().replace(" ", "_"), nm, f"{a} ở cung {pa['name']}, {b} ở cung {pb['name']} (hai bên cung Mệnh)", "Mệnh")
    for nm, a, b in [("Tả Hữu hội chiếu Mệnh", "Tả Phụ", "Hữu Bật"), ("Xương Khúc hội chiếu Mệnh", "Văn Xương", "Văn Khúc"),
                     ("Khôi Việt hội chiếu Mệnh", "Thiên Khôi", "Thiên Việt"), ("Không Kiếp hội chiếu Mệnh", "Địa Không", "Địa Kiếp")]:
        if a in in_tpt and b in in_tpt:
            add("hoi_" + a.lower().replace(" ", "_"), nm, f"{a} ở {where(a)}, {b} ở {where(b)}", "Mệnh")
    sat4 = [x for x in ("Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh") if x in in_tpt]
    if len(sat4) >= 3:
        add("sat_tinh_hoi_menh", "Sát tinh hội Mệnh", f"{', '.join(sat4)} trong tam phương tứ chính", "Mệnh")
    if menh["tuan"] or menh["triet"]:
        add("menh_tuan_triet", "Mệnh gặp " + ("Tuần" if menh["tuan"] else "Triệt"), "cung Mệnh nằm trên " + ("Tuần" if menh["tuan"] else "Triệt"), "Mệnh")
    for p in tv.palaces:   # whole-chart patterns: report the palace that holds them
        st = p["stars"]
        if "Thiên Mã" in st and ("Lộc Tồn" in st):
            add("loc_ma_giao_tri", "Lộc Mã giao trì", f"Lộc Tồn và Thiên Mã cùng ở cung {p['name']}", p["name"])
        if "Tham Lang" in st and ("Hỏa Tinh" in st or "Linh Tinh" in st):
            add("hoa_linh_tham", "Tham Lang gặp Hỏa/Linh đồng cung", f"Tham Lang cùng {'Hỏa Tinh' if 'Hỏa Tinh' in st else 'Linh Tinh'} ở cung {p['name']}", p["name"])
    than = next(p for p in tv.palaces if p["is_than"])
    if than["branch"] == menh["branch"]:
        add("menh_than_dong_cung", "Mệnh Thân đồng cung", "cung Thân trùng với cung Mệnh", "Mệnh")
    else:
        add("than_cu", f"Thân cư {than['name']}", f"cung Thân ({than['branch']}) là cung {than['name']}", than["name"])
    return out
