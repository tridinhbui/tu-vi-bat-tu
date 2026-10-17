"""Formation evaluator: core / boosters / breakers / rescuers / refutations -> one of
khong_hien | hinh_thuc | thanh | thanh_thuong | bi_pha | pha_duoc_cuu  (+ chua_du_du_kien when the core cannot be decided).

No scores are summed. The state follows a fixed, documented order:
  1. core False                      -> khong_hien (UNKNOWN core -> chua_du_du_kien)
  2. a breaker not covered by a rescuer -> bi_pha
  3. every active breaker rescued    -> pha_duoc_cuu
  4. no breaker: 0 boosters -> hinh_thuc, >=1 -> thanh, >= thuong_at -> thanh_thuong
  5. an active refutation lowers thanh_thuong -> thanh -> hinh_thuc (it never raises, never touches bi_pha/pha_duoc_cuu; it is listed)
An UNKNOWN sub-condition is never silently counted as False: it is reported in `unknown` and in the caveats.
"""
from __future__ import annotations

from ..knowledge import dsl
from ..knowledge.formation import Formation

EFFECT = {"thanh": "support", "thanh_thuong": "support", "bi_pha": "limit", "hinh_thuc": "neutral",
          "pha_duoc_cuu": "neutral", "khong_hien": "neutral", "chua_du_du_kien": "neutral"}
STATE_VI = {"khong_hien": "không hiện", "hinh_thuc": "chỉ có hình thức", "thanh": "thành cách", "thanh_thuong": "thành cách, thế mạnh",
            "bi_pha": "bị phá cách", "pha_duoc_cuu": "bị phá nhưng được cứu giải", "chua_du_du_kien": "chưa đủ dữ kiện"}
LOWER = {"thanh_thuong": "thanh", "thanh": "hinh_thuc"}


def evaluate_formation(f: Formation, facts: dict, world=None) -> dict:
    core = dsl.evaluate(f.core, facts, world)
    d: dict = {"id": f.id, "name_vi": f.name_vi, "anchor": f.anchor, "core": core, "state": None, "boosters": [], "breakers": [],
               "rescuers": [], "refutations": [], "uncovered_breakers": [], "unknown": [], "missing_for_next_level": [],
               "downgraded_by_refutation": False, "caveats": []}
    if core is not True:
        d["state"] = "khong_hien" if core is False else "chua_du_du_kien"
        if core is None:
            d["caveats"].append("điều kiện lõi thiếu dữ kiện")
        return d

    unknown_labels: list[str] = []

    def active(kind):
        out = []
        for e in getattr(f, kind):
            v = dsl.evaluate(e.when, facts, world)
            if v is True:
                out.append(e)
            elif v is None:
                d["unknown"].append(f"{kind}:{e.id}")
                unknown_labels.append(e.label)
        return out

    boosters, breakers, rescuers, refs = active("boosters"), active("breakers"), active("rescuers"), active("refutations")
    covered = set()
    for r in rescuers:
        covered |= {b.id for b in f.breakers} if "*" in r.rescues else set(r.rescues)
    uncovered = [b for b in breakers if b.id not in covered]
    d.update(boosters=[e.id for e in boosters], breakers=[e.id for e in breakers], rescuers=[e.id for e in rescuers],
             refutations=[e.id for e in refs], uncovered_breakers=[b.id for b in uncovered])
    if uncovered:
        state = "bi_pha"
        usable = [r for r in f.rescuers if r not in rescuers and ("*" in r.rescues or set(r.rescues) & {b.id for b in uncovered})]
        d["missing_for_next_level"] = [f"cứu giải: {r.label}" for r in usable]
    elif breakers:
        state = "pha_duoc_cuu"
    else:
        n = len(boosters)
        state = "thanh_thuong" if n >= f.thuong_at else "thanh" if n >= 1 else "hinh_thuc"
        left = [e.label for e in f.boosters if e not in boosters]
        if state == "hinh_thuc":
            d["missing_for_next_level"] = [f"tăng thế: {x}" for x in left]
        elif state == "thanh":
            d["missing_for_next_level"] = [f"tăng thế: {x}" for x in left]
        if refs and state in LOWER:
            state, d["downgraded_by_refutation"] = LOWER[state], True
    if d["unknown"]:
        d["caveats"].append("có điều kiện chưa đủ dữ kiện nên không được tính là sai: " + "; ".join(unknown_labels))
    d["state"] = state
    return d


