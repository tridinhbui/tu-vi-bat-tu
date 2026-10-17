# Phase 7: tích hợp API an toàn và UI bản nháp cho Bát Tự sâu

> **Cập nhật Phase 8:** mục 5 ("Không làm được: kiểm tra bằng mắt") đã được thay bằng kiểm tra trình duyệt thật, phát hiện 8 lỗi UX/nội dung đã sửa; xem `docs/BAZI_DEEP_PHASE8_REPORT.md`.

Nhánh: `bazi-deep-draft-integration` (tạo từ `main` = `bb80ab1`, worktree riêng; chưa merge, chưa deploy, chưa đẩy lên remote).
Quyết định đầu vào: CONDITIONAL GO cho tích hợp bản nháp, NO-GO cho công bố kết luận dụng thần chính thức. Phase 7 giữ đúng hai điều đó.

## 0. Kết luận (hai trục tách riêng)

| Trục | Đề xuất | Cơ sở |
|---|---|---|
| **Sẵn sàng kỹ thuật** của tích hợp bản nháp | **READY FOR REVIEW** | cờ mặc định tắt, phản hồi mặc định không đổi một byte (test so từng phản hồi); cờ bật chỉ thêm đúng một khóa; UI giữ mọi kết luận và mọi bất đồng trên 1.500 lá số; 1140 test qua trên cây sạch (baseline `main` 1119); merge sạch về văn bản với PR #1 và nhánh giao diện mới |
| **Xác minh học thuật** của kết luận dụng thần | **NO-GO (công bố)** | `empirical_validated = no` ở mọi phương pháp; không phương pháp nào `source_rule_verified = yes`; 0/120 ô và 0/10 ví dụ có người xác nhận; 9 ô sách tự mâu thuẫn chưa có quyết định học thuật; trong 10 ví dụ của sách chỉ 3 khớp hoàn toàn |
| Điều kiện để bật cho người dùng cuối | **BLOCKED** bởi mục 8 (quyết định sản phẩm và người kiểm), không bởi kỹ thuật | |

Không dòng nào trong báo cáo hay trong UI gọi dụng thần là chính xác, đã chứng minh hay đã được chuyên gia kiểm chứng.

## 1. Review Phase 6 (`0f7cd38`)
- Commit gồm đúng **15 file** (kiểm bằng `git show --name-only`): 6 tài liệu/phiếu trong `docs/`, 2 test và 2 golden trong `engine/tests/`, 4 công cụ trong `tools/` (+ báo cáo Phase 5 chỉnh một dòng). Không có `api.py`, `web/` hay `compare_deep`.
- JSON Schema `docs/bazi_deep_yongshen_contract.schema.json` được đối chiếu với dữ liệu thực: 500 đầu ra pipeline (test Phase 6) và 4+5 phản hồi API thật (test Phase 6 và Phase 7). Validator tự viết có test âm tính (bắt `empirical_validated="yes"`, thiếu `trace`, `no_final_answer=false`, mức xác minh lạ).
- Ba mức xác minh hiển thị độc lập; `empirical_validated` bị schema ép bằng `const "no"`. Việc oracle khớp hay test qua **không** nâng mức nào: các giá trị nằm trong `METHOD_META`, không do kết quả test sinh ra.
- Đã thêm vào hợp đồng (cộng thêm, vẫn tương thích): `group_names`, `status_labels`, `field_labels`, `states.draft_label`, `states.flag_off`, `states.review_status`.

## 2. Kiến trúc tích hợp

