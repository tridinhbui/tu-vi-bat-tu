# Phase 8 — Comparison Accuracy & Release QA

Phạm vi: module so sánh hai lá số (`compare.py`, `compare_deep.py`, `compare_tuvi.py`, `data/compare_rules.json`, `web/js/compare.js`, `web/js/compare_ui.js`, phần CSS `.cpx-*`, `tests/test_compare_deep.py`). Kế thừa commit `3d4aabf`; các sửa lỗi của giai đoạn này nằm ở commit `7e246b9`.
Không sửa: `api.py`, `geju.py`, `yongshen.py`, `beginner.js`, `util.js` (commit `7e246b9` chỉ chạm 8 file của module so sánh). Không merge, không deploy, không push.

Ngày chạy: 2026-10-18. Nhãn: **PASS** đã kiểm và đạt; **FIXED** có lỗi, đã sửa trong module và có test; **FAIL** lỗi còn lại trong module; **BLOCKED** cần người hoặc session khác, hoặc cần quyền truy cập chưa có.

## Tóm tắt

| # | Hạng mục | Kết quả |
|---|---|---|
| 1 | Tính toán so với engine độc lập | PASS |
| 2 | Đại vận / đại hạn | **FIXED** trong module so sánh; **BLOCKED** ở nơi khác còn dùng công thức cũ |
| 3 | Nhãn bằng chứng | **FIXED** (2 nhãn quá mạnh), phần còn lại PASS |
| 4 | UX, trạng thái, a11y | PASS (có 4 lỗi đã sửa); kiểm với công nghệ hỗ trợ thật: BLOCKED |
| 5 | Hồi quy, API | PASS trên worktree sạch; production thật: BLOCKED (chưa kiểm vì không gọi ra ngoài) |
| 6 | Release (thay đổi dở, PR, CI) | PASS (xung đột); **BLOCKED** (CI Cloudflare đang lỗi, chưa xem được log) |

## 1. Audit tính toán — PASS

Đối chiếu kết quả so sánh với engine gốc bằng các test vi sai (`tests/test_compare_deep.py`, mục "Phase 8"):

| Kiểm | Cách kiểm | Kết quả |
|---|---|---|
| Quan hệ Thiên can / Địa chi giữa hai lá số | 30 cặp ngẫu nhiên; so tập quan hệ với bản brute-force dùng các bảng 八字真宗 pp.19-20 **gõ lại riêng trong test**, không import từ `tvbt.bazi` | khớp 30/30 |
| Bốn trụ và Thập Thần của từng trụ | 10 cặp; so với `bz.pillars[...]` (tên trụ, `stem_ten_god`) | khớp |
| Ngũ Hành trên tám chữ | 10 cặp; đếm lại từ `STEM_ELEMENT`, `BRANCH_ELEMENT` | khớp |
| Thập Thần hai chiều | 10 cặp; hàm Thập Thần viết lại từ nguyên tắc (hành, âm dương) trong test | khớp |
| Tử Vi: Mệnh, Thân, Phu Thê, cục | 6 cặp; so với `tv.palaces`, `tv.cuc` | khớp |
| Tử Vi độc lập | test AST: `compare_tuvi.py` không import module Bát Tự | PASS |
| Không có điểm hợp/khắc | quét mọi khóa JSON và các cụm "hợp nhau", "không hợp", "xung khắc" | PASS |
| Đối xứng A/B | đổi chỗ hai người, quan hệ đổi chỗ tương ứng | PASS |

Giới hạn của phép kiểm: các bảng "độc lập" do tôi gõ lại từ cùng nguồn đã đối chiếu trước đó; đây là kiểm chéo cài đặt, không phải đối chiếu lại trang sách gốc.

## 2. Đại vận / đại hạn

