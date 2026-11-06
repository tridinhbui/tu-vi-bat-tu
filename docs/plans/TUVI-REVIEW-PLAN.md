# Màn hình lá số Tử Vi: plan theo hai bản nhận xét (2026-11-06)

Nguồn: hai bản nhận xét của chủ dự án. Bản thứ nhất nói về lời luận giải, cách tương tác và giao diện. Bản thứ hai đi sâu vào nội dung luận giải.

Kiểm tra trên tuvithienban.com, main 158c0336, lá số mẫu 17/05/1990 10:30 nam, khung 375×812.

Hai kế hoạch đã có trên main phủ phần lớn các điểm này:
- `docs/plans/TUVI-ENHANCE-PLAN.md`, gọi tắt **EP**, phần nội dung;
- `docs/plans/LANDING-MOBILE-PLAN.md`, gọi tắt **LM**, phần nút nổi.

Tệp này chỉ thêm những gì hai kế hoạch kia chưa có, và ghi rõ điểm nào đã làm rồi để không làm lại.

## 1. Đối chiếu từng điểm với trang thật

| Điểm nhận xét | Trên trang hiện nay | Xử lý |
|---|---|---|
| Thanh tab "Tổng quan · 12 Cung · Đại vận · Lưu niên · Hỏi đáp Bát Bát" | Không có thanh này. Tab là Tổng quan · Tử Vi · Bát Tự (· Trưởng thành). Đại hạn & lưu niên là chương 08. | Không làm gì |
| Bảng 12 cung bé trên điện thoại, cần dạng danh sách | Đã có: ở 375px bảng mặc định là "Sổ tay" (danh sách 12 cung), nút "Toàn lá số" để xem bàn cờ. Trang không cuộn ngang (scrollWidth 375). | Không làm gì |
| Màu sao theo ngũ hành | Đã có trên bảng truyền thống và trong lời luận (`.pr-star`, 742 tên sao tô màu trên lá mẫu, `stars_hanh.js`). Màu phụ tinh là quy ước chung, chưa đối trang sách (ghi trong `stars_hanh.js`). | Thêm chú giải màu (mục 4.6) |
| Thiếu in đậm từ khóa | Mỗi đoạn có phần mở đầu in đậm, chính tinh in đậm (354 thẻ in đậm). Câu kết luận thì không nổi lên. | Mục 4.1 |
| Khối chữ dày | **Đúng.** Trên 102 đoạn: trung vị 70 chữ (khoảng 9 dòng ở 375px), 34 đoạn quá 80 chữ, dài nhất 226 chữ (27 dòng). | Mục 4.1 |
| Không biết cung nào đã đọc | **Đúng.** Không có dấu đã đọc. | Mục 4.2 |
| Hết lượt hỏi mới báo nạp xu | Một phần. Số câu miễn phí và số xu chỉ hiện ở đầu khung chat sau khi mở, khách thì không thấy gì. | Mục 4.3 |
| Hai nút nổi chồng nhau | Có thật trên một số máy. | Đã có trong LM mục 1, không làm lại |
| Nút chia sẻ, tải ảnh, PDF chưa nổi | Các nút này nằm ở đầu trang. Ở 375px chúng xuống hai dòng, kèm một ô tích. Cuối bản luận không có nút nào. | Mục 4.4 |
| Ghép từ điển, thiếu sự chuyển hóa khi sao đan xen | Đúng một phần. Lời luận đã nói xung chiếu, nhị hợp, Tuần án ngữ và "cân hai bên". Nhưng thân đoạn vẫn là chuỗi "Thêm vào đó, vì sao X… Ngược lại, sao Y…" mỗi sao một câu. Lại có lỗi: câu "xác nhận" đi ngược chiều (mục 2). | Mục 2, mục 3.1, EP giai đoạn 2 và 4 |
| Câu khuyên chung chung (Barnum) | Đúng. Ví dụ "kiên nhẫn với chuyện tình cảm", "xây nền vững trước khi vươn cao". | Mục 3.4 |
| Không phân tầng sao | Đúng. Linh Tinh và Long Trì có câu riêng dài ngang chính tinh. | Mục 3.1 |
| Cung là ốc đảo, thiếu tam hợp Mệnh – Tài – Quan | Đúng một phần. Quan Lộc có câu "trong thế hội với Thiên Phủ ở cung Mệnh", nhưng không có câu nào trả lời "Mệnh đẩy hay kéo lùi công danh". | Mục 3.2 |
| Đại vận không nói nên bung hay thủ | Đúng. Mỗi hạn có mức (thuận, trung bình…) nhưng không có tư thế. | Mục 3.3 |

