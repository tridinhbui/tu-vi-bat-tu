# Đánh giá văn đọc chương tat_ach trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter tat_ach` (prose prose-0.2.0, knowledge `4db446cf1b5653fc`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 22 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 (mọi lá số, kể cả chương trống) | 84.4% | ≥ 95% |
| Như trên, chỉ tính chương có từ 3 câu (646 lá số) | 96.4% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0 / 0.028 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “khi có” 4.3% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “về cung” 9.9% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.086 | ≤ 0.35 |
| Entropy phân bố schema | 1.87 / log(12) = 2.485 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 73.97 ms / 77.03 ms | p95 < 30 ms |

Schema: S_QUIET_STRENGTH 370, S_VCD_BORROW 165, S_SATELLITE_WEAVE 124, S_EDGE_LATE_ELABORATE 112, S_DOUBLE_EDGE 88, S_LIMIT_CORE 45, S_PLAIN 40, S_TIMING_ARC 35, S_TIMING_FIRST 13, S_TENSION_CORE 6, S_TENSION_BRIDGE 1, S_TURN_THEN_TENSION 1



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Khi Thiên Tướng làm chủ cung Tật Ách ở Hợi, người này thường hưởng phúc vào quãng sau của cuộc đời; tuổi trẻ của họ là quãng gieo; quãng gặt đến về sau. Không chỉ thế, đương số thường ít khi phải nằm lâu vì bệnh.

### {"year":1943,"month":2,"day":24,"hour":20,"minute":30,"gender":"female","to_year":2026} · S_SATELLITE_WEAVE

Ở cung Tật Ách, Thiên Phủ đóng tại Hợi cho thấy người mang lá số này thường thuận dần về sau, càng lớn tuổi càng vững; ngoài ra, họ thường ít gặp bệnh nặng, có ốm cũng dễ gặp thầy thuốc. Những gì đương số gieo khi trẻ thường nở vào nửa sau cuộc đời.

Nhìn từ cung Mệnh, người này thường có phúc thọ.

### {"year":1999,"month":1,"day":19,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Có Thiên Đồng tọa thủ cung Tật Ách ở Hợi, người mang lá số này thường hưởng phúc vào quãng sau của cuộc đời; tuổi trẻ của người này là quãng gieo; quãng gặt đến về sau. Có điều, họ cũng dễ gặp tai nạn, bệnh tật cần đề phòng. Nếu biết đề phòng sớm trước những dấu hiệu nhỏ, phần khó ấy sẽ bớt nặng đi nhiều.

Từ phía cung Mệnh, chủ nhân lá số thường được hưởng tuổi già an ổn.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_VCD_BORROW

Không có chính tinh, cung Tật Ách ở Mùi mượn Thiên Đồng và Cự Môn từ phía đối diện; người mang lá số này thường ít khi phải nằm lâu vì bệnh. Về nhịp đời, người mang tổ hợp này thường thuận dần về sau, càng lớn tuổi càng vững. Xét cho cùng, chỗ mạnh của lá số nằm ở sự may mắn về thể chất.

Những trận ốm của họ hiếm khi để lại hậu quả nặng.

### {"year":1996,"month":10,"day":14,"hour":13,"minute":15,"gender":"male","to_year":2026} · S_SATELLITE_WEAVE

Riêng ở cung Tật Ách, Vũ Khúc đóng tại Tuất báo hiệu rằng đương số thường có quãng sau của đời vững vàng hơn quãng đầu; đồng thời, họ thường ít gặp bệnh nặng, có ốm cũng dễ gặp thầy thuốc. Những gì chủ nhân lá số gieo khi trẻ thường nở vào nửa sau cuộc đời.

Nhìn từ cung Mệnh, đương số thường có phúc thọ.

### {"year":1995,"month":5,"day":15,"hour":19,"minute":30,"gender":"male","to_year":2026} · S_VCD_BORROW

Với cung Tật Ách vô chính diệu ở Dần, người mang lá số này thường ít gặp bệnh nặng, có ốm cũng dễ gặp thầy thuốc; xét theo thời gian, họ thường có quãng sau của đời vững vàng hơn quãng đầu. Bởi vậy, điều đáng quý ở lá số này là sự may mắn về thể chất.

Những trận ốm của đương số hiếm khi để lại hậu quả nặng.

### {"year":1997,"month":6,"day":6,"hour":11,"minute":45,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Về cung Tật Ách, nơi Thiên Tướng đóng tại Mùi, người này thường hưởng phúc vào quãng sau của cuộc đời; tuổi trẻ của đương số là quãng gieo; quãng gặt đến về sau. Ngoài ra, họ thường đau ốm phần nhiều nhẹ, mau lành.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_QUIET_STRENGTH

Khi Liêm Trinh và Tham Lang cùng làm chủ cung Tật Ách ở Tỵ, người này thường thuận dần về sau, càng lớn tuổi càng vững. Càng về già, đương số càng có điều kiện sống thong thả.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_LIMIT_CORE

Tại Thân, cung Tật Ách không có chính tinh, nên được đọc qua Thiên Đồng và Thiên Lương từ cung đối diện; người này đôi khi gặp bệnh, nhưng không đến mức nặng. Nhịp đời của người này cũng có điểm riêng: họ thường thuận dần về sau, càng lớn tuổi càng vững. Khi đã biết đề phòng sớm trước những dấu hiệu nhỏ, chỗ yếu cũng thành chỗ rèn mình.

Những trận ốm của người này hiếm khi để lại hậu quả nặng. Cung Mệnh cũng góp một nét vào chuyện này: chủ nhân lá số thường sống lâu, sức bền tốt.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_SATELLITE_WEAVE

Về cung Tật Ách, nơi Thiên Phủ đóng tại Tỵ, người này thường thuận dần về sau, càng lớn tuổi càng vững; song song với điều ấy, chủ nhân lá số thường ít khi phải nằm lâu vì bệnh. Nửa sau cuộc đời của người mang tổ hợp này thường êm hơn nửa đầu.

Soi sang cung Mệnh, lại thấy người này thường sống lâu, sức bền tốt.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_LIMIT_CORE

Khi Liêm Trinh và Phá Quân cùng làm chủ cung Tật Ách ở Mão, người mang lá số này dễ phải chịu những trận ốm khó lường. Khi biết giữ sức khỏe đều đặn thay vì đợi đến lúc cần, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_PLAIN

Cung Mệnh cũng góp một nét vào chuyện này: người mang tổ hợp này thường được hưởng tuổi già an ổn.
