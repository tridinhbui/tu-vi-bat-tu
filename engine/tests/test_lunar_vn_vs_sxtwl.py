"""Independent cross-check: ephemeris-based converter at UTC+8 must equal sxtwl.

Known, explained exceptions (not hidden): three new moons fall within ~5 minutes after Beijing
midnight (1914-11-17, 1916-02-03, 1920-11-10 -> the two libraries disagree by one civil day
for that month), and the 2033 leap-month rule ambiguity. Any other mismatch fails the test.
"""
import datetime as dt

import sxtwl

from tvbt.lunar_vn import solar_to_lunar

KNOWN_WINDOWS = [
    (dt.date(1914, 11, 17), dt.date(1914, 12, 16)),
    (dt.date(1916, 2, 3), dt.date(1916, 3, 3)),
    (dt.date(1920, 11, 10), dt.date(1920, 12, 9)),
    (dt.date(2033, 12, 22), dt.date(2034, 12, 31)),
]


def test_matches_sxtwl_1900_2049_utc8():
    d = dt.date(1900, 3, 1)
    unexplained = []
    total = 0
    while d <= dt.date(2049, 12, 31):
        s = sxtwl.fromSolar(d.year, d.month, d.day)
        want = (s.getLunarDay(), s.getLunarMonth(), s.getLunarYear(), s.isLunarLeap())
        if want != solar_to_lunar(d, 8):
            total += 1
            if not any(a <= d <= b for a, b in KNOWN_WINDOWS):
                unexplained.append(d)
        d += dt.timedelta(days=1)
    assert not unexplained, unexplained[:10]
    assert total < 120
