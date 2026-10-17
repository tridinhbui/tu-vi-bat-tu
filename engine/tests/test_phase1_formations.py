"""Each of the 10 EXPERIMENTAL cách cục is tested through all its states:
khong_hien · hinh_thuc · thanh · thanh_thuong · bi_pha · pha_duoc_cuu · refutation downgrade.
The structures are unverified design hypotheses (data/experimental); these tests prove the ENGINE evaluates them as specified,
not that the doctrine is right."""
import pytest

from phase1_helpers import base_facts, synth
from tvbt.knowledge.formation import validate_formations
from tvbt.knowledge.loader import load_all, load_experimental
from tvbt.knowledge.schema import validate_pack
from tvbt.reasoning import conflict, engine, facts
from tvbt.reasoning.formation_eval import evaluate_formation, render_vi
from tvbt.tuvi import PALACES

KNOWN = {"palace.*", "chart.*", "bazi.*", "derived.*"}
RULES, FORMS, XSRC = load_experimental()
BY_ID = {f.id: f for f in FORMS}

S = lambda star, where="Mệnh": ("star", star, where)          # noqa: E731
H = lambda hoa, where="Mệnh": ("hoa", hoa, where)             # noqa: E731
TA_HUU = [S("Tả Phụ", "Thiên Di"), S("Hữu Bật", "Thiên Di")]
XK = [S("Văn Xương", "Tài Bạch")]
KV = [S("Thiên Khôi", "Thiên Di")]
LOC = [S("Lộc Tồn", "Quan Lộc")]
KQ = [H("Hóa Quyền", "Quan Lộc")]
KY, KHOA, TUAN = [H("Hóa Kỵ")], [H("Hóa Khoa")], [("tuan", "Mệnh")]
KINH = [S("Kình Dương")]
TAM_HOA = [H("Hóa Lộc", "Quan Lộc"), H("Hóa Quyền", "Tài Bạch"), H("Hóa Khoa", "Thiên Di")]      # Lộc, Quyền, Khoa all in the tam phương

