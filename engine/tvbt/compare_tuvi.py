"""Tử Vi side of the two-chart comparison. Independent of the Bát Tự engine: it reads only two TuViChart objects.
Default mode states positions and shared stars (placement is book-checked); how two people's palaces 'interact' is NOT interpreted,
because no source in the repository says so. Items are plain dicts, built by compare_deep.make_item."""
from __future__ import annotations

from .tuvi import TRIAD_GROUP, TuViChart

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
KEY = ["Mệnh", "Thân", "Phu Thê", "Phúc Đức"]


def _palaces(tv: TuViChart) -> dict[str, dict]:
    by = {p["name"]: p for p in tv.palaces}
    out = {n: by[n] for n in ("Mệnh", "Phu Thê", "Phúc Đức")}
    out["Thân"] = next(p for p in tv.palaces if p["is_than"])
    return out


def _four(tv: TuViChart, p: dict) -> list[dict]:
    """The palace and its tam phương tứ chính: itself, opposite, two tam hợp."""
    s = tv.structure[p["branch"]]
    by = {q["branch"]: q for q in tv.palaces}
    return [{"role": role, "palace": by[b]["name"], "branch": b, "major_stars": by[b]["major_stars"]}
            for role, b in (("bản cung", p["branch"]), ("xung chiếu", s["opposite"]), ("tam hợp", s["tam_hop"][0]), ("tam hợp", s["tam_hop"][1]))]


def geometry(i: int, j: int) -> tuple[str, str]:
    d = (j - i) % 12
    if d == 0:
        return "cùng_vị_trí", "cùng một vị trí trên vòng mười hai chi"
    if d == 6:
        return "xung_chiếu", "đối nhau (xung chiếu)"
    if TRIAD_GROUP[i] == TRIAD_GROUP[j]:
        return "tam_hợp", "cùng một bộ tam hợp"
    if d in (1, 11):
        return "liền_kề", "liền kề nhau"
    return "không", "không rơi vào các vị trí tam phương tứ chính của nhau"


def side_structure(tv: TuViChart) -> dict:
    ps = _palaces(tv)
    return {n: {"branch": p["branch"], "stem": p["stem"], "major_stars": p["major_stars"], "dignity": p["major_dignity"],
                "tuan": p["tuan"], "triet": p["triet"], "tam_phuong": _four(tv, p)} for n, p in ps.items()} | {
        "cuc": tv.cuc["name"], "menh_nap_am": tv.menh_nap_am, "year": tv.year_gz}


PAIRS = [("Mệnh", "Mệnh"), ("Thân", "Thân"), ("Phu Thê", "Phu Thê"), ("Phúc Đức", "Phúc Đức"), ("Mệnh", "Phu Thê"), ("Phu Thê", "Mệnh")]


def build(a: TuViChart, b: TuViChart, mk, experimental: bool) -> tuple[dict, list[dict]]:
    """Returns (structure of each chart, items). mk = compare_deep.make_item."""
    sa, sb = side_structure(a), side_structure(b)
    pa, pb = _palaces(a), _palaces(b)
    items: list[dict] = []
    # 1. where the key palaces sit: placement facts for each chart
    for who, s in (("a", sa), ("b", sb)):
        items.append(mk(f"tv.place.{who}", "tuvi", "direct", "placement", f"Bốn cung chính của lá số {who.upper()}", "; ".join(f"{n} ở {s[n]['branch']}" + (f" ({', '.join(s[n]['major_stars'])})" if s[n]['major_stars'] else " (vô chính diệu)") for n in KEY) + ".", {"who": who, "palaces": {n: s[n] for n in KEY}}, "CMP_TV_PLACEMENT", kind_vi="Vị trí cung"))
    # 2. geometry + shared stars between each pair of key palaces
    for x, y in PAIRS:
        i, j = pa[x]["branch_index"], pb[y]["branch_index"]
        code, vi = geometry(i, j)
        four_a, four_b = sa[x]["tam_phuong"], sb[y]["tam_phuong"]
        br_a, br_b = {q["branch"] for q in four_a}, {q["branch"] for q in four_b}
        stars_a = {st for q in four_a for st in q["major_stars"]}
        stars_b = {st for q in four_b for st in q["major_stars"]}
        own_shared = sorted(set(pa[x]["major_stars"]) & set(pb[y]["major_stars"]))
        data = {"a": {"palace": x, "branch": pa[x]["branch"], "major_stars": pa[x]["major_stars"], "tam_phuong": four_a},
                "b": {"palace": y, "branch": pb[y]["branch"], "major_stars": pb[y]["major_stars"], "tam_phuong": four_b},
                "geometry": code, "shared_own_major_stars": own_shared,
                "shared_tam_phuong_branches": sorted(br_a & br_b, key=BRANCHES.index), "shared_tam_phuong_major_stars": sorted(stars_a & stars_b)}
        plain = f"Cung {x} của A ở {pa[x]['branch']}, cung {y} của B ở {pb[y]['branch']}: hai cung {vi}."
        if own_shared:
            plain += f" Hai cung cùng có chính tinh {', '.join(own_shared)}."
        items.append(mk(f"tv.pair.{x}.{y}".replace(" ", "_"), "tuvi", "direct", "geometry", f"{x} (A) và {y} (B)", plain, data, "CMP_TV_GEOMETRY", kind_vi="Quan hệ vị trí"))
    # 3. experimental: nạp âm elements of the two Mệnh
    from .ganzhi import controls, generates
    ea, eb = a.menh_element, b.menh_element
    link = "cùng hành" if ea == eb else "A sinh B" if generates(ea, eb) else "B sinh A" if generates(eb, ea) else "A khắc B" if controls(ea, eb) else "B khắc A"
    items.append(mk("tv.napam", "tuvi", "direct", "napam", "Hành bản mệnh của hai người", f"Bản mệnh A thuộc hành {ea}, B thuộc hành {eb}: {link}.", {"a": ea, "b": eb, "link": link}, "CMP_TV_NAPAM", kind_vi="Nạp âm"))
    return {"a": sa, "b": sb}, items
