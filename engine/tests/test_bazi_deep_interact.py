import json
from pathlib import Path

import pytest

from bazi_deep_util import EX, HOA1, view
from tvbt.bazi_deep import interact
from tvbt.bazi_deep.profile import DEFAULT

BASELINE = json.loads((Path(__file__).parent / "golden/bazi_deep_baseline.json").read_text("utf-8"))


def kinds(v, kind, **kw):
    return [r for r in interact.detect(v) if r["kind"] == kind and all(r.get(k) == x for k, x in kw.items())]


def status(R, kind, pillars=None):
    return [r["status"] for r in R.interactions if r["kind"] == kind and (pillars is None or r["pillars"] == pillars)]


# ---------------- detection
def test_detect_covers_every_relation_the_old_pairwise_code_found():
    """Regression: the new detector is a superset of bazi._relations (same tables, golden-tested elsewhere)."""
    for k, b in BASELINE.items():
        v = view(k)
        new = interact.detect(v)
        for kind, items in b["relations_old"].items():
            for it in items:
                if it is None:                      # penalty triples are stored without pillars in the baseline
                    assert any(r["kind"] == "branch_penalty" and r.get("subtype") in ("vô ân", "thị thế") for r in new), (k, kind)
                elif kind in ("branch_triad_complete", "branch_meeting_complete"):
                    nk = "branch_triad" if "triad" in kind else "branch_meeting"
                    assert any(r["kind"] == nk and r["element"] == it for r in new), (k, kind, it)
                else:
                    nk = kind if kind != "branch_penalty" else "branch_penalty"
                    assert any(r["kind"] == nk and "-".join(r["pillars"]) == it for r in new), (k, kind, it)


def test_detect_new_kinds_the_old_code_could_not_see():
    assert kinds(view("EX3"), "branch_semi_triad", subtype="vuong_mo")[0]["element"] == "Thủy"          # Tý–Thìn bán hợp Thủy
    assert kinds(view("EX4"), "branch_semi_triad", subtype="sinh_vuong")[0]["element"] == "Kim"         # Tỵ–Dậu
    assert kinds(view("EX5"), "branch_penalty", subtype="ban_hinh_thị thế")                                # Tuất–Mùi without Sửu
    assert not kinds(view("EX5"), "branch_penalty", subtype="thị thế")
    assert [r["element"] for r in kinds(view("EX1"), "branch_triad")] == ["Hỏa"]
    assert [r["element"] for r in kinds(view("EX6"), "branch_triad")] == ["Thủy"]
    assert [r["element"] for r in kinds(view("EX12"), "branch_triad")] == ["Mộc"]
    assert [r["element"] for r in kinds(view("EX13"), "branch_meeting")] == ["Mộc"]
    assert kinds(view("EX4"), "branch_self_penalty")                                                      # Dậu–Dậu


def test_adjacency_flags():
    r = kinds(view("EX2"), "stem_combine")[0]
    assert r["pillars"] == ["year", "day"] and r["adjacent"] is False and r["span"] == 2
    c = kinds(view("EX2"), "branch_clash")[0]
    assert c["pillars"] == ["year", "month"] and c["adjacent"] is True


def test_semi_triad_not_reported_when_triad_is_complete():
    assert not kinds(view("EX1"), "branch_semi_triad")


def test_stem_controls_directed_and_with_distance():
    cs = interact.stem_controls(view("EX3"))
    d = next(c for c in cs if c["from"] == "month.stem" and c["to"] == "year.stem")       # Đinh khắc Tân
    assert d["adjacent"] is True
    assert not any(c["from"] == "year.stem" and c["to"] == "month.stem" for c in cs)


# ---------------- resolution
def test_cuc_forms_and_takes_share_of_branch_qi():
    R = interact.resolve(view("EX1"))
    assert [c["element"] for c in R.cuc] == ["Hỏa"] and R.cuc[0]["thau"] is True
    assert R.cuc[0]["share"] == pytest.approx(DEFAULT.cuc_share["triad"] + DEFAULT.cuc_thau_bonus)
    assert set(R.shifts) == {"month.branch", "day.branch", "hour.branch"}


