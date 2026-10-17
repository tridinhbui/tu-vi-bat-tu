"""Builds engine/data/experimental/pack_phi_hoa.json: EXPERIMENTAL Phi Hóa rules (school phi_tinh_draft).
Structure-only wording; every rule is a design hypothesis checked against NO Phi Tinh text. Outside production PACKS."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "engine" / "data" / "experimental" / "pack_phi_hoa.json"
PROV = "Giả thuyết thiết kế của người viết, CHƯA đối chiếu tài liệu Phi Tinh nào; bảng Tứ Hóa theo can dùng lại bảng tam hợp (chưa xác minh cho Phi Tinh)."


def f(n, op="eq", v=True):
    return {"fact": n, "operator": op, "value": v}


def ref(p, n, op="eq", v=True):
    return {"ref": {"palace": p, "fact": n}, "operator": op, "value": v}


def rule(id, desc, when, cons, exc=None, conflicts=None, prio=3):
    return dict(id=id, system="tu_vi", schoolId="phi_tinh_draft", category="phi_hoa", description="[thử nghiệm · Phi Hóa] " + desc,
                conditions=when, consequences=cons, exceptions=exc or [], conflictsWith=conflicts or [], priority=prio,
                sourceIds=["SRC_EXPERIMENTAL_PHI"], reviewStatus="draft", version="0.1.0", subject="palace")


def fnd(claim, effect):
    return [{"kind": "finding", "claim": claim, "effect": effect, "scope": "natal"}]


MENH = f("palace.name", "eq", "Mệnh")
RULES = [
    rule("PH_TU_HOA_KY", "Cung tự hóa Kỵ: can của cung làm Hóa Kỵ rơi vào sao nằm ngay trong cung đó.",
         f("phi.tu_hoa", "contains", "Hóa Kỵ"), fnd("ph_tu_hoa_ky", "neutral")),
    rule("PH_TU_HOA_LOC", "Cung tự hóa Lộc.", f("phi.tu_hoa", "contains", "Hóa Lộc"), fnd("ph_tu_hoa_loc", "neutral")),
    rule("PH_KY_XUNG_PHI", "Hóa Kỵ của một cung bay sang cung xung chiếu (xung phi).",
         f("phi.xung_phi", "contains", "Hóa Kỵ"), fnd("ph_ky_xung_phi", "limit"), exc=[f("phi.in.Hóa Khoa", "ne", [])]),
    rule("PH_LOC_KY_GIAO", "Hai cung phi Lộc và Kỵ cho nhau (A phi Lộc vào B, B phi Kỵ vào A).",
         f("phi.mutual.Hóa Lộc>Hóa Kỵ", "ne", []), fnd("ph_loc_ky_giao", "neutral")),
    rule("PH_MENH_LOC_QUAN_TAI", "Mệnh phi Hóa Lộc vào Quan Lộc hoặc Tài Bạch.",
         {"all": [MENH, f("phi.out.Hóa Lộc", "in", ["Quan Lộc", "Tài Bạch"])]}, fnd("ph_menh_loc_quan_tai", "support")),
    rule("PH_MENH_KY_NHAP", "Mệnh phi Hóa Kỵ vào Quan Lộc, Tài Bạch hoặc Phu Thê.",
         {"all": [MENH, f("phi.out.Hóa Kỵ", "in", ["Quan Lộc", "Tài Bạch", "Phu Thê"])]}, fnd("ph_menh_ky_nhap", "limit")),
    rule("PH_NHIEU_KY_VAO_MOT_CUNG", "Một cung nhận Hóa Kỵ từ ít nhất hai cung khác.", f("phi.in_ky_n", "gte", 2), fnd("ph_nhieu_ky_vao_mot_cung", "limit")),
    rule("PH_NHIEU_LOC_VAO_MOT_CUNG", "Một cung nhận Hóa Lộc từ ít nhất hai cung khác.", f("phi.in_loc_n", "gte", 2), fnd("ph_nhieu_loc_vao_mot_cung", "support")),
    rule("PH_MENH_CHUOI_LOC", "Chuỗi Lộc từ Mệnh đi qua ít nhất ba cung (Mệnh phi Lộc vào B, B phi Lộc vào C).",
         {"all": [MENH, f("phi.loc_chain_n", "gte", 3)]},
         [{"kind": "assert", "fact": "derived.phi.menh_loc_chain", "value": True, "scope": "chart"}] + fnd("ph_menh_chuoi_loc", "support"), prio=5),
    rule("PH_QUAN_LOC_TRONG_CHUOI_LOC", "Quan Lộc nằm trong chuỗi Lộc xuất phát từ Mệnh (suy ra bước 1 → 2, đọc cung Mệnh bằng ref).",
         {"all": [f("palace.name", "eq", "Quan Lộc"), f("derived.phi.menh_loc_chain"), ref("Mệnh", "phi.loc_chain", "contains", "Quan Lộc")]},
         fnd("ph_quan_loc_trong_chuoi_loc", "support"), prio=1),
]

if __name__ == "__main__":
    src = [{"id": "SRC_EXPERIMENTAL_PHI", "title": "Giả thuyết thiết kế Phi Hóa thử engine (không phải sách)", "author": None, "locator": None,
            "verified": False, "note": PROV}]
    OUT.write_text(json.dumps({"rules": RULES, "sources": src}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(len(RULES), "rules")
