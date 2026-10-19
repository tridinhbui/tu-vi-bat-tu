# Đánh giá văn đọc chương cong_danh trên 1000 lá số

Sinh bởi `tools/interpret/eval_prose.ts --chapter cong_danh` (prose prose-0.2.0, knowledge `2b267b2abc0fc1b8`). Toàn bộ thẻ văn đang là bản nháp (allowDraft); các chỉ số là kiểm tra tự động, chưa phải chấm của người đọc hay chuyên gia.

| Chỉ số | Giá trị | Ngưỡng (plan §6) |
|---|---|---|
| Chương không lỗi chặn | 1000/1000 | 100% |
| Lỗi chặn theo loại | {} | 0 |
| Chương rỗng | 8 | 0 |
| Độ dài câu TB 18–35 chữ và độ lệch ≥ 6 | 54.0% | ≥ 95% |
| 4-gram lặp trong một chương (TB / max) | 0.002 / 0.043 | < 0.05 |
| Opener phổ biến nhất (mọi câu) | “bởi vậy,” 5.5% | ≤ 8% |
| Opener phổ biến nhất (câu đầu chương) | “cung quan” 19.8% | (theo dõi) |
| Jaccard 4-gram đoạn 1, cùng nucleus và cùng chính tinh (trung vị) | 0.09 | ≤ 0.35 |
| Entropy phân bố schema | 2.096 / log(12) = 2.485 | ≥ 0.7 × log(số schema dùng được) |
| Câu/đoạn mở dùng > 15% số chương | 0 | 0 |
| Thời gian sinh một chương (TB / p95, Node) | 49.48 ms / 69.59 ms | p95 < 30 ms |

Schema: S_QUIET_STRENGTH 269, S_PLAIN 150, S_VCD_BORROW 142, S_SATELLITE_WEAVE 122, S_DOUBLE_EDGE 81, S_EDGE_LATE_ELABORATE 74, S_LIMIT_CORE 71, S_TENSION_CORE 39, S_TIMING_ARC 29, S_TIMING_FIRST 10, S_TURN_THEN_TENSION 8, S_TENSION_BRIDGE 5



## Mẫu

### {"year":2016,"month":10,"day":17,"hour":11,"minute":0,"gender":"female","to_year":2026} · S_SATELLITE_WEAVE

Khi Thiên Cơ và Thái Âm cùng làm chủ cung Quan Lộc ở Thân, người mang lá số này thường có triển vọng lên địa vị cao. Đi cùng nét này, người này thường nổi danh vào một thời, lại khéo tay, có năng khiếu kỹ thuật hoặc nghệ thuật. Đương số có cơ hội đứng ở những vị trí mà nhiều người mong. Xét theo thời gian, họ thường có công danh đến chậm nhưng bền. Bởi vậy, điều đáng quý ở lá số này không chỉ là chỗ đứng trong xã hội mà còn là danh tiếng.

Hóa Quyền làm Thiên Cơ mạnh tay hơn, và năng lực trở thành nét nổi. Hơn nữa, chủ nhân lá số thường làm việc gì cũng dễ thành. Một nét khác đến từ cung Mệnh: người này thường thiên về con đường công bộc, phục vụ, lại có thiên hướng học thuật.

### {"year":2006,"month":12,"day":9,"hour":20,"minute":15,"gender":"female","to_year":2026} · S_SATELLITE_WEAVE

Cung Quan Lộc có Thiên Lương đóng tại Tỵ cho thấy một người thường đa tài, làm được nhiều việc. Cũng vậy, họ thường làm việc gì cũng dễ thành. Người mang tổ hợp này không dễ bị đóng khung vào một nghề; về nhịp đời, chủ nhân lá số thường thành danh từ khi còn trẻ. Bởi vậy, điều đáng quý ở lá số này không chỉ là sự đa tài mà còn là khả năng biến công sức thành kết quả.

Soi sang cung Mệnh, có thể thấy người này thường có triển vọng lên địa vị cao, lại có người giúp đúng lúc.

### {"year":1984,"month":6,"day":21,"hour":7,"minute":45,"gender":"female","to_year":2026} · S_SATELLITE_WEAVE

Người có Thất Sát ở cung Quan Lộc tại Ngọ thường đi được xa trên đường công danh. Song song với điều ấy, người mang tổ hợp này thường có khí chất của người hành động, hợp ngành võ, lại có uy, dễ được người khác nể và nghe theo. Họ có cơ hội đứng ở những vị trí mà nhiều người mong. Điều đọng lại sau tất cả là chỗ đứng trong xã hội và uy thế tự nhiên.

Cung Mệnh cũng góp một nét vào chuyện này: đương số thường có tài, làm việc giỏi giang, lại hanh thông trên đường sự nghiệp.

### {"year":2013,"month":11,"day":22,"hour":21,"minute":30,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Nhìn vào Thất Sát ở cung Quan Lộc tại Thìn, có thể thấy người này thường có công danh đến chậm nhưng bền; người mang tổ hợp này không nên so mình với người thành công sớm, vì nhịp của mình khác.

