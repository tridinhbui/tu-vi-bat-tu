"""Horary HTTP API: responses serialise, unconfirmed or restricted questions are refused, saved charts recompute identically."""
import json

import pytest
from fastapi.testclient import TestClient

from tvbt.api import app

c = TestClient(app)
M = {"year": 2026, "month": 10, "day": 25, "hour": 9, "minute": 30, "tz": "Asia/Ho_Chi_Minh", "lat": 21.0285, "lon": 105.8542, "place": "Hà Nội"}
F = {"text": "Tôi có được thăng chức không?", "topic": "career", "subtype": "promotion", "confirmed": True}


def test_catalog_and_rules():
    cat = c.get("/api/horary/catalog").json()
    assert set(cat["topics"]) == {"career", "finance", "business", "love", "study", "property", "lost", "travel"}
    rules = c.get("/api/horary/rules").json()["rules"]
    assert len(rules) > 200 and all(r["sources"] for r in rules if r["effect"] not in ("warning",))


def test_classify():
    r = c.post("/api/horary/classify", json={"text": "Em trai tôi có xin được việc không?"}).json()
    assert r["readings"][0]["quesited_house"] == 12 and r["needs_confirmation"]


@pytest.mark.parametrize("topic,sub", [("career", "promotion"), ("lost", "lost_item"), ("property", "buy"), ("travel", "short_trip"),
                                       ("business", "buy_sell"), ("love", "marriage"), ("finance", "gain"), ("study", "admission")])
def test_judge_serialises_for_every_topic(topic, sub):
    r = c.post("/api/horary/judge", json={"moment": M, "frame": {**F, "topic": topic, "subtype": sub}})
    assert r.status_code == 200, r.text[:300]
    body = r.json()
    json.dumps(body)
    assert body["reading"]["quick"]["title"] == body["judgment"]["verdict"]["vi"]


def test_unconfirmed_and_restricted_are_refused():
    assert c.post("/api/horary/judge", json={"moment": M, "frame": {**F, "confirmed": False}}).status_code == 400
    r = c.post("/api/horary/judge", json={"moment": M, "frame": {**F, "text": "Mẹ tôi phẫu thuật có thành công không?"}})
    assert r.status_code == 422 and r.json()["detail"]["restricted"][0]["kind"] == "health"


def test_bad_inputs_are_422_with_a_reason():
    assert c.post("/api/horary/judge", json={"moment": {**M, "month": 2, "day": 30}, "frame": F}).status_code == 422
    assert c.post("/api/horary/judge", json={"moment": {**M, "tz": "Mars/Olympus"}, "frame": F}).status_code == 422
    assert c.post("/api/horary/judge", json={"moment": {**M, "tz": "Europe/London", "month": 3, "day": 29, "hour": 1}, "frame": F}).status_code == 422
    assert c.post("/api/horary/chart", json={**M, "lat": 70.0, "house_system": "regiomontanus"}).status_code == 422
    assert c.post("/api/horary/judge", json={"moment": M, "frame": {**F, "topic": "astrology"}}).status_code == 422


def test_saved_question_recomputes_the_same_chart():
    a = c.post("/api/horary/judge", json={"moment": M, "frame": F}).json()
    b = c.post("/api/horary/judge", json={"moment": M, "frame": F, "fingerprint": a["fingerprint"]}).json()
    assert b["unchanged"] is True and b["reading"] == a["reading"]
    d = c.post("/api/horary/judge", json={"moment": M, "frame": F, "fingerprint": "0000000000000000"}).json()
    assert d["unchanged"] is False
