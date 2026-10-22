# Phase 5 — bảng đối chiếu nguyên văn: Mã đầu đới kiếm, Thạch trung ẩn ngọc, bảng Tứ Hóa

Sinh bởi `tools/build_phase5_readings.py` (dữ liệu: `engine/data/experimental/source_readings_phase5.json`). **Không định nghĩa nào bị sửa, không trạng thái nào được nâng.**

## Cách đọc và loại nguồn

| Loại | Tài liệu | Cách đọc |
|---|---|---|
| `classic_web` | 紫微斗數全書 trên zh.wikisource.org | một bản web, qua công cụ tóm tắt trang, hai lần lấy khớp nhau; chưa đối chiếu bản in |
| `translation_commentary` | Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục dịch và bình chú) | PDF của người dùng, đọc lớp chữ (mã VNI giải mã) |
| `vn_treatise` | Tử Vi Khảo Luận, Tử Vi Thực Hành | PDF của người dùng; TH p.21, p.43 đọc cả ảnh trang vì lớp chữ bị vỡ |
| `registry` | luật trong `pack_*.json` | nội bộ dự án; **không** phải bằng chứng độc lập |

Chính sách trích dẫn: ba cuốn sách Việt còn bản quyền nên chỉ **diễn giải sát nghĩa kèm số trang** (không chép đoạn dài); chỉ các câu Hán văn cổ (phạm vi công cộng) được chép nguyên văn. Cột "diễn giải" là lời của người audit.

## Mã đầu đới kiếm

Bản nháp v2: lõi = Mệnh ở Ngọ + Kình Dương đồng cung; tăng thế = Khoa/Quyền/Lộc hội tam phương, Tả Hữu hội; phá = Thất Sát trong tam phương, Hỏa/Linh/Không/Kiếp đồng cung, Kỵ đồng cung; cứu = Khoa đồng cung, Tam Hóa hội; phản chứng = Tuần/Triệt.

