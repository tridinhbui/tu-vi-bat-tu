"""Deep-interpretation engine (tvbt/synthesis): flag behaviour, API preservation, structure detectors on synthetic positions,
conflict typing, and invariants over a sweep of real charts. Detectors are tested on constructed palaces, never on one attached chart."""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from tvbt import tuvi
from tvbt.api import app
from tvbt.calendar_core import BirthInput, normalize
from tvbt.ganzhi import BRANCHES_VI
from tvbt.synthesis import enabled, structures as S
from tvbt.synthesis.conflicts import classify, find_tensions, MATRIX
from tvbt.synthesis.evidence import Evidence

PAL = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]
BODY = {"year": 1990, "month": 5, "day": 15, "hour": 10, "minute": 30, "gender": "male"}
client = TestClient(app)


def mk(menh_branch=0, than_at="Phúc Đức", **spec):
    """12 palaces; spec = {palace_name: dict(major=[], stars=[], dig={}, tuan=False, triet=False)}; the Mệnh palace sits on menh_branch."""
    ps = []
    for i, n in enumerate(PAL):
        d = spec.get(n, {})
        b = (menh_branch + i) % 12
        ps.append({"name": n, "branch": BRANCHES_VI[b], "branch_index": b, "stem": "Giáp", "is_than": n == than_at,
                   "major_stars": list(d.get("major", [])), "stars": list(d.get("major", [])) + list(d.get("stars", [])),
                   "major_dignity": d.get("dig", {}), "minor_dignity": d.get("mdig", {}), "tuan": d.get("tuan", False), "triet": d.get("triet", False)})
    return ps


def hoa(ps, **where):
    """where: {'Hóa Lộc': ('Cự Môn', 'Mệnh')} -> tu_hoa with the branch of that palace."""
    by = {p["name"]: p for p in ps}
    return {h: {"star": st, "branch": by[pn]["branch_index"]} for h, (st, pn) in where.items()}


def det(ps, th):
    return {s.id: s for s in S.detect_all(ps, th)}


# ---------------- flag / API preservation
def test_flag_default_off(monkeypatch):
    monkeypatch.delenv("TVBT_DEEP_INTERPRETATION", raising=False)
    assert enabled() is False
    assert client.post("/api/deep-reading", json=BODY).status_code == 404


def test_flag_on_serves_ten_chapters_and_leaves_old_api_untouched(monkeypatch):
    monkeypatch.delenv("TVBT_DEEP_INTERPRETATION", raising=False)
    before = {u: client.post(u, json=BODY).text for u in ("/api/reasoning", "/api/analysis", "/api/chart")}
    monkeypatch.setenv("TVBT_DEEP_INTERPRETATION", "1")
    r = client.post("/api/deep-reading", json=BODY)
    assert r.status_code == 200
    assert [c["id"] for c in r.json()["chapters"]] == ["tong_quan", "ban_menh", "tinh_cach", "cong_danh", "tai_bach", "quan_he", "dai_han_luu_nien", "cach_cuc", "muoi_hai_cung", "chuyen_sau"]
    assert {u: client.post(u, json=BODY).text for u in before} == before


# ---------------- special structures (position-driven)
def test_cu_mon_ham_hoa_loc_requires_ham():
    ps = mk(**{"Mệnh": {"major": ["Cự Môn"], "dig": {"Cự Môn": "hãm"}}})
    s = det(ps, hoa(ps, **{"Hóa Lộc": ("Cự Môn", "Mệnh")}))["CU_MON_HOA_LOC"]
    assert s.present and s.premises[1]["ok"] and s.verification == "mot_phan" and "hãm biến" in s.caveat
    ps2 = mk(**{"Mệnh": {"major": ["Cự Môn"], "dig": {"Cự Môn": "miếu"}}})
    s2 = det(ps2, hoa(ps2, **{"Hóa Lộc": ("Cự Môn", "Mệnh")}))["CU_MON_HOA_LOC"]
    assert s2.present and not s2.premises[1]["ok"] and "KHÔNG đúng" in s2.reading


def test_cu_mon_hoa_loc_absent_when_loc_elsewhere():
    ps = mk(**{"Mệnh": {"major": ["Cự Môn"], "dig": {"Cự Môn": "hãm"}}})
    assert not det(ps, hoa(ps, **{"Hóa Lộc": ("Thái Dương", "Tài Bạch")}))["CU_MON_HOA_LOC"].present


def test_cu_mon_tu_mo_loc_limiter_and_tuan_marks_r07():
    ps = mk(menh_branch=4, **{"Mệnh": {"major": ["Cự Môn"], "dig": {"Cự Môn": "hãm"}, "tuan": True}})   # Mệnh at Thìn
    s = det(ps, hoa(ps, **{"Hóa Lộc": ("Cự Môn", "Mệnh")}))["CU_MON_HOA_LOC"]
    assert any("Tứ Mộ" in x for x in s.limiters) and "R07" in s.matrix_ids


