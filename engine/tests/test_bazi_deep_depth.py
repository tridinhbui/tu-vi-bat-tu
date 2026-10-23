"""bazi_deep.depth (2026-10-22): the 'why' facts the reader prose voices. They take apart what the verified methods computed; these tests pin
that the parts add up to the verdict and that the page-transcribed data (the điều hậu notes, the dụng thần reasons) stay well formed."""
import json

import pytest

from tvbt.bazi_deep import depth, tvh_score
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DATA


def _tvh(names: str, days=None):
    return tvh_score.score(ChartView.from_names(names, days))


def test_score_parts_add_up_to_the_40_percent_verdict():
    for names in ("Tân Tỵ / Tân Sửu / Đinh Sửu / Nhâm Dần", "Canh Tuất / Mậu Tý / Tân Mùi / Giáp Ngọ", "Tân Hợi / Quý Tỵ / Kỷ Dậu / Kỷ Tỵ",
                  "Mậu Dần / Ất Mão / Quý Hợi / Canh Thân", "Nhâm Tuất / Nhâm Dần / Đinh Sửu / Giáp Thìn"):
        t = _tvh(names, 20)
        s = depth.score(ChartView.from_names(names, 20), t)
        assert s["own"] == pytest.approx(t["own_share"] * s["total"], abs=0.2)
        assert (s["gap"] >= 0) == t["dm_strong"]
        assert s["need"] == pytest.approx(0.4 * s["total"], abs=0.1)
        # heaven + earth is the total before the month's ±1/5
        assert sum(e["heaven"] + e["earth"] for e in s["elements"]) == pytest.approx(sum(t["totals_before_lenh"].values()), abs=0.5)


def test_stem_combine_reasons_follow_p336():
    # Đinh–Nhâm hợp Mộc in a Sửu month: Sửu holds no Mộc, so no hóa, and the controlled side (Đinh) is the one weakened
    v = ChartView.from_names("Tân Tỵ / Tân Sửu / Đinh Sửu / Nhâm Dần", 20)
    st = depth.stems(v, tvh_score.score(v))
    dm = next(x for x in st["stems"] if x["pillar"] == "day")
    assert dm["hop"]["outcome"] == "khong_hoa" and dm["hop"]["victim"] is True and dm["hop"]["el"] == "Mộc"
    assert {r["stem"] for r in st["dm_roots"]} == {"Bính", "Giáp"}
    # the same pair in a Dần month (Mộc) hóa: TVH p.336 condition 1
    v2 = ChartView.from_names("Nhâm Tuất / Nhâm Dần / Đinh Sửu / Giáp Thìn", 20)
    st2 = depth.stems(v2, tvh_score.score(v2))
    assert st2["hua_day"] == "Mộc"
    assert next(x for x in st2["stems"] if x["pillar"] == "day")["hop"] == {"with": "month", "with_stem": "Nhâm", "el": "Mộc", "outcome": "hoa", "why": "lenh", "victim": None}


def test_roots_use_only_the_branch_combinations_the_score_took():
    # Tỵ (month) – Dậu (day) is the bán tam hợp that hóa Kim; the hour Tỵ stays itself and roots the Kỷ day master (Bính, Mậu)
    v = ChartView.from_names("Tân Hợi / Quý Tỵ / Kỷ Dậu / Kỷ Tỵ", 20)
    st = depth.stems(v, tvh_score.score(v))
    assert {(r["pillar"], r["stem"]) for r in st["dm_roots"]} == {("hour", "Bính"), ("hour", "Mậu")}


def test_useful_god_reason_and_health():
    v = ChartView.from_names("Tân Tỵ / Tân Sửu / Đinh Sửu / Nhâm Dần", 3)
    t = tvh_score.score(v)
    cct = {"status": "ap_dung", "dm": "nhược", "dominant": "Tai", "yong": ["Ti"], "yong_alternatives": ["Ti"], "van_tot": ["Ti"], "van_xau": ["Tai", "QuanSat", "ThucThuong"]}
    y = depth.yong(v, t, cct, {})
    assert y["group"] == "Tỉ Kiếp" and y["el"] == "Hỏa" and "chế ngự Tài" in y["why"]["text"]
    assert y["ky"]["group"] == "Quan Sát" and y["hy"]["group"] == "Ấn"
    assert {"kind": "khac_yong", "part": "stem", "pillar": "hour", "who": "Nhâm"} in y["natal"]
    # a luck pillar Đinh Dậu: the Đinh stem is the useful god, bound by the natal hour Nhâm (p.382: hợp dụng thần)
    tc = depth.touches(v, 3, 9, "Hỏa")
    assert {"kind": "yong_bi_hop", "part": "stem", "who": "Đinh", "target": "hour", "target_stem": "Nhâm"} in tc
    assert depth.luck_reason(v, t, "Thực Thương", "xau", y)[0]["key"] == "weak_ThucThuong"
    assert depth.halves(2033) == {"stem": [2033, 2037], "branch": [2038, 2042], "src": "TVH p.382"}


