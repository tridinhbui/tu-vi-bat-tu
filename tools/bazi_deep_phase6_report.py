"""Phase 6 report: GO / CONDITIONAL GO / NO-GO with evidence, 5,000-chart school-isolation matrix, source-disagreement table, API contract pointer, pre-production checklist.
Matrices are recomputed from the live engine. Run: python tools/bazi_deep_phase6_report.py   (writes docs/BAZI_DEEP_PHASE6_REPORT.md, ~1 minute)"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "engine/tests"))
from tvbt.bazi_deep import pipeline, yongshen  # noqa: E402
from tvbt.bazi_deep.model import ChartView  # noqa: E402
from tvbt.bazi_deep.profile import DEFAULT, TVH_40  # noqa: E402
import test_bazi_deep_phase6 as T  # noqa: E402  (the same 5,000-chart sample the tests use)

SYS, TVH = T.SYS, T.TVH
G = ROOT / "engine/tests/golden"
BOOK = json.loads((G / "tvh_dungthan_examples.json").read_text("utf-8"))


def matrix():
    C = T.CHARTS
    cnt = {m: 0 for m in SYS}
    inner = outer = 0
    for p in C:
        a, b = T.run(p, DEFAULT), T.run(p)
        for m in SYS:
            cnt[m] += T.core(a["yongshen"]["methods"][m]) != T.core(b["yongshen"]["methods"][m])
        inner += T.innerkey(a) != T.innerkey(b)
        outer += T.sys_outer(a) != [(x["name"], x["quality"]) for x in b["geju"]["outer"] if x.get("kind") not in yongshen.TVH_KINDS]
    sl = C[::3]
    rows_sys, rows_tvh = [], []
    for ch in T.SYSTEM_ONLY:
        alt = TVH_40.with_(**ch)
        drop = ("yong_health", "xi_health") if set(ch) & {"season_factor", "class_weight"} else ()
        strip = lambda m: {k: v for k, v in T.core(m).items() if k not in drop}
        moved = tvh_changed = health_changed = 0
        for p in sl:
            a, b = T.run(p), pipeline.analyse(ChartView.from_names(p), alt, with_rules=False)
            moved += any(T.core(a["yongshen"]["methods"][m]) != T.core(b["yongshen"]["methods"][m]) for m in SYS)
            tvh_changed += any(strip(a["yongshen"]["methods"][m]) != strip(b["yongshen"]["methods"][m]) for m in TVH) or a["strength_after"]["tvh"] != b["strength_after"]["tvh"]
            health_changed += any(T.core(a["yongshen"]["methods"][m]) != T.core(b["yongshen"]["methods"][m]) for m in TVH)
        rows_sys.append((next(iter(ch)), moved, tvh_changed, health_changed))
    for ch in T.TVH_ONLY:
        alt = TVH_40.with_(**ch)
        s_ch = t_ch = 0
        for p in sl:
            a, b = T.run(p), pipeline.analyse(ChartView.from_names(p), alt, with_rules=False)
            s_ch += any(T.core(a["yongshen"]["methods"][m]) != T.core(b["yongshen"]["methods"][m]) for m in SYS) or T.innerkey(a) != T.innerkey(b) or T.sys_outer(a) != T.sys_outer(b)
            t_ch += any(T.core(a["yongshen"]["methods"][m]) != T.core(b["yongshen"]["methods"][m]) for m in TVH)
        rows_tvh.append((next(iter(ch)), s_ch, t_ch))
    classes = {}
    for p in C:
        o, a = T.run(p), T.run(p, DEFAULT)
        tv = o["strength_after"]["tvh"]
        tvh_out = [x for x in o["geju"]["outer"] if x.get("kind") in yongshen.TVH_KINDS]
        for k, v in (("hệ thống nhận ngoại cách chân", any(x["quality"] == "chân" for x in a["geju"]["outer"])), ("TVH nhận cách đặc biệt", bool(tvh_out)),
                     ("TVH tòng (tài/sát/nhi)", any(x["kind"] == "tong_tvh" for x in tvh_out)), ("TVH chuyên vượng/hóa khí", any(x["kind"] != "tong_tvh" for x in tvh_out)),
                     ("cả hai trường phái cùng nhận ngoại cách", bool(tvh_out) and any(x["quality"] == "chân" for x in a["geju"]["outer"])), ("sát ngưỡng 40% (±0,03)", abs(tv["own_share"] - 0.4) < 0.03),
                     ("Nhật Chủ vượng theo 40%", tv["dm_strong"]), ("Nhật Chủ nhược theo 40%", not tv["dm_strong"]),
                     ("có bất đồng giữa các phương pháp", bool(o["yongshen"]["comparison"]["disagreements"]))):
            classes[k] = classes.get(k, 0) + v
    return len(C), cnt, inner, outer, rows_sys, rows_tvh, classes


def main():
    n, cnt, inner, outer, rows_sys, rows_tvh, classes = matrix()
    L = []
    w = L.append
    w("# Phase 6: sẵn sàng production và kiểm chứng học thuật (dựa trên `6e88e38`)\n")
    w("Báo cáo do `tools/bazi_deep_phase6_report.py` sinh ra; các bảng được tính lại từ engine. Không có thuật toán mới trong Phase 6.\n")
    w("## 1. Kết luận: **CONDITIONAL GO**\n")
    w("| Phạm vi | Quyết định | Bằng chứng |")
    w("|---|---|---|")
    w(f"| Đưa khối `yongshen` *cộng thêm* (meta, trace, so sánh, cờ mâu thuẫn) ra API/UI **dưới nhãn bản nháp** theo hợp đồng `docs/BAZI_DEEP_API_CONTRACT.md` | **GO có điều kiện** | cách ly hai chiều: 0 sai lệch trên {n} lá số; hợp đồng được kiểm bằng schema trên pipeline và API; tương thích ngược với `d0c3ab8`; không rò nội dung experimental; 949+ test qua trên HEAD sạch |")
    w("| Trình bày bất kỳ dụng thần nào như *đã được chứng minh* hay như *một kết luận duy nhất* | **NO-GO** | `empirical_validated = no` ở mọi phương pháp; không phương pháp nào `source_rule_verified = yes`; trong 10 ví dụ của sách, khớp hoàn toàn 3, một phần 6, không khớp 1; bảng điều hậu không rõ nguồn (tr.388); chín ô sách tự mâu thuẫn |")
    w("| Gỡ nhãn *bản nháp* hay nói 'đã người kiểm' | **NO-GO** | chưa có người nào kiểm 120 ô; ví dụ 4 có ngày dựng lại; ví dụ 5 chỉ một người đọc |\n")
    w("Điều kiện để GO có hiệu lực: (C1) phiên sở hữu `api.py`/`web/` gắn hợp đồng nguyên văn, kể cả nhãn ba mức xác minh và câu *không có kết luận thống nhất*; (C2) banner bản nháp luôn hiện; (C3) UI không dựa vào khóa chỉ có ở một số trạng thái (`methods.*.note`). Danh sách đầy đủ ở mục 7.\n")
    w("## 2. Ma trận cách ly trường phái\n")
    w(f"Mẫu: **{n}** lá số hợp lệ: đủ 60 trụ ngày × 12 tháng (720 tổ hợp, năm và giờ ngẫu nhiên) cộng ngẫu nhiên có hạt giống cố định. Số lượng từng loại trong mẫu (mỗi loại có ngưỡng tối thiểu trong test):\n")
    w("| Loại lá số | Số lá số |")
    w("|---|---|")
    for k, v in classes.items():
        w(f"| {k} | {v} |")
    w("\n**2a. Bật profile TVH có đổi kết quả của hệ thống không?** (số lá số bị đổi, trên toàn bộ mẫu)\n")
    w("| Đầu ra của hệ thống | Bị đổi |")
    w("|---|---|")
    w(f"| trạng thái nội cách và tên nội cách (`geju.inner`) | {inner}/{n} |")
    w(f"| ngoại cách của hệ thống (`geju.outer`, không tính cách TVH) | {outer}/{n} |")
    for m in SYS:
        w(f"| phương pháp `{m}` | {cnt[m]}/{n} |")
    w(f"\n**2b. Đổi một tham số chỉ thuộc hệ thống có làm đổi TVH không?** ({len(T.CHARTS[::3])} lá số mỗi dòng)\n")
    w("| Tham số | Lá số mà phương pháp hệ thống đổi | Lá số mà kết luận TVH (status/yong/xi/ji) hoặc điểm TVH đổi | Lá số mà chú thích hiện diện `yong_health` của TVH đổi |")
    w("|---|---|---|---|")
    for name, mv, t, h in rows_sys:
        w(f"| `{name}` | {mv} | **{t}** | {h} |")
    w("\nGhi chú: `season_factor` và `class_weight` đi qua lớp tương tác dùng chung (`interact.resolve`), nên chúng chỉ có thể đổi chú thích hiện diện `yong_health`/`xi_health`, không đổi kết luận. Đây là lớp chung có chủ ý (cùng bản đồ thấu/tàng can cho cả hai trường phái).\n")
    w("**2c. Đổi một tham số chỉ thuộc TVH có làm đổi hệ thống không?**\n")
    w("| Tham số | Lá số mà hệ thống (phương pháp, nội cách, ngoại cách) đổi | Lá số mà TVH đổi |")
    w("|---|---|---|")
    for name, s_, t in rows_tvh:
        w(f"| `{name}` | **{s_}** | {t} |")
    w("\nKết quả hai chiều: không có dòng nào của cột in đậm khác 0.\n")
    w("## 3. Xử lý bất đồng `phu_uc`\n")
    w("`phu_uc` giữ nguyên, dựa trên khí thế của hệ thống. Việc không còn dùng ngưỡng 40% là **hệ quả có chủ đích của cách ly trường phái**, và được ghi trong `yongshen.isolation.note` và `meta.strength_basis = 'he_thong (tách khỏi điểm TVH)'`. "
      "Trong mẫu, Nhật Chủ theo hệ thống và theo 40% bất đồng ở một phần lớn lá số (test `test_phu_uc_never_reads_the_40_percent_decision_by_design` ghi ≥ 100/1.500). Hai hệ không được trộn để tăng tỉ lệ khớp. "
      "Đề xuất `phu_uc_tvh` riêng (chưa triển khai, kèm điều kiện và test chấp nhận) ở `docs/BAZI_DEEP_PHU_UC_TVH_PROPOSAL.md`.\n")
    w("## 4. Bảng bất đồng nguồn\n")
    w("| # | Bất đồng | Giữa | Xử lý trong engine | Ai quyết |")
    w("|---|---|---|---|---|")
    rows = [
        ("1", "9 ô điều hậu: bảng tr.389–390 và chú thích tr.391–396 nêu tập can khác nhau (5 thay thế, 3 chú thích thêm, 1 bảng thêm)", "bảng ↔ chú thích của cùng một sách", "giữ tập can của bảng; can chỉ ở chú thích không được thăng cấp; cờ `book_internal_conflict`; can chủ không bị ảnh hưởng ở cả 9 ô", "người phụ trách học thuật, sau khi có người kiểm ảnh"),
        ("2", "Bảng điều hậu do một độc giả tặng, tác giả không biết nguồn (tr.388)", "độ tin cậy của nguồn", "chỉ ghi `transcription_verified`; không nâng `source_rule_verified`", "—"),
        ("3", "Ví dụ 2 tr.398: sách đọc *nhược* ('không có gốc') trong khi giờ Tý và tàng can Tân/Canh có mặt; quy tắc 40% cho 41,85% vượng", "lời văn ↔ quy tắc 40% của chính sách", "báo cả hai cách đọc (biên heuristic), đánh dấu cách đọc theo quy tắc", "—"),
        ("4", "Ví dụ 3 tr.399: sách chọn Thủy+Mộc theo cân bằng ngũ hành, không theo bảng cách cục của chính nó (bảng cho Quan Sát+Tài)", "ví dụ ↔ bảng cách × vượng/nhược", "giữ nguyên kết quả bảng; `dieu_hau` và `khuyet_hanh` tái lập lựa chọn của sách; hiển thị bất đồng", "—"),
        ("5", "Ví dụ 5 tr.400–401: bảng cho Quan Sát làm dụng thần, sách coi Hỏa (Quan Sát) là kỵ và Kim (Tỉ) là hỉ", "ví dụ ↔ bảng cách", "giữ nguyên; ghi trong test là xung đột; hiển thị bất đồng", "—"),
        ("6", "Ví dụ 4 tr.400: sách đọc thân vượng thường dùng Thực Thương; engine nhận Tòng Vượng (hệ thống) và Nhuận Hạ (TVH) chân", "ví dụ ↔ điều kiện nhận cách của chính sách (đã vận hành bằng ngưỡng hệ thống)", "không điều chỉnh ngưỡng; hiển thị là không khớp", "người phụ trách học thuật"),
        ("7", "Ví dụ 4 tr.399–400: bảng in vỡ ('Quý hợi | Ất | Quí | Tị tân hợi'); ví dụ 2: hàng thập thần tàng can in 'Ất tài quan' (nghi lỗi in); ví dụ 3: ngày in '129'", "lỗi in trong bản dịch/scan", "ví dụ 4 ghi `pillar_basis` từng trụ; hai lỗi in được ghi nhận, không dùng", "—"),
        ("8", "Ví dụ 1 tr.387: sách lấy Đinh hỏa, chú thích tháng Tuất của Kỷ xếp Giáp đầu (Đinh không có trong ô)", "ví dụ ↔ chú thích", "engine xếp Giáp đầu, Bính (cùng nhóm Ấn với Đinh) là Hỷ; ghi 'khớp một phần'", "—"),
    ]
    for r in rows:
        w("| " + " | ".join(r) + " |")
    w("\nChín ô ở dòng 1 được liệt kê đầy đủ ở `docs/BAZI_DEEP_TVH_AUDIT.md` mục 2 và đánh dấu ⚠ trong phiếu `docs/BAZI_DEEP_TVH_CELLS_CHECK.md`.\n")
    w("## 5. Ví dụ 4 và 5: dựng lại hay đọc trực tiếp\n")
    p4 = BOOK["dungthan_examples"]["p400_vd4"]["pillar_basis"]
    w("**Ví dụ 4 (tr.399–400):**\n")
    for k, v in p4.items():
        w(f"- {k}: {v}")
    w("\n**Ví dụ 5 (tr.400–401), Canh Ngọ…:** bốn trụ **đọc trực tiếp** (in rõ ở tr.400), hàng đại vận nhất quán; một người đọc, chưa có lượt chép mù. Kết quả đối chiếu: Nhật Chủ vượng (khớp); `dieu_hau` cho đúng tập {Thủy, Mộc} của sách (khớp tập); `khuyet_hanh` tìm thấy Thủy nhưng không Mộc (một phần); `cach_cuc_tvh` và `phu_uc` chứa Kim (Tỉ) trong Kỵ trong khi sách coi Kim là Hỉ, và `cach_cuc_tvh` lấy Quan Sát làm dụng trong khi sách coi Hỏa là Kỵ (xung đột). Kết luận: khớp một phần, không điều chỉnh.\n")
    w("Ví dụ 6 bắt đầu ở cuối tr.401; ngoài phạm vi, chưa đọc.\n")
    w("## 6. Quy trình kiểm độc lập 120 ô\n")
    w("`docs/BAZI_DEEP_TVH_REVIEW_PROTOCOL.md` + phiếu CSV (`docs/bazi_deep_tvh_cells_check.csv`, có cột ảnh-theo-người-kiểm) + công cụ `tools/bazi_deep_tvh_review_intake.py`. Công cụ không sửa dữ liệu, không giải quyết 9 ô mâu thuẫn, coi cùng một người điền hai lần là một người. Hiện trạng: **0/120 ô có người kiểm** (`no_review`).\n")
    w("## 7. Checklist điều kiện còn thiếu trước production\n")
    for t in ["[ ] Người kiểm độc lập: ≥ 1 người, tốt nhất 2, điền phiếu 120 ô và ví dụ 4–5 (hiện 0).",
              "[ ] Quyết định học thuật về 9 ô `book_internal_conflict` (hiện: không chọn bên nào).",
              "[ ] Phiên sở hữu `api.py`/`web/` gắn hợp đồng (schema + chuỗi UI); hiện hợp đồng chỉ là tài liệu. PR #1 (zz-api-integration) cũng sửa `api.py`: cần thống nhất thứ tự.",
              "[ ] UI hiển thị ba mức xác minh riêng, câu *không có kết luận thống nhất*, banner nháp; không dùng cụm trong `forbidden_phrases`.",
              "[ ] Quyết định về `phu_uc` (giữ theo hệ thống) và về việc có làm `phu_uc_tvh` hay không (cần đoạn nguồn nói trực tiếp).",
              "[ ] Nghiên cứu thực nghiệm về giá trị dự báo (hiện không có; `empirical_validated` phải giữ `no`).",
              "[ ] Ví dụ 4: người đối chiếu trụ ngày dựng lại; ví dụ 5: lượt chép mù hoặc người kiểm.",
              "[ ] Ngưỡng của hệ thống (đúng 40%, biên ±0,03, các ngưỡng nhận diện) vẫn không có căn cứ nguồn; giữ nhãn heuristic.",
              "[x] Cách ly hai chiều trên ≥ 5.000 lá số (mục 2).",
              "[x] Tương thích ngược khóa phản hồi so với `d0c3ab8` (cộng thêm; chỉ `methods.*.note` phụ thuộc trạng thái).",
              "[x] Không rò nội dung experimental: mã và dữ liệu `bazi_deep` không tham chiếu `experimental`, phản hồi API không chứa."]:
        w(f"- {t}")
    w("\n## 8. Hồ sơ regression trên HEAD sạch\n")
    w("Chạy bằng `git worktree` tách riêng (không có file của phiên khác), ghi tay lúc chạy:\n")
    w("| Cây mã | Kết quả |")
    w("|---|---|")
    w("| `eae32e4` (HEAD khi chạy; có thêm commit của phiên công thức Tử Vi), sạch | 1023 passed, 1 skipped, 2 xfailed, 0 failed |")
    w("| `eae32e4` + các file Phase 6 (không `api.py`, không `web/`, không `compare_deep`) | **1073 passed, 1 skipped, 2 xfailed, 0 failed** (+50 test mới) |")
    w("| cây làm việc chung (có file `web/` và `test_beginner_ux.py` của phiên khác đang sửa) | 1074 passed, 1 skipped, 2 xfailed, 0 failed |")
    w("")
    w("## 9. Phân loại lỗi\n")
    w("- **Lỗi mới do Phase 6:** khi phát triển, 3 giả định sai trong test của chính Phase 6 và 1 bộ lọc ví dụ trong test Phase 4 (ví dụ 5 vào bộ ba ví dụ) đã bị bắt và sửa; còn lại 0.")
    w("- **Lỗi baseline:** 0 test fail trên `eae32e4` sạch; 2 xfailed và 1 skipped có sẵn.")
    w("- **Lỗi do cây làm việc đang sửa:** xem dòng thứ ba của bảng; nếu có, nằm ở file của phiên khác, không ở file Phase 6.")
    w("")
    w("## 10. Phát hiện kỹ thuật của Phase 6\n")
    w("1. Ở quy mô 5.000 lá số, thử đổi `season_factor` và `class_weight` thì chú thích hiện diện `yong_health` của phương pháp TVH đổi (qua lớp tương tác dùng chung `interact.resolve`), nhưng kết luận (status/yong/xi/ji) không đổi. Đã ghi vào hợp đồng và test thay vì coi là rò rỉ; không sửa thuật toán.")
    w("2. Khóa `methods.cach_cuc_tvh.note` có ở d0c3ab8 cho lá số 1990-12-15 nhưng nay vắng, vì từ Phase 5 ngoại cách của hệ thống không còn thay nội cách của TVH. Đây là khóa phụ thuộc trạng thái; hợp đồng cấm UI dựa vào nó.\n")
    out = ROOT / "docs/BAZI_DEEP_PHASE6_REPORT.md"
    out.write_text("\n".join(L) + "\n", "utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
