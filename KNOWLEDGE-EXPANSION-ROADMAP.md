# KNOWLEDGE-EXPANSION-ROADMAP — Lộ trình mở rộng chiều sâu, nguồn và giá trị học tập

Ngày: 2026-10-17. Đi kèm `CLASSICAL-SOURCE-AUDIT.md` (số liệu và phát hiện). Tài liệu này nói **việc tiếp theo, theo thứ tự nên làm, kèm tiêu chí xong việc**.

Nguyên tắc xuyên suốt (giữ nguyên từ các giai đoạn trước):
1. Không gộp trường phái mâu thuẫn thành một chân lý; luôn nêu sách và trang.
2. Phân biệt bốn loại khẳng định: tính toán · quy tắc có nguồn · vận hành hóa của hệ thống · giả thuyết.
3. Không bao giờ nâng nhãn nếu chưa đọc trang; trích dẫn phải máy-kiểm được.
4. Không đổi engine chỉ để khớp nội dung giải thích: nếu nội dung và engine lệch, **ghi lệch và để chủ dữ liệu quyết**.
5. Không trình bày vận mệnh, sức khỏe, tài chính, quan hệ như sự thật khoa học.

---

## Trạng thái hiện tại (sau đợt này)

| Hạng mục | Có | Còn thiếu |
|---|---|---|
| Quy tắc có bằng chứng nguyên văn | 204 / 1.622 (+24 định nghĩa TBCT bản web) | 1.030 quy tắc "Có nguồn" chưa đọc riêng từng câu |
| Chỗ lệch điều kiện đã biết | 45 "một phần", 4 "sai/đọc sai" (3 đã hạ nhãn, 2 đã sửa trang) | 42 chưa sửa (R1) |
| Trang tra cứu | `/reference` theo sao, cung, Bát Tự; 5 mức tin cậy | chưa gắn vào thẻ kết quả của từng lá số (R6) |
| Bài học | 24 bài, 5 cấp | không có bài theo từng sao/từng cung (R5) |
| Người kiểm | 1 người đọc là AI | người thứ hai (R2) |

---

## R1 — Đóng vòng 49 phát hiện (ưu tiên cao nhất, 1–2 ngày của chủ dữ liệu)

Nguồn: `docs/source_audit_findings.csv`. Mỗi dòng có "sửa tối thiểu". Chủ dữ liệu cần quyết từng nhóm, vì **mỗi sửa đổi đầu ra của engine** và có test vàng/độ phủ liên quan.

| Nhóm | Ví dụ (mã quy tắc) | Cách sửa đề xuất | Rủi ro |
|---|---|---|---|
| Cặp sao bị đọc thành "một trong hai" | `TV_TH_VERSE_TU_QUYEN_LOC`, `TV_TH_P2_PHU_MAU_VIET_KHOA`, `TV_KL_STAR_TAI_BACH_KHONG_KIEP`, `TV_KL_CUNG_PHU_THE_KINH_DA_KHONG_KIEP` | đổi điều kiện thành *cả hai*, hoặc ghi "một trong hai" là quy ước và hạ `draft` | giảm số nhận định hiển thị |
| Bắt miếu/vượng/đắc khi sách chỉ nói "miếu" | `TV_TT_PAL_QUAN_LOC_THAI_AM_MIEU_P`, `TV_TH_AUX_MENH_HL_LUONG`, `TV_TH_AM_TOT_HIEN_HOA_VAN_CHUONG` | chặt về `miếu`, hoặc hạ `draft` | |
| Thiếu rào đón: "nhiều sát tinh", "không bị Tứ Sát", nam/nữ, ngoại lệ Tham/Vũ | `TV_TH_AUX_MENH_HK_SAT`, `TV_TT_PAL_PHU_MAU_THAI_DUONG_WITH_THAI_AM_P`, `TV_TH_DUONG_TOT_THONG_MINH_NHAN_HAU`, `TV_TH_AUX_MENH_HL_TU_MO` | thêm điều kiện loại trừ, hoặc nâng mô tả | cần cờ giới tính cho mục phú nằm dưới "A. Nam mệnh" |
| Từ ca thành luật | `TV_KL_CASE_TAI_BACH_THAI_TUE` | chuyển thành `category: case_note`, `draft` | |
| Mạnh/yếu hơn trang | `TV_TT_MENH_TA_HUU_DONG_CUNG` ("sung túc" vs "cao sang"), `TV_TH_P2_TAI_BACH_TT` | sửa câu claim cho sát trang | đổi chữ hiển thị |
| Quy tắc Bát Tự TTT/ZZ thiếu điều kiện | `BT_TTT_HONTAP_KHONG_NGAI` (Quan Sát đương lệnh), `BT_ZZ_DIRECT_E_AN_ROOT` (Ấn lưu nhập Nhật Chủ), `BT_TTT_TONG_THE` (ba thần ngang nhau) | thêm điều kiện hoặc ghi "chưa kiểm" | cần thêm sự kiện `流入日主`, `截脚` |
| `TV_TH_AUX2_TAI_BACH_MO`, `TV_TH_AUX2_DIEN_TRACH_MO` gán nhầm sao Mộ/Tử | (đã hạ nhãn) | **chuyển điều kiện từ sao Mộ sang sao Tử**, kèm cung Điền Trạch/Tài Bạch; hoặc bỏ | thay đổi đầu ra |
| `TV_TH_MV_MENH_TU_SAT_VUONG` đọc "Tứ Sát" thành "Tử, Sát" | (đã hạ nhãn) | viết lại thành bốn sát tinh ở vượng địa, hoặc bỏ | |
| TBCT: Thiên Ấn · Kiêu đoạt Thực; Âm Nhận; Tài cứu Quan; "Tài Quan song mỹ" | `geju:Thiên Ấn`, ánh xạ Âm Nhận (ghi ở qualifier của `geju:Dương Nhận`), `geju:Chính Quan`, `pattern:tai_quan_song_my` | sửa theo văn bản hoặc đổi tên thành "quy ước" | các định nghĩa đã `draft` nên rủi ro thấp |

