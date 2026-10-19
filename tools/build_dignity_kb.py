"""Build engine/data/dignity_kb.json — the ONE authoritative Miếu/Vượng/Đắc/Bình/Hãm knowledge base for every star the engine
places (chính tinh and phụ tinh), read by Python (tvbt/dignity.py) and TypeScript (src/interpret/dignity.ts) alike.

Also re-emits engine/data/dignity_vn.json and dignity_toanthu.json (chính tinh, old shape, kept for their existing readers).

Every cell is from a PAGE IMAGE (tools/show_page.py BOOK PAGE --image DIR). Phụ tinh transcription: tools/build_aux_dignity.py.
Result per (school, star, branch), precomputed so both languages only look up:
  VERIFIED        {value, term, school, locator, legacy?, note?, variants?}   one reading in the chosen book (or its fallback book)
  CONFLICT        {alternatives: [{value, term, locator}]}                    the book prints two readings in its own voice
  UNVERIFIED      {reason, variants?}                                         no classification found (or unreadable / experimental)
  NOT_APPLICABLE  {reason}                                                    a book says brightness is not asked for this star
`variants` = what the OTHER books say for the same cell (school disagreements are shown, never silently resolved).
Never: a guessed cell, a default 'bình', a level taken from cát/hung nature or from another star.
Run: .venv/bin/python tools/build_dignity_kb.py   (pinned by engine/tests/test_dignity_kb.py)"""
from __future__ import annotations

import importlib.util
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "engine" / "data"
BR = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
LEVELS = ["miếu", "vượng", "đắc", "lợi", "bình", "hãm"]
SCHOOLS = {"thuc_hanh": {"book": "TH", "source": "SRC_THUC_HANH", "title": "Tử Vi Thực Hành"},
           "toan_thu": {"book": "TT", "source": "SRC_TOAN_THU", "title": "Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục)"},
           "khao_luan": {"book": "KL", "source": "SRC_KHAO_LUAN", "title": "Tử Vi Khảo Luận"}}
AUX_FALLBACK = {"thuc_hanh": ["thuc_hanh", "toan_thu", "khao_luan"], "toan_thu": ["toan_thu", "thuc_hanh", "khao_luan"],
                "khao_luan": ["khao_luan", "thuc_hanh", "toan_thu"]}
TU_MO = ["Thìn", "Tuất", "Sửu", "Mùi"]


def C(locator, *groups, conflicts=None, unverified=None, note="", old_locator=None):
    """A book's table for one chính tinh. groups: (term, level, [branches]); conflicts: {branch: [(term, level, locator)]}."""
    cells = {}
    for term, level, brs in groups:
        for b in brs:
            assert b in BR and b not in cells, (locator, b)
            cells[b] = {"level": level, "term": term}
    for b in (conflicts or {}):
        assert b not in cells, (locator, b)
    return {"locator": locator, "old_locator": old_locator, "cells": cells, "conflicts": conflicts or {},
            "unverified": unverified or {}, "note": note}


