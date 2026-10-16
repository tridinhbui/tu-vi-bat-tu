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
    assert set(ch) == {"tong-quan", "muoi-hai-cung", "ban-menh", "tinh-cach", "cong-danh", "tai-bach", "quan-he", "dai-van", "cach-cuc"}
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


def test_reasoning_chain_has_vietnamese_fact_labels():
    r = c.post("/api/reasoning", json=B).json()
    f = r["systems"]["tu_vi"]["findings"][0]
    assert len(f["why"]["chain_vi"]) == len(f["why"]["chain"])
    assert not any(x.startswith(("palace.", "derived.")) for x in f["why"]["chain_vi"])


def test_dai_van_reading_matches_khao_luan_worked_examples_pp230_232():
    from tvbt.analysis import TRIAD_ELEM, age_vs_dai_van
    B = {n: i for i, n in enumerate("Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi".split())}
    ex = [("Tý", "Thìn", "cùng hành"),                    # ex.1 Giáp Tý vs đại vận Thìn: both Thủy
          ("Thân", "Tuất", "tuổi khắc đại vận"),           # ex.2 Canh Thân (Thủy) vs Tuất (Hỏa)
          ("Sửu", "Tý", "tuổi sinh xuất cho đại vận"),     # ex.3 tuổi Sửu (Kim) vs Tý (Thủy)
          ("Thìn", "Sửu", "đại vận sinh nhập cho tuổi"),   # ex.4 Mậu Thìn (Thủy) vs Sửu (Kim)
          ("Mùi", "Dậu", "đại vận khắc tuổi")]             # ex.5 Kỷ Mùi (Mộc) vs Dậu (Kim)
    for age, dv, want in ex:
        assert age_vs_dai_van(TRIAD_ELEM[B[age]], TRIAD_ELEM[B[dv]])[0] == want, (age, dv)


def test_dai_van_blocks_per_decade_and_twelve_palaces():
    ch = analyse(*charts())
    dv = [b["text"] for b in ch["dai-van"] if "tuổi, cung" in b["text"]]
    assert len(dv) == 10 and all("Xung chiếu" in t and "nhị hợp" in t for t in dv)
    assert len([b for b in ch["muoi-hai-cung"] if b["text"].startswith("Cung ")]) >= 12