```
client ──POST /api/bazi-structure {…, "bazi_deep_draft": true|false|absent}──▶ api.py (StructureReq ⊂ BirthReq)
                                                                              │
                         pipeline.analyse(...)  ── không đổi, cùng kết quả ──┤
                                                                              ▼
                            flag off/absent:  trả nguyên kết quả pipeline
                            flag on        :  trả kết quả pipeline + khóa mới "bazi_deep_draft" = draft_view.envelope(...)
```
- `engine/tvbt/bazi_deep/draft_view.py` (mới): chỉ đóng gói nhãn, chuỗi bắt buộc, trạng thái kiểm độc lập và cờ mâu thuẫn **quanh** kết quả. Không đọc, xếp hạng, chấm điểm hay đổi kết luận của phương pháp nào.
- `engine/tvbt/api.py` (3 hunk nhỏ): lớp `StructureReq(BirthReq)` với `bazi_deep_draft: bool = False` (chỉ dùng ở `/api/bazi-structure`, không đụng `BirthReq` nên không chồng với PR #1); nhánh `if req.bazi_deep_draft`; route `/bazi-deep-draft` (chỉ để chạy local giống production, như `/library`).
- `/api/bazi-timeline` và mọi endpoint khác bỏ qua cờ (test).
- Trang UI độc lập `engine/web/bazi_deep_draft.html` + `engine/web/js/bazi_deep_draft.js`: **không sửa file nào có sẵn trong `web/`**, nên không xung đột với phiên đang làm giao diện. Production phục vụ nó như tài sản tĩnh từ thư mục `engine/web` (`wrangler.jsonc`); chưa deploy.

### Cách hiểu "mặc định giữ nguyên response hiện tại"
Phản hồi hiện tại của `/api/bazi-structure` trên `main` đã chứa các khóa mở rộng của Phase 4–6 (`meta`, `trace`...). Tôi giữ nguyên toàn bộ phản hồi đó khi không có cờ (và giữ cả `methods.cach_cuc_tvh.note` khi trạng thái là `khong_xac_dinh_noi_cach`), và đặt phần *trình bày* (nhãn, chuỗi, trạng thái kiểm) sau cờ. Nếu chủ sản phẩm muốn mặc định **cắt** các khóa mở rộng của Phase 4–6 khỏi phản hồi (một thay đổi phá tương thích theo hướng ngược lại), đó là quyết định riêng cần xác nhận, chưa làm.

### Phụ thuộc và quyền sở hữu
- Không sửa working tree của phiên khác; mọi thay đổi nằm trên nhánh riêng ở worktree riêng.
- `git merge-tree` giữa nhánh này với `zz-api-integration` (PR #1) và với `feat/observatory-result-pages` đều **không có xung đột văn bản**. Chưa chạy test trên kết quả merge; khi PR #1 được merge, cần chạy lại bộ test này.
- PR #1 sửa `BirthReq` và hai chỗ gọi `facts.bazi_facts`; nhánh này sửa `bazi_structure` và thêm route. Thứ tự merge không quan trọng về văn bản; về ngữ nghĩa PR #1 thêm cờ riêng (`bat_tu_direct`) và không chạm `bazi_structure`.
- Nếu muốn gắn nút vào giao diện chính, đó là việc của phiên sở hữu `web/`; hợp đồng và `BaziDeepDraft.render` đã sẵn sàng để gọi.

## 3. API contract và cờ
| Mục | Giá trị |
|---|---|
| Endpoint | `POST /api/bazi-structure` |
| Cờ | `bazi_deep_draft` (bool, mặc định `false`, bỏ qua nếu vắng) |
| Khi `true` | thêm khóa `bazi_deep_draft`: `contract_version` (`bazi-deep-draft/1`), `draft_label`, `banner`, `ui_strings`, `method_order`, `review_status`, `book_internal_conflict`, `contract_doc` |
| Không bao giờ có | khóa dụng thần cuối, điểm tổng, xếp hạng, người thắng (test quét toàn phản hồi) |
| Schema của `yongshen` | `docs/bazi_deep_yongshen_contract.schema.json` (không đổi hình dạng) |
| Chuỗi UI | `docs/bazi_deep_ui_strings_vi.json`, bản chạy thật `engine/data/bazi_deep/ui_strings_vi.json`; test ép hai bản **giống từng byte** |
| Trạng thái kiểm độc lập | `engine/data/bazi_deep/review_status.json`; test ép nó bằng đúng kết quả của hai công cụ intake trên phiếu thật (hiện 0/120 ô, 0/10 ví dụ) |

## 4. UI bản nháp (đã cài, độc lập)
Khi người dùng tích "Bật phân tích chuyên sâu (thử nghiệm)" (mặc định không tích) và bấm Xem, trang gọi API với cờ và hiển thị theo thứ tự:
1. **Nhãn cố định, dính đầu trang:** "Phân tích thử nghiệm – chưa được kiểm chứng thực nghiệm" (luôn là phần tử đầu tiên; test).
2. Banner bản nháp và dòng trạng thái kiểm: "Kiểm độc lập bảng điều hậu: 0/120 ô đã có người xác nhận."
3. **Trạng thái tổng theo hợp đồng**, tính ở trình duyệt: có bất đồng → "Các phương pháp không cho một kết luận thống nhất…"; chỉ đồng thuận → "đồng thuận không phải bằng chứng"; một phương pháp → câu tương ứng.
4. Khung **mâu thuẫn nội bộ sách** (khi ô điều hậu thuộc 9 ô) nêu can chỉ ở chú thích và can chỉ ở bảng, không bên nào được coi là đúng.
5. Khối **chỗ các phương pháp mâu thuẫn**: từng nhóm, phương pháp nào thuận, phương pháp nào bất lợi.
6. **Tám thẻ phương pháp theo thứ tự cố định của máy chủ** (không xếp theo độ tin cậy): tên, huy hiệu nguồn, trạng thái, Dụng/Hỷ/Kỵ riêng của phương pháp (hai cách đọc khi sát ngưỡng 40%, kèm ghi chú biên là của hệ thống), ba dòng mức xác minh tách riêng, lý do, điều kiện áp dụng, cơ sở khí thế, nguồn sách, và danh sách các bước suy luận.
7. Ghi chú cách ly trường phái.

Mọi chữ lấy từ dữ liệu được dựng bằng `textContent` (không `innerHTML`, `eval`; test quét mã).

## 5. Kiểm thử và regression
| Cây mã | Kết quả |
|---|---|
| `main` (`bb80ab1`) sạch, worktree riêng | 1119 passed, 1 skipped, 2 xfailed, 0 failed |
| nhánh `bazi-deep-draft-integration` (12 file Phase 7 trên `main`) | **1140 passed**, 1 skipped, 2 xfailed, 0 failed (+21 test Phase 7) |

Test Phase 7 (`engine/tests/test_bazi_deep_phase7.py`, kèm `engine/tests/js/phase7_viewmodel_check.js` chạy bằng `node`):
- **Cờ:** với 5 ngày sinh, phản hồi không cờ = phản hồi `false` (so bằng nhau); phản hồi `true` trừ khóa `bazi_deep_draft` = phản hồi mặc định, kể cả khi so chuỗi JSON đã sắp xếp khóa; timeline và endpoint khác bỏ qua cờ.
- **Hợp đồng:** schema qua phản hồi thật; chuỗi UI giống từng byte; khóa phong bì đúng tập hợp; không có khóa xếp hạng; không có cụm cấm.
- **UI trên 1.500 lá số thật** (qua pipeline, mỗi lá số mang phong bì): 0 vấn đề. Mỗi thẻ giữ nguyên Dụng/Hỷ/Kỵ của phương pháp, đúng 8 thẻ theo đúng thứ tự máy chủ, ba mức xác minh với `empirical_validated` hiển thị "Chưa có kiểm chứng…", không có cụm cấm trong view-model, DOM dựng ra chứa nhãn ở vị trí đầu, mọi bước suy luận, mọi mức. **≥ 1.000/1.500 lá số có bất đồng** (tương ứng 4.097/5.000 ở Phase 6) và với **từng** lá số như vậy trạng thái là "không có kết luận thống nhất", câu của hợp đồng được hiển thị và từng bất đồng được liệt kê; các cách đọc `hai_cach_doc` không bị mất. Cài đặt JS và cài đặt Python của quy tắc trạng thái cho cùng kết quả trên cả 1.500 lá số.
- **Cách ly trường phái và tương thích ngược:** các test Phase 5/6 (5.000 lá số hai chiều, schema, khóa phản hồi của `d0c3ab8`, không rò experimental) đều chạy lại và qua trên nhánh mới.
- **Nguồn:** xem mục 6.

**Không làm được:** kiểm tra bằng mắt trong trình duyệt (cửa sổ trình duyệt từ chối `file://` và máy không có `uvicorn` để chạy server cục bộ). Độ tin cậy của giao diện dựa vào kiểm thử DOM giả lập bằng node, chưa phải kiểm tra hình ảnh thật; cần một người mở `/bazi-deep-draft` trước khi review UI.

## 6. Kiểm chứng nguồn độc lập
**Nguồn gốc dữ liệu 10 ví dụ** (`tests/golden/tvh_dungthan_examples.json`, trường `pillar_provenance`, `readers`, `human_verified`):

| Ví dụ | Trang | Năm / Tháng / Ngày / Giờ | Người đọc | Người xác nhận |
|---|---|---|---|---|
| p387_intro, p387_vd1, p388_vd2/3/4 | 387–388 | đọc trực tiếp ×4 | mô hình + lượt chép mù | không |
| p397_vd1, p398_vd2, p399_vd3 | 397–399 | đọc trực tiếp ×4 | mô hình + lượt chép mù | không |
| **p400_vd4** | 399–400 | năm đọc trực tiếp · **tháng suy** · **ngày dựng lại** · giờ đọc trực tiếp | mô hình + lượt chép mù (dựng ra cùng bốn trụ) | không |
| **p401_vd5** | 400–401 | đọc trực tiếp ×4 | **một** người đọc, chưa có lượt chép mù | không |

- Ví dụ 4 **không** được tính là xác nhận hoàn toàn: công cụ `tools/bazi_deep_examples_review_intake.py` chỉ cho tháng và ngày của nó trạng thái `reconstructed_not_independent` (người đọc cùng trang vỡ đồng ý với phần dựng lại không phải là xác nhận dữ liệu gốc). Ví dụ 5 chỉ có một người đọc.
- **Phiếu chép mù** `docs/bazi_deep_examples_review_sheet.csv`: 40 dòng (10 ví dụ × 4 trụ), **không chứa giá trị nào của engine** (test kiểm không trụ nào xuất hiện trong phiếu). Người kiểm ghi trụ như in; công cụ so với dữ liệu vàng, báo từng trụ và từng ví dụ, không sửa gì, không nâng mức nào.
- **Chín ô sách tự mâu thuẫn** vào danh sách chờ quyết định học thuật (bảng dưới). Không ô nào được sửa; test khẳng định dữ liệu vẫn đúng 9 ô lệch tập can.

| # | Can ngày × tháng | Bảng (tr.389–390) | Chú thích (tr.391–396) | Loại | Phương án để người phụ trách học thuật chọn |
|---|---|---|---|---|---|
| 1 | Đinh × Thìn | Canh Giáp | Giáp Canh **Mậu** | chú thích thêm | (a) giữ bảng (hiện tại) (b) thêm Mậu (c) đánh dấu không dùng |
| 2 | Nhâm × Thìn | Canh Giáp | Giáp Canh **Bính** | chú thích thêm | như trên |
| 3 | Bính × Ngọ | **Quý** Nhâm | Nhâm **Canh** | thay thế | (a) bảng (b) chú thích (c) cả hai |
| 4 | Mậu × Ngọ | **Canh** Nhâm Bính | Nhâm **Giáp** Bính | thay thế | như trên |
| 5 | Quý × Ngọ | **Nhâm** Canh Quý | Canh **Tân** Quý | thay thế | như trên |
| 6 | Quý × Mùi | Tân Canh **Nhâm** Quý | Canh Tân Quý | bảng thêm | (a) giữ (b) bỏ Nhâm |
| 7 | Bính × Thân | **Quý** Nhâm | Nhâm **Mậu** | thay thế | (a) bảng (b) chú thích (c) cả hai |
| 8 | Tân × Thân | Giáp Nhâm **Canh** | Nhâm Giáp **Mậu** | thay thế | như trên |
| 9 | Tân × Dậu | Giáp Nhâm | Nhâm Giáp **Đinh** | chú thích thêm | (a) giữ bảng (b) thêm Đinh |

Can chủ (can đứng đầu chú thích) nằm trong bảng ở cả 9 ô, nên quyết định không làm đổi Dụng chính; chỉ đổi tập Hỷ.

## 7. Quy trình 120 ô và hiện trạng
- `tools/bazi_deep_tvh_review_intake.py` được kiểm bằng test: không import hay ghi `METHOD_META`, không `json.dump`, không `write_text`, không mở tệp để ghi; chạy nó trên phiếu đầy đủ **không** đổi byte nào của `tvh_dieuhau.json`; cùng một người điền hai lần chỉ tính một; chín ô mâu thuẫn giữ cờ dù người kiểm xác nhận.
- Bộ hướng dẫn: `docs/BAZI_DEEP_TVH_REVIEW_PROTOCOL.md`. Mỗi ô có nguồn (trang bảng, trang chú thích), kết luận (các can) và cột người xác nhận (`nguoi_kiem`) trong `docs/bazi_deep_tvh_cells_check.csv`.
- Test kiểm các phiếu thật đang **trống hoàn toàn** (không tạo người kiểm giả). **Hiện trạng: 0/120 ô và 0/10 ví dụ có người xác nhận**; `review_status.json` và UI hiển thị đúng con số này.

## 8. Blocker học thuật và checklist điều kiện phát hành
Blocker học thuật (không thể giải bằng kỹ thuật):
1. 0/120 ô, 0/10 ví dụ có người xác nhận độc lập.
2. 9 ô sách tự mâu thuẫn chưa có quyết định.
3. Tác giả không rõ nguồn bảng điều hậu (tr.388): không thể nâng `source_rule_verified`.
4. Không có nghiên cứu thực nghiệm: `empirical_validated` phải giữ `no`.
5. Ví dụ 4 có trụ dựng lại; ví dụ 5 một người đọc.
6. Ngưỡng của hệ thống (đúng 40%, biên ±0,03, các ngưỡng nhận diện) không có căn cứ nguồn.

Checklist phát hành:
- [x] Cờ mặc định tắt; phản hồi mặc định bằng nhau (test).
- [x] Cờ bật chỉ thêm một khóa, kết luận không đổi (test).
- [x] Hợp đồng/schema khớp dữ liệu thật; chuỗi UI giống từng byte.
- [x] UI giữ mọi kết luận và mọi bất đồng trên 1.500 lá số; nhãn thử nghiệm luôn nhìn thấy.
- [x] Không sửa file của phiên khác; merge văn bản sạch với PR #1 và nhánh giao diện mới.
- [ ] Người mở `/bazi-deep-draft` xem bằng mắt (chưa làm được ở đây).
- [ ] Chạy lại bộ test trên kết quả merge khi PR #1 và nhánh giao diện được merge.
- [ ] Quyết định sản phẩm: có cắt khóa mở rộng Phase 4–6 khỏi phản hồi mặc định hay không.
- [ ] Phiên sở hữu `web/` quyết định có gắn nút vào giao diện chính hay giữ trang độc lập.
- [ ] Người kiểm ≥ 1 (tốt nhất 2) cho 120 ô và 10 ví dụ; `review_status.json` chỉ được cập nhật theo kết quả công cụ.
- [ ] Quyết định học thuật cho 9 ô.
- [ ] Review của người có chuyên môn Bát Tự về cách trình bày bất đồng và nhãn (không phải kiểm chứng kết luận).
- [ ] Không bật mặc định; không deploy cho tới khi các mục trên được duyệt.
