"""Độ trung thành với mệnh lệ trong Trích Thiên Tủy (Nhậm Thiết Tiều). Các con số dưới đây là SÀN hồi quy của kết quả đo được, không phải
mục tiêu đã tinh chỉnh theo sách: chúng đo hệ thống đồng ý với nhãn của chính sách tới đâu, không chứng minh tiên đoán đúng."""
import json
from pathlib import Path

import pytest

from tvbt.bazi_deep import pipeline
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DEFAULT, TVH_40

CASES = json.loads((Path(__file__).parent / "golden/ttt_cases.json").read_text("utf-8"))["cases"]
_cache = {}


def run(n, profile):
    key = (n, profile.id)
    if key not in _cache:
        _cache[key] = pipeline.analyse(ChartView.from_names(CASES[str(n)]["pillars"]), profile, with_rules=False)
    return _cache[key]


def of(kind):
    return {int(k): v for k, v in CASES.items() if v["kind"] == kind}


def test_every_book_chart_parses_and_has_a_label():
    assert len(CASES) >= 80
    for k, v in CASES.items():
        ChartView.from_names(v["pillars"])
        assert v["label"] and v["page"]


def dm_agreement(profile):
    ok = tot = 0
    for kind in ("tong", "thuong_quan"):
        for n, c in of(kind).items():
            S = run(n, profile)["strength_after"]
            strong = S["level_index"] >= 4 if S["level_index"] != 3 else None
            tot += 1
            ok += strong is not None and strong == (c["dm"] == "strong")
    return ok, tot


def test_day_master_strength_tvh_method_agrees_with_the_book_labels_more_than_the_system_weights():
    ok_tvh, tot = dm_agreement(TVH_40)
    ok_sys, _ = dm_agreement(DEFAULT)
    assert tot == 48
    assert ok_tvh >= 44                      # measured 45/48 (94%)
    assert ok_sys >= 34                      # measured 36/48 (75%)
    assert ok_tvh > ok_sys


def test_tong_family_detection_floor_and_exact_labels():
    for prof in (DEFAULT, TVH_40):
        fam = exact = 0
        for n, c in of("tong").items():
            outs = [o["name"] for o in run(n, prof)["geju"]["outer"]]
            fam += bool(outs)
            exact += c["label"] in outs
        assert fam >= 17 and exact >= 9, (prof.id, fam, exact)             # measured 18/27 and 10/27


def test_tong_detection_has_few_false_alarms_on_cases_the_book_calls_something_else():
    non = [n for n, c in CASES.items() if c["kind"] in ("sat", "thuong_quan")]
    fp = sum(bool(run(int(n), TVH_40)["geju"]["outer"]) for n in non)
    assert fp <= 12 and len(non) == 50                                   # measured 10/50: mostly 'giả' Tòng Nhi on Thương Quan charts


def test_sat_structures_recognised_like_the_book():
    def hits(label, ids):
        ns = [n for n, c in of("sat").items() if c["label"] == label]
        ok = sum(any(p["id"] in ids and p["state"] != "co_ten_khong_ke" for p in run(n, DEFAULT)["patterns"]) for n in ns)
        return ok, len(ns)
    assert hits("hop_quan_luu_sat", {"hop_sat_luu_quan", "hop_quan_luu_sat"}) == (8, 9)
    assert hits("hon_tap", {"quan_sat_hon_tap"}) == (4, 4)
    assert hits("che_sat_qua_muc", {"che_sat_qua_muc"})[0] >= 4
    assert hits("thuc_che_sat", {"thuc_che_sat"})[0] >= 1                # needs adjacency; the book also counts hidden chế: known gap


def test_hon_tap_is_not_a_problem_in_the_books_own_four_charts():
    """PDF pp.90-91: in cases 151-154 the day master sits on Ấn or is helped by the hour pillar, so the book calls them 'phú quý nhiều'."""
    for n in (151, 152, 153, 154):
        p = next(p for p in run(n, TVH_40)["patterns"] if p["id"] == "quan_sat_hon_tap")
        assert p["state"] == "hon_tap_khong_ngai" and p["hon_tap_support"], (n, p["state"])


def test_han_noan_reproduces_the_four_labelled_cases():
    for n, c in of("han_noan").items():
        d = run(n, TVH_40)["yongshen"]["methods"]["dieu_hau"]["han_noan"]["direction"]
        assert d == c["label"], (n, d, c["label"])


def test_thuong_quan_style_floor():
    ok = sum((run(n, TVH_40)["yongshen"]["thuong_quan"] or {}).get("style") == c["label"] for n, c in of("thuong_quan").items())
    assert ok >= 8                            # measured 9/21: the book's own choice among the five styles is a judgement, only partly reproducible


def test_nguyen_luu_runs_on_every_book_chart():
    for n in CASES:
        nl = run(int(n), TVH_40)["nguyen_luu"]
        assert nl["verdict"] in ("hi", "ky", "khong_ket_luan") and nl["path"]