def test_tam_hoa_hoi_menh_scope_sensitivity():
    ps = mk(**{"Mệnh": {}, "Tài Bạch": {}})     # Tài Bạch and Quan Lộc are Mệnh's two tam hợp
    th = hoa(ps, **{"Hóa Lộc": ("A", "Tài Bạch"), "Hóa Quyền": ("B", "Quan Lộc"), "Hóa Khoa": ("C", "Tài Bạch")})
    s = det(ps, th)["TAM_HOA_HOI_MENH"]
    assert s.present and s.verification == "da_doi_chieu" and "R01" in s.matrix_ids
    assert [v["holds"] for v in s.variants] == [False, False, True]          # only the broad reading holds
    th2 = hoa(ps, **{"Hóa Lộc": ("A", "Mệnh"), "Hóa Quyền": ("B", "Thiên Di"), "Hóa Khoa": ("C", "Tài Bạch")})
    assert [v["holds"] for v in det(ps, th2)["TAM_HOA_HOI_MENH"].variants] == [False, False, True]
    th3 = hoa(ps, **{"Hóa Lộc": ("A", "Mệnh"), "Hóa Quyền": ("B", "Mệnh"), "Hóa Khoa": ("C", "Mệnh")})
    assert [v["holds"] for v in det(ps, th3)["TAM_HOA_HOI_MENH"].variants] == [True, True, True]


def test_than_cu_quan_loc_vcd_never_claims_a_source():
    ps = mk(than_at="Quan Lộc", **{"Phu Thê": {"major": ["Thiên Đồng"]}})
    s = det(ps, {})["THAN_QUAN_VCD"]
    assert s.present and s.verification == "chua_du_nguon" and "Thiên Đồng" in s.supports[0] and "U_THAN_QUAN_VCD" in s.caveat
    assert not det(mk(than_at="Quan Lộc", **{"Quan Lộc": {"major": ["Thiên Cơ"]}}), {})["THAN_QUAN_VCD"].present
    assert not det(mk(than_at="Tài Bạch"), {})["THAN_QUAN_VCD"].present


def test_co_nguyet_phu_the_collects_tuan_ky_da_without_verdict():
    ps = mk(**{"Phu Thê": {"major": ["Thiên Cơ", "Thái Âm"], "stars": ["Đà La"], "tuan": True}})
    s = det(ps, hoa(ps, **{"Hóa Kỵ": ("Thái Âm", "Phu Thê")}))["CO_NGUYET_PHU_THE"]
    text = " | ".join(s.limiters)
    assert s.present and "Tuần" in text and "Hóa Kỵ" in text and "Đà La" in text and "R07" in s.matrix_ids
    assert "không phải dự báo" in s.caveat and s.verification == "mot_phan"


def test_kinh_duong_tu_mo_only_mentions_source_for_menh_with_hoa():
    ps = mk(menh_branch=4, **{"Mệnh": {"stars": ["Kình Dương", "Hỏa Tinh"]}})              # Mệnh at Thìn
    s = det(ps, {})["KINH_DUONG_TU_MO"]
    assert s.present and s.verification == "mot_phan" and any("TT tr.50" in x for x in s.supports)
    ps2 = mk(menh_branch=4, **{"Tài Bạch": {"stars": ["Kình Dương"]}})
    got = [x for x in S.detect_all(ps2, {}) if x.id == "KINH_DUONG_TU_MO"]
    assert all(x.verification == "chua_du_nguon" for x in got) and all(not x.supports for x in got)
    ps3 = mk(menh_branch=3, **{"Mệnh": {"stars": ["Kình Dương"]}})                         # Mệnh at Mão: not Tứ Mộ
    assert not [x for x in S.detect_all(ps3, {}) if x.id == "KINH_DUONG_TU_MO"]


def test_sat_pha_tham_thresholds_can_disagree():
    ps = mk(**{"Mệnh": {"major": ["Phá Quân"]}, "Tài Bạch": {"major": ["Tham Lang"]}, "Quan Lộc": {"major": ["Thất Sát"], "stars": ["Kình Dương"]}})
    s = det(ps, {})["SAT_PHA_THAM"]
    assert s.present and [v["breaks"] for v in s.variants] == [True, False, False] and "R03" in s.matrix_ids
    assert "ba kết luận khác nhau" in s.reading
    assert not det(mk(**{"Mệnh": {"major": ["Phá Quân"]}}), {})["SAT_PHA_THAM"].present


def test_no_khoi_viet_giap_menh_or_nham_khoa_choice():
    assert not [n for n in dir(S) if "khoi" in n.lower()]
    assert tuvi.TU_HOA[8][2] == "Tả Phụ"      # Nhâm-Khoa stays as the existing production table; the engine never switches it
    assert any(e["id"] == "R05" and e["status"] == "nguon_mau_thuan" for e in MATRIX["entries"])


