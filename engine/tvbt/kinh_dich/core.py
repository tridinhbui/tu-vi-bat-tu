"""Kinh Dịch cast: from six line values (6, 7, 8, 9, hào 1 at the bottom) to quẻ chủ, quẻ biến, quẻ hỗ and the position facts of each hào.

Nothing here interprets. The coin faces -> line values step is coins.py, the choice of texts to read is doc_hao.py (Chu Hy). The
position facts (chính, trung, ứng, ngôi) are the definitions of Ngô Tất Tố's preface, which also warns they hold 'đại khái': the reader
must say a fact only where a commentary on that hào uses it."""
from __future__ import annotations

from ..ha_lac import LINES_TRIGRAM
from .tables import (CHINH_CITE, HEX_HAN, NUMBER_HV, POSITION_HAN, POSITION_HV, POSITION_VI, RANK, RANK_CITE, TRUNG_CITE, UNG_CITE,
                     UNG_POLARITY_CITE, VALUE_CITE, VALUE_NAME, hexagram_of)

MOVING = {6, 9}


def hexagram(lines) -> dict:
    """lines: hào 1..6, 1 = dương."""
    lines = tuple(int(x) for x in lines)
    if len(lines) != 6 or set(lines) - {0, 1}:
        raise ValueError("six lines of 0 / 1 expected")
    return hexagram_of(LINES_TRIGRAM[lines[3:]], LINES_TRIGRAM[lines[:3]])


def ho(lines) -> dict:
    """Quẻ hỗ: hào 2-4 below, hào 3-5 above (the hỗ thể of the Tả truyện tradition; Kiền and Khôn are their own hỗ here — Mai Hoa's own rule
    乾坤無互 belongs to mai_hoa.py only)."""
    x = tuple(lines)
    return hexagram(x[1:4] + x[2:5])


def flip(lines, positions) -> tuple[int, ...]:
    x = list(lines)
    for p in positions:
        x[p - 1] ^= 1
    return tuple(x)


def hao_name(position: int, yang: bool) -> dict:
    num = "九" if yang else "六"
    han = f"{POSITION_HAN[0]}{num}" if position == 1 else (f"{POSITION_HAN[5]}{num}" if position == 6 else f"{num}{POSITION_HAN[position - 1]}")
    if position in (1, 6):
        hv = f"{POSITION_HV[position - 1]} {NUMBER_HV[num]}"
    else:
        hv = f"{NUMBER_HV[num]} {POSITION_HV[position - 1]}"
    return {"han": han, "hv": hv, "vi": f"{'Chín' if yang else 'Sáu'} {POSITION_VI[position - 1]}"}


def positions(lines) -> list[dict]:
    """Per hào: chính / trung / ứng / ngôi as Ngô Tất Tố's preface defines them."""
    out = []
    for p in range(1, 7):
        yang = bool(lines[p - 1])
        partner = p + 3 if p <= 3 else p - 3
        out.append({
            "position": p, "yang": yang, **hao_name(p, yang),
            "chinh": yang == (p % 2 == 1),
            "trung": p in (2, 5),
            "ung_with": partner,
            "ung": bool(lines[partner - 1]) != yang,
            "rank": RANK[p - 1],
            "below": p - 1 or None, "above": p + 1 if p < 6 else None,
        })
    return out


POSITION_CITES = {"chinh": CHINH_CITE, "trung": TRUNG_CITE, "ung_with": UNG_CITE, "ung": UNG_POLARITY_CITE, "rank": RANK_CITE}


def cast(values) -> dict:
    """values: six line values 6 / 7 / 8 / 9, hào 1 first."""
    values = [int(v) for v in values]
    if len(values) != 6 or set(values) - {6, 7, 8, 9}:
        raise ValueError("six line values from {6, 7, 8, 9} expected, hào 1 first")
    lines = tuple(1 if v in (7, 9) else 0 for v in values)
    moving = [p for p in range(1, 7) if values[p - 1] in MOVING]
    ban = hexagram(lines)
    bien_lines = flip(lines, moving)
    bien = hexagram(bien_lines) if moving else None
    hx = ho(lines)
    hao = positions(lines)
    for h in hao:
        h["value"] = values[h["position"] - 1]
        h["value_name"] = VALUE_NAME[h["value"]]
        h["moving"] = h["position"] in moving
    return {
        "values": values, "lines": list(lines), "moving": moving,
        "ban": ban, "bien": bien, "ho": hx,
        "noi": {"trigram": ban["lower"], "role": "nội quái"}, "ngoai": {"trigram": ban["upper"], "role": "ngoại quái"},
        "hao": hao, "bien_hao": positions(bien_lines) if moving else None,
        "cites": {"value": VALUE_CITE, **POSITION_CITES},
    }


def from_hexagram(number: int, moving=()) -> dict:
    """Manual entry: a King Wen number and the moving hào."""
    if number not in HEX_HAN:
        raise ValueError("King Wen number 1..64 expected")
    from ..ha_lac import HEXAGRAMS
    _, upper, lower = HEXAGRAMS[number]
    lines = hexagram_of(upper, lower)["lines"]
    moving = sorted(set(int(p) for p in moving))
    if any(p < 1 or p > 6 for p in moving):
        raise ValueError("moving hào are 1..6")
    values = [(9 if x else 6) if p in moving else (7 if x else 8) for p, x in enumerate(lines, start=1)]
    return cast(values)
