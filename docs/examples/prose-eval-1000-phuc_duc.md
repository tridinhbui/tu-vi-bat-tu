# Đánh giá văn đọc chương phuc_duc trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter phuc_duc` (prose prose-0.2.0, knowledge `4db446cf1b5653fc`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 54 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 (mọi lá số, kể cả chương trống) | 76.5% | ≥ 95% |
| Như trên, chỉ tính chương có từ 3 câu (729 lá số) | 89.3% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0.001 / 0.03 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “đường đời” 4.6% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “đến cung” 10.0% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.084 | ≤ 0.35 |
| Entropy phân bố schema | 2.13 / log(12) = 2.485 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 73.28 ms / 76.4 ms | p95 < 30 ms |

Schema: S_DOUBLE_EDGE 211, S_QUIET_STRENGTH 178, S_EDGE_LATE_ELABORATE 176, S_LIMIT_CORE 121, S_VCD_BORROW 94, S_SATELLITE_WEAVE 70, S_PLAIN 60, S_TIMING_ARC 28, S_TURN_THEN_TENSION 23, S_TIMING_FIRST 16, S_TENSION_BRIDGE 12, S_TENSION_CORE 11



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Về cung Phúc Đức, nơi Thái Dương đóng tại Ngọ, người mang lá số này thường có chỗ hóa giải, nên phần khó không đi đến cùng. Có điều, chủ nhân lá số cũng dễ chịu những thăng trầm hơn người cùng cảnh. Lá số của họ có cơ chế tự cân bằng: cái khó đến, cái gỡ cũng đến. Nếu phải gọi tên một điểm tựa, đó là cái thế không bị đẩy đến cùng; biết tích lũy từng bước thay vì mong một bước tới đích là cách để điều bất lợi không đi đến cùng.

### {"year":1943,"month":2,"day":24,"hour":20,"minute":30,"gender":"female","to_year":2026} · S_PLAIN

Soi sang cung Mệnh, lại thấy người này thường sống thanh đạm, ít đòi hỏi.

### {"year":1999,"month":1,"day":19,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Nhìn vào Thất Sát ở cung Phúc Đức tại Ngọ, có thể thấy người này thường gặp nhiều điều tốt lành hơn người; đường đời của họ nhìn chung là đường xuôi, dù không thiếu những khúc quanh. Điều đọng lại sau tất cả là sự thuận lợi của đường đời.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Trong cung Phúc Đức, bộ Vũ Khúc và Thiên Tướng đóng tại Dần cho thấy đương số thường có quý nhân và vận may đi cùng; đường đời của họ nhìn chung là đường xuôi, dù không thiếu những khúc quanh. Nếu phải gọi tên một điểm tựa, đó là sự thuận lợi của đường đời.

### {"year":1996,"month":10,"day":14,"hour":13,"minute":15,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Xét cung Phúc Đức tại Tỵ, nơi Cự Môn tọa thủ, người này thường được hưởng phúc, đường đời nhìn chung thuận; những lúc khó, người mang tổ hợp này thường gặp được người giúp hay một lối ra bất ngờ. Thế nhưng, chủ nhân lá số cũng dễ bận lòng vì nhiều chuyện, ít khi thảnh thơi. Rốt lại, cái vốn quý của người này nằm ở phúc phần sẵn có; khi biết phân biệt điều mình lo được và điều không, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

Ở cung Mệnh, điều này cũng hiện ra: họ thường xem nhẹ danh lợi, không ham tranh giành.

### {"year":1995,"month":5,"day":15,"hour":19,"minute":30,"gender":"male","to_year":2026} · S_TURN_THEN_TENSION

Riêng ở cung Phúc Đức, bộ Tử Vi và Tham Lang tại Dậu báo hiệu rằng người mang lá số này thường được an nhàn, sung túc lúc về già. Địa Kiếp đóng cùng cung làm tính cách thêm phần căng: người này dễ phải lo toan nhiều về chuyện tiền nong. Ở chiều ngược lại, chủ nhân lá số cũng dễ lao tâm khổ tứ, khó yên lòng. Khi đã biết dành cho mình những khoảng nghỉ thật sự, chỗ yếu cũng thành chỗ rèn mình.

Tuổi trẻ của đương số là quãng gieo; quãng gặt đến về sau. Song người này cũng dễ chịu những thăng trầm hơn người cùng cảnh.

### {"year":1997,"month":6,"day":6,"hour":11,"minute":45,"gender":"female","to_year":2026} · S_VCD_BORROW

Tại Dần, cung Phúc Đức không có chính tinh; với Hồng Loan đóng ở đây, người mang lá số này thường có quý nhân và vận may đi cùng. Nếu phải gọi tên một điểm tựa, đó là sự thuận lợi của đường đời.

Đường đời của họ nhìn chung là đường xuôi, dù không thiếu những khúc quanh.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_LIMIT_CORE

Khi Thiên Cơ làm chủ cung Phúc Đức ở Tý, người này dễ lao tâm khổ tứ, khó yên lòng. Khi biết dành cho mình những khoảng nghỉ thật sự, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_LIMIT_CORE

Với Vũ Khúc và Thất Sát đồng cung Phúc Đức tại Mão, người này dễ lo trước những điều chưa tới. Nếu biết dành cho mình những khoảng nghỉ thật sự, phần khó ấy sẽ bớt nặng đi nhiều.

Có một mặt khác cần thấy: đương số cũng dễ có những bất hòa trong nhà; nhìn từ cung Mệnh, họ thường an nhiên trước biến động.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_LIMIT_CORE

Không có chính tinh, cung Phúc Đức tại Tý được đọc qua Địa Không đóng tại đó; người mang lá số này dễ phải lo toan nhiều về chuyện tiền nong, và cũng dễ chịu những thăng trầm hơn người cùng cảnh. Khi biết tích lũy đều đặn thay vì mong một lần đổi đời, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

Từ phía cung Mệnh, chủ nhân lá số thường sống thanh đạm, ít đòi hỏi.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Xét cung Phúc Đức tại Tuất, nơi Thiên Cơ và Thiên Lương đồng cung, đương số thường có quãng sau của đời vững vàng hơn quãng đầu. Người này gặt hái muộn, nhưng phần gặt hái ấy ở lại lâu.

### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Về cung Phúc Đức, nơi Tham Lang đóng tại Ngọ, người này thường gặp nhiều điều tốt lành hơn người; những lúc khó, đương số thường gặp được người giúp hay một lối ra bất ngờ. Thế nhưng, người mang tổ hợp này cũng dễ lo trước những điều chưa tới. Điều đọng lại sau tất cả là phúc phần sẵn có; biết phân biệt điều mình lo được và điều không là cách để điều bất lợi không đi đến cùng.

Ngược lại, chủ nhân lá số cũng dễ có những bất hòa trong nhà.
