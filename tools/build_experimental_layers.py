"""Builds engine/data/experimental/pack_van_han_layers.json: EXPERIMENTAL multi-layer (bản mệnh · đại hạn · lưu niên) interaction rules.
They are design hypotheses from general knowledge, checked against NO page of any book: reviewStatus=draft, outside the production PACKS,
only reachable with the `experimental` flag. Wording states a structure ("hai tầng Kỵ chồng cùng cung"), never an event."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "engine" / "data" / "experimental" / "pack_van_han_layers.json"
PROV = "Giả thuyết thiết kế của người viết, CHƯA đối chiếu trang sách nào; chỉ dùng để thử engine vận hạn đa tầng."


def f(n, op="eq", v=True):
    return {"fact": n, "operator": op, "value": v}


def ref(p, n, op="eq", v=True):
    return {"ref": {"palace": p, "fact": n}, "operator": op, "value": v}


def rule(id, desc, when, cons, exc=None, conflicts=None, prio=3):
    return dict(id=id, system="tu_vi", schoolId="experimental_draft", category="van_han_layers", description="[thử nghiệm] " + desc,
                conditions=when, consequences=cons, exceptions=exc or [], conflictsWith=conflicts or [], priority=prio,
                sourceIds=["SRC_EXPERIMENTAL"], reviewStatus="draft", version="0.1.0", subject="palace")


def fnd(claim, effect):
    return [{"kind": "finding", "claim": claim, "effect": effect, "scope": "temporal"}]


RULES = [
    rule("LY_KY_CHONG_TANG", "Từ hai tầng thời gian cùng đặt Hóa Kỵ lên một cung (bản mệnh, đại hạn, lưu niên).",
         f("time.ky_n", "gte", 2), fnd("ly_ky_chong_tang", "limit"),
         exc=[f("time.dai_han_hoa", "contains", "Hóa Khoa"), f("time.luu_hoa", "contains", "Hóa Khoa")], conflicts=["LY_LOC_CHONG_TANG"]),
    rule("LY_LOC_CHONG_TANG", "Từ hai tầng thời gian cùng đặt Hóa Lộc lên một cung.",
         f("time.loc_n", "gte", 2), fnd("ly_loc_chong_tang", "support"), conflicts=["LY_KY_CHONG_TANG"]),
    rule("LY_DAI_TIEU_TRUNG_CUNG", "Đại hạn và tiểu hạn cùng rơi vào một cung.",
         f("time.layers", "contains_all", ["dai_han", "tieu_han"]), fnd("ly_dai_tieu_trung_cung", "neutral")),
    rule("LY_LUU_KY_XUNG_MENH", "Hóa Kỵ lưu niên rơi vào cung xung chiếu với Mệnh.",
         {"all": [f("palace.name", "eq", "Mệnh"), ref("opp", "time.luu_hoa", "contains", "Hóa Kỵ")]},
         [{"kind": "assert", "fact": "derived.ky_luu_cham_truc_menh", "value": True, "scope": "chart"}] + fnd("ly_luu_ky_xung_menh", "limit"), prio=5),
    rule("LY_LUU_KY_NHAP_MENH", "Hóa Kỵ lưu niên rơi ngay vào cung Mệnh.",
         {"all": [f("palace.name", "eq", "Mệnh"), f("time.luu_hoa", "contains", "Hóa Kỵ")]},
         [{"kind": "assert", "fact": "derived.ky_luu_cham_truc_menh", "value": True, "scope": "chart"}] + fnd("ly_luu_ky_nhap_menh", "limit"), prio=5),
    rule("LY_DAI_HAN_KY_XUNG_MENH", "Hóa Kỵ của đại hạn rơi vào cung xung chiếu với Mệnh.",
         {"all": [f("palace.name", "eq", "Mệnh"), ref("opp", "time.dai_han_hoa", "contains", "Hóa Kỵ")]}, fnd("ly_dai_han_ky_xung_menh", "limit")),
    rule("LY_DAI_HAN_TRONG_TAM_PHUONG_CO_CACH", "Cung đại hạn nằm trong tam phương của Mệnh đang có cách thành (đọc kết quả cách cục, bước 1).",
         {"all": [f("time.layers", "contains", "dai_han"), f("time.in_tp_of_menh"), ref("Mệnh", "derived.cach.formed", "ne", [])]},
         fnd("ly_dai_han_trong_tam_phuong_menh_co_cach", "support"), exc=[f("palace.triet")]),
    rule("LY_KY_LUU_KHI_MENH_CO_CACH", "Hóa Kỵ lưu niên chạm trục Mệnh–Thiên Di trong khi Mệnh có cách thành (suy ra bước 1 → 2): cần xét cách có bị phá.",
         {"all": [f("palace.name", "eq", "Mệnh"), f("derived.ky_luu_cham_truc_menh"), f("derived.cach.formed", "ne", [])]},
         fnd("ly_ky_luu_khi_menh_co_cach", "limit"), prio=1),
]

if __name__ == "__main__":
    src = [{"id": "SRC_EXPERIMENTAL", "title": "Giả thuyết thiết kế thử engine (không phải sách)", "author": None, "locator": None,
            "verified": False, "note": PROV}]
    OUT.write_text(json.dumps({"rules": RULES, "sources": src}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(len(RULES), "rules")
