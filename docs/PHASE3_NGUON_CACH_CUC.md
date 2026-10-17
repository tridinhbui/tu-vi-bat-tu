# Phase 3 — đối chiếu nguồn cho 10 cách cục, Phi Hóa, lưu tinh

Tiếp theo [PHASE1_KET_QUA.md](PHASE1_KET_QUA.md) và [PHASE2_KET_QUA.md](PHASE2_KET_QUA.md). Không dùng LLM trong sản phẩm. **Không cách cục nào được đánh dấu `verified`**; mọi thứ dưới đây vẫn là `draft`, ngoài `PACKS` production, chỉ đi qua cờ `experimental` / endpoint thử nghiệm.

## 1. Cách đối chiếu và mức tin cậy của nguồn

| Nguồn | Cách truy xuất | Mức tin |
|---|---|---|
| Luật đã có trang trong kho: Khảo Luận (KL), Thực Hành (TH), Toàn Thư Vũ Tài Lục (TT) | đọc `engine/data/pack_*.json`; id luật, trang và `reviewStatus` lấy từ pack | tốt nhất hiện có: các phiên trước đã đọc sách. Luật `draft` trong pack vẫn là draft |
| 紫微斗數全書 (nguyên bản chữ Hán) trên zh.wikisource.org | `WebFetch` qua công cụ trích dẫn; tải thô bị chặn (HTTP lỗi Wikimedia) | **yếu**: một nguồn web, đi qua bước tóm tắt, chưa đối chiếu bản in. Chỉ dùng để *khẳng định có câu phú*, không dùng làm căn cứ điều kiện |
| Học thuật / sách khác | không tìm được văn bản truy xuất được trong phiên này | chưa dùng |

Tôi **không** mở các file PDF cá nhân trên máy để tìm sách (không phải tư liệu của dự án); 3 cuốn đã dùng ở các phiên trước không nằm trong thư mục dự án nên phiên này không đọc lại được trang in. Vì vậy phần "đối chiếu" dưới đây dựa chủ yếu vào luật có trang trong pack, được kiểm lại từng điều kiện bằng đọc `conditions` của chính luật đó (không tin mô tả).

### Câu phú gốc truy xuất được (zh.wikisource, chưa đối chiếu bản in)
Trong 斗數骨髓賦: 「紫府同宮終身福厚」, 「紫府朝垣食祿萬鍾」, 「機月同梁作吏人」, 「子午巨門石中隱玉，明祿暗祿錦上添花」, 「日月並明佐九重於堯殿」, 「日月最嫌反背」(cũng có ở 太微賦). Trong 太微賦: 「太陽居午謂之日麗中天」, 「馬頭帶劍鎮衛邊疆」. Trong 定貴局: 「坐貴向貴 謂魁鉞在命迭相坐拱」. Không tìm thấy trong chương này: 「三奇嘉會」, và câu 「殺破廉貪」 đúng nguyên văn (chỉ thấy 「七殺破軍宜出外」). Các câu này xác nhận **tên cách có trong kinh điển**, nhưng **không** cho điều kiện thành/phá/cứu cụ thể; điều kiện lấy từ bản dịch/bình chú Việt có trang.

## 2. Kết quả rà soát: v1 → v2

Phiên UI (phiên khác) đã chỉ ra sáu chỗ lệch giữa bản nháp v1 và nguồn; tôi kiểm lại từng luật nguồn bằng cách đọc điều kiện và thấy đúng, rồi bổ sung phát hiện về Tuần/Triệt. Bản **v2** (`definition_version: 2`) sửa theo nguồn ở những chỗ có nguồn, phần còn lại ghi là giả thuyết.

