"""Quy tắc lấy từ sách đã đọc: Trích Thiên Tủy (Nhậm Thiết Tiều) và Thiệu Vĩ Hoa. Mỗi test ghi trang tương ứng."""
import json

import pytest

from bazi_deep_util import EX, HOA1, TONG1, view
from tvbt.bazi_deep import flow, geju, interact, pipeline, season, strength, temporal_deep as td, yongshen
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep.profile import DEFAULT, TTT_NTT, TVH_40


# ---------- profile ttt_ntt: policies taken from the book
def test_ttt_profile_ignores_tranh_hop_for_a_true_hoa_but_default_does_not():
    t = "Mậu Ngọ / Kỷ Mùi / Giáp Thìn / Kỷ Tỵ"                # Giáp between two Kỷ, month Mùi (Thổ), no Mộc killer
    st = lambda prof: [r["status"] for r in interact.resolve(ChartView.from_names(t), prof).interactions if r["kind"] == "stem_combine"]
    assert st(DEFAULT) == ["tranh_hop", "tranh_hop"]
    assert st(TTT_NTT) == ["chan_hoa", "chan_hoa"]            # PDF p.176: 'tranh hợp đố hợp là luận điệu hoang đường' once the hóa is real


def test_ttt_profile_a_failed_hoa_is_still_a_tranh_hop():
    r = interact.resolve(view("EX4"), TTT_NTT)               # Canh claimed by two Ất, but month Dậu... Ất/Canh hóa Kim fails other conditions or not: either way never plain hop_khong_hoa
    assert {x["status"] for x in r.interactions if x["kind"] == "stem_combine"} <= {"tranh_hop", "khong_ke", "chan_hoa", "gia_hoa"}


def test_ttt_profile_kho_policy_counts_khố_roots_without_opening():
    assert TTT_NTT.kho_policy == "tu_co_can" and DEFAULT.kho_policy == "can_mo"
    from tvbt.bazi_deep import position
    v = ChartView.from_names("Nhâm Tý / Giáp Thìn / Nhâm Thìn / Canh Tý")
    closed = max(x["score"] for x in position.roots(v, 8, DEFAULT) if x["pillar"] == "day")
    free = max(x["score"] for x in position.roots(v, 8, TTT_NTT) if x["pillar"] == "day")
    assert free == pytest.approx(closed * 2, abs=2e-3)       # PDF p.70: mộ khố / dư khí are roots, and 'hình xung tất thương tổn căn khí'


def test_ttt_tu_lenh_table_has_only_the_month_the_book_gives():
    mk = lambda m, d: ChartView.from_names(f"Giáp Tý / {m} / Giáp Tuất / Canh Ngọ", days_into_month=d)
    assert [season.command(mk("Bính Dần", d), TTT_NTT)["name"] for d in (3, 9, 20)] == ["Mậu", "Bính", "Giáp"]       # PDF p.67: 7 + 8 + 15 days
    assert season.command(mk("Đinh Mão", 3), TTT_NTT) is None                                                          # the book gives no other table
    assert [r[1] for r in TTT_NTT.tu_lenh_rows()["Dần"]] == [7, 8, 15]
    assert [r[1] for r in DEFAULT.tu_lenh_rows()["Dần"]] == [7, 7, 16]                                               # the draft common table differs: a school choice


# ---------- tòng roles / hóa dụng
def test_tong_roles_come_from_the_book_and_tong_nhi_is_marked_as_system_inference():
    tr = yongshen.TONG_ROLES["types"]
    assert tr["Tòng Cường"]["ji"] == ["Tai", "QuanSat", "ThucThuong"] and tr["Tòng Vượng"]["ji"][:1] == ["QuanSat"]
    assert tr["Tòng Thế"]["yong"] == ["Tai"] and tr["Tòng Cường"]["src"] == "SRC_TTT_TONG"
    assert tr["Tòng Nhi"].get("verified") is False and tr["Tòng Nhi"]["src"] == "SRC_SYSTEM_STRUCT"


def test_true_tong_sat_gets_the_book_roles_in_the_thuan_the_method_only():
    o = pipeline.analyse(ChartView.from_names(TONG1), TVH_40, with_rules=False)
    m = o["yongshen"]["methods"]
    assert m["thuan_the"]["outer"] == "Tòng Sát" and m["thuan_the"]["yong"] == ["QuanSat"] and m["thuan_the"]["ji"] == ["Ti", "An"]
    assert m["phu_uc"]["status"] == "khong_ap_dung"          # phù ức does not apply to a true tòng


