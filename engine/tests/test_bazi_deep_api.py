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
