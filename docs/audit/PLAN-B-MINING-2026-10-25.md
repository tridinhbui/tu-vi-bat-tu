# Kế hoạch (b): thêm luật có trang từ Khảo Luận, Thực Hành, Toàn Thư cho các cung mỏng (2026-10-25)

Sau khi Hàm Số vào main (`4ccedd9`), số luật verified theo cung và theo sách:

| Cung | KL | TH | TT | HS | Chỗ trống rõ nhất |
|---|---|---|---|---|---|
| Quan Lộc | 30 | 25 | 49 | 111 | đủ; thiếu luật **bước ngoặt / thời điểm** |
| Tài Bạch | 48 | 24 | 62 | 94 | đủ |
| Phu Thê | 28 | **9** | 41 | 88 | TH ít |
| Điền Trạch | **14** | **9** | 43 | 51 | KL, TH ít |
| Phúc Đức | 27 | 13 | 51 | 50 | |
| Thiên Di | 26 | 18 | 59 | 48 | |
| Nô Bộc | 28 | **5** | 38 | 23 | TH ít |
| Tử Tức | 28 | **6** | **9** | 31 | TH, TT ít |
| Huynh Đệ | **8** | 11 | **3** | 22 | KL, TT rất ít |
| Phụ Mẫu | 18 | **6** | 22 | 30 | TH ít |
| Tật Ách | **6** | **0** | **1** | 21 | cả ba sách gần như trống |

Độ sâu đo trên 150 lá cho thấy Huynh Đệ, Tật Ách, Tử Tức vẫn chỉ 5–7 câu sách mỗi chương.

## Làm gì

1. **Rà trang** (đã có công cụ: `tools/show_page.py`, `book_text.quote_on_page`, `tools/mining/*`):
   - TT phần "Thập nhị cung" (các mục cung Tử Tức, Huynh Đệ, Tật Ách, Điền Trạch) và TT pp.143-155 "hợp cách / phá cách theo từng cung"
     (ghi ở `docs/audit/CACH-CUC-SOURCES.md` là nguồn chưa dùng).
   - TH chương luận 12 cung cho Phu Thê, Nô Bộc, Tử Tức, Phụ Mẫu, Điền Trạch, Tật Ách (TH xáo dòng: luôn mở ảnh trang).
   - KL các mục "X ở các cung" (pp.84-142) cho Huynh Đệ, Tật Ách, Điền Trạch; mục sao cứu giải và tối kỵ cho Tật Ách (tr.76, 118-122).
2. **Lọc như cũ:** không tướng mạo, bệnh danh, chết/yểu, tù tội, sự kiện hôn nhân con cái (theo quyết định của chủ dự án); câu nào
   trang không phân định thì bỏ, ghi lý do.
3. **Trước khi thành luật**, so với luật đã có (đã viết sẵn phép so): cùng điều kiện cùng ý → chỉ thêm trích dẫn (đồng chứng), không thêm
   luật; cùng điều kiện ngược ý → ghi là sách bất đồng, nói cả hai.
4. **Đo lại** bằng `depth.ts` 150 lá và các cổng (`eval_synthesis`, `eval_repeat`, `check:prose`), mục tiêu: Huynh Đệ, Tật Ách, Tử Tức
   lên ≥ 7 câu sách mà câu trùng / cụm lặp không tăng.

## Cách chạy

Ba luồng khai thác độc lập (TT, TH, KL), mỗi luồng một nhánh riêng vì đều đọc ảnh trang và lâu; gộp bằng một bước dựng lại dữ liệu chung.
Ước lượng: mỗi luồng vài giờ máy; phần gộp và kiểm như đợt Hàm Số.
