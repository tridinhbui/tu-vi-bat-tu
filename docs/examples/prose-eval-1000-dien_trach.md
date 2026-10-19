# Đánh giá văn đọc chương dien_trach trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter dien_trach` (prose prose-0.2.0, knowledge `71a99fbcd138009d`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 171 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 | 50.2% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0.001 / 0.027 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “nền tảng” 4.7% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “” 17.1% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.076 | ≤ 0.35 |
| Entropy phân bố schema | 1.804 / log(12) = 2.485 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 65.97 ms / 68.73 ms | p95 < 30 ms |

Schema: S_QUIET_STRENGTH 365, S_PLAIN 171, S_SATELLITE_WEAVE 136, S_DOUBLE_EDGE 123, S_EDGE_LATE_ELABORATE 87, S_VCD_BORROW 70, S_TIMING_ARC 28, S_LIMIT_CORE 8, S_TENSION_CORE 6, S_TIMING_FIRST 3, S_TENSION_BRIDGE 2, S_TURN_THEN_TENSION 1



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_SATELLITE_WEAVE

Có Thiên Phủ tọa thủ cung Điền Trạch ở Mùi, đương số thường tạo dựng được tài sản lớn. Bên cạnh đó, người này thường có tài lộc thuận lợi. Nền tảng vật chất của đương số là chỗ dựa lâu dài. Rốt lại, cái vốn quý nhất của người này nằm ở chốn an cư, đi cùng đường tài lộc.

### {"year":1943,"month":2,"day":24,"hour":20,"minute":30,"gender":"female","to_year":2026} · S_PLAIN



### {"year":1999,"month":1,"day":19,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_PLAIN



### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_SATELLITE_WEAVE

Xét cung Điền Trạch tại Mão, nơi Thái Dương và Thiên Lương đồng cung, đương số thường được hưởng nền tảng vật chất tốt. Đi cùng nét này, chủ nhân lá số thường hưởng được phần di sản của gia đình. Nền tảng vật chất của đương số là chỗ dựa lâu dài. Xét cho cùng, chỗ mạnh của lá số nằm ở chốn an cư, rồi đến tổ nghiệp.

### {"year":1996,"month":10,"day":14,"hour":13,"minute":15,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Riêng ở cung Điền Trạch, bộ Liêm Trinh và Thiên Tướng tại Ngọ báo hiệu rằng người mang lá số này thường có cơ nghiệp, nhà cửa vững. Đương số có điều kiện để an cư. Ở chiều ngược lại, người mang tổ hợp này cũng dễ chao đảo về cơ nghiệp, nhà cửa hay đổi thay. Điều đọng lại sau tất cả là cơ nghiệp vững; càng biết xây nền chậm mà chắc, người này càng phát huy được những gì mình vốn có.

### {"year":1995,"month":5,"day":15,"hour":19,"minute":30,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Có Cự Môn tọa thủ cung Điền Trạch ở Tuất, người này giữ được nhà cửa, dù không lớn; đổi lại, ở Tuất, Cự Môn ở vào thế hãm, nên chủ nhân lá số dễ lận đận, việc gì cũng phải qua nhiều lần mới thành. Khi biết tích lũy từng bước thay vì mong một bước tới đích, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

### {"year":1997,"month":6,"day":6,"hour":11,"minute":45,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Với Thiên Phủ ở cung Điền Trạch tại Mão, đương số thường được hưởng nền tảng vật chất tốt; nền tảng vật chất của người mang tổ hợp này là chỗ dựa lâu dài. Xét cho cùng, chỗ mạnh của lá số nằm ở chốn an cư.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_TENSION_BRIDGE

Có Tử Vi và Phá Quân cùng tọa thủ cung Điền Trạch ở Sửu, đương số thường có cơ nghiệp, nhà cửa vững. Nền tảng vật chất của họ là chỗ dựa lâu dài. Hóa Quyền ở Tử Vi thêm cho người này sự thuận lợi chung. Dẫu vậy, người mang tổ hợp này cũng dễ chao đảo về cơ nghiệp, nhà cửa hay đổi thay. Rốt lại, cái vốn quý nhất của người này nằm ở chốn an cư, đi cùng phúc phần sẵn có; càng biết giữ tài sản bằng sự cẩn trọng hơn là may mắn, người này càng phát huy được những gì mình vốn có.

Song song với điều ấy, người này thường có nhà của riêng nhờ sức mình.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_SATELLITE_WEAVE

Với Thái Dương ở cung Điền Trạch tại Thìn, đương số thường hưởng được phần di sản của gia đình. Ngoài ra, họ thường có nguồn thu rộng mở. Người mang tổ hợp này có điểm tựa vật chất từ gia đình. Rốt lại, cái vốn quý nhất của người này nằm ở điểm tựa từ đời trước, đi cùng đường tài lộc.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_VCD_BORROW

Tại Sửu, cung Điền Trạch không có chính tinh; với Mộ đóng ở đây, đương số thường tính toán cẩn thận với đồng tiền.

Người mang tổ hợp này nghĩ hai lần trước mỗi khoản chi lớn.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Riêng ở cung Điền Trạch, bộ Tử Vi và Thất Sát tại Hợi báo hiệu rằng người mang lá số này có cơ nghiệp ở mức vừa.

### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Về cung Điền Trạch, nơi Thiên Đồng và Cự Môn đồng cung tại Mùi, đương số thường có quãng sau của đời vững vàng hơn quãng đầu; những gì đương số gieo khi trẻ thường nở vào nửa sau cuộc đời. Bù lại, họ cũng dễ gặp nhiều vất vả, phải tự mình chống đỡ. Khi đã biết coi mỗi lần vấp là một lần rèn mình, chỗ yếu cũng thành chỗ rèn mình.

Bên cạnh đó, người này thường có nền nhà cửa từ ông cha để lại.
