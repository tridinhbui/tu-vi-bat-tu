# Phase 5 — xác minh nguồn (báo cáo)

Nhánh `phase5-sources` (xếp chồng trên `phase4-audit` / PR #2), chưa push, chưa PR. Không đổi định nghĩa cách cục nào, không thêm luật, không đổi thuật toán production, không nâng trạng thái nào. Bảng đối chiếu chi tiết: [PHASE5_BANG_DOI_CHIEU.md](PHASE5_BANG_DOI_CHIEU.md); dữ liệu: `engine/data/experimental/source_readings_phase5.json`.

## 1. Cách đọc và phân loại nguồn

| Loại | Tài liệu | Cách đọc trong phiên này |
|---|---|---|
| Cổ thư (sơ cấp) | 紫微斗數全書 | **một bản web** (zh.wikisource.org) qua công cụ tóm tắt, hai lần lấy khớp nhau; không tìm được bản thứ hai (tìm web không ra); chưa đối chiếu bản in |
| Bản dịch + chú giải | Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục) | PDF của người dùng, lớp chữ mã VNI giải mã, đọc trực tiếp |
| Sách Việt | Tử Vi Khảo Luận; Tử Vi Thực Hành | PDF của người dùng; TH p.21, p.43 đọc cả ảnh trang vì lớp chữ vỡ |
| Registry nội bộ | `pack_*.json` | không phải bằng chứng độc lập |

Ba cuốn sách Việt còn bản quyền nên báo cáo chỉ **diễn giải sát nghĩa kèm số trang**; chỉ các câu Hán văn cổ được chép nguyên văn. Người dùng có thể mở đúng trang ghi trong bảng để đối chiếu.

## 2. Trạng thái PR và regression

- **PR #2** (`phase4-audit`): https://github.com/tridinhbui/tu-vi-bat-tu/pull/2, mở, **chưa merge**, `MERGEABLE`. Một check đỏ: `Workers Builds: tu-vi-bat-tu` (Cloudflare). PR #1 (nhánh khác) cũng đỏ cùng check; diff của PR #2 không chạm `Dockerfile`, `wrangler`, `src/` hay file production. Tôi không đọc được log Cloudflare (cần đăng nhập), nên **nguyên nhân chưa xác định**; không dùng Auto-fix.
- Diff của PR #2: 12 file, toàn bộ là doc/test/dữ liệu/công cụ audit; mã chỉ ở `phi_hoa/{tables,graph}.py` và `phi_hoa_api.py` (module thử nghiệm). Không có consumer nào của `/api/phi-hoa` cũ (đã tìm toàn repo, Worker chỉ proxy).
- Regression (không loại test nào):
  - `main` `89565d5` sạch: 1008 passed, 1 skipped, 2 xfailed.
  - `phase4-audit` rebase trên `main`: 1213 passed, 1 skipped, 2 xfailed, 0 failed (có thêm test kiểm kê route: route `/api` mới phải được xếp loại mặc định hay thử nghiệm).
  - `phase5-sources`: 1220 passed, 1 skipped, 2 xfailed, 0 failed.
- API mặc định: 16 lời gọi trên 13 endpoint không chứa vật liệu thử nghiệm; bật `experimental` chỉ thêm khóa riêng.

## 3. Mã đầu đới kiếm

Đọc 13 đoạn (KL pp.60, 64 ×4, 200; TT pp.50, 142; TH p.157; 全書 太微賦, 定貴局 chú, 卷三 ×2). **Không có định nghĩa chung.**