| id | loại | tài liệu | trang | cách đọc | diễn giải sát nghĩa | Hán văn (nếu có) | tương ứng với bản nháp | ghi chú |
|---|---|---|---|---|---|---|---|---|
| M01 | vn_treatise | Tử Vi Khảo Luận | p.64 mục 5 | PDF text layer (VNI decoded) read | Cách 'Mã đầu đới kiếm' xấu: Mệnh ở Ngọ có Kình Dương, lại có Thất Sát và Thiên Hình đồng cung; sách nói không chết yểu cũng tàn tật. |  | khop | lõi (Mệnh Ngọ + Kình) khớp; breaker 'Thất Sát' khớp một phần: sách đòi Thất Sát VÀ Thiên Hình ĐỒNG CUNG, bản nháp lấy Thất Sát ở bất kỳ cung nào trong tam phương và bỏ Thiên Hình |
| M02 | vn_treatise | Tử Vi Khảo Luận | p.64 mục 6 | PDF text layer (VNI decoded) read | Cách 'Mã đầu đới kiếm, trấn ngự biên cương' tốt: Mệnh ở Ngọ có Kình Dương đồng cung, tránh được Thất Sát và Thiên Hình, lại gặp Khoa Quyền Lộc; sự nghiệp lớn, hiển đạt về võ nghiệp. |  | khop | booster Khoa/Quyền/Lộc khớp về nội dung; sách nói 'gặp' mà không nêu vai (đồng cung, tam hợp hay chiếu) nên phạm vi tam phương của bản nháp là một cách đọc |
| M03 | vn_treatise | Tử Vi Khảo Luận | p.64 mục 3 | PDF text layer (VNI decoded) read | Kình Dương ở Mệnh tại Tý, Ngọ, Mão, Dậu: không chết non thì tàn tật; Ngọ nguy nhất, Tý nhẹ hơn, Mão Dậu nhẹ nữa; kèm danh sách năm sinh Giáp-Mão, Bính-Ngọ, Canh-Dậu, Nhâm-Tý. |  | lien_quan | cùng một sách coi Kình ở Ngọ là xấu nói chung (mục 3) rồi coi là tốt khi có điều kiện (mục 6): bản thân KL có hai chiều |
| M04 | vn_treatise | Tử Vi Khảo Luận | p.60 mục 6 | PDF text layer (VNI decoded) read | 'Sát Kình tại Ngọ, Mã đầu đới kiếm': Mệnh ở Ngọ có Thất Sát và Kình Dương tọa thủ, thêm nhiều sát tinh hội chiếu thì như kiếm kề cổ ngựa; người tuổi Bính, Mậu gặp tai nạn binh đao. |  | lien_quan | cách nói xấu, điều kiện là Thất Sát + Kình + nhiều sát tinh; có điều kiện theo can năm (Bính, Mậu) |
| M05 | vn_treatise | Tử Vi Khảo Luận | p.64 mục 7 | PDF text layer (VNI decoded) read | Kình Dương ở Mệnh tại Ngọ đồng cung với Thiên Đồng, Thái Âm, Phượng Các, Giải Thần thì nổi danh, giàu sang cả đời. |  | lien_quan | cấu trúc khác (Kình đồng cung Đồng Âm ở Ngọ); không phải tên 'Mã đầu đới kiếm' |
| M06 | vn_treatise | Tử Vi Khảo Luận | p.200 | PDF text layer (VNI decoded) read | Mệnh ở cung Ngọ (Mã) có Kình (gươm) gặp Thiên Mã và Tham Lang là cách Mã đầu đới kiếm, trấn ngự biên cương, phát võ nhưng không bền. |  | khac | định nghĩa thứ ba trong KL: thêm Thiên Mã + Tham Lang; bản nháp không dùng Thiên Mã hay Tham Lang |
| M07 | translation_commentary | Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục) | p.50 | PDF text layer (VNI decoded) read | Người chú giải ghi nhận chính Toàn Thư có hai chiều: một câu phú nói Mệnh ở Ngọ tọa Kình Dương là 'Mã đầu đới kiếm trị vì biên cương', một câu khác nói Kình Dương ở Tý, Ngọ, Mão, Dậu không chết yểu cũng tàn tật (Ngọ nặng nhất). |  | lien_quan | xác nhận mâu thuẫn nội bộ trong chính tài liệu |
| M08 | translation_commentary | Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục) | p.142 | PDF text layer (VNI decoded) read | Chú thích: 'Mã đầu đới nhẫn' là Kình Dương gặp Thiên Mã, nhưng phải ở tứ mộ (Thìn, Tuất, Sửu, Mùi) mới hay; ở Ngọ thì xấu. |  | khac | ngược với lõi bản nháp ở hai điểm: cần Thiên Mã; vị trí tốt là tứ mộ, không phải Ngọ |
| M09 | vn_treatise | Tử Vi Thực Hành | p.157 | PDF text layer (VNI decoded) read | Chỉ gặp câu phú 'Mã đầu đái kiếm trấn ngự biên cương' trong một đoạn thơ; không có điều kiện. |  | lien_quan | chỉ có tên và lời khen |
| M10 | classic_web | 紫微斗數全書 (zh.wikisource.org) | 卷一 太微賦 | WebFetch summariser, 2 fetches agreeing; not checked against print | Đầu ngựa đeo gươm, trấn giữ biên cương. | 馬頭帶劍，鎮衛邊疆 | lien_quan | chỉ có tên và lời khen; không nêu cung hay sao |
| M11 | classic_web | 紫微斗數全書 (zh.wikisource.org) | 卷一 定貴局 (chú) | WebFetch summariser, 2 fetches agreeing; not checked against print | Chú: Mã đầu đới kiếm nghĩa là Mã có 'nhận' (lưỡi dao), chứ không phải cách ở cung Ngọ. | 馬頭帶劍 謂馬有刃是也不是居午格 | khac | phủ nhận định nghĩa 'cư Ngọ'; nếu chữ 'nhận' là 羊刃 (Kình Dương) thì khớp M08 ở chỗ cần Mã + Kình |
| M12 | classic_web | 紫微斗數全書 (zh.wikisource.org) | 卷三 論諸星同垣各司所宜 (擎羊) | WebFetch summariser, 2 fetches agreeing; not checked against print | Kình Dương ở Tý, Ngọ, Mão, Dậu: không chết yểu thì bị hình thương; Ngọ hung, Mão kém hơn, Tý Dậu lại kém nữa; 'mã đầu đới kiếm', nếu nhiều sao tốt thì không cần luận (xấu). | 擎羊子午卯酉非夭折而刑傷 午凶卯次之，子酉又次之，馬頭帶劍，吉多勿論 | khac | cho tên cách gắn với Kình ở cả bốn cung Tý Ngọ Mão Dậu và tính 'cát' phụ thuộc số sao tốt; bản nháp chỉ lấy Ngọ |
| M13 | classic_web | 紫微斗數全書 (zh.wikisource.org) | 卷三 (dòng gần nghĩa, chữ 箭) | WebFetch summariser, 2 fetches agreeing; not checked against print | Đồng, Tham, Dương, Đà ở ngôi Ngọ (năm Bính, Mậu...) trấn giữ biên cương; gọi 'mã đầu đới tiễn', giàu và sang. | 同貪羊陀居午位丙戌鎮御邊疆 為馬頭帶箭富且貴 | khac | dùng chữ 箭 (tên) và nhóm sao Đồng Tham Dương Đà; chỉ ghi để cho thấy dị bản |