(Danh sách đầy đủ và "sửa tối thiểu" của từng dòng nằm trong CSV; bảng trên chỉ phân nhóm.)

**Xong khi:** mỗi dòng CSV có quyết định (`sửa` / `giữ + ghi chú` / `bỏ`) và ngày; sau mỗi sửa chạy `tools/apply_evidence_corrections.py`, đọc lại trang một lần nữa, đổi verdict trong `evidence_overrides.json`; cập nhật test vàng có liên quan; chạy lại `tools/build_reference.py` (test độ tươi sẽ nhắc).

---

## R2 — Người kiểm thứ hai (con người)

* **Việc:** một người đọc được Hán–Việt và biết Tử Vi mở lại mẫu mới, **không xem verdict cũ** (thiết kế mù), trả lời cùng biểu mẫu.
* **Cỡ mẫu:** để ước lượng tỉ lệ khớp trong khoảng ±4% (95%), với p≈0,8 cần khoảng **380 quy tắc** ngẫu nhiên từ nhóm "Có nguồn". Có sẵn `tools/build_source_evidence.py batches` (đổi hạt giống, loại quy tắc đã có bằng chứng).
* **Đo đồng thuận:** tính hệ số kappa giữa người và mô hình; nơi lệch được ưu tiên đọc lại.
* **Xong khi:** mỗi mục có hai lượt đọc; các mục hai lượt trùng khớp mới được gắn nhãn "Đã đối chiếu (2 người đọc)", mức cao nhất của thang.
* Mẫu quy trình đã có ở `docs/BAZI_DEEP_TVH_REVIEW_PROTOCOL.md` (120 ô điều hậu); dùng lại cấu trúc.

## R3 — Mở rộng bằng chứng ra toàn bộ thư viện

* Chi phí đo được: ≈ **5.500 token mỗi quy tắc** (7 tác tử, 204 quy tắc + 24 định nghĩa ≈ 1,26 triệu token). Toàn bộ 1.030 + 179 quy tắc còn lại ≈ **6–7 triệu token** nếu làm bằng mô hình; làm theo gói để dừng lại được.
* Thứ tự gói (theo mức rủi ro đo được): `pack_thuc_hanh_palaces2` (86 v/48 d, nhiều verse cặp sao) → `pack_thuc_hanh_menh_verse` → `pack_toan_thu_palaces` (382, đồng nhất, rủi ro thấp: ưu tiên lấy mẫu, không đọc hết) → `pack_khao_luan_cung` (29 v/19 d) → các gói còn lại.
* Với TH: **luôn xem ảnh** các trang 50-117 (lớp chữ xáo dòng; lỗi Tử/Mộ phát hiện qua đây).
* **Xong khi:** mọi quy tắc `verified` có một dòng bằng chứng; nhãn "Có nguồn" chỉ còn dành cho quy tắc chưa đọc.

## R4 — Đọc phần sách chưa khai thác (mở rộng nội dung)

Số trang đã có quy tắc: KL 56/290, TH 66/163, TT 54/170, ZZ 14/96. Các phần được ghi nhận "chưa mã hóa/chưa đọc" và việc nên làm:

| Nguồn | Phần | Giá trị | Ghi chú |
|---|---|---|---|
| Trích Thiên Tủy | Chương Thiên Can, Địa Chi, Hình Tượng, Bát Cách, Thể Dụng; Phần II Lục thân | **cao**: nguồn có trang cho hình ảnh từng Can/Chi và Thập Thần (hiện từ điển viết tay, không nguồn) | cần phân biệt nguyên chú Lưu Bá Ôn và bình chú Nhậm |
| Thiệu Vĩ Hoa | Lục thân; hóa giải; ví dụ thực tế (sau tr.400) | cao cho Bát Tự | bản scan: đọc ảnh, thiết kế mù |
| 八字真宗 | tr.43-49, 60-96 (một phần đã làm) | trung bình | giữ chính sách bỏ câu tai họa/bệnh/tuổi thọ |
| Khảo Luận | tr.249-290 (hợp tuổi theo nạp âm, chọn ngày, bát hạn…) | thấp; tác giả tự dặn dè dặt | chỉ đưa vào dưới dạng bài "đọc phê phán" |
| Toàn Thư | tr.53-62 (phụ tinh cách an chưa kiểm), 121-146 | trung bình | cần kiểm cách an trước |
| Tử Bình Chân Thuyên | bản in, cùng chương 論正官…論建祿月劫 | **cao**: nâng 24 định nghĩa từ `draft` | hiện chỉ có bản web |
| Uyên Hải Tử Bình, Tam Mệnh Thông Hội, Cùng Thông Bảo Giám | chưa có sách | trung bình | bảng tư lệnh và bảng điều hậu hiện viết theo trí nhớ (`draft`) cần nguồn |
| Phương thuật kỷ dị | chưa đọc | thấp | |

Mỗi phần được đọc theo quy trình: chép nguyên văn máy-kiểm → viết quy tắc `draft` có trang → đối chiếu → chỉ nâng khi đã đọc lại.

## R5 — Chiều sâu giải thích theo từng sao, cung, tổ hợp, cách cục, quan hệ Can Chi

Nền đã có: trang `/reference` sinh tự động theo sao × cung, kèm độ sáng hai trường phái, nhãn tin cậy và nguyên văn của các quy tắc đã đối chiếu. Việc tiếp theo là **thẻ học sâu** cho từng đơn vị, viết tay có căn cứ, dùng khung cố định để người mới và người nghiên cứu cùng đọc được:

| Khung thẻ | Nội dung | Nguồn |
|---|---|---|
| Là gì | định nghĩa tính toán (cách an, vị trí) | bảng đã kiểm |
| Sách nói gì | ≤3 trích dẫn nguyên văn + bản dịch + giọng (phú / lời giải / bình) | `source_evidence.json` |
| Điều kiện áp dụng | sao đi cùng, chi, giới, độ sáng | điều kiện quy tắc, đối chiếu trang |
| Ngoại lệ và lời cảnh báo | Tuần/Triệt, sát tinh, lời dặn của tác giả | qualifier trong bằng chứng |
| Bất đồng giữa sách | hai bên, hai trang | ghi chú trường phái |
| Ví dụ | một lá số minh họa từ sách | `tests/test_book_examples.py` (5 lá số in trong Khảo Luận) |
| Phản ví dụ / vì sao không kết luận được | cùng dấu hiệu ở lá số khác; tỉ lệ nền | `reading_base_rate.json` |
| Mức tin cậy | nhãn 5 bậc, không phải xác suất | `reference.json` |

Thứ tự đề xuất: **(1)** 14 chính tinh (mỗi sao một thẻ; dữ liệu đã đủ); **(2)** 12 cung (cần bù Tử Tức, Huynh Đệ: R4); **(3)** Tứ Hóa; **(4)** Tuần/Triệt và vòng Trường Sinh; **(5)** 10 Thiên Can và 12 Địa Chi từ Trích Thiên Tủy; **(6)** Thập Thần; **(7)** quan hệ Can Chi (hợp, xung, hình, hại).

Tiêu chí xong việc cho **mỗi thẻ**: ≥2 trích dẫn sách in được máy kiểm; ≥1 điều kiện hoặc ngoại lệ có trang; ≥1 phản ví dụ hoặc câu "vì sao không kết luận được"; không câu nào mang giọng tiên đoán; có test trong `test_lessons_deep.py` (hoặc test thẻ tương đương).

## R6 — Đưa bằng chứng vào thẻ kết quả của từng lá số

**Trạng thái:** đã làm ở nhánh này (`engine/web/js/tier.js`, `ui.js`, `beginner.js`; test `test_evidence_tier.py`). Nhãn 5 bậc tính ở trình duyệt từ `/api/evidence` (không đổi trường API nào); chế độ Chuyên sâu có nhãn, cảnh báo "Khớp một phần" và nút "Xem nguyên văn"; chế độ Dễ hiểu chỉ hiện nhãn khi "Khớp một phần".

