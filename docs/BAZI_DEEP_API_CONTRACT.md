# Hợp đồng API/UI đề xuất cho khối `yongshen` của Bát Tự sâu

**Trạng thái:** đề xuất, chưa gắn vào `api.py` hay `web/` (hai nơi này do phiên khác sở hữu). Hợp đồng là *cộng thêm*: không khóa cũ nào bị bỏ (test `test_every_response_key_of_d0c3ab8_still_exists_additive_only`).

Tệp đi kèm:
- `docs/bazi_deep_yongshen_contract.schema.json`: JSON Schema của `response.yongshen`. Test kiểm 500 lá số qua pipeline và 4 phản hồi API thật.
- `docs/bazi_deep_ui_strings_vi.json`: chuỗi bắt buộc cho UI, gồm nhãn của ba mức xác minh và các câu trạng thái. Test kiểm mọi giá trị enum đều có nhãn và không nhãn nào nói "đã chứng minh".

## 1. Nơi dữ liệu nằm
| UI cần | Đường dẫn trong phản hồi `/api/bazi-structure` |
|---|---|
| danh sách phương pháp (8) | `yongshen.methods.{phu_uc,dieu_hau,cach_cuc,cach_cuc_tvh,thong_quan,thuan_the,thuan_the_tvh,khuyet_hanh}` |
| kết luận riêng của phương pháp | `.status`, `.yong`, `.xi`, `.ji` (nhóm thập thần), `.alternatives` khi `status = hai_cach_doc` |
| ba mức xác minh | `.meta.levels.{transcription_verified, source_rule_verified, empirical_validated, why}` |
| nguồn, điều kiện áp dụng, cơ sở khí thế | `.meta.source[]`, `.meta.applies_when`, `.meta.strength_basis`, `.meta.applied` |
| các bước suy luận | `.trace[]` (chuỗi, ổn định giữa các lần chạy) |
| mâu thuẫn nội bộ sách (điều hậu) | `methods.dieu_hau.table.book_internal_conflict` (`null` hoặc `{note_only[], table_only[]}`) |
| ngưỡng 40% | `methods.cach_cuc_tvh.threshold.{rule, rule_src, own_share, book_rule_reading, near_threshold, margin_heuristic, margin_src, equality_choice}` |
| bất đồng giữa phương pháp | `yongshen.comparison.disagreements[]` (`group`, `favourable_in[]`, `unfavourable_in[]`) |
| đồng thuận | `yongshen.comparison.consensus[]` |
| điều kiện áp dụng từng phương pháp | `yongshen.comparison.methods.{tên}.{applied, verification, applies_when, strength_basis}` |
| nguồn của từng phía | `yongshen.isolation.{system_school_computed_from, tvh_school, note}` |
| khóa cấm | `comparison.no_final_answer` luôn `true`; không có khóa dụng thần cuối, điểm tổng hay người thắng |

## 2. Ba mức xác minh (hiển thị riêng, không gộp)
`transcription_verified`: chép đúng bảng/văn bản nguồn. `source_rule_verified`: công thức và ngưỡng khớp điều nguồn nói. `empirical_validated`: có bằng chứng độc lập về giá trị dự báo.
- Ba nhãn luôn hiện cùng nhau, mỗi nhãn một dòng, bằng chuỗi trong `ui_strings.level_values`.
- `empirical_validated` luôn là `no` (schema ép bằng `const`). UI luôn hiện *"Chưa có kiểm chứng thực nghiệm về giá trị dự báo"* cho mọi phương pháp.
- Không suy mức này từ mức khác: một phương pháp `transcription_verified = yes` vẫn có thể `source_rule_verified = no`.
- **Cấm** dùng các từ trong `forbidden_phrases` (đã chứng minh, chính xác, chắc chắn, kết luận cuối...). Khớp sách chỉ có nghĩa là bản cài khớp với trang in.

## 3. Trạng thái tổng và quy tắc hiển thị
UI tính trạng thái bằng quy tắc sau (không có trường server cho nó, để server không bao giờ "chọn"):
1. `comparison.disagreements` không rỗng → hiện `states.no_unified_conclusion`, rồi từng phương pháp xếp song song (không sắp theo "độ tin cậy").
2. Không bất đồng, ≥ 2 phương pháp `meta.applied` và `comparison.consensus` không rỗng → hiện `states.agreement_not_proof` kèm nhóm đồng thuận.
3. Đúng 1 phương pháp áp dụng → `states.single_method`.
4. Không phương pháp nào áp dụng → `states.no_unified_conclusion`.
Trên 1.500 lá số mẫu, trạng thái 1 và 2 đều xuất hiện (trạng thái 1 là phổ biến nhất): UI phải thiết kế cho bất đồng là trường hợp bình thường.

## 4. Các phần tử bắt buộc
- **Thẻ phương pháp:** tên (`method_titles`), huy hiệu (`verification_badges`), ba dòng mức xác minh, `applies_when`, `strength_basis`, kết luận riêng, nút mở `trace`.
- **`hai_cach_doc`:** hiện cả hai cách đọc (`alternatives`), cờ `follows_book_rule` đánh dấu cách đọc theo quy tắc 40%, và `states.two_readings`. Ghi `threshold.margin_src` (biên là của hệ thống).
- **`book_internal_conflict` khác `null`:** hiện `states.book_internal_conflict`, liệt kê can chỉ có ở chú thích và can chỉ có ở bảng; không đánh dấu bên nào là đúng.
- **Banner:** `states.draft_banner` luôn hiện ở đầu khối.
- **Ví dụ của sách (nếu hiển thị trong trang trợ giúp):** dữ liệu `reconstructed` phải kèm `states.reconstructed_example`.

## 5. Tương thích và quyền sở hữu
- Chỉ thêm khóa: `meta`, `trace`, `isolation`, `threshold`, `table.book_internal_conflict`, `comparison.methods`, `comparison.no_final_answer`, hai phương pháp mới. Người dùng cũ không đọc các khóa này vẫn nguyên vẹn.
- Một khóa chỉ có ở một số trạng thái (`methods.*.note`) có thể biến mất tùy lá số: UI không được dựa vào nó.
- `yong_health` / `xi_health` (hiện diện của nhóm trong lá số) dùng lớp tương tác chung của hai trường phái; `season_factor` và `class_weight` đổi lớp này, nên chúng là chú thích hiện diện chứ không phải kết luận của phương pháp.
- `api.py` và `web/` chưa được chạm. Việc gắn hợp đồng vào API/UI thuộc phiên sở hữu hai nơi đó; cần phối hợp với PR #1 (zz-api-integration) đang đề xuất sửa `api.py`.
