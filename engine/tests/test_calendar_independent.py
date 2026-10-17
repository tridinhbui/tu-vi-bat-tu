"""Phase 7: the calendar layer (solar -> lunar -> can chi) against INDEPENDENT references, kept apart from star placement (an_sao) and formation judgement (luan_cach).
References: (1) Hong Kong Observatory table 1901-2100 (UTC+8) as fixtures/calendar_reference_hko.json; (2) the amlich algorithm in oracle_calendar_independent.py (validated against HKO
first, then used for UTC+7/+8 Vietnamese rules); (3) PyEphem new-moon times for the borderline days."""
import bisect
import datetime as dt
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle_calendar_independent as K  # noqa: E402
import oracle_tuvi_independent as O  # noqa: E402
from tvbt import calendar_core as cc, tuvi  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"
HKO = json.loads((FIX / "calendar_reference_hko.json").read_text("utf-8"))
CMP = json.loads((FIX / "calendar_comparison.json").read_text("utf-8"))
STARTS = sorted((dt.date.fromisoformat(d), m, lp) for y in range(1901, 2101) for d, m, lp in HKO["years"][str(y)]["month_starts"])
KEYS = [s[0] for s in STARTS]


def hko_lunar(d):
    s = STARTS[bisect.bisect_right(KEYS, d) - 1]
    return ((d - s[0]).days + 1, s[1], s[2])


def prod(d, cal="vn", hour=12, minute=0, zi="early_zi_next_day", tz="Asia/Ho_Chi_Minh"):
    return cc.normalize(cc.BirthInput(d.year, d.month, d.day, hour, minute, tz, "male", calendar=cal, zi_rule=zi))


# ---- the reference itself ---------------------------------------------------------------------------------------------------------------
def test_the_amlich_oracle_reproduces_hko_month_starts_after_the_1929_time_standard():
    """Before 1929 China used local mean time (UTC+7:45); the oracle's UTC+8 therefore disagrees on a few early starts. From 1929 to 2096: zero month-start disagreements."""
    bad = []
    for d, m, leap in STARTS:
        if 1929 <= d.year <= 2096:
            ld, lm, ly, ll = K.solar_to_lunar(d.day, d.month, d.year, 8)
            if (ld, lm, ll) != (1, m, leap):
                bad.append((d.isoformat(), (m, leap), (ld, lm, ll)))
    assert bad == [], bad[:5]


def test_oracle_day_pillar_and_year_pillar_anchor_points():
    """JDN anchor: 1900-01-31 (lunar new year 1900) is Giáp Thìn day; 2000-01-01 is Mậu Ngọ day; 1984-02-02 is Giáp Tý (cycle start year)."""
    assert K.day_pillar(1, 1, 2000) == ("Mậu", "Ngọ")
    assert K.year_pillar(1984) == ("Giáp", "Tý") and K.year_pillar(2024) == ("Giáp", "Thìn") and K.year_pillar(1900) == ("Canh", "Tý")


# ---- production vs the references ---------------------------------------------------------------------------------------------------------
def test_pinned_full_day_scan_1930_2060():
    assert CMP["days"] == 47789
    assert CMP["counts"]["cn_vs_hko"] == 0                     # production's Chinese calendar (sxtwl) == HKO on every day
    assert CMP["counts"]["oracle8_vs_hko"] == 4                # the amlich approximation fails on exactly four borderline days (below)
    assert CMP["spans"]["oracle8_vs_hko"] == [[x, x] for x in ("1939-04-19", "1947-03-22", "2009-03-26", "2054-05-07")]
    assert CMP["spans"]["vn_vs_oracle"] == CMP["spans"]["vn_south_vs_oracle"] == [["1939-04-19", "1939-04-19"], ["1947-03-22", "1947-03-22"], ["2033-12-22", "2033-12-31"], ["2054-05-07", "2054-05-07"]]


def test_the_single_day_disagreements_are_borderline_new_moons_not_production_errors():
    """PyEphem: each of these new moons falls within 40 minutes after local midnight, so the civil month start depends on sub-hour accuracy; production equals HKO there."""
    ephem = pytest.importorskip("ephem")
    for ymd, tz in (("1939/04/10", 8), ("1947/03/12", 8), ("2009/03/16", 8), ("2054/04/28", 7)):
        t = ephem.Date(ephem.next_new_moon(ymd)).datetime() + dt.timedelta(hours=tz)
        assert t.hour == 0 and t.minute < 40, (ymd, t)
    for d in (dt.date(1939, 4, 19), dt.date(1947, 3, 22), dt.date(2009, 3, 26)):
        n = prod(d, "cn").lunar
        assert (n.day, n.month, n.is_leap) == hko_lunar(d)


