# Thực Hành tr.115-117: luật đại / tiểu hạn cho biểu đồ vận (indices-3.2.0, 2026-10-24)

Mỗi mục đã đối chiếu **ảnh trang** (`tools/show_page.py TH 115|116|117 --image`); lớp chữ của TH đảo thứ tự dòng nên không dùng. Nguyên văn
chép đúng như sách in, kể cả lỗi in (ghi chú trong ngoặc vuông). Trạng thái:

- **đã thêm**: có trong `engine/data/van_han_rules.json` và `VAN_RULES` (`src/interpret/indices.ts`);
- **đã thêm, lời trung tính**: lời sách nói chuyện chết, tù tội, tai nạn, thương tật, bệnh, bỏng, chết đuối hoặc tang. Chủ dự án quyết (2026-10-24): thêm vào, nhưng người đọc chỉ thấy "theo sách rất bất lợi", không bao giờ thấy sự việc. Nguyên văn chỉ nằm trong tài liệu này. Bên bất lợi, trọng số 1;
- **đã có**: luật cũ đã đọc mục này;
- **không tính được**: điều kiện không thể đọc trên một cung vận, hoặc không có chiều thuận / bất lợi để vẽ.

Số "khớp" là số cung vận khớp trên 1.000 lá của `corpus1000` (mỗi lá 11 cung vận ngoài Mệnh).

Cách đọc chung (ghi trong `tools/build_van_han_rules.py`):

- "Lưỡng hạn" = đại hạn và tiểu hạn như nhau. Mục IX.7-8 phải nói "trùng phùng" khi cả hai cùng một cung, nên khi không nói thì mỗi luật đọc riêng một cung vận.
- Sao làm chủ câu (chính tinh, hay sao đứng đầu câu) ở ngay cung vận.
- Các sao "gặp / ngộ / gia" cũng ở ngay cung vận (như `build_van_han_books.py`), trừ khi hai nhóm sao mà câu sách ghép lại không bao giờ cùng một cung. Ví dụ: Tang Môn, Bạch Hổ với Điếu Khách hay Thái Tuế; Hao với Phục Binh. Khi đó các sao ấy được đọc trong tam phương tứ chính. "hội" luôn là tam phương tứ chính.
- Một cặp sách gọi chung (Kình Đà, Không Kiếp, Cô Quả, Tang Hổ, song Hao, Khốc Hư, Hỏa Linh, Thương Sứ) thì có một sao là đủ, như luật cũ `TH_TPVT_KHONG_KIEP_KY`. Những cặp này phần lớn không bao giờ cùng cung.
- "Nhị tam Không" = từ hai trong bốn Địa Không, Thiên Không, Tuần, Triệt. "Kỵ" = Hóa Kỵ; "Tuế" = Thái Tuế; "Diêu" = Thiên Riêu; "Hình" = Thiên Hình; "Sát" đứng cạnh Phục Binh = Kiếp Sát.
- Luật chỉ cho tiểu hạn (6i, 6j) mang nhãn `han: "tieu"`: biểu đồ chỉ tính ở lớp tiểu hạn; lời đọc đại hạn không nói. Luật cần đại và tiểu hạn cùng một cung (IX.7) mang nhãn `han: "trung_phung"`: chỉ tính ở năm có tiểu hạn đứng đúng cung đại hạn đang đi.
- Tuổi = can / chi năm sinh âm lịch (`tv.year_gz`).

## Mục IX (tr.115)

