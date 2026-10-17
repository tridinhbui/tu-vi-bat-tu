"""Generates docs/PHASE5_HIEU_CHINH_NGUON.md from the audit, the variants and the pinned scans. Pure formatting: no judgement lives here."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "engine/tests"))
import build_formation_audit as au  # noqa: E402
from test_formation_audit import CONTROL  # noqa: E402
from test_formation_variants import BEFORE_AFTER  # noqa: E402

AUDIT = json.load(open(ROOT / "engine/data/experimental/formation_audit.json", encoding="utf-8"))
VAR = json.load(open(ROOT / "engine/data/experimental/formations_school_variants.json", encoding="utf-8"))
REACH = json.load(open(ROOT / "engine/tests/fixtures/formation_variants_reach.json", encoding="utf-8"))
META = VAR["meta"]
S = AUDIT["summary"]
NAMES = {"hang_vo": "Hạng Võ", "han_cao_to": "Hán Cao Tổ", "khong_minh": "Khổng Minh", "nu_quy_mao": "Nữ Quý Mão", "mau_ty_pha_san": "Mậu Tý phá sản"}
VERDICT = {"dong_y": "đồng ý", "khong_khop": "không khớp", "khong_phan_xet": "sách không xét"}


def variants_of(base):
    return {k: m for k, m in META.items() if m["base"] == base}


def fate(r):
    vs = variants_of(r["formation"])
    kept = [k.split("@")[1] for k, m in vs.items() if r["id"] in m["kept"].get(r["role"], [])]
    if r["role"] == "core":
        repl = [k.split("@")[1] for k, m in vs.items() if m["core_replaced"]]
        return ("lõi thay bằng định nghĩa nguồn ở: " + ", ".join(repl) + "; ") if repl else "lõi giữ nguyên ở mọi biến thể"
    if r["role"] == "rescuers":
        return "không vào biến thể nào (không nguồn nói sao nào cứu cách nào); chỉ còn ở giả thuyết gốc"
    if kept:
        return "giữ ở: " + ", ".join(kept)
    return "không vào biến thể nào; chỉ còn ở giả thuyết gốc"


def main():
    rows = AUDIT["rows"]
    nvar = len(META)
    rules = [x for m in META.values() for x in m["rules"].values()]
    L = ["# Phase 5 — Hiệu chỉnh định nghĩa cách cục theo nguồn (bản nháp)", "",
         "Sinh bởi `tools/build_formation_report5.py` từ `formation_audit.json`, `formations_school_variants.json` và `formation_variants_reach.json`. "
         "**Định nghĩa gốc (`formations_experimental.json`, của phiên khác) không bị sửa.** Các hiệu chỉnh nằm ở lớp biến thể riêng theo từng sách; "
         "các định nghĩa mâu thuẫn được giữ thành biến thể khác nhau, không gộp, không chọn bên đúng hơn. Mọi thứ vẫn `draft`, chỉ hiện ở `?thu-nghiem`.", "",
         "## 1. Chốt audit", "",
         f"- Tổng điều kiện: **{S['total']}**; khớp nguồn **{S['by_status'].get('khop', 0)}** (trong đó {S['khop_machine_checked']} có câu trích được máy so với văn bản trang, "
         "còn lại dựa vào trang đọc từ ảnh TH tr.72/74); bị loại khỏi tập có nguồn **" + str(S['excluded_from_sourced']) + f"**; đề xuất sửa **{S['by_action'].get('de_xuat_sua', 0)}**.",
         "- Các trích dẫn (94 câu `van_ban`, 5 câu `anh`) được lưu kèm kết quả kiểm trong JSON đã commit, nên việc kiểm lại không phụ thuộc test có chạy hay bị bỏ qua khi thiếu PDF; "
         "test đọc PDF tự bỏ qua khi thiếu sách và KHÔNG được tính là bằng chứng.", "",
         "## 2. Lớp biến thể theo nguồn", "",
         f"{nvar} biến thể cho 10 cách (mỗi biến thể = một sách, một cách đọc). Quy tắc xây dựng: chỉ giữ điều kiện có nguồn ĐÚNG vai trò trong sách đó; thay phạm vi khi câu sách nêu rõ "
         "(đồng cung / đối cung / tam phương / hội chiếu); không mở rộng chữ \"gặp\" khi câu không xác định phạm vi; **không biến thể nào có sao cứu giải**.", "",
         "| Biến thể | Sách · trang | Điều kiện (giữ từ gốc hoặc thêm theo sách) | Lõi | Giả định cách đọc |", "|---|---|---|---|---|"]
    for vid, m in META.items():
        kept = [f"{role[:4]}:{i}" for role, ids in m["kept"].items() for i in ids]
        pages = ", ".join(f"{c['book_code']} tr.{c['page']}" for c in m["cites"])
        L.append(f"| `{vid.split('CACH_X_')[1]}` | {pages} | {', '.join(kept) or '—'} | "
                 f"{'lõi theo sách' if m['core_replaced'] else 'như gốc'} | {'; '.join(m['readings']) or '—'} |")
    L += ["", f"Mức xác minh theo TỪNG QUY TẮC (không nâng cả cách): **{rules.count('doi_chieu_truc_tiep')}** quy tắc `doi_chieu_truc_tiep` "
          f"(câu trích đã được máy so với trang, không cần giả định), **{rules.count('co_nguon_con_gia_dinh')}** quy tắc `co_nguon_con_gia_dinh` "
          f"(có nguồn nhưng còn giả định về phạm vi/ngưỡng), **{rules.count('chua_du_nguon')}** quy tắc `chua_du_nguon` (trang đọc từ ảnh hoặc quy ước thiết kế). Đây là đối chiếu của phiên AI, chưa có thẩm định của chuyên gia Tử Vi nên không mức nào là `verified` ở cấp cách cục.", ""]
    L += ["## 3. Bảng 93 điều kiện sau hiệu chỉnh", "", "| Cách | Vai trò | Điều kiện | Mức khớp (audit) | Số phận sau hiệu chỉnh |", "|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['name_vi']} | {au.ROLE_VI[r['role']]} | `{r['id']}` | {au.STATUS_VI[r['status']]} | {fate(r)} |")
    L += ["", "## 4. Ma trận bất đồng trường phái", "", "Mỗi dòng là một điều kiện có bất đồng; cột cuối là các biến thể giữ riêng từng bên.", "",
          "| Cách | Điều kiện | Bất đồng | Biến thể giữ riêng |", "|---|---|---|---|"]
    for r in rows:
        if r["school_conflict"]:
            vs = ", ".join(k.split("@")[1] for k in variants_of(r["formation"])) or "—"
            L.append(f"| {r['name_vi']} | `{r['id']}` | {r['school_conflict']} | {vs} |")
    L += ["", "## 5. Tám lá số đối chứng (KL tr.237–246), trước và sau", "",
          "Biến thể được viết từ trang sách, không chỉnh theo lá số. Cột sau là kết quả của biến thể; nơi hai sách cho hai kết luận thì ghi cả hai.", "",
          "| Lá số | Cách | Gốc | Sách nói | Kết quả gốc | Biến thể → trạng thái |", "|---|---|---|---|---|---|"]
    for (n, fid), (state, verdict, note) in CONTROL.items():
        after = ", ".join(f"{k.split('@')[1]} → {s}" for k, s in BEFORE_AFTER.get(n, {}).items() if k.startswith(fid + "@")) or "—"
        L.append(f"| {NAMES[n]} | {fid.replace('CACH_X_', '')} | {state} | {note} | {VERDICT[verdict]} | {after} |")
    L += ["", "Nguyên nhân thay đổi: phạm vi. Cơ Nguyệt Đồng Lương theo TT tr.24 tính Kiếp/Không/Kỵ trên cả tam phương → Hạng Võ và Mậu Tý đổi sang `bi_pha` (khớp sách); "
          "Tam kỳ gia hội theo KL tr.66 tính Kỵ/Kình ở đối cung → Hạng Võ `bi_pha` (khớp). Bản KL tr.221 của Cơ Nguyệt Đồng Lương không nêu yếu tố phá nên vẫn `thành`: "
          "bất đồng giữa các sách được giữ, không ép khớp. Khôi Việt giáp Mệnh của Nữ Quý Mão chuyển `bi_pha` do KL tr.62 (sát tinh hội chiếu), sách không đánh giá lá số này nên không phán đúng/sai.", ""]
    L += ["## 6. Phạm vi kết luận hình học", "",
          "- **Giả định của mô hình:** vị trí Tử Vi/Thiên Phủ (đối xứng Dần–Thân), bảng Tứ Hóa theo can năm (Thực Hành tr.21, Khảo Luận tr.196–197), công thức Tả/Hữu theo tháng và Xương/Khúc theo giờ.",
          "- **Bất khả thi trong mô hình:** Tử Phủ đồng cung × *phá được cứu*, được test tái lập trong `test_formation_geometry.py`. Đây KHÔNG phải kết luận cổ thư: một trường phái an sao khác hoặc bảng Tứ Hóa khác "
          "(vd. Nhâm-Khoa là Tả Phụ hay Phủ, đã ghi trong tuvi.py) có thể cho kết quả khác. Trong các biến thể theo nguồn *phá được cứu* không tồn tại vì không sách nào cho phép.",
          "- **Bốn điều kiện không thể kích hoạt** giữ nguyên, không sửa để tăng độ phủ: Thiên Tướng hãm (giới hạn vị trí sao), Thái Dương hãm ở Ngọ và Cự Môn hãm ở Tý/Ngọ (bảng miếu vượng), Tam Hóa hội cứu của Tử Phủ đồng cung (hình học).", "",
          "## 7. Khả năng kích hoạt của các biến thể (quét " + f"{REACH['charts']:,} lá số)", "", "| Biến thể | Các trạng thái xuất hiện |", "|---|---|"]
    for k, v in REACH["variants"].items():
        L.append(f"| `{k.split('CACH_X_')[1]}` | {', '.join(f'{s} {q}' for s, q in v.items() if s != 'khong_hien') or '**không bao giờ hiện trong mẫu quét**'} |")
    L += ["", "## 8. Điều kiện còn thiếu nguồn", "", "| Cách | Vai trò | Điều kiện | Ghi chú |", "|---|---|---|---|"]
    for r in rows:
        if r["status"] in ("khong_co_nguon",) or (r["status"] == "lien_quan" and r["action"] == "giu_gia_thuyet"):
            L.append(f"| {r['name_vi']} | {au.ROLE_VI[r['role']]} | `{r['id']}` | {r['reason']} |")
    (ROOT / "docs/PHASE5_HIEU_CHINH_NGUON.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
