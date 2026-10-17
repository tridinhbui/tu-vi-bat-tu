# Phase 1 — kết quả triển khai (engine suy luận đa tầng, bản thử nghiệm)

Triển khai Phase 1 của [NANG_CAP_LUAN_GIAI.md](NANG_CAP_LUAN_GIAI.md). Không dùng LLM/AI API; không đổi UI, Worker hay cấu hình Cloudflare.

## Đã làm

| Hạng mục | Ở đâu |
|---|---|
| Fact theo vai: đồng cung / xung chiếu / tam hợp (1,2) / giáp (trước, sau) / nhị hợp; hóa theo vai; Tuần-Triệt cung xung; đếm cát/sát | [positions.py](../engine/tvbt/reasoning/positions.py), nối vào `facts.tuvi_facts` (chỉ thêm khóa, không đổi khóa cũ) |
| `dignity_rank` 0–4 (hãm→miếu); `tp_rank.<sao>` cho sao nằm ở bất kỳ cung nào trong tam phương. Độ sáng sách không nêu → không có fact (UNKNOWN, không đoán) | cùng file |
| DSL: `ref` (đọc cung khác theo vai hoặc theo tên), `count`, toán tử `contains_any/contains_all/not_contains`, logic 3 giá trị giữ nguyên | [dsl.py](../engine/tvbt/knowledge/dsl.py) |
| Engine: `ref` + `exceptions` có provenance sang cung khác; fact suy ra ở phạm vi chart được nối đúng vào why-chain; suy luận nhiều bước xuyên cung | [engine.py](../engine/tvbt/reasoning/engine.py) |
| `conflictsWith` thực sự được xử lý (trước đây chỉ validate): hai luật khai báo mâu thuẫn dù kết luận khác nhau → `unresolved` nếu chưa có nguồn đã xác minh | [conflict.py](../engine/tvbt/reasoning/conflict.py) |
| Cách cục là thực thể: `core / boosters / breakers / rescuers / refutations` → `khong_hien · hinh_thuc · thanh · thanh_thuong · bi_pha · pha_duoc_cuu`; phản chứng hạ một bậc; "còn thiếu gì để lên bậc" | [formation.py](../engine/tvbt/knowledge/formation.py), [formation_eval.py](../engine/tvbt/reasoning/formation_eval.py) |
| 10 cách cục thử nghiệm + 3 luật demo suy luận nhiều bước | [data/experimental/](../engine/data/experimental) (sinh bởi [build_experimental_formations.py](../tools/build_experimental_formations.py)) |
| API: `experimental: true` (mặc định tắt) thêm khối `experimental` riêng | [api.py](../engine/tvbt/api.py) |

10 cách: Tử Phủ Vũ Tướng · Tử Phủ đồng cung · Cơ Nguyệt Đồng Lương · Sát Phá Liêm Tham · Nhật Nguyệt tịnh minh · Nhật lệ trung thiên · Thạch trung ẩn ngọc · Mã đầu đới kiếm · Tam kỳ gia hội · Khôi Việt giáp Mệnh.

## Ranh giới "không đưa quy tắc chưa kiểm chứng vào production"

- 10 cách và 3 luật demo nằm trong `data/experimental/`, **không** có trong `PACKS` của `loader.load_all`; `reviewStatus=draft`, nguồn `SRC_EXPERIMENTAL` (`verified=false`); `validate_formations` cấm `verified`.
- Mọi điều kiện thành/phá/cứu/phản chứng là **giả thuyết thiết kế của tôi từ kiến thức chung, chưa đối chiếu trang sách nào**. Chúng chứng minh engine biểu diễn và đánh giá được cấu trúc, không chứng minh mệnh lý đúng.
- Mặc định API không đổi; bật cờ thì `systems` vẫn y hệt (có test). Câu chữ sinh ra luôn gắn "bản thử nghiệm, chưa đối chiếu sách; chỉ mô tả cấu trúc, không dự báo".

## Kiểm chứng

