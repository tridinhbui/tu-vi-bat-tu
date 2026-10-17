from fastapi.testclient import TestClient

from tvbt.api import app

C = TestClient(app)
BODY = {"year": 1990, "month": 12, "day": 15, "hour": 10, "minute": 0, "gender": "male"}


def test_bazi_structure_endpoint_returns_all_layers_and_says_draft():
    r = C.post("/api/bazi-structure", json=BODY)
    assert r.status_code == 200
    d = r.json()
    for k in ("season", "position", "interactions", "resolution", "strength_raw", "strength_after", "geju", "yongshen", "facts", "reasoning", "trace"):
        assert k in d, k
    assert d["profile"]["review_status"] == "draft" and d["reasoning"]["all_rules_draft"] is True
    assert d["season"]["command"] is not None                          # real chart: days into month are known
    assert set(d["yongshen"]["methods"]) == {"phu_uc", "dieu_hau", "cach_cuc", "thong_quan", "thuan_the"}


def test_old_endpoints_still_work_and_chart_has_exact_luck_dates():
    ch = C.post("/api/chart", json=BODY).json()
    assert ch["bazi"]["luck_pillars"][0]["start_date"] and ch["bazi"]["luck_start"]["start_date"]
    assert C.post("/api/reasoning", json=BODY).status_code == 200
    y = C.post("/api/year", json={**BODY, "to_year": 2030}).json()
    assert "luck_changes_within_year" in y["bazi"]


def test_timeline_endpoint_compares_each_luck_and_year_with_the_natal_chart():
    r = C.post("/api/bazi-timeline", json={**BODY, "to_year": 2040})
    assert r.status_code == 200
    d = r.json()
    assert d["review_status"] == "draft" and len(d["luck"]) >= 8 and len(d["years"]) == 2040 - 1990 + 1
    for e in d["luck"] + d["years"]:
        assert e["effect"] in ("pha_cach", "tro_cach", "doi_cach", "trung_tinh") and e["pack_problems"] == []
        assert set(e["roles"]) == {"phu_uc", "dieu_hau", "cach_cuc", "thong_quan", "thuan_the"}
    assert d["years"][0]["labels"] in (["year"], ["luck", "year"])


def test_timeline_year_range_is_capped_and_structure_endpoint_has_patterns():
    r = C.post("/api/bazi-timeline", json={**BODY, "from_year": 2000, "to_year": 2300})
    assert len(r.json()["years"]) == 121
    assert "patterns" in C.post("/api/bazi-structure", json=BODY).json()