| Mục | Nguyên văn | Trạng thái | Ghi chú |
|---|---|---|---|
| IX.5 | "Lương hạn [Lưỡng hạn] : Đại, Tiểu mà gặp Trúc la (tức Sát, Phá, Tham) mà gia thêm Cự môn, Linh Hỏa thì xấu xa, tai biến, khong kể xiết." | **không tính được** (và có chữ "tai biến") | Cự Môn không bao giờ đứng trong tam phương tứ chính của Sát / Phá / Tham (kiểm trên 1.000 lá: 0 lần). Đọc "đại hạn ở Sát Phá Tham, tiểu hạn ở Cự Môn" là suy diễn của hệ thống, sách không nói. |
| IX.6 | "Lưỡng hạn của người Giáp rất kỵ Thiên thương và Thiên sứ đóng cung zdần [Dần]. Người tuổi Canh kỵ gặp Thương sứ ơ cung Thân." | **đã thêm**: `TH_IX6_GIAP_THUONG_SU`, `TH_IX6_CANH_THUONG_SU` (bất lợi, 1) | Can năm Giáp + cung vận ở Dần có Thiên Thương hoặc Thiên Sứ; can Canh + cung vận ở Thân. Thương (Nô Bộc) và Sứ (Tật Ách) không bao giờ cùng cung, nên "và" đọc là một trong hai. |
| IX.7 | "Lưỡng hạn trùng phùng ở cung Tí mà gặp Thương, Sứ Kình, Đà, Tuế thì có thẻ nguy đến tánh mạng." | **đã thêm, lời trung tính**: `TH_IX7_TRUNG_PHUNG_TY` | Năm có tiểu hạn và đại hạn cùng ở Tý; tam phương có Thương hoặc Sứ, Kình hoặc Đà, Thái Tuế. Khớp 94 cung (rồi chỉ tính ở năm trùng phùng). |
| IX.8 | "Thương ở cung Tí, Thìn, Mão, Ngọ, Mùi; Thiên sứ ở Dần, Thân, Tỵ, Hợi mà gặp phải Thái tuế thì tai họa ghê gớm. Nếu lưỡng hạn trùng phùng mà không cso sao giải cứu thì nguy đến tính mệnh." | câu đầu **đã thêm, lời trung tính**: `TH_IX8_THUONG_SU_TUE`; câu sau **không tính được** | Câu đầu: cung vận có Thương (ở Tý Thìn Mão Ngọ Mùi) hoặc Sứ (ở Dần Thân Tỵ Hợi), tam phương có Thái Tuế; khớp 228. Câu sau: sách không nói "sao giải cứu" là sao nào. |
| IX.9 | "Người tuổi Thân mà đến lưỡng hạn gặp Thiên thương rất hại, tai họa liên miên." | **đã thêm**: `TH_IX9_THAN_THUONG` (bất lợi, 1) | Lời đọc: "theo sách rất bất lợi", bỏ chữ "tai họa" (chủ dự án quyết, 2026-10-24). |
| IX.10 | "Người tuổi Thin [Thìn], Tuất, Sửu, Mùi mà lưỡng hạn gặp Kình, Đà, không hề gì, trái lại nếu có Tử, Phủ, Xương, Khúc thì lại là hoạnh phát." | **đã thêm**: `TH_IX10_TU_MO_KINH_DA_PHAT` (thuận, 1); `TH_IX10_TU_MO_KINH_DA` (không có chiều) | Vế "không hề gì": chủ dự án quyết (2026-10-24) cho triệt tiêu phần hãm của Kình / Đà ở chính cung đại hạn, lưu đại hạn và tiểu hạn của người tuổi Tứ Mộ. Mục hãm của KL tr.233 vẫn được liệt kê, kèm một mục bù đúng bằng nó (`KL233_HAM_TH115_IX10`), nên "Căn cứ" nói cả hai sách. Nguyệt hạn không bù, vì "lưỡng hạn" là đại và tiểu hạn. |
| IX.11 | "Hạn gặp Thất sát có gia Hình, Hổ, Quan phủ ở cung hãm thì dễ mắc vòng lao lý." | **đã thêm, lời trung tính**: `TH_IX11_SAT_HAM_HINH_HO` | Thất Sát hãm ở cung vận; tam phương có Thiên Hình, Bạch Hổ, Quan Phủ. Khớp 15. |

## Đoán cách ở đại tiểu hạn (tr.116)

