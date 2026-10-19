# Đánh giá văn đọc chương phuc_duc trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter phuc_duc` (prose prose-0.2.0, knowledge `b301f85298e6bb62`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 53 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 | 67.0% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0.001 / 0.044 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “cung phúc” 6.3% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “cung phúc” 21.8% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.087 | ≤ 0.35 |
| Entropy phân bố schema | 2.127 / log(12) = 2.485 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 42.85 ms / 49.99 ms | p95 < 30 ms |

Schema: S_DOUBLE_EDGE 211, S_EDGE_LATE_ELABORATE 179, S_QUIET_STRENGTH 177, S_LIMIT_CORE 121, S_VCD_BORROW 94, S_SATELLITE_WEAVE 70, S_PLAIN 60, S_TIMING_ARC 25, S_TURN_THEN_TENSION 23, S_TIMING_FIRST 15, S_TENSION_BRIDGE 13, S_TENSION_CORE 12



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Xét cung Phúc Đức tại Ngọ, nơi Thái Dương tọa thủ, người mang lá số này thường có chỗ hóa giải, nên phần khó không đi đến cùng. Có điều, chủ nhân lá số cũng dễ chịu những thăng trầm hơn người cùng cảnh. Lá số của họ có cơ chế tự cân bằng: cái khó đến, cái gỡ cũng đến. Nếu phải gọi tên một điểm tựa, đó là cái thế không bị đẩy đến cùng; biết tích lũy từng bước thay vì mong một bước tới đích là cách để điều bất lợi không đi đến cùng.

### {"year":2006,"month":12,"day":9,"hour":20,"minute":15,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Với Thiên Cơ và Cự Môn cùng ở cung Phúc Đức tại Mão, người này thường đến muộn mà chắc; bù lại, người mang tổ hợp này cũng dễ gặp nhiều vất vả, phải tự mình chống đỡ. Những gì họ gieo khi trẻ thường nở vào nửa sau cuộc đời. Sự hiện diện của Hỏa Tinh khiến mọi thứ gai góc hơn: chủ nhân lá số dễ phải tự mở đường ngay từ những bước đầu. Khi đã biết coi mỗi lần vấp là một lần rèn mình, chỗ yếu cũng thành chỗ rèn mình.

Nhưng người này cũng dễ lao tâm khổ tứ, khó yên lòng.

### {"year":1984,"month":6,"day":21,"hour":7,"minute":45,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Với Tử Vi và Thiên Tướng cùng ở cung Phúc Đức tại Thìn, người mang lá số này thường gặp nhiều điều tốt lành hơn người; ở chiều ngược lại, người mang tổ hợp này cũng dễ lao tâm khổ tứ, khó yên lòng. Đường đời của chủ nhân lá số nhìn chung là đường xuôi, dù không thiếu những khúc quanh. Bởi vậy, điều đáng quý ở lá số này là sự thuận lợi của đường đời; càng biết dành cho mình những khoảng nghỉ thật sự, người này càng phát huy được những gì mình vốn có.

Ngoài ra, người này thường an nhiên trước biến động.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Nhìn vào bộ Vũ Khúc và Thiên Tướng ở cung Phúc Đức tại Dần, có thể thấy đương số thường có quý nhân và vận may đi cùng; đường đời của người mang tổ hợp này nhìn chung là đường xuôi, dù không thiếu những khúc quanh. Nếu phải gọi tên một điểm tựa, đó là sự thuận lợi của đường đời.

### {"year":2017,"month":1,"day":9,"hour":15,"minute":15,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Có Tử Vi và Phá Quân cùng tọa thủ cung Phúc Đức ở Mùi, đương số thường sống nhàn nhã, ít bị xáo trộn; người này có một khoảng yên tĩnh bên trong mà ngoại cảnh khó chạm tới. Dẫu vậy, chủ nhân lá số cũng dễ bận lòng vì nhiều chuyện, ít khi thảnh thơi. Địa Kiếp đóng cùng cung làm tính cách thêm phần căng: người mang tổ hợp này dễ phải lo toan nhiều về chuyện tiền nong. Rốt lại, cái vốn quý của người này nằm ở sự an nhiên; càng biết phân biệt điều mình lo được và điều không, người này càng phát huy được những gì mình vốn có.

