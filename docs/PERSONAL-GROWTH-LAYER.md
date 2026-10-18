# Tầng Trưởng thành (Personal Growth & Life Guidance)

Trạng thái: **đã triển khai sau cờ `TVBT_GROWTH` (mặc định OFF)**. Chưa commit, chưa merge, chưa deploy. Không thay thế, viết lại hay xóa phần luận giải nào hiện có. Với cờ tắt, mọi `/api/growth/*` trả 404 và các endpoint cũ giống từng byte (có test).

## 1. Audit kiến trúc hiện tại (điểm tựa của tầng mới)

| Lớp hiện có | Vai trò | Tầng Trưởng thành dùng thế nào |
|---|---|---|
| `tuvi.py`, `bazi.py`, `temporal.py` | Tính lá số, đại hạn, lưu niên (đã đối chiếu sách) | Đọc **dữ kiện**: sao cung Mệnh/Thân/Phúc Đức, Tứ Hóa theo cung, Tuần/Triệt, Mệnh–Cục, Nhật Chủ, tám chữ, đại hạn/đại vận hiện tại |
| `bazi_deep/pipeline.py` | Khí thế, cách cục, dụng thần (quy tắc **draft**) | Mức vượng/nhược (kể cả khi ở vùng biên: hai cách đọc, không chọn), phép phù ức |
| `analysis.py` (`GROUPS`, `PALACE_ROLE`) | Bốn nhóm sao (Khảo Luận pp.50-51), vai trò 12 cung (pp.214-220) | Trục "hành động ↔ lý luận" để tìm mâu thuẫn nội tâm; lĩnh vực đời sống của từng cung |
| `data/star_profiles.json`, `data/tu_hoa_vi.json` | Hồ sơ sao (TH pp.29-48), ý nghĩa Tứ Hóa và lời khuyên theo can năm (KL pp.195-197) | Tầng **biểu tượng truyền thống** có trang sách |
| `reasoning/`, `nlg/`, `synthesis/` | Suy diễn theo quy tắc, luận giải 10 chương (deep-reading, cờ riêng) | **Không đụng tới.** Tầng mới chỉ đọc lá số, không thêm hay sửa quy tắc nào |
| Nguyên tắc dự án | Không LLM, không lưu dữ liệu ngày sinh, mọi nhận định truy vết được | Giữ nguyên: đối thoại là tất định; nhật ký chỉ ở trình duyệt; mọi nhận định ghi căn cứ |

## 2. Kiến trúc mới

```
 tuvi / bazi / bazi_deep / temporal (không đổi)
          │  chỉ đọc
          ▼
 growth/signals.py ── anchors: {id, câu dữ kiện, check máy kiểm được}
          │
          ▼
 growth/profile.py ── lessons · blind_spots · compass(4 lĩnh vực) · stage · practices · control_bias
          │                     ▲ nội dung: data/growth/{stars,palaces,bazi,concepts}.json (review được)
          ├─► growth/navigator.py   Khi bế tắc (người đọc tự xếp vùng; máy chỉ gợi ý)
          ├─► growth/decide.py      La bàn quyết định (phản chiếu điểm người đọc tự chấm; không chọn)
          ├─► growth/journal.py     Đối chiếu nhật ký (stateless)
          └─► growth/dialogue.py    Đối thoại (từ khóa trong data/growth/dialogue.json; crisis → fate → intent)
 growth/text.py ── bỏ dấu để so khớp, lint chống định mệnh / quyết định thay / sáo rỗng
 growth_api.py ── POST /api/growth/{profile,navigate,compass,journal-review,dialogue}, sau cờ TVBT_GROWTH
 web/js/growth.js ── tab "Trưởng thành" (ẩn nếu server tắt cờ), nhật ký + bài tập trong localStorage
```

### Mỗi nhận định có cấu trúc cố định