def test_meeting_has_priority_over_triad_sharing_a_branch():
    # Dần Mão Thìn (hội Mộc) and Hợi Mão Mùi (hợp Mộc) share Mão; only the hội may form
    from tvbt.bazi_deep.model import ChartView
    v = ChartView.from_names("Ất Hợi / Đinh Mão / Giáp Thìn / Bính Dần")
    R = interact.resolve(v)
    assert status(R, "branch_meeting") == ["formed"]


def test_lu_he_binds_but_does_not_transform():
    R = interact.resolve(view("EX14"))
    assert status(R, "branch_six_combine") == ["khong_ke"]          # Tý (year) – Sửu (day) are two pillars apart
    R2 = interact.resolve(view("Giáp Tý / Bính Tý / Kỷ Sửu / Canh Ngọ"))     # adjacent hợp Tý–Sửu month/day? (Tý month, Sửu day)
    assert status(R2, "branch_six_combine", ["month", "day"]) == ["formed"]
    assert {s["char"] for s in R2.steps if "lục hợp" in s.get("why", "")} == {"month.branch", "day.branch"}     # other effects may compound on top
    assert not R2.shifts


def test_hop_giai_xung_and_giang_co():
    from tvbt.bazi_deep.model import ChartView
    # Thìn–Dậu hợp (day–month adjacent) vs Tuất? use Mão–Dậu xung far from the hợp: Mão (hour) Dậu(month) Thìn(day)
    v = ChartView.from_names("Tân Hợi / Đinh Dậu / Giáp Thìn / Đinh Mão")
    R = interact.resolve(v)
    # Dậu is bound by hợp with Thìn (adjacent); Mão–Dậu clash is two pillars apart -> hợp giải xung
    assert status(R, "branch_six_combine") == ["formed"] and status(R, "branch_clash") == ["hop_giai_xung"]
    v2 = ChartView.from_names("Tân Mão / Đinh Dậu / Giáp Thìn / Giáp Tý")                   # EX3-like: clash is adjacent -> semi-triad outranks lục hợp
    R2 = interact.resolve(v2)
    assert status(R2, "branch_clash")[0] in ("xung_nho", "xung_can_bang", "giang_co")
    v3 = ChartView.from_names("Tân Mão / Đinh Dậu / Giáp Thìn / Giáp Ngọ")                   # no Tý: Thìn–Dậu hợp survives, Mão–Dậu xung adjacent
    R3 = interact.resolve(v3)
    assert status(R3, "branch_six_combine") == ["formed"] and status(R3, "branch_clash") == ["giang_co"]
    assert R3.mult["month.branch"] < DEFAULT.luhe_mult


def test_vuong_xung_suy_pulls_the_weaker_side():
    R = interact.resolve(view("EX3"))
    c = next(r for r in R.interactions if r["kind"] == "branch_clash")
    assert c["status"] == "xung_nho" and c["weaker"] == "year.branch"      # year branch is weaker than the month (lệnh) branch
    assert R.mult["year.branch"] < R.mult["month.branch"]


def test_clash_into_a_formed_cuc_halves_the_cuc():
    R = interact.resolve(view("EX10"))
    assert "xung_vao_cuc" in status(R, "branch_clash")
    assert R.cuc and R.cuc[0]["element"] == "Hỏa" and all(R.shifts[m][1] < 0.35 for m in R.cuc[0]["members"] if m in R.shifts)


def test_clash_opens_kho():
    assert "day" in interact.resolve(view("EX5")).opened and "hour" in interact.resolve(view("EX5")).opened     # Thìn–Tuất xung


