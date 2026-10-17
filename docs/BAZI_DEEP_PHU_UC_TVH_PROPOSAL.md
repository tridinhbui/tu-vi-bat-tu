# Đề xuất `phu_uc_tvh` (CHƯA TRIỂN KHAI)

## Bối cảnh
Từ Phase 5, `phu_uc` luôn đọc khí thế của hệ thống (không dùng quyết định 40% của Thiệu Vĩ Hoa). Đây là **hệ quả có chủ đích của cách ly trường phái**, không phải sai sót: bật/tắt profile TVH không được đổi kết quả của phương pháp hệ thống (đã kiểm trên 5.000 lá số). Hệ quả: trên các ví dụ tr.397–401, phù ức của hệ thống không bám lời sách ở ví dụ 1 (hệ thống đọc cực nhược, sách đọc vượng).

## Đề xuất
Một phương pháp riêng `phu_uc_tvh`, **không thay và không trộn** với `phu_uc`:
- Đầu vào chỉ từ phía TVH: `strength_after.tvh.dm_strong` (quy tắc 40%, tr.355) và nhóm thập thần theo tổng điểm TVH. Không đọc khí thế, ngoại cách hay ngưỡng của hệ thống.
- Đầu ra: nhóm Dụng/Hỷ/Kỵ theo nguyên lý "vượng thì xì hơi hoặc khắc, nhược thì sinh phù" như các ví dụ của sách trình bày.
- Hiển thị như một phương pháp riêng trong `comparison`, có `meta.levels` riêng.

## Vì sao chưa triển khai
1. Trong phạm vi đã đọc (tr.331–400) **không tìm thấy phát biểu tổng quát** của sách về phù ức; nguyên lý chỉ xuất hiện như một câu lập luận bên trong từng ví dụ (ví dụ 4: "vượng thì nên xì hơi hoặc nên khắc"). Ghi lên mức `source_rule_verified` cần một điều nguồn nói trực tiếp.
2. Danh sách nhóm Dụng/Hỷ cho từng trường hợp (vượng/nhược × nhóm nhiều nhất) đã nằm trong bảng của `cach_cuc_tvh` (tr.378–386); `phu_uc_tvh` sẽ chồng lấn với nó, nên cần quyết định rõ nó thêm thông tin gì.
3. Sách không dựa vào phù ức khi có ngoại cách (ví dụ 4 bị engine đọc là ngoại cách); quy tắc ưu tiên giữa hai cách đọc cần nguồn.

## Điều kiện để triển khai
- Tìm một đoạn của chính sách phát biểu nguyên lý (hoặc xin xác nhận rằng chỉ có phần trong ví dụ). Nếu chỉ có ví dụ, mức nguồn tối đa là `partial`.
- Thêm vào `METHOD_META` với `levels.transcription_verified = n/a`, `source_rule_verified = no|partial`, `empirical_validated = no`.
- Test chấp nhận bắt buộc: (a) ví dụ 1, 3, 5 tr.397–401 là oracle; ví dụ 2 vì sách đọc nhược trái với quy tắc 40% phải được ghi là không tái lập; ví dụ 4 phải báo "không áp dụng" khi ngoại cách TVH chân; (b) bất biến hai chiều với `phu_uc` trên ≥ 5.000 lá số; (c) không có phép cộng/trộn điểm giữa `phu_uc` và `phu_uc_tvh`.
- Không dùng tỉ lệ khớp ví dụ để chỉnh ngưỡng.
