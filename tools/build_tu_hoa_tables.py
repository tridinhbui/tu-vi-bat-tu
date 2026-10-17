"""engine/data/experimental/tu_hoa_tables.json — the Tứ Hóa tables of each source side by side. NOT wired into production: the default table stays the one in tvbt/tuvi.py
(Khảo Luận). The file exists so that the disagreement (Nhâm-Khoa, and Canh for an external text) is data, with page/quote evidence, and so that a future opt-in switch has a
documented table to read."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine/tests"))
import oracle_tuvi_independent as O  # noqa: E402

STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
SOURCES = {
    "KL": {"label": "Tử Vi Khảo Luận (Hoàng Thường – Hàm Chương)", "pages": "tr.36 (bảng), tr.196-197 (diễn giải từng sao)", "default_in_production": True,
           "evidence": [{"page": 36, "quote": "Nhâm Lương Vi Phụ Vũ", "how": "van_ban"},
                        {"page": 197, "quote": "Tả phụ, phải khéo léo, chăm chỉ mới có danh", "how": "anh_doc_ro (mục 'Tuổi Nhâm' liệt kê Lương, Vi, Phụ, Vũ và bình từng sao)"},
                        {"page": 36, "quote": "Canh Nhật Vũ Đồng Âm", "how": "van_ban (Khoa Thiên Đồng, Kỵ Thái Âm)"}],
           "note": "bảng tr.36 in nhầm Tân-Lộc là Thiên Cơ; phần diễn giải tr.196 ghi Cự Môn (dùng Cự Môn)"},
    "TH": {"label": "Tử Vi Thực Hành (Dịch Lý Huyền Cơ)", "pages": "tr.20 (câu thơ), tr.21 (văn xuôi)", "default_in_production": False,
           "evidence": [{"page": 20, "quote": "Nhâm : Lương, Tử, Phủ, Vũ tú thị", "how": "anh_doc_ro (chữ 'Phủ' rõ trong ảnh trang)"},
                        {"page": 21, "quote": "Khoa an với Thiên Phủ, Ky an với Vũ Khúc", "how": "anh_doc_ro (cùng trang có lỗi in khác: 'Khao', 'Vự Môn')"}],
           "note": "TH in Thiên Phủ ở CẢ câu thơ lẫn văn xuôi: không thể coi là lỗi chính tả một chỗ"},
    "TT_WS": {"label": "紫微斗數全書 bản số hóa (zh.wikisource.org/wiki/紫微斗數全書/卷二) — NGUỒN NGOÀI, không thuộc ba sách của dự án", "pages": "bài 'Lập Tứ Hóa: 安祿權科忌四星變化訣'", "default_in_production": False,
              "evidence": [{"page": None, "quote": "庚日武陰同為首 / 壬梁紫府武宿是", "how": "văn bản số hóa, truy cập 2026-10-17; một ấn bản, chưa đối chiếu bản gốc"}],
              "note": "khác KL ở Canh (Khoa Thái Âm, Kỵ Thiên Đồng) và Nhâm (Khoa Thiên Phủ). zh.wikipedia/紫微斗數 cũng ghi hai biến thể ở đúng hai hàng này, nên đây là khác biệt giữa các văn bản truyền thống, không phải lỗi một cuốn"},
}
out = {"version": 1, "note": "Bảng Tứ Hóa theo nguồn. Mặc định sản xuất vẫn là KL; không có chuyển đổi nào được nối vào API. Đề xuất cơ chế chọn: tham số `tu_hoa_table` ('KL' mặc định | 'TH' | 'TT_WS'), "
                          "trả về trong kết quả cùng nhãn nguồn, không bao giờ đổi âm thầm.", "stems": STEMS, "sources": SOURCES, "tables": {}, "differs_from_KL": {}}
for k, t in O.TU_HOA_TABLES.items():
    out["tables"][k] = {STEMS[i]: dict(zip(("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"), t[i])) for i in range(10)}
for k in ("TH", "TT_WS"):
    out["differs_from_KL"][k] = {STEMS[i]: {tag: [a, b] for tag, a, b in zip(("Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"), O.TU_HOA_TABLES["KL"][i], O.TU_HOA_TABLES[k][i]) if a != b}
                                 for i in range(10) if O.TU_HOA_TABLES["KL"][i] != O.TU_HOA_TABLES[k][i]}
(ROOT / "engine/data/experimental/tu_hoa_tables.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps(out["differs_from_KL"], ensure_ascii=False))
