# Đánh giá trên 30 lá số × 10 chương (5a2d77eae69ab07f)

| chương | số chữ (min / trung vị / max) | căn cứ độc lập (trung vị) | đạt | cảnh báo | câu sách trùng nguyên văn giữa hai lá số (trung vị / max) | CPU ms (trung vị / max) |
|---|---|---|---|---|---|---|
| menh | 904 / 1336 / 1476 | 24 | 30/30 | — | 0% / 25% | 14.0 / 28.5 |
| cong_danh | 508 / 1044 / 1496 | 12 | 30/30 | excessive_repetition×1 | 0% / 29% | 7.8 / 15.1 |
| tai_bach | 550 / 880 / 1252 | 7 | 30/30 | — | 0% / 40% | 5.7 / 8.0 |
| dien_trach | 227 / 536 / 887 | 2 | 30/30 | possible_inflation×1 | 0% / 13% | 2.9 / 5.4 |
| phu_the | 327 / 621 / 956 | 3 | 30/30 | — | 0% / 20% | 3.4 / 6.1 |
| phuc_duc | 221 / 563 / 925 | 3 | 30/30 | — | 0% / 20% | 3.4 / 6.6 |
| gia_dao | 392 / 629 / 905 | 3 | 30/30 | — | 0% / 29% | 4.7 / 8.5 |
| di_no_tat | 458 / 733 / 1134 | 5 | 30/30 | excessive_repetition×1 | 0% / 20% | 5.8 / 9.6 |
| van_han | 440 / 718 / 868 | 0 | 30/30 | — | 0% / 0% | 2.0 / 3.6 |
| bat_tu | 580 / 625 / 659 | 0 | 30/30 | — | 0% / 0% | 3.1 / 6.6 |

Suy luận dùng chung cho mọi chương của một lá số (luật + bằng chứng + đồ thị): trung vị 36.0 ms, max 51.8 ms; cột CPU ở trên là phần riêng của từng chương (Node v24.7.0, máy phát triển; số đo trên Worker sẽ khác).

## Chương có cảnh báo hoặc lỗi

- lá số 4 (random), di_no_tat: excessive_repetition — 1134 chữ, 12 căn cứ
- lá số 10 (Triệt tại Mệnh), dien_trach: possible_inflation — 379 chữ, 1 căn cứ
- lá số 17 (Quan Lộc vô chính diệu), cong_danh: excessive_repetition — 1269 chữ, 18 căn cứ
