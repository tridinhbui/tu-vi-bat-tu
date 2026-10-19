# Đánh giá văn đọc chương no_boc trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter no_boc` (prose prose-0.2.0, knowledge `4db446cf1b5653fc`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 142 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 (mọi lá số, kể cả chương trống) | 64.5% | ≥ 95% |
| Như trên, chỉ tính chương có từ 3 câu (469 lá số) | 94.5% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0 / 0.02 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “khi cần” 5.6% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “” 14.2% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.106 | ≤ 0.35 |
| Entropy phân bố schema | 1.833 / log(8) = 2.079 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 73.52 ms / 76.48 ms | p95 < 30 ms |

Schema: S_QUIET_STRENGTH 254, S_LIMIT_CORE 193, S_PLAIN 155, S_EDGE_LATE_ELABORATE 148, S_DOUBLE_EDGE 143, S_SATELLITE_WEAVE 60, S_VCD_BORROW 46, S_TENSION_BRIDGE 1



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Với Tử Vi và Tham Lang cùng ở cung Nô Bộc tại Dậu, người này có người giúp, nhưng sự gắn bó còn tùy lúc; đổi lại, người mang tổ hợp này cũng dễ gặp bạn bè, người dưới không thật lòng. Khi đã biết giữ ân oán rạch ròi để người dưới không có cớ oán, chỗ yếu cũng thành chỗ rèn mình.

### {"year":1943,"month":2,"day":24,"hour":20,"minute":30,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Về cung Nô Bộc, nơi Liêm Trinh và Phá Quân đồng cung tại Dậu, đương số thường làm ra của bằng mồ hôi; dẫu vậy, ở Dậu, Liêm Trinh đứng thế hãm, nên người mang tổ hợp này dễ gặp bạn bè, người dưới không thật lòng. Mỗi đồng chủ nhân lá số có được đều gắn với công sức. Biết chọn người cẩn trọng trước khi giao việc lớn là cách để điều bất lợi không đi đến cùng.

Ở cung Mệnh, điều này cũng hiện ra: người này thường được người trên tin cậy.

### {"year":1999,"month":1,"day":19,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_PLAIN



### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_PLAIN



### {"year":1996,"month":10,"day":14,"hour":13,"minute":15,"gender":"male","to_year":2026} · S_LIMIT_CORE

Nhìn vào Thất Sát ở cung Nô Bộc tại Thân, có thể thấy người này dễ bị người mình nâng đỡ quay lưng. Và nếu biết chọn người cẩn trọng trước khi giao việc lớn, mặt khó của lá số sẽ trở thành bài học hơn là trở ngại.

### {"year":1995,"month":5,"day":15,"hour":19,"minute":30,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Về cung Nô Bộc, nơi Thiên Lương đóng tại Tý, người này thường có nhiều người theo, một tiếng gọi nhiều người đáp; quanh đương số thường có một vòng người quen rộng. Song song với điều ấy, người này thường có bạn bè và người dưới quyền tận tâm. Nếu phải gọi tên điểm tựa, đó là khả năng quy tụ người khác và những người tận tâm bên cạnh.

Soi sang cung Mệnh, lại thấy chủ nhân lá số thường được quý nhân nâng đỡ.

### {"year":1997,"month":6,"day":6,"hour":11,"minute":45,"gender":"female","to_year":2026} · S_LIMIT_CORE

Ở Tỵ, Liêm Trinh rơi vào hãm địa, nên người có Liêm Trinh ở cung Nô Bộc dễ gặp bạn bè, người dưới không thật lòng. Nếu biết giữ ân oán rạch ròi để người dưới không có cớ oán, phần khó ấy sẽ bớt nặng đi nhiều.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Xét cung Nô Bộc tại Mão, nơi Thiên Phủ tọa thủ, đương số thường đông bạn bè, giao thiệp rộng; quanh chủ nhân lá số thường có một vòng người quen rộng. Bù lại, người mang tổ hợp này cũng dễ bị người mình nâng đỡ quay lưng. Bởi vậy, điều đáng quý ở lá số này là khả năng quy tụ người khác; và nếu biết giữ ân oán rạch ròi để người dưới không có cớ oán, mặt khó của lá số sẽ trở thành bài học hơn là trở ngại.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Ở cung Nô Bộc, Thiên Cơ đóng tại Ngọ cho thấy đương số thường được người giúp việc, cộng sự trung thành; những người làm việc cùng đương số thường ở lại lâu và giữ chữ tín. Thêm vào đó, người này thường kết giao thuận lợi, quen biết nhiều nơi, lại làm ra của bằng mồ hôi. Điều đọng lại sau tất cả là sự trung thành của người cùng làm và vòng quan hệ rộng.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Xét cung Nô Bộc tại Mão, nơi Liêm Trinh và Phá Quân đồng cung, người này thường gặp những người theo mình đến cùng; đổi lại, ở Mão, Liêm Trinh rơi vào hãm địa, nên đương số dễ gặp bạn bè, người dưới không thật lòng. Khi cần người đỡ một tay, người này ít khi phải tìm xa. Vốn liếng đáng kể nhất là những người tận tâm bên cạnh; càng biết chọn người cẩn trọng trước khi giao việc lớn, người này càng phát huy được những gì mình vốn có.

Một nét khác đến từ cung Mệnh: họ thường được quý nhân nâng đỡ.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_PLAIN



### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_SATELLITE_WEAVE

Với Thái Dương và Thiên Lương đồng cung Nô Bộc tại Dậu, người mang lá số này thường kết giao thuận lợi, quen biết nhiều nơi. Đồng thời, chủ nhân lá số thường gặp những người theo mình đến cùng. Việc gì cần nhiều người, người mang tổ hợp này dễ tập hợp được. Bởi vậy, điều đáng quý ở lá số này không chỉ là vòng quan hệ rộng mà còn là sự trung thành của người cùng làm.