- `pytest`: **263 test xanh** (134 cũ + các test cũ của phiên khác + 129 test Phase 1): fact theo vai, `dignity_rank`, DSL, engine (ref/exception/multi-hop/conflictsWith), **mỗi cách trong 10 cách qua đủ trạng thái** (không hiện, hình thức, thành, thành thượng, bị phá, được cứu, phản chứng hạ bậc, rescuer chỉ cứu đúng breaker được nêu), 49 lá số thật ghim theo trạng thái.
- **A/B hồi quy** ([ab_regression.py](../tools/ab_regression.py)): cùng dữ liệu và cùng mã tính lá số, chỉ đổi `dsl.py/engine.py/conflict.py` từ bản trước Phase 1 sang bản mới. 18 lá số × (`/api/chart`, `/api/analysis`, `/api/reasoning`, danh sách nhận định Tử Vi): **IDENTICAL**. Lệnh: `python tools/ab_regression.py <engine_A> <engine_B> <python>`.
- Quét 35.712 lá số mẫu (1950–2010): cả 10 cách đều gặp đủ các trạng thái trên lá số thật.

## So sánh trước/sau trên lá số thật

"Trước" là đầu ra production hiện hành (không đổi sau Phase 1, theo A/B). "Sau" là cùng lá số qua engine mới với cờ `experimental`. Tạo lại: `python tools/compare_before_after.py 1950-1-4-4-10-male …`.

Cùng một cấu trúc Tử Phủ Vũ Tướng trong tam phương Mệnh, production chỉ nói "điều kiện sơ khởi… tùy sao phụ, độ sáng, Tuần/Triệt, quy tắc hiện chưa phủ hết" cho cả ba lá số dưới đây. Engine mới phân biệt được:

### Lá số 1950-1-4 4:10 male — Mệnh Giáp Tuất, chính tinh: Liêm Trinh, Thiên Phủ

**TRƯỚC (production, không đổi)** — chương “Cách cục”:

- [Thế] (đoạn thần sát Bát Tự, lược bớt)
- [Cách] Trong tam phương của Mệnh có từ ba sao trở lên của nhóm Tử – Phủ – Vũ – Tướng: Thiên Phủ, Thiên Tướng, Tử Vi và Vũ Khúc. Đây mới là điều kiện hình thành sơ khởi của một thế cục; việc thế cục ấy thành hay bị phá còn tùy sao phụ, độ sáng và Tuần/Triệt, mà quy tắc hiện chưa phủ hết.
- [Cách] Cấu trúc Sát – Phá – Tham cùng nằm trong tam phương của các cung: Phúc Đức, Thiên Di và Phu Thê. Đây là vị trí hình học của ba sao; sách chia ba sao này thành các thế khác nhau tùy cung và sao đi kèm.

  (production có 29 nhận định Tử Vi; không có trạng thái thành/phá/cứu cho bất kỳ cách nào.)

**SAU (engine Phase 1, thử nghiệm, bật `experimental`)**:

- `CACH_X_TU_PHU_VU_TUONG` → **thanh_thuong** — Cách Tử Phủ Vũ Tướng (cung Mệnh): thành cách, thế mạnh. Yếu tố tăng thế: Văn Xương hoặc Văn Khúc hội trong tam phương; Lộc Tồn hoặc Hóa Lộc hội trong tam phương. (Bản thử nghiệm, chưa đối chiếu sách; chỉ mô tả cấu trúc, không dự báo.)
- suy luận nhiều bước: `xr_quan_loc_trong_tam_phuong_cach` (support, độ sâu 3, supported) ← xr_quan_loc_trong_tam_phuong_cach (support) @palace:Quan Lộc ← XR_QUAN_LOC_TRONG_TAM_PHUONG_CACH [draft] @palace:Quan Lộc ← SRC_EXPERIMENTAL (unverified) ← palace.rel.tp_names=['Mệnh', 'Thiên Di', 'Quan Lộc', 'Tài Bạch'] @palace:Mệnh

