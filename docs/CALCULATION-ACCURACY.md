# Độ chính xác của phần lập lá số Tử Vi (2026-10-20)

Phạm vi: phần **tính toán** (vị trí sao, độ sáng, lớp lưu niên, nguyệt hạn). Phần luận giải ở `docs/REASONER-DESIGN.md`.

## Bằng chứng đối chiếu

| Loại | Gì | Ý nghĩa |
|---|---|---|
| Đối chiếu độc lập | `engine/tests/reference_charts/2002-01-09_0430_nam.json` (bảng tuvi.vn #260902 do người dùng cung cấp, chép tay) | **1 lá số** khớp toàn bộ: 12 cung, can cung, đại hạn, Tràng Sinh, Tuần/Triệt, Thân, 14 chính tinh, ~100 phụ tinh nguyên cục; 20/21 sao lưu năm 2026; 12/12 tháng nguyệt hạn. Một lá số không đủ để nói "đúng tuyệt đối". |
| Tự nhất quán (không phải đối chiếu) | `tools/regress_charts.py` — 35.120 lá ngẫu nhiên 1900–2049, mọi giờ, giới tính, ngày biên | 0 lỗi bất biến: mỗi sao an đúng một lần, 12 cung, quan hệ sách của sao phụ thuộc (Quốc Ấn = Lộc Tồn+8 …), Tuần/Triệt hai cung kề nhau, 12 Tràng Sinh, đại hạn bước 10, đủ 14 chính tinh. Bắt lỗi lập trình, **không** chứng minh công thức đúng. |
| Thẩm tra nguồn | `docs/audit/tuvi-calc.md` (TV-1 … TV-9) + trang sách TH/KL | công thức mỗi sao mới có trang sách. |

Công cụ: `.venv/bin/python tools/compare_reference.py` (so từng cung, in khác biệt); thêm lá đối chiếu = thêm một file JSON cùng định dạng vào `engine/tests/reference_charts/` (test `test_reference_charts.py` tự chạy).

## Đã sửa / đã thêm

| Hạng mục | Công thức | Nguồn | Trạng thái |
|---|---|---|---|
| Quốc Ấn | Lộc Tồn + 8 | TH tr.22; KL tr.29 | PASS (khớp lá đối chiếu) |
| Đường Phù | Lộc Tồn + 5 | TH tr.22; KL tr.29 | PASS |
| Thai Phụ / Phong Cáo | Văn Khúc ± 2 | TH tr.19; KL tr.27 | PASS |
| Giải Thần | cùng cung Phượng Các | TH tr.20; KL tr.31 | PASS |
| Văn Tinh | theo can năm sinh | TH tr.26 (#39) | PASS |
| Thiên Trù | theo can năm sinh (sao thứ hai của "Lưu Hà – Thiên Trù") | TH tr.26 (#37) | PASS |
| Sao lưu (9 sao sách) | Thái Tuế, Tang Môn, Bạch Hổ, Khốc, Hư, Lộc Tồn, Kình, Đà, Mã | KL tr.41-42; TH tr.114 | PASS, trừ Kình/Đà (dưới) |
| Sao lưu thông lệ | Khôi, Việt, Văn Xương, Văn Khúc, Đào Hoa, Hồng Loan, Kiếp Sát, lưu Tứ Hóa | không có trong ba sách | hiển thị kèm gạch chấm "thông lệ, chưa đối chiếu sách"; **không** đưa vào luận giải |
| Nguyệt hạn (Th.N) | từ cung tiểu hạn năm xem đếm nghịch tới tháng sinh, từ đó lấy Tý đếm thuận tới giờ sinh = tháng Giêng | TH tr.115 | PASS; "năm Tiểu hạn" đọc là *cung tiểu hạn* (cách đọc còn lại — chi năm xem — cho tháng Giêng ở Tuất, không khớp bảng đối chiếu) |

Sao lưu và nguyệt hạn chỉ hiển thị trên bảng (tiền tố "L.", "Th.N"); không quy tắc luận giải nào đọc chúng.

## Bảng độ sáng (miếu/vượng/đắc/bình/hãm)

Ba bảng, chọn tường minh (`dignity_school` trên mọi API; ô chọn "Bảng độ sáng" trên bảng lá số; ghi nhớ trên máy):

| Bảng | Nguồn | Mặc định | Khớp lá đối chiếu (14 chính tinh) |
|---|---|---|---|
| `thuc_hanh` | Tử Vi Thực Hành, đối chiếu từng trang | **có** | 7/14 |
| `khao_luan` | Tử Vi Khảo Luận, bảng "Thế đứng" — chính là bảng các trang phổ thông (tuvi.vn) dùng | không | 12/14 (2 ô sách để trống: Tử Vi tại Dậu, Liêm Trinh tại Sửu — để trống, không chép từ ảnh) |
| `toan_thu` | Tử Vi Đẩu Số Toàn Thư | không | 7/14 |

Một lá số chỉ dùng một bảng: bảng lá số, `/api/facts`, `/api/interpret` và `/api/reasoning` nhận cùng `dignity_school`. Bộ quy tắc được viết theo Thực Hành, nên `/api/reasoning` trả `mixed_school_warning` khi chọn bảng khác. Test: `engine/tests/test_dignity_tables.py` (14 chính tinh × 12 cung × 3 bảng).

## Chưa làm được (BLOCKED, thiếu nguồn)

| Hạng mục | Lý do |
|---|---|
| Cân lượng (xưng cốt) | ba sách KL/TH/TT không in bảng cân xương; không tự tạo bảng |
| Lai nhân cung | không tìm thấy quy tắc trong ba sách (khớp "lai nhân" ở TT tr.24 là chữ trong bài phú, không phải quy tắc) |
| Lưu Kình/Đà cho âm nam / dương nữ | KL tr.42 đảo chiều (Kình lùi, Đà tiến); bảng tuvi.vn không đảo. Giữ theo sách, test ghi rõ khác biệt |
| Hai ô độ sáng Khảo Luận trống | sách không in |
| Lưu Hà các can Canh/Đinh/Tân | KL tr.29 và TH tr.26 khác nhau (audit TV-2); mã hiện theo một bên, cần chọn trường phái |
| Đối chiếu độc lập rộng hơn | mới có 1 lá; cần thêm lá đối chiếu (ảnh từ người dùng hoặc sách có lá mẫu) — không cào trang của bên thứ ba |
