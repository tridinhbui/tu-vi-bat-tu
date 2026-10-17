"""Phase 7: pinned sensitivity of the variants to the readings the audit had to assume (tools/analyse_readings_phase7.py; pure oracle, 116,928 charts). The tests check STRUCTURE
(monotonicity, impossibilities) and key figures; they do not choose a reading."""
import json
from pathlib import Path

D = json.loads((Path(__file__).resolve().parent / "fixtures/readings_sensitivity.json").read_text("utf-8"))
SC = ["dong_cung", "doi_cung", "tam_hop", "hoi_chieu", "tp"]


def test_a_cndl_breaker_grid_is_monotone_in_scope_and_in_strictness():
    n = D["A_core"]["n"]
    assert n == 14688
    r = lambda sc, comp: D["A"][f"{sc}|{comp}"] / n
    for comp in ("mot_trong_ba", "cap_khong_kiep_hoac_ky", "tu_hai_trong_ba", "du_ca_ba"):
        assert r("dong_cung", comp) <= r("hoi_chieu", comp) <= r("tp", comp) and r("doi_cung", comp) <= r("hoi_chieu", comp) and r("tam_hop", comp) <= r("hoi_chieu", comp)
    for sc in SC:
        assert r(sc, "du_ca_ba") <= r(sc, "tu_hai_trong_ba") <= r(sc, "cap_khong_kiep_hoac_ky") <= r(sc, "mot_trong_ba")
    assert round(r("tp", "mot_trong_ba"), 3) == 0.821                    # the variant as built (TT tr.24: tam phương, one of the three)
    assert round(r("dong_cung", "mot_trong_ba"), 3) == 0.322 and round(r("doi_cung", "mot_trong_ba"), 3) == 0.216 and round(r("tp", "du_ca_ba"), 3) == 0.092


def test_b_kvgm_breaker_is_frequent_under_every_reading_that_keeps_a_threshold_of_one_and_the_literal_structure_is_no_rarer():
    n, n2 = D["B_core"]["n"], D["B2_core"]["n"]
    assert (n, n2) == (2784, 22272)
    assert round(D["B"]["tp|sau_sat|>=1"] / n, 3) == 0.917 and round(D["B"]["tp|sau_sat|>=2"] / n, 3) == 0.688 and round(D["B"]["tp|tu_sat|>=2"] / n, 3) == 0.5
    assert round(D["B2"]["tp|sau_sat|>=1"] / n2, 3) == 0.831           # the structure KL tr.62 mục 4 actually names (Khôi Việt in/hội chiếu Mệnh) breaks as often
    for sname in ("sau_sat", "tu_sat"):
        for sc in SC:
            assert D["B"][f"{sc}|{sname}|>=1"] >= D["B"][f"{sc}|{sname}|>=2"] >= D["B"][f"{sc}|{sname}|>=3"]
    assert D["B"]["dong_cung|khong_kiep|>=2"] == 0


def test_c_splt_threshold_grid():
    n = D["C_core"]["n"]
    assert n == 29328
    ks = [D["C"][f">={t}"] / n for t in (1, 2, 3, 4)]
    assert ks == sorted(ks, reverse=True) and round(D["C"][">=3+Ky"] / n, 3) == 0.053 and round(D["C"][">=1"] / n, 3) == 0.861


def test_g_unknown_sun_brightness_matters_for_nhat_nguyet():
    assert D["G"]["core"] == 25728 and D["G"]["unknown_rank"] == 3456                # 13.4% of the structure's charts sit on Thân/Mùi, where TH tr.31 prints no level
    states = {r: {k.split("|")[1]: v for k, v in D["G"].items() if k.startswith(f"state_if_rank_{r}|")} for r in range(5)}
    assert all(sum(v.values()) == 3456 for v in states.values())
    assert states[0] != states[2]                                                    # the assumed brightness changes the verdict for part of those charts


def test_h_the_two_ma_dau_dai_kiem_definitions_describe_different_populations():
    h = D["H"]
    assert h["kl_kinh_o_ngo_trong_menh"] == 4176 and h["tt_kinh_cung_thien_ma_trong_menh"] == 0 and h["kinh_va_thien_ma_cung_cung_bat_ky"] == 0
    # in this model Kình Dương (Mão Thìn Ngọ Mùi Dậu Tuất Tý Sửu) and Thiên Mã (Dần Thân Tỵ Hợi) never share a palace: TT p.142's 'Kình gặp Thiên Mã' can only mean a wider 'gặp'


def test_i_tu_phu_dong_cung_anchor_and_the_tuy_hoi_sentence():
    i = D["I"]
    assert i["tu_phu_dong_cung_o_menh"] == 1920 and i["tu_phu_dong_cung_o_than_khong_o_menh"] == 1440      # 'Mệnh hay Thân' (TH tr.72) would add 75% more charts
    assert i["tu_phu_dong_cung_o_ty_hoi_bat_ky"] == 0 and i["tu_sat_dong_cung_o_menh_ty_hoi"] == 1584       # TT tr.22 'Tử Phủ ... Tỵ Hợi' matches the Tử Sát structure of KL tr.50 mục 13


def test_f_tuan_triet_and_thach_trung():
    f = D["F_ttan"]
    assert f["cu_mon_ty_ngo"] == 1728 and f["thien_co_o_doi_cung"] == 1728          # Cự Môn at Tý/Ngọ always has Thiên Cơ opposite in this model: KL tr.44's second clause is automatic
    assert f["tuan_triet_o_menh"] == 600 and f["hoa_loc_o_menh"] == 96 and f["tam_hoa_trong_tam_phuong"] == 32
    ref = D["F_ref_active"]
    assert round(ref["CACH_X_TU_PHU_VU_TUONG@kl_132_193"] / D["core_n"]["CACH_X_TU_PHU_VU_TUONG@kl_132_193"], 3) == 0.29


def test_e_mechanics_thresholds_change_some_states_but_never_reorder_them():
    assert D["E"]["CACH_X_TU_PHU_VU_TUONG@kl_132_193|thuong1|drop1"] > 0 and D["E"]["CACH_X_TU_PHU_VU_TUONG@kl_132_193|thuong3|drop1"] > 0
    assert "CACH_X_THACH_TRUNG_AN_NGOC@kl_44|thuong1|drop1" not in {k for k, v in D["E"].items() if v}      # no boosters -> no sensitivity


def test_j_tam_ky_breaker_reading_of_chieu():
    n = D["J_core"]["n"]
    assert n == 4048
    r = {k: v / n for k, v in D["J"].items()}
    assert round(r["dong_cung+doi_cung (variant)"], 3) == 0.285                       # equals the pinned bi_pha share of the variant
    assert r["dong_cung"] <= r["dong_cung+doi_cung (variant)"] <= r["hoi_chieu"] <= r["tp"] and r["doi_cung"] <= r["dong_cung+doi_cung (variant)"]
    assert round(r["tp"], 3) == 0.501 and round(r["dong_cung"], 3) == 0.102


def test_k_khoi_viet_chieu_reading_for_nhat_nguyet_ham():
    n = D["K_core"]["n"]
    assert n == 13536
    r = {k: v / n for k, v in D["K"].items()}
    assert r["doi_cung"] >= r["tam_hop"] >= r["hoi_chieu"] >= r["tp"]                  # the wider the region where Khôi/Việt may 'chiếu', the rarer the refutation
    assert round(r["tp"], 3) == 0.436 and round(r["doi_cung"], 3) == 0.794