### Lỗi trong công thức phía trình duyệt (`insights.currentPhase`, trước đây dùng cho phần Tổng quan)
1. **Đại vận dùng `start_year_approx` (năm làm tròn)** thay vì ngày khởi vận chính xác, nên đổi vận trễ tới gần một năm, và bỏ qua tháng sinh.
2. **Tuổi mụ tính theo năm dương** (`năm hiện tại − năm sinh dương + 1`), trong khi Tử Vi dùng năm âm lịch. Sai một tuổi với người sinh trước Tết, và sai cho mọi người trong khoảng đầu năm dương đến Tết.
3. **"Hôm nay" lấy theo đồng hồ và múi giờ của trình duyệt**, không theo nơi sinh.

Đo trên 300 lá số ngẫu nhiên (sinh 1940-2015), ngày 17/10/2026: công thức cũ cho **sai đại vận ở 14 lá số (4,7%)**, **sai tuổi mụ ở 23 (7,7%)**, **sai cung đại hạn ở 4 (1,3%)**. Ví dụ: nữ sinh 04/01/2006 10:00, công thức cũ ra tuổi 21 và đại hạn Phụ Mẫu, đúng là tuổi mụ 22 và đại hạn Phúc Đức.

### Cách sửa (FIXED, trong module so sánh)
- `compare_deep.current_phase` tính ở máy chủ: so ngày hôm nay với `start_date` chính xác từng đại vận; đổi hôm nay sang năm âm lịch bằng đúng lịch của lá số (`vn`, `vn_south`, `cn`) rồi tra đại hạn; "hôm nay" lấy theo múi giờ nơi sinh.
- Không tự kết luận khi sát mốc: cách ngày chuyển vận không quá 60 ngày thì hiện nhãn "sát ngày chuyển vận"; tháng Chạp và tháng Giêng âm lịch thì hiện nhãn "quanh Tết". Mỗi mục kèm danh sách giới hạn (múi giờ, cách làm tròn khởi vận khác nhau giữa trường phái, đại hạn đổi theo Tết).
- Chưa khởi vận, đã qua các đại hạn, hoặc bước tính lỗi: hiện rõ trạng thái đó, không đoán.
- Trình duyệt không còn tính gì: bỏ `/api/chart` ×2 khỏi giao diện so sánh.
- Test: đổi vận đúng ngày (trước một ngày / đúng ngày), chưa khởi vận, Tết (31/1 chưa sang năm âm lịch mới), múi giờ (22/12 18:00 UTC đã là 23/12 ở Hà Nội), lỗi tính, đối chiếu `temporal.bazi_year` và `temporal.tuvi_year` cách xa mốc.

### BLOCKED
`insights.currentPhase` vẫn được dùng ở các thẻ tóm tắt, báo cáo và chương đại vận ngoài phần so sánh (`beginner.js`, `report.js`, `insights.js`); các file này không thuộc module so sánh và `beginner.js` nằm trong danh sách cấm sửa. **Cần session sở hữu thay bằng `v2.phase` hoặc đọc `start_date`**, cùng lỗi 4,7% / 7,7%.

## 3. Nhãn bằng chứng

Kết quả kiểm từng mục theo ba loại (Tính toán / Quy tắc có nguồn / Giả thuyết):

| Phát hiện | Xử lý |
|---|---|
| Dòng Nguyệt lệnh ghi "(phe mình)": khái niệm "phe mình" thuộc quy tắc 40% (một phần), nhưng dòng mang nhãn "Quy tắc có nguồn" đầy đủ | **FIXED**: bỏ cụm này khỏi dòng nguyệt lệnh; test chặn lặp lại |
| Ba mục "chưa đủ căn cứ" về dụng thần, thời gian, Tử Vi gắn vào quy tắc của sách (Thập Thần, hướng cân bằng), hộp chi tiết hiện sai nguồn | **FIXED**: quy tắc riêng `CMP_LIMITS` (loại Tính toán, ghi rõ là lời khai báo giới hạn); riêng mục dụng thần trước đây còn bị ẩn cùng bản nháp ở chế độ thường |
| Quy tắc 40% | PASS: luôn hiện "Quy tắc có nguồn · một phần"; lá số sát ngưỡng, có cách đặc biệt hoặc thiếu dữ liệu không hiện vượng/nhược |
| Dụng thần, hướng cân bằng, bù hành, vai trò trụ, mùa của người kia | PASS: giả thuyết thử nghiệm, chỉ hiện khi bật `?thu-nghiem` |
| Đại vận / đại hạn hiện tại | gắn "Quy tắc có nguồn" (八字真宗 p.23, Thực Hành p.27) kèm giới hạn |