```
id, kind (lesson | blind_spot), title, domains, priority
anchors      → id dữ kiện lá số (mỗi cái có câu chữ + check độc lập)
layers
  bieu_tuong → text, source ∈ {sach (có trang), pho_thong, he_thong}, cites
  tam_ly     → text, concept {name, ref}, note "lá số không chứng minh khái niệm này…"
  doi_song   → text
exercise     → questions (≥2), scenario {situation, try}, practices [{days 7–30, action, track}]
shadow       → (điểm mù) conflict, habit, signals (cách nhận diện), adjust
```

Phân biệt ba tầng là yêu cầu cứng: biểu tượng truyền thống (điều sách/truyền thống nói), tâm lý học (một khái niệm có tên và tác giả, đặt **cạnh** biểu tượng như giả thuyết), đời sống thực (hành vi, tình huống, việc thử). Hiệu ứng Barnum được nêu ngay đầu tab và trong bản đối chiếu nhật ký.

## 3. Bảy tính năng → nơi thực hiện

| # | Tính năng | Căn cứ lá số | Nơi |
|---|---|---|---|
| 1 | Bài học cuộc đời | Sao cung Mệnh (hoặc sao mượn khi vô chính diệu), nhóm sao KL pp.50-51, lời khuyên theo can năm KL pp.195-197, Hóa Kỵ/Khoa theo cung, Thân cư, Nhật Chủ, phù ức | `profile.lessons` |
| 2 | Điểm mù | Bóng tối của sao Mệnh; hai sao Mệnh kéo hai hướng; Mệnh ↔ Thân/Phúc Đức khác nhóm hành động; Lộc–Kỵ đồng cung; Tuần/Triệt ở Mệnh (nêu cả hai chiều, R07); Mệnh–Cục; khí thế × nhóm Thập Thần nặng; đối chiếu hai hệ; ngũ hành thiên/vắng | `profile.blind_spots` |
| 3 | Khi bế tắc | 4 bước (gọi tên → phân vùng → câu hỏi đúng → hành động nhỏ); kiểm tra thiên hướng kiểm soát theo sao Mệnh; câu hỏi từ cung liên quan; lăng kính giai đoạn | `navigator.navigate` |
| 4 | La bàn cuộc đời | Xu hướng theo sao ở Mệnh và cung lĩnh vực (Quan Lộc, Tài Bạch, Phu Thê, Phụ Mẫu…), Tứ Hóa trong cung đó; giá trị hình tượng vs giá trị người đọc chọn; bảng điểm người đọc tự chấm; 4 công cụ ra quyết định | `profile.compass`, `decide.decide` |
| 5 | Bài tập thực hành | Mỗi nhận định: câu hỏi phản tư, tình huống, việc 7/14/30 ngày + cách theo dõi; trình theo dõi bài tập | `exercise`, `profile.practices`, UI |
| 6 | Nhật ký trưởng thành | Ghi chép gắn với nhận định + mức "đúng với tôi"; xu hướng tâm trạng, chuỗi ngày làm bài tập, sự thay đổi từ ngữ gắn với từng điểm mù | `journal.review`, localStorage |
| 7 | Đối thoại với lá số | Intent (mắc kẹt / thay đổi / điểm mạnh / điểm mù / bản chất) × lĩnh vực; xoay vòng nhận định (`exclude`); dùng hoàn cảnh và giá trị người đọc tự chia sẻ | `dialogue.answer` |

## 4. Nguyên tắc an toàn và không áp đặt

