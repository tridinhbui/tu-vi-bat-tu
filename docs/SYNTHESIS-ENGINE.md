# Rule-based Synthesis Engine & Vietnamese Narrative Grammar (Tử Vi)

Trạng thái: **đã triển khai sau cờ `TVBT_DEEP_INTERPRETATION` (mặc định TẮT)**. Chưa commit, chưa merge, chưa deploy. Không dùng mô hình ngôn ngữ, embedding hay dịch vụ sinh văn bản nào ở runtime (có test khóa). Các endpoint hiện có không đổi từng byte khi cờ tắt hoặc bật (có test).

- Endpoint mới: `POST /api/synthesis` (body `BirthReq`; `to_year` chọn năm cho chương Đại hạn; `level=5` trả thêm Semantic IR).
- Giao diện: mục **“Luận giải tổng hợp”** ở đầu 8 chương Tử Vi (Tổng quan, Bản Mệnh, Tính cách, Công danh, Tài Bạch, Quan hệ, Đại hạn & lưu niên, Cách cục). Danh sách quy tắc chi tiết bên dưới giữ nguyên làm tầng bằng chứng. Khi cờ tắt, request trả 404 và giao diện bỏ qua yên lặng.
- Mẫu đầy đủ trước/sau: [docs/synthesis/SAMPLE-REFERENCE-CHART.md](synthesis/SAMPLE-REFERENCE-CHART.md). Kiểm toán bộ quy tắc: [docs/synthesis/rule_audit.json](synthesis/rule_audit.json).

> Lưu ý về yêu cầu: bản prompt dán vào bị cắt giữa Phase 6, mục A (“Hình ảnh con người được xây dựng từ Mệ…”). Phase 1–5 và phần đầu Phase 6 được làm đầy đủ; các mục Phase 6 sau mục A (nếu có) và mọi phase sau đó chưa nhận được nên chưa làm.

---

## 1. Phase 1 — Điều tra và nguyên nhân gốc (có dẫn chứng mã)

Lá số tham chiếu dùng xuyên suốt: 10/03/2001 10:30, nam — Mệnh Tuất có Cự Môn hãm hóa Lộc, Kình Dương miếu, Hỏa Tinh, Hồng Loan. Đây là lá số khớp đúng ví dụ trong yêu cầu; engine không hardcode nó.

### 1.1 Vì sao nhận định bị rời rạc?
- `nlg/generate.py:114-150` (`realize`) dựng **một câu cho mỗi cặp (cung, claim)** với cùng khuôn “Có thể nhận thấy một dấu hiệu gắn với …” (`:128`). Không có bước nào gom các nhận định cùng ý, cùng sao hay cùng lĩnh vực.
- Lớp duy nhất có quan hệ giữa các nhận định là `reasoning/conflict.py:27-31`, và nó chỉ nhóm theo **(subject, claim) trùng khóa**. Hai quy tắc khác claim nhưng cùng nghĩa (“ngang ngược, tự đắc” của KL, “ngang ngược, cương” của TT, “cương cường… nhưng hay tự đắc” của TH) không bao giờ gặp nhau.
- Frontend (`web/js/report.js:172`) rải finding vào chương theo **cung** (`PAL_CH`, `:70`), rồi in từng `findingCard` riêng.

### 1.2 Vì sao có kết luận trái chiều mà không giải thích?
- `conflict.resolve` chỉ coi là xung đột khi **cùng claim** có effect support và limit. “Thông minh, phán xét sáng suốt” (KL, Cự Môn thủ Mệnh) và “kém sáng suốt, đa nghi” (TH, Cự Môn hãm) là hai claim khác nhau ⇒ không được so sánh, hiện cạnh nhau như hai sự thật độc lập.
- Khi có so sánh, quy tắc chọn thắng theo **số lá điều kiện** và chỉ thắng nếu verified; còn lại là “unresolved” chung chung. Không có phân loại *chung–riêng*, *cùng đúng ở hai điều kiện*, *hai sách khác nhau*.
- `Finding.effect` (`reasoning/engine.py:40`) là “support/limit” của **quy tắc đối với claim**, không phải chiều thuận/nghịch của nội dung: `TV_TH_CU_HAM_GIAN_XAO_DA_NGHI` (đa nghi, khắc nghiệt) là `support`. Không có trường nào nói nội dung thuận hay nghịch.