def test_tranh_hop_blocks_hoa_and_weakens_all_involved_stems():
    R = interact.resolve(view("EX4"))                  # Canh (year) is claimed by both Ất (month) and Ất (day)
    assert status(R, "stem_combine", ["year", "month"]) == ["tranh_hop"]
    assert status(R, "stem_combine", ["year", "day"]) == ["khong_ke"]
    assert {s["char"] for s in R.steps if "tranh hợp" in s.get("why", "")} == {"month.stem", "year.stem"}
    assert not R.stem_element


def test_hoa_chan_changes_effective_day_master_element():
    R = interact.resolve(view(HOA1))
    r = next(x for x in R.interactions if x["kind"] == "stem_combine")
    assert r["status"] == "chan_hoa" and r["hua_unmet"] == [] and len(r["hua_met"]) == 7
    assert R.dm_hua == "Thổ" and R.dm_element == "Thổ"
    assert R.stem_element == {"month.stem": "Thổ", "day.stem": "Thổ"}


@pytest.mark.parametrize("name,unmet", [
    ("EX5", ["lenh_khong_bi_pha"]),                 # Tuất–Mùi hình touches the lệnh
    ("EX7", ["dac_lenh"]),                          # Nhâm–Đinh wants Mộc, month Ngọ is Hỏa
])
def test_each_hoa_condition_can_fail_for_its_own_reason(name, unmet):
    R = interact.resolve(view(name))
    r = next(x for x in R.interactions if x["kind"] == "stem_combine" and x["adjacent"])
    assert r["status"] != "chan_hoa" and unmet[0] in r["hua_unmet"]


def test_gia_hoa_vs_hop_khong_hoa_follow_the_condition_counts():
    R5 = interact.resolve(view("EX5"))
    assert next(x for x in R5.interactions if x["kind"] == "stem_combine")["status"] == "gia_hoa"       # kề sát + đắc lệnh met, only lệnh-bị-hình unmet
    R7 = interact.resolve(view("EX7"))
    assert next(x for x in R7.interactions if x["kind"] == "stem_combine")["status"] == "hop_khong_hoa"
    assert R7.mult["month.stem"] == DEFAULT.bound_mult


def test_hoa_requires_killer_free_and_rooted_hoa_than():
    from tvbt.bazi_deep.model import ChartView
    # same as HOA1 but a Mộc stem (Ất, hour) kills the Thổ: Thìn-hour for Giáp day is Mậu; use Giáp day hour Sửu = Ất Sửu
    v = ChartView.from_names("Mậu Ngọ / Kỷ Mùi / Giáp Thìn / Ất Sửu")
    r = next(x for x in interact.resolve(v).interactions if x["kind"] == "stem_combine" and x["adjacent"])
    assert "khong_bi_khac" in r["hua_unmet"] and r["status"] != "chan_hoa"


def test_penalty_scope_is_limited_to_lenh_and_day_unless_full_triple():
    R = interact.resolve(view("EX2"))                  # Mão–Tý hình touches month and day
    assert status(R, "branch_penalty") == ["co_hieu_luc"]
    R2 = interact.resolve(view("EX15"))
    assert "xa" in status(R2, "branch_penalty") or "ghi_nhan" in status(R2, "branch_penalty")


def test_interaction_order_is_a_profile_choice():
    a = interact.resolve(view("EX10"))
    b = interact.resolve(view("EX10"), DEFAULT.with_(interact_order=("clash", "cuc", "stem_combine", "xing_hai_po")))
    assert a.cuc and not b.cuc or a.shifts != b.shifts or a.mult != b.mult      # changing the order changes the outcome


def test_resolver_is_deterministic_and_never_raises_on_all_examples():
    for k in EX:
        v = view(k)
        r1, r2 = interact.resolve(v), interact.resolve(v)
        assert r1.mult == r2.mult and r1.shifts == r2.shifts and r1.steps == r2.steps
        assert all(0.2 <= m <= 1.0 for m in r1.mult.values())
        assert all(r.get("status") for r in r1.interactions if r["kind"] in ("stem_combine", "branch_clash", "branch_six_combine", "branch_triad", "branch_meeting"))
