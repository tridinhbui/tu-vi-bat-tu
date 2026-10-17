# Phase 6: sẵn sàng production và kiểm chứng học thuật (dựa trên `6e88e38`)

Báo cáo do `tools/bazi_deep_phase6_report.py` sinh ra; các bảng được tính lại từ engine. Không có thuật toán mới trong Phase 6.

## 1. Kết luận: **CONDITIONAL GO**

| Phạm vi | Quyết định | Bằng chứng |
|---|---|---|
| Đưa khối `yongshen` *cộng thêm* (meta, trace, so sánh, cờ mâu thuẫn) ra API/UI **dưới nhãn bản nháp** theo hợp đồng `docs/BAZI_DEEP_API_CONTRACT.md` | **GO có điều kiện** | cách ly hai chiều: 0 sai lệch trên 5000 lá số; hợp đồng được kiểm bằng schema trên pipeline và API; tương thích ngược với `d0c3ab8`; không rò nội dung experimental; 949+ test qua trên HEAD sạch |
| Trình bày bất kỳ dụng thần nào như *đã được chứng minh* hay như *một kết luận duy nhất* | **NO-GO** | `empirical_validated = no` ở mọi phương pháp; không phương pháp nào `source_rule_verified = yes`; trong 10 ví dụ của sách, khớp hoàn toàn 3, một phần 6, không khớp 1; bảng điều hậu không rõ nguồn (tr.388); chín ô sách tự mâu thuẫn |
| Gỡ nhãn *bản nháp* hay nói 'đã người kiểm' | **NO-GO** | chưa có người nào kiểm 120 ô; ví dụ 4 có ngày dựng lại; ví dụ 5 chỉ một người đọc |

Điều kiện để GO có hiệu lực: (C1) phiên sở hữu `api.py`/`web/` gắn hợp đồng nguyên văn, kể cả nhãn ba mức xác minh và câu *không có kết luận thống nhất*; (C2) banner bản nháp luôn hiện; (C3) UI không dựa vào khóa chỉ có ở một số trạng thái (`methods.*.note`). Danh sách đầy đủ ở mục 7.

## 2. Ma trận cách ly trường phái

Mẫu: **5000** lá số hợp lệ: đủ 60 trụ ngày × 12 tháng (720 tổ hợp, năm và giờ ngẫu nhiên) cộng ngẫu nhiên có hạt giống cố định. Số lượng từng loại trong mẫu (mỗi loại có ngưỡng tối thiểu trong test):

| Loại lá số | Số lá số |
|---|---|
| hệ thống nhận ngoại cách chân | 162 |
| TVH nhận cách đặc biệt | 562 |
| TVH tòng (tài/sát/nhi) | 206 |
| TVH chuyên vượng/hóa khí | 356 |
| cả hai trường phái cùng nhận ngoại cách | 83 |
| sát ngưỡng 40% (±0,03) | 502 |
| Nhật Chủ vượng theo 40% | 3226 |
| Nhật Chủ nhược theo 40% | 1774 |
| có bất đồng giữa các phương pháp | 4097 |

**2a. Bật profile TVH có đổi kết quả của hệ thống không?** (số lá số bị đổi, trên toàn bộ mẫu)

| Đầu ra của hệ thống | Bị đổi |
|---|---|
| trạng thái nội cách và tên nội cách (`geju.inner`) | 0/5000 |
| ngoại cách của hệ thống (`geju.outer`, không tính cách TVH) | 0/5000 |
| phương pháp `phu_uc` | 0/5000 |
| phương pháp `dieu_hau` | 0/5000 |
| phương pháp `cach_cuc` | 0/5000 |
| phương pháp `thong_quan` | 0/5000 |
| phương pháp `thuan_the` | 0/5000 |
| phương pháp `khuyet_hanh` | 0/5000 |

**2b. Đổi một tham số chỉ thuộc hệ thống có làm đổi TVH không?** (1667 lá số mỗi dòng)

