"""Phase 4: INDEPENDENT oracle for all 48 Phi Hóa edges of many real charts.
The oracle shares no code with phi_hoa/graph.py or tuvi.py's stem/Tứ Hóa tables:
  * palace stem  = ngũ hổ độn recomputed here from the year stem (Dần takes (2*(ys%5)+2)%10, then +1 per branch);
  * Tứ Hóa stars = data/tu_hoa_vi.json (Khảo Luận pp.195-197 table), a different file from tuvi.TU_HOA;
  * star holder  = scan of the chart's raw palaces;
  * edge kinds   = recomputed from branch distances."""
import json
import warnings
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tvbt import tuvi
from tvbt.api import app
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import BRANCHES_VI, STEMS_VI
from tvbt.phi_hoa import graph as G
from tvbt.phi_hoa.tables import HOA

warnings.filterwarnings("ignore")
TU_HOA_VI = json.loads((Path(__file__).resolve().parent.parent / "data" / "tu_hoa_vi.json").read_text("utf-8"))["by_stem"]
CHARTS = [(y, m, d, h, g) for y in range(1950, 2010) for (m, d, h, g) in ((2, 9, 6, "male"), (7, 21, 15, "female"), (11, 3, 23, "male"))]


def real(y, m, d, h, g):
    return tuvi.compute(normalize(BirthInput(y, m, d, h, 20, "Asia/Ho_Chi_Minh", g)))


def oracle_edges(c):
    ys = STEMS_VI.index(c.year_gz.split()[0])
    dan = (2 * (ys % 5) + 2) % 10
    holder = {s: p for p in c.palaces for s in p["stars"]}
    out = {}
    for p in c.palaces:
        b = BRANCHES_VI.index(p["branch"])
        stem = (dan + (b - 2) % 12) % 10
        stars = [x["star"] for x in TU_HOA_VI[str(stem)]]
        for hoa, star in zip(HOA, stars):
            q = holder.get(star)
            d = (BRANCHES_VI.index(q["branch"]) - b) % 12 if q else None
            kinds = sorted(k for k, ok in (("tu_hoa", d == 0), ("xung_phi", d == 6), ("tam_hop", d in (4, 8)), ("giap", d in (1, 11)),
                                           ("nhi_hop", q is not None and (b + BRANCHES_VI.index(q["branch"])) % 12 == 1 and d != 0)) if ok)
            out[(p["name"], hoa)] = dict(stem=STEMS_VI[stem], star=star, dst=q["name"] if q else None, kinds=kinds)
    return out


@pytest.mark.parametrize("y,m,d,h,g", CHARTS)
def test_every_edge_matches_the_independent_oracle(y, m, d, h, g):
    c = real(y, m, d, h, g)
    gr = G.build(c)
    want = oracle_edges(c)
    assert len(gr.edges) == 48 == len(want)
    for e in gr.edges:
        w = want[(e.src, e.hoa)]
        assert (e.src_stem, e.star, e.dst, sorted(e.kinds)) == (w["stem"], w["star"], w["dst"], w["kinds"]), (e.src, e.hoa)
        # provenance: the trace names the source palace, its stem, the hóa, the star, the receiving palace and the table's school
        for part in (e.src, f"can {w['stem']}", e.hoa, w["star"], "tam_hop_vn", "tam hợp", "chưa xác minh cho Phi Tinh"):
            assert part in e.trace, (part, e.trace)
        if e.dst:
            assert e.dst in e.trace
    # incoming lists are exactly the inverse of the edges
    for dst in gr.inc:
        for hoa in HOA:
            assert sorted(gr.inc[dst][hoa]) == sorted(s for (s, h), w in want.items() if h == hoa and w["dst"] == dst)


def test_palace_stems_in_the_chart_follow_ngu_ho_do_independently():
    for y, m, d, h, g in CHARTS[::7]:
        c = real(y, m, d, h, g)
        ys = STEMS_VI.index(c.year_gz.split()[0])
        dan = (2 * (ys % 5) + 2) % 10
        for p in c.palaces:
            assert p["stem"] == STEMS_VI[(dan + (BRANCHES_VI.index(p["branch"]) - 2) % 12) % 10]


def test_two_palaces_sharing_a_stem_fly_identical_stars_in_every_chart():
    """Ngũ hổ độn gives Tý the stem of Dần and Sửu the stem of Mão (12 palaces, 10 stems)."""
    seen = 0
    for y, m, d, h, g in CHARTS:
        c = real(y, m, d, h, g)
        gr = G.build(c)
        by_stem = {}
        for p in c.palaces:
            by_stem.setdefault(p["stem"], []).append(p["name"])
        pairs = [v for v in by_stem.values() if len(v) == 2]
        assert len(pairs) == 2 and sorted(len(v) for v in by_stem.values()) == [1] * 8 + [2] * 2
        names = {p["branch"]: p["name"] for p in c.palaces}
        assert sorted(map(sorted, pairs)) == sorted(map(sorted, [[names["Tý"], names["Dần"]], [names["Sửu"], names["Mão"]]]))
        for a, b in pairs:
            assert [(e.star, e.dst) for e in gr.out[a].values()] == [(e.star, e.dst) for e in gr.out[b].values()]
            for hoa in HOA:                       # the receiving palace lists BOTH senders for that hóa
                dst = gr.out[a][hoa].dst
                if dst:
                    assert {a, b} <= set(gr.inc[dst][hoa])
        seen += 1
    assert seen == len(CHARTS)


def test_api_edges_equal_the_graph_for_several_births():
    cl = TestClient(app)
    for y, m, d, h, g in CHARTS[::40]:
        j = cl.post("/api/phi-hoa", json=dict(year=y, month=m, day=d, hour=h, minute=20, gender=g)).json()
        gr = G.build(real(y, m, d, h, g))
        assert [(e["from"], e["hoa"], e["to"], e["star"], e["stem"], e["kinds"], e["trace"]) for e in j["computation"]["edges"]] == \
               [(e.src, e.hoa, e.dst, e.star, e.src_stem, e.kinds, e.trace) for e in gr.edges]


def test_phi_hoa_v1_top_level_keys_still_present_and_equal_to_nested_blocks():
    """Backward compatibility with the deployed /api/phi-hoa (87a7274): table{id,status}, edges, findings, blocked, conflicts, problems at top level."""
    from fastapi.testclient import TestClient
    from tvbt.api import app
    j = TestClient(app).post("/api/phi-hoa", json=dict(year=1990, month=5, day=17, hour=10, minute=30, gender="male")).json()
    assert set(j["table"]) == {"id", "status"} and j["table"]["status"] == j["computation"]["table"]["status"]
    assert j["edges"] == j["computation"]["edges"] and len(j["edges"]) == 48
    assert j["findings"] == j["interpretation"]["findings"] and j["blocked"] == j["interpretation"]["blocked"]
    assert j["conflicts"] == j["interpretation"]["conflicts"] and j["problems"] == j["interpretation"]["problems"] == []
