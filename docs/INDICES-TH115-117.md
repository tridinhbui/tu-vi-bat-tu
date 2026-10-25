# Thực Hành tr.115-117: luật đại / tiểu hạn cho biểu đồ vận (indices-3.1.0, 2026-10-24)

Mỗi mục đã đối chiếu **ảnh trang** (`tools/show_page.py TH 115|116|117 --image`); lớp chữ của TH đảo thứ tự dòng nên không dùng. Nguyên văn
chép đúng như sách in, kể cả lỗi in (ghi chú trong ngoặc vuông). Trạng thái:

- **đã thêm**: có trong `engine/data/van_han_rules.json` và `VAN_RULES` (`src/interpret/indices.ts`);
- **đã có**: luật cũ đã đọc mục này;
- **chờ duyệt**: lời sách nói chuyện chết, tù tội, tai nạn, thương tật, bệnh, bỏng, chết đuối hoặc tang: chưa thêm, chờ chủ dự án duyệt nội dung;
- **không tính được**: điều kiện không thể đọc trên một cung vận, hoặc không có chiều thuận / bất lợi để vẽ.

Cách đọc chung (ghi trong `tools/build_van_han_rules.py`):

- "Lưỡng hạn" = đại hạn và tiểu hạn như nhau. Mục IX.7-8 phải nói "trùng phùng" khi cả hai cùng một cung, nên khi không nói thì mỗi luật đọc riêng một cung vận.
- "gặp" không nói vị trí = sao ở ngay cung vận (như `build_van_han_books.py`).
- "hội" = sao trong tam phương tứ chính của cung vận. Tang Môn và Bạch Hổ luôn xung chiếu nhau, nên không bao giờ cùng một cung.
- Tuổi = can / chi năm sinh âm lịch (`tv.year_gz`).

## Mục IX (tr.115)

| Mục | Nguyên văn | Trạng thái | Ghi chú |
|---|---|---|---|
| IX.5 | "Lương hạn [Lưỡng hạn] : Đại, Tiểu mà gặp Trúc la (tức Sát, Phá, Tham) mà gia thêm Cự môn, Linh Hỏa thì xấu xa, tai biến, khong kể xiết." | **không tính được** (và có chữ "tai biến") | Cự Môn không bao giờ đứng trong tam phương tứ chính của Sát / Phá / Tham (kiểm trên 1.000 lá: 0 lần). Đọc "đại hạn ở Sát Phá Tham, tiểu hạn ở Cự Môn" là suy diễn của hệ thống, sách không nói. |
| IX.6 | "Lưỡng hạn của người Giáp rất kỵ Thiên thương và Thiên sứ đóng cung zdần [Dần]. Người tuổi Canh kỵ gặp Thương sứ ơ cung Thân." | **đã thêm**: `TH_IX6_GIAP_THUONG_SU`, `TH_IX6_CANH_THUONG_SU` (bất lợi, 1) | Can năm Giáp + cung vận ở Dần có Thiên Thương hoặc Thiên Sứ; can Canh + cung vận ở Thân. Thương (Nô Bộc) và Sứ (Tật Ách) không bao giờ cùng cung, nên "và" đọc là một trong hai. |
| IX.7 | "Lưỡng hạn trùng phùng ở cung Tí mà gặp Thương, Sứ Kình, Đà, Tuế thì có thẻ nguy đến tánh mạng." | **chờ duyệt** (nguy tính mạng) | Cần đại hạn và tiểu hạn cùng ở Tý. |
| IX.8 | "Thương ở cung Tí, Thìn, Mão, Ngọ, Mùi; Thiên sứ ở Dần, Thân, Tỵ, Hợi mà gặp phải Thái tuế thì tai họa ghê gớm. Nếu lưỡng hạn trùng phùng mà không cso sao giải cứu thì nguy đến tính mệnh." | **chờ duyệt** (nguy tính mạng) | Câu đầu chỉ nói "tai họa ghê gớm"; nếu chủ dự án cho, có thể tách câu đầu thành một luật riêng. "sao giải cứu" không có danh sách. |
| IX.9 | "Người tuổi Thân mà đến lưỡng hạn gặp Thiên thương rất hại, tai họa liên miên." | **đã thêm**: `TH_IX9_THAN_THUONG` (bất lợi, 1) | Lời đọc: "theo sách rất bất lợi", bỏ chữ "tai họa" (chủ dự án quyết, 2026-10-24). |
| IX.10 | "Người tuổi Thin [Thìn], Tuất, Sửu, Mùi mà lưỡng hạn gặp Kình, Đà, không hề gì, trái lại nếu có Tử, Phủ, Xương, Khúc thì lại là hoạnh phát." | **đã thêm**: `TH_IX10_TU_MO_KINH_DA_PHAT` (thuận, 1); `TH_IX10_TU_MO_KINH_DA` (không có chiều) | Vế "không hề gì" được nói trong lời đọc vận nhưng không cộng trừ. Nó trái với lớp đắc hãm KL tr.233 (Kình Đà hãm vẫn bị tính bất lợi). **Chủ dự án quyết**: có cho vế này triệt tiêu Kình / Đà hãm ở cung vận của tuổi Tứ Mộ không? |
| IX.11 | "Hạn gặp Thất sát có gia Hình, Hổ, Quan phủ ở cung hãm thì dễ mắc vòng lao lý." | **chờ duyệt** (lao lý) | |