## Thạch trung ẩn ngọc

Bản nháp v2: lõi = Cự Môn ở Tý/Ngọ đồng cung Mệnh; tăng thế = Khoa+Quyền+Lộc hội đủ tam phương, Tả Hữu hội; phá = Kỵ hoặc Kình đồng cung; cứu = Khoa đồng cung; phản chứng = Tuần/Triệt, Cự Môn hãm.

| id | loại | tài liệu | trang | cách đọc | diễn giải sát nghĩa | Hán văn (nếu có) | tương ứng với bản nháp | ghi chú |
|---|---|---|---|---|---|---|---|---|
| T01 | vn_treatise | Tử Vi Khảo Luận | p.57-58 mục 1 | PDF text layer (VNI decoded) read | Cự Môn ở Tý hoặc Ngọ được Khoa, Quyền, Lộc tam hợp chiếu là cách 'Thạch trung ẩn ngọc', phú quý. |  | khop | khớp lõi (Cự Môn Tý/Ngọ) và booster Tam Hóa; sách nói 'tam hợp chiếu', bản nháp dùng cả tam phương (gồm bản cung và xung chiếu) |
| T02 | vn_treatise | Tử Vi Khảo Luận | p.44 | PDF text layer (VNI decoded) read | Trong bảng tên cách: Thạch trung ẩn ngọc = Mệnh có Cự Môn, Thiên Di có Thiên Cơ, ở Tý Ngọ. |  | khac | định nghĩa theo vị trí (Cự Môn ở Mệnh, Thiên Cơ ở Thiên Di), không nhắc Tam Hóa |
| T03 | vn_treatise | Tử Vi Khảo Luận | p.106 | PDF text layer (VNI decoded) read | Cự Môn ở Tý Ngọ gặp Tuần hoặc Triệt là kỳ cách mà người xưa gọi 'Thạch trung ẩn ngọc' (ngọc trong đá gặp thợ đẽo: tài gặp thời); Cự Môn cần Song Hao như nước rửa ngọc; thích Khoa Quyền Lộc. |  | khac | Tuần/Triệt là điều kiện THÀNH của cách; bản nháp dùng Tuần/Triệt làm PHẢN CHỨNG (ngược nghĩa) |
| T04 | vn_treatise | Tử Vi Khảo Luận | p.203 | PDF text layer (VNI decoded) read | Cách Thạch trung ẩn ngọc của Cự Môn cần Song Hao đồng cung để 'rửa đá' mới thành đại phú. |  | khac | thêm điều kiện Song Hao (Đại Hao, Tiểu Hao); bản nháp không có |
| T05 | vn_treatise | Tử Vi Khảo Luận | p.223 | PDF text layer (VNI decoded) read | Cự Môn ở Tý Ngọ có Khoa Quyền Lộc chiếu: học rộng tài cao, như ngọc ẩn trong đá. |  | khop | khớp booster Tam Hóa |
| T06 | translation_commentary | Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục) | p.34 | PDF text layer (VNI decoded) read | Phú 'Cự Môn Tý Ngọ, Khoa Quyền Lộc, Thạch trung ẩn ngọc, phúc hưng long': đóng ở Tý hay Ngọ hội với Khoa, Quyền, Lộc là cách ngọc ẩn trong đá, hưởng phúc lớn; cũng ghi Cự Môn vượng ở Tý Ngọ. |  | khop | khớp lõi và booster Tam Hóa; ghi Cự Môn vượng ở Tý/Ngọ nên refutation 'Cự Môn hãm' của bản nháp không bao giờ kích hoạt |
| T07 | vn_treatise | Tử Vi Thực Hành | p.43 (đọc ảnh) | PDF page image read | Cự ở Tý, Ngọ là ngọc trong đá, cần gặp Tuần, Triệt hoặc Hóa Lộc thì ngọc mới lộ ra; không gặp, hoặc gặp Lộc Tồn thì là 'chìm': đa học đa năng nhưng không gặp thời vận hiển hách. |  | khac | Tuần/Triệt hoặc Hóa Lộc làm thành; Lộc Tồn làm hỏng; không đòi Khoa Quyền; bản nháp ngược ở Tuần/Triệt |
| T08 | classic_web | 紫微斗數全書 (zh.wikisource.org) | 卷三 論諸星同垣各司所宜 (巨門) | WebFetch summariser, 2 fetches agreeing; not checked against print | Cự Môn ở Tý Ngọ có Khoa Quyền Lộc: Thạch trung ẩn ngọc, phúc hưng; giàu và con quý; người tuổi Tân, Quý thượng cách, Đinh, Kỷ thứ hai, Bính, Mậu chủ nam. | 巨門子午科權祿石中隱玉福興隆 富而子貴，辛癸人上格，丁己人次之，丙戊主男 | khop | khớp Tam Hóa đủ (科權祿); thêm điều kiện năm sinh mà bản nháp không có |
| T09 | classic_web | 紫微斗數全書 (zh.wikisource.org) | 卷一 論石中隱玉格 | WebFetch summariser, 2 fetches agreeing; not checked against print | Cự Môn gặp ở hai cung Tý Ngọ, thân hoặc mệnh gặp ắt vinh quý; lại được tam phương Khoa, Lộc chiếu thì ngọc ẩn trong đá là thịnh vượng. | 巨門子午二宮逢，身命逢之必貴榮，更得三方科祿照，石中隱玉是豐隆 | long_hon | chỉ nêu Khoa và Lộc (科祿), không nêu Quyền; áp cho Thân hoặc Mệnh; bản nháp (Khoa+Quyền+Lộc đủ) chặt hơn dòng này, khớp dòng ở 卷三 |
| T10 | classic_web | 紫微斗數全書 (zh.wikisource.org) | 卷一 斗數骨髓賦 | WebFetch summariser, 2 fetches agreeing; not checked against print | Cự Môn ở Tý Ngọ là ngọc ẩn trong đá; minh lộc, ám lộc thêm hoa trên gấm. | 子午巨門石中隱玉，明祿暗祿錦上添花 | lien_quan | nhắc minh lộc/ám lộc (Lộc), không nhắc Khoa Quyền |
| T11 | vn_treatise | Tử Vi Khảo Luận | p.66 mục 10 | PDF text layer (VNI decoded) read | Mệnh có Khoa, Quyền, Lộc hội họp mà bị Hóa Kỵ hoặc Kình Dương ĐỒNG CUNG HOẶC CHIẾU vào thì công danh mờ mịt. |  | chat_hon | breaker bản nháp (Kỵ hoặc Kình đồng cung) hẹp hơn sách: sách tính cả 'chiếu'. Registry (TV_KL_STAR_MENH_TAM_KY_KY_KINH) cũng chỉ ghi đồng cung nên diễn giải của registry hẹp hơn trang sách |

