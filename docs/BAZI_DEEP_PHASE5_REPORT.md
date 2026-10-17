# Phase 5: kiểm chứng độc lập và cách ly trường phái

Báo cáo do `tools/bazi_deep_phase5_report.py` sinh ra; các bảng được tính lại từ engine. Không có phương pháp mới. Kết quả regression (mục 8–9) được ghi tay lúc chạy.

## 1. Ba mức xác minh

- `transcription_verified`: bảng hoặc văn bản đã chép đúng từ trang nguồn.
- `source_rule_verified`: công thức hoặc điều kiện (kể cả ngưỡng) khớp trực tiếp với điều nguồn nói.
- `empirical_validated`: có bằng chứng độc lập về giá trị dự báo.

Ba mức tách rời, không suy từ mức này sang mức khác. **Không phương pháp nào đạt `empirical_validated`; không phương pháp nào đạt `source_rule_verified` trọn vẹn.**

| Phương pháp | transcription | source_rule | empirical | Lý do | Nguồn |
|---|---|---|---|---|---|
| `phu_uc` | n/a | no | no | nguyên lý phổ thông của hệ thống, không có nguồn đối chiếu | he_thong (nguyên lý phù ức phổ thông; ngưỡng cấp độ khí thế là của hệ thống) |
| `dieu_hau` | yes | partial | no | bảng và thứ tự chép khớp trang in (120/120 bảng, chú thích có 9 ô mâu thuẫn nội bộ); vai trò Dụng/Hỷ và ngưỡng hàn/nhiệt là của hệ thống | SRC_TVH_DIEUHAU tr.389-390 (tập can); SRC_TVH_DIEUHAU tr.391-396 (thứ tự); SRC_TTT_HANTHU tr.113-114 (hàn/noãn) |
| `cach_cuc` | partial | no | no | chỉ phần Thương Quan (TTT tr.93-94) chép khớp; phần còn lại là bảng nháp | he_thong (bảng cách cục nháp); SRC_TTT_THUONGQUAN tr.93-94 (Thương Quan) |
| `cach_cuc_tvh` | yes | partial | no | bảng tr.378-386 chép khớp, quy tắc 40% khớp tr.355; biên ±0,03, quy ước đúng 40% và các ví dụ (1/3 khớp hoàn toàn) chưa đủ | SRC_TVH_DUNGTHAN tr.378-386 (bảng cách × vượng/nhược × nhóm nhiều nhất); SRC_TVH_DIEM tr.355 (ngưỡng 40%) |
| `thong_quan` | n/a | no | no | không có nguồn; ngưỡng của hệ thống | he_thong (nguyên lý thông quan; ngưỡng war_share/bridge_min là của hệ thống) |
| `thuan_the` | yes | partial | no | bảng vai trò TTT tr.171-179 chép khớp; ngưỡng nhận diện và hóa thần dư/thiếu là của hệ thống | SRC_TTT_TONG tr.171-179 (vai trò các loại tòng); SRC_TTT_HOA tr.175-176 (hóa thần) |
| `thuan_the_tvh` | yes | partial | no | bảng tr.381-386 chép khớp; điều kiện nhận diện được vận hành bằng ngưỡng của hệ thống | SRC_TVH_DUNGTHAN tr.381-386 |
| `khuyet_hanh` | n/a | no | no | chỉ một ví dụ tr.399, sách không phát biểu thành quy tắc | SRC_TVH_DUNGTHAN tr.399 (ví dụ 3: ngũ hành thiếu mộc, thủy thì dụng mộc, thủy) |

Ghi chú: quy tắc 40% (tr.355) riêng nó là `source_rule_verified = yes` về con số và phép so sánh (tái lập hai phép thử số của sách); phần đúng 40% và biên ±0,03 là của hệ thống. Bảng điều hậu được chép đúng nhưng chính tác giả nói không biết nguồn của nó (tr.388), nên không có cơ sở để nói nó đúng về mặt học thuật.

## 2. Ma trận cách ly trường phái

Mẫu: 1200 lá số hợp lệ sinh ngẫu nhiên có hạt giống cố định (đủ các loại: ngoại cách của hệ thống, cách đặc biệt của Thiệu Vĩ Hoa, tòng, sát vượng, sát ngưỡng 40%, dụng thần xung đột; số lượng từng loại được test ép tối thiểu).

**2a. Bật profile TVH (`he_thong` → `tvh_40`) có đổi kết quả của hệ thống không?** (số lá số bị đổi)

