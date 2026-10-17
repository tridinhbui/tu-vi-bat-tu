# Quy trình để người kiểm độc lập đối chiếu 120 ô với ảnh sách

Mục tiêu: có ít nhất một (tốt nhất hai) người **không phải mô hình** xác nhận bảng điều hậu của Thiệu Vĩ Hoa (tr.389–397) đã được chép đúng. Quy trình này không nâng bất kỳ mức xác minh nào tự động; chỉ ghi lại bằng chứng.

## Chuẩn bị
1. Lấy bản sách: *Dự Đoán Theo Tứ Trụ* (Thiệu Vĩ Hoa), số trang in = số trang PDF của bản scan đang dùng.
2. Mở `docs/BAZI_DEEP_TVH_CELLS_CHECK.md` (để đọc) và `docs/bazi_deep_tvh_cells_check.csv` (để điền). Mỗi dòng ghi sẵn số trang của bảng (tr.389 hoặc 390) và của chú thích (tr.391–397).
3. Người kiểm **không** nhìn cột engine trước: điền theo ảnh trang, rồi mới chạy công cụ so sánh.

## Điền (mỗi ô một dòng)
| Cột | Nội dung |
|---|---|
| `nguoi_kiem` | tên hoặc mã người kiểm (bắt buộc nếu điền dòng) |
| `bang_theo_anh` | các can **in trong ô bảng** (tr.389–390), cách nhau dấu cách, đúng thứ tự in. Ví dụ `Quý Bính` |
| `chu_thich_theo_anh` | các can ngay sau tên tháng trong **chú thích** (tr.391–397), theo thứ tự in (can đầu là chủ). Chỉ lấy đến dấu chấm đầu tiên, bỏ lời giải thích |
| `ket_qua` | `khop` (đã đọc, hai ô trên là điều tôi thấy), `sai_bang`, `sai_chu_thich`, `khong_doc_duoc` |
| `ghi_chu_nguoi_kiem` | tùy ý (chữ mờ, nghi lỗi in...) |

Quy ước chính tả: `kỉ/kì` = Kỷ, `tị` = Tỵ đều được chấp nhận; chỉ ghi tên can.

## Chạy công cụ
```bash
python tools/bazi_deep_tvh_review_intake.py nguoi1.csv nguoi2.csv
```
Công cụ **không sửa dữ liệu engine** và không giải quyết 9 ô mâu thuẫn. Với mỗi ô nó báo một trạng thái:

| Trạng thái | Nghĩa |
|---|---|
| `no_review` | chưa ai điền |
| `confirmed_1` | một người điền, khớp engine (cả bảng và chú thích) |
| `confirmed_2` | hai **người khác nhau** cùng khớp engine (cùng một người điền hai lần chỉ tính một) |
| `disagrees` | có người thấy khác engine, hoặc hai người khác nhau: cần quyết định của con người |
| `unreadable` | có người đánh dấu không đọc được |

## Quy tắc quyết định
- Chín ô `book_internal_conflict` (bảng và chú thích nêu hai tập can khác nhau) **giữ nguyên cờ** dù người kiểm xác nhận cả hai nơi: mâu thuẫn nằm trong sách, không phải trong bản chép. Người kiểm xác nhận rằng sách *thật sự* in như vậy; không ai chọn cách diễn giải nào là đúng.
- `disagrees`: người phụ trách dữ liệu xem ảnh trang, sửa `engine/data/bazi_deep/tvh_dieuhau.json` bằng tay, ghi vào `tests/golden/tvh_dieuhau_blind.json` mục `adjudicated`, và chạy lại test.
- Chỉ khi 120 ô đều `confirmed_1` trở lên, tài liệu mới được ghi *"bản chép đã có người kiểm độc lập"*. Mức `transcription_verified` trong `meta.levels` vẫn là `yes` (chép đúng nguồn); điều thay đổi là ghi chú "chưa có người kiểm" được bỏ. **`source_rule_verified` và `empirical_validated` không đổi.**

## Ví dụ tr.387–400
Cùng cách: so `tests/golden/tvh_dungthan_examples.json` với trang sách. Ví dụ 4 (tr.399–400) có bảng in vỡ: ngày Quý Mão là dữ liệu **dựng lại**, năm và giờ đọc trực tiếp, tháng suy từ hàng đại vận (xem `pillar_basis`). Ví dụ 5 đọc trực tiếp bởi một người đọc, chưa có lượt chép mù.
