"""Phase 3: Phi Hóa as its own school namespace — graph, facts, isolation, and each EXPERIMENTAL rule on constructed charts."""
import warnings

import pytest
from fastapi.testclient import TestClient

from phase1_helpers import synth
from tvbt import tuvi
from tvbt.api import app
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import STEMS_VI
from tvbt.knowledge.loader import load_all, load_experimental_phi_hoa
from tvbt.knowledge.schema import KnowledgeRule, validate_pack
from tvbt.phi_hoa import facts as PF, graph as G, tables
from tvbt.phi_hoa.isolation import validate_isolation
from tvbt.phi_hoa.run import KNOWN, run_phi_hoa
from tvbt.reasoning import facts as natal_facts

warnings.filterwarnings("ignore")
RULES, SRCS = load_experimental_phi_hoa()
HOAS = tables.HOA


def real(b=(1990, 5, 17, 10, 30, "male")):
    return tuvi.compute(normalize(BirthInput(*b[:5], "Asia/Ho_Chi_Minh", b[5])))


# ---- tables + graph -------------------------------------------------------------------------------------------------------
def test_only_the_verified_tam_hop_table_exists_and_unknown_ids_are_refused():
    assert list(tables.TABLES) == ["tam_hop_vn"] and tables.TABLES["tam_hop_vn"]["status"] == "reused_unverified_for_phi_tinh"
    with pytest.raises(ValueError):
        tables.stars_for(0, "trung_chau")
    with pytest.raises(ValueError):
        G.build(real(), "phi_tinh_variant")


@pytest.mark.parametrize("b", [(1990, 5, 17, 10, 30, "male"), (1975, 11, 3, 23, 5, "female"), (2001, 8, 28, 14, 0, "male")])
def test_graph_has_48_edges_each_matching_the_table_and_the_star_holder(b):
    c = real(b)
    g = G.build(c)
    assert len(g.edges) == 48 and all(len(g.out[p["name"]]) == 4 for p in c.palaces)
    holder = {s: p["name"] for p in c.palaces for s in p["stars"]}
    for p in c.palaces:
        want = dict(zip(HOAS, tuvi.TU_HOA[STEMS_VI.index(p["stem"])]))
        for h in HOAS:
            e = g.out[p["name"]][h]
            assert (e.star, e.src, e.hoa, e.src_stem) == (want[h], p["name"], h, p["stem"])
            assert e.dst == holder.get(want[h]) and p["stem"] in e.trace and h in e.trace and "tam_hop_vn" in e.trace
            assert g.inc[e.dst][h].count(p["name"]) == 1


def test_edge_kinds_are_pure_geometry():
    c = real()
    g = G.build(c)
    idx = {p["name"]: p["branch_index"] for p in c.palaces}
    for e in g.edges:
        d = (idx[e.dst] - idx[e.src]) % 12
        assert ("tu_hoa" in e.kinds) == (d == 0) and ("xung_phi" in e.kinds) == (d == 6)
        assert ("tam_hop" in e.kinds) == (d in (4, 8)) and ("giap" in e.kinds) == (d in (1, 11))
        assert ("nhi_hop" in e.kinds) == ((idx[e.src] + idx[e.dst]) % 12 == 1 and d != 0)


def test_dai_han_fly_is_the_same_operation_as_the_phase2_dai_han_tu_hoa():
    from tvbt.reasoning.temporal_facts import layered
    c = real()
    L = layered(c, 2024)
    g = G.build(c)
    assert {h: g.out[L["dai_han_palace"]][h].dst for h in HOAS} == L["dai_han_hoa"]            # đại hạn palace flies its own stem


def test_stem_override_changes_the_flying_stem_only():
    c = real()
    g0, g1 = G.build(c), G.build(c, stem_override={"Mệnh": 0})
    assert [e.star for e in g1.out["Mệnh"].values()] == list(tuvi.TU_HOA[0])
    assert all(g0.out[n][h].star == g1.out[n][h].star for n in g0.out if n != "Mệnh" for h in HOAS)


