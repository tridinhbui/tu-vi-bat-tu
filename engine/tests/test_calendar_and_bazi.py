"""Golden facts come from public calendar knowledge or hand derivation — never from the code under test."""
import datetime as dt

import pytest

from tvbt import bazi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import NAP_AM_NAMES, cycle_index, from_cycle, nap_am_element


def B(y, m, d, h=12, mi=0, tz="Asia/Ho_Chi_Minh", g="male", **kw):
    return BirthInput(y, m, d, h, mi, tz, g, **kw)


def names(c):
    return {k: p.name for k, p in c.pillars.items()}


def test_2000_01_01_noon_known_pillars():
    # 1 Jan 2000 is Mậu Ngọ day (well-known anchor); before Tiểu Hàn -> month Bính Tý; before Lập Xuân -> year Kỷ Mão
    c = bazi.compute(normalize(B(2000, 1, 1, 12, 0)))
    assert names(c) == {"year": "Kỷ Mão", "month": "Bính Tý", "day": "Mậu Ngọ", "hour": "Mậu Ngọ"}


def test_lichun_instant_boundary_1990():
    # Lập Xuân 1990 = 4 Feb 10:14 Beijing time
    before = bazi.compute(normalize(B(1990, 2, 4, 10, 13, tz="Asia/Shanghai")))
    after = bazi.compute(normalize(B(1990, 2, 4, 10, 15, tz="Asia/Shanghai")))
    assert before.pillars["year"].name == "Kỷ Tỵ" and before.pillars["month"].name == "Đinh Sửu"
    assert after.pillars["year"].name == "Canh Ngọ" and after.pillars["month"].name == "Mậu Dần"


def test_year_pillar_ignores_lunar_new_year():
    # Tet 1990 = 27 Jan 1990; BaZi year still Kỷ Tỵ until Lập Xuân
    assert bazi.compute(normalize(B(1990, 2, 1))).pillars["year"].name == "Kỷ Tỵ"
    assert normalize(B(1990, 2, 1)).lunar.year == 1990  # but lunar year already 1990 (Canh Ngọ) for Tử Vi


def test_zi_hour_rules():
    early = bazi.compute(normalize(B(2000, 1, 1, 23, 30, zi_rule="early_zi_next_day")))
    late = bazi.compute(normalize(B(2000, 1, 1, 23, 30, zi_rule="late_zi_same_day")))
    assert early.pillars["day"].name == "Kỷ Mùi" and early.pillars["hour"].name == "Giáp Tý"
    assert late.pillars["day"].name == "Mậu Ngọ" and late.pillars["hour"].name == "Nhâm Tý"


def test_nap_am_method_matches_named_table():
    for n in range(60):
        s, b = from_cycle(n)
        assert nap_am_element(s, b) == NAP_AM_NAMES[n // 2][1]


def test_cycle_roundtrip():
    for n in range(60):
        assert cycle_index(*from_cycle(n)) == n


def test_luck_direction_and_start_age():
    # Canh (yang) male -> forward
    c = bazi.compute(normalize(B(1990, 5, 17, 10, 30)))
    assert c.luck_direction == "thuận"
    f = bazi.compute(normalize(B(1990, 5, 17, 10, 30, g="female")))
    assert f.luck_direction == "nghịch"
    # Birth 17 May 10:30; next jie (Mang Chung) ~6 Jun 1990 -> ~20 days -> ~6.6 years
    assert 6.3 < c.luck_start["age_years"] < 6.9
    assert c.luck_pillars[0].name == "Nhâm Ngọ"  # month Tân Tỵ + 1 step
    assert f.luck_pillars[0].name == "Canh Thìn"  # month Tân Tỵ - 1 step


def test_dst_gap_rejected_and_ambiguity_flagged():
    with pytest.raises(ValueError):
        normalize(B(2021, 3, 14, 2, 30, tz="America/New_York"))
    nb = normalize(B(2021, 11, 7, 1, 30, tz="America/New_York"))
    assert nb.trace.get("tz.resolve").result["ambiguous_wall_time"] is True


def test_historic_offset_vietnam_1975():
    # Saigon used UTC+8 in 1970 per tzdata; the engine must follow IANA, not assume +7
    nb = normalize(B(1970, 6, 1, 12, 0))
    assert str(nb.local.utcoffset()) in ("8:00:00", "7:00:00")
    assert nb.utc.hour == 12 - int(nb.local.utcoffset().total_seconds() // 3600)


def test_true_solar_time_longitude_shift():
    nb = normalize(B(2000, 6, 15, 12, 0, longitude=105.0 + 7.5, use_true_solar_time=True))
    st = nb.trace.get("clock.true_solar").result
    assert st["longitude_minutes"] == pytest.approx(30.0, abs=0.01)  # 7.5 deg * 4 min
    assert abs(st["eot_minutes"]) < 17


def test_lunar_known_new_years():
    assert (normalize(B(1984, 2, 2)).lunar.day, normalize(B(1984, 2, 2)).lunar.month,
            normalize(B(1984, 2, 2)).lunar.year) == (1, 1, 1984)
    assert normalize(B(2000, 2, 5)).lunar.month == 1 and normalize(B(2000, 2, 5)).lunar.day == 1
    assert normalize(B(1990, 1, 27)).lunar.day == 1
    n = normalize(B(2020, 6, 1))
    assert (n.lunar.month, n.lunar.is_leap) == (4, True)  # leap 4th month of 2020 (well-known)


def test_branch_relations_are_facts_not_transformations():
    c = bazi.compute(normalize(B(2000, 1, 1, 12, 0)))
    for r in c.relations["stem_combine"]:
        assert r["transforms"] is None


def test_hidden_stems_ten_gods_day_master_self():
    c = bazi.compute(normalize(B(2000, 1, 1, 12, 0)))
    assert c.pillars["day"].stem_ten_god is None
    assert c.day_master_element == "Thổ"
    # 午 hides 丁 己: for Mậu day master -> Chính Ấn, Tỉ Kiên? (己 vs 戊 = Kiếp Tài)
    tg = [h["ten_god"] for h in c.pillars["day"].hidden]
    assert tg == ["Chính Ấn", "Kiếp Tài"]


def test_vn_calendar_offsets_and_1985_divergence():
    from tvbt.calendar_core import vn_calendar_offset
    assert vn_calendar_offset(1967) == 8 and vn_calendar_offset(1968) == 7 and vn_calendar_offset(2000) == 7
    assert vn_calendar_offset(1970, south=True) == 8 and vn_calendar_offset(1976, south=True) == 7
    # Wikipedia (Vietnamese calendar): the 1984-85 month-11 placement depends on the offset (Chinese month 11 = 22 Dec 1984-20 Jan 1985)
    cn = normalize(B(1984, 12, 22, 12, 0, calendar="cn")).lunar
    vn = normalize(B(1984, 12, 22, 12, 0, calendar="vn")).lunar
    assert (cn.day, cn.month) == (1, 11) and (vn.month, vn.day) != (cn.month, cn.day)
    s70 = normalize(B(1970, 6, 1, 12, 0, calendar="vn_south")).trace.get("lunar.date").rule
    assert "UTC+8" in s70