def test_dieuhau_notes_cover_every_cell_and_resolve_references():
    d = json.loads((DATA / "tvh_dieuhau.json").read_text("utf-8"))
    notes = d["notes_text"]
    assert sum(len(v) for v in notes.values()) == 120
    for b, row in notes.items():
        for s, n in row.items():
            assert n.get("say") or n.get("ref") or not n["text"] or n["text"].startswith(("Là cách", "Nếu bính", "Không có giáp", "Có nhiều")), (b, s, n)
            assert not any(w in (n.get("say") or "") for w in ("tầm thường", "quý cách")), (b, s)
    # Đinh in Sửu says "như tháng mười": the reading follows the Hợi note
    v = ChartView.from_names("Tân Tỵ / Tân Sửu / Đinh Sửu / Nhâm Dần")
    n = depth.dh_note(v, tvh_score.score(v))
    assert n["via"] == "Hợi" and n["say"].startswith("Giáp là chủ, Canh là phụ")


def test_mechanism_rows_match_the_dungthan_table():
    mech = json.loads((DATA / "tvh_mechanism.json").read_text("utf-8"))
    dt = json.loads((DATA / "tvh_dungthan.json").read_text("utf-8"))["rows"]
    first = {(r["cach"], r["dm"], r["dom"]): r["yong"] for r in dt}
    # every reason row names a (yong, dom, side) the table actually has
    for r in mech["dungthan_why"]["rows"]:
        assert any(r["yong"] in y and k[2] == r["dom"] and k[1] == r["dm"] for k, y in first.items()), r


def _owner():
    from tvbt.api import BirthReq
    return BirthReq(year=2002, month=1, day=9, hour=4, minute=30, gender="male", to_year=2026, dignity_school="khao_luan")


def test_owner_review_cach_status_is_one_everywhere():
    """2026-10-22: the analysis text and the reading give the cách ONE status (xác lập một phần), never 'không xác định cách cục'."""
    from tvbt.api import analysis_endpoint, chart_facts
    txt = " ".join(b["text"] for b in analysis_endpoint(_owner())["chapters"]["cach-cuc"])
    assert "không xác định cách cục" not in txt and "chưa có quy tắc cách cục" not in txt
    assert "cách Thiên Tài; trạng thái: xác lập một phần" in txt and "đúng nếu cách Thiên Tài được xác lập" in txt
    assert chart_facts(_owner())["bazi"]["deep"]["cach_tvh"]["verification"] == "partial"


def test_owner_review_years_to_press_on_follow_the_year_verdict():
    """2026-10-22: a luck pillar's 'nên tiến' years are those whose own verdict is thuận / khá thuận, with no head-on clash with the luck;
    2027 (Đinh Mùi: Đinh good, Mùi bad, Mùi hình + phá the luck branch Tuất) is no longer listed under Mậu Tuất."""
    from tvbt.api import chart_facts
    d = chart_facts(_owner())["bazi"]["deep"]
    mt = next(lk for lk in d["luck"] if lk["pillar"] == "Mậu Tuất")
    assert [g["year"] for g in mt["good_years"]] == [2025, 2026]
    assert all(g["verdict"] in ("thuan", "kha_thuan") for lk in d["luck"] for g in lk["good_years"])
    y27 = next(y for y in d["years"] if y["year"] == 2027)
    assert {e["kind"] for e in y27["vs_luck"]} == {"branch_penalty", "branch_destroy"}
    assert y27["reconcile"]["verdict"] == "co_dieu_kien" and y27["reconcile"]["agree"] == "tron"