| Cách | Có nguồn có trang (v2 bám theo) | Đã sửa so với v1 | Vẫn là giả thuyết (không nguồn) |
|---|---|---|---|
| Tử Phủ Vũ Tướng | KL pp.217–219 chỉ nói "nhóm" ở các cung khác; TH p.94 Thiên Phủ hội cát tinh tốt, gặp Tuần/Triệt xấu (đã verified) | bỏ rescuer "Triệt giải sát"; Tuần *hoặc* Triệt thành phản chứng | điều kiện lõi "đủ bốn sao ở tam phương Mệnh"; booster; breaker; Khoa giải Kỵ |
| Tử Phủ đồng cung | KL p.77 (Dần/Thân), KL p.55 Tuần/Triệt án ngữ Tử Phủ thì kém (verified) | như trên | booster; breaker |
| Cơ Nguyệt Đồng Lương | TT p.24 (verified): **đủ bốn sao** trong tam phương, thiếu cát tinh thì chỉ "công chức bình thường"; KL p.221 (draft) hội Khoa Quyền Lộc/Khôi Việt/Xương Khúc | lõi từ "≥3 sao" thành **đủ 4 sao** (tần suất lõi 28% → 12,5% lá số mẫu); booster = cát tinh hội + Khoa/Quyền/Lộc | breaker Không/Kiếp, Kỵ; rescuer |
| Sát Phá Liêm Tham | TH p.77 (draft, có trang): hạ cách khi ≥3 sát tinh hội + Hóa Kỵ; TH p.76 (draft) Thân cư SPLT hội cát tinh phát | breaker thành "≥3 sát tinh và Kỵ trong tam phương" | lõi "≥3 trong 4 sao"; booster |
| Nhật Nguyệt tịnh minh | KL p.224 (verified) Nhật Nguyệt chiếu Mệnh; TH p.93–94 miếu vượng hội cát tinh tốt; TH p.74 (draft) Nhật/Nguyệt hãm gặp sát tinh | thêm breaker "Nhật/Nguyệt hãm có sát tinh" | booster Tả Hữu, Khoa Quyền; breaker Kỵ, Không/Kiếp |
| Nhật lệ trung thiên | TH p.72 (verified) Thái Dương cư Ngọ có Mệnh; KL p.52 | lõi khớp nguồn; bỏ rescuer Triệt | booster, breaker, rescuer |
| Thạch trung ẩn ngọc | KL p.58, TT p.34 (cả hai verified): Cự Môn Tý/Ngọ hội **đủ** Khoa+Quyền+Lộc; KL p.66 (verified) phá khi Kỵ/Kình **đồng cung** | booster = Tam Hóa hội đủ (v1 lỏng hơn nguồn); breaker = Kỵ hoặc Kình đồng cung | booster Tả Hữu; rescuer Khoa |
| Mã đầu đới kiếm | KL p.64 (draft, có trang): Kình ở Ngọ, tránh Thất Sát, gặp Khoa/Quyền/Lộc | booster = Khoa/Quyền/Lộc hội; breaker = Thất Sát trong tam phương; **bỏ** refutation "Kình hãm" (Kình ở Ngọ hãm theo bảng, tức chính là cách này, nên tự mâu thuẫn) | booster Tả Hữu; breaker Hỏa/Linh/Không/Kiếp, Kỵ |
| Tam kỳ gia hội | KL p.66 (verified): Khoa Quyền Lộc hội mà Kỵ hoặc Kình **đồng cung** Mệnh thì mờ mịt | breaker = Kỵ hoặc Kình đồng cung (v1 chặt hơn nguồn: Kỵ bất kỳ trong tam phương) | booster; rescuer Tả Hữu giải Kỵ |
| Khôi Việt giáp Mệnh | KL p.215 (verified): Khôi, Việt giáp hai bên Mệnh | lõi khớp nguồn | booster, breaker, rescuer |

Hai thay đổi dùng chung: (1) **Tam Hóa hội** làm rescuer chung (khái niệm "tuyệt xứ phùng sinh, được Tam Hóa hội cứu giải" có ở TH p.74, verified, nhưng nguồn chỉ nói cho Mệnh ở bại/tuyệt địa — áp dụng rộng hơn là giả thuyết); (2) bỏ mọi rescuer "Triệt giải sát tinh": **không có nguồn nào nói vậy**, và nhiều luật verified (TH pp.94–95) nói Tuần/Triệt bất lợi cho Phủ, Tướng, Âm, Lương.

**Chưa thể `verified`**: mỗi cách vẫn còn ít nhất một thành phần không có nguồn (cột cuối), và hầu hết "nguồn" là luật trong pack chứ chưa phải trang tôi tự đọc lại. Điều kiện để chuyển: từng thành phần có `locator` trang đã xác minh, hoặc bị loại khỏi định nghĩa.

### Tính tới được (35.712 lá số mẫu, v2)
Mọi cách đều gặp đủ các trạng thái khác "không hiện", trừ: Nhật lệ trung thiên × được cứu, Tử Phủ đồng cung × được cứu, Thạch trung ẩn ngọc × thành thượng (chưa thấy trong mẫu; cần công cụ vét cạn của phiên UI để kết luận có tồn tại hay không). Mã đầu đới kiếm × thành thượng, từng "không thể" ở v1, nay có (72 ô) vì đã bỏ refutation tự mâu thuẫn.

## 3. Phi Hóa (namespace riêng)

Mã: `engine/tvbt/phi_hoa/` — `tables.py`, `graph.py`, `facts.py`, `isolation.py`, `run.py`; luật thử nghiệm `data/experimental/pack_phi_hoa.json` (sinh bởi `tools/build_phi_hoa_pack.py`); endpoint `POST /api/phi-hoa` (`phi_hoa_api.py`, 2 dòng đăng ký trong `api.py`).