| Nguồn | Định nghĩa | Hệ quả với bản nháp v2 |
|---|---|---|
| KL p.64 mục 5-6 | Mệnh ở Ngọ + Kình Dương. Xấu nếu Thất Sát **và** Thiên Hình đồng cung; tốt nếu tránh hai sao đó và gặp Khoa Quyền Lộc | lõi khớp; breaker của nháp lỏng hơn (Thất Sát trong tam phương) và bỏ Thiên Hình |
| KL p.200 | Ngọ + Kình + Thiên Mã + Tham Lang, phát võ nhưng không bền | nháp không dùng Thiên Mã, Tham Lang |
| TT p.142 | Kình gặp Thiên Mã; hay ở tứ mộ, **xấu ở Ngọ** | ngược lõi (vị trí) và cần Thiên Mã |
| 全書 chú 定貴局 | "Mã có nhận", **không phải cách cư Ngọ** | ngược lõi |
| 全書 卷三 | Kình ở Tý/Ngọ/Mão/Dậu; "cát nhiều thì khỏi luận" | lõi rộng hơn (bốn cung) |
| KL p.64 mục 3, TT p.50 | Kình ở Tý Ngọ Mão Dậu nói chung xấu; TT p.50 tự nhận có hai chiều | bản thân tài liệu mâu thuẫn |

Phase 4 chưa thấy điều này (chỉ có chú giải 定貴局). **Kết luận:** không thể máy hóa một định nghĩa duy nhất mà không chọn trường phái. Theo quy tắc của bạn tôi không sửa bản nháp; mỗi cách đọc nên là một biến thể có gắn nguồn (phiên UI đang làm lớp biến thể riêng).

## 4. Thạch trung ẩn ngọc

Đọc 11 đoạn (KL pp.44, 57-58, 66, 106, 203, 223; TT p.34; TH p.43 đọc ảnh; 全書 卷一 ×2, 卷三).

- **Lõi** Cự Môn ở Tý/Ngọ: mọi nguồn đồng ý. TT p.34 còn ghi Cự Môn **vượng** ở Tý/Ngọ, nên phản chứng "Cự Môn hãm" của bản nháp không bao giờ kích hoạt.
- **Điều kiện thành** khác nhau: Khoa+Quyền+Lộc (KL p.58, 223, TT p.34, 全書 卷三); chỉ Khoa+Lộc (全書 卷一); **Tuần/Triệt hoặc Hóa Lộc, Lộc Tồn làm chìm** (TH p.43); **Tuần/Triệt** (KL p.106); Song Hao (KL p.106, 203); Thiên Cơ ở Thiên Di (KL p.44).
- **Mâu thuẫn trực tiếp với bản nháp:** TH p.43 và KL p.106 coi Tuần/Triệt là điều kiện thành; bản nháp dùng Tuần/Triệt làm phản chứng.
- **Breaker** (Kỵ hoặc Kình đồng cung) lấy từ KL p.66 cho Tam Hóa hội. Trang in nói "đồng cung **hoặc chiếu**"; registry ghi hẹp hơn trang sách.
- 全書 卷三 thêm điều kiện năm sinh (Tân, Quý thượng cách; Đinh, Kỷ thứ hai) mà bản nháp không có.

## 5. Bảng Tứ Hóa theo can: một phát hiện ảnh hưởng cả production

Đọc ảnh TH p.21 và KL pp.196-197: **hai sách khác nhau ở Hóa Khoa của can Nhâm**, TH ghi Thiên Phủ, KL ghi Tả Phụ. zh.wikipedia (nguồn tổng hợp) cho thấy cùng điểm bất đồng giữa hai bản 全集 và 全書, và thêm một khác biệt thứ tự Khoa/Kỵ ở Canh (hai sách Việt đều theo dạng 全書 ở Canh). Bảng trong code theo KL ở Nhâm và theo dạng 全書 ở Canh. Ghi chú trong `tuvi.py` đã nêu "Thực Hành prints 'Phủ'" nhưng câu mở đầu lại viết "agree on all ten stems".

Đây là bảng của **lá số Tử Vi production** (Tứ Hóa năm Nhâm: 1952, 1962, 1972, 1982, 1992, 2002...) và của Phi Hóa thử nghiệm. Tôi **không đổi**; đề xuất quyết định riêng: gắn nhãn trường phái (KL / TH) cho lá số can Nhâm và sửa câu "agree on all ten stems" cho đúng.

## 6. Phi Hóa