## Đoán cách ở đại tiểu hạn (tr.116)

| Mục | Nguyên văn | Trạng thái | Ghi chú |
|---|---|---|---|
| 1 | "Đăng khoa hay Thăng chức : Hạn cần có Đào Hồng, Xương Khúc, Khôi Việt, Khoa Quyền hoặc thêm Thai Cáo, Quốc ấn." | **đã có**: `TH_DAO_HONG_KHOA_QUYEN` | |
| 2 | "Hôn phối: Phải xem chính cung Phối năm ấy hay Đại Tiểu hạn có: Sát phá Liêm đào; Vũ Diêu Lộc Mã Hỉ Đào (hay Hồng) …" | **không tính được** | Báo sự kiện cưới hỏi, không có chiều thuận / bất lợi. Lớp sách vận hạn (`build_van_han_books.py`) cũng đã bỏ sự kiện hôn nhân. |
| 3 | "Sinh con: Xem ở Tiểu hạn có : Phủ Tướng Long phượng ngộ sao Thái; …" | **không tính được** | Sự kiện sinh con, không có chiều. |
| 4 | "Tình duyên: dang díu: Nếu số người mà cung Thê có Tả Hữu Hồng Đào chiếu, mà đến Tiểu hạn lại gặp các dâm tinh thì thế tất phải dang díu thêm nợ tình duyên." | **không tính được** | "dâm tinh" không có danh sách; là sự kiện, không có chiều. Đoạn sau nói về cung Thê bẩm sinh. |
| 5 | "về cung duyên dang dở: … khi đến hạn gặp phải tất phải sinh ly hay tử biệt." | **chờ duyệt** (tử biệt) | Các cách ở cung Phối bẩm sinh. |

## Đại tiểu hạn thất lợi (tr.116-117)

