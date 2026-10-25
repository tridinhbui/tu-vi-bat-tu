"""Kinh Dịch / Mai Hoa engine (tvbt.kinh_dich), checked against the saved sources rather than against its own tables:
the 'X下Y上' header of every 周易 page (WEB:zh_zhouyi), the worked examples printed in 梅花易數 卷一, Chu Hy's 考變占 clauses, and every
quote the engine cites (tools/book_text.quote_on_page)."""
import itertools
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pytest

from tvbt.kinh_dich import coins, core, doc_hao, mai_hoa, tables

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from book_text import quote_on_page  # noqa: E402

ZHOUYI = {c["chapter"]: c["text"] for c in json.loads((ROOT / "engine/data/sources_web/zh_zhouyi.json").read_text("utf-8"))["chapters"]}
HAN_TRIGRAM = {v: k for k, v in tables.TRIGRAM_HAN.items()}


@pytest.mark.parametrize("n", range(1, 65))
def test_upper_lower_match_the_zhouyi_page(n):
    text = ZHOUYI[f"周易/{tables.HEX_HAN[n]}"]
    m = re.search(r"([乾坤震巽坎離艮兌])下([乾坤震巽坎離艮兌])上", re.sub(r"-\{|\}-", "", text))
    assert m, n
    h = core.from_hexagram(n)["ban"]
    assert (h["lower"], h["upper"]) == (HAN_TRIGRAM[m.group(1)], HAN_TRIGRAM[m.group(2)])
    assert re.search(rf"第[一二三四五六七八九十]+卦", text)


def test_hexagram_lines_are_unique_and_complete():
    seen = {tuple(core.from_hexagram(n)["lines"]) for n in range(1, 65)}
    assert len(seen) == 64


@pytest.mark.parametrize("n", range(1, 65))
def test_every_moving_mask(n):
    base = core.from_hexagram(n)
    for mask in range(64):
        moving = [p for p in range(1, 7) if mask >> (p - 1) & 1]
        c = core.from_hexagram(n, moving)
        assert c["ban"]["number"] == n and c["moving"] == moving
        x = c["lines"]
        assert c["ho"]["lines"] == list(x[1:4] + x[2:5])
        if moving:
            back = core.flip(c["bien"]["lines"], moving)
            assert core.hexagram(back)["number"] == n
            assert sum(a != b for a, b in zip(c["bien"]["lines"], x)) == len(moving)
        else:
            assert c["bien"] is None
        r = doc_hao.resolve(c)
        for ref in [r["main"], *r["also"]]:
            assert 1 <= ref["hexagram"] <= 64
            assert ref["kind"] in ("thoan", "hao", "dung")
            if ref["kind"] == "hao":
                assert 1 <= ref["hao"] <= 6
            if ref["kind"] == "dung":
                assert ref["hexagram"] in (1, 2) and len(moving) == 6
    assert base["moving"] == []


def test_positions_follow_the_preface():
    h = core.from_hexagram(63)["hao"]           # Ký Tế: every line chính, every pair ứng
    assert all(x["chinh"] for x in h) and all(x["ung"] for x in h)
    h = core.from_hexagram(64)["hao"]           # Vị Tế: no line chính, every pair ứng
    assert not any(x["chinh"] for x in h) and all(x["ung"] for x in h)
    h = core.from_hexagram(1)["hao"]            # Kiền: no ứng
    assert not any(x["ung"] for x in h)
    assert [x["trung"] for x in h] == [False, True, False, False, True, False]
    assert [x["han"] for x in core.from_hexagram(2)["hao"]] == ["初六", "六二", "六三", "六四", "六五", "上六"]
    assert [x["han"] for x in h] == ["初九", "九二", "九三", "九四", "九五", "上九"]


def test_coin_faces():
    assert [coins.toss_value(f) for f in (["lung", "chu", "chu"], ["lung", "lung", "chu"], ["lung"] * 3, ["chu"] * 3)] == [7, 8, 9, 6]
    c = core.cast(coins.values_from_tosses([["chu"] * 3] + [["lung", "chu", "chu"]] * 5))
    assert c["moving"] == [1] and c["ban"]["number"] == 44 and c["bien"]["number"] == 1     # Cấu, hào 1 động -> Kiền
    with pytest.raises(ValueError):
        coins.toss_value(["lung", "chu"])


def _main(n, moving):
    r = doc_hao.resolve(core.from_hexagram(n, moving))
    return r["main"], r["also"]


