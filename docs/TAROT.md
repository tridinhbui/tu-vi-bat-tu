# Tarot, bậc 1

Trang `/tarot/` cho rút một hoặc ba lá từ bộ 78 lá Waite–Smith (1909). Bậc này làm phần rút bài, trang lá bài và ảnh lá bài. **Chưa có ý nghĩa lá bài**: ý nghĩa chỉ được đăng khi có câu sách và trang sách (A. E. Waite, *The Pictorial Key to the Tarot*, 1911), mà sách này chưa có trên máy.

API nằm sau biến `TVBT_TAROT`, mặc định `"0"`. Khi tắt, mọi đường dẫn Tarot trả 404. **Các trang tĩnh thì lên ngay khi gộp nhánh**: mục "Tarot" trên thanh điều hướng, `/tarot/`, `/tarot/la-bai/` và 78 trang lá bài. Lúc API còn tắt, bấm "Xáo bài" sẽ hiện: "Phần rút bài chưa mở trên máy chủ".

## Đã làm

| Phần | Tệp |
|---|---|
| Bộ bài: 78 lá (22 Ẩn Chính, 56 Ẩn Phụ), gồm mã, slug, tên tiếng Anh, tên tiếng Việt, số và chất. Chỉ có tên, không có nghĩa. Strength là VIII, Justice là XI, như bộ 1909. | `engine/data/tarot/deck.json`, `src/tarot/deck.ts` |
| Rút bài: hạt giống 128 bit lấy từ `crypto.getRandomValues`, xáo Fisher–Yates bằng dòng số SHA-256 theo bộ đếm (`SHA-256(hạt ‖ bộ đếm 4 byte)`), lấy mẫu loại bỏ (rejection sampling) nên mọi thứ tự đều có xác suất như nhau. Cùng hạt giống cho cùng kết quả. Bit lá ngược được rút sau thứ tự, nên tắt lá ngược không làm đổi chỗ lá nào. | `src/tarot/draw.ts` |
| Hai cách bày: 1 lá và 3 lá. Ba vị trí chỉ là cách bày, không gắn nghĩa quá khứ / hiện tại / tương lai, vì Waite không định nghĩa như vậy. Chưa có Celtic Cross. | `src/tarot/draw.ts`, `route.ts` |
| Ý nghĩa: chỉ lấy từ pack có nguồn. Pack hiện **rỗng**. Lá chưa có mục trong pack thì hiện tên lá và một câu trung tính: "Ý nghĩa của lá này đang được chuẩn bị từ sách nguồn…" | `src/tarot/reading.ts`, `engine/data/tarot/pack_tarot_pkt.json`, `tools/build_tarot_pack.py`, `tools/data/tarot_pkt_entries.json` |
| Kiểm lời: danh sách từ cấm `BANNED` chuyển sang `src/interpret/wording.ts` (validate.ts import lại, hành vi giữ nguyên). Câu hỏi về sức khỏe, thai sản, tính mạng, pháp lý, đầu tư được nhận ra bằng regex (gõ có dấu hay không dấu đều được) và hiện lời khuyên hỏi người có chuyên môn. Trang nào cũng có dòng "Tarot là công cụ để suy ngẫm, không phải lời dự báo." | `src/tarot/guard.ts` |
| API: `POST /api/tarot/draw` (bước 1 xáo bài: trả mã lượt và số lá trong dãy úp; bước 2 gửi vị trí đã chọn: trả các lá), `GET /api/tarot/x/<id>` (lượt đã lưu, dùng cho liên kết chia sẻ), `GET/POST/DELETE /api/me/tarot` (các lượt đã lưu trong tài khoản). Thứ tự bài và hạt giống không bao giờ rời máy chủ. Miễn phí 3 lượt xáo mỗi ngày theo giờ Việt Nam, tính theo tài khoản, hoặc theo địa chỉ IP (đã băm) với khách. | `src/tarot/route.ts`, gắn trong `src/index.ts` trước các route `/api/me/*` và trước lệnh chuyển sang container |
| Câu hỏi: được gửi kèm lúc lật bài chỉ để nhận ra chủ đề nhạy cảm, rồi bỏ đi. Chỉ được lưu khi người dùng đăng nhập, bấm Lưu và chọn "Lưu cả câu hỏi". Liên kết chia sẻ mặc định ẩn câu hỏi. "Xóa dữ liệu" của tài khoản cũng xóa các lượt Tarot. | `route.ts`, `src/account/route.ts` |
| Cơ sở dữ liệu: bảng `tarot_draws` và `tarot_daily`. Lượt chưa lưu bị xóa sau 2 ngày. Lượt xáo chưa lật thì hết hạn sau 1 giờ. | `migrations/app/0011_tarot.sql` (đã viết, **chưa áp dụng lên máy chủ**). Route cũng tự tạo bảng khi dùng lần đầu, như `account/route.ts` |
| Trang web: dãy 78 lá úp để chọn, mặt bài bằng ảnh hoặc bằng chữ, lá ngược quay 180°, lưu và chia sẻ, lịch sử. Khách: kết quả chỉ nằm trong localStorage của trình duyệt. Trang Tarot không nạp nút chat. | `engine/web/js/tarot.js`, `engine/web/css/tarot.css`; trang tạo bởi `engine/tvbt/sitegen.py` (`tarot_pages`), chạy lại bằng `tools/build_site.py` |
| Trang tĩnh: `/tarot/`, `/tarot/la-bai/` và 78 trang `/tarot/la-bai/<slug>/` (tên, số, nhóm, nguồn ảnh, câu trung tính về ý nghĩa). Có trong sitemap. "Tarot" được thêm vào NAV và chân trang. | `engine/web/tarot/…` |
| Ảnh lá bài: chủ nhà duyệt ngày 2026-10-25. Lấy cả 78 tệp trong thể loại Commons "Rider-Waite-Smith tarot deck (TaionWC)", tức bản in "Pam-A" của tranh gốc Pamela Colman Smith (không phải Universal Waite, Radiant hay bản vẽ lại của US Games năm 1971). Với từng tệp, công cụ đọc mục giấy phép của trang. Cả 78 trang đều ghi `{{PD-old-auto-expired|deathyear=1942}}` và Commons báo "Public domain". SHA-1 của tệp tải về khớp với SHA-1 Commons công bố. Mỗi lá có hai bản WebP, rộng 300 px và 600 px (tổng khoảng 15 MB). Ảnh không nằm trong danh sách tải trước của service worker. | `tools/fetch_tarot_images.py`, `engine/data/tarot/images.json`, `engine/web/tarot/img/` |