| Mục | Nguyên văn | Trạng thái | Ghi chú |
|---|---|---|---|
| 1 | "Đăng khoa hay Thăng chức : Hạn cần có Đào Hồng, Xương Khúc, Khôi Việt, Khoa Quyền hoặc thêm Thai Cáo, Quốc ấn." | **đã có**: `TH_DAO_HONG_KHOA_QUYEN` | |
| 2 | "Hôn phối: Phải xem chính cung Phối năm ấy hay Đại Tiểu hạn có: Sát phá Liêm đào; Vũ Diêu Lộc Mã Hỉ Đào (hay Hồng) …" | **không tính được** | Báo sự kiện cưới hỏi, không có chiều thuận / bất lợi. Lớp sách vận hạn (`build_van_han_books.py`) cũng đã bỏ sự kiện hôn nhân. |
| 3 | "Sinh con: Xem ở Tiểu hạn có : Phủ Tướng Long phượng ngộ sao Thái; …" | **không tính được** | Sự kiện sinh con, không có chiều. |
| 4 | "Tình duyên: dang díu: Nếu số người mà cung Thê có Tả Hữu Hồng Đào chiếu, mà đến Tiểu hạn lại gặp các dâm tinh thì thế tất phải dang díu thêm nợ tình duyên." | **không tính được** | "dâm tinh" không có danh sách; là sự kiện, không có chiều. Đoạn sau nói về cung Thê bẩm sinh. |
| 5 | "về cung duyên dang dở: … khi đến hạn gặp phải tất phải sinh ly hay tử biệt." Bảy cách: "Cô Quả ngộ Không Kiếp; Kình Đà Không Kiếp ngộ Tuần Triệt; Tang Hổ ngộ Đại Tiểu hao; Hình Diêu, Thiên không ngộ Hóa Kỵ; Thất sát, Phá toái ngộ Hư Khốc; Linh Hỏa, Kình Đà, Không Kiếp; Cự môn, ngộ Linh Hỏa" | **đã thêm, lời trung tính**: `TH_DC5_PHOI` | Cung vận là Phu Thê và có một trong bảy cách. Khớp 188. |

## Đại tiểu hạn thất lợi (tr.116-117)