| Đầu ra của hệ thống | Trước khi sửa (d0c3ab8) | Sau khi sửa |
|---|---|---|
| trạng thái thành/bại của nội cách (`geju.inner`) | 42/1200 | 0/1200 |
| ngoại cách của hệ thống (`geju.outer`, không tính cách TVH) | 15/1200 | 0/1200 |
| phương pháp `phu_uc` | 995/1200 | 0/1200 |
| phương pháp `dieu_hau` | không đo | 0/1200 |
| phương pháp `cach_cuc` | 0/1200 | 0/1200 |
| phương pháp `thong_quan` | không đo | 0/1200 |
| phương pháp `thuan_the` | 0/1200 | 0/1200 |
| phương pháp `khuyet_hanh` | không đo | 0/1200 |

Trước khi sửa, `phu_uc` đổi ở 995/1200 lá số vì đọc quyết định vượng/nhược của TVH (và mức khí thế khác tên); nay `phu_uc` dùng khí thế của hệ thống nên không đổi.

**2b. Ngược lại: đổi đầu vào của hệ thống có làm đổi kết quả TVH không?** Mỗi dòng là một tham số chỉ thuộc hệ thống bị đổi mạnh (300 lá số, profile `tvh_40`).

| Tham số hệ thống bị đổi | Số lần phương pháp hệ thống đổi (cộng 6 phương pháp × 300 lá số) | Số lá số mà `cach_cuc_tvh`/`thuan_the_tvh`/điểm TVH đổi |
|---|---|---|
| `level_cuts` | 273 | **0** |
| `presence_share` | 10 | **0** |
| `thuong_vuong` | 2 | **0** |
| `tong_cuong_min` | 6 | **0** |
| `tong_vuong_ti` | 12 | **0** |
| `tong_foe_max` | 84 | **0** |
| `tong_the_each` | 3 | **0** |
| `tong_dominant_share` | 24 | **0** |
| `war_share` | 280 | **0** |
| `bridge_min` | 60 | **0** |
| `hua_du_share` | 1 | **0** |
| `flow_min` | 0 | **0** |
| `hidden_frac` | 240 | **0** |
| `season_factor` | 413 | **0** |
| `class_weight` | 6 | **0** |
| `kho_policy` | 1 | **0** |

**2c. Đổi tham số chỉ thuộc TVH có làm đổi hệ thống không?**

| Tham số TVH bị đổi | Số lá số mà phương pháp / cách cục của hệ thống đổi | Số lá số mà phương pháp TVH đổi |
|---|---|---|
| `tvh_no_help` | **0** | 22 |
| `tvh_tong_main` | **0** | 11 |
| `chuyen_vuong_chars` | **0** | 12 |
| `chuyen_vuong_share` | **0** | 7 |
| `tvh_margin` | **0** | 269 |

Trước khi sửa còn một rò rỉ ngược: ở 13/1200 lá số, ngoại cách *của hệ thống* làm `cach_cuc_tvh` thành 'không xác định nội cách'. Nay `cach_cuc_tvh` và `thuan_the_tvh` chỉ thấy cách đặc biệt TVH (0 trường hợp).

**Phần chung không bị cách ly (cố ý):** thông tin đầu vào của lá số, phân giải tương tác (`interact.resolve`) và việc nhận diện *tên* nội cách từ nguyệt lệnh là lớp dùng chung; test xác nhận tên nội cách giống nhau ở cả hai profile trên 1200 lá số.

## 3. Bảng ví dụ đối chứng (tr.387–400)

Đầu vào của cả 9 ví dụ được đối chiếu với một lượt chép mù độc lập (`tests/golden/tvh_examples_blind.json`): 9/9 khớp bốn trụ. Ví dụ 4 (tr.399–400) có bảng in bị vỡ nên bốn trụ được **dựng lại** từ lời văn, hàng đại vận và lịch; lượt chép mù dựng ra đúng cùng bốn trụ. Không điều chỉnh thuật toán để ép khớp.