| Tham số | Lá số mà phương pháp hệ thống đổi | Lá số mà kết luận TVH (status/yong/xi/ji) hoặc điểm TVH đổi | Lá số mà chú thích hiện diện `yong_health` của TVH đổi |
|---|---|---|---|
| `level_cuts` | 1466 | **0** | 0 |
| `presence_share` | 94 | **0** | 0 |
| `thuong_vuong` | 35 | **0** | 0 |
| `tong_cuong_min` | 11 | **0** | 0 |
| `tong_vuong_ti` | 16 | **0** | 0 |
| `tong_foe_max` | 158 | **0** | 0 |
| `tong_the_each` | 4 | **0** | 0 |
| `tong_dominant_share` | 153 | **0** | 0 |
| `tong_chan_tia` | 0 | **0** | 0 |
| `tong_gia_tia` | 0 | **0** | 0 |
| `tong_max_ratio` | 50 | **0** | 0 |
| `war_share` | 1551 | **0** | 0 |
| `bridge_min` | 237 | **0** | 0 |
| `hua_du_share` | 1 | **0** | 0 |
| `flow_min` | 0 | **0** | 0 |
| `hidden_frac` | 987 | **0** | 0 |
| `season_factor` | 1269 | **0** | 1 |
| `class_weight` | 47 | **0** | 11 |
| `kho_policy` | 6 | **0** | 0 |
| `level_margin` | 727 | **0** | 0 |

Ghi chú: `season_factor` và `class_weight` đi qua lớp tương tác dùng chung (`interact.resolve`), nên chúng chỉ có thể đổi chú thích hiện diện `yong_health`/`xi_health`, không đổi kết luận. Đây là lớp chung có chủ ý (cùng bản đồ thấu/tàng can cho cả hai trường phái).

**2c. Đổi một tham số chỉ thuộc TVH có làm đổi hệ thống không?**

| Tham số | Lá số mà hệ thống (phương pháp, nội cách, ngoại cách) đổi | Lá số mà TVH đổi |
|---|---|---|
| `tvh_no_help` | **0** | 108 |
| `tvh_tong_main` | **0** | 49 |
| `chuyen_vuong_chars` | **0** | 46 |
| `chuyen_vuong_share` | **0** | 36 |
| `tvh_margin` | **0** | 1484 |

Kết quả hai chiều: không có dòng nào của cột in đậm khác 0.

## 3. Xử lý bất đồng `phu_uc`

`phu_uc` giữ nguyên, dựa trên khí thế của hệ thống. Việc không còn dùng ngưỡng 40% là **hệ quả có chủ đích của cách ly trường phái**, và được ghi trong `yongshen.isolation.note` và `meta.strength_basis = 'he_thong (tách khỏi điểm TVH)'`. Trong mẫu, Nhật Chủ theo hệ thống và theo 40% bất đồng ở một phần lớn lá số (test `test_phu_uc_never_reads_the_40_percent_decision_by_design` ghi ≥ 100/1.500). Hai hệ không được trộn để tăng tỉ lệ khớp. Đề xuất `phu_uc_tvh` riêng (chưa triển khai, kèm điều kiện và test chấp nhận) ở `docs/BAZI_DEEP_PHU_UC_TVH_PROPOSAL.md`.

## 4. Bảng bất đồng nguồn