1. **Không dự báo**: câu hỏi "bao giờ / có … không" về sự kiện → trả lời giới hạn của lá số, không ghép nội dung lá số.
2. **Không quyết định thay**: câu hỏi "có nên…" → nói rõ quyết định là của người đọc, chuyển sang khung La bàn. La bàn không bao giờ nêu tên lựa chọn nào trong lời bình (có test).
3. **Khủng hoảng trước mọi thứ**: từ khóa tự hại → chỉ trả lời an toàn: cấp cứu 115, đường dây "Ngày Mai" 096 306 1414 (nguồn: HelloBacsi, Find A Helpline; UI nhắc kiểm tra số trên trang chính thức), findahelpline.com khi ở nước ngoài. Dấu hiệu căng thẳng kéo dài → gợi ý gặp chuyên môn.
4. **Người đọc là bằng chứng mạnh nhất**: nhận định bị đánh dấu "không đúng" ≥60% → bản đối chiếu nói rõ trải nghiệm được ưu tiên hơn lá số.
5. **Lint ngôn ngữ** (`text.lint`, theo ranh giới từ): cấm cụm định mệnh ("chắc chắn sẽ", "đã an bai", "định sẵn"…), quyết định thay ("bạn nên chọn"…), khẩu hiệu sáo rỗng ("hãy luôn tích cực", "hãy là chính mình"…). Chạy trên mọi đầu ra của 120 lá số.
6. **Riêng tư**: nhật ký và bài tập nằm trong localStorage, khóa bằng hash của ngày giờ sinh (không lưu ngày giờ thô); xuất/nhập JSON; nút xóa toàn bộ. Server chỉ tính khi được gọi, không ghi gì.
7. **Nguồn trung thực**: chỉ gắn `sach` khi có trang; phần do hệ thống đặt ra ghi `he_thong`; bazi_deep là draft nên mọi nhận định Bát Tự từ đó ghi rõ nháp và nêu hai cách đọc khi ở vùng biên.

## 5. QA và kiểm thử cá nhân hóa (`engine/tests/test_growth.py`, 35 test)

| Nhóm | Điều được khóa |
|---|---|
| Cờ | OFF → 404 cho cả 5 route; `/api/chart`, `/api/reasoning`, `/api/analysis`, `/api/year` giống từng byte khi bật/tắt; đầu ra tất định |
| Căn cứ | 120 lá số ngẫu nhiên (seed cố định): mọi nhận định có anchor, mọi anchor được **kiểm độc lập** trên lá số (`verify_anchor`), mức khí thế khớp `bazi_deep` |
| Ba tầng | 3 tầng khác nhau, không rỗng; `sach` ⇒ có trang; tầng tâm lý có tên khái niệm, tác giả và câu "không chứng minh" |
| Thực hành | ≥2 câu hỏi, tình huống + "thử", bài tập 7–30 ngày có cách theo dõi |
| Cá nhân hóa | Bài học sao = đúng tập sao Mệnh (hoặc sao mượn đúng cung đối diện khi vô chính diệu); lời khuyên can năm khớp từng câu sách; cung Hóa Kỵ khớp lá số; Lộc–Kỵ đồng cung đúng khi và chỉ khi cùng cung; xu hướng La bàn chỉ nêu sao thật sự ở cung đó; Jaccard trung bình < 0.6, >90% hồ sơ có văn bản khác nhau; đổi giờ sinh đổi bài học hàng đầu (≥4 kiểu trong 12 giờ) |
| Ca kiểm tay | Lá số mẫu 17/05/1990 10:30 nam: Vũ Phủ cư Mệnh, Lộc–Kỵ cùng Phụ Mẫu, Thân cư Phu Thê, tuổi Canh, thiên hướng "gánh/kiểm soát", đại hạn 2026 ở Điền Trạch |
| Đối thoại | 4 intent; cùng câu hỏi + hoàn cảnh khác ⇒ nhận định khác (Vũ Khúc vs Thiên Phủ); hỏi tình cảm ⇒ dùng Thân cư Phu Thê và sao Phá Quân của chính cung Phu Thê; xoay vòng `exclude`; ranh giới fate/decision; crisis chỉ trả về an toàn |
| Bế tắc | Máy **không** di chuyển mục người đọc đã xếp; chỉ gợi ý cho mục "chưa rõ"; "thăng tiến" không còn khớp nhầm "tiền" |
| La bàn | Tổng điểm = đúng điểm người đọc chấm; giá trị lạ bị bỏ; lời bình không nhắc tên lựa chọn; ghi chú khi điểm sát nhau |
| Nhật ký | Xu hướng tâm trạng, chuỗi ngày dài nhất, dịch chuyển từ ngữ, ngưỡng "mới một lần", ưu tiên trải nghiệm, stateless |
| Dữ liệu | 14 sao đủ trường, không trùng văn bản giữa các sao; mọi từ khóa ≥2 âm tiết và đã bỏ dấu; phủ đủ mọi họ nhận định trong quần thể test |

