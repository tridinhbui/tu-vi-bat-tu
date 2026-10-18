"""Build engine/data/dignity_aux.json: Miếu/Vượng/Đắc/Bình/Hãm of the phụ tinh, per book, per cell.

Every cell below was read from the PAGE IMAGE (tools/show_page.py BOOK PAGE --image DIR), not only from the text layer
(the Thực Hành text layer scrambles line order). Rules of transcription:
  * only a branch the book names gets a value; every other branch stays unknown (absent);
  * `term` is the word the book prints; `level` is what rules see. 'đắc cách' (TH p.51, Tả Hữu) is read as đắc (KL p.121
    says đắc địa for the same branches). 'lợi' (lợi địa) is its OWN level: TH p.64 lists Miếu / Đắc / Lợi / Hãm as four
    tiers, so lợi is not đắc, and no rule gates on it. The only exception is Văn Xương, whose lợi cells were read as đắc
    before this table existed (dignity_aux_th / dignity_minor); they keep level đắc, marked `legacy`, so no production
    reading changes without a reviewer deciding it. The badge always prints the book's term;
  * a cell the book prints twice with different levels, or that rests on a misprint we cannot resolve, is NOT in the
    production table: it goes to `experimental` with the reason;
  * second-hand quotes inside a book (e.g. Toàn Thư quoting "Tử Vi Việt") are experimental too.
Run:  python tools/build_aux_dignity.py      (rewrites the JSON; tests in engine/tests/test_aux_dignity.py pin it)
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "engine" / "data" / "dignity_aux.json"
BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
TU_MO, TU_SINH = ["Thìn", "Tuất", "Sửu", "Mùi"], ["Dần", "Thân", "Tỵ", "Hợi"]
LEVEL = {"miếu": "miếu", "vượng": "vượng", "đắc": "đắc", "lợi": "lợi", "đắc cách": "đắc", "bình": "bình", "hãm": "hãm"}


def T(locator: str, *groups: tuple[str, list[str]], note: str = "", legacy_loi: bool = False) -> dict:
    cells: dict[str, dict] = {}
    for term, brs in groups:
        for b in brs:
            assert b in BRANCHES, b
            assert b not in cells, f"{locator}: {b} given twice"   # double printing must be resolved by hand, never silently
            cells[b] = {"level": LEVEL[term], "term": term}
            if term == "lợi" and legacy_loi:
                cells[b] = {"level": "đắc", "term": term, "legacy": "lợi read as đắc before aux-dignity-1; kept to avoid changing production"}
    return {"locator": locator, "cells": cells, **({"note": note} if note else {})}


def others(*taken: list[str]) -> list[str]:
    t = {b for g in taken for b in g}
    return [b for b in BRANCHES if b not in t]


TH = {
    "Văn Xương": T("TH p.50", ("miếu", ["Tỵ", "Dậu", "Sửu"]), ("đắc", ["Thân", "Tý", "Thìn"]), ("lợi", ["Hợi"]),
                   ("hãm", ["Dần", "Ngọ", "Tuất"]),
                   note="Printed 'Đắc địa: Thân Tí Thân' (Thìn read from the parallel Văn Khúc line and TT p.41) and "
                        "'Lợi địa: Hợi Dậu' (Dậu is already miếu on the same line; the second lợi branch is left unknown).",
                   legacy_loi=True),
    "Văn Khúc": T("TH p.50", ("miếu", ["Tỵ", "Sửu", "Dậu"]), ("vượng", ["Hợi", "Mão", "Mùi"]), ("đắc", ["Thân", "Tý", "Thìn"]),
                  ("bình", ["Dần"]), ("hãm", ["Ngọ", "Tuất"])),
    "Tả Phụ": T("TH p.51", ("đắc cách", TU_MO), note="Header 'Đắc cách: Thìn Tuất Sửu Mùi' (KL p.121 says đắc địa tứ mộ)."),
    "Hữu Bật": T("TH p.51", ("đắc cách", TU_MO), note="Shared header with Tả Phụ."),
    "Thiên Mã": T("TH p.52", ("đắc", ["Tỵ", "Dần"])),
    "Long Trì": T("TH p.54", ("đắc", ["Sửu", "Mùi"])),
    "Phượng Các": T("TH p.54", ("đắc", ["Sửu", "Mùi"])),
    "Kình Dương": T("TH p.62", ("đắc", TU_MO), ("hãm", ["Tý", "Ngọ", "Mão", "Dậu"])),
    "Đà La": T("TH p.63", ("đắc", TU_MO), ("hãm", ["Dần", "Thân", "Tỵ", "Hợi"])),
    "Hỏa Tinh": T("TH p.64", ("miếu", ["Dần", "Ngọ", "Tuất"]), ("đắc", ["Tỵ", "Dậu", "Sửu"]), ("lợi", ["Hợi", "Mão", "Mùi"]),
                  ("hãm", ["Thân", "Tý", "Thìn"])),
    "Linh Tinh": T("TH p.64", ("miếu", ["Dần", "Tuất"]), ("hãm", ["Hợi", "Dậu", "Sửu"]),
                   note="Printed 'Miếu: Dần, Tuất – Thìn, Tỵ, Mùi / Hãm: Tỵ, Hợi, Dậu, Sửu'. Thìn, Mùi follow a dash whose "
                        "label is missing and Tỵ is printed under both: those three are experimental."),
    "Đại Hao": T("TH p.65", ("đắc", ["Mão", "Dậu", "Dần", "Thân"]), ("hãm", ["Tý", "Ngọ", "Tỵ", "Hợi"]), note="'Song Hao' header."),
    "Tiểu Hao": T("TH p.65", ("đắc", ["Mão", "Dậu", "Dần", "Thân"]), ("hãm", ["Tý", "Ngọ", "Tỵ", "Hợi"]), note="'Song Hao' header."),
    "Tang Môn": T("TH p.65", ("đắc", ["Dần", "Thân", "Mão", "Dậu"])),
    "Bạch Hổ": T("TH p.65", ("đắc", ["Dần", "Thân", "Mão", "Dậu"])),
    "Thiên Khốc": T("TH p.66", ("miếu", ["Tý", "Ngọ"]), ("lợi", ["Mão", "Dậu", "Sửu", "Mùi"]), ("hãm", ["Thìn", "Tuất"]),
                    note="Hãm Thìn Tuất is from the prose on the same page ('Khốc, Hư hãm ở Thìn, Tuất')."),
    "Thiên Hư": T("TH p.66", ("miếu", ["Tý", "Ngọ"]), ("lợi", ["Mão", "Dậu", "Sửu", "Mùi"]), ("hãm", ["Thìn", "Tuất"]),
                  note="Shared header with Thiên Khốc."),
    "Thiên Hình": T("TH p.67", ("đắc", ["Dần", "Thân", "Mão", "Dậu"])),
    "Địa Không": T("TH p.67", ("đắc", ["Tỵ", "Hợi", "Dần", "Thân"])),
    "Địa Kiếp": T("TH p.67", ("đắc", ["Tỵ", "Hợi", "Dần", "Thân"])),
    "Thiên Riêu": T("TH p.68", ("đắc", ["Dần", "Mão", "Dậu", "Tuất"]), note="Printed as 'Thiên Diêu'."),
}

TT = {
    "Văn Xương": T("TT p.41", ("miếu", ["Tỵ", "Dậu", "Sửu"]), ("lợi", ["Thân", "Tý", "Thìn", "Hợi", "Mão", "Mùi"]),
                   ("hãm", ["Dần", "Ngọ", "Tuất"]),
                   note="The phú list. The song on the same page differs (see experimental) and p.42 calls the matter 'lung tung'.",
                   legacy_loi=True),
    "Văn Khúc": T("TT p.43", ("miếu", ["Tý", "Thìn", "Tỵ", "Dậu", "Sửu"]), ("vượng", ["Hợi", "Mão", "Mùi"]), ("hãm", ["Ngọ", "Tuất"])),
    "Kình Dương": T("TT p.50", ("miếu", TU_MO), ("vượng", ["Hợi", "Thân"]), ("hãm", ["Mão", "Tỵ", "Dậu", "Ngọ"]),
                    note="Tý is printed vượng in the first phú and hãm in the fourth ('bốn cung hãm Tí, Ngọ, Mão, Dậu'): experimental."),
    "Đà La": T("TT p.51", ("miếu", TU_MO), ("hãm", ["Mão", "Dậu"]), ("bình", ["Tỵ", "Hợi"])),
    "Hỏa Tinh": T("TT p.52", ("miếu", ["Dần", "Ngọ", "Tuất"]), ("bình", ["Tỵ", "Dậu", "Sửu"]), ("hãm", ["Hợi"])),
    "Lộc Tồn": T("TT p.47", ("miếu", BRANCHES), note="'Thập nhị cung đều là miếu địa. Không có hãm địa đối với Lộc Tồn.'"),
}

KL = {
    "Văn Xương": T("KL p.192", ("đắc", TU_MO + ["Tỵ", "Hợi"]), note="'Xương Khúc đắc địa ở Tứ mộ và Tỵ Hợi'; hãm branches not named."),
    "Văn Khúc": T("KL p.192", ("đắc", TU_MO + ["Tỵ", "Hợi"]), note="Shared sentence with Văn Xương."),
    "Tả Phụ": T("KL p.121", ("đắc", TU_MO), ("hãm", others(TU_MO)), note="'Tả Hữu đắc địa tứ mộ, còn hãm địa tất cả các cung khác.'"),
    "Hữu Bật": T("KL p.121", ("đắc", TU_MO), ("hãm", others(TU_MO))),
    "Kình Dương": T("KL p.200", ("đắc", TU_MO), note="p.143 also reports a variant (Đà đắc Tứ chính) and argues for tứ mộ."),
    "Đà La": T("KL p.200", ("đắc", TU_MO + ["Tỵ", "Hợi"])),
    "Địa Không": T("KL p.199", ("đắc", TU_SINH), ("hãm", others(TU_SINH))),
    "Địa Kiếp": T("KL p.199", ("đắc", TU_SINH), ("hãm", others(TU_SINH))),
    "Kiếp Sát": T("KL p.201", ("đắc", TU_SINH)),
    "Thiên Hình": T("KL pp.201-202", ("đắc", ["Dần", "Thân", "Mão", "Dậu"]), ("hãm", others(["Dần", "Thân", "Mão", "Dậu"])),
                    note="p.202: 'Nếu Thiên hình không nằm trong Dần, Thân, Mão, Dậu … hãm địa'."),
    "Thiên Khốc": T("KL p.202", ("đắc", ["Tý", "Ngọ", "Mão", "Dậu"])),
    "Thiên Hư": T("KL p.202", ("đắc", ["Tý", "Ngọ", "Mão", "Dậu"])),
    "Thiên Không": T("KL p.147", ("đắc", TU_SINH)),
    "Thiên Riêu": T("KL p.121", ("đắc", ["Mão", "Dậu"]), note="'Nếu đắc địa ở Mão Dậu…'; other branches not named."),
}

EXPERIMENTAL = [
    {"star": "Linh Tinh", "school": "thuc_hanh", "locator": "TH p.64", "cells": {"Thìn": "miếu?", "Mùi": "miếu?", "Tỵ": "miếu|hãm"},
     "reason": "Thìn, Mùi follow a dash with no label; Tỵ is printed under both Miếu and Hãm."},
    {"star": "Kình Dương", "school": "toan_thu", "locator": "TT p.50", "cells": {"Tý": "vượng|hãm"},
     "reason": "Two phú lines on the same page disagree."},
    {"star": "Văn Xương", "school": "toan_thu", "locator": "TT p.41", "cells": {"Thìn": "vượng", "Tỵ": "vượng", "Ngọ": "lợi", "Mão": "hiềm", "Dậu": "hiềm"},
     "reason": "The song (bài ca) disagrees with the phú list used in production; TT p.42 says neither can be settled."},
    {"star": "Văn Khúc", "school": "toan_thu", "locator": "TT p.43", "cells": {"Hợi": "lạc", "Tý": "lạc"},
     "reason": "Song line 'Lạc cư Hợi, Tí cung' against the phú (Tý miếu, Hợi vượng)."},
    {"star": "Hỏa Tinh", "school": "toan_thu", "locator": "TT p.52", "cells": {"Tý": "miếu", "Mão": "miếu"},
     "reason": "'Tiền nhân ta cho Hỏa Tinh hai nơi miếu địa nữa là cung Tí và Mão' — reported Vietnamese variant."},
    {"star": "Thiên Khốc", "school": "toan_thu", "locator": "TT p.57", "cells": {"Tý": "miếu", "Ngọ": "miếu", "Mão": "miếu", "Dậu": "miếu", "Thân": "miếu"},
     "reason": "The book gives two schools: Vietnamese phú (Tý Ngọ) vs La Hồng Tiên / Hi Di (Mão Dậu Thân). Also applies to Thiên Hư."},
    {"star": "Bạch Hổ", "school": "toan_thu", "locator": "TT p.60", "cells": {"Dậu": "miếu"},
     "reason": "Quoted from 'Tử Vi Việt'; TH p.65 gives Dậu as đắc."},
    {"star": "Hồng Loan", "school": "toan_thu", "locator": "TT p.62", "cells": {"Dần": "miếu", "Mão": "miếu", "Tý": "miếu", "Hợi": "miếu"},
     "reason": "Commentary attributed to Vietnamese predecessors, no hãm branches given; no other book tabulates Hồng Loan."},
    {"star": "Long Trì", "school": "toan_thu", "locator": "TT p.60", "cells": {"Sửu": "vượng", "Mùi": "vượng"},
     "reason": "Phú nôm verse ('Cung Mùi cung Sửu đóng vào vượng thay'); TH p.54 says đắc. Also Phượng Các."},
    {"star": "Ân Quang", "school": "thuc_hanh", "locator": "TH p.55", "cells": {"Sửu": "đắc cách", "Mùi": "đắc cách"},
     "reason": "A prose sentence about a formation ('Quang Quí đóng Sửu, Mùi là đắc cách'), not a brightness header. Also Thiên Quý."},
    {"star": "Đà La", "school": "khao_luan", "locator": "KL p.143", "cells": {"Tý": "đắc", "Ngọ": "đắc", "Mão": "đắc", "Dậu": "đắc"},
     "reason": "'có sách nói … Đà la đắc địa ở Tứ chính' — reported and argued against by KL."},
    {"star": "Hóa Lộc", "school": "thuc_hanh", "locator": "TH p.52", "cells": {b: "đắc" for b in ["Tý", "Ngọ", "Mão", "Dậu"]},
     "reason": "Tứ Hóa are transformations, not Thiên Bàn stars; kept out of the badge layer. TT p.48 says its source gives no miếu/hãm for Lộc/Quyền/Khoa."},
    {"star": "Hóa Quyền", "school": "thuc_hanh", "locator": "TH p.52", "cells": {b: "đắc" for b in TU_MO},
     "reason": "TT p.48 quotes a phú nôm with Dần Mão Tỵ Hợi as Quyền's 'miếu đường' instead."},
    {"star": "Hóa Khoa", "school": "thuc_hanh", "locator": "TH p.52", "cells": {b: "đắc" for b in ["Dần", "Thân", "Tỵ", "Hợi"]},
     "reason": "Tứ Hóa: see Hóa Lộc."},
    {"star": "Hóa Kỵ", "school": "thuc_hanh", "locator": "TH pp.52-53", "cells": {"Hợi": "miếu", "Tý": "miếu", "Dần": "miếu", "Mão": "miếu", "Thìn": "vượng|đắc", "Tuất": "vượng|đắc", "Sửu": "vượng|đắc", "Mùi": "vượng|đắc"},
     "reason": "The p.52 header says vượng for the tứ mộ, the p.53 prose says đắc. TT pp.49-50: miếu Tý Hợi, vượng Dần Mão Dậu Thân."},
]

# Phụ tinh the engine places for which no book gives a per-branch classification (explicitly unknown, never guessed).
NO_TABLE = {
    "Thiên Khôi": "TT p.46: 'Hai sao Thiên Khôi và Thiên Việt không thấy nói tới hãm địa.' TH/KL give none.",
    "Thiên Việt": "As Thiên Khôi.",
    "Đào Hoa": "TH p.55 / KL p.197 describe it without branches.",
    "Hồng Loan": "Only the experimental TT p.62 commentary.",
    "Thiên Hỷ": "No branch classification in TH p.55 / TT p.62.",
    "Ân Quang": "TH p.55 prose only (experimental).", "Thiên Quý": "TH p.55 prose only (experimental).",
    "Tam Thai": "TH p.55 / TT p.61: no branches.", "Bát Tọa": "TH p.55 / TT p.61: no branches.",
    "Hoa Cái": "TH p.56 / TT p.62: 'miếu vượng' without branches.",
    "Thiên Quan": "TH p.56: none.", "Thiên Phúc": "TH p.56: none.", "Thiên Y": "TH p.69: none.",
    "Cô Thần": "TH p.69: none.", "Quả Tú": "TH p.69: none.", "Đẩu Quân": "TH p.69 / TT p.62: none.",
    "Phá Toái": "TH p.69: none; KL p.202 only says where it can stand.", "Lưu Hà": "TH p.69 / KL p.201: none.",
    "Thiên Thương": "TT p.54: 'không cần hỏi đắc địa hay không'.", "Thiên Sứ": "As Thiên Thương.",
    "Thiên Đức": "None.", "Nguyệt Đức": "None.", "Thiên Giải": "None.", "Địa Giải": "None.", "Thiên La": "None.", "Địa Võng": "None.",
    "Thiên Tài": "None.", "Thiên Thọ": "None.",
    "Vòng Lộc Tồn / Thái Tuế / Trường Sinh (other than Đại Hao, Tiểu Hao, Tang Môn, Bạch Hổ)": "TH pp.58-61: properties only.",
}


def build() -> dict:
    return {
        "version": "aux-dignity-1",
        "levels": ["miếu", "vượng", "đắc", "lợi", "bình", "hãm"],
        "term_to_level": LEVEL,
        "sources": {"thuc_hanh": "SRC_THUC_HANH", "toan_thu": "SRC_TOAN_THU", "khao_luan": "SRC_KHAO_LUAN"},
        "fallback": {"thuc_hanh": ["thuc_hanh", "toan_thu", "khao_luan"], "toan_thu": ["toan_thu", "thuc_hanh", "khao_luan"]},
        "note": "A star the chosen book does not tabulate falls back, star by star, to the next book; within a table an unnamed "
                "branch is unknown. Experimental cells are never returned by the lookup.",
        "tables": {"thuc_hanh": TH, "toan_thu": TT, "khao_luan": KL},
        "experimental": EXPERIMENTAL,
        "no_table": NO_TABLE,
    }


if __name__ == "__main__":
    OUT.write_text(json.dumps(build(), ensure_ascii=False, indent=1) + "\n", "utf-8")
    print("wrote", OUT, sum(len(t) for t in build()["tables"].values()), "star tables")