## Bảng Tứ Hóa theo can (Canh, Nhâm)

Bảng trong code: Canh = Dương Vũ Đồng Âm; Nhâm = Lương Tử Tả Vũ.

| id | loại | tài liệu | trang | cách đọc | diễn giải sát nghĩa | Hán văn (nếu có) | tương ứng với bản nháp | ghi chú |
|---|---|---|---|---|---|---|---|---|
| H01 | vn_treatise | Tử Vi Thực Hành | p.21 (đọc ảnh) | PDF page image read | Bảng Tứ Hóa theo can năm sinh. Canh: Lộc Thái Dương, Quyền Vũ Khúc, Khoa Thiên Đồng, Kỵ Thái Âm. Nhâm: Lộc Thiên Lương, Quyền Tử Vi, Khoa THIÊN PHỦ, Kỵ Vũ Khúc. |  | khac | Nhâm-Khoa = Thiên Phủ; bảng trong code dùng Tả Phụ |
| H02 | vn_treatise | Tử Vi Khảo Luận | p.196-197 | PDF text layer (VNI decoded) read | Tuổi Canh: Nhật, Vũ, Đồng, Âm (Lộc, Quyền, Khoa, Kỵ). Tuổi Nhâm: Thiên Lương, Tử Vi, TẢ PHỤ, Vũ Khúc. |  | khop | Nhâm-Khoa = Tả Phụ khớp bảng trong code; Canh khớp |
| H03 | classic_web | 紫微斗數全書 (zh.wikisource.org) | (qua zh.wikipedia, tam cấp) | WebFetch of zh.wikipedia 紫微斗數 | Bảng an Tứ Hóa theo năm can của hai bản: 全集 và 全書 giống nhau ở 8 can, khác ở Canh (thứ tự Khoa/Kỵ: 陽武陰同 so với 陽武同陰) và Nhâm (全集 Tả Phụ, 全書 Thiên Phủ). |  | lien_quan | nguồn thứ ba (tổng hợp) cho thấy cùng điểm bất đồng; KL theo 全集 ở Nhâm, TH theo 全書 ở Nhâm; bảng code = Canh theo 全書, Nhâm theo 全集 (lai) |

