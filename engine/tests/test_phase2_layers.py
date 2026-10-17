"""Phase 2: multi-layer time facts (đại hạn / tiểu hạn / lưu Thái Tuế / Tứ Hóa of three layers) and the EXPERIMENTAL layer rules."""
import warnings

import pytest
from fastapi.testclient import TestClient

from phase1_helpers import synth
from tvbt import temporal, tuvi
from tvbt.api import app
from tvbt.calendar_core import BirthInput, normalize
from tvbt.knowledge.loader import load_all, load_experimental_layers
from tvbt.knowledge.schema import validate_pack
from tvbt.reasoning import layers, temporal_facts as T

warnings.filterwarnings("ignore")
KNOWN = {"palace.*", "chart.*", "bazi.*", "derived.*", "time.*"}
RULES, SRCS = load_experimental_layers()


def real(b=(1990, 5, 17, 10, 30, "male")):
    return tuvi.compute(normalize(BirthInput(*b[:5], "Asia/Ho_Chi_Minh", b[5])))


# ---- the time layers agree with the existing production year payload -------------------------------------------------------
@pytest.mark.parametrize("year", [2005, 2019, 2024, 2031])
@pytest.mark.parametrize("b", [(1990, 5, 17, 10, 30, "male"), (1975, 11, 3, 23, 5, "female")])
def test_layers_agree_with_temporal_tuvi_year(b, year):
    tv = real(b)
    L, y = T.layered(tv, year), temporal.tuvi_year(tv, year)
    assert L["tieu_han_palace"] == y["tieu_han_palace"] and L["luu_thai_tue_palace"] == y["luu_thai_tue_palace"]
    assert L["dai_han"] == y["dai_han"] and L["age"] == y["age_tuoi_mu"]
    assert {k: v["natal_palace"] for k, v in y["luu_tu_hoa"].items()} == L["luu_hoa"]


def test_dai_han_tu_hoa_uses_the_stem_of_the_dai_han_palace():
    tv = real()
    L = T.layered(tv, 2024)
    assert L["dai_han_stem"] == "Mậu" and L["dai_han_palace"] == "Phúc Đức"
    # Mậu: Tham Lang Lộc, Thái Âm Quyền, Hữu Bật Khoa, Thiên Cơ Kỵ (the table tuvi.TU_HOA uses) -> where those stars sit natally
    where = {s: next(p["name"] for p in tv.palaces if s in p["stars"]) for s in ("Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ")}
    assert L["dai_han_hoa"] == {"Hóa Lộc": where["Tham Lang"], "Hóa Quyền": where["Thái Âm"], "Hóa Khoa": where["Hữu Bật"], "Hóa Kỵ": where["Thiên Cơ"]}


def test_year_before_age_one_or_after_last_dai_han_has_no_dai_han_facts():
    tv = real()
    L = T.layered(tv, 2200)
    assert L["dai_han"] is None and L["dai_han_hoa"] == {}
    f = T.time_facts(tv, 2200)
    assert f["chart"]["time.has_dai_han"] is False and all(v["time.dai_han_hoa"] == [] for k, v in f.items() if k.startswith("palace:"))


def test_time_facts_per_palace_stack_layers():
    f = T.time_facts(real(), 2024)
    assert f["palace:Phụ Mẫu"]["time.ky_layers"] == ["bản mệnh", "lưu niên"] and f["palace:Phụ Mẫu"]["time.ky_n"] == 2
    assert f["palace:Phúc Đức"]["time.layers"] == ["dai_han", "tieu_han"]
    assert sum(1 for k, v in f.items() if k.startswith("palace:") and v["time.in_tp_of_menh"]) == 4
    assert f["palace:Mệnh"]["time.in_tp_of_menh"] is True
    # every hóa of every layer lands somewhere: 3 layers x 4 hóa = 12 landings across the palaces (stars always exist)
    assert sum(v["time.hoa_layer_count"] for k, v in f.items() if k.startswith("palace:")) == 12


# ---- the experimental pack ---------------------------------------------------------------------------------------------------
def test_pack_valid_isolated_and_draft():
    assert validate_pack(RULES, SRCS, KNOWN) == []
    prod, _ = load_all()
    assert not {r.id for r in RULES} & {r.id for r in prod}
    assert all(r.reviewStatus == "draft" and r.schoolId == "experimental_draft" for r in RULES) and all(not s.verified for s in SRCS)
    assert len(RULES) == 8


def fired(tv, year):
    r = layers.run_layers(tv, year)
    return r, {f.rule_id: f for f in r["findings"]}


def stack_chart(ops, menh="Tý"):
    """Synthetic chart + hand-placed hóa; layer facts are then computed from the REAL tables, so we set up positions through stars."""
    return synth(ops, menh)


