# Container capacity & performance review

Trạng thái: **bản rút gọn**. Phiên làm việc dừng vì hết hạn mức sử dụng trước khi chạy xong vòng benchmark thứ hai. Mọi số liệu dưới đây đã đo thật (local, có mô phỏng CPU của Cloudflare); mục "Chưa làm" ghi rõ những gì còn thiếu. Không stress test production thêm, không đổi cấu hình, không deploy.

## 1. Cấu hình hiện tại (đã đọc từ file + tài liệu Cloudflare)

| Hạng mục | Hiện tại | Hệ quả |
|---|---|---|
| Instance type | không khai báo → mặc định **`lite`: 1/16 vCPU, 256 MiB** | CPU chỉ bằng 6,25% một lõi |
| Số instance thực dùng | `src/index.ts` luôn gọi `getContainer(env.TVBT, "main")` → **đúng 1 instance** | `max_instances: 3` không bao giờ được dùng |
| Autoscaling | Cloudflare **chưa có** autoscaling cho container; mở rộng bằng `getRandom(env, N)` (N cố định) | muốn nhiều instance phải đổi code Worker |
| Tiến trình | 1 worker `uvicorn`, endpoint đồng bộ (GIL) | tối đa 1 lõi dù instance lớn hơn |
| `sleepAfter` | 10 phút; cold start 1–3 giây (tài liệu) | |
| Keep-alive | mặc định uvicorn 5 giây | xem nguyên nhân 3 |

## 2. Nguyên nhân (có bằng chứng)

**1. CPU là nút cổ chai (nguyên nhân chính).** Một phiên lập lá số tốn ~0,16–0,17 giây CPU (đo local): `/api/rules` 75 ms (47%), `/api/reasoning` 74 ms (46%), phần còn lại ~10 ms. Trên `lite` (1/16 vCPU) việc đó mất ~2,5 giây thực. Kiểm chứng mô hình: local mô phỏng `lite` cho `reasoning` 2,47 s, production đo được 2,65 s (đã gồm ~0,4 s mạng). Sức chứa `lite`: **~23 phiên/phút**. 14 phiên cùng lúc cần ~36 giây CPU → đúng hiện tượng timeout 30 giây đã gặp (đo: p50 51,5 s, 14/14 phiên quá 30 s).

**2. Công việc thừa trong mỗi phiên.**
- Mỗi lần mở trang đều tải `/api/rules` (1,14 MB) và `/api/claims` (230 KB) chỉ để lấy tên nguồn và cụm tiếng Việt, kể cả người không lập lá số. `/api/claims` chỉ đọc lại file `claims_vi.json`.
- `_compute` (chuẩn hóa + Bát Tự + Tử Vi) chạy lại ở mỗi endpoint của cùng một phiên.
- `/api/reasoning` đọc và kiểm tra lại toàn bộ rule packs ở mỗi request (~25 ms trên ~140 ms khi profile), dù dữ liệu chỉ đổi khi deploy. 70% còn lại nằm trong `engine.run` (87.000 lần `evaluate` mỗi request).
- Trang kết quả gọi `/api/year` 4 lần cho cùng một lá số và cùng một năm.

**3. Ngắt kết nối khi quá tải (giả thuyết mạnh, chưa chứng minh ở Cloudflare).** Khi tiến trình bão hòa CPU, kết nối keep-alive bị uvicorn đóng sau 5 giây. A/B local ở `lite`, 8 phiên: mặc định 6/12 lần chạy có `ECONNRESET`/socket lỗi; với `--timeout-keep-alive 75`: **0/8** (Fisher p≈0,02). Đây là cùng loại lỗi "connection lost" như `Container suddenly disconnected` trên production, nhưng chưa thể xác nhận ánh xạ 1-1 vì không có proxy Cloudflare ở local. Cần xem log/metrics của Containers dashboard.

**4. Bộ nhớ không phải nguyên nhân ở mức tải đã đo.** Bản hiện tại: RSS ~64 MB nhàn rỗi, tăng ~6 MB mỗi phiên đồng thời (170 MB ở 14 phiên, 186 MB ở 20 phiên, so với 256 MiB). Ngoại suy vượt giới hạn ở ~30 phiên đồng thời. Bản tối ưu giữ ~65–80 MB, không tăng theo tải.

Giới hạn của phép đo: máy dev dùng chung với các phiên khác nên có nhiễu (lần lặp `lite`, N=8 cho p50 từ 20 đến 37 s); mô phỏng CPU bằng SIGSTOP/SIGCONT chu kỳ 100 ms xấp xỉ quota CFS; tốc độ lõi Cloudflare so với máy Mac có thể lệch ±30%.