### 1.3 Vì sao chương Tính cách ít nội dung dù Bản Mệnh có nhiều nhận định liên quan?
- `PAL_CH` (`report.js:70`) gán **chỉ Phúc Đức** cho chương Tính cách; mọi finding của cung Mệnh — nơi chứa phần lớn nhận định về tính khí, tư duy, giao tiếp — đi vào Bản Mệnh. Trên lá số tham chiếu: Mệnh 34 finding, Phúc Đức 3.
- Engine mới phân chương theo **khía cạnh ngữ nghĩa** (facet → `home` trong `data/semantic/ontology.json`), không theo cung: chương Tính cách lá số tham chiếu có 8 chủ đề, dựng từ Mệnh + Phúc Đức (+ Thân).

### 1.4 Quy tắc nào lặp cùng một ý?
`tools/semantic_audit.py` (đầu ra `docs/synthesis/rule_audit.json`):
- **40 nhóm** quy tắc verified từ ≥2 sách đứng trên **cùng dữ kiện** và cho cùng khái niệm (ví dụ Tấu Thư ở Mệnh: 3 quy tắc KL/TH cùng “nói ngọt, dễ thuyết phục”; Tử Vi + Tả Hữu: KL và TT). Trước đây mỗi quy tắc là một dòng; engine mới tính là **một căn cứ được nhiều sách xác nhận**.
- Trên lá số tham chiếu: “uy quyền” (TH tr.63 và TT tr.50, cùng Kình–Hỏa ở Tứ Mộ), “Quyền–Lộc gặp nhau” (KL tr.66 và TT tr.49), “Hóa Lộc tại Mệnh tài lộc tốt” (KL, TH).
- Một cấu trúc cấp lá số (`TV_STRUCT_SAT_PHA_THAM_001`) được khẳng định **một lần cho mỗi cung** của bộ tam hợp (3 lần trên lá số tham chiếu).

### 1.5 Quy tắc nào có điều kiện chưa đầy đủ hoặc nhãn bằng chứng không chính xác?
- **46 claim dùng chung** cho nhiều quy tắc; nhãn tiếng Việt của claim mang điều kiện của *một* quy tắc. **36 quy tắc** có điều kiện trong nhãn khác điều kiện thật, ví dụ: `TV_TT_MENH_DUONG_THAN` (nhãn ghi “Thái Dương ở Mùi”, quy tắc là “ở Thân”), `TV_TT_DIEN_TRACH_VU_THAM` (nhãn ghi Tài Bạch, quy tắc đọc Điền Trạch), `TV_KL_AUX_QUAN_PHU_VIET` (nhãn “Quan Phủ và Thái Tuế đồng cung”, quy tắc chỉ kiểm Quan Phủ — trên lá số tham chiếu Thái Tuế ở Tật Ách).
- **14 quy tắc effect=`limit` mang nhãn tích cực**: `TV_KL_PHU2_HOA_LOC_TU_MO` và `TV_TH_AUX_MENH_HL_TU_MO` (Hóa Lộc ở Tứ Mộ: “tài lộc giảm”) hiển thị nhãn “tài lộc thuận lợi”.
- **4 quy tắc rộng phạm vi hơn câu sách**: `TV_KL_AUX_HONG_KHONG` — sách (KL tr.225) ghi “Hồng Loan gặp Thiên Không *đồng cung hoặc xung chiếu*”, điều kiện đọc cả tam phương ⇒ kích hoạt sai trên lá số tham chiếu (Thiên Không ở Tài Bạch, tam hợp). Tương tự hai câu “xung chiếu” của KL về Thái Dương–Cự Môn.
- `api._merge_corroborated` (`tvbt/api.py:172-186`) gộp thẻ theo (cung, claim, effect) và **nâng `basis` của thẻ thành `verified`** nếu bất kỳ quy tắc gộp vào là verified — một quy tắc nháp có thể hiện dưới nhãn đã đối chiếu.
- Engine mới **không sửa rule pack** (sẽ đổi `/api/reasoning`); nó áp các guard trong `data/semantic/applicability.json`: kiểm tra lại phạm vi theo câu sách (`recheck_scope`), đọc theo câu riêng của quy tắc thay vì nhãn chung (`use_description`), và tự động: effect `limit` luôn là hạn chế; cấu trúc lặp theo cung chỉ tính một lần. Đề xuất sửa pack nằm trong `rule_audit.json`.

