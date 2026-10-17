"""Real-API integration for the 八字真宗 直断 rules (no monkeypatching): opt-in flag, verified/experimental split, provenance, trace, edge cases, and that the
other Bát Tự methods and endpoints are untouched."""
import json
import random

import pytest
from fastapi.testclient import TestClient

from tvbt import api, bazi, calendar_core as cc
from tvbt.knowledge.loader import load_all
from tvbt.reasoning import facts

client = TestClient(api.app)
RULES, SOURCES = load_all()
ZZ = {r.id: r for r in RULES if r.id.startswith("BT_ZZ_DIRECT_")}
ZZ_CLAIMS = {c["claim"]: r for r in ZZ.values() for c in r.consequences}
BODY = {"year": 1990, "month": 5, "day": 17, "hour": 8, "minute": 0, "tz": "Asia/Ho_Chi_Minh", "gender": "male"}


def post(path, **extra):
    r = client.post(path, json={**BODY, **extra})
    assert r.status_code == 200, r.text
    return r.json()


def bt(js):
    return js["systems"]["bat_tu"]


def test_default_response_is_unchanged_and_has_no_zz_content():
    js = post("/api/reasoning")
    assert set(bt(js)) == {"findings", "pending", "blocked", "conflicts", "text"}
    assert not any(f["rule_id"].startswith("BT_ZZ_DIRECT_") for f in bt(js)["findings"])
    assert js["pack_problems"] == []
    assert not any(c in bt(js)["text"] for c in ZZ_CLAIMS)
    on = post("/api/reasoning", bat_tu_direct=False)
    assert on == js


def test_tu_vi_block_identical_with_and_without_the_flag():
    a, b = post("/api/reasoning"), post("/api/reasoning", bat_tu_direct=True)
    assert a["systems"]["tu_vi"] == b["systems"]["tu_vi"]


def test_flag_adds_verified_findings_and_separates_experimental_ones():
    js = post("/api/reasoning", bat_tu_direct=True)
    s = bt(js)
    ver = [f for f in s["findings"] if f["rule_id"].startswith("BT_ZZ_DIRECT_")]
    exp = s["experimental_findings"]
    assert ver and exp and s["direct_summary"]["verified"] == len(ver) and s["direct_summary"]["experimental"] == len(exp)
    for f in ver:
        assert ZZ[f["rule_id"]].reviewStatus == "verified" and f["basis"] == "verified"
    for f in exp:
        assert ZZ[f["rule_id"]].reviewStatus == "draft" and f["experimental"] is True and f["label"].startswith("Thử nghiệm")
        assert f["basis"] != "verified" and f["why"] and f["why"].get("chain")
    assert not {f["rule_id"] for f in exp} & {f["rule_id"] for f in s["findings"]}          # draft findings never appear in the public list
    claims_vi = json.loads((api.ROOT / "data" / "claims_vi.json").read_text("utf-8"))
    draft_phrases = [claims_vi[c["claim"]].split(": ", 1)[1].split(" (")[0] for r in ZZ.values() if r.reviewStatus == "draft" for c in r.consequences]
    assert draft_phrases and not any(p in s["text"] for p in draft_phrases)             # draft wording never reaches the public text
    # provenance and trace on every verified zz finding
    for f in ver:
        assert f["why"] and f["why"].get("chain")
        assert any("SRC_BAZI_ZHENZONG" in c for c in f["why"]["chain"])


def test_vietnamese_wording_is_hedged_and_never_absolute():
    claims = json.loads((api.ROOT / "data" / "claims_vi.json").read_text("utf-8"))
    banned = ("chắc chắn", "nhất định", "tất yếu", "sẽ chết", "đoản mệnh", "tuyệt đối")
    for c in ZZ_CLAIMS:
        text = claims[c]
        assert text.startswith(("khuynh hướng theo sách:", "hạn chế theo sách:")), text
        assert not any(w in text.lower() for w in banned), text
    js = post("/api/reasoning", bat_tu_direct=True)
    for f in bt(js)["findings"] + bt(js)["experimental_findings"]:
        if f["rule_id"].startswith("BT_ZZ_DIRECT_"):
            assert "theo sách" in claims[f["claim"]]


