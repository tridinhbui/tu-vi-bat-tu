# Đánh giá văn đọc chương tu_tuc trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter tu_tuc` (prose prose-0.2.0, knowledge `4db446cf1b5653fc`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 229 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 (mọi lá số, kể cả chương trống) | 61.3% | ≥ 95% |
| Như trên, chỉ tính chương có từ 3 câu (650 lá số) | 86.6% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0.001 / 0.022 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “tiền bạc” 7.9% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “” 22.9% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.047 | ≤ 0.35 |
| Entropy phân bố schema | 1.811 / log(9) = 2.197 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 73.71 ms / 76.86 ms | p95 < 30 ms |

Schema: S_QUIET_STRENGTH 253, S_SATELLITE_WEAVE 231, S_PLAIN 229, S_VCD_BORROW 121, S_EDGE_LATE_ELABORATE 51, S_LIMIT_CORE 46, S_DOUBLE_EDGE 42, S_TIMING_ARC 25, S_TIMING_FIRST 2



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Trong cung Tử Tức, bộ Liêm Trinh và Thất Sát đóng tại Sửu cho thấy con cái thường có nguồn thu rộng mở; các con thường có điều kiện vật chất tốt hơn mức trung bình. Cùng một mạch ấy, đương số thường sống giữa một nhà đông người. Rốt lại, ở con cái đáng trân trọng nhất là sự đầy đủ về vật chất.

Song song với điều ấy, những người con thường mang một nét cuốn hút tự nhiên.

### {"year":1943,"month":2,"day":24,"hour":20,"minute":30,"gender":"female","to_year":2026} · S_LIMIT_CORE

Nhìn vào bộ Vũ Khúc và Tham Lang ở cung Tử Tức tại Sửu, có thể thấy người mang lá số này dễ hiếm hoi đường con cái hay anh em. Khi đã biết dồn tình thân cho những người đang có, chỗ yếu cũng thành chỗ rèn mình.

### {"year":1999,"month":1,"day":19,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Riêng ở cung Tử Tức, bộ Thái Dương và Thái Âm tại Sửu báo hiệu rằng con cái sớm có chỗ đứng, cần thời gian để củng cố.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_PLAIN



### {"year":1996,"month":10,"day":14,"hour":13,"minute":15,"gender":"male","to_year":2026} · S_SATELLITE_WEAVE

Về cung Tử Tức, nơi Phá Quân đóng tại Tý, các con thường kiếm tiền không khó, đời sống đầy đủ; kèm theo đó, chủ nhân lá số thường có gia đình đông đủ, con cháu hay anh em đều nhiều. Tiền bạc đến với con cái không quá khó khăn. Điều nên trân trọng nơi con cái là đường tài lộc.

Cùng một mạch ấy, các con thường mang một nét cuốn hút tự nhiên.

### {"year":1995,"month":5,"day":15,"hour":19,"minute":30,"gender":"male","to_year":2026} · S_PLAIN



### {"year":1997,"month":6,"day":6,"hour":11,"minute":45,"gender":"female","to_year":2026} · S_TIMING_FIRST

Đến cung Tử Tức tại Dậu, với Vũ Khúc và Thất Sát cùng tọa thủ, con cái thường có nguồn thu rộng mở; về nhịp đời, các con có những thành tựu sớm, nhưng chưa vững. Tiền bạc đến với con cái không quá khó khăn. Tuy nhiên, đương số cũng dễ hiếm hoi đường con cái hay anh em. Điều đáng quý ở các con là đường tài lộc; biết tìm thêm những người thân không cùng huyết thống là cách để điều bất lợi không đi đến cùng.

Đi cùng nét này, chủ nhân lá số thường sống giữa một nhà đông người.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Riêng ở cung Tử Tức, Thiên Tướng đóng tại Mùi báo hiệu rằng con cái thường sớm có công danh; các con có thể bước vào vị trí quan trọng sớm hơn người cùng lứa. Kèm theo đó, con cái thường học hành sáng dạ, lại kiếm tiền không khó, đời sống đầy đủ. Rốt lại, ở con cái đáng trân trọng nhất là khởi đầu thuận lợi và vốn chữ nghĩa.

Bên cạnh đó, chủ nhân lá số thường được nhiều người thân quây quần.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Có Thái Âm tọa thủ cung Tử Tức ở Tuất, con cái thường kiếm tiền không khó, đời sống đầy đủ; con cái thường có điều kiện vật chất tốt hơn mức trung bình. Cũng vậy, chủ nhân lá số thường có gia đình đông đủ, con cháu hay anh em đều nhiều. Điều nên trân trọng nơi các con là sự đầy đủ về vật chất.

Kèm theo đó, các con thường có duyên, dễ gây thiện cảm ngay từ lần gặp đầu.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_PLAIN



### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Về cung Tử Tức, nơi Thiên Phủ đóng tại Tỵ, các con thường có danh phận hơn người; song người mang tổ hợp này cũng dễ hiếm hoi đường con cái hay anh em. Đường công danh mở ra với những người con rộng hơn mức trung bình. Rốt lại, ở con cái đáng trân trọng nhất là triển vọng công danh; biết dồn tình thân cho những người đang có là cách để điều bất lợi không đi đến cùng.

### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_VCD_BORROW

Tại Sửu, cung Tử Tức không có chính tinh; với Thai đóng ở đây, các con thường kiếm tiền không khó, đời sống đầy đủ. Rốt lại, ở con cái đáng trân trọng nhất là đường tài lộc.

Tiền bạc đến với những người con không quá khó khăn; cũng vậy, đương số thường có gia đình đông đủ, con cháu hay anh em đều nhiều.
