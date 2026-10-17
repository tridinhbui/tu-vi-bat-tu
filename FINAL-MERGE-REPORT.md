# FINAL MERGE REPORT — tu-vi-bat-tu

Ngày chạy: 2026-10-17 (buổi tối, giờ máy). Người thực hiện: Claude (vai Release Manager / Domain Validation Lead).
Nhánh tích hợp: **`qa/final-merge`** (worktree `…/scratchpad/integ`, đầu nhánh `f239464`, cắt từ `main` cục bộ `bb80ab1`).
**Chưa push, chưa merge vào `main`, chưa deploy, không đổi API production, không bật cờ thử nghiệm mặc định.**

> Cảnh báo vận hành: các nhánh và working tree của các session khác **thay đổi liên tục trong lúc tôi làm** (xem §1.3). Mọi kết luận dưới đây gắn với đúng các SHA ghi ở đây; nhánh nào đi tiếp sau các SHA đó chưa được kiểm.

## 0. Kết luận

| Hạng mục | Phân loại | Ghi chú ngắn |
|---|---|---|
| PR #2 `phase4-audit` | **FIX THEN MERGE** → đã sửa, đã merge vào nhánh tích hợp | Đổi hình dạng `/api/phi-hoa` (mất khóa cấp trên cùng) → đã khôi phục khóa v1 + test |
| PR #3 `phase5-sources` | **MERGE** (nhánh tích hợp) | Chỉ tài liệu/dữ liệu thử nghiệm; xếp chồng trên #2 |
| PR #1 `zz-api-integration` | **MERGE** (nhánh tích hợp), kèm một đính chính | Cờ `bat_tu_direct` mặc định tắt; mô tả PR nói "phản hồi mặc định giống hệt" là **không đúng** (`pending` đổi 20 → 0, xem §5.2) |
| PR #4 `bazi-deep-draft-integration` (mới xuất hiện giữa chừng) | **MERGE** (nhánh tích hợp), kèm điều kiện | Cờ mặc định tắt; Phase 8 sửa 4 dòng dụng thần ở dữ liệu mặc định → cần người đọc lại ảnh trang |
| `feat/observatory-result-pages` — redesign giao diện (`39329e3`) | **MERGE** (nhánh tích hợp) | Chỉ trình bày; QA 375/768/1440 đạt |
| `feat/observatory-result-pages` — so sánh hai lá số (`7e246b9`, `be7e63e`) | **MERGE** (nhánh tích hợp), kèm blocker còn lại | `insights.currentPhase` ở thẻ tóm tắt vẫn dùng công thức sai (§7) |
| `feat/observatory-result-pages` — Phase 7 kiểm nguồn (`13c566e`, `5e68dd6`) | **MERGE** (nhánh tích hợp) | Mã production chỉ đổi 1 chuỗi nguồn gốc; lịch pháp có 1 lỗi thật ghi bằng xfail |
| Working tree chính, **chưa commit** (31 mục: sửa 4 pack luật production, `api.py` +2 route, UI học, reference, evidence) | **BLOCKED** | Chưa commit, session chủ đang sửa, không kiểm được thứ đang chạy dở (§1.2) |
| REJECT | không có | |

Chuyển sang `main` và push: **chưa làm** — vì push `main` / merge PR trên GitHub rất có thể kích hoạt Cloudflare Workers Builds (deploy production). Lệnh đề xuất ở §9.

## 1. Kiểm kê

### 1.1 PR, nhánh, commit (SHA đã ghim)

