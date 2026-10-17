"""Builds engine/data/experimental/formations_experimental.json (10 cách cục) and pack_engine_demo.json.

EXPERIMENTAL: these structures are design hypotheses written from general knowledge of Tử Vi. NONE has been checked against a cited
page, so every one is reviewStatus=draft, experimental=true, and lives outside the production PACKS list (loader.load_all never reads it).
Their purpose is to prove that the Phase-1 engine can express and evaluate: core / boosters / breakers / rescuers / refutations,
role-typed positions (đồng cung, xung chiếu, tam hợp, giáp), dignity_rank and cross-palace conditions.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "engine" / "data" / "experimental"

SAT = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]
PROV = "Giả thuyết thiết kế của người viết từ kiến thức chung, CHƯA đối chiếu trang sách nào; chỉ dùng để thử engine."


def f(name, op="eq", value=True):
    return {"fact": name, "operator": op, "value": value}


def has(fact, v):
    return f(fact, "contains", v)


def any_of(fact, vs):
    return f(fact, "contains_any", vs)


def all_of(fact, vs):
    return f(fact, "contains_all", vs)


def ev(id, label, when, rescues=None):
    d = {"id": id, "label": label, "when": when}
    if rescues:
        d["rescues"] = rescues
    return d


# shared vocabulary -------------------------------------------------------------------------------------------------------------
SAT_SELF = ev("sat_dong_cung", "sát tinh (Kình, Đà, Hỏa, Linh, Không, Kiếp) đồng cung với Mệnh", any_of("palace.rel.self_stars", SAT))
KY_SELF = ev("ky_dong_cung", "Hóa Kỵ đồng cung với Mệnh", has("palace.rel.self_hoa", "Hóa Kỵ"))
KHOA_GIAI = ev("khoa_dong_cung", "Hóa Khoa đồng cung với Mệnh (giải Kỵ)", has("palace.rel.self_hoa", "Hóa Khoa"), ["ky_dong_cung"])
TRIET_GIAI = ev("triet_dong_cung", "Triệt đóng ở cung Mệnh (giải sát tinh đồng cung)", f("palace.triet"), ["sat_dong_cung"])
TUAN_REF = ev("tuan_an_ngu", "Tuần án ngữ cung Mệnh", f("palace.tuan"))
B_TA_HUU = ev("ta_huu_hoi", "Tả Phụ, Hữu Bật cùng hội trong tam phương", all_of("palace.rel.tp_stars", ["Tả Phụ", "Hữu Bật"]))
B_XUONG_KHUC = ev("xuong_khuc_hoi", "Văn Xương hoặc Văn Khúc hội trong tam phương", any_of("palace.rel.tp_stars", ["Văn Xương", "Văn Khúc"]))
B_KHOI_VIET = ev("khoi_viet_hoi", "Thiên Khôi hoặc Thiên Việt hội trong tam phương", any_of("palace.rel.tp_stars", ["Thiên Khôi", "Thiên Việt"]))
B_LOC = ev("loc_hoi", "Lộc Tồn hoặc Hóa Lộc hội trong tam phương",
           {"any": [has("palace.rel.tp_stars", "Lộc Tồn"), has("palace.rel.tp_hoa", "Hóa Lộc")]})
B_KHOA_QUYEN = ev("khoa_quyen_hoi", "Hóa Khoa hoặc Hóa Quyền hội trong tam phương", any_of("palace.rel.tp_hoa", ["Hóa Khoa", "Hóa Quyền"]))


def hang(star):
    return ev(f"{star}_ham".replace(" ", "_"), f"{star} ở vị trí hãm (độ sáng thấp nhất trong bảng)", f(f"palace.tp_rank.{star}", "lte", 0))


FORMATIONS = [
    dict(id="CACH_X_TU_PHU_VU_TUONG", name_vi="Tử Phủ Vũ Tướng", anchor="Mệnh",
         core=all_of("palace.rel.tp_majors", ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"]),
         boosters=[B_TA_HUU, B_XUONG_KHUC, B_LOC], breakers=[SAT_SELF, KY_SELF], rescuers=[KHOA_GIAI, TRIET_GIAI],
         refutations=[TUAN_REF, hang("Thiên Tướng")]),
    dict(id="CACH_X_TU_PHU_DONG_CUNG", name_vi="Tử Phủ đồng cung", anchor="Mệnh",
         core=all_of("palace.rel.self_majors", ["Tử Vi", "Thiên Phủ"]),
         boosters=[B_TA_HUU, B_XUONG_KHUC, B_KHOI_VIET], breakers=[SAT_SELF, KY_SELF], rescuers=[KHOA_GIAI, TRIET_GIAI],
         refutations=[TUAN_REF]),
    dict(id="CACH_X_CO_NGUYET_DONG_LUONG", name_vi="Cơ Nguyệt Đồng Lương", anchor="Mệnh",
         core={"count": [has("palace.rel.tp_majors", s) for s in ("Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương")],
               "operator": "gte", "value": 3},
         boosters=[B_XUONG_KHUC, B_KHOA_QUYEN, B_KHOI_VIET],
         breakers=[ev("khong_kiep_dong_cung", "Địa Không hoặc Địa Kiếp đồng cung với Mệnh", any_of("palace.rel.self_stars", ["Địa Không", "Địa Kiếp"])), KY_SELF],
         rescuers=[KHOA_GIAI, ev("triet_giai_khong_kiep", "Triệt đóng ở cung Mệnh", f("palace.triet"), ["khong_kiep_dong_cung"])],
         refutations=[TUAN_REF]),
    dict(id="CACH_X_SAT_PHA_LIEM_THAM", name_vi="Sát Phá Liêm Tham", anchor="Mệnh",
         core={"count": [has("palace.rel.tp_majors", s) for s in ("Thất Sát", "Phá Quân", "Liêm Trinh", "Tham Lang")],
               "operator": "gte", "value": 3},
         boosters=[B_KHOA_QUYEN, B_TA_HUU, B_XUONG_KHUC, B_KHOI_VIET],
         breakers=[ev("sat_tu_hai_tro_len", "từ hai sát tinh trở lên đồng cung với Mệnh", f("palace.khi.sat_self", "gte", 2)), KY_SELF],
         rescuers=[KHOA_GIAI, ev("triet_giai_sat", "Triệt đóng ở cung Mệnh", f("palace.triet"), ["sat_tu_hai_tro_len"])],
         refutations=[TUAN_REF, hang("Thất Sát")]),
    dict(id="CACH_X_NHAT_NGUYET_TINH_MINH", name_vi="Nhật Nguyệt tịnh minh", anchor="Mệnh",
         core=all_of("palace.rel.tp_majors", ["Thái Dương", "Thái Âm"]),
         boosters=[ev("nhat_nguyet_deu_sang", "Thái Dương và Thái Âm đều sáng (độ sáng từ đắc trở lên)",
                      {"all": [f("palace.tp_rank.Thái Dương", "gte", 2), f("palace.tp_rank.Thái Âm", "gte", 2)]}),
                   B_TA_HUU, B_KHOA_QUYEN],
         breakers=[KY_SELF, ev("khong_kiep_dong_cung", "Địa Không hoặc Địa Kiếp đồng cung với Mệnh", any_of("palace.rel.self_stars", ["Địa Không", "Địa Kiếp"]))],
         rescuers=[KHOA_GIAI, ev("triet_giai_khong_kiep", "Triệt đóng ở cung Mệnh", f("palace.triet"), ["khong_kiep_dong_cung"])],
         refutations=[hang("Thái Dương"), hang("Thái Âm"), TUAN_REF]),
    dict(id="CACH_X_NHAT_LE_TRUNG_THIEN", name_vi="Nhật lệ trung thiên", anchor="Mệnh",
         core={"all": [f("palace.branch", "eq", "Ngọ"), has("palace.rel.self_majors", "Thái Dương")]},
         boosters=[B_TA_HUU, B_KHOA_QUYEN, B_XUONG_KHUC], breakers=[SAT_SELF, KY_SELF], rescuers=[KHOA_GIAI, TRIET_GIAI],
         refutations=[TUAN_REF, hang("Thái Dương")]),
    dict(id="CACH_X_THACH_TRUNG_AN_NGOC", name_vi="Thạch trung ẩn ngọc", anchor="Mệnh",
         core={"all": [f("palace.branch", "in", ["Tý", "Ngọ"]), has("palace.rel.self_majors", "Cự Môn")]},
         boosters=[B_KHOA_QUYEN, B_LOC, B_TA_HUU], breakers=[SAT_SELF, KY_SELF], rescuers=[KHOA_GIAI, TRIET_GIAI],
         refutations=[TUAN_REF, hang("Cự Môn")]),
    dict(id="CACH_X_MA_DAU_DOI_KIEM", name_vi="Mã đầu đới kiếm", anchor="Mệnh", kind="hung",
         core={"all": [f("palace.branch", "eq", "Ngọ"), has("palace.rel.self_stars", "Kình Dương")]},
         boosters=[B_TA_HUU, B_KHOI_VIET, B_XUONG_KHUC],
         breakers=[ev("sat_khac_dong_cung", "Hỏa, Linh, Không hoặc Kiếp đồng cung với Mệnh", any_of("palace.rel.self_stars", ["Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"])), KY_SELF],
         rescuers=[KHOA_GIAI, ev("triet_giai_sat_khac", "Triệt đóng ở cung Mệnh", f("palace.triet"), ["sat_khac_dong_cung"])],
         refutations=[hang("Kình Dương"), TUAN_REF]),
    dict(id="CACH_X_TAM_KY_GIA_HOI", name_vi="Tam kỳ gia hội", anchor="Mệnh",
         core=all_of("palace.rel.tp_hoa", ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"]),
         boosters=[ev("hoa_o_ban_cung", "có ít nhất một trong ba hóa ngay ở bản cung Mệnh", any_of("palace.rel.self_hoa", ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa"])),
                   B_TA_HUU, B_XUONG_KHUC],
         breakers=[ev("ky_trong_tam_phuong", "Hóa Kỵ cũng nằm trong tam phương", has("palace.rel.tp_hoa", "Hóa Kỵ"))],
         rescuers=[ev("ta_huu_giai_ky", "Tả Phụ, Hữu Bật cùng hội trong tam phương (giải Kỵ)", all_of("palace.rel.tp_stars", ["Tả Phụ", "Hữu Bật"]), ["ky_trong_tam_phuong"])],
         refutations=[TUAN_REF, ev("triet_an_ngu", "Triệt án ngữ cung Mệnh", f("palace.triet"))]),
    dict(id="CACH_X_KHOI_VIET_GIAP_MENH", name_vi="Khôi Việt giáp Mệnh", anchor="Mệnh",
         core={"any": [{"all": [has("palace.rel.flank_prev_stars", "Thiên Khôi"), has("palace.rel.flank_next_stars", "Thiên Việt")]},
                       {"all": [has("palace.rel.flank_prev_stars", "Thiên Việt"), has("palace.rel.flank_next_stars", "Thiên Khôi")]}]},
         boosters=[ev("co_chinh_tinh", "cung Mệnh có chính tinh", f("palace.has_no_major", "eq", False)), B_TA_HUU, B_XUONG_KHUC],
         breakers=[SAT_SELF, KY_SELF], rescuers=[KHOA_GIAI, TRIET_GIAI],
         refutations=[ev("vo_chinh_dieu", "Mệnh vô chính diệu (phải mượn sao đối cung)", f("palace.has_no_major")), TUAN_REF]),
]

DEMO_RULES = [   # engine-capability demo rules (structure only; wording makes no astrological claim)
    dict(id="XR_MENH_CO_CACH_THANH", system="tu_vi", schoolId="experimental_draft", category="engine_demo",
         description="[thử nghiệm] Mệnh có ít nhất một cách ở trạng thái thành (suy ra từ kết quả cách cục, bước 1).",
         conditions={"all": [f("palace.name", "eq", "Mệnh"), f("derived.cach.formed", "ne", [])]},
         consequences=[{"kind": "assert", "fact": "derived.menh_co_cach_thanh", "value": True, "scope": "chart"}],
         priority=5, sourceIds=["SRC_EXPERIMENTAL"], reviewStatus="draft", subject="palace"),
    dict(id="XR_QUAN_LOC_TRONG_TAM_PHUONG_CACH", system="tu_vi", schoolId="experimental_draft", category="engine_demo",
         description="[thử nghiệm] Quan Lộc nằm trong tam phương của Mệnh đang có cách thành (đọc fact suy ra ở bước 1 và vị trí tương đối, bước 2).",
         conditions={"all": [f("palace.name", "eq", "Quan Lộc"), f("derived.menh_co_cach_thanh", "eq", True),
                             {"ref": {"palace": "Mệnh", "fact": "palace.rel.tp_names"}, "operator": "contains", "value": "Quan Lộc"}]},
         consequences=[{"kind": "finding", "claim": "xr_quan_loc_trong_tam_phuong_cach", "effect": "support", "scope": "natal"}],
         exceptions=[f("palace.triet")], conflictsWith=["XR_QUAN_LOC_KY_HAN_CHE"], priority=3, sourceIds=["SRC_EXPERIMENTAL"],
         reviewStatus="draft", subject="palace"),
    dict(id="XR_QUAN_LOC_KY_HAN_CHE", system="tu_vi", schoolId="experimental_draft", category="engine_demo",
         description="[thử nghiệm] Quan Lộc đồng cung Hóa Kỵ khi Mệnh có cách thành: ghi nhận như yếu tố cần xét thêm.",
         conditions={"all": [f("palace.name", "eq", "Quan Lộc"), f("derived.menh_co_cach_thanh", "eq", True), has("palace.rel.self_hoa", "Hóa Kỵ")]},
         consequences=[{"kind": "finding", "claim": "xr_quan_loc_ky_han_che", "effect": "limit", "scope": "natal"}],
         conflictsWith=["XR_QUAN_LOC_TRONG_TAM_PHUONG_CACH"], priority=3, sourceIds=["SRC_EXPERIMENTAL"], reviewStatus="draft", subject="palace"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for x in FORMATIONS:
        x.update(provenance=PROV, reviewStatus="draft", experimental=True, sourceIds=[],
                 note="EXPERIMENTAL — không nằm trong production; mọi điều kiện cần đối chiếu sách trước khi dùng.")
    (OUT / "formations_experimental.json").write_text(json.dumps({"formations": FORMATIONS}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    src = [{"id": "SRC_EXPERIMENTAL", "title": "Giả thuyết thiết kế thử engine (không phải sách)", "author": None, "locator": None,
            "verified": False, "note": PROV}]
    rules = [dict(r, exceptions=r.get("exceptions", []), conflictsWith=r.get("conflictsWith", []), version="0.1.0") for r in DEMO_RULES]
    (OUT / "pack_engine_demo.json").write_text(json.dumps({"rules": rules, "sources": src}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(len(FORMATIONS), "formations,", len(rules), "demo rules")


if __name__ == "__main__":
    main()
