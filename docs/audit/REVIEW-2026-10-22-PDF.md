# Rà soát bản PDF "Thiên Bàn — Tử Vi và Bát Tự" (lá 09/01/2002 04:30 nam) — kiểm chứng và kế hoạch khắc phục

Nguồn: nhận xét của người đọc (2026-10-22) về bản PDF 91 trang. Mỗi điểm đã được kiểm lại trên mã và đầu ra thật (`/api/interpret`, `/api/analysis`, ảnh trang 1 PDF) trước khi xếp vào kế hoạch. Nguyên tắc: sửa ở tầng dữ kiện / áp quy tắc / tổng hợp, không vá chữ; mỗi lỗi có test hồi quy.

| # | Nhận xét | Kiểm chứng | Nguyên nhân gốc | Người sửa | Trạng thái |
|---|---|---|---|---|---|
| ① | Nô Bộc ghi "Tham Lang hãm ở cung Nô Bộc" dù Nô Bộc vô chính diệu, Tham Lang ở Huynh Đệ | **Đúng** — chương Nô Bộc dùng đường văn cũ (`chapter.ts`), coi sao mượn như sao tọa | đường cũ không phân biệt tọa / mượn | luồng Tử Vi sâu | đang sửa |
| ② | Quan Lộc ghi "Cung đối là Thiên Di (Thìn)" | **Đúng** — `analysis.py:249` gán cứng Thiên Di (Thiên Di là tam hợp của Quan Lộc; cung đối là Phu Thê) | gán cứng tên cung | phiên chính | **đã sửa** + `test_analysis_positions.py` (61 lá) |
| ③ | Bát Tự: cách Thiên Tài được dùng, nhưng chỗ khác nói chưa xác định cách / quy tắc định cách chưa xác minh | **Đúng** — `analysis.py` (văn cũ) vs `bazi_deep` (TVH, partial) | hai tầng có trạng thái khác nhau | luồng Bát Tự sâu | đang sửa: một trạng thái duy nhất; vận tốt/xấu theo bảng TVH nói ở dạng có điều kiện |
| ④ | 2026: 25 tuổi và tuổi mụ 26; đại vận 2003: 1 và 2 tuổi | **Đúng, và là lỗi tính** (không chỉ thiếu nhãn): bảng lá số và thẻ tóm tắt tính tuổi mụ từ năm **dương lịch** (2002) thay vì năm âm lịch (Tân Tỵ 2001); `currentPhase` dùng tuổi này chọn đại hạn hiện tại | `tuvi.js:43`, `insights.js:55` | phiên chính (Tử Vi) · luồng Bát Tự (nhãn tuổi thực/tuổi mụ ở Bát Tự) | Tử Vi **đã sửa** + gắn nhãn "tuổi mụ" trên bảng, Tổng quan |
| ⑤ | Mô tả nói lưu Lộc Tồn, Kình Đà, Mã chưa an; nguyệt vận chưa hỗ trợ — nhưng bảng đã có | **Đúng** — `aux_stars.NOT_PLACED` lỗi thời | văn mô tả không cập nhật | phiên chính | **đã sửa**: tách ba trạng thái "đã tính vị trí / đã có lời luận / chỉ số thử nghiệm" |
| ⑥ | Triệt giảm cường độ tật ách → "sức khỏe thuận, với điều kiện đi kèm" | **Đúng** (Tật Ách và Đại hạn 53–62) | yếu tố giảm nhẹ bị ledger đổi thành kết luận thuận | luồng Tử Vi sâu | đang sửa: giảm nhẹ chỉ nói "có yếu tố giảm nhẹ"; không kết luận trạng thái sức khỏe |
| ⑦ | "không đủ sức bảo vệ" thành "Thiên Tướng … cho thấy nguy cơ tai ách, bạo bệnh" | **Đúng** | ánh xạ luật → khái niệm đảo quan hệ nhân quả | luồng Tử Vi sâu | đang sửa + rà mọi luật "không đủ chế" |
| ⑧ | Tử Tức lấy "cha mẹ khá giả, con cái hòa thuận" ở Phụ Mẫu để xác nhận con của đương số | **Đúng** | chứng thực liên cung không kiểm cùng chủ thể / thế hệ | luồng Tử Vi sâu | đang sửa: chứng thực cần cùng chủ thể + quy tắc quan hệ |
| ⑨ | "Thiên Tài thấu can có gốc → tài vận tốt" chưa hòa giải với thân nhược Tài vượng | **Đúng** | thiếu bước phân tầng (vị trí Tài / sức nhật chủ / kết luận theo phương pháp) | luồng Bát Tự sâu | đang sửa |
| ⑩ | 2027 trong nhóm "nên tiến" nhưng đoạn riêng nói tốt xấu đan xen | **Đúng** | danh sách năm lấy theo nhóm can, chưa xét năm × đại vận | luồng Bát Tự sâu | đang sửa |
| ⑪ | Dùng "đến muộn" / "hoàn cảnh đặc biệt" để "nối" mâu thuẫn về chất lượng | **Đúng** (Mệnh, Phu Thê) | ledger chọn nhận định thời điểm làm cầu nối | luồng Tử Vi sâu | đang sửa: thêm kết luận "chưa phân xử được", nêu hai phía và giới hạn kết luận |
| ⑫ | Nhãn "bị giới hạn bởi quy tắc đối lập" nhưng bên dưới "không có quy tắc đối lập khớp" | **Đúng** (`ui.js:52`) | trộn ba trạng thái | luồng Tử Vi sâu | đang sửa: bất lợi / bị quy tắc khác hạn chế (nêu tên) / xung đột chưa phân xử |
| §4a | Luật "Mệnh Tứ Mộ có Tả Hữu" bắn khi Tả Phụ ở tam phương; luật "Hỏa Tinh nhập miếu" bắn khi đắc | cần đối chiếu nguyên văn | điều kiện luật rộng hơn trang | luồng Tử Vi sâu | đang rà toàn corpus |
| §4b | Dùng bảng độ sáng KL để xét luật của TH/TT | **Đúng** — đang trộn | thiếu bảng theo nguồn của luật | luồng Tử Vi sâu | đang sửa: luật xét bằng bảng của sách nó, thiếu ô thì ghi nhãn |
| §4c | Phạm vi "đã xác minh" Bát Tự hẹp hơn phạm vi kết luận | **Đúng** | panel căn cứ chỉ liệt kê nhận định tính cách | luồng Bát Tự sâu | đang sửa |
| §4d | Biểu đồ tạo cảm giác chính xác | đã có câu "chỉ số tổng hợp từ quy tắc, không phải xác suất" | — | — | giữ; cân nhắc đổi tên "chỉ số quy ước của mô hình" |
| §5 | Câu thêm ý ngoài căn cứ ("lật đi lật lại", "quen tự lo từ sớm"), lời khuyên trộn với lời sách | **Đúng** | thẻ mô tả/khuyên không có nhãn | luồng Tử Vi sâu | đang sửa: gắn nhãn minh họa (một nhận định, không thêm ý) hoặc bỏ; lời khuyên gắn "lời khuyên chung" |
| PDF | Bảng Mệnh bàn tứ trụ bị cắt, mất trụ giờ (trang 1) | **Đúng** (ảnh trang 1) | bố cục bảng điều khiển màn hình rộng (`dash.css`) áp cả khi in | phiên chính | **đã sửa** (chỉ áp cho màn hình + quy tắc in vừa khổ); chưa in thử lại |

Thứ tự: lỗi áp quy tắc và tổng hợp (①⑥⑦⑧⑪⑫ §4) trước, rồi mới đào sâu thêm câu luận.