| # | Bất đồng | Giữa | Xử lý trong engine | Ai quyết |
|---|---|---|---|---|
| 1 | 9 ô điều hậu: bảng tr.389–390 và chú thích tr.391–396 nêu tập can khác nhau (5 thay thế, 3 chú thích thêm, 1 bảng thêm) | bảng ↔ chú thích của cùng một sách | giữ tập can của bảng; can chỉ ở chú thích không được thăng cấp; cờ `book_internal_conflict`; can chủ không bị ảnh hưởng ở cả 9 ô | người phụ trách học thuật, sau khi có người kiểm ảnh |
| 2 | Bảng điều hậu do một độc giả tặng, tác giả không biết nguồn (tr.388) | độ tin cậy của nguồn | chỉ ghi `transcription_verified`; không nâng `source_rule_verified` | — |
| 3 | Ví dụ 2 tr.398: sách đọc *nhược* ('không có gốc') trong khi giờ Tý và tàng can Tân/Canh có mặt; quy tắc 40% cho 41,85% vượng | lời văn ↔ quy tắc 40% của chính sách | báo cả hai cách đọc (biên heuristic), đánh dấu cách đọc theo quy tắc | — |
| 4 | Ví dụ 3 tr.399: sách chọn Thủy+Mộc theo cân bằng ngũ hành, không theo bảng cách cục của chính nó (bảng cho Quan Sát+Tài) | ví dụ ↔ bảng cách × vượng/nhược | giữ nguyên kết quả bảng; `dieu_hau` và `khuyet_hanh` tái lập lựa chọn của sách; hiển thị bất đồng | — |
| 5 | Ví dụ 5 tr.400–401: bảng cho Quan Sát làm dụng thần, sách coi Hỏa (Quan Sát) là kỵ và Kim (Tỉ) là hỉ | ví dụ ↔ bảng cách | giữ nguyên; ghi trong test là xung đột; hiển thị bất đồng | — |
| 6 | Ví dụ 4 tr.400: sách đọc thân vượng thường dùng Thực Thương; engine nhận Tòng Vượng (hệ thống) và Nhuận Hạ (TVH) chân | ví dụ ↔ điều kiện nhận cách của chính sách (đã vận hành bằng ngưỡng hệ thống) | không điều chỉnh ngưỡng; hiển thị là không khớp | người phụ trách học thuật |
| 7 | Ví dụ 4 tr.399–400: bảng in vỡ ('Quý hợi | Ất | Quí | Tị tân hợi'); ví dụ 2: hàng thập thần tàng can in 'Ất tài quan' (nghi lỗi in); ví dụ 3: ngày in '129' | lỗi in trong bản dịch/scan | ví dụ 4 ghi `pillar_basis` từng trụ; hai lỗi in được ghi nhận, không dùng | — |
| 8 | Ví dụ 1 tr.387: sách lấy Đinh hỏa, chú thích tháng Tuất của Kỷ xếp Giáp đầu (Đinh không có trong ô) | ví dụ ↔ chú thích | engine xếp Giáp đầu, Bính (cùng nhóm Ấn với Đinh) là Hỷ; ghi 'khớp một phần' | — |

Chín ô ở dòng 1 được liệt kê đầy đủ ở `docs/BAZI_DEEP_TVH_AUDIT.md` mục 2 và đánh dấu ⚠ trong phiếu `docs/BAZI_DEEP_TVH_CELLS_CHECK.md`.

## 5. Ví dụ 4 và 5: dựng lại hay đọc trực tiếp

**Ví dụ 4 (tr.399–400):**

- year: read_directly: 'Năm 1973' = Quý Sửu; hàng 'Tỉ' và tàng can 'Tị tân quý' đều in
- month: derived: không in tên trụ; suy từ hàng đại vận bắt đầu Ất Sửu (thuận) và 'sinh ở tháng tí'; lịch cho tháng Giáp Tý của năm Quý
- day: reconstructed: ô trụ ngày in vỡ ('Ất'); suy từ 'nhật nguyên quý thuỷ', tàng can Ất của Mão, lịch (2/1/1974 = Quý Mão)
- hour: read_directly: 'Quý hợi' in ở cột giờ

**Ví dụ 5 (tr.400–401), Canh Ngọ…:** bốn trụ **đọc trực tiếp** (in rõ ở tr.400), hàng đại vận nhất quán; một người đọc, chưa có lượt chép mù. Kết quả đối chiếu: Nhật Chủ vượng (khớp); `dieu_hau` cho đúng tập {Thủy, Mộc} của sách (khớp tập); `khuyet_hanh` tìm thấy Thủy nhưng không Mộc (một phần); `cach_cuc_tvh` và `phu_uc` chứa Kim (Tỉ) trong Kỵ trong khi sách coi Kim là Hỉ, và `cach_cuc_tvh` lấy Quan Sát làm dụng trong khi sách coi Hỏa là Kỵ (xung đột). Kết luận: khớp một phần, không điều chỉnh.

Ví dụ 6 bắt đầu ở cuối tr.401; ngoài phạm vi, chưa đọc.

## 6. Quy trình kiểm độc lập 120 ô

`docs/BAZI_DEEP_TVH_REVIEW_PROTOCOL.md` + phiếu CSV (`docs/bazi_deep_tvh_cells_check.csv`, có cột ảnh-theo-người-kiểm) + công cụ `tools/bazi_deep_tvh_review_intake.py`. Công cụ không sửa dữ liệu, không giải quyết 9 ô mâu thuẫn, coi cùng một người điền hai lần là một người. Hiện trạng: **0/120 ô có người kiểm** (`no_review`).

