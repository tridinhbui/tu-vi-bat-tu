# Đánh giá văn đọc chương thien_di trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter thien_di` (prose prose-0.2.0, knowledge `b301f85298e6bb62`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 0 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 | 69.7% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0.001 / 0.027 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “cung thiên” 7.0% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “cung thiên” 27.3% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.098 | ≤ 0.35 |
| Entropy phân bố schema | 1.899 / log(11) = 2.398 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 43.47 ms / 51.9 ms | p95 < 30 ms |

Schema: S_EDGE_LATE_ELABORATE 255, S_DOUBLE_EDGE 229, S_VCD_BORROW 208, S_QUIET_STRENGTH 122, S_SATELLITE_WEAVE 56, S_LIMIT_CORE 42, S_TIMING_ARC 31, S_TIMING_FIRST 24, S_TURN_THEN_TENSION 20, S_TENSION_BRIDGE 12, S_TENSION_CORE 1



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_LIMIT_CORE

Khi Cự Môn làm chủ cung Thiên Di ở Tuất, người này dễ lao tâm khổ tứ, khó yên lòng, và cũng dễ vướng thị phi, tranh cãi vì lời nói thẳng. Nếu biết dành cho mình những khoảng nghỉ thật sự, phần khó ấy sẽ bớt nặng đi nhiều.

Bù lại, người mang tổ hợp này cũng dễ bị dèm pha, quấy nhiễu nơi xa.

### {"year":2006,"month":12,"day":9,"hour":20,"minute":15,"gender":"female","to_year":2026} · S_VCD_BORROW

Cung Thiên Di ở Mùi vô chính diệu; đương số thường phát nhanh nhưng cũng dễ lắng nhanh.

Những cơ hội đến với đương số thường đột ngột và qua cũng nhanh.

### {"year":1984,"month":6,"day":21,"hour":7,"minute":45,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Có Liêm Trinh tọa thủ cung Thiên Di ở Thân, người mang lá số này thường cần đi lại, giao tiếp nhiều mới gặp thời; ngồi một chỗ lâu, đương số dễ thấy bế tắc; đi lại nhiều lại mở ra cơ hội. Đồng thời, họ thường ra ngoài thuận lợi, dễ gặp người quý, lại được người trên tin cậy.

Cùng một mạch ấy, người mang tổ hợp này thường có những nguồn lợi bất ngờ.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Với Tử Vi ở cung Thiên Di tại Ngọ, người này có người giúp, nhưng không nhiều; ở chiều ngược lại, họ cũng dễ lo trước những điều chưa tới. Khi đã biết dành cho mình những khoảng nghỉ thật sự, chỗ yếu cũng thành chỗ rèn mình.

Thêm vào đó, người mang tổ hợp này thường lập nghiệp ở nơi xa.

### {"year":2017,"month":1,"day":9,"hour":15,"minute":15,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Cung Thiên Di có bộ Liêm Trinh và Tham Lang đóng tại Hợi cho thấy người mang lá số này thường hợp với việc năng ra ngoài, hoạt động liên tục; đổi lại, người mang tổ hợp này cũng dễ bị dèm pha, quấy nhiễu nơi xa. Với người này, cơ hội thường nằm ở những nơi phải tự tìm đến. Khi đã biết chuẩn bị kỹ trước mỗi chuyến đi xa, chỗ yếu cũng thành chỗ rèn mình.

Thêm vào đó, chủ nhân lá số thường có những nguồn lợi bất ngờ, lại gắn với những đổi thay về chỗ ở và công việc, mà cũng dễ liều lĩnh, làm trước nghĩ sau.

### {"year":2017,"month":7,"day":9,"hour":0,"minute":15,"gender":"male","to_year":2026} · S_SATELLITE_WEAVE

Xét cung Thiên Di tại Sửu, nơi Liêm Trinh và Thất Sát đồng cung, người mang lá số này thường có nguồn thu rộng mở. Lại nữa, người này thường di chuyển nhiều, dễ rời xa nơi gốc, lại cần đi lại, giao tiếp nhiều mới gặp thời. Tiền bạc đến với chủ nhân lá số không quá khó khăn. Rốt lại, cái vốn quý của người này nằm ở đường tài lộc.

Đi cùng nét này, đương số thường ra ngoài thuận lợi, dễ gặp người quý.

### {"year":1935,"month":4,"day":4,"hour":12,"minute":15,"gender":"female","to_year":2026} · S_VCD_BORROW

Cung Thiên Di tại Thìn không có chính tinh; với Kình Dương đóng ở đây, đương số thường có tài lộc thuận lợi. Bởi vậy, điều đáng quý ở lá số này là sự đầy đủ về vật chất.

Người mang tổ hợp này thường có điều kiện vật chất tốt hơn mức trung bình. Hơn nữa, đương số thường gắn với những đổi thay về chỗ ở và công việc, lại gặp may khi đi xa, ở nơi khác dễ phát đạt.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Khi Thái Âm làm chủ cung Thiên Di ở Thìn, người mang lá số này thường có người giúp đúng lúc; đương số biết quý những người đã giúp mình, nên người giúp cũng ở lại lâu. Nhưng ở Thìn, Thái Âm rơi vào hãm địa, nên họ dễ để lời nói đi trước suy nghĩ, gây những bất đồng không đáng có. Xét cho cùng, chỗ mạnh của lá số nằm ở quý nhân bên cạnh; khi đã biết chọn lúc nói và lúc im lặng, chỗ yếu cũng thành chỗ rèn mình.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Khi Tử Vi và Phá Quân cùng làm chủ cung Thiên Di ở Mùi, đương số thường gặp vận thuận theo từng đợt chứ không đều; điều quan trọng với chủ nhân lá số không phải là có được mà là giữ được. Dẫu vậy, người này cũng dễ thấy âu lo, hoang mang khi phải đi xa. Có Kình Dương ở vào thế đắc đi cùng, tài lộc hiện ra rõ hơn. Càng biết giữ người tin cậy bên cạnh khi làm việc ở nơi lạ, người này càng phát huy được những gì mình vốn có.

Thế nhưng, họ cũng dễ bận lòng vì nhiều chuyện, ít khi thảnh thơi.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_VCD_BORROW

Với cung Thiên Di vô chính diệu ở Thìn, người mang lá số này thường có những lúc lên rất mạnh, cần biết giữ.

Những cơ hội đến với người mang tổ hợp này thường đột ngột và qua cũng nhanh.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_VCD_BORROW

Cung Thiên Di tại Dần không có chính tinh; với Thiên Việt đóng ở đây, người này thường được người trên tin cậy. Điều đọng lại sau tất cả là những mối quan hệ nâng đỡ.

Những khúc quanh quan trọng của đương số thường có bàn tay người khác. Đồng thời, họ thường phát nhanh nhưng cũng dễ lắng nhanh.

### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_TIMING_FIRST

Cung Thiên Di có Thất Sát đóng tại Tuất cho thấy người mang lá số này thường di chuyển nhiều, dễ rời xa nơi gốc; nhịp đời của người này cũng có điểm riêng: người này thường phải đợi đến độ chín mới rực rỡ. Nơi đương số thành công không nhất thiết là nơi mình sinh ra. Mặt khác, ở Tuất, Thất Sát đứng thế hãm, nên chủ nhân lá số dễ bị hiểu lầm vì cách nói sắc cạnh. Địa Không đóng cùng cung làm tính cách thêm phần căng: người này dễ thấy âu lo, hoang mang khi phải đi xa. Và nếu biết dùng lời nói để thấu hiểu thay vì để hơn thua, mặt khó của lá số sẽ trở thành bài học hơn là trở ngại.
