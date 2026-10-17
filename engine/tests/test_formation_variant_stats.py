"""Phase 6 sensitivity of the 17 variants over the pinned 116,928-chart scan (tools/scan_phase6.py). Pure fixture checks: reproducible without PDFs or a rescan."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = json.loads((ROOT / "engine/tests/fixtures/formation_variant_stats.json").read_text("utf-8"))
VARS = json.loads((ROOT / "engine/data/experimental/formations_school_variants.json").read_text("utf-8"))["formations"]
N = S["charts"]
CORE = {"CO_NGUYET_DONG_LUONG@kl_221": 14688, "CO_NGUYET_DONG_LUONG@tt_24": 14688, "KHOI_VIET_GIAP_MENH@kl_44_62": 2784, "MA_DAU_DOI_KIEM@kl_64_tot": 4176,
        "MA_DAU_DOI_KIEM@kl_64_xau": 4176, "NHAT_LE_TRUNG_THIEN@kl_52_85": 672, "NHAT_NGUYET_TINH_MINH@kl_53_68": 25728, "NHAT_NGUYET_TINH_MINH@th_72": 3072,
        "SAT_PHA_LIEM_THAM@th_76_77": 29328, "TAM_KY_GIA_HOI@kl_66": 4048, "THACH_TRUNG_AN_NGOC@kl_106": 696, "THACH_TRUNG_AN_NGOC@kl_44": 1728,
        "THACH_TRUNG_AN_NGOC@kl_58": 32, "TU_PHU_DONG_CUNG@kl_50": 1920, "TU_PHU_DONG_CUNG@tt_22": 1920, "TU_PHU_VU_TUONG@kl_132_193": 14736, "TU_PHU_VU_TUONG@th_115": 14736}


def fire(states):
    return sum(q for s, q in states.items() if s != "khong_hien")


def test_scan_size_and_core_activation_counts_are_pinned():
    assert N == 116928
    got = {k.replace("CACH_X_", ""): fire(v) for k, v in S["states"].items() if "@" in k}
    assert got == CORE
    for k, v in S["states"].items():
        assert sum(v.values()) == N, k


def test_states_a_variant_cannot_produce_by_construction_are_never_seen():
    """the 'impossible in the model' list for variants: structural (no breaker -> no bi_pha, no booster -> no thanh) plus the global ones."""
    for f in VARS:
        seen = S["states"][f["id"]]
        if not f["breakers"]:
            assert seen.get("bi_pha", 0) == 0, f["id"]
        if not f["boosters"]:
            assert seen.get("thanh", 0) == seen.get("thanh_thuong", 0) == 0, f["id"]
        if len(f["boosters"]) < f["thuong_at"]:
            assert seen.get("thanh_thuong", 0) == 0, f["id"]
        assert seen.get("pha_duoc_cuu", 0) == 0                                  # no rescuer in any variant
    no_breaker = [f["id"].split("CACH_X_")[1] for f in VARS if not f["breakers"]]
    assert len(no_breaker) == 9                                                  # for these nine, a 0% broken rate is a design fact, not a finding


def test_low_discrimination_breakers_are_flagged():
    """a breaker that is active in most charts where the formation exists says almost nothing. Reported, not 'fixed'."""
    rate = {k.replace("CACH_X_", ""): v.get("bi_pha", 0) / fire(v) for k, v in S["states"].items() if "@" in k and fire(v)}
    flagged = sorted(k for k, r in rate.items() if r > 0.5)
    assert flagged == ["CO_NGUYET_DONG_LUONG@tt_24", "KHOI_VIET_GIAP_MENH@kl_44_62"]
    assert round(rate["CO_NGUYET_DONG_LUONG@tt_24"], 3) == 0.821 and round(rate["KHOI_VIET_GIAP_MENH@kl_44_62"], 3) == 0.917


def test_disagreement_between_variants_of_the_same_formation():
    p = {k.replace("CACH_X_", ""): v for k, v in S["pairs"].items()}
    assert p["CO_NGUYET_DONG_LUONG@tt_24|CO_NGUYET_DONG_LUONG@kl_221"] == {"both_fire": 14688, "differ": 14352}      # 97.7%: TT and KL almost never agree
    assert p["TU_PHU_DONG_CUNG@tt_22|TU_PHU_DONG_CUNG@kl_50"] == {"both_fire": 1920, "differ": 1439}                    # TT: sát phá + Tả Hữu tăng thế; KL: Kình/Kỵ+Quyền, Xương Khúc, Khôi Việt, Khoa tăng thế
    assert p["MA_DAU_DOI_KIEM@kl_64_xau|MA_DAU_DOI_KIEM@kl_64_tot"] == {"both_fire": 4176, "differ": 94}
    assert p["TU_PHU_VU_TUONG@kl_132_193|TU_PHU_VU_TUONG@th_115"] == {"both_fire": 14736, "differ": 5652}
    # the three Thạch trung ẩn ngọc definitions describe nested populations (kl_58 ⊂ kl_106 ⊂ kl_44 is NOT claimed; only that they do not contradict where they overlap)
    for k, v in p.items():
        if k.startswith("THACH_TRUNG"):
            assert v["differ"] == 0


def test_variants_versus_baseline_cover_and_differ():
    b = S["vs_baseline"]
    assert all(v["variant_only"] == 0 for v in b.values())                       # no variant fires where the baseline core is absent
    assert b["CACH_X_NHAT_NGUYET_TINH_MINH@th_72"]["baseline_only"] == 22656     # TH's fixed positions are a small subset of the baseline structure
    assert b["CACH_X_THACH_TRUNG_AN_NGOC@kl_58"]["baseline_only"] == 1696
