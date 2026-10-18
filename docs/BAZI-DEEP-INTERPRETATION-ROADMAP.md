# Lộ trình nâng cấp luận giải Bát Tự sâu

Trạng thái: nhánh `bazi-deep-reading` (xây trên PR #4), cờ **mặc định tắt**, chưa merge, chưa deploy. Tài liệu đi kèm: `BAZI_DEEP_INTERPRETATION_ARCHITECTURE.md` (kiến trúc), `BAZI_DEEP_READING_COVERAGE.md` (ma trận bao phủ và độ phân biệt), `BAZI_DEEP_READING_SAMPLES.md` (hai bản luận mẫu đối lập).

## 1. Audit baseline: bản luận hiện tại thiếu gì
Đọc `analysis.analyse` và `/api/analysis` của lá số 15/12/1990 (và các lá số khác):
- Phần Bát Tự chỉ **đếm và kể tên**: "Quan Sát xuất hiện ở thiên can trụ năm và tàng can trụ giờ; Ấn xuất hiện ở tàng can trụ tháng; chưa xét việc chúng có thành cách hay không".
- Nói thẳng: "hệ thống chưa có quy tắc cách cục đã xác minh… không xác định cách cục từ nguyệt lệnh", dù engine sâu đã có cách cục, thành/bại, dụng thần, điều hậu, đại vận.
- Ba chương Tính cách, Sự nghiệp, Tài lộc, Hôn nhân (chương `quan-he`) chủ yếu là Tử Vi; phần Bát Tự là một dòng thập thần và một dòng Tài.
- Chương đại vận là đại hạn **Tử Vi**; đại vận Bát Tự không có.
- Không có chuỗi lập luận, không có mức chắc chắn, không có nguồn trang cho phần Bát Tự cấu trúc.
- Engine sâu (`bazi_deep`) chưa hề đi vào trải nghiệm đọc chính: chỉ có API và trang nháp.

## 2. Thứ tự học thuật và chỗ nó nằm trong bản luận
| Yêu cầu | Đã làm trong reading/1 |
|---|---|
| Nguyệt lệnh, khí mùa, đắc lệnh/địa/thế, thông căn, thấu can | Nền tảng: nguyệt lệnh (tư lệnh), ba tiêu chí của hệ thống, thông căn trong cách tính |
| Vượng/nhược, hàn noãn táo thấp, điều hậu, phù ức, thông quan | Nền tảng: 40% của TVH và cách riêng của hệ thống (đặt cạnh nhau), điều hậu TVH, hàn–nóng; phù ức và thông quan ở chương Dụng thần. **Táo–thấp: chưa có** (độ ẩm chưa được tính) |
| Cách cục chính/phụ, thành, phá, cứu | Nền tảng: cách chính, thành/bại, đánh giá tốt xấu của TVH, ngoại cách chân/giả |
| Dụng, hỷ, kỵ, nhàn theo từng trường phái | Chương Dụng thần: tám phương pháp tách biệt, không đáp án cuối |
| Thập thần phối hợp có tên | Nền tảng: `patterns` (draft); chưa có lời sách gán nghĩa |
| Hợp, xung, hình, hại, phá, hội, bán hợp, hợp hóa | Nền tảng: từng quan hệ với trạng thái đã giải (hóa thật/giả, tranh hợp, xung vào cục...) |
| Đại vận, lưu niên, lưu nguyệt lên nguyên cục | Chương Đại vận: lịch chính xác tới ngày, vận hỷ/kỵ, tác động từng đại vận. **Lưu niên, lưu nguyệt: chưa vào bản luận** (có ở `/api/bazi-timeline`) |

## 3. Bảy chương
Mỗi chương có: Kết luận chính (chỉ ghép từ các ý đã chọn), "Vì sao lá số này được luận như vậy?", ý theo mục với chuỗi dữ kiện→quy tắc→điều kiện→kết luận, thuận/bất lợi và cặp ý ngược chiều, mức chắc chắn và nguồn, giới hạn. Chế độ **Dễ hiểu** và **Chuyên sâu** cùng dựa trên một chuỗi lập luận. Chương nào không có quy tắc nào của sách khớp nói rõ điều đó (chỉ báo thực: Năng lực trống ở 27% lá số, Tài lộc 48%; xem ma trận bao phủ).

## 4. Điều bản luận này KHÔNG hứa
- Không dự đoán sự kiện; không gọi dụng thần là đúng hay đã được kiểm chứng.
- Không có kiểm chứng thực nghiệm cho bất kỳ diễn giải nào; 0/120 ô điều hậu và 0/10 ví dụ có người xác nhận (xem tài liệu Phase 7–8).
- Những chỗ nguồn đã nhập không có quy tắc (tổng hợp tính cách, năng lực cụ thể, định lượng tài sản, sao vợ/chồng theo giới tính, cách chọn giữa các phương pháp dụng thần) được in ra là **chưa đủ căn cứ**, không được lấp.

## 5. Lộ trình tiếp theo (theo độ vững của nguồn)
| Giai đoạn | Việc | Điều kiện nguồn |
|---|---|---|
| A (xong ở nhánh này) | Bộ máy reading/1, 7 chương, hai chế độ, ma trận bao phủ, độ phân biệt, cờ tắt | nguồn đã nhập |
| B | **Đọc thêm nguồn** để lấp các chỗ 'chưa đủ căn cứ': lục thân của Thiệu Vĩ Hoa và Trích Thiên Tủy Phần II (cha mẹ, con cái, vợ chồng theo giới tính), chương tài của Trích Thiên Tủy, phần còn lại của 八字真宗 pp.60–96 | cần đọc trang và đối chiếu; mỗi luật mới vào pack ở trạng thái draft |
| C | Người kiểm độc lập: 120 ô điều hậu, 10 ví dụ (quy trình và công cụ đã có), 9 ô sách tự mâu thuẫn chờ quyết định học thuật | người thật |
| D | Đưa lưu niên/lưu nguyệt và độ ẩm (táo–thấp) vào bản luận; gắn vào giao diện chính (do phiên sở hữu `web/` quyết định) | cần nguồn táo–thấp; cần chủ sở hữu giao diện |
| E | Nghiên cứu thực nghiệm về giá trị dự báo (mẫu có kết quả ghi trước, người chấm độc lập) | chưa có; trước đó không được nói "đã kiểm chứng" |

## 6. Bằng chứng kiểm thử (xem `BAZI_DEEP_READING_COVERAGE.md` cho số liệu sinh tự động)
- 22 test Python mới (`engine/tests/test_bazi_deep_reading.py`) trên 400 lá số thật và kiểm tra bằng trình duyệt giả lập node trên 300 lá số ở cả hai chế độ: bảy chương đúng thứ tự; mọi ý đủ bốn bước; ý `co_nguon` luôn có nguồn; không lọt mã nội bộ hay cụm tuyệt đối; không còn luật 八字真宗 nào chưa được định tuyến; ý ngược chiều được ghép cặp; đại vận hỷ/kỵ có điều kiện; hai lần chạy giống từng byte; cờ tắt thì phản hồi không đổi; không import thư viện mạng hay LLM; không có câu nào viết riêng cho một lá số.
- Độ phân biệt (600 lá số): toàn bản luận khác nhau 600/600; chương Tính cách 522 tập khác nhau, Dụng thần 569; chương mỏng nguồn (Năng lực, Tài lộc) chỉ có 6 tổ hợp luật khác nhau và được nói rõ là mỏng.
- Cặp lá số đối lập (vượng rõ/nhược rõ) cho nền tảng và dụng thần khác nhau; ngoại cách chân đổi chương Dụng thần.
- Kiểm tra trình duyệt thật (desktop, 375 px): không tràn ngang, chuyển chế độ không cần gọi lại máy chủ, nhãn "Phân tích thử nghiệm" luôn nằm đầu và dính khi cuộn.