| Mục | Nguyên văn | Trạng thái |
|---|---|---|
| 6a | "Cơ Nguyệt Đồng Lương hay Cự Nhật mà gặp Kình Đà, Không Kiếp hay Phá toái, Kiếp sát thì dễ tàn tật, mất cướp" | **chờ duyệt** (tàn tật) |
| 6b | "Sát phá Liêm Tham mà gặp Nhị tam Không, Linh Hỏa Kình Kỵ hay Đại tiểu Hao Hình, Sát Phục binh, Tang Hổ thì tù ngục vong gia" | **chờ duyệt** (tù ngục) |
| 6c | "Tử Phủ Vũ Tướng  găp phải Tam Không, Kiếp Kỵ Hình Đà hay gặp Linh Hỏa Tang Diêu thì bị giáng chức, phá tài." | **đã có**: `TH_TPVT_KHONG_KIEP_KY` |
| 6d | "Cự Cơ, Đồng Lương mã gặp Kình Đà Không Kiếp, song Hao, Phá toái, Kỵ thì phá tài hay bị thương tật." | **chờ duyệt** (thương tật). Nếu chủ dự án cho, có thể đọc vế "phá tài" như 6c. |
| 6e | "Nguyệt Đồng Cơ Cự mà gặp Không Kiếp Đẩu quân, Tuế, Kỵ, thì bị kiện cáo hay giáng chức." | **đã có**: `TH_NDCC_KHONG_KIEP` |
| 6f | "Nhật Nguyệt gặp Không Kiếp Thiên diêu hay gặp Linh Hỏa, Cô Quả thì đau mắt có thể mù." | **chờ duyệt** (bệnh; quy tắc Tật Ách: không dự đoán sức khỏe) |
| 6g | "Phá Liêm Tham gặp Diêu Kỵ, Mộc dúc dễ bị bỏng." | **chờ duyệt** (bỏng) |
| 6h | "Thiên Đồng gặp Kình Kỵ, Mộc Hỏa Không Kiếp hoặc là Cự Kỵ Tuế Đà Không Kiếp thì dễ chết đuối." | **chờ duyệt** (chết đuối) |
| 6i | "Tiểu hạn găp Tang Hỏa Linh mà nhất là đóng cung Điền trạch thì dễ bị cháy nhà, hay sản vật." | **chờ duyệt** (cháy) |
| 6j | "Cơ Lương đóng Thìn Tuất mà Tiểu hạn đến đó gặp phải Tang Điếu, Tuế, Khôcs Hư thì bị ngã từ cao xuống." | **chờ duyệt** (tai nạn) |
| 6k | "Sát Phá Liêm Tham găp Tang Hổ Kình Đà Điếu khách hay là Tham lang gặp Hổ, Điêu, Ly Tuế ở cung Thìn Tuất thì bị xe cán hay thú cắn." | **chờ duyệt** (tai nạn) |
| 6l | "Kinh Không Kiếp gặp Quan phù hay Tử Phù, Trực phù mà có Phục binh thì phòng có kẻ chực hãm hại." | **chờ duyệt** (bị hãm hại) |
| 6m | "Tham Liêm đóng Tỵ, Hựo [Hợi] hoặc Tham vũ đóng ở Dần Thân mà gặp phải Kỵ, Đà, Không Kiếp tất mắc tù tội" | **chờ duyệt** (tù tội) |
| 6n | "Sát Phá Tham hội Tang Hổ Khốc Khách, Đà, Thiên thương tất gặp lắm tai ương." | **đã thêm**: `TH_6N_SPT_TANG_HO` (bất lợi, 1). Cung vận có Sát / Phá / Tham; đủ sáu sao Tang Môn, Bạch Hổ, Thiên Khốc, Điếu Khách, Đà La, Thiên Thương trong tam phương tứ chính. Lời đọc: "theo sách rất bất lợi", bỏ chữ "tai ương" (chủ dự án quyết, 2026-10-24). |
| 6o | "Tham Liêm, Kình Đà, Hỏa Linh; Kỵ Kiếp Thiên Không tất bị ốm đau nặng." | **chờ duyệt** (bệnh nặng) |

## Đại tiểu hạn có tang (tr.117)

"Khi xem thấy Đại Tiểu hạn có các cách sau đây hải [phải] phòng tang sự". Cả chín mục 7a-i đều **chờ duyệt** (tang):

| Mục | Nguyên văn |
|---|---|
| 7a | "Nhật Nguyệt ngộ Đà la, Thiên không, Hóa kỵ" |
| 7b | "Phủ Tướng ngộ Cô Quả, Thiên Không, Kiếp sát" |
| 7c | "Phủ Tướng ngộ Tang Hổ, Khốc Hư, song Hao" |
| 7d | "Sát Phá Liêm Tham ngộ song Hao, Tang Hổ hay Kình Đà, Khong Kiếp, Khốc Hư." |
| 7e | "Cô Quả, Đào Hồng, Thiên không, Hóa Kỵ" |
| 7f | "Tử Phú Vũ Tướng ngộ Cô Quả, song Hao" |
| 7g | "Nhị tam Không ngộ Tang Hổ, Điếu Tuế" |
| 7h | "Hình Diêu, Kình Đà Không Kiếp, Tang Hổ có đại tang." |
| 7i | "Cơ Nguyệt Đồng Lương ngộ Đại Tiểu hạn (hay Tang Hổ) có đại tang." |

Bị chú của sách (tr.117) đòi cách tang phải có sẵn ở cung Phụ Mẫu rồi tiểu hạn mới gặp, nên dù được duyệt, 7a-i cũng không đọc được trên một cung vận như các luật khác.

## Nhận xét về các luật đã có (chưa sửa, chỉ báo)

So với ảnh trang tr.115 "Đại tiểu hạn phát", ba luật cũ đọc **rộng hơn** sách vì bỏ bớt sao: `TH_TPVT_LOC_TA_HUU` không xét Long Phượng (mục 1), `TH_NDCC_HOA3` không xét "Tướng ấn" (mục 2), `TH_CU_NHAT_SONG_LOC` không xét "Sinh Vượng" (mục 3). `TH_TPVT_KHONG_KIEP_KY` (6c) đòi Không / Kiếp **và** Kỵ, trong khi sách liệt kê "Tam Không, Kiếp Kỵ Hình Đà hay … Linh Hỏa Tang Diêu".
