from fastapi.testclient import TestClient

from tvbt.api import app

c = TestClient(app)
B = {"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male"}


def test_chart_and_validation():
    r = c.post("/api/chart", json=B)
    assert r.status_code == 200 and r.json()["bazi"]["pillars"]["day"]["name"] == "Nhâm Ngọ"
    assert c.post("/api/chart", json={**B, "month": 13}).status_code == 422
    assert c.post("/api/chart", json={**B, "tz": "Mars/Base"}).status_code == 422
    assert c.post("/api/chart", json={**B, "use_true_solar_time": True}).status_code == 422  # no longitude


def test_reasoning_marks_draft_and_has_why():
    B2 = {**B, "year": 2000, "month": 1, "day": 1, "hour": 12, "minute": 0}  # Mậu day master with Thổ root
    r = c.post("/api/reasoning", json=B2).json()
    assert r["pack_problems"] == []
    bt = r["systems"]["bat_tu"]["findings"]
    assert bt and bt[0]["basis"] == "draft" and bt[0]["why"]["chain"]
    assert "chưa xác minh" in c.post("/api/reasoning", json={**B2, "level": 4}).json()["systems"]["bat_tu"]["text"]


def test_year_and_compare():
    assert c.post("/api/year", json={**B, "to_year": 2024}).json()["bazi"]["annual_pillar"] == "Giáp Thìn"
    d = c.post("/api/compare-hours", json={"a": B, "b": {**B, "hour": 11}}).json()
    assert set(d["bazi_pillars"]) == {"hour"}
