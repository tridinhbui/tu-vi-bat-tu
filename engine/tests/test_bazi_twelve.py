"""十二神 (八字真宗 pp.39-42): god numbering and the stem 'borrowed branch' table; table p.41 is reproduced for spot checks."""
from fastapi.testclient import TestClient

from tvbt import bazi, bazi_twelve as bt, calendar_core as cc
from tvbt.api import app


def test_numbering_matches_table_p41():
    # for 子 year the gods sit on 子 丑 寅 卯 … 亥 in order 1..12; for 丑 year they start from 丑 (p.41 rows)
    assert [bt.god_of(b, 0)["no"] for b in range(12)] == list(range(1, 13))
    assert bt.god_of(1, 1)["god"] == "Thái Tuế" and bt.god_of(2, 1)["god"] == "Thanh Long"
    assert bt.god_of(0, 1)["no"] == 12 and bt.god_of(0, 1)["god"] == "Bệnh Phù"          # 子 in a 丑 year


def test_stem_borrowed_branch_and_stem_table_row_p41():
    assert bt.STEM_BORROW == {0: 2, 1: 3, 2: 5, 3: 6, 4: 10, 5: 1, 6: 8, 7: 9, 8: 11, 9: 0}      # 甲寅 乙卯 丙巳 丁午 戊戌 己丑 庚申 辛酉 壬亥 癸子
    # p.41 row 甲寅 reads 3 2 1 12 11 10 9 8 7 6 5 4 for flow years 子..亥
    assert [bt.god_of(2, y)["no"] for y in range(12)] == [3, 2, 1, 12, 11, 10, 9, 8, 7, 6, 5, 4]
    # p.41 row 癸子 reads 1 12 11 10 9 8 7 6 5 4 3 2
    assert [bt.god_of(0, y)["no"] for y in range(12)] == [1, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]


def test_ratings_follow_the_book_marks():
    marks = {n: g[1] for n, g in zip(range(1, 13), bt.GODS)}
    assert [marks[i] for i in (2, 4, 10)] == ["tot"] * 3 and [marks[i] for i in (3, 7, 8, 9)] == ["xau_lon"] * 4
    assert [marks[i] for i in (5, 6, 11, 12)] == ["xau_nho"] * 4 and marks[1] == "trung"


def test_chart_has_seven_columns_and_luck_god():
    nb = cc.normalize(cc.BirthInput(1990, 5, 17, 8, 30, "Asia/Ho_Chi_Minh", "male"))
    res = bt.twelve_gods(bazi.compute(nb), 6, "Giáp Tý")
    assert set(res["columns"]) == {"year", "month", "day", "hour", "thai_yuan", "ming_gong", "shen_gong"}
    assert res["luck"]["branch_god"]["no"] == (0 - 6) % 12 + 1 and sum(res["tally"].values()) == 7


def test_api_endpoint():
    c = TestClient(app)
    r = c.post("/api/twelve-gods", json={"year": 1990, "month": 5, "day": 17, "hour": 8, "minute": 30, "tz": "Asia/Ho_Chi_Minh", "gender": "male", "to_year": 2026})
    assert r.status_code == 200 and r.json()["year"] == 2026 and r.json()["flow_year_branch"] == "Ngọ"