### Lỗi thật do QA phát hiện và đã sửa

1. **Từ khóa một âm tiết sau khi bỏ dấu nhập nhằng**: "thăng tiến" khớp "tiền" (Vũ Khúc) → mọi từ khóa phải ≥2 âm tiết, có test hồi quy.
2. **Lint khớp chuỗi con**: "thấy là chính mình" khớp "hãy là chính mình" → lint theo ranh giới từ.
3. **Code chết**: ngưỡng chênh "hành động" 1.5 không bao giờ đạt vì cấu trúc an sao (Mệnh và Thân/Phúc Đức chỉ chênh tối đa ~1 bậc nhóm) → hạ về 1.0; test phủ nhánh bắt được.
4. **Kể trùng**: Thân cư Phúc Đức sinh hai điểm mù cho cùng một cung → chỉ kể một lần.
5. UI: ngày nhật ký dùng UTC; nhận xét "nhiều lần đúng" khi mới có 1 lần; tiêu đề điểm mù lặp lại nội dung.

### Kết quả chạy

- `tests/test_growth.py`: 35 passed.
- Toàn bộ suite, cờ tắt: 1250 passed, 1 skipped, 2 xfailed (trước khi thêm tầng mới: 1215 passed). Cờ bật (`TVBT_GROWTH=1 TVBT_DEEP_INTERPRETATION=1`): 1250 passed, 1 skipped, 2 xfailed.
- Fuzz 400 lá số (1920–2040, cả hai giới): 0 lỗi, 0 anchor sai, 0 cụm bị cấm.
- Trình duyệt (server cục bộ với `TVBT_GROWTH=1`, cấu hình `tvbt-web-growth` cổng 8766): tab hiện sau khi lập lá số; Đối thoại, Khi bế tắc, La bàn, Bài tập, Nhật ký + Đối chiếu đều chạy; 375px không tràn ngang; không lỗi console.

## 6. Bật thử cục bộ

```bash
cd engine && TVBT_GROWTH=1 ../.venv/bin/python -m uvicorn tvbt.api:app --port 8766
```

Production: Worker chuyển `/api/*` vào container; cờ phải được đặt trong môi trường container mới bật. Chưa thay đổi `Dockerfile`, `wrangler.jsonc`, `render.yaml`.

## 7. Giới hạn đã biết và hướng tiếp

- Nội dung "đời sống" và "tâm lý" của 14 sao do hệ thống soạn (`he_thong`), **chưa được nhà tâm lý học review**; nên có review chuyên môn trước khi bật cho người dùng.
- Đối thoại dựa trên từ khóa: hiểu được các câu hỏi phổ biến, không hiểu ngữ cảnh phức tạp; câu lạ → hướng dẫn hỏi lại. Nếu sau này muốn dùng mô hình ngôn ngữ, cần cờ riêng và giữ nguyên các ràng buộc ở mục 4 (đi ngược nguyên tắc "không AI bịa" hiện tại, nên là quyết định của chủ dự án).
- Sao phụ (Tả Hữu, Xương Khúc, Kình Đà, Hỏa Linh, Không Kiếp…) chưa vào tầng Trưởng thành; mới dùng 14 chính tinh, Tứ Hóa, nhóm sao, ngũ hành, khí thế.
- Lăng kính giai đoạn chỉ dùng đại hạn và đại vận; chưa dùng lưu niên/tiểu hạn để tránh trượt sang "dự báo năm".
- Nhật ký chỉ ở một trình duyệt; đồng bộ nhiều thiết bị cần lớp tài khoản (hiện dự án không có).
