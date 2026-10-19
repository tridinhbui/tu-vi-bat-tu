# Đánh giá văn đọc chương phu_mau trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter phu_mau` (prose prose-0.2.0, knowledge `4db446cf1b5653fc`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 55 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 (mọi lá số, kể cả chương trống) | 81.9% | ≥ 95% |
| Như trên, chỉ tính chương có từ 3 câu (839 lá số) | 92.6% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0 / 0.019 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “riêng ở” 3.0% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “riêng ở” 10.3% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.088 | ≤ 0.35 |
| Entropy phân bố schema | 1.854 / log(10) = 2.303 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 74.23 ms / 77.35 ms | p95 < 30 ms |

Schema: S_DOUBLE_EDGE 289, S_EDGE_LATE_ELABORATE 282, S_QUIET_STRENGTH 112, S_LIMIT_CORE 103, S_SATELLITE_WEAVE 73, S_PLAIN 55, S_VCD_BORROW 32, S_TENSION_BRIDGE 32, S_TURN_THEN_TENSION 21, S_TENSION_CORE 1



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Khi Vũ Khúc và Phá Quân cùng làm chủ cung Phụ Mẫu ở Tỵ, đương số thường sớm xa người thân, mỗi người một ngả; ngược lại, cha mẹ cũng dễ gặp nhiều vất vả, phải tự mình chống đỡ, và cũng dễ chật vật về sinh kế. Khoảng cách địa lý giữa chủ nhân lá số và người nhà thường lớn hơn người khác.

Ngoài ra, người mang tổ hợp này thường được người thân thương yêu, gắn bó, còn cũng dễ không hợp tính người trong nhà.

### {"year":1943,"month":2,"day":24,"hour":20,"minute":30,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Trong cung Phụ Mẫu, bộ Tử Vi và Thất Sát đóng tại Tỵ cho thấy người mang lá số này thường sống xa gia đình; mỗi người trong nhà người mang tổ hợp này một ngả, gặp nhau chủ yếu vào dịp lễ tết. Ở chiều ngược lại, chủ nhân lá số cũng dễ không hợp tính người trong nhà. Càng biết nói rõ điều mình nghĩ trước khi điều ấy thành bất hòa, người này càng phát huy được những gì mình vốn có.

Cùng một mạch ấy, song thân thường gặp tiền đến không báo trước, song cũng dễ tiền vào nhanh, ra cũng nhanh.

### {"year":1999,"month":1,"day":19,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_SATELLITE_WEAVE

Xét cung Phụ Mẫu tại Tỵ, nơi Thiên Lương tọa thủ, người này thường hòa thuận với người thân; đồng thời, cha mẹ thường kiếm tiền không khó, đời sống đầy đủ. Tình thân của đương số bền theo năm tháng. Cái nên giữ gìn nhất ở đây là sự hòa thuận trong nhà.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Nhìn vào bộ Thiên Đồng và Cự Môn ở cung Phụ Mẫu tại Sửu, có thể thấy song thân thường có nguồn thu rộng mở. Nhìn từ phía khác, người này cũng dễ bất hòa, xung khắc với người thân. Cha mẹ thường có điều kiện vật chất tốt hơn mức trung bình. Cái quý nhất mà song thân mang lại là sự đầy đủ về vật chất; càng biết nói rõ điều mình nghĩ trước khi điều ấy thành bất hòa, người này càng phát huy được những gì mình vốn có.

Cùng một mạch ấy, chủ nhân lá số thường sống xa gia đình, lại hợp ý với người trong nhà.

### {"year":1996,"month":10,"day":14,"hour":13,"minute":15,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Đến cung Phụ Mẫu tại Thìn, với Tham Lang tọa thủ, người mang lá số này thường sống xa gia đình; bù lại, song thân cũng dễ chịu những thăng trầm hơn người cùng cảnh, và cũng dễ rơi vào cảnh eo hẹp, khó dư dả. Đường đời đưa người này đi xa nơi gia đình ở. Có Đà La ở Mệnh, khí chất trở nên sắc cạnh hơn, và đương số dễ va chạm với người thân vì những chuyện nhỏ. Nếu biết nói rõ điều mình nghĩ trước khi điều ấy thành bất hòa, phần khó ấy sẽ bớt nặng đi nhiều.

