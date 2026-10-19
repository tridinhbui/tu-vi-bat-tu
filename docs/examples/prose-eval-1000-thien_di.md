# Đánh giá văn đọc chương thien_di trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter thien_di` (prose prose-0.2.0, knowledge `4db446cf1b5653fc`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 0 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 (mọi lá số, kể cả chương trống) | 85.1% | ≥ 95% |
| Như trên, chỉ tính chương có từ 3 câu (831 lá số) | 91.1% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0.001 / 0.027 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “những khúc” 4.5% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “về cung” 9.5% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.101 | ≤ 0.35 |
| Entropy phân bố schema | 1.894 / log(11) = 2.398 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 72.98 ms / 75.98 ms | p95 < 30 ms |

Schema: S_EDGE_LATE_ELABORATE 255, S_DOUBLE_EDGE 229, S_VCD_BORROW 208, S_QUIET_STRENGTH 128, S_SATELLITE_WEAVE 50, S_LIMIT_CORE 42, S_TIMING_ARC 31, S_TIMING_FIRST 24, S_TURN_THEN_TENSION 20, S_TENSION_BRIDGE 12, S_TENSION_CORE 1



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_LIMIT_CORE

Riêng ở cung Thiên Di, Cự Môn đóng tại Tuất báo hiệu rằng người này dễ lao tâm khổ tứ, khó yên lòng, và cũng dễ vướng thị phi, tranh cãi vì lời nói thẳng. Nếu biết dành cho mình những khoảng nghỉ thật sự, phần khó ấy sẽ bớt nặng đi nhiều.

Bù lại, người mang tổ hợp này cũng dễ bị dèm pha, quấy nhiễu nơi xa.

### {"year":1943,"month":2,"day":24,"hour":20,"minute":30,"gender":"female","to_year":2026} · S_VCD_BORROW

Không có chính tinh, cung Thiên Di tại Tuất được đọc qua Hữu Bật đóng tại đó; người này thường có người giúp đúng lúc. Vốn liếng đáng kể nhất là những mối quan hệ nâng đỡ.

Những khúc quanh quan trọng của người mang tổ hợp này thường có bàn tay người khác; song song với điều ấy, họ thường phát nhanh nhưng cũng dễ lắng nhanh.

### {"year":1999,"month":1,"day":19,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Khi Phá Quân làm chủ cung Thiên Di ở Tuất, người mang lá số này thường có những lúc lên rất mạnh, cần biết giữ; điều quan trọng với đương số không phải là có được mà là giữ được. Tuy nhiên, người này cũng dễ bị dèm pha, quấy nhiễu nơi xa. Khi biết giữ người tin cậy bên cạnh khi làm việc ở nơi lạ, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Về cung Thiên Di, nơi Tử Vi đóng tại Ngọ, người này có người giúp, nhưng không nhiều; ở chiều ngược lại, người này cũng dễ lo trước những điều chưa tới. Khi đã biết dành cho mình những khoảng nghỉ thật sự, chỗ yếu cũng thành chỗ rèn mình.

Thêm vào đó, chủ nhân lá số thường lập nghiệp ở nơi xa.

### {"year":1996,"month":10,"day":14,"hour":13,"minute":15,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Khi Thiên Đồng làm chủ cung Thiên Di ở Dậu, người mang lá số này thường có người giúp đúng lúc; chỉ có điều, họ cũng dễ bị dèm pha, quấy nhiễu nơi xa. Những khúc quanh quan trọng của người mang tổ hợp này thường có bàn tay người khác. Bởi vậy, điều đáng quý ở lá số này là những mối quan hệ nâng đỡ; khi đã biết chuẩn bị kỹ trước mỗi chuyến đi xa, chỗ yếu cũng thành chỗ rèn mình.

Hơn nữa, đương số thường gắn với những đổi thay về chỗ ở và công việc.

### {"year":1995,"month":5,"day":15,"hour":19,"minute":30,"gender":"male","to_year":2026} · S_TIMING_FIRST