def _labels(f: Formation, kind: str, ids: list[str]) -> str:
    m = {e.id: e.label for e in getattr(f, kind)}
    return "; ".join(m[i] for i in ids)


def render_vi(f: Formation, d: dict) -> str:
    """Deterministic Vietnamese description of one verdict. States what the structure contains; asserts no event."""
    s = f"Cách {f.name_vi} (cung {f.anchor}): {STATE_VI[d['state']]}."
    if d["state"] in ("khong_hien", "chua_du_du_kien"):
        return s
    if d["boosters"]:
        s += f" Yếu tố tăng thế: {_labels(f, 'boosters', d['boosters'])}."
    if d["breakers"]:
        s += f" Yếu tố phá cách: {_labels(f, 'breakers', d['breakers'])}."
    if d["rescuers"]:
        s += f" Yếu tố cứu giải: {_labels(f, 'rescuers', d['rescuers'])}."
    if d["uncovered_breakers"]:
        s += f" Chưa có yếu tố nào cứu: {_labels(f, 'breakers', d['uncovered_breakers'])}."
    if d["refutations"]:
        s += f" Phản chứng cần xét: {_labels(f, 'refutations', d['refutations'])}" + (" (vì vậy hạ một bậc)." if d["downgraded_by_refutation"] else ".")
    if d["missing_for_next_level"]:
        s += " Còn thiếu: " + "; ".join(d["missing_for_next_level"]) + "."
    for c in d["caveats"]:
        s += f" Lưu ý: {c}."
    return s + " (Bản thử nghiệm, chưa đối chiếu sách; chỉ mô tả cấu trúc, không dự báo.)"


def run_formations(formations, base, facts_of, world, derived, fdepth, nodes, edges, findings) -> list[dict]:
    """Evaluate every formation at its anchor palace; write the outcome into the inference graph as derived facts + findings."""
    from .engine import Edge, Finding, Node, _fact_node
    out, anchors = [], {}
    for f in formations:
        subj = f"palace:{f.anchor}"
        if subj not in base:
            continue
        facts = facts_of(subj)
        d = evaluate_formation(f, facts, world)
        d["subject"], d["text"] = subj, render_vi(f, d)
        out.append(d)
        anchors.setdefault(subj, []).append(d)
        derived[subj][f"derived.cach.{f.id}.state"] = d["state"]
        fdepth[(subj, f"derived.cach.{f.id}.state")] = 1
        rid = f"rule:{f.id}@{subj}"
        nodes[rid] = Node(rid, "rule", f"{f.id} [{f.reviewStatus}, thử nghiệm] @{subj}", {"description": f.name_vi, "formation": True})
        for tsub, name in [(subj if p is None else f"palace:{p}", n) for p, n in dsl.leaves(f.core, facts)]:
            edges.append(Edge(rid, _fact_node(nodes, tsub, name, facts_of(tsub).get(name) if tsub in base else None), "derived_from"))
        claim = f"cach:{f.id}:{d['state']}"
        fid = f"finding:{f.id}:{claim}@{subj}"
        findings.append(Finding(fid, subj, claim, EFFECT[d["state"]], f.id, 1, basis="draft", notes=[d["text"]]))
        nodes[fid] = Node(fid, "finding", f"{claim} ({EFFECT[d['state']]}) @{subj}", {"depth": 1, "formation": True})
        edges.append(Edge(fid, rid, "derived_from"))
        for kind, edge_kind in (("breakers", "opposes"), ("rescuers", "suppresses"), ("boosters", "supports")):
            for eid in d[kind]:
                ev = next(e for e in getattr(f, kind) if e.id == eid)
                nid = f"evidence:{f.id}:{eid}@{subj}"
                nodes[nid] = Node(nid, "fact", f"{kind[:-1]}: {ev.label} @{subj}")
                edges.append(Edge(nid, fid, edge_kind))
    for subj, ds in anchors.items():
        for key, states in (("formed", ("thanh", "thanh_thuong")), ("broken", ("bi_pha",)), ("rescued", ("pha_duoc_cuu",)),
                            ("formal", ("hinh_thuc",))):
            derived[subj][f"derived.cach.{key}"] = sorted(x["id"] for x in ds if x["state"] in states)
            fdepth[(subj, f"derived.cach.{key}")] = 1
    return out