# fid -> (menh branch, core ops, [booster op-lists], breaker ops, breaker id, rescuer ops, rescuer id, refutation ops, refutation id)   -- definition v2
CASES = {
    "CACH_X_TU_PHU_VU_TUONG": ("Tý", [S("Tử Vi"), S("Thiên Phủ", "Quan Lộc"), S("Vũ Khúc", "Tài Bạch"), S("Thiên Tướng", "Thiên Di")],
                               [TA_HUU, XK, LOC], KINH, "sat_dong_cung", TAM_HOA, "tam_hoa_hoi_cuu", TUAN, "tuan_triet_an_ngu"),
    "CACH_X_TU_PHU_DONG_CUNG": ("Dần", [S("Tử Vi"), S("Thiên Phủ")], [TA_HUU, XK, KV], KINH, "sat_dong_cung", TAM_HOA, "tam_hoa_hoi_cuu", TUAN, "tuan_triet_an_ngu"),
    "CACH_X_CO_NGUYET_DONG_LUONG": ("Tý", [S("Thiên Cơ"), S("Thái Âm", "Quan Lộc"), S("Thiên Đồng", "Tài Bạch"), S("Thiên Lương", "Thiên Di")],
                                    [XK, KQ], [S("Địa Không")], "khong_kiep_dong_cung", TAM_HOA, "tam_hoa_hoi_cuu", TUAN, "tuan_triet_an_ngu"),
    "CACH_X_SAT_PHA_LIEM_THAM": ("Tý", [S("Thất Sát"), S("Phá Quân", "Quan Lộc"), S("Tham Lang", "Tài Bạch")],
                                 [KQ, TA_HUU, XK, KV], [S("Kình Dương"), S("Đà La"), S("Hỏa Tinh", "Thiên Di"), H("Hóa Kỵ", "Thiên Di")],
                                 "ba_sat_va_ky_trong_tam_phuong", TAM_HOA, "tam_hoa_hoi_cuu", TUAN, "tuan_triet_an_ngu"),
    "CACH_X_NHAT_NGUYET_TINH_MINH": ("Tý", [S("Thái Dương"), S("Thái Âm", "Quan Lộc")],
                                     [[("dig", "Thái Dương", "Mệnh", "miếu"), ("dig", "Thái Âm", "Quan Lộc", "vượng")], TA_HUU, KQ],
                                     KY, "ky_dong_cung", KHOA, "khoa_dong_cung", TUAN, "tuan_triet_an_ngu"),
    "CACH_X_NHAT_LE_TRUNG_THIEN": ("Ngọ", [S("Thái Dương")], [TA_HUU, [H("Hóa Khoa", "Tài Bạch")], XK], KINH, "sat_dong_cung",
                                   TAM_HOA, "tam_hoa_hoi_cuu", TUAN, "tuan_triet_an_ngu"),
    "CACH_X_THACH_TRUNG_AN_NGOC": ("Tý", [S("Cự Môn")], [TAM_HOA, TA_HUU], KY, "ky_hoac_kinh_dong_cung", KHOA, "khoa_dong_cung", TUAN, "tuan_triet_an_ngu"),
    "CACH_X_MA_DAU_DOI_KIEM": ("Ngọ", [S("Kình Dương")], [KQ, TA_HUU], [S("Thất Sát", "Quan Lộc")], "that_sat_trong_tam_phuong",
                               TAM_HOA, "tam_hoa_hoi_cuu", TUAN, "tuan_triet_an_ngu"),
    "CACH_X_TAM_KY_GIA_HOI": ("Tý", [H("Hóa Lộc", "Quan Lộc"), H("Hóa Quyền", "Tài Bạch"), H("Hóa Khoa", "Thiên Di")],
                              [[H("Hóa Lộc", "Mệnh")], TA_HUU, XK], [H("Hóa Kỵ")], "ky_hoac_kinh_dong_cung",
                              TA_HUU, "ta_huu_giai_ky", TUAN, "tuan_triet_an_ngu"),
    "CACH_X_KHOI_VIET_GIAP_MENH": ("Tý", [S("Thiên Khôi", "Huynh Đệ"), S("Thiên Việt", "Phụ Mẫu")],
                                   [[S("Tử Vi")], TA_HUU, XK], KINH, "sat_dong_cung", TAM_HOA, "tam_hoa_hoi_cuu", TUAN, "tuan_triet_an_ngu"),
}


def verdict(fid, *op_lists, menh=None):
    c = CASES[fid]
    ops = [o for ol in op_lists for o in ol]
    f = base_facts(ops, menh or c[0])["palace:Mệnh"]
    return evaluate_formation(BY_ID[fid], f)


def test_all_ten_formations_present_and_valid():
    assert sorted(CASES) == sorted(BY_ID) and len(FORMS) == 10
    assert validate_formations(FORMS, KNOWN, set(PALACES)) == []
    for f in FORMS:                                      # every formation has all four evidence kinds (the spec of this phase)
        assert f.boosters and f.breakers and f.rescuers and f.refutations, f.id
        assert f.reviewStatus == "draft" and f.experimental and f.sourceIds == []


