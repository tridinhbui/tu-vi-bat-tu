# Cung hoàng đạo (12 cung hoàng đạo phương Tây), bậc 1

Ngày: 2026-10-25. Phạm vi: bậc 1, miễn phí: phần tính toán, và phần luận theo sách (Alan Leo, Lilly, Ptolemy), mỗi câu ghi trang in (mục 3).

Quy ước chữ: luôn viết "cung hoàng đạo", không viết "cung" trơn (trên trang này "cung" là cung của lá số Tử Vi). Không dùng chữ "AI" trong giao diện mới.

## 1. Đã làm gì

| Phần | Tệp | Ghi chú |
|---|---|---|
| Tính toán | `engine/tvbt/hoang_dao.py` | `sun_sign(nb)`, `sun_sign_at(utc, zone)`, `lookup(...)`, `sign_periods(...)`, `ingresses(year)` |
| API | `engine/tvbt/api.py` | khối `western` trong `POST /api/chart`; `GET /api/hoang-dao?y=&m=&d=&h=&mi=&tz=` |
| Thẻ trong lá số | `engine/web/js/hoangdao.js`, `index.html`, `js/app.js`, `css/app.css` | chip trong `#res-hl`, thẻ ở đầu khung Tử Vi (`#hoangdao-host`, nền giấy, viền son, không phải dải tối) |
| Trang tĩnh | `engine/tvbt/sitegen.py` → `tools/build_site.py` | `/bai-viet/hoang-dao/` + 12 trang `/bai-viet/hoang-dao/<slug>/`, trang tra `/cung-hoang-dao/` (`js/hoangdao_page.js`); NAV, chân trang, sitemap, JSON-LD |
| Luận giải theo sách | `tools/data/hoang_dao_rules.json` (217 mục), `tools/build_hoang_dao_pack.py` → `engine/data/hoang_dao/pack.json`, `quotes.json` | không phải rule pack, không nằm trong `PACKS` của loader |
| Đọc sách tiếng Anh | `tools/book_text.py` | mã sách `AL`, `CA`, `TB`; `EN_PAGE_RANGES`, `en_pdf_page`, `en_page_text`, `en_clean`, `en_key`, `en_match` |
| Kiểm thử | `engine/tests/test_hoang_dao.py` | xem mục 4 |
| Bảo mật chia sẻ | `src/account/shares.ts` | link chia sẻ ẩn ngày sinh: Worker bỏ hẳn khối `western` (giờ vào cung hoàng đạo và số giờ tới ranh giới đủ để suy ra ngày sinh) |

Chip và thẻ không hiện khi link chia sẻ ẩn ngày sinh (`req.day == null`), và bị ẩn khi bật "Ẩn ngày giờ sinh khi tải" (`body.hide-birth`). Thẻ có trong bản in / PDF (khung Tử Vi được in; `@media print` giữ thẻ liền một khối, bỏ đường link). Chip nằm trong `.atl-side .res-hl`, vốn đã ẩn khi in.

Nội dung thẻ: tên cung hoàng đạo + glyph SVG vẽ tay (không dùng ký tự ♈…♓), tên Latin, khoảng thời gian Mặt Trời ở cung hoàng đạo đó (giờ nơi sinh, có ghi UTC±), khoảng ngày ước lượng (ghi rõ "ước lượng"), ghi chú "sinh sát ranh giới" nếu cách mốc dưới 24 giờ, nguyên tố / tính chất / chủ tinh kèm trang, năm ý tính cách đầu kèm trang, và một câu phân biệt với mười hai cung của lá số Tử Vi.

## 2. Cách tính thời điểm Mặt Trời vào cung hoàng đạo

