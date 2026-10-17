# Phase 8 — Chính xác lịch pháp, kiểm nguồn, mở rộng quy tắc có nguồn (bản nháp)

Sinh bởi `tools/build_phase8_report.py` từ dữ liệu đã ghim. Mọi biến thể vẫn `draft`, không `verified`, không thay đổi baseline 10 cách, UI hay API; không merge, không deploy.

## 1. Lịch pháp

**Lỗi 2033 đã sửa** (`engine/tvbt/lunar_vn.py`, một dòng): cấu trúc tháng được dựng theo `date.year` với trăng mới chỉ tới tháng 3 năm sau, nên một ngày ở tháng 12 dương lịch không thấy được tháng Đông chí kế tiếp và mất tháng nhuận (2033-12-22..31 bị đánh số tháng 12 thay vì nhuận 11). Cửa sổ trăng mới nay gồm `year` và `year+1`. Bằng chứng trước/sau:
- test cũ `xfail(strict)` nay là test thường, đúng: 2033-12-22..31 = (ngày 1..10, tháng 11 nhuận);
- test bất biến mới: mọi cửa sổ 10-12 → 31-01 của 1950–2100 (hai múi giờ) có đánh số tháng liên tiếp, không trùng số; test này **fail trên mã cũ** (đã kiểm bằng `git stash`) và pass trên mã mới;
- quét mở rộng 71,530 ngày (1903-03-01 → 2098-12-31): sản xuất `cn` ↔ HKO **0** sai khác (kể cả trước 1929); sản xuất `vn`/`vn_south` ↔ oracle độc lập: 64 ngày, toàn bộ trong 6 đoạn mà trăng mới sát nửa đêm địa phương (≤45 phút; hai đoạn 2072-12-09 và 2077-11-15 là 1–2 phút TRƯỚC nửa đêm, một điểm phụ thuộc ΔT dự báo nên không ai kiểm chứng được); PyEphem đồng ý với sản xuất, chuỗi amlich là bên xấp xỉ.

| Đoạn khác biệt `vn` ↔ oracle | Phân loại |
|---|---|
| 1939-04-19 → 1939-04-19 | trăng mới sát nửa đêm (PyEphem) |
| 1947-03-22 → 1947-03-22 | trăng mới sát nửa đêm (PyEphem) |
| 2054-05-07 → 2054-05-07 | trăng mới sát nửa đêm (PyEphem) |
| 2062-04-09 → 2062-04-09 | trăng mới sát nửa đêm (PyEphem) |
| 2072-12-09 → 2073-01-07 | trăng mới sát nửa đêm (PyEphem) |
| 2077-11-15 → 2077-12-14 | trăng mới sát nửa đêm (PyEphem) |

Còn tồn tại (không sửa được bằng tính toán): không có bảng lịch Việt Nam xuất bản độc lập để tải về; quy tắc UTC+8 trước 1968 (VASTI 2019) vs 08/1967 (Wikipedia) và mốc 1975 của `vn_south` vẫn là chọn lựa chưa kiểm.

## 2. Kiểm nguồn

Không có quy tắc nào trong 11 quy tắc cần chuyên gia (R01–R11 của Phase 7) được đóng lại: các quyết định đó không thể thay bằng tính toán. Phase 8 chỉ xử lý phần có nguồn rõ.
Audit sau cập nhật: khớp 21, lỏng hơn 13, chặt hơn 11, khác 4, liên quan 25, chưa có nguồn 19 (tổng 93).

## 3. Mở rộng quy tắc có nguồn (không thêm cách cục mới)

Hai nguồn đúng cấu trúc đã bị bỏ sót ở Phase 2–7 nay vào biến thể **Tử Phủ đồng cung**:
- **TT tr.22** (`tt_22`): 'Tử Vi Thiên Phủ toàn y Phụ Bật chi công' → yếu tố tăng thế Tả Phụ + Hữu Bật (audit `ta_huu_hoi` của Tử Phủ đồng cung từ `lien_quan` lên `khop`).
- **KL tr.96** (`kl_50`): 'Thiên phủ đi với Tử vi, Xương Khúc, Hóa khoa, Thiên việt, Thiên khôi thì rất mạnh' → ba yếu tố tăng thế Xương/Khúc, Khôi/Việt, Hóa Khoa (audit `xuong_khuc_hoi`, `khoi_viet_hoi` từ `khong_co_nguon` lên `long_hon`: sách nêu cặp, bản nháp chấp nhận một sao).

Mức xác minh của 51 quy tắc: **10 đối chiếu trực tiếp / 37 có nguồn còn giả định / 4 chưa đủ nguồn** (4 quy tắc mới đều là 'có nguồn còn giả định': phạm vi 'đi với/dựa vào' không nêu, một-trong-hai-sao).

Tác động lên 1.920 lá số có Tử Phủ đồng cung ở Mệnh: TT và KL khác nhau ở **1,439/1,920** (trước đó 658); trạng thái:

| Biến thể | bi_pha | hinh_thuc | thanh | thanh_thuong |
|---|---|---|---|---|
| `kl_50` | 0 | 780 | 536 | 604 |
| `tt_22` | 658 | 1053 | 209 | 0 |

**Chưa đưa vào** (cần quyết định chuyên gia, xem R09 và R03): mệnh đề 'Giáp nhân' của TT tr.22 (điều kiện tuổi Giáp cho vế 'vô sát tấu'); KL tr.85 Tuần/Triệt cứu cho Thái Dương (cứu cho một sao, không cho cả cách); neo Mệnh-hay-Thân (schema chỉ có một cung neo).

## 4. Độ khớp oracle sau thay đổi

Oracle độc lập (không import `tvbt`) chạy lại trên 116,928 lá số với 17 biến thể đã mở rộng: **0** sai khác (vị trí sao, Tứ Hóa, Tuần/Triệt, trạng thái từng biến thể). Quét tần suất, độ nhạy cách đọc, độ nhạy bảng Tứ Hóa đã chạy lại và ghim.

## 5. Regression

- Worktree sạch của HEAD `18c698a`: **1200 passed, 1 skipped, 2 xfailed, 0 failed (git archive của HEAD, pytest trong engine/)**.
- Ghi chú: Xfail 2033 của Phase 7 đã thành test thường (lỗi đã sửa); còn hai xfail có từ trước. Hai test `test_bazi_deep_tvh_audit` của phiên Bát Tự vẫn không thuộc HEAD sạch và không được sửa. Baseline 10 cách, UI và API mặc định không đổi. Test đọc PDF tự bỏ qua khi thiếu sách và không được tính là bằng chứng; bằng chứng nằm ở JSON đã ghim.

## 6. Việc còn mở cho Phase 9

1. Quyết định của chuyên gia R01–R05 (phạm vi 'hội/gặp/chiếu', liệt kê Kiếp-Không-Kị, ngưỡng sát tinh, Nhâm-Khoa).
2. Nhãn `verified` của `tu_hoa` trong `SCHOOL_PACK` (đề xuất `verified_with_variants`).
3. Bảng lịch Việt Nam xuất bản độc lập (nếu tìm được) để kiểm `vn` thay vì chỉ amlich + PyEphem.
4. Thêm neo Thân cho Tử Phủ đồng cung (cần mở rộng schema anchor) và mệnh đề 'Giáp nhân'.
5. Số phận ba quy tắc `chua_du_nguon` của Khôi Việt giáp Mệnh và quy ước Sát Phá Liêm Tham.

