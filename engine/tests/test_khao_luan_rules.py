"""Rule behaviour on hand-built facts (expected results follow the cited book text, not our chart engine)."""
from tvbt.knowledge.loader import load_all
from tvbt.knowledge.schema import validate_pack
from tvbt.reasoning import conflict, engine

RULES, SOURCES = load_all()
F = {"palace.*", "chart.*", "bazi.*", "derived.*"}


def palace(name="Mệnh", branch="Thìn", own=(), tam=(), tp_stars=(), hoa=()):
    return {"palace.name": name, "palace.branch": branch, "palace.own_major_stars": list(own),
            "palace.tam_phuong_majors": list(tam) or list(own), "palace.tam_phuong_stars": list(tp_stars) or list(own),
            "palace.tam_phuong_tu_hoa": list(hoa), "palace.own_stars": list(own)}


def run(p):
    base = {"chart": {"chart.system": "tu_vi"}, "palace:" + p["palace.name"]: p}
    res = engine.run(RULES, SOURCES, base, system="tu_vi")
    return res, {f.claim for f in res.findings}


def test_pack_valid_and_verified_rules_cite_verified_sources():
    assert validate_pack(RULES, SOURCES, F) == []
    verified = [r for r in RULES if r.reviewStatus == "verified"]
    assert len(verified) >= 8 and all(s.verified for r in verified for s in SOURCES if s.id in r.sourceIds)


def test_group_classification_multi_hop_p166():
    res, claims = run(palace(own=["Tử Vi", "Thiên Tướng"], branch="Ngọ"))
    assert "menh_nhom_tu_phu_vu_tuong" in claims and "menh_nhom_sat_pha_liem_tham" not in claims
    f = next(f for f in res.findings if f.claim == "menh_nhom_tu_phu_vu_tuong")
    assert f.depth == 2 and f.basis == "verified"            # group assertion first, finding second (multi-hop)
    why = res.why(f.id)["chain"]
    assert any("TV_KL_GROUP_TU_PHU_VU_TUONG" in c for c in why) and any("SRC_KHAO_LUAN (verified)" in c for c in why)


def test_co_luong_thin_tuat_p51():
    _, c = run(palace(branch="Thìn", own=["Thiên Cơ", "Thiên Lương"]))
    assert "nhan_tu_thich_tu_hanh" in c and "thich_ban_luan_muu_tri" not in c   # ban luan only at Tuất
    _, c = run(palace(branch="Tuất", own=["Thiên Cơ", "Thiên Lương"]))
    assert {"nhan_tu_thich_tu_hanh", "thich_ban_luan_muu_tri"} <= c
    _, c = run(palace(branch="Tý", own=["Thiên Cơ", "Thiên Lương"]))
    assert "nhan_tu_thich_tu_hanh" not in c


def test_only_menh_palace_triggers_menh_rules():
    _, c = run(palace(name="Tài Bạch", branch="Tuất", own=["Thiên Cơ", "Thiên Lương"]))
    assert not c & {"nhan_tu_thich_tu_hanh", "thich_ban_luan_muu_tri", "menh_nhom_co_nguyet_dong_luong"}


def test_cndl_all_four_required():
    _, c = run(palace(branch="Sửu", own=["Thiên Đồng"], tam=["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"]))
    assert "huong_cong_chuc" in c
    _, c = run(palace(branch="Sửu", own=["Thiên Đồng"], tam=["Thiên Cơ", "Thái Âm", "Thiên Đồng"]))
    assert "huong_cong_chuc" not in c


def test_tu_vi_support_vs_limit_unresolved_and_draft_marked():
    p = palace(branch="Ngọ", own=["Tử Vi"], hoa=["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"], tp_stars=["Tử Vi", "Địa Kiếp"])
    res, c = run(p)
    rep = [r for r in conflict.resolve(res, RULES) if r["claim"] == "tu_vi_thanh_cach"][0]
    assert rep["supporting"] == ["TV_KL_TU_VI_TAM_HOA"] and rep["opposing"] == ["TV_KL_TU_VI_SAT_PHA"]
    assert rep["status"] == "unresolved" and "draft" in rep["basis"]   # limit rule is draft -> no silent winner
    # without the sát: plain support, verified
    res2, c2 = run(palace(branch="Ngọ", own=["Tử Vi"], hoa=["Hóa Khoa", "Hóa Quyền", "Hóa Lộc"]))
    rep2 = [r for r in conflict.resolve(res2, RULES) if r["claim"] == "tu_vi_thanh_cach"][0]
    assert rep2["status"] == "supported" and rep2["basis"] == "verified"


def test_missing_tam_hoa_is_not_support():
    _, c = run(palace(branch="Ngọ", own=["Tử Vi"], hoa=["Hóa Khoa", "Hóa Lộc"]))
    assert "tu_vi_thanh_cach" not in c