### 1.6 Hệ thống hiện có đủ dữ kiện để tổng hợp đến mức nào?
- Đủ: vị trí sao, độ sáng (hai trường phái), Tứ Hóa, Tuần/Triệt, tam phương/giáp, giới tính, đại hạn/tiểu hạn/lưu Tứ Hóa (`temporal.tuvi_year`), điều kiện hình thức của mọi quy tắc (DSL) và nguồn/trang.
- Thiếu: quy tắc ưu tiên giữa các sách; quy tắc giao thoa đại hạn × nguyên cục; phạm vi của chữ “hội/gặp”; câu sách cho đa số tổ hợp. Vì vậy mọi khung ghép (frame) của engine được **ghi nhãn `he_thong`** và chỉ nâng lên `sach` khi chính một câu sách ghép hai ý (xem §3.3).

### 1.7 Rule schema thiếu thông tin ngữ nghĩa nào?
`KnowledgeRule` (`knowledge/schema.py`) chỉ có `conditions/consequences{claim, effect}`: không có lĩnh vực/khía cạnh, chiều thuận–nghịch, tình thái (khuynh hướng/khả năng/điều kiện/hạn chế), quan hệ giữa các mệnh đề, nhóm mâu thuẫn, vai trò diễn ngôn, hay ranh giới “năng lực ↔ cách biểu hiện”. Claim là một **slug + nhãn hiển thị** (`loader.load_claims`), không phải mệnh đề.

---

## 2. Kiến trúc

```
rule engine (không đổi)            Semantic IR                      Reasoner                         Narrative grammar
facts → engine.run → findings ──► semantics.annotate ──► reasoner.group → relate → build_themes ──► grammar (discourse plan,
claims_vi, rule descriptions        (applicability guards,     (dedup theo gốc dữ kiện,              sentence plan, realisation)
data/semantic/*.json                 concept matching,          phân loại mâu thuẫn, ưu tiên,     ──► grammar.validate
                                     chart-grounded trigger)    đồ thị lập luận)                  ──► chapters (8 chương) + crosspalace
```

| Module (`engine/tvbt/synthesis/`) | Vai trò |
|---|---|
| `semantics.py` | **Semantic IR** `SemanticEvidence`; đọc câu riêng của quy tắc; tách điều kiện (ngoặc cuối) và ghi chú biên tập; so khớp khái niệm (dài nhất trước, phủ định → khái niệm đối); cặp “A nhưng B” trong một câu sách; điều kiện thật trên lá số (`chart_trigger`); guard áp dụng. |
| `reasoner.py` | `Proposition` (khái niệm × cung), `Root` (gốc dữ kiện), `Edge` (quan hệ), `Theme`; phân loại mâu thuẫn; độ ưu tiên có công thức; đồ thị chủ đề. |
| `grammar.py` | Ngữ pháp diễn ngôn tiếng Việt, trạng thái diễn ngôn cấp chương, bộ kiểm tra văn bản. |
| `crosspalace.py` | Lăng kính liên cung (Mệnh+Phúc, Mệnh+Quan+Thân, Mệnh+Tài+Quan, Phu Thê+Mệnh+Phúc) và đại hạn. |
| `chapters.py` | Ghép 8 chương; Bản Mệnh theo **sao trục**; Tổng quan; Đại hạn & lưu niên; Cách cục (dùng `structures.py` của lớp v0). |
| `data/semantic/` | `ontology.json` (7 lĩnh vực, 35 khía cạnh, chương nhà, trọng số cung, lăng kính), `concepts.json` (~85 khái niệm, cue tiếng Việt, cụm danh từ thận trọng), `relations.json` (7 khung + ~60 quan hệ), `applicability.json` (guard). |

