"""docs/PHASE7_SOURCE_CRITICAL_VALIDATION.md — formatting of pinned data only (dossiers, fixtures, audit, variants). No judgement lives in this file."""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
J = lambda p: json.load(open(ROOT / p, encoding="utf-8"))
RULES = J("engine/data/experimental/formation_rule_dossier.json")["rules"]
VD = J("engine/data/experimental/formation_variant_dossier.json")["variants"]
AUD = J("engine/data/experimental/formation_audit.json")
VAR = J("engine/data/experimental/formations_school_variants.json")
RD, CAL = J("engine/tests/fixtures/readings_sensitivity.json"), J("engine/tests/fixtures/calendar_comparison.json")
TH, TT = J("engine/tests/fixtures/tu_hoa_sensitivity.json"), J("engine/data/experimental/tu_hoa_tables.json")
REG = J("docs/phase7_regression.json") if (ROOT / "docs/phase7_regression.json").exists() else {}
CLS = {"nguon_xac_nhan": "nguồn xác nhận", "nguon_mau_thuan": "nguồn mâu thuẫn", "nguon_chua_du": "nguồn chưa đủ"}
LV = {"doi_chieu_truc_tiep": "đối chiếu trực tiếp", "co_nguon_con_gia_dinh": "có nguồn còn giả định", "chua_du_nguon": "chưa đủ nguồn"}
short = lambda s: s.replace("CACH_X_", "")
pct = lambda a, b: f"{100 * a / b:.1f}%"
SC = {"dong_cung": "đồng cung", "doi_cung": "đối cung", "tam_hop": "hai tam hợp", "hoi_chieu": "hội chiếu (đối + tam hợp)", "tp": "tam phương tứ chính"}


def cut(s, n=150):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"