# ---- constructed charts: put(A, hoa, B) places A's hoa star inside B -----------------------------------------------------------
BASE = synth()
STEM = {p["name"]: STEMS_VI.index(p["stem"]) for p in BASE.palaces}


def put(src, hoa, dst):
    return ("star", tables.stars_for(STEM[src], "tam_hop_vn")[hoa], dst)


def chart_with(*puts, extra=()):
    ops = [put(*p) for p in puts]
    stars = [o[1] for o in ops]
    assert len(stars) == len(set(stars)), "test setup places one star twice; choose other palaces"
    return synth(ops + list(extra))


def fired(c):
    r = run_phi_hoa(c)
    return r, {(f.subject[7:], f.rule_id) for f in r["findings"]}


def test_tu_hoa_ky_and_loc():
    r, f = fired(chart_with(("Tài Bạch", "Hóa Kỵ", "Tài Bạch"), ("Phu Thê", "Hóa Lộc", "Phu Thê")))
    assert ("Tài Bạch", "PH_TU_HOA_KY") in f and ("Phu Thê", "PH_TU_HOA_LOC") in f
    assert ("Phu Thê", "PH_TU_HOA_KY") not in f and ("Tài Bạch", "PH_TU_HOA_LOC") not in f


def test_ky_xung_phi_and_its_exception():
    c = chart_with(("Mệnh", "Hóa Kỵ", "Thiên Di"))
    r, f = fired(c)
    assert ("Mệnh", "PH_KY_XUNG_PHI") in f
    assert ("Mệnh", "PH_KY_XUNG_PHI") not in fired(chart_with(("Mệnh", "Hóa Kỵ", "Quan Lộc")))[1]            # not the opposite palace
    r2, f2 = fired(chart_with(("Mệnh", "Hóa Kỵ", "Thiên Di"), ("Phu Thê", "Hóa Khoa", "Mệnh")))               # Khoa flies INTO the source palace
    assert ("Mệnh", "PH_KY_XUNG_PHI") not in f2 and any(b["rule"] == "PH_KY_XUNG_PHI" and b["subject"] == "palace:Mệnh" for b in r2["blocked"])


def test_loc_ky_giao_needs_both_directions():
    r, f = fired(chart_with(("Mệnh", "Hóa Lộc", "Quan Lộc"), ("Quan Lộc", "Hóa Kỵ", "Mệnh")))
    assert ("Mệnh", "PH_LOC_KY_GIAO") in f and ("Quan Lộc", "PH_LOC_KY_GIAO") not in f
    assert not [x for x in fired(chart_with(("Mệnh", "Hóa Lộc", "Quan Lộc"), ("Quan Lộc", "Hóa Kỵ", "Tài Bạch")))[1] if x[1] == "PH_LOC_KY_GIAO"]


def test_menh_loc_quan_tai_and_menh_ky_nhap():
    assert ("Mệnh", "PH_MENH_LOC_QUAN_TAI") in fired(chart_with(("Mệnh", "Hóa Lộc", "Tài Bạch")))[1]
    assert ("Mệnh", "PH_MENH_LOC_QUAN_TAI") not in fired(chart_with(("Mệnh", "Hóa Lộc", "Phu Thê")))[1]
    assert ("Mệnh", "PH_MENH_KY_NHAP") in fired(chart_with(("Mệnh", "Hóa Kỵ", "Phu Thê")))[1]
    assert ("Mệnh", "PH_MENH_KY_NHAP") not in fired(chart_with(("Mệnh", "Hóa Kỵ", "Tật Ách")))[1]
    assert ("Quan Lộc", "PH_MENH_KY_NHAP") not in fired(chart_with(("Quan Lộc", "Hóa Kỵ", "Phu Thê")))[1]        # only Mệnh is the source


UNIQ = [n for n, st in STEM.items() if list(STEM.values()).count(st) == 1]        # palaces whose stem no other palace shares


