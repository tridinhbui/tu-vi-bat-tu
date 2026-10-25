"""Vietnamese names and small phrase helpers shared by the reading chapters."""
from __future__ import annotations

from .. import kb

SIGN_VI = {s["id"]: s["vi"] for s in kb.core()["signs"]}
PLANET_VI = {k: v["vi"] for k, v in kb.core()["planets"].items()}
ASPECT_VI = {a["id"]: a["vi"] for a in kb.aspects()["aspects"]}
ELEMENT_VI = {"fire": "Lửa", "earth": "Đất", "air": "Khí", "water": "Nước"}
MODALITY_VI = {"cardinal": "khởi đầu", "fixed": "kiên định", "mutable": "biến đổi"}
DIGNITY_VI = {"domicile": "ở nhà của mình (domicile)", "exaltation": "ở cung tôn vinh (exaltation)", "triplicity": "làm chủ nhóm nguyên tố (triplicity)",
              "term": "ở giới hạn (term) của mình", "face": "ở diện (face) của mình", "detriment": "ở cung tổn hại (detriment)",
              "fall": "ở cung suy hãm (fall)", "peregrine": "lạc chỗ (peregrine), không có phẩm vị nào ở độ đang đứng"}
SOLAR_VI = {"cazimi": "nằm ngay tim Mặt Trời (cazimi)", "combust": "bị Mặt Trời đốt (combust)", "under_beams": "nằm dưới tia Mặt Trời"}
HOUSE_KIND_VI = {"angular": "nhà góc", "succedent": "nhà kế góc", "cadent": "nhà suy (cadent)"}
TEMPERAMENT_VI = {"sanguine": "huyết (sanguine: nóng và ẩm)", "choleric": "mật vàng (choleric: nóng và khô)",
                  "melancholic": "u sầu (melancholic: lạnh và khô)", "phlegmatic": "đàm (phlegmatic: lạnh và ẩm)"}
SCHOOL_VI = {"hellenistic": "chiêm tinh Hy Lạp cổ đại", "traditional": "chiêm tinh truyền thống (Lilly)", "modern": "chiêm tinh hiện đại (Alan Leo)",
             "compare": "đối chiếu các trường phái", "calc": "dữ kiện tính toán"}
SOURCE_SHORT = {"PTOL_TETRA": "Ptolemy, Tetrabiblos", "LILLY_CA": "Lilly, Christian Astrology", "VALENS_ANTH": "Valens, Anthologies",
                "LEO": "Alan Leo", "CONV_ORBS": "quy ước Thiên Bàn", "CONV_PATTERNS": "quy ước hiện đại", "SYSTEM": "định nghĩa của Thiên Bàn"}
ASPECT_NOUN = {"conjunction": "trùng tụ", "opposition": "góc đối", "trine": "góc tam hợp", "square": "góc vuông", "sextile": "góc lục hợp",
               "quincunx": "góc lệch 150°", "semisextile": "góc bán lục hợp", "semisquare": "góc bán vuông", "sesquiquadrate": "góc vuông rưỡi"}
ASPECT_WITH = {"conjunction": "trùng tụ với", "opposition": "đối đỉnh với", "trine": "tam hợp với", "square": "vuông góc với", "sextile": "lục hợp với",
               "quincunx": "lệch 150° với", "semisextile": "bán lục hợp với", "semisquare": "bán vuông với", "sesquiquadrate": "vuông rưỡi với"}
POINT_VI = {"asc": "cung Mọc", "mc": "Thiên Đỉnh", "dsc": "điểm Lặn", "ic": "Thiên Để", "fortune": "Lot of Fortune", "spirit": "Lot of Spirit",
            "north_node": "La Hầu", "south_node": "Kế Đô"}
ANGULARITY = {1: "angular", 4: "angular", 7: "angular", 10: "angular", 2: "succedent", 5: "succedent", 8: "succedent", 11: "succedent",
              3: "cadent", 6: "cadent", 9: "cadent", 12: "cadent"}


def P(name: str) -> str:
    return POINT_VI.get(name) if name in POINT_VI else PLANET_VI.get(name, name)


def num(x: float, d: int = 1) -> str:
    """Vietnamese decimal comma: 36.4 -> '36,4'."""
    return f"{x:.{d}f}".replace(".", ",")


def S(sign: str) -> str:
    return SIGN_VI.get(sign, sign)


def at(chart: dict, name: str) -> str:
    """'Sao Hỏa 19°33′ Song Ngư' (degree truncated, as on the chart)."""
    b = {**chart["bodies"], **chart["points"], **chart.get("angles", {}), **chart.get("lots", {})}[name]
    return f"{P(name)} {b['fmt']} {S(b['sign'])}"


def house_of(chart: dict, name: str) -> int | None:
    b = {**chart["bodies"], **chart["points"], **chart.get("lots", {})}.get(name)
    return b.get("house") if b else None


def join(items: list[str], last: str = "và") -> str:
    items = [i for i in items if i]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + f" {last} " + items[-1]


def src(ref: str) -> dict:
    """'LILLY_CA:p.535' -> {id, loc, label}."""
    sid, _, loc = ref.partition(":")
    base = SOURCE_SHORT.get(sid, kb.sources().get(sid, {}).get("title", sid))
    loc_vi = loc.replace("pp.", "tr. ").replace("p.", "tr. ")
    return {"id": sid, "loc": loc, "label": f"{base}{', ' + loc_vi if loc else ''}"}