def test_hoa_than_du_or_thieu_selects_tiet_or_sinh_tro():
    o = pipeline.analyse(ChartView.from_names(HOA1), TVH_40, with_rules=False)
    t = o["yongshen"]["methods"]["thuan_the"]
    assert t["outer"] == "Hóa Thổ" and t["hoa_than_du"] is True and t["need_elements"] == ["Kim"]     # Thổ dư -> tiết = Kim (PDF pp.175-176)
    S = {"by_element": {"Mộc": 5, "Hỏa": 5, "Thổ": 20, "Kim": 5, "Thủy": 65}}
    out = yongshen.thuan_the({"outer": [{"name": "Hóa Thổ", "quality": "chân"}]}, S, DEFAULT)
    assert out["hoa_than_du"] is False and out["need_elements"] == ["Hỏa", "Thổ"]                       # thiếu -> sinh trợ = Hỏa, rồi chính Thổ


# ---------- nguyên lưu
def _S(by, dm="Mộc"):
    return {"by_element": by, "dm_element": dm}


def test_nguyen_luu_hi_ky_and_blocker():
    hi = flow.nguyen_luu(_S({"Mộc": 40, "Hỏa": 30, "Thổ": 25, "Kim": 3, "Thủy": 2}), DEFAULT)      # Mộc -> Hỏa -> Thổ: Tỉ Kiếp ... Tài
    assert hi["path"][:3] == ["Mộc", "Hỏa", "Thổ"] and hi["verdict"] == "hi" and hi["start_group"] == "Ti"
    ky = flow.nguyen_luu(_S({"Mộc": 10, "Hỏa": 3, "Thổ": 2, "Kim": 50, "Thủy": 35}), DEFAULT)       # Kim (Quan Sát) -> Thủy -> Mộc (Tỉ Kiếp)
    assert ky["start_group"] == "QuanSat" and ky["end_group"] == "Ti" and ky["path"] == ["Kim", "Thủy", "Mộc"] and ky["verdict"] == "ky"
    blocked = flow.nguyen_luu(_S({"Mộc": 90, "Hỏa": 0, "Thổ": 0, "Kim": 10, "Thủy": 0}), DEFAULT)
    assert blocked["path"] == ["Mộc"] and blocked["blocked_by"]                                       # Hỏa is absent: where the flow stops
    assert blocked["verdict"] == "khong_ket_luan"


# ---------- hàn noãn (unit)
def test_han_noan_branches():
    v_cold_warm = ChartView.from_names("Giáp Thân / Bính Tý / Canh Thìn / Mậu Dần")       # book 207: Dần gives hỏa a root
    v_cold_none = ChartView.from_names("Kỷ Dậu / Bính Tý / Canh Thìn / Giáp Thân")        # book 208: no Dần, hỏa lâm tuyệt
    cl = {"label": "cực hàn"}
    assert yongshen.han_noan(v_cold_warm, cl)["direction"] == "can_noan"
    assert yongshen.han_noan(v_cold_none, cl)["direction"] == "thuan_han"
    assert yongshen.han_noan(v_cold_warm, {"label": "ôn hòa"})["direction"] is None


# ---------- Thương Quan table
def test_thuong_quan_styles_follow_the_five_samples():
    TQ = yongshen.TQ["styles"]
    assert set(TQ) == {"tai", "an", "kiep", "thuong", "quan"}
    assert TQ["an"]["yong"] == ["An"] and TQ["tai"]["yong"] == ["Tai"] and TQ["kiep"]["yong"] == ["Ti"] and TQ["thuong"]["yong"] == ["ThucThuong"] and TQ["quan"]["yong"] == ["QuanSat"]
    assert TQ["kiep"]["ji"] == ["Tai", "QuanSat"] and TQ["quan"]["ji"] == ["ThucThuong", "An"]
    c = json.loads(open(__import__("pathlib").Path(__file__).parent / "golden/ttt_cases.json", encoding="utf8").read())["cases"]
    o = pipeline.analyse(ChartView.from_names(c["160"]["pillars"]), TVH_40, with_rules=False)           # book 160: Thương Quan dụng Ấn
    assert o["yongshen"]["thuong_quan"]["style"] == "an"
    cm = o["yongshen"]["methods"]["cach_cuc"]
    assert cm["status"] == "ap_dung_ttt_thuong_quan" and cm["yong"] == ["An"] and cm["ji"] == ["Tai", "ThucThuong"] and cm["source"] == "SRC_TTT_THUONGQUAN"


