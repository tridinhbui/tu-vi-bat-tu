from tvbt import bazi, shensha, tuvi
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import BRANCHES_HAN, BRANCHES_VI, STEMS_HAN

D = shensha._DATA
BR = {c: i for i, c in enumerate(BRANCHES_HAN)}


def test_tables_are_complete():
    for table in ("by_day_stem", "by_day_branch", "by_month_branch", "by_year_branch"):
        keys = STEMS_HAN if table == "by_day_stem" else BRANCHES_HAN
        for t in D[table].values():
            assert set(t["row"]) == set(keys)
    assert D["by_day_stem"]["天乙贵人"]["row"]["甲"] == "丑未" and D["by_day_stem"]["羊刃"]["row"]["丙"] == "午"


def test_book_tables_agree_with_independently_verified_tu_vi_tables():
    """Same stars appear in both traditions: Dịch Mã = Thiên Mã, Đào hoa, Hồng Loan/Thiên Hỷ, Cô Thần/Quả Tú (Tử Vi tables verified on other pages)."""
    for yb in range(12):
        grp = tuvi.TRIAD_GROUP[yb]
        assert BR[D["by_day_branch"]["驿马"]["row"][BRANCHES_HAN[yb]]] == {0: 8, 1: 2, 2: 11, 3: 5}[grp]       # Thiên Mã
        assert BR[D["by_day_branch"]["桃花"]["row"][BRANCHES_HAN[yb]]] == {0: 3, 1: 9, 2: 6, 3: 0}[grp]       # Đào Hoa
        hl = (3 - yb) % 12
        assert BR[D["by_year_branch"]["红鸾"]["row"][BRANCHES_HAN[yb]]] == hl                                  # Hồng Loan
        assert BR[D["by_year_branch"]["天喜"]["row"][BRANCHES_HAN[yb]]] == (hl + 6) % 12                       # Thiên Hỷ
        cô = {0: 5, 1: 8, 2: 11, 3: 2}[[0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3][(yb - 2) % 12]]                    # Dần Mão Thìn -> Tỵ ...
        assert BR[D["by_year_branch"]["孤神"]["row"][BRANCHES_HAN[yb]]] == cô


def test_find_on_real_chart():
    nb = normalize(BirthInput(2000, 1, 1, 12, 0, "Asia/Ho_Chi_Minh", "male"))   # Kỷ Mão / Bính Tý / Mậu Ngọ / Mậu Ngọ
    ss = shensha.find(bazi.compute(nb).pillars)
    names = {(x["zh"], x["pillar"]) for x in ss}
    assert ("十干禄", "day") not in names                                           # Mậu's lộc is Tỵ, absent
    assert ("驿马", "year") not in {(x["zh"], x["pillar"]) for x in ss if x["pillar"] == "day"}   # never reported in the keying pillar
    # Mậu day: 文昌 at Thân (absent), 天乙贵人 at Sửu/Mùi (absent); 金舆 at Mùi (absent); 正桃花 at Tuất/Ngọ -> Ngọ present (day & hour)
    assert ("正桃花", "day") in names and ("正桃花", "hour") in names
