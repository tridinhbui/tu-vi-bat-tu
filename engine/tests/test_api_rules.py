from fastapi.testclient import TestClient

from tvbt.api import app

c = TestClient(app)


def test_rule_library_readonly_and_valid():
    r = c.get("/api/rules").json()
    assert r["problems"] == [] and len(r["rules"]) >= 60 and any(s["verified"] for s in r["sources"])
    assert c.post("/api/rules", json={}).status_code == 405 and c.delete("/api/rules").status_code == 405
    d = c.get("/api/dignity").json()
    assert len(d["stars"]) == 14 and "Thiên Cơ" in d["stars"]


def test_rule_tester_validates_and_dry_runs():
    rule = {"id": "T1", "system": "tu_vi", "schoolId": "x", "category": "c", "description": "d",
            "conditions": {"all": [{"fact": "palace.name", "value": "Mệnh"}]},
            "consequences": [{"kind": "finding", "claim": "k", "effect": "neutral"}], "sourceIds": [], "subject": "palace"}
    b = {"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male"}
    ok = c.post("/api/rules/test", json={"rule": rule, "birth": b}).json()
    assert ok["valid"] and ok["fired_on"] == ["palace:Mệnh"]
    bad = {**rule, "conditions": {"fact": "palace.name", "operator": "eval", "value": "__import__('os')"}}
    j = c.post("/api/rules/test", json={"rule": bad, "birth": b}).json()
    assert not j["valid"] and any("operator" in p for p in j["problems"])
    assert c.post("/api/rules/test", json={"rule": {"nonsense": 1}, "birth": b}).status_code == 422
    v = {**rule, "reviewStatus": "verified", "sourceIds": ["SRC_TOAN_THU"]}
    assert not c.post("/api/rules/test", json={"rule": v, "birth": b}).json()["valid"]   # unverified source can't back 'verified'