def pick(pred, n=3000, seed=4):
    rnd = random.Random(seed)
    for _ in range(n):
        y, m, d, h = rnd.randint(1925, 2035), rnd.randint(1, 12), rnd.randint(1, 28), rnd.randint(0, 23)
        g = rnd.choice(["male", "female"])
        if y > 2049:
            continue
        bz = bazi.compute(cc.normalize(cc.BirthInput(y, m, d, h, 0, "Asia/Ho_Chi_Minh", g)))
        f = facts.bazi_facts(bz, zz=True)["chart"]
        if pred(f):
            return {"year": y, "month": m, "day": d, "hour": h, "gender": g}, f
    raise AssertionError("no chart found")


def claims_of(body):
    js = post("/api/reasoning", **body, bat_tu_direct=True)
    s = bt(js)
    return {f["claim"] for f in s["findings"]}, {f["claim"] for f in s["experimental_findings"]}


@pytest.mark.parametrize("fact,claim", [
    ("bazi.ren_in_tmm", "bt_zz_nhan_thai_than_menh_ich_ky"), ("bazi.ren_combined", "bt_zz_nhan_hop_kheo_nhieu_lao"),
    ("bazi.ma_in_chart", "bt_zz_ma_trong_menh_hieu_dong"), ("bazi.ma_in_hour", "bt_zz_ma_o_gio_than_khong_yen"),
    ("bazi.ma_void", "bt_zz_ma_khong_vong_kem_thanh_tuu"), ("bazi.ma_clashed", "bt_zz_ma_gap_xung_khong_nhan_ha"),
    ("bazi.ma_combined", "bt_zz_ma_gap_hop_phat_muon"), ("bazi.wen_chang_in_chart", "bt_zz_van_xuong_co_trong_menh_hoc_hanh"),
    ("bazi.month_branch_hurt", "bt_zz_hn_nguyet_lenh_hinh_xung"), ("bazi.day_branch_hurt", "bt_zz_hn_nhat_chi_hinh_xung")])
def test_edge_charts_produce_the_expected_claim_in_the_right_bucket(fact, claim):
    body, f = pick(lambda f: f[fact] is True)
    ver, exp = claims_of(body)
    assert claim in (ver | exp)
    # the bucket follows the rule's review status, never the other way round
    assert (claim in ver) == (ZZ_CLAIMS[claim].reviewStatus == "verified")
    body2, _ = pick(lambda f: f[fact] is False)
    assert claim not in (set().union(*claims_of(body2)))


def test_blade_count_and_lu_edge_and_three_branch_penalty_charts():
    body, f = pick(lambda f: f["bazi.ren_count"] >= 2)
    ver, exp = claims_of(body)
    assert "bt_zz_nhan_nhieu_gia_dinh_bat_loi" in ver | exp
    body, f = pick(lambda f: f["bazi.ren_count"] == 0)
    assert "bt_zz_nhan_nhieu_gia_dinh_bat_loi" not in set().union(*claims_of(body))
    # a chart with a three-branch penalty (no 'pillars' key in its relation entry) must not crash the endpoint
    def tri(f):
        return False
    rnd = random.Random(6)
    found = False
    for _ in range(4000):
        b = {"year": rnd.randint(1925, 2035), "month": rnd.randint(1, 12), "day": rnd.randint(1, 28), "hour": rnd.randint(0, 23), "gender": "male"}
        bz = bazi.compute(cc.normalize(cc.BirthInput(b["year"], b["month"], b["day"], b["hour"], 0, "Asia/Ho_Chi_Minh", "male")))
        if any("pillars" not in r for r in bz.relations["branch_penalty"]):
            post("/api/reasoning", **b, bat_tu_direct=True)
            found = True
            break
    assert found