def test_palaces_with_the_same_stem_fly_the_same_star_so_they_count_separately():
    shared = [n for n, st in STEM.items() if list(STEM.values()).count(st) > 1]
    assert len(shared) == 4 and len(UNIQ) == 8                      # 12 palaces, 10 stems: two stems occur twice
    a, b = shared[:2] if STEM[shared[0]] == STEM[shared[1]] else [n for n in shared if STEM[n] == STEM[shared[0]]]
    g = G.build(chart_with((a, "Hóa Kỵ", "Tật Ách")))
    assert sorted(g.inc["Tật Ách"]["Hóa Kỵ"]) == sorted([a, b])      # ONE star placed, TWO palaces fly it there


def test_many_hoa_into_one_palace():
    s1, s2 = UNIQ[0], UNIQ[1]
    assert ("Tật Ách", "PH_NHIEU_KY_VAO_MOT_CUNG") in fired(chart_with((s1, "Hóa Kỵ", "Tật Ách"), (s2, "Hóa Kỵ", "Tật Ách")))[1]
    assert not [x for x in fired(chart_with((s1, "Hóa Kỵ", "Tật Ách")))[1] if x[1] == "PH_NHIEU_KY_VAO_MOT_CUNG"]
    assert ("Tật Ách", "PH_NHIEU_LOC_VAO_MOT_CUNG") in fired(chart_with((s1, "Hóa Lộc", "Tật Ách"), (s2, "Hóa Lộc", "Tật Ách")))[1]


def test_loc_chain_two_level_inference_with_ref_and_trace():
    c = chart_with(("Mệnh", "Hóa Lộc", "Quan Lộc"), ("Quan Lộc", "Hóa Lộc", "Tài Bạch"))
    r, f = fired(c)
    assert ("Mệnh", "PH_MENH_CHUOI_LOC") in f and ("Quan Lộc", "PH_QUAN_LOC_TRONG_CHUOI_LOC") in f
    assert r["result"].derived["chart"]["derived.phi.menh_loc_chain"] is True
    fin = next(x for x in r["findings"] if x.rule_id == "PH_QUAN_LOC_TRONG_CHUOI_LOC")
    assert fin.depth == 2
    chain = " ".join(r["result"].why(fin.id)["chain"])
    assert "PH_MENH_CHUOI_LOC" in chain and "phi.loc_chain" in chain and "SRC_EXPERIMENTAL_PHI (unverified)" in chain
    short = fired(chart_with(("Mệnh", "Hóa Lộc", "Quan Lộc")))[1]                          # chain of 2 only: neither rule fires
    assert not {x for x in short if x[1] in ("PH_MENH_CHUOI_LOC", "PH_QUAN_LOC_TRONG_CHUOI_LOC")}


def test_chain_stops_at_a_cycle_and_self_loop():
    g = G.build(chart_with(("Mệnh", "Hóa Lộc", "Mệnh")))
    assert g.chain("Hóa Lộc", "Mệnh") == ["Mệnh"]
    g = G.build(chart_with(("Mệnh", "Hóa Lộc", "Quan Lộc"), ("Quan Lộc", "Hóa Lộc", "Mệnh")))
    assert g.chain("Hóa Lộc", "Mệnh") == ["Mệnh", "Quan Lộc"]


# ---- facts + isolation + production untouched ------------------------------------------------------------------------------------
def test_phi_facts_are_namespaced_and_symmetric():
    c = real()
    F = PF.phi_facts(c)
    assert all(k.startswith("phi.") for s, d in F.items() for k in d)
    for n, d in F.items():
        if not n.startswith("palace:"):
            continue
        for (a, b) in PF.PAIRS:
            for x in d[f"phi.mutual.{a}>{b}"]:
                assert F[f"palace:{x}"][f"phi.mutual.{b}>{a}"] == [n.split(":", 1)[1]]            # A--a-->X and X--b-->A  <=>  seen from X the reverse pair