@pytest.mark.parametrize("fid", sorted(CASES))
def test_state_machine(fid):
    menh, core, boosters, brk, brk_id, rsc, rsc_id, ref, ref_id = CASES[fid]
    # 1. no core -> khong_hien
    wrong = "Hợi" if menh != "Hợi" else "Tỵ"
    assert verdict(fid, [], menh=wrong)["state"] == "khong_hien"
    # 2. core only -> hinh_thuc (nothing strengthens it)
    d = verdict(fid, core)
    assert d["state"] == "hinh_thuc" and d["core"] is True and d["boosters"] == [] and d["missing_for_next_level"]
    # 3. one booster -> thanh;   4. two boosters -> thanh_thuong
    d = verdict(fid, core, boosters[0])
    assert d["state"] == "thanh" and len(d["boosters"]) == 1, d
    d = verdict(fid, core, boosters[0], boosters[1])
    assert d["state"] == "thanh_thuong" and len(d["boosters"]) == 2
    # 5. breaker, no rescuer -> bi_pha, even though a booster is present
    d = verdict(fid, core, boosters[0], brk)
    assert d["state"] == "bi_pha" and brk_id in d["uncovered_breakers"] and d["missing_for_next_level"], d
    # 6. breaker + its rescuer -> pha_duoc_cuu
    d = verdict(fid, core, boosters[0], brk, rsc)
    assert d["state"] == "pha_duoc_cuu" and brk_id in d["breakers"] and rsc_id in d["rescuers"] and d["uncovered_breakers"] == [], d
    # 7/8. a refutation lowers thành by one rung and thanh_thuong by one rung; it is always listed
    d = verdict(fid, core, boosters[0], boosters[1], ref)
    assert d["state"] == "thanh" and d["downgraded_by_refutation"] and ref_id in d["refutations"], d
    d = verdict(fid, core, boosters[0], ref)
    assert d["state"] == "hinh_thuc" and d["downgraded_by_refutation"], d
    # a refutation on a core-only structure changes nothing (already the lowest rung) but is still reported
    d = verdict(fid, core, ref)
    assert d["state"] == "hinh_thuc" and not d["downgraded_by_refutation"] and ref_id in d["refutations"], d


@pytest.mark.parametrize("fid", sorted(CASES))
def test_rescuer_does_nothing_without_the_breaker_and_breaker_beats_boosters(fid):
    menh, core, boosters, brk, brk_id, rsc, rsc_id, ref, ref_id = CASES[fid]
    d = verdict(fid, core, boosters[0], rsc)                               # rescuer present, nothing to rescue: it must not invent a breaker
    assert d["breakers"] == [] and d["state"] in ("hinh_thuc", "thanh", "thanh_thuong")
    d = verdict(fid, core, *boosters, brk)                                 # every booster + a breaker: never a plain thành (no summing)
    assert d["state"] in ("bi_pha", "pha_duoc_cuu") and brk_id in d["breakers"]
    if rsc_id not in d["rescuers"]:
        assert d["state"] == "bi_pha"


def test_rescuer_only_covers_the_breakers_it_names():
    # CNĐL: Khoa rescues Kỵ but NOT Không/Kiếp; Tam Hóa hội rescues every breaker
    f = "CACH_X_CO_NGUYET_DONG_LUONG"
    core = CASES[f][1]
    d = verdict(f, core, [S("Địa Không")], KY, KHOA)
    assert d["state"] == "bi_pha" and d["uncovered_breakers"] == ["khong_kiep_dong_cung"] and "ky_dong_cung" in d["breakers"]
    d = verdict(f, core, [S("Địa Không")], KY, TAM_HOA)                                         # Tam Hóa hội: covers both
    assert d["state"] == "pha_duoc_cuu" and d["rescuers"] == ["tam_hoa_hoi_cuu"]


def test_nhat_nguyet_ham_gap_sat_breaker_uses_rank_and_sat_count():
    f, core = "CACH_X_NHAT_NGUYET_TINH_MINH", CASES["CACH_X_NHAT_NGUYET_TINH_MINH"][1]
    ham = [("dig", "Thái Dương", "Mệnh", "hãm"), ("dig", "Thái Âm", "Quan Lộc", "miếu")]
    assert "nhat_nguyet_ham_gap_sat" not in verdict(f, core, ham)["breakers"]                    # hãm alone is a refutation, not a breaker
    d = verdict(f, core, ham, [S("Hỏa Tinh", "Tài Bạch")])
    assert d["state"] == "bi_pha" and "nhat_nguyet_ham_gap_sat" in d["breakers"]
    assert "nhat_nguyet_ham_gap_sat" not in verdict(f, core, [S("Hỏa Tinh", "Tài Bạch")], [("dig", "Thái Dương", "Mệnh", "miếu"), ("dig", "Thái Âm", "Quan Lộc", "miếu")])["breakers"]