Lớp v0 (`compose.py`, `/api/deep-reading`) vẫn còn nguyên, không bị thay.

### 2.1 Semantic IR (schema thực tế)

```python
SemanticEvidence(
  id, rule_id, finding_id, subject, palace, claim,
  reading,          # câu riêng của quy tắc (lời sách đã diễn giải), không sinh mới
  segment,          # mệnh đề trong câu mang khái niệm này
  concept, facet, domain, kind,        # kind: capacity | trait | manifestation | outcome | timing | rescue | style
  polarity,         # + | - | ~  (đối với người đọc)
  modality,         # tendency | potential | condition | limitation | rescue
  role,             # asserts | limits | mitigates
  trigger_text,     # điều kiện như sách viết
  chart_trigger,    # các lá điều kiện ĐÚNG trên lá số, bằng tiếng Việt ("Kình hoặc Đà ở Mệnh" → "Kình Dương tại Mệnh")
  leaves, root,     # điều kiện hình thức; gốc dữ kiện chuẩn hóa (khóa độc lập)
  present_stars, facts_used,
  basis, schools, cites,               # basis copy nguyên từ engine, không bao giờ tự nâng
  applicability, applicability_note,   # ok | rechecked | relabelled
  paired_with,      # khái niệm mà CHÍNH câu sách đặt đối lại ("nghĩa khí nhưng nóng nảy")
  mapping)          # cue | palace_fallback
```
Ở cung người khác (Phu Thê, Tử Tức, Huynh Đệ, Phụ Mẫu, Nô Bộc), một nét tính cách/tài lộc mô tả **người đó**, nên được ánh xạ về khái niệm của cung (ví dụ “con cái… khá giả” không thành “tài lộc của đương số”).

Độ phủ ánh xạ (300 lá số ngẫu nhiên): **97,3%** finding verified có ít nhất một khái niệm; phần còn lại chỉ ở tầng bằng chứng và được đếm trong câu giới hạn của chương. Test giữ ngưỡng ≥ 90%.

### 2.2 Ontology
7 lĩnh vực: con người, sự nghiệp, tài chính, quan hệ, phát triển đời sống, đời sống tinh thần, sức khỏe/tuổi thọ; 35 khía cạnh gồm đủ danh sách yêu cầu (tư duy, giao tiếp, tính độc lập→tính khí/áp lực, tham vọng, kỷ luật, thích nghi, cảm xúc, giá trị; động lực/phong cách/lãnh đạo/tập thể/chuyên môn/cạnh tranh/thuận–trở; tạo dựng/phong cách dùng/tích lũy/tài–quan/giới hạn; gắn bó/kỳ vọng/độc lập–gắn bó/thuận–căng; giai đoạn, Mệnh–Thân–đại hạn, phản tư). Khía cạnh nhạy cảm (tiền, hôn nhân, gia đình, sức khỏe, tuổi thọ) luôn được đóng khung “theo cách luận truyền thống (không phải dự báo)” — bộ kiểm tra chặn nếu thiếu.

Quan hệ hỗ trợ: `supports`, `qualifies`, `contradicts`, `conditions`, `amplifies`, `mitigates`, `elaborates`, `depends_on` (gốc dữ kiện chồng nhau).

---

## 3. Suy luận tổng hợp (Phase 3)