### {"year":1995,"month":5,"day":15,"hour":19,"minute":30,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Với Thiên Cơ và Thái Âm cùng ở cung Phụ Mẫu tại Thân, người mang lá số này thường hợp ý với người trong nhà. Thế nhưng, cha mẹ cũng dễ rơi vào cảnh eo hẹp, khó dư dả, và cũng dễ gặp nhiều vất vả, phải tự mình chống đỡ; những bất đồng trong nhà của chủ nhân lá số thường được giải quyết êm thấm. Vốn liếng đáng kể nhất là sự hòa thuận trong nhà.

Cũng vậy, cha mẹ thường có tài lộc thuận lợi.

### {"year":1997,"month":6,"day":6,"hour":11,"minute":45,"gender":"female","to_year":2026} · S_EDGE_LATE_ELABORATE

Với Tử Vi và Phá Quân cùng ở cung Phụ Mẫu tại Sửu, đương số thường sớm xa người thân, mỗi người một ngả; dẫu vậy, người này cũng dễ bất hòa, xung khắc với người thân. Khoảng cách địa lý giữa chủ nhân lá số và người nhà thường lớn hơn người khác. Khi đã biết nói rõ điều mình nghĩ trước khi điều ấy thành bất hòa, chỗ yếu cũng thành chỗ rèn mình.

Song cha mẹ cũng dễ gặp nhiều vất vả, phải tự mình chống đỡ.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_PLAIN



### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_EDGE_LATE_ELABORATE

Đến cung Phụ Mẫu tại Dần, với Thiên Đồng và Thiên Lương cùng tọa thủ, song thân thường có tài lộc thuận lợi. Đổi lại, hai người cũng dễ rơi vào cảnh eo hẹp, khó dư dả, và cũng dễ gặp nhiều vất vả, phải tự mình chống đỡ; tiền bạc đến với song thân không quá khó khăn. Điều đáng quý ở cha mẹ là sự đầy đủ về vật chất.

Cùng một mạch ấy, người mang tổ hợp này thường được người thân thương yêu, gắn bó.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Trong cung Phụ Mẫu, bộ Tử Vi và Thất Sát đóng tại Hợi cho thấy đương số thường sống xa gia đình; mỗi người trong nhà người này một ngả, gặp nhau chủ yếu vào dịp lễ tết. Tuy nhiên, đương số cũng dễ không hợp tính người trong nhà. Linh Tinh đóng cùng cung làm tính cách thêm phần căng: song thân dễ gặp nhiều vất vả, phải tự mình chống đỡ. Nếu biết nói rõ điều mình nghĩ trước khi điều ấy thành bất hòa, phần khó ấy sẽ bớt nặng đi nhiều.

Ngoài ra, cha mẹ thường có tài lộc thuận lợi, lại có vận may tài lộc theo từng đợt, thế nhưng cũng dễ tiền vào nhanh, ra cũng nhanh.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_DOUBLE_EDGE

Khi Thiên Tướng làm chủ cung Phụ Mẫu ở Dậu, người này thường hòa thuận với người thân; người thân là nơi người mang tổ hợp này tìm về khi cần. Thế nhưng, song thân cũng dễ chật vật về sinh kế, và cũng dễ gặp nhiều vất vả, phải tự mình chống đỡ. Nếu phải gọi tên một điểm tựa, đó là tình thân êm ấm.

Bên cạnh đó, song thân thường kiếm tiền không khó, đời sống đầy đủ.

### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_DOUBLE_EDGE

Đến cung Phụ Mẫu tại Tỵ, với Thái Âm tọa thủ, cha mẹ thường có nguồn thu rộng mở; hai người thường có điều kiện vật chất tốt hơn mức trung bình. Nhìn từ phía khác, song thân cũng dễ rơi vào cảnh eo hẹp, khó dư dả, và cũng dễ lận đận, việc gì cũng phải qua nhiều lần mới thành. Ở song thân, điểm đáng quý nhất là sự đầy đủ về vật chất.

Thêm vào đó, chủ nhân lá số thường hòa thuận với người thân, song cũng dễ va chạm với người thân vì những chuyện nhỏ.
