"""Xem ngày month calendar: only computed parts (lunar date, can chi, tiết khí, lục xung), checked against independent references."""
import datetime as dt
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tvbt import xem_ngay as x
from tvbt.api import app

HKO = json.loads((Path(__file__).resolve().parent / "fixtures" / "calendar_reference_hko.json").read_text("utf-8"))
HAN = {"冬至": 0, "小寒": 1, "大寒": 2, "立春": 3, "雨水": 4, "驚蟄": 5, "春分": 6, "清明": 7, "穀雨": 8, "立夏": 9, "小滿": 10, "芒種": 11,
       "夏至": 12, "小暑": 13, "大暑": 14, "立秋": 15, "處暑": 16, "白露": 17, "秋分": 18, "寒露": 19, "霜降": 20, "立冬": 21, "小雪": 22, "大雪": 23}


@pytest.mark.parametrize("year", [1950, 1984, 1990, 2000, 2017, 2026, 2033])
def test_terms_and_month_starts_match_the_hong_kong_observatory_table_in_utc8(year):
    """Calendar 'cn' (UTC+8) must reproduce the HKO conversion table: every solar term on its day, every lunar month start."""
    ref = HKO["years"][str(year)]
    got_terms, got_starts = [], []
    for m in range(1, 13):
        for d in x.month_view(year, m, "cn")["days"]:
            got_terms += [[d["date"], t["index"]] for t in d["terms"]]
            if d["lunar"]["day"] == 1:
                got_starts.append([d["date"], d["lunar"]["month"], d["lunar"]["leap"]])
    assert got_terms == [[d, HAN[n]] for d, n in ref["terms"]]
    assert got_starts == ref["month_starts"]


def test_vietnamese_calendar_differs_from_the_chinese_one_where_it_should():
    # 1985: Vietnam (UTC+7) kept Tết on 21 Jan, China on 20 Feb; 2026: both on 17 Feb
    assert x.day_info(dt.date(1985, 1, 21))["lunar"] == {"day": 1, "month": 1, "year": 1985, "leap": False}
    assert x.day_info(dt.date(1985, 1, 21), "cn")["lunar"]["month"] == 12
    assert x.day_info(dt.date(2026, 2, 17))["lunar"] == {"day": 1, "month": 1, "year": 2026, "leap": False}
    # before 1968 the historical calendar used UTC+8; 'vn_utc7' (the chart option) uses UTC+7 for every year
    assert x.month_view(1960, 1, "vn")["utc_offset"] == 8.0 and x.month_view(1960, 1, "vn_utc7")["utc_offset"] == 7.0
    assert x.month_view(1960, 1, "vn")["days"] == x.month_view(1960, 1, "cn")["days"]


def test_can_chi_of_day_month_year():
    d = x.day_info(dt.date(2000, 1, 1))
    assert d["can_chi"]["day"]["name"] == "Mậu Ngọ"            # the commonly printed anchor for 1 Jan 2000
    assert d["can_chi"]["year"]["name"] == "Kỷ Mão"             # still lunar year 1999
    t = x.day_info(dt.date(2026, 2, 17))["can_chi"]
    assert (t["year"]["name"], t["month"]["name"]) == ("Bính Ngọ", "Canh Dần")   # ngũ hổ độn: Bính year -> Canh Dần month 1
    # the day cycle advances by one every day, across month ends
    days = x.month_view(2026, 1)["days"] + x.month_view(2026, 2)["days"]
    idx = [(d["can_chi"]["day"]["stem"], d["can_chi"]["day"]["branch"]) for d in days]
    for (s0, b0), (s1, b1) in zip(idx, idx[1:]):
        assert ((s0 + 1) % 10, (b0 + 1) % 12) == (s1, b1)


def test_leap_month_gets_no_guessed_can_chi():
    d = x.day_info(dt.date(2025, 7, 25))
    assert d["lunar"] == {"day": 1, "month": 6, "year": 2025, "leap": True}
    assert d["can_chi"]["month"] is None


def test_bazi_pillars_change_at_lap_xuan_not_at_tet():
    feb = {d["day"]: d for d in x.month_view(2026, 2)["days"]}
    assert feb[3]["bazi"]["year"]["name"] == "Ất Tỵ" and feb[5]["bazi"]["year"]["name"] == "Bính Ngọ"
    lx = feb[4]["terms"][0]
    assert lx["name"] == "Lập Xuân" and lx["kind"] == "tiết"
    assert lx["bazi_year_after"] == "Bính Ngọ" and lx["bazi_month_after"] == "Canh Dần"
    assert feb[16]["can_chi"]["year"]["name"] == "Ất Tỵ"       # lunar year changes only at Tết (17 Feb)


def test_clash_with_birth_branch_is_the_six_clash_table():
    m = x.month_view(2026, 10, birth_branch=6)                     # tuổi Ngọ
    assert m["birth_branch"]["clashes_with"] == "Tý"
    for d in m["days"]:
        assert d["clash"] == (d["can_chi"]["day"]["branch"] == 0)
    assert 2 <= sum(d["clash"] for d in m["days"]) <= 3
    assert "clash" not in x.month_view(2026, 10)["days"][0]


def test_nothing_without_a_source_is_produced():
    m = x.month_view(2026, 10)
    assert "Ngọc Hạp Thông Thư" in m["not_computed"]
    keys = set().union(*(d.keys() for d in m["days"]))
    assert keys == {"date", "day", "weekday", "lunar", "can_chi", "bazi", "terms"}
    with pytest.raises(ValueError):
        x.month_view(1800, 1)
    with pytest.raises(ValueError):
        x.month_view(2026, 13)


def test_api_endpoint():
    c = TestClient(app)
    r = c.get("/api/calendar", params={"year": 2026, "month": 2, "branch": 6})
    assert r.status_code == 200 and "max-age" in r.headers["cache-control"]
    j = r.json()
    assert len(j["days"]) == 28 and j["first_weekday"] == 6 and j["birth_branch"]["name"] == "Ngọ"
    assert c.get("/api/calendar", params={"year": 2026, "month": 0}).status_code == 422
    assert c.get("/api/calendar", params={"year": 2026, "month": 1, "branch": 12}).status_code == 422
