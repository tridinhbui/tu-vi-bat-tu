"""Phase 5: first-hand readings for two formations (Mã đầu đới kiếm, Thạch trung ẩn ngọc) and the Tứ Hóa-by-stem table.

Writes engine/data/experimental/source_readings_phase5.json and docs/PHASE5_BANG_DOI_CHIEU.md.

How each page was read (all in this audit session):
  * Khảo Luận (KL), Thực Hành (TH), Toàn Thư (TT): the user's PDFs. The text layer is VNI-encoded legacy Vietnamese; decoded with
    tools/vni_decode.py and read; TH p.21 and p.43 were additionally read as page IMAGES because the text layer was garbled there.
  * 紫微斗數全書 (the classic): ONE web copy (zh.wikisource.org) fetched through a page-summarising tool, two separate fetches that agreed.
    Not checked against a printed edition, so it is a primary text only in the sense of 'the classic as transcribed on that site'.
Quote policy: the three Vietnamese books are modern copyrighted works, so they are PARAPHRASED closely with exact page numbers (no
passages reproduced); only the classical Chinese lines (public domain) are quoted. `paraphrase_vi` is the auditor's own wording.

Source classes: classic_web (the classic), translation_commentary (TT: Vũ Tài Lục dịch và bình chú), vn_treatise (KL, TH),
registry (the project's own pack rules; never independent evidence)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "engine" / "data" / "experimental" / "source_readings_phase5.json"
DOC = ROOT / "docs" / "PHASE5_BANG_DOI_CHIEU.md"
W = {"KL": "Tử Vi Khảo Luận", "TH": "Tử Vi Thực Hành", "TT": "Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục)", "QT": "紫微斗數全書 (zh.wikisource.org)"}
CLS = {"KL": "vn_treatise", "TH": "vn_treatise", "TT": "translation_commentary", "QT": "classic_web"}
M_PDF, M_IMG, M_WEB = "PDF text layer (VNI decoded) read", "PDF page image read", "WebFetch summariser, 2 fetches agreeing; not checked against print"


def r(id, topic, w, page, method, para, rel, note="", zh=None, extracted=None):
    d = dict(id=id, topic=topic, work=W[w], source_class=CLS[w], page=page, method=method, paraphrase_vi=para, relation_to_draft_v2=rel, note=note,
             extracted=extracted or {})
    if zh:
        d["zh"] = zh
    return d


R = [
    # ---------------- Mã đầu đới kiếm ----------------
    r("M01", "MDDK", "KL", "p.64 mục 5", M_PDF, "Cách 'Mã đầu đới kiếm' xấu: Mệnh ở Ngọ có Kình Dương, lại có Thất Sát và Thiên Hình đồng cung; sách nói không chết yểu cũng tàn tật.",
      "khop", "lõi (Mệnh Ngọ + Kình) khớp; breaker 'Thất Sát' khớp một phần: sách đòi Thất Sát VÀ Thiên Hình ĐỒNG CUNG, bản nháp lấy Thất Sát ở bất kỳ cung nào trong tam phương và bỏ Thiên Hình",
      extracted=dict(core="Mệnh ở Ngọ + Kình Dương", bad="Thất Sát và Thiên Hình đồng cung")),
    r("M02", "MDDK", "KL", "p.64 mục 6", M_PDF, "Cách 'Mã đầu đới kiếm, trấn ngự biên cương' tốt: Mệnh ở Ngọ có Kình Dương đồng cung, tránh được Thất Sát và Thiên Hình, lại gặp Khoa Quyền Lộc; sự nghiệp lớn, hiển đạt về võ nghiệp.",
      "khop", "booster Khoa/Quyền/Lộc khớp về nội dung; sách nói 'gặp' mà không nêu vai (đồng cung, tam hợp hay chiếu) nên phạm vi tam phương của bản nháp là một cách đọc",
      extracted=dict(core="Mệnh ở Ngọ + Kình Dương đồng cung", good="Khoa, Quyền, Lộc gặp", cond="không có Thất Sát, Thiên Hình")),
    r("M03", "MDDK", "KL", "p.64 mục 3", M_PDF, "Kình Dương ở Mệnh tại Tý, Ngọ, Mão, Dậu: không chết non thì tàn tật; Ngọ nguy nhất, Tý nhẹ hơn, Mão Dậu nhẹ nữa; kèm danh sách năm sinh Giáp-Mão, Bính-Ngọ, Canh-Dậu, Nhâm-Tý.",
      "lien_quan", "cùng một sách coi Kình ở Ngọ là xấu nói chung (mục 3) rồi coi là tốt khi có điều kiện (mục 6): bản thân KL có hai chiều"),
    r("M04", "MDDK", "KL", "p.60 mục 6", M_PDF, "'Sát Kình tại Ngọ, Mã đầu đới kiếm': Mệnh ở Ngọ có Thất Sát và Kình Dương tọa thủ, thêm nhiều sát tinh hội chiếu thì như kiếm kề cổ ngựa; người tuổi Bính, Mậu gặp tai nạn binh đao.",
      "lien_quan", "cách nói xấu, điều kiện là Thất Sát + Kình + nhiều sát tinh; có điều kiện theo can năm (Bính, Mậu)"),
    r("M05", "MDDK", "KL", "p.64 mục 7", M_PDF, "Kình Dương ở Mệnh tại Ngọ đồng cung với Thiên Đồng, Thái Âm, Phượng Các, Giải Thần thì nổi danh, giàu sang cả đời.", "lien_quan",
      "cấu trúc khác (Kình đồng cung Đồng Âm ở Ngọ); không phải tên 'Mã đầu đới kiếm'"),
    r("M06", "MDDK", "KL", "p.200", M_PDF, "Mệnh ở cung Ngọ (Mã) có Kình (gươm) gặp Thiên Mã và Tham Lang là cách Mã đầu đới kiếm, trấn ngự biên cương, phát võ nhưng không bền.", "khac",
      "định nghĩa thứ ba trong KL: thêm Thiên Mã + Tham Lang; bản nháp không dùng Thiên Mã hay Tham Lang"),
    r("M07", "MDDK", "TT", "p.50", M_PDF, "Người chú giải ghi nhận chính Toàn Thư có hai chiều: một câu phú nói Mệnh ở Ngọ tọa Kình Dương là 'Mã đầu đới kiếm trị vì biên cương', một câu khác nói Kình Dương ở Tý, Ngọ, Mão, Dậu không chết yểu cũng tàn tật (Ngọ nặng nhất).",
      "lien_quan", "xác nhận mâu thuẫn nội bộ trong chính tài liệu"),
    r("M08", "MDDK", "TT", "p.142", M_PDF, "Chú thích: 'Mã đầu đới nhẫn' là Kình Dương gặp Thiên Mã, nhưng phải ở tứ mộ (Thìn, Tuất, Sửu, Mùi) mới hay; ở Ngọ thì xấu.", "khac",
      "ngược với lõi bản nháp ở hai điểm: cần Thiên Mã; vị trí tốt là tứ mộ, không phải Ngọ"),
    r("M09", "MDDK", "TH", "p.157", M_PDF, "Chỉ gặp câu phú 'Mã đầu đái kiếm trấn ngự biên cương' trong một đoạn thơ; không có điều kiện.", "lien_quan", "chỉ có tên và lời khen"),
    r("M10", "MDDK", "QT", "卷一 太微賦", M_WEB, "Đầu ngựa đeo gươm, trấn giữ biên cương.", "lien_quan", "chỉ có tên và lời khen; không nêu cung hay sao", zh="馬頭帶劍，鎮衛邊疆"),
    r("M11", "MDDK", "QT", "卷一 定貴局 (chú)", M_WEB, "Chú: Mã đầu đới kiếm nghĩa là Mã có 'nhận' (lưỡi dao), chứ không phải cách ở cung Ngọ.", "khac",
      "phủ nhận định nghĩa 'cư Ngọ'; nếu chữ 'nhận' là 羊刃 (Kình Dương) thì khớp M08 ở chỗ cần Mã + Kình", zh="馬頭帶劍 謂馬有刃是也不是居午格"),
    r("M12", "MDDK", "QT", "卷三 論諸星同垣各司所宜 (擎羊)", M_WEB, "Kình Dương ở Tý, Ngọ, Mão, Dậu: không chết yểu thì bị hình thương; Ngọ hung, Mão kém hơn, Tý Dậu lại kém nữa; 'mã đầu đới kiếm', nếu nhiều sao tốt thì không cần luận (xấu).",
      "khac", "cho tên cách gắn với Kình ở cả bốn cung Tý Ngọ Mão Dậu và tính 'cát' phụ thuộc số sao tốt; bản nháp chỉ lấy Ngọ",
      zh="擎羊子午卯酉非夭折而刑傷 午凶卯次之，子酉又次之，馬頭帶劍，吉多勿論"),
    r("M13", "MDDK", "QT", "卷三 (dòng gần nghĩa, chữ 箭)", M_WEB, "Đồng, Tham, Dương, Đà ở ngôi Ngọ (năm Bính, Mậu...) trấn giữ biên cương; gọi 'mã đầu đới tiễn', giàu và sang.", "khac",
      "dùng chữ 箭 (tên) và nhóm sao Đồng Tham Dương Đà; chỉ ghi để cho thấy dị bản", zh="同貪羊陀居午位丙戌鎮御邊疆 為馬頭帶箭富且貴"),
    # ---------------- Thạch trung ẩn ngọc ----------------
    r("T01", "TTAN", "KL", "p.57-58 mục 1", M_PDF, "Cự Môn ở Tý hoặc Ngọ được Khoa, Quyền, Lộc tam hợp chiếu là cách 'Thạch trung ẩn ngọc', phú quý.", "khop",
      "khớp lõi (Cự Môn Tý/Ngọ) và booster Tam Hóa; sách nói 'tam hợp chiếu', bản nháp dùng cả tam phương (gồm bản cung và xung chiếu)",
      extracted=dict(core="Cự Môn ở Tý/Ngọ", good="Khoa, Quyền, Lộc tam hợp chiếu")),
    r("T02", "TTAN", "KL", "p.44", M_PDF, "Trong bảng tên cách: Thạch trung ẩn ngọc = Mệnh có Cự Môn, Thiên Di có Thiên Cơ, ở Tý Ngọ.", "khac",
      "định nghĩa theo vị trí (Cự Môn ở Mệnh, Thiên Cơ ở Thiên Di), không nhắc Tam Hóa"),
    r("T03", "TTAN", "KL", "p.106", M_PDF, "Cự Môn ở Tý Ngọ gặp Tuần hoặc Triệt là kỳ cách mà người xưa gọi 'Thạch trung ẩn ngọc' (ngọc trong đá gặp thợ đẽo: tài gặp thời); Cự Môn cần Song Hao như nước rửa ngọc; thích Khoa Quyền Lộc.",
      "khac", "Tuần/Triệt là điều kiện THÀNH của cách; bản nháp dùng Tuần/Triệt làm PHẢN CHỨNG (ngược nghĩa)"),
    r("T04", "TTAN", "KL", "p.203", M_PDF, "Cách Thạch trung ẩn ngọc của Cự Môn cần Song Hao đồng cung để 'rửa đá' mới thành đại phú.", "khac", "thêm điều kiện Song Hao (Đại Hao, Tiểu Hao); bản nháp không có"),
    r("T05", "TTAN", "KL", "p.223", M_PDF, "Cự Môn ở Tý Ngọ có Khoa Quyền Lộc chiếu: học rộng tài cao, như ngọc ẩn trong đá.", "khop", "khớp booster Tam Hóa"),
    r("T06", "TTAN", "TT", "p.34", M_PDF, "Phú 'Cự Môn Tý Ngọ, Khoa Quyền Lộc, Thạch trung ẩn ngọc, phúc hưng long': đóng ở Tý hay Ngọ hội với Khoa, Quyền, Lộc là cách ngọc ẩn trong đá, hưởng phúc lớn; cũng ghi Cự Môn vượng ở Tý Ngọ.",
      "khop", "khớp lõi và booster Tam Hóa; ghi Cự Môn vượng ở Tý/Ngọ nên refutation 'Cự Môn hãm' của bản nháp không bao giờ kích hoạt"),
    r("T07", "TTAN", "TH", "p.43 (đọc ảnh)", M_IMG, "Cự ở Tý, Ngọ là ngọc trong đá, cần gặp Tuần, Triệt hoặc Hóa Lộc thì ngọc mới lộ ra; không gặp, hoặc gặp Lộc Tồn thì là 'chìm': đa học đa năng nhưng không gặp thời vận hiển hách.",
      "khac", "Tuần/Triệt hoặc Hóa Lộc làm thành; Lộc Tồn làm hỏng; không đòi Khoa Quyền; bản nháp ngược ở Tuần/Triệt"),
    r("T08", "TTAN", "QT", "卷三 論諸星同垣各司所宜 (巨門)", M_WEB, "Cự Môn ở Tý Ngọ có Khoa Quyền Lộc: Thạch trung ẩn ngọc, phúc hưng; giàu và con quý; người tuổi Tân, Quý thượng cách, Đinh, Kỷ thứ hai, Bính, Mậu chủ nam.",
      "khop", "khớp Tam Hóa đủ (科權祿); thêm điều kiện năm sinh mà bản nháp không có", zh="巨門子午科權祿石中隱玉福興隆 富而子貴，辛癸人上格，丁己人次之，丙戊主男"),
    r("T09", "TTAN", "QT", "卷一 論石中隱玉格", M_WEB, "Cự Môn gặp ở hai cung Tý Ngọ, thân hoặc mệnh gặp ắt vinh quý; lại được tam phương Khoa, Lộc chiếu thì ngọc ẩn trong đá là thịnh vượng.", "long_hon",
      "chỉ nêu Khoa và Lộc (科祿), không nêu Quyền; áp cho Thân hoặc Mệnh; bản nháp (Khoa+Quyền+Lộc đủ) chặt hơn dòng này, khớp dòng ở 卷三",
      zh="巨門子午二宮逢，身命逢之必貴榮，更得三方科祿照，石中隱玉是豐隆"),
    r("T10", "TTAN", "QT", "卷一 斗數骨髓賦", M_WEB, "Cự Môn ở Tý Ngọ là ngọc ẩn trong đá; minh lộc, ám lộc thêm hoa trên gấm.", "lien_quan", "nhắc minh lộc/ám lộc (Lộc), không nhắc Khoa Quyền", zh="子午巨門石中隱玉，明祿暗祿錦上添花"),
    r("T11", "TTAN", "KL", "p.66 mục 10", M_PDF, "Mệnh có Khoa, Quyền, Lộc hội họp mà bị Hóa Kỵ hoặc Kình Dương ĐỒNG CUNG HOẶC CHIẾU vào thì công danh mờ mịt.", "chat_hon",
      "breaker bản nháp (Kỵ hoặc Kình đồng cung) hẹp hơn sách: sách tính cả 'chiếu'. Registry (TV_KL_STAR_MENH_TAM_KY_KY_KINH) cũng chỉ ghi đồng cung nên diễn giải của registry hẹp hơn trang sách"),
    # ---------------- Tứ Hóa theo can: Canh, Nhâm ----------------
    r("H01", "TUHOA", "TH", "p.21 (đọc ảnh)", M_IMG, "Bảng Tứ Hóa theo can năm sinh. Canh: Lộc Thái Dương, Quyền Vũ Khúc, Khoa Thiên Đồng, Kỵ Thái Âm. Nhâm: Lộc Thiên Lương, Quyền Tử Vi, Khoa THIÊN PHỦ, Kỵ Vũ Khúc.",
      "khac", "Nhâm-Khoa = Thiên Phủ; bảng trong code dùng Tả Phụ"),
    r("H02", "TUHOA", "KL", "p.196-197", M_PDF, "Tuổi Canh: Nhật, Vũ, Đồng, Âm (Lộc, Quyền, Khoa, Kỵ). Tuổi Nhâm: Thiên Lương, Tử Vi, TẢ PHỤ, Vũ Khúc.", "khop", "Nhâm-Khoa = Tả Phụ khớp bảng trong code; Canh khớp"),
    r("H03", "TUHOA", "QT", "(qua zh.wikipedia, tam cấp)", "WebFetch of zh.wikipedia 紫微斗數", "Bảng an Tứ Hóa theo năm can của hai bản: 全集 và 全書 giống nhau ở 8 can, khác ở Canh (thứ tự Khoa/Kỵ: 陽武陰同 so với 陽武同陰) và Nhâm (全集 Tả Phụ, 全書 Thiên Phủ).",
      "lien_quan", "nguồn thứ ba (tổng hợp) cho thấy cùng điểm bất đồng; KL theo 全集 ở Nhâm, TH theo 全書 ở Nhâm; bảng code = Canh theo 全書, Nhâm theo 全集 (lai)"),
]

CONFLICTS = [
    dict(id="P5_MDDK_DEF", topic="MDDK", title="Ba định nghĩa khác nhau của 'Mã đầu đới kiếm'",
         sides=["Kình Dương ở Ngọ (KL p.64, p.60; câu phú trong TT p.50)", "Kình + Thiên Mã + Tham Lang ở Ngọ (KL p.200)", "Kình gặp Thiên Mã, tốt ở tứ mộ, xấu ở Ngọ (TT p.142); 'không phải cách cư Ngọ' (chú 定貴局)",
                "Kình ở Tý/Ngọ/Mão/Dậu, 'cát nhiều thì khỏi luận' (全書 卷三)"],
         effect="không có định nghĩa chung để máy hóa; bản nháp theo KL p.64 mục 6 nhưng bỏ Thiên Hình và đổi 'đồng cung' thành 'tam phương'; giữ draft"),
    dict(id="P5_TTAN_DEF", topic="TTAN", title="Điều kiện thành của 'Thạch trung ẩn ngọc' khác nhau giữa các nguồn",
         sides=["Khoa+Quyền+Lộc tam hợp chiếu (KL p.58, p.223; TT p.34; 全書 卷三)", "Khoa+Lộc (全書 卷一 bài thơ)", "Tuần/Triệt hoặc Hóa Lộc; Lộc Tồn làm chìm (TH p.43)",
                "Tuần/Triệt (KL p.106); Song Hao (KL p.106, p.203)", "Thiên Cơ ở Thiên Di (KL p.44)"],
         effect="bản nháp: Tam Hóa là booster (khớp số đông) nhưng Tuần/Triệt là phản chứng (NGƯỢC TH p.43 và KL p.106)"),
    dict(id="P5_TUHOA_NHAM", topic="TUHOA", title="Hóa Khoa của can Nhâm: Tả Phụ (KL p.197) hay Thiên Phủ (TH p.21)",
         sides=["KL pp.196-197: Tả Phụ", "TH p.21: Thiên Phủ", "zh.wikipedia: 全集 Tả Phụ, 全書 Thiên Phủ"],
         effect="bảng Tứ Hóa trong code (cả production lẫn Phi Hóa thử nghiệm) chọn Tả Phụ; ghi chú trong tuvi.py nói 'agree on all ten stems' nhưng cũng ghi Thực Hành in 'Phủ'; cần gắn nhãn trường phái cho lá số năm Nhâm"),
]

CORRECTIONS_TO_PHASE4 = [
    "Xung đột X_TTAN_HOA ghi ở Phase 4 là 'sách Việt (Khoa+Quyền+Lộc) so với phú gốc (Khoa+Lộc)'. Đọc thêm 全書 卷三 cho thấy chính 全書 có hai dòng: 卷一 (Khoa, Lộc) và 卷三 (科權祿). Xung đột nằm BÊN TRONG 全書, và các sách Việt theo dòng 卷三.",
    "Phase 4 và phiên UI ghi KL p.66 là 'Kỵ hoặc Kình đồng cung'. Trang in nói 'đồng cung hoặc chiếu vào'. Registry hẹp hơn trang sách; breaker bản nháp theo registry nên cũng hẹp hơn.",
    "Phase 4 coi Tuần/Triệt chỉ là phản chứng 'không có nguồn'. Với Thạch trung ẩn ngọc, TH p.43 và KL p.106 coi Tuần/Triệt là điều kiện THÀNH: phản chứng của bản nháp trái hai trang này.",
    "Phase 4 nêu 'registry TH/KL đồng thuận cả mười can' cho bảng Tứ Hóa. Đọc ảnh TH p.21 và KL p.197 cho thấy hai sách khác nhau ở Khoa của can Nhâm.",
]


def markdown():
    L = ["# Phase 5 — bảng đối chiếu nguyên văn: Mã đầu đới kiếm, Thạch trung ẩn ngọc, bảng Tứ Hóa", "",
         "Sinh bởi `tools/build_phase5_readings.py` (dữ liệu: `engine/data/experimental/source_readings_phase5.json`). **Không định nghĩa nào bị sửa, không trạng thái nào được nâng.**", "",
         "## Cách đọc và loại nguồn", "",
         "| Loại | Tài liệu | Cách đọc |", "|---|---|---|",
         "| `classic_web` | 紫微斗數全書 trên zh.wikisource.org | một bản web, qua công cụ tóm tắt trang, hai lần lấy khớp nhau; chưa đối chiếu bản in |",
         "| `translation_commentary` | Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục dịch và bình chú) | PDF của người dùng, đọc lớp chữ (mã VNI giải mã) |",
         "| `vn_treatise` | Tử Vi Khảo Luận, Tử Vi Thực Hành | PDF của người dùng; TH p.21, p.43 đọc cả ảnh trang vì lớp chữ bị vỡ |",
         "| `registry` | luật trong `pack_*.json` | nội bộ dự án; **không** phải bằng chứng độc lập |", "",
         "Chính sách trích dẫn: ba cuốn sách Việt còn bản quyền nên chỉ **diễn giải sát nghĩa kèm số trang** (không chép đoạn dài); chỉ các câu Hán văn cổ (phạm vi công cộng) được chép nguyên văn. Cột \"diễn giải\" là lời của người audit.", ""]
    for topic, title, draft in (
            ("MDDK", "Mã đầu đới kiếm", "Bản nháp v2: lõi = Mệnh ở Ngọ + Kình Dương đồng cung; tăng thế = Khoa/Quyền/Lộc hội tam phương, Tả Hữu hội; phá = Thất Sát trong tam phương, Hỏa/Linh/Không/Kiếp đồng cung, Kỵ đồng cung; cứu = Khoa đồng cung, Tam Hóa hội; phản chứng = Tuần/Triệt."),
            ("TTAN", "Thạch trung ẩn ngọc", "Bản nháp v2: lõi = Cự Môn ở Tý/Ngọ đồng cung Mệnh; tăng thế = Khoa+Quyền+Lộc hội đủ tam phương, Tả Hữu hội; phá = Kỵ hoặc Kình đồng cung; cứu = Khoa đồng cung; phản chứng = Tuần/Triệt, Cự Môn hãm."),
            ("TUHOA", "Bảng Tứ Hóa theo can (Canh, Nhâm)", "Bảng trong code: Canh = Dương Vũ Đồng Âm; Nhâm = Lương Tử Tả Vũ.")):
        L += [f"## {title}", "", draft, "",
              "| id | loại | tài liệu | trang | cách đọc | diễn giải sát nghĩa | Hán văn (nếu có) | tương ứng với bản nháp | ghi chú |", "|---|---|---|---|---|---|---|---|---|"]
        for x in R:
            if x["topic"] == topic:
                L.append(f"| {x['id']} | {x['source_class']} | {x['work']} | {x['page']} | {x['method']} | {x['paraphrase_vi']} | {x.get('zh', '')} | {x['relation_to_draft_v2']} | {x['note']} |")
        L += [""]
    L += ["## Bất đồng giữa các nguồn", ""]
    for c in CONFLICTS:
        L += [f"- **{c['id']} — {c['title']}**: " + " ↔ ".join(c["sides"]) + f". Hệ quả: {c['effect']}."]
    L += ["", "## Đính chính Phase 4", ""] + [f"- {t}" for t in CORRECTIONS_TO_PHASE4]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    OUT.write_text(json.dumps(dict(version=1, note=__doc__.split("\n\n")[0], works=W, readings=R, conflicts=CONFLICTS, corrections_to_phase4=CORRECTIONS_TO_PHASE4),
                              ensure_ascii=False, indent=1) + "\n", "utf-8")
    DOC.write_text(markdown(), "utf-8")
    print(len(R), "readings,", len(CONFLICTS), "conflicts")
