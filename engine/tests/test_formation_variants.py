"""Phase 5: school/source variants of the formations (data/experimental/formations_school_variants.json).
The baseline formations_experimental.json is untouched; variants never merge contradicting definitions; nothing is promoted to formation-level verified."""
import json
import re
import sys
from pathlib import Path

import pytest

from tvbt.formation_explain import analyse
from tvbt.knowledge.formation import load_formations
from tvbt.knowledge.loader import load_experimental

ROOT = Path(__file__).resolve().parents[2]
VPATH = ROOT / "engine/data/experimental/formations_school_variants.json"
VARS = load_formations(VPATH)
META = json.loads(VPATH.read_text("utf-8"))["meta"]
BASE = {f.id: f for f in load_experimental()[1]}
V = {f.id: f for f in VARS}


def test_variants_are_draft_experimental_and_point_to_a_baseline_formation():
    assert len(VARS) == 17 and set(META) == set(V)
    for f in VARS:
        assert f.reviewStatus == "draft" and f.experimental and "@" in f.id
        assert f.id.split("@")[0] in BASE and META[f.id]["base"] == f.id.split("@")[0]
        assert not f.rescuers, "no source says a star rescues a formation: variants carry no rescuer"
        assert META[f.id]["cites"], f.id
        assert META[f.id]["reviewer"].startswith("đối chiếu trang sách bởi phiên AI")


def test_variants_file_is_reproducible_from_the_builder_and_baseline_is_untouched():
    sys.path.insert(0, str(ROOT / "tools"))
    import build_formation_variants as bv
    fs, meta = bv.build()
    doc = json.loads(VPATH.read_text("utf-8"))
    assert fs == doc["formations"] and meta == doc["meta"]
    base_doc = json.loads((ROOT / "engine/data/experimental/formations_experimental.json").read_text("utf-8"))
    assert all("@" not in f["id"] for f in base_doc["formations"]) and len(base_doc["formations"]) == 10


def test_contradicting_definitions_stay_separate_variants():
    by = lambda base: sorted(i.split("@")[1] for i in V if i.startswith(base))
    assert by("CACH_X_THACH_TRUNG_AN_NGOC") == ["kl_106", "kl_44", "kl_58"]            # three definitions, none preferred
    assert by("CACH_X_MA_DAU_DOI_KIEM") == ["kl_64_tot", "kl_64_xau"]
    assert by("CACH_X_TU_PHU_DONG_CUNG") == ["kl_50", "tt_22"]
    assert by("CACH_X_NHAT_NGUYET_TINH_MINH") == ["kl_53_68", "th_72"]
    cores = {json.dumps(V[i].core, sort_keys=True) for i in V if i.startswith("CACH_X_THACH_TRUNG_AN_NGOC")}
    assert len(cores) == 3
    tt, kl = V["CACH_X_TU_PHU_DONG_CUNG@tt_22"], V["CACH_X_TU_PHU_DONG_CUNG@kl_50"]
    assert [b.id for b in tt.breakers] == ["sat_dong_cung"] and not kl.breakers      # TT: sát phá; KL: Kình đồng cung là tăng thế
    assert {b.id for b in kl.boosters} == {"kinh_luc_si_dong_cung", "ky_quyen_dong_cung"}


def test_tuan_triet_works_in_both_directions_without_being_merged():
    """baseline: refutation. Thạch trung ẩn ngọc (KL p.106 / TH p.43): enabling condition inside the core. Nhật Nguyệt (KL p.53/85): no refutation."""
    assert any(r.id == "tuan_triet_an_ngu" for r in BASE["CACH_X_THACH_TRUNG_AN_NGOC"].refutations)
    assert "palace.tuan" in json.dumps(V["CACH_X_THACH_TRUNG_AN_NGOC@kl_106"].core)
    assert not any(r.id == "tuan_triet_an_ngu" for r in V["CACH_X_NHAT_NGUYET_TINH_MINH@kl_53_68"].refutations)
    # and the harm direction is kept where the books say it (Tử Phủ Vũ Tướng, Tử Phủ đồng cung)
    assert any(r.id == "tuan_triet_an_ngu" for r in V["CACH_X_TU_PHU_VU_TUONG@kl_132_193"].refutations)
    assert any(r.id == "tuan_triet_an_ngu" for r in V["CACH_X_TU_PHU_DONG_CUNG@tt_22"].refutations)


