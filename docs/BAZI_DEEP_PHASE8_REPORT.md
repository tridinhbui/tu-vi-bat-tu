# Phase 8: QA tích hợp cuối và chuẩn bị PR (Bát Tự sâu, bản nháp)

Nhánh `bazi-deep-draft-integration` (worktree ổn định `../tuvibattu-bazi-draft`). Cờ `bazi_deep_draft` **mặc định tắt**. Không merge, không deploy, không công bố kết luận dụng thần đã được kiểm chứng.

## 0. Khuyến nghị phát hành (hai trục tách riêng)
| Trục | Kết luận |
|---|---|
| Sẵn sàng kỹ thuật của tích hợp bản nháp | **PASS có điều kiện** → mở **Draft PR** được. Hai việc kỹ thuật chưa làm được ở máy này: `wrangler deploy --dry-run` (cần Docker, chưa cài) và chạy lại bộ test sau khi các PR khác thực sự được merge |
| Xác minh học thuật | **BLOCKED**: 0/120 ô và 0/10 ví dụ có người xác nhận; 9 ô sách tự mâu thuẫn chưa có quyết định; không có kiểm chứng thực nghiệm |
| Chuyển PR sang Ready for review | **Không**: còn blocker bắt buộc (mục 8) |

## 1. Audit hai commit so với `main` — PASS
`git diff main..d30a908`/`f6a2e25` (Phase 7): 13 file, 1.078 dòng thêm, 21 xóa. Phạm vi đúng như đã khai: `api.py` (lớp `StructureReq`, một nhánh `if`, một route), `bazi_deep/draft_view.py` mới, trang `web/bazi_deep_draft.html` + `web/js/bazi_deep_draft.js` mới, chuỗi UI, trạng thái kiểm, hai công cụ intake, golden. Không file có sẵn trong `web/` bị sửa; không `compare_deep`. Hợp đồng, cờ mặc định tắt và bằng chứng nguồn khớp mô tả trong `BAZI_DEEP_PHASE7_INTEGRATION.md`; test cờ (so từng phản hồi) vẫn qua.

## 2. Khởi chạy và kiểm tra trình duyệt thật — PASS sau khi sửa
Chạy bằng `uvicorn` của virtualenv dự án (`.venv`, đã có sẵn; không cài thêm gì) từ worktree của nhánh, cổng cục bộ; trình duyệt tích hợp của ứng dụng; desktop, 768 và 375 px. **Đây là kiểm tra trình duyệt thật, không phải DOM giả lập**; ảnh chụp nằm trong lịch sử phiên, không được commit.

Lỗi tìm thấy khi duyệt bằng mắt (trước khi sửa):
| # | Lỗi | Mức | Trạng thái |
|---|---|---|---|
| 1 | Ô năm/tháng/ngày/giờ rộng quá hẹp, số bị cắt ("199") trên desktop | P1 | FIXED |
| 2 | Nhãn "Phân tích thử nghiệm – chưa được kiểm chứng thực nghiệm" không hiện ở trạng thái tắt, đang tải, lỗi (chỉ hiện ở kết quả) | P1 | FIXED (nhãn có trong **mọi** trạng thái) |
| 3 | Lỗi hiện thô "HTTP 422"; không kiểm tra dữ liệu thiếu hoặc ngày không có thật (31/2) | P1 | FIXED (kiểm tra phía trình duyệt + thông điệp tiếng Việt) |
| 4 | Câu "Nhật Chủ nằm sát ngưỡng 40%" gắn vào `phu_uc`, vốn không dùng ngưỡng 40% (gây hiểu sai) | P1 | FIXED (chỉ phương pháp có ngưỡng 40% mới có câu này) |
| 5 | Mã nội bộ hiện cho người đọc: `he_thong`, `tvh_40`, `SRC_…`, `war_share`, `QuanSat`, `khong_chan`, tên `cach_cuc_tvh` trong ghi chú cách ly | P1 | FIXED (lớp đổi sang tiếng Việt; test quét 1.500 lá số: 0 mã nội bộ lọt ra) |
| 6 | Câu mâu thuẫn nội bộ viết nhầm "Chính sách này…" (phải là "Sách này…") | P1 (nội dung) | FIXED |
| 7 | Không có chỉ báo "chưa đủ bằng chứng" trên từng thẻ phương pháp | P2 | FIXED (huy hiệu "Chưa đủ bằng chứng thực nghiệm" trên cả 8 thẻ) |
| 8 | Bấm Xem liên tiếp có thể chồng yêu cầu | P2 | FIXED (khóa nút khi đang tính, bỏ qua phản hồi cũ) |

