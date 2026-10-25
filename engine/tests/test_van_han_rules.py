"""Phase 2: van_han.read is now DATA-driven (data/van_han_rules.json). It must give EXACTLY the output of the frozen if/else version."""
import dataclasses
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
# rules added after the move to data (TH pp.115-117, 2026-10-24) follow the 28 carried-over ones: the frozen version has no counterpart,
# so the differential leaves them out
NEW = {r["id"] for r in van_han.rules()[28:]}


def old_rules_read(tv, palace):
    return [{"text": o["text"], "src": o["src"]} for o in van_han.read_traced(tv, palace) if o["rule_id"] not in NEW]


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
    assert len({r["id"] for r in rs}) == len(rs) == 28 + len(NEW)
    assert {r["src"] for r in rs} == {"SRC", "SRC_TH"}
    with pytest.raises(RuleError):
        validate({"fact": "palace.x", "operator": "eq", "value": 1}, {"vh.*"})        # rules may only read vh.* facts


def test_differential_random_charts_all_palaces():
    rng = random.Random(20261017)
    fired = set()
    for _ in range(400):
        tv = random_chart(rng)
        for p in tv.palaces:
            new, old = old_rules_read(tv, p["name"]), legacy_read(tv, p["name"])
            assert new == old, (p["name"], new, old)
            fired |= {o["rule_id"] for o in van_han.read_traced(tv, p["name"])}
    assert len(fired - {None}) >= 25, f"random charts exercised too few rules: {sorted(fired - {None})}"          # nearly every rule is compared at least once


@pytest.mark.parametrize("b", [(1990, 5, 17, 10, 30, "male"), (1975, 11, 3, 23, 5, "female"), (2001, 8, 28, 14, 0, "male"), (1958, 2, 4, 6, 0, "female")])
def test_differential_real_charts(b):
    tv = tuvi.compute(normalize(BirthInput(*b[:5], "Asia/Ho_Chi_Minh", b[5])))
    for p in tv.palaces:
        assert old_rules_read(tv, p["name"]) == legacy_read(tv, p["name"])


def test_real_scan_matches_legacy():
    n = 0
    for y in range(1950, 2011, 6):
        for m in (2, 5, 8, 11):
            for h in (0, 6, 12, 18):
                tv = tuvi.compute(normalize(BirthInput(y, m, 9, h, 10, "Asia/Ho_Chi_Minh", "male")))
                for p in tv.palaces:
                    assert old_rules_read(tv, p["name"]) == legacy_read(tv, p["name"])
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
    assert old_rules_read(tv, "Quan Lộc") == legacy_read(tv, "Quan Lộc")
    # remove one required ingredient -> the rule must not fire, again identical to legacy
    tv2 = synth(ops[:-1] if ops[-1][0] == "hoa" else ops[:-1])
    assert rule_id not in [o["rule_id"] for o in van_han.read_traced(tv2, "Quan Lộc")]
    assert old_rules_read(tv2, "Quan Lộc") == legacy_read(tv2, "Quan Lộc")


def _at(tv, branch):
    return next(p["name"] for p in tv.palaces if p["branch"] == branch)


def _fires(rule_id, tv, palace):
    return rule_id in [o["rule_id"] for o in van_han.read_traced(tv, palace)]


def test_th_ix6_thuong_su_needs_the_stem_and_the_branch():
    """TH p.115 IX.6: người Giáp kỵ Thiên Thương, Thiên Sứ đóng cung Dần; người Canh gặp Thương Sứ ở cung Thân."""
    base = synth()
    dan, than = _at(base, "Dần"), _at(base, "Thân")
    tv = dataclasses.replace(synth([S("Thiên Sứ", dan), S("Thiên Thương", than)]), year_gz="Giáp Tý")
    assert _fires("TH_IX6_GIAP_THUONG_SU", tv, dan) and not _fires("TH_IX6_CANH_THUONG_SU", tv, than)
    assert "Thiên Sứ" in next(o["text"] for o in van_han.read_traced(tv, dan) if o["rule_id"] == "TH_IX6_GIAP_THUONG_SU")
    tv = dataclasses.replace(tv, year_gz="Canh Ngọ")
    assert _fires("TH_IX6_CANH_THUONG_SU", tv, than) and not _fires("TH_IX6_GIAP_THUONG_SU", tv, dan)


