# Bát Tự: đối chiếu với bốn cuốn sách (2026-10-17)

Đã đọc trực tiếp các PDF. Mọi "verified" dưới đây nghĩa là **Claude đã đọc đúng trang và diễn đạt lại**; chưa có người thứ hai kiểm, và định nghĩa vận hành bằng ngưỡng số vẫn là của hệ thống (draft).

| Sách | Dạng file | Dùng được vào việc gì | Trạng thái |
|---|---|---|---|
| Trích Thiên Tủy (Lưu Bá Ôn, Nhậm Thiết Tiều bình giảng, bản dịch Việt) | có text layer, 235 trang | tư lệnh tháng Dần, căn/mộ khố, nguyên lưu, thông quan, hàn thử, táo thấp, Quan Sát (hỗn tạp), Thương Quan (5 cách dụng), thanh/trọc, chân/giả thần, tòng (vượng/cường/thế/tài/quan), hóa (dư/thiếu), tuế vận (cái đầu, tiệt cước, thiên khắc địa xung) + hơn 120 mệnh lệ có nhãn | đã đọc các chương trên; chưa đọc: Phần II lục thân, các chương Thiên Can/Địa Chi/Hình Tượng/Bát Cách/Thể Dụng |
| Dự Đoán Theo Tứ Trụ (Thiệu Vĩ Hoa) | **bản scan 681 trang**, không có text, đọc qua ảnh trang | tính điểm vượng suy + quy tắc 40% (tr.331–355); cách lấy cách theo can ngày/tháng sinh, đánh giá tốt xấu của chính cách, cách đặc biệt (tr.356–376); dụng thần theo cách và hỉ kị của vận (tr.376–386); bảng điều hậu 12 tháng × 10 can (tr.389–390) | đã cài và đối chiếu; đã đọc thêm tr.391–399 (chú thích thứ tự điều hậu và 3 ví dụ chọn dụng thần); chưa đọc: các chương lục thân, hóa giải, ví dụ thực tế |
| Đổi Vận Cho Người Mệnh Khuyết, Xuân Hạ / Thu Đông (Lý Cư Minh) | có text layer, 179 + 152 trang | không dùng làm nguồn quy tắc | sách phổ thông về "mệnh khuyết" theo mùa dương lịch cùng khuyến nghị đời sống (màu, hướng, mua vàng...), không phải kinh điển và không kiểm chứng được; đã đọc phần giới thiệu và chương đầu |

## Đã cài từ sách

- **Thiệu Vĩ Hoa, tính điểm** (`tvh_score.py`): 36/9 độ cho thiên can, ngũ hợp, khắc gần/cách/kẹp, quan hệ can–chi cùng trụ, bảng 30 độ của địa chi, tam hội 72 / tam hợp 60 / bán tam hợp 40 / lục hợp 36, xung (bảng hao 1/3, 1/2), chi tháng nắm lệnh ±1/5, nhật chủ vượng khi phe mình ≥ 40%. Khớp **chính xác** độ của thiên can ở các ví dụ 3, 4, 6, 7 và độ của địa chi ở các ví dụ 3, 4, 7; địa chi của ví dụ 6 lệch (sách dùng −6 ở một chỗ và −8 ở chỗ khác, và không cộng +6 mà quy tắc nói cộng); ví dụ 1 và 5 có chỗ sách tự mâu thuẫn (ghi trong docstring của `tvh_score.py`).
- **Trích Thiên Tủy**: tòng vượng/cường/thế (thêm vào ngoại cách), vai trò hỷ/kỵ theo từng loại tòng (`tong_roles.json`), hóa thần dư/thiếu, nguyên lưu (`flow.py`), hàn–noãn, năm cách Thương Quan dụng, Quan Sát hỗn tạp (pp.85, 90–91), chế sát quá mức, cái đầu / tiệt cước, thiên khắc địa xung theo sức nhật chủ, profile `ttt_ntt_v1` (khố tự có căn, không coi tranh hợp là cản hóa thật, bảng tư lệnh chỉ có tháng Dần: Mậu 7 + Bính 8 + Giáp 15 ngày).

## Đã cài thêm từ Thiệu Vĩ Hoa (tr.356–390)

- **Cách đặc biệt** (`tvh_cach.py`): khúc trực, viêm thượng, gia sắc, tòng cách, nhuận hạ, tòng tài/sát/nhi, hóa khí theo đúng điều kiện của sách. Kiểm bằng **các ví dụ của chính sách: 29/31 lá số nhận đúng**; hai lá còn lại là khoảng trống đã ghi (viêm thượng ví dụ 2: sách coi Nhâm là hư phù dù Canh trong Tỵ cho nó chỗ dựa theo phép thử của sách; nhuận hạ ví dụ 4 cần "thê tòng phu hóa").
- **Đánh giá tốt xấu của chính cách** (`tvh_thanhbai.json`, tr.367–369): 39 câu của sách, mỗi câu là một điều kiện trên "nhật chủ vượng/nhược" (quy tắc 40%) và tỉ trọng các nhóm; kết quả liệt kê câu tốt và câu xấu song song, không cộng điểm.
- **Dụng thần theo cách** (`tvh_dungthan.json`, tr.378–386): 51 dòng (cách × vượng/nhược × nhóm nhiều nhất) kèm vận tốt/xấu, chạy thành phương pháp riêng `cach_cuc_tvh`, không trộn với `cach_cuc`.
- **Điều hậu** (`tvh_dieuhau.json`, tr.389–390): bảng 120 ô của sách là nguồn tập can dùng được. Bảng 窮通寶鑑 nhập từ trí nhớ trước đó trùng **108/120 ô** và can đầu của nó luôn nằm trong ô của sách; thứ tự ưu tiên lấy từ chú thích tr.391–396 (`notes_order`, can đầu = chủ), đã đối chiếu: 111/120 ô cùng tập can với bảng, 9 ô lệch được ghi trong `tests/test_bazi_deep_dieuhau.py` (NOTE_DIFFS); bảng 窮通寶鑑 nhập từ trí nhớ chỉ còn là phương án dự phòng.

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
- Ví dụ chọn dụng thần tr.397–399: `cach_cuc_tvh` lấy tỉ trọng nhóm từ điểm TVH; ví dụ 1 ra Quan/Sát trước (khớp 'Mộc' của sách), ví dụ 3 chỉ khớp một phần (sách chọn Thủy+Mộc theo cân bằng ngũ hành), ví dụ 2 nằm sát ngưỡng 40% nên ra hai cách đọc. Chưa đọc: phần lục thân của cả hai sách. Chưa cài: vận hỷ kỵ theo cách đặc biệt cho khúc trực và tòng cách (sách không liệt kê), các điều 'ngoại cách' còn lại của Trích Thiên Tủy.
- Nhãn loại tòng Vượng/Cường của sách không tách được bằng tỉ trọng nhóm (hai nhóm chồng nhau), nên hệ thống vẫn xuất hai tên theo ngưỡng cố định.