## Bất đồng giữa các nguồn

- **P5_MDDK_DEF — Ba định nghĩa khác nhau của 'Mã đầu đới kiếm'**: Kình Dương ở Ngọ (KL p.64, p.60; câu phú trong TT p.50) ↔ Kình + Thiên Mã + Tham Lang ở Ngọ (KL p.200) ↔ Kình gặp Thiên Mã, tốt ở tứ mộ, xấu ở Ngọ (TT p.142); 'không phải cách cư Ngọ' (chú 定貴局) ↔ Kình ở Tý/Ngọ/Mão/Dậu, 'cát nhiều thì khỏi luận' (全書 卷三). Hệ quả: không có định nghĩa chung để máy hóa; bản nháp theo KL p.64 mục 6 nhưng bỏ Thiên Hình và đổi 'đồng cung' thành 'tam phương'; giữ draft.
- **P5_TTAN_DEF — Điều kiện thành của 'Thạch trung ẩn ngọc' khác nhau giữa các nguồn**: Khoa+Quyền+Lộc tam hợp chiếu (KL p.58, p.223; TT p.34; 全書 卷三) ↔ Khoa+Lộc (全書 卷一 bài thơ) ↔ Tuần/Triệt hoặc Hóa Lộc; Lộc Tồn làm chìm (TH p.43) ↔ Tuần/Triệt (KL p.106); Song Hao (KL p.106, p.203) ↔ Thiên Cơ ở Thiên Di (KL p.44). Hệ quả: bản nháp: Tam Hóa là booster (khớp số đông) nhưng Tuần/Triệt là phản chứng (NGƯỢC TH p.43 và KL p.106).
- **P5_TUHOA_NHAM — Hóa Khoa của can Nhâm: Tả Phụ (KL p.197) hay Thiên Phủ (TH p.21)**: KL pp.196-197: Tả Phụ ↔ TH p.21: Thiên Phủ ↔ zh.wikipedia: 全集 Tả Phụ, 全書 Thiên Phủ. Hệ quả: bảng Tứ Hóa trong code (cả production lẫn Phi Hóa thử nghiệm) chọn Tả Phụ; ghi chú trong tuvi.py nói 'agree on all ten stems' nhưng cũng ghi Thực Hành in 'Phủ'; cần gắn nhãn trường phái cho lá số năm Nhâm.

## Đính chính Phase 4

- Xung đột X_TTAN_HOA ghi ở Phase 4 là 'sách Việt (Khoa+Quyền+Lộc) so với phú gốc (Khoa+Lộc)'. Đọc thêm 全書 卷三 cho thấy chính 全書 có hai dòng: 卷一 (Khoa, Lộc) và 卷三 (科權祿). Xung đột nằm BÊN TRONG 全書, và các sách Việt theo dòng 卷三.
- Phase 4 và phiên UI ghi KL p.66 là 'Kỵ hoặc Kình đồng cung'. Trang in nói 'đồng cung hoặc chiếu vào'. Registry hẹp hơn trang sách; breaker bản nháp theo registry nên cũng hẹp hơn.
- Phase 4 coi Tuần/Triệt chỉ là phản chứng 'không có nguồn'. Với Thạch trung ẩn ngọc, TH p.43 và KL p.106 coi Tuần/Triệt là điều kiện THÀNH: phản chứng của bản nháp trái hai trang này.
- Phase 4 nêu 'registry TH/KL đồng thuận cả mười can' cho bảng Tứ Hóa. Đọc ảnh TH p.21 và KL p.197 cho thấy hai sách khác nhau ở Khoa của can Nhâm.