Test chặn: rule nháp ⇔ nhãn giả thuyết ⇔ ẩn ở chế độ thường; chế độ thường chỉ có Tính toán và Quy tắc có nguồn; mọi rule "có nguồn" trỏ tới nguồn đã đối chiếu.

## 4. UX, trạng thái, trợ năng

Kiểm trên Chromium trong ứng dụng (chưa kiểm Safari, Firefox, thiết bị thật).

| Kiểm | Kết quả |
|---|---|
| Rộng 375 / 768 / 1440 px: không tràn ngang, hộp thoại đúng cỡ (375 toàn màn hình, 737 ở tablet, 980 ở 1440) | PASS |
| Đổi A/B, nút đổi chỗ, chọn trùng người (tự chuyển sang người khác) | PASS |
| Đóng rồi mở lại: không gọi lại API (0 request), giữ lựa chọn A/B và vị trí cuộn | PASS |
| Đổi chế độ thử nghiệm: tính lại đúng, không lẫn nội dung | PASS |
| Thiếu dữ liệu (lá số đã lưu mất giờ/phút): thông báo tiếng Việt nêu tên trường thiếu | PASS |
| API v1 (bỏ `v2`): hiện dữ kiện cơ bản | PASS (lỗi nhỏ: còn chữ "người A" thô, **FIXED** thành tên) |
| API 404: thông báo + nút "Thử lại" | PASS |
| API 500: thử lại tự động (tối đa 3 lần, khoảng 3 giây) rồi báo lỗi + "Thử lại", bấm lại phục hồi | PASS |
| Hộp chi tiết lồng nhau: mở chồng lên hộp chính, Escape đóng lớp trên, focus quay lại đúng mục vừa bấm; Escape lần hai đóng hộp chính, focus về nút "So sánh hai lá số" | PASS (bàn phím thật) |
| Thứ tự Tab: nút đóng → chọn A → đổi chỗ → chọn B → thanh các phần; focus không thoát khỏi hộp modal; viền focus 2 px | PASS |
| Nhãn trợ năng: `aria-labelledby` hộp thoại, `aria-label` thanh điều hướng, `th scope=row`, mọi nút có tên, ô chọn có nhãn | PASS |
| Độ tương phản chữ nhỏ | PASS (tối thiểu 4,5; nhãn giả thuyết sát ngưỡng nên **FIXED** đậm hơn) |
| Cỡ nút "?" 22 px dưới mức 24 px của WCAG 2.2 | **FIXED** (28 px) |
| Chữ nhãn bằng chứng 9,6 px quá nhỏ | **FIXED** (10,9 px) |
| Bảng Tổng quan phải cuộn ngang ở 375 px làm mất cột B | **FIXED**: xếp dọc theo từng dòng, mỗi giá trị có tên người |

BLOCKED: chưa thử với trình đọc màn hình thật (VoiceOver, NVDA); chưa thử trên thiết bị cảm ứng thật; ô chọn dùng điều khiển gốc của trình duyệt.

## 5. Hồi quy và API

