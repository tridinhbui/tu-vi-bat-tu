"""Hà Lạc data (plan step H1): engine/data/ha_lac/hexagrams.json (Part II readings of quẻ 24-64, paraphrased, with pages) and
engine/data/ha_lac/worked_examples.json (the book's example charts transcribed as numbers, future golden tests for the caster).
Book-dependent checks skip when the PDF or PyMuPDF is missing (books are not in the repository)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "engine" / "data" / "ha_lac"
H = json.loads((D / "hexagrams.json").read_text("utf-8"))
W = json.loads((D / "worked_examples.json").read_text("utf-8"))
HEX = {h["number"]: h for h in H["hexagrams"]}
PDF_PAGES = 129

LINES = {"Kiền": "111", "Đoài": "110", "Ly": "101", "Chấn": "100", "Tốn": "011", "Khảm": "010", "Cấn": "001", "Khôn": "000"}  # hào 1..3
STEMS = {"Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"}
BRANCHES = {"Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"}
GROUPS = ("quan_chuc", "gioi_si", "nguoi_thuong")


def bits(lines):
    return "".join("1" if x == "dương" else "0" for x in lines)


def test_every_hexagram_24_to_64_with_six_hao_matching_its_trigrams():
    assert sorted(HEX) == list(range(24, 65))
    for n, h in HEX.items():
        assert [a["hao"] for a in h["hao"]] == [1, 2, 3, 4, 5, 6], n
        assert bits(a["line"] for a in h["hao"]) == LINES[h["lower"]] + LINES[h["upper"]], n


def test_pages_lie_inside_the_pdf_and_inside_each_hexagram():
    assert H["source"]["pdf_pages"] == PDF_PAGES
    for n, h in HEX.items():
        lo, hi = h["pages"]
        assert 1 <= lo <= hi <= 121, n
        fields = [h["name_gloss"], h["tuong"], h["month"], h["nap_giap"]]
        for a in h["hao"]:
            assert lo <= a["page"] <= hi, (n, a["hao"])
            fields += [a["quote"], a["y_hao"], a["menh_hop_cach"], a["menh_khong_hop"]]
            fields += [v for v in a["tue_van"].values() if v] + a.get("tue_van_other", [])
        for f in fields:
            assert lo <= f["page"] <= hi, (n, f)
    starts = [HEX[n]["pages"][0] for n in sorted(HEX)]
    assert starts == sorted(starts)


def test_hexagram_header_fields():
    for n, h in HEX.items():
        assert 1 <= h["month"]["value"] <= 12, n
        assert h["name_gloss"]["text"] and h["tuong"]["text"], n
        ng = h["nap_giap"]
        assert ng["ages"], n
        for row in ng["ages"]:
            assert row["stems"] and set(row["stems"]) <= STEMS, n
            assert row["branches"] and set(row["branches"]) <= BRANCHES, n
        fav = ng["favoured_birth_months"]
        assert fav and 1 <= fav["from"] <= fav["to"] <= 12, n


def test_every_hao_has_its_readings():
    for n, h in HEX.items():
        for a in h["hao"]:
            for k in ("y_hao", "menh_hop_cach", "menh_khong_hop"):
                assert a[k] and a[k]["text"].strip(), (n, a["hao"], k)
            assert set(a["tue_van"]) == set(GROUPS)
            given = [v for v in a["tue_van"].values() if v] + a.get("tue_van_other", [])
            if (n, a["hao"]) == (50, 1):  # the book prints no "Xem tuế vận" block here (p.77)
                assert not given and a["tue_van_printed"] is False
            else:
                assert given, (n, a["hao"])


def test_label_misprints_are_recorded_not_hidden():
    notes = {(n, a["hao"], k) for n, h in HEX.items() for a in h["hao"] for k in ("y_hao", "menh_hop_cach", "menh_khong_hop")
             if a[k].get("label_note")}
    assert notes == {(29, 2, "menh_hop_cach"), (31, 6, "menh_khong_hop"), (45, 6, "menh_khong_hop"), (63, 6, "y_hao")}
    assert HEX[48]["heading_reprinted_on"] == 71


def test_stored_text_is_short_paraphrase_not_the_book():
    for n, h in HEX.items():
        for a in h["hao"]:
            assert len(a["quote"]["text"].split()) <= 8
            for k in ("y_hao", "menh_hop_cach", "menh_khong_hop"):
                assert len(a[k]["text"].split()) <= 60, (n, a["hao"], k)
        assert len(h["tuong"]["text"].split()) <= 60, n
    readings = json.dumps(H["hexagrams"], ensure_ascii=False).lower()
    assert "thơ rằng" not in readings


# ---------------------------------------------------------------- worked examples

def spans(ex_side):
    out = []
    for d in ex_side["dai_van"]:
        a, b = d.get("reading") or (d["from"], d["to"])
        out.append((d["hao"], a, b))
    return out


def test_worked_examples_are_complete():
    ids = [e["id"] for e in W["examples"]]
    assert ids == ["p122_mong", "p125_canh_ngo", "p126_at_hoi", "p127_binh_dan", "p127_mau_ty"]
    for e in W["examples"]:
        assert all(122 <= p <= 128 for p in e["pages"]), e["id"]
        for k in ("birth", "sum_am", "sum_duong", "tien_thien", "hau_thien", "hoa_cong", "thien_nguyen_khi", "dia_nguyen_khi", "verdict"):
            assert e.get(k) is not None, (e["id"], k)
        for side in ("tien_thien", "hau_thien"):
            q = e[side]
            assert bits(q["lines"]) == LINES[q["lower"]] + LINES[q["upper"]], (e["id"], side)
        assert e["tien_thien"]["nguyen_duong_hao"] in range(1, 7)
        assert len(e["tien_thien"]["dai_van"]) == 6
        if e["id"] == "p122_mong":
            continue  # p.122 prints only the sums, no can-chi numbers
        assert len(e["pillars"]) == 4
        for s in ("sum_am", "sum_duong"):
            assert sum(e[s]["terms"]) == e[s]["total"], (e["id"], s)
            assert e[s]["trigram"] in (e["tien_thien"]["upper"], e["tien_thien"]["lower"])
        assert e["hau_thien"]["dai_van"]


def test_printed_numbers_agree_with_the_pillars():
    nums = W["numbers_printed_in_examples"]
    for e in W["examples"][1:]:
        odd, even = [], []
        for p in e["pillars"]:
            assert nums["stems"][p["can"]] == p["can_number"] and nums["branches"][p["chi"]] == p["chi_numbers"], (e["id"], p)
            for x in [p["can_number"]] + p["chi_numbers"]:
                (odd if x % 2 else even).append(x)
        assert sorted(odd) == sorted(e["sum_duong"]["terms"]) and sorted(even) == sorted(e["sum_am"]["terms"]), e["id"]
        for s in ("sum_am", "sum_duong"):
            assert nums["trigrams"][str(e[s]["trigram_number"])] == e[s]["trigram"]


def test_dai_van_spans_follow_on_from_the_nguyen_duong():
    for e in W["examples"]:
        tt = e["tien_thien"]
        sp = spans(tt)
        assert sp[0][0] == tt["nguyen_duong_hao"] and sp[0][1] == 1, e["id"]
        assert [h for h, _, _ in sp] == [(tt["nguyen_duong_hao"] - 1 + i) % 6 + 1 for i in range(6)], e["id"]
        for (_, _, b), (_, a, _) in zip(sp, sp[1:]):
            assert a == b + 1, (e["id"], sp)
        for (h, a, b) in sp:
            assert b - a + 1 == (9 if tt["lines"][h - 1] == "dương" else 6), (e["id"], h, a, b)
        ht = e["hau_thien"]
        assert ht["start_age"] == sp[-1][2] + 1, e["id"]
        if ht["dai_van"]:
            assert spans(ht)[0][1] == ht["start_age"]


def test_p122_tue_van_lookup_points_at_que_cach_hao_6():
    t = W["examples"][0]["tue_van_example"]
    a = HEX[t["to"]["number"]]["hao"][t["to"]["hao"] - 1]
    assert a["line"] == t["to"]["line"] == "âm"
    assert a["tue_van"]["gioi_si"] and a["tue_van"]["gioi_si"]["page"] == t["lookup_page"]
    lu = W["examples"][1]
    assert HEX[56]["hao"][0]["line"] == "âm" and lu["tien_thien"]["number"] == 56 and lu["tien_thien"]["nguyen_duong_hao"] == 1


# ---------------------------------------------------------------- against the book

def _book():
    pytest.importorskip("pymupdf")
    sys.path.insert(0, str(ROOT / "tools"))
    import build_ha_lac as B
    if not B.pdf_path().exists():
        pytest.skip("Hà Lạc PDF not on this machine")
    return B


def test_quote_anchors_are_on_their_printed_pages():
    B = _book()
    pages = B.read_pages(B.pdf_path())
    assert len(pages) == PDF_PAGES
    for n, h in HEX.items():
        for a in h["hao"]:
            q = a["quote"]
            assert B.norm(q["text"]) in B.norm(pages[q["page"] - 1]), (n, a["hao"], q)
    for e in W["examples"]:
        for q in e["quotes"]:
            assert B.norm(q["text"]) in B.norm(pages[q["page"] - 1]), (e["id"], q)
    t = W["examples"][0]["tue_van_example"]
    assert "tiến lên" in B.norm(pages[t["lookup_page"] - 1]) and B.norm(t["quote"]) in B.norm(pages[t["quote_page"] - 1])


def test_rebuild_from_the_pdf_reproduces_hexagrams_json():
    _book()
    r = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "build_ha_lac.py"), "--check"], capture_output=True, text=True,
                       env={**os.environ})
    assert r.returncode == 0, r.stdout + r.stderr