| Nhánh | SHA khi merge | PR | Gốc | Ghi chú |
|---|---|---|---|---|
| `main` (cục bộ) | `bb80ab1` | — | `origin/main` = `87a7274`; cục bộ **hơn 10 commit chưa push** | 10 commit gồm Phase 5/6 Bát Tự sâu, so sánh v2, QA production |
| `phase4-audit` | `e9d34fd` | #2 (mở) | `89565d5` | 12 file; PR trên GitHub hiển thị 55 file vì gồm 10 commit chưa push của `main` |
| `phase5-sources` | `832187d` | #3 (mở, base `phase4-audit`) | #2 | 17 file |
| `zz-api-integration` | `1ef0feb` | #1 (mở) | `87a7274` | 6 file |
| `bazi-deep-draft-integration` | `7a4e7ab` (lúc bắt đầu `d30a908`, rồi `f6a2e25`) | #4 (mở, tạo trong lúc tôi làm) | `bb80ab1` | 3 lần dịch chuyển trong phiên; tôi đã merge đủ tới `7a4e7ab` |
| `feat/observatory-result-pages` | `5e68dd6` (lúc bắt đầu `39329e3`) | chưa có | `bb80ab1` | **một nhánh chứa 3 việc khác nhau**: redesign UI, so sánh hai lá số, kiểm nguồn Phase 7 |
| `integ/phase8-check` (worktree `integ8`) | `02e58de` | — | — | tích hợp tạm của session Bát Tự sâu; không đụng |

Merge trên nhánh tích hợp (`git log --first-parent bb80ab1..`):

```
aac38e0  Merge PR #2 phase4-audit
b7c8237  FIX: Phi Hóa API giữ khóa v1
aef68bb  Merge PR #3 phase5-sources
faa58fa  Merge PR #1 zz-api-integration
c7f1c68  Merge bazi-deep-draft-integration (Phase 7, f6a2e25)
933802e  Merge feat/observatory-result-pages (redesign + so sánh, be7e63e)
97b10b8  Merge bazi-deep-draft-integration (PR #4 Phase 8, 7a4e7ab)
f239464  Merge feat/observatory-result-pages (Phase 7 kiểm nguồn, 5e68dd6)
```

Không có xung đột văn bản ở bất kỳ merge nào (`git merge-tree` trước, merge thật sau). Tổng so với `bb80ab1`: 121 file, mã `engine/tvbt` đổi 10 file (+194/−32). Không đụng `Dockerfile`, `wrangler.jsonc`, `src/`, `package.json`.

### 1.2 Working tree chính (chưa commit) — BLOCKED

Cây `/Users/buidinhtri/Desktop/tuvibattu` đứng ở `feat/observatory-result-pages` và **được sửa liên tục** bởi ít nhất một session đang chạy. Lúc đầu nó chứa việc so sánh (đã được commit thành `7e246b9`, tôi đã merge), rồi việc Phase 7 kiểm nguồn (đã commit thành `13c566e`). Hiện còn **9 file sửa + 22 mục chưa theo dõi**:
- Sửa **4 pack luật production** (`pack_khao_luan_stars.json`, `pack_thuc_hanh_aux2.json`, `pack_thuc_hanh_cach.json`, `pack_thuc_hanh_menh_verse.json`) → đổi luận giải mặc định;
- `engine/tvbt/api.py` thêm `GET /reference` và `GET /api/evidence`;
- `engine/web/index.html`, `js/app.js`, `js/glossary.js`, `js/learn.js` + `lessons_deep.json`, `reference.html`, `reference.json`;
- `source_evidence*.json`, các công cụ `tools/audit_*`, `build_reference.py`, `apply_evidence_corrections.py`, 3 file test mới.

Lý do không merge: chưa commit, đang đổi (các file đổi giữa hai lần tôi kiểm kê), chạm `api.py` và dữ liệu production, không thể kiểm một thứ chưa ổn định, và không được ghi đè file session khác. **Rủi ro tích hợp đã thấy trước:** hai route mới sẽ làm test kiểm kê route của Phase 4 (`test_phase4_isolation.py`, `OPT_IN_ROUTES`) fail cho tới khi được xếp loại mặc định/thử nghiệm.

### 1.3 Phân biệt session và vùng file (suy ra từ commit/diff, không đọc transcript)

