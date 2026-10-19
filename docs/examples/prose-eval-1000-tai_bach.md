# Đánh giá văn đọc chương tai_bach trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter tai_bach` (prose prose-0.2.0, knowledge `2b267b2abc0fc1b8`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 71 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 | 40.8% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0 / 0.025 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “và nếu” 7.4% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “cung tài” 18.7% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.079 | ≤ 0.35 |
| Entropy phân bố schema | 2.073 / log(12) = 2.485 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 43.91 ms / 56.97 ms | p95 < 30 ms |

Schema: S_QUIET_STRENGTH 228, S_LIMIT_CORE 168, S_DOUBLE_EDGE 166, S_EDGE_LATE_ELABORATE 156, S_PLAIN 90, S_VCD_BORROW 80, S_TIMING_ARC 38, S_TURN_THEN_TENSION 24, S_TENSION_BRIDGE 19, S_SATELLITE_WEAVE 14, S_TIMING_FIRST 11, S_TENSION_CORE 6



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_SATELLITE_WEAVE

Người có Thiên Lương ở cung Tài Bạch tại Tý có tài lộc, dù chuyện tiền bạc vẫn khiến phải bận tâm. Cũng vậy, đương số thường giữ của kỹ, ít khi tiêu hoang.

### {"year":2006,"month":12,"day":9,"hour":20,"minute":15,"gender":"female","to_year":2026} · S_LIMIT_CORE

Không có chính tinh, cung Tài Bạch tại Dậu được đọc qua Địa Kiếp đóng tại đó; đương số dễ rơi vào cảnh eo hẹp, khó dư dả. Càng biết tích lũy đều đặn thay vì mong một lần đổi đời, người này càng phát huy được những gì mình vốn có.

Có Địa Kiếp ở Mệnh, khí chất trở nên sắc cạnh hơn, và người mang tổ hợp này dễ chịu những thăng trầm hơn người cùng cảnh. Ở cung Mệnh, điều này cũng hiện ra: chủ nhân lá số thường tính toán cẩn thận với đồng tiền.

### {"year":1984,"month":6,"day":21,"hour":7,"minute":45,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Xét cung Tài Bạch tại Tuất, nơi Phá Quân tọa thủ, đương số có lộc, nhưng phần giữ được không nhiều; nhìn từ phía khác, người mang tổ hợp này cũng dễ chật vật về sinh kế. Và nếu biết đặt giá trị của mình ở chỗ khác ngoài tiền bạc, mặt khó của lá số sẽ trở thành bài học hơn là trở ngại.

Từ phía cung Mệnh, chủ nhân lá số thường giữ của kỹ, ít khi tiêu hoang.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_LIMIT_CORE

Ở Thân, Phá Quân rơi vào hãm địa, nên người có Phá Quân ở cung Tài Bạch dễ kiếm được nhưng khó giữ, của cải dễ trôi đi. Khi biết biết giữ trước khi mở rộng, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

### {"year":2017,"month":1,"day":9,"hour":15,"minute":15,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Nhìn vào Thiên Tướng ở cung Tài Bạch tại Sửu, có thể thấy người này có lộc, nhưng phần giữ được không nhiều.

### {"year":2017,"month":7,"day":9,"hour":0,"minute":15,"gender":"male","to_year":2026} · S_LIMIT_CORE

Cung Tài Bạch ở Mão vô chính diệu, nét chính do Tiểu Hao tọa thủ mang lại; người mang lá số này dễ hao tán vì những khoản chi bất ngờ. Càng biết dành riêng một phần không động đến, người này càng phát huy được những gì mình vốn có.

Đôi khi tiền đến với người mang tổ hợp này từ nơi không ngờ tới.

### {"year":1935,"month":4,"day":4,"hour":12,"minute":15,"gender":"female","to_year":2026} · S_TIMING_FIRST

Người có Thiên Đồng và Thái Âm đồng cung Tài Bạch tại Ngọ kiếm được tiền, song không dư dả như mong; nhịp đời của người này cũng có điểm riêng: chủ nhân lá số thường thành đạt muộn, phần nhiều sau tuổi ba mươi. Có một mặt khác cần thấy: người mang tổ hợp này cũng dễ hao tán vì những khoản chi bất ngờ. Hóa Kỵ là chỗ kẹt của Mệnh này: đương số dễ rơi vào cảnh eo hẹp, khó dư dả. Và nếu biết biết giữ trước khi mở rộng, mặt khó của lá số sẽ trở thành bài học hơn là trở ngại.

Từ phía cung Mệnh, người này thường sẵn lòng chia sẻ của cải.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Khi Cự Môn làm chủ cung Tài Bạch ở Ngọ, người mang lá số này có chí tự lập, dù cần thời gian; ở chiều ngược lại, người này cũng dễ rơi vào cảnh eo hẹp, khó dư dả. Càng biết đặt giá trị của mình ở chỗ khác ngoài tiền bạc, người này càng phát huy được những gì mình vốn có.

Không chỉ thế, chủ nhân lá số thường chặt chẽ trong chi tiêu.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_LIMIT_CORE

Khi Thiên Phủ làm chủ cung Tài Bạch ở Dậu, người mang lá số này dễ hao tán vì những khoản chi bất ngờ. Khi biết biết giữ trước khi mở rộng, chính điều từng gây vướng bận sẽ trở thành thế mạnh.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Có Thiên Đồng và Thái Âm cùng tọa thủ cung Tài Bạch ở Ngọ, đương số thường có đường tài lộc rộng mở; tiền bạc đến với người này không quá khó khăn. Dẫu vậy, chủ nhân lá số cũng dễ hao tán vì những khoản chi bất ngờ. Rốt lại, cái vốn quý của người này nằm ở đường tài lộc; càng biết dành riêng một phần không động đến, người này càng phát huy được những gì mình vốn có.

Cũng vậy, người mang tổ hợp này thường tự tay làm nên cơ nghiệp, lại gặp tiền đến không báo trước. Cung Mệnh cũng góp một nét vào chuyện này: đương số thường rộng rãi, không tiếc tiền với người khác.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_PLAIN



### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Nhìn vào Tử Vi ở cung Tài Bạch tại Tý, có thể thấy người này kiếm được tiền, song không dư dả như mong; có điều, đương số cũng dễ phải lo toan nhiều về chuyện tiền nong. Sự hiện diện của Địa Kiếp khiến mọi thứ gai góc hơn: chủ nhân lá số dễ chịu những thăng trầm hơn người cùng cảnh. Càng biết tích lũy đều đặn thay vì mong một lần đổi đời, người này càng phát huy được những gì mình vốn có.
