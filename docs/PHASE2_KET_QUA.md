# Phase 2 — vận hạn đa tầng (kết quả)

Tiếp theo [PHASE1_KET_QUA.md](PHASE1_KET_QUA.md). Không dùng LLM; không đổi UI hay Cloudflare.

## Đã làm

| Hạng mục | Ở đâu |
|---|---|
| **`van_han.read` thành luật dữ liệu**: 28 luật (20 của Khảo Luận pp.233–236 + 8 của Thực Hành pp.115–117) trong [van_han_rules.json](../engine/data/van_han_rules.json); điều kiện bằng DSL, câu có khuôn `{...}` và phần đuôi điều kiện. Câu chữ và điều kiện chép nguyên văn từ code cũ, **không thêm quy tắc mới** | [van_han.py](../engine/tvbt/van_han.py), sinh bởi [build_van_han_rules.py](../tools/build_van_han_rules.py) |
| Thêm `read_traced` (mỗi câu kèm `rule_id`); `read` giữ nguyên hình dạng đầu ra | cùng file |
| **Fact thời gian đa tầng** theo từng cung: cung đại hạn / tiểu hạn / lưu Thái Tuế trùng nhau, Tứ Hóa của ba tầng (bản mệnh, can cung đại hạn, can năm xem) rơi vào cung nào, tầng Kỵ / tầng Lộc chồng nhau, cung có nằm trong tam phương của Mệnh | [temporal_facts.py](../engine/tvbt/reasoning/temporal_facts.py) |
| **Tứ Hóa theo can cung đại hạn** (mới; trước đây `dai_han[].stem` có sẵn nhưng chưa dùng) và lưu Tứ Hóa như fact | cùng file |
| 8 luật tương tác đa tầng **thử nghiệm** (chồng Kỵ, chồng Lộc, đại hạn trùng tiểu hạn, lưu Kỵ xung/nhập Mệnh, đại hạn Kỵ xung Mệnh, đại hạn trong tam phương Mệnh có cách thành, và một luật nhiều bước nối kết quả cách cục) | [pack_van_han_layers.json](../engine/data/experimental/pack_van_han_layers.json), sinh bởi [build_experimental_layers.py](../tools/build_experimental_layers.py) |
| Chạy luật đa tầng cùng engine Phase 1 (cách cục → fact suy ra → luật tầng thời gian) | [layers.py](../engine/tvbt/reasoning/layers.py) |
| API: `/api/year` với `experimental: true` thêm khối `experimental` (mặc định tắt) | [api.py](../engine/tvbt/api.py) |

## Ranh giới độ tin cậy

- **Luật Khảo Luận/Thực Hành đã có trong production**: chỉ đổi cách lưu (code → dữ liệu). Không đổi đầu ra, kể cả từng chữ (xem kiểm chứng).
- **8 luật đa tầng là giả thuyết thiết kế của tôi, chưa đối chiếu trang sách nào** (`draft`, ngoài `PACKS`, nguồn `SRC_EXPERIMENTAL` chưa xác minh). Chúng chỉ mô tả cấu trúc ("hai tầng Kỵ cùng rơi một cung"), không nói sự kiện. Ngoại lệ "Khoa của đại hạn/lưu giải chồng Kỵ" cũng là giả thuyết.
- Fact thời gian chỉ là hình học + bảng Tứ Hóa theo can mà engine đã dùng. Quy ước "hóa rơi vào cung đang giữ sao đó" là quy ước tam hợp; trường phái Phi Hóa tính khác và **chưa** có ở đây.
- Năm xem dùng nhãn năm âm lịch theo can chi của số năm (như `tuvi_year` hiện có); chưa xử lý riêng người sinh sát Tết.

## Kiểm chứng