- Cung hoàng đạo thứ i (0 = Bạch Dương) là đoạn hoàng kinh biểu kiến của Mặt Trời từ 30i° đến 30i+30°.
- Mười hai mốc 0°, 30°, …, 330° chính là mười hai **trung khí** mà `engine/tvbt/astro.py` đã tính (sxtwl, đổi sang UTC): Xuân Phân 0° Bạch Dương, Cốc Vũ 30° Kim Ngưu, Tiểu Mãn 60° Song Tử, Hạ Chí 90° Cự Giải, Đại Thử 120° Sư Tử, Xử Thử 150° Xử Nữ, Thu Phân 180° Thiên Bình, Sương Giáng 210° Bọ Cạp (Thiên Yết), Tiểu Tuyết 240° Nhân Mã, Đông Chí 270° Ma Kết, Đại Hàn 300° Bảo Bình, Vũ Thủy 330° Song Ngư. Công thức: với `jqIndex` chẵn của sxtwl (0 = Đông Chí), chỉ số cung hoàng đạo = ((270 + 15·jq) mod 360) / 30.
- Giờ sinh đi qua `calendar_core.normalize` như lá số, nên giữ múi giờ lịch sử: miền Nam UTC+8 từ 31/12/1959 đến 13/6/1975 (`Asia/Ho_Chi_Minh`), miền Bắc theo `Asia/Hanoi` (backzone). Thời điểm sinh tuyệt đối (UTC) được so với các mốc; không có bảng ngày nào quyết định cung hoàng đạo. Bảng "khoảng 21/3–19/4" chỉ là nhãn ước lượng.
- Không dùng giờ Mặt Trời thực (true solar time) cho việc này: mốc vào cung hoàng đạo là một thời điểm tuyệt đối, chỉ phụ thuộc giờ dân sự đổi ra UTC.
- `cusp_hours` = số giờ tới mốc gần hơn (mốc vào hoặc mốc rời). Dưới 24 giờ: thẻ ghi "Sinh sát ranh giới cung hoàng đạo: Mặt Trời vào X lúc HH:MM ngày …, N giờ trước/sau giờ sinh, nên cung hoàng đạo là Y." Một kết luận duy nhất; dưới một giờ thì ghi cả giây.
- Đối chiếu độc lập: PyEphem, hoàng kinh biểu kiến địa tâm của Mặt Trời theo xuân phân thật của ngày (`Sun.compute(d, epoch=d)`, `g_ra/g_dec` → `Ecliptic`), tìm lúc cắt bội số 30° bằng chia đôi. Trên các năm 1900–2049 lệch với sxtwl dưới 0,5 phút (ngưỡng kiểm thử 2 phút). Lưu ý: dùng toạ độ J2000 hoặc `hlon` sẽ lệch tới ~15 phút (thiếu chương động và quang sai), đừng dùng để đối chiếu.

Khối `western` trong `/api/chart`:

```
{ sun_sign: {index, slug, name, alt_name, label, latin, longitude_from, longitude_to, approx_dates, approx_dates_note},
  ingress: {sign, slug, term, longitude, utc, local, utc_offset, text, text_seconds},
  next_ingress: {…như trên},
  cusp_hours, near_cusp, nearest_boundary, note, readings: [], reading_status }
```

`GET /api/hoang-dao` trả cùng khối đó; 422 khi ngày không tồn tại, giờ rơi vào khoảng nhảy DST, múi giờ lạ hoặc năm ngoài 1900–2049. Có `cache-control: public, max-age=86400` (kết quả chỉ phụ thuộc truy vấn). Lưu ý: ngày giờ sinh nằm trong URL truy vấn của GET này (theo kế hoạch đã duyệt); trang tra không ghi ngày giờ sinh vào địa chỉ trang.

## 3. Phần luận giải theo sách (2026-10-25)

Sách chủ sở hữu chọn, PDF ở `$TVBT_BOOKS_DIR` (mặc định `~/Downloads`), cả ba đều có lớp chữ OCR. Cả ba thuộc phạm vi công cộng (xuất bản 1647, 1822, 1910). Ghi trong `engine/data/sources.json`:

