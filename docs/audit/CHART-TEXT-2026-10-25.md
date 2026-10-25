# Biểu đồ Tổng quan và lời luận: bảy chỗ lệch (2026-10-25)

Kiểm trên lá 09/01/2002 04:30 nam: dữ kiện lấy từ `/api/facts` live, toàn bộ văn dựng bằng mã của main `cfb766e` (site live khóa nửa sau mỗi
chương với khách); mức biểu đồ dựng lại khớp từng chặng, từng năm với `/api/overview` live. Quy ước gọi tên mức (phân vị của 1.000 lá mẫu,
chủ dự án quyết 2026-10-24) **không đổi**. Phiên bản chỉ số `indices-3.1.1`, norms chạy lại.

| # | Chỗ lệch | Sửa | Ở đâu |
|---|---|---|---|
| 1 | Hạn mà lời sách nghiêng thuận vẫn ghi "Nhiều thử thách" không giải thích | Câu mức nói rõ: những điều nói về chặng phần nhiều thuận, **mức là so với các chặng thường gặp**, và kể **cái kéo xuống nặng nhất** (vd. "Hóa Kỵ theo can Giáp rơi vào cung Tài Bạch"). "Lời sách nghiêng thuận" chỉ tính câu sách về vận (KL tr.230-236, TH tr.115-117, Toàn Thư), không tính đắc hãm từng sao (vốn nghiêng thuận ở hầu hết lá) | `prose/vanhan.ts` `bookLean`, `pullOf`; `van_han.json level_against`, `level_against_mixed` |
| 7 | "cộng cả các yếu tố khác của hạn" lặp mà không nói yếu tố nào | Như trên: mọi chặng có câu thuận mà mức thấp (hoặc câu vướng mà mức cao) đều nêu một yếu tố nặng nhất phía bên kia | như trên |
| 2 | Năm 2026: thẻ biểu đồ và đoạn năm kể khác nhau | Đoạn năm thêm **lưu đại hạn** (TH tr.117-118) và **mức của năm đúng như biểu đồ**, kèm lớp nặng nhất ("phần lớn theo đà của đại hạn 23–32 tuổi (mức …)"); khi câu KL về tiểu hạn đi ngược thì nói "dù câu về tiểu hạn ở trên nghiêng về khó". "chặng" → "năm"; "tuổi âm" → "tuổi mụ" | `vanhan.ts yearParagraphs` |
| 3 | Toàn Thư: biểu đồ ghi "diễn ý, chưa đối chiếu", văn ghi lời sách đã kiểm | Biểu đồ dùng **đúng các câu nhập hạn ca đã kiểm trang** mà chương Đại hạn nói (`prose/vanhan_books.ts`, TT tr.96-106), cite theo trang, trọng số giữ ½ mỗi câu | `indices.ts vanItems` |
| 4 | Biểu đồ vẽ 10 đại hạn, văn dừng ở 73–82 | Văn (Đại hạn, Diễn biến theo đại hạn, Tổng luận) nói đủ **10 chặng như biểu đồ** | `vanhan.ts shownDecades`, `course.ts`, `tong_luan.ts` |
| 5 | Nguyệt vận 12 tháng cùng một mức, không lời nào | Khi mọi tháng cùng một mức, thẻ ghi vì sao (đắc hãm các cung nguyệt hạn chỉ nhích quanh mức năm, chưa tháng nào đủ đổi bậc) | `indices.ts months.note`, `web/js/overview.js` |
| 6 | Radar thấp ở Tài Bạch mà Tổng luận xếp kiếm tiền đứng đầu | Tổng luận nói: biểu đồ mười hai cung đo riêng cung Tài Bạch; chỗ mạnh của "khả năng kiếm tiền" nằm ở các cung khác của lĩnh vực ấy (Quan Lộc, Mệnh, Phúc Đức). Chặng thấp nhất mà lời sách vẫn nghiêng thuận cũng nói "thấp là so với các chặng thường gặp" | `tong_luan.ts radarLine`, `tong_luan.json` |

## Mức của lá 2002 thay đổi (vì điểm 3: câu Toàn Thư đã kiểm trang thay cho bản diễn ý cũ, norms chạy lại)

| Đại hạn | Trước (live 3.1.0) | Sau (3.1.1) |
|---|---|---|
| 3–12 Mệnh | Nhiều thử thách | Rất thử thách |
| 13–22 Huynh Đệ | Nhiều thử thách | Nhiều thử thách |
| 23–32 Phu Thê | Thuận | Rất thuận |
| 33–42 Tử Tức | Trung bình | Trung bình |
| 43–52 Tài Bạch | Nhiều thử thách | Nhiều thử thách |
| 53–62 Tật Ách | Trung bình | Thuận |
| 63–72, 73–82 | Nhiều thử thách | Nhiều thử thách |
| 83–92 Quan Lộc | Rất thử thách | Rất thử thách |
| 93–102 Điền Trạch | Thuận | Thuận |

Năm 2026: Trung bình → Thuận (theo đà đại hạn 23–32 mức Rất thuận; câu KL về tiểu hạn Tài Bạch nghiêng khó, được nói ra).
