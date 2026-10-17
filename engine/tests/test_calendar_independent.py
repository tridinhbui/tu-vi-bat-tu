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
def test_pinned_full_day_scan_1903_2098():
    assert CMP["days"] == 71530 and CMP["range"] == ["1903-03-01", "2098-12-31"]
    assert CMP["counts"]["cn_vs_hko"] == 0                     # production's Chinese calendar (sxtwl) == HKO on every one of 71,530 days
    # the amlich oracle itself disagrees with HKO on: 1914/1916/1920 (before the 1929 time standard, China used local mean time) and on single borderline new moons
    pre1929 = {("1914-11-17", "1914-12-16"), ("1916-02-03", "1916-03-03"), ("1920-11-10", "1920-12-09")}
    assert {tuple(x) for x in CMP["spans"]["oracle8_vs_hko"]} - pre1929 == {("1939-04-19",) * 2, ("1947-03-22",) * 2, ("2009-03-26",) * 2, ("2054-05-07",) * 2, ("2062-04-09",) * 2, ("2097-08-07", "2097-09-05")}
    assert CMP["spans"]["vn_vs_oracle"] == CMP["spans"]["vn_south_vs_oracle"] == [["1939-04-19", "1939-04-19"], ["1947-03-22", "1947-03-22"], ["2054-05-07", "2054-05-07"],
                                                                                  ["2062-04-09", "2062-04-09"], ["2072-12-09", "2073-01-07"], ["2077-11-15", "2077-12-14"]]
    # the 2033 leap-month defect (Phase 7) no longer appears in any span
    assert not any(x[0] <= "2033-12-31" and x[1] >= "2033-12-22" for x in CMP["spans"]["vn_vs_oracle"])


@pytest.mark.parametrize("start", ["1939-04-19", "1947-03-22", "2054-05-07", "2062-04-09", "2072-12-09", "2077-11-15"])
def test_every_remaining_vn_disagreement_starts_on_a_borderline_new_moon(start):
    """PyEphem new moon within 45 minutes of the local midnight that decides the civil month start (the 2072/2077 cases are 1-2 minutes BEFORE midnight, a predicted-ΔT-sensitive
    instant). Production agrees with PyEphem; the amlich series is the approximate one."""
    ephem = pytest.importorskip("ephem")
    d = dt.date.fromisoformat(start)
    tz = 8 if d.year < 1968 else 7
    t = ephem.Date(ephem.next_new_moon(f"{d.year}/{d.month}/{max(1, d.day - 9) if d.day > 9 else 1}")).datetime() + dt.timedelta(hours=tz)
    near_midnight = min(abs((t - t.replace(hour=0, minute=0, second=0)).total_seconds()), abs((t.replace(hour=0, minute=0, second=0) + dt.timedelta(days=1) - t).total_seconds())) / 60
    assert near_midnight < 45, (start, t, near_midnight)


def test_vn_calendar_2033_leap_month_11_at_the_year_end():
    """Phase 8 fix (lunar_vn window now reaches the next winter): 2033-12-22..31 are leap month 11, like sxtwl, HKO, the amlich oracle and PyEphem."""
    for d in range(22, 32):
        n = prod(dt.date(2033, 12, d), "vn").lunar
        assert (n.day, n.month, n.is_leap) == (d - 21, 11, True), d
    assert (lambda n: (n.day, n.month, n.is_leap))(prod(dt.date(2034, 1, 20), "vn").lunar) == (1, 12, False)


@pytest.mark.parametrize("tz", [7.0, 8.0])
def test_year_end_windows_have_consecutive_month_numbering_1950_2100(tz):
    """structural invariant that would have caught the 2033 defect: across Dec 10 .. Jan 31 every day either continues its month or starts the next one (same number only for
    the leap pair, otherwise +1 mod 12) — no duplicated month numbers."""
    from tvbt import lunar_vn
    bad = []
    for y in range(1950, 2100):
        d, prev = dt.date(y, 12, 10), None
        while d <= dt.date(y + 1, 1, 31):
            day, month, ly, leap = lunar_vn.solar_to_lunar(d, tz)
            if prev:
                pd, pm, pl, pleap = prev
                if day == pd + 1:
                    ok = (month, leap) == (pm, pleap)
                else:
                    ok = day == 1 and pd in (29, 30) and ((month, leap) == (pm, True) and not pleap or (month == pm % 12 + 1 and not leap) or (month == pm and leap and not pleap))
                    ok = ok or (day == 1 and pd in (29, 30) and pleap and month == pm % 12 + 1 and not leap)
                if not ok:
                    bad.append((d.isoformat(), prev, (day, month, leap)))
            prev = (day, month, leap, leap)
            d += dt.timedelta(days=1)
    assert bad == [], bad[:4]


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