| Vùng | Đang ở đâu |
|---|---|
| `api.py` — cờ `bat_tu_direct` | PR #1 (`zz-api-integration`) |
| `api.py` — cờ `bazi_deep_draft`, route `/bazi-deep-draft` | PR #4 |
| `api.py` — route `/reference`, `/api/evidence` | **chưa commit**, working tree chính |
| `bazi_deep/geju.py`, `yongshen.py`, `tvh_dungthan.json` | PR #4 (Phase 8 sửa `yongshen.py` + 4 dòng dữ liệu); `geju.py` không nhánh nào sửa |
| `beginner.js`, `util.js` | không nhánh/commit nào sửa; `beginner.js` còn gọi `insights.currentPhase` sai (§7) |
| Engine so sánh (`compare*.py`, `compare_rules.json`, `compare*.js`) | `7e246b9`, `be7e63e` — nằm trên nhánh `feat/observatory-result-pages` |
| Redesign UI (`atlas.css/js`, `bazi.js`, `tuvi.js`, `index.html`) | `39329e3` — cùng nhánh |
| Kiểm nguồn/lịch pháp Phase 7 | `13c566e`, `5e68dd6` — cùng nhánh; phần dở dang chưa commit (§1.2) |
| Phi Hóa, nguồn Phase 4/5 | PR #2, #3 |

Điểm cần lưu ý: **một nhánh gộp ba luồng việc** nên không thể merge riêng UI khỏi so sánh bằng thao tác nhánh; tôi đã merge nguyên nhánh sau khi kiểm từng luồng.

## 2. Kết quả test

Môi trường: macOS, Python 3.13 (`.venv` của dự án), Node 24.7, mọi lần chạy ở worktree sạch riêng, `-p no:cacheprovider`.

| Cây mã | passed | skipped | xfailed | failed |
|---|---|---|---|---|
| `main` `bb80ab1` (baseline) | 1119 | 1 | 2 | 0 |
| `zz-api-integration` (cô lập; gốc cũ) | 822 | 0 | 2 | 0 |
| `phase4-audit` (cô lập) | 1213 | 1 | 2 | 0 |
| `phase5-sources` (cô lập) | 1220 | 1 | 2 | 0 |
| `feat/observatory-result-pages` `39329e3` (cô lập) | 1119 | 1 | 2 | 0 |
| `bazi-deep-draft-integration` `f6a2e25` (cô lập) | 1140 | 1 | 2 | 0 |
| tích hợp sau PR #2 + fix | 1325 | 1 | 2 | 0 |
| … sau PR #3 | 1332 | 1 | 2 | 0 |
| … sau PR #1 | 1349 | 0 | 2 | 0 |
| … sau Phase 7 bazi-deep | 1370 | 0 | 2 | 0 |
| … sau redesign + so sánh | 1382 | 0 | 2 | 0 |
| … sau PR #4 Phase 8 | 1386 | 0 | 2 | 0 |
| **Cuối `f239464`** | **1448** | **0** | **3** | **0** |

Ba xfail: hai "documented gap" có từ trước của `bazi_deep` (`test_known_gaps_are_still_gaps`) và **một lỗi lịch thật mới được ghi nhận** (`test_vn_calendar_2033_leap_month_11_at_the_year_end`, §6).