Đến cung Thiên Di tại Sửu, với Liêm Trinh và Thất Sát cùng tọa thủ, người mang lá số này thường kiếm tiền không khó, đời sống đầy đủ. Về nhịp đời, họ thường phải đợi đến độ chín mới rực rỡ. Chủ nhân lá số thường có điều kiện vật chất tốt hơn mức trung bình. Có một mặt khác cần thấy: đương số cũng dễ gặp bất trắc, lao nhọc khi ra ngoài. Xét cho cùng, chỗ mạnh của lá số nằm ở sự đầy đủ về vật chất; nếu biết giữ người tin cậy bên cạnh khi làm việc ở nơi lạ, phần khó ấy sẽ bớt nặng đi nhiều.

Cùng một mạch ấy, người này thường gắn với những đổi thay về chỗ ở và công việc, lại phát huy khi được hoạt động thay vì ngồi yên.

### {"year":1997,"month":6,"day":6,"hour":11,"minute":45,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Đến cung Thiên Di tại Ngọ, với Cự Môn tọa thủ, người mang lá số này thường kiếm tiền không khó, đời sống đầy đủ. Chủ nhân lá số thường có điều kiện vật chất tốt hơn mức trung bình. Bù lại, người này cũng dễ lo trước những điều chưa tới, và cũng dễ để lời nói đi trước suy nghĩ, gây những bất đồng không đáng có. Cái nên giữ gìn nhất ở đây là sự đầy đủ về vật chất; càng biết dành cho mình những khoảng nghỉ thật sự, người này càng phát huy được những gì mình vốn có.

Đồng thời, đương số thường giữ được sự bình thản trong lòng, lại lập nghiệp ở nơi xa, nhưng cũng dễ bị dèm pha, quấy nhiễu nơi xa.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Có Thái Âm tọa thủ cung Thiên Di ở Thìn, người mang lá số này thường có người giúp đúng lúc; đương số biết quý những người đã giúp mình, nên người giúp cũng ở lại lâu. Nhưng ở Thìn, Thái Âm rơi vào hãm địa, nên họ dễ để lời nói đi trước suy nghĩ, gây những bất đồng không đáng có. Xét cho cùng, chỗ mạnh của lá số nằm ở quý nhân bên cạnh; khi đã biết chọn lúc nói và lúc im lặng, chỗ yếu cũng thành chỗ rèn mình.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Có Tử Vi và Phá Quân cùng tọa thủ cung Thiên Di ở Mùi, đương số thường gặp vận thuận theo từng đợt chứ không đều; điều quan trọng với người mang tổ hợp này không phải là có được mà là giữ được. Nhưng họ cũng dễ thấy âu lo, hoang mang khi phải đi xa. Có Kình Dương ở vào thế đắc đi cùng, tài lộc hiện ra rõ hơn. Càng biết giữ người tin cậy bên cạnh khi làm việc ở nơi lạ, người này càng phát huy được những gì mình vốn có.

Song chủ nhân lá số cũng dễ bận lòng vì nhiều chuyện, ít khi thảnh thơi.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_VCD_BORROW

Với cung Thiên Di vô chính diệu ở Thìn, người mang lá số này thường có những lúc lên rất mạnh, cần biết giữ.

Những cơ hội đến với họ thường đột ngột và qua cũng nhanh.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_VCD_BORROW

Tại Dần, cung Thiên Di không có chính tinh; với Thiên Việt đóng ở đây, người này thường được người trên tin cậy. Điều đọng lại sau tất cả là những mối quan hệ nâng đỡ.

Những khúc quanh quan trọng của đương số thường có bàn tay người khác; đồng thời, họ thường phát nhanh nhưng cũng dễ lắng nhanh.

### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_TIMING_FIRST

Nhìn vào Thất Sát ở cung Thiên Di tại Tuất, có thể thấy người mang lá số này thường di chuyển nhiều, dễ rời xa nơi gốc; nhịp đời của người này cũng có điểm riêng: người này thường phải đợi đến độ chín mới rực rỡ. Nơi đương số thành công không nhất thiết là nơi mình sinh ra. Mặt khác, ở Tuất, Thất Sát đứng thế hãm, nên chủ nhân lá số dễ bị hiểu lầm vì cách nói sắc cạnh. Địa Không đóng cùng cung làm tính cách thêm phần căng: người này dễ thấy âu lo, hoang mang khi phải đi xa. Và nếu biết dùng lời nói để thấu hiểu thay vì để hơn thua, mặt khó của lá số sẽ trở thành bài học hơn là trở ngại.