| Ví dụ | Lá số | Sách đọc | Sách chọn | Engine: 40% | cach_cuc_tvh | dieu_hau | phu_uc (hệ thống) | khuyet_hanh | Đánh giá |
|---|---|---|---|---|---|---|---|---|---|
| p397_vd1 | Nhâm Thìn / Tân Hợi / Mậu Tuất / Bính Thìn | vượng | QuanSat | 0.5523 → vượng | QuanSat | QuanSat An | An | — | khớp hoàn toàn ở cach_cuc_tvh và dieu_hau; phu_uc (hệ thống, khí thế cực nhược) không khớp |
| p398_vd2 | Ất Mão / Bính Tuất / Quý Tỵ / Nhâm Tý | nhược | An | 0.4185 → vượng | hai cách đọc: QuanSat ThucThuong / An | An ThucThuong Ti | An | — | khớp một phần: dieu_hau và phu_uc khớp dụng thần; vượng/nhược không tái lập bằng 40% |
| p399_vd3 | Canh Tuất / Bính Tuất / Tân Tỵ / Đinh Dậu | vượng | ThucThuong Tai | 0.7373 → vượng | QuanSat | ThucThuong Tai | hai_cach_doc: QuanSat ThucThuong Tai / QuanSat ThucThuong Tai | Tai ThucThuong | khớp một phần: dieu_hau và khuyet_hanh khớp, cach_cuc_tvh chỉ có Tài |
| p400_vd4 (dựng lại) | Quý Sửu / Giáp Tý / Quý Mão / Quý Hợi | cực vượng | ThucThuong | 0.7598 → vượng | không xác định nội cách (ngoại cách TVH) | Tai An | khong_ap_dung | Tai | KHÔNG khớp: engine đọc ngoại cách (Tòng Vượng / Nhuận Hạ), sách đọc thân vượng thường dùng Thực Thương |

Bảng ví dụ điều hậu (tr.387–388):

| Ví dụ | Lá số | Sách lấy | Engine (can chủ trước) | Kết quả |
|---|---|---|---|---|
| p387_intro | Bính Thân / Canh Tý / Quý Sửu / Ất Mão | Bính (Tai) | Bính=Tai Tân=An | khớp hoàn toàn |
| p387_vd1 | Đinh Mão / Canh Tuất / Kỷ Tỵ / Canh Ngọ | Đinh (An) | Giáp=QuanSat Bính=An Quý=Tai | khớp một phần (nhóm của sách có trong ô nhưng không đứng đầu) |
| p388_vd2 | Mậu Thìn / Giáp Dần / Đinh Mão / Kỷ Dậu | Tân (Tai) | Giáp=An Canh=Tai | khớp một phần (nhóm của sách có trong ô nhưng không đứng đầu) |
| p388_vd3 | Đinh Mão / Quý Sửu / Bính Thân / Mậu Tý | Ất (An) | Nhâm=QuanSat Giáp=An | khớp một phần (nhóm của sách có trong ô nhưng không đứng đầu) |
| p388_vd4 | Canh Dần / Mậu Dần / Giáp Tý / Bính Dần | Bính (ThucThuong) | Bính=ThucThuong Quý=An | khớp hoàn toàn |

Tổng hợp: trong 9 ví dụ, khớp hoàn toàn 3 (vd1 tr.397, intro và vd4 tr.387–388), khớp một phần 5, không khớp 1 (vd4 tr.400). Con số này mô tả độ trung thực với *lời của sách*, không phải độ chính xác dự báo.

## 4. Phạm vi xác minh của từng phương pháp

| Phương pháp | Đã xác minh | Chưa xác minh |
|---|---|---|
| `dieu_hau` | tập can 120 ô và thứ tự can chủ (hai lượt chép, 9 ô sách tự mâu thuẫn được gắn cờ) | vai trò Dụng/Hỷ; ngưỡng hàn/nhiệt; học thuyết (tác giả không rõ nguồn bảng); phiếu kiểm của người |
| `cach_cuc_tvh` | bảng cách × vượng/nhược × nhóm nhiều (tr.378–386) đã chép; ngưỡng 40% (tr.355) | đúng 40% và biên ±0,03; 'nhóm nhiều nhất' khi đồng hạng; các ví dụ chỉ khớp một phần |
| `thuan_the_tvh` | bảng dụng thần/vận của tòng tài/sát/nhi và cách đặc biệt (tr.381–386) | ngưỡng nhận diện (`tvh_no_help`, `tvh_tong_main`, `chuyen_vuong_*`); ví dụ 4 tr.400 không khớp |
| `thuan_the` | bảng vai trò tòng (Trích Thiên Tủy tr.171–179) | ngưỡng nhận diện tòng/hóa và hóa thần dư/thiếu |
| `phu_uc`, `cach_cuc`, `thong_quan` | — | toàn bộ (draft); `cach_cuc` chỉ có phần Thương Quan (TTT tr.93–94) được chép đúng |
| `khuyet_hanh` | — | chỉ một ví dụ (tr.399), sách không nêu thành quy tắc; ví dụ 4 tr.400 không khớp |

## 5. Điều kiện còn thiếu trước khi tích hợp production