- **Worktree sạch** (`git worktree` tại `7e246b9`, không có thay đổi dở nào): **1131 passed, 1 skipped, 2 xfailed**, 100 giây. Mục skip là `test_bazi_zz_tables.py:163` (api.py chưa truyền `zz=True`, điểm tích hợp của session khác). Trên cây làm việc hiện tại (kèm thay đổi dở của session khác) cũng đạt 1131.
- **Gói chạy của container**: tạo venv mới chỉ có `sxtwl ephem tzdata fastapi uvicorn` (đúng Dockerfile), chạy uvicorn từ worktree sạch: `GET /` 200, `POST /api/compare-charts` trả đủ trường v1 và `v2` (39 mục), ngày sai trả 422. Không thiếu phụ thuộc.
- **Tương thích v1**: test khóa 8 trường v1 giống hệt `compare.compare(...)`; endpoint và chữ ký route không đổi; phía giao diện tự lùi về dữ kiện cơ bản khi không có `v2`.
- **Production cũ**: mô phỏng ba trạng thái (chỉ v1, 404 do chưa có route, 500) đều có thông báo hợp lý. **BLOCKED**: chưa gọi production thật (không gọi ra ngoài khi chưa được phối hợp); cần kiểm sau khi phối hợp với session sở hữu `api.py`.
- Số liệu "hôm nay" của `phase` đọc đồng hồ máy chủ; test cố định bằng tham số `today`, golden không phụ thuộc đồng hồ.

## 6. Release

### Thay đổi chưa commit của session khác (không đụng)
12 file đang sửa dở: `docs/PHASE4_KIEM_TOAN_NGUON.md`, `engine/data/experimental/formation_audit.json`, `formation_proposals.json`, `formations_school_variants.json`, `engine/tests/oracle_tuvi_independent.py`, `test_formation_audit.py`, `test_formation_proposals.py`, `test_formation_variants.py`, `engine/tvbt/tuvi.py`, `tools/build_formation_audit.py`, `build_formation_proposals.py`, `build_formation_variants.py`. Không file nào thuộc module so sánh. Lưu ý: `tuvi.py` đang bị sửa, và `compare_tuvi.py` đọc `TuViChart`; test so sánh đạt cả khi có và không có thay đổi này.
Cây làm việc chính hiện đứng ở nhánh `feat/observatory-result-pages` (đổi so với đầu giai đoạn); còn nhiều worktree khác đang mở.

### PR và xung đột
| PR | Nhánh → đích | Chứa code so sánh | Mergeable | Ghi chú |
|---|---|---|---|---|
| #1 | `zz-api-integration` → main | không | MERGEABLE | không chồng file với module so sánh |
| #2 | `phase4-audit` → main | có (đến `3d4aabf`) | MERGEABLE | 55 file, chồng 11 file của module so sánh; **chưa có `7e246b9`** |
| #3 | `phase5-sources` → `phase4-audit` | có (kế thừa #2) | MERGEABLE | không chồng thêm |

`git merge-tree` giữa `7e246b9` và `phase4-audit`: **không có xung đột**. Các commit so sánh (`ba355e2`, `3d4aabf`, `7e246b9`) **chưa nằm trên `main`**; muốn lên main cần đi cùng PR #2 (hoặc PR riêng), và `7e246b9` cần được đẩy lên nhánh đó. Tôi chưa push.

### CI — BLOCKED
Check duy nhất là Cloudflare "Workers Builds: tu-vi-bat-tu". Kết quả: **thất bại trên cả ba PR**, kể cả #1 không chứa code so sánh; **thành công** trên commit cũ của `origin/main`. Vì vậy lỗi không đến từ module so sánh, nhưng nguyên nhân chưa biết: log nằm trong dashboard Cloudflare, tôi không có quyền xem. Đã loại trừ: `tsc --noEmit` sạch; phụ thuộc runtime đủ (mục 5). Chưa loại trừ: bước build container (không có Docker để thử), giới hạn tài nguyên hay cấu hình trên Cloudflare. **Cần chủ repo mở log build để chốt nguyên nhân trước khi merge.**

## Việc còn lại và người nhận
1. Thay `insights.currentPhase` bằng `v2.phase` ở các thẻ tóm tắt và báo cáo (`beginner.js`, `report.js`, `insights.js`): session sở hữu các file đó.
2. Mở log Workers Builds thất bại của PR #1, #2, #3: chủ repo.
3. Đẩy `7e246b9` lên nhánh của PR #2 hoặc mở PR riêng cho module so sánh; kiểm `/api/compare-charts` trên production sau khi phối hợp với session sở hữu `api.py`.
4. Thử bằng trình đọc màn hình thật và thiết bị thật nếu cần đạt chuẩn trợ năng.
