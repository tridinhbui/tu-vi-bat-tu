"""Real calculated charts pinned to the verdict the Phase-1 engine gives each EXPERIMENTAL cách cục (found by scanning 1950-2010 births; DEFINITION v2).
They prove every state is reachable on genuine charts, and that the verdict obeys the state-machine invariants on real data."""
import warnings

import pytest
from fastapi.testclient import TestClient

from tvbt import tuvi
from tvbt.api import app
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.loader import load_experimental
from tvbt.reasoning import engine, facts

warnings.filterwarnings("ignore")
_, FORMS, _ = load_experimental()
BY_ID = {f.id: f for f in FORMS}

REAL_PINS = [
    ('CACH_X_CO_NGUYET_DONG_LUONG', 'bi_pha', (1950, 1, 4, 8, 10, 'male')),
    ('CACH_X_CO_NGUYET_DONG_LUONG', 'hinh_thuc', (1952, 1, 4, 18, 10, 'male')),
    ('CACH_X_CO_NGUYET_DONG_LUONG', 'pha_duoc_cuu', (1950, 9, 4, 4, 10, 'male')),
    ('CACH_X_CO_NGUYET_DONG_LUONG', 'thanh', (1950, 1, 25, 6, 10, 'male')),
    ('CACH_X_CO_NGUYET_DONG_LUONG', 'thanh_thuong', (1950, 1, 4, 0, 10, 'male')),
    ('CACH_X_KHOI_VIET_GIAP_MENH', 'bi_pha', (1952, 2, 4, 20, 10, 'female')),
    ('CACH_X_KHOI_VIET_GIAP_MENH', 'hinh_thuc', (1952, 7, 4, 4, 10, 'female')),
    ('CACH_X_KHOI_VIET_GIAP_MENH', 'pha_duoc_cuu', (1956, 3, 4, 8, 10, 'female')),
    ('CACH_X_KHOI_VIET_GIAP_MENH', 'thanh', (1952, 2, 25, 22, 10, 'male')),
    ('CACH_X_KHOI_VIET_GIAP_MENH', 'thanh_thuong', (1952, 2, 4, 20, 10, 'male')),
    ('CACH_X_MA_DAU_DOI_KIEM', 'bi_pha', (1956, 2, 18, 16, 10, 'male')),
    ('CACH_X_MA_DAU_DOI_KIEM', 'hinh_thuc', (1956, 8, 25, 4, 10, 'male')),
    ('CACH_X_MA_DAU_DOI_KIEM', 'pha_duoc_cuu', (1956, 2, 25, 16, 10, 'female')),
    ('CACH_X_MA_DAU_DOI_KIEM', 'thanh', (1956, 2, 25, 16, 10, 'male')),
    ('CACH_X_MA_DAU_DOI_KIEM', 'thanh_thuong', (1956, 10, 4, 8, 10, 'female')),
    ('CACH_X_NHAT_LE_TRUNG_THIEN', 'bi_pha', (1950, 11, 25, 10, 10, 'male')),
    ('CACH_X_NHAT_LE_TRUNG_THIEN', 'hinh_thuc', (1950, 3, 4, 16, 10, 'male')),
    ('CACH_X_NHAT_LE_TRUNG_THIEN', 'thanh', (1950, 1, 4, 12, 10, 'male')),
    ('CACH_X_NHAT_LE_TRUNG_THIEN', 'thanh_thuong', (1964, 1, 4, 12, 10, 'male')),
    ('CACH_X_NHAT_NGUYET_TINH_MINH', 'bi_pha', (1950, 1, 4, 8, 10, 'male')),
    ('CACH_X_NHAT_NGUYET_TINH_MINH', 'hinh_thuc', (1950, 2, 4, 0, 10, 'male')),
    ('CACH_X_NHAT_NGUYET_TINH_MINH', 'pha_duoc_cuu', (1956, 3, 4, 0, 10, 'male')),
    ('CACH_X_NHAT_NGUYET_TINH_MINH', 'thanh', (1950, 1, 18, 12, 10, 'male')),
    ('CACH_X_NHAT_NGUYET_TINH_MINH', 'thanh_thuong', (1950, 1, 4, 0, 10, 'male')),
    ('CACH_X_SAT_PHA_LIEM_THAM', 'bi_pha', (1950, 1, 11, 8, 10, 'male')),
    ('CACH_X_SAT_PHA_LIEM_THAM', 'hinh_thuc', (1950, 1, 4, 6, 10, 'male')),
    ('CACH_X_SAT_PHA_LIEM_THAM', 'pha_duoc_cuu', (1952, 2, 25, 20, 10, 'male')),
    ('CACH_X_SAT_PHA_LIEM_THAM', 'thanh', (1950, 1, 4, 22, 10, 'male')),
    ('CACH_X_SAT_PHA_LIEM_THAM', 'thanh_thuong', (1950, 1, 4, 14, 10, 'male')),
    ('CACH_X_TAM_KY_GIA_HOI', 'bi_pha', (1954, 7, 11, 8, 10, 'male')),
    ('CACH_X_TAM_KY_GIA_HOI', 'hinh_thuc', (1954, 3, 11, 10, 10, 'male')),
    ('CACH_X_TAM_KY_GIA_HOI', 'pha_duoc_cuu', (1954, 9, 4, 12, 10, 'male')),
    ('CACH_X_TAM_KY_GIA_HOI', 'thanh', (1954, 2, 4, 18, 10, 'male')),
    ('CACH_X_TAM_KY_GIA_HOI', 'thanh_thuong', (1954, 2, 4, 0, 10, 'male')),
    ('CACH_X_THACH_TRUNG_AN_NGOC', 'bi_pha', (1952, 4, 4, 8, 10, 'male')),
    ('CACH_X_THACH_TRUNG_AN_NGOC', 'hinh_thuc', (1950, 2, 18, 16, 10, 'male')),
    ('CACH_X_THACH_TRUNG_AN_NGOC', 'pha_duoc_cuu', (1958, 7, 11, 0, 10, 'male')),
    ('CACH_X_THACH_TRUNG_AN_NGOC', 'thanh', (1970, 6, 11, 12, 10, 'male')),
    ('CACH_X_TU_PHU_DONG_CUNG', 'bi_pha', (1950, 2, 4, 10, 10, 'female')),
    ('CACH_X_TU_PHU_DONG_CUNG', 'hinh_thuc', (1950, 2, 4, 10, 10, 'male')),
    ('CACH_X_TU_PHU_DONG_CUNG', 'thanh', (1950, 9, 25, 2, 10, 'male')),
    ('CACH_X_TU_PHU_DONG_CUNG', 'thanh_thuong', (1950, 2, 25, 0, 10, 'male')),
    ('CACH_X_TU_PHU_VU_TUONG', 'bi_pha', (1950, 1, 4, 20, 10, 'male')),
    ('CACH_X_TU_PHU_VU_TUONG', 'hinh_thuc', (1950, 2, 4, 10, 10, 'male')),
    ('CACH_X_TU_PHU_VU_TUONG', 'pha_duoc_cuu', (1954, 3, 11, 10, 10, 'male')),
    ('CACH_X_TU_PHU_VU_TUONG', 'thanh', (1950, 1, 18, 18, 10, 'male')),
    ('CACH_X_TU_PHU_VU_TUONG', 'thanh_thuong', (1950, 1, 4, 4, 10, 'male')),
]