Kiểm khác:
- **Frontend**:       19 file `engine/web/js/*.js` qua `node --input-type=module --check` (0 lỗi cú pháp); `phase7_viewmodel_check.js` (DOM giả lập 1.500 lá số) chạy trong pytest, không bị skip.
- **Kiểu/tĩnh**: `tsc --noEmit` (Worker `src/index.ts`) 0 lỗi; `compileall` Python sạch. **Không có** pyflakes/ruff/mypy cài sẵn → không chạy.
- **Quét độc lập 116.928 lá số** (`tools/scan_phase6.py`) chạy lại trên cây tích hợp: `mismatches: 0`, tệp đầu ra **giống từng byte** với bản đã ghim.
- **E2E trình duyệt**: §8.
- **Build**: không có bước build frontend (tĩnh). `wrangler deploy --dry-run` **không chạy** (cần Docker, và tôi không được deploy). Container: không dựng lại; diff không đụng Dockerfile và không thêm phụ thuộc ngoài stdlib (`sxtwl`, `ephem`, `tzdata`, `fastapi`, `uvicorn` đã có).
- **CI GitHub**: duy nhất là Cloudflare "Workers Builds: tu-vi-bat-tu" — **fail trên cả PR #1, #2, #3**, kể cả PR #3 chỉ có tài liệu/dữ liệu; **success** trên `origin/main` `87a7274`. Không thấy log (Cloudflare MCP chưa được uỷ quyền) → nguyên nhân chưa biết. Không phải lỗi mã đã đo được.

## 3. Audit domain Tử Vi / Bát Tự

| Mảng | Bằng chứng | Kết quả |
|---|---|---|
| An sao Tử Vi, Mệnh/Thân, cục, Tứ Hóa, Tuần/Triệt, 17 biến thể cách cục | Oracle độc lập `oracle_tuvi_independent.py` (không import `tvbt`), quét lại 116.928 lá số | 0 sai khác |
| Trụ ngày | 600 ngày ngẫu nhiên 1900–2049 so với neo số học 2000-01-01 = Mậu Ngọ (tôi tự viết) | 600/600 |
| Trụ năm | 150 năm (1900–2049), giữa năm | 150/150 |
| Tiết khí: Lập Xuân 2024/2023/2020/2000 (giờ UTC+8 đã công bố) ±10 phút | đổi trụ năm đúng ở mốc | 4/4 |
| Giờ Tý (early/late), múi giờ | đổi quy tắc Tý đúng cả trụ ngày lẫn trụ giờ; trụ ngày/tháng/năm giống nhau khi cùng thời điểm ở 3 múi giờ | Đạt. Trụ **giờ** theo đồng hồ địa phương nơi sinh nên khác nhau giữa múi giờ — đúng quy ước, không phải lỗi |
| Lịch Trung Quốc `cn` | HKO 1901–2100, 47.789 ngày (Phase 7) | 0 sai khác |
| Lịch Việt Nam `vn` | oracle amlich viết lại độc lập + PyEphem (Phase 7) | khớp, **trừ 2033-12-22..31** (tháng nhuận 11 bị đánh số là 12) = **lỗi thật, chưa sửa** (xfail strict) |
| Đại vận / đại hạn trong so sánh | so với `temporal.*` và bảng độc lập (Phase 8 so sánh); tôi kiểm tay: khởi vận 1990-05-17 nam = 1996-12-23, Giáp Thân 2016-12-23 → 2026-12-23, tuổi mụ 2026 = 37 | Đạt |
| Đại vận / đại hạn **ở thẻ tóm tắt/báo cáo** | không đạt (§7) | **Blocker còn lại** |
| Cách cục, dụng thần, Thập Thần, các trường phái | các test Phase 5/6 (5.000 lá số hai chiều, schema, cách ly trường phái) đều qua; kiểm tay: cờ tắt ⇒ không có `experimental_findings`, `direct_summary`, `bazi_deep_draft` ở 4 endpoint mặc định | Đạt về cách ly. **Không** có nghĩa là dụng thần đã được kiểm chứng học thuật |
| So sánh hai lá số | nhãn bằng chứng ba loại (tính toán / có nguồn / giả thuyết); giả thuyết chỉ hiện ở `?thu-nghiem`; sát ngưỡng 40%, cách đặc biệt, thiếu dữ liệu không ép vượng/nhược; không có điểm hợp/khắc | Đạt (đọc tài liệu + test + quan sát UI) |

## 4. Giới hạn nguồn (không che giấu)