- Người đọc kiểm độc lập 120 ô trên ảnh trang (phiếu `docs/BAZI_DEEP_TVH_CELLS_CHECK.md`, cột *Người kiểm* còn trống). Hiện chỉ có hai lượt chép của mô hình.
- Quyết định của chủ sản phẩm về 9 ô sách tự mâu thuẫn (hiện: giữ tập can của bảng, gắn cờ, không thăng cấp can chỉ có ở chú thích).
- Quyết định về hiển thị phù ức theo quyết định 40%: nay `phu_uc` luôn theo khí thế của hệ thống (độ trung thực với nhãn Trích Thiên Tủy 36/48 so với 45/48 của quy tắc 40%). Muốn có phù ức theo 40% phải là một phương pháp riêng, nằm ngoài phạm vi Phase 5.
- Bằng chứng thực nghiệm về giá trị dự báo của bất kỳ phương pháp nào (hiện 0): cần bộ lá số có kết quả đời thực được ghi trước, người chấm độc lập.
- Ví dụ 4 tr.399–400 dựng lại từ lời văn vì bảng in vỡ; cần người đối chiếu trang. Ví dụ 5 (tr.400–401) chưa đọc.
- Ngưỡng của hệ thống (mục 7 của `BAZI_DEEP_TVH_AUDIT.md`) chưa có căn cứ nguồn; không nên trình bày như điều sách nói.
- UI và `api.py` chưa được chạm: cần phiên phụ trách web hiển thị `meta.levels`, `trace` và cờ `book_internal_conflict` trước khi người dùng cuối thấy kết quả.

## 6. Phát hiện và sửa trong Phase 5

1. `geju.analyse` dưới `tvh_40` trước đây đánh giá trạng thái nội cách và ngoại cách của hệ thống bằng khí thế TVH → nay chỉ *thêm* cách đặc biệt TVH (headline `geju` = geju hệ thống + cách TVH).
2. `cach_cuc_tvh` / `thuan_the_tvh` trước đây đọc danh sách ngoại cách gộp, nên ngoại cách của hệ thống thay nội cách của TVH → nay có `G_tvh` chỉ chứa cách TVH.
3. `phu_uc` trước đây đọc quyết định TVH và ngoại cách của TVH → nay dùng khí thế và ngoại cách của hệ thống.
4. Siêu dữ liệu `levels` (ba mức xác minh) thêm vào `meta` của từng phương pháp; locator của `SRC_TVH_DIEUHAU` và `SRC_TVH_DUNGTHAN` mở rộng theo các trang thực sự đã đọc.

## 7. Oracle độc lập đã dùng

- `tests/golden/tvh_dieuhau_blind.json`: bảng 120 ô và chú thích, chép mù (Phase 4).
- `tests/golden/tvh_examples_blind.json`: bốn trụ và kết luận của 9 ví dụ tr.387–400, chép mù; so với `tvh_dungthan_examples.json` (oracle viết tay).
- Lịch: ngày Quý Mão của 2/1/1974 cho ví dụ 4, độc lập với cả hai lượt chép.
- Giới hạn: tất cả do mô hình thực hiện; chưa có người kiểm.

## 8. Quy trình kiểm tra trên HEAD sạch

Mọi lần chạy dùng `git worktree` tách riêng (không có file của phiên khác), cùng một venv. Ghi lại bằng tay lúc chạy:

| Cây mã | Kết quả |
|---|---|
| `d0c3ab8` (commit audit Phase 4), sạch | 879 passed, 1 skipped, 2 xfailed, 0 failed |
| `3d4aabf` (HEAD hiện tại, có thêm commit giao diện so sánh của phiên khác), sạch | 892 passed, 1 skipped, 2 xfailed, 0 failed |
| `3d4aabf` + các file Phase 5 (15 file, không `api.py`, không `web/`, không `compare_deep`) | **949 passed, 1 skipped, 2 xfailed, 0 failed** |

## 9. Phân loại lỗi

- **Lỗi mới do Phase 5:** khi phát triển có 4 nhóm test cũ phải sửa vì giả định cũ (số phương pháp, `readings` của TVH, mức khí thế của `phu_uc`, snapshot TVH của EX5/EX12); tất cả được xem xét từng cái và ghi trong commit; còn lại 0.
- **Lỗi baseline:** 0 test fail ở `d0c3ab8` và `3d4aabf` sạch. 2 xfailed và 1 skipped có sẵn ở cả hai, không do Phase 5.
- **Lỗi do phiên khác đang sửa dở:** trên cây làm việc chung, `tests/test_compare_deep.py` fail 6 ca khi phiên so sánh chưa commit (đã biến mất ở HEAD sạch `3d4aabf` sau khi phiên đó commit). Không liên quan Phase 5.