@pytest.mark.xfail(strict=True, reason="calendar bug (lunar_vn.solar_to_lunar splits on the Gregorian year): 2033-12-22..31 should be leap month 11 like sxtwl, HKO and the amlich oracle; "
                                       "recorded for the module owner, NOT fixed in Phase 7 (calendar logic is out of scope)")
def test_vn_calendar_2033_leap_month_11_at_the_year_end():
    for d in range(22, 32):
        n = prod(dt.date(2033, 12, d), "vn").lunar
        assert (n.day, n.month, n.is_leap) == (d - 21, 11, True)


def test_the_2033_bug_is_confined_to_the_vietnamese_path_and_has_a_precise_signature():
    """the same days are right in the Chinese path and in January 2034: the Vietnamese path numbers 2033-12-22 as month 12 and 2034-01-20 as month 12 again (two month 12s)."""
    assert hko_lunar(dt.date(2033, 12, 22)) == (1, 11, True)
    assert (lambda n: (n.day, n.month, n.is_leap))(prod(dt.date(2033, 12, 22), "cn").lunar) == (1, 11, True)
    v = prod(dt.date(2033, 12, 22), "vn").lunar
    assert (v.day, v.month, v.is_leap) == (1, 12, False)
    assert (lambda n: (n.day, n.month))(prod(dt.date(2034, 1, 20), "vn").lunar) == (1, 12)
    assert (lambda n: (n.day, n.month, n.is_leap))(prod(dt.date(2034, 1, 19), "vn").lunar) == (29, 11, True)   # the leap flag appears only on the 2034 side


def test_the_rule_for_the_vietnamese_utc_offset_is_visible_in_1968():
    """Tết 1968 (the Tet Offensive year): the new moon is 16:29 UTC on 1968-01-29, i.e. 00:29 on Jan 30 in UTC+8 but 23:29 on Jan 29 in UTC+7. China/HKO: Tết = Jan 30; Vietnam
    (UTC+7 from 1968, production rule) = Jan 29 — the well-known one-day gap between North Vietnam and China/the South."""
    ephem = pytest.importorskip("ephem")
    nm = ephem.Date(ephem.next_new_moon("1968/01/20")).datetime()
    assert (nm.day, nm.hour) == (29, 16)
    assert hko_lunar(dt.date(1968, 1, 29)) == (30, 12, False) and hko_lunar(dt.date(1968, 1, 30)) == (1, 1, False)
    n_cn, n_vn = prod(dt.date(1968, 1, 29), "cn").lunar, prod(dt.date(1968, 1, 29), "vn").lunar
    assert (n_cn.day, n_cn.month) == (30, 12) and (n_vn.day, n_vn.month) == (1, 1)
    assert (lambda n: (n.day, n.month))(prod(dt.date(1967, 1, 21), "vn").lunar) == (hko_lunar(dt.date(1967, 1, 21))[0], hko_lunar(dt.date(1967, 1, 21))[1])   # before 1968 Vietnam == China
    assert cc.vn_calendar_offset(1967) == 8.0 and cc.vn_calendar_offset(1968) == 7.0 and cc.vn_calendar_offset(1975, south=True) == 8.0 and cc.vn_calendar_offset(1976, south=True) == 7.0


def test_production_cn_on_every_month_boundary_equals_hko():
    for d, m, leap in STARTS:
        if 1950 <= d.year <= 2050:
            n = prod(d, "cn").lunar
            assert (n.day, n.month, n.is_leap) == (1, m, leap), d
            before = prod(d - dt.timedelta(days=1), "cn").lunar
            assert before.day in (29, 30) and (before.month, before.is_leap) != (m, leap), d


# ---- boundary tests -----------------------------------------------------------------------------------------------------------------------------
TY = [(22, 59, 11), (23, 0, 0), (23, 59, 0), (0, 0, 0), (0, 59, 0), (1, 0, 1), (2, 59, 1), (3, 0, 2)]      # hour, minute, expected hour branch (Tý=0)


