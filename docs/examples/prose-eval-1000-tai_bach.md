# Đánh giá văn đọc chương tai_bach trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter tai_bach` (prose prose-0.2.0, knowledge `b301f85298e6bb62`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 71 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 | 43.0% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0 / 0.029 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “cung tài” 8.0% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “cung tài” 20.4% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.078 | ≤ 0.35 |
| Entropy phân bố schema | 2.103 / log(12) = 2.485 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 43.11 ms / 52.53 ms | p95 < 30 ms |

Schema: S_QUIET_STRENGTH 219, S_LIMIT_CORE 169, S_DOUBLE_EDGE 164, S_EDGE_LATE_ELABORATE 151, S_PLAIN 89, S_VCD_BORROW 80, S_TIMING_ARC 48, S_TURN_THEN_TENSION 24, S_TENSION_BRIDGE 19, S_TIMING_FIRST 16, S_SATELLITE_WEAVE 15, S_TENSION_CORE 6



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_SATELLITE_WEAVE

Cung Tài Bạch có Thiên Lương đóng tại Tý cho thấy đương số có tài lộc, dù chuyện tiền bạc vẫn khiến phải bận tâm. Cũng vậy, đương số thường giữ của kỹ, ít khi tiêu hoang.

### {"year":2006,"month":12,"day":9,"hour":20,"minute":15,"gender":"female","to_year":2026} · S_LIMIT_CORE

Không có chính tinh, cung Tài Bạch tại Dậu được đọc qua Địa Kiếp đóng tại đó; người này dễ rơi vào cảnh eo hẹp, khó dư dả. Biết tích lũy đều đặn thay vì mong một lần đổi đời là cách để điều bất lợi không đi đến cùng.

Có Địa Kiếp ở Mệnh, khí chất trở nên sắc cạnh hơn, và người mang tổ hợp này dễ chịu những thăng trầm hơn người cùng cảnh. Ở cung Mệnh, điều này cũng hiện ra: chủ nhân lá số thường tính toán cẩn thận với đồng tiền.

### {"year":1984,"month":6,"day":21,"hour":7,"minute":45,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Nhìn vào Phá Quân ở cung Tài Bạch tại Tuất, có thể thấy người này có lộc, nhưng phần giữ được không nhiều; nhìn từ phía khác, người mang tổ hợp này cũng dễ chật vật về sinh kế. Khi đã biết đặt giá trị của mình ở chỗ khác ngoài tiền bạc, chỗ yếu cũng thành chỗ rèn mình.

Từ phía cung Mệnh, chủ nhân lá số thường giữ của kỹ, ít khi tiêu hoang.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_LIMIT_CORE

Ở Thân, Phá Quân rơi vào hãm địa, nên người có Phá Quân ở cung Tài Bạch dễ kiếm được nhưng khó giữ, của cải dễ trôi đi. Biết biết giữ trước khi mở rộng là cách để điều bất lợi không đi đến cùng.

### {"year":2017,"month":1,"day":9,"hour":15,"minute":15,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Xét cung Tài Bạch tại Sửu, nơi Thiên Tướng tọa thủ, người này có lộc, nhưng phần giữ được không nhiều.

### {"year":2017,"month":7,"day":9,"hour":0,"minute":15,"gender":"male","to_year":2026} · S_LIMIT_CORE

Cung Tài Bạch ở Mão vô chính diệu, nét chính do Tiểu Hao tọa thủ mang lại; đương số dễ hao tán vì những khoản chi bất ngờ. Biết dành riêng một phần không động đến là cách để điều bất lợi không đi đến cùng.

Đôi khi tiền đến với người mang tổ hợp này từ nơi không ngờ tới.

### {"year":1935,"month":4,"day":4,"hour":12,"minute":15,"gender":"female","to_year":2026} · S_TIMING_FIRST

Với Thiên Đồng và Thái Âm đồng cung Tài Bạch tại Ngọ, người mang lá số này kiếm được tiền, song không dư dả như mong. Nhịp đời của người này cũng có điểm riêng: chủ nhân lá số thường thành đạt muộn, phần nhiều sau tuổi ba mươi. Có một mặt khác cần thấy: người mang tổ hợp này cũng dễ hao tán vì những khoản chi bất ngờ. Hóa Kỵ là chỗ kẹt của Mệnh này: đương số dễ rơi vào cảnh eo hẹp, khó dư dả. Và nếu biết biết giữ trước khi mở rộng, mặt khó của lá số sẽ trở thành bài học hơn là trở ngại.

Từ phía cung Mệnh, người này thường sẵn lòng chia sẻ của cải.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Cung Tài Bạch có Cự Môn đóng tại Ngọ cho thấy đương số có chí tự lập, dù cần thời gian; ở chiều ngược lại, người này cũng dễ rơi vào cảnh eo hẹp, khó dư dả. Biết đặt giá trị của mình ở chỗ khác ngoài tiền bạc là cách để điều bất lợi không đi đến cùng.

Không chỉ thế, chủ nhân lá số thường chặt chẽ trong chi tiêu.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_LIMIT_CORE

Có Thiên Phủ tọa thủ cung Tài Bạch ở Dậu, người này dễ hao tán vì những khoản chi bất ngờ. Khi biết biết giữ trước khi mở rộng, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Có Thiên Đồng và Thái Âm cùng tọa thủ cung Tài Bạch ở Ngọ, đương số thường có nguồn thu rộng mở; tiền bạc đến với người này không quá khó khăn. Dẫu vậy, chủ nhân lá số cũng dễ hao tán vì những khoản chi bất ngờ; xét theo thời gian, họ thường có công danh đến chậm nhưng bền. Xét cho cùng, chỗ mạnh của lá số nằm ở đường tài lộc; biết dành riêng một phần không động đến là cách để điều bất lợi không đi đến cùng.

Cũng vậy, đương số thường tự tay làm nên cơ nghiệp, lại gặp tiền đến không báo trước. Cung Mệnh cũng góp một nét vào chuyện này: chủ nhân lá số thường rộng rãi, không tiếc tiền với người khác.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_PLAIN



### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Nhìn vào Tử Vi ở cung Tài Bạch tại Tý, có thể thấy đương số kiếm được tiền, song không dư dả như mong; có điều, đương số cũng dễ phải lo toan nhiều về chuyện tiền nong. Sự hiện diện của Địa Kiếp khiến mọi thứ gai góc hơn: chủ nhân lá số dễ chịu những thăng trầm hơn người cùng cảnh. Càng biết tích lũy đều đặn thay vì mong một lần đổi đời, người này càng phát huy được những gì mình vốn có.