1. **Thu thập**: chỉ finding verified; guard áp dụng; finding nháp, finding bị loại và finding chưa ánh xạ được đếm riêng và nêu trong câu giới hạn.
2. **Gom nhóm**: một mệnh đề = một khái niệm ở một cung.
3. **Khử trùng**: bằng chứng cùng gốc dữ kiện chuẩn hóa = **một** căn cứ dù nhiều sách/quy tắc; gốc chồng sao với gốc trước tính **0,5** (không độc lập). Văn bản nói đúng điều đó: “hai câu cùng chỉ về đây… vì chung dữ kiện gốc, đây là một căn cứ được nhìn từ hai phía”.
4. **Giải quyết mâu thuẫn** (chỉ cho cặp `contradicts`, xét mọi cặp gốc):
   - `refinement` — điều kiện bên này chứa trọn bên kia: “Khảo Luận ghi … cho trường hợp chung (Cự Môn thủ Mệnh); Thực Hành, khi xét riêng Cự Môn ở vị trí hãm — đúng với lá số này — lại ghi … Điều kiện riêng điều chỉnh chứ không xóa nhận định chung.”
   - `both_hold` — hai điều kiện khác nhau, cùng thỏa: nêu cả hai, nói rõ sách không xếp thứ tự; nếu khác cung, nêu mỗi cung nói về chủ đề gì.
   - `school_divergence` / `unresolved` — cùng điều kiện, hai sách / một sách đọc ngược: báo đúng là chưa phân xử. Bộ kiểm tra **bắt buộc** câu này xuất hiện nếu hai mệnh đề được kể.
   - Năng lực ↔ cách biểu hiện, khuynh hướng ↔ hoàn cảnh, bên trong ↔ bên ngoài, mặt mạnh ↔ thái quá, tạo ra ↔ giữ lại: các **khung** trong `relations.json` (`qualifies`). Khung là của hệ thống (`he_thong`), trừ khi **chính câu sách ghép hai ý** (“nghĩa khí nhưng nóng nảy”, KL) — khi đó câu được trích và basis là `sach`; nếu chỉ có tiền lệ ở điều kiện khác thì nói rõ “khung đọc tham khảo”.
   - **Giảm nhẹ có nguồn**: mệnh đề `rescue` (ví dụ TH tr.88 “Cự Môn hãm ở Thìn/Tuất nhưng hóa Lộc (tuổi Tân) thì vẫn khá”) làm nhẹ các mệnh đề kết quả cùng cung đứng trên cùng sao; câu sách được trích nguyên văn đã diễn giải.
5. **Ưu tiên**: `trọng số cung với chương × Σ độc lập·(1 + neo + độ cụ thể) + 0,5·(số sách − 1)`; neo 1 nếu dựa trên chính tinh/Tứ Hóa, 0,5 lục cát/lục sát/Lộc/Mã, 0,25 phụ tinh khác. Chỉ dùng để **xếp thứ tự trình bày**; mọi thành phần được trả trong `salience_parts`; giao diện ghi rõ “không phải xác suất”.
6. **Đồ thị lập luận**: Theme → trọng tâm → củng cố → đối trọng → điều kiện, mỗi nút mang mã quy tắc và điều kiện thật trên lá số (tab “Đồ thị lập luận” ở chế độ Chuyên sâu).

Thống kê 200 lá số ngẫu nhiên (mỗi lá số trung bình): 10,1 cặp `both_hold`, 8,3 `qualifies`, 8,4 `supports`, 0,8 `refinement`, 0,34 `mitigates`, 0,05 `unresolved`. Thời gian: trung vị 54 ms, p95 79 ms / lá số.

---

## 4. Ngữ pháp tường thuật tiếng Việt (Phase 4)

`Semantic IR → Discourse Planner → Proposition Selection → Sentence Planner → Linguistic Realizer → Narrative Validator`.

