# Thêm Bát Tự Hà Lạc (quẻ Dịch theo giờ sinh) — kế hoạch (2026-10-21)

Nguồn người dùng cung cấp: `~/Downloads/Bát-tự-Hà-Lạc-dantocking.com.pdf` (129 trang, có lớp chữ đọc được).

## Tệp này có gì / thiếu gì

| Có (Phần II) | Trang |
|---|---|
| Lời giải 41 quẻ, số 24 Địa Lôi Phục → 64 Hỏa Thủy Vị Tế. Mỗi quẻ: tên, tháng, Lời tượng, Lược nghĩa, "Những tuổi Nạp Giáp" hợp quẻ; mỗi hào: lời hào, Lược nghĩa, Ý hào, Mệnh hợp cách / không hợp cách, Xem tuế vận (quan chức / giới sĩ / người thường), thơ | 1–121 |
| "Cách dùng Phần II để giải đoán" + "Tóm lược cách giải đoán số Hà Lạc" (thể cách, đại vận, tuế vận theo hào) | 122–123 |
| "Luận mấy cách quý hiển" (quẻ × tuổi → cách) và "Mấy cách xét mệnh giờ" | 124 |
| 4 lá số mẫu giải đầy đủ: số của can chi, tổng âm/dương → quẻ, Hóa công, Thiên/Địa nguyên khí, Nguyên đường, đại vận theo hào | 125–128 |
| So sánh Tử Vi / Hà Lạc / Mệnh lý | 128–129 |

| Thiếu | Hệ quả |
|---|---|
| **Phần I — cách lập quẻ**: số Hà Đồ của 10 can, 12 chi; cộng số âm/dương, trừ bội số, ra quái thượng/hạ; quẻ Tiên Thiên; định **Nguyên đường** theo giờ sinh và âm/dương nam nữ; quẻ **Hậu Thiên**; số năm mỗi hào (đại vận), tuế vận; **Hóa công**, **Thiên/Địa nguyên khí**; "Thể cách" (mục 9) | không thể lập quẻ cho người dùng mà không tự đặt quy tắc — không làm |
| Quẻ 1–23 | 23/64 quẻ chưa có lời giải |

## Kế hoạch

| Bước | Việc | Điều kiện |
|---|---|---|
| H0 | **Bạn gửi Phần I** (cách lập quẻ) và phần quẻ 1–23 của cùng sách | chặn H2–H4 |
| H1 | Trích Phần II thành dữ liệu có cấu trúc `engine/data/ha_lac/hexagrams.json`: mỗi quẻ/hào → trường (tượng, ý hào, mệnh hợp/không hợp, tuế vận theo nhóm người, tuổi nạp giáp, tháng), kèm số trang. Lưu bản **tóm ý ngắn** + trích dẫn ngắn, không chép lại toàn văn (bản quyền); công cụ `tools/build_ha_lac.py`, kiểm tra trang như quy trình sách hiện có | làm được ngay |
| H2 | Bộ lập quẻ (Python `engine/tvbt/ha_lac.py`): số can chi, tổng âm/dương, quẻ Tiên/Hậu Thiên, Nguyên đường, hỗ quái, Hóa công, nguyên khí, đại vận & tuế vận theo hào | cần H0 |
| H3 | **Kiểm định bằng 4 lá mẫu tr.126–128 + ví dụ tr.122** (Bính Tý / Quý Tỵ / Bính Ngọ / Tân Mão → Sơn Thủy Mông, biến Thiên Thủy Địa Tỷ): bộ lập quẻ phải ra đúng từng con số sách in | cần H2 |
| H4 | Giao diện tab "Hà Lạc" cạnh Tử Vi / Bát Tự: vẽ quẻ Tiên Thiên và Hậu Thiên (6 hào), đánh dấu Nguyên đường, Hóa công/nguyên khí; dòng thời gian đại vận theo hào; tuế vận năm xem | cần H2 |
| H5 | Luận giải Hà Lạc: thể cách (nạp giáp, tên quẻ, số âm/dương hợp mùa, vị Nguyên đường, hóa công, nạp âm hợp quẻ — theo tr.122), quý cách tr.124, lời hào của Nguyên đường và của hào đại vận/tuế vận; theo đúng lời sách "hào từ chưa thể căn cứ… phải suy lý" (tr.123): trình bày như gợi ý, không khẳng định | cần H1–H3 |
| H6 | Kết nối với báo cáo: chương "Quẻ mệnh Hà Lạc", và một dòng đối chiếu trong tổng quan (sách tr.128–129: Tử Vi "Hẳn", Hà Lạc "Nếu", Mệnh lý "Nên") | |

Làm ngay: H1 (dữ liệu 41 quẻ có trang). H2–H6 chờ Phần I.

## Kinh Dịch trọn bộ (người dùng gửi 2026-10-21)