def test_chu_hy_rules():
    assert _main(11, []) == ({"hexagram": 11, "kind": "thoan"}, [])
    assert _main(11, [3]) == ({"hexagram": 11, "kind": "hao", "hao": 3}, [])
    assert _main(11, [2, 5]) == ({"hexagram": 11, "kind": "hao", "hao": 5}, [{"hexagram": 11, "kind": "hao", "hao": 2}])
    bien_123 = core.from_hexagram(11, [1, 2, 3])["bien"]["number"]
    assert _main(11, [1, 2, 3]) == ({"hexagram": 11, "kind": "thoan"}, [{"hexagram": bien_123, "kind": "thoan"}])
    bien_456 = core.from_hexagram(11, [4, 5, 6])["bien"]["number"]
    assert _main(11, [4, 5, 6]) == ({"hexagram": bien_456, "kind": "thoan"}, [{"hexagram": 11, "kind": "thoan"}])
    b = core.from_hexagram(11, [1, 2, 3, 4])["bien"]["number"]
    assert _main(11, [1, 2, 3, 4]) == ({"hexagram": b, "kind": "hao", "hao": 5}, [{"hexagram": b, "kind": "hao", "hao": 6}])
    b = core.from_hexagram(11, [1, 2, 3, 4, 6])["bien"]["number"]
    assert _main(11, [1, 2, 3, 4, 6]) == ({"hexagram": b, "kind": "hao", "hao": 5}, [])
    assert _main(1, [1, 2, 3, 4, 5, 6]) == ({"hexagram": 1, "kind": "dung"}, [])
    assert _main(2, [1, 2, 3, 4, 5, 6]) == ({"hexagram": 2, "kind": "dung"}, [])
    assert _main(11, [1, 2, 3, 4, 5, 6]) == ({"hexagram": 12, "kind": "thoan"}, [])


def test_three_lines_split_ten_and_ten():
    masks = list(itertools.combinations(range(1, 7), 3))
    by_ban = [m for m in masks if _main(30, list(m))[0]["hexagram"] == 30]
    assert len(masks) == 20 and len(by_ban) == 10 and all(1 in m for m in by_ban)


def test_book_example_guan_mei():
    """卷一 觀梅占: 辰年五數，十二月十二數，十七日十七數 … 加申時九數 … 餘一為動爻，是為澤火革。初爻變咸，互見乾巽。"""
    assert quote_on_page("WEB:zh_meihua", "梅花易數/卷一", "初爻變咸，互見乾巽")
    r = mai_hoa.by_time(5, 12, 17, 9)
    assert (r["ban"]["han"], r["moving"], r["bien"]["han"]) == ("革", 1, "咸")
    assert (r["ho"]["upper"], r["ho"]["lower"]) == ("Kiền", "Tốn")
    assert r["the"]["trigram"] == "Đoài" and r["dung"]["trigram"] == "Ly"          # 右兌金為體，離火克之
    assert r["relations"]["dung"] == "khac_the" and r["relations"]["bien"] == "sinh_the"   # 幸變為艮土，兌金得生


def test_book_example_mu_dan():
    """卷一 牡丹占: 巳年六數，三月三數，十六日十六數 … 卯時四數 … 得天風姤 … 得五爻動，變鼎卦，互見重乾。"""
    assert quote_on_page("WEB:zh_meihua", "梅花易數/卷一", "得五爻動，變鼎卦，互見重乾")
    r = mai_hoa.by_time(6, 3, 16, 4)
    assert (r["ban"]["han"], r["moving"], r["bien"]["han"], r["ho"]["han"]) == ("姤", 5, "鼎", "乾")
    assert r["the"]["trigram"] == "Tốn" and r["relations"]["dung"] == "khac_the"    # 巽木為體，乾金克之


def test_book_example_knocks():
    """卷一 鄰夜扣門借物占: 以一聲屬乾為上卦，以五聲屬巽為下卦 … 加酉時數共得十六數 … 得天風姤。第四爻變巽卦，互見重乾。"""
    r = mai_hoa.by_sound(1, 10, second=5)
    assert (r["ban"]["han"], r["moving"], r["ho"]["han"]) == ("姤", 4, "乾")
    assert r["bien"]["upper"] == "Tốn"                                            # 第四爻變巽卦


def test_remainders():
    assert mai_hoa.trigram_of_number(8) == "Khôn" and mai_hoa.trigram_of_number(16) == "Khôn" and mai_hoa.trigram_of_number(9) == "Kiền"
    assert mai_hoa.moving_of_number(12) == (6, True) and mai_hoa.moving_of_number(43) == (1, False)
    assert mai_hoa.by_time(1, 1, 4, 6)["notes"][0] == mai_hoa.HE_THONG_SIX       # 12 chia hết cho 6


def test_kien_khon_have_no_ho():
    r = mai_hoa.by_object_direction("Kiền", "tay_bac", 1)                         # Thuần Kiền, hào (1+1+1)=3
    assert r["ban"]["number"] == 1 and r["ho_from"] == "bien"
    b = r["bien"]["lines"]
    assert r["ho"]["lines"] == list(b[1:4] + b[2:5])


def test_hau_thien_uses_hao_text_and_tien_thien_numbers():
    r = mai_hoa.by_object_direction("Cấn", "nam", 3)                             # Cấn 7 + Ly 3 + 3 = 13 -> hào 1
    assert (r["upper"], r["lower"], r["moving"], r["use_hao_text"]) == ("Cấn", "Ly", 1, True)
    assert mai_hoa.by_count(7, 3)["use_hao_text"] is False


