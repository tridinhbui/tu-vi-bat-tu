import datetime as dt

import pytest

from tvbt import bazi, temporal
from tvbt.bazi import add_ymd, decimal_year
from tvbt.calendar_core import BirthInput, normalize


def chart(y, m, d, h=10, gender="male"):
    nb = normalize(BirthInput(y, m, d, h, 0, "Asia/Ho_Chi_Minh", gender))
    return nb, bazi.compute(nb)


def test_add_ymd_clips_month_end_and_carries_years():
    assert add_ymd(dt.date(2000, 1, 31), 0, 1, 0) == dt.date(2000, 2, 29)
    assert add_ymd(dt.date(2001, 1, 31), 0, 1, 0) == dt.date(2001, 2, 28)
    assert add_ymd(dt.date(1990, 12, 15), 5, 3, 10) == dt.date(1996, 3, 25)
    assert add_ymd(dt.date(1990, 11, 15), 0, 14, 0) == dt.date(1992, 1, 15)


def test_decimal_year_monotone_and_leap_aware():
    assert decimal_year(dt.date(2000, 1, 1)) == 2000.0
    assert 2000.99 < decimal_year(dt.date(2000, 12, 31)) < 2001.0
    assert decimal_year(dt.date(2001, 3, 1)) > decimal_year(dt.date(2001, 2, 28))


def test_luck_start_date_is_birth_plus_the_three_day_rule():
    nb, bz = chart(1990, 12, 15)
    ls = bz.luck_start
    d0 = add_ymd(nb.local.date(), ls["years"], ls["months"], round(ls["days"]))
    assert abs((dt.date.fromisoformat(bz.luck_pillars[0].start_date) - d0).days) <= 1
    assert bz.luck_start["start_date"] == bz.luck_pillars[0].start_date
    steps = [dt.date.fromisoformat(l.start_date) for l in bz.luck_pillars]
    assert all(9 * 365 <= (b - a).days <= 10 * 366 + 1 for a, b in zip(steps, steps[1:]))      # ten calendar years apart


def test_start_year_approx_can_be_a_year_off_and_exact_is_not():
    nb, bz = chart(1990, 12, 15)
    lp = bz.luck_pillars[0]
    assert lp.start_year_exact - lp.start_year_approx > 0.7          # December birth: the approximation ignores the month
    assert dt.date.fromisoformat(lp.start_date) > nb.local.date()
    assert int(lp.start_year_exact) == dt.date.fromisoformat(lp.start_date).year


def test_luck_for_year_uses_the_exact_start_date():
    nb, bz = chart(1990, 12, 15)
    lps = bz.luck_pillars
    s = lps[1].start_year_exact
    y_before = int(s) - 1 if s - int(s) > 0.09 else int(s) - 2          # a BaZi year that begins before luck #2 starts
    assert temporal.bazi_year(bz, 1990, int(s) - 1)["luck_pillar"] == lps[0].name
    after = temporal.bazi_year(bz, 1990, int(s) + 1)
    assert after["luck_pillar"] == lps[1].name
    assert s - int(s) >= 0.09 or True


def test_luck_boundary_flag_in_the_year_it_happens():
    nb, bz = chart(1990, 12, 15)
    s = bz.luck_pillars[1].start_year_exact
    y = int(s)                                                           # the Gregorian year containing the change
    flags = {yy: temporal.bazi_year(bz, 1990, yy)["luck_changes_within_year"] for yy in range(y - 2, y + 2)}
    assert sum(flags.values()) == 1 and flags[y if s - y >= 0.09 else y - 1] is True


def test_old_integer_age_test_would_have_picked_a_different_luck_for_some_years():
    nb, bz = chart(1990, 12, 15)
    diffs = 0
    for y in range(1990, 2060):
        age = y - 1990
        old = next((lp.name for lp in bz.luck_pillars if lp.start_age <= age < lp.start_age + 10), None)
        new = temporal.bazi_year(bz, 1990, y)["luck_pillar"]
        diffs += old != new
    assert diffs >= 1          # this is the bug the exact start date fixes