| Mục | Nguyên văn | Trạng thái, điều kiện đã cài |
|---|---|---|
| 6a | "Cơ Nguyệt Đồng Lương hay Cự Nhật mà gặp Kình Đà, Không Kiếp hay Phá toái, Kiếp sát thì dễ tàn tật, mất cướp" | **đã thêm, lời trung tính**: `TH_6A_CNDL_SAT`. Cơ Nguyệt Đồng Lương hoặc Cự Nhật, gặp một trong Kình, Đà, Không, Kiếp, Phá Toái, Kiếp Sát. Khớp 1.356: rộng nhất trong các luật mới, vì sách chỉ đòi một sao. |
| 6b | "Sát phá Liêm Tham mà gặp Nhị tam Không, Linh Hỏa Kình Kỵ hay Đại tiểu Hao Hình, Sát Phục binh, Tang Hổ thì tù ngục vong gia" | **đã thêm, lời trung tính**: `TH_6B_SPLT_KHONG`. Sát Phá Liêm Tham, gặp Nhị tam Không; hoặc Linh/Hỏa, Kình và Kỵ; hoặc (tam phương) Hao, Hình, Kiếp Sát, Phục Binh, Tang/Hổ. Khớp 245. |
| 6c | "Tử Phủ Vũ Tướng  găp phải Tam Không, Kiếp Kỵ Hình Đà hay gặp Linh Hỏa Tang Diêu thì bị giáng chức, phá tài." | **đã có**: `TH_TPVT_KHONG_KIEP_KY` |
| 6d | "Cự Cơ, Đồng Lương mã gặp Kình Đà Không Kiếp, song Hao, Phá toái, Kỵ thì phá tài hay bị thương tật." | **đã thêm, lời trung tính**: `TH_6D_CU_CO_DONG_LUONG`. Cự Cơ hoặc Đồng Lương, gặp một trong Kình, Đà, Không, Kiếp, Hao, Phá Toái, Kỵ. Khớp 147. |
| 6e | "Nguyệt Đồng Cơ Cự mà gặp Không Kiếp Đẩu quân, Tuế, Kỵ, thì bị kiện cáo hay giáng chức." | **đã có**: `TH_NDCC_KHONG_KIEP` |
| 6f | "Nhật Nguyệt gặp Không Kiếp Thiên diêu hay gặp Linh Hỏa, Cô Quả thì đau mắt có thể mù." | **đã thêm, lời trung tính**: `TH_6F_NHAT_NGUYET`. Nhật Nguyệt đồng cung, gặp Không/Kiếp và Riêu, hoặc Linh/Hỏa và Cô/Quả. Khớp 8. |
| 6g | "Phá Liêm Tham gặp Diêu Kỵ, Mộc dúc dễ bị bỏng." | **đã thêm, lời trung tính**: `TH_6G_PHA_LIEM_THAM`. Phá, Liêm hoặc Tham, gặp Riêu, Kỵ, Mộc Dục. Khớp 3. |
| 6h | "Thiên Đồng gặp Kình Kỵ, Mộc Hỏa Không Kiếp hoặc là Cự Kỵ Tuế Đà Không Kiếp thì dễ chết đuối." | **đã thêm, lời trung tính**: `TH_6H_THIEN_DONG`. Thiên Đồng, gặp Kình và Kỵ; hoặc Mộc Dục, Hỏa và Không/Kiếp; hoặc Cự Môn, Kỵ, Thái Tuế, Đà và Không/Kiếp. Khớp 26. |
| 6i | "Tiểu hạn găp Tang Hỏa Linh mà nhất là đóng cung Điền trạch thì dễ bị cháy nhà, hay sản vật." | **đã thêm, lời trung tính**: `TH_6I_TANG_HOA_LINH` (chỉ tiểu hạn). Tang Môn, Hỏa Tinh, Linh Tinh ở cung tiểu hạn. "nhất là đóng cung Điền trạch" là nhấn mạnh, không phải điều kiện. Khớp 14. |
| 6j | "Cơ Lương đóng Thìn Tuất mà Tiểu hạn đến đó gặp phải Tang Điếu, Tuế, Khôcs Hư thì bị ngã từ cao xuống." | **đã thêm, lời trung tính**: `TH_6J_CO_LUONG_THIN_TUAT` (chỉ tiểu hạn). Cơ Lương ở Thìn/Tuất, gặp Tang, Điếu hoặc Tuế cùng Khốc hoặc Hư. Khớp 15. |
| 6k | "Sát Phá Liêm Tham găp Tang Hổ Kình Đà Điếu khách hay là Tham lang gặp Hổ, Điêu, Ly Tuế ở cung Thìn Tuất thì bị xe cán hay thú cắn." | **đã thêm, lời trung tính**: `TH_6K_SPLT_TANG_HO`. Sát Phá Liêm Tham, tam phương có Tang/Hổ, Kình/Đà, Điếu Khách; hoặc Tham Lang ở Thìn/Tuất, tam phương có Hổ, Riêu, Tuế ("Ly" không rõ nghĩa, bỏ). Khớp 654. |
| 6l | "Kinh Không Kiếp gặp Quan phù hay Tử Phù, Trực phù mà có Phục binh thì phòng có kẻ chực hãm hại." | **đã thêm, lời trung tính**: `TH_6L_KINH_KHONG_PHUC_BINH`. Kình, Không hoặc Kiếp cùng Quan Phù, Tử Phù hoặc Trực Phù và Phục Binh. Khớp 44. |
| 6m | "Tham Liêm đóng Tỵ, Hựo [Hợi] hoặc Tham vũ đóng ở Dần Thân mà gặp phải Kỵ, Đà, Không Kiếp tất mắc tù tội" | **đã thêm, lời trung tính**: `TH_6M_THAM_LIEM_VU`. Tham Liêm ở Tỵ/Hợi hoặc Tham Vũ ở Dần/Thân, gặp Kỵ, Đà, Không/Kiếp. Khớp 1. |
| 6n | "Sát Phá Tham hội Tang Hổ Khốc Khách, Đà, Thiên thương tất gặp lắm tai ương." | **đã thêm**: `TH_6N_SPT_TANG_HO` (bất lợi, 1). Cung vận có Sát / Phá / Tham; đủ sáu sao Tang Môn, Bạch Hổ, Thiên Khốc, Điếu Khách, Đà La, Thiên Thương trong tam phương tứ chính. Lời đọc: "theo sách rất bất lợi", bỏ chữ "tai ương" (chủ dự án quyết, 2026-10-24). |
| 6o | "Tham Liêm, Kình Đà, Hỏa Linh; Kỵ Kiếp Thiên Không tất bị ốm đau nặng." | **đã thêm, lời trung tính**: `TH_6O_THAM_LIEM_KY_KIEP`. Tham Liêm gặp Kình/Đà và Hỏa/Linh; hoặc Kỵ, Địa Kiếp, Thiên Không. Khớp 6. |

## Đại tiểu hạn có tang (tr.117)

"Khi xem thấy Đại Tiểu hạn có các cách sau đây hải [phải] phòng tang sự". Cả chín mục 7a-i: **đã thêm, lời trung tính**.

