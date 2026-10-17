# Bát Tự: đối chiếu với bốn cuốn sách (2026-10-17)

Đã đọc trực tiếp các PDF. Mọi "verified" dưới đây nghĩa là **Claude đã đọc đúng trang và diễn đạt lại**; chưa có người thứ hai kiểm, và định nghĩa vận hành bằng ngưỡng số vẫn là của hệ thống (draft).

| Sách | Dạng file | Dùng được vào việc gì | Trạng thái |
|---|---|---|---|
| Trích Thiên Tủy (Lưu Bá Ôn, Nhậm Thiết Tiều bình giảng, bản dịch Việt) | có text layer, 235 trang | tư lệnh tháng Dần, căn/mộ khố, nguyên lưu, thông quan, hàn thử, táo thấp, Quan Sát (hỗn tạp), Thương Quan (5 cách dụng), thanh/trọc, chân/giả thần, tòng (vượng/cường/thế/tài/quan), hóa (dư/thiếu), tuế vận (cái đầu, tiệt cước, thiên khắc địa xung) + hơn 120 mệnh lệ có nhãn | đã đọc các chương trên; chưa đọc: Phần II lục thân, các chương Thiên Can/Địa Chi/Hình Tượng/Bát Cách/Thể Dụng |
| Dự Đoán Theo Tứ Trụ (Thiệu Vĩ Hoa) | **bản scan 681 trang**, không có text, đọc qua ảnh trang | phương pháp tính điểm độ vượng suy nhật chủ (tr.331–355) và quy tắc 40% | đã cài và đối chiếu; chưa đọc: phân loại cách cục (tr.356–375), chọn dụng thần (tr.376–397), các chương lục thân, hóa giải |
| Đổi Vận Cho Người Mệnh Khuyết, Xuân Hạ / Thu Đông (Lý Cư Minh) | có text layer, 179 + 152 trang | không dùng làm nguồn quy tắc | sách phổ thông về "mệnh khuyết" theo mùa dương lịch cùng khuyến nghị đời sống (màu, hướng, mua vàng...), không phải kinh điển và không kiểm chứng được; đã đọc phần giới thiệu và chương đầu |

## Đã cài từ sách

- **Thiệu Vĩ Hoa, tính điểm** (`tvh_score.py`): 36/9 độ cho thiên can, ngũ hợp, khắc gần/cách/kẹp, quan hệ can–chi cùng trụ, bảng 30 độ của địa chi, tam hội 72 / tam hợp 60 / bán tam hợp 40 / lục hợp 36, xung (bảng hao 1/3, 1/2), chi tháng nắm lệnh ±1/5, nhật chủ vượng khi phe mình ≥ 40%. Khớp **chính xác** độ của thiên can ở các ví dụ 3, 4, 6, 7 và độ của địa chi ở các ví dụ 3, 4, 7; địa chi của ví dụ 6 lệch (sách dùng −6 ở một chỗ và −8 ở chỗ khác, và không cộng +6 mà quy tắc nói cộng); ví dụ 1 và 5 có chỗ sách tự mâu thuẫn (ghi trong docstring của `tvh_score.py`).
- **Trích Thiên Tủy**: tòng vượng/cường/thế (thêm vào ngoại cách), vai trò hỷ/kỵ theo từng loại tòng (`tong_roles.json`), hóa thần dư/thiếu, nguyên lưu (`flow.py`), hàn–noãn, năm cách Thương Quan dụng, Quan Sát hỗn tạp (pp.85, 90–91), chế sát quá mức, cái đầu / tiệt cước, thiên khắc địa xung theo sức nhật chủ, profile `ttt_ntt_v1` (khố tự có căn, không coi tranh hợp là cản hóa thật, bảng tư lệnh chỉ có tháng Dần: Mậu 7 + Bính 8 + Giáp 15 ngày).

## Độ trung thành đo được (tests/test_bazi_deep_fidelity.py, 81 mệnh lệ)

| Phép đo | Kết quả |
|---|---|
| Nhật chủ vượng/nhược so với nhãn của sách (48 lá số: tòng + Thương Quan) | **Thiệu Vĩ Hoa 45/48 (94%)**; trọng số cũ của hệ thống 36/48 (75%) |
| Nhận ra có ngoại cách tòng (27 lá số tòng) | 18/27; đúng nhãn loại tòng 10/27 |
| Chọn đúng một trong năm cách Thương Quan dụng | 9/21 (sách tự chọn theo phán đoán, chỉ tái hiện được một phần) |
| Hợp quan lưu sát / hỗn tạp / chế sát quá mức | 8/9, 4/4, 4/5 |
| Hàn–noãn (4 lá số có nhãn) | 4/4 |

Vì vậy profile `tvh40_v1` (quyết định vượng/nhược theo Thiệu Vĩ Hoa) là mặc định của `pipeline.analyse` và `/api/bazi-structure`; profile `baseline_v1` giữ nguyên để so sánh.

## Chưa làm / giới hạn

- Thiệu Vĩ Hoa: phu tòng thê hóa, thê tòng phu hóa, uyên ương hợp hóa chưa hỗ trợ (ghi trong `notes.unsupported`); tính điểm chỉ áp cho nguyên cục, **không** áp cho đại vận/lưu niên (phần "cục mở rộng" vẫn dùng trọng số của hệ thống).
- Đã đọc nhưng **chưa cài**: tư lệnh các tháng ngoài Dần (sách không có bảng), tòng khí, quy tắc Thanh–Trọc thành thuật toán (mới có phần trọc qua các mẫu thập thần), điều hậu theo bảng 窮通寶鑑 (bảng 10×12 trong repo vẫn nhập từ trí nhớ, chưa đối chiếu).
- Chưa đọc: phân loại cách cục và chọn dụng thần của Thiệu Vĩ Hoa (tr.356–397), phần lục thân của cả hai sách.
- Nhãn loại tòng Vượng/Cường của sách không tách được bằng tỉ trọng nhóm (hai nhóm chồng nhau), nên hệ thống vẫn xuất hai tên theo ngưỡng cố định.