- **Kế hoạch đoạn** (mỗi chủ đề): nhận định trung tâm → căn cứ → củng cố → đối trọng + cách tương tác → điều kiện/giảm nhẹ → câu tự phản tư (chỉ khi có căn cứ cho sự căng; nhãn `he_thong`). Không đủ bằng chứng thì không có phần đó.
- **Cấu trúc câu** theo chức năng diễn ngôn: nguyên nhân–kết quả, bổ sung, tương phản–nhượng bộ, điều kiện–hệ quả, chung–riêng, so sánh–phân biệt, tổng hợp. Mỗi chức năng có 2–4 cách diễn đạt; chọn bằng hash ổn định theo nội dung và **bỏ qua cách mở câu vừa dùng** trong chương.
- **Thứ tự kể**: khi trọng tâm là “mặt thái quá” của một khung, mở bằng mặt năng lực/mặt mạnh rồi mới đến mặt thái quá.
- **Tham chiếu**: điều kiện được gọi lại (“cùng điều kiện ấy”) chỉ từ câu ngay sau trong cùng đoạn; hai căn cứ luôn được nêu tên rõ.
- **Cấp chương**: đoạn đầu nêu dữ kiện; các đoạn sau mở như phần tiếp nối (“Chuyển sang…”, “Ở một lớp khác…”); một mệnh đề chỉ được kể đầy đủ một lần trong chương; một cặp khái niệm chỉ được giải thích một lần; đoạn liên cung; đoạn kết tổng hợp + giới hạn.
- **Bộ kiểm tra văn bản** (`grammar.validate`): câu nội dung không có truy vết → bỏ; từ ngữ phán quyết (chắc chắn, định mệnh, tai họa, sẽ bị, tuyệt đối…) → bỏ; câu lặp → bỏ; nhận định chỉ có ở dạng điều kiện mà câu viết như nét cố định → báo; khía cạnh nhạy cảm thiếu khung → báo; mâu thuẫn thật chưa kể → báo. Nguyên tắc: **hạ cấp bằng cách bớt chữ**, không bao giờ viết mạnh hơn. Trên 200 lá số sau khi sửa nguồn: còn 3 câu lặp bị lược (0 câu không truy vết, 0 từ cấm, 0 khía cạnh nhạy cảm thiếu khung).

Phân bố nguồn của câu (200 lá số): 53% `sach`, 5% `dieu_kien`, 29% `he_thong`, 13% `tinh_toan`. Ở chế độ Chuyên sâu, câu `he_thong` được gạch chấm; nhấn vào câu bất kỳ hiện mã quy tắc sinh ra nó.

---

## 5. Liên cung và theo chương (Phase 5–6)

- **Bản Mệnh** dựng theo **sao trục** của cung Mệnh (chính tinh → sao hóa tại Mệnh → lục sát/lục cát/Hồng–Đào), gom các nhận định của mỗi sao **xuyên lĩnh vực**, nêu quan hệ chung–riêng và câu giảm nhẹ có nguồn. Lá số tham chiếu: “Trục thứ nhất… Cự Môn (hãm) thủ Mệnh … về tính cách, sự sắc sảo trong suy nghĩ nhưng cũng thị phi… Khảo Luận ghi … cho trường hợp chung, còn Thực Hành khi xét riêng Cự Môn ở vị trí hãm … nghiêng về sự suy xét kém sáng … Thực Hành có ghi một điều kiện làm nhẹ: ‘… thì vẫn khá’. Lớp thứ hai đến từ Hóa Lộc tại Mệnh … Khảo Luận và Thực Hành, khi xét riêng Hóa Lộc ở Mệnh nhưng đóng Tứ Mộ, lại nghiêng về sự eo hẹp tài chính…”. Sau đó là nhịp đời và Thân.
- **Lăng kính liên cung** chỉ nói khi có căn cứ: (1) dữ kiện hình học (cung nằm trong tam phương của Mệnh hay không; Thân cư đâu), (2) quan hệ tường minh giữa mệnh đề **ở các cung khác nhau** trong lăng kính, giới hạn theo lĩnh vực trọng tâm của chương, (3) cùng một lĩnh vực lặp ở nhiều cung (cùng chiều / khác chiều). Không có gì thì nói “bộ quy tắc hiện có không cho thấy điểm giao nhau đủ căn cứ”.
- **Đại hạn**: vị trí (đại hạn, tiểu hạn, lưu Thái Tuế) → những gì nguyên cục ghi ở cung đại hạn (và mâu thuẫn giữa chúng nếu có) → liên hệ với Mệnh/Thân qua quan hệ tường minh → Tứ Hóa theo can đại hạn đáp cung nào, đặt cạnh nhận định nguyên cục với lời nói rõ **không có luật giao thoa** → lời Khảo Luận theo sao hóa lưu niên. Năm trước đại hạn đầu: nói rõ chưa vào đại hạn.
- **Tổng quan** (3–5 đoạn): dữ kiện Mệnh/Thân/Cục → hình ảnh con người (hai chủ đề nổi nhất của Tính cách + nét đi kèm và cách chúng tương tác) → công danh & tài chính (cả hai chiều) → đời sống & quan hệ → giới hạn (số quy tắc đã dùng / nháp / chưa ánh xạ, phân loại các chỗ trái chiều, không có điểm số).
- **Cách cục**: 6 cấu trúc của lớp v0 viết thành đoạn (điều kiện thỏa/chưa thỏa, nâng, phá, cứu, mức đối chiếu).