Cùng một mạch ấy, đương số thường gặp nhiều điều tốt lành hơn người, lại hưởng phúc từ gia đình, song cũng dễ lận đận, việc gì cũng phải qua nhiều lần mới thành.

### {"year":2017,"month":7,"day":9,"hour":0,"minute":15,"gender":"male","to_year":2026} · S_TIMING_FIRST

Khi Tử Vi và Tham Lang cùng làm chủ cung Phúc Đức ở Dậu, đương số thường gặp nhiều điều tốt lành hơn người; nhịp đời của người này cũng có điểm riêng: người mang tổ hợp này thường hưởng phúc vào quãng sau của cuộc đời. Những lúc khó, họ thường gặp được người giúp hay một lối ra bất ngờ. Ở chiều ngược lại, người này cũng dễ lao tâm khổ tứ, khó yên lòng. Điều đọng lại sau tất cả là phúc phần sẵn có; khi biết phân biệt điều mình lo được và điều không, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

Thêm vào đó, đương số thường an nhiên trước biến động, lại có chỗ dựa từ cha mẹ, anh em.

### {"year":1935,"month":4,"day":4,"hour":12,"minute":15,"gender":"female","to_year":2026} · S_VCD_BORROW

Không có chính tinh, cung Phúc Đức tại Tý được đọc qua Đế Vượng đóng tại đó; đương số thường có chỗ dựa từ cha mẹ, anh em. Rốt lại, cái vốn quý của người này nằm ở tình thân.

Gia đình là hậu phương vững của chủ nhân lá số. Lại nữa, đương số thường gặp nhiều điều tốt lành hơn người, lại có người giúp đúng lúc. Một nét khác đến từ cung Mệnh: họ thường xem nhẹ danh lợi, không ham tranh giành.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_LIMIT_CORE

Có Thiên Cơ tọa thủ cung Phúc Đức ở Tý, người này dễ lao tâm khổ tứ, khó yên lòng. Khi biết dành cho mình những khoảng nghỉ thật sự, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_LIMIT_CORE

Với Vũ Khúc và Thất Sát đồng cung Phúc Đức tại Mão, người này dễ lo trước những điều chưa tới. Nếu biết dành cho mình những khoảng nghỉ thật sự, phần khó ấy sẽ bớt nặng đi nhiều.

Có điều, người mang tổ hợp này cũng dễ có những bất hòa trong nhà. Nhìn từ cung Mệnh, chủ nhân lá số thường an nhiên trước biến động.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_LIMIT_CORE

Không có chính tinh, cung Phúc Đức tại Tý được đọc qua Địa Không đóng tại đó; người mang lá số này dễ phải lo toan nhiều về chuyện tiền nong, và cũng dễ chịu những thăng trầm hơn người cùng cảnh. Khi biết tích lũy đều đặn thay vì mong một lần đổi đời, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

Từ phía cung Mệnh, đương số thường sống thanh đạm, ít đòi hỏi.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Với Thiên Cơ và Thiên Lương cùng ở cung Phúc Đức tại Tuất, đương số thường đến muộn mà chắc; những gì người này gieo khi trẻ thường nở vào nửa sau cuộc đời.

### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Với Tham Lang ở cung Phúc Đức tại Ngọ, người này thường gặp nhiều điều tốt lành hơn người; những lúc khó, đương số thường gặp được người giúp hay một lối ra bất ngờ. Thế nhưng, người mang tổ hợp này cũng dễ lo trước những điều chưa tới. Điều đọng lại sau tất cả là phúc phần sẵn có; biết phân biệt điều mình lo được và điều không là cách để điều bất lợi không đi đến cùng.

Ngược lại, chủ nhân lá số cũng dễ có những bất hòa trong nhà.
