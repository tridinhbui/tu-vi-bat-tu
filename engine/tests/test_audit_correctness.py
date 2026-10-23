"""Python side of the owner's review of 09/01/2002 (2026-10-22, docs/audit/DEEP-TUVI.md §Correctness):
  6  per-finding statuses kept apart: an adverse reading, a reading limited by another rule (named), an unresolved conflict
  7  no verified rule is wider than its page on 'nhập miếu' / 'độc thủ' (tools/interpret/audit_widening.py), Tả Hữu Tứ mộ is draft
  8  a rule of Thực Hành / Toàn Thư / Khảo Luận reads brightness in its own book's table, falling back to the chart's table when that book has
     no cell"""
import json
import subprocess
import sys
from pathlib import Path

from tvbt import dignity as dg
from tvbt.knowledge import dsl
from tvbt.knowledge.loader import load_all
from tvbt.reasoning import conflict, engine

ROOT = Path(__file__).resolve().parents[2]
RULES, SOURCES = load_all()


def _run(palace):
    res = engine.run(RULES, SOURCES, {"chart": {"chart.system": "tu_vi"}, "palace:" + palace["palace.name"]: palace}, system="tu_vi")
    conflict.resolve(res, RULES)
    return res


def test_statuses_adverse_limited_unresolved():
    # Hóa Kỵ at Tài Bạch, nothing opposing: an adverse reading, not "limited by an opposing rule"
    res = _run({"palace.name": "Tài Bạch", "palace.branch": "Tý", "palace.own_major_stars": ["Thiên Đồng", "Thái Âm"], "palace.own_stars": ["Thiên Đồng", "Thái Âm", "Địa Không"],
                "palace.tu_hoa": [], "palace.tuan": False, "palace.triet": False})
    lim = [f for f in res.findings if f.effect == "limit"]
    assert lim and all(f.status in ("adverse", "limited", "unresolved") for f in lim)
    for f in res.findings:
        assert f.status != "limited" or f.limited_by, f.rule_id
        assert f.status != "adverse" or f.effect == "limit"


def test_no_widened_rule_left():
    out = subprocess.run([sys.executable, str(ROOT / "tools" / "interpret" / "audit_widening.py")], capture_output=True, text=True, cwd=ROOT)
    assert out.stdout.strip().endswith("0 found"), out.stdout[-2000:]
    r = next(r for r in RULES if r.id == "TV_KL_STAR_MENH_TA_HUU_TU_MO")
    assert r.reviewStatus == "draft"


def test_own_book_dignity():
    # a star / branch where Khảo Luận and Thực Hành disagree: the rule's own book decides
    pair = None
    for s in ["Thái Dương", "Thái Âm", "Tham Lang", "Thiên Lương", "Cự Môn", "Liêm Trinh", "Thiên Phủ", "Thiên Cơ", "Vũ Khúc", "Thiên Đồng", "Phá Quân", "Thất Sát", "Thiên Tướng", "Tử Vi"]:
        for b in dg.kb()["branches"]:
            a, t = dg.dignity(s, b, "khao_luan"), dg.dignity(s, b, "thuc_hanh")
            if a and t and a != t:
                pair = (s, b, a, t); break
        if pair:
            break
    assert pair, "the two tables differ somewhere"
    s, b, kl, th = pair
    facts = {"palace.branch": b, f"palace.dignity.{s}": kl}
    assert dsl.evaluate({"fact": f"palace.dignity@thuc_hanh.{s}", "operator": "eq", "value": th}, facts) is True
    assert dsl.evaluate({"fact": f"palace.dignity@khao_luan.{s}", "operator": "eq", "value": kl}, facts) is True
    # no cell in the book: the chart's table
    facts2 = {"palace.branch": b, "palace.dignity.Không Có Sao": "đắc"}
    assert dsl.evaluate({"fact": "palace.dignity@thuc_hanh.Không Có Sao", "operator": "eq", "value": "đắc"}, facts2) is True
    # every rule of the three books reads its own table
    for r in RULES:
        if r.system == "tu_vi" and len(r.sourceIds) == 1 and r.sourceIds[0] in ("SRC_THUC_HANH", "SRC_TOAN_THU", "SRC_KHAO_LUAN"):
            assert '"palace.dignity.' not in json.dumps(r.conditions, ensure_ascii=False), r.id
