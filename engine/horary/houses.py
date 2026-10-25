"""House cusps for horary charts.

Regiomontanus (Lilly's system: his Tables of Houses are Regiomontanus tables) and Alcabitius (the common medieval system)
are computed here; Placidus, Whole Sign, Equal and Porphyry come from engine/western/houses.py. Ascendant and MC are always
western's. Spherical astronomy only, no approximation.

Regiomontanus: the equator is divided into twelve 30-degree arcs from the meridian; each cusp is where the great circle
through the north and south points of the horizon and that equator point cuts the ecliptic. For the house whose equator
point lies `a` degrees east of the MC, the pole of that circle satisfies tan(P) = tan(latitude) * sin(a), and the cusp is
lambda = atan2(sin R, cos R cos(eps) - sin(eps) tan P) with R = ARMC + a (a = 90 gives the Ascendant, a = 0 the MC).

Alcabitius: the Ascendant degree's diurnal semi-arc is trisected in right ascension from the MC (houses 11, 12) and its
nocturnal semi-arc from the Ascendant (houses 2, 3); each cusp is the ecliptic point with that right ascension.
"""
from __future__ import annotations

import math

from western import houses as WH

SYSTEMS = {
    "regiomontanus": {"vi": "Regiomontanus", "note": "Hệ nhà Lilly dùng (bảng nhà trong Christian Astrology là bảng Regiomontanus); mặc định cho trường phái Lilly."},
    "alcabitius": {"vi": "Alcabitius", "note": "Hệ nhà phổ biến thời trung cổ (thời Bonatti)."},
    "whole_sign": {"vi": "Whole Sign (trọn cung)", "note": "Cả cung Mọc là Nhà 1; cách cổ Hy Lạp, một số người làm horary hiện đại dùng."},
    "placidus": {"vi": "Placidus", "note": "Phổ biến ở phần mềm hiện đại; không phải hệ của Lilly."},
    "equal": {"vi": "Equal (nhà đều)", "note": "Mỗi nhà 30° từ độ Mọc."},
    "porphyry": {"vi": "Porphyry", "note": "Chia đều từng góc phần tư; dùng thay khi hệ khác vô nghiệm ở vĩ độ cao."},
}

_r, _d = math.radians, math.degrees


class PolarHouses(WH.PolarHouses):
    pass


def _norm(x: float) -> float:
    return x % 360.0


def _regio_cusp(armc: float, eps: float, lat: float, a: float) -> float:
    pole = math.atan(math.tan(_r(lat)) * math.sin(_r(a)))
    R = _r(armc + a)
    return _norm(_d(math.atan2(math.sin(R), math.cos(R) * math.cos(_r(eps)) - math.sin(_r(eps)) * math.tan(pole))))


def _ra_to_lon(ra: float, eps: float) -> float:
    a = _r(ra)
    return _norm(_d(math.atan2(math.sin(a), math.cos(a) * math.cos(_r(eps)))))


def _complete(c: list[float]) -> list[float]:
    """Cusps 1, 2, 3, 10, 11, 12 are set; the other six are their opposites."""
    for i in (0, 1, 2, 9, 10, 11):
        c[(i + 6) % 12] = _norm(c[i] + 180.0)
    return c


def cusps(system: str, armc: float, eps: float, lat: float) -> list[float]:
    """Twelve cusp longitudes, cusp 1 first."""
    if abs(lat) >= 90.0 - eps and system in ("regiomontanus", "alcabitius", "placidus"):
        raise PolarHouses(f"{SYSTEMS[system]['vi']}: không xác định trong vòng cực (|vĩ độ| ≥ {90 - eps:.1f}°)")
    if system == "regiomontanus":
        asc, mc = WH.ascendant(armc, eps, lat), WH.midheaven(armc, eps)
        c = [0.0] * 12
        c[0], c[9] = asc, mc
        c[10], c[11] = _regio_cusp(armc, eps, lat, 30.0), _regio_cusp(armc, eps, lat, 60.0)
        c[1], c[2] = _regio_cusp(armc, eps, lat, 120.0), _regio_cusp(armc, eps, lat, 150.0)
        return _complete(c)
    if system == "alcabitius":
        asc, mc = WH.ascendant(armc, eps, lat), WH.midheaven(armc, eps)
        dec = math.asin(math.sin(_r(eps)) * math.sin(_r(asc)))
        x = -math.tan(_r(lat)) * math.tan(dec)
        if abs(x) > 1.0:
            raise PolarHouses("Alcabitius: bán cung ngày của độ Mọc không tồn tại ở vĩ độ này")
        dsa = _d(math.acos(x))
        nsa = 180.0 - dsa
        c = [0.0] * 12
        c[0], c[9] = asc, mc
        c[10], c[11] = _ra_to_lon(armc + dsa / 3, eps), _ra_to_lon(armc + 2 * dsa / 3, eps)
        c[1], c[2] = _ra_to_lon(armc + dsa + nsa / 3, eps), _ra_to_lon(armc + dsa + 2 * nsa / 3, eps)
        return _complete(c)
    try:
        return WH.cusps(system, armc, eps, lat)
    except WH.PolarHouses as e:
        raise PolarHouses(str(e)) from e


def house_of(lon: float, cusp_list: list[float], near_cusp_deg: float = 0.0) -> tuple[int, bool]:
    """(house 1-12, moved_by_cusp_rule). With near_cusp_deg > 0, a body within that many degrees BEFORE the next cusp is
    counted in the next house (Lilly's practice; the degree limit is a school setting with its source in the KB)."""
    h = WH.house_of(lon, cusp_list)
    if near_cusp_deg > 0:
        nxt = cusp_list[h % 12]
        if 0 < (nxt - lon) % 360.0 <= near_cusp_deg:
            return h % 12 + 1, True
    return h, False


ANGULARITY = {1: "angular", 4: "angular", 7: "angular", 10: "angular", 2: "succedent", 5: "succedent", 8: "succedent",
              11: "succedent", 3: "cadent", 6: "cadent", 9: "cadent", 12: "cadent"}