### {"year":2017,"month":1,"day":9,"hour":15,"minute":15,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Người có Thiên Phủ ở cung Quan Lộc tại Dậu thường thành danh từ khi còn trẻ; tuổi trẻ của đương số đã có những thành quả đáng kể. Rốt lại, cái vốn quý của người này nằm ở sự thành đạt sớm.

### {"year":2017,"month":7,"day":9,"hour":0,"minute":15,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Người có Thiên Tướng ở cung Quan Lộc tại Hợi thường linh hoạt giữa nhiều lĩnh vực; người này không dễ bị đóng khung vào một nghề. Điều đọng lại sau tất cả là sự đa tài.

Nhìn từ cung Mệnh, đương số thường đi được xa trên đường công danh, lại nhạy với cơ hội làm ăn.

### {"year":1935,"month":4,"day":4,"hour":12,"minute":15,"gender":"female","to_year":2026} · S_VCD_BORROW

Cung Quan Lộc ở Dần vô chính diệu, nét chính do Đà La tọa thủ mang lại; người mang lá số này thường có triển vọng lên địa vị cao. Rốt lại, cái vốn quý của người này nằm ở chỗ đứng trong xã hội.

Đương số có cơ hội đứng ở những vị trí mà nhiều người mong. Không chỉ thế, họ thường kiêm được cả văn lẫn võ. Cung Mệnh cũng góp một nét vào chuyện này: người này thường phát huy tốt khi có khuôn khổ rõ ràng, lại làm việc gì cũng dễ thành.

### {"year":1994,"month":8,"day":11,"hour":19,"minute":45,"gender":"female","to_year":2026} · S_VCD_BORROW

Cung Quan Lộc ở Dần vô chính diệu, nét chính do Lộc Tồn tọa thủ mang lại; người mang lá số này thường linh hoạt giữa nhiều lĩnh vực. Bởi vậy, điều đáng quý ở lá số này là khả năng làm được nhiều việc.

Nhiều người ngạc nhiên vì chủ nhân lá số làm được những việc tưởng chừng trái ngành. Ở cung Mệnh, điều này cũng hiện ra: người mang tổ hợp này thường có công danh hiển đạt, lại có thiên hướng học thuật.

### {"year":2019,"month":10,"day":10,"hour":18,"minute":0,"gender":"male","to_year":2026} · S_VCD_BORROW

Cung Quan Lộc ở Tỵ vô chính diệu, nét chính do Đà La tọa thủ mang lại; người mang lá số này thường đi được xa trên đường công danh. Bởi vậy, điều đáng quý ở lá số này là chỗ đứng trong xã hội.

Người mang tổ hợp này có cơ hội đứng ở những vị trí mà nhiều người mong. Ở cung Mệnh, điều này cũng hiện ra: đương số thường giỏi chữ nghĩa, có năng khiếu văn chương, lại có người giúp đúng lúc.

### {"year":2017,"month":10,"day":19,"hour":21,"minute":30,"gender":"female","to_year":2026} · S_VCD_BORROW

Cung Quan Lộc ở Dần vô chính diệu, nét chính do Hỏa Tinh tọa thủ mang lại; người mang lá số này thường thành đạt muộn, phần nhiều sau tuổi ba mươi.

Sự hiện diện của Hỏa Tinh khiến mọi thứ gai góc hơn: người mang tổ hợp này dễ gặp trở ngại lúc khởi đầu, chưa đúng chỗ của mình. Thành quả của họ đến khi nhiều người cùng lứa đã dừng lại. Nhìn từ cung Mệnh, đương số thường hợp làm trong tổ chức, cơ quan, lại giỏi chữ nghĩa, có năng khiếu văn chương.

### {"year":2011,"month":8,"day":1,"hour":23,"minute":45,"gender":"female","to_year":2026} · S_VCD_BORROW

Không có chính tinh, cung Quan Lộc tại Tý được đọc qua Đào Hoa và Hồng Loan đóng tại đó; đương số thường sớm có công danh. Điều đọng lại sau tất cả là sự thành đạt sớm.

Tuổi trẻ của họ đã có những thành quả đáng kể. Từ phía cung Mệnh, chủ nhân lá số thường đi được xa trên đường công danh, lại học hành sáng dạ.

### {"year":1979,"month":5,"day":20,"hour":2,"minute":0,"gender":"male","to_year":2026} · S_QUIET_STRENGTH

Xét cung Quan Lộc tại Thân, nơi Vũ Khúc và Thiên Tướng đồng cung, đương số thường dũng mãnh, hợp những việc cần can đảm; môi trường càng thử thách, người mang tổ hợp này càng bộc lộ được bản lĩnh. Lại nữa, họ thường đa tài, làm được nhiều việc. Có Hỏa Tinh ở Mệnh, khí chất trở nên sắc cạnh hơn, và chủ nhân lá số dễ gặp trở ngại lúc khởi đầu, chưa đúng chỗ của mình. Xét theo thời gian, người này thường phải đợi đến độ chín mới rực rỡ.

Nhìn từ cung Mệnh, họ thường nắm được quyền hành khi có dịp.