| Mã | Sách | Bản | Dùng cho | Trang in ↔ trang PDF (đo trên ảnh trang) |
|---|---|---|---|---|
| AL | Alan Leo, *Astrology for All* | tái bản lần 4, 1910; archive.org `dli.ernet.19807` | tính cách, khuynh hướng, nghề tác giả nêu; cũng nguyên tố và tính chất | tr. 5–48 = PDF − 15; tr. 51–62 = PDF − 13 (bản quét thiếu tr. 49–50 và 63–64: độ lệch trôi, không phải một hằng số) |
| CA | William Lilly, *Christian Astrology* | bản in đầu 1647; Wellcome `b30338724` | chỉ phân loại: tam hợp, chuyển động / cố định / chung, nhà của hành tinh | tr. 61–103 = PDF − 34 (con số "+35" báo trước đó dư một) |
| TB | Ptolemy, *Tetrabiblos* | bản dịch J. M. Ashmand, 1822 (không phải Robbins); Wellcome `b29293066` | chỉ phân loại: nhà của hành tinh (tr. 42–43), tam hợp (tr. 44–45), cung hoàng đạo chí / phân điểm (tr. 34–35) | tr. 4–54 = PDF − 36 (con số "+37" báo trước đó dư một) |

`tools/book_text.py`: `EN_PAGE_RANGES` (chỉ những khoảng đã đo; trang ngoài khoảng bị từ chối), `en_pdf_page`, `en_page_text`, `en_clean` (chữ ghép, ngoặc cong, gạch nối cuối dòng kể cả dấu `¬`, khoảng trắng OCR), `en_key` (chỉ giữ chữ và số, nên khoảng trắng và dấu câu OCR không ảnh hưởng; với CA gộp f và s vì OCR đọc chữ s dài của bản 1647 thành f: "Seafon" = "Season"), `en_match` (khớp đúng trên khóa chữ; nếu không thì tìm cửa sổ gần đúng, đạt khi ≥ 90 % chữ trùng: OCR đôi chỗ đọc sai một chữ như "iouitulse" cho "impulse").

### Số câu

217 mục trong `tools/data/hoang_dao_rules.json`, tất cả `use: reading`, mỗi câu trích ≥ 6 từ và được kiểm trên đúng trang (179 khớp đúng, 38 khớp gần đúng do lỗi OCR, điểm thấp nhất 0,935; không câu nào trượt). Theo sách: AL 174, TB 28, CA 15. Theo chủ đề: tính cách 147, nghề 15, phân loại 55.

| Cung hoàng đạo | AL tính cách | AL nghề | AL phân loại | Lilly | Ptolemy |
|---|---|---|---|---|---|
| Bạch Dương | 12 | 2 | 1 | 2 | 3 |
| Kim Ngưu | 12 | 2 | 1 | 1 | 2 |
| Song Tử | 12 | 1 | 1 | 1 | 2 |
| Cự Giải | 13 | 1 | 1 | 2 | 3 |
| Sư Tử | 12 | 1 | 1 | 1 | 2 |
| Xử Nữ | 11 | 2 | 1 | 1 | 2 |
| Thiên Bình | 12 | 1 | 1 | 1 | 3 |
| Bọ Cạp | 14 | 1 | 1 | 1 | 2 |
| Nhân Mã | 13 | 1 | 1 | 1 | 2 |
| Ma Kết | 12 | 1 | 1 | 1 | 3 |
| Bảo Bình | 12 | 1 | 1 | 1 | 2 |
| Song Ngư | 12 | 1 | 1 | 2 | 2 |

Nguyên tố, tính chất, chủ tinh: cả 12 cung hoàng đạo đều có đủ ba mục, mỗi giá trị kèm mọi trang nêu nó (ví dụ Kim Ngưu: Đất [Alan Leo, tr. 16] [Lilly, tr. 94]; kiên định [Alan Leo, tr. 16] [Lilly, tr. 94]; Sao Kim [Lilly, tr. 94] [Ptolemy, tr. 43]). Bộ dựng dừng lại nếu hai sách cho hai giá trị khác nhau cho cùng một mục; hiện không có chỗ nào khác nhau.

### Hiển thị

- Thẻ trong lá số: nguyên tố, tính chất, chủ tinh kèm trang; năm ý tính cách đầu (theo thứ tự trang) dạng "… [Alan Leo, tr. 16]"; một câu nói rõ đây là khuynh hướng theo sách; liên kết "Đọc đủ N ý" tới trang cung hoàng đạo.
- Trang `/bai-viet/hoang-dao/<slug>/`: mục "Phân loại" (ba mục trên và các câu phân loại của Lilly, Ptolemy), "Tính cách và khuynh hướng", "Công việc tác giả cho là hợp", bảng giờ Mặt Trời vào/rời, "Nguồn của bài này" (sách, bản, trang). JSON-LD `Article` có `citation` ba sách.
- Trang `/bai-viet/hoang-dao/` ghi nguyên tố của từng cung hoàng đạo và danh sách nguồn.