### Lá số 1950-1-4 20:10 male — Mệnh Bính Dần, chính tinh: Vũ Khúc, Thiên Tướng

**TRƯỚC (production, không đổi)** — chương “Cách cục”:

- [Thế] (đoạn thần sát Bát Tự, lược bớt)
- [Cách] Trong tam phương của Mệnh có từ ba sao trở lên của nhóm Tử – Phủ – Vũ – Tướng: Thiên Phủ, Thiên Tướng, Tử Vi và Vũ Khúc. Đây mới là điều kiện hình thành sơ khởi của một thế cục; việc thế cục ấy thành hay bị phá còn tùy sao phụ, độ sáng và Tuần/Triệt, mà quy tắc hiện chưa phủ hết.
- [Cách] Cấu trúc Sát – Phá – Tham cùng nằm trong tam phương của các cung: Phu Thê, Phúc Đức và Thiên Di. Đây là vị trí hình học của ba sao; sách chia ba sao này thành các thế khác nhau tùy cung và sao đi kèm.

  (production có 50 nhận định Tử Vi; không có trạng thái thành/phá/cứu cho bất kỳ cách nào.)

**SAU (engine Phase 1, thử nghiệm, bật `experimental`)**:

- `CACH_X_TU_PHU_VU_TUONG` → **bi_pha** — Cách Tử Phủ Vũ Tướng (cung Mệnh): bị phá cách. Yếu tố tăng thế: Văn Xương hoặc Văn Khúc hội trong tam phương; Lộc Tồn hoặc Hóa Lộc hội trong tam phương. Yếu tố phá cách: Hóa Kỵ đồng cung với Mệnh. Chưa có yếu tố nào cứu: Hóa Kỵ đồng cung với Mệnh. Còn thiếu: cứu giải: Hóa Khoa đồng cung với Mệnh (giải Kỵ). (Bản thử nghiệm, chưa đối chiếu sách; chỉ mô tả cấu trúc, không dự báo.)

### Lá số 1950-2-4 10:10 female — Mệnh Nhâm Thân, chính tinh: Tử Vi, Thiên Phủ

**TRƯỚC (production, không đổi)** — chương “Cách cục”:

- [Thế] (đoạn thần sát Bát Tự, lược bớt)
- [Cách] Trong tam phương của Mệnh có từ ba sao trở lên của nhóm Tử – Phủ – Vũ – Tướng: Thiên Phủ, Thiên Tướng, Tử Vi và Vũ Khúc. Đây mới là điều kiện hình thành sơ khởi của một thế cục; việc thế cục ấy thành hay bị phá còn tùy sao phụ, độ sáng và Tuần/Triệt, mà quy tắc hiện chưa phủ hết.
- [Cách] Cấu trúc Sát – Phá – Tham cùng nằm trong tam phương của các cung: Thiên Di, Phu Thê và Phúc Đức. Đây là vị trí hình học của ba sao; sách chia ba sao này thành các thế khác nhau tùy cung và sao đi kèm.

  (production có 40 nhận định Tử Vi; không có trạng thái thành/phá/cứu cho bất kỳ cách nào.)

**SAU (engine Phase 1, thử nghiệm, bật `experimental`)**:

- `CACH_X_TU_PHU_VU_TUONG` → **pha_duoc_cuu** — Cách Tử Phủ Vũ Tướng (cung Mệnh): bị phá nhưng được cứu giải. Yếu tố tăng thế: Lộc Tồn hoặc Hóa Lộc hội trong tam phương. Yếu tố phá cách: sát tinh (Kình, Đà, Hỏa, Linh, Không, Kiếp) đồng cung với Mệnh. Yếu tố cứu giải: Triệt đóng ở cung Mệnh (giải sát tinh đồng cung). (Bản thử nghiệm, chưa đối chiếu sách; chỉ mô tả cấu trúc, không dự báo.)
- `CACH_X_TU_PHU_DONG_CUNG` → **pha_duoc_cuu** — Cách Tử Phủ đồng cung (cung Mệnh): bị phá nhưng được cứu giải. Yếu tố tăng thế: Thiên Khôi hoặc Thiên Việt hội trong tam phương. Yếu tố phá cách: sát tinh (Kình, Đà, Hỏa, Linh, Không, Kiếp) đồng cung với Mệnh. Yếu tố cứu giải: Triệt đóng ở cung Mệnh (giải sát tinh đồng cung). (Bản thử nghiệm, chưa đối chiếu sách; chỉ mô tả cấu trúc, không dự báo.)


