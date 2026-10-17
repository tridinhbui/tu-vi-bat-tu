"""Reading of a 'vận' palace (đại hạn or tiểu hạn) after Tử Vi Khảo Luận pp.233-236.
The book's idea: the stars of the vận palace are the events/people waiting at the door; the person brings the Mệnh stars to stay
among them, so the useful question is how the Mệnh configuration meets the vận configuration. Facts in, sourced sentences out;
nothing here says an event WILL happen."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .knowledge import dsl
from .tuvi import TuViChart

SRC = "Khảo Luận pp.233-236"
SRC_TH = "Thực Hành pp.115-117"
SAT4 = ("Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh")
GROUPS = {
    "tu_phu_vu_tuong": ("Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"),
    "sat_pha_tham": ("Thất Sát", "Phá Quân", "Tham Lang"),
    "co_nguyet_dong_luong": ("Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"),
}
STAGE_THUAN = {"Mệnh": "tuổi thơ", "Phụ Mẫu": "tuổi thanh thiếu niên", "Phúc Đức": "tuổi thành niên", "Điền Trạch": "tuổi thành danh",
               "Quan Lộc": "tuổi nổi danh", "Nô Bộc": "tuổi già", "Thiên Di": "tuổi nghỉ ngơi"}
STAGE_NGHICH = {"Mệnh": "tuổi thơ", "Huynh Đệ": "tuổi thanh thiếu niên", "Phu Thê": "tuổi thành niên", "Tử Tức": "tuổi thành danh",
                "Tài Bạch": "tuổi nổi danh", "Thiên Di": "tuổi nghỉ ngơi"}
DOMAIN = {"Mệnh": "chính mình", "Phụ Mẫu": "cha mẹ, người bề trên", "Phúc Đức": "đời sống tinh thần, họ hàng", "Điền Trạch": "nhà cửa, đất đai",
          "Quan Lộc": "công danh, sự nghiệp", "Nô Bộc": "bạn bè, người cộng tác", "Thiên Di": "giao thiệp bên ngoài, đi xa", "Tật Ách": "thể trạng",
          "Tài Bạch": "tiền bạc", "Tử Tức": "con cái", "Phu Thê": "hôn nhân", "Huynh Đệ": "anh chị em"}
SAT_POS = {"Thất Sát": [(("Dần", "Thân"), "muôn sự dễ thành"), (("Mão", "Dậu"), "muôn sự dở dang")],
           "Phá Quân": [(("Tý", "Ngọ"), "bạn bè đông đủ"), (("Mão", "Dậu"), "cô đơn, lẻ bóng")],
           "Tham Lang": [(("Thìn", "Tuất", "Mùi"), "giàu sang hiển hách"), (("Tý", "Ngọ", "Mão", "Dậu"), "hao tài, phóng túng")]}


def _stars(p) -> set[str]:
    return set(p["stars"])


def _has_group(p, g) -> bool:
    return any(s in p["major_stars"] for s in GROUPS[g])


def life_stage(direction: str, palace: str) -> str | None:
    return (STAGE_THUAN if direction == "thuận" else STAGE_NGHICH).get(palace)


_RULES = Path(__file__).resolve().parent.parent / "data" / "van_han_rules.json"
_SRC = {"SRC": SRC, "SRC_TH": SRC_TH}
HOA3 = ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")


@lru_cache(maxsize=1)
def rules() -> list[dict]:
    """The vận-palace readings as DATA (data/van_han_rules.json, built by tools/build_van_han_rules.py)."""
    rs = json.loads(_RULES.read_text("utf-8"))["rules"]
    for r in rs:
        for e in [r["when"]] + [t["when"] for t in r.get("tails", [])]:
            dsl.validate(e, {"vh.*"})
    return rs


def vh_facts(tv: TuViChart, v: dict) -> dict:
    """Flat facts (`vh.*`) comparing the Mệnh palace with the vận palace `v`. Geometry/membership only."""
    m = next(p for p in tv.palaces if p["name"] == "Mệnh")
    vs = _stars(v)
    sat_in = [s for s in SAT4 if s in vs]
    good = [s for s in ("Văn Xương", "Văn Khúc") if s in vs]
    hoa_good = [k for k, x in tv.tu_hoa.items() if x["branch"] == v["branch_index"] and k in ("Hóa Khoa", "Hóa Quyền", "Hóa Lộc")]
    hoa_here = [k for k, x in tv.tu_hoa.items() if x.get("branch") == v["branch_index"]]
    ky = [x for k, x in tv.tu_hoa.items() if k == "Hóa Kỵ"]
    return {
        "vh.m_major": list(m["major_stars"]), "vh.m_no_major": not m["major_stars"], "vh.m_tuan": bool(m["tuan"]), "vh.m_triet": bool(m["triet"]),
        "vh.v_major": list(v["major_stars"]), "vh.v_stars": list(v["stars"]), "vh.v_tuan": bool(v["tuan"]), "vh.v_triet": bool(v["triet"]),
        "vh.v_branch": v["branch"], "vh.v_hoa": hoa_here, "vh.hoa3_n": len([k for k in hoa_here if k in HOA3]),
        "vh.sat_in": sat_in, "vh.sat_in_n": len(sat_in), "vh.good": good + hoa_good, "vh.good_n": len(good + hoa_good),
        "vh.ky_here": any(x["branch"] == v["branch_index"] for x in ky),
        "vh.ky_here_star": any(x.get("star") and x["branch"] == v["branch_index"] for x in ky),
        "vh.loc": "Lộc Tồn" in vs or "Hóa Lộc" in hoa_here, "vh.ta_huu": bool({"Tả Phụ", "Hữu Bật"} & vs),
        "vh.khoi_viet": bool({"Thiên Khôi", "Thiên Việt"} & vs), "vh.xk": bool({"Văn Xương", "Văn Khúc"} & vs),
        "vh.dao_hong": bool({"Hồng Loan", "Đào Hoa"} & vs),
    }


def _fill(text: str, facts: dict) -> str:
    for k, v in facts.items():
        key = "{" + k[3:] + "}"
        if key in text:
            text = text.replace(key, ", ".join(v) if isinstance(v, list) else str(v))
    return text


def read(tv: TuViChart, van_palace: str) -> list[dict]:
    """Sentences about how the Mệnh palace meets the given vận palace. Rule-driven: every sentence comes from a rule in
    data/van_han_rules.json whose condition is true (same output as the former if/else implementation, proven by a differential test)."""
    return [{"text": o["text"], "src": o["src"]} for o in read_traced(tv, van_palace)]


def read_traced(tv: TuViChart, van_palace: str) -> list[dict]:
    """Like read(), plus `rule_id` (which data rule produced each sentence; the closing conflict note has rule_id None)."""
    out: list[dict] = []
    if van_palace == "Mệnh":
        return out
    v = next(p for p in tv.palaces if p["name"] == van_palace)
    facts = vh_facts(tv, v)
    for r in rules():
        if dsl.evaluate(r["when"], facts) is not True:
            continue
        if "tails" in r:
            tails = [t["text"] for t in r["tails"] if dsl.evaluate(t["when"], facts) is True]
            text = r["text"] + (": " + "; ".join(tails) if tails else "") + "."
        else:
            text = _fill(r["text"], facts)
        out.append({"text": text, "src": _SRC[r["src"]], "rule_id": r["id"]})
    joined = " ".join(o["text"] for o in out)
    if "đi lên" in joined and "đi xuống" in joined:
        out.append({"text": "Hai điều kiện trái chiều của sách (đi lên và đi xuống) cùng khớp, nên hệ thống không kết luận hạn này đi lên hay đi xuống.", "src": SRC, "rule_id": None})
    return out