Kiểm tra sau sửa (chạy kịch bản trong trang): trạng thái tắt, thiếu dữ liệu, 31/2, năm 1800, giờ 24, mất mạng, máy chủ 503, máy chủ 422, đang tải (nút bị khóa, `aria-busy`), kết quả (8 thẻ), tắt lại. **Nhãn là phần tử đầu tiên ở cả 11 trạng thái**, thông điệp lỗi có `role="alert"`. Kết quả cho lá số 13/4/1985 (một ô điều hậu mâu thuẫn sách, hai cách đọc): hiện đủ nhãn, thông điệp "không có kết luận thống nhất", khung mâu thuẫn nội bộ, khối chỗ các phương pháp mâu thuẫn, tám thẻ đủ ba mức xác minh, bước suy luận, nguồn. Không tràn ngang ở 375 và 768 px; nhãn dính đầu trang khi cuộn; chữ không nhỏ hơn 11 px; console không lỗi.

## 3. Trải nghiệm đầy đủ
| Kịch bản | Kết quả |
|---|---|
| Nhập ngày sinh hợp lệ, bật chế độ | PASS |
| Chế độ tắt (mặc định) | PASS: chỉ hiện nhãn và lời giải thích; không gọi API |
| Dữ liệu thiếu / không có thật / ngoài khoảng | PASS: thông điệp rõ, không gọi API |
| Đang tải | PASS: nút khóa, `aria-busy`, nhãn vẫn hiện |
| Lỗi máy chủ 4xx/5xx / mất mạng | PASS: ba thông điệp riêng |
| Phương pháp bất đồng | PASS: câu của hợp đồng + danh sách từng bất đồng (≥ 1.000/1.500 lá số mẫu có bất đồng) |
| Sát ngưỡng 40% | PASS: hai cách đọc, ghi chú biên là của hệ thống |
| Ô sách tự mâu thuẫn | PASS: khung riêng, không chọn bên nào |
| Nguồn và mức xác minh | PASS: ba mức riêng, `empirical_validated` luôn "Chưa có kiểm chứng…" |
| **Thiếu giờ sinh** | **Giới hạn đã biết (không phải lỗi mới)**: engine cần cả giờ; trang nói rõ "cần cả giờ sinh" |