def test_v2_aligned_with_cited_rules_kinh_or_ky_must_be_in_the_same_palace():
    """KL p.66 / TV_KL_STAR_MENH_TAM_KY_KY_KINH: the breaker is Kỵ OR Kình in the SAME palace as Mệnh, not Kỵ somewhere in the tam phương."""
    f, core = "CACH_X_TAM_KY_GIA_HOI", CASES["CACH_X_TAM_KY_GIA_HOI"][1]
    assert verdict(f, core, [H("Hóa Kỵ", "Quan Lộc")])["breakers"] == []                       # Kỵ in tam hợp: no longer a breaker
    assert verdict(f, core, [H("Hóa Kỵ")])["breakers"] == ["ky_hoac_kinh_dong_cung"]
    assert verdict(f, core, KINH)["breakers"] == ["ky_hoac_kinh_dong_cung"]                    # Kình Dương in Mệnh counts too


def test_v2_cndl_needs_all_four_stars_as_in_toan_thu_p24():
    f = "CACH_X_CO_NGUYET_DONG_LUONG"
    three = [S("Thiên Cơ"), S("Thái Âm", "Quan Lộc"), S("Thiên Đồng", "Tài Bạch")]
    assert verdict(f, three)["state"] == "khong_hien"
    assert verdict(f, three, [S("Thiên Lương", "Thiên Di")])["state"] == "hinh_thuc"            # the book: without cát tinh only "công chức bình thường"
    assert verdict(f, three, [S("Thiên Lương", "Thiên Di")], XK)["state"] == "thanh"


def test_v2_mddk_follows_kl_p64_khoa_quyen_loc_good_that_sat_bad():
    f, core = "CACH_X_MA_DAU_DOI_KIEM", CASES["CACH_X_MA_DAU_DOI_KIEM"][1]
    assert "khoa_quyen_loc_hoi" in verdict(f, core, [H("Hóa Lộc", "Tài Bạch")])["boosters"]
    assert "that_sat_trong_tam_phuong" in verdict(f, core, [S("Thất Sát", "Thiên Di")])["breakers"]
    assert verdict(f, core, [("dig", "Kình Dương", "Mệnh", "hãm")])["refutations"] == []        # Kình is hãm at Ngọ by table; that is the cách itself, not a refutation


def test_v2_ttan_booster_is_full_tam_hoa_as_in_kl_p58_tt_p34():
    f, core = "CACH_X_THACH_TRUNG_AN_NGOC", CASES["CACH_X_THACH_TRUNG_AN_NGOC"][1]
    assert verdict(f, core, [H("Hóa Lộc", "Quan Lộc"), H("Hóa Quyền", "Tài Bạch")])["boosters"] == []       # two of three is not enough
    assert verdict(f, core, TAM_HOA)["boosters"] == ["tam_hoa_hoi_du"]


def test_core_requires_enough_stars_count_operator():
    f = "CACH_X_SAT_PHA_LIEM_THAM"
    assert verdict(f, [S("Thất Sát"), S("Phá Quân", "Quan Lộc")])["state"] == "khong_hien"             # 2 of 4
    assert verdict(f, [S("Thất Sát"), S("Phá Quân", "Quan Lộc"), S("Liêm Trinh", "Thiên Di")])["state"] == "hinh_thuc"   # 3 of 4, xung chiếu counts
    assert verdict(f, [S("Thất Sát"), S("Phá Quân", "Quan Lộc"), S("Tham Lang", "Huynh Đệ")])["state"] == "khong_hien"  # giáp is NOT tam phương


def test_giap_is_distinguished_from_dong_cung_and_xung_chieu():
    f = "CACH_X_KHOI_VIET_GIAP_MENH"
    core = CASES[f][1]
    assert verdict(f, core)["state"] == "hinh_thuc"
    assert verdict(f, [S("Thiên Khôi", "Huynh Đệ"), S("Thiên Việt", "Thiên Di")])["state"] == "khong_hien"      # xung chiếu, not giáp
    assert verdict(f, [S("Thiên Khôi"), S("Thiên Việt", "Phụ Mẫu")])["state"] == "khong_hien"                   # đồng cung, not giáp
    assert verdict(f, [S("Thiên Việt", "Huynh Đệ"), S("Thiên Khôi", "Phụ Mẫu")])["state"] == "hinh_thuc"       # either side order