def test_scopes_are_explicit_and_not_widened_beyond_the_sentence():
    ky = V["CACH_X_TAM_KY_GIA_HOI@kl_66"].breakers[0]
    assert "opp_hoa" in json.dumps(ky.when) and "tp_" not in json.dumps(ky.when)           # 'chiếu' read narrowly as đối cung, declared as a reading
    assert any("xung chiếu" in r for r in META["CACH_X_TAM_KY_GIA_HOI@kl_66"]["readings"])
    cn = V["CACH_X_CO_NGUYET_DONG_LUONG@tt_24"]
    assert all("tp_" in json.dumps(b.when) for b in cn.breakers) and "self_" not in json.dumps([b.when for b in cn.breakers])
    md = V["CACH_X_MA_DAU_DOI_KIEM@kl_64_xau"].breakers[0]
    assert "self_stars" in json.dumps(md.when) and "tp_" not in json.dumps(md.when)      # Thất Sát + Thiên Hình ĐỒNG CUNG, not tam phương
    kv = V["CACH_X_KHOI_VIET_GIAP_MENH@kl_44_62"].breakers[0]
    assert "sat_tp" in json.dumps(kv.when)                                                  # 'hội chiếu' stated by KL p.62 -> tam phương


LEVELS = {"doi_chieu_truc_tiep", "co_nguon_con_gia_dinh", "chua_du_nguon"}


def test_rule_levels_follow_each_rules_own_evidence():
    from collections import Counter
    for vid, m in META.items():
        assert set(m["rules"]) == set(m["rule_detail"]) and set(m["rules"].values()) <= LEVELS
        for key, d in m["rule_detail"].items():
            cites = [c for c in m["cites"] if c["id"] in d["cites"]]
            assert cites and len(cites) == len(d["cites"]), (vid, key)
            if d["level"] == "doi_chieu_truc_tiep":
                assert not d["assumption"] and all(c["read"] == "van_ban" for c in cites), (vid, key)
                assert d["audit_status"] in ("khop", "viet_moi_tu_trang_sach"), (vid, key)
            if any(c["read"] == "anh" for c in cites):
                assert d["level"] == "chua_du_nguon", (vid, key)                            # image-read pages are never counted as machine-checked
            if d["level"] == "co_nguon_con_gia_dinh":
                assert d["assumption"] or d["audit_status"] not in ("khop", "viet_moi_tu_trang_sach"), (vid, key)
    # pinned (Phase 6 recount, per-rule assumptions): the old coarse figure 15 / 8 is superseded
    c = Counter(x for m in META.values() for x in m["rules"].values())
    assert (c["doi_chieu_truc_tiep"], c["co_nguon_con_gia_dinh"], c["chua_du_nguon"]) == (10, 34, 3) and sum(c.values()) == 47
    # no variant rule is ever promoted to 'verified'
    assert "verified" not in json.dumps(META, ensure_ascii=False).replace("unverified", "")


def test_variants_do_not_leak_into_production_or_the_main_reading():
    src = "".join(p.read_text("utf-8") for p in (ROOT / "engine/tvbt").rglob("*.py") if "formation" not in p.name)
    assert "formations_school_variants" not in src
    loader = (ROOT / "engine/tvbt/knowledge/loader.py").read_text("utf-8")
    assert "school_variants" not in loader
    for f in VARS:
        assert "verified" not in f.reviewStatus.replace("unverified", "")


