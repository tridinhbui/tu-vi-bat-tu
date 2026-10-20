# Interpretation Reasoner — chương Mệnh (luận trước, viết sau)

Kế hoạch: `~/.claude/plans/quirky-tinkering-rabin.md`. Phiên bản: `reasoner-0.2.0` (guard vị trí + cách cục nháp), `narrative-0.1.0`. Trạng thái 2026-10-20: chỉ chương **Mệnh**, sau cờ `TVBT_REASONER=1` (route `mode: "reasoned"`); production không đổi (Worker không truyền cờ này). 11 chương còn lại đóng băng trên đường `mode: "prose"` cũ. Không có chuyên gia trong vòng kiểm định; mọi chỉ số dưới đây là tự động.

## Vì sao

Đường cũ (`prose/select.ts`) chọn khái niệm theo một điểm phẳng rồi điền vào schema. Đo trên 1.000 lá số (`docs/REASONER-BASELINE.md`):

- 60 % khái niệm được nói ra là thứ ≥ 50 % lá số đều có (`cog.sharp` có ở 89 % lá số, được nói trong 72 % chương Mệnh);
- bỏ một sao không luật nào nhắc tới làm **văn đổi nhiều hơn** bỏ một sát tinh (độ giống trigram 0,20 so với 0,59), vì câu chữ được gieo theo danh sách sao; 30 % biến thể vô hại còn đổi cả nội dung;
- bỏ một Hóa khỏi Mệnh chỉ đổi nội dung 2/9 lần; cách cục (vd. *Kình Dương nhập miếu*, 0,9 % lá số) bị bỏ rơi; giới hạn Tứ Mộ của chính Hóa Lộc đang "gỡ" cho Cự Môn hãm không được nói cạnh nhau.

## Kiến trúc

```
facts → run → lift → resolve → applyQualifiers            (giữ nguyên)
      → reason/tiers.ts      seat của mỗi khẳng định + tầng (T1 chính tinh … T6 phụ tinh), độ hiếm từ base_rates
      → reason/adjudicate.ts trục khái niệm ↔ đối khái niệm: lời sách → đặc hiệu → tầng → tranh chấp
      → reason/plan.ts       khung, luận điểm (2–3), yếu tố điều chỉnh, đường đời, độ số  ⇒ ReadingPlan (dữ liệu, test được)
      → prose/narrative.ts   mỗi luận điểm một đoạn: CLAIM → BECAUSE → BUT/UNLESS → đối chiếu Tài/Quan/Di
```

### Seat và tầng (quy ước hệ thống, `he_thong`)
Mỗi khẳng định đứng trên **atom cơ bản nhất** của điều kiện luật (seat); các atom khác là *liên kết* (bằng chứng hai yếu tố tương tác). T1 chính tinh + độ sáng tại Mệnh (VCD: chính tinh xung chiếu) · T2 cách cục (luật `formation` bắn, nâng seat mang nó) · T3 Tứ Hóa, gắn sao mang Hóa · T4 lục sát / lục cát / Lộc Tồn / Thiên Mã tại Mệnh · T5 Tuần/Triệt, tam phương · T6 phụ tinh khác. Độ số (giờ, mùa, cục, can chi) chỉ làm seat khi không còn atom nào khác.

### Độ hiếm
`tools/interpret/base_rates.ts` → `engine/data/kg/base_rates.json` (biên dịch vào `knowledge.kg.baseRates`): tần suất mỗi khái niệm ở Mệnh và mỗi luật bắn ở Mệnh trên corpus 1.000 lá (corpus phân tầng, nên đây là cận trên, không phải xác suất). `rarity = log₂(1/rate)/log₂(200)`.

### Xử lý mâu thuẫn (`adjudicate.ts`)
Theo thứ tự cố định, không đếm phiếu: (a) luật nói khái niệm **giảm** (stance `weakens`, vd. Hóa Lộc ở Tứ Mộ) là *reducer* của phía đó, không phải phía đối lập; khẳng định bị sách làm yếu vẫn ở phía mình, nói ở dạng giảm; (b) đặc hiệu: chữ ký bằng chứng chứa chữ ký kia (có tính độ sáng: "Cự Môn hãm" hẹp hơn "Cự Môn") → hẹp thắng; (c) tầng thấp hơn là nền, phía kia thành giới hạn; (d) còn lại: **contested**, nói rõ hai chiều, không kết luận.

### Luận điểm (`plan.ts`)
Mỗi trục thuộc về seat của khẳng định mạnh nhất. Claim bị loại nếu khái niệm có ở ≥ 60 % corpus mà mọi luật đỡ nó bắn ở > ~7 % (Barnum gate). Điểm seat = trọng số tầng × phạm vi × (0,5 + tổng 3 độ hiếm cao nhất + thưởng cách cục). Lấy 2 luận điểm, thêm luận điểm thứ 3 nếu ≥ 40 % điểm luận điểm đầu. Một luận điểm *cứu giải* (life.mitigated) mà yếu tố cứu bị giảm ở chỗ khác mang theo `rescuerCaveat`; narrative kể hai điều liền nhau. **Modifiers**: mỗi Hóa / sát / cát tinh / Tuần–Triệt tại Mệnh không thành luận điểm có đúng một câu (chọn theo cấu trúc, không theo độ hiếm) — trả lời "Kình Dương đổi kết luận đến đâu".