**Lá bị bỏ qua vì giấy phép: không có** (0/78). Nếu một trang tệp đổi giấy phép, chạy lại công cụ: lá đó sẽ sang mục `skipped` và trang tự dùng mặt bài bằng chữ.

Ghi chú về ảnh: trang Commons ghi ngày 1910 cho bản in Pam-A; tranh là của bộ 1909. Phần mô tả trên Commons có tên thương mại của bộ bài, nên `images.json` không chép phần mô tả, chỉ ghi `"printing": "Pam-A"`. Giao diện chỉ dùng tên "bộ Waite–Smith (1909)".

## Kiểm thử

- `npm run test:tarot`, gồm `src/tarot/test/`:
  - `draw.test.ts`: cùng hạt giống cho cùng kết quả; phân bố gần đều (chi bình phương, 3.120 lần xáo); công tắc lá ngược; dòng SHA-256 khớp đặc tả.
  - `route.test.ts`: chạy trên D1 cục bộ. Kiểm công tắc TVBT_TAROT, giới hạn 3 lượt mỗi ngày, hạt giống không lộ ra ngoài, câu hỏi không bị lưu, chia sẻ ẩn câu hỏi, chỉ chủ lượt mới xóa được, migration khớp với schema của route.
  - `content.test.ts`: không có từ cấm; không có chữ "AI" và không có tên thương mại trong các tệp giao diện Tarot; mọi trang có dòng suy ngẫm; giấy phép và SHA-256 của ảnh; nhận diện chủ đề nhạy cảm.
- `engine/tests/test_tarot_pack.py`: pack đúng với tệp nguồn, mục sai bị từ chối, câu trích nằm đúng trang (bỏ qua khi chưa có PDF).
- `engine/tests/test_sitegen.py`: các trang đã commit khớp với bản generator tạo ra (gồm cả trang Tarot).

## Việc chờ chủ nhà

1. **Sách nguồn.** Đặt PDF *The Pictorial Key to the Tarot* (1911) vào `~/Downloads` với một trong các tên trong `PDF_NAMES` của `tools/build_tarot_pack.py`, hoặc đặt biến `TVBT_BOOKS_DIR`. Sau đó:
   - Đo độ lệch trang (trang PDF = trang in + `pdf_offset`) rồi ghi vào `tools/data/tarot_pkt_entries.json`.
   - Chép từng câu "Divinatory Meanings" (xuôi và ngược) cùng trang in và bản tiếng Việt chỉ của đúng câu đó.
   - Chạy `.venv/bin/python tools/build_tarot_pack.py`, rồi `.venv/bin/python tools/build_site.py`.
   - Bộ build sẽ dừng nếu câu trích không nằm đúng trang hoặc bản tiếng Việt dùng từ cấm.
2. **Bật API.** Áp dụng migration trước: `npx wrangler d1 migrations apply tvbt-app --remote` (để chủ nhà chạy). Sau đó đặt `"TVBT_TAROT": "1"` trong `wrangler.jsonc`.
3. **Trang tĩnh lên trước API.** Mục "Tarot" trên thanh điều hướng sẽ hiện ngay khi gộp nhánh, dù API còn tắt. Nếu muốn ẩn đến khi bật API, bỏ `("/tarot/", "Tarot")` khỏi `NAV` và khỏi chân trang trong `sitegen.py`, rồi build lại.

## Câu hỏi còn mở

- **Lỗi có sẵn trong `BANNED`.** `\b` của JavaScript chỉ hiểu chữ ASCII. Vì vậy các mẫu bắt đầu hoặc kết thúc bằng chữ có dấu không bao giờ khớp trong `validate.ts`: "định mệnh", "sẽ bị", "nhất định sẽ". Tarot dùng `BANNED_WORDS` (cùng danh sách, ranh giới từ hiểu chữ có dấu). Bộ kiểm chương Tử Vi / Bát Tự vẫn dùng `BANNED` như cũ: đổi sang bản đúng có thể làm thêm chương bị đánh lỗi, nên đó là quyết định của chủ nhà.
- **Tên tiếng Việt của lá bài** là tên thông dụng do hệ thống đặt, không phải bản dịch của sách. Ví dụ: Death → "Tử Thần" (tránh từ cấm "chết"), Page → "Tiểu Đồng", Pentacles → "Tiền". Chủ nhà có muốn đổi tên nào không?
- **Slug của trang lá bài** theo tên tiếng Anh (`/tarot/la-bai/the-fool/`), cho ổn định và dễ tìm. Có cần slug tiếng Việt không?
- **Cách đếm lượt miễn phí**: lượt được tính lúc xáo bài, không phải lúc lật bài. Lượt đã xáo mà bỏ dở vẫn bị tính.
- **Khách chưa đăng nhập dùng chung một mạng** (cùng IP, ví dụ quán cà phê) thì dùng chung 3 lượt mỗi ngày.