## 2. Lỗi phải sửa trước: câu "xác nhận" đi ngược chiều

Trên lá mẫu có hai chỗ, đều từ khung `corroborated` trong `src/interpret/content/prose/reasoning_frames.json`:

1. Chương Công danh: "…kéo theo chiều ngược lại: gặp thời vận tốt. **Mệnh xác nhận thêm điều đó**, vì Thiên Phủ kỵ nhất gặp Tuần, Triệt hoặc Thiên, Địa Không: cùng khổ, chỉ tu hành mới yên thân."
   - Câu sách xấu được đưa ra như lời xác nhận cho một nhận định tốt.
   - Trên lá này cung Mệnh có vẻ không có Tuần, Triệt hay Không Kiếp, nên điều kiện "kỵ gặp" có lẽ chưa xảy ra. Phải kiểm lại bằng dữ liệu lá số.
2. Chương Mệnh: "…kiếm được tiền, song không dư dả như mong. **Nhìn sang Tài Bạch**, Lộc Tồn ở Tài Bạch **cũng cùng chiều ấy**: vàng ngọc đầy nhà."
   - Hai vế ngược nhau, nhưng câu nói là cùng chiều.

Sửa:
- Câu `corroborated` chỉ được dùng khi câu chứng có cùng chiều (polarity) với câu được chứng.
- Câu sách mang điều kiện ("kỵ gặp X") chỉ được nói khi X có mặt.
- Câu ngược chiều thì chuyển sang khung `countered`, hoặc bỏ.

Tệp sửa: chỗ tạo bước `corroborated:` trong `src/interpret/prose/luan.ts` và `src/interpret/reason/`. Lần ra hàm chính xác khi làm.

Test: trên benchmark20 và 300 lá của `eval_deep3`, không câu `corroborated` nào có chiều khác câu nó chứng. Thêm vào `readable.test.ts`.

Đề xuất nhập việc này vào EP giai đoạn 0.

## 3. Nội dung: phần EP chưa có

EP đã có các việc sau, ở đây không lặp lại:
- cặp chính tinh đồng cung và Tứ Hóa bị bỏ sót (giai đoạn 2);
- bộ sao, cách cục theo vị trí (giai đoạn 4);
- vận hạn gọn, mỗi đại hạn có điểm chính (giai đoạn 5);
- văn phong, câu lặp (giai đoạn 6).

### 3.1 Ba tầng trong mỗi chương cung

Hiện nay mọi sao đều được viết thành câu dài ngang nhau. Đổi thành ba tầng:

1. **Cốt lõi.** Chính tinh với độ sáng, cùng Tứ Hóa, Tuần, Triệt trong cung. Đoạn đầu phải nói được sự chuyển hóa: chính tinh hãm mà gặp Hóa, Tuần, Triệt thì chiều đổi ra sao. Chỉ nói khi có câu sách cho tổ hợp ấy. Nếu không có, nói hai sao riêng và ghi "sách không bàn chung".
2. **Bộ kích hoạt.** Các cặp lục cát, lục sát (Xương Khúc, Khôi Việt, Tả Hữu, Kình Đà, Hỏa Linh, Không Kiếp) và Lộc Mã. Mỗi cặp một câu, nói nó đẩy cốt lõi theo chiều nào.
3. **Sao nhỏ.** Gom vào một dòng cuối đoạn, ví dụ "Sao nhỏ: Long Trì (hòa hợp), Linh Tinh (chi li)…". Không viết đoạn riêng. Câu đầy đủ chuyển vào Đọc sâu.

Tầng của mỗi sao lấy từ chính trọng số đang dùng để cân (`domains.json → weigh`, `reason/tiers.ts`), không đặt bảng mới.

Tệp sửa: `src/interpret/prose/luan.ts` (thứ tự và gom câu), `src/interpret/reason/tiers.ts`, `src/interpret/content/prose/luan.json` (khung dòng sao nhỏ).

Cổng kiểm tra:
- tầng 3 không quá 1 câu mỗi chương ở phần chính;
- câu đầu phần luận nhắc tên cốt lõi trên 100 % lá số;
- chỉ số Barnum và strip không xấu hơn số gốc.

### 3.2 Câu nối tam hợp trong Công danh và Tài Bạch

