# Trang chủ trên điện thoại: plan khắc phục (2026-11-06)

Nguồn: nhận xét của chủ dự án về màn hình di động, bốn điểm. Kiểm tra trên tuvithienban.com ở khung 375×812 (main 7ea528f4):
khung đầu có nút "Lập lá số" trên thanh đầu trang, nút "Lập lá số" lớn, nút "Xem lá số mẫu", khối "Trực tiếp" cao khoảng 100px,
ba cam kết bị đẩy xuống sát hai nút nổi ở đáy. Ở 375px hai nút nổi nằm hai góc (Góp ý trái, Bát Bát phải); ảnh của chủ dự án
cho thấy chúng chồng nhau ở góc phải, nên coi như lỗi có thật ở một số máy và sửa tận gốc: chỉ còn một nút nổi.

Chỉ đụng giao diện tĩnh (engine/web), không đụng engine, API hay luận giải.

## 1. Một nút nổi duy nhất

Hiện trạng: `feedback.js` dựng `.fb-fab` (góc trái dưới, z 58), `ask.js` dựng `.ask-fab` (góc phải dưới, z 59). Hai nút độc lập.

Sửa:
- Bỏ `.fb-fab` ở mọi cỡ màn hình. Nút Bát Bát là điểm chạm duy nhất.
- Đầu khung Bát Bát (`.ask-h`) thêm nút nhỏ "Góp ý". Bấm vào thì đóng khung Bát Bát và mở khung Góp ý.
  `feedback.js` xuất `openFeedback()` và nghe sự kiện `tb:feedback`, để không phụ thuộc thứ tự nạp script.
- Chấm báo "admin đã trả lời" (`.fb-dot`) chuyển lên nút Bát Bát. Bấm vào thì mở thẳng khung Góp ý.
- Thêm lối vào thứ hai không nổi: mục "Góp ý" ở chân trang và ở `side-foot` của thanh bên khi đã đăng nhập.
- Nút Bát Bát ẩn trên trang chủ khi khối `.hero-cta` hoặc nút `#submit-btn` đang hiện. Dùng IntersectionObserver và lớp
  `html.cta-in-view`, để nút nổi không che nút chính. `body` có `padding-bottom` bằng cỡ nút cộng `env(safe-area-inset-bottom)`,
  để dòng cuối trang không bị nút che.

Tệp: `engine/web/js/feedback.js`, `engine/web/css/feedback.css`, `engine/web/js/ask.js`, `engine/web/css/ask.css`,
`engine/web/js/app.js` (observer), chân trang trong `engine/tvbt/sitegen.py`/`sitenav.py`.

## 2. Một nút "Lập lá số" trong khung đầu

Hiện trạng: `.hdr-cta` trên thanh đầu trang luôn hiện. `.hero-cta` có nút lớn "Lập lá số" và nút viền "Xem lá số mẫu" cao bằng nhau.

Sửa:
- Chỉ trên trang chủ: `.hdr-cta` ẩn khi `.hero-cta` còn trong khung nhìn, hiện lại (mờ dần) khi đã cuộn qua.
  Dùng chung observer ở mục 1, bằng lớp `html.cta-in-view`. Các trang khác giữ nguyên.
- Trên ≤600px, "Xem lá số mẫu" thành liên kết chữ dưới nút chính ("hoặc xem một lá số mẫu →"), không còn là nút cao 48px.
  Từ đó chỉ còn một nút đỏ trong khung đầu.
- Không có JS hay trình duyệt không hỗ trợ IntersectionObserver: giữ như hiện nay (nút trên thanh vẫn hiện).

Tệp: `engine/web/index.html`, `engine/web/css/app.css`, `engine/web/js/app.js`.

## 3. Khối "Trực tiếp" thành một dòng, cam kết lên trên

Hiện trạng: `#live-stats` nằm ngay dưới nút chính, gồm thẻ "Trực tiếp" và hai ô số lớn. `.hero-facts` nằm dưới nó.