def test_ky_chong_tang_on_real_chart_2024_phu_mau():
    r, f = fired(real(), 2024)
    assert "LY_KY_CHONG_TANG" in f and f["LY_KY_CHONG_TANG"].subject == "palace:Phụ Mẫu" and f["LY_KY_CHONG_TANG"].effect == "limit"
    assert "LY_LOC_CHONG_TANG" not in f                                   # Lộc: natal Phụ Mẫu only
    assert "LY_DAI_TIEU_TRUNG_CUNG" in f and f["LY_DAI_TIEU_TRUNG_CUNG"].subject == "palace:Phúc Đức"


def test_exception_khoa_of_dai_han_or_luu_blocks_ky_chong_tang():
    tv = real()
    # find a year where some palace has >=2 Kỵ layers AND a Khoa from đại hạn/lưu in the same palace -> rule must be blocked there
    blocked_seen = fired_seen = 0
    for y in range(1995, 2060):
        r, f = fired(tv, y)
        blocked_seen += sum(1 for b in r["blocked"] if b["rule"] == "LY_KY_CHONG_TANG")
        fired_seen += "LY_KY_CHONG_TANG" in f
        for b in r["blocked"]:
            if b["rule"] == "LY_KY_CHONG_TANG":
                pf = T.time_facts(tv, y)[b["subject"]]
                assert pf["time.ky_n"] >= 2 and ("Hóa Khoa" in pf["time.dai_han_hoa"] or "Hóa Khoa" in pf["time.luu_hoa"])
    assert fired_seen >= 1


def test_declared_conflict_between_ky_and_loc_stacking():
    tv = real()
    seen = False
    for b in [(1990, 5, 17, 10, 30, "male"), (1975, 11, 3, 23, 5, "female"), (2001, 8, 28, 14, 0, "male"), (1968, 1, 15, 0, 0, "female")]:
        tv = real(b)
        for y in range(1990, 2070):
            r = layers.run_layers(tv, y)
            claims = {(f.subject, f.rule_id) for f in r["findings"]}
            for subj in {s for s, rid in claims if rid == "LY_KY_CHONG_TANG"}:
                if (subj, "LY_LOC_CHONG_TANG") in claims:
                    assert [c for c in r["conflicts"] if "ly_ky_chong_tang" in c["claim"]][0]["status"] == "unresolved"
                    seen = True
    assert seen, "no chart/year combined both stackings; widen the scan"


def test_multi_hop_ky_luu_on_menh_axis_with_formed_cach():
    """Level 1: formation verdict and the layer rule that asserts derived.ky_luu_cham_truc_menh. Level 2: the rule that needs both."""
    found = None
    for y in range(1990, 2075):
        for b in [(1950, 1, 4, 4, 10, "male"), (1950, 1, 18, 18, 10, "male"), (1950, 1, 4, 4, 10, "female")]:
            tv = real(b)
            r = layers.run_layers(tv, y)
            hit = [f for f in r["findings"] if f.rule_id == "LY_KY_LUU_KHI_MENH_CO_CACH"]
            if hit:
                found = (r, hit[0])
                break
        if found:
            break
    assert found, "no multi-hop example in scan range"
    r, f = found
    assert f.depth >= 2 and r["result"].derived["chart"]["derived.ky_luu_cham_truc_menh"] is True
    chain = " ".join(r["result"].why(f.id)["chain"])
    assert "LY_KY_LUU_KHI_MENH_CO_CACH" in chain and ("LY_LUU_KY_XUNG_MENH" in chain or "LY_LUU_KY_NHAP_MENH" in chain)


def test_no_formed_cach_means_no_multi_hop_finding():
    tv = real((1990, 5, 17, 10, 30, "male"))
    for y in range(1995, 2060):
        r = layers.run_layers(tv, y)
        formed = r["result"].derived["palace:Mệnh"]["derived.cach.formed"]
        if not formed:
            assert not [f for f in r["findings"] if f.rule_id == "LY_KY_LUU_KHI_MENH_CO_CACH" or f.rule_id == "LY_DAI_HAN_TRONG_TAM_PHUONG_CO_CACH"]


def test_deterministic():
    tv = real()
    a, b = layers.run_layers(tv, 2026), layers.run_layers(tv, 2026)
    assert [(f.id, f.claim, f.depth) for f in a["findings"]] == [(f.id, f.claim, f.depth) for f in b["findings"]]


# ---- API: production unchanged, experimental opt-in --------------------------------------------------------------------------
BIRTH = dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male", to_year=2024)


def test_api_year_default_unchanged_and_flag_adds_only_experimental():
    c = TestClient(app)
    plain = c.post("/api/year", json=BIRTH).json()
    flagged = c.post("/api/year", json={**BIRTH, "experimental": True}).json()
    assert "experimental" not in plain
    assert {k: flagged[k] for k in ("bazi", "tuvi")} == plain
    x = flagged["experimental"]
    assert x["status"] == "draft" and x["pack_problems"] == [] and "không dự báo" in x["warning"]
    assert x["stack_by_palace"]["Phụ Mẫu"]["ky_layers"] == ["bản mệnh", "lưu niên"]
    assert any(f["claim"] == "ly_ky_chong_tang" and f["why"]["chain"] for f in x["findings"])