def test_production_facts_and_rules_know_nothing_about_phi_hoa():
    c = real()
    assert not any(k.startswith("phi.") for d in natal_facts.tuvi_facts(c).values() for k in d)
    prod, _ = load_all()
    assert not any(r.schoolId.startswith("phi_tinh") for r in prod)
    assert not {r.id for r in RULES} & {r.id for r in prod}


def test_pack_is_valid_isolated_draft_and_unverified():
    assert validate_pack(RULES, SRCS, KNOWN) == [] and validate_isolation(RULES) == []
    assert len(RULES) == 10 and all(r.reviewStatus == "draft" and r.schoolId == "phi_tinh_draft" for r in RULES)
    assert all(not s.verified for s in SRCS)


def _r(id, school, cond, cons=None):
    return KnowledgeRule(id, "tu_vi", school, "x", id, cond, cons or [{"kind": "finding", "claim": "c"}], sourceIds=[], subject="palace")


def test_isolation_blocks_cross_school_reads_and_asserts():
    phi_read = {"fact": "phi.tu_hoa", "operator": "contains", "value": "Hóa Kỵ"}
    assert any("may not read Phi Hóa fact" in e for e in validate_isolation([_r("A", "vn_dlhc_draft", phi_read)]))
    assert any("non-neutral fact" in e for e in validate_isolation([_r("B", "phi_tinh_draft", {"fact": "derived.cach.formed", "operator": "ne", "value": []})]))
    assert any("must be derived.phi" in e for e in validate_isolation([_r("C", "phi_tinh_draft", phi_read, [{"kind": "assert", "fact": "derived.x", "value": True}])]))
    assert any("only Phi Hóa rules" in e for e in validate_isolation([_r("D", "vn_dlhc_draft", {"fact": "palace.name", "value": "Mệnh"},
                                                                        [{"kind": "assert", "fact": "derived.phi.x", "value": True}])]))
    assert validate_isolation([_r("E", "phi_tinh_draft", {"all": [phi_read, {"fact": "palace.name", "value": "Mệnh"}]})]) == []
    # exceptions and ref leaves are checked too
    ex = KnowledgeRule("F", "tu_vi", "vn_dlhc_draft", "x", "F", {"fact": "palace.name", "value": "Mệnh"}, [{"kind": "finding", "claim": "c"}],
                       exceptions=[{"ref": {"palace": "opp", "fact": "phi.tu_hoa"}, "operator": "contains", "value": "Hóa Kỵ"}], subject="palace")
    assert any("may not read" in e for e in validate_isolation([ex]))


def test_deterministic_and_traceable():
    c = real()
    a, b = run_phi_hoa(c), run_phi_hoa(c)
    assert [(f.id, f.claim) for f in a["findings"]] == [(f.id, f.claim) for f in b["findings"]]
    for f in a["findings"]:
        assert a["result"].why(f.id)["chain"]


def test_api_phi_hoa_endpoint_separates_computation_from_interpretation():
    c = TestClient(app)
    r = c.post("/api/phi-hoa", json=dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male"))
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "draft" and j["school"] == "phi_tinh_draft" and "CHƯA được xác minh" in j["warning"] and "Tam Hợp" in j["warning"]
    comp, itp = j["computation"], j["interpretation"]
    assert comp["level"] == "computed" and comp["table"]["school"] == "tam_hop" and comp["table"]["status"] == "reused_unverified_for_phi_tinh"
    assert comp["table"]["verified_for"] == ["tam_hop_natal_tu_hoa"]
    assert len(comp["edges"]) == 48 and all(e["trace"] and e["from"] and e["hoa"] in HOAS for e in comp["edges"])
    assert all("tam hợp" in e["trace"] and "chưa xác minh cho Phi Tinh" in e["trace"] for e in comp["edges"])
    assert itp["level"] == "experimental" and itp["reviewStatus"] == "draft" and itp["problems"] == [] and itp["findings"]
    assert all(f["why"]["chain"] for f in itp["findings"])
    assert not any(k in comp for k in ("findings", "rules", "conflicts"))                  # the graph part carries no interpretation
    assert "edges" not in itp