## 3. Benchmark (1 phiên = claims + rules + chart + reasoning + analysis song song, rồi year; mọi phiên bắt đầu cùng lúc; 1 lần chạy mỗi ô)

Cột "gốc" = code hiện tại; "tối ưu" = 3 thay đổi bên dưới. Đơn vị: p50/p95 giây, thông lượng phiên/phút, RSS đỉnh MB.

| Instance (mô phỏng) | Phiên | gốc p50 / p95 | gốc phiên/phút | gốc RSS | tối ưu p50 / p95 | tối ưu phiên/phút | tối ưu RSS |
|---|---|---|---|---|---|---|---|
| **1/16 vCPU (lite, hiện tại)** | 1 | 2,48 / 2,48 | 23 | 79 | 2,54 / 2,54 | 23 | 59 |
| | 4 | 10,4 / 10,5 | 23 | 111 | 5,5 / 5,6 | 42 | 66 |
| | 8 | 20,5 / 20,6 | 23 | 153 | 11,7 / 11,9 | 40 | 65 |
| | 14 | **51,5 / 53,8** | 16 | 170 | 17,9 / 19,7 | 42 | 66 |
| | 20 | **62,5 / 70,7** | 17 | 186 | 27,9 / 31,8 | 38 | 65 |
| **1/4 vCPU (basic)** | 1 | 0,94 / 0,94 | 63 | 69 | 0,31 / 0,31 | 191 | 64 |
| | 8 | 6,9 / 7,0 | 68 | 146 | 2,3 / 2,3 | 210 | 72 |
| | 14 | 10,9 / 11,0 | 76 | 182 | 3,6 / 3,9 | 215 | 70 |
| | 20 | 13,6 / 15,9 | 75 | 208 | 4,2 / 5,8 | 207 | 68 |
| **1/2 vCPU (standard-1)** | 14 | 4,8 / 4,8 | 173 | 189 | 1,7 / 1,7 | 493 | 80 |
| | 20 | 6,2 / 6,7 | 177 | 228 | 2,6 / 2,6 | 443 | 81 |
| **1 vCPU (standard-2)** | 14 | 2,6 / 2,6 | 316 | 194 | 0,9 / 0,9 | 926 | 80 |
| | 20 | 3,3 / 3,8 | 315 | 218 | 1,3 / 1,3 | 873 | 79 |

(Đủ 1/4/8/14/20 cho cả 4 mức CPU nằm trong `results_v1_year1x.jsonl` đi kèm.)

Tách đóng góp, 1/4 vCPU, 14 phiên: gốc 12,0 s / 3,16 CPU-s; chỉ bỏ claims+rules 9,4 s / 2,21; chỉ cache backend 8,5 s / 2,53; cả ba 3,9 s / 1,10 (CPU/phiên giảm ~65%).

Lưu ý: vòng này mỗi phiên chỉ gọi `/api/year` 1 lần cho cả hai bản; thực tế bản gốc gọi 4 lần, nên số "gốc" ở trên hơi lạc quan (~+10% CPU). Vòng đo lại với 4 lần đang chạy dở khi phiên bị cắt (xem "Chưa làm").

## 4. Tối ưu code đã thử (trong worktree riêng, **chưa áp vào repo**)

Patch: `docs/capacity/prototype.patch`. Kiểm chứng: 810/810 phản hồi **giống từng byte** giữa bản gốc và bản tối ưu (chart, analysis, reasoning, year, hour-sweep; 160 ngày sinh gồm hai trường phái, hai lịch, lỗi 422); `pytest` 1119 đạt cả hai bản; 38/38 hành trình giao diện đạt với frontend tối ưu; meta tĩnh khớp API (1674 cụm, 7 nguồn); chặn `meta.json` thì tự quay về API.

1. **Meta tĩnh**: `tools/build_meta.py` sinh `engine/web/js/meta.json` (claims + tên nguồn, 48 KB nén), `loadMeta` đọc file này trước, lỗi mới gọi API. Bỏ 2 request và ~75 ms CPU mỗi lượt mở trang.
2. **Cache backend** (`api.py`): `lru_cache` cho `_compute` (theo `BirthInput`, tối đa 64) và cho gói rule + kiểm tra gói (`_pack`). Lỗi vẫn trả 422 như cũ, không cache lỗi.
3. **Chống trùng request** (`util.post`): các POST giống hệt nhau trong một lượt xem dùng chung một request (`/api/year` 4 → 1).