@pytest.mark.parametrize("hour,minute,hb", TY)
@pytest.mark.parametrize("zi", ["early_zi_next_day", "late_zi_same_day"])
def test_gio_ty_and_day_rollover_against_the_oracle(hour, minute, hb, zi):
    d = dt.date(2021, 3, 17)                                       # an ordinary mid-month day
    nb = prod(d, "cn", hour, minute, zi)
    expect_date = d + dt.timedelta(days=1) if (hour == 23 and zi == "early_zi_next_day") else d
    assert nb.rule_date == expect_date
    want = K.solar_to_lunar(expect_date.day, expect_date.month, expect_date.year, 8)
    assert (nb.lunar.day, nb.lunar.month, nb.lunar.year) == want[:3]
    tv = tuvi.compute(nb)
    o = O.chart(want[2], want[1], want[0], hb, True)
    assert tv.extras["hour_branch"] == hb == ((hour + 1) // 2) % 12
    assert (tv.menh_branch, tv.than_branch, tv.cuc["n"]) == (o["menh"], o["than"], o["cuc"])


def test_the_ty_hour_rule_moves_the_lunar_year_at_tet():
    """2024-02-09 23:30: with 'early Tý' the chart is the lunar new-year day (Giáp Thìn); with 'late Tý' it is still 30 tháng Chạp of Quý Mão. A genuine school choice, not an error."""
    d = dt.date(2024, 2, 9)
    assert hko_lunar(dt.date(2024, 2, 10)) == (1, 1, False)
    early, late = prod(d, "cn", 23, 30, "early_zi_next_day"), prod(d, "cn", 23, 30, "late_zi_same_day")
    assert (early.lunar.year, early.lunar.day) == (2024, 1) and (late.lunar.year, late.lunar.day) == (2023, 30)
    assert tuvi.compute(early).year_gz == "Giáp Thìn" and tuvi.compute(late).year_gz == "Quý Mão"


def test_tu_vi_uses_the_lunar_year_not_lap_xuan():
    """2024-02-05 is after Lập Xuân (HKO: 2024-02-04) but before Tết (2024-02-10): Tử Vi year = Quý Mão (a Bát Tự reading would already say Giáp Thìn)."""
    terms = {t: d for d, t in HKO["years"]["2024"]["terms"]}
    assert terms["立春"] == "2024-02-04"
    assert tuvi.compute(prod(dt.date(2024, 2, 5), "vn")).year_gz == "Quý Mão" == " ".join(K.year_pillar(K.solar_to_lunar(5, 2, 2024, 7)[2]))


def test_leap_months_every_year_in_hko_1950_2050():
    leaps = [(d, m) for d, m, lp in STARTS if lp and 1950 <= d.year <= 2050]
    assert len(leaps) >= 35
    for d, m in leaps:
        n = prod(d, "cn").lunar
        assert (n.day, n.month, n.is_leap) == (1, m, True)
        prev = prod(d - dt.timedelta(days=1), "cn").lunar
        assert (prev.month, prev.is_leap) == (m, False)


@pytest.mark.parametrize("rule", ["same_month", "next_month", "split_15"])
def test_leap_month_rules_move_menh_exactly_as_documented(rule):
    """leap month: same_month = its own number; next_month = number+1; split_15 = day<=15 own number, else next. Mệnh/Thân recomputed independently by the oracle."""
    for d, m, lp in [s for s in STARTS if s[2] and 1990 <= s[0].year <= 2030]:
        for dd in (0, 14, 15, 20):
            day = d + dt.timedelta(days=dd)
            nb = prod(day, "cn")
            if not nb.lunar.is_leap:
                continue
            eff = {"same_month": m, "next_month": m % 12 + 1, "split_15": m if nb.lunar.day <= 15 else m % 12 + 1}[rule]
            tv = tuvi.compute(nb, leap_rule=rule)
            o = O.chart(nb.lunar.year, eff, nb.lunar.day, 6, True)
            assert (tv.menh_branch, tv.than_branch) == (o["menh"], o["than"]) or tv.extras["hour_branch"] != 6, (day, rule)


def test_timezone_changes_the_instant_not_the_wall_clock_date_and_dst_gaps_are_rejected():
    a = prod(dt.date(2021, 3, 17), "cn", 10, 0, tz="Asia/Ho_Chi_Minh")
    b = prod(dt.date(2021, 3, 17), "cn", 10, 0, tz="Asia/Shanghai")
    assert (a.lunar, a.rule_date) == (b.lunar, b.rule_date) and a.utc != b.utc            # the lunar date is read from the civil wall clock of the birth place
    with pytest.raises(ValueError):
        prod(dt.date(2021, 3, 14), "cn", 2, 30, tz="America/New_York")                  # spring-forward gap does not exist
