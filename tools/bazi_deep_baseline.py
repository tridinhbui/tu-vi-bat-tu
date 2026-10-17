"""Freeze the PRE-upgrade Bát Tự view of EX1–EX15 (old pipeline: pairwise relations, boolean đắc lệnh/căn, 8 facts).
Run once before the upgrade; the result is committed as tests/golden/bazi_deep_baseline.json and compared by tools/bazi_deep_compare.py."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent / "engine"
sys.path.insert(0, str(ROOT))
from tvbt import bazi
from tvbt.analysis import bazi_core
from tvbt.ganzhi import BRANCHES_VI, STEMS_VI, nap_am_name
from tvbt.reasoning import facts
from tvbt.trace import Trace
from tvbt.bazi_deep.model import ChartView, PILLARS


def old_view(text):
    v = ChartView.from_names(text)
    pillars = {p: bazi._pillar(v.dm, v.stem(p), v.branch(p), p == "day") for p in PILLARS}
    chart = bazi.BaziChart(pillars=pillars, day_master=v.dm, day_master_element=bazi.STEM_ELEMENT[v.dm], luck_direction="", luck_start={},
                           luck_pillars=[], relations=bazi._relations(pillars), jie_used={}, trace=Trace(), school={})
    dm_el, mb, stage, tiet, roots, helpers = bazi_core(chart)
    f = facts.bazi_facts(chart)["chart"]
    rel = {k: [r.get("pillars", r.get("element")) for r in rs] for k, rs in chart.relations.items() if rs}
    return {"pillars": v.name(), "dac_lenh_old_boolean": tiet, "stage_vs_month": stage, "root_pillars_old": roots, "visible_helpers_old": helpers,
            "facts_old": f, "relations_old": rel, "geju": None, "dm_level": None, "yongshen": None}


if __name__ == "__main__":
    ex = json.loads((ROOT / "data/bazi_deep/examples.json").read_text("utf-8"))["charts"]
    out = {k: old_view(t) for k, t in ex.items()}
    dst = ROOT / "tests/golden/bazi_deep_baseline.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), "utf-8")
    print("wrote", dst, len(out))