Đọc kết quả: lá số 1 `thành cách, thế mạnh` (có Xương/Khúc và Lộc hội, không yếu tố phá); lá số 2 cùng cấu trúc nhưng `bị phá cách` vì Hóa Kỵ đồng cung Mệnh, và engine nói còn thiếu gì để cứu (Hóa Khoa đồng cung); lá số 3 có sát tinh đồng cung nhưng `được cứu giải` nhờ Triệt. Lá số 1 còn kích hoạt suy luận hai bước: cách thành ở Mệnh → luật demo đọc Quan Lộc qua `ref` vào tam phương của Mệnh, kèm why-chain đầy đủ.

## Giới hạn và việc tiếp theo

- Chưa nối UI (theo yêu cầu giữ nguyên UI). Trạng thái cách nằm ở `/api/reasoning` → `experimental.formations[].state`.
- Chưa có lưu niên/lưu Tứ Hóa, Phi Hóa, topic recipe liên cung (các Phase sau trong tài liệu đề xuất).
- Tỷ lệ xuất hiện của vài cách rất cao (Cơ Nguyệt Đồng Lương, Sát Phá Liêm Tham ≥3/4 sao trong tam phương: ~25–28% lá số mẫu), nên điều kiện lõi cần đối chiếu sách trước khi đưa vào production.
- Việc quan trọng nhất: đối chiếu từng cách với sách có số trang, rồi mới chuyển `draft` → `verified` và đưa vào `PACKS`.
- Lưu ý quy trình: một phiên khác trong cùng repo đã gom các thay đổi Phase 1 đang viết dở của tôi vào commit `f13e724` (cùng 64 luật cách cục của họ). Nội dung là của Phase 1; chỉ có engine.py (sửa provenance fact chart-scope) và các file test/tool mới còn chưa commit.

## Cập nhật: hai ô "không bao giờ gặp" (do phiên UI phát hiện khi quét 25.000 lá số)

Tôi quét toàn bộ không gian (10 can năm × 12 tháng × 28 ngày × 12 giờ, nam và nữ; 40.320 lá số mỗi giới):

- **Khôi Việt giáp Mệnh × bị phá nhưng được cứu**: có tồn tại, hiếm (cần năm Bính, Mệnh ở Tuất, giờ Tý, Hóa Khoa đồng cung Hóa Kỵ). Ví dụ: 1986-10-10 giờ Tý, nam; đã ghim vào `test_phase1_real_charts.py`.
- **Mã đầu đới kiếm × thành cách thế mạnh**: **không có lá số nào** trong toàn không gian đó. Nguyên nhân dự đoán (chưa chứng minh chặt): Kình Dương ở Ngọ chỉ xảy ra với can Bính/Mậu, và ở hai can này Thiên Khôi/Thiên Việt không bao giờ rơi vào tam phương của Mệnh Ngọ, nên một trong ba yếu tố tăng thế không bao giờ có; hai yếu tố còn lại (Tả Hữu cùng hội, Xương Khúc) không khớp đồng thời với điều kiện còn lại. Đây là hệ quả của **định nghĩa tôi đặt**, không phải phát hiện về mệnh lý. Cách xử lý đề xuất: khi đối chiếu sách, định nghĩa lại yếu tố tăng thế của cách này (hoặc hạ `thuong_at` về 1).
- Sửa lỗi: phần "Lưu ý" của `render_vi` không còn in id nội bộ (`boosters:...`), dùng nhãn tiếng Việt; id máy đọc vẫn ở trường `unknown`.