Đề xuất thêm, chưa thử:
- `uvicorn --timeout-keep-alive 75` (A/B ở mục 2.3; không tốn phí).
- `.dockerignore` loại `engine/tests`, tài liệu, file không cần ở runtime; ghim phiên bản `pip`.
- Lập chỉ mục quy tắc trong `engine.run` (chiếm ~70% CPU của reasoning): hứa hẹn nhất nhưng thuộc phiên reasoning-engine, cần test hồi quy riêng.
- Giao diện: timeout cho mỗi lần gọi và dòng "máy chủ đang bận, đang thử lại…" sau vài giây.

## 5. Ba cấu hình (đơn giá từ tài liệu Cloudflare Containers, cập nhật 5/10/2026)

Giá: bộ nhớ $0,0000025/GiB-s (miễn phí 25 GiB-giờ), đĩa $0,00000007/GB-s (miễn phí 200 GB-giờ), CPU $0,00002/vCPU-s theo mức dùng thực (miễn phí 375 vCPU-phút), cộng gói Workers Paid $5/tháng (giả định đã có). Bộ nhớ và đĩa tính theo cấu hình **cấp phát** trong lúc instance chạy; CPU theo mức dùng. Egress từ container $0,025/GB sau 1 TB miễn phí: ~1,6 MB/phiên (gốc), nên ~600.000 phiên/tháng vẫn miễn phí. Chi phí CPU thực tế ≈ $0,002 trên 1.000 phiên, không đáng kể.

Chi phí tháng giả định **chạy liên tục 730 giờ** (trần trên; trang ít truy cập sẽ ngủ sau 10 phút nên rẻ hơn):

| Cấu hình | Thiết lập | Sức chứa bền vững (code tối ưu) | 14 phiên cùng lúc (p50) | Chi phí tháng (trần) | Đánh đổi |
|---|---|---|---|---|---|
| **Low Cost** | `lite` ×1 (giữ nguyên) + tối ưu code | ~40 phiên/phút | ~18 s (20 phiên: p95 ~32 s) | **~$1,7** (bộ nhớ 1,42 + đĩa 0,32) | rẻ nhất; vẫn chậm khi có đợt tải đột biến; 1 điểm hỏng |
| **Balanced (khuyến nghị)** | `basic` ×1 (1/4 vCPU, 1 GiB) + tối ưu code | ~200 phiên/phút | ~3,6 s (20 phiên: p95 ~5,8 s) | **~$7** (bộ nhớ 6,35 + đĩa 0,69) | hết timeout trong đo; vẫn 1 instance, không dự phòng |
| **High Capacity** | 2 × custom (1 vCPU, 3 GiB) + `getRandom(env.TVBT, 2)` + `max_instances ≥ 2` | ~1.700 phiên/phút (ước tính, chưa đo 2 instance) | ~0,9 s | **~$40** | có dự phòng; cần sửa `src/index.ts`; tốn gấp nhiều lần so với nhu cầu hiện tại |

Giả định: tốc độ lõi Cloudflare ≈ máy đo; mỗi instance chỉ dùng 1 lõi (1 worker). Không nên mua `standard-3/4` (2–4 vCPU) nếu không chạy thêm `--workers`. Số 1.700 là 2 × 880 phiên/phút đo ở 1 vCPU, chưa đo thật 2 instance.

## 6. Khuyến nghị (theo thứ tự)

1. Áp 3 tối ưu code + `--timeout-keep-alive 75` (miễn phí; giảm ~65% CPU mỗi phiên; không đổi kết quả lá số).
2. Nâng lên `basic` (`"instance_type": "basic"` trong `wrangler.jsonc`, +~$5/tháng). Đây là cải thiện lớn nhất theo chi phí.
3. Chỉ chuyển sang nhiều instance khi lưu lượng thực tế đòi hỏi; cần sửa Worker dùng `getRandom`.
4. Xem Containers dashboard (log + metrics) để xác nhận nguyên nhân 500 trước khi mua thêm: nếu thấy OOM hay restart thì tăng bộ nhớ, nếu không thì giữ `basic`.

Cần bạn quyết định: bước 2 và 3 phát sinh chi phí; tôi chưa đổi gì.

## 7. Chưa làm (do hết hạn mức)

- Vòng benchmark lặp với `/api/year` ×4 cho bản gốc (script chạy nền ghi vào `results2.jsonl`; kết quả chưa được kiểm).
- Chưa áp patch vào repo, chưa thêm test tự động cho patch (cần `test_glossary`-kiểu kiểm tra meta.json không lỗi thời).
- Chưa đo cold start thật trên production, chưa lặp mỗi ô benchmark nhiều lần để có khoảng tin cậy.
