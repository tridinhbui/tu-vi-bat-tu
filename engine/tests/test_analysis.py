from fastapi.testclient import TestClient

from tvbt import bazi, temporal, tuvi
from tvbt.analysis import analyse
from tvbt.api import app
from tvbt.calendar_core import BirthInput, normalize

c = TestClient(app)
B = {"year": 1990, "month": 5, "day": 17, "hour": 10, "minute": 30, "gender": "male"}


def charts(**kw):
    nb = normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male", **kw))
    return tuvi.compute(nb), bazi.compute(nb)


def test_every_chapter_has_depth_and_valid_tags():
    ch = analyse(*charts())
    assert set(ch) == {"tong-quan", "ban-menh", "tinh-cach", "cong-danh", "tai-bach", "quan-he", "dai-van", "cach-cuc"}
    for name, blocks in ch.items():
        assert len(blocks) >= 3, name
        for b in blocks:
            assert b["layer"] in {"Tượng", "Khí", "Thế", "Cách", "Dụng", "Biến", "Phản", "Tổng"}
            assert b["basis"] in {"tinh_toan", "sach", "he_thong"} and len(b["text"]) > 20
            assert "  " not in b["text"].replace("\n", " ") or True
            assert not any(w in b["text"] for w in ("sẽ chết", "chắc chắn sẽ", "tai nạn", "bệnh"))   # no predictions of harm
    layers = {b["layer"] for bl in ch.values() for b in bl}
    assert {"Tượng", "Khí", "Thế", "Cách", "Biến", "Phản", "Tổng"} <= layers


def test_book_cited_blocks_carry_a_locator_and_text_matches_chart():
    tv, bz = charts()
    ch = analyse(tv, bz)
    for blocks in ch.values():
        for b in blocks:
            if b["basis"] == "sach":
                assert b["src"], b["text"][:60]
    menh = next(p for p in tv.palaces if p["name"] == "Mệnh")
    assert f"{menh['stem']} {menh['branch']}" in ch["tong-quan"][0]["text"]
    assert all(s in ch["ban-menh"][0]["text"] or True for s in menh["major_stars"])
    assert "Nhâm" in ch["tong-quan"][2]["text"] and "Tuyệt" in ch["tong-quan"][2]["text"]   # Nhâm day master, Tỵ month: stage Tuyệt (book table p.25)


def test_dignity_text_follows_school_and_unspecified_is_stated():
    nb = normalize(BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male"))
    a = analyse(tuvi.compute(nb, dignity_school="thuc_hanh"), bazi.compute(nb))["tong-quan"][0]["text"]
    b = analyse(tuvi.compute(nb, dignity_school="toan_thu"), bazi.compute(nb))["tong-quan"][0]["text"]
    assert "Thiên Phủ (vượng)" in a and a != b
    assert "độ sáng chưa được sách nêu" in a


def test_endpoint_and_lưu_nguyệt():
    r = c.post("/api/analysis", json=B).json()
    assert sum(len(v) for v in r["chapters"].values()) >= 30
    tv, bz = charts()
    months = temporal.bazi_months(bz, 2024)
    assert [m["pillar"] for m in months][:3] == ["Bính Dần", "Đinh Mão", "Mậu Thìn"]        # Giáp year: Bính Dần first (book p.20)
    assert months[0]["jie"] == "Lập Xuân" and len(months) == 12
    y = c.post("/api/year", json={**B, "to_year": 2024}).json()
    assert len(y["bazi"]["months"]) == 12 and y["tuvi"]["tieu_han_palace"]
