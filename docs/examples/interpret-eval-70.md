# Đánh giá trên 70 lá số × 10 chương (e76cb546f1fe7888)

| chương | số chữ (min / trung vị / max) | căn cứ độc lập (trung vị) | đạt | cảnh báo | câu sách trùng nguyên văn giữa hai lá số (trung vị / max) | CPU ms (trung vị / max) |
|---|---|---|---|---|---|---|
| menh | 775 / 1269 / 1488 | 22 | 70/70 | near_duplicate_sentence×1, excessive_repetition×1 | 0% / 33% | 11.4 / 24.2 |
| cong_danh | 509 / 968 / 1411 | 11 | 70/70 | excessive_repetition×3, contradiction_not_explained×1 | 0% / 64% | 7.4 / 13.8 |
| tai_bach | 446 / 807 / 1231 | 6 | 70/70 | — | 0% / 38% | 5.6 / 8.9 |
| dien_trach | 227 / 572 / 935 | 2 | 70/70 | possible_inflation×1 | 0% / 50% | 3.2 / 5.8 |
| phu_the | 327 / 578 / 973 | 3 | 70/70 | possible_inflation×2, weak_personalization×1 | 0% / 40% | 3.3 / 6.4 |
| phuc_duc | 221 / 535 / 897 | 2 | 70/70 | — | 0% / 40% | 3.1 / 5.9 |
| gia_dao | 392 / 559 / 862 | 3 | 70/70 | — | 0% / 60% | 4.7 / 8.3 |
| di_no_tat | 458 / 711 / 1086 | 5 | 70/70 | near_duplicate_sentence×2, excessive_repetition×1 | 0% / 50% | 5.8 / 9.7 |
| van_han | 440 / 669 / 844 | 0 | 70/70 | — | 0% / 0% | 2.0 / 3.5 |
| bat_tu | 572 / 624 / 659 | 0 | 70/70 | — | 0% / 0% | 3.1 / 4.1 |

Suy luận dùng chung cho mọi chương của một lá số (luật + bằng chứng + đồ thị): trung vị 36.2 ms, max 56.5 ms; cột CPU ở trên là phần riêng của từng chương (Node v24.7.0, máy phát triển; số đo trên Worker sẽ khác).

## Chương có cảnh báo hoặc lỗi

- lá số 10 (Triệt tại Mệnh), cong_danh: excessive_repetition — 1230 chữ, 17 căn cứ
- lá số 10 (Triệt tại Mệnh), dien_trach: possible_inflation — 379 chữ, 1 căn cứ
- lá số 17 (Quan Lộc vô chính diệu), cong_danh: excessive_repetition — 1219 chữ, 18 căn cứ
- lá số 26 (Thái Dương hãm tại Mệnh), menh: near_duplicate_sentence — 1224 chữ, 26 căn cứ
- lá số 33 (sweep ql_Hóa Quyền,ql_major:Thiên Tướng,ql_major:Vũ Khúc,ql_pair,ql_tuan,tp_loc_ma), di_no_tat: near_duplicate_sentence — 1000 chữ, 9 căn cứ
- lá số 35 (sweep now_in_ql_decade,ql_Hóa Khoa,ql_Hóa Quyền,ql_major:Phá Quân,ql_major:Vũ Khúc,ql_pair), menh: excessive_repetition — 1418 chữ, 34 căn cứ
- lá số 35 (sweep now_in_ql_decade,ql_Hóa Khoa,ql_Hóa Quyền,ql_major:Phá Quân,ql_major:Vũ Khúc,ql_pair), cong_danh: excessive_repetition — 1035 chữ, 17 căn cứ
- lá số 40 (sweep ql_major:Liêm Trinh,ql_major:Thiên Phủ,ql_pair,tp_loc_ma,tp_sat_0), di_no_tat: near_duplicate_sentence, excessive_repetition — 856 chữ, 6 căn cứ
- lá số 47 (sweep now_in_ql_decade,ql_major:Liêm Trinh,ql_major:Phá Quân,ql_pair,tp_sat_0), cong_danh: contradiction_not_explained — 1064 chữ, 12 căn cứ
- lá số 64 (sweep menh_vcd,ql_major:Cự Môn,ql_major:Thái Dương,ql_pair,ql_triet,ql_tuan), phu_the: possible_inflation — 377 chữ, 1 căn cứ
- lá số 68 (sweep menh_vcd,passed_ql_decade,ql_Hóa Lộc,ql_Hóa Quyền,ql_major:Cự Môn,ql_major:Thái Dương), phu_the: weak_personalization, possible_inflation — 386 chữ, 1 căn cứ