# ---- chính tinh, Thực Hành (verse headers pp.29-48, every header image-checked 2026-10-18) -------------------------------------
TH = {
    "Tử Vi": C("TH p.29", ("miếu", "miếu", ["Tý", "Ngọ", "Dần", "Thân"]), ("vượng", "vượng", ["Thìn", "Tuất"]),
               ("địa", "đắc", ["Sửu", "Mùi"]), ("bình", "bình", ["Tỵ", "Hợi", "Mão", "Dậu"]), old_locator="p.29",
               note="Header 'Miếu: Tí Ngọ Dần Thân?' carries a printed '?'; p.30 prose repeats Tỵ Hợi Mão Dậu as bình hoà."),
    "Thiên Cơ": C("TH p.30", ("miếu", "miếu", ["Tý", "Ngọ"]), ("vượng", "vượng", ["Mão", "Dậu"]), ("địa", "đắc", ["Dần", "Thân"]),
                  ("bình", "bình", ["Tỵ", "Hợi"]), ("hãm", "hãm", ["Sửu", "Mùi"]), old_locator="p.30",
                  unverified={"Thìn": "printed 'Ích Thìn Tuất' — not a level of the scale (lợi ích?)", "Tuất": "as Thìn"},
                  note="'Vượng thì Mão Dậu, Địa Dần Thân': Dần Thân are đắc ('Địa', as Tử Vi p.29 and Thiên Phủ p.37), not vượng "
                       "(corrected 2026-10-18). Thìn Tuất were stored as bình before; the header prints 'Ích'."),
    "Thái Dương": C("TH p.31", ("miếu", "miếu", ["Mão"]), ("vượng", "vượng", ["Ngọ", "Tỵ", "Thìn", "Dần"]), ("bình", "bình", ["Dậu"]),
                    ("hãm", "hãm", ["Tuất", "Hợi", "Tý", "Sửu"]), old_locator="p.31"),
    "Vũ Khúc": C("TH p.34", ("miếu", "miếu", ["Sửu", "Mùi", "Thìn", "Tuất"]), ("hãm", "hãm", ["Tỵ", "Hợi"]),
                 unverified={"Mão": "prose 'Vũ tại Mão Dậu tuy cũng khá' — 'khá' is not a level", "Dậu": "as Mão"},
                 old_locator="p.34 (prose only: miếu Sửu Mùi Thìn Tuất; hãm Tỵ Hợi; Mão Dậu 'khá' unclassified)",
                 note="No verse header (p.33): prose only."),
    "Thiên Đồng": C("TH p.35", ("miếu", "miếu", ["Tỵ", "Hợi"]), ("vượng", "vượng", ["Tý", "Thân"]),
                    ("bình", "bình", ["Mão", "Dậu", "Tuất", "Thìn"]), ("lợi", "đắc", ["Dần"]), ("hãm", "hãm", ["Ngọ", "Mùi", "Sửu"]),
                    old_locator="p.35", note="'Lợi về độc chiếm nơi Dần ấy': stored as đắc before this audit — legacy reading, see LEGACY."),
    "Liêm Trinh": C("TH p.36", ("miếu", "miếu", ["Dần", "Thân", "Tý", "Ngọ"]), ("vượng", "vượng", ["Thìn", "Tuất", "Sửu", "Mùi"]),
                    ("hãm", "hãm", ["Tỵ", "Hợi", "Dậu", "Mão"]), old_locator="p.36",
                    note="'Cùng là Dậu Mão' is settled by p.37 prose 'LIÊM HÃM ĐỊA (Tỵ Hợi, Dậu Mão)'."),
    "Thiên Phủ": C("TH p.37", ("miếu", "miếu", ["Sửu", "Mùi", "Thìn", "Tuất", "Mão"]), ("vượng", "vượng", ["Tý", "Ngọ"]),
                   ("địa", "đắc", ["Dậu", "Tỵ", "Hợi", "Dần", "Thân"]), old_locator="p.37"),
    "Thái Âm": C("TH p.39", ("miếu", "miếu", ["Hợi", "Tý", "Sửu"]), ("vượng", "vượng", ["Dậu", "Tuất"]),
                 ("lợi ích", "đắc", ["Mùi", "Thân"]), ("hãm", "hãm", ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ"]), old_locator="p.39",
                 note="'Mùi, Thân lợi ích đôi phương'; p.40 prose calls them 'cung đắc địa thôi (không phải Miếu, Vượng địa)'."),
    "Tham Lang": C("TH p.40", ("miếu", "miếu", ["Sửu", "Mùi", "Thìn", "Tuất"]), ("địa", "đắc", ["Dần", "Thân"]),
                   ("bình", "bình", ["Tý", "Ngọ"]), ("hãm", "hãm", ["Mão", "Dậu", "Tỵ", "Hợi"]), old_locator="p.40",
                   note="Printed 'bính : Tí, ngọ'; p.42 prose 'Tham ở BINH địa Tí Ngọ' and 'THAM HÃM ĐỊA (Tỵ, Hợi Mão, Dậu)'. "
                        "KL p.189 gives Tý Ngọ as hãm (school variant)."),
    "Cự Môn": C("TH p.42", ("miếu", "miếu", ["Mão", "Dậu"]), ("vượng", "vượng", ["Tý", "Ngọ", "Dần"]), ("đắc", "đắc", ["Thân", "Hợi"]),
                ("hãm", "hãm", ["Thìn", "Tuất", "Sửu", "Mùi", "Tỵ"]), old_locator="p.42"),
    "Thiên Tướng": C("TH p.44", ("miếu", "miếu", ["Dần", "Thân"]), ("vượng", "vượng", ["Tý", "Ngọ", "Tuất", "Thìn"]),
                     ("đắc", "đắc", ["Tỵ", "Hợi", "Sửu", "Mùi"]), ("hãm", "hãm", ["Mão", "Dậu"]), old_locator="p.44"),
    "Thiên Lương": C("TH p.45", ("miếu", "miếu", ["Ngọ", "Tuất", "Thìn"]), ("vượng", "vượng", ["Tý", "Mão", "Dần", "Thân"]),
                     ("đắc", "đắc", ["Mùi", "Sửu"]), ("hãm", "hãm", ["Tỵ", "Hợi", "Dậu"]), old_locator="p.45"),
    "Thất Sát": C("TH p.46", ("miếu", "miếu", ["Dần", "Thân", "Tý", "Ngọ"]), ("vượng", "vượng", ["Tỵ", "Hợi"]),
                  ("địa", "đắc", ["Sửu", "Mùi"]), ("hãm", "hãm", ["Mão", "Dậu", "Thìn", "Tuất"]), old_locator="p.46"),
    "Phá Quân": C("TH pp.47-48", ("miếu", "miếu", ["Tý", "Ngọ"]), ("vượng", "vượng", ["Mùi", "Sửu"]), ("địa", "đắc", ["Thìn", "Tuất"]),
                  ("bình", "bình", ["Tỵ", "Hợi"]), ("hãm", "hãm", ["Dần", "Thân", "Mão", "Dậu"]), old_locator="pp.47-48",
                  note="'Cùng là Mão Dậu' is settled by p.49 prose 'Phá hãm địa tại Mão Dậu'."),
}

# ---- chính tinh, Toàn Thư (phú lists / Hi Di prose, pp.21-40, image-checked) ------------------------------------------------------
TT = {
    "Tử Vi": C("TT p.21", ("miếu", "miếu", ["Dần", "Ngọ"]), ("vượng", "vượng", ["Thân", "Hợi", "Thìn", "Tỵ", "Tý", "Sửu", "Mùi"]),
               ("bình", "bình", ["Mão", "Dậu"]), old_locator="PDF p.21"),
    "Thiên Cơ": C("TT p.24", ("miếu", "miếu", ["Tý", "Ngọ"]), ("bình", "bình", ["Tỵ", "Hợi", "Thìn", "Tuất"]), ("hãm", "hãm", ["Sửu", "Mùi"]),
                  old_locator="PDF p.24", note="Hi Di prose. The song 'Thìn Tuất Tí Ngọ địa / Nhập miếu hữu công danh' is poetic, kept as a reported variant."),
    "Thái Dương": C("TT p.26", ("miếu", "miếu", ["Ngọ", "Mão"]), ("vượng", "vượng", ["Dần", "Thìn", "Tỵ"]), ("hãm", "hãm", ["Tuất", "Hợi", "Tý"]),
                    old_locator="PDF p.26"),
    "Vũ Khúc": C("TT p.27", ("miếu", "miếu", ["Sửu", "Mùi", "Tuất"]), ("vượng", "vượng", ["Tý", "Ngọ"]), ("bình", "bình", ["Tỵ", "Hợi"]),
                 old_locator="PDF p.27"),
    "Thiên Đồng": C("TT p.28", ("miếu", "miếu", ["Tỵ", "Hợi"]), ("vượng", "vượng", ["Tý", "Thân"]), ("hãm", "hãm", ["Ngọ", "Sửu", "Mùi", "Dậu"]),
                    old_locator="PDF p.28"),
    "Liêm Trinh": C("TT p.29", ("miếu", "miếu", ["Dần", "Thân", "Tý", "Ngọ"]), ("bình", "bình", ["Thìn", "Tuất", "Sửu", "Mùi"]),
                    ("hãm", "hãm", ["Tỵ", "Hợi", "Dậu", "Mão"]), old_locator="PDF p.29"),
    "Thiên Phủ": C("TT p.30", ("miếu", "miếu", ["Tý", "Sửu", "Dần", "Mùi"]), ("vượng", "vượng", ["Ngọ", "Mão", "Thìn", "Tuất"]),
                   ("bình", "bình", ["Dậu", "Tỵ", "Thân", "Hợi"]), old_locator="PDF p.30"),
    "Thái Âm": C("TT p.31", ("miếu", "miếu", ["Dậu"]), ("hãm", "hãm", ["Ngọ", "Dần", "Thìn", "Tỵ", "Mão"]), old_locator="PDF p.31",
                 conflicts={"Hợi": [("miếu", "miếu", "TT p.31 phú"), ("đắc", "đắc", "TT p.31 Hi Di")],
                            "Tuất": [("miếu", "miếu", "TT p.31 phú"), ("đắc", "đắc", "TT p.31 Hi Di")],
                            "Tý": [("vượng", "vượng", "TT p.31 phú"), ("đắc", "đắc", "TT p.31 Hi Di")],
                            "Sửu": [("vượng", "vượng", "TT p.31 phú"), ("đắc", "đắc", "TT p.31 Hi Di")]},
                 note="Phú: miếu Dậu Hợi Tuất, vượng Tý Sửu, hãm Ngọ Dần Thìn Tỵ Mão. Hi Di prose on the same page: 'Mão Thìn Tị Ngọ là hãm "
                      "địa, Dậu Tuất Hợi Tí Sửu là đắc địa, miếu tại cung Dậu'."),
    "Tham Lang": C("TT p.32", ("miếu", "miếu", ["Thìn", "Tuất", "Sửu", "Mùi"]), ("vượng", "vượng", ["Ngọ"]), ("hãm", "hãm", ["Hợi", "Mão", "Dậu"]),
                   conflicts={"Tý": [("vượng", "vượng", "TT p.32"), ("hãm", "hãm", "TT p.32")]}, old_locator="PDF p.32 (text layer lists Tý as both vượng and hãm: Tý omitted)"),
    "Cự Môn": C("TT p.34", ("miếu", "miếu", ["Mão", "Dậu", "Dần", "Thân"]), ("vượng", "vượng", ["Tý", "Ngọ", "Hợi"]),
                ("hãm", "hãm", ["Tỵ", "Thìn", "Tuất", "Sửu", "Mùi"]), old_locator="PDF p.34"),
    "Thiên Tướng": C("TT p.35", ("miếu", "miếu", ["Tý", "Ngọ", "Dần", "Thân"]), ("đắc", "đắc", ["Tỵ", "Hợi", "Sửu", "Mùi"]),
                     ("hãm", "hãm", ["Mão", "Dậu"]), old_locator="PDF p.35", note="p.36 reports a phú nôm (Vietnamese) giving Thìn Tuất miếu: variant."),
    "Thiên Lương": C("TT pp.37-38", ("miếu", "miếu", ["Tuất", "Thìn", "Ngọ"]), ("vượng", "vượng", ["Sửu", "Mùi", "Tý", "Mão", "Dần", "Thân"]),
                     ("hãm", "hãm", ["Tỵ", "Hợi", "Dậu"]), old_locator="PDF pp.37-38"),
    "Thất Sát": C("TT p.39", ("miếu", "miếu", ["Dần", "Thân", "Tý", "Ngọ"]), ("bình", "bình", ["Mão", "Dậu", "Sửu", "Mùi", "Tỵ", "Hợi"]),
                  old_locator="PDF p.39 (the book itself notes the source is inconsistent about hãm)",
                  note="The phú ends 'vô hãm địa' while the song says 'Sát cư hãm địa'; no branch is named for hãm, so Thìn Tuất stay unknown."),
    "Phá Quân": C("TT p.40", ("miếu", "miếu", ["Tý", "Ngọ"]), ("vượng", "vượng", ["Thìn", "Tuất", "Sửu", "Mùi"]),
                  ("hãm", "hãm", ["Tỵ", "Hợi", "Dần", "Thân", "Mão", "Dậu"]), old_locator="PDF p.40"),
}

# ---- chính tinh, Khảo Luận ('Tóm tắt về các sao quan trọng', pp.186-190; no table for Tử Vi) --------------------------------------
KL = {
    "Thiên Cơ": C("KL p.187", ("miếu", "miếu", ["Thìn", "Tuất", "Mão", "Dậu"]), ("vượng", "vượng", ["Tỵ", "Thân"]),
                  ("đắc", "đắc", ["Tý", "Ngọ", "Sửu", "Mùi"]), ("hãm", "hãm", ["Dần", "Hợi"])),
    "Thái Dương": C("KL p.187", ("miếu", "miếu", ["Tỵ", "Ngọ"]), ("vượng", "vượng", ["Dần", "Mão", "Thìn"]), ("đắc", "đắc", ["Sửu", "Mùi"]),
                    ("hãm", "hãm", ["Thân", "Dậu", "Tuất", "Hợi", "Tý"])),
    "Vũ Khúc": C("KL p.187", ("miếu", "miếu", TU_MO), ("vượng", "vượng", ["Dần", "Thân", "Tý", "Ngọ"]), ("đắc", "đắc", ["Mão", "Dậu"]),
                 ("hãm", "hãm", ["Tỵ", "Hợi"])),
    "Thiên Đồng": C("KL p.188", ("miếu", "miếu", ["Dần", "Thân"]), ("vượng", "vượng", ["Tý"]), ("đắc", "đắc", ["Mão", "Tỵ", "Hợi"]),
                    ("hãm", "hãm", ["Thìn", "Tuất", "Sửu", "Mùi", "Ngọ", "Dậu"])),
    "Liêm Trinh": C("KL p.188", ("miếu", "miếu", ["Thìn", "Tuất"]), ("vượng", "vượng", ["Tý", "Ngọ", "Dần", "Thân"]),
                    ("hãm", "hãm", ["Tỵ", "Hợi", "Mão", "Dậu"])),
    "Thiên Phủ": C("KL p.188", ("miếu", "miếu", ["Dần", "Thân", "Tý", "Ngọ"]), ("vượng", "vượng", ["Thìn", "Tuất"]),
                   ("đắc", "đắc", ["Tỵ", "Hợi", "Mùi"]), ("bình hòa", "bình", ["Mão", "Dậu", "Sửu"])),
    "Thái Âm": C("KL p.188", ("miếu", "miếu", ["Dậu", "Tuất", "Hợi"]), ("vượng", "vượng", ["Thân", "Tý"]), ("đắc", "đắc", ["Sửu", "Mùi"]),
                 ("hãm", "hãm", ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ"])),
    "Tham Lang": C("KL p.189", ("miếu", "miếu", ["Sửu", "Mùi"]), ("hãm", "hãm", ["Tỵ", "Hợi", "Tý", "Ngọ", "Mão", "Dậu"]),
                   conflicts={"Thìn": [("vượng", "vượng", "KL p.189"), ("miếu", "miếu", "KL p.101")],
                              "Tuất": [("vượng", "vượng", "KL p.189"), ("miếu", "miếu", "KL p.101")],
                              "Dần": [("đắc", "đắc", "KL p.189"), ("vượng", "vượng", "KL p.101")],
                              "Thân": [("đắc", "đắc", "KL p.189"), ("vượng", "vượng", "KL p.101")]},
                   note="p.101 ('Thế đứng của Tham lang'): miếu Thìn Tuất Sửu Mùi, vượng Dần Thân, hãm Tí Ngọ Mão Dậu Tỵ Hợi."),
    "Cự Môn": C("KL p.189", ("miếu", "miếu", ["Mão", "Dậu"]), ("vượng", "vượng", ["Tý", "Ngọ", "Dần"]), ("đắc", "đắc", ["Thân", "Hợi"]),
                ("hãm", "hãm", ["Thìn", "Tuất", "Sửu", "Mùi", "Tỵ"])),
    "Thiên Tướng": C("KL p.189", ("miếu", "miếu", ["Dần", "Thân"]), ("vượng", "vượng", ["Thìn", "Tuất", "Tý", "Ngọ"]),
                     ("đắc", "đắc", ["Sửu", "Mùi", "Tỵ", "Hợi"]), ("hãm", "hãm", ["Mão", "Dậu"])),
    "Thiên Lương": C("KL p.189", ("miếu", "miếu", ["Thìn", "Tuất", "Ngọ"]), ("vượng", "vượng", ["Dần", "Thân", "Tý", "Mão"]),
                     ("đắc", "đắc", ["Sửu", "Mùi"]), ("hãm", "hãm", ["Dậu", "Tỵ", "Hợi"])),
    "Thất Sát": C("KL p.190", ("miếu", "miếu", ["Dần", "Thân", "Tý", "Ngọ"]), ("vượng", "vượng", ["Tỵ", "Hợi"]), ("đắc", "đắc", ["Sửu", "Mùi"]),
                  ("hãm", "hãm", ["Mão", "Dậu", "Thìn", "Tuất"])),
    "Phá Quân": C("KL p.190", ("miếu", "miếu", ["Tý", "Ngọ"]), ("vượng", "vượng", ["Sửu", "Mùi"]), ("đắc", "đắc", ["Thìn", "Tuất"]),
                  ("hãm", "hãm", ["Mão", "Dậu", "Dần", "Thân", "Tỵ", "Hợi"]), note="Tỵ Hợi hãm from p.115 (same table, fuller)."),
}

# Reported variants (another tradition quoted inside a book): shown next to the result, never used as the result.
REPORTED = [
    ("Thiên Tướng", "toan_thu", "TT p.36", {"Thìn": "miếu", "Tuất": "miếu"}, "phú nôm quoted by Vũ Tài Lục"),
    ("Thiên Cơ", "toan_thu", "TT p.24", {"Thìn": "miếu", "Tuất": "miếu"}, "song 'Thìn Tuất Tí Ngọ địa, nhập miếu hữu công danh'"),
]

# lợi read as đắc before aux-dignity-1: kept (production unchanged) and marked legacy until a reviewer decides.
LEGACY = {("thuc_hanh", "Thiên Đồng", "Dần"), ("thuc_hanh", "Văn Xương", "Hợi")} | {("toan_thu", "Văn Xương", b) for b in ("Tý", "Thìn", "Thân", "Hợi", "Mão", "Mùi")}

# Toàn Thư's own song / translation against its phú list for Văn Xương (p.41): the book says it cannot be settled (p.42).
AUX_CONFLICTS = {
    ("toan_thu", "Văn Xương"): {"Thìn": [("lợi", "đắc", "TT p.41 phú"), ("vượng", "vượng", "TT p.41 ca")],
                                "Tỵ": [("miếu", "miếu", "TT p.41 phú"), ("vượng", "vượng", "TT p.41 ca")],
                                "Ngọ": [("hãm", "hãm", "TT p.41 phú"), ("lợi", "lợi", "TT p.41 ca")],
                                "Mão": [("lợi", "đắc", "TT p.41 phú"), ("bất lợi", None, "TT p.41 ca")],
                                "Dậu": [("miếu", "miếu", "TT p.41 phú"), ("bất lợi", None, "TT p.41 ca")]},
    ("toan_thu", "Kình Dương"): {"Tý": [("vượng", "vượng", "TT p.50 phú 1"), ("hãm", "hãm", "TT p.50 phú 4")]},
    ("thuc_hanh", "Linh Tinh"): {"Tỵ": [("miếu", "miếu", "TH p.64 Miếu line"), ("hãm", "hãm", "TH p.64 Hãm line")]},
}

NOT_APPLICABLE = {
    "Thiên Thương": "TT p.54: 'Thái Tuế gặp Thiên Thương, Thiên Sứ không cần hỏi đắc địa hay không đắc địa'.",
    "Thiên Sứ": "TT p.54 (as Thiên Thương).",
}

TU_HOA = ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"]
ALIASES = {"Thiên Diêu": "Thiên Riêu", "Hoả Tinh": "Hỏa Tinh", "Tử vi": "Tử Vi", "Nhật": "Thái Dương", "Nguyệt": "Thái Âm",
           "Dương Nhận": "Kình Dương", "Kình": "Kình Dương", "Đà": "Đà La", "Bật": "Hữu Bật", "Tràng Sinh": "Trường Sinh",
           "Thiên Hỉ": "Thiên Hỷ", "Bát Toạ": "Bát Tọa", "Thiên Quí": "Thiên Quý", "Hoá Lộc": "Hóa Lộc", "Hoá Quyền": "Hóa Quyền",
           "Hoá Khoa": "Hóa Khoa", "Hoá Kỵ": "Hóa Kỵ", "Hóa Kị": "Hóa Kỵ", "Nguyệt Tướng": "Đẩu Quân"}


ID_OVERRIDE = {"Quan Phủ": "quan_phu_loc_ton", "Quan Phù": "quan_phu_thai_tue"}   # identical once marks are stripped


def slug(name: str) -> str:
    """Star id: NFD, marks stripped, đ->d, lower, spaces->_ (mirrored by src/interpret/dignity.ts starId)."""
    s = unicodedata.normalize("NFD", name.replace("Đ", "D").replace("đ", "d"))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower().strip().replace(" ", "_")


def _aux_module():
    spec = importlib.util.spec_from_file_location("build_aux_dignity", ROOT / "tools" / "build_aux_dignity.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def inventory() -> dict[str, str]:
    """Every star the engine places, with its group (deterministic sweep over all year stems/branches, months, hours, four days)."""
    sys.path.insert(0, str(ROOT / "engine"))
    from tvbt import tuvi
    from tvbt.calendar_core import BirthInput, normalize
    names: dict[str, str] = {}
    for y in range(1984, 1996):
        for m in range(1, 13):
            for h in range(0, 24, 2):
                for d in (1, 9, 17, 25):
                    for s in tuvi.compute(normalize(BirthInput(y, m, d, h, 10, "Asia/Ho_Chi_Minh", ("male", "female")[d % 2]))).stars:
                        names.setdefault(s.name, s.group)
    return names


def _cell(level, term, locator, school, **extra):
    return {"status": "VERIFIED", "value": level, "term": term, "school": school, "locator": locator, **{k: v for k, v in extra.items() if v}}


def build() -> dict:
    aux = _aux_module().build()
    inv = inventory()
    stars = {}
    for n, g in inv.items():
        kind = "chinh_tinh" if g.startswith("chính tinh") else "phu_tinh"
        stars[n] = {"id": ID_OVERRIDE.get(n, slug(n)), "kind": kind, "group": g.replace(" (chưa đối chiếu sách)", "")}
    for h in TU_HOA:
        stars[h] = {"id": slug(h), "kind": "tu_hoa", "group": "Tứ Hóa"}
    ids = [s["id"] for s in stars.values()]
    assert len(ids) == len(set(ids)), "star id collision"
    # lookup keys (see normalize_star): every id, every name's mark-stripped slug unless two stars share it, and the aliases
    by_slug: dict[str, set] = {}
    for n, meta in stars.items():
        by_slug.setdefault(slug(n), set()).add(meta["id"])
    aliases = {k: next(iter(v)) for k, v in by_slug.items() if len(v) == 1}
    aliases.update({slug(a): stars[t]["id"] for a, t in ALIASES.items()})
    ambiguous = sorted(k for k, v in by_slug.items() if len(v) > 1)

    major = {"thuc_hanh": TH, "toan_thu": TT, "khao_luan": KL}
    aux_t = aux["tables"]
    exp_by = {}
    for e in aux["experimental"]:
        exp_by.setdefault((e["school"], e["star"]), []).append(e)

    def major_cell(school, star, b):
        t = major[school].get(star)
        if not t:
            return None, None
        if b in t["cells"]:
            c = t["cells"][b]
            return _cell(c["level"], c["term"], t["locator"], school, legacy=(school, star, b) in LEGACY or None), t
        if b in t["conflicts"]:
            return {"status": "CONFLICT", "school": school,
                    "alternatives": [{"value": lv, "term": tm, "locator": loc} for tm, lv, loc in t["conflicts"][b]]}, t
        return {"status": "UNVERIFIED", "school": school,
                "reason": t["unverified"].get(b) or f"{t['locator']} does not name {b}"}, t

    def aux_cell(school, star, b):
        for sc in AUX_FALLBACK[school]:
            t = aux_t[sc].get(star)
            if not t:
                continue
            conf = AUX_CONFLICTS.get((sc, star), {})
            if b in conf:
                return {"status": "CONFLICT", "school": sc,
                        "alternatives": [{"value": lv, "term": tm, "locator": loc} for tm, lv, loc in conf[b]]}
            c = t["cells"].get(b)
            if c:
                return _cell(c["level"], c["term"], t["locator"], sc, legacy=c.get("legacy") and True)
            reason = next((e["reason"] for e in exp_by.get((sc, star), []) if b in e["cells"]), None)
            return {"status": "UNVERIFIED", "school": sc, "reason": reason or f"{t['locator']} does not name {b}"}
        return None

    def own_level(school, star, b):
        """What one book says for a cell (for `variants`): its own table only, no fallback."""
        t = (major if star in TH else aux_t)[school].get(star) if school in major else None
        if not t:
            return None
        if star in TH:
            c = t["cells"].get(b)
            return c and {"school": school, "value": c["level"], "term": c["term"], "locator": t["locator"]}
        if b in AUX_CONFLICTS.get((school, star), {}):
            return None
        c = t["cells"].get(b)
        return c and {"school": school, "value": c["level"], "term": c["term"], "locator": t["locator"]}

    resolved = {}
    for school in SCHOOLS:
        R = resolved[school] = {}
        for star, meta in stars.items():
            row = {}
            for b in BR:
                if star in NOT_APPLICABLE:
                    r = {"status": "NOT_APPLICABLE", "reason": NOT_APPLICABLE[star]}
                elif meta["kind"] == "chinh_tinh":
                    r, _ = major_cell(school, star, b)
                    r = r or {"status": "UNVERIFIED", "school": school, "reason": f"{SCHOOLS[school]['title']} gives no table for {star}"}
                elif meta["kind"] == "tu_hoa":
                    e = next((e for e in aux["experimental"] if e["star"] == star), None)
                    r = {"status": "UNVERIFIED", "reason": "Tứ Hóa: book tables exist but are kept experimental "
                                                           f"({e['locator']}: {e['reason']})" if e else "no table"}
                else:
                    r = aux_cell(school, star, b) or {"status": "UNVERIFIED", "reason": aux["no_table"].get(star, "no book gives a per-branch classification")}
                mine = r.get("value") if r["status"] == "VERIFIED" else None
                var = [v for sc in SCHOOLS if sc != r.get("school") for v in [own_level(sc, star, b)] if v and v["value"] != mine]
                var += [{"school": sc, "value": cells[b], "term": cells[b], "locator": loc, "reported": why}
                        for (st, sc, loc, cells, why) in REPORTED if st == star and b in cells]
                if var and r["status"] != "NOT_APPLICABLE":
                    r["variants"] = var
                row[b] = r
            R[star] = row
    return {
        "version": "dignity-kb-1",
        "levels": LEVELS,
        "statuses": ["VERIFIED", "CONFLICT", "UNVERIFIED", "NOT_APPLICABLE"],
        "schools": SCHOOLS,
        "default_school": "thuc_hanh",
        "branches": BR,
        "stars": stars,
        "aliases": aliases,
        "ambiguous": ambiguous,
        "resolved": resolved,
        "note": "Generated by tools/build_dignity_kb.py. Only VERIFIED results carry a level; rules and badges never see the others.",
    }


def legacy_tables(kb: dict) -> dict[str, dict]:
    """dignity_vn.json / dignity_toanthu.json in their original shape (VERIFIED chính tinh cells of each book)."""
    out = {}
    for school, fname, book in (("thuc_hanh", "dignity_vn.json", TH), ("toan_thu", "dignity_toanthu.json", TT)):
        old = json.loads((DATA / fname).read_text("utf-8"))
        stars = {}
        for star, t in book.items():
            stars[star] = {"locator": t["old_locator"], "levels": {b: c["level"] for b, c in t["cells"].items()}}
        out[fname] = {**old, "generated_by": "tools/build_dignity_kb.py (edit there; see dignity_kb.json for statuses)", "stars": stars}
    return out


if __name__ == "__main__":
    kb = build()
    (DATA / "dignity_kb.json").write_text(json.dumps(kb, ensure_ascii=False, separators=(",", ":")) + "\n", "utf-8")
    for fname, d in legacy_tables(kb).items():
        (DATA / fname).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", "utf-8")
    n = {s: 0 for s in kb["statuses"]}
    for row in kb["resolved"]["thuc_hanh"].values():
        for r in row.values():
            n[r["status"]] += 1
    print("wrote dignity_kb.json:", len(kb["stars"]), "stars; thuc_hanh cells", n)