def test_gender_input_is_used_and_the_character_rules_are_gender_scoped():
    body, f = pick(lambda f: f["bazi.all_yin"] is True and f["chart.gender"] == "nam", n=8000)
    assert f["chart.gender_source"] == "input"
    ver, exp = claims_of(body)
    assert "bt_zz_nam_thuan_am_mem_yeu" in exp and "bt_zz_nam_thuan_am_mem_yeu" not in ver          # draft -> experimental bucket only
    body2 = {**body, "gender": "female"}
    assert "bt_zz_nam_thuan_am_mem_yeu" not in set().union(*claims_of(body2))


def test_other_methods_and_endpoints_are_unaffected_by_the_flag():
    for path in ("/api/bazi-structure", "/api/year", "/api/analysis", "/api/chart"):
        a, b = post(path), post(path, bat_tu_direct=True)
        assert a == b, path
    other = {**BODY, "year": 1985}
    r1 = client.post("/api/compare-charts", json={"a": BODY, "b": other})
    r2 = client.post("/api/compare-charts", json={"a": {**BODY, "bat_tu_direct": True}, "b": {**other, "bat_tu_direct": True}})
    assert r1.status_code == r2.status_code == 200 and r1.json() == r2.json()


def test_rules_test_endpoint_dry_runs_zz_rules_on_the_zz_facts():
    rule = {"id": "BT_ZZ_DIRECT_PROBE", "system": "bat_tu", "schoolId": "x", "category": "probe", "description": "probe [PDF p.57]",
            "conditions": {"fact": "bazi.hour_stem_group", "value": "thuc_thuong"},
            "consequences": [{"kind": "finding", "claim": "bt_zz_probe", "effect": "neutral", "scope": "natal"}],
            "exceptions": [], "conflictsWith": [], "priority": 1, "sourceIds": ["SRC_BAZI_ZHENZONG"], "reviewStatus": "draft", "version": "0", "subject": "chart"}
    r = client.post("/api/rules/test", json={"rule": rule, "birth": BODY})
    assert r.status_code == 200 and r.json()["valid"] and r.json()["fired_on"] == ["chart"]


def test_vietnamese_sentences_name_the_book_and_stay_hedged():
    js = post("/api/reasoning", bat_tu_direct=True)
    lines = [l for l in bt(js)["text"].split("\n") if "八字真宗" in l]
    assert lines
    for l in lines:
        assert l.startswith(("Theo 八字真宗, lá số có xu hướng", "Theo 八字真宗, lá số có thể gặp hạn chế:", "Chưa thể khẳng định rằng, theo 八字真宗"))
        assert not any(w in l.lower() for w in ("chắc chắn", "nhất định", "sẽ ", "tuyệt đối", "một dấu hiệu liên quan đến khuynh hướng"))
    # the old template is untouched for every other claim
    assert any(l.startswith("Có thể nhận thấy một dấu hiệu") for l in bt(js)["text"].split("\n"))


def test_every_rule_has_source_status_and_a_page_and_verified_means_condition_matches_source_only():
    for r in ZZ.values():
        assert r.sourceIds == ["SRC_BAZI_ZHENZONG"] and "[PDF p." in r.description and r.reviewStatus in ("verified", "draft")
    js = post("/api/reasoning", bat_tu_direct=True)
    assert "không thuộc luận giải chính thức" in bt(js)["direct_summary"]["note"] and "xu hướng" in bt(js)["direct_summary"]["note"]
    drafts = {r.id for r in ZZ.values() if r.reviewStatus == "draft"}
    assert {"BT_ZZ_DIRECT_M_HURT", "BT_ZZ_DIRECT_D_HURT", "BT_ZZ_DIRECT_S_PURE_YIN_M"} <= drafts


def test_phi_hoa_and_other_registered_routes_unaffected_by_the_flag():
    a, b = post("/api/phi-hoa"), post("/api/phi-hoa", bat_tu_direct=True)
    assert a == b
    a, b = post("/api/bazi-timeline", to_year=2030), post("/api/bazi-timeline", to_year=2030, bat_tu_direct=True)
    assert a == b
    assert post("/api/reasoning", experimental=True)["experimental"] == post("/api/reasoning", experimental=True, bat_tu_direct=True)["experimental"]
