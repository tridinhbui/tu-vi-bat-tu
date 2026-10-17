"""Reader-checkable sheet of the 120 điều hậu cells (Thiệu Vĩ Hoa tr.389-396, 397).
Writes docs/BAZI_DEEP_TVH_CELLS_CHECK.md and docs/bazi_deep_tvh_cells_check.csv: one row per (day stem, month) with the printed table cell, the printed note list, the page of
each, the 9 book-internal conflicts, and what independent checking each value has had. The last column is for a human reader to tick against the page image; nothing is pre-ticked."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
G = ROOT / "engine/tests/golden"
BLIND = json.loads((G / "tvh_dieuhau_blind.json").read_text("utf-8"))
ENG = json.loads((ROOT / "engine/data/bazi_deep/tvh_dieuhau.json").read_text("utf-8"))
MONTHS = ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]
STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
MONTH_NO = {m: i + 1 for i, m in enumerate(MONTHS)}       # 'tháng giêng' = Dần = 1 in the note lists
NOTE_ADJ = {("Thìn", "Ất"): "lượt chép mù và engine cũ khác nhau; đối chiếu ảnh p.391: engine cũ sai, đã sửa",
            ("Mùi", "Tân"): "lượt chép mù và engine khác nhau; đối chiếu ảnh p.395: lượt mù đảo thứ tự, engine đúng",
            ("Sửu", "Quý"): "lượt chép mù không được đưa trang 397; chỉ một lượt (engine) + đối chiếu ảnh p.397"}


def table_page(m):
    return 389 if MONTHS.index(m) <= 4 else 390


def note_page(s, m):
    n = MONTH_NO[m]
    return {"Giáp": 391, "Ất": 391 if n <= 6 else 392, "Bính": 392, "Đinh": 392 if n <= 3 else 393, "Mậu": 393, "Kỷ": 394, "Canh": 394 if n <= 6 else 395,
            "Tân": 395, "Nhâm": 395 if n <= 2 else 396, "Quý": 396 if n <= 11 else 397}[s]


def rows():
    out = []
    for m in MONTHS:
        for s in STEMS:
            t = ENG["cells"][m][s]
            n = ENG["notes_order"][m][s]
            conflict = set(t) != set(n)
            out.append({"month": m, "month_no": MONTH_NO[m], "stem": s, "table": t, "table_page": table_page(m), "notes": n, "notes_page": note_page(s, m), "conflict": conflict,
                        "note_only": [x for x in n if x not in t], "table_only": [x for x in t if x not in n],
                        "table_check": "2 lượt chép độc lập khớp" if BLIND["table"][m][s] == t else "KHÔNG KHỚP",
                        "notes_check": NOTE_ADJ.get((m, s), "2 lượt chép độc lập khớp" if BLIND["notes"][m][s] == n else "KHÔNG KHỚP")})
    return out


def main():
    R = rows()
    nc = sum(r["conflict"] for r in R)
    L = ["# Phiếu kiểm 120 ô điều hậu (Thiệu Vĩ Hoa tr.389–397)\n",
         "Phiếu này để người đọc đối chiếu với ảnh trang sách. Cột *Bảng* là ô in trong bảng dụng thần dự bị (thứ tự in, không mang nghĩa ưu tiên); cột *Chú thích* là danh sách ở mục "
         "'Chú thích bảng dụng thần điều hậu' (can đầu là chủ). *Tháng* theo cách sách gọi: tháng giêng = Dần … tháng mười hai = Sửu.\n",
         f"- **{nc} ô mâu thuẫn nội bộ sách** (đánh dấu ⚠): bảng và chú thích nêu hai tập can khác nhau.",
         f"- Chưa có ô nào được **người** kiểm độc lập. Mức hiện có: hai lượt chép của mô hình (một lượt mù) khớp nhau ở {sum(r['table_check'].startswith('2') for r in R)}/120 ô bảng "
         f"và {sum(r['notes_check'].startswith('2') for r in R)}/120 ô chú thích; 3 ô chú thích còn lại đã được đối chiếu ảnh trang bởi cùng mô hình (xem cột *Kiểm độc lập*).",
         "- Cột cuối để trống cho người kiểm: ☐ = chưa kiểm.\n"]
    cur = None
    for r in R:
        if r["month"] != cur:
            cur = r["month"]
            L += [f"\n## Tháng {cur} (tháng {r['month_no']})\n", "| Can ngày | Bảng (tr.) | Chú thích (tr.) | Mâu thuẫn | Kiểm độc lập (bảng / chú thích) | Người kiểm |", "|---|---|---|---|---|---|"]
        flag = "⚠ " + (f"chú thích có thêm {', '.join(r['note_only'])}" if r["note_only"] else "") + (" · " if r["note_only"] and r["table_only"] else "") + (f"bảng có thêm {', '.join(r['table_only'])}" if r["table_only"] else "") if r["conflict"] else "—"
        L.append(f"| {r['stem']} | {' '.join(r['table'])} (tr.{r['table_page']}) | {' '.join(r['notes'])} (tr.{r['notes_page']}) | {flag} | {r['table_check']} / {r['notes_check']} | ☐ |")
    (ROOT / "docs/BAZI_DEEP_TVH_CELLS_CHECK.md").write_text("\n".join(L) + "\n", "utf-8")
    with (ROOT / "docs/bazi_deep_tvh_cells_check.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["thang", "thang_so", "can_ngay", "bang_in", "trang_bang", "chu_thich", "trang_chu_thich", "mau_thuan_noi_bo", "can_chi_co_trong_chu_thich", "can_chi_co_trong_bang", "kiem_doc_lap_bang", "kiem_doc_lap_chu_thich", "nguoi_kiem"])
        for r in R:
            w.writerow([r["month"], r["month_no"], r["stem"], " ".join(r["table"]), r["table_page"], " ".join(r["notes"]), r["notes_page"], "x" if r["conflict"] else "",
                        " ".join(r["note_only"]), " ".join(r["table_only"]), r["table_check"], r["notes_check"], ""])
    print("wrote sheet:", len(R), "cells,", nc, "conflicts")


if __name__ == "__main__":
    main()
