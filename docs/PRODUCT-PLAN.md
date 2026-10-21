# Thiên Bàn — kế hoạch thành website chuyên nghiệp (2026-10-21)

Tham khảo: ảnh chụp trang Altuvi do người dùng gửi (biểu đồ vận, bảng giá miễn phí / chuyên sâu, xem ngày, VNPAY, ví xu, hồ sơ, FAQ, chân trang doanh nghiệp). Làm **tính năng tương đương bằng thiết kế và lời văn của Thiên Bàn**, không sao chép thương hiệu, câu chữ hay giao diện của họ.

Nguyên tắc giữ nguyên: mọi con số và nhận định phải lần ra được dữ liệu lá số và quy tắc có nguồn; không quảng cáo "chính xác", "khoa học" (Tử Vi chưa được khoa học xác nhận là phương pháp dự báo); phần nào chưa có nguồn thì ghi rõ hoặc không làm.

## Hiện trạng (đã có)

Lập lá số Tử Vi + Bát Tự, bảng lá số truyền thống (zoom/kéo), sao lưu, nguyệt hạn, ba bảng độ sáng, luận giải 14 chương + gợi ý hành động, reasoner chương Mệnh, đăng nhập Google, lưu lá số, ví xu + Stripe Checkout, chat về lá số, đếm lượt dùng (đang làm: trang quản trị, góp ý trực tiếp).

## Giai đoạn 1 — Sản phẩm cốt lõi (2–3 tuần)

| # | Hạng mục | Nội dung | Ghi chú trung thực |
|---|---|---|---|
| 1.1 | Biểu đồ xu hướng đại vận | cột theo 10 chặng đại vận: hai lớp "Thuận lợi" / "Thử thách", đánh dấu chặng hiện tại | **Chỉ số hệ thống**: tổng hợp có trọng số các nhận định đã đối chiếu sách bắn vào cung đại vận và tam phương của nó (hỗ trợ vs hạn chế, theo tầng của reasoner). Ghi rõ "chỉ số tổng hợp từ quy tắc, không phải xác suất" và có nút xem căn cứ từng chặng |
| 1.2 | Biểu đồ tiểu vận (từng năm) | đường theo năm trong khoảng ±10 năm, mốc "Năm nay" | cùng cách tính, trên cung tiểu hạn + lưu Thái Tuế + lưu Tứ Hóa (lưu Tứ Hóa là thông lệ → trọng số thấp, ghi chú) |
| 1.3 | Biểu đồ năng lực 12 cung (radar) | mỗi cung một điểm | điểm = cân bằng nhận định hỗ trợ/hạn chế của cung đó (đã có trong reasoner: seat, tầng, độ hiếm) |
| 1.4 | Nguyệt vận (12 tháng của năm) | cột theo tháng, từ nguyệt hạn TH tr.115 | chỉ dùng vị trí tháng đã kiểm; không làm "nhật vận" theo ngày cho đến khi có nguồn |
| 1.5 | Trang "Tổng quan lá số" | tóm tắt 1 màn hình: cách cục chính, 3 luận điểm, 4 biểu đồ, nút đọc từng chương | dùng ReadingPlan của reasoner |
| 1.6 | Mở rộng reasoner | Quan Lộc, Tài Bạch, rồi các cung còn lại, liên cung Mệnh–Tài–Quan–Di | việc P3 đang dở |

## Giai đoạn 2 — Thương mại hóa (2 tuần, cần người dùng làm phần pháp lý)

| # | Hạng mục | Nội dung | Ai làm |
|---|---|---|---|
| 2.1 | Bảng so sánh gói | Miễn phí (lá số, tổng quan, biểu đồ) vs Chuyên sâu (12 cung chi tiết, đại/tiểu/nguyệt vận, lời khuyên theo mốc) | tôi |
| 2.2 | Gói & giá | gói lẻ theo chương, gói vận hạn, gói toàn bộ; mã giảm giá; VAT | tôi làm cơ chế; **giá do bạn quyết** |
| 2.3 | Ví xu | nạp xu, gift code, lịch sử dùng, mở khóa nội dung bằng xu | phần lớn đã có; thêm gift code + lịch sử chi tiết |
| 2.4 | Cổng VNPAY | QR ngân hàng, thẻ nội địa, thẻ quốc tế, cạnh Stripe | **bạn**: đăng ký merchant VNPAY (cần pháp nhân), gửi khóa; tôi tích hợp + sandbox |
| 2.5 | Hóa đơn, hoàn tiền | email biên nhận, chính sách hoàn tiền khi lỗi | tôi soạn mẫu; bạn duyệt nội dung pháp lý |
| 2.6 | Paywall | khóa phần chuyên sâu, xem trước 1–2 đoạn | tôi |

