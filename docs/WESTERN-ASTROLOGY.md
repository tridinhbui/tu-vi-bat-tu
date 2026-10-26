# Chiêm tinh phương Tây (Western astrology) — module `engine/western/`

Trang `/chiem-tinh/`, API `/api/west/*`. Không dùng mô hình ngôn ngữ khi chạy: số liệu là thiên văn, luận giải là quy tắc có nguồn áp vào lá số.
Chiêm tinh được trình bày là một truyền thống diễn giải biểu tượng, không phải phương pháp dự báo đã được khoa học chứng minh.

## 1. Tính toán thiên văn

| Thành phần | Cách làm | Nguồn | Đối chiếu |
|---|---|---|---|
| Vị trí 10 thiên thể | biểu kiến, địa tâm, hoàng đạo và xuân phân thực của ngày (nhiệt đới), Skyfield 1.55 + JPL DE440s (cắt 1899–2101, `engine/data/western/de440s_1899_2101.bsp`) | JPL_DE440, SKYFIELD | Swiss Ephemeris 2.10, 249 thời điểm 1900–2100: ≤ 0,01″; JPL Horizons 15 điểm: ≤ 0,5″ |
| Chiron | vector Horizons (lời giải JPL#171) mỗi 4 ngày, nội suy Hermite (`tools/west/build_chiron.py`) | JPL_HORIZONS | Swiss ≤ 0,9″; Horizons ≤ 2″ |
| Nút Mặt Trăng | thực (osculating, từ vị trí + vận tốc), trung bình (Meeus 47.7 + chương động) | MEEUS, SWE_DOC | Swiss ≤ 0,05″ / 0,11″ |
| Tốc độ, nghịch hành, đứng | sai phân trung tâm ±1 giờ của kinh độ biểu kiến (đạo hàm giải tích của Skyfield bỏ qua thay đổi quang sai, làm lệch thời điểm đứng của Sao Thổ tới 2 giờ) | | thời điểm đứng khớp Swiss < 10 phút |
| ASC, MC, nhà | công thức cầu: Placidus (lặp), Regiomontanus, Equal, Whole Sign, Porphyry; Placidus vô nghĩa trong vòng cực → Porphyry và báo; trong vòng cực công thức cung Mọc có lúc trả về điểm lặn, khi đó lấy điểm đối diện (điểm đang mọc, như Swiss); Regiomontanus cho đỉnh nhà sai thứ tự trong vòng cực thì coi là không xác định, phần của Lilly dùng Porphyry | SWE_DOC | Swiss: 0,01″ trước 2050; sau 2050 lệch tới vài ″ do hai mô hình UT1 ngoại suy khác nhau |
| Thời gian | lịch sử múi giờ IANA (giờ mùa hè, giờ lặp, giờ không tồn tại), Asia/Hanoi từ backzone, giờ địa phương trung bình của nơi sinh khi tzdb ghi LMT; trước 1972 coi giờ dân sự là UT1 (Skyfield lệch 2,7 s năm 1969) | TZDB | test DST New York, LMT 1900, Hà Nội 1965 |
| Địa danh | GeoNames cities15000 + cities1000 (Việt Nam), tên tiếng Việt, Sài Gòn/TP HCM | GEONAMES (CC BY 4.0) | |
| Transit | quỹ đạo kinh độ lấy mẫu một lần, nội suy Lagrange bậc ba, tìm nghiệm trên đa thức | | Swiss: ingress ≤ 60 s, giao hội chính xác ≤ 60 s; 1 năm × 11 thiên thể ≈ 1 s |
| Solar Return | Newton trên lịch thiên văn, sai số kinh độ Mặt Trời < 0,05″ | LILLY_CA tr.734 | Swiss `solcross_ut` ≤ 5 s |
| Secondary progressions | 1 ngày = 1 năm chí tuyến (365,24219 ngày); trục: solar arc (kinh độ), solar arc theo xích kinh, Naibod | LEO tr.27 | test đối chiếu ngược ngày |
| Profection | trọn cung từ cung Mọc (Valens IV.11) hoặc +30°/năm (Lilly tr.715); năm bắt đầu lúc Solar Return (Lilly tr.716) | VALENS_ANTH, LILLY_CA | chu kỳ 12 năm |

Swiss Ephemeris (AGPL-3.0 hoặc giấy phép trả phí) **không** được đóng gói: repo công khai, chưa có giấy phép, site có trả phí, nên AGPL sẽ buộc cả site theo AGPL. Nó chỉ dùng trong môi trường dev (`tools/west/make_swe_reference.py`, `make_swe_events.py`) để sinh số tham chiếu cho test.

## 2. Tri thức và trường phái

Bảng tham chiếu: `engine/data/western/kb/` (`sources.json`, `core.json`, `dignities.json`, `aspects.json`, `meanings.json`), trích dẫn gốc: `engine/data/western/sources/` (Ptolemy bản Robbins 240 mục, Lilly 1647 160 mục, Valens bản Riley 102 mục không kèm câu trích vì bản dịch còn bản quyền, Alan Leo 68 mục).

| Trường phái | Nguồn đã đọc | Dùng cho |
|---|---|---|
| Hy Lạp cổ đại | Ptolemy, *Tetrabiblos* (Robbins 1940, public domain); Valens, *Anthologies* (Riley) | sect, tam hợp chủ, Lot, chỗ trọn cung, chủ tâm hồn, chủ hành nghiệp, của cải, tình bạn, profection |
| Truyền thống | Lilly, *Christian Astrology* (1647, ảnh trang Wellcome) | bảng phẩm vị tr.104, điểm tr.101-103/115, orb tr.107, combust/cazimi tr.113-114, Regiomontanus, Lord of the Geniture, khí chất, tính cách, nghề, danh vọng, tiền bạc, hôn nhân, gia đình, revolution |
| Hiện đại | Alan Leo (1906–1928, public domain) | ba trung tâm, Mặt Trời/Mặt Trăng theo cung, Thiên Vương, Hải Vương, năm phép tổng hợp, progressions, thứ bậc transit |

Mỗi đoạn luận giải chỉ trích nguồn của trường phái mình, tính bằng bảng và cách chia nhà của trường phái ấy (Lilly: Regiomontanus; Valens: trọn cung; Ptolemy: chỗ 30° bắt đầu 5° trên điểm Mọc). Đoạn "Đối chiếu" đặt hai kết quả cạnh nhau và nói rõ.

Khác biệt giữa các trường phái được giữ, không trộn: bảng term (Ai Cập / Ptolemy theo Robbins / Lilly — ba bảng khác nhau), chủ tam hợp (Valens 3 chủ / Ptolemy-Lilly ngày-đêm), Lot of Fortune ban đêm (Ptolemy và Lilly: không đảo; Valens: đảo khi Mặt Trăng còn trên chân trời; quy ước "sect": luôn đảo), phe của Sao Thủy (Ptolemy: đông/tây; Valens: theo chủ term).

**Chưa có nguồn đã kiểm, nên không luận:** ý nghĩa Sao Diêm Vương và Chiron (chỉ hiện vị trí), các cấu hình hiện đại (T-square, Yod… chỉ ghi hình học), ý nghĩa từng cặp góc hợp trong synastry, orb hiện đại (quy ước Thiên Bàn, ghi rõ). Brennan, Arroyo, Robert Hand còn bản quyền và không có bản đọc hợp pháp miễn phí, nên không được trích.

**Định nghĩa của Thiên Bàn khi sách để ngỏ** (`reading/facts.py: OPERATIONAL`, hiện trong "Đọc sâu"): ngưỡng đắc/thất thế (tổng điểm bản chất và ngẫu nhiên theo Lilly: từ +10 / từ 0 trở xuống), partile = cùng số độ, "mới mọc buổi sáng" của Ptolemy = cách Mặt Trời ≥ 15°, "đáng trọng" của Ptolemy = ở nhà/tôn vinh/tam hợp của mình và không bị Mặt Trời che, bị vây = Thổ và Hỏa hai bên trong cùng cung, đồng độ với định tinh = cách không quá 5° theo kinh độ (Lilly tr.616; tr.115 với Algol).

**Định tinh** (`western/stars.py`): ba sao của bảng điểm Lilly tr.115 (Cor Leonis +6, Spica +5, Caput Algol −5) và sáu sao vương giả của luật danh vọng tr.616 (Oculus Tauri = Aldebaran, Hercules = Pollux, Cor Leonis, Spica, Lucida Lancis = Zubenelgenubi, Cor Scorpii = Antares; tên của Lilly ứng với sao theo kinh độ năm 1647 ông in, cộng tuế sai, lệch < 0,5°). Vị trí tính cho ngày sinh từ dữ liệu Hipparcos; khớp Swiss Ephemeris dưới 0,1″ năm 1900–2050.

## 3. Luận giải

`engine/western/reading/`: `facts.py` (tính theo từng trường phái), `ch_core.py` (Tổng quan, Tính cách, Tư duy, Cảm xúc), `ch_life.py` (Sự nghiệp, Tài chính, Quan hệ, Gia đình, Định hướng), `ch_time.py` (Thời vận: profection, transit, Solar Return, progressions, mỗi kỹ thuật một đoạn), `synastry.py`, `audit.py`.

Mỗi đoạn: `heading, text, school, sources[{id, loc, label}], evidence[{kind, id, label, house?, system?}], level (overview/deep), layer (summary/analysis/deep), tier, steps, polarity`.
`level` là thứ `src/billing/west.ts` cắt theo người đọc (không đổi); `layer` là thứ trang dùng: "Đọc nhanh" hiện lớp `summary`, "Đọc sâu" hiện cả ba lớp và gập lớp `deep`.

**Nhà theo từng trường phái (2026-10-25).** Mỗi trường phái đọc trong hệ nhà của mình: Lilly = Regiomontanus cộng quy tắc 5° của chính ông ("if he be within five degrees of the Cusp of any house, his vertue shall be assigned to that house", *Christian Astrology* tr.33; `houses.house_of_lilly`), Valens = trọn cung, Ptolemy = chỗ 30° từ 5° trên điểm Mọc, Alan Leo = hệ đang chọn (Placidus mặc định). Lần đầu một hành tinh mang số nhà khác ở hệ khác, câu văn ghi kèm (`Facts.house_note`); chip chứng cứ mang `{house, system}` và bánh xe tô dải nhà của đúng hệ ấy. Ví dụ lá 09/01/2002 04:30 Hà Nội: Sao Kim 17°05′ Ma Kết là Nhà 1 Placidus, Nhà 2 trọn cung, và Nhà 2 theo Lilly (cách đỉnh Nhà 2 Regiomontanus 0°12′).

**Điểm phẩm vị của Lilly** luôn tính trên bảng của Lilly (tam hợp ngày/đêm, Sao Hỏa giữ nhóm Nước cả ngày lẫn đêm, giới hạn của Lilly): `dignity.lilly_essential`, `conditions[p].lilly`. Bảng "Phẩm vị" vẫn cho chọn bảng tam hợp và giới hạn khác, nhưng cột "Điểm Lilly" không cộng điểm Lilly trên bảng của trường phái khác (trước đó Mặt Trăng ở Bọ Cạp lá 2002 hiện −1, đúng ra −9).

**Phần tóm tắt của tám chương** (`reading/argue.py`): Tính cách, Tư duy, Cảm xúc, Sự nghiệp, Tài chính, Quan hệ, Gia đình, Định hướng mở đầu bằng một đoạn viết cho người mới: luận điểm chính, lý do (đánh số), điều kéo về phía ngược lại, kết luận cho lá này, biểu hiện theo lời sách, độ nhạy với giờ sinh (bao nhiêu phút thì phần dựa vào nhà đổi). Mỗi "chứng" là kết quả một phép mà chính chương ấy đã áp (cùng hàm `Facts`, cùng ngưỡng); phần của Thiên Bàn là cách cân: trọng số 3 khi sách tự tính một chứng bằng nhiều chứng (Lilly tr.616), 2 cho sao chủ của phép, 1 cho chứng phụ; "thuận"/"nghịch" khi một bên nặng gấp đôi, "hai mặt" khi gần cân, "nhẹ" khi ít chứng. Chỉ nói "nhiều trường phái cùng chỉ" khi hai tác giả, bằng phép riêng, cùng chọn một hành tinh. Các chứng và trọng số nằm trong `steps` (Đọc sâu).

**Thời vận** (`reading/ch_time.py`, `reading/milestones.py`): tóm tắt mười hai tháng tới, "Bốn kỹ thuật khác nhau thế nào" (ví dụ lấy từ chính lá số), từng quý (mỗi kỹ thuật một dòng), profection, transit chọn theo điểm, Solar Return sắp tới, tiến trình. Điểm transit (quy ước Thiên Bàn, ghi đủ từng phần): hành tinh đi qua (Mộc, Thổ, Thiên Vương 3 theo thứ bậc của Leo tr.193; Hỏa 1 vì mỗi lần chạm chỉ vài ngày; Hải Vương, Diêm Vương, Chiron 1; Thủy, Kim chỉ khi là chủ lá số, Leo tr.201), điểm gốc (chủ năm +3 theo Valens IV.11 và Lilly tr.726-727, hai sao sáng và hai trục +2, chủ lá số +1, hành tinh khác +1), loại góc (trùng tụ 3, đối và vuông 2, tam hợp và lục hợp 1), chính xác trong khung +1, một vòng nghịch hành +1; nổi bật từ 7 điểm. `/api/west/transits` trả điểm cho từng sự kiện để timeline lọc "Chỉ mốc nổi bật". Các kỹ thuật không bao giờ cộng thành một điểm chung.

**Transit theo vòng nghịch hành.** Mỗi đoạn nằm trong orb là một sự kiện; các đoạn của cùng một vòng nghịch hành qua cùng một điểm có chung `cycle` và được vẽ thành một dòng. Góc lục hợp, vuông, tam hợp có hai phía (`side`: ahead/behind), nên hai dòng cùng tên được ghi phía.

**Tiến trình** có `retrograde` ở sự kiện đổi cung, đổi nhà, góc chiếu, và sự kiện `station` (Sao Thủy của lá 2002 đứng lại đi lùi ở tuổi 9,97, đi thuận ở tuổi 30,83, khớp Swiss Ephemeris).
Kiểm toán chạy trên mọi bản luận: thiếu nguồn, trộn trường phái, câu lặp (lớp tóm tắt chỉ so với lớp tóm tắt), câu chung chung kiểu Barnum, từ cấm (chắc chắn, chết, tên bệnh, tội phạm), đoạn trái chiều chưa đối chiếu, dấu `{}` còn sót, khung câu nối sai (viết hoa sau dấu phẩy), ba đoạn liền nhau mở cùng một kiểu ("Theo Lilly…"), số nhà không ghi hệ, chương thiếu tóm tắt hoặc tóm tắt không có chứng cứ.
Đánh giá trên nhiều lá: `python tools/west/eval_reading.py 1000 --report docs/WESTERN-EVAL.md` (theo chương: số câu, chữ ở Đọc nhanh, câu mang dữ kiện, câu lặp ở nửa số lá; phân bố luận điểm và kết luận của tóm tắt; mâu thuẫn đắc/thất thế; thuật ngữ có glossary; đổi giờ sinh 2 giờ; đổi kinh độ 0,001°). Bất biến của engine: `python tools/west/fuzz_engine.py 1000`.

## 3b. Thu phí một phần (chủ site chốt 2026-10-25)

Worker cắt `/api/west/reading` theo người đọc (`src/billing/west.ts`, bật cùng `TVBT_PAYWALL`); bản đồ, bảng, bánh xe, dữ liệu vận hạn (transit, progression, profection, solar return) và synastry không bị cắt.

| Người đọc | Được đọc |
|---|---|
| Khách (chưa đăng nhập) | nửa đầu phần luận chính của mỗi chương |
| Thành viên (miễn phí) | trọn phần luận chính của 11 chương lá số gốc; Đọc sâu của Tổng quan, Hành tinh, Góc hợp, Tính cách; nửa đầu Tổng hợp và Thời vận |
| Gói "Chiêm tinh" (99 xu, giá tạm) | thêm Đọc sâu của Tư duy, Cảm xúc, Sự nghiệp, Tài chính, Quan hệ, Gia đình, Định hướng, và trọn Tổng hợp, Thời vận |

Gói mua cho một ngày giờ + nơi sinh (dấu vân tay `w:năm:tháng:ngày:giờ:phút:vĩ độ:kinh độ:múi giờ`, khác lá số Tử Vi); gói Tử Vi không mở chương Chiêm tinh và ngược lại. Đăng nhập từ thẻ khóa quay về `/chiem-tinh/` (`?next=`, chỉ nhận đường dẫn nội bộ) và mở lại bản đồ đang xem.

## 4. API

`GET /api/west/places?q=` · `POST /api/west/chart` · `/transits` · `/progressions` · `/profections` · `/solar-return` · `/reading` · `/synastry` (xem `engine/western/api.py`). Không lưu dữ liệu sinh.

**Máy chủ:** container production chạy loại `basic` (1/4 vCPU, 1 GiB) từ 2026-10-25, cho cả Tử Vi, Bát Tự và Chiêm tinh (`wrangler.jsonc`). CPU tính theo mức dùng thật; bộ nhớ và đĩa tính khi container thức (ngủ sau 10 phút không có request): nếu thức cả tháng, thêm khoảng 6 USD so với `lite`. Lưu ý: check run của Workers Builds có lúc hiện "failure" rồi mới chuyển "success"; xem rollout của container (`wrangler containers info`, API rollouts) trước khi kết luận deploy hỏng.

**Tốc độ trên `lite` (2026-10-25):** vị trí hành tinh lấy mẫu theo khúc cố định và dùng chung cho mọi request (`transits._samples`): bầu trời quanh hôm nay giống nhau cho mọi lá số, nên Thời vận và Vận hạn của người sau dùng lại phần người trước đã tính. Bài luận giải trọn (Đọc sâu) của 32 lá số gần nhất được giữ trong ngày (`api._READINGS`); Tổng quan lọc từ đó. Đo trên máy dev: lần đầu 0,34–0,45 giây CPU, mở lại hoặc đổi chế độ 0,002 giây, lá số mới khi cache đã ấm khoảng 0,2–0,3 giây.

## 5. Tái tạo dữ liệu

```
python tools/west/build_chiron.py                 # Horizons → chiron_1899_2101.npz
python tools/west/build_places.py <geonames dir>  # GeoNames → places.json.gz
<venv có pyswisseph> tools/west/make_swe_reference.py <ephe>; make_swe_events.py <ephe>   # chỉ cho test
```

## 6. Còn thiếu / chưa kiểm

- Đối chiếu trực tiếp trên Astro.com cần bấm đồng ý điều khoản của Astrodienst; Astro-Seek chặn bằng kiểm tra chống bot. Thay vào đó đã đối chiếu với Swiss Ephemeris (thư viện Astro.com dùng) và JPL Horizons.
- Valens: dựng lại lá năm theo Mặt Trăng (V.5) và profection tháng/ngày chưa làm, có chủ ý (2026-10-25): vận năm đã có profection và Solar Return; đoạn V.5 của bản Riley khó đọc, dễ diễn sai, nên chờ có thêm nguồn đối chiếu. Lilly: cung bị chặn (intercepted) ở Nhà 2/3 chưa xét.
- Ngày trước 1899 hoặc sau 2100 bị từ chối (giới hạn của file lịch thiên văn đi kèm).
- (Đã quyết 2026-10-25, chủ site chọn) "Đắc thế / thất thế" tính trên tổng điểm của Lilly: phẩm vị (tr.104) cộng điểm ngẫu nhiên (tr.115), như Lilly cộng khi chọn sao chủ lá số (tr.531). Mạnh từ +10, yếu từ 0 trở xuống: một sao không có gì đặc biệt (không phẩm vị, đi thuận, không bị Mặt Trời che) đã được khoảng +5 theo bảng tr.115, nên khoảng giữa đặt quanh mức ấy. Mỗi kết luận ghi tổng điểm và các dòng nặng nhất (`Facts.strength_why`). Trước đó chỉ xét điểm bản chất: 55% vị trí ra "yếu", phần lớn chỉ vì lạc chỗ.
- Thử với người mới mới chỉ là một bản đọc mô phỏng (một agent đóng vai người chưa học chiêm tinh); chưa có người đọc thật.