# ---------- cái đầu / tiệt cước
def test_can_chi_relations_and_mitigation():
    v = view("EX1")
    rel = lambda s, b, others=(): td.can_chi_relation(v, td.tp("luck", s, b), [td.tp("year", *o) for o in others])
    assert rel(6, 2)["relation"] == "cai_dau"           # Canh Dần: can khắc chi
    assert rel(0, 8)["relation"] == "tiet_cuoc"         # Giáp Thân: chi khắc can
    assert rel(2, 6)["relation"] == "dong_hanh" and rel(4, 6)["relation"] == "chi_sinh_can" and rel(2, 4)["relation"] == "can_sinh_chi"
    assert rel(6, 2)["aggravated"] is True              # EX1 already has Canh on the stems (PDF p.230: 'nhất định hung hiểm')
    v2 = ChartView.from_names("Mậu Tý / Bính Dần / Giáp Tuất / Bính Tý")                # Bính (Hỏa) controls the attacker Kim, no Kim of its own
    r2 = td.can_chi_relation(v2, td.tp("luck", 6, 2), [])
    assert r2["relation"] == "cai_dau" and r2["mitigated"] is True and r2["aggravated"] is False


def test_tiet_cuoc_and_cai_dau_findings_use_each_methods_own_role():
    v = view("EX1")
    tl = pipeline.timeline(v, TVH_40, [{"index": 1, "stem": 4, "branch": 2, "start_year_exact": 2000.0}, {"index": 2, "stem": 6, "branch": 2, "start_year_exact": 2010.0}], [])
    c1 = {f["claim"]: f for f in tl["luck"][0]["findings"]}
    c2 = {f["claim"]: f for f in tl["luck"][1]["findings"]}
    assert "bt_ttt_tiet_cuoc_cach_cuc" in c1 and c1["bt_ttt_tiet_cuoc_cach_cuc"]["basis"] == "verified"       # Mậu (Tài, a dụng of the cách) sits on Dần
    assert "bt_ttt_cai_dau_cach_cuc" in c2 and c2["bt_ttt_cai_dau_cach_cuc"]["basis"] == "verified"           # Canh (Sát) on Dần
    assert not any(k.startswith("bt_ttt_tiet_cuoc") for k in c2)


def test_thien_khac_dia_xung_rules_depend_on_the_day_master():
    for strong, claim in ((True, "bt_ttt_thien_khac_vuong"), (False, "bt_ttt_thien_khac_nhuoc")):
        base = {"chart": {"chart.system": "bat_tu", "bazi.t.effect": "trung_tinh", "bazi.t.can_chi": "", "bazi.t.can_chi_mitigated": False, "bazi.t.can_chi_aggravated": False,
                          "bazi.t.dm_strong": strong, "bazi.t.dm_weak": not strong, "bazi.t.event_kinds": ["thien_khac_dia_xung"], "bazi.t.opens_kho": False, "bazi.t.completes_cuc": False,
                          "bazi.t.role.cach_cuc": "", "bazi.t.role.phu_uc": "", "bazi.t.role.dieu_hau": ""}}
        out = pipeline.reason(base, "pack_temporal.json")
        got = {f["claim"]: f for f in out["findings"]}
        assert claim in got and got[claim]["basis"] == "verified"


# ---------- verified rules: each cites a verified source with a locator
def test_every_verified_rule_has_a_vietnamese_claim_and_a_page_locator():
    claims = json.loads((pipeline.DATA / "claims_vi.json").read_text("utf-8"))
    for pack in ("pack_structure.json", "pack_temporal.json"):
        rules, sources = pipeline.load_structure_pack(pack)
        src = {s.id: s for s in sources}
        for r in rules:
            if r.reviewStatus != "verified":
                continue
            assert all(src[s].verified and "p" in (src[s].locator or "").lower() for s in r.sourceIds), r.id
            for c in r.consequences:
                assert c["claim"] in claims and len(claims[c["claim"]]) > 20
