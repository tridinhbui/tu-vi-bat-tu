from fastapi.testclient import TestClient

from tvbt import dignity, tuvi
from tvbt.api import app
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import BRANCHES_VI

c = TestClient(app)
B = {"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male"}


def test_schools_disagree_and_are_kept_separate():
    assert dignity.dignity("Tử Vi", "Tý", "thuc_hanh") == "miếu" and dignity.dignity("Tử Vi", "Tý", "toan_thu") == "vượng"
    assert dignity.dignity("Thái Dương", "Ngọ", "thuc_hanh") == "vượng" and dignity.dignity("Thái Dương", "Ngọ", "toan_thu") == "miếu"
    d = dignity.compare(list(BRANCHES_VI))
    assert len(d) > 20 and all(x["thuc_hanh"] != x["toan_thu"] for x in d)
    # cells both books agree on stay out of the disagreement list
    assert not any(x["star"] == "Thiên Cơ" and x["branch"] in ("Tý", "Ngọ", "Sửu", "Mùi") for x in d)


def test_chart_uses_chosen_school_and_api_flags_mixing():
    nb = normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male"))
    a = tuvi.compute(nb, dignity_school="thuc_hanh"); b = tuvi.compute(nb, dignity_school="toan_thu")
    assert [p["stars"] for p in a.palaces] == [p["stars"] for p in b.palaces]          # placement identical
    assert a.school["dignity_school"] == "thuc_hanh" and b.school["dignity_school"] == "toan_thu"
    r = c.post("/api/reasoning", json={**B, "dignity_school": "toan_thu"}).json()
    assert r["mixed_school_warning"] is True
    assert c.post("/api/reasoning", json={**B, "dignity_school": "nope"}).status_code == 422
    assert c.get("/api/dignity/compare").json()["count"] > 20