### Đã bỏ ra (theo loại)

- Sức khỏe, cơ thể, bệnh tật: mọi đoạn bệnh của từng chương AL (đầu, cổ họng, tiêu hóa, tim, phổi, thận…), "Difeafes" của Lilly, "sickly Signe" (Song Ngư, Lilly tr. 99).
- Chết, tai nạn: "apoplexy and sudden death" (Kim Ngưu, tr. 17); "more liable than others to accident" (Nhân Mã, tr. 37).
- Hôn nhân, con cái: các đoạn "would marry well with…" của AL (tr. 15, 18, 20…), bảng "Harmonious signs for business, marriage" (tr. 61); "prone to many children" (Lilly, tr. 95).
- Tình dục, đam mê thể xác: Bọ Cạp "Ignorance and lust", "excesses of sensuality", "sex nature" (tr. 33–34); Sư Tử "very amative, with very strong passions", "pride, arrogance and extreme passion" (tr. 26, 59); Lilly "luxurious" (Bạch Dương) và các dòng về bộ phận sinh dục.
- Sự kiện, dự báo: Bọ Cạp "always mixed up in some tragedy" (tr. 34); Ma Kết "acquire riches… great wealth is often found associated with this sign" (tr. 40).
- Điều tác giả tự đánh dấu là chưa chắc: Song Ngư "If it be true that they come under the planet Neptune…" (tr. 47).
- Nhận xét kiểu 1910 về phụ nữ, chủng tộc, tôn giáo: Cự Giải "men become freemasons… women are drawn to mystical meetings", "Catholic faith" (tr. 22); Ma Kết và "the Hindus… lower castes" (tr. 41); Song Tử "The Hindus symbolise this sign by a beautiful woman" (tr. 56).
- Thông linh, ám nhập, rượu: Song Ngư "easily obsessed… draw many spirits", "take to drink" (tr. 46); các câu "clairvoyant", "magnetic healers", "mediums" khi là lời khẳng định năng lực siêu nhiên (giữ lại không câu nào).
- Hành tinh ở cung hoàng đạo khác, góc chiếu, nhà: toàn bộ chương XVII–XXIII của AL (Mặt Trăng trong các cung hoàng đạo, kết hợp Mặt Trời – Mặt Trăng, hành tinh trong cung hoàng đạo, cung mọc); các dòng "if the Lord of the Ascendant…" của Lilly; điểm vượng (exaltation) của Ptolemy.
- Ghi chú của người dịch Ashmand (chú thích chân trang, ví dụ bảng nhà ngày/đêm "from Whalley", tr. 43).

### Điều còn nghi ngờ / cần chủ sở hữu quyết

1. **Chủ tinh Bảo Bình**: bảng của Alan Leo (tr. 61) ghi Uranus; Ptolemy (tr. 42) ghi Sao Thổ (Lilly tr. 98 cũng là nhà của Sao Thổ, nhưng ký hiệu không đọc được ra chữ nên không trích). Hiện chỉ hiện Sao Thổ theo Ptolemy, vì bảng của Leo là ô bảng, không có câu ≥ 6 từ để trích. Nếu muốn hiện cả "Uranus (Alan Leo)" cần chấp nhận trích ô bảng.
2. **Song Ngư và Neptune**: Leo nêu có điều kiện ("if it be true…"), đã bỏ; chủ tinh hiện là Sao Mộc (Lilly tr. 99, Ptolemy tr. 42).
3. **Câu nặng nề giữ nguyên độ mạnh**: ví dụ Song Ngư "hầu như luôn tỏ ra khác với con người thật của mình" (tr. 45), Bọ Cạp "thù dai và hay bắt lỗi… tới mức quá đáng" (tr. 33), Ma Kết "có thể cực kỳ ích kỷ" (tr. 41). Đúng lời sách và luôn đi kèm điều kiện "khi chỉ sống theo cái tôi" nếu sách có ghi; chủ sở hữu có thể muốn bớt.
4. **"Phẩm chất bên trong" (inner nature or destiny)**: mỗi chương AL kết bằng một chữ (Truth, Obedience…); đã giữ cho 11 cung hoàng đạo dưới dạng "theo tác giả". Kim Ngưu dùng câu tr. 56 ("Duty and obedience are the high keynotes") vì dòng tr. 18 OCR quá hỏng.
5. **Ptolemy nói "nhà" (house) của hành tinh**, không nói "ruler"; trang ghi "Chủ tinh" theo cách gọi quen thuộc. Ptolemy cũng không gọi tên nguyên tố cho các tam hợp, nên câu tam hợp của Ptolemy chỉ nói "cùng X và Y tạo thành tam hợp thứ…", không gán Lửa/Đất.
6. **Khớp gần đúng**: 38 câu khớp nhờ ngưỡng 90 % (OCR). Văn bản câu trích là chữ in thật (đã đối chiếu ảnh trang ở các chỗ Lilly), không phải chữ OCR lỗi.