# ---- control charts: before/after, pinned. The variants were NOT tuned to the charts: they were written from the pages above. -------------
BEFORE_AFTER = {
    # chart: {variant id: state}   (baseline state in the second tuple slot is pinned in test_formation_audit.CONTROL)
    "hang_vo": {"CACH_X_CO_NGUYET_DONG_LUONG@tt_24": "bi_pha", "CACH_X_CO_NGUYET_DONG_LUONG@kl_221": "thanh", "CACH_X_TAM_KY_GIA_HOI@kl_66": "bi_pha"},
    "mau_ty_pha_san": {"CACH_X_CO_NGUYET_DONG_LUONG@tt_24": "bi_pha", "CACH_X_CO_NGUYET_DONG_LUONG@kl_221": "thanh_thuong",
                       "CACH_X_NHAT_NGUYET_TINH_MINH@kl_53_68": "bi_pha"},
    "han_cao_to": {"CACH_X_TU_PHU_VU_TUONG@kl_132_193": "thanh_thuong", "CACH_X_TU_PHU_VU_TUONG@th_115": "thanh_thuong"},
    "khong_minh": {"CACH_X_NHAT_NGUYET_TINH_MINH@kl_53_68": "thanh"},
    "nu_quy_mao": {"CACH_X_CO_NGUYET_DONG_LUONG@tt_24": "thanh", "CACH_X_CO_NGUYET_DONG_LUONG@kl_221": "thanh_thuong",
                   "CACH_X_KHOI_VIET_GIAP_MENH@kl_44_62": "bi_pha"},
}


@pytest.mark.parametrize("name", sorted(BEFORE_AFTER))
def test_control_chart_states_under_variants(name):
    sys.path.insert(0, str(ROOT / "engine/tests"))
    from test_book_examples import CHARTS, build
    got = {x["id"]: x["state"] for x in analyse(build(CHARTS[name]), VARS)}
    active = {k: v for k, v in got.items() if v != "khong_hien"}
    assert active == BEFORE_AFTER[name], (name, active)


def test_the_three_mismatches_are_explained_by_scope_and_the_kl_reading_still_disagrees():
    """Hạng Võ and Mậu Tý: TT p.24 / KL p.66 (explicit tam phương / chiếu) agree with the book's verdict; the KL p.221 reading, which names no breaker, still says 'thành'."""
    assert BEFORE_AFTER["hang_vo"]["CACH_X_CO_NGUYET_DONG_LUONG@tt_24"] == "bi_pha" == BEFORE_AFTER["hang_vo"]["CACH_X_TAM_KY_GIA_HOI@kl_66"]
    assert BEFORE_AFTER["mau_ty_pha_san"]["CACH_X_CO_NGUYET_DONG_LUONG@tt_24"] == "bi_pha"
    assert BEFORE_AFTER["hang_vo"]["CACH_X_CO_NGUYET_DONG_LUONG@kl_221"] == "thanh"          # not forced to agree
    assert BEFORE_AFTER["mau_ty_pha_san"]["CACH_X_CO_NGUYET_DONG_LUONG@kl_221"] == "thanh_thuong"


def test_variants_evaluate_without_unknowns_on_a_sample_of_real_charts():
    from tvbt import calendar_core as cc, tuvi
    n = 0
    for y in (1975, 1988, 2001):
        for m in (1, 5, 9):
            for hb in range(0, 24, 3):
                tv = tuvi.compute(cc.normalize(cc.BirthInput(y, m, 14, hb, 0, "Asia/Ho_Chi_Minh", "female" if hb % 2 else "male")))
                for x in analyse(tv, VARS):
                    assert x["state"] != "chua_du_du_kien", (y, m, hb, x["id"])
                    n += 1
    assert n == 72 * 17


def test_pinned_reach_scan_every_variant_fires_and_none_reaches_pha_duoc_cuu():
    """tools/scan_variant_reach.py (116,928 charts: ten consecutive years x every lunar day x 12 hours x 2 genders, plus four Mậu years). Pinned, reproducible without PDFs."""
    reach = json.loads((ROOT / "engine/tests/fixtures/formation_variants_reach.json").read_text("utf-8"))
    assert reach["charts"] == 116928 and set(reach["variants"]) == set(V)
    for vid, st in reach["variants"].items():
        assert set(st) - {"khong_hien"}, f"{vid} never fires in the scan"                   # reported, not 'fixed'
        assert "pha_duoc_cuu" not in st                                                      # no rescuers exist in any source-based variant
    assert reach["variants"]["CACH_X_THACH_TRUNG_AN_NGOC@kl_58"].get("hinh_thuc") == 32      # rare: Cự Môn Tý/Ngọ with all three Hóa in tam phương