Tệp nhận được là trang Google Drive đã lưu (`KINH DỊCH TRỌN BỘ.PDF - Google Drive.html`), **không chứa chữ của sách**: Drive vẽ từng trang (666 trang) thành ảnh khi xem. Cần tải đúng tệp PDF (nút Tải xuống trong Drive) vào `~/Downloads`.

Vai trò khi có PDF:

| Bước | Việc |
|---|---|
| K1 | Kiểm tra lớp chữ (hay phải OCR) và bố cục: 64 quẻ, Thoán từ, Đại tượng, Hào từ, Tiểu tượng, Hệ từ, Thuyết quái |
| K2 | Bổ sung lời quẻ / lời hào cho **quẻ 1–23** mà tệp Hà Lạc thiếu (phần "Lược nghĩa"); phần giải đoán riêng của Hà Lạc (Ý hào, Mệnh hợp cách, Tuế vận) vẫn phải từ sách Hà Lạc |
| K3 | Dữ liệu quẻ dùng chung `engine/data/ha_lac/hexagrams.json`: số thứ tự, tên Hán–Việt, quái thượng/hạ, 6 hào, Đại tượng, lời hào — mỗi trường ghi sách và trang; chỉ tóm ý + trích ngắn (bản quyền) |
| K4 | Thuyết quái (tượng của 8 quái, ngũ hành, phương vị) — cần cho Hóa công / nguyên khí trong Hà Lạc khi có Phần I |
| K5 | Trang "Kinh Dịch" trong mục Bài viết: 64 trang quẻ, mỗi trang có nguồn |

Kinh Dịch **không** chứa cách lập quẻ Hà Lạc theo giờ sinh: vẫn cần Phần I của sách Hà Lạc (bước H0).

## Tình trạng (2026-10-21, nhánh `claude/ha-lac-data-4734d6`)

Đã nhận thêm hai tệp: sách gốc đầy đủ **Học-Năng, *Bát-Tự Hà-Lạc Lược-Khảo* (Sài Gòn 1974)** — `(kinhdich)-Sách bat-tu-ha-lac-dantocking.com.pdf`, 633 trang **ảnh quét, không có lớp chữ** (Phần I tr.15–135, Phần II tr.136–528; ở Phần I trang PDF = trang in − 2) — và **Kinh Dịch, Ngô Tất Tố dịch và chú giải (NXB Văn Học)** — `KINH DỊCH TRỌN BỘ.PDF`, 666 trang ảnh quét (lớp chữ chỉ là dấu tải về; trang in = trang PDF + 4).

| Bước | Trạng thái |
|---|---|
| H0 | **Xong**: Phần I đọc từ ảnh quét. Cách lập quẻ tr.35–90 (trị số can chi, Lạc Thư, thứ tự trên/dưới, rút gọn tổng, số 5 theo Tam Nguyên, Hóa công, nguyên khí, Nguyên đường gồm quẻ thuần Kiền/Khôn, Hậu Thiên, hỗ, đại vận, lưu niên) |
| H1 | **Xong**: `engine/data/ha_lac/hexagrams.json` (quẻ 24–64, tóm ý có trang), `tools/build_ha_lac.py`, `worked_examples.json` |
| H2 | **Xong**: `engine/tvbt/ha_lac.py` — `cast()` (từ bốn trụ), `cast_birth()` (từ ngày giờ sinh, trụ lấy từ `tvbt.bazi`), `luu_nien_at()`, `summary()` (JSON gọn cho văn luận giải) |
| H3 | **Xong**: `engine/data/ha_lac/golden_part1.json` chép mọi ví dụ Phần I (tr.43–96) + 5 lá mẫu Phần II; `tests/test_ha_lac_cast.py` khớp từng con số sách in (chỗ in sai được ghi lại) |
| H4–H6 | Chưa làm (giao diện, luận thể cách, nối vào báo cáo) |
| K1 | **Xong**: bản Ngô Tất Tố, mỗi quẻ: lời kinh (chữ Hán), dịch âm, dịch nghĩa, Truyện của Trình Di, Bản nghĩa của Chu Hy, lời bàn của tiên nho; ảnh rõ, đọc được |
| K2–K3 | Chưa làm. Lời giải đoán Hà Lạc cho **quẻ 1–23** có sẵn ở Phần II của sách gốc (ảnh quét, tr.139–307 theo bảng "Đồ biểu 64 quẻ") — nguồn đúng hơn Kinh Dịch cho phần Ý hào / Mệnh hợp cách / Tuế vận; cần chép (tóm ý) từ ảnh |
| K4 | Không cần cho lập quẻ nữa: Phần I đã cho số Lạc Thư của 8 quái và bảng nguyên khí |

Còn mở: sách ghi Tam Nguyên 1864–2043 (tr.48) và chú thích rằng sách Dương Trạch tính khác (1984 là Thượng nguyên mới) — bộ lập quẻ theo sách này. Giờ Tý và ngày: theo quy ước Tý của engine (sách tr.31 chỉ cho bảng giờ và các lần đổi giờ ở Việt Nam 1943–1960).
