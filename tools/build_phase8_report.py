"""docs/PHASE8_CALENDAR_AND_RULE_EXPANSION.md — formatting of pinned data only."""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
J = lambda p: json.load(open(ROOT / p, encoding="utf-8"))
CAL, ST, AUD, VAR = J("engine/tests/fixtures/calendar_comparison.json"), J("engine/tests/fixtures/formation_variant_stats.json"), J("engine/data/experimental/formation_audit.json"), J("engine/data/experimental/formations_school_variants.json")
ORC = J("engine/tests/fixtures/formation_oracle_full.json")
REG = J("docs/phase8_regression.json") if (ROOT / "docs/phase8_regression.json").exists() else {}
lv = collections.Counter(x for v in VAR["meta"].values() for x in v["rules"].values())
S = AUD["summary"]["by_status"]
tp = {k.split("@")[1]: v for k, v in ST["states"].items() if "TU_PHU_DONG_CUNG@" in k}
pair = ST["pairs"]["CACH_X_TU_PHU_DONG_CUNG@tt_22|CACH_X_TU_PHU_DONG_CUNG@kl_50"]
L = ["# Phase 8 — Chính xác lịch pháp, kiểm nguồn, mở rộng quy tắc có nguồn (bản nháp)", "",
     "Sinh bởi `tools/build_phase8_report.py` từ dữ liệu đã ghim. Mọi biến thể vẫn `draft`, không `verified`, không thay đổi baseline 10 cách, UI hay API; không merge, không deploy.", "",
     "## 1. Lịch pháp", "",
     "**Lỗi 2033 đã sửa** (`engine/tvbt/lunar_vn.py`, một dòng): cấu trúc tháng được dựng theo `date.year` với trăng mới chỉ tới tháng 3 năm sau, nên một ngày ở tháng 12 dương lịch không thấy được tháng Đông chí kế tiếp "
     "và mất tháng nhuận (2033-12-22..31 bị đánh số tháng 12 thay vì nhuận 11). Cửa sổ trăng mới nay gồm `year` và `year+1`. Bằng chứng trước/sau:",
     "- test cũ `xfail(strict)` nay là test thường, đúng: 2033-12-22..31 = (ngày 1..10, tháng 11 nhuận);",
     "- test bất biến mới: mọi cửa sổ 10-12 → 31-01 của 1950–2100 (hai múi giờ) có đánh số tháng liên tiếp, không trùng số; test này **fail trên mã cũ** (đã kiểm bằng `git stash`) và pass trên mã mới;",
     f"- quét mở rộng {CAL['days']:,} ngày ({CAL['range'][0]} → {CAL['range'][1]}): sản xuất `cn` ↔ HKO **{CAL['counts']['cn_vs_hko']}** sai khác (kể cả trước 1929); sản xuất `vn`/`vn_south` ↔ oracle độc lập: {CAL['counts']['vn_vs_oracle']} ngày, "
     "toàn bộ trong 6 đoạn mà trăng mới sát nửa đêm địa phương (≤45 phút; hai đoạn 2072-12-09 và 2077-11-15 là 1–2 phút TRƯỚC nửa đêm, một điểm phụ thuộc ΔT dự báo nên không ai kiểm chứng được); PyEphem đồng ý với sản xuất, chuỗi amlich là bên xấp xỉ.", "",
     "| Đoạn khác biệt `vn` ↔ oracle | Phân loại |", "|---|---|"]
for a, b in CAL["spans"]["vn_vs_oracle"]:
    L.append(f"| {a} → {b} | trăng mới sát nửa đêm (PyEphem) |")