## 7. Checklist điều kiện còn thiếu trước production

- [ ] Người kiểm độc lập: ≥ 1 người, tốt nhất 2, điền phiếu 120 ô và ví dụ 4–5 (hiện 0).
- [ ] Quyết định học thuật về 9 ô `book_internal_conflict` (hiện: không chọn bên nào).
- [ ] Phiên sở hữu `api.py`/`web/` gắn hợp đồng (schema + chuỗi UI); hiện hợp đồng chỉ là tài liệu. PR #1 (zz-api-integration) cũng sửa `api.py`: cần thống nhất thứ tự.
- [ ] UI hiển thị ba mức xác minh riêng, câu *không có kết luận thống nhất*, banner nháp; không dùng cụm trong `forbidden_phrases`.
- [ ] Quyết định về `phu_uc` (giữ theo hệ thống) và về việc có làm `phu_uc_tvh` hay không (cần đoạn nguồn nói trực tiếp).
- [ ] Nghiên cứu thực nghiệm về giá trị dự báo (hiện không có; `empirical_validated` phải giữ `no`).
- [ ] Ví dụ 4: người đối chiếu trụ ngày dựng lại; ví dụ 5: lượt chép mù hoặc người kiểm.
- [ ] Ngưỡng của hệ thống (đúng 40%, biên ±0,03, các ngưỡng nhận diện) vẫn không có căn cứ nguồn; giữ nhãn heuristic.
- [x] Cách ly hai chiều trên ≥ 5.000 lá số (mục 2).
- [x] Tương thích ngược khóa phản hồi so với `d0c3ab8` (cộng thêm; chỉ `methods.*.note` phụ thuộc trạng thái).
- [x] Không rò nội dung experimental: mã và dữ liệu `bazi_deep` không tham chiếu `experimental`, phản hồi API không chứa.

## 8. Hồ sơ regression trên HEAD sạch

Chạy bằng `git worktree` tách riêng (không có file của phiên khác), ghi tay lúc chạy:

| Cây mã | Kết quả |
|---|---|
| `eae32e4` (HEAD khi chạy; có thêm commit của phiên công thức Tử Vi), sạch | 1023 passed, 1 skipped, 2 xfailed, 0 failed |
| `eae32e4` + các file Phase 6 (không `api.py`, không `web/`, không `compare_deep`) | **1073 passed, 1 skipped, 2 xfailed, 0 failed** (+50 test mới) |
| cây làm việc chung (có file `web/` và `test_beginner_ux.py` của phiên khác đang sửa) | 1074 passed, 1 skipped, 2 xfailed, 0 failed |

## 9. Phân loại lỗi

- **Lỗi mới do Phase 6:** khi phát triển, 3 giả định sai trong test của chính Phase 6 và 1 bộ lọc ví dụ trong test Phase 4 (ví dụ 5 vào bộ ba ví dụ) đã bị bắt và sửa; còn lại 0.
- **Lỗi baseline:** 0 test fail trên `eae32e4` sạch; 2 xfailed và 1 skipped có sẵn.
- **Lỗi do cây làm việc đang sửa:** xem dòng thứ ba của bảng; nếu có, nằm ở file của phiên khác, không ở file Phase 6.

## 10. Phát hiện kỹ thuật của Phase 6

1. Ở quy mô 5.000 lá số, thử đổi `season_factor` và `class_weight` thì chú thích hiện diện `yong_health` của phương pháp TVH đổi (qua lớp tương tác dùng chung `interact.resolve`), nhưng kết luận (status/yong/xi/ji) không đổi. Đã ghi vào hợp đồng và test thay vì coi là rò rỉ; không sửa thuật toán.
2. Khóa `methods.cach_cuc_tvh.note` có ở d0c3ab8 cho lá số 1990-12-15 nhưng nay vắng, vì từ Phase 5 ngoại cách của hệ thống không còn thay nội cách của TVH. Đây là khóa phụ thuộc trạng thái; hợp đồng cấm UI dựa vào nó.