Quy trình khi sửa: sửa `tools/data/hoang_dao_rules.json` → `.venv/bin/python tools/build_hoang_dao_pack.py` → `.venv/bin/python tools/build_site.py` → `pytest engine/tests/test_hoang_dao.py engine/tests/test_sitegen.py`.

## 4. Kiểm thử (`engine/tests/test_hoang_dao.py`)

- Tên 12 cung hoàng đạo; glyph Python và JS trùng nhau.
- Mốc cung hoàng đạo đúng bằng các trung khí, liên tiếp không bỏ cung hoàng đạo nào; khớp PyEphem độc lập dưới 2 phút (1900–2049); trước / sau Xuân Phân 2024; Sài Gòn 1964 UTC+8; khối API và `GET /api/hoang-dao`.
- Gói luận giải dựng lại đúng từ các mục; nằm ngoài `PACKS`; ba nguồn có trong `sources.json`, TB là bản Ashmand.
- Mỗi cung hoàng đạo có 8–16 ý tính cách/nghề, tất cả từ Alan Leo; Lilly và Ptolemy chỉ phân loại; đủ nguyên tố, tính chất, chủ tinh; thứ tự Lửa–Đất–Khí–Nước và tiên phong–kiên định–linh hoạt đúng vòng.
- Lọc nội dung loại trừ (sức khỏe, hôn nhân, tình dục, chủng tộc, hành tinh khác…) trên câu trích và lời diễn.
- **Mọi câu trích được kiểm trên đúng trang** (217 tham số; chỉ bỏ qua khi máy không có PDF); kiểm thử "có răng": câu đúng trang khác thì trượt, câu bị sửa nghĩa thì trượt.
- Bản đồ trang: tr. 49 của AL bị từ chối (không có trong bản quét), CA tr. 93 = PDF 127, TB tr. 42 = PDF 78.
- Trang mới: không có chữ "AI", không "cung" trơn, không ký tự ♈…♓; có trích dẫn "[Alan Leo, tr. 13]", "[Ptolemy, tr. 43]", mục nguồn và JSON-LD `Book`.

## 5. Câu hỏi mở cho chủ sở hữu

1. Chủ tinh Bảo Bình: chỉ Sao Thổ (truyền thống) hay thêm Uranus của Alan Leo (mục 3, điểm 1)?
2. Có bớt những câu tiêu cực mạnh (mục 3, điểm 3) hay giữ nguyên độ mạnh của sách?
3. Tên gọi Bọ Cạp / Thiên Yết: hiện ghi "Bọ Cạp (Thiên Yết)".
4. Khoảng ngày ước lượng: đang dùng nhãn quen thuộc (21/3–19/4…), khác đôi chút với ngày Alan Leo in (21/3–20/4…).
5. Khung "Hỏi Bát Bát" (`js/ask.js`) có trên mọi trang tĩnh, kể cả trang cung hoàng đạo, và có chữ "AI" trong khung chat (phần có sẵn, không thuộc bậc 1).
6. Bậc 2 (cung mọc, Mặt Trăng): Alan Leo có chương riêng (tr. 63–70 Mặt Trăng, tr. 164–184 cung mọc), nhưng cần giờ và nơi sinh chính xác, và bản quét lệch trang khác (cần đo thêm).