def main():
    st = collections.Counter(r["status"] for r in AUD["rows"])
    lv = collections.Counter(x for v in VAR["meta"].values() for x in v["rules"].values())
    fits = collections.Counter(r["structure_fit"] for r in AUD["rows"])
    L = ["# Phase 7 — Kiểm chứng nguồn có phê phán (source-critical) cho 17 biến thể cách cục Tử Vi (bản nháp)", "",
         "Sinh bởi `tools/build_phase7_report.py` từ các file đã ghim. **Không quy tắc nào được đóng dấu `verified`, không cách đọc nào được chọn, không giả làm ý kiến chuyên gia.** "
         "Oracle khớp sản xuất chỉ chứng minh hai bản hiện thực nhất quán; mục tiêu của Phase 7 là tìm những chỗ mà cả hai (hoặc audit) đã âm thầm giả định.", "",
         "## 0. Kết quả chính", "",
         f"1. **Tứ Hóa Nhâm-Khoa** (R05): khác biệt giữa hai dòng văn bản, không phải lỗi in một chỗ và không phải lỗi diễn giải: TH tr.20 *và* tr.21 in Thiên Phủ; KL tr.36, tr.197 in Tả Phụ; một văn bản 紫微斗數全書 số hóa độc lập cũng ghi 府. "
         "Production giữ bảng KL; ba bảng theo nguồn được lưu riêng; ghi chú sai 'agree on all ten stems' trong `tuvi.py` đã sửa (chỉ chữ, không đổi logic).",
         f"2. **Hai breaker tỷ lệ phá cao** (R03): 82,1% và 91,7% đều đến từ ngưỡng 'một sát tinh/một trong ba' ở phạm vi tam phương. Thu hẹp phạm vi hay siết cách đọc kéo xuống 0–69%; không cách nào được chọn. "
         "Với Khôi Việt giáp Mệnh còn phát hiện thêm: các câu KL tr.62 nói về Khôi Việt Ở Mệnh, không phải giáp Mệnh (cấu trúc khác) nên ba quy tắc bị hạ xuống `chua_du_nguon`.",
         f"3. **Đọc lại toàn đoạn** {len({c['id'] for r in AUD['rows'] for c in r['cites']})} câu trích khác nhau của audit (không chỉ từ khoá): {fits['khac_cau_truc']} dòng audit có nguồn thuộc cấu trúc lân cận (chuyển về `lien_quan`), {fits['khac_ngu_canh']} dòng nói về đại tiểu hạn, "
         "bỏ sót nhiều đoạn có ích (mục 4). Số quy tắc của 17 biến thể nay là "
         f"**{lv['doi_chieu_truc_tiep']} đối chiếu trực tiếp / {lv['co_nguon_con_gia_dinh']} có nguồn còn giả định / {lv['chua_du_nguon']} chưa đủ nguồn** (tổng {sum(lv.values())}).",
         f"4. **Lịch pháp**: lịch Trung Quốc của sản xuất khớp bảng Hong Kong Observatory trên {CAL['days']:,} ngày (0 sai khác). Lịch Việt Nam khớp oracle amlich độc lập, trừ 4 đoạn: 3 ngày sát nửa đêm (new moon trong 40 phút sau 0h) và "
         "**một lỗi thật của sản xuất**: 2033-12-22..31 (tháng nhuận 11) bị đánh số là tháng 12. Lỗi ghi lại bằng test `xfail`, chưa sửa (ngoài phạm vi).",
         "5. **Oracle mở rộng**: mọi công thức an sao của oracle (Địa Kiếp/Không, Hỏa/Linh, Kình/Đà, Thiên Hình, Lực Sĩ, Thiên Mã, Lộc Tồn, Tuần, Triệt, Khôi Việt) có câu in trong Thực Hành và ví dụ minh họa của chính sách được chạy lại; "
         "thêm kiểm biên: giờ Tý, giao ngày/Tết, tháng nhuận (3 quy tắc), Lập Xuân so với Tết, múi giờ.", "",
         "## 1. Ma trận 11 quy tắc cần chuyên gia", "",
         "| # | Quy tắc | Phân loại | Nguồn chính | Cách đọc có căn cứ (✓ = đang dùng) | Tác động đo được | Cần quyết định |", "|---|---|---|---|---|---|---|"]
    for r in RULES:
        src = "; ".join(f"{p['book_code']} tr.{p['page']}" for p in r["passages"][:7]) or "—"
        rds = "<br>".join(("✓ " if x["implemented"] else "") + x["text"] for x in r["readings"][:5]) or "—"
        imp = r["impact"].get("mo_ta", "")
        L.append(f"| {r['id']} | {r['title']} | **{CLS[r['classification']]}** | {src} | {rds} | {imp} (số liệu ở mục dưới / JSON) | {r['decision'] or '—'} |")
    L += ["", "### 1.1 Hồ sơ từng quy tắc", "", "Mỗi mục: nguyên văn · trang · ngữ cảnh trước/sau (tự trích từ trang; câu in trong ảnh được ghi 'đọc từ ảnh') · kết luận. Toàn bộ trong `formation_rule_dossier.json`.", ""]
    for r in RULES:
        L += [f"#### {r['id']} — {r['title']}", "", f"*Câu hỏi:* {r['question']}", f"*Phân loại:* **{CLS[r['classification']]}** · *Trạng thái:* {r['trang_thai']}", ""]
        for p in r["passages"]:
            ctx = p["context"]
            c = f" _…{cut(ctx['truoc'][-110:], 110)}_ **[câu]** _{cut(ctx['sau'], 110)}…_" if isinstance(ctx, dict) else f" ({ctx})"
            L.append(f"- {p['book_code']} tr.{p['page']} ({p['how']}): “{p['quote']}”{c}")
        for e in r.get("extra", []):
            L.append(f"- {e['book']}{' tr.' + str(e['page']) if e['page'] else ''}: “{e['quote']}” — {e['how']}")
        if r.get("evidence_for_distinguishing"):
            L += ["", r["evidence_for_distinguishing"]]
        if r.get("verdict"):
            L += ["", f"**Kết luận:** {r['verdict']}"]
        if r.get("note"):
            L += ["", f"*Ghi chú:* {r['note']}"]
        L += ["", f"*Đang triển khai:* {r['current']}.", ""]
    n = RD["A_core"]["n"]
    L += ["## 2. Tứ Hóa: Nhâm-Khoa (và Canh)", "",
          "| Nguồn | Nhâm: Lộc · Quyền · Khoa · Kỵ | Canh: Lộc · Quyền · Khoa · Kỵ | Ghi chú |", "|---|---|---|---|"]
    for k in ("KL", "TH", "TT_WS"):
        t = TT["tables"][k]
        L.append(f"| {TT['sources'][k]['label']} | {' · '.join(t['Nhâm'].values())} | {' · '.join(t['Canh'].values())} | {TT['sources'][k]['note']} |")
    L += ["", f"Độ nhạy (oracle, 16.704 lá số của hai năm Canh và hai năm Nhâm): đổi bảng Canh **không** đổi trạng thái biến thể nào; đổi Nhâm-Khoa sang Thiên Phủ đổi "
          f"{', '.join(f'{short(k)}: {v}' for k, v in TH['Nhâm|TH']['differ'].items())} lá số. Bảng riêng từng nguồn: `engine/data/experimental/tu_hoa_tables.json`. "
          "**Cơ chế lựa chọn đề xuất (chưa nối):** tham số `tu_hoa_table` = `KL` (mặc định hiện tại) | `TH` | `TT_WS`; kết quả luôn kèm nhãn nguồn và cảnh báo khi hai bảng cho kết quả khác nhau; không bao giờ đổi âm thầm.", "",
          "## 3. Độ nhạy của hai breaker có tỷ lệ phá cao", "",
          f"### 3.1 Cơ Nguyệt Đồng Lương — TT tr.24 (lõi đúng ở {n:,} lá số). Tỷ lệ bị phá theo phạm vi và cách đọc liệt kê", "",
          "| Phạm vi | một trong ba (Không, Kiếp, Kỵ) — đang dùng | cặp Không-Kiếp hoặc Kỵ | ít nhất hai trong ba | đủ cả ba |", "|---|---|---|---|---|"]
    for sc in ("dong_cung", "doi_cung", "tam_hop", "hoi_chieu", "tp"):
        L.append(f"| {SC[sc]} | " + " | ".join(pct(RD['A'][f'{sc}|{c}'], n) for c in ("mot_trong_ba", "cap_khong_kiep_hoac_ky", "tu_hai_trong_ba", "du_ca_ba")) + " |")
    nb, nb2 = RD["B_core"]["n"], RD["B2_core"]["n"]
    L += ["", "Câu của TT: 'Mệnh thân và các cung tam hợp xung chiếu có đủ bốn sao ... Gặp Kiếp Không Hoá Kị xuống hạ cách'. Phạm vi tam phương có căn cứ vì chính câu đã nêu 'tam hợp xung chiếu'; "
          "nhưng 'gặp' có thể chỉ Mệnh/Thân, và liệt kê ba sao có thể đòi đủ ba. Mọi ô trong bảng đều có chỗ dựa trong câu; ô nào cũng không được chọn.", "",
          f"### 3.2 Khôi Việt giáp Mệnh — KL tr.62 mục 4 (lõi đúng ở {nb:,} lá số). Tỷ lệ phá theo phạm vi / tập sát tinh / ngưỡng", "",
          "| Phạm vi · tập sát tinh | ≥1 | ≥2 | ≥3 |", "|---|---|---|---|"]
    for sname, lab in (("sau_sat", "sáu sát tinh"), ("tu_sat", "Tứ sát (Kình Đà Hỏa Linh)"), ("khong_kiep", "Không Kiếp")):
        for sc in ("dong_cung", "doi_cung", "hoi_chieu", "tp"):
            L.append(f"| {SC[sc]} · {lab} | " + " | ".join(pct(RD['B'][f'{sc}|{sname}|>={t}'], nb) for t in (1, 2, 3)) + " |")
    L += ["", f"Điều quan trọng: câu KL tr.62 mục 4 mô tả 'Cung mệnh CÓ Khôi Việt lại bị sát tinh hội chiếu', không phải Khôi Việt *giáp* Mệnh. Trên cấu trúc đúng như sách mô tả (Khôi Việt cùng trong tam phương, {nb2:,} lá số) "
          f"'ít nhất một sát tinh hội chiếu' vẫn đúng ở {pct(RD['B2']['tp|sau_sat|>=1'], nb2)} lá số. Nghĩa là tần suất cao do **ngưỡng một sát tinh**, không do việc áp sang cấu trúc giáp. "
          "Nhưng việc áp sang cấu trúc giáp là một suy diễn riêng nên quy tắc bị đánh `chua_du_nguon`.", "",
          f"### 3.3 Sát Phá Liêm Tham — TH tr.77 'nhiều sát tinh' (lõi đúng ở {RD['C_core']['n']:,} lá số)", "",
          "| Ngưỡng | không Kỵ | kèm Kỵ |", "|---|---|---|"]
    for t in (1, 2, 3, 4):
        L.append(f"| ≥{t} sát tinh | {pct(RD['C'][f'>={t}'], RD['C_core']['n'])} | {pct(RD['C'][f'>={t}+Ky'], RD['C_core']['n'])} |")
    L += ["", "Các tỷ lệ này là tần suất toán học của điều kiện trong mô hình, không phải độ đúng của sách. Việc điều kiện phá hầu như luôn đúng nghĩa là nó không phân biệt được lá số tốt/xấu; "
          "KL tr.199-200 còn cho Khoa, Tuần Triệt làm 'hung tinh lép vế', tức sát tinh không phá tuyệt đối.", "",
          "## 4. Đọc lại toàn đoạn: phát hiện và hiệu chỉnh audit", "",
          "Phase 6 chỉ kiểm câu trích có chứa từ khoá. Phase 7 đọc cả đoạn quanh mỗi câu (ngữ cảnh lưu trong dossier). Kết quả:", "",
          "**Sai/yếu của audit (đã sửa trong dữ liệu):**", "",
          "- Mười dòng audit có trang nói về **cấu trúc lân cận** (`structure_fit = khac_cau_truc`), nay chỉ được xếp `lien_quan`: Khôi Việt giáp Mệnh (3 dòng; KL tr.62 nói Khôi Việt *ở* Mệnh), Tam kỳ gia hội Hóa ở bản cung "
          "(TH tr.72 mục 12 là *Tam Hóa liên châu*, ba cung liền), Tả Hữu của Tử Phủ đồng cung (KL tr.49 nói Tử Vi), cát tinh của Sát Phá Liêm Tham (danh sách TH tr.76 là của Thượng cách), Tả Hữu và Khoa Quyền Lộc của Nhật Nguyệt tịnh minh.",
          "- Ba dòng Tử Phủ Vũ Tướng dựa vào TH tr.115-116 là **đại tiểu hạn**, không phải bản cách (`khac_ngu_canh`).",
          "- Hai dòng Kỵ/Thái Dương dẫn câu 'Tuần Triệt' thay vì câu 'ghét Kỵ'; một dòng Cơ Nguyệt Đồng Lương dẫn nhầm câu về Sát Phá Tham — đã thay (Phase 6).",
          "- Trang TH tr.72, tr.74: đã đọc ảnh; câu ghi nguyên văn kể cả lỗi in của sách; TH tr.74 mục 7 máy kiểm được.", "",
          "**Đoạn có ích mà audit trước bỏ sót (chưa đưa vào biến thể; đề xuất Phase 8):**", "",
          "- TT tr.22: 'Tử Vi Thiên Phủ toàn y Phụ Bật chi công' — nguồn đúng cấu trúc cho yếu tố tăng thế Tả Hữu của Tử Phủ đồng cung.",
          "- KL tr.96: 'Nếu Thiên phủ đi với Tử vi, Xương Khúc, Hóa khoa, Thiên việt, Thiên khôi thì rất mạnh' — nguồn cho tăng thế Xương Khúc/Khôi Việt của Tử Phủ.",
          "- TT tr.22: 'Tử Phủ đồng cung vô sát tấu, **Giáp nhân** hưởng phúc chung thân': mệnh đề chỉ cho tuổi Giáp; biến thể `tt_22` bỏ điều kiện này.",
          "- KL tr.85: 'Thái dương sợ: Kình, Đà, Không, Kiếp ... **cần Tuần Triệt cứu giải**' và KL tr.106: 'Cự môn hãm địa cần có Hóa khoa cứu giải' — hai chỗ sách nói trực tiếp sao cứu cho MỘT SAO; chưa phải cứu cho cả cách, nên vẫn không có sao cứu trong biến thể.",
          "- TT tr.142: 'Khoa, Quyền lộc củng (**Chiếu thủ** có cả ba)' — củng cố cách đọc 'hội' = Mệnh cùng các cung chiếu cho Tam Hóa.",
          "- KL tr.44 có mục 7 'Tam hoá liên châu' lặp nguyên định nghĩa của mục 6 Thạch trung ẩn ngọc (nghi lỗi in của sách).", "",
          "**Hai lá số KL tr.221 không khớp (Hạng Võ, Mậu Tý) — kiểm lại:** KL tr.221 (ảnh đã đọc) là phần *loại hình*: 'may thì làm quan, xui thì làm công chức ba cọc ba đồng', 'hội Tả Hữu Quang Quí, Thiên quan, Thiên phúc → bác sĩ danh tiếng', "
          "'hội Khoa Quyền Lộc, Khôi Việt, Xương Khúc → giáo sư danh tiếng'; **không nêu yếu tố phá**. Việc sách coi hai lá số là thất bại nằm ở phần luận cung (tr.238, tr.246): Hạng Võ — Tài có Đồng Lương ngộ Triệt và Địa Kiếp, Quan có Thái Âm ngộ Tuần, Di có Cự Kỵ; "
          "Mậu Tý — Cơ Hóa Kỵ gặp Hỏa Linh ở Tài. Oracle xác nhận từng chi tiết đó trên lá số dựng lại (Triệt và Địa Kiếp cùng cung Đồng Lương; Tuần cùng cung Thái Âm; Hỏa, Linh, Cơ Kỵ cùng cung Tý). "
          "Biến thể TT tr.24 chỉ bắt được qua Kiếp/Kỵ, **không** qua Tuần/Triệt (TT không liệt kê). Đây là khác biệt thể loại bên trong một cuốn, không phải mâu thuẫn quy tắc; và không có cơ sở để thêm Tuần/Triệt làm breaker chỉ để khớp hai lá số.", "",
          "## 5. Kiểm lịch pháp độc lập", "",
          f"Tham chiếu: bảng *Gregorian-Lunar Calendar Conversion Table* của Hong Kong Observatory 1901–2100 (UTC+8; `calendar_reference_hko.json`) và thuật toán amlich (Hồ Ngọc Đức) viết lại độc lập (`oracle_calendar_independent.py`; không import `tvbt`, không dùng `sxtwl`), "
          f"được xác nhận với HKO trước khi dùng cho UTC+7. Quét {CAL['days']:,} ngày 1930-03-01 → 2060-12-31:", "",
          "| So sánh | Số ngày khác nhau | Phân loại |", "|---|---|---|",
          f"| sản xuất `cn` (sxtwl) ↔ HKO | {CAL['counts']['cn_vs_hko']} | **khớp hoàn toàn** |",
          f"| oracle amlich UTC+8 ↔ HKO | {CAL['counts']['oracle8_vs_hko']} | 4 ngày có trăng mới trong 40 phút sau nửa đêm (1939-04-19, 1947-03-22, 2009-03-26, 2054-05-07): giới hạn độ chính xác của oracle, sản xuất đúng |",
          f"| sản xuất `vn` ↔ oracle (UTC+8 trước 1968, UTC+7 từ 1968) | {CAL['counts']['vn_vs_oracle']} | 3 ngày trên (cùng ngày borderline) + **2033-12-22..31: lỗi của sản xuất** |",
          f"| sản xuất `vn_south` ↔ oracle (UTC+8 đến 1975) | {CAL['counts']['vn_south_vs_oracle']} | như trên |", "",
          "**Lỗi lịch pháp thật (chỉ đường `vn`/`vn_south`):** 2033-12-22..31 thuộc tháng nhuận 11 (sxtwl, HKO, amlich và PyEphem đều đồng ý: tháng bắt đầu 12-22 không chứa trung khí; Đại Hàn rơi 2034-01-20), nhưng `lunar_vn.solar_to_lunar` cắt cấu trúc theo năm dương nên gán 12-22 là tháng 12 ngày 1 "
          "và 2034-01-20 lại là tháng 12 ngày 1 (hai tháng 12), cờ nhuận chỉ xuất hiện ở bên 2034. Tác động: Mệnh/Thân của người sinh trong 10 ngày này (đường lịch Việt) lệch một cung. Bằng chứng: test `xfail(strict)` + `test_the_2033_bug_is_confined_to_the_vietnamese_path_and_has_a_precise_signature`. "
          "Chưa sửa vì ngoài phạm vi và thuộc module của phiên khác; hướng sửa: tính cấu trúc theo cặp trung khí Đông chí liên tiếp thay vì `date.year`.", "",
          "**Kiểm biên** (`test_calendar_independent.py`): giờ Tý (22:59, 23:00, 23:59, 00:00, 00:59, 01:00, 02:59, 03:00 × hai quy tắc Tý sớm/muộn); giao ngày; Tết 2024 với Tý 23:30 (hai quy tắc cho hai năm khác nhau: Giáp Thìn vs Quý Mão — lựa chọn trường phái, không phải lỗi); "
          "Tử Vi dùng năm âm lịch chứ không phải Lập Xuân (2024-02-05); mọi tháng nhuận 1950–2050 (≥35) ở hai phía ranh giới; ba quy tắc tháng nhuận `same_month/next_month/split_15` so với oracle; múi giờ không đổi ngày âm đọc từ lịch treo tường nhưng đổi UTC; "
          "khoảng không tồn tại do DST bị từ chối; Tết 1968 (Việt Nam 29-1 vs Trung Quốc 30-1, trăng mới 16:29 UTC) tái hiện quy tắc UTC+7 từ 1968.", "",
          "**Phân tách ba tầng lỗi:**", "",
          "| Tầng | Kiểm bằng | Kết quả |", "|---|---|---|",
          "| Lịch pháp (dương → âm → can chi) | HKO, amlich, PyEphem, quét 47.789 ngày, kiểm biên | 1 lỗi thật (2033-12-22..31, đường VN); phần còn lại khớp |",
          "| An sao | oracle không import `tvbt` trên 116.928 lá số + công thức tra trang TH + ví dụ in trong sách + 6 lá số KL | 0 sai khác; hai chỗ sách khác nhau (Nhâm-Khoa, độ sáng Thân/Mùi) |",
          "| Luận cách | 17 biến thể, audit từng quy tắc, độ nhạy cách đọc | không phải đúng/sai; xem ma trận mục 1 |", "",
          "Giới hạn: không có bảng lịch Việt Nam xuất bản độc lập để tải về; phần Việt Nam dựa vào amlich + PyEphem và quy tắc UTC+8 trước 1968 (nguồn quy tắc: tài liệu mô-đun; VASTI 1/2019 theo chú thích của `calendar_core.py`, Wikipedia ghi 8/1967 — nguồn khác nhau); `vn_south` đến 1975 vẫn ghi là chưa xác minh.", "",
          "## 6. Hồ sơ học thuật từng biến thể", "",
          "Mỗi biến thể hiển thị được: trường phái và sách; điều kiện trích trực tiếp; điều kiện còn giả định; mức xác minh từng quy tắc; trường phái đưa kết luận khác (`formation_variant_dossier.json`).", "",
          "| Biến thể | Trường phái · sách | trực tiếp | giả định | chưa đủ nguồn | Kích hoạt | Trường phái khác (mức khác biệt) |", "|---|---|---|---|---|---|---|"]
    for v in VD:
        c = collections.Counter(r["level"] for r in v["rules"])
        conf = "; ".join(f"{x['variant'].split('@')[1]}" + (f" ({x['khac_nhau']:,}/{x['ca_hai_hien']:,})" if x["khac_nhau"] is not None else "") for x in v["conflicting_variants"]) or "—"
        L.append(f"| `{short(v['id'])}` | {v['school']} · {', '.join(v['books'][:4])} | {c['doi_chieu_truc_tiep']} | {c['co_nguon_con_gia_dinh']} | {c['chua_du_nguon']} | {v['kich_hoat_pct']}% | {conf} |")
    L += ["", "## 7. Regression", ""]
    if REG:
        L += [f"- Worktree sạch của HEAD `{REG['head']}`: **{REG['summary']}**.", f"- Ghi chú: {REG['note']}"]
    L += ["", "## 8. Đề xuất ưu tiên cho Phase 8", "",
          "1. **Quyết định của chuyên gia** cho R01–R05 (phạm vi 'hội/gặp/chiếu', liệt kê Kiếp-Không-Kị, ngưỡng sát tinh, Nhâm-Khoa). Cung cấp cho họ ma trận mục 1 và hai bảng mục 3; không triển khai gì trước đó.",
          "2. **Sửa lỗi lịch 2033** trong `lunar_vn.solar_to_lunar` (module của phiên khác) rồi bỏ `xfail`; thêm quét độc lập hằng năm cho `vn` so với oracle.",
          "3. **Thêm quy tắc có nguồn đúng cấu trúc** đã tìm thấy: TT tr.22 (Tả Hữu và mệnh đề tuổi Giáp), KL tr.96 (Xương Khúc, Khoa, Khôi Việt) cho Tử Phủ đồng cung — kèm quét lại 116.928 lá số.",
          "4. **Quyết định số phận quy tắc `chua_du_nguon` của Khôi Việt giáp Mệnh** (loại khỏi bản có nguồn hay giữ như giả thuyết); không dựa vào tỷ lệ phá.",
          "5. **Tham số `tu_hoa_table`** hiển thị trong kết quả (chỉ sau khi chuyên gia chọn mặc định).",
          "6. **Tra bảng độ sáng đầy đủ** của Thái Dương ở Thân/Mùi từ nguồn thứ hai; hiện để trống.",
          "7. **Tuần/Triệt**: viết quy tắc ưu tiên khi Tuần/Triệt vừa hại quý tinh vừa cứu hung tinh trong cùng lá số.",
          "8. **Nhãn `verified` của `tu_hoa` trong `SCHOOL_PACK`** (tuvi.py) không còn đúng khi hai nguồn của chính dự án bất đồng ở Nhâm-Khoa; Phase 7 chỉ sửa ghi chú, chưa đổi nhãn (đổi nhãn đổi đầu ra API). Đề xuất `verified_with_variants` như `leap_month`, khi chủ module đồng ý.",
          "9. **Đối chiếu sách giấy** cho những câu chỉ đọc được từ ảnh (`anh_doc_ro`), đặc biệt TH tr.72."]
    (ROOT / "docs/PHASE7_SOURCE_CRITICAL_VALIDATION.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