- **Tìm tài liệu Phi Tinh có bảng Tứ Hóa riêng và công thức phi cung:** hai truy vấn web (Hán và Việt), ba trang đã mở. Không có trang nào có bảng mười can theo Phi Tinh kèm công thức; một trang bị chặn (403); hai bài phổ thông không dẫn tác giả hay sách. zh.wikipedia (nguồn tổng hợp) mô tả hệ Phi Tinh lấy "cung can phi hóa" làm gốc nhưng bảng nó đưa là bảng theo **can năm sinh**, không phải bảng riêng cho cung can.
- Bằng chứng yếu (phổ thông/tổng hợp, không có tên sách) cho thấy Phi Hóa dùng **cùng bảng mười can** áp lên can cung (ngũ hổ độn) — đúng cách đồ thị đang dựng, nhưng **chưa xác minh từ một văn bản Phi Tinh**.
- **Không thêm bảng nào.** Bảng đang dùng vẫn mang nhãn `school: tam_hop`, `reused_unverified_for_phi_tinh`.

## 7. Mức xác minh từng module

Thang: **L0** experimental/draft · **L1** source-aligned (mỗi thành phần có trang đã đọc, không xung đột chưa giải) · **L2** source-verified (mọi thành phần đọc trực tiếp ở nguồn sơ cấp hoặc dịch + một nguồn độc lập thứ hai, ví dụ trong sách làm golden test).

| Module | Mức | Verified facts | Còn thiếu / xung đột |
|---|---|---|---|
| 10 cách cục | L0 | máy trạng thái đúng (test, oracle độc lập, vét cạn) | Mã đầu đới kiếm, Thạch trung ẩn ngọc: nhiều định nghĩa xung đột giữa nguồn, và bản nháp trái hai trang; 8 cách còn lại chưa đọc lại trực tiếp |
| Phi Hóa: đồ thị 48 cạnh | tính toán đã kiểm (oracle 180 lá số) | hình học và dữ liệu đúng theo bảng đã chọn | bảng chưa xác minh cho Phi Tinh; sách Việt bất đồng ở Nhâm |
| Phi Hóa: 10 luật | L0 | không | tài liệu Phi Tinh có trang |
| Lưu tinh + 13 luật tầng thời gian | L0 | bảng nguyên cục đã đọc (TH pp.19-24) | không có nguồn cho phép an lưu theo năm |
| Bảng Tứ Hóa (production) | đã đọc trực tiếp | 8/10 can hai sách trùng nhau | Nhâm-Khoa: TH ≠ KL |

## 8. Điều kiện chuyển từ experimental sang source-verified

1. Mỗi thành phần có đoạn đã đọc (số trang), lưu trong `source_readings`, và **không còn xung đột chưa giải**: với cách có nhiều định nghĩa, tách thành biến thể theo nguồn (mỗi biến thể một trường phái) thay vì một định nghĩa trộn.
2. Ít nhất một lá số mẫu trong chính sách làm golden test; có oracle độc lập.
3. Phản chứng/cứu giải chỉ giữ khi một trang nói rõ vai trò đó (hiện Tuần/Triệt bị hai trang nói ngược).
4. Phi Hóa: một tài liệu Phi Tinh cụ thể (tên, tác giả, trang) cho bảng mười can và công thức phi cung; đối chiếu 48 cạnh với một lá số trong tài liệu đó.
5. Lưu tinh: một trang nói rõ phép an lưu theo can/chi năm bằng đúng các bảng nguyên cục.
6. Cuối cùng người dùng duyệt từng bước chuyển; không tự động.

## 9. Đính chính Phase 4 (đã ghi trong bảng đối chiếu)

(a) xung đột Khoa+Quyền+Lộc / Khoa+Lộc nằm bên trong 全書 (卷一 so với 卷三), không phải giữa sách Việt và cổ thư; (b) KL p.66 là "đồng cung hoặc chiếu"; (c) Tuần/Triệt là điều kiện thành ở TH p.43 và KL p.106; (d) "hai sách đồng thuận mười can" không đúng ở Nhâm.