Thêm một câu ngay sau đoạn đầu của Quan Lộc và Tài Bạch. Câu này trả lời: tố chất ở Mệnh đẩy hay kéo lùi lĩnh vực này.
- Lấy từ hai kết luận đã có trong bảng kết luận (`reason/ledger.ts`): kết luận Mệnh về mặt liên quan, và kết luận của cung này.
- Bốn trường hợp:
  - cùng thuận: Mệnh đẩy thêm;
  - Mệnh thuận, cung nghịch: Mệnh gỡ được một phần;
  - Mệnh nghịch, cung thuận: có đất nhưng thiếu người;
  - cùng nghịch: cần dựa vào đại hạn tốt.
  Mỗi trường hợp nêu sao cụ thể của hai bên.
- Đây là câu tổng hợp, nên gắn nhãn `tong_hop` theo quyết định Review-19. Không thêm câu sách mới.

Tệp sửa: `src/interpret/prose/luan.ts`, `src/interpret/reason/ledger.ts`, khung câu trong `luan.json`.

Cổng kiểm tra: câu này có trên mọi lá số, nêu tên ít nhất một sao ở mỗi bên, và không ngược chiều với bảng kết luận.

### 3.3 Tư thế của mỗi đại hạn và năm: mở rộng, giữ, hay phòng thủ

Mỗi đại hạn, và năm hiện tại cùng hai năm tới, thêm một dòng tư thế. Dòng này ghép hai thứ đã tính sẵn:
- **gốc**: độ mạnh của cung được đại hạn kích hoạt, theo bảng kết luận;
- **thời**: mức của chặng trong `indices.ts`.

| Gốc \ Thời | Thuận | Nghịch |
|---|---|---|
| Mạnh | Mở rộng | Giữ, chờ |
| Yếu | Thử nhỏ, có giới hạn | Phòng thủ |

Mỗi dòng nêu lý do bằng sao và cung, ví dụ "Hóa Lộc của hạn vào Tài Bạch, bản cung có Vũ Khúc vượng".

Bảng hai chiều này là **quy ước hệ thống**, không có trang sách. Phải gắn nhãn như các quy ước khác, và cần chủ dự án duyệt (mục 6). Nếu tìm được câu sách về Mệnh – hạn thì thay bảng bằng câu sách.

Tệp sửa: `src/interpret/prose/vanhan.ts`, `src/interpret/prose/course.ts`, `src/interpret/indices.ts`.

Làm cùng EP giai đoạn 5, vì giai đoạn này cũng rút mỗi đại hạn về "mức chung, có lý do".

### 3.4 Câu khuyên phải riêng cho lá số

Câu "Gợi ý…" hiện chỉ lấy từ tên khái niệm, nên lá nào có "trắc trở tình cảm" cũng nhận cùng một câu.

Sửa:
- Câu khuyên nêu nguồn cụ thể (sao, cung, chặng tuổi). Ví dụ: "Phá Quân ở Phu Thê thì lúc đầu trắc trở, về sau mới nên: đừng chốt chuyện lớn trước chặng 36–45".
- Mốc tuổi lấy từ đại hạn đã tính.
- Khung câu nào không có chi tiết riêng của lá số để điền thì bỏ câu khuyên, không nói chung chung.
- Đo bằng `eval_repeat`: câu khuyên trùng nguyên văn trên hơn 5 % lá số bị coi là Barnum.

Tệp sửa: khung "gợi ý" trong `luan.json` và chỗ chọn khung trong `luan.ts`.

Cổng kiểm tra: không câu khuyên nào trùng nguyên văn trên hơn 5 % của 300 lá.

## 4. Giao diện và luồng đọc

Chỉ đụng `engine/web`, không đổi engine hay API.

### 4.1 Cắt khối chữ, thêm tóm tắt đầu chương

- Mỗi bước suy luận (trace.step) là một đoạn riêng, thay vì nối nhiều bước thành một `<p>`. Đoạn quá 60 chữ thì tách ở ranh giới câu.
- Đầu mỗi chương cung có 2–3 dòng "Tóm lại". Lấy nguyên các kết luận của bảng kết luận cho chương đó, có dấu chiều (thuận, nghịch, hai mặt).
- Mệnh đề kết luận trong câu (phần sau dấu ":" hoặc "nên") được in đậm nhẹ, để mắt quét được. Chỉ in đậm phần kết luận, không in đậm tên sao vì tên sao đã có màu.

Tệp sửa: `src/interpret/prose/realize.ts` (ranh giới đoạn), `engine/web/js/report.js`, `engine/web/css/app.css`.

Cổng kiểm tra: ở 375px, không đoạn nào quá 80 chữ, trung vị không quá 45 chữ (hiện 70). Bản in PDF vẫn giữ đủ nội dung.