def test_position_specific_cores():
    assert verdict("CACH_X_NHAT_LE_TRUNG_THIEN", [S("Thái Dương")], menh="Tý")["state"] == "khong_hien"          # right star, wrong branch
    assert verdict("CACH_X_MA_DAU_DOI_KIEM", [S("Kình Dương")], menh="Tý")["state"] == "khong_hien"
    assert verdict("CACH_X_THACH_TRUNG_AN_NGOC", [S("Cự Môn")], menh="Ngọ")["state"] == "hinh_thuc"              # Tý OR Ngọ
    assert verdict("CACH_X_THACH_TRUNG_AN_NGOC", [S("Cự Môn")], menh="Dần")["state"] == "khong_hien"


def test_nhat_nguyet_brightness_uses_dignity_rank_and_unknown_is_reported():
    f, core = "CACH_X_NHAT_NGUYET_TINH_MINH", CASES["CACH_X_NHAT_NGUYET_TINH_MINH"][1]
    bright = [("dig", "Thái Dương", "Mệnh", "đắc"), ("dig", "Thái Âm", "Quan Lộc", "đắc")]
    assert verdict(f, core, bright)["boosters"] == ["nhat_nguyet_deu_sang"]
    dim = [("dig", "Thái Dương", "Mệnh", "đắc"), ("dig", "Thái Âm", "Quan Lộc", "bình")]
    assert verdict(f, core, dim)["boosters"] == []                                           # bình (rank 1) is not sáng
    d = verdict(f, core)                                                                       # no brightness data at all
    assert d["boosters"] == [] and "boosters:nhat_nguyet_deu_sang" in d["unknown"] and d["caveats"]
    hang = [("dig", "Thái Dương", "Mệnh", "hãm"), ("dig", "Thái Âm", "Quan Lộc", "miếu")]
    assert "Thái_Dương_ham" in verdict(f, core, hang, TA_HUU)["refutations"]


def test_tam_ky_booster_needs_hoa_in_own_palace():
    f = "CACH_X_TAM_KY_GIA_HOI"
    core = CASES[f][1]
    assert verdict(f, core)["boosters"] == []
    assert "hoa_o_ban_cung" in verdict(f, [H("Hóa Lộc"), H("Hóa Quyền", "Tài Bạch"), H("Hóa Khoa", "Thiên Di")])["boosters"]


def test_render_vi_is_labelled_experimental_and_never_predicts():
    f = BY_ID["CACH_X_TU_PHU_DONG_CUNG"]
    core = CASES[f.id][1]
    d = verdict(f.id, core, TA_HUU, XK, KINH)
    t = render_vi(f, d)
    assert "Tử Phủ đồng cung" in t and "thử nghiệm" in t and "không dự báo" in t
    d = verdict(f.id, core, TA_HUU, XK)
    t = render_vi(f, d)
    assert "thành cách, thế mạnh" in t and "Tả Phụ, Hữu Bật" in t


# ---- engine integration + multi-hop on the demo rules ---------------------------------------------------------------------
def run_full(ops, menh="Tý"):
    base = facts.tuvi_facts(synth(ops, menh))
    rules, srcs = load_all()
    allr, alls = rules + RULES, srcs + XSRC
    return engine.run(allr, alls, base, system="tu_vi", formations=FORMS), allr


TPVT = CASES["CACH_X_TU_PHU_VU_TUONG"]


def test_formation_result_feeds_ordinary_rules_two_hops():
    res, _ = run_full(TPVT[1] + TA_HUU)
    assert "CACH_X_TU_PHU_VU_TUONG" in res.derived["palace:Mệnh"]["derived.cach.formed"]
    assert res.derived["chart"]["derived.menh_co_cach_thanh"] is True                        # hop 1: rule reads the formation verdict
    f = [x for x in res.findings if x.claim == "xr_quan_loc_trong_tam_phuong_cach"]          # hop 2: rule reads hop 1 + Mệnh's tp via ref
    assert [x.subject for x in f] == ["palace:Quan Lộc"] and f[0].depth >= 3
    chain = " ".join(res.why(f[0].id)["chain"])
    assert "XR_MENH_CO_CACH_THANH" in chain and "XR_QUAN_LOC_TRONG_TAM_PHUONG_CACH" in chain