def test_methods():
    r = mai_hoa.by_count(10, 5)                       # 10 % 8 = 2 -> Đoài, giờ 5 -> Tốn, 15 % 6 = 3
    assert (r["upper"], r["lower"], r["moving"]) == ("Đoài", "Tốn", 3)
    r = mai_hoa.by_sound(3, 4)                        # 3 -> Ly, 7 -> Cấn, 7 % 6 = 1
    assert (r["upper"], r["lower"], r["moving"]) == ("Ly", "Cấn", 1)
    r = mai_hoa.by_words(13)                          # 6 trên, 7 dưới: Khảm, Cấn; 13 % 6 = 1
    assert (r["upper"], r["lower"], r["moving"]) == ("Khảm", "Cấn", 1)
    r = mai_hoa.by_zhang_chi(2, 5)                    # Đoài, Tốn, 7 -> 1
    assert (r["upper"], r["lower"], r["moving"]) == ("Đoài", "Tốn", 1)
    r = mai_hoa.by_chi_cun(3, 4, 2)                   # Ly, Chấn, 9 -> 3
    assert (r["upper"], r["lower"], r["moving"]) == ("Ly", "Chấn", 3)
    with pytest.raises(ValueError):
        mai_hoa.by_words(5)


def test_time_inputs():
    assert [mai_hoa.hour_branch_of(h) for h in (23, 0, 1, 2, 11, 12, 22)] == [1, 1, 2, 2, 7, 7, 12]
    t = mai_hoa.time_inputs(datetime(2026, 2, 17, 9, 0))                # Tết Bính Ngọ
    assert (t["month"], t["day"], t["year_branch_vi"], t["hour_branch_vi"]) == (1, 1, "Ngọ", "Tỵ")
    t = mai_hoa.time_inputs(datetime(2026, 2, 16, 23, 30))              # 23:30 the evening before: giờ Tý of Tết
    assert (t["month"], t["day"], t["hour_branch"]) == (1, 1, 1)
    t = mai_hoa.time_inputs(datetime(2026, 2, 16, 22, 30))
    assert (t["month"], t["year_branch_vi"]) == (12, "Tỵ")


def test_strength_follows_the_season_tables():
    assert mai_hoa.strength("Chấn", 1) == "vuong" and mai_hoa.strength("Khôn", 1) == "suy"
    assert mai_hoa.strength("Khảm", 12) == "suy" and mai_hoa.strength("Cấn", 6) == "vuong" and mai_hoa.strength("Ly", 7) == "binh"


def _cites():
    out = [tables.TIEN_THIEN_CITE, tables.ELEMENT_CITE, tables.SINH_KHAC_CITE, tables.VUONG_CITE, tables.SUY_CITE, tables.DIRECTION_CITE,
           tables.RANK_CITE, tables.CHINH_CITE, tables.TRUNG_CITE, tables.UNG_CITE, tables.UNG_POLARITY_CITE, tables.VALUE_CITE,
           coins.COIN_CITE, coins.FACES_CITE]
    out += [c for cs in doc_hao.CITES.values() for c in cs]
    out += [v for k, v in vars(mai_hoa).items() if k.startswith("C_")]
    out += [o["cite"] for n in range(7) for o in doc_hao.other_schools(n)]
    return out


def test_other_schools_by_count():
    assert [o["school"] for o in doc_hao.other_schools(2)] == ["trinh_hoi", "han_bang_ky"]
    assert [o["school"] for o in doc_hao.other_schools(1)] == ["trinh_hoi"]


@pytest.mark.parametrize("c", _cites(), ids=lambda c: c["quote"][:16])
def test_every_cited_quote_is_in_its_source(c):
    assert quote_on_page(c["book"], c["chapter"], c["quote"])


def test_api_routes():
    from fastapi.testclient import TestClient

    from tvbt.api import app
    c = TestClient(app)
    r = c.post("/api/kinh-dich/cast", json={"tosses": [["chu"] * 3] + [["lung", "chu", "chu"]] * 5})
    assert r.status_code == 200 and r.json()["ban"]["number"] == 44
    assert r.json()["reading_rule"]["main"] == {"hexagram": 44, "kind": "hao", "hao": 1}
    r = c.post("/api/kinh-dich/cast", json={"hexagram": 11, "moving": [2, 5]})
    assert r.json()["reading_rule"]["main"]["hao"] == 5
    assert c.post("/api/kinh-dich/cast", json={"values": [6, 7]}).status_code == 422
    assert c.post("/api/kinh-dich/cast", json={"values": [7] * 6, "hexagram": 1}).status_code == 422
    r = c.post("/api/mai-hoa/cast", json={"method": "thoi_gian", "moment": "2026-10-25T15:30", "year_branch": 5, "lunar_month": 12,
                                          "lunar_day": 17, "hour_branch": 9})
    assert r.json()["ban"]["han"] == "革" and r.json()["steps"][2]["expr"] == "43 chia 6 dư 1"
    r = c.post("/api/mai-hoa/cast", json={"method": "thoi_gian", "moment": "2026-10-25T15:30"})
    assert r.status_code == 200 and r.json()["inputs"]["month"] == 9 and mai_hoa.TIME_NOTE in r.json()["notes"]
    assert c.post("/api/mai-hoa/cast", json={"method": "vat_so", "moment": "2026-10-25T15:30"}).status_code == 422