---

## 6. Kiểm thử

`engine/tests/test_synthesis_engine.py` (38 test): cờ/404 và giữ nguyên `/api/reasoning`, `/api/analysis`, `/api/chart`; không có thư viện LLM; toàn vẹn từ điển; tách câu sách; so khớp dài nhất/phủ định/câu khuyên; guard trên lá số tham chiếu (Tứ Mộ, Hồng–Không, Quan Phủ, cấu trúc lặp, cặp sách “nhưng”, điều kiện thật); độc lập căn cứ; 5 loại mâu thuẫn; văn bản lá số tham chiếu (chung–riêng Cự Môn, khung Kình/Hỏa, câu trích KL, câu giảm nhẹ TH, thứ tự sao trục); chương Tính cách dùng Mệnh; bất biến trên 25 lá số (truy vết ⊆ quy tắc đã kích hoạt và verified, không từ cấm, không câu lặp, mỗi mệnh đề một lần, khung nhạy cảm); tất định; không độn chữ khi thiếu bằng chứng; độ phủ ≥ 90%.

Toàn bộ `engine/tests` sau lượt sửa cuối: **1288 passed, 1 skipped, 2 xfailed**.

Kiểm tra trên trình duyệt (cờ bật, cổng 8767): mục tổng hợp hiện ở đủ 8 chương; chế độ Chuyên sâu hiện chú thích nguồn, đồ thị lập luận, kiểm tra văn bản; nhấn câu hiện truy vết ngay dưới đoạn; màn hình 375 px không cuộn ngang; không lỗi console mới (404 duy nhất là `/api/growth/profile`, tính năng khác đang tắt cờ).

---

## 7. Giới hạn và việc chưa làm

| Mục | Lý do |
|---|---|
| Từ điển khái niệm và khung quan hệ do hệ thống định nghĩa | Không có sách nào phân loại nhận định theo khía cạnh; mọi khung được ghi `he_thong` và hiển thị như vậy. Nên có người am hiểu duyệt `concepts.json`/`relations.json` (mẫu ánh xạ để duyệt: `rule_audit.json → mapping_sample`). |
| Cụm danh từ (`np`) là cách diễn đạt của hệ thống | Lời sách giữ nguyên ở tầng bằng chứng và được trích khi dùng làm căn cứ ghép/giảm nhẹ; câu tổng hợp dùng cụm danh từ thận trọng, khái quát hơn câu sách. |
| Không sửa rule pack | Sửa sẽ đổi `/api/reasoning`; guard nằm ở lớp tổng hợp; đề xuất sửa (36 nhãn sai điều kiện, 14 nhãn tích cực cho quy tắc hạn chế, 4 phạm vi rộng, cơ chế nâng basis khi gộp thẻ) nằm trong `rule_audit.json`. |
| Bát Tự | Prompt chỉ nêu Tử Vi cho Phase 6 phần nhận được; Bát Tự chưa có lớp tổng hợp. |
| Phase 6 sau mục A và các phase sau | Prompt bị cắt. |
| Ngưỡng “hội/gặp”, Tuần/Triệt hại–cứu, Nhâm-Khoa, giao thoa đại hạn | Không có nguồn để phân xử; engine nêu hai chiều hoặc chỉ đặt cạnh nhau. |

## 7b. Sửa sau hai bản đánh giá (18/10/2026)