- **Đồ thị**: mỗi cung (cung phát hóa) lấy can của mình, bay Lộc–Quyền–Khoa–Kỵ tới cung đang giữ ngôi sao đó (cung nhận hóa): 12 × 4 = 48 cạnh, mỗi cạnh có `trace` ("cung X (can Y) phát Hóa Z → sao S đang ở cung T"), và nhãn hình học: tự hóa, xung phi, tam hợp, giáp, nhị hợp.
- **Tương tác liên cung**: `phi.in.*` (ai bay hóa vào cung này), `phi.mutual.*` (A phi Lộc cho B và B phi Kỵ cho A, v.v.), chuỗi Lộc/Kỵ (`phi.loc_chain`), số hóa nhận vào. Hai cung **cùng can** bay cùng một sao nên được đếm riêng (12 cung, 10 can: hai can lặp), có test.
- **Cách ly trường phái**: luật Phi Hóa chỉ đọc `phi.*` và fact trung tính (`palace.*`, `chart.*`, `time.*`), chỉ được `assert` `derived.phi.*`; luật trường phái khác không được đọc `phi.*`. `validate_isolation` kiểm cả điều kiện, ngoại lệ lẫn ref; có test cho từng trường hợp vi phạm. Fact production không chứa khóa `phi.*` nào (có test).
- **Bảng Tứ Hóa**: chỉ có `tam_hop_vn` (tái sử dụng bảng tam hợp, verified cho trường phái tam hợp); trạng thái ghi `reused_unverified_for_phi_tinh`. Bảng Phi Tinh có thể khác ở vài can nhưng tôi **không thêm** bảng nào vì chưa kiểm được; `stars_for` từ chối id lạ. Thêm bảng đã xác minh = thêm một mục vào `TABLES`.
- **10 luật thử nghiệm** (tự hóa Kỵ/Lộc, xung phi Kỵ có ngoại lệ, Lộc–Kỵ giao nhau, Mệnh phi Lộc/Kỵ vào cung, nhiều hóa cùng vào một cung, chuỗi Lộc hai bước dùng `ref`): giả thuyết cấu trúc, nguồn `SRC_EXPERIMENTAL_PHI` chưa xác minh. Đại hạn phi chính là phép bay từ can cung đại hạn đã có ở Phase 2 (có test chứng minh hai cách tính trùng khớp).

## 4. Lưu tinh và tương tác nguyên cục – đại hạn – lưu niên

- `temporal_facts.luu_tinh`: lưu Lộc Tồn, Kình Dương, Đà La (theo can năm), lưu Khôi, Việt (theo can năm), lưu Thiên Mã (theo chi năm). **Quy ước chưa xác minh**: dùng các bảng nguyên cục đã verified (TH pp.19–24) áp lên can/chi của năm xem. **Không** có lưu Xương/Khúc, lưu Hỏa/Linh: chưa có bảng nào được kiểm.
- 5 luật thử nghiệm mới trong `pack_van_han_layers.json` (lưu Lộc/Kình/Đà nhập Mệnh, Lộc–Mã cùng cung lưu, song Lộc lưu, ba tầng cùng Kỵ). Pack này nay có 13 luật, tất cả `draft`.
- **Nguyệt hạn**: chưa làm. Cung nguyệt hạn (Đẩu Quân) có nhiều quy ước khác nhau và tôi không có công thức đã kiểm.

## 5. Kiểm chứng

- Test mới: `test_phi_hoa.py` (21), mở rộng `test_phase2_layers.py` (23), `test_phase1_formations.py` cập nhật theo v2 (có test riêng cho từng chỗ sửa theo nguồn), `test_phase1_real_charts.py` ghim lại 57 lá số thật theo v2.
- Phần production không bị đụng: các file sửa trong phiên này là đồ thử nghiệm (`formation*.py`, `phi_hoa/`, `temporal_facts.py`, data `experimental/`) cộng hai dòng đăng ký route trong `api.py`.
- 64 test của phiên UI (`test_formation_explain/oracle/provenance`) bám v1 nên đỏ cho tới khi họ cập nhật; chưa commit v2 để không để HEAD đỏ.

## 6. Cần từ người dùng để đi tiếp
1. Trang sách (hoặc file) để đọc lại các luật nguồn còn là `draft` trong pack (đặc biệt KL p.64, KL p.221, TH pp.74, 76, 77) và để tìm nguồn cho các thành phần còn là giả thuyết.
2. Một bảng Tứ Hóa theo can của một tài liệu Phi Tinh cụ thể, nếu muốn Phi Hóa có bảng riêng.
3. Công thức nguyệt hạn (Đẩu Quân) và lưu Xương/Khúc từ một nguồn cụ thể.