### Văn (`narrative.ts`, `content/prose/reasoning_frames.json`, draft)
Ground dựng từ atom thật của lá số ("Cự Môn tuy ở vào thế hãm ở Tuất nhưng được hóa Lộc"), claim là lời đọc của chính luật hiếm nhất (mẫu "claim (điều kiện)" ở 1.141/1.171 luật Tử Vi verified), làm sạch; không sạch thì dùng thẻ khái niệm. Mỗi câu mang `trace.step` (bước của plan); validator chặn câu không có bước, câu nói khái niệm ngoài plan, cộng các lỗi chặn cũ. Biến thể câu gieo theo **nội dung plan**, nên thay đổi không ảnh hưởng lập luận không làm đổi chữ.

## Guard vị trí và cách cục (nối 2026-10-20)

- **Guard vị trí** (`engine/data/kg/position_guards.json`, từ `tools/interpret/audit_positions.ts`, `docs/audit/POSITION-AUDIT.md`): 270 luật bị đánh dấu; mặc định chỉ áp 12 yêu cầu `book` (siết chắc chắn), 122 yêu cầu `book?` chỉ áp khi `strictGuards`. Khẳng định không qua guard bị bỏ trước khi xếp seat và ghi vào `plan.guarded`. Trên corpus: 378/1.000 lá có ít nhất một khẳng định bị chặn, chủ yếu `TV_TH_AUX_MENH_DH_CHIEU` (sách "xung chiếu", điều kiện cả tam phương, 216 lá), `TV_TT_MENH_TA_HUU_TAI_QUAN` (sách "ở Tài Bạch, Quan Lộc", 154), `TV_TH_AUX_MENH_LOC_PHA` ("Phá Quân chính chiếu", 27). Lá mẫu: bỏ "đời sống đầy đủ" vì Hữu Bật ở Mệnh, Tả Phụ ở Thiên Di.
- **Cách cục nháp** (10 cách, `formations_experimental.json`, evaluator `reason/structures.ts`): trạng thái thành / thành thượng / bị phá / phá được cứu đặt lên seat của các sao lõi, nâng tầng lên T2 và cộng điểm; vào `frame.states`; chỉ được nói khi `allowDraft` (cùng cờ `TVBT_PROSE_DRAFT`), và không nói lại một cách đã có tên từ luật verified. Hình thức / không hiện / thiếu dữ kiện không được nói.

## Kết quả (tự động) — `docs/REASONER-EVAL.md` so với `docs/REASONER-BASELINE.md`

| Chỉ số | Cũ | Reasoned | Cổng kế hoạch |
|---|---|---|---|
| Biến thể critical làm đổi nội dung đúng chỗ | 73,0 % | 95,9 % | ≥ 90 % ✔ |
| Biến thể inert giữ nguyên nội dung / văn | 70 % / 0,20 | 100 % / 1,00 | ≥ 90 % ✔ |
| Jaccard tập khái niệm, cùng chính tinh (corpus) | 0,444 | 0,214 | giảm ✔ |
| Khái niệm được nói mà ≥ 50 % lá số có | 60,1 % | 40,5 % | (theo dõi) |
| Barnum: tần suất nền TB khái niệm được nói | 56,6 % | 47,5 % | giảm ≥ 30 % ✘ (−16 %) |
| Căn cứ: tần suất luật hiếm nhất mỗi câu | 8,2 % | 7,0 % | (theo dõi) |
| Strip test (trigram, khác chính tinh) | 0,054 | 0,079 | (theo dõi; khung câu còn ít biến thể) |

Barnum chưa đạt mục tiêu −30 %: lớp modifiers cố ý nói những đọc phổ biến nhưng mang tính cấu trúc (Tuần → "vui ít buồn nhiều"), và bộ khái niệm chỉ có 76 nét thô nên có sàn. Thước đo cấp luật (căn cứ) phản ánh tốt hơn vì văn mới nói lời của luật, không phải của khái niệm.

## Hạn chế đã biết
- Tầng, trọng số, ngưỡng Barnum, quy tắc đặc hiệu là quy ước hệ thống, chưa qua người am hiểu trường phái.
- Lời đọc luật là bản diễn ý (paraphrased) trong pack; điều kiện chung ("Thìn hoặc Tuất") đôi khi lọt vào văn.
- Biến thể phản thực một phần không có thật về thiên văn (cờ `synthetic`); chúng kiểm tra lập luận, không kiểm tra lịch.
- Cách cục nháp và guard vị trí đều là bản nháp (xem dưới); bộ dò `structures.py` đã port (`reason/structures.ts`, parity 1.000 lá) nhưng chưa dùng trong văn — kết luận của nó trùng các luật đã nói.
- `base_rates.json` tính trước khi áp guard (tần suất bắn luật không đổi; tần suất khái niệm có thể hơi cao hơn thực).

## Chạy lại
```
.venv/bin/python tools/interpret/make_benchmark.py      # benchmark20.json + counterfactual100.json.gz
node tools/interpret/base_rates.ts && node tools/interpret/build.ts
node tools/interpret/eval_distinct.ts --engine old       # docs/REASONER-BASELINE.md
node tools/interpret/eval_distinct.ts --engine reasoned  # docs/REASONER-EVAL.md
node --test src/interpret/test/reasoner.test.ts          # UPDATE_GOLDEN=1 tái sinh benchmark20.reasoned.txt
```
Dev server: `TVBT_INTERPRET=1 TVBT_PROSE_DRAFT=1 TVBT_REASONER=1 node tools/interpret/dev_server.ts`, rồi `POST /api/interpret {…, "chapter":"menh", "mode":"reasoned"}` (trả `text`, `paragraphs` có `trace.step`, và `plan`).
