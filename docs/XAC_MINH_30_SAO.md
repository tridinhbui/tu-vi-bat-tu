# Phiếu đối chiếu: 30 sao phụ, Mệnh chủ, Thân chủ

**Trạng thái: CHƯA xác minh bản nào.** Các công thức trong `engine/tvbt/aux_stars.py` và `engine/tvbt/cach_cuc.py` được viết từ kiến thức chung về cách an sao phổ biến, không đối chiếu với trang sách nào (repo không chứa nguồn cho 30 sao này; các gói luật hiện có chỉ nhắc tên một vài sao trong *luận giải*, không có công thức an). Vì vậy `rule_review.aux_stars` và `rule_review.menh_chu_than_chu` giữ `unverified`, và giao diện gạch chân chấm các sao này.

Cột “độ chắc” là mức tự tin của người viết, **không phải** bằng chứng. Chỉ chuyển sang `verified` khi người có sách điền cột “trang” và hai dòng nguồn đều khớp (nhớ thêm `locator` trong `data/sources.json`).

Quy ước: chi 0=Tý … 11=Hợi; “tháng” là tháng âm lịch hiệu lực; “giờ” là chi giờ sinh (Tý=0); “ngày” là ngày âm lịch.

| Sao | Công thức đã cài | Độ chắc | Dị bản/điểm cần kiểm | Sách, trang (điền) |
|---|---|---|---|---|
| Thiên Khốc | Ngọ lùi theo chi năm: `6 − chi năm` | cao | — | |
| Thiên Hư | Ngọ tiến theo chi năm: `6 + chi năm` | cao | — | |
| Long Trì | Thìn tiến theo chi năm | cao | — | |
| Phượng Các | Tuất lùi theo chi năm | cao | — | |
| Cô Thần | theo mùa của chi năm: Hợi-Tý-Sửu→Dần; Dần-Mão-Thìn→Tỵ; Tỵ-Ngọ-Mùi→Thân; Thân-Dậu-Tuất→Hợi | cao | — | |
| Quả Tú | cùng nhóm: →Tuất; →Sửu; →Thìn; →Mùi | cao | — | |
| Thiên Quan | bảng theo can năm: Giáp Mùi, Ất Thìn, Bính Tỵ, Đinh Dần, Mậu Mão, Kỷ Dậu, Canh Hợi, Tân Dậu, Nhâm Tuất, Quý Ngọ | vừa | có dị bản giữa các ấn bản; kiểm từng can | |
| Thiên Phúc | Giáp Dậu, Ất Thân, Bính Tý, Đinh Hợi, Mậu Mão, Kỷ Dần, Canh Ngọ, Tân Tỵ, Nhâm Ngọ, Quý Tỵ | vừa | như trên | |
| Thiên Thọ | từ cung Thân đếm thuận tới chi năm | vừa | kiểm điểm xuất phát (Thân hay Mệnh) | |
| Thiên Tài | từ cung Mệnh đếm thuận tới chi năm | vừa | như trên | |
| Thiên Thương | cố định ở cung Nô Bộc | cao | — | |
| Thiên Sứ | cố định ở cung Tật Ách | cao | — | |
| Thiên La | cố định ở Thìn | cao | — | |
| Địa Võng | cố định ở Tuất | cao | — | |
| Thiên Hình | Dậu tiến theo tháng (tháng 1 ở Dậu) | vừa | kiểm điểm xuất phát | |
| Thiên Riêu | Sửu tiến theo tháng (tháng 1 ở Sửu) | vừa | kiểm điểm xuất phát | |
| Thiên Y | cùng cung Thiên Riêu | vừa | một số sách an riêng; kiểm | |
| Thiên Giải | Thân tiến theo tháng | vừa | kiểm | |
| Địa Giải | Mùi tiến theo tháng | vừa | kiểm | |
| Đẩu Quân | chi năm lùi theo tháng, rồi tiến theo giờ | vừa | công thức dễ nhầm hướng | |
| Hoa Cái | theo tam hợp chi năm: Dần-Ngọ-Tuất→Tuất; Thân-Tý-Thìn→Thìn; Tỵ-Dậu-Sửu→Sửu; Hợi-Mão-Mùi→Mùi | vừa | kiểm | |
| Kiếp Sát | cùng nhóm: →Hợi; →Tỵ; →Dần; →Thân | vừa | kiểm | |
| Phá Toái | Tý-Ngọ-Mão-Dậu→Tỵ; Dần-Thân-Tỵ-Hợi→Dậu; Thìn-Tuất-Sửu-Mùi→Sửu | vừa | kiểm | |
| Lưu Hà | bảng theo can năm: Giáp Dậu, Ất Tuất, Bính Mùi, Đinh Thân, Mậu Tỵ, Kỷ Ngọ, Canh Thìn, Tân Mão, Nhâm Hợi, Quý Dần | vừa | kiểm | |
| Thiên Đức | Dậu tiến theo chi năm | thấp | rất có thể có dị bản; kiểm đầu tiên | |
| Nguyệt Đức | Tỵ tiến theo chi năm | thấp | như trên | |
| Tam Thai | từ Tả Phụ tiến `ngày − 1` | vừa | kiểm | |
| Bát Tọa | từ Hữu Bật lùi `ngày − 1` | vừa | kiểm | |
| Ân Quang | từ Văn Xương tiến `ngày − 2` | vừa | “lùi một cung” có thể tính khác; kiểm | |
| Thiên Quý | từ Văn Khúc tiến `ngày − 2` | vừa | như trên | |
| Mệnh chủ | theo chi cung Mệnh: Tý Tham Lang; Sửu, Hợi Cự Môn; Dần, Tuất Lộc Tồn; Mão, Dậu Văn Khúc; Thìn, Thân Liêm Trinh; Tỵ, Mùi Vũ Khúc; Ngọ Phá Quân | vừa | một số sách tính theo chi năm hoặc đổi tên; kiểm | |
| Thân chủ | theo chi năm: Tý Linh Tinh; Sửu, Mùi Thiên Tướng; Dần, Thân Thiên Lương; Mão, Dậu Thiên Đồng; Thìn, Tuất Văn Xương; Tỵ, Hợi Thiên Cơ; Ngọ Hỏa Tinh | vừa | kiểm | |

