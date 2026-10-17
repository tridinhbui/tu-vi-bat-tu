import json

import pytest

from bazi_deep_util import EX, SAVED, TAI_AN, THUC_SAT, view
from tvbt.bazi_deep import geju, interact, patterns, strength
from tvbt.bazi_deep.profile import DEFAULT


def P(v, profile=DEFAULT):
    R = interact.resolve(v, profile)
    S = strength.compute(v, profile, R)
    return {p["id"]: p for p in patterns.evaluate_all(geju.Ctx(v, profile, R, S))}


def test_defs_are_draft_and_every_predicate_parses():
    d = json.loads((patterns.DATA / "patterns_defs.json").read_text("utf-8"))
    assert d["_status"] == "draft"
    v = view("EX1"); R = interact.resolve(v); S = strength.compute(v, DEFAULT, R); ctx = geju.Ctx(v, DEFAULT, R, S)
    for pid, c in d["defs"].items():
        assert c["polarity"] in ("cat", "benh")
        for e in c["formed"] + c["weak"] + list(c["bai"].values()) + [x for l in c["cuu"].values() for x in l]:
            geju.pred(ctx, e)
        if c["polarity"] == "cat":
            assert set(c["cuu"]) == set(c["bai"]), pid


def test_sat_an_tuong_sinh_forms_only_when_the_chain_touches_the_day_master():
    p = P(view("EX11"))["sat_an_tuong_sinh"]          # Tân (Sát) -> Nhâm (Ấn) -> Ất, three adjacent steps
    assert p["state"] == "thanh" and p["polarity"] == "cat"


def test_thuc_che_sat_needs_adjacency_otherwise_it_only_has_a_name():
    assert P(view(THUC_SAT))["thuc_che_sat"]["state"] == "thanh"
    assert P(view("EX1"))["thuc_che_sat"]["state"] == "co_ten_khong_ke"        # Bính (month) and Canh (hour) are separated by the day stem


def test_tai_pha_an_is_a_disease_with_only_a_weak_rescue():
    p = P(view(TAI_AN))["tai_pha_an"]
    assert p["polarity"] == "benh" and p["state"] in ("co_benh_cuu_yeu", "co_benh_co_cuu", "co_benh")
    assert p["state"] == "co_benh_cuu_yeu" and p["saved_by"].startswith("any:")        # Giáp is only hidden (Hợi, Dần)


def test_thuong_kien_quan_rescue_strength_distinguishes_visible_from_hidden():
    assert P(view("EX3"))["thuong_kien_quan"]["state"] == "co_benh_cuu_yeu"            # Quý only hidden in Tý
    assert P(view(SAVED))["thuong_kien_quan"]["state"] == "co_benh_co_cuu"             # Quý on the stems


def test_kieu_doat_thuc_in_ex6():
    assert P(view("EX6"))["kieu_doat_thuc"]["state"] == "co_benh_cuu_yeu"              # Mậu (Kiêu) kề Nhâm (Thực); Tài only hidden


def test_hop_quan_luu_sat_when_the_quan_is_bound():
    for k in ("EX4", "EX7"):
        assert P(view(k))["hop_quan_luu_sat"]["state"] == "thanh"
    assert "hop_quan_luu_sat" not in P(view("EX1"))


def test_quan_sat_hon_tap_is_reported_with_its_rescue():
    p = P(view("EX4"))["quan_sat_hon_tap"]
    assert p["polarity"] == "benh" and p["state"].startswith("co_benh_")


def test_thuong_phoi_an_requires_a_weak_enough_day_master():
    assert P(view("EX12"))["thuong_phoi_an"]["state"] == "thanh"
    assert P(view("EX13")).get("thuong_phoi_an") is None


def test_hidden_only_pairs_do_not_create_noise():
    assert P(view("EX13")) == {} or all(p["state"] != "thanh" for p in P(view("EX13")).values())
    assert all(p["evidence"] for p in P(view("EX2")).values())


def test_patterns_are_deterministic_on_all_examples():
    for k in EX:
        assert P(view(k)) == P(view(k))