Hiện thẻ kết quả (`ui.js`) có nhãn "Đã đối chiếu với sách / Nháp". Việc tiếp theo:
* Dùng `GET /api/evidence` để hiện nhãn 5 bậc và nút "Xem nguyên văn" ngay trong thẻ (chế độ *Chuyên sâu*; chế độ *Dễ hiểu* chỉ hiện nhãn khi "Khớp một phần").
* Cảnh báo "Khớp một phần: sách nói thêm …" trực tiếp cạnh nhận định bị lệch điều kiện.
* **Tương thích:** chỉ thêm trường mới vào đáp án hiện có (ví dụ `evidence_tier`), không đổi trường cũ; test hợp đồng `docs/BAZI_DEEP_API_CONTRACT.md` giữ nguyên.

## R7 — Lộ trình học (learning paths)

Đã có 24 bài (5 cấp). Cần thêm để hoàn chỉnh từ cơ bản tới nghiên cứu:

| Lộ trình | Cấp | Bài đã có | Bài kế tiếp |
|---|---|---|---|
| Tử Vi | 1–3 | tv-1…tv-7 | — |
| Tử Vi | 4 · Đọc có nguồn | tv-8 chuỗi trang→dòng; tv-9 độ sáng; tv-10 điều kiện/ngoại lệ; tv-11 ví dụ và tỉ lệ nền | tv-12 Tuần/Triệt (hai vai trò trái nhau); tv-13 Tứ Hóa và tranh chấp Nhâm-Khoa; tv-14 cách cục: tên, điều kiện, vì sao còn nháp |
| Bát Tự | 1–3 | bt-1…bt-4 | — |
| Bát Tự | 4 · Đọc có nguồn | bt-5 vượng suy; bt-6 dụng thần/điều hậu; bt-7 cách cục | bt-8 hàn–noãn và tư lệnh; bt-9 đại vận/tuế vận (thiên khắc địa xung, tiệt cước) |
| Nghiên cứu | 5 | rs-1…rs-5 | rs-6 đọc một bản dịch phê phán (so Hán văn và bản Việt); rs-7 thiết kế phép thử cho một nhận định (dự đoán ghi trước, đối chứng) |

Mỗi bài mới phải qua `test_lessons_deep.py`: trích dẫn thật, số liệu có nguồn đo, không tiên đoán.

## R8 — Chuẩn hóa nhãn và hợp đồng dữ liệu

* Đổi ý nghĩa nhãn `reviewStatus` thành thang 5 bậc *trong dữ liệu* (hiện chỉ `verified`/`draft`), bằng trường mới `evidenceTier` sinh từ `source_evidence.json` (không bỏ trường cũ).
* Sinh `sources.json` locator từ các trang được cite (đã sửa tay đợt này; nên tự động hóa để không lỗi thời lại).
* Gắn `sourceIds` cho 28 quy tắc `van_han_rules.json` (hiện `src: "SRC"`), kèm trang KL 233-236, TH 115-117.
* Tách `SRC_TTT_*` thành hai nguồn: *nguyên chú Lưu Bá Ôn* và *bình chú Nhậm Thiết Tiều*.

## R9 — CI

* Thêm bước `pytest` hiện có (đã gồm test mới); test cần sách tự `skip` nếu thiếu sách (đã làm).
* Một lệnh kiểm "dữ liệu sinh còn tươi": `build_reference.py`, `build_glossary.py` (đã có test).
* Cảnh báo khi một gói quy tắc được sinh lại mà không chạy `apply_evidence_corrections.py` (test `test_corrections_are_applied` đã bắt).

---

## Thứ tự và công sức (ước lượng thô)

| # | Việc | Ai | Công sức |
|---|---|---|---|
| R1 | Quyết định 49 phát hiện | chủ dữ liệu | 1–2 ngày |
| R2 | Người kiểm thứ hai, 380 quy tắc | chuyên gia | 3–5 ngày |
| R5(1) | 14 thẻ chính tinh | biên tập + máy kiểm | 3–4 ngày |
| R6 | Bằng chứng trong thẻ kết quả | dev | 2 ngày |
| R3 | Bằng chứng toàn thư viện | mô hình + người xem mẫu | 6–7 triệu token |
| R4 | Đọc TTT Thiên Can/Địa Chi trước (giá trị cao nhất) | mô hình + người | 2–3 ngày |
| R7–R9 | Bài học bổ sung, nhãn, CI | dev + biên tập | rải theo |

## Điều **không** nằm trong lộ trình

* Mọi câu về chết chóc, tai nạn, tù tội, bệnh cụ thể, số con sống chết, danh tiếng tình dục.
* Khuyến nghị đời sống (màu, hướng, mua vàng) từ sách phổ thông "mệnh khuyết".
* Bất kỳ chỉ số "độ chính xác dự báo" nào nếu chưa có phép thử đối chứng thật.
