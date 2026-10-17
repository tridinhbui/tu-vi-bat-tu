"""The 25 audit proposals (action = de_xuat_sua), one row each: original condition, source/page, new reading, assumption, related variants,
what happened (implemented / dropped / not implemented and why), condition-level before/after on a fixed chart sample, regression test.
Output: engine/data/experimental/formation_proposals.json (+ rows used by build_formation_report6.py).
The 'before/after' figures are CONDITION-level: among charts where the baseline core is true, how often the original condition and the variant's
replacement are true, and how often they differ. relation (declared here, asserted in the tests) is one of
  mo_rong  replacement is true wherever the original is (it only adds)    thu_hep  replacement is true only where the original is
  thay_the neither contains the other                                     giu      same condition, only the reading is declared
  bo       the condition does not exist in the variant(s)                 chua     proposal deliberately NOT implemented (reason given)"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from tvbt import calendar_core as cc, lunar_input, tuvi  # noqa: E402
from tvbt.formation_explain import _Chart  # noqa: E402
from tvbt.knowledge import dsl  # noqa: E402

AUDIT = json.load(open(ROOT / "engine/data/experimental/formation_audit.json", encoding="utf-8"))
BASE = {f["id"]: f for f in json.load(open(ROOT / "engine/data/experimental/formations_experimental.json", encoding="utf-8"))["formations"]}
VAR = {f["id"]: f for f in json.load(open(ROOT / "engine/data/experimental/formations_school_variants.json", encoding="utf-8"))["formations"]}
OUT = ROOT / "engine/data/experimental/formation_proposals.json"
F = "CACH_X_"
DROP_RESCUE = "Không biến thể nào có sao cứu: TH tr.74 chỉ nói Tam Hóa cứu Mệnh ở bại/tuyệt địa, KL tr.132 chỉ gọi Hóa Khoa là sao giải nói chung; không trang nào nói sao đó cứu cách này."
HOP = "cách đọc 'gặp' trong ngữ cảnh đại tiểu hạn, không xác định phạm vi trong bản cách → không mở rộng"

# (formation key, role, id, relation, variants it touches (suffix), variant condition id or None, new reading, assumption, why-not (for chua/bo))
P = [
    ("TPVT", "breakers", "sat_dong_cung", "chua", [], None, "giữ đồng cung ở baseline", HOP, HOP),
    ("TPVT", "breakers", "ky_dong_cung", "chua", [], None, "giữ đồng cung ở baseline", HOP, HOP),
    ("TPVT", "rescuers", "tam_hoa_hoi_cuu", "bo", ["@kl_132_193", "@th_115"], None, "bỏ khỏi mọi biến thể", "", DROP_RESCUE),
    ("TPDC", "core", "core", "chua", [], None, "neo ở Mệnh hoặc Thân (TH tr.72)", "mô hình chỉ neo một cung; Thân không biểu diễn được ở dạng dữ liệu hiện tại",
     "anchor của cách cục là một tên cung duy nhất; cần thay đổi schema của phiên khác"),
    ("TPDC", "breakers", "sat_dong_cung", "giu", ["@tt_22"], "sat_dong_cung", "TT tr.22: sát tinh làm hỗn là phá; KL tr.50 là bản ngược (Kình Dương đồng cung là tăng thế)",
     "'gặp sát tinh' đọc là đồng cung", ""),
    ("TPDC", "breakers", "ky_dong_cung", "bo", ["@tt_22", "@kl_50"], None, "bỏ khỏi cả hai biến thể; KL tr.50 thêm 'Kỵ + Quyền ở Dần' như tăng thế", "", "TT tr.22 không nói Kỵ; KL tr.50 nói Kỵ+Quyền đồng cung là tốt"),
    ("CNDL", "breakers", "khong_kiep_dong_cung", "mo_rong", ["@tt_24"], "khong_kiep_trong_tam_phuong", "Địa Không/Địa Kiếp trong tam phương (TT tr.24 'các cung tam hợp xung chiếu')",
     "câu liệt kê Kiếp, Không, Kị: một trong số đó là đủ", ""),
    ("CNDL", "breakers", "ky_dong_cung", "mo_rong", ["@tt_24"], "ky_trong_tam_phuong", "Hóa Kỵ trong tam phương (TT tr.24)", "câu liệt kê Kiếp, Không, Kị: một trong số đó là đủ", ""),
    ("CNDL", "rescuers", "tam_hoa_hoi_cuu", "bo", ["@tt_24", "@kl_221"], None, "bỏ khỏi mọi biến thể", "", DROP_RESCUE),
    ("SPLT", "breakers", "ky_dong_cung", "chua", [], None, "giữ đồng cung ở baseline", HOP, HOP),
    ("SPLT", "rescuers", "tam_hoa_hoi_cuu", "bo", ["@th_76_77"], None, "bỏ khỏi mọi biến thể", "", DROP_RESCUE),
    ("NNTM", "core", "core", "thu_hep", ["@th_72"], "core", "TH tr.72: Nhật Thìn/Tỵ, Nguyệt Dậu/Tuất, Mệnh ở Nhật hay Nguyệt; bản KL tr.53 giữ lõi hợp chiếu của baseline",
     "bản KL: 'hợp chiếu' mô hình là cả hai sao trong tam phương", ""),
    ("NNTM", "rescuers", "tam_hoa_hoi_cuu", "bo", ["@th_72", "@kl_53_68"], None, "bỏ khỏi mọi biến thể", "", DROP_RESCUE),
    ("NNTM", "refutations", "Thái_Dương_ham", "thay_the", ["@kl_53_68"], "nhat_nguyet_ham_khong_khoi_viet", "KL tr.68: Nhật/Nguyệt hãm mà KHÔNG có Khôi/Việt chiếu mới là phản chứng",
     "'Khôi Việt chiếu' đọc là hội chiếu tam phương", "TH tr.74 chỉ nói 'không có cứu tinh' mà không nêu cứu tinh nên bản TH không có phản chứng này"),
    ("NNTM", "refutations", "Thái_Âm_ham", "thay_the", ["@kl_53_68"], "nhat_nguyet_ham_khong_khoi_viet", "như Thái Dương hãm (gộp một điều kiện cho cả hai sao)", "như trên", ""),
    ("NNTM", "refutations", "tuan_triet_an_ngu", "bo", ["@th_72", "@kl_53_68"], None, "bỏ khỏi cả hai biến thể", "", "KL tr.53 mục 11 và tr.85 coi Tuần/Triệt là điều kiện thuận cho Nhật Nguyệt/Thái Dương hãm"),
    ("NLTT", "breakers", "ky_dong_cung", "chua", [], None, "giữ nguyên ở baseline", "KL tr.85 'ghét Kỵ' không nêu phạm vi", "KL tr.85 'ghét Kỵ' không nêu phạm vi → không suy ra đồng cung"),
    ("NLTT", "rescuers", "tam_hoa_hoi_cuu", "bo", ["@kl_52_85"], None, "bỏ khỏi mọi biến thể", "", DROP_RESCUE),
    ("TTAN", "refutations", "tuan_triet_an_ngu", "bo", ["@kl_44", "@kl_58", "@kl_106"], None, "bỏ phản chứng; ở bản KL tr.106/TH tr.43 Tuần/Triệt là điều kiện thuận nằm trong lõi",
     "'gặp' Tuần/Triệt đọc là cùng cung Mệnh", "KL tr.106 và TH tr.43 coi Tuần/Triệt (hoặc Hóa Lộc) là điều kiện để ngọc lộ ra"),
    ("MDDK", "breakers", "that_sat_trong_tam_phuong", "thu_hep", ["@kl_64_xau"], "that_sat_thien_hinh_dong_cung", "KL tr.64 mục 5: Thất Sát VÀ Thiên Hình ĐỒNG CUNG với Kình Dương", "", ""),
    ("MDDK", "rescuers", "tam_hoa_hoi_cuu", "bo", ["@kl_64_xau", "@kl_64_tot"], None, "bỏ khỏi mọi biến thể", "", DROP_RESCUE),
    ("TKGH", "breakers", "ky_hoac_kinh_dong_cung", "mo_rong", ["@kl_66"], "ky_kinh_dong_cung_hoac_doi_cung", "KL tr.66: đồng cung HOẶC chiếu → đồng cung hoặc đối cung",
     "'chiếu' đọc hẹp là xung chiếu (đối cung); chưa mở ra tam phương vì câu sách không nói", ""),
    ("KVGM", "breakers", "sat_dong_cung", "mo_rong", ["@kl_44_62"], "sat_tinh_hoi_chieu", "KL tr.62 mục 4: sát tinh HỘI CHIẾU → tam phương", "'hội chiếu' = tam phương (từ ngữ đã xác định phạm vi)", ""),
    ("KVGM", "breakers", "ky_dong_cung", "chua", [], None, "giữ đồng cung ở baseline", "KL tr.62 'cản phá' không nêu phạm vi", "KL tr.62 'Hóa kỵ Thiên hình cản phá' không nêu phạm vi"),
    ("KVGM", "rescuers", "tam_hoa_hoi_cuu", "bo", ["@kl_44_62"], None, "bỏ khỏi mọi biến thể", "", DROP_RESCUE),
]
assert len(P) == 25


def when_of(f, role, cid):
    if role == "core":
        return f["core"]
    return next(c["when"] for c in f[role] if c["id"] == cid)


def sample():
    for ly in range(2014, 2024):
        for lm in range(1, 13):
            for ld in (4, 11, 18, 25):
                try:
                    sol = lunar_input.lunar_to_solar(ld, lm, ly, False, "vn")[0]
                except Exception:
                    continue
                for hb in range(12):
                    for g in ("male", "female"):
                        yield tuvi.compute(cc.normalize(cc.BirthInput(sol.year, sol.month, sol.day, 2 * hb, 0, "Asia/Ho_Chi_Minh", g)))


def build():
    rows = {(r["formation_key"], r["role"], r["id"]): r for r in AUDIT["rows"] if r["action"] == "de_xuat_sua"}
    assert set(rows) == {(p[0], p[1], p[2]) for p in P}, set(rows) ^ {(p[0], p[1], p[2]) for p in P}
    stats = {}
    for p in P:
        k, role, cid, rel, vs, vcid = p[:6]
        if not vcid:
            continue
        bf = BASE[next(b for b in BASE if b.endswith(rows[(k, role, cid)]["formation"][7:]))] if False else BASE[rows[(k, role, cid)]["formation"]]
        vf = VAR[rows[(k, role, cid)]["formation"] + vs[0]]
        stats[(k, role, cid)] = dict(base_when=when_of(bf, role, cid), var_when=when_of(vf, "core" if vcid == "core" else role if role != "refutations" else "refutations", vcid),
                                     base_core=bf["core"], n_base_core=0, base_true=0, var_true=0, both_true=0, base_only=0, var_only=0, unknown=0)
    n = 0
    for tv in sample():
        n += 1
        ch = _Chart(tv)
        facts, world = ch.facts_of("palace:Mệnh"), ch.world
        cache = {}
        for key, s in stats.items():
            core = dsl.evaluate(s["base_core"], facts, world)
            if core is not True:
                continue
            s["n_base_core"] += 1
            a, b = dsl.evaluate(s["base_when"], facts, world), dsl.evaluate(s["var_when"], facts, world)
            if a is None or b is None:
                s["unknown"] += 1
                continue
            s["base_true"] += a
            s["var_true"] += b
            s["both_true"] += a and b
            s["base_only"] += a and not b
            s["var_only"] += b and not a
    out = []
    for i, p in enumerate(P, 1):
        k, role, cid, rel, vs, vcid, reading, assumption, why = p
        r = rows[(k, role, cid)]
        s = stats.get((k, role, cid))
        out.append({"id": f"P{i:02d}", "formation": r["formation"], "formation_key": k, "name_vi": r["name_vi"], "role": role, "condition": cid, "label": r["label"],
                    "audit_status": r["status"], "cites": r["cites"], "relation": rel, "new_reading": reading, "assumption": assumption, "not_implemented_reason": why if rel in ("chua", "bo") else "",
                    "variants": [r["formation"] + v for v in vs], "variant_condition": vcid,
                    "before_after": ({kk: s[kk] for kk in ("n_base_core", "base_true", "var_true", "both_true", "base_only", "var_only", "unknown")} if s else None),
                    "regression_test": ("engine/tests/test_formation_proposals.py::test_relation_holds_on_the_sample" if s else "engine/tests/test_formation_proposals.py::test_unimplemented_and_dropped_stay_out_of_variants")})
    OUT.write_text(json.dumps({"version": 1, "sample_charts": n, "proposals": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    o = build()
    for r in o:
        print(r["id"], r["formation_key"], r["condition"], r["relation"], r["before_after"] and (r["before_after"]["base_true"], r["before_after"]["var_true"], r["before_after"]["base_only"], r["before_after"]["var_only"]))