def verdicts(b):
    c = tuvi.compute(normalize(BirthInput(*b[:5], "Asia/Ho_Chi_Minh", b[5])))
    res = engine.run([], [], facts.tuvi_facts(c), system="tu_vi", formations=FORMS)
    return {d["id"]: d for d in res.formations}


@pytest.mark.parametrize("fid,state,birth", REAL_PINS)
def test_real_chart_pin(fid, state, birth):
    d = verdicts(birth)[fid]
    assert d["state"] == state, d["text"]
    if state == "bi_pha":
        assert d["uncovered_breakers"]
    elif state == "pha_duoc_cuu":
        assert d["breakers"] and not d["uncovered_breakers"] and d["rescuers"]
    elif state in ("thanh", "thanh_thuong"):
        assert d["boosters"] and not d["breakers"]
    elif state == "hinh_thuc":
        assert not d["breakers"]


def test_every_state_is_reached_on_real_charts():
    assert {s for _, s, _ in REAL_PINS} >= {"hinh_thuc", "thanh", "bi_pha", "pha_duoc_cuu"}
    assert {f for f, _, _ in REAL_PINS} == set(BY_ID)


# ---- API: production output is untouched, experimental is strictly opt-in ---------------------------------------------------
BIRTH = dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male")


def test_api_default_has_no_experimental_and_flag_does_not_change_production_systems():
    c = TestClient(app)
    plain = c.post("/api/reasoning", json=BIRTH).json()
    flagged = c.post("/api/reasoning", json={**BIRTH, "experimental": True}).json()
    assert "experimental" not in plain and plain["pack_problems"] == []
    assert flagged["systems"] == plain["systems"]                             # production reading byte-identical with the flag on
    x = flagged["experimental"]
    assert x["status"] == "draft" and "chưa đối chiếu sách" in x["warning"] and x["pack_problems"] == []
    assert len(x["formations"]) == 10 and all("thử nghiệm" in f["text"] or f["state"] in ("khong_hien", "chua_du_du_kien") for f in x["formations"])
    prod_claims = {f["claim"] for s in plain["systems"].values() for f in s["findings"]}
    assert not any(cl.startswith(("cach:", "xr_")) for cl in prod_claims)


def test_api_experimental_formation_cards_have_why_chain():
    c = TestClient(app)
    for b in [(1950, 1, 4, 4, 10, "male"), (1950, 1, 4, 20, 10, "male")]:
        r = c.post("/api/reasoning", json=dict(year=b[0], month=b[1], day=b[2], hour=b[3], minute=b[4], gender=b[5], experimental=True)).json()
        for f in r["experimental"]["findings"]:
            assert f["why"]["chain"] and f["claim"].startswith(("cach:", "xr_"))
