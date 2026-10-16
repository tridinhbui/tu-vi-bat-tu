"""Regression tests for the unverified auxiliary stars, Mệnh/Thân chủ and cách-cục recognition.
These pin the *implemented* formulas (not book-verified) so accidental changes are noticed."""
from fastapi.testclient import TestClient

from tvbt.api import app

c = TestClient(app)
B = dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male")


def chart(**kw):
    return c.post("/api/chart", json={**B, **kw}).json()["tuvi"]


def where(t, star):
    return next(p["branch"] for p in t["palaces"] if star in p["stars"])


def test_aux_stars_are_placed_in_their_own_group():
    t = chart()
    grp = {s["name"]: s["group"] for s in t["stars"]}
    for n in ("Thiên Khốc", "Thiên Hư", "Long Trì", "Phượng Các", "Cô Thần", "Quả Tú", "Tam Thai", "Bát Tọa", "Thiên Thương", "Thiên Sứ"):
        assert grp[n] == "phụ tinh (chưa đối chiếu sách)", n
    assert t["school"]["rule_review"]["aux_stars"][0] == "unverified"
    assert len({n for p in t["palaces"] for n in p["stars"]}) >= 95


def test_sample_positions_1990_canh_ngo():
    t = chart()   # Canh Ngọ year, lunar 23/4, giờ Tỵ
    assert where(t, "Thiên Khốc") == where(t, "Thiên Hư") == "Tý"      # Ngọ year: both land on Tý
    assert where(t, "Long Trì") == "Tuất" and where(t, "Phượng Các") == "Thìn"
    assert where(t, "Cô Thần") == "Thân" and where(t, "Quả Tú") == "Thìn"
    assert where(t, "Thiên La") == "Thìn" and where(t, "Địa Võng") == "Tuất"
    assert where(t, "Thiên Hình") == "Tý" and where(t, "Thiên Riêu") == where(t, "Thiên Y") == "Thìn"
    names = {p["name"]: p for p in t["palaces"]}
    assert "Thiên Thương" in names["Nô Bộc"]["stars"] and "Thiên Sứ" in names["Tật Ách"]["stars"]


def test_khoc_hu_mirror_each_other_across_ngo():
    for y in (1985, 1991, 2000):
        t = chart(year=y)
        k, h = where(t, "Thiên Khốc"), where(t, "Thiên Hư")
        idx = {p["branch"]: p["branch_index"] for p in t["palaces"]}
        assert (idx[k] + idx[h]) % 12 == 0 and idx[k] != 12  # symmetric about Tý/Ngọ axis


def test_menh_chu_than_chu_and_cach_cuc():
    t = chart()
    assert t["extras"]["menh_chu"]["star"] == "Tham Lang"      # Mệnh at Tý
    assert t["extras"]["than_chu"]["star"] == "Hỏa Tinh"       # year Ngọ
    ids = {x["id"] for x in t["extras"]["cach_cuc"]}
    assert {"cach_tử_phủ_vũ_tướng", "dong_cung_vũ_phủ", "loc_ma_giao_tri", "than_cu"} <= ids
    assert all(x["review"] == "unverified" for x in t["extras"]["cach_cuc"])


def test_lunar_to_solar_roundtrip_and_errors():
    r = c.post("/api/lunar-to-solar", json=dict(year=1990, month=4, day=23)).json()
    assert r["solar"] == {"year": 1990, "month": 5, "day": 17}
    assert c.post("/api/lunar-to-solar", json=dict(year=1990, month=4, day=30)).status_code == 422   # that month has 29 days
    leap = c.post("/api/lunar-to-solar", json=dict(year=2023, month=2, day=10, leap=True)).json()["solar"]
    t = c.post("/api/chart", json={**B, **leap}).json()["tuvi"]["lunar"]
    assert (t["day"], t["month"], t["year"], t["leap"]) == (10, 2, 2023, True)


def test_hour_sweep_covers_twelve_hours_and_shows_what_changes():
    h = c.post("/api/hour-sweep", json=B).json()["hours"]
    assert [x["hour_branch"] for x in h][:3] == ["Tý", "Sửu", "Dần"] and len(h) == 12
    assert len({x["pillars"]["hour"] for x in h}) == 12
    assert len({x["pillars"]["day"] for x in h}) == 1 and len({x["pillars"]["year"] for x in h}) == 1
    assert next(x for x in h if x["hour_branch"] == "Tỵ")["menh_branch"] == "Tý"      # matches the 10:30 sample chart