def test_th_ix9_and_ix10_read_the_birth_year_branch():
    tv = dataclasses.replace(synth([S("Thiên Thương", "Nô Bộc"), S("Kình Dương", "Quan Lộc"), S("Đà La", "Tài Bạch"),
                                    S("Văn Khúc", "Tài Bạch")]), year_gz="Bính Thân")
    assert _fires("TH_IX9_THAN_THUONG", tv, "Nô Bộc") and not _fires("TH_IX10_TU_MO_KINH_DA", tv, "Quan Lộc")
    tv = dataclasses.replace(tv, year_gz="Mậu Thìn")
    assert not _fires("TH_IX9_THAN_THUONG", tv, "Nô Bộc")
    # Kình or Đà alone: 'không hề gì'; with Tử, Phủ, Xương or Khúc: 'hoạnh phát' — never both on one palace
    assert _fires("TH_IX10_TU_MO_KINH_DA", tv, "Quan Lộc") and not _fires("TH_IX10_TU_MO_KINH_DA_PHAT", tv, "Quan Lộc")
    assert _fires("TH_IX10_TU_MO_KINH_DA_PHAT", tv, "Tài Bạch") and not _fires("TH_IX10_TU_MO_KINH_DA", tv, "Tài Bạch")


def test_th_6n_needs_all_six_stars_in_the_tam_phuong():
    """TH p.117 6n: Sát Phá Tham hội Tang Hổ Khốc Khách, Đà, Thiên thương."""
    six = ["Tang Môn", "Bạch Hổ", "Thiên Khốc", "Điếu Khách", "Đà La", "Thiên Thương"]
    where = ["Quan Lộc", "Phu Thê", "Quan Lộc", "Tài Bạch", "Mệnh", "Quan Lộc"]     # Quan Lộc's tam phương: Mệnh, Tài Bạch; xung chiếu Phu Thê
    ops = [S("Thất Sát", "Quan Lộc")] + [S(s, w) for s, w in zip(six, where)]
    assert _fires("TH_6N_SPT_TANG_HO", synth(ops), "Quan Lộc")
    assert not _fires("TH_6N_SPT_TANG_HO", synth(ops[:-1]), "Quan Lộc")
    assert not _fires("TH_6N_SPT_TANG_HO", synth(ops[1:]), "Quan Lộc")
    assert not _fires("TH_6N_SPT_TANG_HO", synth(ops[:5] + [S("Thiên Thương", "Huynh Đệ")]), "Quan Lộc")


def test_th_hạn_tags_keep_tieu_han_and_trung_phung_rules_off_the_wrong_reading():
    """TH p.117 6i names the tiểu hạn only; IX.7 needs đại and tiểu hạn on one palace, which read() cannot know."""
    tv = synth([S("Tang Môn", "Quan Lộc"), S("Hỏa Tinh", "Quan Lộc"), S("Linh Tinh", "Quan Lộc")])
    traced = [o for o in van_han.read_traced(tv, "Quan Lộc") if o["rule_id"] == "TH_6I_TANG_HOA_LINH"]
    assert traced and traced[0]["han"] == "tieu"
    assert any("Tang Môn" in o["text"] for o in van_han.read(tv, "Quan Lộc", han="tieu"))
    assert not any("Tang Môn" in o["text"] for o in van_han.read(tv, "Quan Lộc", han="dai"))
    assert not any("Tang Môn" in o["text"] for o in van_han.read(tv, "Quan Lộc"))
    ty = _at(synth(menh="Ngọ"), "Tý")            # read() says nothing for the Mệnh palace itself
    tv = synth([S("Thiên Thương", ty), S("Kình Dương", ty), S("Thái Tuế", ty)], menh="Ngọ")
    assert [o["han"] for o in van_han.read_traced(tv, ty) if o["rule_id"] == "TH_IX7_TRUNG_PHUNG_TY"] == ["trung_phung"]
    assert van_han.read(tv, ty, han="tieu") == van_han.read(tv, ty, han="dai") == van_han.read(tv, ty)


def test_grave_rules_are_told_without_the_event():
    """Owner 2026-10-24: the rules naming death, prison, injury, illness, burns, drowning or mourning say only 'theo sách rất bất lợi'."""
    grave = [r for r in van_han.rules() if r["text"].endswith("theo sách rất bất lợi.")]
    assert len(grave) >= 27
    words = ("chết", " tù", "đại tang", "tang sự", "tai nạn", "bỏng", "cháy", "đuối", " mù", "ốm", "thương tật", "tàn tật", "lao lý", "tai họa",
             "tai ương", "hãm hại", "sinh ly", "tử biệt")
    for r in grave:
        assert not any(w in r["text"].lower() for w in words), r["id"]