- `pytest`: **gần 420 test xanh; 2–3 test `test_bazi_deep_*` đang đỏ và không thuộc phần này** (Bát Tự sâu của phiên khác đang sửa dở các file `bazi_deep`; engine/DSL dùng chung không đổi so với HEAD ở Phase 2, chỉ `loader.py` thêm một hàm). Phase 2 thêm 29 test: [test_van_han_rules.py](../engine/tests/test_van_han_rules.py), [test_phase2_layers.py](../engine/tests/test_phase2_layers.py).
- **Differential test**: `van_han.read` mới so với bản if/else cũ đóng băng ([legacy_van_han.py](../engine/tests/legacy_van_han.py)) trên 400 lá số ngẫu nhiên × 12 cung, 1 000+ cung của lá số thật; 28/28 luật đều được so ít nhất một lần (3 luật hiếm bằng ca dựng sẵn, có cả ca thiếu một thành phần để chắc luật không bắn).
- **A/B hồi quy** ([ab_regression.py](../tools/ab_regression.py), nay có thêm `/api/year` ở 3 năm): bản `van_han.py` cũ vs mới, 18 lá số × 5 đầu ra: **IDENTICAL**.
- Fact thời gian khớp `temporal.tuvi_year` hiện có (tiểu hạn, lưu Thái Tuế, đại hạn, lưu Tứ Hóa) trên 2 lá số × 4 năm.

## So sánh trước/sau

Tạo lại: `python tools/compare_year_before_after.py 1990-5-17-10-30-male 2024`.

### 1990-5-17-10-30-male xem năm 2024 (tuổi mụ 35)

**TRƯỚC (production)**: đại hạn Phúc Đức (26–35); tiểu hạn ở Phúc Đức; lưu Thái Tuế ở Quan Lộc; lưu Tứ Hóa: Hóa Lộc (Liêm Trinh) ở Tài Bạch; Hóa Quyền (Phá Quân) ở Phu Thê; Hóa Khoa (Vũ Khúc) ở Mệnh; Hóa Kỵ (Thái Dương) ở Phụ Mẫu.
- 1 câu về tiểu hạn; mỗi tầng được đọc riêng, không có chỗ nào nói các tầng chồng lên nhau.

**SAU (đa tầng, thử nghiệm)**:

- đại hạn Tứ Hóa (can Mậu): Hóa Lộc → Phúc Đức; Hóa Quyền → Phụ Mẫu; Hóa Khoa → Tật Ách; Hóa Kỵ → Điền Trạch
- cung Phụ Mẫu: các tầng cùng rơi vào đây — vị trí thời gian —, hóa bản mệnh ['Hóa Lộc', 'Hóa Kỵ'], đại hạn ['Hóa Quyền'], lưu ['Hóa Kỵ']
- cung Phúc Đức: các tầng cùng rơi vào đây — vị trí thời gian ['dai_han', 'tieu_han'], hóa bản mệnh —, đại hạn ['Hóa Lộc'], lưu —
- `ly_dai_tieu_trung_cung` (neutral, độ sâu 1, supported) @Phúc Đức
- `ly_ky_chong_tang` (limit, độ sâu 1, limited) @Phụ Mẫu

Production nói rõ từng tầng nhưng không cho thấy chúng **chồng lên nhau**: năm 2024 cung Phụ Mẫu vừa có Kỵ bản mệnh vừa có Kỵ lưu niên, và cung Phúc Đức vừa là đại hạn vừa là tiểu hạn. Bản mới nêu hai điều đó thành fact và finding có why-chain; ngoại lệ Khoa đại hạn/lưu không áp dụng ở đây (đại hạn Khoa ở Tật Ách, lưu Khoa ở Mệnh).

Ví dụ suy luận nhiều bước (lá số 1950-1-4 giờ 4, nam; năm 1996): cách Tử Phủ Vũ Tướng thành ở Mệnh (kết quả cách cục, Phase 1) + lưu Kỵ rơi vào cung Mệnh (luật tầng thời gian đặt fact `derived.ky_luu_cham_truc_menh`) ⇒ luật cấp cao `ly_ky_luu_khi_menh_co_cach`: "lưu Kỵ chạm trục Mệnh trong khi Mệnh có cách thành, cần xét cách có bị phá". Đồng thời cung đại hạn nằm trong tam phương Mệnh có cách thành. Không tầng nào trong production nối được hai thông tin này.

## Còn lại

- Đối chiếu sách cho 8 luật đa tầng (đặc biệt "chồng Kỵ", "Khoa giải") trước khi đưa vào production; hiện chưa có trang nguồn.
- Phi Hóa (can cung bay Tứ Hóa), lưu tinh (lưu Lộc Tồn/Kình/Đà/Khôi Việt/Xương Khúc/Mã), nguyệt hạn: cần công thức đã xác minh.
- Chưa nối UI; dữ liệu ở `/api/year` → `experimental`.