1. **Không biến giả thuyết thành kết luận.** Mọi cách cục biến thể và mọi phương pháp dụng thần của `bazi_deep` vẫn `draft`. `empirical_validated = no` ở mọi phương pháp; không phương pháp nào `source_rule_verified = yes`. **0/120 ô điều hậu và 0/10 ví dụ có người xác nhận.** 9 ô sách tự mâu thuẫn chưa có quyết định học thuật.
2. **Bất đồng trường phái ảnh hưởng cả sản xuất lẫn oracle:** Nhâm-Khoa = Tả Phụ (Khảo Luận tr.36, 197; sản xuất theo) so với Thiên Phủ (Thực Hành tr.20-21; một bản 全書 số hoá cũng ghi 府). Hai nguồn **không** "agree on all ten stems". Chuỗi nguồn gốc ở `tuvi.py` đã được sửa đúng sự thật trong `13c566e` (đây là lý do `/api/chart` đổi ở cả 15 lá số mẫu — chỉ khác chuỗi giải thích). Cần chuyên gia quyết định, tôi không chọn.
3. **Oracle độc lập có giới hạn:** công thức Địa Không/Kiếp, Hỏa/Linh, Thiên Hình, Lực Sĩ gõ theo quy tắc chuẩn chứ không theo một trang sách đã đọc; bảng độ sáng đặt trên cùng trang sách với sản xuất; độ sáng Thái Dương ở Thân/Mùi để trống (không đoán); không có bảng lịch Việt Nam xuất bản độc lập (dựa amlich + PyEphem; quy tắc UTC+8 trước 1968 có nguồn mâu thuẫn VASTI 1/2019 vs Wikipedia 8/1967; `vn_south` đến 1975 ghi chưa xác minh).
4. **Nguồn Phase 5 (PR #3):** bản 紫微斗數全書 được đọc qua một bản web (wikisource) bằng công cụ tóm tắt, hai lần khớp nhau, **không có bản thứ hai và chưa đối chiếu bản in**; ba cuốn sách Việt đọc qua PDF của người dùng (một số trang qua ảnh vì lớp chữ vỡ).
5. **Kiểm trích dẫn của audit chỉ là kiểm từ khoá** — không chứng minh ý nghĩa câu trích (tự báo cáo trong `PHASE6_INDEPENDENT_VALIDATION.md`).
6. **Các bản chép bảng sách chỉ do một người đọc** (mô hình), nay có thêm một lượt chép mù. Lượt mù Phase 8 vừa tìm ra **4 dòng sai của chính engine** ở bảng dụng thần tr.378–386 — bằng chứng rằng nhãn `transcription_verified` một người đọc là chưa đủ. Một dòng (Kiến lộc, vượng, Thực Thương nhiều) có dụng thần do hệ thống **suy ra**, sách không nêu (đánh dấu `yong_inferred`). 14 dòng Kiến lộc/Kình dương tr.386 chưa so được bằng lượt mù.
7. **Các test đọc PDF** dùng sách trong `~/Downloads` và tự skip khi không có PDF; skip không phải bằng chứng. Ở máy này skip = 0; trên CI không có PDF thì bằng chứng chỉ còn các JSON đã ghim (`quote_check`).
8. Các bảng "độc lập" trong test so sánh được gõ lại từ cùng nguồn đã đối chiếu → kiểm chéo cài đặt, không phải đối chiếu lại trang sách gốc.

## 5. Tương thích API, cờ, xác thực

### 5.1 So với **bản đang chạy** (`origin/main` = `87a7274`)
Băm phản hồi 139 lời gọi (12 lá số × 8 endpoint, 3 biến thể lịch/giờ, so sánh, tra cứu, trang) trên `87a7274` và trên nhánh tích hợp:

| Endpoint | Thay đổi | Đánh giá |
|---|---|---|
| `/api/analysis`, `/api/year`, `/api/twelve-gods`, `/api/hour-sweep`, `/api/compare-hours`, `/api/lunar-to-solar`, `/api/rules`, `/api/dignity*`, `/library` | **không đổi** | |
| `/api/chart` | chỉ chuỗi nguồn gốc Tứ Hóa (xem §4.2); khóa không đổi | chấp nhận |
| `/api/reasoning` | **chỉ** `systems.bat_tu.pending` (§5.2); findings/text/blocked/conflicts giống hệt | chấp nhận, ghi chú |
| `/api/claims` | chuỗi tiếng Việt khóa `bt_zz_*` | chấp nhận |
| `/api/bazi-structure` | không đổi trên lưới mẫu | |
| `/api/bazi-timeline` | 2/15 lá số mẫu đổi (dòng dụng thần Phase 8) | chấp nhận có điều kiện (§7) |
| `/api/compare-charts` | thêm khóa `v2` (cộng thêm), `v1` giữ nguyên 8 trường; thêm mục "đại vận/đại hạn hiện tại" phụ thuộc đồng hồ máy chủ | tương thích ngược; không còn tất định theo thời gian (có chủ đích; golden ghim `today`) |
| `/api/phi-hoa` (thử nghiệm) | thêm `computation`, `interpretation`; **khóa v1 được khôi phục** | **đã sửa** |
| `/` | HTML mới (redesign) | chủ ý |

Vi phạm tương thích tìm thấy và **đã sửa**: PR #2 chuyển `table/edges/findings/blocked/conflicts/problems` của `/api/phi-hoa` vào khối lồng → client cũ vỡ. Sửa ở `b7c8237` (+ test `test_phi_hoa_v1_top_level_keys_still_present_and_equal_to_nested_blocks`). Hai báo cáo Phase 4/5 nói "không có consumer" — đúng với UI, nhưng API đã public nên vẫn giữ tương thích.

### 5.2 Đính chính cho PR #1
Mô tả PR nói với cờ tắt phản hồi "giống hệt cũ". Đo thực tế: `systems.bat_tu.pending` trước đây bị 20 luật `BT_ZZ_DIRECT_*` chưa đánh giá chiếm hết (giới hạn 20); nay là 0 nên thẻ báo cáo "N quy tắc chờ dữ kiện" của Bát Tự đổi từ 20 sang 0. Hướng đi hợp lý (luật thử nghiệm không nên đếm là "chờ"), nhưng không giống hệt.

### 5.3 Cờ
`experimental`, `bat_tu_direct`, `bazi_deep_draft` đều mặc định `false`. Đã kiểm thủ công: tắt ⇒ phản hồi không có `experimental_findings` / `direct_summary` / `bazi_deep_draft`; bật `bat_tu_direct` ⇒ 5 finding 直断 đã xác minh (trong 9 finding Bát Tự) + 2 `experimental_findings` đều có `experimental: true` và nhãn "Thử nghiệm: …", không lọt vào `text`. Giao diện chính không gọi `/api/phi-hoa` hay endpoint thử nghiệm (test của Phase 4 qua). Trang `/bazi-deep-draft` ở trạng thái tắt: 0 lời gọi API.

### 5.4 Xác thực, rate limit, đầu vào
- **Không có xác thực, không rate limit, không CORS** ở bất kỳ endpoint nào, cả production lẫn nhánh tích hợp (Worker chỉ proxy sang container). Không đổi bởi các merge này. `/api/rules/test` công khai (không trạng thái, không ghi).
- Kiểm đầu vào: năm 1800, giới tính lạ, 30/2, múi giờ không tồn tại, cờ boolean sai đều trả **422**. `/api/bazi-timeline` tối đa 120 năm: 0,12 s, 480 KB — chi phí tính toán vừa phải nhưng không giới hạn tần suất.
- **Chưa kiểm production thật** (không gọi ra ngoài); chỉ so với bản `87a7274` chạy cục bộ.

## 6. Lỗi/vấn đề tìm thấy

| # | Mức | Vấn đề | Xử lý |
|---|---|---|---|
| 1 | P1 | PR #2 phá hình dạng `/api/phi-hoa` | **Đã sửa** (`b7c8237`) |
| 2 | P1 | Lịch Việt Nam: 2033-12-22..31 (tháng nhuận 11) bị đánh số tháng 12, vì `lunar_vn.solar_to_lunar` cắt theo năm dương | **Chưa sửa** — module của session khác, cần sửa riêng + quét oracle hằng năm; ghi bằng xfail strict. Chỉ ảnh hưởng ngày sinh/ngày tra rơi vào 10 ngày đó (API cho phép tới 2049) |
| 3 | P1 | `insights.currentPhase` (trình duyệt) ở thẻ tóm tắt/báo cáo | **Chưa sửa** — xem §7 |
| 4 | P2 | `/api/compare-charts` `v2.sources[].locator` **không tất định** giữa các tiến trình (đổi theo `PYTHONHASHSEED`): nhiều luật cùng nguồn nhưng khác locator, `compare_deep.py:371` lấy cái cuối theo thứ tự tập hợp. Có trên cả `main`. | **Chưa sửa** (tránh đụng file session so sánh). Đề xuất: duyệt `sorted(used)` hoặc nối các locator |
| 5 | P2 | PR #1: câu "giống hệt" không đúng (§5.2) | Ghi nhận |
| 6 | P3 | Giao diện: sao trong cung là `span role=button` lồng trong `<button class="pal">` (98 phần tử), ngăn kéo chi tiết cung là `aside` không modal và không chuyển focus; mục glossary 11–17 px; `id="fe-a"` trùng (marker SVG). **Có sẵn ở `main`**, không do redesign | Ghi nhận |
| 7 | Quy trình | Merge PR #2/#3/#4 lên GitHub sẽ mang theo 10 commit chưa push của `main` (PR #2 = 55 file, PR #4 = 13 commit) | §9 |

## 7. Blocker còn lại

1. **Công thức đại vận/đại hạn sai ở thẻ tóm tắt** (`insights.js` `currentPhase`, dùng ở `beginner.js:115,133`, `report.js:95,159`): dùng đồng hồ/múi giờ trình duyệt, năm dương thay năm âm lịch cho tuổi mụ, và `start_year_approx` thay vì ngày khởi vận chính xác. Session so sánh đo trên 300 lá số: sai đại vận 4,7%, sai tuổi mụ 7,7%, sai cung đại hạn 1,3%. Phần so sánh đã đúng (tính ở máy chủ, `v2.phase`). **Sửa cần thay bằng dữ liệu `v2.phase`/trường mới của máy chủ — chạm `beginner.js`, `report.js`, `insights.js` (khác session) và có thể thêm trường API.** Đã có sẵn ở production hiện tại, không phải hồi quy do các merge.
2. **Lỗi lịch VN 2033** (§6.2).
3. **Working tree chính chưa commit** (§1.2) — gồm sửa pack luật production và 2 route mới; phải commit, rồi chạy lại toàn bộ test (đặc biệt test kiểm kê route Phase 4) trước khi merge.
4. **Học thuật:** 0/120 ô, 0/10 ví dụ có người kiểm; 9 ô sách tự mâu thuẫn; bất đồng Nhâm-Khoa Tả Phụ/Thiên Phủ; 4 dòng dụng thần Phase 8 + 1 dòng `yong_inferred` cần người đọc lại ảnh trang; không có kiểm chứng thực nghiệm. **Chặn việc bật cờ/công bố dụng thần**, không chặn việc merge bản nháp có cờ tắt.
5. **CI Cloudflare đỏ** trên PR #1, #2, #3 mà chưa biết nguyên nhân (xem log trên dashboard; cần quyền).
6. **Xác thực/rate limit** chưa có (§5.4) — tồn tại sẵn.
7. Chưa kiểm: trình đọc màn hình thật (VoiceOver/NVDA), thiết bị cảm ứng thật, Safari/Firefox, ảnh chụp trực quan ở 1440 px (khung trình duyệt của công cụ cắt ảnh, nên 1440 chỉ kiểm bằng số đo DOM), `?thu-nghiem` trên giao diện chính, `wrangler deploy --dry-run`, production thật.
8. Hai nỗ lực tích hợp song song (`qa/final-merge` của tôi và `integ/phase8-check` của session Bát Tự sâu) — chọn một làm nguồn chính để tránh merge hai lần.

## 8. QA giao diện (trình duyệt tích hợp, server cục bộ từ nhánh tích hợp)

| Kiểm | 375 | 768 | 1440 |
|---|---|---|---|
| Trang kết quả (Bát Tự + Tử Vi): không tràn ngang | đạt | — | đạt (sw 1425 < 1440) |
| Hộp thoại so sánh: kích thước, không tràn, 6 mục điều hướng | đạt (toàn màn hình, 375) | đạt (737) | đạt (980; cả 6 mục không tràn) |
| Tử Vi: ngăn kéo cung (bottom sheet) mở, hiển thị đủ | đạt | — | — |
| Trang `/bazi-deep-draft`: nhãn "chưa được kiểm chứng thực nghiệm" luôn thấy; tắt = 0 lời gọi API; bật = 1 lời gọi, 8 thẻ | đạt | — | — |
| Console lỗi | 0 | 0 | 0 |

Bàn phím và trợ năng: nút trụ Bát Tự `aria-pressed`, focus giữ; 12 cung là `button` có `aria-label` đầy đủ; hộp thoại so sánh `showModal` + `aria-labelledby`, focus vào nút đóng, **Escape đóng và trả focus về nút "So sánh hai lá số"** (đo bằng phím thật); không có nút/ô nhập thiếu tên; không `aria-controls/labelledby` trỏ vào id không tồn tại. Hạn chế đã biết ở §6.6. Trang kết quả ở 768 px **chưa được audit riêng** (chỉ hộp thoại so sánh). Chưa kiểm Escape của ngăn kéo cung bằng phím thật (chỉ đọc mã: giống `main`). Chưa kiểm vòng Tab đầy đủ cả trang (549 phần tử tab được trên trang kết quả).

## 9. Đề xuất để lên `main` (chưa thực hiện — cần quyết định của chủ repo)

Vì `origin/main` (`87a7274`) **thiếu 10 commit** của `main` cục bộ, và PR #2/#3/#4 đều chứa các commit đó, nên:
1. Quyết định có chấp nhận **Workers Builds tự deploy khi push `main`** hay không (tôi suy ra từ việc build chạy trên mỗi commit; chưa xác minh cấu hình). Nếu không muốn deploy ngay, tắt/tạm dừng build tự động trước khi push.
2. Xem log Workers Builds đỏ trên PR #1–#3.
3. Chọn một đường: (a) push `qa/final-merge` thành PR duy nhất vào `main` (ưu tiên: một diff có regression 1448 passed), rồi đóng PR #1–#4; hoặc (b) merge PR theo thứ tự #2 → #3 → #1 → #4 trên GitHub. Với (b) phải đưa kèm bản sửa `b7c8237` vào PR #2 trước.
4. Giải quyết §7.1–7.3 trước khi coi giao diện tóm tắt là chính xác.
5. Không bật `bat_tu_direct`, `bazi_deep_draft`, `experimental` mặc định ở UI cho tới khi blocker học thuật §7.4 được người có chuyên môn duyệt.

```bash
# kiểm lại tại chỗ
cd engine && ../.venv/bin/python -m pytest -q          # chạy trong worktree của qa/final-merge
git log --first-parent --oneline bb80ab1..qa/final-merge
```