# ---------------- conflict typing
def ev(rule, claim, effect, leaves, schools=("Thực Hành",), aspect="danh", anchors=("Phá Quân",), val=None, subj="palace:Quan Lộc"):
    from tvbt.synthesis import taxonomy as tx
    return Evidence(rule, subj, "Quan Lộc", claim, claim, effect, "draft", list(schools), [], leaves, list(anchors), aspect, val or tx.valence_of(claim))


def test_conflict_kinds():
    base = [("palace.name", "eq", "Quan Lộc"), ("palace.own_major_stars", "contains", "Phá Quân")]
    good = ev("A", "pha_cat_cong_danh", "support", base + [("palace.dignity.Phá Quân", "eq", "miếu")])
    bad = ev("B", "pha_kho_cong_danh", "limit", base + [("palace.own_stars", "contains", "Địa Kiếp")])
    assert classify(good, bad).kind == "both_hold"
    spec = ev("C", "pha_kho_cong_danh", "limit", base + [("palace.dignity.Phá Quân", "eq", "miếu"), ("palace.own_stars", "contains", "Địa Kiếp")])
    assert classify(good, spec).kind == "refinement"
    twin = ev("D", "pha_kho_cong_danh", "limit", base + [("palace.dignity.Phá Quân", "eq", "miếu")], schools=("Khảo Luận",))
    assert classify(good, twin).kind == "school_divergence"
    same_book = ev("E", "pha_kho_cong_danh", "limit", base + [("palace.dignity.Phá Quân", "eq", "miếu")])
    assert classify(good, same_book).kind == "unresolved"
    other_aspect = ev("F", "pha_kho_tai", "limit", base, aspect="tai")
    assert classify(good, other_aspect) is None
    same_side = ev("G", "pha_cat_quyen", "support", base)
    assert classify(good, same_side) is None


def test_tensions_are_deterministic():
    import random
    cl = []
    from tvbt.synthesis.evidence import Cluster
    base = [("palace.name", "eq", "Quan Lộc")]
    items = [ev("A", "x_tot_cong_danh", "support", base + [("palace.own_stars", "contains", "Tả Phụ")]), ev("B", "x_kho_cong_danh", "limit", base + [("palace.own_stars", "contains", "Địa Kiếp")])]
    outs = []
    for _ in range(3):
        random.shuffle(items)
        outs.append([(t.kind, t.a, t.b) for t in find_tensions([Cluster(("k",), "palace:Quan Lộc", "Quan Lộc", "danh", None, "cong_danh", list(items))])])
    assert outs[0] == outs[1] == outs[2] and outs[0]


# ---------------- sweep over real charts
SWEEP = [(y, m, d, h) for y in (1949, 1963, 1978, 1992, 2004) for m in (2, 6, 10) for d in (9, 22) for h in (1, 8, 15, 21)]


def test_sweep_invariants(monkeypatch):
    monkeypatch.setenv("TVBT_DEEP_INTERPRETATION", "1")
    banned = ["Có thể nhận thấy một dấu hiệu", "dự báo chắc chắn"]
    for y, m, d, h in SWEEP:
        for g in ("male", "female"):
            body = {"year": y, "month": m, "day": d, "hour": h, "minute": 0, "gender": g}
            j = client.post("/api/deep-reading", json=body).json()
            blob = json.dumps(j, ensure_ascii=False)
            assert not any(b in blob for b in banned), body
            seen = {}
            for c in j["chapters"]:
                assert c["conclusion"] and c["reasoning_chain"] and c["reasoning_chain"][-1]["step"] == "ket_luan", (body, c["id"])
                for bucket in ("supports", "limits", "neutral"):
                    for line in c["details"].get(bucket, []):
                        # one finding is narrated in exactly one chapter
                        assert seen.setdefault(line["rule_id"], c["id"]) == c["id"], (body, line["rule_id"])
                for s in c["details"].get("structures", []):
                    assert s["verification"] in ("da_doi_chieu", "mot_phan", "chua_du_nguon")
            assert "verified" not in j["meta"]["note"].replace("không tự nâng cấp", "")


def test_sensitive_lines_are_framed_as_tradition(monkeypatch):
    monkeypatch.setenv("TVBT_DEEP_INTERPRETATION", "1")
    hits = 0
    for y, m, d, h in SWEEP[:30]:
        j = client.post("/api/deep-reading", json={"year": y, "month": m, "day": d, "hour": h, "minute": 0, "gender": "female"}).json()
        for c in j["chapters"]:
            for line in c["details"].get("limits", []) + c["details"].get("supports", []):
                if line["aspect"] in ("hon_nhan", "suc_khoe", "tuoi_tho"):
                    hits += 1
                    shown = [x for x in c["supports"] + c["limits"] if line["text"] in x]
                    assert all("không phải dự báo" in x for x in shown)
    assert hits > 0