## Giai đoạn 3 — Tài khoản & cá nhân hóa (1 tuần)

- Trang hồ sơ: họ tên, giới tính, ngày giờ sinh (dương/âm), tình trạng nghề nghiệp, tình trạng quan hệ → luận giải nhấn vào điều người dùng quan tâm.
- "Lá số của tôi": nhiều lá số (gia đình, bạn bè), so sánh hai lá số (đã có compare).
- Ẩn thông tin sinh khi chia sẻ; liên kết chia sẻ lá số; tải PDF/ảnh bảng lá số.

## Giai đoạn 4 — Nội dung & tăng trưởng (liên tục)

| # | Hạng mục | Ghi chú |
|---|---|---|
| 4.1 | Trang giới thiệu "Cách Thiên Bàn luận giải" | mô tả thật: quy tắc từ sách có trang, reasoner, không dùng AI để bịa nhận định; khác với lời quảng cáo "cơ sở khoa học" |
| 4.2 | FAQ | không biết Tử Vi có xem được không, miễn phí gì, độ tin cậy, quên giờ sinh (đã có chế độ không giờ), sửa ngày sinh, bảo mật dữ liệu |
| 4.3 | Blog / bài viết SEO | ý nghĩa từng sao, cung, cách cục — viết từ dữ liệu sách đã có (glossary, KL/TH), mỗi bài có nguồn |
| 4.4 | Chatbot | đã có chat theo lá số; giới hạn theo xu |
| 4.5 | Affiliate / giới thiệu bạn | mã giới thiệu, thưởng xu |
| 4.6 | Xem ngày tốt xấu | lịch tháng, ngày hoàng đạo/hắc đạo, tiết khí, can chi ngày/tháng, xung khắc với tuổi | **BLOCKED một phần**: lịch âm, can chi, tiết khí đã tính được; hoàng đạo/hắc đạo, sao ngày, điểm "cát hung %" cần sách (Ngọc Hạp Thông Thư, Hiệp Kỷ Biện Phương Thư) — chưa có trong kho; không tự đặt điểm % |
| 4.7 | Ứng dụng di động | PWA trước (cài từ trình duyệt); app store sau |

## Giai đoạn 5 — Vận hành & tin cậy

- Chân trang doanh nghiệp: tên công ty, MST, địa chỉ, hotline, email hỗ trợ, mạng xã hội, chính sách thanh toán / bảo mật / điều khoản / hướng dẫn thanh toán. **Bạn cung cấp thông tin pháp nhân.**
- **Thông báo website TMĐT với Bộ Công Thương** (bắt buộc khi bán hàng online ở VN) — bạn làm, tôi chuẩn bị trang chính sách.
- Trang quản trị (đang làm): doanh thu, người dùng, lượt lập lá số, góp ý; nhật ký lỗi; sao lưu D1.
- Hiệu năng & đo lường: Core Web Vitals, analytics tôn trọng riêng tư, giám sát Worker.
- Bảo mật: giới hạn tần suất API, chống lạm dụng xu, kiểm thử thanh toán.

## Thứ tự đề xuất

1. Giai đoạn 1 (biểu đồ + tổng quan + reasoner) — đây là giá trị cốt lõi, làm được ngay.
2. Song song: bạn lo pháp nhân, VNPAY merchant, thông báo Bộ Công Thương, quyết định giá.
3. Giai đoạn 2 khi có khóa VNPAY; giai đoạn 3; rồi 4–5.

## Cần bạn quyết / cung cấp

- Giá từng gói và nội dung miễn phí vs trả phí.
- Pháp nhân, MST, địa chỉ, hotline cho chân trang và VNPAY.
- Có làm "Xem ngày" khi chưa có sách nguồn không (chỉ phần lịch âm/can chi/tiết khí), hay chờ sách.
- Cách đặt tên chỉ số trên biểu đồ (đề xuất: "Mức thuận lợi" / "Mức thử thách" kèm chú thích "chỉ số tổng hợp từ quy tắc sách").