| Mục | Nguyên văn | Luật, điều kiện đã cài |
|---|---|---|
| 7a | "Nhật Nguyệt ngộ Đà la, Thiên không, Hóa kỵ" | `TH_7A_NHAT_NGUYET_DA`. Nhật Nguyệt đồng cung, gặp Đà, Thiên Không, Kỵ. Khớp 2. |
| 7b | "Phủ Tướng ngộ Cô Quả, Thiên Không, Kiếp sát" | `TH_7B_PHU_TUONG_CO_QUA`. Phủ hoặc Tướng, gặp Cô/Quả, Thiên Không, Kiếp Sát. Khớp 59. |
| 7c | "Phủ Tướng ngộ Tang Hổ, Khốc Hư, song Hao" | `TH_7C_PHU_TUONG_TANG_HO`. Phủ hoặc Tướng, gặp Tang/Hổ, Khốc/Hư, Hao. **Khớp 0** trên 1.000 lá: có thể không bao giờ khớp trên một cung. |
| 7d | "Sát Phá Liêm Tham ngộ song Hao, Tang Hổ hay Kình Đà, Khong Kiếp, Khốc Hư." | `TH_7D_SPLT_HAO_TANG`. Sát Phá Liêm Tham, gặp Hao và Tang/Hổ; hoặc Kình/Đà, Không/Kiếp, Khốc/Hư. Khớp 124. |
| 7e | "Cô Quả, Đào Hồng, Thiên không, Hóa Kỵ" | `TH_7E_CO_QUA_DAO_HONG`. Cô/Quả, Đào/Hồng, Thiên Không, Kỵ. Khớp 15. |
| 7f | "Tử Phú Vũ Tướng ngộ Cô Quả, song Hao" | `TH_7F_TPVT_CO_QUA_HAO`. Tử Phủ Vũ Tướng, gặp Cô/Quả và Hao. Khớp 55. |
| 7g | "Nhị tam Không ngộ Tang Hổ, Điếu Tuế" | `TH_7G_KHONG_TANG_HO`. Nhị tam Không ở cung vận; tam phương có Tang/Hổ và Điếu/Tuế. Khớp 286. (Đọc cả "Không" trong tam phương thì khớp 3.278 cung: Tang Hổ Điếu Tuế luôn đứng sẵn trong tam phương của nửa số cung, nên điều kiện không còn phân biệt gì.) |
| 7h | "Hình Diêu, Kình Đà Không Kiếp, Tang Hổ có đại tang." | `TH_7H_HINH_KINH_TANG`. Hình/Riêu, Kình/Đà, Không/Kiếp, Tang/Hổ. Khớp 7. |
| 7i | "Cơ Nguyệt Đồng Lương ngộ Đại Tiểu hạn (hay Tang Hổ) có đại tang." | `TH_7I_CNDL_TANG_HO`. Cơ Nguyệt Đồng Lương, gặp Tang/Hổ. Khớp 485. |

Bị chú của sách (tr.117) nói muốn **đoán tang** thì cách phải có sẵn ở cung Phụ Mẫu, rồi tiểu hạn mới gặp. Hệ thống không đoán tang, chỉ nói "theo sách rất bất lợi", nên chưa áp điều kiện Phụ Mẫu ấy. **Xin chủ dự án xem**: nếu muốn theo sát Bị chú, 7a-i sẽ chỉ tính khi cung Phụ Mẫu bẩm sinh có cách tương ứng. Luật "cát tinh chiếm 2/3" trong Bị chú vẫn không tính được, vì sách không kèm danh sách cát tinh.

## Nhận xét về các luật đã có (chưa sửa, chỉ báo)

So với ảnh trang tr.115 "Đại tiểu hạn phát", ba luật cũ đọc **rộng hơn** sách vì bỏ bớt sao: `TH_TPVT_LOC_TA_HUU` không xét Long Phượng (mục 1), `TH_NDCC_HOA3` không xét "Tướng ấn" (mục 2), `TH_CU_NHAT_SONG_LOC` không xét "Sinh Vượng" (mục 3). `TH_TPVT_KHONG_KIEP_KY` (6c) đòi Không / Kiếp **và** Kỵ, trong khi sách liệt kê "Tam Không, Kiếp Kỵ Hình Đà hay … Linh Hỏa Tang Diêu".
