# Đánh giá văn đọc chương phu_the trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter phu_the` (prose prose-0.2.0, knowledge `4db446cf1b5653fc`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 53 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 (mọi lá số, kể cả chương trống) | 76.3% | ≥ 95% |
| Như trên, chỉ tính chương có từ 3 câu (751 lá số) | 94.8% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0 / 0.023 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “chuyện gia” 5.4% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “nhìn vào” 10.1% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.112 | ≤ 0.35 |
| Entropy phân bố schema | 1.832 / log(7) = 1.946 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 72.58 ms / 75.91 ms | p95 < 30 ms |

Schema: S_DOUBLE_EDGE 245, S_EDGE_LATE_ELABORATE 228, S_QUIET_STRENGTH 165, S_LIMIT_CORE 119, S_SATELLITE_WEAVE 117, S_PLAIN 63, S_VCD_BORROW 63



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_PLAIN



### {"year":1943,"month":2,"day":24,"hour":20,"minute":30,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Xét cung Phu Thê tại Dần, nơi Thái Dương và Cự Môn đồng cung, người này thường có duyên đến muộn mà bền; chủ nhân lá số sẽ thấy hạnh phúc hơn khi lập gia đình lúc đã hiểu rõ mình. Bù lại, đương số cũng dễ gặp dang dở trong chuyện duyên. Nếu biết kiên nhẫn với chuyện tình cảm, phần khó ấy sẽ bớt nặng đi nhiều.

### {"year":1999,"month":1,"day":19,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_LIMIT_CORE

Với Tham Lang ở cung Phu Thê tại Dần, người này dễ gặp dang dở trong chuyện duyên. Càng biết chọn người hợp hơn là người làm mình rung động nhất, người này càng phát huy được những gì mình vốn có.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Đến cung Phu Thê tại Tuất, với Liêm Trinh và Thiên Phủ cùng tọa thủ, đương số thường giữ được mối gắn bó lâu dài. Đổi lại, người mang tổ hợp này cũng dễ trắc trở trong tình cảm. Đương số biết cách giữ hòa khí trong nhà. Cái nên giữ gìn nhất ở đây là những quan hệ bền lâu; khi biết chọn người hợp hơn là người làm mình rung động nhất, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

### {"year":1996,"month":10,"day":14,"hour":13,"minute":15,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Ở cung Phu Thê, Thiên Cơ đóng tại Sửu cho thấy người mang lá số này thường hợp với việc kết duyên khi đã vững vàng.

Soi sang cung Mệnh, lại thấy họ thường có tình cảm êm ấm.

### {"year":1995,"month":5,"day":15,"hour":19,"minute":30,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Về cung Phu Thê, nơi Vũ Khúc và Phá Quân đồng cung tại Tỵ, đương số thường nên lập gia đình muộn; ngược lại, chủ nhân lá số cũng dễ gặp dang dở trong chuyện duyên. Chuyện gia đình với người mang tổ hợp này không nên vội. Biết chọn người hợp hơn là người làm mình rung động nhất là cách để điều bất lợi không đi đến cùng.

### {"year":1997,"month":6,"day":6,"hour":11,"minute":45,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Ở cung Phu Thê, Thái Dương đóng tại Tuất cho thấy người mang lá số này thường có duyên đến muộn mà bền; đổi lại, chủ nhân lá số cũng dễ có những mối tình không trọn. Chuyện gia đình với người mang tổ hợp này không nên vội. Và nếu biết chọn người hợp hơn là người làm mình rung động nhất, mặt khó của lá số sẽ trở thành bài học hơn là trở ngại.

Từ phía cung Mệnh, đương số thường giữ được mối gắn bó lâu dài.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_SATELLITE_WEAVE

Về cung Phu Thê, nơi Thiên Đồng và Thiên Lương đồng cung tại Thân, người này thường giữ được mối gắn bó lâu dài; ngoài ra, người mang tổ hợp này thường có duyên đến muộn mà bền, lại có duyên với người khác mình. Chủ nhân lá số biết cách giữ hòa khí trong nhà. Vốn liếng đáng kể nhất là những quan hệ bền lâu.

Cùng một mạch ấy, người phối ngẫu thường có duyên, dễ gây thiện cảm ngay từ lần gặp đầu.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_LIMIT_CORE

Trong cung Phu Thê, bộ Liêm Trinh và Tham Lang đóng tại Hợi cho thấy đương số dễ trắc trở trong tình cảm. Và nếu biết chọn người hợp hơn là người làm mình rung động nhất, mặt khó của lá số sẽ trở thành bài học hơn là trở ngại.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Với Thái Dương và Cự Môn đồng cung Phu Thê tại Thân, người này thường nên lập gia đình muộn; người mang tổ hợp này sẽ thấy hạnh phúc hơn khi lập gia đình lúc đã hiểu rõ mình. Bù lại, đương số cũng dễ gặp dang dở trong chuyện duyên. Khi đã biết kiên nhẫn với chuyện tình cảm, chỗ yếu cũng thành chỗ rèn mình.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Đến cung Phu Thê tại Ngọ, với Thiên Đồng và Thái Âm cùng tọa thủ, người mang lá số này thường có tình cảm êm ấm; những mối quan hệ của người mang tổ hợp này thường bền theo năm tháng. Cùng một mạch ấy, đương số thường gặp người bạn đời có nét riêng, lại có duyên đến muộn mà bền. Cái nên giữ gìn nhất ở đây là sự êm ấm trong tình cảm.

### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_LIMIT_CORE

Khi Phá Quân làm chủ cung Phu Thê ở Dần, người mang lá số này dễ có những mối tình không trọn. Nếu biết kiên nhẫn với chuyện tình cảm, phần khó ấy sẽ bớt nặng đi nhiều.
