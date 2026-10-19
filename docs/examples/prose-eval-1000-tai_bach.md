# Đánh giá văn đọc chương tai_bach trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter tai_bach` (prose prose-0.2.0, knowledge `71a99fbcd138009d`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 71 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 | 43.0% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0 / 0.028 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “càng biết” 4.0% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “riêng ở” 7.8% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.074 | ≤ 0.35 |
| Entropy phân bố schema | 2.103 / log(12) = 2.485 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 65.9 ms / 69.65 ms | p95 < 30 ms |

Schema: S_QUIET_STRENGTH 219, S_LIMIT_CORE 169, S_DOUBLE_EDGE 164, S_EDGE_LATE_ELABORATE 151, S_PLAIN 89, S_VCD_BORROW 80, S_TIMING_ARC 48, S_TURN_THEN_TENSION 24, S_TENSION_BRIDGE 19, S_TIMING_FIRST 16, S_SATELLITE_WEAVE 15, S_TENSION_CORE 6



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_SATELLITE_WEAVE

Nhìn vào Thiên Lương ở cung Tài Bạch tại Tý, có thể thấy đương số có tài lộc, dù chuyện tiền bạc vẫn khiến phải bận tâm. Cũng vậy, đương số thường giữ của kỹ, ít khi tiêu hoang.

### {"year":1943,"month":2,"day":24,"hour":20,"minute":30,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Với Thiên Đồng và Thái Âm cùng ở cung Tài Bạch tại Tý, người mang lá số này có lộc, nhưng phần giữ được không nhiều; chỉ có điều, đương số cũng dễ chật vật về sinh kế. Nhịp đời của người này cũng có điểm riêng: người mang tổ hợp này thường phải đợi đến độ chín mới rực rỡ. Và nếu biết tích lũy đều đặn thay vì mong một lần đổi đời, mặt khó của lá số sẽ trở thành bài học hơn là trở ngại.

Không chỉ thế, họ thường chặt chẽ trong chi tiêu. Một nét khác đến từ cung Mệnh: đương số thường chi tiêu phóng khoáng.

### {"year":1999,"month":1,"day":19,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Nhìn vào bộ Vũ Khúc và Thiên Phủ ở cung Tài Bạch tại Tý, có thể thấy người này có lộc, nhưng phần giữ được không nhiều.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_LIMIT_CORE

Ở Thân, Phá Quân rơi vào hãm địa, nên người có Phá Quân ở cung Tài Bạch dễ kiếm được nhưng khó giữ, của cải dễ trôi đi. Biết biết giữ trước khi mở rộng là cách để điều bất lợi không đi đến cùng.

### {"year":1996,"month":10,"day":14,"hour":13,"minute":15,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Với Thái Dương ở cung Tài Bạch tại Hợi, đương số kiếm được tiền, song không dư dả như mong; ngược lại, ở Hợi, Thái Dương đứng thế hãm, nên chủ nhân lá số dễ phải lo toan nhiều về chuyện tiền nong. Biết tích lũy đều đặn thay vì mong một lần đổi đời là cách để điều bất lợi không đi đến cùng.

Một nét khác đến từ cung Mệnh: đương số thường tính toán cẩn thận với đồng tiền.

### {"year":1995,"month":5,"day":15,"hour":19,"minute":30,"gender":"male","to_year":2026} · S_VCD_BORROW

Tại Mão, cung Tài Bạch không có chính tinh; với Mộ đóng ở đây, người này thường chặt chẽ trong chi tiêu. Bù lại, người mang tổ hợp này cũng dễ chật vật về sinh kế.

Đồng tiền qua tay người này thường được dùng đúng việc.

### {"year":1997,"month":6,"day":6,"hour":11,"minute":45,"gender":"female","to_year":2026} · S_TIMING_ARC

Về cung Tài Bạch, nơi Thiên Đồng và Thiên Lương đồng cung tại Thân, người này kiếm được tiền, song không dư dả như mong. Nhịp đời của người này cũng có điểm riêng: đương số thường thành đạt muộn, phần nhiều sau tuổi ba mươi.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Nhìn vào Cự Môn ở cung Tài Bạch tại Ngọ, có thể thấy đương số có chí tự lập, dù cần thời gian; ở chiều ngược lại, người này cũng dễ rơi vào cảnh eo hẹp, khó dư dả. Biết đặt giá trị của mình ở chỗ khác ngoài tiền bạc là cách để điều bất lợi không đi đến cùng.

Không chỉ thế, chủ nhân lá số thường chặt chẽ trong chi tiêu.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_LIMIT_CORE

Khi Thiên Phủ làm chủ cung Tài Bạch ở Dậu, người này dễ hao tán vì những khoản chi bất ngờ. Khi biết biết giữ trước khi mở rộng, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Khi Thiên Đồng và Thái Âm cùng làm chủ cung Tài Bạch ở Ngọ, đương số thường có nguồn thu rộng mở; tiền bạc đến với chủ nhân lá số không quá khó khăn. Dẫu vậy, người này cũng dễ hao tán vì những khoản chi bất ngờ; xét theo thời gian, đương số thường có công danh đến chậm nhưng bền. Xét cho cùng, chỗ mạnh của lá số nằm ở đường tài lộc; biết dành riêng một phần không động đến là cách để điều bất lợi không đi đến cùng.

Cũng vậy, người mang tổ hợp này thường tự tay làm nên cơ nghiệp, lại gặp tiền đến không báo trước. Cung Mệnh cũng góp một nét vào chuyện này: chủ nhân lá số thường rộng rãi, không tiếc tiền với người khác.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_PLAIN



### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Ở cung Tài Bạch, Tử Vi đóng tại Tý cho thấy đương số kiếm được tiền, song không dư dả như mong; có điều, đương số cũng dễ phải lo toan nhiều về chuyện tiền nong. Sự hiện diện của Địa Kiếp khiến mọi thứ gai góc hơn: chủ nhân lá số dễ chịu những thăng trầm hơn người cùng cảnh. Càng biết tích lũy đều đặn thay vì mong một lần đổi đời, người này càng phát huy được những gì mình vốn có.