### 4.2 Dấu đã đọc

- Mỗi chương và mỗi cung trong "Sổ tay" có dấu đã đọc. Một chương được tính là đã đọc khi đã ở trong khung nhìn ít nhất 4 giây (IntersectionObserver).
- Lưu trong `localStorage`, theo dấu vân tay lá số, bọc try/catch.
- Mục lục chương ghi "Đã đọc 4/11". Các chương Mệnh, Thân, Quan Lộc, Tài Bạch chưa đọc thì có chấm nhắc.

Tệp sửa: `engine/web/js/report.js`, `engine/web/js/atlas.js`, `engine/web/css/atlas.css`.

### 4.3 Số câu hỏi còn lại hiện trước khi gõ

- Thành viên: chip "2 câu miễn phí hôm nay · N xu" hiện ngay trên ô nhập.
  - Khi còn 0 câu miễn phí, chip đổi thành "Câu tiếp theo: N xu".
  - Không còn hộp nạp xu bật ra đột ngột.
- Khách: một dòng "Đăng nhập để hỏi 2 câu mỗi ngày". Ô nhập vẫn hiện.
- LM mục 1 cũng sửa `ask.js` (gộp nút Góp ý, chấm báo), nên làm mục này sau LM mục 1.

Tệp sửa: `engine/web/js/ask.js`, `engine/web/css/ask.css`.

### 4.4 Thẻ cuối bản luận và hàng nút gọn trên điện thoại

- Sau chương cuối, thêm một thẻ "Giữ lại lá số này", gồm: Lưu lá số, Tải ảnh, Tải PDF, Chia sẻ (thành viên).
  - Dùng lại các hàm của nút đầu trang. Không thêm hàm mới.
- Ở ≤600px, hàng nút đầu trang thu thành: "Tải PDF" và một nút "…" mở ra các mục còn lại.
  - Ô "Ẩn ngày giờ sinh khi tải" vào trong menu đó.

Tệp sửa: `engine/web/index.html`, `engine/web/js/app.js`, `engine/web/css/app.css`.

### 4.5 Nút nổi

Làm theo LM mục 1. Không thêm việc ở đây.

### 4.6 Chú giải màu ngũ hành

- Thêm một dòng chú giải "Kim · Mộc · Thủy · Hỏa · Thổ" dưới bảng lá số và ở đầu phần luận, dùng đúng màu `--k-*`.
- Kèm lời ghi: màu phụ tinh là quy ước bảng thường dùng.
- Không đổi màu nào.

Tệp sửa: `engine/web/js/tuvi.js`, `engine/web/css/atlas.css`.

## 5. Thứ tự

```
Mục 2 (lỗi xác nhận ngược chiều) ─► Mục 3.1 ─► Mục 3.2 ─► Mục 3.4
                                       Mục 3.3 đi cùng EP giai đoạn 5
Mục 4.1, 4.2, 4.4, 4.6 song song với mục 3 (chỉ đụng engine/web, trừ realize.ts ở mục 4.1)
LM mục 1 ─► Mục 4.3
```

- Mục 2 khoảng nửa ngày.
- Mục 3.1 khoảng 2 ngày; các mục 3.2, 3.3, 3.4 mỗi mục khoảng 1 ngày.
- Mục 4.1 khoảng 1 ngày; các mục 4.2, 4.3, 4.4, 4.6 mỗi mục 2–4 giờ.

Kiểm tra:
- theo `testing-lessons`: `npm run check:prose` trước, rồi test của phần đã sửa, rồi một lần chạy toàn bộ tách nền trước khi đẩy;
- giao diện kiểm ở 320, 375 và 1280px;
- chụp ảnh trước và sau, không có cuộn ngang, không lỗi console.

Đổi khung câu thì phải tạo lại golden của lá 2002 và benchmark20, kèm bảng so trước/sau để chủ dự án duyệt.

## 6. Cần chủ dự án quyết

1. Bảng tư thế "mở rộng / giữ / phòng thủ" (mục 3.3) là quy ước hệ thống, không có trang sách. Đồng ý dùng có gắn nhãn, hay chỉ dùng khi tìm được câu sách?
2. Sao nhỏ chỉ còn một dòng ở phần chính, câu đầy đủ chuyển vào Đọc sâu (mục 3.1). Đồng ý không?
3. Câu khuyên không có chi tiết riêng thì bỏ hẳn (mục 3.4), hay giữ mà ghi rõ là lời khuyên chung?
4. Mục 2 nên làm ngay như một lỗi, trước cả EP giai đoạn 1 (đề xuất)?
