"""Phase 2: van_han.read is now DATA-driven (data/van_han_rules.json). It must give EXACTLY the output of the frozen if/else version."""
import random

import pytest

from legacy_van_han import read as legacy_read
from phase1_helpers import synth
from tvbt import tuvi, van_han
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import BRANCHES_VI
from tvbt.knowledge.dsl import RuleError, validate

MAJORS = list(tuvi.MAJOR_NAMES)
AUX = ["Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt", "Tả Phụ",
       "Hữu Bật", "Lộc Tồn", "Đào Hoa", "Hồng Loan", "Thiên Hỷ", "Thái Tuế", "Quan Phù", "Bạch Hổ", "Tấu Thư", "Phi Liêm"]
HOAS = ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"]


def random_chart(rng):
    ops = []
    names = [p["name"] for p in synth().palaces]
    for n in names:
        for s in rng.sample(MAJORS, rng.choice([0, 0, 1, 1, 2, 3])):
            ops.append(("star", s, n))
        for s in rng.sample(AUX, rng.choice([0, 1, 2, 3, 5])):
            ops.append(("star", s, n))
        if rng.random() < 0.15:
            ops.append((rng.choice(["tuan", "triet"]), n))
    for h in HOAS:
        if rng.random() < 0.9:
            ops.append(("hoa", h, rng.choice(names)))
    return synth(ops, rng.choice(BRANCHES_VI))


def test_rules_file_is_valid_and_has_unique_ids():
    rs = van_han.rules()
    assert len({r["id"] for r in rs}) == len(rs) == 28
    assert {r["src"] for r in rs} == {"SRC", "SRC_TH"}
    with pytest.raises(RuleError):
        validate({"fact": "palace.x", "operator": "eq", "value": 1}, {"vh.*"})        # rules may only read vh.* facts


def test_differential_random_charts_all_palaces():
    rng = random.Random(20261017)
    fired = set()
    for _ in range(400):
        tv = random_chart(rng)
        for p in tv.palaces:
            new, old = van_han.read(tv, p["name"]), legacy_read(tv, p["name"])
            assert new == old, (p["name"], new, old)
            fired |= {o["rule_id"] for o in van_han.read_traced(tv, p["name"])}
    assert len(fired - {None}) >= 25, f"random charts exercised too few rules: {sorted(fired - {None})}"          # nearly every rule is compared at least once


@pytest.mark.parametrize("b", [(1990, 5, 17, 10, 30, "male"), (1975, 11, 3, 23, 5, "female"), (2001, 8, 28, 14, 0, "male"), (1958, 2, 4, 6, 0, "female")])
def test_differential_real_charts(b):
    tv = tuvi.compute(normalize(BirthInput(*b[:5], "Asia/Ho_Chi_Minh", b[5])))
    for p in tv.palaces:
        assert van_han.read(tv, p["name"]) == legacy_read(tv, p["name"])


def test_real_scan_matches_legacy():
    n = 0
    for y in range(1950, 2011, 6):
        for m in (2, 5, 8, 11):
            for h in (0, 6, 12, 18):
                tv = tuvi.compute(normalize(BirthInput(y, m, 9, h, 10, "Asia/Ho_Chi_Minh", "male")))
                for p in tv.palaces:
                    assert van_han.read(tv, p["name"]) == legacy_read(tv, p["name"])
                    n += 1
    assert n > 1000


def test_public_output_shape_unchanged_no_extra_keys():
    tv = random_chart(random.Random(1))
    for p in tv.palaces:
        for o in van_han.read(tv, p["name"]):
            assert set(o) == {"text", "src"}


def test_traced_output_names_the_rule_behind_each_sentence():
    tv = synth([("star", "Vũ Khúc", "Mệnh"), ("star", "Thiên Tướng", "Mệnh"), ("star", "Tử Vi", "Quan Lộc")])
    t = van_han.read_traced(tv, "Quan Lộc")
    assert [o["rule_id"] for o in t] == ["VH_VT_TP"] or "VH_VT_TP" in [o["rule_id"] for o in t]


S = lambda s, n: ("star", s, n)      # noqa: E731


@pytest.mark.parametrize("rule_id,ops", [
    ("VH_CU_NHAT_SPT", [S("Cự Môn", "Mệnh"), S("Thái Dương", "Mệnh"), S("Thất Sát", "Quan Lộc")]),
    ("TH_CU_NHAT_SONG_LOC", [S("Cự Môn", "Quan Lộc"), S("Thái Dương", "Quan Lộc"), S("Lộc Tồn", "Quan Lộc"), S("Tả Phụ", "Quan Lộc"),
                             ("hoa", "Hóa Lộc", "Quan Lộc")]),
    ("TH_CNDL_TAM_HOA", [S("Thiên Cơ", "Quan Lộc"), S("Văn Xương", "Quan Lộc"), S("Hồng Loan", "Quan Lộc"), ("hoa", "Hóa Lộc", "Quan Lộc"),
                         ("hoa", "Hóa Quyền", "Quan Lộc"), ("hoa", "Hóa Khoa", "Quan Lộc")]),
])
def test_rules_the_random_charts_rarely_reach_match_legacy(rule_id, ops):
    tv = synth(ops)
    assert rule_id in [o["rule_id"] for o in van_han.read_traced(tv, "Quan Lộc")]
    assert van_han.read(tv, "Quan Lộc") == legacy_read(tv, "Quan Lộc")
    # remove one required ingredient -> the rule must not fire, again identical to legacy
    tv2 = synth(ops[:-1] if ops[-1][0] == "hoa" else ops[:-1])
    assert rule_id not in [o["rule_id"] for o in van_han.read_traced(tv2, "Quan Lộc")]
    assert van_han.read(tv2, "Quan Lộc") == legacy_read(tv2, "Quan Lộc")