## 4. Kết hợp thực tế với PR #1 và nhánh giao diện mới nhất — PASS
Worktree tích hợp **riêng và tạm** (`integ/phase8-check`, không đẩy lên remote) tạo từ nhánh này, rồi `git merge` thật `zz-api-integration` (PR #1, `1ef0feb`) và `feat/observatory-result-pages` (`be7e63e`). Cả hai merge tự động, kể cả `api.py` (hunk của PR #1 và của nhánh này không chạm nhau).
| Kiểm tra trên kết quả tích hợp | Kết quả |
|---|---|
| Toàn bộ test | **1173 passed**, 2 xfailed, 0 failed |
| Server từ kết quả tích hợp: `/bazi-deep-draft`, `/`, `/library` | 200, 200, 200 |
| `/api/bazi-structure` với `bazi_deep_draft` và `bat_tu_direct` cùng bật | trả về bình thường, có khối `bazi_deep_draft` |
| Trang nháp trong trình duyệt trên kết quả tích hợp | 8 thẻ, nhãn, khung mâu thuẫn, console sạch |
| `tsc --noEmit` (Worker) | không lỗi |
| `wrangler deploy --dry-run` | **BLOCKED**: cần Docker (chưa cài); không deploy |
Nhánh riêng của nhánh này: 1144 passed, 1 skipped, 2 xfailed, 0 failed.

## 5. Audit độc lập quy tắc dụng thần, mâu thuẫn và 120 ô
- **Bảng dụng thần tr.378–386 (mới)**: một lượt chép mù (tác tử khác, chỉ nhìn ảnh trang) đối chiếu với `tvh_dungthan.json`: so được 104 trường, 100 khớp ngay. Phát hiện **bốn chỗ chép sai của chính engine** (ba thứ tự in, một dụng thần), đối chiếu lại với ảnh trang và **đã sửa**:
  1. Chính tài, nhược, Quan Sát nhiều: dụng thần đúng thứ tự in là Tỉ Kiếp rồi Ấn (engine cũ: Ấn rồi Tỉ Kiếp). **Đổi dụng thần chính** của dòng này.
  2. Thiên/Chính Ấn, vượng, Ấn nhiều: vận tốt Thực Thương rồi Tài.
  3. Thất Sát, nhược, Tài nhiều: vận xấu Thực Thương rồi Tài.
  4. Kiến lộc, vượng, Quan Sát nhiều: dụng thần là Tài (tr.386 "lấy tài tinh"); engine cũ có thêm Thực Thương.
  Một lỗi đọc của lượt chép mù (Chính quan, nhược, Thực Thương nhiều) được đối chiếu và bác bỏ. Test cũ của chính tôi đã mã hóa cùng một thứ tự sai (oracle không độc lập): đã sửa và thay bằng test so với bản chép mù.
- **Một dòng có dụng thần do hệ thống suy ra** (Kiến lộc, vượng, Thực Thương nhiều): tr.386 không nêu dụng thần; dòng được đánh dấu `yong_inferred`, và kết quả/trace nói rõ.
- **Chưa so được bằng lượt mù**: 14 dòng Kiến lộc/Kình dương ở tr.386 (sách không ghi vượng/nhược hoặc nhóm nhiều nhất cho một số dòng); tôi đối chiếu chúng bằng tay với ảnh trang và không thấy lệch, nhưng đó là một người đọc.
- **120 ô điều hậu**: giữ nguyên hai lượt chép (một mù) khớp 120/120 bảng; chín ô sách tự mâu thuẫn **không đổi**, vẫn trong danh sách chờ quyết định học thuật (`BAZI_DEEP_PHASE7_INTEGRATION.md` mục 6). Hiện trạng người xác nhận: **0/120 ô, 0/10 ví dụ** (`review_status.json` được test ép bằng hai công cụ intake).
- **Không có mục nào được đánh dấu validated.** Bốn chỗ sửa ở trên là bằng chứng rằng các nhãn `transcription_verified` trước đó, dựa trên một người đọc, chưa đủ; vì vậy chúng vẫn ghi "chưa có người kiểm độc lập".

## 6. Sửa lỗi P0/P1 và kiểm thử lại
P0: không có. P1: sáu lỗi UX/nội dung ở mục 2 và bốn dòng dữ liệu ở mục 5, đều đã sửa. Test mới (Phase 7 mở rộng): thông điệp trang bằng chuỗi UI, nhãn có trong mọi trạng thái tĩnh, không có mã nội bộ lọt ra trên 1.500 lá số, chip "chưa đủ bằng chứng" trên mọi thẻ, câu 40% chỉ ở phương pháp có ngưỡng, nhãn nguồn cho mọi `SRC_`, bảng dụng thần đối chiếu bản chép mù, bốn dòng đã sửa và dòng suy ra. Bộ test của nhánh: 1144 passed. Build: không có bước build front-end (tài sản tĩnh); `tsc` sạch; `wrangler --dry-run` bị chặn bởi Docker.

## 7. Push và Draft PR
Xem phần kết của báo cáo trong mô tả PR. Lưu ý quan trọng: `origin/main` đang ở `87a7274`, còn nhánh này nằm trên `main` cục bộ, nên PR chứa **13 commit**, gồm 10 commit đã có trên `main` cục bộ nhưng chưa từng được đẩy (Phase 4–6 của Bát Tự sâu và các commit của phiên khác); PR này chỉ mới là **Draft**.

## 8. Blocker còn lại trước khi Ready
1. 0/120 ô, 0/10 ví dụ có người kiểm; ví dụ 4 có trụ dựng lại, ví dụ 5 một người đọc.
2. Quyết định học thuật cho 9 ô sách tự mâu thuẫn.
3. Không có kiểm chứng thực nghiệm (`empirical_validated = no`).
4. Người kiểm tra giao diện bằng mắt trên thiết bị thật và người có chuyên môn Bát Tự xem cách trình bày bất đồng.
5. Quyết định sản phẩm: giữ trang độc lập hay gắn vào giao diện chính; có cắt khóa mở rộng Phase 4–6 khỏi phản hồi mặc định hay không.
6. `wrangler deploy --dry-run` trên máy có Docker; chạy lại bộ test sau khi PR #1 và nhánh giao diện thực sự được merge.
7. Bốn dòng dữ liệu vừa sửa và dòng `yong_inferred` cần người đọc lại ảnh trang.