## Chưa an (không rõ công thức)
Quốc Ấn, Đường Phù, Phong Cáo, Giải Thần. Cố ý bỏ trống thay vì đoán; khai báo trong `aux_stars.NOT_PLACED` và hiện ở khung “Phạm vi lá số”.

## Về trường phái
Hiện chỉ có **một** cách an cho mỗi sao (chưa có tham số trường phái). Chỉ thêm tham số khi có sách chỉ ra dị bản cụ thể, vì thêm dị bản không có nguồn sẽ chỉ tạo thêm lựa chọn không kiểm chứng được.

## Kiểm thử hiện có (không chứng minh đúng sách)
`tests/test_aux_stars_cach_cuc.py` khóa công thức đã cài để thay đổi vô tình bị phát hiện, cùng các bất biến: Khốc–Hư đối xứng qua trục Tý–Ngọ, Thiên Y trùng cung Thiên Riêu, mỗi sao chỉ xuất hiện một lần, vị trí luôn thuộc 0–11.

## Việc cần người có sách
1. Điền cột “trang” cho từng dòng (ưu tiên các dòng độ chắc “thấp” và “vừa”).
2. Với dòng khớp: thêm nguồn vào `data/sources.json` (có `locator`), đổi `rule_review` tương ứng sang `verified`, tách sao đó khỏi nhóm “chưa đối chiếu”.
3. Với dòng không khớp: sửa công thức, cập nhật test khóa, ghi dị bản vào cột bên cạnh.