def test_no_formed_cach_means_downstream_rule_does_not_fire():
    res, _ = run_full(TPVT[1] + KINH)                                                          # TPVT broken, none formed
    assert res.derived["palace:Mệnh"]["derived.cach.formed"] == [] and "CACH_X_TU_PHU_VU_TUONG" in res.derived["palace:Mệnh"]["derived.cach.broken"]
    assert "derived.menh_co_cach_thanh" not in res.derived["chart"]
    assert not [x for x in res.findings if x.claim.startswith("xr_")]


def test_exception_on_demo_rule_blocks_it_and_leaves_audit_trail():
    res, _ = run_full(TPVT[1] + TA_HUU + [("triet", "Quan Lộc")])
    assert not [x for x in res.findings if x.claim == "xr_quan_loc_trong_tam_phuong_cach"]
    assert any(b["rule"] == "XR_QUAN_LOC_TRONG_TAM_PHUONG_CACH" and b["subject"] == "palace:Quan Lộc" for b in res.blocked)


def test_declared_conflict_between_demo_rules_is_surfaced_not_resolved():
    res, allr = run_full(TPVT[1] + TA_HUU + [H("Hóa Kỵ", "Quan Lộc")])
    claims = {x.claim: x for x in res.findings}
    assert "xr_quan_loc_trong_tam_phuong_cach" in claims and "xr_quan_loc_ky_han_che" in claims
    rep = [r for r in conflict.resolve(res, allr) if r.get("declared")]
    assert len(rep) == 1 and rep[0]["status"] == "unresolved"
    assert claims["xr_quan_loc_ky_han_che"].status == claims["xr_quan_loc_trong_tam_phuong_cach"].status == "unresolved"


def test_formation_findings_carry_evidence_edges_for_why():
    res, _ = run_full(TPVT[1] + TA_HUU + KINH)
    f = next(x for x in res.findings if x.rule_id == "CACH_X_TU_PHU_VU_TUONG")
    assert f.claim == "cach:CACH_X_TU_PHU_VU_TUONG:bi_pha" and f.effect == "limit"
    why = res.why(f.id)
    assert any("sát tinh" in x for x in why["opposed_by"])                                      # the breaker is listed as opposing


def test_engine_deterministic_with_formations():
    a, _ = run_full(TPVT[1] + TA_HUU)
    b, _ = run_full(TPVT[1] + TA_HUU)
    assert [(f.id, f.claim, f.depth) for f in a.findings] == [(f.id, f.claim, f.depth) for f in b.findings]
    assert a.formations == b.formations


# ---- production isolation ----------------------------------------------------------------------------------------------------
def test_experimental_never_in_production_packs():
    rules, sources = load_all()
    ids = {r.id for r in rules}
    assert not ids & ({r.id for r in RULES} | set(BY_ID))
    assert "SRC_EXPERIMENTAL" not in {s.id for s in sources}
    assert all(r.schoolId != "experimental_draft" for r in rules)
    assert validate_pack(RULES, XSRC, KNOWN) == []


def test_experimental_never_marked_verified():
    assert all(r.reviewStatus == "draft" for r in RULES) and all(f.reviewStatus == "draft" for f in FORMS)
    assert all(not s.verified for s in XSRC)


def test_user_facing_text_never_shows_internal_ids():
    f = BY_ID["CACH_X_NHAT_NGUYET_TINH_MINH"]
    d = verdict(f.id, CASES[f.id][1])                    # no brightness data -> an unknown booster
    assert "boosters:nhat_nguyet_deu_sang" in d["unknown"]          # machine-readable id kept for tools
    t = render_vi(f, d)
    assert "boosters:" not in t and "nhat_nguyet" not in t and "đều sáng" in t