L += ["", "Còn tồn tại (không sửa được bằng tính toán): không có bảng lịch Việt Nam xuất bản độc lập để tải về; quy tắc UTC+8 trước 1968 (VASTI 2019) vs 08/1967 (Wikipedia) và mốc 1975 của `vn_south` vẫn là chọn lựa chưa kiểm.", "",
      "## 2. Kiểm nguồn", "",
      "Không có quy tắc nào trong 11 quy tắc cần chuyên gia (R01–R11 của Phase 7) được đóng lại: các quyết định đó không thể thay bằng tính toán. Phase 8 chỉ xử lý phần có nguồn rõ.",
      f"Audit sau cập nhật: khớp {S['khop']}, lỏng hơn {S['long_hon']}, chặt hơn {S['chat_hon']}, khác {S['khac']}, liên quan {S['lien_quan']}, chưa có nguồn {S['khong_co_nguon']} (tổng {AUD['summary']['total']}).", "",
      "## 3. Mở rộng quy tắc có nguồn (không thêm cách cục mới)", "",
      "Hai nguồn đúng cấu trúc đã bị bỏ sót ở Phase 2–7 nay vào biến thể **Tử Phủ đồng cung**:",
      "- **TT tr.22** (`tt_22`): 'Tử Vi Thiên Phủ toàn y Phụ Bật chi công' → yếu tố tăng thế Tả Phụ + Hữu Bật (audit `ta_huu_hoi` của Tử Phủ đồng cung từ `lien_quan` lên `khop`).",
      "- **KL tr.96** (`kl_50`): 'Thiên phủ đi với Tử vi, Xương Khúc, Hóa khoa, Thiên việt, Thiên khôi thì rất mạnh' → ba yếu tố tăng thế Xương/Khúc, Khôi/Việt, Hóa Khoa (audit `xuong_khuc_hoi`, `khoi_viet_hoi` từ `khong_co_nguon` lên `long_hon`: sách nêu cặp, bản nháp chấp nhận một sao).", "",
      f"Mức xác minh của {sum(lv.values())} quy tắc: **{lv['doi_chieu_truc_tiep']} đối chiếu trực tiếp / {lv['co_nguon_con_gia_dinh']} có nguồn còn giả định / {lv['chua_du_nguon']} chưa đủ nguồn** (4 quy tắc mới đều là 'có nguồn còn giả định': phạm vi 'đi với/dựa vào' không nêu, một-trong-hai-sao).", "",
      f"Tác động lên 1.920 lá số có Tử Phủ đồng cung ở Mệnh: TT và KL khác nhau ở **{pair['differ']:,}/{pair['both_fire']:,}** (trước đó 658); trạng thái:", "",
      "| Biến thể | " + " | ".join(sorted({s for v in tp.values() for s in v if s != 'khong_hien'})) + " |", "|---|" + "---|" * len({s for v in tp.values() for s in v if s != 'khong_hien'})]
for k, v in tp.items():
    cols = sorted({s for vv in tp.values() for s in vv if s != 'khong_hien'})
    L.append(f"| `{k}` | " + " | ".join(str(v.get(c, 0)) for c in cols) + " |")
L += ["", "**Chưa đưa vào** (cần quyết định chuyên gia, xem R09 và R03): mệnh đề 'Giáp nhân' của TT tr.22 (điều kiện tuổi Giáp cho vế 'vô sát tấu'); KL tr.85 Tuần/Triệt cứu cho Thái Dương (cứu cho một sao, không cho cả cách); neo Mệnh-hay-Thân (schema chỉ có một cung neo).", "",
      "## 4. Độ khớp oracle sau thay đổi", "",
      f"Oracle độc lập (không import `tvbt`) chạy lại trên {ORC['charts']:,} lá số với 17 biến thể đã mở rộng: **{sum(ORC['mismatches'].values())}** sai khác (vị trí sao, Tứ Hóa, Tuần/Triệt, trạng thái từng biến thể). Quét tần suất, độ nhạy cách đọc, độ nhạy bảng Tứ Hóa đã chạy lại và ghim.", "",
      "## 5. Regression", ""]
if REG:
    L += [f"- Worktree sạch của HEAD `{REG['head']}`: **{REG['summary']}**.", f"- Ghi chú: {REG['note']}"]
L += ["", "## 6. Việc còn mở cho Phase 9", "",
      "1. Quyết định của chuyên gia R01–R05 (phạm vi 'hội/gặp/chiếu', liệt kê Kiếp-Không-Kị, ngưỡng sát tinh, Nhâm-Khoa).",
      "2. Nhãn `verified` của `tu_hoa` trong `SCHOOL_PACK` (đề xuất `verified_with_variants`).",
      "3. Bảng lịch Việt Nam xuất bản độc lập (nếu tìm được) để kiểm `vn` thay vì chỉ amlich + PyEphem.",
      "4. Thêm neo Thân cho Tử Phủ đồng cung (cần mở rộng schema anchor) và mệnh đề 'Giáp nhân'.",
      "5. Số phận ba quy tắc `chua_du_nguon` của Khôi Việt giáp Mệnh và quy ước Sát Phá Liêm Tham.", ""]
(ROOT / "docs/PHASE8_CALENDAR_AND_RULE_EXPANSION.md").write_text("\n".join(L) + "\n", encoding="utf-8")