| Phát hiện của người đánh giá | Nguyên nhân trong mã | Đã sửa |
|---|---|---|
| “Hồng Loan gặp Thiên Không đồng cung hoặc xung chiếu” kích hoạt khi Thiên Không ở Tài Bạch | `TV_KL_AUX_HONG_KHONG` đọc `palace.tam_phuong_stars` | Rule pack: chỉ đồng cung hoặc `palace.rel.opp_stars` (KL tr.225); test âm/dương |
| “Quan Phủ và Thái Tuế đồng cung Mệnh” khi Thái Tuế ở Tật Ách | `TV_KL_AUX_QUAN_PHU_VIET` (chỉ kiểm Quan Phủ) dùng chung claim với quy tắc TH có cả Thái Tuế | Claim riêng `quan_phu_menh_mieng_tieng` với câu của chính quy tắc |
| “Lộc Mã giao trì … ở cung Mệnh” khi Lộc Tồn, Thiên Mã ở Tài Bạch | 3 quy tắc TH (Tài Bạch / Quan Lộc / Thiên Di) dùng chung nhãn của quy tắc ở Mệnh | 24 quy tắc có điều kiện thực, cung khác với quy tắc “chủ” của nhãn nay có claim + nhãn riêng lấy từ câu sách của chính chúng; quy tắc *hạn chế* vẫn dùng chung claim (để bộ giải quyết mâu thuẫn đánh dấu nhận định gốc là “bị giới hạn”) và hiển thị câu `limit:` riêng; công cụ kiểm toán nay bắt cả nhãn nêu sai cung |
| Thái Dương–Cự Môn “xung chiếu” | điều kiện đọc cả tam phương | Rule pack: `palace.rel.opp_majors` |
| “Tiền bạc đến tự nhiên, ít mất công lao khó nhọc” nằm dưới “Điểm cần cân nhắc” | bộ lọc từ khóa: “khó” khớp “khó nhọc” | `/api/claims` cấp `tone:<claim>` từ lớp ngữ nghĩa (có phủ định); câu thuận thuần không bị gập, câu hỗn hợp có từ khó vẫn gập |
| Chương Tính cách chỉ có “họ hàng đông đúc”, “làm bạn với quý nhân”; nét tính cách nằm ở Bản Mệnh | `PAL_CH` định tuyến theo cung | `/api/claims` cấp `facet:<claim>`; nhận định ở Mệnh/Phúc Đức đi theo ý nghĩa (tính cách → Tính cách, nghề → Công danh, tiền → Tài Bạch, gia đình → Quan hệ); cung khác giữ định tuyến theo cung |
| Tuổi mụ 38 / Tứ Hóa khác ở phần lưu niên | Khối “Chọn năm” hiển thị năm đã kéo thanh trượt, nhưng khi in thanh trượt bị ẩn nên không thấy năm | Kết quả luôn ghi “Năm … · can chi · tuổi mụ …” và chú thích khi không phải năm hiện tại |
| PDF: trang 1 gần trống, trang gần trống giữa bài, trang “Trưởng thành” không có nội dung | quy tắc in `.pane+.pane .r-sec:first-child{break-before:page}` đẩy Bát Tự sang trang 2 trên bố cục mới; cả chương bị cấm ngắt trang; `print.js` đặt `data-view` lên `#tuvi-host` thay vì `.tv-stage` (bảng 12 cung in ra trắng); phần đệm cuối Bát Tự tràn trang | Sửa các quy tắc in, `print.js` trỏ đúng phần tử, ẩn khung Trưởng thành khi tính năng tắt/rỗng. Kiểm bằng Chrome headless trên 3 lá số: 20 trang, không trang trống |

Các nhận xét về chiều sâu tổng hợp (danh sách nhận định rời rạc, mâu thuẫn không giải thích) là phần lớp `/api/synthesis` giải quyết; lớp này vẫn **tắt** trên production cho tới khi bật cờ `TVBT_DEEP_INTERPRETATION`.

## 8. Bật thử

```bash
TVBT_DEEP_INTERPRETATION=1 .venv/bin/python -m uvicorn tvbt.api:app --app-dir engine --port 8767
```
Hoặc cấu hình `tvbt-web-synthesis` trong `.claude/launch.json`. Kiểm toán bộ quy tắc: `.venv/bin/python tools/semantic_audit.py --out docs/synthesis/rule_audit.json`.