Sửa:
- Đổi thứ tự: `.hero-facts` (Có nguồn sách · Riêng tư · Tải PDF) đặt ngay dưới nút chính.
- `#live-stats` thành một dòng nhỏ đặt sau `.hero-facts`: "● 532+ lượt lập lá số · 123+ lượt đăng nhập", chữ 0,8rem,
  chiều cao cố định khoảng 24px, giữ sẵn chỗ để không làm trang nhảy khi số về.
  `live.js` giữ nguyên cách lấy số, chỉ đổi phần hiển thị (vẫn đếm lên, vẫn nháy khi tăng, tôn trọng giảm chuyển động).
- Đổi nhãn "Lượt quét" thành nhãn người đọc hiểu được. Cần xác nhận `/api/stats` đếm `scans` là gì trước khi đặt tên.
- Mục tiêu: ở 375×812, cả ba cam kết nằm trọn trong khung đầu, phía trên vùng nút nổi.

Tệp: `engine/web/index.html`, `engine/web/css/app.css` (khối `.live*` dòng 599–615), `engine/web/js/live.js`.

## 4. Bảng Khách và Thành viên gọn trên điện thoại

Hiện trạng: `.perks-t` có 12 hàng, 3 cột, nằm trong `.perks-scroll` cuộn ngang. Cột "Thành viên" có câu dài
(chat 30 ngày, giá xu).

Sửa, chỉ trên ≤600px (máy tính giữ nguyên bảng):
- Đầu khối là 4 thẻ tóm tắt khác biệt chính:
  1. Mọi luận giải đối chiếu sách: miễn phí, đọc trọn, cho cả khách.
  2. Tải PDF và ảnh lá số: ai cũng tải được.
  3. Thành viên: lưu lá số trên mọi máy, hỏi Bát Bát 2 câu mỗi ngày.
  4. Luận riêng ba mức: trả bằng xu.
- Bảng đầy đủ vào `<details class="perks-more">`, tiêu đề "Xem bảng so sánh chi tiết".
  Khi mở, mỗi hàng hiển thị thành một khối dọc: tên quyền lợi, rồi hai dòng "Khách: …" và "Thành viên: …".
  Nhãn lấy từ `data-k` trên `<td>`, hiện bằng `::before`. Không còn cuộn ngang.
- Nội dung bảng không đổi, nên giữ được một nguồn sự thật. Các thẻ tóm tắt viết tay trong `index.html`, cạnh bảng,
  để khi đổi giá chỉ sửa một chỗ.

Tệp: `engine/web/index.html`, `engine/web/css/app.css`.

## Thứ tự và kiểm tra

Một nhánh, một commit cho mỗi mục, theo thứ tự 1 → 2 → 3 → 4 (mục 1 và 2 dùng chung observer).
Sau đó chạy `.venv/bin/python tools/build_site.py` để cập nhật mã phiên bản tệp.

Kiểm tra trong trình duyệt, không viết thêm bộ test:
- Khung 320, 375, 414 và 1280px, cả khi chưa và đã đăng nhập.
- Ảnh chụp khung đầu ở 375px trước và sau.
- `document.documentElement.scrollWidth === innerWidth` ở mọi cỡ, tức không có cuộn ngang.
- Ở 375px, chỉ một nút đỏ và không nút nổi nào trong khung đầu. Ba cam kết nằm trọn trong khung.
- Mở và đóng Bát Bát, chuyển sang Góp ý, chấm báo trả lời hiện trên nút Bát Bát.
- Trang khác (chiem-tinh, kinh-dich, tài khoản) vẫn có nút Bát Bát và lối vào Góp ý.
- Không lỗi trong console.

Ước lượng: mục 1 khoảng nửa ngày, các mục 2, 3, 4 mỗi mục 1–2 giờ.

## Cần chủ dự án quyết

- Bỏ nút Góp ý nổi ở mọi cỡ màn hình (đề xuất), hay chỉ bỏ trên điện thoại?
- Khối "Trực tiếp": giữ một dòng nhỏ trong khung đầu (đề xuất), hay chuyển hẳn xuống cuối trang?
