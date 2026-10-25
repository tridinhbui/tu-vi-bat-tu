"""The /api/west routes answer with plain JSON (no numpy scalars) and refuse bad input with 422."""
from fastapi.testclient import TestClient

from tvbt.api import app

c = TestClient(app)
B = {"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "lat": 10.8231, "lon": 106.6297, "tz": "Asia/Ho_Chi_Minh"}


def test_every_route_answers():
    assert c.get("/api/west/places", params={"q": "ha noi"}).json()["results"][0]["name"] == "Hà Nội"
    assert c.post("/api/west/chart", json={"birth": B}).json()["angles"]["asc"]["sign"] == "leo"
    tr = c.post("/api/west/transits", json={"birth": B, "start": "2026-01-01", "end": "2026-04-01", "transiting": ["moon", "mars", "saturn"]})
    assert tr.status_code == 200 and tr.json()["events"] and tr.json()["sky"]
    assert c.post("/api/west/progressions", json={"birth": B, "when": "2026-10-25"}).status_code == 200
    assert c.post("/api/west/profections", json={"birth": B, "age": 36}).json()["current"]["lord"] == "sun"
    assert c.post("/api/west/solar-return", json={"birth": B, "year": 2026}).status_code == 200
    rd = c.post("/api/west/reading", json={"birth": B, "mode": "overview", "when": "2026-10-25"})
    assert rd.status_code == 200 and rd.json()["chapters"]
    sy = c.post("/api/west/synastry", json={"a": B, "b": {**B, "year": 1992, "hour": None, "minute": None}})
    assert sy.status_code == 200 and sy.json()["synastry"]["overlays"]["b_in_a"] is not None


def test_bad_input_is_422():
    assert c.post("/api/west/chart", json={"birth": {**B, "tz": "Mars/Base"}}).status_code == 422
    assert c.post("/api/west/chart", json={"birth": {**B, "year": 2021, "month": 3, "day": 14, "hour": 2, "minute": 30, "tz": "America/New_York"}}).status_code == 422
    assert c.post("/api/west/transits", json={"birth": B, "start": "2026-01-01", "end": "2030-01-01"}).status_code == 422
    assert c.post("/api/west/profections", json={"birth": {**B, "hour": None, "minute": None}}).status_code == 422
