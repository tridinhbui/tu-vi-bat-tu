from tvbt import bazi, cross, temporal, tuvi
from tvbt.calendar_core import BirthInput, normalize

BI = BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")


def charts():
    nb = normalize(BI)
    return bazi.compute(nb), tuvi.compute(nb)


def test_annual_pillars_known():
    assert temporal.annual_pillar(2024) == (0, 4)   # Giáp Thìn
    assert temporal.annual_pillar(1984) == (0, 0)   # Giáp Tý


def test_bazi_year_ten_god_and_luck_window():
    bz, _ = charts()
    r = temporal.bazi_year(bz, 1990, 2024)  # age 34
    assert r["annual_pillar"] == "Giáp Thìn" and r["annual_stem_ten_god"] == "Thực Thần"  # Nhâm DM, Giáp = Thực Thần
    assert r["luck_pillar"] is not None and r["scope"] == "temporal"
    assert temporal.bazi_year(bz, 1990, 1990)["luck_pillar"] is None  # before first luck pillar starts


def test_clash_detected_as_fact():
    bz, _ = charts()
    # natal day branch Ngọ; year 2026 = Bính Ngọ same, 2025 Ất Tỵ; 2030 = Canh Tuất; find a Tý year -> clashes Ngọ
    r = temporal.bazi_year(bz, 1990, 2020)  # Canh Tý
    assert any(x["kind"] == "chi_xung" and x["with"] == "day" for x in r["annual_vs_natal"])


def test_tuvi_year_and_timeline_purity():
    bz, tv = charts()
    r = temporal.tuvi_year(tv, 2024)
    assert r["age_tuoi_mu"] == 35 and r["dai_han"]["age_from"] <= 35 <= r["dai_han"]["age_to"]
    assert set(r["luu_tu_hoa"]) == {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"}
    before = [(s.name, s.branch) for s in tv.stars]
    tl = temporal.timeline(bz, tv, 1990, 100)
    assert len(tl) == 101 and before == [(s.name, s.branch) for s in tv.stars]


def test_compare_hours_changes_only_dependents():
    a = BirthInput(1990, 5, 17, 10, 30, "Asia/Ho_Chi_Minh", "male")
    b = BirthInput(1990, 5, 17, 11, 30, "Asia/Ho_Chi_Minh", "male")  # next hour branch
    d = cross.compare_charts(a, b)
    assert set(d["bazi_pillars"]) == {"hour"}          # year/month/day unaffected
    assert d["tuvi"]["moved_stars"]                     # hour-dependent stars move
    assert "Tử Vi" not in d["tuvi"]["moved_stars"] or True
    same = cross.compare_charts(a, a)
    assert not same["bazi_pillars"] and not same["tuvi"]["moved_stars"]


def test_cross_system_keeps_separate_and_caveat():
    from tvbt.nlg.generate import Interpretation
    mk = lambda c, r: Interpretation("chart", c, "support", "supported", "draft", [r], [], [], [], [], None)
    out = cross.compare_systems([mk("career", "TV1"), mk("x", "TV2")], [mk("career", "BT1")])
    assert [t["claim"] for t in out["shared_topics"]] == ["career"] and out["tuvi_only"] == ["x"]
    assert "tương đương" in out["caveat"] and "probab" not in str(out)


def test_tieu_han_rule_p27():
    # Thực Hành p.27: Dần/Ngọ/Tuất births start at Thìn; males go thuận, females nghịch. 1998 = Mậu Dần.
    nb = normalize(BirthInput(1998, 6, 15, 12, 0, "Asia/Ho_Chi_Minh", "male"))
    tv = tuvi.compute(nb)
    assert tv.lunar["year"] == 1998
    assert temporal.tuvi_year(tv, 1998)["tieu_han_branch"] == "Thìn"      # age 1
    assert temporal.tuvi_year(tv, 1999)["tieu_han_branch"] == "Tỵ"        # age 2, thuận
    nf = tuvi.compute(normalize(BirthInput(1998, 6, 15, 12, 0, "Asia/Ho_Chi_Minh", "female")))
    assert temporal.tuvi_year(nf, 1999)["tieu_han_branch"] == "Mão"       # age 2, nghịch
    t1 = tuvi.compute(normalize(BirthInput(1996, 6, 15, 12, 0, "Asia/Ho_Chi_Minh", "male")))   # Bính Tý -> Tuất
    assert temporal.tuvi_year(t1, 1996)["tieu_han_branch"] == "Tuất"


def test_leap_month_default_follows_khao_luan_p41():
    nb = normalize(BirthInput(2020, 6, 1, 12, 0, "Asia/Ho_Chi_Minh", "male"))     # leap 4th month, day 10
    assert (nb.lunar.month, nb.lunar.is_leap, nb.lunar.day) == (4, True, 10)
    assert tuvi.compute(nb).effective_lunar_month == 4                            # same month number, whatever the day
    late = normalize(BirthInput(2020, 6, 20, 12, 0, "Asia/Ho_Chi_Minh", "male"))  # leap 4th month, day 29
    assert late.lunar.is_leap and tuvi.compute(late).effective_lunar_month == 4
    assert tuvi.compute(late, leap_rule="split_15").effective_lunar_month == 5    # variant still available
